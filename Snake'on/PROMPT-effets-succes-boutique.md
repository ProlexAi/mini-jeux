# Passation — Effets déblocables, succès et boutique

> **Document jetable.** Il ouvre UNE session dédiée, puis se supprime. Il ne recopie aucune
> valeur du jeu : tout ce qui est chiffré se relit à la source, citée à chaque fois. Si une
> phrase d'ici contredit le code, **c'est le code qui a raison**.

---

## 1. Où en est le projet

### Ce qui est livré et mesuré

**Treize skins**, tous fonctionnels, dans `Snake'on/index.html` :

- **Dix formes de base** (niveaux 1 à 20) : couleur, motif du contour, dégradé, pulsation du
  halo, et pour certaines une tête particulière (yeux fendus, cornes, crocs).
- **Trois auras élémentaires** (niveaux 25, 30, 35) : Flamme Ardente, Orage, Volutes. Ce sont
  des silhouettes vivantes qui épousent le contour du serpent, débordent de ses bords, et à
  travers lesquelles le serpent reste visible.

La liste fait foi dans le code :

```bash
grep -n "SKINS: \[" -A 20 "Snake'on/index.html"
```

### L'architecture de rendu, à ne pas défaire

Elle a coûté plusieurs cycles de correction. Les points structurants :

1. **L'ordre de dessin garantit la lisibilité.** Aura d'abord, translucide ; liseré sombre sur le
   bord du corps ; cœur du corps par-dessus à opacité pleine ; enfin une passe de « léchage »
   plafonnée. C'est cet ordre, et lui seul, qui autorise l'aura à déborder sans empêcher de
   juger sa taille — ce qui décide de la vie ou de la mort.
2. **Le corps est parcouru à pas constant en pixels**, jamais segment par segment. Le nombre
   d'ancrages reste dans les dizaines quelle que soit la longueur.
3. **Les auras sont des taches à dégradé radial superposées**, en fusion additive pour ce qui
   émet de la lumière (flamme, foudre) et normale pour ce qui l'absorbe (fumée). Un polygone
   rempli en aplat ne lira jamais comme du feu : cela a été essayé et rejeté.
4. **Tout est proportionnel au rayon**, jamais en pixels absolus.
5. **Chaque effet animé a un repli figé** identifiable, pour `prefers-reduced-motion` et le
   palier de qualité le plus bas.

### Ce qui reste ouvert côté skins

Rien de bloquant. Deux réserves connues, ni l'une ni l'autre urgente :

- Le **budget de particules est saturé** en partie chargée, indépendamment des skins : les bots,
  les morts et les kill streaks le remplissent seuls. Les étincelles de la Flamme cèdent donc la
  place proprement, mais deviennent rares. Si on les veut visibles, il faudra leur réserver une
  part du budget.
- La **stabilité à 60 fps n'a pas pu être certifiée** : les mesures ont été prises dans un onglet
  d'arrière-plan non composité, où même un skin sans aucune aura produit des pics à 378 ms. Seule
  la médiane est exploitable, et elle est confortable. À rejouer au premier plan sur la machine
  cible.

---

## 2. Ce que cette session doit produire

Matt veut **découpler la forme et l'effet**.

> Tous les serpents existent sous les dix formes de base. Par-dessus, on ajoute des **effets**
> qui se débloquent — via les succès, les séries de kills, ou une **boutique** alimentée par des
> récompenses gagnées en partie.

Aujourd'hui les trois auras sont des skins entiers, au même rang que les dix formes, et
mutuellement exclusifs avec elles. Il faut passer à **forme + effet**, combinables.

### Les questions à trancher, chacune avec ta recommandation

1. **Modèle de données.** Le skin sélectionné est aujourd'hui un index unique. Il faut au moins
   deux emplacements — forme et effet — dans la sauvegarde. Comment migrer les sauvegardes
   existantes sans perdre le skin choisi ? La compatibilité ascendante est obligatoire : un
   joueur qui revient ne doit rien perdre.
2. **Combinaisons.** Dix formes × N effets. Toutes les combinaisons sont-elles permises, ou
   certaines sont-elles interdites parce qu'illisibles ? Le point de vigilance est réel : la
   Flamme sur une forme déjà claire, ou une aura de fumée sur un corps blanc, ont déjà posé des
   problèmes de contraste — le code porte un helper de luminance pour cette raison.
