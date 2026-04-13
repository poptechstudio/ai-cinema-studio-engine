"""
PopTech Cinema Studio — LUT Generator
Generates .cube 3D LUT files for film stock emulations and creative grades.

Each LUT is a 17x17x17 3D lookup table in .cube format.
Film stock emulations approximate the color science of real film stocks
using tone curves, color channel shifts, and saturation adjustments.
"""

import math
import os
from pathlib import Path


LUT_SIZE = 17  # 17x17x17 = 4913 entries — good balance of accuracy vs file size


def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def apply_curve(x, shadows=0.0, midtones=0.0, highlights=0.0, gamma=1.0, lift=0.0, gain=1.0):
    """Apply a tonal curve to a single channel value (0-1)."""
    # Lift/gain
    x = lift + x * gain
    # Gamma
    x = clamp(x)
    x = pow(x, 1.0 / gamma) if gamma > 0 else x
    # S-curve influenced by shadows/midtones/highlights
    if shadows != 0 or midtones != 0 or highlights != 0:
        shadow_effect = shadows * (1.0 - x) * (1.0 - x)
        mid_effect = midtones * 4.0 * x * (1.0 - x)
        high_effect = highlights * x * x
        x = clamp(x + shadow_effect + mid_effect + high_effect)
    return clamp(x)


def apply_saturation(r, g, b, sat):
    """Adjust saturation. sat=1.0 is neutral, <1 desaturates, >1 saturates."""
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
    r = clamp(luma + (r - luma) * sat)
    g = clamp(luma + (g - luma) * sat)
    b = clamp(luma + (b - luma) * sat)
    return r, g, b


def apply_color_temp_shift(r, g, b, temp_shift):
    """Shift color temperature. Positive = warm, negative = cool."""
    r = clamp(r + temp_shift * 0.05)
    b = clamp(b - temp_shift * 0.05)
    g = clamp(g + temp_shift * 0.01)  # slight green shift for warmth
    return r, g, b


def apply_cross_channel(r, g, b, r_to_g=0, r_to_b=0, g_to_r=0, g_to_b=0, b_to_r=0, b_to_g=0):
    """Cross-channel color contamination for film look."""
    nr = clamp(r + g * g_to_r + b * b_to_r)
    ng = clamp(g + r * r_to_g + b * b_to_g)
    nb = clamp(b + r * r_to_b + g * g_to_b)
    return nr, ng, nb


def write_cube(filepath, lut_data, title=""):
    """Write a .cube LUT file."""
    with open(filepath, "w") as f:
        if title:
            f.write(f"TITLE \"{title}\"\n")
        f.write(f"LUT_3D_SIZE {LUT_SIZE}\n")
        f.write(f"DOMAIN_MIN 0.0 0.0 0.0\n")
        f.write(f"DOMAIN_MAX 1.0 1.0 1.0\n\n")
        for entry in lut_data:
            f.write(f"{entry[0]:.6f} {entry[1]:.6f} {entry[2]:.6f}\n")


def generate_lut(transform_fn, title=""):
    """Generate a 3D LUT by applying transform_fn to every RGB combination."""
    data = []
    for bi in range(LUT_SIZE):
        for gi in range(LUT_SIZE):
            for ri in range(LUT_SIZE):
                r = ri / (LUT_SIZE - 1)
                g = gi / (LUT_SIZE - 1)
                b = bi / (LUT_SIZE - 1)
                nr, ng, nb = transform_fn(r, g, b)
                data.append((clamp(nr), clamp(ng), clamp(nb)))
    return data


# ---------------------------------------------------------------------------
# Film Stock Emulation Transforms
# ---------------------------------------------------------------------------

def kodak_vision3_500t(r, g, b):
    """Tungsten cinema negative. Warm highlights, rich shadows, organic feel."""
    r, g, b = apply_color_temp_shift(r, g, b, 1.5)  # warm
    r = apply_curve(r, shadows=0.02, midtones=0.01, highlights=-0.02, gamma=1.05, lift=0.01)
    g = apply_curve(g, shadows=0.01, midtones=0.005, highlights=-0.01, gamma=1.0)
    b = apply_curve(b, shadows=-0.01, midtones=-0.005, highlights=0.01, gamma=0.97)
    r, g, b = apply_saturation(r, g, b, 0.92)
    r, g, b = apply_cross_channel(r, g, b, r_to_g=0.02, b_to_r=0.01)
    return r, g, b


