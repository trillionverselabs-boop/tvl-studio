"""The dashboard loader path: plugin_api.py loaded by file spec, standalone."""
import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _load_api():
    path = REPO / "dashboard" / "plugin_api.py"
    spec = importlib.util.spec_from_file_location("_tvl_studio_api_test", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_routes_mount_and_plugin_dir_stays_off_sys_path():
    before = set(sys.path)
    mod = _load_api()
    assert str(REPO) not in set(sys.path) - before
    paths = {r.path for r in mod.router.routes}
    assert {"/health", "/brands", "/projects", "/import",
            "/project/{project_id}", "/project/{project_id}/voiceover",
            "/project/{project_id}/assemble", "/project/{project_id}/brand"} <= paths


def test_detail_has_thumbs_and_next_action():
    mod = _load_api()
    from tvl_studio.engine import storyboard
    proj = storyboard.create("API Test", "A short prose paragraph about the pipeline.")
    d = mod._detail(proj)
    assert d["shots"][0]["thumb"] is None  # no image yet
    assert d["next_action"]["action"] in ("generate_image", "voiceover")
