---
name: task
description: Implementer une tache technique avec analyse parallele, planification validee, implementation deleguee, et verification. Utiliser pour des taches de developpement necessitant une analyse prealable du code existant.
argument-hint: <description de la tache>
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
---

# Workflow d'implementation de tache

Implemente : **$ARGUMENTS**

## Principe fondamental : Cause racine

**Si la tache concerne la resolution d'un bug ou probleme** :
- Ne JAMAIS faire un patch ou un workaround rapide
- Toujours investiguer pour trouver la **cause racine** du probleme
- Remonter la chaine de donnees/appels jusqu'a identifier l'origine exacte
- Corriger le probleme a sa source, pas ses symptomes
- Si l'utilisateur propose un patch, expliquer pourquoi corriger la cause racine est preferable

---

## Phase 0 : Verification de l'etat initial

Avant de commencer :

1. **Verifier la reprise de session** : Lis `.task-progress.md` a la racine du projet. Si le fichier existe, affiche son contenu et demande a l'utilisateur :
   ```
   AskUserQuestion:
     - "Un checkpoint de tache precedente a ete trouve. Que faire ?"
       Options: "Reprendre la tache" / "Ignorer et recommencer"
   ```
   Si reprise, sauter directement a la phase indiquee dans le checkpoint.

2. **Verifier l'etat git** : Execute `git status --short` pour detecter des changements non commites. Si des changements existent, informe l'utilisateur brievement.

---

## Phase 1 : Analyse parallele

Lance **2 a 3 agents `analyzer` en parallele** (agent custom read-only, modele haiku) :

### Agent 1 : Cartographie des fichiers
```
Task:
  subagent_type: analyzer
  model: haiku
  description: "Cartographier fichiers pour $0"
  prompt: |
    Mission : cartographie des fichiers

    Tache a analyser : $ARGUMENTS

    Identifie :
    1. Les fichiers a modifier (avec ce qui doit changer dans chacun)
    2. Les fichiers de reference a consulter (patterns a suivre, exemples existants)

    Retourne UNIQUEMENT les tableaux markdown, pas de prose.
```

### Agent 2 : Architecture et dependances
```
Task:
  subagent_type: analyzer
  model: haiku
  description: "Analyser architecture pour $0"
  prompt: |
    Mission : architecture et dependances

    Tache a analyser : $ARGUMENTS

    Identifie :
    1. Les couches et modules concernes
    2. Les patterns utilises dans le projet
    3. Les dependances entrantes (appelants, impact si modifie)
    4. Les dependances sortantes (appeles)
    5. Les imports requis
    6. Les risques (breaking changes, tests a mettre a jour)

    Retourne UNIQUEMENT les tableaux markdown, pas de prose.
```

### Agent 3 (conditionnel) : Qualite
Lance cet agent SEULEMENT si la tache implique un refactoring ou un bug complexe :
```
Task:
  subagent_type: analyzer
  model: haiku
  description: "Analyser qualite pour $0"
  prompt: |
    Mission : qualite du code

    Tache a analyser : $ARGUMENTS

    Identifie :
    1. Fonctions complexes (complexite cyclomatique > 10)
    2. Code mort detecte dans les zones concernees
    3. Zones de refactoring potentiel

    Retourne UNIQUEMENT les tableaux markdown, pas de prose.
```

**IMPORTANT** : Lance les 2-3 agents en parallele dans un seul message avec plusieurs appels `Task`.

---

## Phase 1b : Synthese de l'analyse

Apres reception des resultats des agents analyzer, produis une **synthese compacte** (max 20 lignes) :

```markdown
### Synthese

**Fichiers a modifier** : `fichier1`, `fichier2`, ...
**Fichiers de reference** : `exemple` (pattern X), ...
**Couches** : couche1 -> couche2 -> couche3
**Pattern** : patterns identifies
**Risques** : [liste courte]
**Approche** : [1-3 etapes cles]
```

Cette synthese sera reutilisee dans les prompts de delegation (Phase 3). Ne pas transmettre les tableaux bruts aux agents d'implementation.

---

## Phase 2 : Plan, validation et checkpoint

### Presentation du plan

Presente le plan a l'utilisateur :

---

## Plan d'implementation

**Objectif** : [Une phrase resumant ce qui sera fait]

### Etapes

| # | Action | Fichier | Detail |
|---|--------|---------|--------|
| 1 | Creer/Modifier/Supprimer | `chemin/fichier` | Description courte |
| 2 | ... | ... | ... |

### Apercu des changements

**Etape 1 : [Nom]**
```
+ Ce qui sera ajoute
~ Ce qui sera modifie
- Ce qui sera supprime
```

### Impact

- **Tests** : A creer / A modifier / Aucun
- **API** : Breaking change / Compatible / Aucun
- **Dependances** : Nouvelles / Aucune

---

### Creation des taches et validation

1. Cree les taches avec `TaskCreate` (voir references/task-management.md)

2. **Demande validation** avec `AskUserQuestion` :
   - Valider et continuer
   - Modifier le plan
   - Annuler

