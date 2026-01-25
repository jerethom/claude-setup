---
name: task
description: Implémenter une tâche technique avec analyse du code, validation du plan et vérification
argument-hint: [description de la tâche]
disable-model-invocation: true
---

Implémente la tâche suivante : $ARGUMENTS

Exécute ce workflow en 4 étapes séquentielles. Attends la fin de chaque étape avant de passer à la suivante.

## Étape 1 : Analyse du code existant

Analyse le code existant avec **demongrep** et **CodeGraphContext** :

### 1. Recherche sémantique (demongrep)

- `mcp__demongrep__semantic_search` : Recherche par similarité sémantique
- `mcp__demongrep__get_file_chunks` : Chunks indexés d'un fichier
- `mcp__demongrep__index_status` : Statut de l'index

### 2. Outils CodeGraphContext disponibles

#### Recherche de code
- `find_code` : Rechercher des snippets par mot-clé (supporte fuzzy search)

#### Analyse des relations (`analyze_code_relationships`)
Types de requêtes disponibles :
- `find_callers` : Appelants directs d'une fonction
- `find_callees` : Fonctions appelées par une fonction
- `find_all_callers` : Tous les appelants (récursif)
- `find_all_callees` : Toutes les fonctions appelées (récursif)
- `find_importers` : Fichiers qui importent un module
- `who_modifies` : Qui modifie une variable/propriété
- `class_hierarchy` : Hiérarchie d'héritage d'une classe
- `overrides` : Méthodes qui override une méthode parente
- `dead_code` : Code mort pour une cible spécifique
- `call_chain` : Chaîne d'appels entre deux fonctions
- `module_deps` : Dépendances d'un module
- `variable_scope` : Portée d'une variable
- `find_complexity` : Complexité d'une fonction
- `find_functions_by_argument` : Fonctions par type d'argument
- `find_functions_by_decorator` : Fonctions par décorateur

#### Analyse de qualité
- `find_dead_code` : Trouver le code mort global (avec exclusion de décorateurs)
- `find_most_complex_functions` : Fonctions les plus complexes
- `calculate_cyclomatic_complexity` : Complexité d'une fonction spécifique

#### Requêtes avancées
- `execute_cypher_query` : Requête Cypher directe (lecture seule)
- `visualize_graph_query` : Générer URL de visualisation Neo4j Browser

### 3. Stratégie d'analyse recommandée

1. **Recherche sémantique** : Fichiers concernés, patterns similaires
2. **Analyse des relations** : Impact amont et aval
3. **Recherche de patterns** : Modules réutilisables, conventions
4. **Qualité du code** : Fonctions complexes, code mort

## Étape 2 : Validation du plan

**ATTENDS la validation de l'utilisateur avant de passer à l'étape 3.**

Présente un plan d'implémentation :
1. **Fichiers à modifier** : Liste des fichiers impactés
2. **Modifications prévues** : Changements pour chaque fichier
3. **Impacts des changements** : Conséquences sur le reste du code
4. **Patterns réutilisés** : Patterns existants à utiliser
5. **Approche technique** : Justification des choix

Utilise `AskUserQuestion` pour demander la validation :
- Valider et continuer
- Modifier le plan
- Annuler

## Étape 3 : Implémentation

Lance un ou plusieurs agents spécialisés via `Task` avec le `subagent_type` adapté.

**Important** : Agents lancés séquentiellement, jamais en parallèle.

Chaque agent doit :
1. Recevoir les tâches du plan validé
2. Recevoir le contexte de l'étape 1 (fichiers, patterns, relations)
3. Réutiliser les patterns identifiés
4. Implémenter les modifications

## Étape 4 : Simplification et vérification

Lance un agent pour :
1. Refactoriser si nécessaire
2. Supprimer le code redondant
3. Supprimer les commentaires évidents
4. Optimiser les imports
5. Lancer le format avec mise
6. Vérifier le lint avec mise
7. Vérifier le build avec mise

## Résumé attendu

À la fin, fournis un résumé :
- **Analyse** : Découvertes de l'analyse du code
- **Fichiers impactés** : Fichiers créés, modifiés ou supprimés
- **Changements effectués** : Modifications apportées
- **Patterns réutilisés** : Conventions suivies
- **Refactoring** : Simplifications réalisées
- **Vérifications** : Résultats format, lint et build