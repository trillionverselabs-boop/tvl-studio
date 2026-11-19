import pytest

from tvl_studio.engine.script_parser import parse_script

SCRIPT = """CAST: GUIDE — a friendly cyan robot with an antenna
CAST: SKEPTIC — a small red stick figure

INT. THE LAB — NIGHT

GUIDE: Every big idea starts as a paper nobody has read yet.
SKEPTIC: And most of them stay that way.
GUIDE: Not when an agent scores it.

INT. THE MARKET — DAY

GUIDE: Evidence first. Then we ship.
"""


def test_screenplay_scenes_cast_and_dialogue():
    out = parse_script(SCRIPT)
    assert out["mode"] == "screenplay"
    assert len(out["shots"]) == 2
    assert out["shots"][0]["scene"].startswith("THE LAB")
    assert out["cast"]["GUIDE"].startswith("a friendly cyan robot")
    chars = [l["character"] for l in out["shots"][0]["lines"]]
    assert chars == ["GUIDE", "SKEPTIC", "GUIDE"]


def test_prose_becomes_narration():
    out = parse_script("First paragraph about the pipeline.\n\nSecond paragraph about the market.")
    assert out["mode"] == "prose"
    assert len(out["shots"]) == 2
    assert all(l["character"] == "NARRATOR" for s in out["shots"] for l in s["lines"])


def test_markdown_scene_headings():
    out = parse_script("## Scene: Opening\n\nGUIDE: Hello there.\n")
    assert out["shots"][0]["scene"] == "Opening"


def test_empty_script_raises():
    with pytest.raises(ValueError):
        parse_script("   ")


def test_parenthetical_becomes_direction():
    out = parse_script("INT. ROOM — DAY\n\n(whispering)\nGUIDE: Keep it quiet.\n")
    assert out["shots"][0]["direction"] == "whispering"
