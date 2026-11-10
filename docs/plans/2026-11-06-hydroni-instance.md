# Plan: a Hydrograf instance for the Hydroni area, PGW data in Kartograf, processing beyond one raster

Approved: 2026-11-06 (the author delegated the architecture: "masz wolną rękę"; the disk clean-up
was his choice: Docker build cache and unused images of the system daemon)

Requirements: HUB-5.2 (producers first), DEV-17.4, DEV-19.1 to DEV-19.14, ECO-054.

## Goal

Hydrograf's results (streams, sub-catchments, watershed delineation, design hydrographs) for the
whole area `/mnt/magazyn/agent-tmp/Hydroni/Obszar_h_07_dissolved.gpkg` (layer `Zlewnie`, one
multipolygon, EPSG:2180, 2,940.7 km², 70 × 78 km), served by a new Hydrograf instance that shares
nothing with the production one (`hydrograf-test.debever.pl`, compose project `hydrograf`) and is
published later on its own port. Along the way:

- Kartograf gains the download of the water management plan data of PGW Wody Polskie (its branch
  `feature/pgw`, PROGRESS item 27);
- Hydrograf's preprocessing stops holding the whole area in memory at once.

## Where it starts (2026-11-06)

| Fact | Consequence |
|---|---|
| Host: 4 CPUs, 15 GB RAM (about 9 GB free beside production Hydrograf, Archiwista, Hydrolog), local disk 23 GB free after the clean-up, NAS `/mnt/magazyn/agent-tmp` (CIFS, 211 GB free) | PostgreSQL stays on the local disk (no database on CIFS); rasters and the Kartograf store on the NAS; the Kartograf metadata cache (SQLite) on the local disk |
| Hydrograf processes NMT at 5 m (`backend/config.yaml:14`); the area is 117.6 M cells | one raster of the area at today's ~103 B/cell needs ~12 GB: over the host |
| A 183 M-cell bootstrap (Kaczawa) was OOM-killed twice; 59.5 M cells (1,488 km², the current part of h_07) works | the limit today is roughly half of this area |
| Memory plan F1–F7 (Hydrograf `docs/TECHNICAL_DEBT.md`) is designed and prototyped bit-identical (9.1 GB at 183 M cells, 287 s → 52 s on a cut), not implemented (`docs/BACKLOG.md:12`) | the first, low-risk step |
| The API reads whole rasters at query time (`core/raster_io.py:94-125`, `core/raster_service.py`) | ~0.9 GB per float64 layer for this area: windowed reads needed |
| `docker-compose.yml` hard-codes `container_name` (`hydro_db`, `hydro_api`, `hydro_nginx`) | a second stack clashes with production until the names follow the compose project |
| Kartograf `feature/pgw` holds only its opening commit (`1d3602d3`) | PGW is new work |
| PGW's spatial geodatabase: `Geobaza_2aPGW_ver_20230915.gdb.zip`, 142 MB, FileGDB, from `wody.isok.gov.pl/api/repo-mdd/publ/download/file/bccfebcf31ac47799fe1de6294b73c29/geobaza-2apgw-ver-20230915-gdb-zip` (200, no auth) | layers: `PGW_WP` (catchments of river, lake, transitional and coastal water bodies, `Pozostale_obszary_JCWP`, river water bodies, `Rzeki_glowne`, river-basin districts, water regions, RZGW, ecoregions), `JCWPd`, `SIG` (protected areas) and 34 tables |
| In the area: 16 river JCWP catchments (2,193 km², 16–465 km² each, 13 wholly inside), 34 direct catchments of lake JCWP (374 km²), 1 `Pozostale_obszary_JCWP` (31 km²) | units of 16–465 km² (0.6–18.6 M cells at 5 m) for the processing |

## Decisions

### D1. Kartograf: `hydro download --product pgw --country pl`

- The group `hydro` (today `network`, CZ) gains the product `pgw`: the PGW geodatabase of a plan
  cycle, edition `2apgw-20230915` (the version is the publication date of the file).
- `--whole-country` stores the archive as published (store segment `hydro/pl_pgw_gdb/country/`);
  an area (`--geometry`, `--bbox`) writes one GeoPackage in EPSG:2180 with the spatial layers of
  `PGW_WP` (and `JCWPd`, `SIG` on request via `--layers`) that intersect the area, unclipped
  features (a catchment is a whole unit), attribute tables left out; the archive is fetched once
  and reused as the parent version (`parent_request`, as the NMT mosaics do).
