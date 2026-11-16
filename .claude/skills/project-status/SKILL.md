---
name: project-status
description: Summarize where the project stands: open technical debt by priority, open decisions (and stale ones already decided), and branches not yet merged to main. Use at the start of a session, or when asked "what is pending?" or "what is next?".
model: haiku
effort: low
---

# Project status

## Steps

1. From the project root, run:
   `./.venv/Scripts/python.exe scripts/audit/project_status.py`
2. Answer in this order, using the numbers printed:
   - Open debt: count per priority (P0 first). P0 items are external work or are blocked
     (see `docs/technical-debt.md`); say so, do not treat them as code tasks.
   - Open decisions: the count, plus any listed as open that the Decided section settles.
     Those are stale rows and must be fixed in `specs/planning/risks-open-decisions.md`.
   - Branches not merged into main, and which one is checked out.
3. Name the next code task only if one is unblocked. Otherwise say that nothing unblocked
   is left in P0 or P1, and ask which later-phase item to take. Later-phase work is not
   started without the user's go-ahead (CLAUDE.md, phases).

## Notes

- A `[done ...]` note on a debt row means part of the item is done. It does not close it.
- "Paid rows" is the count of rows in the Paid table, which is a history, not a to-do list.
