"""Tests pour smart-update.py."""
import json
from pathlib import Path


# ── collect_files ───────────────────────────────────────────────────


class TestCollectFiles:
    def test_repertoire_vide(self, smart_update, tmp_path):
        assert smart_update.collect_files(tmp_path) == set()

    def test_fichiers_plats(self, smart_update, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.py").write_text("b")

        result = smart_update.collect_files(tmp_path)
        assert result == {"a.txt", "b.py"}

    def test_fichiers_imbriques(self, smart_update, tmp_path):
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "c.txt").write_text("c")

        result = smart_update.collect_files(tmp_path)
        assert "sub/c.txt" in result

    def test_exclut_git(self, smart_update, tmp_path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("git stuff")
        (tmp_path / "a.txt").write_text("a")

        result = smart_update.collect_files(tmp_path)
        assert result == {"a.txt"}


# ── is_binary ───────────────────────────────────────────────────────


class TestIsBinary:
    def test_fichier_texte(self, smart_update, tmp_path):
        f = tmp_path / "text.txt"
        f.write_text("hello world")
        assert smart_update.is_binary(f) is False

    def test_fichier_binaire(self, smart_update, tmp_path):
        f = tmp_path / "bin.dat"
        f.write_bytes(b"hello\x00world")
        assert smart_update.is_binary(f) is True

    def test_fichier_vide(self, smart_update, tmp_path):
        f = tmp_path / "empty"
        f.write_bytes(b"")
        assert smart_update.is_binary(f) is False

    def test_null_apres_8192(self, smart_update, tmp_path):
        f = tmp_path / "large.dat"
        f.write_bytes(b"a" * 8192 + b"\x00")
        assert smart_update.is_binary(f) is False


# ── classify_files ──────────────────────────────────────────────────


class TestClassifyFiles:
    def test_arbres_identiques(self, smart_update, tmp_path, monkeypatch):
        local = tmp_path / "local"
        upstream = tmp_path / "upstream"
        local.mkdir()
        upstream.mkdir()
        (local / "a.txt").write_text("same")
        (upstream / "a.txt").write_text("same")
        monkeypatch.setattr(smart_update, "LOCAL_CLAUDE", local)

        upstream_only, local_only, identical, diverged = (
            smart_update.classify_files(upstream)
        )

        assert identical == {"a.txt"}
        assert upstream_only == set()
        assert local_only == set()
        assert diverged == set()

    def test_fichiers_upstream_et_local_only(
        self, smart_update, tmp_path, monkeypatch
    ):
        local = tmp_path / "local"
        upstream = tmp_path / "upstream"
        local.mkdir()
        upstream.mkdir()
        (local / "local_only.txt").write_text("l")
        (upstream / "upstream_only.txt").write_text("u")
        monkeypatch.setattr(smart_update, "LOCAL_CLAUDE", local)

        upstream_only, local_only, identical, diverged = (
            smart_update.classify_files(upstream)
        )

        assert upstream_only == {"upstream_only.txt"}
        assert local_only == {"local_only.txt"}

    def test_scenario_mixte(self, smart_update, tmp_path, monkeypatch):
        local = tmp_path / "local"
        upstream = tmp_path / "upstream"
        local.mkdir()
        upstream.mkdir()

        # Identique
        (local / "same.txt").write_text("same")
        (upstream / "same.txt").write_text("same")
        # Divergé
        (local / "diff.txt").write_text("local version")
        (upstream / "diff.txt").write_text("upstream version")
        # Local only
        (local / "mine.txt").write_text("mine")
        # Upstream only
        (upstream / "new.txt").write_text("new")

        monkeypatch.setattr(smart_update, "LOCAL_CLAUDE", local)

        upstream_only, local_only, identical, diverged = (
            smart_update.classify_files(upstream)
        )

        assert identical == {"same.txt"}
        assert diverged == {"diff.txt"}
        assert local_only == {"mine.txt"}
        assert upstream_only == {"new.txt"}


# ── merge_mcp_json (auto mode) ─────────────────────────────────────


class TestMergeMcpJson:
    def test_serveur_local_only(self, smart_update, tmp_path):
        local = tmp_path / "local.json"
        upstream = tmp_path / "upstream.json"
        local.write_text(json.dumps({"mcpServers": {"a": {"cmd": 1}}}))
        upstream.write_text(json.dumps({"mcpServers": {}}))

        smart_update.merge_mcp_json(local, upstream, auto=True)

        result = json.loads(local.read_text())
        assert "a" in result["mcpServers"]

    def test_serveur_upstream_only(self, smart_update, tmp_path):
        local = tmp_path / "local.json"
        upstream = tmp_path / "upstream.json"
        local.write_text(json.dumps({"mcpServers": {}}))
        upstream.write_text(json.dumps({"mcpServers": {"b": {"cmd": 2}}}))

        smart_update.merge_mcp_json(local, upstream, auto=True)

        result = json.loads(local.read_text())
        assert "b" in result["mcpServers"]

    def test_divergent_auto_garde_local(self, smart_update, tmp_path):
        local = tmp_path / "local.json"
        upstream = tmp_path / "upstream.json"
        local.write_text(
            json.dumps({"mcpServers": {"a": {"version": "local"}}})
        )
        upstream.write_text(
            json.dumps({"mcpServers": {"a": {"version": "upstream"}}})
        )

        smart_update.merge_mcp_json(local, upstream, auto=True)

        result = json.loads(local.read_text())
        assert result["mcpServers"]["a"]["version"] == "local"

    def test_cles_non_mcpservers_preservees(self, smart_update, tmp_path):
        local = tmp_path / "local.json"
        upstream = tmp_path / "upstream.json"
        local.write_text(
            json.dumps({"mcpServers": {}, "localExtra": True})
        )
        upstream.write_text(
            json.dumps({"mcpServers": {}, "upstreamExtra": True})
        )

        smart_update.merge_mcp_json(local, upstream, auto=True)

        result = json.loads(local.read_text())
        assert result["localExtra"] is True
        assert result["upstreamExtra"] is True
