# 🐍 Snake'on

Arène survivor-like néon dans un **grand monde qui défile** : mange, grossis, dévore les serpents
plus petits que toi. Seul face à 45 bots, ou **à plusieurs dans la même arène** en s'échangeant un
code. **100 % HTML/JS/CSS**, aucun build, aucun serveur. Installable comme une vraie appli
(**PWA**) et **jouable hors-ligne** en solo.

▶️ **Jouer : https://prolexai.github.io/mini-jeux/Snake'on/**
*(ce jeu fait partie du dépôt [mini-jeux](../README.md), qui en regroupe plusieurs)*

---

## 🎮 Comment on joue

| Support | Contrôle |
|---|---|
| Mobile / tablette | Le serpent suit ton **doigt** |
| Ordinateur | Le serpent suit la **souris** |
| Clavier | `Échap` ou `P` = pause · `Entrée` / `Espace` = jouer |

**But :** grossir le plus possible, **sans fin** — comme sur slither.io, la partie ne s'arrête
jamais d'elle-même. Une seule façon de « gagner » : arriver **en tête du classement** et choisir
de t'arrêter là, depuis Pause, pour empocher le bonus de victoire.
Face à 150 adversaires, seul un coup sur la **tête** détruit complètement un serpent (il faut être
25 % plus lourd) ; toucher son **corps** ne le tue pas — ça le "coupe" : il perd la partie amputée
mais **survit**, raccourci. Le tronçon amputé devient des pastilles de nourriture, dont la taille
et le gain sont proportionnels à ce qui a été coupé. Toucher un corps plus gros ou égal agit comme
un mur.

**Un kill, c'est une élimination complète — jamais une découpe.** Le compteur ne monte qu'en
mangeant une tête, et le jeu le dit maintenant : une découpe a son propre son, sec et bref, et sa
propre gerbe de particules dirigée le long de la coupure. Sans ça on croyait tuer à chaque touche,
et il aurait suffi de couper dix fois le même serpent pour « le tuer » dix fois. Tu es **invincible 3 secondes** à l'apparition, le temps de te placer. À la mort, la caméra suit
4 secondes le serpent qui t'a mangé, puis tu réapparais aussitôt dans la **même arène**. Une
pop-up explique tout ça en quelques secondes à la toute première partie — jamais revue ensuite.

**Quitter ne coûte jamais rien.** Deux sorties existent : **🏳 Quitter la partie** depuis Pause
(contour rouge, confirmation obligatoire) et **Quitter** sur la bannière qui suit ta mort. Les
deux comptent la vie en cours exactement comme si tu avais continué — XP, stats, entrée à
l'historique. Une partie commencée en attendant quelqu'un ne se perd donc pas quand cette
personne arrive. Le rouge signale seulement que c'est **irréversible** : on ne revient pas dans
la même arène. Si tu es **en tête du classement**, le bouton devient **Terminer la partie** et
l'XP est majoré d'un bonus de victoire.

---

## 🌐 Jouer à plusieurs (partie privée)

Le bouton **🌐 Partie Privée** de l'accueil ouvre un **salon** : l'un crée un salon et reçoit un
**code de 5 caractères** (sans `0`/`O` ni `1`/`I`/`L`, pour qu'il se dicte à voix haute sans
confusion), les autres le saisissent pour le rejoindre. Tout le monde joue alors dans **la même
arène**, mêlé aux bots. On peut rejoindre **en cours de partie** : on apparaît aussitôt, protégé
par le bouclier d'apparition.

C'est du **pair-à-pair (WebRTC)** : la partie ne transite par aucun serveur, seule la mise en
relation passe par un annuaire public. Celui qui crée le salon fait autorité sur la partie ; s'il
quitte, la partie s'arrête pour tout le monde — mais chacun **garde l'XP** de la vie en cours,
personne ne paie une coupure qu'il n'a pas causée. Aucun compte, aucune donnée qui sort de ton
appareil : la progression reste dans ton navigateur, comme en solo.

**Ce que ça coûte à celui qui héberge.** L'hôte simule toute la partie et envoie à chacun
seulement ce qu'il peut voir, en binaire. Les corps ne voyagent jamais : chaque joueur redessine
la traînée chez lui, si bien que le coût dépend du nombre de serpents en vue, pas de leur
longueur. Mesuré en montée chez l'hôte, à 9 joueurs connectés : **26 ko/s en début de partie,
39 ko/s en fin** — environ 300 kbit/s, ce que tient n'importe quelle connexion moderne.

