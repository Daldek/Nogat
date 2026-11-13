# Plan: the providers' attribution in every product

Approved: 2026-11-13, the author's order in session (attribution MUST be in every product)

Amended: 2026-11-13, the author's principle „Tam, gdzie się da, odsyłamy do regulaminu dostawcy danych. Treści w naszych produktach mają być ograniczone do minimum.”, recorded as ECO-065: the notice N (our summary of the terms, which also mis-stated §3 ust. 2) and the line H are dropped; `terms_notice` holds only the links RD, RH, RK, which now name the terms they open; no product restates a provider's terms. The tables below are amended; each project's migration is in „Amendment: minimal provider texts” below.

Status: step 1 (Nogat) done 2026-11-13 on branch `fix/provider-attribution`; steps 2 to 7 in each project's own branch `fix/provider-attribution`; no merges, tags or releases.

Requirements: DEV §20 and ECO-060 (added by step 1), DEV-15.5, DEV-15.6, DEV-19.16, AGI-4.1, HUB-5.2 (producers before consumers), DEV-17.5.

## Goal

Every product of the ecosystem that contains data of IMGW-PIB or ČHMÚ, or results derived from them, carries the lines the providers' terms prescribe, verbatim, where a person or a program meets the data. Use is non-commercial.

## Verified requirements (read 2026-11-13)

| Source | Text | Consequence |
|---|---|---|
| IMGW-PIB terms, https://danepubliczne.imgw.pl/regulations §5 ust. 3 | „Udostępnienie i korzystanie z danych następuje pod warunkiem wskazania źródła pochodzenia danych, poprzez umieszczenie przez korzystającego na wszelkiego rodzaju pracach lub produktach, opracowanych z użyciem danych IMGW-PIB informacji: „Źródłem pochodzenia danych jest Instytut Meteorologii i Gospodarki Wodnej – Państwowy Instytut Badawczy”.” | S on every product |
| same, §5 ust. 4 | „W przypadku przetworzenia danych przez korzystającego, obok wskazania źródła ich pochodzenia, jak w ust. 1, należy również wskazać na fakt przetworzenia danych, poprzez umieszczenie … informacji: „Dane Instytutu Meteorologii i Gospodarki Wodnej – Państwowego Instytutu Badawczego zostały przetworzone”.” | S and P on every processed product |
| same, §5 ust. 1, §2 pkt 3 | free use for private (non-profit) purposes, any purpose for high-value data; a website with advertising is business use | no line of ours: RD links the terms (ECO-065; the notice N that summarised them is gone) |
| PMAXTP terms (relayed verbatim by the author), ust. 1 | „…pod warunkiem wskazania źródła pochodzenia danych, w tym wskazania na monografię pt. „Modele probabilistyczne opadów maksymalnych o określonym czasie trwania i prawdopodobieństwie przewyższenia – Projekt PMAXTP” pod redakcją Bogdana Ozga-Zielińskiego, Instytut Meteorologii i Gospodarki Wodnej – Państwowy Instytut Badawczy, Warszawa 2022 i ponadto podanie adresu strony internetowej projektu PMAXTP…” | PS and M replace S for PMAXTP |
| same, ust. 2 | the processed text PP | PP replaces P for PMAXTP |
| Terms of the hydrological service, https://hydro.imgw.pl/#/regulamin | „Użytkownik może używać nieodpłatnie udostępnionych informacji jedynie do celów prywatnych. Wykorzystywanie informacji pochodzących z IMGW-PIB dla potrzeb działalności gospodarczej, na stronach internetowych zawierających reklamy lub do celów: […] bez zawarcia umowy … stanowi wprost naruszenie art. 385 ust. 5 … Prawo wodne.”; a missing source or processed-data note can bring liability | S and P with RH (H, never required, dropped by ECO-065); data of hydro.imgw.pl and hydro-back.imgw.pl are operational |
| ČHMÚ, https://www.chmi.cz/-/jak-mohu-pou%C5%BE%C3%ADvat-otev%C5%99en%C3%A1-data-%C4%8Dhm%C3%BA- | open data under CC BY 4.0; §3(a)(1) of the licence: the creator, a URI of the material where reasonably practicable, an indication of modification, the licence with its link; a reasonable manner by medium | C, and CP when modified |

## The rule

DEV §20 holds the lines byte for byte and the surfaces; in short:

