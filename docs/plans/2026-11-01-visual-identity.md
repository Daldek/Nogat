# Plan: one visual identity for the ecosystem's GUIs

Approved: 2026-11-01 (the author, after reviewing the specimen and the marks)

Requirements: HUB-5.2, DEV-17.4. Item 11 of Next in
[PROGRESS](../PROGRESS.md#next); the look of the
[shared GUI](2026-10-20-unified-gui.md), whose scope and storage question it
does not decide.

## Goal

Every tool that has or will have a GUI (Archiwista, Hydrograf and the web GUI
of IMGWTools today) looks like one family: the same colours, type, spacing,
controls, marks and layout, in a light and a dark theme, with room for each
tool's own accent and glyph.
The brand comes from the author's site debever.pl; the working interface
comes from Archiwista, the most complete GUI of the ecosystem.

## Where it starts

| Source | What it gives | What it lacks |
|---|---|---|
| debever.pl (`assets/css/style.css`, favicon) | warm off-white `#faf8f8`, navy `#284b63`, sage `#5f8a80`; GitHub-dark night theme (`#0d1117`, `#58a6ff`) with `prefers-color-scheme` and a stored switch; Lato from Google Fonts; a favicon of two waves on a dark rounded square | status colours, controls, density for data screens |
| Archiwista (`src/archiwista/web/styles.css`) | 13 px dense interface, status colours ok/warn/bad/local with background and ink, radii 5 to 12 px, three shadows, 32 px controls, focus ring, 16 px phone fields (iOS zoom) | its own indigo accent `#3730a3`, no dark theme, no mark |
| Hydrograf (`frontend/css/glass.css`) | Apple-style glass panels over the map, `#0A84FF` | shared tokens; nothing of the brand |

## Options

1. Keep each app's look and only share the marks. Cheap; the apps keep
   looking unrelated.
2. A shared CSS framework or component library (a build step, a package).
   Archiwista is build-free under CSP `'self'` (A-ADR-028) and Hydrograf
   serves plain files; a build step in both is a cost neither needs.
3. Shared design tokens as one plain CSS file, marks as SVG files and written
   guidelines with component patterns; each app maps its own variables to the
   tokens. No build, works offline, adoptable one screen at a time.

## Decision

Option 3, in Nogat's `design/`:

- `design/tokens.css`: colour, type, space, radius, control, elevation and
  motion tokens; light by default, dark by `prefers-color-scheme` or
  `data-theme="dark"`, light forced by `data-theme="light"`.
- Brand colours from debever.pl, status colours and metrics from Archiwista;
  the shared interactive accent is the brand navy (dark: `#58a6ff`), which
  replaces Archiwista's indigo.
- Type: Lato first (the site's face) where installed or vendored, then the
  system UI stack; no remote fonts (apps run offline under CSP `'self'`).
- Marks: a 32 px rounded square in `#0d1117` (the site's favicon frame) with
  line art in the tool's accent; Nogat's mark is the favicon's two waves,
  every other tool has one family wave and its own glyph.
- One accent pair per project (`--tool-<name>`), for the mark, the tool name
  and a header rule only; never for status.
- The author chose the glyphs on 2026-11-01: Hydrolog the hydrograph,
  Hydrograf a river network with cross sections (HEC-RAS's geometry editor),
  IMGWTools a staff gauge.
- Layout: Archiwista's shell (top bar, navigation rail, content with a
  resizable side panel) for every GUI, Hydrograf's map included; floating
  glass cards go.
- The standard binds it: DEV-15.3 (profile `app`), ECO-055; the adoption rows
  are in `standards/ADOPTION_PLAN.md`.
- `design/README.md` holds the guidelines; `design/specimen.html` previews
  them; `tests/contract/test_design.py` checks WCAG 2.2 AA contrast of the
  promised pairs in both themes and one mark and accent per project of
  `ecosystem.yaml`; `design/mockups/` shows a GUI redrawn before its
  project adopts it.

## Steps

1. Nogat: tokens, marks, guidelines, specimen and contract tests
   (`feature/visual-identity`). Done 2026-11-01, see Results.
2. The author reviews the identity (the specimen in both themes) and
   approves this plan. Done 2026-11-01, with three marks redrawn.
3. DEV-15.3 and ECO-055 in the standard; the adoption rows. Done 2026-11-01.
4. A mockup of Hydrograf in the identity and Archiwista's shell
   (`design/mockups/hydrograf/`), for the author's review before Hydrograf's
   own plan.
5. Archiwista adopts it in its own session and plan: copy `tokens.css` with
   the Nogat commit, map `--panel`, `--line`, `--text-*`, `--accent*` and
   `--local` to the tokens, add the dark theme, replace the favicon; its
   e2e tests cover the screens.
6. Hydrograf adopts it from the approved mockup: the shell around the map,
   the tokens instead of `glass.css`, the dark theme, its mark.
7. IMGWTools moves its web GUI templates to the tokens and the shell.
8. Any later GUI starts from the tokens; a new project in `ecosystem.yaml`
   needs its mark and accent pair (the contract test fails without them).

## Risks

- Lato is not installed on most Linux machines; until an app vendors it the
  system face is shown. Accepted: the layout does not depend on the face.
- Copies of `tokens.css` drift from Nogat; each copy names its Nogat commit,
  and a later `drift` check could compare them.
- The marks are drawn by hand and not tested by eye at 16 px on every
  platform; the specimen shows them at 16, 32 and 64 px for the review.

## Results

Step 1 (2026-11-01): `design/tokens.css`, `design/marks/` (eight marks),
`design/README.md`, `design/specimen.html`, `tests/contract/test_design.py`.

Steps 2 and 3 (2026-11-01): the author approved the identity after
redrawing the marks of Hydrolog, Hydrograf and IMGWTools; DEV-15.3, ECO-055,
the adoption rows, the `--rail-*` tokens and the layout section of
`design/README.md`.

Step 4 (2026-11-01): `design/mockups/hydrograf/` (`index.html`,
`mockup.css`, `mockup.js`, `theme-init.js`): Hydrograf's selected-watershed
screen in Archiwista's shell, with the layers panel on the left, the map
with modes, legend and the terrain-profile drawer in the centre, the
watershed parameters, hietogram and hydrograph on the right, the feedback
dialog, both themes and the phone layout. Static data; no remote resources.

Step 6 (2026-11-01, in review): Hydrograf `feature/visual-identity`
(`3ea0bc6` to `0e5b8d1`; its ADR-065) ports the approved mockup into the real
frontend (Leaflet, Chart.js): the shell (rail with Mapa and Administracja
only), layers with one zoom-to-extent button, Archiwista's basemaps plus the
ESRI orthophoto (OpenFreeMap through MapLibre), charts and overlays on the
tokens, (i) explanations with the applicability of each method, an advanced
hydrograph mode, admin and a new nine-slide guide in the same shell. It runs
as a parallel nginx container on port 8081 with production's
API and database; production on port 8080 is unchanged until the author
approves the deployment.
