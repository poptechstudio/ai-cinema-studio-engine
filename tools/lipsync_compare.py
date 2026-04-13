"""
PopTech Cinema Studio — Lip-Sync Model Comparison Tool
Task 3.2 + 3.4: Compare lip-sync models across cloud providers.

Usage:
  python tools/lipsync_compare.py --video VIDEO_URL --audio AUDIO_URL --models all
  python tools/lipsync_compare.py --video VIDEO_URL --audio AUDIO_URL --models latentsync,creatify
  python tools/lipsync_compare.py --list                    # List available models
  python tools/lipsync_compare.py --results                 # Show comparison results

Providers:
  Muapi.ai ($7.96 balance) — 9 lip-sync models, pay-per-use
  fal.ai (needs top-up) — LatentSync, Hallo, MuseTalk, LivePortrait, Wav2Lip, LipSync

Requirements:
  MUAPI_API_KEY in .env
  FAL_KEY in .env (optional — only for fal.ai models)
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent
RESULTS_FILE = SCRIPT_DIR / "lipsync_results.json"

# ---------------------------------------------------------------------------
# Model Registry — all available lip-sync models across providers
# ---------------------------------------------------------------------------
MODELS = {
    # === Muapi.ai models (9) ===
    "muapi_latentsync": {
        "provider": "muapi",
        "endpoint": "/api/v1/latentsync-video",
        "name": "LatentSync (Muapi)",
        "input_type": "video",  # video + audio
        "quality_tier": "high",
        "notes": "ByteDance model. Proven on Seedance footage. $0.26/run.",
    },
    "muapi_infinitetalk": {
        "provider": "muapi",
        "endpoint": "/api/v1/infinitetalk-image-to-video",
        "name": "InfiniteTalk I2V (Muapi)",
        "input_type": "image",  # image + audio
        "quality_tier": "high",
        "notes": "Unlimited length. Image-to-video with lip-sync.",
    },
    "muapi_infinitetalk_v2v": {
        "provider": "muapi",
        "endpoint": "/api/v1/infinitetalk-video-to-video",
        "name": "InfiniteTalk V2V (Muapi)",
        "input_type": "video",
        "quality_tier": "high",
        "notes": "Video-to-video lip-sync with unlimited length.",
    },
    "muapi_wan22_speech": {
        "provider": "muapi",
        "endpoint": "/api/v1/wan2.2-speech-to-video",
        "name": "Wan 2.2 Speech-to-Video (Muapi)",
        "input_type": "image",
        "quality_tier": "medium",
        "notes": "Wan model native speech-to-video.",
    },
    "muapi_ltx_23": {
        "provider": "muapi",
        "endpoint": "/api/v1/ltx-2.3-lipsync",
        "name": "LTX 2.3 Lipsync (Muapi)",
        "input_type": "video",
        "quality_tier": "medium",
        "notes": "LTX model lip-sync.",
    },
    "muapi_ltx_219b": {
        "provider": "muapi",
        "endpoint": "/api/v1/ltx-2-19b-lipsync",
        "name": "LTX 2 19B Lipsync (Muapi)",
        "input_type": "video",
        "quality_tier": "medium",
        "notes": "Larger LTX model.",
    },
    "muapi_sync": {
        "provider": "muapi",
        "endpoint": "/api/v1/sync-lipsync",
        "name": "Sync Lipsync (Muapi)",
        "input_type": "video",
        "quality_tier": "medium",
        "notes": "General-purpose sync.",
    },
    "muapi_creatify": {
        "provider": "muapi",
        "endpoint": "/api/v1/creatify-lipsync",
        "name": "Creatify Lipsync (Muapi)",
        "input_type": "video",
        "quality_tier": "medium",
        "notes": "Creatify model.",
    },
    "muapi_veed": {
        "provider": "muapi",
        "endpoint": "/api/v1/veed-lipsync",
        "name": "Veed Lipsync (Muapi)",
        "input_type": "video",
        "quality_tier": "medium",
        "notes": "Veed model.",
    },
    # === fal.ai models (6) — needs FAL_KEY with credits ===
    "fal_latentsync": {
        "provider": "fal",
        "endpoint": "fal-ai/latentsync",
        "name": "LatentSync (fal.ai)",
        "input_type": "video",
        "quality_tier": "high",
        "notes": "Same model as Muapi but on fal.ai infrastructure.",
    },
    "fal_hallo": {
        "provider": "fal",
        "endpoint": "fal-ai/hallo",
        "name": "Hallo (fal.ai)",
        "input_type": "image",
        "quality_tier": "high",
        "notes": "Portrait animation model.",
    },
    "fal_musetalk": {
        "provider": "fal",
        "endpoint": "fal-ai/musetalk",
        "name": "MuseTalk (fal.ai)",
        "input_type": "video",
        "quality_tier": "medium",
        "notes": "Real-time capable lip-sync.",
    },
    "fal_liveportrait": {
        "provider": "fal",
        "endpoint": "fal-ai/live-portrait",
        "name": "LivePortrait (fal.ai)",
        "input_type": "image",
        "quality_tier": "high",
        "notes": "Expression control, stitching mode.",
    },
    "fal_wav2lip": {
        "provider": "fal",
        "endpoint": "fal-ai/wav2lip",
        "name": "Wav2Lip (fal.ai)",
        "input_type": "video",
        "quality_tier": "low",
        "notes": "Fastest but lowest quality. Needs CodeFormer post.",
    },
    "fal_lipsync": {
        "provider": "fal",
        "endpoint": "fal-ai/lipsync",
        "name": "LipSync General (fal.ai)",
        "input_type": "video",
        "quality_tier": "medium",
        "notes": "General-purpose fal.ai lip-sync.",
    },
}

# ---------------------------------------------------------------------------
# Muapi.ai runner
# ---------------------------------------------------------------------------
def run_muapi(model_key: str, video_url: str, audio_url: str, image_url: str = None) -> dict:
    """Run a Muapi.ai lip-sync model and return result."""
    key = os.environ.get("MUAPI_API_KEY", "")
    if not key:
        return {"error": "MUAPI_API_KEY not set"}

    model = MODELS[model_key]
    headers = {"X-API-Key": key, "Content-Type": "application/json"}

    body = {"audio_url": audio_url}
    if model["input_type"] == "video":
        body["video_url"] = video_url
    else:
        body["image_url"] = image_url or video_url

    start = time.time()
    try:
        resp = requests.post(f"https://api.muapi.ai{model['endpoint']}", headers=headers, json=body, timeout=30)
        if resp.status_code != 200:
            return {"error": f"HTTP {resp.status_code}: {resp.text[:200]}"}

        result = resp.json()
        request_id = result.get("request_id")
        if not request_id:
            return {"error": f"No request_id: {json.dumps(result)[:200]}"}

        # Poll for completion
        while True:
            time.sleep(10)
            poll = requests.get(f"https://api.muapi.ai/api/v1/predictions/{request_id}/result",
                                headers={"X-API-Key": key}, timeout=15)
            if poll.status_code != 200:
                continue

            poll_data = poll.json()
            status = poll_data.get("status", "?")

            if status in ("completed", "succeeded") or poll_data.get("outputs"):
                elapsed = time.time() - start
                outputs = poll_data.get("outputs", [])
                output_url = outputs[0] if outputs else None
                return {
                    "status": "completed",
                    "output_url": output_url,
                    "elapsed_sec": round(elapsed, 1),
                    "request_id": request_id,
                }
            elif status == "failed":
                return {"error": f"Failed: {json.dumps(poll_data)[:200]}"}
            elif time.time() - start > 600:
                return {"error": "Timeout (10 min)"}

    except Exception as e:
        return {"error": str(e)[:200]}


# ---------------------------------------------------------------------------
# fal.ai runner
# ---------------------------------------------------------------------------
def run_fal(model_key: str, video_url: str, audio_url: str, image_url: str = None) -> dict:
    """Run a fal.ai lip-sync model and return result."""
    try:
        import fal_client
    except ImportError:
        return {"error": "fal_client not installed"}

    fal_key = os.environ.get("FAL_KEY", "")
    if not fal_key or fal_key.startswith("your_"):
        return {"error": "FAL_KEY not set or placeholder"}

    model = MODELS[model_key]
    args = {"audio_url": audio_url}
    if model["input_type"] == "video":
        args["video_url"] = video_url
    else:
        args["source_image_url"] = image_url or video_url
        args["driven_audio_url"] = audio_url

    start = time.time()
    try:
        result = fal_client.subscribe(model["endpoint"], arguments=args, with_logs=True)
        elapsed = time.time() - start
        output_url = result.get("video", {}).get("url", "")
        return {
            "status": "completed",
            "output_url": output_url,
            "elapsed_sec": round(elapsed, 1),
        }
    except Exception as e:
        return {"error": str(e)[:200]}


# ---------------------------------------------------------------------------
# Main comparison runner
# ---------------------------------------------------------------------------
def run_comparison(video_url: str, audio_url: str, model_keys: list,
                   image_url: str = None, output_dir: str = "tests/e2e_phase2/lipsync_compare"):
    """Run multiple lip-sync models and save results."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    results = []

    for key in model_keys:
        model = MODELS.get(key)
        if not model:
            print(f"  Unknown model: {key}")
            continue

        print(f"\n=== {model['name']} ({model['provider']}) ===")

        if model["provider"] == "muapi":
            result = run_muapi(key, video_url, audio_url, image_url)
        elif model["provider"] == "fal":
            result = run_fal(key, video_url, audio_url, image_url)
        else:
            result = {"error": f"Unknown provider: {model['provider']}"}

        if result.get("error"):
            print(f"  ERROR: {result['error']}")
            results.append({"model": key, "name": model["name"], "status": "failed",
                            "error": result["error"]})
        else:
            print(f"  Completed in {result['elapsed_sec']}s")
            output_url = result.get("output_url", "")
            if output_url:
                # Download result
                outfile = f"{output_dir}/{key}.mp4"
                try:
                    dl = requests.get(output_url, timeout=120)
                    with open(outfile, "wb") as f:
                        f.write(dl.content)
                    size_kb = len(dl.content) // 1024
                    print(f"  Downloaded: {outfile} ({size_kb}KB)")
                    results.append({
                        "model": key, "name": model["name"], "status": "completed",
                        "elapsed_sec": result["elapsed_sec"], "output_file": outfile,
                        "size_kb": size_kb, "output_url": output_url,
                    })
                except Exception as e:
                    print(f"  Download failed: {e}")
                    results.append({"model": key, "name": model["name"], "status": "download_failed"})
            else:
                results.append({"model": key, "name": model["name"], "status": "no_output_url"})

    # Save results
    with open(RESULTS_FILE, "w") as f:
        json.dump({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "video_url": video_url,
            "audio_url": audio_url,
            "results": results,
        }, f, indent=2)

    print(f"\nResults saved to {RESULTS_FILE}")
    return results


