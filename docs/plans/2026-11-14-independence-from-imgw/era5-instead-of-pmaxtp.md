# Design rainfall without IMGW-PIB: can Hydrograf replace PMAXTP with ERA5/ERA5-Land, CERRA and others?

Research of 2026-11-14 (Era5Research), translated from Polish for the plan [2026-11-14-independence-from-imgw.md](../2026-11-14-independence-from-imgw.md). Scope: research only, no code changes. Quotations of terms, laws and attribution lines stay verbatim in Polish.

**The author's priority:** free Hydrograf from IMGW-PIB and its terms, which do not allow commercial use of the service. Every option is therefore judged first by **commercial use (a paid service, selling the results of expert reports) without IMGW-PIB data**, and only then by quality.

Notation: [n] – a source from the list at the end; **[INFERENCE]** – my inference, not stated by the source. **Nothing in this report is legal advice**; legal assessments are a working reading of the texts, to be verified by a lawyer.

---

## 0. In short

1. **Licences.** ERA5, ERA5-Land, CERRA and CERRA-Land are under CC BY 4.0 since 2 July 2025: commercial use is allowed, with Copernicus attribution [L1, L2]. E-OBS_EU, EURADCLIM, the OPERA composites (from release 2025b) and KOSTRA-DWD-2020 are CC BY 4.0 too. **E-OBS for the whole of Europe is not** (non-commercial research and education only) [L6].
2. **PMAXTP.** The PMAXTP terms say nothing explicit about commercial purposes, but the general IMGW-PIB terms require an agreement for using information from the PSHM network „dla potrzeb działalności gospodarczej” (for business purposes), except for high-value datasets (HVD); PMAXTP is not on the Polish HVD list. Without an agreement with IMGW-PIB: commercially **no** [L8–L10] [INFERENCE].
3. **Correction.** Any correction of ERA5 against PMAXTP (multipliers, calibration, validation inside the product) carries the PMAXTP terms over. A correction against IMGW-PIB HVD data (station observations, validated climate data, radar) is commercially allowed but keeps IMGW-PIB as an attributed source. Without IMGW at all: KOSTRA-DWD (Germany), ČHMÚ PERUN (Czechia, licence to be confirmed), EURADCLIM/OPERA, published areal reduction factors (ARF).
4. **Science.** ERA5 is a cell average over ~0.25° (≈480 km² at 52°N) with parameterised convection and no assimilation of rainfall measurements. At two points with published PMAXTP values, ERA5 values (the PXR-2 dataset, 1979–2018) are: Warsaw 35–44% of PMAXTP for 1 h, 75–91% for 24 h, 80–104% for 72 h; Kłodzko 27–33%, 66–69%, 73–77% (§5.3). For 5–45 min ERA5 gives nothing (1 h step). ERA5-Land has the same rainfall, only interpolated to 0.1°.
5. **ERA5 alone will not replace PMAXTP** as design rainfall – it would under-size structures. A commercial version needs „open rainfall”: ERA5/CERRA plus a transfer to point scale determined without IMGW (KOSTRA/PERUN, EURADCLIM, ARF) or with published coefficients from a study (§3 „Research path”).
6. **Paths for a commercial version:** (A) open Copernicus rainfall + transfer from DE/CZ – without IMGW; (R) research path: a non-commercial, peer-reviewed study of ERA5 vs IMGW-PIB rain gauges that publishes a few coefficients the service applies to ERA5; (B) own DDF from IMGW-PIB HVD data (commercially allowed, but with IMGW attribution); (C) an agreement with IMGW-PIB on PMAXTP; (D) user rainfall („bring your own rainfall”). Recommendation: D at once, R as the basis of the default rainfall (with A as cross-validation), a written confirmation from IMGW-PIB before a commercial start.
7. **Apart from PMAXTP, Hydrograf uses no IMGW-PIB data** (no station data, hydro.imgw.pl, danepubliczne). Depending on IMGW: bootstrap step 6 and `precipitation_data`, the `pmaxtp_grid` fields in API responses, the attribution and regulamin („Dane IMGW-PIB … niezarobkowo”), the ready SFINCS result computed with PMAXTP rainfall, the `obserwator` dependency, documentation (§2.3).
8. **Plan in Nogat:** download – Obserwator (hydro-meteorological data; Kartograf sends meteorology to Obserwator), statistics – Hydrolog, consumption – Hydrograf (no runtime dependency on Obserwator), plan and `data_sources` – Nogat. Effort: D ≈ 1 week; A or R ≈ 6–10 weeks (R + review time); B ≈ 6–10 weeks + time for the request to IMGW.

---

## 1. Starting point

### 1.1 How Hydrograf uses PMAXTP today (code, branch `develop`, `aa975b0`)

- `backend/core/precipitation.py`: 16 durations 5 min–72 h × 27 probabilities 0.01–99.9% (432 scenarios). Catchment rainfall = Thiessen average of the grid points (ADR-069), or IDW from 4 points when the catchment boundary is unknown.
- `backend/scripts/preprocess_precipitation.py` (bootstrap step 6 „Opady IMGW”): Obserwator `fetch_pmaxtp` → API `powietrze.imgw.pl/tpmax-api`, POT method (`core/handoff.py: PMAXTP_METHOD = "POT"`), points every 2 km (`IMGW_GRID_SPACING_KM`, `IMGW_RATE_LIMIT_DELAY_S` in `core/config.py`), written to `precipitation_data` with source `IMGW_PMAXTP`.
- `backend/api/endpoints/hydrograph.py`: rainfall = PMAXTP × the user's ARF (no reduction by default); catchments up to 250 km² (README); 24 h and p = 1% by default (manual).
- Attribution: lines PS, PP, M, RK (`core/attribution.py`); in the regulamin the block `pmaxtp`; there is no `copernicus` block because CORINE is not used (ADR-085).

### 1.2 PMAXTP in brief [P1–P5]

- 100 rain gauges, 1986–2015 (denser in the mountains); 16 durations 5–4320 min; AMP and POT selection, POT threshold P_POTmin,t = 3.5·t^0.275 mm (t in min) [P2].
- Local probabilistic models at stations (fitted theoretical distributions), interpolated by residual kriging; 2592 maps (16 × 27 × 2 methods × 3 layers) [P1, P3, P4].
- Three layers: quantile, upper bound of the confidence interval (τα = 1, i.e. quantile + 1σ, 84.1% one-sided), estimation error [P2].
- Update (FEnIKS, IMGW-PIB with the Wrocław University of Science and Technology): data up to 2025, runs under RCP 4.5/8.5, a new platform [P5].
- The distribution details are in the monograph (PDF 47 MB – not downloaded, size limit). A secondary source [P6] describes the base procedure of PANDa and PMAXTP: Fréchet, gamma, GED, Gumbel, log-normal, Weibull distributions; MLE estimation; Anderson–Darling test.

---

## 2. Independence from IMGW-PIB

### 2.1 What the IMGW-PIB terms say (read 2026-11-14)

