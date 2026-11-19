# Image & motion models for TVL Studio — verified pricing and verdicts

**Date:** 2026-11-19 · **Author:** Charlene (research subagent deleg_f6447d44 gathered
sources; report written from its saved primary pages after it stalled on the final write).
**Rule:** every price below was read from a primary source today; anything not verified is
marked **UNVERIFIED**. Lisa decides the default *after* seeing outputs side by side (the bench).

## 1. Nous Portal catalogue (token-billed models)

Source: `https://inference-api.nousresearch.com/v1/models` — fetched 2026-11-19 17:44 EST,
413 models, saved at `cache/scratch/nous_models.json`.

Only **2 models output images**; both are Google Gemini image models billed per token:

| Model | Input /1M tok | Output /1M tok | Image output | Notes |
|---|---|---|---|---|
| `google/gemini-nano-banana-2.1` (Nano Banana 2.1) | $1.50 | $7.50 | $30 /1M image tokens ($0.00003/tok) | text+image → text+image; per-image cost depends on tokens/image — **UNVERIFIED** (not published in catalogue) |
| `google/gemini-3-pro-image` (Nano Banana Pro) | $2.00 | $12.00 | $120 /1M image tokens | reasoning-depth image model; same per-image caveat |

**Free variants in the catalogue: 5, all text** (`solar-mini4:free`, `hy4-flash:free`,
`step-3.7-flash:free`, `qwen4-max:free`, `longcat-2.5:free`). **There is no free image model
in the token catalogue.** Free web search (Perplexity Fast Search) is separate and free on
every plan via Hermes.

