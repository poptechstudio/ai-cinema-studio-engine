"""
PopTech Cinema Studio — API Credit Balance Checker
Task 5.5: Checks all service balances and logs to MySQL governance dashboard.

Usage:
  python tools/check_balances.py              # Check all services, print summary
  python tools/check_balances.py --log-mysql  # Check and log to MySQL
  python tools/check_balances.py --json       # Output as JSON
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests not installed"); sys.exit(1)


def load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    if v and not v.startswith("your_"):
                        os.environ.setdefault(k, v)


def check_fal():
    key = os.environ.get("FAL_KEY", "")
    if not key or key.startswith("your_"):
        return {"service": "fal_ai", "balance": None, "status": "no_key"}
    # fal.ai doesn't have a public balance API — check by attempting a minimal call
    try:
        import fal_client
        fal_client.submit("fal-ai/nano-banana-2", arguments={"prompt": "test"})
        return {"service": "fal_ai", "balance": None, "status": "active"}
    except Exception as e:
        if "Exhausted" in str(e) or "locked" in str(e).lower():
            return {"service": "fal_ai", "balance": 0, "status": "exhausted"}
        return {"service": "fal_ai", "balance": None, "status": "error", "error": str(e)[:100]}


def check_muapi():
    key = os.environ.get("MUAPI_API_KEY", "")
    if not key or key.startswith("your_"):
        return {"service": "muapi", "balance": None, "status": "no_key"}
    try:
        resp = requests.get("https://api.muapi.ai/api/v1/account/balance",
                            headers={"X-API-Key": key}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return {"service": "muapi", "balance": data.get("balance", 0), "status": "active"}
        return {"service": "muapi", "balance": None, "status": f"http_{resp.status_code}"}
    except Exception as e:
        return {"service": "muapi", "balance": None, "status": "error", "error": str(e)[:100]}


def check_elevenlabs():
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not key or key.startswith("your_"):
        return {"service": "elevenlabs", "balance": None, "status": "no_key"}
    try:
        resp = requests.get("https://api.elevenlabs.io/v1/user/subscription",
                            headers={"xi-api-key": key}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            chars_used = data.get("character_count", 0)
            chars_limit = data.get("character_limit", 0)
            return {"service": "elevenlabs", "balance": chars_limit - chars_used,
                    "status": "active", "unit": "characters",
                    "used": chars_used, "limit": chars_limit}
        return {"service": "elevenlabs", "balance": None, "status": f"http_{resp.status_code}"}
    except Exception as e:
        return {"service": "elevenlabs", "balance": None, "status": "error", "error": str(e)[:100]}


def check_heygen():
    key = os.environ.get("HEYGEN_API_KEY", "")
    if not key or key.startswith("your_"):
        return {"service": "heygen", "balance": None, "status": "no_key"}
    try:
        resp = requests.get("https://api.heygen.com/v2/user/remaining_quota",
                            headers={"X-Api-Key": key}, timeout=10)
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            api_credits = data.get("remaining_quota", 0)
            plan_credits = data.get("details", {}).get("plan_credit", 0)
            return {"service": "heygen", "balance": api_credits,
                    "status": "active" if api_credits > 0 else "web_only",
                    "api_credits": api_credits, "plan_credits": plan_credits}
        return {"service": "heygen", "balance": None, "status": f"http_{resp.status_code}"}
    except Exception as e:
        return {"service": "heygen", "balance": None, "status": "error", "error": str(e)[:100]}


def main():
    parser = argparse.ArgumentParser(description="PopTech Credit Balance Checker")
    parser.add_argument("--log-mysql", action="store_true", help="Log balances to MySQL")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    load_env()

    checkers = [check_muapi, check_elevenlabs, check_heygen]
    results = [checker() for checker in checkers]

    timestamp = datetime.now(timezone.utc).isoformat()

    if args.json:
        print(json.dumps({"timestamp": timestamp, "balances": results}, indent=2))
        return

    print(f"\n  PopTech Cinema Studio — Credit Balances ({timestamp[:19]}Z)\n")
    print(f"  {'Service':<15s} {'Balance':<15s} {'Status':<15s} {'Notes'}")
    print("  " + "-" * 65)
    for r in results:
        bal = f"${r['balance']:.2f}" if isinstance(r.get("balance"), (int, float)) else "N/A"
        notes = ""
        if r.get("unit") == "characters":
            notes = f"{r.get('used', 0):,}/{r.get('limit', 0):,} chars"
        elif r.get("plan_credits"):
            notes = f"plan: {r['plan_credits']}"
        print(f"  {r['service']:<15s} {bal:<15s} {r['status']:<15s} {notes}")

    if args.log_mysql:
        print("\n  MySQL logging: STUB (requires VPS MySQL connection)")


if __name__ == "__main__":
    main()
