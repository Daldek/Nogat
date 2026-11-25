# Visual identity of the Nogat ecosystem

One look for every tool with a GUI: Archiwista, Hydrograf, Hydrolog and Obserwator now, and any tool that gains one later.
The brand comes from debever.pl, the author's site: warm off-white and navy, a GitHub-dark night theme, the wave mark and Lato.
The working UI comes from Archiwista: a dense 13 px interface, status colours and 32 px controls.
Background and decisions: [the plan](../docs/plans/2026-11-01-visual-identity.md).

## Files

| File | Content |
| --- | --- |
| [tokens.css](tokens.css) | CSS custom properties, light and dark theme |
| [marks/](marks/) | One 32x32 SVG mark per project: [nogat](marks/nogat.svg), [archiwista](marks/archiwista.svg), [hydrograf](marks/hydrograf.svg), [kartograf](marks/kartograf.svg), [obserwator](marks/obserwator.svg), [hydrolog](marks/hydrolog.svg), [hydraulik](marks/hydraulik.svg), [retman](marks/retman.svg) |
| [specimen.html](specimen.html) | Preview of tokens, components and marks in both themes; serve `design/` over HTTP (`python -m http.server`) to see the kit's app menu, sources strip, base-map switcher and charts, since modules do not load from `file://` |
| [specimen-admin.html](specimen-admin.html) | The kit's admin panel on a fake API in the page ([specimen-admin.js](specimen-admin.js), key `nogat`); served over HTTP like the specimen |
| [kit/](kit/) | The GUI kit every GUI copies (DEV-15.4 to DEV-15.7, DEV-15.13, DEV-15.15, DEV-15.16, DEV-20.5): the app menu `nogat-app-menu.js` and `.css`, the sources strip `nogat-sources.js` and `.css`, the hand-off `nogat-handoff.js`, the base maps `nogat-basemaps.json`, `.js` and `.css`, the charts `nogat-chart.js` and `.css`, the terms `nogat-terms.md`, `.html` and `.css`, the operator's draft terms `nogat-terms-operator.md`, the admin panel `nogat-admin.js` and `.css`, the manifest `nogat-kit.json` |
| [mockups/hydrograf/](mockups/hydrograf/index.html) | Hydrograf redrawn in the identity and Archiwista's shell (mockup) |
| [mockups/hydrolog/](mockups/hydrolog/index.html) | Hydrolog's GUI: five sections; the hydrograph workbench in full, its results following every change; the river network drawn vertically, each node's settings on click; alone and inside Nogat's shell (mockup) |

## Principles

- Content first: maps, tables and data carry the screen; chrome stays quiet.
- Calm surfaces. Colour carries meaning (status), not decoration.
- One accent per screen.
- Dense but readable: 13 px base in apps, 16 px on sites and in phone form fields.
- Both themes, always.
- No remote resources but maps: no script, style or font from another server, only basemaps and map layers from their providers (DEV-15.7); fonts may be vendored.

## Colour

| Token | Light | Dark | Use |
| --- | --- | --- | --- |
| `--bg` | `#faf8f8` | `#0d1117` | Page background |
| `--surface` | `#ffffff` | `#161b22` | Panels, cards, inputs |
| `--surface-2` | `#f4f1f1` | `#21262d` | Table headers, hover rows, wells |
| `--line` | `#e5e5e5` | `#30363d` | Dividers, panel borders |
| `--line-2` | `#d4cfcf` | `#3d444d` | Control borders |
| `--text` | `#2b2b2b` | `#e6edf3` | Body text |
| `--text-2` | `#4e4e4e` | `#9da7b3` | Secondary text, labels |
| `--text-3` | `#6b6565` | `#8b949e` | Hints, metadata |
| `--accent` | `#284b63` | `#58a6ff` | Links, primary buttons, selection |
| `--accent-hover` | `#1a3a50` | `#79b8ff` | Hover of accent elements |
| `--accent-soft` | `#e4ecf1` | `#132a44` | Selected rows, active tabs |
| `--accent-ink` | `#ffffff` | `#0d1117` | Text on `--accent` |
| `--accent-green` | `#5f8a80` | `#3fb950` | Secondary brand accent (sparingly) |
| `--focus` | `#284b63` | `#58a6ff` | Focus ring |
| `--highlight` | `rgba(143, 159, 169, 0.15)` | `rgba(88, 166, 255, 0.1)` | Search hits, transient emphasis |

Status: a dot or border uses the base colour; a badge uses `-bg` with `-ink` text.

| Status | Base light / dark | `-bg` light / dark | `-ink` light / dark |
| --- | --- | --- | --- |
| `--ok` | `#16a34a` / `#3fb950` | `#dcfce7` / `#12261a` | `#166534` / `#56d364` |
| `--warn` | `#d97706` / `#d29922` | `#fef3c7` / `#2b2111` | `#92400e` / `#e3b341` |
| `--bad` | `#dc2626` / `#f85149` | `#fee2e2` / `#2d1215` | `#991b1b` / `#ff7b72` |
| `--info` | `#1d4ed8` / `#58a6ff` | `#dbeafe` / `#132a44` | `#1e40af` / `#79c0ff` |

| Token | Light | Dark | Use |
| --- | --- | --- | --- |
| `--code-bg` | `#0d1117` | `#010409` | Code blocks, sidecars (dark in both themes) |
| `--code-text` | `#e6edf3` | `#e6edf3` | Text on `--code-bg` |

Navigation rail (dark in both themes):

| Token | Light | Dark | Use |
| --- | --- | --- | --- |
| `--rail-bg` | `#0d1117` | `#010409` | Rail background |
| `--rail-hover` | `#161b22` | `#161b22` | Hovered rail item |
| `--rail-active` | `#284b63` | `#1f3a5c` | Active rail item |
| `--rail-ink` | `#9da7b3` | `#9da7b3` | Rail icons and labels |
| `--rail-ink-active` | `#ffffff` | `#ffffff` | Active item icon and label |

Rules:

- Body text pairs meet WCAG 2.2 AA 4.5:1; focus and status marks meet 3:1. Checked by `tests/contract/test_design.py`.
- Never signal status with a tool accent.
- Never use colour alone: add an icon or a word.

## Theme

Dark follows `prefers-color-scheme` unless the page sets `<html data-theme="light">` or `<html data-theme="dark">`.
A manual switch stores the choice and sets the attribute before first paint, as debever.pl's theme-init does.
Under CSP `'self'` inline scripts are blocked, so the snippet is a small file loaded first in `<head>` (`<script src="theme-init.js"></script>`):

```js
const t = localStorage.getItem("theme");
if (t === "light" || t === "dark") document.documentElement.dataset.theme = t;
```

## Type

- `--font-sans`: Lato where installed or vendored, else the system UI font.
- `--font-mono`: paths, codes, formats and numbers in tables, with `font-variant-numeric: tabular-nums`.
- Weights: `--weight-regular` 400, `--weight-medium` 500, `--weight-bold` 700.
- Headings: tight letter-spacing, `-0.01em`. Line height `--line-height` 1.4.

| Token | Size | Use |
| --- | --- | --- |
| `--text-xs` | 11px | Chips, badges, footnotes |
| `--text-sm` | 12px | Labels, table metadata |
| `--text-base` | 13px | App body |
| `--text-md` | 15px | Panel titles |
| `--text-lg` | 18px | Section headings |
| `--text-xl` | 22px | Page headings |
| `--text-2xl` | 28px | Hero numbers, landing titles |
| `--text-site` | 16px | Site body, phone form fields |

## Space, shape and elevation

- 4 px grid: `--space-1` 4, `--space-2` 8, `--space-3` 12, `--space-4` 16, `--space-6` 24, `--space-8` 32, `--space-12` 48, `--space-16` 64.
- Radii: `--radius-xs` 4 (badges, kbd), `--radius-sm` 6 (marks, small buttons), `--radius-md` 8 (controls), `--radius-lg` 12 (panels, cards), `--radius-pill` 999 (counters, status badges).
- Control heights: `--control-sm` 26, `--control` 32, `--control-lg` 38, `--control-touch` 44 on touch.
- Shadows: `--shadow-sm` controls, `--shadow` panels, `--shadow-lg` dialogs.
- Motion: `--transition` (0.2s ease) for hover and state changes.

