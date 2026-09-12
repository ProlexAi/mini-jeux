#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""workflow.py -- le protocole, en une seule commande.

    workflow.py snapshot                       etat complet, a lire en debut de session
    workflow.py todo add "..." [--corrige T-x]  cree une tache
    workflow.py claim T-003 [--surface ...]     reserve (refus explicite si prise)
    workflow.py status <doc> in-progress        change le statut d'un document
    workflow.py todo done T-003 [--verif "..."] clot (sort du TODO, reste au journal)
    workflow.py log "decision X car Y"          trace

Tout agent -- Claude Code, Hermes, modele local -- passe par ici. C'est le contrat
minimal qui rend la coordination possible : lire l'etat avant d'agir, reserver avant de
travailler, cloturer apres verification.

POURQUOI UN CLI ET PAS UNE BIBLIOTHEQUE
---------------------------------------
Le denominateur commun de trois moteurs heterogenes n'est pas un framework Python : c'est
le systeme de fichiers et une ligne de commande. Un modele local qui ne sait qu'appeler
un shell doit pouvoir participer au meme protocole qu'une session Claude Code.
"""

import argparse
import os
import subprocess
import sys

# UTF-8 SUR LA SORTIE, TOUJOURS -- mesure du 2026-08-31.
#
# Sous Windows, `print()` vers un PIPE (et non une console) encode avec la locale, ici
# cp1252. Le TODO genere porte des accents et un tiret cadratin : le consommateur qui
# attend de l'UTF-8 -- un hook, un agent, un autre script -- recoit alors des octets
# invalides et se casse. Trouve par une demonstration, pas par les tests : ceux-ci
# decodaient eux aussi en cp1252 et se accordaient sur l'erreur.
#
# C'est la regle d'`AGENTS.md` §9, appliquee ici a la SORTIE et pas seulement aux
# fichiers : un script qui ecrit correctement sur disque peut mentir sur stdout.
for _flux in (sys.stdout, sys.stderr):
    try:
        _flux.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):  # flux remplace par un objet sans reconfigure
        pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow import (  # noqa: E402
    config, documents, journal as jrn, orchestration, registre as reg, remontee,
    synchro, taches, verrou,
)
from workflow.etat import lire, ecrire, etat_neuf, EtatIllisible  # noqa: E402

def _version():
    """La version vient du fichier VERSION, jamais d'une constante recopiee.

    Mesure du 2026-08-31 : cette constante disait 1.0.0 alors que le kit etait en 1.1.0.
    Deux sources pour une information donnent deux verites -- et c'est la commande
    `version` qui ment, celle-la meme qu'on interroge pour lever un doute.

    Le fichier est cherche a deux endroits : a la racine du kit au socle, et dans
    `.workflow/` chez une cible, ou l'installeur le depose.
    """
    ici = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for candidat in (os.path.join(ici, "VERSION"),
                     os.path.join(ici, ".workflow", "VERSION")):
        try:
            with open(candidat, encoding="utf-8") as f:
                return f.read().strip()
        except OSError:
            continue
    return "inconnue"


def _sortir(message, code=1):
    print(message, file=sys.stderr)
    return code


def _liberer_presence_si_plus_rien(rac, agent):
    """Retire la declaration de presence quand l'agent n'a plus aucune reservation.

    MESURE DU 2026-08-31, TROUVEE PAR L'USAGE ET PAS PAR LES TESTS.
    Clore une tache la retirait bien du TODO, mais laissait la presence en place : les
    agents restaient declares sur leurs surfaces, et le detecteur continuait a signaler un
    chevauchement qui n'existait plus.

    C'est le pire defaut possible pour ce dispositif. Un signal qui persiste apres sa
    cause devient du bruit, et un detecteur bruyant finit desarme -- on cesse de le lire
    avant qu'il n'ait eu raison une seule fois.

    La declaration ne se retire que si l'agent n'a plus RIEN : tant qu'il tient une autre
    tache, il travaille toujours quelque part et doit rester visible.
    """
    registre = config.registre(rac)
    if not registre:
        return
    etat = lire(config.chemin_etat(rac))
    if any(c.get("agent") == agent for c in etat.get("claims", {}).values()):
        return
    try:
        reg.retirer(registre, agent)
    except OSError:
        # Le registre n'est qu'une vue : son indisponibilite n'annule pas une cloture.
        pass


def _regenerer_todo(rac, arbre=None):
    """Remet `TODO.md` a jour APRES toute commande qui change les taches.

    DEUX RACINES : `rac` est celle de l'ETAT (partagee, un seul state.json par
    depot), `arbre` celle du WORKTREE ou l'on ecrit le TODO.md. Sans cette
    separation, une commande jouee dans un worktree reecrivait le TODO.md du
    CHECKOUT PRINCIPAL, ou un autre agent travaille -- son propre arbre ne voyait
    jamais la tache qu'il venait de creer. Mesure du 2026-09-09.

    LA REGENERATION SUIT LA CAUSE, PAS LE COMMIT -- mesure du 2026-08-31.
    La premiere version laissait le `pre-commit` s'en charger, ce qui l'obligeait a mettre
    le fichier en zone d'index a la place de l'agent : un `git add` dans un hook, contre
    la regle du pathspec explicite, et invisible avant coup.

    En regenerant ici, le fichier est juste des l'instant ou la tache change. L'agent le
    commite avec le reste s'il le decide -- ou pas. Personne ne choisit a sa place, et
    l'arbre ne reste jamais sale d'une modification que rien n'explique.

    N'ecrit que si le contenu differe : rejouer une commande ne doit pas toucher le mtime.
    """
    try:
        texte = taches.rendre_todo(config.chemin_etat(rac), config.nom_depot(rac))
        chemin = os.path.join(arbre or config.racine(), config.NOM_BACKLOG)
        return synchro._ecrire_si_different(chemin, texte)
    except OSError as e:
        # Ne jamais faire echouer une commande reussie a cause du fichier genere : la
        # verite est dans l'etat, TODO.md n'en est qu'une vue.
        print("note : %s n'a pas pu etre regenere (%s)" % (config.NOM_BACKLOG, e), file=sys.stderr)
        return False


# ------------------------------------------------------------------ commandes

IGNORES_ETAT = ("state.json", "journal.jsonl", "journal.*.jsonl", "local.json", "*.lock")

EN_TETE_GITIGNORE = """# Ecrit par `workflow.py init`. Rien de ce dossier ne se versionne.
#
# state.json et journal.jsonl decrivent qui travaille sur CETTE machine, en ce
# moment. Versionnes, ils etaient detruits par un `git checkout` de branche, ils
# faisaient allouer le meme identifiant a deux branches, et un conflit de fusion
# rendait toutes les commandes du kit inutilisables. Mesure du 2026-09-09.
#
# journal.*.jsonl : les archives que la rotation par taille (F21) produit --
# journal.1.jsonl, journal.2.jsonl... Meme raison que journal.jsonl lui-meme."""


