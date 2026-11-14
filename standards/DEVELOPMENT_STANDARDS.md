# Development standards

Part of standard 1.0 · IDs `DEV-…`

Related: [DOCUMENTATION_STANDARDS.md](DOCUMENTATION_STANDARDS.md),
[AGENT_INTERFACE.md](AGENT_INTERFACE.md), [ERROR_REGISTRY.md](ERROR_REGISTRY.md),
[RELEASE_AND_DISTRIBUTION.md](RELEASE_AND_DISTRIBUTION.md),
[ECOSYSTEM_HUB.md](ECOSYSTEM_HUB.md).

---

## 1. Project profiles

Requirements apply to all projects unless marked with a profile.

| Profile | Meaning | Projects |
|---|---|---|
| `tool` | Installable Python package; CLI, MCP and REST optional | Kartograf, Obserwator, Hydrolog, Retman, Hydraulik |
| `app` | Deployed service (web UI, server) | Obserwator (web GUI), Hydrograf, Archiwista |
| `hub` | Registry, standard and user package | Nogat |

A project may have several profiles; `ecosystem.yaml` is authoritative.

**DEV-1.1** Each project MUST declare its profiles in `ecosystem.yaml` and in
the first section of `CLAUDE.md`.
*Why:* profiles decide which sections of this standard apply; agents need
that without reading the whole standard.

**DEV-1.2** A deviation from this standard is recorded in one place: the
"Deviations" section of the project's `CLAUDE.md`, as the requirement ID, one
line and a link to the ADR if there is one.
*Why:* an undocumented deviation looks like a mistake to the next agent,
which then "fixes" it.

**DEV-1.3** Project documents cite requirements by ID and link to this
standard by URL, never by relative path; they do not copy its content, and a
project has no `docs/DEVELOPMENT_STANDARDS.md`.
*Why:* a copy forks into a second version of the rule.

---

## 2. Language

**DEV-2.1** Code, identifiers, docstrings, comments, log messages,
documentation, commit messages, ADRs, plans, error codes, JSON field names and
catalog/MCP descriptions MUST be in English.
*Why:* agents search and parse English; one language removes duplicate
maintenance (ECO-005, ECO-023).

**DEV-2.2** Human-readable output for end users (UI, CLI output without
`--json`) is Polish by default and English on request; machine output
(`--json`, MCP, REST without `Accept-Language`) is English. AGI-9.2 defines
the switch.
*Why:* target user groups are in Poland; agents read English (ECO-042).

**DEV-2.3** User-facing text MUST live in translation resources (for example
`locales/pl.toml`, or `messages.py` dictionaries keyed by English IDs), not
inline in logic.
*Why:* keeps code English and lets the language switch work everywhere.

**DEV-2.4** Polish domain proper names (BDOT10k, PMAXTP, TERYT, NMT) MAY be
used as identifiers when they are the official name of a dataset or system.
Common words MUST be translated (`road_class`, not `klasa`).
*Why:* official names are what users and agents search for.

---

## 3. Git

**DEV-3.1** Branches: `main` (released state, default branch on GitHub),
`develop` (integration), topic branches `<type>/<topic>` from `develop`
(`<type>` is a Conventional Commits type, DEV-4.1) and `hotfix/<topic>` from
`main`.
*Why:* one model for every repository (ECO-008).

**DEV-3.3** Without the author's approval in the current session an agent
MUST NOT merge a pull request, create or move tags, publish a release,
force-push a branch that is shared or merged, or rewrite the history of
`main` or `develop`. Pushing its own topic branch and opening a pull request
are allowed.
*Why:* these operations are visible to consumers and hard to undo (ECO-030).

**DEV-3.4** A cross-project change planned in Nogat (DEV-17.5) is made on a
dedicated branch of the target repository and follows the target's
`CLAUDE.md`, including its CHANGELOG and PROGRESS rules.
*Why:* the target repository stays the authority over its own rules.

**DEV-3.5** Work MUST be committed in the repository it belongs to.
*Why:* uncommitted work is invisible to other agents and blocks history
rewrites and branch renames.

**DEV-3.6** `main` and `develop` are protected on GitHub by a ruleset: pull
request required, 0 approvals, required checks = the three non-experimental
`gate` jobs (and `db` where the project has that job, DEV-7.7), force push and
deletion blocked, no bypass actors. Every pull request (topic → `develop`,
`develop` → `main`, hotfix → `main`, `main` → `develop`) is merged with a
merge commit, the only merge method the ruleset allows. A tag ruleset blocks
update and deletion of `v*` tags. For a history rewrite the author disables
the ruleset, rewrites, re-enables it and notes it in PROGRESS.
*Why:* ECO-030, ECO-037; nothing reaches `main` or `develop` without a pull
request and a green gate. Merges and tags still rest on DEV-3.3.

---

## 4. Commits

**DEV-4.1** Subjects MUST follow Conventional Commits:
`<type>[(<scope>)][!]: <description>` with type `feat`, `fix`, `docs`, `test`,
`refactor`, `perf`, `style`, `build`, `ci` or `chore`; `!` marks a breaking
change. Merge commits and git's own `Revert "…"` subjects are exempt.
*Why:* machine-readable history; the gate checks exactly this.

**DEV-4.2** Commits made by the author and by agents have the author
`Daldek <git@debever.pl>`; each repository MUST set `user.name` and
`user.email` locally. The committer is not checked and merge commits created
by GitHub are exempt. External contributors keep their identity (DEV-16.5).
*Why:* ECO-006, ECO-038; a repository-local setting stops agents committing
under their own identity.

**DEV-4.3** Messages MUST NOT contain `Co-Authored-By` trailers naming AI
tools, `Claude-Session:` lines, "Generated with ..." lines or other AI
attribution. The gate rejects such commits.
*Why:* ECO-006; agent defaults add these lines, so a check is the only
reliable control.

**DEV-4.4** One logical change per commit, together with the documentation
that describes it.
*Why:* review and revert by agents operate on commits.

**DEV-4.5** Commit messages and authors are checked once, when commits enter
`develop` or, for a hotfix, `main`: locally by the gate (DEV-7.6) and in CI on
pull requests into `develop` and on pull requests from `hotfix/*` into
`main`. Messages are checked on every such pull request; the author check
applies only to pull requests from the repository's own branches, not to
forks or Dependabot. Other pull requests into `main` and pushes are not
checked again.
*Why:* ECO-038, ECO-049.

---

## 5. Repository layout

**DEV-5.1** (`tool`, `hub`) Package code MUST be in `src/<package>/`. (`app`)
Another layout MAY be used and is described in `CLAUDE.md`.
*Why:* ECO-011.

**DEV-5.2** Standard top level:

```
<repo>/
├── src/<package>/      # code, package data, py.typed
├── tests/
│   ├── unit/           # offline, fast
│   ├── integration/    # offline, several modules or a database
│   ├── contract/       # interface parity, generated-file drift, registry
│   └── fixtures/
├── docs/               # DOC §1
├── scripts/            # gate.sh, check-commits.sh and helpers
├── .github/            # workflows, dependabot.yml, PR template
├── README.md  CLAUDE.md  LICENSE  …   # required files: DOC §1
├── pyproject.toml  uv.lock
└── .editorconfig  .gitattributes  .gitignore  .env.example
```

