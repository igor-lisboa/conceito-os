# Editing specs

You are in `specs/`. These rules apply to every edit here.

- Follow [PROCESS.md](PROCESS.md). Use [_templates/module.md](_templates/module.md) for new modules and add the new file to the index in [README.md](README.md).
- Front matter is mandatory (`id`, `status`, `phase`, `version`, `updated`). On every edit, bump `version` and set `updated` to an absolute date.
- Write specs in English. Requirements use `PREFIX-NNN` and MUST / MUST NOT / SHOULD / MAY, and each one is a single verifiable rule.
- Don't duplicate rules: link to the file that owns them. Use relative links and keep them valid.
- Never set `status` to `implemented` without listed evidence.
- Doubt or conflict → add it to `planning/risks-open-decisions.md` (next `D-NN`) and ask the user; don't decide.
- Anything not in the product owner's source material is marked `PROPOSAL`.
- Every edit ends with a line in [CHANGELOG.md](CHANGELOG.md): `YYYY-MM-DD · file(s) · change · reason`.
- Preserve the substance of the source specification v1.0: refine (clarity, IDs, structure), but don't drop requirements without approval.
