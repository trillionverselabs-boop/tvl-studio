import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

# pytest resolves modules by walking up through dirs that contain __init__.py, so
# a checkout with a hyphenated name cannot be imported as a package. Give sys.path
# a directory that holds the package under a valid identifier.
_shim = Path(tempfile.mkdtemp(prefix="plugin-import-"))
_link = _shim / "tvl_studio"
if not _link.exists():
    _link.symlink_to(REPO, target_is_directory=True)
sys.path.insert(0, str(_shim))


@pytest.fixture(autouse=True)
def tmp_hermes_home(tmp_path, monkeypatch):
    """Never let a test write into the real ~/.hermes."""
    home = tmp_path / "hermes"
    home.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(home))
    yield home
