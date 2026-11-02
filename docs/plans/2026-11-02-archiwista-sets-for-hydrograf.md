# Plan: Archiwista's sets as Hydrograf's only Kartograf input

Requirements: HUB-5.2, DEV-17.4, DEV-3.4, DEV-17.5, AGI-3.3, ECO-054. Builds
on the approved [projects plan](2026-10-31-archiwista-projects.md)
(`archiwista-project/1`, Archiwista's A-ADR-049) and replaces step S5 of
Hydrograf's store migration plan (`docs/plans/2026-11-02-store-migration.md`
on Hydrograf's `feature/store-migration`, worktree `Hydrograf-store`).
Decided: the author's answers of 2026-11-02 are in „Decisions of the
author”; D6 (the deploy window on :8090) is still open, so nobody deploys.

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
- Order (the author's choice b of 2026-11-02): A1, Archiwista's
  uncommitted fix of the project area, gated; A2, draft sets in Archiwista
  („zestaw w budowie”, new); A3, the deploy on :8090; A4, the author moves
  Kaczawa into its own directory; A5, the author builds the set of NMT 5 m,
  BDOT10k and SoilGrids/HSG in the web interface as a draft set and closes
  it; then H2, Hydrograf's staging mounts, and S5: the bootstrap of the
  production area from the set in staging, the clip to the Kaczawa
  catchment above 51.222825 N, 16.179380 E, and the results published
  again. H1, Hydrograf's input, is written in parallel from now on.
- Consumers read only closed sets: an open set may change under them.

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
  downloads of 2026-11-02), SoilGrids of Poland 3 × 10.6 MB, HSG 0.6 MB. The
  205 sheets are in the store already (313 MB).

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
  re-pin; the web interface pastes one line per plan window (`PasteCommand`,
  `src/archiwista/web/src/map/source.js`), so it builds one set per call.
  Draft sets (step A2) lift this.
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
`/home/claude-agent/data/archiwista-public/projects/kaczawa` (step A4),
built by the author in the web interface as a draft set of three plan
windows and closed by him (D1, D5; step A5); its name is his (proposed
„Hydrograf 2020”, `SET` below). `AREA` is the project's area,
`/home/claude-agent/data/archiwista-public/xdg-data/archiwista/areas/88627fe9cd5763de.geojson`;
the group's calls name it as `obszary/88627fe9cd5763de.geojson` (A-ADR-049
erratum 3). The calls, as `archiwista commands parse` reads them:

| # | Call | Selects |
|---|---|---|
| 1 | `{"command": "elevation download", "options": {"product": "nmt", "country": "pl", "geometry": AREA, "resolution": "5m", "vertical_crs": "EVRF2007", "sheet_system": "1992", "year": 2020}}` (the author's year) | the 205 sheets of the area (local; D3) |
| 2 | `{"command": "landcover download", "options": {"product": "bdot10k", "geometry": AREA}}` | ten counties |
| 3 | `{"command": "soil hsg", "options": {"depth": "0-5cm", "bbox": [167000.0, 29000.0, 860000.0, 814000.0], "bbox_crs": "EPSG:2180"}}` (D4) | three SoilGrids inputs and the HSG raster |

No extra sheets (D3): `M-33-33-C-b-2-1` comes only from production's
envelope rule, and `M-33-45-B-c-1-1` holds about 935 m² of the catchment at
the divide, which S5 accepts as a tolerance.

### Hydrograf's strict input

`python -m scripts.bootstrap --project PATH --set NAME`, exclusive with
`--bbox`, `--sheets` and `--boundary-file`. Before step 1 it reads and checks
everything; `--dry-run` stops after the checks and prints what the run would
use:

1. `PATH/archiwista-project.json` with `schema: archiwista-project/1`; the
   area file below `PATH` with its recorded SHA-256; the set by its name
   (compared case-folded, as Archiwista does), closed: its `state` absent or
   `closed` (step A2); the digest of its pins, `pins_sha256` as A2 defines
   it, equal to the one the file records when it records one; the Kartograf
   store of the file (absolute, or relative to `PATH`) with its marker; when
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
   SHA-256, the set, its `closed_at` and `closed_by`, the pins per product
   and the set's `pins_sha256` (the file's, else computed), which ties a
   database to its set.

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
| the set is open („w budowie”) | `conflict` | `set_open` | Archiwista: „Zamknij zestaw” (`archiwista project-close`) |
| the recorded `pins_sha256` differs from the pins | `data_error` | `set_digest_mismatch` | the file was changed outside Archiwista: „Otwórz do edycji”, then „Zamknij zestaw” |
| no Kartograf store, no root, no marker | `store_unavailable` | `store_missing` | the mount, or Archiwista's „Zmień…” of the store |
| the root is not `HYDROGRAF_KARTOGRAF_ROOT` | `validation_error` | `store_mismatch` | – |
| a pinned file is absent | `not_found` | `pin_missing` (`details.pins`) | Archiwista: „Przywróć brakujące” of the set (`archiwista project-restore`) |
| a pinned file's size or SHA-256 differs | `data_error` | `pin_changed` | Archiwista: „Weryfikuj” (`archiwista project-verify`), then „Przywróć brakujące” |
| a file cannot be read | `io_error` | `pin_unreadable` | the ACL of the new ADR |
| sheets, counties or the HSG raster missing from the set | `no_data` | `set_sheets_missing`, `set_counties_missing`, `set_hsg_missing` (with the units) | Archiwista: „Otwórz do edycji”, a plan window adding a call that covers the project's area, „Zamknij zestaw” |
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
`/health`): run before and after every step from A3 on, the result an empty
diff and 200. Sizes in sessions. The draft sets of 2026-11-02 added step A2;
the steps A2, A3 and A4 of commit d2f17ac are now A3, A4 and A5.

