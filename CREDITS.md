# Credits

- **HyperFrames** (HeyGen) — the deterministic composition/render engine the
  assembly step builds on. Loaded via npx; not vendored.
- **Kokoro-82M / kokoro-onnx** — local TTS voices, invoked through
  `npx hyperframes tts`.
- **FFmpeg** — concatenation, loudness normalization, thumbnails.
- **Imagination Studio by keys+Wasserman** (Keys/drowzeys and Sam Wasserman,
  Apache-2.0) — the *orchestration concepts* (script → shot list → generation →
  QA → assembly → library) inspired this pipeline's shape. **No code, prompts
  or assets from that repository are included here**; this is a clean-room
  implementation on Hermes + HyperFrames.
- **Hermes plugin scaffold** (example-plugin, MIT) — the package shape.
- TVL internal design language — Lisa's approved Validize look
  (`tvl-vault/docs/TVL-INTERNAL-DESIGN-LANGUAGE.md`).
