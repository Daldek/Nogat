# Plan: one logging convention for every server

Approved: 2026-11-13, the author's request in session („Czy możesz ujednolicić logowanie we wszystkich aplikacjach i zdefiniować je w Nogacie?”)

Status: step 1 (Nogat) done 2026-11-13 on branch `feat/unified-logging`; steps 2 to 6 in each project's own branch; no merges, tags or releases.

Requirements: DEV-12.4 to DEV-12.9, DEV-15.6, DEV-15.10, DEV-18.1, DEV-18.2, HUB-4.1 and ECO-066 (added or changed by step 1); DEV-12.3, DEV-15.9, DEV-15.11, HUB-5.2, DEV-17.5.

## Goal

Every server of the ecosystem, Hydrograf, Hydrolog's GUI, Obserwator's GUI and REST server and Archiwista, logs in one way that Nogat defines and checks: the same kinds of log, one record format, files the server deletes itself after 14 days, and no IP address in any log, on today's host (systemd user units, Docker for Hydrograf) and on the dedicated server outside Cloudflare alike, without root.

## State on 2026-11-13

Read in the repositories, the user units, `docker inspect` and the user journal.

| Server | Where its logs go | What breaks the rules |
|---|---|---|
| Hydrograf, `develop` `d515aad`, containers `hydro_api`, `hydro_nginx` | the API's structlog JSON (`request_completed`: method, path without query, status, duration, the id nginx sends in `X-Request-ID`, returned in a response header) and nginx's `log_format hydrograf` (`$request_uri`, `$http_user_agent`) to stdout, `error_log /dev/stderr crit`; both through Docker's `journald` driver into the system journal; `hydro_db` `json-file` 10 MB × 50 | no time limit (`docker/journald.conf` needs root and is not installed); the full User-Agent; at `crit` nginx still names the client of a failed TLS handshake |
| Hydroni, Hydrograf's second instance, `hydroni_*` | `json-file` 10 MB × 50; the API with `--workers 2` and uvicorn's access log on | addresses only of the loopback and the Docker gateway; no time limit |
| Hydrolog, `develop` `d9dc7f6`, user unit `hydrolog-gui` | with `[nogat.operator]`: one JSON line per request (`PublicGuard`, `src/hydrolog/gui/_public.py` 476–484) on stderr, into the user journal | no time limit; the full User-Agent; the request id in `X-Request-Id` |
| Obserwator's GUI, `feature/gui` `4c944fc` | its own `<data_dir>/obserwator/logs/access-YYYY-MM-DD.jsonl`, deleted after 14 days (`gui/_traffic.py`) | the full User-Agent; its own format; no application or lifecycle files; the id in `X-Request-Id` |
| Obserwator's mockup, user unit `obserwator-public` on :8060 | uvicorn with `--proxy-headers` printed access lines with the client's address until 21:05 CET; now `--no-access-log` | 673 such lines in the user journal (below) |
| Obserwator's REST server, `develop` `9aefb23`; container `imgwtools-api` on 0.0.0.0:8000 since 2026-08-02 | uvicorn's default access log with the client's address to stdout, `json-file` without `max-size`; `docker/nginx.conf`: `log_format main` with `$remote_addr`, `error_log … warn` | IP addresses; no limit at all (267,131 lines, 62 with two LAN addresses) |
| Archiwista, `develop` `3a02da8`, user unit `archiwista-public` | warnings on stderr (`logs.py`), `serve.started` with the one-time sign-in URL on stdout, uvicorn's access log off unless `--access-log` | no files and no deletion; a credential-bearing URL in the journal (DEV-12.3) |

The user journal of `claude-agent` holds entries since 2026-10-06, the system journal since January; journald keeps them until its size limit, since `MaxRetentionSec` is not set, and changing that needs root and changes the whole host.

## Decisions

