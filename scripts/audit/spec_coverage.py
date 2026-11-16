"""Requirement traceability: which spec IDs exist, which the code cites, and whether evidence is real.

Usage (from the project root):
    python scripts/audit/spec_coverage.py            # report only
    python scripts/audit/spec_coverage.py --strict   # exit 1 if there are errors

Standard library only, so it runs on any machine without the virtualenv.
Errors: duplicate IDs, a module marked `implemented` without Evidence, Evidence paths that
do not exist. Warnings: a cited ID the specs do not declare, `[x]` boxes without Evidence,
partial status without Evidence. Info: declared IDs that no code, test or doc cites.
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC_DIR = ROOT / "specs"
DECLARED = re.compile(r"\*\*([A-Z]{2,4}-\d{3})\b")  # also "**NAV-002 Mobile**"
ANY_ID = re.compile(r"\b([A-Z]{2,4}-\d{3})\b")
EVIDENCE_PATH = re.compile(r"`((?:apps|web|api|config|scripts|docs|specs)/[^`\s]+)`")
CITING_DIRS = ["apps", "web", "api", "config", "scripts", "docs", "README.md"]
SKIP_PARTS = {"migrations", "__pycache__", "CHANGELOG.md"}


def spec_files():
    for path in sorted(SPEC_DIR.rglob("*.md")):
        if "_templates" not in path.parts and path.name not in SKIP_PARTS:
            yield path


def front_matter(text):
    if not text.startswith("---"):
        return {}
    block = text.split("---", 2)[1]
    return {k.strip(): v.strip() for k, _, v in (line.partition(":") for line in block.splitlines()) if k.strip()}


def evidence_section(text):
    match = re.search(r"^## Evidence\s*$(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else None


def citing_files():
    for name in CITING_DIRS:
        base = ROOT / name
        if base.is_file():
            yield base
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".html", ".md", ".po"} and not (SKIP_PARTS & set(path.parts)):
                yield path


def check_spec_file(path, declared, errors, warnings):
    """Record the IDs a spec declares, and check its status and Evidence."""
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT).as_posix()
    for req_id in DECLARED.findall(text):
        declared[req_id].append(rel)

    status = front_matter(text).get("status", "")
    evidence = evidence_section(text)
    if status.startswith(("implemented", "partially")):
        if evidence is None:
            level = errors if status == "implemented" else warnings
            level.append(f"{rel}: status '{status}' but no '## Evidence' section")
        else:
            for ev_path in EVIDENCE_PATH.findall(evidence):
                if not (ROOT / ev_path).exists():
                    errors.append(f"{rel}: Evidence path does not exist: {ev_path}")
    if re.search(r"^- \[x\]", text, re.MULTILINE) and evidence is None:
        warnings.append(f"{rel}: has checked boxes '[x]' but no Evidence section")


def find_citations():
    """Map each requirement-looking ID to the files that mention it outside specs."""
    cited = defaultdict(set)
    for path in citing_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for req_id in set(ANY_ID.findall(text)):
            cited[req_id].add(path.relative_to(ROOT).as_posix())
    return cited


def print_report(declared, cited, untraced, errors, warnings):
    print(f"Declared requirement IDs: {len(declared)}")
    print(f"Cited by code, tests or docs: {sum(1 for r in declared if r in cited)}")
    print("\nNot cited anywhere outside specs (traceability gap, by prefix):")
    for prefix in sorted(untraced):
        print(f"  {prefix}: {len(untraced[prefix])}  e.g. {', '.join(sorted(untraced[prefix])[:6])}")
    for title, items in (("ERRORS", errors), ("WARNINGS", warnings)):
        print(f"\n{title} ({len(items)})")
        for item in items:
            print(f"  - {item}")


def main(strict):
    errors, warnings = [], []
    declared = defaultdict(list)  # ID -> [file]
    for path in spec_files():
        check_spec_file(path, declared, errors, warnings)

    for req_id, files in declared.items():
        if len(files) > 1:
            errors.append(f"{req_id} is declared in several files: {', '.join(files)}")

    cited = find_citations()
    prefixes = {req_id.split("-")[0] for req_id in declared}
    for req_id in sorted(cited):
        if req_id.split("-")[0] in prefixes and req_id not in declared:
            warnings.append(f"{req_id} is cited in {', '.join(sorted(cited[req_id])[:3])} but not declared in specs")

    untraced = defaultdict(list)
    for req_id in declared:
        if req_id not in cited:
            untraced[req_id.split("-")[0]].append(req_id)

    print_report(declared, cited, untraced, errors, warnings)
    return 1 if (strict and errors) else 0


if __name__ == "__main__":
    sys.exit(main("--strict" in sys.argv))
