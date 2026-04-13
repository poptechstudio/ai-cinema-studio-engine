"""
PopTech Cinema Studio — Effects Presets RAG Population Script
Task 2.3: Populate Qdrant effects_presets collection with 100+ entries.

Usage:
  python tools/populate_effects_presets.py --generate
  python tools/populate_effects_presets.py --upload
  python tools/populate_effects_presets.py --query "text"
  python tools/populate_effects_presets.py --stats
"""

import json
import os
import sys
import hashlib
from pathlib import Path

# ---------------------------------------------------------------------------
# Effects data — 4 categories, 100+ entries
# ---------------------------------------------------------------------------

EFFECTS = []

# ===== FILM STOCK EMULATIONS (20) =====
_film_stocks = [
    ("Kodak Vision3 500T", "film_stock_emulation", "color_grade",
     "Tungsten-balanced cinema negative. Warm highlights, rich shadows, organic grain structure. The cinema standard.",
     "Kodak Vision3 500T film stock, warm tungsten color balance, organic film grain, rich shadow detail, gentle highlight rolloff",
     {"method": "lut", "lut_file": "kodak_vision3_500t.cube", "alt_method": "prompt_modifier"},
     ["cinematic", "interior", "dramatic", "narrative"],
     {"camera": ["ARRI Alexa 35", "Panavision DXL2"], "lighting": ["Rembrandt", "Practical Motivated"]}),

    ("Kodak Vision3 250D", "film_stock_emulation", "color_grade",
     "Daylight-balanced cinema negative. Vibrant color, moderate grain, excellent outdoor stock.",
     "Kodak Vision3 250D film stock, daylight balanced, vibrant saturated color, moderate grain, crisp outdoor image",
     {"method": "lut", "lut_file": "kodak_vision3_250d.cube", "alt_method": "prompt_modifier"},
     ["exterior", "daylight", "commercial", "vibrant"],
     {"camera": ["ARRI Alexa 35", "Sony VENICE 2"], "lighting": ["Golden Hour", "Three-Point Classic"]}),

    ("Kodak Vision3 200T", "film_stock_emulation", "color_grade",
     "Tungsten low-grain cinema stock. Finer grain than 500T, ideal for close-ups and controlled lighting.",
     "Kodak Vision3 200T film stock, fine grain, tungsten balanced, smooth highlight rolloff, clean shadow detail",
     {"method": "lut", "lut_file": "kodak_vision3_200t.cube", "alt_method": "prompt_modifier"},
     ["portrait", "studio", "controlled_lighting", "fine_detail"],
     {"camera": ["ARRI Alexa 35", "RED V-Raptor"], "lighting": ["Butterfly Paramount", "Three-Point Classic"]}),

    ("Fuji Eterna Vivid 500", "film_stock_emulation", "color_grade",
     "Punchy color rendition with strong saturation. Excellent for exteriors and vibrant environments.",
     "Fuji Eterna Vivid 500 film stock, punchy saturated color, vivid greens and blues, crisp grain, bold image",
     {"method": "lut", "lut_file": "fuji_eterna_vivid_500.cube", "alt_method": "prompt_modifier"},
     ["exterior", "vibrant", "landscape", "commercial"],
     {"camera": ["Sony VENICE 2", "ARRI Alexa 35"], "lighting": ["Golden Hour", "Overcast Soft"]}),

    ("Fuji Eterna 250D", "film_stock_emulation", "color_grade",
     "Neutral daylight cinema stock. Natural skin tones, moderate saturation, professional baseline.",
     "Fuji Eterna 250D film stock, neutral daylight balanced, natural skin tones, moderate saturation, clean grain",
     {"method": "lut", "lut_file": "fuji_eterna_250d.cube", "alt_method": "prompt_modifier"},
     ["daylight", "natural", "documentary", "neutral"],
     {"camera": ["Sony VENICE 2", "Blackmagic URSA Mini Pro 12K"], "lighting": ["Documentary Available Light", "Overcast Soft"]}),

    ("Kodak Ektachrome 100D", "film_stock_emulation", "color_grade",
     "Reversal film. Saturated, punchy, direct positive. No negative inversion — what you shoot is what you get.",
     "Kodak Ektachrome 100D reversal film, highly saturated color, punchy contrast, vivid direct positive image, fine grain",
     {"method": "lut", "lut_file": "kodak_ektachrome_100d.cube", "alt_method": "prompt_modifier"},
     ["saturated", "vivid", "fashion", "music_video"],
     {"camera": ["ARRI Alexa 35", "Bolex H16"], "lighting": ["Golden Hour", "Music Video Dramatic"]}),

    ("Kodak Tri-X 400", "film_stock_emulation", "color_grade",
     "Classic black and white with visible grain. The photojournalism standard. Gritty, honest, timeless.",
     "Kodak Tri-X 400 black and white film, visible grain structure, high contrast, classic photojournalism look, gritty texture",
     {"method": "lut", "lut_file": "kodak_trix_400_bw.cube", "alt_method": "prompt_modifier"},
     ["black_and_white", "documentary", "street", "gritty"],
     {"camera": ["Bolex H16", "ARRI Alexa 35"], "lighting": ["Documentary Available Light", "Hard Noon Sun"]}),

    ("Ilford HP5 Plus", "film_stock_emulation", "color_grade",
     "Fine-grain black and white. Smoother than Tri-X, wider tonal range, more forgiving exposure latitude.",
     "Ilford HP5 Plus black and white film, fine grain, smooth tonal gradation, wide latitude, elegant monochrome",
     {"method": "lut", "lut_file": "ilford_hp5_bw.cube", "alt_method": "prompt_modifier"},
     ["black_and_white", "portrait", "elegant", "fine_art"],
     {"camera": ["ARRI Alexa 35", "Panavision Millennium XL2"], "lighting": ["Rembrandt", "Window Light Natural"]}),

    ("Kodak Double-X 5222", "film_stock_emulation", "color_grade",
     "Cinema black and white. The film noir standard, used in Raging Bull, Schindler's List, The Lighthouse.",
     "Kodak Double-X 5222 black and white film, cinema noir grain, deep blacks, crisp whites, high contrast negative",
     {"method": "lut", "lut_file": "kodak_doublex_5222_bw.cube", "alt_method": "prompt_modifier"},
     ["noir", "black_and_white", "cinema", "dramatic"],
     {"camera": ["ARRI Alexa 35", "Panavision Millennium XL2"], "lighting": ["Film Noir", "Split Lighting"]}),

    ("16mm Reversal Vintage", "film_stock_emulation", "color_grade",
     "16mm reversal film with heavy grain, warm color cast, vintage documentary texture. Home movie feel.",
     "16mm reversal film, heavy visible grain, warm faded color, vintage documentary texture, gate weave, soft focus edges",
     {"method": "lut", "lut_file": "16mm_reversal_vintage.cube", "alt_method": "prompt_modifier"},
     ["vintage", "documentary", "archival", "retro"],
     {"camera": ["Bolex H16"], "lighting": ["Documentary Available Light", "Golden Hour"]}),

    ("Super 8mm Home Movie", "film_stock_emulation", "color_grade",
     "Super 8mm with extreme grain, color shifts, flicker. Nostalgic home movie aesthetic.",
     "Super 8mm film, extreme heavy grain, warm color shift, light leaks, flicker, nostalgic home movie look, soft resolution",
     {"method": "lut", "lut_file": "super_8mm_home_movie.cube", "alt_method": "prompt_modifier"},
     ["nostalgic", "home_movie", "vintage", "personal"],
     {"camera": ["Bolex H16"], "lighting": ["Golden Hour", "Practical Motivated"]}),

    ("70mm IMAX Large Format", "film_stock_emulation", "color_grade",
     "70mm IMAX — massive resolution, negligible grain, epic scale, razor-sharp detail.",
     "70mm IMAX film, ultra-fine grain, massive resolution, epic scale, crystal-clear detail, wide dynamic range",
     {"method": "lut", "lut_file": "70mm_imax.cube", "alt_method": "prompt_modifier"},
     ["epic", "landscape", "imax", "large_format"],
     {"camera": ["Panavision DXL2", "RED V-Raptor"], "lighting": ["Golden Hour", "Haze Backlight Volumetric"]}),

    ("Technicolor 3-Strip", "film_stock_emulation", "color_grade",
     "Golden age Hollywood saturated color. Three-strip dye transfer — vivid reds, greens, blues.",
     "Technicolor 3-strip, golden age Hollywood color, vivid saturated reds and greens, rich dye transfer look, classic cinema",
     {"method": "lut", "lut_file": "technicolor_3strip.cube", "alt_method": "prompt_modifier"},
     ["classic_hollywood", "saturated", "musical", "golden_age"],
     {"camera": ["Panavision Millennium XL2", "ARRI Alexa 35"], "lighting": ["Three-Point Classic", "Butterfly Paramount"]}),

    ("Bleach Bypass", "film_stock_emulation", "color_grade",
     "Desaturated, high contrast. Silver retention process — gritty, metallic, war-movie aesthetic.",
     "bleach bypass film process, desaturated color, high contrast, silver metallic sheen, gritty texture, war movie look",
     {"method": "lut", "lut_file": "bleach_bypass.cube", "alt_method": "prompt_modifier"},
     ["gritty", "war", "desaturated", "harsh"],
     {"camera": ["RED V-Raptor", "ARRI Alexa 35"], "lighting": ["Hard Noon Sun", "Three-Point High Contrast"]}),

    ("Cross Processing", "film_stock_emulation", "color_grade",
     "Deliberate wrong-chemistry processing. Extreme color shifts, high saturation, unpredictable palette.",
     "cross-processed film, extreme color shift, high saturation, green-yellow shadows, magenta highlights, unpredictable color",
     {"method": "lut", "lut_file": "cross_process.cube", "alt_method": "prompt_modifier"},
     ["experimental", "fashion", "music_video", "retro"],
     {"camera": ["Bolex H16", "ARRI Alexa 35"], "lighting": ["Music Video Dramatic", "Neon Urban Night"]}),

    ("Faded Film Aged", "film_stock_emulation", "color_grade",
     "Lifted blacks, desaturated color, faded look. Aged film stock or deliberate vintage processing.",
     "faded vintage film, lifted blacks, desaturated muted color, aged film stock look, soft contrast, nostalgic patina",
     {"method": "lut", "lut_file": "faded_film_aged.cube", "alt_method": "prompt_modifier"},
     ["vintage", "nostalgic", "indie", "faded"],
     {"camera": ["Bolex H16", "Panavision Millennium XL2"], "lighting": ["Golden Hour", "Overcast Soft"]}),

    ("Polaroid Instant", "film_stock_emulation", "color_grade",
     "Instant film color science. Shifted greens, warm shadows, characteristic color cast, white border feel.",
     "Polaroid instant film, warm shifted color, faded greens, soft contrast, vintage instant camera aesthetic",
     {"method": "lut", "lut_file": "polaroid_instant.cube", "alt_method": "prompt_modifier"},
     ["nostalgic", "casual", "personal", "vintage"],
     {"camera": ["Bolex H16"], "lighting": ["Overcast Soft", "Golden Hour"]}),

    ("Technicolor 2-Strip", "film_stock_emulation", "color_grade",
     "Early color process with only red and cyan channels. Distinctive limited palette, 1920s-30s look.",
     "Technicolor 2-strip, red and cyan bias only, limited color palette, early cinema color, 1920s-1930s vintage look",
     {"method": "lut", "lut_file": "technicolor_2strip.cube", "alt_method": "prompt_modifier"},
     ["period", "vintage", "early_cinema", "limited_palette"],
     {"camera": ["Panavision Millennium XL2", "Bolex H16"], "lighting": ["Three-Point Classic", "Practical Motivated"]}),

    ("Kodak 5222 Lighthouse", "film_stock_emulation", "color_grade",
     "The Lighthouse (2019) look — extreme contrast B&W, crushed blacks, blown highlights, 1.19:1 aspect.",
     "Kodak 5222 extreme contrast black and white, crushed deep blacks, blown white highlights, harsh vintage grain, gothic mood",
     {"method": "lut", "lut_file": "kodak_5222_lighthouse.cube", "alt_method": "prompt_modifier"},
     ["gothic", "horror", "extreme_contrast", "art_house"],
     {"camera": ["Panavision Millennium XL2", "Bolex H16"], "lighting": ["Film Noir", "Practical Motivated"]}),

    ("35mm Negative Standard", "film_stock_emulation", "color_grade",
     "Standard 35mm color negative. The baseline cinema look — moderate grain, natural color, wide latitude.",
     "35mm color negative film, standard cinema grain, natural color rendition, wide exposure latitude, theater projection look",
     {"method": "lut", "lut_file": "35mm_negative_standard.cube", "alt_method": "prompt_modifier"},
     ["standard", "cinema", "theatrical", "baseline"],
     {"camera": ["Panavision Millennium XL2", "ARRI Alexa 35"], "lighting": ["Three-Point Classic", "Rembrandt"]}),
]

