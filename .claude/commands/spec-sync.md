---
description: Sync specs after a change (specs, checklist and changelog)
argument-hint: "[change description, optional]"
---

Change to reflect in the specs: $ARGUMENTS (if empty, infer it from the recent work in this conversation).

1. Find the affected specs via `specs/README.md`.
2. Update text, requirements (stable IDs), acceptance criteria, `version`, `updated` and status/Evidence based on real facts.
3. Go through the consistency checklist in `specs/PROCESS.md` (states, data model, permissions, screens, roadmap, open decisions).
4. Add a line to `specs/CHANGELOG.md`.
5. If you hit a conflict with a spec or an undecided question, do NOT decide: record it as an open decision and ask.
6. Summarize: files changed, what changed, and what's pending.
