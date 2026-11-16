# Plan: Obserwator's result, error and catalog documents follow standard 1.0

Approved: 2026-11-04 (the author: "start" on the v3.0.0 blocker B6); the
decisions below by delegated approval.

Requirements: AGI-2.4, AGI-3.2, AGI-3.3, AGI-3.4, AGI-4.1 to AGI-4.4,
AGI-5.6, AGI-5.7, AGI-6.3, AGI-6.5, ERR-3, ECO-056, HUB-5.2.

## Goal

Before its first release as Obserwator (v3.0.0) the tool's machine documents
validate against Nogat's `schemas/agent/` (`result-1`, `error-1`,
`commands-1`), its CLI has `--json`, and its collections page by cursor.
Every change is breaking for an unreleased document, so the ids stay `/1`
(ECO-056); consumers move with the producer (HUB-5.2).

## Facts (Obserwator `develop` `88ac772`, 2026-11-04)

- `CommandResult.to_json` (`src/obserwator/store/types.py:1287`) writes
  `schema, command, check, status, result, notices`: no `tool`, `version`,
  `items` or `page`. A paged command returns `Page(items, total, limit,
  offset)` as its `result` (`commands.py:2521-2587`); the option is
  `--offset` (`commands.py:507`), in REST and MCP too.
- The CLI error line (`cli/_dispatch.py:233`) and the MCP error
  (`mcp/_calls.py:98`) are `{code, detail, details}`; REST is
  problem+json with `type, title, status, detail, code, details`
  (`api/errors.py:55`).
- The CLI always prints the envelope; there is no `--json` and no human
  rendering.
- `list_commands` and `command_schema` (`commands.py:3317`, `3232`) fail
  `commands-1` (318 and 361 errors, release audit of 2026-11-03).
- No copy of `schemas/agent/` or `error_registry.json` (ERR-3).
- Consumers: Retman and Archiwista call the Python command layer and read
  the envelope; Hydraulik calls `fetch_pmaxtp` and names `obserwator pmaxtp
  fetch` in its texts; Hydrograf calls `fetch_pmaxtp` only.

## Decisions

| # | Decision |
|---|---|
| D1 | The envelope gains `tool` (`"obserwator"`) and `version` (`__version__`). `items` stays absent until a batch command reports units (optional field, addable later). |
| D2 | A paged command returns the list of its items as `result` and the envelope's `page` `{total, next_cursor, truncated}`. `--offset` becomes `--cursor` (CLI, REST `cursor`, MCP `cursor`): an opaque string (the URL-safe base64 of the next index), refused with `validation_error` when malformed. The default page stays within DOC-1.7. |
| D3 | The error document `obserwator-error/1` has `schema, code, title, message, hint?, details, exit_code, command?`: `message` is the former `detail`; `title` and `hint` come from the registry and the message catalogue; the CLI's last stderr line and the MCP error are that document in English; REST keeps problem+json and adds `hint` (AGI-6.3). |
| D4 | `--json` prints exactly the envelope; without it the CLI prints a short human rendering in the `--lang` language (status, counts, the result's main fields, notices), so the default output is no longer JSON. Data streams (`store export`, `series export` to stdout) are unchanged. |
| D5 | `list_commands` and `command_schema` validate against `commands-1`. |
| D6 | `schemas/nogat/` holds copies of `result-1`, `error-1`, `commands-1` and `error_registry.json` from Nogat `develop` (README records the commit; refreshed from `std-1.0` at the tag); contract tests validate every document of the CLI, REST, MCP and Python against them. |
| D7 | Obserwator records the change as ADR-010 and a CHANGELOG Breaking entry with migration lines. |

## Steps

| # | Project | Change | Verified by |
|---|---|---|---|
| 1 | Obserwator | D1–D7 | its gate, the CI matrix |
| 2 | Nogat | `set bump Obserwator` | `set check` |
| 3 | Retman, Archiwista, Hydraulik, Hydrolog | `set apply`; follow `page`/`cursor`, `message`, `--json` where they use them; Archiwista's range `>=3.0.0.dev0,<4` | each gate |

## Results

2026-11-04, all three steps done.

| # | Project | Commit (merge into its integration branch) | Verified by |
|---|---|---|---|
| 1 | Obserwator | `develop` `1ee5457` (D1–D7, ADR-010); follow-ups `cfde74d` (CHANGELOG entries in the final shapes, `StoreInfo.schema` → `store_schema`) and `84e43a1` (the guide names the `commands-1` fields; the MCP instructions stay below 2 KiB with macOS temp paths) | gate 2634 passed; CI on ubuntu, macOS and Windows green on `84e43a1` (`1ee5457` failed only the 2 KiB test on macOS) |
| 2 | Nogat | `candidate-1`: Obserwator `ea158dc` → `1ee5457` (`d672083`) | `set check` ok for every consumer |
| 3 | Retman | `develop` `bc272e2`: list `result` with `page`, notice and error `message`, `hint`, the audit line with `--json`, a catalog reader of `commands-1` | gate 3361 passed; smoke of the 21 Obserwator operations: everything except the large daily sync (time box) and the export that depends on it |
| 3 | Archiwista | `develop` `4ac2933`: range `>=3.0.0.dev0,<4`, `StoreInfo.store_schema`, Obserwator's `hint` passed on | gate 2783 passed (61 min); e2e of the adapter 82 passed |
| 3 | Hydraulik | `feature/sfincs-swmm` `9fc9572`: the texts name `obserwator pmaxtp fetch --json` | gate (823 passed); a live document of the new CLI read by `read_pmaxtp_document` equals `fetch_pmaxtp` |
| 3 | Hydrograf | `develop` `9e50785` (pin only; it calls `fetch_pmaxtp`), production rebuilt (`812a432` records it) | gate 1430 passed; in the image obserwator 3.0.0.dev0; `/health`, a design hydrograph, `fetch_pmaxtp` in the container, 404 problem+json, admin 401 |

Deviations: `commands list` stays the summary `obserwator-command-list/1`. The full catalog in
`commands-1` is 87 kB, over the 50 kB document limit (DOC-1.7), the same as in Kartograf and
Hydrolog; AGI-2.4's wording needs a decision in the standard. The `--json` and `--lang` flags are
run flags of `parse_command`/`format_command`, not options of `commands-1`, as in Kartograf.
Hydrolog had no Obserwator call to migrate. The set keeps `1ee5457`: `84e43a1` changes only
guide texts and a test, so it waits for the next bump.

Not caused by this plan: Retman's CI fails on macOS (a store under `/var`, a symlink) and on
Windows (paths, encoding) since before `01a4efd`; ubuntu is green.