def kodak_vision3_250d(r, g, b):
    """Daylight cinema negative. Vibrant, moderate grain, outdoor stock."""
    r = apply_curve(r, shadows=0.01, midtones=0.02, highlights=-0.01, gamma=1.02)
    g = apply_curve(g, shadows=0.01, midtones=0.02, highlights=0.0, gamma=1.03)
    b = apply_curve(b, shadows=0.0, midtones=0.01, highlights=0.01, gamma=1.0)
    r, g, b = apply_saturation(r, g, b, 1.08)
    return r, g, b


def fuji_eterna_vivid(r, g, b):
    """Punchy color, strong saturation, vivid greens and blues."""
    r = apply_curve(r, shadows=0.01, midtones=0.01, highlights=-0.02, gamma=1.02)
    g = apply_curve(g, shadows=0.02, midtones=0.03, highlights=0.0, gamma=1.05)
    b = apply_curve(b, shadows=0.01, midtones=0.02, highlights=0.01, gamma=1.03)
    r, g, b = apply_saturation(r, g, b, 1.15)
    return r, g, b


def fuji_eterna_250d(r, g, b):
    """Neutral daylight. Natural skin tones, moderate saturation."""
    r = apply_curve(r, shadows=0.005, midtones=0.005, gamma=1.01)
    g = apply_curve(g, shadows=0.005, midtones=0.005, gamma=1.01)
    b = apply_curve(b, shadows=0.005, midtones=0.005, gamma=1.0)
    r, g, b = apply_saturation(r, g, b, 0.95)
    return r, g, b


def kodak_ektachrome(r, g, b):
    """Reversal film. Saturated, punchy, direct positive."""
    r = apply_curve(r, shadows=-0.02, midtones=0.03, highlights=-0.02, gamma=1.08, gain=1.05)
    g = apply_curve(g, shadows=-0.02, midtones=0.02, highlights=-0.01, gamma=1.05, gain=1.03)
    b = apply_curve(b, shadows=-0.01, midtones=0.02, highlights=0.0, gamma=1.03, gain=1.02)
    r, g, b = apply_saturation(r, g, b, 1.25)
    return r, g, b


def kodak_trix_bw(r, g, b):
    """Classic B&W. High contrast, visible grain character."""
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
    luma = apply_curve(luma, shadows=-0.03, midtones=0.02, highlights=-0.02, gamma=1.1, gain=1.05)
    return luma, luma, luma


def ilford_hp5_bw(r, g, b):
    """Fine-grain B&W. Smoother tonal range."""
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
    luma = apply_curve(luma, shadows=0.01, midtones=0.01, highlights=-0.01, gamma=1.05)
    return luma, luma, luma


def kodak_doublex_bw(r, g, b):
    """Cinema B&W. Noir standard. Deep blacks, crisp whites."""
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
    luma = apply_curve(luma, shadows=-0.05, midtones=0.03, highlights=-0.03, gamma=1.15, gain=1.08)
    return luma, luma, luma


def sixteenmm_reversal(r, g, b):
    """16mm reversal. Warm, faded, heavy grain look."""
    r, g, b = apply_color_temp_shift(r, g, b, 2.0)
    r = apply_curve(r, shadows=0.04, highlights=-0.04, gamma=0.95, lift=0.03)
    g = apply_curve(g, shadows=0.03, highlights=-0.03, gamma=0.93, lift=0.02)
    b = apply_curve(b, shadows=0.02, highlights=-0.02, gamma=0.90, lift=0.01)
    r, g, b = apply_saturation(r, g, b, 0.75)
    return r, g, b


def super_8mm(r, g, b):
    """Super 8mm. Extreme warmth, faded, low contrast."""
    r, g, b = apply_color_temp_shift(r, g, b, 3.0)
    r = apply_curve(r, shadows=0.06, highlights=-0.06, gamma=0.90, lift=0.05)
    g = apply_curve(g, shadows=0.05, highlights=-0.05, gamma=0.88, lift=0.04)
    b = apply_curve(b, shadows=0.03, highlights=-0.04, gamma=0.85, lift=0.02)
    r, g, b = apply_saturation(r, g, b, 0.65)
    return r, g, b


# ---------------------------------------------------------------------------
# Creative Grade Transforms
# ---------------------------------------------------------------------------

def bleach_bypass(r, g, b):
    """Desaturated, high contrast. Silver retention process."""
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
    # Blend original with B&W for partial desaturation
    mix = 0.5
    r = r * (1 - mix) + luma * mix
    g = g * (1 - mix) + luma * mix
    b = b * (1 - mix) + luma * mix
    # Increase contrast
    r = apply_curve(r, shadows=-0.04, highlights=-0.02, gamma=1.15, gain=1.1)
    g = apply_curve(g, shadows=-0.04, highlights=-0.02, gamma=1.15, gain=1.1)
    b = apply_curve(b, shadows=-0.04, highlights=-0.02, gamma=1.15, gain=1.1)
    return r, g, b


