# Ecosystem standard decisions

Decision log for the shared standard v2.0. Each entry records what was
decided, why, and which alternatives were rejected. Requirements that follow
from a decision live in the topic documents; this file explains the reasons.

Status values: `accepted`, `proposed` (awaiting the author), `superseded`.

| ID | Title | Status | Date |
|---|---|---|---|
| [ECO-001](#eco-001-nogat-is-the-ecosystem-hub) | Nogat is the ecosystem hub | accepted | 2026-10-19 |
| [ECO-002](#eco-002-machine-readable-registry-ecosystemyaml) | Machine-readable registry `ecosystem.yaml` | accepted | 2026-10-19 |
| [ECO-003](#eco-003-scope-eight-projects-basichydraulic-excluded) | Scope: eight projects, BasicHydraulic excluded | accepted | 2026-10-19 |
| [ECO-004](#eco-004-standard-v20-is-rewritten-from-practice) | Standard v2.0 is rewritten from practice | accepted | 2026-10-19 |
| [ECO-005](#eco-005-english-everywhere-polish-only-in-the-end-user-interface) | English everywhere, Polish only in the end-user interface | accepted | 2026-10-19 |
| [ECO-006](#eco-006-single-author-identity-no-ai-attribution) | Single author identity, no AI attribution | accepted | 2026-10-19 |
| [ECO-007](#eco-007-one-off-history-rewrite) | One-off history rewrite | accepted | 2026-10-19 |
| [ECO-008](#eco-008-main-and-develop-in-every-repository) | `main` and `develop` in every repository | accepted | 2026-10-19 |
| [ECO-009](#eco-009-ruff-for-formatting-and-linting) | Ruff for formatting and linting | accepted | 2026-10-19 |
| [ECO-010](#eco-010-mypy-as-the-only-type-checker) | mypy as the only type checker | accepted | 2026-10-19 |
| [ECO-011](#eco-011-src-layout) | `src` layout | accepted | 2026-10-19 |
| [ECO-012](#eco-012-uv-and-lock-files) | uv and lock files | accepted | 2026-10-19 |
| [ECO-013](#eco-013-progress-holds-current-state-history-is-archived) | PROGRESS holds current state, history is archived | accepted | 2026-10-19 |
| [ECO-014](#eco-014-claudemd-for-developers-agentsmd-for-users) | CLAUDE.md for developers, AGENTS.md for users | accepted | 2026-10-19 |
| [ECO-015](#eco-015-shared-error-registry) | Shared error registry | accepted | 2026-10-19 |
| [ECO-016](#eco-016-ecosystem-dependencies-pinned-to-released-versions) | Ecosystem dependencies pinned to released versions | accepted | 2026-10-19 |
| [ECO-017](#eco-017-agent-first-design) | Agent-first design | accepted | 2026-10-19 |
| [ECO-018](#eco-018-mcp-tool-names-carry-a-project-prefix) | MCP tool names carry a project prefix | accepted | 2026-10-19 |
| [ECO-019](#eco-019-cli-errors-go-to-the-last-line-of-stderr) | CLI errors go to the last line of stderr | accepted | 2026-10-19 |
| [ECO-020](#eco-020-breaking-changes-are-acceptable-during-adoption) | Breaking changes are acceptable during adoption | accepted | 2026-10-19 |
| [ECO-021](#eco-021-publish-to-pypi-then-conda-forge) | Publish to PyPI, then conda-forge | accepted | 2026-10-19 |
| [ECO-022](#eco-022-common-distribution-name-pattern) | Common distribution name pattern | preferred: `nogat-` | 2026-10-19 |
| [ECO-023](#eco-023-commit-messages-in-english) | Commit messages in English | accepted | 2026-10-19 |

---

## ECO-001 Nogat is the ecosystem hub

**Decision.** Nogat describes every project of the ecosystem, their
dependencies and shared rules, and is the place from which an agent
coordinates work across repositories. It keeps its original role of
collecting scripts and third-party tools for meteorology, hydrology,
oceanography and hydraulics.

**Why.** The number of projects and cross-project contracts (Kartograf
store read by Archiwista, Hydrolog consumed by Hydrograf and Hydraulik,
Retman adapters over every tool) outgrew per-project documentation.
Hydrograf `docs/CROSS_PROJECT_ANALYSIS.md` already tried to hold this map
from the point of view of one consumer.

**Rejected.** A dedicated new repository (one more repo to maintain);
keeping the map in Hydrograf (biased to one consumer).

## ECO-002 Machine-readable registry `ecosystem.yaml`

**Decision.** The registry of projects is a YAML file in Nogat. Human-readable
overviews are generated from it.

**Why.** Version drift between consumers (Hydrograf pinned Kartograf 0.7.0,
Hydraulik 0.7.2, Retman a commit SHA) is only detectable automatically when
pins are data. YAML is readable by people and agents alike.

**Rejected.** Markdown-only registry (no automatic drift checks).

## ECO-003 Scope: eight projects, BasicHydraulic excluded

**Decision.** The standard covers Kartograf, Hydrolog, IMGWTools, Hydrograf,
Hydraulik, Retman, Archiwista and Nogat. BasicHydraulic is out of scope at
this stage.

**Why.** Archiwista already depends on Kartograf and IMGWTools stores.
BasicHydraulic has no active development.

## ECO-004 Standard v2.0 is rewritten from practice

**Decision.** v1.0 (2026-01-29) is archived in `legacy/v1.0/`. v2.0 is
written from what the projects actually do, plus the agent-first
requirements.

**Why.** Six projects forked v1.0 into their own standards (Kartograf v3.5,
Hydrograf v2.1, IMGWTools v1.3, Hydrolog v1.1, Retman v1.0, Archiwista v1.0)
and moved beyond it. v1.0 also contains defects: a non-existent build backend
`setuptools.backends._legacy:_Backend` (absent in setuptools 84.0.0),
contradictory CHANGELOG locations, `fail_under = 60` versus the 80% rule,
`mypy src/` with a mandatory flat layout, an agent-in-Docker workflow nobody
uses, a PR review process that does not match single-author work, and links
to a `shared/standards/` path that does not exist in the workspace.

## ECO-005 English everywhere, Polish only in the end-user interface

**Decision.** Code, identifiers, docstrings, comments, all documentation
(README, CLAUDE.md, AGENTS.md, llms.txt, PRD, SCOPE, ARCHITECTURE, ADRs,
PROGRESS, CHANGELOG, research notes, specs), MCP and catalog descriptions,
error codes and machine fields are in English. There is no Polish README.
Polish remains only in the end-user interface of applications (web UI of
Hydrograf and Archiwista, Retman conversation, human-readable CLI messages),
because target user groups are in Poland. English user-interface text is
available as an option wherever a language switch exists.

**Why.**
- AI agents search, rank and parse documentation in English. Indexers
  exclude non-English content by default (Context7 skips `i18n/pl*`).
- Multilingual tool-calling research shows models pick the right tool in any
  language but generate parameter values worse outside English
  (https://arxiv.org/abs/2601.05366).
- One language removes duplicated maintenance (no README.pl.md).
- The audience of the applications is Polish, so their interface stays
  Polish.

**Rejected.** Polish internal documentation with an English README (two
languages to maintain, internal docs invisible to agents); bilingual README.

**Consequence.** Existing Polish documentation is translated during adoption.

## ECO-006 Single author identity, no AI attribution

**Decision.** Every commit has author and committer `Daldek <git@debever.pl>`.
Commit messages contain no `Co-Authored-By` trailers for AI tools and no
"Generated with ..." lines. Applies to commits made by agents.

**Why.** The author decided this for Kartograf on 2026-10-09; Retman and
Archiwista already follow it. Hydrolog, IMGWTools, Hydrograf and Hydraulik
still record `Claude <agent@local>` as author and AI trailers. Five email
variants of the same person fragment `git shortlog` and GitHub contribution
data.

## ECO-007 One-off history rewrite

**Decision.** History of Kartograf, Hydrolog, IMGWTools, Hydrograf and
Hydraulik is rewritten once: author/committer `Claude <agent@local>` and
every Daldek email variant become `Daldek <git@debever.pl>`, AI
`Co-authored-by` trailers and "Generated with Claude Code" lines are removed.
The third-party contributor in IMGWTools keeps their identity.

**Why.** ECO-006 applied to history. A dry run on mirror copies
(2026-10-19, `git-filter-repo` a40bce548d2c) removed all AI trailers and
`agent@local` identities with unchanged commit counts and identical trees
for every branch and tag.

**Consequences.** All commit hashes change; force-push of branches and tags;
SHA pins and SHA references in documentation must be remapped; GitHub keeps
old commits reachable through IMGWTools pull request #1; five
GitHub-signed commits lose their signature. Procedure: `ADOPTION_PLAN.md`.

## ECO-008 `main` and `develop` in every repository

**Decision.** `main` (released state, default branch on GitHub) and `develop`
(integration) in every repository. IMGWTools renames `master`/`slave`;
Nogat gains `develop`; Hydraulik makes `main` its default branch.

**Why.** Six of eight repositories already use it. One convention lets an
orchestrating agent operate without per-repo branch tables. Links in
generated `llms.txt` point at branch names, and IMGWTools currently links to
`master`.

## ECO-009 Ruff for formatting and linting

**Decision.** `ruff format` and `ruff check` everywhere. Hydrolog moves from
Black and flake8.

**Why.** Seven of eight Python projects use ruff. `ruff format` is
Black-compatible, so the code diff is small. One tool replaces formatter,
linter, isort and pydocstyle.

## ECO-010 mypy as the only type checker

**Decision.** mypy everywhere; IMGWTools moves from pyright; Hydraulik adds
it. New code targets `strict`; existing projects may keep a recorded
baseline that only shrinks.

**Why.** Five projects already use mypy. One checker means one
configuration vocabulary and one baseline mechanism for agents. Strictness
today ranges from `strict = true` (Archiwista) to a baseline without strict
(Kartograf); a ratchet allows convergence without blocking work.

## ECO-011 `src` layout

**Decision.** Every distributable Python package uses `src/<package>/`.
Kartograf, Hydrolog, Retman and Archiwista migrate. Exempt: Hydrograf
`backend/` (deployed application, not a distributed package) and Nogat.

**Why.**
- Recommended by PyPA
  (https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/):
  tests run against the installed package, not the working directory.
- The projects are installed by each other from git and later from PyPI, and
  they ship non-Python data that a flat layout silently hides when missing
  from the wheel: Hydrolog agent-guide templates (`.md`), Retman `.toml` and
  `.jsonl`, Archiwista web assets (`.css`, `.js`, `.pbf`).
- Agents often check `python -c "import pkg"` from the repository root. In a
  flat layout that succeeds even when the environment is broken; in `src`
  layout it fails loudly.
- `src/` marks unambiguously where the code is.

**Cost.** `git mv` and path updates in pyproject, ruff, coverage, mypy and
documentation. Import paths do not change.

## ECO-012 uv and lock files

**Decision.** uv is the package and environment manager. Libraries declare
version ranges in `pyproject.toml` and commit `uv.lock` for reproducible
development. Applications commit `uv.lock` and deploy from it
(`uv sync --frozen`).

**Why.** A lock file records exact versions and hashes of every direct and
transitive dependency. Hydrograf broke twice on unlocked rebuilds
(`sqlalchemy` 2.1 switching driver, `affine` 3.x breaking numba). Libraries
must not force exact versions on consumers, so they publish ranges. uv
produces a cross-platform lock, manages the Python version and is already
used by Retman. Archiwista's `requirements.lock` with hashes is replaced by
`uv.lock`.

## ECO-013 PROGRESS holds current state, history is archived

**Decision.** `docs/PROGRESS.md` holds current status, the last session and
next steps (target 300 lines or less). Older sessions move to
`docs/progress/YYYY-MM.md`.

**Why.** Append-only PROGRESS files reached 3,637 lines (Kartograf) and
145 KB (Hydrograf). Agents read PROGRESS at every session start, so its size
is paid every time and older entries crowd out current state. History stays
available by month.

## ECO-014 CLAUDE.md for developers, AGENTS.md for users

**Decision.** `CLAUDE.md` instructs agents that develop the repository.
`AGENTS.md` and `llms.txt` instruct agents that use the tool, are generated
from the command catalog and are never edited by hand.

**Why.** Kartograf forbade AGENTS.md while Hydrolog and IMGWTools generate it.
The two audiences need different content. Claude Code reads AGENTS.md only
when CLAUDE.md is absent, while Codex, Cursor, Copilot and others read
AGENTS.md (https://agents.md/), so AGENTS.md must end with a pointer to
CLAUDE.md for agents that develop the repository.

## ECO-015 Shared error registry

**Decision.** One registry of error codes, exit codes and HTTP statuses for
every project: `error_registry.json` with `ERROR_REGISTRY.md`.

**Why.** Kartograf, Hydrolog and IMGWTools each built a registry with the same
idea and conflicting numbers: exit 4 means `conflict` in IMGWTools and
`calculation_error` in Hydrolog; exit 8 means `store_unavailable` and
`forbidden`; exit 1 mixes domain failures with internal errors in Kartograf.
Agents and Retman that chain tools cannot interpret an exit code without
knowing which tool emitted it.

## ECO-016 Ecosystem dependencies pinned to released versions

**Decision.** A project depends on another ecosystem project only through a
released version: a tag now, a PyPI version once published. Commit-SHA pins
and editable sibling installs are temporary and recorded in `ecosystem.yaml`.

**Why.** Tags (Hydrograf, Hydraulik) survived the 2026-10-08 Hydrograf history
rewrite; SHA pins (Retman) and branch-based editable installs (Archiwista)
break on every rewrite or rebase and hide which release a consumer supports.

## ECO-017 Agent-first design

**Decision.** Projects are designed so that AI agents discover, understand and
prefer the tools when they fit the task. README, library, CLI, MCP, REST,
`llms.txt` and `AGENTS.md` follow `AGENT_INTERFACE.md` and
`DOCUMENTATION_STANDARDS.md`.

**Why.** Agents are the primary operators of these tools. Agents choose tools
by precise scope, names, descriptions, schemas and recoverable errors. They
penalise slogans: MCP guidance discourages "best server" claims in
instructions, and Context7 rejects promotional descriptions. Measured
evidence:
- Context files on average do not raise success and cost more than 20% extra
  (https://arxiv.org/abs/2602.11988).
- A docs index in AGENTS.md beat skills on APIs outside training data
  (https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals).

Niche tools such as these benefit, but only from lean, precise context.

## ECO-018 MCP tool names carry a project prefix

**Decision.** Every MCP tool name starts with the project prefix
(`kartograf_`, `imgw_`, `hydrolog_`, ...).

**Why.** Retman and agents load several servers at once. Generic names such
as `get_catalog` or `store_entries` collide, and `serverInfo.name` is not
guaranteed unique. Namespacing improves tool selection
(https://www.anthropic.com/engineering/writing-tools-for-agents).

## ECO-019 CLI errors go to the last line of stderr

**Decision.** On failure the CLI writes the error document as the last line of
stderr. stdout carries only the result document.

**Why.** IMGWTools already does this; the CLI specification for agents
recommends it (https://clispec.dev/); stdout then always parses as the result
type. Kartograf currently emits `kartograf-error/1` on stdout and changes.

## ECO-020 Breaking changes are acceptable during adoption

**Decision.** Adopting v2.0 may break public interfaces (error codes, envelope
fields, MCP tool names, CLI channels). Breaking changes are recorded in
CHANGELOG with migration notes; no compatibility shims.

**Why.** All projects are pre-1.0 or in early major versions and the known
consumers are in this ecosystem. Converging now costs less than carrying
aliases.

## ECO-021 Publish to PyPI, then conda-forge

**Decision.** Every distributable package is published to PyPI. conda-forge
follows for packages with a geospatial native stack. Further channels are
listed in `RELEASE_AND_DISTRIBUTION.md`.

**Why.** PyPI enables one-line installs (`uvx`, `pip`) and is required for the
official MCP Registry, which hosts metadata only and points at a public
package (https://modelcontextprotocol.io/registry/about). conda-forge
resolves GDAL/PROJ/rasterio binaries that pip users struggle with on Windows,
which matters for Kartograf, Hydraulik and Hydrograf users.

## ECO-022 Common distribution name pattern

**Status: preferred, not final.** The author prefers option A (`nogat-`) on
2026-10-19 and will confirm it before the first PyPI release or name
reservation. Until then, documents use `nogat-<name>` as the working
assumption.

The author wants one prefix or suffix shared by all distributed packages
instead of a one-off fix for Kartograf.

**Facts (checked 2026-10-19).**
- `kartograf` is taken on PyPI (1.0.2) and conda-forge (2.0.0) by
  OpenFreeEnergy, a package for mapping atoms between molecules
  (https://github.com/OpenFreeEnergy/kartograf). It installs the import
  package `kartograf`.
- `imgwtools` on PyPI (2.1.1) belongs to this ecosystem.
- All seven names are free on PyPI and conda-forge under each candidate
  pattern: `nogat-<name>`, `daldek-<name>`, `<name>-pl`, `py<name>`.

**What the pattern applies to.** Distribution names on PyPI and conda-forge
only. Repository names, CLI commands (`kartograf`, `imgw`, `hydrolog`), MCP
server and tool names and import names stay as they are, unless option E is
chosen.

**Options.**

| | Pattern | Example | For | Against |
|---|---|---|---|---|
| A | brand prefix `nogat-` | `nogat-kartograf`, `nogat-hydrolog`, `nogat-imgwtools` | Names the ecosystem; PyPI search "nogat" lists the whole family; matches the hub | `imgwtools` moves to a new name; the name of the hub repository becomes the brand |
| B | country suffix `-pl` | `kartograf-pl` | Signals the Polish focus | Misleading: Kartograf and IMGWTools already cover Czechia, Slovakia is planned |
| C | author prefix `daldek-` | `daldek-kartograf` | Clear ownership | Personal handle, not a family name; says nothing about the domain |
| D | `py` prefix | `pykartograf` | Common Python habit | Generic; does not group the family |
| E | A plus namespace package | `nogat-kartograf`, `import nogat.kartograf` | Removes the import clash with OpenFreeEnergy `kartograf` | Every import in every consumer changes; longer imports in agent-written code |

**Recommendation and author's preference.** A. The import clash with OpenFreeEnergy `kartograf`
requires both packages in one environment, which is unlikely across chemistry
and GIS; the README "When not to use" section names the other package to
prevent agent confusion. The published `imgwtools` gets a final release whose
README points to `nogat-imgwtools`; no code shim (ECO-020).

## ECO-023 Commit messages in English

**Decision.** Commit messages are in English, including the description.

**Why.** ECO-005: only the end-user interface stays Polish. Commit history is
internal documentation that agents read (`git log` at session start,
CHANGELOG preparation).

**Rejected.** Polish descriptions with English type and scope (current
practice in Kartograf, Retman and Archiwista).

**Consequence.** Existing commit messages are not translated; the history
rewrite (ECO-007) changes only identities and AI attribution.
