#!/bin/bash
set -e

REPO_URL="https://github.com/jerethom/claude-setup"
REPO_NAME="claude-setup"
TEMP_DIR=$(mktemp -d)

echo "🔧 Installation du setup Claude..."

# Installer mise si non présent
if ! command -v mise &> /dev/null; then
    echo "📦 Installation de mise..."
    curl -fsSL https://mise.run | sh

    # Ajouter mise au PATH pour la session courante
    export PATH="$HOME/.local/bin:$PATH"

    echo "✅ mise installé"
else
    echo "✅ mise déjà installé"
fi

# Cloner le repo dans un dossier temporaire
echo "📥 Téléchargement de la configuration..."
git clone --depth 1 "$REPO_URL" "$TEMP_DIR/$REPO_NAME" 2>/dev/null

# Copier le dossier .claude à la racine du projet courant
echo "📁 Copie de la configuration .claude..."
cp -r "$TEMP_DIR/$REPO_NAME/.claude" .

# Copier les fichiers de config à la racine
echo "📋 Copie des fichiers de configuration..."
cp "$TEMP_DIR/$REPO_NAME/.claude/config/mise.toml" ./mise.toml
cp "$TEMP_DIR/$REPO_NAME/.claude/config/mcp.docker-compose.yml" ./mcp.docker-compose.yml

# Nettoyer le dossier temporaire
rm -rf "$TEMP_DIR"

# Lancer mise setup
echo "🚀 Lancement de mise setup..."
mise run setup

echo ""
echo "✅ Installation terminée !"
echo ""
echo "Pour démarrer les serveurs MCP, lance : mise run mcps"
echo "Pour démarrer Docker (Neo4j) : mise run docker"