def _ecrire_gitignore_etat(chemin):
    """Pose ou complete le .gitignore du dossier d'etat, sans jamais ecraser."""
    lignes = []
    if os.path.exists(chemin):
        with open(chemin, encoding="utf-8") as f:
            lignes = [l.rstrip("\n") for l in f]
    # UN SEUL CHEMIN, ET C'EST VOULU. La premiere version en avait deux -- ecrire
    # le gabarit complet si le fichier etait absent, completer sinon. Le sabotage
    # de la liste ne mordait alors que sur la moitie des cas : le test passait
    # par l'autre branche et restait vert. Deux chemins, c'est deux fois plus a
    # prouver, pour la meme propriete.
    manquantes = [m for m in IGNORES_ETAT if m not in lignes]
    if manquantes:
        entete = [] if lignes else EN_TETE_GITIGNORE.splitlines()
        synchro._ecrire_si_different(chemin, "\n".join(entete + lignes + manquantes) + "\n")
    return manquantes


def _sortir_l_etat_de_l_index(rac):
    """Retire l'etat de l'index Git s'il y est. REVERSIBLE : le disque n'est pas touche.

    On ne joue `git rm --cached` que sur ce qui est REELLEMENT suivi -- `git
    ls-files` le dit. Le lancer a l'aveugle rendrait une erreur sur un depot
    neuf, ce qui ferait passer une migration reussie pour un echec.
    """
    suivis = []
    # Seuls les noms LITTERAUX ont un sens ici -- ls-files --error-unmatch sur un
    # motif glob ("*.lock", "journal.*.jsonl") ne dit pas quel fichier PRECIS
    # etait suivi. Aucun n'a jamais ete versionne avant ce .gitignore de toute
    # facon : les exclure du controle ne perd rien.
    for nom in (n for n in IGNORES_ETAT if "*" not in n):
        rel = "%s/%s" % (config.DOSSIER_ETAT, nom)
        r = subprocess.run(["git", "-C", rac, "ls-files", "--error-unmatch", rel],
                           capture_output=True, text=True)
        if r.returncode == 0:
            suivis.append(rel)
    if suivis:
        subprocess.run(["git", "-C", rac, "rm", "--cached", "-q"] + suivis,
                       capture_output=True, text=True)
    return suivis


