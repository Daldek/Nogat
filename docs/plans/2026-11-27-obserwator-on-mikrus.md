# Plan: Obserwator's public instance on a Mikrus VPS, its data built at home

Status: not pursued. The author dropped the move on 2026-11-27 („Ok, rezygnuję z przeniesienia”) after the privacy finding below, and asked for the findings to be kept in case he changes his mind. There is no `Approved:` line (DEV-17.4); before any work this plan needs its open points settled and his approval.

Requirements: DEV-15.7 (regulamin), DEV-15.9 and DEV-15.10 (limit, statistics, logs), DEV-18.5 (backups), ECO-084 (captures), ECO-085 (readers first), REL-1.4 (the regulamin's version is the author's).

## The author's aim (2026-11-27)

- Renewing his Mikrus 2.1 and considering a larger plan; Mikrus „nie daje pełnej swobody z uwagi na swoją architekturę”.
- „Na początek wystarczy, że sam Obserwator będzie działać na zewnątrz. Z czasem dojdą Hydrolog i Hydrograf, może też inne usługi, ale wtedy będę myślał albo o bare metal, albo o innej usłudze.”
- „Proces budowania zostawiłbym u siebie, do Obserwatora/na Mikrusa chciałbym przesyłać już gotowe pliki.”
- The analyses on request stay on Mikrus (his question, agreed).

## Facts

Measured on the author's machine on 2026-11-27, Obserwator `v3.3.1`, Hydrolog `v0.10.0`. Values are momentary; peaks after several days can be higher (Obserwator 3.1.0's GUI reached 3.5 GB plus 2.3 GB of swap).

| Item | Measured |
|---|---|
| Obserwator GUI (`gui serve`) | 1.4 GB now, 1.9 GB peak since its start |
| Obserwator REST API (`obserwator server`) | 0.37 GB, 0.76 GB peak |
| Archiwista | 1.56 GB, 2.1 GB peak |
| Hydrolog GUI | 0.19 GB, 0.34 GB peak |
| Hydrograf | `hydro_api` 272 MB, `hydro_db` 62 MB; database 357 MB, `data/` 0.93 GB, each `hydrograf-api` image about 2 GB; PostgreSQL 16.4 with PostGIS 3.4.3 in Docker |
| An analysis on request | 2.9–3.5 s (`flood_frequency.Q` 1981–2010 and `characteristic.H` 1991–2020 of 151160060); about 125 MB RSS per Hydrolog process, sampled every 0.1 s; at most two at a time, 30 s each; the result kept in the GUI's memory (500 results), never written to the data root |
| Building one month of `pl.pig.groundwater_subdaily` | 4.2–5.3 GB peak and 43–82 s per month, whatever the month holds: 2015-03 with 8 stations 5.2 GB, 2026-11 with 798 stations 4.2 GB. It probably reads whole captures (the backfill capture of 2026-11-24 is 121 MB) each time; not checked in the code |
| Disk | data root 4.4 GB; raw root about 1.8 GB on 2026-11-23, before PIG-PIB's import, growing by about 5 MB (hydro-back) and 9 MB (ČHMÚ) of gzip a night; Archiwista's local data 2.3 GB; Kartograf's store on the NAS over 66 GB; Obserwator's venv 374 MB, Hydrolog's 756 MB; a monthly backup about 6 GB |

Mikrus (read 2026-11-27):

