# MODIFICATIONS DOC PROPOSÉES — mini-jeux, implantation de l'orchestration

*Étape 2 du prompt d'implantation. Posé par l'orchestrateur dédié (D66) : « tu appliques
toi-même `CLAUDE.md`, `SOUL.md` et `OUTILS.md` dans ton dépôt, par ton workflow git ; Matt relit
le diff après. » Chaque diff exact est dans l'historique git de la branche
`orchestration-2026-09-11` — pointé ici, pas recopié (D63 : « un chiffre mesuré périme, la
commande qui le rejoue non »).*

## CLAUDE.md

**Diff exact** : `git show <commit> -- CLAUDE.md` (voir le journal du jour pour les hash — deux
commits, `0091f17` puis `a90b3d0`). **Longueur** : 95 lignes (mesurée, `wc -l`). **Contrôle de
ton** : `[OK] 0 tournure punitive, 0 ligne VOIR` (`controler-ton-claude-md.py CLAUDE.md`) — obtenu
au second passage : R-09 joué ici aussi. Le premier jet omettait la règle « ne pas retraiter la
tâche d'un autre agent, ne pas relire `docs/archive/` » (trouvé en relisant mon propre rapport
d'état, qui la classait « coexistence outillée » — gardée — sans qu'elle le soit réellement dans
la pose) ; réintégrée sous une forme « `Ne jamais retraiter…` » que le contrôle a refusée
(`BLOQUANT`, tournure « ne … jamais » adressée à l'agent) ; reformulée en constat, contrôle
rejoué, vert.

**Justification en une phrase** : le fichier existant ne câblait ni `@SOUL.md` ni `@AGENTS.md`
(défaut C1 du rapport d'état — contredit D32) et ne nommait ni `JOURNAL/` (C2), ni la
contre-passe (C3), ni R-09 (C4) ; la nouvelle version câble les deux imports en tête, condense
les 9 règles de kit-hygiène existantes (aucune perdue en substance — voir le tableau du rapport
d'état §2), et ajoute les quatre manques ci-dessus comme règles écrites plutôt que pratiques
tacites.

**Ce qui est repris tel quel, en substance** : l'identité `WORKFLOW_AGENT` préfixée à chaque
commande, l'interdiction d'éditer `TODO.md`/`state.json`/`journal.jsonl` à la main, l'interdiction
de rouvrir un document archivé, l'interdiction d'une liste de suivi parallèle — condensés dans
« Ouvrir » et absorbés par la logique du kit lui-même (le fichier généré porte déjà
l'avertissement).

**Ce qui est neuf** : la section « Le jeu, et le dépôt public » (bump `CACHE_VERSION`, piège du
service worker, données personnelles hors dépôt — reprises depuis `AGENTS.md`/le coffre, pour
qu'elles soient visibles dès `CLAUDE.md` sans devoir lire deux fichiers) ; la contre-passe et
R-09 dans « Tenir le travail » ; une table de délégation (reprise du profil socle
`claude-md/mini-jeux.md`, corrigée : `orchestrateur-federe` n'est plus « en réserve », il est
opérationnel depuis WP5).

## SOUL.md

**Diff exact** : nouveau fichier (n'existait pas à la racine). **Longueur** : 70 lignes.
**Contrôle de ton** : `[OK] 0 tournure punitive, 0 ligne VOIR` — obtenu après une correction
R-09 : la première version portait 31 lignes de prose hors du chapeau « Qui tu es » (D62,
`[VOIR]`), causées par des puces Markdown repliées sur plusieurs lignes physiques que
l'instrument lit comme autant de paragraphes ; corrigée en ramenant chaque puce à une seule
ligne physique, à la forme exacte du pilote KmopBudget.

**Justification** : matière de départ `ProlexCore/SOCLE/profils-agents/soul/mini-jeux.md` (D63),
condensée de 118 à 70 lignes pour tenir le plafond D30-D38 (< 200 lignes, zéro fait mesuré hors
chapeau, deuxième personne). Perdu en chemin, volontairement : les faits mesurés inline (« WSL »,
comptes de ports, dates) — remplacés par des pointeurs (`OUTILS.md`, `AGENTS.md`) ; l'affirmation
« absence du kit agent-workflow », factuellement fausse depuis WP5. Gardé intégralement en
substance : la hiérarchie d'arbitrage à 6 rangs (section « Ce qui passe devant quoi »), l'exigence
de contre-passe sur un changement critique, la thèse « zéro dépendance », le principe
« l'instrument ment plus souvent que le code ».

## OUTILS.md

**Diff exact** : nouveau fichier. **Longueur** : 187 lignes. **Contrôle de ton** :
`[OK] 0 tournure punitive, 0 ligne VOIR`.

**Justification** : matière de départ `ProlexCore/SOCLE/profils-agents/outils/mini-jeux.md`
(relevé du 2026-09-08 21:48, commit `6a3e8bd`), **entièrement re-mesurée ce soir** plutôt que
recopiée (D63 : « c'est TOI qui le tiendras ensuite »). Changements de fond par rapport au
relevé du 2026-09-08 : le kit `agent-workflow` (absent alors, 1.22.0 fédéré maintenant),
`orchestrateur-federe` (inerte alors, opérationnel maintenant), le plugin `permafrost` (absent du
relevé précédent, activé maintenant), le coffre `Obsidian_MiniJeux/` (absent alors, posé ce
soir), la section §7 « Ce qui manque » recomptée (l'absence de `CLAUDE.md` retirée — fausse
depuis le 2026-09-09 — deux manques ajoutés : le retrait différé de `mini-jeux-projet.md`
[D69] et la richesse non remontée dans `AGENTS.md`).

## Pas de USER.md (2bis)

Conforme à D67 : `USER.md` est unique, tenu dans ProlexCore, chargé par toutes les sessions de la
machine. Aucune copie posée ici. Rien appris sur Matt ce soir qui mériterait remontée
(la session a porté sur l'infrastructure du dépôt, pas sur une préférence nouvelle de Matt).

## Coffre Obsidian (2ter)

Traité et posé : voir le rapport d'état §3 (ligne C6 pour la question adjacente du retrait de
`mini-jeux-projet.md`) et le commit `697b92c` (« D85 : coffre Obsidian du dépôt, gitignore et
vérifié »). Emplacement choisi : **dans le dépôt, gitignoré et vérifié** — motivé dans ce même
commit, écart assumé par rapport à la recommandation « hors dépôt » du gabarit, à cause du
garde-fou D104 de cette session (aucune écriture hors de `/home/matt/mini-jeux` ce soir).

## Ce qui s'applique sans attendre

Rien d'autre n'a été touché ce soir : `AGENTS.md` reste identique (ses quatre sujets sont propres
au dépôt, aucune contradiction, aucun mort trouvé — rapport d'état §2). Aucun chemin mort ni
doublon intra-lecteur trouvé dans `AGENTS.md` qui justifierait une correction indépendante des
trois surfaces posées.
