"""
PopTech Cinema Studio — fal.ai Generation Wrapper
Task 2.5: Multi-model video/image generation via fal.ai API.

Usage:
  python tools/fal_generate.py --model seedance --prompt "..." --duration 5 --output shot.mp4
  python tools/fal_generate.py --model kling --prompt "..." --duration 10 --aspect 9:16 --output shot.mp4
  python tools/fal_generate.py --model flux --prompt "..." --output ref_frame.png
  python tools/fal_generate.py --model wan --prompt "..." --duration 5 --output shot.mp4
  python tools/fal_generate.py --models              # List available models
  python tools/fal_generate.py --check               # Check API key and connectivity
  python tools/fal_generate.py --costs               # Show cost log summary

Requires:
  pip install fal_client requests
  FAL_KEY environment variable set
"""

import argparse
import csv
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import fal_client
except ImportError:
    print("ERROR: fal_client not installed. Run: pip install fal_client")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    sys.exit(1)


SCRIPT_DIR = Path(__file__).parent
COST_LOG = SCRIPT_DIR / "cost_log.csv"

# ---------------------------------------------------------------------------
# Model Registry
# ---------------------------------------------------------------------------
MODELS = {
    "seedance": {
        "endpoint": "fal-ai/seedance-2/text-to-video",
        "type": "text-to-video",
        "name": "Seedance 2.0",
        "strengths": "Unified audio+video, 12 inputs, multi-axis motion control, stacked camera movements",
        "cost_per_sec": 0.50,
        "max_duration": 10,
        "default_duration": 5,
        "supports_ref_image": True,
        "supports_audio": True,
    },
    "kling": {
        "endpoint": "fal-ai/kling-video/v2/master/text-to-video",
        "type": "text-to-video",
        "name": "Kling 3.0",
        "strengths": "Multi-shot consistency, natural motion, dialogue scenes, 3-15 sec sequences",
        "cost_per_sec": 0.40,
        "max_duration": 15,
        "default_duration": 5,
        "supports_ref_image": True,
        "supports_audio": False,
    },
    "wan": {
        "endpoint": "fal-ai/wan/v2.6/text-to-video",
        "type": "text-to-video",
        "name": "Wan 2.6 (Cloud)",
        "strengths": "Open source, free locally, anime/stylized, FramePack for long-form",
        "cost_per_sec": 0.10,
        "max_duration": 10,
        "default_duration": 5,
        "supports_ref_image": True,
        "supports_audio": False,
    },
    "flux": {
        "endpoint": "fal-ai/flux/schnell",
        "type": "text-to-image",
        "name": "FLUX Schnell",
        "strengths": "Fast image generation, reference stills, storyboards, character sheets",
        "cost_per_image": 0.01,
        "supports_ref_image": False,
        "supports_audio": False,
    },
    "flux-pro": {
        "endpoint": "fal-ai/flux-pro/v1.1",
        "type": "text-to-image",
        "name": "FLUX Pro 1.1",
        "strengths": "Higher quality stills, production reference frames",
        "cost_per_image": 0.05,
        "supports_ref_image": False,
        "supports_audio": False,
    },
    "nano-banana": {
        "endpoint": "fal-ai/nano-banana-2",
        "type": "text-to-image",
        "name": "Nano Banana Pro",
        "strengths": "Storyboard frames, character images, reference stills. Primary image model for PopTech pipeline.",
        "cost_per_image": 0.01,
        "supports_ref_image": False,
        "supports_audio": False,
    },
}

# ---------------------------------------------------------------------------
# Cost tracking
# ---------------------------------------------------------------------------
def log_cost(model_key: str, prompt: str, duration: float, aspect: str,
             cost: float, output_path: str):
    """Append a row to cost_log.csv."""
    exists = COST_LOG.exists()
    with open(COST_LOG, "a", newline="") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow([
                "timestamp", "model", "prompt_hash", "duration_sec",
                "aspect_ratio", "cost_usd", "output_path", "quality_rating"
            ])
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
        writer.writerow([
            datetime.now(timezone.utc).isoformat(),
            model_key,
            prompt_hash,
            duration,
            aspect,
            f"{cost:.4f}",
            output_path,
            "",  # quality_rating — filled during QC
        ])


