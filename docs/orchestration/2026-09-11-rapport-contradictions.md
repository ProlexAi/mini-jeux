# Rapport de contradictions — implantation de l'orchestration, mini-jeux

*Étape 3 du prompt d'implantation. « Le rapport qui vaut l'implantation. » Déposé à la boîte
d'échange à la suite de ce document.*

## Doctrine contre dépôt — ce que la nouvelle orchestration casse ici, et ce que ça coûte

- **Condensation de la kit-hygiène.** Les 9 règles du `CLAUDE.md` existant (interdiction
  d'éditer `TODO.md`/`state.json` à la main, de rouvrir un document archivé, de dupliquer le
  suivi…) sont condensées en 4 lignes dans « Ouvrir ». **Coût** : un lecteur pressé qui ne lit
  que le nouveau `CLAUDE.md` perd la liste exhaustive et explicite des quatre interdits — il lui
  reste la logique (le fichier généré porte lui-même l'avertissement) plutôt que la liste. Risque
  faible (l'avertissement du fichier généré tient), mais réel.
- **Le coffre est posé DANS le dépôt, gitignoré — pas hors dépôt comme le gabarit le
  recommande.** Coût direct : la garde ne tient plus que sur une ligne de `.gitignore` et la
  discipline de ne jamais faire `git add -f`, quand une localisation hors dépôt l'aurait rendue
  structurellement impossible. C'est un écart assumé, imposé par le garde-fou D104 de cette
  session (aucune écriture hors de `/home/matt/mini-jeux` ce soir) et non par un choix de fond —
  **à rouvrir avec Matt** : si la voie hors-dépôt est préférée à terme, le coffre devra être
  déplacé, ce qui n'est pas un geste anodin dans Obsidian (chemins internes, liens).
- **`AGENTS.md` n'a pas été touché**, alors que `SOCLE/agents/mini-jeux-projet.md` (encore
  vivant, D69 non exécutée) porte des pièges plus détaillés (service worker fantôme nommé comme
  tel, onglet caché sous Wayland, dégradation de qualité graphique). Coût : cette richesse ne vit
  que dans un sous-agent promis au retrait et dans le coffre versé ce soir (moins visible qu'un
  `AGENTS.md` enrichi) — signalé en `OUTILS.md` §7, non corrigé ce soir (hors périmètre du prompt,
  §4).

## Dépôt contre doctrine — ce que mini-jeux a de meilleur, à remonter au gabarit

- **Le témoin vit DANS l'instrument, pas à côté.** `verifie-formes-speciales.js` refuse de
  conclure (sort en erreur) s'il n'extrait aucune forme à teinte imposée, au lieu de rendre un OK
  vide — la même logique que `~/.claude/CLAUDE.md` §2 demande en général (« un critère s'exécute
  à la source avant d'être écrit »), mais ce dépôt en a une réalisation concrète et citable.
  **Proposition** : verser cet exemple précis à `CANON/PIEGES-MESURES.md` de ProlexCore comme cas
  d'école, à côté des pièges déjà catalogués.
- **Le critère d'arrêt posé avant de commencer, honoré sans le redébattre.** L'encodeur QR
  documente explicitement sa propre faute de méthode (« le critère d'arrêt n'avait pas été posé
  avant de commencer, mais en cours de route ») — une leçon vécue, pas théorique, qui illustre
  exactement `~/.claude/CLAUDE.md` §3 (« le critère d'arrêt s'écrit avant de commencer »).
  **Proposition** : ce cas concret comme exemple dans la doctrine générale, au même endroit.
- **Le marqueur de déploiement doit être une chaîne absente de la version précédente**, sous
  peine de « réussir » en zéro seconde en mesurant la présence du fichier et non celle du
  correctif — mesuré ici deux fois (une fois où ça a raté, la boucle de vérification en ligne
  corrigée depuis). Généralisable à tout dépôt qui déploie par push simple (GitHub Pages ou
  équivalent) sans étape de build intermédiaire.
- **Quatre contrôles rejouables avec sabotage systématique avant mise en production** — la
  pratique du dépôt (chaque contrôle accepte un chemin de cible pour être rejoué sur une copie
  sabotée) préfigure exactement `AGENTS.md` §10 de ProlexCore côté gouvernance
  (« maintien à partir de 5 déclenchements sans faux positif… ») mais l'applique à un jeu, pas à
  un outil de gouvernance — un second terrain de validation pour la même idée, à citer si
  `AGENTS.md` de ProlexCore cherche un second exemple hors de son propre périmètre.

## Doctrine contre elle-même — ce qui se contredit entre PROTOCOLE-AGENTS.md, DECISIONS.md, LANGUE-COMMUNE et les gabarits

- **`PROTOCOLE-AGENTS.md` se contredit lui-même sur la validation d'un spécialiste de flotte.**
  Section « La flotte appartient à l'agent » : « **Matt valide ou améliore.** Un agent non
  validé n'existe pas. » — puis, trois paragraphes plus bas, dans le même fichier : « Depuis D66,
  le dédié crée ses spécialistes sans validation préalable et les inscrit à son `OUTILS.md` le
  jour même. » Les deux phrases coexistent, non réconciliées : la première n'a pas été retirée ni
  marquée périmée quand la seconde a été ajoutée. Un lecteur qui s'arrête à la première bullet
  croit encore devoir attendre Matt. **Proposition** : retirer ou biffer la phrase « Matt valide
  ou améliore » (le paragraphe D66 suffit et est plus récent), ou la faire pointer explicitement
  vers l'amendement.
- **`LANGUE-COMMUNE.md` affirme T-098/T-105 « encore ouvertes » alors que D81 les a closes le
  même jour.** `LANGUE-COMMUNE.md` §6 (« Matière des profils… leur forme est antérieure à
  D30-D38 **tant que T-098 et T-105 restent ouvertes** (D58) ») — mais D81 (« A-02 »), daté du
  même 2026-09-11, dit : « Déjà clos par `prolexcore-master` avant la réponse… T-098, T-105 et
  T-123, closes comme caduques (D63, D66). » `LANGUE-COMMUNE.md` n'a pas été remis à jour après
  D81 : sa condition (« tant que… restent ouvertes ») est donc fausse au moment où je la lis. Sans
  conséquence pratique ce soir (je n'ai pas attendu ces tâches pour poser mes surfaces, D66
  l'autorisant explicitement), mais un lecteur strict de `LANGUE-COMMUNE.md` seul s'y tromperait.
- **« Posé » (D66) et le déclencheur du retrait (D69) ne sont pas synchronisés sur le même
  jalon.** D66 dit qu'un dédié « pose, puis rend compte » — sans mentionner de fusion sur `main`
  comme condition. D69 dit qu'un sous-agent `*-projet.md` « se retire… quand l'orchestrateur
  dédié de son dépôt est posé », et son propre texte précise pour KmopBudget : « sa branche
  d'implantation n'est pas fusionnée, et `main` ne porte ni `SOUL.md` ni `OUTILS.md`. Le retrait
  attend donc. » — traitant donc implicitement « posé » comme « fusionné sur `main` », un sens
  plus étroit que celui de D66. J'ai suivi cette lecture implicite ce soir (`mini-jeux-projet.md`
  non retiré, ma branche n'étant pas fusionnée) par cohérence avec le seul précédent existant,
  mais **la doctrine ne le dit nulle part explicitement** — un point à trancher une fois pour
  toutes plutôt que de le déduire à chaque dépôt.
- **Le plafond « moins de 200 lignes » (`LANGUE-COMMUNE.md` §3) ne précise pas s'il vaut pour
  `OUTILS.md`.** Le seul précédent posé, `KmopBudget/OUTILS.md`, fait **232 lignes** — au-dessus
  du plafond, sans correction ni exception écrite nulle part. Mon `OUTILS.md` (187 lignes) reste
  dessous, mais par choix, pas parce que la règle l'exigeait clairement — à clarifier : le
  plafond vaut-il pour les trois surfaces, ou seulement `SOUL.md`/`CLAUDE.md` (ce qui serait
  cohérent avec la nature « inventaire » d'`OUTILS.md`, plus longue par construction) ?
