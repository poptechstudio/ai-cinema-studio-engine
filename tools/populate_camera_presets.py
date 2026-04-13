"""
PopTech Cinema Studio — Camera Presets RAG Population Script
Task 2.1: Populate Qdrant camera_presets collection with 200+ entries.

Usage:
  python tools/populate_camera_presets.py --generate     # Generate presets JSON only
  python tools/populate_camera_presets.py --upload        # Embed + upload to Qdrant
  python tools/populate_camera_presets.py --query "text"  # Test semantic search
  python tools/populate_camera_presets.py --stats         # Show collection stats

Requirements:
  pip install openai qdrant-client

Environment:
  OPENAI_API_KEY      - For text-embedding-3-small embeddings
  QDRANT_URL          - Default: http://localhost:16333 (SSH tunnel)
  QDRANT_API_KEY      - Qdrant auth key
"""

import json
import os
import sys
import hashlib
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Camera body definitions
# ---------------------------------------------------------------------------
CAMERA_BODIES = {
    "ARRI Alexa 35": {
        "traits": "15+ stops dynamic range, natural highlight rolloff, organic color science, fine grain at high ISO, ARRI LogC4",
        "cinema_studio_mapping": "Full-Frame Cine Digital",
        "format": "full-frame",
    },
    "ARRI Alexa Mini LF": {
        "traits": "large format sensor, shallow native DoF, cinematic image quality, compact cinema body, ARRI color science",
        "cinema_studio_mapping": "Full-Frame Cine Digital",
        "format": "large-format",
    },
    "RED V-Raptor": {
        "traits": "8K resolution, clinical sharpness, high detail retention, REDWideGamutRGB2 color space, modular design",
        "cinema_studio_mapping": "Modular 8K Digital",
        "format": "full-frame",
    },
    "Panavision DXL2": {
        "traits": "large format 8K RED sensor, Panavision color science, grand cinematic scale, epic 70mm-equivalent depth",
        "cinema_studio_mapping": "Grand Format 70mm Film",
        "format": "large-format",
    },
    "Panavision Millennium XL2": {
        "traits": "35mm film gate, classic film motion cadence, organic grain structure, traditional cinema texture",
        "cinema_studio_mapping": "Grand Format 70mm Film",
        "format": "35mm",
    },
    "Sony VENICE 2": {
        "traits": "dual base ISO (800/3200), excellent low-light, versatile S35/full-frame, X-OCN codec, natural skin tones",
        "cinema_studio_mapping": "Studio Digital S35",
        "format": "full-frame",
    },
    "Blackmagic URSA Mini Pro 12K": {
        "traits": "12K sensor, Blackmagic color science, BRAW codec, high resolution for reframing, accessible cinema camera",
        "cinema_studio_mapping": "Premium Large Format Digital",
        "format": "super-35",
    },
    "Bolex H16": {
        "traits": "16mm film gate, vintage mechanical texture, documentary grain, handheld ergonomics, wind-up motor character",
        "cinema_studio_mapping": "Classic 16mm Film",
        "format": "16mm",
    },
}

