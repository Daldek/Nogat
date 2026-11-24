# Plan: one chart module in the kit — zoom, pan and reset alike in every GUI

Approved: pending

Status: proposed on 2026-11-24 (branch `plan/unified-charts`); nothing done. The design's proposals are marked „[proposed]”.

Requirements: DEV-15.1, DEV-15.2, DEV-15.3, DEV-15.6, DEV-19.21, DEV-20.5, REL-1.4, ECO-055, ECO-058, ECO-072. Source: Obserwator's feedback #9 (2026-11-23): „Fajnie byłoby dodać zoom i przesuwanie do wykresów w tych wszystkich apkach. No i reset widoku po zoomie.” Related: the GUI platform plan `2026-11-01-nogat-gui-platform.md` (pending, deferred on 2026-11-12), whose stage 2 proposed a `chart-theme.js` that kept Chart.js beside the hand-drawn SVG; this plan replaces that row for charts.

## The author's direction (2026-11-24)

- „musimy ujednolicać pomiędzy projektami zachowanie i technologię”: one behaviour and one implementation of charts across the GUIs.
- The interaction sketch, approved:
  - a drag over the plot selects a range of x (kept);
  - Ctrl with the wheel zooms around the cursor; the wheel alone scrolls the page;
  - Shift with a drag, or a drag with the middle button, pans;
  - a double click, the key 0 or „Cały zakres” resets;
  - on a phone two fingers pinch and pan; one finger scrolls the page and reads values;
  - a small bar under a zoomed chart with „−”, „+”, „Cały zakres” and the range shown;
  - the y axis fits the visible part;
  - scatter charts (the rating curve, PMAXTP) zoom both axes by a rectangle;
  - a PNG exports what is visible, a CSV the whole series.

## What exists (checked on 2026-11-24 on each `develop`)

| GUI (`develop`) | Charts | Zoom and pan today |
|---|---|---|
| Obserwator (`b5a1c1a`) | Its own SVG engine `src/obserwator/gui/web/src/charts/` (9 files, about 2,500 lines: `chart.js` the Preact wrapper, `draw.js` DOM only, „so a kit component can wrap it as `Chart` does”, `draw.js:1-3`); scales linear, log, time, date, datetime, gumbel, y `band`, a `y2` panel above; series line, step, area, band, bars, points, rug; marks; decimation per pixel column (`thinPoints`); readout by pointer and keys; `toPng` (`png.js:93`); words from the catalog `charts.*` (`messages/gui/charts.py`), Polish and English. Used by 16 views. | `chart.js:37` documents `zoom` as „`true` by default on a `date` axis”; `draw.js:204-211` zooms `date` and `datetime` by default (the header lags `39665f4`, 2026-11-23), linear, log and time with `zoom: true`, never gumbel or a `band` y. A mouse drag selects x; `+`/`−` halve and double around the readout; arrows move the range past its edge; `0`, a double click or the button reset; a bar under a zoomed chart with „Widoczne: {from} – {to}” and „Pokaż całość” (`charts.py:22-23`). The y axis fits the range (`axes.js:100-131`). A touch reads out and scrolls the page (`draw.js:500-503`). No Ctrl+wheel, no pan by drag, no pinch. Zoomed by default: `dane`, `teraz`, `characteristic`, `lowflow`, `trends`, `susze`, `duration` (log x); not zoomed: the rating curve (`rating.js:112,167`, linear or log x), PMAXTP (log–log, `pmaxtp/result.js:82-89`), the Gumbel plots, the month and day-of-year charts. `toPng` has no caller in the views. |
| Hydrolog (`34563ef`) | A diverged copy of the same engine, `src/hydrolog/gui/web/src/charts/` (8 files, about 1,800 lines; each differs from Obserwator's, `svg.js` by one line): no date or datetime scale, no `band` series, no zoom; named ticks `labels` instead of `tickList`; a short time axis in minutes (`d33b2a2`); Polish words as constants (`labels.js`, `CHART_TEXT`); `toPng` draws the providers' lines under the image (`png.js:9-14`, DEV-20.5). Used by Hydrogram (3 time charts), Sieć, Statystyka (gumbel), Kalkulatory (`band`) and the result view. | None: a readout by pointer and keys only. PNG of the chart shown in the export panel (`ui/export-panel.js:332`, `siec/results-panel.js:276`); CSV and JSON of the whole result. |
| Hydrograf (`dba88d7`) | Chart.js 4.4.7 vendored (`frontend/vendor/chart.js-4.4.7/chart.umd.js`, 205,615 B; `index.html:630-631`) and `frontend/js/charts.js` (888 lines, IIFE on `window.Hydrograf`): land-cover and HSG share bars, the hypsometric curve (scatter), the terrain profile (its hover moves a marker on the map), the hyetograph and the hydrograph (x in minutes). Colours restyled per theme by stylers. The kit reaches its scripts through `js/nogat.js` (ADR-082). | None; no zoom plugin. CSV of the hyetograph (`rain-export.js:78-80`); no PNG. |
| Archiwista (`8805a78`) | Its own SVG drawing `src/archiwista/web/src/views/station-chart.js` (1,223 lines; `ChartPlot` also draws the panels of `station-compare.js`): one or two variables, a second unit on a right-hand axis, gaps as grey bands, the server's min/mean/max band of a simplified chart (`max_points` = the plot's width), extremes as dots, sums as diamonds, hollow dots of incomplete years, tooltips. | A drag selects a range; the wheel alone zooms around the cursor (`station-chart.js:658-667`), so it takes the page's scroll over the chart; `+`/`−` zoom, arrows pan, `Home` and „Cały okres” reset (`:668-689`, `labels/station.js:81-82`). A zoom refetches the range and writes `from` and `to` into the address. The plot has `touch-action: none` (`station.css:87`): a finger never scrolls the page there and a one-finger drag selects a range. No pinch. No PNG or CSV of the chart; its hand-off carries the chart's range (plan `2026-11-05-archiwista-series-to-hydrolog.md`, erratum to D4). |

