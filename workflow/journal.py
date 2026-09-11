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

ROTATION PAR TAILLE, LOCALE (F21)
----------------------------------
Le journal grossit sans fin -- mesure du 2026-09-11 sur ProlexCore : 839 lignes,
247 Ko. `lire()` et `chercher()` le rechargent en entier a chaque appel. La premisse
d'origine d'une rotation MENSUELLE etait de servir des fusions Git qui n'existent
plus : le journal est ignore par git depuis ba80259 (aucun conflit a fusionner).
Reste la seule vraie contrainte : borner ce qu'un appel relit.

La rotation se declenche a l'AJOUT, quand le fichier courant a deja atteint le
seuil : il devient une archive numerotee dans le MEME dossier -- `journal.1.jsonl`,
l'ancienne `.1` glissant vers `.2`, et ainsi de suite -- puis un fichier courant
neuf recoit la ligne qui vient d'etre ecrite. Le decalage se fait SOUS LE MEME
VERROU que l'ajout : jamais deux agents ne tournent en meme temps, jamais une
rotation ne court-circuite un ajout en cours. `os.replace` est atomique sur POSIX
et sur Windows pour un renommage sur le meme volume -- pas de fenetre ou un fichier
porterait deux noms, pas de fenetre ou il n'en porterait aucun.

`lire()` et `chercher()` parcourent les archives puis le fichier courant, dans
l'ordre CHRONOLOGIQUE -- la plus ancienne archive d'abord -- un fichier a la fois,
sans jamais charger l'ensemble en memoire. Aucune ligne n'est perdue ni dupliquee :
la rotation deplace des fichiers entiers, elle ne touche jamais au contenu d'une
ligne.
"""

import json
import os
from datetime import datetime

from .verrou import verrou

# Seuil de rotation, en octets. 1 Mo par defaut -- assez grand pour ne jamais gener
# une lecture normale, assez petit pour que la rotation reste un evenement rare.
# Les tests le surchargent via le parametre `seuil_rotation` d'`ajouter()`, jamais
# en modifiant cette constante : une constante de module changee par un test reste
# changee pour les tests suivants dans le meme process.
SEUIL_ROTATION_OCTETS = 1_000_000

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


def _chemin_archive(chemin, numero):
    """`.../journal.jsonl` + 2 -> `.../journal.2.jsonl`."""
    racine, ext = os.path.splitext(chemin)
    return "%s.%d%s" % (racine, numero, ext)


def archives(chemin):
    """Les archives numerotees deja sur le disque, triees NUMERO CROISSANT.

    `.1` est la derniere rotation -- la plus RECENTE des archives. Le numero le
    plus eleve est la plus ANCIENNE. Une liste vide si aucune rotation n'a encore
    eu lieu. Lu depuis le disque a chaque appel -- jamais mis en cache -- pour
    rester juste apres une rotation faite par un autre processus.
    """
    dossier = os.path.dirname(chemin) or "."
    base = os.path.basename(chemin)
    racine, ext = os.path.splitext(base)
    prefixe = racine + "."
    try:
        noms = os.listdir(dossier)
    except FileNotFoundError:
        return []
    trouvees = []
    for nom in noms:
        if not (nom.startswith(prefixe) and (not ext or nom.endswith(ext))):
            continue
        milieu = nom[len(prefixe):len(nom) - len(ext)]
        if milieu.isdigit():
            trouvees.append((int(milieu), os.path.join(dossier, nom)))
    trouvees.sort(key=lambda t: t[0])
    return trouvees


def fichiers(chemin):
    """Tous les fichiers du journal ROTATIF, dans l'ordre CHRONOLOGIQUE.

    La plus ancienne archive d'abord, le fichier courant en dernier -- c'est
    l'ordre que suivent `lire()` et `chercher()`. Un lecteur qui doit parcourir a
    rebours (le plus RECENT d'abord, avec sortie anticipee) n'a qu'a inverser
    cette liste : `orchestration.backlogs_bouges` fait exactement cela.
    """
    return [c for _, c in reversed(archives(chemin))] + [chemin]


def _rotation_necessaire(chemin, seuil):
    if not seuil or seuil <= 0:
        return False
    try:
        return os.path.getsize(chemin) >= seuil
    except FileNotFoundError:
        return False


def _tourner(chemin):
    """Decale chaque archive d'un cran (n -> n+1) puis pousse le fichier COURANT
    en `.1`. A appeler SOUS LE VERROU DE `chemin` -- jamais seul : deux decalages
    simultanes ecraseraient l'un l'autre, et une rotation qui croiserait un ajout
    laisserait une ligne partir dans le mauvais fichier.

    Le decalage se fait du plus GRAND numero vers le plus petit : dans l'ordre
    inverse, glisser `.1` vers `.2` en premier ecraserait un `.2` deja present
    avant qu'il ait lui-meme ete pousse vers `.3`. `os.replace` est un renommage
    atomique sur POSIX comme sur Windows pour un meme volume : jamais de fenetre
    ou le fichier porterait deux noms ou aucun.
    """
    for numero, chemin_archive in sorted(archives(chemin), key=lambda t: -t[0]):
        os.replace(chemin_archive, _chemin_archive(chemin, numero + 1))
    os.replace(chemin, _chemin_archive(chemin, 1))


def ajouter(chemin, evenement, agent, cible=None, tache=None, detail=None,
            seuil_rotation=SEUIL_ROTATION_OCTETS, **extra):
    """Ajoute une ligne. Rend l'entree ecrite.

    `agent`  -- identite de la session (WORKFLOW_AGENT), jamais anonyme.
    `cible`  -- chemin RELATIF au depot, ou identifiant. Jamais un chemin absolu.
    `tache`  -- l'identifiant de tache dans laquelle l'action s'inscrit, si elle existe.
    `seuil_rotation` -- octets au-dela desquels le fichier courant tourne AVANT
        de recevoir cette ligne. 0 ou None desactive la rotation. Le defaut est
        `SEUIL_ROTATION_OCTETS` ; les tests passent une valeur plus petite pour
        forcer la rotation sans ecrire un fichier reel de plusieurs Mo.
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
        # AVANT d'ecrire : si le fichier courant a deja atteint le seuil, il
        # devient une archive et cette ligne ouvre le fichier neuf. Le controle
        # et le decalage vivent SOUS LE MEME VERROU que l'ecriture qui suit :
        # aucun autre agent ne peut ni ajouter ni tourner entre les deux.
        if _rotation_necessaire(chemin, seuil_rotation):
            _tourner(chemin)
        with open(chemin, "a", encoding="utf-8", newline="\n") as f:
            f.write(ligne)
            f.flush()
            os.fsync(f.fileno())
    return entree


def _lire_un_fichier(chemin):
    """Itere les entrees d'UN fichier. Une ligne illisible est SIGNALEE, jamais
    ignoree en silence -- meme regle que pour le fichier courant, une archive
    n'est jamais moins fiable.
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


def lire(chemin):
    """Itere les entrees, archives puis fichier courant, dans l'ordre chronologique.

    Ignorer une ligne cassee ferait rendre au journal un historique incomplet en se
    presentant comme complet -- pire qu'une erreur franche. Un fichier a la fois,
    jamais tout charge en memoire : le cout d'un parcours complet reste celui du
    nombre total de lignes, pas celui de les garder toutes en RAM a la fois.
    """
    for f in fichiers(chemin):
        yield from _lire_un_fichier(f)


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
