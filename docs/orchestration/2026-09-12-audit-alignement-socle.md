# Audit d'alignement au socle — mini-jeux, D116 à D154

*Joué le 2026-09-12 par `claude-mini-jeux` (orchestrateur dédié), tâche `T-013`, sur le prompt
d'ouverture écrit par ProlexCore et remis par Matt. Source des décisions :
`/home/matt/ProlexCore/docs/orchestrateur/DECISIONS.md`, lu ce jour.*

**Critère d'arrêt, écrit avant de commencer** : l'approche est morte si plus de 3 décisions
restent non classables faute de mesure jouable depuis ce dépôt. **Résultat : 0.** Les 38 entrées
sont classées.

---

## Ce que l'audit a trouvé, en une phrase

Ce dépôt **portait déjà** ce que les décisions de gouvernance lui demandaient sur les surfaces
(pas de gate, imports en tête, coffre au bon endroit, plafonds respectés) et **ne portait aucune**
des quatre décisions de méthode prises depuis — D148, D149, D151, D154. Les quatre sont entrées
aujourd'hui. Un cinquième écart, le plus coûteux, était un suivi en double : `TODO.md` versionné
et figé depuis le 2026-09-10, `backlog.md` vivant et non versionné.

---

## 1. Le classement des 38 décisions

`D150` n'existe pas comme entrée : sa première rédaction a été reprise et absorbée dans **D148**,
qui le dit lui-même. Les commits datés qui citent « D150 » visent D148.

### Portées par ce dépôt avant cette session — 6

| # | Objet | Ce qui l'établit |
|---|---|---|
| D116 | La gate locale sur les surfaces d'ordres tombe ; le canon reste à Matt | Aucune gate dans les quatre surfaces — `grep "validation préalable\|sous gate"` rend une seule ligne, `CLAUDE.md:77`, qui dit **l'inverse** (« tu le crées sans validation préalable »). Le canon reste nommé à Matt : `SOUL.md:63` |
| D117 | Le coffre Obsidian vit dans le dépôt, ignoré si le dépôt est public | `Obsidian_MiniJeux/` présent, `git ls-files Obsidian_MiniJeux` rend 0 ligne, `git check-ignore -v` pointe `.gitignore:39` |
| D119 | Un `CLAUDE.md` court suffit si `AGENTS.md` porte les règles ; R-09 doit être chargé | `CLAUDE.md` porte R-09 à la ligne 33, et importe `@AGENTS.md` |
| D120 | Le plafond de 200 lignes ne vaut pas pour `OUTILS.md` | `OUTILS.md` suit la grille `OUTILS_MIN/MAX_LIGNES = 120, 360` (`controler-ton-claude-md.py:185`) et rend `[OK]` |
| D124 | Un commentaire HTML avant les imports respecte D32 | `head -2 CLAUDE.md` rend `@SOUL.md` puis `@AGENTS.md`, sans commentaire — conforme *a fortiori* |
| D133 | Le kit passe à 1.23.0 à la fusion de la branche, pas avant | `installer.py . --controle` : socle 1.23.0, installé 1.23.0, conforme |

### Contredites, et corrigées aujourd'hui — 5

| # | L'écart mesuré | Le geste |
|---|---|---|
| D148 | La règle « une question à la fois, autant qu'il en faut » n'était portée par **aucune** des quatre surfaces — `grep -n "question"` rendait zéro ligne. ProlexCore l'avait déjà mesuré : « mini-jeux ne porte pas la règle » | Entrée à `CLAUDE.md` §Tenir le travail, avec les deux lectures fausses nommées (le plafond, le paquet) |
| D149 | Aucune ligne d'ouverture n'énumérait les skills invocables. `grep "lister-skills-invocables\|inventorier-actifs"` : zéro | `CLAUDE.md` §Ouvrir cite désormais `lister-skills-invocables.py` |
| D151 | **Partiellement portée**, et c'est la nuance : `git show 3c67233:OUTILS.md` la montre déjà à la ligne 154, posée par le commit `bf250a5`. Mais `OUTILS.md` est un inventaire, pas une surface d'ordres — aucun ordre ne la portait. Et l'identifiant dérivé de la tâche que D151 demande est **refusé par la garde A1 du kit** (voir §2) | Entrée à `CLAUDE.md` §Déléguer, avec la garde qui manquait : déclarer l'identifiant dans `.workflow/local.json` avant de lancer l'agent |
| D154 | `CLAUDE.md:16` renvoyait à `docs/archive/`, **un dossier qui n'existe pas** : `ls docs/` rend `active`, `inbox`, `migration-linux`, `orchestration`, `travaux-en-cours` | Le renvoi mort est remplacé par le test de D154 : ce qui raconte ne bouge pas, ce qui prescrit prend un bandeau daté |
| D125 | Le contrôle de ton n'avait pas été rejoué depuis le 2026-09-11 | Rejoué ce jour sur les 7 fichiers. Deux `[VOIR]` subsistent, motivés plutôt que faits taire (§3) |

