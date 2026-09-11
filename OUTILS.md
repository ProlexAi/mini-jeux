# mini-jeux — outils

Ce dont l'agent **mini-jeux** dispose : à qui déléguer, quoi jouer, quoi servir. Rang **dédié**
(D59/D60) — il écrit dans son dépôt, délègue la production, vérifie, rend compte.

*Relevé le 2026-09-11 au soir, dépôt `/home/matt/mini-jeux`, session d'implantation
(D82/D104). Chaque ligne a été rejouée ce soir, sauf mention contraire. Ce qui n'a pas pu
l'être est marqué « non vérifié ».*

---

## 1. À qui déléguer

| Ce que j'ai à faire | Je délègue à | D'où il vient |
|---|---|---|
| Chercher si ça existe déjà, avant de coder | `verifier-existant` | socle |
| Faire tomber une conclusion avant de la transmettre à Matt | `refuter` | socle |
| Prouver qu'un contrôle sait encore rater | `test-saboteur` | socle |
| Faire tourner la suite, traquer le code mort et inutile | `code-health-auditor` | socle |
| Comparer des configurations, monter un banc rejouable | `bench-runner` | socle |
| Savoir qui travaille où quand plusieurs sessions tournent | `orchestrateur-federe` | socle |
| Relire un rendu fini contre sa direction visuelle | `impeccable-finish-reviewer` | plugin `impeccable` |
| Produire un asset raster propre depuis une maquette validée | `impeccable-asset-producer` | plugin `impeccable` |
| Diagnostiquer une panne jusqu'à sa cause | `apex-investigator` | plugin `apex` |
| Relire un changement par le risque | `apex-reviewer` | plugin `apex` |

**Mesuré** : `/home/matt/mini-jeux/.claude/agents/` n'existe pas — le dépôt n'a toujours aucun
agent à lui. Les neuf liens de `~/.claude/agents/` pointent tous vers
`ProlexCore/SOCLE/agents/`. `orchestrateur-federe` n'est plus inerte ici depuis WP5 (2026-09-09) :
le kit est posé et fédéré (§2). Les trois `codebase-memory-*` restent **hors service** —
`codebase-memory-mcp` toujours absent (`ListMcpResourcesTool`/`.mcp.json` néant, voir §4).

`SOCLE/agents/mini-jeux-projet.md` (lien `~/.claude/agents/mini-jeux-projet.md`, mesuré présent)
reste en place ce soir : D69 le retire « quand l'orchestrateur dédié de son dépôt est posé », mais
seulement une fois la branche fusionnée sur `main` — même précédent que KmopBudget, dont le
retrait a attendu la fusion. Ma branche (`orchestration-2026-09-11`) ne l'est pas. Suite à
proposer à Matt une fois la fusion faite (équivalent local de T-172).

---

## 2. Les commandes qui prouvent

Zéro dépendance, zéro build. Les contrôles sont des fichiers autonomes, joués à la main.

### Le kit `agent-workflow` — 1.22.0, fédéré

```bash
WORKFLOW_AGENT=<ton-nom> python3 bin/workflow.py snapshot     # tâches réservées, par qui
WORKFLOW_AGENT=<ton-nom> python3 bin/workflow.py claim/done   # réserver, clore avec --verif
python3 /home/matt/ProlexCore/SOCLE/kits/agent-workflow/installer.py . --controle
```

Mesuré ce soir : socle 1.22.0, installé 1.22.0, conforme. `.workflow/local.json` porte
`agents: ["claude-mini-jeux", "git"]` (T-055) — non versionné (gitignoré par le kit lui-même,
motif dans `.workflow/.gitignore`). 4 dépôts fédérés au registre.

### Les quatre contrôles rejouables du jeu — canon au §9 de `Snake'on/cahier-des-charges-ui.md`

```bash
node "Snake'on/verifie-traductions.js"                       # 6 langues completes, aucune cle morte ni orpheline
node "Snake'on/verifie-formes-speciales.js"                  # teinte imposee lue la ou elle est declaree
python3 "Snake'on/ia-assets/verifie-chemins.py"              # dossier d'entree ComfyUI jamais code en dur
shellcheck -S style docs/migration-linux/restauration-linux.sh
```

