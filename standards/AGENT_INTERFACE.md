# Agent interface standard

Part of standard 2.1 · IDs `AGI-…`

How a project exposes its functionality to programs and AI agents: Python
library, CLI, MCP server, REST API, `llms.txt` and `AGENTS.md`. It applies to
profile `tool` in full and to profile `app` for the documents (AGI §4), the
REST API (AGI §6) and languages (AGI §9). Until the `nogat` package exists,
the `hub`'s scripts report errors as AGI-3.3 and ERR say and are exempt from
the rest of AGI §3; the hub takes part in AGI §8 through the routing table of
HUB-4.3 (ECO-044, ECO-048).

The goal (ECO-017) is that an agent which needs Polish/Czech spatial data,
hydrological computation, IMGW/ČHMÚ observations or flood modelling finds
these tools, judges correctly whether they fit, and calls them right the
first time. Agents select by precise scope, names, schemas and recoverable
errors; they do not respond to claims of superiority (DOC-1.6).

---

## 1. Principles

**AGI-1.1** Every operation is declared once in a command catalog. The Python
public API, CLI, MCP tools, REST routes, `AGENTS.md`, `llms.txt`, OpenAPI and
reference documentation are generated from it or tested against it.
*Why:* drift between interfaces is the main source of wrong agent calls.

**AGI-1.2** The same operation has the same name, the same option names, the
same defaults, the same result document and the same error codes in every
interface (AGI-3.4, AGI §4, ERR §2).
*Why:* an agent switches interfaces (MCP in one session, CLI in another,
library in generated code) without relearning.

**AGI-1.3** Read-only operations are the default; writing operations offer a
`check` mode (plan without effects, DEV-19.10); MCP servers start read-only;
destructive operations need an explicit flag (replacing files: `--force`,
DEV-19.9).
*Why:* agents execute autonomously; a plan without effects can be confirmed
before anything is written.

**AGI-1.4** Everything an agent needs to call an operation (list, schema,
examples, errors) is available without network or credentials.

**AGI-1.5** Details come on demand: catalog summary → command schema → full
guide. No response exceeds the result budget (DOC-1.7).
*Why:* agent clients truncate large outputs.

**AGI-1.6** Command names, option names, enum values, codes and JSON keys are
English and identical in all languages; only human-readable text is
translated (AGI §9).

---

## 2. Command catalog

**AGI-2.1** Each project with profile `tool` exposes `list_commands()`,
`command_schema(command)`, `validate_command(command, **options)`,
`check_command(command, **options)` and `run_command(command, **options)` in
its public API. `validate_command` checks the options against the command's
schema and returns them with defaults filled, without planning or effects, or
raises `validation_error`; `check_command` returns the plan of `--check`. A
project whose CLI lines other projects store or pass on also exposes
`parse_command(line)`, which reads a line into the command, its options and
its run flags, and `format_command(command, options=…, run=…)`, which writes
them back as the canonical line, the form of every catalog example call; other
projects MAY.
*Why:* an orchestrating assistant can drive any tool generically through
these five functions; a consumer reads and writes a tool's CLI lines without a
copy of its parser.

**AGI-2.2** Each command declares:

| Field | Meaning |
|---|---|
| `name` | `<group> <verb>` as typed in the CLI, English, lowercase |
| `operation_id` | `<tool>_<group>_<verb>`, snake_case, unique in the ecosystem; also the MCP tool name and OpenAPI `operationId` |
| `function` | public Python function implementing it |
| `summary` | one sentence starting with a verb (budget DOC-1.7) |
| `description` | what it does, **when to use**, **when not to use (and what instead)**, main limit |
| `options` | list of options (AGI-2.3) |
| `result` | result document schema id (`<tool>-<kind>/<n>`) and cardinality (`single`, `bounded`, `unbounded`) |
| `effects` | `read_only` (bool), `writes` (`none`, `add`, `replace`, `delete`), `idempotent` (bool), `network` (bool), `destructive` (bool) |
| `check` | catalog name of the command that plans this one without effects, or `null` |
| `families` | MCP tool families for `--tools` (AGI-5.8); `core` marks the core family (AGI-5.12) |
| `rules` | short imperative rules for agents |
| `examples` | at least one `{call, result}`: a complete CLI call and an excerpt of its result |
| `errors` | registry codes the command can raise |
| `i18n` | Polish texts for human-readable fields |