*Why:* agents locate tests, docs and gates without exploration. A test that
needs a service or a database carries a marker (DEV-10.1), not a directory.

**DEV-5.3** All tool configuration MUST be in `pyproject.toml`; no
`setup.cfg`, `tox.ini`, `.flake8`, `pyrightconfig.json`.
*Why:* one file for agents to read and edit.

**DEV-5.4** Package data (templates, translations, tables, web assets) MUST be
inside `src/<package>/` and covered by a test that imports or reads it from
the installed package.
*Why:* missing package data is the most frequent defect for consumers
installing from a wheel (ECO-011).

---

## 6. Python environment and dependencies

**DEV-6.1** `requires-python` is `>=3.12`.

**DEV-6.2** uv MUST manage environments and dependencies; the environment is
`.venv/` in the repository root; commands are run through `uv run`.
*Why:* ECO-012; one invocation pattern for agents.

**DEV-6.3** `uv.lock` MUST be committed, and every environment of the
repository (development, CI, deployment, container build) MUST be installed
with `uv sync --locked`; the check of a built wheel (REL-2.3) installs the
wheel.
*Why:* ECO-012; a stale lock fails the install instead of being ignored.

**DEV-6.4** (`tool`) Runtime dependencies on third-party packages MUST be
ranges with a lower bound; an upper bound only for a known incompatibility,
with a comment naming the reason. Dependencies on ecosystem projects follow
REL §5.
*Why:* exact pins in a library make consumers unsolvable; reasons for caps are
otherwise forgotten.

**DEV-6.5** Optional features MUST be extras (`[mcp]`, `[api]`, `[raster]`,
`[viz]`, `[all]`); development tools MUST be a `dev` dependency group. A
missing extra raises `missing_dependency` (`error_registry.json`) naming the
install command.
*Why:* keeps base installs light for agents (MCP startup time) and makes the
fix self-explaining.

---

## 7. Code quality

**DEV-7.1** Formatting: `ruff format`, line length 88, double quotes.
*Why:* ECO-009.

**DEV-7.2** Linting: `ruff check` with at least
`select = ["E", "F", "W", "I", "UP", "B", "SIM", "C4", "D"]` and
`pydocstyle.convention = "numpy"`; tests MAY ignore `D`.
*Why:* `D` enforces the docstrings agents rely on.

**DEV-7.3** Type checking: mypy over `src/` and `tests/` with `strict = true`.
A shortfall is a per-module override in `pyproject.toml`, listed as a
deviation in `CLAUDE.md` (DEV-1.2).
*Why:* ECO-010.

**DEV-7.4** (`tool`) The package MUST ship `py.typed` and declare
`Typing :: Typed`.
*Why:* a typed public API gives an agent writing consumer code errors before
it runs the code.

**DEV-7.5** Package coverage MUST be at least 80%; `[tool.coverage.report]
fail_under` is the floor. Setting it below 80 or lowering it is a deviation
line in `CLAUDE.md` (DEV-1.2).
*Why:* the gate enforces the floor; a deviation line keeps a lowered floor
visible to the next agent.

**DEV-7.6** Each repository MUST have `scripts/gate.sh` (template
`standards/ci/gate.sh` with `check-commits.sh`) that works from a git worktree
and runs, in order: `ruff format --check`, `ruff check`, mypy, one pytest call
over `tests/` with coverage (selection per DEV-10.1; contract tests are part of
`tests/`), and the commit step: an identity preflight (git must commit as the
author, DEV-4.2), then the checks of DEV-4.1 to DEV-4.3 on commits already
made. Run the gate before every commit and do not commit while any other step
fails; a failing message on an unpushed commit is repaired by amending it,
which needs no approval.
*Why:* one command for agents to verify work; the message of a commit cannot
be checked before the commit exists.

**DEV-7.7** CI (GitHub Actions) MUST run the gate on push and pull request to
`main` and `develop`: on Linux, macOS and Windows for `tool` projects; an
`app` project MAY run the platform matrix without `db` tests plus a Linux `db`
job; the `hub` runs on Linux until the `nogat` package exists. Templates:
`standards/ci/ci.yml` (gate on the three systems) and `standards/ci/live.yml`
(weekly `live` tests).
*Why:* file-system and path bugs appear only on the platform that has them.

---

## 8. Naming

**DEV-8.1** Python naming: `snake_case` functions and variables, `PascalCase`
classes, `UPPER_SNAKE_CASE` constants, `_prefix` for internal names.

**DEV-8.2** Physical quantities MUST carry the unit in the name: `area_km2`,
`elevation_m`, `discharge_m3s`, `precipitation_mm`, `intensity_mm_h`,
`duration_min`, `timeout_s`, `slope_percent`, `slope_m_per_m`, `size_bytes`.
*Why:* removes unit ambiguity for people and agents.

**DEV-8.3** Function name prefixes carry meaning and MUST be used
consistently across projects:

| Prefix | Meaning |
|---|---|
| `fetch_` | read live data from a remote service, no files written |
| `download_` | write files from a remote source |
| `check_` | plan or availability check, no writes |
| `find_`, `search_` | look up identifiers by criteria |
| `list_` | enumerate known items |
| `read_` | read local or stored data, offline |
| `parse_` | turn text or bytes into objects |
| `build_` | construct objects, URLs, derived data |
| `sync_` | bring local store in line with a source |
| `calculate_` | pure computation |
| `export_` | write a derived file for users |

*Why:* an agent infers effects (network, writes) from the name.

---

## 9. Docstrings and comments

**DEV-9.1** Every public module, class and function MUST have a NumPy-style
docstring in English with `Parameters`, `Returns` and `Raises`; public API
adds an `Examples` section.
*Why:* examples are what agents extract.

**DEV-9.2** Units MUST be stated in docstrings in square brackets (`[km2]`).

**DEV-9.3** Comments explain why, not what; open questions belong in PROGRESS
or an ADR, not in code.

---

## 10. Testing

**DEV-10.1** pytest runs with `--strict-markers`. Registered markers: `live`
(real network services), `db` (needs a database), `slow` (more than ~10 s or
Docker). The default run and the gate MUST exclude `live`, and `db` where no
database is available.
*Why:* deterministic offline runs for agents; a marker says what a test needs.

**DEV-10.2** Unit tests MUST NOT access the network; HTTP is mocked (for
example `respx`) or replaced by recorded fixtures.

**DEV-10.3** Live tests MUST be runnable on demand; CI runs them weekly
(`standards/ci/live.yml`), never in the gate.
*Why:* upstream services change without notice.

**DEV-10.4** (`tool`) Generated files (`AGENTS.md`, `llms.txt`,
`openapi.json`) are never edited by hand. Contract tests in `tests/contract`
check that each equals its generator's output, that option names have parity
across library, CLI, MCP and REST, that error codes match
`error_registry.json`, and the size budgets of generated files (DOC-1.7).
*Why:* the agent interface depends on these invariants; a check proves
generated files are fresh.

**DEV-10.5** Test names: `test_<unit>_<scenario>[_<expected>]`; tests assert
behaviour, not the wording of messages.

