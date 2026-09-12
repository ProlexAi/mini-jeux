# mini-jeux — outils

Ce dont l'agent **mini-jeux** dispose : à qui déléguer, quoi jouer, quoi servir. Rang **dédié**
(D59/D60) — il écrit dans son dépôt, délègue la production, vérifie, rend compte.

*Relevé le 2026-09-11 au soir (D82/D104), rejoué et repris le 2026-09-12 sur l'audit
d'alignement au socle (T-013). Ce document porte l'**opératoire** : quand un chiffre est
rejouable, c'est la commande qui figure ici, pas sa valeur du jour. Ce qui n'a pas pu être joué
est marqué « non vérifié ».*

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

`/home/matt/mini-jeux/.claude/agents/` n'existe pas — le dépôt n'a aucun agent à lui, et tout
ce qu'il invoque vient de `~/.claude/agents/`, dont les liens pointent vers
`ProlexCore/SOCLE/agents/`. Le compte se rejoue, il ne se recopie pas :

```bash
ls ~/.claude/agents/ | wc -l ; ls -l ~/.claude/agents/ | head -3    # combien, et vers où
```

`orchestrateur-federe` n'est plus inerte ici depuis WP5 (2026-09-09) : le kit est posé et fédéré
(§2). Les trois `codebase-memory-*` restent **hors service** — `codebase-memory-mcp` toujours
absent (`ListMcpResourcesTool`/`.mcp.json` néant, voir §4).

`SOCLE/agents/mini-jeux-projet.md` (lien `~/.claude/agents/mini-jeux-projet.md`) est **promis au
retrait, et sa condition est remplie** : D69 le retire quand l'orchestrateur dédié de son dépôt
est posé, et D121 précise « à la fusion de l'implantation, pas à sa pose sur une branche ». La
fusion est faite — `git merge-base --is-ancestor orchestration-2026-09-11 main` rend vrai. Le
retrait lui-même vit hors de ce dépôt : il revient à ProlexCore, après que ses pièges détaillés
sont passés dans `AGENTS.md` (fait le 2026-09-12).

---

## 2. Les commandes qui prouvent

Zéro dépendance, zéro build. Les contrôles sont des fichiers autonomes, joués à la main.

### Le kit `agent-workflow` — fédéré

```bash
WORKFLOW_AGENT=<ton-nom> python3 bin/workflow.py snapshot     # tâches réservées, par qui
WORKFLOW_AGENT=<ton-nom> python3 bin/workflow.py claim/done   # réserver, clore avec --verif
python3 /home/matt/ProlexCore/SOCLE/kits/agent-workflow/installer.py . --controle
```

La version ne se recopie pas ici : `--controle` la dit, et c'est la seule à croire —
`cat .workflow/VERSION` donne l'installée, le contrôle dit si elle vaut celle du socle.

`.workflow/local.json` porte les identités que ce dépôt alloue — non versionné (gitignoré par le
kit lui-même, motif dans `.workflow/.gitignore`), lu directement par la garde A1 :

```bash
python3 -c "import json;print(json.load(open('.workflow/local.json'))['agents'])"
```

**Le suivi vit dans `backlog.md`**, généré par le kit et jamais édité à la main (D40). Le nom
`TODO.md` appartient à l'ancienne convention : il a été retiré le 2026-09-12, le kit ne l'écrivant
plus depuis la pose de la 1.23.0.

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
| `PreToolUse` / `Write\|Edit` | `gardes-shell.py --observe`, `garde-identite.py` | observent l'écriture de fichier, ne bloquent pas |
| `PostToolUse` / Skill | `log_skill_use.py` | journalise l'usage des skills |
| `SessionStart` | `injecter-revisions.py`, `garde-worktree-a-jour.py`, `indexer-sessions.py --quiet`, `ping-orchestrateurs.py --hook` | reprise, worktree, index, qui d'autre travaille |
| `SessionEnd` | `balayer-ledger.py` | balaye le registre |
| `Stop` | `reviser-session.py`, `todo-a-jour.py` | révision de fin de session, **et refus de rendre si `backlog.md` est en retard** (D86) |

La table se rejoue plutôt que se croire — le fichier porte les scripts sous `args`, pas dans
`command`, et un relevé qui lit `command` ne ramasse que « python3 » :

