# Outils de recherche disponibles

## 1. Recherche sémantique (demongrep)

| Outil | Usage |
|-------|-------|
| `mcp__demongrep__semantic_search` | Recherche par similarité sémantique |
| `mcp__demongrep__get_file_chunks` | Chunks indexés d'un fichier |
| `mcp__demongrep__index_status` | Statut de l'index |

## 2. CodeGraphContext

### Recherche de code

- `mcp__CodeGraphContext__find_code` : Rechercher des snippets par mot-clé (fuzzy search supporté)

### Analyse des relations

Utiliser `mcp__CodeGraphContext__analyze_code_relationships` avec ces types de requêtes :

| Type | Description |
|------|-------------|
| `find_callers` | Appelants directs d'une fonction |
| `find_callees` | Fonctions appelées par une fonction |
| `find_all_callers` | Tous les appelants (récursif) |
| `find_all_callees` | Toutes les fonctions appelées (récursif) |
| `find_importers` | Fichiers qui importent un module |
| `who_modifies` | Qui modifie une variable/propriété |
| `class_hierarchy` | Hiérarchie d'héritage d'une classe |
| `overrides` | Méthodes qui override une méthode parente |
| `dead_code` | Code mort pour une cible spécifique |
| `call_chain` | Chaîne d'appels entre deux fonctions |
| `module_deps` | Dépendances d'un module |
| `variable_scope` | Portée d'une variable |
| `find_complexity` | Complexité d'une fonction |
| `find_functions_by_argument` | Fonctions par type d'argument |
| `find_functions_by_decorator` | Fonctions par décorateur |

### Analyse de qualité

| Outil | Usage |
|-------|-------|
| `mcp__CodeGraphContext__find_dead_code` | Code mort global |
| `mcp__CodeGraphContext__find_most_complex_functions` | Fonctions les plus complexes |
| `mcp__CodeGraphContext__calculate_cyclomatic_complexity` | Complexité d'une fonction spécifique |

### Requêtes avancées

| Outil | Usage |
|-------|-------|
| `mcp__CodeGraphContext__execute_cypher_query` | Requête Cypher directe (lecture seule) |
| `mcp__CodeGraphContext__visualize_graph_query` | URL de visualisation Neo4j Browser |

## Stratégie d'analyse recommandée

1. **Recherche sémantique** : Identifier fichiers concernés et patterns similaires
2. **Analyse des relations** : Comprendre l'impact amont et aval
3. **Recherche de patterns** : Modules réutilisables et conventions
4. **Qualité du code** : Identifier fonctions complexes et code mort