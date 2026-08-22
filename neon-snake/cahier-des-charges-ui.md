# Cahier des charges — UI de Neon Snake.io Ultimate

**Portée : UI uniquement.** Ce document définit les interfaces du jeu, leur rôle, leur contenu
et leurs actions — pas d'implémentation, pas de code. Version 2 : les 6 points ouverts de la V1
sont tranchés (§5), deux nouvelles interfaces sont ajoutées (Réglages, Pop-up de bienvenue), et
la contrainte du futur multijoueur est posée par écrit (§6).

---

## 1. Vue d'ensemble

```
Accueil ──[Jouer, 1ère partie]──> Pop-up de bienvenue ──> En jeu
Accueil ──[Jouer, parties suivantes]──────────────────────> En jeu

En jeu ──[bouton Pause]──> Pause ──[Reprendre]──> En jeu
Pause ──[🏳 Abandonner, confirmé]──> Accueil

En jeu ──[mort]──> Spectateur ──[4s ou "Passer"]──> En jeu (nouvelle vie, même arène)
```

Il n'y a pas de fin de partie : la boucle En jeu ⇄ Spectateur peut se répéter indéfiniment. Seul
**Abandonner** (depuis Pause) ramène à l'Accueil. La pop-up de bienvenue n'apparaît qu'une seule
fois, à la toute première partie du joueur.

---

## 2. Langage visuel commun

### Couleurs — rôle sémantique (tranché, §5.5)

| Couleur | Rôle | Où |
|---|---|---|
| 🟦 Cyan (accent) | Action principale, progression, identité du joueur | Boutons principaux, titres, XP, classement |
| 🟨 Jaune (warning) | Récompense / accomplissement / Pause | XP, succès débloqué, combo, écran Pause |
| 🟥 Rouge (danger) | La seule action destructrice de l'interface | Contour de l'icône **Abandonner** |
| 🟪 Violet | Décoratif, hors interface | Reste côté configuration du jeu (bonus aimant, un skin) — aucun rôle UI, et ce n'est pas un manque |

### Tailles tactiles
Cible minimale **44×44px** sur tout élément interactif — mobile est la plateforme prioritaire.

### Comportement bloquant / non-bloquant
- **Bloquant** (occupe tout l'écran) : Accueil, Pause, Réglages, Pop-up de bienvenue.
- **Non-bloquant** (superposé au jeu qui continue de tourner) : HUD, classement, minimap, bouton
  pause, kill streak, bannière spectateur, toasts.

### Terminologie
Français partout, sauf **« Kills »**, conservé tel quel (tranché, §5.4). La qualité graphique
peut elle aussi utiliser des libellés anglais courts (**Low / Medium / High**), dans le même
esprit — un vocabulaire de jeu, pas un manque de traduction.

---

## 3. Inventaire des interfaces

### A. Écrans plein cadre (bloquants)

#### Accueil (écran de démarrage)
- **Rôle :** point d'entrée unique, hub de progression entre deux vies.
- **Contenu :** titre du jeu, niveau + barre XP, 5 onglets (voir ci-dessous), bouton Jouer, bouton
  d'installation (PWA, conditionnel), indicateur hors-ligne.
- **Actions :** Jouer, changer d'onglet, installer l'appli.

| Onglet | Rôle | Contenu |
|---|---|---|
| 🎨 Skins | Personnalisation de l'apparence | Grille de couleurs, verrouillées selon le niveau |
| 📊 Stats | Progression cumulée, toutes vies confondues | Record, kills total, parties jouées, temps total |
| 📜 Historique | Les 10 dernières vies | # / taille / kills / durée |
| 🏅 Succès | Objectifs de jeu (8) | Icône, nom, description, verrouillé/déverrouillé |
| ⚙️ Réglages | *(nouveau, §5.1)* | Voir ci-dessous |

#### ⚙️ Réglages *(nouvelle interface)*
- **Rôle :** régler le confort de jeu (son, image) et retrouver les commandes à tout moment —
  pas seulement au premier lancement.
- **Contenu :**
  - **Audio** : Musique et Effets sonores réglés **séparément** (deux curseurs ou interrupteurs)
  - **Qualité graphique** : Low / Medium / High
  - **Commandes** : rappel permanent des gestes tactiles et touches clavier (le même contenu que
    la pop-up de bienvenue, disponible à la demande, en permanence)
- **Actions :** ajuster chaque réglage (effet immédiat, pas de bouton "valider").

#### Pop-up de bienvenue *(nouvelle interface)*
- **Rôle :** expliquer le but du jeu en quelques secondes, une seule fois — jamais revue ensuite.
- **Déclencheur :** automatique, seulement à la toute première partie du joueur.
- **Contenu :** but du jeu, brièvement — pas un tutoriel pas-à-pas, pas de commentaires. Le ton
  des pop-up d'accroche habituelles du genre.
- **Actions :** fermer / commencer à jouer.

#### Pause
- **Rôle :** interrompre temporairement sans perdre la vie en cours.
- **Contenu :** titre, message de réassurance, icône **🏳 Abandonner** en bas de l'écran (petite,
  discrète, contour rouge).
