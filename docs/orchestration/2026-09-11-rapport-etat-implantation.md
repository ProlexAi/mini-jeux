# Rapport d'état — implantation de l'orchestration, mini-jeux

*Session `claude-mini-jeux`, 2026-09-11 au soir. Étape 1 du prompt d'implantation (D82,
`ProlexCore/docs/orchestrateur/PROMPT-IMPLANTATION-PROJET.md`). Chaque affirmation porte sa
nature — **mesuré** (commande), **lu** (source), **déduit** (jugement) — et sa preuve.*

## 1. Surfaces existantes

**`CLAUDE.md`** — **mesuré**, 1473 octets, 44 lignes (`wc -c/-l CLAUDE.md`). Nature : **consignes
en dur, propres au cycle de vie du kit `agent-workflow`** — pas un miroir, pas quasi-vide. Il ne
porte que le kit : ouverture (`workflow.py snapshot`), identité `WORKFLOW_AGENT`, quatre
interdits (éditer `TODO.md`/`state.json`/`journal.jsonl` à la main, marquer `done` sans `--verif`,
rouvrir un document archivé, dupliquer le suivi), et `workflow.py log`.

**Qui le lit réellement** — **mesuré**, `grep -n "@" CLAUDE.md` : aucune occurrence. `CLAUDE.md`
**n'importe rien** — ni `@AGENTS.md`, ni (a fortiori) `@SOUL.md`, qui n'existe pas encore à la
racine. Il *mentionne* `AGENTS.md` en prose (« Le protocole complet est dans AGENTS.md ») mais
cette prose n'est pas un import : d'après D32 (mesuré sur onze dépôts par ProlexCore, cité dans
`PROTOCOLE-AGENTS.md`), « un ordre dépend de l'obéissance de l'agent ; un import est chargé par le
harnais » — Claude Code ne charge nativement que `<dépôt>/CLAUDE.md`. **Conséquence mesurée ici,
pas seulement déduite de D32 : une session ouverte à la racine de `mini-jeux` ne charge
`AGENTS.md` que si elle le lit elle-même** — ce que le `CLAUDE.md` actuel demande en prose sans le
garantir par le harnais. C'est un défaut réel, corrigé dans le bloc de proposition (§2ter... voir
plus bas, §3).

**`AGENTS.md`** — **mesuré**, 3768 octets, 67 lignes. Quatre sujets propres, tous confirmés à la
lecture : vérification avant merge (la séquence complète « vérification complète, si validé merge
et push », avec ses cinq réflexes de mesure — `getBoundingClientRect`, mobile 375×812, GitHub
Pages ~1 min, régression vs comportement conditionnel, canvas animé 5-10 s) ; lecture d'une
maquette Claude Design (bundle base64, décodage JSON, piège `skewX`) ; génération d'assets IA
(un seul LoRA actif, VRAM 16 Go) ; données personnelles hors dépôt (`localStorage`, jamais
versionné). **Aucun des quatre ne couvre le jeu lui-même** ni la doctrine d'orchestration : ce
sont des pièges d'outil et de process propres à ce dépôt, exactement la nature attendue
d'`AGENTS.md` (« ce qui empêche l'erreur d'OUTIL », `LANGUE-COMMUNE.md` §2).

**`SOUL.md`, `OUTILS.md`** — **mesuré**, absents à la racine (`ls SOUL.md OUTILS.md` échoue).
Matière de départ existante, non vivante (D63) : `ProlexCore/SOCLE/profils-agents/{soul,outils}/mini-jeux.md`,
**lus** en entier ce soir — datés du 2026-09-08 à 21:48, commit `6a3e8bd`. Le profil `soul/`
affirme encore l'absence du kit `agent-workflow` (faux depuis WP5, 2026-09-09) et une hiérarchie
d'arbitrage à 6 rangs sans la forme D30-D38 (prose longue, plusieurs faits mesurés inline — ports,
dates). Le profil `outils/` porte un relevé daté 2026-09-08, avec une section entière (§7, « Ce
qui manque à cet agent ») listant « Aucun `CLAUDE.md` dans le dépôt » — **faux** : `CLAUDE.md`
existe (le profil `outils/` lui-même semble contredire le profil `soul/`, qui dit à l'inverse ne
pas le porter dans la même phrase que celle citée par le prompt ; en réalité les deux profils
étaient corrects à leur date, `CLAUDE.md` ayant été posé entre-temps le 2026-09-09 par une autre
session — voir `JOURNAL/2026-09-10.md`, « Le suivi passe au kit »).

