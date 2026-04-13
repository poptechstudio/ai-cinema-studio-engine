"""
PopTech Cinema Studio — Lighting Presets RAG Population Script
Task 2.2: Populate Qdrant lighting_presets collection with 50+ entries.

Usage:
  python tools/populate_lighting_presets.py --generate
  python tools/populate_lighting_presets.py --upload
  python tools/populate_lighting_presets.py --query "text"
  python tools/populate_lighting_presets.py --stats
"""

import json
import os
import sys
import hashlib
from pathlib import Path

# ---------------------------------------------------------------------------
# Lighting setup definitions — 33 base setups x color temp variants = 50+
# ---------------------------------------------------------------------------
LIGHTING_SETUPS = [
    # === Standard Cinema Setups ===
    {
        "setup_type": "Three-Point Classic",
        "description": "Standard three-point setup with balanced key, fill, and backlight. The workhorse of cinema lighting.",
        "key_light": {"position": "45 degrees camera-left, above eye level", "type": "large softbox or Fresnel with diffusion", "intensity": "primary (2:1 key-to-fill ratio)", "color_temp_k": 5600},
        "fill_light": {"position": "camera-right, near lens axis", "type": "bounce board or soft fill", "intensity": "moderate — preserves shadow shape without going flat", "color_temp_k": 5600},
        "back_light": {"position": "behind subject, opposite key, elevated", "type": "small Fresnel or dedolight", "intensity": "subtle edge separation", "color_temp_k": 5600},
        "mood_tags": ["balanced", "natural", "professional", "clean"],
        "use_cases": ["interview", "corporate", "dialogue_scene", "general_purpose"],
        "post_processing_notes": "Neutral base for any color grade. Works with all film stock emulations.",
        "variants": [
            {"suffix": "daylight", "color_temperature_k": 5600, "variant_note": "daylight-balanced, neutral"},
            {"suffix": "tungsten", "color_temperature_k": 3200, "variant_note": "warm tungsten, indoor classic"},
        ],
    },
    {
        "setup_type": "Three-Point High Contrast",
        "description": "Modified three-point with minimal fill for dramatic contrast. Shadows are allowed to go deep.",
        "key_light": {"position": "45 degrees camera-left, above eye level", "type": "Fresnel with barndoors, no diffusion", "intensity": "primary (4:1 or higher key-to-fill)", "color_temp_k": 3200},
        "fill_light": {"position": "camera-right", "type": "neg fill (black flag) — subtractive", "intensity": "minimal to none", "color_temp_k": 3200},
        "back_light": {"position": "behind subject, hard edge", "type": "bare Fresnel, tight barndoors", "intensity": "strong rim for separation", "color_temp_k": 3200},
        "mood_tags": ["dramatic", "intense", "contrasty", "cinematic"],
        "use_cases": ["drama", "thriller", "emotional_scene", "music_video"],
        "post_processing_notes": "Lift shadows slightly in post to retain detail. Pairs with crushed black LUT.",
        "variants": [
            {"suffix": "tungsten", "color_temperature_k": 3200, "variant_note": "warm dramatic"},
            {"suffix": "cool", "color_temperature_k": 5600, "variant_note": "cold dramatic, clinical"},
        ],
    },
    {
        "setup_type": "Rembrandt",
        "description": "Classic portrait lighting named after the painter. Defined by triangular highlight on shadow-side cheek.",
        "key_light": {"position": "45 degrees camera-left, slightly above eye level", "type": "large softbox or book light", "intensity": "primary (3:1 key-to-fill ratio)", "color_temp_k": 3200},
        "fill_light": {"position": "camera-right, near lens axis", "type": "bounce card or neg fill", "intensity": "subtle — enough for shadow detail, not enough to flatten", "color_temp_k": 3200},
        "back_light": {"position": "behind subject, opposite key", "type": "hard source with barndoors", "intensity": "edge separation only", "color_temp_k": 3200},
        "mood_tags": ["dramatic", "portrait", "classic", "warm", "painterly"],
        "use_cases": ["interview", "portrait", "dramatic_scene", "product_hero"],
        "post_processing_notes": "Pairs well with Kodak Vision3 500T film stock emulation. IC-Light can adjust key angle in post.",
        "variants": [
            {"suffix": "tungsten_warm", "color_temperature_k": 3200, "variant_note": "warm tungsten, classic feel"},
            {"suffix": "daylight", "color_temperature_k": 5600, "variant_note": "neutral daylight, modern take"},
        ],
    },
    {
        "setup_type": "Split Lighting",
        "description": "Half the face lit, half in complete shadow. Maximum drama, reveals duality or conflict.",
        "key_light": {"position": "90 degrees to one side, at eye level", "type": "hard source (Fresnel or bare bulb)", "intensity": "strong, no spill to shadow side", "color_temp_k": 3200},
        "fill_light": {"position": "none", "type": "neg fill on shadow side", "intensity": "zero — full shadow", "color_temp_k": 0},
        "back_light": {"position": "behind, opposite key", "type": "optional subtle rim", "intensity": "minimal", "color_temp_k": 3200},
        "mood_tags": ["extreme_dramatic", "duality", "conflict", "noir_adjacent"],
        "use_cases": ["villain_reveal", "internal_conflict", "dramatic_portrait", "thriller"],
        "post_processing_notes": "Can push further with crushed blacks in post. ComfyUI IC-Light can add subtle fill if needed.",
        "variants": [
            {"suffix": "tungsten", "color_temperature_k": 3200, "variant_note": "warm, intimate conflict"},
            {"suffix": "cool_blue", "color_temperature_k": 7500, "variant_note": "cold, clinical tension"},
        ],
    },
    {
        "setup_type": "Loop Lighting",
        "description": "Small shadow loop from nose onto cheek. Flattering, slightly more dramatic than flat.",
        "key_light": {"position": "30-45 degrees camera-left, slightly above", "type": "medium softbox", "intensity": "primary, gentle falloff", "color_temp_k": 5600},
        "fill_light": {"position": "on-axis, below key", "type": "reflector or soft fill", "intensity": "gentle 2:1 ratio", "color_temp_k": 5600},
        "back_light": {"position": "behind, above", "type": "hairlight", "intensity": "subtle separation", "color_temp_k": 5600},
        "mood_tags": ["flattering", "natural", "portrait", "gentle"],
        "use_cases": ["beauty", "interview", "headshot", "corporate_portrait"],
        "post_processing_notes": "Clean base for beauty retouching. Minimal post needed.",
        "variants": [
            {"suffix": "daylight", "color_temperature_k": 5600, "variant_note": "clean daylight"},
        ],
    },
    {
        "setup_type": "Butterfly Paramount",
        "description": "Key directly above and in front, creating butterfly shadow under nose. Classic Hollywood glamour.",
        "key_light": {"position": "directly above camera, elevated 45 degrees", "type": "large soft source (beauty dish or octabox)", "intensity": "primary, even and wrapping", "color_temp_k": 5600},
        "fill_light": {"position": "below face, reflector on lap or table", "type": "silver or white reflector", "intensity": "fills under-chin shadows", "color_temp_k": 5600},
        "back_light": {"position": "behind, elevated", "type": "hairlight for glamour halo", "intensity": "accent", "color_temp_k": 5600},
        "mood_tags": ["glamour", "beauty", "classic_hollywood", "elegant"],
        "use_cases": ["beauty_commercial", "fashion", "portrait", "product_beauty"],
        "post_processing_notes": "Skin retouching workflow in ComfyUI. Pairs with soft-focus vintage LUTs.",
        "variants": [
            {"suffix": "daylight_glamour", "color_temperature_k": 5600, "variant_note": "clean glamour"},
            {"suffix": "warm_golden", "color_temperature_k": 4500, "variant_note": "warm golden glamour"},
        ],
    },
    {
        "setup_type": "Broad Lighting",
        "description": "Lit side of face turned toward camera. Opens up the face, used for thinner appearance.",
        "key_light": {"position": "on the side of face closest to camera", "type": "medium softbox", "intensity": "primary", "color_temp_k": 5600},
        "fill_light": {"position": "opposite side, gentle", "type": "bounce", "intensity": "moderate fill", "color_temp_k": 5600},
        "back_light": {"position": "behind, rim on shadow side", "type": "small Fresnel", "intensity": "separation", "color_temp_k": 5600},
        "mood_tags": ["open", "friendly", "approachable", "natural"],
        "use_cases": ["interview", "corporate", "vlog", "testimonial"],
        "post_processing_notes": "Standard color correction. No special treatment needed.",
        "variants": [
            {"suffix": "daylight", "color_temperature_k": 5600, "variant_note": "daylight balanced"},
        ],
    },
    {
        "setup_type": "Short Lighting",
        "description": "Shadow side of face toward camera. Adds depth and slimming effect, more dramatic than broad.",
        "key_light": {"position": "on far side of face from camera", "type": "medium softbox or Fresnel with diffusion", "intensity": "primary, sculpting", "color_temp_k": 3200},
        "fill_light": {"position": "near camera, subtle", "type": "bounce or soft fill", "intensity": "minimal — maintain shadow depth", "color_temp_k": 3200},
        "back_light": {"position": "behind subject, camera-side", "type": "rim light", "intensity": "moderate for dimension", "color_temp_k": 3200},
        "mood_tags": ["sculpted", "dimensional", "dramatic_natural", "slimming"],
        "use_cases": ["portrait", "drama", "interview_dramatic", "character_intro"],
        "post_processing_notes": "Works well with slightly desaturated grades. Film stock emulation adds character.",
        "variants": [
            {"suffix": "tungsten", "color_temperature_k": 3200, "variant_note": "warm tungsten"},
            {"suffix": "daylight", "color_temperature_k": 5600, "variant_note": "neutral daylight"},
        ],
    },
    {
        "setup_type": "Rim Edge Lighting",
        "description": "Subject mostly in silhouette with strong edge/rim light outlining the form. Mysterious, powerful.",
        "key_light": {"position": "none from front", "type": "absent — darkness is the key", "intensity": "zero front light", "color_temp_k": 0},
        "fill_light": {"position": "none or extremely subtle ambient", "type": "ambient spill only", "intensity": "near zero", "color_temp_k": 0},
        "back_light": {"position": "behind subject, both sides", "type": "hard sources, barndoors tight", "intensity": "strong rim defining the silhouette", "color_temp_k": 5600},
        "mood_tags": ["mysterious", "powerful", "silhouette", "epic", "dramatic"],
        "use_cases": ["hero_reveal", "title_sequence", "villain_entrance", "product_silhouette"],
        "post_processing_notes": "Crush blacks in post. Can add subtle front fill with IC-Light if needed for face detail.",
        "variants": [
            {"suffix": "daylight", "color_temperature_k": 5600, "variant_note": "white rim"},
            {"suffix": "warm_amber", "color_temperature_k": 2700, "variant_note": "warm golden rim"},
            {"suffix": "cool_blue", "color_temperature_k": 8000, "variant_note": "cold blue rim, sci-fi feel"},
        ],
    },
    {
        "setup_type": "Practical Motivated",
        "description": "Lighting motivated by visible in-scene sources — table lamps, neon signs, TV screens, windows.",
        "key_light": {"position": "near the practical source in frame", "type": "hidden key matching practical color and direction", "intensity": "matched to practical, natural feeling", "color_temp_k": 2700},
        "fill_light": {"position": "ambient bounce from scene elements", "type": "bounce from walls/ceiling", "intensity": "natural room ambient", "color_temp_k": 3200},
        "back_light": {"position": "another practical or window behind", "type": "motivated by scene", "intensity": "varies with scene", "color_temp_k": 3200},
        "mood_tags": ["natural", "realistic", "immersive", "motivated", "environmental"],
        "use_cases": ["interior_scene", "restaurant", "home_interior", "naturalistic_drama"],
        "post_processing_notes": "Preserve mixed color temps in grade — they add realism. Don't white-balance to neutral.",
        "variants": [
            {"suffix": "warm_interior", "color_temperature_k": 2700, "variant_note": "warm residential interior"},
            {"suffix": "mixed_neon", "color_temperature_k": 4000, "variant_note": "mixed sources, urban interior"},
        ],
    },
    # === Mood / Environment Setups ===
    {
        "setup_type": "Golden Hour",
        "description": "Low-angle warm sunlight with long shadows. The last hour before sunset — the most cinematic natural light.",
        "key_light": {"position": "low angle from horizon, warm directional", "type": "natural sun (or large tungsten bounced through silk)", "intensity": "warm and soft but directional", "color_temp_k": 3500},
        "fill_light": {"position": "open sky ambient", "type": "natural skylight fill from above", "intensity": "gentle ambient", "color_temp_k": 5500},
        "back_light": {"position": "sun can double as backlight if shooting toward it", "type": "natural flare and rim", "intensity": "varies with angle", "color_temp_k": 3500},
        "mood_tags": ["warm", "romantic", "nostalgic", "cinematic", "golden"],
        "use_cases": ["romantic_scene", "establishing_shot", "portrait_outdoor", "commercial_lifestyle"],
        "post_processing_notes": "Enhance warm tones. Kodak Vision3 50D or Fuji Eterna emulation. Push highlights warm.",
        "variants": [
            {"suffix": "early", "color_temperature_k": 4000, "variant_note": "early golden hour, slightly cooler"},
            {"suffix": "late", "color_temperature_k": 2800, "variant_note": "deep golden, moments before sunset"},
        ],
    },
    {
        "setup_type": "Blue Hour",
        "description": "Cool ambient light after sunset, before full dark. No direct sun, everything bathed in soft blue.",
        "key_light": {"position": "ambient sky from all directions", "type": "natural diffused skylight", "intensity": "low, even, no hard shadows", "color_temp_k": 7500},
        "fill_light": {"position": "omnidirectional ambient", "type": "sky", "intensity": "very low", "color_temp_k": 7500},
        "back_light": {"position": "none natural — add practical lights for interest", "type": "city lights, car headlights, windows", "intensity": "accent only", "color_temp_k": 3200},
        "mood_tags": ["melancholy", "quiet", "contemplative", "cool", "twilight"],
        "use_cases": ["transition_scene", "reflective_moment", "establishing_evening", "documentary_mood"],
        "post_processing_notes": "Push blue in shadows, add subtle warm practicals for contrast. Low saturation grade.",
        "variants": [
            {"suffix": "pure_blue", "color_temperature_k": 7500, "variant_note": "pure cool blue ambient"},
        ],
    },
    {
        "setup_type": "Moonlight",
        "description": "Cool blue toplight simulating moonlight. Deep shadows, minimal fill, night exterior feeling.",
        "key_light": {"position": "high overhead, slightly behind", "type": "large soft source with blue gel (CTB)", "intensity": "low, cool, toplight", "color_temp_k": 8000},
        "fill_light": {"position": "ambient bounce from ground", "type": "minimal bounce", "intensity": "very low", "color_temp_k": 8000},
        "back_light": {"position": "moonlight doubles as backlight", "type": "same source raking across", "intensity": "subtle rim on shoulders and hair", "color_temp_k": 8000},
        "mood_tags": ["nocturnal", "mysterious", "serene", "ethereal", "cool"],
        "use_cases": ["night_exterior", "romantic_night", "horror_exterior", "establishing_night"],
        "post_processing_notes": "Desaturate slightly, push blue channel. Add grain for night film stock feel.",
        "variants": [
            {"suffix": "cool_silver", "color_temperature_k": 8000, "variant_note": "silver moonlight"},
            {"suffix": "blue_deep", "color_temperature_k": 10000, "variant_note": "deep blue-white, full moon"},
        ],
    },
    {
        "setup_type": "Overcast Soft",
        "description": "Completely diffused skylight, no hard shadows. The sky is one giant softbox.",
        "key_light": {"position": "overhead, omnidirectional", "type": "natural overcast sky", "intensity": "even, soft, wrapping", "color_temp_k": 6500},
        "fill_light": {"position": "ground bounce", "type": "natural ground reflection", "intensity": "gentle", "color_temp_k": 6500},
        "back_light": {"position": "none — no directional separation", "type": "none", "intensity": "flat", "color_temp_k": 0},
        "mood_tags": ["soft", "flat", "gentle", "neutral", "documentary"],
        "use_cases": ["documentary", "outdoor_portrait", "product_natural", "lifestyle"],
        "post_processing_notes": "Add contrast in post to compensate for flat lighting. Can add directional fill with IC-Light.",
        "variants": [
            {"suffix": "neutral", "color_temperature_k": 6500, "variant_note": "neutral overcast"},
        ],
    },
    {
        "setup_type": "Hard Noon Sun",
        "description": "Harsh overhead midday sun. Deep eye socket shadows, high contrast, unflattering but authentic.",
        "key_light": {"position": "directly overhead", "type": "hard direct sunlight", "intensity": "maximum, harsh", "color_temp_k": 5600},
        "fill_light": {"position": "ground bounce from pavement", "type": "harsh bounce", "intensity": "hot spots on ground plane", "color_temp_k": 5600},
        "back_light": {"position": "none needed — overhead key provides toplight", "type": "same source", "intensity": "harsh top edge", "color_temp_k": 5600},
        "mood_tags": ["harsh", "raw", "authentic", "documentary", "brutal"],
        "use_cases": ["desert_scene", "war_documentary", "verite", "music_video_raw"],
        "post_processing_notes": "Bleach bypass or desaturated LUT. 16mm film grain adds texture.",
        "variants": [
            {"suffix": "harsh_daylight", "color_temperature_k": 5600, "variant_note": "harsh midday sun"},
        ],
    },
    {
        "setup_type": "Neon Urban Night",
        "description": "Multiple colored neon and LED sources. Urban nightlife, wet reflections, cyberpunk aesthetic.",
        "key_light": {"position": "from neon signs at various angles", "type": "colored LED/neon practicals", "intensity": "medium, colored", "color_temp_k": 0},
        "fill_light": {"position": "reflected from wet surfaces", "type": "colored bounce from environment", "intensity": "ambient neon spill", "color_temp_k": 0},
        "back_light": {"position": "neon behind subject", "type": "colored rim from environmental sources", "intensity": "strong colored rim", "color_temp_k": 0},
        "mood_tags": ["cyberpunk", "urban", "neon", "night", "colorful", "energetic"],
        "use_cases": ["music_video", "urban_night", "cyberpunk_scene", "nightlife_commercial"],
        "post_processing_notes": "Preserve neon saturation. Add wet/reflective surfaces in generation prompt. Halation on highlights.",
        "variants": [
            {"suffix": "pink_blue", "color_temperature_k": 4500, "variant_note": "pink and blue neon, classic cyberpunk"},
            {"suffix": "green_red", "color_temperature_k": 4000, "variant_note": "green and red, Asian market aesthetic"},
        ],
    },
    {
        "setup_type": "Candlelight",
        "description": "Extremely warm, flickering, intimate. Motivated by visible candles in frame.",
        "key_light": {"position": "below face, from candle level", "type": "candle flame or warm LED flicker", "intensity": "very low, intimate", "color_temp_k": 1800},
        "fill_light": {"position": "ambient bounce from nearby surfaces", "type": "warm reflected glow", "intensity": "minimal", "color_temp_k": 1800},
        "back_light": {"position": "none — darkness surrounds", "type": "darkness", "intensity": "zero", "color_temp_k": 0},
        "mood_tags": ["intimate", "warm", "romantic", "religious", "period"],
        "use_cases": ["period_drama", "romantic_dinner", "religious_scene", "intimate_confession"],
        "post_processing_notes": "Ultra-warm grade, crushed shadows. Barry Lyndon reference. Add flicker in post if static.",
        "variants": [
            {"suffix": "single_candle", "color_temperature_k": 1800, "variant_note": "single candle, maximum intimacy"},
        ],
    },
    {
        "setup_type": "Firelight",
        "description": "Warm orange animated light from campfire or fireplace. Dancing shadows on faces.",
        "key_light": {"position": "low, from fire source position", "type": "warm flickering source (fire or animated warm LED)", "intensity": "medium, animated", "color_temp_k": 2200},
        "fill_light": {"position": "ambient warm glow on surroundings", "type": "warm bounce from nearby surfaces", "intensity": "low ambient", "color_temp_k": 2200},
        "back_light": {"position": "darkness behind, stars or moonlight possible", "type": "cool ambient if exterior", "intensity": "subtle contrast to fire warmth", "color_temp_k": 8000},
        "mood_tags": ["warm", "primal", "storytelling", "camping", "animated_shadows"],
        "use_cases": ["campfire_scene", "storytelling", "survival", "period_exterior_night"],
        "post_processing_notes": "Warm shadows, cool highlights for contrast. Animate shadow flicker in post.",
        "variants": [
            {"suffix": "campfire", "color_temperature_k": 2200, "variant_note": "outdoor campfire"},
            {"suffix": "fireplace_interior", "color_temperature_k": 2500, "variant_note": "indoor fireplace, warmer walls"},
        ],
    },
    {
        "setup_type": "Fluorescent Industrial",
        "description": "Green-tinted overhead fluorescent tubes. Institutional, unsettling, clinical.",
        "key_light": {"position": "directly overhead, flat", "type": "fluorescent tubes (green spike)", "intensity": "harsh, flat, overhead", "color_temp_k": 4200},
        "fill_light": {"position": "bounce from institutional walls", "type": "green-tinted bounce", "intensity": "flat, unflattering", "color_temp_k": 4200},
        "back_light": {"position": "none — flat industrial lighting", "type": "none", "intensity": "flat", "color_temp_k": 0},
        "mood_tags": ["clinical", "unsettling", "institutional", "green_tint", "horror_adjacent"],
        "use_cases": ["hospital", "prison", "office_horror", "interrogation", "institutional_scene"],
        "post_processing_notes": "Leave the green cast — it's the point. Can push further with green tint LUT.",
        "variants": [
            {"suffix": "green_cast", "color_temperature_k": 4200, "variant_note": "standard fluorescent green"},
        ],
    },
    {
        "setup_type": "Mixed Color Temperature",
        "description": "Deliberate warm/cool contrast. Warm tungsten practicals against cool window daylight.",
        "key_light": {"position": "from window, cool daylight", "type": "natural daylight through window", "intensity": "medium, directional", "color_temp_k": 5600},
        "fill_light": {"position": "room interior, warm practicals", "type": "tungsten table lamp, warm bulbs", "intensity": "low ambient warmth", "color_temp_k": 2700},
        "back_light": {"position": "warm practical behind subject", "type": "tungsten practical", "intensity": "warm rim accent", "color_temp_k": 2700},
        "mood_tags": ["natural", "realistic", "mixed", "environmental", "textured"],
        "use_cases": ["interior_scene", "naturalistic_drama", "documentary_interior", "real_estate"],
        "post_processing_notes": "Do NOT white-balance to one temp. The warm/cool contrast is the aesthetic. Preserve both.",
        "variants": [
            {"suffix": "warm_cool", "color_temperature_k": 4000, "variant_note": "warm interior vs cool window"},
        ],
    },
    # === Genre-Specific Setups ===
    {
        "setup_type": "Film Noir",
        "description": "Single hard source, deep shadows, venetian blind patterns, chiaroscuro. 1940s crime aesthetic.",
        "key_light": {"position": "high and to side, through venetian blinds or gobo", "type": "hard Fresnel with gobo/cookie patterns", "intensity": "strong, patterned", "color_temp_k": 3200},
        "fill_light": {"position": "none — darkness is essential", "type": "neg fill", "intensity": "zero", "color_temp_k": 0},
        "back_light": {"position": "hard rim from behind, low angle", "type": "bare bulb or small Fresnel", "intensity": "slash of light on shoulder or hat brim", "color_temp_k": 3200},
        "mood_tags": ["noir", "mysterious", "dangerous", "chiaroscuro", "crime"],
        "use_cases": ["noir_scene", "detective", "crime_drama", "femme_fatale", "thriller"],
        "post_processing_notes": "Black and white conversion option. High contrast LUT. Venetian blind gobo patterns.",
        "variants": [
            {"suffix": "classic_bw", "color_temperature_k": 3200, "variant_note": "classic black and white noir"},
            {"suffix": "neo_noir_color", "color_temperature_k": 4000, "variant_note": "neo-noir with color, Blade Runner-adjacent"},
        ],
    },
    {
        "setup_type": "Horror Underlighting",
        "description": "Light from below the face, unnatural angles. Rim-only with colored gels. Disorienting, threatening.",
        "key_light": {"position": "below face, looking up", "type": "hard source from ground level", "intensity": "medium-strong, creates inverted shadows", "color_temp_k": 3200},
        "fill_light": {"position": "none — let it be unsettling", "type": "darkness", "intensity": "zero", "color_temp_k": 0},
        "back_light": {"position": "colored rim, red or green gel", "type": "hard source with color gel", "intensity": "colored accent", "color_temp_k": 0},
        "mood_tags": ["horror", "unsettling", "threatening", "supernatural", "inverted"],
        "use_cases": ["horror_scene", "monster_reveal", "nightmare", "campfire_ghost_story"],
        "post_processing_notes": "Desaturate skin tones. Push green or red in shadows. Add grain and slight blur.",
        "variants": [
            {"suffix": "warm_underlight", "color_temperature_k": 3200, "variant_note": "warm underlight, torchlight feel"},
            {"suffix": "green_sickly", "color_temperature_k": 4500, "variant_note": "green-tinted, sickly supernatural"},
        ],
    },
    {
        "setup_type": "Sci-Fi Blue Key",
        "description": "Cool blue key light with warm practicals. Lens flare motivated by in-scene tech. Futuristic.",
        "key_light": {"position": "from screen/tech source, cool blue", "type": "large LED panel with CTB, simulating screen light", "intensity": "medium, cool wash", "color_temp_k": 8000},
        "fill_light": {"position": "warm practicals from console displays", "type": "small warm LED accents", "intensity": "low, colored", "color_temp_k": 3200},
        "back_light": {"position": "cool rim from overhead fixtures", "type": "blue-white LED strip", "intensity": "strong rim", "color_temp_k": 7500},
        "mood_tags": ["futuristic", "sci-fi", "tech", "cool", "blue_key"],
        "use_cases": ["spaceship_interior", "tech_demo", "sci-fi_drama", "cyberpunk_interior"],
        "post_processing_notes": "Teal and orange grade. Add lens flare. Anamorphic streaks from highlights.",
        "variants": [
            {"suffix": "blue_warm_accent", "color_temperature_k": 6500, "variant_note": "blue key with warm accents"},
        ],
    },
    {
        "setup_type": "Commercial Product",
        "description": "Large soft key, white cyclorama, clean and bright. Hero product lighting for advertising.",
        "key_light": {"position": "large overhead, slight angle", "type": "very large softbox or scrim overhead", "intensity": "bright, even, wrapping", "color_temp_k": 5600},
        "fill_light": {"position": "white cyc bounce from all sides", "type": "white studio walls and floor", "intensity": "high — minimal shadows", "color_temp_k": 5600},
        "back_light": {"position": "behind product, low angle", "type": "strip softbox for edge definition", "intensity": "accent edge", "color_temp_k": 5600},
        "mood_tags": ["clean", "bright", "commercial", "product", "white"],
        "use_cases": ["product_hero", "e-commerce", "commercial", "packshot", "beauty_product"],
        "post_processing_notes": "Clean white point. Minimal grading — accuracy matters. Product color fidelity.",
        "variants": [
            {"suffix": "bright_white", "color_temperature_k": 5600, "variant_note": "standard bright product lighting"},
            {"suffix": "warm_luxury", "color_temperature_k": 4500, "variant_note": "slightly warm for luxury products"},
        ],
    },
    {
        "setup_type": "Documentary Available Light",
        "description": "Minimal lighting intervention. Work with what's there — windows, overhead fixtures, natural.",
        "key_light": {"position": "whatever the environment provides", "type": "natural/existing sources", "intensity": "as-is, supplemented minimally", "color_temp_k": 5000},
        "fill_light": {"position": "natural ambient", "type": "environment", "intensity": "natural", "color_temp_k": 5000},
        "back_light": {"position": "environmental", "type": "whatever exists", "intensity": "uncontrolled", "color_temp_k": 5000},
        "mood_tags": ["authentic", "raw", "documentary", "verite", "unpolished"],
        "use_cases": ["documentary", "verite", "news", "behind_the_scenes", "reality"],
        "post_processing_notes": "Light normalization in post. Shoot LOG to preserve latitude. Grade for consistency.",
        "variants": [
            {"suffix": "natural_mixed", "color_temperature_k": 5000, "variant_note": "mixed natural sources"},
        ],
    },
    {
        "setup_type": "Music Video Dramatic",
        "description": "Colored gels, haze, strong backlight. Dramatic and stylized for performance energy.",
        "key_light": {"position": "from side, colored gel", "type": "hard source with colored gel (magenta, blue, amber)", "intensity": "strong, stylized", "color_temp_k": 0},
        "fill_light": {"position": "contrasting color from opposite side", "type": "hard source with complementary gel", "intensity": "matching key for dual-color look", "color_temp_k": 0},
        "back_light": {"position": "strong backlight through haze", "type": "large source through atmospheric haze", "intensity": "strong, volumetric", "color_temp_k": 5600},
        "mood_tags": ["energetic", "stylized", "performance", "colorful", "haze"],
        "use_cases": ["music_video", "concert", "performance", "dance_sequence"],
        "post_processing_notes": "Push saturation. Add haze/atmospheric in generation prompt. Lens flare from backlight.",
        "variants": [
            {"suffix": "magenta_blue", "color_temperature_k": 4500, "variant_note": "magenta key, blue fill"},
            {"suffix": "amber_teal", "color_temperature_k": 4500, "variant_note": "amber key, teal fill"},
        ],
    },
    {
        "setup_type": "Corporate Clean",
        "description": "Soft flattering key, fill for web compression, clean background. Professional and approachable.",
        "key_light": {"position": "30 degrees off-axis, slightly above", "type": "large softbox, very diffused", "intensity": "gentle, wrapping", "color_temp_k": 5600},
        "fill_light": {"position": "on-axis, near camera", "type": "ring light or soft panel", "intensity": "moderate — keeps shadows open for video compression", "color_temp_k": 5600},
        "back_light": {"position": "behind subject, opposite key", "type": "soft hairlight", "intensity": "gentle separation from background", "color_temp_k": 5600},
        "mood_tags": ["professional", "clean", "approachable", "corporate", "web"],
        "use_cases": ["corporate_video", "zoom_call", "linkedin_content", "training_video"],
        "post_processing_notes": "Clean, neutral grade. Optimize for web compression — avoid fine detail in shadows.",
        "variants": [
            {"suffix": "neutral_clean", "color_temperature_k": 5600, "variant_note": "standard corporate neutral"},
        ],
    },
    {
        "setup_type": "Anime Stylized Flat",
        "description": "Flat key lighting with strong colored rim. Exaggerated color, minimal shadow. Anime/cartoon aesthetic.",
        "key_light": {"position": "front, flat, even", "type": "large diffused panel", "intensity": "even, minimal shadow", "color_temp_k": 5600},
        "fill_light": {"position": "flat fill from all angles", "type": "bounce from all sides", "intensity": "very high — eliminate shadows", "color_temp_k": 5600},
        "back_light": {"position": "strong colored rim from behind", "type": "hard colored LED", "intensity": "strong, exaggerated", "color_temp_k": 0},
        "mood_tags": ["anime", "stylized", "colorful", "flat", "graphic"],
        "use_cases": ["anime_content", "stylized_commercial", "gaming", "vtuber"],
        "post_processing_notes": "Push saturation, reduce micro-contrast. Cel-shading in ComfyUI possible.",
        "variants": [
            {"suffix": "bright_rimmed", "color_temperature_k": 5600, "variant_note": "flat lit with strong colored rim"},
        ],
    },
    # === Volumetric / Atmospheric ===
    {
        "setup_type": "Haze Backlight Volumetric",
        "description": "Strong backlight through atmospheric haze creates visible light shafts. God rays, volumetric beams.",
        "key_light": {"position": "strong backlight, elevated, through haze", "type": "hard source (HMI or Fresnel) through haze", "intensity": "strong, creating visible beams", "color_temp_k": 5600},
        "fill_light": {"position": "minimal front, mostly silhouette", "type": "ambient scatter from haze", "intensity": "low, haze provides ambient fill", "color_temp_k": 5600},
        "back_light": {"position": "same as key — backlight is the key in this setup", "type": "hard source through atmosphere", "intensity": "strong", "color_temp_k": 5600},
        "mood_tags": ["volumetric", "epic", "godray", "atmospheric", "divine"],
        "use_cases": ["epic_reveal", "spiritual_scene", "forest_scene", "concert_backlight"],
        "post_processing_notes": "Enhance volumetric rays in post. ComfyUI can add atmospheric effects. Push contrast.",
        "variants": [
            {"suffix": "daylight_haze", "color_temperature_k": 5600, "variant_note": "daylight through haze"},
            {"suffix": "warm_shaft", "color_temperature_k": 3200, "variant_note": "warm tungsten shafts through dust"},
        ],
    },
    {
        "setup_type": "Fog Practicals",
        "description": "Dense fog with visible practical lights creating diffused halos. Eerie, dreamlike.",
        "key_light": {"position": "practicals visible in fog", "type": "street lamps, car lights, lanterns in fog", "intensity": "medium, heavily diffused by fog", "color_temp_k": 3200},
        "fill_light": {"position": "fog provides omnidirectional scatter", "type": "fog scatter", "intensity": "ambient glow", "color_temp_k": 3200},
        "back_light": {"position": "practicals behind subject", "type": "light sources visible in fog creating halos", "intensity": "glow halos around sources", "color_temp_k": 3200},
        "mood_tags": ["eerie", "dreamlike", "mysterious", "foggy", "atmospheric"],
        "use_cases": ["horror_exterior", "dream_sequence", "thriller", "period_night"],
        "post_processing_notes": "Low contrast grade. Lift blacks. Halation effect on practicals. Desaturate slightly.",
        "variants": [
            {"suffix": "warm_fog", "color_temperature_k": 3200, "variant_note": "warm practicals in fog"},
            {"suffix": "cold_fog", "color_temperature_k": 6500, "variant_note": "cool moonlight fog"},
        ],
    },
    {
        "setup_type": "Dust Beam Shaft",
        "description": "Single shaft of light through dust particles. Visible beam cutting through darkness.",
        "key_light": {"position": "single shaft from window, ceiling hole, or doorway", "type": "hard narrow beam (Leko or shaft from opening)", "intensity": "focused, isolated beam", "color_temp_k": 5600},
        "fill_light": {"position": "near zero — darkness outside the beam", "type": "darkness with dust scatter providing minimal ambient", "intensity": "extremely low", "color_temp_k": 5600},
        "back_light": {"position": "none needed — the beam IS the light", "type": "dust particles make the beam visible", "intensity": "beam only", "color_temp_k": 5600},
        "mood_tags": ["isolated", "divine", "discovery", "decay", "atmospheric"],
        "use_cases": ["abandoned_building", "discovery_moment", "religious_space", "dust_atmosphere"],
        "post_processing_notes": "Crush everything outside the beam. Add particle effects in ComfyUI if needed.",
        "variants": [
            {"suffix": "daylight_shaft", "color_temperature_k": 5600, "variant_note": "daylight shaft through dust"},
            {"suffix": "golden_shaft", "color_temperature_k": 3500, "variant_note": "golden warm shaft, late afternoon"},
        ],
    },
    {
        "setup_type": "Window Light Natural",
        "description": "Single large soft source from window. Classic portraiture and interior photography lighting.",
        "key_light": {"position": "large window to one side of subject", "type": "natural window light (diffused or direct)", "intensity": "varies with time of day and weather", "color_temp_k": 5600},
        "fill_light": {"position": "bounce card opposite window", "type": "white reflector or room bounce", "intensity": "gentle fill to open shadows", "color_temp_k": 5600},
        "back_light": {"position": "none or second window behind", "type": "natural only", "intensity": "natural ambient", "color_temp_k": 5600},
        "mood_tags": ["natural", "soft", "portrait", "intimate", "simple"],
        "use_cases": ["portrait", "interview", "lifestyle", "real_estate_interior", "food_photography"],
        "post_processing_notes": "Minimal intervention. Natural and clean. Slight warm push for lifestyle content.",
        "variants": [
            {"suffix": "north_light", "color_temperature_k": 6500, "variant_note": "cool north-facing window, painter's light"},
            {"suffix": "direct_sun", "color_temperature_k": 5600, "variant_note": "direct sun through window, hard shadows"},
        ],
    },
    {
        "setup_type": "Studio Flags Shaped",
        "description": "Controlled studio light sculpted with flags, neg fill, and cutters. Precision-shaped light pools.",
        "key_light": {"position": "shaped by flags to hit only desired area", "type": "Fresnel with barndoors, floppy flags, cutters", "intensity": "strong but tightly controlled", "color_temp_k": 5600},
        "fill_light": {"position": "neg fill (black cards) to deepen shadows where wanted", "type": "subtractive — removing light, not adding", "intensity": "controlled absence", "color_temp_k": 0},
        "back_light": {"position": "precisely shaped rim", "type": "snooted or barndoored spot", "intensity": "accent only, shaped", "color_temp_k": 5600},
        "mood_tags": ["controlled", "precise", "editorial", "sculpted", "intentional"],
        "use_cases": ["fashion_editorial", "product_hero", "high_end_portrait", "art_direction"],
        "post_processing_notes": "Minimal post — the lighting IS the look. Don't soften what was shaped hard.",
        "variants": [
            {"suffix": "precision_shaped", "color_temperature_k": 5600, "variant_note": "precision-shaped studio lighting"},
        ],
    },
]