### Concernées, l'action vivant hors de ce dépôt — 2

| # | État | Où va l'action |
|---|---|---|
| D121 | **Condition remplie.** `git merge-base --is-ancestor orchestration-2026-09-11 main` rend vrai. Le retrait de `SOCLE/agents/mini-jeux-projet.md` peut avoir lieu. Ses cinq pièges détaillés sont **versés dans `AGENTS.md` aujourd'hui**, avant tout retrait | À ProlexCore : le fichier vit dans `SOCLE/`, je n'écris pas hors de ce dépôt |
| D126 | T-053 et T-064, dont les livrables vivaient sur la branche, se closent à la fusion — faite en local | Au registre de ProlexCore, pas au mien : mes tâches sont `T-001` à `T-013` |

### Non concernées — 25

- **Propres à KmopBudget** (20) : D123, D129, D130, D131, D132, D134, D135, D136, D137, D138,
  D139, D140, D142, D143, D144, D145, D146, D147, D152, D153 — aucune ne nomme ce dépôt ni une
  surface qu'il porte.
- **Propres à un autre dépôt** (2) : D118 (DeepSeekHarness, `CLAUDE.md` lien symbolique), D141
  (contrat du dashboard, ProlexTalk / ProlexDashBoard).
- **Propres au socle ou à la bibliothèque de skills** (3) : D122 et D128 (triage et écriture des
  skills — ce dépôt n'a aucun skill, `.claude/skills/` n'existe pas), D127 (questions du tour 2,
  ProlexTalk / DeepSeekHarness / ProlexDashBoard).

Le compte se referme : 6 + 5 + 2 + 25 = **38**.

---

## 2. La contradiction qui mérite qu'on la nomme

**D151 demande un identifiant par tâche ; le kit installé ici ne l'alloue pas.**

- D151 : « son identifiant porte sa tâche, pas seulement son dépôt : `claude-<depot>-<tache>` ».
- `.workflow/local.json` alloue exactement deux noms : `claude-mini-jeux` et `git`.
- Mesuré dans cette session, sur ma toute première commande d'écriture :

  ```
  WORKFLOW_AGENT=MiniJeuxAgent python3 bin/workflow.py todo add …
  → WORKFLOW_AGENT vaut 'MiniJeuxAgent', que ce depot n'alloue pas.
    Noms alloues : claude-mini-jeux, git
  EXIT=1
  ```

Un sous-agent qui suit D151 à la lettre est donc **bloqué par la garde du kit**, et la garde a
raison de mordre : c'est elle qui empêche un nom inventé de réserver une surface. Les deux règles
sont bonnes ; c'est leur jonction qui manquait. Elle est écrite à `CLAUDE.md` §Déléguer :
l'identifiant se déclare dans `local.json` **avant** que l'agent parte.

Je ne tranche pas plus loin : savoir si le kit doit accepter un motif `claude-<depot>-*` plutôt
qu'une liste close est une question de socle, pas de dépôt. Elle part à ProlexCore.

---

## 3. Les deux `[VOIR]` qui restent, et pourquoi ils restent

`controler-ton-claude-md.py .` rend `EXIT=0`, « aucune tournure punitive sur 7 fichiers », avec :

- **`AGENTS.md`, 104 lignes** (grille 40-100). Le fichier vient d'absorber les cinq pièges de
  mesure qui ne vivaient que dans un sous-agent promis au retrait. Couper quatre lignes coûterait
  un piège. D125 autorise explicitement ce verdict à se coller au rendu sur `AGENTS.md`, sans
  refuser le tour ; D65 demande de motiver la ligne plutôt que de rembourrer le fichier.
