---
name: task
description: Implémenter une tâche technique avec analyse du code, planification validée, et vérification. Utiliser pour des tâches de développement nécessitant une analyse préalable du code existant.
argument-hint: <description de la tâche>
disable-model-invocation: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Task
  - TaskCreate
  - TaskUpdate
  - TaskList
  - TaskGet
  - AskUserQuestion
  - mcp__demongrep__semantic_search
  - mcp__demongrep__get_file_chunks
  - mcp__CodeGraphContext__find_code
  - mcp__CodeGraphContext__analyze_code_relationships
---

# Workflow d'implémentation de tâche

Implémente : **$ARGUMENTS**

## Étapes séquentielles

### 1. Analyse du code existant

Lance un agent `general-purpose` pour analyser le code :

```
Task:
  subagent_type: general-purpose
  description: "Analyser code pour $0"
  prompt: |
    Analyse le code existant pour : $ARGUMENTS

    Explore les outils disponibles (recherche sémantique, analyse de graphe de code, etc.) et utilise les plus appropriés pour cette analyse.

    ## Rapport d'analyse à retourner

    ### 1. Cartographie du code

    **Fichiers à modifier** (par ordre de priorité) :
    | Fichier | Rôle | Modifications prévues |
    |---------|------|----------------------|
    | chemin/fichier.go | Description | Ce qui doit changer |

    **Fichiers de référence** (à lire, sans modifier) :
    - `chemin/example.go` : Raison de la consultation

    ### 2. Architecture et patterns

    **Structure identifiée** :
    - Couche concernée (domain, application, infrastructure)
    - Pattern utilisé (repository, handler, service, etc.)

    **Conventions à respecter** :
    - Nommage : convention observée
    - Organisation : structure des fichiers similaires
    - Exemples de code réutilisables avec chemin:ligne

    ### 3. Analyse des dépendances

    **Dépendances entrantes** (qui appelle ce code) :
    - fonction/module → impact si modifié

    **Dépendances sortantes** (ce que ce code appelle) :
    - fonction/module utilisée

    **Imports requis** :
    - packages à importer

    ### 4. Points d'attention

    **Complexité** :
    - Fonctions complexes identifiées (score > 10)
    - Zones de refactoring potentiel

    **Risques** :
    - Breaking changes possibles
    - Tests existants à mettre à jour
    - Code mort détecté

    ### 5. Recommandations

    **Approche suggérée** :
    1. Étape 1 : action
    2. Étape 2 : action

    **Alternatives considérées** :
    - Option B : avantages/inconvénients
```

Attends le résultat avant de continuer.

### 2. Plan et validation

Présente le plan à l'utilisateur dans ce format lisible :

---

## 📋 Plan d'implémentation

**Objectif** : [Une phrase résumant ce qui sera fait]

### Étapes

| # | Action | Fichier | Détail |
|---|--------|---------|--------|
| 1 | Créer/Modifier/Supprimer | `chemin/fichier.go` | Description courte |
| 2 | ... | ... | ... |

### Aperçu des changements

**Étape 1 : [Nom de l'étape]**
```
+ Ce qui sera ajouté (résumé)
~ Ce qui sera modifié
- Ce qui sera supprimé
```

**Étape 2 : [Nom de l'étape]**
```
...
```

### Impact

- **Tests** : À créer / À modifier / Aucun
- **API** : Breaking change / Compatible / Aucun
- **Dépendances** : Nouvelles / Aucune

---

Ensuite :

1. Crée les tâches avec `TaskCreate` (voir references/task-management.md)

2. **Demande validation** avec `AskUserQuestion` :
   - Valider et continuer
   - Modifier le plan
   - Annuler

### 3. Implémentation

**IMPORTANT** : Tu ne dois PAS coder toi-même. Délègue TOUTE l'implémentation à un sous-agent **spécialisé** dans le langage ou le domaine de la tâche (ex: agent Go pour du Go, agent React pour du React, etc.).

Pour chaque tâche :

1. `TaskUpdate` → status: `in_progress`
2. **Délègue à un sous-agent spécialisé** avec `Task` :
   ```
   Task:
     subagent_type: [agent spécialisé adapté au langage/domaine]
     description: "Implémenter [nom de la tâche]"
     prompt: |
       ## Tâche à implémenter
       [Description complète de la tâche]

       ## Contexte du code
       [Résumé de l'analyse de l'étape 1 : fichiers concernés, patterns à suivre]

       ## Instructions
       1. Lis les fichiers nécessaires
       2. Implémente le code en suivant les patterns existants
       3. Formate avec : mise exec -- go tool golines -w <fichier.go>

       ## Critères de succès
       - [Critère 1]
       - [Critère 2]
   ```
3. Attends le résultat du sous-agent
4. `TaskUpdate` → status: `completed`
5. `TaskList` pour afficher la progression

### 4. Vérification finale

Crée une tâche de vérification puis exécute :

1. Refactoring si nécessaire
2. Suppression du code redondant
3. Optimisation des imports
4. Format : `mise exec -- go tool golines -w <fichier.go>`
5. Lint : `mise run lint`
6. Build : `mise run build`

## Résumé final

- Tâches complétées (`TaskList`)
- Fichiers impactés
- Changements effectués
- Vérifications : format, lint, build

---

## Ressources additionnelles

Consulte ces fichiers si besoin de détails :

- **[references/search-tools.md](references/search-tools.md)** : Documentation complète des outils demongrep et CodeGraphContext
- **[references/task-management.md](references/task-management.md)** : Guide détaillé de TaskCreate, TaskUpdate et agents spécialisés