def generate_id(setup_type: str, suffix: str) -> str:
    key = f"{setup_type}_{suffix}"
    short_hash = hashlib.md5(key.encode()).hexdigest()[:8]
    slug = key.lower().replace(" ", "_").replace("/", "").replace("+", "")[:50]
    return f"light_{short_hash}_{slug}"


def build_prompt_fragment(setup: dict, variant: dict) -> str:
    parts = [f"{setup['setup_type']} lighting"]

    color_k = variant["color_temperature_k"]
    if color_k > 0:
        if color_k <= 2000:
            parts.append(f"candlelight warm {color_k}K")
        elif color_k <= 3500:
            parts.append(f"warm tungsten {color_k}K")
        elif color_k <= 5000:
            parts.append(f"mixed {color_k}K")
        elif color_k <= 6000:
            parts.append(f"daylight {color_k}K")
        else:
            parts.append(f"cool blue {color_k}K")

    key = setup["key_light"]
    if "position" in key and key["position"] != "none":
        parts.append(f"key light {key['position']}")

    mood = ", ".join(setup["mood_tags"][:3])
    parts.append(mood)

    if setup.get("description"):
        # Extract the first sentence as a compact descriptor
        desc_short = setup["description"].split(".")[0]
        parts.append(desc_short.lower())

    return ", ".join(parts)


