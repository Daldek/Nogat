# Development standards

Part of standard 2.1 · IDs `DEV-…`

Related: [DOCUMENTATION_STANDARDS.md](DOCUMENTATION_STANDARDS.md),
[AGENT_INTERFACE.md](AGENT_INTERFACE.md), [ERROR_REGISTRY.md](ERROR_REGISTRY.md),
[RELEASE_AND_DISTRIBUTION.md](RELEASE_AND_DISTRIBUTION.md),
[ECOSYSTEM_HUB.md](ECOSYSTEM_HUB.md).

---

## 1. Project profiles

Requirements apply to all projects unless marked with a profile.

| Profile | Meaning | Projects |
|---|---|---|
| `tool` | Installable Python package; CLI, MCP and REST optional | Kartograf, IMGWTools, Hydrolog, Retman, Hydraulik |
| `app` | Deployed service (web UI, server) | IMGWTools (web GUI), Hydrograf, Archiwista |
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
module that builds small, valid instances, offline, of every format another
project reads from its store or files (registry edges whose `via` includes
`store` or `file`), and keep it in step with those formats. Consumers'
contract tests use it, with the producer at the version they pin.
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
`cache_dir`, `lang`); section `[<tool>]` holds the tool's own keys. A value
comes from the first of: command-line option, environment variable
(`<TOOL>_<KEY>` before `NOGAT_<KEY>`), `nogat.toml` (`[<tool>]` before
`[nogat]`), built-in default. Every tool reads the file with `tomllib` and
works without it and without the `nogat` package.
*Why:* ECO-028.

**DEV-18.2** Data stores live under `data_dir` (default
`platformdirs.user_data_path("nogat")`), one directory per tool,
`<data_dir>/<tool>`, unless the user sets a store root (`--root`,
`<TOOL>_ROOT`, `[<tool>] root`; DEV-19.2). Caches live in `<cache_dir>/<tool>`
(`cache_dir` default `platformdirs.user_cache_path("nogat")`); tools do not
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
root and its source (DEV-18.6).
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

**DEV-19.6** Before the first byte is transferred a plain write builds the
full list of targets and checks it, first for duplicate names (`conflict`,
reason `duplicate_output_name`), then for existing targets without `--force`
(`conflict`, reason `output_exists`). The error lists every offending path in
`details.paths`, and nothing is written.
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
(status `ok`, exit 0), and only the real run fails with `conflict`.

**DEV-19.11** An `output_dir` that is, or lies inside, a store of any tool,
or a directory the write would enter that contains a store marker, is a
`conflict` with reason `output_in_store`, and its hint names `--root`. A
store is recognised by its marker file name alone (DEV-19.12).

**DEV-19.12** A store root holds the marker `<tool>-store.json`, a JSON
document of schema `<tool>-store/1` with at least the fields `schema`, `tool`,
`created_at` and `producer_version`. The markers are `kartograf-store.json`
and `imgw-store.json`; a tool looks for exactly these names and imports
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

**DEV-19.18** A command whose input is the store (a `project` command, or a
command that builds derived data from stored versions) is store-only and says
so in its catalog entry. Every other writing command supports both modes; one
that needs inputs fetches them to staging and in plain mode writes only its
result.

**DEV-19.19** The domain result of a writing command lists `files[]`:
`{path, size_bytes, sha256, status}`, with `sha256` computed while the file is
streamed. `status` is `written` or `replaced` in plain mode and `new`,
`unchanged` or `relabeled` in store mode; per-unit outcomes stay in `items[]`
(AGI-4.2), and skips are notices.

**DEV-19.20** The reasons of this section are `details.reason` values
(AGI-4.3) under the codes given above: `duplicate_output_name`,
`output_exists`, `output_in_store` and `skipped_incomplete`. A tool adds no
registry code for the convention (ERR-1).
