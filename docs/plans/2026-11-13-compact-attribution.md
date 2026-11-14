# Plan: one compact strip of provider lines per GUI view

Approved: 2026-11-13, the author (in session)

Amended: 2026-11-14, ECO-070: a GUI has no footer; without a welcome window the dialog is reached from the strip only, and with one, the window's „Regulamin serwisu” is its regulamin link ([the plan](2026-11-14-no-footer.md)).

Status: done 2026-11-13. Steps 1 to 5 merged into the `develop` of Nogat, Obserwator, Hydrolog, Hydrograf and Archiwista ([Results](#results)); no tags, no release.

Requirements: DEV-20.5 and DEV-20.7 as amended by ECO-064, DEV §20, DEV-15.6, DEV-15.7, HUB-5.2 (producers before consumers), DEV-17.5.

## Goal

The provider lines of ECO-060 took too much of every GUI: Obserwator showed about six lines under the map and a block under every card of its station panel. A view now shows them once, in one compact strip, while every product keeps the full lines.

## The compromise

| Where | What |
|---|---|
| The strip, one per view, the kit's `<nogat-sources>` | 12 px, `--text-3`; S, P, PS, PP and CK („Źródło: ČHMÚ, CC BY 4.0”, linked to https://opendata.chmi.cz and the licence), each once in the order of DEV-20.4; then „Źródła i warunki”. At most two lines at 1440 px for one IMGW-PIB family with ČHMÚ, a third when a view shows both families (the five sentences measure 3306 px at 12 px Lato); wrapping on phones |
| The dialog behind „Źródła i warunki” | Every line (S, P, PS, PP, M, C, CP), the terms (RD, RH, RK) and „Regulamin serwisu” where the GUI serves one; H and N dropped by ECO-065 |
| A welcome window, where the GUI has one | The same content on the first visit, through `fillSources()`; without one, the dialog is reached from the strip and the footer |
| Files, exports, PNG and SVG, print views, hand-offs, API, CLI and MCP | Unchanged: the full lines, `attribution` and `terms_notice` |

Legal basis: §5 ust. 3 and 4 of the IMGW-PIB terms and ust. 1 and 2 of the PMAXTP terms require their sentences on the product, so S, P, PS and PP stay on screen verbatim; CC BY 4.0 §3(a)(2) allows a reasonable manner, a link to a page with the full information included, so C shrinks to CK.

## Steps

1. Nogat (done): DEV-20.5 and DEV-20.7 amended, CK in the table of DEV §20, ECO-064; kit 0.5.0 with `nogat-sources.js` and `.css`; `design/README.md` and the specimen; contract tests (the element's lines equal DEV §20, the button's label, the documented attributes) and browser tests (the lines once and in order, at most two lines at 1440 px per family, the dialog with every line, focus kept in it, Esc, both themes, 390 px, CSP `'self'`, nothing loaded but the kit).
2. Obserwator: copy kit 0.5.0 byte for byte (DEV-15.6); replace the lines under the map and under every card of the station panel with one `<nogat-sources>` per view, fed the union of the `attribution` and `terms_notice` of the data the view shows, `terms` set where the regulamin is served; the welcome window, if it has one, filled with `fillSources()`. PNG, SVG, CSV and the API keep the full lines.
3. Hydrolog: the same in each of its five sections; a section with a station series and PMAXTP rainfall passes both, and its strip may take a third line.
4. Hydrograf: the same for the map view and the hydrograph panel; a hand-off received keeps its arrays, merged into the view's union.
5. Archiwista: the same for the map and the station views of its stores; no `terms` attribute, since it serves no regulamin (ECO-062).

Each project checks in its own gate that every view has exactly one strip and that its exports still carry the full lines.

## Results

- 2026-11-13, step 1: Nogat `5406e5c`, merged into `develop` at `751e978` (kit 0.5.0; kit 0.5.1 at `9940bb8`).
- 2026-11-13, step 2: Obserwator `47144ba` (kit 0.5.1), merged at `c594117`.
- 2026-11-13, step 3: Hydrolog `faa32cf` (kit 0.5.1), merged at `f2978a4`.
- 2026-11-13, step 4: Hydrograf `68dc905`, merged at `6615439`.
- 2026-11-13, step 5: Archiwista `3bd512f`, merged at `1567b77`.