| Data | Lines (`attribution`) | Terms (`terms_notice`) |
|---|---|---|
| danepubliczne.imgw.pl (archives, current API) | S; S and P when processed (nearly always: parsed, harmonised, reformatted, aggregated, charted, computed) | RD |
| hydro.imgw.pl, hydro-back.imgw.pl (water-state classes, operational data, station locations) | S, P; operational data (states, measurements, warnings) shown live with their time, never stored or presented as archive; station locations are reference data that may be kept with their lines (DEV-20.8, the author's decision of 2026-11-13) | RH |
| PMAXTP (powietrze.imgw.pl tpmax-api, klimat.imgw.pl) | PS and M; PS, PP and M when processed (design rainfall, hyetographs, hydrographs, model inputs, tables in another form) | RK |
| ČHMÚ open data | C; C and CP (what was done) when modified | none |

Order S, P, PS, PP, M, C, CP, then RD, RH, RK; each line once. A product with several sources carries every set that applies. In an English context the Polish line stays and an English gloss may follow. Surfaces (DEV-20.5): GUI popups, panels, charts, tables, current measurements and the view's footer; CSV (trailing columns `attribution` and `terms_notice`, one line per cell from the first data row down; columns a project already has stay), JSON and API, REST and MCP responses (fields `attribution` and `terms_notice`), Parquet (metadata keys of the same names, JSON arrays), ZIP and plain files in a directory (`ATTRIBUTION.txt`: the lines in order, merged on a later write), PNG and SVG (footer lines drawn in the image), print, PDF and generated reports; CLI output with data or results; model inputs (a header comment, or `ATTRIBUTION.txt` beside them). Never in a tooltip only. One source of the lines per project.

## Hand-off

`nogat-handoff/1` had no place for text a person reads: `provenance` holds keyed origins. Step 1 adds two optional top-level arrays of strings, `attribution` and `terms_notice`, and keeps `/1` (AGI-4.1); the schema's examples carry PS, PP, M and RK. A producer writes them whenever the hand-off carries provider data; a consumer shows them with the loaded data and carries them, merged without duplicates, into its own products and further hand-offs (DEV-20.6, DEV-20.7). The kit's `nogat-handoff.js` is unchanged; each GUI copies the new `schemas/exchange/handoff-1.schema.json` byte for byte in its own branch (DEV-15.6). Copies of today accept both fields as unknown. The decision went to the agents of Obserwator, Archiwista, Hydrolog, Hydrograf, Hydraulik and Retman on 2026-11-13.

## Steps

1. Nogat: this plan, DEV §20, ECO-060, the two fields in `nogat-handoff/1` with contract tests.
2. Obserwator, the producer of the data.
3. Hydrolog.
4. Hydrograf.
5. Archiwista.
6. Hydraulik.
7. Retman.

Steps 2 to 7 run in parallel: the lines are fixed by DEV §20, so no consumer waits for a producer's release; a consumer still passes on whatever lines it receives.

## Per project

| Project | Provider data | Surfaces to cover |
|---|---|---|
| Obserwator (repository IMGWTools) | all three IMGW-PIB sources and ČHMÚ: archives, current API, hydro-back (`fetch_hydro_states`, `HYDRO_MAP_API_URL`, the `api_hydro` catalog source and the hydro locations of `reference_data`), PMAXTP | CLI, MCP and REST results (`obserwator-result/1` gains `attribution` and `terms_notice`); CSV export (its attribution rows stay); Parquet metadata of the store; the public web pages (footer, charts, tables, current measurements); `provider_notice_imgw` gives the R lines; one source of the lines next to `processed_attribution` and the notices of `src/obserwator/messages/datasets.py`; PMAXTP lines PS, PP, M instead of S, P. Hands nothing off |
| Hydrolog | PMAXTP depths in hyetographs and hydrographs; series and annual maxima from Obserwator exports in `stats` | GUI (hyetograph, hydrograph, network, statistics views and the footer); its CSV, JSON, PNG and SVG exports; CLI, MCP and JSON results; reads and writes `attribution` and `terms_notice` in the hand-off and copies the new schema |
| Hydrograf | PMAXTP only (confirmed by its agent): design rainfall and hydrographs | `POST /api/generate-hydrograph` and other responses with derived results; GUI map popups, charts, tables and footer; exports; the hand-off it writes (`backend/core/handoff.py`) with PS, PP, M, RK; copies the new schema |
| Archiwista | Obserwator's store (station series, current data), PMAXTP cells | map popups and panels, series charts and tables, current measurements, footer; REST `/api/v1` responses; `project-export` ZIP gets `ATTRIBUTION.txt`; the series hand-off to Hydrolog carries the lines; copies the new schema |
| Hydraulik | PMAXTP depth in `rainfall build`, through Hydrolog's shape into models | result documents (`hydraulik-rain/1`, `-model/1`, `-run/1`, `-results/1`, `-export/1`, `-couple/1`, `-swmm/1`) gain `attribution` and `terms_notice`; rain tables and SFINCS and SWMM inputs carry a header comment or `ATTRIBUTION.txt`; reports and exported maps and charts |
| Retman | none of its own; prints and writes the results of Obserwator, Hydrolog and Hydraulik | passes on `attribution`, `terms_notice` and the providers' notices verbatim in its CLI output and the files its mappers write (its CSV kinds already keep `attribution_source` and `attribution_processed`) |
| Kartograf | none: it downloads data of GUGiK, ČÚZK, Copernicus and ISRIC; IMGW-PIB and ČHMÚ appear only in its agent guides, routing to Obserwator (`src/kartograf/_data/agents/`, `origin/develop` `d0990c89`) | none under this plan |

Out of scope: the licences of Kartograf's own providers, and anything a project would need to use data commercially.

## Amendment: minimal provider texts (ECO-065, 2026-11-13)

Nogat's step: DEV §20 without H and N, RD, RH and RK renamed, DEV-20.4 and DEV-20.7, ECO-065, kit 0.6.0 (the regulamin's source blocks hold the provider, its lines and the link; no `imgw-terms`), `scripts/terms.py` without derived blocks, the schema's examples with RK alone. The lines, old → new:

| Mark | Before | After |
|---|---|---|
| H | Dane pochodzą z serwisu hydrologicznego IMGW-PIB https://hydro.imgw.pl | dropped |
| N | Dane IMGW-PIB można wykorzystywać nieodpłatnie do celów prywatnych (niezarobkowych). Wykorzystanie … wymaga umowy z IMGW-PIB. | dropped |
| RD | Regulamin: https://danepubliczne.imgw.pl/regulations | Regulamin danych IMGW-PIB: https://danepubliczne.imgw.pl/regulations |
| RH | Regulamin: https://hydro.imgw.pl/#/regulamin | Regulamin serwisu hydrologicznego IMGW-PIB: https://hydro.imgw.pl/#/regulamin |
| RK | Regulamin: https://klimat.imgw.pl/opady-maksymalne | Regulamin danych PMAXTP: https://klimat.imgw.pl/opady-maksymalne |

S, P, PS, PP, M, C, CK and CP are unchanged. A tool that told terms lines from attribution lines by the prefix „Regulamin: ” (in `ATTRIBUTION.txt` merges and CSV readers) recognises the new form „Regulamin <whose terms>: <address>” instead. Each project, in its own branch, read on 2026-11-13 at the heads named:

| Project | Constants | Tests and other copies |
|---|---|---|
| Obserwator (`develop` `9aefb23`, `feature/compact-sources` `150d810`) | `messages/legal.py`: `_IMGW_HYDRO` and the message `imgw_hydro_attribution` (H), `_IMGW_TERMS` and `imgw_terms_notice` (N) go; `_TERMS_DANEPUBLICZNE`, `_TERMS_HYDRO`, `_TERMS_PMAXTP` take the new RD, RH, RK. `attribution.py`: `_H` and `_N` go, `_ATTRIBUTION_ORDER` S, P, PS, PP, M, C, CP, `_TERMS_ORDER` RD, RH, RK, `_LINES` with terms `(_RD,)`, `(_RH,)`, `(_RK,)` and `imgw_hydro` without H. `messages/datasets.py` `provider_notice_imgw`: the English summary of the terms goes, `{terms}` stays. `gui/_terms.py`: no derived `imgw-terms` | `tests/unit/test_attribution.py` (the table pin: H, N out, RD, RH, RK new); `tests/unit/gui/test_terms.py` (the `imgw-terms` cases); the golden exports `tests/fixtures/export_golden/store_read_*` and `series_export_*` regenerated by their script; `gui/web/instrukcja/index.html` (the N and H paragraphs, the three „Regulamin:” lines); kit 0.6.0 into `gui/web/nogat/`; `schemas/nogat/handoff-1.schema.json`; `docs/DECISIONS.md` D1 |
| Hydrograf (`develop` `6615439`, `feature/compact-sources` `68dc905`) | `backend/core/attribution.py`: `IMGW_TERMS_NOTICE` goes; `PMAXTP_TERMS` takes RK; `PMAXTP.terms_notice = (PMAXTP_TERMS,)`. `backend/scripts/analyze_watershed.py` (`write_attribution_file`): terms lines by the new form, not by `IMGW_TERMS_NOTICE` or „Regulamin: ”. `backend/core/terms.py`: no derived `imgw-terms` | `backend/tests/unit/test_terms.py` (the `imgw-terms` cases); `frontend/instrukcja/index.html` and `docs/Hydrograf-prezentacja.html` (N and RK on every slide); kit 0.6.0 into `frontend/nogat/`; the schema copy; ADR-0084 and `docs/ARCHITECTURE.md` naming `imgw-terms` |
| Hydrolog (`develop` `f2978a4`, `feature/compact-sources` `faa32cf`) | `src/hydrolog/_attribution.py`: `IMGW_HYDRO` (H) and `IMGW_TERMS` (N) go, from `__all__` too; `TERMS_DANEPUBLICZNE`, `TERMS_HYDRO`, `TERMS_PMAXTP` take RD, RH, RK; `_TERMS_PREFIX` „Regulamin:” gives way to the new form; `_LINES["imgw_hydro"]` without H, the terms of each provider one line; `_ORDER`. `gui/_terms.py`: no derived `imgw-terms` | `tests/unit/test_attribution.py` (H, N, RD, RH, RK pins; the other-terms example „Regulamin: https://example.org/terms” in the new form; the SVG footer pin of RK); `tests/unit/test_operations_pmaxtp.py` (`IMGW_TERMS`, RK); `tests/unit/gui/test_terms.py`; kit 0.6.0 into `gui/web/nogat/`; the schema copy; ADR-0028 and ADR-0034 |
| Archiwista (`develop` and `feature/compact-sources` `3a02da8`) | `messages/legal.py`: `imgw_hydro` (H) and `imgw_terms` (N) go; `imgw_terms_public_data`, `imgw_terms_hydro`, `imgw_terms_pmaxtp` take RD, RH, RK. `attribution.py`: `_ATTRIBUTION`, `_TERMS` and `_LINES` without `legal.imgw_hydro` and `legal.imgw_terms` | `tests/fixtures/provider_lines.py` (`IMGW_HYDRO`, `IMGW_TERMS` go; `IMGW_TERMS_PUBLIC_DATA`, `IMGW_TERMS_HYDRO`, `IMGW_TERMS_PMAXTP` new) and the tests importing them: `tests/unit/test_attribution.py`, `test_project_exports.py`, `tests/integration/test_station_compare_api.py`, `test_station_series_api.py`, `test_station_statistics_api.py`, `test_stations_api.py`, `test_stations_cli.py`, `test_version_lines.py`, `tests/e2e/test_compare.py`, `test_file_projects_store.py`, `test_station_card.py`, `test_station_chart.py`, `test_stations_catalog.py`, `test_stations_map.py`; `web/guide/index.html` (the card „Warunki IMGW-PIB”); `docs/SPEC.md` (the line table and examples); kit 0.6.0 and the schema copy |
| Hydraulik (`fix/provider-attribution` `34500ef`, not on `develop`) | `src/hydraulik/attribution.py`: `IMGW_TERMS_NOTICE` goes, from `__all__` too; `_TERMS_PREFIX` „Regulamin: ” gives way to the new form in `is_terms`; `PMAXTP_TERMS` takes RK; `_ORDER` without H and N, with the new RD and RH; the PMAXTP lines' terms `(PMAXTP_TERMS,)` | `tests/unit/test_attribution.py` (RD); `test_rainfall_command.py` (`PMAXTP_TERMS_NOTICE` becomes RK alone); `test_model_build.py` (N, RD); `test_couple_command.py`, `test_swmm_command.py`, `test_tables.py` (example terms lines „Regulamin: …” in the new form); ADR-0012 |
| Retman (`develop` `64893fa`, `fix/provider-attribution` `8b8d473`) | none: it passes the producers' lines on | `tests/integration/adapters/test_manifest_adapter.py` (its RD fixture) |

Stored files keep the lines they were written with. Those a tool reads back and serves or merges again must be rebuilt by the tool, never edited by hand: Obserwator's stored analyses and series documents (`store/analyses.py`, `store/series.py` replay their `attribution` and `terms_notice`), and every `ATTRIBUTION.txt` merged on a later write (Obserwator's plain writes, Hydrograf's analysis outputs, Hydrolog's run directories, Hydraulik's model and run directories), since the merge would carry H and N into the next product. Exports already handed out (CSV, Parquet, ZIP, images) need no rebuild: they carry the required lines, and the next export carries the new ones.

## Results

- Step 1: commit on Nogat `fix/provider-attribution` (see `CHANGELOG.md`); gate green.
- Amendment (ECO-065): commit on Nogat `feat/minimal-provider-texts` (see `CHANGELOG.md`); gate green.