def cross_process(r, g, b):
    """Cross-processing. Extreme color shifts."""
    r = apply_curve(r, shadows=0.03, midtones=0.05, highlights=-0.02, gamma=1.1, gain=1.1)
    g = apply_curve(g, shadows=-0.02, midtones=0.02, highlights=0.03, gamma=0.95)
    b = apply_curve(b, shadows=0.05, midtones=-0.03, highlights=-0.05, gamma=0.9)
    r, g, b = apply_saturation(r, g, b, 1.3)
    return r, g, b


def faded_film(r, g, b):
    """Lifted blacks, desaturated. Aged film stock."""
    r = apply_curve(r, shadows=0.03, highlights=-0.03, gamma=0.95, lift=0.05)
    g = apply_curve(g, shadows=0.03, highlights=-0.03, gamma=0.93, lift=0.04)
    b = apply_curve(b, shadows=0.02, highlights=-0.02, gamma=0.92, lift=0.03)
    r, g, b = apply_saturation(r, g, b, 0.7)
    return r, g, b


def teal_orange(r, g, b):
    """Hollywood blockbuster complementary grade."""
    r = apply_curve(r, shadows=-0.02, midtones=0.03, highlights=0.02, gamma=1.05)
    g = apply_curve(g, shadows=0.02, midtones=-0.01, highlights=-0.01, gamma=0.98)
    b = apply_curve(b, shadows=0.04, midtones=0.01, highlights=-0.03, gamma=1.02)
    r, g, b = apply_saturation(r, g, b, 1.1)
    return r, g, b


def desaturated_moody(r, g, b):
    """Pulled-back saturation, lifted blacks. Indie film look."""
    r = apply_curve(r, shadows=0.02, highlights=-0.02, gamma=0.97, lift=0.03)
    g = apply_curve(g, shadows=0.02, highlights=-0.02, gamma=0.96, lift=0.03)
    b = apply_curve(b, shadows=0.02, highlights=-0.02, gamma=0.95, lift=0.03)
    r, g, b = apply_saturation(r, g, b, 0.6)
    return r, g, b


def high_contrast_bw(r, g, b):
    """Aggressive B&W. Crushed blacks, blown highlights."""
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
    luma = apply_curve(luma, shadows=-0.08, midtones=0.04, highlights=-0.04, gamma=1.3, gain=1.15)
    return luma, luma, luma


def day_for_night(r, g, b):
    """Makes daylight look like night. Blue push, lowered exposure."""
    r = apply_curve(r, gamma=0.7, gain=0.5, lift=0.0)
    g = apply_curve(g, gamma=0.75, gain=0.55, lift=0.0)
    b = apply_curve(b, gamma=0.8, gain=0.7, lift=0.02)
    r, g, b = apply_saturation(r, g, b, 0.5)
    return r, g, b


def split_tone_warm(r, g, b):
    """Warm shadows, cool highlights. Editorial split tone."""
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
    shadow_mask = max(0, 1.0 - luma * 2)
    highlight_mask = max(0, luma * 2 - 1.0)
    r = clamp(r + shadow_mask * 0.05 - highlight_mask * 0.02)
    g = clamp(g + shadow_mask * 0.02 - highlight_mask * 0.01)
    b = clamp(b - shadow_mask * 0.03 + highlight_mask * 0.04)
    return r, g, b


def technicolor_3strip(r, g, b):
    """Technicolor 3-strip. Vivid saturated, golden age Hollywood."""
    r = apply_curve(r, midtones=0.04, highlights=-0.02, gamma=1.08, gain=1.05)
    g = apply_curve(g, midtones=0.03, highlights=-0.01, gamma=1.05, gain=1.03)
    b = apply_curve(b, midtones=0.02, highlights=0.0, gamma=1.02, gain=1.02)
    r, g, b = apply_saturation(r, g, b, 1.35)
    r, g, b = apply_cross_channel(r, g, b, r_to_g=0.03, g_to_b=0.02)
    return r, g, b


# ---------------------------------------------------------------------------
# Base / Correction Transforms
# ---------------------------------------------------------------------------

