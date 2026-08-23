# Cahier des charges — UI de Snake'on

**Portée : UI uniquement.** Ce document définit les interfaces du jeu, leur rôle, leur contenu
et leurs actions — pas d'implémentation, pas de code. Version 0.6 : ajoute la **partie privée**
(écran de Salon, bouton `A06`, pause qui ne fige plus le monde des autres) et **renverse la
punition de l'abandon** — quitter une partie compte désormais la vie en cours, où qu'on parte
(§5.23). Les V0.3 à V0.5 (éclat néon, skins, auras) restent décrites telles quelles ; le §7
consigne les arbitrages de la V0.3 et le §8 ce qui reste ouvert.

---

## 1. Vue d'ensemble

```
Accueil ──[Jouer, 1ère partie]──> Pop-up de bienvenue ──> En jeu
Accueil ──[Jouer, parties suivantes]──────────────────────> En jeu

En jeu ──[bouton Pause]──> Pause ──[Reprendre]──> En jeu
Pause ──[🏳 Quitter la partie, confirmé]──> Accueil

En jeu ──[mort]──> Spectateur ──[4s ou "Continuer"]──> En jeu (nouvelle vie, même arène)
Spectateur ──["Quitter"]──> Accueil
```

Il n'y a pas de fin de partie : la boucle En jeu ⇄ Spectateur peut se répéter indéfiniment. Deux
sorties ramènent à l'Accueil : **Quitter la partie** (depuis Pause) et **Quitter** (depuis la
bannière spectateur). **Les deux comptent la vie en cours** — voir §5.23. La pop-up de bienvenue n'apparaît qu'une seule
fois, à la toute première partie du joueur. **Réglages** est accessible de façon identique depuis
l'Accueil et depuis Pause (v0.3) — ce n'est plus réservé à l'Accueil.

---

## 2. Langage visuel commun

### Couleurs — révisé en v0.3 (remplace la table de la V0.2)

Huit teintes au choix du joueur ; toute l'interface suit — bordures, onglets, hachures, titre,
éclat de clic. **Une seule exception, fixe, qui ne suit jamais le choix du joueur : Quitter la
partie, toujours rouge, encadré de deux ⚠.** Le rouge y signale l'**irréversibilité** — on ne
revient pas dans la même arène — et non une punition : la vie quittée est comptée normalement.

| Teinte | Hex | Statut |
|---|---|---|
| 🟦 Cyan | `#00ffcc` | Par défaut à l'installation |
| 🟩 Vert | `#39ff88` | Au choix |
| 🟢 Citron | `#d8ff3c` | Au choix |
| 🟧 Ambre | `#ffb020` | Au choix |
| 🟠 Corail | `#ff7a4d` | Au choix |
| 🟪 Rose | `#ff4d9d` | Au choix |
| 🟣 Violet | `#b06bff` | Au choix |
| 🔵 Bleu | `#3ba9ff` | Au choix |
| 🟥 Rouge | `#ff5c8a` | **Fixe — sorties irréversibles uniquement, jamais choisissable** |

Ce que ça change par rapport à la V0.2 (tranchée en §5.5) : le **jaune n'a plus de rôle réservé** —
Pause suivait le jaune, elle suit maintenant la couleur choisie comme le reste. Le **violet**
n'est plus "décoratif hors interface" : c'est une des huit teintes sélectionnables. Le **rouge**
garde exactement son rôle de v0.2 (seule action destructrice) mais devient la seule couleur qui
échappe totalement au choix du joueur.

### Skins du serpent *(nouveau, v0.4)*

Un skin change l'apparence physique du serpent en jeu — trait du corps et forme de la tête —
jamais sa couleur d'interface (indépendante, voir ci-dessus), jamais sa hitbox. Le trait "cœur"
du corps garde sur tous les skins sa largeur et son opacité pleines, et peut porter une texture
contenue sous 1 r : c'est la silhouette, non l'aplat, qui est le repère de lisibilité permettant
de juger en un coup d'œil qui est plus gros. Une texture qui déborderait recouvrirait le liseré
de menace, et c'est cela seul qui est proscrit. Un skin animé a toujours une
version figée sous `prefers-reduced-motion`. Les bots ne portent jamais de skin.

