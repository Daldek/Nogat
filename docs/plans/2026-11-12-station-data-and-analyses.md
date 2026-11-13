# Plan: station data and analyses: raw data in Archiwista, harmonized data and analysis results in Obserwator, every computation in Hydrolog

Approved: 2026-11-13, the author (answers to questions 1–6 and the go-ahead to implement, in session)

Requirements: HUB-5.2 (producers before consumers), DEV-17.4, DEV-17.5, DEV-3.4, DEV §15, DEV §19, ECO-054, ECO-055, ECO-058, ECO-059; the author's requests of 2026-11-12 and answers of 2026-11-13 (below). Project plans: Obserwator's GUI, `docs/plans/2026-11-12-obserwator-gui.md` in Obserwator (branch `plan/obserwator-gui`, approved 2026-11-13), carries the GUI's detail (this plan's O3 and O4), with the reviewed prototype on Obserwator's branch `feat/gui-mockup` (`mockup/gui/`); Hydrolog's and Archiwista's own plans follow this one's approval (DEV-17.4) and point at it.

## The author's requests (2026-11-12)

The first three answers, verbatim:

- „Podgląd stacji, udostępnianie zharmonizowanych danych w innym formacie niż to co dane IMGW i Czesi. Archiwista pokazuje to co teraz i odpowiada za trzymanie surowych danych, pobieranie ich, itp., a Obserwator docelowo ma też udostępniać statystyki i inne dane po ich analizie.”
- „Podobnie do GUI Hydrografa, bo wszystkie stacje będą na mapie, a ich dane w panelu po prawej stronie.”
- A public GUI in the test deployment beside hydrograf-test, hydrolog-test and archiwista-test (Cloudflare Access).

The requirements that followed the same day, as relayed in English:

1. Archiwista manages downloading; raw data come from Archiwista's store. Obserwator keeps only the parsed (harmonized) versions of those data and the results of analyses, and serves them (GUI, exports, API). Hydrolog does every computation; its code is extended for that.
2. A station's view differs by kind: hydrological and meteorological stations show different data and analyses.
3. Hydrological analyses, computed by Hydrolog and shown and served by Obserwator: characteristic water levels of the first degree (NW, SW, WW per year or period) and of the second degree (NNW, SNW, WNW, NSW, SSW, WSW, NWW, SWW, WWW over a multi-year period) with the warning and alarm levels IMGW publishes; rating curves fitted from stage and discharge over a range of years the user chooses; maximum flows of a given probability computed identically to Hydrolog's `stats flood-frequency`; further analyses from water levels, discharges and water temperature (regime, harmonic analysis, low flows, duration curves, trends, seasonality).
4. Meteorological analyses: precipitation maxima, sums, means, the number of days with precipitation, dry spells, and more.
5. Inspiration: the author's analysis code of 2024 and 2025 in Obserwator's history.

## The author's answers (2026-11-13)

Verbatim, with their meaning:

1. „Kod pobierania zostaje biblioteką Obserwatora, którą Archiwista wywołuje” — B1: the download code stays Obserwator's library, and Archiwista calls it.
2. „Surowy leży u Archiwisty, zharmonizowany też, ale tylko jako backup całego zakresu. Wersja produkcyjna leży u Obserwatora. Co do odświeżania — dane powinny być przeliczone raz, na początku i tyle, a pobieranie nowych będzie realizowane 1 raz w roku, gdy pojawią się nowe paczki danych publicznych. Jeżeli user liczy jakieś rzeczy dla wybranego wycinka danych, to robimy to w locie i nie jest to w żaden sposób zapisywane na stałe.” The raw data live in Archiwista; Archiwista also keeps the harmonized data, but only as a backup of the full range; the production harmonized data and results live in Obserwator. Everything is computed once, at the start; new data are downloaded once a year, when IMGW-PIB and ČHMÚ publish new packages. Computations for a subset a person chooses run on the fly and are never stored.
3. „Nie, danych operacyjnych nie archiwizujemy” — IMGW-PIB's warning and alarm levels (operational data of hydro.imgw.pl) are not archived; a station's view shows ČHMÚ's thresholds and the characteristic levels only.
4. IMGW-PIB's terms for the public instance: „do sprawdzenia” (to be checked); a research note follows.

As relayed in English the same day:

5. Reference periods: the whole record by default, adjustable by the person, with a note that the recommended minimum period is 30 years.
6. XLSX (question 1 of the GUI plan): not needed; exports are CSV, JSON and Parquet.

With them, the GUI requests recorded in Obserwator's GUI plan: PMAXTP of a point in the GUI without a layer of its grid; the map's second view renamed „Pomiary bieżące”, with the current measurements of IMGW-PIB's hydrological and meteorological stations and only that layer shown; station points styled as on hydro.imgw.pl; and the go-ahead to implement, Hydrolog's extensions first.

## Goal

