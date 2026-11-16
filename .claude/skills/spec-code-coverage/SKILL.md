---
name: spec-code-coverage
description: Check that every requirement ID in specs/ is traceable to code and tests, and that every "implemented" claim has real evidence. Use before a release, after a batch of features, or when asked "are we covering all the rules?".
model: haiku
effort: low
---

# Spec to code coverage

The script does the measuring. Do not re-check it by hand.

## Steps

1. From the project root, run:
   `./.venv/Scripts/python.exe scripts/audit/spec_coverage.py`
2. Report the numbers exactly as printed: declared IDs, cited IDs, and the gap per prefix.
3. Report every ERROR and WARNING with its file. Do not fix anything.
4. For each ERROR, say which spec or test to change. Put a spec-versus-code disagreement
   in the answer and ask which side is right (see CLAUDE.md, rule 4). Never resolve it silently.

## What the results mean

- **ERROR, `implemented` without Evidence**: the status is a claim. Either add Evidence with
  real test paths, or lower the status to `partially-implemented`.
- **ERROR, Evidence path does not exist**: the test or code moved or was never written.
- **WARNING, cited but not declared**: an ID is used in code with no spec line. Add it to the
  spec, or fix the code comment. IDs are never renumbered (PROCESS.md rule 4).
- **Untraced IDs** are not failures. They show where a requirement has no test or code
  citation yet. Name the prefixes with the most gaps; do not list all of them.

## Options

- `--strict` exits 1 when there are errors. Use it in a pre-release gate.
