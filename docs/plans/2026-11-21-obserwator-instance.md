# Plan: Obserwator deployed for an operator with its own network

Approved: pending

Status: a draft of 2026-11-21 from the author's direction of the same day; not approved, so no code starts (DEV-17.4). The design marks its own proposals „[proposed]”.

Requirements: DEV-17.4, DEV-18.1 to DEV-18.4, DEV-12.4 to DEV-12.9, DEV-13, DEV-15.4, DEV-15.7, DEV-15.8, DEV §20, HUB-5.2. Related plans: `2026-11-20-hydromet-providers.md` (branch `plan/hydromet-providers`, P1 to P13), `2026-11-17-install-contract.md` (branch `plan/install-contract`, rules 1 to 13).

Releases [proposed]: steps 1 to 5 are Obserwator `v3.1.0`, beside its scope decided on 2026-11-14 to 2026-11-20; step 6, the operator's own network, joins `v3.2.0` with the provider adapters of `hydromet-providers`. Nothing is tagged before the whole round ends (the author, 2026-11-21).

## The author's direction (2026-11-21)

- A potential client wants Obserwator on his own infrastructure and has his own measurement network.
- The GUI must let one provider's data stand out and make it easy to control the visibility and the availability of the other sources; a view limited to a chosen area, or a start zoomed to the chosen provider's stations instead of the whole data set, is wanted.
- Obserwator stays the single source of code: clients update it through git. A deployment's choices live in separate files (environment or configuration), never in code.
- Security, running on someone else's infrastructure, portability, data security and sign-in security are of the highest importance.
- For now the clients' data are public and the client wants a better interface of his own. If data become private and must be closed, the whole instance goes behind SSO or Cloudflare Access; Obserwator gets no accounts.

## What exists (2026-11-21, Obserwator `develop` `73574bb`)

| Topic | Today |
|---|---|
| Deployment settings | `nogat.toml` (through `NOGAT_CONFIG`) with `[obserwator]`, `[nogat.gui]` (app-menu addresses, DEV-15.4) and `[nogat.operator]` (the operator of a public instance, its regulamin); `OBSERWATOR_*` variables and `.env`; credentials from the environment or a `*_FILE` only (`_environment.py:41`, DEV-18.4). |
| Basemap | `OBSERWATOR_GUI_BASEMAP_URL`: any TileJSON of one origin (a self-hosted one included), or `none` for the packaged borders only, offline (ADR-018). |
| Providers | `ProviderDescriptor` `IMGW-PIB` and `CHMI` in `datasets.py`; attribution origins in `attribution.py`. |
| Station layer | `api/stations` always returns every station of every current catalog (1.63 MB); the provider, kind and dataset filters run in the browser (`gui/web/src/list.js`), so a hidden source is still served. |
| Start view | The extent of the whole data set; no area, no featured provider. |
| Outbound calls of the GUI server | IMGW-PIB's current data (hydro-back.imgw.pl and danepubliczne.imgw.pl), PMAXTP answers; the page itself reaches only its origin and the basemap's. |
| Admin | `/admin/` with `X-Admin-Key` (`OBSERWATOR_ADMIN_API_KEY[_FILE]`, compared in constant time, `gui/_admin.py:145`); Cloudflare Access in front at the author's instance. |
| REST writes | One token, `OBSERWATOR_STORE_WRITE_TOKEN`, header `X-API-Key`, constant time (`api/routes/commands.py:378`). The keys of `obserwator admin keys` (`api_keys.json`, plain text) are checked by nothing. |
| CORS of the REST server | `allow_origins=["*"]` with `allow_credentials=True` (`api/main.py:193`); being fixed on `fix/3.1.0-findings` (a setting, closed by default). |
| Regulamin | Kit 1.0.0, regulamin 1.0: § 1 and § 3 call the service free and non-commercial and use IMGW-PIB's data for non-profit purposes. |

A precedent for an area: Archiwista's project area is one WGS84 polygon in a GeoJSON file, enforced where it indexes (A-ADR-049, decision 4).