| # | Repository | Step | Who | Size | After |
|---|---|---|---|---|---|
| N1 | Nogat, `plan/archiwista-sets-hydrograf` | this plan, the author's decisions | agent | done | – |
| KF | Kartograf, a `fix/` branch from `feature/archiwista-projects` | mode-safe writes of the two affected writers (optional, D10) | agent | 0.5 | later (D10 a) |
| A1 | Archiwista, `feature/archiwista-projects` | the two commits of the area fix, the hang, the full gate | agent | 0.5-1 | D7 (confirmed) |
| A2 | Archiwista, `feature/archiwista-projects` | draft sets: the file's members, routes, CLI, index, card, plan window, erratum 6 of A-ADR-049, the full gate | agent | 1.5-2 | A1, D12 |
| A3 | Archiwista, instance :8090 | deploy A2's head, rollback ready | agent in the author's window | 0.25 | A2, D6 |
| A4 | Archiwista, data | Kaczawa in its own directory | author, web interface | minutes | A3 |
| A5 | Archiwista, data | the set: three plan windows into a draft set, then „Zamknij zestaw” | author, web interface; agent checks read-only | 0.25-0.5 | A4, D1, D3-D5 |
| H1 | Hydrograf, `feature/store-migration` | ADR-067, `--project`/`--set`, closed sets only, refusals, tests, documentation | agent | 1.5-2 | now, in parallel; its smoke after A5 |
| H2 | Hydrograf, staging | mounts, ACL, image | agent | 0.25 | H1, A5 |
| S5 | Hydrograf, staging | the bootstrap from the set, clip, results; S5's text in the migration plan | agent | 1 | H2, A5, SFINCS window (K1) |
| N2 | Nogat | registry edges, the closed-set rule, Results, PROGRESS | agent | 0.25 | H1, A2 |

H1's code is written now, beside A1 and A2, against the file members A2
defines; its smoke, H2 and S5 wait for A5. A5 needs A1 to A3 on :8090: the
web interface builds the set only with the project's area in a pasted
command (A1) and with draft sets (A2).

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

### A2: Archiwista, draft sets

A set („zestaw”, a group of the project file) gets a state: `open`, a set
in the making („w budowie”) whose content changes, or `closed`, a frozen
set: no change of its content, no re-pin, nothing automatic; to change it a
person opens it („Otwórz do edycji”), edits or re-pins it, and closes it
again („Zamknij zestaw”, a new digest). The calls' options, `year`
included, are the set's intent: Archiwista never drops or changes one (a
re-pin, a check and a restore run the calls as written, only the area file
resolved to the project's, as today). On the branch of A1, after its
commits.

