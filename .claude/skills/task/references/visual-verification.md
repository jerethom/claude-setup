# Vérification visuelle avec Playwright

## Outils disponibles

### Navigation

| Outil | Usage |
|-------|-------|
| `mcp__playwright__browser_navigate` | Naviguer vers une URL |
| `mcp__playwright__browser_navigate_back` | Retour à la page précédente |

### Capture d'état

| Outil | Usage |
|-------|-------|
| `mcp__playwright__browser_snapshot` | Capture l'arbre d'accessibilité (recommandé pour les actions) |
| `mcp__playwright__browser_take_screenshot` | Capture d'écran PNG/JPEG |
| `mcp__playwright__browser_console_messages` | Messages de la console (erreurs, warnings) |

### Interactions

| Outil | Usage |
|-------|-------|
| `mcp__playwright__browser_click` | Cliquer sur un élément |
| `mcp__playwright__browser_type` | Saisir du texte dans un champ |
| `mcp__playwright__browser_press_key` | Appuyer sur une touche |
| `mcp__playwright__browser_select_option` | Sélectionner dans un dropdown |
| `mcp__playwright__browser_hover` | Survoler un élément |
| `mcp__playwright__browser_drag` | Glisser-déposer |

### Formulaires

| Outil | Usage |
|-------|-------|
| `mcp__playwright__browser_fill_form` | Remplir plusieurs champs d'un formulaire |
| `mcp__playwright__browser_file_upload` | Upload de fichiers |

### Gestion du navigateur

| Outil | Usage |
|-------|-------|
| `mcp__playwright__browser_resize` | Redimensionner la fenêtre (test responsive) |
| `mcp__playwright__browser_tabs` | Gérer les onglets (list, new, close, select) |
| `mcp__playwright__browser_close` | Fermer le navigateur |
| `mcp__playwright__browser_wait_for` | Attendre un texte ou un délai |

### Debug

| Outil | Usage |
|-------|-------|
| `mcp__playwright__browser_network_requests` | Voir les requêtes réseau |
| `mcp__playwright__browser_evaluate` | Exécuter du JavaScript |

## Workflow recommandé

1. **Naviguer** vers l'URL de l'application
2. **Capturer un snapshot** pour comprendre la structure de la page
3. **Vérifier les éléments** attendus sont présents
4. **Tester les interactions** critiques
5. **Vérifier la console** pour les erreurs
6. **Fermer** le navigateur

## Exemple de vérification

```
# 1. Naviguer
mcp__playwright__browser_navigate:
  url: "http://localhost:3000/dashboard"

# 2. Attendre le chargement
mcp__playwright__browser_wait_for:
  text: "Bienvenue"

# 3. Capturer l'état
mcp__playwright__browser_snapshot

# 4. Vérifier les erreurs console
mcp__playwright__browser_console_messages:
  level: "error"

# 5. Tester une interaction
mcp__playwright__browser_click:
  ref: "<ref du bouton depuis le snapshot>"
  element: "Bouton de connexion"

# 6. Fermer
mcp__playwright__browser_close
```

## Test responsive

```
# Taille mobile
mcp__playwright__browser_resize:
  width: 375
  height: 667

mcp__playwright__browser_snapshot

# Taille tablette
mcp__playwright__browser_resize:
  width: 768
  height: 1024

mcp__playwright__browser_snapshot
```

## Checklist de validation

### Lisibilité

| Critère | Vérification |
|---------|--------------|
| Contraste | Texte lisible sur le fond (ratio minimum 4.5:1) |
| Taille de police | Corps de texte >= 14-16px |
| Hiérarchie | Titres > sous-titres > paragraphes distincts |
| Espacement | Marges et padding cohérents |
| Longueur de ligne | 45-75 caractères par ligne idéalement |

### UX (Expérience utilisateur)

| Critère | Vérification |
|---------|--------------|
| Affordance | Boutons et liens clairement identifiables |
| Feedback | États hover, focus, loading visibles |
| Erreurs | Messages d'erreur clairs et actionnables |
| Navigation | Chemin utilisateur logique et prévisible |
| Performance | Temps de chargement acceptable |
| Accessibilité | Labels, aria-labels, navigation clavier |

### UI (Interface utilisateur)

| Critère | Vérification |
|---------|--------------|
| Cohérence | Même style (couleurs, fonts, espacements) partout |
| Alignement | Éléments alignés sur une grille |
| Débordement | Pas de texte/éléments qui débordent |
| États | Normal, hover, active, disabled cohérents |
| Icônes | Taille et style uniformes |
| Images | Qualité suffisante, pas de pixelisation |

## Points d'attention par type d'élément

### Boutons
- Taille cliquable suffisante (44x44px minimum sur mobile)
- Texte lisible et action claire
- États visuels distincts

### Formulaires
- Labels associés aux champs
- Indication des champs obligatoires
- Validation en temps réel si possible
- Messages d'erreur près du champ concerné

### Navigation
- Position actuelle visible
- Liens fonctionnels
- Breadcrumb si navigation profonde

### Contenu
- Titres descriptifs
- Paragraphes aérés
- Listes pour les énumérations