#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lecture et ecriture d'un fichier d'etat JSON : atomique, verrouillee, portable.

TROIS GARANTIES, TROIS RAISONS
------------------------------
1. ATOMIQUE (R-02) -- on ecrit un fichier temporaire dans le MEME repertoire, on le
   force sur le disque, puis `os.replace`. Un lecteur voit l'ancien etat ou le nouveau,
   jamais un JSON tronque. Le temporaire doit etre dans le meme repertoire : `os.replace`
   n'est atomique qu'a l'interieur d'un systeme de fichiers.

2. VERROUILLEE (R-01) -- toute modification passe par `modifier()`, qui tient le verrou
   pendant la lecture ET l'ecriture. Lire puis ecrire sans verrou rouvre exactement la
   fenetre que le verrou existe pour fermer.

3. PORTABLE (R-13) -- sauts de ligne forces en `\\n` et aucun chemin absolu accepte.
   Sans le premier, le meme etat differe entre Windows et Linux et Git le voit modifie a
   chaque bascule. Sans le second, l'etat produit sous Windows rend des chemins morts
   apres la migration.

CE QUE `modifier()` GARANTIT
---------------------------
    with modifier(chemin) as etat:
        etat["taches"]["T-001"] = {...}

Le bloc s'execute sous verrou. Si le corps leve, RIEN n'est ecrit -- l'etat sur disque
reste celui d'avant. C'est ce qui rend une commande interrompue inoffensive.
"""

import hashlib
import json
import os
import tempfile
import time
from contextlib import contextmanager

from .verrou import verrou
from .atomique import remplacer as _remplacer

VERSION_SCHEMA = 1

# Motifs de chemin absolu, les deux mondes. Une valeur qui ressemble a cela dans l'etat
# est refusee a l'ecriture : c'est le seul moment ou l'on peut encore l'empecher.
import re
_ABSOLU = re.compile(r"^(?:[A-Za-z]:[\\/]|\\\\|/(?!/))")


class EtatIllisible(RuntimeError):
    """L'etat existe mais ne se lit pas. Dit QUOI faire, pas seulement QUOI casse.

    Un `json.JSONDecodeError` nu tuait toutes les commandes du kit sans nommer le
    fichier ni suggerer de reparation. La cause de loin la plus frequente est un
    conflit de fusion -- que le lot 4 rend impossible en sortant l'etat du
    versionnement, mais qui reste possible sur un depot pas encore migre.
    """

    def __init__(self, chemin, cause):
        self.chemin = chemin
        marqueurs = ""
        try:
            with open(chemin, encoding="utf-8", errors="replace") as f:
                if "<<<<<<<" in f.read():
                    marqueurs = ("\n  Le fichier porte des marqueurs de conflit Git : cet etat "
                                 "a ete fusionne.\n  Il n'a pas a l'etre -- voir `init`, qui le "
                                 "sort du versionnement.")
        except OSError:
            pass
        super().__init__(
            "etat illisible : %s\n  %s%s\n  Reparer le fichier, ou le supprimer pour "
            "repartir d'un etat neuf (les taches en cours seraient perdues)."
            % (chemin, cause, marqueurs))


class CheminAbsoluInterdit(ValueError):
    """Une valeur de l'etat porte un chemin absolu : il ne survivrait pas a la machine."""

    def __init__(self, cle, valeur):
        super().__init__(
            "chemin absolu interdit dans l'etat, a la cle %r : %r\n"
            "L'etat doit rester relatif a la racine du depot, sinon il ne survit pas a "
            "un changement de machine (migration Windows vers Linux)." % (cle, valeur)
        )


def _verifier_relatif(donnees, prefixe=""):
    """Parcourt l'etat et refuse tout chemin absolu. Recursif sur dicts et listes."""
    if isinstance(donnees, dict):
        for k, v in donnees.items():
            _verifier_relatif(v, "%s.%s" % (prefixe, k) if prefixe else str(k))
    elif isinstance(donnees, list):
        for i, v in enumerate(donnees):
            _verifier_relatif(v, "%s[%d]" % (prefixe, i))
    elif isinstance(donnees, str) and _ABSOLU.match(donnees):
        raise CheminAbsoluInterdit(prefixe, donnees)


def etat_neuf(depot=""):
    """L'etat initial. `depot` est un NOM, jamais un chemin."""
    return {
        "version": VERSION_SCHEMA,
        "depot": depot,
        "taches": {},
        "claims": {},
        "documents": {},
    }


