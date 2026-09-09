#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Frontmatter YAML : un sous-ensemble ferme, lu et reecrit sans dependance.

POURQUOI PAS PyYAML
-------------------
Trois raisons, dans l'ordre de poids.

1. `AGENTS.md` §1 pose « aucune dependance hors bibliotheque standard ». Un kit copie
   dans N depots ne peut pas exiger un `pip install` dans chacun.
2. Ubuntu 24.04 et suivants -- Kubuntu 26.04 compris -- appliquent PEP 668 : `pip install`
   sur le Python systeme est REFUSE. Un kit qui dependrait de PyYAML obligerait a monter
   un environnement virtuel par depot, pour lire dix lignes de metadonnees.
3. Le besoin est minuscule et FERME : sept champs, trois types. Le rapport le chiffre
   lui-meme a « un parseur de 20 lignes ».

CE QUI EST SUPPORTE, ET RIEN D'AUTRE
------------------------------------
    ---
    title: "Titre lisible"        chaine, guillemets optionnels
    status: todo                  valeur fermee
    owner: ""                     chaine
    created: 2026-08-31           date ISO, rendue telle quelle
    updated: 2026-08-31
    source: "reunion"
    tags: [a, b]                  liste courte sur une ligne
    corrige: T-012                lien de reouverture (R-15)
    ---

Pas d'imbrication, pas de blocs multi-lignes, pas d'ancres. **Une ligne non reconnue
n'est pas ignoree : elle leve.** Ignorer silencieusement ferait perdre des metadonnees
sans que personne ne le sache -- exactement le genre de defaut que ce kit existe pour
supprimer.

CE QUE LA REECRITURE PRESERVE
-----------------------------
L'ordre des cles, les cles inconnues, et le corps du document a l'octet pres. Un outil
qui reordonne ou normalise produit un diff Git enorme a chaque changement de statut, et
rend la relecture impossible.
"""

import re

DELIMITEUR = "---"

STATUTS = ("todo", "in-progress", "done", "archived")

# Une cle YAML plate : `cle: valeur`. Les cles sont en minuscules avec tirets bas.
_LIGNE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$")


class FrontmatterInvalide(ValueError):
    pass


class SansFrontmatter(ValueError):
    def __init__(self, chemin=""):
        super().__init__(
            "aucun frontmatter trouve%s\n"
            "Tout document gere par le workflow commence par un bloc delimite par '---'. "
            "Un document sans frontmatter n'a pas de statut, donc sera relu indefiniment."
            % ((" dans " + str(chemin)) if chemin else "")
        )


def _valeur(brut, numero):
    """Convertit une valeur scalaire ou une liste courte. Leve sur ce qu'on ne sait pas."""
    brut = brut.strip()
    if brut == "":
        return ""
    if brut.startswith("[") and brut.endswith("]"):
        interieur = brut[1:-1].strip()
        if not interieur:
            return []
        return [_scalaire(x.strip(), numero) for x in interieur.split(",")]
    if brut.startswith(("|", ">", "&", "*", "{")):
        raise FrontmatterInvalide(
            "ligne %d : construction YAML non supportee (%r).\n"
            "Le kit lit un sous-ensemble ferme : scalaires et listes courtes. "
            "Refuser est deliberé -- accepter a moitie perdrait des donnees en silence."
            % (numero, brut[:20])
        )
    return _scalaire(brut, numero)


def _scalaire(brut, numero):
    if len(brut) >= 2 and brut[0] == brut[-1] and brut[0] in "\"'":
        return brut[1:-1]
    if brut.lower() in ("true", "false"):
        return brut.lower() == "true"
    if brut.lower() in ("null", "~"):
        return None
    return brut


def fins_de_ligne(texte):
    """Rend le style dominant du texte : '\\r\\n' ou '\\n'.

    MESURE DU 2026-08-31, ET POURQUOI CETTE FONCTION EXISTE
    ------------------------------------------------------
    Reecrire un document en '\\n' alors qu'il etait en '\\r\\n' ne change pas une ligne :
    il change TOUTES les lignes. `git diff` annonce un fichier entierement modifie, la
    relecture devient impossible, et le vrai changement -- un statut passe de todo a
    in-progress -- se noie dans le bruit.

    `AGENTS.md` §9 documente ce reformatage a propos de `sed -i` ; on l'atteint ici par
    un chemin different. Sur cette machine, `core.autocrlf=true` : les fichiers arrivent
    en CRLF, et `roles-fr.json` en porte 489 pour zero LF nu. Un depot clone sous Kubuntu
    sera en LF. Le kit doit donc RESTITUER ce qu'il a trouve, jamais imposer un style.
    """
    crlf = texte.count("\r\n")
    return "\r\n" if crlf and crlf >= (texte.count("\n") - crlf) else "\n"