**DEV-10.6** (`tool`) A producer MUST ship a public `<package>.testing`
module (`kartograf.testing`, `obserwator.testing`) in its installed wheel,
not under `tests/`, that builds small, valid instances, offline, of every
format another project reads from its store or files (registry edges whose
`via` includes `store` or `file`), and keep it in step with those formats;
the registry lists it in the producer's `exchange` as `<tool>-testing`.
Consumers' contract tests use it, with the producer at the version they pin,
not the producer's formats written by hand.
*Why:* a format change then breaks the consumer's tests at the producer's
release instead of at users.

---

## 11. Errors

**DEV-11.1** Each project MUST define one base exception (`<Project>Error`)
carrying `code` (from the shared registry), `message`, `details`
(JSON-compatible) and optional `hint`; subclasses select a default code.
*Why:* ECO-015.

**DEV-11.3** Validation MUST happen at system boundaries (CLI, MCP, REST,
public functions) and MUST name the offending option and allowed values.
*Why:* agents repair calls from `details`; silent coercion hides mistakes.

---

## 12. Logging

**DEV-12.1** Modules use `logging.getLogger(__name__)`; libraries MUST NOT
configure handlers or call `print`.

**DEV-12.2** CLI logs and progress go to stderr; the level is set by
`--verbose`/`--quiet` and `<TOOL>_LOG_LEVEL`.
*Why:* stdout is reserved for results (AGI §3).

**DEV-12.3** Use `%`-style arguments in log calls; never log secrets, tokens
or credential-bearing URLs.

**DEV-12.4** A server, an `app` or a tool's command that answers HTTP such as
`gui serve`, keeps three logs: the access log, one record per HTTP request it
answers; the application log, its warnings, errors and exceptions; and
lifecycle records of its start, with a summary of its settings, its stop and
the deletion of old files. A record is one JSON object per line of UTF-8 JSON
Lines, valid against Nogat `schemas/log/record-1.schema.json` (`nogat-log/1`),
which admits no key but these:

| Key | In | Value |
|---|---|---|
| `time` | every record | RFC 3339 in UTC with `Z` |
| `level` | every record | `debug`, `info`, `warning`, `error` or `critical` |
| `app` | every record | the project's name in lower case |
| `version` | every record | the server's version |
| `kind` | every record | `access`, `app` or `lifecycle` |
| `request_id` | every record | 16 random hexadecimal digits of the request it belongs to, never sent to the client; `null` outside a request |
| `method`, `path`, `status`, `bytes`, `duration_ms` | `access` | the method, the path with its query (DEV-12.5), the status, the bytes of the body sent, the time to the last byte |
| `agent` | `access` | the class of the User-Agent (DEV-12.5) |
| `event`, `message`, `error` | `app` | a stable code or the logger's name, the message, the exception's `type`, `message` and `stack` or `null` |
| `event`, `message`, `settings` | `lifecycle` | `start`, `stop`, `prune` or another stage of the server, a fixed text, in `start` the summary of the settings |

*Why:* one format, read the same way in every project (ECO-066).

**DEV-12.5** No log holds a client's IP address, a cookie, a credential
header, a request body or an uploaded file's name, and an IP address in a
message, traceback or path is written `[ip]`; the User-Agent is kept only as
`agent`: `bot` when it names a robot, `browser` when it starts with
`Mozilla/`, `script` for any other value, `none` without one. In `path` a
query parameter that may carry personal data or a credential (`REDACTED` of
the reference module: free text, names, e-mail, tokens and keys) keeps only
its name, and static content (files, map tiles, documents the same for every
client) answered below 400 is not logged.
*Why:* a log serves operation; an address, a full User-Agent or a search text
could single out a person (ECO-066).

**DEV-12.6** Records go to `<state_dir>/<project>/logs/<kind>-YYYY-MM-DD.jsonl`
by the UTC date of `time`, `state_dir` resolved as DEV-18.1 says, in an app
too, and the server deletes a file once its date is 14 days old: at start and
at each 00:00 UTC. In a container, `NOGAT_STATE_DIR` names the directory in
which the host's `<state_dir>/<project>` is mounted as `<project>`, so the
files land where a server outside a container writes them.
*Why:* the deletion needs no root, journald or Docker setting (ECO-066).

**DEV-12.7** Standard output and error, and with them the journal or the
container's log, get only the lifecycle records and the app records of level
`error` and `critical`, these with `request_id` and `message` `null` and
`error` holding only its `type`, whatever the level of DEV-12.2. A
container's logging driver is `local` with `max-size: "1m"` and
`max-file: "3"`.
*Why:* what outlives the 14 days names no request (ECO-066).

**DEV-12.8** uvicorn runs with `access_log=False` and `log_config=None`
(`--no-access-log --log-level warning` on its command line): the server's own
middleware writes the access log, outermost, so that it records the rate
limit's answers too, and the server configures no other log handler. nginx
in front of a server keeps no log: `access_log off;` and
`error_log /dev/null;`, which also drops the rejections of `limit_req` and
`limit_conn`, and it passes no `X-Request-ID`.
*Why:* nginx names the client in an error of a request at every level, `crit`
included (ECO-066).

**DEV-12.9** A Python server does all of this with Nogat
[standards/reference/nogat_logging.py](reference/nogat_logging.py), copied byte
for byte (DEV-15.6): `ServerLog` for the files, the deletion, standard error
and the application log, `AccessLog` for the ASGI middleware. Its README gives,
with its path, the command that reads its logs:
`jq -cs 'sort_by(.time)[] | select(.kind != "access" or .status >= 500)' <state_dir>/<project>/logs/*.jsonl`;
use is counted by the statistics of DEV-15.11, never from the logs.
*Why:* one implementation to review, and `drift` names every copy that is
behind or edited (ECO-066).

---

## 13. Security

**DEV-13.1** Secrets MUST be read from environment variables only (user
credentials: DEV-18.4); `.env` is git-ignored; `.env.example` lists every
variable without values.

**DEV-13.2** Every HTTP request MUST have a timeout; retries use bounded
exponential backoff.

**DEV-13.3** Inputs that become paths MUST be resolved and checked against
allowed roots; reject `..`, control characters and URL metacharacters in
identifiers.
*Why:* agents hallucinate paths and identifiers; MCP servers expose the file
system to them.

**DEV-13.4** SQL MUST use parameterised queries.

**DEV-13.5** Licences of dependencies MUST be compatible with the project
licence and the distribution channel; GPL dependencies MUST be named in
`README.md` and `CLAUDE.md`.

**DEV-13.6** Dependency updates and supply chain:
- Dependabot (`.github/dependabot.yml`, template in `standards/ci/`) updates
  GitHub Actions weekly in grouped pull requests;
- GitHub Actions are pinned to a full commit SHA with the version in a
  comment; Dependabot updates both;
- GitHub "Dependabot security updates" are enabled in the repository settings
  for Python vulnerabilities;
- CI runs `pip-audit` weekly and on pull requests over PyPI packages only
  (ecosystem packages are excluded); the job is not a required check, and an
  accepted finding is ignored by ID with a comment;
- third-party versions change with release sets (REL §6), not per project;
  a security fix is a patch release set (REL-6.6).
*Why:* ECO-040.

**DEV-13.7** Public repositories MUST have `SECURITY.md` and GitHub private
vulnerability reporting enabled; reports are not filed as public issues.

---

## 14. Files and encoding