- One role per project for hydro-meteorological station data: **Archiwista** downloads and keeps the raw data of IMGW-PIB and ČHMÚ; **Obserwator** turns them into harmonized series and station catalogs, keeps the results of the analyses and serves both (its GUI, files, REST, MCP); **Hydrolog** computes every analysis. Kartograf's data and roles do not change.
- Obserwator's GUI (its own plan): every station on a map, the chosen station in the right panel, with views that differ for hydrological and meteorological stations and show the analyses below.
- The analyses of the two lists below, each computed by Hydrolog's code, stored by Obserwator with where it came from, and the same number in Obserwator and in Hydrolog for the same series and options.

## Where it starts

Read on 2026-11-12: Nogat `origin/develop` `99de00a`; Obserwator `origin/develop` `b853637`; Hydrolog `origin/develop` `912dbf2`; Archiwista `origin/develop` `a656ee1`; the deployment host; with the research of the same day on the published data and Hydrolog's statistics (`StationDataSources`) and on Obserwator's history (`HistoryDig`), each fact checked against the source cited. Paths of other projects are named with their project.

| Fact | Consequence |
|---|---|
| One Obserwator store holds the raw archives with their sidecars, the Parquet series, the station catalogs and the PMAXTP cells (Obserwator `docs/ARCHITECTURE.md:199-211`); ECO-054 says „Kartograf and IMGWTools download, check and keep the versioned store” (`standards/DECISIONS.md:982`) | the roles of requirement 1 amend ECO-054 for hydro-meteorological data and split that store |
| Archiwista „never writes to a store”: a download „goes through the producer's API” (Archiwista `README.md:3,43`) on the command of a person with `store.write` (Archiwista `docs/SPEC.md:405`); its actions are Obserwator's `store sync`, `store catalog` and `series build` (Archiwista `src/archiwista/adapter/obserwator/actions.py:98`); `store sync` also builds the series unless `--no-series` (Obserwator `AGENTS.md:124,137`) | Archiwista already orders the downloads through Obserwator's library; parsing runs in the same calls |
| Obserwator's download side is about 7,900 lines (`store/sync.py`, `store/writer.py`, `store/content.py`, `store/plain.py`, `store/pmaxtp.py`, `datasets.py`, `fetch.py`, `stations.py`, `urls.py` under Obserwator `src/obserwator/`); its parsing and reading side about 9,700 (`_parsing/`, `store/series.py`, `store/catalog.py`, `store/reader.py`, `store/export.py`); the registry `datasets.py` serves both | moving the download code is a large change (question 1) |
| Building a catalog fetches station metadata that is not archived: ČHMÚ `now/metadata/meta1.json` and `meta3.json` (Obserwator `docs/DECISIONS.md:214`) and IMGW-PIB's coordinates (Obserwator `docs/ARCHITECTURE.md:238`) | with raw data in Archiwista, these sources become raw archives too, so that Obserwator builds catalogs offline |
| Obserwator's PRD: „Analytical and statistical parts … live in a separate repository (Hydrolog) and are out of scope” (Obserwator `docs/PRD.md:13`); Archiwista: „Hydrological calculations and statistics of series” out of scope (Archiwista `docs/SCOPE.md:108`), „Statistics stay Hydrolog's and Retman's” (Archiwista `docs/decisions/0051-monthly-and-annual-charts.md:24`) | Obserwator serves results and computes none; Archiwista keeps its display-only annual extremes (A-ADR-051) |
| Hydrolog's statistics today: `stats characteristic` (second degree WW, SW, ZW, NW of annual maxima, means and minima of a daily Q or H series, by hydrological year), `stats daily`, `stats monthly` (with a confidence interval), `stats flood-frequency` (log-normal, GEV, Pearson III, Weibull; L-moments by default, ML, moments, least squares; KS, A², AIC), `stats low-flow`, `stats low-flow-sequences` (threshold level, `min_duration_days`, `max_gap_days`), `stats mann-kendall`, `stats homogeneity` (Hydrolog `src/hydrolog/catalog/groups/stats.py:86,186,241,331,462,524,651,770`); `hydrometrics rating-curve` Q = a·(H − H₀)^b and `hydrometrics water-level-zones` after Rybczyński (Hydrolog `src/hydrolog/catalog/groups/hydrometrics.py:17,218`) | most of the hydrological list exists; the meteorological list and several hydrological items are new (tables below) |
| Limits found: `stats characteristic` returns only the second degree, without half-years, and labels H as WWH…NNH (Hydrolog `src/hydrolog/statistics/characteristic.py:36-84`, `catalog/groups/stats.py:161`); `stats low-flow-sequences` needs „a complete daily series without NaN” (`stats.py:524-545`); no public duration curve, Sen's slope, harmonic analysis, regime index or precipitation statistics (`git grep` of `src/hydrolog`) | the extensions of the steps H1 to H3 |
| Hydrolog reads Obserwator's series CSV (its example `obserwator_series_export.csv`, Hydrolog `catalog/groups/stats.py:24`; `ecosystem.yaml:279`) and the hand-off `hydrolog-series/1` with daily values or annual extremes (Hydrolog `src/hydrolog/schemas/hydrolog-series-1.schema.json`, its ADR-0020); Hydrolog depends on Obserwator, optionally (`ecosystem.yaml:273-279`); Obserwator is on PyPI and Hydrolog is not (`ecosystem.yaml:131,208`) | Hydrolog takes Obserwator's files; Obserwator cannot declare a package dependency on Hydrolog, so it starts Hydrolog's program |
| Published data: IMGW-PIB half-year and annual characteristics, `{H,Q,T}_{min,mean,max}` with the dates of the extremes (Obserwator `src/obserwator/store/series.py:803-817`); ČHMÚ daily H, Q, T only, „No monthly H, no monthly minima, no semi-annual/annual extremes”, but rating curves `RC_{WIGOS}.json` (731 files) and long-term characteristics `CHAR_MDQ`, `CHAR_MONQ`, `NY` (1,217 files), not in Obserwator's registry (Obserwator `docs/superpowers/research/2026-10-18-chmi-hydro.md:29,319`); ČHMÚ's SPA 1–3, drought and Q50 levels are in the catalog (Obserwator `src/obserwator/store/reader.py:1770-1771`); IMGW-PIB's warning and alarm levels have no source in Obserwator: the map API it reads gives only a state class (Obserwator `src/obserwator/stations.py:440-470`) | first-degree values come from IMGW-PIB's characteristics where published; new raw sources: ČHMÚ's curves and characteristics; IMGW-PIB's levels are operational data and are not archived (answer 3) |
| Meteorological data in the store: IMGW-PIB daily climate (`Tmax`, `Tmin`, `Tmean`, `Tground`, `P`, `snow_cover`) and precipitation (`P`, `snow_cover`, `fresh_snow`) stations, ČHMÚ daily `P`, `Tmean`, `Tmax`, `Tmin` with quality flags (Obserwator `AGENTS.md:54-67`) | the meteorological analyses need no new raw data |
| Deployment: `obserwator-test.debever.pl` already serves a placeholder from 127.0.0.1:8060 behind Cloudflare Access (`docs/PROGRESS.md:94`, `docs/plans/2026-11-12-gui-links-and-handoff.md:184-189`); the public Archiwista's Obserwator store `/mnt/magazyn/agent-tmp/hydroni/obserwator` is empty, `/mnt/magazyn/agent-tmp/archiwista-zespol/obserwator` holds 481 MB with test data among them | the tunnel host exists; where the stores live is question 2 |