Non rejoués ce soir (aucun code de jeu touché) — dernier vert connu : 2026-09-08 21:48
(`EXIT=0` chacun, `Obsidian_MiniJeux/03-Travailler/De-la-modification-a-la-mise-en-ligne.md`).
Les trois premiers portent leur témoin **dans** l'instrument ; le quatrième est un outil tiers.
Chacun accepte un chemin de cible pour être joué sur une copie sabotée.

### Servir le jeu et y jouer

`preview_start` avec une configuration de `.claude/launch.json` — `snakeon` (port 8420) et
`snakeon-wt` (port 8422, depuis un worktree), toutes deux `python3 -m http.server --directory
Snake'on`. Mesuré présent, inchangé depuis 2026-09-08.

### Vérifier le déployé

Pousser sur `main` publie sur `https://prolexai.github.io/mini-jeux/` (~1 min, GitHub Pages).

```bash
grep -n "CACHE_VERSION" "Snake'on/sw.js"          # v14, mesure ce soir — inchangee depuis le 2026-09-08 (aucun deploiement entre-temps)
md5sum "Snake'on/index.html"                      # a confronter au fichier servi en ligne
```

### Autres exécutables

| Fichier | Ce qu'il fait | Plateforme |
|---|---|---|
| `Snake'on/ia-assets/build_style_sheet.py` | assemble la planche de style pour ComfyUI | les deux |
| `Snake'on/ia-assets/generate_piece*.ps1` | génération d'assets, chaîne standard/Flux | Windows — non vérifié ici, ni `$env:` ni secret trouvés par grep ce soir |
| `docs/migration-linux/restauration-linux.sh` | restauration du poste après migration | Linux — jamais exécuté (T-010) |

---

## 3. Skills

Aucun skill propre : `/home/matt/mini-jeux/.claude/skills/` n'existe pas (mesuré). Plugins
activés (`~/.claude/settings.json`, mesuré ce soir) : `prolex-agents`, `prolex-seo`,
`prolex-marketing`, `impeccable`, `apex`, `permafrost` — ce dernier absent du relevé du
2026-09-08, ajouté depuis.

| Besoin | Skill |
|---|---|
| Créer ou refondre un rendu visuel navigateur | `web-design-engineer` |
| Revue d'interface complète (a11y, typo, couleur, texte) | `better-interface` |
| Un bug, un test qui casse, un comportement inattendu | `systematic-debugging` |
| Prouver que ça marche avant de l'annoncer | `prolex-agents:verification-before-completion` |
| Deux tâches indépendantes en parallèle | `prolex-agents:dispatching-parallel-agents` |
| Retrouver une décision d'une session passée | `session-recall` |
| Lancer et piloter le jeu pour voir un changement tourner | `run` |

---

## 4. Serveurs MCP

Aucun `.mcp.json`, ni dans le dépôt ni chez l'utilisateur (mesuré ce soir, inchangé). Disponible
par le harnais et les plugins : `Claude_Browser` (mesure dans la page qui tourne), `visualize`,
`terminal`, `ccd_session`, `hermes` (fenêtre fermée 08h-12h UTC+2 fixe, hook bloquant). Une
quinzaine de connecteurs de plugins restent sans autorisation OAuth.

---

## 5. Hooks

