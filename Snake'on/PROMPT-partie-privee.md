# Prompt de session — Partie privée : jouer la même partie à plusieurs, par code

> **Écrit le 22/08/2026. Document jetable :** il ouvre UNE session de conception, puis se supprime
> — comme `PASSATION.md` avant lui, périmé le jour où le jeu a dépassé ce qu'il décrivait. Il ne
> recopie aucune valeur du jeu : tout ce qui est chiffré se relit à la source. Si une phrase d'ici
> contredit le code, **c'est le code qui a raison**.

## Ce qu'on te demande

Concevoir puis livrer la **partie privée** de Snake'on : plusieurs joueurs, réunis par un code,
dans la même arène. Grosse tâche — la session commence par la **conception validée par Matt**,
l'implémentation ne démarre qu'après.

## Cadre, posé par Matt et non rediscutable

- **C'est un jeu personnel et amical.** Une partie entre proches, réunis par un code qu'on
  s'échange. **Ce n'est pas une surface de multijoueur massif** : pas de matchmaking public, pas de
  salon ouvert, pas de classement mondial, pas de modération à prévoir. Toute proposition qui pousse
  vers l'échelle publique est hors sujet — dis-le et propose l'option sobre.
- **Réseau : WebRTC pair-à-pair, l'hôte fait autorité.** Un serveur de signalisation gratuit suffit
  à mettre les pairs en relation ; il ne voit pas la partie. Conséquence assumée : l'hôte peut
  tricher, et sa déconnexion arrête la partie — c'est acceptable entre amis.
- **Aucun compte, aucune donnée hors de l'appareil.** La progression reste dans le `localStorage`
  déjà en place (`CONFIG.SAVE_KEY`). Si ta conception exige de stocker quoi que ce soit ailleurs,
  **arrête-toi et dis-le** : c'est une décision de Matt, pas la tienne.
- **Le dépôt reste une PWA statique** servie par GitHub Pages, sans build ni backend à maintenir.
- **Mort en partie privée : « Continuer / Quitter ».** Quitter n'est **pas** un abandon — le joueur
  garde son XP, ses stats et son entrée d'historique, exactement comme une mort en solo.

## Ce que le jeu fait déjà, et qu'il ne faut pas casser

Ouvre `Snake'on/index.html` et lis avant de proposer quoi que ce soit :

```bash
grep -n "function startGame\|function simulate\|function checkCollisions\|function endGame\|function respawnPlayer\|function pauseGame\|function confirmPauseExit" "Snake'on/index.html"
```

- Le monde est **recalculé à chaque partie** selon la taille de l'écran (`computeWorld`) : deux
  joueurs sur deux écrans différents n'obtiennent pas le même monde. **C'est le premier problème à
  résoudre**, avant tout le reste.
- La simulation tourne à **pas fixe** avec accumulateur (`STEP_MS`, `MAX_STEPS_PER_FRAME`) : c'est
  la bonne base pour une synchro, ne la remplace pas sans raison mesurée.
- L'horloge de jeu `gameClock` **n'avance que dans `gameLoop`**, pas dans `simulate` — piège vérifié
  le 22/08/2026 : tout test qui appelle `simulate()` en boucle sans avancer `gameClock` mesure un
  jeu dont aucun minuteur n'expire.
- Depuis le patch du 22/08/2026 : **plus aucun plafond de longueur**, la prédation compare les
  longueurs (`EAT_RATIO`), les bots ont des **profils d'IA** avec verrou de cible et quota de
  poursuivants (`CONFIG.BOT_PROFILES`, `CONFIG.BOT_MAX_HUNTERS`), et depuis Pause **le joueur en
  tête du classement peut terminer la partie** en gagnant son XP (`confirmPauseExit`).
- Le cahier des charges **§6 traite déjà la pause en multijoueur** : mettre pause ne doit jamais
  figer la partie des autres. Deux pistes y sont posées — tranche entre elles, ne réinvente pas
  la question.

## Ce qu'il faut définir avant d'écrire du code

1. **Effectif.** Combien d'humains au maximum (Matt évoque une dizaine) ? Les bots complètent-ils
   jusqu'à l'effectif solo (`CONFIG.BOT_COUNT`) ? Qui simule les bots — l'hôte, forcément ?
2. **Le code de partie.** Longueur, alphabet (sans caractères ambigus), durée de vie, unicité, ce
   qui se passe si on rejoint une partie déjà commencée (spectateur ? apparition immédiate ?).
3. **Monde commun.** L'hôte fixe les dimensions et les transmet ; que voit un joueur dont l'écran a
   un ratio très différent ? La caméra et le dézoom (`updateCamera`) doivent rester jouables sur un
   monde qu'on n'a pas calculé pour soi.
4. **Modèle de synchro.** Ce que l'hôte envoie (état complet ? deltas ?), à quelle fréquence, ce que
   les clients envoient (leur cap uniquement ?), comment on masque la latence (interpolation,
   prédiction), et le budget en octets par tick pour un effectif plein.
5. **Pause en multi.** Applique le §6 du cahier des charges. Et la victoire depuis Pause
   (`confirmPauseExit`) : que devient-elle quand plusieurs humains sont dans l'arène ? Une victoire
   « je suis n°1, je sors » a-t-elle encore un sens, ou faut-il une fin de partie commune ?
6. **Déconnexions.** Hôte qui part, client qui part, réseau qui tombe. Que voit chacun, que devient
   l'XP en cours, que devient la partie.
7. **Écran d'accueil.** Nouveau bouton **« Partie Privée »** à côté ou sous « Jouer », **au même
   format de design** : mêmes barres HUD codées, même hachure de bord droit, même couleur
   d'interface, cible tactile 44 × 44 px. Il lui faut un code de barre HUD cohérent avec la série
   existante (`A01`…`A06`) — à choisir, pas à inventer au hasard.
8. **Écran de salon.** Créer / rejoindre, liste des joueurs présents, qui est l'hôte, lancer la
   partie. Bloquant ou non-bloquant selon la grille du cahier des charges §2.
9. **Six langues.** Tout libellé d'interface ajouté existe en fr, en, es, de, it, pt. Les textes de
   jeu restent en français (règle du §7).
10. **Hors-ligne.** La PWA se revendique jouable hors-ligne : la partie privée exige le réseau. Que
    montre le bouton quand on est hors-ligne — désactivé, masqué, ou message ?

## Ce qu'on attend en sortie

1. Une **note de conception** courte : effectif, protocole, format des messages, gestion des
   déconnexions, ce qui est simulé où.
2. Le **bloc MODIFICATIONS DOC PROPOSÉES** pour `cahier-des-charges-ui.md` (§6 notamment, qui
   annonce ce chantier) — soumis à validation, jamais appliqué en autonomie.
3. Après validation seulement : l'**implémentation**, par lots commitables un par un.
4. Une **procédure de test à deux navigateurs** rejouable par Matt, écrite noir sur blanc.

## Méthode

Une question précise à la fois plutôt qu'une supposition. Chaque proposition arrive avec **ta
recommandation et son motif en une phrase**. Aucune affirmation sur le code sans l'avoir ouvert
dans la session ; aucune affirmation sur le réseau sans l'avoir mesurée à deux navigateurs.
Français dans les échanges et les commentaires, anglais réservé au code.
