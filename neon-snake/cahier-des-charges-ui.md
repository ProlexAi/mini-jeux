# Cahier des charges — UI de Neon Snake.io Ultimate

**Portée : UI uniquement.** Ce document définit les interfaces du jeu, leur rôle, leur contenu
et leurs actions — pas d'implémentation, pas de code. Il part de l'état actuel du jeu (audité le
22/08/2026) comme socle, propose un langage commun, et liste les incohérences et décisions encore
ouvertes pour qu'on les tranche ensemble.

---

## 1. Vue d'ensemble

Quatre états d'écran, un seul actif à la fois côté superposition plein cadre (Accueil / Pause) ;
le HUD et les notifications restent visibles au-dessus du jeu sans jamais le bloquer.

```
Accueil ──[Jouer]──> En jeu ──[bouton Pause]──> Pause ──[Reprendre]──> En jeu
                        │                          │
                    [mort]                     [Menu] 
                        │                          │
                        v                          v
                   Spectateur ──[4s ou "Passer"]──> En jeu (nouvelle vie)   Accueil
```

- **Accueil → En jeu → (Pause) → En jeu → (Spectateur) → En jeu → … → Menu → Accueil**
- Il n'y a pas de fin de partie : la boucle Jeu/Spectateur peut se répéter indéfiniment. Seul le
  bouton **Menu** (accessible depuis Pause) ramène à l'Accueil.

---

## 2. Langage visuel commun

### Couleurs — rôle sémantique

| Couleur | Rôle voulu | Usage actuel |
|---|---|---|
| 🟦 Cyan (accent) | Action positive, progression, identité du joueur | Boutons principaux, titres, XP, classement — cohérent |
| 🟨 Jaune (warning) | Récompense / accomplissement | XP, succès débloqué, combo — **mais aussi utilisé pour un bouton d'action neutre ("Menu"), voir §4** |
| 🟥 Rouge (danger) | Alerte / rupture / action destructrice | **Défini mais jamais utilisé dans l'interface** |
| 🟪 Violet | Décoratif | **Défini mais jamais utilisé dans l'interface** (seulement côté configuration du jeu : bonus aimant, un skin) |

### Tailles tactiles
Cible minimale **44×44px** sur tout élément interactif — déjà appliqué au bouton pause et aux
onglets du menu, à respecter pour tout nouvel élément (mobile = plateforme prioritaire).

### Comportement bloquant / non-bloquant
- **Bloquant** (occupe tout l'écran, coupe la vue du jeu) : Accueil, Pause.
- **Non-bloquant** (superposé au jeu, qui continue de tourner derrière) : HUD, classement,
  minimap, bouton pause, kill streak, bannière spectateur, toasts.

### Terminologie
Le reste de l'interface est en français ; **« Kills »** est le seul terme resté en anglais (HUD,
Stats, Succès) — à trancher (§5).

---

## 3. Inventaire des interfaces

### A. Écrans plein cadre (bloquants)

#### Accueil (écran de démarrage)
- **Rôle :** point d'entrée unique, hub de progression entre deux vies.
- **Contenu :** titre du jeu, niveau + barre XP, 4 onglets, bouton Jouer, bouton d'installation
  (PWA, conditionnel), indicateur hors-ligne.
- **Actions :** Jouer (démarre une partie), changer d'onglet, installer l'appli.

Quatre onglets à l'intérieur de l'Accueil :

| Onglet | Rôle | Contenu |
|---|---|---|
| 🎨 Skins | Personnalisation de l'apparence | Grille de couleurs, verrouillées/déverrouillées selon le niveau |
| 📊 Stats | Progression cumulée, toutes vies confondues | Record, kills total, parties jouées, temps total |
| 📜 Historique | Les 10 dernières vies | # / taille / kills / durée |
| 🏅 Succès | Objectifs de jeu (8) | Icône, nom, description, verrouillé/déverrouillé |

#### Pause
- **Rôle :** interrompre temporairement sans perdre la vie en cours.
- **Contenu :** titre, message ("la partie reprend où tu l'as laissée").
- **Actions :** Reprendre (retour au jeu), Menu (retour à l'Accueil — **abandonne silencieusement
  la vie en cours, voir §5**).

### B. HUD & superpositions non-bloquantes (visibles pendant une vie)

| Élément | Position | Rôle | Contenu |
|---|---|---|---|
| HUD principal | Haut-gauche | État vital de la vie en cours | Taille, temps, kills, bonus actifs, combo |
| Classement | Haut-droite | Situer le joueur dans l'arène | Top 3 (médaille+nom+taille), rang du joueur si hors top 3 |
| Minimap | Bas-droite | Vue d'ensemble du monde | Contour du monde, tous les serpents, zone visible à l'écran |
| Bouton pause | Bas-gauche | Accès à l'écran Pause | — |
| Kill streak | Centre, transitoire (1,5s) | Célébrer un enchaînement de kills | "DOUBLE KILL !", etc. |

### C. Notifications transitoires

| Élément | Position | Rôle | Déclencheur / durée |
|---|---|---|---|
| Bannière spectateur | Haut-centre | Accompagner la mort, montrer le tueur | Mort du joueur → 4s ou clic sur "Voir mes résultats" |
| Toasts | Bas-centre | Notifications empilables | Succès débloqué, bonus ramassé, combo activé, résumé de fin de vie — chacun ~3s |

---

## 4. Incohérences relevées

Pas des bugs — des choix faits au fil des ajouts, jamais unifiés.

1. **`.btn-secondary` utilise le jaune "récompense"** pour une action neutre (quitter la partie) —
   collision avec les usages du jaune ailleurs (succès, XP, combo).
2. **Le rouge (danger) n'est jamais utilisé** dans l'interface actuelle, alors qu'aucune action
   n'a de couleur "attention / destructeur" — pas même quitter la partie en pause.
3. **Le violet n'existe que côté configuration du jeu**, jamais dans l'interface elle-même.
4. **Quitter au Menu depuis Pause abandonne silencieusement la vie en cours** : pas de XP, pas
   d'entrée dans l'historique. Seule la mort "compte" une vie. Aucune confirmation, aucun signal.
5. **Aucun réglage audio accessible** depuis l'interface — le son peut être coupé côté moteur du
   jeu, mais rien dans l'UI ne le permet.
6. **Aucune aide en jeu.** Le "comment on joue" n'existe que dans le README du dépôt, jamais
   montré dans le jeu — pertinent pour un nouveau joueur, surtout sur mobile où les contrôles
   tactiles ne sont pas évidents au premier lancement.

---

## 5. Points ouverts à trancher ensemble

- Faut-il un écran/panneau **Réglages** (son, plus tard peut-être qualité graphique) ?
- Faut-il un **onboarding court** au tout premier lancement (contrôles, but du jeu) ?
- Que doit devenir **"Menu" depuis Pause** : garder l'abandon silencieux, ou le traiter comme une
  mort (banque la vie, éventuellement avec confirmation type "Abandonner ?") ?
- **"Kills"** : franciser (ex. "Victimes") ou assumer l'anglicisme, courant dans le genre ?
- Faut-il **redéfinir formellement le rôle des couleurs** (proposition du §2) et l'appliquer
  partout, y compris aux futurs écrans ?
- Ce cahier des charges doit-il aussi servir de **socle pour les futurs mini-jeux** du dépôt
  `mini-jeux`, ou rester propre à Neon Snake ?

---

*Prochaine étape suggérée : trancher les points du §5 un par un, puis ce document devient la
référence pour tout nouvel écran ou composant d'interface ajouté au jeu.*