def show_costs():
    """Print cost log summary."""
    if not COST_LOG.exists():
        print("No cost log found. No generations have been run yet.")
        return

    with open(COST_LOG) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("Cost log is empty.")
        return

    total = sum(float(r.get("cost_usd", 0)) for r in rows)
    by_model = {}
    for r in rows:
        model = r["model"]
        by_model[model] = by_model.get(model, 0) + float(r.get("cost_usd", 0))

    print(f"Total generations: {len(rows)}")
    print(f"Total cost: ${total:.4f}")
    print(f"\nBy model:")
    for model, cost in sorted(by_model.items()):
        count = sum(1 for r in rows if r["model"] == model)
        print(f"  {model:15s}  {count} runs  ${cost:.4f}")


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------
def check_api():
    """Verify FAL_KEY is set and fal.ai API is reachable."""
    fal_key = os.environ.get("FAL_KEY", "")
    if not fal_key or fal_key.startswith("your_"):
        print("ERROR: FAL_KEY not set or is placeholder.")
        print("  Set it: export FAL_KEY=your_actual_key")
        print("  Or add to .env: FAL_KEY=...")
        return False

    print(f"FAL_KEY: set (length {len(fal_key)})")

    # Test API connectivity
    try:
        headers = {"Authorization": f"Key {fal_key}"}
        resp = requests.get("https://rest.alpha.fal.ai/", headers=headers, timeout=10)
        print(f"fal.ai API: reachable (HTTP {resp.status_code})")
        return True
    except requests.RequestException as e:
        print(f"fal.ai API: unreachable ({e})")
        return False


def generate_video(model_key: str, prompt: str, duration: int = 5,
                   aspect: str = "16:9", ref_image: str = None,
                   output: str = None, seed: int = None) -> str:
    """Submit a video generation request to fal.ai and wait for result."""
    model = MODELS[model_key]

    if model["type"] != "text-to-video":
        print(f"ERROR: {model_key} is {model['type']}, not text-to-video. Use generate_image().")
        return None

    args = {
        "prompt": prompt,
        "duration": str(duration),  # fal.ai expects string for duration
        "aspect_ratio": aspect,
    }
    if seed is not None:
        args["seed"] = seed
    if ref_image and model.get("supports_ref_image"):
        args["image_url"] = ref_image

    print(f"Submitting to {model['name']} ({model['endpoint']})...")
    print(f"  Prompt: {prompt[:80]}...")
    print(f"  Duration: {duration}s, Aspect: {aspect}")

    try:
        print("  Waiting for generation...", end="", flush=True)
        start = time.time()
        result = fal_client.subscribe(model["endpoint"], arguments=args, with_logs=True)
        elapsed = time.time() - start
        print(f" done ({elapsed:.1f}s)")
    except Exception as e:
        err_msg = str(e)
        if "Exhausted balance" in err_msg or "locked" in err_msg.lower():
            print(f"\n  ERROR: fal.ai account balance exhausted. Top up at fal.ai/dashboard/billing")
        elif "403" in err_msg:
            print(f"\n  ERROR: Access denied (403). Check FAL_KEY and account status.")
        else:
            print(f"\n  ERROR: Generation failed: {err_msg[:200]}")
        return None

    # Extract video URL
    video_url = None
    if "video" in result:
        video_url = result["video"].get("url")
    elif "output" in result:
        video_url = result["output"].get("video", {}).get("url")

    if not video_url:
        print(f"ERROR: No video URL in response. Keys: {list(result.keys())}")
        return None

    # Download
    output = output or f"renders/raw/{model_key}_{int(time.time())}.mp4"
    Path(output).parent.mkdir(parents=True, exist_ok=True)

    print(f"  Downloading to {output}...")
    resp = requests.get(video_url, timeout=120)
    with open(output, "wb") as f:
        f.write(resp.content)

    size_mb = len(resp.content) / (1024 * 1024)
    cost = duration * model.get("cost_per_sec", 0.50)
    print(f"  Output: {output} ({size_mb:.1f}MB)")
    print(f"  Estimated cost: ${cost:.2f}")

    # Log cost
    log_cost(model_key, prompt, duration, aspect, cost, output)

    return output


