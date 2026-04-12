#!/usr/bin/env python3
"""Mise a jour intelligente et non-destructive de Claude Setup.

Compare les fichiers locaux .claude/ avec la version upstream et propose
un merge interactif pour les fichiers divergents.
"""
import argparse
import difflib
import filecmp
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/jerethom/claude-setup"

if sys.platform == "win32":
    LOCAL_REPO = Path(os.environ.get("LOCALAPPDATA", "")) / "claude-setup" / "repo"
else:
    LOCAL_REPO = Path.home() / ".local" / "share" / "claude-setup" / "repo"

LOCAL_CLAUDE = Path(".claude")

# ANSI colors
if sys.platform == "win32":
    os.system("")  # enable ANSI on Windows 10+
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
RED = "\033[31m"
BOLD = "\033[1m"
NC = "\033[0m"


def pull_upstream() -> None:
    if (LOCAL_REPO / ".git").is_dir():
        subprocess.run(["git", "-C", str(LOCAL_REPO), "pull"], check=True)
    else:
        LOCAL_REPO.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", "--depth", "1", REPO_URL, str(LOCAL_REPO)], check=True
        )


def collect_files(base_dir: Path) -> set[str]:
    result = set()
    for p in base_dir.rglob("*"):
        if p.is_file() and ".git" not in p.parts:
            result.add(str(p.relative_to(base_dir)))
    return result


def is_binary(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:8192]
        return b"\x00" in chunk
    except OSError:
        return False


def classify_files(
    upstream_dir: Path,
) -> tuple[set[str], set[str], set[str], set[str]]:
    upstream_files = collect_files(upstream_dir)
    local_files = collect_files(LOCAL_CLAUDE)

    upstream_only = upstream_files - local_files
    local_only = local_files - upstream_files
    common = upstream_files & local_files

    identical = set()
    diverged = set()
    for rel in common:
        if filecmp.cmp(str(LOCAL_CLAUDE / rel), str(upstream_dir / rel), shallow=False):
            identical.add(rel)
        else:
            diverged.add(rel)

    return upstream_only, local_only, identical, diverged


def show_diff(local_path: Path, upstream_path: Path) -> None:
    if is_binary(local_path) or is_binary(upstream_path):
        print(f"  {YELLOW}[fichier binaire]{NC}")
        return

    local_lines = local_path.read_text(encoding="utf-8").splitlines(keepends=True)
    upstream_lines = upstream_path.read_text(encoding="utf-8").splitlines(keepends=True)

    diff = difflib.unified_diff(
        local_lines,
        upstream_lines,
        fromfile="local",
        tofile="upstream",
    )
    for line in diff:
        if line.startswith("---") or line.startswith("+++"):
            print(f"  {BOLD}{line.rstrip()}{NC}")
        elif line.startswith("-"):
            print(f"  {RED}{line.rstrip()}{NC}")
        elif line.startswith("+"):
            print(f"  {GREEN}{line.rstrip()}{NC}")
        elif line.startswith("@@"):
            print(f"  {BLUE}{line.rstrip()}{NC}")
        else:
            print(f"  {line.rstrip()}")


