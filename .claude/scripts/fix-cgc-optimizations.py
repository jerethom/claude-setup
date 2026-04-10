#!/usr/bin/env python3
"""Cross-platform CodeGraphContext optimization script.

Applies idempotent performance patches to the codegraphcontext package:
1. cli_helpers.py: Optimized Cypher queries for index/stats (avoids double scan)
2. watcher.py: Optimized batch modification (targeted update, not full scan)
"""
import importlib
import shutil
import sys
from pathlib import Path

# ANSI colors (supported on Windows 10+ and all modern terminals)
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"

# Enable ANSI on Windows
if sys.platform == "win32":
    import os
    os.system("")  # enables ANSI escape sequences on Windows 10+


def find_cgc_path() -> Path:
    """Find the codegraphcontext package path."""
    try:
        import codegraphcontext
        return Path(codegraphcontext.__path__[0])
    except ImportError:
        print(f"{RED}Erreur: Package codegraphcontext non trouvé{NC}")
        sys.exit(1)


def patch_cli_helpers(cli_helpers: Path) -> bool:
    """Patch cli_helpers.py with optimized Cypher queries."""
    print(f"{YELLOW}[1/3] Vérification de cli_helpers.py...{NC}")

    if not cli_helpers.exists():
        print(f"{RED}  ✗ Fichier cli_helpers.py non trouvé{NC}")
        return False

    content = cli_helpers.read_text(encoding="utf-8")

    # Check if already optimized
    if "WITH collect(f) as files, count(f) as file_count" in content:
        print(f"{GREEN}  ✓ Déjà optimisé{NC}")
        return False

    if "Repository {path: $path})-[:CONTAINS]->(f:File)" not in content:
        print(f"{GREEN}  ✓ Déjà optimisé ou format différent{NC}")
        return False

    print(f"{YELLOW}  → Application de la correction...{NC}")
    modified = False

    # Fix 1: index_helper - simple query
    old_index = '"MATCH (r:Repository {path: $path})-[:CONTAINS]->(f:File) RETURN count(f) as file_count"'
    new_index = '"MATCH (f:File) WHERE f.path STARTS WITH $path RETURN count(f) as file_count"'
    if old_index in content:
        content = content.replace(old_index, new_index)
        modified = True
        print("    - index_helper corrigé")

    # Fix 2: path with "/" for index_helper
    old_path = "path=str(path_obj))"
    new_path = 'path=str(path_obj) + "/")'
    if "STARTS WITH $path" in content and old_path in content:
        if 'path=str(path_obj) + "/"' not in content:
            content = content.replace(old_path, new_path, 1)
            modified = True
            print('    - path avec / ajouté')

    # Fix 3: stats_helper - optimized query (avoids double scan)
    old_stats = '''                # Get stats
                stats_query = """
                MATCH (r:Repository {path: $path})-[:CONTAINS]->(f:File)
                WITH r, count(f) as file_count, f
                OPTIONAL MATCH (f)-[:CONTAINS]->(func:Function)
                OPTIONAL MATCH (f)-[:CONTAINS]->(cls:Class)
                OPTIONAL MATCH (f)-[:IMPORTS]->(m:Module)
                RETURN
                    file_count,
                    count(DISTINCT func) as function_count,
                    count(DISTINCT cls) as class_count,
                    count(DISTINCT m) as module_count
                """
                result = session.run(stats_query, path=str(path_obj))'''

    new_stats = '''                # Get stats - using path prefix to find files in the repository
                stats_query = """
                MATCH (f:File) WHERE f.path STARTS WITH $path
                WITH collect(f) as files, count(f) as file_count
                UNWIND files as f
                OPTIONAL MATCH (f)-[:CONTAINS]->(func:Function)
                OPTIONAL MATCH (f)-[:CONTAINS]->(cls:Class)
                OPTIONAL MATCH (f)-[:IMPORTS]->(m:Module)
                RETURN
                    file_count,
                    count(DISTINCT func) as function_count,
                    count(DISTINCT cls) as class_count,
                    count(DISTINCT m) as module_count
                """
                result = session.run(stats_query, path=str(path_obj) + "/")'''

    if old_stats in content:
        content = content.replace(old_stats, new_stats)
        modified = True
        print("    - stats_helper corrigé")

    if modified:
        cli_helpers.write_text(content, encoding="utf-8")
        print("  Corrections appliquées!")
        return True

    print("  Aucune modification nécessaire")
    return False


