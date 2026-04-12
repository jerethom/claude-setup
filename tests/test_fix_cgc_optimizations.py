"""Tests pour fix-cgc-optimizations.py."""
from pathlib import Path

# Patterns exacts tirés du script source

OLD_INDEX_QUERY = '"MATCH (r:Repository {path: $path})-[:CONTAINS]->(f:File) RETURN count(f) as file_count"'
NEW_INDEX_QUERY = '"MATCH (f:File) WHERE f.path STARTS WITH $path RETURN count(f) as file_count"'
OPTIMIZED_MARKER = "WITH collect(f) as files, count(f) as file_count"

OLD_STATS_BLOCK = '''                # Get stats
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

OLD_BATCH_METHOD = '''    def _handle_batch_modification(self, changed_paths: list):
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


# ── patch_cli_helpers ───────────────────────────────────────────────


class TestPatchCliHelpers:
    def _make_unoptimized(self, path: Path):
        """Crée un fichier cli_helpers simulé avec les anciens patterns."""
        content = f"""# Fake cli_helpers
def index_helper():
    query = {OLD_INDEX_QUERY}
    result = session.run(query, path=str(path_obj))

def stats_helper():
{OLD_STATS_BLOCK}
"""
        path.write_text(content, encoding="utf-8")

    def test_fichier_inexistant(self, fix_cgc, tmp_path):
        result = fix_cgc.patch_cli_helpers(tmp_path / "missing.py")
        assert result is False

    def test_deja_optimise(self, fix_cgc, tmp_path):
        f = tmp_path / "cli_helpers.py"
        f.write_text(
            f"# Already patched\n{OPTIMIZED_MARKER}\n", encoding="utf-8"
        )
        original = f.read_text()

        result = fix_cgc.patch_cli_helpers(f)

        assert result is False
        assert f.read_text() == original

    def test_patch_applique(self, fix_cgc, tmp_path):
        f = tmp_path / "cli_helpers.py"
        self._make_unoptimized(f)

        result = fix_cgc.patch_cli_helpers(f)

        assert result is True
        content = f.read_text()
        assert "STARTS WITH $path" in content
        assert OPTIMIZED_MARKER in content
        assert "Repository {path: $path})-[:CONTAINS]->(f:File)" not in content

    def test_idempotence(self, fix_cgc, tmp_path):
        f = tmp_path / "cli_helpers.py"
        self._make_unoptimized(f)

        fix_cgc.patch_cli_helpers(f)
        patched = f.read_text()

        result = fix_cgc.patch_cli_helpers(f)

        assert result is False
        assert f.read_text() == patched


# ── patch_watcher_batch ─────────────────────────────────────────────


class TestPatchWatcherBatch:
    def _make_unoptimized(self, path: Path):
        """Crée un fichier watcher simulé avec l'ancien batch method."""
        content = f"""# Fake watcher
class CodeWatcher:
{OLD_BATCH_METHOD}
"""
        path.write_text(content, encoding="utf-8")

    def test_fichier_inexistant(self, fix_cgc, tmp_path):
        result = fix_cgc.patch_watcher_batch(tmp_path / "missing.py")
        assert result is False

    def test_deja_optimise(self, fix_cgc, tmp_path):
        f = tmp_path / "watcher.py"
        f.write_text(
            "# OPTIMIZED: Only updates changed files\n", encoding="utf-8"
        )
        original = f.read_text()

        result = fix_cgc.patch_watcher_batch(f)

        assert result is False
        assert f.read_text() == original

    def test_patch_applique(self, fix_cgc, tmp_path):
        f = tmp_path / "watcher.py"
        self._make_unoptimized(f)

        result = fix_cgc.patch_watcher_batch(f)

        assert result is True
        content = f.read_text()
        assert "OPTIMIZED: Only updates changed files" in content
        assert 'self.repo_path.rglob("*")' not in content

    def test_idempotence(self, fix_cgc, tmp_path):
        f = tmp_path / "watcher.py"
        self._make_unoptimized(f)

        fix_cgc.patch_watcher_batch(f)
        patched = f.read_text()

        result = fix_cgc.patch_watcher_batch(f)

        assert result is False
        assert f.read_text() == patched
