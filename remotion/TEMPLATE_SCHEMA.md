# Remotion Template Schema Reference

## Templates

### PopTech (`PopTechComposition`)
**IDs:** `PopTech` (16:9), `PopTech-Vertical` (9:16)

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `clips` | `{videoUrl: string, duration: number}[]` | Yes | Array of video clips with duration in seconds |
| `audioUrl` | `string` | Yes | Path/URL to audio file |
| `title` | `string` | Yes | Title shown in lower third |
| `description` | `string` | No | Subtitle text |
| `ctaButton` | `{text: string, url?: string}` | Yes | Call-to-action on end card |
| `logoUrl` | `string` | No | Logo image URL |
| `brandColors` | `{primary: string, secondary: string}` | No | Hex colors (default: PopTech blue/dark) |
| `transitionType` | `'fade' \| 'dissolve' \| 'wipe-left'` | No | Default: `'fade'` |
| `transitionDuration` | `number` | No | Frames. Default: 10 |
| `endCardDuration` | `number` | No | Seconds. Default: 3 |

### Generic Client (`GenericComposition`)
**IDs:** `Generic` (16:9), `Generic-Vertical` (9:16)

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `clips` | `{videoUrl?: string, imageUrl?: string, duration: number}[]` | Yes | Video clips or still images (Ken Burns) |
| `audioUrl` | `string` | Yes | Audio track |
| `branding` | `{logoUrl?, logoPosition?, primaryColor, secondaryColor, fontFamily?}` | Yes | Client branding |
| `metadata` | `{title, clientName?, episodeTitle?, airDate?, credits?, contactEmail?, website?}` | Yes | Project metadata |
| `subtitles` | `{text, startFrame, endFrame}[]` | No | Timed subtitles |
| `transitionType` | `'fade' \| 'dissolve' \| 'wipe-left' \| 'wipe-right' \| 'zoom'` | No | Default: `'fade'` |
| `transitionDuration` | `number` | No | Frames. Default: 15 |
| `endCardDuration` | `number` | No | Seconds. Default: 4 |

## Shared Components

| Component | Props | Used In |
|-----------|-------|---------|
| `LogoOverlay` | logoUrl, position, scale, opacity, animation, margin | PopTech, Generic |
| `LowerThird` | primaryText, secondaryText, backgroundColor, accentColor, startFrame, durationFrames | All |
| `EndCard` | title, buttonText, credits, contactEmail, website, backgroundColor, accentColor, animation | PopTech, Generic |
| `Subtitle` | entries[], fontSize, color, backgroundColor, position | Generic |
| `KenBurns` | imageUrl, startScale, endScale, panX, panY | Generic |
| `Transition` | type, durationFrames, startFrame, children | PopTech, Generic |

## N8N Integration

```bash
# Render from CLI with JSON props
npx remotion render src/index.ts PopTech --props='examples/poptech-commercial.json' --output out/poptech.mp4
npx remotion render src/index.ts Generic --props='examples/generic-documentary.json' --output out/documentary.mp4
```

N8N builds the JSON props file from the production order, then calls `npx remotion render` with the appropriate template ID and props path.
