"""Script -> storyboard parser.

Understands three shapes, in priority order:

1. Screenplay-ish: ``INT./EXT.`` scene headings, ``CHARACTER: dialogue``
   lines (character names uppercase), ``CAST: NAME — description`` lines,
   parentheticals ``(beat)`` kept as direction, other prose = action/visual.
2. Markdown scenes: ``## Scene: title`` headings, same dialogue/CAST rules.
3. Plain prose: paragraphs become shots narrated by the kit's narrator.

Every shot carries the dialogue lines (with speakers), the action text that
becomes the image prompt, and the scene it belongs to. Nothing is generated
here — parsing is pure and deterministic so the same script always yields the
same storyboard.
"""

from __future__ import annotations

import re

SCENE_HEADING_RE = re.compile(r"^(INT\.|EXT\.|INT/EXT\.|SCENE\b|##\s*Scene:?)\s*(.*)$", re.IGNORECASE)
DIALOGUE_RE = re.compile(r"^([A-Z][A-Z0-9 _.'-]{0,38}):\s+(.+)$")
CAST_RE = re.compile(r"^CAST:\s*([A-Z][A-Z0-9 _.'-]{0,38})\s*[-—:]+\s*(.+)$", re.IGNORECASE)
PAREN_RE = re.compile(r"^\(([^)]*)\)\s*$")
NARRATOR = "NARRATOR"


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_script(script: str) -> dict:
    """Return {scenes: [...], shots: [...], cast: {name: description}}."""
    if not isinstance(script, str) or not script.strip():
        raise ValueError("script is empty")
    lines = script.replace("\r\n", "\n").split("\n")

    cast: dict[str, str] = {}
    shots: list[dict] = []
    scene_title = ""
    scene_no = 0
    current: dict | None = None
    direction = ""

    def flush() -> None:
        nonlocal current
        if current is not None and (current["lines"] or current["action"]):
            shots.append(current)
        current = None

    def new_shot() -> dict:
        nonlocal current
        flush()
        current = {
            "id": f"s{len(shots) + 1:02d}",
            "scene": scene_title or f"Scene {scene_no or 1}",
            "title": "",
            "action": "",
            "direction": "",
            "lines": [],
        }
        return current

    prose_mode = not any(
        SCENE_HEADING_RE.match(l.strip()) or DIALOGUE_RE.match(l.strip())
        for l in lines if l.strip()
    )

    if prose_mode:
        for para in re.split(r"\n\s*\n", script.strip()):
            para = _clean(para)
            if not para:
                continue
            scene_no += 1
            shot = new_shot()
            shot["scene"] = f"Scene {scene_no}"
            shot["action"] = para
            shot["lines"] = [{"character": NARRATOR, "text": para}]
        flush()
        return {"shots": shots, "cast": cast, "mode": "prose"}

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        m_cast = CAST_RE.match(line)
        if m_cast:
            cast[_clean(m_cast.group(1)).upper()] = _clean(m_cast.group(2))
            continue
        m_scene = SCENE_HEADING_RE.match(line)
        if m_scene:
            flush()
            scene_no += 1
            scene_title = _clean(m_scene.group(2)) or f"Scene {scene_no}"
            new_shot()
            continue
        m_paren = PAREN_RE.match(line)
        if m_paren:
            direction = _clean(m_paren.group(1))
            if current is None:
                current = new_shot()
            current["direction"] = direction
            continue
        m_dial = DIALOGUE_RE.match(line)
        if m_dial:
            name = _clean(m_dial.group(1)).upper()
            if name in ("INT", "EXT", "CAST", "SCENE"):
                continue
            if current is None:
                current = new_shot()
            current["lines"].append({"character": name, "text": _clean(m_dial.group(2))})
            cast.setdefault(name, "")
            continue
        # Prose inside a screenplay = action/visual description.
        if current is None:
            current = new_shot()
        current["action"] = _clean((current["action"] + " " + line).strip())

    flush()

    # A scene with several dialogue-only shots stays one shot per scene unless
    # action lines split it; title each shot from its scene + first words.
    for shot in shots:
        first = shot["lines"][0]["text"] if shot["lines"] else shot["action"]
        shot["title"] = (first[:60] + "…") if len(first) > 60 else first
    if not shots:
        raise ValueError("no shots found in script")
    return {"shots": shots, "cast": cast, "mode": "screenplay"}