**DEV-14.1** UTF-8, LF line endings, final newline, no trailing whitespace,
enforced by `.editorconfig` and `.gitattributes` (`* text=auto eol=lf`).
Byte-exact fixtures (golden CSV) MUST be marked `-text` in `.gitattributes`.
*Why:* Windows users and agents on different platforms.

**DEV-14.2** Indentation: 4 spaces for Python, 2 for JSON, YAML, TOML,
Markdown, JavaScript, CSS.

---

## 15. Frontend (profile `app`)

**DEV-15.1** JavaScript: ES modules, `camelCase`, `PascalCase` for classes and
components, 2-space indent, 100-column lines, JSDoc for exported functions.
No build step is required; vendored libraries keep their licence files.

**DEV-15.2** UI text in Polish through translation resources (DEV-2.3);
`data-*` attributes and CSS classes in English.

**DEV-15.3** A GUI follows Nogat's visual identity in
[design/](../design/README.md): a copy of `tokens.css` that names the Nogat
commit it came from and no colour, font or size outside its tokens, the light
and the dark theme, the project's mark as favicon and in the top bar, and the
shell of the guidelines (top bar, navigation rail, resizable side panel).
*Why:* the GUIs serve one user as one family of tools (ECO-055).

**DEV-15.4** A GUI shows the kit's app menu, `<nogat-app-menu>` from Nogat
`design/kit/`, in its top bar left of the theme switch, on every page but its
admin page (DEV-15.13). It lists the GUIs whose address the deployment sets
in `[nogat.gui]` of `nogat.toml` (DEV-18.1), one key per registry name in
lower case; the app passes that table to its page, and with no other GUI set
the menu is not drawn. An entry opens its GUI in the tab named
`nogat-<name>`.
*Why:* one person moves between the GUIs (ECO-058).

**DEV-15.5** A GUI hands data to another as `nogat-handoff/1` (Nogat
`schemas/exchange/handoff-1.schema.json`) through the kit's `nogat-handoff.js`.
The producer offers „Kopiuj do <GUI in genitive>” and „Plik przekazania”; the
file is `<subject>.handoff.json` in 2-space JSON with a final newline. The
consumer offers „Wczytaj z <GUI in genitive>” with „Plik przekazania…” and
„Wklej ze schowka”, checks the envelope against its copy of the schema and
the payload against its owner's schema, and names each problem in Polish.
Copying falls back to a selected text field where the Clipboard API is
missing or refused.
*Why:* three implementations differed in file name, text and clipboard
(ECO-058).

**DEV-15.6** Files of Nogat's kit, tokens, marks, schemas and reference module
(DEV-12.9) are copied byte for byte and never edited in the project (a token
copy keeps only the leading comment of DEV-15.3); a change is made in Nogat
and copied again. `drift` reports each copy as current, behind or modified
(HUB-4.1).
*Why:* copies that drift unseen split the shared look and contracts again.

**DEV-15.7** A public GUI, one that a deployment with `[nogat.operator]`
(DEV-18.1) opens to anyone without signing in, serves its terms at
`regulamin.html` beside its start page: the kit's `nogat-terms.html`, filled
as `design/README.md` says from `[nogat.operator]`, `[nogat.gui]` and the
project's own values, with the blocks of its data sources kept, and refilled
with each kit version it copies. Every view but the admin page (DEV-15.13)
links „Regulamin” to it visibly in its footer or status bar, beside the
attribution lines (DEV-20.5), and the app menu and `<nogat-sources>` pass it
in their `terms` attribute; every such link opens a new tab
(`target="_blank"`, `rel="noopener"`). A GUI run without
`[nogat.operator]`, or used only by its operator behind a sign-in, has
neither page nor link. A GUI loads no script, style or font from another
server: only basemaps and map layers come from their providers' servers.
*Why:* one text tells everyone who uses a public GUI its rules and what
happens to their data (RODO art. 13; ECO-061, ECO-062); a link that replaced
the GUI's tab would end its session and lose the user's work; § 8 ust. 5
names only the providers of map layers as receiving the visitor's IP
address (ECO-068).

**DEV-15.8** Every view of a public GUI but its admin page (DEV-15.13) shows
in its footer or status bar, beside „Regulamin”, the statement
„Serwis jest niekomercyjny i bezpłatny, nie zawiera reklam i nie służy
działalności gospodarczej operatora. Służy celom badawczym i edukacyjnym.
Dane IMGW-PIB są w nim wykorzystywane do celów niezarobkowych, zgodnie z
regulaminami IMGW-PIB.”, which opens § 3 of the terms.
*Why:* the author's statement of what the services are (ECO-062).

**DEV-15.9** A public GUI limits the requests of each client IP address in
its own server, the app or its reverse proxy (behind a proxy, the address the
proxy reports, trusted only from it): by default 300 requests in 60 s, static
files not counted, settable per GUI as `request_limit` and `request_window`
(DEV-18.1); a GUI MAY give map tiles a limit of their own, named in its
README. Over the limit it answers `429` with `Retry-After` in seconds, a page
with „Zbyt wiele żądań. Spróbuj ponownie za <n> s.” and an API route with the
error document of `rate_limited` (AGI-6.3); the address stays in memory for
the window only and is never written to disk or a log.
*Why:* protection against excessive requests without storing addresses
(ECO-062).

**DEV-15.10** A public GUI and its reverse proxy log only as DEV-12.4 to
DEV-12.9 say, which § 8 of its regulamin describes: no IP address in any log,
access, error or application, the access and application logs deleted after
14 days, and nothing on standard output or error that names a request.
*Why:* logs serve the operation of the service, not the identification of
its users, and the regulamin says so (ECO-062, ECO-063, ECO-066).

**DEV-15.11** A public GUI counts its use in daily totals only, the requests
of its admin panel not counted (DEV-15.13). For each request the rate limit
counts, a visitor is the HMAC-SHA-256 of the client IP address and the
User-Agent under a 32-byte random salt drawn at start and at each 00:00 UTC;
salt and hashes stay in memory to count the day's distinct visitors and are
never written. Each UTC day is one JSON object per line of
`<data_dir>/<project>/stats.jsonl` (DEV-18.2), in date order, with the keys
below; the GUI rewrites the day's line at least every 10 minutes and at
shutdown, adds to it after a restart (with a new salt), and names in its
README what it counts as each total.

| Key | Value |
|---|---|
| `date` | the UTC day, `YYYY-MM-DD` |
| `visitors` | distinct visitors of the day |
| `page_views` | HTML pages served |
| `stations_opened` | stations opened; 0 in a GUI without stations |
| `analyses_run` | computations run |
| `downloads` | files downloaded |

*Why:* how the services are used, without tracking anyone and without a
cookie (ECO-062).

