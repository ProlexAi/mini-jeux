# 🐍 Neon Snake.io Ultimate

Arène survivor-like néon dans un **grand monde qui défile** : mange, grossis, dévore les serpents
plus petits que toi. **100 % HTML/JS/CSS**, aucune dépendance, aucun build, aucun serveur.
Installable comme une vraie appli (**PWA**) et **jouable hors-ligne**.

▶️ **Jouer : https://prolexai.github.io/mini-jeux/neon-snake/**
*(ce jeu fait partie du dépôt [mini-jeux](../README.md), qui en regroupe plusieurs)*

---

## 🎮 Comment on joue

| Support | Contrôle |
|---|---|
| Mobile / tablette | Le serpent suit ton **doigt** |
| Ordinateur | Le serpent suit la **souris** |
| Clavier | `Échap` ou `P` = pause · `Entrée` / `Espace` = jouer |

**But :** dépasser la taille 300 **et** être le plus gros de l'arène — face à 45 adversaires.
Tête contre tête, le plus gros mange le plus petit (il faut être ~10 % plus gros).
Tu es **invincible 3 secondes** à l'apparition, le temps de te placer.

**Bonus :** ⚡ Vitesse (×1,8) · 🧲 Aimant (attire la nourriture) · 🛡️ Invincible.
**Progression :** XP, niveaux, 10 skins à débloquer, 10 succès, historique des 10 dernières parties.
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
| Ordinateur 1100×700 | 4400 × 2800 | 684 | ~1,9 |
| iPhone 390×844 (plein écran) | 1987 × 2650 | 293 | ~1,8 |

La **minimap** en bas à droite montre le monde entier, ta position, celle des 45 serpents,
et le rectangle blanc = la portion que tu vois réellement.
Le **mur cyan** marque le bord du monde.

---

## 🚀 Mettre le jeu en ligne (GitHub Pages)

L'activation de GitHub Pages se fait une seule fois, au niveau du dépôt `mini-jeux` — voir le
[README racine](../README.md#mettre-le-portail-en-ligne-github-pages). Une fois activée, ce jeu
est automatiquement servi sur `https://prolexai.github.io/mini-jeux/neon-snake/`.

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
| `FOOD_GROWTH: 2` | taille gagnée par pastille — **c'est LE bouton qui fixe la durée d'une partie** |
| `WIN_THRESHOLD: 300` | taille à atteindre pour gagner (+ être le plus gros) |
| `WORLD_SCREENS: 16` | taille du monde, en écrans de surface — monte-le pour une carte plus vaste |
| `BOT_COUNT: 45` | nombre d'adversaires (la densité de rencontres) |
| `BOT_MAX_LENGTH: 300` | plafond des bots. **Doit rester ≤ à ce que le joueur peut atteindre**, sinon « être le plus gros » devient impossible et la partie n'est plus gagnable |
| `SPAWN_SHIELD_MS: 3000` | invincibilité à l'apparition |
| `FOOD_AREA_PER_ITEM` | densité de nourriture (px² par pastille) |
| `MIN_ZOOM: 0.45` | jusqu'où on dézoome quand on devient énorme |
| `POWERUPS` / `SKINS` | durées, couleurs, niveaux de déblocage |

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
- **Durée d'une partie** mesurée sur 84 parties simulées (deux profils de jeu) :
  victoire médiane **~45 s**, 2 à 4 défaites sur 14 parties, **aucune mort avant la 5ᵉ seconde**
- Pause qui **fige réellement** l'horloge de jeu, nourriture, combo ×2, les 3 bonus, kill + réapparition,
  victoire, défaite, sauvegarde persistée, **rechargement hors-ligne**, zéro erreur console

Le jeu tourne à **pas de simulation fixe (60 Hz)** : même vitesse sur un écran 60, 90 ou 120 Hz.