## Goal

1. One file section describes an instance: which providers it serves, which one it features, its area and its start view, its title. The same code serves the author's public instance and every client's.
2. What an instance does not serve is filtered on the server, at one place, for every route: never only hidden in the browser.
3. An instance starts only from a valid description (fail closed) and reports it in `config show` and `api/session`.
4. A client can run, move, back up and update an instance on his own infrastructure from a git tag, with a written threat model and no secret in any tracked file.
5. In `v3.2.0`, the client's own network enters as data, not as code: a file-fed provider (step 6).

## Design decisions [proposed]

| ID | Decision |
|---|---|
| I1 | **The instance section.** `[obserwator.instance]` in `nogat.toml`, read at start (DEV-18.1); no credential in it (DEV-18.4). Fields: `title` (the page title and the header, optional), `featured_provider` (a provider id, optional), `start_view` (`all`, the default, `featured` or `area`), `area` (a path to a GeoJSON file, optional), `area_mode` (`focus`, the default, or `clip`), and the table `[obserwator.instance.providers]` mapping a provider id to `visible` (the default for every provider), `hidden` or `off`. Without the section an instance behaves exactly as today. |
| I2 | **Three provider states.** `visible`: served and shown. `hidden`: served, but off in the GUI's default filters; a person turns it on. `off`: not served at all, so absent from the station layer, series, analyses, exports, hand-offs, current data, the attribution strip, the „Źródła i warunki” dialog and the regulamin's source blocks, and the server makes no request to that provider. The featured provider cannot be `off`. |
| I3 | **One filter on the server.** The data root's snapshot (`gui/_root.py`) is reduced once, after each read, to the instance's providers and, with `area_mode = "clip"`, to the stations inside the area; every route reads that reduced snapshot, so the station layer, its ETag and every station route agree. A station outside the instance answers `not_found` (no leak through a guessed code). The REST server (`obserwator server`) applies the same section; the CLI and MCP, local tools, do not. |
| I4 | **The area.** One Polygon or MultiPolygon in WGS84 (RFC 7946), at most 1 MB and 100,000 vertices, read once at start. `focus`: nothing is removed; the outline is drawn and the map starts on it. `clip`: stations outside are removed by I3, and the map's bounds are the area's box with a margin. No buffer: the operator draws the polygon he means. |
| I5 | **The start view.** `featured`: the box of the featured provider's stations after I3, with a margin; `area`: the area's box; `all`: today's. A start view with nothing in it falls back to `all` and logs a warning. |
| I6 | **The featured provider stands out.** Its stations are drawn above the others at full strength; the others are drawn smaller and faded while „Pokaż inne źródła” is off, its default on an instance with a featured provider. The left panel lists the featured provider first, above the class headings of `hydromet-providers` P12, so the two designs fit; its attribution line comes first in the strip. Without a featured provider the GUI is today's. |
| I7 | **Fail closed.** An unknown provider id, a featured provider that is `off`, an area file that is missing, too large, not a polygon or not in WGS84 range, or an unknown field is `validation_error` (exit 2) at start, with `details.option` naming the field; the server does not start. `config show --json` reports the resolved section; `api/session` reports what the page needs (featured provider, start box, area outline in `focus`/`clip`, title), never a path. |
| I8 | **Outbound requests follow the states.** Each source the server contacts is listed in USAGE with the setting that turns it off: IMGW-PIB's current data and PMAXTP follow `IMGW-PIB` (`off` makes no request), the basemap follows `OBSERWATOR_GUI_BASEMAP_URL` (a self-hosted TileJSON or `none`). |
| I9 | **No accounts.** Obserwator gets no sign-in and no roles. A private instance runs entirely behind the operator's SSO or Cloudflare Access at the edge (`install-contract` rule 12); the admin panel keeps its key and, on every instance, a rule of the edge in front of `/admin`, `/admin/*` and `/api/admin/*`. |
| I10 | **Secrets and files.** Credentials only as `OBSERWATOR_*_FILE` (or the variable), files of mode 0600 owned by the service user; `.env`, `*.key` and `api_keys.json` are ignored by git; the admin key and the write token must be at least 32 bytes, or the server refuses to start. A deployment's own files (`nogat.toml`, the area, the secrets) live outside the checkout, under `/config` in a container (`install-contract` rule 4). |
| I11 | **Threat model.** `docs/SECURITY.md` gains a threat model of an instance on foreign infrastructure: assets (the data roots, the secrets, the feedback reports, the logs), entry points (the GUI's private API, the REST API, the admin panel, the outbound fetches), the trust in the reverse proxy (one variable of trusted proxies), what the operator must provide (TLS at the edge, the edge's rules, backups, updates in the maintenance window) and what Obserwator guarantees. |
| I12 | **Update and move.** A client pins a tag (`uv tool install "obserwator[gui,api] @ git+…@vX.Y.Z"` or the image of `install-contract` S4), never a branch. At start the server checks that the data root's layout version is one it reads and refuses otherwise with a hint; moving an instance is copying its two roots (`rsync -aH`, DEV-18.5), its `state_dir` and its `/config`. USAGE gets one section „Deploying an instance for an operator”; the Polish runbooks of a client live in the private deployment repository (`install-contract` S5). |
| I13 | **The operator's own network (`v3.2.0`).** A provider fed by files, not a client's module: a station catalog (GeoJSON of the documented fields) and series in `obserwator-series-csv` or Parquet, imported by one command into the stores, with the provider's id, name, country, source class (`other` by `hydromet-providers` P11, unless the author decides otherwise for a service), licence and attribution line declared in a provider file beside `nogat.toml`. It is one adapter of P1, so no `if provider == …` appears; adding a client is configuration and data. |