**DEV-15.12** A public GUI offers „Zgłoś uwagę”: one text field of 1 to
5,000 characters with „Nie wpisuj danych osobowych. Jeśli chcesz odpowiedzi,
napisz na <e-mail>” under it, `<e-mail>` being `[nogat.operator] email`, and
no contact field. `POST /api/feedback` stores the text with a context the GUI
adds itself (the view, the station, the view's parameters, the app version),
never an IP address or User-Agent, as a report with the fields below, in the
GUI's database or, without one, as a line of
`<data_dir>/<project>/feedback.jsonl`, and answers
`{"id": <id>, "status": "ok"}`; only the operator lists, marks and deletes
reports, at `/api/admin/feedback[/{id}]` behind the sign-in of DEV-15.13, and
deletes each once handled.

| Field | Value |
|---|---|
| `id` | integer, ascending |
| `created_at` | UTC time of receipt, ISO 8601 with offset |
| `message` | the text |
| `context` | object of at most 100 KB: `view`, `station` (`null` without one), `parameters`, `app_version` |
| `is_read` | `false` until the operator marks it read |

*Why:* reports carry no personal data, and one format serves every GUI
(ECO-062).

**DEV-15.13** A GUI that stores reports (DEV-15.12) or statistics
(DEV-15.11) serves its admin panel at `/admin/` and its admin API under
`/api/admin/`, an app whose API has a prefix of its own keeping it
(`/api/v1/admin/`); `/admin` answers `308` to `/admin/`, and no other admin
path exists, so a deployment protects exactly `/admin`, `/admin/*` and
`/api/admin/*`. Every admin route checks the header `X-Admin-Key` in
constant time against the credential `admin_api_key`, read per request from
the environment variable `<PREFIX>ADMIN_API_KEY` or the file named by
`<PREFIX>ADMIN_API_KEY_FILE` (DEV-18.4), `<PREFIX>` being the prefix of the
GUI's other settings (`<TOOL>_` in a tool, DEV-18.3; empty where they have
none); a failure answers `401` with the error document of `unauthorized`
(AGI-6.3) and the reason `admin_key_not_configured`, `admin_key_missing` or
`admin_key_invalid`. No key is generated and none is ever logged. An app
with accounts replaces the key with its own role check and keeps everything
else. The core API is the same in every GUI; an app's own sections use
routes of their own under `/api/admin/`.

| Route | Answer |
|---|---|
| `GET /api/admin/feedback?limit=&offset=` | `{items, total, unread_count}`, newest first; `limit` 1 to 200, default 50 |
| `PATCH /api/admin/feedback/{id}` with `{"is_read": bool}` | the report |
| `DELETE /api/admin/feedback/{id}` | `{"status": "deleted"}`; an unknown id answers `404 not_found` |
| `GET /api/admin/stats?from=&to=` | `{days, totals}`: the lines of `stats.jsonl` (DEV-15.11) between the two UTC days, default the last 30, plus the current day as counted so far; `totals` sums every key but `visitors` |
| `GET /api/admin/status` | `{app, version, started_at, uptime_s, data_dir, disk: {free_bytes, total_bytes}, checks: [{name, status, detail}]}`, `status` one of `ok`, `warning`, `failed`; each GUI names its checks in its README |

The page is the kit's `<nogat-admin>` ([design/](../design/README.md)) with
„Zgłoszenia”, „Statystyki” and „Stan”, then the app's own sections; it keeps
the key in `sessionStorage` under `<project>/admin-key/1`, which „Wyloguj”
forgets. It is the operator's, not a public view: no footer statement,
regulamin link, app menu or stats count (DEV-15.4, DEV-15.7, DEV-15.8 and
DEV-15.11 do not apply to it); `<meta name="robots" content="noindex">`;
every admin answer `Cache-Control: no-store`; CSP `'self'`; its requests stay
under the rate limit (DEV-15.9).
*Why:* the operator handles every GUI in one place and one way, and a
deployment protects three paths (ECO-067).

