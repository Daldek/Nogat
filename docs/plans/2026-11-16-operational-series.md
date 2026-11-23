# Plan: operational hydro series of IMGW-PIB and ČHMÚ, captured nightly by Obserwator's timers

Approved: 2026-11-23, Fable for the author (delegated in session: „Oddeleguj przegląd planów do Fable i jeżeli będzie mieć uwagi - zaktualizuj plan. Fable daje approve.”; the review and its decisions 1–24: `~/workspace/wt/logs/fable-obserwator-3.2.0.md`)

Status: approved 2026-11-23 (Fable for the author; the review and its decisions: `~/workspace/wt/logs/fable-obserwator-3.2.0.md`); the first joint release is done (`v0.1.0` of 2026-11-17, `v0.2.0` of 2026-11-22); code starts with N0 (HUB-5.2). The facts below were probed on 2026-11-16 against Obserwator `f4f6a8d`; where 3.1.0 changed them (ADR-024 to ADR-028: the names `IMGW`/`CHMU`, the slugs `imgw_*`/`chmu_*`, no `Referer`, the data root `~/data/obserwator-310/data`) and where the decisions of 2026-11-23 amend the design, those take precedence. The design marks its own proposals „[proposed]”.

Requirements: DEV-17.4, DEV-17.5 and DEV-3.4 (each project in its own session and branch), DEV-17.2 (each project records its decisions as ADRs), DEV-3.3 (merges with the author's approval), DEV-17.6 and ECO-073 (long jobs outside the agent's session), DEV-18.5 (store backups), DEV-20.1, DEV-20.5, DEV-20.8 (amended by N0), ECO-059 (raw data in Archiwista, harmonized in Obserwator; as amended by ECO-084: the timers write the raw root, the backup is the deployment's), ECO-060, ECO-072 (released formats change only with the author's consent), ECO-084, ECO-085, AGI-3.4.

## Goal

- „Pomiary bieżące” in Obserwator's GUI gets a chart like the station page of hydro.imgw.pl, with water level H, discharge Q and water temperature T over the recent weeks.
- Obserwator keeps its own record of the current period: unverified operational data harvested every night for all stations, replaced month by month by IMGW-PIB's telemetry. The result is one continuous record from the verified archive up to yesterday.
- The same is done for ČHMÚ.
- Meteorological telemetry and ČHMÚ's climate `now`/`recent` data are a separate, later plan (Q7).

## Facts (probed 2026-11-16)

Probe files are in `/data/nmt/e2e-2026-11-15/tmp/oper-check/`. The investigation's report is `obserwator-oper.md` of that session.

### Providers