## Components

Patterns from Archiwista; use tokens only. The kit's elements, the base-map switcher among them, are under Kit.

Button (default, primary, ghost, small):

```css
.btn { height: var(--control); padding: 0 var(--space-3); border: 1px solid var(--line-2); border-radius: var(--radius-md); background: var(--surface); color: var(--text); font: var(--weight-medium) var(--text-base)/1 var(--font-sans); transition: background var(--transition); }
.btn:hover { background: var(--surface-2); }
.btn.primary { background: var(--accent); border-color: var(--accent); color: var(--accent-ink); }
.btn.primary:hover { background: var(--accent-hover); }
.btn.ghost { background: transparent; border-color: transparent; }
.btn.sm { height: var(--control-sm); border-radius: var(--radius-sm); font-size: var(--text-sm); }
```

Input and select (on phones `font-size: 16px` so iOS does not zoom):

```css
.input { height: var(--control); padding: 0 var(--space-2); border: 1px solid var(--line-2); border-radius: var(--radius-md); background: var(--surface); color: var(--text); }
@media (pointer: coarse) { .input { height: var(--control-touch); font-size: var(--text-site); } }
```

Focus ring:

```css
:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
```

Panel or card:

```css
.panel { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow); padding: var(--space-4); }
```

Status badge:

```css
.badge { border-radius: var(--radius-pill); padding: 0 var(--space-2); font-size: var(--text-xs); }
.badge.ok { background: var(--ok-bg); color: var(--ok-ink); }
.badge.bad { background: var(--bad-bg); color: var(--bad-ink); }
```

Format chip:

```css
.chip { font: var(--text-xs) var(--font-mono); border: 1px solid var(--line-2); border-radius: var(--radius-xs); padding: 0 var(--space-1); color: var(--text-2); }
```

Code block or sidecar:

```css
pre { background: var(--code-bg); color: var(--code-text); font-family: var(--font-mono); border-radius: var(--radius-md); padding: var(--space-3); }
```

App header: height `--header-height`, mark at 24 px plus the tool name in `--tool-<name>`; everything else neutral.

```css
.app-header { height: var(--header-height); display: flex; align-items: center; gap: var(--space-2); background: var(--surface); border-bottom: 1px solid var(--line); }
.app-header img { width: 24px; height: 24px; }
.app-header .name { color: var(--tool-hydrograf); font-weight: var(--weight-bold); }
```

