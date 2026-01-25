---
name: explore
description: Explorer et clarifier une demande utilisateur avant de proposer un plan d'action
argument-hint: [demande à explorer]
disable-model-invocation: true
---

Explore et clarifie la demande suivante : $ARGUMENTS

## Phase 1 : Contexte et Objectif

Pose des questions via `AskUserQuestion` pour comprendre :
- Le problème ou besoin à résoudre
- L'objectif final attendu
- Les contraintes (temps, budget, ressources)
- Le contexte existant (projet, équipe, environnement)

## Phase 2 : Détails Techniques

Une fois le contexte clair, pose des questions sur :
- Les technologies concernées ou souhaitées
- L'architecture existante ou cible
- Les dépendances et intégrations
- Les critères de succès techniques

## Règles

1. **Utilise TOUJOURS** `AskUserQuestion` pour poser tes questions
2. **Pose 1 à 4 questions à la fois** sous forme de choix multiples
3. **Continue** tant que tu n'as pas suffisamment d'informations
4. **Ne propose JAMAIS de plan** avant d'avoir clarifié tous les points ambigus

## Critères de complétude

Tu as assez d'informations quand tu connais :
- L'objectif précis et mesurable
- Le contexte technique (langages, frameworks, architecture)
- Les contraintes et limitations
- Les critères d'acceptation
- Les risques potentiels identifiés

## Phase 3 : Revue par agents spécialisés

Quand tous les critères sont remplis, **AVANT d'écrire le plan** :

1. **Identifie les domaines concernés** (frontend, backend, infrastructure, sécurité, etc.)

2. **Lance les agents pertinents en parallèle** via `Task`. Chaque agent doit :
   - Identifier les points faibles dans son domaine
   - Suggérer des améliorations techniques
   - Poser des questions critiques sur les choix
   - Valider la faisabilité technique

3. **Consolide les retours** dans le plan final

4. Si des questions critiques émergent, **pose-les à l'utilisateur** via `AskUserQuestion`

## Phase 4 : Simplification du plan

Simplifie le plan :
1. Élimine la verbosité
2. Fusionne les étapes similaires
3. Utilise un langage direct
4. Conserve l'essentiel (risques, contraintes critiques)

Objectif : Un plan **concis, clair et directement exploitable**.

## Génération du plan

Génère un fichier `.plans/PLAN-{date}-{titre-court}.md` :

```markdown
# Plan : {Titre}

## Résumé
{Brève description de la demande clarifiée}

## Objectif
{Objectif précis et mesurable}

## Contexte
{Contexte technique et organisationnel}

## Revue par agents spécialisés

### {Nom agent}
- **Améliorations intégrées** : {suggestions appliquées}
- **Points d'attention** : {alertes ou recommandations}

## Contraintes
{Liste des contraintes identifiées}

## Étapes d'implémentation
1. {Étape 1}
2. {Étape 2}

## Fichiers concernés
- `chemin/fichier` : {description des modifications}

## Risques et mitigations
| Risque | Impact | Mitigation |
|--------|--------|------------|
| {risque} | {impact} | {mitigation} |

## Critères d'acceptation
- [ ] {Critère 1}
- [ ] {Critère 2}
```

Après création du fichier, affiche un résumé et demande confirmation pour passer à l'implémentation.

---

Analyse la demande et pose tes premières questions.