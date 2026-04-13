"""
PopTech Cinema Studio — HeyGen Avatar Video Generation Wrapper
Task 3.1: Programmatic avatar video generation via HeyGen API.

Usage:
  python tools/heygen_generate.py --list-avatars [--search "name"]
  python tools/heygen_generate.py --list-voices [--search "name"]
  python tools/heygen_generate.py --generate --avatar AVATAR_ID --voice VOICE_ID --script "text" --output out.mp4
  python tools/heygen_generate.py --status VIDEO_ID
  python tools/heygen_generate.py --check

Requires:
  HEYGEN_API_KEY in .env
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
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent
COST_LOG = SCRIPT_DIR / "cost_log.csv"
API_BASE = "https://api.heygen.com"


def load_api_key() -> str:
    key = os.environ.get("HEYGEN_API_KEY", "")
    if not key or key.startswith("your_"):
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if line.startswith("HEYGEN_API_KEY=") and "your_" not in line:
                        key = line.strip().split("=", 1)[1]
                        break
    return key


def api_get(endpoint: str, key: str, params: dict = None) -> dict:
    headers = {"X-Api-Key": key}
    resp = requests.get(f"{API_BASE}{endpoint}", headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def api_post(endpoint: str, key: str, body: dict) -> dict:
    headers = {"X-Api-Key": key, "Content-Type": "application/json"}
    resp = requests.post(f"{API_BASE}{endpoint}", headers=headers, json=body, timeout=30)
    resp.raise_for_status()
    return resp.json()


def log_cost(model: str, prompt: str, duration: float, cost: float, output_path: str):
    exists = COST_LOG.exists()
    with open(COST_LOG, "a", newline="") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["timestamp", "model", "prompt_hash", "duration_sec",
                             "aspect_ratio", "cost_usd", "output_path", "quality_rating"])
        writer.writerow([
            datetime.now(timezone.utc).isoformat(),
            model, hashlib.md5(prompt.encode()).hexdigest()[:8],
            duration, "16:9", f"{cost:.4f}", output_path, "",
        ])


def check_api(key: str):
    print(f"HEYGEN_API_KEY: {'set' if key else 'MISSING'} (length {len(key)})")
    try:
        data = api_get("/v2/avatars", key)
        avatars = data.get("data", {}).get("avatars", [])
        print(f"API: connected ({len(avatars)} avatars available)")
        return True
    except Exception as e:
        print(f"API: failed ({str(e)[:100]})")
        return False


def list_avatars(key: str, search: str = None):
    data = api_get("/v2/avatars", key)
    avatars = data.get("data", {}).get("avatars", [])

    if search:
        search_lower = search.lower()
        avatars = [a for a in avatars if search_lower in a.get("avatar_name", "").lower()
                   or search_lower in a.get("avatar_id", "").lower()]

    print(f"\nAvatars ({len(avatars)} found):\n")
    for a in avatars[:30]:
        name = a.get("avatar_name", "Unknown")
        aid = a.get("avatar_id", "?")
        atype = a.get("type", "?")
        print(f"  {aid[:35]:35s}  {name:30s}  [{atype}]")

    if len(avatars) > 30:
        print(f"\n  ... {len(avatars) - 30} more (use --search to filter)")


def list_voices(key: str, search: str = None):
    data = api_get("/v2/voices", key)
    voices = data.get("data", {}).get("voices", [])

    if search:
        search_lower = search.lower()
        voices = [v for v in voices if search_lower in v.get("name", v.get("display_name", "")).lower()
                  or search_lower in v.get("voice_id", "").lower()
                  or search_lower in v.get("language", "").lower()]

    print(f"\nVoices ({len(voices)} found):\n")
    for v in voices[:30]:
        name = v.get("name", v.get("display_name", "Unknown"))
        vid = v.get("voice_id", "?")
        lang = v.get("language", "?")
        gender = v.get("gender", "?")
        print(f"  {vid[:30]:30s}  {name:25s}  {lang:10s}  [{gender}]")

    if len(voices) > 30:
        print(f"\n  ... {len(voices) - 30} more (use --search to filter)")


def generate_video(key: str, avatar_id: str, voice_id: str, script: str,
                   output: str = None, background: str = None,
                   dimension: dict = None) -> str:
    """Generate an avatar video via HeyGen API v2."""

    body = {
        "video_inputs": [{
            "character": {
                "type": "avatar",
                "avatar_id": avatar_id,
                "avatar_style": "normal",
            },
            "voice": {
                "type": "text",
                "input_text": script,
                "voice_id": voice_id,
            },
        }],
        "dimension": dimension or {"width": 1920, "height": 1080},
    }

    if background:
        body["video_inputs"][0]["background"] = {"type": "color", "value": background}

    print(f"Submitting HeyGen video generation...")
    print(f"  Avatar: {avatar_id[:30]}...")
    print(f"  Voice: {voice_id[:30]}...")
    print(f"  Script: {script[:60]}...")

    try:
        result = api_post("/v2/video/generate", key, body)
    except requests.HTTPError as e:
        print(f"  ERROR: {e.response.status_code} — {e.response.text[:200]}")
        return None

    data = result.get("data", {})
    video_id = data.get("video_id")
    if not video_id:
        print(f"  ERROR: No video_id returned. Response: {json.dumps(result)[:200]}")
        return None

    print(f"  Video ID: {video_id}")
    print(f"  Polling for completion...", end="", flush=True)

    # Poll for completion
    start = time.time()
    while True:
        time.sleep(5)
        status_resp = api_get("/v1/video_status.get", key, {"video_id": video_id})
        status_data = status_resp.get("data", {})
        status = status_data.get("status", "unknown")

        elapsed = time.time() - start
        if status == "completed":
            video_url = status_data.get("video_url")
            duration = status_data.get("duration", 0)
            print(f" done ({elapsed:.0f}s)")
            print(f"  Status: completed")
            print(f"  Duration: {duration}s")

            # Download
            output = output or f"renders/raw/heygen_{video_id}.mp4"
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            print(f"  Downloading to {output}...")
            resp = requests.get(video_url, timeout=120)
            with open(output, "wb") as f:
                f.write(resp.content)

            size_mb = len(resp.content) / (1024 * 1024)
            print(f"  Output: {output} ({size_mb:.1f}MB)")

            # Log cost (Creator plan — included in subscription)
            log_cost("heygen", script, duration, 0.00, output)
            return output

        elif status == "failed":
            error = status_data.get("error", "unknown error")
            print(f"\n  ERROR: Generation failed — {error}")
            return None

        elif elapsed > 300:
            print(f"\n  ERROR: Timed out after 5 minutes (status: {status})")
            return None

        print(".", end="", flush=True)


def get_status(key: str, video_id: str):
    data = api_get("/v1/video_status.get", key, {"video_id": video_id})
    status_data = data.get("data", {})
    print(f"Video: {video_id}")
    print(f"Status: {status_data.get('status', 'unknown')}")
    if status_data.get("video_url"):
        print(f"URL: {status_data['video_url']}")
    if status_data.get("duration"):
        print(f"Duration: {status_data['duration']}s")


def main():
    parser = argparse.ArgumentParser(description="PopTech HeyGen Avatar Video Generator")
    parser.add_argument("--list-avatars", action="store_true")
    parser.add_argument("--list-voices", action="store_true")
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--avatar", help="Avatar ID")
    parser.add_argument("--voice", help="Voice ID")
    parser.add_argument("--script", help="Script text (or path to .txt file)")
    parser.add_argument("--output", "-o", help="Output video path")
    parser.add_argument("--background", default="#000000", help="Background color (default: black)")
    parser.add_argument("--status", help="Check video generation status by ID")
    parser.add_argument("--search", help="Filter avatars/voices by name")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    key = load_api_key()
    if not key:
        print("ERROR: HEYGEN_API_KEY not set. Add to .env or environment.")
        sys.exit(1)

    if args.check:
        check_api(key)
    elif args.list_avatars:
        list_avatars(key, args.search)
    elif args.list_voices:
        list_voices(key, args.search)
    elif args.status:
        get_status(key, args.status)
    elif args.generate:
        if not args.avatar or not args.voice or not args.script:
            print("ERROR: --avatar, --voice, and --script required for generation.")
            sys.exit(1)
        script = args.script
        if os.path.isfile(script):
            with open(script) as f:
                script = f.read().strip()
        generate_video(key, args.avatar, args.voice, script, args.output, args.background)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
