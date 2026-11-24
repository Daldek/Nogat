# Plan: Goniec, a QGIS plugin over Obserwator's server

Approved: pending

Status: a draft of 2026-11-24 from Obserwator's feedback #11 and the author's decisions and answers of 2026-11-24; not approved, so no code starts (DEV-17.4). The design marks its own proposals „[proposed]”. Branch `plan/qgis-plugin` (worktree `~/workspace/wt/nogat-qgis-plugin`), not merged into `develop` until the author decides (DEV-3.3).

Requirements: HUB-5.2, DEV-17.4, DEV-17.5 and DEV-3.4 (each project in its own session and branch), DEV §1 and HUB §2 (profiles, registry), DEV-16.1 and DEV-13.5 (licences), DEV §20 and DEV-15.7 (lines, regulamin), DEV-15.9 and DEV-15.10 (limits, logs), DEV-19.21 (file names), AGI-4.1 and ECO-085 (additive `/1`). Obserwator ADR-002 (REST from the command catalog), ADR-025 (the instance filter), ADR-030 D5 (publication state).

## The source

Obserwator's feedback #11 (2026-11-23): „Obserwator jako wtyczka QGIS. Serwuje lokalizacje stacji, rodzaj, aktualne pomiary i dane historyczne, tak samo jak wersja webowa. Analizy można na razie całkowicie lub częściowo wyłączyć. Może zrobić to jako WFS?”

## Decisions of the author (2026-11-24, as relayed to this plan)

1. The plugin only connects to a server, the source of all data: no computation and nothing to download on the user's side; it is just another interface.
2. The user can change the server's address, e.g. to his own local Obserwator.
3. OGC API – Features; WFS only as a possible extension when needed, but the design must be ready for it.
4. `/api/v1` public, read-only, with limits.
5. QGIS: the latest 3.x LTR (3.44) supported, the focus on 4.x.
6. First scope: stations, current data and series in a panel, with copying values and saving CSV.
7. A user's requirement: copying water levels and discharges, and their combinations, in a form HEC-RAS or HEC-HMS accepts.
8. Answers of the same day: the plugin is „Goniec” (repository `Goniec`, QGIS folder `goniec`; „Pegaz” was the alternative, not chosen), licensed GPL-2.0-or-later; Obserwator stays MIT.

## Facts (checked on 2026-11-24)

### Obserwator (`develop` `b5a1c1a`, `3.3.0.dev0`)

