---
name: explore
description: Explorer une demande utilisateur et générer un mini PRD (Product Requirements Document).
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

Utilise `AskUserQuestion` pour comprendre rapidement :
- **Quoi** : Quelle fonctionnalité / quel problème ?
- **Pourquoi** : Quel est le besoin utilisateur ?
- **Pour qui** : Qui sont les utilisateurs cibles ?
- **Contraintes** : Limitations techniques ou business ?

**Règles :**
- 1 à 3 questions max par tour
- Questions à choix multiples quand possible
- Arrête dès que l'essentiel est clair

## Phase 2 : Analyse du code existant

Si pertinent, explore rapidement le code pour identifier :
- Les fichiers/modules concernés
- Les patterns existants à réutiliser
- Les points d'intégration

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

Pose tes premières questions pour clarifier la demande.