def log_to_rec709(r, g, b):
    """Basic LOG to Rec.709 conversion. Expands contrast, normalizes levels."""
    r = apply_curve(r, shadows=-0.03, midtones=0.02, highlights=-0.01, gamma=1.3, gain=1.2)
    g = apply_curve(g, shadows=-0.03, midtones=0.02, highlights=-0.01, gamma=1.3, gain=1.2)
    b = apply_curve(b, shadows=-0.03, midtones=0.02, highlights=-0.01, gamma=1.3, gain=1.2)
    return r, g, b


def neutral_normalize(r, g, b):
    """Subtle normalization for AI footage. Slight deband, level balance."""
    # Very gentle curve to even out AI generation artifacts
    r = apply_curve(r, shadows=0.005, highlights=-0.005, gamma=1.01)
    g = apply_curve(g, shadows=0.005, highlights=-0.005, gamma=1.01)
    b = apply_curve(b, shadows=0.005, highlights=-0.005, gamma=1.01)
    return r, g, b


# ---------------------------------------------------------------------------
# Main Generation
# ---------------------------------------------------------------------------

LUTS_TO_GENERATE = {
    # Base
    "base/log_to_rec709.cube": (log_to_rec709, "LOG to Rec.709 Base Conversion"),
    "corrections/neutral_normalize.cube": (neutral_normalize, "AI Footage Neutral Normalize"),
    # Film stocks
    "film_stocks/kodak_vision3_500t.cube": (kodak_vision3_500t, "Kodak Vision3 500T"),
    "film_stocks/kodak_vision3_250d.cube": (kodak_vision3_250d, "Kodak Vision3 250D"),
    "film_stocks/fuji_eterna_vivid_500.cube": (fuji_eterna_vivid, "Fuji Eterna Vivid 500"),
    "film_stocks/fuji_eterna_250d.cube": (fuji_eterna_250d, "Fuji Eterna 250D"),
    "film_stocks/kodak_ektachrome_100d.cube": (kodak_ektachrome, "Kodak Ektachrome 100D"),
    "film_stocks/kodak_trix_400_bw.cube": (kodak_trix_bw, "Kodak Tri-X 400 B&W"),
    "film_stocks/ilford_hp5_bw.cube": (ilford_hp5_bw, "Ilford HP5 Plus B&W"),
    "film_stocks/kodak_doublex_5222_bw.cube": (kodak_doublex_bw, "Kodak Double-X 5222 B&W"),
    "film_stocks/16mm_reversal_vintage.cube": (sixteenmm_reversal, "16mm Reversal Vintage"),
    "film_stocks/super_8mm_home_movie.cube": (super_8mm, "Super 8mm Home Movie"),
    "film_stocks/technicolor_3strip.cube": (technicolor_3strip, "Technicolor 3-Strip"),
    # Creative
    "creative/bleach_bypass.cube": (bleach_bypass, "Bleach Bypass"),
    "creative/cross_process.cube": (cross_process, "Cross Processing"),
    "creative/faded_film_aged.cube": (faded_film, "Faded Film Aged"),
    "creative/teal_orange_blockbuster.cube": (teal_orange, "Teal Orange Blockbuster"),
    "creative/desaturated_moody.cube": (desaturated_moody, "Desaturated Moody"),
    "creative/high_contrast_bw.cube": (high_contrast_bw, "High Contrast B&W"),
    "creative/day_for_night.cube": (day_for_night, "Day for Night"),
    "creative/split_tone_warm_shadows.cube": (split_tone_warm, "Split Tone Warm Shadows"),
}


def main():
    lut_root = Path(__file__).parent.parent / "luts"
    generated = 0

    for rel_path, (transform_fn, title) in LUTS_TO_GENERATE.items():
        filepath = lut_root / rel_path
        filepath.parent.mkdir(parents=True, exist_ok=True)

        print(f"  Generating {rel_path}...", end="", flush=True)
        data = generate_lut(transform_fn, title)
        write_cube(filepath, data, title)
        size_kb = filepath.stat().st_size / 1024
        print(f" {size_kb:.0f}KB")
        generated += 1

    print(f"\nGenerated {generated} LUT files in {lut_root}")
    print(f"  base/: {len([p for p in LUTS_TO_GENERATE if p.startswith('base/')])}")
    print(f"  film_stocks/: {len([p for p in LUTS_TO_GENERATE if p.startswith('film_stocks/')])}")
    print(f"  creative/: {len([p for p in LUTS_TO_GENERATE if p.startswith('creative/')])}")
    print(f"  corrections/: {len([p for p in LUTS_TO_GENERATE if p.startswith('corrections/')])}")


if __name__ == "__main__":
    main()
