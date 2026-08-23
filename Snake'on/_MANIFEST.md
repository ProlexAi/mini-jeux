# _MANIFEST.md — Routeur de lecture de Snake'on

> ⚠️ **CE FICHIER EST UN ROUTEUR, PAS UNE SOURCE DE VÉRITÉ.**
> Il dit **quoi lire et dans quel ordre**. Il ne duplique aucun contenu et ne porte aucun chiffre.
> En cas de divergence entre ce fichier et la source qu'il désigne, **c'est la source qui fait foi**.
>
> Dernière révision : 2026-08-23.

---

## 0. À lire en ouvrant une session

1. **`cahier-des-charges-ui.md`** — la surface normative. Toute règle d'interface y est actée.
2. **`_MANIFEST.md`** (ce fichier) — pour savoir où aller ensuite.
3. **`analyse-concurrence.md`** — **avant toute recherche**, pour vérifier qu'elle n'a pas déjà
   été faite. C'est sa seule raison d'être.

Rien d'autre n'est à lire systématiquement. Le reste se consulte au besoin, via la table du §2.

---

## 1. Les quatre natures de document

Les mélanger est le défaut le plus coûteux d'un dépôt. La distinction tient en une phrase :

| Nature | Ce que le document affirme | Le geste quand c'est faux |
|---|---|---|
| **Canon** | « voici la règle » — non re-débattable | jamais réécrit : on **ajoute** une décision qui supersède |
| **Vivant** | « voici ce qui EST vrai » | **corrigé sur place**, avec sa date |
| **Log** | « voici ce qui ÉTAIT vrai à cette date » | **jamais réécrit** : on annote, on n'efface pas |
| **Machinerie** | rien — c'est un outil ou un gabarit | modifié comme du code, supprimé quand périmé |

**Test :** *ce document dit-il ce qui EST, ou ce qui ÉTAIT à une heure donnée ?*

### Classement des documents existants

| Document | Nature | Note |
|---|---|---|
| `cahier-des-charges-ui.md` | **Canon** | Jamais modifié en autonomie — voir §3 |
| `README.md` | Vivant | Comment lancer, tester, déployer |
| `_MANIFEST.md` | Vivant | Ce fichier |
| `analyse-concurrence.md` | **Log** | Entrées datées et sourcées, jamais supprimées |
| `RAPPORT-session-*.md` | Log | Un par session, jamais réécrit |
| `DIGEST-session-*.md` | Log | Version courte du rapport de la même session |
| `PROMPT-*.md` | Machinerie | Jetable : se supprime une fois sa session faite |

---

## 2. Où est la vérité — ne jamais deviner, aller lire

| Tu cherches… | Source unique |
|---|---|
| Une règle d'interface, un écran, un comportement acté | `cahier-des-charges-ui.md` |
| Le **pourquoi** d'une décision, et sa date | `cahier-des-charges-ui.md` §5 (registre par version) |
| **Une valeur chiffrée de gameplay** | l'objet `CONFIG` dans `index.html` — **jamais un document** |
| Ce que font les jeux concurrents, et ce qu'on en a retenu | `analyse-concurrence.md` |
| Ce qui s'est passé dans une session passée | `RAPPORT-session-*.md` / `DIGEST-session-*.md` |
| Le travail confié à une session à venir | le `PROMPT-*.md` correspondant |
| Comment lancer ou déployer | `README.md` (et le README racine du dépôt) |

> **Règle d'or.** Aucune valeur chiffrée de gameplay ne vit dans un document. Elle vit dans
> `CONFIG`, et un document qui en a besoin cite **la commande qui la relit** :
>
> ```bash
> grep -n "NOM_DE_LA_CLE" "Snake'on/index.html"
> ```
>
> Un chiffre recopié dans un document périme dès que le code bouge, et rien ne le recalcule.

---

## 3. Ce qui ne se fait jamais en autonomie

- **Modifier `cahier-des-charges-ui.md`.** Il est normatif. La procédure : finir la tâche, puis
  proposer un bloc « MODIFICATIONS DOC PROPOSÉES » — fichier, diff exacte, une phrase de
  justification — et attendre la validation. Un refus ne se rediscute pas.
- **Pousser sur `main`.** Le dépôt déploie automatiquement sur GitHub Pages à chaque push :
  **pousser, c'est publier**, sans étape intermédiaire ni filet.

---

## 4. Ce qu'on écrit en fin de session

Deux documents, jamais un seul :

- **`RAPPORT-session-<sujet>-<AAAA-MM-JJ>.md`** — le détail. Ce qui a été livré, les défauts
  trouvés **avec leur preuve**, ce qui a demandé plusieurs passes et pourquoi, ce qui reste
  ouvert.
- **`DIGEST-session-<sujet>-<AAAA-MM-JJ>.md`** — la version courte : décisions actées, chiffres
  clés, ce qui attend un arbitrage.

Et, si une recherche a été menée : **une entrée dans `analyse-concurrence.md`**, datée et sourcée.

---

## 5. Le piège de ce projet

Sur Snake'on, **les faux diagnostics viennent plus souvent de l'instrument que du code**. Quatre
cas relevés en une seule session, tous détaillés dans `RAPPORT-session-skins-2026-08-22.md` :

- un canvas non effacé entre deux passes, qui densifie le rendu et fait croire à un effet ;
- la tête du serpent hors cadre, qui fait mesurer zéro là où il y a quelque chose ;
- un écart mesuré entre deux points fixes qui **encadrent** l'élément cherché sans le toucher ;
- `window.innerWidth` à zéro dans un panneau non composité, qui annule toute unité relative.

**Avant de conclure qu'un correctif ne marche pas :** vérifier que le navigateur ne sert pas une
version en cache, que le viewport n'est pas nul, et que la mesure couvre exactement ce que
l'affirmation prétend.
