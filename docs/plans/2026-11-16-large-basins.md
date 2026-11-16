# Plan: large basins in one Hydrograf instance

Approved: pending

Status: a draft of 2026-11-16 from the scenario test of 2026-11-15/16, revised the same day with the author's second, third and fourth rounds of decisions; not approved, so no code starts (DEV-17.4). The decisions are the author's (four rounds of 2026-11-16, the second with the coordinator's answer to the old question 9, the fourth after finding E7-GAP-03); the design marks its own proposals „[proposed]”.

Requirements: HUB-5.2, DEV-17.4, DEV-17.5 and DEV-3.4 (each project in its own session and branch), DEV-17.2 (Hydrograf records its decisions as ADRs), DEV-3.3 (merges with the author's approval), DEV-17.6 and ECO-073 (bootstraps run as user systemd units), ECO-054 (the project and its set are Archiwista's), ECO-072 (a released format changes only with the author's consent).

## Goal

One Hydrograf instance serves whole large basins, one or several: the Barycz (5,543.2 km²) and the Bóbr (5,881.8 km², 232.4 km² of it in Czechia) together, later the Odra. The data are continuous: one address, one database, delineation and parameters across each whole basin. A basin is composed of many runs, its parts, each within a fixed cell budget under the 8 GB cap of a bootstrap: the method composes many analyses into one whole instead of fitting an area into one run. It does not depend on the resolution: a basin has one grid, and as the DEM gets finer (the author plans to work at 1 m), the budget in cells stays and the parts get smaller. The analysis is a single-flow-direction D8 tree. The priority is the work done with adequate quality, not the fewest runs.

## Facts

Source: the scenario test of 2026-11-15/16 on the Barycz and the Bóbr, report `~/workspace/_e2e/2026-11-15/scenario/REPORT.md` (in Polish, cited as `REPORT.md:<line>`) and the coordinator's findings `COORD-FINDINGS.md` beside it. Hydrograf's code at `develop` `939b55f` (the member of candidate-5; code paths under `backend/`).

### The scenario test

- **No second part in one instance** (E7-08, `REPORT.md:148`, `COORD-FINDINGS.md:8`): a second bootstrap into an instance replaces the first part, mixes land cover and soils, and gets no inflow from the part above. The workaround was one instance and one address per part: 7 instances for two basins, 7 databases of 9,509 MiB together (`REPORT.md:96`, `:254`).
- **Truncated catchments look complete** (G07-2 = G09-2/3, `REPORT.md:150`): a catchment cut by the edge of a part or by the Czech border is shown without a warning, e.g. Błażkowa with 13.46 km² against the 103.54 km² of IMGW-PIB's catalog.
- **A part with several outlets** (E7-GAP-03, `REPORT.md:152`; evidence `/data/nmt/e2e-2026-11-15/e7/boleslawiec.gpkg` and the GUI report `~/workspace/_e2e/2026-11-15/scenario/E6/reports/g10-bobr-boleslawiec.md`): GeoRecon grouped the JCWP into parts by their MPHP code group (`/data/nmt/e2e-2026-11-15/geo/build_geo.py:26-29`, `:50`; groups 161–163 → the Bóbr's part 1). PGW's river lines of the reach (layer `jcwp_rivers` of the evidence) end where each JCWP drains. The upper Bóbr (`RW600003163759`) and the Żeliszowski Potok (`RW60000616376`) end at 258368, 375472, where `RW60001116599` begins (the Bóbr from the Żeliszowski Potok to the Kwisa, part 2b). The Młynówka (`RW600006163794`) enters it at 259564, 383811 (Bóbr km 13.9), and the Bobrzyca (`RW60000616389`, with `RW600003163859` above it) at 260945, 390197 (km 21.8). Part 1 thus drained into part 2b at three points, 187.9 km² of it (11 %) below the cut. Its mosaic, the sheets that touch its outline, held the Bóbr only in pieces: in its instance the Bóbr stops 1.15 km below the Żeliszowski Potok and is missing at every threshold up to km 12.2, and a delineation at the Dąbrowa Bolesławiecka gauge returns the Bobrzyca's 178.17 km² (IMGW-PIB: 1,711.8 km²).
- **Memory** (E7-09, `REPORT.md:87-97`, `:117-127`, `:162`): Barycz 1 (2,393.3 km²) ran under an 8 GB cap on a window of 188.6 M grid cells (11,663 × 16,173), 111.0 M of them with data; step 3 took 2,467.8 s and the bootstrap 5,631.4 s (21:53–23:27), with logged peaks of 8,003 MB (polygonize_subcatchments), 8,064 MB (secondary_rasters, 98.4 % of the cap) and 8,045 MB (publish) (log `/data/nmt/e2e-2026-11-15/logs/hydrograf-barycz-bootstrap-run-20261115-215308.log:154-155`, `:203`, `:212`). The six other parts ran under 9 GB on windows of 108.9–196.7 M grid cells and peaked at 7,618–9,065 MB, about 98 % of the cap whatever their size (Bóbr 2a, 108.9 M grid cells, 8,147 MB), so the logged peak is bounded by the cap, not by the need [INFERENCE of the report]; `docker stats` sampled 6,830–7,495 MiB. Bóbr 2 PL (296.7 M grid cells), estimated at 10–12 GB [INFERENCE of the report], was split along JCWP into 2a (108.9 M) and 2b (135.0 M) before it ran.
- **Time** (`REPORT.md:37`, `:96`, `:101-102`, `:134`): the 7 bootstraps took 24,024.5 s (6 h 40 min), 1.84–2.36 s/km²; the longest steps are step 3, the NMT (685–2,468 s), and step 8, the MVT tiles (756–2,093 s). The chain of five parts ran 00:10:52–05:08:06, one at a time behind a gate of 9,500 MB free memory.
- **Whole basins on the 5 m grid**, computed for the first draft from the scenario's sheet lists (`/data/nmt/e2e-2026-11-15/geo/sheets/`, frames by Kartograf's `SheetParser.get_bbox`; Barycz 1's frames give the logged 188.6 M): the Barycz has 1,213 sheets, 24,578 × 15,288 = 375.7 M cells, of which 221.7 M valid; the Bóbr's Polish part 1,297 sheets, 17,643 × 32,123 = 566.7 M cells, of which 226.0 M valid. The scenario's windows held 42–61 % data (`REPORT.md:89-95`).
- **The two basins together** (`/data/nmt/e2e-2026-11-15/geo/zlewnie_barycz_bobr.gpkg`, EPSG:2180): the boxes of the outlines lie 1.8 km apart (x 220.5–306.4 km for the Bóbr, 308.2–430.1 km for the Barycz) and together span 209.6 × 160.1 km, 1,341.7 M cells at 5 m (33.5 G at 1 m), of which the basins cover 34 %. The sheet boxes of Bóbr 1 (x ≤ 308,278) and Barycz 3 (x ≥ 307,812) overlap in a strip of 466 m × 8.2 km (the „Mosaic extent for BDOT10k” lines of `logs/hydrograf-bobr-bootstrap-run-20261115-232835.log` and `logs/hydrograf-barycz-3-bootstrap-run-czesc-3-20261116-030033.log`).
- **The JCWP of the two basins** (layer `jednostki_jcwp` of the same file): the Barycz 48 river JCWP of 10.8–683.2 km²; the Bóbr 70 of 0.34–474.7 km² and 5 `pozostale_obszary_jcwp` of 11.1–15.2 km², the reservoirs Pilchowice, Bukówka, Sosnówka, Złotniki and Leśna. Below 10 km² lie only Stary Bóbr (`RW60000316373969`, 0.34 km²; by its name an old arm of the Bóbr [INFERENCE]) and Czerwonka do zb. Sosnówka (4.26 km²).
- **Side channels in BDOT10k** (the scenario's `hydrograf-<part>/data/hydro/hydro_merged.gpkg`): OT_SWRS_L marks a course as `PRZEBIEG = 'ciek główny'` or `'ramię boczne'` (a side arm). Barycz 3 has 126 side arms among 11,110 OT_SWRS_L lines, 85 of them with an MPHP identifier, and 537 of its 603 canals (OT_SWKN_L) carry an MPHP identifier; Bóbr 3 has 200 side arms and 322 of 362 canals with one.
- **One area per Archiwista project** (E7-01, `REPORT.md:151`): `AreaChoice` holds one area (`src/archiwista/api/models.py:3177`, `800231c`), and changing it under a closed set returns 200; the workaround was 8 projects, one per part.
- **Czechia** (GEO-01, GEO-06, `REPORT.md:149`, `:204`): Hydrograf reads no CZ DEM, so the Bóbr's 232.4 km² in Czechia are outside the model. Kartograf has CZ watercourse lines as HY-NET (`hydro download --product network --country cz`, `src/kartograf/catalog/commands/hydro.py:1` at `e14bc78`), which Hydrograf does not read, and no CZ catchment polygons (DIBAVOD A07 was used outside it).
- **Network window** (E5b-10, `REPORT.md:191`): a network closing at Łąki is refused, `network_window_too_large`, 135,118,485 cells over 60 M (`/data/nmt/e2e-2026-11-15/e5b/network/laki-window.json`).

### Hydrograf at `939b55f`

- **One run per instance.** The unique index `idx_processing_runs_one_active` allows one active run (`migrations/versions/005_processing_runs.py:70-71`); `publish_run` (`core/unit_run_store.py:516`) deletes every DEM-derived `stream_network` row and every `stream_catchments` row (`:600`, `:603`).
- **ADR-071 and its amendment** (`docs/decisions/0071-pgw-units-and-boundary-event-routing.md`): PGW units own the outputs (tiles, records, resume), not the computation. Fills per unit window never agreed on the seams at 5 m (closed basins wider than any halo, flats broken differently by each window; the halo grew from 500 m to 16 km, `:65`), so the fill and D8 run once on the whole grid at about 18 B per cell, and „a larger area needs the fill itself to change, not windows” (`:71`). Burning, smoothing, buildings and lakes run on the whole DEM too: a window changed 37 cells by up to 5.2 m where a stream enters it (`:52`).
- **The run's grid in one array.** `fill_whole_grid` (`core/unit_hydrology.py:182`) reads the run's whole DEM (`:211`, through `core/raster_io.py:199`, `src.read(1)`), the box of the set's sheet frames (`utils/kartograf_set.py:298`; the mosaic at `scripts/bootstrap.py:579-583`); the fill and the routing scratch are removed after the run, and the run keeps per-owner tiles of `02_filled`, `03_flowdir`, `04_flowacc`, `06_streams` and the other rasters (`scripts/process_dem_units.py:14-24`, `:794-803`), and a report with the peak memory of each stage (`:17-18`).
- **Units.** A PGW polygon owns the cells whose centre it holds, and a cell outside every polygon goes to the nearest owner (`core/unit_ownership.py:284`); the layers are `zlewnie_jcwp_rzecznych` and `pozostale_obszary_jcwp` (`:34-35`), from a `--units` file beside the set (`scripts/bootstrap.py:1696-1705`).
- **Rasters.** Per-owner tiles and one VRT per raster on the run's grid, every valid cell in exactly one tile, verified before anything is replaced (`core/unit_rasters.py:24-26`, `_write_vrt` at `:386`, `write_unit_mosaics` at `:550`); the API reads the VRTs of the run that `active_run.json` names (`core/active_run.py:121-140`, `core/config.py:240-252`).
- **Graph.** In memory, keyed by `(threshold_m2, segment_idx)` (`core/catchment_graph.py:156-157`, `:282`) and loaded from the whole `stream_catchments` (`:225-233`); its docstring sizes it at ~87k nodes (`:114`), Barycz 1 had 163,750 and the 7 parts 806,916 (`REPORT.md:96`). It loads lazily in the first request, about 6 min beside a bootstrap (E5b-01, `REPORT.md:165`).
- **Limits.** Stream thresholds of 0.01, 0.1, 1 and 10 km² (`core/constants.py:26`); precise-mode windows up to 40 M cells (`core/raster_service.py:42`), network windows up to 60 M (`core/network_delineation.py:115`), hydrographs up to 250 km² (SCS-CN, `core/constants.py:19`).
- **Burning.** `dem.stream_burning: main` (default `all`, `core/config.py:353`) burns the OT_SWRS_L main courses (`PRZEBIEG = 'ciek główny'`, never a side arm) that are rivers or carry `IDENTYFIKATORMPHP`, every OT_SWKN_L that carries it, whatever it connects, and no OT_SWRM_L (`core/hydrology.py:378-386`). The ends of the burned lines are joined into nodes within one cell (`_line_nodes`, `:672`), and each line is oriented by the rules of ADR-077 (`_line_directions`, `:1014`): rule 1 orients an MPHP watercourse towards the node where it meets its receiver, a line whose identifier is a proper prefix of its own (`_mouth_directions`, `:802`); rule 2 orients the lines of one MPHP identifier, else of one name, down the DEM (`_watercourse_directions`, `:954`, the keys at `:985-988`).
- **PGW units carry no receiver.** Hydrograf reads PGW's catchment polygons by `MS_KOD` (`_read_pgw_polygons`, `core/unit_ownership.py:152`) and no other PGW layer. Nothing in the GeoPackage says which JCWP a JCWP drains into: in the scenario's file (`/data/nmt/e2e-2026-11-15/geo/raw/pgw/`) the catchments carry `MS_KOD`, `AREA` and `UWAGI`, and the 548 river lines of `jednolite_czesci_wod_powierzchniowych_rzecznych` carry `MS_KOD`, `Nazwa_JCWP` and `DLUG`.
- **Line topology.** Besides `_line_nodes`, the pipeline orders lines by Kahn's algorithm over their nodes (`_flow_order`, `core/hydrology.py:1072`), and ADR-077's rule 1 reads only the nodes, the MPHP identifiers and the lengths, no DEM (`_mouth_directions`, `:802`). The diagnostic `scripts/check_stream_directions.py`, outside the pipeline, reads the line layers that reach into an area (`read_lines`, `:160`), splits a line where another line's end lies on its middle (`split_at_t_junctions`, `:239`), joins ends within 0.5 m (`join_ends`, `:300`), names a node where two or more lines begin a bifurcation, `rozwidlenie` (`node_kinds`, `:341-385`, `:379`), marks a line from a bifurcation to a dead end (`:1099`) and joins the lines of each watercourse end to end (`trace_watercourses`, `:683`).
- **Accumulation.** `flw.upstream_area(unit="cell")` (`core/hydrology.py:2243`); pyflwdir's `accuflux(data)` accumulates from initial values.
- **Resolution.** A set's NMT comes at `1m` or `5m` (`utils/kartograf_set.py:72`), from `nmt/pl_1992_<resolution>_evrf2007` only (`:77`); one `--resolution` per run (`scripts/bootstrap.py:1806-1811`). ADR-087 (`docs/decisions/0087-a-sheet-missing-at-the-run-resolution-from-a-finer-nmt-of-the-set.md:18-20`) builds a missing 5 m sheet from 1 m data with `align_to_cellsize` (`utils/raster_utils.py:195`, called at `scripts/bootstrap.py:575-577`): `gdalwarp -r average` at the run's cell size over the sheet's frame grown outward to whole cells of the lattice, nodata −9999 left out of the mean (`utils/raster_utils.py:263-287`). The lattice is the corner offset that the run's sheets of its cell size share, (0, 0) when the run has none (`:234-244`), and a sheet coarser than the run is refused (`:252-256`). The 1 m cells nest in the 5 m lattice: M-33-19-B-c-2-2 has its 1 m `xllcenter` at 246,673.00 and its 5 m copy its `xllcorner` at 246,672.5, so a 5 m cell is the mean of the valid 1 m cells within it, 25 when all are valid. Thresholds are areas in m², turned into cells by the run's cell size (`core/unit_hydrology.py:599`, `core/cell_parameters.py:132`), and the readers take the cell size from the raster (`core/cell_parameters.py:125-127`, `core/raster_service.py:128`).
- **Network method** (ADR-080, `docs/decisions/0080-network-delineation-at-control-points.md:136-143`, `:164-166`): control points, reaches, the przyrzecze as an element that enters the junction below it unrouted, and `hydrolog-network/1` to Hydrolog.
- Decision D3 of [the Hydroni plan](2026-11-06-hydroni-instance.md) processed units in windows with an upstream-first hand-off; ADR-071's amendment replaced that with the whole-grid fill. This plan returns to fills per window, for parts much larger than units, and accepts a measured seam instead of an exact one.

## Several basins in one instance

The author asked whether one instance can hold two distant basins, e.g. the Barycz and the Bóbr, each from its own Archiwista project and set and each in its parts. Read in Hydrograf's code at `939b55f`:

| Subsystem | At `939b55f` | With two basins | Verdict |
|---|---|---|---|
| Sources | `--project` is one choice of the exclusive, required area group (`scripts/bootstrap.py:1627`, `:1645`) with one `--set` (`:1655`); `set_inputs` reads one project and one set (`utils/kartograf_set.py:186`); a project has one area (`utils/archiwista_project.py:95-99`, `:122`) | the reader serves one basin per call as it is; the bootstrap takes a basin (its project and set) and a part, and the instance keeps a registry of its basins | works with listed changes |
| Fill and D8 | the run's whole grid in one array (`core/unit_hydrology.py:211`, `core/raster_io.py:199`), on the box of the set's sheets (`utils/kartograf_set.py:298`) | one run over both basins would allocate 1,341.7 M cells at 5 m; a run is one part's window, never the instance's box | works with the parts |
| Paths and pointers | the mosaic `data/nmt/dem_mosaic.vrt` (`scripts/bootstrap.py:581`); one `active_run.json` (`core/active_run.py:121-140`); the API's DEM from the active run, else the fixed mosaic (`core/config.py:240-252`) | a directory and a pointer per part; one VRT per raster over the active runs of every part of every basin (XML, no allocation) | works with listed changes |
| Runs | one active run per instance (`migrations/versions/005_processing_runs.py:70-71`) | one per part | works with listed changes |
| DEM-derived tables | `publish_run` deletes every DEM-derived `stream_network` row and all `stream_catchments` (`core/unit_run_store.py:600`, `:603`) | replaced by part | works with listed changes |
| Other tables | whole tables: `bdot_streams` (`core/db_bulk.py:485`), depressions with `--clear-existing` (`scripts/generate_depressions.py:839`), the sewer (`core/sewer_service.py:376-377`), `clean` (`scripts/clean.py:328`); soil: every polygon touching the sheet box (`scripts/bootstrap.py:803-804`, `:886-887`); land cover: where an old polygon's point lies in the new import (`scripts/import_landcover.py:728-736`, the whole table with `--clear-existing`, `:792`); precipitation: upserted by point (`scripts/preprocess_precipitation.py:299`) | by part, clipped to the part's JCWP outline. Boxes are not safe even here: Bóbr 1's soil import deletes Barycz 3's polygons that touch their 466 m strip | works with listed changes; precipitation works today |
| Graph | all of `stream_catchments` (`core/catchment_graph.py:225-233`), keyed `(threshold, segment_idx)` (`:282`); a node without a downstream node is an outlet (`:641`); a repeated `segment_idx` is an error (`:428-432`); tables indexed by label are sized by the largest label (`core/network_delineation.py:899`) | several components are several outlets, as every area's edge already has [INFERENCE]; two runs both numbering from 1 collide, so `segment_idx` must be unique per threshold in the instance and stay dense | works with listed changes |
| Precise mode, network window | windows grown around the click (`core/raster_service.py:42`) or the closing section's catchment (`core/network_delineation.py:705-750`) on one VRT | the instance's box costs nothing; a window across a seam reads both parts' tiles | works today on one VRT |
| MVT tiles | every threshold of the whole tables exported (`scripts/generate_tiles.py:77-98`) and tiled by tippecanoe (`:121`) at every bootstrap; the API's stream and catchment tiles are queried by the tile's box (`api/endpoints/tiles.py:48`, `:109`) | a part's own export, then `tile-join`; the queried tiles work today | works with listed changes |
| DEM tiles, overlays | `dem.png`, the DEM tile pyramid (zoom 8–16) and `streams.png` from the whole mosaic (`scripts/bootstrap.py:1092-1160`), the pyramid deleted and rebuilt whole (`:1132`); memory stays bounded (strips, `scripts/generate_dem_tiles.py:1-11`; reduced blocks, `scripts/generate_dem_overlay.py:63-78`), time and disk follow the box | only the tiles of a re-run part, cut from the instance's VRT so the tiles at a seam hold both parts; one colour range per instance | works with listed changes |
| `instance.json` | one `area` (name, km², boundary file), one `nmt.resolution_m`, one `set` (`scripts/write_instance_info.py:311-335`); one `--area-name` (`scripts/bootstrap.py:1675-1679`); one list of sources (`core/data_sources.py:141`) | `basins`, each with its project, set, area, sources and parts; `area` names the instance and `nmt.resolution_m` its one cell size | works with listed changes |
| Frontend | one area label (`frontend/js/instance.js:33-38`) in the welcome text (`frontend/js/welcome.js:47-52`); the map fits the bounds of the DEM tiles (`frontend/js/map.js:262-276`) | the label names the basins; the map fits their union, with a list that zooms to a basin | works with listed changes |
| Admin panel | a bootstrap from one box, sheet list or boundary file, never a project and set (`api/endpoints/admin.py:718-745`, `:796-808`), one at a time (`:794`); one boundary on its page (`frontend/admin/boundaries.js:4-5`) | basins, parts, runs and seam reports listed; a part's run from its basin's project and set, one at a time | works with listed changes |
| Cell size | one `--resolution` per run (`scripts/bootstrap.py:1806-1811`), the lattice from the run's own sheets (`utils/raster_utils.py:234-244`); the readers take the cell size from the raster (`core/cell_parameters.py:125-127`) | one grid for every part of every basin of the instance, fixed in the basin registry (Grid and cell size) | works with listed changes |

**Verdict: works with listed changes, no redesign.** Today the second basin replaces the first (E7-08). Once each run is one part's window, no step allocates the instance's box: the fill holds one window, the API's windows grow from a point, and the overlays work in bounded memory. Most changes are ones the parts need anyway: replacement by part, a run and its rasters per part, instance-wide segment numbers, one grid passed to every run. Four belong to the basins themselves: a source per basin, the basin registry, `instance.json` with its basins, and the GUI and admin panel for several basins (D8).

## Options

| Option | Continuity | Memory | Detail | Decision |
|---|---|---|---|---|
| A. Closed JCWP parts joined at BDOT10k inlets, in one instance for one or several basins | whole basin, through the inlets; the seam measured, not exact | bounded by the budget of a part's window | one cell size per basin, any | chosen |
| B. The whole basin in one run at 10 m | whole basin, exact | the Barycz 93.9 M grid cells at 10 m [INFERENCE: fits 8 GB] | 10 m | rejected by the author: the goal is a method that composes many analyses into one whole, not one area fitted into one run; the resolution will rise (1 m), where no basin fits one run; the priority is the work with adequate quality, not the fewest runs |
| C. A bigger machine, the whole basin at 5 m in one run | whole basin, exact | the Barycz's 375.7 M cells need about 6.8 GB for the fill alone (18 B per cell) and about twice Barycz 1's cap for the later stages [INFERENCE]; the Odra and 1 m out of reach | 5 m | rejected |
| D. Exact tiled algorithms (parallel priority-flood, TauDEM with MPI) | whole basin, exact | bounded by the tile | any | rejected: a second fill whose flats must agree with pyflwdir's, what failed in ADR-071 (`:65`), and a rewrite of the pipeline |
| E. A coarse 25 m pre-pass for the divides of the parts | whole basin | small pre-pass | 5 m | rejected by the author: the JCWP divides are the reference |
| F. One instance per part (today's workaround) | none: truncated catchments without a warning | per part | 5 m | rejected: 7 addresses and 7 databases for two basins (E7-08) |

## Decisions (the author, 2026-11-16)

| # | Decision | Round |
|---|---|---|
| D1 | Parts are aggregates of whole JCWP from Kartograf's PGW GeoPackage, cut along their boundaries, without a coarse pre-pass: the JCWP divides are the reference. Each part is processed with a ~1 km buffer; a cell belongs to the part its D8 flow reaches within the buffered window, and a seam report measures the area that drains across a JCWP boundary outside the inlets. | 1 |
| D2 | Budget and memory: the bootstrap's cap stays 8 GB, and the budget is 90 M grid cells of the part's window, final. It counts every cell of the window, nodata included, since the arrays are allocated on the window. A part that does not fit becomes smaller parts. The budget does not depend on the cell size, so the parts shrink as the resolution grows (at 1 m a 90 M-cell window covers 90 km²). | 2, 3 |
| D3 | One grid per basin; different cell sizes within one basin are never allowed. DEM inputs of any resolution are accepted and resampled to the coarsest of them on the basin's grid, snapped to its origin and cell size (a warp). The basin's cell size is the coarsest among its inputs, and every part uses that grid. The design stays resolution-agnostic: the cell size is fixed per basin, and the budget counts cells. | 3 |
| D4 | Inlets come from BDOT10k lines: the intersection of the burned main river of the upstream part's outlet JCWP (chosen by its MPHP identifier and oriented by ADR-077 and the MPHP order, never by its vertices) with the JCWP boundary. At a reservoir or lake on the cut the inlet is the lake's outflow (better: no cut at a reservoir); cuts lie at least 200–500 m from tributary confluences; unburned ditches and canals enter only the seam report; a line running along the boundary gives its last exit along the flow. DEM check: the upstream part's owned cell of the highest accumulation lies within N cells (e.g. 10) of the inlet, else a warning. | 1, 3 |
| D5 | Order: a part's only inlets are main rivers, above every stream threshold, so a secondary inlet cannot exist (Inlets); the re-run of the stream extraction at a threshold and the forced-channel fallback are dropped. A part's geometry needs no other part; only the attributes below an inlet need the record of the part above, and only they keep the topological order, upstream first. A watercourse that still crosses a part boundary outside an inlet gets a warning only. | 2, 3 |
| D6 | The przyrzecze of the downstream part, the direct area along the main river from the inlet down, comes from that part's own run; nothing is filled in later. In the network (ADR-080) the upstream part is an inflow node at the start of the reach and the przyrzecze its lateral element. | 1 |
| D7 | One database: `part_id` on runs, on the DEM-derived tables, land cover and soil; `publish_run` replaces only its part; one active run per part; graph edges across parts (the upstream part's outlet segment to the downstream inlet segment); delineation crosses parts and uses whole-part aggregates (dissolved outline, parameters) for an upstream part it holds whole; one VRT over all parts; the tiles merged (`tile-join`); one `instance.json` listing the parts. | 1 |
| D8 | Several basins in one instance: independent basins, each with its parts, share the database, the graph (one connected component or more per basin), the VRTs, the tiles and `instance.json`; Hydrograf accepts several project and set sources, each a basin. | 2 |
| D9 | Archiwista is unchanged at this stage: one project with the whole basin as its area and one closed set per basin, possible today; Hydrograf partitions the set. | 2 |
| D10 | The seam report's thresholds only warn; nothing blocks a publish. | 2 |
| D11 | Czechia: this stage is Hydrograf only, and T1 accepts the errors in the upper Bóbr. Continuity across the border is a later, separate plan (Follow-ups): Kartograf gets ZABAGED, the Czech counterpart of BDOT10k, and whatever else the analyses need (DMR 5G is already in Kartograf), then Hydrograf reads them. | 2 |
| D12 | Gauges are only a possible extension (Appendix): Hydrograf must eventually be free of IMGW-PIB's data ([the IMGW-PIB plan](2026-11-14-independence-from-imgw.md)) but must allow using such data. No step of this plan uses gauges, and the acceptance does not depend on them. | 2 |
| D13 | Branches and release: the work does not touch the planned release (candidate-5); code starts after `Approved:`, on Hydrograf's `feature/large-basins`, and merges into `develop` only after the first joint release, as an update. | 2 |
| D14 | T1 uses the scenario's harness, with GPT for the GUI tasks, Claude continuing where GPT hits its limit. | 2 |
| D15 | Side channels are cut out of the analysis: every BDOT10k line that leaves the main river, or any other burned river, instead of flowing into it (bifurcations, mill races, distributary and irrigation canals) is not burned, is no inlet and makes no flow path. Water is not routed or split at the GIS stage: the analysis is a single-flow-direction D8 tree, and cells that would drain through a side channel follow the DEM. Splitting flow is for later models (Hydrolog, Hydraulik), outside this plan. | 3 |
| D16 | Topology first: the topology of the hydrographic network is analysed before the JCWP are grouped into parts. The network is the burned BDOT10k and MPHP lines with the JCWP outflow relations, directed by ADR-077, side channels already cut (D15); the analysis builds the JCWP graph, each JCWP's outlet point and the JCWP it drains into. A part is a connected upstream subtree of that graph. Before any download or bootstrap a check requires each part to have exactly one outlet, one edge to a JCWP outside the part or the basin's outlet, on the part's main river, and every inlet of a part to be the outlet of exactly one part above. A failure is an error that stops the basin and lists the offending JCWP with their receiving JCWP, not a seam-report warning. | 4 |

Later, outside this plan's steps: the Odra's scale, with thresholds per part and the graph loaded by part.

## Design

### Side channels (D15)

1. Detection is a step of the network topology (below), once per basin, on its split, joined and directed lines, before any part runs. A line is a side channel when:
   - BDOT10k marks it a side arm, `PRZEBIEG = 'ramię boczne'`, which `main` already leaves out (`core/hydrology.py:380-384`);
   - it begins at a bifurcation, a node where two or more burned lines begin (the diagnostic's `rozwidlenie`, `scripts/check_stream_directions.py:379`), and does not continue the river: the line that continues it belongs to the watercourse of the line that ends there, by its MPHP identifier, else its name, as ADR-077's rule 2 groups lines (`core/hydrology.py:985-988`);
   - or its watercourse reaches burned rivers at both ends, a loop off a river, for which ADR-077's rule 1 finds two mouths and turns the halves towards both (`_mouth_directions`, `core/hydrology.py:802`).
2. Every line that continues a side channel downstream, to where it ends or rejoins a river, is cut with it. A bifurcation that neither rule decides keeps its lines and gets a warning.
3. A side channel is not burned, is no inlet and makes no flow path; the seam report lists one that crosses a part boundary, as it lists ditches. The cells that would drain through it follow the DEM: the D8 of the filled DEM gives each cell one direction, wherever the terrain leads, through a channel cut into the DEM too. No water is routed or split at the GIS stage.
4. The topology's GeoPackage lists each side channel with the rule that cut it.

### Network topology (D16)

Once per basin, before the JCWP are grouped and before any download or bootstrap. It reads vectors only, the basin's PGW GeoPackage and the BDOT10k hydro layers of its counties, and no NMT sheet.

1. The network: the burned BDOT10k lines (`main`, `core/hydrology.py:378-386`) that reach into the basin, split at T-junctions and joined at their ends into nodes.
2. Direction without the DEM: ADR-077's rule 1 orients every MPHP watercourse towards its receiver; any other line keeps its digitized direction, BDOT10k's downstream (ADR-077's last rule). The JCWP's main rivers are MPHP watercourses [INFERENCE: BDOT10k carries their identifiers], so rule 1 orients them the same way when the preparation along lines later applies every rule, with the DEM, to burn them.
3. The side channels are cut (D15).
4. Outlets: a JCWP's main river is the burned watercourse that its PGW river line follows (`jednolite_czesci_wod_powierzchniowych_rzecznych`, by `MS_KOD`), and its outlet is that river's last exit from the JCWP's polygon along the flow. A reservoir of `pozostale_obszary_jcwp`, without a river line, has its lake's outflow as its outlet (D4).
5. Receivers: the JCWP whose polygon the network enters at the outlet; none for the JCWP whose outlet leaves the basin. Every other JCWP has exactly one receiver, and the graph has no cycle; a JCWP with no receiver or two stops the basin as a failed partition check does, listed with what was found.
6. Output: a GeoPackage per basin with the directed lines, the side channels, every JCWP's outlet point and the graph's edges; the grouping, the inlet table and the admin panel read it.
7. In Hydrograf (H2): a module `core/basin_topology.py` and a command `python -m scripts.partition_basin` [proposed names]. They take over the diagnostic's line topology (`read_lines`, `split_at_t_junctions`, `join_ends`, `node_kinds`, `trace_watercourses`; `scripts/check_stream_directions.py:160`, `:239`, `:300`, `:341`, `:683`), which the diagnostic then imports, and reuse the pipeline's `_select_burned_features` (`core/hydrology.py:367`), `_mouth_directions` (`:802`), `_flow_order` (`:1072`, for the topological order of the parts) and `_read_pgw_polygons` (`core/unit_ownership.py:152`).

### Parts (D1, D2, D16)

1. A basin's closed set brings its area, the NMT sheets, the BDOT10k counties and the HSG raster; the PGW GeoPackage comes from `--units` beside the set, as today. Its JCWP (`zlewnie_jcwp_rzecznych`, `pozostale_obszary_jcwp`) are the units of ADR-071 and the nodes of the JCWP graph.
2. The grouping follows the graph, after the topology: it grows parts from the basin's outlet JCWP up the graph while the part's window stays within the budget. A part is a connected upstream subtree: a root JCWP, whose outlet is the part's, and the JCWP whose path down the graph reaches the root inside the part; what it leaves out above it are whole parts, each entering it at one inlet. A JCWP thus belongs to the part of the JCWP it drains into, unless it is the root of a part of its own, and never to a part by its code (E7-GAP-03). A part whose outlet drains less than the largest stream threshold (10 km², `core/constants.py:26`; e.g. Stary Bóbr alone) joins the part below. The grouping avoids cuts at reservoirs, lakes and confluences (D4) and keeps pond complexes in one part. A part is named by the `MS_KOD` of its root; the partition (part → JCWP, the topological order) is a file of the basin, the same for one set and budget [proposed].
3. A part's window is its outline buffered by 1 km, as a rectangle on the basin's grid; cells beyond the buffered outline are nodata. At 90 M grid cells and 42–61 % data per window, the Barycz and the Bóbr's Polish part need about 5–6 parts each at 5 m [INFERENCE]; at 1 m a part's window is at most 90 km².
4. Preparation: what works per cell (buildings, repaired holes) runs per window; what works along lines (the burning depth, ADR-072's smoothing, ADR-077's directions by every rule, lake outflows) runs once per basin on the topology's lines, side channels cut, with the DEM sampled along them, and is rasterized into every window, so both windows of a seam burn the same values [proposed: the answer to ADR-071's `:52`].
5. Fill and D8 per window, with the code of today's whole-grid fill (`fill_whole_grid`) and the window's edge as outlets.
6. Ownership: a cell belongs to a part when its D8 path in the part's window reaches an outlet of the part without passing an inlet of the part. A cell that two parts claim, or none (windows that disagree on a flat, a path that leaves the window), goes to the part whose JCWP holds its centre and is listed in the seam report, so every cell has one owner, as the tiles need; a D8 cycle across a seam is broken the same way [proposed].

### Partition check (D16)

It runs on every partition, the one the grouping grows and one given as a file (T1 gives the scenario's), after the topology and before any download or bootstrap of the basin:

1. Coverage: every JCWP of the basin lies in exactly one part.
2. One outlet: a part has exactly one outlet edge, from one of its JCWP to a JCWP outside it, or holds the basin's outlet JCWP and has none; its outlet point lies on the burned line of the main river of the part's root (for a reservoir, on the river leaving its lake).
3. Inlets: every edge into a part, from a JCWP outside it, is the outlet of exactly one part above: that JCWP is the root of its part, and no other part's outlet falls on the same inlet cell.
4. A failure is an error, not a seam-report warning (D10 covers the seams only). The command writes no partition, a part's bootstrap refuses a basin without a passed partition, and the message lists for each failing part its outlet edges as JCWP → receiving JCWP (codes, names, outlet points), each with the JCWP above it in the part.
5. The scenario's grouping of the Bóbr fails it. Its part 1 has four outlet edges into `RW60001116599` (the Bóbr from the Żeliszowski Potok to the Kwisa, part 2b), at three points: `RW600003163759` (the upper Bóbr) and `RW60000616376` (the Żeliszowski Potok) at 258368, 375472; `RW600006163794` (the Młynówka) at 259564, 383811; `RW60000616389` (the Bobrzyca, `RW600003163859` above it) at 260945, 390197. An outlet is an edge, so the fix that E7-GAP-03 proposes, the Młynówka and the Bobrzyca moved to part 2, still fails: the Żeliszowski Potok drains into 16599 beside the upper Bóbr, so it belongs to the part of 16599 or to a part of its own.

### Grid and cell size (D2, D3)

1. A basin has one grid. Its cell size is the coarsest among its DEM inputs, the NMT sheets of its set that cover it: 5 m when any of them is 5 m, 1 m only when all are 1 m. Its lattice is that of those sheets, whose corners agree modulo the cell size. The basin registry records both; every part, every re-run and the inlet table use them, and the bootstrap derives them from the set instead of taking `--resolution` (`scripts/bootstrap.py:1806-1811`) [proposed].
2. A finer input is averaged onto the grid by ADR-087's method, `align_to_cellsize` (Facts): `gdalwarp -r average` at the grid's cell size over the input's frame grown outward to whole cells of the lattice, nodata left out of the mean; a 5 m cell is the mean of the valid 1 m cells within it. An input coarser than the grid cannot occur, since the grid takes the coarsest, and `align_to_cellsize` refuses one anyway (`utils/raster_utils.py:252-256`).
3. One change for the parts: `align_to_cellsize` takes the lattice from the run's own sheets, (0, 0) when the run has none of its cell size (`utils/raster_utils.py:234-244`), so a part whose window holds only 1 m sheets in a 5 m basin would land on another lattice. Every part gets the basin's lattice instead.
4. The basins of one instance share its grid, so one VRT per raster serves them all: the instance's cell size is the coarsest among its basins' inputs, and a basin wanted at a finer cell size gets its own instance [proposed].
5. Resolution-agnostic: the method works at any cell size, fixed per basin. The budget counts cells, 90 M per window, about 2,250 km² of window at 5 m and 90 km² at 1 m, so a finer basin needs more parts, not another design. Thresholds stay areas in m² (`core/unit_hydrology.py:599`), and the readers take the cell size from the raster (`core/cell_parameters.py:125-127`).

### Memory budget (D2)

1. The budget is 90 M grid cells per window under the 8 GB cap, counted with nodata: the fill reads the whole window into one array (`core/unit_hydrology.py:211`, `core/raster_io.py:199`), and the fill, the D8 and the later stages allocate on the window.
2. Its margin: Barycz 1's window of 188.6 M grid cells (111.0 M with data) completed under the 8 GB cap; 90 M is under half of it and below every window of the scenario. That peak, like every part's, sat at about 98 % of the cap, so it bounds the need without measuring it [INFERENCE of the report].
3. Every run's report keeps its peak memory per stage (`scripts/process_dem_units.py:17-18`); a part that exceeds the cap becomes smaller parts (D2).

### Inlets (D4, D5)

The inlet table comes from the vectors alone, once per basin and set and before any part runs, so both runs of a seam read the same cell of the basin's grid. An inlet is the outlet of a part above; the downstream run starts the river at the next cell down.

| Case | Inlet |
|---|---|
| The main river | the burned BDOT10k watercourse with the MPHP identifier of the upstream part's outlet JCWP, oriented by ADR-077 and the MPHP order; the cell of the basin's grid that holds its intersection with the part boundary |
| Several intersections (meanders across the boundary, a line along it) | the last exit along the flow |
| A reservoir or lake on the cut | the lake's outflow, where the outflowing line leaves the OT_PTWP_A polygon |
| A cut less than 200–500 m from a confluence | the partition moves the cut (the JCWP on both sides into one part); where the budget forbids it, the inlet stays, flagged |
| An unburned ditch or canal (OT_SWRM_L, OT_SWKN_L without an MPHP identifier) or a side channel crossing the boundary | none; the seam report lists it |
| The CZ border, at this stage (D11) | where the burned line reaches the border on the PL DEM; its upstream area unknown, its delineations marked `catchment_truncated` |

No other watercourse is an inlet, so a secondary inlet cannot exist (D5):

- A watercourse without a JCWP of its own lies inside the JCWP of the stretch it joins, since PGW's JCWP are the catchments of their stretches, and so inside the part where it joins. One with a JCWP of its own drains, in the JCWP graph, into the JCWP of the stretch it joins: it lies in that JCWP's part, or it is the root of a part above, whose outlet it then is, a main-river inlet of the table. The partition check enforces this; the scenario's grouping by code broke it (E7-GAP-03).
- Every inlet drains a whole part above it, at least 10 km² (Parts 2), so its river exceeds every stream threshold.
- What remains is a burned watercourse that crosses a part boundary where the JCWP divide and the DEM disagree. Within the 1 km buffer the D8 ownership gives its cells to the part where it joins. Where its catchment reaches beyond the downstream window, the seam report lists it with the area beyond the window that drains through it: a warning only, with no inlet, no record and no re-run.

Each upstream run checks its inlets: its owned cell of the highest accumulation near each crossing lies within D4's N cells of the inlet, else a warning in the seam report.

### Inlet record (D5)

One record per inlet, written by the upstream part's run [proposed fields]:

| Field | Meaning |
|---|---|
| `inlet_id` | stable: basin, downstream part, kind, MPHP identifier, ordinal |
| `basin_id`, `upstream_part`, `downstream_part` | the basin and the parts' ids |
| `kind` | `main_river`, `lake_outflow` or `border` |
| `row`, `col`, `x`, `y` | the inlet cell on the basin's grid and its centre, EPSG:2180 |
| `mphp_id`, `name`, `bdot_layer`, `bdot_id` | the BDOT10k line |
| `run_id` | the upstream run that wrote the values |
| `upstream_cells`, `upstream_area_km2` | the accumulation offset |
| `longest_flow_path_m` | the longest flow path to the inlet (hydraulic length) |
| `distance_to_source_m` | along the main stream |
| `strahler_order` | per threshold |
| `segment_idx` | the upstream outlet segment, per threshold |
| `elevation_m` | the filled DEM at the inlet |
| `dem_check_cells` | the distance of D4's check; a warning above N |
| `area_outside_data_km2` | border inlets: null at this stage (D11) |

### Order and attribute pass (D5)

1. A part's geometry needs no other part. Each run seeds its inlets with an accumulation above the largest threshold: the record's upstream area where the record exists, else the area of the JCWP above the inlet in the graph (pyflwdir's `accuflux` from initial values, or the offset added along the path in the routing on disk). Its fill, D8, streams at every threshold, segments and sub-catchments are then final whatever the order of the runs.
2. Only the attributes along the main river below an inlet need the record of the part above: the upstream area, the longest flow path and hydraulic length, the distance to the source, the Strahler order, and the part's own outlet record for the part below. Only they keep the topological order: the runs go upstream first where they can, as T1's chain does, so each run applies the records of the parts above it.
3. The attribute pass carries a later change down, part by part, upstream first: after an upstream part is re-run, or after a part ran before the part above it. Along the D8 path from each inlet to the part's outlet it adds the change of the inlet's upstream area, takes the longer of the local and the inlet's longest flow path and distance to the source, and recomputes the Strahler order with the inlet's. It updates those rows (`upstream_area_km2`, `strahler_order`, the flow distances), the cells of those paths in the raster tiles and the stream tiles, and writes the part's outlet record for the next part down. It touches one path per inlet (tens of kilometres, about 10⁴ cells at 5 m), not a raster: no fill, no D8, no stream extraction.
4. A part run before the part above it publishes the PGW estimate below that inlet with a warning in its record and the seam report; the attribute pass clears it once the part above is published.

### One database (D7, D8)

- A basin registry: the basin's id and name, its project and set (their identity as `instance.json` records it today), its area, grid (cell size and lattice), partition and parts.
- `basin_id` and `part_id` on `processing_runs` (the one-active index per part), on the DEM-derived `stream_network` rows, `stream_catchments`, `land_cover`, `soil_hsg`, `bdot_streams`, `depressions`, the sewer tables and every other table a bootstrap fills for its area (H3 makes the inventory; precipitation stays upserted by point).
- `publish_run` deletes and inserts its part's rows only, in one transaction; the imports delete by `part_id`, never by a box (the 466 m strip), and clip land cover and soil to the part's JCWP outline, so the parts' rows tile each basin; `clean` takes a basin or a part.
- `segment_idx` stays the key with `threshold_m2`, unique in the instance: each run takes the next free dense range per threshold at its start and records it, so the graph, the label tables (`core/network_delineation.py:899`), the MVT tiles, the API and `hydrolog-network/1` keep their key, and nothing public changes after the release [proposed]. A cross-part edge is the upstream outlet segment's `downstream_segment_idx`, set to the downstream inlet segment and re-linked at every publish of either part.
- Whole-part aggregates per part and outlet: the dissolved outline, the area, the elevation histogram, the slope, the land cover and soil group shares, the stream length. A delineation that reaches an upstream part's outlet takes its aggregate instead of its nodes, and continues through that part's inlets.
- The graph holds every basin, one or more components each, and loads when the API starts, not in the first request (E5b-01); loading it by part waits for the Odra.

### Rasters, tiles and the GUI (D7, D8)

- Every part writes its tiles on the basin's grid, which the instance's basins share; one VRT per raster lists the tiles of every part's active run of every basin and is rewritten (XML only) at each publish; a pointer names one run per part; a part's DEM mosaic and run go to `data/nmt/<basin>/<part>/`.
- MVT tiles: tippecanoe on the part's own rows, then `tile-join` into the instance's tiles; a re-run joins its part again.
- DEM tiles and overlays: only the tiles that a re-run part intersects, cut from the instance's VRT so the tiles at a seam or between two basins hold both, with one colour range per instance.
- `instance.json`: `area` names the instance and `nmt.resolution_m` keeps its one cell size; `basins` lists each basin (name, project, set, area, sources) with its `parts` (id, name, area, run, activation) [proposed: fields added within version 1, ECO-072].
- Frontend: the area label and the welcome text name the basins; the map fits their union, with a list that zooms to a basin.
- Admin panel: the basins, their parts, active runs, seam reports and side channels; a part's run started from its basin's project and set, one at a time.
- A delineation that holds a border inlet, or whose outline follows the edge of the data where flow enters, gets the notice `catchment_truncated` (`REPORT.md:273`) in the panel and in the hand-off; the missing area stays unknown at this stage (D11).

### Archiwista (D9)

Unchanged. One project per basin with the whole basin as its area, and one closed set with everything of the basin: for the Barycz, 1,213 NMT sheets at 5 m (with 1 m sheets where 5 m ones are missing, ADR-087), the BDOT10k counties of the frames and the HSG raster. Hydrograf takes each part's sheets and counties from the set by the part's window (ADR-067 and ADR-076 per window). Two basins are two projects and two sets, one source each (D8).

### Seam report (D1, D4, D5, D10)

Written with every run, per pair of neighbouring parts and per basin (JSON, and a GeoPackage of crossings and disputed cells), and shown in the admin panel:

| Item | Content |
|---|---|
| Inlets | cell, kind, DEM check, a missing record (a part run before the part above it) |
| Crossing area | the area whose D8 crosses the JCWP boundary outside an inlet, per stretch of boundary and direction |
| Crossing watercourses | burned watercourses that cross a part boundary outside an inlet, each with the area beyond the downstream window that drains through it |
| Disputed area | cells that two parts claim, or none; cycles broken |
| Unburned crossings | ditches, canals and side channels crossing a boundary |
| Warnings | over a threshold [to calibrate in H4; e.g. 0.1 % of the smaller part and 1 km² per boundary] |

Every item only warns, and a run over a threshold still publishes (D10); the remedy is the partition (JCWP moved between parts, a larger buffer), not a patch [proposed].

## Branches and release (D13)

- Nogat: this plan on the branch `plan/large-basins` (worktree `~/workspace/wt/nogat-large-basins`), not merged into `develop` until the author decides (DEV-3.3).
- Hydrograf: the branch `feature/large-basins` from `develop` `939b55f` (worktree `~/workspace/wt/hydrograf-large-basins`), pushed without code. Code starts only after this plan's `Approved:` line (DEV-17.4), under Hydrograf's `CLAUDE.md` (DEV-3.4); the H-steps' topic branches start from and merge into `feature/large-basins` [proposed], which takes `develop`'s later changes by merges.
- The work does not touch candidate-5 or the first joint release. `feature/large-basins` merges into Hydrograf's `develop` only after the first joint release (the author's decision), as an update, with the author's approval (DEV-3.3). After the release a released format changes only with the author's consent (ECO-072); the design only adds fields.

## Steps

Hydrograf only at this stage (D9, D11, D12); each step in its own session and branch under Hydrograf's `CLAUDE.md` (DEV-3.4, DEV-17.5); Hydrograf's ADR and plan carry its detail (DEV-17.2, DEV-17.4); bootstraps as user systemd units (DEV-17.6). Nothing starts before this plan's `Approved:` line.

| # | Project | Change | Depends on | Verified by |
|---|---|---|---|---|
| N1 | Nogat | this plan on `plan/large-basins`; after Hydrograf's merge, PROGRESS, and the registry only if an exchange changed | – | Nogat's gate |
| H1 | Hydrograf | an ADR amending ADR-071, ADR-067, ADR-077 and ADR-087 (the topology before the parts and the partition check, parts within 90 M grid cells, one grid per basin, side channels cut, main-river inlets, the attribute pass, one database for several basins, a source per basin) and noting ADR-080's network across parts; Hydrograf's plan | this plan approved | the author's review |
| H2 | Hydrograf | the network topology and the partition, before any bootstrap (Network topology 7): the lines with the side channels cut, the JCWP graph, the grouping into connected upstream subtrees within 90 M grid cells with an outlet of at least 10 km², the partition check as an error, the inlet table; a part's bootstrap refuses a basin without a passed partition | H1 | synthetic networks: a part with two outlets, one with none, an inlet that is no part's outlet, two outlets on one inlet cell, a bifurcation; the scenario's grouping of the Bóbr rejected (Acceptance 2); the partitions of the Barycz and the Bóbr pass, their side channels listed |
| H3 | Hydrograf | the database and the stores: the basin registry with its grid, `basin_id` and `part_id` on runs and on every table a bootstrap fills, one active run per part; `publish_run`, land cover, soil, `bdot_streams`, depressions, the sewer and `clean` by part; the instance-wide segment numbers; a directory and pointer per part; the bootstrap's source per basin and part (`--project`, `--set`, a part) | H2 | a part of the Barycz and a part of the Bóbr in one database: each publish leaves the other's rows and files unchanged (E7-08 closed), the 466 m strip included |
| H4 | Hydrograf | the basin's grid and lattice given to every part, the windows, the preparation along lines, ownership by D8, the seam report with its warnings | H3 | synthetic DEMs for each case of the inlet table and for a bifurcation; the Orla in three parts and its seam report |
| H5 | Hydrograf | inlet records, the seed at the inlets, the attribute pass in topological order, the warning of a part run before the part above it | H4 | synthetic DEMs: the parts equal the whole run; an upstream re-run changes only attributes; a part run out of order equals, after the pass, the run in order |
| H6 | Hydrograf | the graph across parts and basins, loaded at start; delineation across parts with whole-part aggregates; precise-mode and network windows across a seam | H5 | the Orla: whole run against parts (Acceptance 1); windows across a seam |
| H7 | Hydrograf | the VRTs over every part, per-part MVT export and `tile-join`, DEM tiles and overlays per part; `instance.json` with `basins` and `parts`; the map, the area label and the welcome text for several basins; the admin panel's basins, parts, runs, seam reports and topology; `catchment_truncated` | H3, H6 | two basins in one instance in the GUI; MVT and DEM tiles continuous across a seam; `instance.json` |
| T1 | e2e | the Acceptance on the Barycz and the Bóbr in one instance, from two Archiwista projects and two closed sets, with the scenario's harness (below) | H1–H7 | Acceptance |

T1's first case gives the partition check the scenario's grouping of the Bóbr (`czesc` of the layer `jednostki_jcwp` of `/data/nmt/e2e-2026-11-15/geo/zlewnie_barycz_bobr.gpkg`, made by `geo/build_geo.py:26-29`, `:50`), which must be rejected before any bootstrap (Acceptance 2). Its harness: copies of `~/workspace/_e2e/2026-11-15/scenario/E7/run_part.sh`, which runs one bootstrap with its memory sampling and starts the instance after it, and `E7/chain_parts.sh`, which chains the runs behind a free-memory gate. Both are adapted to one shared instance, the topological order of each basin and the 8 GB cap. `E6/run_gpt.sh` gives the GUI tasks to GPT, even when it hits its usage limit (`LIMIT_HIT` in its log); Claude then continues the task and the report notes the switch. The errors in the upper Bóbr, beyond the Czech border, are accepted (D11).

## Acceptance

1. Equivalence: the Orla (Barycz 2, 1,599.3 km², 75.7 M valid cells), run whole as in the scenario and in three parts, has the same D8 on every cell outside the seam report's disputed cells, and the upstream areas of its nodes at the 1 km² threshold agree within ±0.5 %. Re-running an upstream part changes only attributes downstream; a part run before the part above it equals, after the attribute pass, the run in topological order (D5).
2. Partition: each basin's topology and partition check run from the vectors alone, before any bootstrap, and the partitions of the Barycz and the Bóbr pass, every part with one outlet on its main river. The scenario's grouping of the Bóbr by MPHP code group is rejected with an error that names the Młynówka (`RW600006163794`) and the Bobrzyca (`RW60000616389`, with `RW600003163859` above it) draining into `RW60001116599` of part 2b, beside the upper Bóbr and the Żeliszowski Potok at the cut, and no part of that partition is bootstrapped.
3. Grid and inlets: every part of a basin lies on the basin's grid (one cell size, one lattice), its finer sheets averaged by ADR-087's method; every inlet of the partition is a main river draining at least 10 km².
4. Side channels: each basin's side channels are listed with the rule that cut each, none is burned, and on a synthetic bifurcation the D8 follows the DEM through the side channel's cells.
5. Seams: every boundary has its report in JSON, GeoPackage and the admin panel; a seam over a threshold publishes with a warning, and T1 lists every warning with its areas.
6. Memory: every part's window holds at most 90 M grid cells, and every run completes under the 8 GB cap, its report giving the peak of each stage.
7. Two basins in one instance: the Barycz and the Bóbr from two projects and two closed sets; a part's bootstrap leaves the other parts' and the other basin's rows, files and tiles unchanged (counts and checksums per part before and after); the GUI shows both basins, and the admin panel lists both with their parts.
8. Continuity: a delineation at each basin's mouth crosses all its parts, and its area agrees with the basin's JCWP outline (the Barycz 5,543.2 km², the Bóbr's Polish part 5,649.4 km²) within ±1 % [to calibrate in H4]; a delineation in the upper Bóbr that holds the border inlet carries `catchment_truncated`, and its missing Czech area is an accepted error (D11).
9. Optional diagnostic, not a criterion: the delineated areas at the IMGW-PIB gauges of the two basins against the catalog's areas (Appendix).

## Risks and open questions

Risks:

- Seams in flat land: ADR-071 met closed basins wider than a 16 km halo, so a 1 km buffer leaves disputed area, and its size decides whether D1 holds [INFERENCE].
- The Barycz's fish ponds: their supply canals and mill races are side channels, cut by D15, so the ponds' water follows a flat, embanked DEM, and the D8 tree there is the terrain's, not the canals' [INFERENCE].
- Side channels misread: a canal that leaves a river and ends without rejoining one, whose MPHP identifier has the river's as a prefix, is oriented by ADR-077's rule 1 towards the river and looks like a tributary; it stays burned unless BDOT10k marks it a side arm (H2 lists such lines).
- JCWP without one receiver: where a JCWP's PGW river line and the burned lines disagree, or its main river carries no MPHP identifier, the topology finds no receiver or two, and the basin stops until the cause is found [INFERENCE: how often is unknown until H2 runs both basins].
- Reservoirs on the Bóbr and the Kwisa (Bukówka, Pilchowice, Leśna) on JCWP boundaries: the lake-outflow rule, or parts that keep each reservoir whole.
- The preparation along lines is new code; where it differs from today's whole-DEM smoothing, the windows of a seam disagree where streams enter.
- 1 m: 25 times the cells of 5 m, so about 25 times the bootstrap time per km² (the Barycz 3–4 days at the scenario's 1.84–2.36 s/km²) [INFERENCE: linear in cells]; a 90 km² window keeps less than two thirds of its area inside its 1 km buffer, and the seams multiply.
- The graph of both basins (806,916 nodes in the scenario's 7 parts) in one API process, loaded at start: its memory is unmeasured.
- The Odra (~119,000 km²): at most 2,250 km² per window at 5 m means at least 53 parts; the measured 72 graph nodes per km² give about 8.6 M nodes, and 6.3 MiB per km² of data, tiles and database (`REPORT.md:96`, `:373-382`) about 0.7 TiB [INFERENCE: linear].

Open questions for the author:

1. Formats after the release: the instance-wide segment numbers keep the API, the tiles and `hydrolog-network/1` as they are, and `instance.json` gains `basins` beside `area`; may these additions stay version 1 (ECO-072)?

## Follow-ups (outside this plan's steps)

- Czechia (D11), a separate plan, owners Kartograf then Hydrograf. Kartograf: ZABAGED, the Czech counterpart of BDOT10k, and whatever else the analyses need across the border, e.g. catchment polygons, which only DIBAVOD A07 outside Kartograf gave (GEO-06); DMR 5G is already in Kartograf. Hydrograf: the CZ DEM in the set reader (GEO-01; today only `nmt/pl_1992_<resolution>_evrf2007`, `utils/kartograf_set.py:77`), the Czech lines in burning and inlets, and the border inlet replaced by continuity, so that Błażkowa and Żagań get their whole catchments. These were the first draft's K1 and H8.
- Archiwista: nothing for this plan (D9). E7-01's area change accepted under a closed set is Archiwista's own finding; a set that pins the PGW GeoPackage only if `--units` beside the set proves insufficient.
- The split of flow at bifurcations and side channels: later models, Hydrolog and Hydraulik; the GIS stage stays a single-flow D8 tree (D15).
- The Odra's scale: thresholds per part, the graph loaded by part.

## Appendix: possible extensions (not in this plan's steps)

Gauges, kept from the first draft as ideas (D12). Gauge data would be an optional input, from the user or from a file export of Obserwator's catalog, never a requirement of a bootstrap, since Hydrograf must eventually be free of IMGW-PIB's data but must allow using it.

Facts:

- In Barycz 1 the precomputed delineation differs from IMGW-PIB's area by +0.25 % (Odolanów, 159.53 against 159.13 km²), +0.17 % (Kanclerzowice) and +0.74 % (Łąki, 1,760.71 against 1,747.85); in the other parts by −3.65 % at Korzeńsko (the click snapped 0.7 km away) and +5.88 % at Rydzyna, unexplained (`REPORT.md:14`, `:277`). The precise mode at a gauge's catalog coordinates, 5–10 m off the stream, returns 0.0003 km² (E5b-03, `REPORT.md:187`). The two basins hold 42 IMGW-PIB hydrological gauges with an area, 10 on the Barycz and 32 on the Bóbr (`/data/nmt/e2e-2026-11-15/geo/stacje_barycz_bobr.csv`).
- 2,140 of IMGW-PIB's 3,808 stations have no location in Obserwator's catalog, partly because the static source `python -m obserwator.reference_data` was skipped; live `stations find` gives a 2-digit `hydrographic_code` (GEO-03, GEO-04, `REPORT.md:176`, `:208`). The catalog's station properties include `river`, `hydrographic_code`, `river_km` and `catchment_area_km2`, with a location uncertainty of at least 150 m (Obserwator `f4f6a8d`, `src/obserwator/store/catalog.py:130-158`); the area comes from IMGW-PIB's station details only (`:163-169`, `:805`), so ČHMÚ gauges have none.
- Hydrolog's `route network` already takes given discharges for a subcatchment, inline or as a column of `inflows_file` (Hydrolog `d82982a`, `src/hydrolog/operations/_network_input.py:27-32`).

Extensions:

1. Gauge control after a bootstrap: each gauge of a part snapped to the burned BDOT10k line of its river (within ~300 m, the river km as a second hint), delineated from the graph at the finest threshold (never by the precise mode at the catalog point), and compared with its published area within a tolerance by size (e.g. ±2 % above 1,000 km², ±5 % at 100–1,000, ±10 % below 100), a reference rather than the truth; statuses `ok`, `outside_tolerance`, `partly_outside_data`, `not_snapped`, `no_reference`; one table per instance; the GUI showing the model's and the gauge's area.
2. Analysis segments on very large rivers (the Odra): the reach between two gauges has a differential catchment, a graph query across parts. A network (ADR-080) with control points at the gauges and the tributaries' mouths goes to Hydrolog, which routes the observed upstream hydrograph through the reach, adds the tributaries (observed where gauged, SCS-CN up to 250 km² where not) and the przyrzecze, compares the result with the downstream gauge and balances the differential catchment.
3. Tributaries that fit whole: their gauges as control points, compared with the series and with Hydrolog's Q1% quantiles.
4. What they would need, the first draft's O1, L1, H7 and H9: Obserwator, every hydrological station located (GEO-03), the full `hydrographic_code` (GEO-04), the MPHP code of a gauge's river and ČHMÚ areas; Hydrolog, observed inflow nodes in `hydrolog-network/1` and the balance of a differential catchment; Hydrograf, the gauge table and the network with observed inflow nodes; Nogat, the registry's edges.

## Results

None yet.