def generate_image(model_key: str, prompt: str, output: str = None,
                   width: int = 1024, height: int = 1024, seed: int = None) -> str:
    """Submit an image generation request to fal.ai and wait for result."""
    model = MODELS[model_key]

    args = {
        "prompt": prompt,
        "image_size": {"width": width, "height": height},
        "num_images": 1,
    }
    if seed is not None:
        args["seed"] = seed

    print(f"Submitting to {model['name']} ({model['endpoint']})...")
    print(f"  Prompt: {prompt[:80]}...")
    print(f"  Size: {width}x{height}")

    try:
        print("  Waiting for generation...", end="", flush=True)
        start = time.time()
        result = fal_client.subscribe(model["endpoint"], arguments=args, with_logs=True)
        elapsed = time.time() - start
        print(f" done ({elapsed:.1f}s)")
    except Exception as e:
        err_msg = str(e)
        if "Exhausted balance" in err_msg or "locked" in err_msg.lower():
            print(f"\n  ERROR: fal.ai account balance exhausted. Top up at fal.ai/dashboard/billing")
        elif "403" in err_msg:
            print(f"\n  ERROR: Access denied (403). Check FAL_KEY and account status.")
        else:
            print(f"\n  ERROR: Generation failed: {err_msg[:200]}")
        return None

    # Extract image URL
    image_url = None
    if "images" in result and result["images"]:
        image_url = result["images"][0].get("url")
    elif "output" in result:
        image_url = result["output"].get("images", [{}])[0].get("url")

    if not image_url:
        print(f"ERROR: No image URL in response. Keys: {list(result.keys())}")
        return None

    # Download
    output = output or f"renders/raw/{model_key}_{int(time.time())}.png"
    Path(output).parent.mkdir(parents=True, exist_ok=True)

    print(f"  Downloading to {output}...")
    resp = requests.get(image_url, timeout=60)
    with open(output, "wb") as f:
        f.write(resp.content)

    size_kb = len(resp.content) / 1024
    cost = model.get("cost_per_image", 0.05)
    print(f"  Output: {output} ({size_kb:.0f}KB)")
    print(f"  Estimated cost: ${cost:.4f}")

    log_cost(model_key, prompt, 0, f"{width}x{height}", cost, output)

    return output


def list_models():
    """Print available models with details."""
    print("\nAvailable models:\n")
    for key, m in MODELS.items():
        print(f"  {key:12s}  {m['name']}")
        print(f"  {'':12s}  Type: {m['type']}")
        print(f"  {'':12s}  Strengths: {m['strengths'][:70]}")
        if "cost_per_sec" in m:
            print(f"  {'':12s}  Cost: ~${m['cost_per_sec']:.2f}/sec")
        elif "cost_per_image" in m:
            print(f"  {'':12s}  Cost: ~${m['cost_per_image']:.2f}/image")
        print()


def main():
    parser = argparse.ArgumentParser(description="PopTech fal.ai Generation Wrapper")
    parser.add_argument("--model", "-m", help="Model: seedance, kling, wan, flux, flux-pro")
    parser.add_argument("--prompt", "-p", help="Generation prompt (or path to .txt file)")
    parser.add_argument("--duration", "-d", type=int, default=5, help="Video duration in seconds")
    parser.add_argument("--aspect", "-a", default="16:9", help="Aspect ratio (16:9, 9:16, 1:1)")
    parser.add_argument("--width", type=int, default=1024, help="Image width (for image models)")
    parser.add_argument("--height", type=int, default=1024, help="Image height (for image models)")
    parser.add_argument("--ref-image", help="Reference image URL (for img2vid)")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--models", action="store_true", help="List available models")
    parser.add_argument("--check", action="store_true", help="Check API key and connectivity")
    parser.add_argument("--costs", action="store_true", help="Show cost log summary")
    args = parser.parse_args()

    if args.models:
        list_models()
        return

    if args.check:
        check_api()
        return

    if args.costs:
        show_costs()
        return

    if not args.model or not args.prompt:
        parser.print_help()
        return

    if args.model not in MODELS:
        print(f"ERROR: Unknown model '{args.model}'. Use --models to list available.")
        sys.exit(1)

    # Load FAL_KEY from .env if not in environment
    if not os.environ.get("FAL_KEY"):
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if line.startswith("FAL_KEY=") and "your_" not in line:
                        os.environ["FAL_KEY"] = line.strip().split("=", 1)[1]
                        break

    # Resolve prompt from file if path given
    prompt = args.prompt
    if os.path.isfile(prompt):
        with open(prompt) as f:
            prompt = f.read().strip()

    model = MODELS[args.model]
    if model["type"] == "text-to-video":
        generate_video(
            args.model, prompt,
            duration=args.duration, aspect=args.aspect,
            ref_image=args.ref_image, output=args.output,
            seed=args.seed,
        )
    elif model["type"] == "text-to-image":
        generate_image(
            args.model, prompt,
            output=args.output, width=args.width, height=args.height,
            seed=args.seed,
        )


if __name__ == "__main__":
    main()