**How we actually generate images:** not through these token models — through the Portal
**Tool Gateway** (`image_gen.provider: nous`, currently `model: krea-3`), included with the
paid subscription, pay-as-you-use. Gateway per-use prices for subscribers: **UNVERIFIED**
(the four demo images on 2026-11-19 ran on Lisa's plan; billing treatment not confirmed).

## 2. The picker Lisa asked for already exists

`hermes tools → 🎨 Image Generation` shows a live model table (speed · strengths · price).
The **Nous Subscription** row spans the FAL catalog + native Krea 3/Krea 2 + Portal image
models. Source: https://hermes-agent.nousresearch.com/docs/user-guide/features/image-generation
(fetched 2026-11-19). Published table:

| Model | Speed | Strengths | Price |
|---|---|---|---|
| `fal-ai/flux-2/klein/9b` (FAL default) | <1 s | fast, crisp text | $0.006/MP |
| `fal-ai/flux-2-pro` | ~6 s | studio photorealism | $0.03/MP |
| `fal-ai/z-image/turbo` | ~2 s | bilingual EN/CN, 6B | $0.005/MP |
| `fal-ai/nano-banana-pro` | ~8 s | reasoning depth, text rendering | $0.15/image (1K) |
| `fal-ai/gpt-image-1.5` | ~15 s | prompt adherence | $0.034/image |
| `fal-ai/gpt-image-2` | ~20 s | SOTA text rendering, photorealism | $0.04–0.06/image |
| `fal-ai/ideogram/v3` | ~5 s | best typography | $0.03–0.09/image |
| `fal-ai/recraft/v4/pro/text-to-image` | ~8 s | design/brand systems | $0.25/image |
| `fal-ai/qwen-image` | ~12 s | LLM-based, complex text | $0.02/MP |
| `fal-ai/krea/v2/medium/text-to-image` | ~15–25 s | illustration/anime/painting | $0.030–0.035/image |
| `fal-ai/krea/v2/large/text-to-image` | ~25–60 s | photorealism, film texture | $0.060–0.065/image |

Free tool-pool accounts see FAL models only; **Krea and Portal models need the paid
subscription** (Lisa's account has it — krea-3 served today's demo).

## 3. fal.ai direct prices (primary source: each model page's billing JSON)

Extracted 2026-11-19 ~17:55–17:57 from the `endpointBilling` data embedded in fal.ai model
pages (saved HTML in `cache/scratch/`). MP = megapixel of output; edit endpoints bill input
MP too (inputs resized to 1 MP).

| Endpoint | Unit | Price |
|---|---|---|
| `fal-ai/flux/schnell` | MP | $0.003 |
| `fal-ai/flux-2/klein/4b` | MP | $0.005 |
| `fal-ai/flux-2/klein/4b/edit` | MP (in+out) | $0.010 |
| `fal-ai/flux-2/klein/4b/base` · `/base/edit` | MP | $0.009 |
| `fal-ai/flux-2/klein/4b/distilled/edit` | MP | $0.014 |
| **`fal-ai/flux-2/klein/9b`** | MP | **$0.006** |
| `fal-ai/flux-2/klein/9b/edit` | MP (in+out) | $0.011 |
| `fal-ai/flux-2/flash` | MP | $0.005 |
| `fal-ai/flux-2` (dev) | MP | $0.012 |
| `fal-ai/flux-2-pro` · `/outpaint` | processed MP | $0.030 |
| `fal-ai/flux-2-max/edit` | processed MP | $0.070 |
| `blackforestlabs/flux-3/klein/text-to-image` · `/edit-image` | MP | $0.009 |
| `blackforestlabs/flux-3/text-to-image` | MP | $0.048 |
| **`fal-ai/z-image/turbo`** · `/image-to-image` | MP | **$0.005** |
| `fal-ai/z-image/turbo/controlnet/lora` | MP | $0.010 |
| `fal-ai/z-image/base` | MP | $0.010 |
| `bytedance/seedream/v5/flash/edit` | image | $0.027 |
| `bytedance/seedream/v5/pro/us/text-to-image` | image ≤1536² | $0.0675 |
| `fal-ai/wan/v2.7/text-to-image` | image | $0.030 |

Name check: **"FLUX 2 Klein 9B" is real** (`fal-ai/flux-2/klein/9b`); **"Z Image Turbo" is
real** (`fal-ai/z-image/turbo`, Alibaba). Both names Lisa used resolve. fal page data marks
the Klein endpoints `licenseType: commercial`; upstream BFL licence terms should be checked
before any redistribution of weights (we only call APIs, so this is informational).

## 4. Krea (our current backend)

Source: https://www.krea.ai/docs/developers/krea-3/overview.md (fetched 2026-11-19).
**Krea 3 official per-generation pricing:**

| Component | 1K output | 2K output |
|---|---|---|
| Base price | $0.03 | $0.06 |
| Each 1K reference image | +$0.02 | +$0.02 |
| Each 2K reference image | +$0.07 | +$0.07 |
| `high` thinking | +$0.02 | +$0.02 |
| `ultra` thinking | — | +$0.20 |

4K = 2K + $0.04. Direct Krea API: pay-as-you-go, $5 minimum top-up, no subscription
(https://www.krea.ai/docs/developers/api-keys-and-billing.md). REST async jobs + webhooks —
fits an agent pipeline. Via Portal it is a subscription gateway model (per-use billing
**UNVERIFIED**, §1). Krea 3's strength is plain-language **editing** and expressive styles;
it served today's 4 demo images (~$0.20 at list: 2 portraits × $0.03 + 2 shots × ($0.03 + 2×$0.02)).

## 5. Verdict table (cost per ~1MP image, plain language)

| Option | ≈Cost/image | Quality signal | Commercial | Verdict |
|---|---|---|---|---|
| FLUX.2 Klein 9B (fal/Portal) | **$0.006** t2i · $0.011 edit | <1 s, crisp text; Hermes default | API use ok | **Cost-effective workhorse** for batch shots |
| Z-Image Turbo | $0.005 | ~2 s, bilingual; quality vs Klein = bench it | API use ok | Cheapest candidate; bench before trusting |
| FLUX.2 Klein 4B | $0.005 | smaller sibling of 9B | API use ok | Only if bench shows it holds up |
| Krea 3 (current) | $0.03 + $0.02/ref | best-in-class editing, expressive style; proven in our demo | hosted API terms | **Keep for edits/character work** until bench says otherwise |
| Seedream v5 Flash | $0.027/edit | ByteDance; strong edits | API use ok | Mid-price edit alternative |
| Nano Banana Pro | $0.15 (1K, fal) | reasoning depth, text rendering | API use ok | Premium shots only |
| FLUX.2 Pro / Max | $0.03–0.07/MP | photorealism | API use ok | Hero frames only |
| FLUX.3 Klein | $0.009/MP | newest Klein generation | API use ok | Bench against Klein 9B |

**Recommendation for "most cost-effective":** default batch shots to **FLUX.2 Klein 9B**
(~0.6¢) and keep **Krea 3** for reference-heavy edits — *after* the side-by-side bench
(same 3 prompts × each model, Lisa judges). Do not switch the default before seeing outputs.

## 6. Motion & lip sync (Phase 2 — answering "can they talk / can images move")

Verified 2026-11-19 from fal model pages and roundups (fal.ai/learn/tools/ai-lip-sync-generators,
nodetool.ai/blog/ai-voiceover-and-lip-sync, fal.ai/models/fal-ai/kling-video/lipsync/audio-to-video,
fal.ai/models/fal-ai/sync-lipsync/v2):

**Make stills move (image-to-video):** our `video_generate` tool is configured
(`video_gen.provider: nous`), 1–15 s clips, ≤1080p. Family prices: Kling 2.5 Turbo $0.042/s,
Turbo Pro $0.07/s, WAN 2.5 $0.05/s, Veo 3 $0.40/s (litellm fal catalogue + xAI docs table).
Which video models Lisa's subscription proxies: **UNVERIFIED — needs one probe.**

**Lip sync (image/video + our Kokoro WAV → talking clip):**

| Model | Input | Price | 10 s clip |
|---|---|---|---|
| Kling LipSync | 2–10 s video + audio | $0.014 per 5 s increment | $0.14 (cheapest; ~12 min processing) |
| LatentSync (open source) | video + audio ≤40 s | $0.20/video | $0.20 |
| PixVerse Lipsync | video + audio/text | $0.04/s | $0.40 |
| VEED Lipsync | video + audio | $0.07/s | $0.70 |
| HeyGen Lipsync Precision | video + audio | $0.10/s | $1.00 |
| Sync Lipsync 2 / Pro / 3 | video + audio | $3 / $5 / $8 per min | $0.50 / $0.83 / $1.33 |
| **Talking from ONE still:** H3 Max Lip Sync | image + audio | $0.05–0.32/s by res | $1.60 @1080p |
| VEED Fabric 1.0 | image + audio | $0.08–0.15/s | $1.50 @720p |
| Kling AI Avatar v2 Pro | image + audio | $0.115/s | $1.15 |
| OmniHuman 1.5 (ByteDance) | image + audio | $0.16/s | $1.60 |

**Caveats (honest):** (1) lip-sync models are trained on human faces — our stylized robot may
sync poorly; the Calvin story lane (human characters) is the right fit. (2) Lip sync is NOT in
Hermes' unified `video_generate` surface — it needs fal direct (own FAL_KEY) or a dedicated
tool/plugin; whether the Portal gateway proxies any sync model is **UNVERIFIED**.
(3) Drama-grade cost reality: 1 min of motion ≈ $2.50–4 (Kling/WAN tier); + lip sync ≈ $1–8/min;
Veo-tier ≈ $24+/min. The doctrine 5x gate applies before any publish-lane spend.

## 7. How we verified

- Nous catalogue: `curl https://inference-api.nousresearch.com/v1/models`, 2026-11-19 17:44 EST (413 models).
- fal prices: `endpointBilling` JSON inside each fal.ai model page HTML, fetched 17:55–17:57 EST.
- Krea: official docs pages (overview, api-keys-and-billing), fetched ~18:20 EST.
- Hermes picker/table: official image-generation + tool-gateway docs, fetched ~18:20 EST.
- Lip-sync/video: fal model pages + two independent roundups, fetched ~18:30 EST.
- Live proof: 4 images generated today via `image_generate` → provider `krea`, model `krea-3`.

## 8. Limitations

- Portal gateway per-use subscriber prices: UNVERIFIED (docs say pay-as-you-use, no public rate card found).
- Nano Banana per-image token counts: UNVERIFIED.
- Quality rankings are signals, not measurements — the bench (same prompts, side-by-side outputs) decides.
- Prices move fast; re-fetch before any spend commitment. All figures are list rates on 2026-11-19.