- **The file, additive in `archiwista-project/1`.** The reader ignores
  members it does not know and the writers keep them
  (`src/archiwista/projects/document.py:7-9`, `files.py:197-198`; A-ADR-049
  decision 2, H), so no `/2`. A group gains, all optional:
  - `state`: `"open"` or `"closed"`; absent is closed, so every set written
    before A2 (plan and local) is closed. Another value is an invalid file,
    rule `set_state`.
  - `closed_at` (UTC, `TIME_FORMAT`), `closed_by` (the account's id, `local`
    for the local owner) and `pins_sha256`: written together when Archiwista
    closes a set, all three or none, never on an open set (rule
    `set_closed_members`).
  - A plan origin may hold `selections`, as a local origin does: the hand
    pins of an open set that holds calls.
  - A pin of a plan group may hold `calls`, the ascending distinct indices
    of `origin.calls` whose runs pinned it: non-empty for a run's pin, `[]`
    for a pin added by hand; absent on pins written before A2, which belong
    to the group's calls as a whole, as today. Local groups' pins hold none
    (rule `pin_calls`). From A2 on every run that writes pins writes `calls`:
    a download into a new or an open set and a re-pin (which so also
    migrates an older set).
  - The origin follows the content: `plan` while the set holds a call (so
    1 to 1,000 calls, `MAX_GROUP_CALLS`, as an older reader requires),
    `local` otherwise. An empty draft is `local` with no selections; the
    first call turns it into `plan` (its selections kept in
    `origin.selections`, its hand pins get `"calls": []`); removing the last
    call turns it back into `local` (the `calls` members go).
  - An older Archiwista (`dd4268c`) reads such a file without the new
    members' rules: it keeps them but does not honour `state`, so a change
    there (A3's rollback) can leave a stale `pins_sha256`, which Archiwista
    and Hydrograf then report (`set_digest_mismatch`).
- **The digest.** `pins_sha256` is the lowercase hexadecimal SHA-256 of the
  UTF-8 bytes of the lines `<producer>\t<version>\t<sha256>\n`, one per pin
  of the set, sorted by (`producer`, `version`) by code point, the three
  strings exactly as the file holds them (a tab or a line feed cannot occur
  in them: `_PRODUCER`, `_relative` with `_plain`, `_SHA256`). Only the pins'
  identity counts: their `calls`, `pinned_at`, labels and the origin do not.
  A closed set always has a pin, so the empty input is never written. Test
  vector, shared with Hydrograf's H1: the pins (`kartograf`,
  `nmt/pl_1992_5m_evrf2007/versions/b.asc`, 64 × `b`) and (`kartograf`,
  `hsg/a.tif`, 64 × `a`), in that order, give
  `e7319a8d77a126fc2eb12f46b92ef5ac98a5b2132808474eebbb222fd5c691fe`. One
  function, `archiwista.projects.document.pins_digest`, computes it for the
  writers and the index.
