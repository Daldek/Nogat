# Plan: Hydrograf's design rainfall without IMGW-PIB, after the first joint release

Approved: pending

Status: a to-do recorded on 2026-11-14 from the research [era5-instead-of-pmaxtp.md](2026-11-14-independence-from-imgw/era5-instead-of-pmaxtp.md) and the author's decisions of that day; not an approved plan, so no code starts (DEV-17.4). Work begins only after the first joint release (decision 2) and this plan's `Approved:` line.

Requirements: DEV-17.4, DEV-17.5, HUB-2.7, HUB-5.2 (producers before consumers), DEV §20, ECO-059 (roles of Archiwista, Obserwator and Hydrolog for hydro-meteorological data).

## The author's decisions (2026-11-14)

1. Today Hydrograf is entirely non-commercial, so the IMGW-PIB licence does not limit it; PMAXTP stays in Hydrograf, with its lines PS, PP, M and RK, until this plan's steps replace it.
2. Moving away from IMGW-PIB starts immediately after the first joint release of the ecosystem. The release: Nogat (the ecosystem), Hydrograf (the main tool), Obserwator and Kartograf (producers), Hydrolog (the computation engine), Archiwista (the common data store); Retman optional (AI support); Hydraulik later; Astronom undecided (it may be folded into Kartograf).
3. The path away from PMAXTP, in this order:
   - **D** first: the user enters the design rainfall;
   - **R**: ERA5/CERRA (CC BY 4.0) × a few published, peer-reviewed correction parameters derived only from IMGW-PIB HVD observations, as a research study with Obserwator and Hydrolog;
   - **A**: a transfer from KOSTRA-DWD and ČHMÚ PERUN, as a check of R;
   - **C**: an agreement with IMGW-PIB on PMAXTP, only on demand.

   A written question to IMGW-PIB (biznes@imgw.pl) goes out before any commercial start.

## Goal

Hydrograf can be offered commercially without any data whose terms require an agreement with IMGW-PIB. Its default design rainfall comes from open Copernicus reanalysis corrected by published coefficients, and a user can always enter their own.

## Options

From the research, §0 point 6 and §8:

| Path | Without IMGW-PIB? | Quality | Decision |
|---|---|---|---|
| D. User rainfall („bring your own”) | yes | the user's | first (decision 3) |
| R. ERA5/CERRA × published coefficients from a study against IMGW-PIB HVD gauges | yes in the service; the study uses HVD data with lines S and P | close to point scale, if the study succeeds | the target default rainfall |
| A. ERA5/CERRA + transfer from KOSTRA-DWD (DE) and PERUN (CZ) | yes | screening | the independent check of R |
| B. Own DDF from IMGW-PIB HVD data | no (IMGW-PIB attribution, the 10-min archive on request) | close to PMAXTP | not chosen |
| C. Agreement with IMGW-PIB on PMAXTP | no | the best | only on demand |
| ERA5 alone, uncorrected | yes | 27–44 % of PMAXTP for 1 h, 66–91 % for 24 h at the two tested points (research §5.3) | rejected: under-sizes structures |
| Any correction fitted to PMAXTP | no (carries PMAXTP's terms) | – | rejected (research §2.4) |

## What in Hydrograf depends on PMAXTP

PMAXTP is Hydrograf's only IMGW-PIB data (research §2.3, grep of `develop` `aa975b0`):

1. Data and processing: `scripts/preprocess_precipitation.py`, bootstrap step 6 („Opady IMGW”) in `scripts/bootstrap.py`, `IMGW_GRID_SPACING_KM` and `IMGW_RATE_LIMIT_DELAY_S` in `core/config.py` and `.env.example`, the table `precipitation_data` (source `IMGW_PMAXTP`), the live `fetch_pmaxtp` in `scripts/analyze_watershed.py`.
2. Computation and API: `core/precipitation.py` (PMAXTP's sets of durations and p, `PmaxtpGridPointUnknown`), `api/endpoints/hydrograph.py` (design rainfall, `PmaxtpPoint`), `api/endpoints/watershed.py` and `core/network_delineation.py` (`thiessen_cells`, the field `pmaxtp_grid` in every delineation response), `models/schemas.py` (`PmaxtpGridCell`, `pmaxtp_grid`, `derived_from: "pmaxtp"`), `core/handoff.py` (`pmaxtp_origin`, `source: "pmaxtp"`), `core/messages.py`.
3. Attribution and regulamin: `core/attribution.py` (PS, PP, M, RK), the block `pmaxtp` in `core/terms.py`, the PMAXTP lines in `api/endpoints/site.py`, the statement „Dane IMGW-PIB są w nim wykorzystywane do celów niezarobkowych” in `frontend/index.html`, the manual and `frontend/nogat/`.
4. Analysis results: `frontend/data/results/sfincs-kamiennik-24h-p1` (Hydraulik/SFINCS, rainfall from PMAXTP) and `core/analysis_results.py`.
5. User series: a hyetograph copied from PMAXTP (`derived_from = "pmaxtp"`) carries PMAXTP's terms.
6. The package dependency `obserwator` in `backend/pyproject.toml`, used only for PMAXTP.
7. Interface and documentation: `js/info-texts.js`, the labels „Opad PMAXTP”, the export „Punkty PMAXTP (GeoJSON)”, the manual, slides, PDF; tests (`pmaxtp_body`, `test_preprocess_precipitation.py`).

## Steps

Producers before consumers (HUB-5.2); each project in its own session and branch (DEV-17.5). Under ECO-059 Archiwista orders downloads into its raw root through Obserwator's library; the download code itself is Obserwator's.

### Nogat

- N1. `data_sources` (HUB-2.7): `c3s` (Copernicus Climate Change Service: ERA5, ERA5-Land, CERRA, CERRA-Land; CC BY 4.0), `dwd` (KOSTRA-DWD-2020; CC BY 4.0), `knmi` (EURADCLIM; CC BY 4.0), `chmi-perun` once its licence is confirmed; `c3s` and the others in the `data_sources` of the projects that access them directly. `imgw-pib` stays for Obserwator.
- N2. DEV §20: the C3S attribution line (research §2.2) and the citation of the study's article next to S, P, PS, PP, M, RK; the regulamin kit gains a `copernicus` block and a variant of the footer statement for a commercial instance.
- N3. The written question to IMGW-PIB (biznes@imgw.pl), the four points of research §3.6, as a draft next to this plan, sent by the author before any commercial start; the answer archived.

### Obserwator (download)

- O1. A Copernicus C3S provider and the dataset `eu.c3s.era5_tp`: hourly `tp` per cell as „virtual stations” in the Parquet store, a CC BY 4.0 sidecar, ECMWF ARCO with the CDS key from the configuration or Earthmover anonymously; PL + CZ + a German strip, 1950–2025 (~4 GB).
- O2. CERRA hourly totals (since 1984) behind the same provider, if the study compares it.
- O3. The IMGW-PIB dataset `terminowe/synop` (6-h rainfall `WO6G`, since 1966), and the 10-min/1-min archive once IMGW-PIB releases it on request (HVD terms to be confirmed by N3).
- O4. Reference datasets for A: KOSTRA-DWD-2020 and, if licensed, PERUN; EURADCLIM 1 h and 24 h.

### Hydrolog (statistics)

- HL1. `stats duration-maxima`: rolling totals and annual maxima with dates from hourly and 6-h series (1–72 h), with the Hershfield factor for daily data.
- HL2. `stats ddf`: GEV and Gumbel (and GPD) from L-moments, a regional shape (ROI), block-bootstrap confidence intervals (upper bound = quantile + 1σ, as PMAXTP), DDF consistency across durations, a grid mode for reanalysis cells; NetCDF/Zarr or Parquet input.
- HL3. Versioned correction coefficients k(D, T) as an explicit parameter set with its DOI, applied to reanalysis quantiles; result schemas (AGI-4.1).
- HL4. The study (R) with Obserwator's data: ERA5/CERRA vs IMGW-PIB HVD gauges, 3–6 published numbers, no per-station values or grids; validation against KOSTRA, PERUN and EURADCLIM (A); open-access, peer-reviewed publication under CC BY 4.0 with lines S and P and the code.

### Hydrograf (intake, last)

- HG1 (path D, first after the release). The user's design rainfall replaces PMAXTP in the commercial service: PMAXTP out of the pipeline (bootstrap step 6, `precipitation_data`), the API (`pmaxtp_grid`, `PmaxtpPoint`, `PmaxtpGridCell`, as an API version), the UI, the hand-off, the regulamin and attribution, the docs and tests; copying a PMAXTP hyetograph removed; the SFINCS result recomputed or removed; the `obserwator` dependency dropped.
- HG2 (path R). The default rainfall from Hydrolog's files (no runtime import of Obserwator): a new source in `precipitation_data` (e.g. `ERA5_DDF`), durations ≥ 1 h from the reanalysis and shorter ones explicitly from the DDF, p ≥ 1 %, labelled „areal rainfall from a reanalysis, corrected” with its uncertainty and not combined with the user's ARF; the C3S lines and the article's citation in `core/attribution.py`, the `copernicus` block in `core/terms.py`; CHANGELOG.

Kartograf, Archiwista, Retman and Hydraulik: no step beyond registry edges; meteorology stays Obserwator's.

## Open questions

1. IMGW-PIB's answer (N3): whether the daily posts, the 6-h synop and the 10-min/1-min archive are HVD; whether the archive is released on HVD terms, in what format and for what fee; whether a few published coefficients applied to ERA5 in a commercial service are „use of IMGW-PIB data” in the sense of §3 ust. 2; the attribution expected in the article and in the service.
2. A lawyer's assessment of research §3.3 and §3.4 (derived results, the sui generis database right), and whether the study must be run with a university as the „entitled body” of §4 of IMGW-PIB's terms when its author later runs a commercial service.
3. Whether processing PMAXTP values the user enters (path D) is safe in a paid service.
4. The licences of ČHMÚ PERUN and HydroRAIN; the presence of `tp` in Earthmover's Icechunk ERA5.
5. ERA5 or CERRA as the reanalysis of R (CERRA is better for rainfall but starts in 1984); the start year (1950 or 1979, homogeneity); readiness for ERA6 (end of 2027).
6. Whether reanalysis cells belong in Archiwista's raw root (ECO-059) or only in Obserwator's data root, given their size and form.
7. Durations 5–45 min: kept from a DDF shape with flagged uncertainty, or dropped from the default rainfall.
8. Who carries the study, the journal and the time to review; the C path only if clients ask for PMAXTP.
9. GUGiK's commercial status (outside this plan, research §2.2).

## Results

None yet.
