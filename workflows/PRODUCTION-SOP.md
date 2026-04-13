# Production SOP — AI Cinema Studio Engine

> **Version:** 2.0 (public release)
> **Scope:** End-to-end production governance — creative brief → published deliverables
> **Quality benchmark:** Professional cinematic output. Photo-real, deliberate lens and light choices, proper sound design, real-camera feel. No "AI avatar" look.
> **Architecture mapping:** Five-layer cinema engine grouped into three governance phases — Pre-production → Production → Post-production.

This SOP is the governance layer of the engine. It is the rulebook every commercial-quality production must follow from A to Z. The engine will execute any step you skip, but the output quality will degrade in proportion to how much of this SOP you ignore. Treat the phase gates as non-negotiable.

---

## How This SOP Works

Every production follows this sequence. No phase starts until the previous phase gate is cleared.

| Studio Phase | Engine Layers | Core Systems |
|---|---|---|
| **Pre-production** | Layer 0 (Orchestration + Knowledge) + test renders from Layer 1 | Notion, Qdrant, Claude, Firecrawl, N8N |
| **Production** | Layers 1–3 (Generation + Virtual Production + Audio) | fal.ai, Muapi/Open Generative AI, ComfyUI, HeyGen, ElevenLabs, N8N |
| **Post-production** | Layers 3–5 (Audio polish + Compositing + Distribution) | Remotion, FFmpeg, Topaz, N8N, publishing MCPs |

**26 steps. 3 phase gates. Human-in-the-loop sign-off required at every gate before moving forward.**

---

## Naming Conventions

All project assets follow this pattern so N8N, Remotion, and FFmpeg scripts can find them programmatically.

```
{client_slug}/{project_slug}/
├── brief/                  # Brief export, reference images, research
├── scripts/                # Script versions (v1, v2, final)
├── references/             # Mood boards, style refs, client samples
├── presets/                # Project-specific camera/lighting/FX overrides
├── renders/
│   ├── tests/              # Look tests (pre-production)
│   ├── raw/                # Raw model outputs (production)
│   ├── processed/          # Post-processed shots (graded, enhanced)
│   └── finals/             # Delivery masters per platform
├── audio/
│   ├── vo/                 # Voice-over takes
│   ├── sfx/                # Sound effects
│   └── music/              # Music tracks
├── assets/                 # Logos, overlays, lower thirds, fonts
└── production_order.json   # N8N production order (scenes → shots → specs)
```

**File naming:** `{project}_{scene}_{shot}_{version}.{ext}`
Example: `acme_s01_sh03_v2.mp4`, `acme_s01_sh03_v2_4k.mp4`

---

## Phase 0 — System Readiness Gate

**Before ANY production begins, verify the toolchain is connected and functional.** Do not proceed to Phase 1 until every required tool passes its verification check. A disconnected tool mid-production causes re-work that costs more than the time spent verifying upfront.

### Tool verification checklist

| Tool | Verification | Pass Criteria |
|------|------|---------------|
| Qdrant RAG | `python tools/populate_camera_presets.py --query "test"` | Returns results with relevance scores |
| fal.ai gateway | `python tools/fal_generate.py --check` | API responds, credits available |
| ElevenLabs MCP | Generate a 3-second test clip | MCP connected, audio returned |
| Muapi / Open Generative AI | Test call to any Lip Sync Studio model | Key valid, model responds |
| ComfyUI | MCP or REST to `localhost:8188` | Server responds with system info |
| HeyGen (backup) | `python tools/heygen_generate.py --check` | Key valid |
| FFmpeg | `ffmpeg -version` | Installed and on PATH |
| Remotion | `cd remotion && npm run dev` | Studio launches |
| LUT pipeline | `ls luts/**/*.cube \| wc -l` | 21 `.cube` files present |

### Cost philosophy verification

