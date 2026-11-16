---
name: doc-code-sync
description: Check that README, docs/ and specs/ still match the code: file paths, links, environment variable names and test counts. Use after a refactor, before a deploy, or when a document feels out of date.
model: haiku
effort: low
---

# Documentation against code

## Steps

1. From the project root, run:
   `./.venv/Scripts/python.exe scripts/audit/doc_code_sync.py`
2. Report the ERRORS first (paths and links that do not exist), then the WARNINGS.
3. Do not edit the documents. Propose the exact line change for each finding, and apply
   it only if the user asks.

## Notes

- A **test count** is approximate. The script counts `def test_` functions in `apps/`. The
  exact number comes from the quality gate (`manage.py test`). When a document has a stale
  count, the fix is to remove the number or use the exact one from the gate run.
- A **variable warning** means a name is documented but appears nowhere in the code or
  `.env.example`. It may be an old name, or a value that should be added to `.env.example`.
- A **path error** inside a spec may be intentional (for example a planned folder). Say
  so and ask, rather than deleting it.