def lire(texte, chemin=""):
    """Rend (metadonnees, corps, lignes_brutes). Leve si le frontmatter manque.

    Le texte est normalise en '\\n' pour l'analyse ; `ecrire()` restitue le style
    d'origine, que `fins_de_ligne()` sait retrouver.
    """
    texte = texte.replace("\r\n", "\n")
    if not texte.startswith(DELIMITEUR):
        raise SansFrontmatter(chemin)

    lignes = texte.split("\n")
    fin = None
    for i in range(1, len(lignes)):
        if lignes[i].strip() == DELIMITEUR:
            fin = i
            break
    if fin is None:
        raise FrontmatterInvalide(
            "frontmatter jamais referme%s : le second '---' manque."
            % ((" dans " + str(chemin)) if chemin else "")
        )

    meta, brutes = {}, lignes[1:fin]
    for decalage, ligne in enumerate(brutes):
        numero = decalage + 2
        if not ligne.strip() or ligne.lstrip().startswith("#"):
            continue
        if ligne[0] in " \t":
            raise FrontmatterInvalide(
                "ligne %d : indentation non supportee. Le kit ne lit pas de structures "
                "imbriquees ; aplatir la cle ou la sortir du frontmatter." % numero
            )
        m = _LIGNE.match(ligne)
        if not m:
            raise FrontmatterInvalide(
                "ligne %d : ni 'cle: valeur', ni commentaire, ni ligne vide -- %r"
                % (numero, ligne[:60])
            )
        cle = m.group(1)
        if cle in meta:
            # UNE CLE EN DOUBLE EST UNE AMBIGUITE, PAS UN CHOIX. Avant, le second
            # ecrasait le premier en silence : le kit decidait du cycle de vie du
            # document sur une valeur que son auteur n'avait peut-etre jamais
            # voulue, et l'aller-retour supprimait la premiere ligne -- la trace
            # de l'ambiguite disparaissait avec elle.
            raise FrontmatterInvalide(
                "ligne %d : la cle %r apparait deux fois -- laquelle fait foi ? "
                "En supprimer une." % (numero, cle))
        meta[cle] = _valeur(m.group(2), numero)

    corps = "\n".join(lignes[fin + 1:])
    return meta, corps, brutes


def _rendre(valeur):
    if isinstance(valeur, list):
        return "[" + ", ".join(str(v) for v in valeur) + "]"
    if isinstance(valeur, bool):
        return "true" if valeur else "false"
    if valeur is None:
        return "null"
    texte = str(valeur)
    # On guillemette seulement ce qui l'exige : un ':' suivi d'espace casserait la relecture,
    # et une chaine vide disparaitrait. Guillemetter tout produirait un diff inutile.
    if texte == "" or ": " in texte or texte.strip() != texte:
        return '"%s"' % texte.replace('"', '\\"')
    return texte


def ecrire(meta, corps, brutes=None, fins="\n"):
    """Reconstruit le document. Preserve l'ordre d'origine des cles si `brutes` est donne.

    `fins` restitue le style de fin de ligne du document d'origine -- voir
    `fins_de_ligne()`. Le defaut '\\n' ne vaut que pour un document cree de zero.

    Les cles inconnues sont conservees : le kit n'est pas proprietaire du frontmatter,
    d'autres outils y ecrivent (Obsidian, un generateur de site).
    """
    # UNE LIGNE INCHANGEE EST REECRITE TELLE QUELLE, A L'OCTET.
    #
    # Re-rendre chaque valeur perdrait la forme d'origine : `title: "x"` reviendrait
    # `title: x`, ce qui est semantiquement identique et textuellement different. Sur un
    # simple changement de statut, git verrait bouger toutes les lignes guillemetees --
    # le diff cesserait de montrer ce qui a change.
    #
    # On ne re-rend donc QUE les cles dont la valeur a reellement change.
    # ON REJOUE LES LIGNES D'ORIGINE DANS L'ORDRE, y compris celles qui ne
    # portent aucune cle. Avant, commentaires et lignes vides etaient perdus a
    # CHAQUE changement de statut : un frontmatter documente se vidait de ses
    # explications au fil des transitions, sans que personne ne le decide.
    lignes = [DELIMITEUR]
    vues = set()
    for ligne in (brutes or []):
        m = _LIGNE.match(ligne) if ligne and ligne[0] not in " \t" else None
        if not m:
            lignes.append(ligne)          # commentaire, ligne vide : tel quel
            continue
        cle = m.group(1)
        if cle not in meta:               # cle retiree par l'appelant
            continue
        if cle in vues:                   # ne peut plus arriver : lire() refuse
            continue
        vues.add(cle)
        try:
            inchangee = _valeur(m.group(2), 0) == meta[cle]
        except FrontmatterInvalide:
            inchangee = False
        # UNE LIGNE INCHANGEE EST REECRITE A L'OCTET. Re-rendre chaque valeur
        # transformerait `title: "x"` en `title: x` -- semantiquement identique,
        # textuellement different : le diff d'un simple changement de statut
        # ferait bouger toutes les lignes guillemetees.
        lignes.append(ligne if inchangee else "%s: %s" % (cle, _rendre(meta[cle])))
    for cle in meta:                      # cles ajoutees par l'appelant
        if cle not in vues:
            lignes.append("%s: %s" % (cle, _rendre(meta[cle])))
    lignes.append(DELIMITEUR)
    # Le corps est normalise puis restitue dans le style demande : sans cela, un corps
    # deja en CRLF melange les deux styles dans le meme fichier.
    corps = corps.replace("\r\n", "\n")
    return fins.join(lignes) + fins + corps.replace("\n", fins)


def statut(meta):
    """Rend le statut, ou leve si absent ou hors du vocabulaire ferme."""
    s = meta.get("status")
    if s is None:
        raise FrontmatterInvalide(
            "champ 'status' absent. Sans statut, le document sera relu a chaque session.")
    if s not in STATUTS:
        raise FrontmatterInvalide(
            "statut %r inconnu -- attendus : %s" % (s, ", ".join(STATUTS)))
    return s