def cmd_init(args):
    rac = config.racine_partagee()
    os.makedirs(config.dossier_etat(rac), exist_ok=True)
    for sous in ("docs/inbox", "docs/active"):
        os.makedirs(os.path.join(rac, sous), exist_ok=True)

    etat = config.chemin_etat(rac)
    if not os.path.exists(etat):
        ecrire(etat, etat_neuf(config.nom_depot(rac)))

    # RIEN de ce dossier n'est versionne, et les trois raisons sont mesurees :
    #  - un `git checkout` de branche detruisait state.json et journal.jsonl, et
    #    le kit repartait de zero EN SILENCE en reattribuant T-001 ;
    #  - deux branches allouaient le MEME identifiant, et aucune fusion ne pouvait
    #    garder les deux travaux ;
    #  - un state.json conflicte tuait toutes les commandes par un traceback.
    # L'etat dit qui travaille sur CETTE machine maintenant : il n'a aucun sens
    # ailleurs, et le registre porte deja la meme regle pour depots.json.
    gitignore = os.path.join(config.dossier_etat(rac), ".gitignore")
    _ecrire_gitignore_etat(gitignore)
    retires = _sortir_l_etat_de_l_index(rac)

    print("Initialise dans %s" % rac)
    if retires:
        print("  L'etat etait versionne. Retire de l'index (le disque est intact) :")
        for f in retires:
            print("    %s" % f)
        print("  Commiter ce retrait ; `git add` le remettrait si besoin.")
    print("  etat    : %s" % os.path.relpath(etat, rac))
    print("  journal : %s" % os.path.relpath(config.chemin_journal(rac), rac))
    reg = config.registre(rac)
    print("  registre: %s" % (reg if reg else "aucun (federation desactivee)"))
    return 0


def cmd_snapshot(args):
    rac = config.racine_partagee()
    etat = lire(config.chemin_etat(rac))
    tous = etat.get("taches", {})
    claims = etat.get("claims", {})
    moi = config.agent()

    print("Depot   : %s" % config.nom_depot(rac))
    print("Agent   : %s" % (moi or "NON DECLARE -- definir WORKFLOW_AGENT"))
    reg = config.registre(rac)
    print("Registre: %s" % (reg if reg else "aucun"))
    print()

    actives = {i: t for i, t in tous.items() if t.get("etat") != "close"}
    print("Taches  : %d ouvertes, %d closes" % (len(actives), len(tous) - len(actives)))

    if claims:
        print("\nRESERVATIONS EN COURS -- ne pas retraiter ce qui appartient a un autre :")
        for ident in sorted(claims):
            c = claims[ident]
            marque = "  (vous)" if c["agent"] == moi else ""
            titre = tous.get(ident, {}).get("titre", "?")
            print("  %-8s %-22s %s%s" % (ident, c["agent"], titre[:44], marque))
    else:
        print("\nAucune reservation en cours.")

    libres = [(i, t) for i, t in sorted(actives.items())
              if i not in claims and t.get("niveau") == "todo"]
    if libres:
        print("\nA PRENDRE :")
        for ident, t in libres[:12]:
            print("  %-8s %s" % (ident, t["titre"][:60]))
        if len(libres) > 12:
            print("  ... et %d autres" % (len(libres) - 12))

    vieux = taches.orphelins(config.chemin_etat(rac), heures=args.heures)
    if vieux:
        print("\nRESERVATIONS ANCIENNES -- signalees, pas liberees :")
        for ident, agent, age in vieux:
            print("  %-8s %-22s %s" % (ident, agent, age))
        print("  Liberer avec : workflow.py release <id> --force")

    ecarts = documents.verifier(rac)
    if ecarts:
        print("\nECARTS DOCUMENTAIRES (%d) :" % len(ecarts))
        for chemin, quoi in ecarts[:10]:
            print("  %-46s %s" % (chemin[:46], quoi))
    return 0


