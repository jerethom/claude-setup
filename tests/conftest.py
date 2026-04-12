"""Fixtures pour le chargement des scripts avec noms à tirets."""
import importlib.util
import pytest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent / ".claude" / "scripts"


def _load_script(name: str):
    """Charge un script Python par nom de fichier (supporte les tirets)."""
    script_path = SCRIPTS_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(
        name.replace("-", "_"), script_path
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def sync_config():
    return _load_script("sync-config")


@pytest.fixture
def smart_update():
    return _load_script("smart-update")


@pytest.fixture
def fix_cgc():
    return _load_script("fix-cgc-optimizations")
