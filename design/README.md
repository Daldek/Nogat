# Visual identity of the Nogat ecosystem

One look for every tool with a GUI: Archiwista and Hydrograf now, and any tool that gains one later.
The brand comes from debever.pl, the author's site: warm off-white and navy, a GitHub-dark night theme, the wave mark and Lato.
The working UI comes from Archiwista: a dense 13 px interface, status colours and 32 px controls.
Background and decisions: [the plan](../docs/plans/2026-11-01-visual-identity.md).

## Files

| File | Content |
| --- | --- |
| [tokens.css](tokens.css) | CSS custom properties, light and dark theme |
| [marks/](marks/) | One 32x32 SVG mark per project: [nogat](marks/nogat.svg), [archiwista](marks/archiwista.svg), [hydrograf](marks/hydrograf.svg), [kartograf](marks/kartograf.svg), [obserwator](marks/obserwator.svg), [hydrolog](marks/hydrolog.svg), [hydraulik](marks/hydraulik.svg), [retman](marks/retman.svg) |
| [specimen.html](specimen.html) | Preview of tokens, components and marks in both themes; serve `design/` over HTTP (`python -m http.server`) to see the kit's app menu, since modules do not load from `file://` |
| [kit/](kit/) | The GUI kit every GUI copies (DEV-15.4 to DEV-15.7): the app menu `nogat-app-menu.js` and `.css`, the hand-off `nogat-handoff.js`, the terms `nogat-terms.md`, `.html` and `.css`, the manifest `nogat-kit.json` |
| [mockups/hydrograf/](mockups/hydrograf/index.html) | Hydrograf redrawn in the identity and Archiwista's shell (mockup) |
| [mockups/hydrolog/](mockups/hydrolog/index.html) | Hydrolog's GUI: five sections; the hydrograph workbench in full, its results following every change; the river network drawn vertically, each node's settings on click; alone and inside Nogat's shell (mockup) |

## Principles

- Content first: maps, tables and data carry the screen; chrome stays quiet.
- Calm surfaces. Colour carries meaning (status), not decoration.
- One accent per screen.
- Dense but readable: 13 px base in apps, 16 px on sites and in phone form fields.
- Both themes, always.
- No remote resources: apps run offline under CSP `'self'`. No web fonts from CDNs; fonts may be vendored.

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

Patterns from Archiwista; use tokens only.

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

## Layout

The app shell comes from Archiwista; use it for every tool with a map or a workspace.

