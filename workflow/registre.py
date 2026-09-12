#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Registre federe : la vue transverse, DERIVEE et jamais ecrite en double.

CE QUE LE REGISTRE RESOUT
-------------------------
`ListAgents` rend soixante sessions sans dire sur quoi elles travaillent. Un orchestrateur
-- humain ou agent -- est aveugle. Le registre repond a trois questions qu'aucun depot
ne peut repondre seul : qui travaille ou en ce moment, ce qui reste ouvert tous depots
confondus, et ce qui s'est passe.

UNE INFORMATION, UN LIEU D'AUTORITE (D-10)
------------------------------------------
Le premier reflexe est d'ecrire dans le backlog du projet ET dans un master central.
C'est ce qu'il ne faut pas faire : deux copies ne divergent pas parfois, elles divergent.
Il suffit que la premiere ecriture reussisse et la seconde echoue -- agent tue entre les
deux, verrou pris, registre injoignable -- pour obtenir deux verites sans moyen de savoir
laquelle ment. Et aucun hook ne rend atomiques deux ecritures dans deux depots Git
distincts : il peut verifier qu'on a ecrit, jamais garantir la coherence.

Le master ne se REMPLIT donc pas, il se CALCULE :

    backlog du projet   AUTORITE   ecrit par l'agent, une seule fois
    presence.json       ecrit      qui travaille ou, maintenant -- volatil, NON versionne
    journal.jsonl       ajoute     ce qui s'est passe -- append-only, versionne
    *-MASTER.md         GENERE     agregat, jamais edite

C'est le motif deja etabli dans ProlexCore : `Html_actif/PROLEXCORE-SKILLS.html` est
rendu par script et ne s'edite jamais a la main.

