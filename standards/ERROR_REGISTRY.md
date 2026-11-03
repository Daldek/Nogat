# Shared error registry

Part of standard 2.1 · IDs `ERR-…`

[error_registry.json](error_registry.json) is the source of truth; this page
explains it.

One registry for every project (ECO-015). An exit code or HTTP status means the
same thing whichever tool produced it, so agents, Retman and shell scripts can
chain tools without per-tool tables.

---

## 1. Outcomes (not errors)

<!-- generated: error-outcomes from error_registry.json by `uv run scripts/ecosystem.py standard --write`; do not edit -->
| Status | Exit | Meaning |
|---|---|---|
| `ok` | 0 | Operation completed for every unit. |
| `partial` | 10 | Batch operation completed for some units; per-unit status in items[]. |
| `failed` | 11 | Batch operation ran but no unit succeeded; per-unit codes in items[]. |
| `cancelled` | 130 | Cancelled by the user (Ctrl+C, declined plan, MCP cancellation). |
<!-- end generated -->

*Why:* an agent retries units when the run finished with failed units and
fixes the call when the run could not start. Exit codes 10 and 11 never mean
an error.

## 2. Errors

<!-- generated: error-codes from error_registry.json by `uv run scripts/ecosystem.py standard --write`; do not edit -->
| Code | Exit | HTTP | Meaning |
|---|---|---|---|
| <a id="internal_error"></a>`internal_error` | 1 | 500 | Defect in the tool or an unexpected exception. |
| <a id="validation_error"></a>`validation_error` | 2 | 400 | Unknown command or option, wrong type, value out of range or not allowed, missing required option, violated exclusion rule. |
| <a id="not_found"></a>`not_found` | 3 | 404 | Referenced file, resource, station, project or identifier does not exist. |
| <a id="conflict"></a>`conflict` | 4 | 409 | Operation conflicts with current state: version collision, lock held, identifier taken. |
| <a id="source_unavailable"></a>`source_unavailable` | 5 | 502 | Remote service failed: timeout, connection error, HTTP error, download failure. |
| <a id="missing_dependency"></a>`missing_dependency` | 6 | 503 | Feature needs an extra or an external program that is not installed; hint names the install command. |
| <a id="data_error"></a>`data_error` | 7 | 500 | Data read by the tool (input file, archive, sidecar, stored series) is malformed or violates its format. |
| <a id="store_unavailable"></a>`store_unavailable` | 8 | 503 | Data store or cache cannot be used: missing marker, locked, unreadable, network share disconnected. |
| <a id="io_error"></a>`io_error` | 9 | 500 | Reading or writing files failed: permissions, no space, path missing. |
| <a id="forbidden"></a>`forbidden` | 12 | 403 | Path outside allowed directories, write attempted in read-only mode, insufficient role. |
| <a id="calculation_error"></a>`calculation_error` | 13 | 422 | Input is valid but no result can be computed: no convergence, series too short, numerical failure, transformation failed. |
| <a id="no_data"></a>`no_data` | 14 | 404 | Request is valid but the source has no data for the area, period or product requested. |
| <a id="unsupported"></a>`unsupported` | 15 | 422 | Request is valid but this combination is not supported: no safe CRS transformation, product not offered for the country, operation outside the tool's scope. |
| <a id="cancelled"></a>`cancelled` | 130 | – | Cancelled by the user or by SIGINT. |
| <a id="terminated"></a>`terminated` | 143 | – | Terminated by SIGTERM (container stop, timeout). |
| <a id="unauthorized"></a>`unauthorized` | – | 401 | REST only: missing or invalid credentials. |
| <a id="method_not_allowed"></a>`method_not_allowed` | – | 405 | REST only: HTTP method not supported by the route. |
| <a id="rate_limited"></a>`rate_limited` | – | 429 | REST only: client exceeded a rate limit; Retry-After is set. |
<!-- end generated -->

Titles in English and Polish are in the JSON file.

*Why the numbers:* new codes take 12–15, so they cannot collide with the
outcomes 10 and 11; 130 and 143 follow the 128+signal convention; ECO-015
records the collisions this resolves.

## 3. Rules

**ERR-1** Every raised error carries exactly one registry `code`. Projects MUST
NOT invent codes. Finer distinctions go to `details.reason` as snake_case
English (`no_coverage`, `invalid_sheet_code`, `year_out_of_range`); the
reasons that every tool shares are defined with their rule (DEV §19).
*Why:* consumers branch on `code`; `reason` keeps project precision without
fragmenting the registry.

**ERR-2** The registry grows only through a new version of this standard; a
project that needs a new code proposes it in Nogat.

**ERR-3** Each project keeps a copy of `error_registry.json` and of Nogat's
`schemas/agent/` (AGI-4.1) taken from the standard tag
`std-<standard_version>`, and generates its error module from the registry
(for example `src/<package>/_errors.py`); a contract test compares the module
with the copy.
*Why:* ECO-015; the gate is offline, so it compares the generated module with
the vendored copy.

**ERR-4** Interfaces report errors as follows:
- Python: `<Project>Error` subclass with `code`, `message`, `hint`, `details`.
- CLI: last line of stderr is `<tool>-error/1`; exit code from the table.
- MCP: `isError: true` with the error document.
- REST: `application/problem+json` with `type` pointing to the code's anchor
  on this page (`ERROR_REGISTRY.md#<code>`), `status` from the table, plus
  `code`, `hint`, `details`.

**ERR-5** Every error has a `hint` when a fix is known: the option to change,
allowed values, the command to run (`uv add "nogat-<project>[mcp]"`).
*Why:* the hint lets an agent fix the call in one retry instead of a guess.

**ERR-6** `message`, `title` and `hint` are English in machine output and
follow `lang` in human-readable output (AGI-9.2); `code`, `details` keys and
`reason` never change with language.

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