- Shell: a grid of two columns (64 px rail, content) and two rows (`--header-height`, content).
- Top bar spans both columns: `--surface`, bottom border `--line`. Left to right: mark at 24 px and the tool name in `--tool-<name>`, then the context (project, area, selection), then actions on the right.
- Navigation rail: dark column of `.rail-item`s, 54 px wide, icon over a short label, `--radius-md`. Background `--rail-bg`, items `--rail-ink`, hover `--rail-hover`, active `--rail-active` with `--rail-ink-active`.
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
.view-layout { --left-w: 300px; --right-w: 400px; display: grid; grid-template-columns: var(--left-w) minmax(480px, 1fr) var(--right-w); min-height: 0; }
.resizer { width: 10px; cursor: col-resize; }
```

Phone (width <= 860 px):

- Top bar 48 px.
- The rail becomes a 58 px bottom bar: `--surface` background, `--line` top border, items in `--text-2`, active item in `--accent`.
- Panels become bottom sheets: fixed above the bar (bottom 58 px), height `min(74vh, 640px)`, radius 16 px on the top corners, with a grip, a title and a close button. Resizers are hidden.
- Form fields use 16 px text so iOS does not zoom.

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
`nogat-kit.json` holds the kit version and the SHA-256 of each file; `tests/contract/test_kit.py` fails when they disagree.

App menu (DEV-15.4): link `nogat-app-menu.css`, load `nogat-app-menu.js` as a module, and put the element in the top bar left of the theme switch.

```html
<nogat-app-menu current="hydrolog" marks="nogat/marks/" terms="regulamin.html"></nogat-app-menu>
```

The app sets `element.apps` (or the `apps` attribute, as JSON) to the deployment's `[nogat.gui]` table of `nogat.toml`, e.g. `{"hydrograf": "https://hydrograf.example/", "archiwista": "/archiwista/"}`.
Addresses resolve against the page; only http and https stay. With no GUI but the current one the element is not drawn. An entry opens its GUI in the tab `nogat-<name>`: Chromium reuses that tab unless one of the two pages sends `Cross-Origin-Opener-Policy`, which costs one more tab.
The menu styles itself with the tokens and falls back to light values, so a GUI without `tokens.css` shows it too.
The `terms` attribute, the address of the GUI's filled terms (DEV-15.7), ends the list with the link „Regulamin”; the menu is not the only link, since it is not drawn without another GUI.

Hand-off (DEV-15.5): `import * as handoff from "./nogat/nogat-handoff.js"`.

| Export | Use |
| --- | --- |
| `TEXTS.copyTo(name)`, `TEXTS.file`, `TEXTS.loadFrom(name)`, `TEXTS.openFile`, `TEXTS.paste`, `TEXTS.open(name)` | The labels: „Kopiuj do Hydrologa”, „Plik przekazania”, „Wczytaj z Hydrografa”, „Plik przekazania…”, „Wklej ze schowka”, „Otwórz Archiwistę” |
| `copyHandoff(doc, field)` | Clipboard in a secure context; otherwise the text goes selected into `field` and the result is `"field"` (show `TEXTS.copyByHand`) |
| `downloadHandoff(doc)` | Saves `<subject>.handoff.json`, 2-space JSON with a final newline; returns the name |
| `readFile(file)`, `readClipboard()` | The text of a picked file; the clipboard's, or `null` when refused (offer a field, `TEXTS.pasteByHand`) |
| `readHandoff(text, envelope)` | Parses and checks the envelope against the GUI's copy of `handoff-1.schema.json`: `{doc, problems}` with Polish messages |
| `validate(value, schema)` | The same check for a payload against its owner's schema (draft 2020-12, local `$ref`s) |

Terms (DEV-15.7, ECO-061 to ECO-063): [nogat-terms.md](kit/nogat-terms.md) is the regulamin in Polish, the source; `nogat-terms.html` is generated from it by `uv run scripts/ecosystem.py standard --write` and is never edited. A GUI copies both with `nogat-terms.css` into its kit directory, fills the HTML for its deployment and serves the result at `regulamin.html` beside its start page; no script, no remote resource, one stylesheet of the kit plus `tokens.css`.
The regulamin carries its own version („Wersja 1.0”, one for every GUI) and ends with „Historia zmian”, linked to the history of `nogat-terms.md` on Nogat's `main`. A change of its text once published raises that version, adds its entry to the history and releases a new kit version; the operator then sets a new `terms_effective`, the day the GUIs publish it, since a new version takes effect on publication. Until its first publication, version 1.0 is revised in place, each revision in a new kit version.
Its § 3 opens with the statement every view shows in its footer (DEV-15.8); the template's fixed text describes the rate limit, the logs, the statistics and „Zgłoś uwagę” of DEV-15.9 to DEV-15.12, so a GUI serves the page only once it follows them.

Filling, in this order (reference: `fill` in [scripts/terms.py](../scripts/terms.py)):

1. Blocks. A block is the lines between `<!-- block: <name> -->` and `<!-- /block -->`, each marker on a line of its own. Keep the lines of every block the project lists below, without the two marker lines; drop every other block with its markers. The block `imgw-terms` follows the others and is never listed: it stays with any of `imgw`, `imgw-hydro` and `pmaxtp`.
2. Fields. Replace every `{{name}}` with its value, HTML-escaped (`&`, `<`, `>`, `"`, `'`). Every field needs a value, non-empty except `processor_transfer`, `processor_cookie` and `mail_transfer`, each a whole sentence or empty: with a field missing, or with a `{{` left, the GUI serves no page and no link.

The GUI fills at start or at build with its own code; a page filled from an older kit version is filled again when the kit is copied.

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
| `chmi` | ČHMÚ open data | Obserwator; Hydrolog with station series |
| `gugik` | GUGiK data | Hydrograf |
| `cuzk` | ČÚZK data | none yet |
| `copernicus` | Copernicus data | Hydrograf |
| `isric` | ISRIC SoilGrids | Hydrograf |
| `wody-polskie` | flood hazard maps of Wody Polskie | Hydrograf |
| `osm` | OpenStreetMap basemaps (OpenFreeMap, the OSM basemap of geoportal) | Hydrograf; Obserwator with a map |
| `esri` | the Esri World Imagery basemap | Hydrograf |

## Adopting

1. Copy `tokens.css` into the app's static files and record the Nogat commit it came from in a comment at the top.
2. Link it before the app stylesheet.
3. Map the app's own variables to the tokens, e.g. Archiwista `--panel` -> `--surface`, `--line` -> `--line`, `--text-2` -> `--text-2`, `--accent` -> `--accent`, `--local` -> `--info`.
4. Replace hard-coded colours with tokens.
5. Add the dark theme (both the media query and `data-theme`).
6. Swap the favicon for the tool's mark.

Each app adopts in its own repository and session, following [the plan](../docs/plans/2026-11-01-visual-identity.md).
