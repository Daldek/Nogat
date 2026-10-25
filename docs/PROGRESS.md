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
| Generated `AGENTS.md` (HUB-4.3) | done | `uv run scripts/ecosystem.py agents` from the `routes` of the registry (HUB-2.9, ECO-052), `agents --check` in the gate; the guide links name `main`, so they resolve once each project is merged there (IMGWTools after the rename of `master`) |
| `nogat` package (HUB §7) | planned | |
| Adoption in the projects | in progress | phases 2 to 4 on the projects' branches, table at the end of ADOPTION_PLAN; data output: IMGWTools done, Kartograf in progress, Retman half done, Hydraulik done on its branch, Archiwista waits; nothing is pushed, so Retman's pin of IMGWTools is a local commit (plan step 7) |

## Next

1. Data output in the projects, following `docs/plans/2026-10-24-data-output.md`
   (each project in its own session, DEV-3.4): Kartograf's plain mode and its
   documents, then Retman's Kartograf calls and Archiwista, then the
   integration check (record it in the plan's Results) and the first release
   set. DEV-10.6 now falls due for Hydrolog (`hydrolog.testing`: Hydraulik
   reads its hydrograph tables), and for the files the new `file` edges read
   (the PMAXTP document of IMGWTools, the GeoTIFFs of Kartograf). When a tool
   renames a command, change its `routes` and run `agents` (CLAUDE.md).
2. The author pushes producers before consumers (IMGWTools, Kartograf,
   Hydrolog, then Retman, Archiwista, Hydraulik; plan step 7), so that Retman's
   pin `a304521` exists on GitHub; consumers re-pin after a producer's last
   rewrite.
3. Hydrograf's registry entry waits for its `chore/nogat-2.1` (its PROGRESS):
   `backend/requirements.txt` leaves `python_manifests` with the uv step, and
   `uses` of Kartograf changes after its migration.
4. Publish 2.1 to `main` with the author (ADOPTION_PLAN 0.3, 0.4).

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