**Auras élémentaires (v0.5).** Un skin peut porter une *aura* : une silhouette vivante qui
épouse le contour du serpent et **déborde franchement de ses bords**. La lisibilité n'est alors
plus garantie par la distance mais par l'**ordre de dessin** — l'aura passe sous le cœur, tracé
par-dessus à opacité pleine, et une seule passe repasse devant lui, plafonnée à 0,25 d'alpha.
Le débordement est borné à 2,2 fois le rayon. L'aura est une composante permanente : seule sa
déformation s'anime, elle demeure donc sous `prefers-reduced-motion`.

### Typographie *(nouveau, v0.3)*

- **Titres et libellés HUD** : police **Tektur**, contre-inclinée de 8°.
- **Texte courant** : police **Rajdhani**.
- Le titre `SNAKE'ON` ajoute deux tranches décalées et un clignotement néon fatigué.
- `prefers-reduced-motion` fige toutes ces animations (contre-inclinaison, clignotement, éclat de
  clic) — accessibilité non négociable.

### L'éclat néon au clic *(nouveau, v0.3 — comportement transverse, pas un écran)*

Une bille de lumière jetée sous le doigt/curseur, qui éclate au point de contact. Se déclenche
sur **chaque interaction dans les menus** (Accueil, Réglages, Pause…) — **jamais pendant une
vie** : HUD, classement, bouton pause et toasts restent nets en jeu, aucun éclat ne s'y déclenche.

Anatomie (séquence, ≤ 600 ms au total) :

| Phase | Durée | Effet |
|---|---|---|
| Vol | 110 ms | la bille arrive du haut-gauche vers le point de contact |
| Cœur | 150 ms | flash blanc, 4 → 30 px |
| Anneau | 260 ms | anneau, 6 → 62 px |
| Éclats | 430 ms | 14 traînées qui se dispersent |

Prend la couleur d'interface choisie ; toujours rouge sur Quitter la partie. Son **intensité** est
réglable — voir "Effets" dans Réglages ci-dessous.

### Tailles tactiles
Cible minimale **44×44px** sur tout élément interactif — mobile est la plateforme prioritaire.

