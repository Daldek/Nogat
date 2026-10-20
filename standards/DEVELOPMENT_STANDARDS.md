# Development standards

Version 2.0 · 2026-10-19 · applies to every project listed in `ecosystem.yaml`.

Keywords MUST, MUST NOT, SHOULD, SHOULD NOT and MAY follow RFC 2119. Every
requirement has an ID (`DEV-…`) so project documents, ADRs and adoption plans
can reference it. Rationale follows each requirement; longer reasoning is in
[DECISIONS.md](DECISIONS.md).

Related: [DOCUMENTATION_STANDARDS.md](DOCUMENTATION_STANDARDS.md),
[AGENT_INTERFACE.md](AGENT_INTERFACE.md), [ERROR_REGISTRY.md](ERROR_REGISTRY.md),
[RELEASE_AND_DISTRIBUTION.md](RELEASE_AND_DISTRIBUTION.md),
[ECOSYSTEM_HUB.md](ECOSYSTEM_HUB.md).

---

## 1. Project profiles

Requirements apply to all projects unless marked with a profile.

| Profile | Meaning | Projects (2026-10-19) |
|---|---|---|
| `library` | Python package consumed by other code | Hydrolog |
| `tool` | Package with library + CLI + MCP (+ optional REST) | Kartograf, IMGWTools, Hydrolog (v1.0) |
| `app` | Deployed application (web UI, server) | Hydrograf, Archiwista |
| `pipeline` | Compute package driven by config files, research stage | Hydraulik |
| `assistant` | Natural-language layer over other tools | Retman |
| `hub` | Registry, standards, collected scripts | Nogat |

A project may have several profiles (IMGWTools: `tool` + `app` for its web GUI).

**DEV-1.1** Each project MUST declare its profiles in `ecosystem.yaml` and in
the first section of `CLAUDE.md`.
*Why:* profiles decide which sections of this standard apply; agents need
that without reading the whole standard.

**DEV-1.2** Deviations from this standard MUST be recorded as an ADR in the
project and listed in a "Deviations from the ecosystem standard" section of
`CLAUDE.md` with the requirement ID.
*Why:* undocumented deviations look like mistakes to the next agent, which
then "fixes" them.

**DEV-1.3** Project documents MUST reference this standard by version and
URL, not by relative path, and MUST NOT copy its content. A project-level
`docs/DEVELOPMENT_STANDARDS.md` MAY exist and then contains only additions
and deviations.
*Why:* v1.0 was copied into six projects and forked into six versions; the
relative path `../../shared/standards/` never existed in the workspace.

---

## 2. Language

**DEV-2.1** Code, identifiers, docstrings, comments, log messages,
documentation, commit messages, ADRs, specs, research notes, error codes,
JSON field names and catalog/MCP descriptions MUST be in English.
*Why:* agents search and parse English; one language removes duplicate
maintenance (ECO-005, ECO-023).

**DEV-2.2** Text shown to end users of applications and human-readable CLI
messages MUST be Polish by default and SHOULD be available in English
through the language switch defined in AGENT_INTERFACE §9.
*Why:* target user groups are in Poland; English output helps agents and
non-Polish collaborators.

**DEV-2.3** User-facing text MUST live in translation resources (for example
`locales/pl.toml`, `messages.py` dictionaries keyed by English IDs), not
inline in logic.
*Why:* keeps code English and lets the language switch work everywhere
(Retman `pl.toml` and Archiwista `messages.py` are the reference).

**DEV-2.4** Polish domain proper names (BDOT10k, PMAXTP, TERYT, NMT) MAY be
used as identifiers when they are the official name of a dataset or system.
Common words MUST be translated (`road_class`, not `klasa`).
*Why:* official names are what users and agents search for; translating
common words keeps the code readable for agents (Hydraulik `roads.py`
currently uses `klasa`, `przejezdny`, `uwagi`).

---

## 3. Git

**DEV-3.1** Branches: `main` (released state, default branch on GitHub),
`develop` (integration), `feature/<topic>`, `fix/<topic>`, `docs/<topic>`
from `develop`, `hotfix/<topic>` from `main`.
*Why:* one model for every repository (ECO-008).

**DEV-3.2** Releases MUST be annotated tags `vX.Y.Z` on `main`. Working
checkpoints are recorded in PROGRESS, not as tags.
*Why:* consumers pin tags (ECO-016).

**DEV-3.3** An agent MUST NOT merge into `main` or `develop`, push, create or
move tags, force-push or rewrite history without explicit approval of the
author in the current session.
*Why:* these operations are visible to consumers and hard to undo; current
practice in Kartograf and Archiwista.

