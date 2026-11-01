# Plan: Nogat as the GUI platform of the ecosystem

Approved: pending

Requirements: HUB-5.2, DEV-17.4, DEV-15.1, DEV-15.3, AGI-2.1, AGI-2.3,
AGI-6.1, HUB-1.1, HUB-1.2, HUB §7, ECO-054, ECO-055. Continues the
[visual identity](2026-11-01-visual-identity.md) (its steps 5 to 7), gives the
[shared GUI](2026-10-20-unified-gui.md) the scope it lacked without deciding
its storage question, and keeps projects in Archiwista
([projects plan](2026-10-31-archiwista-projects.md)). A draft of 2026-11-01:
research and a proposal for the author; no code.

## Goal

The author's request of 2026-11-01, in short:

1. The GUIs already look alike; their common parts are kept by Nogat and each
   project only extends them.
2. Hydrolog and IMGWTools get GUIs.
3. Kartograf is reached through Archiwista, which already takes a pasted
   producer command; a graphical editor of such commands gives the full power
   of the producers to people who do not write command lines.
4. Nogat is the main product: its own GUI into which every project plugs and
   which carries data between them. Example: the user changes the hydrograph
   inputs in Hydrograf's advanced mode, switches to Hydrolog and finds its
   fields filled with the same values.
5. Hydrolog shows the river network as a simple topological network, for when
   sub-catchments are joined.

## Where it starts

Checked on 2026-11-01 in the workspace checkouts and on the running services
(`curl` of the headers only). A path outside Nogat is relative to the
repository named in its row or sentence.

### The GUIs

| GUI | Stack, size, build | Libraries | CSP and framing | Auth and serving | Shared with Nogat today |
|---|---|---|---|---|---|
| Archiwista (`feature/archiwista-projects`) | Preact 10.29.8 + htm 3.1.1 as ES modules, no build (A-ADR-028, `docs/DECISIONS.md:1451`); about 34,000 lines in `src/archiwista/web/` | vendored with SHA-256 per file (`src/archiwista/web/vendor/vendor.json`); MapLibre GL 6.14.0; charts drawn as SVG (`web/src/views/station-chart.js`) | `script-src 'self'`, `frame-ancestors 'none'` (`src/archiwista/security.py:1484-1519`; seen on 127.0.0.1:8090) | local: one-time token in the URL fragment; team: TLS, accounts, roles (SPEC 10.1, 10.2; A-ADR-046); :8090 answers `403 tls_required`; FastAPI | nothing: own indigo `styles.css`, no dark theme, no `tokens.css` in any of its three worktrees (visual identity step 5 not started) |
| Hydrograf (`Hydrograf-gui`, `feature/visual-identity`, port 8081) | plain IIFE scripts on `window.Hydrograf` (`frontend/js/shell.js:10-13`), no build; about 9,200 lines of JS, CSS and HTML | Leaflet 1.9.4, MapLibre GL 4.7.1, Chart.js 4.4.7, VectorGrid 1.3.0 from unpkg and jsDelivr with SRI (`frontend/index.html:17-24,476-496`) | allows unpkg and jsDelivr scripts; `frame-ancestors 'none'`, `X-Frame-Options: DENY` (`docker/nginx.conf:50`; seen on :8080 and :8081) | none, except `X-Admin-Key` for admin routes (`backend/api/dependencies/admin_auth.py`); nginx in Docker before FastAPI and PostGIS | `tokens.css` copied at Nogat `29e7e1c` (`frontend/css/tokens.css:1-2`); shell and theme switch ported from Nogat's mockup (`shell.js`, `theme-*.js`); its own (i) tooltips with MathML (`info.js`, 76 texts in `info-texts.js`) |
| IMGWTools web (`feature/archiwista-projects`) | FastAPI + Jinja2 + HTMX; about 1,900 lines in `src/imgwtools/web/`: archives, PMAXTP, stations, map | HTMX 1.9.10 and Pico 2 from unpkg and jsDelivr (`src/imgwtools/web/templates/base.html:9,12`) | no CSP header (seen on 127.0.0.1:8000); CORS `*` (`src/imgwtools/api/main.py:149`) | reads open, writes need `X-API-Key` (`src/imgwtools/api/routes/commands.py:22,97`); `imgw server` beside `/api/v1` and `/mcp` | nothing |
| Hydrolog, Kartograf, Hydraulik, Retman | no GUI: library and CLI, Kartograf and Hydrolog also MCP; Hydrolog's README plans none | – | – | – | – |