Chart (DEV-15.16, ECO-090): every chart over axes is drawn by the kit's chart module (Kit, Charts): the grid in `--line`, ticks and axis labels in `--text-3`, the series `s1` to `s6` in colours mixed from `--info`, `--warn`, `--accent-green` and `--bad`, the readout's box in `--surface` with a `--line-2` border, the selection in `--focus`.
A chart whose x is `date`, `datetime`, `time`, `linear` or `log` shows a range of it; one of probabilities (`gumbel`), of named bars (a `band` y) or that its GUI draws with `zoom: false` (a year's months or days) does not.

| To | Mouse and trackpad | Touch | Keys and buttons |
| --- | --- | --- | --- |
| Show a range of x | a drag over the plot of at least 6 units of the viewBox, else a click; on a chart of points (`zoom: "xy"`) a rectangle of x and y | | |
| Zoom in or out | Ctrl with the wheel around the cursor, 1.25 a notch, and a trackpad's pinch in proportion | two fingers pinch around their middle | `+` and `−` around the readout, else the middle; „+” and „−” under the chart |
| Pan | Shift with a drag, or a drag with the middle button, within the whole | two fingers | an arrow past the edge of the range moves it a quarter on |
| Show the whole | a double click | | `0`; „Cały zakres” |
| Read the values | the pointer | one finger along the plot | arrows, Shift or Page Up and Page Down ten steps, Home, End; Esc hides the readout |
| Scroll the page | the wheel alone | one finger up or down | |

The y axis fits the values in the range shown; on a chart of points it is the person's. Every zoom in stops at four points of the readout's series in the range, on a chart without a readout at a thousandth of the whole, and a burst of wheel, pinch or pan events draws once an animation frame.
Under a zoomable chart the bar: a lone „+” before a zoom; then „−”, „+”, „Cały zakres” and the range shown in the axis's format, `x` and `y` both on a chart of points, which a reset folds back to „+”. It is one line at 390 px, the range cut with an ellipsis and whole in its tooltip; its buttons are the GUI's `.btn.sm`, at least 24 × 24 px (WCAG 2.2 SC 2.5.8).
A zoomable chart keeps one finger's vertical move for the page's scroll (`touch-action: pan-y`) and up to 860 px is drawn at its container's width; a chart that does not zoom leaves the touch to the browser and keeps its 560 px minimum, scrolling sideways.
The live region says the readout and, after each zoom, the range shown; the SVG has `role="img"`, the chart's title and an `aria-description` of its keys and gestures.

The module's own words are `CHART_TEXTS`, in Polish; a GUI in another language passes its own as `spec.texts`, every key, the placeholders kept:

| Key | Polish | Where |
| --- | --- | --- |
| `zoomIn` | Przybliż | the name of „+” |
| `zoomOut` | Oddal | the name of „−” |
| `reset` | Cały zakres | the button that shows the whole; the live region after it |
| `range` | {from} – {to} | the range shown |
| `rangeXY` | {x}: {xFrom} – {xTo}, {y}: {yFrom} – {yTo} | the range shown on a chart of points, `x` and `y` the axes' `short` |
| `returnPeriod` | T [lata] | the second row of a probability axis, under „p [%]” |
| `probabilityReadout` | p = {p} % · T = {years} lat | the readout's heading on a probability axis |
| `keysReadout` | Strzałki w lewo i w prawo: odczyt wartości; Shift albo Page Up i Page Down: dziesięć kroków; Home, End: początek i koniec; Esc: ukryj odczyt. | the `aria-description` of a chart with a readout |
| `keysZoom` | Plus i minus: przybliż i oddal; strzałki za brzegiem zakresu: przesuń go; 0, podwójne kliknięcie albo „Cały zakres”: cały zakres; przeciągnij po wykresie, aby pokazać jego część; Ctrl z kółkiem myszy: przybliż w miejscu kursora; Shift z przeciąganiem albo przeciąganie środkowym przyciskiem myszy: przesuń; na ekranie dotykowym dwa palce: przybliż i przesuń. | the `aria-description` of a zoomable chart, after `keysReadout` |
| `imageFailed` | Przeglądarka nie zdołała zapisać wykresu jako obrazu. | the error of `toPng` |

## Layout

The app shell comes from Archiwista; use it for every tool with a map or a workspace.

- Shell: a grid of two columns (64 px rail, content) and two rows (`--header-height`, content).
- Top bar spans both columns: `--surface`, bottom border `--line`. Left to right: mark at 24 px and the tool name in `--tool-<name>`, then the context (project, area, selection), then actions on the right.
- Operator's mark (DEV-15.3, ECO-079): on an instance an operator other than the author runs, the top bar may show the operator's logo, at most 24 px high, and name right of the tool name, after a 1 px `--line` divider, the name in `--text-2` at `--weight-medium`. The project's mark and name stay first and the favicon stays the project's mark; the logo is a file of the deployment served from the GUI's own origin (no other server, no new CSP origin), as `<img>` with the operator's name as `alt`, never inlined.
- Navigation rail: dark column of `.rail-item`s, 54 px wide, icon over a short label, `--radius-md`. Background `--rail-bg`, items `--rail-ink`, hover `--rail-hover`, active `--rail-active` with `--rail-ink-active`.
- Regulamin (DEV-15.7, ECO-070): a public GUI ends its rail, or its left navigation where it has no rail, with a small, quiet link „Regulamin” to its `regulamin.html`, opened in a new tab (`target="_blank"`, `rel="noopener"`): `.rail-terms` at the foot, `--text-xs` in `--rail-ink`, no icon, hover `--rail-ink-active` and underlined. No footer or status bar carries the link or a statement (DEV-15.8).
- Content: `.view-layout` grid of left panel, centre, right panel. Left panel 260-560 px (default 300), right panel 340-720 px (default 400), centre at least 480 px.
- Resizer: 10 px hit area on the panel edge with a 2 px line; on hover or drag a 36 px thumb in `--accent`. Focusable: arrow keys move 16 px, Shift+arrow 64 px, double-click resets the default width.
- Centre: a 46 px `.map-bar` (segmented control for the view plus a short hint) over the map.
- Map controls: legend bottom-left, zoom bottom-right. Secondary results (a terrain profile, a table) open as drawers at the bottom of the centre. No floating glass cards over the map.

```css
.shell { display: grid; grid-template-columns: 64px minmax(0, 1fr); grid-template-rows: var(--header-height) minmax(0, 1fr); height: 100vh; background: var(--bg); }
.topbar { grid-column: 1 / -1; display: flex; align-items: center; gap: var(--space-3); padding: 0 var(--space-4); background: var(--surface); border-bottom: 1px solid var(--line); }
.rail { display: flex; flex-direction: column; align-items: center; gap: var(--space-1); padding: var(--space-2) 0; background: var(--rail-bg); }
.rail-item { width: 54px; padding: var(--space-2) 0; border-radius: var(--radius-md); color: var(--rail-ink); font-size: var(--text-xs); text-align: center; }
.rail-item:hover { background: var(--rail-hover); }
.rail-item.active { background: var(--rail-active); color: var(--rail-ink-active); }
.rail-terms { margin-top: auto; padding: var(--space-2) 0; color: var(--rail-ink); font-size: var(--text-xs); text-decoration: none; }
.rail-terms:hover { color: var(--rail-ink-active); text-decoration: underline; }
.view-layout { --left-w: 300px; --right-w: 400px; display: grid; grid-template-columns: var(--left-w) minmax(480px, 1fr) var(--right-w); min-height: 0; }
.resizer { width: 10px; cursor: col-resize; }
```

Phone (width <= 860 px):

- Top bar 48 px.
- The rail becomes a 58 px bottom bar: `--surface` background, `--line` top border, items in `--text-2`, active item in `--accent`. `.rail-terms` stays as its last small item, in `--text-3`; a GUI whose left navigation becomes a bottom sheet keeps it as the sheet's last item.
- Panels become bottom sheets: fixed above the bar (bottom 58 px), height `min(74vh, 640px)`, radius 16 px on the top corners, with a grip, a title and a close button. Resizers are hidden.
- Form fields use 16 px text so iOS does not zoom.

## Info texts

The text behind „(i)”, in a help popover or in „Objaśnienie metod” follows DEV-15.14 (ECO-069): a definition, then the formula, how to read the value and the sources where they apply; Polish and impersonal; at most about 400 characters without the formula and the sources.
It names no program, file, plan step or development status; a longer explanation goes to the GUI's guide, which it links.
A good one:

```text
Opad efektywny Pₑ

Część opadu, która odpływa po powierzchni terenu; reszta wsiąka w glebę
lub zostaje zatrzymana przez roślinność i zagłębienia terenu.

Pₑ = (P − 0,2·S)² / (P + 0,8·S) dla P > 0,2·S, w przeciwnym razie Pₑ = 0
S = 25 400 / CN − 254
gdzie: P – opad całkowity [mm], S – retencja maksymalna zlewni [mm],
CN – parametr krzywej odpływu, 30–100 [–]

Im wyższy CN, tym większa część opadu odpływa. Przy CN = 80 z opadu
50 mm odpływa około 14 mm.

Źródła: USDA-NRCS 2004, National Engineering Handbook, cz. 630, rozdz. 10
```

## Marks

- Frame: 32x32 rounded square, `rx="6"`, filled with `--mark-frame` `#0d1117` in both themes.
- Line art: stroke 2.5, round caps and joins, in the tool's dark-theme accent.
- Nogat: the two waves of debever.pl's favicon.
- Every other tool: one family wave at the bottom plus its glyph:
  - Archiwista: archive drawer
  - Hydrograf: hydrographic network (reaches and cross sections, as in HEC-RAS's geometry editor)
  - Kartograf: folded map
  - Obserwator: staff gauge
  - Hydrolog: hydrograph
  - Hydraulik: channel cross-section
  - Retman: boat with pennant
- Use as favicon (`<link rel="icon" type="image/svg+xml" href="...">`) and in the header at 24 px.
- Never recolour, stretch or add effects. Minimum size 16 px.

## Tool identity

| Project | Token | Accent light | Accent dark | Mark |
| --- | --- | --- | --- | --- |
| Nogat | `--tool-nogat` | `#284b63` | `#58a6ff` | [nogat.svg](marks/nogat.svg) |
| Archiwista | `--tool-archiwista` | `#4a776c` | `#7fbfae` | [archiwista.svg](marks/archiwista.svg) |
| Hydrograf | `--tool-hydrograf` | `#12708a` | `#4cc3e0` | [hydrograf.svg](marks/hydrograf.svg) |
| Kartograf | `--tool-kartograf` | `#8a5a1c` | `#d9a35f` | [kartograf.svg](marks/kartograf.svg) |
| Obserwator | `--tool-obserwator` | `#3b5bab` | `#8fa9f5` | [obserwator.svg](marks/obserwator.svg) |
| Hydrolog | `--tool-hydrolog` | `#3f7a3a` | `#7cc474` | [hydrolog.svg](marks/hydrolog.svg) |
| Hydraulik | `--tool-hydraulik` | `#5e4fa2` | `#b0a3f0` | [hydraulik.svg](marks/hydraulik.svg) |
| Retman | `--tool-retman` | `#a4472f` | `#f0907a` | [retman.svg](marks/retman.svg) |

The tool accent appears only in the mark, the tool name and an optional 2-3 px header rule.
The shared `--accent` stays the interactive colour everywhere.
A new project gets a mark and a `--tool-<name>` pair in both themes; the contract test requires one per project in `ecosystem.yaml`.

## Kit

Plain files in [kit/](kit/), copied byte for byte into each GUI and never edited there (DEV-15.6); `uv run scripts/ecosystem.py drift` names every copy that is behind or modified.
`nogat-kit.json` holds the kit version and the SHA-256 of each file; `tests/contract/test_kit_manifest.py` fails when they disagree.
The version, `1.3.0` since ECO-089 and ECO-090, moves only with the author's consent (REL-1.4, ECO-072): a change to a kit file updates its hash, never the version, and a copy is compared with Nogat's by the hashes.

App menu (DEV-15.4): link `nogat-app-menu.css`, load `nogat-app-menu.js` as a module, and put the element in the top bar left of the theme switch.

```html
<nogat-app-menu current="hydrolog" marks="nogat/marks/" terms="regulamin.html"></nogat-app-menu>
```

The app sets `element.apps` (or the `apps` attribute, as JSON) to the deployment's `[nogat.gui]` table of `nogat.toml`, e.g. `{"hydrograf": "https://hydrograf.example/", "archiwista": "/archiwista/"}`.
Addresses resolve against the page; only http and https stay. With no GUI but the current one the element is not drawn. An entry opens its GUI in the tab `nogat-<name>`: Chromium reuses that tab unless one of the two pages sends `Cross-Origin-Opener-Policy`, which costs one more tab.
The menu styles itself with the tokens and falls back to light values, so a GUI without `tokens.css` shows it too.
The `terms` attribute, the address of the GUI's filled terms (DEV-15.7), ends the list with the link „Regulamin”, opened in a new tab (`target="_blank"`, `rel="noopener"`) so the GUI's own tab and its session stay; the rail's link stays too (Layout), since the menu is not drawn without another GUI.

Sources (DEV-20.5, DEV-20.7, ECO-064): link `nogat-sources.css`, load `nogat-sources.js` as a module, and put one element per view where its data end, e.g. under the map or at the foot of the panel; never one per card or popup.

```html
<nogat-sources attribution='["Źródłem pochodzenia danych jest …"]' terms-notice='["Regulamin danych IMGW-PIB: …"]' terms="regulamin.html"></nogat-sources>
```

| Attribute or property | Value |
| --- | --- |
| `attribution` (attribute, JSON) or `element.attribution` (array) | The full lines the view's data carry, the API's `attribution`: the union over the data shown |
| `terms-notice` (attribute, JSON) or `element.termsNotice` (array) | The API's `terms_notice`, the links to the providers' terms (RD, RH, RK) |
| `terms` | The address of the GUI's `regulamin.html` (DEV-15.7); omitted where the GUI serves none |
| `screen-lines` (attribute, JSON) or `element.screenLines` (array) | The lines the GUI declares for the strip beyond the element's own (DEV-20.5, ECO-087): `[{"text": "…", "short": "…", "links": [["…", "https://…"]]}]`, `short` and `links` optional; below |

The strip is 12 px in `--text-3`: of the full lines it shows S, P, PS and PP, recognised byte for byte, and the short forms of C, G, SG and Z (DEV §20), each once in the order of DEV-20.4, then the button „Źródła i warunki”.
C is shown as CK „Źródło: ČHMÚ, CC BY 4.0” with „ČHMÚ” and „CC BY 4.0” linked; every G, recognised by its text around `<products>`, `<period>` and `<date>`, as one GK „Źródło: GUGiK (`<products>`)” naming the products of all of them, each once; SG as SK „Źródło: ISRIC SoilGrids, CC BY 4.0” and every Z as one ZK „Źródło: ČÚZK, CC BY 4.0”, „CC BY 4.0” linked in both.
Any other line (M, CP, another provider's) is shown only in the dialog unless the GUI declares it in `screen-lines`, so a GUI passes its arrays unchanged, never a short form; with both arrays empty the element is not drawn.
A declared line is `{text, short, links}`: `text` a full line, byte for byte as `attribution` carries it; `short`, optional, the text the strip shows in its place, only for a provider the tables of DEV §20 do not hold and as its deployment gives it; `links`, optional, pairs of a word of the shown text and its http or https address, resolved like `terms`, each word linked at its next occurrence and a word not found or another address left plain; without `links` the shown text's addresses are linked, as in S.
The strip shows a declared line only while `attribution` carries its `text`, after its own lines, in the order declared and each once; a line the element shows itself is not repeated, and the dialog keeps the full line. Without `screen-lines` the strip is unchanged. The line of an operator's own network, which the deployment declares (DEV-20.4), comes so:

```html
<nogat-sources attribution='["…", "Źródło danych: Wodociągi Przykładowe Sp. z o.o., https://pomiary.example.pl"]' screen-lines='[{"text": "Źródło danych: Wodociągi Przykładowe Sp. z o.o., https://pomiary.example.pl", "short": "Źródło: Wodociągi Przykładowe", "links": [["Wodociągi Przykładowe", "https://pomiary.example.pl"]]}]'></nogat-sources>
```

On a screen up to 860 px wide (ECO-080) the strip is one line: the lines start on it and are cut with an ellipsis, followed by „więcej” and „Źródła i warunki”; „więcej” shows only while the line cuts them and unfolds the strip in place, wrapped, as „zwiń”. `element.expanded` (the attribute `expanded`) is that state, and the element carries `clipped` while its folded line cuts the lines. A GUI that lays the strip out itself (e.g. inline with a basemap credit) keeps its own rules above 860 px only, so the fold applies on a phone.
The button opens a modal `<dialog>` with every line, the terms lines and „Regulamin serwisu”, which opens in a new tab like the menu's „Regulamin”: Tab stays inside it, Esc, „Zamknij” and a click on the backdrop close it, and focus returns to the button.
`element.open()` and `element.close()` do the same from code; the element fires `nogat-sources-open` and `nogat-sources-close`, both bubbling.
A GUI with its own welcome window fills it with `fillSources(container, {attribution, termsNotice, terms})` from the same module, which writes the dialog's content into `container`; given `terms`, its „Regulamin serwisu” is the welcome window's regulamin link (DEV-15.7), so the window carries no second one. The module also exports `LINES` (S, P, PS, PP, C, CK, CP, G, GK, SG, SK, Z, ZK, as DEV §20 writes them, a value as `` `<name>` ``), `SOURCES_TEXTS` and `screenMarks(attribution)`; an old CP line with parenthetical detail is displayed as the canonical CP once (DEV-20.4).
The element loads nothing and needs no inline script or style, so it runs under CSP `'self'`.

Charts (DEV-15.16, ECO-090): link `nogat-chart.css`, import `drawChart` from `nogat-chart.js` and draw each chart into an element of its own. A GUI keeps a wrapper of its own of some 20 lines, a Preact component or a function of its scripts, that draws on mount, calls `update` when its spec changes and `destroy` when it goes.

```js
import { drawChart } from "./nogat/nogat-chart.js";
const chart = drawChart(element, {
  title: "Przepływ dobowy",
  x: { scale: "date" },
  y: { label: "Q [m³/s]", unit: "m³/s", zero: false, digits: 1 },
  series: [{ id: "q", label: "Q", data: days.map((day) => [day.number, day.flow]) }],
  readout: true,
  fit: { ratio: 0.42, minHeight: 210 },
  onRange: (range) => writeAddress(range),   // Archiwista's from and to
});
```

| Field of the spec | Value |
| --- | --- |
| `x` | `{label, scale, min, max, domain, digits, short, tickList, tickLabels}`; `scale`: `linear` (the default), `log`, `time` (minutes: ticks in minutes on a short axis, else in hours, the `{unit}` of `label` written `min` or `h`), `date` (day numbers, days since 1970-01-01: years, months or days), `datetime` (fractional day numbers of UTC instants: the reader's hours and days) or `gumbel` (the exceedance probability [%], ticks of p and T = 100 / p, `domain: [99, 0.1]` its ends); `tickList: [{value, label, sub}]` in place of the computed ticks; `tickLabels: false` draws the axis without its labels, so panels one above another share one time axis under the last |
| `y` | `{label, unit, scale, min, max, zero, pad, ticks, digits, short, width}`; `scale`: `linear`, `log` or `band`, one horizontal bar per point `{x: value, y: name, sub, cls, text}`; `zero: false` for an axis that need not hold 0; `width` the space left of the plot, so charts one above another align |
| `y2` | the same for a second axis: a panel above the main one sharing x, its bars hanging from its top (`share` its part of the height: a hyetograph over a hydrograph), or with `side: "right"` a second unit right of the main panel (`width` the space right of the plot) |
| `series` | `[{id, kind, data, axis, cls, label, unit, digits, width, align, shape, readout, legend}]`; `kind`: `line` (the default), `step`, `area`, `band` (`[x, lo, hi]`, a min–max envelope), `bars`, `points` or `rug` (x values); `data`: `[x, y]` pairs or `{x, y, cls, shape}`, a point without a value breaking a line, each `data` a new array when its values change; `shape` of points: `dot`, `hollow` or `diamond`; `cls`: `s1` to `s6`, `bar-p`, `bar-pe` or a GUI's own class |
| `marks` | `{kind: "peak", x, y, label, cls, guides}`, `{kind: "hline", y, label}`, `{kind: "vline", x, from, to, extend, label}`, `{kind: "note", x, y, label, dx, dy, anchor}`, `{kind: "span", from, to, cls}` (a grey band over a range of x: a gap); `axis: "y2"` on the second axis |
| `legend` | `true`, the labelled series, or items `{label, kind, cls, shape}` (`kind: "text"` a note, `"stroke"` a line drawn as the curves are, `"break"` a new line) |
| `readout` | `true` or `{series, x: (x) => text, value: (value, series) => text}` |
| `zoom` | by the x's scale as above; `false` none; `"xy"` x and y alike, by a rectangle, Ctrl with the wheel, a pinch and the keys (Obserwator's rating curve, PMAXTP) |
| `size`, `fit` | `"wide"` (760 × 432, the default), `"small"` (360 × 178) or `{width, height}`; `fit: {ratio, minHeight}` draws the chart at its container's width, again when it changes |
| `title`, `labelledBy` | the chart's name, or the id of the element naming it |
| `texts`, `locale`, `dateFormat` | words over `CHART_TEXTS`; the language of the numbers and dates of the ticks, the readout and the bar, `pl-PL` by default (`en-GB`: a decimal point, `01/11/1950`, `Jan 2020`); a day as the GUI writes it where it differs from its language's, a pattern of `YYYY`, `MM` and `DD` (Archiwista's `YYYY.MM.DD`: the readout `2020.03.02`, ticks `2020.03.02`, `03.05` and months `2020.01`) |
| `onReadout(index)` | the readout moved to that index of its series' `data`, `null` when it hid (Hydrograf's profile moves its map marker) |
| `onRange(range)` | a person settled a range: at the end of a drag, a pinch or a key, the wheel idle 200 ms; `{min, max, width}` with `y` on a chart of points, `width` the plot's width in CSS px (Archiwista's `max_points`), `null` the whole |

