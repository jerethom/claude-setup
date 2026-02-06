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
  - mcp__playwright__browser_navigate
  - mcp__playwright__browser_snapshot
  - mcp__playwright__browser_take_screenshot
  - mcp__playwright__browser_click
  - mcp__playwright__browser_type
  - mcp__playwright__browser_wait_for
  - mcp__playwright__browser_close
---

# Workflow d'implémentation de tâche

Implémente : **$ARGUMENTS**

## Principe fondamental : Cause racine

**Si la tâche concerne la résolution d'un bug ou problème** :
- Ne JAMAIS faire un patch ou un workaround rapide
- Toujours investiguer pour trouver la **cause racine** du problème
- Remonter la chaîne de données/appels jusqu'à identifier l'origine exacte
- Corriger le problème à sa source, pas ses symptômes
- Si l'utilisateur propose un patch, expliquer pourquoi corriger la cause racine est préférable

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

### 5. Vérification visuelle (si applicable)

**Si la tâche a un impact visuel** (UI, pages web, composants frontend), effectue une vérification via le navigateur :

1. **Demande l'URL à vérifier** avec `AskUserQuestion` si non fournie
2. **Navigue vers la page** :
   ```
   mcp__playwright__browser_navigate:
     url: "<URL de l'application>"
   ```
3. **Capture l'état de la page** :
   ```
   mcp__playwright__browser_snapshot
   ```
   ou pour une capture d'écran :
   ```
   mcp__playwright__browser_take_screenshot:
     type: "png"
   ```
4. **Vérifie les éléments clés** :
   - Présence des composants attendus
   - Textes et labels corrects
   - État des boutons/formulaires
5. **Teste les interactions** si nécessaire :
   - Click sur les éléments interactifs
   - Saisie dans les champs
   - Navigation entre les pages
6. **Ferme le navigateur** :
   ```
   mcp__playwright__browser_close
   ```

**Critères de validation visuelle** :
- L'UI correspond aux spécifications
- Pas d'erreurs dans la console (`browser_console_messages`)
- Les interactions fonctionnent comme prévu
- Le responsive est correct (si applicable, utiliser `browser_resize`)

**Critères de lisibilité** :
- Contraste suffisant entre texte et fond
- Taille de police lisible (minimum 14-16px pour le corps de texte)
- Hiérarchie visuelle claire (titres, sous-titres, paragraphes)
- Espacement cohérent entre les éléments

**Critères UX** :
- Affordance des éléments interactifs (boutons reconnaissables, liens clairs)
- Feedback visuel sur les actions (hover, focus, loading states)
- Messages d'erreur clairs et utiles
- Navigation intuitive et prévisible
- Temps de réponse acceptable

**Critères UI** :
- Cohérence visuelle (couleurs, typographie, espacements)
- Alignement correct des éléments
- Pas d'éléments qui débordent ou se chevauchent
- Icônes et images de qualité appropriée
- États visuels cohérents (normal, hover, active, disabled)

## Résumé final

- Tâches complétées (`TaskList`)
- Fichiers impactés
- Changements effectués
- Vérifications : format, lint, build
- Vérification visuelle : résultat (si applicable)

---

## Ressources additionnelles

Consulte ces fichiers si besoin de détails :

- **[references/search-tools.md](references/search-tools.md)** : Documentation complète des outils demongrep et CodeGraphContext
- **[references/task-management.md](references/task-management.md)** : Guide détaillé de TaskCreate, TaskUpdate et agents spécialisés
- **[references/visual-verification.md](references/visual-verification.md)** : Guide complet des outils Playwright pour la vérification visuelle