- **What a state allows.**

  | Action | Open set | Closed set |
  |---|---|---|
  | a plan window's download pinning into it (`pin.add`) | its calls and pins are appended after a whole success | `409 conflict`, `set_closed` |
  | „Dodaj do projektu…” (`POST …/groups/{group}/pins`), any origin | added; recorded in `origin.selections` | `409 conflict`, `set_closed` (replaces `group_origin_plan`) |
  | „Odepnij” (`…/unpin`), „Usuń polecenie” | yes | `409 conflict`, `set_closed` |
  | „Przepnij” (`project_repin`) | yes; stays open | `409 conflict`, `set_closed`, before a job exists (`services/project_jobs.py:start`), and again by the worker under the lock |
  | „Weryfikuj”, „Sprawdź aktualizacje”, „Przywróć brakujące”, „Eksportuj…” | yes | yes |
  | „Usuń zestaw” | yes | yes, as today |
  | „Zamknij zestaw” | the checks below | `409 conflict`, `set_closed` |
  | „Otwórz do edycji” | `409 conflict`, `set_open` | yes |

  A set created by „Dodaj do projektu…” or by a plan window's download
  without `open` is written closed at once, with the three members (its
  pins are versions the index holds or the job's own files); with `open`,
  or when it would be empty (every version skipped), it is open. Adding to
  an older local set needs „Otwórz do edycji” first: the pin dialog's
  „Istniejący zestaw projektu” becomes „Zestaw w budowie” and lists open
  sets only.
- **Calls into an open set.** `POST /jobs` (kind `download`) takes
  `pin: {"project", "group", "add": true}` (into the open set `group`) or
  `pin: {"project", "group", "open": true}` (a new set left open);
  `check_plan_pin` (`src/archiwista/services/pins.py:369-416`) refuses before
  a job exists: no such set (`404`, `group_not_found`), a closed one (`409`,
  `set_closed`), a producer other than the set's (`409`, `set_producer`,
  D12), more than `MAX_GROUP_CALLS` calls together (`400`,
  `too_many_calls`), and the store rules of today (`other_store`,
  `unknown_store`). `pin_download` (`pins.py:419-560`) appends under the
  lock: it checks again that the set is open (closed or removed meanwhile:
  the job ends `partial` with the pin's error, the files stay; „Otwórz do
  edycji”, then `jobs retry`), appends the job's calls to `origin.calls`,
  and pins each file and each kept plan's position with `calls` naming its
  call (`files[].call`, the plan's place, offset by the calls the set held);
  a version the set pins already gains the index and keeps `pinned_at` and
  `pinned_by`. A job that is not `ok` writes nothing (`job_partial`, as
  today). Each window keeps its own check, plan and claims (A-ADR-036,
  ADR-047).
- **Removing a call.** `DELETE /projects/{project}/groups/{group}/calls/{call}`
  (`call` the 0-based index of `origin.calls`, as `files[].call` of a
  download's summary), open sets only: the index leaves every pin's `calls`
  and the higher ones shift down; a pin whose `calls` becomes empty that way
  goes, a hand pin (`[]`) and a pin of another call too stay. A set holding a
  pin without `calls` (written before A2) refuses it (`409 conflict`,
  `pins_without_calls`, the hint „Przepnij”, which writes them). Logged as
  `project.unpin` with `call` (the removed call) and the pins removed.
- **Jobs over a mixed set.** A pin with `calls`, or without the member, is
  checked, restored and re-pinned as a plan group's pins are today (the
  union of the set's calls' plans); a hand pin (`[]`) as a local group's
  pin, by its own call from `version_calls` / `command_for_version`, so a
  derived one (`soil hsg`) is `not_checkable`, `not_restorable` and blocks a
  re-pin (`command_not_rebuildable`). `_group_calls`
  (`src/archiwista/jobs/project_jobs.py:480-540`) returns both kinds;
  `_replace_pins` (`:741`) replaces the run pins by the runs' files with
  their `calls`, and each hand pin by the file of its call at its slot, only
  while the set is open (checked again under the lock: a set closed
  meanwhile ends the re-pin `partial`, no pin changed).
- **„Zamknij zestaw”.** `POST /projects/{project}/groups/{group}/close`
  (`project.write`: the owner or an administrator; the local owner may),
  a change of the file under its lock that answers the card. Refused, in
  this order: the set is closed (`409 conflict`, `set_closed`); a job that
  writes into it waits or runs, a `download` whose `params.pin` names the
  project and the set or a `project_repin` of the set (`409 conflict`,
  `set_job_active`, `details.job`; `JobSupervisor.active_set_job(project,
  group)` beside `active_project_job`, `src/archiwista/jobs/supervisor.py:1324`);
  the set has no pin (`409 conflict`, `set_empty`); a pin whose state in the
  index is not `ok`, that is `missing`, `sha256_mismatch` or `unknown` (`409
  conflict`, `set_pins_not_ok`, `details.counts` by state and
  `details.pins`, the first 100 with producer, version and state). The
  states are those of the last scan (A-ADR-049 decision 5); the card
  advises „Weryfikuj” before closing, without requiring it. Then it writes
  `state: "closed"`, `closed_at` (now, whole seconds), `closed_by` (the
  actor) and `pins_sha256`, and logs `project.set_close` (`group`, `pins`,
  `pins_sha256`). A restore that runs does not block it: it only writes the
  store, and can only turn a pin `ok`.
- **„Otwórz do edycji”.** `POST /projects/{project}/groups/{group}/reopen`
  (`project.write`): refused for an open set (`409 conflict`, `set_open`);
  writes `state: "open"`, removes `closed_at`, `closed_by` and
  `pins_sha256`, and logs `project.set_open` (`group` and the `closed_at`,
  `closed_by` and `pins_sha256` of the closing it ends). An older set
  (no `state`) is opened the same way.
- **Creating a draft.** `POST /projects/{project}/groups` takes `open`
  (default `false`); with `open: true` `versions` and `query` may be left
  out: an empty draft. Logged as `project.pin` with `open` (and `pins: 0`).
- **The command line**, as the other project commands, without HTTP:
  `archiwista project-draft PROJEKT ZESTAW` (an empty draft);
  `archiwista project-pin … --open` (a new set left open) and `--add` (into
  an open set); `archiwista project-unpin` (open sets only);
  `archiwista project-uncall PROJEKT ZESTAW --call N`;
  `archiwista project-close PROJEKT ZESTAW` and `archiwista project-reopen
  PROJEKT ZESTAW`, each with `--json` and the route's refusals as exit
  codes; `archiwista jobs start download … --pin PROJEKT --pin-group ZESTAW`
  with `--pin-add` or `--pin-open`.
- **The answers.** `ProjectGroup` (`src/archiwista/api/models.py:2868`)
  gains `state`, `closed_at`, `closed_by`, `pins_sha256` and `digest_state`
  (`ok`, `mismatch`, `null` without a recorded digest); `GroupOrigin` gives
  `selections` for a plan origin too; `ProjectPin` gains `calls`. The
  project list counts open sets.
- **The index** (rebuildable): `SCHEMA_VERSION` 16 to 17
  (`src/archiwista/index/schema.py:99`), so it rebuilds once at the start.
  `pin_groups` gains `state` (`open`, `closed`; `closed` for an absent
  member), `closed_at`, `closed_by`, `pins_sha256` and `digest_state` (the
  recorded digest compared with `pins_digest` of the pins when the file is
  read); `pins` gains `calls` (JSON, `NULL` without the member). The state
  database needs no migration (`action` is free text); `ACTION_NAMES`
  (`src/archiwista/state/store.py`) gains `project.set_close` and
  `project.set_open`, which the project's activity shows with the others
  (A-ADR-049 decision 14).
- **The web interface.** The card (`views/projects.js`, `Groups`,
  `GroupActions`, `PlanCalls`, `PinList`): a badge „w budowie” on an open
  set and „zamknięty {data} · {kto}” on a closed one with the first 12
  characters of `pins_sha256` (the whole in the title, copyable); „Zamknij
  zestaw” on an open set, disabled with its reasons in the `ReasonList` of
  `views/project-jobs.js` („Zadanie {rodzaj} zapisuje do zestawu.”, „{n}
  przypięć nie jest w stanie ok: brak {a}, inna suma {b}, nieznany magazyn
  {c}.”, „Zestaw jest pusty.”); „Otwórz do edycji” on a closed set, with the
  question „Otworzyć zestaw „{group}” do edycji? Programy, które czytają
  tylko zamknięte zestawy (Hydrograf), odmówią go do ponownego
  zamknięcia.”; „Odepnij” and „Usuń polecenie” (at each call) only on open
  sets; „Przepnij” of a closed set disabled with „Zestaw jest zamknięty:
  otwórz go do edycji, aby go przepiąć.”; „Nowy zestaw w budowie…” on the
  card; a warning for
  `digest_state` `mismatch`: „Skrót zestawu nie zgadza się z przypięciami:
  plik zmieniono poza Archiwistą. Otwórz zestaw do edycji i zamknij go
  ponownie.” The plan window (`views/plan.js`, `PinOption`): „Nowy zestaw”
  with the box „Zostaw w budowie”, or „Zestaw w budowie” choosing one of the
  project's open sets. The pin dialog (`views/pin-dialog.js`): „Zestaw w
  budowie” lists open sets only, with the hint that a closed set is opened
  on its card. Texts in `labels/pins.js`; the guide (`/instrukcja`) gets a
  part „Zestaw w budowie”. The download's result card says „Dodano do
  zestawu w budowie „{group}”: {count}.”
- **A-ADR-049, erratum 6** (the author's request of 2026-11-02 for draft
  sets): decisions 1 (the members, the digest), 5 (the index), 8 and 9
  (pinning into open sets, `group_origin_plan` gone), 11 (the jobs over
  mixed sets; a re-pin of a closed set refused; the calls' options, `year`
  included, never dropped or changed), 15 (`project.set_close`,
  `project.set_open`) and 16 (the routes and commands above), and D12.
  SPEC's projects part and the user guide follow.
- **Tests.** The file: each new rule (`set_state`, `set_closed_members`,
  `pin_calls`), unknown members kept, `local` to `plan` to `local`, the
  digest's test vector and its order independence. The services: every
  refusal of close (a download into the set, a re-pin of it, a missing pin,
  another SHA-256, an unknown store, an empty set, a closed set), reopen of
  an open set, a re-pin of a closed set refused before a job exists,
  a hand pin into an open plan set and into a closed one, the
  removal of a call (shifted indices, a pin of two calls stays, an older
  pin refused), `set_producer`, `too_many_calls`. The worker: a download
  with `add` appends calls and pins after a whole success, a partial one
  writes nothing, a set closed meanwhile ends `partial` with the error, a
  re-pin of a set closed while it ran ends `partial` with no pin changed; a
  re-pin's calls keep `year` and every other option as written; check,
  restore and re-pin of a set holding run pins and hand pins. The index:
  version 17, `digest_state` `mismatch` for a file edited by hand. The API's
  routes and problem documents, the CLI's commands, and e2e: the badge,
  „Zamknij zestaw” disabled with its reasons, „Otwórz do edycji” with its
  question, a plan window adding to an open set.
- Acceptance: `scripts/gate.sh` green (50 to 60 minutes, `TMPDIR` on `/`),
  CHANGELOG „Added”, PROGRESS; a smoke in a throwaway installation (XDG
  directories in `/home/claude-agent/data/tmp`, the generated store of
  `tests/fixtures/make_store.py`): a draft, hand pins, close refused for a
  missing pin, close, the digest computed by a one-line Python script equal
  to `pins_sha256`, reopen, close again.

### A3: Archiwista, deploy on :8090

- Before: K0; no job waits or runs (`archiwista jobs list` with `env.sh`);
  copies of `index.sqlite` and `state.sqlite` by SQLite's backup API into
  `/home/claude-agent/data/tmp/`.
- Deploy: `git -C /home/claude-agent/data/archiwista-public/app checkout
  --detach <A2 head>`, `uv sync --locked` in that worktree, the line
  `Environment=TMPDIR=/home/claude-agent/data/tmp` in the unit (D6),
  `systemctl --user daemon-reload`, `systemctl --user restart
  archiwista-public.service`. The index rebuilds once (`SCHEMA_VERSION` 17).
- Smoke: the unit active; `GET /` and `GET /api/v1/session/methods` 200 with
  the proxy headers of S4; `index.sqlite` read-only: store `zespol`
  available, three projects `ok`, their sets `closed`; the author sees
  „Obszar projektu” and „Nowy zestaw w budowie…”.
- Rollback: `checkout --detach dd4268c`, `uv sync --locked`, restart; the
  index rebuilds again at version 16 (or the copy is put back), the state
  database needs nothing. Project files written meanwhile stay readable
  there (unknown members ignored); a set changed there may carry a stale
  `pins_sha256` (A2).

### A4: Archiwista, Kaczawa in its own directory

- The author, signed in: deletes the project „Kaczawa” (only
  `projects/archiwista-project.json` and `projects/obszary/…` go; set „2020”
  goes with them, its versions stay in the store), then creates „Kaczawa”
  („Kaczawa do Legnicy”) in `…/projects/kaczawa` with the area
  `88627fe9cd5763de`. The CLI could do both, but its project would have no
  owner.
- Acceptance (agent, read-only): the index has the project at
  `…/projects/kaczawa` with the area's SHA-256 `c0c4a9ad…8a36`, state `ok`,
  owner `piotr`; no project at `…/projects`.

### A5: Archiwista, the set

The author does the data operations (D5) in the web interface on :8090;
the agent checks read-only.

- Before: A3 and A4 done, `df -h /` at least 5 GB free, K0; with D6 b (no
  `TMPDIR` in the unit) `/tmp` must have about 0.7 GB free for the largest
  county.
- On Kaczawa's card: „Nowy zestaw w budowie…” named `SET` (or „Nowy zestaw”
  with „Zostaw w budowie” in the first plan window). Then three plan
  windows, each checked at the source, its plan approved by the author and
  downloaded with „Dodaj do projektu” → „Zestaw w budowie” `SET`:
  1. NMT 5 m of 2020 by the project's area: the map's step 1 „Obszar
     projektu” or „Wklej polecenie producenta” with „Obszar polecenia” =
     Kaczawa, `elevation download --product nmt --resolution 5m --year 2020`
     (call 1 of „The set”). Expected plan: 205 sheets local, nothing to
     download.
  2. BDOT10k by the area: `landcover download --product bdot10k` with
     „Obszar polecenia” = Kaczawa (call 2). Expected: ten counties.
  3. HSG for Poland's box: `soil hsg --depth 0-5cm --bbox 167000 29000 860000
     814000 --bbox-crs EPSG:2180` (call 3, D4). Expected: three SoilGrids
     inputs and the HSG raster (no sizes: Kartograf's KH).
- „Weryfikuj” the set, then „Zamknij zestaw”. A window that fails writes
  nothing into the set (`job_partial`): „Ponów” on its job card.
- Acceptance (agent, read-only): the project file holds `SET` with `state`
  `closed`, `closed_by` `piotr`, three calls and 219 pins (205 sheets, ten
  counties, three SoilGrids inputs, the HSG raster), each with `calls`; its
  `pins_sha256` equals the digest computed from the file by a one-line
  script; `archiwista project-verify <key>` (read-only job) all `ok`; `/`
  about 0.83 GB fuller; `getfacl` of one BDOT10k and the HSG version shows
  `user:999` in effect; K0 unchanged.

### H1: Hydrograf, the set as input

- ADR-067, the reader of `archiwista-project/1` (a new module in
  `backend/utils/`), the checks and the error table, steps 2 to 5 in set
  mode, the guard, the panel's refusal, the removals above, texts in
  `core/messages.py` in both languages, the bootstrap's documentation,
  CHANGELOG, PROGRESS.
- Tests: each refusal of the table (an open set, a recorded `pins_sha256`
  that differs, A2's test vector of the digest), the requirements (a
  missing sheet, county, raster; two versions of a unit), a set without
  `state` read as closed, the private store still downloading; a fixture
  project and store, no network.
- Acceptance: the gate green; in a `run --rm` container of staging on the
  real set: `--dry-run` exit 0 with 205 sheets, 10 counties, one raster and
  the set's `pins_sha256`; copies of the project file (in
  `/home/claude-agent/data/tmp`) with one changed SHA-256 exit 7,
  `pin_changed`, and with `"state": "open"` `set_open`; `--bbox` exit 12,
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

- Conditions: S4 confirmed, H1 and H2 done, A5's set closed, the SFINCS
  window (K1), at least 9 GB of free memory and 5 GB on `/`; the set verified
  in Archiwista. The rule that no Archiwista download may run goes: the
  closed set does not change, and the run checks every pin at its start.
- Set `s5`: database `hydro_s5`, directories `s5/…`; from production only
  `zlewnia_kaczawy_790km2_przyciecie.gpkg` (for the clip), `sewer_network.gpkg`
  and `sewer/`.
- Bootstrap in `run --rm` with `HYDROGRAF_STAGING_SET=s5
  HYDROGRAF_STAGING_DB=hydro_s5 HYDROGRAF_STAGING_API_MEM=8G`, no store mode:
  `--project …/projects/kaczawa --set "SET" --dry-run`, then without
  `--dry-run`; the rest of the configuration as before (reference: 4478 s for
  827.7 km²).
- The clip and the republication as the current S5 has them (`OUTLET` anew in
  `hydro_s5`, the boundary compared with that of 2026-11-01).
- Acceptance: exit 0; the log shows 205/205 sheets of the set, ten counties
  and the set's `pins_sha256`, kept with the results; the store unchanged
  (`iter_store` counts and Archiwista's index of `zespol` equal before and
  after, nothing new in `versions/.incoming`); the catchment delineated on
  the mosaic of the 205 sheets (D3); coverage: the clip boundary lies in the
  mosaic but for at most about 0.001 km² at the divide in `M-33-45-B-c-1-1`
  (935 m² measured), and `land_cover` and `soil_hsg` cover the part of the
  clip boundary inside the mosaic, not 100 % of the old boundary; the rest
  of the current criteria (790.57 km² ±0.5 %, `is_sewer_augmented` 0,
  51.0376/16.1723 about 15.16 km² ±2 %, Kamiennik about 37.23 km², SFINCS
  and the water on the profile, K0 unchanged). Land cover and CN are
  compared with production and the differences reported: today's BDOT10k
  packages may differ from those production downloaded between 2026-03-24
  and 2026-10-29.

### N2: Nogat

- `ecosystem.yaml`: Hydrograf depends on Archiwista (`kind: data`, `via:
  [file]`, `exchange: [archiwista-project/1]`, `note`: reads one closed set
  of a project, read-only, ADR-067); its edge to Kartograf gains `store` and
  `kartograf-store/1`, and `find_sheets` and `discover_teryts_for_bbox` in
  `uses`. The contract rule of the exchange, in the summary of Archiwista's
  interface `archiwista-project/1`: a set has a `state` (`open`, `closed`;
  absent is closed) and a closed one `closed_at`, `closed_by` and
  `pins_sha256` (A2's definition); consumers read only closed sets, refuse
  an open one, and check a recorded `pins_sha256` against the pins.
  Recorded for A2 (Archiwista's side) and H1 (the first consumer); `map`
  and `agents` regenerated, this plan's Results, PROGRESS, CHANGELOG, the
  gate.

## Pins

| Consumer | Kartograf | Change |
|---|---|---|
| Archiwista | `26ee459` (`pyproject.toml`, `uv.lock`) | none: the set needs nothing newer; KF at its next re-pin |
| Hydrograf | `26ee459` (`backend/pyproject.toml` `[tool.uv.sources]`, `backend/uv.lock`); Hydrolog `5fa22b3`, IMGWTools `6bd35a4` | none; a re-pin needs `uv lock` and a new image |

## Decisions of the author

Answered by the author on 2026-11-02 unless marked otherwise; „default”
marks the coordinator's default, which the author may still override.

| ID | Question | Options | Decision |
|---|---|---|---|
| D1 | The set's name and calls | a) a new set „Hydrograf 2020” built by the agent by one CLI job; b) another way | replaced: the author builds the set himself in the web interface as a draft set of three plan windows and closes it (A5); its name is his (proposed „Hydrograf 2020”) |
| D3 | Sheets | a) 207, production's (two extra sheet calls); b) the 205 of the area | b): `M-33-33-C-b-2-1` comes only from production's envelope rule; `M-33-45-B-c-1-1` holds about 935 m² of the catchment at the divide, negligible (S5's tolerance) |
| D4 | HSG extent | a) Poland's box, as step 5 today (32 MB, reusable); b) the area's envelope (1.6 km short of the mosaic's west edge, filled there by the nearest class) | a): the author's set takes `soil hsg` for Poland's box |
| D5 | Who runs the data operations | a) the agent builds the set by the CLI; b) the author does them in the web interface | changed to b): the author moves the project (A4) and builds and closes the set (A5); draft sets (A2) give one set of several plan windows |
| D6 | The deploy on :8090 | a) a window the author names, with `TMPDIR` on `/` in the unit; b) without the `TMPDIR` line | open; recommended a): `/tmp` has 738 MB free, a county needs about twice its package. Nobody deploys before it |
| D7 | The interface of A-ADR-049 erratum 5 (`POST /commands/area`, `archiwista commands area`, `AreaCommandAdapter`, „Obszar projektu”, „Obszar polecenia”), made without a plan | a) confirm it under this plan; b) change it first | a), confirmed |
| D8 | Bootstrap from a set in the admin panel | a) out of scope: the panel refuses against the shared store; a later plan, after S7; b) in H1 | a), default |
| D9 | The ADR | a) a new ADR-067, ADR-066 superseded in part; b) an amendment of ADR-066 | a), default |
| D10 | Kartograf's mode fix | a) later, in Kartograf's own session (RCN and WFS cut-outs only); b) KF now | a), default |
| D11 | UID 999 on the store | a) read only (`rX`), as Hydrograf no longer writes; b) keep `rwX` | a), default |
| D12 | Producers of a draft set (new) | a) one producer per set: fixed by its first call or pin, a call or pin of another producer refused (`set_producer`); a local set of several producers' hand pins stays possible but takes no call; b) a producer per call: `producer` in each call, run pins of several producers in one plan set | open; recommended a): the Kaczawa set is Kartograf's alone, and IMGWTools has no commands until its v0.5; b) breaks the older reader within `/1` (it gives every call the group's `producer` and refuses a plan group's pin of another producer, `plan_producer`, `document.py:616-617`), so it needs `archiwista-project/2` or that loss; ask again with IMGWTools v0.5 |

The NMT year is no question: the author wrote `year: 2020` into the call,
and the year of a call is part of the set's intent, never dropped or
changed by Archiwista (A2).

## Risks

| Risk | Effect | Mitigation |
|---|---|---|
| `/tmp` (tmpfs) full | BDOT10k extraction fails in Archiwista, Firefox stalls in the e2e tests | `TMPDIR` on `/` in the unit before A5 (D6); pytest's leftovers removed before A1's and A2's gates |
| `/` at 95 % | the set adds 0.83 GB, a county up to 0.33 GB more for a moment | `df -h /` at least 5 GB before A5 and S5; the image build follows the migration plan's prune rule |
| The catchment leaves the area (2.87 km², the outlet 972 m out) | a mask by the area would cut the outlet off | the bootstrap never masks by the area; the requirements come from the area and the mosaic; S5 checks the clip's area and its coverage within the mosaic |
| PRG does not answer | no county check | `source_unavailable`, a retry; Hydrograf's metadata cache keeps answers |
| The set reopened during a bootstrap | none for that run | all pins checked at the start, version paths never change, `pins_sha256` names the set used; a later run refuses the open set (`set_open`) |
| A set closed on stale pin states (the index's last scan, no hashing) | a changed file closed into the set | A5 runs „Weryfikuj” before „Zamknij zestaw”; Hydrograf hashes every pin before step 1 |
| A project file edited outside Archiwista, or by the older Archiwista after a rollback | a closed set's pins no longer match its digest | `digest_state` `mismatch` on the card, `set_digest_mismatch` in Hydrograf |
| A pinned version removed from the store by hand | the run stops | `pin_missing` and „Przywróć brakujące” |
| `archiwista-project/1` changes | the reader fails | only that schema id is read (`unsupported` otherwise); a fixture copied from a real file in H1's tests |
| The project directory created again | the ACL is gone, `pin_unreadable` or an unreadable project file | ADR-067 names the grant; H2's commands again |
| The deploy breaks :8090 | the author's instance is down | rollback to `dd4268c`, database copies |
| The e2e hang returns | A1's gate blocked | A1's steps; the gate with `TMPDIR` on `/` |
| A plan window's job fails | nothing written into the set for that window | `job_partial`; „Ponów” on its job card, the set stays open until it is whole |
| Production touched by mistake | outage | K0 before and after every step; staging only through `scripts/staging-compose.sh`; the production checkout read only |

## Results

| Step | Repository and branch | Result |
|---|---|---|
| N1 | Nogat, `plan/archiwista-sets-hydrograf` | this plan; the author's decisions of 2026-11-02 and draft sets (A2) recorded; D6 and D12 open |