# ---------------------------------------------------------------------------
# Lens definitions
# ---------------------------------------------------------------------------
LENSES = {
    "Cooke S7i": {
        "traits": "warm color rendering, smooth focus falloff, gentle barrel distortion, subtle flare character, the 'Cooke Look'",
        "cinema_studio_mapping": "Warm Cinema Prime",
        "type": "spherical_prime",
    },
    "Cooke Anamorphic /i": {
        "traits": "2x anamorphic squeeze, oval bokeh, horizontal blue streak flares, wide aspect ratio, cinematic distortion",
        "cinema_studio_mapping": "Classic Anamorphic",
        "type": "anamorphic",
    },
    "Laowa Probe": {
        "traits": "extreme macro, bug-eye close-up perspective, waterproof tip, deep focus at close range, unusual POV",
        "cinema_studio_mapping": "Extreme Macro",
        "type": "specialty",
    },
    "Zeiss Super Speed": {
        "traits": "1970s cinema prime character, warm vintage rendering, T1.3 maximum aperture, classic period look",
        "cinema_studio_mapping": "70s Cinema Prime",
        "type": "spherical_prime",
    },
    "Atlas Orion Anamorphic": {
        "traits": "modern compact anamorphic, controlled blue/amber streak flares, oval bokeh, sharp center with gentle edges",
        "cinema_studio_mapping": "Compact Anamorphic",
        "type": "anamorphic",
    },
    "Zeiss Supreme Prime": {
        "traits": "clinical sharpness corner-to-corner, neutral color rendering, minimal distortion, modern precision",
        "cinema_studio_mapping": "Premium Modern Prime",
        "type": "spherical_prime",
    },
    "Cooke Speed Panchro": {
        "traits": "golden-age Hollywood character, vintage warmth, gentle softness, classic portraiture rendering",
        "cinema_studio_mapping": "Vintage Prime",
        "type": "spherical_prime",
    },
    "Helios 44-2": {
        "traits": "distinctive swirly bokeh, Soviet vintage character, warm color cast, dreamy out-of-focus rendering",
        "cinema_studio_mapping": "Swirl Bokeh Portrait",
        "type": "spherical_prime",
    },
    "Canon K35": {
        "traits": "warm halation around highlights, dreamy diffusion, vintage 70s/80s look, gentle contrast rolloff",
        "cinema_studio_mapping": "Halation Diffusion",
        "type": "spherical_prime",
    },
    "Tiffen Pro-Mist + Zeiss": {
        "traits": "diffused highlight glow, reduced contrast, soft blooming around light sources, ethereal quality",
        "cinema_studio_mapping": "Creative Tilt",
        "type": "filtered_prime",
    },
    "Zeiss Otus": {
        "traits": "maximum clinical sharpness, zero optical character, forensic detail, reference-grade rendering",
        "cinema_studio_mapping": "Clinical Sharp Prime",
        "type": "spherical_prime",
    },
}

# ---------------------------------------------------------------------------
# Focal lengths
# ---------------------------------------------------------------------------
FOCAL_LENGTHS = {
    8: {
        "traits": "ultra-wide, extreme distortion, immersive POV, environmental storytelling, fish-eye effect",
        "cinema_studio_mapping": "8mm (Ultra-Wide)",
        "category": "ultra_wide",
    },
    14: {
        "traits": "ultra-wide, dramatic perspective, architectural scale, environmental context, slight barrel distortion",
        "cinema_studio_mapping": "14mm (Ultra-Wide)",
        "category": "ultra_wide",
    },
    24: {
        "traits": "wide establishing, environmental context with subject, natural wide perspective, minimal distortion",
        "cinema_studio_mapping": "24mm (Wide)",
        "category": "wide",
    },
    35: {
        "traits": "natural field of view, journalistic perspective, environmental portrait, documentary standard",
        "cinema_studio_mapping": "35mm (Standard Wide)",
        "category": "standard",
    },
    50: {
        "traits": "classic normal perspective, minimal distortion, natural eye-level view, portrait standard",
        "cinema_studio_mapping": "50mm (Portrait)",
        "category": "standard",
    },
    85: {
        "traits": "tight portrait, flattering compression, subject isolation, shallow DoF emphasis, intimate framing",
        "cinema_studio_mapping": "85mm (Tight Portrait)",
        "category": "telephoto",
    },
}

# ---------------------------------------------------------------------------
# Apertures
# ---------------------------------------------------------------------------
APERTURES = {
    "f/1.4": {
        "traits": "extreme shallow depth of field, creamy bokeh, strong subject isolation, low-light capable",
        "cinema_studio_mapping": "f/1.4 Shallow DoF",
    },
    "f/4": {
        "traits": "moderate depth of field, balanced sharpness, environmental context visible, versatile",
        "cinema_studio_mapping": "f/4 Balanced",
    },
    "f/11": {
        "traits": "deep focus, everything sharp front to back, landscape/architectural, Gregg Toland style",
        "cinema_studio_mapping": "f/11 Deep Focus",
    },
}

