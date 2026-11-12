# Plan: the GUI hub, stage 2 of the GUI platform

Approved: pending; item 6, the hand-off schema (step N1 of
[Hydrolog's GUI](2026-11-02-hydrolog-gui.md)), approved by the author on
2026-11-02 ahead of the rest

Status: stage 2, deferred by the author on 2026-11-12 until stage 1,
[links between the GUIs and one hand-off](2026-11-12-gui-links-and-handoff.md),
is done. The path of this file keeps its first name because other
repositories and the description of `handoff-1` cite it.

Requirements: HUB-5.2, DEV-17.4, DEV-15.1, DEV-15.3, AGI-2.1, AGI-2.3,
AGI-6.1, HUB-1.1, HUB-1.2, HUB §2, DEV §13, ECO-054, ECO-055. Continues the
[visual identity](2026-11-01-visual-identity.md) (its steps 5 to 7), gives the
[shared GUI](2026-10-20-unified-gui.md) the scope it lacked without deciding
its storage question, and keeps projects in Archiwista
([projects plan](2026-10-31-archiwista-projects.md)). A draft of 2026-11-01,
revised twice that day with the author's decisions A1 to A5 and B1 to B6, and
on 2026-11-12 with C1 to C3: the host leaves Nogat for a new project, and the
work is split in two stages; no code.

"The GUI hub" and `guihub` (package, command, data directory, `nogat.toml`
section) are a working name; the author names the project later (question
11). Contracts this plan gives Nogat keep the `nogat` prefix
(`nogat-handoff/1`, `<nogat-…>` elements, `nogat:` messages, `X-Nogat-*`
headers, `?nogat=1`, the entry point group `nogat.gui`): they belong to the
standard, not to the hub, and survive its renaming. IMGWTools is Obserwator
since 2026-11-03 (ECO-057); the evidence of 2026-11-01 below keeps the old
name.

## Goal

The author's request of 2026-11-01, in short, as revised on 2026-11-12:

1. Nogat keeps the common parts of the GUIs; each project only extends them.
2. Hydrolog and Obserwator get GUIs.
3. Kartograf is reached through Archiwista, which takes a pasted producer
   command; a graphical editor of such commands gives the producers' full power.
4. The GUI hub is the main product for people: one place that starts every
   GUI of the ecosystem, switches between them and carries data between them
   (inputs changed in Hydrograf's advanced mode appear in Hydrolog's fields).
   Nogat stays without a GUI.
5. Hydrolog shows the river network as a simple topological network.

Decided by the author on 2026-11-01:

- A1. An app may be framed from one address only, the hub's: its CSP
  `frame-ancestors` names that origin, set in the app's configuration,
  `'none'` when it runs alone; `X-Frame-Options` goes where it contradicts.
- A2. The whole package, or a part of it, runs on one machine.
- A3. Every project also works alone, without the hub (Zen 10 of
  [the standard](../../standards/README.md#zen-of-nogat)).
- A4. Every app gets an embedded mode: no top bar or rail of its own, the
  hub's shell around it, the theme and the data from the hub.
- A5. Through the hub a person signs in once, at the start, and then reaches
  the apps, on Archiwista's model: local mode with a one-time token in the
  address's fragment; team mode with TLS, accounts and roles.
- B1. Replaced by C1 on 2026-11-12 (the host was to live in Nogat, which
  would have become `hub` and `app`).
- B2. Local and team mode are built together.
- B3. Roles come from the hub and are the same everywhere: an app under the
  hub adopts them; an app alone keeps its own administration.
- B4. Trust is variant A: the hub's proxy names the account and its roles in
  headers (A-ADR-046 decision 8). Accepted with it: any process on the server
  that reaches an app's loopback port can forge them, so a team server is
  dedicated (no other OS accounts or untrusted services, as Archiwista's
  runbook asks), and the hub strips identity and role headers and the other
  apps' cookies from client requests. Variant B, signed short-lived
  assertions, is mandatory before other accounts or services on the server,
  apps on separate machines, or access from outside the LAN. Unix sockets
  instead of loopback TCP are an optional hardening to evaluate.
- B5. Topology 1 (one hub process hosting the Hydrolog and Obserwator
  modules, Archiwista as a child process in its own environment, Hydrograf in
  its Docker stack) is transitional; topology 2 (each app in its own
  container, one compose file for the package, the hub's container hosting
  the modules) is the target. Every app stays standalone. A person signs in
  once, at the start, never again in the apps; app sessions renew silently.
- B6. Obserwator gets a new hosted module; its Jinja pages are removed.

Decided by the author on 2026-11-12:

- C1. The host is a new project, the GUI hub, with its own repository and
  profile `app`. Nogat stays `hub` and runs no GUI.
- C2. The GUI kit stays in Nogat, `design/kit/`, beside the tokens: a copied
  template, as `standards/ci/` is for CI. The hub copies it like every other
  GUI; no app depends on the hub.
- C3. Two stages. Stage 1, [its own plan](2026-11-12-gui-links-and-handoff.md):
  a menu in every GUI that leads to the others, and the hand-off by file and
  clipboard fixed and made the same everywhere. Stage 2, this plan: the hub
  with one window and one sign-in.

## Since 2026-11-01

- Hydrolog's GUI exists, by its own plan
  ([pointer](2026-11-02-hydrolog-gui.md)): `hydrolog gui serve` on
  127.0.0.1:8070, Preact and htm without a build, Nogat's tokens and marks,
  Archiwista's shell; a module for a host through the entry point group
  `nogat.gui` (`hydrolog.gui:gui_module`, a `GuiModule`); `?nogat=1` hides its
  top bar and rail at first paint. Item 7 below and steps 12 and 16 shrink
  accordingly.
- `nogat-handoff/1` (item 6) is published and in use: Hydrograf → Hydrolog (a
  watershed, a network with `node_provenance`), Archiwista → Hydrolog (a
  station's series, `hydrolog-series/1`), by file and clipboard.
- Stage 1 adds the app menu, the kit's `nogat-handoff.js` and the copy report in
  `drift`; this plan builds on them and no longer lists them.

## Where it starts

Checked on 2026-11-01 in the workspace checkouts and on the running services
(`curl` of headers only); a path outside Nogat is relative to its repository.

### The GUIs

| GUI | Stack, size, build | Libraries | CSP and framing | Auth and serving | Shared with Nogat today |
|---|---|---|---|---|---|
| Archiwista (`feature/archiwista-projects`) | Preact 10.29.8 + htm 3.1.1 as ES modules, no build (A-ADR-028, `docs/DECISIONS.md:1451`); about 34,000 lines in `src/archiwista/web/` | vendored with SHA-256 per file (`src/archiwista/web/vendor/vendor.json`); MapLibre GL 6.14.0; charts drawn as SVG (`web/src/views/station-chart.js`) | `script-src 'self'`, `frame-ancestors 'none'` (`src/archiwista/security.py:1484-1519`; seen on 127.0.0.1:8090) | local and team mode (next section); FastAPI; :8090 answers `403 tls_required` | nothing: own indigo `styles.css`, no dark theme, no `tokens.css` in any of its three worktrees (visual identity step 5 not started) |
| Hydrograf (`Hydrograf-gui`, `feature/visual-identity`, port 8081) | plain IIFE scripts on `window.Hydrograf` (`frontend/js/shell.js:10-13`), no build; about 9,200 lines of JS, CSS and HTML | Leaflet 1.9.4, MapLibre GL 4.7.1, Chart.js 4.4.7, VectorGrid 1.3.0 from unpkg and jsDelivr with SRI (`frontend/index.html:17-24,476-496`) | allows unpkg and jsDelivr scripts; `frame-ancestors 'none'`, `X-Frame-Options: DENY` (`docker/nginx.conf:48,50`; seen on :8080 and :8081) | an admin key only (next section); nginx in Docker before FastAPI and PostGIS | `tokens.css` copied at Nogat `29e7e1c` (`frontend/css/tokens.css:1-2`); shell and theme switch ported from Nogat's mockup (`shell.js`, `theme-*.js`); its own (i) tooltips with MathML (`info.js`, 76 texts in `info-texts.js`) |
| IMGWTools web (`feature/archiwista-projects`) | FastAPI + Jinja2 + HTMX; about 1,900 lines in `src/imgwtools/web/`: archives, PMAXTP, stations, map | HTMX 1.9.10 and Pico 2 from unpkg and jsDelivr (`src/imgwtools/web/templates/base.html:9,12`) | no CSP header (seen on 127.0.0.1:8000); CORS `*` (`src/imgwtools/api/main.py:149`) | reads open, writes need `X-API-Key` (`src/imgwtools/api/routes/commands.py:20-22,97`); `imgw server` beside `/api/v1` and `/mcp` | nothing |
| Hydrolog, Kartograf, Hydraulik, Retman | no GUI: library and CLI, Kartograf and Hydrolog also MCP; Hydrolog's README plans none (Hydrolog's GUI since: [Since 2026-11-01](#since-2026-11-01)) | – | – | – | – |

- The shell and the theme switch exist three times: Nogat's mockup
  ([mockup.js](../../design/mockups/hydrograf/mockup.js), 338 lines),
  Hydrograf's port (`frontend/js/shell.js`, 292) and Archiwista's Preact shell
  (`src/archiwista/web/src/shell.js`, 633). They drift:
  [design/README.md](../../design/README.md#theme) stores the theme under
  `theme`, the specimen and Hydrograf under `nogat-theme`
  (`design/specimen.html:10`, `frontend/js/theme-init.js:11`).
- Only Hydrograf's `tokens.css` names its Nogat commit; `drift` checks only
  dependency pins (`report_drift` in [ecosystem.py](../../scripts/ecosystem.py));
  Archiwista's `vendor.json` (SHA-256 per file) is a model of a checked copy.
  Maps (MapLibre 6; Leaflet) and charts (SVG by hand; Chart.js) differ.

### Sign-in today

- Archiwista, the model A5 names (A-ADR-012, A-ADR-046). Local mode listens on
  127.0.0.1 only (`src/archiwista/server.py:128-156`) and prints a one-time
  address (`#token=…`, 10 minutes; `server.py:577-603`) that becomes the
  cookie `archiwista_session` (24 hours idle; `security.py:88,115`). Team mode
  (`[team]`): TLS in the server or behind `trusted_proxies`, Argon2id
  accounts, throttling, `__Host-archiwista_session` (8 hours idle;
  `security.py:91,116`), roles `admin` and `store_writer`
  (`auth/authorize.py`), a CSRF header on every `/api` request
  (`security.py:95`). By decision 8 a trusted proxy names the person
  (`proxy_user_header`); `proxy_autocreate` creates the account without roles
  (`api/session.py:416-432`); the SPA offers that sign-in as a button
  (`web/src/views/login.js:66-72`); team mode refuses to start without an
  administrator who can sign in (`server.py:179-200`). Code: `security.py`
  1,621 lines, `api/session.py` 752, `auth/` 1,179.
- Archiwista refuses frames twice: `frame-ancestors 'none'` is fixed
  (`security.py:1519`), and its fetch-metadata rule opens a page of another
  site only as a top-level navigation (`security.py:1002-1066`). Its SPA uses
  absolute paths (`API_PREFIX = "/api/v1"`, `web/src/api.js:119`).
- Hydrograf has no accounts: admin routes take `X-Admin-Key` from a variable
  or a secret file, compared in constant time
  (`backend/api/dependencies/admin_auth.py`), and the admin page keeps it in
  `localStorage` (`frontend/js/admin/admin-api.js:12`); users are "a separate,
  later stage" (`docs/DECISIONS.md:800`), and `feat/wspolne-uwierzytelnianie`
  ("shared authentication") is empty (`docs/PROGRESS.md:306`). Its nginx
  listens on 127.0.0.1:8080 (`docker-compose.yml:98-102`); its pages use
  absolute paths (`/api/…`, `/data/…` in `frontend/js/api.js`, `map.js`).

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
(`Hydraulik-sfincs/tests/contract/test_command_catalog.py:20`). Archiwista has
an editor's server side (`GET /commands`, `POST /commands/parse`, `/validate`,
`/format`, SPEC lines 3423-3426) but only „Wklej polecenie producenta” in its
UI (`web/src/map/source.js:199-240`): BDOT10k and orthophoto are downloaded by
pasting ([PROGRESS](../PROGRESS.md#next), item 6).

### Data between the apps

- Hydrograf computes with Hydrolog 0.6.3 as a library
  (`backend/requirements.txt:59`); its advanced mode edits 11 morphometry
  fields and a rain series (`frontend/js/advanced.js:20-30`,
  `custom-rain.js:558-566`) beside PMAXTP probability and duration, AMC, the
  hietogram, the unit hydrograph and the tc method
  (`backend/models/schemas.py:358-510`).
- Hydrolog's `hydrolog-network/1` (routing branch,
  `src/hydrolog/schemas/hydrolog-network-1.schema.json`) holds the same per
  subcatchment (`watershed`, `runoff`, `rainfall`) and refuses unknown fields
  (`src/hydrolog/routing/document.py:187`); no registry edge exchanges it.
  Names differ: `length_to_centroid_km` is `Lc_km`
  (`backend/api/endpoints/hydrograph.py:333-343`), `nash_estimation` has no
  option in `hydrograph generate`, Hydrolog takes `total_mm`. No GUI hands
  data to another (since: [Since 2026-11-01](#since-2026-11-01)).

### The network discussed on 2026-10-25

In the coordinating session of 2026-10-24 to 2026-10-28 (transcript
`~/.omp/agent/sessions/-tmp/2026-10-24T13-52-09-509Z_01a16e2e-e525-73dd-87db-ba388db8e443.jsonl`,
2026-10-25, 09:03 to 09:54 UTC) the author asked for typed objects joined by a
JSON network picked in Hydrograf (outlet first, picks never absorbing another's
area, rainfall per sub-catchment), shown "with the values used in the
calculation as a topological schematic (e.g. a Beck map)". Hydrolog recorded it
in ADR-0012 and ADR-0013 (`hydrolog-network-schematic/1`, drawn by any consumer;
`docs/decisions/0013-network-schematic.md:12,50-51,69-71`) and
`docs/INTEGRATION.md:350-368`, on the unmerged `feature/routing-schematic`.

### Constraints

- ECO-055 rejected a shared CSS framework or component package; DEV-15.1 asks
  for ES modules without a build; apps run offline under CSP `'self'`. HUB-1.1
  gives Nogat no GUI, HUB-1.2 no other project's code; `nogat` is planned only.
- `nogat` will install Kartograf, Obserwator, Hydrolog and Retman
  ([first release set](2026-10-20-first-release-set.md)); Hydrograf runs in
  Docker (PostGIS 2 GB, API 8 GB, `docker-compose.yml`); Archiwista and
  Hydrograf cannot share a Python environment ([PROGRESS](../PROGRESS.md#open-questions)).
- A project enters `ecosystem.yaml` with a repository (`repo` is required,
  HUB §2) and then needs its mark and accent pair in `design/` (ECO-055).
- Cookies ignore ports ([RFC 6265, 8.5](https://www.rfc-editor.org/rfc/rfc6265#section-8.5)).
  Verified on 2026-11-01 in Chromium by the coordinating session: a host-only
  cookie set by 127.0.0.1:18101 was sent inside a frame of 127.0.0.1:18100,
  and Archiwista's `archiwista_session` of :8090 was sent to :18101. Frames
  across the ports of one host are same-site.

## Options

**A. How the shared parts travel.**

| Option | Verdict |
|---|---|
| A1. Copies of plain files (CSS, ES modules, custom elements without shadow DOM) with a kit version and SHA-256 per file, checked by Nogat | Recommended: no build, CSP `'self'`, offline; works in Preact, IIFE and Jinja pages alike; the cost is updating copies |
| A2. An npm package or bundled component library | Rejected, as in ECO-055: a build step and Node in build-free apps |
| A3. Files served at run time by the hub | Rejected: breaks CSP `'self'` and offline use, and apps must work alone (A3) |
| A4. Package data of `nogat`, mounted by each app | Rejected: every app would depend on `nogat` (A3) |

Where the kit lives is the author's decision C2: in Nogat, not in the hub, so
that the source of the shared parts is the neutral one that already holds the
tokens.

**B. The host**: apps in frames of the hub's shell from one origin, tools
without a server as modules of the hub: the author's decision (A1, A4, C1); a
portal, one SPA of every GUI and one server rendering all were rejected in the
first draft, the host in Nogat on 2026-11-12.

**C. Data sync.**

| Option | Verdict |
|---|---|
| C1. A new flat `hydrograph-inputs/1` | Rejected: a second schema of what `hydrolog-network/1` already holds |
| C2. `hydrolog-network/1` as the payload (one watershed is one subcatchment and the outlet; joined sub-catchments are more nodes) in a small Nogat envelope `nogat-handoff/1` with provenance | Chosen (approved with N1, 2026-11-02) |
| C3. Shared state in a hub database | Rejected for now: apps and modules keep their own state |

**D. Obserwator**: a hosted module without the Jinja pages, the author's
decision (B6). **E. The command editor**: in Archiwista only (E1), or a kit
component for Archiwista and the hub (E2, recommended).

**F. Sign-in and trust between the hub and the apps (A5, B4).**

| Option | Verdict |
|---|---|
| One origin: the hub proxies `/archiwista/` and `/hydrograf/` | Rejected: both SPAs use absolute paths; one origin makes all apps one security domain (a script of one reads the frames and storage of the others) |
| Variant A: a front door, a port of the hub per app on the same host, apps on loopback; the proxy names the account and its roles in headers | The author's decision (B4) for team mode; in local mode everything is on 127.0.0.1 and the frames load the apps directly. Separate origins keep the apps apart, one host keeps one cookie jar, so one sign-in |
| Variant B: short-lived signed assertions (account, roles, audience, expiry) that each app verifies | Mandatory later stage, before any trigger of B4 |
| Each app keeps its own sign-in | Rejected by A5 |

**G. Sign-in code.**

| Option | Verdict |
|---|---|
| G1. Archiwista's auth moved into a library (`nogat-auth`) imported by Archiwista and the hub | Rejected now: a dependency between projects, rejected against Zen 10 in ECO-051; Archiwista would split a storage-neutral core from its databases, messages and errors and repeat its v0.4 checklist (`docs/reports/v0.4-security-checklist.md`). Later, when a third server needs accounts, that core may travel as kit server files with hashes |
| G2. The hub implements Archiwista's model (A-ADR-012; A-ADR-046 decisions 1 to 7) with the same parameters and test cases; Archiwista keeps its code and trusts the hub by decision 8, extended with roles | Recommended: no dependency, no refactor of reviewed code |

**H. How an app knows it is embedded.** A query flag can be added by anyone,
so it may only hide the chrome at first paint; a proxy header says "behind
the hub", not "in a frame", and is absent in local mode (no proxy there).
Recommended: a `postMessage` handshake with both origins checked.

## Decision

**Proposal**, built on the author's decisions; the rest is recommended by this
research and waits for the author's approval.

1. **Nogat stays `hub`; the GUI hub is a new project** (C1, C2). A new ECO
   decision records A1 to A5, B2 to B6 and C1 to C3 (stage 1's decision may
   take C1 to C3 first); amends HUB-1.1 (Nogat also holds the GUI kit, a
   template it runs nowhere), ECO-055 and DEV-15.3 (a copy of the kit, not of
   the tokens only); and adds to DEV §15: an app accepts frames from one
   configured origin (default `'none'`), has the embedded mode of item 5,
   adopts the hub's roles under the hub, and works alone. HUB-1.2 stays: a
   tool's GUI module ships in the tool's package (question 1), and the hub
   contains no other project's code either. HUB-7.3 stays: `nogat` gets no
   `up` command; starting the GUIs is the hub's own CLI. Nogat defines the
   contracts between the hub and the apps: `nogat-handoff/1`, the handshake
   messages, the identity headers, the role vocabulary, the registry's `gui`
   field.
2. **The kit** (`design/kit/` in Nogat, option A1, C2), Nogat's own code grown
   from its mockup and specimen, with Hydrograf's port as the reference;
   stage 1 starts it with `nogat-app-menu.*`, `nogat-handoff.js` and `nogat-kit.json`:

   | File | Content |
   |---|---|
   | `tokens.css`, `base.css` | today's tokens; buttons, inputs, panels, badges, chips, tables, dialog, toast |
   | `shell.css`, `shell.js` | top bar, rail, view layout, resizers with keys, phone sheets, a layout event for maps, the embedded switch; an API for rail items and panels |
   | `theme.js` | pre-paint init and the three-way switch, one storage key |
   | `info.js`, `form.js` | `<nogat-info>` tooltip with MathML, the texts the app's; number with unit and bounds, choice with meanings, series table with paste and CSV |
   | `command-form.js`, `schematic.js` | `<nogat-command-form>` (item 8); `<nogat-schematic>` drawing `hydrolog-network-schematic/1` in the tokens (ADR-0013 lets a consumer draw it) |
   | `chart-theme.js`, `basemaps.json` | tokens as Chart.js defaults and SVG classes; shared basemaps, attribution and the origins a CSP must allow |
   | `embed.js` | both sides of the handshake (item 5); `nogat-handoff.js` of stage 1 gains `nogat:handoff` |
   | `nogat-app-menu.*`, `nogat-handoff.js`, `nogat-kit.json` | from stage 1 |

   Projects, the hub among them, add their CSS after the kit (tokens only),
   rail items, panels and texts (DEV-15.2), and never edit a kit file; stage
   1's copy report in `drift` (HUB-4.1) shows each copy as current, behind or
   modified.
3. **Plugging in.** The registry gains an optional `gui` field: `kind`
   (`hosted`, a module in the tool's package found through the entry point
   group `nogat.gui`, which Hydrolog already exports; `embedded`, an app in a
   frame), the kit directory, and the payloads it `accepts` and `emits`.
   Structure only (HUB-2.4): the apps' addresses are `[nogat.gui]` of
   `nogat.toml` (stage 1), the hub's ports and start commands `[guihub]`
   (DEV-18.1). The hub has its own entry with profile `app` once its
   repository exists.
4. **The hub and the sign-in**, local and team mode together (A2, A5, B2 to
   B5; F variant A, G2):

   | | Local mode | Team mode |
   |---|---|---|
   | Who | one person at the machine | people on the LAN; everything on one dedicated server |
   | The hub | 127.0.0.1; a one-time address in the fragment, a session cookie, a CSRF header (A-ADR-012's rules) | TLS; Argon2id accounts holding roles, throttling, sessions of 8 hours idle and 7 days, the action log (A-ADR-046 decisions 1 to 7); `guihub users add ID --role admin` at the terminal |
   | Apps reach the browser | directly on their loopback ports, in frames | through the hub's front ports, one per app; apps on loopback (topology 1) or an internal network (topology 2) |
   | Archiwista | its local mode; the hub asks it for the owner's one-time address and opens it in the frame | `trusted_proxies`, `proxy_user_header`, a new `proxy_roles_header`, `proxy_autocreate`; `origin` its front port |
   | Hydrograf | as alone | every account reaches it; the front port adds `X-Admin-Key` for `admin` |
   | Hydrolog, Obserwator | modules in the hub process under the hub's session | the same, with a work directory per person |

   - Roles (B3): `admin` and `store_writer` (question 2), held by the hub's
     accounts and sent as `X-Nogat-User` and `X-Nogat-Roles`. Archiwista
     adopts them as they are. Hydrograf: `admin` gets `X-Admin-Key`, which
     the hub reads from Hydrograf's secret file and never shows the browser.
     Obserwator: `store_writer` is what `X-API-Key` grants in its server;
     the module sends those writes to Archiwista (ECO-054), which checks the
     same role. Everything else needs an account only. The local owner holds
     both roles, as Archiwista's `local` principal does.
   - Archiwista under the hub: a `[team]` key `proxy_roles_header`, read only
     from trusted proxies, gives a proxy session its roles; a change of roles
     ends the session, as decision 8 does for the account; assigning roles is
     refused while it is set; `proxy_autocreate` accounts take the header's
     roles; the start check (`server.py:179-200`) accepts the hub's
     administrators. Groups and sharing stay in Archiwista (question 4).
   - Once at the start (B5): an embedded app that loses its session tells the
     shell (`nogat:session`) and shows no sign-in; the shell renews it
     silently (a new owner address in local mode; in team mode Archiwista's
     SPA starts the proxy session itself, today a button, `login.js:66-72`).
   - Trust (B4): front ports strip `X-Nogat-*`, `X-Admin-Key`, `X-API-Key` and
     the cookies of the hub and the other apps from every client request; apps
     listen on loopback only; the server is dedicated; variant B is steps 20
     to 22. Sign-out ends the hub's session and expires the apps' cookies of
     the host. CSRF and fetch metadata as in Archiwista; a front port forwards
     a state-changing request only with `Sec-Fetch-Site: same-origin`. An
     app's `frame-ancestors` names only the shell; the shell's is `'none'`.
   - Topology 1: `guihub up` reads `[guihub]`, starts the hub with the
     modules, Archiwista as a child process in its own environment and
     Hydrograf by `docker compose` on 127.0.0.1, waits for their health and
     stops what it started; `guihub doctor` checks Docker, memory and ports.
     Topology 2: one compose file (a hub image with the modules, Archiwista's
     image, Hydrograf's services), only the hub publishing ports; there
     Archiwista's 127.0.0.1 is not reachable through a published port
     [inference] and its team mode wants HTTPS from the proxy (question 5).
   - A catalog bridge `/api/<tool>/<group>/<verb>` (AGI-6.1, AGI-6.3) runs the
     modules' commands, with paths only in the person's work directory; store
     lines go to Archiwista (ECO-054).
5. **The embedded mode** (A1, A4). An app has one optional setting, the
   shell's origin (Archiwista `[nogat] shell_origin`, Hydrograf
   `NOGAT_SHELL_ORIGIN` into an nginx template): `frame-ancestors` names it,
   `X-Frame-Options` goes, Archiwista admits a frame navigation; unset, the
   headers stay as today. In a frame the page sends `nogat:hello` to that
   origin; the shell answers `nogat:welcome` (theme, language, a
   `MessageChannel` port) only to an app origin it configured, both checking
   `event.origin` and `event.source`. Welcomed, the app hides its top bar,
   rail and stage 1's app menu and exchanges `nogat:theme`, `handoff`,
   `navigate`, `signout`, `title` and `session`; otherwise it is the app
   alone. `?nogat=1` only hides the chrome at first paint (Hydrolog has it).
6. **The hand-off.** `schemas/exchange/handoff-1.schema.json` in Nogat,
   copied like the agent schemas (ECO-050): `schema` `nogat-handoff/1`,
   `created_at`, `producer` (tool, version, page to return to), `subject`,
   `provenance` (e.g. PMAXTP probability and duration), `payload`
   (`hydrolog-network/1` first: one subcatchment node with the values used)
   and an optional `result` for comparison. Embedded, `nogat:handoff` goes
   through the shell, which opens the target with it, the author's example in
   one click; alone, file and clipboard (stage 1). The hub keeps them in
   `<data_dir>/guihub/handoffs/`. The schema was approved on 2026-11-02
   ahead of the rest of this plan, as step N1 of
   [Hydrolog's GUI](2026-11-02-hydrolog-gui.md); the shell's part and the
   store of hand-offs wait for this plan.
7. **Hydrolog's GUI** exists ([Since 2026-11-01](#since-2026-11-01)): the
   hydrograph of one watershed, the network with the schematic, flow
   statistics, calculators and every command. Under the hub it runs as a
   hosted module called in process, through its `nogat.gui` entry point.
   Joining sub-catchments stays the control-point flow of ADR-0012, picked in
   Hydrograf.
8. **The command editor**, `<nogat-command-form>`, reads commands-1 entries:
   fields by type, a choice per `one_of` group, rules that enable fields, path
   options hidden where the app owns paths, the line live through
   `format_command`, a pasted line through `parse_command`, errors placed by
   `validate_command`'s `details.option`. Archiwista shows it as „Kreator
   polecenia” beside the paste field, feeding the same plan window; the hub
   shows every installed catalog. AGI-2.3 and commands-1 gain optional option
   fields `i18n.pl`, `requires`, `excludes`, `applies_to`, `section`, `format`.
9. **Obserwator** (B6): the module covers stations, series read from a local
   store, PMAXTP (a depth handed to Hydrolog's rainfall) and current data; the
   Jinja, HTMX and Pico pages go; store sync stays in Archiwista.

The first version is topology 1 with local and team mode (B2): steps 1 to 3
and 8 to 13 (step 9 without „Polecenia”, which needs steps 4 to 7), the
author's example on one machine with one sign-in.

## Steps

After stage 1. Producers before consumers (HUB-5.2): Nogat's contracts and
kit, then the producers' catalogs, then the hub, then the GUIs. Each step
runs in its repository's own session on a topic branch (DEV-3.4), with its
gate, ADR, CHANGELOG and PROGRESS. Sizes are estimates in sessions.

| # | Owner | Step | Size | Verified by |
|---|---|---|---|---|
| 1 | Nogat | The ECO decision; HUB-1.1, DEV-15.3 and the new rule of DEV §15; AGI-2.3 and the option fields of commands-1; the schema of the handshake messages (`handoff-1` done ahead, N1 of Hydrolog's GUI); the identity headers and the role vocabulary; the registry's `gui` field | 1 | gate: `validate`, `standard`, schema tests |
| 2 | Nogat | Kit, chrome: `tokens.css`, `base.css`, `shell.*` with the embedded switch, `theme.js`; the specimen rebuilt on it; browser tests | 1.5 | specimen in both themes, alone and in a frame |
| 3 | Nogat | Kit, parts: `info.js`, `form.js`, `chart-theme.js`, `embed.js`, `nogat:handoff` in `nogat-handoff.js`, `basemaps.json` | 1.5 | handshake tests across two origins |
| 4 | Kartograf | Export option `i18n.pl`, its constraints, `section` and `format` in `kartograf-commands/1` | 1-2 | commands-1 contract test; Archiwista's adapter tests unchanged |
| 5 | Obserwator | `commands list` and `commands schema` with `--json` in commands-1 shape, with option texts and dependencies; the JSON Schema stays the REST and MCP input schema | 1.5-2 | commands-1 contract test |
| 6 | Hydrolog | Public `parse_command` and `format_command` where still missing; the schematic document without an output file (its routing branches are merged since) | 0.5-1 | gate; every catalog example read back into the same call |
| 7 | Nogat | Kit: `<nogat-command-form>` and `<nogat-schematic>` | 1.5-2 | tests on the three catalogs and on `hydrolog.testing`'s example network |
| 8 | the author, Nogat | The hub's repository (`https://github.com/Daldek/<name>`, created by the author) from the standard's templates: `CLAUDE.md`, `AGENTS.md`, `docs/PROGRESS.md`, CI, a package skeleton; its entry in `ecosystem.yaml` (profile `app`, status `research`), its mark and accent pair in `design/`, the regenerated map and `AGENTS.md` | 1 | Nogat's gate (`validate`, the design contract test); the hub's gate green on an empty package |
| 9 | the hub | Both modes: local by A-ADR-012's rules, team by A-ADR-046 decisions 1 to 7 (TLS, accounts with roles, throttling, sessions, the action log, `guihub users`); the shell with frames and modules; „Pulpit”, the catalog bridge, the inbox, „Polecenia” | 5-6 | Archiwista's v0.4 checklist applied to the hub |
| 10 | the hub | Front ports and topology 1: identity and role headers per app, stripping of client headers and foreign cookies, streaming, silent renewal; `guihub up`, `guihub doctor`; the dedicated-server runbook; an evaluation of Unix sockets (B4) | 3-4 | a forged header or another app's cookie from the client never reaches an app; one sign-in reaches every app in both modes |
| 11 | Archiwista | Visual identity step 5 on the kit; the embedded mode; `[nogat] shell_origin` (frames, frame navigations); `proxy_roles_header` and the rules of item 4; the owner's one-time address on demand (`archiwista token` gives an agent's); silent renewal in a frame | 4-6 | e2e alone (local, team) and in the shell (local, team); a change of roles ends the session |
| 12 | Hydrolog | Its module under the hub: the hub's session and work directory instead of its own server's, the embedded switch of the kit | 1-2 | a sample hand-off opens with the same values and peak, alone and in the hub |
| 13 | Hydrograf | The kit's chrome; the embedded mode; `NOGAT_SHELL_ORIGIN` into an nginx template (headers on every location); CDN libraries vendored; „Wczytaj z Hydrologa” with the field mapping (the way to Hydrolog exists, ADR-068); the admin page without a key prompt behind the hub | 3-4 | e2e alone and in the shell; the same request after a round trip through Hydrolog |
| 14 | Obserwator | Hosted module (item 9); Jinja, HTMX and Pico removed | 2-3 | hub smoke; REST and MCP tests green |
| 15 | Archiwista | „Kreator polecenia” beside the paste field | 1.5-2 | form to line to plan window and back; BDOT10k without pasting |
| 16 | Hydrolog | Network workbench with the schematic and results per node | done by Hydrolog's own plan | – |
| 17 | Archiwista | Topology 2: an image, and serving behind the hub in a container in local mode (question 5) | 1.5-2 | e2e in a container, alone and behind the hub |
| 18 | the hub | Topology 2: one compose file (a hub image with the modules, Archiwista's image, Hydrograf's services), only the hub publishing ports | 2-3 | the package from one `docker compose up`; each app also alone |
| 19 | Hydrograf | Control points (outlet first) give `hydrolog-network/1` of residual sub-catchments; the schematic beside the map | own plan | its plan |
| 20 | the hub | Variant B: signed short-lived assertions (keys and their rotation; account, roles, audience, expiry) | own plan | before any trigger of B4 |
| 21 | Archiwista | Variant B: the assertion verified instead of the headers | own plan | with step 20 |
| 22 | Hydrograf | Variant B: the assertion verified before the admin routes, and before every page once apps leave the host | own plan | with step 20 |
| 23 | Nogat | The hub's entry and the `gui` fields active, map, PROGRESS, CHANGELOG; the hub in a release set (question 12) | 0.5 | gate |

Without steps 19 to 22, about 33 to 45 sessions; the first version (steps 1
to 3 and 8 to 13) about 21 to 27. Later, outside this plan: Retman filling
the editor from a Polish sentence (`retman plan run`), a Hydraulik module
taking `route network` tables, Hydrograf on MapLibre to share a map shell.

## Risks

| Risk | Effect | Mitigation |
|---|---|---|
| A new repository (C1) | one more project to keep on the standard: templates, CI, gate, releases, drift | built from the standard's templates in step 8; it holds only the host, the modules stay in the tools (question 1) |
| A working name (C1) | a rename after step 8 touches the repository, the package, the command, `[guihub]` and the registry entry | Nogat's contracts carry `nogat`, not the hub's name; the name is settled before step 8 (question 11) |
| The kit in Nogat, the host elsewhere (C2) | the hub needs a kit change and waits for a Nogat session | the kit's parts (steps 2, 3, 7) come before the hub; the hub proposes kit changes as `request` issues in Nogat (DEV-17.5) |
| Local and team mode together (B2) | a larger first version (about 21 to 27 sessions) | Archiwista's reviewed rules and test cases reused (G2); small steps |
| Kit copies drift | the shared look and fixes split again | `nogat-kit.json` hashes and stage 1's copy report; each app's contract test |
| One front door for all apps (team mode), a second implementation of Archiwista's sign-in | a defect in the hub's sign-in opens every app; the two drift apart | one checklist; the hub's tests replay Archiwista's cases; apps on loopback; no session, nothing forwarded |
| Identity and roles forged on the server (accepted, B4) | a process that reaches an app's loopback port acts as anyone with any role | a dedicated server (runbook); variant B before any trigger; Unix sockets evaluated |
| Cookies reach every port of the host (verified) | an app receives the hub's and the other apps' cookies | front ports strip them; `HttpOnly`; apps log no cookies; the hub ignores app cookies |
| Roles from the hub in Archiwista (B3) | an Archiwista moved under the hub loses its own role assignments | role assignment refused while `proxy_roles_header` is set; question 3 |
| Everything on one machine (A2) | Hydrograf's API (8 GB) and PostGIS (2 GB) beside Archiwista's previews | `guihub up` starts only the configured apps; `guihub doctor` checks memory |
| Hydrograf pins a Hydrolog commit (`1708a09` on 2026-11-03), the hub the release set | the same inputs give different numbers | the hand-off carries the producer's version and result; the module shows the difference |
| The work competes with the first release set and Archiwista's release | both slip | steps after those releases unless the author says otherwise (question 9) |

## Open questions for the author

1. Module code: in each tool's package (recommended, HUB-1.2), or in the hub?
2. Shared roles: `admin` and `store_writer` (recommended), or also a read-only one?
3. Archiwista team accounts moving under the hub: imported once, or started afresh?
4. Archiwista's groups and sharing under the hub: kept there (recommended), or sent?
5. Topology 2: a proxied local mode in Archiwista, or local TLS in the hub?
6. Hand-off: an envelope around `hydrolog-network/1` (C2) or a flat document;
   is Nogat its owner; do Archiwista projects keep hand-offs? The envelope
   and Nogat as its owner were approved with N1 on 2026-11-02; the last part
   is open.
7. Editor: every option, grouped, or basic and advanced views; Kartograf first?
8. Schematic: in Hydrograf (ADR-0013), in Hydrolog's module or both; and when
   does Hydrograf plan its control points?
9. The order against stage 1, the first release set and Archiwista's release
   (D2, D3).
10. Do steps 2, 3, 11, 13 and 14 replace steps 5 to 7 of the visual identity?
11. The hub's name, before step 8 creates its repository.
12. Does `nogat` install the hub, or does the hub install the tools it hosts?

## Results

- 2026-11-02, item 6 ahead of the rest (N1 of
  [Hydrolog's GUI](2026-11-02-hydrolog-gui.md)): `nogat-handoff/1` in
  [`schemas/exchange/handoff-1.schema.json`](../../schemas/exchange/handoff-1.schema.json)
  with the complete example of Hydrolog's plan (D15), contract-tested in
  `tests/contract/test_handoff_schema.py`; branch `feature/handoff-1`, not
  merged, not pushed.