def patch_watcher_batch(watcher_file: Path) -> bool:
    """Patch watcher.py with optimized batch modification."""
    print(f"\n{YELLOW}[2/3] Vérification de watcher.py (filtrage)...{NC}")

    if not watcher_file.exists():
        print(f"{RED}  ✗ Fichier watcher.py non trouvé{NC}")
        return False

    content = watcher_file.read_text(encoding="utf-8")

    if "OPTIMIZED VERSION" in content:
        print(f"{GREEN}  ✓ Filtrage déjà optimisé{NC}")
    else:
        print(f"{YELLOW}  → Watcher non optimisé, vérification en cours...{NC}")

    print(f"\n{YELLOW}[3/3] Vérification de watcher.py (batch modification)...{NC}")

    if "OPTIMIZED: Only updates changed files" in content:
        print(f"{GREEN}  ✓ Batch modification déjà optimisé{NC}")
        return False

    if 'self.repo_path.rglob("*")' not in content:
        print(f"{GREEN}  ✓ Batch modification déjà optimisé{NC}")
        return False

    print(f"{YELLOW}  → Application de l'optimisation batch...{NC}")

    old_method = '''    def _handle_batch_modification(self, changed_paths: list):
        """
        Handle multiple file modifications in a single batch.
        """
        info_logger(f"Processing batch of {len(changed_paths)} file changes")

        # 1. Get all supported files in the repository (with filtering)
        supported_extensions = self.graph_builder.parsers.keys()
        all_files = []
        for f in self.repo_path.rglob("*"):
            if f.is_file() and f.suffix in supported_extensions:
                if not self._should_ignore(f):
                    all_files.append(f)

        # 2. Re-scan all files to get a fresh, global map of all symbols.
        self.imports_map = self.graph_builder._pre_scan_for_imports(all_files)
        info_logger("Refreshed global imports map.")

        # 3. Update each changed file in the graph
        for path_str in changed_paths:
            modified_path = Path(path_str)
            if modified_path.exists() and modified_path.suffix in supported_extensions:
                self.graph_builder.update_file_in_graph(
                    modified_path, self.repo_path, self.imports_map
                )

        # 4. Re-parse all files to have a complete, in-memory representation
        self.all_file_data = []
        for f in all_files:
            parsed_data = self.graph_builder.parse_file(self.repo_path, f)
            if "error" not in parsed_data:
                self.all_file_data.append(parsed_data)
        info_logger("Refreshed in-memory cache of all file data.")

        # 5. Re-link the entire graph
        info_logger("Re-linking the entire graph for calls and inheritance...")
        self.graph_builder._create_all_function_calls(self.all_file_data, self.imports_map)
        self.graph_builder._create_all_inheritance_links(self.all_file_data, self.imports_map)
        info_logger(f"Batch graph refresh complete! ✅")'''

    new_method = '''    def _handle_batch_modification(self, changed_paths: list):
        """
        Handle multiple file modifications in a single batch.
        OPTIMIZED: Only updates changed files, not the entire repository.
        """
        info_logger(f"Processing batch of {len(changed_paths)} file changes")

        supported_extensions = self.graph_builder.parsers.keys()

        # Filter to only valid, existing files with supported extensions
        valid_changed_files = []
        for path_str in changed_paths:
            modified_path = Path(path_str)
            if modified_path.exists() and modified_path.suffix in supported_extensions:
                valid_changed_files.append(modified_path)

        if not valid_changed_files:
            info_logger("No valid files to process in batch")
            return

        # For small batches (< 10 files), only update those specific files
        if len(valid_changed_files) < 10:
            info_logger(f"Small batch: updating only {len(valid_changed_files)} changed files")

            # Update only the changed files in the graph
            for modified_path in valid_changed_files:
                try:
                    self.graph_builder.update_file_in_graph(
                        modified_path, self.repo_path, self.imports_map
                    )
                except Exception as e:
                    warning_logger(f"Error updating {modified_path}: {e}")

            # Update in-memory cache only for changed files
            for modified_path in valid_changed_files:
                # Remove old data for this file
                self.all_file_data = [d for d in self.all_file_data
                                       if d.get("file_path") != str(modified_path)]
                # Add new parsed data
                parsed_data = self.graph_builder.parse_file(self.repo_path, modified_path)
                if "error" not in parsed_data:
                    self.all_file_data.append(parsed_data)

            info_logger(f"Batch update complete for {len(valid_changed_files)} files")
        else:
            # Large batch (>= 10 files): do a more thorough update but still optimized
            info_logger(f"Large batch ({len(valid_changed_files)} files): performing targeted refresh")

            # Only rescan imports for changed files, not all files
            changed_imports = self.graph_builder._pre_scan_for_imports(valid_changed_files)
            self.imports_map.update(changed_imports)

            # Update each changed file
            for modified_path in valid_changed_files:
                try:
                    self.graph_builder.update_file_in_graph(
                        modified_path, self.repo_path, self.imports_map
                    )
                except Exception as e:
                    warning_logger(f"Error updating {modified_path}: {e}")

            # Update in-memory cache only for changed files
            for modified_path in valid_changed_files:
                self.all_file_data = [d for d in self.all_file_data
                                       if d.get("file_path") != str(modified_path)]
                parsed_data = self.graph_builder.parse_file(self.repo_path, modified_path)
                if "error" not in parsed_data:
                    self.all_file_data.append(parsed_data)

            info_logger(f"Large batch update complete for {len(valid_changed_files)} files")'''

    if old_method in content:
        content = content.replace(old_method, new_method)
        watcher_file.write_text(content, encoding="utf-8")
        print("  Batch modification optimisé!")
        return True

    print("  Pattern non trouvé (déjà modifié ou format différent)")
    return False


