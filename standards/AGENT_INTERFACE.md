# Agent interface standard

Version 2.0 · 2026-10-19 · IDs `AGI-…` · keywords per RFC 2119.

How a project exposes its functionality to programs and AI agents: Python
library, CLI, MCP server, REST API, `llms.txt` and `AGENTS.md`. Applies to
profiles `tool` and `assistant` in full, to `library` for §1, §2, §5, §8 and
§10, and to `app` for §6 and §7 where an API exists.

The goal (ECO-017) is that an agent which needs Polish/Czech spatial data,
hydrological computation, IMGW/ČHMÚ observations or flood modelling finds
these tools, judges correctly whether they fit, and calls them right the
first time. Agents select by precise scope, names, schemas and recoverable
errors; they do not respond to claims of superiority (DOC-1.6).

Reference implementations: IMGWTools (catalog, envelope, REST, MCP,
generated guides), Kartograf (CLI errors with hints, layered catalog
introspection, MCP sandbox, network limits), Hydrolog v1.0 branch
(catalog-driven CLI, agent guide templates).

---

## 1. Principles

**AGI-1.1 One catalog, all interfaces.** Every operation is declared once in a
command catalog. The Python public API, CLI, MCP tools, REST routes,
`AGENTS.md`, `llms.txt`, OpenAPI and reference documentation are generated
from it or tested against it.
*Why:* Kartograf, IMGWTools and Hydrolog converged on this independently;
drift between interfaces is the main source of wrong agent calls.

**AGI-1.2 Parity.** The same operation has the same name, the same option
names, the same defaults, the same result document and the same error codes in
every interface (§3.4, §4, ERROR_REGISTRY).
*Why:* an agent switches interfaces (MCP in one session, CLI in another,
library in generated code) and must not relearn.

**AGI-1.3 Safe by default.** Read-only operations are the default; writing
operations offer a `check` mode (plan without effects); MCP servers start
read-only; destructive operations need an explicit flag.
*Why:* agents execute autonomously; Retman requires confirmation of a plan
before execution and builds on `check`.

**AGI-1.4 Offline introspection.** Everything an agent needs to call an
operation (list, schema, examples, errors) is available without network or
credentials.

**AGI-1.5 Progressive disclosure.** Small summaries first, details on demand:
catalog summary → command schema → full guide. No single response above the
size limits of §5.6.
*Why:* Kartograf's layered catalog (about 7k → 30k → 300k characters) shows
the need; agent clients truncate large outputs.

**AGI-1.6 Machine values in English, never translated.** Command names,
option names, enum values, codes and JSON keys are English and identical in
all languages; only human-readable text is translated (§9).

---

## 2. Command catalog

**AGI-2.1** Each project with profile `tool` exposes `list_commands()`,
`command_schema(command)`, `check_command(command, **options)`,
`run_command(command, **options)` and `validate_command(command, **options)`
in its public API.
*Why:* common shape across Kartograf, IMGWTools and Hydrolog; Retman can
drive any tool generically through these five functions.

**AGI-2.2** Each command declares:

| Field | Meaning |
|---|---|
| `name` | `<group> <verb>` as typed in the CLI, English, lowercase |
| `operation_id` | `<prefix>_<group>_<verb>`, snake_case, unique in the ecosystem; also the MCP tool name and OpenAPI `operationId` |
| `function` | public Python function implementing it |
| `summary` | ≤ 100 characters, starts with a verb |
| `description` | ≤ 600 characters: what it does, **when to use**, **when not to use (and what instead)**, main limit |
| `options` | list of options (AGI-2.3) |
| `result` | result document schema id (`<prefix>-<kind>/<n>`) and cardinality (`single`, `bounded`, `unbounded`) |
| `effects` | `read_only` (bool), `writes` (`none`, `add`, `replace`, `delete`), `idempotent` (bool), `network` (bool), `destructive` (bool) |
| `check` | name of the check operation or `null` |
| `rules` | short imperative rules for agents |
| `examples` | at least one complete call with expected result excerpt |
| `errors` | registry codes the command can raise |
| `i18n` | Polish texts for human-readable fields |

