# Progress

## Status

| Component | State | Note |
|---|---|---|
| Standard 2.1 | in progress | not yet published to `main`; tagged `std-2.1` when it is (HUB-6.1) |
| Registry and schema | done | `ecosystem.yaml`, `schemas/ecosystem.schema.json`; follows the branches of Kartograf, IMGWTools, Hydrolog and Hydraulik since 2026-10-25 (CHANGELOG); `routes` name the commands of those branches, of Retman and of Archiwista |
| `validate`, `map`, `agents`, `deps`, `drift` | done | `scripts/ecosystem.py`, errors by the registry (HUB-4.8) |
| Hub gate and CI | done | `scripts/gate.sh` on `uv.lock`, tests in `tests/` |
| Standard checks | done | `uv run scripts/ecosystem.py standard`, in the gate |
| Contradictions in standard 2.1 | done | ECO-042 to ECO-049 and consistency fixes |
| Canonical agent-interface schemas | done | `schemas/agent/`, contract tests (ECO-050) |
| Data-output convention (ECO-051) | done in Nogat | DEV §19 and AGI-3.4 and related rules, store markers in the registry, plan `docs/plans/2026-10-24-data-output.md` with the state of every project (Results, 2026-10-25) |
| Integration dry run | done 2026-10-25 | the six heads in one environment: suites, four cross-tool flows, eight failures with their owners and, since the coordinator's decisions (ECO-053: supported range of a pinned producer, tests found from the test file, `<package>.testing`), their follow-ups (`docs/plans/2026-10-25-integration-dry-run.md`); the check of plan step 7 repeats once Kartograf's step 2 is complete |
| Final integration run | done 2026-10-25, fixed | the eight heads in one environment, each member's own gate and eight cross-tool flows; F1 to F8 with their owners and fixing commits, every one fixed but F6, the author's history rewrite (`docs/plans/2026-10-25-final-integration.md`, Fixes). Retman, Hydraulik, Hydrograf and Archiwista are re-pinned to the fixed producer heads (Kartograf `c31ca04c`, IMGWTools `6bd35a4`), each with its full gate (Next 3 of that plan). Hydrograf (`affine<3` until pyflwdir 0.5.13, its ADR-062) and Archiwista (`affine>=3`) are a known incompatible pair, which `deps` reports as a `range_conflict`; a repeat runs them apart |
| Generated `AGENTS.md` (HUB-4.3) | done | `uv run scripts/ecosystem.py agents` from the `routes` of the registry (HUB-2.9, ECO-052), `agents --check` in the gate; the guide links name `main`, so they resolve once each project is merged there (IMGWTools after the rename of `master`) |
| `nogat` package (HUB §7) | planned | |
| Adoption in the projects | in progress | phases 2 to 4 on the projects' branches, table at the end of ADOPTION_PLAN; data output: IMGWTools done, Kartograf in progress, Retman half done, Hydraulik done on its branch, Archiwista waits; nothing is pushed, so Retman's pin of IMGWTools is a local commit (plan step 7) |

## Next

1. Data output in the projects, following `docs/plans/2026-10-24-data-output.md`
   (each project in its own session, DEV-3.4): Kartograf's plain mode and its
   documents, then Retman's Kartograf calls and Archiwista, then the
   integration check (record it in the plan's Results; the dry run of
   2026-10-25 names what fails and who owns it) and the first release
   set. DEV-10.6 now falls due for Hydrolog (`hydrolog.testing`: Hydraulik
   reads its hydrograph tables), and for the files the new `file` edges read
   (the PMAXTP document of IMGWTools, the GeoTIFFs of Kartograf). When a tool
   renames a command, change its `routes` and run `agents` (CLAUDE.md).
2. Repeat the final integration run for the members that changed since it
   (Kartograf, IMGWTools and the four re-pinned consumers), with Hydrograf and
   Archiwista apart and the two flows of F2, and record it in the Results of
   the data-output plan (`docs/plans/2026-10-25-final-integration.md`, Next 3).
3. Publish 2.1 to `main` with the author (ADOPTION_PLAN 0.3, 0.4).
4. Prepare a coherent visual identity for Hydrograf, Archiwista and every
   other ecosystem tool that has or will have a GUI (user request, 2026-10-28).
   Define shared visual guidelines and reusable design assets, with room for
   each tool's identity. Backlog only; design and implementation have not started.

## Open questions

- Hydraulik's code is committed on `feature/sfincs-swmm` (worktree
  `Hydraulik-sfincs`, not merged), and its registry entry lists that branch's
  `pyproject.toml`, which the `Hydraulik` checkout on `develop` lacks until the
  merge (`deps` notes it). Keep `status: research` until the author merges the
  branch and settles the proof of concept, or mark it `active` now?
- The Hydraulik entry has no data source, because the branch has no
  OpenStreetMap access (its roads come from BDOT10k), but its README still
  names OpenStreetMap and ODbL in the data and licensing paragraph: which is
  right?
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