## Steps (producers first)

1. **Nogat:** this plan; `ecosystem.yaml` notes the instance section in Obserwator's interfaces; PROGRESS.
2. **Obserwator, ADR „instance”** (I1, I2, I7, I10): settings, validation, `config show`, `.env.example`, messages pl/en, the length checks of the secrets, `.gitignore`.
3. **Obserwator, the server's filter** (I3, I4, I8): the reduced snapshot, the REST server, the outbound switches; tests that an `off` provider and a clipped station are absent from every route and that no request leaves for an `off` provider.
4. **Obserwator, the GUI** (I4 to I6): start view, featured drawing, „Pokaż inne źródła”, the area's outline and bounds, the title; the attribution strip and the regulamin's source blocks of the served providers only; browser tests of each state.
5. **Obserwator, documents** (I11, I12): `SECURITY.md`, USAGE „Deploying an instance for an operator”, the layout-version check; a demonstration instance on this machine (a featured provider and an area, `clip`), smoke-checked on 127.0.0.1.
6. **Obserwator `v3.2.0`, the file-fed provider** (I13), with the adapters of `hydromet-providers` steps 2 and 3.
7. **Nogat:** registry drift, the release set of the round, PROGRESS.

## Open questions

1. **Commercial use and the regulamin.** Regulamin 1.0 says the service is free, non-commercial and uses IMGW-PIB's data for non-profit purposes (§ 1, § 3), and only the author raises its version. A client's instance may be commercial: it needs either a regulamin variant for operators other than the author, or IMGW-PIB `off` on such an instance; and `2026-11-14-independence-from-imgw.md` records the author's decision to ask IMGW-PIB in writing before any commercial start.
2. **The client's name and mark.** May an instance carry the client's title (and logo) beside Nogat's marks (DEV §15), or only a title? The draft has a title only.
3. **PMAXTP** follows `IMGW-PIB` in I8; or a switch of its own?
4. **The REST server** applies the instance section (I3); or only the GUI?
5. **The source class of a client's network** (I13): `other` by default; may the author declare a client a service?
6. **The keys of `obserwator admin keys`** (I10): remove the unused command and keep the one write token, or make per-client REST keys real (hashed, constant time, per-key limits)?

## Results

None yet.
