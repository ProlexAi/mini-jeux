#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Synchronisation : archiver ce qui est fait, regenerer ce qui se genere.

IDEMPOTENCE, ET CE QU'ELLE EXIGE VRAIMENT
-----------------------------------------
« Rejouer ne produit aucun effet supplementaire » ne suffit pas comme intention : il faut
que la seconde execution N'ECRIVE RIEN DU TOUT. Un TODO.md reecrit a l'identique change
sa date de modification, ce qui suffit a le faire entrer dans le commit suivant, a
declencher un watcher, ou a faire croire a une autre session qu'il vient de bouger.

D'ou la regle appliquee partout ici : **on compare avant d'ecrire, et on n'ecrit que si
le contenu differe.** C'est ce qui autorise a appeler `sync` depuis un hook pre-commit,
une fin de session et un cron sans se demander laquelle a deja tourne.

CE QUE SYNC FAIT, DANS CET ORDRE
--------------------------------
1. archive les documents `done` vers docs/archive/AAAA-MM/
2. regenere le backlog
3. rend le compte-rendu de ce qui a REELLEMENT change

Il ne touche jamais au backlog du projet ni au journal : le premier est l'autorite de
l'agent, le second ne se reecrit pas.
"""

import os

from . import config, documents, taches
from .frontmatter import lire as lire_fm, statut
from .atomique import ecrire_octets


def _ecrire_si_different(chemin, contenu):
    """Rend True si le fichier a ete ecrit, False s'il etait deja juste.

    Le mode binaire evite qu'une comparaison passe puis qu'une ecriture en mode texte
    reintroduise des CRLF sous Windows : on compare et on ecrit les MEMES octets.
    """
    octets = contenu.encode("utf-8")
    try:
        with open(chemin, "rb") as f:
            if f.read() == octets:
                return False
    except FileNotFoundError:
        pass
    # Ecriture ATOMIQUE : mesure du 2026-09-09, TODO.md etait lisible a zero
    # octet 14 fois pendant une sequence banale de `todo add`. Un agent qui lit
    # le TODO.md a cet instant conclut que le depot n'a aucune tache.
    ecrire_octets(chemin, octets)
    return True


def documents_a_archiver(racine):
    """Les documents `done` qui ne sont pas encore dans docs/archive/."""
    prets = []
    actif = os.path.join(racine, "docs", "active")
    if not os.path.isdir(actif):
        return prets
    for nom in sorted(os.listdir(actif)):
        if not nom.endswith(".md"):
            continue
        complet = os.path.join(actif, nom)
        try:
            with open(complet, encoding="utf-8", newline="") as f:
                meta, _, _ = lire_fm(f.read(), complet)
            if statut(meta) == "done":
                prets.append(complet)
        except Exception:  # noqa: BLE001
            # Un document illisible n'est pas archive en silence : `verifier` le
            # signalera. Archiver ce qu'on ne sait pas lire serait pire que l'ignorer.
            continue
    return prets


def synchroniser(arbre=None, agent=None, archiver=True, racine_etat=None):
    """Rend un compte-rendu : {'archives': [...], 'todo_reecrit': bool, 'ecarts': [...]}.

    DEUX RACINES, ET C'EST VOLONTAIRE. `arbre` porte les documents et le TODO.md
    de CE worktree ; `racine_etat` porte state.json et journal.jsonl, qui sont
    UNIQUES par depot. Les confondre sous un seul parametre est ce qui faisait
    lire l'etat du worktree : `sync` annoncait « Rien a faire » alors que l'etat
    partage portait une tache de plus (mesure du 2026-09-09).

    `archiver=False` sert au controle a blanc : on veut savoir ce qui bougerait
    sans que rien ne bouge.
    """
    arbre = arbre or config.racine()
    racine_etat = racine_etat or config.racine_partagee()
    agent = agent or config.agent() or "sync"
    etat = config.chemin_etat(racine_etat)
    jrnl = config.chemin_journal(racine_etat)

    archives = []
    for complet in documents_a_archiver(arbre):
        if not archiver:
            archives.append(os.path.relpath(complet, arbre).replace(os.sep, "/"))
            continue
        # Les documents sont archives DANS LEUR ARBRE, le geste est journalise
        # dans le journal PARTAGE : chaque notion suit sa racine.
        archives.append(documents.changer_statut(arbre, complet, "archived", agent, jrnl))

    todo_texte = taches.rendre_todo(etat, config.nom_depot(racine_etat))
    chemin_todo = os.path.join(arbre, config.NOM_BACKLOG)
    reecrit = _ecrire_si_different(chemin_todo, todo_texte) if archiver else False

    return {
        "archives": archives,
        "todo_reecrit": reecrit,
        "ecarts": documents.verifier(arbre),
    }


def resume(rapport):
    """Une ligne par effet reel. Silence si rien n'a bouge -- c'est le cas nominal."""
    lignes = []
    for chemin in rapport["archives"]:
        lignes.append("archive : %s" % chemin)
    if rapport["todo_reecrit"]:
        lignes.append(config.NOM_BACKLOG + " regenere")
    for chemin, quoi in rapport["ecarts"]:
        lignes.append("ecart   : %s -- %s" % (chemin, quoi))
    return lignes
