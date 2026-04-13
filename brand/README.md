# PopTech Studio — Brand Guidelines

> **Status:** Draft v1.0 — Awaiting CTO review
> **Machine-readable profile:** `poptech_profile.json`
> **Last updated:** 2026-04-12

---

## Who We Are

**PopTech Studio** is a self-hosted AI cinema production engine. We replace $400+/mo platform subscriptions (Higgsfield Cinema Studio, Arcads) with a node-based pipeline that runs at API-cost-only pricing (~$100-200/mo total).

**The thesis:** The AI models are commodities — anyone can call the same APIs. The value layer is **virtual cinematography**: camera presets, lighting simulation, effects chains, and multi-shot sequencing stored in RAG. That's the product.

---

## Brand Voice

**Tone:** Confident, technical-but-accessible, cinematic.

**We sound like:** A creative director who builds their own tools. Decisive, visual-first, pragmatic about costs. We speak the language of film production, not marketing.

**We say:**
- "production pipeline" (not workflow)
- "virtual cinematography" (not AI video)
- "cinema engine" (not video tool)
- "shot, sequence, scene" (not clip, content, post)
- "render, composite, grade" (not make, create, edit)

**We never say:** game-changing, revolutionary, democratize, leverage, synergy, disrupt, 10x, vibe, magic, automagically.

**Example copy:**
- "Cinema-grade output at API-cost pricing."
- "The models are commodities. The cinematography intelligence is the product."
- "RAG-driven camera presets, not prompt guessing."

---

## Visual Identity

### Color Palette

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Primary BG | Void Black | `#0a0a0a` | Backgrounds, dark mode base |
| Mid BG | Deep Navy | `#1a1a2e` | Gradient midpoint, panels |
| Accent BG | Midnight Blue | `#16213e` | Gradient endpoint |
| Primary Text | Studio White | `#ffffff` | Headings, high-contrast |
| Secondary Text | Silver | `#888888` | Subtitles, metadata |
| Interactive | Accent Blue | `#2792dc` | Links, highlights, CTAs |
| Data | Accent Teal | `#9ce6e6` | Visualizations, secondary accent |

**Direction:** Dark, cinematic. The palette reflects a color-graded film frame, not a corporate dashboard. Gradients go from pure black through deep blue.

### Typography

- **Headings:** System UI sans-serif, weight 800, letter-spacing -0.02em
- **Body:** System UI sans-serif, weight 400
- **Code/Technical:** Monospace

### Photography & Video Style

- Dark, high-contrast, cinematic
- Shallow depth of field preferred
- Anamorphic lens character (subtle flares, oval bokeh)
- Noir and moody over bright and corporate
- Every frame should feel intentional

---

## Cinema Defaults

These are starting-point preferences for the engine. Phase 2 builds out the full RAG preset library.

| Setting | Default |
|---------|---------|
| Color grading | Film stock emulation — warm highlights, lifted shadows |
| Film stock | Kodak Vision3 500T (interiors), Fuji Eterna Vivid 500 (exteriors) |
| Camera body | ARRI Alexa 35 |
| Lens set | Cooke S7i primes (organic rendering) |
| Lighting | Modified three-point: soft key 45deg, minimal fill, subtle edge light |

---

## Content Specifications

### Formats
Cinematic commercial, documentary, anime series, avatar/talking head, social short, product demo, motion graphics.

### Platform Targets
YouTube, YouTube Shorts, Instagram Reels, TikTok, LinkedIn, X/Twitter.

### Encoding Defaults

| Spec | Value |
|------|-------|
| Codec | H.264 |
| FPS | 30 |
| Audio | AAC 192kbps, -16 LUFS normalization |
| Color space | Rec.709 |
| Bitrate (1080p) | 8-12 Mbps |

### Aspect Ratios

| Format | Resolution | Use |
|--------|-----------|-----|
| Landscape (16:9) | 1920x1080 | YouTube, LinkedIn |
| Portrait (9:16) | 1080x1920 | Reels, TikTok, Shorts |
| Square (1:1) | 1080x1080 | Feed posts |

---

## Target Audience

**Primary:** Small-to-mid creative agencies and independent filmmakers who need cinema-quality AI video without $200+/mo platform subs.

**Secondary:** DTC brands and e-commerce businesses needing high-volume video content at scale.

---

## Assets

Logo files and color swatches go in `brand/assets/`. Currently empty — CTO to provide.

---

## CTO Review Needed

The following items need CTO confirmation before this profile moves from draft to final:

1. **Tagline** — Is "AI Cinema Production Engine" the final tagline?
2. **Logo files** — Need to be added to `brand/assets/`
3. **Brand voice** — Do the personality traits match Rob's vision?
4. **Target audience** — Validate ICP descriptions
5. **Photography style** — Confirm dark/cinematic direction
6. **Film stock defaults** — Confirm Kodak Vision3 / Fuji Eterna preferences
