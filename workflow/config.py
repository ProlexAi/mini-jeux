#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ou sont les choses : racine du depot, etat local, registre central.

LE PROBLEME QUE CE MODULE RESOUT
--------------------------------
Un kit installe dans N depots doit trouver trois choses sans qu'aucun chemin absolu ne
soit versionne :

    la racine du depot      -- pour que tout le reste soit relatif
    l'etat local            -- <racine>/.workflow/
    le registre central     -- ailleurs sur la machine, donc HORS du depot

Le troisieme est le piege. Un chemin absolu vers ProlexCore ecrit dans un fichier
versionne casse le jour ou la machine change -- et la bascule vers Kubuntu 26.04 est
annoncee. Il vient donc de l'ENVIRONNEMENT, jamais du depot :

    PROLEX_REGISTRE=/chemin/vers/registre

a defaut, `.workflow/local.json`, qui n'est PAS versionne (l'installeur l'ajoute au
.gitignore). Un depot clone sur une autre machine n'herite d'aucun chemin mort.

LE PIEGE DU WORKTREE, DEJA PAYE DANS CE DEPOT
---------------------------------------------
`.git` est un DOSSIER dans un checkout normal et un FICHIER dans un worktree. Tester
`os.path.isdir(".git")` fait donc echouer toute detection dans un worktree -- c'est
exactement le defaut d'`install.sh` du rapport, qui installait ses hooks nulle part en
sortant avec un code 0. On demande donc a Git, on ne devine pas.
"""

import json
import os
import subprocess

DOSSIER_ETAT = ".workflow"


class HorsDepot(RuntimeError):
    def __init__(self, depart):
        super().__init__(
            "aucun depot Git trouve depuis %s\n"
            "Le kit s'installe DANS un depot : son etat suit l'historique du projet."
            % depart)


def _git(args, cwd):
    """Interroge Git. Rend None plutot que de lever : l'appelant decide."""
    try:
        r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True,
                           timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def racine(depart=None):
    """Racine du depot de travail. Fonctionne dans un worktree comme dans un checkout."""
    depart = os.path.abspath(depart or os.getcwd())
    trouve = _git(["rev-parse", "--show-toplevel"], depart)
    if trouve:
        return os.path.abspath(trouve)

    # Repli sans Git : on remonte en acceptant `.git` fichier OU dossier.
    courant = depart
    while True:
        if os.path.exists(os.path.join(courant, ".git")):
            return courant
        parent = os.path.dirname(courant)
        if parent == courant:
            raise HorsDepot(depart)
        courant = parent


def dossier_hooks(depart=None):
    """Ou vivent VRAIMENT les hooks. On le DEMANDE a Git, on ne le deduit jamais.

    `core.hooksPath` PASSE AVANT TOUT LE RESTE. Un depot qui le definit -- comme
    ProlexDashBoard, qui pointe vers `.githooks` -- n'execute JAMAIS ce qui se trouve
    dans `.git/hooks`. Mesure le 2026-08-31 : les hooks y avaient ete poses, le controle
    disait « conforme », et rien ne s'executait.

    Ensuite seulement le git-common-dir, partage par tous les worktrees : dans un
    worktree, `<worktree>/.git` est un FICHIER et `.git/hooks` n'existe pas.
    """
    depart = os.path.abspath(depart or os.getcwd())

    perso = _git(["config", "--get", "core.hooksPath"], depart)
    if perso:
        chemin = os.path.expanduser(perso)
        if not os.path.isabs(chemin):
            chemin = os.path.join(racine(depart), chemin)
        return os.path.abspath(chemin)

    commun = _git(["rev-parse", "--path-format=absolute", "--git-common-dir"], depart)
    if not commun:
        commun = os.path.join(racine(depart), ".git")
    return os.path.join(os.path.abspath(commun), "hooks")


def racine_partagee(depart=None):
    """Le checkout PRINCIPAL, demande a Git -- jamais deduit d'un chemin.

    Depuis un worktree, `--git-common-dir` rend le `.git` du principal ; sa maison
    est le dossier parent. Depuis le principal, il rend le meme chemin, donc la
    fonction est l'identite la ou il n'y a qu'un seul arbre.

    POURQUOI ELLE EXISTE. `racine()` utilise `--show-toplevel`, qui rend le
    WORKTREE. L'etat des taches suivait donc chaque arbre de travail, et le
    2026-09-08 ce depot en portait TROIS divergents : 56 taches dans le principal,
    52 dans le worktree `orchestrateur`, 44 dans `demarrage-suite` -- avec deux
    taches closes dans l'un et ouvertes dans l'autre. Aucune erreur, aucun signal.

    Le defaut etait structurel ici : le canon du depot IMPOSE de travailler en
    worktree. Un etat de taches decrit un DEPOT, pas une branche.
    """
    depart = os.path.abspath(depart or os.getcwd())
    commun = _git(["rev-parse", "--path-format=absolute", "--git-common-dir"], depart)
    if commun:
        return os.path.dirname(os.path.abspath(commun))
    return racine(depart)


def dossier_etat(rac=None):
    """Ou vit l'etat PARTAGE : un seul par depot, quel que soit le worktree.

    `rac` explicite reste respecte -- les tests fabriquent des depots jetables et
    doivent pouvoir viser un chemin precis sans que Git s'en mele.
    """
    if rac is not None:
        return os.path.join(rac, DOSSIER_ETAT)
    return os.path.join(racine_partagee(), DOSSIER_ETAT)


