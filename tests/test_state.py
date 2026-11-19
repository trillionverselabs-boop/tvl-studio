import pytest

from tvl_studio.engine import storyboard

SCRIPT = """CAST: GUIDE — a friendly cyan robot
CAST: SKEPTIC — a small red stick figure

INT. THE LAB — NIGHT

GUIDE: Every big idea starts as a paper.
SKEPTIC: And most stay unread.
"""


def _project():
    return storyboard.create("State Test", SCRIPT)


def _fake_png(tmp_path, name="x.png"):
    p = tmp_path / name
    p.write_bytes(b"\x89PNG\r\n\x1a\nfake")
    return p


def test_next_action_walks_the_whole_machine(tmp_path):
    proj = _project()
    pid = proj["id"]
    # 1. portraits first
    na = storyboard.next_action(proj)
    assert na["action"] == "generate_portrait"
    storyboard.attach_portrait(pid, "GUIDE", str(_fake_png(tmp_path, "g.png")))
    proj = storyboard.load(pid)
    assert storyboard.next_action(proj)["character"] == "SKEPTIC"
    storyboard.attach_portrait(pid, "SKEPTIC", str(_fake_png(tmp_path, "s.png")))
    # 2. then shot images, with portrait references
    proj = storyboard.load(pid)
    na = storyboard.next_action(proj)
    assert na["action"] == "generate_image"
    assert len(na["reference_image_urls"]) == 2
    storyboard.attach_image(pid, "s01", str(_fake_png(tmp_path, "shot.png")))
    # 3. then voiceover, 4. assemble, 5. done
    proj = storyboard.load(pid)
    assert storyboard.next_action(proj)["action"] == "voiceover"
    proj["shots"][0]["audio"] = "/tmp/fake.wav"
    storyboard._save(storyboard.project_dir(pid), proj)
    assert storyboard.next_action(proj)["action"] == "assemble"
    proj["film"] = "/tmp/fake.mp4"
    storyboard._save(storyboard.project_dir(pid), proj)
    assert storyboard.next_action(proj)["action"] == "done"


def test_switching_brand_recompiles_prompts_and_voices(tmp_path):
    proj = _project()
    pid = proj["id"]
    before = proj["shots"][0]["image_prompt"]
    storyboard.set_brand(pid, "tvl")
    after = storyboard.load(pid)
    assert "TVL internal design language" in after["shots"][0]["image_prompt"]
    assert after["shots"][0]["image_prompt"] != before
    assert after["brand"] == "tvl"


def test_traversal_and_unknown_ids_are_refused(tmp_path):
    with pytest.raises(ValueError):
        storyboard.load("../../etc")
    proj = _project()
    with pytest.raises(ValueError):
        storyboard.attach_image(proj["id"], "s99", str(_fake_png(tmp_path)))
    with pytest.raises(ValueError):
        storyboard.attach_portrait(proj["id"], "NOBODY", str(_fake_png(tmp_path)))


def test_summary_counts(tmp_path):
    proj = _project()
    s = storyboard.summary(proj)
    assert s["shots"] == 1 and s["imaged"] == 0 and s["voiced"] == 0
    assert s["status"] == "storyboarding"