## What the author computed before

The author's analysis code of 2023-09 to 2025-08 in IMGWTools (now Obserwator), found by the research of 2026-11-12 (HistoryDig) and checked in Obserwator's history: `code/hydro_stats.py` with the class `StationData` and the extreme-value classes, and `code/meteo_stats.py` with `MeteoStationData` (fullest at `a10a0ec`, 2025-04-07); commits „Montly stats and plotting” (`154a5d0`, 2024-10-29), „Rating curve” (`8dc65c0`, 2024-11-03), „Water level frequencies and low water level sequences” (`9fe797c`, 2024-11-26), „Water level frequency curve” (`b38283e`, 2024-11-27), „rating curve update” (`8b171d6`, 2024-11-29), the daily volumes and the modal flow (`95ec3ea`, 2025-04-06), the PMAXTP page and the Beta hyetograph workbook (2025-04-06 to 2025-04-11). It was removed from Obserwator by „Remove legacy code and update README” (`2bea370`, 2026-01-10; merged `a0ff98c`, 2026-01-11); none of it remains there, and Hydrolog's statistics carry its methods on.

| Method then (`a10a0ec:code/hydro_stats.py`) | Hydrolog today | In this plan |
|---|---|---|
| `characteristic_values` (`:375`): WW, SW, ZW, NW of maxima, means and minima, from IMGW-PIB's half-year file (pooled half-year extremes) or per year from daily data | `stats characteristic`, daily data only, second degree only | H1, H2: both sources, first and second degree, half-years |
| `calculate_water_levels_frequency` (`:482`): 10 cm classes of H counted per hydrological month, the cumulative duration „including higher”; `plt_water_level_frequency` with the modal class (`:1199`) | inside `hydrometrics water-level-zones` only | H8: a public duration curve and class frequencies |
| `rybczynski_method` (`:683`): the line between the extremes and a parallel through a point the user picks; NTW at the modal class | `hydrometrics water-level-zones`, limits found from the curve | H9, unchanged |
| `power_func`, `plt_rating_curve` (`:679,829`): H = a·Q^c with residuals beyond 2σ removed | `hydrometrics rating-curve`, Q = a·(H − H₀)^b with outlier removal, pairs only | H4: dated series and ranges of years |
| `find_low_sequences` (`:741`): Q below a threshold given by the user (SNQ was a to-do) for at least 5 days, runs merged across gaps under 4 days, the deficit volume | `stats low-flow-sequences`, threshold given, no gaps allowed | H7: gaps, thresholds from the series, yearly summaries |
| `calculate_monthly_statistics`, `plt_confidence_interval` (`:570,1069`): monthly statistics with a 95 % interval | `stats monthly` | H11, unchanged |
| `LogNormalAnalysis`, `GenExtremeAnalysis`, `PearsonIIIAnalysis` with KS (`:1515,1563,1615`); `FisherTippettAnalysis` of minima (`:1747`) | `stats flood-frequency`, `stats low-flow` | H5, H6 |
| Daily volume differences and cumulative volumes (`95ec3ea`) | none | H17 |
| `meteo_stats.py` `basic_stats` (`:52`): extremes and means of temperature, sums and the maximum of precipitation | none | M1, M2, M11 |