**DEV-15.14** An info text, behind „(i)”, in a help popover or in a
section's „Objaśnienie metod”, explains to the GUI's user what a value or
view means and how it is computed, in this order: a definition of one or two
sentences, then, each only where it applies, the formula with its symbols and
units, how to read the value in one or two sentences, and the sources (norms,
literature, data provider). It is Polish, impersonal and descriptive („Suma
opadów…”, „Liczona z…”), never in the first person, and addresses the user
as „Ty” only in an instruction, as the regulamin does; a unit follows a space
(„12 mm”, „[mm]” in a table head), a decimal a comma and a range an en dash
(„5–10 min”). It holds no experience, opinion or past work of the author or
the operator, no internal identifier (a plan step such as M12, an ADR number,
a branch or plan name), no development status („prototyp”, „docelowo”, „w
planie”), no detail the user cannot act on (the program, module, command,
file, library or palette that computes or draws the value, the server's
capabilities) unless a licence requires naming it, and no long list of
output fields or file contents. Without its formula and sources it has at
most about 400 characters; a longer explanation of a method belongs in the
GUI's guide (instrukcja), which the info text links; an example is in
[design/](../design/README.md#info-texts).
*Why:* every GUI explains its values one way, short enough to read beside
them (ECO-069).

---

## 16. Licence and contributions

**DEV-16.1** Licence: MIT unless an ADR states otherwise.

**DEV-16.2** Public repositories MUST have `CONTRIBUTING.md`, `docs/CLA.md`
and `CONTRIBUTORS.md`.

**DEV-16.4** `CONTRIBUTING.md` MUST describe the workflow: `uv sync --locked`,
`GATE_CHECK_AUTHOR=0 scripts/gate.sh` before a pull request, Conventional
Commits, the CLA and where to report security issues.
`.github/PULL_REQUEST_TEMPLATE.md` MUST contain the CLA checkbox that
`CONTRIBUTING.md` refers to.
*Why:* contributors keep their own identity, which the author check of the
gate would reject (DEV-16.5).

**DEV-16.5** External contributions keep the contributor's identity (DEV-4.2);
CI does not run the author check on their pull requests (DEV-4.5). The CLA is
signed with the checkbox, and the contributor adds their line to
`CONTRIBUTORS.md` in the same pull request (ECO-031).

---

## 17. Working with agents (developers)

**DEV-17.1** Session start: read `CLAUDE.md` and `docs/PROGRESS.md`, run
`git status` and `git log --oneline -10`, confirm the branch and list the
repository's open GitHub issues labelled `request` (DEV-17.5).

**DEV-17.2** Decisions with alternatives are recorded as ADRs (DOC §8).

**DEV-17.3** Session end: `docs/PROGRESS.md` MUST be updated (DOC §6) before
the last commit.
*Why:* the next agent starts from PROGRESS.

**DEV-17.4** A change to a public interface or across more than one module
starts with a plan, `docs/plans/YYYY-MM-DD-slug.md` (goal, options, decision,
steps, results). After the author approves it in a session, the plan gets
the line `Approved: YYYY-MM-DD` under its title; code starts only after
that line exists. `docs/specs/` and `docs/research/` are not used for new
work.
*Why:* ECO-039, ECO-047; prevents agents building the wrong thing at scale.

**DEV-17.5** An agent MUST change only the repository of its session, except
for a cross-project change planned in Nogat (DEV-3.4). A need in another
project is a GitHub issue in that project's repository labelled `request`;
the session that resolves it closes the issue.
*Why:* keeps each project's scope intact; the issue tracker is the list
(ECO-043).

---

## 18. User environment (profile `tool`)

**DEV-18.1** Shared settings live in one TOML file, `nogat.toml`, in the user
configuration directory (`platformdirs.user_config_path("nogat")`, or the path
in `NOGAT_CONFIG`). Section `[nogat]` holds shared keys (`data_dir`,
`cache_dir`, `state_dir`, `lang`, the table `gui` of GUI addresses, DEV-15.4,
and the
table `operator` of who runs a deployment open to others, DEV-15.7: `name`,
`email`, `terms_effective` (a date), `processor`, who carries the traffic and
processes IP addresses for the operator, `processor_transfer`, the sentence
on that processor's transfers outside the EEA, empty without them,
`processor_cookie`, the sentence on its cookie against bots, empty without
one, `mail_provider`, the service holding the operator's mailbox, and
`mail_transfer`, the sentence on its processing outside the EEA, empty
without it);
section `[<tool>]` holds the tool's own keys. A value
comes from the first of: command-line option, environment variable
(`<TOOL>_<KEY>` before `NOGAT_<KEY>`), `nogat.toml` (`[<tool>]` before
`[nogat]`), built-in default. Every tool reads the file with `tomllib` and
works without it and without the `nogat` package.
*Why:* ECO-028.

**DEV-18.2** Data stores live under `data_dir` (default
`platformdirs.user_data_path("nogat")`), one directory per tool,
`<data_dir>/<tool>`, unless the user sets a store root (`--root`,
`<TOOL>_ROOT`, `[<tool>] root`; DEV-19.2). Caches live in `<cache_dir>/<tool>`
(`cache_dir` default `platformdirs.user_cache_path("nogat")`), and state kept
between runs, such as a server's logs (DEV-12.6), in `<state_dir>/<tool>`
(`state_dir` default `platformdirs.user_state_path("nogat")`); tools do not
write caches or state into the current working directory.

**DEV-18.3** Tool-specific environment variables are named `<TOOL>_<KEY>`;
every variable is listed in the tool's README and `.env.example`.

**DEV-18.4** User credentials (CLMS account, store write tokens, API keys) are
read from environment variables only, named in the tool's README and reported
by `config show` (DEV-18.6); never in `nogat.toml`, never printed.

**DEV-18.5** Tools with versioned stores (DEV §19) document in README which
data cannot be downloaded again (versions removed from the source) and how to
back up a store: a copy that preserves hard links (`rsync -aH`; on Windows a
tool that keeps hard links, not Explorer or `robocopy`), or the tool's own
export.
*Why:* sources remove old versions, and a copy without hard links multiplies
the size of a store.

**DEV-18.6** Every `tool` has `<tool> config show --json`: each key with its
value and source, each credential name with present or missing, the store root
with its source (DEV-19.2) and its size. `nogat doctor` uses only this command.
*Why:* `nogat` learns a tool's settings from the tool, not from a copy of its
rules.

---

## 19. Data output (profile `tool`)

A tool that provides a versioned store (a `store` in the registry, HUB-2.5)
writes data in one of two modes. *Plain mode* writes ordinary files without
metadata, as a directory (`output_dir`) or as one file (`output`). *Store
mode* writes the versioned store with sidecars (`root`). Names, defaults,
errors and results are the same in every tool and interface (AGI-1.2,
ECO-051); a tool without a store writes with `--output` and `--output-dir` as
AGI-3.4 says.

**DEV-19.1** The location of the data files a command writes comes from these
options and from no other (not `--store`, not `--path`):

| CLI | API (keyword-only) | `path_role` | Meaning |
|---|---|---|---|
| `-o`, `--output-dir` | `output_dir` | `output` | plain mode: files in a directory |
| `--root` | `root` | `root` | store mode: root of the versioned store |
| `--output` | `output` | `output` | plain mode: exactly one file (an export) |

`output_dir` and `root` form one `one_of` group: giving both is
`validation_error`.
*Why:* one name per target in every tool and interface (AGI-1.2, AGI-3.4).

**DEV-19.2** The store root is the first of `--root`, `<TOOL>_ROOT`,
`[<tool>] root` in `nogat.toml` and `<data_dir>/<tool>` (DEV-18.1, DEV-18.2).
A command with neither `output_dir` nor `output` uses the store at that root,
so no option is required to write; `<tool> config show --json` reports the
root and its source (DEV-18.6). A producer's library names the read-only accessor
of that root `store_root()` (root, source, whether the marker exists; it reads no store).
*Why:* the common call needs no flag, and the store has one place (ECO-051).

**DEV-19.3** A REST server writes only to the store root set in its server
configuration and only with writes enabled, and it accepts no `root`,
`output_dir` or `output` in a request. An MCP server writes only inside its
`--allow-dir` directories and only with `--allow-writes`, so a default root
outside them is `forbidden` (AGI-5.8).
*Why:* a client must not choose where a server writes (DEV-13.3).

**DEV-19.4** In plain mode a command selects the same data as in store mode,
unless its catalog entry and documentation declare a selection rule that
applies only to plain mode. A unit that such a rule leaves without data is
skipped, with a warning notice of code `skipped_incomplete` and an entry
`{id, reason, message}` in `skipped[]` of the domain result (`id` as in
`items[]`, `reason` `skipped_incomplete`); when every unit is skipped the
command fails with `no_data`, reason `skipped_incomplete`.
*Why:* a difference between the modes is declared and visible in the result.

**DEV-19.5** In plain mode the file name is the name the file has in the
store, a unit name that the tool declares and knows before the transfer; a
file given by `output` has the name the caller gave it. The directory is flat
unless names within one request can collide, and the tool then declares a
relative sub-path.
*Why:* the names are known before the first byte, so DEV-19.6 can check them.

**DEV-19.6** Before the first byte is transferred, and before any request, a
plain write checks `output_dir` itself: one that is, or lies inside, a store
is a `conflict` (reason `output_in_store`, DEV-19.11) with the directory as
the only entry of `details.paths`. It then builds the full list of targets
and checks it, first for duplicate names (`conflict`, reason
`duplicate_output_name`), then for a target that would enter a directory with
a store marker below `output_dir` (`output_in_store`, the target path), then
for existing targets without `--force` (`conflict`, reason `output_exists`).
The error lists every offending path in `details.paths`, and nothing is
written.
*Why:* an agent repairs the whole call at once.

**DEV-19.7** A plain write goes through a staging directory
`<dir>/.<tool>-incoming/<host>_<pid>_<token>/` on the same file system, where
`<dir>` is `output_dir` or the directory that holds `output`; each file is
verified there and moved into place with `os.replace`. Staging is removed on
success, on error, on SIGINT and on SIGTERM, and leftovers older than 24
hours are removed on the next run.
*Why:* an interrupted write leaves no partial target.

**DEV-19.8** A plain write creates the output directory if it is missing and
nothing but the data files: no sidecar, no hard link, no `versions/`
directory, so it works on FAT, exFAT and SMB.

**DEV-19.9** `--force` in plain mode replaces existing targets, each
atomically with `os.replace`, and never deletes another file; without it
nothing is overwritten. In store mode `--force` fetches again and gives a new
version or `unchanged`, and never overwrites.

**DEV-19.10** `--check` is the only way to plan without effects, in both
modes, and `check_command` returns the same plan (AGI-2.1). In plain mode the
plan lists each target with its action: `write`, `replace` (only with
`--force`) or `conflict`; a plan that lists `conflict` is a successful result
(status `ok`, exit 0), and only the real run fails with `conflict`. In store
mode a refusal of the root that is a `conflict` (`nested_store`,
`not_empty`) is one `conflict` action for the root in the same successful
plan, with no request; one that is not a `conflict` (`store_unavailable` for
a root without marker, `data_error` for an unreadable marker) is raised by
`--check` as that error.

**DEV-19.11** An `output_dir` that is, or lies inside, a store of any tool is
a `conflict` with reason `output_in_store`; the refusal comes before any
request, applies to every target, and `details.paths` is the output
directory. A store found only below `output_dir`, a directory the write for a
particular target would enter that contains a store marker, is reported for
that target's path. The hint names `--root`. A store is recognised by its
marker file name alone (DEV-19.12).

**DEV-19.12** A store root holds the marker `<tool>-store.json`, a JSON
document of schema `<tool>-store/1` with at least the fields `schema`, `tool`,
`created_at` and `producer_version`. The markers are `kartograf-store.json`
and `obserwator-store.json`; a tool looks for exactly these names and imports
nothing from another tool.
*Why:* each tool refuses another's store without depending on it (ECO-051).

**DEV-19.13** A tool creates the marker on its first write into an empty or
new root. A root that has the tool's layout but no marker is
`store_unavailable` with the hint `<tool> store init --root <path>`, and
`store init` verifies the layout and writes the marker.

**DEV-19.14** A store never nests in another store of any tool: before it
writes, a command looks for markers in the ancestors of the root and in its
existing descendants, and a nested store is a `conflict`.

**DEV-19.15** Store mode keeps the layout of the tool:
`…/versions/…/<label>_<sha8>/<file>` with `<file>.meta.json` beside it,
published by `os.link` from `.incoming/` with the sidecar linked last, so it
needs hard links. The current version is the one the tool's read API returns;
a link to it at a standard path is the tool's own addition, not part of this
convention.

**DEV-19.16** Every sidecar `<tool>-meta/N` has these fields with the same
meaning; a tool brings its sidecar in line by adding optional fields within
`/1`, never by renaming:

| Field | Meaning |
|---|---|
| `schema` | `<tool>-meta/N` |
| `producer` | name of the package that wrote the file (`distribution.import_name` in the registry) |
| `producer_version` | version of that package |
| `dataset` | dataset key `<scope>.<provider>.<name>` as written, never rewritten; scope is a country code, `eu` or `global` |
| `dataset_key` | current key of `dataset` (a renamed key resolved), null when the tool does not know it; the read API returns it |
| `country` | country of the data in capitals: ISO 3166-1 alpha-2 code, `EU` or `GLOBAL` |
| `provider` | short name of the organisation that publishes the data |
| `size_bytes` | size of the main file in bytes |
| `sha256` | SHA-256 of the main file, 64 lower-case hexadecimal digits |
| `downloaded_at` | UTC time the file was downloaded or built, ISO 8601 with offset |
| `license` | object `{id, attribution, url}`: licence identifier, attribution text, link to the terms |
| `request` | object: the request that produced the file, in the tool's own keys |
| `extra` | object: tool-specific details; a reader ignores keys it does not know |

*Why:* a consumer reads the stores of every tool through the same fields
(ECO-051).

**DEV-19.17** Options that act on versions are valid only in store mode:
`--upgrade`, `--plan` (saved update plans), the selection of several
campaigns (`--all-campaigns`) and any update mode other than the default;
with `output_dir` each is a `validation_error` that names `--root`.

**DEV-19.18** A command whose input is the store (a command that builds
derived data from stored versions) is store-only and says so in its catalog
entry. Every other writing command supports both modes; one that needs inputs
fetches them to staging and in plain mode writes only its result.

**DEV-19.19** The domain result of a writing command lists `files[]`:
`{path, size_bytes, sha256, status}`, with `sha256` computed while the file is
streamed. `status` is `written` or `replaced` in plain mode and `new`,
`unchanged` or `relabeled` in store mode; per-unit outcomes stay in `items[]`
(AGI-4.2), and skips are notices.

**DEV-19.20** The reasons of this section are `details.reason` values
(AGI-4.3) under the codes given above: `duplicate_output_name`,
`output_exists`, `output_in_store`, `skipped_incomplete`, `nested_store`
(`conflict`, DEV-19.14) and `not_empty` (`conflict`: a root that holds other
files and is no store). A tool adds no registry code for the convention
(ERR-1).

---

## 20. Provider attribution

Every profile. A product is anything a project shows, writes or returns
with a provider's data or with results derived from them. The lines below
are quoted byte for byte: Polish quotation marks „ ”, en dashes –, no final
full stop, never paraphrased or translated away; in an English context the
Polish line stays and an English gloss MAY follow it.

| Mark | Line |
|---|---|
| S | Źródłem pochodzenia danych jest Instytut Meteorologii i Gospodarki Wodnej – Państwowy Instytut Badawczy |
| P | Dane Instytutu Meteorologii i Gospodarki Wodnej – Państwowego Instytutu Badawczego zostały przetworzone |
| PS | Źródłem pochodzenia danych jest Instytut Meteorologii i Gospodarki Wodnej – Państwowy Instytut Badawczy, dane pochodzą ze strony https://klimat.imgw.pl/opady-maksymalne |
| PP | Dane Instytutu Meteorologii i Gospodarki Wodnej – Państwowego Instytutu Badawczego pochodzące ze strony https://klimat.imgw.pl/opady-maksymalne zostały przetworzone |
| M | „Modele probabilistyczne opadów maksymalnych o określonym czasie trwania i prawdopodobieństwie przewyższenia – Projekt PMAXTP”, red. Bogdan Ozga-Zieliński, Instytut Meteorologii i Gospodarki Wodnej – Państwowy Instytut Badawczy, Warszawa 2022 |
| C | Źródło danych: Český hydrometeorologický ústav (ČHMÚ), https://opendata.chmi.cz, licencja CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/) |
| CK | Źródło: ČHMÚ, CC BY 4.0 |
| CP | Dane ČHMÚ zostały przetworzone (`<what was done>`) |
| G | Źródło: Główny Urząd Geodezji i Kartografii – GUGiK, `<products>` (wytworzono `<period>`, pozyskano `<date>`); dane przetworzone |
| GK | Źródło: GUGiK (`<products>`) |
| SG | Źródło: ISRIC – World Soil Information, SoilGrids, licencja CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/); dane przetworzone |
| SK | Źródło: ISRIC SoilGrids, CC BY 4.0 |
| Z | Źródło: Český úřad zeměměřický a katastrální (ČÚZK), `<products>` (pozyskano `<date>`), licencja CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/); dane przetworzone |
| ZK | Źródło: ČÚZK, CC BY 4.0 |
| RD | Regulamin danych IMGW-PIB: https://danepubliczne.imgw.pl/regulations |
| RH | Regulamin serwisu hydrologicznego IMGW-PIB: https://hydro.imgw.pl/#/regulamin |
| RK | Regulamin danych PMAXTP: https://klimat.imgw.pl/opady-maksymalne |