| Member of the handle | Use |
| --- | --- |
| `update(spec)` | Redraws in place, the GUI's language switch too (new `texts`, `locale`); the range shown outlives a spec of the same data (every series' `data` the same array, the same x) and is reset by new data |
| `zoom.set(min, max, y)`, `zoom.reset()`, `zoom.range()` | Shows a range, as an address's `from` and `to` give it back, or the whole, never calling `onRange`; the range shown, `null` the whole |
| `readout.show(index)`, `readout.hide()`, `readout.index()` | The readout at an index of its series' `data` |
| `plotWidth()` | The plot's width in CSS px |
| `svg`, `destroy()` | The chart's SVG, for `toPng`; empties the element |

| Export | Use |
| --- | --- |
| `drawChart(element, spec)` | The chart and its handle |
| `toPng(svg, {footer, scale, background, texts})` | Resolves to a PNG of a drawn SVG, a chart as shown (its range, its y fitted, without the readout and the selection) or another (Hydrolog's network schematic), on `--surface`, `scale` (2) times its drawn size, with `footer`, the providers' lines of its data (DEV-20.5), under it; while the module reads its styles the SVG has the class `nogat-chart-exporting`, under which a GUI hides what a picture leaves out; the file's name is the GUI's (DEV-19.21) |
| `svgText(svg)` | The SVG with its styles, as `toPng` draws it |
| `CHART_TEXTS` | The words (Components, Chart) |
| `chartFormat({locale, dateFormat})` | The chart's numbers (`number(value, digits)`), times and days, for a table beside it |
| `extent`, `niceStep`, `stepDigits`, `niceDomain`, `linearTicks`, `logDomain`, `logTicks`, `timeDomain`, `timeTicks`, `dateDomain`, `dateTicks`, `datetimeDomain`, `datetimeTicks`, `gumbelDomain`, `gumbelTicks`, `linearScale`, `logScale`, `gumbelScale`, `reducedVariate`, `exceedanceFromVariate`, `thinPoints` | The scales, ticks and decimation the module draws with, pure functions; a tick function takes a `chartFormat` last |

`nogat-chart.css` scopes every rule by `.nogat-chart`, which the module sets on the element, and prefixes the classes outside the SVG (`nogat-chart-legend`, `nogat-chart-zoom`), so it meets none of a GUI's own classes; the series' colours `--series-1` to `--series-6`, `--rain` and `--rain-eff` are set on `.nogat-chart`, and every token has its light value as fallback, so a GUI without `tokens.css` draws its charts in the light theme. A class of one view's series (PMAXTP's ramp, a fit's line) stays in the GUI's CSS.
The module loads nothing and writes no style attribute, so it runs under CSP `'self'`, `toPng` with `img-src 'self' data: blob:`, as `tests/browser/test_chart.py` runs it.

Hand-off (DEV-15.5): `import * as handoff from "./nogat/nogat-handoff.js"`.

| Export | Use |
| --- | --- |
| `TEXTS.copyTo(name)`, `TEXTS.file`, `TEXTS.loadFrom(name)`, `TEXTS.openFile`, `TEXTS.paste`, `TEXTS.open(name)` | The labels: „Kopiuj do Hydrologa”, „Plik przekazania”, „Wczytaj z Hydrografa”, „Plik przekazania…”, „Wklej ze schowka”, „Otwórz Archiwistę” |
| `copyHandoff(doc, field)` | Clipboard in a secure context; otherwise the text goes selected into `field` and the result is `"field"` (show `TEXTS.copyByHand`) |
| `downloadHandoff(doc)` | Saves `<producer>_handoff_<subject>.json` (DEV-19.21), the producer `doc.producer.tool`, the subject through `nameSlug` (`hydrograf_handoff_kamiennik-swierzawa.json`, `hydrograf_handoff.json` when nothing of it remains), 2-space JSON with a final newline; returns the name |
| `fileName(subject, producer)`, `nameSlug(text)` | That name; a person's text as a part of a file name: lower-case ASCII without diacritics, each run of other characters one `-`, none at either end (`Kamiennik — Świerzawa` → `kamiennik-swierzawa`), for a GUI's own downloads too |
| `readFile(file)`, `readClipboard()` | The text of a picked file; the clipboard's, or `null` when refused (offer a field, `TEXTS.pasteByHand`) |
| `readHandoff(text, envelope)` | Parses and checks the envelope against the GUI's copy of `handoff-1.schema.json`: `{doc, problems}` with Polish messages |
| `validate(value, schema)` | The same check for a payload against its owner's schema (draft 2020-12, local `$ref`s) |

Basemaps (DEV-15.15, ECO-089): [nogat-basemaps.json](kit/nogat-basemaps.json) is the catalogue of the base maps every GUI with a map offers, in its order: `openfreemap`, „OpenFreeMap szary”, OpenFreeMap's TileJSON drawn in the kit's grey style and the default; `gugik-osm`, „OSM GUGiK szary (tylko Polska)”, and `gugik-ortho`, „Ortofotomapa GUGiK”, both in Poland's box and never the default, since GUGiK's services are often unstable. The GUI's server reads it for its setting, its CSP and its regulamin's blocks, and hands its page the entries the deployment allows, then the deployment's own base maps in the same shape.

| Field of an entry | Value |
| --- | --- |
| `id`, `label` | The id the settings and the browser keep; the switcher's Polish label |
| `kind` | `vector`: `url` is a TileJSON of the OpenMapTiles schema, drawn in the kit's grey style; `raster`: `url` is a tile template with `{z}`, `{x}` and `{y}`, or a WMS with `{bbox-epsg-3857}` |
| `url`, `origin` | The address and its origin, the only one the GUI's CSP names for the entry; a TileJSON's tiles must stay on it |
| `minzoom`, `maxzoom`, `bounds` | The zooms of the tiles and the box `[west, south, east, north]` no request leaves |
| `grey` | A raster drawn grey: MapLibre's `raster-saturation: -1`, Leaflet's class `nogat-basemap-grey` |
| `default` | Whether a GUI may open on it: the first allowed entry with `true`, else „bez podkładu” |
| `credit` | `{text, links}`: the words the map's attribution shows, in Polish on every page, and `[word, address]` pairs linking them |
| `blocks` | The regulamin's blocks the entry needs: `osm` with `openfreemap` or `gugik-osm`, `gugik` with `gugik-osm` or `gugik-ortho` |

The settings are shared keys of `[nogat]` (DEV-18.1), which `[<tool>]` and the environment override (`NOGAT_BASEMAPS` or `<TOOL>_BASEMAPS`, the ids joined by `,`):

```toml
[nogat]
basemaps = ["openfreemap", "gugik-osm", "gugik-ortho"]   # the default, every entry; [] none
basemap_mirrors = { openfreemap = "https://kafle.example.org/planet" }   # a copy in its provider's place

[[nogat.basemap_extra]]   # a base map of the deployment's own
id = "gmina"
name = "Mapa gminy"
kind = "xyz"              # xyz, wms, or vector: a TileJSON of the OpenMapTiles schema
url = "https://kafle.example.org/gmina/{z}/{x}/{y}.png"
attribution = "© Gmina Przykładowa"
grayscale = false
```

An unknown id, or an own base map without its credit or with an id of the catalogue, stops the server at start with an error document naming the key (`details.option`, `details.value`). A copy in `basemap_mirrors` keeps its entry's label, style and credit, its origin taking the provider's place. An own base map reaches the page in the catalogue's shape: `label` its `name`, `kind` `raster` (a WMS made a tile template with `{bbox-epsg-3857}`) or `vector`, `origin`, `default` false, `credit` its `attribution` as given and no `blocks`; the browser asks its origin directly, never through the server, and no visitor adds a base map.
The CSP's `img-src` and `connect-src` name the origins of the allowed entries (a copy's in its entry's place), of the own base maps and of the GUI's own map layers, and no scheme source: with every entry `https://tiles.openfreemap.org` and `https://mapy.geoportal.gov.pl`. `worker-src` stays the library's: `'self'` for MapLibre 6, `blob:` for MapLibre 4 under maplibre-gl-leaflet. A public GUI keeps the regulamin's blocks its allowed entries name.

The switcher: link `nogat-basemaps.css`, load `nogat-basemaps.js` as a module, put `<nogat-basemaps></nogat-basemaps>` where the GUI's layers are, under its heading `BASEMAP_TEXTS.group` („Podkłady kartograficzne”), give it the entries, draw its `value` and draw again on its `change`:

```js
import { maplibreBasemap, removeMaplibreBasemap } from "./nogat/nogat-basemaps.js";
const switcher = document.querySelector("nogat-basemaps");
switcher.entries = session.basemaps;   // what the server allows, then its own
const show = (id) => {
  const entry = switcher.entries.find((candidate) => candidate.id === id);
  if (!entry) return removeMaplibreBasemap(map);
  const onFailure = (failed) => switcher.fail(failed);
  maplibreBasemap(entry, { map, glyphs: GLYPHS, before: "stations", onFailure }).catch(() => {});
};
show(switcher.value);
switcher.addEventListener("change", (event) => show(event.detail.id));
```

| Attribute or property of `<nogat-basemaps>` | Value |
| --- | --- |
| `element.entries` | The entries in the catalogue's shape: the catalogue's (those with `blocks`) first in their order, then the deployment's own, then „bez podkładu”; with none the element is not drawn |
| `element.value` | The id shown, `"none"` for „bez podkładu”: the person's choice while it is offered, else the first entry whose `default` is true, else `"none"`; setting it fires no event |
| `element.texts` | The words, `BASEMAP_TEXTS` by default: `group`, `name` (the radio group's „Podkład kartograficzny”), `none`, `failed` („Podkład nie odpowiada”), `credit` (the name of the credit's „i”) and `labels` by id in place of the entries' own; a GUI in another language passes its own |
| `element.fail(id)`, `element.failed` | Marks an entry „Podkład nie odpowiada” until the person chooses it again; the ids marked |
| `remember` | `browser`, the default: a person's choice is kept in `localStorage` under `nogat-basemap`, no server and no cookie, as § 8 ust. 7 of the regulamin says; `none`: nothing is kept and the GUI sets `value`, as Archiwista's account preference in its team mode |

The element fires `change` (bubbling) with `detail.id` when a person picks a base map, the radios' own `change` staying inside; arrow keys move between the radios.

| Export | Use |
| --- | --- |
| `maplibreBasemap(entry, {map, glyphs, locale, colors, before, onFailure})` | MapLibre GL JS: draws the entry on `map` under the layer `before`, the GUI's lowest overlay, in place of the kit's base map drawn before, and resolves to `{sources, layers}`; without `map` it only builds them. A vector entry asks its TileJSON first and checks that its tiles stay on the entry's origin; a failure calls `onFailure(id)` and rejects before any tile is asked. First tiles that fail take the base map off and call `onFailure(id)`; the overlays stay and nothing switches by itself. A call that a later one or a removal overtakes rejects with an `AbortError` and draws nothing |
| `removeMaplibreBasemap(map)` | „bez podkładu” |
| `repaintMaplibreBasemap(map, colors)` | Repaints the vector base map after the GUI switches its theme |
| `leafletBasemap(L, entry, {glyphs, locale, colors, onFailure, texts})` | Leaflet: resolves to a layer the GUI adds and removes, `L.tileLayer` under the other tile layers or, for a vector entry, `L.maplibreGL` of maplibre-gl-leaflet in the kit's grey style; it fails as above and takes itself off the map, and a vector layer's theme is repainted through `repaintMaplibreBasemap(layer.getMaplibreMap())` |

`glyphs` is the GUI's vendored glyph template, `…/{fontstack}/{range}.pbf`, holding the font `noto-sans-regular` (Obserwator's and Archiwista's Noto Sans 2.0); `locale` the page's language, the names in `name:<locale>`, else Latin, else local (`pl` by default); `colors` the grey style's colours by name over those of `nogat-basemaps.css`, which gives them in both themes as `--nogat-basemap-bg`, `-landuse`, `-water`, `-road`, `-state`, `-country`, `-water-text`, `-halo` and `-place-1` to `-place-4`. A MapLibre map keeps an `error` listener of the GUI's own, since a tile that fails once its base map is drawn is no fault of the page.
The credit is the entry's, never its TileJSON's and never in `<nogat-sources>` (DEV-20.5, DEV-20.9): in the map's own attribution control in its corner, which `nogat-basemaps.css` draws at 12 px in `--text-3` under the class `nogat-basemap-map` the adapters set on the map's container. Up to 860 px it shows when the map opens and folds behind „i” at the first drag, a tap showing it again: a MapLibre GUI creates its map with `attributionControl: {compact: matchMedia("(max-width: 860px)").matches}` and `locale: {"AttributionControl.ToggleAttribution": BASEMAP_TEXTS.credit}`, and the Leaflet adapter adds „i” to the map's attribution control itself.
The element and the adapters ask nothing but the base map's own requests and need no inline script or style, so they run under the GUI's CSP, as `tests/browser/test_basemaps.py` runs them on MapLibre 6.14.0 and on Leaflet 1.9.4 with maplibre-gl-leaflet 0.0.22 over MapLibre 4.7.1.

Terms (DEV-15.7, ECO-061 to ECO-063, ECO-065, ECO-066, ECO-068, ECO-070, ECO-071): [nogat-terms.md](kit/nogat-terms.md) is the regulamin in Polish, the source; `nogat-terms.html` is generated from it by `uv run scripts/ecosystem.py standard --write` and is never edited. A GUI copies both with `nogat-terms.css` into its kit directory, fills the HTML for its deployment and serves the result at `regulamin.html` beside its start page; no script, no remote resource, one stylesheet of the kit plus `tokens.css`. It links the page in exactly three places: the app menu's `terms`, the rail's `.rail-terms` (Layout) and, where it has one, the welcome window through `fillSources()`; the dialog of `<nogat-sources>` links it too.
The regulamin carries its own version („Wersja 1.1”, one for every GUI) and ends with „Historia zmian”, linked to the history of `nogat-terms.md` on Nogat's `develop`, where the published text lives; `main` is released only on the author's word. Version 1.0 was published on 2026-11-13 and republished on 2026-11-14; its corrections (ECO-068, ECO-071) are made in place. Version 1.1 names the base map among the settings the browser keeps (§ 8 ust. 7, ECO-089), with the author's consent of 2026-11-24. Only the author raises the version; an agent never does. A GUI publishes a corrected text with the kit that carries it, and the operator sets a new `terms_effective` only when the author asks for it.
Its § 3 opens with the author's statement of what the services are (DEV-15.8), which no view repeats in a footer or status bar; the template's fixed text describes the rate limit, the logs, the statistics and „Zgłoś uwagę” of DEV-15.9 to DEV-15.12, the logs as DEV-12.4 to DEV-12.9 keep them (§ 8 ust. 3), so a GUI serves the page only once it follows them.
Its § 5 says once that use of data taken from the service is governed by the providers' terms, and each data-source block holds only the provider's name, the lines it requires and the link to its terms or licence, never a summary of them (DEV-20.7, ECO-065). Its § 8 ust. 5 names the basemap and the map layers of the providers in § 5 as the only resources the visitor's browser fetches from other servers, which holds only while the GUI loads no script, style or font from elsewhere (DEV-15.7).

Filling, in this order (reference: `fill` in [scripts/terms.py](../scripts/terms.py)):

1. Blocks. A block is the lines between `<!-- block: <name> -->` and `<!-- /block -->`, each marker on a line of its own. Keep the lines of every block the project lists below, without the two marker lines; drop every other block with its markers.
2. Fields. Replace every `{{name}}` with its value, HTML-escaped (`&`, `<`, `>`, `"`, `'`). Every field needs a value, non-empty except `processor_transfer`, `processor_cookie` and `mail_transfer`, each a whole sentence or empty: with a field missing, or with a `{{` left, the GUI serves no page and no link.

The GUI fills at start or at build with its own code; a page filled from older kit files is filled again when the kit is copied.

| Field | Value from |
| --- | --- |
| `service_name` | the project: its name in the registry, e.g. `Hydrograf` |
| `service_url` | the deployment: the project's entry of `[nogat.gui]` in `nogat.toml` |
| `operator_name` | the deployment: `[nogat.operator] name` |
| `operator_email` | the deployment: `[nogat.operator] email`, published on the page |
| `terms_effective` | the deployment: `[nogat.operator] terms_effective`, the day the filled terms are published and take effect, e.g. `2026-11-20` |
| `processor` | the deployment: `[nogat.operator] processor`, who carries the traffic and processes IP addresses for the operator, e.g. `Cloudflare, Inc.` |
| `processor_transfer` | the deployment: `[nogat.operator] processor_transfer`, the sentence on that processor's transfers outside the EEA; empty without them |
| `processor_cookie` | the deployment: `[nogat.operator] processor_cookie`, the sentence on a cookie the processor sets to protect the service from bots, „Dostawca ruchu (Cloudflare, Inc.) może ustawić plik cookie niezbędny do ochrony serwisu przed botami; nie służy on śledzeniu.” with the processor's name; empty while it sets none |
| `mail_provider` | the deployment: `[nogat.operator] mail_provider`, the service holding the operator's mailbox, e.g. `iCloud Mail (Apple)` |
| `mail_transfer` | the deployment: `[nogat.operator] mail_transfer`, the sentence on that mail service's processing outside the EEA, „Mogą być przetwarzane poza Europejskim Obszarem Gospodarczym.”; empty without it |
| `software_licence` | the project: `license` of its `pyproject.toml`, e.g. `MIT` |
| `source_url` | the project: `repo` of its entry in `ecosystem.yaml` |
| `tokens_href` | the project: the address of its copy of `tokens.css`, relative to the page |
| `kit_href` | the project: the address of its kit directory with a final slash, relative to the page, e.g. `nogat/` |

```toml
[nogat.operator]          # a deployment open to others (DEV-15.7, DEV-18.1)
name = "…"
email = "…"
terms_effective = 2026-11-20
processor = "Cloudflare, Inc."
processor_transfer = "Dane mogą być przekazywane do USA na podstawie decyzji Komisji Europejskiej w sprawie EU-U.S. Data Privacy Framework."
processor_cookie = ""
mail_provider = "iCloud Mail (Apple)"
mail_transfer = "Mogą być przetwarzane poza Europejskim Obszarem Gospodarczym."
```

A move to a host that keeps the data in the EEA changes `processor` and sets `processor_transfer = ""`; the text of the terms stays. `processor_cookie` is set once the processor's zone sets a cookie of its own (Cloudflare: Bot Fight Mode, challenges), and the zone runs no analytics beacon, since the terms say the service uses no external analytics. The server is the operator's own hardware, so no hosting provider is named; a move to a hosted server adds that provider to the terms in a new version.

| Block | Kept for | GUIs, as a start to check in each adoption |
| --- | --- | --- |
| `imgw` | IMGW-PIB data of danepubliczne.imgw.pl | Obserwator; Hydrolog with station series |
| `imgw-hydro` | IMGW-PIB data of hydro.imgw.pl and hydro-back.imgw.pl | Obserwator |
| `pmaxtp` | PMAXTP | Hydrograf, Hydrolog, Obserwator |
| `chmu` | ČHMÚ open data | Obserwator; Hydrolog with station series |
| `camels-pl` | CAMELS-PL data: catchments, attributes and series of its Zenodo record (DEV-20.12) | Obserwator with CAMELS-PL, beside `imgw` |
| `e-obs` | CAMELS-PL's catchment means derived from E-OBS, only where the deployment serves them (DEV-20.12) | none by default |
| `gugik` | GUGiK data; the base maps `gugik-osm` and `gugik-ortho` of the kit's catalogue | Hydrograf, Obserwator; a GUI that allows either base map |
| `cuzk` | ČÚZK data | Obserwator |
| `copernicus` | Copernicus data | none |
| `isric` | ISRIC SoilGrids | Hydrograf |
| `wody-polskie` | flood hazard maps of Wody Polskie | Hydrograf |
| `osm` | OpenStreetMap base maps: the kit's `openfreemap` (OpenFreeMap's tiles) and `gugik-osm` (the OSM base map of geoportal) | a GUI that allows either base map: Hydrograf; Obserwator with a map |