def chemin_etat(rac=None):
    return os.path.join(dossier_etat(rac), "state.json")


def chemin_journal(rac=None):
    return os.path.join(dossier_etat(rac), "journal.jsonl")


def orchestrateur(rac=None):
    """Le nom de l'agent qui orchestre ce depot, ou None.

    Declare dans `local.json` -- non versionne, propre a la machine. Une variable
    d'environnement serait aussi libre que WORKFLOW_AGENT, donc aussi usurpable :
    un garde qui ne garde rien.

    Personne de declare = personne n'a le droit de retirer la presence d'autrui.
    C'est le bon defaut : un depot qui n'a pas nomme son orchestrateur n'a pas
    non plus besoin qu'on y arbitre a sa place.
    """
    return (lire_local(rac) or {}).get("orchestrateur")


def suis_orchestrateur(rac=None, agent=None):
    o = orchestrateur(rac)
    return bool(o) and (agent or globals()["agent"]()) == o


def chemin_local(rac=None):
    """Reglages propres a CETTE machine. Jamais versionne."""
    return os.path.join(dossier_etat(rac), "local.json")


def lire_local(rac=None):
    try:
        with open(chemin_local(rac), encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def registre(rac=None):
    """Chemin du registre central, ou None s'il n'est pas configure.

    None n'est PAS une erreur : un depot peut utiliser le kit seul, sans federation.
    Le kit doit rester utile hors de toute installation centrale -- et R-19 exige qu'un
    registre injoignable ne bloque jamais un commit.
    """
    depuis_env = os.environ.get("PROLEX_REGISTRE")
    if depuis_env:
        return os.path.abspath(os.path.expanduser(depuis_env))
    depuis_local = lire_local(rac).get("registre")
    if depuis_local:
        return os.path.abspath(os.path.expanduser(depuis_local))
    return None


def nom_depot(rac=None):
    """Nom court du depot, pour prefixer les identifiants dans les masters."""
    rac = rac or racine()
    return os.path.basename(os.path.abspath(rac))


def agent():
    """Identite de la session. Un agent anonyme rend le journal inexploitable."""
    return os.environ.get("WORKFLOW_AGENT") or ""


def noms_alloues(rac=None):
    """Les noms d'agents que ce depot accepte, ou None si le depot n'en declare aucun.

    None et [] ne sont PAS la meme chose : aucune declaration signifie « ce depot
    n'a pas d'autorite de nommage, tout nom passe » ; une liste vide signifie
    « aucun nom n'est alloue », donc plus rien ne passe. Confondre les deux
    fermerait un depot entier sur une cle oubliee.
    """
    local = lire_local(rac) or {}
    if "agents" not in local:
        return None
    valeur = local.get("agents")
    return list(valeur) if isinstance(valeur, (list, tuple)) else None


class NomNonAlloue(RuntimeError):
    """A1 : le nom declare n'est pas dans la liste que ce depot alloue.

    BARRIERE CONTRE LA NEGLIGENCE, PAS CONTRE LA MALVEILLANCE -- choix assume au
    canon (A1). Un agent compromis lit `local.json` aussi bien que le CLI. Ce que
    ce garde attrape : la faute de frappe, le nom recycle d'une session
    precedente, l'agent lance sans que personne ne lui ait donne le sien.
    """

    def __init__(self, nom, alloues):
        super().__init__(
            "WORKFLOW_AGENT vaut %r, que ce depot n'alloue pas.\n"
            "  Noms alloues : %s\n"
            "  Les declarer dans .workflow/local.json : {\"agents\": [\"...\"]}\n"
            "  Retirer la cle \"agents\" laisse passer tous les noms."
            % (nom, ", ".join(sorted(alloues)) or "aucun"))


class AgentNonDeclare(RuntimeError):
    def __init__(self):
        super().__init__(
            "WORKFLOW_AGENT n'est pas defini.\n"
            "Chaque session porte une identite unique, sinon le journal ne peut plus dire "
            "qui a fait quoi -- et c'est la seule chose qu'il sait faire.\n"
            "    Windows  : $env:WORKFLOW_AGENT = 'claude-1'\n"
            "    Linux    : export WORKFLOW_AGENT=claude-1")


def agent_obligatoire(rac=None):
    """L'identite de la session : forme valide, puis nom alloue (A1).

    LA FORME AVANT L'ALLOCATION. Un WORKFLOW_AGENT multiligne forgeait une entree
    de journal attribuee a un faux agent -- et il l'aurait fait meme sur un depot
    qui alloue ses noms, puisque « agent-un\nfaux-agent » n'est pas
    « agent-un ». Valider la forme d'abord ferme les deux.
    """
    nom = agent()
    if not nom:
        raise AgentNonDeclare()
    from .taches import valider_texte, MAX_AGENT
    nom = valider_texte(nom, "WORKFLOW_AGENT", MAX_AGENT)
    alloues = noms_alloues(rac)
    if alloues is not None and nom not in alloues:
        raise NomNonAlloue(nom, alloues)
    return nom


def correlation():
    """L'identifiant qui relie les lignes d'une meme chaine, a travers les depots.

    Vide par defaut : le kit fonctionne tres bien sans, et un identifiant invente
    a chaque commande ne relierait rien. Il se propage par l'environnement, comme
    un identifiant de requete -- l'orchestrateur le pose, les agents qu'il lance
    en heritent.
    """
    return os.environ.get("WORKFLOW_CORRELATION") or ""
