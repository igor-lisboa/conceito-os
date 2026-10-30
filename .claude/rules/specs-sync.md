# Keep specs and implementation in sync

Applies to any work that changes or creates code, database schema, routes, permissions, states, screens or integrations.

**Before:** find the affected specs in `specs/README.md` and read them, together with roles/permissions, states, data model and security. If the requested change contradicts a spec, say so and ask before implementing.

**During:** implement against the spec's acceptance criteria; write tests that cite the IDs (`CRM-004`).

**After (mandatory before saying "done"):**

1. Update the touched specs (text, `version`, `updated`, status, Evidence).
2. Go through the checklist in `specs/PROCESS.md` (states, data model, permissions, screens, roadmap, open decisions).
3. Log it in `specs/CHANGELOG.md`.
4. In the final summary, say which specs changed and why; if none needed to change, say so.

Never leave a spec claiming something the code doesn't do, nor code doing something the spec doesn't describe.
