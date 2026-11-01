# Plan: Nogat as the GUI platform of the ecosystem

Approved: pending

Requirements: HUB-5.2, DEV-17.4, DEV-15.1, DEV-15.3, AGI-2.1, AGI-2.3,
AGI-6.1, HUB-1.1, HUB-1.2, HUB §7, DEV §13, ECO-054, ECO-055. Continues the
[visual identity](2026-11-01-visual-identity.md) (its steps 5 to 7), gives the
[shared GUI](2026-10-20-unified-gui.md) the scope it lacked without deciding
its storage question, and keeps projects in Archiwista
([projects plan](2026-10-31-archiwista-projects.md)). A draft of 2026-11-01,
revised the same day with the author's decisions A1 to A5; no code.

## Goal

The author's request of 2026-11-01, in short:

1. Nogat keeps the common parts of the GUIs; each project only extends them.
2. Hydrolog and IMGWTools get GUIs.
3. Kartograf is reached through Archiwista, which takes a pasted producer
   command; a graphical editor of such commands gives the producers' full power.
4. Nogat is the main product: one GUI into which every project plugs and
   which carries data between them (inputs changed in Hydrograf's advanced
   mode appear in Hydrolog's fields).
5. Hydrolog shows the river network as a simple topological network.

Decided by the author on 2026-11-01, after the first draft:

- A1. An app may be framed from one address only, the Nogat host: its CSP
  `frame-ancestors` names that origin, set in the app's configuration,
  `'none'` when it runs alone; `X-Frame-Options` goes where it contradicts.
- A2. The whole package, or a part of it, runs on one machine.
- A3. Every project also works alone, without Nogat (Zen 10 of
  [the standard](../../standards/README.md#zen-of-nogat)).
- A4. Every app gets an embedded mode: no top bar or rail of its own, Nogat's
  shell around it, the theme and the data from the host.
- A5. Through Nogat a person signs in once, at the start, and then reaches the
  apps. Nogat takes Archiwista's model: local mode with a one-time token in
  the address's fragment; team mode with TLS, accounts and roles.

## Where it starts

Checked on 2026-11-01 in the workspace checkouts and on the running services
(`curl` of headers only); a path outside Nogat is relative to its repository.

### The GUIs

| GUI | Stack, size, build | Libraries | CSP and framing | Auth and serving | Shared with Nogat today |
|---|---|---|---|---|---|
| Archiwista (`feature/archiwista-projects`) | Preact 10.29.8 + htm 3.1.1 as ES modules, no build (A-ADR-028, `docs/DECISIONS.md:1451`); about 34,000 lines in `src/archiwista/web/` | vendored with SHA-256 per file (`src/archiwista/web/vendor/vendor.json`); MapLibre GL 6.14.0; charts drawn as SVG (`web/src/views/station-chart.js`) | `script-src 'self'`, `frame-ancestors 'none'` (`src/archiwista/security.py:1484-1519`; seen on 127.0.0.1:8090) | local and team mode (next section); FastAPI; :8090 answers `403 tls_required` | nothing: own indigo `styles.css`, no dark theme, no `tokens.css` in any of its three worktrees (visual identity step 5 not started) |
| Hydrograf (`Hydrograf-gui`, `feature/visual-identity`, port 8081) | plain IIFE scripts on `window.Hydrograf` (`frontend/js/shell.js:10-13`), no build; about 9,200 lines of JS, CSS and HTML | Leaflet 1.9.4, MapLibre GL 4.7.1, Chart.js 4.4.7, VectorGrid 1.3.0 from unpkg and jsDelivr with SRI (`frontend/index.html:17-24,476-496`) | allows unpkg and jsDelivr scripts; `frame-ancestors 'none'`, `X-Frame-Options: DENY` (`docker/nginx.conf:48,50`; seen on :8080 and :8081) | an admin key only (next section); nginx in Docker before FastAPI and PostGIS | `tokens.css` copied at Nogat `29e7e1c` (`frontend/css/tokens.css:1-2`); shell and theme switch ported from Nogat's mockup (`shell.js`, `theme-*.js`); its own (i) tooltips with MathML (`info.js`, 76 texts in `info-texts.js`) |
| IMGWTools web (`feature/archiwista-projects`) | FastAPI + Jinja2 + HTMX; about 1,900 lines in `src/imgwtools/web/`: archives, PMAXTP, stations, map | HTMX 1.9.10 and Pico 2 from unpkg and jsDelivr (`src/imgwtools/web/templates/base.html:9,12`) | no CSP header (seen on 127.0.0.1:8000); CORS `*` (`src/imgwtools/api/main.py:149`) | reads open, writes need `X-API-Key` (`src/imgwtools/api/routes/commands.py:22,97`); `imgw server` beside `/api/v1` and `/mcp` | nothing |
| Hydrolog, Kartograf, Hydraulik, Retman | no GUI: library and CLI, Kartograf and Hydrolog also MCP; Hydrolog's README plans none | – | – | – | – |

Shared already, but written three times:

- The shell and the theme switch exist as Nogat's mockup
  ([mockup.js](../../design/mockups/hydrograf/mockup.js), 338 lines), as
  Hydrograf's port (`frontend/js/shell.js`, 292 lines, `theme-*.js`) and as
  Archiwista's Preact shell (`src/archiwista/web/src/shell.js`, 633). They
  drift: [design/README.md](../../design/README.md#theme) stores the theme
  under `theme`, the specimen and Hydrograf under `nogat-theme`
  (`design/specimen.html:10`, `frontend/js/theme-init.js:11`).
- Only Hydrograf's `tokens.css` names its Nogat commit, and `drift` compares
  only dependency pins with tags (`report_drift` in
  [ecosystem.py](../../scripts/ecosystem.py)), so copies go unchecked;
  Archiwista's `vendor.json` (source and SHA-256 per file) is a model.
- Maps differ (MapLibre 6 in Archiwista; Leaflet with MapLibre basemaps in
  Hydrograf), and so do charts (SVG by hand; Chart.js).

### Sign-in today

- Archiwista, the model A5 names (A-ADR-012, A-ADR-046). Local mode:
  `archiwista serve` listens on 127.0.0.1 only and prints a one-time address
  (`#token=…`, 10 minutes; `src/archiwista/server.py:577-603`) that becomes
  the cookie `archiwista_session` (`HttpOnly`, `SameSite=Strict`, 24 hours
  idle; `security.py:88,115`). Team mode (`[team]`): TLS in the server or
  `trusted_proxies` with `X-Forwarded-Proto: https`, Argon2id accounts,
  throttled sign-in, `__Host-archiwista_session` (`security.py:91`), roles
  `admin` and `store_writer` with project visibility (`auth/authorize.py`),
  and decision 8: a trusted proxy names the person in `proxy_user_header`
  (`proxy_autocreate` creates the account). Every `/api` request carries
  `X-Archiwista-CSRF` (`security.py:95`). Code: `security.py` 1,621 lines,
  `api/session.py` 752, `auth/` 1,179.
- Archiwista refuses frames twice: `frame-ancestors 'none'` is fixed
  (`security.py:1519`), and its fetch-metadata rule opens a page of another
  site only as a top-level navigation (`security.py:1002-1066`). Its SPA uses
  absolute paths (`API_PREFIX = "/api/v1"`, `web/src/api.js:119`).
- Hydrograf has no accounts: admin routes take `X-Admin-Key`, compared in
  constant time (`backend/api/dependencies/admin_auth.py`) and kept by the
  admin page in `localStorage` (`frontend/js/admin/admin-api.js:12`); users
  are "a separate, later stage" (`docs/DECISIONS.md:800`, ADR-036), and the
  branch `feat/wspolne-uwierzytelnianie` ("shared authentication") is empty
  (`docs/PROGRESS.md:306`). Its nginx listens on 127.0.0.1:8080
  (`docker-compose.yml:98-102`); its pages use absolute paths (`/api/…`,
  `/data/…` in `frontend/js/api.js`, `map.js`).
- IMGWTools' web GUI has no sign-in; writes of `/api/v1` need `X-API-Key`.

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
(`Hydraulik-sfincs/tests/contract/test_command_catalog.py:20`). Archiwista
has the server side of an editor (`GET /commands`, `POST /commands/parse`,
`/validate`, `/format`, SPEC lines 3423-3426; `CommandOption` in
`src/archiwista/sources/types.py:488-583`) but only the field „Wklej
polecenie producenta” in its UI (`web/src/map/source.js:199-240`); in use,
BDOT10k and orthophoto are downloaded only by pasting a command
([PROGRESS](../PROGRESS.md#next), item 6).

### Data between the apps

- Hydrograf computes with Hydrolog 0.6.3 as a library
  (`backend/requirements.txt:59`). Its advanced mode edits 11 morphometry
  fields (`frontend/js/advanced.js:20-30`) and a rain series
  (`custom-rain.js:558-566`); the request adds PMAXTP probability and
  duration, AMC, the hietogram, the unit hydrograph and the tc method
  (`backend/models/schemas.py:358-510`).
- Hydrolog's `hydrolog-network/1` (routing branch,
  `src/hydrolog/schemas/hydrolog-network-1.schema.json`) holds the same per
  subcatchment (`watershed`; `runoff` with tc, `ia_coefficient`, `amc`, the
  unit hydrograph; `rainfall`) and refuses unknown fields
  (`src/hydrolog/routing/document.py:187`); no registry edge exchanges it.
- Names differ: `length_to_centroid_km` is `Lc_km`
  (`backend/api/endpoints/hydrograph.py:333-343`); `nash_estimation` has no
  option in `hydrograph generate`; Hydrolog takes `total_mm`, not PMAXTP's
  probability and duration. No GUI hands data to another.

### The network discussed on 2026-10-25

In the coordinating session of 2026-10-24 to 2026-10-28 (transcript
`~/.omp/agent/sessions/-tmp/2026-10-24T13-52-09-509Z_01a16e2e-e525-73dd-87db-ba388db8e443.jsonl`,
messages of 2026-10-25, 09:03 to 09:54 UTC) the author asked for objects per
subcatchment, reach, junction and outlet, defined by JSON and picked in
Hydrograf; a pick joined with everything above it into one unit, one outlet
picked first, no pick absorbing the area above another; rainfall per
sub-catchment; and the network shown "with the values used in the
calculation as a topological schematic (e.g. a Beck map)". Hydrolog recorded
it in ADR-0012 (`docs/decisions/0012-network-objects-rainfall-and-runoff.md:11-17`)
and ADR-0013 (`hydrolog-network-schematic/1`, laid out by the library, drawn
by any consumer: "Hydrograf will show the picture next to its map",
`0013-network-schematic.md:12,50-51,69-71`), with Hydrograf's mapping in
`docs/INTEGRATION.md:350-368`, all on the unmerged `feature/routing-schematic`.

### Constraints

- ECO-055 rejected a shared CSS framework or component package (a build step,
  a dependency between apps); DEV-15.1 asks for ES modules without a build;
  the apps run offline under CSP `'self'`. HUB-1.1 gives Nogat no GUI,
  HUB-1.2 keeps other projects' code out of Nogat, and the `nogat` package is
  planned only ([PROGRESS](../PROGRESS.md#status)).
- `nogat` will install Kartograf, IMGWTools, Hydrolog and Retman
  ([first release set](2026-10-20-first-release-set.md)). Hydrograf runs in
  Docker (PostGIS limited to 2 GB, the API to 8 GB in `docker-compose.yml`);
  Archiwista follows alone; the two cannot share one Python environment
  (`affine`, [PROGRESS](../PROGRESS.md#open-questions)).
- Cookies are not isolated by port
  ([RFC 6265, 8.5](https://www.rfc-editor.org/rfc/rfc6265#section-8.5)), and
  a port does not change the site `SameSite` compares
  ([HTML, same site](https://html.spec.whatwg.org/multipage/browsers.html#same-site)):
  on one host a session cookie reaches every port, also inside frames.

## Options

**A. How the shared parts travel.**

| Option | Verdict |
|---|---|
| A1. Copies of plain files (CSS, ES modules, custom elements without shadow DOM) with a kit version and SHA-256 per file, checked by Nogat | Recommended: no build, CSP `'self'`, offline; works in Preact, IIFE and Jinja pages alike; the cost is updating copies |
| A2. An npm package or bundled component library | Rejected, as in ECO-055: a build step and Node in build-free apps |
| A3. Files served at run time by a Nogat server | Rejected: breaks CSP `'self'` and offline use, and apps must work alone (A3) |
| A4. Package data of `nogat`, mounted by each app | Rejected: every app would depend on `nogat` (A3) |

**B. The Nogat GUI host.** B1 (a portal of links) falls to A4; B2 (one SPA
holding every GUI) to three stacks, Hydrograf's Docker and the `affine`
conflict; B4 (Nogat rendering every UI) to two rewritten frontends. **B3, the
apps in frames of Nogat's shell from its one origin, with the tools that have
no server as modules of the host, is the author's decision (A1, A4).**

**C. Data sync.**

| Option | Verdict |
|---|---|
| C1. A new flat `hydrograph-inputs/1` | Rejected: a second schema of what `hydrolog-network/1` already holds |
| C2. `hydrolog-network/1` as the payload (one watershed is one subcatchment and the outlet; joined sub-catchments are more nodes) in a small Nogat envelope `nogat-handoff/1` with provenance | Recommended |
| C3. Shared state in a host database | Rejected for now: apps and modules keep their own state |

**D. IMGWTools.** D1: restyle the Jinja pages (visual identity step 7),
keeping a third stack and CDN libraries. D2, recommended: a hosted module
from the catalog, without the Jinja and HTMX pages; `imgw server` (REST, MCP)
stays; 3.0.0 is untagged (ECO-020). **E. The command editor**: in Archiwista
only (E1), or a kit component for Archiwista and the host (E2, recommended).

**F. How a framed app learns who signed in (A5).**

| Option | Verdict |
|---|---|
| (a) One origin: Nogat proxies `/archiwista/` and `/hydrograf/` and names the person to each app | Rejected: both SPAs use absolute paths and would need a base path; one origin makes all apps one security domain (a script of one reads the frames and storage of the others) |
| (a′) A front door: Nogat proxies each app on a port of its own of the same host, apps on loopback; Nogat names the person in the way the app already trusts | Recommended for team mode (in local mode all is on 127.0.0.1 and the frames load the apps directly): the browser reaches only Nogat; separate origins keep the apps apart while one host keeps one cookie jar, so one sign-in; Archiwista already trusts such a proxy (A-ADR-046 decision 8); no base paths |
| (b) Nogat signs short-lived assertions that each app verifies and exchanges for its own session; apps on their own ports | Rejected: every app on the network with its own TLS, a new sign-in endpoint and keys in each app, a sign-out that must reach every app |
| (c) Each app keeps its own sign-in | Rejected by A5 |

**G. Sign-in code.**

| Option | Verdict |
|---|---|
| R1. Archiwista's auth moved into a library (`nogat-auth`) imported by Archiwista and the host | Rejected now: a dependency between projects, rejected against Zen 10 in ECO-051; Archiwista would split a storage-neutral core (tokens, sessions, CSRF, passwords, throttle, transport) from its state and index databases, messages and errors, and repeat its v0.4 security checklist (`docs/reports/v0.4-security-checklist.md`) |
| R2. That core as server files of the kit, copied with hashes like the JS | Later: when a third server needs accounts (Hydrograf's deferred user system) |
| R3. Nogat implements Archiwista's model (A-ADR-012; A-ADR-046 decisions 1 to 7) with the same parameters and test cases; Archiwista keeps its code and trusts Nogat by decision 8 | Recommended: no dependency, no refactor of reviewed code; the two never serve the same request |

**H. How an app knows it is embedded.** A query flag can be added by anyone,
so it may only hide the chrome at first paint; a proxy header says "behind
Nogat", not "in a frame", and is absent in local mode (no proxy there).
Recommended: a `postMessage` handshake with both origins checked.

## Decision

**Proposal**, recommended by this research; nothing is decided until the
author approves it.

1. **Nogat becomes `hub` and `app`.** A new ECO decision amends HUB-1.1
   (Nogat holds the GUI kit and the host), HUB-7.3 (`nogat up`), ECO-055 and
   DEV-15.3 (a copy of the kit, not of the tokens only), and adds to DEV §15:
   an app accepts frames from one configured origin (default `'none'`), has
   the embedded mode of item 5, and works alone (A1, A3, A4). HUB-1.2 stays:
   a tool's GUI module ships in the tool's package.
2. **The kit** (`design/kit/`, option A1), Nogat's own code grown from its
   mockup and specimen, with Hydrograf's port as the reference:

   | File | Content |
   |---|---|
   | `tokens.css`, `base.css` | today's tokens; buttons, inputs, panels, badges, chips, tables, dialog, toast |
   | `shell.css`, `shell.js` | top bar, rail, view layout, resizers with keys, phone sheets, a layout event for maps, the embedded switch; an API for rail items and panels |
   | `theme.js` | pre-paint init and the three-way switch, one storage key |
   | `info.js`, `form.js` | `<nogat-info>` tooltip with MathML, the texts the app's; number with unit and bounds, choice with meanings, series table with paste and CSV |
   | `command-form.js`, `schematic.js` | `<nogat-command-form>` (item 8); `<nogat-schematic>` drawing `hydrolog-network-schematic/1` in the tokens (ADR-0013 lets a consumer draw it) |
   | `chart-theme.js`, `basemaps.json` | tokens as Chart.js defaults and SVG classes; shared basemaps, attribution and the origins a CSP must allow |
   | `embed.js`, `handoff.js` | both sides of the handshake (item 5); read, validate and write `nogat-handoff/1` |
   | `kit.json` | kit version (SemVer) and SHA-256 of every file |

   Projects add their CSS after the kit (tokens only), rail items, panels and
   texts (DEV-15.2), and never edit a kit file; `drift` (HUB-4.1) reports
   each kit copy as current, behind or modified against `kit.json`.
3. **Plugging in.** The registry gains an optional `gui` field: `kind`
   (`hosted`, a module in the tool's package found through the entry point
   group `nogat.gui`; `embedded`, an app in a frame), the kit directory, and
   the payloads it `accepts` and `emits`. Structure only (HUB-2.4): addresses,
   ports and start commands are `[gui]` of `nogat.toml` (DEV-18.1).
4. **The host and the sign-in** (A2, A5; options F (a′) and G R3):

   | | Local mode | Team mode |
   |---|---|---|
   | Who | one person at the machine | people on the LAN; everything on one server |
   | Nogat | 127.0.0.1; a one-time address in the fragment, a session cookie, a CSRF header (A-ADR-012's rules) | TLS from certificate files; Argon2id accounts, throttling, sessions, the action log (A-ADR-046 decisions 1 to 7); `nogat users add ID --role admin` at the terminal |
   | Apps reach the browser | directly on their loopback ports, in frames | through Nogat's front ports, one per app on the same host; apps on loopback |
   | Archiwista | Nogat starts `archiwista serve --no-browser`, takes the owner's one-time address and opens it in the frame | team mode with `trusted_proxies` on loopback, `proxy_user_header`, `proxy_autocreate` and `origin` its front port |
   | Hydrograf | no sign-in, as on loopback today | the proxy forwards only people granted Hydrograf and adds `X-Admin-Key` for those granted its admin |
   | Hydrolog, IMGWTools | modules in the host process, under its session | the same, with a work directory per person |

   - Roles: a Nogat account has `admin` (accounts, grants, starting apps) and
     grants per app (`archiwista`, `hydrograf`, `hydrograf-admin`,
     `hydrolog`, `imgwtools`), checked before a front port forwards; inside
     Archiwista its roles, groups and sharing stay authoritative (A-ADR-029).
     The local owner has every grant, like Archiwista's `local` principal.
   - Sign-out ends Nogat's session and expires the apps' session cookies of
     the host (cookies ignore ports); a front port without a session forwards
     nothing, and Archiwista ends a proxy session whose header changes.
   - CSRF and clickjacking: Nogat's API takes a CSRF header and fetch
     metadata as Archiwista does; a front port forwards a state-changing
     request only with `Sec-Fetch-Site: same-origin`, drops cookies that are
     not the app's and any identity or key header a client sent, and streams
     (job events, the bootstrap log). An app's `frame-ancestors` names only
     the shell, and the shell has `frame-ancestors 'none'`, so nobody frames
     the frame.
   - Start: `nogat up` reads `[gui]`, starts the host, Archiwista as a child
     process and Hydrograf with `docker compose` (PostGIS, API and nginx on
     127.0.0.1), waits for their health, shows them on „Pulpit” and stops what
     it started; `nogat doctor` checks Docker, memory and ports.
   - A catalog bridge `/api/<tool>/<group>/<verb>` (AGI-6.1, AGI-6.3) runs the
     modules' commands, with paths only in the person's work directory; store
     lines go to Archiwista (ECO-054).
5. **The embedded mode** (A1, A4). An app has one optional setting, the
   shell's origin (Archiwista `[nogat] shell_origin`, Hydrograf
   `NOGAT_SHELL_ORIGIN` into an nginx template): `frame-ancestors` names it,
   `X-Frame-Options` goes, Archiwista's fetch-metadata rule admits a frame
   navigation; unset, the headers stay as today. In a frame the page sends
   `nogat:hello` to that origin; the shell answers `nogat:welcome` (theme,
   language, a `MessageChannel` port) only to an app origin it configured;
   both check `event.origin` and `event.source`. Welcomed, the app hides its
   top bar and rail, follows `nogat:theme`, `nogat:handoff`, `nogat:navigate`
   and `nogat:signout`, and sends `nogat:title` and `nogat:handoff`; without a
   welcome within a second, or in its own tab, it is the app alone.
   `?nogat=1` only hides the chrome at first paint. `embed.js` holds both sides.
6. **The hand-off.** `schemas/exchange/handoff-1.schema.json` in Nogat,
   copied like the agent schemas (ECO-050): `schema` `nogat-handoff/1`,
   `created_at`, `producer` (tool, version, page to return to), `subject`,
   `provenance` (e.g. PMAXTP probability and duration), `payload`
   (`hydrolog-network/1` first: one subcatchment node with the values used)
   and an optional `result` for comparison. Embedded, `nogat:handoff` goes
   through the shell, which opens the target with it, the author's example in
   one click; alone, file and clipboard. Kept in `<data_dir>/nogat/handoffs/`.
7. **Hydrolog's GUI**, a hosted module in Hydrolog, called in process (no
   REST layer): first the hydrograph of one watershed with the inputs of
   Hydrograf's advanced mode, charts, balance, notices, CSV and hand-off; then
   the network with reach methods, rainfall per subcatchment, results per node
   and the schematic; later `stats flood-frequency`. Joining sub-catchments
   stays the control-point flow of ADR-0012, picked in Hydrograf.
8. **The command editor**, `<nogat-command-form>`, reads commands-1 entries:
   fields by type, a choice per `one_of` group, rules that enable fields, path
   options hidden where the app owns paths, the line live through
   `format_command`, a pasted line through `parse_command`, errors placed by
   `validate_command`'s `details.option`. Archiwista shows it as „Kreator
   polecenia” beside the paste field, feeding the same plan window; the host
   shows every installed catalog. AGI-2.3 and commands-1 gain optional option
   fields `i18n.pl`, `requires`, `excludes`, `applies_to`, `section`, `format`.
9. **IMGWTools**: option D2; the module covers stations, series read from a
   local store, PMAXTP (a depth handed to Hydrolog's rainfall) and current
   data; store sync stays in Archiwista.

The first version is local mode: steps 1, 2, 3, 8 (without „Polecenia”, which
needs steps 4 to 7), 9, 10 and 11, the author's example on one machine with
one sign-in. Team mode follows in steps 14 and 15.

## Steps

Producers before consumers (HUB-5.2): Nogat's contracts and kit, then the
producers' catalogs, then the host, then the GUIs. Each step runs in its
repository's own session on a topic branch (DEV-3.4), with its gate, ADR,
CHANGELOG and PROGRESS. Sizes are estimates in sessions.

| # | Owner | Step | Size | Verified by |
|---|---|---|---|---|
| 1 | Nogat | The ECO decision; HUB-1.1, HUB-7.3, DEV-15.3 and the new rule of DEV §15; AGI-2.3 and the option fields of commands-1; schemas `handoff-1` and of the handshake messages; the registry's `gui` field; Nogat's profiles `[hub, app]` | 1-1.5 | gate: `validate`, `standard`, schema tests |
| 2 | Nogat | Kit 0.1, chrome: `tokens.css`, `base.css`, `shell.*` with the embedded switch, `theme.js`, `kit.json`; the specimen rebuilt on it; browser tests | 1.5 | specimen in both themes, alone and in a frame |
| 3 | Nogat | Kit 0.1, parts: `info.js`, `form.js`, `chart-theme.js`, `embed.js`, `handoff.js`, `basemaps.json`; the copy check in `drift` | 2 | handshake tests across two origins; `drift` reports Hydrograf's copy |
| 4 | Kartograf | Export option `i18n.pl`, its constraints, `section` and `format` in `kartograf-commands/1` | 1-2 | commands-1 contract test; Archiwista's adapter tests unchanged |
| 5 | IMGWTools | `imgw commands list` and `imgw commands schema` with `--json` in commands-1 shape, with option texts and dependencies; the JSON Schema stays the REST and MCP input schema | 1.5-2 | commands-1 contract test |
| 6 | Hydrolog | Merge the routing branches (its PROGRESS, Next 8 and 10); public `parse_command` and `format_command`; the schematic document without an output file | 1-2 | gate; every catalog example read back into the same call |
| 7 | Nogat | Kit 0.2: `<nogat-command-form>` and `<nogat-schematic>` | 1.5-2 | tests on the three catalogs and on `hydrolog.testing`'s example network |
| 8 | Nogat | `src/nogat/` skeleton (the part of HUB §7 it needs); `nogat up` in local mode: sign-in, sessions and CSRF by A-ADR-012's rules, the shell with frames and modules, supervision of Archiwista and Hydrograf, „Pulpit”, the catalog bridge, the inbox, „Polecenia”; `nogat doctor` checks | 4-5 | on one machine: one sign-in, Archiwista and Hydrograf in frames, a Hydrolog example through the bridge |
| 9 | Hydrolog | Hosted module: the hydrograph workbench (item 7, first part) | 3-4 | Hydrograf's sample hand-off opens with the same values and peak |
| 10 | Hydrograf | Kit copies; the embedded mode; `NOGAT_SHELL_ORIGIN` into an nginx template (`frame-ancestors`, no `X-Frame-Options` when set, headers on every location); CDN libraries vendored; „Przenieś do Hydrologa” and „Wczytaj z Hydrologa” with the field mapping; the admin page without a key prompt when the proxy adds the key | 3-4 | e2e alone and in the shell; the same request after a round trip through Hydrolog |
| 11 | Archiwista | Visual identity step 5 on the kit; the embedded mode; `[nogat] shell_origin` for `frame-ancestors` and frame navigations (`security.py:1002-1066`); the owner's one-time address on demand for the host (`archiwista token` gives an agent's); „Kreator polecenia” | 4-6 | e2e alone (local and team) and in the shell; form to line to plan window and back |
| 12 | IMGWTools | Hosted module (item 9); Jinja, HTMX and Pico removed | 2-3 | host smoke; REST and MCP tests green |
| 13 | Hydrolog | Network workbench with `<nogat-schematic>` and results per node | 2-3 | `hydrolog.testing` example network routed and drawn |
| 14 | Nogat | Team mode: TLS, accounts, throttling, sessions, roles and grants, the action log; front ports naming the person per app, cookie and header filtering, streaming; a LAN runbook | 4-5 | Archiwista's v0.4 checklist applied to Nogat; a three-person run as Archiwista's |
| 15 | Archiwista | Team mode behind Nogat: tests of decision 8 with Nogat as the trusted proxy (front origin, autocreate, sign-out); the runbook's section | 1 | e2e with the host in team mode |
| 16 | Hydrograf | Control points (outlet first) give `hydrolog-network/1` of residual sub-catchments; the schematic beside the map | own plan | its plan |
| 17 | Nogat | Registry entries active, map, PROGRESS, CHANGELOG; `nogat` released with the next release set | 0.5 | gate |

Without step 16, about 33 to 45 sessions; the first version (steps 1 to 3 and
8 to 11) about 18 to 24. Later, outside this plan: Retman filling the editor
from a Polish sentence (`retman plan run`), a Hydraulik module taking
`route network` tables, Hydrograf on MapLibre to share a map shell.

## Risks

| Risk | Effect | Mitigation |
|---|---|---|
| Nogat grows from a hub into an app | the repository of the standard carries a web server, a sign-in and browser tests | the kit and the host in their own directories with their own tests; or a separate repository (question 1) |
| The `nogat` package does not exist yet | the host waits for HUB §7 and a release set | develop with an editable install from the workspace; release with the next set |
| Kit copies drift | the shared look and fixes split again | `kit.json` hashes, the copy check in `drift`, each app's contract test |
| One front door for all apps (team mode) | a defect in Nogat's sign-in opens every app | Archiwista's rules and checklist; apps on loopback; no session, nothing forwarded |
| Cookies reach every port of the host | an app's server receives Nogat's cookie in local mode; Archiwista's cookie reaches Nogat's ports | `HttpOnly` cookies; front ports drop foreign cookies; apps log no cookies; Nogat ignores app cookies |
| Another account of the team server connects to an app's loopback port as the proxy (A-ADR-046, its consequences) | sign-in as anyone in Archiwista | the runbook's server without other accounts, or signed assertions (question 5) |
| Two implementations of sign-in, Nogat's and Archiwista's | their levels drift apart | one checklist; Nogat's tests replay Archiwista's cases; R2 when a third server needs accounts |
| Everything on one machine (A2) | Hydrograf's API (8 GB) and PostGIS (2 GB) beside Archiwista's previews | `nogat up` starts only the configured apps; `nogat doctor` checks memory |
| Hydrograf pins Hydrolog 0.6.3, the host the release set | the same inputs give different numbers | the hand-off carries the producer's version and result; the module shows the difference |
| The work competes with the first release set and Archiwista's release | both slip | steps after those releases unless the author says otherwise (question 11) |

## Open questions for the author

1. The host in Nogat (Nogat becomes `hub` and `app`), or in a new repository?
2. A tool's GUI module in its own package (recommended), or all in Nogat?
3. Local mode first and team mode later (recommended), or both at once?
4. Team roles: Nogat signs in and grants apps while Archiwista keeps its
   roles, groups and sharing (recommended), or Nogat sends roles that
   Archiwista adopts, for one administration screen?
5. Trust on a team server: the plain proxy header that A-ADR-046 allows with
   its runbook rule (recommended first), or signed short-lived assertions that
   Archiwista and Hydrograf verify (code in both)?
6. Should Archiwista join the `nogat` environment and release set, so that
   `nogat up` starts it without a separate install?
7. IMGWTools: a hosted module without the Jinja pages (D2), or restyled (D1)?
8. The hand-off: `hydrolog-network/1` in a Nogat envelope (C2) or a flat
   document; is Nogat its owner; should Archiwista projects keep hand-offs?
9. The editor: every option of every command, grouped (full power), or basic
   and advanced views; Kartograf in Archiwista first?
10. Joined sub-catchments: is the schematic shown in Hydrograf (ADR-0013), in
    Hydrolog's module or both, and when does Hydrograf plan its control points?
11. The order against the first release set and Archiwista's release (D2, D3).
12. Do steps 2, 3, 10, 11 and 12 replace steps 5 to 7 of the visual identity?

## Results

None yet.
