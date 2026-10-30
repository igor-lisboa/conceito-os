---
name: close-debt
description: Mark a technical debt item (TD-NN) as done in the project. Moves it to the Paid table with real evidence, updates the module spec status and Evidence, and adds the changelog line. Use when the user says a TD item is finished, or asks to record progress against docs/technical-debt.md.
---

# Close a debt item

Input: the item ID, for example `TD-03`. If the user gives no ID, list the open items from `docs/technical-debt.md` and ask which one.

## Before changing any document

1. **Check the work is really done.** Find the tests or files that prove it. Run them. If they fail, stop: the item is not closed.
   - Find evidence: search `apps/` for the feature (for example `grep -rln "invite_member" apps`).
   - Run the proving tests: `./.venv/Scripts/python.exe manage.py test <module> --settings=config.settings.test`
   - If there is no test, say so. Do not close the item without evidence. Offer to write the test.

2. **Know the priority and the spec reference.** Read the row of the item in `docs/technical-debt.md`. Note the spec IDs it pays for (for example AUTH-011).

## Update, in this order

1. `docs/technical-debt.md`
   - In the priority table, put `[done: <short note>]` at the start of the debt cell. If only part is done, write `[done for ...; ... still open]` and say what is open.
   - In the **Paid** table, add a row: item, date (today), and the test files as evidence.
   - If the item created a new shortcut, add it to "Known shortcuts" with the next `TD-SNn` number.

2. The module spec in `specs/modules/` that owns the spec IDs
   - Set `status` to `partially-implemented` or `implemented`. Only use `implemented` when every requirement of that module is done.
   - Add the test paths under `## Evidence`.

3. `specs/CHANGELOG.md`: one line at the top: date, files, what was done, reason.

4. `docs/phase-1-decisions.md`: only if the work made a new decision. Add `PD-NN` with status, reason and location.

## Report

Item, what was proven (test names and counts), files changed, and what remains open for that item.