Three gesture sets, three words for the reset („Pokaż całość”, „Cały okres”, none), two that disagree with the sketch (Archiwista's plain wheel and its `touch-action: none`), two copies of one engine drifting apart, and one foreign library. Every project is MIT-licensed, so Obserwator's code moves into Nogat as it is.

## Design [proposed]

| ID | Decision |
|---|---|
| C1 | **One module in the kit.** `design/kit/nogat-chart.js` (`drawChart(container, spec)` and its handle, the gestures, the range bar, the words), `nogat-chart-axes.js`, `nogat-chart-scale.js`, `nogat-chart-series.js`, `nogat-chart-png.js` and `nogat-chart.css`, built from Obserwator's engine at `b5a1c1a` (`draw.js`, `axes.js`, `scale.js`, `series.js`, `svg.js`, `png.js`, `labels.js` and the chart rules of `css/charts.css`). Plain ES modules without Preact or a build step (DEV-15.1), tokens only (DEV-15.3), listed in `nogat-kit.json` and copied byte for byte (DEV-15.6); `drift` names a copy that lags. Each GUI keeps a wrapper of its own of some 20 lines (Obserwator's and Hydrolog's `Chart` for Preact, Archiwista's for Preact, Hydrograf's for its scripts through `js/nogat.js`). Series classes of one view (PMAXTP's ramp, the rating curve's fit) stay in the GUI's CSS. |
| C2 | **What it takes from Hydrolog's copy.** A short time axis labelled in minutes (`d33b2a2`); `toPng` with the providers' lines under the image (DEV-20.5). Hydrolog's `labels` becomes Obserwator's `tickList`. |
| C3 | **What it gains for Archiwista and Hydrograf.** A second unit on a right-hand axis (`y.side: "right"`, beside `y2`, the panel above); `span` marks (a grey band over a gap); point shapes `hollow` and `diamond`; `onReadout(index | null)`, so Hydrograf's profile moves its map marker; `onRange({min, max} | null)` once a range settles (the end of a drag, a pinch or a key, the wheel idle 200 ms), so Archiwista refetches the range at the plot's width and keeps `from` and `to` in its address, and `zoom.set` takes a range back; `group`: charts of one group share the range of x (Archiwista's compare panels, Hydrograf's hyetograph and hydrograph). |
| C4 | **Words.** The module's own words in Polish in an exported `CHART_TEXTS`, as the kit's other modules (`TEXTS` of `nogat-handoff.js`); a GUI with another language passes its own through `spec.texts` (Obserwator from its `charts.*` catalog), and redraws on its language switch with `update`. One word for the reset everywhere: „Cały zakres” (Obserwator's „Pokaż całość” and Archiwista's „Cały okres” go). |
| C5 | **Mouse and trackpad.** A drag selects x (a rectangle on a `zoom: "xy"` chart) when it covers at least 6 units of the viewBox (Obserwator's `DRAG`), else it is a click. Ctrl with the wheel zooms around the cursor, the x under the cursor staying there, by 1.25 per notch and in proportion for a trackpad's small steps, and prevents the browser's page zoom over that chart only; the wheel alone is never taken, the page scrolls. A trackpad's pinch reaches the page as Ctrl with the wheel in Chromium and Firefox [INFERENCE, checked in step 1]. Shift with a drag, or a drag with the middle button (its autoscroll prevented), pans, held within the whole. A double click resets. A zoom stops at 4 points of the readout's series in the range (Obserwator's limit), panning at the whole's edges. |
| C6 | **Phone.** The plot has `touch-action: pan-y`: one finger moving up or down scrolls the page, one finger along the plot moves the readout (as Obserwator's touch today), two fingers pinch (around their middle) and pan. A drag of one finger never selects a range. The browser's own pinch zoom of the page is not available over a zoomable chart; outside it, it is. |
| C7 | **The range bar.** Under a zoomed chart, one line at 390 px: „−” („Oddal”), „+” („Przybliż”), „Cały zakres”, and the range shown („{from} – {to}” in the axis's format; a `zoom: "xy"` chart names x and y). Buttons at least 24 × 24 px (WCAG 2.2 SC 2.5.8), the kit's `btn sm`; hidden again by a reset. |
| C8 | **Axes.** On a `zoom: true` chart the y axis (and `y2`, a right-hand axis) fits the values within the range shown (Obserwator's `extents` already does so). A `zoom: "xy"` chart zooms and pans x and y alike, by a rectangle, Ctrl+wheel, pinch and keys; its y is then the person's, not fitted. `zoom: "xy"`: Obserwator's rating curve (both charts) and PMAXTP; others where a GUI asks for it. |
| C9 | **Which charts zoom.** By default every chart whose x is `date`, `datetime`, `time`, `linear` or `log`; never a `band` y or a share bar. A GUI sets `zoom: false` on a chart of a year's months or days (the regime, month climatologies), where a range means nothing. Gumbel plots: open question 5. |
| C10 | **Keys** (the chart is focusable where it reads out or zooms, as Obserwator's): arrows read the values, Shift or Page ten steps, Home and End the first and last, Esc hides the readout (Obserwator's); `+` and `−` zoom around the readout or the middle, the arrows past the range's edge move it a quarter on, `0` resets. Archiwista's `Home` reset becomes `0` and its arrows read out. |
| C11 | **Accessibility.** `role="img"` with the chart's title, an `aria-description` naming the keys and the gestures, an `aria-live="polite"` region that says the range after each zoom (Obserwator's `keysHint`, `draw.js:358-411`); the bar's buttons named; every gesture has a key and a button that does the same, so no zoom needs a path or two fingers (WCAG 2.2 SC 2.5.1, 2.5.7). Both themes from tokens. |
| C12 | **Exports.** `toPng` draws the chart as shown: the range shown, the y fitted, without the readout and the selection (Obserwator's `svgText`), with the providers' lines under it (Hydrolog's footer, DEV-20.5); the file names stay each GUI's (DEV-19.21). A CSV holds the whole series whatever the range shown; the kit writes no CSV. A hand-off is not an export: Archiwista's keeps the chart's range (its D4 erratum). |
| C13 | **The range across redraws.** Kept while the data are the same (Obserwator's `sameData`), reset when they change; a GUI may keep it elsewhere through `onRange` and `zoom.set` (Archiwista's address). |
| C14 | **Hydrograf off Chart.js** (recommended, option A below): its six charts are drawn by the kit's module; the share bars as the `band` y (one bar per class, as Hydrolog's Kalkulatory), the peaks as `peak` marks, the profile's marker through `onReadout`; the theme stylers go (colours are CSS classes); Chart.js 4.4.7 and its licence leave the vendor directory. |
| C15 | **The rule**, a new rule of DEV §15 (its next free number, 15.15 on `develop` today): „A GUI draws its charts with the kit's chart module (`nogat-chart.js`, DEV-15.6), never with a chart library or a drawing of its own. A chart over a continuous axis shows a range of it: a drag over the plot selects the range of x, of x and y on a chart of points; Ctrl with the wheel zooms around the cursor and the wheel alone scrolls the page; Shift with a drag, or a drag with the middle button, pans; a double click, the key 0 and „Cały zakres” show the whole. On a touch screen two fingers pinch and pan, one finger scrolls the page and reads the values. A zoomed chart shows under it „−”, „+”, „Cały zakres” and the range shown, and its y axis fits the values shown. A PNG of a chart is the chart as shown with the lines of DEV-20.5; a CSV holds the whole series. *Why:* one person moves between the GUIs, and four implementations had three sets of gestures (ECO-0NN).” |
| C16 | **The decision** (ECO-0NN, the next free number when step 1 lands: 088 on `develop` today): Decision as C1 to C15; Why: feedback #9 and the author's direction of 2026-11-24; Rejected: four implementations kept to one written gesture specification (they drifted already: Hydrolog's copy); Chart.js with its zoom plugin everywhere (a canvas without the keys and the readout the SVG engine has, and a second migration of three GUIs); the wheel alone zooming (Archiwista's today: it takes the page's scroll); Consequence: the kit's minor version (open question 2), the chart rule of C15, and each GUI's minor of steps 2 to 5. |

### Hydrograf: two ways weighed

| | A: the kit's module (recommended) | B: an interim layer on Chart.js |
|---|---|---|
| Gestures | the same code as the other GUIs | `chartjs-plugin-zoom` 3.0.2 (npm registry, 2026-11-23; 3.0.0 of 2026-11-21 dropped the hammerjs dependency of 2.2.0) gives a drag zoom, a wheel zoom with `modifierKey: "ctrl"`, a pan with `modifierKey: "shift"`, pinch, and sets `touch-action: pan-y` when only x zooms (https://www.chartjs.org/chartjs-plugin-zoom/latest/guide/options.html, read 2026-11-24); the middle button, the keys, the range bar, the double click, the readout by keys and the live region are Hydrograf's own code |
| Look, words, PNG | the kit's: tokens as classes, `CHART_TEXTS`, `toPng` with the lines | Chart.js's canvas, restyled by stylers; a PNG of its own |
| Tests | the kit's browser tests, plus Hydrograf's e2e of its views | a second set for the same gestures |
| Cost | six chart functions (888 lines) rewritten on the kit's spec; Chart.js removed | a vendored plugin whose 3.0 line is three days old; later a second migration (the chart rule of C15) |

B is only worth it if Hydrograf must zoom before the kit's module exists; A is proposed.

## Steps

| # | Repository, branch | Change |
|---|---|---|
| 1 | Nogat, `feat/kit-chart` | The six kit files (C1 to C13) and their hashes in `nogat-kit.json`; the kit's version as open question 2 decides (REL-1.4, ECO-072); the chart rule of C15 and ECO-0NN, the changelog of `standards/README.md`; `design/README.md`: „Charts” under Components (the gestures, the bar, the words) and the kit's file list; a chart in `specimen.html`; `tests/browser/test_chart.py` (below); the row `chart-theme.js` of the GUI platform plan points here |
| 2 | Obserwator, its next minor (open question 1) | `gui/web/src/charts/` replaced by the kit's copy, the `Chart` wrapper kept; `charts.*` words passed in, „Pokaż całość” → „Cały zakres”; rating curve and PMAXTP `zoom: "xy"`; the month and day-of-year charts `zoom: false`; `tests/e2e/test_charts.py` keeps its cases on the kit's module (the 50,000 points under 200 ms among them); ADR, manual, changelog |
| 3 | Hydrolog, its next minor | its copy of `charts/` replaced by the kit's; `labels` → `tickList`; `CHART_TEXT` goes; the PNGs of the export panel and of Sieć's results through the kit's `toPng`; Hydrogram's and Sieć's time charts zoom; ADR, manual, changelog |
| 4 | Archiwista, its next minor | `ChartPlot` and its drawing replaced by the kit's module (C3: the right-hand axis, the gap spans, the point shapes, `onRange`, `group` for the compare panels); the wheel alone no longer zooms; `touch-action: none` goes; `Home` → `0`; „Cały okres” → „Cały zakres”; the range stays in the address; `tests/e2e/test_station_chart.py:244,282` and `test_stations_compare.py:167` follow; ADR, manual, changelog |
| 5 | Hydrograf, its next minor | option A (C14): `js/charts.js` on the kit's module through `js/nogat.js`, Chart.js removed; the hyetograph and the hydrograph one `group`; ADR, manual, changelog |

Step 1 first (producer); steps 2 to 5 independent of each other after it, each with its own gate and its e2e at 1440 and 390 px. Nothing is tagged before the round ends.

### Tests of step 1 (Chromium through Playwright, under CSP `'self'`, at 1440 × 900 and 390 × 844 px, both themes)

- a drag selects x, the y axis fits, the bar shows the range; a drag shorter than 6 units is a click; a rectangle on `zoom: "xy"`;
- Ctrl+wheel keeps the x under the cursor; the wheel alone scrolls the page and leaves the chart as it was;
- Shift+drag and a middle-button drag pan, held within the whole;
- a double click, `0` and „Cały zakres” reset; `+`, `−` and the arrows past the edge; the live region says the range;
- at 390 px: a vertical swipe scrolls the page, a horizontal one moves the readout and never selects; two touch points (CDP `Input.dispatchTouchEvent`) pinch and pan; the bar fits one line and its buttons are at least 24 px;
- `toPng` of a zoomed chart: the range shown, no readout or selection, the lines under it;
- `onRange`, `onReadout` and `group`; `spec.texts` replaces every word; 50,000 points under 200 ms; nothing loaded but the kit.

## Open questions

1. Obserwator's release: the author's rule of 2026-11-22 leaves `v3.3.0` to Gdańskie Wody and `v3.4.0` to CAMELS-PL, so charts in `v3.5.0` [proposed]; or into an earlier one, since feedback #9 is Obserwator's?
2. The kit's version: `1.2.0` is on `develop`, unreleased (`main` holds `1.1.0`); the chart module joins `1.2.0` or makes `1.3.0`?
3. Hydrograf: option A (off Chart.js, recommended) or B (an interim layer on `chartjs-plugin-zoom` 3.0.2 until A)?
4. A zoomable chart not yet zoomed: no bar (as sketched), or a lone „+” in its place, so a person who can neither drag nor pinch zooms by a tap (WCAG 2.2 SC 2.5.1, 2.5.7)? Recommended: the lone „+”.
5. The Gumbel (probability) plots of Obserwator and Hydrolog: zoom both axes by a rectangle like the scatter charts, or no zoom (Obserwator's engine excludes them today)?
6. Obserwator's charts have no PNG download (its `toPng` has no caller): add „PNG” under them in step 2, or keep the export rule to the GUIs that export charts today?

## Results

None yet.