POURQUOI LA PRESENCE N'EST PAS VERSIONNEE
-----------------------------------------
Cinq sessions ecrivant un fichier suivi par Git, c'est un conflit de fusion par commit.
La presence decrit l'INSTANT : elle n'a pas a survivre. Le journal, lui, est append-only
-- ses conflits se resolvent en gardant les deux jeux, comme le journal de ProlexCore.
"""

import hashlib
import json
import os
from datetime import datetime, timedelta

from . import journal as jrn
from .etat import lire as lire_etat, modifier, empreinte as empreinte_etat
from .atomique import ecrire_texte
from .verrou import verrou


class RegistreIllisible(RuntimeError):
    """Le fichier des depots existe mais ne se lit pas.

    Distincte de l'absence : un registre ABSENT vaut « aucun depot federe »,
    un registre ILLISIBLE ne vaut rien et ne doit surtout pas etre pris pour
    zero. Mesure du 2026-09-09 : les deux etaient confondus, et un
    depots.json tronque faisait regenerer les masters a « 0 depot » en
    annoncant leur mise a jour.
    """

PRESENCE = "presence.json"
JOURNAL = "journal.jsonl"
DEPOTS = "depots.json"
COMPTEURS = "compteurs.json"
BACKLOG_MASTER = "BACKLOG-MASTER.md"
TODO_MASTER = "TODO-MASTER.md"

# F04 : borne le temps qu'un `todo add` peut perdre a attendre ce compteur.
# Court a dessein -- ce n'est pas `depots.json` (rare, un enregistrement par
# federation) mais un fichier touche a CHAQUE tache creee : un delai long y
# ferait sentir la moindre contention. `taches._prochain_id` se replie sur le
# comportement local des que ce delai est depasse (jamais d'echec de todo
# add a cause du registre).
DELAI_COMPTEUR_DEFAUT = 2.0

ENTETE = (
    "> **Fichier généré par le kit agent-workflow. Ne pas éditer à la main.**\n"
    "> Il agrège les backlogs des dépôts fédérés ; chaque dépôt reste seule autorité\n"
    "> sur le sien. Régénérer avec `workflow.py master`.\n"
)


def chemin(registre, quoi):
    return os.path.join(registre, quoi)


def _maintenant():
    return datetime.now().astimezone().isoformat(timespec="seconds")


# ---------------------------------------------------------------- presence

def declarer(registre, agent, depot, surface=None, tache=None, motif=None):
    """Annonce ou un agent travaille. Ecrase sa propre entree, jamais celle d'un autre.

    `surface` dit OU, `motif` dit POURQUOI. Le second n'est pas decoratif : quand deux
    surfaces se recouvrent, c'est le motif qui permet a l'un des deux agents de contester
    -- et c'est ce qui a evite trois collisions le 2026-08-31, par des messages en prose
    qu'aucune machine ne pouvait relire.
    """
    os.makedirs(registre, exist_ok=True)
    p = chemin(registre, PRESENCE)
    with modifier(p) as etat:
        etat.setdefault("agents", {})[agent] = {
            "depot": depot, "surface": surface, "tache": tache,
            "motif": motif, "vu": _maintenant(),
        }
        etat.pop("taches", None)
        etat.pop("claims", None)
        etat.pop("documents", None)
    jrn.ajouter(chemin(registre, JOURNAL), "surface-declaree", agent,
                cible=depot, tache=tache,
                detail=" -- ".join(x for x in (surface, motif) if x) or None)
    return p


def retirer(registre, agent):
    p = chemin(registre, PRESENCE)
    with modifier(p) as etat:
        etat.setdefault("agents", {}).pop(agent, None)
    return p


def presences(registre, fraicheur_heures=12):
    """Rend [(agent, info, frais)] -- `frais` dit si la declaration est recente.

    On ne supprime PAS les declarations anciennes : la meme raison que pour les claims
    orphelins -- un agent lent et un agent parti se ressemblent. On les marque.
    """
    etat = lire_etat(chemin(registre, PRESENCE), defaut={})
    limite = datetime.now().astimezone() - timedelta(hours=fraicheur_heures)
    sortie = []
    for agent, info in sorted(etat.get("agents", {}).items()):
        try:
            frais = datetime.fromisoformat(info.get("vu", "")) >= limite
        except ValueError:
            frais = False
        sortie.append((agent, info, frais))
    return sortie


# ---------------------------------------------------------------- depots federes

def depots(registre):
    """Chemins des depots federes. NON VERSIONNE : ces chemins sont propres a la machine.

    Un chemin absolu vers un depot ne survit pas au changement de machine ; le fichier
    est donc local, et se reconstruit en une commande apres la migration.
    """
    p = chemin(registre, DEPOTS)
    try:
        with open(p, encoding="utf-8") as f:
            contenu = f.read()
    except FileNotFoundError:
        return []                      # aucun depot federe : cas normal
    try:
        return json.loads(contenu).get("depots", [])
    except json.JSONDecodeError as e:
        # NE PAS rendre [] ici. Mesure du 2026-09-09 : un depots.json tronque
        # faisait regenerer les masters a « 0 depot » en annoncant leur mise a
        # jour -- la federation entiere disparaissait sans un mot. « Aucun
        # depot » et « je n'ai pas pu lire » ne sont pas le meme resultat.
        raise RegistreIllisible(
            "%s est illisible (%s). La federation n'est PAS vide : elle est "
            "inconnue. Reparer le fichier ou le supprimer pour repartir de zero."
            % (p, e)) from e


def enregistrer_depot(registre, racine_depot):
    """Ajoute un depot a la federation, sous verrou et par ecriture atomique.

    SANS LE VERROU, mesure du 2026-09-09 : 79 enregistrements sur 100 etaient
    perdus, et chacun annoncait sa reussite. La sequence est un
    lire-modifier-ecrire ; deux processus lisent la meme liste, chacun y ajoute
    le sien, le dernier ecrit efface l'autre. Le verrou serialise, l'ecriture
    atomique protege le lecteur qui, lui, ne verrouille pas.
    """
    os.makedirs(registre, exist_ok=True)
    p = chemin(registre, DEPOTS)
    racine_depot = os.path.abspath(racine_depot)
    with verrou(p + ".lock", delai=10.0):
        liste = depots(registre)
        if racine_depot not in liste:
            liste.append(racine_depot)
            liste.sort()
            ecrire_texte(p, json.dumps({"depots": liste}, ensure_ascii=False,
                                       indent=2) + "\n")
    return liste


# ---------------------------------------------------------------- identifiants federes (F04)

def prochain_identifiant(registre, identite, minimum, delai=DELAI_COMPTEUR_DEFAUT):
    """Alloue et RETIENT le prochain numero pour `identite`. Rend un entier.

    F04 (T-170) : deux clones du meme depot appellent ceci avec la MEME
    `identite` (voir `config.identite_depot`) -- c'est ce partage, VOULU, qui
    leur interdit de s'attribuer deux fois le meme T-NNN.

    SOUS VERROU, meme patron qu'`enregistrer_depot` : la sequence est un
    lire-modifier-ecrire, et deux clones peuvent l'executer au meme instant.
    `minimum` est le plus grand numero deja vu localement par l'appelant --
    le compteur ne peut jamais RECULER en dessous : un depot qui porte deja
    T-005 ne doit jamais se voir proposer T-002 parce que le registre n'a
    encore rien enregistre pour son identite.

    `delai` est COURT et BORNE a dessein (voir `DELAI_COMPTEUR_DEFAUT`) :
    l'appelant (`taches._prochain_id`) se replie sur le seul `minimum` au
    premier `VerrouIndisponible` -- un registre lent ou dispute ne doit
    jamais retarder un `todo add` de facon perceptible.

    Un `compteurs.json` illisible (JSON tronque) leve `RegistreIllisible`,
    comme `depots()` pour `depots.json` : on ne le confond pas avec « aucun
    numero encore alloue », et l'appelant s'en remet au meme repli que pour
    un verrou indisponible.
    """
    os.makedirs(registre, exist_ok=True)
    p = chemin(registre, COMPTEURS)
    with verrou(p + ".lock", delai=delai):
        try:
            with open(p, encoding="utf-8") as f:
                contenu = f.read()
        except FileNotFoundError:
            contenu = ""
        try:
            compteurs = json.loads(contenu) if contenu.strip() else {}
        except json.JSONDecodeError as e:
            raise RegistreIllisible(
                "%s est illisible (%s). Reparer le fichier ou le supprimer pour "
                "repartir de zero -- le compteur repart alors du maximum local "
                "de chaque depot, jamais en dessous." % (p, e)) from e
        dernier = compteurs.get(identite, 0)
        prochain = max(minimum, dernier) + 1
        compteurs[identite] = prochain
        ecrire_texte(p, json.dumps(compteurs, ensure_ascii=False, indent=2,
                                   sort_keys=True) + "\n")
    return prochain


# ---------------------------------------------------------------- agregation

def _lire_depot(racine):
    """Rend (nom, taches, claims, ecart) ou None si le depot est injoignable.

    Un depot absent n'interrompt JAMAIS l'agregation : il est signale dans le master.
    Refuser de generer parce qu'un disque est demonte rendrait le registre inutilisable
    au pire moment.

    `ecart` porte B-D : True si l'empreinte declaree par le depot ne correspond
    pas a son etat reel. Un depot qui n'en declare aucune n'est PAS en ecart --
    il n'a simplement pas encore ete touche par une version qui les ecrit.
    """
    etat = os.path.join(racine, ".workflow", "state.json")
    if not os.path.exists(etat):
        return None
    d = lire_etat(etat)
    taches, claims = d.get("taches", {}), d.get("claims", {})
    declaree = d.get("empreinte")
    # UNE SEULE implementation de l'empreinte, celle d'etat.py. Deux copies
    # divergeraient au premier changement de format, et le master crierait sur
    # des depots sains.
    ecart = bool(declaree) and declaree != empreinte_etat(d)
    return os.path.basename(os.path.abspath(racine)), taches, claims, ecart


def agreger(registre):
    """Rend le master unique, en deux sections (actives, en reserve). Purement calcule."""
    lignes_todo = ["## Tâches actives", ""]
    lignes_bl = ["## Tâches en réserve", ""]
    injoignables = []
    en_ecart = []          # B-D : empreinte declaree != etat reel
    total_todo = total_bl = 0

    for racine in depots(registre):
        lu = _lire_depot(racine)
        if lu is None:
            injoignables.append(racine)
            continue
        nom, taches, claims, ecart = lu
        if ecart:
            # B-D : on AGREGE QUAND MEME, et on le dit. Refuser d'agreger rendrait
            # le master inutilisable des qu'un depot a ete touche a la main -- or
            # c'est justement ce moment-la qu'il faut pouvoir lire.
            en_ecart.append(nom)
        actives = {i: t for i, t in taches.items() if t.get("etat") != "close"}
        todo = sorted((i, t) for i, t in actives.items() if t.get("niveau") == "todo")
        backlog = sorted((i, t) for i, t in actives.items() if t.get("niveau") == "backlog")

        for titre, groupe, cible in (("todo", todo, lignes_todo),
                                     ("backlog", backlog, lignes_bl)):
            cible.append("### %s" % nom)
            cible.append("")
            if not groupe:
                cible.append("_(rien d'ouvert)_")
                cible.append("")
                continue
            for ident, t in groupe:
                # Les identifiants sont prefixes par depot : T-001 existe dans chaque
                # depot, et le master les melangerait sans cela.
                marque = ""
                if ident in claims:
                    marque = " — `%s`" % claims[ident]["agent"]
                if t.get("corrige"):
                    marque += " — corrige %s/%s" % (nom, t["corrige"])
                cible.append("- [ ] **%s/%s** %s%s" % (nom, ident, t.get("titre", "?"), marque))
            cible.append("")
        total_todo += len(todo)
        total_bl += len(backlog)

    for lignes, total, quoi in ((lignes_todo, total_todo, "actives"),
                                (lignes_bl, total_bl, "en réserve")):
        lignes.insert(2, "_%d tâches %s, %d dépôt(s) fédéré(s)._" % (
            total, quoi, len(depots(registre)) - len(injoignables)))
    # B-D : le bandeau d'ecart va en TETE de chaque section -- c'est la premiere
    # chose qu'un lecteur doit savoir avant de lire le reste. On agrege quand
    # meme : refuser rendrait le master inutilisable au moment precis ou il faut
    # pouvoir le lire.
    if en_ecart:
        for cible in (lignes_todo, lignes_bl):
            cible.insert(2, "> ⚠ **Empreinte divergente** : %s. Leur état a bougé hors "
                            "protocole depuis leur dernière déclaration —\n"
                            "> les lignes ci-dessous restent à lire comme des données."
                         % ", ".join(sorted(en_ecart)))

    if injoignables:
        for lignes_ in (lignes_todo, lignes_bl):
            lignes_.append("### Dépôts injoignables")
            lignes_.append("")
            for r in injoignables:
                lignes_.append("- `%s` — pas de `.workflow/state.json`" % r)
            lignes_.append("")

    lignes = ["# Backlog master", "", ENTETE, ""]
    lignes.extend(lignes_todo)
    lignes.append("")
    lignes.extend(lignes_bl)
    return "\n".join(lignes).rstrip() + "\n"


def ecrire_masters(registre):
    """Genere le master unique. Rend la liste des changements REELS (ecriture, retrait).

    SOUS VERROU, comme `enregistrer_depot` : `agreger()` LIT l'etat de tous les
    depots federes puis on ECRIT le resultat -- la meme classe de sequence, meme
    si ce n'est pas un lire-modifier-ecrire sur un fichier partage. Mesure du
    2026-09-11 (T-176bis) : sans le verrou, deux appels concurrents -- le hook
    post-commit tourne desormais sur CHAQUE commit qui touche un backlog, dans
    CHAQUE depot federe -- peuvent lire un instantane differ, et celui qui a lu
    le plus vieux ecrire APRES l'autre, effacant en silence la tache la plus
    recente d'un depot pendant que son propre hook annonce le succes. Le verrou
    vit ICI plutot que chez l'appelant : il protege aussi `cmd_master`, qui
    appelle cette fonction sans jamais avoir pris de verrou lui-meme.
    """
    from .synchro import _ecrire_si_different
    os.makedirs(registre, exist_ok=True)
    changes = []
    with verrou(chemin(registre, BACKLOG_MASTER) + ".lock", delai=10.0):
        if _ecrire_si_different(chemin(registre, BACKLOG_MASTER), agreger(registre)):
            changes.append(BACKLOG_MASTER)
        # D54 : TODO-MASTER.md n'est plus genere -- un fichier genere qui traine,
        # jamais mis a jour, ment par silence (piege 48).
        ancien = chemin(registre, TODO_MASTER)
        if os.path.exists(ancien):
            os.remove(ancien)
            changes.append("%s (retiré)" % TODO_MASTER)
    return changes
