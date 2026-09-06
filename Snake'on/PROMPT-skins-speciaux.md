# Passation — Skins spéciaux à partir de sprites

> **Document jetable** (nature *machinerie*, cf. `_MANIFEST.md` §1). Il ouvre UNE session dédiée,
> puis se supprime. Il ne recopie aucune valeur du jeu : tout ce qui est chiffré ou énuméré se
> relit à la source, par la commande citée à côté. **Si une phrase d'ici contredit le code, c'est
> le code qui a raison.**
>
> Rédigé le 23/08/2026, avant la session.

---

## 1. Ce que cette session doit produire

Matt envoie, une par une, des **images de sprites de skins** générées par une autre IA. Chaque
image montre le même skin sous deux vues : une colonne de segments vus à plat (la matière du
corps) et une vignette du serpent entier (tête, corps, queue, halo).

Le travail de la session : **transposer chaque sprite en skin jouable** dans
`Snake'on/index.html`, cohérent avec les dix formes et les quatre effets déjà en place.

Deux cas, et c'est Matt qui dit lequel :

- **sprite validé tel quel** → le transposer sans le réinterpréter ;
- **sprite avec corrections** → il énonce ce qui doit changer (yeux manquants, queue à arrondir,
  teinte à corriger…). **Sa consigne prime toujours sur ce que l'image montre.**

Toute la session est dédiée à ça. Elle ne touche à rien d'autre.

---

## 2. La contrainte structurante — à lire avant toute autre chose

**Un sprite est une référence artistique, jamais un asset à importer.**

Le serpent n'est pas dessiné à partir d'images. Son corps est **un seul chemin**, tracé en
quatre passes superposées (halo, liseré de menace, cœur, contour). Le cahier des charges interdit
explicitement de repasser par un dessin par segment — c'est ce qui tient les 60 fps au-delà de
200 segments.

```bash
sed -n "$(grep -n "^    draw(ctx) {" "Snake'on/index.html" | tail -1 | cut -d: -f1),+120p" "Snake'on/index.html"
```

Donc « coder un skin » ne veut jamais dire découper l'image. Ça veut dire **lire le sprite comme
un cahier des charges visuel**, puis le reproduire avec les primitives du moteur.

### Trois conformations qui se font toutes seules

Vérifiées dans le code avant d'être écrites ici — inutile de coder quoi que ce soit pour elles :

| Ce que montre le sprite | Ce que fait le jeu, déjà |
|---|---|
| **Queue pointue, effilée** | La queue est **déjà ronde** : `lineCap='round'` et largeur constante `r*2`. Rien à faire. Et surtout rien à ajouter pour l'effiler : la largeur du cœur est non négociable. |
| **Tête sans yeux** | La tête dessine **toujours** des yeux. Le seul choix qui reste est leur *type* — ronds par défaut, fendus avec `head:'viper'` — jamais leur présence. |
| **Segments/perles bien séparés** | Le corps en jeu est un **tube lisse**. Une segmentation visible ne peut passer que par le **contour pointillé**, seul canal où un motif est autorisé. |

### Le piège du pointillé, déjà payé une fois

`dash` s'exprime en **multiples de r**, jamais en pixels, et `lineCap='round'` rallonge chaque
tiret de `r*0.35` de chaque côté. Un trou plus court que `r*0.7` est entièrement comblé : le
pointillé disparaît. Mesuré — un `dash:[6,4]` sur un rayon 15 changeait **exactement 0 pixel**.

---

## 3. Où en est le jeu

Modèle **forme + effet**, découplé le 23/08/2026 :

| Ce que tu cherches | Commande |
|---|---|
| Les formes et leurs styles | `grep -n "SKINS: \[" -A 14 "Snake'on/index.html"` |
| Les effets superposables | `grep -n "EFFECTS: \[" -A 6 "Snake'on/index.html"` |
| La fusion des deux | `grep -n "function currentStyle" -A 4 "Snake'on/index.html"` |
| La grille de la boutique | `grep -n "skinsRow" -A 30 "Snake'on/index.html"` |

Un effet se pose **par-dessus** une forme et l'emporte sur les clés qu'il définit. La boutique
(entrée `A01`, « 🛒 Boutique ») a deux catégories : **Effets** (ouverte par défaut) et **Skins**.

### Le vocabulaire de style que le moteur comprend

Il se relit — ne pas se fier à une liste recopiée :

```bash
grep -o "style\.\(dash\|dashAnim\|gradient\|hueShift\|hueStops\|pulse\|trail\|trailColor\|head\|glowBoost\|aura\)" "Snake'on/index.html" | sort -u
```

**Une clé absente de cette sortie n'existe pas.** L'écrire dans `CONFIG.SKINS` ne fait rien du
tout : le moteur ne la lit pas, et rien ne prévient. Ajouter une clé au vocabulaire est un
travail sur le moteur de rendu, à faire explicitement.

