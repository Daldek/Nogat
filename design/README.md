# Visual identity of the Nogat ecosystem

One look for every tool with a GUI: Archiwista and Hydrograf now, and any tool that gains one later.
The brand comes from debever.pl, the author's site: warm off-white and navy, a GitHub-dark night theme, the wave mark and Lato.
The working UI comes from Archiwista: a dense 13 px interface, status colours and 32 px controls.
Background and decisions: [the plan](../docs/plans/2026-11-01-visual-identity.md).

## Files

| File | Content |
| --- | --- |
| [tokens.css](tokens.css) | CSS custom properties, light and dark theme |
| [marks/](marks/) | One 32x32 SVG mark per project: [nogat](marks/nogat.svg), [archiwista](marks/archiwista.svg), [hydrograf](marks/hydrograf.svg), [kartograf](marks/kartograf.svg), [imgwtools](marks/imgwtools.svg), [hydrolog](marks/hydrolog.svg), [hydraulik](marks/hydraulik.svg), [retman](marks/retman.svg) |
| [specimen.html](specimen.html) | Preview of tokens, components and marks in both themes (open the file in a browser) |

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

## Marks

- Frame: 32x32 rounded square, `rx="6"`, filled with `--mark-frame` `#0d1117` in both themes.
- Line art: stroke 2.5, round caps and joins, in the tool's dark-theme accent.
- Nogat: the two waves of debever.pl's favicon.
- Every other tool: one family wave at the bottom plus its glyph:
  - Archiwista: archive drawer
  - Hydrograf: hydrographic network (reaches and cross sections, as in HEC-RAS's geometry editor)
  - Kartograf: folded map
  - IMGWTools: staff gauge
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
| IMGWTools | `--tool-imgwtools` | `#3b5bab` | `#8fa9f5` | [imgwtools.svg](marks/imgwtools.svg) |
| Hydrolog | `--tool-hydrolog` | `#3f7a3a` | `#7cc474` | [hydrolog.svg](marks/hydrolog.svg) |
| Hydraulik | `--tool-hydraulik` | `#5e4fa2` | `#b0a3f0` | [hydraulik.svg](marks/hydraulik.svg) |
| Retman | `--tool-retman` | `#a4472f` | `#f0907a` | [retman.svg](marks/retman.svg) |

The tool accent appears only in the mark, the tool name and an optional 2-3 px header rule.
The shared `--accent` stays the interactive colour everywhere.
A new project gets a mark and a `--tool-<name>` pair in both themes; the contract test requires one per project in `ecosystem.yaml`.

## Adopting

1. Copy `tokens.css` into the app's static files and record the Nogat commit it came from in a comment at the top.
2. Link it before the app stylesheet.
3. Map the app's own variables to the tokens, e.g. Archiwista `--panel` -> `--surface`, `--line` -> `--line`, `--text-2` -> `--text-2`, `--accent` -> `--accent`, `--local` -> `--info`.
4. Replace hard-coded colours with tokens.
5. Add the dark theme (both the media query and `data-theme`).
6. Swap the favicon for the tool's mark.

Each app adopts in its own repository and session, following [the plan](../docs/plans/2026-11-01-visual-identity.md).
