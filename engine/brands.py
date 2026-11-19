"""Brand kits — one named branding applied across images, video, text, voices, music.

A kit is a JSON file. Bundled kits ship in ``data/brands/`` and are copied into
the data root on first use; user/agent-added kits live in the data root only.
The app chrome is always TVL-branded; the kit brands the *media*, and the
default kit ("script-driven") deliberately leaves visuals to the script.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from ..paths import data_root

KIT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")

# Kokoro voices shipped by `npx hyperframes tts` (verified 2026-11-19, v0.9.70).
VOICE_POOL = [
    "af_heart", "af_nova", "af_sky", "am_adam", "am_michael", "bf_emma",
    "bf_isabella", "bm_george", "ef_dora", "ff_siwis", "jf_alpha", "zf_xiaobei",
]

DEFAULT_KIT = "script-driven"


def _bundled_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "brands"


def brands_dir() -> Path:
    d = data_root() / "brands"
    d.mkdir(parents=True, exist_ok=True)
    # Seed bundled kits once; never overwrite a kit the user has edited.
    for src in _bundled_dir().glob("*.json"):
        dst = d / src.name
        if not dst.exists():
            shutil.copyfile(src, dst)
    return d


def validate_kit_id(kit_id: str) -> str:
    if not isinstance(kit_id, str) or not KIT_ID_RE.match(kit_id):
        raise ValueError(f"invalid brand kit id: {kit_id!r}")
    return kit_id


def _normalize(kit: dict) -> dict:
    """Fill every field so consumers never branch on missing keys."""
    kit = dict(kit)
    kit.setdefault("name", kit.get("id", "brand"))
    visual = dict(kit.get("visual") or {})
    visual.setdefault("style_prompt", "")
    palette = dict(visual.get("palette") or {})
    for key, fallback in {
        "bg": "#0b0f14", "card": "#111827", "accent": "#22d3ee",
        "accent2": "#8b5cf6", "success": "#34d399", "text": "#f1f5f9",
        "muted": "#94a3b8",
    }.items():
        palette.setdefault(key, fallback)
    visual["palette"] = palette
    fonts = dict(visual.get("fonts") or {})
    fonts.setdefault("display", "Inter")
    fonts.setdefault("body", "Inter")
    fonts.setdefault("mono", "JetBrains Mono")
    visual["fonts"] = fonts
    kit["visual"] = visual

    voice = dict(kit.get("voice") or {})
    narrator = voice.get("narrator", "af_heart")
    voice["narrator"] = narrator if narrator in VOICE_POOL else "af_heart"
    pool = [v for v in (voice.get("pool") or []) if v in VOICE_POOL]
    voice["pool"] = pool or [v for v in VOICE_POOL if v != voice["narrator"]]
    speed = voice.get("speed", 1.0)
    try:
        speed = float(speed)
    except (TypeError, ValueError):
        speed = 1.0
    voice["speed"] = min(1.5, max(0.7, speed))
    kit["voice"] = voice

    music = dict(kit.get("music") or {})
    mode = music.get("mode", "none")
    music["mode"] = mode if mode in ("none", "file") else "none"
    music.setdefault("file", "")
    try:
        music["volume"] = min(0.5, max(0.05, float(music.get("volume", 0.18))))
    except (TypeError, ValueError):
        music["volume"] = 0.18
    kit["music"] = music

    text = dict(kit.get("text") or {})
    text.setdefault("tone", "")
    try:
        text["caption_max_chars"] = int(text.get("caption_max_chars", 90))
    except (TypeError, ValueError):
        text["caption_max_chars"] = 90
    kit["text"] = text
    return kit


def list_kits() -> list[dict]:
    kits = []
    for p in sorted(brands_dir().glob("*.json")):
        try:
            kits.append(_normalize(json.loads(p.read_text())))
        except (json.JSONDecodeError, OSError):
            continue
    return kits


def get_kit(kit_id: str) -> dict:
    validate_kit_id(kit_id)
    p = brands_dir() / f"{kit_id}.json"
    if not p.exists():
        raise ValueError(f"unknown brand kit: {kit_id!r} (have: "
                         f"{', '.join(k['id'] for k in list_kits())})")
    return _normalize(json.loads(p.read_text()))


def save_kit(kit: dict) -> dict:
    kit_id = validate_kit_id(str(kit.get("id", "")))
    kit = _normalize({**kit, "id": kit_id})
    p = brands_dir() / f"{kit_id}.json"
    p.write_text(json.dumps(kit, indent=2))
    return kit


def assign_voices(cast_names: list[str], kit: dict) -> dict[str, str]:
    """Deterministic voice per character: kit pool in order, narrator excluded."""
    pool = [v for v in kit["voice"]["pool"] if v != kit["voice"]["narrator"]]
    out = {}
    for i, name in enumerate(cast_names):
        out[name] = pool[i % len(pool)] if pool else kit["voice"]["narrator"]
    return out