⚠️ **Mettre pause ne fige pas la partie des autres.** Pendant ta pause, ton serpent passe en
pilotage automatique (il fuit, il ne chasse pas) — **tu peux te faire manger pendant ce temps**,
et le jeu te le dit. Le bouton Partie Privée est désactivé hors ligne, avec le motif affiché.

L'hôte peut changer d'onglet ou réduire sa fenêtre sans arrêter la partie des autres : le
navigateur suspend `requestAnimationFrame` dans un onglet caché, donc la simulation est cadencée
par un Web Worker de secours dès qu'elle héberge (mesuré : 0 instantané par seconde sans lui,
13 avec).

---

**Bonus :** ⚡ Vitesse (×1,8) · 🧲 Aimant (attire la nourriture) · 🛡️ Invincible.
**Progression :** XP, niveaux, 10 skins à débloquer, 8 succès, historique des 10 dernières vies.
**Réglages :** son (musique / effets séparés), qualité graphique (Low/Medium/High), rappel des
commandes — accessibles à tout moment depuis l'onglet ⚙️ du menu. La **musique est générée**, comme
les sons : aucun fichier, une boucle de seize secondes sur quatre accords, volontairement discrète.
À zéro, le curseur l'arrête vraiment ; un onglet en arrière-plan la met en veille.
Tout est sauvegardé dans le navigateur (`localStorage`), rien n'est envoyé nulle part.

---

## 🗺️ Le monde

La carte ne tient **pas** dans l'écran : la caméra suit le serpent, la carte défile sous lui,
et on **dézoome en grossissant** pour continuer à voir venir le danger.

Sa taille n'est pas fixe, elle est **calculée au début de chaque partie** : le monde vaut toujours
**16 écrans de surface** (au-delà de 6000 px sur un axe, le monde est plafonné en conservant son
ratio — l'aire de 16 écrans n'est alors plus garantie, c'est le compromis qui protège la grille
spatiale et le nombre de pastilles sur très grand écran). Un écran de téléphone voit 2,3× moins de
surface qu'un écran d'ordinateur — un monde de taille fixe serait désert sur l'un ou étouffant sur
l'autre. À l'arrivée :

| Écran | Monde | Nourriture | Adversaires visibles en moyenne |
|---|---|---|---|
| Ordinateur 1100×700 | 4400 × 2800 | 560 | ~1,9 |
| iPhone 390×844 (plein écran) | 1987 × 2650 | 239 | ~1,8 |

La nourriture n'est **pas** éparpillée uniformément : elle apparaît par **amas** (une quinzaine de
pastilles par zone, comme sur slither.io), avec des poches vides entre les amas — des zones plus
riches à repérer et à disputer plutôt qu'un nuage homogène.

La **minimap** en bas à droite montre le monde entier, ta position, celle des 45 serpents,
et le rectangle blanc = la portion que tu vois réellement.
Le **mur cyan** marque le bord du monde.

---

## 🚀 Mettre le jeu en ligne (GitHub Pages)