## Options

**A. Raw and parsed data: one store or two**

| Option | Verdict |
|---|---|
| A1. One root as today, each project writing its own directories | Rejected: requirement 1 says Obserwator keeps only parsed data and results, and a public Obserwator would carry every raw archive |
| A2. Two roots: Archiwista's raw root (the archives with their sidecars, the archived station metadata, the PMAXTP cells) and Obserwator's data root (series, catalogs, analysis results), each with its own marker | Chosen (answer 2): the roles of requirement 1 in the file system; the public host gets only the data root; the raw root keeps today's archive layout, so its bytes, sidecars and provenance stay as they are |
| A3. A raw format of Archiwista's own | Rejected: a second implementation of downloads, freshness and provenance that Obserwator's store already has |

**B. The download code** (question 1, answered)

| Option | Verdict |
|---|---|
| B1. It stays Obserwator's library; Archiwista calls it into its raw root, as it calls `store sync` today | Chosen (answer 1): no code moves, Archiwista already runs it, the archive contracts (`obserwator-store/1`, `obserwator-meta/1`) stay with the code that writes them |
| B2. It moves to Archiwista | Rejected (answer 1): about 7,900 lines and their tests would move, Hydrograf and Hydraulik (`fetch_pmaxtp`) and Retman (the store commands) would follow, and Archiwista, a browser that „never writes to a store”, would become a producer |

**C. How Hydrolog computes for Obserwator**

