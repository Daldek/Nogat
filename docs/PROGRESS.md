# Progress

## Status

| Component | State | Note |
|---|---|---|
| Standard 2.1 | in progress | not yet published to `main`; tagged `std-2.1` when it is (HUB-6.1) |
| Registry and schema | done | `ecosystem.yaml`, `schemas/ecosystem.schema.json` |
| `validate`, `map`, `deps`, `drift` | done | `scripts/ecosystem.py`, errors by the registry (HUB-4.8) |
| Hub gate and CI | done | `scripts/gate.sh` on `uv.lock`, tests in `tests/` |
| Standard checks | done | `uv run scripts/ecosystem.py standard`, in the gate |
| Contradictions in standard 2.1 | done | ECO-042 to ECO-049 and consistency fixes |
| Canonical agent-interface schemas | done | `schemas/agent/`, contract tests (ECO-050) |
| Data-output convention (ECO-051) | done in Nogat | DEV §19, AGI-3.4 and related rules, store markers in the registry, plan `docs/plans/2026-10-24-data-output.md` |
| Generated `AGENTS.md` (HUB-4.3) | planned | routing table with links |
| `nogat` package (HUB §7) | planned | |
| Adoption in the projects | planned | ADOPTION_PLAN phases 1 to 6; data output: steps 2 to 8 of its plan |

## Next

1. Generated Nogat `AGENTS.md` (HUB-4.3): routing table with links.
2. Data output in the projects, following `docs/plans/2026-10-24-data-output.md`
   (each project in its own session, DEV-3.4): Kartograf and IMGWTools, then
   Archiwista, Retman and the Hydrolog documents, the integration check
   (record it in the plan's Results) and the first release set.
3. Publish 2.1 to `main` with the author (ADOPTION_PLAN 0.3, 0.4).

## Open questions

- Hydraulik's registry entry declares a CLI and package that are not
  committed (code in an uncommitted worktree): commit it, or mark the entry
  `research` until then?
- Publishing 2.1 to `main` (and its tag) and replacing the v1 `templates/`
  and `configs/` (root-owned files).
- The plans in `docs/plans/` predate DEV-17.4's `Approved:` line: add it to
  the ones the author approved.
- Contribution files (`SECURITY.md`, `CONTRIBUTING.md`, `docs/CLA.md`,
  `CONTRIBUTORS.md`, DEV-13.7, DEV-16.2) are listed under Deviations in
  `CLAUDE.md`, but they are a gap, not a deliberate deviation: move the entry
  here (ADOPTION_PLAN 0.6), or adapt Archiwista's files and write
  `SECURITY.md` (CLA text needs the author's approval; private vulnerability
  reporting is a GitHub setting)?
- Merge order into `develop`: `fix/hub-gaps` first, then `feature/data-output`
  (cut from `fix/hub-gaps`); `develop` lacks the 2.1 fixes, the standard
  checks and this file. Both merges need the author's approval (DEV-3.3).