`summary`, `description` and `rules` together are the MCP tool description
(AGI-5.3) and fit its budget (DOC-1.7).
*Why:* when-not and examples most improve agent tool choice
(https://www.anthropic.com/engineering/writing-tools-for-agents,
https://arxiv.org/abs/2602.14878); `effects` feeds the MCP annotations
(AGI-5.4).

**AGI-2.3** Each option declares: `name` (snake_case), `type`, `unit` (when
physical), `required`, `default`, `enum` with a one-line meaning per value,
`min`/`max`, `pattern`, `examples`, `description`, mutual exclusion groups
(`one_of`), and whether it is a path (`path_role`: `input`, `output`, `root`;
the write targets of DEV-19.1 have `output` and `root`).
*Why:* enums and bounds let agents fill parameters without reading prose;
`path_role` drives the sandbox (AGI-5.8).

**AGI-2.4** The catalog is serialisable as `<tool>-commands/1` JSON
(schema in AGI-4.1) and returned by `<tool> commands list --json`,
`<tool> commands schema --command "<group> <verb>" --json` and the MCP
catalog tools (AGI-5.9).

---

## 3. CLI

**AGI-3.1** Shape: `<tool> <group> <verb> [--option value ...]`; one
executable per project; option flags are kebab-case forms of option names
(`--output-dir` ↔ `output_dir`).

**AGI-3.2** `--json` prints exactly one JSON document (the result envelope,
AGI-4.2) on stdout and nothing else. Without `--json`, a human-readable
rendering. Logs, progress and warnings go to stderr. Outcomes `partial` and
`failed` (exit 10 and 11) print the envelope; an error (ERR §2) prints
nothing on stdout.
*Why:* stdout then always parses as the declared result type
(https://clispec.dev/).

**AGI-3.3** On an error, the last line of stderr is the error document
(AGI-4.3) as compact JSON, in both modes; the exit code comes from the
registry. Outcomes (ERR §1) print no error document.
*Why:* ECO-019; agents read the last stderr line without parsing prose.

**AGI-3.4** Where the concept applies, projects MUST use these option names:

| Option | Meaning |
|---|---|
| `--json` | machine output |
| `--lang` | language of human-readable output, `pl` or `en` (AGI-9.2) |
| `--check` | plan without effects; the only option for it (DEV-19.10) |
| `--yes` | confirm without prompt |
| `--output` | the one output file of a command that writes exactly one file (DEV-19.1) |
| `--output-dir`, `-o` | directory for plain output files, no metadata; `-o` is its short form and no other option's (DEV-19.1) |
| `--root` | store root; default `<data_dir>/<tool>` (DEV-18.2, DEV-19.2) |
| `--project` | project manifest path or name |
| `--bbox` + `--crs` | bounding box `min_x,min_y,max_x,max_y` and its CRS |
| `--geometry` + `--layer` | area from a vector file |
| `--teryt` | Polish administrative unit code |
| `--station` / `--stations` | station identifier(s) |
| `--start` / `--end` | ISO dates or datetimes |
| `--years` | year range `YYYY-YYYY` or list |
| `--force` | ignore caches and existing results: replace existing target files in plain mode, fetch again in store mode and never overwrite a version (DEV-19.9) |
| `--workers` | parallelism |
| `--limit` / `--cursor` | pagination |
| `--allow-dir` | sandbox root (MCP) |
| `--verbose` / `--quiet` | log level |

*Why:* shared names let agents transfer knowledge between tools.

**AGI-3.5** Non-interactive by default when stdin is not a TTY: no prompts,
`--yes` to confirm; every input is settable by flag, environment variable or
file, except credentials, which come from environment variables only
(DEV-18.4).

**AGI-3.6** No ANSI colour when stdout is not a TTY, when `NO_COLOR` is set
or with `TERM=dumb`.

**AGI-3.7** `--help` starts with one sentence saying what the command does,
lists enum values with meanings, and ends with examples. `--version` prints
the package version.

**AGI-3.8** `<tool> commands guide --format agents|llms|agents-md-block`
renders AGENTS.md, llms.txt and the block of AGI-8.2 (AGI §8); `<tool> mcp`
starts the MCP server (AGI §5).

---

## 4. Documents: result, error, domain

**AGI-4.1** Every machine-readable document has a top-level `schema` field
`<tool>-<kind>/<n>`. Adding optional fields keeps `<n>`, so consumers accept
unknown fields; removing or changing meaning increments it. The schemas of
the result envelope, the error document and the catalog are Nogat's
`schemas/agent/` (`result-1`, `error-1`, `commands-1`); each project copies
them with `error_registry.json` (ERR-3), and its contract tests validate its
documents against them. Domain schemas are published in the package
(`src/<package>/schemas/`) and listed in the catalog.
*Why:* one schema per shared document; prose alone let projects drift while
each claimed AGI-1.2 (ECO-050).

**AGI-4.2** The result envelope `<tool>-result/1`:

| Field | Type | Meaning |
|---|---|---|
| `schema` | string | `<tool>-result/1` |
| `tool` | string | `<tool>` |
| `version` | string | package version |
| `command` | string | catalog command name |
| `check` | bool | true if this was a plan |
| `status` | `ok` \| `partial` \| `failed` \| `cancelled` | overall outcome |
| `result` | object, list or null | domain document (`<tool>-<kind>/<n>`), a list of them, or null when nothing was produced |
| `items` | list | per-unit outcome for batch operations: `{id, status, code?, reason?, message?}`; `status` is `ok` or `failed`, a failed unit has `code`; `partial` has both kinds, `failed` has no `ok` unit |
| `notices` | list | `{level, code, message}`; `level` is `info` or `warning` |
| `page` | object | `{total?, next_cursor?, truncated}` for collections; `truncated` is true when more results exist, and `next_cursor` then fetches them |

*Why:* explicit `status` and per-item status let agents retry only the failed
units.

**AGI-4.3** The error document `<tool>-error/1`:

| Field | Meaning |
|---|---|
| `schema` | `<tool>-error/1` |
| `code` | registry code (ERR §2) |
| `title` | registry title in the language of the channel (AGI-9.2) |
| `message` | what happened, in the language of the channel |
| `hint` | one line: how to fix, naming the option or command; same language as `message` |
| `details` | JSON object: `reason` (project-specific sub-code; the shared ones are in DEV §19), `option`, `value`, `allowed`, `path`, `paths`, ... |
| `exit_code` | process exit code from the registry |
| `command` | command name, if known |

*Why:* `reason` keeps project-specific precision under a shared `code`
(ERR-1).

**AGI-4.4** Library functions return typed document objects with `to_dict()`
and `to_json()`; the dictionary is identical to the CLI/MCP/REST result.

---

## 5. MCP server

**AGI-5.1** `<tool> mcp` starts the MCP server over stdio (extra `[mcp]`), with
HTTP transport only for `app` projects that already run a server; the console
script `<tool>-mcp` starts the same server, so a one-off start is
`uvx --from "nogat-<project>[mcp]" <tool>-mcp`. The MCP specification revision
and the SDK version are pinned in `pyproject.toml` and recorded in README.
*Why:* one entry per tool; the protocol changes between revisions
(https://modelcontextprotocol.io/specification/2026-07-28/changelog).

**AGI-5.2** Tool names are the catalog `operation_id`:
`<tool>_<group>_<verb>`, characters `[a-z0-9_]`, at most 48 characters,
deterministic order in `tools/list`.
*Why:* ECO-018; clients prepend `mcp__` and the server name to every tool
name, so short names avoid truncation.

**AGI-5.3** Descriptions come from the catalog (`summary`, `description`,
`rules`): English, key terms first, within the budget of DOC-1.7; each field
of `inputSchema` has its own `description`.
*Why:* Claude Code loads only names and server instructions up front and
searches descriptions, so key terms come first
(https://code.claude.com/docs/en/mcp).

**AGI-5.4** Every tool has the annotations `title`, `readOnlyHint`,
`destructiveHint`, `idempotentHint`, `openWorldHint`, derived from catalog
`effects` and from the server mode (write tools report `readOnlyHint: true`
only when the server runs read-only and they are restricted to `check`).
*Why:* clients use them for approval policies (Codex asks only for
non-read-only tools); directory submission requires them
(https://claude.com/docs/connectors/building/submission).

**AGI-5.5** `inputSchema` is JSON Schema 2020-12 with
`additionalProperties: false`, `required`, `enum`, `default`; `outputSchema`
is the result envelope; results return `structuredContent` and the same JSON
as a text block.

**AGI-5.6** Collections are paginated (`limit`, `cursor`); the default page
and every response stay within the result budgets of DOC-1.7; larger results
are written to files and the envelope returns paths.
*Why:* Claude Code warns above 10,000 tokens and truncates at 25,000
(https://code.claude.com/docs/en/mcp).

**AGI-5.7** Execution errors return a result with `isError: true` whose
content is the error document (AGI-4.3). Protocol errors (unknown tool,
malformed request) stay JSON-RPC errors.
*Why:* the agent sees and repairs execution errors; the hint and allowed
values make one retry sufficient.

**AGI-5.8** `--allow-dir DIR` (repeatable) restricts every option with
`path_role` and the default store root (DEV-19.3); outside paths raise
`forbidden`. `--allow-writes` enables writing tools; without it they run in
`check` mode or are hidden. `--tools <families>` limits exposed tools.

**AGI-5.9** Each server exposes the catalog as the tools `<tool>_commands_list`
(catalog summary) and `<tool>_commands_schema` (one command's schema), the
`operation_id`s of `<tool> commands list` and `<tool> commands schema` (AGI-5.2),
and MAY expose AGENTS.md and the catalog as resources and typical flows as
prompts. One or two entry tools MAY set
`_meta["anthropic/alwaysLoad"] = true`.
*Why:* tools are model-controlled and always reachable; resources and prompts
depend on client support.

**AGI-5.10** Server instructions are English and stay within the budget of
DOC-1.7; they state the relations between tools, the required order (discover
→ check → run → read), limits and licences, and neither duplicate tool
descriptions nor market.
*Why:* instructions raise correct workflow use
(https://blog.modelcontextprotocol.io/posts/2025-11-03-using-server-instructions/);
Claude Code truncates them at 4,096 characters.

**AGI-5.11** Cold start and `tools/list` take under 5 seconds: heavy imports
(GDAL, rasterio, pyarrow, pandas) are lazy. Long operations send progress
notifications when the client provides a progress token. Network concurrency
is bounded per server.
*Why:* client connection timeouts are around 5–10 seconds.

**AGI-5.12** Each server defines a `core` family of at most 10 tools covering
the main tasks, selectable with `--tools core`.
*Why:* local models have no tool search and degrade with large tool lists.

**AGI-5.13** The gate starts the server with an MCP SDK client and checks:
tool names (AGI-5.2), annotations, schemas and `outputSchema`; descriptions,
instructions and the default page against DOC-1.7; the cold start of
AGI-5.11; one read-only call; one validation error (`isError: true`, registry
code, hint).

---

## 6. REST API (projects with a server)

**AGI-6.1** Where the project has a command catalog, its operations are
exposed at `/api/v1/<group>/<verb>`; `GET` for read-only, `POST` for writing;
`?check=true` for plans; the response body is the result envelope.

**AGI-6.2** OpenAPI 3.1 at `/openapi.json`; where the project has a command
catalog, `operationId` equals the catalog `operation_id`; every operation has
`summary`, `description` (with when/when-not), parameter descriptions, examples
and documented error responses. FastAPI uses `generate_unique_id_function` to
emit catalog ids.
*Why:* FastAPI's default ids (`read_items_items__get`) are meaningless to
agents and generators.

**AGI-6.3** Errors are `application/problem+json` (RFC 9457) with `type`
(URL of the registry entry), `title`, `status`, `detail`, `instance`, plus
`code`, `hint`, `details`, and `errors[]` with JSON Pointers for validation.
HTTP status from the registry.

**AGI-6.4** Human text in responses follows `Accept-Language` (English when
the header is absent, AGI-9.2); `Content-Language` in responses; machine
fields unaffected.

**AGI-6.5** Pagination by opaque cursor; write endpoints require
authentication; rate limits return `rate_limited` (429).

**AGI-6.6** A contract test validates the OpenAPI 3.1 document and checks that
it agrees with the catalog.

---

## 7. Python library

**AGI-7.1** The public API is exactly `__all__` of the top-level package;
everything else is private and changes without notice. A contract test imports
every name in `__all__` and type-checks a consumer snippet with mypy.

**AGI-7.2** One public function per catalog command, keyword-only arguments
named as catalog options, typed, returning document objects (AGI-4.4), raising
`<Project>Error` subclasses with registry codes.

**AGI-7.3** Importing the package performs no network access, no file writes
and no heavy imports.

**AGI-7.4** Async variants, when provided, use the same name with an `a`
prefix or an `aio` submodule, consistently within a project.

---

## 8. AGENTS.md and llms.txt generation

**AGI-8.1** Both files are rendered by `<tool> commands guide` from templates
in `src/<package>/_data/agents/` (English) with blocks filled from the
catalog, error registry and typical flows (DOC §4, DOC §5).

**AGI-8.2** `<tool> commands guide --format agents-md-block` prints a compact
block (budget DOC-1.7) for consumer repositories, delimited by
`<!-- BEGIN <tool> -->` and `<!-- END <tool> -->`; `--inject PATH` replaces
the block in a consumer's AGENTS.md idempotently.
*Why:* an agent working in another repository never loads this repository's
AGENTS.md; injection is the delivery channel
(https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals).

**AGI-8.3** Nogat's AGENTS.md links each tool's AGENTS.md from its routing
table (HUB-4.3); the blocks of AGI-8.2 are for consumer repositories.

---

## 9. Languages

**AGI-9.1** Catalog texts are authored in English; Polish translations are
stored next to them (`i18n.pl`) and used for human-readable output.

**AGI-9.2** Machine output is English: `--json` output, the error document
on the last stderr line, MCP results, descriptions and instructions, REST
responses without `Accept-Language` (AGI-6.4), AGENTS.md, llms.txt and
OpenAPI. Human-readable output (CLI without `--json`, UI) follows the key
`lang` of DEV-18.1 (default `pl`) and the option `--lang`.
*Why:* end users are Polish (ECO-005); agents read English and must get the
same text whatever the user's setting (ECO-042).

**AGI-9.3** Inputs with Polish names (stations, municipalities, rivers) are
matched case- and diacritic-insensitively; on no match the error lists close
candidates.
*Why:* agents often drop diacritics.

---

## 10. Discoverability metadata

**AGI-10.1** `pyproject.toml` has a `description` (the 200-character form of
DOC-2.3, budget DOC-1.7), at least 5 `keywords`, classifiers including
`Typing :: Typed` and, where relevant, `Topic :: Scientific/Engineering :: GIS`
or `Hydrology`, and `[project.urls]` with `Homepage`, `Source`,
`Documentation`, `Changelog`, `Issues`; the built distribution passes
`twine check`.
*Why:* PyPI metadata is indexed by package search and agents
(https://packaging.python.org/en/latest/specifications/well-known-project-urls/).
