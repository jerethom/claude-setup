# Gestion des tâches et agents

## Créer une tâche

```
TaskCreate:
  subject: "Titre impératif" (ex: "Implémenter le handler CreateCase")
  description: "Description détaillée avec contexte et critères d'acceptation"
  activeForm: "Forme progressive" (ex: "Implémentant le handler CreateCase")
```

## Règles de création

- Tâches granulaires et indépendantes quand possible
- Une tâche = une responsabilité claire
- Inclure les fichiers concernés dans la description
- Définir les dépendances avec `TaskUpdate` (addBlockedBy/addBlocks)

## Cycle de vie d'une tâche

```
pending → in_progress → completed
```

### Démarrer une tâche

```
TaskUpdate:
  taskId: "<id>"
  status: "in_progress"
```

### Compléter une tâche

```
TaskUpdate:
  taskId: "<id>"
  status: "completed"
```

### Définir les dépendances

```
TaskUpdate:
  taskId: "<id>"
  addBlockedBy: ["<id_tâche_prérequise>"]
```

```
TaskUpdate:
  taskId: "<id>"
  addBlocks: ["<id_tâche_dépendante>"]
```

## Afficher la progression

- `TaskList` : vue d'ensemble de toutes les tâches
- `TaskGet` avec un ID : détails complets d'une tâche

## Déléguer à un sous-agent avec `Agent`

> **Note** : L'outil `Task` a été renommé `Agent` en v2.1.63. Les deux noms fonctionnent.

### Paramètres de l'outil Agent

| Paramètre | Description |
|-----------|-------------|
| `subagent_type` | Type d'agent à utiliser (voir tableau ci-dessous) |
| `description` | Description courte (3-5 mots) de ce que fait l'agent |
| `prompt` | Instructions détaillées pour l'agent |
| `model` | Override de modèle : `haiku` (rapide, économique), `sonnet` (équilibré), `opus` (puissant) |
| `run_in_background` | `true` pour exécuter en arrière-plan sans bloquer |
| `isolation` | `worktree` pour travailler sur une copie isolée du repo (git worktree) |
| `mode` | Mode de permission : `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, `plan` |

### Stratégie de routage de modèle

| Tâche | Modèle recommandé |
|-------|-------------------|
| Exploration, recherche, analyse read-only | `haiku` (via agent `Explore`) |
| Implémentation standard, corrections | `sonnet` |
| Tâches complexes, architecture, refactoring majeur | `opus` (ou `inherit` si déjà sur Opus) |

### Agents spécialisés disponibles

| Agent | Usage |
|-------|-------|
| `Explore` | Exploration et recherche read-only (modèle Haiku, rapide) |
| `Plan` | Planification d'implémentation (read-only) |
| `general-purpose` | Tâches multi-étapes nécessitant tous les outils |

**Agents par langage** (`voltagent-lang:*`) :

| Agent | Usage |
|-------|-------|
| `voltagent-lang:golang-pro` | Go |
| `voltagent-lang:javascript-pro` | JavaScript |
| `voltagent-lang:typescript-pro` | TypeScript |
| `voltagent-lang:python-pro` | Python |
| `voltagent-lang:react-specialist` | React |
| `voltagent-lang:rust-engineer` | Rust |
| `voltagent-lang:sql-pro` | SQL, requêtes BDD |

**Agents par domaine** (`voltagent-core-dev:*`, `voltagent-infra:*`, etc.) :

| Agent | Usage |
|-------|-------|
| `voltagent-core-dev:backend-developer` | Backend API, services |
| `voltagent-core-dev:frontend-developer` | UI, composants frontend |
| `voltagent-core-dev:fullstack-developer` | Feature complète bout en bout |
| `voltagent-infra:devops-engineer` | CI/CD, infrastructure |
| `voltagent-qa-sec:code-reviewer` | Revue de code |
| `voltagent-qa-sec:test-automator` | Tests automatisés |
| `voltagent-qa-sec:debugger` | Diagnostic et résolution de bugs |
| `voltagent-dev-exp:refactoring-specialist` | Refactoring |
| `voltagent-data-ai:postgres-pro` | PostgreSQL |

## Bonnes pratiques de délégation

1. **Prompt détaillé** : Inclure la tâche, le contexte du code (fichiers, patterns), les instructions, et les critères de succès
2. **Contexte complet** : Transmettre les résultats de l'analyse (étape 1) au sous-agent
3. **Critères mesurables** : Définir clairement ce qui constitue un succès
4. **Un agent = une responsabilité** : Ne pas surcharger un agent avec plusieurs tâches indépendantes
5. **Parallélisme** : Lancer les tâches indépendantes en parallèle avec `run_in_background: true`
6. **Isolation** : Utiliser `isolation: worktree` quand plusieurs agents modifient le même repo