> **Contrôle utile à ajouter si la session crée des clés :** toute clé déclarée dans
> `SKINS`/`EFFECTS` doit apparaître dans la sortie ci-dessus. C'est une divergence silencieuse
> par construction, donc exactement le genre de chose qui mérite une commande rejouable
> (cf. `cahier-des-charges-ui.md` §9).

### Les invariants que rien ne révise

- **Cœur du corps** : alpha 1, largeur `r*2`. Seule sa **teinte** peut varier (dégradé). Jamais
  son opacité, jamais des pointillés dessus. C'est le repère qui permet de juger qui est plus
  gros — donc qui décide de la vie et de la mort.
- **Un seul chemin** pour le corps. Aucun style ne repasse par un dessin par segment.
- **Tout est proportionnel à `r`**, jamais en pixels absolus : le rayon va de 8 à 130.
- **La hitbox ne bouge jamais.** Cornes, crocs, halo, aura : décoration pure.
- **Tout ce qui s'anime a un repli figé identifiable**, pour `prefers-reduced-motion` et le
  palier de qualité `LOW`. Un skin qui deviendrait invisible une fois figé est refusé.
- **Les bots ne portent jamais de skin.**
- **Noms de skins en français**, non traduits (texte de jeu, cf. cahier des charges §7).
- **Fichier unique** `Snake'on/index.html` : HTML + CSS + JS, aucun build, aucune dépendance,
  canvas 2D, PWA hors-ligne. Pas de bibliothèque, pas de WebGL, aucun fichier image ajouté.
- **Mobile prioritaire**, cible tactile 44 × 44 px.

---

## 4. Le protocole, sprite par sprite

À suivre dans l'ordre, un sprite à la fois. Ne pas empiler trois skins avant la première
vérification.

### Étape 1 — Fiche de lecture, **avant** toute ligne de code

Écrire ce qu'on voit, en une dizaine de lignes : silhouette générale · palette exacte (teintes
relevées, pas devinées) · tête (yeux, appendices) · queue · halo (couleur, ampleur) · motif du
corps · animation que le sprite laisse supposer.

Puis, séparément : **ce que le sprite montre et qui n'est pas reproductible**, avec le motif.
C'est ce point qui appelle un arbitrage de Matt, pas le reste.

### Étape 2 — Classer : forme ou effet ?

- Le sprite définit la **matière du corps** (couleur, motif, texture) → c'est une **forme**
  (`CONFIG.SKINS`), elle va dans la catégorie « Skins ».
- Le sprite ajoute quelque chose **qui déborde du corps** et qui marcherait par-dessus n'importe
  quelle couleur → c'est un **effet** (`CONFIG.EFFECTS`), catégorie « Effets ».

En cas de doute, trancher pour la forme : un effet doit rester lisible sur les dix formes, ce qui
est une contrainte bien plus lourde à tenir.

### Étape 3 — Arbitrer la couleur identitaire

`skin.color` n'est **pas** seulement la couleur du corps. Elle sert aussi au pseudo, au
classement, à la minimap, à la pastille de la boutique et au multijoueur.

```bash
grep -n "currentSkin().color\|skin.color" "Snake'on/index.html"
```

Conséquence directe pour un skin à corps sombre (le sprite Foudre en est un : corps noir, halo
cyan) : **`color` ne peut pas être le noir**, sinon le serpent disparaît de la minimap et le
pseudo devient illisible. `color` prend la teinte identitaire — le cyan du halo — et le corps
sombre passe par une clé de style (dégradé, ou une clé à ajouter au vocabulaire).

### Étape 4 — Coder

Réutiliser le vocabulaire existant chaque fois qu'il suffit. N'étendre le moteur que quand le
sprite demande quelque chose qu'aucune clé ne sait faire, et alors : une clé nommée, documentée
au-dessus de `SKINS`, lue dans `draw()`, avec son repli figé.

### Étape 5 — Vérifier, et vérifier l'instrument avant la conclusion

- Le skin rendu **en jeu**, pas seulement dans un harnais.
- Aux deux extrêmes du rayon (8 et 130) : un motif calé à l'œil sur un rayon moyen se casse aux
  bornes.
- En `prefers-reduced-motion` et en qualité `LOW` : le skin reste-t-il reconnaissable ?
- Le bord du corps reste-t-il tranché, et le cœur net ?
- Sur fond de jeu réel, pas sur fond neutre.

### Étape 6 — Passer au suivant

Un skin fini avant d'en ouvrir un autre. Et son compte-rendu écrit au fil de l'eau, pas à la fin.

---

## 5. Le trou d'interface déjà connu

La pastille de la boutique est un **aplat de `skin.color`** avec une ombre portée de la même
teinte :

```bash
grep -n "btn.style.background = skin.color" -B 4 -A 4 "Snake'on/index.html"
```

Aucun aperçu de la matière. Deux skins à halo cyan y seront **indiscernables**, et un skin dont
tout l'intérêt est un motif d'éclairs y apparaîtra comme un rond cyan uni.