3. **Écran des skins.** Une grille de dix devient une grille de dix **plus** une grille d'effets,
   avec un aperçu de la combinaison. Sur mobile, cible tactile de 44 × 44 px minimum. Comment
   éviter que ça devienne illisible ?
4. **Source de déblocage.** Succès, séries de kills, boutique : les trois coexistent-ils ? Un
   même effet peut-il s'obtenir de deux façons ? Que se passe-t-il si un effet est équipé puis
   que sa condition cesse d'être remplie ?
5. **Boutique et monnaie.** S'il y a une monnaie, elle se gagne en partie et se dépense hors
   partie. Attention : **aucun achat réel**, aucun paiement. C'est une monnaie de jeu.
6. **Séries de kills.** Le jeu a déjà des effets de kill streak (`CONFIG.KILL_EFFECTS`) qui sont
   des effets visuels temporaires. Les nouveaux effets déblocables s'y ajoutent-ils, les
   remplacent-ils, ou cohabitent-ils ? Trancher, sinon deux systèmes visuels se marcheront dessus.

### Contraintes non négociables

- **Fichier unique** `Snake'on/index.html` : HTML, CSS et JS, sans build, sans dépendance,
  canvas 2D, PWA hors-ligne. Pas de bibliothèque tierce, pas de WebGL.
- **`Snake'on/cahier-des-charges-ui.md` est normatif.** Ne jamais le modifier en autonomie :
  finir par un bloc « MODIFICATIONS DOC PROPOSÉES » (fichier, diff exacte, une phrase de
  justification) soumis à Matt.
- **`Snake'on/analyse-concurrence.md`** garde la mémoire des recherches sur les jeux concurrents.
  Toute nouvelle analyse comparative s'y écrit, datée et sourcée. Le relire **avant** de chercher :
  la boutique et les monnaies de jeu n'y sont pas encore traitées, mais la prédation, les bots,
  la longueur maximale et les textures y sont.
- **Six langues** d'interface, mais les **textes de jeu restent en français** — noms de skins,
  succès, toasts. Règle au §7 du cahier des charges : l'appliquer, ne pas la réinventer.
- **Mobile prioritaire.** `prefers-reduced-motion` respecté.
- **Français** dans les échanges et les commentaires ; anglais réservé au code et aux
  identifiants.

### Méthode attendue

- Une question précise à la fois plutôt qu'une supposition, et **chaque proposition arrive avec
  ta recommandation et son motif en une phrase**, y compris quand la recommandation est de ne
  rien faire.
- **Aucune affirmation sur le code sans l'avoir ouvert dans la session.**
- **Vérifie ton instrument avant ta conclusion.** Sur ce projet, trois faux diagnostics sont
  venus du harnais de mesure et non du code : un canvas non effacé entre les passes qui
  densifiait le rendu, une tête de serpent hors cadre, un écart mesuré entre deux points fixes
  qui encadraient l'élément cherché sans jamais le toucher. Et le navigateur sert volontiers une
  version en cache : vérifier que le correctif est bien actif avant de conclure qu'il ne marche
  pas.
- **Méfie-toi des tirages pseudo-aléatoires écrits à la main.** Un bug de ce type a survécu
  longtemps ici : une sélection en `(k * A + t * B) % M` où `B` était un multiple de `M`, ce qui
  annulait purement et simplement le terme de temps. Le code porte désormais un helper de
  hachage ; l'utiliser plutôt que d'improviser une formule modulo.

---

## 3. Livrable

- Le modèle forme + effet implémenté, avec la migration des sauvegardes existantes.
- L'écran des skins refait, testé au doigt sur mobile.
- Le système de déblocage retenu, et la boutique si elle est validée.
- Les mesures qui prouvent que la lisibilité en jeu est préservée sur les combinaisons permises :
  le cœur du corps doit rester net et le bord détectable, quelle que soit la combinaison.
- Le bloc « MODIFICATIONS DOC PROPOSÉES » pour le cahier des charges.
- Les entrées ajoutées à `analyse-concurrence.md` si une recherche a été menée.
