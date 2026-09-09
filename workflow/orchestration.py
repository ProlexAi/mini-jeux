#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Les FAITS que l'orchestrateur lit. Aucun jugement ici.

POURQUOI CE MODULE EXISTE SEPAREMENT DE L'AGENT
-----------------------------------------------
Un agent qui mesure ET juge n'est optimisable ni d'un cote ni de l'autre : on ne peut pas
corriger sa mesure sans toucher son jugement, ni changer son jugement sans risquer sa
mesure. La separation est la condition pour que l'agent « reste optimisable » (demande de
Matt, 2026-08-31) :

    ce module          -> ce qui EST. Deterministe, teste, sans modele.
    les seuils         -> `.workflow/orchestration.json`, ajustables sans toucher au code.
    l'agent            -> ce qu'IL FAUT EN FAIRE. Remplacable sans toucher a la mesure.

CE QU'IL DETECTE, ET POURQUOI CEUX-LA
-------------------------------------
Les quatre signaux viennent de collisions REELLES observees le 2026-08-31 entre trois
sessions, pas d'une liste imaginee :

  chevauchement   deux agents travaillent des surfaces qui se recouvrent -- le cas des
                  14 scripts corriges pendant qu'ils etaient deplaces. C'est le signal le
                  plus precieux : c'est le seul qu'aucune session ne peut voir seule.
  claim ancien    une reservation tenue depuis trop longtemps. SIGNALEE, jamais purgee :
                  un agent lent et un agent mort se ressemblent exactement.
  sans porteur    une tache prete que personne n'a prise.
  travail muet    un agent present dans le registre, sans aucune reservation -- il
                  travaille sans dire ou.