# ---------------------------------------------------------------------------
# Camera movements
# ---------------------------------------------------------------------------
MOVEMENTS = {
    "static": {
        "traits": "locked-off tripod, deliberate stillness, compositional emphasis, tableau framing",
        "speed": None,
    },
    "dolly_in_slow": {
        "traits": "gradual forward movement, builds intimacy, draws viewer into subject, 2-3 sec duration",
        "speed": "slow",
    },
    "dolly_out_slow": {
        "traits": "gradual pull-back, reveals context, creates distance or isolation, 2-3 sec duration",
        "speed": "slow",
    },
    "dolly_in_fast": {
        "traits": "rapid push-in, dramatic emphasis, sudden focus on detail, impact moment",
        "speed": "fast",
    },
    "pan_left": {
        "traits": "horizontal sweep left, follows action, reveals environment, smooth lateral scan",
        "speed": "medium",
    },
    "pan_right": {
        "traits": "horizontal sweep right, follows action, reveals environment, smooth lateral scan",
        "speed": "medium",
    },
    "tilt_up": {
        "traits": "vertical reveal upward, establishes scale, reveals height, dramatic unveiling",
        "speed": "medium",
    },
    "tilt_down": {
        "traits": "vertical descent, grounds the viewer, reveals detail from overview, investigative",
        "speed": "medium",
    },
    "crane_up": {
        "traits": "rising overhead, epic scale reveal, emotional lift, scene transition, bird's-eye approach",
        "speed": "slow",
    },
    "crane_down": {
        "traits": "descending from height, arrival, grounding, intimate approach from distance",
        "speed": "slow",
    },
    "steadicam_follow": {
        "traits": "smooth gliding follow shot, walking pace, continuous take, immersive POV, Kubrick-style",
        "speed": "medium",
    },
    "handheld_subtle": {
        "traits": "organic micro-movements, documentary feel, present-tense tension, verite realism",
        "speed": "subtle",
    },
    "handheld_aggressive": {
        "traits": "shaky urgent movement, chaos energy, war/action intensity, Greengrass-style",
        "speed": "aggressive",
    },
    "tracking_lateral": {
        "traits": "sideways dolly alongside subject, parallel movement, profile perspective, reveals depth",
        "speed": "medium",
    },
    "zoom_in_slow": {
        "traits": "gradual focal length increase, Hitchcock-style creep, psychological tension, no physical movement",
        "speed": "slow",
    },
    "rack_focus": {
        "traits": "shift focus plane from foreground to background or vice versa, reveals relationship, dramatic emphasis",
        "speed": "medium",
    },
    "dolly_zoom": {
        "traits": "simultaneous dolly + counter-zoom, vertigo effect, Spielberg/Hitchcock, disorientation",
        "speed": "medium",
    },
    "orbit_slow": {
        "traits": "circular movement around subject, 180-360 degree arc, reveals all angles, product hero shot",
        "speed": "slow",
    },
    "whip_pan": {
        "traits": "extremely fast horizontal pan, motion blur transition, scene-to-scene cut alternative, energetic",
        "speed": "fast",
    },
    "push_pull_breathing": {
        "traits": "subtle in-out oscillation, breathing rhythm, hypnotic, dreamlike, Wong Kar-wai style",
        "speed": "slow",
    },
}

# ---------------------------------------------------------------------------
# Compatibility rules — which combos make sense
# ---------------------------------------------------------------------------
def is_valid_combo(body: str, lens: str, focal: int, aperture: str, movement: str) -> bool:
    lens_data = LENSES[lens]

    # Laowa Probe is specialty — only works at macro distances, specific combos
    if lens == "Laowa Probe":
        if focal not in (24, 35):
            return False
        if aperture != "f/11":
            return False
        if movement not in ("static", "dolly_in_slow", "dolly_out_slow"):
            return False

    # Anamorphic lenses don't come in ultra-wide or extreme telephoto
    if lens_data["type"] == "anamorphic" and focal in (8,):
        return False

    # 8mm ultra-wide doesn't pair well with telephoto-oriented lenses
    if focal == 8 and lens in ("Zeiss Otus", "Helios 44-2"):
        return False

    # f/1.4 not available on all lenses
    if aperture == "f/1.4" and lens in ("Laowa Probe", "Tiffen Pro-Mist + Zeiss"):
        return False

    # Bolex H16 (16mm) doesn't pair with large-format lenses
    if body == "Bolex H16" and lens in ("Cooke Anamorphic /i", "Zeiss Supreme Prime", "Zeiss Otus"):
        return False

    # Dolly zoom is a specific technique — only with standard/telephoto
    if movement == "dolly_zoom" and focal in (8, 14):
        return False

    # Whip pan mainly with wider lenses
    if movement == "whip_pan" and focal > 50:
        return False

    return True