def prompt_choice(rel_path: str, local_path: Path, upstream_path: Path) -> str:
    print(f"\n  {BOLD}{YELLOW}Fichier modifie: {rel_path}{NC}")
    while True:
        print(f"  [d] Voir le diff")
        print(f"  [l] Garder la version locale (defaut)")
        print(f"  [u] Utiliser la version upstream")
        try:
            choice = input(f"  Choix [d/l/u] (defaut: l) : ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return "l"
        if choice == "" or choice == "l":
            return "l"
        if choice == "u":
            return "u"
        if choice == "d":
            show_diff(local_path, upstream_path)


def show_json_diff(key: str, local_val: dict, upstream_val: dict) -> None:
    local_str = json.dumps(local_val, indent=2, ensure_ascii=False).splitlines(
        keepends=True
    )
    upstream_str = json.dumps(upstream_val, indent=2, ensure_ascii=False).splitlines(
        keepends=True
    )
    diff = difflib.unified_diff(local_str, upstream_str, fromfile="local", tofile="upstream")
    for line in diff:
        if line.startswith("---") or line.startswith("+++"):
            print(f"    {BOLD}{line.rstrip()}{NC}")
        elif line.startswith("-"):
            print(f"    {RED}{line.rstrip()}{NC}")
        elif line.startswith("+"):
            print(f"    {GREEN}{line.rstrip()}{NC}")
        elif line.startswith("@@"):
            print(f"    {BLUE}{line.rstrip()}{NC}")
        else:
            print(f"    {line.rstrip()}")


def prompt_server_choice(key: str, local_val: dict, upstream_val: dict) -> str:
    print(f"\n    {BOLD}{YELLOW}Serveur MCP divergent: {key}{NC}")
    while True:
        print(f"    [d] Voir le diff")
        print(f"    [l] Garder la version locale (defaut)")
        print(f"    [u] Utiliser la version upstream")
        try:
            choice = input(f"    Choix [d/l/u] (defaut: l) : ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return "l"
        if choice == "" or choice == "l":
            return "l"
        if choice == "u":
            return "u"
        if choice == "d":
            show_json_diff(key, local_val, upstream_val)


def merge_mcp_json(
    local_path: Path, upstream_path: Path, auto: bool = False
) -> None:
    local_data = json.loads(local_path.read_text(encoding="utf-8"))
    upstream_data = json.loads(upstream_path.read_text(encoding="utf-8"))

    local_servers = local_data.get("mcpServers", {})
    upstream_servers = upstream_data.get("mcpServers", {})

    merged = {}
    all_keys = sorted(set(local_servers) | set(upstream_servers))

    added = []
    kept_local = []

    for key in all_keys:
        if key in local_servers and key not in upstream_servers:
            merged[key] = local_servers[key]
            kept_local.append(key)
        elif key in upstream_servers and key not in local_servers:
            merged[key] = upstream_servers[key]
            added.append(key)
        elif local_servers[key] == upstream_servers[key]:
            merged[key] = local_servers[key]
        else:
            if auto:
                merged[key] = local_servers[key]
                kept_local.append(key)
                print(
                    f"    {BLUE}= {key}: version locale conservee (mode auto){NC}"
                )
            else:
                choice = prompt_server_choice(
                    key, local_servers[key], upstream_servers[key]
                )
                if choice == "u":
                    merged[key] = upstream_servers[key]
                    print(f"    {GREEN}^ {key} -> version upstream{NC}")
                else:
                    merged[key] = local_servers[key]
                    kept_local.append(key)
                    print(f"    {BLUE}= {key} -> version locale conservee{NC}")

    result = dict(upstream_data)
    result["mcpServers"] = merged
    for k in local_data:
        if k not in result:
            result[k] = local_data[k]

    local_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    if added:
        print(f"    {GREEN}+ Serveurs ajoutes: {', '.join(added)}{NC}")
    if kept_local:
        print(f"    {BLUE}= Serveurs conserves (version locale): {', '.join(kept_local)}{NC}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Mise a jour intelligente Claude Setup")
    parser.add_argument(
        "--upstream-dir",
        type=Path,
        default=None,
        help="Chemin du dossier .claude upstream (defaut: depot local cache)",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Mode non-interactif, garde la version locale pour les conflits",
    )
    args = parser.parse_args()

    print(f"\n{BLUE}{BOLD}=== Mise a jour Claude Setup ==={NC}\n")

    # Step 1: Pull upstream (skip if --upstream-dir provided)
    if args.upstream_dir:
        upstream_claude = args.upstream_dir
    else:
        print(f"{YELLOW}[1/3] Mise a jour du depot upstream...{NC}")
        pull_upstream()
        upstream_claude = LOCAL_REPO / ".claude"

    if not upstream_claude.is_dir():
        print(f"{RED}Erreur: dossier upstream introuvable: {upstream_claude}{NC}")
        sys.exit(1)

    # Step 2: Classify files
    print(f"{YELLOW}[2/3] Analyse des differences...{NC}")
    upstream_only, local_only, identical, diverged = classify_files(upstream_claude)

    print(f"\n  {GREEN}{len(identical)} fichier(s) identique(s){NC}")
    print(f"  {GREEN}{len(upstream_only)} nouveau(x) fichier(s) upstream{NC}")
    print(f"  {BLUE}{len(local_only)} fichier(s) local(aux) conserve(s){NC}")
    print(f"  {YELLOW}{len(diverged)} fichier(s) modifie(s){NC}\n")

    # Step 3a: Auto-add upstream-only files
    for rel in sorted(upstream_only):
        src = upstream_claude / rel
        dst = LOCAL_CLAUDE / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(dst))
        print(f"  {GREEN}+ {rel}{NC}")

    # Step 3b: Handle diverged files
    if diverged:
        print(f"\n{YELLOW}[3/3] Resolution des conflits...{NC}")

        for rel in sorted(diverged):
            local_file = LOCAL_CLAUDE / rel
            upstream_file = upstream_claude / rel

            # Special handling for .mcp.json
            if rel == "config/.mcp.json":
                print(f"\n  {BLUE}~ {rel} (fusion JSON des serveurs MCP){NC}")
                merge_mcp_json(local_file, upstream_file, auto=args.auto)
                continue

            if args.auto:
                print(f"  {BLUE}= {rel} -> version locale conservee (mode auto){NC}")
                continue

            choice = prompt_choice(rel, local_file, upstream_file)
            if choice == "u":
                shutil.copy2(str(upstream_file), str(local_file))
                print(f"  {GREEN}^ {rel} -> version upstream{NC}")
            else:
                print(f"  {BLUE}= {rel} -> version locale conservee{NC}")
    else:
        print(f"{GREEN}[3/3] Aucun conflit a resoudre.{NC}")

    if local_only:
        print(f"\n  {BLUE}Fichiers locaux conserves (non presents upstream):{NC}")
        for rel in sorted(local_only):
            print(f"    {BLUE}- {rel}{NC}")

    print(f"\n{GREEN}{BOLD}Mise a jour terminee !{NC}\n")


if __name__ == "__main__":
    main()
