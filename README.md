# Claude Setup

Configuration personnalisée pour Claude Code avec des outils MCP (CodeGraphContext, Demongrep) et les subagents VoltAgent.

## Installation

### macOS / Linux

Exécute cette commande à la racine de ton projet :

```bash
curl -fsSL https://raw.githubusercontent.com/jerethom/claude-setup/main/install.sh | bash
```

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/jerethom/claude-setup/main/install.ps1 | iex
```

Le script va :
- Installer [mise](https://mise.run) (si non présent)
- Copier la configuration `.claude` dans ton projet
- Copier `mise.toml`, `mcp.docker-compose.yml`, `.cgcignore` et `.mcp.json` à la racine
- Ajouter le contenu de `.cgcignore` au `.gitignore` du projet
- Lancer `mise setup` pour installer les dépendances

## Utilisation

### Démarrer les serveurs MCP

```bash
mise run docker   # Démarre Neo4j (requis pour CodeGraphContext)
mise run mcps     # Démarre CodeGraphContext et Demongrep
```

### Commandes disponibles

| Commande | Description |
|----------|-------------|
| `mise run setup` | Installation complète |
| `mise run docker` | Démarre Neo4j via Docker Compose |
| `mise run mcps` | Démarre les serveurs MCP (CGC + Demongrep) |
| `mise run cgc <cmd>` | Exécute une commande CodeGraphContext |
| `mise run demongrep <cmd>` | Exécute une commande Demongrep |

## Contenu

- **CodeGraphContext** : Analyse de code avec graphe Neo4j
- **Demongrep** : Recherche sémantique dans le code
- **VoltAgent** : Subagents spécialisés pour Claude Code

## Prérequis

- Git
- Docker (pour Neo4j)
- Connexion internet (pour l'installation)
- **Windows uniquement** : Visual Studio Build Tools (pour compiler Demongrep en Rust)
