"""Project state — the storyboard store and the repeatable next-action machine.

A project is a folder under ``data_root()/projects/<id>`` holding
``project.json`` (script, brand kit, cast, shots, film path) plus assets.
Every mutation is a load -> change -> atomic save, so an agent, the desktop
UI and a cron job can drive the same project without racing on structure.

The state machine is deliberately simple and legible:
    portraits -> images -> voiceover -> assemble -> done
``next_action()`` returns exactly one structured step, so any bot can loop:
read next_action, do it, attach the result, repeat.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
import uuid
from pathlib import Path

from ..paths import data_root
from . import brands
from .script_parser import NARRATOR, parse_script

PROJECT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
SHOT_ID_RE = re.compile(r"^s\d{2,3}$")


def projects_dir() -> Path:
    d = data_root() / "projects"
    d.mkdir(parents=True, exist_ok=True)
    return d


def validate_project_id(project_id: str) -> str:
    if not isinstance(project_id, str) or not PROJECT_ID_RE.match(project_id):
        raise ValueError(f"invalid project id: {project_id!r}")
    return project_id


def validate_shot_id(shot_id: str) -> str:
    if not isinstance(shot_id, str) or not SHOT_ID_RE.match(shot_id):
        raise ValueError(f"invalid shot id: {shot_id!r}")
    return shot_id


def project_dir(project_id: str) -> Path:
    validate_project_id(project_id)
    p = (projects_dir() / project_id).resolve()
    root = projects_dir().resolve()
    if p.parent != root:
        raise ValueError(f"project path escapes data root: {project_id!r}")
    return p


def _save(pdir: Path, proj: dict) -> None:
    pdir.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(pdir), suffix=".tmp")
    with os.fdopen(fd, "w") as fh:
        json.dump(proj, fh, indent=2)
    os.replace(tmp, pdir / "project.json")


def load(project_id: str) -> dict:
    pdir = project_dir(project_id)
    p = pdir / "project.json"
    if not p.exists():
        raise ValueError(f"unknown project: {project_id!r}")
    return json.loads(p.read_text())


def list_projects() -> list[dict]:
    out = []
    for p in sorted(projects_dir().glob("*/project.json")):
        try:
            proj = json.loads(p.read_text())
            out.append(summary(proj))
        except (json.JSONDecodeError, OSError):
            continue
    return out


def summary(proj: dict) -> dict:
    shots = proj.get("shots", [])
    return {
        "id": proj["id"], "name": proj["name"], "brand": proj["brand"],
        "shots": len(shots),
        "imaged": sum(1 for s in shots if s.get("image")),
        "voiced": sum(1 for s in shots if s.get("audio")),
        "cast": list((proj.get("cast") or {}).keys()),
        "film": proj.get("film"),
        "status": status(proj),
    }


def status(proj: dict) -> str:
    if proj.get("film"):
        return "done"
    shots = proj.get("shots", [])
    if all(s.get("audio") for s in shots) and shots:
        return "ready-to-assemble"
    if all(s.get("image") for s in shots) and shots:
        return "voicing"
    return "storyboarding"


def create(name: str, script: str, brand: str = brands.DEFAULT_KIT,
           style: str = "") -> dict:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("project name is empty")
    kit = brands.get_kit(brand)
    parsed = parse_script(script)
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:48] or "film"
    pid = f"{slug}-{uuid.uuid4().hex[:6]}"
    pdir = project_dir(pid)
    (pdir / "assets").mkdir(parents=True, exist_ok=True)
    (pdir / "vo").mkdir(parents=True, exist_ok=True)

    cast_names = [n for n in parsed["cast"] if n != NARRATOR]
    voices = brands.assign_voices(cast_names, kit)
    cast = {}
    for cname in parsed["cast"]:
        cast[cname] = {
            "description": parsed["cast"][cname],
            "voice": kit["voice"]["narrator"] if cname == NARRATOR else voices[cname],
            "portrait": None,
        }
    # Dialogue speakers the CAST block didn't describe still get a voice.
    for shot in parsed["shots"]:
        for line in shot["lines"]:
            c = line["character"]
            if c not in cast:
                cast[c] = {"description": "", "voice": voices.get(c, kit["voice"]["narrator"]),
                           "portrait": None}

    proj = {
        "id": pid, "name": name.strip(), "brand": kit["id"], "style": style.strip(),
        "script": script, "mode": parsed["mode"], "cast": cast,
        "shots": [
            {**s, "image": None, "image_prompt": "", "audio": None, "duration": None}
            for s in parsed["shots"]
        ],
        "film": None, "busy": None,
    }
    from .prompts import compile_prompts
    compile_prompts(proj, kit)
    _save(pdir, proj)
    return proj


def set_brand(project_id: str, brand: str) -> dict:
    proj = load(project_id)
    kit = brands.get_kit(brand)
    proj["brand"] = kit["id"]
    # Re-assign voices for the new kit, keep portraits and images.
    cast_names = [n for n in proj["cast"] if n != NARRATOR]
    voices = brands.assign_voices(cast_names, kit)
    for cname, c in proj["cast"].items():
        c["voice"] = kit["voice"]["narrator"] if cname == NARRATOR else voices.get(
            cname, kit["voice"]["narrator"])
    from .prompts import compile_prompts
    compile_prompts(proj, kit)
    _save(project_dir(project_id), proj)
    return proj


def attach_image(project_id: str, shot_id: str, image_path: str) -> dict:
    proj = load(project_id)
    validate_shot_id(shot_id)
    src = Path(image_path).expanduser().resolve()
    if not src.is_file():
        raise ValueError(f"image file not found: {image_path}")
    if src.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
        raise ValueError(f"not an image file: {src.name}")
    shot = next((s for s in proj["shots"] if s["id"] == shot_id), None)
    if shot is None:
        raise ValueError(f"unknown shot {shot_id!r} in {project_id!r}")
    import shutil
    dst = project_dir(project_id) / "assets" / f"{shot_id}{src.suffix.lower()}"
    shutil.copyfile(src, dst)
    shot["image"] = str(dst)
    _save(project_dir(project_id), proj)
    return summary(proj)


def attach_portrait(project_id: str, character: str, image_path: str) -> dict:
    proj = load(project_id)
    cname = str(character).upper().strip()
    if cname not in proj["cast"]:
        raise ValueError(f"unknown character {character!r}")
    src = Path(image_path).expanduser().resolve()
    if not src.is_file():
        raise ValueError(f"portrait file not found: {image_path}")
    import shutil
    safe = re.sub(r"[^A-Z0-9]+", "_", cname)
    dst = project_dir(project_id) / "assets" / f"cast_{safe}{src.suffix.lower()}"
    shutil.copyfile(src, dst)
    proj["cast"][cname]["portrait"] = str(dst)
    _save(project_dir(project_id), proj)
    return summary(proj)


def next_action(proj: dict) -> dict:
    """One structured step for the agent loop. Pure — no side effects."""
    kit = brands.get_kit(proj["brand"])
    for cname, c in proj["cast"].items():
        if cname != NARRATOR and not c.get("portrait"):
            from .prompts import portrait_prompt
            return {
                "action": "generate_portrait", "character": cname,
                "prompt": portrait_prompt(cname, c.get("description", ""), proj, kit),
                "then": f"studio_attach_portrait(project={proj['id']!r}, character={cname!r}, image_path=<result>)",
            }
    for shot in proj["shots"]:
        if not shot.get("image"):
            refs = [proj["cast"][l["character"]]["portrait"]
                    for l in shot["lines"]
                    if l["character"] in proj["cast"]
                    and proj["cast"][l["character"]].get("portrait")]
            return {
                "action": "generate_image", "shot": shot["id"],
                "prompt": shot["image_prompt"],
                "reference_image_urls": refs[:4],
                "then": f"studio_attach_image(project={proj['id']!r}, shot_id={shot['id']!r}, image_path=<result>)",
            }
    if not all(s.get("audio") for s in proj["shots"]):
        return {"action": "voiceover",
                "then": f"studio_voiceover(project={proj['id']!r})"}
    if not proj.get("film"):
        return {"action": "assemble",
                "then": f"studio_assemble(project={proj['id']!r})"}
    return {"action": "done", "film": proj["film"]}
