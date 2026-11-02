# Plan: Archiwista's sets as Hydrograf's only Kartograf input

Requirements: HUB-5.2, DEV-17.4, DEV-3.4, DEV-17.5, AGI-3.3, ECO-054. Builds
on the approved [projects plan](2026-10-31-archiwista-projects.md)
(`archiwista-project/1`, Archiwista's A-ADR-049) and replaces step S5 of
Hydrograf's store migration plan (`docs/plans/2026-11-02-store-migration.md`
on Hydrograf's `feature/store-migration`, worktree `Hydrograf-store`).
Proposed: no code starts before the author approves it.

## Goal

The author's variant B of 2026-11-02:

- Archiwista is the only program that writes Kartograf data into the store
  shared with Hydrograf, `/home/claude-agent/data/archiwista-public/store`
  (Archiwista's store `zespol`).
- Hydrograf reads that store only through a project and one of its sets
  (zestaw: a group of pins of `archiwista-project.json`), strictly: every
  Kartograf input of the bootstrap is a pin of the set, checked by SHA-256;
  a missing or changed input stops the run with a code of the error registry
  and a hint naming the Archiwista action that fixes it.
- With `--bbox`, `--sheets` or `--boundary-file` Hydrograf still downloads,
  but only into its private store `<cache_dir>/kartograf` (Hydrograf's
  ADR-061); against the shared store these options are refused.
- IMGW PMAXTP (step 6 of the bootstrap) stays outside sets.
- Order: Archiwista's part on the Kartograf side first (its uncommitted fix
  of the project area, then one set of NMT 5 m, BDOT10k and SoilGrids/HSG),
  then Hydrograf's input, then S5: the bootstrap of the production area from
  the set in staging, the clip to the Kaczawa catchment above 51.222825 N,
  16.179380 E, and the results published again.

## Where it starts

Checked on 2026-11-02 at Kartograf `26ee459` (the checkout `07cfed48` adds
one documentation commit), Archiwista `e9a18b9` with its uncommitted fix (the
instance on :8090 runs `dd4268c`) and Hydrograf-store `a86204e`. Paths are
relative to each repository unless absolute.

### The store and its writers

- `kartograf-store/1`, 2.7 GB, four NMT segments, 735 versions; the marker
  `kartograf-store.json` names no identity of the store (schema, tool,
  `created_at`, producer version).
- Hydrograf's ADR-066 made the bootstrap a second writer: a `run --rm`
  container with `HYDROGRAF_KARTOGRAF_STORE_MODE=rw`
  (`docker-compose.staging.yml:32`), guarded by `writes_in_progress`
  (`backend/utils/kartograf_store.py:78`, called in
  `backend/scripts/bootstrap.py:448-458`). POSIX ACL on the store:
  `user:999:rwx` with default entries for `999` and `claude-agent`; its
  parents are 700 without ACL, which a bind mount does not traverse
  (ADR-066, fact 5).

### What Kartograf writes, and with which modes

Measured offline on this host: Kartograf's own functions under umask 077
(Archiwista's service has `UMask=0077`), writing into a throwaway directory
with ADR-066's ACL, `TMPDIR` once on `/tmp` (tmpfs) and once on `/`:

| Writer | Code | UID 999 |
|---|---|---|
| BDOT10k county package (`landcover download --product bdot10k` goes to `Bdot10kProvider`, `src/kartograf/landcover/manager.py:163`) | layers extracted and merged in `TMPDIR` (`src/kartograf/providers/pl/bdot10k.py:711`, `:821`), the merged file copied by content into the staging directory (`shutil.copyfile`, `:841`), `os.replace` there (`:751`) | reads (mask `rw-`), both `TMPDIR`s |
| `_unpack_checked_layers` (`src/kartograf/transport/unit_package.py:559-588`: `tempfile.mkdtemp` `:571`, `shutil.move` `:586`) | only channels with `unpack_layers`: RCN transaction prices, `pl.gugik.rcn` (`src/kartograf/sources/registry.py:1550-1555`) | cannot: mask `---` across file systems (`copy2` copies mode 600), no entry at all on one file system (the rename keeps the 600 file) |
| `_fetch_features` (`src/kartograf/download/collections.py:3182-3195`, the same `mkdtemp` and `shutil.move`) | WFS feature cut-outs (`FeatureBBoxParams`: BDOO, PRG addresses and special objects, trees, Czech ZABAGED and RÚIAN) | cannot [code reading: the same pattern] |
| SoilGrids inputs | `<file>.<pid>_<tid>.tmp` beside the target, `os.replace` (`src/kartograf/transport/http.py:346-354`) | reads [code reading] |
| HSG raster (`soil hsg`) | temporary directory only for warped inputs (`src/kartograf/hydrology/hsg.py:1391`); the raster is written at its staging path and published by `store_file` (`:1022`) | reads [code reading] |
| NMT sheets | `new_incoming_dir` (`src/kartograf/download/versions.py:187`), `os.link` (`:478`) | reads (S4's smoke as UID 999) |

The products of the set are not affected. ADR-066 fact 4 names the wrong
function for BDOT10k: the defect is real, but in two writers the set does
not use. A fix there keeps SQLite on the local copy, as the module requires
(`unit_package.py:22-26`: no byte-range locks on a network store, Kartograf's
ADR-042 D5).

### Temporary space and disk

- BDOT10k is extracted and merged in `TMPDIR`; a county takes about twice its
  package there, and its ZIP is held in memory (`bdot10k.py:674-678`).
  Archiwista's service sets no `TMPDIR`
  (`~/.config/systemd/user/archiwista-public.service`), so it uses `/tmp`:
  tmpfs of 7.8 GB with 738 MB free (4.8 GB in `/tmp/pytest-of-claude-agent`,
  1.7 GB in `/tmp/nogat-test`).
- `/` (ext4, holds the store): 12 GB free, 95 % used. The set adds about
  0.83 GB there: BDOT10k of ten counties 794 MB (the sizes of the same
  packages in production's cache; 0205 and 0226 have the SHA-256 of S3's
  downloads of 2026-11-02), SoilGrids of Poland 3 × 10.6 MB, HSG 0.6 MB, two
  sheets about 3 MB. The 205 sheets are in the store already (313 MB).

### Archiwista

- **The uncommitted fix** (A-ADR-049 erratum 5). The index holds commit 1,
  backend (20 files): `POST /commands/area`, `archiwista commands area`, the
  source capability `AreaCommandAdapter` and Kartograf's `with_area`. The
  unstaged changes are commit 2, web (21 files): „Obszar projektu” in the
  map's step 1 and the Katalog's area filter, „Obszar polecenia” under
  „Wklej polecenie producenta”, the plan window's „Obszar” row, the card's
  „Pliki obszaru w Katalogu”. It lets a person run any Kartograf command
  that takes an area, `landcover download` and `soil hsg` included, on a
  project's area from the web interface. Its PROGRESS asks the author to
  confirm this interface change, made without a plan (decision D7).
- **The CLI does without the fix.** At `dd4268c`, `archiwista jobs start
  check|download kartograf --store zespol --call JSON …` accepts as
  `geometry` an area file Archiwista wrote
  (`src/archiwista/services/actions.py:11-13`):
  `xdg-data/archiwista/areas/88627fe9cd5763de.geojson`, whose SHA-256
  `c0c4a9ad…8a36` is that of Kaczawa's area. `--pin PROJEKT --pin-group
  ZESTAW` writes a new group. The CLI calls the services without HTTP, as the
  installation's owner (`src/archiwista/commands/jobs.py:1-25`; roles `admin`
  and `store_writer`, `src/archiwista/auth/principal.py:19-20`): no session
  and no token.
- **A set holds many calls.** One download job of one producer's calls
  becomes one `plan` group holding the calls in order
  (`src/archiwista/services/pins.py:419-477`; up to 1,000 calls,
  `src/archiwista/projects/document.py:43`), written only when every call
  succeeded (`src/archiwista/jobs/worker.py:889-890`, `job_partial`). A plan
  group takes no added pin (`pins.py:253-257`, `group_origin_plan`), a taken
  name is refused (`group_exists`), „Przepnij” replaces its pins after a full
  success. A set is therefore built by one job and changed by a new set or a
  re-pin.
- **Pins of the other products**, as Hydrograf's S3 store (same Kartograf)
  holds them: BDOT10k
  `landcover/pl_bdot10k_gpkg/versions/teryt/<date>_<sha8>/<TERYT>.gpkg`
  (one GeoPackage per county, label the download date), HSG
  `hsg/global_soilgrids_0-5cm_mean/versions/bbox/2.0_<sha8>/<box>.tif` (its
  sidecar lists the three inputs with SHA-256), SoilGrids
  `soil/global_soilgrids_<property>_0-5cm_mean/versions/bbox/2.0_<sha8>/<box>.tif`.
  A pin records producer, `version`, `sha256`, `size_bytes`, unit, label,
  `pinned_at` and `pinned_by`, as Kaczawa's NMT pins do.
- **The gate's hang.** `tests/e2e/test_guide.py` runs in both engines
  (`tests/e2e/conftest.py:33`, 113-117). A gate log of 2026-11-01 21:31
  (`~/data/tmp/gate-run.log`) shows pytest's 10-minute faulthandler dump at
  13 %: the main thread waits in Playwright's synchronous loop beside a
  server of `tests/fixtures/local_server.py`, which does not tell which test.
  [INFERENCE] Not caused by the change: the test drives the top bar and
  `/instrukcja`, which neither commit touches; the map view it opens differs
  only by the project areas it now fetches and offers (`useProjectAreas`,
  `src/archiwista/web/src/views/map.js`, `map/panel.js`, `map/source.js`).
  Its calls without a Playwright timeout (`set_viewport_size` of the guide's
  new tab, `evaluate`, `close`, lines 75-92) wait forever when Firefox stops
  answering; `/tmp`, where Firefox keeps its profile, was 91 % full.
- **Kaczawa lies in the project directory itself.** `project_dirs` is
  `["/home/claude-agent/data/archiwista-public/projects"]`
  (`xdg-config/archiwista/config.toml`), and Kaczawa's path is that directory
  (`index.sqlite`, table `projects`): its file and its `obszary/` sit beside
  the directories of `wolin`, `kamiennik` and `test`. Access is keyed by the
  path (`state.sqlite`, `project_acl`). Files 600 and directories 700 without
  ACL: UID 999 cannot read them, and a grant or a bind mount of Kaczawa's
  directory would cover every other project. Deleting a project removes only
  what Archiwista wrote (`src/archiwista/services/projects.py:601-610`); a
  project created by the CLI gets no owner (`:331-337`).
- **The instance on :8090.** The systemd user unit `archiwista-public.service`
  runs `/home/claude-agent/data/archiwista-public/app/.venv/bin/archiwista
  serve --host 127.0.0.1 --port 8090` from the detached worktree
  `/home/claude-agent/data/archiwista-public/app` at `dd4268c`, with
  `XDG_CONFIG_HOME` and `XDG_DATA_HOME` of that directory (also `env.sh`),
  `Restart=on-failure`.

### Coverage of the Kaczawa area

Computed with Kartograf's `find_sheets` and sheet outlines and GeoPandas in
EPSG:2180; counties by `landcover download --check` (PRG), the extra sheets by
`elevation download --check`, both into a throwaway store:

- Kaczawa's area (`obszary/88627fe9cd5763de.geojson`, 827.68 km²) is the
  production area `data/boundary/obszar_mniejszy.gpkg` (0 km² apart).
- Sheets by shape (Kartograf's ADR-058): 205, exactly the pins of set „2020”.
  Production's `mniejszy_sheets.txt` has 207: `M-33-33-C-b-2-1` and
  `M-33-45-B-c-1-1` come from an envelope rule and touch the area with 0 m²;
  both have NMT 2020 at the source (`2020-04-18_73715`).
- The clip boundary `zlewnia_kaczawy_790km2_przyciecie.gpkg` (790.56 km²) is
  not inside the area: 2.87 km² lie outside in 767 slivers (44 above
  0.01 km², the largest 0.47 km², up to 979 m deep), and the outlet lies
  972 m outside it. The 205 sheets cover the boundary except 935 m², which
  lie in `M-33-45-B-c-1-1`; the 207 cover it whole.
- Counties: the same ten for the area's envelope, the box of the sheets'
  mosaic (274133, 335602, 313598, 377619) and the clip boundary: 0205, 0206,
  0207, 0209, 0218, 0219, 0221, 0226, 0261, 0262.
- HSG: `soil hsg --geometry` takes the area's envelope (275713, 335521,
  313347, 377471), which holds the clip boundary but stops up to 1.6 km short
  of the mosaic's west edge; step 5 uses Poland's box (167000, 29000, 860000,
  814000) today.

### What Hydrograf reads from Kartograf

| Place | Reads today |
|---|---|
| Step 2, `step_download_nmt` (`backend/scripts/bootstrap.py:426-475`) | `download_sheets` into `store_dir()`, standard paths (`:460`) |
| Step 3, `step_process_dem` (`:477-577`) | the mosaic of step 2's files; BDOT10k of the counties of the mosaic's box (`download_bdot10k`, `:530`) for burning and the frontend |
| Step 4, `step_landcover` (`:580-615`) | the same counties (`:598`), `import_landcover` per package |
| Step 5, `step_soil_hsg` (`:618-802`) | `calculate_hsg(root=store, bbox=Poland, depth=0-5cm)` (`:654`), clipped to the mosaic's box at 250 m with nearest-neighbour fill (`:669-716`) |
| `core/cn_calculator.py:160-167`, `:265-267` | HSG from SoilGrids into a temporary directory and BDOT10k into the store, when `core/land_cover.py:327-330` finds no land cover in the database (`scripts/analyze_watershed.py:313`) |
| `scripts/analyze_watershed.py:122-138`, `scripts/prepare_area.py:258`, `:336` | every 5 m sheet of the store; BDOT10k downloads |
| Admin panel, `POST /bootstrap/start` (`backend/api/endpoints/admin.py:602`) | starts the bootstrap with `bbox`, `sheets` or `boundary_file`; in staging the API's store is read-only, so it fails in step 2 |

The serving API reads no Kartograf data per request. Errors are
`HydrografError(message_id, reason=, code=)` with registry codes and texts in
`core/messages.py` (`backend/core/errors.py:17`); the bootstrap exits 1
(`bootstrap.py:1436`, `:1513`). Constants: `SHEET_SYSTEM = "1992"`,
`HSG_DEPTH = "0-5cm"` (`backend/utils/kartograf_store.py:43-45`).

## Options

| Option | Verdict |
|---|---|
| A. Keep ADR-066: the bootstrap writes the shared store too | Rejected by the author: two writers, a time guard, results not tied to a set |
| B. Archiwista alone writes; Hydrograf reads a set strictly and stops on a missing input | Chosen by the author on 2026-11-02 |
| C. Hydrograf reads a set and downloads what it lacks into its private store | Rejected: a run would mix pinned and unpinned data without saying so |

Choices inside B, recorded in Hydrograf's new ADR:

| Question | Choice | Why |
|---|---|---|
| How the container sees the store and the project | read-only bind mounts at their host paths; `HYDROGRAF_KARTOGRAF_ROOT` names the store's path | the project file's absolute store root holds as written; no mapping of paths to keep in step |
| Which sheets the set must hold | `find_sheets(geometry=<area>, scale="1:10000", sheet_system="1992")`, offline (`src/kartograf/sheet_info.py:366`); pinned sheets beyond them are used too | the rule Archiwista's call applied (ADR-058) |
| Which counties | Kartograf's PRG answer for the mosaic's box (`discover_teryts_for_bbox`, `src/kartograf/providers/pl/prg.py:361`), the rule of steps 3 and 4 today | the set's own call cannot prove what it covers; PRG is a lookup, not data |
| Which pin is which product | the segment of its `version`: `nmt/pl_1992_<resolution>_evrf2007/`, `landcover/pl_bdot10k_gpkg/`, `hsg/global_soilgrids_0-5cm_mean/`; other pins (SoilGrids inputs) are verified, not used | Kartograf's store layout |

## Decision

Option B.

### The set

A new set of the Kaczawa project, in its own directory
`/home/claude-agent/data/archiwista-public/projects/kaczawa` (step A3),
built by one download job (D1). `AREA` is
`/home/claude-agent/data/archiwista-public/xdg-data/archiwista/areas/88627fe9cd5763de.geojson`;
the group's calls name it as `obszary/88627fe9cd5763de.geojson` (A-ADR-049
erratum 3). The calls, as `archiwista commands parse` reads them:

| # | Call | Selects |
|---|---|---|
| 1 | `{"command": "elevation download", "options": {"product": "nmt", "country": "pl", "geometry": AREA, "resolution": "5m", "vertical_crs": "EVRF2007", "sheet_system": "1992", "year": 2020}}` | the 205 sheets (local) |
| 2, 3 | the same with `"sheet": "M-33-33-C-b-2-1"`, then `"sheet": "M-33-45-B-c-1-1"`, in place of `geometry` (D3) | two sheets to download |
| 4 | `{"command": "landcover download", "options": {"product": "bdot10k", "geometry": AREA}}` | ten counties |
| 5 | `{"command": "soil hsg", "options": {"depth": "0-5cm", "bbox": [167000.0, 29000.0, 860000.0, 814000.0], "bbox_crs": "EPSG:2180"}}` (D4) | three SoilGrids inputs and the HSG raster |

### Hydrograf's strict input

`python -m scripts.bootstrap --project PATH --set NAME`, exclusive with
`--bbox`, `--sheets` and `--boundary-file`. Before step 1 it reads and checks
everything; `--dry-run` stops after the checks and prints what the run would
use:

1. `PATH/archiwista-project.json` with `schema: archiwista-project/1`; the
   area file below `PATH` with its recorded SHA-256; the set by its name
   (compared case-folded, as Archiwista does); the Kartograf store of the
   file (absolute, or relative to `PATH`) with its marker; when
   `HYDROGRAF_KARTOGRAF_ROOT` is set it must be the same directory.
2. Every pin of the set: the file at `<root>/<version>` with its size and
   SHA-256 (about 1.1 GB, seconds).
3. What the run needs: the sheets of the area (choices above) among the
   pins of the NMT segment of `--resolution`; the counties of the mosaic's
   box among the BDOT10k pins (unless `--skip-landcover`); one HSG pin whose
   raster covers the area's envelope (unless `--skip-hsg`). One version per
   sheet, county and raster.
4. Steps 2 to 5 take the pinned files by their version paths, which never
   change: step 2 downloads nothing and logs `N/N arkuszy z zestawu`, steps
   3 and 4 read the pinned packages, step 5 the pinned raster; the rest of
   each step stays. No Kartograf download function runs; the store and the
   project are mounted read-only. The log names the project, the area's
   SHA-256, the set, the pins per product and a digest of the sorted pins
   (`version`, `sha256`), which ties a database to its set.

A failure ends the run with the registry's exit code and, as the last line of
standard error, the error document (AGI-3.3):

| Situation | Code | `details.reason` | Hint |
|---|---|---|---|
| `--project` without `--set`, or with an area option | `validation_error` | the parser's | – |
| `--bbox`, `--sheets`, `--boundary-file` while `HYDROGRAF_KARTOGRAF_ROOT` is set | `forbidden` | `shared_store_read_only` | use `--project` and `--set`, or unset the variable to download into `<cache_dir>/kartograf` |
| no project file | `not_found` | `project_file_missing` | the directory of the project's card in Archiwista |
| another schema | `unsupported` | `project_schema_unsupported` | a newer Hydrograf |
| the file breaks its format | `data_error` | `project_file_invalid` | the project's card names the problem |
| the area file is missing, or its SHA-256 differs | `not_found`, `data_error` | `area_missing`, `area_changed` | Archiwista: set the project's area again on its card |
| no set of the name | `not_found` | `set_not_found` (`details.sets`) | the sets on the project's card |
| no Kartograf store, no root, no marker | `store_unavailable` | `store_missing` | the mount, or Archiwista's „Zmień…” of the store |
| the root is not `HYDROGRAF_KARTOGRAF_ROOT` | `validation_error` | `store_mismatch` | – |
| a pinned file is absent | `not_found` | `pin_missing` (`details.pins`) | Archiwista: „Przywróć brakujące” of the set (`archiwista project-restore`) |
| a pinned file's size or SHA-256 differs | `data_error` | `pin_changed` | Archiwista: „Weryfikuj” (`archiwista project-verify`), then „Przywróć brakujące” |
| a file cannot be read | `io_error` | `pin_unreadable` | the ACL of the new ADR |
| sheets, counties or the HSG raster missing from the set | `no_data` | `set_sheets_missing`, `set_counties_missing`, `set_hsg_missing` (with the units) | Archiwista: a new set whose call covers the project's area (a plan set takes no added pin) |
| PRG does not answer | `source_unavailable` | `prg_unavailable` | try again |
| two versions of one unit | `conflict` | `set_unit_ambiguous` | a set with one version per unit |

Every code is in the shared registry; no new code is needed.

### Refusals and what goes

- One guard in `backend/utils/kartograf_store.py`: with
  `HYDROGRAF_KARTOGRAF_ROOT` set, every function that may write a store
  (`download_bdot10k`, the wrapper of `download_sheets`, `calculate_hsg` with a
  root) refuses with `forbidden`, so `download_dem`, `download_landcover`,
  `prepare_area`, `analyze_watershed --download` and the CN fallback refuse
  too. The panel's `POST /bootstrap/start` answers `403` problem+json before
  it starts a process. Unset, the private store works as it does now.
- Removed (no shims): `writes_in_progress` and its guard in step 2,
  `HYDROGRAF_KARTOGRAF_STORE_MODE`, the rw container of S5, and ADR-066's
  rule that nobody downloads in Archiwista while a bootstrap runs.

### Mounts and permissions

- Staging mounts the store and the project directory read-only at their host
  paths: `${HYDROGRAF_KARTOGRAF_STORE}:${HYDROGRAF_KARTOGRAF_STORE}:ro` with
  `HYDROGRAF_KARTOGRAF_ROOT: ${HYDROGRAF_KARTOGRAF_STORE}`, and
  `${HYDROGRAF_PROJECT_DIR}:${HYDROGRAF_PROJECT_DIR}:ro`.
- UID 999 reads only: ACL `u:999:rX` with default entries on the store
  (narrowed from `rwX`) and on Kaczawa's directory. Archiwista writes its
  project file with mode 666 beside it (`src/archiwista/projects/files.py:590-597`),
  so a default entry keeps every new version of the file readable.

### ADR

A new ADR-067 in Hydrograf (D9) records the decision, the choices above, the
error table, the mounts and the ACL, and corrects ADR-066 fact 4. ADR-066
gets „Superseded in part by ADR-067” (decisions 2 and 4).

## Steps

Producers before consumers (HUB-5.2). Each step runs in its repository's
session on a branch of that repository (DEV-3.4), with its gate,
CHANGELOG and PROGRESS. Merges wait for the author (DEV-3.3), and so, by
this plan, do pushes and the deploy on :8090. K0 is the production check of
Hydrograf's migration plan (containers, image, production checkout,
`/health`): run before and after every step from A2 on, the result an empty
diff and 200. Sizes in sessions.

| # | Repository | Step | Who | Size | After |
|---|---|---|---|---|---|
| N1 | Nogat, `plan/archiwista-sets-hydrograf` | this plan | agent | done | – |
| KF | Kartograf, a `fix/` branch from `feature/archiwista-projects` | mode-safe writes of the two affected writers (optional, D10) | agent | 0.5 | approval |
| A1 | Archiwista, `feature/archiwista-projects` | the two commits of the area fix, the hang, the full gate | agent | 0.5-1 | approval, D7 |
| A2 | Archiwista, instance :8090 | deploy A1's head, rollback ready | agent in the author's window | 0.25 | A1, D6 |
| A3 | Archiwista, data | Kaczawa in its own directory | author, web interface | minutes | approval |
| A4 | Archiwista, data | the set, by the CLI | agent, after the author approves the check | 0.25-0.5 | A3, D1-D5 |
| H1 | Hydrograf, `feature/store-migration` | ADR-067, `--project`/`--set`, refusals, tests, documentation | agent | 1.5-2 | approval; its smoke after A4 |
| H2 | Hydrograf, staging | mounts, ACL, image | agent | 0.25 | H1, A4 |
| S5 | Hydrograf, staging | the bootstrap from the set, clip, results; S5's text in the migration plan | agent | 1 | H2, SFINCS window (K1) |
| N2 | Nogat | registry edges, Results, PROGRESS | agent | 0.25 | H1 |

H1's code may start when the plan is approved; its smoke, H2 and S5 wait for
A4. A3 and A4 do not need A1 and A2: the CLI path works at `dd4268c`.

### KF: Kartograf (optional)

- `_unpack_checked_layers` keeps the check on the local copy and writes the
  staged file by content (`shutil.copyfile` to a temporary name beside it,
  then `os.replace`, the pattern of `unpack_member`, `unit_package.py:546-556`)
  instead of `shutil.move` (`:586`); `_fetch_features` the same for its
  `result.gpkg` (`collections.py:3195`).
- A regression test: under `os.umask(0o077)`, into a staging directory with a
  default ACL naming another user, both functions leave that entry in effect
  (mask not `---`); skipped where `setfacl` is missing.
- Acceptance: Kartograf's gate green, CHANGELOG „Fixed”. Archiwista and
  Hydrograf take the commit at their next re-pin; the set does not need it.

### A1: Archiwista, the area fix

- Commit the index as it stands (commit 1, backend), then the remaining
  changes (commit 2, web), with the messages the Archiwista session writes.
- The hang: with no pytest running, remove pytest's leftovers in
  `/tmp/pytest-of-claude-agent`; run `tests/e2e/test_guide.py` alone under
  `timeout 900` with `DEBUG=pw:api` at the new head and, in a throwaway
  worktree, at `e9a18b9`. Both hang: the environment or Firefox, not the
  change; bound the untimed calls (the phone part in a new context with its
  viewport instead of resizing the guide's tab) as its own `test(e2e)`
  commit. Only the new head hangs: bisect commit 2 (the map view's fetch of
  project areas first).
- Acceptance: the full gate green (50 to 60 minutes), PROGRESS without the
  „paused” entry; push after the author's approval.

### A2: Archiwista, deploy on :8090

- Before: K0; no job waits or runs (`archiwista jobs list` with `env.sh`);
  copies of `index.sqlite` and `state.sqlite` by SQLite's backup API into
  `/home/claude-agent/data/tmp/`.
- Deploy: `git -C /home/claude-agent/data/archiwista-public/app checkout
  --detach <A1 head>`, `uv sync --locked` in that worktree, the line
  `Environment=TMPDIR=/home/claude-agent/data/tmp` in the unit (D6),
  `systemctl --user daemon-reload`, `systemctl --user restart
  archiwista-public.service`.
- Smoke: the unit active; `GET /` and `GET /api/v1/session/methods` 200 with
  the proxy headers of S4; `index.sqlite` read-only: store `zespol`
  available, three projects `ok`; the author sees „Obszar projektu”.
- Rollback: `checkout --detach dd4268c`, `uv sync --locked`, restart. Neither
  commit touches `index/` or `state/`, so the databases need no restore.

### A3: Archiwista, Kaczawa in its own directory

- The author, signed in: deletes the project „Kaczawa” (only
  `projects/archiwista-project.json` and `projects/obszary/…` go; set „2020”
  goes with them, its versions stay in the store), then creates „Kaczawa”
  („Kaczawa do Legnicy”) in `…/projects/kaczawa` with the area
  `88627fe9cd5763de`. The CLI could do both, but its project would have no
  owner.
- Acceptance (agent, read-only): the index has the project at
  `…/projects/kaczawa` with the area's SHA-256 `c0c4a9ad…8a36`, state `ok`,
  owner `piotr`; no project at `…/projects`.

### A4: Archiwista, the set

- Before: D1 to D5 decided, `df -h /` at least 5 GB free, K0.
- In a shell with `source /home/claude-agent/data/archiwista-public/env.sh`,
  `TMPDIR=/home/claude-agent/data/tmp` and `umask 077`:
  `archiwista jobs start check kartograf --store zespol --call … --json`
  with the five calls. Expected plan: 205 sheets local, 2 to download, ten
  counties, three SoilGrids inputs and the HSG raster (no sizes: Kartograf's
  KH). The author approves it.
- `archiwista jobs start download kartograf --store zespol --plan <check job>
  --call … --pin <Kaczawa's key> --pin-group "<D1>" --json`: exit 0, the
  summary's `pin.written` true. Then `archiwista project-verify <key>`.
- Acceptance: the project file holds the set with its five calls and every
  pin's file; „Weryfikuj” all `ok`; `/` about 0.83 GB fuller;
  `getfacl` of one BDOT10k and the HSG version shows `user:999` in effect;
  K0 unchanged. A failed call leaves no set (`job_partial`):
  `archiwista jobs retry`.

### H1: Hydrograf, the set as input

- ADR-067, the reader of `archiwista-project/1` (a new module in
  `backend/utils/`), the checks and the error table, steps 2 to 5 in set
  mode, the guard, the panel's refusal, the removals above, texts in
  `core/messages.py` in both languages, the bootstrap's documentation,
  CHANGELOG, PROGRESS.
- Tests: each refusal of the table, the requirements (a missing sheet,
  county, raster; two versions of a unit), the private store still
  downloading; a fixture project and store, no network.
- Acceptance: the gate green; in a `run --rm` container of staging on the
  real set: `--dry-run` exit 0 with 207 sheets, 10 counties and one raster;
  a copy of the project file with one changed SHA-256 (in
  `/home/claude-agent/data/tmp`) exit 7, `pin_changed`; `--bbox` exit 12,
  `forbidden`; K0 before and after.

### H2: Hydrograf, staging

- `docker-compose.staging.yml` and `.env.staging` as in „Mounts and
  permissions” (`HYDROGRAF_PROJECT_DIR=…/projects/kaczawa`); the ACL as the
  owner `claude-agent` with the `setfacl` of `~/scratch/store-pre-s5/acl/`:
  `setfacl -R -m u:999:rX` and `setfacl -R -d -m u:999:rX,u:claude-agent:rwX`
  on the store and on `…/projects/kaczawa`.
- `scripts/staging-compose.sh build api`, then `config`: both mounts
  `read_only: true`. Smoke as UID 999: the project file and every pin read,
  no write possible. K0 before and after.

### S5: Hydrograf, the production area from the set

The S5 section of Hydrograf's migration plan is rewritten in H2's session
(in Polish, as that plan is):

- Conditions: S4 confirmed, H1 and H2 done, the SFINCS window (K1), at least
  9 GB of free memory and 5 GB on `/`; the set verified in Archiwista. The
  rule that no Archiwista download may run goes.
- Set `s5`: database `hydro_s5`, directories `s5/…`; from production only
  `zlewnia_kaczawy_790km2_przyciecie.gpkg` (for the clip), `sewer_network.gpkg`
  and `sewer/`.
- Bootstrap in `run --rm` with `HYDROGRAF_STAGING_SET=s5
  HYDROGRAF_STAGING_DB=hydro_s5 HYDROGRAF_STAGING_API_MEM=8G`, no store mode:
  `--project …/projects/kaczawa --set "<D1>" --dry-run`, then without
  `--dry-run`; the rest of the configuration as before (reference: 4478 s for
  827.7 km²).
- The clip and the republication as the current S5 has them (`OUTLET` anew in
  `hydro_s5`, the boundary compared with that of 2026-11-01).
- Acceptance: exit 0; the log shows 207/207 sheets of the set, ten counties
  and the pin digest, kept with the results; the store unchanged (`iter_store`
  counts and Archiwista's index of `zespol` equal before and after, nothing
  new in `versions/.incoming`); the rest of the current criteria (790.57 km²
  ±0.5 %, `land_cover` and `soil_hsg` 100 % of the clip boundary,
  `is_sewer_augmented` 0, 51.0376/16.1723 about 15.16 km² ±2 %, Kamiennik
  about 37.23 km², SFINCS and the water on the profile, K0 unchanged). Land
  cover and CN are compared with production and the differences reported:
  today's BDOT10k packages may differ from those production downloaded
  between 2026-03-24 and 2026-10-29.

### N2: Nogat

- `ecosystem.yaml`: Hydrograf depends on Archiwista (`kind: data`, `via:
  [file]`, `exchange: [archiwista-project/1]`); its edge to Kartograf gains
  `store` and `kartograf-store/1`, and `find_sheets` and
  `discover_teryts_for_bbox` in `uses`. `map` and `agents` regenerated, this
  plan's Results, PROGRESS, CHANGELOG, the gate.

## Pins

| Consumer | Kartograf | Change |
|---|---|---|
| Archiwista | `26ee459` (`pyproject.toml`, `uv.lock`) | none: the set needs nothing newer; KF at its next re-pin |
| Hydrograf | `26ee459` (`backend/pyproject.toml` `[tool.uv.sources]`, `backend/uv.lock`); Hydrolog `5fa22b3`, IMGWTools `6bd35a4` | none; a re-pin needs `uv lock` and a new image |

## Decisions of the author

| ID | Question | Options | Recommended |
|---|---|---|---|
| D1 | The set's name and calls | a) a new set „Hydrograf 2020” of the five calls; b) another name or composition | a) |
| D2 | NMT year | a) 2020, as set „2020” and production; a re-pin stays on it; b) the newest (no `year`): a re-pin follows new flights | a) |
| D3 | Sheets | a) 207, production's (calls 2 and 3; 935 m² of the catchment lie in `M-33-45-B-c-1-1`); b) the 205 of the area | a) |
| D4 | HSG extent | a) Poland's box, as step 5 today (32 MB, reusable); b) the area's envelope (1.6 km short of the mosaic's west edge, filled there by the nearest class) | a) |
| D5 | Who runs the data operations | a) the author moves the project (its owner), the agent builds the set by the CLI after the author approves the check; b) the author does both in the web interface | a): one job holds the five calls; the web interface pastes one line per plan window (`PasteCommand`, `src/archiwista/web/src/map/source.js`), so b) gives one set per call |
| D6 | The deploy on :8090 | a) a window the author names, with `TMPDIR` on `/` in the unit; b) without the `TMPDIR` line | a): `/tmp` has 738 MB free, a county needs about twice its package |
| D7 | The interface of A-ADR-049 erratum 5 (`POST /commands/area`, `archiwista commands area`, `AreaCommandAdapter`), made without a plan | a) confirm it under this plan; b) change it first | a) |
| D8 | Bootstrap from a set in the admin panel | a) out of scope: the panel refuses against the shared store; a later plan, after S7; b) in H1 | a) |
| D9 | The ADR | a) a new ADR-067, ADR-066 superseded in part; b) an amendment of ADR-066 | a): the decision reverses who writes |
| D10 | Kartograf's mode fix | a) later, in Kartograf's own session (RCN and WFS cut-outs only); b) KF now | a) |
| D11 | UID 999 on the store | a) read only (`rX`), as Hydrograf no longer writes; b) keep `rwX` | a) |