CE QU'IL NE FAIT PAS
--------------------
Il ne classe pas par gravite, ne recommande rien, ne modifie rien. Un fait sans jugement
peut etre relu et conteste ; un jugement sans fait ne le peut pas.
"""

import json
import os
from datetime import datetime, timedelta

from . import registre as reg

SEUILS_DEFAUT = {
    # Heures. Aucun n'est un couperet : ce sont les points ou il devient raisonnable de
    # DEMANDER. Ils vivent dans un fichier parce qu'ils sont faits pour etre ajustes --
    # les valeurs ci-dessous sont un point de depart, pas une mesure.
    "claim_ancien_heures": 8,
    "sans_porteur_heures": 48,
    "presence_fraiche_heures": 12,
    # Fenetre des mouvements de backlog rendus par `constat`. Le journal central est
    # append-only et grossit sans fin : un constat qui rendrait tout l'historique
    # cesserait d'etre lu, ce qui revient a ne rien rendre.
    "backlog_recent_heures": 24,
    # A6 : la chaine LLM est unique. Quand elle tombe, reservations et passations
    # gelent ensemble -- et le liberateur designe est lui-meme sur la chaine
    # tombee. Le filet n'est pas une releve automatique : c'est une PASSATION
    # ecrite, exigee au-dela de deux heures de reservation.
    "passation_heures": 2,
    # F13 : « prevenir Matt, il avise ». Aucune releve automatique -- seulement
    # le constat qu'un orchestrateur declare n'a plus donne signe de vie.
    "orchestrateur_absent_heures": 6,
    # B-B : les clotures sans verification remontent sur cette fenetre.
    "sans_verif_jours": 7,
}

FICHIER_SEUILS = "orchestration.json"


def seuils(registre):
    """Lit les seuils, avec repli sur les valeurs par defaut.

    Un seuil absent du fichier prend sa valeur par defaut : ajouter un seuil au code ne
    doit pas casser les installations qui portent un fichier plus ancien.
    """
    valeurs = dict(SEUILS_DEFAUT)
    try:
        with open(os.path.join(registre, FICHIER_SEUILS), encoding="utf-8") as f:
            lus = json.load(f)
        for cle, valeur in lus.items():
            if cle in SEUILS_DEFAUT and isinstance(valeur, (int, float)):
                valeurs[cle] = valeur
    except (OSError, json.JSONDecodeError, AttributeError):
        pass
    return valeurs


def _age_heures(horodatage):
    """Rend l'age en heures, ou None si l'horodatage est illisible."""
    try:
        quand = datetime.fromisoformat(horodatage)
    except (ValueError, TypeError):
        return None
    return (datetime.now().astimezone() - quand).total_seconds() / 3600.0


def _normaliser(surface):
    """Reduit une surface a une forme comparable : minuscules, separateurs POSIX.

    On ne cherche pas a resoudre les chemins sur le disque : une surface peut designer un
    module, un sujet, un fichier qui n'existe pas encore. La comparaison reste textuelle,
    et c'est assume -- mieux vaut un chevauchement signale a tort qu'une collision vue par
    personne.
    """
    if not surface:
        return ""
    return surface.strip().replace("\\", "/").strip("/").lower()


def _se_recouvrent(a, b):
    """Vrai si deux surfaces se recouvrent : identiques, ou l'une contenant l'autre."""
    a, b = _normaliser(a), _normaliser(b)
    if not a or not b:
        return False
    if a == b:
        return True
    return a.startswith(b + "/") or b.startswith(a + "/")


def chevauchements(registre):
    """Les paires d'agents dont les surfaces declarees se recouvrent.

    C'EST LE SIGNAL QUE PERSONNE NE PEUT VOIR SEUL. Une session connait sa propre surface
    et ignore celle des autres ; c'est ce qui a produit trois collisions le 2026-08-31,
    dont une ou 14 fichiers etaient modifies pendant qu'on les deplacait.
    """
    # `presences()` rend des triplets (agent, info, frais) -- interface lue, pas supposee.
    # On ne compare QUE les declarations fraiches : une surface annoncee il y a trois
    # jours ne dit rien de ce qui se passe maintenant.
    vivants = [(a, i) for a, i, frais in
               reg.presences(registre, seuils(registre)["presence_fraiche_heures"])
               if frais]
    trouves = []
    for i, (agent_a, info_a) in enumerate(vivants):
        for agent_b, info_b in vivants[i + 1:]:
            if agent_a == agent_b:
                continue
            if _se_recouvrent(info_a.get("surface"), info_b.get("surface")):
                trouves.append({
                    "agents": [agent_a, agent_b],
                    "surfaces": [info_a.get("surface"), info_b.get("surface")],
                    "depots": [info_a.get("depot"), info_b.get("depot")],
                    "motifs": [info_a.get("motif"), info_b.get("motif")],
                })
    return trouves


def _lignes_depuis_la_fin(chemin, bloc=65536):
    """Rend les lignes d'un fichier de la DERNIERE vers la premiere, paresseusement.

    Ecrit a la main parce que la bibliotheque standard n'offre rien pour cela et
    que le kit n'a aucune dependance. Trois pieges evites, chacun silencieux :

    - LECTURE EN BINAIRE, decodage ligne par ligne. Lire en texte et decouper
      apres coup casserait un caractere multi-octet a cheval sur deux blocs -- un
      accent tombant sur la frontiere suffirait, et l'erreur serait rare donc
      invisible en test.
    - LE RESTE EST GARDE entre deux blocs : une ligne coupee par la frontiere est
      recollee avec le bloc precedent, jamais rendue en deux morceaux.
    - `errors="replace"` au decodage : une ligne corrompue par un incident
      d'ecriture concurrente ne doit pas faire echouer TOUTE la lecture. L'appelant
      la jettera a l'analyse JSON.
    """
    with open(chemin, "rb") as f:
        f.seek(0, os.SEEK_END)
        reste = b""
        position = f.tell()
        while position > 0:
            taille = min(bloc, position)
            position -= taille
            f.seek(position)
            morceau = f.read(taille) + reste
            lignes = morceau.split(b"\n")
            # La premiere est peut-etre incomplete : elle attend le bloc d'avant.
            reste = lignes.pop(0)
            for l in reversed(lignes):
                yield l.decode("utf-8", errors="replace")
        if reste:
            yield reste.decode("utf-8", errors="replace")


def backlogs_bouges(registre, fenetre_heures=24):
    """Mouvements de backlog remontes recemment, du plus recent au plus ancien.

    C'est ce que l'orchestrateur ne pouvait pas voir avant la 1.7.0 : un depot
    reecrivait tout son backlog et la vue transverse n'en savait rien. Les lignes
    viennent du journal central, ecrites par le hook `post-commit` de chaque depot.

    Une fenetre, pas tout l'historique : le journal est append-only et grossit sans
    fin. Un constat qui rendrait dix mille lignes ne serait plus lu.

    LU PAR LA FIN, ET C'EST CE QUI BORNE LE COUT. Le journal est chronologique par
    construction -- append-only, une ligne ajoutee est toujours la plus recente.
    Les lignes de la fenetre sont donc TOUJOURS a la fin du fichier. Lire depuis le
    debut coutait la taille totale : mesure du 2026-09-08, 320 octets par ligne,
    soit 73 000 lignes et 23 Mo par an a dix depots -- relus a chaque `constat`
    pour rendre les vingt-quatre dernieres heures.

    On lit donc par blocs depuis la fin, et on s'arrete des qu'une ligne SORT de la
    fenetre. Le cout devient proportionnel a la fenetre, plus a l'historique.

    La sortie anticipee est sure PARCE QUE le fichier est chronologique. Si un jour
    il cessait de l'etre -- une fusion Git qui reordonne, un import de lignes
    anciennes -- ce raccourci deviendrait faux en silence. Le cas est couvert par un
    test qui place volontairement une ligne ancienne apres une recente.
    """
    fichier = reg.chemin(registre, reg.JOURNAL)
    if not os.path.exists(fichier):
        return []
    vus = []
    try:
        for ligne in _lignes_depuis_la_fin(fichier):
            ligne = ligne.strip()
            if not ligne:
                continue
            if '"backlog-bouge"' not in ligne:
                # Filtre bon marche avant l'analyse JSON : la grande majorite des
                # lignes du journal central sont d'autres evenements.
                continue
            try:
                e = json.loads(ligne)
            except json.JSONDecodeError:
                # Une ligne illisible n'invalide pas les autres : le journal est
                # ecrit par N depots a la fois, et une ligne tronquee par un
                # incident ne doit pas rendre le constat aveugle.
                continue
            if e.get("quoi") != "backlog-bouge":
                continue
            age = _age_heures(e.get("quand", ""))
            if age is None:
                continue
            if age > fenetre_heures:
                # SORTIE ANTICIPEE : tout ce qui precede est encore plus ancien.
                break
            vus.append({
                "depot": e.get("cible"), "quand": e.get("quand"),
                "age_heures": round(age, 1), "detail": e.get("detail"),
                "fichiers": e.get("fichiers") or [], "ouvertes": e.get("ouvertes"),
            })
    except OSError:
        return []
    vus.sort(key=lambda v: v["quand"], reverse=True)
    return vus


def orchestrateurs_absents(registre, seuil_heures):
    """Les orchestrateurs declares qui n'ont plus donne signe de vie (F13).

    « PREVENIR MATT, IL AVISE » -- decision du 2026-09-09. Aucune releve
    automatique : un orchestrateur silencieux peut etre en train de reflechir, en
    train de lire, ou parti. La machine ne sait pas lequel, et se tromper
    couterait plus cher que d'attendre.

    Un depot qui ne declare aucun orchestrateur n'apparait jamais ici : on ne
    reproche pas une absence a qui n'a designe personne.
    """
    absents = []
    vus = {a: i for a, i, _ in reg.presences(registre, seuil_heures * 10)}
    for racine in reg.depots(registre):
        local = os.path.join(racine, ".workflow", "local.json")
        try:
            with open(local, encoding="utf-8") as f:
                nom = (json.load(f) or {}).get("orchestrateur")
        except (OSError, json.JSONDecodeError, AttributeError):
            continue
        if not nom:
            continue
        info = vus.get(nom)
        age = _age_heures(info.get("vu")) if info else None
        if info is None or (age is not None and age > seuil_heures):
            absents.append({"depot": os.path.basename(os.path.abspath(racine)),
                            "orchestrateur": nom,
                            "depuis_heures": round(age, 1) if age is not None else None})
    return absents


def clotures_sans_verif(registre, jours):
    """Les taches closes sans verification declaree, sur la fenetre donnee (B-B).

    Le refus du lot 6a empeche d'en creer de nouvelles ; cette vue montre celles
    qui existent deja, et celles closes avec une DISPENSE -- dont le motif est
    lisible ici, ce qui est tout l'interet de l'avoir exige.
    """
    limite = datetime.now().astimezone() - timedelta(days=jours)
    trouvees = []
    for racine in reg.depots(registre):
        etat_fichier = os.path.join(racine, ".workflow", "state.json")
        try:
            with open(etat_fichier, encoding="utf-8") as f:
                etat = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        nom = os.path.basename(os.path.abspath(racine))
        for ident, t in sorted((etat.get("taches") or {}).items()):
            if t.get("etat") != "close":
                continue
            quand = t.get("clos")
            if quand:
                try:
                    if datetime.fromisoformat(quand) < limite:
                        continue
                except ValueError:
                    pass
            v = t.get("verification") or ""
            if not v or v.startswith("SANS VERIFICATION"):
                trouvees.append({"depot": nom, "tache": ident,
                                 "titre": (t.get("titre") or "")[:70],
                                 "dispense": v[:80] if v else None})
    return trouvees


def constater(registre):
    """Rend les faits, sans jugement ni tri par gravite.

    La structure est stable : un consommateur -- agent, script, humain -- peut s'y fier.
    Ajouter une categorie est possible ; en renommer une casserait ce contrat.
    """
    s = seuils(registre)
    faits = {
        "quand": datetime.now().astimezone().isoformat(timespec="seconds"),
        "seuils": s,
        "presences": [],
        "chevauchements": chevauchements(registre),
        "claims_anciens": [],
        "sans_porteur": [],
        "travail_muet": [],
        "backlogs_bouges": backlogs_bouges(registre, s.get("backlog_recent_heures", 24)),
        "depots_injoignables": [],
        # A6, F13, B-B : trois SIGNAUX. Rien ne se releve, rien ne se purge, rien
        # ne se bloque -- le kit dit ce qu'il voit, Matt tranche.
        "passations_dues": [],
        "orchestrateurs_absents": orchestrateurs_absents(
            registre, s.get("orchestrateur_absent_heures", 6)),
        "clotures_sans_verif": clotures_sans_verif(
            registre, s.get("sans_verif_jours", 7)),
    }

    # A6 : au-dela du seuil, une reservation doit porter une PASSATION ecrite --
    # de quoi qu'un autre reprenne si la chaine tombe. Ce n'est pas une purge :
    # c'est la demande d'un texte.
    for racine in reg.depots(registre):
        etat_fichier = os.path.join(racine, ".workflow", "state.json")
        try:
            with open(etat_fichier, encoding="utf-8") as f:
                etat_d = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        nom_d = os.path.basename(os.path.abspath(racine))
        for ident, c in sorted((etat_d.get("claims") or {}).items()):
            age = _age_heures(c.get("depuis"))
            if age is not None and age > s.get("passation_heures", 2) and not c.get("passation"):
                faits["passations_dues"].append(
                    {"depot": nom_d, "tache": ident, "agent": c.get("agent"),
                     "depuis_heures": round(age, 1)})

    vivants = reg.presences(registre, s["presence_fraiche_heures"])
    faits["presences"] = [
        {"agent": a, "depot": i.get("depot"), "surface": i.get("surface"),
         "motif": i.get("motif"), "tache": i.get("tache"), "vu": i.get("vu"),
         "frais": frais}
        for a, i, frais in vivants
    ]
    declarants = {a for a, _, frais in vivants if frais}
    avec_claim = set()

    for racine in reg.depots(registre):
        etat_fichier = os.path.join(racine, ".workflow", "state.json")
        if not os.path.exists(etat_fichier):
            # NE PAS VOIR UN DEPOT N'EST PAS LA MEME CHOSE QUE LE VOIR VIDE.
            faits["depots_injoignables"].append(racine)
            continue
        try:
            with open(etat_fichier, encoding="utf-8") as f:
                etat = json.load(f)
        except (OSError, json.JSONDecodeError):
            faits["depots_injoignables"].append(racine)
            continue

        depot = etat.get("depot") or os.path.basename(racine)
        taches = etat.get("taches", {})

        for ident, claim in etat.get("claims", {}).items():
            avec_claim.add(claim.get("agent"))
            age = _age_heures(claim.get("depuis", ""))
            if age is None or age >= s["claim_ancien_heures"]:
                faits["claims_anciens"].append({
                    "depot": depot, "tache": ident,
                    "agent": claim.get("agent"),
                    "surface": claim.get("surface"),
                    "motif": claim.get("motif"),
                    "age_heures": None if age is None else round(age, 1),
                    "titre": taches.get(ident, {}).get("titre"),
                })

        pris = set(etat.get("claims", {}))
        for ident, t in taches.items():
            if t.get("etat") == "close" or t.get("niveau") != "todo" or ident in pris:
                continue
            age = _age_heures(t.get("cree", ""))
            if age is not None and age >= s["sans_porteur_heures"]:
                faits["sans_porteur"].append({
                    "depot": depot, "tache": ident, "titre": t.get("titre"),
                    "age_heures": round(age, 1),
                })

    faits["travail_muet"] = sorted(a for a in declarants - avec_claim if a)
    return faits


def rendre_texte(faits):
    """Une vue lisible des memes faits. Le silence est le cas nominal."""
    lignes = ["Constat du %s" % faits["quand"], ""]
    n = 0

    # B-B EN PREMIERE SECTION -- le canon le demande explicitement. Ce que Matt
    # relit, ce sont les AFFIRMATIONS : une cloture sans preuve doit lui sauter
    # aux yeux avant tout le reste.
    if faits.get("clotures_sans_verif"):
        lignes.append("CLOTURES SANS VERIFICATION (%d derniers jours) :"
                      % faits["seuils"].get("sans_verif_jours", 7))
        for c in faits["clotures_sans_verif"]:
            lignes.append("  %-12s %-8s %s" % (c["depot"], c["tache"], c["titre"]))
            if c.get("dispense"):
                lignes.append("      dispense : %s" % c["dispense"])
        lignes.append("")
        n += len(faits["clotures_sans_verif"])

    # F13 : on PREVIENT, on ne releve pas. Un orchestrateur silencieux peut etre
    # en train de lire, de reflechir, ou parti -- la machine ne sait pas lequel.
    if faits.get("orchestrateurs_absents"):
        lignes.append("ORCHESTRATEUR ABSENT (> %s h) -- prevenir Matt, il avise :"
                      % faits["seuils"].get("orchestrateur_absent_heures", 6))
        for o in faits["orchestrateurs_absents"]:
            depuis = ("jamais vu" if o["depuis_heures"] is None
                      else "vu il y a %.1f h" % o["depuis_heures"])
            lignes.append("  %-12s %-18s %s" % (o["depot"], o["orchestrateur"], depuis))
        lignes.append("")
        n += len(faits["orchestrateurs_absents"])

    # A6 : la chaine LLM est unique. Au-dela du seuil, une reservation doit
    # porter de quoi qu'un autre reprenne. Ce n'est pas une purge : c'est la
    # demande d'un texte.
    if faits.get("passations_dues"):
        lignes.append("PASSATION DUE (> %s h de reservation) -- la chaine peut tomber :"
                      % faits["seuils"].get("passation_heures", 2))
        for pz in faits["passations_dues"]:
            lignes.append("  %-12s %-8s %-18s depuis %.1f h"
                          % (pz["depot"], pz["tache"], pz["agent"] or "?",
                             pz["depuis_heures"]))
        lignes.append("")
        n += len(faits["passations_dues"])

    if faits["chevauchements"]:
        lignes.append("SURFACES QUI SE RECOUVRENT -- personne ne peut le voir seul :")
        for c in faits["chevauchements"]:
            lignes.append("  %s (%s)" % (" / ".join(str(a) for a in c["agents"]),
                                         " | ".join(str(s) for s in c["surfaces"])))
            for agent, motif in zip(c["agents"], c["motifs"]):
                if motif:
                    lignes.append("      %s : %s" % (agent, motif))
        lignes.append("")
        n += len(faits["chevauchements"])

    if faits.get("backlogs_bouges"):
        lignes.append("BACKLOGS QUI ONT BOUGE (fenetre : %d h) -- remontes par les hooks :"
                      % faits["seuils"].get("backlog_recent_heures", 24))
        for b in faits["backlogs_bouges"]:
            ouvertes = "" if b["ouvertes"] is None else " -- %d ouverte(s)" % b["ouvertes"]
            lignes.append("  %-12s il y a %4.1f h  %s%s"
                          % (b["depot"], b["age_heures"], b["detail"] or "", ouvertes))
            lignes.append("      %s" % ", ".join(b["fichiers"]))
        lignes.append("")
        n += len(faits["backlogs_bouges"])

    if faits["claims_anciens"]:
        lignes.append("RESERVATIONS ANCIENNES (seuil : %d h) -- signalees, pas liberees :"
                      % faits["seuils"]["claim_ancien_heures"])
        for c in faits["claims_anciens"]:
            age = "age inconnu" if c["age_heures"] is None else "%.0f h" % c["age_heures"]
            lignes.append("  %-10s %-8s %-20s %s" % (c["depot"], c["tache"],
                                                     c["agent"], age))
        lignes.append("")
        n += len(faits["claims_anciens"])

    if faits["sans_porteur"]:
        lignes.append("PRETES ET SANS PORTEUR (seuil : %d h) :"
                      % faits["seuils"]["sans_porteur_heures"])
        for t in faits["sans_porteur"]:
            lignes.append("  %-10s %-8s %s" % (t["depot"], t["tache"], t["titre"]))
        lignes.append("")
        n += len(faits["sans_porteur"])

    if faits["travail_muet"]:
        lignes.append("PRESENTS SANS RESERVATION -- ils travaillent sans dire ou :")
        lignes.append("  " + ", ".join(faits["travail_muet"]))
        lignes.append("")
        n += len(faits["travail_muet"])

    if faits["depots_injoignables"]:
        lignes.append("DEPOTS INJOIGNABLES -- ne pas conclure qu'ils sont vides :")
        for d in faits["depots_injoignables"]:
            lignes.append("  " + d)
        lignes.append("")
        n += len(faits["depots_injoignables"])

    if n == 0:
        lignes.append("Rien a signaler. %d agent(s) present(s)." % len(faits["presences"]))
    return "\n".join(lignes).rstrip() + "\n"