Shared already, but written three times:

- The shell and the theme switch exist as Nogat's mockup
  ([mockup.js](../../design/mockups/hydrograf/mockup.js), 338 lines), as
  Hydrograf's port (`frontend/js/shell.js`, 292 lines, `theme-init.js`,
  `theme-switch.js`) and as Archiwista's Preact shell
  (`src/archiwista/web/src/shell.js`, 633).
- They drift: [design/README.md](../../design/README.md#theme) stores the
  theme under `theme`; the specimen, the mockup and Hydrograf use
  `nogat-theme` (`design/specimen.html:10`, `frontend/js/theme-init.js:11`).
- One copy carries a stamp (Hydrograf's `tokens.css`). `drift` compares only
  dependency pins with tags (`report_drift` in
  [ecosystem.py](../../scripts/ecosystem.py)), so copies are unchecked, the
  risk the visual-identity plan named. Archiwista's `vendor.json` (source and
  SHA-256 of every file) is a ready model of a stamped copy.
- Maps differ (MapLibre 6 in Archiwista; Leaflet with MapLibre basemaps in
  Hydrograf), and so do charts (SVG by hand; Chart.js).

### Command catalogs, the input of a command editor

| | Kartograf | IMGWTools | Hydrolog (`Hydrolog-routing`) |
|---|---|---|---|
| Shape | Nogat [commands-1](../../schemas/agent/commands-1.schema.json), contract-tested | own JSON Schema per command in `imgw-commands/1` (`src/imgwtools/commands.py:3229-3303`); no commands-1 test | commands-1 (`tests/contract/test_catalog.py:234`) |
| Commands, counted with `list_commands()` in each checkout | 39 | 30 | 44 |
| Polish texts of options | none (Archiwista `src/archiwista/adapter/kartograf/actions.py:148-150`) | by `lang` | `i18n.pl` per option, beyond commands-1 (`src/hydrolog/catalog/document.py:199-202`) |
| Rules between options | declared (`src/kartograf/catalog/spec.py:49`: `requires`, `excludes`, `applies_to`, `required_when`, `any_of`), exported only as `one_of` (`catalog/build.py:109-127`) | `dependentRequired`, `oneOf` (`src/imgwtools/commands.py:3184-3188`) | `one_of`; others not checked |
| Sections of a form | declared (`catalog/spec.py:171,212`), not exported | command groups only | not checked |
| `parse_command`, `format_command` | `src/kartograf/commands.py:153`, `:323` | `src/imgwtools/commands.py:1979`, `:1854` | none public (`src/hydrolog/cli/parser.py:683` is internal) |

Hydraulik validates against commands-1 too
(`Hydraulik-sfincs/tests/contract/test_command_catalog.py:20`).
Archiwista already holds the rest of an editor: `GET /commands` and
`POST /commands/parse|validate|format` (SPEC lines 3423-3426) over the
producer-neutral `CommandInfo` and `CommandOption` (type, choices with
meanings, default, bounds, item type, exclusive group, `path_role`;
`src/archiwista/sources/types.py:488-583`), and it refuses path options in a
request (A-ADR-034, point 5). Its UI has only the field „Wklej polecenie
producenta” (`src/archiwista/web/src/map/source.js:199-240`) feeding the plan
window (`web/src/views/plan.js`). SPEC KB-1 asked for "download forms
without a copy of Kartograf's rules" (SPEC line 4333); in use, BDOT10k and
orthophoto are downloaded only by pasting a Kartograf command
([PROGRESS](../PROGRESS.md#next), item 6).

### Data between the apps

- Hydrograf (`Hydrograf-gui`) computes hydrographs with Hydrolog 0.6.3 as a
  library (`backend/requirements.txt:59`). Its advanced mode edits 11 morphometry
  fields (`frontend/js/advanced.js:20-30`) and a rain series
  (`custom-rain.js:558-566`); the request (`backend/models/schemas.py:358-510`)
  adds PMAXTP probability and duration, AMC, the hietogram and its shape, the
  unit hydrograph with its parameters and the tc method; the response gives
  the tc and Nash parameters used (`schemas.py:561-575`) and the CN used
  (`:552`).
- Hydrolog's `hydrolog-network/1`
  (`src/hydrolog/schemas/hydrolog-network-1.schema.json`, routing branch)
  already holds the same content per subcatchment: `watershed` (the fields of
  `WatershedParameters`), `runoff` (`curve-number`: `tc_min` or `tc_method`,
  `ia_coefficient`, `amc`, `uh_model` and its parameters) and `rainfall` (a
  design storm with its hietogram, or a series). It refuses unknown fields
  (`additionalProperties: false`, `src/hydrolog/routing/document.py:187`).
  The registry lists it among Hydrolog's `provides`; no edge exchanges it.
- Names differ at the edge: Hydrograf's `length_to_centroid_km` is Hydrolog's
  `Lc_km` (mapped in `backend/api/endpoints/hydrograph.py:333-343`);
  Hydrograf's `nash_estimation` (Lutz and others) has no option in
  `hydrograph generate`, which takes `nash_n` and `nash_k_min`; PMAXTP
  probability and duration exist only in Hydrograf, Hydrolog takes `total_mm`.
- No GUI hands data to another; the only hand-off is Archiwista's `pliki.txt`
  export for Hydrograf (projects plan, P6).

### The network discussed on 2026-10-25

The discussion is in the coordinating session of 2026-10-24 to 2026-10-28
(transcript `~/.omp/agent/sessions/-tmp/2026-10-24T13-52-09-509Z_01a16e2e-e525-73dd-87db-ba388db8e443.jsonl`,
the author's messages of 2026-10-25 at 09:03, 09:11, 09:18 and 09:54 UTC).
The author asked that:

- every subcatchment, reach, junction and outlet be an object, joined without
  CSV files, JSON being the definition of the network, chosen in Hydrograf's
  GUI;
- a picked sub-catchment be joined with everything above it into one
  homogeneous unit; each further pick be another (large) sub-catchment; all
  end in one outlet; a lower pick never absorb the area of a pick above it;
  rainfall may differ between sub-catchments and the code take more
  combinations later;
- the network be shown "with the values used in the calculation as a
  topological schematic (e.g. a Beck map)";
- the outlet be picked first and sub-catchments only inside it.

Hydrolog recorded this in ADR-0012 (typed nodes, control points;
`docs/decisions/0012-network-objects-rainfall-and-runoff.md:11-17`) and
ADR-0013 (the metro-style document `hydrolog-network-schematic/1`, laid out by
the library, drawn by `schematic_svg` or by any consumer; "Hydrograf will show
the picture next to its map": `0013-network-schematic.md:12,50-51,69-71`),
with the mapping for Hydrograf in `docs/INTEGRATION.md:350-368`, all on the
unmerged `feature/routing-schematic`. The exporter in Hydrograf is an
unopened request (`INTEGRATION.md:348`); Hydrograf has no channel routing
("instant aggregation", quoted in
`docs/plans/2026-10-24-long-term-and-routing.md:64` of Hydrolog).

### Constraints

- ECO-055 rejected "a shared CSS framework or component package" for its build
  step and the dependency between apps; DEV-15.1 asks for ES modules without a
  build; the apps run offline under CSP `'self'`.
- HUB-1.1 gives Nogat no GUI; HUB-1.2 keeps other projects' code out of Nogat.
  The `nogat` package is planned only ([PROGRESS](../PROGRESS.md#status);
  `pyproject.toml`: `package = false`).
- `nogat` will install Kartograf, IMGWTools, Hydrolog and Retman
  ([first release set](2026-10-20-first-release-set.md)). Hydrograf is an app
  without a package; Archiwista follows alone; the two cannot share one
  environment (`affine`, [PROGRESS](../PROGRESS.md#open-questions)).
- All three running GUIs refuse to be framed (headers above).

## Options

**A. How the shared parts travel.**

| Option | Verdict |
|---|---|
| A1. Copies of plain files (CSS, ES modules, custom elements without shadow DOM) with a kit version and SHA-256 per file, checked by Nogat | Recommended: no build, CSP `'self'`, offline; works in Preact, IIFE and Jinja pages alike; the cost is updating copies |
| A2. An npm package or bundled component library | Rejected, as in ECO-055: a build step and Node in build-free apps |
| A3. Files served at run time by a Nogat server | Rejected: breaks CSP `'self'` and offline use; Hydrograf on a server would load code from a user's machine |
| A4. Package data of `nogat`, mounted by each app | Rejected: every app would depend on `nogat`, which HUB-7.2 installs in its own environment |

**B. The Nogat GUI host.**

| Option | Verdict |
|---|---|
| B1. A portal: one page of links and status | Cheap, but no Hydrolog or IMGWTools GUI and no sync beyond files |
| B2. One SPA with every GUI as a module | Rejected for the existing apps: three stacks; Hydrograf needs PostGIS and Docker; Archiwista has its own server, auth and jobs; the `affine` conflict |
| B3. Iframes (micro-frontends) | Rejected for now: all three refuse framing; two shells on one screen; sessions and clickjacking to re-check |
| B4. A Nogat server proxying every API and rendering every UI | Rejected: rewrites Hydrograf's and Archiwista's frontends and stands in front of Archiwista's security model |
| B5. `nogat gui` hosts the modules of tools that `nogat` installs (in process, through their catalogs) and links to the deployed apps; a hand-off document travels between all | Recommended |

**C. Data sync.**

| Option | Verdict |
|---|---|
| C1. A new flat `hydrograph-inputs/1` | Rejected: a second schema of what `hydrolog-network/1` already holds |
| C2. `hydrolog-network/1` as the payload (one watershed is one subcatchment and the outlet; joined sub-catchments are more nodes) in a small Nogat envelope `nogat-handoff/1` with provenance | Recommended |
| C3. Shared state in a host database | Rejected for now: Hydrograf runs on a server, the host on the user's machine |

**D. IMGWTools.** D1: restyle the Jinja pages (visual identity step 7),
keeping a third stack and CDN libraries. D2: rebuild them as a hosted module
from the catalog, remove the Jinja and HTMX pages, keep `imgw server` (REST,
MCP). Recommended: D2 (3.0.0 is untagged, ECO-020).

**E. The command editor.** E1: in Archiwista only (Kartograf only). E2: a kit
component used by Archiwista and the host. Recommended: E2.

## Decision

**Proposal**, recommended by this research; nothing is decided until the
author approves it.

1. **Nogat becomes `hub` and `app`.** A new ECO decision amends HUB-1.1
   (Nogat holds the GUI kit and the host), HUB-7.3 (`nogat gui`), ECO-055 and
   DEV-15.3 (a copy of the kit, not of the tokens only). HUB-1.2 stays: a
   tool's GUI module ships in the tool's package.
2. **The kit** (`design/kit/`, option A1), Nogat's own code grown from its
   mockup and specimen, with Hydrograf's port as the reference:

   | File | Content |
   |---|---|
   | `tokens.css` | today's tokens, moved |
   | `base.css` | buttons, inputs, panels, badges, chips, tables, dialog, toast: the components of the guidelines |
   | `shell.css`, `shell.js` | top bar, rail, view layout, resizers with keys, phone sheets, a layout event for maps; an API to register rail items and panels |
   | `theme.js` | pre-paint init and the three-way switch, one storage key |
   | `info.js` | `<nogat-info>`: tooltip with MathML from a small notation; the texts are the app's |
   | `form.js` | number with unit and bounds, choice with meanings, series table with paste and CSV |
   | `command-form.js` | `<nogat-command-form>` (item 7) |
   | `schematic.js` | `<nogat-schematic>`: draws `hydrolog-network-schematic/1` in the tokens (ADR-0013 lets a consumer draw it) |
   | `chart-theme.js` | tokens as Chart.js defaults and as classes for SVG charts |
   | `handoff.js` | read, validate and write `nogat-handoff/1` (file, clipboard, URL fragment) |
   | `basemaps.json` | shared basemaps, their attribution and the origins a CSP must allow |
   | `kit.json` | kit version (SemVer) and SHA-256 of every file |

   Projects extend it with their own CSS after the kit (tokens only), their
   rail items, panels and texts (DEV-15.2), and never edit a kit file. An IIFE
   app loads `<script type="module">` before its deferred scripts; custom
   elements work alike in htm, plain HTML and Jinja. `drift` (HUB-4.1) gains
   the kit copies of every project with a GUI: current, behind or modified
   against its `kit.json`; each app's contract test checks its copy.
3. **Plugging in.** The registry gains an optional `gui` field per project:
   `kind` (`hosted` or `linked`), the kit directory in the repository, and the
   payloads it `accepts` and `emits`; structure only, the addresses of
   deployed apps come from `nogat.toml` (DEV-18.1, HUB-2.4). A hosted module is
   package data `src/<package>/gui/` with a `manifest.json`, found through the
   entry point group `nogat.gui`.
4. **The host**, `nogat gui` in the `nogat` package: FastAPI on 127.0.0.1, a
   one-time token in the fragment (Archiwista's local mode), CSP `'self'`, no
   CORS. Rail: „Pulpit” (apps with status, recent hand-offs), the modules,
   „Polecenia” (the editor over the catalogs of installed tools), „Wymiana”
   (hand-off inbox). A catalog bridge `/api/<tool>/<group>/<verb>` in the shape
   of AGI-6.1 calls `validate_command`, `check_command` and `run_command` and
   answers with the envelope or AGI-6.3 errors; path options only inside a host
   work directory. The host does not write producers' stores: a Kartograf or
   IMGWTools store line goes to Archiwista (store writes, locks and pins stay
   there, ECO-054). One user, local; no team mode in this plan.
5. **The hand-off.** `schemas/exchange/handoff-1.schema.json` in Nogat, copied
   like the agent schemas (ECO-050): `schema` `nogat-handoff/1`, `created_at`,
   `producer` (tool, version, page to return to), `subject` (label, outlet,
   CRS), `provenance` (e.g. PMAXTP probability and duration), `payload` (typed
   documents: `hydrolog-network/1` first) and an optional `result` of the
   producer for comparison. Hydrograf to Hydrolog: one subcatchment node with
   the values used; back: the same document, a design storm as the series
   Hydrolog computes (`precip hietogram`), which Hydrograf's custom rain
   takes. File and clipboard always; a link with the document in the fragment
   when it is small. The host keeps hand-offs in `<data_dir>/nogat/handoffs/`
   (DEV-18.2); Archiwista projects may hold them later (question 6).
6. **Hydrolog's GUI**, a hosted module in Hydrolog: first the hydrograph of one
   watershed with the inputs of Hydrograf's advanced mode (watershed fields,
   CN, AMC, `ia_coefficient`, tc method or tc, design storm or series, unit
   hydrograph and its parameters), charts of rain, effective rain and
   discharge, the balance and notices, CSV and hand-off; then the network with
   reach methods, rainfall per subcatchment, per-node results and the
   schematic; later `stats flood-frequency` on IMGWTools series. Hydrolog gets
   no REST layer: the host calls it in process. Joining sub-catchments stays
   the control-point flow of ADR-0012, picked in Hydrograf.
7. **The command editor**, `<nogat-command-form>`, reads commands-1 entries:
   a field per option by type, a choice for a `one_of` group, rules that
   enable or disable fields, path options hidden where the app owns paths, the
   canonical line live through `format_command`, a pasted line read through
   `parse_command`, errors placed by `details.option` from `validate_command`.
   Archiwista puts it as „Kreator polecenia” beside the paste field, producing
   the same call for the existing plan window; the host shows every installed
   catalog. AGI-2.3 and commands-1 gain optional option fields: `i18n.pl`
   (description, value meanings, as Hydrolog does), `requires`, `excludes`,
   `applies_to`, `section` with order, and `format` (box, sheet, date, area
   file).
8. **IMGWTools**: option D2; the module covers stations, series read from a
   local store, PMAXTP (a depth handed to Hydrolog's rainfall) and current
   data; store sync stays in Archiwista.

The first usable version is steps 1, 2, 3, 8 (without „Polecenia”, which
needs steps 4 to 7), 9 and 10: the kit, `nogat gui` with „Pulpit”, Hydrolog's
hydrograph and the inbox, and Hydrograf's export; that is the author's example
end to end.

## Steps

Producers before consumers (HUB-5.2): Nogat's contracts and kit, then the
producers' catalogs, then the host, then the GUIs. Each step runs in its
repository's own session on a topic branch (DEV-3.4), with its gate, ADR,
CHANGELOG and PROGRESS. Sizes are estimates in sessions.

| # | Owner | Step | Size | Verified by |
|---|---|---|---|---|
| 1 | Nogat | The ECO decision; HUB-1.1, HUB-7.3, DEV-15.3, AGI-2.3 and the optional option fields of commands-1; `handoff-1` schema; the registry schema's `gui` field and planned entries; Nogat's profiles `[hub, app]` | 1 | gate: `validate`, `standard`, schema tests |
| 2 | Nogat | Kit 0.1, chrome: `tokens.css`, `base.css`, `shell.*`, `theme.js`, `kit.json`; the specimen rebuilt on it; browser tests (theme before paint, resizer keys, phone sheets) | 1.5 | specimen in both themes; tests |
| 3 | Nogat | Kit 0.1, parts: `info.js`, `form.js`, `chart-theme.js`, `handoff.js`, `basemaps.json`; the copy check in `drift` | 1.5 | `drift` reports Hydrograf's `tokens.css` copy |
| 4 | Kartograf | Export option `i18n.pl`, its constraints, `section` and `format` in `kartograf-commands/1` | 1-2 | commands-1 contract test; Archiwista's adapter tests unchanged |
| 5 | IMGWTools | `imgw commands list` and `imgw commands schema` with `--json` in commands-1 shape, with option texts and dependencies; the JSON Schema stays the REST and MCP input schema | 1.5-2 | commands-1 contract test |
| 6 | Hydrolog | Merge the routing branches (its PROGRESS, Next 8 and 10); public `parse_command` and `format_command`; the schematic document without an output file | 1-2 | gate; every catalog example read back into the same call |
| 7 | Nogat | Kit 0.2: `<nogat-command-form>` and `<nogat-schematic>` | 1.5-2 | tests on the three catalogs and on `hydrolog.testing`'s example network |
| 8 | Nogat | `src/nogat/` skeleton (the part of HUB §7 it needs) and `nogat gui` 0.1: server, token, CSP, „Pulpit”, catalog bridge, inbox, „Polecenia” | 3-4 | browser smoke: a Hydrolog example through the bridge; a hand-off file opened |
| 9 | Hydrolog | Hosted module: the hydrograph workbench (item 6, first part) | 3-4 | Hydrograf's sample hand-off opens with the same values and peak |
| 10 | Hydrograf | Kit copies replace its shell, theme and info code; „Przenieś do Hydrologa” and „Wczytaj z Hydrologa” in advanced mode, with the field mapping and a contract test on `hydrolog.testing` | 2-3 | e2e: Hydrograf, file, host, Hydrograf gives the same request |
| 11 | Archiwista | Visual identity step 5 on the kit; „Kreator polecenia”; a link that fills the paste field from the host | 3-5 | e2e: form to line to plan window, pasted line to form; BDOT10k and orthophoto without pasting |
| 12 | IMGWTools | Hosted module (item 8); Jinja, HTMX and Pico removed | 2-3 | host smoke; REST and MCP tests green |
| 13 | Hydrolog | Network workbench with `<nogat-schematic>` and per-node results | 2-3 | `hydrolog.testing` example network routed and drawn |
| 14 | Hydrograf | Control points (outlet first) give `hydrolog-network/1` of residual sub-catchments; the schematic beside the map | own plan | its plan |
| 15 | Nogat | Registry entries active, map, PROGRESS, CHANGELOG; `nogat gui` released with the next release set | 0.5 | gate |

Without step 14, about 25 to 35 sessions. Later, outside this plan: Retman
filling the editor from a Polish sentence (`retman plan run`), a Hydraulik
module taking `route network` tables, a team mode of the host, hand-offs in
Archiwista projects.

## Risks

| Risk | Effect | Mitigation |
|---|---|---|
| Nogat grows from a hub into an app | the repository of the standard carries a web server and browser tests | the kit and the host in their own directories with their own tests; or a separate repository (question 1) |
| The `nogat` package does not exist yet | the host waits for HUB §7 and a release set | develop with an editable install from the workspace; release with the next set |
| Kit copies drift | the shared look and fixes split again | `kit.json` hashes, the copy check in `drift`, each app's contract test |
| Two catalog shapes until step 5 | the editor misses IMGWTools | the editor reads commands-1 only; Archiwista's IMGW adapter normalises meanwhile |
| A browser page runs tools on the user's machine | misuse from another page or user | loopback only, one-time token, CSRF header, no path options from requests, writes only after `check_command` and a confirmation |
| Hydrograf on a remote server, the host on loopback | links with a fragment may be blocked or too long | file and clipboard always work; the link is a convenience |
| Hydrograf pins Hydrolog 0.6.3, the host the release set | the same inputs give different numbers | the hand-off carries the producer's version and result; the module shows the difference |
| Two map engines | no shared map component | only map chrome and basemaps are shared (question 8) |
| The work competes with the first release set and Archiwista's release | both slip | steps after those releases unless the author says otherwise (question 10) |

## Open questions for the author

1. The host in Nogat (Nogat becomes `hub` and `app`), or in a new repository?
2. A tool's GUI module in its own package (recommended), or all in Nogat?
3. One local user for the first version; when, if ever, a LAN team mode, and
   would it reuse Archiwista's accounts?
4. IMGWTools: rebuild as a hosted module and remove the Jinja pages (D2), or
   restyle them (D1, the visual-identity step 7)?
5. The hand-off: `hydrolog-network/1` in a Nogat envelope (C2), or a flat
   document; and is Nogat the envelope's owner?
6. Where hand-offs persist: only in the host, or also in Archiwista projects?
7. The editor: every option of every command, grouped (full power), or basic
   and advanced views; Kartograf in Archiwista first?
8. Hydrograf's CDN libraries: vendor them for CSP `'self'` and offline use now;
   and should Hydrograf move to MapLibre to share a map shell later?
9. Joined sub-catchments: is the schematic shown in Hydrograf (ADR-0013), in
   Hydrolog's module or both, and when does Hydrograf plan its control points?
10. The order against the first release set and Archiwista's release (D2, D3
    of the projects plan).
11. Do steps 2, 3, 10, 11 and 12 replace steps 5 to 7 of the visual identity?

## Results

None yet.
