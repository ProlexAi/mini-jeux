# -*- coding: utf-8 -*-
"""Ecriture atomique de fichier, partagee par tout le kit.

POURQUOI CE MODULE. L'audit du 2026-09-09 a mesure la meme faute a trois
endroits : `etat.py` protegeait `state.json` par temporaire + fsync + os.replace,
mais `registre.enregistrer_depot`, `synchro._ecrire_si_different` et
`documents.changer_statut` ecrivaient EN PLACE. Le kit enoncait donc la bonne
regle et ne l'appliquait qu'a un seul de ses quatre fichiers.

CE QUE COUTAIT L'ECRITURE EN PLACE, mesure et non deduit :
  - `TODO.md` et les masters lisibles a ZERO OCTET pendant leur regeneration --
    14 lectures vides pendant une sequence banale de `todo add` ;
  - un document detruit si l'ecriture est interrompue en cours ;
  - un `depots.json` tronque qu'une lecture tolerante prend pour « aucun depot ».

CE QUE CE MODULE NE FAIT PAS. Il ne prend aucun verrou. Une ecriture atomique
garantit que le lecteur voit l'ancien fichier OU le nouveau, jamais un fichier a
moitie ecrit -- elle ne garantit RIEN sur deux ecrivains qui se lisent l'un
l'autre. Une sequence lire-modifier-ecrire a besoin des DEUX : le verrou pour
serialiser, l'atomicite pour le lecteur qui ne verrouille pas.
"""
import os
import tempfile
import time


def remplacer(source, cible, tentatives=500, pause=0.01):
    """os.replace, avec reprise.

    Sous Windows, le remplacement echoue tant qu'un autre processus tient la
    cible ouverte -- lecteur concurrent, antivirus, editeur. Sous POSIX il
    reussit toujours : la reprise ne sert qu'a Windows et coute zero ailleurs.

    Le budget total (5 s par defaut) est volontairement genereux. Mesure du
    2026-08-31 : avec 20 tentatives sur 1 s, quatre ecrivains face a un lecteur
    en boucle serree plantaient sur PermissionError. Echouer ici perdrait une
    ecriture DEJA validee -- le pire moment pour abandonner.
    """
    for reste in range(tentatives - 1, -1, -1):
        try:
            os.replace(source, cible)
            return
        except PermissionError:
            if reste == 0:
                raise
            time.sleep(pause)


def ecrire_octets(chemin, octets, prefixe=".tmp-"):
    """Ecrit `octets` dans `chemin` : un lecteur voit l'ancien ou le neuf, jamais entre.

    Le temporaire va dans le MEME dossier que la cible : `os.replace` n'est
    atomique qu'a l'interieur d'un volume, et /tmp peut etre un autre systeme de
    fichiers. Le `fsync` precede le remplacement, sinon une coupure de courant
    laisse un fichier de la bonne taille rempli de zeros.
    """
    chemin = os.fspath(chemin)
    dossier = os.path.dirname(chemin) or "."
    os.makedirs(dossier, exist_ok=True)

    fd, tmp = tempfile.mkstemp(prefix=prefixe, suffix=".tmp", dir=dossier)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(octets)
            f.flush()
            os.fsync(f.fileno())
        remplacer(tmp, chemin)
        tmp = None
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)


def ecrire_texte(chemin, texte, prefixe=".tmp-"):
    """Comme `ecrire_octets`, en UTF-8 et en fins de ligne LF.

    Les fins de ligne sont forcees : un kit qui s'installe sur Windows et sur
    Linux ne peut pas laisser la plateforme decider du contenu de ses fichiers.
    """
    ecrire_octets(chemin, texte.encode("utf-8"), prefixe=prefixe)
