# Plan: one admin panel for every GUI

Approved: 2026-11-13, the author (in session)

Status: done 2026-11-14 except the author's Cloudflare Access rules of step 6. Steps 1 to 5 merged into the `develop` of Nogat, Hydrolog, Hydrograf, Obserwator and Archiwista and deployed with their keys ([Results](#results)); no tags, no release.

Requirements: DEV-15.6 (kit copied byte for byte), DEV-15.11, DEV-15.12, DEV-18.4, AGI-6.3 (error documents), HUB-5.2 (producers before consumers), DEV-17.5.

## Goal

The operator handles each GUI in the same place and the same way. Today every GUI does it differently:

| GUI | Page | Sign-in | What it offers |
|---|---|---|---|
| Hydrograf | `/admin.html` (`/admin` rewritten to it), Bootstrap 5, the only Bootstrap page of the app | `X-Admin-Key` against `ADMIN_API_KEY` or `ADMIN_API_KEY_FILE`; without one it draws a random key and logs it as a warning | reports; dashboard and resources; DEM bootstrap; cleanup; boundary and sewer upload |
| Hydrolog | `/admin/` (`/admin` answers 307), Preact on the tokens | `X-Admin-Key` against `HYDROLOG_ADMIN_API_KEY` or `HYDROLOG_ADMIN_API_KEY_FILE`, read per request; without one `401 admin_key_not_configured` | reports |
| Obserwator | none; reports read with `jq` from `feedback.jsonl`, a recorded deviation from DEV-15.12 | none | none |
| Archiwista (private) | the view „Zgłoszenia” of the app | accounts with the role `admin` (team mode) or the local owner | reports; users and groups |

The author decided on 2026-11-13: every panel offers „Zgłoszenia”, „Statystyki” and „Stan” from the Nogat kit, an app's own functions are further sections of the same shell, and Archiwista uses the same views from the kit while keeping its own sign-in.

## The standard: DEV-15.13 (new), ECO-067

**Where.** A GUI that stores reports (DEV-15.12) or statistics (DEV-15.11) serves its admin panel at `/admin/` and its admin API under `/api/admin/`. `/admin` answers `308` to `/admin/`. No other admin path exists, so a deployment protects exactly `/admin`, `/admin/*` and `/api/admin/*` (Cloudflare Access on the test deployment). An app with an API prefix of its own keeps it (Archiwista: `/api/v1/admin/`).

**Sign-in.** Every admin route checks the header `X-Admin-Key` in constant time against the credential `admin_api_key`, read per request from the environment variable `<PREFIX>ADMIN_API_KEY` or the file named by `<PREFIX>ADMIN_API_KEY_FILE` (DEV-18.4), where `<PREFIX>` is the prefix of the tool's other settings (Hydrograf none, Hydrolog `HYDROLOG_`, Obserwator `OBSERWATOR_`). Failures answer `401` with the error document of `unauthorized` (AGI-6.3) and the reason `admin_key_not_configured`, `admin_key_missing` or `admin_key_invalid`. No key is generated and none is ever logged. The page keeps the key in `sessionStorage` under `<project>/admin-key/1`; „Wyloguj” forgets it. An app with accounts replaces the key with its own role check and keeps everything else.

**Core API**, identical in every GUI:

| Route | Answer |
|---|---|
| `GET /api/admin/feedback?limit=&offset=` | `{items, total, unread_count}`, newest first; `limit` 1 to 200, default 50 |
| `PATCH /api/admin/feedback/{id}` with `{"is_read": bool}` | the report |
| `DELETE /api/admin/feedback/{id}` | `{"status": "deleted"}`; an unknown id answers `404 not_found` |
| `GET /api/admin/stats?from=&to=` | `{days, totals}`: the lines of `stats.jsonl` (DEV-15.11) between the two UTC days, default the last 30, plus the current day as counted so far; `totals` sums every key but `visitors` |
| `GET /api/admin/status` | `{app, version, started_at, uptime_s, data_dir, disk: {free_bytes, total_bytes}, checks: [{name, status, detail}]}`, `status` one of `ok`, `warning`, `failed`; each GUI names its checks in its README |

An app's own sections use routes of their own under `/api/admin/`.

**The page.** It is the operator's, not a public view: no footer statement, regulamin link, app menu or stats count (DEV-15.8, DEV-15.11 do not apply to it); `<meta name="robots" content="noindex">`; every admin answer `Cache-Control: no-store`; CSP `'self'`; requests to it stay under the rate limit (DEV-15.9).

## The kit: 0.7.0

`design/kit/nogat-admin.js` and `nogat-admin.css`, framework-free custom elements on the tokens, no external resources, Polish texts:

- `<nogat-admin app="Hydrolog" project="hydrolog" back="../">`: the shell. Top bar „Hydrolog · Administracja” with „Wróć do aplikacji” and „Wyloguj”; the key prompt; the navigation „Zgłoszenia”, „Statystyki”, „Stan”, then each child `<section data-admin-section="id" data-label="…">` of the app in document order; the section in the URL hash. It exposes `adminFetch(path, init)`, which adds the key and returns to the prompt on `401`, for the app's sections, and an `auth` property an app with accounts sets to `"session"` so no key is asked and requests carry its cookie.
- `<nogat-admin-feedback endpoint="api/admin/feedback">`: the reports, 50 per page, the unread count, „Tylko nieprzeczytane”, „Oznacz jako przeczytane” and back, „Usuń” after a confirmation, the context folded under each report.
- `<nogat-admin-stats endpoint="api/admin/stats">`: the table of days (data, odwiedzający, odsłony, otwarte stacje, obliczenia, pobrania) for 7, 30 or 90 days or the whole record, a totals row in which visitors appear as „suma dziennych odwiedzających”, and the table as CSV.
- `<nogat-admin-status endpoint="api/admin/status">`: version, uptime, data directory, free disk, and the checks with their status.

Each element also works alone, which is how Archiwista uses `<nogat-admin-feedback>` inside its own view.

## Steps

1. **Nogat**: DEV-15.13 and ECO-067; DEV-15.12 points its operator routes to DEV-15.13 and loses its Obserwator exception; kit 0.7.0 with `nogat-admin.*`, `design/README.md` and a specimen page backed by a fake API; contract tests (routes, fields and texts as documented) and browser tests (prompt, `401` back to the prompt, the three views against the fake API, an app section in the navigation, Esc and focus in the confirmation, both themes, 390 px, CSP `'self'`, nothing loaded but the kit).
2. **Hydrolog**: copy kit 0.7.0; `web/admin/` becomes the kit shell; add `stats` and `status` (checks: data directory writable, the reports database); `/admin` answers 308; its own Preact admin removed.
3. **Hydrograf**: copy kit 0.7.0; `/admin.html` becomes `frontend/admin/index.html` on the kit shell, nginx serves `/admin/` and redirects `/admin`, `/admin.html` is removed; its sections „Zasoby”, „Przetwarzanie NMT”, „Czyszczenie” and „Granice i kanalizacja” are rewritten on the tokens with `adminFetch`, Bootstrap removed; `dashboard` folds into `status` (checks: database, catchment graph, data directory); the generated key goes, so no key means `401 admin_key_not_configured`. The deployment keeps `ADMIN_API_KEY`.
4. **Obserwator**, on `feature/gui` before the public switch: `OBSERWATOR_ADMIN_API_KEY` and `_FILE`; the feedback routes over `feedback.jsonl`, rewritten atomically under the file lock it already takes; `stats` and `status` (checks: data root marker, stored analyses, the Hydrolog command); the kit page; the deviation and the `jq` instructions removed. The REST keys of `obserwator admin` stay separate and are named so.
5. **Archiwista**: copy kit 0.7.0; the view „Zgłoszenia” renders `<nogat-admin-feedback endpoint="/api/v1/admin/feedback">` with `auth="session"`; its account sign-in and its users and groups views stay. It keeps no statistics, so it has no „Statystyki”; „Stan” is out of scope for this private app.
6. **Deployment**: each GUI deployed with its key set (Hydrolog and Obserwator: a key file of mode 0600 named by the unit); on the test deployment the author sets Cloudflare Access on `/admin`, `/admin/*` and `/api/admin/*` of hydrograf-test, hydrolog-test and obserwator-test, leaving the rest public, and archiwista-test unchanged.

Each project checks in its own gate that the core routes answer as documented, that every admin route refuses a missing, wrong or unconfigured key, and that its page is the kit shell.

## Not in scope

Logs in the panel (the unified logging, decided on its own on `feat/unified-logging`, writes files the operator reads directly), accounts for the public GUIs, and a shared admin across GUIs (the future „GUI hub”).

## Results

- 2026-11-13, step 1: Nogat `096ec51`, merged into `develop` at `229ade3` (DEV-15.13, ECO-067, kit 0.7.0).
- 2026-11-14, step 2: Hydrolog `cddfd1e` (kit 0.7.0) and `3da4b3b`, merged at `5286cb0`.
- 2026-11-14, step 3: Hydrograf `0c64490` and `132d93f` (ADR-086), merged at `aa975b0`.
- 2026-11-14, step 4: Obserwator `9d921cb` (ADR-020), merged at `0591b82`.
- 2026-11-14, step 5: Archiwista `0981a4d`, merged at `b6b56d8`.
- 2026-11-14, step 6: the four GUIs deployed with the panel and their keys. Open: Cloudflare Access on `/admin`, `/admin/*` and `/api/admin/*`, the author's step.
