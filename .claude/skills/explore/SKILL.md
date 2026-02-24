---
name: explore
description: >
  Clarifie une demande utilisateur via des questions ciblées, analyse le code existant,
  puis génère un mini PRD (Product Requirements Document) structuré.
  Utiliser ce skill en amont d'une implémentation pour cadrer le périmètre et les spécifications.
argument-hint: <fonctionnalité à explorer>
disable-model-invocation: true
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - AskUserQuestion
  - mcp__demongrep__semantic_search
  - mcp__CodeGraphContext__find_code
---

# Mini PRD Generator

Explore et clarifie : **$ARGUMENTS**

## Phase 1 : Clarification

Si la demande est déjà suffisamment claire et détaillée, passe directement à la Phase 2.

Sinon, utilise `AskUserQuestion` pour comprendre rapidement :
- **Quoi** : Quelle fonctionnalité / quel problème ?
- **Pourquoi** : Quel est le besoin utilisateur ?
- **Pour qui** : Qui sont les utilisateurs cibles ?
- **Contraintes** : Limitations techniques ou business ?

**Règles :**
- 1 à 3 questions max par tour
- Questions à choix multiples quand possible (2-4 options par question)
- Arrête dès que l'essentiel est clair — ne pose pas de questions dont la réponse est évidente

## Phase 2 : Analyse du code existant

Commence par lire `CLAUDE.md` à la racine du projet pour comprendre l'architecture, les conventions et les outils disponibles.

Ensuite, explore méthodiquement le code pour identifier :

1. **Architecture concernée** : Quels modules/couches sont impactés ?
   - Utilise `Glob` pour localiser les fichiers pertinents
   - Utilise `Grep` pour trouver les patterns et références existants
2. **Patterns existants** : Comment des fonctionnalités similaires sont-elles déjà implémentées ?
   - Utilise `mcp__demongrep__semantic_search` pour trouver du code sémantiquement proche
   - Utilise `mcp__CodeGraphContext__find_code` pour explorer les relations entre composants
3. **Points d'intégration** : Où et comment la nouvelle fonctionnalité se branche sur l'existant ?
   - Identifie les interfaces, handlers, routes ou composants à étendre

## Phase 3 : Génération du mini PRD

Génère `.prd/PRD-{date}-{titre-court}.md` :

```markdown
# {Titre de la fonctionnalité}

## Problème
{1-2 phrases décrivant le problème à résoudre}

## Solution
{1-2 phrases décrivant la solution proposée}

## User Stories
- En tant que {persona}, je veux {action} afin de {bénéfice}

## Scope

### Inclus
- {Fonctionnalité 1}
- {Fonctionnalité 2}

### Exclus
- {Ce qui n'est pas dans le scope}

## Spécifications techniques
- **Fichiers concernés** : `chemin/fichier`
- **Dépendances** : {libs, APIs, services}
- **Contraintes** : {performance, sécurité, compatibilité}

## Critères d'acceptation
- [ ] {Critère 1}
- [ ] {Critère 2}

## Risques
| Risque | Mitigation |
|--------|------------|
| {risque} | {solution} |
```

## Finalisation

Affiche un résumé du PRD et demande :
- Valider et passer à l'implémentation
- Modifier le PRD
- Annuler

---

Pose tes premières questions pour clarifier la demande — ou passe directement à l'analyse si la demande est déjà claire.