## Risks

| Risk | Effect | Mitigation |
|---|---|---|
| `/tmp` (tmpfs) full | BDOT10k extraction fails in Archiwista, Firefox stalls in the e2e tests | `TMPDIR` on `/` for A4 and the unit (D6); pytest's leftovers removed before A1's gate |
| `/` at 95 % | the set adds 0.83 GB, a county up to 0.33 GB more for a moment | `df -h /` at least 5 GB before A4 and S5; the image build follows the migration plan's prune rule |
| The catchment leaves the area (2.87 km², the outlet 972 m out) | a mask by the area would cut the outlet off | the bootstrap never masks by the area; the requirements come from the area and the mosaic; S5 checks the clip's area and the 100 % coverage |
| PRG does not answer | no county check | `source_unavailable`, a retry; Hydrograf's metadata cache keeps answers |
| A re-pin of the set during a bootstrap | none for that run | all pins checked at the start, version paths never change, the pin digest names the set used |
| A pinned version removed from the store by hand | the run stops | `pin_missing` and „Przywróć brakujące” |
| `archiwista-project/1` changes | the reader fails | only that schema id is read (`unsupported` otherwise); a fixture copied from a real file in H1's tests |
| The project directory created again | the ACL is gone, `pin_unreadable` or an unreadable project file | ADR-067 names the grant; H2's commands again |
| The deploy breaks :8090 | the author's instance is down | rollback to `dd4268c`, database copies |
| The e2e hang returns | A1's gate blocked | A1's steps; the gate with `TMPDIR` on `/` |
| The CLI job dies with the agent's shell | no set | a failed job writes no group; `archiwista jobs retry` |
| Production touched by mistake | outage | K0 before and after every step; staging only through `scripts/staging-compose.sh`; the production checkout read only |

## Results

| Step | Repository and branch | Result |
|---|---|---|
| N1 | Nogat, `plan/archiwista-sets-hydrograf` | this plan, proposed |