**DEV-3.4** An agent working from another repository (including Nogat) MUST
work on a dedicated branch in the target repository, MUST follow the target's
`CLAUDE.md`, and MUST record what it changed in the target's PROGRESS and
CHANGELOG.
*Why:* cross-repo work is the purpose of the hub; the target repository stays
the authority over its own rules (Kartograf `CLAUDE.md` rule for agents from
other repositories).

**DEV-3.5** Work MUST be committed in the repository it belongs to. Long-lived
uncommitted work in worktrees SHOULD be avoided; an exception (such as the
Hydraulik proof of concept) MUST be stated in `CLAUDE.md`.
*Why:* uncommitted work blocks history rewrites, branch renames and other
cross-repo operations and is invisible to other agents.

---

## 4. Commits

**DEV-4.1** Messages MUST follow Conventional Commits:
`<type>(<scope>): <description>`, types `feat`, `fix`, `docs`, `test`,
`refactor`, `perf`, `style`, `build`, `ci`, `chore`. Breaking changes MUST
use `!` after the scope and a `BREAKING CHANGE:` footer.
*Why:* already used everywhere; machine-readable history enables CHANGELOG
checks.

**DEV-4.2** Author and committer MUST be `Daldek <git@debever.pl>`; each
repository MUST set `user.name` and `user.email` locally.
*Why:* ECO-006; repository-local configuration prevents agents committing
under their own identity.

**DEV-4.3** Messages MUST NOT contain `Co-Authored-By` trailers naming AI
tools, "Generated with ..." lines or other AI attribution. The gate (DEV-7.6)
MUST reject such commits.
*Why:* ECO-006; enforcement in the gate is the only reliable control because
agent defaults add these lines.

**DEV-4.4** One logical change per commit; documentation that describes a
change SHOULD be in the same commit as the change.
*Why:* review and revert by agents operate on commits.

---

## 5. Repository layout

**DEV-5.1** (`library`, `tool`, `assistant`, `pipeline`) Code MUST be in
`src/<package>/`. (`app`) Deployed applications MAY use another layout
documented in `CLAUDE.md`.
*Why:* ECO-011.

**DEV-5.2** Standard top level:

```
<repo>/
├── src/<package>/      # code, package data, py.typed
├── tests/
│   ├── unit/           # offline, fast
│   ├── integration/    # offline, several modules or a database
│   ├── contract/       # interface parity, generated-file drift, registry
│   ├── live/           # real network services (marker `live`)
│   ├── e2e/            # end-to-end UI or pipeline (optional)
│   ├── perf/           # benchmarks (optional)
│   └── fixtures/
├── docs/               # see DOCUMENTATION_STANDARDS
├── scripts/            # gate.sh and helpers
├── README.md  CLAUDE.md  AGENTS.md  llms.txt  LICENSE
├── pyproject.toml  uv.lock
├── .editorconfig  .gitattributes  .gitignore  .env.example
```

*Why:* agents locate tests, docs and gates without exploration; the `tests/`
split mirrors markers used by the gate (IMGWTools and Archiwista already
split this way).

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

**DEV-6.1** Python `>=3.12`. CI SHOULD also test the newest stable Python.
*Why:* common baseline today (Retman ADR-002, Kartograf); newest version
catches deprecations early.

**DEV-6.2** uv MUST manage environments and dependencies; the environment is
`.venv/` in the repository root; commands are run through `uv run` or
`.venv/bin/…`.
*Why:* ECO-012; one invocation pattern for agents.

**DEV-6.3** `uv.lock` MUST be committed. (`app`, `pipeline`) Deployment and
container builds MUST install with `uv sync --frozen`.
*Why:* reproducible environments; prevents the rebuild failures seen in
Hydrograf.

**DEV-6.4** (`library`, `tool`) Runtime dependencies MUST be ranges with a
lower bound; an upper bound only for a known incompatibility, with a comment
naming the reason.
*Why:* exact pins in a library make consumers unsolvable; reasons for caps
(`affine<3`, `sqlalchemy<2.1`) are otherwise forgotten.

**DEV-6.5** Optional features MUST be extras (`[mcp]`, `[api]`, `[raster]`,
`[viz]`, `[all]`); development tools MUST be a `dev` dependency group.
Missing extras MUST raise `missing_dependency` (ERROR_REGISTRY) naming the
install command.
*Why:* keeps base installs light for agents (MCP startup time) and makes the
fix self-explaining.

**DEV-6.6** Dependencies on other ecosystem projects MUST follow
RELEASE_AND_DISTRIBUTION §5.
*Why:* ECO-016.

---

## 7. Code quality

**DEV-7.1** Formatting: `ruff format`, line length 88, double quotes.
*Why:* ECO-009.