**Coffre Obsidian** — **mesuré**, absent du dépôt le 2026-09-11 avant cette session
(`find . -iname '*obsidian*'` vide). Matière de départ trouvée **hors du périmètre de lecture que
le prompt annonçait** (non citée dans son préambule « sources lues ») :
`ProlexCore/SOCLE/profils-agents/coffres/mini-jeux/`, 9 notes + accueil, 1125 lignes, même date de
revue (2026-09-08, commit `6a3e8bd`). Versé ce soir dans le dépôt, gitignoré (§2ter, détail dans
le rapport de contradictions).

## 2. Ce qui couvre déjà la doctrine

Confrontation des 9 règles de `CLAUDE.md` et des 4 sujets d'`AGENTS.md` aux cinq consignes
transverses (`LANGUE-COMMUNE.md` §4), à la contre-passe, aux boucles fermées et à la gestion du
backlog :

| Règle existante | Couvre déjà | Verdict |
|---|---|---|
| `workflow.py snapshot` en ouverture | « Ouvrir » du gabarit demande l'équivalent | **remplacement** — repris sous la forme condensée de KmopBudget |
| Ne pas éditer `TODO.md`/`state.json`/`journal.jsonl` à la main | gestion du backlog | **remplacement, condensé** — le fichier généré porte déjà l'avertissement dans son propre en-tête (`TODO.md` : « Fichier généré… Ne pas éditer à la main »), la règle est donc partiellement redondante avec l'artefact lui-même ; KmopBudget (pilote posé) ne la répète pas telle quelle non plus |
| Ne pas rouvrir un document `archived`/une tâche close | gestion du backlog | **remplacement, condensé** — même logique |
| Pas de liste de suivi parallèle | gestion du backlog | **remplacement, condensé** |
| `workflow.py log` pour ce qui reste ouvert/a changé une décision/peut se reproduire | « Journal au fil de l'eau » (consigne transverse 2) | **coexistence outillée** — le kit trace dans `.workflow/journal.jsonl` (mémoire machine), `JOURNAL/AAAA-MM-JJ.md` trace pour un lecteur humain : deux canaux, pas un doublon, mais **aucune des deux surfaces actuelles ne nomme `JOURNAL/`** (gap, voir §3) |
| Ne pas retraiter la tâche d'un autre agent, ne pas relire `docs/archive/` | réservations (`LANGUE-COMMUNE.md` §5) | **coexistence outillée** — `docs/archive/` n'existe pas encore (mesuré : `find docs -maxdepth 2 -type d` rend `active`, `inbox`, `migration-linux`, `travaux-en-cours`, pas `archive`) ; règle préventive, pas morte, gardée |
| Vérification avant merge (5 réflexes de mesure) | « Vérifier avant d'affirmer » (consigne transverse 3) | **coexistence outillée** — c'est un **approfondissement local** de la consigne générique, pas une redite : les réflexes sont propres à ce jeu (canvas, PWA, mobile). Gardé intégralement dans `AGENTS.md` |
| Maquette Claude Design, assets IA, données perso | rien de générique n'en parle | **coexistence outillée** — proprement local, aucun recouvrement |

**Compte du critère d'arrêt (§6 du gabarit)** : sur les 9 règles de `CLAUDE.md` + 4 sujets
d'`AGENTS.md` = 13 unités confrontées, **0 sortent en « reprise au gabarit »** (aucune n'est à la
fois absente de la doctrine générique ET assez générale pour y entrer — les kit-hygiène sont trop
spécifiques au kit pour enrichir `LANGUE-COMMUNE.md`, et les 4 sujets d'`AGENTS.md` sont déjà à
leur place). **9 en remplacement/condensation, 4 en coexistence outillée.** Sous la moitié :
**le critère d'arrêt ne se déclenche pas**, la passe continue à l'étape 2.