def cmd_todo_add(args):
    rac = config.racine_partagee()
    agent = config.agent_obligatoire()
    registre = config.registre(rac)
    # F04 (T-170) : l'identite se calcule ICI, UNE SEULE FOIS par appel -- elle
    # invoque git, et rien ne doit repeter cet appel par tache. None quand
    # aucun registre n'est configure : inutile d'interroger git pour une
    # valeur que `taches.ajouter` n'utiliserait de toute facon pas.
    identite = config.identite_depot(rac) if registre else None
    try:
        ident = taches.ajouter(config.chemin_etat(rac), args.titre, agent,
                               niveau="todo" if args.actif else "backlog",
                               corrige=args.corrige,
                               chemin_journal=config.chemin_journal(rac),
                               depend_de=args.depend_de or None,
                               allowed_paths=args.allowed_paths or None,
                               acceptance=args.acceptance,
                               registre=registre, identite=identite)
    except taches.TacheInconnue as e:
        return _sortir(str(e))
    _regenerer_todo(rac)
    print("%s cree (%s)" % (ident, "todo" if args.actif else "backlog"))
    if args.corrige:
        print("  corrige %s -- le lien existe dans les deux sens" % args.corrige)
    if args.depend_de:
        print("  depend de %s -- non reservable tant qu'elles restent ouvertes"
              % ", ".join(args.depend_de))
    return 0


def cmd_todo_done(args):
    rac = config.racine_partagee()
    agent = config.agent_obligatoire()
    if not args.verif and not args.sans_verif:
        # B-B : la DoD n'est plus un avertissement qu'on ignore. Matt ne lit pas
        # le code, il lit les AFFIRMATIONS : une cloture sans verification
        # declaree est une affirmation sans preuve.
        return _sortir(
            "cloture refusee : aucune verification declaree.\n"
            "  Une tache n'est terminee que si un critere verifiable est satisfait.\n"
            "    --verif \"ce qui a ete CONSTATE\"   (la commande jouee, sa sortie)\n"
            "  Rien a verifier ici ? Le dire explicitement :\n"
            "    --sans-verif \"pourquoi il n'y a rien a verifier\"")
    if args.sans_verif and len(args.sans_verif.strip()) < 20:
        return _sortir("--sans-verif attend un motif d'au moins 20 caracteres. "
                       "« rien a verifier » n'est pas un motif.")
    # T-016 : le journal sait ce que l'etat des claims a oublie -- une tache jamais
    # reservee et une tache reservee puis liberee sont indiscernables par les seuls
    # claims en cours. Cherche AVANT la cloture : `chercher` ne lit que ce qui existe
    # deja, et `tache-close` n'est pas encore ecrit.
    #
    # Ce pre-check LIT tout le journal, alors que clore() n'a jamais eu besoin que
    # d'y AJOUTER (append, sans lecture). Une ligne corrompue ailleurs dans le
    # journal -- sans aucun rapport avec la tache qu'on ferme -- ne doit donc pas
    # empecher la cloture : meme logique que _liberer_presence_si_plus_rien et
    # _regenerer_todo plus bas, une lecture annexe qui echoue n'annule pas une
    # commande par ailleurs reussie. Le defaut reste signale, jamais avale en
    # silence : juste pas au prix d'un traceback brut ni d'une tache non fermee.
    chemin_journal = config.chemin_journal(rac)
    try:
        jamais_reservee = not any(
            jrn.chercher(chemin_journal, tache=args.tache, evenement="tache-reservee"))
        journal_illisible = None
    except ValueError as e:
        jamais_reservee = False
        journal_illisible = str(e)
    taches.clore(config.chemin_etat(rac), args.tache, agent,
                 verification=args.verif or ("SANS VERIFICATION : " + args.sans_verif),
                 chemin_journal=chemin_journal)
    _regenerer_todo(rac)
    _liberer_presence_si_plus_rien(rac, agent)
    print("%s close. Retiree du TODO, conservee au journal." % args.tache)
    if jamais_reservee:
        print("AVERTISSEMENT : %s close sans avoir jamais ete reservee par claim -- "
              "le registre ne dit pas qui y a travaille." % args.tache)
    elif journal_illisible is not None:
        print("AVERTISSEMENT : impossible de verifier si %s a deja ete reservee -- "
              "journal illisible, a corriger :\n%s" % (args.tache, journal_illisible))
    return 0


def cmd_todo_list(args):
    rac = config.racine_partagee()
    print(taches.rendre_todo(config.chemin_etat(rac), config.nom_depot(rac)), end="")
    return 0


def cmd_promote(args):
    rac = config.racine_partagee()
    agent = config.agent_obligatoire()
    taches.promouvoir(config.chemin_etat(rac), args.tache, agent,
                      chemin_journal=config.chemin_journal(rac))
    _regenerer_todo(rac)
    print("%s passee du backlog au todo : elle est reservable." % args.tache)
    return 0