for name, etype, cat, desc, prompt, impl, uses, pairs in _film_stocks:
    EFFECTS.append({
        "name": name, "effect_type": etype, "category": cat,
        "description": desc, "prompt_fragment": prompt,
        "implementation": impl, "use_cases": uses, "pairs_with": pairs,
    })

# ===== ARTISTIC STYLES (25) =====
_artistic_styles = [
    ("Film Noir Style", "artistic_style", "visual_style",
     "High contrast black and white, hard shadows, chiaroscuro. 1940s crime cinema aesthetic.",
     "film noir style, high contrast black and white, deep hard shadows, chiaroscuro lighting, 1940s crime cinema, venetian blind shadow patterns",
     {"method": "prompt_modifier", "alt_method": "lora", "comfyui_workflow": "noir_style_transfer"},
     ["noir", "crime", "dramatic", "black_and_white"]),

    ("Pencil Sketch", "artistic_style", "visual_style",
     "Line drawing with cross-hatching. Graphite on paper, architectural or editorial illustration feel.",
     "pencil sketch drawing, graphite on paper, cross-hatching shading, line art, architectural illustration style",
     {"method": "prompt_modifier", "alt_method": "lora", "comfyui_workflow": "sketch_style_transfer"},
     ["editorial", "storyboard", "illustration", "minimal"]),

    ("Watercolor Painting", "artistic_style", "visual_style",
     "Soft bleeding edges, translucent color washes, wet-on-wet technique, visible paper texture.",
     "watercolor painting, soft bleeding edges, translucent color washes, wet-on-wet technique, visible paper texture, gentle brush strokes",
     {"method": "prompt_modifier", "alt_method": "lora"},
     ["artistic", "gentle", "pastoral", "illustration"]),

    ("Oil Painting Impasto", "artistic_style", "visual_style",
     "Thick textured brushstrokes, rich color, visible canvas texture. Dutch masters to impressionism.",
     "oil painting, thick impasto brushstrokes, rich pigment color, visible canvas texture, classical painting technique",
     {"method": "prompt_modifier", "alt_method": "lora"},
     ["artistic", "classical", "textured", "rich"]),

    ("Anime Cel-Shaded", "artistic_style", "visual_style",
     "Flat color fills with bold outlines, limited shadow gradation, bright palette. Japanese animation aesthetic.",
     "anime cel-shaded style, flat color fills, bold black outlines, limited shadow gradation, bright vibrant palette, Japanese animation",
     {"method": "prompt_modifier", "alt_method": "lora", "comfyui_workflow": "anime_style_transfer"},
     ["anime", "stylized", "colorful", "youth"]),

    ("Studio Ghibli", "artistic_style", "visual_style",
     "Soft watercolor anime, pastoral landscapes, warm colors, gentle environmental storytelling. Miyazaki aesthetic.",
     "Studio Ghibli style, soft watercolor anime, pastoral landscape, warm gentle colors, hand-painted backgrounds, Miyazaki aesthetic",
     {"method": "prompt_modifier", "alt_method": "lora"},
     ["anime", "pastoral", "gentle", "environmental"]),

    ("Cyberpunk Neon", "artistic_style", "visual_style",
     "Neon-soaked urban nightscape, rain-slicked streets, chromatic aberration, holographic displays.",
     "cyberpunk aesthetic, neon lights in rain, wet reflective streets, chromatic aberration, holographic displays, dystopian urban night",
     {"method": "prompt_modifier", "alt_method": "lora"},
     ["cyberpunk", "sci-fi", "urban", "neon"]),

    ("Vaporwave", "artistic_style", "visual_style",
     "Pink/cyan gradient palette, retro 80s/90s digital aesthetic, Greek statues, grid backgrounds.",
     "vaporwave aesthetic, pink and cyan gradient, retro 80s digital, Greek statue elements, sunset grid background, nostalgic digital",
     {"method": "prompt_modifier", "alt_method": "lora"},
     ["retro", "digital", "nostalgic", "aesthetic"]),

    ("Comic Book Pop Art", "artistic_style", "visual_style",
     "Bold halftone dots, thick outlines, limited flat color palette, speech bubbles. Lichtenstein meets Marvel.",
     "comic book style, halftone dot pattern, thick bold outlines, flat limited color palette, pop art, graphic novel aesthetic",
     {"method": "prompt_modifier", "alt_method": "lora"},
     ["graphic", "bold", "commercial", "youth"]),

    ("Renaissance Painting", "artistic_style", "visual_style",
     "Classical composition, chiaroscuro, sfumato technique, religious/mythological grandeur, oil on canvas.",
     "Renaissance painting style, classical composition, chiaroscuro lighting, sfumato soft edges, oil on canvas, Caravaggio influence",
     {"method": "prompt_modifier", "alt_method": "lora"},
     ["classical", "dramatic", "artistic", "grand"]),

    ("Pixel Art Retro", "artistic_style", "visual_style",
     "8-bit/16-bit limited palette, visible square pixels, retro gaming aesthetic, dithering patterns.",
     "pixel art style, 8-bit retro aesthetic, limited color palette, visible square pixels, dithering patterns, retro gaming look",
     {"method": "prompt_modifier", "alt_method": "comfyui_workflow"},
     ["retro", "gaming", "minimal", "nostalgic"]),

    ("Paper Cutout Stop Motion", "artistic_style", "visual_style",
     "Textured paper layers, visible cut edges, stop-motion jitter, handmade feel. South Park to Wes Anderson.",
     "paper cutout stop motion style, textured layered paper, visible cut edges, slight stop-motion jitter, handmade craft aesthetic",
     {"method": "prompt_modifier", "alt_method": "lora"},
     ["handmade", "quirky", "indie", "textured"]),

    ("Double Exposure", "artistic_style", "visual_style",
     "Two overlapping images blended together. Ghostly transparency, silhouette filled with landscape or texture.",
     "double exposure effect, two overlapping transparent images, ghostly silhouette filled with landscape, ethereal blended imagery",
     {"method": "comfyui_workflow", "alt_method": "prompt_modifier"},
     ["artistic", "ethereal", "portrait", "abstract"]),

    ("Infrared Photography", "artistic_style", "visual_style",
     "False color infrared. White foliage, dark skies, surreal color mapping. Invisible spectrum rendered visible.",
     "infrared photography, false color, white foliage and grass, dark sky, surreal color mapping, ethereal alien landscape",
     {"method": "prompt_modifier", "alt_method": "lut"},
     ["surreal", "landscape", "artistic", "otherworldly"]),

    ("Glitch Art Digital", "artistic_style", "visual_style",
     "Deliberate data corruption aesthetic. RGB channel splitting, pixel sorting, compression artifacts as art.",
     "glitch art, data corruption aesthetic, RGB channel shift, pixel sorting, compression artifacts, digital noise, broken digital image",
     {"method": "comfyui_workflow", "alt_method": "ffmpeg_filter"},
     ["experimental", "digital", "avant-garde", "music_video"]),

    ("Tilt-Shift Miniature", "artistic_style", "visual_style",
     "Selective focus blur making real scenes look like miniature models. Toy-like, whimsical scale shift.",
     "tilt-shift miniature effect, selective narrow focus band, extreme blur top and bottom, toy-like miniature world, saturated color",
     {"method": "ffmpeg_filter", "alt_method": "comfyui_workflow", "ffmpeg_cmd": "lenscorrection + tiltandshift"},
     ["whimsical", "aerial", "architectural", "creative"]),

    ("Lomography Vintage", "artistic_style", "visual_style",
     "Heavy vignette, color shifts, light leaks, saturated cross-processed look. Analog imperfection as aesthetic.",
     "lomography style, heavy dark vignette, color shift, light leaks, saturated cross-processed look, analog camera imperfections",
     {"method": "lut", "lut_file": "lomo_vintage.cube", "alt_method": "prompt_modifier"},
     ["vintage", "casual", "lo-fi", "artistic"]),

    ("Vintage VHS Analog", "artistic_style", "visual_style",
     "VHS scan lines, tracking artifacts, color bleed, tape noise. 1980s-90s home recording aesthetic.",
     "VHS tape aesthetic, scan lines, tracking artifacts, color bleed, tape noise, 1980s home video look, analog degradation",
     {"method": "ffmpeg_filter", "alt_method": "comfyui_workflow", "ffmpeg_cmd": "noise+scanline overlay"},
     ["retro", "nostalgic", "lo-fi", "found_footage"]),

    ("90s Camcorder", "artistic_style", "visual_style",
     "Handheld camcorder with date stamp, auto-focus hunting, interlaced video, consumer DV compression.",
     "90s camcorder footage, date stamp overlay, auto-focus hunting, interlaced video, consumer DV quality, home video aesthetic",
     {"method": "ffmpeg_filter", "alt_method": "comfyui_workflow"},
     ["nostalgic", "documentary", "found_footage", "personal"]),

    ("Underwater Caustics", "artistic_style", "visual_style",
     "Underwater light patterns, blue-green color cast, caustic light dancing on surfaces, floating particles.",
     "underwater scene, blue-green water color cast, caustic light patterns dancing on surfaces, floating particles, aquatic atmosphere",
     {"method": "prompt_modifier", "alt_method": "comfyui_workflow"},
     ["aquatic", "dreamy", "environmental", "fantasy"]),

    ("Holographic Iridescent", "artistic_style", "visual_style",
     "Rainbow light diffraction, prismatic color shifts, chrome reflections. Futuristic material aesthetic.",
     "holographic iridescent effect, rainbow light diffraction, prismatic color shift, chrome reflections, futuristic material surface",
     {"method": "prompt_modifier", "alt_method": "comfyui_workflow"},
     ["futuristic", "fashion", "product", "experimental"]),

    ("Daguerreotype Early Photo", "artistic_style", "visual_style",
     "First photographic process. Metallic silver image on polished plate, monochrome, long exposure softness.",
     "daguerreotype early photography, metallic silver on polished plate, monochrome sepia, long exposure softness, antique photograph",
     {"method": "prompt_modifier", "alt_method": "lut"},
     ["antique", "historical", "monochrome", "period"]),

    ("Thermal Heat Vision", "artistic_style", "visual_style",
     "False-color temperature mapping. Hot objects in red/yellow, cold in blue/purple. Surveillance/sci-fi aesthetic.",
     "thermal heat vision, false-color temperature map, hot areas red and yellow, cold areas blue and purple, infrared surveillance look",
     {"method": "comfyui_workflow", "alt_method": "lut"},
     ["sci-fi", "surveillance", "technical", "military"]),

    ("Cinemagraph Living Photo", "artistic_style", "visual_style",
     "Mostly frozen still image with one isolated element in seamless motion loop. Mesmerizing subtlety.",
     "cinemagraph effect, frozen still photograph with one isolated element in seamless motion loop, subtle mesmerizing movement",
     {"method": "comfyui_workflow", "alt_method": "remotion_component"},
     ["social_media", "editorial", "subtle", "artistic"]),

    ("Wes Anderson Symmetry", "artistic_style", "visual_style",
     "Perfect centered symmetry, pastel color palette, whimsical production design, deadpan framing.",
     "Wes Anderson style, perfect centered symmetry, pastel color palette, whimsical design, deadpan framing, dollhouse aesthetic",
     {"method": "prompt_modifier", "alt_method": "lora"},
     ["whimsical", "symmetrical", "pastel", "editorial"]),
]

