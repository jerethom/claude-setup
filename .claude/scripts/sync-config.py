#!/usr/bin/env python3
"""Cross-platform config sync for Claude Setup."""
import json
import os
import shutil
import sys
from pathlib import Path

MARKER_START = "# >>> Claude Setup >>>"
MARKER_END = "# <<< Claude Setup <<<"
GI_MARKER_START = "# >>> Claude Setup - CGC ignore >>>"
GI_MARKER_END = "# <<< Claude Setup - CGC ignore <<<"

CONFIG_DIR = Path(".claude/config")


def merge_with_markers(target: Path, source: Path, marker_start: str, marker_end: str):
    """Merge source content into target using marker-delimited sections."""
    source_content = source.read_text(encoding="utf-8")

    if not target.exists():
        target.write_text(source_content, encoding="utf-8")
        return

    content = target.read_text(encoding="utf-8")
    if marker_start in content:
        # Remove old section between markers (inclusive)
        lines = content.splitlines(keepends=True)
        new_lines = []
        inside = False
        for line in lines:
            if line.rstrip("\n\r") == marker_start:
                inside = True
                continue
            if line.rstrip("\n\r") == marker_end:
                inside = False
                continue
            if not inside:
                new_lines.append(line)
        content = "".join(new_lines)

    # Append source content
    if content and not content.endswith("\n"):
        content += "\n"
    content += source_content
    target.write_text(content, encoding="utf-8")


def adapt_mcp_json(source: Path, target: Path):
    """Copy .mcp.json, adapting demongrep paths for the current platform."""
    data = json.loads(source.read_text(encoding="utf-8"))

    if sys.platform == "win32":
        data_dir = Path(os.environ["LOCALAPPDATA"]) / "claude-setup"
        demongrep_bin = str(data_dir / "demongrep" / "target" / "release" / "demongrep.exe")
        if "demongrep" in data.get("mcpServers", {}):
            data["mcpServers"]["demongrep"]["command"] = "cmd"
            data["mcpServers"]["demongrep"]["args"] = ["/c", f"{demongrep_bin} mcp ."]

    target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_gitignore(cgcignore: Path):
    """Merge .cgcignore content into .gitignore with markers."""
    gitignore = Path(".gitignore")

    if not gitignore.exists():
        gitignore.write_text("", encoding="utf-8")
    elif GI_MARKER_START in gitignore.read_text(encoding="utf-8"):
        # Remove old section
        content = gitignore.read_text(encoding="utf-8")
        lines = content.splitlines(keepends=True)
        new_lines = []
        inside = False
        for line in lines:
            if line.rstrip("\n\r") == GI_MARKER_START:
                inside = True
                continue
            if line.rstrip("\n\r") == GI_MARKER_END:
                inside = False
                continue
            if not inside:
                new_lines.append(line)
        gitignore.write_text("".join(new_lines), encoding="utf-8")

    # Append new section
    ignore_content = cgcignore.read_text(encoding="utf-8")
    with gitignore.open("a", encoding="utf-8") as f:
        f.write(f"{GI_MARKER_START}\n")
        f.write(ignore_content)
        if not ignore_content.endswith("\n"):
            f.write("\n")
        f.write(f"{GI_MARKER_END}\n")


def main():
    # Merge mise.toml
    merge_with_markers(Path("mise.toml"), CONFIG_DIR / "mise.toml", MARKER_START, MARKER_END)

    # Copy config files
    shutil.copy2(CONFIG_DIR / "mcp.docker-compose.yml", "mcp.docker-compose.yml")
    shutil.copy2(CONFIG_DIR / ".cgcignore", ".cgcignore")

    # Adapt and copy .mcp.json
    adapt_mcp_json(CONFIG_DIR / ".mcp.json", Path(".mcp.json"))

    # Update .gitignore
    update_gitignore(CONFIG_DIR / ".cgcignore")


if __name__ == "__main__":
    main()