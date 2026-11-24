# Plan: PIG-PIB groundwater levels in Obserwator, each monthly publication captured before the service replaces it

Approved: pending

Status: draft of 2026-11-24 on `plan/pgi-groundwater` (worktree `~/workspace/wt/nogat-pgi`), not merged into `develop` until the author decides (DEV-3.3); nothing started. Facts probed on 2026-11-24 against the live services and Obserwator `develop` `b5a1c1a` (3.3.0.dev0). Probe files are in `~/data/tmp/pgi-probe-2026-11-24/`: `raw/` holds the 115 answers of one full capture as they came, with `manifest.jsonl` (time, address, status, SHA-256), including October 2026's readings; `terms/` holds the texts of the pages quoted below. The design marks its own proposals „[proposed]”.

Requirements: HUB-5.2, DEV-17.4, DEV-17.5 and DEV-3.4 (each project in its own session and branch), DEV-17.2, DEV-17.6 and ECO-073, DEV-18.5, DEV §19 (DEV-19.21), DEV §20 (DEV-20.4, DEV-20.5, DEV-20.7, DEV-20.8), DEV-2.5 and ECO-082, ECO-059 as amended by ECO-084, ECO-065, ECO-071, ECO-085, ECO-087, AGI-3.4, AGI-4.1. Also Obserwator ADR-029 to ADR-033, and the providers plan `2026-11-20-hydromet-providers.md`: its intake, P1, P8 and P11–P16, and its open question 5, which names PIG-PIB's MWP.

## The author's request (2026-11-24)

> „Jeszcze jedna rzecz dla Obserwatora, którą trzeba gdzieś uwzględnić. Jako osobny minor, albo do już istniejącego. Chodzi o dane hydrogeologiczne i pomiary poziomu wody. Te dane też muszą być wersjonowane. Tutaj adres do sprawdzenia: https://cbdgmapa.pgi.gov.pl/arcgis/rest/services/hydrogeologia/mwp/MapServer”

## Goal

1. Obserwator keeps PIG-PIB's groundwater monitoring as versioned data:
   - the monitoring points with their hydrogeological description;
   - the readings of groundwater depth and spring yield;
   - the automatic hourly measurements.

   Each publication is captured as it came before the service replaces it.
2. The readings become series and the points a station catalog. They are shown in the GUI's layer „Podziemne” beside ČHMÚ's bores and springs, and can be downloaded with PIG-PIB's lines.
3. No month is lost from now on. An interim capture runs before the release (S0), and the release takes its captures in.

## Facts (probed 2026-11-24)

### The service `hydrogeologia/mwp`

- **The service:**
  - ArcGIS Server 11.1 MapServer, EPSG:2180, `capabilities` `Map,Query,Data`, `maxRecordCount` 1000. Queries answer in JSON, GeoJSON (layer 0 only) and PBF, with pagination, statistics and distinct values.
  - `serviceDescription` is „Monitoring Wód Podziemnych (MWP)”; `copyrightText` is empty.
  - The service keeps no history of its own: `supportsHistoricMoment` is false and `isDataVersioned` is false. Its item metadata (`info/metadata`, created 2023-10-23) names no licence, contact or update frequency.
  - Its HTML Services Directory is off: `…/0/metadata` answers 403 „The administrator has disabled the Services Directory”. The JSON endpoints answer.
- **Access:**
  - Behind Imperva (`x-cdn: Imperva`). Query answers carry an `ETag` and no `Last-Modified`.
  - About 350 requests were made on 2026-11-24, one at a time; none was refused. `www.pgi.gov.pl`, also behind Imperva, refused plain `curl`.
- **Layer 0 „MWP - monitoring wód podziemnych”, 3,505 points:**
  - `ID` is unique (2 to 10,972).
  - `AKTUALNIE_OBSERWOWANY` is „Tak” 1,505, „Nie” 1,920 and null 80. Its values are words, which is why the query `='T'` finds none.
  - `RODZAJ_OTWORU`: drilled well („st. wiercona”) 1,698, piezometer 1,021, blank 450, spring („źródło”) 170, dug well 143, mine shaft 11, water shaft 4, staff gauge 3, research borehole 3, ventilation shaft 2.
  - `CHARAKTER_PUNKTU`: confined („Zwierciadło napięte”) 1,905, unconfined 1,424, yield („Pomiar wydajności”) 176.
  - `RZEDNA_TERENU` [m n.p.m.] is null at 600 points, none of them measured in October.
  - Coordinates: `WSP_X_1992` is the easting and `WSP_Y_1992` the northing, both equal to the geometry's x and y. `outSR=4326` returns the server's WGS84 point (point 6495: 22.10886 E, 52.02697 N).
  - The layer repeats each point's latest reading (`DATA_POMIARU` as a date field, `GLEBOKOSC_ZWIERCIADLA`, `WYDAJNOSC`) at 1,250 points.
  - Only `ID` identifies every point:
    - PSH's number `NR_PKT_MONIT_ILOSC` (e.g. `II_963_1`) is „__” at 1,596 points, 109 of them measured.
    - `NUMER_CBDH` is empty at 76 measured points and occurs twice once.
    - `IDENT_EU` is set at 1,661 points only.
- **Table 1 „MWP - pomiary”** (relationship `HG_MWP`, `OTWOR_ID` → `ID`):
  - Loaded whole, not appended: 28,514 rows with `OBJECTID` 1 to 28,514 and no gap.
  - Its only period is October. `DATA_POMIARU` is a string with a leading space, „ 2026-10-01” to „ 2026-10-31”.
  - One row per point and day at 1,255 points. Five of them (9390, 9551–9554) are not in layer 0.
  - 819 points have 31 rows (daily). 309 have 4: the Mondays 5, 12, 19 and 26 October, when about 1,200 rows are dated, against about 880 on the other days. The rest have 1 to 30.
  - `GLEBOKOSC_ZWIERCIADLA` [m p.p.t.]:
    - present in 28,355 rows, to the centimetre, from −18.32 to 592.35 m;
    - negative in 673 rows at 37 points (36 of them confined): the water stands above the ground (artesian).
  - `WYDAJNOSC` [l/s]: 159 rows at 43 points (41 springs), never in the same row as a depth.
  - Every measured point of layer 0 is „Tak”. 255 „Tak” points have no reading in October.
  - Daily readings: 879 points. 586 of them are in `mwp_auto`'s list of automatic points (below) and 293 are not.
  - Readings only on Mondays: 334 points, none of them automatic.
