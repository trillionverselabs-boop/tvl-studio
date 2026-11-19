"""Agent tools — the repeatable script-to-film pipeline.

Rules (catalog-checked):
1. Model-controlled ids are validated against the minted format before they
   touch a path; every write stays inside data_root().
2. A refusal is data: handlers return {"error": "..."} JSON, never raise.

The agent loop: studio_import_script -> studio_status (read next_action) ->
generate the image with the host's image_generate tool -> studio_attach_image
-> repeat until next_action is voiceover -> studio_voiceover -> studio_assemble.
"""

from __future__ import annotations

import json

from .engine import assemble, brands, storyboard, voiceover


def _ok(payload: dict) -> str:
    return json.dumps(payload)


def _err(exc: Exception) -> str:
    return json.dumps({"error": str(exc)})


def register_tools(ctx) -> None:
    def tool(name, description, properties, required, handler):
        ctx.register_tool(
            name=name, toolset="tvl_studio",
            schema={"name": name, "description": description,
                    "parameters": {"type": "object", "properties": properties,
                                   "required": required}},
            handler=handler)

    def h_import(params, **kw):
        try:
            proj = storyboard.create(
                name=str(params.get("name", "")),
                script=str(params.get("script", "")),
                brand=str(params.get("brand", brands.DEFAULT_KIT)),
                style=str(params.get("style", "")))
            return _ok({"project": storyboard.summary(proj),
                        "cast": proj["cast"],
                        "next_action": storyboard.next_action(proj)})
        except Exception as exc:
            return _err(exc)

    tool("studio_import_script",
         "Import a script into TVL Studio and build its storyboard. Understands "
         "screenplay format (INT./EXT. headings, CHARACTER: dialogue, CAST: name — "
         "description), markdown scenes, or plain prose (narrated). Returns the "
         "project id, cast with voices, and the first next_action. Then loop: "
         "studio_status -> do next_action -> attach results.",
         {"name": {"type": "string", "description": "Project/film name."},
          "script": {"type": "string", "description": "The full script text."},
          "brand": {"type": "string", "description": "Brand kit id (studio_brands lists them). Default 'script-driven' lets the script set the visuals; 'tvl' applies TVL branding to all media."},
          "style": {"type": "string", "description": "Optional extra visual style line for this film only."}},
         ["name", "script"], h_import)

    def h_list(params, **kw):
        try:
            return _ok({"projects": storyboard.list_projects()})
        except Exception as exc:
            return _err(exc)

    tool("studio_list", "List TVL Studio projects with their status.", {}, [], h_list)

    def h_status(params, **kw):
        try:
            proj = storyboard.load(str(params.get("project", "")))
            return _ok({"project": storyboard.summary(proj),
                        "cast": proj["cast"],
                        "shots": [{"id": s["id"], "scene": s["scene"],
                                   "title": s["title"], "lines": s["lines"],
                                   "image_prompt": s["image_prompt"],
                                   "image": s["image"], "audio": s["audio"],
                                   "duration": s["duration"]} for s in proj["shots"]],
                        "next_action": storyboard.next_action(proj)})
        except Exception as exc:
            return _err(exc)

    tool("studio_status",
         "Read a project's storyboard and the single next_action to perform. "
         "next_action tells you exactly which portrait/image to generate (with "
         "prompt and reference images), or to run voiceover/assemble.",
         {"project": {"type": "string", "description": "Project id from studio_import_script."}},
         ["project"], h_status)

    def h_attach_image(params, **kw):
        try:
            return _ok(storyboard.attach_image(
                str(params.get("project", "")), str(params.get("shot_id", "")),
                str(params.get("image_path", ""))))
        except Exception as exc:
            return _err(exc)

    tool("studio_attach_image",
         "Attach a generated image file to a shot (after calling image_generate "
         "with the shot's image_prompt). Copies it into the project.",
         {"project": {"type": "string"}, "shot_id": {"type": "string"},
          "image_path": {"type": "string", "description": "Absolute path or URL-local file returned by image_generate."}},
         ["project", "shot_id", "image_path"], h_attach_image)

    def h_attach_portrait(params, **kw):
        try:
            return _ok(storyboard.attach_portrait(
                str(params.get("project", "")), str(params.get("character", "")),
                str(params.get("image_path", ""))))
        except Exception as exc:
            return _err(exc)

    tool("studio_attach_portrait",
         "Attach a character reference portrait (generated with image_generate "
         "from next_action's portrait prompt). Later shot images use it as a "
         "reference for character consistency.",
         {"project": {"type": "string"}, "character": {"type": "string"},
          "image_path": {"type": "string"}},
         ["project", "character", "image_path"], h_attach_portrait)

    def h_voiceover(params, **kw):
        try:
            return _ok(voiceover.run(str(params.get("project", "")),
                                     params.get("shot_id")))
        except Exception as exc:
            return _err(exc)

    tool("studio_voiceover",
         "Record voiceovers with local Kokoro TTS — one voice per character from "
         "the brand kit, free and offline. Concatenates each shot's lines and "
         "measures durations. Takes ~10-30s per shot.",
         {"project": {"type": "string"},
          "shot_id": {"type": "string", "description": "Optional: re-record one shot."}},
         ["project"], h_voiceover)

    def h_assemble(params, **kw):
        try:
            return _ok(assemble.run(str(params.get("project", ""))))
        except Exception as exc:
            return _err(exc)

    tool("studio_assemble",
         "Assemble the film: builds a HyperFrames composition from the "
         "storyboard (images + captions + voiceover + brand-kit music), passes "
         "the check gate, renders MP4, normalizes loudness with ffmpeg. Takes "
         "1-5 minutes. Returns the film path — deliver it with MEDIA:<path>.",
         {"project": {"type": "string"}},
         ["project"], h_assemble)

    def h_brands(params, **kw):
        try:
            action = str(params.get("action", "list"))
            if action == "list":
                return _ok({"brands": [
                    {"id": k["id"], "name": k["name"],
                     "style_prompt": k["visual"]["style_prompt"],
                     "narrator": k["voice"]["narrator"],
                     "music": k["music"]["mode"]} for k in brands.list_kits()]})
            if action == "save":
                kit = params.get("kit")
                if not isinstance(kit, dict):
                    return _err(ValueError("kit must be an object"))
                return _ok({"saved": brands.save_kit(kit)})
            if action == "apply":
                return _ok(storyboard.set_brand(
                    str(params.get("project", "")), str(params.get("brand", ""))))
            return _err(ValueError(f"unknown action {action!r}"))
        except Exception as exc:
            return _err(exc)

    tool("studio_brands",
         "Brand kits: one named branding applied across images (style-lock), "
         "video (palette/fonts), voices (narrator + character pool) and music. "
         "action=list|save|apply. save takes a full kit object {id, name, "
         "visual:{style_prompt,palette,fonts}, voice:{narrator,pool,speed}, "
         "music:{mode:none|file,file,volume}, text:{tone,caption_max_chars}}.",
         {"action": {"type": "string", "enum": ["list", "save", "apply"]},
          "kit": {"type": "object", "description": "For save: the full kit."},
          "project": {"type": "string", "description": "For apply."},
          "brand": {"type": "string", "description": "For apply: kit id."}},
         ["action"], h_brands)
