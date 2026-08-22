# Prompt de passation — Snake'on

*Rédigé le 22/08/2026, après la V0.3 du cahier des charges UI. À coller comme premier message
d'une nouvelle session pour reprendre le travail avec le contexte complet.*

---

Je reprends le développement de **Snake'on**, un mini-jeu solo type slither.io (HTML/JS/CSS pur,
sans dépendance, PWA jouable hors-ligne), dans le dépôt GitHub `ProlexAi/mini-jeux`
(https://github.com/ProlexAi/mini-jeux.git), sous-dossier `Snake'on/` (avec l'apostrophe — c'est
le nom réel du dossier depuis le commit `5c0d660`, distinct de `neon-snake/` qui n'existe plus).

Jeu en ligne : https://prolexai.github.io/mini-jeux/Snake'on/
Portail : https://prolexai.github.io/mini-jeux/

## État du code (implémenté, en ligne)

- Mode sans fin façon slither.io : pas de victoire, mort → mode spectateur (4s, vue du tueur) →
  réapparition immédiate dans la même arène.
- Découpe corps-à-corps **non létale** : toucher le corps d'un serpent plus petit le raccourcit
  (il survit) et génère des ressources proportionnelles à ce qui a été amputé ; seul un coup sur
  la **tête** détruit entièrement.
- Effets de kills (fumée/éclair/flamme) généralisés sur toute la longueur du corps.
- Écran **Réglages** (5ᵉ onglet du menu — pas encore accessible depuis Pause, voir plus bas) :
  Audio en deux interrupteurs ON/OFF (Musique, Effets), Qualité graphique en 3
  niveaux **Low/Medium/High** (pilote le plafond de résolution DPR, le budget de particules, les
  halos lumineux), Commandes en rappel texte.
- Pop-up de bienvenue à la toute première partie uniquement.
- Pause : bouton **Abandonner** (drapeau, contour rouge fixe) avec confirmation obligatoire ;
  ne compte pas comme une vie (pas de XP, pas d'historique).
- Aucune couleur d'interface personnalisable, aucun effet de clic, pas de multi-langue.

## Cahier des charges — à jour, en avance sur le code

`Snake'on/cahier-des-charges-ui.md` est en **V0.3** (commit `bd34960`) : il documente des
décisions qui ne sont **pas encore codées**. Artefact de lecture (mis en page, diagramme) :
https://claude.ai/code/artifact/06563fc5-c35c-494b-a61b-b860c2c5377b

### Ce que la V0.3 ajoute au-dessus du code actuel (à implémenter)

1. **Couleur d'interface personnalisable** : 8 teintes au choix (cyan par défaut `#00ffcc`, vert
   `#39ff88`, citron `#d8ff3c`, ambre `#ffb020`, corail `#ff7a4d`, rose `#ff4d9d`, violet
   `#b06bff`, bleu `#3ba9ff`), propagée à toute l'UI. Seule exception fixe : **Abandonner** reste
   rouge (`#ff5c8a`), encadré de deux ⚠, jamais personnalisable.
2. **Éclat néon au clic** : effet transverse déclenché sur chaque interaction **dans les menus
   uniquement** (jamais pendant une vie — HUD/classement/pause/toasts restent nets). Anatomie en
   4 phases sur ≤600ms : Vol 110ms (bille arrive du haut-gauche) → Cœur 150ms (flash blanc
   4→30px) → Anneau 260ms (6→62px) → Éclats 430ms (14 traînées). Prend la couleur d'interface
   choisie, toujours rouge sur Abandonner.
3. **Réglage Effets** (nouveau, distinct de Qualité graphique) : intensité de l'éclat de clic —
   sélecteur Aucun (flash seul) / Léger (anneau + moitié) / Complet (bille lancée).
4. **Qualité graphique redéfinie en résolution** : 1280×720 "économe" / 1600×900 "équilibré" /
   1920×1080 "natif", remplace les libellés Low/Medium/High actuels.
5. **Audio en curseurs numériques** : Musique et Sons, 0–100 chacun, remplace les deux
   interrupteurs ON/OFF actuels.
6. **Réglage Langue** : sous-page listant 6 langues (nommées dans leur propre langue) — le jeu
   est aujourd'hui 100% français, code compris (pas de couche i18n).
7. **Réglages accessible depuis Pause**, pas seulement depuis l'Accueil — avec un aperçu "vivant"
   inline (puces Effets, curseur Musique visibles directement dans l'écran Pause).
8. **Typographie** : police Tektur (titres/HUD, contre-inclinée 8°) + Rajdhani (texte courant) —
   remplace les polices système actuelles. `prefers-reduced-motion` doit figer toutes les
   animations liées (contre-inclinaison, clignotement, éclat de clic).
9. **Pause** : sous-titre stylé `SYS//HALT` sous le titre.
10. **Variantes paysage mobile** maquettées (844×390) pour Accueil, Réglages, Pause — non prises
    en compte dans l'implémentation actuelle (portrait-first).

## Points ouverts à trancher (§7 du CDC) — avant ou pendant l'implémentation

- **Les 6 langues** : lesquelles précisément ? Le français reste-t-il la référence pour les
  textes de jeu (succès, toasts…) ou seule l'interface se traduit ? C'est un chantier
  d'internationalisation à part entière, pas un réglage ponctuel.
- **Qualité graphique vs performance** : le code actuel pilote déjà DPR + budget de particules +
  halos via 3 niveaux abstraits. Il faut faire correspondre chaque résolution concrète
  (1280×720/1600×900/1920×1080) à un budget d'effets cohérent, pas seulement changer le rendu en
  pixels affiché.
- **"Hachures"** citées dans la maquette comme élément suivant la couleur d'interface — motif
  visuel non défini (où, à quelle échelle) : à préciser avant de coder quoi que ce soit dessus.
- **Panneau Réglages dans Pause** : identique en tout point à celui de l'Accueil, ou une version
  condensée propre à l'aperçu "vivant" décrit dans la maquette ?

## Autre point en suspens (hors CDC, remonté lors du renommage)

`SAVE_KEY: 'neonSnakeUltimate_v1'` dans `index.html` n'a **pas** été renommé lors du passage
`neon-snake` → `Snake'on` : le changer viderait silencieusement la sauvegarde localStorage de
quiconque a déjà joué (niveau, XP, skins, succès, historique deviendraient inaccessibles, pas
supprimés mais orphelins). Aucun bénéfice fonctionnel à le renommer tant que ce n'est pas voulu
explicitement — à trancher avec Matt si un reset des sauvegardes est acceptable/souhaité.

## Prochaine étape suggérée

Trancher les 4 points ouverts ci-dessus avec Matt, puis implémenter la V0.3 dans le code
(`Snake'on/index.html`) en réutilisant le système déjà en place (overlays `.tab-content`,
`bindBtn`, `save.settings`, quality gating existant) plutôt que d'en inventer un nouveau.
