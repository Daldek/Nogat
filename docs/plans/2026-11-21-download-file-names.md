# Plan: one way of naming the files a tool hands to a user

Approved: 2026-11-21, the author (in session: „Jeszcze jedna rzecz do ujednolicenia - nazwy pobieranych plikow”, then the choices „Cały ekosystem w tej rundzie”, „Angielskie”, „Tak, z nazwą narzędzia na początku” out of: the whole ecosystem in this round, the rule now and Obserwator now, Obserwator only; Polish or English words; with or without the tool's name)

Status: approved; step 1 in progress.

Requirements: DEV §19 (files a tool writes), DEV-15.5 (hand-off file), DEV-15.11 (statistics file), ECO-082 (identifiers by national acronyms). Raised by the author's test of Obserwator's station list on 2026-11-21.

## The state on 2026-11-21

Each tool names its files its own way: Obserwator `stations_imgw-pib_meteo.csv`, `252170380_meteo_precip_daily.csv` (ČHMÚ `…_chmi_meteo_daily.csv`), `252170380_analyses.csv`, `pmaxtp_ks_52.4142_17.4586.csv`; Hydrograf `hietogram_<…>.csv`, `punkty_PMAXTP_<…>.geojson`; Hydrolog `<…>-wezly.csv`; Archiwista `porownanie-<…>.csv`; the kit `<project>-stats-<first>-<last>.csv`. Polish and English words, `-` and `_`, the tool's name and the station's code each in a different place.

## Decision

A file a tool names for a user (a GUI's download, a REST attachment, a file written into `--output-dir` under a name the tool chooses) is named

`<tool>_<content>_<qualifiers>.<extension>`

- `<tool>`: the tool's name in the registry, lower case (`obserwator`, `hydrolog`, `hydrograf`, `archiwista`, `kartograf`).
- `<content>`: what the file holds, in English, lower case, words joined by `-` (`stations`, `series`, `analyses`, `pmaxtp`, `hyetograph`, `network-nodes`, `comparison`, `stats`).
- `<qualifiers>`: what tells two such files apart, each part separated by `_`, identifiers as they are (a dataset key `pl.imgw.meteo_precip_daily`, a station code, a provider's id in lower case `imgw-pib` or `chmu`, a method), dates as ISO `2026-11-21`, a text a user gave (a project's or a subject's name) reduced to lower-case ASCII without diacritics with `-` for anything else; none when the content alone names the file.
- `<extension>`: lower case, the format's own (`csv`, `json`, `geojson`, `parquet`, `png`, `svg`, `zip`).
- Only ASCII letters, digits, `.`, `-` and `_`; no spaces or diacritics.

Not covered: files kept as the provider published them (DEV-19.5, plain mode), a store's own files, and a name the user gives (`--output`).

## Steps

| # | Repository, branch | Change |
|---|---|---|
| 1 | Nogat, `feat/download-file-names` | the rule in DEV §19 with an ECO decision; the kit's files that name a download (`nogat-admin.js` statistics, `nogat-handoff.js` hand-off file) and their tests, the kit's hashes (kit `1.1.0`); `design/README.md`; the table of every tool's current names and their new names in this plan |
| 2 | Obserwator, from `feat/national-provider-names` | its GUI downloads, REST attachments and default export names; tests, docs, the manual; the kit's copy |
| 3 | Hydrolog, from `feat/national-provider-names` | its GUI downloads and default output names; the kit's copy |
| 4 | Hydrograf, from `feat/phone-sources-strip` | its GUI downloads and API attachments; the kit's copy |
| 5 | Archiwista, from `fix/national-provider-names` | its GUI downloads, API attachments and `project-export` names; the kit's copy |

Steps 2 to 5 are part of the round's releases; nothing is tagged before the round ends.
