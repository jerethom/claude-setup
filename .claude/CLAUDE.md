# Instructions

## Serveur de développement

Le serveur de développement est lancé par l'utilisateur. **Ne lance jamais le serveur de dev toi-même.**
## Exécution des commandes

Utilise **mise** pour exécuter les commandes. Préfixe les commandes avec `mise exec --` ou utilise `mise run` pour les tâches définies dans `mise.toml`.

## Versions des langages

Avant d'écrire du code, vérifie les versions des langages dans le fichier `mise.toml` à la racine du projet pour adapter la syntaxe utilisée.

## Mode Plan

En mode plan, utilise **en priorité** les outils MCP pour explorer le codebase :

- `mcp__demongrep__semantic_search` pour la recherche sémantique
- `mcp__CodeGraphContext__find_code` pour la recherche de code par mot-clé
- `mcp__CodeGraphContext__analyze_code_relationships` pour comprendre les relations entre fonctions, modules et classes

Réserve `Grep` et `Glob` comme fallback pour les recherches structurelles simples (noms de fichiers, patterns exacts).

# Instructions de Recherche

## 1. Recherche sémantique (demongrep)

- `mcp__demongrep__semantic_search` : Recherche par similarité sémantique
- `mcp__demongrep__get_file_chunks` : Chunks indexés d'un fichier
- `mcp__demongrep__index_status` : Statut de l'index

## 2. Outils CodeGraphContext disponibles

### Recherche de code
- `find_code` : Rechercher des snippets par mot-clé (supporte fuzzy search)

### Analyse des relations (`analyze_code_relationships`)
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

### Analyse de qualité
- `find_dead_code` : Trouver le code mort global (avec exclusion de décorateurs)
- `find_most_complex_functions` : Fonctions les plus complexes
- `calculate_cyclomatic_complexity` : Complexité d'une fonction spécifique

### Requêtes avancées
- `execute_cypher_query` : Requête Cypher directe (lecture seule)
- `visualize_graph_query` : Générer URL de visualisation Neo4j Browser