### Comportement bloquant / non-bloquant
- **Bloquant** (occupe tout l'écran) : Accueil, Pause, Réglages, Pop-up de bienvenue.
- **Non-bloquant** (superposé au jeu qui continue de tourner) : HUD, classement, minimap, bouton
  pause, kill streak, bannière spectateur, toasts.

### Terminologie
Français partout, sauf **« Kills »**, conservé tel quel (tranché, §5.4).

---

## 3. Inventaire des interfaces

### A. Écrans plein cadre (bloquants)

#### Accueil (écran de démarrage) — *style révisé en v0.3*
- **Rôle :** point d'entrée unique, hub de progression entre deux vies.
- **Contenu :** titre du jeu (voir Typographie), niveau + XP (`LVL 07 · 2140/3000`), 5 entrées de
  navigation en **barres HUD codées** (`A01`…`A06`, pas des onglets pilules), bouton Jouer, bouton
  d'installation (PWA, conditionnel), indicateur hors-ligne.
- **Actions :** Jouer, ouvrir une entrée, installer l'appli.

| Entrée | Code | Rôle | Contenu |
|---|---|---|---|
| 🛒 Boutique | A01 | Personnalisation de l'apparence | Trois catégories indépendantes — couleurs, formes, effets — verrouillées selon le niveau |
| 📊 Stats | A02 | Progression cumulée, toutes vies confondues | Record, kills total, parties jouées, temps total |
| 📜 Historique | A03 | Les 10 dernières vies | # / taille / kills / durée |
| 🏅 Succès | A04 | Objectifs de jeu (8) | Icône, nom, description, verrouillé/déverrouillé |
| ⚙️ Réglages | A05 | Confort de jeu | Voir ci-dessous |

Une **variante paysage mobile** (844×390) existe pour l'Accueil, Réglages et Pause — layouts
adaptés en largeur plutôt qu'en hauteur, même contenu.

#### ⚙️ Réglages — *contenu révisé en v0.3*
- **Rôle :** régler le confort de jeu et retrouver les commandes, **à tout moment** — accessible
  identiquement depuis l'Accueil et depuis Pause (pas juste au premier lancement).
- **Contenu :**
  - **Audio** — deux curseurs numériques indépendants : **Musique** et **Sons** (0–100 chacun,
    pas de simple ON/OFF)
  - **Effets** — sélecteur à 3 choix, pas une jauge : **Aucun** (flash seul) · **Léger** (anneau +
    moitié) · **Complet** (bille lancée) — règle l'intensité de l'éclat de clic (§2)
  - **Qualité graphique** — résolution de rendu en pixels : **1280×720** (économe) ·
    **1600×900** (équilibré) · **1920×1080** (natif)
  - **Langue** — ouvre une sous-page listant 6 langues, chacune nommée dans sa propre langue
    *(nouvelle fonctionnalité, voir §7 — le jeu est aujourd'hui français uniquement)*
  - **Couleur de l'interface** — les 8 teintes du §2
  - **Commandes** — rappel permanent des gestes tactiles et touches clavier
- **Actions :** ajuster chaque réglage (effet immédiat, pas de bouton "valider").

#### Pop-up de bienvenue
- **Rôle :** expliquer le but du jeu en quelques secondes, une seule fois — jamais revue ensuite.
- **Déclencheur :** automatique, seulement à la toute première partie du joueur.
- **Contenu :** but du jeu, brièvement — pas un tutoriel pas-à-pas, pas de commentaires.
- **Actions :** fermer / commencer à jouer.

#### Pause — *révisé en v0.3*
- **Rôle :** interrompre temporairement sans perdre la vie en cours.
- **Contenu :** titre `PAUSE` avec sous-titre stylé `SYS//HALT`, Réglages accessible **directement
  depuis cet écran** avec un aperçu vivant (puces Effets, curseur Musique visibles inline), icône
  **🏳 Quitter la partie** (A00) en bas, encadrée de deux ⚠, contour rouge fixe.
- **Actions :**
  - **Reprendre** : retour immédiat au jeu.
  - **Réglages** : ouvre le même panneau qu'à l'Accueil.
  - **🏳 Quitter la partie** : ouvre une confirmation ("Quitter la partie ?" Oui/Non) avant de
    revenir à l'Accueil. En tête du classement, le libellé devient **Terminer la partie** et le
    bouton quitte le rouge pour la couleur d'interface (les ⚠ deviennent des 🏆).

  **Quitter compte la vie en cours** exactement comme une mort — XP, stats et entrée à
  l'historique (§5.23) ; en tête, l'XP est majoré du bonus de victoire. Pause suit maintenant la
  couleur d'interface choisie comme le reste de l'UI (v0.2 la réservait au jaune — révisé, §2).

#### 🌐 Salon (partie privée) — *nouveau*
- **Rôle :** créer ou rejoindre une partie privée par code, avant de jouer.
- **Contenu :** code de partie (généré ou saisi), liste des joueurs présents, badge hôte,
  bouton **Lancer** (hôte uniquement).
- **Actions :** créer un salon, rejoindre par code, lancer la partie, quitter le salon.
- Accessible depuis l'Accueil via le bouton **Partie Privée** (code `A06`), même hachure de
  bord droit, même cible tactile 44×44 px que le reste des CTA.

### B. HUD & superpositions non-bloquantes (visibles pendant une vie)

| Élément | Position | Rôle | Contenu |
|---|---|---|---|
| HUD principal | Haut-gauche | État vital de la vie en cours | Taille, temps, kills, bonus actifs, combo |
| Classement | Haut-droite | Situer le joueur dans l'arène | Top 3 (médaille+nom+taille), rang du joueur si hors top 3 |
| Minimap | Bas-droite | Vue d'ensemble du monde | Contour du monde, tous les serpents, zone visible à l'écran |
| Bouton pause | Bas-gauche | Accès à l'écran Pause | — |
| Kill streak | Centre, transitoire (1,5s) | Célébrer un enchaînement de kills | "DOUBLE KILL !", etc. |

**Aucun éclat de clic ici** (§2) : le HUD reste net pendant une vie, par design.

### C. Notifications transitoires

| Élément | Position | Rôle | Déclencheur / durée |
|---|---|---|---|
| Bannière spectateur | Haut-centre | Accompagner la mort, montrer le tueur, offrir la sortie | Mort du joueur → **Continuer** (défaut au bout de 4s) ou **Quitter** (rouge) |
| Toasts | Bas-centre | Notifications empilables | Succès débloqué, bonus ramassé, combo activé, résumé de fin de vie — chacun ~3s |

---

## 4. Historique — incohérences relevées en V0.1

Pour mémoire, ce qui a motivé les décisions du §5 (toutes résolues) :

1. Le bouton "Menu" de Pause utilisait le jaune "récompense" pour une action neutre.
2. Le rouge n'était jamais utilisé dans l'interface.
3. Le violet n'existait que côté configuration du jeu, jamais dans l'UI.
4. Quitter au Menu depuis Pause abandonnait silencieusement la vie en cours, sans confirmation.
5. Aucun réglage audio n'était accessible depuis l'interface.
6. Aucune aide en jeu : le "comment on joue" n'existait que dans le README du dépôt.

---

## 5. Décisions actées

### V0.2
1. **Écran Réglages : oui.** Contenu révisé en v0.3, voir §3.
2. **Onboarding : oui, minimal.** Une pop-up unique à la toute première partie, sans tutoriel
   pas-à-pas. Le détail des commandes vit dans Réglages, pas dans la pop-up.
3. **"Menu" de Pause : devient une sortie confirmée.** Icône drapeau, contour rouge fixe,
   confirmation obligatoire avant de quitter. *Libellé et comptabilité révisés en v0.4 — voir
   §5.23 : "Abandonner" devient "Quitter la partie", et la vie en cours est désormais comptée.*
4. **"Kills" : conservé tel quel.** Pas de francisation.
5. **Couleurs : rôle clarifié.** Révisé en v0.3, voir §2 — le principe (une couleur, un rôle net)
   reste le même, la table change.
6. **Portée du document : confirmée propre à Snake'on.** Sa structure pourra servir de gabarit
   aux futurs mini-jeux du dépôt `mini-jeux` ; le contenu de chacun sera spécifique.

### V0.3 — addendum "L'éclat néon au clic"
7. **Couleur d'interface personnalisable : oui.** 8 teintes, cyan par défaut, propagée à toute
   l'UI. Seule exception fixe : la sortie irréversible reste rouge, encadrée de deux ⚠. Jaune et violet
   perdent leur statut spécial de la v0.2 (voir §2).
8. **Éclat néon au clic : oui, dans les menus uniquement.** Jamais pendant une vie — HUD,
   classement, bouton pause et toasts restent nets. Anatomie et durée fixées en §2.
9. **Réglage Effets (intensité de l'éclat) : oui.** Sélecteur à 3 niveaux (Aucun/Léger/Complet),
   distinct de la Qualité graphique.
10. **Qualité graphique : redéfinie en résolution de rendu** (1280×720 / 1600×900 / 1920×1080)
    plutôt qu'en niveaux abstraits Low/Medium/High.
11. **Audio : deux curseurs numériques** (Musique, Sons, 0–100) plutôt que deux interrupteurs
    ON/OFF.
12. **Réglages accessible depuis Pause, pas seulement l'Accueil.**
13. **Typographie fixée :** Tektur (titres/HUD, contre-inclinée 8°) + Rajdhani (texte courant),
    `prefers-reduced-motion` respecté.
14. **Langue du jeu personnalisable : posé en principe**, 6 langues prévues — liste et périmètre
    exact à trancher, voir §7.

### V0.4 — addendum "Skins qui changent le serpent"
15. **Skin = trait du corps + tête, jamais une couleur seule.** 10 skins, mêmes paliers de
    déblocage qu'avant. Silhouette et opacité du trait cœur non négociables (lisibilité).
16. **Indépendant de la couleur d'interface.** Les deux systèmes restent étanches.
17. **Pas de pièces combinables.** Un skin est un tout, identifié par un id court (coût de
    réplication multijoueur futur).
18. **Bots sans skin**, gardent leurs couleurs actuelles — préserve la distinction joueur/bot.
19. **Noms de skins non traduits** (texte de jeu, français partout, cf. §7).

### V0.5 — addendum « Auras élémentaires »
20. **Une aura peut déborder de la silhouette.** Révise la décision 15 : la lisibilité est
    assurée par l'ordre de dessin et une hiérarchie d'opacité, non plus par l'absence de
    recouvrement.
21. **Débordement borné à 2,2 r** et passe avant-plan plafonnée à 0,25 d'alpha. Ce que le
    plafond protège est la lecture de la taille, et celle-ci est assurée par le liseré tracé
    sur le bord du corps, non par l'étroitesse de l'aura.
22. **Trois auras** : Flamme Ardente (25), Orage (30), Volutes (35).

### V0.6 — partie privée
23. **Quitter ne coûte plus rien. Renverse le §5.3.** Toute sortie compte la vie en cours —
    XP, stats, entrée à l'historique — qu'on parte depuis Pause ou depuis la bannière spectateur.
    En tête du classement, l'XP reste majoré du bonus de victoire.
    *Motif :* une partie brève commencée en attendant quelqu'un devait pouvoir s'interrompre
    quand cette personne arrive. Punir ce départ effaçait une partie réellement jouée, alors que
    le joueur n'avait rien à se reprocher. La punition n'apportait rien : le jeu n'a pas de fin,
    donc rien à protéger d'une sortie anticipée.
    *Conséquences :* « ABANDONNER » devient « **QUITTER LA PARTIE** » (le mot portait la
    punition qu'on retire) ; la confirmation dit désormais ce qu'on garde au lieu de ce qu'on
    perd ; le rouge et les deux ⚠ **restent**, mais signalent l'irréversibilité — on ne revient
    pas dans la même arène — et non une sanction.
24. **Bannière spectateur : deux issues.** « **Continuer** » (défaut au bout de 4 s, comme avant)
    et « **Quitter** » (rouge). Les deux encaissent la vie identiquement ; seule diffère la
    destination — nouvelle vie dans la même arène, ou retour à l'Accueil.
25. **Partie privée : bouton d'Accueil `A06`**, désactivé hors ligne avec son motif affiché
    plutôt que masqué — un bouton absent ne s'explique pas.
26. **Sortie subie ≠ sortie choisie.** Perdre l'hôte ou le réseau en pleine partie encaisse la
    vie comme une mort : on ne fait pas payer au joueur une panne qu'il n'a pas causée.
27. **Un kill est une élimination complète, jamais une découpe.** Le compteur ne monte qu'en
    mangeant une **tête**. Il l'a toujours fait ; ce qui mentait, c'était le retour sensoriel —
    une découpe jouait le son de kill et les particules de mort, si bien qu'on croyait tuer sans
    voir son compteur bouger. La découpe a désormais **son propre son** (sec, bref, descendant)
    et **sa propre gerbe** de particules, dirigée le long de la coupure. Faire compter la découpe
    aurait été l'autre issue possible : elle est écartée, on « tuerait » dix fois le même serpent
    en le coupant dix fois.
28. **Quitter l'écran des yeux : cinq secondes de grâce.** En partie privée, la pause ne fige rien
    et le serpent laissé derrière passe sous IA. Le laisser ainsi sans limite reviendrait à occuper
    une place dans l'arène sans y jouer, en laissant l'IA récolter à sa place. Au-delà de cinq
    secondes, la partie s'arrête donc pour ce joueur, sa vie comptée comme une mort (§5.26). En
    solo rien ne change : la pause fige tout et peut durer, personne n'attend.
29. **Paysage mobile : deux colonnes, pas un rétrécissement.** Accueil, Pause et Salon disposent
    l'identité et les actions à gauche, la navigation et son contenu à droite — seuls ces derniers
    défilent. La cible de 44 px reste un plancher : la place se prend sur les marges et les
    interlignes, jamais sur la zone touchable.
30. **Musique : générée, comme les sons.** Aucun fichier, aucune dépendance — une boucle de seize
    secondes sur quatre accords, trois voix, sans percussion. Elle accompagne une partie qui dure,
    elle ne doit ni réclamer l'attention ni fatiguer. À zéro, le curseur ARRÊTE réellement les
    oscillateurs au lieu de jouer un silence ; un onglet caché suspend le contexte audio.

---

## 6. Pause en partie privée

En solo, Pause fige l'intégralité de la simulation. En partie privée, ce comportement ne peut
pas être conservé : la partie continue pour tout le monde.

**Décidé :** au clic sur Pause, le serpent du joueur bascule en pilotage automatique — le
profil d'IA "peureux" déjà utilisé par les bots (fuit tôt, ne chasse jamais). Un message
prévient : **« Toi seul es en pause — tu peux te faire manger pendant ce temps. »** Reprendre
rend la main immédiatement.

---

## 7. Points tranchés à l'implémentation de la V0.3

Les quatre points laissés ouverts par l'addendum sont désormais arbitrés :

- **Les 6 langues : Français, Anglais, Espagnol, Allemand, Italien, Portugais**, chacune nommée
  dans sa propre langue. **Seule l'interface se traduit** (menus, HUD, classement, Réglages,
  Pause, bannière spectateur, écran de bienvenue). Les **textes de jeu restent en français dans
  toutes les langues** : noms et descriptions des succès, toasts, kill streaks, dates de
  l'historique. « Kills » reste « Kills » partout (§5.4).
- **Qualité graphique** : les trois niveaux existants (DPR + budget de particules + halos) sont
  conservés tels quels, seuls leurs **libellés** deviennent des résolutions — 1280×720 « économe »,
  1600×900 « équilibré », 1920×1080 « natif ». Le comportement de rendu est inchangé : ce sont les
  mêmes paliers, présentés dans le langage de l'utilisateur.
- **Hachures** : bandeau vertical de 18 à 26 px collé au **bord droit** d'un élément, rempli de
  hachures diagonales fines (`repeating-linear-gradient` à 135°, trait de 2 px, pas de 6 px) à la
  couleur d'interface. Appliqué à : JOUER, INSTALLER L'APPLI, la ligne LANGUE, REPRENDRE et
  QUITTER LA PARTIE — cette dernière en rouge fixe.
- **Réglages dans Pause** : **version condensée fixe**, pas le panneau complet. Elle contient
  uniquement le sélecteur Effets, le curseur Musique et les 8 pastilles de couleur, branchés sur
  les mêmes réglages que l'Accueil. Qualité graphique, Sons, Langue et Commandes restent
  accessibles depuis l'Accueil seulement.

**Ajout hors addendum : le pseudo.** L'Accueil porte un champ de pseudo librement modifiable
(14 caractères), placé au-dessus du niveau. Il remplace le nom du joueur en jeu (HUD, classement,
bannière spectateur) ; laissé vide, le jeu retombe sur « TOI », traduit selon la langue choisie.

---

## 8. Reste à faire

- **Apparence d'un joueur distant en partie privée.** Le protocole ne transporte que sa
  **couleur** : forme et effet ne voyagent pas, si bien qu'un joueur se voit avec son skin mais
  que les autres le voient uni. Antérieur au découplage forme/effet, qui le rend seulement plus
  visible. À corriger en joignant les deux index au `HELLO` et au roster de `GAME_START` — deux
  entiers par joueur, envoyés une seule fois : l'apparence ne change pas en cours de partie, elle
  n'a donc rien à faire dans les instantanés.
- **Reconnexion réseau.** Une coupure de la liaison compte comme un départ définitif. Le retrait
  d'écran, lui, est traité (§5.28). À rouvrir si l'usage montre que les coupures brèves gênent.

## 9. Contrôles rejouables

| Ce qui est vérifié | Commande |
|---|---|
| Les 6 langues sont complètes, aucune clé morte ni orpheline | `node "Snake'on/verifie-traductions.js"` |

Ce contrôle échoue si une langue perd une clé, si le HTML cite une clé inexistante, ou si une clé
n'est plus utilisée nulle part. Il a été saboté dans les trois sens pour vérifier qu'il sait
encore échouer.

---

*Ce document est la référence pour tout nouvel écran ou composant d'interface ajouté au jeu.
La V0.6 est implémentée, à l'exception des points listés au §8.*
