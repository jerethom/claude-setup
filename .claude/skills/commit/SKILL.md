---
name: commit
description: Commiter les fichiers modifiés avec un message de commit approprié basé sur l'analyse des changements.
argument-hint: [message optionnel]
disable-model-invocation: true
allowed-tools:
  - Bash
  - Read
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

## Étape 2 : Regroupement logique des changements

À partir des résultats, **regroupe les changements par groupe logique de commit**. Chaque commit doit être **atomique et fonctionnel** :

- Un commit par fonctionnalité, correction ou refactoring distinct
- Ne pas mélanger des changements non liés dans un même commit
- Exemple : si les changements incluent un fix + un refactoring + une nouvelle feature, cela fait 3 commits séparés
- **Chaque commit doit laisser le projet dans un état fonctionnel.** Si on fait un `git checkout` sur n'importe quel commit, le code doit compiler/s'exécuter correctement. Ne jamais commiter un état intermédiaire cassé (ex : un import sans le fichier importé, une fonction appelée mais pas encore définie, une migration sans le code qui l'utilise).
- Si des fichiers sont interdépendants, ils doivent être dans le **même commit**. Préférer un commit plus gros mais fonctionnel à plusieurs petits commits cassés.

## Étape 3 : Pour chaque groupe logique, créer un commit

Répète les sous-étapes suivantes pour chaque groupe :

### 3a. Identifie la nature du groupe

   - `feat:` nouvelle fonctionnalité
   - `fix:` correction de bug
   - `refactor:` refactoring sans changement de comportement
   - `docs:` documentation
   - `test:` ajout/modification de tests
   - `chore:` maintenance, dépendances, configuration
   - `style:` formatage, pas de changement de code
   - `perf:` amélioration de performance

### 3b. Rédige un message de commit

   - Première ligne : type + description concise (< 72 caractères)
   - Focalisé sur le **pourquoi**, pas le **quoi**
   - En anglais (convention standard) ou selon le style du projet

### 3c. Vérifie les fichiers sensibles

   - Ne JAMAIS commiter : `.env`, `credentials.json`, clés API, secrets
   - Avertir l'utilisateur si de tels fichiers sont détectés

### 3d. Stage et commit

1. **Ajoute uniquement les fichiers du groupe** (préférer les fichiers spécifiques à `git add -A`) :

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

3. **Vérifie le succès** avant de passer au groupe suivant :

```bash
git status
```

## Étape 4 : Gestion des erreurs de pre-commit hook

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