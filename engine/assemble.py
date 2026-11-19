"""Assembly — storyboard -> HyperFrames composition -> gated render -> ffmpeg finish.

Each shot becomes a scene: full-bleed image with a slow push-in, brand-palette
lower-third, captions timed to the dialogue, VO at 0.6 s lead-in. Scene slot =
VO duration + 1.7 s pad. The kit's music file (if any) sits under everything at
the kit's volume. Render passes the HyperFrames check gate first; ffmpeg then
normalizes loudness to -16 LUFS and adds audio fades. Deterministic: no random
anything, fromTo tweens only.
"""

from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

from . import brands, storyboard
from .voiceover import _run, duration_of, ffmpeg, npx

PAD_S = 1.7
LEAD_S = 0.6
MIN_SLOT_S = 4.0
RENDER_TIMEOUT_S = 1500
FONT_SRC = Path.home() / "work/tvl-explainer-template/assets/fonts"


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def _scene_html(shot: dict, proj: dict, kit: dict, slot: float, index: int) -> str:
    p = kit["visual"]["palette"]
    fonts = kit["visual"]["fonts"]
    sid = shot["id"]
    img = Path(shot["image"]).name
    vo = Path(shot["audio"]).name
    speakers = []
    for line in shot["lines"]:
        if line["character"] not in speakers:
            speakers.append(line["character"])
    chip_colors = [p["accent"], p["accent2"], p["success"]]
    chip_of = {c: chip_colors[i % 3] for i, c in enumerate(speakers)}

    # Caption timing: shares of the VO duration proportional to text length.
    total_chars = max(1, sum(len(l["text"]) for l in shot["lines"]))
    vo_dur = shot.get("duration") or (slot - PAD_S)
    captions = []
    t = LEAD_S
    for i, line in enumerate(shot["lines"]):
        share = max(0.8, vo_dur * len(line["text"]) / total_chars)
        text = line["text"]
        cap_max = kit["text"]["caption_max_chars"]
        if len(text) > cap_max:
            text = text[: cap_max - 1] + "…"
        chip = (f'<span class="{sid}-chip" style="color:{chip_of.get(line["character"], p["accent"])}">'
                f'{_esc(line["character"].title())}</span> ') if line["character"] != "NARRATOR" else ""
        captions.append(
            f'  <div id="{sid}-cap{i}" class="{sid}-cap clip" data-start="{t:.2f}" '
            f'data-duration="{share:.2f}" data-track-index="{10 + i}">'
            f'{chip}{_esc(text)}</div>')
        t += share
    caption_css = (
        f'.{sid}-cap{{position:absolute;left:96px;right:96px;bottom:150px;'
        f'font-family:{fonts["body"]},system-ui,sans-serif;font-size:34px;line-height:1.35;'
        f'color:{p["text"]};background:rgba(0,0,0,.62);border-left:4px solid {p["accent"]};'
        f'padding:18px 24px;border-radius:10px}}'
        f'.{sid}-chip{{font-family:{fonts["mono"]},monospace;font-size:28px;'
        f'letter-spacing:.1em;text-transform:uppercase;margin-right:10px}}')

    title = _esc(shot.get("title") or shot["scene"])
    scene_label = _esc(shot["scene"].upper())
    # Dialogue-only shots title by scene; showing it again in the big bar
    # duplicates the micro label and crowds the lower third — omit it then.
    show_bar = (shot.get("title") or shot["scene"]).strip().lower() != shot["scene"].strip().lower()
    bar_html = (
        f'    <div id="{sid}-bar" class="{sid}-bar clip" data-start="0.4" '
        f'data-duration="{slot - 0.6:.2f}" data-track-index="3">{title}</div>\n'
    ) if show_bar else ""
    bar_tween = (
        f'tl.fromTo("#{sid}-bar", {{opacity:0, x:-30}}, {{opacity:1, x:0, duration:0.5, ease:"power4.out"}}, 0.4);\n'
    ) if show_bar else ""
    page = f"{index + 1:02d} / {len(proj['shots']):02d}"
    return f"""<template>
<style>
#{sid}-root{{position:absolute;inset:0;background:{p["bg"]};overflow:hidden}}
.{sid}-img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.{sid}-micro{{position:absolute;top:56px;left:96px;font-family:{fonts["mono"]},monospace;font-size:28px;letter-spacing:.16em;color:{p["text"]};text-transform:uppercase;background:rgba(0,0,0,.78);padding:8px 16px;border-radius:8px}}
.{sid}-bar{{position:absolute;left:96px;bottom:64px;font-family:{fonts["display"]},system-ui,sans-serif;font-weight:700;font-size:44px;color:{p["text"]};border-left:6px solid {p["accent"]};padding-left:22px;max-width:1400px;text-shadow:0 2px 12px rgba(0,0,0,.8)}}
.{sid}-page{{position:absolute;right:96px;bottom:64px;font-family:{fonts["mono"]},monospace;font-size:28px;color:{p["text"]};letter-spacing:.14em;background:rgba(0,0,0,.78);padding:6px 14px;border-radius:8px}}
{caption_css}
</style>
<div id="root" data-composition-id="{sid}" data-width="1920" data-height="1080">
  <div id="{sid}-root">
    <img id="{sid}-img" class="{sid}-img" src="../assets/{img}" alt="" data-layout-allow-overflow>
    <div id="{sid}-micro" class="{sid}-micro clip" data-start="0.2" data-duration="{slot - 0.4:.2f}" data-track-index="2">{scene_label}</div>
{bar_html}    <div id="{sid}-page" class="{sid}-page clip" data-start="0.2" data-duration="{slot - 0.4:.2f}" data-track-index="4">{page}</div>
{chr(10).join(captions)}
    <audio id="{sid}-vo" class="clip" src="../assets/{vo}" data-start="{LEAD_S}" data-track-index="5" data-volume="1"></audio>
  </div>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
tl.fromTo("#{sid}-img", {{scale:1.0}}, {{scale:1.06, duration:{slot:.2f}, ease:"none"}}, 0);
tl.fromTo("#{sid}-micro", {{opacity:0, y:-14}}, {{opacity:1, y:0, duration:0.4, ease:"power3.out"}}, 0.2);
{bar_tween}tl.fromTo("#{sid}-page", {{opacity:0}}, {{opacity:1, duration:0.4, ease:"power2.out", immediateRender:false}}, 0.2);
window.__timelines["{sid}"] = tl;
</script>
</template>
"""