- **`backlog.md`, 37 lignes** (grille 40-100). Fichier **généré** par le kit. Le rembourrer
  n'aurait pas de sens : il serait réécrit à la commande suivante.

`CLAUDE.md` et `OUTILS.md` rendent `[OK]`. Deux régressions que j'ai moi-même introduites ont été
prises par le contrôle et corrigées avant commit : `CLAUDE.md` passé à 109 lignes, et `OUTILS.md`
dont ma réécriture d'en-tête avait fait tomber la date de relevé. R-09 joué jusqu'au vert.

---

## 3bis. Ce que la contre-passe a fait tomber

Dix affirmations d'état ont été remises, **sans le raisonnement qui y mène**, à un agent qui ne
les avait pas produites. Sept tenues, une non vérifiable, **deux tombées** :

- **Un chiffre d'avance écrit en dur.** Le §5 disait « rend `0 13` ». L'agent a mesuré `0 18`, et
  au moment où j'écris ces lignes c'est `0 19` : mes six commits de la session l'ont fait bouger
  trois fois en une heure. Les deux mesures étaient justes à leur instant — le défaut est d'avoir
  recopié une valeur là où la commande devait figurer. Corrigé : le §5 porte la commande.
- **« D148, D149, D151, D154 n'apparaissaient dans aucune des quatre surfaces. »** Faux pour
  D151 : `git show 3c67233:OUTILS.md` la porte déjà, ligne 154. Le tableau du §1 disait bien
  « portée par `OUTILS.md` §6 seulement » ; c'est la formule courte qui débordait. Corrigé, et la
  ligne de D151 est reclassée en **partiellement portée**.

**La non vérifiable mérite d'être dite** : que `sync` ne réécrivait pas `TODO.md` a été mesuré
avant son retrait, par deux exécutions à mtime inchangé. Le fichier n'existant plus, personne ne
peut rejouer cette mesure — l'instrument a été consommé par le geste qu'il justifiait. Elle reste
au journal, datée, et ne vaut que pour ce qu'elle est : une mesure d'auteur, non contre-passée.

## 4. Ce qui a changé sur disque

| Commit | Geste |
|---|---|
| `e0c149b` | `OUTILS.md` réaligné : version du kit, compte des agents, table des hooks complétée de quatre lignes, coffre et retrait requalifiés, deux manques neufs inscrits |
| `959cd86` | `AGENTS.md` : les cinq pièges de mesure entrent avant que leur seule surface parte |
| `65a6a43` | `CLAUDE.md` : D148, D149, D151, D154 entrent ; le renvoi mort à `docs/archive/` sort |
| `deb432f` | Le suivi passe de `TODO.md` à `backlog.md` (D40), récupérabilité prouvée avant le retrait |

---

## 5. Ce qui reste ouvert

**Pour Matt** — chacun avec sa recommandation :

1. **Pousser `main`.** L'avance se mesure, elle ne se recopie pas — elle bouge à chaque commit :

   ```bash
   git fetch && git rev-list --left-right --count origin/main...main   # gauche = retard, droite = avance
   ```

   Onze journées de travail sont fusionnées en local et absentes d'`origin`, donc du site en
   ligne. Pousser, c'est publier. *Recommandation : pousser, mais après avoir joué les quatre
   contrôles du §9 depuis l'URL de production, et seulement si `CACHE_VERSION` a été montée —
   aucun commit de ce lot ne touche le code du jeu, donc le bump n'est pas dû, ce qui est à
   vérifier avant.*
2. **Le sort de `.workflow/local.json` face à D151** (§2). *Recommandation : laisser la garde
   close et déclarer chaque identifiant de tâche à la main — trois caractères de friction contre
   une garde qui a déjà mordu.*

**Pour ProlexCore** :

- le retrait de `SOCLE/agents/mini-jeux-projet.md` (D69/D121), désormais sans perte ;
- la clôture de T-053 et T-064 à son registre (D126) ;
- la convention `backlog.md` non uniforme dans le parc : ProlexCore le versionne, Profundus et
  ProlexTalk le laissent non suivi, DeepSeekHarness n'en a pas.
