---
name: tvl-studio
description: Use when making a film from a script with TVL Studio (storyboard, images, voices, render).
version: 0.1.0
author: Trillionverse Labs
license: MIT
metadata:
  hermes:
    tags: [tvl, video, storyboard, tts, hyperframes]
---

# TVL Studio — the repeatable script-to-film loop

Tools: `studio_import_script`, `studio_list`, `studio_status`,
`studio_attach_image`, `studio_attach_portrait`, `studio_voiceover`,
`studio_assemble`, `studio_brands`. The desktop board lives at **TVL Studio**
in the left nav; its buttons hand the image loop to the focused session.

## The loop (any agent or bot can run it)

1. `studio_import_script(name, script, brand?, style?)` — parses screenplay
   (`INT./EXT.` headings, `CHARACTER: dialogue`, `CAST: NAME — description`),
   markdown scenes, or plain prose. Returns project id + first `next_action`.
2. Read `studio_status(project)` → `next_action`:
   - `generate_portrait` / `generate_image`: call the host's **image_generate**
     with the given `prompt` and `reference_image_urls` (portraits keep
     characters consistent; ≤4 refs). Attach the returned file with
     `studio_attach_portrait` / `studio_attach_image`. Repeat.
   - `voiceover`: call `studio_voiceover(project)` — local Kokoro TTS, one
     voice per character from the brand kit, free. ~10–30 s/shot.
   - `assemble`: call `studio_assemble(project)` — HyperFrames composition,
     check gate, render, ffmpeg loudness finish. 1–5 min.
   - `done`: deliver the film with `MEDIA:<film path>`.
3. Never fabricate an image or audio path — attach only files that exist.

## Brand kits

`studio_brands(action=list|save|apply)` — one kit brands all four media:
image style-lock (`visual.style_prompt`), video palette/fonts, voices
(`voice.narrator` + `pool`), music (`music.mode: none|file`). Bundled:
`tvl` (TVL look) and `script-driven` (default; visuals follow the script).
The app UI is always TVL-branded regardless of kit.

## Limits (honest, verified 2026-11-19)

- 12 Kokoro voices; characters beyond that share voices. No cloning/lip-sync.
- Images: host image_generate (Portal) — 1K/2K, ≤4 references; credits apply.
- Generated live-action clips are NOT part of this pipeline yet (Portal
  video_generate 1–15 s is a later phase); motion = HyperFrames animation.
- Music: kit file only (inside the data dir); no auto-composed score yet.
- Film length: no hard cap; render time and 30 GB RAM are the real limits.
