---
name: task
description: >-
  Implémente des tâches techniques avec analyse du code existant, planification validée par l'utilisateur,
  et vérification automatique. Utiliser quand l'utilisateur demande d'implémenter une fonctionnalité,
  corriger un bug, refactorer du code, ou toute tâche de développement nécessitant une analyse préalable.
argument-hint: <description de la tâche>
disable-model-invocation: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Agent
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

## Quand NE PAS utiliser ce workflow

- Changement trivial (typo, rename simple, ajout d'un commentaire) → édite directement
- Question ou exploration sans implémentation → utilise `/explore`
- Tâche de commit → utilise `/commit`

## Checklist de progression

Copie cette checklist et coche au fur et à mesure :

```
Progression :
- [ ] Étape 1 : Analyse du code existant
- [ ] Étape 2 : Plan présenté et validé par l'utilisateur
- [ ] Étape 3 : Implémentation déléguée aux sous-agents
- [ ] Étape 4 : Vérification finale (checks techniques, revue de code)
```

## Étapes séquentielles

### 1. Analyse du code existant

Lance un agent `Explore` (read-only, rapide) pour analyser le code :

```
Agent:
  subagent_type: Explore
  description: "Analyser code pour $0"
  prompt: |
    Analyse approfondie du code existant pour : $ARGUMENTS

    ## Stratégie de recherche (dans cet ordre)

    ### A. Recherche sémantique — `mcp__demongrep__semantic_search`
    Commence TOUJOURS par une recherche sémantique pour trouver le code lié à la tâche.
    Fais plusieurs requêtes avec des angles différents :
    - La fonctionnalité ou le concept décrit dans la tâche
    - Les noms de domaine métier associés
    - Les patterns d'implémentation attendus (handler, service, repository, etc.)

    ### B. Graphe de code — `mcp__CodeGraphContext__find_code` et `analyze_code_relationships`
    Utilise `find_code` pour localiser les fonctions, types et structures identifiés en A.
    Puis analyse les relations avec `analyze_code_relationships` :
    - `find_callers` / `find_all_callers` : qui appelle ce code ? (impact si modifié)
    - `find_callees` / `find_all_callees` : que fait ce code ? (dépendances sortantes)
    - `find_importers` : qui importe ce module ?
    - `module_deps` : dépendances du module
    - `who_modifies` : qui modifie une variable/propriété clé
    - `class_hierarchy` / `overrides` : si du polymorphisme est impliqué

    ### C. Recherche structurelle — Glob et Grep
    Complète avec Glob/Grep pour :
    - Trouver les fichiers de test associés
    - Vérifier les conventions de nommage
    - Localiser les fichiers de configuration (mise.toml, etc.)

    ## Rapport attendu

    ### 1. Cartographie du code
    - Fichiers à modifier (par priorité) : chemin, rôle, modifications prévues
    - Fichiers de référence (patterns à suivre, conventions observées)

    ### 2. Architecture et patterns
    - Couche concernée (domain, application, infrastructure)
    - Patterns utilisés et exemples de code réutilisables avec chemin:ligne

    ### 3. Dépendances (issues du graphe de code)
    - Entrantes : appelants directs et indirects, impact si modifié
    - Sortantes : fonctions appelées, imports requis
    - Modules dépendants

    ### 4. Points d'attention
    - Risques : breaking changes, tests à mettre à jour
    - Contraintes de version (vérifier mise.toml)

    ### 5. Recommandations
    - Approche suggérée avec étapes ordonnées
```

Attends le résultat avant de continuer.

### 2. Plan et validation

Présente le plan à l'utilisateur :

**Objectif** : [Une phrase résumant ce qui sera fait]

| # | Action | Fichier | Détail |
|---|--------|---------|--------|
| 1 | Créer/Modifier/Supprimer | `chemin/fichier` | Description courte |

**Impact** :
- Tests : À créer / À modifier / Aucun
- API : Breaking change / Compatible / Aucun
- Dépendances : Nouvelles / Aucune

Ensuite :

1. Crée les tâches avec `TaskCreate` (voir [references/task-management.md](references/task-management.md))
2. Pour les tâches avec dépendances, utilise `TaskUpdate` avec `addBlockedBy`/`addBlocks`
3. **Demande validation** avec `AskUserQuestion` :
   - Valider et continuer
   - Modifier le plan
   - Annuler

### 3. Implémentation

**Tu ne codes PAS toi-même.** Délègue TOUTE l'implémentation à des sous-agents **spécialisés** dans le langage ou le domaine de la tâche.

Pour chaque tâche :

1. `TaskUpdate` → status: `in_progress`
2. Délègue à un sous-agent spécialisé avec `Agent` :
   ```
   Agent:
     subagent_type: [agent spécialisé : voltagent-lang:golang-pro, voltagent-lang:javascript-pro, voltagent-lang:react-specialist, etc.]
     description: "Implémenter [nom de la tâche]"
     model: sonnet  # ou inherit pour les tâches complexes nécessitant Opus
     prompt: |
       ## Tâche
       [Description complète]

       ## Contexte du code
       [Résumé de l'analyse : fichiers concernés, patterns à suivre, conventions]

       ## Instructions
       1. Lis les fichiers nécessaires
       2. Implémente en suivant les patterns existants du projet
       3. Vérifie les versions de langages dans mise.toml
       4. Formate avec les outils du projet (consulte mise.toml ou la config du projet)

       ## Critères de succès
       - [Critère 1]
       - [Critère 2]
   ```
3. Attends le résultat du sous-agent
4. `TaskUpdate` → status: `completed`
5. `TaskList` pour afficher la progression

**Parallélisme** : Pour les tâches indépendantes (sans dépendances), lance plusieurs agents en parallèle avec `run_in_background: true`. Pour les modifications sur les mêmes fichiers, utilise `isolation: worktree` pour éviter les conflits.

### 4. Vérification finale

Crée une tâche de vérification puis exécute les deux phases suivantes :

#### Phase A — Checks techniques (découverte automatique)

```
Découverte des commandes :
1. Lis les fichiers de configuration du projet (mise.toml, package.json, Makefile, etc.)
2. Identifie les commandes disponibles : format, lint, build, tests...
3. Exécute les commandes trouvées

Boucle de correction (max 3 itérations) :
1. Exécute toutes les commandes identifiées
2. Si erreurs → corrige automatiquement → retour à l'étape 1
3. Si succès → passe à la Phase B
```

#### Phase B — Revue de cohérence par l'agent principal

L'agent principal (toi) relis tous les fichiers modifiés et vérifie 3 dimensions :

1. **Cohérence avec le plan** : l'implémentation respecte le plan validé à l'étape 2
2. **Logique métier** : code correct, cas limites gérés
3. **Intégration** : les composants s'intègrent entre eux et avec l'existant

```
Boucle de revue (max 2 itérations) :
1. Lis tous les fichiers modifiés
2. Vérifie les 3 dimensions ci-dessus
3. Si problèmes → corrige → relance Phase A
4. Si OK → terminé
```

## Résumé final

- Tâches complétées (`TaskList`)
- Fichiers impactés
- Changements effectués
- Résultat des vérifications : checks techniques (commandes exécutées et résultats)
- Revue de cohérence : points vérifiés et corrections apportées

---

## Ressources additionnelles

- **[references/search-tools.md](references/search-tools.md)** : Outils demongrep et CodeGraphContext
- **[references/task-management.md](references/task-management.md)** : TaskCreate, TaskUpdate, agents spécialisés et options avancées