| Question | Decision | Why |
|---|---|---|
| Kinds | access, one record per HTTP request; app, warnings, errors and exceptions; lifecycle, start with a summary of the settings, stop, deletion of old files | what the operation needs: what was asked, what failed, when the server ran |
| Format | `nogat-log/1`: JSON Lines, UTF-8, one compact object per line; the keys of DEV-12.4 and no other (`schemas/log/record-1.schema.json` has `unevaluatedProperties: false`) | one reader for every server; a key not in the schema, such as `ip` or `user_agent`, fails validation |
| `time`, `request_id` | RFC 3339 in UTC with `Z`, milliseconds; 16 random hex digits made by the middleware, never taken from a header and never sent back | a time without zones to convert; an id a person could quote would tie a record to them |
| `user_agent` | dropped; its class `agent` is kept: `bot` when it names a robot (`bot`, `crawl`, `spider`, `headless`…), `browser` when it starts with `Mozilla/`, `script` for any other value, `none` without one | a full User-Agent with a time and a path can single out a person (the legal review of 2026-11-13, RODO art. 5 ust. 1 lit. c); telling robots, scripts and browsers apart is all the operation uses it for, and four values single out no one. The statistics keep reading the header in memory (DEV-15.11) |
| Query strings | kept; a parameter in `REDACTED` (`q`, `query`, `search`, `text`, `message`, `comment`, `address`, `name`, `user`, `username`, `login`, `email`, `mail`, `phone`, `key`, `token`, `password`, `secret`, `session`, `auth`, `signature`, `sig`) or whose name contains `token`, `secret`, `passw`, `apikey`, `api_key`, `session` or `mail` keeps its name and loses its value: `?q=&lat=51.2` | coordinates, station codes and limits explain a request; free text, names and credentials are what a person types about themselves |
| IP addresses in text | written `[ip]` in `path`, `message` and `error` | a library or a mistake must not break the regulamin's promise |
| Where | `<state_dir>/<project>/logs/<kind>-YYYY-MM-DD.jsonl`, by the UTC date; `state_dir` a new key of `[nogat]` (DEV-18.1), default `platformdirs.user_state_path("nogat")`, `~/.local/state/nogat` on Linux | logs are state, not data to back up (XDG); one tree for every server on a host |
| Containers | `NOGAT_STATE_DIR=/state` inside, the host's `<state_dir>/<project>` mounted at `/state/<project>`; the host directory writable by the container's user, as Hydrograf's `data/` is today | the files land on the host where a server outside Docker writes them and are read without `docker exec` |
| Deletion | by the server: a file goes once its date is 14 days old (a record of 2026-11-13T00:00Z goes at 2026-11-27T00:00Z), at start and at each 00:00 UTC by a daemon thread | needs no root, journald or Docker setting; a stopped server deletes its old files at its next start |
| Standard output and error | lifecycle records, and app records of level `error` and `critical` reduced to their type: `request_id` and `message` `null`, `error` `{"type": …}`; nothing else | the journal and Docker keep them beyond 14 days, so they name no request: no path, no query, no User-Agent, no message |
| Docker | logging driver `local`, `max-size: "1m"`, `max-file: "3"`, for every container of a deployment | nothing personal is printed, so a size cap suffices; the `journald` driver keeps entries without a time limit |
| nginx | option 1: `access_log off;`, the API writes the access log; `error_log /dev/null;`; no `X-Request-ID` | the API already sees every page (`X-Accel-Redirect` from the API) and every API call and tile; nginx cannot drop query parameters or write UTC `Z` times and `duration_ms`, so option 2 (nginx writing daily files that the API deletes) would be a second writer of one format. At every level, `crit` included, nginx names the client in errors of a request (an unknown TLS handshake failure is `crit`), which the dedicated server terminating TLS would write. Static files need no log |
| uvicorn | `access_log=False` and `log_config=None`, on the command line `--no-access-log --log-level warning`; the module's `AccessLog` outermost | uvicorn's access line names the client; its default configuration prints plain lines before the module starts |
| Static content | files, map tiles and documents the same for every client (Hydrolog's catalog) are logged only when answered with 400 or more | dozens of identical lines per page view tell nothing |
| Reading | one command per server over its files (below); usage numbers only from `stats.jsonl` (DEV-15.11) | the logs hold 14 days of requests for debugging, never counts of people |
| Implementation | `standards/reference/nogat_logging.py`, standard library only, copied byte for byte into each package; `drift` reports each copy and each copy of the schema as current, behind or modified | one implementation reviewed once, the kit's model (DEV-15.6) |
| Regulamin | § 8 ust. 3 of regulamin 1.0, unpublished, revised in place in kit 0.6.1: the access and error logs go after 14 days, messages about the server's start, stop and errors hold no request data, and the access log keeps the kind of program, „przeglądarka, robot albo inny program” | the text must stay true of what reaches the journal, and of the User-Agent no longer kept |
| Out of scope | Archiwista's action log in `state.sqlite` (actor, action, target, client address; 365 days by default, `action_log_retention_days`) is the app's record of its users' actions, not one of the three logs | the author decides whether a private tool's audit trail keeps addresses |

## The reference module

`standards/reference/nogat_logging.py` (standard library only; ruff and mypy `--strict` clean under the shared configuration):

| Name | Use |
|---|---|
| `ServerLog(app, version, directory, *, stream=None, clock=None)` | the logs of one server; `directory` is `<state_dir>/<project>/logs` |
| `ServerLog.start(settings=None)` | root logger's handlers replaced by one writing `app` records from `warning`; uvicorn's loggers sent to it, its access logger silenced; warnings and threads' uncaught exceptions captured; lifecycle `start` with the settings; old files deleted now and at each 00:00 UTC |
| `ServerLog.stop()` | lifecycle `stop`; previous handlers back; files closed |
| `ServerLog.lifecycle(event, message, *, level, settings)`, `.access(...)`, `.application(levelno, event, message, exc_info)`, `.prune()`, `.close()` | the records themselves, for a server that is not ASGI or has its own events |
| `AccessLog(app, log, quiet=None)` | the ASGI middleware: one access record per HTTP request; `quiet`, a regular expression over the path, names the static content; an exception leaving the app becomes one app record of the request and a 500; reads only method, path, query and User-Agent |
| `agent_class(ua)`, `redact_query(query)`, `scrub(text)`, `request_id()`, `REDACTED`, `REDACTED_PARTS`, `RETENTION_DAYS`, `FORMAT` | the rules as functions and constants |

```python
from <package>.nogat_logging import AccessLog, ServerLog

log = ServerLog("hydrolog", __version__, state_dir / "hydrolog" / "logs")
app.add_middleware(AccessLog, log=log, quiet=r"^/(css|src|vendor|nogat)/")  # added last

@asynccontextmanager
async def lifespan(app):
    log.start({"url": url, "public": public})
    yield
    log.stop()
```

## Steps

| # | Project | Change | Verified by |
|---|---|---|---|
| 1 | Nogat | DEV-12.4 to DEV-12.9, DEV-15.6, DEV-15.10, DEV-18.1, DEV-18.2, HUB-4.1, ECO-066; the module and the schema; `drift` reports their copies; kit 0.6.1 | unit and contract tests, a run under uvicorn 0.38 with proxy headers, the gate (done) |
| 2 | Hydrograf | below | its gate; on the test host a page, an API call, a 500 and a tile: records in `~/.local/state/nogat/hydrograf/logs/`, `docker logs hydro_api` with JSON lifecycle and reduced errors only, `docker inspect` showing `local` |
| 3 | Hydrolog | below | its gate; on :8070 the same, `journalctl --user -u hydrolog-gui` with JSON lines only |
| 4 | Obserwator GUI | below | the same on :8060 once the GUI replaces the mockup |
| 5 | Obserwator REST server | below | its gate; `docker logs` of its container |
| 6 | Archiwista | below | its gate; `journalctl --user -u archiwista-public` |

Each copies `standards/reference/nogat_logging.py` and `schemas/log/record-1.schema.json` byte for byte (DEV-15.6), names its reading command in its README, adds `state_dir` with `<TOOL>_STATE_DIR` to its README and `.env.example` (DEV-18.3), records the step in its CHANGELOG and PROGRESS, and drops its own access-log code and tests in favour of the module.

### 2. Hydrograf (`develop` `d515aad`)

- Copy the module to `backend/core/nogat_logging.py`; `backend/core/config.py`: the setting `state_dir` (`HYDROGRAF_STATE_DIR`, `NOGAT_STATE_DIR`, `[hydrograf]` or `[nogat] state_dir` of `NOGAT_CONFIG`).
- `backend/api/main.py`: `structlog.configure(...)` (52–70) and `logging.basicConfig(...)` (73–76) stop writing anywhere: structlog renders to the standard library (`structlog.stdlib.LoggerFactory()` with `structlog.stdlib.render_to_log_kwargs` last) or goes; `request_logger` (78) and `add_request_id` (143–175, which trusts nginx's `X-Request-ID` and sets the response header) go; `log = ServerLog("hydrograf", get_version(), Path(settings.state_dir) / "hydrograf" / "logs")`; `lifespan` (82–108) begins with `log.start({...})` and ends with `log.stop()` instead of `logger.info("Starting/Shutting down…")`; `app.add_middleware(AccessLog, log=log, quiet=r"^/api/tiles/")` after `app.middleware("http")(limit_and_count)` (140), so it is outermost and logs the 429s.
- `backend/Dockerfile` 85, `docker-compose.prod.yml` 17 and `docker-compose.override.yml` 8 (production runs with the override today): `--no-access-log --log-level warning`.
- `docker-compose.yml`: `logging:` of `db` (13–17), `api` (75–78) and `nginx` (130–133) become `driver: local` with `max-size: "1m"`, `max-file: "3"`, the comment on line 74 goes; `api` gains `NOGAT_STATE_DIR: /state` and `- ${NOGAT_STATE_DIR:-./state}/hydrograf:/state/hydrograf`; `.env` sets `NOGAT_STATE_DIR=/home/claude-agent/.local/state/nogat`, and `install -d -m 0777 ~/.local/state/nogat/hydrograf` once, so UID 999 writes there as it does in `data/`.
- `docker/nginx.conf` and `docker/nginx-ssl.conf.template`: `log_format hydrograf` (17–20; 13–16) goes, `access_log off;` (21; 17), `error_log /dev/null;` (22; 18), every `proxy_set_header X-Request-ID $request_id;` goes (63, 87, 138, 155, 166, 180; 73, 94, 143, 158, 169, 181); nginx has no `limit_req`, since the API limits (ADR-084). `docker/journald.conf` is deleted.
- Hydroni takes the same at its next update (its production command has `--workers 2` and no `--no-access-log`; the module writes safely from both processes).
- Reading: `jq -cs 'sort_by(.time)[] | select(.kind != "access" or .status >= 500)' ~/.local/state/nogat/hydrograf/logs/*.jsonl`; `docker logs hydro_api` for starts, stops and errors.

### 3. Hydrolog (`develop` `d9dc7f6`)

- Copy the module to `src/hydrolog/gui/nogat_logging.py`; `src/hydrolog/_settings.py` 53: `state_dir` in `KEYS`, default `platformdirs.user_state_path("nogat")`.
- `src/hydrolog/gui/_public.py`: `PublicGuard` (414–500) keeps the limit and the totals; its access line (`_ACCESS.info`, 476–484), `ACCESS_LOGGER` (76–77, 92) and `REQUEST_ID_HEADER` (90, 457) go. `AccessLog` writes the access log in every run, public or not, outside `PublicGuard`, `quiet=r"^/(css|src|vendor|nogat)/|^/theme-init\.js$|^/api/(commands|schemas)(/|$)"`.
- `src/hydrolog/gui/_serving.py`: `_access_log()` (71–92) goes; `uvicorn.Config(..., log_config=None, access_log=False)` (66–72) stays; the printed `Hydrolog GUI: <url>` (64) becomes `start`'s `settings` (`url`, `public`); `log.start`/`log.stop` around serving.
- The unit `hydrolog-gui` needs no change; the files go to `~/.local/state/nogat/hydrolog/logs/`.
- Reading: `jq -cs 'sort_by(.time)[] | select(.kind != "access" or .status >= 500)' ~/.local/state/nogat/hydrolog/logs/*.jsonl`.

### 4. Obserwator GUI (`feature/gui` `4c944fc`)

- Copy the module once to `src/obserwator/nogat_logging.py`, for the GUI and the REST server.
- `gui/_traffic.py`: `Traffic` keeps the limit and the totals; its access log goes: `LOG_DIR`, `LOG_DAYS` (67–68), `_prune_logs` (391–), the write of `access-YYYY-MM-DD.jsonl`, the record with `user_agent` (560–568) and `X-Request-Id` (530). `AccessLog` outermost, `quiet=r"^/(css|src|vendor|nogat)/|^/theme-init\.js$"`.
- `gui/_config.py`: the logs go to `<state_dir>/obserwator/logs` of the new key (`OBSERWATOR_STATE_DIR`, `NOGAT_STATE_DIR`); `stats.jsonl` and `feedback.jsonl` stay in the GUI's own directory, `<data_dir>/obserwator` (DEV-15.11, DEV-15.12).
- `gui/_serving.py` 130–135 keeps `log_config=None`, `access_log=False`; the printed `gui.server.listening` (108–109) becomes `start`'s `settings`.
- Until the GUI replaces it, the mockup's unit keeps `--no-access-log` and adds `--log-level warning`.
- Reading: `jq -cs 'sort_by(.time)[] | select(.kind != "access" or .status >= 500)' ~/.local/state/nogat/obserwator/logs/*.jsonl`.

### 5. Obserwator REST server (`develop` `9aefb23`)

- `cli/main.py` 66–93 (`server`) and `api/main.py` 221–226 (`run_server`): `uvicorn.run(..., access_log=False, log_config=None)`; the printed `cli.server_starting` becomes `start`'s `settings`; `obserwator.api.main` adds `AccessLog` last and calls `log.start`/`log.stop` in its lifespan, with `ServerLog("obserwator", __version__, …)`. Beside the GUI on one host both write `<state_dir>/obserwator/logs`; each line is one write, and `start`'s `settings` tell the two apart.
- `docker/Dockerfile` 39: `--no-access-log --log-level warning`; `docker/docker-compose.yml`: `logging: driver: local` (`1m`, `3`) for `app` and `nginx`, `NOGAT_STATE_DIR: /state` with the mount of `<state_dir>/obserwator`; `docker/nginx.conf`: `error_log /dev/null;` (2), `log_format main` goes (16–18), `access_log off;` (20); its `limit_req` zones (38–39) stay, now unlogged.
- The container `imgwtools-api` (image `docker-app`, built 2026-08-02 from an old IMGWTools worktree) logs uvicorn's lines with client addresses into an uncapped `json-file`: once replaced by the migrated image or removed, Docker deletes that file with the container, without root.

### 6. Archiwista (`develop` `3a02da8`)

- Copy the module to `src/archiwista/nogat_logging.py`.
- `server.py`: `uvicorn_log_config()` (89–103) with its `TokenRedactionFilter` goes; `log_config=None`, `access_log=False` (394–397); the option `--access-log` goes (`cli.py` 178–181, 298). `AccessLog` outermost, `quiet=r"^/static/|/tiles/\d+/\d+/\d+\.png$"`; `log.start`/`log.stop` around serving.
- `logs.py` 100–121: while serving, no handler of its own on the `archiwista` logger (`propagate = False` would keep printing beside the module); the job and preview workers (`jobs/worker.py` 264, `previews/worker.py` 157) log through a `ServerLog` of the same directory instead of `basicConfig` on stderr (several processes append safely; only the server deletes).
- `serve.started` (590–610) prints the one-time sign-in URL to stdout and so into the journal: the record `start` carries the origin only, and the URL goes to a terminal only (DEV-12.3: no credential-bearing URL in a log).
- Reading: `jq -cs 'sort_by(.time)[] | select(.kind != "access" or .status >= 500)' ~/.local/state/nogat/archiwista/logs/*.jsonl`, with `state_dir` of the unit's environment (it sets `XDG_*` to `~/data/archiwista-public/`).

## Reading the logs

The command of each server above shows the last 14 days in time order without successful requests: starts, stops, deletions, warnings, errors and 5xx answers. Other questions, for example:

- `jq -r 'select(.kind == "access") | "\(.status) \(.agent)"' <logs>/access-*.jsonl | sort | uniq -c`: answers by status and kind of client;
- `jq -c 'select(.request_id == "3f2a9c1b8e7d6c5a")' <logs>/*.jsonl`: one request with its errors.

jq is not installed on today's host: `apt install jq` (root, once) or jq's static release binary in `~/.local/bin` (no root). Usage is counted only from `<data_dir>/<project>/stats.jsonl` (DEV-15.11): daily totals of visitors, page views, stations, analyses and downloads, kept without a limit and never derived from the logs, which hold no visitor and are gone after 14 days.

## Journal entries written before the migration

Measured on 2026-11-13 in the user journal of `claude-agent` (`journalctl --user`): `obserwator-public.service` wrote 673 uvicorn access lines with a client's address, 499 IPv4 and 174 IPv6, of two addresses, between 07:35 and 21:05 CET, besides 317 with 127.0.0.1; all lie in the active file `/var/log/journal/752502a2ac8b4926b0120f6fde0fbd46/user-2001.journal`. Hydrolog's and Archiwista's units wrote no address other than 127.0.0.1. The journal files and their directory belong to root (`root:systemd-journal`, the file readable by UID 2001 through an ACL, group `adm` read-only) and journald deletes only whole files, so without root no entry can be removed: `journalctl --user --rotate` and `--vacuum-*` need write access to that directory.

- Without root, the narrowest step is done: the unit stopped writing them at 21:05 (`--no-access-log`); they stay readable only by `claude-agent`, root and `adm`, and nothing exports or copies them.
- The narrowest removal is one root step by the author, after steps 3 to 6 so that nothing new arrives: `sudo journalctl --rotate`, then `sudo find /var/log/journal/752502a2ac8b4926b0120f6fde0fbd46 -name 'user-2001@*.journal' -delete`. It deletes only `claude-agent`'s user journal up to that moment: the 673 lines, Hydrolog's lines since 2026-11-05 and the rest of the user units' history since 2026-10-06; the system journal and every other user's stay.
- Hydrograf's containers log through the `journald` driver into the system journal, which `claude-agent` cannot read; lines written before Hydrograf dropped `$remote_addr` from nginx (ADR-084) may still hold addresses. The author checks with `sudo journalctl CONTAINER_NAME=hydro_nginx | grep -cE '([0-9]{1,3}\.){3}[0-9]{1,3}'` (Chrome's versions, such as `Chrome/131.0.0.0`, match too). The system journal holds the host's history since January, so `--vacuum-time` is not narrow; removing those lines alone is not possible.
- `json-file` logs of containers (`imgwtools-api`, `hydro_db`, `hydroni_*`) go with their containers when they are recreated after the migration (`docker compose up -d --force-recreate`, docker group, no root).

## Results

- Step 1: commit on Nogat `feat/unified-logging` (see `CHANGELOG.md`); gate green. A run of the module under uvicorn 0.38 and Starlette 1.10 with `--proxy-headers --forwarded-allow-ips '*'` and `X-Forwarded-For`, `X-Real-IP` and `CF-Connecting-IP` set: no address in any file or on stderr, `?q=&email=&bbox=…` logged, one app record for a 500 that uvicorn reported too, stderr only JSON lifecycle and one reduced error, no `X-Request-Id` in the answers, the file of 2026-10-20 deleted at start.
