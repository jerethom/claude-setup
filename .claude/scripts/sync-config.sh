#!/usr/bin/env bash
set -euo pipefail

MARKER_START="# >>> Claude Setup >>>"
MARKER_END="# <<< Claude Setup <<<"
SRC=".claude/config/mise.toml"

if [ ! -f mise.toml ]; then
  cp "$SRC" mise.toml
elif grep -q "$MARKER_START" mise.toml; then
  sed -i.bak "/^${MARKER_START}$/,/^${MARKER_END}$/d" mise.toml
  rm -f mise.toml.bak
  cat "$SRC" >> mise.toml
else
  cat "$SRC" >> mise.toml
fi

cp .claude/config/mcp.docker-compose.yml mcp.docker-compose.yml