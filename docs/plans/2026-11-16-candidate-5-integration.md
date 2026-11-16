# Plan: integration run of release set candidate-5

Approved: 2026-11-16 (the author: build the candidate's `pyproject.toml`, its
`uv.lock` and the workflow `verify-candidate`, then run the integration run;
known failures that are not critical are fixed in the next releases)

Requirements: REL-2.5, REL-6.4, REL-6.5, REL-7.1, DEV-10.1, DEV-17.6,
DEV-19.10 to DEV-19.14, ECO-073, ECO-074, ECO-077. Step 4 of the
[first release set](2026-10-20-first-release-set.md), run on this machine;
the repeat that the [final integration run](2026-10-25-final-integration.md)
left open.

## Goal

Before the workflow `verify-candidate` can run on GitHub (it must be on
`main`), show on this machine that the members of candidate-5 work together
at the set's commits: each suite in the candidate's environment, each member
on its own lock, and the flows that cross two tools.

## Decision

The options of the final integration run stand: A, one environment with
every member as a wheel, which is now `uv run scripts/ecosystem.py set
verify` on the candidate's own lock; B, each member's `scripts/gate.sh` on its
own lock; then the flows. The jobs ran as user systemd units with their logs
in files (DEV-17.6): `nogat-candidate5-union`, `nogat-candidate5-gates` and
the repeats `nogat-candidate5-union-{hydrolog,archiwista,obserwator}`, logs
in `~/tmp/nogat-run-2026-11-16/logs/`. User directories (XDG) pointed into
that throwaway area, Python 3.12.15, Linux only; the gates skipped the
commit step (`GATE_COMMIT_RANGE=none`: their commits were checked on entry
to `develop`).

## Steps

1. **Heads.** The set's commits, each fetched from GitHub alone: Kartograf
   `e14bc78`, Obserwator `f4f6a8d`, Hydrolog `3ce7ee8`, Hydrograf `939b55f`,
   Archiwista `800231c`. `set check`: every pin between members matches;
   Retman and Hydraulik, not members, differ.
2. **Environment.** `uv sync --locked` of `release-sets/candidate-5/`:
   127 packages for the three platforms, one version each; the four members
   with a package installed as wheels (each `direct_url.json` names its
   commit); Hydrograf on its own lock in `backend/`.
3. **Suites** (A), **gates** (B), **flows**.

## Results

### Suites in the candidate's environment (`set verify`)

| Member | Environment | Result | Coverage | Time |
|---|---|---|---|---|
| Kartograf | candidate | 8,651 passed | 95.37 % | 481 s |
| Obserwator | candidate | first run 3,325 passed, 152 skipped (no browser); repeat 3,432 passed, 45 skipped | 94.57 % | 471 s |
| Hydrolog | candidate | first run 234 errors (no browser); repeat 8,855 passed | 94.27 % | 765 s |
| Hydrograf | own lock | 2,392 passed | 87.24 % | 175 s |
| Archiwista | candidate | first run 2,732 passed, 2 failed, 293 errors (no browser); repeat 3,024 passed, 3 failed (C2, C3) | 93.68 % | 4,394 s |

The errors of the first run are this machine's: the candidate's Playwright
1.65.2 needs Chromium build 1255 and Firefox build 1572, which were not
installed; the workflow installs them before the suites. After `playwright
install chromium firefox` in the candidate's environment the repeats ran
with them.

### Gates on each member's own lock

| Member | Result | Coverage | Time |
|---|---|---|---|
| Kartograf | GATE OK, 8,651 passed | 95.36 % | 598 s |
| Obserwator | GATE OK, 3,432 passed, 45 skipped | 94.56 % | 568 s |
| Hydrolog | GATE OK, 8,855 passed | 94.27 % | 1,004 s |
| Hydrograf | GATE OK, 2,392 passed | 87.24 % | 198 s |
| Archiwista | stopped at pytest: 3,026 passed, 1 failed (C2) | 93.77 % | 4,464 s |

### Flows

Eight flows, offline (every request refused by a proxy on a closed port),
with the candidate's executables:

| # | Flow | Result |
|---|---|---|
| 1 | Kartograf plain `elevation download --check` while the sheet index cannot be asked (F2 of the final run) | Passes: plain and store `--check` and the plain run exit 11, `ok: false`, `check_failed`, nothing written |
| 2 | `store init` of Kartograf and Obserwator: new, empty, layout without marker; a writer on such a root | Passes: markers written once, `--check` writes nothing, a writer answers `store_unavailable` (exit 8) |
| 3 | Nested stores, both directions | Fails for Obserwator's data root (C1); passes for the raw root and for Kartograf's store |
| 4 | `--root` with `--output-dir`, store-only options with `--output-dir` | Passes: `validation_error`, `exclusive_options` and `store_only_option`, in both producers |
| 5 | Archiwista `doctor` with both producers | Passes: exit 0 with markers, 10 without, 10 for a nested store |
| 6 | Hydrolog `route network --schematic` | Passes: check writes nothing, the run writes the tables and the SVG, a second run `conflict`, `--force` `replaced` |
| 7 | Obserwator `series export` → Hydrolog `stats flood-frequency` | The CSV is read as is; no quantiles, because the fixture series hold fewer than 3 hydrological years (`calculation_error`, by design) |
| 8 | Archiwista `reindex`, `search`, `project-init`, `project-pin`, `project-export` over a `kartograf.testing` store | Passes; `project-export` has no `--check` |

### Known failures, fixed in the next releases

The author's decision of 2026-11-16: none of them blocks the set; each is
fixed in its project's next release.

| # | Where | Cause | Owner |
|---|---|---|---|
| C1 | Kartograf `store init --root`, `--root` and `-o` inside Obserwator's data root: planned as `write`, a Kartograf store is created there, and Obserwator then refuses its own root (`nested_store`, exit 4) | `kartograf/marker.py:75` lists `kartograf-store.json` and `obserwator-store.json`, not `obserwator-data.json` (DEV-19.12); Obserwator's ADR-017 recorded the gap. No existing root is nested: the data root `~/data/obserwator-target/data` holds only its own trees | Kartograf |
| C2 | Archiwista `tests/integration/test_projects_api.py::test_a_project_the_server_writes_is_readable_by_its_folders_group`, in its gate and in the candidate's environment | The test expects `index.sqlite` without group or other bits, which only `cli.main`'s `umask 077` (`cli.py:141`) gives; the test builds the app without it, so under the umask 022 of a systemd unit it fails, under 077 it passes (both environments). A defect of the test, not of the server | Archiwista |
| C3 | Archiwista `tests/e2e/test_station_chart.py::test_an_incomplete_year_is_a_hollow_dot_whose_tooltip_names_the_missing_half[firefox]` and `tests/e2e/test_stations_map.py::test_legend_counter_and_chips_stand_beside_the_map[firefox]` in the candidate's environment | Firefox 159 (Playwright 1.65.2, the set's version) crashes the page (`TargetClosedError: Page crashed`), deterministically; both pass with the Playwright 1.64.0 of Archiwista's own lock, and their Chromium cases pass in both. The set keeps 1.65.2 (the author) | Archiwista |
| C4 | Obserwator's plain plan into another tool's store lists `ATTRIBUTION.txt` as `write` while the run refuses every target (DEV-19.10, DEV-19.11) | — | Obserwator |
| C5 | Obserwator's `no_marker` hint does not name the path (DEV-19.13); Kartograf's `nested_store` error has no `hint` (ERR-5) | — | Obserwator, Kartograf |
| C6 | `archiwista test_unreadable_cached_as_code_and_timeout_not_cached` once (`PreviewTimeoutError`, limit 1 s) in the first run, with the gate beside it on four cores; it passed in the repeat and in the gate | Timing under load | Archiwista |
| C7 | Obserwator `tests/unit/test_agent_guide.py::test_instructions_are_english_and_hold_the_rules_and_the_mode_below_2_kib[read]`, in the gate of its release commit | The MCP instructions carry the path of the test's temporary directory, so a long `TMPDIR` takes them past the 2,048-byte limit (2,050); it fails the same way on `develop` without the release commit and passes with `/tmp` and in a repeat of the gate. A defect of the test | Obserwator |

The findings of the scenario test of 2026-11-15/16 on the Barycz and the
Bóbr (`~/workspace/_e2e/2026-11-15/scenario/REPORT.md`) are also left to the
next releases by the author's decision of 2026-11-16.