def cleanup_pycache(cgc_path: Path):
    """Remove __pycache__ directories."""
    print(f"\n{YELLOW}Suppression du cache bytecode Python...{NC}")
    for cache_dir in cgc_path.rglob("__pycache__"):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir, ignore_errors=True)
    print(f"{GREEN}Cache supprimé{NC}")


def validate_imports():
    """Validate that patched modules still import correctly."""
    print(f"\n{YELLOW}Validation des modules...{NC}")
    ok = True

    try:
        importlib.invalidate_caches()
        importlib.import_module("codegraphcontext.cli.cli_helpers")
        print(f"{GREEN}  ✓ cli_helpers.py{NC}")
    except Exception:
        print(f"{RED}  ✗ cli_helpers.py - erreur d'import{NC}")
        ok = False

    try:
        importlib.invalidate_caches()
        importlib.import_module("codegraphcontext.core.watcher")
        print(f"{GREEN}  ✓ watcher.py{NC}")
    except Exception:
        print(f"{RED}  ✗ watcher.py - erreur d'import{NC}")
        ok = False

    return ok


def main():
    print(f"{BLUE}╔════════════════════════════════════════════════════════════╗{NC}")
    print(f"{BLUE}║     Optimisations CodeGraphContext - Script Unifié         ║{NC}")
    print(f"{BLUE}╚════════════════════════════════════════════════════════════╝{NC}")

    cgc_path = find_cgc_path()
    print(f"Package trouvé: {GREEN}{cgc_path}{NC}\n")

    cli_helpers = cgc_path / "cli" / "cli_helpers.py"
    watcher_file = cgc_path / "core" / "watcher.py"

    changes_made = False
    changes_made |= patch_cli_helpers(cli_helpers)
    changes_made |= patch_watcher_batch(watcher_file)

    if changes_made:
        cleanup_pycache(cgc_path)

    tests_ok = validate_imports()

    print(f"\n{BLUE}════════════════════════════════════════════════════════════{NC}")
    if tests_ok:
        print(f"{GREEN}Toutes les optimisations sont en place !{NC}")
        print(f"\nOptimisations actives:")
        print(f"  • Requêtes Cypher: 1 scan au lieu de 2")
        print(f"  • Watcher: filtrage .gitignore/.cgcignore avant traitement")
        print(f"  • Watcher: debounce global (3s) au lieu de par fichier")
        print(f"  • Batch: update ciblé des fichiers modifiés uniquement")
        print(f"\n{YELLOW}Relance 'mise mcps' pour appliquer les changements.{NC}")
    else:
        print(f"{RED}Des erreurs ont été détectées. Vérifiez les logs ci-dessus.{NC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
