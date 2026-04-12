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

# Copier/mettre à jour le dossier .claude
if [ -d .claude ]; then
    echo "📁 Configuration existante detectee. Mise a jour intelligente..."
    python3 "$TEMP_DIR/$REPO_NAME/.claude/scripts/smart-update.py" \
        --upstream-dir "$TEMP_DIR/$REPO_NAME/.claude"
else
    echo "📁 Copie de la configuration .claude..."
    cp -r "$TEMP_DIR/$REPO_NAME/.claude" .
fi

# Copier/merger les fichiers de config à la racine
echo "📋 Synchronisation des fichiers de configuration..."
MISE_MARKER_START="# >>> Claude Setup >>>"
MISE_MARKER_END="# <<< Claude Setup <<<"
MISE_SRC=".claude/config/mise.toml"

if [ ! -f mise.toml ]; then
    cp "$MISE_SRC" ./mise.toml
elif grep -q "$MISE_MARKER_START" mise.toml; then
    sed -i.bak "/^${MISE_MARKER_START}$/,/^${MISE_MARKER_END}$/d" mise.toml
    rm -f mise.toml.bak
    cat "$MISE_SRC" >> mise.toml
    echo "   (section Claude Setup mise à jour dans mise.toml)"
else
    cat "$MISE_SRC" >> mise.toml
    echo "   (section Claude Setup ajoutée à mise.toml)"
fi

cp ".claude/config/mcp.docker-compose.yml" ./mcp.docker-compose.yml
cp ".claude/config/.cgcignore" ./.cgcignore
cp ".claude/config/.mcp.json" ./.mcp.json

# Ajouter/mettre à jour le contenu de .cgcignore dans .gitignore
echo "📝 Mise à jour du .gitignore..."
MARKER_START="# >>> Claude Setup - CGC ignore >>>"
MARKER_END="# <<< Claude Setup - CGC ignore <<<"

if [ -f .gitignore ]; then
    if grep -q "$MARKER_START" .gitignore; then
        sed -i.bak "/$MARKER_START/,/$MARKER_END/d" .gitignore
        rm -f .gitignore.bak
        echo "   (ancienne section remplacée)"
    fi
    echo "" >> .gitignore
else
    touch .gitignore
fi

{
    echo "$MARKER_START"
    cat ".claude/config/.cgcignore"
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
