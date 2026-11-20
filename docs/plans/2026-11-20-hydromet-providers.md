# Plan: hydro-meteorological providers beyond the national services, starting with Gdańskie Wody

Approved: pending (the author's answers of 2026-11-20 below; the open questions and the licence block the steps that store or publish data)

Requirements: DEV-17.4, HUB-5.2, DEV-18.4, DEV §19, DEV §20, AGI-3.4, ECO-002.

Releases (the author, 2026-11-20): step 0 is a fix of Obserwator `v3.1.1`; steps 2 to 5 are Obserwator `v3.2.0`, after `v3.1.0` keeps its scope; the consumers' steps 6 and 7 follow in their own next minors.

## The author's answers (2026-11-20)

- Aim: „zacząć pracę nad dodawaniem kolejnych źródeł danych hydrometeorologicznych. Będą to inne podmioty niż służby hydrometeo, np. urzędy, uniwersytety lub inne podmioty. Trzeba więc zaplanować jak dalej dodawać nowych dostawców.” The first candidate is `https://pomiary.gdanskiewody.pl/rest/`.
- Architecture: „Adapter na dostawcę”. Obserwator first extracts a provider interface and moves IMGW-PIB and ČHMÚ onto it without a change of behaviour; Gdańskie Wody is the first new adapter.
- Scope for Gdańskie Wody: „Pełny tor”. Raw files in the store, Parquet series, a station catalog, the GUI's map and exports with attribution, once the provider's terms allow storing and serving the data.
- Time step: „Godzinowe”. A new `time_unit` `hour`; daily values are computed from the hourly ones, not stored instead of them.
- Source classes: „trzeba jakoś rozdzielić dane pochodzące od służb hydrometeorologicznych, co do których mamy pewność, że spełniają wymagania WMO, od pozostałych źródeł, gdzie takiej pewności nie mamy. Myślę, że wystarczy to zrobić na poziomie GUI.” Decision P11.

## What a provider of this kind is

The services Obserwator reads today publish open archives without an account: IMGW-PIB's annual packages and ČHMÚ's CC BY 4.0 files. The providers this plan opens up are municipal companies, offices and universities. Their access is an API with an account, their terms are often visible only after sign-in, their networks cover a city or a catchment, their time step is hourly or finer, their values are often raw and unverified, and their levels are often in metres above sea level rather than centimetres above a gauge zero. Every rule below comes from one of these differences.

## Gdańskie Wody: what was checked (2026-11-20)

The documentation is visible only to registered users. The author pasted it into the session. The facts below were checked against the live API with the author's key unless marked otherwise.

| Topic | Finding |
|---|---|
| Access | Free registration; header `Authorization: Bearer <key>`; the key is in the account's settings. |
| Errors | Always HTTP 200 with `{"status":"error","code":N,"message":…}`: `-100` authentication, `-2` unknown symbol, `-3` bad date, `-11` unknown station, `-12`/`-13` the station does not measure the quantity. The result is known only from the body. |
| Stations | `GET /rest/stations`: 131 stations, all `active: true`, `no` an integer from 1 to 999 with gaps, `lat`/`long` as strings, one boolean per quantity, no first-data date, no river, no elevation, no datum. |
| Quantities | 202 station×quantity pairs: `water` 91, `rain` 40, `temp` 16, `humidity` 13, `winddir` 7, `windlevel` 7, `pressure` 6, `sun` 4, `flow` 2, `dissolvedoxygen`/`redox`/`ph`/`conductivity`/`watertemp` 3 each, `turbidity` 1. |
| Measurements | `GET /rest/measurements/{no}/{symbol}/{YYYY-MM-DD}`: 24 pairs `["YYYY-MM-DD HH:MM:SS", value]`, UTC, from 06:00 of the date to 05:00 of the next day; a missing hour is `null`; values are JSON numbers, integers and floats mixed. |
| History | A date before a station's start or after today answers 24 `null`s, not an error. The first non-null day found by bisection: no. 1 `rain` 2005-06-15, no. 4 and no. 999 `water` 2015-10-16, no. 201 `water` 2017-12-18, no. 504 `flow` 2020-12-31. Bisection assumes no long gaps; the store's first-date record must be built from data, not from bisection alone. |
| Speed | 0.2 to 1.5 s per request, sequential; no rate-limit headers. |
| Units | Confirmed only by the public charts: `rain` „Opad [mm]”, `water` „Poziom wody [m n.p.m.]” (absolute level, not IMGW-PIB's H in cm). The other units are unknown. |
| Verification | The public site says: „Prezentowane dane są danymi surowymi bez weryfikacji. Nie mogą być wykorzystane jako materiał dowodowy.” |
| Terms | The signup form requires accepting a regulamin and a RODO clause; the regulamin is not visible without signing in. **Unknown: whether the data may be stored, redistributed or shown in a public GUI, and with which attribution.** |
| Not a source | The site's charts call `/measurments/json/{station}/{channel}/{0..2}` (sic) without a key: the last three days only, values as strings, undocumented. It is not used. |

Estimate, not measured: about 200 pairs × 10 years × 365 days ≈ 0.7 million requests for the full history, so 40 to 120 hours of sequential downloading. That is too much to do without asking the provider first.

## Goal

1. A written intake process that any new provider passes before code is written (below), kept in Nogat as the record of the decision.
2. Obserwator with one provider interface. IMGW-PIB, ČHMÚ and every new provider are adapters. Adding a provider means one module, registry entries, attribution lines and messages, with no new `if provider == …` branches elsewhere.
3. Gdańskie Wody served end to end once its terms allow it: station catalog, raw store, hourly series, daily aggregates, map and exports with its attribution and a notice that the data are raw and unverified.

## Provider intake (every new provider)

A provider is added only after a note in Obserwator's `docs/` (one per provider) answers every row of this list, with the date it was checked and the evidence:

| Row | Question |
|---|---|
| Identity | Legal name, short name, country, contact address, provider id (`gdanskie-wody`) and dataset prefix (`pl.gdanskiewody`). |
| Terms | Licence or regulamin text, stored verbatim in the note. May the data be stored, served publicly and redistributed? Is attribution required, and in what words? Is commercial use allowed? |
| Access | Open files, an API with a key, OAuth or something else. Credential names in Obserwator. Rate limits and the load the provider accepts. |
| Errors | How the API reports authentication, an unknown station, no data and a bad request, mapped to the error registry. |
| Stations | List endpoint, identifier and its stability, coordinates with CRS and accuracy, river, elevation, datum, first and last data. |
| Quantities | Every quantity with unit, datum, time step, aggregation (sum, mean, instant), interval labelling (the start or end of the hour) and time zone. |
| Quality | Verified or raw, revisions of past values, flags, missing-value encoding. |
| History | Earliest data, how to find it per station, and the request count of a full backfill. |
| Overlap | Stations that duplicate IMGW-PIB or ČHMÚ gauges (no merging; a cross-reference at most). |

## Design decisions proposed

| ID | Decision | Rejected alternative |
|---|---|---|
| P1 | **Provider adapters in Obserwator.** A package `obserwator.providers` with one module per provider, `pl/imgw.py`, `cz/chmi.py` and `pl/gdanskie_wody.py`, the same layout as Kartograf's `kartograf.providers.pl/…`. An adapter implements one `Protocol`: station sources (fetch and parse), archive enumeration and download per dataset, parsers per dataset, live current data (optional), the credential it needs (optional) and its attribution origin. `datasets.py` stays the declarative registry the catalog, AGENTS.md and llms.txt are generated from. `ProviderDescriptor` gains an `adapter` reference, and the scattered branches (fetch `_origin`, stations `_live_sources`/`_parsed`/`_identity`, catalog `_CATALOG_DIRS`, attribution `_PROVIDERS`, commands `_GROUP_PROVIDERS`, the GUI's `_station_attribution`) dispatch through it. | Further `if/else` branches per provider. |
| P2 | **The refactor changes no behaviour.** The bytes of archives, sidecars, series, catalogs, envelopes and AGENTS.md stay the same for IMGW-PIB and ČHMÚ. The contract tests and the fixture stores are the gate. `stations/versions/` (IMGW-PIB) and `stations/versions/chmi_stations/` keep their paths, and new providers get `stations/versions/<provider_id>/`. | Moving the IMGW-PIB catalog: it breaks Archiwista and the existing stores. |
| P3 | **Provider credentials.** One credential per provider that needs one: `OBSERWATOR_<PROVIDER>_API_KEY`, or the file named by `OBSERWATOR_<PROVIDER>_API_KEY_FILE`, as for the admin key (ADR-020). For Gdańskie Wody: `OBSERWATOR_GDANSKIE_WODY_API_KEY[_FILE]`. They are added to `CREDENTIAL_KEYS`, never read from `nogat.toml`, never logged, and reported `present`/`missing` by `config show`. A key file must have mode 0600, otherwise it is a warning. The author's key is in `~/.config/nogat/secrets/gdanskie-wody.key`. | A key in `nogat.toml`; a single generic `OBSERWATOR_API_KEYS` JSON. |
| P4 | **Errors.** A missing or rejected provider key is `forbidden` (exit 12) with `details.reason` `missing_credentials` or `invalid_credentials`, `details.provider` and a hint naming the variable. A body-level error of an HTTP 200 answer maps to the registry: unknown station → `not_found`, quantity not measured → `no_data`, bad request → `validation_error`, anything else → `source_unavailable`. No new code in Nogat's registry. Nogat step 1 records the two reasons in `standards/ERROR_REGISTRY.md` as reasons of `forbidden`, so Kartograf's CLMS credentials can use them too. | A new top-level code `unauthorized` outside REST. The registry reserves it for HTTP 401. |
| P5 | **Hourly series.** `time_unit` `hour` in `DatasetDescriptor` and `obserwator-series/1` (additive). A record carries the UTC start of its hour. The adapter converts the provider's label once the intake note has settled whether a label marks the start or the end. `year_type` `calendar`, `hydro_year` as for the other providers. Daily aggregates follow the provider's day: for Gdańskie Wody 06:00–05:59 UTC, with sums for `rain` and means or extremes for the others, as Hydrolog's or the series reader's documented rule, not ad hoc. | Daily values only. |
| P6 | **Raw form for per-day APIs.** One answer covers one station, quantity and day, so raw files would number about 10⁶. The raw unit is a **month per station×quantity**: the daily answers of the month gathered into one canonical JSON (answers verbatim, keyed by date, sorted, LF-terminated) with `archive_scope` `station_element_month` and a sidecar like the others. This follows the precedent of `pl.imgw.hydro_details`, a file gathered from many requests (ADR-015 D5), and of ČHMÚ's content pin (`chmi-json/1`). A closed month is fetched again only on an explicit request, because the provider may revise raw values. The current month is a new version each sync until it closes. | One raw file per day. |
| P7 | **Absolute levels are their own variable.** Gdańskie Wody's `water` is in m a.s.l. It becomes `H_asl` (m), never `H` (cm above gauge zero), with the datum in the station catalog once the intake note gives it. `flow` is `Q` (m³/s) once its unit is confirmed. The water-quality quantities keep their own names. | Converting to IMGW-PIB's H: no gauge zero is published. |
| P8 | **Raw-data notice.** Every provider of the class `other` (P11) carries a fixed notice (a catalog message) beside its attribution in envelopes, exports and the GUI's station panel. The notice says that the data do not come from a national hydro-meteorological service and, where the provider states it (Gdańskie Wody does), that they are unverified. It is not one of the attribution lines of DEV §20. Exports therefore keep the distinction after they leave the GUI, with no new field. | Silent. |
| P9 | **Attribution lines.** DEV §20 lists a line per provider (S, P, C, CP …). Rather than one rule per new provider, Nogat step 1 turns it into a table of provider lines (code, text, processed text, order) that DEV-20.4 orders. Gdańskie Wody gets its line once its terms give the wording; „Gdańskie Wody Sp. z o.o., pomiary.gdanskiewody.pl” is the draft. | A new rule in DEV §20 for each provider. |
| P10 | **Load.** Downloads are sequential, 1 request per second by default (`OBSERWATOR_<PROVIDER>_REQUEST_INTERVAL`), cancellable between requests and resumable by month. A full backfill runs only after the provider agrees, with the address `pomiary@gdanskiewody.pl` from its API page. | An unthrottled backfill. |
| P11 | **Two source classes, separated in the GUI.** `ProviderDescriptor.source_class` is `nmhs` (a national meteorological and hydrological service of a WMO member: IMGW-PIB, ČHMÚ) or `other` (offices, municipal companies, universities and the rest). The registry holds it, so no GUI code names providers (P1). It is given per provider, not per station or dataset. The label states the operator, not a compliance certificate: „Służby hydrologiczno-meteorologiczne” and „Inne źródła”. Even an NMHS network has posts and operational data outside WMO's quality procedures, so the GUI never writes „zgodne z WMO”. The station panel of an `other` station opens with a badge of the class and P8's notice, and its analyses keep the badge on every chart and table. Archiwista's GUI shows the same class wherever it shows Obserwator's stations. Outside the GUIs only P8's notice carries the class; `stations find`, `stations export` and the catalog get `source_class` as an additive field because they already list `provider`. | GUI-only code keyed on provider ids (breaks P1); a claim of WMO compliance per station. |
| P12 | **Grouping in the „Stacje” view: class → provider → dataset; kind stays a separate filter.** Today the left panel (`list.js`) holds every filter: a provider switch (`Wszyscy` / IMGW-PIB / ČHMÚ), a kind switch, dataset chips grouped by provider and „tylko czynne”; the map's legend has no switches. The provider switch is replaced by a class switch (`Wszystkie` / `Służby` / `Inne źródła`), which stays three buttons however many providers come. The dataset chips are grouped under two class headings, with the provider's name and country (`IMGW-PIB · PL`) above its chips, so one provider is still chosen by its chips. Within a class, providers are sorted by country, then name; country headings appear only when one class holds more providers than fit the panel. Every filter stays in the left panel; the legend only explains the symbols. Both classes are shown by default (the author, 2026-11-20). `NO_FILTERS.provider` becomes `class`, and `NoStation`'s summary counts by class. Filters are not in the address, so no old address has to keep working. Country is not a grouping axis: the map already shows it, every NMHS is one country, and country-first grouping would put Gdańskie Wody beside IMGW-PIB, the mix P11 exists to avoid. | Country first; filters in both the panel and the legend; one switch button per provider. |
| P13 | **Symbols: the outline tells the class.** Shape (triangle hydro, circle meteo), fill (the kind's colour of hydro.imgw.pl), a hollow centre (only in the catalog) and fading (inactive) keep their meaning. The outline changes. It is solid grey for every NMHS, as on hydro.imgw.pl, and dashed (`DASH` 5/3, width 2.6, as now) for `other`. ČHMÚ loses its dashed outline because it is now a service like IMGW-PIB and its stations lie in Czechia. Two outline styles stay readable at 16 px, three would not. The legend reads „Służba hydrologiczno-meteorologiczna” (solid) and „Inne źródło” (dashed); the tooltip, the list's second line and the panel's badge name the provider. `stationIcon` and `StationSymbol` take the class instead of comparing with `"CHMI"`. „Pomiary bieżące” is unchanged (IMGW-PIB only). | Hollow for `other` (hollow already means „tylko w katalogu”); a third outline style; a colour per provider. |

## Steps (producers first)

0. **Obserwator `v3.1.1`:** `.env` is not in `.gitignore` (`git check-ignore .env` exits 1), while credentials may live in `.env`. Add it.
1. **Nogat:** this plan; `ecosystem.yaml` `data_sources` gets `gdanskie-wody` (PL, `https://pomiary.gdanskiewody.pl`, licence from its terms) and Obserwator's `data_sources` and summaries mention it; DEV §20 table of provider lines (P9); the reasons of P4 in the error registry; `docs/ECOSYSTEM_MAP.md` and AGENTS.md regenerated. The routing rows saying „IMGW-PIB or ČHMÚ” are rewritten when step 5 ships, not before.
2. **Obserwator, ADR „provider adapters”** (P1, P2): extract the interface and move IMGW-PIB and ČHMÚ. The full gate and the fixture stores must give the same bytes. No Gdańskie Wody code yet.
3. **Obserwator, credentials and errors** (P3, P4): settings, `config show`, `.env.example`, `CLAUDE.md`, messages pl/en.
4. **Obserwator, `hour`** (P5): registry, series schema (additive), reader, exports (CSV/JSON/Parquet), the GUI's charts for hourly data, and daily aggregation by the provider's day.
5. **Obserwator, Gdańskie Wody adapter** (P6–P8, P10–P13): intake note; datasets `pl.gdanskiewody.stations` (station source) and `pl.gdanskiewody.hourly`; parsers with fixtures recorded from the live API (key never in fixtures); `store sync`/`check`, `series build`, `store catalog --provider gdanskie-wody`, `stations find`; attribution and the raw-data notice; `source_class` in the registry (`nmhs` for IMGW-PIB and ČHMÚ); in the GUI the class switch and class headings of P12, the outlines of P13 and the panel badge of P11, in the same change, because a class switch with an empty „Inne źródła” has nothing to separate; `@pytest.mark.live` tests that skip without the key. Storing and the public GUI wait for the terms (question 1).
6. **Archiwista:** its jobs download through Obserwator's library, so it needs the credential in its deployment, the new datasets in its job choices and the catalog path `stations/versions/gdanskie-wody/` in its reader. Its GUI shows the source class (P11) from Obserwator's registry.
7. **Hydrolog / Retman:** Hydrolog's `hydrolog-series/1` hand-off is checked for hourly input (hyetographs, tc); Retman's manifest is refreshed from `commands schema` (drift check), no code expected.
8. **Nogat:** registry drift, release set, PROGRESS.

## Open questions

1. **Terms (blocks storing and the public GUI).** The regulamin of pomiary.gdanskiewody.pl as accepted at signup: storage, redistribution, public display, attribution wording. Visible only after sign-in; the author pastes it like the API documentation.
2. **Hour labels.** Does `2026-11-19 06:00:00` with `rain` 1.3 mean the sum over 06:00–07:00 or over 05:00–06:00? To be asked of `pomiary@gdanskiewody.pl` or derived from a comparison with the daily total on the site.
3. **Units and datums** of `temp`, `pressure`, `humidity`, `sun`, `windlevel`, `flow` and the water-quality quantities, and the vertical datum of `water` (PL-EVRF2007-NH or older).
4. **Backfill.** Whether the provider accepts about 0.7 million requests, at what rate, or offers a bulk export.
5. **Next providers.** Which offices or universities follow (named by the author). Each one passes the intake before code.

## Results

(filled as steps finish)