for name, etype, cat, desc, prompt, impl, uses in _artistic_styles:
    EFFECTS.append({
        "name": name, "effect_type": etype, "category": cat,
        "description": desc, "prompt_fragment": prompt,
        "implementation": impl, "use_cases": uses, "pairs_with": {},
    })

# ===== IN-CLIP MOTION FX (20) =====
_motion_fx = [
    ("Dolly Zoom Vertigo", "motion_fx", "in_clip",
     "Simultaneous dolly + counter-zoom. Background warps while subject stays same size. Hitchcock/Spielberg.",
     "dolly zoom vertigo effect, background warps and shifts while subject remains same size, Hitchcock vertigo, disorienting perspective shift",
     {"method": "comfyui_workflow", "alt_method": "prompt_modifier"}),

    ("Whip Pan Blur", "motion_fx", "in_clip",
     "Extremely fast horizontal pan creating full-frame motion blur. Scene-to-scene transition or energy burst.",
     "whip pan effect, extremely fast horizontal camera pan, full-frame horizontal motion blur, energetic camera movement",
     {"method": "ffmpeg_filter", "alt_method": "prompt_modifier", "ffmpeg_cmd": "minterpolate+motion blur"}),

    ("Rack Focus Shift", "motion_fx", "in_clip",
     "Smooth focus transition from foreground to background or vice versa. Reveals relationships, directs attention.",
     "rack focus shift, smooth focus transition from foreground to background, selective focus pull, depth attention redirect",
     {"method": "prompt_modifier", "alt_method": "comfyui_workflow"}),

    ("Zoom Burst Radial", "motion_fx", "in_clip",
     "Radial zoom blur emanating from center. Impact emphasis, psychedelic energy, action emphasis.",
     "zoom burst effect, radial zoom blur from center, impact emphasis, streaking light lines from center, dramatic zoom energy",
     {"method": "ffmpeg_filter", "alt_method": "comfyui_workflow", "ffmpeg_cmd": "zoompan+radial blur"}),

    ("Speed Ramp Dramatic", "motion_fx", "in_clip",
     "Variable speed within a single clip. Slow motion for emphasis, speed up for action. Snyder/Bay style.",
     "speed ramp, variable speed slow to fast to slow within single shot, dramatic slow motion emphasis then accelerate, Snyder style",
     {"method": "ffmpeg_filter", "alt_method": "remotion_component", "ffmpeg_cmd": "setpts for speed ramp"}),

    ("Reverse Motion", "motion_fx", "in_clip",
     "Time reversal. Objects un-break, water flows upward, people walk backward. Surreal, music video staple.",
     "reverse motion, time reversal effect, objects reassembling, liquid flowing upward, surreal backward movement",
     {"method": "ffmpeg_filter", "ffmpeg_cmd": "reverse"}),

    ("Time-Lapse Accelerated", "motion_fx", "in_clip",
     "Dramatically accelerated time. Clouds racing, crowds flowing, day-to-night. Temporal compression.",
     "time-lapse, dramatically accelerated time, clouds racing across sky, crowds flowing, day to night transition, compressed time",
     {"method": "ffmpeg_filter", "alt_method": "prompt_modifier", "ffmpeg_cmd": "setpts=PTS/30"}),

    ("Hyperlapse Moving", "motion_fx", "in_clip",
     "Stabilized moving time-lapse. Camera travels through space while time accelerates. Google Earth style.",
     "hyperlapse, stabilized moving time-lapse, camera traveling through space, time accelerating, smooth aerial movement through time",
     {"method": "comfyui_workflow", "alt_method": "prompt_modifier"}),

    ("Freeze Frame Hold", "motion_fx", "in_clip",
     "Motion freezes to still image. Record scratch moment, dramatic pause, ending card. Goodfellas style.",
     "freeze frame, motion suddenly stops, held still frame, dramatic pause, voiceover moment, record scratch freeze",
     {"method": "ffmpeg_filter", "alt_method": "remotion_component", "ffmpeg_cmd": "select frame + loop"}),

    ("Slow Motion Overcrank", "motion_fx", "in_clip",
     "120fps+ playback at 24/30fps. Smooth slow motion, detail emphasis, emotional weight, impact stretch.",
     "slow motion, overcranked high frame rate, smooth slowed movement, every detail emphasized, emotional weight, impact stretching",
     {"method": "comfyui_workflow", "alt_method": "ffmpeg_filter"}),

    ("Dutch Angle Tilt", "motion_fx", "in_clip",
     "Tilted horizon creating diagonal framing. Disorientation, unease, comic book energy. Batman Returns style.",
     "Dutch angle tilted horizon, diagonal framing, disorienting perspective, unease and tension, comic book dynamic angle",
     {"method": "prompt_modifier", "alt_method": "ffmpeg_filter"}),

    ("Parallax 2.5D Depth", "motion_fx", "in_clip",
     "Depth layers moving at different rates creating 3D feel from 2D. Photo animation, Ken Burns evolution.",
     "parallax 2.5D depth effect, foreground and background layers moving at different speeds, 3D depth from 2D image, layered movement",
     {"method": "comfyui_workflow", "alt_method": "remotion_component"}),

    ("Ken Burns Pan Zoom", "motion_fx", "in_clip",
     "Slow pan and zoom on still image. Documentary standard for photo animation. Subtle, reveals detail.",
     "Ken Burns effect, slow smooth pan and zoom on still photograph, gradual reveal of image detail, documentary photo animation",
     {"method": "remotion_component", "alt_method": "ffmpeg_filter", "ffmpeg_cmd": "zoompan"}),

    ("Particle Snow Fall", "motion_fx", "in_clip",
     "Gentle falling snow particles overlaid on scene. Seasonal, atmospheric, dreamy. Adjustable density.",
     "falling snow particles, gentle snowfall overlay, atmospheric winter particles, adjustable density, seasonal mood",
     {"method": "comfyui_workflow", "alt_method": "remotion_component"}),

    ("Particle Rain Storm", "motion_fx", "in_clip",
     "Rain streaks overlaid with appropriate splashes, wet surfaces. Atmospheric, moody, dramatic tension.",
     "rain particles, visible rain streaks, wet reflective surfaces, rain splashes, atmospheric storm, moody tension",
     {"method": "comfyui_workflow", "alt_method": "prompt_modifier"}),

    ("Particle Ember Float", "motion_fx", "in_clip",
     "Floating embers, sparks, or firefly particles. Warm, atmospheric, magical. Campfire to battle scene.",
     "floating ember particles, warm sparks rising, firefly glow, atmospheric warm particles, magical floating lights",
     {"method": "comfyui_workflow", "alt_method": "remotion_component"}),

    ("Lens Flare Anamorphic", "motion_fx", "in_clip",
     "Horizontal blue streak flares from bright light sources. Anamorphic lens signature. Abrams style.",
     "anamorphic lens flare, horizontal blue streak from bright light source, cinematic flare, J.J. Abrams style, light artifact",
     {"method": "comfyui_workflow", "alt_method": "prompt_modifier"}),

    ("Chromatic Aberration RGB", "motion_fx", "in_clip",
     "RGB color fringe at frame edges. Distressed lens or deliberate stylistic choice. Subtle to extreme.",
     "chromatic aberration, RGB color fringe splitting at edges, distressed lens effect, red and blue color separation",
     {"method": "ffmpeg_filter", "alt_method": "comfyui_workflow"}),

    ("Film Gate Weave", "motion_fx", "in_clip",
     "Subtle vertical frame instability mimicking film running through a projector gate. Organic imperfection.",
     "film gate weave, subtle vertical frame instability, organic projector movement, film running through gate, analog imperfection",
     {"method": "ffmpeg_filter", "alt_method": "comfyui_workflow"}),

    ("Infinite Zoom Fractal", "motion_fx", "in_clip",
     "Continuous zoom into image that reveals new scene inside, recursively. Hypnotic, infinite, psychedelic.",
     "infinite fractal zoom, continuous zooming into image revealing new scene inside, recursive zoom, hypnotic endless depth",
     {"method": "comfyui_workflow", "alt_method": "remotion_component"}),
]