**DEV-7.2** Linting: `ruff check` with at least
`select = ["E", "F", "W", "I", "UP", "B", "SIM", "C4", "D"]` and
`pydocstyle.convention = "numpy"`; tests MAY ignore `D`.
*Why:* union of rules already used (IMGWTools, Archiwista); `D` enforces the
docstrings agents rely on.

**DEV-7.3** Type checking: mypy over `src/` and `tests/`. New projects
`strict = true`. Existing projects MAY keep a committed baseline of known
errors that MUST NOT grow, and SHOULD reach strict.
*Why:* ECO-010.

**DEV-7.4** (`library`, `tool`) The package MUST ship `py.typed` and declare
`Typing :: Typed`.
*Why:* typed public API is the most precise documentation an agent gets; an
agent writing consumer code gets errors before running it.

**DEV-7.5** Coverage MUST be at least 80% for the package; the threshold is
set in `[tool.coverage.report] fail_under`. Projects below MAY set their
current value and MUST NOT lower it.
*Why:* 80% is practised in six projects; a ratchet lets Kartograf (60%)
converge.

**DEV-7.6** Each repository MUST have `scripts/gate.sh` that runs, in order:
`ruff format --check`, `ruff check`, mypy, offline tests, contract tests
(generated files, error registry, interface parity) and commit-message checks
(DEV-4.3). It MUST work from a git worktree. A commit MUST NOT be made when
the gate fails.
*Why:* one command for agents to verify work; Kartograf's worktree-aware
`gate.sh` is the reference.

**DEV-7.7** CI (GitHub Actions) MUST run the gate on push and pull request to
`main` and `develop`. (`library`, `tool`, `assistant`) CI SHOULD run on Linux,
macOS and Windows.
*Why:* only Hydrograf has CI today; Retman and IMGWTools target Windows and
have had macOS/Windows-specific store bugs.

---

## 8. Naming

**DEV-8.1** Python naming: `snake_case` functions and variables, `PascalCase`
classes, `UPPER_SNAKE_CASE` constants, `_prefix` for internal names.

**DEV-8.2** Physical quantities MUST carry the unit in the name: `area_km2`,
`elevation_m`, `discharge_m3s`, `precipitation_mm`, `intensity_mm_h`,
`duration_min`, `timeout_s`, `slope_percent`, `slope_m_per_m`, `size_bytes`.
*Why:* removes unit ambiguity for people and agents; consistently practised
in every project.

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

*Why:* union of prefixes from Kartograf, IMGWTools, Archiwista and Retman; an
agent infers effects (network, writes) from the name.

**DEV-8.4** Interface option names MUST follow the shared vocabulary in
AGENT_INTERFACE §3.4.
*Why:* an agent that learned one tool can drive the next without lookup.

---

## 9. Docstrings and comments

**DEV-9.1** Every public module, class and function MUST have a NumPy-style
docstring in English with `Parameters`, `Returns`, `Raises` and, for public
API, an `Examples` section that runs as a doctest.
*Why:* NumPy style is already used in every project; examples are what
indexers (Context7) and agents extract.

**DEV-9.2** Units MUST be stated in docstrings in square brackets (`[km2]`).

**DEV-9.3** Comments explain why, not what. `TODO`, `FIXME`, `NOTE` tags MAY be
used; open questions belong in PROGRESS or an ADR, not in code.

---

## 10. Testing

**DEV-10.1** pytest with `--strict-markers`. Registered markers: `live`
(real network), `slow` (more than ~10 s or Docker), `db` (database), `perf`,
`e2e`. The default run and the gate MUST exclude `live`, `perf` and `e2e`.
*Why:* deterministic offline runs for agents; union of markers in use.

**DEV-10.2** Unit tests MUST NOT access the network; HTTP is mocked (for
example `respx`) or replaced by recorded fixtures.

**DEV-10.3** Live tests MUST be runnable on demand and SHOULD write a JSON
report of results.
*Why:* upstream services (IMGW, GUGiK, ČÚZK) change without notice; IMGWTools
`IMGW_LIVE_REPORT` is the reference.

**DEV-10.4** (`tool`) Contract tests MUST check: parity of option names across
library, CLI, MCP and REST; generated files (`AGENTS.md`, `llms.txt`,
`openapi.json`) equal generator output; error codes match
`error_registry.json`.
*Why:* AGENT_INTERFACE depends on these invariants; IMGWTools already has
parity and drift tests.

**DEV-10.5** Test names: `test_<unit>_<scenario>[_<expected>]`; tests
assert behaviour, not wording of messages.

---

## 11. Errors

