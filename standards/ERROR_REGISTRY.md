# Shared error registry

Version 2.0 · 2026-10-19 · IDs `ERR-…` · source of truth:
[error_registry.json](error_registry.json) (this page explains it).

One registry for every project (ECO-015). An exit code or HTTP status means the
same thing whichever tool produced it, so agents, Retman and shell scripts can
chain tools without per-tool tables.

---

## 1. Outcomes (not errors)

| Status | Exit | Meaning |
|---|---|---|
| `ok` | 0 | completed for every unit |
| `partial` | 10 | batch completed for some units; per-unit status in `items[]` |
| `failed` | 11 | batch ran, no unit succeeded; per-unit codes in `items[]` |
| `cancelled` | 130 | cancelled by the user (Ctrl+C, declined plan, MCP cancellation) |

*Why:* IMGWTools separates "the run finished with failed units" from "the run
could not start". An agent retries units in the first case and fixes the call
in the second. Exit codes 10 and 11 never mean an error.

## 2. Errors

| Code | Exit | HTTP | Meaning |
|---|---|---|---|
| `internal_error` | 1 | 500 | defect in the tool, unexpected exception |
| `validation_error` | 2 | 400 | unknown command or option, wrong type, value not allowed, missing option |
| `not_found` | 3 | 404 | referenced file, resource, station, identifier does not exist |
| `conflict` | 4 | 409 | version collision, lock held, identifier taken |
| `source_unavailable` | 5 | 502 | remote service failed: timeout, connection, HTTP error, download failure |
| `missing_dependency` | 6 | 503 | extra or external program not installed |
| `data_error` | 7 | 500 | data read by the tool is malformed (file, archive, sidecar, stored series) |
| `store_unavailable` | 8 | 503 | store or cache unusable: no marker, locked, unreadable, share disconnected |
| `io_error` | 9 | 500 | file system failure: permissions, space, missing path |
| `forbidden` | 12 | 403 | path outside allowed roots, write in read-only mode, insufficient role |
| `calculation_error` | 13 | 422 | valid input, no computable result (no convergence, short series, failed transformation) |
| `no_data` | 14 | 404 | valid request, source has no data for the area, period or product |
| `unsupported` | 15 | 422 | valid request, unsupported combination or outside the tool's scope |
| `cancelled` | 130 | – | user or SIGINT |
| `terminated` | 143 | – | SIGTERM |
| `unauthorized` | – | 401 | REST only |
| `method_not_allowed` | – | 405 | REST only |
| `rate_limited` | – | 429 | REST only |

Titles in English and Polish are in the JSON file.

*Why the numbers:* 1–9 keep IMGWTools' assignments, the most complete
registry and already shared with Hydrolog for 2, 3, 6, 7 and 9. New codes
take 12–15, so they cannot collide with the outcomes 10 and 11. This resolves
the existing collisions:
- 4 meant `conflict` in IMGWTools and `calculation_error` in Hydrolog.
- 8 meant `store_unavailable` in IMGWTools and `forbidden` in Hydrolog.
- In Kartograf, 1 mixed domain outcomes (`no_coverage`, `download_failed`)
  with defects.

130 and 143 follow the 128+signal convention.

## 3. Rules

**ERR-1** Every raised error carries exactly one registry `code`. Projects MUST
NOT invent codes. Finer distinctions go to `details.reason` as snake_case
English (`no_coverage`, `invalid_sheet_code`, `year_out_of_range`).
*Why:* consumers branch on `code`; `reason` keeps project precision without
fragmenting the registry.

**ERR-2** The registry grows only through a new version of this standard; a
project that needs a new code proposes it in Nogat.

**ERR-3** Each project vendors the registry as generated code (for example
`src/<package>/_errors.py`) and a contract test compares it with
`error_registry.json` of the pinned standard version.

**ERR-4** Interfaces report errors as follows:
- Python: `<Project>Error` subclass with `code`, `message`, `hint`, `details`.
- CLI: last line of stderr is `<prefix>-error/1`; exit code from the table.
- MCP: `isError: true` with the error document.
- REST: `application/problem+json` with `type` pointing to this page's anchor
  for the code, `status` from the table, plus `code`, `hint`, `details`.

**ERR-5** Every error has a `hint` when a fix is known: the option to change,
allowed values, the command to run (`uv add "kartograf[mcp]"`).
*Why:* the hint lets an agent fix the call in one retry instead of a guess.

**ERR-6** `message` and `title` follow the active language (AGI-9.2); `code`,
`details` keys and `reason` never change with language.

## 4. Mapping of current project codes

Applied during adoption; breaking changes are accepted (ECO-020).

| Project | Current | New `code` (`details.reason`) | Exit change |
|---|---|---|---|
| Kartograf | `invalid_input`, `usage_error` | `validation_error` (`invalid_input`, `usage`) | 2 → 2 |
| Kartograf | `invalid_sheet_code` | `validation_error` (`invalid_sheet_code`) | 2 → 2 |
| Kartograf | `no_coverage` | `no_data` (`no_coverage`) | 1 → 14 |
| Kartograf | `year_out_of_range` | `no_data` (`year_out_of_range`) | 1 → 14 |
| Kartograf | `download_failed` | `source_unavailable` | 1 → 5 |
| Kartograf | `io_error` | `io_error` | 1 → 9 |
| Kartograf | `cache_error` | `store_unavailable` (`cache`) | 1 → 8 |
| Kartograf | `invalid_sidecar` | `data_error` (`invalid_sidecar`) | 1 → 7 |
| Kartograf | `transform_failed` | `calculation_error` (`transform_failed`) | 1 → 13 |
| Kartograf | `transform_unavailable` | `unsupported` (`transform_unavailable`) | 1 → 15 |
| Kartograf | `interrupted` | `cancelled` | 130 |
| Kartograf | result `ok: false` | envelope `status: partial` or `failed` | 1 → 10 / 11 |
| IMGWTools | `forbidden` (REST only) | `forbidden` | none → 12 |
| IMGWTools | others | unchanged | – |
| Hydrolog | `calculation_error` | `calculation_error` | 4 → 13 |
| Hydrolog | `forbidden` | `forbidden` | 8 → 12 |
| Hydrolog | output not writable | `io_error` (`output_unwritable`) | 9 |
| Archiwista | exception classes, RFC 9457 without registry | map each class to a registry code | new |
| Retman | exit 3 (cancelled), 4 (out of scope) | `cancelled` 130, `unsupported` 15 | changed |
| Hydraulik, Hydrograf | no registry | adopt | new |

Kartograf codes not listed are mapped in its adoption step by the same rules.
