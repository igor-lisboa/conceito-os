"""Where the project stands: open debt, open decisions, unmerged branches.

Usage (from the project root):
    python scripts/audit/project_status.py

Reads docs/technical-debt.md and specs/planning/risks-open-decisions.md. Prints what is
still open, and flags decisions listed as open that the Decided section already settles.
Standard library only; git is called only for the branch list.
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TD_DOC = ROOT / "docs" / "technical-debt.md"
DECISIONS = ROOT / "specs" / "planning" / "risks-open-decisions.md"
ROW = re.compile(r"^\| ((?:TD|D|PD)-\w+)[ |]")


def sections(text):
    """Map each level-2 heading to the text under it."""
    found = {}
    for part in re.split(r"^## ", text, flags=re.MULTILINE)[1:]:
        title, _, body = part.partition("\n")
        found[title.strip()] = body
    return found


def ids_in(body):
    matches = (ROW.match(line) for line in body.splitlines())
    return [match.group(1) for match in matches if match]


def debt_report():
    parts = sections(TD_DOC.read_text(encoding="utf-8"))
    print("Open technical debt by priority:")
    for title, body in parts.items():
        if not title.startswith(("P0", "P1", "P2", "P3")):
            continue
        rows = [line for line in body.splitlines() if ROW.match(line)]
        partly = [row for row in rows if "[done" in row]
        print(f"  {title.split(':')[0]}: {len(rows)} listed, {len(partly)} with a [done ...] note")
        for row in rows:
            status = "has a [done ...] note" if "[done" in row else "open"
            print(f"      {ROW.match(row).group(1)}: {status}")
    print(f"  Paid rows: {len(ids_in(parts.get('Paid', '')))}")


def decisions_report():
    parts = sections(DECISIONS.read_text(encoding="utf-8"))
    open_ids = ids_in(parts.get("Open decisions", ""))
    decided_ids = ids_in(parts.get("Decided", ""))
    stale = sorted(set(open_ids) & set(decided_ids))
    print(f"\nOpen decisions listed: {len(open_ids)}; decided section: {len(decided_ids)}")
    if stale:
        print("  Listed as open but already decided (update the open table):")
        for decision in stale:
            print(f"    - {decision}")


def branch_report():
    merged = subprocess.run(["git", "branch", "--no-merged", "main"], cwd=ROOT, capture_output=True, text=True)
    current = subprocess.run(["git", "branch", "--show-current"], cwd=ROOT, capture_output=True, text=True)
    print(f"\nCurrent branch: {current.stdout.strip() or 'unknown'}")
    branches = [line.strip().lstrip("* ") for line in merged.stdout.splitlines() if line.strip()]
    print(f"Branches not merged into main ({len(branches)}):")
    for branch in branches:
        print(f"  - {branch}")


if __name__ == "__main__":
    debt_report()
    decisions_report()
    branch_report()
    sys.exit(0)