def generate_id(body: str, lens: str, focal: int, aperture: str, movement: str) -> str:
    """Deterministic ID from combo — ensures idempotent upserts."""
    key = f"{body}_{lens}_{focal}_{aperture}_{movement}"
    short_hash = hashlib.md5(key.encode()).hexdigest()[:8]
    slug = key.lower().replace(" ", "_").replace("/", "").replace("+", "")[:60]
    return f"cam_{short_hash}_{slug}"


def build_prompt_fragment(body: str, lens: str, focal: int, aperture: str, movement: str) -> str:
    body_data = CAMERA_BODIES[body]
    lens_data = LENSES[lens]
    focal_data = FOCAL_LENGTHS[focal]
    apt_data = APERTURES[aperture]
    mov_data = MOVEMENTS[movement]

    parts = [f"shot on {body} with {lens} {focal}mm at {aperture}"]

    # Movement
    if movement != "static":
        mov_desc = movement.replace("_", " ")
        parts.append(mov_desc)

    # Key visual traits (pick the most distinctive)
    traits = []
    if "shallow" in apt_data["traits"]:
        traits.append("shallow depth of field")
    elif "deep focus" in apt_data["traits"]:
        traits.append("deep focus, everything sharp")

    if "grain" in body_data["traits"]:
        traits.append("fine film grain")
    if "8K" in body_data["traits"] or "12K" in body_data["traits"]:
        traits.append("ultra-sharp detail")
    if "16mm" in body_data["traits"]:
        traits.append("16mm film grain texture")

    if "warm" in lens_data["traits"]:
        traits.append("warm color rendering")
    if "anamorphic" in lens_data["traits"]:
        traits.append("anamorphic oval bokeh, horizontal lens flare")
    if "swirly" in lens_data["traits"]:
        traits.append("swirly bokeh")
    if "halation" in lens_data["traits"]:
        traits.append("warm highlight halation")
    if "diffused" in lens_data["traits"]:
        traits.append("soft diffused highlights")
    if "clinical" in lens_data["traits"]:
        traits.append("clinical sharpness")

    if traits:
        parts.append(", ".join(traits))

    return ", ".join(parts)


def build_use_cases(body: str, lens: str, focal: int, aperture: str, movement: str) -> list:
    cases = []
    focal_data = FOCAL_LENGTHS[focal]

    if focal <= 14:
        cases.extend(["establishing_shot", "environment", "architecture"])
    elif focal <= 35:
        cases.extend(["scene_setting", "group_shot", "documentary"])
    elif focal <= 50:
        cases.extend(["portrait", "dialogue", "interview"])
    else:
        cases.extend(["close_up", "portrait", "emotional_moment"])

    if aperture == "f/1.4":
        cases.append("subject_isolation")
        cases.append("bokeh_aesthetic")
    if aperture == "f/11":
        cases.append("landscape")
        cases.append("architectural")

    if "dolly_in" in movement:
        cases.append("product_reveal")
    if "crane" in movement:
        cases.append("epic_reveal")
    if "handheld" in movement:
        cases.append("verite")
        cases.append("tension")
    if "orbit" in movement:
        cases.append("hero_shot")
        cases.append("product_showcase")
    if movement == "rack_focus":
        cases.append("narrative_shift")
    if movement == "dolly_zoom":
        cases.append("psychological_tension")

    if "16mm" in CAMERA_BODIES[body].get("traits", ""):
        cases.append("vintage")
        cases.append("archival")

    if LENSES[lens]["type"] == "anamorphic":
        cases.append("cinematic_widescreen")

    return list(dict.fromkeys(cases))[:8]  # dedupe, max 8