| Option | Verdict |
|---|---|
| C1. Obserwator writes the series files and a list of catalog calls; one Hydrolog process runs them all (a batch) and writes one result envelope per call; a subset the person chooses (a range of years, a distribution, a threshold) is a single call of Hydrolog's CLI from Obserwator's server | Recommended: Hydrolog's own commands compute everything, imported once per batch; no package dependency |
| C2. One CLI call per analysis | Rejected for the stored results: about 1.4 s per call (Hydrolog's GUI plan) for thousands of stations and a dozen analyses each |
| C3. Obserwator imports Hydrolog | Impossible: Obserwator is on PyPI and Hydrolog is not; and a cycle with Hydrolog's optional dependency on Obserwator |
| C4. Obserwator computes the simple ones itself | Rejected by requirement 1 and by A-ADR-051's rule that statistics stay Hydrolog's |

**D. Where results live**

| Option | Verdict |
|---|---|
| D1. Versioned in Obserwator's data root, with the series version, the Hydrolog version, the command and its options | Chosen (answer 2): requirement 1; a result is reproducible and its age is visible |
| D2. Computed on every request, never stored | Rejected for the default results (cost on a small server); used for a subset the person chooses, which answer 2 says is computed on the fly and never stored |
| D3. Kept by Hydrolog | Rejected: Hydrolog keeps no store |

**E. The same number in both tools**

| Option | Verdict |
|---|---|
| E1. Hydrolog's code computes every number Obserwator shows; the hand-off to Hydrolog carries the same input series and options; results name the Hydrolog version | Recommended: identical by construction; a different version is visible |
| E2. A second implementation checked by tests | Rejected: two codes drift |

**F. Annual extremes for the first degree and the flood quantiles**

| Option | Verdict |
|---|---|
| F1. IMGW-PIB's published half-year characteristics where they exist (the larger of the winter and summer maxima is the annual maximum), daily series elsewhere (ČHMÚ, IMGW-PIB stations without them); the source is named in the result | Recommended: „IMGW-PIB's half-year extremes may be instantaneous, above every daily mean” (Archiwista `docs/decisions/0051-monthly-and-annual-charts.md:9`); the old `characteristic_values` used both sources |
| F2. Daily series only | Rejected: maxima that may stay below IMGW-PIB's published ones for the same years |

## Decisions

| # | Decision |
|---|---|
| D1 | **Roles** (ECO-059, amending ECO-054 for hydro-meteorological data): Archiwista orders the downloads of IMGW-PIB's and ČHMÚ's data, through Obserwator's library (B1), and keeps the raw data; Obserwator parses them into harmonized series and catalogs, keeps analysis results and serves both; Hydrolog computes every analysis. Kartograf is not affected. |
| D2 | **Two roots** (A2, answer 2). The raw root lives in Archiwista: it keeps today's archive layout (`archives/`, `observations/`, `pmaxtp/`) and `obserwator-store/1`. The data root holds `series/`, `stations/` and `analyses/` under a marker of its own, named in Obserwator's ADR; Obserwator holds the production data root, the one its GUI, files, REST and MCP serve, and Archiwista keeps a backup copy of the whole data root beside its raw root. Existing stores are split once by a documented copy, without aliases. |
| D3 | **Raw data reach Obserwator by reading** the raw root that Archiwista maintains, read-only: `series build`, the catalog build and the analyses take a raw root as their source and write only the data root, at the start and at each yearly refresh (D7). Obserwator's GUI never downloads. Live reads that keep nothing, the current IMGW-PIB measurements of hydrological and meteorological stations and PMAXTP of a point, stay in Obserwator's server, in memory only; current data are outside Archiwista's scope (Archiwista `docs/SCOPE.md:109`). |
| D4 | **Catalogs offline.** The station metadata a catalog needs (ČHMÚ `now` metadata, IMGW-PIB coordinates) become raw archives downloaded with the station lists, so a catalog is built from the raw root alone. |
| D5 | **Downloads under Archiwista.** Archiwista orders every download into the raw root through Obserwator's library (B1) and keeps its permissions (`store.write`) and jobs; `series build` and `store catalog` leave its actions, as they write Obserwator's data root. Archiwista reads series and catalogs from the data root. |
| D6 | **Hydrolog computes** (C1): a batch entry that runs a JSON Lines file of catalog calls in one process and writes one `hydrolog-result/1` per call; series come as Obserwator's export files; single calls for a subset the person chooses. Hydrolog's catalog gains the extensions and new commands of the tables below, each with its result schema. |
| D7 | **Results in Obserwator** (D1, answer 2): `analyses build` exports the series, runs Hydrolog's batch through a configured `hydrolog` program, and stores each result as a version with the station, dataset, series version, command, options and Hydrolog's version; `analyses read` and `analyses export` serve them in Python, the CLI, REST and MCP. Everything is computed once, at the start, over the whole record. Once a year, when IMGW-PIB and ČHMÚ publish new packages, Archiwista downloads them, Obserwator rebuilds the series and catalogs and `analyses build` recomputes the results; the new data root replaces the production one and its backup. A result for a subset the person chooses (a range of years, a distribution, a threshold, a period) is computed on the fly by a single Hydrolog call and never stored: not in the data root and not cached to disk, at most held in the server's memory. |
| D8 | **The same number** (E1, F1): every number of an analysis in Obserwator is Hydrolog's; the hand-off from Obserwator's station view to Hydrolog („Kopiuj do Hydrologa”, „Plik przekazania”, DEV-15.5) carries `hydrolog-series/1` with the same series or annual maxima and the options, and Hydrolog's „Wczytaj z Obserwatora” recomputes and shows the producer's numbers beside its own. The deployment runs one Hydrolog version for its GUI and for Obserwator's batch. |
| D9 | **Station views by kind** in Obserwator's GUI: a hydrological station shows its levels, discharges and water temperature with the hydrological analyses; a meteorological station its precipitation, temperature and snow with the meteorological analyses; each view in its own sections, defined in Obserwator's GUI plan. |
| D10 | **New raw sources** (D5): ČHMÚ's rating curves and long-term characteristics (`characteristic/data/discharge_rating_curve/`, `hydrological_characteristic/`). No operational data are archived (answer 3): IMGW-PIB's warning and alarm levels of hydro.imgw.pl are dropped, and a station's view shows ČHMÚ's thresholds and the characteristic levels only. IMGW-PIB's hydrological phenomena (ice) stay outside this plan. |
| D11 | **Registry** (HUB-2.9): summaries of the three projects by D1; edges: Archiwista to Obserwator (library, B1), Obserwator to Archiwista's raw root (data, store), Obserwator to Hydrolog (optional, `cli`), Hydrolog to Obserwator (file, the series export); routes for `obserwator analyses …`, `obserwator gui serve` and Hydrolog's new commands. |
| D12 | **Reference periods** (answer 5): second-degree values, normals, anomalies and every analysis over a period run over the whole record by default; the person may choose another period, which is a subset computed on the fly (D7). Wherever a period is shown or chosen, a note says that 30 years is the recommended minimum, and a shorter period is marked. |
| D13 | **Files** (answer 6): series, stations and analysis results as CSV, JSON and Parquet as Obserwator's GUI plan lists them; no XLSX. |

## Analyses

Every analysis below is computed by Hydrolog (its status today in the column), stored and served by Obserwator; its input is Obserwator's harmonized series unless the column names a raw source of Archiwista. First and second degree follow the hydrological year XI–X and the half-years XI–IV and V–X.

### Hydrological stations (H, Q, T)

| # | Analysis | Data | Hydrolog today |
|---|---|---|---|
| H1 | Characteristic values of the first degree: NW, SW, WW per hydrological year and half-year; the same for Q (NQ, SQ, WQ) and T | IMGW-PIB half-year characteristics (F1), else the daily series | partly: `stats characteristic` finds annual extremes but returns none and has no half-years; extend |
| H2 | Characteristic values of the second degree over a chosen period: NNW, SNW, WNW, NSW, SSW, WSW, NWW, SWW, WWW (and the medians ZNW, ZSW, ZWW); NNQ…WWQ | the values of H1 | yes, `stats characteristic` (whole series, labels WWH…NNH); extend: period, half-years, the input of H1, the W labels |
| H3 | ČHMÚ's SPA 1–3, drought level and Q50, and the characteristic levels of H1 and H2, shown with H and Q; days above each level per year and the events above it (start, end, peak, duration). IMGW-PIB's warning and alarm levels are not archived (D10) | ČHMÚ catalog thresholds; the values of H1 and H2; daily H, Q | no: events above a level are new (`stats low-flow-sequences` finds runs below one) |
| H4 | Rating curve Q = a·(H − H₀)^b from same-day H and Q over a range of years the person chooses, curves of successive periods to show the change, ČHMÚ's published curve beside the fit | daily H and Q; ČHMÚ `RC_{WIGOS}.json` (D10) | partly: `hydrometrics rating-curve` fits pairs; extend: dated series, a range of years, periods |
| H5 | Maximum flows of a given probability: quantiles of annual maxima, four distributions, L-moments by default, goodness of fit | the annual maxima of H1 (F1) | yes: `stats flood-frequency`, used as it is |
| H6 | Minimum flows of a given probability: quantiles of annual minima | the annual minima of H1 | yes: `stats low-flow` |
| H7 | Low-flow periods (niżówki): threshold level method with SNQ, a percentile of the duration curve (Q70, Q90) or a given value; at least 5 days, runs merged across gaps of under 4 days, the deficit volume; per year the number, the longest and the total deficit; for H as low-stage periods | daily Q or H | partly: `stats low-flow-sequences`; extend: gaps in the record, thresholds from the series, yearly summaries |
| H8 | Duration curves of H and Q (exceedance and „including higher”), per period, year or hydrological month; class frequencies (10 cm for H) with the modal class | daily H, Q | partly: inside `hydrometrics water-level-zones` only; new public command |
| H9 | Water level zones after Rybczyński: NTW, STW, WTW | daily H | yes: `hydrometrics water-level-zones` |
| H10 | Daily regime curves: per day of the hydrological year the maximum, mean, median and minimum | daily H, Q, T | yes: `stats daily` |
| H11 | Monthly statistics with a confidence interval (mean, median, extremes, standard deviation, CV, skewness) | daily or monthly H, Q, T | yes: `stats monthly` |
| H12 | River regime: Pardé coefficients (mean monthly over mean annual flow), the regime type of a classification chosen in Hydrolog's plan (for Polish rivers e.g. Dynowska's: niwalny, niwalno-pluwialny, pluwialno-niwalny, pluwialny), the share of the spring snowmelt flood | monthly or daily Q over at least ten years | partly: monthly means from `stats monthly`; coefficients and the type new |
| H13 | Seasonality: the dates of annual maxima and minima as circular statistics (mean date, concentration), the share of winter and summer half-year maxima, a seasonality index of monthly flows | dates of the extremes (IMGW-PIB half-year characteristics carry them) or daily Q | no: new |
| H14 | Harmonic analysis of the annual cycle: mean, amplitude and phase (the day of the maximum) of the first harmonics and the variance they explain, per year and over the period; water temperature first, also Q and H | daily T, Q, H | no: new |
| H15 | Water temperature: days above and below thresholds per year, the warmest period, the annual cycle of H14 compared across years | daily T | no: new |
| H16 | Trends and change points of annual series (WQ, SQ, NQ, NW, SW, WW, mean T, the dates of maxima): Mann–Kendall with Sen's slope; homogeneity of annual maxima | the annual series of H1 | partly: `stats mann-kendall`, `stats homogeneity`; Sen's slope new |
| H17 | Runoff volumes: monthly and annual volumes, the cumulative volume and daily volume differences | daily Q | no: new |
| H18 | Baseflow: separation by a recursive filter, the baseflow index, recession constants | daily Q | no: new |