def list_models():
    print("\nAvailable lip-sync models:\n")
    for provider in ["muapi", "fal"]:
        models = {k: v for k, v in MODELS.items() if v["provider"] == provider}
        provider_name = "Muapi.ai" if provider == "muapi" else "fal.ai"
        print(f"  [{provider_name}]")
        for key, m in models.items():
            print(f"    {key:30s}  {m['name']}")
            print(f"    {'':30s}  Quality: {m['quality_tier']} | Input: {m['input_type']}")
            print(f"    {'':30s}  {m['notes']}")
            print()


def show_results():
    if not RESULTS_FILE.exists():
        print("No results file found. Run a comparison first.")
        return

    with open(RESULTS_FILE) as f:
        data = json.load(f)

    print(f"\nLip-sync comparison results ({data['timestamp'][:19]})\n")
    print(f"{'Model':<35s} {'Status':<12s} {'Time':<8s} {'Size':<10s} {'Quality'}")
    print("-" * 80)
    for r in data["results"]:
        model_info = MODELS.get(r["model"], {})
        status = r.get("status", "?")
        elapsed = f"{r.get('elapsed_sec', '?')}s" if "elapsed_sec" in r else "—"
        size = f"{r.get('size_kb', '?')}KB" if "size_kb" in r else "—"
        quality = model_info.get("quality_tier", "?")
        print(f"  {r['name']:<33s} {status:<12s} {elapsed:<8s} {size:<10s} {quality}")


