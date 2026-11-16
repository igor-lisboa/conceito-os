"""Code health for a junior developer: size, nesting and documentation of the code.

Usage (from the project root):
    python scripts/audit/code_health.py              # report only
    python scripts/audit/code_health.py --strict     # exit 1 if any finding is over the limit
    python scripts/audit/code_health.py --coverage   # also run the tests under coverage (slow)

Checks production code (not migrations, not tests):
- functions longer than 50 lines
- nesting deeper than 4 levels of if/for/while/with/try
- files longer than 400 lines
- public functions and classes without a docstring in the domain and application layers
Also runs ruff's complexity check (C901, max 10) when ruff is available.
"""

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY_DIRS = ["apps", "api", "config", "scripts"]
MAX_FUNCTION_LINES = 50
MAX_NESTING = 4
MAX_FILE_LINES = 400
DOCSTRING_LAYERS = ("domain", "application")
NESTING_NODES = (ast.If, ast.For, ast.While, ast.With, ast.Try)


def production_files():
    for name in PY_DIRS:
        for path in (ROOT / name).rglob("*.py"):
            parts = set(path.parts)
            if "migrations" in parts or "tests" in parts or "__pycache__" in parts or ".venv" in parts:
                continue
            yield path


def depth(node, level=0):
    deepest = level
    for child in ast.iter_child_nodes(node):
        step = level + 1 if isinstance(child, NESTING_NODES) else level
        deepest = max(deepest, depth(child, step))
    return deepest


def check_file(path, findings):
    rel = path.relative_to(ROOT).as_posix()
    source = path.read_text(encoding="utf-8")
    lines = len(source.splitlines())
    if lines > MAX_FILE_LINES:
        findings["file length"].append(f"{rel}: {lines} lines (limit {MAX_FILE_LINES})")
    tree = ast.parse(source)
    in_docstring_layer = any(layer in path.parts for layer in DOCSTRING_LAYERS)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            size = node.end_lineno - node.lineno + 1
            if size > MAX_FUNCTION_LINES:
                findings["function length"].append(f"{rel}:{node.lineno} {node.name}: {size} lines")
            if depth(node) > MAX_NESTING:
                findings["nesting"].append(f"{rel}:{node.lineno} {node.name}: nested deeper than {MAX_NESTING}")
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and in_docstring_layer:
            if not node.name.startswith("_") and ast.get_docstring(node) is None:
                findings["missing docstring"].append(f"{rel}:{node.lineno} {node.name}")


def ruff_complexity():
    command = [
        sys.executable, "-m", "ruff", "check", "--select", "C901",
        "--config", "lint.mccabe.max-complexity=10", *PY_DIRS,
    ]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    return result.stdout.strip() or result.stderr.strip()


def main(strict, with_coverage):
    findings = {key: [] for key in ("file length", "function length", "nesting", "missing docstring")}
    for path in production_files():
        check_file(path, findings)

    over_limit = 0
    for key, items in findings.items():
        print(f"\n{key} ({len(items)})")
        for item in items[:40]:
            print(f"  - {item}")
        if len(items) > 40:
            print(f"  ... and {len(items) - 40} more")
        if key != "missing docstring":
            over_limit += len(items)

    print("\nComplexity (ruff C901, max 10):")
    print(ruff_complexity() or "  none over the limit")

    if with_coverage:
        omit = "--omit=*/tests/*,*/migrations/*"
        subprocess.run([sys.executable, "-m", "coverage", "run", "--source=apps", omit, "manage.py", "test",
                        "--settings=config.settings.test"], cwd=ROOT)
        subprocess.run([sys.executable, "-m", "coverage", "report", omit], cwd=ROOT)

    return 1 if (strict and over_limit) else 0


if __name__ == "__main__":
    sys.exit(main("--strict" in sys.argv, "--coverage" in sys.argv))