| Purpose | Use | Never Use |
|---------|-----|-----------|
| Iteration, testing, storyboards | Local/free models (Wan 2.6, ComfyUI, open TTS) | Paid video models |
| Final stills & character sheets | Nano Banana Pro or equivalent photoreal still model | — |
| Final video generation | Seedance 2.0 / Veo 3.1 / Kling 3.0 via pay-per-use | Monthly video subscriptions |
| Lip-sync (primary) | LatentSync or Muapi Lip Sync Studio, pay-per-use | Monthly subscription endpoints |
| Voice generation | ElevenLabs active plan | — |
| Upscaling | Topaz (one-time) or ComfyUI ESRGAN (free) | Cloud upscaling subscriptions |
| Color grading | FFmpeg + LUT pipeline (free) | — |
| Compositing | Remotion (free) + FFmpeg (free) | Paid NLE subscriptions |

**Rule:** No monthly subscriptions in the production pipeline. All model access is pay-per-use. The only recurring costs are voice-generation plan fees and infrastructure.

---

## PHASE 1 — PRE-PRODUCTION (Brief → Blueprint)

**Layers involved:** Layer 0 (Orchestration + Knowledge), test renders from Layer 1
**Typical duration:** 1–3 days
**Cost target:** Near-zero (research, scripting, free test renders)

### Step 1 — Intake & Scoping

Capture the creative brief in your project manager of choice (Notion recommended). Every field matters downstream.

**Required brief fields:** client name, project name, project slug, goals, key message, target audience (or reference to brand profile in Qdrant), deliverable formats (duration, aspect ratios, platforms), budget ceiling per finished minute, timeline (draft + final dates), approval workflow (who reviews, sign-off contact).

### Step 2 — Research & World Context

Ingest client and world context into Qdrant so every downstream prompt is brand-aware.

- Firecrawl MCP to scrape client site, competitor sites, reference URLs
- Crawl4AI MCP to ingest into Qdrant collections: `brand_profiles`, `shot_library`, `character_library`
- If client has an existing brand profile JSON, import it directly; otherwise build from scraped data

### Step 3 — Narrative & Structure

Lock the story before writing a single line of script.

- **Logline + synopsis** — one sentence + one paragraph, locked in the project doc
- **Structure + beat sheet** — 3-act (narrative), modular (commercial), or episodic (series), broken into sequences → scenes → beats
- **Script** — drafted by Claude Code from the beat sheet, informed by Qdrant brand context and any character voice governance; versioned; **locked by client approval** before Step 4 starts

### Step 4 — Character Development

Build the character system BEFORE any visual generation.

- **Character bible** — identity, backstory, visual anchors, voice settings, behavioral rules, ICP calibration. Stored in Notion.
- **Reference sheet** — minimum 10-view set (master, close-up, back, action, over-shoulder, side profiles, walking, full back, extreme close-up). Use client-provided images if available; otherwise generate via Nano Banana Pro or adapt via InstantID/IP-Adapter in ComfyUI.
- **Qdrant `character_library` entry** — voice, settings, reference image paths, LoRA/avatar IDs, version lock date. No changes without a version bump + approval.

### Step 5 — Worldbuilding & Design Language

Lock the visual language across shots.

- Environment references in `shot_library`
- Signature color palette, typography, motion language
- Project-specific camera/lighting overrides in `{project}/presets/`

### Step 6 — Shot List & Storyboard

Translate the script into a shot-by-shot plan.

- Shot list in the project doc: scene, shot, duration, camera body, lens, focal length, movement, lighting preset, effects, audio beats
- Storyboard stills via Nano Banana Pro or equivalent photoreal still model, 1 per shot minimum
- Each still becomes the **first-frame reference** for Step 14

### Step 7 — Cinematography Assembly (RAG Query)

For every shot, query Qdrant and assemble the full cinematography prompt.

```
camera_body + lens + focal_length + movement + lighting_preset + effects/style
```

Never hardcode these. They live in the `camera_presets`, `lighting_presets`, and `effects_presets` Qdrant collections (1,645 entries total across 8 collections). This is what makes output cinematic rather than generic.

### Step 8 — Audio Direction

Plan the audio track before production.

- Voice cast: assign voices (ElevenLabs) to characters; lock voice IDs and tuned settings
- Music direction: tempo, mood, genre tags from `music_library`
- SFX list: per beat, with timing anchors
- Dialogue vs. narration split documented