def main():
    parser = argparse.ArgumentParser(description="PopTech Lip-Sync Model Comparison")
    parser.add_argument("--video", help="Video URL (for video-input models)")
    parser.add_argument("--audio", help="Audio URL")
    parser.add_argument("--image", help="Image URL (for image-input models)")
    parser.add_argument("--models", default="all", help="Comma-separated model keys or 'all', 'muapi', 'fal'")
    parser.add_argument("--output-dir", default="tests/e2e_phase2/lipsync_compare")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--results", action="store_true")
    args = parser.parse_args()

    if args.list:
        list_models()
        return
    if args.results:
        show_results()
        return

    if not args.video or not args.audio:
        parser.print_help()
        return

    # Load env
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    if v and not v.startswith("your_"):
                        os.environ.setdefault(k, v)

    # Resolve model list
    if args.models == "all":
        model_keys = list(MODELS.keys())
    elif args.models == "muapi":
        model_keys = [k for k, v in MODELS.items() if v["provider"] == "muapi"]
    elif args.models == "fal":
        model_keys = [k for k, v in MODELS.items() if v["provider"] == "fal"]
    else:
        model_keys = [m.strip() for m in args.models.split(",")]

    run_comparison(args.video, args.audio, model_keys, args.image, args.output_dir)


if __name__ == "__main__":
    main()
