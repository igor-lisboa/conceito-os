"""Documentation drift: do docs point at files, settings and test counts that exist?

Usage (from the project root):
    python scripts/audit/doc_code_sync.py            # report only
    python scripts/audit/doc_code_sync.py --strict   # exit 1 if there are errors

Checks README.md, docs/*.md, specs/**/*.md and .claude/**/*.md for:
- backticked repo paths (apps/..., docs/..., ...) that do not exist (error)
- relative markdown links that do not resolve (error)
- environment variable names that appear nowhere in the code or .env.example (warning)
- "N tests" claims that differ from the number of test functions in apps/ (warning;
  the count is approximate: the quality gate prints the exact number)
Standard library only.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH_TOKEN = re.compile(r"`((?:apps|web|api|config|scripts|docs|specs|docker|\.claude)/[\w./-]+)`")
LINK = re.compile(r"\]\(([^)#\s]+)\)")
ENV_NAME = re.compile(
    r"\b(DJANGO_[A-Z_]+|MYSQL_[A-Z_]+|EMAIL_[A-Z_]+|INITIAL_ADMIN_[A-Z_]+|MFA_ENCRYPTION_KEY|SITE_URL)\b"
)
TEST_CLAIM = re.compile(r"\b(\d{2,4}) tests\b")


def doc_files():
    yield ROOT / "README.md"
    yield from sorted((ROOT / "docs").glob("*.md"))
    yield from sorted((ROOT / "specs").rglob("*.md"))
    yield from sorted((ROOT / ".claude").rglob("*.md"))


def code_text():
    chunks = []
    for name in ["apps", "web", "api", "config", "scripts"]:
        for path in (ROOT / name).rglob("*"):
            if path.is_file() and path.suffix in {".py", ".html", ".txt", ".toml", ".yml", ".yaml"}:
                chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
    for extra in [ROOT / ".env.example", ROOT / "docker-compose.yml"]:
        if extra.exists():
            chunks.append(extra.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(chunks)


def actual_test_count():
    return sum(
        path.read_text(encoding="utf-8", errors="ignore").count("def test_")
        for path in (ROOT / "apps").rglob("test*.py")
    )


def check_doc(doc, code, actual_tests, errors, warnings):
    text = doc.read_text(encoding="utf-8")
    rel = doc.relative_to(ROOT).as_posix()
    for token in set(PATH_TOKEN.findall(text)):
        if not any(mark in token for mark in "*<>{}") and not (ROOT / token).exists():
            errors.append(f"{rel}: path does not exist: {token}")
    for target in set(LINK.findall(text)):
        if not target.startswith(("http", "mailto:")) and not (doc.parent / target).exists():
            errors.append(f"{rel}: link does not resolve: {target}")
    for name in set(ENV_NAME.findall(text)):
        if name not in code:
            warnings.append(f"{rel}: variable '{name}' is documented but not in code or .env.example")
    for claim in set(TEST_CLAIM.findall(text)):
        if abs(int(claim) - actual_tests) > max(5, actual_tests * 0.05):
            warnings.append(f"{rel}: says '{claim} tests'; about {actual_tests} test functions exist in apps/ now")


def main(strict):
    errors, warnings = [], []
    code = code_text()
    actual_tests = actual_test_count()
    for doc in doc_files():
        if doc.exists():
            check_doc(doc, code, actual_tests, errors, warnings)

    print(f"Test functions in apps/ (approximate): {actual_tests}")
    for title, items in (("ERRORS", errors), ("WARNINGS", warnings)):
        print(f"\n{title} ({len(items)})")
        for item in items:
            print(f"  - {item}")
    return 1 if (strict and errors) else 0


if __name__ == "__main__":
    sys.exit(main("--strict" in sys.argv))