- Plain mode (`-o`) and store mode (`--root`), `--check`, sidecars with source „PGW Wody Polskie,
  KZGW, IIaPGW” and the licence/attribution text of the portal; errors from the registry
  (`source_unavailable`, `validation_error`). An ADR in Kartograf; plan item 27 closed.
- Not in scope: the plans in editable formats, the index, the set of measures, the water-body
  cards (`karty.apgw.gov.pl`).

### D2. Hydrograf: memory plan F1–F7 as designed

Implemented in the documented order (F7 → F1+F2 → F3 → F4+F6 → F5) with the equivalence tests
the plan lists; the known `fix_internal_sinks` 4-neighbour-cycle bug is fixed in the same branch
(it changes results; recorded in Hydrograf's CHANGELOG).

### D3. Hydrograf: processing by PGW units

- A new bootstrap input `--units FILE` (layers of the PGW GeoPackage of D1): the area is split
  into processing units = PGW catchments (river JCWP catchments; lake direct catchments and the
  remaining areas merged into the unit they drain into, by adjacency and the DEM), each processed
  as its own raster with a buffer of 500 m.
- Order: upstream before downstream. The unit graph comes from the DEM, not from the codes: a cell
  whose downstream cell lies in another unit is an outflow; its accumulated area and its stream
  segment are handed to the receiving unit as an inflow (added to the receiver's accumulation at
  that cell, and the receiver's segment that starts there gets the upstream segment as
  `upstream`/`downstream_segment_idx` link). A cycle between two units (PGW divide and DEM divide
  disagreeing at two places) merges the two units into one.
- Segment and catchment ids are global (unit offset); the tables, tiles and the API stay as they
  are, the delineation query already walks `downstream_segment_idx` in PostGIS.
- Peak memory is bounded by the largest unit (465 km² → 18.6 M cells), so the host's limit no
  longer depends on the area; units run one at a time (two when memory allows).
- A whole-area mosaic VRT of the per-unit rasters serves the API.

### D4. Hydrograf: runtime reads in windows

`read_raster` and the raster cache read a window around the query (the watershed's bounding box
plus a margin) from the VRT instead of whole files; the precise mode is bounded by the window of
the precomputed watershed of the point.

### D5. The instance `hydroni`

- Its own checkout: worktree `~/workspace/Hydrograf-hydroni` of Hydrograf's `develop` once D2–D4
  are merged, compose project `hydroni` (`docker compose -p hydroni`); `container_name` comes from
  the compose project (Hydrograf change: names `${COMPOSE_PROJECT_NAME}-db` and so on, production
  keeps its names through its `.env`).
- Database: a named volume of the project `hydroni` on the local disk; data, cache outputs and
  tiles on the NAS under `/mnt/magazyn/agent-tmp/Hydroni/hydrograf/`; the Kartograf metadata
  cache on the local disk.
- Port `127.0.0.1:8081` (free; production 8080, Hydrolog 8070, Archiwista 8090); own admin key and
  database password as secret files; publication (tunnel) is the author's later step.

### D6. Inputs through the ecosystem

- Kartograf's store of the team store „hydroni” (`/mnt/magazyn/agent-tmp/Hydroni/kartograf`,
  initialised with `kartograf store init`): NMT 5 m sheets of the area, BDOT10k of its counties,
  SoilGrids HSG, PGW (D1).
- An Archiwista project in `/mnt/magazyn/agent-tmp/Hydroni/projekty/h07` with a set pinning those
  versions; Hydrograf bootstraps with `--project … --set …` (ADR-067) and `HYDROGRAF_KARTOGRAF_ROOT`
  set, so the instance downloads nothing itself.
- PMAXTP grid at 2 km (about 1,400 points, one Obserwator request each).

### D7. Only the main watercourses of BDOT10k are burned into the DEM (the author, 2026-11-06)

