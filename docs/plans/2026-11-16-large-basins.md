# Plan: large basins in one Hydrograf instance, with gauges as control and analysis segments

Approved: pending

Status: a draft written on 2026-11-16 from the scenario test of 2026-11-15/16 and the author's discussion of 2026-11-16; not approved, so no code starts (DEV-17.4). The decisions are the author's; their column „To confirm” marks what the author still has to confirm, and the design marks its own proposals „[proposed]”.

Requirements: HUB-5.2 (producers before consumers), DEV-17.4, DEV-17.5 and DEV-3.4 (each project in its own session), DEV-17.2 (Hydrograf records its decisions as ADRs), DEV-17.6 and ECO-073 (bootstraps run as user systemd units), ECO-054 (the project and its set are Archiwista's), ECO-059 (station series and catalogs from Obserwator, analyses by Hydrolog), ECO-072 (`hydrolog-network/1` and every other format stay version 1).

## Goal

One Hydrograf instance serves a whole large basin, the Barycz (5,543.2 km²) or the Bóbr (5,881.8 km², 232.4 km² of it in Czechia) and later the Odra, with continuous data: one address, one database, delineation and parameters across the whole basin, computed in parts that each fit the host's memory. Gauges check every bootstrap against their published catchment areas and, on very large rivers, divide the analysis into reaches between gauges, whose differential catchments Hydrolog balances with Obserwator's observed series.

## Facts

Source: the scenario test of 2026-11-15/16 on the Barycz and the Bóbr, report `~/workspace/_e2e/2026-11-15/scenario/REPORT.md` (in Polish, cited as `REPORT.md:<line>`) and the coordinator's findings `COORD-FINDINGS.md` beside it. Hydrograf's code at `develop` `939b55f` (the member of candidate-5; code paths under `backend/`).

### The scenario test

- **No second part in one instance** (E7-08, `REPORT.md:148`, `COORD-FINDINGS.md:8`): a second bootstrap into an instance replaces the first part, mixes land cover and soils, and gets no inflow from the part above. The workaround was one instance and one address per part: 7 instances for two basins, 7 databases of 9,509 MiB together (`REPORT.md:96`, `:254`).
- **Truncated catchments look complete** (G07-2 = G09-2/3, `REPORT.md:150`): Błażkowa 13.46 km² (IMGW-PIB 103.54), Kamienna Góra 89.33 (189.84), Osetno 597.06 (4,574.72), Żagań 56.22 (4,258.38), Łozy 799.91 (898.71), each shown without a warning.
- **Memory** (E7-09, `REPORT.md:87-97`, `:117-127`, `:162`): Barycz 1 (2,393.3 km²) has 110,985,971 valid cells on a 188.6 M-cell grid; step 3 took 2,467.8 s and the bootstrap 5,631.4 s (21:53–23:27), with peaks of 8,003 MB (polygonize_subcatchments), 8,064 MB (secondary_rasters) and 8,045 MB (publish) under an 8 GB cap (log `/data/nmt/e2e-2026-11-15/logs/hydrograf-barycz-bootstrap-run-20261115-215308.log:154-155`, `:203`, `:212`). Every part peaked at 7,618–9,065 MB, about 98 % of its 8 or 9 GB cap whatever its size (Bóbr 2a, 50.4 M valid cells, 8,147 MB), so the logged peak is bounded by the cap, not by the need [INFERENCE of the report]; `docker stats` sampled 6,830–7,495 MiB. Bóbr 2 PL (296.7 M grid cells) did not fit 9 GB and was split along JCWP into 2a (108.9 M) and 2b (135.0 M).
- **Time** (`REPORT.md:37`, `:96`, `:101-102`, `:134`): the 7 bootstraps took 24,024.5 s (6 h 40 min), 1.84–2.36 s/km²; the longest steps are step 3, the NMT (685–2,468 s), and step 8, the MVT tiles (756–2,093 s). The chain of five parts ran 00:10:52–05:08:06, one at a time behind a gate of 9,500 MB free memory.
- **Whole basins on the 5 m grid**, computed for this plan from the scenario's sheet lists (`/data/nmt/e2e-2026-11-15/geo/sheets/`, frames by Kartograf's `SheetParser.get_bbox`; Barycz 1's frames give the logged 188.6 M): the Barycz has 1,213 sheets, 24,578 × 15,288 = 375.7 M cells (93.9 M at 10 m), of which 221.7 M valid; the Bóbr's Polish part 1,297 sheets, 17,643 × 32,123 = 566.7 M cells (141.7 M at 10 m), of which 226.0 M valid.
- **One area per Archiwista project** (E7-01, `REPORT.md:151`): `AreaChoice` holds one area (`src/archiwista/api/models.py:3177`, `800231c`), and changing it under a closed set returns 200; the workaround was 8 projects, one per part.
- **Gauges** (`REPORT.md:14`, `:277`): in Barycz 1 the precomputed delineation differs from IMGW-PIB's area by +0.25 % (Odolanów, 159.53 against 159.13 km²), +0.17 % (Kanclerzowice) and +0.74 % (Łąki, 1,760.71 against 1,747.85); in the other parts by −3.65 % at Korzeńsko (the click snapped 0.7 km away) and +5.88 % at Rydzyna, unexplained. The precise mode at a gauge's catalog coordinates, 5–10 m off the stream, returns 0.0003 km² (E5b-03, `REPORT.md:187`). The two basins hold 42 IMGW-PIB hydrological gauges with an area: 10 on the Barycz, 32 on the Bóbr (`/data/nmt/e2e-2026-11-15/geo/stacje_barycz_bobr.csv`).
- **Station catalog** (GEO-03, GEO-04, `REPORT.md:176`, `:208`): 2,140 of IMGW-PIB's 3,808 stations have no location (`/data/nmt/e2e-2026-11-15/geo/raw/stations/catalog-IMGW-PIB.json`; 2,143 of 3,811 in E3, every key station located), partly because the static source `python -m obserwator.reference_data` was skipped; live `stations find` gives a 2-digit `hydrographic_code` and no coordinates.
- **Czechia** (GEO-01, GEO-06, `REPORT.md:149`, `:204`): Hydrograf reads no CZ DEM, so the Bóbr's 232.4 km² in Czechia are outside the model and Błażkowa lacks 87 % of its area without a message. Kartograf has no source of CZ catchment polygons (DIBAVOD A07 was used outside it); CZ watercourse lines are in Kartograf as HY-NET (`hydro download --product network --country cz`, `src/kartograf/catalog/commands/hydro.py:1` at `e14bc78`), which Hydrograf does not read.
- **Network window** (E5b-10, `REPORT.md:191`): a network closing at Łąki is refused, `network_window_too_large`, 135,118,485 cells over 60 M (`/data/nmt/e2e-2026-11-15/e5b/network/laki-window.json`).

### Hydrograf at `939b55f`

- **One run per instance.** The unique index `idx_processing_runs_one_active` allows one active run (`migrations/versions/005_processing_runs.py:68-72`); `publish_run` (`core/unit_run_store.py:516`) deletes every DEM-derived `stream_network` row and every `stream_catchments` row (`:600`, `:603`).
- **Area-wide replacements elsewhere.** The DEM mosaic is always `data/nmt/dem_mosaic.vrt` (`scripts/bootstrap.py:581`); soil groups are deleted by the area's envelope (`scripts/bootstrap.py:886`), land cover by the import's extent (`scripts/import_landcover.py:728`; the whole table with `--clear-existing`, `:792`), `bdot_streams` entirely (`core/db_bulk.py:485`), depressions entirely with `--clear-existing` (`scripts/generate_depressions.py:839`).
- **ADR-071 and its amendment** (`docs/decisions/0071-pgw-units-and-boundary-event-routing.md`): PGW units own the outputs (tiles, records, resume), not the computation. Fills per unit window never agreed on the seams at 5 m (closed basins wider than any halo, flats broken differently by each window; the halo grew from 500 m to 16 km, `:65`), so the fill and D8 run once on the whole grid at about 18 B per cell, and „a larger area needs the fill itself to change, not windows” (`:71`). Burning, smoothing, buildings and lakes run on the whole DEM too: a window changed 37 cells by up to 5.2 m where a stream enters it (`:52`).
- **Units.** A PGW polygon owns the cells whose centre it holds, and a cell outside every polygon goes to the nearest owner (`core/unit_ownership.py:284`); the layers are `zlewnie_jcwp_rzecznych` and `pozostale_obszary_jcwp` (`:34-35`), from a `--units` file beside the set (`scripts/bootstrap.py:1695-1705`).
- **Rasters.** Per-owner tiles and one VRT per raster, every valid cell in exactly one tile, verified before anything is replaced (`core/unit_rasters.py:24-26`, `write_unit_mosaics` at `:550`); the API reads the VRTs of the run that `active_run.json` names (`core/active_run.py:3-7`, `:121-140`).
- **Graph.** In memory, keyed by `(threshold_m2, segment_idx)` (`core/catchment_graph.py:156-157`) and loaded from the whole `stream_catchments` (`:225-233`); its docstring sizes it at ~87k nodes (`:114`), Barycz 1 had 163,750 and the 7 parts 806,916 (`REPORT.md:96`). It loads lazily in the first request, about 6 min beside a bootstrap (E5b-01, `REPORT.md:165`).
- **Limits.** Precise-mode windows up to 40 M cells (`core/raster_service.py:42`), network windows up to 60 M (`core/network_delineation.py:115`), hydrographs up to 250 km² (SCS-CN, `core/constants.py:19`).
- **Burning and accumulation.** `dem.stream_burning: main` (default `all`, `core/config.py:353`) burns the OT_SWRS_L main courses that are rivers or carry `IDENTYFIKATORMPHP`, the OT_SWKN_L that carry it, and no OT_SWRM_L (`core/hydrology.py:367-388`); each MPHP watercourse is oriented towards its mouth (ADR-077, `_mouth_directions`, `core/hydrology.py:802`). Accumulation is `flw.upstream_area(unit="cell")` (`core/hydrology.py:2243`); pyflwdir's `accuflux(data)` accumulates from initial values.
- **Resolution.** A set's NMT comes at `1m` or `5m` (`utils/kartograf_set.py:72`), from `nmt/pl_1992_<resolution>_evrf2007` only (`:77`); finer sheets are averaged onto the run's lattice (`gdalwarp -r average`, `scripts/bootstrap.py:576`; ADR-087, `docs/decisions/0087-a-sheet-missing-at-the-run-resolution-from-a-finer-nmt-of-the-set.md:18-20`).
- **Network method** (ADR-080, `docs/decisions/0080-network-delineation-at-control-points.md:136-143`, `:164-166`): control points, reaches, the przyrzecze as an element that enters the junction below it unrouted, and `hydrolog-network/1` to Hydrolog.
- **Instance and tiles.** `frontend/data/instance.json` names one area and one set (`scripts/write_instance_info.py:311-329`); MVT tiles come from tippecanoe (`scripts/generate_tiles.py:121`).

### Producers and earlier work

- Obserwator (`develop` `f4f6a8d`): the catalog's station properties include `river`, `hydrographic_code`, `river_km` and `catchment_area_km2`, with a location uncertainty of at least 150 m (`src/obserwator/store/catalog.py:130-158`); the area comes from hydro.imgw.pl's details of IMGW-PIB hydrological stations only (`:163-169`, `:805`), so ČHMÚ gauges have none.
- Hydrolog (`develop` `d82982a`): `route network` already takes given discharges for a subcatchment, inline or as a column of `inflows_file` (`src/hydrolog/operations/_network_input.py:27-32`).
- Decision D3 of [the Hydroni plan](2026-11-06-hydroni-instance.md) processed units in windows with an upstream-first hand-off; ADR-071's amendment replaced that with the whole-grid fill. This plan returns to fills per window, for parts much larger than units, and accepts a measured seam instead of an exact one.

## Options

| Option | Continuity | Memory | Detail | Decision |
|---|---|---|---|---|
| A. Closed JCWP parts joined at BDOT10k inlets, in one instance | whole basin, through the inlets; the seam measured, not exact | bounded by the largest part (~110 M valid cells) | 5 m | chosen |
| B. The whole basin in one run at 10 m | whole basin, exact | the Barycz has 93.9 M grid cells (55.4 M valid) at 10 m, half of Barycz 1's grid, which peaked at 8 GB [INFERENCE: fits]; the Bóbr's Polish part 141.7 M (56.5 M valid) | 10 m: small catchments coarser; needs a target cell coarser than the source | interim; the author has not decided |
| C. A bigger machine, the whole basin at 5 m in one run | whole basin, exact | the Barycz's 375.7 M cells need about 6.8 GB for the fill alone (18 B per cell) and about twice Barycz 1's cap for the later stages [INFERENCE]; the Odra out of reach | 5 m | rejected |
| D. Exact tiled algorithms (parallel priority-flood, TauDEM with MPI) | whole basin, exact | bounded by the tile | 5 m | rejected: a second fill whose flats must agree with pyflwdir's, what failed in ADR-071 (`:65`), and a rewrite of the pipeline |
| E. A coarse 25 m pre-pass for the divides of the parts | whole basin | small pre-pass | 5 m | rejected by the author: the JCWP divides are the reference |
| F. One instance per part (today's workaround) | none: truncated catchments without a warning | per part | 5 m | rejected: 7 addresses and 7 databases for two basins (E7-08) |

## Decisions (the author, 2026-11-16)

| # | Decision | To confirm |
|---|---|---|
| D1 | Parts are aggregates of whole JCWP from Kartograf's PGW GeoPackage, cut along their boundaries, without a coarse pre-pass: the JCWP divides are the reference. Each part stays under a cell budget (~110 M cells at 5 m, Barycz 1's measured 8 GB) and is processed with a ~1 km buffer; a cell belongs to the part its D8 flow reaches within the buffered window, and a seam report measures the area that drains across a JCWP boundary outside the inlets. | the budget's measure (valid or grid cells) and its cap (8 or 9 GB) |
| D2 | Inlets and outlets come from BDOT10k lines. The intersection of the JCWP's burned main river (chosen by its MPHP identifier and oriented by ADR-077 and the MPHP order, never by its vertices) with the JCWP boundary, rasterized on the common 5 m PL-1992 grid, is the same cell in both parts' runs whatever their fills. At a reservoir or lake on the cut the inlet is the lake's outflow (better: no cut at a reservoir); cuts lie at least 200–500 m from tributary confluences; other burned watercourses crossing a boundary are further inlets; unburned ditches and canals enter only the seam report; a line running along the boundary gives its last exit along the flow. DEM check: the upstream part's owned cell of the highest accumulation lies within N cells (e.g. 10) of the inlet, else a warning. | N, and 200 or 500 m |
| D3 | A part's geometry and topology do not depend on the order of the runs: parts run in any order, or in parallel where memory allows. What depends on the upstream area (the accumulation offset at the inlets, the longest flow path and hydraulic length, the Strahler order, the distance to the source) comes from the upstream part's inlet record and is applied upstream first in a cheap attribute pass. Re-running an upstream part rebuilds no downstream network, only attributes, because the main river exceeds every threshold at the inlet. | the last sentence is an inference; the equivalence test confirms it |
| D4 | The przyrzecze of the downstream part, the direct area along the main river from the inlet down, comes from that part's own run; nothing is filled in later. In the network (ADR-080) the upstream part is an inflow node at the start of the reach and the przyrzecze its lateral element. | – |
| D5 | One database: `part_id` on runs, on the DEM-derived tables, land cover and soil; `publish_run` replaces only its part; one active run per part; graph edges across parts (the upstream part's outlet segment to the downstream inlet segment); delineation crosses parts and uses whole-part aggregates (dissolved outline, parameters) for an upstream part it holds whole; one VRT over all parts; the tiles merged (`tile-join`); one `instance.json` listing the parts. | – |
| D6 | Archiwista: one project and one closed set for the whole basin, which ends the project-per-part workaround of E7-01; Hydrograf partitions the set itself. | – |
| D7 | Gauges as control: after every bootstrap each gauge of the part is delineated from the graph and compared with its IMGW-PIB (or ČHMÚ) area within a tolerance by size (e.g. ±2 % above 1,000 km², ±5 % at 100–1,000, ±10 % below 100); those areas are a reference, not the truth. One table per instance; the GUI shows the model's and the gauge's area and warns when a catchment lies partly outside the data (Błażkowa: 13.5 of 103.5 km²). This needs gauges snapped to the burned BDOT10k line of the named river (radius ~300 m, the river km as a second hint) and complete gauge locations from Obserwator. | the tolerances, to calibrate |
| D8 | Gauges as analysis segments on very large rivers (the Odra): the reach between two gauges has a differential catchment, a graph query, and the processing parts need not match the gauges. A Hydrograf network with control points at the main river's gauges and the tributaries' mouths goes to Hydrolog, which routes the observed upstream hydrograph (Obserwator's series) through the reach, adds the tributaries (observed where gauged, SCS-CN up to 250 km² only where not) and the przyrzecze, compares the result with the downstream gauge, and balances the differential catchment for calibration. | – |
| D9 | Tributaries that fit whole: their gauges are control points too, compared with the series and with Hydrolog's Q1% quantiles. | – |
| D10 | Czechia: GEO-01 (a CZ DEM in Hydrograf) and GEO-06 (in Kartograf) come before continuity across the border; until then the border inlet is set from the DEM. | what GEO-06 must deliver (open question 3) |

Not decided: the interim whole-basin run at 10 m (option B). Later, outside this plan's steps: the Odra's scale, with thresholds per part and the graph loaded by part.

## Design

### Parts (D1)

1. The basin's closed set (D6) brings the PGW GeoPackage of its area. Its JCWP (`zlewnie_jcwp_rzecznych`, `pozostale_obszary_jcwp`) are the units of ADR-071, and a part is a connected group of them, the domain of one run. The Barycz needs at least three parts (221.7 M valid cells), the Bóbr at least three (226.0 M valid cells in Poland, 9.3 M in Czechia).
2. The partition grows parts from the outlet up along the river network until the budget, avoids cuts at reservoirs, lakes and confluences (D2), and keeps pond complexes and canal networks in one part. A part is named by the `MS_KOD` of its outlet JCWP; the partition (part → JCWP) is a file of the instance, the same for one set and budget [proposed].
3. A part's window is its outline buffered by 1 km, as a rectangle on the 5 m PL-1992 lattice of the NMT sheets; cells beyond the buffered outline are nodata [proposed].
4. Preparation: what works per cell (buildings, repaired holes) runs per window; what works along lines (the burning depth, ADR-072's smoothing, ADR-077's directions, lake outflows) runs once per basin on the vectors, with the DEM sampled along them, and is rasterized into every window, so both windows of a seam burn the same values [proposed: the answer to ADR-071's `:52`].
5. Fill and D8 per window, with the code of today's whole-grid fill (`fill_whole_grid`) and the window's edge as outlets.
6. Ownership: a cell belongs to a part when its D8 path in the part's window reaches an outlet of the part without passing an inlet of the part. A cell that two parts claim, or none (windows that disagree on a flat, a path that leaves the window), goes to the part whose JCWP holds its centre and is listed in the seam report, so every cell has one owner, as the tiles need; a D8 cycle across a seam is broken the same way [proposed].

### Inlets (D2)

The inlet table comes from the vectors alone, once per basin and set and before any part runs, so both runs of a seam read the same cells. An inlet cell is the upstream part's outlet; the downstream run starts the river at the next cell down.

| Case | Inlet |
|---|---|
| The JCWP's main river | the burned BDOT10k watercourse with the JCWP's MPHP identifier, oriented by ADR-077 and the MPHP order; the cell of the common lattice that holds its intersection with the part boundary |
| Several intersections (meanders across the boundary, a line along it) | the last exit along the flow |
| A reservoir or lake on the cut | the lake's outflow, where the outflowing line leaves the OT_PTWP_A polygon |
| A cut less than 200–500 m from a confluence | the partition moves the cut (the JCWP on both sides into one part); where the budget forbids it, the inlet stays, flagged |
| Another burned watercourse crossing the boundary | an inlet of its own |
| An unburned ditch or canal crossing (OT_SWRM_L, OT_SWKN_L without an MPHP identifier) | none; the seam report lists it with the area it carries |
| The CZ border, before H8 | the cell where the burned line reaches the border on the PL DEM; its upstream area unknown |

Each upstream run checks its inlets: its owned cell of the highest accumulation near each crossing lies within N cells (10) of the inlet cell, else a warning in the seam report.

### Inlet record (D3)

One record per inlet, written by the upstream part's run [proposed fields]:

| Field | Meaning |
|---|---|
| `inlet_id` | stable: downstream part, kind, MPHP identifier, ordinal |
| `upstream_part`, `downstream_part` | the parts' ids |
| `kind` | `main_river`, `watercourse`, `lake_outflow` or `border` |
| `row`, `col`, `x`, `y` | the inlet cell on the basin's lattice, EPSG:2180 |
| `mphp_id`, `name`, `bdot_layer`, `bdot_id` | the BDOT10k line |
| `run_id` | the upstream run that wrote the values |
| `upstream_cells`, `upstream_area_km2` | the accumulation offset |
| `longest_flow_path_m` | the longest flow path to the inlet (hydraulic length) |
| `distance_to_source_m` | along the main stream |
| `strahler_order` | per threshold |
| `segment_idx` | the upstream outlet segment, per threshold |
| `elevation_m` | the filled DEM at the inlet |
| `dem_check_cells` | the distance of D2's check; a warning above N |
| `area_outside_data_km2` | border inlets: the area beyond the data where known (GEO-06), else null |

### Attribute pass (D3)

1. A run seeds each of its inlets with an accumulation above the largest threshold (the PGW area above it as the estimate), so its streams, segments and sub-catchments need no other run.
2. When a run is published, every part below it gets the attribute pass, upstream first. Along the D8 path from each inlet to the part's outlets the pass adds the inlet's upstream area, takes the longer of the local and the inlet's longest flow path and distance to the source, and recomputes the Strahler order with the inlet's; it updates those rows (`upstream_area_km2`, `strahler_order`, the flow distances), the cells of those paths in the raster tiles and the stream tiles, and writes the part's own outlet records for the next part down.
3. The pass touches one path per inlet (tens of kilometres, about 10⁴ cells), not a raster: no fill, no D8.
4. A small watercourse's inlet whose upstream area crosses a threshold changes the network at that threshold: the pass marks the downstream part for a re-run instead of patching it [proposed].

### One database (D5)

- `part_id` on `processing_runs` (the one-active index per part), on the DEM-derived `stream_network` rows, `stream_catchments`, `land_cover`, `soil_hsg`, `bdot_streams`, `depressions` and every other table a bootstrap fills for its area (H2 makes the inventory).
- `publish_run` deletes and inserts its part's rows only, in one transaction; the imports delete by `part_id`, not by envelopes, and clip land cover and soil to the part's JCWP outline, so the parts' rows tile the basin.
- Keys `(part_id, threshold_m2, segment_idx)`; a cross-part edge is `downstream_part_id` and `downstream_segment_idx` on the upstream outlet segment of each threshold; responses that carry `segment_idx` gain `part_id` [proposed; H5 checks the consumers].
- Whole-part aggregates per part and outlet: the dissolved outline, the area, the elevation histogram, the slope, the land cover and soil group shares, the stream length. A delineation that reaches an upstream part's outlet takes its aggregate instead of its nodes, and continues through that part's inlets.
- The graph loads every part when the API starts, not in the first request (E5b-01); loading it by part waits for the Odra.

### Rasters, tiles and `instance.json` (D5)

- Every part writes its tiles on the basin's lattice; one VRT per raster lists the tiles of every part's active run and is rewritten (XML only) at each publish; `active_run.json` names one run per part; a part's DEM mosaic goes to `data/nmt/parts/<part>/`.
- MVT tiles: tippecanoe per part, then `tile-join` into the instance's tiles; a re-run joins its part again.
- `instance.json` keeps the basin as its area and lists `parts` (id, name, area, run, activation, set).

### Archiwista (D6)

One project per basin and one closed set with everything of the basin: for the Barycz, 1,213 NMT sheets at 5 m (with 1 m sheets where 5 m ones are missing, ADR-087), the BDOT10k counties of the frames, the HSG raster and the PGW GeoPackage. Hydrograf takes each part's sheets from the set by its window (ADR-067 and ADR-076 per window). Until a set can pin the PGW GeoPackage, Hydrograf reads it from `--units` beside the set (A1 finds out).

### Seam report (D1, D2)

Written with every run, per pair of neighbouring parts and for the instance (JSON, and a GeoPackage of crossings and disputed cells), and shown in the admin panel:

| Item | Content |
|---|---|
| Inlets | cell, kind, DEM check |
| Crossing area | the area whose D8 crosses the JCWP boundary outside an inlet, per stretch of boundary and direction |
| Disputed area | cells that two parts claim, or none; cycles broken |
| Unburned crossings | ditches and canals, each with the area it carries |
| Status | under or over the threshold [to calibrate; e.g. at most 0.1 % of the smaller part and 1 km² per boundary] |

A run over the threshold publishes with a warning; the remedy is the partition (JCWP moved between parts, a larger buffer), not a patch [proposed].

### Gauge control (D7, D9)

1. Gauges: Obserwator's catalog of the IMGW-PIB and ČHMÚ hydrological stations of the basin (code, name, river, river km, MPHP code, catchment area, location and its uncertainty), read from a file export rather than through the library, which the draft [IMGW-PIB plan](2026-11-14-independence-from-imgw.md) drops from Hydrograf (its HG1) [proposed; H7 settles the exchange].
2. Snapping: to the burned BDOT10k line of the named river (by name, or by MPHP code where the catalog has it) within ~300 m; among several candidates the river km (the distance up the oriented watercourse from its mouth) decides; no candidate means `not_snapped`.
3. Delineation from the graph at the finest threshold (10,000 m²), across parts, never by the precise mode at the catalog point (E5b-03).
4. Comparison: |model − reference| / reference within ±2 % above 1,000 km², ±5 % at 100–1,000 km², ±10 % below 100 km² [to calibrate]. Statuses `ok`, `outside_tolerance`, `partly_outside_data`, `not_snapped`, `no_reference`. A gauge outside its tolerance is a lead for review (Korzeńsko, Rydzyna), not a failed run [proposed].
5. After every bootstrap and attribute pass: the gauges of the part and every gauge below it; one table per instance (JSON, CSV, the admin panel).
6. Tributaries that fit whole (D9): their gauges are control points; Hydrolog compares the modelled hydrograph with the gauge's series and its Q1% from Obserwator's analyses (ECO-059).

### Differential catchments (D4, D8)

1. Hydrograf: a reach of a large river between gauges G1 and G2. Its differential catchment is a graph query, the nodes above G2 that are not above G1, across parts and with whole-part aggregates; no raster window (a network at Łąki already needs 135 M cells).
2. Hydrograf: the network (ADR-080) with control points at G1, G2, the tributaries' mouths and the tributary gauges. G1 is an inflow node at the start of the reach, a gauged tributary an observed inflow node, an ungauged tributary up to 250 km² an SCS-CN subcatchment, each przyrzecze a lateral element. Elements beyond the 60 M-cell window come from the graph (an amendment of ADR-080) [proposed].
3. Hand-off: `hydrolog-network/1` in which each observed node names its station (provider and code), fields added within version 1 (ECO-072).
4. Hydrolog: the observed series from Obserwator (`hydrolog-series/1` or `obserwator-series-csv`, ECO-059) as the given discharges of those nodes; it routes G1 through the reach, adds the tributaries and the przyrzecze, compares the outflow with G2's series (volume, peak, timing), and balances the differential catchment (G2 less G1 and the gauged tributaries, against the modelled ungauged area) for calibration.

### GUI (D7)

- A delineation whose outlet is a snapped gauge shows the model's area, the gauge's area, the difference and the status.
- A delineation that holds a border inlet without upstream data, or whose outline follows the edge of the data where flow enters, gets the notice `catchment_truncated` (`REPORT.md:273`) with the missing area where known (a GEO-06 polygon, the gauge's area), in the panel and in the hand-off.
- The admin panel shows the seam report and the gauge table per part.

## Steps

Producers first (HUB-5.2); each project in its own session and branch under its own `CLAUDE.md` (DEV-3.4, DEV-17.5); Hydrograf's ADR and plan carry its detail (DEV-17.2, DEV-17.4); merges with the author's approval (DEV-3.3); bootstraps as user systemd units (DEV-17.6). Nothing starts before this plan's `Approved:` line.

| # | Project | Change | Depends on | Verified by |
|---|---|---|---|---|
| N1 | Nogat | this plan; once H7 and L1 settle their exchanges, the registry's edges (Hydrograf reads Obserwator's station catalog, Hydrolog reads observed series for a network) | – | Nogat's gate |
| O1 | Obserwator | every hydrological station located (the static source in the catalog build, GEO-03); the full `hydrographic_code` in live results (GEO-04); the MPHP code of a gauge's river; the catchment areas of ČHMÚ gauges | – | the scenario's catalog: no hydrological station of the two basins without a location; the Bóbr's ČHMÚ gauges with areas |
| K1 | Kartograf | CZ catchment polygons as a product (GEO-06, DIBAVOD), beside HY-NET's lines | – | the Bóbr's Czech part (232.4 km²) from Kartograf |
| A1 | Archiwista | check one project and one closed set per basin: the Barycz's 1,213 sheets, counties, HSG and the PGW GeoPackage pinned; an area change refused under a closed set (E7-01) | – | `project_verify` ok; Hydrograf's dry run of the whole set rc 0 |
| L1 | Hydrolog | observed inflows: a node of `hydrolog-network/1` names its station and series, read from `hydrolog-series/1` or Obserwator's CSV as given discharges; the balance of a differential catchment against the downstream gauge | – | Hydrolog's gate; Łąki to Osetno on the Barycz's series |
| H1 | Hydrograf | an ADR amending ADR-071 and ADR-067 (parts, inlets, one database, one set per basin) and Hydrograf's plan | this plan approved | the author's review |
| H2 | Hydrograf | migration: `part_id`, one active run per part; `publish_run`, land cover, soil, `bdot_streams` and depressions replaced by part; a DEM mosaic per part | H1 | two parts in one database: the second leaves the first's rows and files unchanged (E7-08 closed) |
| H3 | Hydrograf | the partition, windows, the preparation along lines, ownership by D8, the inlet table with its cases, the seam report | H2 | synthetic DEMs for each case of the inlet table; the Orla in three parts and its seam report |
| H4 | Hydrograf | inlet records and the attribute pass | H3 | synthetic DEMs: the parts equal the whole run; an upstream re-run changes only downstream attributes |
| H5 | Hydrograf | the graph across parts, delineation across parts, whole-part aggregates, the graph loaded at start | H4 | Osetno over Barycz 1 to 3 equals the whole run within ±0.5 % |
| H6 | Hydrograf | tiles on the basin's lattice, one VRT over the parts, a run pointer per part, `tile-join`, `instance.json` with its parts | H2 | precise-mode and network windows across a seam; MVT tiles at a seam; `instance.json` |
| H7 | Hydrograf | gauge control (catalog, snapping, tolerances, table), the GUI's area comparison and `catchment_truncated` | H5, O1 | the 42 IMGW-PIB gauges of the two basins in the table; Błażkowa warned before H8 |
| H8 | Hydrograf | the CZ DEM in the set reader (GEO-01) and HY-NET lines for burning and inlets; until then border inlets from the DEM | K1 | the Bóbr with its Czech part: Błażkowa and Żagań within their tolerance |
| H9 | Hydrograf | differential catchments from the graph; the network with observed inflow nodes and graph elements beyond the window (ADR-080 amendment) | H5, H7, L1 | Łąki to Osetno with the Orla at Korzeńsko: a valid hand-off that Hydrolog routes and balances |
| T1 | e2e | the acceptance below on the Barycz and the Bóbr, each one instance from one closed set | H2–H9, A1 | Acceptance |

## Acceptance

1. Equivalence: the Orla (Barycz 2, 1,599.3 km², 75.7 M valid cells), run whole as in the scenario and in three parts, has the same D8 on every cell outside the seam report's disputed cells, and the upstream areas of its nodes at the 1 km² threshold agree within ±0.5 %; re-running an upstream part changes only attributes downstream (D3).
2. Gauges: the 42 IMGW-PIB gauges of the two basins lie within their tolerances (D7). Before H8 the Bóbr's gauges below its Czech part are `partly_outside_data`, with the missing area named; any other miss carries a reviewed reason in the table.
3. Seams: every boundary's report is under its threshold.
4. Memory: every part's peak RSS stays under its cap, with anonymous and mapped memory logged per stage.
5. Continuity: in one instance per basin, delineation at Osetno (4,574.72 km²) and at Żagań (4,258.38 km²) crosses parts and matches the gauge's area within tolerance (Żagań after H8); no part's bootstrap replaces another's data.

## Risks and open questions

Risks:

- The Odra (~119,000 km²): at most 2,750 km² per part means at least 44 parts; the measured 72 graph nodes per km² give about 8.6 M nodes, and 6.3 MiB per km² of data, tiles and database (`REPORT.md:96`, `:373-382`) about 0.7 TiB [INFERENCE: linear].
- Seams in flat land: ADR-071 met closed basins wider than a 16 km halo, so a 1 km buffer leaves disputed area, and its size decides whether D1 holds [INFERENCE].
- The Barycz's fish ponds and canals: bifurcations and canals across divides that D8 cannot split; their unburned crossings are only reported.
- Reservoirs on the Bóbr and the Kwisa (Bukówka, Pilchowice, Leśna) on JCWP boundaries: the lake-outflow rule, or parts that keep each reservoir whole.
- IMGW-PIB's areas: of unknown method and date; on border rivers they include Czech land; Korzeńsko and Rydzyna are unexplained.
- Memory: the logged peak is bounded by the cap, so the budget stays uncertain until anonymous memory is measured per stage.
- The preparation along lines is new code; where it differs from today's whole-DEM smoothing, the windows of a seam disagree where streams enter.

Open questions for the author:

1. Option B: an interim whole-basin run at 10 m (the Barycz 93.9 M grid cells; the Bóbr's Polish part 141.7 M, 56.5 M valid), with a target cell coarser than the source, before or instead of A for the Barycz?
2. The tolerances (±2/5/10 %), the seam threshold, N (10 cells) and the distance to confluences (200 or 500 m): calibrated on which gauges, and by whom?
3. GEO-06 is CZ catchment polygons in the report and CZ watercourse lines in the discussion; Kartograf already has HY-NET's lines and Hydrograf reads neither. Which comes first?
4. The budget: valid or grid cells, and the cap (8 GB, or the test's 9 GB overlay)?
5. Does a gauge outside its tolerance, or a seam over its threshold, only warn, or block the publish?
6. One basin per instance, or the Barycz and the Bóbr in one instance?
7. Timing: after the first joint release (candidate-5 holds Hydrograf `939b55f`), like the IMGW-PIB plan, or before it?
8. T1: reuse the scenario's harness (`~/workspace/_e2e/2026-11-15/scenario/E7/`: `chain_parts.sh`, `run_part.sh` with its free-memory gate) and GPT for the GUI tasks, whose usage limit ran out at 01:22 (`COORD-FINDINGS.md:14`)?
9. A small inlet whose upstream area crosses a threshold: a re-run of the downstream part (order then matters for it), or a fixed seed?

## Results

None yet.