**DEV-11.1** Each project MUST define one base exception
(`<Project>Error`) carrying `code` (from the shared registry), `message`,
`details` (JSON-compatible) and optional `hint`; subclasses select a default
code.
*Why:* ECO-015; Hydrolog and IMGWTools exceptions are the reference.

**DEV-11.2** Errors MUST be reported in every interface as defined in
[ERROR_REGISTRY.md](ERROR_REGISTRY.md).

**DEV-11.3** Validation MUST happen at system boundaries (CLI, MCP, REST,
public functions) and MUST name the offending option and allowed values.
*Why:* agents repair calls from `details`; silent coercion hides mistakes.

---

## 12. Logging

**DEV-12.1** Modules use `logging.getLogger(__name__)`; libraries MUST NOT
configure handlers or call `print`.

**DEV-12.2** CLI logs and progress go to stderr; level controlled by
`--verbose`/`--quiet` and `<TOOL>_LOG_LEVEL`.
*Why:* stdout is reserved for results (AGENT_INTERFACE §3).

**DEV-12.3** Use `%`-style arguments in log calls; never log secrets, tokens
or full credentials-bearing URLs.

---

## 13. Security

**DEV-13.1** Secrets only through environment variables or files outside the
repository; `.env` is git-ignored; `.env.example` lists every variable
without values.

**DEV-13.2** Every HTTP request MUST have a timeout; retries use bounded
exponential backoff.

**DEV-13.3** Inputs that become paths MUST be resolved and checked against
allowed roots; reject `..`, control characters and URL metacharacters in
identifiers.
*Why:* agents hallucinate paths and identifiers; MCP servers expose the file
system to them.

**DEV-13.4** SQL MUST use parameterised queries.

**DEV-13.5** Licences of dependencies MUST be compatible with the project
licence and the distribution channel; GPL dependencies MUST be documented in
`CLAUDE.md` and README.
*Why:* Hydraulik depends on GPL-3.0 `hydromt_sfincs`; whether that imposes
obligations on an MIT repository is not yet established (its `CLAUDE.md`
assumes it does and calls the repository private, while GitHub shows it
public on 2026-10-19). To be investigated in a separate session.

---

## 14. Files and encoding

**DEV-14.1** UTF-8, LF line endings, final newline, no trailing whitespace,
enforced by `.editorconfig` and `.gitattributes` (`* text=auto eol=lf`).
Byte-exact fixtures (golden CSV) MUST be marked `-text` in `.gitattributes`.
*Why:* Windows users and agents on different platforms; Kartograf
`docs/DECISIONS.md` is CRLF today and becomes LF.

**DEV-14.2** Indentation: 4 spaces for Python, 2 for JSON, YAML, TOML,
Markdown, JavaScript, CSS.

---

## 15. Frontend (profile `app`)

**DEV-15.1** JavaScript: ES modules, `camelCase`, `PascalCase` for classes and
components, 2-space indent, 100-column lines, JSDoc for exported functions.
No build step is required; vendored libraries keep their licence files.
*Why:* Hydrograf (vanilla JS) and Archiwista (Preact + htm) already work this
way.

**DEV-15.2** UI text in Polish through translation resources (DEV-2.3);
`data-*` attributes and CSS classes in English.

---

## 16. Licence and contributions

**DEV-16.1** Licence: MIT unless an ADR states otherwise.

**DEV-16.2** Public repositories MUST have `CONTRIBUTING.md`, `docs/CLA.md`
and `CONTRIBUTORS.md`, in the form used by IMGWTools, Hydraulik and
Archiwista.

**DEV-16.3** Publicly cited projects SHOULD include `CITATION.cff`.
*Why:* hydrology users are often researchers; GitHub renders citation data
and Zenodo uses it for DOIs.

---

## 17. Working with agents (developers)

**DEV-17.1** Session start: read `CLAUDE.md`, `docs/PROGRESS.md`, run
`git status` and `git log --oneline -10`, confirm the branch.

**DEV-17.2** During a session: small commits after a passing gate; CHANGELOG
updated with user-visible changes; decisions with alternatives recorded as
ADRs.

**DEV-17.3** Session end: `docs/PROGRESS.md` MUST be updated (DOCUMENTATION
§6) before the last commit.
*Why:* the next agent starts from PROGRESS; practised in every project.

**DEV-17.4** Specs and plans for non-trivial changes MUST be written before
code and reviewed by the author (`docs/specs/`, `docs/plans/`).
*Why:* current practice in Kartograf, Retman, Archiwista and Hydraulik;
prevents agents from building the wrong thing at scale.

**DEV-17.5** An agent MUST NOT change another project to suit its own project.
It records the need as a requirement for the other project in Nogat or in
that project's backlog.
*Why:* Retman's rule "tools know nothing about Retman" generalised; keeps
each project's scope intact.