3. **Checkpoint** : Apres validation, ecris `.task-progress.md` :
   ```markdown
   # Task Progress
   ## Tache : $ARGUMENTS
   ## Phase : 3 (implementation)
   ## Taches
   - [ ] Tache 1 : description
   - [ ] Tache 2 : description
   ## Derniere mise a jour : [timestamp]
   ```

---

## Phase 3 : Implementation deleguee

**IMPORTANT** : Tu ne dois PAS coder toi-meme. Delegue TOUTE l'implementation aux agents specialises.

### Selection dynamique de l'agent

Pour chaque tache, determine l'agent appropriate :

1. **Verifie les agents custom du projet** : Lis `.claude/agents/` pour voir si un agent custom correspond a la zone de code
2. **Sinon, utilise un agent built-in** :
   - `general-purpose` comme choix par defaut (acces a tous les outils)
   - Ou un agent voltagent-lang specialise si le langage est clairement identifie (ex: `voltagent-lang:golang-pro`, `voltagent-lang:react-specialist`, `voltagent-lang:typescript-pro`, etc.)
3. **Consulte CLAUDE.md** pour extraire les conventions et commandes specifiques a injecter dans le prompt de delegation

### Pour chaque tache

1. `TaskUpdate` -> status: `in_progress`
2. **Delegue a l'agent appropriate** :

```
Task:
  subagent_type: [agent custom | general-purpose | voltagent-lang:*]
  description: "Implementer [nom de la tache]"
  prompt: |
    ## Objectif
    [Description claire de ce qui doit etre fait]

    ## Fichiers concernes
    - `chemin/fichier` : ce qui doit changer

    ## Patterns a suivre
    - Voir `chemin/exemple` pour le pattern [X]

    ## Conventions du projet
    [Extraites de CLAUDE.md : commandes de format, lint, build, repertoires generes, etc.]

    ## Contraintes
    - [Contraintes specifiques de la tache]

    ## Criteres de succes
    - [Critere 1]
    - [Critere 2]

    ## Verification
    - Consulter CLAUDE.md pour la commande de verification appropriee et l'executer avant de terminer
```

3. **Phase 3b : Verification post-tache**

   Apres le retour de chaque sous-agent, execute la commande de build/check appropriee telle que decrite dans CLAUDE.md pour la zone modifiee.

   **Strategie de recovery** (max 2 tentatives) :
   1. Si echec -> Re-delegue au meme agent avec le message d'erreur complet
   2. Si 2eme echec -> `git checkout -- [fichiers modifies]` + escalade :
      ```
      AskUserQuestion:
        - "L'implementation de [tache] a echoue 2 fois. Erreur : [message]. Que faire ?"
          Options: "Reessayer manuellement" / "Modifier l'approche" / "Abandonner cette tache"
      ```

4. `TaskUpdate` -> status: `completed`
5. **Mise a jour du checkpoint** : Coche la tache dans `.task-progress.md`
6. `TaskList` pour afficher la progression

---

## Phase 4 : Verification finale

Delegue la verification technique au `verifier` :

```
Task:
  subagent_type: verifier
  description: "Verifier qualite du code"
  prompt: |
    Verifie la qualite du code apres implementation.

    ## Zones modifiees
    [Liste des zones modifiees]

    ## Fichiers modifies
    [Liste des fichiers]

    ## Verifications a effectuer
    Consulte CLAUDE.md pour identifier les commandes de format, lint, build et test
    appropriees aux zones modifiees, puis execute-les dans l'ordre :
    1. Formatage
    2. Lint
    3. Build / Type check
    4. Tests

    Retourne un rapport structure avec le resultat de chaque verification.
```

Si le verifier remonte des erreurs de format/lint, corrige-les directement (ou re-delegue a l'agent appropriate).

---

## Phase 5 : Verification visuelle (si applicable)

**Si la tache a un impact visuel** (UI, composants frontend), delegue au `verifier` :

```
Task:
  subagent_type: verifier
  description: "Verifier visuellement l'UI"
  prompt: |
    Verifie visuellement l'implementation via Playwright.

    ## URL a verifier
    [URL ou demander a l'utilisateur]

    ## Elements attendus
    [Liste des composants/textes/interactions a verifier]

    ## Criteres
    - Lisibilite : contraste, taille police, hierarchie
    - UX : affordance, feedback, navigation
    - UI : coherence, alignement, pas de debordement
    - Console : pas d'erreurs

    Retourne un rapport structure.
```

Si l'URL n'est pas connue, demande-la d'abord a l'utilisateur avec `AskUserQuestion`.

---

## Phase 6 : Nettoyage et resume

1. **Supprime `.task-progress.md`** via Bash : `rm -f .task-progress.md`

2. **Resume final** :

```markdown
## Resume

**Taches completees** : [TaskList]
**Fichiers impactes** : [liste]
**Changements** : [description concise]
**Verifications** :
- Format : OK
- Lint : OK
- Build : OK
- Tests : OK
- Visuel : OK / N/A
```

---

## Ressources additionnelles

Consulte ces fichiers si besoin de details :

- **[references/search-tools.md](references/search-tools.md)** : Documentation des outils de recherche
- **[references/task-management.md](references/task-management.md)** : Guide TaskCreate/TaskUpdate et selection d'agents
- **[references/visual-verification.md](references/visual-verification.md)** : Guide Playwright pour la verification visuelle
