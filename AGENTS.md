# mini-jeux — règles spécifiques au dépôt

Portées à ce dépôt uniquement. Portées depuis les sessions de travail sur Windows
(projet local `C:\JeuRapide`) lors de la migration vers Kubuntu, 2026-09.

## Vérification avant merge

Quand Matt dit « vérification complète, si validé merge et push », il attend une séquence
entière et autonome : **captures d'écran + contrôle de conformité contre le cahier des
charges → correction de ce qui cloche → retest → merge → push → déploiement vérifié en
ligne**, sans repasser par lui entre chaque étape.

- **Mesurer, ne pas juger à l'œil** (`getBoundingClientRect`, styles calculés, `DOMMatrix`).
  Plusieurs défauts sur Snake'on n'étaient pas visibles sur une capture desktop classique.
- **Vérifier en mobile (375×812), pas seulement en desktop** — un défaut de hachure n'existait
  qu'en dessous de 480px à cause d'une media query de spécificité égale.
- **Vérifier le déployé, pas seulement le local.** GitHub Pages met ~1 minute à reconstruire :
  boucler sur un marqueur du correctif avant d'annoncer la mise en prod.
- **Distinguer régression et comportement conditionnel** avant de « corriger » — vérifier
  `git show <commit>:<fichier>` plutôt que de supposer.
- **Laisser tourner plusieurs secondes avant la capture** sur toute page à canvas animé en
  continu (fond `#neonFxCanvas`, particules, traînées). Un menu masqué par un `fillRect`
  semi-transparent rejoué en boucle peut converger vers l'opacité totale en ~15 frames — un
  défaut invisible sur un screenshot pris juste après le chargement. Attendre 5-10s avant de
  capturer.

## Les pièges de mesure de ce dépôt

Ici l'instrument ment plus souvent que le code. Ces cinq-là sont mesurés, et chacun fait
conclure faux sans jamais lever d'erreur.

**Le service worker sert une version fantôme.** Le premier essai après un correctif a rendu
« toujours cassé » alors que le disque était bon : c'était le SW qui servait l'ancien
`index.html`. Une passe de test entière perdue le 2026-09-07. Deux gestes en découlent :

- interroger le **runtime** plutôt que le fichier — par exemple `netStyleFrom.toString()` dans
  la console, qui dit ce qui tourne vraiment ;
- désinscrire le SW et vider les caches avant de conclure quoi que ce soit.

**Un onglet en arrière-plan fige la boucle de jeu.** `document.visibilityState === 'hidden'`
suspend `requestAnimationFrame`, au point qu'un `await` sur une frame expire. Sous Wayland,
aucun script ne met au premier plan la fenêtre d'une autre application — c'est une limite de
conception, pas un outil manquant. Deux clients ne se capturent donc pas simultanément : il
faut les mettre au premier plan à tour de rôle, ou cadencer `gameLoop` à la main.

**La qualité graphique se dégrade toute seule.** Sous le seuil de fps, le jeu descend de HIGH à
MEDIUM sans qu'on l'ait demandé (`save.settings.quality`). Un pilotage headless tourne autour de
2 fps : la qualité chute pendant la mesure. La remettre à HIGH avant toute capture de skin.

**Sans viewport réel, `window.innerWidth` vaut 0** et tous les chiffres de monde deviennent des
inventions — le code retombe sur `WORLD_MIN`. Forcer un viewport réel (1100×700, la référence du
dépôt) avant toute mesure, puis rejouer en 375×812.

**Snake'on est un monolithe.** Tout — CSS, JS, HTML, dictionnaires de traduction — vit dans le
seul `Snake'on/index.html`. Sa taille se mesure :

```bash
python3 -c "t=open(\"Snake'on/index.html\",encoding='utf-8').read();print(t.count(chr(10))+1,len(t))"
```

L'édition se fait par motif unique, diff relu. Une réécriture globale du fichier détruit du code
qui n'a jamais été lu.

## Lire une maquette exportée depuis Claude Design

Les maquettes déposées dans ce dépôt (ex. `Snake'on/Snake'on - Eclat neon au clic.html`) sont
des exports Claude Design : un bundle d'environ 1 Mo, essentiellement du React gzippé en
base64, illisible tel quel et trop gros pour une lecture directe.

Le HTML de référence exact est lisible en clair mais concentré sur une seule ligne géante :
le bloc `<script type="__bundler/template">` contient une chaîne JSON à décoder pour obtenir
le template complet (CSS, `@keyframes`, valeurs numériques exactes, code du composant).

Repérer la ligne à décoder :

```bash
awk '{ print length, NR }' "<fichier>.html" | sort -rn | head -5
```

Décoder cette ligne (`json.loads` en Python) et écrire le résultat dans un fichier scratch
avant de le lire — c'est la seule source qui donne les valeurs exactes voulues par Matt
(durées d'animation, formules de dégradé, géométrie des clip-path) plutôt qu'une
approximation à l'œil depuis une capture.

**Piège vérifié :** le CSS de maquette utilise `transform: skewX(8deg)`, qui penche le texte
vers l'arrière (contre-inclinaison). Écrire `-8deg` donne l'inverse (italique avant).

## Génération d'assets IA (ComfyUI / LoRAs)

Un seul LoRA actif à la fois dans un workflow ComfyUI de test. Un LoRA testé et réfuté
(résultat ne convient pas) se supprime du dossier de LoRAs local plutôt que d'être laissé
« au cas où ».

**Pourquoi :** contrainte VRAM sur la RX 7900 GRE (16 Go) — consigne explicite de Matt lors
du choix des LoRAs de style pour les skins Snake'on. Le chemin exact du dossier LoRAs dépend
de l'installation ComfyUI locale sur Kubuntu (backend Vulkan/ROCm, plus DirectML comme sous
Windows) — à vérifier avant d'appliquer, ne pas supposer `C:\ComfyUI\...`.

## Données personnelles hors dépôt

Le dépôt est **public** : aucune progression de joueur (localStorage `neonSnakeUltimate_v1`
sur `prolexai.github.io`) ne doit y être versionnée. Cette donnée vit uniquement dans le
navigateur et, en sauvegarde, hors-git sur la clé USB de migration.