def generate_all_presets() -> list:
    """Generate a curated set of 200+ presets with good coverage, not every permutation."""
    presets = []
    seen_ids = set()

    # Strategy: For each body, pick its 2-3 best lens pairings, 2-3 key focal lengths,
    # the most natural aperture, and 3-4 signature movements. This gives us ~200-300
    # curated presets instead of 24K permutations.

    # Define the best lens pairings per body
    BODY_LENS_PAIRINGS = {
        "ARRI Alexa 35": ["Cooke S7i", "Cooke Anamorphic /i", "Zeiss Supreme Prime", "Canon K35"],
        "ARRI Alexa Mini LF": ["Cooke S7i", "Atlas Orion Anamorphic", "Zeiss Supreme Prime"],
        "RED V-Raptor": ["Zeiss Supreme Prime", "Zeiss Otus", "Atlas Orion Anamorphic"],
        "Panavision DXL2": ["Cooke Anamorphic /i", "Cooke S7i", "Cooke Speed Panchro"],
        "Panavision Millennium XL2": ["Cooke Speed Panchro", "Zeiss Super Speed", "Canon K35"],
        "Sony VENICE 2": ["Cooke S7i", "Zeiss Supreme Prime", "Atlas Orion Anamorphic", "Tiffen Pro-Mist + Zeiss"],
        "Blackmagic URSA Mini Pro 12K": ["Zeiss Supreme Prime", "Cooke S7i", "Zeiss Otus"],
        "Bolex H16": ["Zeiss Super Speed", "Helios 44-2", "Canon K35", "Cooke Speed Panchro"],
    }

    # Key focal lengths per lens type
    LENS_FOCALS = {
        "Cooke S7i": [35, 50, 85],
        "Cooke Anamorphic /i": [24, 35, 50],
        "Laowa Probe": [24],
        "Zeiss Super Speed": [24, 35, 50],
        "Atlas Orion Anamorphic": [35, 50, 85],
        "Zeiss Supreme Prime": [24, 50, 85],
        "Cooke Speed Panchro": [35, 50],
        "Helios 44-2": [50, 85],
        "Canon K35": [24, 35, 50],
        "Tiffen Pro-Mist + Zeiss": [35, 50, 85],
        "Zeiss Otus": [50, 85],
    }

    # Best aperture per use case
    FOCAL_APERTURES = {
        8: ["f/4", "f/11"],
        14: ["f/4", "f/11"],
        24: ["f/1.4", "f/4"],
        35: ["f/1.4", "f/4"],
        50: ["f/1.4", "f/4"],
        85: ["f/1.4", "f/4"],
    }

    # Signature movements (most commonly used)
    CORE_MOVEMENTS = [
        "static", "dolly_in_slow", "dolly_out_slow", "pan_right",
        "crane_up", "steadicam_follow", "handheld_subtle", "tracking_lateral",
        "rack_focus", "orbit_slow",
    ]

    # Phase 1: Core curated combos (~200)
    for body, lens_list in BODY_LENS_PAIRINGS.items():
        body_data = CAMERA_BODIES[body]
        for lens in lens_list:
            lens_data = LENSES[lens]
            focals = LENS_FOCALS.get(lens, [35, 50])
            for focal in focals:
                focal_data = FOCAL_LENGTHS[focal]
                apertures = FOCAL_APERTURES.get(focal, ["f/4"])
                for aperture in apertures:
                    apt_data = APERTURES[aperture]
                    for movement in CORE_MOVEMENTS:
                        if not is_valid_combo(body, lens, focal, aperture, movement):
                            continue
                        pid = generate_id(body, lens, focal, aperture, movement)
                        if pid in seen_ids:
                            continue
                        seen_ids.add(pid)

                        preset = {
                            "id": pid,
                            "camera_body": body,
                            "camera_body_traits": body_data["traits"],
                            "lens_type": lens,
                            "lens_traits": lens_data["traits"],
                            "focal_length_mm": focal,
                            "focal_traits": focal_data["traits"],
                            "aperture": aperture,
                            "aperture_traits": apt_data["traits"],
                            "movement": movement,
                            "movement_traits": MOVEMENTS[movement]["traits"],
                            "prompt_fragment": build_prompt_fragment(body, lens, focal, aperture, movement),
                            "use_cases": build_use_cases(body, lens, focal, aperture, movement),
                            "cinema_studio_mapping": {
                                "body": body_data["cinema_studio_mapping"],
                                "lens": lens_data["cinema_studio_mapping"],
                                "focal": focal_data["cinema_studio_mapping"],
                                "aperture": apt_data["cinema_studio_mapping"],
                            },
                        }
                        presets.append(preset)

    # Phase 2: Add specialty combos for coverage gaps
    SPECIALTY_COMBOS = [
        # Ultra-wide establishing shots
        ("ARRI Alexa 35", "Cooke S7i", 14, "f/4", "crane_up"),
        ("RED V-Raptor", "Zeiss Supreme Prime", 14, "f/11", "static"),
        ("Sony VENICE 2", "Cooke S7i", 14, "f/4", "pan_right"),
        # Extreme macro
        ("ARRI Alexa 35", "Laowa Probe", 24, "f/11", "dolly_in_slow"),
        ("Sony VENICE 2", "Laowa Probe", 24, "f/11", "static"),
        # Dramatic compound movements
        ("ARRI Alexa 35", "Cooke S7i", 50, "f/1.4", "dolly_zoom"),
        ("Panavision DXL2", "Cooke Anamorphic /i", 35, "f/4", "whip_pan"),
        ("ARRI Alexa 35", "Canon K35", 35, "f/1.4", "push_pull_breathing"),
        # Aggressive handheld
        ("Bolex H16", "Zeiss Super Speed", 24, "f/1.4", "handheld_aggressive"),
        ("Sony VENICE 2", "Zeiss Supreme Prime", 35, "f/4", "handheld_aggressive"),
        # Fast dolly
        ("RED V-Raptor", "Zeiss Otus", 85, "f/1.4", "dolly_in_fast"),
        ("ARRI Alexa 35", "Cooke S7i", 50, "f/1.4", "dolly_in_fast"),
        # Zoom
        ("Sony VENICE 2", "Cooke S7i", 50, "f/4", "zoom_in_slow"),
        ("Panavision Millennium XL2", "Zeiss Super Speed", 35, "f/1.4", "zoom_in_slow"),
        # Deep focus 8mm
        ("ARRI Alexa 35", "Cooke S7i", 8, "f/11", "static"),
        ("Blackmagic URSA Mini Pro 12K", "Zeiss Supreme Prime", 8, "f/11", "pan_right"),
    ]

    for body, lens, focal, aperture, movement in SPECIALTY_COMBOS:
        if not is_valid_combo(body, lens, focal, aperture, movement):
            continue
        pid = generate_id(body, lens, focal, aperture, movement)
        if pid in seen_ids:
            continue
        seen_ids.add(pid)

        body_data = CAMERA_BODIES[body]
        lens_data = LENSES[lens]
        focal_data = FOCAL_LENGTHS[focal]
        apt_data = APERTURES[aperture]

        preset = {
            "id": pid,
            "camera_body": body,
            "camera_body_traits": body_data["traits"],
            "lens_type": lens,
            "lens_traits": lens_data["traits"],
            "focal_length_mm": focal,
            "focal_traits": focal_data["traits"],
            "aperture": aperture,
            "aperture_traits": apt_data["traits"],
            "movement": movement,
            "movement_traits": MOVEMENTS[movement]["traits"],
            "prompt_fragment": build_prompt_fragment(body, lens, focal, aperture, movement),
            "use_cases": build_use_cases(body, lens, focal, aperture, movement),
            "cinema_studio_mapping": {
                "body": body_data["cinema_studio_mapping"],
                "lens": lens_data["cinema_studio_mapping"],
                "focal": focal_data["cinema_studio_mapping"],
                "aperture": apt_data["cinema_studio_mapping"],
            },
        }
        presets.append(preset)

    return presets


