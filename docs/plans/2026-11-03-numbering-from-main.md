# Plan: numbers count from `main`

Approved: 2026-11-03 (the author; the legacy directory is `shared-2026-01`)

Requirements: HUB-6.1, HUB-5.2, REL-1.1, REL-1.3, AGI-4.1, ERR-3, DEV-17.4.

## Goal

The author's rule (2026-11-03): only a repository's `main` fixes a number.
What `develop` and topic branches carry is not binding for a user; a number
that never reached `main` may be renumbered, and is when `main` would
otherwise read illogically. This applies to the version of the standard and
to the document ids `<tool>-<kind>/<n>`.

## Facts

- Nogat's `main` (`c9a2188`, 2025-07-25) holds an unrelated oceanography
  project and no standard; `origin` has no tags. `develop` calls the standard
  2.1 (`standards/README.md:3`, `ecosystem.yaml:7`) and its changelog lists
  only 2.1; `standards/legacy/v1.0/` (added in `d844eb9`, 2026-10-20) archives
  the shared standards of 2026-01-29, which were never on Nogat's `main`.
  Kartograf's and Hydrograf's `main` cite them as `shared/standards`
  (10 and 6 lines); no `main` cites a standard version.
- References to the version on the development branches (`standard 2.1`,
  `Nogat 2.1`, `std-2.1`, `nogat-2.1`, `standard_version`), lines in files:

  | Project | Ref | Lines | Files |
  |---|---|---|---|
  | Nogat | `develop` | 60 | 18 |
  | Kartograf | `develop` | 25 | 18 |
  | IMGWTools | `slave` | 15 | 7 |
  | Hydrolog | `develop` | 21 | 12 |
  | Hydrograf | `develop` | 29 | 12 |
  | Retman | `develop` | 19 | 10 |
  | Archiwista | `develop` | 16 | 10 |
  | Hydraulik | `feature/sfincs-swmm` | 7 | 6 |

  Each project's `main` has none. `chore/nogat-2.1` branches are merged and
  are history.
- Document ids: on every `main` the only id in code is `kartograf-meta/1`
  (Kartograf v0.7.2, `kartograf/sources/sidecar.py:56`). On the development
  branches every emitted id is `/1` except `archiwista-state/2`
  (Archiwista `src/archiwista/state/export.py:43`, bumped by `7fc98f7`,
  2026-10-26, never on `main`); its reader also accepts the unreleased
  pre-v0.4 format as `archiwista-state/1` (`export.py:41,44,409-420`).
  Every other `/2` or `/3` on those branches is prose about a possible future
  version. Archiwista's own PROGRESS (`docs/PROGRESS.md:55-56`) already plans
  the renumber at its release preparation.

## Decision proposed

A new ECO decision in `standards/DECISIONS.md`, numbers count from `main`:

1. The first standard published to Nogat's `main` is 1.0, tagged `std-1.0`;
   the 2.1 changelog becomes the 1.0 changelog. HUB-6.1 gains: a version
   exists from its tag on `main`; `develop` carries the next version.
2. AGI-4.1 gains: `<n>` increments only past a number released on the
   producer's `main`; a breaking change to an unreleased document keeps its
   number.
3. `standards/legacy/v1.0/` is renamed to `standards/legacy/shared-2026-01/`
   and described as the shared standards that preceded Nogat, so that 1.0
   names one thing.

## Steps (producers first, HUB-5.2)

| # | Project | Change | Verified by |
|---|---|---|---|
| 1 | Nogat | the ECO decision, HUB-6.1 and AGI-4.1 texts; 2.1 to 1.0 in `standards/`, `ecosystem.yaml`, `error_registry.json`, `README.md`, `CLAUDE.md`, the registry tests; the legacy directory renamed; generated `AGENTS.md` and `docs/ECOSYSTEM_MAP.md` regenerated. Dated plans and past CHANGELOG entries keep their text as records | `scripts/gate.sh` (the version check of HUB-6.1) |
| 2 | Kartograf | references and any emitted `standard_version`; on the release-prep branch before v0.8.0 | its gate |
| 3 | IMGWTools | references; the copy of `schemas/agent/` and `error_registry.json` (its B6) taken from `std-1.0` | its gate |
| 4 | Hydrolog, Retman, Hydraulik, Hydrograf | references and emitted `standard_version` | each gate |
| 5 | Archiwista | references; `archiwista-state/2` to `/1`, the reader of the unreleased pre-v0.4 format dropped (or told apart by content), tests `test_state.py:501,507,572,574` | its gate |
| 6 | Nogat | `develop` into `main` and the tag `std-1.0`, both the author's (ADOPTION_PLAN 0.4) | the tag |

Each project's step runs in its own session (DEV-3.4) and lands before that
project's next merge into `main`.

## Open questions

1. Archiwista: drop the import of the pre-v0.4 state format, or keep it and
   tell the formats apart by content? Archiwista has no tag and no `main` on
   `origin` (its local `main` is the initial commit `5578983`); v0.3 and v0.4
   are names of development plans, folded into one release by D2 of the
   projects plan, so no state format has been released.

## Results

Step 1 (2026-11-03, merged into `develop` in `4bb6659`): ECO-056,
amending ECO-004 and ECO-046; HUB-6.1 and AGI-4.1 carry the rule; the
standard is 1.0 in `standards/`, `ecosystem.yaml`, `error_registry.json`,
`CLAUDE.md`, `docs/PROGRESS.md` and the registry tests, with the 2.1
changelog as the 1.0 changelog; `standards/legacy/v1.0/` is
`standards/legacy/shared-2026-01/`; `docs/ECOSYSTEM_MAP.md` regenerated
(`AGENTS.md` and the error tables unchanged). Branch names such as
`chore/nogat-2.1` stay: they name existing refs.

Step 2 (2026-11-03): Kartograf `develop` `4e4445e5`, the commit that freezes
it for 0.8.0, cites the standard as 1.0 (CLAUDE.md, ADR-048 to ADR-058,
PROGRESS, CHANGELOG); its copy of `error_registry.json` comes from
`4bb6659`, so `kartograf._errors.STANDARD_VERSION` is `"1.0"`; gate green
(8,577 passed). Branch names `chore/nogat-2.1` stay.
