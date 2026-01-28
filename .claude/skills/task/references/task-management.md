# Gestion des tâches Claude Code

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

Utiliser `TaskList` régulièrement pour afficher l'état d'avancement.

Utiliser `TaskGet` avec un ID pour récupérer les détails complets d'une tâche.

## Agents spécialisés disponibles

Utiliser l'outil `Task` avec le `subagent_type` approprié :

| Agent | Usage |
|-------|-------|
| `Explore` | Exploration et recherche dans le code |
| `Plan` | Planification d'implémentation |
| `general-purpose` | Tâches générales multi-outils |
| Agents voltagent-* | Agents spécialisés par domaine |

Les agents ont accès à tous les outils : Read, Write, Edit, Bash, Glob, Grep, et outils MCP.