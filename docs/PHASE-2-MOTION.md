# Phase 2 — Motion & Lip Sync (the "characters actually talk" upgrade)

**Status:** Probe 1 DONE 2026-11-19 (Lisa approved). Result: `video_generate` served
**fal-ai/pixverse/v6/image-to-video** (provider fal, despite `video_gen.provider: nous` —
the Portal path delegates video to FAL). 5 s, 1280×720, ~1.4 MB. Frame review: coherent,
cinematic, clean faces; minor hand/prop-intersection artifacts (watch for temporal flicker
on hands). **FAL requires a PUBLIC HTTPS image_url** — local paths fail with
file_download_error. Working pattern: upload the still to litterbox.catbox.moe (24 h
temporary host, `curl -F'reqtype=fileupload' -F'time=24h' -F'fileToUpload=@<png>'
https://litterbox.catbox.moe/resources/internals/api.php`), pass that URL, download the
returned fal.media MP4 locally. Probe clip: cache/scratch/tvl-motion-probe.mp4.
Lip-sync probes still awaiting approval.

## The upgrade in one sentence

Every shot's still becomes a moving clip (`video_generate`, image-to-video), dialogue
shots get a lip-sync pass against the Kokoro WAV we already record, and HyperFrames
assembles clips instead of stills — the whole Phase 1 pipeline stays.

## Pipeline delta

```
Phase 1:  script → storyboard → stills → VO → HyperFrames(stills) → film
Phase 2:  script → storyboard → stills → VO → animate(still, motion prompt, dur=VO)
                                   → lipsync(clip, shot WAV)  [dialogue shots only]
                                   → HyperFrames(clips) → film
```

New tools (to build):
- `studio_animate(project, shot_id?)` — per shot: `video_generate(image_url=shot.image,
  prompt=motion direction from shot.action/direction, duration=min(15, ceil(VO+1.7)))`.
  Store clip path + duration on the shot; keep the still as fallback.
- `studio_lipsync(project, shot_id?)` — dialogue shots: send clip + `shot.audio` to the
  chosen sync model; store the talking clip. Non-dialogue shots skip.
- `studio_assemble` — scene template switches from `<img>` push-in to `<video>` when a
  clip exists (muted — the VO track stays the audio source of truth).

## Model decisions (bench before committing)

| Step | Candidates | Cost | Decision gate |
|---|---|---|---|
| Motion | Portal `video_generate` (configured, provider nous) — Kling/WAN/Veo family | $0.042–0.40/s | **Probe 1:** one 5 s clip from the demo lab still (~$0.21–0.35). Confirms which model the subscription proxies + quality |
| Lip sync, cheap | Kling LipSync ($0.014/5 s increment, needs 2–10 s source clip, ~12 min processing) · LatentSync ($0.20/video ≤40 s) | ~$0.14–0.20 per 10 s | **Probe 2:** one dialogue shot, human-face test image first |
| Lip sync, from still | OmniHuman 1.5 ($0.16/s) · Kling Avatar v2 Pro ($0.115/s) · H3 Max ($0.05–0.32/s) | ~$1.15–1.60 per 10 s | Only if animate+sync two-step quality disappoints |
| Lip sync, broadcast | Sync Labs 2 Pro ($5/min) · HeyGen Precision ($0.10/s) | ~$0.83–1.33 per 10 s | Hero episodes only |

## Setup decisions needed from Lisa

1. **Probe 1 approval** (motion, ~$0.21–0.35) — the gate for everything else.
2. **Lip-sync access path:** lip sync is NOT in Hermes' unified `video_generate` surface.
   Options: (a) free fal.ai signup + `FAL_KEY` in the profile `.env` (direct, all sync
   models, pay-per-use); (b) confirm whether the Portal gateway proxies any sync model
   (UNVERIFIED — ask Nous/support or test); (c) HeyGen via the media-use skill (credits).
   Recommendation: (a) — one free signup, full model choice, costs visible per call.
3. **Character realism:** sync models are trained on human faces. The Calvin story lane
   (human characters) fits; stylized explainer characters may not sync well — for those,
   motion + captions stays the right look.

## Cost envelope (per minute of finished film)

| Tier | Motion | Lip sync | Total/min |
|---|---|---|---|
| Explorer (Kling Turbo + Kling LipSync) | ~$2.50 | ~$0.85 | **~$3.40** |
| Drama (WAN/Kling Pro + OmniHuman) | ~$3–4 | ~$6–8 | **~$10–12** |
| Cinema (Veo 3 + Sync Pro) | ~$24 | ~$5 | **~$29** |

Doctrine: the 5x gate ((RPM × views) / asset cost ≥ 5) applies before any publish-lane
spend; internal Academy explainers can stay Phase 1 ($0.20–0.50/min) indefinitely.

## Risks

- 15 s clip cap per call → long dialogue shots split into sub-clips or stay still+push-in.
- Kling LipSync ~12 min processing per clip → batch overnight (night-shift cron pattern).
- Generated motion is probabilistic → keep the still fallback; re-roll budget per shot.
- Audio: clips render muted; the Kokoro VO + ffmpeg mix remains the single audio truth
  (no drift, captions stay timed to the WAV).