# ---------------------------------------------------------------------------
# Embedding + Qdrant upload
# ---------------------------------------------------------------------------
def embed_texts(texts: list[str], api_key: str) -> list[list[float]]:
    """Batch embed texts via OpenAI text-embedding-3-small."""
    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    all_embeddings = []
    batch_size = 100  # OpenAI allows up to 2048 per call
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(
            input=batch,
            model="text-embedding-3-small",
        )
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)
        print(f"  Embedded {min(i + batch_size, len(texts))}/{len(texts)}")

    return all_embeddings


def upload_to_qdrant(presets: list, embeddings: list[list[float]], qdrant_url: str, qdrant_key: str):
    """Batch upsert presets + embeddings into Qdrant camera_presets collection."""
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct

    client = QdrantClient(url=qdrant_url, api_key=qdrant_key)

    points = []
    for i, (preset, embedding) in enumerate(zip(presets, embeddings)):
        point = PointStruct(
            id=i + 1,  # Qdrant needs integer or UUID
            vector=embedding,
            payload=preset,
        )
        points.append(point)

    # Batch upsert (100 at a time)
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        client.upsert(collection_name="camera_presets", points=batch)
        print(f"  Upserted {min(i + batch_size, len(points))}/{len(points)}")

    info = client.get_collection("camera_presets")
    print(f"  Collection now has {info.points_count} points")