### Meteorological stations (P, T, snow)

| # | Analysis | Data | Hydrolog today |
|---|---|---|---|
| M1 | Precipitation sums: annual (calendar and hydrological), half-year, season, month; the normal of a reference period and the anomaly in % of it | daily P | no: new |
| M2 | Precipitation maxima: the annual and monthly maximum daily precipitation and the largest sums of 2, 3, 5 and 10 consecutive days, with their dates | daily P | no: new |
| M3 | Maximum precipitation of a given probability: quantiles of the annual maxima of M2; beside PMAXTP of the station's point for IMGW-PIB | the maxima of M2 | yes: the quantile code of `stats flood-frequency`, labelled for precipitation |
| M4 | Means and intensity: the mean annual precipitation, the mean precipitation of a wet day | daily P | no: new |
| M5 | Days with precipitation at least 0.1, 1, 10 and 20 mm per month and year | daily P | no: new |
| M6 | Dry spells: the lengths of the breaks between days with precipitation (below 0.1 or 1 mm), the longest per year, their distribution and the number of spells of at least 10, 15 and 20 days; wet spells likewise | daily P | no: new (the run logic of `stats low-flow-sequences` is its analogue) |
| M7 | The share of heavy precipitation: the sum on days above the 95th and 99th percentile | daily P | no: new |
| M8 | Drought and wetness: SPI over 1, 3, 6 and 12 months; Kaczorowska's relative precipitation classes of months and years | daily or monthly P over at least 30 years | no: new |
| M9 | Seasonality of precipitation: the monthly regime, a concentration and a seasonality index | daily P | no: new |
| M10 | Snow: days with snow cover, the maximum depth of each winter, the first and last day, sums of fresh snow | IMGW-PIB `snow_cover`, `fresh_snow` | no: new |
| M11 | Air temperature: monthly and annual means and extremes, the normal and the anomaly; frost, ice, summer and hot days and tropical nights; growing and heating degree days; the daily range | daily Tmax, Tmin, Tmean | no: new |
| M12 | Harmonic analysis of the annual temperature cycle, as H14 | daily Tmean | no: new (shared with H14) |
| M13 | Trends of the annual series of M1, M2, M5, M6 and M11: Mann–Kendall with Sen's slope | the annual series | partly: `stats mann-kendall`; Sen's slope new |
| M14 | Hydrothermal coefficient and other indices of P and T together, at climate stations | daily P, Tmean | no: new |