- Plans, per year: 2.1 1 GB RAM / 10 GB disk, 75 zł; 3.0 2 GB / 25 GB, 130 zł; 3.5 4 GB / 40 GB, 197 zł; 4.1 8 GB / 80 GB, 395 zł; 4.2 16 GB / 160 GB, 790 zł. Docker from 2.1 up (1.0 without it). A change between 2.1, 3.0 and 3.5 is automatic, in place and without downtime; moving to 4.x needs the administrator and means downtime (https://mikr.us/).
- Technical limits (https://wiki.mikr.us/ograniczenia_techniczne_mikrusa/): LXC containers on a shared kernel; IPv6 and a few random IPv4 ports; no stable swap in a file; no NFS or CIFS mounts the classic way, FUSE only; no block devices.
- Its terms (https://mikr.us/regulamin): the provider is „UW-TEAM.org Jakub Mrugalski”, hosting at third parties („np. Datacenter Hetzner”), the servers in Finland (EEA); it reserves the right to „podejmowania interwencji na serwerze klienta”. The terms describe only the processing of its clients' own data; no data processing agreement (art. 28 GDPR) was found in them.

Cloudflare (https://developers.cloudflare.com/rules/transform/request-header-modification/, „Important remarks”): a Request Header Transform Rule may remove `cf-connecting-ip`, but Cloudflare's proxy adds `x-forwarded-for` again after every rule phase; only a Worker can send a request without it. A tunnel connects outwards, so Mikrus's port limits do not matter.

## Design considered

| ID | Decision considered |
|---|---|
| M1 | **The split.** At home: the timers (night, telemetry, current poll), the NAS, the raw root, every build (series, PIG-PIB's hourly series, `analyses build`) and the backups. On Mikrus: `obserwator gui serve` on a copy of the data root, Hydrolog for the analyses on request, `cloudflared` for `obserwator-test.debever.pl`; the REST API optional. The GUI reads the data root only (ADR-013 D5) and picks up new versions without a restart. |
| M2 | **The copy.** Home pushes, since Mikrus cannot reach the home network: `rsync -aH --exclude=.incoming/ --delay-updates` over SSH, once a day after the night and the telemetry (about 07:30) and after a build by hand; no `--delete`, since the store only adds versions. The key on Mikrus restricted by `rrsync` to the one directory. About 4.4 GB the first time, a few MB a day after. |
| M3 | **The way back.** Before the night's sealing (02:30) home pulls Mikrus's capture spool (files named by time and SHA-256, never changed) into its own spool, and the feedback and daily statistics into its backups; otherwise the answers Mikrus's GUI fetched live are never stored (ECO-084). |
| M4 | **The plan.** Mikrus 3.5: the GUI's 1.9 GB peak, about 0.25 GB of analyses on request, 0.76 GB with the API, so about 2.2–2.9 GB of 4 GB. 3.0 is too small without swap. With the builds on Mikrus, 3.5 is too small (5.3 GB for one PIG-PIB month) and 4.1 too tight (about 7.2 GB without the API). |
| M5 | **Memory.** `MemoryMax` about 3 GB in the GUI's unit, so systemd restarts it (`Restart=on-failure`) instead of the container's OOM killer taking another process. |
| M6 | **Versions.** Mikrus, the reader, is upgraded before home, the writer (ECO-085); Obserwator and Hydrolog at the same versions on both sides, since a stored and a computed result each name Hydrolog's version. |
| M7 | **Settings.** Mikrus's copy of `nogat.toml` decides what is served: `[obserwator.capture]`, `[nogat.operator]` with `terms_effective`, `[nogat.gui]`, and the admin key file. Cloudflare Access's `/admin` rules follow the host name. |
| M8 | **Monitoring.** After each copy, the newest series versions in Mikrus's `api/session` compared with home's, and a notification on failure (the channel is the author's to choose). A missed copy leaves Mikrus serving the last one; home's timers catch up 40 days. |
| M9 | **Fallback.** Home's GUI on :8060 stays; switching the host back in Cloudflare is the rollback (it keeps 1.9 GB of RAM at home). |

## Why it stopped: Mikrus would be a processor

- A tunnel changes the path, not where the server runs. The tunnel ends at `cloudflared` on Mikrus, which hands the decrypted request with its headers to the GUI.
- The visitor's address reaches the GUI whatever the edge does: `x-forwarded-for` is added again after every rule (Facts).
- Without the address Mikrus is still a processor: the feedback and the daily statistics are on its disk, and its terms reserve interventions on the client's server.
- Hiding the address would also break the GUI's per-client limit (everyone would be `127.0.0.1`, one shared 300 requests a minute) and the visitor count, both described in § 8 ust. 2 of the regulamin.
- The regulamin names one processor, `processor` in § 8 ust. 4 („Ruch do serwisu przechodzi przez …”); hosting needs another field or sentence, so a new version of the regulamin, which only the author makes (REL-1.4).

Options put to the author: (a) name Mikrus, with Hetzner in Finland, as a processor after a data processing agreement from `pomoc@mikr.us`, and add hosting to § 8 in a new version of the regulamin (recommended); (b) keep serving from home (chosen); (c) a Worker removing `x-forwarded-for`, the limit at Cloudflare (Free: one rule of 10 s) and the feedback forwarded home (rejected: much work, and Mikrus would still hold the statistics). This is a technical assessment, not legal advice; the lawyer's review of the operator's draft regulamin (PROGRESS, Next 15) is the place for the question.

The same holds for any hosting provider. Only hardware the operator owns, as at home today, keeps the operator the only party besides Cloudflare.

## Before resuming

1. A data processing agreement from the host (Mikrus: `pomoc@mikr.us`), and § 8 of the regulamin naming the hosting, in a version the author publishes.
2. From the host, `curl` to hydro-back.imgw.pl, danepubliczne.imgw.pl, opendata.chmi.cz and cbdgmapa.pgi.gov.pl: the GUI asks them live, and their answers from Finland were not tested.
3. The plan (3.5 for Obserwator alone, M4), SSH access to the host, and the host name switched in Cloudflare (the dashboard or a tunnel token).
4. The notification channel of M8.
5. Then the steps: install the tags, the units with M5, the first copy and its timer (M2), the way back (M3), `cloudflared`, the switch, a rollback document; in a session with this plan approved.

## Related

- The PIG-PIB build's memory (Facts) is a defect worth fixing at home too: about 5 GB a night whatever the month holds.
- Today's access to Obserwator from outside the machine: the public GUI behind the tunnel, and the read-only REST API in the LAN at 192.168.88.9:8001 through an SSH tunnel (PROGRESS, Ports). A public, cached `/api/v1` is Obserwator `v3.6.0` (`2026-11-24-qgis-plugin.md`, S2).

## Results

None: not pursued.