def generate_all_presets() -> list:
    presets = []
    for setup in LIGHTING_SETUPS:
        for variant in setup["variants"]:
            preset_id = generate_id(setup["setup_type"], variant["suffix"])
            prompt_fragment = build_prompt_fragment(setup, variant)

            preset = {
                "id": preset_id,
                "setup_type": setup["setup_type"],
                "description": setup["description"],
                "key_light": setup["key_light"],
                "fill_light": setup["fill_light"],
                "back_light": setup["back_light"],
                "color_temperature_k": variant["color_temperature_k"],
                "variant_note": variant["variant_note"],
                "mood_tags": setup["mood_tags"],
                "prompt_fragment": prompt_fragment,
                "use_cases": setup["use_cases"],
                "post_processing_notes": setup["post_processing_notes"],
            }
            presets.append(preset)

    return presets


# ---------------------------------------------------------------------------
# Embedding + Qdrant (reused from populate_camera_presets.py)
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
        client.upsert(collection_name="lighting_presets", points=points[i : i + batch_size])
        print(f"  Upserted {min(i + batch_size, len(points))}/{len(points)}")
    info = client.get_collection("lighting_presets")
    print(f"  Collection now has {info.points_count} points")


def query_qdrant(query_text: str, qdrant_url: str, qdrant_key: str, openai_key: str, top_k: int = 5):
    from qdrant_client import QdrantClient
    embeddings = embed_texts([query_text], openai_key)
    client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
    results = client.query_points(collection_name="lighting_presets", query=embeddings[0], limit=top_k, with_payload=True)
    print(f'\nQuery: "{query_text}"')
    print(f"Top {top_k} results:\n")
    for point in results.points:
        p = point.payload
        print(f"  [{point.score:.4f}] {p['setup_type']} ({p.get('variant_note', '')})")
        print(f"           Mood: {', '.join(p['mood_tags'][:4])}")
        print(f"           Prompt: {p['prompt_fragment'][:120]}...")
        print()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="PopTech Lighting Presets RAG Tool")
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
        out_path = Path(__file__).parent / "lighting_presets.json"
        with open(out_path, "w") as f:
            json.dump(presets, f, indent=2)
        print(f"Generated {len(presets)} lighting presets -> {out_path}")
        setups = set(p["setup_type"] for p in presets)
        moods = set(m for p in presets for m in p["mood_tags"])
        print(f"  Setup types: {len(setups)}")
        print(f"  Unique mood tags: {len(moods)}")

    elif args.upload:
        if not args.openai_key:
            print("ERROR: OPENAI_API_KEY required."); sys.exit(1)
        if not args.qdrant_key:
            print("ERROR: QDRANT_API_KEY required."); sys.exit(1)
        presets_path = Path(__file__).parent / "lighting_presets.json"
        if not presets_path.exists():
            print("No presets JSON found. Run --generate first."); sys.exit(1)
        with open(presets_path) as f:
            presets = json.load(f)
        print(f"Embedding {len(presets)} prompt fragments...")
        texts = [p["prompt_fragment"] for p in presets]
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
        info = client.get_collection("lighting_presets")
        print(f"Collection: lighting_presets\nPoints: {info.points_count}\nVectors: {info.config.params.vectors.size}d\nStatus: {info.status.name}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
