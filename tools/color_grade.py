"""
PopTech Cinema Studio — FFmpeg Color Grading Pipeline
Task 2.4: Apply LUT-based color grading to video files.

Usage:
  python tools/color_grade.py input.mp4 --lut kodak_vision3_500t --output graded.mp4
  python tools/color_grade.py input.mp4 --chain "neutral_normalize,kodak_vision3_500t" --output graded.mp4
  python tools/color_grade.py input.mp4 --lut bleach_bypass --grain 0.3 --vignette 0.5 --output graded.mp4
  python tools/color_grade.py --list                    # List available LUTs
  python tools/color_grade.py --batch input_dir/ --lut kodak_vision3_500t --output-dir graded/

Requires:
  FFmpeg accessible via Remotion: cd remotion && npx remotion ffmpeg
  Or system FFmpeg if installed.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


# Resolve paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
LUTS_DIR = PROJECT_ROOT / "luts"
INDEX_PATH = LUTS_DIR / "index.json"
REMOTION_DIR = PROJECT_ROOT / "remotion"


def find_ffmpeg() -> str:
    """Find FFmpeg — prefer system full build (has lut3d), fall back to Remotion's bundled."""
    # Winget install location
    winget_path = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Links"

    # Try system FFmpeg (full build with lut3d filter)
    search_paths = [str(winget_path)] + os.environ.get("PATH", "").split(os.pathsep)
    for path_dir in search_paths:
        ffmpeg_exe = Path(path_dir) / "ffmpeg.exe"
        if ffmpeg_exe.exists():
            try:
                result = subprocess.run([str(ffmpeg_exe), "-filters"], capture_output=True, text=True, timeout=5)
                if "lut3d" in result.stdout:
                    return str(ffmpeg_exe)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

    # Try bare ffmpeg command
    try:
        result = subprocess.run(["ffmpeg", "-filters"], capture_output=True, text=True, timeout=5)
        if "lut3d" in result.stdout:
            return "ffmpeg"
    except FileNotFoundError:
        pass

    # Fall back to Remotion FFmpeg (minimal, no lut3d — encoding only)
    try:
        result = subprocess.run(
            ["npx", "remotion", "ffmpeg", "-version"],
            capture_output=True, text=True, timeout=15, cwd=str(REMOTION_DIR)
        )
        if result.returncode == 0:
            return "npx remotion ffmpeg"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return None


def resolve_lut_path(lut_name: str) -> Path:
    """Resolve a LUT name to its .cube file path."""
    # Direct .cube path
    if lut_name.endswith(".cube"):
        path = LUTS_DIR / lut_name
        if path.exists():
            return path

    # Search by name in index
    if INDEX_PATH.exists():
        with open(INDEX_PATH) as f:
            index = json.load(f)
        for category in ["base", "film_stocks", "creative", "corrections"]:
            cat_data = index.get(category, {})
            if lut_name in cat_data:
                return LUTS_DIR / cat_data[lut_name]["file"]

    # Search by filename pattern
    for cube_file in LUTS_DIR.rglob("*.cube"):
        if lut_name in cube_file.stem:
            return cube_file

    return None


def build_filter_chain(luts: list[str], grain: float = 0, vignette: float = 0,
                       exposure: float = 0, contrast: float = 0, saturation: float = 0,
                       deband: bool = False) -> str:
    """Build an FFmpeg video filter chain string."""
    filters = []

    # Debanding (for AI footage artifacts)
    if deband:
        filters.append("deband=1thr=0.02:2thr=0.02:3thr=0.02:blur=1")

    # LUT chain
    for lut_name in luts:
        lut_path = resolve_lut_path(lut_name)
        if lut_path is None:
            print(f"WARNING: LUT '{lut_name}' not found, skipping")
            continue
        # For FFmpeg filter paths on Windows, use short relative paths to avoid
        # issues with spaces and colons. Fall back to absolute if needed.
        try:
            lut_path_rel = lut_path.relative_to(Path.cwd())
            lut_path_str = str(lut_path_rel).replace("\\", "/")
        except ValueError:
            # Can't make relative — use 8.3 short path or absolute
            lut_path_str = str(lut_path).replace("\\", "/")
        filters.append(f"lut3d=file='{lut_path_str}'")

    # Exposure/contrast/saturation adjustments via eq filter
    eq_parts = []
    if exposure != 0:
        eq_parts.append(f"brightness={exposure}")
    if contrast != 0:
        eq_parts.append(f"contrast={1.0 + contrast}")
    if saturation != 0:
        eq_parts.append(f"saturation={1.0 + saturation}")
    if eq_parts:
        filters.append(f"eq={':'.join(eq_parts)}")

    # Film grain overlay
    if grain > 0:
        intensity = int(grain * 30)  # 0-1 maps to 0-30 noise strength
        filters.append(f"noise=alls={intensity}:allf=t")

    # Vignette
    if vignette > 0:
        angle = 0.3 + vignette * 0.5  # 0-1 maps to subtle-strong
        filters.append(f"vignette=angle={angle:.2f}")

    return ",".join(filters) if filters else "null"


