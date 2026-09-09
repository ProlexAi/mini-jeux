# CLAUDE.md — cycle de vie (obligatoire)

Ce dépôt maintient son état par `bin/workflow.py`. Le protocole complet est dans
[AGENTS.md](AGENTS.md) — il vaut pour toi comme pour tout autre agent. Ce fichier ne
porte que ce qui t'est propre.

## En début de session, avant toute autre chose

```sh
python3 bin/workflow.py snapshot
```

Il rend les tâches réservées et par qui. **Ne retraite pas ce qui appartient à un autre
agent, et ne relis pas `docs/archive/`** : un document archivé est figé, le relire coûte
du contexte pour une information qui ne changera plus.

## Ton identité

```sh
$env:WORKFLOW_AGENT = 'claude-1'     # Windows
export WORKFLOW_AGENT=claude-1       # Linux
```

Un nom unique par session parallèle. Sans lui, le journal ne peut plus dire qui a fait
quoi — et c'est la seule chose qu'il sait faire.

## Ce que tu ne fais jamais

- Éditer `TODO.md`, `.workflow/state.json` ou `.workflow/journal.jsonl` à la main.
- Marquer une tâche `done` sans vérification réelle : passe `--verif` avec ce que tu as
  **constaté**.
- Rouvrir un document `archived` ou une tâche close — crée une tâche neuve avec
  `--corrige T-XXX`.
- Créer une liste de suivi parallèle. Un seul `TODO.md`, un seul état.

## Ce qui vaut la peine d'être tracé

```sh
python3 bin/workflow.py log "choix X car Y"
```

Ce qui reste **ouvert**, ce qui a **changé une décision**, ce qui **peut se reproduire**.
Pas un défaut corrigé dans la foulée.