for name, etype, cat, desc, prompt, impl in _motion_fx:
    EFFECTS.append({
        "name": name, "effect_type": etype, "category": cat,
        "description": desc, "prompt_fragment": prompt,
        "implementation": impl, "use_cases": [], "pairs_with": {},
    })

# ===== TRANSITIONS (20) =====
_transitions = [
    ("Cross Dissolve", "transition", "shot_transition",
     "Standard fade between two shots. Gradual opacity blend. Time passage or gentle scene change.",
     "cross dissolve transition, gradual opacity blend between two shots, gentle scene change, time passage",
     {"method": "ffmpeg_filter", "ffmpeg_cmd": "xfade=transition=fade:duration=1"}),

    ("Hard Cut Direct", "transition", "shot_transition",
     "Direct cut with no transition. Most common edit. Purposeful, clean, editorial.",
     "hard cut, direct edit between shots, no transition effect, clean purposeful cut",
     {"method": "ffmpeg_filter", "ffmpeg_cmd": "concat"}),

    ("J-Cut Audio Lead", "transition", "shot_transition",
     "Audio from next scene begins before video cuts. Pulls viewer into upcoming scene. Conversational flow.",
     "J-cut transition, audio from next scene heard before video transition, sound leads picture, conversational editing flow",
     {"method": "remotion_component", "alt_method": "ffmpeg_filter"}),

    ("L-Cut Video Lead", "transition", "shot_transition",
     "Video cuts to new scene while previous audio continues. Reaction shots, dialogue overlap.",
     "L-cut transition, video shows new scene while previous audio continues, reaction shot editing, dialogue overlap",
     {"method": "remotion_component", "alt_method": "ffmpeg_filter"}),

    ("Match Cut Visual", "transition", "shot_transition",
     "Cut between two shots sharing visual similarity — shape, movement, or color. 2001 bone-to-satellite.",
     "match cut transition, visual similarity between shots, matching shape or movement, seamless visual connection, 2001 style",
     {"method": "remotion_component", "alt_method": "prompt_modifier"}),

    ("Iris Wipe Circular", "transition", "shot_transition",
     "Circular reveal expanding or contracting. Classic silent film era, now used for retro or playful feel.",
     "iris wipe transition, circular reveal expanding from center, classic film transition, retro playful wipe",
     {"method": "ffmpeg_filter", "ffmpeg_cmd": "xfade=transition=circlecrop:duration=1"}),

    ("Light Leak Warm", "transition", "shot_transition",
     "Warm orange/amber light bleed between shots. Film changeover aesthetic, nostalgic, organic.",
     "light leak transition, warm orange amber light bleed between shots, film changeover aesthetic, nostalgic organic glow",
     {"method": "ffmpeg_filter", "alt_method": "remotion_component"}),

    ("Film Burn Overexpose", "transition", "shot_transition",
     "Overexposed celluloid burn effect. White-hot center spreading, film damage aesthetic, dramatic ending.",
     "film burn transition, overexposed celluloid burn spreading from edge, white-hot center, film damage aesthetic, dramatic",
     {"method": "ffmpeg_filter", "alt_method": "comfyui_workflow"}),

    ("Glitch Digital Corrupt", "transition", "shot_transition",
     "Digital corruption between shots. Data moshing, pixel sorting, codec artifact transition.",
     "glitch transition, digital corruption between shots, data moshing, pixel sorting, codec artifacts, broken digital signal",
     {"method": "ffmpeg_filter", "alt_method": "comfyui_workflow"}),

    ("Whip Pan Blur Transition", "transition", "shot_transition",
     "Fast horizontal blur connecting two shots. Both shots end/begin with motion blur that matches.",
     "whip pan blur transition, horizontal motion blur connecting two shots, matching blur on both ends, energetic scene change",
     {"method": "ffmpeg_filter", "ffmpeg_cmd": "xfade with motion blur overlay"}),

    ("Zoom Punch Through", "transition", "shot_transition",
     "Rapid zoom into element in shot A, emerge from element in shot B. Dynamic, social media popular.",
     "zoom transition, rapid zoom into detail then emerge in new scene, dynamic punch-through zoom, social media style transition",
     {"method": "ffmpeg_filter", "alt_method": "remotion_component"}),

    ("Fade to Black", "transition", "shot_transition",
     "Image fades to solid black. Scene ending, time passage, chapter break. The most final transition.",
     "fade to black, image gradually darkens to solid black, scene ending, chapter break, definitive closure",
     {"method": "ffmpeg_filter", "ffmpeg_cmd": "fade=out:st=0:d=1"}),

    ("Fade to White Flash", "transition", "shot_transition",
     "Image blows out to pure white. Impact, revelation, flashback entry, transcendence.",
     "fade to white, image blows out to pure white, impact flash, revelation moment, flashback entry, transcendent brightness",
     {"method": "ffmpeg_filter", "ffmpeg_cmd": "fade=out:st=0:d=0.5:color=white"}),

    ("Split Screen Dual", "transition", "shot_transition",
     "Show two shots simultaneously side by side. Comparison, parallel action, phone conversations.",
     "split screen, two shots displayed simultaneously side by side, parallel action, comparison, phone conversation framing",
     {"method": "remotion_component", "alt_method": "ffmpeg_filter"}),

    ("Push Slide Wipe", "transition", "shot_transition",
     "One shot physically pushes another off screen. Directional, editorial, clean motion.",
     "push slide transition, one shot pushes another off screen, directional sliding wipe, clean editorial motion",
     {"method": "ffmpeg_filter", "ffmpeg_cmd": "xfade=transition=slideleft:duration=0.5"}),

    ("Ink Bleed Reveal", "transition", "shot_transition",
     "Ink or paint bleeding across frame to reveal new shot underneath. Artistic, editorial, dramatic.",
     "ink bleed transition, dark ink spreading across frame revealing new shot underneath, artistic paint reveal, editorial dramatic",
     {"method": "comfyui_workflow", "alt_method": "remotion_component"}),

    ("Smoke Fog Reveal", "transition", "shot_transition",
     "Smoke or fog fills frame, clears to reveal new scene. Atmospheric, mysterious, theatrical.",
     "smoke fog transition, atmospheric smoke filling frame then clearing to reveal new scene, mysterious theatrical reveal",
     {"method": "comfyui_workflow", "alt_method": "prompt_modifier"}),

    ("Clock Wipe", "transition", "shot_transition",
     "Radial wipe like clock hand sweeping. Retro, time-related, Star Wars homage.",
     "clock wipe transition, radial sweeping wipe like clock hand, retro star wars style, time passage indication",
     {"method": "ffmpeg_filter", "ffmpeg_cmd": "xfade=transition=radial:duration=1"}),

    ("Morph Shape Blend", "transition", "shot_transition",
     "One image morphs into another via shape interpolation. Faces morphing, objects transforming.",
     "morph transition, one image shape-blending into another, face morphing, object transformation, smooth shape interpolation",
     {"method": "comfyui_workflow", "alt_method": "remotion_component"}),

    ("Page Turn", "transition", "shot_transition",
     "Page turning to reveal next shot. Book/magazine feel, presentation style, storybook narrative.",
     "page turn transition, turning page to reveal next scene, book magazine aesthetic, storybook narrative feel",
     {"method": "remotion_component", "alt_method": "ffmpeg_filter"}),
]