*Why:* union of fields already present in the three catalogs, plus
`effects.idempotent`/`destructive` required by MCP annotations (§5.4), plus
when/when-not and examples, which most improve agent tool choice
(https://www.anthropic.com/engineering/writing-tools-for-agents,
https://arxiv.org/abs/2602.14878).

**AGI-2.3** Each option declares: `name` (snake_case), `type`, `unit` (when
physical), `required`, `default`, `enum` with a one-line meaning per value,
`min`/`max`, `pattern`, `examples`, `description`, mutual exclusion groups
(`one_of`), and whether it is a path (`path_role`: `input`, `output`, `root`).
*Why:* enums and bounds let agents fill parameters without reading prose;
`path_role` drives the sandbox (§5.8).

**AGI-2.4** The catalog is serialisable as `<prefix>-commands/1` JSON and
returned by `<tool> commands list --json`, `<tool> commands schema
--command "<name>" --json` and the MCP catalog tool (§5.9).

---

## 3. CLI

**AGI-3.1** Shape: `<tool> <group> <verb> [--option value ...]`; one
executable per project; option flags are kebab-case forms of option names
(`--output-dir` ↔ `output_dir`).

**AGI-3.2** `--json` prints exactly one JSON document (the result envelope,
§4) on stdout and nothing else. Without `--json`, a human-readable rendering.
Logs, progress and warnings go to stderr.
*Why:* stdout must always parse as the declared result type
(https://clispec.dev/).

**AGI-3.3** On failure, the last line of stderr is the error document (§4.3)
as compact JSON, in both modes; the exit code comes from the registry.
*Why:* ECO-019; agents read the last stderr line without parsing prose.

**AGI-3.4** Shared option vocabulary. Where the concept applies, projects
MUST use these names:

| Option | Meaning |
|---|---|
| `--json` | machine output |
| `--lang pl|en` | language of human-readable text |
| `--check` | plan without effects |
| `--yes` | confirm without prompt |
| `--output` | output file |
| `--output-dir` | output directory |
| `--root` | store root |
| `--project` | project manifest path or name |
| `--bbox` + `--crs` | bounding box `min_x,min_y,max_x,max_y` and its CRS |
| `--geometry` + `--layer` | area from a vector file |
| `--teryt` | Polish administrative unit code |
| `--station` / `--stations` | station identifier(s) |
| `--start` / `--end` | ISO dates or datetimes |
| `--years` | year range `YYYY-YYYY` or list |
| `--force` | ignore caches and existing results |
| `--workers` | parallelism |
| `--limit` / `--cursor` | pagination |
| `--allow-dir` | sandbox root (MCP) |
| `--verbose` / `--quiet` | log level |

*Why:* today the same concept is `--output` in one tool and `--path` or
`--output-dir` in another; shared names let agents transfer knowledge.

**AGI-3.5** Non-interactive by default when stdin is not a TTY: no prompts,
`--yes` to confirm; every input settable by flag, environment variable or
file; secrets never on the command line.

**AGI-3.6** No ANSI colour when stdout is not a TTY, when `NO_COLOR` is set
or with `TERM=dumb`.

**AGI-3.7** `--help` starts with one sentence saying what the command does,
lists enum values with meanings, and ends with examples. `--version` prints
the package version.

**AGI-3.8** `<tool> commands guide --format agents|llms --lang en|pl` renders
AGENTS.md and llms.txt (§8); `<tool> mcp` starts the MCP server (§5).

---

## 4. Documents: result, error, domain

**AGI-4.1** Every machine-readable document has a top-level `schema` field
`<prefix>-<kind>/<n>`. Adding optional fields keeps `<n>`; removing or
changing meaning increments it. JSON Schemas are published in the package
(`src/<package>/schemas/`) and listed in the catalog.

**AGI-4.2 Result envelope `<prefix>-result/1`:**

| Field | Type | Meaning |
|---|---|---|
| `schema` | string | `<prefix>-result/1` |
| `tool` | string | project name |
| `version` | string | package version |
| `command` | string | catalog command name |
| `check` | bool | true if this was a plan |
| `status` | `ok` \| `partial` \| `failed` \| `cancelled` | overall outcome |
| `result` | object or list | domain document (`<prefix>-<kind>/<n>`) |
| `items` | list | per-unit outcome for batch operations: `{id, status, code?, message?}` |
| `notices` | list | `{level: info|warning, code, message}` |
| `page` | object | `{total?, next_cursor?, truncated}` for collections |

*Why:* IMGWTools `imgw-result/1` is the most complete; explicit `status`
replaces Kartograf's boolean `ok`; per-item status lets agents retry only
failed units.

**AGI-4.3 Error document `<prefix>-error/1`:**

| Field | Meaning |
|---|---|
| `schema` | `<prefix>-error/1` |
| `code` | registry code (ERROR_REGISTRY) |
| `title` | registry title in the active language |
| `message` | what happened, in the active language |
| `hint` | one line: how to fix, naming the option or command |
| `details` | JSON object: `reason` (project-specific sub-code), `option`, `value`, `allowed`, `path`, ... |
| `exit_code` | process exit code from the registry |
| `command` | command name, if known |

*Why:* union of Kartograf (`hint`, `exit_code`), Hydrolog and IMGWTools
(`details`, titles in two languages); `reason` keeps project-specific
precision under a shared `code`.

**AGI-4.4** Library functions return typed document objects with `to_dict()`
and `to_json()`; the dictionary is identical to the CLI/MCP/REST result.

---

## 5. MCP server

**AGI-5.1 Entry and transport.** `<tool> mcp` (and a console script
`<tool>-mcp` for `uvx`), extra `[mcp]`, stdio transport. HTTP transport only
for `app` profiles that already run a server. The supported MCP specification
revision and SDK version are pinned in `pyproject.toml` and recorded in
README.
*Why:* single entry per tool; the protocol changes between revisions
(2026-07-28 made the protocol stateless,
https://modelcontextprotocol.io/specification/2026-07-28/changelog).

**AGI-5.2 Tool names** are the catalog `operation_id`: `<prefix>_<group>_<verb>`,
characters `[a-z0-9_]`, at most 48 characters, deterministic order in
`tools/list`.
*Why:* ECO-018; clients prepend the server name (`mcp__<server>__<tool>`), so
short names avoid truncation.

**AGI-5.3 Descriptions** come from the catalog (`summary` + `description` +
`rules`), English, 300–600 characters, key terms first, each field of
`inputSchema` with its own `description`.
*Why:* 97% of surveyed MCP tool descriptions have defects and 56% state no
clear purpose (https://arxiv.org/abs/2602.14878); Claude Code loads only names
and server instructions up front and searches descriptions, so key terms must
come first (https://code.claude.com/docs/en/mcp).

**AGI-5.4 Annotations** on every tool: `title`, `readOnlyHint`,
`destructiveHint`, `idempotentHint`, `openWorldHint`, derived from catalog
`effects` and from the server mode (write tools report `readOnlyHint: true`
only when the server runs read-only and they are restricted to `check`).
*Why:* clients use them for approval policies (Codex asks only for
non-read-only tools); directory submission requires them
(https://claude.com/docs/connectors/building/submission).

**AGI-5.5 Schemas.** `inputSchema` is JSON Schema 2020-12 with
`additionalProperties: false`, `required`, `enum`, `default`; `outputSchema`
is the result envelope; results return `structuredContent` and the same JSON
as a text block.

**AGI-5.6 Size.** Collections are paginated (`limit`, `cursor`), default page
fits in about 10,000 tokens, hard maximum about 25,000 tokens (~50,000
characters); larger results are written to files and the envelope returns
paths.
*Why:* Claude Code warns above 10k tokens and truncates at 25k
(https://code.claude.com/docs/en/mcp).

**AGI-5.7 Errors.** Execution errors return a result with `isError: true`
whose content is the error document (§4.3). Protocol errors (unknown tool,
malformed request) stay JSON-RPC errors.
*Why:* the agent sees and repairs execution errors; the hint and allowed
values make one retry sufficient.

**AGI-5.8 Sandbox and mode.** `--allow-dir DIR` (repeatable) restricts every
option with `path_role`; outside paths raise `forbidden`. `--allow-writes`
enables writing tools; without it they run in `check` mode or are hidden.
`--tools <families>` limits exposed tools.

**AGI-5.9 Discovery tools.** Each server exposes `<prefix>_catalog` (catalog
summary and schemas) and MAY expose AGENTS.md and the catalog as resources and
typical flows as prompts. One or two entry tools MAY set
`_meta["anthropic/alwaysLoad"] = true`.
*Why:* tools are model-controlled and always reachable; resources and prompts
depend on client support.

**AGI-5.10 Instructions.** Server instructions ≤ 4,096 characters, English:
relations between tools, required order (discover → check → run → read),
limits, licences. No duplicated tool descriptions, no marketing.
*Why:* instructions raised correct workflow use from 60% to 85% in an MCP
test (https://blog.modelcontextprotocol.io/posts/2025-11-03-using-server-instructions/);
Claude Code truncates them at 4,096 characters.

**AGI-5.11 Performance.** Cold start and `tools/list` in under 5 seconds:
heavy imports (GDAL, rasterio, pyarrow, pandas) are lazy. Long operations send
progress notifications when the client provides a progress token. Network
concurrency is bounded per server.
*Why:* client connection timeouts are around 5–10 seconds.

**AGI-5.12 Core set.** Each server defines a `core` family of at most 10 tools
covering the main tasks, selectable with `--tools core`.
*Why:* local models used through Retman have no tool search and degrade with
large tool lists.

**AGI-5.13 Testing.** The gate runs the server through MCP Inspector CLI or an
SDK client: list tools, validate annotations and schemas, call one read-only
tool, trigger one validation error.

---

## 6. REST API (profiles with a server)

**AGI-6.1** Catalog operations are exposed at `/api/v1/<group>/<verb>`; `GET`
for read-only, `POST` for writing; `?check=true` for plans; the response body
is the result envelope.

**AGI-6.2** OpenAPI 3.1 at `/openapi.json`; `operationId` equals the catalog
`operation_id`; every operation has `summary`, `description` (with
when/when-not), parameter descriptions, examples and documented error
responses. FastAPI uses `generate_unique_id_function` to emit catalog ids.
*Why:* FastAPI's default ids (`read_items_items__get`) are meaningless to
agents and generators.

**AGI-6.3** Errors are `application/problem+json` (RFC 9457) with `type`
(URL of the registry entry), `title`, `status`, `detail`, `instance`, plus
`code`, `hint`, `details`, and `errors[]` with JSON Pointers for validation.
HTTP status from the registry.

**AGI-6.4** Language by `Accept-Language` (default `pl` for human text),
`Content-Language` in responses; machine fields unaffected.

**AGI-6.5** Pagination by opaque cursor; write endpoints require
authentication; rate limits return `rate_limited` (429).

**AGI-6.6** A contract test checks that OpenAPI and the catalog agree.

---

## 7. Python library

**AGI-7.1** The public API is exactly `__all__` of the top-level package;
everything else is private and may change without notice.

**AGI-7.2** One public function per catalog command, keyword-only arguments
named as catalog options, typed, returning document objects (§4.4), raising
`<Project>Error` subclasses with registry codes.

**AGI-7.3** Importing the package performs no network access, no file writes
and no heavy imports.

**AGI-7.4** Async variants, when provided, use the same name with `a`
prefix or an `aio` submodule, consistently within a project.

---

## 8. AGENTS.md and llms.txt generation

**AGI-8.1** Both files are rendered by `<tool> commands guide` from templates
in `src/<package>/_data/agents/` (English) with blocks filled from the
catalog, error registry and typical flows (DOC-4, DOC-5).

**AGI-8.2** `<tool> commands guide --format agents-md-block` prints a compact
block (≤ 60 lines) for consumer repositories, delimited by
`<!-- BEGIN <tool> -->` and `<!-- END <tool> -->`; `--inject PATH` replaces
the block in a consumer's AGENTS.md idempotently.
*Why:* an agent working in another repository never loads this repository's
AGENTS.md; injection is the delivery channel (precedent: Next.js codemod
injecting an AGENTS.md index, https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals).

**AGI-8.3** Nogat aggregates the blocks of all tools into its own AGENTS.md
(ECOSYSTEM_HUB §4).

---

## 9. Languages

**AGI-9.1** Catalog texts are authored in English; Polish translations are
stored next to them (`i18n.pl`) and used for human-readable output.

**AGI-9.2** Language selection: `--lang`, then `<TOOL>_LANG`, then default.
Default for human-readable CLI and UI text is `pl`; default for MCP
descriptions, instructions, AGENTS.md, llms.txt and OpenAPI is `en`.
*Why:* end users are Polish (ECO-005); agents work best in English.

**AGI-9.3** Inputs with Polish names (stations, municipalities, rivers) are
matched case- and diacritic-insensitively; on no match the error lists close
candidates.
*Why:* agents often drop diacritics; IMGWTools already normalises.

---

## 10. Discoverability metadata

**AGI-10.1** `pyproject.toml`: `description` (≤ 200 characters, from the
ladder DOC-2.3), at least 5 `keywords`, classifiers including
`Typing :: Typed`, `Topic :: Scientific/Engineering :: GIS` or `Hydrology`
where relevant, and `[project.urls]` with `Homepage`, `Source`,
`Documentation`, `Changelog`, `Issues`.
*Why:* PyPI metadata is indexed by package search and agents
(https://packaging.python.org/en/latest/specifications/well-known-project-urls/).

**AGI-10.2** GitHub: "About" from the ladder; topics (≤ 20) including
`mcp-server`, `model-context-protocol`, `llms-txt`, `agents-md`, `hydrology`,
`gis`, `poland` as applicable.

**AGI-10.3** `context7.json` in the repository root with `projectTitle`,
`description`, `folders`, `excludeFolders` and `rules`.
*Why:* Context7 is a common documentation source for coding agents
(https://context7.com/docs/library-owners).

---

## 11. Agent-readiness checklist

Automated in the gate unless marked *(release)* or *(nightly)*.

1. `llms.txt` follows DOC-5: H1, blockquote, link lists; links resolve and
   point to raw Markdown on `main` or a tag *(release)*.
2. `AGENTS.md` and `llms.txt` equal generator output.
3. `AGENTS.md` ≤ 200 lines and ≤ 16 KiB; ends with the CLAUDE.md pointer.
4. `CLAUDE.md` ≤ 200 lines.
5. README: summary ≤ 400 characters in English; sections "When to use" and
   "When not to use"; one-line install; one example per interface; MCP
   snippets for at least three clients; links to `llms.txt` and `AGENTS.md`.
6. README examples execute.
7. No steering phrases (DOC-1.6) in README, AGENTS.md, llms.txt, descriptions.
8. `pyproject` metadata per AGI-10.1; `py.typed` present in the built wheel;
   `twine check` passes *(release)*.
9. Every name in `__all__` imports; mypy passes on a consumer snippet.
10. Catalog: every command has summary, description with when/when-not,
    effects, examples and error codes; every option has a description.
11. Parity: option names equal across library, CLI, MCP and REST.
12. CLI: each command with `--json` prints parsable JSON on stdout and nothing
    on stderr on success; error ends stderr with an error document; exit
    codes match the registry; no ANSI without TTY; nothing waits on stdin.
13. MCP: tool names prefixed and ≤ 48 characters; annotations present;
    descriptions 300–600 characters; every input field described;
    `outputSchema` present; instructions ≤ 4,096 characters.
14. MCP: cold start and `tools/list` under 5 seconds; a bad argument returns
    `isError: true` with registry code and hint.
15. MCP/CLI: default page within the size limit (AGI-5.6).
16. REST: OpenAPI 3.1 validates; `operationId` equals catalog ids; errors are
    problem+json with registry codes.
17. Error codes used in code exist in `error_registry.json` of the pinned
    standard version.
18. `server.json` validates and its version equals the package version
    *(release)*.
19. `context7.json` validates.
20. Agent evaluation: at least 10 tasks per tool run against a reference
    agent; tracks correct tool choice, number of calls, validation errors
    *(nightly)*.
    *Why:* the only direct measure of whether agents pick and use the tool
    correctly; Retman's `retman-eval` is the starting point.