- `uv run -q obserwator commands list --json` lists 37 commands, 34 with a route `/api/v1/<group>/<name>` (ADR-002; `src/obserwator/api/routes/commands.py:4`): GET among them `stations find|export`, `current hydro|meteo|synop|warnings|hydro-states`, `series select|read|summary|export`, `analyses list|read|export`, `commands list|schema`; POST `store sync|catalog|import`, `series build`, `analyses build`, `pmaxtp sync`.
- `stations find`, the five `current` commands, `pmaxtp fetch` and `store check` (a GET) call a provider on every request (`network: true`); the REST server keeps no snapshot of current data. The exports answer as attachments, a Parquet one written to a private directory and removed after the answer, and server and local options in a request are refused (`commands.py:11-14`, `:29`). Writes need `OBSERWATOR_STORE_WRITES_ENABLED`, the token and `X-API-Key`, POST `?check=true` none (`:29-32`); lists page by `limit` and `cursor` (`:33-34`); errors are `application/problem+json` (`api/errors.py:4`); `/health` reports the version (`api/main.py:280`).
- The REST server sets no `ETag` or `Cache-Control` and limits no address; `rate_limit` (`config.py:174-175`) belongs to the deprecated `admin keys` and limits nothing. The GUI server limits each address (`request_limit` 300 in `request_window` 60 s, `config.py:226-231`, DEV-15.9), answers with a strong ETag of what an answer was made from, the server's run included, and `Cache-Control: no-cache` (`gui/_http.py:32`, `:119-150`; `gui/_app.py:384-386`), and asks each source of current data at most once per 600 s (`gui/_live.py:64`).
- ADR-025 D3: „`obserwator server` loads the same section at start … and guards every catalog route before the call … The CLI and MCP never apply the section.” (`docs/DECISIONS.md:1080`); a private capture is never served (ADR-030 D5, `commands.py:38-40`).
- H in cm, Q in m³/s (`datasets.py:615`), times in UTC and points in WGS84 (`gui/web/instrukcja/index.html:1059`). IMGW-PIB's gauge zero and its datum come from hydro.imgw.pl's station pages (`providers/pl/imgw.py:813-838`; the GUI's guide: „stan 250 cm przy zerze 281,617 m to lustro wody na 284,117 m n.p.m.”, `instrukcja/index.html:1038`); ČHMÚ's gauges have none (`providers/cz/chmu.py:608`). Daily H and Q are „Water level of the day (COSTAN)” and „Discharge of the day (COPRZP)” (`messages/datasets.py:327-336`): whether instantaneous or a mean is not recorded.
- The analysis `rating_curve` (`store/analysis_registry.py:675-698`, Hydrolog's `hydrometrics rating-curve`) fits Q = a·(H − H₀)^b to the same-day daily pairs of chosen years (`instrukcja/index.html:379`); „Pary dobowe to nie pomiary hydrometryczne” (`:390`).
- A CSV of a series or of stations ends with the columns `attribution` and `terms_notice` (`store/export.py:90-93`, `:206-210`; DEV-20.5). No dependency reprojects (`pyproject.toml`). Licence MIT (`pyproject.toml:10`). Tags `v3.0.0` to `v3.2.0`; `v3.3.0` is next, `v3.4.0` is CAMELS-PL's (ECO-086), the rest `v3.5.0` at the earliest (`2026-11-16-operational-series.md`, E6).

### The public instance

`obserwator-test.debever.pl`, 2026-11-24 10:10 CET: `/api/v1`, `/api/v1/commands/list` and `/api/v1/stations/find` answer 404 with the GUI server's `obserwator-error/1` („Nic tu nie ma: /api/v1/commands/list”): only `gui serve` answers. `api/session` reports Obserwator `3.1.0` and `instance: null`. `api/stations` is 141 kB gzipped, `Cache-Control: no-cache`, `cf-cache-status: DYNAMIC`; with gzip accepted the strong ETag passes and `If-None-Match` gets 304, without it Cloudflare decompresses, weakens the ETag to `W/"…"` and the same request gets 200.

### QGIS and its plugin repository

- Roadmap (qgis.org): 4.4.0, an LTR, released 2026-11-20 (tag `final-4_4_0`); 3.44 stays in the long-term repository until 4.6.0 (2027-03-26), its last point release 3.44.19 on 2027-02-12.
- plugins.qgis.org (`/docs/publish`, `/docs/approval`, `/docs/migrate-qgis4`): a licence compatible with GPLv2 or later; „Don't include binaries”, „Plugins that utilize binaries will not be approved”; at most 25 MB; Windows, Linux and macOS; `QgsNetworkAccessManager` instead of urllib or requests; homepage, tracker and a public repository in `metadata.txt`; QGIS 4 through `qgisMaximumVersion=4.99`, `supportsQt6` no longer recognised, the `qgis.PyQt` shim; a security scan of every upload. The QGIS blog, 2016-05-29 (https://blog.qgis.org/2016/05/29/licensing-requirements-for-qgis-plugins/): plugins distributed via plugins.qgis.org „(or through other repositories that may be self-hosted) should comply with the GPL version 2 or greater license”.
- The OAPIF provider reads the conformance classes of Part 2 (`crs`, `bbox-crs`, `storageCrs`), Part 3 (CQL2 text) and Part 5 (schemas), and on 4.4 JSON-FG (`src/providers/wfs/oapif/qgsoapifprovider.cpp:176-185` on `release-3_44`, `:184-201` on `release-4_4`); a collection's `description` becomes the layer's abstract and its `license` or `rel="license"` links the layer's licences (`qgsoapifcollection.cpp:92-98`, `:239-276` on `release-3_44`).
- `QgsNetworkAccessManager` keeps a `QgsNetworkDiskCache` in the user's cache directory (`src/core/network/qgsnetworkaccessmanager.cpp:827-842` on `release-3_44`); WFS and OAPIF requests use `PreferCache` unless refreshed (`src/providers/wfs/qgsbasenetworkrequest.cpp:227` on `release-3_44`, `:216` on `release-4_4`). Qt: `PreferCache` „can return possibly stale (but not expired) items from cache”; `PreferNetwork`, the default, „will never return stale data from the cache, but revalidate resources that have become stale”. The auth manager has an API-header method (`src/auth/apiheader/core/qgsauthapiheadermethod.cpp`).

### HEC

- HEC-RAS 6.6 manual, „Boundary Conditions” (https://www.hec.usace.army.mil/confluence/rasdocs/rasum/6.6/performing-a-1d-unsteady-flow-analysis/entering-and-editing-unsteady-flow-data/boundary-conditions): a flow or stage hydrograph is read from HEC-DSS or typed into a table after a „Data time interval” („Currently the program only supports regular interval time series data”) and „Use Simulation Time” or „Fixed Start Time”; „Stage and Flow Hydrograph” uses the stage until it runs out, then the flow, „The end of the stage data is identified by the HEC-DSS missing data code of "-901.0"”; „Rating Curve”, downstream, is „a single valued relationship”; in a table „the end of data is a blank line. Do _not_ enter -901 in the table”.
- HEC-HMS 4.14 manual, „Time-Series Data” (https://www.hec.usace.army.mil/confluence/hmsdocs/hmsum/latest/shared-component-data/time-series-data): manual entry takes the clipboard („The table includes support for the clipboard”); a missing value „should be left blank”; intervals of 1 minute to 1 day; dates `02Oct1955`, times `18:20`, „an arbitrary local time zone that does not observe summer time”; manual Discharge and Stage are INST-VAL, „an instantaneous measurement at the end of each time interval”; in HEC-DSS, Discharge is `FLOW` in `M3/S` (PER-AVER or INST-VAL) and Stage `STAGE` in `M`, an elevation, under „a very strict set of rules for data type and units”; a pathname has six parts, up to 256 characters.
- Both read HEC-DSS natively. HEC's `hecdss` (PyPI 0.1.33 of 2026-08-28, MIT) wraps the native library through ctypes; its wheel carries `hecdss.dll` and `libhecdss.so` only, no macOS library, and writes DSS 7 only.

### Cloudflare

- „The Cloudflare CDN does not cache HTML or JSON by default” (developers.cloudflare.com/cache/concepts/default-cache-behavior); a strong ETag survives only when the visitor accepts the origin's compression, and „Respect Strong ETags” is a cache-rule setting (`/cache/reference/etag-headers`).
- Rate-limiting rules (`/waf/rate-limiting-rules`): Free 1 rule, counting and mitigation 10 s, by IP; Pro 2 rules, up to 1 min; Business 5, up to 10 min.

### Nogat (`develop` `813c6ed`)

- Profiles `tool`, `app` and `hub` only (`standards/DEVELOPMENT_STANDARDS.md:16-20`, the schema's enum); a project requires `distribution` {`pypi`, `import_name`} and `interfaces` {`cli`, `mcp`, `rest`, `python`} (`schemas/ecosystem.schema.json`) and routes starting with its CLI or an HTTP method (HUB-2.9, `standards/ECOSYSTEM_HUB.md:105-110`): a QGIS plugin has none of them. DEV-5.1 puts a `tool`'s code in `src/<package>/` (`:156`).
- DEV-16.1: „Licence: MIT unless an ADR states otherwise.” (`:727`); DEV-13.5: dependencies compatible with the project's licence and the distribution channel (`:470-472`).
- DEV-20.5 (`:1137-1152`) puts the lines on every surface: CSV trailing columns, a ZIP's `ATTRIBUTION.txt`, an API's `attribution` and `terms_notice`, model inputs „a header comment of the file, or `ATTRIBUTION.txt` beside it where the format has no comments”; it has no row for a clipboard or a desktop GIS layer. DEV §15 is the profile `app`'s (web GUIs). The highest ECO is ECO-087 (`standards/DECISIONS.md:2330`).

## Design [proposed]

### Goniec: a shell and modules

Goniec is a shell plus one module per kind of server. The shell holds what every module shares: server connections and their authentication, attribution and regulamin, HTTP caching, settings, the CSV, clipboard and HEC exports, and the panel framework. A module is shown only when the connected server advertises it: at connection the shell reads the server's version and capabilities (S4), and QGIS reads the OGC conformance for the layers. Goniec 0.1 has only the Obserwator module.

### The server: Obserwator

S1. **OGC API – Features** at `/ogcapi/` of `obserwator server`: landing page, `conformance`, `api` (OpenAPI 3.0), `collections`, `collections/{id}/items`, `items/{featureId}`.
- Conformance: Part 1 Core, GeoJSON and OpenAPI 3.0, in CRS84; QGIS reprojects the points itself. Part 2 (EPSG:2180) only when a client needs it, with a reprojecting dependency; Part 3 filters later.
- Collections: `stations-<provider>`, one per served provider, a point per station with the catalog's properties (the code as `featureId`, name, kind, river, hydrographic code, river km, catchment area, gauge zero and its datum, the datasets with series); `latest-<provider>-<kind>`, one per provider and kind with current data, the station's point with its last readings (time in UTC, value and unit per variable, tier, time of the server's snapshot).
- Paging by `limit` (default 1,000, maximum 10,000, so one page holds a provider's stations) and `next` links with `numberMatched`; `bbox`. The instance filter applies (ADR-025 D3): only served providers have collections, clipped stations are absent, a private capture has none (ADR-030 D5).
- Each collection's `description` carries its provider's lines and its `rel="license"` links the terms, so QGIS fills the layer's abstract and licences even without Goniec; each `items` answer carries `attribution` and `terms_notice` beside `features` (DEV-20.5).
- Ready for WFS: one feature source per collection, flat properties (lists as text, no nested objects), stable collection and feature ids, so a WFS 2.0 endpoint can later serve the same collections as feature types.

S2. **`/api/v1` public and read-only** under a setting of the REST server, `api_public`: every POST, `?check=true` included, is `forbidden`; the routes that call a provider per request (`stations find`, `pmaxtp fetch`, `store check`) are refused, the station collections and `stations export` serve the catalog; `current` answers from a snapshot of at most 600 s, the GUI's code (`gui/_live.py`) shared by both servers; each address is limited as DEV-15.9 (`request_limit`, `request_window`; 429, `Retry-After`, `rate_limited`) and `limit` capped; logs keep no address (DEV-15.10); CORS stays closed (Goniec is no browser). The public host routes `/api/v1/*`, `/ogcapi/*` and `/health` to `obserwator server`, the rest to `gui serve`.

S3. **Caching by resource class.** Strong, quoted ETags; `Vary: Accept-Encoding, Accept-Language`; `public` only with `api_public`, else `private`.

| Class | Answers | ETag from | Cache-Control |
|---|---|---|---|
| Catalog | `stations-*`, `stations export`, `datasets list`, landing page, `collections` | catalog versions (`2026-11-22_4808b177`), instance key, API version | `max-age=86400` |
| Versioned series | `series read`, `export`, `hec` naming a store version | version and query | `max-age=31536000, immutable` |
| Current series | the same without a version | version and query | `max-age=3600` |
| Current data | `latest-*`, `current *` | the snapshot's serial | `max-age` = the snapshot's remaining life, ≤ 600 |
| Errors, refusals, 429 | all | none | `no-store` |

Goniec reads a series by the version `series select` names, so what it reads once never changes.

S4. **Version and capabilities.** `GET /api/v1/server` answers `nogat-server/1`, a schema in Nogat's `schemas/exchange/` (additive within `/1`, AGI-4.1): `tool`, `version`, `api` (`{"/api/v1": 1}`), `capabilities` (`stations`, `current`, `series`, `hec-table`, `hec-dss`, `analyses`, each only when served), `ogcapi` (the landing page), `instance` (title, featured provider), `terms` (the regulamin's address and version), and the served providers' `attribution` and `terms_notice`. `/api/v1` changes only additively (ECO-085); a breaking change is `/api/v2`, served beside v1 for at least one minor.

S5. **HEC export on the server**, a catalog command `series hec` (CLI, REST, MCP and Python; ADR-002): station, dataset, version, period, `variables` (`Q`, `H` or `H,Q`), `program` (`ras`, `hms`), `form` (`table`, `dss`), `stage` (`gauge`: m above the gauge zero; `elevation`: m in the zero's datum, only where the catalog has one) and `tz` (`UTC`, or `UTC+01:00` without summer time). The server converts and checks; Goniec only copies or saves the answer.
- `table`: tab-separated values in SI with a decimal point, the series' own regular interval, no header; the envelope gives the start, interval, count, units and HEC type the panel shows for HEC's editor. HEC-RAS: Flow, Stage, or Stage and Flow (two columns); a gap inside the period refuses the table, naming the first missing time, since a blank line ends HEC-RAS's data and -901 is DSS's. HEC-HMS: one column, Discharge or Stage, a gap an empty line, the time window as `02Oct1955 18:20`.
- Rating curve for HEC-RAS: stage–discharge pairs tabulated from the `rating_curve` analysis of the chosen years, single-valued and sorted by stage, only where the server serves analyses; never the raw daily pairs.
- `dss`: one DSS 7 file in a ZIP with `ATTRIBUTION.txt` (DEV-20.5: ZIP, model inputs), written with `hecdss` as the optional extra `obserwator[hec]` (Linux and Windows, as its wheel's libraries; without it `hec-dss` is not advertised); pathname `/<river>/<code> <name in ASCII>/FLOW|STAGE/<block start>/1DAY|1HOUR|10MIN/OBSERWATOR <version>/`. Goniec writes no DSS: that needs HEC's native library, which a plugin may not carry.

S6. **The edge** (the author's instance): a cache rule making GET `/ogcapi/*` and `/api/v1/*` eligible, the origin's `Cache-Control` respected, „Respect Strong ETags” on, the whole query in the cache key; a rate-limiting rule per IP on the same paths, within the zone's plan; Access in front of `/admin` as today.

### Goniec

G1. **Connections.** The author's public instance by default; any other address, e.g. one's own `obserwator server` on 127.0.0.1. A connection is a name, an address and an `authcfg` of QGIS's auth manager (Basic, OAuth2, or an API header such as a Cloudflare Access service token) for an operator's private instance; Goniec stores no secret. At connection it reads `nogat-server/1`: an unknown `tool` or an API major it does not speak is refused with both versions named, and a capability the server lacks hides its part of the panel.

G2. **Network and cache.** Every request goes through `QgsNetworkAccessManager` (proxy, auth, disk cache) with `PreferNetwork`: the disk cache serves what is fresh and revalidates the rest by ETag (304, no body). The map layers are QGIS's own OAPIF layers of the server's collections, so a project stays portable and anyone can add them through „WFS / OGC API – Features” without Goniec. Per server and catalog version Goniec keeps the station collections as served (GeoJSON, unprocessed) in its cache directory, for the panel's search and list and for the last known stations, marked as such, when the server cannot be reached; a new catalog version replaces them.

G3. **The panel, 0.1** (the Obserwator module): stations (search by name, code or river; a click on the map), the station's description, current readings, a series (dataset, variables, period) as a table; „Kopiuj” (the values shown, tab-separated); „Zapisz CSV” (the bytes of `series export` under the server's file name, DEV-19.21); „Kopiuj do HEC-RAS” and „Kopiuj do HEC-HMS” with the editor settings shown beside them; „Zapisz HEC-DSS” where the server has `hec-dss`. Analyses off (feedback #11) except the rating-curve table under `analyses`; a chart is a later minor.

G4. **Attribution and regulamin.** At the first connection to a server, before any data request: the server's title, its providers' lines and a link to its regulamin, confirmed once per server and regulamin version. Each layer carries the lines in its metadata (abstract and licences from the collection, rights and attribution set by Goniec). The panel shows a strip with the lines of what it shows, „Źródła i warunki” and „Regulamin”. Saved files are the server's bytes with their lines. The clipboard holds values only, since a paste target takes nothing else; the lines stay beside the buttons and in every saved file (a DEV-20.5 row, N1).

G5. **Versions and packaging.** `qgisMinimumVersion=3.44`, `qgisMaximumVersion=4.99`, Qt only through `qgis.PyQt`, tested on 3.44 and 4.4 on Linux and Windows; a minor after 4.6.0 (2027-03-26) may drop 3.44. No third-party runtime dependency and no binary. Polish UI through Qt translations, English code and docs (DEV-2.1, DEV-2.2), an English description for plugins.qgis.org. GPL-2.0-or-later; uv for development tools only; released as a ZIP of `goniec/` to plugins.qgis.org, 0.x marked experimental.

### Nogat

An ECO decision records Goniec: its name, its licence as DEV-16.1's exception (QGIS's requirement), the shell and its modules; a profile `plugin` in DEV §1 (code in `<folder>/` at the root, uv for development only, no PyPI, CLI, MCP, REST or command catalog, no routes, distribution through plugins.qgis.org); the schema's profile `plugin` and `distribution.qgis`; DEV-20.5 rows for a clipboard copy and a desktop GIS layer; the regulamin's kit text naming the API and Goniec among a service's interfaces; `nogat-server/1`; Goniec's mark in `design/marks/`. Registry: `Goniec` (`profiles: [plugin]`, `status: research` until 0.1, `depends_on` Obserwator, `runtime` via `rest`, exchanges `nogat-server/1`, `obserwator-ogcapi`, `obserwator-series-csv`, `obserwator-hec`); Obserwator `provides` `obserwator-ogcapi` (service) and `obserwator-hec` (document).

## Steps (producers first)

| # | Project, release | Change | Verified by |
|---|---|---|---|
| N1 | Nogat, the next standard minor | the ECO decision, the profile `plugin`, the schema and registry entries, the DEV-20.5 rows, the regulamin's kit text, `nogat-server/1`, Goniec's mark; PROGRESS | Nogat's gate |
| O1 | Obserwator, a minor after `v3.4.0` (`v3.5.0` at the earliest) | an ADR and S1 to S5: `/ogcapi/`, `api_public`, the caching headers, `/api/v1/server`, `series hec` and the extra `hec`; contract tests; USAGE | OGC's Part 1 test suite (`ets-ogcapi-features10`); each route of S2 refused or limited as listed; each HEC form pasted by the author into HEC-RAS 6.6 and HEC-HMS 4.14, a DSS file opened in HEC-DSSVue |
| D1 | The author's public instance | `obserwator server` beside `gui serve`, the routes and edge rules of S6 | `curl`: conformance, a 304, `cf-cache-status: HIT` on a repeated request, 429 over the limit, 403 for a POST |
| G1 | Goniec `0.1.0`, a new repository | the shell and the Obserwator module (G1 to G5), uploaded to plugins.qgis.org | QGIS 3.44 and 4.4: connection, layers, panel, copy and save; a pasted HEC table; a saved CSV equal to the server's bytes; the repository's checks |
| N2 | Nogat | `Goniec` `status: active`, drift, PROGRESS | Nogat's gate |

Each step in its own session and branch (DEV-3.4, DEV-17.5); nothing starts before this plan's `Approved:` line.

## Later modules

- Hydrograf: an instance's catchments and network as collections, its hydrographs and hyetographs in HEC-HMS forms.
- Archiwista: a project's area, sets and files.

## Open questions

1. IMGW-PIB's daily H and Q: instantaneous (INST-VAL, stamped at the observation time) or daily means (PER-AVER, stamped at the end of the day, 24:00)? Obserwator records neither (Facts); HEC's type, the time stamps of the forms and the DSS records depend on it.
2. The HEC forms' default time zone: UTC, as Obserwator, or UTC+01:00, Poland's standard time without summer time?
3. The rating-curve table in 0.1, while analyses may stay off?
4. Obserwator's minor: `v3.5.0` beside the interval-estimation draft's O1, or the next?
5. The zone's Cloudflare plan: Free gives one rate-limiting rule of 10 s.

## Results

None yet.