Operator's terms (DEV-15.7, ECO-079): [nogat-terms-operator.md](kit/nogat-terms-operator.md) is a draft regulamin in Polish for an instance an operator other than the author runs on its own infrastructure, where the kit's regulamin, which names the author as a private, non-commercial operator, does not apply. It keeps the twelve sections, the Markdown, the fields and the data-source blocks of `nogat-terms.md`, so a GUI renders it with the subset of `build` and fills it with `fill` of [scripts/terms.py](../scripts/terms.py) as above, from the same values; it states that the operator is the service provider and the controller of personal data, that the software is provided as is under its licence without warranty or liability for availability, data or results, that keeping the data providers' terms is the operator's, and that the author's part ends with the deployment, and it adds what the act on electronic services asks of a provider acting in business: the technical requirements, the conclusion of the contract and complaints within 14 days.
It is a template, not legal advice, and opens with a comment saying so: a lawyer reviews it before an operator gets it and adapts it to the operator's deployment. The operator copies it into the deployment's own files, outside the GUI's checkout, writes in the fields below, checks § 3, § 4 and § 8 against the deployment and removes the comment; a GUI serves the operator's copy in place of the kit's page and refuses one that does not start with its `# ` title or keeps a field it does not fill. A GUI copies the draft with the rest of the kit, since its manifest lists it, but never serves it as its terms. The draft has no version of its own: the operator's copy is version 1.0 of the operator's regulamin, which the operator versions from then on.

