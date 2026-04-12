"""Tests pour sync-config.py."""
import json
from pathlib import Path

MARKER_START = "# >>> Claude Setup >>>"
MARKER_END = "# <<< Claude Setup <<<"
GI_MARKER_START = "# >>> Claude Setup - CGC ignore >>>"
GI_MARKER_END = "# <<< Claude Setup - CGC ignore <<<"


# ── merge_with_markers ──────────────────────────────────────────────


class TestMergeWithMarkers:
    def test_target_inexistant(self, sync_config, tmp_path):
        target = tmp_path / "target.toml"
        source = tmp_path / "source.toml"
        source.write_text("new content\n")

        sync_config.merge_with_markers(target, source, MARKER_START, MARKER_END)

        assert target.read_text() == "new content\n"

    def test_target_sans_marqueurs(self, sync_config, tmp_path):
        target = tmp_path / "target.toml"
        source = tmp_path / "source.toml"
        target.write_text("existing\n")
        source.write_text("new\n")

        sync_config.merge_with_markers(target, source, MARKER_START, MARKER_END)

        assert target.read_text() == "existing\nnew\n"

    def test_target_sans_trailing_newline(self, sync_config, tmp_path):
        target = tmp_path / "target.toml"
        source = tmp_path / "source.toml"
        target.write_text("existing")
        source.write_text("new\n")

        sync_config.merge_with_markers(target, source, MARKER_START, MARKER_END)

        assert target.read_text() == "existing\nnew\n"

    def test_target_avec_marqueurs_remplace(self, sync_config, tmp_path):
        target = tmp_path / "target.toml"
        source = tmp_path / "source.toml"
        target.write_text(
            f"before\n{MARKER_START}\nold content\n{MARKER_END}\nafter\n"
        )
        source.write_text("new content\n")

        sync_config.merge_with_markers(target, source, MARKER_START, MARKER_END)

        result = target.read_text()
        assert "old content" not in result
        assert result == "before\nafter\nnew content\n"

    def test_section_marquee_vide(self, sync_config, tmp_path):
        target = tmp_path / "target.toml"
        source = tmp_path / "source.toml"
        target.write_text(f"{MARKER_START}\n{MARKER_END}\n")
        source.write_text("new\n")

        sync_config.merge_with_markers(target, source, MARKER_START, MARKER_END)

        assert target.read_text() == "new\n"

    def test_idempotence(self, sync_config, tmp_path):
        target = tmp_path / "target.toml"
        source = tmp_path / "source.toml"
        target.write_text("base\n")
        source.write_text(f"{MARKER_START}\ncontent\n{MARKER_END}\n")

        sync_config.merge_with_markers(target, source, MARKER_START, MARKER_END)
        first = target.read_text()

        sync_config.merge_with_markers(target, source, MARKER_START, MARKER_END)
        second = target.read_text()

        assert first == second


# ── adapt_mcp_json ──────────────────────────────────────────────────


class TestAdaptMcpJson:
    def test_target_inexistant(self, sync_config, tmp_path):
        source = tmp_path / "source.json"
        target = tmp_path / "target.json"
        data = {"mcpServers": {"a": {"command": "cmd_a"}}}
        source.write_text(json.dumps(data))

        sync_config.adapt_mcp_json(source, target)

        result = json.loads(target.read_text())
        assert result["mcpServers"]["a"]["command"] == "cmd_a"

    def test_pas_de_chevauchement(self, sync_config, tmp_path):
        source = tmp_path / "source.json"
        target = tmp_path / "target.json"
        source.write_text(json.dumps({"mcpServers": {"a": {"cmd": 1}}}))
        target.write_text(json.dumps({"mcpServers": {"b": {"cmd": 2}}}))

        sync_config.adapt_mcp_json(source, target)

        result = json.loads(target.read_text())
        assert "a" in result["mcpServers"]
        assert "b" in result["mcpServers"]

    def test_cle_commune_garde_local(self, sync_config, tmp_path):
        source = tmp_path / "source.json"
        target = tmp_path / "target.json"
        source.write_text(
            json.dumps({"mcpServers": {"a": {"version": "upstream"}}})
        )
        target.write_text(
            json.dumps({"mcpServers": {"a": {"version": "local"}}})
        )

        sync_config.adapt_mcp_json(source, target)

        result = json.loads(target.read_text())
        assert result["mcpServers"]["a"]["version"] == "local"

    def test_source_ajoute_nouvelle_cle(self, sync_config, tmp_path):
        source = tmp_path / "source.json"
        target = tmp_path / "target.json"
        source.write_text(
            json.dumps({"mcpServers": {"a": {"v": 1}, "b": {"v": 2}}})
        )
        target.write_text(json.dumps({"mcpServers": {"a": {"v": 0}}}))

        sync_config.adapt_mcp_json(source, target)

        result = json.loads(target.read_text())
        assert result["mcpServers"]["a"]["v"] == 0  # local conservé
        assert result["mcpServers"]["b"]["v"] == 2  # upstream ajouté

    def test_cles_non_mcpservers_preservees(self, sync_config, tmp_path):
        source = tmp_path / "source.json"
        target = tmp_path / "target.json"
        source.write_text(
            json.dumps({"mcpServers": {}, "sourceKey": "from_source"})
        )
        target.write_text(
            json.dumps({"mcpServers": {}, "targetKey": "from_target"})
        )

        sync_config.adapt_mcp_json(source, target)

        result = json.loads(target.read_text())
        assert result["sourceKey"] == "from_source"
        assert result["targetKey"] == "from_target"


# ── update_gitignore ────────────────────────────────────────────────


class TestUpdateGitignore:
    def test_gitignore_inexistant(self, sync_config, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cgcignore = tmp_path / ".cgcignore"
        cgcignore.write_text("*.log\n")

        sync_config.update_gitignore(cgcignore)

        content = (tmp_path / ".gitignore").read_text()
        assert GI_MARKER_START in content
        assert "*.log" in content
        assert GI_MARKER_END in content

    def test_gitignore_existant_sans_marqueurs(
        self, sync_config, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".gitignore").write_text("node_modules/\n")
        cgcignore = tmp_path / ".cgcignore"
        cgcignore.write_text("*.log\n")

        sync_config.update_gitignore(cgcignore)

        content = (tmp_path / ".gitignore").read_text()
        assert content.startswith("node_modules/\n")
        assert GI_MARKER_START in content
        assert "*.log" in content

    def test_gitignore_avec_anciens_marqueurs(
        self, sync_config, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".gitignore").write_text(
            f"keep\n{GI_MARKER_START}\nold\n{GI_MARKER_END}\n"
        )
        cgcignore = tmp_path / ".cgcignore"
        cgcignore.write_text("new\n")

        sync_config.update_gitignore(cgcignore)

        content = (tmp_path / ".gitignore").read_text()
        assert "old" not in content
        assert "new" in content
        assert content.count(GI_MARKER_START) == 1

    def test_idempotence(self, sync_config, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".gitignore").write_text("")
        cgcignore = tmp_path / ".cgcignore"
        cgcignore.write_text("*.log\n")

        sync_config.update_gitignore(cgcignore)
        first = (tmp_path / ".gitignore").read_text()

        sync_config.update_gitignore(cgcignore)
        second = (tmp_path / ".gitignore").read_text()

        assert first == second
        assert second.count(GI_MARKER_START) == 1