for name, etype, cat, desc, prompt, impl in _transitions:
    EFFECTS.append({
        "name": name, "effect_type": etype, "category": cat,
        "description": desc, "prompt_fragment": prompt,
        "implementation": impl, "use_cases": [], "pairs_with": {},
    })

# ===== COMBINATION / VARIANT EFFECTS (20+) =====
_combos = [
    ("Film Grain Light 35mm", "film_stock_emulation", "texture_overlay",
     "Light 35mm film grain overlay. Adds organic texture without overwhelming the image.",
     "light 35mm film grain overlay, subtle organic texture, barely visible grain pattern, adds analog warmth without dominating",
     {"method": "ffmpeg_filter", "alt_method": "comfyui_workflow", "ffmpeg_cmd": "noise=c0s=8:allf=t"}),

    ("Film Grain Heavy 16mm", "film_stock_emulation", "texture_overlay",
     "Heavy 16mm grain overlay. Visible, textured, documentary feel. Bolex/Eclair aesthetic.",
     "heavy 16mm film grain, visible coarse grain texture, documentary analog feel, Bolex camera aesthetic, rough organic texture",
     {"method": "ffmpeg_filter", "alt_method": "comfyui_workflow", "ffmpeg_cmd": "noise=c0s=20:allf=t"}),

    ("Vignette Dark Edges", "artistic_style", "lens_effect",
     "Darkened frame edges drawing attention to center. Classic lens falloff, dramatic focus.",
     "dark vignette, darkened frame edges, light falloff toward corners, attention drawn to center, classic lens vignetting",
     {"method": "ffmpeg_filter", "ffmpeg_cmd": "vignette=PI/4"}),

    ("Lens Distortion Barrel", "artistic_style", "lens_effect",
     "Barrel distortion mimicking wide-angle lens. Edges curve outward, center magnified slightly.",
     "barrel lens distortion, wide-angle edge curvature, edges bowing outward, fisheye-adjacent, immersive wide perspective",
     {"method": "ffmpeg_filter", "alt_method": "comfyui_workflow", "ffmpeg_cmd": "lenscorrection"}),

    ("Color Grade Teal Orange", "artistic_style", "color_grade",
     "Hollywood blockbuster teal/orange complementary grade. Warm skin tones against cool shadows.",
     "teal and orange color grade, warm orange skin tones, cool teal shadows and backgrounds, Hollywood blockbuster complementary palette",
     {"method": "lut", "lut_file": "teal_orange_blockbuster.cube", "alt_method": "ffmpeg_filter"}),

    ("Color Grade Desaturated Moody", "artistic_style", "color_grade",
     "Pulled-back saturation with lifted blacks. Moody, contemplative, indie film aesthetic.",
     "desaturated moody color grade, pulled-back muted saturation, lifted blacks, contemplative indie film look, muted palette",
     {"method": "lut", "lut_file": "desaturated_moody.cube", "alt_method": "ffmpeg_filter"}),

    ("Color Grade High Contrast BW", "artistic_style", "color_grade",
     "Aggressive black and white conversion with crushed blacks and blown highlights. Maximum drama.",
     "high contrast black and white, crushed deep blacks, blown bright whites, maximum tonal drama, stark monochrome",
     {"method": "lut", "lut_file": "high_contrast_bw.cube", "alt_method": "ffmpeg_filter"}),

    ("Letterbox Cinematic 2.39", "artistic_style", "framing",
     "Anamorphic widescreen letterbox bars. 2.39:1 aspect ratio, the cinema standard for scope films.",
     "2.39:1 anamorphic widescreen letterbox, black bars top and bottom, cinematic scope framing, epic widescreen",
     {"method": "ffmpeg_filter", "alt_method": "remotion_component", "ffmpeg_cmd": "crop=iw:iw/2.39"}),

    ("Letterbox Ultra-Wide 2.76", "artistic_style", "framing",
     "Ultra-wide letterbox for epic scope. Ben-Hur, Hateful Eight territory. Maximum panoramic framing.",
     "2.76:1 ultra-wide letterbox, extreme panoramic framing, epic scope, maximum horizontal field of view",
     {"method": "ffmpeg_filter", "ffmpeg_cmd": "crop=iw:iw/2.76"}),

    ("Light Leak Red Warm", "artistic_style", "lens_effect",
     "Warm red/orange light leak from film edge exposure. Nostalgic, analog imperfection, accidental beauty.",
     "warm red orange light leak, film edge exposure, nostalgic analog imperfection, warm light bleeding into frame",
     {"method": "comfyui_workflow", "alt_method": "remotion_component"}),

    ("Halation Highlight Bloom", "artistic_style", "lens_effect",
     "Soft glow bleeding from bright highlights into surrounding areas. Vintage lens or film halation effect.",
     "halation effect, soft warm glow bleeding from bright highlights, vintage lens bloom, diffused highlight edges, dreamy softness",
     {"method": "comfyui_workflow", "alt_method": "ffmpeg_filter"}),

    ("Film Scratch Damage", "film_stock_emulation", "texture_overlay",
     "Visible film scratches, dust, and hair. Aged projector print aesthetic. Grindhouse to art house.",
     "film scratch damage overlay, visible scratches dust and hair, aged projector print, worn celluloid, grindhouse aesthetic",
     {"method": "ffmpeg_filter", "alt_method": "comfyui_workflow"}),

    ("Flicker Projector", "film_stock_emulation", "texture_overlay",
     "Subtle exposure flicker mimicking old projector or early cinema. Adds organic temporal variation.",
     "projector flicker, subtle exposure variation, old cinema projection artifact, organic brightness oscillation, vintage screening",
     {"method": "ffmpeg_filter", "alt_method": "comfyui_workflow"}),

    ("Stabilization Smooth", "motion_fx", "post_processing",
     "Digital stabilization removing camera shake. Smooth gliding result from handheld footage.",
     "digital stabilization, smooth camera movement, removed camera shake, gliding stabilized footage, steady image",
     {"method": "ffmpeg_filter", "ffmpeg_cmd": "vidstabdetect + vidstabtransform"}),

    ("Defocus Soft Glow", "artistic_style", "lens_effect",
     "Gentle overall soft focus with glowing highlights. Pro-Mist filter equivalent, beauty/dream look.",
     "soft focus glow, gentle defocus, glowing highlights, Pro-Mist filter effect, dreamy beauty softness, romantic diffusion",
     {"method": "comfyui_workflow", "alt_method": "ffmpeg_filter"}),

    ("Day for Night", "artistic_style", "color_grade",
     "Color treatment making daylight footage appear as nighttime. Blue push, lowered exposure, moon-motivated.",
     "day for night color grade, blue color push, lowered exposure, daylight made to appear nighttime, moon-motivated lighting feel",
     {"method": "lut", "lut_file": "day_for_night.cube", "alt_method": "ffmpeg_filter"}),

    ("Split Tone Warm Shadows", "artistic_style", "color_grade",
     "Warm-toned shadows with cool highlights. Vintage faded aesthetic, Instagram-era editorial look.",
     "split tone grade, warm orange shadows, cool blue highlights, vintage faded aesthetic, editorial color split",
     {"method": "lut", "lut_file": "split_tone_warm_shadows.cube", "alt_method": "ffmpeg_filter"}),

    ("Text Lower Third", "motion_fx", "overlay",
     "Animated lower third text overlay for names, titles, locations. Broadcast standard identification.",
     "lower third text overlay, animated name title graphic, broadcast identification bar, clean professional text placement",
     {"method": "remotion_component", "alt_method": "ffmpeg_filter"}),

    ("Data Visualization Overlay", "motion_fx", "overlay",
     "Animated charts, graphs, statistics overlaid on footage. Documentary data storytelling.",
     "data visualization overlay, animated charts and graphs, statistics on screen, documentary data storytelling, infographic animation",
     {"method": "remotion_component"}),

    ("Countdown Leader", "transition", "shot_transition",
     "Classic film countdown leader (5-4-3-2-1). Retro, theatrical, nostalgic opening device.",
     "film countdown leader, classic 5 4 3 2 1 countdown, retro theatrical opening, vintage film leader with circles and numbers",
     {"method": "remotion_component", "alt_method": "ffmpeg_filter"}),
]