- **Actions :**
  - **Reprendre** : retour immédiat au jeu.
  - **🏳 Abandonner** : ouvre une confirmation ("Abandonner la partie ?" Oui/Non) avant de revenir
    à l'Accueil — plus aucun risque de perdre sa vie en cours par un clic accidentel (résout
    l'ancien problème d'abandon silencieux).

  *Proposition à valider :* l'abandon ne compte pas comme une vie terminée (pas de XP, pas
  d'entrée à l'historique), à la différence d'une mort — cohérent avec l'idée qu'abandonner n'est
  pas une performance. À corriger si ce n'est pas voulu.

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

## 4. Historique — incohérences relevées en V1

Pour mémoire, ce qui a motivé les décisions du §5 (toutes résolues) :

1. Le bouton "Menu" de Pause utilisait le jaune "récompense" pour une action neutre.
2. Le rouge n'était jamais utilisé dans l'interface.
3. Le violet n'existait que côté configuration du jeu, jamais dans l'UI.
4. Quitter au Menu depuis Pause abandonnait silencieusement la vie en cours, sans confirmation.
5. Aucun réglage audio n'était accessible depuis l'interface.
6. Aucune aide en jeu : le "comment on joue" n'existait que dans le README du dépôt.

---

## 5. Décisions actées

1. **Écran Réglages : oui.** Contenu détaillé en §3 (Audio séparé Musique/Effets, Qualité
   graphique Low/Medium/High, Commandes en rappel permanent).
2. **Onboarding : oui, minimal.** Une pop-up unique à la toute première partie, sans tutoriel
   pas-à-pas. Le détail des commandes vit dans Réglages, pas dans la pop-up.
3. **"Menu" de Pause : devient "Abandonner".** Icône drapeau blanc à contour rouge, en bas de
   l'écran Pause (pas d'élément permanent affiché pendant le jeu — cette option a été écartée).
   Confirmation obligatoire avant de quitter. Pour l'instant (jeu solo face à des bots), confirmer
   relance simplement une nouvelle partie, comme aujourd'hui.
4. **"Kills" : conservé tel quel.** Pas de francisation.
5. **Couleurs : clarifiées, pas de refonte.** Le jaune reste légitime pour Pause — ce n'était pas
   le vrai problème. Le rouge devient le contour de l'action Abandonner. Le violet reste
   volontairement hors interface. Voir tableau §2.
6. **Portée du document : confirmée propre à Neon Snake.** Sa structure (les sections, la
   méthode) pourra servir de gabarit pour de futurs mini-jeux du dépôt `mini-jeux`, mais le
   contenu de chaque futur cahier des charges sera spécifique à son jeu.

---

## 6. À prévoir : Pause et multijoueur futur

Aujourd'hui le jeu est **solo face à des bots** : mettre pause fige l'intégralité de la
simulation, bots compris, sans conséquence pour personne d'autre.

Si le jeu évolue vers du **multijoueur réel** (parties privées sur invitation, plusieurs amis
mélangés à des bots), ce comportement ne pourra plus être conservé tel quel : mettre pause ne
doit **jamais** figer la partie pour les autres joueurs. Deux pistes, à trancher le moment venu :

- Pause ne fige plus que l'affichage et les contrôles du joueur qui l'utilise — la partie continue
  pour tout le monde ; ou
- Si figer sa propre présence est inévitable, un message doit prévenir clairement :
  **« Toi seul es en pause — tu peux te faire manger pendant ce temps. »**

---

*Ce document est maintenant la référence pour tout nouvel écran ou composant d'interface ajouté
au jeu. Prochaine étape suggérée : passer les décisions du §5 à l'implémentation.*
