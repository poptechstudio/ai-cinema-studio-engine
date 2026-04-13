"""
PopTech Cinema Studio — Performance Benchmarking Framework
Task 5.3: Collect quality metrics, generation times, and costs per engine.

Usage:
  python tools/benchmark.py --collect                    # Collect from cost_log.csv
  python tools/benchmark.py --report                     # Print benchmark report
  python tools/benchmark.py --report --competitive       # Include Higgsfield/Arcads comparison
  python tools/benchmark.py --add --engine seedance_2.0 --duration 5 --cost 0.50 --quality 8 --time 45
"""

import argparse
import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
COST_LOG = SCRIPT_DIR / "cost_log.csv"
BENCHMARK_DB = SCRIPT_DIR / "benchmark_data.json"

COMPETITOR_MONTHLY = {"higgsfield": 200, "arcads": 220}


def load_benchmarks() -> list:
    if BENCHMARK_DB.exists():
        with open(BENCHMARK_DB) as f:
            return json.load(f)
    return []


def save_benchmarks(data: list):
    with open(BENCHMARK_DB, "w") as f:
        json.dump(data, f, indent=2)


def add_benchmark(engine: str, duration: float, cost: float, quality: float,
                  generation_time: float, resolution: str = "720p", notes: str = ""):
    benchmarks = load_benchmarks()
    entry = {
        "engine": engine,
        "duration_sec": duration,
        "cost_usd": cost,
        "quality_score": quality,
        "generation_time_sec": generation_time,
        "resolution": resolution,
        "cost_per_sec": round(cost / duration, 4) if duration > 0 else 0,
        "notes": notes,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    benchmarks.append(entry)
    save_benchmarks(benchmarks)
    print(f"Added: {engine} — {duration}s, ${cost:.2f}, quality {quality}/10, {generation_time}s gen time")


def collect_from_costlog():
    """Import data from cost_log.csv into benchmark database."""
    if not COST_LOG.exists():
        print("No cost_log.csv found.")
        return

    benchmarks = load_benchmarks()
    existing_count = len(benchmarks)

    with open(COST_LOG) as f:
        for row in csv.DictReader(f):
            entry = {
                "engine": row.get("model", "unknown"),
                "duration_sec": float(row.get("duration_sec", 0)),
                "cost_usd": float(row.get("cost_usd", 0)),
                "quality_score": float(row.get("quality_rating", 0)) if row.get("quality_rating") else None,
                "generation_time_sec": None,
                "resolution": row.get("aspect_ratio", ""),
                "cost_per_sec": 0,
                "notes": f"from cost_log: {row.get('output_path', '')}",
                "timestamp": row.get("timestamp", ""),
            }
            if entry["duration_sec"] > 0:
                entry["cost_per_sec"] = round(entry["cost_usd"] / entry["duration_sec"], 4)
            benchmarks.append(entry)

    save_benchmarks(benchmarks)
    print(f"Imported {len(benchmarks) - existing_count} entries from cost_log.csv")


def generate_report(competitive: bool = False):
    benchmarks = load_benchmarks()
    if not benchmarks:
        print("No benchmark data. Run --collect or --add first.")
        return

    # Aggregate by engine
    engines = {}
    for b in benchmarks:
        e = b["engine"]
        if e not in engines:
            engines[e] = {"runs": 0, "total_cost": 0, "total_duration": 0,
                          "total_gen_time": 0, "quality_scores": []}
        engines[e]["runs"] += 1
        engines[e]["total_cost"] += b.get("cost_usd", 0)
        engines[e]["total_duration"] += b.get("duration_sec", 0)
        if b.get("generation_time_sec"):
            engines[e]["total_gen_time"] += b["generation_time_sec"]
        if b.get("quality_score"):
            engines[e]["quality_scores"].append(b["quality_score"])

    print(f"\n  PopTech Engine Benchmark Report ({len(benchmarks)} data points)\n")
    print(f"  {'Engine':<25s} {'Runs':<6s} {'Avg $/sec':<10s} {'Avg Quality':<12s} {'Total $'}")
    print("  " + "-" * 70)
    for name, data in sorted(engines.items()):
        avg_cost = data["total_cost"] / data["total_duration"] if data["total_duration"] > 0 else 0
        avg_quality = sum(data["quality_scores"]) / len(data["quality_scores"]) if data["quality_scores"] else 0
        print(f"  {name:<25s} {data['runs']:<6d} ${avg_cost:<9.4f} {avg_quality:<12.1f} ${data['total_cost']:.2f}")

    if competitive:
        total_cost = sum(e["total_cost"] for e in engines.values())
        total_min = sum(e["total_duration"] for e in engines.values()) / 60
        print(f"\n  Competitive Comparison:")
        print(f"    PopTech total: ${total_cost:.2f} ({total_min:.1f} min produced)")
        for comp, monthly in COMPETITOR_MONTHLY.items():
            print(f"    {comp.title()}: ${monthly}/mo equivalent")
            if total_cost > 0:
                savings_pct = ((monthly - total_cost) / monthly) * 100
                print(f"    Savings: ${monthly - total_cost:.2f} ({savings_pct:.0f}%)")


def main():
    parser = argparse.ArgumentParser(description="PopTech Performance Benchmarking")
    parser.add_argument("--collect", action="store_true")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--competitive", action="store_true")
    parser.add_argument("--add", action="store_true")
    parser.add_argument("--engine", help="Engine name")
    parser.add_argument("--duration", type=float)
    parser.add_argument("--cost", type=float)
    parser.add_argument("--quality", type=float)
    parser.add_argument("--time", type=float, help="Generation time in seconds")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.collect:
        collect_from_costlog()
    elif args.report:
        generate_report(args.competitive)
    elif args.add and args.engine:
        add_benchmark(args.engine, args.duration or 0, args.cost or 0,
                      args.quality or 0, args.time or 0)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
