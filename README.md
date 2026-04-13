<p align="center">
  <strong>AI Cinema Studio Prodcution Engine by PopTech Studio</strong>
</p>

<h1 align="center">AI Cinema Studio Prodcution Engine</h1>

<p align="center"><strong>Self-hosted, RAG-driven cinematic production. Camera presets, lighting simulation, effects chains, and multi-shot sequencing — powered by your own infrastructure.</strong></p>

<p align="center">
  <a href="#quick-start">Quick Start</a> &nbsp;&middot;&nbsp;
  <a href="#five-layer-architecture">Architecture</a> &nbsp;&middot;&nbsp;
  <a href="#production-workflows">Workflows</a> &nbsp;&middot;&nbsp;
  <a href="#installation--configuration">Install Guide</a> &nbsp;&middot;&nbsp;
  <a href="#production-sop">Production SOP</a> &nbsp;&middot;&nbsp;
  <a href="#engineering-ops-collaboration-engine">Ops Engine</a> &nbsp;&middot;&nbsp;
  <a href="#contributing">Contributing</a>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT"></a>
  <a href="https://poptechstudio.ai"><img src="https://img.shields.io/badge/site-poptechstudio.ai-blue" alt="Website"></a>
</p>

---

Replace subscription-based platforms like Higgsfield Cinema Studio and Arcads with a self-hosted pipeline where you only pay for the APIs you use. No monthly platform fees. The engine doesn't wrap a single model — it orchestrates dozens of them through a **virtual cinematography layer** powered by 1,645 RAG presets that make every generation cinematic rather than generic. See [LEGAL.md](LEGAL.md) for important disclaimers regarding third-party API fees.

**What makes this different:** Every video generation call assembles a cinematography prompt from a vector database: camera body + lens + focal length + movement + lighting setup + effects/style. A "cinematic dolly shot at golden hour" isn't a vague prompt — it's a precise technical directive assembled from RAG-matched presets for an ARRI Alexa Mini LF body, Cooke S7/i lens, 35mm focal length, slow dolly movement, golden hour three-point lighting, and Kodak Vision3 500T film stock grade.

**Who this is for:** Independent filmmakers, content studios, marketing agencies, and solo creators who want cinema-quality AI video without paying platform rent. If you can run Docker and Node.js, you can run a production studio.

---

## What You Get

| Layer | Capability | Tools |
|-------|-----------|-------|
| **Orchestration** | Workflow automation, cinematography RAG, project management | N8N (5 workflows, 67 nodes), Qdrant (1,645 presets), Notion |
| **Generation** | Multi-model video + image + avatar | fal.ai (Seedance 2.0, Kling 3.0, Veo 3.1), Muapi.ai (200+ models), local ComfyUI |
| **Virtual Production** | Camera, lighting, effects direction | 1,486 camera presets, 54 lighting setups, 105 effects/styles |
| **Audio** | Voice, SFX, music, lip-sync | ElevenLabs, 15-model lip-sync pipeline, open-source TTS |
| **Post-Production** | Compositing, color grading, upscaling | Remotion (3 templates, 7 compositions), FFmpeg (21 LUTs), Topaz Video AI |
| **Distribution** | Multi-platform publishing | N8N publisher (YouTube, Shorts, Reels, TikTok, LinkedIn) |

### Feature Comparison

| Capability | Subscription Platforms | PopTech Studio (self-hosted) |
|---|---|---|
| AI video generation | Credit-limited or per-video fee | Pay-per-use via fal.ai or free via local Wan 2.6 |
| Camera simulation | Platform UI (locked) | 1,486 open RAG presets + ComfyUI ControlNet |
| Multi-shot sequencing | Platform-dependent | N8N workflows + ComfyUI batch |
| Audio (voice, SFX, music) | Basic or N/A | ElevenLabs full platform + open-source local TTS |
| Color grading | Limited presets | FFmpeg 21-LUT pipeline |
| Publishing | Download only | Automated 6-platform via N8N |
| **Pricing model** | **Monthly subscription** | **Pay only for APIs you use** |

> **Note:** All third-party API pricing is set by the respective providers and subject to change. Review each provider's current pricing before use. See [LEGAL.md](LEGAL.md).

---

## Quick Start

**Time to install:** ~30 minutes for core engine. ~1 hour with all MCP servers and skills.

### Prerequisites

| Requirement | Version | Why |
|-------------|---------|-----|
| Python | 3.10+ | Pipeline scripts, RAG population, API wrappers |
| Node.js | 18+ | Remotion video rendering, N8N workflows |
| FFmpeg | 7+ | Color grading, video encoding, transitions |
| Docker | 20+ | Qdrant vector DB |
| Git | 2.30+ | Version control |

