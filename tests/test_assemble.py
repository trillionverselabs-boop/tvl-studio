from pathlib import Path

import pytest

from tvl_studio.engine import assemble, brands, storyboard

SCRIPT = """CAST: GUIDE — a cyan robot

INT. LAB — NIGHT

GUIDE: Line one.
"""


def _ready_project(tmp_path):
    proj = storyboard.create("Asm Test", SCRIPT)
    pid = proj["id"]
    pdir = storyboard.project_dir(pid)
    img = tmp_path / "img.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\nfake")
    wav = tmp_path / "vo.wav"
    wav.write_bytes(b"RIFFfakeWAVE")
    storyboard.attach_image(pid, "s01", str(img))
    proj = storyboard.load(pid)
    proj["shots"][0]["audio"] = str(wav)
    proj["shots"][0]["duration"] = 3.0
    storyboard._save(pdir, proj)
    return proj, pdir


def test_build_film_writes_gated_composition(tmp_path):
    proj, pdir = _ready_project(tmp_path)
    kit = brands.get_kit("tvl")
    hf = assemble.build_film(proj, kit, pdir)
    index = (hf / "index.html").read_text()
    scene = (hf / "compositions" / "s01.html").read_text()
    # slot = duration 3.0 + pad 1.7
    assert 'data-duration="4.7"' in index
    assert 'data-composition-src="compositions/s01.html"' in index
    # brand palette reaches the frame
    assert "#0a0e1a" in scene
    # VO lead-in and caption present
    assert 'data-start="0.6"' in scene
    assert "Line one." in scene
    # deterministic: no Math.random anywhere
    assert "Math.random" not in scene and "Math.random" not in index
    assert (hf / "hyperframes.json").exists()


def test_missing_image_refuses_assembly(tmp_path):
    proj, pdir = _ready_project(tmp_path)
    proj["shots"][0]["image"] = None
    with pytest.raises(ValueError, match="missing image"):
        assemble.build_film(proj, brands.get_kit("tvl"), pdir)


def test_music_outside_data_root_is_refused(tmp_path):
    proj, pdir = _ready_project(tmp_path)
    kit = brands.get_kit("tvl")
    outside = tmp_path / "song.mp3"
    outside.write_bytes(b"fake")
    kit["music"] = {"mode": "file", "file": str(outside), "volume": 0.18}
    with pytest.raises(ValueError, match="music file"):
        assemble.build_film(proj, kit, pdir)


def test_music_inside_data_root_is_copied(tmp_path):
    proj, pdir = _ready_project(tmp_path)
    kit = brands.get_kit("tvl")
    inside = storyboard.data_root() / "song.mp3"
    inside.write_bytes(b"fake")
    kit["music"] = {"mode": "file", "file": str(inside), "volume": 0.18}
    hf = assemble.build_film(proj, kit, pdir)
    assert (hf / "assets" / "music.mp3").exists()
    assert 'data-volume="0.18"' in (hf / "index.html").read_text()


def test_dialogue_only_shot_omits_the_redundant_title_bar(tmp_path):
    proj, pdir = _ready_project(tmp_path)  # SCRIPT is dialogue-only
    hf = assemble.build_film(proj, brands.get_kit("tvl"), pdir)
    scene = (hf / "compositions" / "s01.html").read_text()
    assert 'id="s01-bar"' not in scene
    assert "#s01-bar" not in scene  # no orphan tween either
    # an action-titled shot keeps its bar
    proj["shots"][0]["title"] = "A distinct action title"
    hf = assemble.build_film(proj, brands.get_kit("tvl"), pdir)
    assert 'id="s01-bar"' in (hf / "compositions" / "s01.html").read_text()
