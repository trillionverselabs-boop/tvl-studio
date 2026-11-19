import json
from pathlib import Path

from tvl_studio.engine import storyboard, voiceover

SCRIPT = """CAST: GUIDE — a cyan robot

INT. LAB — NIGHT

GUIDE: Line one.
GUIDE: Line two.
"""


def _fake_run_factory(created):
    """Stub for voiceover._run: simulates tts/ffprobe/ffmpeg without binaries."""
    def fake_run(args, timeout, cwd=None, env=None):
        created.append(args)
        if "tts" in args:
            out = Path(args[args.index("-o") + 1])
            out.write_bytes(b"RIFFfakeWAVE")
            return ""
        if args[0].endswith("ffprobe") or "ffprobe" in args[0]:
            if "format=duration" in args:
                return json.dumps({"format": {"duration": "2.5"}})
            return json.dumps({"streams": [{"sample_rate": "24000", "channels": "1"}]})
        if "anullsrc" in " ".join(args):
            Path(args[-1]).write_bytes(b"RIFFfakeWAVE")
            return ""
        if "concat" in args:
            Path(args[-1]).write_bytes(b"RIFFfakeWAVEconcat")
            return ""
        raise AssertionError(f"unexpected command: {args}")
    return fake_run


def test_voiceover_records_per_character_and_measures(monkeypatch):
    proj = storyboard.create("VO Test", SCRIPT)
    pid = proj["id"]
    created = []
    monkeypatch.setattr(voiceover, "_run", _fake_run_factory(created))
    out = voiceover.run(pid)
    assert out["voiced"] == 1
    after = storyboard.load(pid)
    shot = after["shots"][0]
    assert shot["audio"] and Path(shot["audio"]).exists()
    assert shot["duration"] == 2.5
    assert after["busy"] is None
    # two TTS calls, one per line, with the cast voice
    tts_calls = [a for a in created if "tts" in a]
    assert len(tts_calls) == 2
    voice = after["cast"]["GUIDE"]["voice"]
    assert all(a[a.index("-v") + 1] == voice for a in tts_calls)


def test_voiceover_failure_clears_busy(monkeypatch):
    proj = storyboard.create("VO Fail", SCRIPT)
    pid = proj["id"]

    def boom(args, timeout, cwd=None, env=None):
        raise RuntimeError("tts exploded")

    monkeypatch.setattr(voiceover, "_run", boom)
    try:
        voiceover.run(pid)
    except RuntimeError:
        pass
    assert storyboard.load(pid)["busy"] is None


def test_tts_subprocess_gets_the_kokoro_venv(monkeypatch):
    py = voiceover.tts_python()
    if not py:
        import pytest
        pytest.skip("no kokoro venv on this machine")
    proj = storyboard.create("VO Env", SCRIPT)
    seen = []

    def capture(args, timeout, cwd=None, env=None):
        if "tts" in args:
            seen.append(env)
            Path(args[args.index("-o") + 1]).write_bytes(b"RIFFfakeWAVE")
            return ""
        if "format=duration" in args:
            return json.dumps({"format": {"duration": "1.0"}})
        if "sample_rate" in " ".join(args):
            return json.dumps({"streams": [{"sample_rate": "24000", "channels": "1"}]})
        Path(args[-1]).write_bytes(b"RIFFfakeWAVE")
        return ""

    monkeypatch.setattr(voiceover, "_run", capture)
    voiceover.run(proj["id"])
    assert seen and all(e and e.get("HYPERFRAMES_PYTHON") == py for e in seen)
