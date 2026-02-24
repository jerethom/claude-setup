# Gestion des taches Claude Code

## Creer une tache

```
TaskCreate:
  subject: "Titre imperatif" (ex: "Implementer le handler CreateCase")
  description: "Description detaillee avec contexte et criteres d'acceptation"
  activeForm: "Forme progressive" (ex: "Implementant le handler CreateCase")
```

## Regles de creation

- Taches granulaires et independantes quand possible
- Une tache = une responsabilite claire
- Inclure les fichiers concernes dans la description
- Definir les dependances avec `TaskUpdate` (addBlockedBy/addBlocks)

## Cycle de vie d'une tache

### Demarrer une tache

```
TaskUpdate:
  taskId: "<id>"
  status: "in_progress"
```

### Completer une tache

```
TaskUpdate:
  taskId: "<id>"
  status: "completed"
```

### Definir les dependances

```
TaskUpdate:
  taskId: "<id>"
  addBlockedBy: ["<id_tache_prerequise>"]
```

```
TaskUpdate:
  taskId: "<id>"
  addBlocks: ["<id_tache_dependante>"]
```

## Afficher la progression

Utiliser `TaskList` regulierement pour afficher l'etat d'avancement.

Utiliser `TaskGet` avec un ID pour recuperer les details complets d'une tache.

## Selection d'agent

### Agents custom du projet

Verifie `.claude/agents/` pour les agents custom disponibles dans le projet courant.

Deux agents custom generiques sont fournis avec le skill `/task` :

| Agent | Role | Modele | Outils |
|-------|------|--------|--------|
| `analyzer` | Analyse read-only (cartographie, architecture, qualite) | haiku | Read, Glob, Grep |
| `verifier` | Verification post-implementation (format, lint, build, tests, Playwright) | sonnet | Read, Bash, Glob, Grep, Playwright |

### Agents built-in pour l'implementation

Pour l'implementation, selectionner l'agent en fonction de la zone de code :

1. **Agent custom du projet** : Si un agent custom specifique existe dans `.claude/agents/` pour la zone concernee, l'utiliser en priorite
2. **`general-purpose`** : Choix par defaut, acces a tous les outils, adapte a toute situation
3. **Agents voltagent-lang** : Pour une expertise langage specialisee :
   - `voltagent-lang:golang-pro` pour Go
   - `voltagent-lang:react-specialist` pour React
   - `voltagent-lang:typescript-pro` pour TypeScript
   - `voltagent-lang:python-pro` pour Python
   - etc. (voir la liste complete des agents disponibles)

### Principes de selection

- Toujours consulter CLAUDE.md pour les conventions et commandes du projet
- Injecter les conventions et commandes dans le prompt de delegation
- L'agent d'implementation doit executer la commande de verification appropriee avant de terminer
- En cas de doute, `general-purpose` est toujours un choix sur

## Agents specialises generiques (exploration)

| Agent | Usage |
|-------|-------|
| `Explore` | Exploration et recherche dans le code (read-only, rapide) |
| `Plan` | Planification d'implementation (read-only) |
