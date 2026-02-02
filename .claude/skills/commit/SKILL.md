---
name: commit
description: Commiter les fichiers modifiés avec un message de commit approprié basé sur l'analyse des changements.
argument-hint: [message optionnel]
disable-model-invocation: true
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
---

# Workflow de commit Git

## Protocole de sécurité Git

**IMPORTANT - Règles à respecter impérativement :**

- Ne JAMAIS modifier la configuration git
- Ne JAMAIS exécuter de commandes destructives (push --force, reset --hard, checkout ., restore ., clean -f, branch -D) sauf demande explicite
- Ne JAMAIS utiliser --no-verify ou --no-gpg-sign sauf demande explicite
- Ne JAMAIS faire de force push sur main/master
- TOUJOURS créer de NOUVEAUX commits plutôt que d'amender (sauf demande explicite)
- Ne JAMAIS pousser vers le remote sauf demande explicite de l'utilisateur

## Étape 1 : Analyse de l'état du dépôt

Exécute ces trois commandes **en parallèle** :

```bash
# Voir les fichiers modifiés et non suivis (JAMAIS -uall)
git status

# Voir les changements staged et unstaged
git diff HEAD

# Voir les messages de commit récents pour suivre le style
git log --oneline -10
```

## Étape 2 : Analyse et rédaction du message

À partir des résultats :

1. **Identifie la nature des changements** :
   - `feat:` nouvelle fonctionnalité
   - `fix:` correction de bug
   - `refactor:` refactoring sans changement de comportement
   - `docs:` documentation
   - `test:` ajout/modification de tests
   - `chore:` maintenance, dépendances, configuration
   - `style:` formatage, pas de changement de code
   - `perf:` amélioration de performance

2. **Rédige un message de commit** :
   - Première ligne : type + description concise (< 72 caractères)
   - Focalisé sur le **pourquoi**, pas le **quoi**
   - En anglais (convention standard) ou selon le style du projet

3. **Vérifie les fichiers sensibles** :
   - Ne JAMAIS commiter : `.env`, `credentials.json`, clés API, secrets
   - Avertir l'utilisateur si de tels fichiers sont détectés

## Étape 3 : Validation avec l'utilisateur

Si `$ARGUMENTS` est vide ou si les changements sont significatifs :

Utilise `AskUserQuestion` pour présenter :
- Résumé des fichiers à commiter
- Message de commit proposé
- Options : Valider / Modifier le message / Annuler

Si `$ARGUMENTS` contient un message, l'utiliser directement.

## Étape 4 : Création du commit

1. **Ajoute les fichiers pertinents** (préférer les fichiers spécifiques à `git add -A`) :

```bash
git add <fichier1> <fichier2> ...
```

2. **Crée le commit** avec HEREDOC pour un formatage correct :

```bash
git commit -m "$(cat <<'EOF'
<type>: <description>

<corps optionnel expliquant le contexte et le pourquoi>
EOF
)"
```

3. **Vérifie le succès** :

```bash
git status
```

## Étape 5 : Gestion des erreurs de pre-commit hook

Si le commit échoue à cause d'un hook pre-commit :

1. **Le commit N'A PAS eu lieu** - ne pas utiliser --amend
2. Corrige les problèmes identifiés
3. Re-stage les fichiers : `git add <fichiers>`
4. Crée un **NOUVEAU** commit (ne pas amender)

## Résultat final

Affiche :
- Le hash du commit créé
- Les fichiers inclus
- Le message de commit complet

**Rappel** : Ne pas pousser vers le remote sauf demande explicite.