- Ditch networks (`OT_SWRM_L`) form loops that falsify the flow directions when burned. For this
  instance the burning takes `OT_SWRS_L` with `PRZEBIEG = 'ciek główny'` (no side arms) that is a
  river (`RODZAJ = 'rzeka'`) or carries an MPHP identifier (`IDENTYFIKATORMPHP`), and `OT_SWKN_L`
  only with an MPHP identifier; no `OT_SWRM_L`. Water polygons (`OT_PTWP_A`) stay as today.
  Measured in county 3001: ditches 1,643 km, all SWRS 554 km, of which rivers 41 km and MPHP
  streams 188 features.
- A Hydrograf setting (`stream_burning` in `config.yaml`, default: today's three layers, so
  production's results do not change); the stream table `bdot_streams` (names at a point) and the
  lake-outflow classification keep every layer.

## Steps

| # | Project | Branch | Step | Depends on |
|---|---|---|---|---|
| 1 | Kartograf | `feature/pgw` | D1: plan and ADR in Kartograf, catalog, provider, store/plain writing, tests, docs | – |
| 2 | Hydrograf | `feature/memory-f1-f7` | D2 | – |
| 3 | Hydrograf | `feature/pgw-units` | D3 (reads the GeoPackage of step 1; fixtures from `kartograf.testing`) | 1, 2 |
| 4 | Hydrograf | `feature/windowed-reads` | D4 | 2 |
| 5 | Hydrograf | `feature/compose-instances` | D5, the compose names | – |
| 5a | Hydrograf | `feature/burn-main-streams` | D7, the `stream_burning` setting | – |
| 6 | host | – | D6 inputs: store init, downloads, Archiwista project and set | 1 |
| 7 | host | – | the instance: worktree, `.env`, secrets, `docker compose -p hydroni up`, bootstrap by units, verification | 3, 4, 5, 6 |

Steps 1 and 2 run in parallel (different repositories). Every branch: tests of the changed parts
during the work, the project's gate before its merge; merges into `develop` and pushes with the
author's approval (DEV-3.3).

## Risks

- PGW divides and DEM divides differ: flows cross unit boundaries away from the river; D3's
  inflow hand-off handles any crossing, cycles merge units.
- CIFS: SQLite and PostgreSQL never on it; rasters on it are slower to write (measured in step 7).
- Memory of production while the bootstrap runs: units one at a time, a cgroup limit on the
  bootstrap container.

## Results

Recorded 2026-11-08. Every merge below had the author's approval in the session.

- **Step 1, Kartograf (D1):** `feature/pgw` merged into `develop` (`2470acf9`, rebased onto the
  rewritten history; gate 8,641 tests, 95.3 %): ADR-059, the whole-country archive, the area
  GeoPackage, the `kartograf.testing` fixture, the size probes asking for identity encoding (the
  PGW server gzips its answers). Live run into the store `hydroni`: archive 142,048,450 B, area
  GeoPackage 25 layers, 363 features; 26 river catchments plus `LW10235` cover the area exactly.
- **Step 2, memory plan (D2):** F1–F7 and tiled GeoTIFFs merged, bit-identical on six synthetic
  cases. The memory work exposed a sink-fix bug: pits next to nodata were "fixed" towards a
  neighbour draining back, 2,335 two-cell cycles on the production raster, outlet accumulation
  understated by about 1,047 km² (fix `3b968d0`). Production still runs the old code; its
  reprocessing is postponed by the author.
- **Step 3, units (D3):** ADR-071. Units are groups of the 223 h07 catchments by the JCWP they
  lie in (27 units, 13.9–291.4 km²; every catchment lies 100 % in one JCWP). A fill per unit
  window never agreed on the seams at 5 m (closed basins, flats), so the depressions of the whole
  grid are filled once (161–172 s, 4.1–4.3 GB) and the units share it; accumulation, streams and
  sub-catchments run per unit with a cell-level hand-off. Full area: 233.2 M cells, 138.5 M with
  data, step 3 in 48 min, peak about 7.9 GB.
- **Step 4, windows (D4):** precise delineation reads windows (`MAX_WINDOW_CELLS` 40 M); the
  profile stays on point sampling.
- **Step 5, instance (D5):** `hydroni` on 127.0.0.1:8081, public at
  `https://hydrograf-hydroni.debever.pl`; DB volume on local disk, rasters on the NAS, `data/hydro`,
  cache and MVT tiles on local disk (SQLite cannot write on the share; 2.8 M tiles took 17.6 h on
  it and 34 min locally).
- **Step 5a, burning (D7):** `dem.stream_burning: main`. A user report (the Noteć flowing upstream)
  led to ADR-072: the smoothing of burned lines follows the digitized direction of BDOT10k
  (reversed only where the DEM rises > 2 m over ≥ 200 m), strictly descending, gaps ≤ 50 m
  bridged; no inflow from outside the area (the author). Noteć after the run: 581 of 583 D8
  samples downstream (was 7 of 569).
- **Step 6, inputs (D6):** Archiwista project `h07`; set `2026` lacked the sheet
  N-33-120-D-a-3-3 inside the area (an enclosed nodata hole draining 40 km²), so set `2026-2`
  (727 pins) adds it; the union of the sheets now covers the area completely. Water bodies are
  never endorheic (`--waterbody-mode none`, the author): the `auto` classification marked 81 % of
  the lakes endorheic.
- **Step 7, verification:** delineation, land cover, HSG, PMAXTP hydrographs, depressions,
  overlays and tiles answer through the public host. The deliverable for the author is
  `/mnt/magazyn/agent-tmp/Hydroni/h07_parametry_zlewni.gpkg`: the 223 catchments with the panel's
  basic parameters (without catchment length and width), Gravelius and Miller indices, land cover
  per class and control columns (`scripts/export_catchment_parameters.py`).
- **After the plan (2026-11-08, the author's requests):** land cover from the attributes of
  BDOT10k with industrial land (Hydrograf ADR-074: PTZB kinds, grassland split from arable land,
  KUPG plants cut out of the PT partition) and CN from the land cover × hydrologic soil group
  complexes of the TR-55 table in Hydrolog (ADR-075); a lake with any outflowing watercourse is
  exorheic. Hydroni runs `develop` `8156dee`; the land cover was imported again (which also
  removed duplicated rows). The GeoPackage (v3) carries CN for AMC I, II and III (mean 50.2,
  69.5, 84.1) and the HSG shares (A 5.3 %, B 94.7 %); v1 and v2 are kept with date suffixes.
  The area sheet list missed a sheet because of the complex geometry of the area (the author);
  the HSG is usable (groups by area, not polygon count).
- **2026-11-10:** Hydroni bootstrapped again from the closed set `2026-3` (728 pins: `2026-2`
  plus the sheet N-33-118-B-a-4-2 that Hydrograf's ADR-076 coverage check asked for), run 3 on
  `545f109`, 00:54–03:15 CET: 710 sheets, 201,195 segments at 0.01 / 0.1 / 1 / 10 km², 92.01 km²
  of wetlands as group D, 73 burned lines reversed by ADR-077; export v4 of the 223 catchments
  with the runoff control columns. Hydroni then ran `894810c` and now runs `fd0b533`, Hydrograf's
  `develop` with release set candidate-2. Production switched to `894810c` at 05:00 CET,
  reprocessed by Hydrograf's runbook `docs/runbooks/2026-11-10-reprocessing.md` (backup
  `/data/nmt/hydrograf-backup-2026-11-10/`, image `hydrograf-api:pre-2026-11-10`); it keeps the
  candidate-1-era producer pins until its next rebuild.
- **Closed of the 2026-11-08 Open list:** production reprocessed (above); wetlands and the KU
  lawns in the land cover (Hydrograf ADR-078: soil under wetlands is group D, KUSK/KUKO lawns
  open space); the area text per instance (`frontend/data/instance.json`); the runoff-weighted
  check (control columns of the export, ADR-075 amendment); Kartograf's cell-size refusal
  (ADR-060) and HSG of the least permeable layer of 0–100 cm (ADR-061); Hydrolog's TR-55 rows
  and CN 98 for water (in candidate-2); enclosed nodata filled on request
  (`dem.fill_enclosed_nodata`, default `false`, ADR-073), not needed on Hydroni since `2026-3`.
- **Open:** using the 0–100 cm HSG in Hydrograf's bootstrap (the author's call, step 5 again on
  each instance); catchment 1883617 and the 11 catchments with a polygon/NMT area ratio above
  1.2 for the author's review; the report to GUGiK on the 1 m sheets (the author's step).
