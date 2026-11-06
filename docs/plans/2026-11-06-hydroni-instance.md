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

(filled in per step)
