#!/usr/bin/env bash
set -euo pipefail

MARKER_START="# >>> Claude Setup >>>"
MARKER_END="# <<< Claude Setup <<<"
SRC=".claude/config/mise.toml"

# Merge mise.toml
if [ ! -f mise.toml ]; then
  cp "$SRC" mise.toml
elif grep -q "$MARKER_START" mise.toml; then
  sed -i.bak "/^${MARKER_START}$/,/^${MARKER_END}$/d" mise.toml
  rm -f mise.toml.bak
  cat "$SRC" >> mise.toml
else
  cat "$SRC" >> mise.toml
fi

# Copy config files to project root
cp .claude/config/mcp.docker-compose.yml mcp.docker-compose.yml
cp .claude/config/.cgcignore .cgcignore
cp .claude/config/.mcp.json .mcp.json

# Update .gitignore with CGC ignore section
GI_MARKER_START="# >>> Claude Setup - CGC ignore >>>"
GI_MARKER_END="# <<< Claude Setup - CGC ignore <<<"

if [ ! -f .gitignore ]; then
  touch .gitignore
elif grep -q "$GI_MARKER_START" .gitignore; then
  sed -i.bak "/^${GI_MARKER_START}$/,/^${GI_MARKER_END}$/d" .gitignore
  rm -f .gitignore.bak
fi

{
  echo "$GI_MARKER_START"
  cat .claude/config/.cgcignore
  echo "$GI_MARKER_END"
} >> .gitignore