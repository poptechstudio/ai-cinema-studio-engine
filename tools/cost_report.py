"""
PopTech Cinema Studio — Cost Report Generator
Task 5.5: Monthly cost reports comparing PopTech vs Higgsfield/Arcads.

Usage:
  python tools/cost_report.py                    # Print current month summary
  python tools/cost_report.py --month 2026-04    # Specific month
  python tools/cost_report.py --competitive      # Include competitive comparison
  python tools/cost_report.py --json             # Output as JSON
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
COST_LOG = SCRIPT_DIR / "cost_log.csv"

# Competitive pricing reference
COMPETITOR_PRICING = {
    "higgsfield": {"monthly_sub": 200, "per_video": 0, "name": "Higgsfield Cinema Studio"},
    "arcads": {"monthly_sub": 220, "per_video": 10, "name": "Arcads"},
}


def load_cost_log():
    if not COST_LOG.exists():
        return []
    with open(COST_LOG) as f:
        return list(csv.DictReader(f))


def generate_report(month=None, competitive=False):
    rows = load_cost_log()
    if not rows:
        print("No cost data. Run productions first.")
        return {}

    if month:
        rows = [r for r in rows if r.get("timestamp", "").startswith(month)]

    total = sum(float(r.get("cost_usd", 0)) for r in rows)
    by_model = {}
    for r in rows:
        model = r.get("model", "unknown")
        by_model[model] = by_model.get(model, 0) + float(r.get("cost_usd", 0))

    report = {
        "period": month or "all_time",
        "total_generations": len(rows),
        "total_cost_usd": round(total, 4),
        "by_model": {k: round(v, 4) for k, v in sorted(by_model.items(), key=lambda x: -x[1])},
        "avg_cost_per_generation": round(total / len(rows), 4) if rows else 0,
    }

    if competitive:
        videos_produced = len(set(r.get("output_path", "") for r in rows if r.get("output_path")))
        report["competitive"] = {
            "poptech_total": round(total, 2),
            "higgsfield_equivalent": COMPETITOR_PRICING["higgsfield"]["monthly_sub"],
            "arcads_equivalent": COMPETITOR_PRICING["arcads"]["monthly_sub"] + videos_produced * COMPETITOR_PRICING["arcads"]["per_video"],
            "savings_vs_higgsfield": round(COMPETITOR_PRICING["higgsfield"]["monthly_sub"] - total, 2),
            "savings_vs_arcads": round(COMPETITOR_PRICING["arcads"]["monthly_sub"] + videos_produced * 10 - total, 2),
            "videos_produced": videos_produced,
        }

    return report


def print_report(report, as_json=False):
    if as_json:
        print(json.dumps(report, indent=2))
        return

    print(f"\n  PopTech Cinema Studio — Cost Report ({report.get('period', 'all_time')})\n")
    print(f"  Total generations: {report['total_generations']}")
    print(f"  Total cost: ${report['total_cost_usd']:.2f}")
    print(f"  Avg cost/generation: ${report['avg_cost_per_generation']:.4f}")
    print(f"\n  By model:")
    for model, cost in report.get("by_model", {}).items():
        print(f"    {model:<25s} ${cost:.4f}")

    if "competitive" in report:
        comp = report["competitive"]
        print(f"\n  Competitive comparison ({comp['videos_produced']} videos):")
        print(f"    PopTech:     ${comp['poptech_total']:.2f}")
        print(f"    Higgsfield:  ${comp['higgsfield_equivalent']:.2f}/mo")
        print(f"    Arcads:      ${comp['arcads_equivalent']:.2f}/mo + ${comp['videos_produced'] * 10}/videos")
        print(f"    Savings vs Higgsfield: ${comp['savings_vs_higgsfield']:.2f}")
        print(f"    Savings vs Arcads:     ${comp['savings_vs_arcads']:.2f}")


def main():
    parser = argparse.ArgumentParser(description="PopTech Cost Report Generator")
    parser.add_argument("--month", help="Month to report (YYYY-MM)")
    parser.add_argument("--competitive", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = generate_report(args.month, args.competitive)
    if report:
        print_report(report, args.json)


if __name__ == "__main__":
    main()
