# -*- coding: utf-8 -*-
"""Remontee : un backlog qui bouge dans un depot arrive au registre central.

LE TROU QU'ELLE FERME. Avant elle, une seule chose ecrivait au journal central :
la declaration d'une surface, au moment d'un `claim`. Un depot pouvait donc
reecrire tout son backlog sans que la vue transverse en sache rien. L'orchestrateur
voyait qui travaillait ou, jamais ce qui avait bouge.

CE QU'ELLE FAIT. Appelee apres un commit, elle regarde si ce commit a touche un
fichier de backlog -- le `TODO.md` du kit, son `state.json`, ou un backlog tenu a
la main comme `docs/backlog_trace.md`. Si oui, une ligne part au journal central :
quel depot, quel commit, quels fichiers, combien de taches ouvertes apres coup.

TROIS INTERDITS, chacun ne d'un defaut deja paye dans ce depot.

**Elle ne bloque JAMAIS.** AGENTS.md §12 : aucun hook bloquant sur une ressource
exterieure au depot. Le registre EST exterieur -- il peut etre absent, sur un
disque demonte, ou appartenir a une autre machine. Toute erreur est avalee et rend
un motif, jamais une exception.

**Elle n'ecrit rien dans l'index.** Le `pre-commit` du kit a deja fait cette faute
une fois : un `git add -A` dans un hook a fait entrer un fichier dans un commit que
son auteur n'avait pas choisi. Un hook herite de l'autorite de celui qui commite
sans heriter de ses regles.

**Elle n'ecrit aucun chemin absolu dans le depot.** Les chemins de fichiers
remontes sont RELATIFS a la racine : le registre est lu depuis d'autres machines,
et un `/home/matt/...` y serait faux partout ailleurs. Seul le journal central --
qui decrit une machine a un instant -- porte le nom du depot, jamais son chemin.
"""

from __future__ import annotations

import json
import os
import subprocess

from . import config, journal as jrn, registre as reg

# Motifs de fichiers qui, touches, valent une remontee. Compares sur le chemin
# RELATIF, en minuscules, avec des barres obliques -- Git rend toujours des `/`,
# meme sous Windows, donc aucune normalisation de separateur n'est necessaire.
#
# `backlog_trace.md` est nomme explicitement : quatre depots le portent, tenu a la
# main, et le kit ne le touche pas. C'est precisement le fichier que Matt veut voir
# remonter (demande du 2026-09-08).
MOTIFS = (
    "todo.md",
    ".workflow/state.json",
    "backlog_trace.md",
    "backlog-master.md",
    "todo-master.md",
)


def _git(args, cwd):
    try:
        r = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=30)
        return r.stdout if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def fichiers_du_commit(racine, sha="HEAD"):
    """Chemins RELATIFS touches par un commit. Vide si indeterminable.

    `--root` couvre le tout premier commit d'un depot, qui n'a pas de parent :
    sans lui, `git diff-tree` rend vide et la toute premiere creation d'un backlog
    ne remonterait jamais. Le cas paraît theorique et ne l'est pas -- c'est
    exactement l'etat d'un depot le jour ou on y installe le kit.
    """
    sortie = _git(["diff-tree", "--no-commit-id", "--name-only", "-r", "--root", sha], racine)
    return [l.strip() for l in sortie.splitlines() if l.strip()]


def concernes(fichiers):
    """Ceux qui valent une remontee, dans l'ordre ou ils ont ete donnes.

    La comparaison est un suffixe, pas une egalite : `docs/backlog_trace.md` et
    `sous/projet/TODO.md` comptent tous les deux. Un `endswith` sur le motif nu
    ferait de `mon-todo.md` un faux positif, d'ou la barre oblique exigee -- sauf
    quand le fichier est a la racine, ou le chemin relatif vaut le motif.
    """
    retenus = []
    for f in fichiers:
        bas = f.lower()
        for m in MOTIFS:
            if bas == m or bas.endswith("/" + m):
                retenus.append(f)
                break
    return retenus


def _compte_taches(racine):
    """Taches ouvertes apres le commit. None si l'etat est illisible.

    None n'est pas 0 : un etat illisible et un backlog vide sont deux faits
    differents, et les confondre ferait lire une purge la ou il y a une panne.
    """
    try:
        with open(config.chemin_etat(racine), encoding="utf-8") as f:
            taches = (json.load(f) or {}).get("taches") or {}
        return sum(1 for t in taches.values() if t.get("etat") != "close")
    except (OSError, ValueError, AttributeError):
        return None


def remonter(racine=None, sha="HEAD", agent=None):
    """Remonte le mouvement du backlog au registre. Rend un dict de compte rendu.

    `rendu["remonte"]` est True seulement si une ligne a ete ecrite. Toute autre
    issue porte un `motif` en clair -- destine a un humain qui lit le journal du
    depot, pas a un code de sortie que personne ne regarde.
    """
    racine = racine or config.racine()
    rendu = {"remonte": False, "motif": "", "fichiers": [], "depot": config.nom_depot(racine)}

    central = config.registre(racine)
    if not central:
        rendu["motif"] = "hors federation : aucun registre configure"
        return rendu
    if not os.path.isdir(central):
        rendu["motif"] = "registre declare mais absent du disque"
        return rendu

    fichiers = fichiers_du_commit(racine, sha)
    if not fichiers:
        rendu["motif"] = "aucun fichier lisible pour %s" % sha
        return rendu

    touches = concernes(fichiers)
    if not touches:
        rendu["motif"] = "aucun fichier de backlog dans ce commit"
        return rendu

    rendu["fichiers"] = touches
    court = (_git(["rev-parse", "--short", sha], racine) or "").strip() or sha
    sujet = (_git(["log", "-1", "--format=%s", sha], racine) or "").strip()

    try:
        jrn.ajouter(
            reg.chemin(central, reg.JOURNAL),
            "backlog-bouge",
            agent or config.agent() or "git",
            cible=rendu["depot"],
            detail="%s : %s" % (court, sujet),
            fichiers=touches,
            ouvertes=_compte_taches(racine),
        )
    except Exception as e:  # noqa: BLE001 -- un hook ne leve jamais
        # Le registre peut etre en lecture seule, sur un montage disparu, ou tenu
        # par un verrou d'une autre machine. Aucun de ces cas ne doit toucher au
        # commit qui vient d'avoir lieu : il est deja ecrit, et le penaliser pour
        # une panne exterieure au depot est exactement ce que le §12 interdit.
        rendu["motif"] = "ecriture au registre refusee : %s" % e
        return rendu

    rendu["remonte"] = True
    rendu["motif"] = "%d fichier(s) de backlog remonte(s)" % len(touches)
    return rendu