CK, GK, SK and ZK are the short forms of C, G, SG and Z for the strip of a
GUI view only (DEV-20.5) and are never written into a product: CK with
„ČHMÚ” linked to https://opendata.chmi.cz and „CC BY 4.0” to the licence, SK
and ZK with „CC BY 4.0” linked to the licence, and one GK naming the
products of every G of the view, each once.

In G and Z, `<products>` names the products used, joined by „, ” (e.g.
„NMT, BDOT10k” of GUGiK, „RÚIAN” of ČÚZK); `<period>` the year in which the
data used were created, or the first and the last joined by an en dash
(„2020–2025”); `<date>` the day they were downloaded, `YYYY-MM-DD`, or the
first and the last joined by a spaced en dash („2026-03-24 – 2026-10-29”);
both from the Kartograf metadata of the files.

RD, RH and RK, the terms lines, each name the terms they link and have the
form „Regulamin <whose terms>: <address>”, so a reader of `ATTRIBUTION.txt`
or of a CSV column tells them from the attribution lines.

**DEV-20.1** A product with IMGW-PIB data other than PMAXTP (archives and
current data of danepubliczne.imgw.pl, operational data and station
locations of hydro.imgw.pl and its backend hydro-back.imgw.pl) carries S,
and S and P once the data were processed in any way: parsed, harmonised,
reformatted, aggregated, charted or used to compute a result. Only a
verbatim, untouched copy of an IMGW-PIB file carries S alone.
*Why:* §5 ust. 3 and 4 of the IMGW-PIB terms, repeated by the terms of the
hydrological service (ECO-060); neither requires a line naming
hydro.imgw.pl, which RH links (ECO-065).

