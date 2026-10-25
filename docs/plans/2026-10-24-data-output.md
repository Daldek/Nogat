# Plan: one data-output convention

Approved: 2026-10-24

Requirements: DEV §19, AGI-3.4, DEV-18.2, HUB-5.2, ECO-051. Part of phase 4 of
the [adoption plan](../../standards/ADOPTION_PLAN.md); it lands before the
[first release set](2026-10-20-first-release-set.md).

## Goal

Every tool with a versioned store writes data in the same two modes, plain
files or the store, with the same options, defaults, errors and result
([DEV §19](../../standards/DEVELOPMENT_STANDARDS.md#19-data-output-profile-tool),
[ECO-051](../../standards/DECISIONS.md#eco-051-one-data-output-convention)).
Kartograf 0.8.0 and IMGWTools 3.0.0 are untagged, so the breaking changes land
before the first release set and no data is migrated (ECO-020). The projects
that call them follow, so the verified set has one meaning of `-o`, `--root`
and `output_dir`.

## Options

| Option | Verdict |
|---|---|
| A. The variant drafted on the Kartograf branch `claude/vigilant-faraday-finqvd` (ADR-048): `-o`/`--output` is the plain directory, `--store` the store, one of them required, no flag to overwrite, Kartograf only | Rejected: `--store` and a directory-valued `--output` contradict AGI-3.4, "neither = error" ignores the default store of DEV-18.2, and IMGWTools would keep its own names (ECO-051) |
| B. One convention for every tool with a store: `--output-dir` (`-o`), `--root`, default store, `--force`, markers, `files[]` | Chosen (ECO-051) |
| C. A shared store library imported by all tools | Rejected: a new dependency between all projects (Zen 10); the layouts differ per tool, and a marker file name needs no import |
| D. Leave each tool as it is | Rejected: the same call means different things in two tools, and Kartograf's `-o` as a store root cannot write one plain file |

## Decision

Option B. The rules are DEV-19.1 to DEV-19.20, the reasons are ECO-051, and
the author approved the convention on 2026-10-24.

## Steps

Producers before consumers, in the dependency order of `ecosystem.yaml`
(HUB-5.2). Kartograf and IMGWTools run in parallel: their only link is the
marker file names of DEV-19.12, which need no code from the other tool. In
every project:
- the work is on a local topic branch from the project's development branch,
  one commit per step, the project's gate green before each commit; nothing is
  pushed, tagged or merged without the author (DEV-3.3);
- a producer first brings the repository in line with standard 2.1 as far as
  the author is not needed (ADOPTION_PLAN phases 2 to 4; not the history
  rewrite, GitHub settings, root-owned files, licence or CLA text, tags or
  pushes) and lists in PROGRESS what it skipped;
- the decision goes into the project's ADR file, and CHANGELOG and PROGRESS
  are updated; there are no aliases and no deprecated paths (ECO-020).

File and line references are those of 2026-10-24 and only locate the work.

1. **Nogat** (done 2026-10-24). ECO-051, DEV §19, the amended AGI-1.3,
   AGI-2.3, AGI-3.4, AGI-4.3, AGI-5.8, ERR-1, DEV-18.2, DEV-18.5 and DEV-18.6,
   the store markers and the IMGWTools exchange in `ecosystem.yaml` and the
   map, the items in ADOPTION_PLAN, and this plan. Tagging `std-2.1` waits for
   the author (ADOPTION_PLAN 0.4).

2. **Kartograf**, after its standard 2.1 adoption:
   - **ADR.** A new ADR (the next number after ADR-047 in
     `docs/DECISIONS.md`) records DEV §19 for Kartograf and supersedes the
     branch's ADR-048. ADR-048, its spec
     `docs/superpowers/specs/2026-10-23-plain-output-design.md` and its plan
     `docs/superpowers/plans/2026-10-23-plain-output.md` get a "superseded by
     <new ADR>" status line, and the branch is neither merged nor developed
     further.
   - **Options** (DEV-19.1, DEV-19.17). `OUTPUT_DIR` in
     `kartograf/catalog/shared.py` (`--output`/`-o`, required, the store
     directory) becomes `--output-dir` (`-o`, plain) and `--root` (store) in
     one `one_of` group, neither required; the `output_dir(files)` helper, the
     parsers, MCP and the generated docs follow the catalog. `--upgrade`,
     `--plan`, `--all-campaigns` and `project *` reject `output_dir` with
     `validation_error` naming `--root`. How `--full-sheet` behaves in plain
     mode is decided in the ADR (the branch warned that it is redundant).
   - **API names.** A parameter that names a store root is `root`:
     `list_segments`, `list_partitions` and `iter_store` in
     `kartograf/store.py`, the download and check functions,
     `DownloadManager`, `run_command`, `check_command`, `validate_command`,
     `init_project`, and `Project.output_dir` with the `output_dir` key of
     `kartograf-project/1` (`project/manifest.py`; unreleased, so renamed
     without migration). `output_dir` then means plain output only. The CLI
     calls `cli/download_cmd.py:477`, `cli/landcover_cmd.py:50`,
     `cli/soil_cmd.py:39,93` and `cli/project_cmd.py:41,97` pass the new names.
   - **Plain mode** (DEV-19.4 to DEV-19.11, DEV-19.18). Every write path gets a
     plain branch beside `commit_version` and `store_file`:
     `download/fetch.py` (`fetch_version`), `download/manager.py`
     (`_download_version`, near line 1334), `download/cz_orto.py` (`_download`,
     near 334), `landcover/manager.py` (`store_file` near 1742, 1833 and 1855),
     and the CZ sheets, LAZ, contours and collections tracks. File names come
     from the slot's unit name; the preflight, `.kartograf-incoming/`,
     `os.replace` and `--force` are written once and shared by the tracks.
     `calculate_hsg` supports both modes: inputs go to staging, only the
     result is written in plain mode.
   - **Selection rule of plain mode** (DEV-19.4). PL sheets (NMT, NMPT,
     orthophoto) take the newest full flight; a sheet without one is skipped
     (`skipped_incomplete`, `skipped[]`), and all skipped is `no_data`. The
     difference from the store is written in USAGE, ARCHITECTURE 4.1, the
     `--help` of the options, the catalog `description` and the API docstrings.
   - **Store** (DEV-19.12 to DEV-19.15). The marker `kartograf-store.json`
     (`kartograf-store/1`) is written on the first write into an empty or new
     root; `kartograf store init --root` verifies the layout and writes it; a
     root with the layout and no marker is `store_unavailable`. The nested-store
     check looks for the markers of both tools in ancestors and descendants,
     in both modes. The hard-linked standard path stays Kartograf's own
     addition.
   - **Default root** (DEV-19.2, DEV-18.2, DEV-18.6). `<data_dir>/kartograf`,
     `KARTOGRAF_ROOT`, `[kartograf] root`, reported by `config show --json`
     with its source. The default metadata cache moves from
     `<cwd>/.kartograf_cache.db` (`cache_info.py`, `cache/defaults.py`) to
     `<cache_dir>/kartograf`.
   - **Plan and result** (DEV-19.10, DEV-19.4, DEV-19.19). `--check-updates`
     becomes `--check`; `check_*` and `check_command` return the same plan,
     with the plain actions `write`, `replace` and `conflict`; a plan that
     lists conflicts is a successful result, and only the real run fails.
     `kartograf-download/1` lists `files[]` as `{path, size_bytes, sha256,
     status}` instead of `files[].file.path`, with the store statuses `new`,
     `unchanged` and `relabeled` (the tool's own words today), and
     `skipped[]` as `{id, reason, message}`; `sha256` is computed while the
     file streams.
   - **Sidecar and tests.** `kartograf-meta/1` gains `producer` (`kartograf`)
     and `producer_version` beside `kartograf_version` (optional fields
     within `/1`, `ResultMetadata` in `kartograf/sources/sidecar.py`); its
     other fields have the meaning of DEV-19.16 (Results). The
     `kartograf.testing` module that DEV-10.6 asks for in the standard
     adoption builds stores with the marker; contract tests cover DEV-19.1,
     DEV-19.6, DEV-19.10, DEV-19.11, DEV-19.12 and DEV-19.19.
   - **Documents.** USAGE (examples start with `-o`), ARCHITECTURE 1, 3.3 and
     4.x, README, `llms.txt`, the generated AGENTS.md, CHANGELOG `[0.8.0]`
     marked **Breaking** with migration notes, PROGRESS.

3. **IMGWTools**, in parallel, after its standard 2.1 adoption:
   - **ADR.** A new ADR in `docs/DECISIONS.md` records DEV §19 for IMGWTools:
     plain mode and the store are two modes of the same writing commands, and
     nested stores are detected by marker name only (it changes D3 and Q3 of
     ADR-001). It classifies each writing command by DEV-19.18: store-only
     are `series build`, `store catalog` and `project *`; every other writing
     command, such as `datasets download`, `store sync` and `pmaxtp sync`,
     supports both modes.
   - **Options** (DEV-19.1). The plain download (`download_archives(...,
     output="data/downloaded")` in `fetch.py:989`, the option `_OUTPUT`
     `--output`/`-o` in `commands.py`, and the `.part` files) becomes plain
     mode with `output_dir` (`--output-dir`, `-o`); the default in the current
     directory is gone, because a command without a target writes to the
     store. The `path` of the exports (`export_series(path=)` in
     `store/export.py:448`, `series export`, `store export`) becomes `output`
     (`--output`). `--root` stays, and `output_dir` and `root` form one
     `one_of` group.
   - **Default root and servers** (DEV-19.2, DEV-19.3). `IMGW_STORE_ROOT`
     becomes `IMGW_ROOT` (`commands.py:314`, `api/main.py:69`,
     `api/errors.py:168`, `api/routes/commands.py:14,252,349-372`); the default
     root is `<data_dir>/imgw`, replacing "no default location" in README and
     ARCHITECTURE; `config show --json` reports root and source. REST accepts
     no `root`, `output_dir` or `output` in a request, and MCP checks the
     default root against `--allow-dir`.
   - **Plan and result** (DEV-19.10, DEV-19.19). `_check_download`
     (`commands.py:2414`) and the download path get the preflight,
     `.imgw-incoming/<host>_<pid>_<token>/`, `--force` and the plan actions
     `write`, `replace` and `conflict`; a plan that lists conflicts is a
     successful result, and only the real run fails. The sub-path is the
     server path. `DownloadReport` becomes the `files[]` of DEV-19.19 with
     the store statuses `new`, `unchanged` and `relabeled`: `created` becomes
     `new` in `VersionResult`, `CatalogReport` and the PMAXTP and series
     reports (`store/types.py`, `store/writer.py`, `store/catalog.py`,
     `store/pmaxtp.py`, `store/series.py`), unreleased and so without
     migration, and a reused version is listed as `unchanged`.
   - **Store** (DEV-19.12 to DEV-19.14). `imgw-store.json` gains `tool` and
     `producer_version` and always carries `created_at` (today `created_by`
     and an optional `created_at`). The first write into an empty or new root
     creates it, and `store init` verifies the layout of a root without a
     marker instead of refusing it. `_check_kartograf` (`store/writer.py`,
     near 297 to 360, which reads `kartograf-project.json` and
     `kartograf-meta/1` sidecars) is replaced by the detection of
     `kartograf-store.json` and `imgw-store.json` in ancestors and
     descendants.
   - **Sidecar and tests.** `imgw-meta/1` has the core of DEV-19.16 (Results).
     `imgwtools.testing` builds stores with the new marker; contract tests
     cover the same rules as in Kartograf.
   - **Documents.** README, ARCHITECTURE, AGENTS.md (generated), CHANGELOG
     `[3.0.0]` marked **Breaking**, PROGRESS.

4. **Archiwista**, once the producers' development heads have steps 2 and 3
   (REL-5.3 if it must pin a commit):
   - `archiwista/adapter/kartograf/adapter.py:645` reads `project.output_dir`,
     which is `project.root`; the texts that call Kartograf's `--output`
     directory the store (`messages.py:274`, `config.py:179`,
     `api/models.py:2401`, `sources/types.py:4`) say `--root`; `probe` follows
     the marker rules (DEV-19.12, DEV-19.13).
   - `tests/contract/test_kartograf.py` pins the parameter names of the read
     API (`output_dir` of `list_segments`, `list_partitions`, `iter_store`,
     lines 54 to 61) and describes the probe (line 602): `root`.
     `tests/fixtures/make_store.py` writes the marker and the project
     manifest key.
   - `docs/SPEC.md`: §12 KB-5 (`run_command(..., output_dir, ...)`), KA-1,
     KH-1 and the passages that call Kartograf's `--output` directory the
     store (near lines 174, 783, 813, 1431, 1445 and 3118) follow the new names.
     Archiwista keeps calling Kartograf in store mode.

5. **Retman**, after step 2 (and step 3 for the IMGWTools adapter):
   - `retman/tools/kartograf/client.py` (lines 9, 188, 195 and 255 to 273)
     passes `root=` instead of `output_dir=` to `validate_command`,
     `run_command` and `check_command` and shows `--root` in the command line;
     `handlers.py` (lines 84 and 137) builds `DownloadManager(root=...)`. The
     `store_dir` setting keeps meaning the store root, and whether it stays
     required (DEV-19.2 gives the tool a default) is decided in Retman.
   - `tests/tools/kartograf/`, USAGE, ARCHITECTURE and CHANGELOG follow. The
     IMGWTools adapter already passes `root`; it is rechecked against the
     new default root and `IMGW_ROOT`.

6. **Hydrolog** (documents only), after step 2:
   - `docs/INTEGRATION.md:430` calls `download_soil(output_dir="/dane/kartograf",
     ...)` and reads `report.files[0].file.path`; it uses plain `output_dir`
     and `report.files[0].path`. `hydrolog/agent_guide.py:425` has the CLI
     example `--output /dane/kartograf`; it uses `--output-dir` and the
     `files[].path` of the result, and the generated `AGENTS.md` (lines 212 to
     214) and `llms.txt` (lines 56 and 57) are regenerated.

7. **Integration check**, after steps 2 to 6: one throwaway environment with
   every member at its branch head (Kartograf, IMGWTools, Hydrolog, Retman,
   Archiwista), installed from the checkouts and committed nowhere (REL-5.3).
   Each member's offline suite and contract tests run in it, the consumers'
   tests against the producers' `testing` modules (DEV-10.6), plus an offline
   smoke run of both modes in both producers and of nested-store refusal in
   both directions. `uv run scripts/ecosystem.py deps --installed` shows no
   conflicts. The result is recorded in Results. Failures are fixed in their
   project (own session and branch) and the check repeats.

   The checkouts are found by registry name (HUB-3.1), but the branches of
   this plan sit in worktrees (`Kartograf-dataout`, `Hydrolog-routing`,
   `Hydraulik-sfincs`), so the check sets `NOGAT_WORKSPACE` to a directory of
   links named `Kartograf`, `IMGWTools`, `Hydrolog`, ... to the checkouts at
   the heads under test.

   **Integration rule: pins before pushes, producers first.** A consumer pins
   a producer by commit while the producer has no tag (REL-5.3), and until the
   author pushes, such a pin names a local commit. `uv lock` and `uv sync`
   fetch the producer's GitHub URL, so the commit resolves only on a machine
   whose uv git cache was given it with a `git fetch` of the local clone
   (Retman's pin of IMGWTools `a304521` is one). The author therefore pushes in
   the order of the registry (HUB-5.2): the producers first, IMGWTools,
   Kartograf and Hydrolog, each with the branch that holds a pinned commit, and
   then the consumers, Retman, Archiwista and Hydraulik (Hydrograf after the
   first release set). A consumer pushed before its producers has no green CI.
   A producer that rewrites or rebases a pinned commit afterwards (Kartograf's
   rebase of `feature/data-output` onto the message catalog, the history
   rewrite of ADOPTION_PLAN phase 1) moves it, so the consumers re-pin
   (`uv lock`) after the producer's last rewrite and before their own push.
   The check above installs from the checkouts and does not depend on pushes.

8. **First release set.** The [first release set](2026-10-20-first-release-set.md)
   starts from the heads verified in step 7. After the release, Hydrograf
   upgrades as its step 8 says and also changes `DownloadManager(output_dir=...)`
   in `backend/scripts/download_dem.py` to `root=`; Hydraulik's proof of
   concept (`src/hydraulik/data.py` calls `kartograf download --output ...` and
   reads the store layout) uses `--output-dir` and the `files[].path` of the
   result when it is committed.

## Results

Nogat, 2026-10-24: step 1 is done (list above), with the check of
`standard` that the markers of DEV-19.12 are those of the registry's stores
(HUB-4.7).

Sidecar core, compared in the code on 2026-10-24: Kartograf `Sidecar`
(`kartograf/store.py`) and `ResultMetadata` (`kartograf/sources/sidecar.py`),
IMGWTools `Meta` (`store/types.py`), writer (`store/writer.py`) and reader
(`store/reader.py`). The thirteen fields of DEV-19.16 exist in IMGWTools, in
the document or in the read model, and in Kartograf except `producer` and
`producer_version`; where both have a field, the meaning is the same. What
differs is the range of a value, and no field is renamed:

| Field | Difference | Who adapts |
|---|---|---|
| `producer`, `producer_version` | IMGWTools writes both; Kartograf has only `kartograf_version` | Kartograf adds both within `/1` and keeps `kartograf_version` |
| `dataset_key` | derived from `dataset` on read in both, stored in neither | nobody; DEV-19.16 leaves the storage open |
| `country`, `dataset` | Kartograf has `EU` and `GLOBAL` and keys `eu.…`, `global.…`; IMGWTools accepts two capital letters and a two-letter key scope only | IMGWTools widens both patterns when it stores data without one country; none does yet |
| `downloaded_at` | Kartograf writes `+00:00` with microseconds, IMGWTools `Z` | nobody; both are ISO 8601 UTC with an offset |
| `license` | IMGWTools adds the optional `terms_url` | nobody; an optional field within `/1` |
| `schema`, `provider`, `size_bytes`, `sha256`, `request`, `extra` | none | – |

Also found:
- Marker: IMGWTools `imgw-store.json` has `schema`, `created_by` and an
  optional `created_at`, so step 3 adds `tool` and `producer_version` and
  always writes `created_at` within `/1`; Kartograf has no marker yet
  (step 2).
- Store statuses of `files[]` are `new`, `unchanged` and `relabeled`
  (DEV-19.19): IMGWTools says `created` for `new` (step 3), Kartograf already
  says `new`.

State of the projects on 2026-10-24, before the work:

| Project | State |
|---|---|
| Kartograf | `develop`, clean; the branch `claude/vigilant-faraday-finqvd` (documents only: ADR-048, spec, plan) is not merged |
| IMGWTools | `fix/archiwista-compat-2`, clean; one stash |
| Hydrolog | `develop`, clean |
| Retman | `develop`, clean |
| Archiwista | `develop`, clean |
| Hydrograf | `feature/kartograf-wykorzystanie`, one uncommitted file |
| Hydraulik | `develop`; the proof of concept is uncommitted |

### State on 2026-10-25

Each project works on a local branch from its development branch; nothing is
pushed, tagged or merged (DEV-3.3). The heads are those read on 2026-10-25;
they move while the sessions run.

| Project | Step | Branch (worktree), head | State |
|---|---|---|---|
| Nogat | 1 | `feature/data-output` | done; the registry follows the branches below |
| Kartograf | 2 | `feature/data-output` (worktree `Kartograf-dataout`), `91c4510f` | in progress |
| IMGWTools | 3 | `feature/data-output`, `a304521` | done on the branch |
| Archiwista | 4 | `chore/nogat-2.1`, `2b167c3` | not started |
| Retman | 5 | `feature/imgwtools-data-output`, `932d2cf` | the IMGWTools half is done |
| Hydrolog | 6 | `chore/nogat-2.1`, `d4f7282`; `feature/routing-network`, `6c9ba5a` | documents done; routing documents are new |
| Hydrograf | 8 | `chore/nogat-2.1`, `39eb15e` | not part of this work |
| Hydraulik | 8 | `feature/sfincs-swmm` (worktree `Hydraulik-sfincs`), `793002a` | done on the branch, not merged |

- **Nogat.** The registry and the map follow the branches below (CHANGELOG):
  plain files and `files[]` beside the stores, the default roots, the published
  `<tool>-command-list/1` and `<tool>-commands/1`, `kartograf-result/1`, the
  `testing` modules, `hydrolog-network/1`, `hydrolog-hydrograph-csv` and the
  edges of Hydraulik.
- **Kartograf**, nine commits on `chore/nogat-2.1` `18a33d01`. Landed, each
  with its gate green: ADR-054, `root` and `--root` for every store root, the
  default root `<data_dir>/kartograf` and `KARTOGRAF_ROOT`, the marker
  `kartograf-store.json` with `kartograf store init`, `producer` and
  `producer_version` in `kartograf-meta/1`, `--check` instead of
  `--check-updates`, the engine `kartograf.output` (preflight, staging,
  `--force`; no command calls it yet) and `files[]`, `skipped[]` and `mode` in
  `kartograf-download/1` and `kartograf-plan/1`. Open: plain mode in the tracks
  and `calculate_hsg` (in the working tree, uncommitted), the
  `output_dir`/`root` group with `store_only_option` and the MCP checks, USAGE,
  ARCHITECTURE, README and the migration guide of the CHANGELOG, the smoke
  runs, and the status lines of the superseded ADR-048 on
  `claude/vigilant-faraday-finqvd` (ADR-054 names it by its branch, because
  `develop` has another ADR-048). The branch is rebased onto `chore/nogat-2.1`
  later: that branch holds the standard 2.1 adoption and moves the texts into
  the message catalog (ADR-053) area by area.
- **IMGWTools**, 21 commits on `chore/nogat-2.1` `b526f16`. Done: ADR-007;
  `--output-dir` (`-o`), `--root`, `--output` and `--force`; `IMGW_ROOT` and the
  default root `<data_dir>/imgw`; plain `datasets download`, `store sync` and
  `pmaxtp sync` with preflight, `.imgw-incoming/` and the `--check` plan; the
  marker with `tool`, `created_at` and `producer_version`, written by the first
  write, and `store init`; nested stores by marker name; `new` and `unchanged`;
  `files[]`; the MCP `--allow-dir`; `imgwtools.testing`; the "Migration guide:
  data output" of its CHANGELOG for the consumers. Open: a smoke run against the
  real servers (no `live` test covers plain mode), the author's review, and the
  fold of `[Unreleased]` into `[3.0.0]` at the tag.
- **Archiwista.** Step 4 waits for the producers' heads (its Next 2 lists the
  call sites). Its standard 2.1 adoption is in progress: the error registry
  and the job error codes are done, the message catalog is parked on
  `wip/message-catalog`.
- **Retman**, seven commits on `chore/nogat-2.1` `f6ac4d1`. The IMGWTools half
  is done: `output_dir` and `output`, `new` and `unchanged`,
  `IMGW_REFERENCE_DIR`, the marker states of a store folder (`no_marker`, the
  `api_keys.json` state file), ADR-024 and the user documents. The Kartograf
  half (`root=`, the error codes) waits for Kartograf's branch.
- **Hydrolog.** Step 6 is done on `chore/nogat-2.1` (16 commits on `develop`):
  INTEGRATION, USAGE and the generated guide name `kartograf soil download
  --output-dir`, `download_soil(output_dir=)`, `files[].path` and `imgw series
  export --output`, and Hydrolog checks the names when the producers' releases
  land (its Next 3). Beyond the plan, `feature/routing-network` (20 commits on
  `chore/nogat-2.1`, six branches in one line, merge order in its
  `docs/plans/2026-10-25-flood-routing-summary.md`) adds the `route` group and
  `route network`: the document `hydrolog-network/1` with its JSON Schema, one
  hydrograph table `<id>.csv` per node and the plain mode of a directory
  (`--output-dir`, `-o`, DEV-19.5, DEV-19.6, DEV-19.11; ADR-0010). Open for
  DEV-10.6: Hydrolog has no `hydrolog.testing`, which falls due now that
  Hydraulik reads its tables (an edge via `file`).
- **Hydrograf.** Not part of this work: step 8 follows the first release set.
  Its PROGRESS asks the registry for two changes, left until its branch is
  merged: drop `backend/requirements.txt` from `python_manifests` (the uv step
  deleted it) and revise `uses` of Kartograf after its migration.
- **Hydraulik**, 29 commits on `develop` `de97009`. Done ahead of the release
  set, not merged: plain files only (ADR-0001); `terrain download` starts the
  `kartograf` program with `--check` and `--output-dir` and refuses a Kartograf
  whose `output_dir` is not `path_role: output` (ADR-0006); `rainfall build`
  from Hydrolog shapes and IMGWTools depths; `swmm run` and `model couple` read
  the tables of `hydrolog route network` (ADR-0009, checked on Hydrolog
  `081fda2`). The Kartograf calls run against a fake program: the live run
  waits for Kartograf's plain mode, and the field names of its plan and the ids
  of its items are what may differ. The proof of concept stays uncommitted in
  the `Hydraulik` checkout; the merge plan is in its PROGRESS.

Pins of one project on another (`uv run scripts/ecosystem.py drift`, and the
`pyproject.toml` of the Hydraulik branch):

| Consumer | Producer | Pin | State |
|---|---|---|---|
| Retman | IMGWTools | commit `a304521`, the head of `feature/data-output` | local only: not on GitHub, resolves where the uv git cache holds it |
| Retman, Archiwista | Kartograf | commit `8e9bcbb` | on `origin/develop`; moves to the head of `feature/data-output` when step 2 is complete and pushed |
| Hydraulik | Hydrolog, IMGWTools | tags `v0.7.0`, `v2.1.1` (extra `rainfall`) | pushed; no Hydrolog tag has `route network` yet |
| Hydrograf | Kartograf, Hydrolog, IMGWTools | tags `v0.7.0`, `v0.6.3`, `v2.1.0` | pushed, behind the latest tags; changes after the first release set |

Integration check: not run. IMGWTools (`a304521`), Hydrolog (`6c9ba5a`) and
Retman (`932d2cf`) are candidates; Kartograf is not until step 2 is complete,
and Archiwista waits for it (step 4). Hydraulik and Hydrograf are not members
of the check (step 8); Hydraulik's live `terrain download` needs Kartograf's
plain mode.
