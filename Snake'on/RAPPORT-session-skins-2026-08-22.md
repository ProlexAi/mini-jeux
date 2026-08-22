# Rapport de session — Skins, prédation par masse et équilibrage

**Date :** 22/08/2026
**Branche :** `claude/snakeon-skins-system-af98cf` — 17 commits
**Point de départ :** `c9dcf73`
**Périmètre initial :** brainstorm sur les skins. Il s'est étendu, à la demande de Matt, à la
prédation, au comportement des bots, à la taille du monde et à la télémétrie.

---

## 1. Ce qui a été livré

### Skins — 13 au total

**Dix formes de base** (niveaux 1 à 20), qui changent le trait du corps et la tête : motif du
contour, dégradé, pulsation du halo, yeux fendus, cornes, crocs.

**Trois auras élémentaires** (niveaux 25, 30, 35) — Flamme Ardente, Orage, Volutes. Ce sont des
silhouettes vivantes qui épousent le contour, débordent de ses bords, et à travers lesquelles le
serpent reste visible.

### Prédation par masse

La masse est désormais une grandeur explicite, **sans plafond**, découplée de la longueur
affichée et du rayon, qui restent plafonnés comme contraintes de rendu. Modèle agar.io : il faut
**+25 % de masse** pour absorber. Le ralentissement suit la masse, plus le rayon.

### Liseré de menace

Le contour de chaque serpent porte le rapport de force avec le joueur local : **rouge et large**
s'il peut vous dévorer, **sombre et discret** à l'égalité, **vert et fin** s'il est votre proie.
Couleur *et* épaisseur, pour rester lisible sans distinguer les teintes. Légende ajoutée à
l'écran de bienvenue, dans les six langues.

### Bots

Désengagement explicite de la traque — durée maximale, distance d'abandon, repos avant
réengagement — et malus de vitesse au poursuivant. Plafond de masse à 1500.

### Monde

Porté de 16 à **58 écrans**, à l'échelle d'agar.io. Peuplement porté de 45 à 150 bots, les deux
réglages étant indissociables.

### Télémétrie

Ligne `ping / fps` discrète au HUD. Le ping mesure un aller-retour réel vers l'hébergeur ; il
affiche `—` hors-ligne, faute de serveur de jeu.

### Documentation

- `analyse-concurrence.md` — **nouveau.** Mémoire des recherches sur les jeux concurrents, pour
  ne plus les refaire. Cinq entrées, chacune sourcée et datée.
- `PROMPT-effets-succes-boutique.md` — **nouveau.** Passation pour la session dédiée aux effets
  déblocables et à la boutique.
- `cahier-des-charges-ui.md` — addenda v0.4 et v0.5, validés par Matt avant écriture.

---

## 2. Ce qui a demandé plusieurs passes

Trois sujets ont nécessité d'être repris après un premier jet insuffisant, chaque fois parce que
la mesure a contredit ce que je croyais avoir livré.

**Les skins « invisibles ».** Le premier jet posait bien un style par skin, mais rien ne se
voyait. En rendant les dix skins dans une **couleur imposée identique** — ce qui isole ce qu'un
skin change au-delà de la teinte — quatre d'entre eux modifiaient moins de 1 % des pixels du
serpent. Trois causes : des pointillés écrits en pixels absolus qu'un `lineCap` arrondi avalait
intégralement, un motif blanc sur un corps blanc, des cornes à la couleur du corps.

**Le rendu des auras.** Le premier rendu, jugé « dégueulasse » par Matt à juste titre, employait
des polygones remplis en aplat, à bords nets. C'est la mauvaise technique pour du feu. Refondu en
taches à dégradé radial superposées, en fusion additive pour ce qui émet de la lumière.

**La prédation.** Le premier diagnostic — supprimer la marge de 10 % — était incomplet. La vraie
cause était que la comparaison portait sur le **rayon plafonné** : deux serpents au plafond
étaient à égalité quelle que soit leur masse. La marge a pu revenir à 25 % une fois la
comparaison passée sur la masse.

---

## 3. Défauts trouvés et corrigés

