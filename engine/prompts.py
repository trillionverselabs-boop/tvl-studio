"""Prompt compilation — where the brand kit meets the script.

Image prompts = the shot's action (what the script asks for) + scene context
+ the kit's visual style-lock (empty for the script-driven kit) + character
consistency instructions pointing at the reference portraits. Portraits get
a neutral-background character-sheet prompt so they work as references.
"""

from __future__ import annotations


def _style_suffix(proj: dict, kit: dict) -> str:
    parts = []
    if proj.get("style"):
        parts.append(proj["style"])
    if kit["visual"].get("style_prompt"):
        parts.append(kit["visual"]["style_prompt"])
    return (" Visual style: " + " ".join(parts)) if parts else ""


def portrait_prompt(name: str, description: str, proj: dict, kit: dict) -> str:
    desc = description or f"a character named {name.title()}"
    return (
        f"Character reference sheet, single full-body portrait, neutral plain "
        f"background, even lighting, consistent design: {desc}.{_style_suffix(proj, kit)} "
        f"No text, no watermark, no other characters."
    )


def compile_prompts(proj: dict, kit: dict) -> None:
    """Fill every shot's image_prompt from action + dialogue + brand kit."""
    suffix = _style_suffix(proj, kit)
    for shot in proj["shots"]:
        speakers = []
        for line in shot["lines"]:
            c = line["character"]
            if c != "NARRATOR" and c not in speakers:
                speakers.append(c)
        base = shot.get("action") or ""
        if not base:
            # Dialogue-only shot: depict the speakers in the scene.
            cast_bits = []
            for c in speakers:
                d = (proj["cast"].get(c) or {}).get("description", "")
                cast_bits.append(f"{c.title()} ({d})" if d else c.title())
            base = ("Scene: " + ", ".join(cast_bits) + " — "
                    + shot["lines"][0]["text"]) if cast_bits else shot["title"]
        consistency = ""
        if speakers:
            consistency = (
                " Keep these characters exactly consistent with the reference "
                "images: " + ", ".join(speakers) + "."
            )
        direction = f" ({shot['direction']})" if shot.get("direction") else ""
        shot["image_prompt"] = (
            f"{base}{direction}.{consistency}{suffix} "
            f"Cinematic 16:9 composition, no text, no watermark."
        )
