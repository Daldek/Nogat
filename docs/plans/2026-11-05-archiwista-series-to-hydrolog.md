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

To be filled after the work: commits of Hydrolog, Archiwista and Nogat, tests, gates.