**Ma recommandation :** remplacer l'aplat par un aperçu réel — un court tronçon de serpent tracé
par le vrai code de rendu dans un mini-canvas, à un rayon fixe. Motif : sinon le travail fait sur
la matière ne se voit nulle part au moment du choix, et l'ajout de skins spéciaux perd son
intérêt commercial. C'est un chantier à part entière ; **à valider par Matt avant de l'ouvrir**,
et à ne pas mêler à la transposition d'un sprite.

---

## 6. Les questions à trancher, chacune avec ma recommandation

1. **Étendre le moteur de rendu est-il autorisé ?** *Recommandation : oui*, par ajout de clés au
   vocabulaire de style, jamais par un dessin par segment ni par un fichier image. Motif : les
   onze clés actuelles ne couvrent pas une texture de corps, et c'est précisément ce que les
   sprites apportent.
2. **Combien de skins spéciaux, et à quel palier se débloquent-ils ?** *Recommandation :
   déblocage par niveau, dans le prolongement des paliers existants*, tant que la question de la
   monnaie de jeu n'est pas tranchée (elle est ouverte depuis `PROMPT-effets-succes-boutique.md`
   et n'a pas été décidée). Motif : introduire une monnaie en passant, pour placer un skin,
   ferait prendre une décision de conception par effet de bord.
3. **Que faire du multijoueur ?** *Recommandation : ne rien faire ici.* Le protocole ne
   transporte pas l'apparence — un joueur distant apparaît uni chez les autres. C'est inscrit au
   §8 du cahier des charges et **le sujet appartient à la session partie privée**. Un skin
   spécial sera donc invisible pour les autres joueurs tant que ce n'est pas fait : le savoir,
   le dire à Matt, ne pas l'attaquer.
4. **Faut-il un aperçu réel dans la boutique ?** Voir §5 : recommandé, mais comme chantier
   distinct.

---

## 7. Les pièges mesurés de ce projet

Sur Snake'on, **les faux diagnostics viennent plus souvent de l'instrument que du code** — quatre
cas en une seule session, tous documentés dans `RAPPORT-session-skins-2026-08-22.md` :

- un canvas non effacé entre deux passes, qui densifie le rendu et fait croire à un effet ;
- la tête du serpent hors cadre, qui fait mesurer zéro là où il y a quelque chose ;
- un écart mesuré entre deux points fixes qui **encadrent** l'élément cherché sans le toucher ;
- `window.innerWidth` à zéro dans un panneau non composité, qui annule toute unité relative.

Deux autres, propres au rendu :

- **Le navigateur sert volontiers une version en cache.** Vérifier que le correctif est actif
  avant de conclure qu'il ne marche pas.
- **Les tirages pseudo-aléatoires écrits à la main.** Une sélection en `(k*A + t*B) % M` avec `B`
  multiple de `M` annule le terme de temps : les éclairs sont restés figés sur trois positions à
  vie. Le fichier porte un helper `hash01(a, b)` — l'utiliser, ne pas improviser un modulo.

---

## 8. Coordination et git

- **Trois autres worktrees travaillent le même `index.html`.** Rester dans sa branche, mesurer
  l'écart avant de coder (`git fetch` puis `git rev-list --left-right --count main...HEAD`), ne
  merger qu'après s'être annoncé. Enseignement payé : deux sessions qui commitent sur la même
  branche finissent par publier le travail l'une de l'autre sans l'avoir relu.
- **Pousser sur `main`, c'est publier** : le dépôt déploie sur GitHub Pages à chaque push, sans
  étape intermédiaire.
- `git add` par pathspec explicite, jamais `-A`. Une tâche = un commit.

---

## 9. Livrable et clôture

- Chaque sprite transposé, avec sa fiche de lecture et l'écart assumé entre l'image et le rendu.
- Les extensions du moteur documentées à l'endroit où elles se lisent.
- `node "Snake'on/verifie-traductions.js"` au vert si une clé d'interface a bougé.
- Un bloc **« MODIFICATIONS DOC PROPOSÉES »** pour `cahier-des-charges-ui.md` (fichier, diff
  exacte, une phrase de justification) — **jamais de modification en autonomie**.
- `RAPPORT-session-skins-speciaux-<AAAA-MM-JJ>.md` et son `DIGEST-…` correspondant.
- Ce document supprimé une fois la session faite.

---

## 10. Méthode attendue

- **Une question précise plutôt qu'une supposition**, et **chaque proposition arrive avec sa
  recommandation et son motif en une phrase** — y compris quand la recommandation est de ne rien
  faire.
- **Aucune affirmation sur le code sans l'avoir ouvert dans la session.**
- **Todo-list vivante**, visible dès le premier message, republiée entière à chaque changement.
- **Français** dans les échanges et les commentaires du code ; anglais réservé aux identifiants.
