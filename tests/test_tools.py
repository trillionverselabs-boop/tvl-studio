import json
from pathlib import Path

import yaml

from tvl_studio import tools

REPO = Path(__file__).resolve().parent.parent


class Ctx:
    def __init__(self):
        self.handlers = {}
        self.names = []

    def register_tool(self, name, toolset, schema, handler):
        self.names.append(name)
        self.handlers[name] = handler


def _ctx():
    c = Ctx()
    tools.register_tools(c)
    return c


def test_registered_tools_match_the_manifest():
    manifest = yaml.safe_load((REPO / "plugin.yaml").read_text())
    assert sorted(_ctx().names) == sorted(manifest["provides_tools"])


SCRIPT = """CAST: GUIDE — a friendly cyan robot
CAST: SKEPTIC — a small red stick figure

INT. THE LAB — NIGHT

GUIDE: Every big idea starts as a paper.
SKEPTIC: And most stay unread.
"""


def test_import_builds_a_storyboard_with_cast_and_next_action():
    c = _ctx()
    out = json.loads(c.handlers["studio_import_script"](
        {"name": "Test Film", "script": SCRIPT}))
    assert "error" not in out
    assert out["project"]["shots"] == 1
    assert set(out["cast"]) == {"GUIDE", "SKEPTIC"}
    voices = {out["cast"][k]["voice"] for k in ("GUIDE", "SKEPTIC")}
    assert len(voices) == 2  # distinct voice per character
    assert out["next_action"]["action"] == "generate_portrait"


def test_bad_project_id_is_a_json_error_not_a_crash():
    c = _ctx()
    out = json.loads(c.handlers["studio_status"]({"project": "../../etc"}))
    assert "error" in out


def test_attach_missing_image_is_a_json_error():
    c = _ctx()
    out = json.loads(c.handlers["studio_import_script"](
        {"name": "T", "script": SCRIPT}))
    pid = out["project"]["id"]
    out = json.loads(c.handlers["studio_attach_image"](
        {"project": pid, "shot_id": "s01", "image_path": "/nonexistent/x.png"}))
    assert "error" in out


def test_brands_list_includes_bundled_kits():
    c = _ctx()
    out = json.loads(c.handlers["studio_brands"]({"action": "list"}))
    ids = {b["id"] for b in out["brands"]}
    assert {"tvl", "script-driven"} <= ids
