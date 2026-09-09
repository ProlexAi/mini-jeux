#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cycle de vie d'un document : le statut est PHYSIQUE, porte deux fois.

LE PRINCIPE
-----------
Un agent n'a ni memoire entre sessions, ni connaissance des sessions voisines. Si le
statut d'un document n'existe que dans sa tete, le document sera relu indefiniment. On
le rend donc physique, et deux fois plutot qu'une :

    docs/inbox/           -> status: todo
    docs/active/          -> status: in-progress, puis done
    docs/archive/AAAA-MM/ -> status: archived

Le champ dit ce que le document PRETEND etre ; l'emplacement dit ce qu'il EST pour qui
liste un repertoire. La double representation tolere la panne : si l'un ment, l'autre
corrige, et `verifier()` les confronte.

CE QUI EST INTERDIT, ET POURQUOI
--------------------------------
On ne rouvre jamais un document archive. Un archive dit ce qui etait vrai a sa date ; le
reecrire ferait mentir l'histoire. Quand un defaut est decouvert apres coup -- le cas
NOMINAL quand plusieurs agents se succedent -- on cree un document neuf qui NOMME son
predecesseur (D-12, R-15). La chaine reste lisible dans les deux sens et rien n'est
reecrit.
"""

import os
import re
import shutil
from datetime import datetime

from . import journal as jrn
from .atomique import ecrire_texte
from .frontmatter import lire, ecrire, fins_de_ligne, statut, STATUTS
from .verrou import verrou

DOSSIERS = {
    "todo": "docs/inbox",
    "in-progress": "docs/active",
    "done": "docs/active",
    "archived": None,  # docs/archive/AAAA-MM, calcule a la volee
}

# Transitions autorisees. Fermees a dessein : un graphe ouvert laisse passer
# `archived -> in-progress`, qui est precisement ce qu'on interdit.
TRANSITIONS = {
    "todo": {"in-progress"},
    "in-progress": {"done", "todo"},   # retour a todo : l'agent rend la main
    "done": {"archived", "in-progress"},  # in-progress : la verification a echoue
    "archived": set(),
}


class TransitionInterdite(ValueError):
    def __init__(self, de, vers):
        if de == "archived":
            complement = (
                "\nUn document archive est fige. Pour traiter un defaut decouvert apres "
                "coup, creer un document neuf dans docs/inbox/ portant `corrige: <id>` "
                "-- l'historique reste vrai et la chaine reste lisible.")
        else:
            complement = "\nTransitions possibles depuis %r : %s" % (
                de, ", ".join(sorted(TRANSITIONS.get(de, set()))) or "aucune")
        super().__init__("transition interdite : %s -> %s%s" % (de, vers, complement))


class CollisionDeCasse(ValueError):
    """Deux documents que Linux distingue et que Windows confond (R-14)."""

    def __init__(self, a, b):
        super().__init__(
            "collision de casse : %r et %r\n"
            "Linux les distingue, Windows les confond. Migrer un depot qui contient les "
            "deux en perd un, sans message. Renommer avant d'aller plus loin." % (a, b)
        )


def _aujourdhui():
    return datetime.now().strftime("%Y-%m-%d")


def _dossier_cible(statut_vise):
    if statut_vise == "archived":
        return "docs/archive/" + datetime.now().strftime("%Y-%m")
    return DOSSIERS[statut_vise]


def _relatif(racine, chemin):
    """Rend le chemin relatif a la racine, en separateurs POSIX.

    Les separateurs sont normalises : un etat qui porte `docs\\inbox\\x.md` ne se
    retrouve pas sous Linux. C'est le pendant de R-13 pour les chemins relatifs.
    """
    rel = os.path.relpath(os.path.abspath(chemin), os.path.abspath(racine))
    return rel.replace(os.sep, "/")


def collisions_de_casse(racine, bases=None):
    """Rend la liste des paires de chemins qui ne different que par la casse (R-14).

    Bornee aux dossiers geres, comme `verifier()` : un depot est libre de nommer ses
    propres documents comme il veut, y compris d'une facon que Windows confondrait.
    """
    vus, trouvees = {}, []
    for base in (bases if bases is not None else _dossiers_geres(racine)):
        for dossier, _, fichiers in os.walk(base):
            for nom in fichiers:
                complet = _relatif(racine, os.path.join(dossier, nom))
                cle = complet.lower()
                if cle in vus and vus[cle] != complet:
                    trouvees.append((vus[cle], complet))
                else:
                    vus[cle] = complet
    return trouvees


def changer_statut(racine, chemin, vers, agent, chemin_journal=None):
    """Change le statut d'un document et le deplace. Rend le nouveau chemin relatif.

    L'ordre compte : on ECRIT le frontmatter, PUIS on deplace, PUIS on journalise. Si le
    deplacement echoue, le champ a deja bouge -- `verifier()` le rattrapera. L'inverse
    laisserait un fichier deplace dont le champ ment, ce que rien ne rattrape.
    """
    if vers not in STATUTS:
        raise ValueError("statut inconnu : %r -- attendus : %s" % (vers, ", ".join(STATUTS)))

    chemin = os.path.abspath(chemin)

    # UN SEUL VERROU pour tous les changements de statut du depot. Verrouiller le
    # document lui-meme ne marcherait pas : il est DEPLACE pendant l'operation, et
    # le fichier de verrou resterait a cote de l'ancien emplacement.
    verrou_chemin = os.path.join(racine, ".workflow", "documents.lock")
    os.makedirs(os.path.dirname(verrou_chemin), exist_ok=True)

    with verrou(verrou_chemin, delai=10.0):
        with open(chemin, encoding="utf-8", newline="") as f:
            texte = f.read()

        meta, corps, brutes = lire(texte, chemin)
        actuel = statut(meta)
        if vers not in TRANSITIONS[actuel]:
            raise TransitionInterdite(actuel, vers)

        cible_dossier = os.path.join(racine, _dossier_cible(vers))
        cible = os.path.join(cible_dossier, os.path.basename(chemin))
        deplacement = os.path.abspath(cible) != chemin

        # LA COLLISION SE TESTE AVANT D'ECRIRE. C'est une condition connue
        # d'avance, pas un alea : la tester ici laisse le document intact, alors
        # que la tester apres le laissait declarer `archived` en restant dans
        # `active/` -- un etat qu'aucune commande du CLI ne sait reparer.
        if deplacement and os.path.exists(cible):
            raise FileExistsError(
                "un document du meme nom occupe deja %s -- ne pas ecraser une trace"
                % _relatif(racine, cible))

        meta["status"] = vers
        meta["updated"] = _aujourdhui()
        fins = fins_de_ligne(texte)
        # ATOMIQUE : une ecriture en place interrompue detruisait le document.
        ecrire_texte(chemin, ecrire(meta, corps, brutes, fins=fins))

        # L'ORDRE EST CONSERVE : frontmatter d'abord, deplacement ensuite. Si le
        # deplacement echoue malgre tout, le champ a bouge et `verifier()` le
        # rattrape ; l'inverse laisserait un fichier deplace dont le champ ment,
        # ce que rien ne rattrape.
        if deplacement:
            os.makedirs(cible_dossier, exist_ok=True)
            shutil.move(chemin, cible)

    rel = _relatif(racine, cible)
    if chemin_journal:
        jrn.ajouter(chemin_journal,
                    "document-archive" if vers == "archived" else "document-statut",
                    agent, cible=rel, detail=vers)
    return rel


def _dossiers_geres(racine):
    """Les seuls dossiers dont le kit est responsable.

    LE KIT NE JUGE PAS CE QU'IL NE GERE PAS -- mesure du 2026-08-31.
    Le premier deploiement reel, sur ProlexDashBoard, a remonte 29 ecarts : le controle
    parcourait `docs/` en entier et reclamait un frontmatter a quatorze documents ecrits
    a la main bien avant le kit, dont `backlog_trace.md` et `decisions.md` -- ceux-la
    memes que la decision D-13 interdit de toucher.

    Le hook les aurait affiches a chaque commit, sur cinq worktrees. Ce n'etait pas du
    bruit : c'etait FAUX. Un depot qui adopte le kit garde ses documents libres, et seuls
    ceux qu'il place dans les dossiers du cycle entrent dans son perimetre.
    """
    dossiers = [os.path.join(racine, "docs", "inbox"),
                os.path.join(racine, "docs", "active")]
    archive = os.path.join(racine, "docs", "archive")
    if os.path.isdir(archive):
        dossiers.append(archive)
    return [d for d in dossiers if os.path.isdir(d)]


def verifier(racine):
    """Confronte le champ `status` et l'emplacement. Rend la liste des ecarts.

    C'est la contrepartie de la double representation : sans confrontation, deux sources
    de verite deviennent deux verites. Borne aux dossiers geres -- voir `_dossiers_geres`.
    """
    ecarts = []
    fichiers_vus = []
    for base in _dossiers_geres(racine):
        for dossier, _, fichiers in os.walk(base):
            fichiers_vus += [os.path.join(dossier, n) for n in fichiers if n.endswith(".md")]

    for complet in sorted(fichiers_vus):
        rel = _relatif(racine, complet)
        try:
            with open(complet, encoding="utf-8", newline="") as f:
                meta, _, _ = lire(f.read(), complet)
            declare = statut(meta)
        except Exception as e:  # noqa: BLE001
            ecarts.append((rel, "frontmatter illisible : %s" % str(e).split("\n")[0]))
            continue
        attendu = _dossier_cible(declare)
        if declare == "archived":
            if not rel.startswith("docs/archive/"):
                ecarts.append((rel, "declare archived mais hors de docs/archive/"))
        elif not rel.startswith(attendu + "/"):
            ecarts.append((rel, "declare %s, attendu dans %s/" % (declare, attendu)))

    for a, b in collisions_de_casse(racine):
        ecarts.append((a, "collision de casse avec %s" % b))
    return ecarts