### Recommended LLM Setup

This engine is designed around a **two-agent collaboration model** using Claude:

| Role | Tool | What It Does |
|------|------|-------------|
| **CTO / Creative Director** | Claude Desktop (Cowork mode) | Reviews work, writes creative briefs, runs QC protocol, manages Notion tasks |
| **Lead Engineer** | Claude Code in VS Code | Picks up tasks, writes code, runs pipelines, builds workflows, submits deliverables |

The CTO directs from Cowork — dispatching tasks, reviewing submissions, making creative decisions. The Engineer executes in VS Code — building tools, wiring APIs, rendering video. They communicate through a file-based ops pipeline (see [Engineering Ops](#engineering-ops-collaboration-engine) below).

> **Other setups work too.** Any AI coding assistant that can read files and run Python/Node will work as the Engineer. The Cowork CTO role can be done manually if you prefer.

---

## Five-Layer Architecture

Every production flows through five layers, bottom-to-top. This is not optional — the layer sequence is what makes the output cinematic.

```
Layer 5 — Distribution          Automated multi-platform publishing
Layer 4 — Post-Production       Remotion compositing + FFmpeg LUT grading + upscaling
Layer 3 — Audio Production      Voice synthesis + SFX + music + lip-sync
Layer 2 — Virtual Production    RAG-assembled camera + lighting + effects direction
Layer 1 — AI Generation         Multi-model video/image/avatar creation
Layer 0 — Orchestration         N8N workflows + Qdrant RAG + Notion + brand profiles
```

**Layer 0 — Orchestration + Knowledge:** Qdrant vector DB with 1,645 cinematography presets across 8 collections. N8N workflow engine with 5 production workflows (67 nodes). Notion for project management and content calendars. This layer coordinates everything else.

**Layer 1 — AI Generation Engines:** Multi-model gateway. Seedance 2.0 for stacked camera movements with audio sync. Veo 3.1 for 4K 60fps highest quality. Kling 3.0 for multi-shot consistency. Wan 2.6 for free local generation. Sora 2 for physics simulation. Engine selection is content-driven — see [Model Selection](#model-selection).

**Layer 2 — Virtual Production (Core Differentiator):** This is the cinematography layer that replaces the Higgsfield UI. Every video generation call queries RAG for camera body, lens, focal length, movement, lighting setup, and effects/style — then assembles them into a precise technical prompt. 1,486 camera presets, 54 lighting setups, 105 effects/styles.

**Layer 3 — Audio Production:** ElevenLabs for voice synthesis, custom clones, SFX, and music. 15-model lip-sync pipeline ranked by quality (Wav2Lip through Wan 2.6 native). Open-source local TTS alternatives (Qwen3-TTS, F5-TTS, Chatterbox) for unlimited free generation.

**Layer 4 — Post-Production:** Remotion React-based compositing with 3 production templates and 7 shared components. FFmpeg LUT color grading pipeline with 21 LUT files (11 film stocks, 8 creative grades). Standard finishing chain: normalize LUT → film stock → creative grade → grain (0.12) → vignette (0.25). Topaz Video AI for 4K upscaling and frame interpolation.

**Layer 5 — Distribution:** N8N video publisher workflow dispatches to 6 platforms (YouTube, Shorts, Reels, TikTok, LinkedIn, feed posts) with per-platform metadata generation and aspect ratio variants (16:9, 9:16, 1:1). All publishes logged to MySQL governance dashboard.

---

## Production Workflows

5 N8N workflows, 67 nodes total. All structurally complete with API stubs ready for live wiring.

| Workflow | Nodes | File | Trigger | What It Does |
|----------|-------|------|---------|-------------|
| **Cinematic Commercial** | 20 | `workflows/n8n/cinematic-commercial-production.json` | Notion brief | Pull brief → RAG camera/lighting/FX → generate shots → composite → grade → publish |
| **Documentary** | 14 | `workflows/n8n/documentary-production.json` | Notion brief | Research topic → narrator script → B-roll generation → talking heads → composite |
| **Anime / Stylized** | 13 | `workflows/n8n/anime-production.json` | Notion brief | Character sheets → LoRA train → keyframes → AnimateDiff → style transfer → composite |
| **Kit Daily Content** | 12 | `workflows/n8n/kit-daily-content.json` | Cron (daily 9AM) | Pull calendar → write script → voice → video → overlays → 3 aspect ratios → publish |
| **Video Publisher** | 8 | `workflows/n8n/video-publisher.json` | Called downstream | Route to platforms → generate metadata → encode variants → publish → log |

The first 4 are production workflows triggered by Notion briefs or cron schedules. The Video Publisher is a distribution layer called downstream from any production workflow. Import all 5 into your N8N instance and wire your API credentials through the N8N credential store.

---

## Installation & Configuration

### Step 1 — Clone and Configure Environment

```bash
git clone git@github.com:PopTechStudio/cinema-studio-engine.git
cd cinema-studio-engine
cp .env.example .env
```

### Step 2 — Set API Keys

Edit `.env` with your keys. Only the first three are required for the core engine:

| Variable | Required | Purpose | Free Tier? |
|----------|----------|---------|-----------|
| `OPENAI_API_KEY` | **Yes** | Embeddings for RAG (text-embedding-3-small) | Pay-per-use |
| `QDRANT_API_KEY` | **Yes** | Vector DB authentication | Free (self-hosted) |
| `FAL_KEY` | **Yes** | Video/image generation gateway | Pay-per-use |
| `ELEVENLABS_API_KEY` | Recommended | Voice, SFX, music, transcription | Free tier available |
| `HEYGEN_API_KEY` | Optional | Avatar video (backup path) | Subscription (see provider) |
| `MUAPI_API_KEY` | Optional | 200+ model gateway, lip-sync | Pay-per-use |
| `NOTION_TOKEN` | Optional | Project management integration | Free tier available |

### Step 3 — Install Python Dependencies

```bash
pip install qdrant-client openai requests python-dotenv
```

### Step 4 — Deploy Qdrant Vector DB

```bash
# Docker (recommended) — on your VPS or local machine
docker run -d --name qdrant --restart unless-stopped \
  -p 127.0.0.1:6333:6333 -p 127.0.0.1:6334:6334 \
  -v /opt/qdrant/storage:/qdrant/storage \
  -e QDRANT__SERVICE__API_KEY=$QDRANT_API_KEY \
  qdrant/qdrant:latest
```

### Step 5 — Populate the Cinematography RAG (1,645 Presets)

This is the core differentiator. These presets are what make every generation cinematic.

```bash
# Camera presets (1,486 entries: 8 bodies x 11 lenses x 6 focal lengths x 3 apertures x 16 movements)
python tools/populate_camera_presets.py --generate
python tools/populate_camera_presets.py --upload --qdrant-key $QDRANT_API_KEY

# Lighting presets (54 entries: 33 setups with variations)
python tools/populate_lighting_presets.py --generate
python tools/populate_lighting_presets.py --upload --qdrant-key $QDRANT_API_KEY

# Effects presets (105 entries: film stocks, transitions, artistic styles)
python tools/populate_effects_presets.py --generate
python tools/populate_effects_presets.py --upload --qdrant-key $QDRANT_API_KEY
```

Verify with a test query:

```bash
python tools/populate_camera_presets.py --query "dramatic close-up with shallow depth of field"
# Returns: ARRI Alexa Mini LF + Cooke S7/i + 85mm + f/1.4 + static lock
```

### Step 6 — Install Remotion (Layer 4 Compositing)

```bash
cd remotion
npm install
npm run dev      # Launch Remotion Studio for preview
npm run build    # Bundle for production rendering
```

Two production templates included: **PopTech** (brand, 16:9 + 9:16) and **Generic** (client-configurable, any aspect, 16:9 + 9:16). Extend with your own templates using the shared component library (`LogoOverlay`, `LowerThird`, `EndCard`, `Subtitle`, `KenBurns`, `Transition`).

### Step 7 — Install MCP Servers (Agent Orchestration)

These connect Claude to your production tools:

```bash
# ElevenLabs — voice, SFX, music, transcription (24 tools)
claude mcp add-json "ElevenLabs" '{"command":"uvx","args":["elevenlabs-mcp"]}'

# Playwright — browser automation for any UI without an API
claude mcp add playwright npx @playwright/mcp@latest

# ComfyUI Local — image/video generation (31 tools)
npx -y comfyui-mcp

# ComfyUI Cloud — if no local GPU
claude mcp add comfyui-cloud --transport http https://cloud.comfy.org/mcp
```

### Step 8 — Install Claude Code Skills

```bash
# Remotion video rendering (30+ rule files)
npx skills add remotion

# ElevenLabs audio (6 sub-skills: Voice AI, Narration, SFX, Music, Transcription, Voice Processing)
npx skills add elevenlabs

# HeyGen avatar (9 sub-skills) — from MCPMarket: heygen-com/skills
# ComfyUI Expert (12 sub-skills) — from: github.com/MCKRUZ/ComfyUI-Expert
```

### Step 9 — Deploy N8N Workflows

```bash
# N8N runs via PM2 on your VPS. Import each workflow JSON through the N8N UI:
# workflows/n8n/cinematic-commercial-production.json  (20 nodes)
# workflows/n8n/documentary-production.json           (14 nodes)
# workflows/n8n/anime-production.json                 (13 nodes)
# workflows/n8n/kit-daily-content.json                (12 nodes, cron trigger)
# workflows/n8n/video-publisher.json                  (8 nodes, downstream)

# IMPORTANT: Wire API credentials through N8N's credential store, NOT .env files.
# N8N is the central credential store for all production API keys.
```

### Step 10 — Deploy Governance Database

```bash
# On your VPS MySQL instance
mysql -u root -p < dashboard/schema.sql

# Creates 8 tables: production_orders, cost_tracking, quality_metrics,
# publishing_log, credit_balances, governance_logs, lora_registry,
# video_benchmarks — plus 2 summary views and engine profiles
```

### Verify Everything Works

```bash
# Test RAG
python tools/populate_camera_presets.py --query "cinematic dolly shot"

# Test color grading
python tools/color_grade.py input.mp4 output.mp4 \
  --chain luts/base/neutral_normalize.cube luts/film_stocks/kodak_vision3_500t.cube \
  --grain 0.12 --vignette 0.25

# Test video generation (requires fal.ai credits)
python tools/fal_generate.py --model nano-banana-pro \
  --prompt "cinematic studio shot, ARRI Alexa Mini LF, Cooke S7/i lens" --output test.png

# Test Remotion
cd remotion && npm run dev

# Check API balances
python tools/check_balances.py --json
```

---

## Production SOP

The engine runs on a **26-step Standard Operating Procedure** organized into three phases with quality gates between each. This is the full production pipeline — from creative brief to published video.

See [`workflows/studio-production-pipeline.md`](workflows/studio-production-pipeline.md) for the complete SOP with detailed instructions per step.

### Pre-Production (Steps 1-13)

| Step | What | Key Output |
|------|------|-----------|
| 1 | Creative Brief Intake | Structured brief from Notion or client |
| 2 | Brand Profile Load | Brand voice, colors, fonts, ICP from RAG |
| 3 | Character Development | Character profile per SOP Step 4 schema |
| 4 | Shot List + Storyboard | Shot-by-shot plan with camera/lighting/FX specs |
| 5 | RAG: Camera Preset Query | Camera body + lens + focal length + movement per shot |
| 6 | RAG: Lighting Preset Query | Lighting setup per shot (three-point, Rembrandt, noir, etc.) |
| 7 | RAG: Effects Preset Query | Style + transitions + color treatment per shot |
| 8 | Prompt Assembly | Combined cinematography prompt per shot |
| 9 | Key Visual Lock | Generate reference stills before video (Nano Banana Pro) |
| 10 | Script Writing | Dialogue, narration, timing |
| 11 | Voice Casting | ElevenLabs voice selection or clone |
| 12 | Music Direction | Mood, tempo, genre from RAG `music_library` |
| 13 | Production Approval | CTO review and sign-off before generation |

**Phase Gate 1:** Brief complete, storyboard approved, key visuals locked, production approved.

### Production (Steps 14-19)

| Step | What | Key Output |
|------|------|-----------|
| 14 | Multi-Shot Video Generation | Seedance/Kling/Veo per shot using assembled prompts |
| 14A | Cinematic Prompt Framework | Shot size + lens + angle + movement, chained with "Cut to." |
| 15 | Audio Generation | Voice, SFX, music via ElevenLabs |
| 16 | Lip-Sync Application | LatentSync via Muapi on talking shots |
| 17 | Post-Processing | ComfyUI relight, enhance, deflicker per shot |
| 18 | Upscaling | Topaz Video AI or ComfyUI ESRGAN to 4K if needed |
| 19 | Quality Review | Per-shot review against storyboard |

**Phase Gate 2:** All shots rendered, audio synced, lip-sync verified, quality approved.

### Post-Production (Steps 20-26)

| Step | What | Key Output |
|------|------|-----------|
| 20 | Remotion Compositing | Assemble shots + audio + motion graphics using templates |
| 21 | Color Grading | FFmpeg LUT chain: normalize → film stock → creative → grain → vignette |
| 22 | Platform Encoding | Aspect ratio variants: 16:9, 9:16, 1:1 |
| 23 | Subtitle Generation | ElevenLabs Scribe v2 transcription → burn-in |
| 24 | Final Review | Full video playback, audio levels (-16 LUFS), color check |
| 25 | Client Approval | Governance gate via Gmail/Notion |
| 26 | Multi-Platform Publish | N8N Video Publisher → 6 platforms |

**Phase Gate 3:** Final video approved, all platforms published, governance logged.

---

## Model Selection

Choose the right engine for the content type. The engine is model-agnostic — swap providers freely.

| Content Type | Primary Model | Backup | Best For |
|-------------|---------------|--------|----------|
| Stills / storyboards | **Nano Banana Pro** (fal.ai) | FLUX via ComfyUI | Key visual lock before video generation |
| Video clips | **Seedance 2.0** (fal.ai) | Kling 3.0, Veo 3.1 | Multi-axis motion, stacked camera movements |
| Highest quality | **Veo 3.1** | Runway Gen-4.5 | 4K 60fps, best lip-sync, photorealistic |
| Multi-shot consistency | **Kling 3.0** | Seedance 2.0 | Dialogue scenes, angle coverage |
| Lip-sync | **LatentSync** (Muapi.ai) | Wan 2.6 native | Cinema-quality lip-sync on talking shots |
| Anime / stylized | **Wan 2.6** (local or API) | AnimateDiff V3 + LoRA | Unlimited local generation, anime LoRAs |
| Avatar (backup) | **HeyGen** | Seedance + LatentSync | Backup path only, not primary pipeline |
| Voice / narration | **ElevenLabs** | Qwen3-TTS, F5-TTS | Custom clones, emotion control |
| Music / SFX | **ElevenLabs** | Suno V5 via Muapi | AI-generated SFX and music |

> **Philosophy:** No platform subscriptions. Pay only for the APIs you choose to use. Free and local options exist for every layer (Wan 2.6, ComfyUI, open-source TTS). Reserve cloud APIs for final production renders. Always review provider pricing before use — see [LEGAL.md](LEGAL.md).

---

## RAG Collections (Qdrant)

The engine's cinematography knowledge lives in 8 Qdrant collections using OpenAI `text-embedding-3-small` (1536 dimensions, cosine similarity):

| Collection | Entries | What It Contains |
|-----------|---------|-----------------|
| `camera_presets` | 1,486 | 8 camera bodies (ARRI, RED, Panavision, etc.) x 11 lens types x 6 focal lengths x 3 apertures x 16 movements |
| `lighting_presets` | 54 | 33 lighting setups: three-point, Rembrandt, noir, golden hour, neon, volumetric, studio |
| `effects_presets` | 105 | Film stocks, transitions, artistic styles (noir, sketch, anime, Ghibli, pixel art, etc.) |
| `character_library` | Active | Character descriptions, reference images, LoRA paths |
| `shot_library` | Active | Reference frames, style guides, mood boards |
| `music_library` | Active | Tempo, mood, genre tags for AI music direction |
| `brand_profiles` | Active | Studio + client brand guides in vector form |
| `film_stock_luts` | Active | LUT files + metadata for film emulation |

Each preset contains a `prompt_fragment` that gets injected into the generation prompt, plus `cinema_studio_mapping` fields for Open Generative AI Cinema Studio controls.

---

## LUT Pipeline

21 production-grade LUT files organized by category:

| Category | Count | Files |
|----------|-------|-------|
| **Base** | 1 | `neutral_normalize` — level correction before creative grading |
| **Film Stocks** | 11 | Kodak Vision3 500T/250D/50D, Fuji Eterna 500/250, Kodak Ektachrome, Tri-X B&W, CineStill 800T, Ilford HP5, Fuji Velvia, Kodak Portra 400 |
| **Creative** | 8 | Bleach bypass, cross-process, teal & orange, day-for-night, 70mm IMAX, Polaroid, Technicolor, vintage |
| **Corrections** | 1 | Daylight 5600K |

**Standard finishing chain:**

```bash
python tools/color_grade.py input.mp4 output.mp4 \
  --chain luts/base/neutral_normalize.cube luts/film_stocks/kodak_vision3_500t.cube \
  --grain 0.12 --vignette 0.25
```

Generated from real film stock characteristic curves using `tools/generate_luts.py`. Not downloaded presets — mathematically derived from Kodak/Fuji spectral data.

---

## Engineering Ops Collaboration Engine

The studio uses a **file-based CTO-Engineer collaboration pipeline** that separates creative direction from execution. Every task flows through a defined lifecycle with clear handoff signals and a full audit trail.

### How It Works

```
CTO (Cowork)                          Engineer (VS Code / Claude Code)
    |                                         |
    |-- writes task to ops/queue/ ----------->|
    |                                         |-- picks up, moves to ops/active/
    |                                         |-- implements, tests, documents
    |                                         |-- submits to ops/review/ with Engineer Log
    |<-- reviews with 7-step QC --------------|
    |-- PASS: moves to ops/done/              |
    |-- FAIL: back to ops/active/ with notes  |
```

### Ops Folder Structure

```
ops/
  queue/      # Tasks awaiting engineer pickup
  active/     # CTO directives + tasks being worked on
  review/     # Engineer submissions awaiting CTO QC
  done/       # QC-passed and signed-off tasks
```

### 7-Step QC Protocol

Every submission goes through this before sign-off:

1. **Register** — Confirm task file, submission date, engineer
2. **QC Results** — Verify each acceptance criterion with evidence (file exists, line count, code review, test output)
3. **Fix Log** — Document issues found and their resolution
4. **Commit & Deploy Log** — List all files delivered and deployment status
5. **Document Updates** — Confirm SOP, workflow, and spec updates
6. **Memory Update** — Persist new project knowledge for future conversations
7. **Phase Gate Sign-Off** — Approve with UTC timestamp, or reject with failure reasons

### CTO Directives

Master directives live in `ops/active/` and govern execution order:

| Directive | Purpose |
|-----------|---------|
| `CTO-DIRECTIVE-BUILD-ORDER.md` | Master build plan: dev waves + test rounds |
| `CTO-DIRECTIVE-CINEMA-KIT.md` | Client-specific avatar guidance |
| `CTO-DIRECTIVE-LIPSYNC.md` | Lip-sync pipeline selection rules |
| `BLOCKED.md` | Active blockers with severity and workarounds |

### Prompts for CTO (Cowork)

**Dispatch a task:**
> "Create a task file in ops/queue/ for [objective]. Include acceptance criteria, technical spec referencing the SOP, dependencies, and CTO notes. Priority: P[0-3]. Phase: [3-5]. Layer: [L0-L5]."

**Review submissions:**
> "Check ops/review/ for READY signals. Run the full 7-step QC protocol on all submitted tasks. Verify deliverables exist with evidence. Write the QC sign-off with UTC timestamp."

**Check pipeline status:**
> "Show me the current ops pipeline: what is in queue, active, review, and done. Flag any blockers."

**Batch review:**
> "Run CTO batch review of all tasks in ops/review/. Full 7-step protocol with evidence tables. Write a consolidated QC sign-off report."

### Prompts for Lead Engineer (VS Code / Claude Code)

**Pick up work:**
> "Check ops/queue/ for the next task per CTO-DIRECTIVE-BUILD-ORDER.md. Move it to ops/active/, read the full spec, and begin implementation. Follow the SOP and layer sequence."

**Submit work:**
> "Task [X.Y] is complete. Update the Engineer Log with: work completed, files created/modified, test results, acceptance criteria status. Move to ops/review/."

**Check directives:**
> "Read ops/active/CTO-DIRECTIVE-BUILD-ORDER.md and BLOCKED.md. What is the next task in the current wave? Are there any blockers?"

**Follow the SOP:**
> "Read workflows/studio-production-pipeline.md. I am at Step [N]. What are the inputs, process, and outputs for this step? What RAG collections should I query?"

---

## Notion Task Tracking

All development tasks are tracked in Notion alongside the ops/ file system. The two systems mirror each other.

**Cinema Studio Engine — Task Tracker**

### Schema

| Property | Type | Values |
|----------|------|--------|
| Task | Title | Descriptive task name |
| Task ID | Auto | CSE-xxx (auto-incrementing) |
| Phase | Select | Phase 1-5 |
| Status | Select | Queued, Active, In Review, Blocked, Done |
| Priority | Select | P0 Critical, P1 High, P2 Medium, P3 Low |
| Assignee | Person | CTO or Engineer |
| Layer | Multi-select | L0-L5 (maps to architecture layers) |
| Ops File | URL | Link to ops/ task file |
| QC Status | Select | Pending, Pass, Pass w/ Notes, Fail |
| Sign-Off UTC | Date | QC sign-off timestamp |

### Status Mapping

| Notion Status | Ops Folder | Meaning |
|---------------|------------|---------|
| Queued | `ops/queue/` | Task written, awaiting pickup |
| Active | `ops/active/` | Engineer working on it |
| In Review | `ops/review/` | Submitted for CTO QC |
| Blocked | `ops/active/BLOCKED.md` | Waiting on dependency |
| Done | `ops/done/` | QC passed, signed off |

---

## Supported Providers

### Video Generation

| Provider | Type | Best For |
|----------|------|----------|
| **Seedance 2.0** | Cloud (fal.ai) | Stacked camera movements, audio sync |
| **Veo 3.1** | Cloud (fal.ai) | 4K 60fps, photorealistic |
| **Kling 3.0** | Cloud (fal.ai) | Multi-shot consistency, dialogue |
| **Sora 2** | Cloud (OpenAI) | Physics simulation, narrative |
| **Runway Gen-4.5** | Cloud | Iterative editing, character lock |
| **Wan 2.6** | Local GPU or API | Anime, stylized, unlimited local |
| **AnimateDiff V3** | Local (ComfyUI) | Anime LoRA animation |
| **FramePack** | Local | 60+ sec on 6GB VRAM |

### Image Generation

| Provider | Type | Best For |
|----------|------|----------|
| **Nano Banana Pro** | Cloud (fal.ai) | Key visual lock, storyboards |
| **FLUX** | Cloud or local | High quality stills |
| **InstantID / IP-Adapter** | Local (ComfyUI) | Character consistency |

### Audio

| Provider | Type | Best For |
|----------|------|----------|
| **ElevenLabs** | Cloud | Voice, SFX, music, transcription |
| **Qwen3-TTS** | Local | Unlimited local TTS |
| **F5-TTS** | Local | Unlimited local TTS |
| **Chatterbox** | Local | Unlimited local TTS |

### Lip-Sync (15 models ranked by quality)

| Tier | Models | Provider | Quality |
|------|--------|----------|---------|
| 1 (fastest) | Wav2Lip | ComfyUI | Basic |
| 2 | SadTalker | ComfyUI | Good |
| 3 | LivePortrait | ComfyUI | Better |
| 4 | LatentSync 1.6 | Muapi.ai / ComfyUI | Cinema-quality |
| 5 (best) | Wan 2.6 native | Local / API | Highest quality |
| Cloud | 9 additional models | Muapi.ai Lip Sync Studio | Varies |

---

## Project Structure

```
tools/                          # 17+ Python pipeline scripts
  populate_camera_presets.py    # RAG: 1,486 camera presets
  populate_lighting_presets.py  # RAG: 54 lighting presets
  populate_effects_presets.py   # RAG: 105 effects presets
  color_grade.py                # FFmpeg LUT grading wrapper
  generate_luts.py              # LUT generation from film stock curves
  fal_generate.py               # fal.ai multi-model wrapper (6 models)
  heygen_generate.py            # HeyGen avatar wrapper (5 CLI modes)
  lipsync_compare.py            # 15-model lip-sync benchmark
  lora_train.py                 # LoRA training pipeline + registry
  benchmark.py                  # Performance benchmarking framework
  check_balances.py             # API credit balance checker
  cost_report.py                # Usage + competitive analysis reports
  client_intake.py              # Client self-service brief routing
  deploy_wan26_vps.sh           # Wan 2.6 GPU VPS deployment
  camera_presets.json           # Generated data (40,333 lines)
  lighting_presets.json         # Generated data
  effects_presets.json          # Generated data
workflows/                      # SOPs + N8N workflow JSONs
  PRODUCTION-SOP.md             # 26-step master SOP v2.0
  n8n/                          # 4 core workflows (cinematic, documentary, anime, publisher)
remotion/                       # React-based video (Layer 4)
  templates/                    # 2 templates (PopTech, Generic) — extend with your own
  src/components/               # 7 shared components
  src/Root.tsx                  # Compositions registry
  examples/                     # JSON config examples
luts/                           # 21 .cube LUT files
  base/                         # Neutral normalize
  film_stocks/                  # 11 film stock emulations
  creative/                     # 8 creative grades
  corrections/                  # Daylight correction
brand/                          # Brand profiles
  kit_profile.json              # Character schema (SOP Step 4)
dashboard/                      # Governance
  schema.sql                    # MySQL: 8 tables, 2 views
tests/                          # Benchmarks + test assets
  lipsync_benchmark/            # 21-method benchmark framework
ops/                            # Engineering ops engine
  queue/                        # Pending tasks
  active/                       # Directives + in-progress
  review/                       # Awaiting CTO QC
  done/                         # Signed off
```

---

## Infrastructure Requirements

To run the full engine, you need:

| Component | Minimum | Recommended | Purpose |
|-----------|---------|-------------|---------|
| **VPS** | 2 CPU, 4GB RAM | 4 CPU, 8GB RAM | N8N, Qdrant, MySQL |
| **Local Machine** | 16GB RAM | 32GB RAM, GPU | ComfyUI, Remotion, Topaz |
| **GPU (optional)** | 6GB VRAM | 12GB+ VRAM | Local Wan 2.6, ComfyUI generation |
| **Storage** | 50GB | 200GB+ | Video assets, LUT files, model weights |

**VPS Services:**

| Service | Port | Purpose |
|---------|------|---------|
| N8N (PM2) | 5678 | Workflow engine, 5 production workflows |
| Qdrant (Docker) | 6333/6334 | Vector DB, 1,645 cinematography presets |
| MySQL | 3306 | Governance tables, usage tracking, publishing log |

---

## Documentation

| Document | Purpose |
|----------|---------|
| [`workflows/studio-production-pipeline.md`](workflows/studio-production-pipeline.md) | 26-step production SOP with phase gates |
| [`CLAUDE.md`](CLAUDE.md) | Full architecture, WAT framework, MCP registry, agent instructions |
| [`ops/review/QC-BATCH-SIGNOFF-WAVES-1-3.md`](ops/review/QC-BATCH-SIGNOFF-WAVES-1-3.md) | 15-task QC report with evidence |
| [`ops/active/CTO-DIRECTIVE-BUILD-ORDER.md`](ops/active/CTO-DIRECTIVE-BUILD-ORDER.md) | Master build plan (3 waves + 3 test rounds) |
| [`remotion/TEMPLATE_SCHEMA.md`](remotion/TEMPLATE_SCHEMA.md) | Remotion template props reference |
| [`tests/lipsync_benchmark/BENCHMARK_REPORT.md`](tests/lipsync_benchmark/BENCHMARK_REPORT.md) | 21-method lip-sync benchmark results |

---

## Contributing

PopTech Cinema Studio Engine is open source under the MIT license. Contributions welcome.

### Ways to Contribute

**Add RAG presets** — Camera bodies, lens profiles, lighting setups, and effects styles. The more presets in the vector DB, the better the cinematography layer performs. See `tools/populate_camera_presets.py` for the schema.

**Add N8N workflow templates** — New production pipeline types (music video, product demo, tutorial, etc.). Follow the existing pattern in `workflows/n8n/` with Notion triggers and stub API nodes.

**Add Remotion templates** — New brand templates or shared components. Templates live in `remotion/templates/`, components in `remotion/src/components/`.

**Add LUT files** — Film stock emulations, creative grades, correction LUTs. Place in `luts/` and add metadata to `luts/index.json`.

**Improve the SOP** — The 26-step production pipeline is a living document. If you find better methods, update the workflow.

**Add lip-sync models** — The benchmark framework in `tests/lipsync_benchmark/` supports adding new models. See `tools/lipsync_compare.py` for the integration pattern.

### Development Setup

```bash
git clone git@github.com:PopTechStudio/cinema-studio-engine.git
cd cinema-studio-engine
cp .env.example .env
# Fill in your API keys
# Follow the 10-step install guide above
```

### Code of Conduct

Be respectful, be constructive. This is a creative tool — bring creative energy.

---

## License & Legal

This software is released under the [MIT License](LICENSE).

**By using this software, you agree to the terms in [LEGAL.md](LEGAL.md)**, which includes:

- **No warranty** on output quality, API availability, or fitness for any purpose
- **No cost guarantees** — all third-party API fees are your sole responsibility
- **Mandatory human-in-the-loop** review of all content prior to publishing
- **Hold harmless** — you hold PopTech Studio LLC, its founder, executives, associates, and partners harmless from all claims
- **Third-party IP** — no trademark license is granted for third-party logos or branding; contact those companies directly for your own license
- **Binding arbitration** in Los Angeles County, California governs all disputes
- **Class action waiver** — disputes are resolved individually, not as a class

This system does not make you creative. It streamlines and automates creativity. If you are not prepared to bring your own creative vision, editorial taste, and willingness to iterate — do not use this software.

See [LEGAL.md](LEGAL.md) for the complete legal notice, disclaimer of warranty, and terms of use.

---

<p align="center">

**PopTech Studio LLC.** | AI-Powered Automation & Prism IO

&copy; 2026 POPTECH STUDIO | All Rights Reserved

[poptechstudio.ai](https://poptechstudio.ai) | [prismio.ai](https://prismio.ai)

</p>
