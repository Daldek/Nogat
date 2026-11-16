# Plan: large basins in one Hydrograf instance

Approved: pending

Status: a draft of 2026-11-16 from the scenario test of 2026-11-15/16, revised the same day with the author's second round of decisions; not approved, so no code starts (DEV-17.4). The decisions are the author's (two rounds of 2026-11-16, the second with the coordinator's answer to the old question 9); the design marks its own proposals „[proposed]”.

Requirements: HUB-5.2, DEV-17.4, DEV-17.5 and DEV-3.4 (each project in its own session and branch), DEV-17.2 (Hydrograf records its decisions as ADRs), DEV-3.3 (merges with the author's approval), DEV-17.6 and ECO-073 (bootstraps run as user systemd units), ECO-054 (the project and its set are Archiwista's), ECO-072 (a released format changes only with the author's consent).

## Goal

One Hydrograf instance serves whole large basins, one or several: the Barycz (5,543.2 km²) and the Bóbr (5,881.8 km², 232.4 km² of it in Czechia) together, later the Odra. The data are continuous: one address, one database, delineation and parameters across each whole basin. A basin is composed of many runs, its parts, each within a fixed cell budget under the 8 GB cap of a bootstrap: the method composes many analyses into one whole instead of fitting an area into one run. It does not depend on the resolution: as the DEM gets finer (the author plans to work at 1 m), the budget stays and the parts get smaller. The priority is the work done with adequate quality, not the fewest runs.

## Facts

Source: the scenario test of 2026-11-15/16 on the Barycz and the Bóbr, report `~/workspace/_e2e/2026-11-15/scenario/REPORT.md` (in Polish, cited as `REPORT.md:<line>`) and the coordinator's findings `COORD-FINDINGS.md` beside it. Hydrograf's code at `develop` `939b55f` (the member of candidate-5; code paths under `backend/`).

### The scenario test

- **No second part in one instance** (E7-08, `REPORT.md:148`, `COORD-FINDINGS.md:8`): a second bootstrap into an instance replaces the first part, mixes land cover and soils, and gets no inflow from the part above. The workaround was one instance and one address per part: 7 instances for two basins, 7 databases of 9,509 MiB together (`REPORT.md:96`, `:254`).
- **Truncated catchments look complete** (G07-2 = G09-2/3, `REPORT.md:150`): a catchment cut by the edge of a part or by the Czech border is shown without a warning, e.g. Błażkowa with 13.46 km² against the 103.54 km² of IMGW-PIB's catalog.
- **Memory** (E7-09, `REPORT.md:87-97`, `:117-127`, `:162`): Barycz 1 (2,393.3 km²) ran under an 8 GB cap on a window of 188.6 M grid cells (11,663 × 16,173), 111.0 M of them with data; step 3 took 2,467.8 s and the bootstrap 5,631.4 s (21:53–23:27), with logged peaks of 8,003 MB (polygonize_subcatchments), 8,064 MB (secondary_rasters, 98.4 % of the cap) and 8,045 MB (publish) (log `/data/nmt/e2e-2026-11-15/logs/hydrograf-barycz-bootstrap-run-20261115-215308.log:154-155`, `:203`, `:212`). The six other parts ran under 9 GB on windows of 108.9–196.7 M grid cells and peaked at 7,618–9,065 MB, about 98 % of the cap whatever their size (Bóbr 2a, 108.9 M grid cells, 8,147 MB), so the logged peak is bounded by the cap, not by the need [INFERENCE of the report]; `docker stats` sampled 6,830–7,495 MiB. Bóbr 2 PL (296.7 M grid cells), estimated at 10–12 GB [INFERENCE of the report], was split along JCWP into 2a (108.9 M) and 2b (135.0 M) before it ran.
- **Time** (`REPORT.md:37`, `:96`, `:101-102`, `:134`): the 7 bootstraps took 24,024.5 s (6 h 40 min), 1.84–2.36 s/km²; the longest steps are step 3, the NMT (685–2,468 s), and step 8, the MVT tiles (756–2,093 s). The chain of five parts ran 00:10:52–05:08:06, one at a time behind a gate of 9,500 MB free memory.
- **Whole basins on the 5 m grid**, computed for the first draft from the scenario's sheet lists (`/data/nmt/e2e-2026-11-15/geo/sheets/`, frames by Kartograf's `SheetParser.get_bbox`; Barycz 1's frames give the logged 188.6 M): the Barycz has 1,213 sheets, 24,578 × 15,288 = 375.7 M cells, of which 221.7 M valid; the Bóbr's Polish part 1,297 sheets, 17,643 × 32,123 = 566.7 M cells, of which 226.0 M valid. The scenario's windows held 42–61 % data (`REPORT.md:89-95`).
- **The two basins together** (`/data/nmt/e2e-2026-11-15/geo/zlewnie_barycz_bobr.gpkg`, EPSG:2180): the boxes of the outlines lie 1.8 km apart (x 220.5–306.4 km for the Bóbr, 308.2–430.1 km for the Barycz) and together span 209.6 × 160.1 km, 1,341.7 M cells at 5 m (33.5 G at 1 m), of which the basins cover 34 %. The sheet boxes of Bóbr 1 (x ≤ 308,278) and Barycz 3 (x ≥ 307,812) overlap in a strip of 466 m × 8.2 km (the „Mosaic extent for BDOT10k” lines of `logs/hydrograf-bobr-bootstrap-run-20261115-232835.log` and `logs/hydrograf-barycz-3-bootstrap-run-czesc-3-20261116-030033.log`).
- **One area per Archiwista project** (E7-01, `REPORT.md:151`): `AreaChoice` holds one area (`src/archiwista/api/models.py:3177`, `800231c`), and changing it under a closed set returns 200; the workaround was 8 projects, one per part.
- **Czechia** (GEO-01, GEO-06, `REPORT.md:149`, `:204`): Hydrograf reads no CZ DEM, so the Bóbr's 232.4 km² in Czechia are outside the model. Kartograf has CZ watercourse lines as HY-NET (`hydro download --product network --country cz`, `src/kartograf/catalog/commands/hydro.py:1` at `e14bc78`), which Hydrograf does not read, and no CZ catchment polygons (DIBAVOD A07 was used outside it).
- **Network window** (E5b-10, `REPORT.md:191`): a network closing at Łąki is refused, `network_window_too_large`, 135,118,485 cells over 60 M (`/data/nmt/e2e-2026-11-15/e5b/network/laki-window.json`).

### Hydrograf at `939b55f`

- **One run per instance.** The unique index `idx_processing_runs_one_active` allows one active run (`migrations/versions/005_processing_runs.py:70-71`); `publish_run` (`core/unit_run_store.py:516`) deletes every DEM-derived `stream_network` row and every `stream_catchments` row (`:600`, `:603`).
- **ADR-071 and its amendment** (`docs/decisions/0071-pgw-units-and-boundary-event-routing.md`): PGW units own the outputs (tiles, records, resume), not the computation. Fills per unit window never agreed on the seams at 5 m (closed basins wider than any halo, flats broken differently by each window; the halo grew from 500 m to 16 km, `:65`), so the fill and D8 run once on the whole grid at about 18 B per cell, and „a larger area needs the fill itself to change, not windows” (`:71`). Burning, smoothing, buildings and lakes run on the whole DEM too: a window changed 37 cells by up to 5.2 m where a stream enters it (`:52`).
- **The run's grid in one array.** `fill_whole_grid` (`core/unit_hydrology.py:182`) reads the run's whole DEM (`:211`, through `core/raster_io.py:199`, `src.read(1)`), the box of the set's sheet frames (`utils/kartograf_set.py:298`; the mosaic at `scripts/bootstrap.py:579-583`); the fill and the routing scratch are removed after the run, and the run keeps per-owner tiles of `02_filled`, `03_flowdir`, `04_flowacc`, `06_streams` and the other rasters (`scripts/process_dem_units.py:14-24`, `:794-803`).
- **Units.** A PGW polygon owns the cells whose centre it holds, and a cell outside every polygon goes to the nearest owner (`core/unit_ownership.py:284`); the layers are `zlewnie_jcwp_rzecznych` and `pozostale_obszary_jcwp` (`:34-35`), from a `--units` file beside the set (`scripts/bootstrap.py:1696-1705`).
- **Rasters.** Per-owner tiles and one VRT per raster on the run's grid, every valid cell in exactly one tile, verified before anything is replaced (`core/unit_rasters.py:24-26`, `_write_vrt` at `:386`, `write_unit_mosaics` at `:550`); the API reads the VRTs of the run that `active_run.json` names (`core/active_run.py:121-140`, `core/config.py:240-252`).
- **Graph.** In memory, keyed by `(threshold_m2, segment_idx)` (`core/catchment_graph.py:156-157`, `:282`) and loaded from the whole `stream_catchments` (`:225-233`); its docstring sizes it at ~87k nodes (`:114`), Barycz 1 had 163,750 and the 7 parts 806,916 (`REPORT.md:96`). It loads lazily in the first request, about 6 min beside a bootstrap (E5b-01, `REPORT.md:165`).
- **Limits.** Precise-mode windows up to 40 M cells (`core/raster_service.py:42`), network windows up to 60 M (`core/network_delineation.py:115`), hydrographs up to 250 km² (SCS-CN, `core/constants.py:19`).
- **Burning and accumulation.** `dem.stream_burning: main` (default `all`, `core/config.py:353`) burns the OT_SWRS_L main courses that are rivers or carry `IDENTYFIKATORMPHP`, the OT_SWKN_L that carry it, and no OT_SWRM_L (`core/hydrology.py:367-388`); each MPHP watercourse is oriented towards its mouth (ADR-077, `_mouth_directions`, `core/hydrology.py:802`). Accumulation is `flw.upstream_area(unit="cell")` (`core/hydrology.py:2243`); pyflwdir's `accuflux(data)` accumulates from initial values.
- **Resolution.** A set's NMT comes at `1m` or `5m` (`utils/kartograf_set.py:72`), from `nmt/pl_1992_<resolution>_evrf2007` only (`:77`); one `--resolution` per run (`scripts/bootstrap.py:1806-1811`), finer sheets averaged onto the run's lattice (`gdalwarp -r average`, `:575-577`; ADR-087). Thresholds are areas in m², turned into cells by the run's cell size (`core/unit_hydrology.py:599`, `core/cell_parameters.py:132`), and the readers take the cell size from the raster (`core/cell_parameters.py:125-127`, `core/raster_service.py:128`).
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
| Precise mode, network window | windows grown around the click (`core/raster_service.py:42`) or the closing section's catchment (`core/network_delineation.py:705-750`) on one VRT | the instance's box costs nothing; a window across a seam reads both parts' tiles | works today on one VRT, one cell size |
| MVT tiles | every threshold of the whole tables exported (`scripts/generate_tiles.py:77-98`) and tiled by tippecanoe (`:121`) at every bootstrap; the API's stream and catchment tiles are queried by the tile's box (`api/endpoints/tiles.py:48`, `:109`) | a part's own export, then `tile-join`; the queried tiles work today | works with listed changes |
| DEM tiles, overlays | `dem.png`, the DEM tile pyramid (zoom 8–16) and `streams.png` from the whole mosaic (`scripts/bootstrap.py:1092-1160`), the pyramid deleted and rebuilt whole (`:1132`); memory stays bounded (strips, `scripts/generate_dem_tiles.py:1-11`; reduced blocks, `scripts/generate_dem_overlay.py:63-78`), time and disk follow the box | only the tiles of a re-run part, cut from the instance's VRT so the tiles at a seam hold both parts; one colour range per instance | works with listed changes |
| `instance.json` | one `area` (name, km², boundary file), one `nmt.resolution_m`, one `set` (`scripts/write_instance_info.py:311-335`); one `--area-name` (`scripts/bootstrap.py:1675-1679`); one list of sources (`core/data_sources.py:141`) | `basins`, each with its project, set, area, cell size, sources and parts; `area` names the instance | works with listed changes |
| Frontend | one area label (`frontend/js/instance.js:33-38`) in the welcome text (`frontend/js/welcome.js:47-52`); the map fits the bounds of the DEM tiles (`frontend/js/map.js:262-276`) | the label names the basins; the map fits their union, with a list that zooms to a basin | works with listed changes |
| Admin panel | a bootstrap from one box, sheet list or boundary file, never a project and set (`api/endpoints/admin.py:718-745`, `:796-808`), one at a time (`:794`); one boundary on its page (`frontend/admin/boundaries.js:4-5`) | basins, parts, runs and seam reports listed; a part's run from its basin's project and set, one at a time | works with listed changes |
| Cell size | per run, from the raster (above) | one VRT has one cell size: basins or parts at different sizes need a VRT per size | works with listed changes |

**Verdict: works with listed changes, no redesign.** Today the second basin replaces the first (E7-08). Once each run is one part's window, no step allocates the instance's box: the fill holds one window, the API's windows grow from a point, and the overlays work in bounded memory. Most changes are ones the parts need anyway: replacement by part, a run and its rasters per part, instance-wide segment numbers. Four belong to the basins themselves: a source per basin, the basin registry, `instance.json` with its basins, and the GUI and admin panel for several basins (D8).

## Options

| Option | Continuity | Memory | Detail | Decision |
|---|---|---|---|---|
| A. Closed JCWP parts joined at BDOT10k inlets, in one instance for one or several basins | whole basin, through the inlets; the seam measured, not exact | bounded by the budget of a part's window | any cell size | chosen |
| B. The whole basin in one run at 10 m | whole basin, exact | the Barycz 93.9 M grid cells at 10 m [INFERENCE: fits 8 GB] | 10 m | rejected by the author: the goal is a method that composes many analyses into one whole, not one area fitted into one run; the resolution will rise (1 m), where no basin fits one run; the priority is the work with adequate quality, not the fewest runs |
| C. A bigger machine, the whole basin at 5 m in one run | whole basin, exact | the Barycz's 375.7 M cells need about 6.8 GB for the fill alone (18 B per cell) and about twice Barycz 1's cap for the later stages [INFERENCE]; the Odra and 1 m out of reach | 5 m | rejected |
| D. Exact tiled algorithms (parallel priority-flood, TauDEM with MPI) | whole basin, exact | bounded by the tile | any | rejected: a second fill whose flats must agree with pyflwdir's, what failed in ADR-071 (`:65`), and a rewrite of the pipeline |
| E. A coarse 25 m pre-pass for the divides of the parts | whole basin | small pre-pass | 5 m | rejected by the author: the JCWP divides are the reference |
| F. One instance per part (today's workaround) | none: truncated catchments without a warning | per part | 5 m | rejected: 7 addresses and 7 databases for two basins (E7-08) |

## Decisions (the author, 2026-11-16)

| # | Decision | Round |
|---|---|---|
| D1 | Parts are aggregates of whole JCWP from Kartograf's PGW GeoPackage, cut along their boundaries, without a coarse pre-pass: the JCWP divides are the reference. Each part is processed with a ~1 km buffer; a cell belongs to the part its D8 flow reaches within the buffered window, and a seam report measures the area that drains across a JCWP boundary outside the inlets. | 1 |
| D2 | Budget and memory: the bootstrap's cap stays 8 GB, and a part that does not fit becomes smaller parts. The budget is a fixed number of grid cells of the part's window, nodata included, since the arrays are allocated on the window; it is derived from the cap with a margin. The budget does not depend on the cell size, so the parts shrink as the resolution grows (at 1 m a 90 M-cell window covers 90 km²). | 2 |
| D3 | Resolution-agnostic design: parts of one basin may have different cell sizes (1 m in a detailed sub-area, 5 m elsewhere) as a property the design keeps possible. The inlet record is geometric (coordinates and attributes in metres and m²), and each part rasterizes the BDOT10k lines on its own grid. | 2 |
| D4 | Inlets and outlets come from BDOT10k lines: the intersection of the JCWP's burned main river (chosen by its MPHP identifier and oriented by ADR-077 and the MPHP order, never by its vertices) with the JCWP boundary. At a reservoir or lake on the cut the inlet is the lake's outflow (better: no cut at a reservoir); cuts lie at least 200–500 m from tributary confluences; other burned watercourses crossing a boundary are further inlets; unburned ditches and canals enter only the seam report; a line running along the boundary gives its last exit along the flow. DEM check: the upstream part's owned cell of the highest accumulation lies within N cells (e.g. 10) of the inlet, else a warning. | 1 |
| D5 | Order: parts run in topological order, upstream first, always. The runs are sequential anyway under the 8 GB cap, so „any order” buys nothing, and every inlet record exists before the downstream run extracts its streams with the accumulation offset; this includes secondary inlets whose upstream area is near a stream threshold. When an upstream part is re-run and a secondary inlet's area crosses a threshold, the downstream part's stream extraction is re-run, not its fill; the attribute pass alone covers every other change. Fallback when the order cannot be kept: a channel source is forced at every inlet (a stream at every threshold), with a notice. | 2 (old question 9) |
| D6 | The przyrzecze of the downstream part, the direct area along the main river from the inlet down, comes from that part's own run; nothing is filled in later. In the network (ADR-080) the upstream part is an inflow node at the start of the reach and the przyrzecze its lateral element. | 1 |
| D7 | One database: `part_id` on runs, on the DEM-derived tables, land cover and soil; `publish_run` replaces only its part; one active run per part; graph edges across parts (the upstream part's outlet segment to the downstream inlet segment); delineation crosses parts and uses whole-part aggregates (dissolved outline, parameters) for an upstream part it holds whole; one VRT over all parts; the tiles merged (`tile-join`); one `instance.json` listing the parts. | 1 |
| D8 | Several basins in one instance: independent basins, each with its parts, share the database, the graph (one connected component or more per basin), the VRTs, the tiles and `instance.json`; Hydrograf accepts several project and set sources, each a basin. | 2 |
| D9 | Archiwista is unchanged at this stage: one project with the whole basin as its area and one closed set per basin, possible today; Hydrograf partitions the set. | 2 |
| D10 | The seam report's thresholds only warn; nothing blocks a publish. | 2 |
| D11 | Czechia: this stage is Hydrograf only, and T1 accepts the errors in the upper Bóbr. Continuity across the border is a later, separate plan (Follow-ups): Kartograf gets ZABAGED, the Czech counterpart of BDOT10k, and whatever else the analyses need (DMR 5G is already in Kartograf), then Hydrograf reads them. | 2 |
| D12 | Gauges are only a possible extension (Appendix): Hydrograf must eventually be free of IMGW-PIB's data ([the IMGW-PIB plan](2026-11-14-independence-from-imgw.md)) but must allow using such data. No step of this plan uses gauges, and the acceptance does not depend on them. | 2 |
| D13 | Branches and release: the work does not touch the planned release (candidate-5); code starts after `Approved:`, on Hydrograf's `feature/large-basins`, and merges into `develop` only after the first joint release, as an update. | 2 |
| D14 | T1 uses the scenario's harness, with GPT for the GUI tasks, Claude continuing where GPT hits its limit. | 2 |

Later, outside this plan's steps: the Odra's scale, with thresholds per part and the graph loaded by part.

## Design

### Parts (D1, D2)

1. A basin's closed set brings its area, the NMT sheets, the BDOT10k counties and the HSG raster; the PGW GeoPackage comes from `--units` beside the set, as today. Its JCWP (`zlewnie_jcwp_rzecznych`, `pozostale_obszary_jcwp`) are the units of ADR-071, and a part is a connected group of them, the domain of one run.
2. The partition grows parts from the basin's outlet up along the river network while the part's window stays within the budget, counted in grid cells of the window's rectangle at the part's cell size. It avoids cuts at reservoirs, lakes and confluences (D4) and keeps pond complexes and canal networks in one part. A part is named by the `MS_KOD` of its outlet JCWP; the partition (part → JCWP, the topological order) is a file of the basin, the same for one set, budget and cell size [proposed].
3. A part's window is its outline buffered by 1 km, as a rectangle on the lattice of the NMT sheets at the part's cell size; cells beyond the buffered outline are nodata. At the provisional budget of 90 M grid cells (Memory budget) and 42–61 % data per window, the Barycz and the Bóbr's Polish part need about 5–6 parts each at 5 m [INFERENCE]; at 1 m a part's window is at most 90 km².
4. Preparation: what works per cell (buildings, repaired holes) runs per window; what works along lines (the burning depth, ADR-072's smoothing, ADR-077's directions, lake outflows) runs once per basin on the vectors, with the DEM sampled along them, and is rasterized into every window, so both windows of a seam burn the same values [proposed: the answer to ADR-071's `:52`].
5. Fill and D8 per window, with the code of today's whole-grid fill (`fill_whole_grid`) and the window's edge as outlets.
6. Ownership: a cell belongs to a part when its D8 path in the part's window reaches an outlet of the part without passing an inlet of the part. A cell that two parts claim, or none (windows that disagree on a flat, a path that leaves the window), goes to the part whose JCWP holds its centre and is listed in the seam report, so every cell has one owner, as the tiles need; a D8 cycle across a seam is broken the same way [proposed].

### Cell size (D2, D3)

- The code is already resolution-agnostic within a run: thresholds are m² (`core/unit_hydrology.py:599`), the readers take the cell size from the raster (`core/cell_parameters.py:125-127`), so the graph's density per km² stays the same at 1 m. Every distance of this design is in metres (the buffer, the cut's distance from a confluence, the DEM check of D4, e.g. 50 m, ten cells at 5 m [to calibrate in H4]).
- Parts of one basin at different cell sizes need, beyond that: the partition counting each part's window at its own cell size; inlet records in coordinates and areas, each part placing the inlet on its own grid (D3); the seam report comparing two grids on the coarser one; one VRT per raster and cell size, or per part, and readers that find a point's part and its VRT; precise-mode and network windows that stop at a boundary between cell sizes and continue through the graph, as across a whole upstream part; `instance.json` and the GUI naming the cell size per part.
- Proposal: H3–H7 build one cell size per basin, keeping every key, record and file per part and the cell size on the part, so mixed sizes need no migration later; the readers' VRT per cell size and the windows stopping at a size boundary come as a later step (open question 2) [proposed].

### Memory budget (D2)

1. The budget counts the grid cells of the part's window, nodata included: the fill reads the whole window into one array (`core/unit_hydrology.py:211`, `core/raster_io.py:199`), and the fill, the D8 and the later stages allocate on the window.
2. What is known: Barycz 1's window of 188.6 M grid cells (111.0 M with data) completed under the 8 GB cap. Its logged peak of 8,064 MB was 98.4 % of the cap, and every other part's peak sat at about 98 % of its cap whatever its size. A peak at the cap measures the cap: the kernel reclaims file-mapped pages under it, so the need itself is unknown [INFERENCE of the report].
3. Measure once (H1): one small part of the scenario (Bóbr 2a, 108.9 M grid cells) on `939b55f` with a 12 GB cap and Hydroni stopped, logging the anonymous and the file-mapped memory per stage (the cgroup's `memory.stat` `anon` and `file`, or `RssAnon` and `RssFile`). The budget is then (8 GiB × 0.8 − the fixed part) ÷ the peak anonymous bytes per grid cell, a margin of 20 % [proposed].
4. Until it is measured, the budget is 90 M grid cells [INFERENCE]: under half of Barycz 1's 188.6 M grid cells that completed under 8 GB, and below every window of the scenario.

### Inlets (D4)

The inlet table comes from the vectors alone, once per basin and set and before any part runs, so both runs of a seam read the same point; each part places it on its own grid (D3). An inlet is the upstream part's outlet; the downstream run starts the river at the next cell down.

| Case | Inlet |
|---|---|
| The JCWP's main river | the burned BDOT10k watercourse with the JCWP's MPHP identifier, oriented by ADR-077 and the MPHP order; its intersection with the part boundary |
| Several intersections (meanders across the boundary, a line along it) | the last exit along the flow |
| A reservoir or lake on the cut | the lake's outflow, where the outflowing line leaves the OT_PTWP_A polygon |
| A cut less than 200–500 m from a confluence | the partition moves the cut (the JCWP on both sides into one part); where the budget forbids it, the inlet stays, flagged |
| Another burned watercourse crossing the boundary | an inlet of its own |
| An unburned ditch or canal crossing (OT_SWRM_L, OT_SWKN_L without an MPHP identifier) | none; the seam report lists it with the area it carries |
| The CZ border, at this stage (D11) | where the burned line reaches the border on the PL DEM; its upstream area unknown, its delineations marked `catchment_truncated` |

Each upstream run checks its inlets: its owned cell of the highest accumulation near each crossing lies within D4's N cells of the inlet, as a distance in metres (Cell size), else a warning in the seam report.

### Inlet record (D3, D5)

One record per inlet, written by the upstream part's run [proposed fields]:

| Field | Meaning |
|---|---|
| `inlet_id` | stable: basin, downstream part, kind, MPHP identifier, ordinal |
| `basin_id`, `upstream_part`, `downstream_part` | the basin and the parts' ids |
| `kind` | `main_river`, `watercourse`, `lake_outflow` or `border` |
| `x`, `y` | the inlet point, EPSG:2180; each part maps it to its own grid |
| `mphp_id`, `name`, `bdot_layer`, `bdot_id` | the BDOT10k line |
| `run_id`, `cell_size_m` | the upstream run that wrote the values, and its cell size |
| `upstream_area_m2` | the accumulation offset, in m², not cells |
| `longest_flow_path_m` | the longest flow path to the inlet (hydraulic length) |
| `distance_to_source_m` | along the main stream |
| `strahler_order` | per threshold |
| `segment_idx` | the upstream outlet segment, per threshold |
| `elevation_m` | the filled DEM at the inlet |
| `dem_check_m` | the distance of D4's check; a warning above it |
| `area_outside_data_km2` | border inlets: null at this stage (D11) |

### Order and attribute pass (D5)

1. The parts of a basin form a tree by their inlets; the runs go in its topological order, upstream first, one at a time under the cap. Each run reads the inlet records of the parts above it.
2. A run seeds each inlet with the record's upstream area as the initial value of its accumulation (pyflwdir's `accuflux` from initial values, or the offset added along the path in the routing on disk), so its streams, segments and sub-catchments are right at every threshold in the first run.
3. Re-running an upstream part: the attribute pass, upstream first, on every part below it. Along the D8 path from each inlet to the part's outlets it adds the change of the inlet's upstream area, takes the longer of the local and the inlet's longest flow path and distance to the source, and recomputes the Strahler order with the inlet's. It updates those rows (`upstream_area_km2`, `strahler_order`, the flow distances), the cells of those paths in the raster tiles and the stream tiles, and writes the part's own outlet records for the next part down. It touches one path per inlet (tens of kilometres, about 10⁴ cells at 5 m), not a raster: no fill, no D8.
4. When a secondary inlet's upstream area crosses a stream threshold, the pass re-runs the downstream part's stream extraction instead: from its kept `03_flowdir` and `04_flowacc` tiles (`scripts/process_dem_units.py:794-803`), with the new seed; no fill.
5. Fallback, when a downstream part runs before a part above it: every inlet without a record forces a channel source (a stream at every threshold) with a notice in the run's record and the seam report; when the upstream part arrives, the attribute pass corrects the attributes, and the stream extraction is re-run where the inlet's area lies below a threshold.

### One database (D7, D8)

- A basin registry: the basin's id and name, its project and set (their identity as `instance.json` records it today), its area, cell size, partition and parts.
- `basin_id` and `part_id` on `processing_runs` (the one-active index per part), on the DEM-derived `stream_network` rows, `stream_catchments`, `land_cover`, `soil_hsg`, `bdot_streams`, `depressions`, the sewer tables and every other table a bootstrap fills for its area (H3 makes the inventory; precipitation stays upserted by point).
- `publish_run` deletes and inserts its part's rows only, in one transaction; the imports delete by `part_id`, never by a box (the 466 m strip), and clip land cover and soil to the part's JCWP outline, so the parts' rows tile each basin; `clean` takes a basin or a part.
- `segment_idx` stays the key with `threshold_m2`, unique in the instance: each run takes the next free dense range per threshold at its start and records it, so the graph, the label tables (`core/network_delineation.py:899`), the MVT tiles, the API and `hydrolog-network/1` keep their key, and nothing public changes after the release [proposed]. A cross-part edge is the upstream outlet segment's `downstream_segment_idx`, set to the downstream inlet segment and re-linked at every publish of either part.
- Whole-part aggregates per part and outlet: the dissolved outline, the area, the elevation histogram, the slope, the land cover and soil group shares, the stream length. A delineation that reaches an upstream part's outlet takes its aggregate instead of its nodes, and continues through that part's inlets.
- The graph holds every basin, one or more components each, and loads when the API starts, not in the first request (E5b-01); loading it by part waits for the Odra.

### Rasters, tiles and the GUI (D7, D8)

- Every part writes its tiles on its lattice (the NMT sheets' lattice at its cell size); one VRT per raster lists the tiles of every part's active run of every basin and is rewritten (XML only) at each publish; a pointer names one run per part; a part's DEM mosaic and run go to `data/nmt/<basin>/<part>/`.
- MVT tiles: tippecanoe on the part's own rows, then `tile-join` into the instance's tiles; a re-run joins its part again.
- DEM tiles and overlays: only the tiles that a re-run part intersects, cut from the instance's VRT so the tiles at a seam or between two basins hold both, with one colour range per instance.
- `instance.json`: `area` names the instance; `basins` lists each basin (name, project, set, area, cell size, sources) with its `parts` (id, name, area, run, activation) [proposed: fields added within version 1, ECO-072].
- Frontend: the area label and the welcome text name the basins; the map fits their union, with a list that zooms to a basin.
- Admin panel: the basins, their parts, active runs and seam reports; a part's run started from its basin's project and set, one at a time.
- A delineation that holds a border inlet, or whose outline follows the edge of the data where flow enters, gets the notice `catchment_truncated` (`REPORT.md:273`) in the panel and in the hand-off; the missing area stays unknown at this stage (D11).

### Archiwista (D9)

Unchanged. One project per basin with the whole basin as its area, and one closed set with everything of the basin: for the Barycz, 1,213 NMT sheets at 5 m (with 1 m sheets where 5 m ones are missing, ADR-087), the BDOT10k counties of the frames and the HSG raster. Hydrograf takes each part's sheets and counties from the set by the part's window (ADR-067 and ADR-076 per window). Two basins are two projects and two sets, one source each (D8).

### Seam report (D1, D4, D10)

Written with every run, per pair of neighbouring parts and per basin (JSON, and a GeoPackage of crossings and disputed cells), and shown in the admin panel:

| Item | Content |
|---|---|
| Inlets | point, kind, DEM check, forced channel source (D5's fallback) |
| Crossing area | the area whose D8 crosses the JCWP boundary outside an inlet, per stretch of boundary and direction |
| Disputed area | cells that two parts claim, or none; cycles broken |
| Unburned crossings | ditches and canals, each with the area it carries |
| Warnings | over a threshold [to calibrate in H4; e.g. 0.1 % of the smaller part and 1 km² per boundary] |

A run over a threshold publishes with a warning, never blocked (D10); the remedy is the partition (JCWP moved between parts, a larger buffer), not a patch [proposed].

## Branches and release (D13)

- Nogat: this plan on the branch `plan/large-basins` (worktree `~/workspace/wt/nogat-large-basins`), not merged into `develop` until the author decides (DEV-3.3).
- Hydrograf: the branch `feature/large-basins` from `develop` `939b55f` (worktree `~/workspace/wt/hydrograf-large-basins`), pushed without code. Code starts only after this plan's `Approved:` line (DEV-17.4), under Hydrograf's `CLAUDE.md` (DEV-3.4); the H-steps' topic branches start from and merge into `feature/large-basins` [proposed], which takes `develop`'s later changes by merges.
- The work does not touch candidate-5 or the first joint release. `feature/large-basins` merges into Hydrograf's `develop` only after the first joint release (the author's decision), as an update, with the author's approval (DEV-3.3). After the release a released format changes only with the author's consent (ECO-072); the design only adds fields.

## Steps

Hydrograf only at this stage (D9, D11, D12); each step in its own session and branch under Hydrograf's `CLAUDE.md` (DEV-3.4, DEV-17.5); Hydrograf's ADR and plan carry its detail (DEV-17.2, DEV-17.4); bootstraps as user systemd units (DEV-17.6). Nothing starts before this plan's `Approved:` line.

| # | Project | Change | Depends on | Verified by |
|---|---|---|---|---|
| N1 | Nogat | this plan on `plan/large-basins`; after Hydrograf's merge, PROGRESS, and the registry only if an exchange changed | – | Nogat's gate |
| H1 | Hydrograf | the memory measurement, no code (Memory budget 3): Bóbr 2a on `939b55f` with a 12 GB cap, Hydroni stopped | this plan approved; open question 1 | the budget in grid cells with its margin, for H2's ADR |
| H2 | Hydrograf | an ADR amending ADR-071 and ADR-067 (parts, inlets, topological order, one database for several basins, a source per basin) and noting ADR-080's network across parts; Hydrograf's plan | H1 | the author's review |
| H3 | Hydrograf | the database and the stores: the basin registry, `basin_id` and `part_id` on runs and on every table a bootstrap fills, one active run per part; `publish_run`, land cover, soil, `bdot_streams`, depressions, the sewer and `clean` by part; the instance-wide segment numbers; a directory and pointer per part; the bootstrap's source per basin and part (`--project`, `--set`, a part) | H2 | a part of the Barycz and a part of the Bóbr in one database: each publish leaves the other's rows and files unchanged (E7-08 closed), the 466 m strip included |
| H4 | Hydrograf | the partition (the budget in grid cells at the part's cell size), the windows, the preparation along lines, ownership by D8, the inlet table with its cases, the seam report with its warnings | H3 | synthetic DEMs for each case of the inlet table; the Orla in three parts and its seam report |
| H5 | Hydrograf | inlet records, the topological order, the seed at the inlets, the attribute pass, the re-run of the stream extraction at a threshold, the forced-channel fallback with its notice | H4 | synthetic DEMs: the parts equal the whole run; an upstream re-run changes only attributes, or re-runs only the extraction below a secondary inlet that crossed a threshold; the fallback's notice |
| H6 | Hydrograf | the graph across parts and basins, loaded at start; delineation across parts with whole-part aggregates; precise-mode and network windows across a seam | H5 | the Orla: whole run against parts (Acceptance 1); windows across a seam |
| H7 | Hydrograf | the VRTs over every part, per-part MVT export and `tile-join`, DEM tiles and overlays per part; `instance.json` with `basins` and `parts`; the map, the area label and the welcome text for several basins; the admin panel's basins, parts, runs and seam reports; `catchment_truncated` | H3, H6 | two basins in one instance in the GUI; MVT and DEM tiles continuous across a seam; `instance.json` |
| T1 | e2e | the Acceptance on the Barycz and the Bóbr in one instance, from two Archiwista projects and two closed sets, with the scenario's harness (below) | H1–H7 | Acceptance |

T1's harness: copies of `~/workspace/_e2e/2026-11-15/scenario/E7/run_part.sh`, which runs one bootstrap with its memory sampling and starts the instance after it, and `E7/chain_parts.sh`, which chains the runs behind a free-memory gate. Both are adapted to one shared instance, the topological order of each basin and the 8 GB cap. `E6/run_gpt.sh` gives the GUI tasks to GPT, even when it hits its usage limit (`LIMIT_HIT` in its log); Claude then continues the task and the report notes the switch. The errors in the upper Bóbr, beyond the Czech border, are accepted (D11).

## Acceptance

1. Equivalence: the Orla (Barycz 2, 1,599.3 km², 75.7 M valid cells), run whole as in the scenario and in three parts, has the same D8 on every cell outside the seam report's disputed cells, and the upstream areas of its nodes at the 1 km² threshold agree within ±0.5 %. Re-running an upstream part changes only attributes downstream, or re-runs only the stream extraction below a secondary inlet whose area crossed a threshold (D5).
2. Order: every part runs after the parts above it; the fallback, forced on one synthetic case, leaves its notice and is corrected when the upstream part arrives.
3. Seams: every boundary has its report in JSON, GeoPackage and the admin panel; a seam over a threshold publishes with a warning, and T1 lists every warning with its areas.
4. Memory: every part's window is within the budget in grid cells, every run stays under the 8 GB cap, and the anonymous and file-mapped memory is logged per stage.
5. Two basins in one instance: the Barycz and the Bóbr from two projects and two closed sets; a part's bootstrap leaves the other parts' and the other basin's rows, files and tiles unchanged (counts and checksums per part before and after); the GUI shows both basins, and the admin panel lists both with their parts.
6. Continuity: a delineation at each basin's mouth crosses all its parts, and its area agrees with the basin's JCWP outline (the Barycz 5,543.2 km², the Bóbr's Polish part 5,649.4 km²) within ±1 % [to calibrate in H4]; a delineation in the upper Bóbr that holds the border inlet carries `catchment_truncated`, and its missing Czech area is an accepted error (D11).
7. Optional diagnostic, not a criterion: the delineated areas at the IMGW-PIB gauges of the two basins against the catalog's areas (Appendix).

## Risks and open questions

Risks:

- Seams in flat land: ADR-071 met closed basins wider than a 16 km halo, so a 1 km buffer leaves disputed area, and its size decides whether D1 holds [INFERENCE].
- The Barycz's fish ponds and canals: bifurcations and canals across divides that D8 cannot split; their unburned crossings are only reported.
- Reservoirs on the Bóbr and the Kwisa (Bukówka, Pilchowice, Leśna) on JCWP boundaries: the lake-outflow rule, or parts that keep each reservoir whole.
- Memory: the budget stays provisional until H1 measures the need.
- The preparation along lines is new code; where it differs from today's whole-DEM smoothing, the windows of a seam disagree where streams enter.
- 1 m: 25 times the cells of 5 m, so about 25 times the bootstrap time per km² (the Barycz 3–4 days at the scenario's 1.84–2.36 s/km²) [INFERENCE: linear in cells]; a 90 km² window keeps less than two thirds of its area inside its 1 km buffer, and the seams multiply.
- The graph of both basins (806,916 nodes in the scenario's 7 parts) in one API process, loaded at start: its memory is unmeasured.
- The Odra (~119,000 km²): at most 2,250 km² per window at 5 m means at least 53 parts; the measured 72 graph nodes per km² give about 8.6 M nodes, and 6.3 MiB per km² of data, tiles and database (`REPORT.md:96`, `:373-382`) about 0.7 TiB [INFERENCE: linear].

Open questions for the author:

1. H1: may the measurement stop Hydroni for about an hour (one part with a 12 GB cap), or should the provisional budget of 90 M grid cells stand without it?
2. Mixed cell sizes within one basin: built in this plan's steps, or kept possible by the keys and records (Cell size) and built later?
3. Formats after the release: the instance-wide segment numbers keep the API, the tiles and `hydrolog-network/1` as they are, and `instance.json` gains `basins` beside `area`; may these additions stay version 1 (ECO-072)?

## Follow-ups (outside this plan's steps)

- Czechia (D11), a separate plan, owners Kartograf then Hydrograf. Kartograf: ZABAGED, the Czech counterpart of BDOT10k, and whatever else the analyses need across the border, e.g. catchment polygons, which only DIBAVOD A07 outside Kartograf gave (GEO-06); DMR 5G is already in Kartograf. Hydrograf: the CZ DEM in the set reader (GEO-01; today only `nmt/pl_1992_<resolution>_evrf2007`, `utils/kartograf_set.py:77`), the Czech lines in burning and inlets, and the border inlet replaced by continuity, so that Błażkowa and Żagań get their whole catchments. These were the first draft's K1 and H8.
- Archiwista: nothing for this plan (D9). E7-01's area change accepted under a closed set is Archiwista's own finding; a set that pins the PGW GeoPackage only if `--units` beside the set proves insufficient.
- The Odra's scale: thresholds per part, the graph loaded by part.
- Mixed cell sizes within a basin, if open question 2 keeps them out of the steps.

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