**Git** : `core.hooksPath` = `.githooks` (mesuré), versionnés. `pre-commit` **consultatif** —
en-tête relu ce soir : « il regarde, il avertit, il ne modifie RIEN » (motif écrit : une version
antérieure faisait `git add -A`, contournant le pathspec explicite d'`AGENTS.md` §11, corrigée).
`post-commit` journalise vers le registre via `.workflow/local.json`.

**Session** (`~/.claude/settings.json`, tous vers `ProlexCore/SOCLE/hooks/`) :

| Moment | Hook | Effet |
|---|---|---|
| `PreToolUse` / Bash | `gardes-shell.py` | gardes sur les commandes shell |
| `PreToolUse` / Bash + `mcp__hermes__.*` | `hermes_window.py` | refuse Spark 08h-12h UTC+2 |
| `PostToolUse` / Skill | `log_skill_use.py` | journalise l'usage des skills |
| `SessionStart` | `injecter-revisions.py`, `garde-worktree-a-jour.py`, `indexer-sessions.py` | reprise, worktree, index |
| `SessionEnd` | `balayer-ledger.py` | balaye le registre |
| `Stop` | `reviser-session.py` | révision de fin de session |

---

## 6. Services et infrastructure

- **Publication** : GitHub Pages sur `main`, `git@github.com:ProlexAi/mini-jeux.git`, public.
  `.nojekyll` à la racine et dans `Snake'on/` (mesuré présent ce soir). Pousser, c'est publier.
- **Aucun serveur applicatif, aucune base, aucune API.** Progression du joueur dans le
  `localStorage` du navigateur, jamais dans le dépôt.
- **Coffre Obsidian** : `Obsidian_MiniJeux/`, gitignoré, jamais publié (D85, posé ce soir —
  §2ter du rapport d'état).
- **Génération d'assets** : ComfyUI local, un seul LoRA actif à la fois (VRAM 16 Go). Chemin du
  dossier LoRAs — non vérifié sous Kubuntu.
- **Worktrees** : `.claude/worktrees/` existe, vide, ignoré par Git.

---

## 7. Ce qui manque encore

| Manque | Conséquence | Le geste qui le comble |
|---|---|---|
| **`mini-jeux-scribe` écrit mais pas installé** | Inappelable — fiche dans `SOCLE/profils-agents/agents-scribes/`, aucun lien | L'installer si le besoin se confirme |
| **Aucun agent de production propre au jeu** | Personne ne sait spécifiquement lire `index.html` (monolithe) ni mener une passe de mesure navigateur sans repasser par un agent générique | Un agent « mesure dans la page » à écrire, sur le critère du contexte isolé (pas fait ce soir : hors périmètre du prompt, §4) |
| **`codebase-memory-mcp` retiré** | Trois agents de socle sur neuf inertes ici | Réinstaller — `ProlexCore/SOCLE/mcp/README.md` |
| **Contrôles Windows injouables sous Kubuntu** | `verifie-chemins.py` ne prouve que sa branche Linux ; les `.ps1` non couverts | Les jouer depuis Windows, ou les déclarer hors périmètre |
| **`SOCLE/agents/mini-jeux-projet.md` toujours présent** | Doublonne une partie du coffre et d'`AGENTS.md`, promis au retrait par D69 | Le proposer à Matt une fois la branche de ce soir fusionnée sur `main` |
| **`AGENTS.md` n'a pas les pièges détaillés de `mini-jeux-projet.md`** (SW fantôme nommé, Wayland, qualité graphique adaptative) | Cette richesse ne vit que dans un sous-agent promis au retrait et dans le coffre versé ce soir | Proposer leur fusion dans `AGENTS.md` avant le retrait ci-dessus, pour ne rien perdre |

---

## Comment tenir ce document

Il se met à jour **dans la session où le changement a lieu**, jamais après coup. Ce qui le
déclenche : un agent/skill/plugin apparaît, change de rôle ou disparaît · un contrôle rejouable
change · une configuration entre ou sort de `.claude/launch.json` · un hook est posé ou retiré ·
un serveur MCP est connecté ou retiré · un manque du §7 est comblé.

```bash
ls ~/.claude/agents /home/matt/mini-jeux/.claude/agents 2>&1
ls /home/matt/mini-jeux/.claude/skills 2>&1
git -C /home/matt/mini-jeux config --get core.hooksPath ; ls /home/matt/mini-jeux/.githooks
python3 /home/matt/ProlexCore/SOCLE/kits/agent-workflow/installer.py /home/matt/mini-jeux --controle
cat /home/matt/mini-jeux/.claude/launch.json
```

Un chiffre qu'on ne peut pas rejouer par une de ces commandes n'a pas sa place ici : il vit au
journal, daté.
