# Prompt de session — Des skins qui changent le serpent, pas seulement sa couleur

> **Écrit le 22/08/2026. Document jetable :** il sert à ouvrir UNE session de brainstorm, puis se
> supprime — comme `PASSATION.md` avant lui, périmé le jour où le jeu a dépassé ce qu'il décrivait.
> Il ne recopie aucune valeur du jeu : tout ce qui est chiffré se relit à la source, citée à chaque
> fois. Si une phrase d'ici contredit le code, **c'est le code qui a raison**.

## Ce qu'on te demande

Animer une session de **brainstorm produit + technique** sur les skins de Snake'on. Pas
d'implémentation dans cette session : le livrable est une **liste de décisions argumentées** et un
**addendum au cahier des charges** proposé à la validation de Matt.

## Le problème, en une phrase

Le menu Accueil promet une entrée « 🎨 Skins » (`A01` au cahier des charges), mais un skin ne
change aujourd'hui **qu'une couleur** : `CONFIG.SKINS` ne porte qu'un `name`, un `color` et un
`unlockLevel`, `currentSkin()` n'en tire que la couleur, et `Snake.draw()` n'utilise que
`this.color`. Monter de niveau ne change donc **rien de physique** — même corps, même tête, même
traînée. Un joueur qui débloque le niveau 20 voit exactement le serpent du niveau 1, en doré.

Vérifie-le toi-même avant de partir de là :

```bash
grep -n "SKINS\|currentSkin\|this.color" "Snake'on/index.html"
```

## Ce qu'il faut trancher

1. **De quoi un skin est-il fait ?** Corps (motif, écailles, segmentation, épaisseur), tête (forme,
   yeux, mâchoire, antennes), traînée/aura, déformation à la vitesse, comportement du dessin quand
   le serpent grossit. Lesquels de ces axes ouvre-t-on, et lesquels reste-t-on à ne jamais toucher ?
2. **Skin vs couleur d'interface.** Le joueur choisit déjà une couleur d'UI parmi huit (§2 du
   cahier des charges) qui irrigue toute l'interface. Un skin doit-il en être indépendant, la
   suivre, ou la remplacer en jeu ? Le risque à nommer : deux systèmes de couleur qui se marchent
   dessus.
3. **Lisibilité en jeu, non négociable.** Un joueur doit lire en un coup d'œil qui est plus long que
   lui — c'est devenu le critère de vie ou de mort depuis que la prédation se compare sur la
   longueur (cf. `EAT_RATIO` et `radiusForLength` dans `index.html`). Un skin ne doit jamais rendre
   un serpent plus difficile à jauger. Comment le garantir : contrainte de silhouette ? de contraste ?
4. **Progression.** Le déblocage par niveau existe (`unlockLevel`). Garde-t-on un skin par palier,
   ou passe-t-on à des pièces combinables (tête + corps + traînée) ? Combien de combinaisons avant
   que la grille de l'Accueil devienne illisible sur mobile ?
5. **Budget de rendu.** Le jeu dessine le corps en **un seul chemin** — c'est explicitement ce qui
   tient les 60 fps quand un serpent dépasse quelques centaines de segments (commentaire dans
   `Snake.draw()`), et il n'y a plus de plafond de longueur depuis le patch du 22/08/2026. Tout skin
   qui dessine segment par segment est à justifier, chiffres à l'appui. Le réglage « Qualité
   graphique » a trois paliers : quel skin dégrade quoi à chaque palier ?
6. **`prefers-reduced-motion`.** Le cahier des charges en fait une contrainte d'accessibilité non
   négociable. Un skin animé doit avoir sa version figée.
7. **Bots.** Ils tirent leurs couleurs dans `CONFIG.BOT_COLORS`. Portent-ils des skins ? Si oui,
   lesquels — et comment reste-t-on capable de distinguer un bot d'un joueur humain quand la partie
   privée arrivera (voir `PROMPT-partie-privee.md`) ?
8. **Réplication multijoueur.** Le skin devra voyager entre joueurs. Ça n'impose rien aujourd'hui,
   mais un skin défini par un *identifiant* se réplique en trois octets, un skin défini par un
   *paquet de paramètres* est plus coûteux à synchroniser. À décider **maintenant**, pas après.

## Contraintes du dépôt à respecter

- **Un seul fichier de jeu.** Tout vit dans `Snake'on/index.html` (HTML + CSS + JS), sans build,
  sans dépendance, servi en PWA hors-ligne. Une bibliothèque tierce est hors sujet.
- **Canvas 2D**, pas de WebGL — le changer serait une décision d'architecture à part entière.
- **Mobile prioritaire**, cible tactile minimale 44 × 44 px.
- **Six langues** d'interface (fr, en, es, de, it, pt). Les noms de skins sont-ils de l'interface
  (donc traduits) ou du texte de jeu (donc français partout, comme les succès et les toasts) ?
  Le §7 du cahier des charges pose la règle : applique-la, ne la réinvente pas.
- **`Snake'on/cahier-des-charges-ui.md` est normatif.** On ne le modifie jamais en autonomie :
  la session finit par un bloc « MODIFICATIONS DOC PROPOSÉES » (fichier, diff exacte, une phrase
  de justification) soumis à Matt.
- **Français** dans les échanges et les commentaires ; anglais réservé au code et aux identifiants.

## Ce qu'on attend en sortie

1. Une **définition écrite de ce qu'est un skin** dans ce jeu, en trois lignes maximum.
2. Le **jeu de skins retenu**, chacun avec : ce qu'il change physiquement, son coût de rendu
   estimé, son comportement en `reduced-motion`, son palier de déblocage.
3. Les **arbitrages rejetés** et pourquoi — ça évite de les rouvrir à la session suivante.
4. Le bloc **MODIFICATIONS DOC PROPOSÉES** pour le cahier des charges.
5. Une **estimation d'effort** par skin, pour que Matt choisisse par où commencer.

## Méthode

Une question précise à la fois plutôt qu'une supposition. Chaque proposition arrive avec **ta
recommandation et son motif en une phrase** — y compris quand la recommandation est de ne rien
faire. Aucune affirmation sur le code sans l'avoir ouvert dans la session.