def run_ffmpeg(ffmpeg_cmd: str, input_path: str, output_path: str, filter_chain: str,
               codec: str = "libx264", crf: int = 18, audio: str = "copy"):
    """Execute FFmpeg with the given filter chain."""
    # Build command
    if ffmpeg_cmd == "npx remotion ffmpeg":
        cmd_parts = ["npx", "remotion", "ffmpeg"]
        cwd = str(REMOTION_DIR)
    else:
        cmd_parts = [ffmpeg_cmd]
        cwd = None

    cmd_parts.extend([
        "-y",  # overwrite output
        "-i", input_path,
        "-vf", filter_chain,
        "-c:v", codec,
        "-crf", str(crf),
        "-c:a", audio,
        output_path,
    ])

    print(f"Running: {' '.join(cmd_parts[:6])}... -vf \"{filter_chain[:80]}...\"")

    result = subprocess.run(cmd_parts, capture_output=True, text=True, cwd=cwd, timeout=300)
    if result.returncode != 0:
        print(f"FFmpeg error:\n{result.stderr[-500:]}")
        return False

    output_size = Path(output_path).stat().st_size / 1024
    print(f"Output: {output_path} ({output_size:.0f}KB)")
    return True


def list_luts():
    """Print all available LUTs."""
    if not INDEX_PATH.exists():
        print("No index.json found. Run tools/generate_luts.py first.")
        return

    with open(INDEX_PATH) as f:
        index = json.load(f)

    for category in ["base", "corrections", "film_stocks", "creative"]:
        cat_data = index.get(category, {})
        if not cat_data:
            continue
        print(f"\n  [{category.upper()}]")
        for key, data in cat_data.items():
            print(f"    {key:30s}  {data['name']}")
            print(f"    {'':30s}  {data['description'][:70]}")


def main():
    parser = argparse.ArgumentParser(description="PopTech Cinema Color Grading Pipeline")
    parser.add_argument("input", nargs="?", help="Input video file")
    parser.add_argument("--lut", help="Single LUT to apply (name from index)")
    parser.add_argument("--chain", help="Comma-separated LUT chain (e.g. 'neutral_normalize,kodak_vision3_500t')")
    parser.add_argument("--output", "-o", help="Output video file")
    parser.add_argument("--grain", type=float, default=0, help="Film grain intensity (0-1)")
    parser.add_argument("--vignette", type=float, default=0, help="Vignette strength (0-1)")
    parser.add_argument("--exposure", type=float, default=0, help="Exposure adjustment (-1 to 1)")
    parser.add_argument("--contrast", type=float, default=0, help="Contrast adjustment (-1 to 1)")
    parser.add_argument("--saturation", type=float, default=0, help="Saturation adjustment (-1 to 1)")
    parser.add_argument("--deband", action="store_true", help="Apply debanding filter for AI footage")
    parser.add_argument("--codec", default="libx264", help="Output video codec (default: libx264)")
    parser.add_argument("--crf", type=int, default=18, help="Quality (lower=better, default: 18)")
    parser.add_argument("--list", action="store_true", help="List all available LUTs")
    parser.add_argument("--batch", help="Batch mode: grade all videos in directory")
    parser.add_argument("--output-dir", help="Output directory for batch mode")
    args = parser.parse_args()

    if args.list:
        list_luts()
        return

    if not args.input and not args.batch:
        parser.print_help()
        return

    # Find FFmpeg
    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        print("ERROR: FFmpeg not found. Install FFmpeg or ensure Remotion is installed.")
        sys.exit(1)
    print(f"Using FFmpeg: {ffmpeg}")

    # Build LUT chain
    if args.chain:
        luts = [l.strip() for l in args.chain.split(",")]
    elif args.lut:
        luts = [args.lut]
    else:
        print("ERROR: Specify --lut or --chain")
        sys.exit(1)

    # Validate LUTs exist
    for lut_name in luts:
        path = resolve_lut_path(lut_name)
        if path is None:
            print(f"ERROR: LUT '{lut_name}' not found. Use --list to see available LUTs.")
            sys.exit(1)

    filter_chain = build_filter_chain(
        luts, grain=args.grain, vignette=args.vignette,
        exposure=args.exposure, contrast=args.contrast,
        saturation=args.saturation, deband=args.deband,
    )

    if args.batch:
        # Batch mode
        input_dir = Path(args.batch)
        output_dir = Path(args.output_dir or str(input_dir) + "_graded")
        output_dir.mkdir(parents=True, exist_ok=True)

        video_exts = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
        files = [f for f in input_dir.iterdir() if f.suffix.lower() in video_exts]
        print(f"Batch grading {len(files)} files -> {output_dir}")

        for f in files:
            out = output_dir / f.name
            run_ffmpeg(ffmpeg, str(f), str(out), filter_chain, args.codec, args.crf)
    else:
        # Single file mode
        output = args.output or str(Path(args.input).stem) + "_graded.mp4"
        run_ffmpeg(ffmpeg, args.input, output, filter_chain, args.codec, args.crf)


if __name__ == "__main__":
    main()
