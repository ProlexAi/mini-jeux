# 🎮 Mini-jeux

Petits jeux **100 % HTML/JS/CSS**, sans dépendance, sans build, sans serveur. Chaque jeu est
installable comme une PWA et jouable hors-ligne. Un seul dépôt, un dossier par jeu.

▶️ **Portail : https://prolexai.github.io/mini-jeux/**

## Jeux

| Jeu | Lien | Dossier |
|---|---|---|
| 🐍 Neon Snake.io Ultimate | https://prolexai.github.io/mini-jeux/neon-snake/ | [`neon-snake/`](neon-snake/) |

## Ajouter un jeu

1. Créer un dossier à la racine (ex. `mon-jeu/`) avec son propre `index.html`, `manifest.webmanifest`,
   `sw.js` et `icons/` — chaque jeu est une PWA indépendante, isolée par son propre `scope`.
2. Ajouter une carte vers `mon-jeu/index.html` dans [`index.html`](index.html) (portail racine).
3. Ajouter une ligne au tableau ci-dessus.

## Mettre le portail en ligne (GitHub Pages)

1. Sur GitHub, ouvre ce dépôt → onglet **Settings**
2. Menu de gauche → **Pages**
3. **Source** : `Deploy from a branch`
4. **Branch** : `main` — dossier `/ (root)` → **Save**

Attends 1–2 minutes : le portail est en ligne sur `https://prolexai.github.io/mini-jeux/`.
Chaque `git push` sur `main` redéploie automatiquement.

> ⚠️ Le dépôt doit rester **public** pour que Pages fonctionne sans abonnement payant.

## Tester en local

```bash
npx http-server -p 8080 .
```
Puis ouvre `http://localhost:8080`. Le double-clic sur un `index.html` marche aussi, mais **sans**
le hors-ligne : un service worker exige `http://localhost` ou `https://`.
