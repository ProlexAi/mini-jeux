#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Journal append-only : ce qui s'est passe, qui l'a fait, quand.

POURQUOI IL EXISTE
------------------
Le TODO se purge : une tache close disparait de la liste active, sinon la liste se
remplit de bruit et les agents relisent du travail deja fait. Mais purger sans trace,
c'est oublier. Le journal est la contrepartie exacte de la purge -- ce qui sort de la
vue reste dans l'histoire.

Il porte la reponse a une question que rien d'autre ne sait rendre (R-16) :
    « qui a touche ce fichier, quand, dans quelle tache ? »
C'est ce qui permet a un agent de reprendre le travail d'un autre trois jours plus tard,
et de remonter d'un defaut a la tache qui l'a produit.

APPEND-ONLY, SANS EXCEPTION
---------------------------
On ajoute des lignes, on n'en retire ni n'en modifie jamais. Un JSONL -- une ligne, un
objet JSON -- se lit ligne a ligne sans tout charger, se `grep`, et se fusionne
proprement : quand deux sessions ecrivent le meme jour, un conflit Git se resout en
gardant les deux blocs. C'est exactement la regle du journal de ProlexCore.

L'ajout se fait sous verrou. Sur la plupart des systemes un ajout court est deja
atomique, mais « la plupart » n'est pas une garantie : deux agents peuvent entrelacer
leurs octets et produire une ligne illisible, qui casserait la lecture de tout le fichier.
"""

import json
import os
from datetime import datetime

from .verrou import verrou

# Types d'evenement. Ferme a dessein : un vocabulaire ouvert derive en synonymes
# ("fini", "termine", "done") et rend le journal inexploitable par machine.
EVENEMENTS = {
    "tache-ajoutee",
    "tache-reservee",
    "tache-liberee",
    "tache-close",
    "tache-liee",        # correction tardive : voir R-15
    "document-statut",
    "document-archive",
    "surface-declaree",  # un agent annonce ou il travaille
    "backlog-bouge",     # le backlog d'un depot a change dans un commit
    "note",              # decision, arbitrage, observation
    # Deux gestes d'AUTORITE, distincts de leur equivalent ordinaire parce qu'ils
    # s'exercent SUR AUTRUI. Les confondre avec « tache-liberee » rendrait une
    # eviction indiscernable d'une restitution volontaire au moment de la
    # relecture -- or c'est precisement ce qu'un lecteur doit pouvoir distinguer.
    "tache-liberee-de-force",              # B-C : une reservation a ete evincee
    "presence-retiree-par-orchestrateur",  # B-E : un agent a ete retire du registre
}


class EvenementInconnu(ValueError):
    def __init__(self, evenement):
        super().__init__(
            "evenement inconnu : %r\nAttendus : %s\n"
            "Le vocabulaire est ferme pour que le journal reste lisible par machine."
            % (evenement, ", ".join(sorted(EVENEMENTS)))
        )


def horodatage():
    """ISO 8601 local AVEC decalage : '2026-08-31T00:54:36+02:00'.

    Le decalage explicite rend l'instant non ambigu entre deux machines, sans sacrifier
    la lisibilite humaine d'un UTC nu. La migration vers Linux ne changera pas la lecture
    des lignes deja ecrites.
    """
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _os_user():
    """Le compte systeme, par la voie qui marche partout.

    `getpass.getuser()` LEVE si aucune des variables d'environnement usuelles
    n'est definie -- ce qui arrive dans un conteneur ou un cron depouille. Le
    journal ne doit jamais echouer pour si peu : on rend une chaine vide.
    """
    try:
        import getpass
        return getpass.getuser()
    except Exception:
        return os.environ.get("USER") or os.environ.get("USERNAME") or ""


def ajouter(chemin, evenement, agent, cible=None, tache=None, detail=None, **extra):
    """Ajoute une ligne. Rend l'entree ecrite.

    `agent`  -- identite de la session (WORKFLOW_AGENT), jamais anonyme.
    `cible`  -- chemin RELATIF au depot, ou identifiant. Jamais un chemin absolu.
    `tache`  -- l'identifiant de tache dans laquelle l'action s'inscrit, si elle existe.
    """
    if evenement not in EVENEMENTS:
        raise EvenementInconnu(evenement)

    entree = {"quand": horodatage(), "quoi": evenement, "qui": agent}
    # A1 : OS-user et PID ne PROUVENT rien -- ils se forgent aussi. Ils servent
    # l'expertise a posteriori : quand deux lignes se contredisent, savoir si
    # elles viennent de deux processus distincts ou du meme a deux instants
    # oriente la recherche. Ecrits sous des cles courtes pour ne pas alourdir un
    # journal qu'on lit ligne par ligne.
    entree["os"] = _os_user()
    entree["pid"] = os.getpid()
    corr = os.environ.get("WORKFLOW_CORRELATION") or ""
    if corr:
        entree["corr"] = corr
    if cible is not None:
        entree["cible"] = cible
    if tache is not None:
        entree["tache"] = tache
    if detail is not None:
        entree["detail"] = detail
    entree.update(extra)

    chemin = os.fspath(chemin)
    dossier = os.path.dirname(chemin)
    if dossier:
        os.makedirs(dossier, exist_ok=True)

    ligne = json.dumps(entree, ensure_ascii=False, sort_keys=True) + "\n"
    with verrou(chemin + ".lock"):
        with open(chemin, "a", encoding="utf-8", newline="\n") as f:
            f.write(ligne)
            f.flush()
            os.fsync(f.fileno())
    return entree


def lire(chemin):
    """Itere les entrees. Une ligne illisible est SIGNALEE, jamais ignoree en silence.

    Ignorer une ligne cassee ferait rendre au journal un historique incomplet en se
    presentant comme complet -- pire qu'une erreur franche.
    """
    try:
        with open(chemin, encoding="utf-8") as f:
            for numero, ligne in enumerate(f, 1):
                ligne = ligne.strip()
                if not ligne:
                    continue
                try:
                    yield json.loads(ligne)
                except json.JSONDecodeError as e:
                    raise ValueError(
                        "journal illisible a la ligne %d de %s : %s\n"
                        "Une ligne corrompue signale un ajout non serialise ; ne pas la "
                        "supprimer sans l'avoir lue." % (numero, chemin, e)
                    ) from e
    except FileNotFoundError:
        return


def chercher(chemin, cible=None, agent=None, tache=None, evenement=None):
    """Filtre les entrees. Sans critere, rend tout.

    C'est la reponse a R-16 : `chercher(j, cible="docs/active/note.md")` rend qui a
    touche ce fichier, quand, et dans quelle tache.
    """
    for e in lire(chemin):
        if cible is not None and e.get("cible") != cible:
            continue
        if agent is not None and e.get("qui") != agent:
            continue
        if tache is not None and e.get("tache") != tache:
            continue
        if evenement is not None and e.get("quoi") != evenement:
            continue
        yield e
