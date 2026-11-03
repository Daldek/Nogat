# Plan: final integration run at the data-output heads

Status: done 2026-10-25. A safeguard run: nothing is pinned, tagged or
released, and the environments, the checkouts and the logs of the run were
removed afterwards (REL-5.3). Its failures were fixed the same day, F6 (the
author's) excepted ([Fixes](#fixes)).

Requirements: ECO-051, ECO-053, DEV-10.1, DEV-10.6, DEV-19.10 to DEV-19.14,
REL-2.5, REL-5.3, REL-5.6, REL-6.5. Step 7 of the [data-output
plan](2026-10-24-data-output.md); the [dry run](2026-10-25-integration-dry-run.md)
repeated at the final heads.

## Goal

While the data output was built, each commit was checked with `ruff`, `mypy`
and the commit step only (the author's decision of 2026-10-25), so no member's
tests had run at its final head. This is the one full offline run of every
member at the final heads: in one environment, in each member's own, and on the
flows that cross two tools. A failure is fixed in its own project (DEV-3.4), so
each one is listed with its cause, its class and its owner.

## Options

| Option | Verdict |
|---|---|
| A. One environment; every member installed as a wheel from a detached checkout of its head; the pins between members overridden; each suite run from its checkout with the marker expression and the coverage floor of its gate | Chosen for the combination: it is what `verify-candidate` does (REL-6.5) |
| B. Each member's own `scripts/gate.sh` in its detached checkout, on its own `uv.lock` | Also run: it finds what is specific to a lock and says nothing about the combination |
| C. The live trees, installed editable | Rejected, as in the dry run: sessions edit them, and an editable install hides every test that finds its files through the package path |

## Decision

A and B, then the flows. Every flow ran with connections refused (a proxy on a
closed port), so none depends on a server and nothing was downloaded. The user
data, configuration and cache directories pointed into the throwaway area, so
no run touched a user directory.

## Steps

1. **Heads.** One `git worktree add --detach` checkout per member at the head
   its branch has on `origin`; the heads were fetched again at the end and none
   had moved.

   | Project | Branch | Head | Version |
   |---|---|---|---|
   | Nogat | `feature/data-output` | `e6d4ee1cdcc900bf5936be2ba21513288229dfe9` | no package |
   | Kartograf | `feature/data-output` | `45dedf4a155e2d2f7302459a8c383876fed98e98` | 0.8.0.dev0 |
   | IMGWTools | `feature/data-output` | `3f7de36f98f1ba40d72ab5556942567cfbc55b92` | 3.0.0 |
   | Hydrolog | `feature/routing-schematic` | `5fa22b35e5e1ec9076c41d0be04d2a99458f5049` | 1.0.0.dev0 |
   | Hydraulik | `feature/sfincs-swmm` | `e10c82cf1030850b866c9457feb7e1389be095f3` | 0.1.0.dev0 |
   | Retman | `feature/kartograf-data-output` | `cd1770c34f01fe7ffac6a6b1f53f2460a1b50e49` | 0.1.0.dev0 |
   | Hydrograf | `feature/producer-heads` | `91015478dc6d4889c03d6f328e69ea5b3473c5cf` | 0.5.0.dev0 |
   | Archiwista | `feature/kartograf-data-output` | `74c29cb45d4a3d48d3d987ea17c258c4cfefeabb` | 0.3.0.dev0 |

2. **Environment.** A throwaway uv project on Python 3.12 with the eight
   members as path dependencies on their checkouts, the extras the gates install
   named (`kartograf[mcp]`, `imgwtools[api,cli,mcp,pandas,store]`,
   `hydrolog[all]`, `hydraulik[all]`, `archiwista[imgw]`, `hydrograf[viz]`), the
   union of the members' `dev` groups as its `dev` group, and a lock universal
   for Linux, macOS and Windows. The six installable members are installed as
   wheels, not editable. Hydrograf is an application and Nogat has no package
   (`package = false`), so uv installs their dependencies and not their code;
   their suites run from their checkouts (`backend/` for Hydrograf). The pins
   between members are replaced by the checkouts:

   ```toml
   [tool.uv]
   environments = ["sys_platform == 'linux'", "sys_platform == 'darwin'", "sys_platform == 'win32'"]
   override-dependencies = ["kartograf[mcp]", "imgwtools[api,cli,mcp,pandas,store]", "hydrolog[all]"]

   [tool.uv.sources]
   kartograf = { path = "<checkout>" }   # likewise the other seven members
   ```

3. **Suites.** `pytest tests -m "<expression>" --cov[=<package>]
   --cov-report=term-missing:skip-covered -q`, exactly as the gate calls it,
   with the `pytest` of that environment, from the member's checkout. The
   expression is `not live` (Archiwista: `not live and not perf and not smb`;
   Hydrograf: `not live and not db and not benchmark`). The floor is the
   `fail_under = 80` of each project, enforced by `pytest-cov`. For Nogat the
   steps of its gate after `uv sync` ran in the same environment.
   Archiwista's union run was cut into three shards that ran side by side (the
   tests outside `tests/e2e`, and two halves of `tests/e2e`), and their coverage
   data were combined, to keep the run short.
4. **Gates.** Each member's own `scripts/gate.sh` in its checkout (`uv sync
   --locked --all-extras`, `ruff`, `mypy`, the suite with coverage, the commit
   step), on its own lock and its own `.venv`. Six members ran on Python
   3.13.5 (uv's choice), Hydrograf on 3.12.15. The suites and the gates ran two
   or three at a time on four cores.
5. **Flows.** Eight flows across two tools, in the environment of step 2, with
   the tools' own `store init` and `--check`. Retman's decision model is a
   scripted OpenAI-compatible server on the loopback: at this head the only
   backend its factory builds is `openai_compatible`, and the default `basal`
   raises `backend_unavailable` (`src/retman/backends/__init__.py:32`).

## Results

### Environment

The lock resolves: 159 packages for the three platforms, 154 installed on
Linux, no package in two versions, and `uv pip check` finds the environment
consistent. `scripts/ecosystem.py deps` over the eight checkouts lists 56
third-party packages, 25 of them declared by two or more projects, and flags no
conflicting range. The members' own environments differ in 13 packages
(`deps --installed`), none of them a conflict except `affine` (below).

The pins between members conflict with the checkouts as uv sees them, except
Retman's, and that is why they are overridden: without the overrides uv stops
with "conflicting URLs" (`kartograf` for Archiwista, `hydrolog` for Hydraulik
and for Hydrograf; it applies the `[tool.uv.sources]` of a path dependency).
Retman's pins sit in its `tools` group, which is no dependency of anything, so
it resolves as it is.

| Consumer | Pin that conflicts | Producer |
|---|---|---|
| Archiwista | `kartograf @ git+…@45dedf4a…` and, in the extra `imgw`, `imgwtools[store] @ git+…@3f7de36f…` | Kartograf, IMGWTools |
| Hydraulik | `[tool.uv.sources]`: Hydrolog `5fa22b35…`, IMGWTools `3f7de36f…` | Hydrolog, IMGWTools |
| Hydrograf | `[tool.uv.sources]`: Kartograf `45dedf4a…`, IMGWTools `3f7de36f…`, Hydrolog `5fa22b35…` | all three |

Each of those commits is the head tested here, in the `pyproject.toml` and in
the `uv.lock` of the consumer, so the override changes the form of the source
and not the code. The override names the extras (an override replaces every
requirement on the package, extras included; the dry run found the trap).

One conflict the resolver does not see: Hydrograf caps `affine>=2.4,<3`
(`backend/pyproject.toml:56`, pyflwdir), so the union resolves `affine` 2.4.0,
while the lock of every other member has 3.0.1. Archiwista's previews use the
`@` operator of affine 3 (`src/archiwista/previews/tiles.py:506-510`) and
Archiwista declares no `affine` requirement (it arrives through rasterio). In
the union environment its previews fail at run time (F3).

### Suites in the union environment

| Project | Passed | Failed | Skipped | Not run | Coverage |
|---|---|---|---|---|---|
| Nogat | 174 | 0 | 0 | 0 | 83.97 % (`scripts/`) |
| Kartograf | 8,970 | 1 | 0 | 18 | 95.23 % |
| IMGWTools | 2,491 | 0 | 0 | 80 | 94.50 % |
| Hydrolog | 5,791 | 0 | 17 | 0 | 95.34 % |
| Hydraulik | 823 | 0 | 1 | 17 | 95.64 % |
| Retman | 3,234 | 0 | 0 | 7 | 95.34 % |
| Hydrograf | 1,302 | 0 | 0 | 19 | 85.57 % |
| Archiwista | 1,359 | 85, and 2 errors | 0 | 47 | 90.19 % (three shards, combined) |

The floor of 80 % holds for every member that was measured. Hydraulik's skip is
an empty parameter set; the steps of Nogat's gate after `uv sync` (`ruff`,
`mypy`, registry, map, `AGENTS.md`, standard, `shellcheck`, `actionlint`, commit
step) all pass in this environment.

### Gates on each member's own lock

| Project | Result | Time | Note |
|---|---|---|---|
| Nogat | GATE OK | 11 s | 33 commits checked |
| Hydraulik | GATE OK | 63 s | 32 commits checked |
| Retman | GATE OK | 106 s | 44 commits checked |
| Hydrolog | GATE OK | 169 s | 45 commits checked |
| IMGWTools | GATE OK | 206 s | the commit step checked one commit: with no `origin/develop` it falls back to `HEAD^!` (F6) |
| Kartograf | stopped at pytest | 647 s | F1 (8,970 passed, 95.24 %); the commit step run apart: 67 commits pass |
| Hydrograf | stopped at the commit step | 75 s | `ruff`, `mypy` and pytest pass (1,302 passed, 85.57 %); F5 |
| Archiwista | stopped at pytest | 1,596 s | `ruff` and `mypy` pass; 6 failed, 1,440 passed, 92.28 % (F4, F5 of the table below) |

Every `uv sync --locked` of the eight gates succeeded: the locks agree with
their `pyproject.toml` files.

### Flows

| Flow | Result |
|---|---|
| Hydrolog `route network` to CSV, then Hydraulik `swmm run --check` | Passes. Hydraulik's fixture network gives five tables that equal Hydraulik's recorded ones byte for byte; the plan has two `write` targets, no blocker, and writes nothing; the real run writes `network.inp` and `network.rpt` (continuity error 0.012 %), and a second `--check` lists both as `conflict` (`output_exists`). Hydrolog's own flood fixture gives six tables, and the plan applies 299,026.5 m3 to `J1` |
| Hydrolog `route network --schematic` | Passes. `--check` lists the SVG as `write` and writes nothing; the run writes a well-formed SVG and returns `hydrolog-network-schematic/1`; a second run exits 4 (`conflict`, `output_exists`); `--force` gives `replaced`; tables and schematic together, and `--main-stem` on an inline network, pass |
| Retman `plan run --check` with an IMGWTools `datasets download -o` and a Kartograf command | Passes. "Dobowe dane hydrologiczne IMGW z lat 2019–2020" gives a complete plan of 24 archives, and "NMT 1 m EVRF2007 dla arkusza N-34-130-D-d-2-4" one of 1 sheet, each previewed without network; Retman's journal is the only file it writes. The call Retman builds, `imgw datasets download --dataset pl.imgw.hydro_daily --years 2019,2020 --output-dir <results>`, validates and the tool's own `--check` lists 24 `write` targets and creates nothing. The Kartograf call, `kartograf elevation download --product nmt --sheet N-34-130-D-d-2-4 --resolution 1m --vertical-crs EVRF2007 --root <store>`, validates, and its `--check` creates no store and, offline, ends with `check_failed` (exit 11); the same sheet with `--output-dir` is F2. `retman doctor check` shows both tools in their ranges (`>=3.0.0.dev0,<4`, `>=0.8.0.dev0,<0.9`) and their manifests consistent with the catalogs |
| Hydraulik `terrain download --check` on the real Kartograf head, offline | A clean `source_unavailable` (exit 5), as expected: "PRG query (counties): download failed after 3 attempts", engine `kartograf`, command `landcover download`; nothing is created, the run fails the same way. `engines check` finds Kartograf and "--output-dir writes plain files". With `--products elevation` the plan is one `write` target and no blocker, although the index could not be asked (F2) |
| Archiwista `doctor`, both producers, both default roots | Passes (exit 0, no error, no warning): the plugins `imgw` 3.0.0 (`>=3.0.0,<4`) and `kartograf` 0.8.0.dev0 (`>=0.8.0.dev0,<0.9`), each producer's default root under `NOGAT_DATA_DIR` "with a marker", and a store entry with both roots. Without the markers it exits 10 with the two repair commands (`kartograf store init --root …`, `imgw store init --root …`); an IMGW directory inside the Kartograf one exits 10 as a nested store |
| Nested stores, both directions | Passes. IMGWTools into a Kartograf store: `-o` inside it or at its root, `--check` lists `conflict` `output_in_store` and the run exits 4 with the output directory in `details.paths`; `-o` over a marker below it, every target is listed; `--root` inside or at it, `--check` lists `conflict` `nested_store` and the run exits 4 before any request. Kartograf into an IMGWTools store: the same refusals for `-o` and `--root`, on `soil download`, whose target names need no request. `store init` in the other tool's store, or over a root that holds one: `nested_store` in both directions. Nothing was created where a refusal came |
| `store init`, both producers | Passes. A new root, an empty one, and a root with the layout and no marker (the fixture stores of `kartograf.testing` and `imgwtools.testing` without their marker) get a marker with `schema`, `tool`, `created_at`, `producer_version`; a second `init` changes nothing; `--check` writes nothing; the default roots are created under `NOGAT_DATA_DIR` and `config show` names root and source. A writer on a root with the layout and no marker answers `store_unavailable` (exit 8) with the `store init --root` hint, in check and run |
| One `one_of` group and the store-only options | Passes. `--root` with `--output-dir`: `validation_error` (exit 2, `exclusive_options`) in both producers; `--upgrade` with `--output-dir`: `validation_error` (`store_only_option`) naming `--root` |

### Failures

| # | Where it shows | Cause | Class | Owner |
|---|---|---|---|---|
| F1 | Kartograf: `tests/integration/test_mcp_server.py::test_stdio_stdout_has_only_protocol_frames` (`JSONDecodeError` at line 1970), in the union environment and in the own gate | `_serve` (`src/kartograf/mcp_server.py:963-972`) leaves the `async with stdio_server()` block while `sys.stdout` still holds the text of a stray `print`. The SDK has then restored descriptor 1, so with a block-buffered stdout (a pipe: the normal case) the text is flushed after the restore and reaches the client as a non-JSON line (`STRAY PRINT`). Hydrolog flushes before it leaves (`src/hydrolog/mcp/server.py:307-318`); IMGWTools has the same gap (`src/imgwtools/mcp/server.py:123-127`) and no test | Real defect. Deterministic: 3 of 3 alone with `PYTHONUNBUFFERED` unset, 0 of 3 with `PYTHONUNBUFFERED=1`, which agent shells set, so a per-commit run there would not show it | Kartograf; the same flush in IMGWTools |
| F2 | Kartograf, plain `--check` while the sheet index cannot be asked: `elevation download --sheet … --output-dir … --check` exits 0 with `ok: true`, the item `missing`, action `write`, and the failed WFS request only in the item's `error`. The store `--check` exits 11 (`check_failed`, `source_unavailable`), and so does the plain run | `plain_items` (`src/kartograf/download/plan.py:273-293`) turns every position, a `check_failed` one included, into `missing`/`write` or `unverifiable`, so `UpdatePlan.ok` (`plan.py:150`) is true. DEV-19.10 asks the plan to predict the run. Hydraulik's plan for `--products elevation` rests on it | Real defect, minor (wrong only while the source is down) | Kartograf |
| F3 | Archiwista in the union environment: 81 tests (79 failures and 2 errors in fixtures) in `tests/unit` (raster, COG, styles, compose, points), `tests/integration` (previews, local layers, own data, CLI, permissions) and `tests/e2e` (acceptance, compare, fan, map previews, own data, previews) | `Affine @ tuple` raises `TypeError` in `raster_bounds` (`src/archiwista/previews/tiles.py:506-510`) on affine 2.4.0, so every preview is `unreadable`. With Hydrograf left out of the environment (affine 3.0.1) 79 of the 81 pass; the two others are F8 and a timing failure (below) | Environment (the union resolves affine 2.4.0 for Hydrograf) over a real defect: Archiwista uses the affine 3 operator and declares no `affine>=3` | Archiwista declares it; Hydrograf's cap stays until pyflwdir is released |
| F4 | Archiwista, own gate and union environment: `tests/contract/test_plugins.py::test_plugins_default_root_comes_from_the_source_that_has_one` (line 292), `tests/integration/test_default_root.py::test_default_root_health_leaves_it_out`, `::test_default_root_command_line_prints_what_the_route_answers`, `tests/integration/test_sources_imgw.py::test_sources_lists_imgw_with_its_versions_and_schemas` | The tests expect that only Kartograf reports a default root; the `imgw` source does too now (`src/archiwista/adapter/imgw/adapter.py:173-185`, `IMGW_ROOT`), as the doctor and `GET /sources` show | Real defect: stale tests, deterministic | Archiwista |
| F5 | Archiwista, own gate and union environment: `tests/unit/test_config.py::test_config_store_needs_a_directory_and_detects_its_kind_from_any` (2 cases, line 448) | The test looks for the Polish "kartograf albo imgw" in `problem.message`, which is English (`DEFAULT_LANG = "en"`; the Polish text is `src/archiwista/messages/settings.py:60`). Not the locale: the same with `LANG=pl_PL.UTF-8` | Real defect: stale test, deterministic | Archiwista |
| F6 | The commit step of the gates. Hydrograf: 19 commits of local `develop` that are not on `origin/develop` (author `agent@local`, AI trailers) fail; the 49 commits of the branch pass with `GATE_COMMIT_RANGE=develop..HEAD`. IMGWTools: the gate checks one commit; over the 138 commits since `master`, 48 old ones fail (author `agent@local`, 21 with AI trailers, one subject) | The rewrite of the old history is the author's (Hydrograf's PROGRESS names it) | Known, not a defect of the heads | The author |
| F7 | `deps` notes "Hydrograf: backend/requirements.txt missing" | The registry still lists it in `python_manifests`; Hydrograf dropped the file in `3ca62f2` (uv step) | Known (PROGRESS, Next 3) | Nogat, with Hydrograf's entry |
| F8 | Archiwista: `tests/integration/test_preview_cache.py::test_cache_safe_across_processes` (`BrokenPipeError` at line 363), in the union environment and in the environment without Hydrograf; it passes in the own gate (Python 3.13.5). Alone in the Python 3.12 environment it fails 4 of 6 runs | A child process ends before the test has written to it; the cause was not isolated | Flaky (intermittent) | Archiwista |

Every failure above is deterministic except F8. One more test failed once, in a
batch, and passed three times alone: `tests/e2e/test_map_previews.py::test_year_buttons_select_layer_and_tiles`
(the count of footprints in the view, under load). Apart from the failures
listed, every test passed in the union environment and on its member's own lock.

### The findings of the dry run

| Dry run | Now |
|---|---|
| F1 Retman's Kartograf half called the old Kartograf | Closed: Retman passes (3,234), and its plan of a Kartograf sheet validates the call with the tool |
| F2 Supported ranges refused the development versions | Closed: Retman's doctor and Archiwista's show `>=0.8.0.dev0,<0.9` for Kartograf |
| F3 Archiwista's fixtures used the old `output_dir` | Closed: its fixtures use `kartograf.testing` and `imgwtools.testing`; what still fails is F3 to F5 above |
| F4 Tests found the repository through the installed package | Closed for the six wheels: every suite runs against its wheel without a collection error |
| F5 Kartograf's CLI had no plain mode | Closed: `--output-dir` on the data commands; the flows pass |
| F6 Archiwista had no IMGWTools source | Closed: the doctor lists both plugins and both default roots |
| F7 IMGWTools `--root --check` inside another store planned a download | Closed: it lists a `conflict` (`nested_store`) |
| F8 `testing` modules (DEV-10.6) | Closed: Archiwista, Retman, Hydraulik and Hydrolog build their fixtures with `kartograf.testing`, `imgwtools.testing` and `hydrolog.testing` |

### What the run does not show

- Anything on macOS or Windows (the lock resolves for them, nothing ran there),
  and Python 3.13 beyond the own gates of six members.
- The `live` tests, the `db` tests of Hydrograf (no PostGIS), the `perf` and
  `smb` tests of Archiwista, and any download from a real server.
- Retman with a real model, or with its default `basal` backend.
- Timing: two or three runs shared four cores.

## Fixes

Every failure but F6 was fixed on 2026-10-25, each in its own project and on the
branch of the table in step 1; F3 also left a known incompatible pair. Every
commit below is pushed.

| # | Fix | Commits |
|---|---|---|
| F1 | `_serve` hands the stray text of `sys.stdout` to standard error before the SDK restores descriptor 1, as Hydrolog does; IMGWTools does the same and has the test now (`tests/unit/test_mcp_stdio.py`) | Kartograf `ca7d538f23f385625fc10b186673a8a5705d2848`, IMGWTools `6bd35a49b329f99b591ffdee39367daec0e75af7` |
| F2 | A position whose check failed stays `check_failed` in a plain plan, with its error and without action, path or reason, as in the store; the plan is `ok: false` (exit 11, or 10 when other positions are fine) | Kartograf `c31ca04c078ebbee36850d0aa4dcead59dd77a41` |
| F3 | Archiwista declares `affine>=3,<4`; its lock keeps 3.0.1, and a resolver now refuses Archiwista beside `affine>=2.4,<3`. Hydrograf keeps its cap (its ADR-062): with pyflwdir 0.5.12, the latest release, and affine 3.0.1, 15 of its 1,302 offline tests fail (`FlwdirRaster.stream_distance` and `path`, which `scripts/process_dem.py` needs: numba cannot type `affine.Affine`, which `set_transform` makes of any transform). pyflwdir's own suite at `v0.5.12` passes only because its `conftest.py` disables the JIT; with the JIT on, 33 of its tests fail with affine 3.0.1 that pass with 2.4.0. The fix, pyflwdir #109 (issue #108), is merged for 0.5.13, which is not released | Archiwista `bc230d46bb49ba7f901d45ab5acb4d5fe07a5e33`, Hydrograf `b3545ca086701dd84a570d9d21d4bcdc1aadba01` |
| F4 | The four tests expect the default root of IMGWTools beside Kartograf's; they pass with and without the extra `imgw` | Archiwista `19ff4d9cb3a8c3f0587c10253f0885f174584b40` |
| F5 | The test asserts the English text, the default language | Archiwista `c168893a5a8e41933402c8884d47b901f284cf82` |
| F6 | Not fixed: the rewrite of the old history is the author's. Hydrograf's branch is gated with `GATE_COMMIT_RANGE=develop..HEAD`, and IMGWTools' commit step still checks one commit | — |
| F7 | Hydrograf's `python_manifests` is `backend/pyproject.toml` alone, and `deps` no longer notes the file; the map and `AGENTS.md` show no manifests and are unchanged | Nogat `d485bc2a3fdef319b265b1782f156a8b151227df` |
| F8 | The cause was in the cache, not in the test. `PreviewCache` switches `cache.sqlite` to WAL when it opens; the switch reads the header and then writes it, and SQLite answers a process that read the header while another one writes it with `SQLITE_BUSY` at once, without the busy timeout (waiting could deadlock). The child died at its start with "database is locked", and the test's write of the start line raised `BrokenPipeError`. Not Python 3.12 alone: eight processes that open a new cache together failed in 7 of 10 rounds on 3.12 (SQLite 3.53.1) and in 5 of 10 on 3.13 (SQLite 3.46.1). The switch is now tried again until `BUSY_TIMEOUT_MS` (0 of 30 rounds fail on each). The new `test_cache_opened_by_processes_at_once` (eight processes, five new caches) failed in every run before the fix and passes 12 of 12 after on both versions, as `test_cache_safe_across_processes` does; the handshake of these tests reports a child that ended by its standard error, not by a broken pipe | Archiwista `6e5517e2bd83f19e2954027e1e8763ef0f4b4bd4` |

The test that failed once under load (`test_year_buttons_select_layer_and_tiles`)
is unchanged; it passed in Archiwista's gate below.

**The known incompatible pair.** Hydrograf (`affine>=2.4,<3`) and Archiwista
(`affine>=3,<4`) cannot share an environment until pyflwdir 0.5.13 lets
Hydrograf lift its cap. Each is an application with its own lock, so only an
environment of the whole ecosystem meets the conflict: `deps` now reports
`affine` as a `range_conflict` (exit 4) and a resolver refuses the pair, where
before it chose affine 2.4.0 for both; a repeat of this run installs the two
apart.

Full gates of the fixed heads, each on its own lock. Kartograf's and IMGWTools'
ran in the session that fixed F1 and F2, with `PYTHONUNBUFFERED` unset as F1
needs; the other three ran with it set (none of them has an MCP server).

| Project | Head | Result |
|---|---|---|
| Kartograf | `c31ca04c` | GATE OK, 647 s: 8,973 passed, 18 not run, 95.23 %, 69 commits checked |
| IMGWTools | `6bd35a4` | GATE OK, 209 s: 2,492 passed, 80 not run, 94.48 %; the commit step checked one commit (F6) |
| Archiwista | `fc5e658` | GATE OK, 1,513 s: 1,447 passed, 47 not run, 92.28 %, 76 commits checked |
| Hydrograf | `b3545ca` | GATE OK, 32 s, with `GATE_COMMIT_RANGE=develop..HEAD` (F6): 1,302 passed, 19 not run, 85.57 %, 50 commits checked |
| Nogat | `d485bc2` | GATE OK, 8 s: 174 passed, 83.97 %, 35 commits checked |

## Next

1. The author: the history of Hydrograf's `develop` and of IMGWTools (F6).
2. Hydrograf lifts the affine cap with pyflwdir 0.5.13 (its ADR-062); until
   then Hydrograf and Archiwista run in separate environments.
3. Done 2026-10-25: the consumers are re-pinned to the producers' new heads
   (Kartograf `c31ca04c`, IMGWTools `6bd35a4`), each with its full gate and
   pushed: Retman `cc6d1ee`, Hydraulik `91559e0`, Hydrograf `9dfa3a8`,
   Archiwista `e5b4c22` (the pins table in the Results of the
   data-output plan). Open: repeat the run for the members that changed, with
   Hydrograf and Archiwista apart, and the two flows of F2, and record it in
   the Results of the data-output plan.