| Field | Value from |
| --- | --- |
| `operator_address` | the operator, in its copy: its seat or address |
| `operator_register` | the operator, in its copy: the register and number that identify it, e.g. `KRS 0000000000, NIP 0000000000` |

Admin panel (DEV-15.13, ECO-067): the admin page of a GUI, at `/admin/`, is the shell `<nogat-admin>` alone. Link `nogat-admin.css`, load `nogat-admin.js` as a module and put the app's own sections inside the element; the page adds only `<meta name="robots" content="noindex">` and its own scripts.

```html
<link rel="stylesheet" href="../nogat/tokens.css">
<link rel="stylesheet" href="../nogat/nogat-admin.css">
<script type="module" src="../nogat/nogat-admin.js"></script>
<script type="module" src="admin.js"></script>
…
<nogat-admin app="Hydrograf" project="hydrograf" back="../" marks="../nogat/marks/">
  <section data-admin-section="resources" data-label="Zasoby">…</section>
</nogat-admin>
```

| Attribute or property of `<nogat-admin>` | Value |
| --- | --- |
| `app` | The GUI's name; the top bar shows it, a middle dot and „Administracja” |
| `project` | The registry name in lower case: the key is kept in `sessionStorage` under `<project>/admin-key/1`, the name takes the tool's accent, and the statistics file is named after it |
| `back` | The address of „Wróć do aplikacji”, default `../` |
| `api` | The address of the admin API with a final slash, resolved against the page; default `../api/admin/`, the API of DEV-15.13 seen from `/admin/` |
| `marks` | Optional: the directory of Nogat's marks, e.g. `../nogat/marks/`; with it the top bar shows `<project>.svg` |
| `auth` (attribute) or `element.auth` | `key`, the default: the key prompt and `X-Admin-Key`; `session`, for an app with accounts: no prompt, no „Wyloguj”, requests carry the page's cookies |