def query_qdrant(query_text: str, qdrant_url: str, qdrant_key: str, openai_key: str, top_k: int = 5):
    """Semantic search against camera_presets."""
    from qdrant_client import QdrantClient

    # Embed the query
    embeddings = embed_texts([query_text], openai_key)
    query_vector = embeddings[0]

    client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
    results = client.query_points(
        collection_name="camera_presets",
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )

    print(f"\nQuery: \"{query_text}\"")
    print(f"Top {top_k} results:\n")
    for point in results.points:
        p = point.payload
        print(f"  [{point.score:.4f}] {p['camera_body']} + {p['lens_type']} {p['focal_length_mm']}mm {p['aperture']} | {p['movement']}")
        print(f"           Prompt: {p['prompt_fragment'][:100]}...")
        print(f"           Uses:   {', '.join(p['use_cases'][:5])}")
        print()


def show_stats(qdrant_url: str, qdrant_key: str):
    from qdrant_client import QdrantClient
    client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
    info = client.get_collection("camera_presets")
    print(f"Collection: camera_presets")
    print(f"Points: {info.points_count}")
    print(f"Vectors: {info.config.params.vectors.size}d, {info.config.params.vectors.distance.name}")
    print(f"Status: {info.status.name}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    import argparse
    parser = argparse.ArgumentParser(description="PopTech Camera Presets RAG Tool")
    parser.add_argument("--generate", action="store_true", help="Generate presets JSON to tools/camera_presets.json")
    parser.add_argument("--upload", action="store_true", help="Embed + upload presets to Qdrant")
    parser.add_argument("--query", type=str, help="Semantic search query")
    parser.add_argument("--stats", action="store_true", help="Show Qdrant collection stats")
    parser.add_argument("--qdrant-url", default=os.environ.get("QDRANT_URL", "http://localhost:16333"))
    parser.add_argument("--qdrant-key", default=os.environ.get("QDRANT_API_KEY", ""))
    parser.add_argument("--openai-key", default=os.environ.get("OPENAI_API_KEY", ""))
    args = parser.parse_args()

    if args.generate:
        presets = generate_all_presets()
        out_path = Path(__file__).parent / "camera_presets.json"
        with open(out_path, "w") as f:
            json.dump(presets, f, indent=2)
        print(f"Generated {len(presets)} camera presets -> {out_path}")

        # Print coverage stats
        bodies = set(p["camera_body"] for p in presets)
        lenses = set(p["lens_type"] for p in presets)
        focals = set(p["focal_length_mm"] for p in presets)
        movements = set(p["movement"] for p in presets)
        print(f"  Bodies:    {len(bodies)} ({', '.join(sorted(bodies)[:4])}...)")
        print(f"  Lenses:    {len(lenses)}")
        print(f"  Focals:    {sorted(focals)}mm")
        print(f"  Movements: {len(movements)}")

    elif args.upload:
        if not args.openai_key:
            print("ERROR: OPENAI_API_KEY required for embedding. Set env var or --openai-key.")
            sys.exit(1)
        if not args.qdrant_key:
            print("ERROR: QDRANT_API_KEY required. Set env var or --qdrant-key.")
            sys.exit(1)

        # Load presets
        presets_path = Path(__file__).parent / "camera_presets.json"
        if not presets_path.exists():
            print("No presets JSON found. Run --generate first.")
            sys.exit(1)

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
            print("ERROR: Both OPENAI_API_KEY and QDRANT_API_KEY required for query.")
            sys.exit(1)
        query_qdrant(args.query, args.qdrant_url, args.qdrant_key, args.openai_key)

    elif args.stats:
        if not args.qdrant_key:
            print("ERROR: QDRANT_API_KEY required.")
            sys.exit(1)
        show_stats(args.qdrant_url, args.qdrant_key)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