```bash
python3 -c "
import json
s=json.load(open('/home/matt/.claude/settings.json'))
[print(k,'|',m.get('matcher','-'),'|',' '.join(x.split('/')[-1] for x in h.get('args',[])))
 for k,v in s['hooks'].items() for m in v for h in m['hooks']]"
```

`Stop`, `SessionStart` et `SessionEnd` tiennent au cycle de la session de premier niveau : **ils
ne se déclenchent pas pour un sous-agent**. `PreToolUse`/`PostToolUse` s'appliquent à tout appel
d'outil, quel qu'en soit l'émetteur.

---

## 6. Services et infrastructure

- **Publication** : GitHub Pages sur `main`, `git@github.com:ProlexAi/mini-jeux.git`, public.
  `.nojekyll` à la racine et dans `Snake'on/` (mesuré présent ce soir). Pousser, c'est publier.
- **Aucun serveur applicatif, aucune base, aucune API.** Progression du joueur dans le
  `localStorage` du navigateur, jamais dans le dépôt.
- **Coffre Obsidian** : `Obsidian_MiniJeux/`, gitignoré, jamais publié (D85). **Son emplacement
  n'est plus une question ouverte** : D117 tranche que le coffre vit dans le dépôt, et qu'un dépôt
  public l'ignore — exactement ce qui est posé ici. Garde : `git ls-files Obsidian_MiniJeux`
  doit rendre zéro ligne.
- **Génération d'assets** : ComfyUI local, un seul LoRA actif à la fois (VRAM 16 Go). Chemin du
  dossier LoRAs — non vérifié sous Kubuntu.
- **Worktrees** : ils vivent sous `~/.worktrees/mini-jeux/<branche>` (D151 de ProlexCore, 2026-09-12), et se
  retirent dans le geste qui fusionne leur branche. `.claude/worktrees/` existe encore, vide et ignoré par Git.

---

## 7. Ce qui manque encore

| Manque | Conséquence | Le geste qui le comble |
|---|---|---|
| **`mini-jeux-scribe` écrit mais pas installé** | Inappelable — fiche dans `SOCLE/profils-agents/agents-scribes/`, aucun lien | L'installer si le besoin se confirme |
| **Aucun agent de production propre au jeu** | Personne ne sait spécifiquement lire `index.html` (monolithe) ni mener une passe de mesure navigateur sans repasser par un agent générique | Un agent « mesure dans la page » à écrire, sur le critère du contexte isolé (pas fait ce soir : hors périmètre du prompt, §4) |
| **`codebase-memory-mcp` retiré** | Trois agents de socle inertes ici (`codebase-memory-scout`, `-verify`, `-auditor`) | Réinstaller — `ProlexCore/SOCLE/mcp/README.md` |
| **Contrôles Windows injouables sous Kubuntu** | `verifie-chemins.py` ne prouve que sa branche Linux ; les `.ps1` non couverts | Les jouer depuis Windows, ou les déclarer hors périmètre |
| **`SOCLE/agents/mini-jeux-projet.md` toujours présent** | Doublonne une partie du coffre et d'`AGENTS.md`, promis au retrait par D69/D121, **condition remplie** | Le retrait vit hors de ce dépôt : proposé à ProlexCore, ses pièges désormais versés dans `AGENTS.md` |
| **La garde A1 du kit refuse les identifiants que D151 demande** | D151 veut `claude-<depot>-<tache>` pour tout agent lancé ; `.workflow/local.json` n'alloue que `claude-mini-jeux` et `git`, donc un sous-agent conforme à D151 est **bloqué** | Allouer l'identifiant de la tâche dans `local.json` avant de lancer l'agent — mesuré le 2026-09-12, un nom non alloué rend `EXIT=1` |
| **Aucune ligne d'ouverture n'énumère les skills invocables** | D149 a mesuré qu'une session voit un seul skill dans son listing alors que des dizaines sont invocables ; sans la ligne, le réflexe « ça existe déjà ? » ne peut pas jouer | `python3 /home/matt/ProlexCore/GOUVERNANCE/scripts/lister-skills-invocables.py` — porté à `CLAUDE.md` §Ouvrir le 2026-09-12 |

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
