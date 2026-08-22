# 🐍 Snake'on

Arène survivor-like néon dans un **grand monde qui défile** : mange, grossis, dévore les serpents
plus petits que toi. **100 % HTML/JS/CSS**, aucune dépendance, aucun build, aucun serveur.
Installable comme une vraie appli (**PWA**) et **jouable hors-ligne**.

▶️ **Jouer : https://prolexai.github.io/mini-jeux/Snake'on/**
*(ce jeu fait partie du dépôt [mini-jeux](../README.md), qui en regroupe plusieurs)*

---

## 🎮 Comment on joue

| Support | Contrôle |
|---|---|
| Mobile / tablette | Le serpent suit ton **doigt** |
| Ordinateur | Le serpent suit la **souris** |
| Clavier | `Échap` ou `P` = pause · `Entrée` / `Espace` = jouer |

**But :** grossir le plus possible, **sans fin** — comme sur slither.io, il n'y a pas de victoire.
Face à 45 adversaires, seul un coup sur la **tête** détruit complètement un serpent (~10 % plus
gros suffit) ; toucher son **corps** ne le tue pas — ça le "coupe" : il perd la partie amputée
mais **survit**, raccourci. Le tronçon amputé devient des pastilles de nourriture, dont la taille
et le gain sont proportionnels à ce qui a été coupé. Toucher un corps plus gros ou égal agit comme
un mur. Tu es **invincible 3 secondes** à l'apparition, le temps de te placer. À la mort, la caméra suit
4 secondes le serpent qui t'a mangé, puis tu réapparais aussitôt dans la **même arène**. Une
pop-up explique tout ça en quelques secondes à la toute première partie — jamais revue ensuite.

Le bouton pause propose **🏳 Abandonner** (contour rouge, confirmation obligatoire) pour retourner
à l'accueil sans attendre la mort — l'abandon ne compte pas comme une vie (pas de XP, pas
d'entrée à l'historique), à la différence d'une mort.

**Bonus :** ⚡ Vitesse (×1,8) · 🧲 Aimant (attire la nourriture) · 🛡️ Invincible.
**Progression :** XP, niveaux, 10 skins à débloquer, 8 succès, historique des 10 dernières vies.
**Réglages :** son (musique / effets séparés), qualité graphique (Low/Medium/High), rappel des
commandes — accessibles à tout moment depuis l'onglet ⚙️ du menu. *Le jeu n'a pas de musique pour
l'instant (seulement des effets sonores) : le réglage existe et se sauvegarde, mais n'a encore
rien à couper.*
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
index.html            le jeu entier : HTML + CSS + JS + sons générés (aucune image, aucune lib)
manifest.webmanifest  carte d'identité de l'appli (nom, icônes, couleurs, plein écran)
sw.js                 service worker : met le jeu en cache pour le hors-ligne
icons/                icônes de l'appli (192, 512, maskable, Apple, favicon)
.nojekyll             dit à GitHub Pages de servir les fichiers tels quels
```

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
- Pause qui **fige réellement** l'horloge de jeu, nourriture, combo ×2, les 3 bonus, kill + réapparition,
  sauvegarde persistée, **rechargement hors-ligne**, zéro erreur console
- **Pop-up de bienvenue** : affichée une seule fois à la toute première partie, jamais aux
  suivantes (vérifié sur une sauvegarde vidée puis rejouée)
- **Abandon (Pause → 🏳)** : confirmation obligatoire (Oui repart au menu sans compter la vie —
  ni XP ni historique —, Non revient à la pause normale), testé aussi après une reprise
- **Réglages** : les interrupteurs Musique/Effets et le choix de qualité graphique se
  sauvegardent et survivent à un rechargement ; couper les effets coupe bien tous les sons
  (vérifié sur `AudioManager.play()`) ; les trois niveaux de qualité (résolution, budget de
  particules, halos lumineux, grille de fond) tournent sans erreur sur 60 s simulées chacun

Le jeu tourne à **pas de simulation fixe (60 Hz)** : même vitesse sur un écran 60, 90 ou 120 Hz.