## 3. Contradictions et conflits

| # | Affirmation | Source | Verdict |
|---|---|---|---|
| C1 | `CLAUDE.md` n'importe ni `@SOUL.md` ni `@AGENTS.md` | mesuré, `grep -n "@" CLAUDE.md` → vide | **Contredit D32.** À corriger : le nouveau `CLAUDE.md` câble les deux imports en tête |
| C2 | La convention `JOURNAL/AAAA-MM-JJ.md` n'est nommée dans **aucune** surface d'ordres du dépôt | mesuré, `grep -rn "JOURNAL" CLAUDE.md AGENTS.md` → vide ; confirmé par `SOCLE/agents/mini-jeux-projet.md` : « aucune surface d'ordres ne le nomme : la convention n'est portée que par l'usage » | **Gap réel, pas une contradiction de doctrine mais un manque.** Corrigé : le nouveau `CLAUDE.md` la nomme explicitement |
| C3 | « Contre-passe » n'apparaît dans aucune des deux surfaces actuelles | mesuré, `grep -rn "contre-passe" CLAUDE.md AGENTS.md` → vide | **Le dépôt pratique déjà la contre-passe** (journal du 2026-09-10 : « Ce sont les contre-passes qui ont trouvé les vrais défauts », deux défauts réseau réels trouvés ainsi) **sans jamais l'écrire comme règle.** Corrigé dans le nouveau `CLAUDE.md` |
| C4 | R-09 (« un rendu refusé par un vérificateur repart en boucle jusqu'à passer ») absent des surfaces actuelles | mesuré, absent | Le dépôt a déjà l'équivalent en pratique — le journal du 2026-09-10 documente une boucle de contrôle (quatre contrôles rejouables, deux tenus au vert après correction). **Reprise au sens local** : R-09 entre au `CLAUDE.md` |
| C5 | `SOCLE/agents/mini-jeux-projet.md` porte des pièges opérationnels plus détaillés qu'`AGENTS.md` (service worker fantôme, onglet caché/`Wayland`, qualité graphique adaptative) | lu, sections « Le piège qui coûterait le plus cher ici » et suivantes | **Ni une contradiction ni une règle morte : un enrichissement non remonté.** `AGENTS.md` actuel couvre une partie (canvas 5-10s, mobile 375, GH Pages ~1min) mais pas le service worker fantôme ni Wayland. Signalé au rapport de contradictions (§ Dépôt contre doctrine), **pas corrigé d'office ce soir** — hors du périmètre du prompt (§4, « le reste de ton dépôt s'écrit puis se rend compte », mais une réécriture de fond d'`AGENTS.md` n'est pas demandée par ce prompt-ci) |
| C6 | D69 : « chaque `SOCLE/agents/<projet>-projet.md` se retire… quand l'orchestrateur dédié de son dépôt est posé » — appliqué à `mini-jeux-projet.md` ? | lu, D69 | **Pas encore.** Par le précédent exact de D69 sur KmopBudget (« sa branche d'implantation n'est pas fusionnée, et `main` ne porte ni `SOUL.md` ni `OUTILS.md`. Le retrait attend donc. »), et par le garde-fou D104 de cette session (branche seule, pas de fusion sur `main` ce soir), **je ne retire pas `mini-jeux-projet.md` ce soir** — même situation exacte que le pilote. Signalé comme suite (équivalent T-172 pour mini-jeux) |
| C7 | Les profils socle `soul/mini-jeux.md` et `outils/mini-jeux.md` se contredisent en apparence sur l'existence de `CLAUDE.md` | lu, les deux fichiers, §7 d'`outils/mini-jeux.md` : « Aucun `CLAUDE.md` dans le dépôt » | **Fausse contradiction : écart temporel.** Les deux profils datent du même relevé (2026-09-08 21:48, commit `6a3e8bd`) — `CLAUDE.md` n'existait alors pas encore, posé le lendemain (2026-09-09, commit `06eaca6`, `JOURNAL/2026-09-10.md`). Les deux étaient vrais à leur date ; aucun n'est à corriger, ils sont remplacés ce soir par les surfaces neuves |
| C8 | Le prompt (§0.7) demandait de commiter `.workflow/local.json` | lu, prompt §0.7 | **Prémisse périmée par la version du kit** (1.20.0/1.21.0 → 1.22.0 entre l'écriture du prompt et cette session). Mesuré : `local.json` est gitignoré au socle 1.22.0, motif documenté dans le fichier. Non commité, documenté au journal (déjà tracé en PARTIE A) |
| C9 | Le prompt (§0.8, en option) proposait `.env*` pour couvrir toute variante | lu, prompt §0.8 | **Piège d'instrument mesuré** : `.env.*` + `!.env.example` fait dire « ignoré » à `git check-ignore .env.example` (exit 0) bien que `git status --ignored` confirme le fichier suivi. Réglé par une règle plus simple, déjà tracée en PARTIE A |

## 4. Les spécificités

- **Dépôt PUBLIC servi tel quel par GitHub Pages** — **mesuré**, `.nojekyll` présent à la racine
  ET dans `Snake'on/` (`find . -name .nojekyll`). Aucune donnée personnelle, tout ce qui entre
  est publié — corollaire direct pour le coffre (§2ter) et pour `.env.example` (T-064).
- **Aucun build, aucune CI, aucun gestionnaire de paquets** — **mesuré**, ni `package.json`, ni
  `Makefile`, ni `.github/workflows/` (`find . -maxdepth 2 -iname 'package.json' -o -iname
  Makefile` vide, `.github/` absent). Le jeu se sert tel quel.
- **Le service worker sert une version fantôme pendant les tests** — **lu**,
  `SOCLE/agents/mini-jeux-projet.md`, confirmé par `Obsidian_MiniJeux/03-Travailler/Les-pieges-de-mesure-de-ce-depot.md`
  fraîchement versé. Piège déjà payé, documenté à deux endroits maintenant redondants (le sous-agent
  socle, promis au retrait par D69, et le coffre versé ce soir qui en devient la source pérenne).
- **D40 vise `backlog.md`, mais laisse l'exécution à chaque dépôt** — **lu**, D40 (citée dans le
  prompt). Mesuré ce soir (après la pose du kit 1.22.0) : `grep -rln "TODO\.md" . | grep -v
  '^\./\.git/'` rend 10 fichiers, dont `docs/orchestration/2026-09-11-rapport-etat-implantation.md`
  (ce document même, autoréférence attendue) et deux entrées de `JOURNAL/` (mentions historiques).
  Le noyau **code** cité par le prompt (`bin/workflow.py`, `workflow/atomique.py`,
  `workflow/synchro.py`, `workflow/taches.py`, `workflow/remontee.py`, `.githooks/pre-commit`,
  6 fichiers) est confirmé, **et un septième s'y est ajouté au passage 1.20.0 → 1.22.0** :
  `workflow/config.py`, absent du relevé du prompt. Plus `CLAUDE.md` lui-même, qui mentionne
  `TODO.md` en prose (§ « Ce que tu ne fais jamais »). **Écart avec le prompt, corrigé ici** : ce
  n'était donc pas « inchangé » mais **un fichier de plus à réécrire** le jour où le renommage sera
  fait — non renommé ce soir, conforme à l'instruction explicite du prompt (§4) et au garde-fou
  D104 (pas d'intention de Matt reçue sur ce point précis).
- **Aucun skill ni agent local** — **mesuré**, `.claude/agents/` et `.claude/skills/` absents
  (`find .claude -maxdepth 1 -type d`). Tout vient du socle et des plugins.
- **Hooks Git** — **mesuré**, `core.hooksPath` = `.githooks`, versionnés, pre-commit
  **consultatif** (n'écrit rien, ne bloque jamais — lu dans `SOCLE/agents/mini-jeux-projet.md`,
  non re-vérifié ligne à ligne ce soir, à confirmer si un contrôle en dépend).