for name, etype, cat, desc, prompt, impl in _combos:
    EFFECTS.append({
        "name": name, "effect_type": etype, "category": cat,
        "description": desc, "prompt_fragment": prompt,
        "implementation": impl, "use_cases": [], "pairs_with": {},
    })


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------
def generate_id(name: str) -> str:
    slug = name.lower().replace(" ", "_").replace("/", "").replace("-", "_")[:50]
    short_hash = hashlib.md5(name.encode()).hexdigest()[:8]
    return f"fx_{short_hash}_{slug}"


def generate_all_presets() -> list:
    presets = []
    for fx in EFFECTS:
        preset = {
            "id": generate_id(fx["name"]),
            **fx,
        }
        presets.append(preset)
    return presets


# ---------------------------------------------------------------------------
# Embedding + Qdrant (reused pattern)
# ---------------------------------------------------------------------------
def embed_texts(texts: list[str], api_key: str) -> list[list[float]]:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    all_embeddings = []
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(input=batch, model="text-embedding-3-small")
        all_embeddings.extend([item.embedding for item in response.data])
        print(f"  Embedded {min(i + batch_size, len(texts))}/{len(texts)}")
    return all_embeddings


def upload_to_qdrant(presets: list, embeddings: list[list[float]], qdrant_url: str, qdrant_key: str):
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct
    client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
    points = [PointStruct(id=i + 1, vector=emb, payload=preset) for i, (preset, emb) in enumerate(zip(presets, embeddings))]
    batch_size = 100
    for i in range(0, len(points), batch_size):
        client.upsert(collection_name="effects_presets", points=points[i : i + batch_size])
        print(f"  Upserted {min(i + batch_size, len(points))}/{len(points)}")
    info = client.get_collection("effects_presets")
    print(f"  Collection now has {info.points_count} points")


