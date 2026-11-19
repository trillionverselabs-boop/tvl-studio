"""Voiceover — Kokoro TTS per dialogue line, per-character voices from the kit.

Free and local: ``npx hyperframes tts`` with the kokoro-onnx venv. Lines are
concatenated per shot with 0.25 s gaps (ffmpeg concat demuxer) and measured
with ffprobe; the duration drives the scene slot in assembly.
"""

from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
from pathlib import Path

from . import brands, storyboard

GAP_S = 0.25
TTS_TIMEOUT_S = 180


def _find(name: str, pattern: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    hits = sorted(glob.glob(str(Path.home() / ".hermes" / "tools" / pattern)))
    if hits:
        return hits[-1]
    raise RuntimeError(f"{name} not found on PATH or under ~/.hermes/tools")


def npx() -> str:
    return _find("npx", "node-*/bin/npx")


def ffmpeg() -> str:
    return _find("ffmpeg", "ffmpeg-*/bin/ffmpeg")


def ffprobe() -> str:
    return _find("ffprobe", "ffmpeg-*/bin/ffprobe")


def tts_python() -> str | None:
    env = os.environ.get("TVL_STUDIO_TTS_PYTHON")
    if env and Path(env).exists():
        return env
    default = Path.home() / "work/arena-demo-video/.venv/bin/python"
    return str(default) if default.exists() else None


def _run(args: list[str], timeout: int, cwd: Path | None = None,
         env: dict | None = None) -> str:
    """List-args subprocess, no shell. Returns stdout; raises with stderr tail."""
    proc = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=str(cwd) if cwd else None, text=True, env=env,
    )
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate()
        raise RuntimeError(f"timed out after {timeout}s: {args[0]} … {args[-1]}")
    if proc.returncode != 0:
        raise RuntimeError(
            f"{Path(args[0]).name} exited {proc.returncode}: {(err or out)[-800:]}")
    return out


def duration_of(path: Path) -> float:
    out = _run([ffprobe(), "-v", "error", "-show_entries", "format=duration",
                "-of", "json", str(path)], 30)
    return float(json.loads(out)["format"]["duration"])


def _silence(path: Path, sample_rate: int, channels: int) -> None:
    _run([ffmpeg(), "-y", "-v", "error", "-f", "lavfi", "-i",
          f"anullsrc=r={sample_rate}:cl={'mono' if channels == 1 else 'stereo'}",
          "-t", str(GAP_S), "-c:a", "pcm_s16le", str(path)], 30)


def _wav_format(path: Path) -> tuple[int, int]:
    out = _run([ffprobe(), "-v", "error", "-select_streams", "a:0",
                "-show_entries", "stream=sample_rate,channels", "-of", "json",
                str(path)], 30)
    st = json.loads(out)["streams"][0]
    return int(st["sample_rate"]), int(st["channels"])


def voice_shot(proj: dict, shot: dict, kit: dict, pdir: Path) -> None:
    vo = pdir / "vo"
    vo.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    py = tts_python()
    if py:
        env["HYPERFRAMES_PYTHON"] = py
    speed = str(kit["voice"]["speed"])
    parts: list[Path] = []
    for i, line in enumerate(shot["lines"]):
        txt = vo / f"{shot['id']}_l{i:02d}.txt"
        wav = vo / f"{shot['id']}_l{i:02d}.wav"
        txt.write_text(line["text"])
        voice = (proj["cast"].get(line["character"]) or {}).get(
            "voice", kit["voice"]["narrator"])
        if voice not in brands.VOICE_POOL:
            voice = kit["voice"]["narrator"]
        if not wav.exists():
            _run([npx(), "hyperframes", "tts", str(txt), "-o", str(wav),
                  "-v", voice, "-s", speed], TTS_TIMEOUT_S, cwd=pdir, env=env)
        if not wav.exists():
            raise RuntimeError(f"TTS produced no file for {shot['id']} line {i}")
        parts.append(wav)
    if not parts:
        raise RuntimeError(f"shot {shot['id']} has no dialogue to voice")

    rate, ch = _wav_format(parts[0])
    gap = vo / "gap.wav"
    _silence(gap, rate, ch)
    seq: list[Path] = []
    for i, p in enumerate(parts):
        if i:
            seq.append(gap)
        seq.append(p)
    listing = vo / f"{shot['id']}_concat.txt"
    listing.write_text("".join(f"file '{p.name}'\n" for p in seq))
    out = pdir / "assets" / f"{shot['id']}_vo.wav"
    _run([ffmpeg(), "-y", "-v", "error", "-f", "concat", "-safe", "0",
          "-i", str(listing), "-c", "copy", str(out)], 60)
    shot["audio"] = str(out)
    shot["duration"] = round(duration_of(out), 3)


def run(project_id: str, shot_id: str | None = None) -> dict:
    proj = storyboard.load(project_id)
    kit = brands.get_kit(proj["brand"])
    pdir = storyboard.project_dir(project_id)
    targets = proj["shots"]
    if shot_id:
        storyboard.validate_shot_id(shot_id)
        targets = [s for s in targets if s["id"] == shot_id]
        if not targets:
            raise ValueError(f"unknown shot {shot_id!r}")
    proj["busy"] = "voiceover"
    storyboard._save(pdir, proj)
    try:
        for shot in targets:
            if shot.get("audio") and not shot_id:
                continue
            voice_shot(proj, shot, kit, pdir)
            storyboard._save(pdir, proj)
    finally:
        proj["busy"] = None
        storyboard._save(pdir, proj)
    return storyboard.summary(proj)
