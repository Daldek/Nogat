# Plan: a station series from Archiwista to Hydrolog's statistics through the hand-off

Approved: 2026-11-05, the author („Hydrolog ma możliwość liczenia statystyk z szeregów rocznych maksimów lub dobowych. Trzeba zrobić mechanizm przekazywania danych z Archiwisty do Hydrologa analogiczny do tego, który jest pomiędzy Hydrografem a Hydrologiem. Daję ci autonomię w działaniu”); the decisions below by that delegated authority.

Requirements: HUB-5.2 (producers before consumers), DEV-17.4, AGI-4.1; `schemas/exchange/handoff-1.schema.json` (`nogat-handoff/1`, item 6 of `2026-11-01-nogat-gui-platform.md`).

## Goal

A person looking at a station's series in Archiwista hands it to Hydrolog's „Statystyka przepływów” in two clicks, as Hydrograf hands a watershed to „Hydrogram zlewni”: „Kopiuj do Hydrologa” (clipboard) or „Plik przekazania” (`<subject>.handoff.json`) in Archiwista, „Wczytaj…” in Hydrolog. Two kinds of series: the daily series of a variable (Hydrolog finds the annual maxima of complete hydrological years itself) and the annual maxima Archiwista finds in IMGW-PIB's half-year characteristics (Archiwista A-ADR-051).

## Decisions

| # | Decision |
|---|---|
| D1 | The envelope stays `nogat-handoff/1`, byte for byte: its copies in Hydrolog and Hydrograf are pinned by SHA-256, and the envelope already allows any payload `<tool>-<kind>/<n>` a consumer validates against its owner's schema. The registry (D5) names the new payload. |
| D2 | The payload is `hydrolog-series/1`, owned by Hydrolog (`src/hydrolog/schemas/hydrolog-series-1.schema.json`), like `hydrolog-network/1`: `name`, `variable`, `unit`, `step` `day` with `dates` (ISO days) or `year` with `years`, `statistic` (`max`, `min`) and `year_type`, and `values` (numbers, `null` for a missing value), the same length as the dates or years. |
| D3 | Hydrolog's GUI opens it in „Statystyka przepływów”: a daily series becomes a session file `<subject>.csv` (`date`, the variable) chosen with its columns; annual maxima become the pasted values (missing years left out). Annual minima are refused for now with a clear reason (the section computes flood quantiles; low flows are `stats low-flow` in „Polecenia”). |
| D4 | Archiwista writes it from the station card's chart: `GET /stations/{code}/handoff` (and `archiwista stations handoff`) for a variable of the daily series or, with `resolution=annual`, the annual maxima; the web's „Kopiuj do Hydrologa” and „Plik przekazania” beside the chart. `provenance.series` names the source (`imgw-pib`, dataset, station code, version) and, for annual maxima, the rule and the years left out because one half is missing: only complete years are handed off, since a flood frequency analysis must not take a half's maximum for a year's. |
| D5 | Registry: Hydrolog provides `hydrolog-series/1`; Archiwista depends on Hydrolog (`kind: data`, `via: [file]`, `exchange: [hydrolog-series/1]`), as Hydrograf's watershed hand-off would be declared. |

Order (HUB-5.2): Hydrolog (schema and consumer) first, then Archiwista (producer), then this registry.

## Results

Done in the order of HUB-5.2 and merged into each `develop` on 2026-11-05 with the author's approval:

- Hydrolog `52ebd3b`, `35054bf` (`feature/series-handoff`, merge `b33e812`; ADR-0020): the schema `hydrolog-series/1` and „Wczytaj z Archiwisty”; served on :8070 since 2026-11-05.
- Archiwista `feature/series-handoff` (tip `ec3e746`, merge `32d3ce4`; A-ADR-052): `GET /stations/{code}/handoff`, `archiwista stations handoff`, the copied schemas; served on :8090. Its gate on `ec3e746`: 2852 passed, coverage 93.7 %.
- Nogat `845af50` (this plan and D5 in the registry, merge `269c388`); its gate green.
- Check on the author's data, station 152160140 POZNAŃ-MOST ROCHA, 26 years each: the annual maxima give GEV Q1% 705.3 m³/s in Hydrolog, the daily series 714.5 m³/s.
- Erratum to D4, 2026-11-05/06 (Archiwista `77f7fbc`, the author's request): the buttons sit in a group „Do Hydrologa” under the chart, which chooses the data („wartości dobowe” or „maksima roczne (pełne lata hydrologiczne)”) and the variable whatever chart is shown; the chart's range goes with its own kind only. The author checked it on 2026-11-06.
- CI on 2026-11-06: green on Archiwista `8f34a4c` and Hydrolog `88dbe71` (Linux, macOS; Windows reported, not blocking).