| Défaut | Cause | Preuve |
|---|---|---|
| Pointillés invisibles | `lineCap:'round'` rallonge chaque tiret de `lineWidth/2` | `[6,4]` sur un contour de 10,5 px changeait **0 pixel** |
| Traînée invisible | particules émises à la tête, que le corps recouvre en permanence | corrigé par émission à la queue, 2 r en retrait |
| Éclairs figés sur 3 positions | `(k*A + t*B) % 23` avec `B = 23 × 1761` : le terme de temps s'annulait | 27 ancrages sur 30 ne portaient **jamais** d'arc |
| Débordement d'aura hors spec | le plafond portait sur le centre de la tache, pas sur ce qu'elle peint | 3 r mesurés pour un plafond de 1,8 |
| Masse au plancher après amputation | portion calculée sur la longueur nominale, supérieure aux segments réels | couper en deux ramenait la masse à 10 |
| Bot devenu colosse | aucun plafond de masse pour les bots | 31 574 après 15 min, écran saturé |

---

## 4. Le piège de méthode de cette session

**Quatre faux diagnostics sont venus du harnais de mesure, aucun du code.** C'est le principal
enseignement, et il vaut pour toute session future sur ce projet.

1. **Canvas non effacé entre les passes.** Je dessinais 55 fois sur le même canvas ; en version
   figée les passes se superposaient à l'identique et s'accumulaient en additif. J'en ai conclu
   que le figé était plus riche que l'animé — faux, l'effet n'existait que dans mon harnais.
2. **Tête du serpent hors cadre.** J'en ai conclu que les skins ne changeant que la tête ne
   changeaient rien : ils mesuraient 0 % parce que la tête sortait du canvas.
3. **Mesure entre deux points fixes qui encadrent l'élément cherché.** Un liseré fin passait pour
   absent, avec un contraste chutant à 5 %. Mesuré au gradient de traversée : 96 à 109 %.
4. **`window.innerWidth === 0`.** Le panneau navigateur n'étant pas composité, toute unité
   relative au viewport se résout à zéro. J'en ai conclu à un CSS effondré, puis à un
   `WORLD_MAX` sans effet — les deux étaient faux.

**Règle qui en découle :** avant de conclure qu'un correctif ne marche pas, vérifier que le
navigateur ne sert pas une version en cache, que le viewport n'est pas nul, et que l'instrument
mesure bien ce que l'affirmation prétend.

---

## 5. Ce qui reste ouvert

**Un arbitrage qui revient à Matt** — le seul point bloquant pour une base réellement propre :

> **Une découpe joue le son de kill et les particules de mort, mais ne compte pas comme un kill.**
> Mesuré : la cible passe de 120 à 51 segments, survit, et le compteur ne bouge pas. Seule une
> dévoration tête-contre-tête compte, et là le compteur monte correctement. Le compteur n'est
> donc pas cassé : c'est le retour sensoriel qui ment. Trois issues possibles — faire compter la
> découpe (mais on « tuerait » dix fois le même serpent), distinguer le retour sensoriel
> (recommandé), ou afficher les deux compteurs séparément. **Non corrigé faute d'arbitrage.**

**Deux réserves connues, non bloquantes :**

- Le **budget de particules est saturé** en partie chargée, indépendamment des skins. Matt l'a
  validé comme conforme à l'objectif.
- La **stabilité à 60 fps n'est pas certifiée** : mesurée dans un onglet d'arrière-plan où même
  un skin sans aura pique à 378 ms. Seule la médiane est exploitable, et elle est confortable
  (2,6 ms sur 16,67). À rejouer au premier plan.

**Un curseur à ajuster au ressenti :** les 150 bots. La table de mesures donne le rendu à 45,
120 et 160.

---

## 6. Coordination

Une session parallèle travaille la partie privée multijoueur. Matt a tranché que le modèle de
masse de cette session-ci fait autorité ; l'autre a retiré ses critères concurrents et rebase
derrière. Quatre échanges ont porté sur : le transport de la masse (`massValue` et non le
getter, Uint32 et non Uint16), la vérification que le liseré est bien calculé par joueur local,
et un trou trouvé dans son paquet minimap — non filtré mais dépourvu de masse, il aurait affiché
une carte muette sur la menace lointaine qu'elle sert précisément à repérer.