L'activation de GitHub Pages se fait une seule fois, au niveau du dépôt `mini-jeux` — voir le
[README racine](../README.md#mettre-le-portail-en-ligne-github-pages). Une fois activée, ce jeu
est automatiquement servi sur `https://prolexai.github.io/mini-jeux/Snake'on/`.

---

## 📲 Installer l'appli

| Système | Manip |
|---|---|
| **Android / Chrome** | Un bouton **« Installer l'appli »** apparaît dans le menu du jeu |
| **iPhone / Safari** | Bouton **Partager** ⬆ → **« Sur l'écran d'accueil »** |
| **Windows / Mac** | Icône d'installation dans la barre d'adresse de Chrome ou Edge |

Une fois installé : plein écran, sans barre de navigateur, **et ça marche sans réseau**.

---

## 📁 Ce qu'il y a dans le dépôt

```
index.html              le jeu entier : HTML + CSS + JS + sons générés (aucune image, aucune lib)
manifest.webmanifest    carte d'identité de l'appli (nom, icônes, couleurs, plein écran)
sw.js                   service worker : met le jeu en cache pour le hors-ligne
icons/                  icônes de l'appli (192, 512, maskable, Apple, favicon)
verifie-traductions.js  contrôle : les 6 langues sont complètes (node, hors jeu)
.nojekyll               dit à GitHub Pages de servir les fichiers tels quels
```

La partie privée charge **PeerJS** depuis un CDN, à l'ouverture du salon seulement : le jeu solo
ne dépend de rien et reste jouable hors-ligne.

Pourquoi pas **un seul** fichier HTML ? Le jeu, lui, l'est : tout tient dans `index.html`.
Mais une PWA impose que le **manifest** et le **service worker** soient des fichiers séparés —
le navigateur refuse un service worker écrit à l'intérieur d'une page. C'est lui qui donne le hors-ligne.

---

## 🔧 Régler le jeu

Tout est regroupé dans l'objet `CONFIG`, tout en haut du `<script>` de `index.html`.

| Réglage | Effet |
|---|---|
| `FOOD_GROWTH: 2` | taille gagnée par pastille |
| `WORLD_SCREENS: 16` | taille du monde, en écrans de surface — monte-le pour une carte plus vaste |
| `BOT_COUNT: 45` | nombre d'adversaires (la densité de rencontres) |
| `BOT_MAX_LENGTH: 300` | plafond des bots, pour qu'aucun ne finisse par dominer toute l'arène |
| `SPAWN_SHIELD_MS: 3000` | invincibilité à l'apparition (et à chaque réapparition) |
| `SPECTATE_MS: 4000` | durée de la vue sur le tueur avant de réapparaître |
| `FOOD_AREA_PER_ITEM` | densité de nourriture (px² par pastille) |
| `FOOD_CLUSTER_RADIUS` / `FOOD_PER_CLUSTER` | rayon d'un amas de pastilles / pastilles visées par amas |
| `MIN_ZOOM: 0.45` | jusqu'où on dézoome quand on devient énorme |
| `MIN_SPEED_RATIO: 0.65` | vitesse minimale (fraction de la vitesse de base) à la taille max |
| `POWERUPS` / `SKINS` | durées, couleurs, niveaux de déblocage |

Juste après l'objet `CONFIG`, deux tables séparées pilotent la qualité graphique (onglet
Réglages) : `QUALITY_DPR` (plafond de résolution de l'écran) et `QUALITY_PARTICLES` (nombre max
de particules à l'écran) — une entrée par niveau (`LOW` / `MEDIUM` / `HIGH`).

⚠️ Le manifest et les icônes sont en cache-first : **après une modification de `manifest.webmanifest`
ou de `icons/`**, change `CACHE_VERSION` dans `sw.js` (`'v1'` → `'v2'`…) sinon les joueurs gardent
l'ancienne version en cache. `index.html` (donc `CONFIG`) est en network-first : il arrive à jour
dès le rechargement, sans bump nécessaire.

---

## 💻 Tester en local

```bash
npx http-server -p 8080 .
```
Puis ouvre `http://localhost:8080`.
Le double-clic sur `index.html` marche aussi, mais **sans** le hors-ligne :
un service worker exige `http://localhost` ou `https://`.

### Tester la partie privée à deux navigateurs

Il faut **deux fenêtres séparées, toutes deux visibles** — pas deux onglets d'une même fenêtre :
un onglet caché a son `requestAnimationFrame` suspendu par le navigateur, ce qui fausse tout.

1. Sers le jeu (commande ci-dessus) et ouvre `http://localhost:8080` dans **deux fenêtres**,
   côte à côte. Mets un pseudo différent dans chacune.
2. Fenêtre A : **🌐 Partie Privée** → **Créer un salon**. Un code de 5 caractères s'affiche.
3. Fenêtre B : **🌐 Partie Privée** → **Rejoindre**, saisis le code. Les deux pseudos doivent
   apparaître dans la liste des deux côtés, avec 👑 sur l'hôte.
4. Fenêtre A : **▶ Lancer**. Les deux passent en jeu dans la même arène.

Ce qu'il faut vérifier :

| Test | Attendu |
|---|---|
| Bouger la souris dans B | Le serpent de B suit **sans latence perceptible** ; A le voit bouger |
| Regarder le classement dans B | Top 3 et rang **globaux**, y compris des serpents que B ne voit pas |
| Regarder la minimap dans B | Tous les serpents du monde, pas seulement les voisins |
| Pause dans B | Message ⚠ « Toi seul es en pause » · le serpent de B **continue de bouger** chez A |
| Se faire manger dans B | Bannière avec **Continuer** / **Quitter** · les deux gardent l'XP |
| Réduire la fenêtre de A | La partie **continue** dans B (c'est le rôle du Worker de secours) |
| Fermer la fenêtre de A | B revient au menu avec « L'hôte a quitté la partie » et **garde son XP** |
| Rejoindre pendant la partie | Le retardataire apparaît aussitôt, dans le monde **déjà en cours** |

Une troisième fenêtre permet de vérifier que les joueurs déjà en partie voient bien arriver le
retardataire, sous son pseudo.

---

## 🧪 Ce qui a été vérifié

Testé automatiquement dans Chromium (ordinateur 1100×700 et iPhone 390×844 en 3×) :

- **60 fps** tenus avec 45 serpents et ~700 pastilles, sur les deux formats
- **Caméra** : suit le joueur, se bloque exactement aux murs du monde, dézoom 1 → 0,59 quand on grossit
- **Visée** : le pointeur est converti en coordonnées monde, donc juste même quand la caméra est bloquée au bord
- **Boucle sans fin** : 100 s simulées, 7 morts du joueur, l'état de jeu ne quitte jamais
  `PLAYING`/`SPECTATING` (pas d'écran de fin) — le monde, les bots et la nourriture restent les
  mêmes d'une vie à l'autre, seul le serpent du joueur est recréé
- **Découpe corps-à-corps** : la cible survit, raccourcie exactement de ce qui a été amputé,
  l'attaquant ne grandit pas instantanément ; les pastilles générées ont une valeur totale égale
  à l'amputation (conservation vérifiée à l'exact) et un rayon qui grandit avec leur valeur ;
  toucher la **tête**, elle, détruit toujours entièrement (croissance instantanée inchangée) ;
  mur testé à l'approche verticale, diagonale et en bout de corps, sans traversée sur 300 pas
- **Effets de kills** : fumée, éclair et flamme émanent bien de points tirés sur toute la longueur
  du corps (vérifié : la dispersion des points dessinés couvre toute la longueur, pas seulement
  la tête), zéro erreur avec les trois effets actifs simultanément sur 46 serpents
- Pause qui **fige réellement** l'horloge de jeu **en solo** (nourriture, combo ×2, les 3 bonus),
  et qui **ne fige rien** en partie privée : le serpent passe sous IA et reste mangeable (vérifié
  — mangé par un bot pendant la pause). Kill + réapparition, sauvegarde persistée, **rechargement
  hors-ligne**, zéro erreur console
- **Partie privée**, vérifiée à deux et trois navigateurs : même monde chez tous (dimensions,
  nombre et positions des pastilles), cap d'un joueur appliqué chez l'hôte, cycle complet
  mort → spectateur → XP → réapparition, arrivée en cours de partie sur une partie déjà vieille de
  10 s, et perte de l'hôte encaissée comme une mort
- **Les 6 langues sont complètes**, par un contrôle rejouable et saboté :
  `node "Snake'on/verifie-traductions.js"`
- **Partie privée dans un vrai Chrome**, deux fenêtres visibles, sans rien piloter à la main :
  horloges synchronisées (+5016 ms côté hôte, +5017 ms côté client sur 5013 ms réels), **16 ms**
  de latence médiane entre le geste d'un joueur et son application chez l'hôte, **3,2 ko/s** reçus
  par client (≈29 ko/s en montée extrapolés à 9 joueurs, ce qui confirme la mesure théorique),
  zéro erreur console. La saccade résiduelle d'un serpent distant est **identique en solo**
  (42 images sans mouvement sur 60, à 200 fps) : elle vient du pas de simulation fixe à 60 Hz,
  pas du réseau.
- **Pop-up de bienvenue** : affichée une seule fois à la toute première partie, jamais aux
  suivantes (vérifié sur une sauvegarde vidée puis rejouée)
- **Quitter (Pause → 🏳, ou bannière spectateur)** : confirmation obligatoire côté Pause, et les
  deux sorties comptent la vie — mesuré : hors du top 1 l'XP est celui d'une mort, en tête il est
  majoré du bonus de victoire (×1,5), avec dans les deux cas +1 partie et +1 entrée d'historique
- **Réglages** : les interrupteurs Musique/Effets et le choix de qualité graphique se
  sauvegardent et survivent à un rechargement ; couper les effets coupe bien tous les sons
  (vérifié sur `AudioManager.play()`) ; les trois niveaux de qualité (résolution, budget de
  particules, halos lumineux, grille de fond) tournent sans erreur sur 60 s simulées chacun

Le jeu tourne à **pas de simulation fixe (60 Hz)** : même vitesse sur un écran 60, 90 ou 120 Hz.
