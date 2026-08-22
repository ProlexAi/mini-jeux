# Analyse de fonctionnement des concurrents — Snake'on

**Rôle de ce document.** Mémoire des recherches faites sur les jeux `.io` concurrents, pour ne
plus les refaire. Toute analyse comparative menée pour Snake'on **s'écrit ici**, datée, avec sa
source et la décision qu'elle a servie.

**Règle d'écriture.** Une entrée = un sujet. Chacune porte : la date, la question posée, ce qui
a été trouvé **avec sa source**, et ce qu'on en a fait pour Snake'on. Une entrée n'est jamais
supprimée ; si elle devient fausse, on l'annote sans l'effacer — savoir qu'une piste a été
explorée et écartée vaut autant que la conclusion.

**Ce document décrit les AUTRES jeux.** Les décisions propres à Snake'on vivent dans
`cahier-des-charges-ui.md`, qui reste la surface normative.

---

## 1. Prédation : qui mange qui ?

*Recherché le 22/08/2026. Question : quand deux serpents se touchent, qu'est-ce qui décide de
l'issue ? Motivée par un blocage constaté en jeu — être plus gros ne suffisait pas à manger.*

### Deux paradigmes opposés, à ne pas confondre

**slither.io — la masse ne compte pas du tout.**
La tête qui touche un corps meurt, quelle que soit la taille des deux serpents. Un petit serpent
peut donc tuer un géant en lui coupant la route pour que sa tête percute son corps. Conséquence
de conception assumée : les plus gros ne sont pas les plus en sécurité, et la manœuvrabilité
prime sur la masse.
Source : [Slither.io Wiki — Tips](https://slitherio-archive.fandom.com/wiki/Tips)

**agar.io — la masse décide, avec une marge.**
Il faut être **au moins 25 % plus gros** (facteur 1,25) pour absorber une autre cellule. Une
cellule issue d'une division doit, elle, être 33 % plus grosse. La marge existe pour éviter que
deux cellules quasi identiques ne s'absorbent au hasard des collisions.
Source : [Agar.io Wiki — Cell](https://agario.fandom.com/wiki/Cell)

### Ce que Snake'on a choisi

**Le modèle agar.io, pas celui de slither.io** : la masse prime, le plus gros écrase. Décision de
Matt, réaffirmée le 22/08/2026 — « si j'ai mangé plus que les autres, j'ai une plus grosse masse,
c'est moi qui écrase les autres ».

**La marge d'agar.io est reprise telle quelle : +25 % de masse pour absorber**, validé par Matt
le 22/08/2026. Elle évite que deux serpents de masses quasi identiques ne s'absorbent au hasard
des collisions.

> *Historique, à ne pas rouvrir sans élément nouveau.* Une première version avait supprimé toute
> marge, pour corriger un blocage où être plus gros ne suffisait pas à manger. Le diagnostic
> était incomplet : la vraie cause n'était pas la marge mais le fait qu'elle portait sur le
> **rayon plafonné** (voir ci-dessous). La marge a donc été rétablie à 1,25 une fois la
> comparaison passée sur la masse.

**La masse n'est ni le rayon, ni la longueur affichée.** C'est le cumul de tout ce qui a été
mangé, et elle n'a **aucun plafond**. La longueur affichée et le rayon, eux, sont plafonnés :
ce sont des contraintes de rendu, pas de jeu. Au-delà du plafond, le serpent continue donc de
prendre de la masse sans s'allonger à l'écran — même principe que slither.io (§3).

**Le ralentissement suit la masse**, jamais le rayon : au rayon plafonné, deux masses très
différentes donnaient exactement la même vitesse. La courbe sature à une masse de référence,
faute de quoi un serpent très lourd finirait immobile.

### Piège à ne pas rouvrir : le rayon plafonné

Snake'on faisait sa comparaison sur le **rayon**, or celui-ci est plafonné (`MAX_RADIUS`) alors
que la longueur continue de croître. Deux serpents au plafond affichent donc le même rayon quelle
que soit leur masse réelle, et **plus personne ne peut manger personne**. Une comparaison de
prédation ne doit jamais porter sur une grandeur plafonnée : elle porte sur la masse.

Commande qui donne les valeurs en vigueur :

```bash
grep -n "MAX_RADIUS\|MAX_LENGTH\|BOT_MAX_LENGTH\|EAT_MASS_RATIO\|SPEED_REF_MASS\|BASE_MASS" "Snake'on/index.html"
```

**Conséquence à ne pas perdre de vue.** Le rayon étant plafonné et la masse ne l'étant pas, deux
serpents au plafond ont la même épaisseur à l'écran alors que l'un peut dévorer l'autre. Le
joueur ne peut donc plus juger le rapport de force à l'œil seul une fois le plafond atteint.
C'est un écart avec la contrainte de lisibilité du §2 du cahier des charges, et il reste ouvert.

---

## 2. Comportement des bots : la traque collante

*Recherché le 22/08/2026. Question : pourquoi se faire suivre par un bot est-il frustrant, et
comment les concurrents l'évitent ?*

### Le problème constaté dans Snake'on

Un bot dont la vitesse est quasi identique à celle du joueur et qui le prend en chasse ne le
lâche jamais. À chaque fois que le joueur grossit, la queue qu'il vient d'allonger passe à portée
du poursuivant, qui la coupe. **Le joueur ne peut donc structurellement pas grossir** tant qu'il
est suivi.

Trois causes cumulées, propres à Snake'on :

1. La vitesse ne dépend que du rayon, et le rayon est plafonné — un poursuivant plafonné va
   exactement aussi vite que sa cible plafonnée.
2. Le bot n'abandonne jamais sa poursuite : aucune condition de désengagement, ni de durée, ni de
   distance.
3. Le corps du joueur s'allonge derrière lui, donc grossir **augmente** la surface offerte au
   poursuivant. La croissance se punit elle-même.

### Ce que font les concurrents

Dans slither.io, la question ne se pose pas de la même façon : la masse ne protège de rien, un
poursuivant n'a aucun avantage mécanique à suivre, et l'accélération se paie en masse perdue, ce
qui rend la traque coûteuse. Le désengagement est donc économique, pas scripté.
Source : [Slither.io Wiki — Slithering](https://slitherio.fandom.com/wiki/Slithering)

**Conclusion transposable.** Puisque Snake'on a choisi le modèle de la masse (§1), il ne peut pas
importer le désengagement économique de slither.io. Il lui faut un désengagement **explicite** :
un bot doit renoncer, et un poursuivant ne doit jamais être aussi rapide que sa proie.

*Décision et paramètres retenus : voir le journal du dépôt et `cahier-des-charges-ui.md`.*

---

## 3. Longueur maximale d'un serpent

*Recherché le 22/08/2026, entrée conservée pour éviter une quatrième recherche.*

- **slither.io** : pas de plafond de segments exposé. La masse plafonne visuellement vers 40 000,
  au-delà de quoi le score continue de monter sans que le serpent grossisse à l'écran. Le record
  rapporté dépasse 200 000.
  Source : [Slither.io Wiki — Length](https://slitherio-archive.fandom.com/wiki/Length)
- **Clone open source de référence** (`phocode/slither.io`) : plafond explicite à **500 points**,
  motivé noir sur blanc par la performance.
  Source : [phocode/slither.io](https://github.com/phocode/slither.io)

**Pour Snake'on.** Le plafond joueur est plus haut que celui de ce clone, ce qui est cohérent :
le corps est tracé en **un seul chemin**, technique nettement moins coûteuse que le dessin par
segment qu'emploie le clone. Valeur en vigueur :

```bash
grep -n "MAX_LENGTH" "Snake'on/index.html"
```

---

## 4. Textures d'effets (feu, foudre, fumée)

*Recherché le 22/08/2026. Question : faut-il des assets externes pour obtenir des effets
crédibles ?*

**Conclusion : non, et c'est tranché.** Le rendu convaincant ne vient pas d'illustrations mais de
la **technique de composition** : fusion additive (`globalCompositeOperation = 'lighter'`) pour ce
qui émet de la lumière, taches à dégradé radial superposées pour obtenir des bords doux. Un
polygone rempli en aplat ne lira jamais comme du feu, quelle que soit sa palette.

**Pourquoi les planches de sprites ont été écartées** : le jeu est un fichier unique hors-ligne,
donc toute planche finit en base64 dans `index.html` (vite 0,5 à 2 Mo) ; la teinte par skin est
malaisée sur un sprite déjà colorié ; et la cohérence entre images d'une planche générée par IA
est souvent mauvaise, ce qui se voit en boucle. Enfin, cela n'épargne pas le travail d'animation.

*Ne pas rouvrir sans élément nouveau.*