def query_qdrant(query_text: str, qdrant_url: str, qdrant_key: str, openai_key: str, top_k: int = 5):
    from qdrant_client import QdrantClient
    embeddings = embed_texts([query_text], openai_key)
    client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
    results = client.query_points(collection_name="effects_presets", query=embeddings[0], limit=top_k, with_payload=True)
    print(f'\nQuery: "{query_text}"')
    print(f"Top {top_k} results:\n")
    for point in results.points:
        p = point.payload
        print(f"  [{point.score:.4f}] {p['name']} ({p['effect_type']} / {p['category']})")
        print(f"           Method: {p['implementation'].get('method', 'N/A')}")
        print(f"           Prompt: {p['prompt_fragment'][:100]}...")
        print()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="PopTech Effects Presets RAG Tool")
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--query", type=str)
    parser.add_argument("--stats", action="store_true")
    parser.add_argument("--qdrant-url", default=os.environ.get("QDRANT_URL", "http://localhost:16333"))
    parser.add_argument("--qdrant-key", default=os.environ.get("QDRANT_API_KEY", ""))
    parser.add_argument("--openai-key", default=os.environ.get("OPENAI_API_KEY", ""))
    args = parser.parse_args()

    if args.generate:
        presets = generate_all_presets()
        out_path = Path(__file__).parent / "effects_presets.json"
        with open(out_path, "w") as f:
            json.dump(presets, f, indent=2)
        print(f"Generated {len(presets)} effects presets -> {out_path}")
        cats = {}
        for p in presets:
            cats[p["effect_type"]] = cats.get(p["effect_type"], 0) + 1
        for cat, count in sorted(cats.items()):
            print(f"  {cat}: {count}")
        methods = set(p["implementation"].get("method") for p in presets)
        print(f"  Implementation methods: {sorted(methods)}")

    elif args.upload:
        if not args.openai_key:
            print("ERROR: OPENAI_API_KEY required."); sys.exit(1)
        if not args.qdrant_key:
            print("ERROR: QDRANT_API_KEY required."); sys.exit(1)
        presets_path = Path(__file__).parent / "effects_presets.json"
        if not presets_path.exists():
            print("No presets JSON found. Run --generate first."); sys.exit(1)
        with open(presets_path) as f:
            presets = json.load(f)
        # Embed prompt_fragment + description concatenated for richer search
        texts = [f"{p['prompt_fragment']} {p['description']}" for p in presets]
        print(f"Embedding {len(presets)} effects (prompt + description)...")
        embeddings = embed_texts(texts, args.openai_key)
        print(f"Uploading to Qdrant ({args.qdrant_url})...")
        upload_to_qdrant(presets, embeddings, args.qdrant_url, args.qdrant_key)
        print("Done.")

    elif args.query:
        if not args.openai_key or not args.qdrant_key:
            print("ERROR: Both OPENAI_API_KEY and QDRANT_API_KEY required."); sys.exit(1)
        query_qdrant(args.query, args.qdrant_url, args.qdrant_key, args.openai_key)

    elif args.stats:
        if not args.qdrant_key:
            print("ERROR: QDRANT_API_KEY required."); sys.exit(1)
        from qdrant_client import QdrantClient
        client = QdrantClient(url=args.qdrant_url, api_key=args.qdrant_key)
        info = client.get_collection("effects_presets")
        print(f"Collection: effects_presets\nPoints: {info.points_count}\nVectors: {info.config.params.vectors.size}d\nStatus: {info.status.name}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
