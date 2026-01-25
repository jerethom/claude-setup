#!/bin/bash
set -e

REPO_URL="https://github.com/jerethom/claude-setup"
REPO_NAME="claude-setup"
TEMP_DIR=$(mktemp -d)

# Nettoyage en cas d'erreur ou d'interruption
cleanup() {
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

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

# Copier le dossier .claude à la racine du projet courant (supprime l'ancien si existant)
echo "📁 Copie de la configuration .claude..."
if [ -d .claude ]; then
    rm -rf .claude
    echo "   (ancienne configuration remplacée)"
fi
cp -r "$TEMP_DIR/$REPO_NAME/.claude" .

# Copier les fichiers de config à la racine (écrase si existant)
echo "📋 Copie des fichiers de configuration..."
cp "$TEMP_DIR/$REPO_NAME/.claude/config/mise.toml" ./mise.toml
cp "$TEMP_DIR/$REPO_NAME/.claude/config/mcp.docker-compose.yml" ./mcp.docker-compose.yml
cp "$TEMP_DIR/$REPO_NAME/.claude/config/.cgcignore" ./.cgcignore

# Ajouter/mettre à jour le contenu de .cgcignore dans .gitignore
echo "📝 Mise à jour du .gitignore..."
MARKER_START="# >>> Claude Setup - CGC ignore >>>"
MARKER_END="# <<< Claude Setup - CGC ignore <<<"

if [ -f .gitignore ]; then
    # Supprimer l'ancienne section si elle existe (entre les marqueurs)
    if grep -q "$MARKER_START" .gitignore; then
        sed -i.bak "/$MARKER_START/,/$MARKER_END/d" .gitignore
        rm -f .gitignore.bak
        echo "   (ancienne section remplacée)"
    fi
    echo "" >> .gitignore
else
    touch .gitignore
fi

# Ajouter la nouvelle section
{
    echo "$MARKER_START"
    cat "$TEMP_DIR/$REPO_NAME/.claude/config/.cgcignore"
    echo "$MARKER_END"
} >> .gitignore

# Lancer mise setup
echo "🚀 Lancement de mise setup..."
mise run setup

echo ""
echo "✅ Installation terminée !"
echo ""
echo "Pour démarrer les serveurs MCP, lance : mise run mcps"
echo "Pour démarrer Docker (Neo4j) : mise run docker"