## Steps

Producers before consumers (HUB-5.2): Nogat's decision, then Hydrolog's computations and the raw root under Archiwista, then Obserwator's data root and stored results, then Obserwator's GUI, then the consumers' adjustments and the registry. Each step runs in its repository's own session on a topic branch, under its own plan where the step changes a public interface (DEV-17.4), with its gate, ADR, CHANGELOG and PROGRESS. Sizes are in sessions.

| # | Owner | Step | Size | Verified by | After |
|---|---|---|---|---|---|
| A1 | the author | Approval; answers to questions 1 to 6 | — | the line `Approved:` (2026-11-13) | — |
| N1 | Nogat | ECO-059, the ECO decision of D1 (amends ECO-054); the edges and summaries of D11 as `planned`; a pointer to this plan in Obserwator's GUI plan, and in Hydrolog's and Archiwista's plans as they are written | 1 | gate: `standard`, `validate` | A1 |
| H1 | Hydrolog | Hydrological computations: H1 to H4, H7, H8, H17 (first degree and half-years, the period and W labels of the second degree, events above a level, the rating curve from dated series and ranges of years, low flows with gaps and thresholds from the series, duration curves, volumes); a fixture series of IMGW-PIB and ČHMÚ shape | 3-4 | each command's catalog example and tests; the old notebook values reproduced where the method is the same | N1 |
| H2 | Hydrolog | Regime, seasonality, harmonics and trends: H12 to H16, H18, Sen's slope | 2.5-3.5 | tests against published worked examples of each method | N1 |
| H3 | Hydrolog | Meteorological computations: M1 to M14 | 3-4 | tests against hand-computed sequences; the ETCCDI-style counts on a fixture year | N1 |
| H4 | Hydrolog | The batch entry of D6 and the derivation of annual extremes from IMGW-PIB half-year characteristics (F1); result schemas of every new command | 1-1.5 | a batch of 1,000 calls in one process equals the same calls run singly | H1 |
| R1 | Obserwator (B1) | The raw root: `store sync` and the other downloads write only raw data; the station metadata of D4 archived; the new raw datasets of D10 | 2-3 | `store sync` on a fixture writes no series; a catalog builds with the network off | N1 |
| R2 | Archiwista | Downloads into the raw root by its jobs and permissions; `series build` and `store catalog` leave its actions; series and catalogs read from Obserwator's data root; its stores configured with both roots | 1.5-2.5 | its e2e of a download and of the station card on split roots | R1, O1 |
| O1 | Obserwator | The data root (D2, D3): builders read a raw root and write the data root; the marker; readers and `command_for_version`; the one-off split of existing stores; ADR | 2-3 | the Python = CLI = REST = MCP contract tests; a data root built from a read-only raw root | R1 |
| O2 | Obserwator | Stored results (D7): `analyses build`, `analyses read`, `analyses export`; the defaults per station kind over the whole record (D12); provenance; the configured `hydrolog` program; the function that computes a chosen subset without storing it | 2-2.5 | results of the fixture stations equal Hydrolog's single calls byte for byte; a subset computed on the fly leaves the data root and the disk unchanged | O1, H4 |
| O3 | Obserwator | Harmonized exports: the stations as GeoJSON and CSV, a series as JSON and Parquet (its GUI plan, slice S0) | 2-2.5 | its GUI plan's acceptance of S0 | N1 |
| O4 | Obserwator | The GUI by its own plan (slices S1 to S7), with the station views by kind (D9), the analyses of O2, subsets the person chooses computed on the fly through Hydrolog's single calls (D7) and the hand-off of D8 | 17-22 | its GUI plan's acceptance; a flood quantile equal in both GUIs | O2, O3 |
| H5 | Hydrolog | „Wczytaj z Obserwatora” and the producer's numbers beside its own (D8) | 0.5-1 | a hand-off from Obserwator's fixture opens with equal quantiles | O4 |
| N2 | Nogat | The edges, summaries and routes of D11 active; the map; the public deployment's list; release-set pins | 0.5-1 | gate: `validate`, `map --check` | O2, O4 |
| A2 | the author | The hosts of the raw root with the data root's backup (Archiwista's) and of the production data root (Obserwator's), by D2; the first full download and the yearly refresh (D7); reviews and merges of every project's branch (DEV-3.3); later the VPS | — | the public GUI names a current series version | O1 |

In total about 38 to 52 sessions, about 17 to 21 on the critical path (N1, H1, H4, O2 and O4's own path). R1, O1 and O3 run beside Hydrolog's steps; O4's slices of the GUI shell, the map and the files start after O1 and O3 and take the analyses as O2 lands.

## Results

- 2026-11-13, N1 (branch `plan/station-data-and-analyses`): ECO-059 in `standards/DECISIONS.md`, amending ECO-054; in `ecosystem.yaml` the planned edges Obserwator → Archiwista (data, `store`, the raw root), Obserwator → Hydrolog (optional, `cli` and `file`) and the notes of Archiwista → Obserwator (B1) and Hydrolog → Obserwator (the batch reads the series export), with the planned items `archiwista-raw-root`, `obserwator-data` and `obserwator-analyses`, whose summaries say they are planned; the projects' own summaries change at N2, when the roles are in the code. `docs/ECOSYSTEM_MAP.md` regenerated. Obserwator's GUI plan points at this plan; Hydrolog's and Archiwista's plans will when they are written.

## Risks

| Risk | Effect | Mitigation |
|---|---|---|
| The store's split (D2) touches Archiwista's adapter and Retman's store commands | consumers break | one documented split, `obserwator.testing` fixtures for both roots, the consumers' contract tests before R1 lands |
| A refresh only once a year (D7) | a correction IMGW-PIB or ČHMÚ publishes mid-year shows only at the next refresh | the panel names the series version and its date; a refresh can be run by hand the same way |
| Hydrolog's catalog grows by about 20 to 25 commands | Hydrolog's catalog, its `AGENTS.md` budget and tests | grouped commands where one method serves many indices (the meteorological counts as one command with an index option); Hydrolog's own plan |
| Methods without a single standard (regime type, SPI fit, baseflow filter, dry-day threshold) | numbers that differ from a reader's handbook | each method named with its source in the result and the (i) text; the choice fixed in Hydrolog's plan |
| Hydrolog versions differ between its GUI and Obserwator's batch | the same input, different numbers | one Hydrolog version per deployment; results name it; the hand-off shows both |
| Annual extremes from two sources (F1) | the same station, two sets of maxima | the source named in every result; the hand-off carries the maxima used |
| Batch cost on the small VPS | slow first computation and yearly refresh | the batch runs where the raw root lives and the data root is copied to Obserwator's production host |
| A subset computed on the fly costs a Hydrolog call per request | slow answers on a small server | the defaults over the whole record are stored; on-the-fly calls limited in number and time, held in memory only (GUI plan D8) |
| Results computed from series later corrected | stale results | a result names its series version; `analyses build` recomputes for every new series version |

## Decided (2026-11-13)

The author's answers of [2026-11-13](#the-authors-answers-2026-11-13) to the open questions of this plan and of Obserwator's GUI plan:

1. **Download code** (question 1): B1. Obserwator's provider and download code stays Obserwator's library; Archiwista calls it into its raw root (D1, D5, R1).
2. **Where the roots live and their refresh** (question 2): the raw root in Archiwista; Archiwista also keeps a backup copy of the whole harmonized data root; the production data root in Obserwator (D2). Everything is computed once, at the start; new packages are downloaded once a year and the data root is rebuilt and recomputed; a subset a person chooses is computed on the fly and never stored, not cached to disk (D3, D7). Decided here, open to the author's veto: the deployment's roots start afresh with one full download, since `/mnt/magazyn/agent-tmp/archiwista-zespol/obserwator` (481 MB) mixes test data with IMGW-PIB series; the documented split (D2) stays for other existing stores.
3. **IMGW-PIB's warning and alarm levels** (question 3): dropped; no operational data are archived. A station's view shows ČHMÚ's thresholds and the characteristic levels only (D10, H3).
4. **Reference periods** (question 5): the whole record by default, adjustable by the person, with a note that 30 years is the recommended minimum (D12).
5. **XLSX** (question 1 of Obserwator's GUI plan): no; exports are CSV, JSON and Parquet (D13).

## Open question for the author

1. **IMGW-PIB's terms on the public instance** (question 4, „do sprawdzenia”). IMGW-PIB's notice reads „Do użytku prywatnego i badawczego; inne zastosowania wymagają sprawdzenia warunków IMGW-PIB, także wyjątków dla danych o wysokiej wartości.” (Obserwator `src/obserwator/messages/datasets.py:122-127`). Is serving IMGW-PIB series and analysis results to the Access audience within the terms? A research note follows; until it is answered the public instance stays behind Cloudflare Access.

## Not in this plan

Kartograf's data and roles; IMGW-PIB's hydrological phenomena and synoptic data; analyses across several stations (correlation, filling gaps, areal precipitation, which Hydrolog's `precip areal` already gives); runoff depth and specific runoff, which need catchment areas that no catalog holds; the GUI hub (stage 2 of the GUI platform); ČHMÚ's current data.