def _index_html(proj: dict, slots: list[float], kit: dict, music_name: str | None) -> str:
    total = round(sum(slots), 2)
    scenes = []
    t = 0.0
    for shot, slot in zip(proj["shots"], slots):
        scenes.append(
            f'      <div id="{shot["id"]}" data-composition-id="{shot["id"]}" '
            f'data-composition-src="compositions/{shot["id"]}.html" data-start="{t:.2f}" '
            f'data-duration="{slot:.2f}" data-track-index="1" data-width="1920" data-height="1080"></div>')
        t += slot
    music = ""
    if music_name:
        music = (f'      <audio id="music" src="assets/{music_name}" data-start="0" '
                 f'data-duration="{total}" data-track-index="0" '
                 f'data-volume="{kit["music"]["volume"]}"></audio>')
    return f"""<!doctype html>
<html lang="en" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: {kit["visual"]["palette"]["bg"]}; }}
      #root {{ width: 100%; height: 100%; position: relative; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1920" data-height="1080" data-fps="30">
{chr(10).join(scenes)}
{music}
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""


def build_film(proj: dict, kit: dict, pdir: Path) -> Path:
    hf = pdir / "hf"
    (hf / "compositions").mkdir(parents=True, exist_ok=True)
    (hf / "assets").mkdir(parents=True, exist_ok=True)
    (hf / "renders").mkdir(parents=True, exist_ok=True)

    slots = []
    for i, shot in enumerate(proj["shots"]):
        if not shot.get("image") or not shot.get("audio"):
            raise ValueError(f"shot {shot['id']} is missing image or voiceover")
        shutil.copyfile(shot["image"], hf / "assets" / Path(shot["image"]).name)
        shutil.copyfile(shot["audio"], hf / "assets" / Path(shot["audio"]).name)
        slot = max(MIN_SLOT_S, round((shot.get("duration") or 2.0) + PAD_S, 2))
        slots.append(slot)
        (hf / "compositions" / f"{shot['id']}.html").write_text(
            _scene_html(shot, proj, kit, slot, i))

    music_name = None
    if kit["music"]["mode"] == "file" and kit["music"].get("file"):
        msrc = Path(kit["music"]["file"]).expanduser().resolve()
        root = storyboard.data_root().resolve()
        bundled = (Path(__file__).resolve().parent.parent / "data").resolve()
        if not msrc.is_file() or (root not in msrc.parents and bundled not in msrc.parents):
            raise ValueError("music file must exist inside the studio data folder")
        music_name = "music" + msrc.suffix.lower()
        shutil.copyfile(msrc, hf / "assets" / music_name)

    if FONT_SRC.is_dir():
        (hf / "assets" / "fonts").mkdir(exist_ok=True)
        for f in FONT_SRC.glob("*.woff2"):
            shutil.copyfile(f, hf / "assets" / "fonts" / f.name)

    (hf / "index.html").write_text(_index_html(proj, slots, kit, music_name))
    (hf / "hyperframes.json").write_text(json.dumps({
        "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
        "paths": {"blocks": "compositions", "components": "compositions/components",
                  "assets": "assets"},
        "media": {"autoProxy": True},
    }, indent=2))
    return hf


def run(project_id: str) -> dict:
    proj = storyboard.load(project_id)
    kit = brands.get_kit(proj["brand"])
    pdir = storyboard.project_dir(project_id)
    proj["busy"] = "assembling"
    storyboard._save(pdir, proj)
    try:
        hf = build_film(proj, kit, pdir)
        # check exits nonzero when it finds anything; the report is the truth.
        try:
            _run([npx(), "hyperframes", "check", "--json"], 300, cwd=hf)
        except RuntimeError:
            pass
        reports = sorted((hf / ".hyperframes" / "artifacts" / "checks").glob("*.json"),
                         key=lambda p: p.stat().st_mtime)
        if not reports:
            raise RuntimeError("HyperFrames check produced no report")
        rep = json.loads(reports[-1].read_text())
        if not rep.get("ok", False):
            errs = []
            for sec in ("lint", "runtime", "layout", "motion", "contrast", "craft", "audio"):
                v = rep.get(sec)
                findings = v.get("findings", []) if isinstance(v, dict) else (v or [])
                for f in findings:
                    if isinstance(f, dict) and f.get("severity") == "error":
                        errs.append(str(f.get("message", ""))[:160])
            raise RuntimeError("HyperFrames check gate failed: " + "; ".join(errs[:5]))
        raw = hf / "renders" / "raw.mp4"
        _run([npx(), "hyperframes", "render", "-o", str(raw), "--quality", "looks"],
             RENDER_TIMEOUT_S, cwd=hf)
        if not raw.exists():
            raise RuntimeError("render produced no output")
        total = duration_of(raw)
        film = hf / "renders" / "film.mp4"
        fade_out = max(0.0, total - 0.6)
        _run([ffmpeg(), "-y", "-v", "error", "-i", str(raw),
              "-af", f"loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:d=0.4,"
                     f"afade=t=out:st={fade_out:.2f}:d=0.6",
              "-c:v", "copy", str(film)], 300)
        proj["film"] = str(film if film.exists() else raw)
        proj["film_duration"] = round(duration_of(Path(proj["film"])), 2)
        storyboard._save(pdir, proj)
    finally:
        proj["busy"] = None
        storyboard._save(pdir, proj)
    return storyboard.summary(proj)