| Document | Text | Consequence |
|---|---|---|
| PMAXTP terms, klimat.imgw.pl/opady-maksymalne [P2] | ust. 1: source with the page address and the monograph; ust. 2: a note on processing; ust. 5: IMGW bears no liability; ust. 6: the monograph under CC BY 4.0. **Nothing on commercial purposes** – neither a ban nor a permission | attribution PS, PP, M, RK (Hydrograf has it) |
| IMGW-PIB data terms, danepubliczne.imgw.pl/regulations [L8] | §5 ust. 1: „Korzystający może używać nieodpłatnie udostępnionych danych do celów prywatnych, a w przypadku danych o wysokiej wartości w każdym celu. Jakikolwiek użycie danych w celach określonych w § 3 ust. 2 regulaminu wymaga podpisania umowy…” | non-HVD data: commercially only with an agreement |
| same | §3 ust. 1: „Nieodpłatnym dostępem nie są objęte przypadki udostępniania danych do celów, o których mowa w ust. 2, chyba że są to dane o wysokiej wartości.” §3 ust. 2: information „pochodzące z podstawowej sieci pomiarowo-obserwacyjnej […] państwowej służby hydrologiczno-meteorologicznej, dla potrzeb działalności gospodarczej lub dla celów […] planowania w gospodarowaniu wodami […] art. 317 ust. 1 Prawa wodnego” – an agreement | hydrological expert reports are named explicitly |
| same | §2 pkt 3: „cel działalności gospodarczej – […] w tym publikacja danych […] na stronach internetowych, zawierających reklamy”; §5 ust. 6: „Użycie danych udostępnionych nieodpłatnie w celach określonych w § 3 ust. 2 stanowi oszustwo w rozumieniu art. 286” of the Penal Code | high risk in a „grey zone” |
| Commission Implementing Regulation (EU) 2023/138, annex item 3 [L9]; the Polish HVD list [L10] | IMGW-PIB: station observations („full temporal resolution”), climate data – validated observations („daily validated hourly (and better temporal resolution) and daily average observations data; all digitised historical data”), warnings, radar (rainfall among others), NWP. Licence: CC0, CC BY 4.0 or equivalent, „allowing for unrestricted re-use”; attribution may be required | IMGW-PIB HVD data: commercially **yes**, with lines S (+P) |

Conclusion [INFERENCE]: PMAXTP is a derived product (modelled quantiles), not „validated observations”, and it is not on the HVD list. On a cautious reading, its use in business requires an agreement with IMGW-PIB (§8, biznes@imgw.pl). Hence the present statement in Hydrograf's footer and regulamin: „Serwis jest niekomercyjny i bezpłatny […] Dane IMGW-PIB są w nim wykorzystywane do celów niezarobkowych”, and Nogat's plan `2026-11-13-gui-terms` requires reviewing the regulamin before any paid service.

### 2.2 Licence table