### Step 9 — Test Renders (Look Tests)

Burn-in the look before committing to full production.

- Pick 1 hero shot and 1 transition shot
- Render in both local/free path (Wan 2.6, ComfyUI) and paid path (Seedance 2.0) for comparison
- Lock the engine choice per shot-type before Phase 2

### Step 10 — Production Order (Machine-Readable)

Serialize the shot list into `production_order.json` that N8N can execute.

Every shot entry includes: scene, shot, duration_seconds, aspect_ratio, prompt (assembled from Step 7), reference_image_path, engine (`seedance-2`, `veo-3.1`, `kling-3.0`, `wan-2.6`, etc.), audio_refs, post_ops (LUT, upscale, relight), output_path.

### Step 11 — Engine Selection & Budget Lock

Per shot, confirm the right engine for the job.

| Shot type | Preferred engine |
|---|---|
| Stacked camera movements, audio-synced | Seedance 2.0 |
| Highest photoreal quality, talking scenes | Veo 3.1 |
| Multi-shot consistency, dialogue coverage | Kling 3.0 |
| Complex physical interactions | Sora 2 |
| Editorial character lock | Runway Gen-4.5 |
| Anime / stylized | Wan 2.6 + LoRAs |
| Long-form (60+ sec) on limited VRAM | FramePack |

Recompute cost estimate from the locked production order. **Share with client and get sign-off on the budget before generation starts.**

### Step 12 — Compliance & IP Review

Before any paid generation:

- Confirm all reference imagery is cleared (client-provided or public domain or licensed)
- Flag any third-party trademarks/logos/IP that appear — **do not generate them into shots without a direct license from the IP holder**
- Log the compliance check in the project doc

### Step 13 — 🚦 PHASE GATE 1 — Pre-production Sign-Off

**Human-in-the-loop required.** Production cannot proceed until the brief owner (or their designated approver) signs off in writing.

Sign-off artifacts: locked script, locked shot list, locked character bibles + reference sheets, locked cinematography prompts, production_order.json, cost estimate, compliance log.

---

## PHASE 2 — PRODUCTION (Blueprint → Raw Footage)

**Layers involved:** Layers 1–3 (Generation + Virtual Production + Audio)
**Typical duration:** 1–5 days depending on shot count and engine
**Cost target:** Majority of project budget lives here

### Step 14 — Reference-Frame Generation

For every shot that needs character or subject lock:

- Generate the first-frame still via Nano Banana Pro (or InstantID/IP-Adapter in ComfyUI if adapting from existing reference)
- Confirm character consistency against the reference sheet (Step 4)
- Save to `{project}/references/shot_frames/` — this is the anchor for the video model

### Step 15 — Video Generation (Layer 1)

Execute the production order via N8N → fal.ai / ComfyUI / HeyGen.

- First frame from Step 14 feeds the video model as the reference
- Cinematography prompt from Step 7 is the primary text prompt
- Stack up to 3 simultaneous camera movements on Seedance; use multi-shot lock on Kling for coverage
- Retry policy: 2 paid attempts max per shot; if still off, fall back to ComfyUI local path or re-brief the shot

### Step 16 — Virtual Cinematography Post (Layer 2)

For every raw shot that needs polish at the cinematography layer:

- IC-Light / Relight in ComfyUI for directional light, temperature, intensity corrections
- Style-transfer LoRAs for film stock emulation (Kodak Vision3, Fuji Eterna, 16mm reversal, 35mm negative)
- Deflicker for any AI-generated footage showing frame-to-frame inconsistency
- Motion LoRAs for trained-weight effects (zoom burst, whip pan, rack focus) when needed

### Step 17 — Voice & Audio Generation (Layer 3)

- **Dialogue / narration** — ElevenLabs with locked voice IDs and tuned settings from Step 8
- **SFX** — ElevenLabs SFX generation or equivalent, per the Step 8 SFX list
- **Music** — ElevenLabs music generation or licensed tracks, matched to the Step 8 mood/tempo
- **Speech-to-speech** for performance capture when the line needs specific emotion

### Step 18 — Lip-Sync (Talking-Head Shots)