**DEV-20.2** A product with PMAXTP data (powietrze.imgw.pl, klimat.imgw.pl)
carries PS and M, and PP as well once the data were processed: a design
rainfall, hyetograph, hydrograph, model input, or a table or file in another
form. For PMAXTP these lines replace S and P.
*Why:* ust. 1 and 2 of the PMAXTP terms, which require the monograph and the
project's address (ECO-060).

**DEV-20.3** A product with ČHMÚ data carries C (the creator, the address of
the material, the licence and its link) and, once the data were modified, CP
naming what was done; an English context MAY use English equivalents of C
and CP with the same elements.
*Why:* ČHMÚ open data are under CC BY 4.0, §3(a)(1) (ECO-060).

**DEV-20.4** A product with data of several providers carries every line that
applies, in the order S, P, PS, PP, M, C, CP, G, SG, Z, each once. A project
keeps the lines in one place in its code, and every surface takes them from
there.
*Why:* lines equal byte for byte merge across tools without duplicates.

**DEV-20.5** The lines are visible and legible, never in a tooltip only, on
every surface with the data or results derived from them:

| Surface | Where the lines go |
|---|---|
| GUI | the strip of the view and the dialog behind it (below) |
| CSV | trailing columns `attribution` and `terms_notice`, one line per cell from the first data row down, empty below; a table with fewer rows than lines joins the rest into its last cell with a newline. Columns a project already has stay (DEV-20.6) |
| JSON | the fields `attribution` and `terms_notice` (DEV-20.6, DEV-20.7) |
| Parquet | the file metadata keys `attribution` and `terms_notice`, each a JSON array of the lines |
| ZIP | `ATTRIBUTION.txt` at the root of the archive |
| plain files in a directory (DEV-19.1) | `ATTRIBUTION.txt` in the directory's root, listed in `files[]` |
| PNG, SVG | footer lines drawn in the image |
| print, PDF, generated reports | a visible line on the page or in the report |
| API, REST, MCP | the fields `attribution` and `terms_notice` of the response (DEV-20.6, DEV-20.7) |
| CLI | the human-readable output that prints data or results |
| model inputs | a header comment of the file, or `ATTRIBUTION.txt` beside it where the format has no comments |

`ATTRIBUTION.txt` is UTF-8 with one line per line, the attribution lines and
then the terms lines of DEV-20.7, in order; a later write to the same place
merges its lines in, each once and in order.

A GUI view shows one strip for all its data, the kit's `<nogat-sources>`,
not one per panel, card, chart or popup: 12 px in the muted text colour, at
most two lines at 1440 px for one IMGW-PIB family (S and P, or PS and PP)
with the short forms, a third allowed when the view shows both, wrapping on
phones. It holds the on-screen lines S, P, PS, PP, CK, GK, SK and ZK, those
the view's data need, each once in the order of DEV-20.4, a short form in
the place of its full line, and ends with „Źródła i warunki”, which opens a
dialog with every line (S, P, PS, PP, M, C, CP, G, SG, Z) and the terms of
DEV-20.7 (RD, RH, RK), and with „Regulamin” where the GUI serves one
(DEV-15.7). A GUI with a welcome window shows the same full content there on
the first visit; one without it reaches the dialog from the strip and the
footer. Files, exports, PNG and SVG images, print views, hand-offs and the
fields `attribution` and `terms_notice` keep the full lines.

*Why:* the terms bind every product made with the data (ECO-060); the
IMGW-PIB and PMAXTP terms require their sentences on the product, while CC
BY 4.0 lets a link carry ČHMÚ's details (ECO-064); GUGiK, ISRIC and ČÚZK
are named the same way, their full lines one click away (ECO-068).

**DEV-20.6** A JSON document, result or hand-off (DEV-15.5) with such data has
`attribution`, an array of the lines as strings. A consumer shows the lines it
receives with the data and carries them into its own products and further
hand-offs, merged without duplicates; a field a project already has for them
(a CSV column, `license.attribution` of a sidecar, DEV-19.16) stays.
*Why:* the obligation follows the data through every tool (ECO-060).

**DEV-20.7** Every GUI view and every exported product with IMGW-PIB data
also carries the links to the terms that apply, one line each in the order
RD (danepubliczne.imgw.pl), RH (hydro.imgw.pl), RK (PMAXTP), right after the
attribution lines and on the surfaces of DEV-20.5, in a GUI view in the
dialog behind its strip; a JSON document, result or hand-off has them in
`terms_notice`, an array of strings carried on like `attribution`. No
product restates, summarises or paraphrases a provider's terms: it carries
the lines of the table and links the rest. ČHMÚ, ISRIC and ČÚZK data take
no terms line, since C, SG and Z name the licence with its link, nor do
GUGiK data, whose conditions of reuse a regulamin links in its § 5.
*Why:* the providers' own terms are the only binding text, and a summary
can mis-state them; products carry only what the providers require (the
author's principle of 2026-11-13, ECO-065); a dialog one click from the data
keeps the screen for the data (ECO-064).

**DEV-20.8** Operational data of hydro.imgw.pl (water states and their
classes, measurements, warnings) are shown as current with their time and
never stored or presented as archive; station locations from it MAY be kept
as reference data with their lines (DEV-20.1).
*Why:* operational data are not the verified archive of danepubliczne.imgw.pl,
and no project keeps them (ECO-060).

**DEV-20.9** A product with GUGiK data (NMT, BDOT10k, PRG and the other data
of geoportal.gov.pl) or results derived from them carries G; a basemap a GUI
loads live from GUGiK's services is credited in the map's own attribution
instead, the orthophoto as „Ortofotomapa © GUGiK”.
*Why:* pkt 1 and 2 of GUGiK's conditions of reuse: its full name, the time
the data were created and acquired, and a note that they were processed
(ECO-068).

**DEV-20.10** A product with ISRIC SoilGrids data or results derived from
them carries SG.
*Why:* SoilGrids is under CC BY 4.0, §3(a)(1) (ECO-068).

**DEV-20.11** A product with ČÚZK data (RÚIAN and the other data of ČÚZK) or
results derived from them carries Z.
*Why:* ČÚZK's open data are under CC BY 4.0, §3(a)(1) (ECO-068).