| Source | Licence | Commercially? | Attribution text | Link |
|---|---|---|---|---|
| PMAXTP (IMGW-PIB) | PMAXTP terms + general IMGW-PIB terms | **NO without an agreement** (cautiously) | PS, PP, M, RK – as today in `core/attribution.py` | [P2], [L8] |
| IMGW-PIB, HVD data (station observations, validated climate data, radar, warnings, NWP) | HVD: CC BY 4.0 or equivalent | **YES** | „Źródłem pochodzenia danych jest Instytut Meteorologii i Gospodarki Wodnej – Państwowy Instytut Badawczy”; after processing also „Dane Instytutu Meteorologii i Gospodarki Wodnej – Państwowego Instytutu Badawczego zostały przetworzone” | [L8], [L10] |
| IMGW-PIB, other data (e.g. operational hydro.imgw.pl) | IMGW-PIB terms | NO without an agreement | S, P, link to the terms | [L8] |
| ERA5 (CDS) | CC BY 4.0 (since 02.07.2025) | **YES** | „Contains modified Copernicus Climate Change Service information [year]. Neither the European Commission nor ECMWF is responsible for any use that may be made of the Copernicus information or data it contains.” + citation: Hersbach et al., ERA5 hourly data on single levels from 1940 to present, DOI 10.24381/cds.adbb2d47 | [L1–L4] |
| ERA5-Land | CC BY 4.0 | **YES** | as above + dataset citation, DOI 10.24381/cds.e2161bac | [L2] |
| CERRA, CERRA-Land | CC BY 4.0 | **YES** | as above + DOI 10.24381/cds.622a565a / 10.24381/cds.a7f3cd0b | [L2] |
| C3S Extreme precipitation risk indicators | CC BY 4.0 | **YES** | as above + DOI 10.24381/cds.3a9c4f89 | [B2] |
| E-OBS (whole of Europe) | E-OBS product licence | **NO** (non-commercial research and education only) | „We acknowledge the E-OBS dataset and the data providers in the ECA&D project (https://www.ecad.eu)” + Cornes et al. 2018, doi:10.1029/2017JD028200 | [L6] |
| E-OBS_EU (EU + NO, CH, IS, UK) | CC BY 4.0 | **YES** | as above | [L6] |
| EURADCLIM v3 (KNMI) | CC BY 4.0, „No use limitations” | **YES** | KNMI dataset citation: doi:10.21944/1rxx-ev62 (1 h), doi:10.21944/hk1t-8p07 (24 h) | [A4] |
| OPERA composites (EUMETNET, ORD API) | CC BY 4.0 (from release 2025b) | **YES** | „EUMETNET OPERA”, CC BY 4.0 | [A12] |
| KOSTRA-DWD-2020 (Germany) | CC BY 4.0 (DWD CDC terms) | **YES** | Junghänel, Ostermöller, Deutschländer (2023), doi:10.5676/DWD/KOSTRA-DWD-2020 | [A10] |
| ČHMÚ, open data | CC BY 4.0 | **YES** | line C from Obserwator: „Źródło danych: Český hydrometeorologický ústav (ČHMÚ), https://opendata.chmi.cz, licencja CC BY 4.0 (…)” | [L11] |
| ČHMÚ PERUN, design rainfall | no licence stated on the page | **?** – confirm with ČHMÚ | – | [A8] |
| HydroRAIN (ČVUT, ÚFA, ČHMÚ) | no licence stated | **?** | – | [A9] |
| PXR (Courty et al., ready IDF from ERA5) | ODbL 1.0 | YES, but derived databases used publicly inherit ODbL (share-alike) | ODbL notice + „Generated using Copernicus Climate Change Service information [2019]” | [B1] |
| ERA5 mirrors: Earthmover Icechunk (AWS) | CC BY 4.0 | **YES** | per the registry's „How to Cite” | [E11] |
| ERA5 mirrors: Google ARCO-ERA5 | refers to the Copernicus licence | **YES** | C3S line | [E10] |
| Published ARF (FSR/FEH: Keers and Wescott 1977; DVWK 1984 after KZGW 2017) | formulas and values from the literature | **YES** (citation) | citation of the publication | [B9] |

Hydrograf's other sources, outside the scope of this research (per the READMEs of Hydrograf and Kartograf): SoilGrids and MZP of Wody Polskie – CC BY 4.0; GUGiK – „free reuse with attribution (Prawo geodezyjne i kartograficzne)”; OSM – ODbL. GUGiK's commercial status is worth confirming separately.

### 2.3 What else in Hydrograf depends on IMGW-PIB (grep of the code, without `.venv`)

PMAXTP is the only source of IMGW-PIB data; the plan `2026-11-13-provider-attribution` confirms it („Hydrograf has no other provider data”). Dependencies on PMAXTP:

1. **Data and processing:** `scripts/preprocess_precipitation.py`, step 6 in `scripts/bootstrap.py` („Opady IMGW”), `core/config.py` and `.env.example` (`IMGW_GRID_SPACING_KM`, `IMGW_RATE_LIMIT_DELAY_S`), the table `precipitation_data` (`IMGW_PMAXTP`), `scripts/analyze_watershed.py` (live `fetch_pmaxtp`).
2. **Computation and API:** `core/precipitation.py` (the sets of durations and p are PMAXTP's sets, `PmaxtpGridPointUnknown`), `api/endpoints/hydrograph.py` (design rainfall, `PmaxtpPoint`), `api/endpoints/watershed.py` and `core/network_delineation.py` (`thiessen_cells` – the field `pmaxtp_grid` in **every** catchment delineation response), `models/schemas.py` (`PmaxtpGridCell`, `pmaxtp_grid`, `derived_from: "pmaxtp"`), `core/handoff.py` (`pmaxtp_origin`, hand-off with `source: "pmaxtp"`), `core/messages.py`.
3. **Attribution and regulamin:** `core/attribution.py` (PS, PP, M, RK), `core/terms.py` (block `pmaxtp`), `api/endpoints/site.py` (PMAXTP lines always in the site's attribution), the footer and regulamin („Dane IMGW-PIB są w nim wykorzystywane do celów niezarobkowych”) in `frontend/index.html`, the manual and the kit `frontend/nogat/`.
4. **Analysis results:** `frontend/data/results/sfincs-kamiennik-24h-p1` (Hydraulik/SFINCS, „opad: IMGW-PIB (PMAXTP)”) and `core/analysis_results.py`.
5. **User series:** a hyetograph copied from PMAXTP (`derived_from = "pmaxtp"`) carries the PMAXTP terms.
6. **Package dependency:** `obserwator` in `backend/pyproject.toml` – used in Hydrograf only for PMAXTP.
7. **Interface and documentation:** `js/info-texts.js` (D and p defined by PMAXTP), labels „Opad PMAXTP”, the export „Punkty PMAXTP (GeoJSON)”, the manual, slides, PDF; tests (`pmaxtp_body`, `test_preprocess_precipitation.py`).

Hydrographs (Hydrolog: SCS-CN, UH, tc, AMC) use no IMGW-PIB data. References to IMGW warnings in the manual and regulamin are pointers, not data.

### 2.4 Bias correction: what carries the IMGW-PIB terms over and what does not

| ERA5 correction variant | Reference | Terms of the result | Commercially? |
|---|---|---|---|
| Multiplier or regression ERA5 → PMAXTP | PMAXTP | PMAXTP/IMGW terms | **NO without an agreement** – exclude |
| Quantile mapping to IMGW-PIB stations inside the service (a grid of corrections) | IMGW data (HVD or not) | attribution S/P; an agreement for non-HVD data | HVD: yes, but with IMGW in the attribution; the rest: no |
| A few published coefficients from a study of ERA5 vs IMGW-PIB rain gauges | a scientific publication | citation of the publication | **yes** [INFERENCE], see §3 |
| Transfer from KOSTRA-DWD (DE) and ČHMÚ PERUN (CZ) | DWD, ČHMÚ | CC BY 4.0 (PERUN to be confirmed) | **yes**, without IMGW |
| 2 km scale from EURADCLIM (2013–2023) or the OPERA composites | KNMI, EUMETNET | CC BY 4.0 | **yes** |
| Physical: inverse ARF (FSR/FEH) and the Hershfield factor | literature | formulas | **yes**, but removes only part of the error (§5.3) |
| Dynamical downscaling (2–3 km) from ERA5 | own computation | own | **yes**, but expensive |

Validation against PMAXTP is possible only as a non-commercial study (e.g. with a university) or with IMGW-PIB's consent; coefficients „learnt” on PMAXTP are a product developed using IMGW-PIB data [INFERENCE].

---

## 3. Research path

**Variant:** a non-commercial, published (preferably peer-reviewed, open-access) study comparing annual maxima of ERA5 (or CERRA) with IMGW-PIB rain gauges. Obserwator downloads the data, Hydrolog fits the distributions. The article publishes correction coefficients (e.g. per duration, per return period, possibly a function of region or elevation). The commercial Hydrograf then applies only ERA5 and the published coefficients.

### 3.1 What IMGW-PIB publishes on rainfall (server and formats read 2026-11-14)

| Dataset (danepubliczne.imgw.pl) | Step | Years | Rainfall field | In Obserwator |
|---|---|---|---|---|
| `dane_meteorologiczne/dobowe/opad` (rainfall posts) | day | 1950–2026 | `SMDB` – daily total [mm], status „Z” = accumulated rainfall | yes, `pl.imgw.meteo_precip_daily` (since 1950) |
| `dobowe/klimat` (climatological stations) | day | 1951–2026 | P [mm] | yes, `pl.imgw.meteo_climate_daily` |
| `dobowe/synop` | day | 1966–2026 | daily total | no („daily synoptic archives” unsupported) |
| `terminowe/synop` (hourly records) | 6 h | 1966–2026 | `WO6G` – „Opad za 6 godzin [mm]” | no |
| `terminowe/klimat` | observation terms | 1951–2026 | no rainfall field (format `k_t_format.txt`) | file download only |
| Current API `api/data/meteo` (~788 automatic stations) | 10 min | current value only | `opad_10min` | `current …` (live, no archive) |
| Current API `api/data/synop` (62 stations) | 1 h | current value only | `suma_opadu` | `current …` |
| 1-min/10-min archive (pluviographs, automatic stations; PMAXTP's base 1986–2015) | 1–10 min | – | – | **not published**; on request only (§1 ust. 4, §8) |

Conclusion: only daily totals (since 1950) and 6-hour totals (synop, since 1966) are public. A 1–12 h study needs a request for the 10-min or 1-min archive. The HVD annex covers „daily validated hourly (and better temporal resolution) […] observations data; all digitised historical data” [L9], so that archive should be released on HVD terms, i.e. for any purpose [INFERENCE – to be confirmed by IMGW-PIB].

### 3.2 Course of the study

1. Obserwator: daily posts (1950–), 6-h synop (new dataset `terminowe/synop`), the 10-min archive from the request; ERA5 from CDS/ARCO (a new provider, §8).
2. Hydrolog: rolling annual maxima for 1, 2, 3, 6, 12, 24, 48, 72 h (for 24–72 h from daily data with the Hershfield factor, as ČHMÚ does: 1.18 for totals ≤ 40 mm, 1.12 > 40 mm; 2 days 1.05 [A8]); GEV (L-moments), regional shape (ROI), bootstrap confidence intervals; the same for the ERA5 cells over the stations.
3. Coefficient k(D, T) = station quantile / ERA5 quantile, averaged regionally; fit of a parametric function, e.g. k = a·D^(−b)·(1 + c·z), possibly separately for „lowlands” and „mountains”.
4. Cross-validation without IMGW: KOSTRA-DWD (German border strip), PERUN (Sudetes, Beskids), EURADCLIM 1 h.
5. Open-access publication under CC BY 4.0, with IMGW-PIB lines S and P, a description of the data and the code (Hydrolog), without tables of station quantiles beyond what is needed to understand the result.

### 3.3 (1) What the IMGW-PIB terms say about derived results

- §2 pkt 4: „dane – wszelkiego rodzaju dane, produkty lub usługi, […] udostępniane przez Instytut […]”; §2 pkt 8: „korzystanie – pobranie lub otrzymanie dostępu, a także komercyjne lub niekomercyjne korzystanie z danych”.
- §2 pkt 2: „cel prywatny – użycie danych do celów prywatnych, niezarobkowych, w tym do celów prac magisterskich lub doktorskich”; §4 pkt 2: free access for universities and research institutes „na potrzeby […] badań naukowych i działalności dydaktycznej”.
- §5 ust. 3: attribution „na wszelkiego rodzaju pracach lub produktach, opracowanych z użyciem danych IMGW-PIB”; §5 ust. 4: „W przypadku przetworzenia danych […] na wszelkiego rodzaju pracach lub produktach, opracowanych z użyciem przetworzonych danych IMGW-PIB informacji: »Dane […] zostały przetworzone«”.
- §7 ust. 2 pkt 5: limitations „jeżeli prawa autorskie, prawa pokrewne, prawa do baz danych lub prawa własności przemysłowej przysługują podmiotom innym niż IMGW-PIB”.

The terms do not define „processing” or the line beyond which a result stops being „IMGW-PIB data”; they govern the attribution of works and products and the purpose of using the data. Working reading [INFERENCE]:
- **The article** is „a work developed using processed data” – it must carry S and P; it is non-profit research (§2 pkt 2), consistent with the terms.
- **A few published parameters** (e.g. 3–6 numbers of the function k) are a scientific finding; a service using them neither downloads nor releases IMGW-PIB data. Cautiously, the service should cite the article with the note „coefficients determined from IMGW-PIB data”.
- **A grid of corrections** (a value in every cell, in practice an interpolated station field) reproduces the stations' spatial information and is closer to „processed IMGW-PIB data” in the sense of §5 ust. 4. It is the same type of product as PMAXTP (kriging of stations). Do not publish it or apply it in the service.

### 3.4 (2) Facts and scientific findings vs the sui generis database right – general principles, not legal advice

- **Copyright** protects the expression, not facts: „nie są objęte ochroną odkrycia, idee, procedury, metody i zasady działania oraz koncepcje matematyczne” (art. 1 ust. 2¹ of the Polish Copyright Act). Numerical measurement results and derived coefficients are, as a rule, not works [INFERENCE]. The text and layout of an article may be protected, not the value of a coefficient.
- **The sui generis database right** (Directive 96/9/EC, art. 7; the Polish Act of 27 July 2001 on the protection of databases, art. 6) protects the maker of a database against extraction and re-utilisation of the whole or a **substantial part** of its contents (quantitatively or qualitatively), if obtaining, verifying or presenting it required substantial investment. Insubstantial parts may be used (art. 8 of the Directive), but not repeatedly and systematically against the normal exploitation of the database (art. 7(5)). Exception for illustration for teaching or scientific research, with the source indicated, to the extent justified by the non-commercial purpose (art. 9(b) of the Directive; similarly art. 8 of the Polish Act). In CJEU case law „extraction” also covers transferring contents after a critical assessment (C-304/07 Directmedia), and investment in creating the data themselves is not protected (C-203/02 BHB v William Hill).
- **The Open Data Directive 2019/1024**, art. 1(6): public-sector bodies do not exercise the sui generis right so as to prevent or restrict re-use beyond its limits; the IMGW-PIB terms invoke the national open-data act and the HVD regulation [L8, L9].
- For the research path [INFERENCE]: the study draws on a substantial part of the database, but for a research, non-commercial purpose, with the source indicated, and – if the data are HVD – for any purpose at all. A few parameters in the service are not an extraction or re-utilisation of a substantial part of the IMGW-PIB database. A dense grid of corrections or a table of station quantiles could be judged so. **These theses need a lawyer's assessment** (in particular whether a study done by a person who later runs a commercial service changes the assessment of its purpose; it is safer with a university as an „entitled body” of §4).

### 3.5 (3) A correction designed to minimise the dependency

1. **Few parameters:** one function k(D) = a·D^(−b), possibly with a return-period or elevation term – 3–6 numbers in total; no per-station values and no grids.
2. **Only IMGW-PIB HVD data** (daily posts, 6-h synop, the 10-min archive on HVD terms), **no PMAXTP** – PMAXTP is not HVD.
3. **Peer-reviewed open-access publication (CC BY 4.0)**, citing IMGW-PIB with lines S and P, with code and a method description; the coefficients are a scientific result with a DOI.
4. **Independent confirmation outside IMGW:** the same coefficients checked against KOSTRA-DWD and PERUN (and EURADCLIM for 1 h) – the service can then refer to the agreement with those sources.
5. **In the service:** ERA5 (CC BY 4.0) × the article's coefficients; Copernicus attribution + citation of the article (with a note on IMGW-PIB data, if IMGW-PIB asks for one).
6. **Versioning:** the coefficients as an explicit, versioned parameter (e.g. in Hydrolog), so that after an update of the study (or a move to ERA6) they can be replaced without a code change.

### 3.6 (4) Whether to ask IMGW-PIB for a written confirmation

**Yes, before a commercial start.** The cost is small (§9: an answer within 14 days, at most 2 months), and §5 ust. 6 threatens to qualify the use of free data for the purposes of §3 ust. 2 as „fraud”. The request (§8, biznes@imgw.pl) should ask:
1. whether the data used in the study (daily posts, 6-h synop, the 10-min/1-min archive) are high-value datasets in the sense of §2 pkt 5 and §5 ust. 1;
2. whether they will release the 10-min/1-min archive on HVD terms, in what format and for what fee (§10);
3. whether a few published correction coefficients, applied to ERA5 data in a commercial service, are „use of IMGW-PIB data” for the purposes of §3 ust. 2;
4. what attribution they expect in the article and in the service.

Without a confirmation: keep to the variant of §3.5 and keep path A (without IMGW) ready.

---

## 4. ERA5 and ERA5-Land – facts

| | ERA5 | ERA5-Land |
|---|---|---|
| Native resolution | ~31 km (TL639, 0.28125°) [E1] | ~9 km (TCo1279) [E2] |
| Grid in CDS | 0.25° | 0.1° |
| Step and period | 1 h; since 01.1940, ~5 days latency (ERA5T) [E1, E7] | 1 h; since 01.1950, 2–3 months latency (+ ERA5-Land-T) [E2] |
| Origin of rainfall | short-range forecasts from 06 and 18 UTC (in CDS steps 1–12 h); rain gauges are not assimilated (except the US radar composite since 2009) [E1, B3] | ERA5 rainfall linearly interpolated (triangular grid) from 31 to 9 km; elevation correction only for temperature, humidity and pressure [E2, E4] |
| `tp` | total over the hour ending at the validity time, in metres (×1000 → mm) [E5] | total from 00 UTC to the given hour, daily reset – must be differenced; 00 UTC = total of the previous day [E5] |
| Value for extremes | – | none beyond ERA5; the denser grid gives a false impression of resolution [INFERENCE] |

**Access:** CDS API (account, key, request cost limits, lower for NetCDF than GRIB) [E6]; CDS „ERA5 hourly time-series” – a point or an area up to 5° × 5° [E7]; ECMWF ARCO Zarr (geo-chunked for long series, CDS key) [E7], also ERA5-Land ARCO with de-accumulation [E8]; Google ARCO-ERA5 (`gs://gcp-public-data-arco-era5`, anonymous, but chunk = 1 hour × the whole globe, so inefficient for time series) [E10]; Earthmover Icechunk on AWS (anonymous, CC BY 4.0, 1940–2025, quarterly, „temporal” layout; presence of `tp` to be confirmed) [E11].

**Volume** (float32, uncompressed; computed):

| Domain | ERA5 0.25°, 1940–2025 (753 888 h) | ERA5-Land 0.1°, 1950–2025 (666 216 h) |
|---|---|---|
| Europe 34–72°N, 25°W–45°E | 42 993 cells → 130 GB (GRIB 16-bit ≈ 65 GB) | 267 081 → 712 GB |
| PL + CZ with a margin 48.5–55°N, 12–24.25°E | 1 350 → 4.1 GB | 8 118 → 21.6 GB |
| Poland (rectangle) | 1 050 → 3.2 GB | 6 283 → 16.7 GB |

The result is small: annual maxima (86 years × 10 durations) ≈ 4.6 MB for PL+CZ and ≈ 150 MB for Europe; quantile grids (10 durations × 27 p × 3 layers) ≈ 4.4 MB and ≈ 140 MB; GEV parameters with confidence intervals alone – a few MB.

**ERA6:** 14 km, from at least 1950; the first streams (2007+) at the end of 2027 [E9]. The pipeline should be designed from the start independently of the reanalysis version; convection at 14 km will still be parameterised [INFERENCE].

---

## 5. ERA5 biases for extremes

### 5.1 Mechanisms

1. **Scale:** a 0.25° cell ≈ 477 km² at 52°N, and the effective resolution is coarser than the grid step [B4]. ARF per FSR/FEH (Keers and Wescott 1977 [B9]) for 477 km²: 0.70 (1 h), 0.77 (2 h), 0.80 (3 h), 0.85 (6 h), 0.89 (12 h), 0.91 (24 h), 0.93 (48 h), 0.94 (72 h). For a 250 km² catchment (Hydrograf's upper limit): 0.75 (1 h), 0.93 (24 h).
2. **Model:** convection parameterised at 31 km underestimates short, intense rainfall [B1, B2].
3. **No assimilation of rainfall measurements**, too many days with light rain [B3, B4, B6].
4. **Discretisation:** a 1 h maximum from clock-hour totals underestimates the true 60-min maximum (Hershfield factor ~1.13–1.14 for a single interval [B10]).
5. **Inhomogeneity in time:** from 17 thousand observations a day (1940) to 25 million (2022) [E12] – homogeneity must be tested; consider starting from 1950 or 1979.

### 5.2 Literature

| Work | Area | Durations | Result |
|---|---|---|---|
| Courty et al. 2019 [B1] | UK, MIDAS rain gauges | 1–360 h | median ERA5 error: approx. −45…−65% for 1 h, approx. −20…−35% for 24 h, 0…−15% for 120–360 h (read off a chart) |
| C3S, Extreme precipitation risk indicators [B2] | Europe | 24 h, T = 1–100 years | from ERA5 „about one third lower” than from ECA&D stations, more for T = 100 than for T = 1; E-OBS also strongly underestimated |
| Lavers et al. 2022 [B3] | global, 5637 stations | 24 h | ERA5 does not reproduce the highest totals; wet bias |
| Bandhauer et al. 2022 [B4] | Alps, Carpathians, Fennoscandia | 24 h | fields too smooth, high quantiles underestimated |
| Rivoire et al. 2021 [B5] | Europe vs E-OBS | 24 h | good agreement with E-OBS, e.g. over Germany – much of the difference against stations is scale |
| Paluba et al. 2025 [B6] | Czechia | 24 h | ERA5-Land overestimates annual totals by 15–35%, underestimates days > 5 mm |
| Szturc et al. 2025 [B7] | Poland, flood of IX 2024 | 1 h, 24 h | field pattern correct, values underestimated; for hours > 5 mm correlation with RainGRS ≤ 0.10 |
| Wood et al. 2025 [B8] | Switzerland | day | CERRA clearly better than ERA5/ERA5-Land |
| Lengfeld et al. 2020 [B11] | Germany, radar | 1–6 h | the rain-gauge network captured 17.3% of hourly heavy events (81.8% of daily ones) |

I found no work comparing 1–72 h annual maxima from ERA5 and from IMGW-PIB rain gauges for the whole of Poland – a gap the research path (§3) would fill.

### 5.3 Comparison with PMAXTP at two points (published numbers)

ERA5: the PXR-2 v2.0.0 dataset (Courty et al., Zenodo 10.5281/zenodo.2616438, ODbL) – GEV parameters (μ, σ; κ = −0.114 fixed; PWM) of annual maxima of ERA5 rolling totals 1979–2018 on the 0.25° grid [B1]. I read only the cells nearest the points through HTTP Range requests (~3.6 KB of values, without downloading ERA5). Depth = (μ + σ·y_T)·D, y_T = (1 − (−ln(1 − 1/T))^κ)/κ. PMAXTP (POT, quantiles): Warszawa-Bielany from [P3], Kłodzko from [P2].

**Warszawa-Bielany** (cell 52.25°N 21.00°E), mm:

| p | | 1 h | 3 h | 6 h | 12 h | 24 h | 48 h | 72 h |
|---|---|---|---|---|---|---|---|---|
| 50% | ERA5 | 6.1 | 12.1 | 17.4 | 23.1 | 28.8 | 36.2 | 40.7 |
| | PMAXTP | 17.4 | 22.9 | 27.3 | 32.4 | 38.6 | 45.9 | 50.7 |
| | ERA5/PMAXTP | 0.35 | 0.53 | 0.64 | 0.71 | 0.75 | 0.79 | 0.80 |
| 10% | ERA5 | 10.5 | 19.7 | 26.4 | 35.9 | 46.3 | 58.3 | 67.4 |
| | PMAXTP | 25.9 | 33.8 | 39.9 | 47.2 | 55.7 | 65.8 | 72.6 |
| | ERA5/PMAXTP | 0.41 | 0.58 | 0.66 | 0.76 | 0.83 | 0.89 | 0.93 |
| 2% | ERA5 | 15.2 | 27.8 | 36.1 | 49.7 | 65.2 | 82.1 | 96.0 |
| | PMAXTP | 34.6 | 44.6 | 52.3 | 61.3 | 71.9 | 84.3 | 92.5 |
| | ERA5/PMAXTP | 0.44 | 0.62 | 0.69 | 0.81 | 0.91 | 0.97 | 1.04 |

**Kłodzko** (cell 50.50°N 16.50°E), mm:

| p | | 1 h | 2 h | 3 h | 6 h | 12 h | 24 h | 48 h | 72 h |
|---|---|---|---|---|---|---|---|---|---|
| 50% | ERA5 | 5.8 | 9.6 | 12.3 | 17.5 | 24.2 | 32.5 | 42.4 | 47.0 |
| | PMAXTP | 21.4 | 25.5 | 28.3 | 33.7 | 40.1 | 47.8 | 56.9 | 63.0 |
| | ERA5/PMAXTP | 0.27 | 0.38 | 0.43 | 0.52 | 0.60 | 0.68 | 0.74 | 0.75 |
| 10% | ERA5 | 9.2 | 15.5 | 20.2 | 28.0 | 36.8 | 49.9 | 67.4 | 75.6 |
| | PMAXTP | 30.2 | 36.6 | 41.0 | 49.8 | 60.4 | 73.3 | 88.9 | 99.5 |
| | ERA5/PMAXTP | 0.30 | 0.42 | 0.49 | 0.56 | 0.61 | 0.68 | 0.76 | 0.76 |
| 2% | ERA5 | 12.8 | 21.9 | 28.7 | 39.1 | 50.3 | 68.6 | 94.2 | 106.2 |
| | PMAXTP | 38.8 | 48.1 | 54.5 | 67.5 | 83.6 | 103.6 | 128.4 | 145.5 |
| | ERA5/PMAXTP | 0.33 | 0.46 | 0.53 | 0.58 | 0.60 | 0.66 | 0.73 | 0.73 |

PMAXTP values in the tables – Źródłem pochodzenia danych jest Instytut Meteorologii i Gospodarki Wodnej – Państwowy Instytut Badawczy, dane pochodzą ze strony https://klimat.imgw.pl/opady-maksymalne. Dane Instytutu Meteorologii i Gospodarki Wodnej – Państwowego Instytutu Badawczego pochodzące ze strony https://klimat.imgw.pl/opady-maksymalne zostały przetworzone. „Modele probabilistyczne opadów maksymalnych o określonym czasie trwania i prawdopodobieństwie przewyższenia – Projekt PMAXTP”, red. Bogdan Ozga-Zieliński, Instytut Meteorologii i Gospodarki Wodnej – Państwowy Instytut Badawczy, Warszawa 2022. Regulamin danych PMAXTP: https://klimat.imgw.pl/opady-maksymalne. ERA5 values: contains data from PXR-2 (Courty et al. 2019) under the ODbL v1.0 licence; Generated using Copernicus Climate Change Service information [2019].

Observations:
- The ratio grows with duration. After removing the scale effect (dividing by the cell's ARF, for 1 h × 1.13), for p = 10% what remains is: Warsaw 0.65 (1 h), 0.72 (3 h), 0.78 (6 h), 0.86 (12 h), 0.91 (24 h), 0.95 (48 h), 0.98 (72 h); Kłodzko 0.49, 0.55 (2 h), 0.61, 0.66, 0.69, 0.75, 0.81, 0.80. In the lowlands for ≥ 48 h the difference is mainly scale; for short durations and in the mountains a large model error remains.
- Neighbouring cells give almost the same (1 h, p = 10%: Warsaw 9.6–10.5 mm, Kłodzko 9.2–9.4 mm) – ERA5 lacks the spatial structure PMAXTP shows.
- PMAXTP's POT threshold (3.5·t^0.275): 10.8 mm (1 h), 14.6 mm (3 h), 25.9 mm (24 h). The median of ERA5 annual maxima in Warsaw for 1–3 h (6.1 and 12.1 mm) lies below the threshold – PMAXTP-style POT does not work on ERA5 for short durations.
- Caveats: different periods (1979–2018 vs 1986–2015), AMS and GEV with fixed κ vs POT and PMAXTP's distributions; for p = 50% POT usually gives more than AMP, for p < 50% the two methods are considered comparable [P3]. This is an order-of-magnitude comparison, not a validation.

---

## 6. Method sketch (variant A, without IMGW)

1. **Data:** ERA5 `tp`, 1 h, 0.25°, PL + CZ + a German strip (to overlap KOSTRA), 1950–2025, final ERA5 only (no ERA5T); alternatively CERRA (hourly totals from 1–6 h forecasts, since 1984) [A2].
2. **Maxima:** rolling totals (cumsum) for D = 1, 2, 3, 6, 12, 18, 24, 36, 48, 72 h, annual maximum with its date; homogeneity and Mann–Kendall tests (Hydrolog has them).
3. **Distribution:** GEV from L-moments; Gumbel as a special case; regional shape (ROI, as ČHMÚ [A8] and C3S [B2]); DDF consistency by scaling the parameters with D; confidence intervals by block bootstrap over years (upper bound = quantile + 1σ, as in PMAXTP).
4. **Transfer to point scale without IMGW:** a function R(D, T, x) = KOSTRA/PERUN point value ÷ ERA5 quantile, x = elevation, mean annual rainfall (ERA5 or E-OBS_EU), continentality; „leave-region-out” validation; check of short durations against EURADCLIM 1 h (2013–2023) with ARF to point.
5. **5–45 min:** DDF shape P(D)/P(60 min) from KOSTRA/PERUN – large uncertainty; flag explicitly.
6. **Result:** GEV parameters with confidence intervals per cell → quantiles for Hydrograf's durations and p (p ≥ 1%, because KOSTRA/PERUN stop at 100 years).
7. **Cost:** for PL+CZ a read of ~4 GB, rolling totals ~10¹⁰ additions (seconds to minutes), ~13.5 thousand GEV fits with bootstrap (minutes); Europe ~30× more, I/O the bottleneck.
8. **Hydrolog's gaps:** no rolling totals for hourly series (there are 1–10-day ones from daily data), no Gumbel or GPD as models, no confidence intervals, grid mode, regional model or DDF, no NetCDF/Zarr input. Present: GEV/LN/P3/Weibull with L-moments and MLE, homogeneity tests, Mann–Kendall.

---

## 7. Alternatives (first: commercially?)

| Product | Commercially | Coverage | Durations | Notes |
|---|---|---|---|---|
| CERRA [A2] | yes | Europe 5.5 km, since 09.1984 | ≥ 1 h | better rainfall than ERA5 [B8]; still a model |
| CERRA-Land [A3] | yes | 5.5 km, daily rainfall analysis with rain gauges | ≥ 24 h | a good basis for 24–72 h |
| E-OBS_EU [L6] | yes | 0.1°/0.25°, daily, since 1950 | ≥ 24 h | extremes underestimated, depending on station density [B2] |
| EURADCLIM v3 [A4] | yes | 2 km, 1 h and 24 h, 2013–2023, covers Poland | 1 h, 24 h | too short for p = 1% on its own; good for scale and the spatial pattern |
| OPERA composites [A12] | yes | Europe, archive since 2011 (announced) | 1 h | raw radar, needs corrections |
| KOSTRA-DWD-2020 [A10] | yes | Germany, 5 km, 1951–2020 | 22 durations 5 min–7 days, 9 return periods 1–100 years | the reference atlas; material for a transfer to western Poland |
| ČHMÚ PERUN [A8] | ? (licence to be confirmed) | 164 CZ stations, 1951–2022, GEV + ROI; 1 km rasters for 1, 6, 24 h | 5 min–72 h, 0.5–100 years | the best reference for Czechia and the Sudetes |
| HydroRAIN [A9] | ? | Czechia, methodology certified 2023 | 6 h storms, N = 2–100 years | WMS/WPS services |
| C3S Extreme precipitation indicators [B2] | yes | ERA5 0.25°, E-OBS 0.1°, ECA&D; 1989–2018 | 24 h, T = 5–100 | ready 24 h return levels |
| PXR [B1] | yes (ODbL) | ERA5 0.25°, 1979–2018 | 1–360 h | ready IDF from ERA5; share-alike |
| ERA6 [E9] | yes (CC BY 4.0 expected) | 14 km, from ≥ 1950; from the end of 2027 | 1 h | ERA5's successor |
| IMGW-PIB HVD [L8–L10] | yes, with IMGW attribution | stations, radar | daily public; sub-daily on request | path B / R |
| PMAXTP [P2] | not without an agreement | Poland | 5 min–72 h | the national standard; FEnIKS update [P5] |

---

## 8. Recommendation

**Legally:** Copernicus (ERA5, ERA5-Land, CERRA, CERRA-Land) – yes, with attribution; PMAXTP – not in business without an agreement; IMGW-PIB HVD data – yes, with IMGW attribution.

**Scientifically:** ERA5 alone is not design rainfall (underestimated by 55–70% for 1 h and 10–35% for 24 h at the tested points); after the scale correction (ARF, Hershfield) a model error remains that depends on duration and relief. It needs a correction determined on point data and an explicit uncertainty.

**Practically (paths):**
- **D – user rainfall:** Hydrograf does not supply design rainfall; the user enters their own (the own-series field already exists). To do: remove PMAXTP from the commercial service, including copying the PMAXTP hyetograph. Whether processing PMAXTP values entered by the user in a paid service is safe – to be assessed legally.
- **R – research path (§3):** default rainfall = ERA5 × published coefficients; the best compromise of quality and independence, if IMGW-PIB confirms the HVD status of the data.
- **A – transfer from DE/CZ without IMGW (§6):** fully without IMGW; „screening” quality; good as a cross-validation of R.
- **B – own DDF from IMGW-PIB HVD data:** quality close to PMAXTP, commercially allowed, but with IMGW-PIB attribution and a dependency on the release of the 10-min archive.
- **C – an agreement with IMGW-PIB on PMAXTP:** the best quality; the dependency and the cost remain.

Recommendation: **D at once; R as the target default rainfall, with A as an independent check; a written question to IMGW-PIB (§3.6) before a commercial start; C only if clients require PMAXTP.** Label ERA5 rainfall in the service as „areal rainfall from a reanalysis, corrected” with an uncertainty interval; do not combine it with the user's ARF (double reduction).

**Effort (estimate [INFERENCE]):** D – 3–5 person-days (Hydrograf: removing PMAXTP from the pipeline, API and UI, regulamin, documentation, tests; recomputing or removing the SFINCS result). R – 6–10 weeks of work + review time and IMGW-PIB's answer. A – 6–10 weeks (shared in part with R). B – 6–10 weeks + 14 days to 2 months for the request.

**Plan in Nogat (HUB-5.2: producers first):**
1. Nogat: the plan; `ecosystem.yaml` → `data_sources` (HUB-2.7): `c3s` (CC BY 4.0), `knmi` (EURADCLIM), `dwd` (KOSTRA), possibly `chmi-perun`; the C3S attribution lines in the standard next to PS/PP/M/RK; a change of the statement „Serwis jest niekomercyjny…” in the regulamin kit for commercial instances.
2. Obserwator: a Copernicus C3S provider and the dataset `eu.c3s.era5_tp` (cell series as „virtual stations” in the Parquet store, a CC BY 4.0 sidecar, ECMWF ARCO with the CDS key in the configuration or Earthmover anonymously); the IMGW dataset `terminowe/synop` (6-h rainfall, since 1966) and handling of the 10-min archive from the request – for path R/B.
3. Hydrolog: `stats duration-maxima` (rolling totals from hourly series), `stats ddf` (GEV/Gumbel/GPD, regional shape, bootstrap, DDF, grid mode), application of versioned correction coefficients; result schemas.
4. Study and validation (R, A): ERA5 vs IMGW-PIB rain gauges (HVD), KOSTRA, PERUN, EURADCLIM; publication.
5. Hydrograf (last): a new source in `precipitation_data` (e.g. `ERA5_DDF`), a `copernicus` block in `core/terms.py`, C3S lines in `core/attribution.py` and the hand-off, renaming the `pmaxtp_*` fields (an API version), removing the `obserwator` dependency (files from Hydrolog instead of an import), durations only ≥ 1 h from ERA5 (shorter ones explicitly from the DDF), p ≥ 1%, documentation and CHANGELOG.
6. Kartograf: no changes (geodata; meteorology belongs to Obserwator).

---

## 9. Limits of this research

- I did not download ERA5 (no CDS credentials; as instructed). The comparison in §5.3 rests on the published PXR-2 dataset (~3.6 KB of values read through HTTP Range).
- I did not download the PMAXTP monograph (PDF 47 MB); the methodology is described from the PMAXTP page and secondary sources.
- The licences of PERUN and HydroRAIN are unconfirmed; the presence of `tp` in Earthmover Icechunk is unconfirmed.
- Values read off the chart of Courty et al. are approximate.
- The legal assessments (§2, §3) are a working reading of the terms, directives and acts, not legal advice; the principles of §3.4 are given from memory of the law, without reading the acts in that session – to be verified.

---

## Sources

**Hydrograf and the ecosystem (local files)**
- [H1] Hydrograf: `README.md` (Data and licensing), `backend/core/precipitation.py`, `backend/core/attribution.py`, `backend/core/terms.py`, `backend/api/endpoints/hydrograph.py`, `backend/scripts/preprocess_precipitation.py`, `backend/scripts/bootstrap.py`, `backend/core/handoff.py`, `backend/models/schemas.py`, `backend/pyproject.toml`, `frontend/index.html`, `frontend/data/results/index.json`, `docs/decisions/0085-…md`.
- [H2] Hydrolog: `src/hydrolog/statistics/high_flows.py` (`FloodFrequencyAnalysis`).
- [H3] Obserwator: `src/obserwator/datasets.py`, `src/obserwator/messages/legal.py`, `src/obserwator/fetch.py`.
- [H4] Nogat: `standards/ECOSYSTEM_HUB.md` (HUB-2.7, HUB-5.2); `docs/plans/2026-11-13-provider-attribution.md`, `2026-11-13-gui-terms.md` (worktree `nogat-admin`); Kartograf `README.md`.

**PMAXTP**
- [P1] IMGW-PIB (2022): PMAXTP monograph, https://www.imgw.pl/sites/default/files/2022-12/imgw-pib-monografia_modele-probabilistyczne-opadow-maksymalnych.pdf (CC BY 4.0).
- [P2] PMAXTP – glossary and terms: https://klimat.imgw.pl/opady-maksymalne; Kaźmierczak et al. (2025), Rocznik Ochrona Środowiska 27, 13–18, doi:10.54740/ros.2025.002 (values for Kłodzko).
- [P3] Barszcz, Kaznowska, Wasilewicz (2024), Przegląd Geograficzny 96(4), 473–494, doi:10.7163/PrzG.2024.4 (values for Warszawa-Bielany).
- [P4] IMGW-PIB, Obserwator (21.12.2022): https://obserwator.imgw.pl/2022/12/21/najnowszy-projekt-imgw-pib-odpowiedzia-na-zagrozenia-opadowe/
- [P5] IMGW-PIB: the FEnIKS project, https://imgw.pl/projekt-uaktualnienie-i-rozwoj-atlasu-opadow-natezen-miarodajnych-pmaxtp-z-dofinansowaniem-z-programu-feniks/
- [P6] Wdowikowski et al. (2025), Water 17(11), 1673, doi:10.3390/w17111673.

**ERA5 and ERA5-Land**
- [E1] ERA5: data documentation, https://confluence.ecmwf.int/spaces/CKB/pages/76414402/ERA5+data+documentation
- [E2] ERA5-Land: data documentation, https://confluence.ecmwf.int/spaces/CKB/pages/140385202/ERA5-Land+data+documentation
- [E4] Muñoz-Sabater et al. (2021), ESSD 13, 4349–4383, doi:10.5194/essd-13-4349-2021.
- [E5] Conversion table for accumulated variables, https://confluence.ecmwf.int/spaces/CKB/pages/197702790
- [E6] Limitation change on netCDF ERA5 requests, https://forum.ecmwf.int/t/limitation-change-on-netcdf-era5-requests/12477
- [E7] ERA5 hourly ARCO PUG, https://confluence.ecmwf.int/spaces/CKB/pages/505390919 ; ERA5 hourly time-series PUG, https://confluence.ecmwf.int/pages/viewpage.action?pageId=627854119
- [E8] ERA5-Land hourly ARCO PUG, https://confluence.ecmwf.int/spaces/CKB/pages/536218894
- [E9] ECMWF Newsletter 188: ERA6 reanalysis is in production, https://www.ecmwf.int/en/newsletter/188/news/era6-reanalysis-production
- [E10] Google ARCO-ERA5, https://github.com/google-research/arco-era5
- [E11] Icechunk ERA5 (Earthmover), https://registry.opendata.aws/earthmover-era5/
- [E12] Soci et al. (2024), QJRMS, doi:10.1002/qj.4803.

**Licences and law**
- [L1] CC-BY licence to replace Licence to use Copernicus Products on 02 July 2025, https://forum.ecmwf.int/t/cc-by-licence-to-replace-licence-to-use-copernicus-products-on-02-july-2025/13464
- [L2] CDS STAC catalogue (field `license` = CC-BY-4.0 for ERA5, ERA5-Land, CERRA, CERRA-Land), https://cds.climate.copernicus.eu/api/catalogue/v1/collections/reanalysis-era5-single-levels
- [L3] How to acknowledge and cite a CDS catalogue entry, https://confluence.ecmwf.int/spaces/CKB/pages/197704114
- [L4] Use Case 2: ERA5 hourly data on single levels, https://confluence.ecmwf.int/spaces/CKB/pages/222493847
- [L6] E-OBS and E-OBS_EU product licences (PDF from the CDS page of the dataset `insitu-gridded-observations-europe`).
- [L8] IMGW-PIB data terms (Regulamin udostępniania danych IMGW-PIB), https://danepubliczne.imgw.pl/regulations
- [L9] Commission Implementing Regulation (EU) 2023/138, https://eur-lex.europa.eu/eli/reg_impl/2023/138/oj
- [L10] List of HVD datasets with their providers in Poland, https://cms.dane.gov.pl/documents/175/
- [L11] ČHMÚ, open data CC BY 4.0 (line C in Obserwator; https://opendata.chmi.cz).
- Acts for §3.4 (not verified in that session): Directive 96/9/EC (art. 7–9), https://eur-lex.europa.eu/eli/dir/1996/9/oj ; the Polish Act of 27 July 2001 on the protection of databases; the Polish Copyright Act (art. 1 ust. 2¹); Directive (EU) 2019/1024 (art. 1(6)), https://eur-lex.europa.eu/eli/dir/2019/1024/oj ; CJEU C-203/02, C-304/07.

**ERA5 biases**
- [B1] Courty et al. (2019), Environ. Res. Lett. 14, 084045, doi:10.1088/1748-9326/ab370a; preprint https://eartharxiv.org/repository/view/1113/ ; PXR: doi:10.5281/zenodo.2616438 (ODbL).
- [B2] C3S Extreme precipitation risk indicators – PUG, https://confluence.ecmwf.int/spaces/CKB/pages/283558162
- [B3] Lavers et al. (2022), QJRMS, doi:10.1002/qj.4351.
- [B4] Bandhauer et al. (2022), Int. J. Climatol., doi:10.1002/joc.7269.
- [B5] Rivoire et al. (2021), Earth and Space Science, doi:10.1029/2020EA001633.
- [B6] Paluba et al. (2025), Big Earth Data, doi:10.1080/20964471.2025.2592444.
- [B7] Szturc et al. (2025), HESS 29, 5405, doi:10.5194/hess-29-5405-2025.
- [B8] Wood et al. (2025), HESS 29, 4153, doi:10.5194/hess-29-4153-2025.
- [B9] Kjeldsen (2007), FEH Supplementary Report 1 (ARF after Keers and Wescott 1977), https://nora.nerc.ac.uk/id/eprint/2637/
- [B10] Mazzoglio et al. (2024), Proc. IAHS 385, 147–153, doi:10.5194/piahs-385-147-2024.
- [B11] Lengfeld et al. (2020), Environ. Res. Lett., doi:10.1088/1748-9326/ab98b4.

**Alternatives**
- [A2] CERRA – PUG, https://confluence.ecmwf.int/spaces/CKB/pages/272323672 ; Ridal et al. (2024), QJRMS, doi:10.1002/qj.4764.
- [A3] CERRA-Land, CDS page `reanalysis-cerra-land`.
- [A4] EURADCLIM v3, https://dataplatform.knmi.nl/dataset/rad-opera-24h-rainfall-accumulation-euradclim-3-0 ; Overeem et al. (2023), ESSD 15, 1441, doi:10.5194/essd-15-1441-2023.
- [A8] ČHMÚ PERUN: https://www.perun-klima.cz/srazky/ ; report https://www.perun-klima.cz/results/navrhSrazekZprava.pdf ; 1 km rasters doi:10.57680/asep.0619880.
- [A9] HydroRAIN, https://rain.fsv.cvut.cz/webapp2/
- [A10] KOSTRA-DWD-2020, doi:10.5676/DWD/KOSTRA-DWD-2020 ; DWD CDC terms: https://opendata.dwd.de/climate_environment/CDC/Terms_of_use.pdf
- [A12] EUMETNET Open Radar Data – HVD compliance summary, https://eumetnet.github.io/openradardata-documentation/ORD_HVD_summary/