- **Table 2 „MWP - wskaźniki chemiczne”:**
  - 53,497 rows at 738 points: 370 indicators, sampled from 2025-01-20 to 2025-10-09.
  - `BAZA_HISTORYCZNA`: „PMŚ” 43,479 rows (GIOŚ's State Environmental Monitoring, also published at https://mjwp.gios.gov.pl) and „PSG” 10,018.
  - A result below the limit of quantification is a text in `ZNAK` („< 0.002  (wartość poniżej granicy oznaczalności LOQ)”).
  - Layer 0's `ANALIZY_CHEMICZNE` lists the years of analyses of a point.
- **Table 3 „MWP - parametry z listy obserwacyjnej (DWD 2020/2184)”:**
  - 151 rows at 151 points, sampled from 2023-01-08 to 2023-12-09.
  - 17-beta-estradiol („<0,30” in every row) and 4-nonylphenol, as text with decimal commas.
- **A full capture**, sizes gzip-compressed:

  | Part | Requests | Compressed | Plain |
  |---|---|---|---|
  | Layer 0 | 4 | 0.45 MB | 3.8 MB |
  | Table 1 | 29 | 0.31 MB | 3.6 MB |
  | Table 2 | 54 | 0.79 MB | 15.5 MB |
  | Table 3 | 1 | 5 KB | 40 KB |

  The probe's capture took 2 min 37 s at one request a second: 115 requests, including `mwp_auto`'s points and one of its days.

### The sibling `hydrogeologia/mwp_auto` (not in the author's address)

- **The service:** „MWP - pomiar automatyczny”, `copyrightText` „PIG-PIB”. Its layer 0 lists 626 automatic points (`ID_PKT_MWP`), every one of them in `mwp`'s layer 0.
- **Table 2 „MWP - dane pomiarowe bez walidacji (metry)”** (`PSH_MONITORING_ID`, `LOCATION_NAME`, `TIME`, `VALUE` [m]):
  - 7,053,184 rows at about 22:00 UTC on 2026-11-24, and growing: 7,053,763 at 22:27 UTC, whose newest row was stored at 22:00 that day.
  - Rows are appended in `OBJECTID` order (60,941,047 the newest).
  - Hourly values at 752 points: 18,053 rows for 2026-11-22 and 17,584 for 2026-11-23.
  - The network's hourly record starts in 2026-01 (535,025 rows in January). Before 2026 the table holds a few points only (8 in 2020), some rows duplicated.
  - Stray times fall in 2033, 2093 and 2136.
  - `VALUE` runs from −23.561 to 74.65: the depth below ground, the same quantity as `mwp`'s readings.
  - One UTC day takes 18 requests, 0.18 MB gzip-compressed (2.35 MB plain).
- **Table 1 „… bez walidacji (temperatura, ciśnienie)”:** the loggers' raw `Temperature` [°C], `Air Pressure` and `Pressure1` [bar] at 785 points, 1,647,686 rows from 2026-08-25 to 2026-09-25 only.
- **Time:**
  - The service declares its date fields as „Central European Standard Time” with daylight saving. A query converts the stored wall-clock times to UTC epochs by that rule. Statistics and where clauses use the stored times unconverted: `TIME >= TIMESTAMP '2026-11-22 00:00:00'` selects stored times.
  - An MWP reading, taken at 06:00 UTC by PSG's own description, equals the hourly value stored at 06:00. The service returns that value at 04:00Z before 25 October (CEST) and at 05:00Z after it. This held for 600 of 625 and 148 of 150 point-days of 25 sampled points, to two decimals.
  - The stored wall-clock time is UTC. The table 1 check: the loggers' hourly `Air Pressure` of September 2026, by stored hour, against IMGW-PIB's hourly SYNOP station pressure of the same month (`terminowe/synop/2026/2026_09_s.zip`, UTC). The hourly changes correlate best with no shift at 5 of 6 pairs 10 to 23 km apart (0.65 to 0.94: Poznań, Wrocław, Lublin, Białystok, Toruń); at Kraków-Balice (point 704) the best shift is one hour.
  - So the service's conversion is one hour off in winter and two in summer. On 2026-03-29 the stored 01:00 and 02:00 come back as one epoch, two rows at `00:00:01Z`. On 2026-10-25 no hour is lost.

### What PIG-PIB says about the data

- **dane.gov.pl, dataset 170 „Monitoring Wód Podziemnych (MWP)”** (https://dane.gov.pl/pl/dataset/170, its API read 2026-11-24):
  - licence „CC BY 4.0”; `has_dynamic_data` and `has_high_value_data` true; `update_frequency` „Codziennie”; verified 2026-11-05;
  - its resources are this service's WMS, the GeoLOG app, the yearbooks and the quarterly bulletins;
  - its description: „Pomiary zwierciadła wody i wydajności źródeł dokonywane są manualne raz na tydzień, w poniedziałek o 6.00 UTC, a w wybranych punktach automatyczne, codziennie 6.00 UTC. Zasilanie bazy pomiarami następuje raz w miesiącu.” The automatic database „zawiera wyniki surowych pomiarów ciśnienia i temperatury wykonywanych automatycznie … z częstotliwością raz na godzinę”, and the depth is „głębokość od powierzchni terenu [m]”.
- **https://www.pgi.gov.pl/psh/psh-2/monitoring-wod-podziemnych.html:** „Pomiary wykonywane są co godzinę i raz dziennie przesyłane są na serwer w PIG-PIB … W pozostałych punktach pomiary wykonywane są manualnie, z częstotliwością raz na tydzień, w każdy poniedziałek o godz. 6 UTC i raz na miesiąc przesyłane są do PIG-PIB. Po sprawdzeniu poprawności danych, do bazy danych Monitoring Wód Podziemnych trafiają dane pomiarowe wykonane o 6 UTC rano.”
- **The MWP database page** (https://www.pgi.gov.pl/psh/dane-hydrogeologiczne-psh/947-bazy-danych-hydrogeologiczne/8887-bazy-danych-monitoring-wod-podziemnych.html):
  - „Aktualizacja danych pomiarowych następuje w cyklu comiesięcznym, danych związanych z wynikami analiz chemicznych przynajmniej raz w roku, a danych o punktach w miarę napływu informacji. Wyżej wymienione dane poddawane są weryfikacji na każdym etapie gromadzenia danych.”
  - The network „istnieje od 1972 r., pomiary w niektórych punktach prowadzone są od 1965 r.”
  - „Możliwe jest udostępnianie wyselekcjonowanych danych z monitoringu w postaci źródłowej oraz przetworzonej.”
- **Cadence of table 1:** monthly by these pages. No page found names the day of the swap, so S0 observes it [INFERENCE: after the month closes and its data are checked; on 2026-11-24 the table held October].

### History

- **No public download of the record.** „Szerszy dostęp do wybranych baz danych (CBDH, MWP, POBORY) można uzyskać poprzez złożenie odpowiedniego wniosku.” (https://www.pgi.gov.pl/psh/psh-2/dane-online.html)
- **The request form** (Załącznik nr 1 – MWP, of the director's order nr 3 of 2 February 2026):
  - It offers „Dane pomiarowe - głębokość od powierzchni terenu do zwierciadła wody podziemnej [m] lub wydajność źródła [l/s]” by years, as Excel.
  - Free: „Informacje hydrogeologiczne w celu ich ponownego wykorzystywania udostępniane są bezpłatnie” (§ 9 ust. 1 of the order). Only extra work is charged, 98 zł net an hour by the 2026 price list.
  - Filed by ePUAP, by e-mail with a qualified signature or a trusted profile, or on paper; answered within 14 days, at most two months.
- **Rocznik Hydrogeologiczny PSH/PSG** (https://www.pgi.gov.pl/psh/materialy-informacyjne-psh/rocznik-hydrogeologiczny-psh.html):
  - Free PDFs for the hydrological years 2003–2025; 1991–1999 in print.
  - It holds „przetworzonych w zakresie standardowym wyników obserwacji”: monthly to annual characteristic levels (NG, SG, WG), not the readings. It is no source for a series.
- **The quarterly bulletins and the monthly „Komunikat o bieżącej sytuacji hydrogeologicznej”** are processed summaries too (October 2026's is on https://www.pgi.gov.pl/psh/psh-2/aktualna-sytuacja-hydrogeologiczna.html).
- **`mwp_auto`** keeps the automatic network's hourly values from 2026-01 (observed, not documented). It is the only public record longer than a month, and it is unvalidated.

### Terms

- **PIG-PIB's terms of reuse** (https://www.pgi.gov.pl/rejestry-i-bazy-danych-geologicznych/zasady-korzystania-z-isp.html). They are linked as the `AccessConstraints` of the service's WMS and as the `licenseInfo` of the web map `mapa_hydro_mwp`, and issued under the open-data act.
  - „Prawo do udostępnianych informacji przysługuje Skarbowi Państwa.”
  - The user must inform „o źródle, czasie wytworzenia i pozyskania informacji publicznej”.
  - Whoever processes the information must state „fakt przetworzenia informacji, a w szczególności … czy wykorzystuje informacje w całości czy we fragmentach”: „Informacja o przetworzeniu musi zawierać pełne dane co do zakresu przetworzenia”. They must also inform recipients „o pełnej treści warunków wykorzystywania informacji, w szczególności … zakresu odpowiedzialności”.
  - The terms are an offer for information „w systemie teleinformatycznym PIG-PIB … w centralnym repozytorium informacji publicznej”, accepted by use.
  - Use is free „co do zasady”. The fee for real-time access „nie stosuje się do danych dynamicznych i danych o wysokiej wartości udostępnianych przez API”.
- **PIG-PIB's website terms** (https://www.pgi.gov.pl/korzystanie-z-serwisu.html) cover the site's materials: they „można wykorzystywać do tworzenia własnych opracowań oraz do dalszego rozpowszechniania”, naming „źródło informacji - Państwowy Instytut Geologiczny - Państwowy Instytut Badawczy”.
- **The request form** prescribes a source sentence for requested data: „Opracowano na podstawie danych uzyskanych w ramach zadań państwowej służby geologicznej realizującej zadania określone w ustawie Prawo wodne”.
- **The law:**
  - Prawo wodne (Dz.U. 2026 poz. 1335):
    - art. 386 ust. 1: „Skarb Państwa jest właścicielem wszystkich informacji zbieranych i przetwarzanych przez służby państwowe”;
    - art. 386 ust. 3: IMGW-PIB and PIG-PIB „przekazują nieodpłatnie w celu ponownego wykorzystywania informacje … na zasadach określonych w przepisach ustawy z dnia 11 sierpnia 2021 r. o otwartych danych i ponownym wykorzystywaniu informacji sektora publicznego”;
    - art. 380 gives the state geological service the „bazy danych monitoringu wód podziemnych”.
  - The open-data act (Dz.U. 2023 poz. 1524), art. 15 ust. 1, allows conditions only on the source and its times, on informing about processing, on liability and on personal data.
  - The MWP data are hydrogeological information under Prawo wodne (PIG-PIB's order nr 3/2026, § 2). They are not geological information under Prawo geologiczne i górnicze (Dz.U. 2026 poz. 69), whose art. 99 ust. 1 („Prawo do informacji geologicznej przysługuje Skarbowi Państwa”) and art. 100 (free use, paid only for the purposes of ust. 2–3a) therefore do not apply.
- **Assessment:** the data may be stored, archived and served publicly. The conditions:
  - the source, with the times of creation and acquisition;
  - the fact of processing. PIG-PIB asks for its extent as well, which ECO-071 does not write into a line (open question 4);
  - PIG-PIB's terms passed on, which a link does (ECO-065).

## Where it starts (Obserwator `develop` `b5a1c1a`, 3.3.0.dev0)

- **Provider adapters (ADR-029):**
  - A provider is one module of `obserwator.providers` with its registry entries, lines and messages.
  - The providers' station-code grammars are disjoint (`store/analyses.py:703-704`; IMGW-PIB's is `^[0-9]{9}$`, `datasets.py:1877`).
- **Captures and tiers (ADR-030):**
  - Every answer is kept. A capture dataset has `archive_scope` `country_day` and Obserwator's gzip-compressed JSON Lines container.
  - The sidecar carries `tier` and `publication` for a dataset that is not verified, and `[obserwator.capture]` sets the state per source.
  - The timers live in `deploy/systemd/` and run `deploy/obserwator-jobs.sh`:
    - night at 02:30: IMGW-PIB's harvest until 05:00, then ČHMÚ's until 06:30;
    - telemetry at 06:45;
    - current hourly at :15;
    - backup on Sundays at 07:00.
- **Hourly series (ADR-031):** `time_unit` `hour`, one slot per month, `series:<key>:<YYYY-MM>`.
- **ČHMÚ groundwater (ADR-032):**
  - The kind `groundwater`, with `groundwater_kind` `bore` or `spring`.
  - The variables `H_asl` [m] and `spring_yield` [l/s] (`datasets.py:562`).
  - `time_unit` `week`: each reading at its own date, rows only at reading dates, coverage by calendar weeks (`store/series.py:1179-1192`).
  - In the GUI: the kind switch „Podziemne”, a brown diamond, a panel without „teraz”, with `H_asl` or `spring_yield` first (`gui/web/src/sections/dane.js:123`).
  - `cz.chmu.groundwater_recent` (operational, daily) is stored without a series (ADR-032 erratum).
- **Providers fed by files (ADR-033):** `source_class` `other`, the chip „Inne źródło” and the `screen-lines` of kit 1.2.0.
- **No ArcGIS client:** nothing in `src/` pages a query (`resultOffset`, `exceededTransferLimit`).
- **No intake notes:** the providers plan („Provider intake”) asks for a note per provider in Obserwator's `docs/`, and none exists yet (ČHMÚ groundwater's facts are in ADR-032). The table below is PIG-PIB's intake; O1 copies it into Obserwator.

| Row | PIG-PIB, Monitoring Wód Podziemnych |
|---|---|
| Identity | Państwowy Instytut Geologiczny – Państwowy Instytut Badawczy, Warsaw, PL, the state geological service (PSG) under Prawo wodne. Contacts: cbdg@pgi.gov.pl (the WMS), uig.cag@pgi.gov.pl (requests). Provider id `PIG`, prefix `pl.pig` (W1) |
| Terms | CC BY 4.0 by dane.gov.pl's dataset 170, and PIG-PIB's terms of reuse: the source, the times, the processing and its extent, the terms passed on. Storing, serving and redistributing are allowed |
| Access | Open ArcGIS REST without a key, 1,000 rows a page, Imperva in front, no rate stated |
| Errors | A bad query answers HTTP 200 with `{"error": {...}}`. A disabled endpoint answers HTTP 403 with HTML. An Imperva block would be HTML as well [INFERENCE: not met] |
| Stations | Layer 0: `ID` (stability unverified, R4), points in EPSG:2180 (WGS84 on request), ground elevation, type, aquifer, depths, active flag, first and last year of observation |
| Quantities | Depth to water below ground [m] (negative above ground) and spring yield [l/s], at 06:00 UTC daily (automatic points) or on Mondays (manual points). Hourly depth at automatic points, unvalidated. Chemistry yearly; the watch list of 2023 |
| Quality | Readings are checked before they enter the database. `mwp_auto` is „bez walidacji”. No flags; a missing reading is a missing row |
| History | 1965/1972 on request, free, as Excel. The service holds one month of readings and the hourly values from 2026-01 |
| Overlap | None with IMGW-PIB's or ČHMÚ's datasets. PIG-PIB's border points („Graniczny CZ…”, 77 points) are other objects than ČHMÚ's |

## Design

### Decisions proposed

| ID | Decision | Rejected alternative |
|---|---|---|
| W1 | **The provider `PIG`** (DEV-2.5, ECO-082): the national acronym of Państwowy Instytut Geologiczny without the legal suffix PIB, as IMGW-PIB is `IMGW`.<br>Names:<br>• adapter `obserwator.providers.pl.pig`;<br>• keys `pl.pig.*`, slugs `pig_*`;<br>• catalog `stations/versions/pig_stations` (slot `catalog:pl.pig.stations`);<br>• attribution origin `pig`, Nogat's data source `pig`, the regulamin's block `pig`.<br>Text for people says „PIG-PIB”. The addresses stay (`cbdgmapa.pgi.gov.pl`, `www.pgi.gov.pl`). | `PGI` / `pl.pgi.*`, the English acronym of the domain. ECO-082 rejected English acronyms: ČHMÚ is `chmu`, not `chmi`. (Open question 9.) |
| W2 | **The source class `other`** (P11). PIG-PIB runs the state geological service, not a national meteorological and hydrological service of a WMO member. Its points therefore get the dashed outline (P13), the chip „Inne źródło” and P8's notice in PIG-PIB's words: the data come from the monitoring of the state geological service, not from a hydro-meteorological service. „Niezweryfikowane” appears only with its operational tier (DEV-20.8). | `nmhs`: P11 defines it by WMO membership. A third class: P13 found three outlines unreadable at 16 px. (Open question 5.) |
| W3 | **The datasets and tiers** of the table below. The readings of the MWP database are `verified`: PIG-PIB checks them before they enter it and says they are verified at every stage of their collection. `mwp_auto` is `operational`: PIG-PIB calls it „bez walidacji”. | Every dataset `operational` (open question 3) |
| W4 | **One capture per run, kept as published and compared by content.**<br>• A sync of an `mwp` dataset pages its layer or table in one run: `orderByFields=OBJECTID`, `resultOffset`, 1,000 rows a page, `returnCountOnly` before and after. If the count changes during the run, it is retried once, then ends `partial` with nothing written.<br>• The run's answers are kept as they came in Obserwator's capture container (time, address, status, body; ADR-030 D3 erratum).<br>• A run makes one version, unless its content equals the current version's. The content form `pig-json/1` [proposed] decides: rows sorted by their key, without `OBJECTID` and paging. An equal run is `unchanged`, recorded in the observation register as seen (ADR-003 D18, as `chmu-json/1`).<br>• Layer 0's content leaves out the repeated latest reading, so a new month alone makes no new station version. | A version per day: the same month's bytes thirty times. Comparing bytes: a reload renumbers `OBJECTID`, which changes no data. HTTP signals: there is no `Last-Modified`, and the `ETag` follows the bytes. |
| W5 | **Months, replacement and gaps.**<br>• A readings version is named by the calendar month of its rows: `MWP_<YYYY-MM>.jsonl.gz`, slot `archive:pl.pig.groundwater_readings:MWP_<YYYY-MM>.jsonl.gz` (`archive_scope` `country`, as the telemetry's monthly zip).<br>• The same month found again is `unchanged`.<br>• The same month with other rows is a new version of its slot. The older version is kept, and the notice `month_republished` counts the readings changed, added and removed.<br>• A new month is a new slot.<br>• Rows of more or less than one calendar month name the file by their first and last dates, `MWP_<first>_<last>`, with the warning `window_unexpected`.<br>• `store check` reports `not_captured` for every month between the first and the last captured that has no version. Such a month is a gap no capture can fill, only a request (open question 8). | Slots by the day of the capture: a month would be spread over thirty slots. |
| W6 | **The station catalog**, from the newest `pl.pig.groundwater_stations`:<br>• **Code:** `ID`, grammar `^[1-9][0-9]{0,5}$`, disjoint from the nine digits of IMGW-PIB, ČHMÚ's WIGOS ids and `<ID>-<code>` of ADR-033.<br>• **Kind:** `groundwater`, with `groundwater_kind` `spring` for „źródło” and `bore` for every other type, blank included. The type as published is kept.<br>• **Name:** `MIEJSCOWOSC`.<br>• **Other fields:** `active` from „Tak”/„Nie”; `elevation_m` = `RZEDNA_TERENU`; the location from the server's WGS84 point.<br>• **`hydrogeology`**, an optional object, additive under ECO-085: confinement, stratigraphy, lithology, medium, bore and final depths, the water struck and at rest, screen top and bottom, the years observed, JCWPd, PSH's and CBDH's numbers, the EU code, the kinds of monitoring and whether the point is automatic.<br>• **Notices:** a reading of a point the catalog lacks is kept with `station_unknown` (5 points in October). An `ID` whose CBDH number or point changed between versions gives `station_identity_changed` (R4). | PSH's number (empty at 109 measured points). The CBDH number (empty or repeated). `PIG-<ID>` (a prefix PIG-PIB's map does not show). |
| W7 | **The readings series `pl.pig.groundwater_readings`**, one dataset, `time_unit` `week` in ADR-032 D2's sense: each reading at its own date, rows only at reading dates, coverage by calendar weeks.<br>• **Variables:**<br>&nbsp;&nbsp;– `depth_to_water` [m] as published („m p.p.t.”), positive below the ground and negative above it;<br>&nbsp;&nbsp;– `H_asl` [m] = `elevation_m − depth_to_water`, derived from the catalog version the build reads. That version is named among the series' inputs, so a changed ground elevation makes a new series version;<br>&nbsp;&nbsp;– `spring_yield` [l/s].<br>• **Dates:** a reading's date is the reading of 06:00 UTC. `year_type` is hydrological, November–October, as PSG's yearbooks.<br>• **Coverage:** the known periods are the months captured. A month never captured is unknown, not a gap. A calendar week without a reading inside a known month is a gap.<br>• **Precedence:** for each point and date the newest version holding it wins; the others stay (E5 of the operational-series plan). | Two datasets, daily and weekly. PIG-PIB publishes no regime per point, 293 daily points are not in the automatic list, and a point's regime changes over the years (automation since 2021).<br>`day` with a filled calendar: six false gaps a week at the 334 manual points. |
| W8 | **The hourly series `pl.pig.groundwater_subdaily`** (ADR-031), built from `pl.pig.groundwater_operational`: `time_unit` `hour`, one slot per month, `depth_to_water` and the derived `H_asl`, one tier, `operational`.<br>• It is never joined to, nor aggregated into, the readings series (DEV-20.8). The daily reading is the 06:00 hour rounded to the centimetre, so precedence over the hours would leave a step every morning.<br>• Identical duplicated rows count once. Differing duplicates: the later `OBJECTID` wins, with a notice.<br>• Times outside the captured day (2136) stay in the capture and leave the series with a notice. | The 06:00 readings put in place of the hourly values |
| W9 | **The time of the automatic measurements.**<br>• The parser takes each returned epoch to its Europe/Warsaw wall time and reads that time as UTC (Facts).<br>• The night's harvest selects each UTC day by stored time.<br>• On the March night, where two rows share one epoch, it asks for the stored hour 02 by a clause of its own. Any other collision is a notice, never a guess. | Trusting the epochs: an hour off in winter, two in summer |
| W10 | **The publication state:** `pl.pig.groundwater_operational` is `public` by default (CC BY 4.0). The verified datasets carry no state (ADR-030 D6). | `private` |
| W11 | **The timers** (ECO-084, P16; the units of `deploy/systemd/` unchanged, `deploy/obserwator-jobs.sh` extended):<br>• **night:** PIG-PIB's harvest first, `--pace-until 02:45`, about 20 requests of the closed UTC days since the last whole harvest, then the hourly series of the months touched. IMGW-PIB until 05:00 and ČHMÚ until 06:30 follow as now.<br>• **telemetry, 06:45:** `store sync` of `pl.pig.groundwater_stations` and `pl.pig.groundwater_readings` every day; on Mondays also `…_chemistry` and `…_watchlist`. When a new version arrives, the catalog and the readings series are built.<br>• **Pacing:** at most one request per 2 s, gzip, the `User-Agent` of 3.1.0, backoff on 429 and 5xx.<br>• **Failed answers:** an `{"error"}` answer or one that is not JSON (an Imperva page) is `source_unavailable`, and nothing is written.<br>• **Declared rates:** the adapter declares a day for the readings and the points and a week for the chemistry. | A timer of its own: a monthly set is checked daily like the telemetry's zip |
| W12 | **The GUI:**<br>• **„Podziemne”:** PIG-PIB's 3,505 points (1,505 active) beside ČHMÚ's 1,884 objects, as brown diamonds with the outline of their class.<br>• **„Stacja”:** the name, `ID` and PSH's number, the type, `hydrogeology`, the ground elevation, the badge and P8's notice.<br>• **„Dane”:** the readings, with `H_asl` first for a bore and `spring_yield` for a spring, and `depth_to_water` in the table and the downloads. For an automatic point, the hourly series follows, labelled „dane operacyjne, niezweryfikowane”.<br>• **Not added:** „teraz” and analyses, as for ČHMÚ's objects.<br>• **Elsewhere:** the guide („Instrukcja”) and the info texts (DEV-15.14) name the quantities, the sign and the 06:00 UTC reading. | `depth_to_water` charted first: depth drawn downward needs a reversed axis, which the kit's chart module (`2026-11-24-unified-charts.md`, Obserwator `v3.5.0`) does not have; a request |
| W13 | **Downloads**, each carrying W, WP and RG (DEV-20.5):<br>• `series export` of both series as CSV, JSON or Parquet, e.g. `obserwator_series_pl.pig.groundwater_readings_6495.csv` (DEV-19.21);<br>• `stations export --kind groundwater` with `hydrogeology`;<br>• `datasets files|download` of the four `mwp` datasets as plain files: the pages as published with `ATTRIBUTION.txt` (DEV §19);<br>• raw versions through Archiwista as any archive version. | — |
| W14 | **Lines, terms, regulamin, registry** (Nogat, step N1). See „Lines and terms” below. | — |
| W15 | **The interim capture and its import.** See „S0” below. | Waiting for the release: every month until then lost |

### Datasets

| Dataset | Source | Tier | `time_unit` | `archive_scope` | One version holds | Built into |
|---|---|---|---|---|---|---|
| `pl.pig.groundwater_stations` | `mwp` layer 0, `outSR=4326` | verified | `station_list` | `country` | the pages of one run | the catalog `pig_stations` |
| `pl.pig.groundwater_readings` | `mwp` table 1 | verified | `week` | `country`, one file per month (W5) | the pages of one publication of the month | the readings series (W7) |
| `pl.pig.groundwater_chemistry` | `mwp` table 2 | verified | `snapshot` | `country` | the pages of one run | nothing in this plan |
| `pl.pig.groundwater_watchlist` | `mwp` table 3 | verified | `snapshot` | `country` | the page of one run | nothing in this plan |
| `pl.pig.groundwater_operational` | `mwp_auto` layer 0 and table 2 | operational | `hour` | `country_day` | the night's answers for one closed UTC day | `pl.pig.groundwater_subdaily` (W8) |
| `pl.pig.groundwater_subdaily` | built | operational | `hour` | — (series, `series:<key>:<YYYY-MM>`) | — | — |

`mwp_auto`'s table 1 (raw temperature and pressures, a month ending 2026-09-25) is not fetched (open question 6).

### Load and storage

| Item | Requests | On the wire | When |
|---|---|---|---|
| `mwp` layer 0 and table 1 | 33 | 0.8 MB | daily |
| `mwp` tables 2 and 3 | 55 | 0.8 MB | Mondays |
| `mwp_auto` layer 0 and one UTC day | about 20 | 0.25 MB | nightly |
| Backfill of `mwp_auto` from 2026-01 | about 5,800 | about 80 MB (14 KB a page) | once, at night, at most one request per 5 s (open question 7) |

- **Raw root:** about 70 MB a year, almost all of it `mwp_auto`'s nights. The readings add 12 versions of about 0.3 MB, and the points and the chemistry change a few times a year.
- **Data root:** under 0.1 GB [INFERENCE].
- **Backup:** the weekly copy grows by a few MB (D10 of the operational-series plan).

### Lines and terms (Nogat, step N1)

- **The licence:** CC BY 4.0 by dane.gov.pl's dataset 170, which lists this very service. PIG-PIB's own terms are linked by a terms line, as ECO-088 let CAMELS-PL's Zenodo record govern (open question 4).
- **A row of the table of provider lines** [proposed]. Its order is 8, after D, so G, SG and Z become 9 to 11 and keep their relative order:
  - **W:** „Źródło danych: Państwowy Instytut Geologiczny – Państwowy Instytut Badawczy (PIG-PIB), Monitoring Wód Podziemnych państwowej służby geologicznej (wytworzono `<period>`, pozyskano `<date>`), licencja CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)”;
  - **WP:** „Dane PIG-PIB zostały przetworzone”, fixed, as ECO-071 requires;
  - `<period>` and `<date>` take G's forms: the dates of the readings used, and the days of the captures.
- **The short form WK** „Źródło: PIG-PIB, CC BY 4.0”, „PIG-PIB” linked to https://www.pgi.gov.pl/psh and „CC BY 4.0” to the licence. The kit's `LINES`, `SCREEN` and `SHORT_LINKS` gain it.
- **The terms line RG:** „Regulamin danych PIG-PIB: https://www.pgi.gov.pl/rejestry-i-bazy-danych-geologicznych/zasady-korzystania-z-isp.html”.
- **A new rule of DEV §20** [proposed], numbered when it lands (DEV-20.12 is the last on `develop` on 2026-11-24): „A product with PIG-PIB data (the points, readings and automatic measurements of its Monitoring Wód Podziemnych) or results derived from them carries W, and WP once they were processed, and the terms line RG.”
- **Amendments:** DEV-20.7 names RG; DEV-20.8 names PIG-PIB's automatic measurements without validation among the operational data.
- **The regulamin's block `pig`**, in `nogat-terms.md` and in the operator's draft `nogat-terms-operator.md`, added in place as `camels-pl` was (ECO-086), or within regulamin 1.1 if Goniec's N1 has raised it first:

  ```
  <!-- block: pig -->
  ### PIG-PIB: monitoring wód podziemnych

  > Źródło danych: Państwowy Instytut Geologiczny – Państwowy Instytut Badawczy (PIG-PIB), Monitoring Wód Podziemnych
  > Dane PIG-PIB zostały przetworzone

  Regulamin danych PIG-PIB: <https://www.pgi.gov.pl/rejestry-i-bazy-danych-geologicznych/zasady-korzystania-z-isp.html>
  Licencja CC BY 4.0: <https://creativecommons.org/licenses/by/4.0/>
  <!-- /block -->
  ```

- **`ecosystem.yaml`:**
  - the data source `pig`:
    - name „PIG-PIB (Monitoring Wód Podziemnych of the state geological service: points, groundwater readings, automatic measurements)”;
    - country PL;
    - url https://cbdgmapa.pgi.gov.pl/arcgis/rest/services/hydrogeologia/mwp/MapServer;
    - licence „CC BY 4.0 (dane.gov.pl dataset 170); PIG-PIB's terms of reuse”;
  - `pig` in Obserwator's `data_sources`;
  - `pig-json/1` in Obserwator's `provides`;
  - PIG-PIB named in the summaries of `obserwator-store/1`, `obserwator-archives`, `obserwator-data/1` and Archiwista's `archiwista-raw-root`;
  - `docs/ECOSYSTEM_MAP.md` and `AGENTS.md` regenerated. No new route: Obserwator's routes already name `store sync`, `series read` and `series export`.
- **ECO-0NN,** the next free number when it lands: PIG-PIB as a source, with the licence, the tiers, the class and the lines above. Its rejected alternatives are those of this plan's questions.
- **The requested history:** data received by request (open question 8) carry the request form's sentence as a line of its own, added to the table when they enter.

### S0: the interim capture (before the release)

- **What runs:**
  - The user timer `pig-capture.timer`, daily at 07:15 local, `Persistent=true`, runs a script of about 60 lines: `curl`, or Python's standard library. It uses no Obserwator code and writes in no store.
  - The script and its output live in `/mnt/magazyn/agent-tmp/obserwator-staging/pig/`, beside the raw root on the NAS, never inside a root.
- **Each run fetches:**
  - `mwp` layer 0 (with `outSR=4326`) and table 1, every day;
  - tables 2 and 3, on Mondays;
  - `mwp_auto` layer 0 and the table 2 rows of the closed UTC days since the last run, selected by stored time.
- **How it writes:**
  - One request per 2 s, with the probe's `User-Agent`.
  - Every answer as it came, created only, never overwritten: `<run UTC time>/<dataset>/page-NNNN.json`.
  - `manifest.jsonl` records the time, address, HTTP status, selected headers, size, SHA-256, and `returnCountOnly` before and after. A run whose counts differ is marked `incomplete`, and the next day repeats it.
- **Its first run** is the probe's capture of 2026-11-24 (`~/data/tmp/pgi-probe-2026-11-24/raw/`), copied in as found. It holds October 2026, the only copy once December's swap comes.
- **Backup:** the weekly `obserwator-backup` copies the staging with the roots.
- **The import (O4):**
  - `obserwator store import --staging DIR` [proposed; the ADR decides the form] reads the runs in time order and checks every page against its manifest's SHA-256. It writes each run as W4 and W5 would have written it that day: `downloaded_at` is the run's time, and the sidecar names the run.
  - `--check` plans it; a second import is `unchanged`.
- **Retirement:** S0's timer stops after the release's timers have captured a whole month themselves. The staging stays until the author removes it (D4 of the operational-series plan).

## Release

**Recommended: Obserwator `v3.3.0`,** beside Gdańskie Wody and the provider fed by files (open question 2):

- **The release date loses no data:** from S0 on, no month depends on it, and O4 takes the staging in.
- **It fits that release's purpose:**
  - PIG-PIB is the providers plan's own „next provider” (its open question 5).
  - It needs what `v3.3.0` brings: the source classes P11–P13, its class `other`, and a second adapter written against ADR-029 beside Gdańskie Wody's.
- **It blocks nothing:** its terms are known today (CC BY 4.0), while Gdańskie Wody still waits for its regulamin. If that is still missing when PIG-PIB's steps are done, the author may release `v3.3.0` with PIG-PIB and the provider fed by files and move Gdańskie Wody on. P11–P13 then come with PIG-PIB, whose class `other` keeps „Inne źródła” from being empty (the providers plan's reason to ship them with a provider).
- **A separate minor would be later or would renumber:**
  - Inserted before CAMELS-PL, it would renumber `v3.4.0` (ECO-086), the charts' and base maps' `v3.5.0` and Goniec's `v3.6.0`, all approved.
  - Placed after them, it waits for `v3.7.0`, which the Latarnik plan takes for its O1 at the earliest. That leaves S0's staging growing for months and `mwp_auto`'s 2026 record unguarded unless S0 backfills it (open question 7).

## Steps

Each step runs in its own session and branch under the project's `CLAUDE.md` (DEV-3.4, DEV-17.5), records its decisions as ADRs (DEV-17.2) and runs long jobs as user units (DEV-17.6). Nothing but S0 starts before this plan's `Approved:` line.

| # | Project | Change | Depends on | Verified by |
|---|---|---|---|---|
| S0 | Operator, with the author's approval (question 1), before the `Approved:` line | The interim capture and its first run from the probe (S0) | — | The first runs' manifests: every answer HTTP 200, the counts equal before and after; October 2026 in the staging; the next weekly backup holds it |
| N1 | Nogat, `feat/pig-groundwater` | ECO-0NN; DEV §20's rows W/WP, WK and RG; the new rule of DEV §20; DEV-20.7 and DEV-20.8 amended; the kit's `LINES`, the block `pig` in both templates (`standard --write` regenerates `nogat-terms.html`), the kit's version by the rule of 2026-11-24; `ecosystem.yaml` (the data source, `data_sources`, `pig-json/1`, the summaries); map and agents regenerated; the changelog of `standards/README.md`, CHANGELOG, PROGRESS | `Approved:` | The gate; `ecosystem.py validate`, `map --check`, `agents --check`, `standard` |
| O1 | Obserwator `v3.3.0` | The ADR „PIG-PIB groundwater” (W1–W15) and the intake note in `docs/`; the provider `PIG` and its six datasets declared in `_PENDING` (ADR-030 D8); the variable `depth_to_water`; the code grammar; P8's notice; messages pl/en | N1 | The ADR's review; `datasets(pending=True)` lists them; every other provider's bytes unchanged |
| O2 | Obserwator | The ArcGIS client in `fetch.py` (paging, counts, `outSR`, gzip, pacing, `{"error"}` and non-JSON answers); the adapter `pl/pig.py`: `store check\|sync` of the four `mwp` datasets (W4, W5), the night's harvest of `pl.pig.groundwater_operational` (W9), `pig-json/1`, `datasets files\|download` | O1 | Tests 1–13 on the answers recorded on 2026-11-24; a live sync into a throwaway root |
| O3 | Obserwator | The catalog `pig_stations` (W6) and both series (W7, W8); the fixture variant `groundwater_pl` [proposed] | O2 | Tests 14–18; the variants `complete_pl_cz` and `groundwater` byte-identical |
| O4 | Obserwator | `store import --staging` (S0) | O2 | The probe's run imported as October 2026's version with its time; a second import `unchanged` |
| O5 | Obserwator | GUI (W12) and downloads (W13); the strip's WK and the dialog's W, WP and RG | O3; P11–P13 of `v3.3.0` | Test 19 (e2e) |
| O6 | Obserwator | `obserwator-jobs.sh` (W11), the deployment guide's „Timers”, README (DEV-18.5: the readings exist at the source for one month) | O2, O3 | A night and a telemetry run on the test instance; the spacing of requests in the log |
| A1 | Archiwista, its next minor only if needed | A contract test with `obserwator.testing`'s PIG fixture: a third provider, `depth_to_water`, a `week` series of a second provider, an operational capture of PIG-PIB. Code only if its adapter or GUI names providers (ECO-085) | O3 | Test 20; `archiwista doctor` 0 errors |
| D1 | Operator, with the author's approval | Archiwista first if A1 changed code; Obserwator `v3.3.0`; O4's import of the staging; the timers; the backfill (question 7) unless S0 did it; S0 stopped after the release's first whole month | all | A week of captures; the next swap of the month captured and versioned |

## Tests

On fixtures recorded from the live services on 2026-11-24 (cut to a few points), unless marked otherwise:

1. „ 2026-10-01” is read as 2026-10-01; the capture keeps the space.
2. A negative depth stays negative, and `H_asl` = `elevation_m − depth_to_water` at an artesian point.
3. A yield row gives `spring_yield` without a depth.
4. A reading of an unknown point (9390) stays in the series with `station_unknown`.
5. The geometry of `outSR=4326` locates a point, not `WSP_X_1992`/`WSP_Y_1992`.
6. „źródło” → `spring`; blank and every other type → `bore`; „Tak”/„Nie”/null → `active`.
7. Content comparison:
   - a reload with renumbered `OBJECTID`s and pages in another order is `unchanged`;
   - one changed value is a new version with `month_republished` counting 1.
8. Rows of two months name the file by their dates, with `window_unexpected`.
9. A count that changes during the run: one retry, then `partial` with nothing written.
10. An HTTP 200 answer of `{"error": …}`, and an HTML answer, are `source_unavailable` with nothing written.
11. `mwp_auto` time, against 6495's recorded days:
    - 2026-10-20 (CEST) and 2026-10-30 (CET): the 06:00 UTC hour equals the MWP reading;
    - 2026-03-29: the two rows at one epoch become 01:00 and 02:00 by the stored-hour query;
    - 2026-10-25: 24 distinct hours.
12. Identical duplicated rows count once; differing ones keep the later `OBJECTID`, with a notice.
13. Times in 2136 stay in the capture and leave the series with a notice.
14. `store check` names a missing month between two captured ones `not_captured`.
15. `datasets list` lists the six datasets with tier, `time_unit` and `archive_scope`; `AGENTS.md` and `llms.txt` stay within their budget.
16. `stations find --provider PIG --kind groundwater` finds 6495 with `hydrogeology`.
17. `series read|export` of `pl.pig.groundwater_readings` at 6495, a weekly bore and a spring:
    - rows at reading dates, gaps by calendar weeks;
    - `attribution` W, WP and `terms_notice` RG, in the CSV's last two columns and in Parquet's metadata.
18. `pl.pig.groundwater_subdaily` of 6495 for 2026-11: hourly, tier `operational`, never in the readings series.
19. GUI (e2e):
    - a PIG-PIB bore and spring in „Podziemne” with the dashed outline;
    - the panel's `hydrogeology`;
    - the chart's `H_asl`;
    - the hourly series labelled „dane operacyjne, niezweryfikowane”;
    - the strip with WK and the dialog with W, WP and RG;
    - a download carrying them.
20. Archiwista's contract test on the PIG fixture.
21. `@pytest.mark.live`, skipped offline: one page of each `mwp` layer and table, and one hour of `mwp_auto`.

## Acceptance

1. **The daily capture:** after a day of the release's timers, the raw root holds:
   - the night's version of `pl.pig.groundwater_operational` for the closed UTC day;
   - the current month's `pl.pig.groundwater_readings` version, or an `unchanged` record of it;
   - every answer as it came, with a sidecar whose address carries no credential.
2. **A month replaced:** when PIG-PIB swaps the month, the next 06:45 run writes the new month's slot. The previous month keeps its last version, and the readings series covers both months.
3. **A repeated sync:** a second sync of the same month is `unchanged`. A changed month is a new version, with the notice counting the changes.
4. **The import:** October 2026, from S0's staging, is a version of `pl.pig.groundwater_readings` dated 2026-11-24. `series read --dataset pl.pig.groundwater_readings --station 6495` gives its 31 readings.
5. **Gaps:** `store check` lists `not_captured` months, if any.
6. **The GUI and the downloads** show PIG-PIB's points and series with W, WP, WK and RG as DEV-20.5 places them.
7. **No other change:** the other providers' fixture bytes, Hydrolog and Archiwista's suites pass unchanged, Archiwista with A1 where needed.
8. **The load:** no more than one request per 2 s to `cbdgmapa.pgi.gov.pl` (the jobs' log).

## Risks

- **R1. An unlisted interface.**
  - dane.gov.pl lists the WMS, not the REST query of the same service. The REST service's HTML directory is off, and its layout or its window may change without notice.
  - Each run checks counts and fields and refuses an unknown layout with a notice. S0's manifests show a change on the day.
- **R2. Imperva.** It already refuses `curl` on `www.pgi.gov.pl`.
  - Mitigation: one request per 2 s and a stable `User-Agent`. A block is `source_unavailable` and the next day retries.
  - Only a block longer than the month's window loses data, and a request (question 8) recovers it.
- **R3. The day of the swap is unknown.** A capture that fails for a whole month loses that month publicly.
  - Mitigation: `store check` reports `not_captured`.
  - A log record and a `config show` problem appear when the last successful `mwp` capture is older than 7 days [proposed].
- **R4. `ID` stability is unverified.** A renumbering would split records. W6 compares each `ID` with its CBDH number and point between versions.
- **R5. The time base of `mwp_auto`** (W9). A change on PIG-PIB's side would move every hour; test 11 on live data at each release.
- **R6. Revisions after the window.** PIG-PIB's verification „na każdym etapie” may change a month after it leaves the service, which only a request shows [INFERENCE: not observed].
- **R7. The vertical datum of `RZEDNA_TERENU` is not stated.** `H_asl` is labelled „m n.p.m.” without a datum name. The datum stays an item of the intake note until PIG-PIB states it.
- **R8. The extent-of-processing clause** of PIG-PIB's terms against ECO-071 (question 4).
- **R9. The 2026 hourly record of `mwp_auto`** may be cut before it is backfilled (question 7).
- **R10. The staging of S0 lies outside every store.** The backup covers it, and O4 checks every page against its manifest.

## Open questions (with recommendations)

1. **Start S0 now, before this plan's approval?**
   - *Recommended:* yes, today.
     - October 2026 is captured already (the probe), and November replaces it within weeks.
     - S0 writes in no store and changes no project, so DEV-17.4's „code starts only after that line” binds the steps, not this operator's job. It is the author's approval in session, as for any job on his machine.
2. **Release: `v3.3.0` or a separate minor?**
   - *Recommended:* `v3.3.0` (Release). If Gdańskie Wody's terms are still missing when PIG-PIB's steps are done, release `v3.3.0` without Gdańskie Wody.
3. **The tier of the MWP readings: `verified` or `operational`?**
   - *Recommended:* `verified`. PIG-PIB checks them before they enter its database of record, says they are verified at every stage, and labels only `mwp_auto` „bez walidacji”.
   - The yearbook is no later verified source for the readings, since it holds aggregates only.
   - `operational` would label PSG's checked database „niezweryfikowane” on every surface.
4. **Which terms govern?**
   - *Recommended:* the CC BY 4.0 of dane.gov.pl's record, which lists this service, as ECO-088 let the Zenodo record govern. The fixed WP (ECO-071) and the terms line RG pass PIG-PIB's terms on by a link (ECO-065).
   - Add a short courtesy question to cbdg@pgi.gov.pl on whether this meets their extent-of-processing clause. It blocks nothing.
   - The alternative is a processed line naming the extent („wybór punktów i okresu, zmiana formatu, rzędna obliczona z głębokości i rzędnej terenu”), an exception to ECO-071.
5. **The source class: `other` or `nmhs`?**
   - *Recommended:* `other`, by P11's own definition (W2).
   - PSG is a state service, which P8's notice says in PIG-PIB's words, but it is no WMO hydro-meteorological service.
6. **Scope of tables 2 and 3 and of `mwp_auto`'s table 1?**
   - *Recommended:* tables 2 and 3 as raw versions only, served as other raw versions, with no series or GUI until a later plan on water quality.
   - Those tables are small, change yearly and mostly hold GIOŚ's PMŚ results, whose own series is published at mjwp.gios.gov.pl.
   - `mwp_auto`'s table 1 is not fetched: raw pressures from which PIG-PIB derives table 2, one month, last written on 2026-09-25.
7. **Backfill `mwp_auto` from 2026-01 (about 5.8 million rows, about 5,800 requests)?**
   - *Recommended:* yes, once, by S0 at night at one request per 5 s (about 8 h over two or three nights), into the staging, for O4 to import.
   - The service documents no retention, and the record is the only public one longer than a month.
8. **File a request for the history?**
   - *Recommended:* yes, by the author, since it needs his identity (ePUAP, a qualified signature or a trusted profile).
   - Ask for Załącznik nr 1 – MWP: the readings of every point for every year, as Excel, free.
   - The files enter later as a verified dataset `pl.pig.groundwater_requested` [proposed], with the request form's sentence as their line. A later step designs this once their form is known.
9. **The names: `PIG` and `pl.pig.*`, or `PGI` after the domain `pgi.gov.pl`?**
   - *Recommended:* `PIG`, by DEV-2.5 and ECO-082's rule of the national acronym. `pgi` stays in PIG-PIB's addresses.
   - DEV-2.5 counts „a part of a file name” as well. This plan's file and branch were named `pgi-groundwater` when it was drafted and may become `pig-groundwater` when it merges.

## Follow-ups (outside this plan's steps)

- **A plan on water quality:** series of PSG's and PMŚ's chemistry and of the watch list, with GIOŚ's terms checked.
- **The requested history and its import** (question 8).
- **A depth chart drawn downward,** once the kit's chart module has a reversed axis (a request to `2026-11-24-unified-charts.md`).
- **Goniec's collections** (`v3.6.0`) list PIG-PIB's points like the other providers'.
- **A live tail of the automatic points** (the hours since the night's harvest), if wanted.
- **Other PSG services in the same folder,** not proposed: `podtopienia` (groundwater flooding), `cbdh_otwory`, `pobory`, `gzwp`, `jcwpd`.

## Results

None yet (draft).