def cmd_claim(args):
    rac = config.racine_partagee()
    agent = config.agent_obligatoire()
    try:
        taches.reserver(config.chemin_etat(rac), args.tache, agent,
                        surface=args.surface, motif=args.motif,
                        chemin_journal=config.chemin_journal(rac))
    except (taches.DejaReservee, taches.TacheBloquee) as e:
        return _sortir(str(e))
    _regenerer_todo(rac)
    print("%s reservee par %s." % (args.tache, agent))

    # La declaration de surface au registre est un BONUS, jamais une condition. Un
    # registre injoignable ne doit pas faire echouer une reservation deja acquise :
    # l'autorite est le depot, le registre n'est qu'une vue (D-10).
    r = config.registre(rac)
    if r:
        try:
            reg.declarer(r, agent, config.nom_depot(rac), args.surface, args.tache,
                         motif=args.motif)
        except OSError as e:
            print("registre injoignable, reservation conservee : %s" % e, file=sys.stderr)
    return 0


def cmd_release(args):
    rac = config.racine_partagee()
    agent = config.agent_obligatoire()
    try:
        taches.liberer(config.chemin_etat(rac), args.tache, agent,
                       chemin_journal=config.chemin_journal(rac))
    except taches.DejaReservee as e:
        if not args.force:
            return _sortir("%s\nUtiliser --force pour liberer la reservation d'un autre "
                           "agent -- a faire seulement s'il est parti." % e)
        # B-C : GARDE TRIPLE. Purger la reservation d'un agent VIVANT est le cas
        # reel qui a motive cette regle -- il revient, et son travail n'existe
        # plus nulle part.
        motif = (args.motif or "").strip()
        if len(motif) < 20:
            return _sortir(
                "--force exige --motif d'au moins 20 caracteres.\n"
                "  Ce motif est lu par l'agent evince quand il revient : il doit lui "
                "dire POURQUOI, pas seulement QUE.")
        heures = taches.age_du_claim(config.chemin_etat(rac), args.tache)
        if heures is not None and heures < 12 and not args.panne:
            return _sortir(
                "reservation prise il y a %.1f h -- moins de 12 h.\n"
                "  Un agent qui travaille depuis moins de douze heures est "
                "probablement vivant.\n"
                "  S'il est en panne declaree : ajouter --panne." % heures)
        from workflow.etat import modifier
        with modifier(config.chemin_etat(rac)) as etat:
            etat.get("claims", {}).pop(args.tache, None)
        jrn.ajouter(config.chemin_journal(rac), "tache-liberee-de-force", agent,
                    tache=args.tache, detail=motif)
    _regenerer_todo(rac)
    _liberer_presence_si_plus_rien(rac, agent)
    print("%s liberee." % args.tache)
    return 0


def cmd_status(args):
    # Les DOCUMENTS vivent dans l'arbre, le JOURNAL est partage par le depot.
    # Passer une seule racine aux deux faisait ecrire un SECOND journal dans le
    # worktree -- mesure du 2026-09-09.
    arbre = config.racine()
    agent = config.agent_obligatoire()
    try:
        nouveau = documents.changer_statut(
            arbre, args.document, args.statut, agent,
            config.chemin_journal(config.racine_partagee()))
    except documents.TransitionInterdite as e:
        return _sortir(str(e))
    print("%s -> %s" % (nouveau, args.statut))
    return 0


def cmd_log(args):
    rac = config.racine_partagee()
    agent = config.agent_obligatoire()
    jrn.ajouter(config.chemin_journal(rac), "note", agent,
                detail=args.message, tache=args.tache)
    print("Note tracee.")
    return 0


def cmd_remonter(args):
    """Remonte au registre le mouvement de backlog d'un commit.

    Appelee par le hook `post-commit`, donc elle SORT TOUJOURS EN 0 : un hook qui
    fait echouer un commit pour une ressource exterieure au depot est interdit
    (AGENTS.md §12), et le commit est de toute facon deja ecrit quand elle tourne.
    Ce qui n'a pas pu remonter se lit dans son motif, pas dans un code de sortie.
    """
    # La remontee declare un DEPOT au registre federe, jamais un worktree :
    # sinon le registre porte un depot fantome par arbre de travail, avec un
    # compte de taches faux. Mesure du 2026-09-09.
    r = remontee.remonter(config.racine_partagee(), args.sha)
    if r["remonte"]:
        print("%s -> registre : %s" % (r["depot"], ", ".join(r["fichiers"])))
    elif not args.silencieux:
        print("rien remonte -- %s" % r["motif"])
    return 0


