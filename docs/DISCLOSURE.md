# Disclosure (catalog rule 13)

- **Network calls:** the plugin itself makes none directly. Image generation is
  performed by the **host's `image_generate` tool** (the agent calls it; the
  plugin only stores the returned file). HyperFrames assembly loads GSAP from
  `cdn.jsdelivr.net` inside the render page (same as every HyperFrames project)
  and npx may fetch the HyperFrames package on first use.
- **Reads outside the plugin's data dir:** bundled brand kits and fonts inside
  the plugin tree; shot/portrait source files the agent attaches (copied in);
  a kit music file only if it resolves inside the data dir; the TTS venv at
  `TVL_STUDIO_TTS_PYTHON` or `~/work/arena-demo-video/.venv` (executed, not read
  for secrets). No Hermes config/auth files are ever read.
- **Shell commands:** list-argument subprocesses (no shell): `npx hyperframes
  tts|check|render`, `ffmpeg`, `ffprobe`. All bounded by timeouts.
- **Background processes:** none persistent. Voiceover/assembly run inside the
  request/tool call with a `busy` flag; no daemon, no auto-update, no telemetry.
- **Stored credentials:** none — no `.env`, no `auth.json`, no vendor tokens.
- **Model requirements:** no LLM calls from the plugin. Images use whatever
  image model the host has configured (Portal credits apply — the board says
  so before the hand-off). TTS/render are local and free. On TTS/render failure
  the tool returns a JSON error naming the stage; nothing is fabricated.