If any shot involves a character speaking:

1. Generate the video (Step 15) with character + framing locked
2. Generate the voice take (Step 17)
3. Run lip-sync: LatentSync (primary) via fal.ai or Muapi Lip Sync Studio; fall back to Wan 2.6 native lip-sync for highest quality, or HeyGen Avatar IV as a premium backup
4. QC: watch at 100% and 200% speed, check for sync drift, jaw artifacts, eye flicker

### Step 19 — 🚦 PHASE GATE 2 — Production Sign-Off

**Human-in-the-loop required.** Post cannot start until every shot passes the shot-level QC checklist and the producer signs off.

Sign-off artifacts: every raw shot rendered, every audio asset generated, lip-sync approved, shot-level QC log with any accepted defects documented.

---

## PHASE 3 — POST-PRODUCTION (Footage → Published)

**Layers involved:** Layers 3–5 (Audio polish + Compositing + Distribution)
**Typical duration:** 1–2 days
**Cost target:** Minimal (mostly free/local tools)

### Step 20 — Assembly & Edit

Assemble the cut in FFmpeg or Remotion composition.

- Bring raw shots together per the production order
- First pass edit: duration, pacing, cut-point timing
- Transition templates from the library (cross dissolve, iris wipe, light leak, whip pan blur) applied per beat-sheet intention

### Step 21 — Color Grading

Apply the LUT pipeline.

- LOG → Rec.709 base conversion
- Film-stock emulation LUT (21 `.cube` files in `luts/`)
- Creative LUT (teal-orange, bleach bypass, day-for-night, etc.)
- Final correction LUT if needed

### Step 22 — Enhancement

- Topaz Video AI or ComfyUI ESRGAN for 2x/4x upscaling
- RIFE for frame interpolation (24 → 60fps) where motion smoothness matters
- Face enhancement on hero shots if the model output is soft

### Step 23 — Audio Finishing

- Mix: dialogue forward, SFX mid, music bed under
- Normalize to broadcast spec: **-16 LUFS** for social, **-23 LUFS** for broadcast
- Stereo check, true-peak limiter at -1dBTP

### Step 24 — Compositing & Branding (Remotion)

- Lower thirds, titles, motion graphics
- Logo overlays and end cards
- Subtitles/captions (from ElevenLabs Scribe transcription with diarization)
- Data viz if applicable

### Step 25 — Platform Packaging

- Aspect ratio variants: 16:9, 9:16, 1:1
- Platform-specific encodes: bitrate, codec, file size per platform spec
- Thumbnails: 1 per variant
- Metadata: title, description, tags, chapters (YouTube)

### Step 26 — 🚦 PHASE GATE 3 — Distribution & Human-in-the-Loop Publishing

**Human-in-the-loop required — mandatory.** No content is published automatically. Every deliverable must pass a named human reviewer before distribution, per the LEGAL.md terms.

- Final client review and written approval
- Publish via N8N scheduled workflow or publishing MCP (Blotato, YouTube Data API, etc.)
- Log to governance dashboard (production_orders + publishing_log tables)
- Archive masters, production_order.json, and all approvals

**Phase Gate 3 sign-off** closes the production.

---

## The Self-Improvement Loop

Every production feeds the engine.

1. Identify what broke or surprised you
2. Fix the tool or workflow
3. Update the affected Qdrant collection if the fix reveals a missing preset
4. Update this SOP if the process changed
5. Commit the change with the production ID in the message

The system gets stronger with every project.

---

## Governance Summary

| Gate | Phase | Sign-off required | Artifacts |
|---|---|---|---|
| Gate 1 | Pre-production complete | Yes (human-in-the-loop) | Locked script, shots, characters, prompts, budget |
| Gate 2 | Production complete | Yes (human-in-the-loop) | All raw shots + audio + lip-sync QC'd |
| Gate 3 | Post-production + publish | Yes (human-in-the-loop) | Final masters, client approval, publish log |

**If any gate is skipped, the engine will still run — but the output is no longer a governed production and the quality guarantees of this SOP no longer apply.**

This SOP is the difference between "AI generated a video" and "a studio delivered a commercial-quality film."
