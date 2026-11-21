# Plan: one way of naming the files a tool hands to a user

Approved: 2026-11-21, the author (in session: „Jeszcze jedna rzecz do ujednolicenia - nazwy pobieranych plikow”, then the choices „Cały ekosystem w tej rundzie”, „Angielskie”, „Tak, z nazwą narzędzia na początku” out of: the whole ecosystem in this round, the rule now and Obserwator now, Obserwator only; Polish or English words; with or without the tool's name)

Status: approved; step 1 (Nogat) done on 2026-11-21 on `feat/download-file-names` (DEV-19.21, ECO-083), not yet merged; steps 2 to 5 to do.

Requirements: DEV §19 (files a tool writes), DEV-15.5 (hand-off file), DEV-15.11 (statistics file), ECO-082 (identifiers by national acronyms). Raised by the author's test of Obserwator's station list on 2026-11-21.

## The state on 2026-11-21

Each tool names its files its own way: Obserwator `stations_imgw-pib_meteo.csv`, `252170380_meteo_precip_daily.csv` (ČHMÚ `…_chmi_meteo_daily.csv`), `252170380_analyses.csv`, `pmaxtp_POT_52.4142_17.4586.csv`; Hydrograf `hietogram_<…>.csv`, `punkty_PMAXTP_<…>.geojson`; Hydrolog `<…>-wezly.csv`; Archiwista `porownanie-<…>.csv`; the kit `<project>-stats-<first>-<last>.csv`. Polish and English words, `-` and `_`, the tool's name and the station's code each in a different place.

## Decision

A file a tool names for a user (a GUI's download, a REST attachment, a file written into `--output-dir` under a name the tool chooses) is named

`<tool>_<content>_<qualifiers>.<extension>`

- `<tool>`: the tool's name in the registry, lower case (`obserwator`, `hydrolog`, `hydrograf`, `archiwista`, `kartograf`).
- `<content>`: what the file holds, in English, lower case, words joined by `-` (`stations`, `series`, `analyses`, `pmaxtp`, `hyetograph`, `network-nodes`, `comparison`, `stats`).
- `<qualifiers>`: what tells two such files apart, each part separated by `_`, identifiers as they are (a dataset key `pl.imgw.meteo_precip_daily`, a station code, a provider's id in lower case `imgw-pib` or `chmu`, a method), dates as ISO `2026-11-21`, a text a user gave (a project's or a subject's name) reduced to lower-case ASCII without diacritics with `-` for anything else; none when the content alone names the file.
- `<extension>`: lower case, the format's own (`csv`, `json`, `geojson`, `parquet`, `png`, `svg`, `zip`).
- Only ASCII letters, digits, `.`, `-` and `_`; no spaces or diacritics.

Not covered: files kept as the provider published them (DEV-19.5, plain mode), a store's own files, and a name the user gives (`--output`).

The rule is DEV-19.21; ECO-083 gives its reasons and the hand-off's name. A person's text is reduced by the kit's `nameSlug` (`nogat-handoff.js`): lower-case ASCII without diacritics (`ł` is `l`), each run of other characters one `-`, none at either end; a GUI uses it for its own names too, a Python tool does the same.

## Names now and under the rule

Read in the code on 2026-11-21, at the commits the steps start from. Lines are those of that commit. „Stays” marks a name the rule does not cover, with the reason. The kit's two names change in Nogat (step 1) and reach a tool when it copies the kit: hand-off `<subject>.handoff.json` → `<tool>_handoff_<subject>.json`, statistics `<tool>-stats-<first>-<last>.csv` → `<tool>_stats_<first>_<last>.csv` (all four GUIs have `nogat-admin.js`).

### Obserwator

`feat/national-provider-names` at `08842b6`; `develop` at `f0e0508` has the same lines, with ČHMÚ as `chmi` (`stations_chmi_meteo.csv`, `…_chmi_hydro_daily.csv`). No CLI or MCP command chooses a name in `--output-dir`: `datasets download -o` keeps the provider's names (DEV-19.5) and the exports are streams to standard output or `--output`.

| Where | Surface | Now | Under the rule |
|---|---|---|---|
| `src/obserwator/gui/_app.py:1207-1210` (`_stations_name`; sent at `:1283-1289`, listed for `gui/web/src/panel.js:291` at `:1231-1234`) | GUI download | `stations[_<provider>][_<kind>].<format>`: `stations_imgw-pib_meteo.csv`, `stations_chmu_hydro.csv`, `stations.geojson` | `obserwator_stations[_<provider>][_<kind>].<format>`: `obserwator_stations_imgw-pib_meteo.csv`, `obserwator_stations.geojson` |
| `src/obserwator/gui/_app.py:1052-1054` (`_series_name`; listed at `:1070`, sent at `:1140-1172`; `gui/web/src/sections/pobierz.js:73`, `:99`) | GUI download | `<code>_<dataset slug>.<format>`: `252170380_meteo_precip_daily.csv`, `0-203-1-900001_chmu_hydro_daily.csv` | `obserwator_series_<dataset key>_<code>.<format>`: `obserwator_series_pl.imgw.meteo_precip_daily_252170380.csv`, `obserwator_series_cz.chmu.hydro_daily_0-203-1-900001.csv` |
| `src/obserwator/gui/_app.py:739-741` (`_analyses_name`; sent at `:789-792`, listed at `:1099`) | GUI download | `<code>_analyses.<format>`, one analysis `<code>_<analysis>.<format>`: `252170380_analyses.csv` | `obserwator_analyses_<code>[_<analysis>].<format>`: `obserwator_analyses_252170380.csv` |
| `src/obserwator/gui/_app.py:730-733` (`analysis_file`); `gui/web/src/sections/pobierz.js:127` builds both names again in the page | GUI download | `<code>_<analysis>.json`, `<code>_<analysis>.csv`: `149190310_flood_frequency.Q.json` | `obserwator_analyses_149190310_flood_frequency.Q.json`; the page takes the name from the server's list, not its own copy |
| `src/obserwator/gui/_app.py:994` (`pmaxtp_file`, sent at `:1026`); `gui/web/src/pmaxtp/result.js:52` builds it again from the query (`download=` at `:167`) | GUI download | `pmaxtp_<method>_<lat>_<lon>.<format>`: `pmaxtp_POT_52.4142_17.4586.csv` | `obserwator_pmaxtp_POT_52.4142_17.4586.csv` (the method as it is, coordinates with 4 decimals) |
| `src/obserwator/gui/web/src/sections/meteo/stripes.js:359-371`, texts `messages/gui/meteo_temperature.py:457-464` | GUI Blob save | translated: `climate-stripes-<code>-<first>-<last>[-axis].<png\|svg\|csv>`, in Polish `paski-klimatyczne-<code>-<first>-<last>[-os].<…>` | `obserwator_climate-stripes_<code>_<first>_<last>[_axis].<png\|svg\|csv>`: `obserwator_climate-stripes_252170380_1951_2025.png`, one name in both languages, so no message |
| `src/obserwator/gui/web/src/sections/handoff.js:83` (kit `downloadHandoff`), subject `messages/gui/server.py:118-125` | GUI download (kit) | `Poznań — Q, wartości dobowe.handoff.json` | `obserwator_handoff_poznan-q-wartosci-dobowe.json` |
| `src/obserwator/api/routes/commands.py:613-614` (`_attachment`, header at `:658`), `series export` | REST attachment | `<station>.<format>`: `252170380.csv` | `obserwator_series_<dataset key>_<station>.<format>` as in the GUI, the dataset of `dataset` or of `version` |
| `src/obserwator/api/routes/commands.py:615-616`, `stations export` | REST attachment | `stations.<format>` whatever the filters | `obserwator_stations[_<provider>][_<family>].<format>` as in the GUI |
| `src/obserwator/api/routes/commands.py:617-618`, `analyses export` | REST attachment | `<station>_analyses.<format>` | `obserwator_analyses_<station>.<format>` |
| `src/obserwator/api/routes/commands.py:619-622`, `store export` | REST attachment | the stored file's stem: `codz_2024.csv` | stays: the unit's name in the store, the provider's (DEV-19.5) |
| `src/obserwator/api/routes/commands.py:611-612`, `commands guide` | REST attachment | `AGENTS.md`, `llms.txt` | stays: the names AGI §8 gives the guides |

Texts that name the files change with them: the manual's `….handoff.json` (`gui/web/instrukcja/index.html:882`) and the tests that read `content-disposition`.

### Hydrolog

`feat/national-provider-names` at `15de29a`. The GUI's exports take their base from a subject through `fileBase` (`src/hydrolog/gui/web/src/ui/export-panel.js:37-43`: characters a file system refuses become `-`, diacritics and spaces stay, `hydrolog` when empty), which goes for `nameSlug`; each section gives its content word.

| Where | Surface | Now | Under the rule |
|---|---|---|---|
| `src/hydrolog/gui/web/src/ui/export-panel.js:299`, `:304`, `:313` (ExportButtons), subject of Hydrogram zlewni `sections/hydrogram/index.js:367` | GUI Blob save | `<subject>.csv`, `<subject>.result.json`, `<subject>.png`: `Kamiennik — Świerzawa.csv` | `hydrolog_hydrograph_kamiennik-swierzawa.csv`, `hydrolog_hydrograph-result_kamiennik-swierzawa.json`, `hydrolog_hydrograph_kamiennik-swierzawa.png` |
| the same buttons, subject of Statystyka `sections/statystyka/export.js:40-43` | GUI Blob save | `<series file>-kwantyle.<csv\|result.json\|png>`: `maksima_roczne-kwantyle.csv` | `hydrolog_quantiles_maksima-roczne.csv`, `hydrolog_quantiles-result_maksima-roczne.json` |
| the same buttons, subject of Kalkulatory and Wszystkie polecenia `sections/kalkulatory/export.js:60`, `sections/polecenia/export.js:18` | GUI Blob save | the command with `-` for spaces: `tc-kirpich.csv` | `hydrolog_<command>.<…>`, the command as content: `hydrolog_tc-kirpich.csv`, `hydrolog_tc-kirpich-result.json` |
| `src/hydrolog/gui/web/src/ui/export-panel.js:321` (report into the session's `out/`, saved by `api.js:393-394`, served with `content-disposition` at `gui/_app.py:940`) | GUI download | `<subject>.md` through `sessionFileName` (`controls/file-field.js:71-77`: diacritics folded, case kept, `_` for the rest): `Kamiennik _ Swierzawa.md` | `hydrolog_report_kamiennik-swierzawa.md` |
| `src/hydrolog/gui/web/src/sections/kalkulatory/results-panel.js:151` | GUI Blob save | `porownanie-tc.csv` | `hydrolog_tc-comparison.csv` |
| `src/hydrolog/gui/web/src/sections/siec/export.js:87`; stem `sections/siec/state.js:479-481` (the opened file's name, `siec` by default, `:81`) | GUI Blob save | `<stem>-<node>.csv`: `kamiennik-W3.csv` | `hydrolog_node-hydrograph_kamiennik_W3.csv` (the node id as it is) |
| `src/hydrolog/gui/web/src/sections/siec/export.js:97` | GUI Blob save | `<stem>-wezly.csv`: `siec-wezly.csv` | `hydrolog_network-nodes_<stem>.csv`: `hydrolog_network-nodes.csv` for the default `siec`, `hydrolog_network-nodes_kamiennik.csv` |
| `src/hydrolog/gui/web/src/sections/siec/export.js:107`, `sections/siec/index.js:1075` (the network's document) | GUI Blob save | `<stem>.json`: `siec.json` | `hydrolog_network_<stem>.json`: `hydrolog_network_kamiennik.json`; a stem that already starts `hydrolog_network_` loses it, so saving again does not repeat it |
| `src/hydrolog/gui/web/src/sections/siec/export.js:117` | GUI Blob save | `<stem>.result.json` | `hydrolog_network-result_<stem>.json` |
| `src/hydrolog/gui/web/src/sections/siec/export.js:127`, `:136` (PNG drawn in the page, SVG from the session's `out/`) | GUI Blob save, GUI download | `<stem>.png`, `<stem>.svg` | `hydrolog_network-schematic_<stem>.png`, `hydrolog_network-schematic_<stem>.svg` |
| `src/hydrolog/gui/web/src/handoff/handoff-panel.js:546` (kit `downloadHandoff`) | GUI download (kit) | `<subject>.handoff.json`: `Kamiennik — Świerzawa.handoff.json` | `hydrolog_handoff_kamiennik-swierzawa.json` |
| `src/hydrolog/operations/route.py:1287`, `:1365-1368` (`route network -o`; catalog `catalog/groups/route.py:358-362`, `:1449-1455`) | CLI, MCP default | `<node id>.csv` per node: `W3.csv` | `hydrolog_node-hydrograph_<node id>.csv`: `hydrolog_node-hydrograph_W3.csv` |

Stays: `ATTRIBUTION.txt` beside the tables (`operations/route.py:279-287`, DEV-20.5); the files a received hand-off puts into the session's `in/` (`handoff/handoff-panel.js:181`, `:194`), which the person never downloads; `report generate --output` and `route schematic --schematic`, named by the caller. Texts: the manual's `<nazwa>.handoff.json` (`gui/web/instrukcja/index.html:530`), `handoff/handoff-panel.js:523`.

### Hydrograf

`feat/phone-sources-strip` and `develop` (`d23cb02`) have the same lines. Every name is built in the page; the backend sends no attachment (`POST /api/downloads` only counts) and the scripts of `backend/scripts/` write the operator's data directory, not a user's file. The stem is `fileStem` (`frontend/js/rain-export.js:26-32`), with a decimal comma (`p0,5`, `arf0,9`), which the rule does not allow.

| Where | Surface | Now | Under the rule |
|---|---|---|---|
| `frontend/js/rain-export.js:77` | GUI Blob save | `hietogram_<duration>_p<probability>[_arf<factor>].csv`: `hietogram_1h_p10.csv`, `hietogram_12h_p0,5_arf0,9.csv`; a series of one's own `hietogram_wlasna_seria.csv` | `hydrograf_hyetograph_1h_p10.csv`, `hydrograf_hyetograph_12h_p0.5_arf0.9.csv`, `hydrograf_hyetograph_custom.csv` |
| `frontend/js/rain-export.js:106` | GUI Blob save | `hietogram_<…>.json` | `hydrograf_hyetograph_<…>.json` |
| `frontend/js/rain-export.js:148` | GUI Blob save | `punkty_PMAXTP_<…>.geojson`: `punkty_PMAXTP_1h_p10.geojson` | `hydrograf_pmaxtp-points_1h_p10.geojson` |
| `frontend/js/handoff.js:156` (kit `downloadHandoff`), subject `backend/core/handoff.py:497`, `:577-579` | GUI download (kit) | `<subject>.handoff.json`: `Kaczawa, sieć (3 zlewnie).handoff.json` | `hydrograf_handoff_kaczawa-siec-3-zlewnie.json` |

Texts: `frontend/index.html:544` (the button's title), `frontend/instrukcja/index.html:474`, `frontend/js/handoff.js:12`.

### Archiwista

`fix/national-provider-names` at `85c5df0`.

| Where | Surface | Now | Under the rule |
|---|---|---|---|
| `src/archiwista/web/src/views/compare.js:778-788` (`csvName`, saved at `:760`; titles `:177`, `:234`), word `web/src/labels/compare.js:111` | GUI Blob save | `porownanie-<A>-<B>.csv`, the sides' titles with diacritics folded and `_` for the rest, case kept: `NMT · 2020` gives `porownanie-NMT_2020-NMT_2024.csv` | `archiwista_comparison_<a>_<b>.csv` through `nameSlug`: `archiwista_comparison_nmt-2020_nmt-2024.csv`; the word leaves the labels |
| `src/archiwista/services/log.py:179` (sent at `api/log.py:75`; the page's fallback `web/src/api.js:1158`) | REST attachment | `archiwista-log-<YYYYMMDDTHHMMSSZ>.<jsonl\|csv>`: `archiwista-log-20261121T143022Z.jsonl`; fallback `archiwista-log.<format>` | `archiwista_log_2026-11-21_143022Z.jsonl`; fallback `archiwista_log.<format>` |
| `src/archiwista/api/projects.py:674-678` (`GET /projects/{project}/exports/{name}/zip`) | REST attachment | the ZIP's name on disk, `<export name>.zip`: `raba-2024.zip` | `archiwista_export_<project>_<export name>.zip`: `archiwista_export_raba_raba-2024.zip`; the file on disk keeps the name the person gave |
| `src/archiwista/web/src/views/station-chart.js:345` (kit `downloadHandoff`), subject `services/station_handoff.py:182-184`, texts `messages/api.py:324-327` | GUI download (kit) | `<subject>.handoff.json`: `Nowy Sącz — Q, maksima roczne.handoff.json` | `archiwista_handoff_nowy-sacz-q-maksima-roczne.json` |

Stays: `project-export` writes `eksport/<name>/` and `eksport/<name>.zip` (`projects/exports.py:223`), named by the person, with the stored files under their own names (`:353-377`), `README.txt` and `ATTRIBUTION.txt`; a stored file sent by `api/files.py:309-315` keeps its name in the store. Texts: `web/src/labels/station.js:122`, `messages/cli.py:2480-2486`, `api/models_handoff.py:107`, `commands/stations.py:359`, `tests/e2e/test_station_chart.py:445`.

### Kartograf

`develop` at `228a2870`: nothing to change. Kartograf has no GUI and no REST attachment (no `Content-Disposition`, `FileResponse` or `download=` in `src/`). Its files keep the names of their units in the store (DEV-19.5), in plain mode too: the provider's names (LAZ `tile.filename`, `download/laz.py:151`; the sheets and packages) or the unit's identifier (a sheet, TERYT, country or tile code, `download/storage.py:779` `unit_slot`; a cutout's box `<min_x>_<min_y>_<max_x>_<max_y>.tif`, `download/storage.py:699`). `keep_raw` of BDOT10k writes `<output stem>_GPKG.zip` beside the caller's `output` (`providers/pl/bdot10k.py:387`), a name the caller gives.

## Steps

| # | Repository, branch | Change |
|---|---|---|
| 1 | Nogat, `feat/download-file-names` | the rule in DEV §19 with an ECO decision; the kit's files that name a download (`nogat-admin.js` statistics, `nogat-handoff.js` hand-off file) and their tests, the kit's hashes (kit `1.1.0`); `design/README.md`; the table of every tool's current names and their new names in this plan |
| 2 | Obserwator, from `feat/national-provider-names` | its GUI downloads, REST attachments and default export names; tests, docs, the manual; the kit's copy |
| 3 | Hydrolog, from `feat/national-provider-names` | its GUI downloads and default output names; the kit's copy |
| 4 | Hydrograf, from `feat/phone-sources-strip` | its GUI downloads (it sends no attachment); the kit's copy |
| 5 | Archiwista, from `fix/national-provider-names` | its GUI downloads and API attachments (`project-export` keeps the names the person gives); the kit's copy |

Steps 2 to 5 are part of the round's releases; nothing is tagged before the round ends.