| Source | Content | Step and span | Stations | Published |
|---|---|---|---|---|
| `hydro-back.imgw.pl/station/hydro/status/data?id=<code>&hoursInterval=<h>`; `…/discharge`; `…/water-temperature` (the probe of 2026-11-16 sent `Referer: https://hydro.imgw.pl/`; since 3.1.0 Obserwator sends none and `User-Agent: Obserwator/<version> (+https://github.com/Daldek/Obserwator)`, ADR-021 erratum of 2026-11-21 — O2 keeps that) | `operational`: H, Q, T (`B00100S`) | Hourly. 10-min points only for about the last 2 hours before the request (A4). Reached back to 2026-08-16 with `h=2200`; the terms promise „do 6 tygodni wstecz” | H about 878, Q about 659–682, T about 81–83 | live |
| `danepubliczne.imgw.pl/datastore/getfiledown/Arch/Telemetria/Hydro/<YYYY>/Hydro_<YYYY-MM>.zip` | CSV `KodSH;Param;YYYY-MM-DD HH:MM;value` for `B00020S` (H), `B00050S` (Q), `B00100S` (T); `999` means missing | 10 min, UTC. One zip per month for all stations (October: 17.6 MB) | 878 / 682 / 83 | about 12 days after the month (October built 2026-11-12); November not yet |
| `danepubliczne.imgw.pl/data/dane_pomiarowo_obserwacyjne/dane_hydrologiczne/` (Obserwator's `pl.imgw.hydro_*`) | verified daily, monthly and semi-annual data | daily; no sub-daily verified set | about 900 | about 10 months after the hydrological year (2025 on 2026-08-31) |
| `opendata.chmi.cz/hydrology/now/data/<WIGOS>.json` | H, Q, `TH` (and the forecasts `H_F`, `Q_F` at some stations) | 10 min, the current UTC day | 548 | rewritten every 20 min |
| `opendata.chmi.cz/hydrology/recent/data/<YYYYMMDD>_<WIGOS>.json` | the same, one file per station and day | 10 min, from 1 January of the year | 548 (Q about 500, `TH` about 250 [INFERENCE from file sizes]) | about 00:20 UTC the next day, never rewritten (A3) |
| `opendata.chmi.cz/hydrology/historical/data/hourly/H_<WIGOS>_HQ_<YYYY>.json` | validated hourly `HH` (cm) and `QH` (m³/s), `DT,VAL` | 1 h, 8,760 values for 2025 | 543 for 2025 | 2025 on 2026-05-21 (`daily/…_DQ_2025.json` the same day) |

### Comparisons

- **Głogów 151160060 and Kłodzko 150160180, October 2026:** hydro-back's hourly `operational` values equal the full-hour records of the 10-min telemetry. Both stations: 744 of 744 for H; Głogów also for Q. Głogów's T: 22 of 22 daily readings at 06:00 UTC.
- **What this shows:** the hourly value is the full-hour sample, not a mean. A month of telemetry replaces the hourly series without changing any value.
- **Telemetry is UTC:** Kłodzko's October has exactly 31 × 144 = 4,464 records, with no extra hour on the DST night of 25 October.

### Answers to the author's questions (2026-11-16)

#### A1. What Obserwator versions today (`develop` `f4f6a8d`)

- **Raw root:**
  - Archive files with their `obserwator-meta/1` sidecar, under `archives/versions/<server dir>/<stem>/<label>_<sha8>/`.
  - Station sources (`pl.imgw.hydro_now` kept as a derived file of `kept_fields`, ADR-015 D5).
  - PMAXTP cells.
  - The observation register is no version (`docs/ARCHITECTURE.md:236-251`).
- **Data root:**
  - Series: `series.json` plus one Parquet file per station.
  - The catalogs and the analyses.
  - No separate manifest file: the sidecar of a version is its manifest, and a series sidecar holds its input manifest.
- **When a new version arises:**
  - An archive download writes a new version only when the SHA-256 differs (`new`).
  - The same bytes with the same HTTP signal are `unchanged` and not written.
  - The same bytes with a new signal are `relabeled`: a copy under the new label (`store/types.py:175-204`, labels in `store/writer.py:1704-1713`).
  - ČHMÚ bytes with the same canonical content are `unchanged`, recorded in the observation register (ADR-003 D6, D18).
  - A series build writes a new version only when its input manifest (slot and SHA-256 of every input, `store/series.py:336`, rule at `:1040-1050`, `_reusable` at `:391`) differs from the current version's. A series version rewrites every station's Parquet file (`series.py:1255`); nothing is shared between versions.
- **Slots:** a slot names one versioned thing: `archive:<key>:<file>`, `series:<key>`, `catalog:<provider>.stations`, `pmaxtp:…`, `analyses:…` (`store/reader.py:124-130`). `current_version(root, slot=…)` (`reader.py:1577`) picks the newest by Last-Modified, then the download or build time.
- **Immutability:** every version is immutable. It is published from `.incoming/` by no-replace hard links, sidecar last (`writer.py:322`, `ARCHITECTURE.md:252`).
- **Never deleted:** ADR-001 D1 (`docs/DECISIONS.md:51`, append-only) and ADR-017 D1. The reasons are reproducibility and the pins of Archiwista's projects, which `command_for_version` rebuilds from sidecars (ADR-008 D5). DEV-18.5 adds that sources remove old versions. Only stale `.incoming/` directories older than 24 h are removed (`writer.py:1068`). There is no prune command.

#### A2. Versioning of harvested operational data: see „Versioning (A2)” under Design. The recommendation is (a) plus (b) nightly, with pruning available and off by default.

#### A3. ČHMÚ validation

- **`recent` is never rewritten after publication.**
  - In the listing, every one of the 170,719 files of `hydrology/recent/data/` (20260101 to 20261115) has its modification time on the day after its date, none later.
  - `20260105_0-203-1-004200.json` still has `Last-Modified: Tue, 06 Jan 2026 00:20:18 GMT`, ETag `"695c5542-4b9d"`.
  - `20261110_0-203-1-004200.json` downloaded again 30 min later was byte-identical.
- **Where the validation goes:** ČHMÚ's description (`hydrology/hydrologicka_data_now_a_recent_popis.pdf`) says „Tato data se následně kontrolují a validují. Po uplynutí jednoho kalendářního roku jsou postupně nahrazena daty historickými.” The validated set is published once a year as `hydrology/historical/data/hourly/` (HQ) and `daily/` (DQ). Year 2025 was published on 2026-05-21; 2024's files carry 2025-07-01.
- **Consequence:** no refetch of `recent`. The validated hourly set is the verified tier for ČHMÚ (D5).

#### A4. The 10-min tail of hydro-back

In every probe the 10-min points begin about 2 h before the request; before that there are only full hours.

| Request | 10-min from | Last point | Probe file |
|---|---|---|---|
| ~09:28Z | 07:30 | 09:20 | `hb_status_data.json` |
| ~09:38Z | 07:40 | 09:30 | `cmp_151160060_status_data.json` |
| ~09:56Z | 08:10 | 09:50 | `sd25.json` |

The same holds for `discharge` and `water-temperature`. A night run after 00:00 UTC + 2 h therefore sees the closed UTC day in full hours only.

### Terms of use

The texts were read on 2026-11-16. They give no blocker, and none was contacted (decision 6). The flags stay in Risks.

- **hydro.imgw.pl** (`https://hydro.imgw.pl/#/regulamin`; the text is in `https://hydro.imgw.pl/assets/i18n/pl.json`, key `REGULATIONS`):
  - „Udostępnia dane operacyjne do 6 tygodni wstecz.”
  - „Użytkownik może używać nieodpłatnie udostępnionych informacji jedynie do celów prywatnych.”
  - Use „dla potrzeb działalności gospodarczej, na stronach internetowych zawierających reklamy lub do celów: … badania elementów hydrologicznych … na potrzeby planowania w gospodarowaniu wodami … bez zawarcia umowy” is a breach of art. 385 ust. 5 Prawa wodnego.
  - Nothing on automated retrieval, rate or storage.
- **danepubliczne.imgw.pl** (`https://danepubliczne.imgw.pl/pl/regulations`):
  - § 1 „Przyjęcie oferty następuje poprzez przystąpienie do korzystania”.
  - § 5 ust. 1 „do celów prywatnych, a w przypadku danych o wysokiej wartości w każdym celu”.
  - § 6 ust. 3 „Część udostępnianych danych może stanowić dane niezweryfikowane”.
  - § 8 ust. 2: a request may ask for use „w sposób stały i bezpośredni w czasie rzeczywistym”.
  - The telemetry's `opis_1.1.txt`: „należy traktować jako dane operacyjne”.
- **ČHMÚ** (`https://www.chmi.cz/o-chmu/produkty-a-sluzby/data-a-vyhodnoceni`): „Otevřená data ČHMÚ můžete využívat bezplatně při respektování licence Creative Commons BY 4.0”. The same page announces an „API rozhraním pro automatické stahování”.

## Where it starts

- **DEV-20.8** (`standards/DEVELOPMENT_STANDARDS.md:1131`) and ECO-060 (`standards/DECISIONS.md:1191`): operational data of hydro.imgw.pl are „never stored or presented as archive”.
- **Obserwator:**
  - ADR-015 D5 (`docs/DECISIONS.md:749`): „danych operacyjnych nie archiwizujemy”. ADR-003 D4 (`:227`): ČHMÚ `now`/`recent` are out of scope.
  - `current hydro` and `current hydro-states` are live snapshots (`src/obserwator/commands.py:748-837`).
  - `_hydro_details` already asks hydro-back once per station (`src/obserwator/stations.py:546-604`).
  - The GUI reads the data root only (ADR-013 D5) and keeps live snapshots in memory for 10 min (`gui/_live.py:79-110`).
  - Series are daily only (`commands.py:163-167`, `store/series.py:819-879`).
  - There is no pacing in the library (`fetch.py:77-90`).
- **Archiwista (`develop` `800231c`):**
  - Downloads run as `download` jobs in its queue (`src/archiwista/jobs/supervisor.py:569`), in a worker process per job. They call Obserwator's `store sync` through `obserwator.run_command` (`adapter/obserwator/actions.py:95`, `:241-308`; `jobs/worker.py:740-885`).
  - At most 2 network jobs run at once (`supervisor.py:161-162`). A position another active download holds is skipped as `taken` (ADR-047).
  - `ScanScheduler` (`jobs/scheduler.py:158`, tick 60 s at `:55`) plans only interval scans, warm-ups and hourly pruning. There is no calendar or time window, no recurring download and no pacing.
  - `archiwista jobs start download …` (`docs/USAGE.md:565`) submits a download and follows it to its end.
  - Archiwista has no backup feature; ECO-059's backup copy of the data root is not built. Only `archiwista state export` exists.
- **Stores today:** Nogat `docs/PROGRESS.md`, „Deployment and storage”.
  - The raw root is on the NAS, `/mnt/magazyn/agent-tmp/obserwator` (CIFS, with hard links that Obserwator's writer needs).
  - The data root is local, `~/data/obserwator-310/data` (3.1.0's layout, since 2026-11-23).
  - There is no backup timer anywhere, and only `rsync` is installed (no `restic`, no `borg`).

## Decisions (the author, 2026-11-16)

| # | Decision |
|---|---|
| D1 | Amend DEV-20.8 (step N0): operational measurements may be kept as a labelled, unverified tier. Warnings and water-state classes stay live only. |
| D2 | On-demand deltas in the GUI stay in memory only. |
| D3 | The nightly job runs in Archiwista's job queue, not as an Obserwator timer. |
| D4 | Nothing is deleted by default. A command can prune superseded versions; it is off by default. |
| D5 | Fetch ČHMÚ again after its validation if one exists. A3 found none in `recent`: the refetch is dropped, and the validated `historical` hourly set takes its place (D5 of the design). |
| D6 | No contact with IMGW-PIB before the first run. The terms flags stay in Risks. |
| D7 | Meteorological telemetry and ČHMÚ's climate data are a separate, later plan. This plan ships after the first joint release. |
| D8 | The nightly window is 02:30–06:30. |
| D9 | The nightly API harvest keeps only the 1 h step: the 10-min tail is dropped and each night is trimmed to one full day, midnight to midnight. |
| D10 | Backups of the store to the NAS: weekly incremental, monthly full. |
| D11 | The plan lives in Nogat as a cross-project plan. |

## Decisions (the author, 2026-11-22)

Recorded in the providers plan `2026-11-20-hydromet-providers.md` as P14 to P16; they change this plan:

| # | Decision |
|---|---|
| E1 | Everything Obserwator receives is kept as a capture in the raw root (P14), warnings and water-state classes and the GUI's live fetches included: D1's „warnings and water-state classes stay live only” and D2 are superseded. This plan's nightly harvest is the capture of hydro-back's hourly values, and its sub-daily series are built from the captures. |
| E2 | Whether captured data are served (shown as stored data, downloaded from Obserwator or Archiwista) is the operator's decision per source (P15); the author's service is free, without advertising and earns nothing („To nadal nie jest działalność gospodarcza”). The terms flags of hydro.imgw.pl stay in Risks for an operator who earns. |
| E3 | The polling rate follows the source (P16). |
| E4 | Releases (the author, 2026-11-22: „CAMELS przesuwa się na 3.4.0, a Gdańskie Wody wchodzą jako v3.3.0”): this plan ships with Obserwator `v3.2.0` (the captures, sub-daily series, telemetry replacement and the chart; steps O1–O4, O6) and Archiwista's minor beside it (A1, A2, A4: indexing, the nightly schedule, backups, which must run from the first capture, since the captures are the only copy of what the API forgets after 6 weeks); Gdańskie Wody is `v3.3.0`, CAMELS-PL `v3.4.0`. (A2 and A4 are Obserwator's since E9; Archiwista's minor is A1 — Fable, 2026-11-23.) |
| E5 | Replacement is precedence, not deletion (the author, 2026-11-22: „zamiast usuwać (tylko na żądanie), to podmieniamy źródło dla danego miesiąca, a to co zostało pobrane z API i tak zostaje w archiwum dla ewentualnego porównania”): when a month's telemetry (ČHMÚ: the validated year) arrives, the month's series is rebuilt from it (Precedence below), and the captured API answers stay in the raw root for comparison, never deleted. Only superseded versions of the derived series (rebuildable from the raw root) may be pruned, on demand only (D4); `store prune` (O5, A3) leaves `v3.2.0` and waits for a later release. |
| E6 | Everything outside `v3.2.0`, `v3.3.0` and `v3.4.0` (including `store prune`) comes in `v3.5.0` at the earliest („2. tak”). |
| E7 | Backups (Q9): the NAS copy for now; a copy outside the NAS waits for the author („na razie nie mam innego miejsca na kopie zapasowe, będę musiał to przemyśleć”). R5 stays open. |
| E8 | Telemetry enters the series at 1 h only (Q11: „tylko co godzinę”); the 10-min records stay readable in the raw root. |
| E9 | Scheduling (Q3: „timer systemd”): the nightly run, the telemetry and validated-year checks and the captures' polling of P16 are Obserwator commands run by user systemd timers (`OnCalendar`, `Persistent=true` for a missed night), shipped as `.service`/`.timer` templates and a `docker-compose` service in Obserwator's deployment guide; an operator without Archiwista (a client's instance runs Obserwator and Hydrolog only) loses nothing. Backups likewise: an `rsync` script with its timer in the deployment guide, not an Archiwista job kind. D3 is superseded; Archiwista indexes, shows and serves what the timers wrote. The sections „Nightly job”, „Locking” (Archiwista's claims) and „Backups” (who) below read with this change. |
| E10 | ČHMÚ's validated hourly set (`cz.chmu.hydro_hourly`, Q10: „tak, dodać ten drugi zbiór w 3.2.0”) is the verified tier of ČHMÚ's sub-daily series in `v3.2.0`, replacing the `recent` hours year by year, with its history; R6 is checked on the data before the series is built. |
| E11 | Names follow Nogat's decision of 2026-11-21 on national acronyms (plan `2026-11-21-national-provider-names.md` on `develop`), which came after this plan's design: `cz.chmu.*` for `cz.chmi.*`, slugs `imgw_*`/`chmu_*`; the design keeps the old spelling only where it quotes the past. „On demand (D2)” and the follow-up „warnings and water-state classes stay live only” are superseded by E1 (P14): every live answer is captured. |

## Design

### Tiers and datasets

| Tier | Raw dataset | Kept as | Step in the raw root |
|---|---|---|---|
| verified | `pl.imgw.hydro_daily` (exists), `cz.chmu.hydro_daily` (exists) | as published | day |
| verified | `cz.chmu.hydro_hourly` (new) | as published, `historical/data/hourly/H_<WIGOS>_HQ_<YYYY>.json` | 1 h |
| telemetry | `pl.imgw.hydro_telemetry` (new) | the monthly zip as published | 10 min |
| operational | `pl.imgw.hydro_operational` (new) | the capture of the night: every hydro-back answer of the run as it came (P14, forecasts included), one version per UTC day of the request, gzip-compressed JSON Lines (time, address, status, body); the series takes the full hours of the closed UTC day only (D9) | 1 h in the series |
| operational | `cz.chmu.hydro_recent` (new) | the capture of the night: the 548 station files of the day as they came (P14) | 10 min |

A tier is a property of the dataset (`DatasetDescriptor.tier`). It is never inferred from values.

### Midnight: UTC (D9)

[proposed] Trim at 00:00 UTC.

- Every source is UTC: hydro-back's `Z`, ČHMÚ's `Z`, and the telemetry (31 × 144 records across the DST night).
- A UTC day always has 24 hours. A local day has 23 or 25: on the last Sunday of October the hour 02:00–03:00 local occurs twice, so local labels are ambiguous; in March one hour is missing.
- With a local midnight, each night would cut the same UTC hours differently in winter and summer, and a telemetry month would not line up with the nights.
- **Cost:** the GUI shows local time. A „local day” in the chart is drawn from 24 UTC hours shifted by one or two hours, which the chart handles, not the store.
- **The window relative to UTC midnight:** 02:30 local is 01:30 UTC in winter and 00:30 UTC in summer, after 00:00 UTC in both seasons. So the night always harvests the UTC day that has just closed.
  - Requests made after 02:00 UTC see that day in full hours only (A4).
  - Earlier requests also hold 10-min points of its last 2 hours, which the trim drops.

### Resolution of the series (D9)

[proposed] One sub-daily series per provider at **1 h**, from every tier:

- **The telemetry's 10-min records stay in the raw root as published.** The series takes their full-hour records: samples, not means, exactly as hydro-back's hourly values (744 of 744).
  - So replacing an operational month by its telemetry changes no hourly value; it only fills hours the night missed and marks them `telemetry`.
  - A mean would create a step at every boundary between tiers.
- **ČHMÚ's 10-min `recent` records are sampled the same way.** Its validated hourly set is used as published. Whether HQ's values are full-hour samples or hourly means is unverified (R6).
- **Cost:** a month of 878 IMGW-PIB stations in Parquet is 7.9 MB at 1 h against 33.6 MB at 10 min (October, measured). The 10-min data stay readable from the raw root (`datasets download`, `read_archive`).

### Versioning (A2)

What can change after the fact:

- **IMGW-PIB's operational values inside the 6 weeks:** no change was observed (two stations, 744 of 744 between hydro-back read on 2026-11-16 and the telemetry of 2026-11-12). That does not prove a value read the next night is final [INFERENCE].
- **ČHMÚ `recent`:** never rewritten (A3).
- **Telemetry and ČHMÚ's validated year:** they supersede the operational tier month by month and year by year.

Growth per year, IMGW-PIB plus ČHMÚ, at 1 h in the series:

| Option | Raw root | Data root | Assessment |
|---|---|---|---|
| (a) The nightly file as an immutable raw input, one per UTC day | IMGW-PIB about 1.8 MB/day [INFERENCE: about 1.1 KB per station and parameter], so 0.65 GB. ČHMÚ about 6 MB/day, so 2.2 GB. Telemetry 0.21 GB | — | **Take it.** It is the only copy of data the API forgets after 6 weeks; it fits the existing store (a day file is written once, a backfill with other bytes becomes a second version and records the correction); Archiwista can pin it. |
| (b1) Sub-daily series rebuilt monthly | as (a) | IMGW-PIB about 0.1 GB (12 × 7.9 MB), ČHMÚ about 0.06 GB | The nights would not reach the GUI until the month closes, so the on-demand delta would have to cover a month per station. That contradicts „the nightly harvest builds the database”. |
| (b2) Sub-daily series rebuilt nightly, one slot per month `series:<key>:<YYYY-MM>` [proposed] | as (a) | Current version of each month as (b1). Superseded nightly versions: about 30 per month of 3.5–8 MB for IMGW-PIB plus about 2–5 MB for ČHMÚ, so about 3–4 GB a year [INFERENCE] | **Take it.** Each night is visible the next morning. Closed months get a new version only when the telemetry or ČHMÚ's validated year arrives. Superseded nightly versions are what the prune command (D4) reclaims. |
| (c) No versioning of the operational tier: append in place, replace by telemetry | about 0.65 GB (IMGW-PIB) | about 0.16 GB | **Reject.** It needs mutable files in roots that are append-only (ADR-001 D1, ADR-017 D1): readers could see half-written files, and Archiwista's pins and `command_for_version` would point at changed bytes. The savings are about 3 GB a year. |

**Recommendation:** (a) plus (b2). Keep every version by default (D4), with an explicit prune command for superseded sub-daily series versions. Closed months shrink to their current version when pruned.

### Precedence

- **Within the sub-daily series:** telemetry over operational (IMGW-PIB), and validated hourly over operational (ČHMÚ), per station, variable and hour. A higher tier replaces a lower one even where the values differ (R4); the captured answer stays for comparison (E5).
  - A month is rebuilt when its telemetry zip arrives; a year is rebuilt when ČHMÚ's validated year arrives.
  - Operational points stay only where the higher tier has no record (`999` or a gap). Each point carries `<var>_tier`.
- **Across resolutions:** the verified daily series stays the archive. The sub-daily series is never aggregated into it and never changes it. The analyses (Hydrolog) read only verified daily series.
- **„Continuous”:** verified daily up to the last published hydrological year (IMGW-PIB) or year (ČHMÚ); hourly telemetry or validated hourly data; operational hours up to yesterday; then the live tail.

### Data root

- **New datasets:** `pl.imgw.hydro_subdaily` and `cz.chmu.hydro_subdaily` (slugs `imgw_hydro_subdaily` and `chmu_hydro_subdaily`, ADR-028), `time_unit` `hour` — P5 of `2026-11-20-hydromet-providers.md`, one hourly form for every provider — `year_type` `calendar`.
- **Columns:** those of `obserwator-series/1` for an hourly unit: `time` (timestamp, UTC, the start of the hour) in place of `date`, `hydro_year`, and per H, Q, T the columns `<var>_value`, `<var>_flag` and the new optional `<var>_tier` (dictionary `verified|telemetry|operational`), which only a series built from several tiers carries.
- **Contract:** `obserwator-series/1` stays `/1` (ECO-085): `hour` and `<var>_tier` are additions a reader can skip, and every daily series is byte-identical. There is no `obserwator-subdaily/1`.
- **Slots per month:** `series:<key>:<YYYY-MM>`, a new form of the slot grammar (`store/reader.py`, spec §13.7), so a night rebuilds one month and `series read` joins the months; the directory form and how `current_version` lists the months are the ADR of O4.

### The timers (E9, D8, P16)

Three user systemd timers of Obserwator's deployment guide run Obserwator's commands (`Persistent=true`: a missed run happens at the next boot). Archiwista's queue runs none of them (D3 superseded by E9), so an instance without Archiwista loses nothing.

- **`obserwator-night.timer`, 02:30 local:** `obserwator store sync --datasets pl.imgw.hydro_operational --pace-until 06:30` (the last closed UTC day by default), the sealing of every closed day of the spool, then `series build` of the months touched; `cz.chmu.hydro_recent` from 05:00 local, well after its files appear at about 00:20 UTC. `--start`/`--end` (UTC dates, AGI-3.4) name other days: `--start <D−39>` backfills 40 days (inside „6 tygodni”), one request per station and parameter with `hoursInterval` covering them. A `--pace-until` already passed means the minimum spacing of 5 s.
- **`obserwator-telemetry.timer`, 06:45 local:** one `POST datastore/getFilesList` for `Arch/Telemetria/Hydro/<YYYY>` and one listing of `historical/data/hourly/`; a new month's zip (about 18 MB) or a new validated year (about 543 files of about 0.5 MB, spread over several runs) is downloaded and the months or years touched are rebuilt.
- **`obserwator-current.timer`, hourly at :15:** the captures of the sources that answer for every station in one request — `api/data/hydro`, `api/data/meteo`, the hydro-back map of water states and their classes, `warningshydro` and `warningsmeteo` — about five requests an hour, written to the spool only. ČHMÚ `now` (548 files a poll) is not scheduled: its 10-min values arrive whole in `recent` the next day (A3), so it is captured on demand only (the live tail). The adapter's declared rate (P16) is a ceiling: the guide's timers run at or below it, never above.
- **Pacing in Obserwator:** `--pace-until` spreads the requests evenly up to the deadline, one at a time, with gzip. On 429 or 5xx it backs off (60 s, 120 s, 240 s, then skips the station until the next night). Three connection failures in a row end the call `partial`.
- **Idempotent by content:** a run for a day already stored writes a new capture only when the bytes differ (a correction, R4); the series are `unchanged` when their inputs are. A DST night is harmless: the capture is keyed by the UTC day.

### Load budget (per night, 02:30–06:30)

| Item | Requests | On the wire | Spacing |
|---|---|---|---|
| hydro-back H, about 880 stations, `hoursInterval` about 26–29 | about 880 | about 5 KB each (gzip; 32 KB plain, mostly forecasts), so about 4.4 MB | |
| hydro-back Q, about 680 stations | about 680 | about 0.5 KB each, so 0.35 MB | |
| hydro-back T, about 85 stations | about 85 | 0.05 MB | |
| **IMGW-PIB total** | **about 1,650**, at most 2,700 if every station were asked for all three; stations without Q or T are known from the previous night and `api/data/hydro` | **about 5 MB** | one every 8–9 s over 4 h |
| ČHMÚ `recent`, 548 files | 548 | about 9 MB (15 Nov: 9.04 MB) | one every 6.5 s, 05:00–06:00 |
| Telemetry | 1 listing a day, 1 zip a month | 17.6 MB a month | — |

The hourly timer adds about 120 requests a day. Nothing runs in Archiwista's queue (E9).

### The live tail (E1, E11; was „On demand (D2)”)

- **When a station's card opens:** the GUI server reads the station's newest stored hour. If it is older than the current hour, it asks hydro-back for that station only, with `hoursInterval = hours since then + 1` (at most 1,000), or ČHMÚ's `now/data/<WIGOS>.json`.
- **The answer is written to the spool (P14) and stays in memory** for 10 min per station, at most 500 stations (ADR-027 D3 bounds the documents), one request per station at a time and one live request for the whole server, as today's snapshots (`gui/_live.py`).
- **What is served:** the chart joins the stored series and the live tail only for sources set `public` (decision 15); otherwise the card shows the live tail as today.

### Locking

- **Writers of the raw root:** `store sync`, run by the timers or by hand. It takes `flock` on `<state_dir>/obserwator/store-sync.lock`, waits up to 10 minutes for it, then fails with the existing `conflict` (exit 4, `src/obserwator/exceptions.py`). The timers are set apart (02:30 the night, 05:00 ČHMÚ, 06:45 the telemetry, the hourly poll at :15), so the wait covers a late run, not the rule.
- **The spool** (`<state_dir>/obserwator/captures/<dataset>/<YYYY-MM-DD>/`, the day of the answer's time in UTC): one file per answer, created with `O_EXCL` and named by its time and the SHA-256 of its body, so the GUI, the hourly timer and a CLI run write it without a lock; the night's `store sync` seals every closed day into one version. The GUI writes nothing else and never a root (ADR-013 D5 holds for the roots; the spool is `state_dir`, where the GUI already writes its statistics). A spool write that fails is one warning record and a `config show` problem; the answer is still served.
- **Archiwista** claims positions of its own downloads only (ADR-047); its jobs and the timers never download the same dataset.

### Chart

- **Where:** the station card „teraz” (`src/obserwator/gui/web/src/sections/teraz.js:34`, `HydroNow`), with the SVG module `gui/web/src/charts/`.
- **What it shows:**
  - H with the warning and alarm levels of `pl.imgw.hydro_details` (ADR-021); Q and T on a switch.
  - Ranges 3 d, 7 d, 30 d and „all stored”.
  - Each tier in its own style and legend entry, with the live tail apart. The caption reads „dane operacyjne, niezweryfikowane” (§ 6 ust. 3).
  - Daily T readings drawn as points, not joined.
- **Data:** a private route `GET /api/station/{code}/subdaily?from=…` joins the stored series with the delta.
- **Served only when public:** the route and the chart join the stored series with the live tail only when every capture source of the series is `public` (P15); otherwise the card shows the live tail as today, and the series routes answer `not_found`.
- **Lines:** the provider's lines of each tier (RH, RD, C/CP) in the card's strip (DEV-20.5).

### Pruning superseded versions (D4)

- **The command:** `obserwator store prune` [proposed], off by default and never run by the schedule unless the operator enables it.
  - It removes superseded versions (never the current version of a slot) of chosen slot prefixes older than a chosen age, for example `--slot 'series:pl.imgw.hydro_subdaily:*' --superseded --older-than 30d`.
  - It refuses any version listed as pinned by Archiwista: an input `--keep FILE` exported by Archiwista (A-step), or a check through its read API.
  - `--check` gives the plan (`obserwator-plan/1`) with the bytes freed.
- **What it needs:**
  - An Obserwator ADR amending ADR-001 D1 and ADR-017 D1 („append-only; nothing is ever replaced”): pruning deletes only superseded, unpinned versions, by an explicit command.
  - A Nogat ECO decision amending ECO-059: Archiwista's pins of Obserwator versions are honoured by a prune. Without that rule, a prune could break a project's restore (ADR-008 D5).

### Backups (D10)

- **What:**
  - The whole Obserwator store: the data root (local) and the raw root (on the NAS).
  - The raw root is the irreplaceable part: the operational tier exists nowhere else after 6 weeks, and sources remove old versions (DEV-18.5).
  - The data root can be rebuilt from the raw root but takes hours (Hydrolog's analyses), so it is backed up too, as ECO-059 asks.
  - The operational tier alone cannot be isolated cleanly: its datasets are directories of the same roots, and the series join every tier.
- **Tool:**
  - `rsync -aH` (DEV-18.5, the only one installed), with snapshots in dated directories.
  - Weekly incremental: `--link-dest=<previous snapshot>`. Since the store is append-only, a week copies only its new version directories; the rest are hard links.
  - Monthly full: a snapshot without `--link-dest`, an independent copy, so damage to a shared inode cannot reach every snapshot.
  - `.incoming/` directories are excluded. A version without its sidecar in a copy is an interrupted publication that `store scan` reports and the next write completes.
- **Where:** `/mnt/magazyn/agent-tmp/backup/obserwator/{weekly,monthly}/<YYYY-MM-DD>/{raw,data}/` [proposed].
  - The NAS accepts hard links: Obserwator's writer needs them (`writer.py:287-295`) and publishes there today [INFERENCE from the working deployment].
  - **The raw root's copy on the same NAS protects against deletion and software errors, not against loss of the NAS (Q9).**
- **Retention:** 8 weekly and 6 monthly snapshots. Before a full the script checks the share's free space (`df`) and refuses the full with an error record when it would leave less than 15 % free: the backup shares the NAS with the raw root and Archiwista's store, and a full NAS stops Obserwator's writer. The sizes are measured in A4 before the first full (234 GB of 300 GB were free on 2026-11-22).
- **Deletion:** the only deletion the script does is of whole snapshot directories beyond the retention, under `backup/obserwator/{weekly,monthly}/` only, never following a link, never in a root.
- **Restore test:** after each monthly full, copy its data root into a temporary directory and run:
  - `obserwator store scan --root <tmp>`, offline, which lists versions and problems: the same count of versions as the source at the snapshot's time, no problems.
  - A SHA-256 check of 50 random version files against their sidecars.
  - `obserwator series read` of one station.

  The raw root's restore is tested the same way on a sample of 100 version directories. The result is `restore-test.log` beside the snapshot and one record in Obserwator's server log (DEV-12.4).
- **Who:** Obserwator's deployment guide (A4): `obserwator-backup.timer`, Sunday 07:00 weekly, the first Sunday of the month full, after the night's run; the unit confined as the install contract's unit rule, `ReadWritePaths=` for the target only, the roots read; the first run before the first night (E4). Archiwista has no part in it (ECO-059 as amended by ECO-084).

## Steps

Each step runs in its own session and branch under the project's `CLAUDE.md` (DEV-3.4, DEV-17.5). Each project records its decisions as ADRs (DEV-17.2). Long runs are user systemd units (DEV-17.6). Nothing starts before this plan's `Approved:` line and the first joint release.

| # | Project | Change | Depends on | Verified by |
|---|---|---|---|---|
| N0 | Nogat | ECO-084 (the captures and the operational tier; DEV-20.8 amended as decision 1 of Fable's review; ECO-059 amended: Obserwator's commands run by the deployment's timers write the raw root beside the downloads Archiwista orders, operational data are kept as captures, the backup copy of both roots is the deployment's `rsync` timer) and ECO-085 (additions within version 1, Q8), in `standards/DECISIONS.md`; DEV-20.8 in `standards/DEVELOPMENT_STANDARDS.md` and the sentence on values and forms in AGI-4.1; the reasons `missing_credentials` and `invalid_credentials` of `forbidden` in `standards/error_registry.json` (P4; the tables regenerate); `ecosystem.yaml`: the summaries of `obserwator-store/1` (captures), `obserwator-series/1` (hourly series) and of the sources `imgw` and `chmu`, no new contract; `standards/README.md` changelog 1.2; PROGRESS Next 17 and the CHANGELOG entry (Q12). This is also step 1 of `2026-11-20-hydromet-providers.md`. | the `Approved:` lines of both plans | Nogat's gate (its `CLAUDE.md`): no registry drift, the ECO ids unique, the error tables regenerated |
| H2 | Obserwator | ADR „provider adapters” (P1, P2): `obserwator.providers` (`pl/imgw.py`, `cz/chmu.py`), the `Protocol`, `ProviderDescriptor.adapter`; the scattered branches dispatch through it; no Gdańskie Wody code | N0 | the full gate; the fixture stores, the sidecars and AGENTS.md byte-identical (P2) |
| O1 | Obserwator | The ADR „captures and the operational tier” (amends ADR-003 D4, ADR-013 D5 and ADR-015 D5: the tiers; ČHMÚ `recent`, `now` and `historical/hourly` in scope; the captures as archive versions; the GUI's spool), numbered when it lands (3.1.0 took ADR-024 to ADR-028; no number is fixed here, for any ADR of this plan). Descriptors `pl.imgw.hydro_operational`, `pl.imgw.hydro_telemetry`, `cz.chmu.hydro_recent`, `cz.chmu.hydro_hourly` and one capture dataset per polled source of 2a, each with `tier`, `time_unit` and `archive_scope`. Errata of ADR-025 (step 6 is `v3.3.0`) and the re-cut of PROGRESS „Release 3.2.0” to the scope of 2026-11-22 | N0 | the author's review; the ADR index of `docs/DECISIONS.md` has no duplicate; `datasets()` lists the new descriptors with their tiers |
| H2a | Obserwator | Captures (P14–P16): the capture writer in the adapter interface; the spool `<state_dir>/obserwator/captures/<dataset>/<YYYY-MM-DD>/` (one file per answer, create-only; the GUI and the hourly timer write it); `store sync` of a capture dataset seals every closed UTC day of the spool into one version per dataset and day (equal answers recorded once, as seen); `[obserwator.capture]` and `config show` (P15, the defaults of decision 15); the GUI's live fetches through the writer | H2, O1 | a GUI card opened and an hourly poll appear in the next sealed version; an equal answer is recorded once; no sidecar holds a credential (test); `config show` lists every source's state |
| O2 | Obserwator | Fetchers: hydro-back series beside `_hydro_details` (3.1.0's `User-Agent`, no `Referer`), the telemetry listing and zip, ČHMÚ `recent`, `now` and `historical/hourly`; pacing (`--pace-until`), backoff and gzip in one place (`fetch.py`) | H2a | recorded answers; one live night on the test instance with no more than one request per 5 s |
| O3 | Obserwator | `store sync --start/--end` (UTC dates, AGI-3.4; default the last closed UTC day) for the capture datasets and the night's harvest; the lock with a bounded wait (Locking) | O2 | a backfill of 40 days gives the same hours as the nights of the same days; a second `store sync` of the same dataset waits, then fails with `conflict` |
| O4 | Obserwator | Hourly series (P5 and this plan; absorbs step 4 of the providers plan): `time_unit` `hour` in the registry, the series schema (`time`, the optional `<var>_tier`), the builder, the monthly slots, precedence, `series read`/`export` (CSV, JSON, Parquet), the GUI's charts of hourly data; D9's trim (the full hours of a closed UTC day, the 10-min tail dropped) is a rule of this builder; one ADR „hourly series” | O3 | October of 151160060 and 150160180: the operational hours equal the telemetry's full hours (744 of 744), the gap stays operational; the daily fixture series byte-identical; `series read` of one month and across months |
| H3 | Obserwator | Credentials and errors (P3, P4): `OBSERWATOR_<PROVIDER>_API_KEY[_FILE]` in `CREDENTIAL_KEYS`, `config show`, `.env.example`, `CLAUDE.md`, messages pl/en; no provider of `v3.2.0` uses one | N0 | `config show` reports a test provider's key `present`/`missing`; a missing key is `forbidden`/`missing_credentials` with the hint naming the variable; the key appears in no log, envelope or sidecar (test) |
| H5a | Obserwator | ČHMÚ groundwater (its own ADR): `cz.chmu.groundwater_*` (`historical` verified; `recent` and `now` operational captures; `characteristic`), `H_asl`, the yield and temperature variables, the station kind `groundwater` (bore, spring) with its symbol, filter and export line; a weekly unit, if the ADR needs one, follows ECO-085 and A1 covers it | H2, O1 | `store sync`, `series build`, `store catalog --provider CHMU` of one bore and one spring; the GUI shows them with their kind; the hydro and meteo fixtures byte-identical |
| O6 | Obserwator | GUI: the chart in „teraz”, its route, the live tail through the spool, the publication state honoured (decision 15) | O4, H2a | the GUI on the test instance: the stored hours to the end of yesterday (UTC), today's hours from the live fetch, each tier labelled; a second opening within 10 min makes no request; a `private` source is not served |
| A2 | Obserwator | The `.service`/`.timer` templates (`obserwator-night`, `obserwator-telemetry`, `obserwator-current`) and the `docker-compose` service in the deployment guide; `Persistent=true`; the window end as `--pace-until`; catch-up with `--start` after a missed night; the units confined as the install contract's unit rule (`NoNewPrivileges`, `ProtectHome=read-only`, `ReadWritePaths=` for the roots and `state_dir`) | O3, H2a | a night run and a missed-night catch-up on the test instance |
| A1 | Archiwista | Its minor: `time_unit` `hour` and the monthly slots in the adapter and the index (a migration or `reindex`); an unknown unit skipped with a warning record instead of a failure; the tier and the publication state of a version shown; the station kind `groundwater` accepted | O4, H2a, H5a | contract test with `obserwator.testing` on a fixture holding an hourly series, a monthly slot, a capture version and a groundwater station; `archiwista doctor` 0 errors |
| A4 | Obserwator | The backup script and its timer (decision 16) in the deployment guide and README (DEV-18.5) | A2 | a weekly snapshot and a monthly full on the test instance; the restore test passes |
| D1 | Operator | Production, in this order: Archiwista's minor deployed; Obserwator `v3.2.0`; `[obserwator.capture]` set (the author decides `public` for hydro-back on his instance, E2); the first backup; the timers; the first backfill `--start <D−39>` | O6, A1, A2, A4 | the first week of nights, one weekly snapshot, Archiwista's scan without problems |

Left for `v3.5.0` (E5, E6): O5 `store prune` and A3, Archiwista's export of the versions its projects pin.

## Acceptance

1. After one night the raw root holds the capture version of `pl.imgw.hydro_operational` and of `cz.chmu.hydro_recent` for the UTC day of the run, every answer as it came, and the sealed captures of the polled sources for the closed UTC day; the month's slot of each sub-daily series has a new version whose hours of D are the full hours 00:00–23:00 UTC only. The run's summary gives the requests, failures and wall time, and the run ended before 06:30.
2. `series read --dataset pl.imgw.hydro_subdaily --station 151160060` gives October's hours with tier `operational`. After `Hydro_2026-10.zip` is synced, the same read gives tier `telemetry` with the same values (744 of 744).
3. A station opened in the GUI shows the stored hours to the end of yesterday (UTC) plus today's hours from the delta, each labelled with its tier. A second opening within 10 min makes no request.
4. A second run for the same day stores a new capture only when the source's bytes differ and leaves the series `unchanged`; a second `store sync` of the same dataset during the night's run waits for the lock, then fails with `conflict`.
5. No more than one request per 5 s to hydro-back in the window (the job's log).
6. Hydrolog's reader of `obserwator-series/1` passes unchanged; Archiwista passes with A1 (0.3.3 would refuse an hourly series, ECO-085), and its contract test covers an hourly series, a monthly slot and a capture version.
7. A weekly snapshot holds only the week's new version directories as new files. The monthly restore test passes.
8. The lines of each tier appear in the GUI's strip, the exports and the envelopes.

## Risks and open questions

Risks:

- **R1. Undocumented backend.** hydro-back is the site's own backend, not a published API: its paths or fields may change, or it may refuse scripted clients. The telemetry month is the fallback.
- **R2. Terms** (decision 6: no contact before the first run):
  - (a) IMGW-PIB allows free use „do celów prywatnych”. Serving its stored series on the public instance is the question already open in Obserwator's PROGRESS; the public GUI stays behind Cloudflare Access.
  - (b) Use for water-management planning (Hydrograf, Hydraulik) needs a contract.
  - (c) The formal path to continuous access is a request under § 8 ust. 2 (biznes@imgw.pl) or cash@imgw.pl.
- **R3. Growth without pruning:** about 3–4 GB a year of superseded nightly series versions (Versioning).
- **R4. Late operational corrections** by IMGW-PIB inside the 6 weeks are read only with the telemetry month [INFERENCE: none observed].
- **R5. The NAS:** the raw root and its backup share one device (Q9).
- **R6. ČHMÚ's validated hourly values:** whether they are full-hour samples or hourly means is unverified, so a step may appear at the boundary with the operational hours.
- **R7. Temperature:** some stations give one reading a day at 06:00 UTC, others hourly.
- **R8. Overlapping timers:** on a slow night two `store sync` runs meet on the lock (Locking); a run that reaches 06:30 ends `partial` and the next night fills the gap with `--start`.

Topics to settle before implementation (the author, before this plan's `Approved:` line or at the latest before N0 starts; the plan ships after the first joint release):

- **Q3.** Answered (E9): user systemd timers running Obserwator's commands.
- **Q8.** Decided (Fable, 2026-11-23; ECO-085): `time_unit` `hour`, the optional column `<var>_tier` and the slot form `series:<key>:<YYYY-MM>` stay within `obserwator-series/1` and `obserwator-data/1`. The one reader that tells series apart by `time_unit`, Archiwista, changes in A1 and its minor is deployed before the first hourly series reaches the shared data root (D1): Archiwista 0.3.3 refuses such a series (`adapter/obserwator/adapter.py:590-597`, `index/schema.py:471`), so the order is not optional.
- **Q9.** Answered for now (E7): the NAS copy; a copy outside the NAS waits for the author.
- **Q10.** Answered (E10): `cz.chmu.hydro_hourly` in `v3.2.0`.
- **Q11.** Answered (E8): 1 h only.
- **Q12.** Decided (Fable, 2026-11-23): the merge on `plan/obserwator-3.2.0` kept `develop`'s PROGRESS (items 15 and 16 of 2026-11-22) and CHANGELOG, so this plan and the providers plan are one new item 17 and one CHANGELOG entry; `plan/large-basins` takes 18 when it merges. The same rule for ECO numbers (ECO-085's consequence).

## Follow-ups (outside this plan's steps)

- Meteorological telemetry (`Arch/Telemetria/Meteo`) and ČHMÚ's climate `now`/`recent`: a separate, later plan (D7).
- Forecasts (`hdModelStateForecast`, `H_F`/`Q_F`) stay inside the captures as they came and are read into no series; warnings and water-state classes are captured (E1) and shown live.

## Results

- 2026-11-23, Obserwator `v3.2.0` (release commit `1550a3a`, `main` `92d5d89`, gate 3980 passed): N0 (Nogat ECO-084, ECO-085, `3fb305e`); O1 (ADR-030, tiers and captures), O2 (fetchers with pacing), O3 (`store sync --start/--end`, the capture lock `store-sync.lock`), O4 (ADR-031, hourly series within `obserwator-series/1`, precedence telemetry over operational), O6 (the chart in „teraz”, the live tail through the spool), A2 (`obserwator-night`, `obserwator-telemetry`, `obserwator-current` units; the night runs IMGW `--pace-until 05:00`, then ČHMÚ `--pace-until 06:30`), A4 (backups); `cz.chmu.hydro_hourly`. Live smoke run on a throwaway root: poll, harvest, October's telemetry, `series build`, `series read` (744 hours of October from telemetry, 48 operational hours of November), the GUI's `/api/station/151160060/subdaily` (stored hours and the live tail, no second request within 10 min).
- 2026-11-23, Archiwista `v0.4.0` (A1, A-ADR-059; `main` `99756f5`, gate 3132 passed): pins Obserwator `v3.2.0`, adapter range `>=3.2.0,<4`; tiers and publication shown, hourly and weekly series indexed with their coverage, the 0.3.3 index completed in place (schema 1). Deploy before Obserwator `v3.2.0` writes to shared roots; otherwise `archiwista reindex --store <store>` once.
- Both member releases came outside a release set (REL-6.6 deviation, the author's decision of 2026-11-23 that Nogat's release waits); the next set carries them. D1 (production) is the author's.