def lire(chemin, defaut=None, tentatives=200, pause=0.01):
    """Lit l'etat. Rend `defaut` (ou un etat neuf) si le fichier n'existe pas.

    Ne prend PAS le verrou : une lecture seule tolere de voir l'etat d'il y a une
    milliseconde. Ce qui ne se tolere pas, c'est un etat a moitie ecrit -- et l'ecriture
    atomique l'interdit deja.

    LE PIEGE WINDOWS, MESURE LE 2026-08-31
    --------------------------------------
    Sous POSIX, `os.replace` reussit meme si un lecteur tient le fichier ouvert : le
    lecteur garde son inode, le remplacement passe. Sous Windows, `open()` de Python
    n'ouvre PAS avec FILE_SHARE_DELETE, si bien qu'un lecteur en boucle fait echouer le
    remplacement de l'ecrivain -- et reciproquement, le lecteur se voit refuser l'acces
    pendant l'instant du remplacement.

    Ce refus est TRANSITOIRE et ne signale aucune corruption : on le reprend. Un JSON
    invalide, lui, n'est jamais repris -- il signalerait une ecriture non atomique, donc
    un vrai defaut, et le taire rendrait le controle aveugle.
    """
    for reste in range(tentatives - 1, -1, -1):
        try:
            with open(chemin, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return etat_neuf() if defaut is None else defaut
        except PermissionError:
            if reste == 0:
                raise
            time.sleep(pause)
        except json.JSONDecodeError as e:
            # Un JSON invalide n'est JAMAIS repris -- il signale un vrai defaut.
            # Mais le traceback brut de json ne disait ni quel fichier, ni quoi
            # faire : toutes les commandes du kit mouraient dessus sans qu'un
            # agent puisse rien en tirer. Le cas le plus frequent est un conflit
            # de fusion, d'ou la piste donnee en clair.
            raise EtatIllisible(chemin, e) from e


def ecrire(chemin, donnees):
    """Ecrit l'etat de facon atomique. Ne prend pas le verrou : voir `modifier()`."""
    _verifier_relatif(donnees)
    chemin = os.fspath(chemin)
    dossier = os.path.dirname(chemin) or "."
    os.makedirs(dossier, exist_ok=True)

    # Le temporaire va dans le MEME dossier : os.replace n'est atomique qu'intra-volume.
    fd, tmp = tempfile.mkstemp(prefix=".etat-", suffix=".tmp", dir=dossier)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump(donnees, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        _remplacer(tmp, chemin)
        tmp = None
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)


def empreinte(donnees):
    """L'empreinte du fragment que ce depot apporte a la federation (B-D).

    CE QUE CE N'EST PAS : de la cryptographie. Personne ne signe, rien n'est
    secret, et qui modifie l'etat recalcule l'empreinte aussi bien que nous.

    CE QUE C'EST : un detecteur de MODIFICATION HORS PROTOCOLE. Le master agrege
    tous les depots -- c'est le point d'entree ideal d'une injection transverse.
    L'empreinte est recalculee a l'agregation et confrontee a celle que le depot
    avait declaree : qui edite un state.json a la main entre deux passages est vu.

    Seules les taches ACTIVES et les claims comptent. Une tache close ne voyage
    pas au master : sa disparition ne doit pas faire crier.
    """
    actives = {i: t for i, t in (donnees.get("taches") or {}).items()
               if t.get("etat") != "close"}
    charge = json.dumps({"taches": actives, "claims": donnees.get("claims") or {}},
                        ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(charge.encode("utf-8")).hexdigest()[:16]


@contextmanager
def modifier(chemin, verrou_chemin=None, delai=10.0):
    """Lecture-modification-ecriture sous verrou. Rien n'est ecrit si le corps leve."""
    chemin = os.fspath(chemin)
    verrou_chemin = verrou_chemin or (chemin + ".lock")
    with verrou(verrou_chemin, delai=delai):
        donnees = lire(chemin)
        yield donnees
        # B-D : l'empreinte se pose ICI, au point de passage unique de toute
        # modification. La poser dans chaque commande garantirait qu'une commande
        # l'oublie -- et un detecteur qui n'a rien a comparer ne detecte rien.
        donnees["empreinte"] = empreinte(donnees)
        ecrire(chemin, donnees)