Without a key the shell shows the prompt („Zaloguj się”, „Klucz administratora”, „Zaloguj”). It checks a key with `GET feedback?limit=1` below `api` before keeping it and names a refusal by its reason: „Serwer nie ma ustawionego klucza administratora.” (`admin_key_not_configured`), „Podaj klucz administratora.” (`admin_key_missing`), „Nieprawidłowy klucz. Spróbuj ponownie.” (`admin_key_invalid`), else „Brak dostępu.”.
With a key it shows the navigation „Zgłoszenia”, „Statystyki”, „Stan”, then each child `<section data-admin-section="id" data-label="…">` in document order, and one section at a time: the one the URL hash names (`#feedback`, `#stats`, `#status` or the app's id), else the first. The three ids are the shell's.
„Wyloguj”, and in key mode every `401`, forget the key and return to the prompt; nothing of the panel stays on the page.

| Member of `<nogat-admin>` | Use |
| --- | --- |
| `adminFetch(path, init)` | `fetch` for the app's own sections: `path` is resolved against `api` (`adminFetch("resources")` asks `../api/admin/resources`), the key goes as `X-Admin-Key` (none with `auth="session"`), and `credentials: "same-origin"` and `cache: "no-store"` apply unless `init` sets them; it resolves to the `Response` as `fetch` does, and a `401` returns to the prompt (with `auth="session"` it fires `nogat-admin-unauthorized` instead) |
| `section` | The id of the section shown, `null` at the prompt; setting it moves the URL hash |
| `signOut()` | What „Wyloguj” does |

| Event (bubbles) | `detail` | Fired |
| --- | --- | --- |
| `nogat-admin-section` | `{id}` | when a section is shown: after the sign-in, on navigation and on a change of the hash; an app's section loads its data then |
| `nogat-admin-signout` | `{reason}` | when the key is forgotten: `signout` for „Wyloguj”, else the reason of the `401` |
| `nogat-admin-unauthorized` | `{status, reason}` | on a `401` the prompt does not answer: through the shell with `auth="session"`, or from a view on its own; the app's sign-in takes over |

The shell starts, and a view alone sends its first request, once the page's module scripts have run (`DOMContentLoaded`), so the app's script attaches its listeners and its `adminFetch` first.

The views work in the shell and alone in an app's own view, as Archiwista's „Zgłoszenia”: `<nogat-admin-feedback endpoint="/api/v1/admin/feedback" auth="session">`, its `adminFetch` adding the app's CSRF header.

| Element | Shows |
| --- | --- |
| `<nogat-admin-feedback>` | The reports, 50 per page and newest first („Poprzednia strona”, „Następna strona”), „Nieprzeczytane: {unread} z {total}”, „Tylko nieprzeczytane” (the reports of the page shown, since the core API has no filter), each report's number, time and text with „nowe” while unread, its context folded under „Kontekst”, „Oznacz jako przeczytane” or „Oznacz jako nieprzeczytane”, and „Usuń” after the question „Usunąć zgłoszenie #{id}?” („Usuń”, „Anuluj”): Tab stays in it, Esc, „Anuluj” and a click outside cancel, and focus returns to the report |
| `<nogat-admin-stats>` | „7 dni”, „30 dni”, „90 dni” or „Cały okres” as a table of „Data”, „Odwiedzający”, „Odsłony”, „Otwarte stacje”, „Obliczenia” and „Pobrania”, one row per day, ending with „Razem”, where the visitors are the „suma dziennych odwiedzających”; „Pobierz CSV” saves the days shown, built in the browser |
| `<nogat-admin-status>` | „Aplikacja”, „Wersja”, „Uruchomiona”, „Czas działania”, „Katalog danych”, „Wolne miejsce”, and „Kontrole”, each check with „OK”, „Ostrzeżenie” or „Błąd” |

| Attribute or property of a view | Value |
| --- | --- |
| `endpoint` | The route, resolved against the page; default `../api/admin/feedback`, `../api/admin/stats` or `../api/admin/status`; in the shell its `api` sets it |
| `auth` | `session`: the view's requests go through `fetch` with the page's cookies and never a key, in the shell too |
| `project` | `<nogat-admin-stats>` alone: names its CSV file, as the shell's `project` does; `nogat` without it |
| `element.adminFetch` | The function every request of the view goes through, `(url, init) => Promise<Response>`: by default the nearest `<nogat-admin>`'s `adminFetch`; alone or with `auth="session"`, `fetch` with `credentials: "same-origin"` and `cache: "no-store"`; an app whose requests need more assigns its own |
| `load()` | Asks the route again and redraws; the shell calls it when the view's section is shown |
| `clear()` | Drops what the view shows; the shell calls it when it returns to the prompt |

`<nogat-admin-stats>` asks `from` the day 6, 29 or 89 days before today (UTC) and `to` today, both days included; „Cały okres” asks `from=1970-01-01`. Its file is `<project>_stats_<first>_<last>.csv` (DEV-19.21), e.g. `hydrolog_stats_2026-08-01_2026-11-13.csv`: the keys of DEV-15.11 as the header, then one line per day, comma-separated, LF, without the totals.

Every GUI answers the core API of DEV-15.13, each answer JSON with `Cache-Control: no-store` and each refusal the error document of `unauthorized` with `details.reason`:

| Route | Answer |
|---|---|
| `GET /api/admin/feedback?limit=&offset=` | `{items, total, unread_count}`, newest first; `limit` 1 to 200, default 50 |
| `PATCH /api/admin/feedback/{id}` with `{"is_read": bool}` | the report |
| `DELETE /api/admin/feedback/{id}` | `{"status": "deleted"}`; an unknown id answers `404 not_found` |
| `GET /api/admin/stats?from=&to=` | `{days, totals}`: the lines of `stats.jsonl` (DEV-15.11) between the two UTC days, default the last 30, plus the current day as counted so far; `totals` sums every key but `visitors` |
| `GET /api/admin/status` | `{app, version, started_at, uptime_s, data_dir, disk: {free_bytes, total_bytes}, checks: [{name, status, detail}]}`, `status` one of `ok`, `warning`, `failed`; each GUI names its checks in its README |

A deployment protects exactly `/admin`, `/admin/*` and `/api/admin/*` (Cloudflare Access on the test deployment); the rest of the GUI stays public.
The key the prompt asks for lives in one place per deployment, `~/.config/nogat/keys/<project>-admin.key` (mode `0600`, or `0640` with a group a container's user belongs to); the app gets only its path in `<PREFIX>ADMIN_API_KEY_FILE`, never the value in `.env`, a unit file or compose (DEV-15.13).
The elements load nothing but their requests to the API and need no inline script or style, so they run under CSP `'self'`; every text of a report is a text node.
[specimen-admin.html](specimen-admin.html) runs the shell on a fake API inside the page, [specimen-admin.js](specimen-admin.js), which is not a kit file; the key is `nogat`.

## Adopting

1. Copy `tokens.css` into the app's static files and record the Nogat commit it came from in a comment at the top.
2. Link it before the app stylesheet.
3. Map the app's own variables to the tokens, e.g. Archiwista `--panel` -> `--surface`, `--line` -> `--line`, `--text-2` -> `--text-2`, `--accent` -> `--accent`, `--local` -> `--info`.
4. Replace hard-coded colours with tokens.
5. Add the dark theme (both the media query and `data-theme`).
6. Swap the favicon for the tool's mark.

Each app adopts in its own repository and session, following [the plan](../docs/plans/2026-11-01-visual-identity.md).
