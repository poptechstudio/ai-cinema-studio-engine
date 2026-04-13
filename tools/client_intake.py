"""
PopTech Cinema Studio — Client Self-Service Intake
Task 5.4: Brief -> automated production routing.

Usage:
  python tools/client_intake.py --create --client "Acme Corp" --project "Product Launch" --format cinematic
  python tools/client_intake.py --list                      # List pending briefs
  python tools/client_intake.py --route BRIEF_ID            # Route to N8N workflow
  python tools/client_intake.py --estimate BRIEF_ID         # Estimate cost before routing

Notion Integration:
  Creates project page in Cinema DB ($NOTION_DB_ID)
  Sets status to "Queued" for CTO review before production starts
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
BRIEFS_DIR = SCRIPT_DIR.parent / "briefs"
NOTION_DB_ID = os.environ.get("NOTION_DB_ID", "")

# Format -> workflow mapping
FORMAT_WORKFLOWS = {
    "cinematic": {"workflow": "cinematic-commercial-production", "template": "PopTech", "avg_cost_per_min": 6.0},
    "documentary": {"workflow": "documentary-production", "template": "Generic", "avg_cost_per_min": 10.0},
    "anime": {"workflow": "anime-production", "template": "Generic", "avg_cost_per_min": 3.0},
    "custom": {"workflow": "cinematic-commercial-production", "template": "Generic", "avg_cost_per_min": 8.0},
}


def create_brief(client: str, project: str, format: str, duration_sec: int = 30,
                 description: str = "", budget: float = None, platforms: list = None):
    BRIEFS_DIR.mkdir(parents=True, exist_ok=True)

    brief_id = f"BR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    workflow = FORMAT_WORKFLOWS.get(format, FORMAT_WORKFLOWS["custom"])

    brief = {
        "brief_id": brief_id,
        "client": client,
        "project_name": project,
        "format": format,
        "description": description,
        "target_duration_sec": duration_sec,
        "budget_ceiling_usd": budget,
        "platforms": platforms or ["youtube", "instagram_reels", "tiktok"],
        "workflow": workflow["workflow"],
        "remotion_template": workflow["template"],
        "estimated_cost": round(workflow["avg_cost_per_min"] * duration_sec / 60, 2),
        "status": "draft",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "notion_db_id": NOTION_DB_ID,
        "approval_gates": {
            "cto_review": False,
            "client_brief_approved": False,
            "budget_approved": False,
        },
    }

    brief_path = BRIEFS_DIR / f"{brief_id}.json"
    with open(brief_path, "w") as f:
        json.dump(brief, f, indent=2)

    print(f"Brief created: {brief_id}")
    print(f"  Client: {client}")
    print(f"  Project: {project}")
    print(f"  Format: {format} -> workflow: {workflow['workflow']}")
    print(f"  Template: {workflow['template']}")
    print(f"  Duration: {duration_sec}s")
    print(f"  Estimated cost: ${brief['estimated_cost']:.2f}")
    print(f"  Saved to: {brief_path}")
    print(f"\n  Next: CTO reviews brief, then 'python tools/client_intake.py --route {brief_id}'")
    return brief


def list_briefs():
    if not BRIEFS_DIR.exists():
        print("No briefs directory.")
        return

    briefs = sorted(BRIEFS_DIR.glob("BR-*.json"), reverse=True)
    if not briefs:
        print("No briefs found.")
        return

    print(f"\nClient Briefs ({len(briefs)}):\n")
    print(f"  {'ID':<25s} {'Client':<20s} {'Project':<25s} {'Format':<12s} {'Est $':<8s} {'Status'}")
    print("  " + "-" * 100)
    for bp in briefs:
        with open(bp) as f:
            b = json.load(f)
        print(f"  {b['brief_id']:<25s} {b['client']:<20s} {b['project_name']:<25s} {b['format']:<12s} ${b['estimated_cost']:<7.2f} {b['status']}")


def estimate_brief(brief_id: str):
    brief_path = BRIEFS_DIR / f"{brief_id}.json"
    if not brief_path.exists():
        print(f"Brief not found: {brief_id}")
        return

    with open(brief_path) as f:
        brief = json.load(f)

    wf = FORMAT_WORKFLOWS.get(brief["format"], FORMAT_WORKFLOWS["custom"])
    duration_min = brief["target_duration_sec"] / 60

    print(f"\nCost Estimate: {brief_id}\n")
    print(f"  Format: {brief['format']}")
    print(f"  Duration: {brief['target_duration_sec']}s ({duration_min:.1f} min)")
    print(f"  Workflow: {wf['workflow']}")
    print(f"\n  Estimated breakdown:")
    print(f"    Video generation (Seedance):  ${duration_min * 3:.2f}")
    print(f"    Lip-sync (LatentSync):        ${0.26 * (brief['target_duration_sec'] // 15 + 1):.2f}")
    print(f"    Voice (ElevenLabs):            ${0.01:.2f}")
    print(f"    Color grading (local):         $0.00")
    print(f"    Remotion compositing (local):  $0.00")
    print(f"    Platform encoding (local):     $0.00")
    print(f"  {'─' * 40}")
    print(f"    TOTAL ESTIMATE:                ${brief['estimated_cost']:.2f}")
    print(f"\n  Competitive equivalent:")
    print(f"    Higgsfield: ~${200 * duration_min:.2f}/mo allocation")
    print(f"    Arcads: ~${10 * (brief['target_duration_sec'] // 30 + 1):.2f}")


def route_brief(brief_id: str):
    brief_path = BRIEFS_DIR / f"{brief_id}.json"
    if not brief_path.exists():
        print(f"Brief not found: {brief_id}")
        return

    with open(brief_path) as f:
        brief = json.load(f)

    if not brief["approval_gates"]["cto_review"]:
        print(f"BLOCKED: CTO review required before routing.")
        print(f"  Approve: edit {brief_path} and set cto_review: true")
        return

    brief["status"] = "routed"
    with open(brief_path, "w") as f:
        json.dump(brief, f, indent=2)

    print(f"Brief {brief_id} routed to N8N workflow: {brief['workflow']}")
    print(f"  STUB: In production, creates Notion page in Cinema DB and triggers N8N workflow")


def main():
    parser = argparse.ArgumentParser(description="PopTech Client Self-Service Intake")
    parser.add_argument("--create", action="store_true")
    parser.add_argument("--client", help="Client name")
    parser.add_argument("--project", help="Project name")
    parser.add_argument("--format", choices=list(FORMAT_WORKFLOWS.keys()), default="cinematic")
    parser.add_argument("--duration", type=int, default=30, help="Target duration (seconds)")
    parser.add_argument("--description", default="")
    parser.add_argument("--budget", type=float)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--estimate", help="Brief ID to estimate")
    parser.add_argument("--route", help="Brief ID to route to N8N")
    args = parser.parse_args()

    if args.create and args.client and args.project:
        create_brief(args.client, args.project, args.format, args.duration, args.description, args.budget)
    elif args.list:
        list_briefs()
    elif args.estimate:
        estimate_brief(args.estimate)
    elif args.route:
        route_brief(args.route)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
