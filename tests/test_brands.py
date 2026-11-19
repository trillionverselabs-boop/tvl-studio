import pytest

from tvl_studio.engine import brands


def test_bundled_kits_are_seeded():
    ids = {k["id"] for k in brands.list_kits()}
    assert {"tvl", "script-driven"} <= ids


def test_tvl_kit_carries_the_style_lock_and_palette():
    kit = brands.get_kit("tvl")
    assert "navy" in kit["visual"]["style_prompt"]
    assert kit["visual"]["palette"]["bg"] == "#0a0e1a"
    assert kit["voice"]["narrator"] in brands.VOICE_POOL


def test_script_driven_kit_has_no_style_lock():
    kit = brands.get_kit("script-driven")
    assert kit["visual"]["style_prompt"] == ""


def test_voice_assignment_is_deterministic_and_distinct():
    kit = brands.get_kit("tvl")
    a = brands.assign_voices(["GUIDE", "SKEPTIC", "ANALYST"], kit)
    b = brands.assign_voices(["GUIDE", "SKEPTIC", "ANALYST"], kit)
    assert a == b
    assert len(set(a.values())) == 3
    assert kit["voice"]["narrator"] not in a.values()


def test_save_kit_normalizes_hostile_values():
    kit = brands.save_kit({
        "id": "test-kit", "name": "Test",
        "voice": {"narrator": "not_a_voice", "pool": ["af_sky", "bogus"], "speed": 99},
        "music": {"mode": "youtube", "volume": 5},
    })
    assert kit["voice"]["narrator"] == "af_heart"
    assert kit["voice"]["pool"] == ["af_sky"]
    assert kit["voice"]["speed"] == 1.5
    assert kit["music"]["mode"] == "none"
    assert kit["music"]["volume"] == 0.5
    assert brands.get_kit("test-kit")["name"] == "Test"


@pytest.mark.parametrize("bad", ["../evil", "UPPER", "", "a" * 80])
def test_bad_kit_ids_are_refused(bad):
    with pytest.raises(ValueError):
        brands.get_kit(bad)


def test_unknown_kit_names_the_alternatives():
    with pytest.raises(ValueError, match="script-driven"):
        brands.get_kit("does-not-exist")