### What the run does not show

- macOS, Windows and Python 3.15: the workflow `verify-candidate` runs them
  once it is on `main`.
- `live` tests, Hydrograf's `db` tests, Archiwista's `perf` and `smb` tests,
  any real download.
- Retman and Hydraulik, which join a later set.

## candidate-6 and the releases (2026-11-16)

The author's decisions of 2026-11-16: Kartograf v0.8.0 (the PGW data and the
size-probe fixes merged after its freeze of 2026-11-03 are admitted),
Obserwator v3.0.0, Hydrolog v0.8.0, Hydrograf v0.5.0, Archiwista v0.3.0;
Nogat is released separately. Two rounds of documentation closed every
member for its release: the release text and the deferred defects, then the
style of the documentation against DOC §1 to §10; each merged into the
member's `develop`.

**Deviation from DEV-7.6, the author's decision of 2026-11-16.** A commit
that changes documentation only, and a commit that only moves a pin to a
producer commit whose code is unchanged, ran `ruff format --check`, `ruff
check`, mypy, the tests that read the changed files (README examples,
contract tests, the tests of the pinned producer's calls) and the commit
step, not the whole suite; the whole suite ran in `set verify` of
candidate-6 and in the gate of each release commit. Hydrograf, whose gate
takes about 2 minutes, ran it whole.

**candidate-6** (`release-sets/candidate-6/`): Kartograf `7a1eb11`,
Obserwator `11eedea`, Hydrolog `1be867d`, Hydrograf `1aa66f1`, Archiwista
`95b0540`; between candidate-5 and candidate-6 the producers change only
documentation, and the lock moves only the members (127 packages). `set
check`: every pin between the members matches. `set verify` (unit
`nogat-candidate6-verify`, 6,413 s): Kartograf 8,651 passed, Obserwator
3,432, Hydrolog 8,855, Hydrograf 2,392 on its own lock, Archiwista 3,024
passed and 3 failed (C2 and C3 only).

**Deviation from REL-6.5.** The workflow `verify-candidate` is not on Nogat's
`main` (Nogat's release comes later), so candidate-6 ran only on this
machine (Linux, Python 3.12) and its `members.toml` has no `runs`. macOS,
Windows and Python 3.15 are covered only by each member's own CI on its
own lock.

**Releases**, producers first (REL-6.6). Each release commit changes the
version, the CHANGELOG heading and, in a consumer, the pins (commit → tag)
and the supported ranges (REL-5.6), with `uv.lock`; its full gate passes
before the commit; then `develop` → `main` with a merge commit and the
annotated tag on it.

| Member | Release commit | `main` | Tag | Gate of the release commit |
|---|---|---|---|---|
| Kartograf | `1245289` | `333ef5c` | `v0.8.0` | GATE OK, 8,651 passed |
| Obserwator | `b407c1a` | `707b4a5` | `v3.0.0` | GATE OK, 3,432 passed (C7 failed in the first run) |
| Hydrolog | `6fb8af6` | `3353fc5` | `v0.8.0` | GATE OK, 8,855 passed |
| Hydrograf | `d8906eb` | `634fce6` | `v0.5.0` | GATE OK, 2,392 passed |
| Archiwista | `babc880` | `7fd25e8` | `v0.3.0` | GATE OK, 3,027 passed (umask 077) |

Each tag is annotated and points at the merge commit on `main`, whose tree
equals the member's `develop` after the release commit. The members'
`develop` still carries the release version; each opens its next cycle
(`X.Y.(Z+1).dev0`, a new `[Unreleased]`) with its next change.

**Nogat's release** (2026-11-17, ECO-076): `v0.1.0`, the release commit
`78e0149` on `develop` with `release-sets/v0.1.0/`, candidate-6 with the
tags in place of the commits and the same 127 packages (HUB-7.2, REL-6.6);
`develop` → `main` merged locally without a pull request, with the
author's approval, and the merge commit tagged `v0.1.0` and `std-1.0`.
There is no `nogat` package yet (HUB §7), so the set is installed as an
environment, `uv sync --locked --no-dev` in `release-sets/v0.1.0/`. The
workflow `verify-candidate` reaches `main` with it; candidate-6 stays
verified only by the local `set verify` above.
