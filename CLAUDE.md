@SOUL.md
@AGENTS.md

# Règles — mini-jeux

## Ouvrir

- Préfixer chaque commande du kit par ton nom, l'export ne survivant pas d'un appel à l'autre :
  `WORKFLOW_AGENT=<ton-nom> python3 bin/workflow.py snapshot`.
- Lire la dernière entrée de `JOURNAL/`, puis `Snake'on/_MANIFEST.md` avant toute affirmation
  sur le jeu — c'est son routeur, tenu par le jeu lui-même.
- Déclarer ton périmètre avant d'écrire, `python3 bin/workflow.py claim <T-xxx> --surface
  <chemin> --motif "…"`, et clore avec ce qui a été constaté, `python3 bin/workflow.py todo done
  <T-xxx> --verif "…"`.
- Lire `OUTILS.md`, et le mettre à jour dans la session même où un agent, un skill, un contrôle
  ou un hook apparaît, change de rôle ou disparaît.

## Tenir le travail

- Ouvrir une todo-list dès que la tâche porte plus d'un point, visible dès ta première réponse ;
  tenir les deux listes — à faire, fait — et republier l'entière dès qu'un point bouge, avec son
  motif pour tout point abandonné.
- Tracer chaque point terminé au journal du jour, `JOURNAL/AAAA-MM-JJ.md`, sous un titre à
  l'heure, avant de passer au suivant — c'est la seule surface qui porte le récit ; le kit
  (`.workflow/journal.jsonl`) trace pour la machine, ce fichier trace pour qui lit.
- Un changement critique — une conclusion qui engage, une mesure qui conditionne une livraison —
  se fait falsifier par un agent qui ne l'a pas produit, sur la conclusion seule (contre-passe) :
  c'est déjà ce qui a trouvé les deux vrais défauts du réseau pair-à-pair, jamais les propres
  vérifications de l'auteur.
- **R-09** : un rendu refusé par un vérificateur — ton, test, contre-passe — repart en boucle
  jusqu'à passer. Une preuve de fin est sa sortie qui passe, jamais un contrôle contourné.
- Conclure tout rendu par ce qui reste ouvert et ce qui attend un arbitrage de Matt.

## Le jeu, et le dépôt public

- Monter `CACHE_VERSION` d'un cran dans `Snake'on/sw.js`, dans le commit du changement — sans
  bump, un joueur qui a installé la PWA garde les anciens assets.
- Avant de conclure qu'un correctif front ne marche pas, désinscrire le service worker et vider
  les caches : il sert une version fantôme pendant les tests, piège déjà payé.
- Aucune donnée personnelle, aucune progression de joueur (`localStorage`), aucun fichier du
  coffre `Obsidian_MiniJeux/` ne rentre dans un commit — ce dépôt est **public**, servi tel quel
  par GitHub Pages : ce qui entre est publié.
- Repérer une section de `Snake'on/index.html` par ses bannières de sommaire, prendre tout
  chiffre de gameplay dans l'objet `CONFIG`, et faire porter un document la commande qui le
  relit plutôt que sa valeur.

## Avant d'annoncer qu'une chose marche

- Jouer les quatre contrôles du §9 du cahier des charges (`Snake'on/cahier-des-charges-ui.md`)
  et lire leur sortie entière, jamais leur seul code de retour.
- Faire trancher une valeur mesurée dans la page — `getBoundingClientRect`, styles calculés,
  `DOMMatrix` — en desktop **et** en 375×812 mobile.
- Laisser tourner 5 à 10 secondes avant de capturer une page à canvas animé en continu.
- Boucler sur un marqueur absent de la version précédente pour vérifier le déployé (GitHub
  Pages met environ une minute), et jouer depuis l'URL de production, pas seulement `localhost`.

## Déléguer

| Ce que tu as à faire | À qui |
|---|---|
| Chercher si ça existe déjà, avant de produire | `verifier-existant` |
| Faire tomber une conclusion avant de la remonter | `refuter` |
| Prouver qu'un contrôle sait encore rater | `test-saboteur` |
| Jouer la suite, traquer le code mort et inutile | `code-health-auditor` |
| Comparer deux configurations sur un banc rejouable | `bench-runner` |
| Diagnostiquer une panne jusqu'à sa cause | `apex-investigator` |
| Relire un changement par le risque | `apex-reviewer` |
| Relire un rendu fini contre sa direction visuelle | `impeccable-finish-reviewer` |
| Produire un asset raster depuis une maquette validée | `impeccable-asset-producer` |

- Déclarer ton budget d'agents en tête de tâche, et dire à chaque sous-agent ce qu'il peut
  écrire et où — par défaut, rien, et s'il peut en lancer d'autres — par défaut, non.
- Proposer à Matt un spécialiste dès qu'un même contexte isolé se redemande deux fois ; tu le
  crées sans validation préalable et l'inscris à `OUTILS.md` le jour même.

## Remonter

- **À Matt** : pousser sur `main` (publication), introduire une dépendance, un build ou un
  serveur, modifier le cahier des charges d'un jeu, tout geste irréversible ou destructif.
- **À Matt** : une contradiction entre ce dépôt et la doctrine d'orchestration que tu ne peux
  pas trancher seul — jamais réduite au silence « parce qu'il faut avancer ».
- **À l'orchestrateur** : ce qui touche un autre domaine — ta part faite, ce qui reste, et à
  quel domaine cela appartient.
- **À l'orchestrateur master, pour analyse** : ton état, par la boîte d'échange
  (`~/echanges-agents/deposer.py --de claude-mini-jeux --pour claude-prolexcore`).

## Où vit le reste

- Les règles propres à ce dépôt — vérification avant merge, maquette Claude Design, assets IA,
  données personnelles — vivent dans `AGENTS.md`, importé en tête.
- Vérification, secrets, git, mémoire, voies vers Spark : `~/.claude/CLAUDE.md`. Rien de tout
  cela n'est recopié ici.
