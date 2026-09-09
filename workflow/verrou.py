#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verrou exclusif inter-processus, portable Windows et POSIX.

POURQUOI CE MODULE EXISTE
-------------------------
L'etat partage entre agents est un fichier. Deux agents qui l'ecrivent en meme temps
produisent des ecritures dechirees et des pertes silencieuses. La reponse standard est
`fcntl.flock` -- mais `fcntl` N'EXISTE PAS sous Windows (mesure le 2026-08-30 :
`import fcntl` rend ModuleNotFoundError, et le binaire `flock` est absent du PATH).

Un kit qui promet la protection de concurrence en s'appuyant sur flock ne protege donc
rien sur la moitie des machines. Ce module donne UNE API pour les deux mondes :

    from workflow.verrou import verrou
    with verrou(chemin_du_lock):
        ...  # personne d'autre n'est ici

DEUX IMPLEMENTATIONS, UN SEUL CONTRAT
-------------------------------------
POSIX   : fcntl.flock(LOCK_EX | LOCK_NB) dans une boucle d'attente.
Windows : msvcrt.locking(LK_NBLCK) sur un octet, meme boucle.

Les deux verrouillent le MEME fichier `.lock` : un depot produit sous Windows puis
rejoue sous Linux se comporte identiquement. C'est la condition pour que la bascule
annoncee ne fasse rien perdre.

CE QUE CE MODULE NE FAIT PAS
----------------------------
Il ne serialise QUE les processus qui l'utilisent. Un agent qui edite l'etat a la main
contourne tout. C'est pour cela que le protocole passe par le CLI, sans exception.
"""

import errno
import os
import time
from contextlib import contextmanager

# Selection de l'implementation a l'import : une seule fois, pas a chaque appel.
try:
    import fcntl  # POSIX
    _SYSTEME = "posix"
except ImportError:  # pragma: no cover - depend de l'OS
    import msvcrt  # Windows
    _SYSTEME = "windows"


DELAI_DEFAUT = 10.0      # secondes avant d'abandonner
PAUSE = 0.05             # attente entre deux tentatives


class VerrouIndisponible(RuntimeError):
    """Le verrou n'a pas pu etre pris dans le delai imparti.

    Porte le chemin et le delai : un agent qui recoit cette erreur doit pouvoir dire
    a l'utilisateur QUI il attendait, pas seulement qu'il a echoue.
    """

    def __init__(self, chemin, delai):
        self.chemin = str(chemin)
        self.delai = delai
        super().__init__(
            "verrou indisponible apres %.1f s : %s\n"
            "Une autre session ecrit l'etat. Relancer la commande ; si le blocage "
            "persiste, verifier qu'aucun processus n'est reste suspendu." % (delai, chemin)
        )


def _tenter_posix(fh):
    fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


def _liberer_posix(fh):
    fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


def _tenter_windows(fh):
    # msvcrt verrouille une PLAGE a partir de la position courante : un octet a 0 suffit,
    # mais il faut que le fichier fasse au moins cet octet -- d'ou l'ecriture ci-dessous.
    fh.seek(0)
    msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)


def _liberer_windows(fh):
    fh.seek(0)
    msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)


_TENTER = _tenter_posix if _SYSTEME == "posix" else _tenter_windows
_LIBERER = _liberer_posix if _SYSTEME == "posix" else _liberer_windows


@contextmanager
def verrou(chemin, delai=DELAI_DEFAUT):
    """Prend un verrou exclusif sur `chemin`, ou leve VerrouIndisponible.

    Le fichier de verrou est cree s'il manque et n'est jamais supprime : le supprimer
    ouvrirait une fenetre ou deux processus tiennent chacun un fichier different sous
    le meme nom. Il pese un octet.
    """
    chemin = os.fspath(chemin)
    parent = os.path.dirname(chemin)
    if parent:
        os.makedirs(parent, exist_ok=True)

    # "r+b" apres creation : il faut pouvoir lire ET ecrire pour verrouiller sous Windows.
    if not os.path.exists(chemin):
        with open(chemin, "wb") as f:
            f.write(b"0")

    fh = open(chemin, "r+b")
    limite = time.monotonic() + delai
    pris = False
    try:
        while True:
            try:
                _TENTER(fh)
                pris = True
                break
            except OSError as e:
                # POSIX rend EWOULDBLOCK/EAGAIN, Windows rend EDEADLOCK/EACCES.
                attendu = (errno.EACCES, errno.EAGAIN, errno.EWOULDBLOCK, errno.EDEADLOCK)
                if e.errno not in attendu:
                    raise
                if time.monotonic() >= limite:
                    raise VerrouIndisponible(chemin, delai) from e
                time.sleep(PAUSE)
        yield chemin
    finally:
        if pris:
            try:
                _LIBERER(fh)
            except OSError:
                # La liberation echoue si le descripteur est deja invalide ; la fermeture
                # ci-dessous libere de toute facon. Taire ici evite de masquer l'exception
                # d'origine qui remonte du bloc `with`.
                pass
        fh.close()


def systeme():
    """Rend 'posix' ou 'windows' -- utile aux tests et au diagnostic."""
    return _SYSTEME
