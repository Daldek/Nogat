# Plan: user feedback in Archiwista and Hydrolog

Approved: 2026-11-03 (the author: "the same mechanism as Hydrograf"); the
decisions below by delegated approval.

Requirements: DEV-18.2, DEV-18.4, DEV-2.3, ECO-055.

## Goal

Archiwista and Hydrolog get Hydrograf's feedback mechanism: a „Zgłoś uwagę”
button in the top bar opens a dialog; the report is stored by the app and an
administrator reads, marks and deletes reports in the app.

## Facts (Hydrograf `develop`, the reference)

- Table `feedback` (`backend/migrations/versions/002_feedback.py`): `id`,
  `created_at`, `message` (1–5000 characters), `contact` (≤ 200, optional),
  `page_url`, `user_agent` (≤ 500), `diagnostics` (JSON ≤ 100 KB),
  `is_read`; newest first.
- `POST /api/feedback` (no key) → `{id, status: "ok"}`;
  `GET /api/admin/feedback?limit&offset` → `{items, total, unread_count}`;
  `PATCH /api/admin/feedback/{id}` `{is_read}`; `DELETE
  /api/admin/feedback/{id}`; admin endpoints need `X-Admin-Key`
  (`backend/api/endpoints/feedback.py`, `backend/api/dependencies/admin_auth.py`).
- Dialog (`frontend/js/feedback.js`): message with a live counter, optional
  contact, „Dołącz dane diagnostyczne” (checked, with a preview), Anuluj /
  Wyślij, a status line; closes 2 s after success. Diagnostics
  (`frontend/js/diagnostics.js`): a ring buffer of 50 events (JS errors, API
  calls with status, duration and request id), the workspace state and the
  environment, ≤ 100 KB. Admin list (`frontend/js/admin/admin-feedback.js`):
  date, excerpt, unread badge, details, read toggle, delete; DOM built with
  `textContent` only.
- Archiwista: FastAPI under `/api/v1`, Preact without a build, a state
  SQLite database with migrations by `PRAGMA user_version`
  (`src/archiwista/state/schema.py`), accounts with the role `admin`
  (local mode: the local user).
- Hydrolog: the GUI is Starlette (`src/hydrolog/gui/_app.py`, `:8070`),
  Preact, Polish UI, per-session folders, no database and no administrator.

## Decisions

| # | Decision |
|---|---|
| D1 | Same behaviour, limits, texts and response shapes as Hydrograf; each app has its own copy (the shared shell of the GUI platform plan may extract one widget later). |
| D2 | Archiwista stores reports in its state database: a new migration adds the table `feedback`; `POST /api/v1/feedback` for any signed-in user; `GET`, `PATCH`, `DELETE /api/v1/admin/feedback[/{id}]` for the role `admin`, as the other admin routes; the list in the admin view. |
| D3 | Hydrolog stores reports in SQLite `<data_dir>/hydrolog/feedback.sqlite3` (DEV-18.2), created on the first report; `POST /api/feedback` for a GUI session; the admin endpoints `/api/admin/feedback[/{id}]` need `X-Admin-Key` from `HYDROLOG_ADMIN_API_KEY` or `HYDROLOG_ADMIN_API_KEY_FILE` (DEV-18.4), refused with 401 when no key is set (no generated key); an admin page `/admin/` lists the reports after the key is entered. |
| D4 | Diagnostics collect only what the user sees in the app (events, the current view and its parameters, the environment), never file contents or tokens; the preview shows exactly what is sent. |
| D5 | Error documents follow each app's error registry use (ERR); texts in Polish and English where the app has both, Polish in Hydrolog's GUI. |
| D6 | Each README documents where reports live, how to read them and how to back them up (SQLite `.backup`). |

## Steps

| # | Project | Change | Verified by |
|---|---|---|---|
| 1 | Archiwista | D2, D4–D6, after its Obserwator migration is merged | its gate, a browser smoke |
| 2 | Hydrolog | D3–D6, after its Obserwator rename is merged | its gate, a browser smoke |

## Results

Step 2, Hydrolog (2026-11-03, `2eb8bd0`): `<data_dir>/hydrolog/feedback.sqlite3`,
`POST /api/feedback`, `/api/admin/feedback[/{id}]` with `X-Admin-Key`
(`HYDROLOG_ADMIN_API_KEY[_FILE]`, 401 when unset), the admin page `/admin/`;
gate green (one known flaky e2e test, passing on rerun). Step 1, Archiwista
(2026-11-04, `e479219`): state schema 5 with `feedback`, `POST
/api/v1/feedback`, `/api/v1/admin/feedback[/{id}]` for the role `admin`,
the admin view „Zgłoszenia”; no request id exists, so its diagnostics keep
the problem code and reason instead; gate green (2,782 passed). Neither is
deployed.