def cmd_sync(args):
    # Sans argument, synchroniser() prend l'arbre courant pour les documents et
    # la racine partagee pour l'etat. C'est le bon defaut : ne pas le forcer.
    rapport = synchro.synchroniser(agent=config.agent() or "sync",
                                   archiver=not args.blanc)
    lignes = synchro.resume(rapport)
    if not lignes:
        print("Rien a faire." if not args.blanc else "Rien ne bougerait.")
        return 0
    if args.blanc:
        print("A BLANC -- rien n'a ete ecrit :")
    for ligne in lignes:
        print("  " + ligne)
    return 0


def cmd_constat(args):
    """Les faits que l'orchestrateur lit. Aucun jugement, aucune modification.

    Deux sorties pour deux lecteurs : `--json` pour un agent ou un script, le texte pour
    un humain. Les memes faits dans les deux cas -- si l'un disait autre chose que
    l'autre, on ne saurait plus lequel croire.
    """
    rac = config.racine_partagee()
    registre = config.registre(rac)
    if not registre:
        return _sortir(
            "aucun registre configure : la vue transverse n'existe pas sans lui.\n"
            "    PROLEX_REGISTRE=<chemin>   ou   .workflow/local.json")
    faits = orchestration.constater(registre)
    if args.json:
        import json as _json
        print(_json.dumps(faits, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(orchestration.rendre_texte(faits), end="")
    return 0


def cmd_verifier(args):
    if getattr(args, "titres", False):
        # A2 : on REMONTE, on ne change rien. Le code de sortie est non nul pour
        # qu'un controle automatique le voie, mais rien n'est bloque nulle part :
        # c'est un signalement, et l'humain tranche.
        suspects = taches.titres_suspects(config.chemin_etat(config.racine_partagee()))
        if not suspects:
            print("Aucun titre ne ressemble a un ordre.")
            return 0
        print("%d texte(s) qui ressemblent a un ordre -- A RELIRE, pas a corriger "
              "d'office :" % len(suspects))
        for ident, champ, motif, extrait in suspects:
            print("  %-8s %-16s %-22s %s" % (ident, champ, "« %s »" % motif, extrait))
        print("\nUn titre de tache est une DONNEE, jamais un ordre. Ces textes sont "
              "injectes verbatim\ndans TODO.md et les masters, que chaque session lit "
              "a l'ouverture froide.")
        return 1

    # `racine()` EST correct ici, et ce n'est pas un oubli : on verifie que le
    # champ `status` des documents concorde avec leur emplacement, et les
    # documents vivent dans l'ARBRE. Chaque worktree verifie les siens.
    arbre = config.racine()
    ecarts = documents.verifier(arbre)
    if not ecarts:
        print("Aucun ecart : le champ `status` et l'emplacement concordent partout.")
        return 0
    print("%d ecart(s) :" % len(ecarts))
    for chemin, quoi in ecarts:
        print("  %-50s %s" % (chemin, quoi))
    return 1


def _registre_ou_erreur(rac):
    r = config.registre(rac)
    if not r:
        print("Aucun registre configure.\n"
              "Le kit fonctionne tres bien sans -- la federation est optionnelle.\n"
              "Pour l'activer :\n"
              "    PROLEX_REGISTRE=<chemin>   (variable d'environnement)\n"
              "  ou .workflow/local.json : {\"registre\": \"<chemin>\"}",
              file=sys.stderr)
    return r


def cmd_federer(args):
    rac = config.racine_partagee()
    r = _registre_ou_erreur(rac)
    if not r:
        return 1
    liste = reg.enregistrer_depot(r, rac)
    print("%s federe. %d depot(s) au registre :" % (config.nom_depot(rac), len(liste)))
    for d in liste:
        print("  " + d)
    return 0


def cmd_master(args):
    rac = config.racine_partagee()
    r = _registre_ou_erreur(rac)
    if not r:
        return 1
    if args.blanc:
        print(reg.agreger(r), end="")
        return 0
    changes = reg.ecrire_masters(r)
    print("Master regenere : %s" % (", ".join(changes) if changes
                                     else "aucun changement (idempotent)"))
    return 0


def cmd_presence(args):
    rac = config.racine_partagee()
    r = _registre_ou_erreur(rac)
    if not r:
        return 1
    lignes = reg.presences(r, fraicheur_heures=args.heures)
    if not lignes:
        print("Personne de declare.")
        return 0
    if args.retirer:
        # Un agent doit pouvoir se retirer sans avoir de tache a cloturer -- une session
        # qui se termine, un chantier abandonne. Sans cette commande il fallait passer par
        # le module, ce qui n'est pas un protocole.
        moi = config.agent_obligatoire()
        agent = args.retirer if args.retirer is not True else moi
        connus = {a for a, _, _ in lignes}
        if agent not in connus:
            return _sortir("%s n'est pas declare. Presents : %s"
                           % (agent, ", ".join(sorted(connus)) or "personne"))
        # B-E : se retirer soi-meme est libre. Retirer AUTRUI est reserve a
        # l'orchestrateur, parce que la presence porte le signal de chevauchement
        # le plus precis du systeme : l'effacer aveugle tout le monde.
        if agent != moi and not config.suis_orchestrateur(rac, moi):
            o = config.orchestrateur(rac)
            return _sortir(
                "retirer la presence d'un autre agent est reserve a l'orchestrateur.\n"
                "  Orchestrateur de ce depot : %s\n"
                "  Se retirer soi-meme reste libre : `presence --retirer`."
                % (o or "aucun declare (voir .workflow/local.json)"))
        reg.retirer(r, agent)
        if agent != moi:
            jrn.ajouter(config.chemin_journal(rac), "presence-retiree-par-orchestrateur",
                        moi, detail=agent)
        print("%s retire du registre." % agent)
        return 0

    print("%-22s %-18s %-26s %s" % ("AGENT", "DEPOT", "SURFACE", "VU"))
    for agent, info, frais in lignes:
        marque = "" if frais else "   (ancien)"
        print("%-22s %-18s %-26s %s%s" % (
            agent[:22], (info.get("depot") or "?")[:18],
            (info.get("surface") or "-")[:26], info.get("vu", "?"), marque))
        if info.get("motif"):
            print("%-22s   %s" % ("", info["motif"][:60]))
    return 0


def cmd_version(args):
    print("agent-workflow %s" % _version())
    return 0


# ------------------------------------------------------------------ entree

def construire():
    p = argparse.ArgumentParser(
        prog="workflow.py",
        description="Protocole de cycle de vie documentaire et de taches, multi-agents.")
    s = p.add_subparsers(dest="commande", required=True)

    s.add_parser("init", help="cree la structure dans le depot courant").set_defaults(f=cmd_init)

    snap = s.add_parser("snapshot", help="etat complet, a lire en debut de session")
    snap.add_argument("--heures", type=int, default=8,
                      help="age a partir duquel une reservation est signalee (defaut : 8)")
    snap.set_defaults(f=cmd_snapshot)

    todo = s.add_parser("todo", help="gestion des taches").add_subparsers(
        dest="sous", required=True)

    ajout = todo.add_parser("add", help="cree une tache")
    ajout.add_argument("titre")
    ajout.add_argument("--actif", action="store_true",
                       help="cree directement dans le todo au lieu du backlog")
    ajout.add_argument("--corrige", metavar="T-XXX",
                       help="cette tache corrige un defaut laisse par une autre")
    ajout.add_argument("--depend-de", dest="depend_de", metavar="T-XXX", action="append",
                       help="non reservable tant que cette tache n'est pas close "
                            "(repetable)")
    ajout.add_argument("--allowed-paths", dest="allowed_paths", metavar="CHEMIN",
                       action="append",
                       help="chemin que cette tache a vocation a toucher, declaratif "
                            "(repetable)")
    ajout.add_argument("--acceptance", help="critere qui dira si la tache est faite, "
                                            "ecrit AVANT le travail")
    ajout.set_defaults(f=cmd_todo_add)

    fin = todo.add_parser("done", help="clot une tache")
    fin.add_argument("tache")
    fin.add_argument("--verif", help="ce qui a ete constate (Definition of Done)")
    fin.add_argument("--sans-verif", dest="sans_verif", metavar="MOTIF",
                     help="clore sans verification, en disant pourquoi (20 car. minimum)")
    fin.set_defaults(f=cmd_todo_done)

    todo.add_parser("list", help="rend le TODO genere").set_defaults(f=cmd_todo_list)

    prom = todo.add_parser("promote", help="passe une tache du backlog au todo")
    prom.add_argument("tache")
    prom.set_defaults(f=cmd_promote)

    cl = s.add_parser("claim", help="reserve une tache")
    cl.add_argument("tache")
    cl.add_argument("--surface", help="OU vous allez travailler (fichier, module, sujet)")
    cl.add_argument("--motif", help="POURQUOI -- ce qui permettra a un autre agent de "
                                    "contester ou de comprendre, quand la conversation "
                                    "aura disparu")
    cl.set_defaults(f=cmd_claim)

    rel = s.add_parser("release", help="rend une tache")
    rel.add_argument("tache")
    rel.add_argument("--motif", help="pourquoi la reservation est evincee (20 car. minimum)")
    rel.add_argument("--panne", action="store_true",
                     help="l'agent evince est en panne declaree : leve le seuil de 12 h")
    rel.add_argument("--force", action="store_true",
                     help="libere la reservation d'un autre agent")
    rel.set_defaults(f=cmd_release)

    st = s.add_parser("status", help="change le statut d'un document")
    st.add_argument("document")
    st.add_argument("statut", choices=("todo", "in-progress", "done", "archived"))
    st.set_defaults(f=cmd_status)

    lg = s.add_parser("log", help="trace une decision")
    lg.add_argument("message")
    lg.add_argument("--tache", help="tache a laquelle rattacher la note")
    lg.set_defaults(f=cmd_log)

    rm = s.add_parser("remonter", help="remonte au registre le backlog touche par un commit")
    rm.add_argument("--sha", default="HEAD", help="commit a examiner (defaut : HEAD)")
    rm.add_argument("--silencieux", action="store_true",
                    help="ne dit rien quand il n'y avait rien a remonter")
    rm.set_defaults(f=cmd_remonter)

    sy = s.add_parser("sync", help="archive les done, regenere le TODO (idempotent)")
    sy.add_argument("--blanc", action="store_true",
                    help="montre ce qui bougerait sans rien ecrire")
    sy.set_defaults(f=cmd_sync)

    co = s.add_parser("constat", help="les faits transverses, sans jugement")
    co.add_argument("--json", action="store_true", help="sortie machine")
    co.set_defaults(f=cmd_constat)

    ver = s.add_parser("verifier", help="confronte les statuts et les emplacements")
    ver.add_argument("--titres", action="store_true",
                     help="A2 : remonte les titres et motifs qui ressemblent a un ordre")
    ver.set_defaults(
        f=cmd_verifier)
    s.add_parser("federer", help="inscrit ce depot au registre central").set_defaults(
        f=cmd_federer)

    ma = s.add_parser("master", help="regenere le master agrege (jamais edite)")
    ma.add_argument("--blanc", action="store_true", help="affiche sans ecrire")
    ma.set_defaults(f=cmd_master)

    pr = s.add_parser("presence", help="qui travaille ou, en ce moment")
    pr.add_argument("--heures", type=int, default=12,
                    help="au-dela, une declaration est marquee ancienne (defaut : 12)")
    pr.add_argument("--retirer", nargs="?", const=True, metavar="AGENT",
                    help="retire une declaration : la sienne sans argument, celle d'un "
                         "autre en le nommant -- pour une session qui s'arrete sans avoir "
                         "de tache a cloturer")
    pr.set_defaults(f=cmd_presence)

    s.add_parser("version", help="version du kit").set_defaults(f=cmd_version)
    return p


def principal(argv=None):
    args = construire().parse_args(argv)
    try:
        return args.f(args)
    except (config.AgentNonDeclare, config.HorsDepot, config.NomNonAlloue) as e:
        return _sortir(str(e))
    except taches.TexteInvalide as e:
        return _sortir(str(e))
    except taches.DejaReservee as e:
        # Elle remontait nue depuis `todo done` : le refus de cloturer la
        # tache d'autrui s'affichait en traceback Python, alors que son
        # message nomme le detenteur et la date. `release` la rattrapait
        # deja localement -- ce chemin-ci ne l'attrapait nulle part.
        return _sortir(str(e))
    except (taches.TacheInconnue, taches.TacheClose) as e:
        return _sortir(str(e).strip("'"))
    except FileNotFoundError as e:
        return _sortir("fichier introuvable : %s" % e)
    except verrou.VerrouIndisponible as e:
        # Son message est redige pour l'agent qui le recoit -- il faut encore le
        # lui montrer. Sans ce rattrapage, vingt-cinq lignes de traceback
        # prenaient la place d'une phrase ecrite pour ca.
        return _sortir(str(e))
    except EtatIllisible as e:
        return _sortir(str(e))
    except reg.RegistreIllisible as e:
        return _sortir(str(e))


if __name__ == "__main__":
    sys.exit(principal())
