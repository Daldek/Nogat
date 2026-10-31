# Ecosystem standard decisions

Decision log for the shared standard (2.x). Each entry records what was
decided, why, and which alternatives were rejected. Requirements that follow
from a decision live in the topic documents; this file explains the reasons.
Entries changed by a later decision carry an "Amended by" line.

Status values: `accepted`, `amended` (still valid, changed by a later entry),
`superseded`.

| ID | Title | Status | Date |
|---|---|---|---|
| [ECO-001](#eco-001-nogat-is-the-ecosystem-hub) | Nogat is the ecosystem hub | amended by ECO-036 | 2026-10-19 |
| [ECO-002](#eco-002-machine-readable-registry-ecosystemyaml) | Machine-readable registry `ecosystem.yaml` | amended by ECO-034 | 2026-10-19 |
| [ECO-003](#eco-003-scope-eight-projects-basichydraulic-excluded) | Scope: eight projects, BasicHydraulic excluded | accepted | 2026-10-19 |
| [ECO-004](#eco-004-standard-v20-is-rewritten-from-practice) | Standard v2.0 is rewritten from practice | accepted | 2026-10-19 |
| [ECO-005](#eco-005-english-everywhere-polish-only-in-the-end-user-interface) | English everywhere, Polish only in the end-user interface | accepted | 2026-10-19 |
| [ECO-006](#eco-006-single-author-identity-no-ai-attribution) | Single author identity, no AI attribution | amended by ECO-038 | 2026-10-19 |
| [ECO-007](#eco-007-one-off-history-rewrite) | One-off history rewrite | accepted | 2026-10-19 |
| [ECO-008](#eco-008-main-and-develop-in-every-repository) | `main` and `develop` in every repository | accepted | 2026-10-19 |
| [ECO-009](#eco-009-ruff-for-formatting-and-linting) | Ruff for formatting and linting | accepted | 2026-10-19 |
| [ECO-010](#eco-010-mypy-as-the-only-type-checker) | mypy as the only type checker | amended by ECO-033 | 2026-10-19 |
| [ECO-011](#eco-011-src-layout) | `src` layout | amended by ECO-036 | 2026-10-19 |
| [ECO-012](#eco-012-uv-and-lock-files) | uv and lock files | amended by ECO-037 | 2026-10-19 |
| [ECO-013](#eco-013-progress-holds-current-state-history-is-archived) | PROGRESS holds current state, history is archived | amended by ECO-039 | 2026-10-19 |
| [ECO-014](#eco-014-claudemd-for-developers-agentsmd-for-users) | CLAUDE.md for developers, AGENTS.md for users | accepted | 2026-10-19 |
| [ECO-015](#eco-015-shared-error-registry) | Shared error registry | accepted | 2026-10-19 |
| [ECO-016](#eco-016-ecosystem-dependencies-pinned-to-released-versions) | Ecosystem dependencies pinned to released versions | amended by ECO-034 | 2026-10-19 |
| [ECO-017](#eco-017-agent-first-design) | Agent-first design | accepted | 2026-10-19 |
| [ECO-018](#eco-018-mcp-tool-names-carry-a-project-prefix) | MCP tool names carry a project prefix | accepted | 2026-10-19 |
| [ECO-019](#eco-019-cli-errors-go-to-the-last-line-of-stderr) | CLI errors go to the last line of stderr | accepted | 2026-10-19 |
| [ECO-020](#eco-020-breaking-changes-are-acceptable-during-adoption) | Breaking changes are acceptable during adoption | accepted | 2026-10-19 |
| [ECO-021](#eco-021-publish-to-pypi-then-conda-forge) | Publish to PyPI, then conda-forge | amended by ECO-035 | 2026-10-19 |
| [ECO-022](#eco-022-common-distribution-name-pattern) | Common distribution name pattern | accepted: `nogat-` | 2026-10-20 |
| [ECO-023](#eco-023-commit-messages-in-english) | Commit messages in English | accepted | 2026-10-19 |
| [ECO-024](#eco-024-registry-records-exchanged-data) | Registry records exchanged data | amended by ECO-034 | 2026-10-20 |
| [ECO-025](#eco-025-coordinated-releases-form-a-verified-release-set) | Coordinated releases form a verified release set | amended by ECO-035, ECO-037 | 2026-10-20 |
| [ECO-026](#eco-026-nogat-is-the-users-installable-environment) | Nogat is the users' installable environment | amended by ECO-037 | 2026-10-20 |
| [ECO-027](#eco-027-nogat-drops-its-legacy-script-collection) | Nogat drops its legacy script collection | accepted | 2026-10-20 |
| [ECO-028](#eco-028-one-user-environment-for-all-tools) | One user environment for all tools | amended by ECO-033 | 2026-10-20 |
| [ECO-029](#eco-029-automated-dependency-updates-and-audit) | Automated dependency updates and audit | amended by ECO-040 | 2026-10-20 |
| [ECO-030](#eco-030-protected-branches-require-green-ci-only) | Protected branches require green CI only | amended by ECO-037 | 2026-10-20 |
| [ECO-031](#eco-031-external-contributors-keep-their-identity) | External contributors keep their identity | amended by ECO-038 | 2026-10-20 |
| [ECO-032](#eco-032-small-explicit-support-policy) | Small, explicit support policy | superseded by ECO-035 | 2026-10-20 |
| [ECO-033](#eco-033-zen-of-nogat-and-one-way-to-write-a-rule) | Zen of Nogat and one way to write a rule | amended by ECO-046 | 2026-10-20 |
| [ECO-034](#eco-034-the-registry-holds-structure-only) | The registry holds structure only | accepted | 2026-10-20 |
| [ECO-035](#eco-035-minimal-support-and-three-channels) | Minimal support and three channels | accepted | 2026-10-20 |
| [ECO-036](#eco-036-three-profiles-tool-app-hub) | Three profiles: tool, app, hub | accepted | 2026-10-20 |
| [ECO-037](#eco-037-one-release-path) | One release path | accepted | 2026-10-20 |
| [ECO-038](#eco-038-commits-are-checked-once-on-entry-to-develop) | Commits are checked once, on entry to develop | amended by ECO-049 | 2026-10-20 |
| [ECO-039](#eco-039-one-planning-document-one-request-list-short-progress) | One planning document, one request list, short PROGRESS | amended by ECO-043 | 2026-10-20 |
| [ECO-040](#eco-040-dependabot-for-actions-audit-informs) | Dependabot for actions, audit informs | accepted | 2026-10-20 |
| [ECO-041](#eco-041-hydraulik-stays-mit-sfincs-is-not-distributed) | Hydraulik stays MIT; SFINCS is not distributed | accepted | 2026-10-20 |
| [ECO-042](#eco-042-agent-facing-text-follows-the-channel) | Agent-facing text follows the channel | accepted | 2026-10-21 |
| [ECO-043](#eco-043-needs-between-projects-are-github-issues) | Needs between projects are GitHub issues | accepted | 2026-10-21 |
| [ECO-044](#eco-044-nogats-tooling-reports-errors-by-the-registry) | Nogat's tooling reports errors by the registry | accepted | 2026-10-21 |
| [ECO-045](#eco-045-precedence-of-conflicting-requirements) | Precedence of conflicting requirements | accepted | 2026-10-21 |
| [ECO-046](#eco-046-the-standard-is-tagged-when-published) | The standard is tagged when published | accepted | 2026-10-21 |
| [ECO-047](#eco-047-plan-approval-is-a-line-in-the-plan) | Plan approval is a line in the plan | accepted | 2026-10-21 |
| [ECO-048](#eco-048-nogats-agentsmd-routes-and-links) | Nogat's AGENTS.md routes and links | accepted | 2026-10-21 |
| [ECO-049](#eco-049-hotfix-commits-are-checked-on-entry-to-main) | Hotfix commits are checked on entry to main | accepted | 2026-10-21 |
| [ECO-050](#eco-050-agent-documents-have-canonical-schemas-in-nogat) | Agent documents have canonical schemas in Nogat | accepted | 2026-10-21 |
| [ECO-051](#eco-051-one-data-output-convention) | One data-output convention | accepted | 2026-10-24 |
| [ECO-052](#eco-052-the-routing-table-is-registry-data) | The routing table is registry data | accepted | 2026-10-25 |
| [ECO-053](#eco-053-development-versions-of-a-pinned-producer-and-tests-in-a-wheel) | Development versions of a pinned producer, and tests in a wheel | accepted | 2026-10-25 |
| [ECO-054](#eco-054-projects-belong-to-archiwista) | Projects belong to Archiwista | accepted | 2026-10-31 |

---

## ECO-001 Nogat is the ecosystem hub

**Amended by ECO-036 (2026-10-20):** third-party tool entries are removed from the registry.

**Decision.** Nogat describes every project of the ecosystem, their
dependencies and shared rules, and is the place from which an agent
coordinates work across repositories. It keeps its original role of
collecting third-party tools for meteorology, hydrology, oceanography and
hydraulics, as registry entries; its own script collection was removed
(ECO-027).

**Why.** The number of projects and cross-project contracts (Kartograf
store read by Archiwista, Hydrolog consumed by Hydrograf and Hydraulik,
Retman adapters over every tool) outgrew per-project documentation.
Hydrograf `docs/CROSS_PROJECT_ANALYSIS.md` already tried to hold this map
from the point of view of one consumer.

**Rejected.** A dedicated new repository (one more repo to maintain);
keeping the map in Hydrograf (biased to one consumer).

## ECO-002 Machine-readable registry `ecosystem.yaml`

**Amended by ECO-034 (2026-10-20):** the registry records structure, not versions or pins.

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

**Amended by ECO-038 (2026-10-20):** the author identity is checked, not the committer;
merge commits created by GitHub are exempt.

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

**Amended by ECO-033 (2026-10-20):** there is no shrinking baseline; mypy shortfalls use
per-module overrides listed as deviations.

**Decision.** mypy everywhere; IMGWTools moves from pyright; Hydraulik adds
it. New code targets `strict`; existing projects may keep a recorded
baseline that only shrinks.

**Why.** Five projects already use mypy. One checker means one
configuration vocabulary and one baseline mechanism for agents. Strictness
today ranges from `strict = true` (Archiwista) to a baseline without strict
(Kartograf); a ratchet allows convergence without blocking work.

## ECO-011 `src` layout

**Amended by ECO-036 (2026-10-20):** Nogat uses `src/nogat/` once it ships the `nogat`
package; Hydrograf `backend/` stays exempt.

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

**Amended by ECO-037 (2026-10-20):** installs use `uv sync --locked` everywhere.

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

**Amended by ECO-039 (2026-10-20):** history is git log and CHANGELOG; there is no monthly
archive.

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

**Amended by ECO-034 (2026-10-20):** pins are read from the repositories, not recorded in
`ecosystem.yaml`.

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

**Amended by ECO-035 (2026-10-20):** conda-forge and other channels are deferred until a
user asks.

**Decision.** Every distributable package is published to PyPI. conda-forge
follows for packages with a geospatial native stack. Further channels are
listed in `RELEASE_AND_DISTRIBUTION.md`.

**Why.** PyPI enables one-line installs (`uvx`, `pip`) and is required for the
official MCP Registry, which hosts metadata only and points at a public
package (https://modelcontextprotocol.io/registry/about). conda-forge
resolves GDAL/PROJ/rasterio binaries that pip users struggle with on Windows,
which matters for Kartograf, Hydraulik and Hydrograf users.

## ECO-022 Common distribution name pattern

**Status: accepted 2026-10-20.** The author confirmed option A (`nogat-`)
after preferring it on 2026-10-19. The user package itself is `nogat`
(ECO-026).

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

## ECO-024 Registry records exchanged data

**Amended by ECO-034 (2026-10-20):** structure only; no versions, pins or release sets.

**Decision.** `ecosystem.yaml` records, besides dependencies, what each
project provides (`provides`), how a consumer reaches it (`via`) and which
provided ids cross each dependency (`exchange`), planned dependencies
(`status: planned`) and external data sources (HUB-2.5 to HUB-2.7).
`docs/ECOSYSTEM_MAP.md` is generated from it (HUB-4.5).

**Why.** The author asked for a map of which information the tools exchange
and how they depend on each other. Format stability is the real contract:
Archiwista reads Kartograf sidecars and manifests, Retman reads both tools'
catalogs and envelopes, Hydrolog reads files exported by IMGWTools and
Kartograf without importing them. A dependency list without formats hides
these consumers.

**Rejected.** A hand-written Markdown map (ECO-002: drifts from the registry);
a separate contracts file (two sources for one graph).

## ECO-025 Coordinated releases form a verified release set

**Amended by ECO-035 (2026-10-20):** the set is verified on Python 3.12 and on the
newest stable Python that CI runs (REL-7.1), not on one version.

**Amended by ECO-037 (2026-10-20):** the published set is the `nogat` repository at its
tag; candidates are verified by a Nogat CI workflow.

**Decision.** The coordinated releases of the ecosystem tools are pinned in
Nogat as a release set: every project at a tag and every third-party package
at one version, for one Python version, verified by running each project's
tests in that environment (REL §6). Projects lock against the set's
constraints.

**Why.** The author wants the next coordinated releases kept as a tested
configuration with the same external package versions everywhere. On
2026-10-20 the declared ranges did not conflict (`scripts/ecosystem.py deps`),
but the environments did: 59 packages at different versions, Python 3.12 and
3.13 mixed, and only Retman and Archiwista had lock files. Divergence comes
from resolving each project at a different time, so ranges alone do not
prevent it; a shared lock does.

**Rejected.** Exact pins in every `pyproject.toml` (breaks library users and
REL-5.2); one shared environment for development only (does not give a
released, verified configuration); harmonising lower bounds without a lock
(still resolves to different versions over time).

## ECO-026 Nogat is the users' installable environment

**Amended by ECO-037 (2026-10-20):** until every member is on PyPI, `nogat` is installed
from its git tag; uv is the only documented installer.

**Decision.** Besides maintaining the ecosystem (standards, registry, map of
dependencies), Nogat is a package. `uv tool install nogat` installs every
tool and all their Python dependencies, at the versions of one verified
release set, as one uniform working environment. Each Nogat release is a
release set; Nogat versions follow SemVer. Docker, SFINCS, PostGIS and similar
system components are not installed but checked (HUB §7).

**Why.** The author wants Nogat to be the single working environment for
users, with all dependencies handled by one command. Installing the tools
separately leads to the version spread measured on 2026-10-20 (ECO-025).

**Rejected.** Nogat as a maintenance tool only (users would assemble the
environment themselves); CalVer named after the month of a set (the author
chose SemVer, which also tells users whether an upgrade may break their
scripts).

**Consequence.** The package pins exact versions, so it is installed in its
own environment.

## ECO-027 Nogat drops its legacy script collection

**Decision.** The R plotting script and its renv environment, the RStudio
project, the Copernicus Marine download scripts, the sample NetCDF and CSV
files and the old `requirements.txt` are removed from Nogat. Third-party
tools stayed as registry entries until 2.1 removed them (ECO-036).

**Why.** The author decided to drop R, data files and other legacy content.
None of it met the tool standard (R cannot ship in the Python package, the
scripts had no catalog or `--json`, sample data does not belong in a
package), and nothing in the ecosystem used it.

**Rejected.** Turning the Copernicus scripts into `nogat marine` commands;
keeping them as an unpackaged collection.

**Consequence.** The files remain in git history before 2026-10-20.

## ECO-028 One user environment for all tools

**Amended by ECO-033 (2026-10-20):** credentials come from environment variables only; there
is no keyring.

**Decision.** All tools read shared settings from `nogat.toml` and `NOGAT_*`
variables, keep stores under one data directory and caches under one cache
directory, name their own variables `<TOOL>_<KEY>`, take credentials only
from the environment or the system keyring, and document how to back up
their stores (DEV §18). Each tool still works alone.

**Why.** The `nogat` package (ECO-026) is meant to be one working
environment. On 2026-10-20 each tool configured itself differently: Kartograf
wrote its cache into the current directory, IMGWTools used about twenty
`IMGW_*` variables, Retman its own `retman.toml`, Archiwista platform
directories, and the language was set per tool (`IMGW_LANG`,
`HYDROLOG_LANG`). `nogat init` could not configure that in one step.

**Rejected.** A shared configuration library imported by every tool (a new
dependency between all projects for reading one TOML file); configuration
only in `nogat` passed to tools on the command line (tools used alone would
lose it).

## ECO-029 Automated dependency updates and audit

**Amended by ECO-040 (2026-10-20):** Dependabot covers GitHub Actions only; the audit is
informative.

**Decision.** Dependabot for GitHub Actions and `uv.lock`, actions pinned by
commit SHA, a blocking `pip-audit` job, third-party updates per release set
and patch releases for vulnerabilities between sets (DEV-13.6, DEV-13.7).

**Why.** Nothing was automated on 2026-10-20; Hydrograf's audit did not
block. Release sets fix versions for months, so known vulnerabilities need a
path that does not wait for the next set. Tags of actions can be moved by
their owners; a SHA cannot.

**Rejected.** Renovate (one more service; Dependabot is built into GitHub and
supports uv); updating third-party packages in each project independently
(undoes ECO-025).

## ECO-030 Protected branches require green CI only

**Amended by ECO-037 (2026-10-20):** merge commits only, no bypass actors, release tags
protected.

**Decision.** `main` and `develop` accept changes only through pull requests
with green required CI checks; no review is required while the author is the
only maintainer (DEV-3.6).

**Why.** The author develops the repositories alone and asked for green CI as
the only condition. Agents then cannot push unchecked code to shared
branches even if they ignore DEV-3.3.

**Rejected.** Required reviews (no second maintainer); no protection
(DEV-3.3 enforced by agent discipline only).

## ECO-031 External contributors keep their identity

**Amended by ECO-038 (2026-10-20):** messages are checked when commits enter `develop`.

**Decision.** DEV-4.2 (single author identity) applies to the author's and
agents' commits. Commits from external contributors keep their identity; the
gate skips the author check for pull requests from forks, and the CLA is
signed in the pull request and recorded in `CONTRIBUTORS.md` (DEV-16.4,
DEV-16.5).

**Why.** The gate template rejected every author other than
`git@debever.pl`, which would have blocked every outside pull request; the
CLA needs the contributor's identity to mean anything. The history rewrite
already keeps the third-party author `PL1B5J` (ADOPTION_PLAN phase 1).

## ECO-032 Small, explicit support policy

**Superseded by ECO-035.**

**Decision.** Tier-1 platforms are the three CI systems; Python versions are
dropped only in a major `nogat` release and not before upstream end of life;
fixes go to the latest release, security fixes to the previous major for 6
months (REL §7).

**Why.** Users of `nogat` need to know whether they can stay on an older
release and whether their platform is tested; one maintainer can only
support a narrow window.

## ECO-033 Zen of Nogat and one way to write a rule

**Amended by ECO-046 (2026-10-21):** the version moves when the standard is
published to `main`, not at every change.

**Decision.** Standard 2.1 starts from twelve principles (standards/README.md,
"Zen of Nogat"). Every requirement is mandatory; `MAY` marks an option; there
is no SHOULD. A requirement is one or two sentences with an optional one-line
*Why*; dated facts and the state of named projects stay out of rules. Every
change of the standard bumps its minor version.

**Why.** One maintainer develops the ecosystem with agents. The 2.0 text had
279 items and about 18,000 words; 148 of 227 requirements carried no keyword,
so nobody could tell a rule from a description, and five same-day amendments
all stayed "2.0".

**Rejected.** Keeping RFC 2119 with three strengths (agents cannot apply
SHOULD without a criterion).

**Consequence.** Rules that could not be checked were removed or reduced to
what a check can enforce: the shrinking mypy baseline (ECO-010) and the
keyring for credentials (ECO-028).

## ECO-034 The registry holds structure only

**Decision.** `ecosystem.yaml` records what only Nogat knows: projects, their
roles, what they provide, who depends on whom, through what and with which
formats. Versions, pins and release tags are read from the repositories by
`nogat ecosystem drift` (`uv run scripts/ecosystem.py drift` until the
package exists).

**Why.** Copies of versions and pins had to be edited by hand at every
release and pin change; the drift check compared one copy with another, not
with the repositories (Zen 2).

**Rejected.** Hand-kept versions and pins (simpler script, stale data).

## ECO-035 Minimal support and three channels

**Decision.** Supported is the latest release set and the latest release of
each member, on the three CI runners, on the Python versions the set
verified. Distribution channels are PyPI, GitHub Releases and the MCP
Registry; others wait until a user asks.

**Why.** One maintainer cannot keep backports, untested platform tiers or
six further channels; the author agreed to the minimal policy.

**Rejected.** Tier-2 platforms, six-month backports, EOL promises (ECO-032).

## ECO-036 Three profiles: tool, app, hub

**Decision.** Profiles are `tool` (installable Python package), `app`
(deployed service) and `hub` (Nogat). `library`, `pipeline` and `assistant`
become `tool`; `external` is removed with third-party registry entries.

**Why.** Six profiles for eight projects, three of them with one project
each, multiplied applicability rules without changing what the projects do.

## ECO-037 One release path

**Decision.** A release is: verified code, a release pull request into
`develop` that changes only version, CHANGELOG, lock and member pins, a pull
request `develop` → `main` merged with a merge commit, and a tag on that
commit. Hotfixes branch from `main` and return to `develop`. A release set
candidate is verified by a Nogat CI workflow on the three runners; the
published set is the `nogat` repository at its tag, installed from git until
the members are on PyPI. Rulesets allow merge commits only, have no bypass
actors and protect `v*` tags.

**Why.** The 2.0 text tagged "exactly the verified commit", which a
pull-request merge cannot produce; it published `nogat` to PyPI before its
members could be there (PyPI rejects git dependencies); and it relied on
manual verification on three machines.

**Rejected.** Trunk-based development without `develop` (the author keeps
`develop`, ECO-008); squash merges (would make `develop` and `main` diverge).

## ECO-038 Commits are checked once, on entry to develop

**Amended by ECO-049 (2026-10-21):** messages are checked on every pull
request into `develop` (the author only on the repository's own branches),
and hotfix commits on their pull request into `main`.

**Decision.** The gate and CI check commit messages and the author when
commits enter `develop` (locally and on pull requests into `develop` from the
repository's own branches); pull requests into `main` and pushes are not
re-checked. The committer is not checked.

**Why.** Re-checking the whole unreleased history in the release pull request
failed on any Dependabot, contributor or GitHub-made commit; GitHub sets
itself as committer of merge commits.

## ECO-039 One planning document, one request list, short PROGRESS

**Amended by ECO-043 (2026-10-21):** needs for another project are GitHub
issues labelled `request` in that project's repository.

**Decision.** Plans, specifications and research notes for new work are one
kind, `docs/plans/YYYY-MM-DD-slug.md`. Needs for another project are entries
in Nogat `docs/requests/<Project>.md`, read at that project's session start.
PROGRESS holds status, next steps and open questions only.

**Why.** Seven places held "think before coding" and two destinations held
cross-project needs; PROGRESS duplicated git history.

## ECO-040 Dependabot for actions, audit informs

**Decision.** Dependabot updates GitHub Actions; Python vulnerabilities come
from GitHub's Dependabot security updates and a non-required `pip-audit` job
over PyPI packages. Third-party versions change with release sets.

**Why.** Weekly `uv.lock` pull requests contradicted release sets (ECO-025),
and a required audit could never pass in projects that depend on siblings
through git (no hashes).

## ECO-041 Hydraulik stays MIT; SFINCS is not distributed

**Decision.** The Hydraulik repository stays MIT. The SFINCS engine is not
distributed with it: users run it themselves, for example from a Docker image.

**Why.** Author decision 2026-10-20: SFINCS runs as an external engine, so
Hydraulik does not distribute it.

**Consequence.** The `README.md` and `CLAUDE.md` of Hydraulik name
`hydromt_sfincs` (GPL-3.0) and SFINCS as external, per DEV-13.5.

## ECO-042 Agent-facing text follows the channel

**Decision.** Machine output is English whatever the user's language:
`--json` output, the error document on the last stderr line, MCP results and
descriptions, REST responses unless the client sends `Accept-Language`
(browsers of a web UI do). `lang` (default `pl`) selects the language of
human-readable output only. `hint` is in the language of `message`.

**Why.** With `lang = pl` as the default, the error document that agents
parse carried Polish `title` and `message`, against Zen 9 and AGI-9.2's own
reason ("agents work best in English"); an agent's result also depended on
the user's setting.

**Rejected.** English by default everywhere (end users would have to
configure Polish); Polish by default in machine output (agents get Polish).

## ECO-043 Needs between projects are GitHub issues

**Decision.** A need in another project is a GitHub issue labelled `request`
in that project's repository; the session that resolves it closes it.
Nogat `docs/requests/` and the hub requirement that kept it are removed.

**Why.** DEV-17.5 allowed an agent to change only its session's repository,
yet asked it to write and delete entries in Nogat; every request cost a Nogat
branch, gate and pull request. Issues need no commit and are read where the
work happens.

**Rejected.** An exception for Nogat request files (a pull request per
request); needs in the requesting project's PROGRESS (scattered list).

## ECO-044 Nogat's tooling reports errors by the registry

**Decision.** Nogat's scripts report failures with registry codes and exit
codes, and print the `nogat-error/1` document as the last stderr line: a
malformed input is `data_error`, a missing one `not_found`, a stale
generated file or incompatible ranges `conflict`, a wrong call
`validation_error`, a defect `internal_error` (HUB-4.8). The rest of the
command shape (`--json` envelopes) waits for the `nogat` package.

**Why.** The scripts exited 1 for failed checks, which ERR §2 reserves for
`internal_error`; agents could not tell a stale map from a crash.

**Rejected.** Exempting the hub from ERR until the package exists (two
meanings of exit 1 in one ecosystem).

## ECO-045 Precedence of conflicting requirements

**Decision.** When two requirements conflict, safety and the author's
approvals (DEV-3.3, DEV §13) come first, then the requirement that names a
profile or is narrower, then the general one. The agent follows the higher
one and reports the conflict as an issue in Nogat labelled `standard`.

**Why.** Every requirement is mandatory (ECO-033), so a conflict left an
agent with no rule to follow; reporting it turns the conflict into a fix of
the standard.

**Rejected.** Stopping and asking the author at every conflict (blocks
autonomous work on known conflicts).

## ECO-046 The standard is tagged when published

**Decision.** Changes of the standard accumulate on `develop` under the next
version and its changelog; the merge into `main` is tagged `std-X.Y`, and
the next change starts X.(Y+1).

**Why.** ECO-033 bumped and tagged at every change. Version 2.1 changed many
times before it reached `main`; a tag per change would have produced
versions no project could use, and ERR-3 needs a tag only for what projects
copy.

**Rejected.** A minor version and tag per change (ECO-033).

## ECO-047 Plan approval is a line in the plan

**Decision.** After the author approves a plan in a session, the plan gets
`Approved: YYYY-MM-DD` under its title; code starts only after that line
exists (DEV-17.4).

**Why.** DEV-17.4 required approval before code but left no record, so an
agent in a later session could not tell an approved plan from a draft.

**Rejected.** A merged pull request per plan (a review cycle before every
interface change).

## ECO-048 Nogat's AGENTS.md routes and links

**Decision.** Nogat's AGENTS.md is generated from the registry: a routing
table (task → tool → entry command) with links to each tool's AGENTS.md. The
tools' blocks are not inlined; the AGENTS.md budget of DOC-1.7 applies.

**Why.** Seven blocks of up to 60 lines and a routing table exceed the
200-line budget, and clients truncate AGENTS.md (Codex reads 32 KiB).

**Rejected.** A separate, larger budget for the hub (more context for every
agent starting in Nogat).

## ECO-049 Hotfix commits are checked on entry to main

**Decision.** Commit messages are checked on every pull request into
`develop`, the author only on pull requests from the repository's own
branches (DEV-4.5). Pull requests from `hotfix/*` into `main` get the same
checks, because their commits enter `main` before `develop`.

**Why.** ECO-038 checked commits on entry to `develop`, which hotfix commits
reach only after they are released; its text also limited message checks to
the repository's own branches, which DEV-4.5 and the CI template did not.

**Rejected.** Checking every pull request into `main` (re-checks released
history, the failure ECO-038 removed).

## ECO-050 Agent documents have canonical schemas in Nogat

**Decision.** The result envelope, the error document and the command
catalog have JSON Schemas in Nogat `schemas/agent/` (`result-1`, `error-1`,
`commands-1`); the error schema is generated from `error_registry.json`.
Projects copy them with the registry (ERR-3) and validate their documents in
contract tests. The contract they encode: an error prints nothing on stdout
and the error document on stderr; `partial` and `failed` print the envelope
and no error document; a failed unit carries a registry `code`;
`validate_command` checks options without planning; the MCP catalog tools are
`<tool>_commands_list` and `<tool>_commands_schema`; a catalog command lists
its MCP `families`.

**Why.** AGENT_INTERFACE.md defined the documents in prose only, without
examples; seven projects could each claim AGI-1.2 and still emit different
documents. The review also found the stream contract on errors, the meaning
of `validate_command`, the `core` family field and the catalog tool name
(which broke AGI-5.2's pattern) undefined.

**Rejected.** Each project writing its own schemas (drift, Zen 2); a Python
package of validators before the `nogat` package exists (one more
distribution to release).

## ECO-051 One data-output convention

**Decision.** A tool with a versioned store writes data in the same two modes
everywhere (DEV §19): plain files in a directory (`--output-dir`, `-o`) with
no metadata, or the store (`--root`) with sidecars and a marker file; an
export writes one file (`--output`). With neither option a command writes to
the store at `<data_dir>/<tool>`. A plain write checks every target before
the first byte, goes through a staging directory and replaces an existing
file only with `--force`. A store is recognised by its marker file name, so
no tool imports another to refuse a nested store. A writing command lists
`files[]` with path, size, SHA-256 and status.

**Why.** On 2026-10-24 the two store tools disagreed: Kartograf's `-o` was a
store root and no command wrote a plain file; IMGWTools had `--root`, the
variable `IMGW_STORE_ROOT`, `--path` for exports and a plain download into
`data/downloaded` of the current directory. The same call meant different
things in two tools (AGI-1.2, Zen 1), and a rule written for one tool would
have been written again for the second (Zen 11). Both tools are untagged, so
the change lands before their first release and needs no data migration
(ECO-020).

**Rejected.** The variant drafted on the Kartograf branch
`claude/vigilant-faraday-finqvd` (its ADR-048): `--output` for the plain
directory and `--store` for the store (AGI-3.4 gives `--output` to a file and
`--root` to the store root); one of the two required, neither an error (the
store already has a place, DEV-18.2); no flag to overwrite (a second download
needs a manual delete, while AGI-3.4 already gives `--force` the meaning
"ignore existing results"); Kartograf alone, with HSG outside plain mode
(IMGWTools would keep its own names). A shared store library imported by all
tools (a new dependency between all projects, against Zen 10; the layouts
differ per tool, and a marker file name needs no import).

**Consequence.** Kartograf and IMGWTools adopt DEV §19 before their first
release; their consumers change the calls that gave a store as `output_dir`
or `-o` (plan `docs/plans/2026-10-24-data-output.md`).

## ECO-052 The routing table is registry data

**Decision.** The rows of Nogat's AGENTS.md routing table (ECO-048) are the
`routes` of `ecosystem.yaml`: for each project a `task` and the `command` that
starts it (HUB-2.9). `uv run scripts/ecosystem.py agents` writes the file,
`agents --check` is a step of the gate, and a contract test compares the file
with the generator (HUB-4.3, DEV-10.4). Each row links the tool's guide as raw
Markdown on `main`; an `app`, which has no AGENTS.md, links its README.

**Why.** Which tool covers a task is the one thing only Nogat knows, so it
belongs in the registry (ECO-034). The tools' catalogs cannot supply it: Nogat
imports no tool (HUB-1.2), the gate runs offline without the checkouts, and a
catalog lists every command (Kartograf alone has more than forty), not the
tasks a person states. Raw Markdown is what an agent fetches without HTML
(DOC-5.2), and every repository releases from `main` (DEV-3.1).

**Rejected.** Reading each tool's `commands list` when generating: it needs
every tool installed, the file would change with each tool's release, and the
gate could not run offline. A row for every command of every tool: the tools'
own guides list them, and the file would exceed its budget (ECO-048).

**Consequence.** `validate` checks that a route starts with its project's CLI,
not that the tool still has the command; when a tool renames or drops an entry
command, its route changes in the registry in the same plan (HUB-5.2).

## ECO-053 Development versions of a pinned producer, and tests in a wheel

**Decision.** The integration dry run of 2026-10-25 (plan
`docs/plans/2026-10-25-integration-dry-run.md`) ended in three decisions.
(1) While a consumer pins a producer by commit (REL-5.3), the range of
producer versions it declares as supported starts at the producer's
development version of the pending release: `>=0.8.0.dev0,<0.9`; its release
pull request narrows it to `>=0.8.0` with the tag. Runtime checks use the same
range, with `prereleases=True` (REL-5.6). (2) A test finds repository files
from its own location, never through the installed package; the members are
installed as wheels (REL-2.5). (3) Consumers' contract tests use the
producer's public `<package>.testing`, which the producer ships in its wheel
(DEV-10.6, REL-6.5).

**Why.** Develop carries `0.8.0.dev0` (REL-1.1), which PEP 440 puts below
`0.8.0`; Retman and Archiwista accepted `>=0.8.0,<0.9` and refused Kartograf's
head: nine Retman tests and 156 of Archiwista's failures came from that alone,
while the commit they pinned still said `0.8.0` and hid it. Kartograf and
Archiwista located their repository through `<package>.__file__`; that works
in an editable install and fails in the wheel that REL-2.3 and REL-6.5 test.
Only Retman's IMGWTools half built its stores with a producer's `testing`
module, so a change of format would not break the other consumers' tests
before users.

**Rejected.** Dropping the lower bound, or accepting any `0.8` pre-release
through a second check in each consumer (two ranges to keep equal; the
declared one is the one `uv` resolves). Changing `develop` to carry `X.Y.0`
between releases (REL-1.1 gives the unreleased version a spelling that cannot
be mistaken for the release). Installing the member under test editable in
`verify-candidate` (it tests another artefact than the wheel users get and
hides missing package data, ECO-011). Keeping the tests that use the package
path and skipping them in CI (they stay broken in the wheel check of REL-2.3).

**Consequence.** Retman (`supported_versions` and the checks that read it) and
Archiwista (its Kartograf range and doctor), and any consumer that pins a
producer by commit, change their range before their next pin; Kartograf and
Archiwista change the tests that find their repository through the package;
Archiwista, Retman, Hydraulik and Hydrolog move to the producers' `testing`
modules (the owners' follow-ups are listed in the dry-run plan).

## ECO-054 Projects belong to Archiwista

**Decision.** A project, the record of the work on one task (its area, the
store versions it pins, its activity and its exports), is kept only by
Archiwista, in `archiwista-project.json` (`archiwista-project/1`) in the
project's directory. Kartograf and IMGWTools download, check and keep the
versioned store; they have no project manifest, command, MCP tool or library
function, and each gives the command of a stored version from its metadata
(Kartograf `command_for_file`, IMGWTools `command_for_version`), refusing
with `unsupported` where the metadata does not rebuild the call. Plan:
`docs/plans/2026-10-31-archiwista-projects.md` (option B).

**Why.** The notion was split in three: `kartograf-project/1`,
`imgw-project/1` and Archiwista's projects with access, own data and
snapshots. In the producers' model a pin exists only inside a task and only
after a full run of its command, so data already in the store could not be
pinned without asking the source, and a project had no area, activity or
export. Every new project feature crossed three repositories. Neither
producer had released projects, so removing them breaks no user (ECO-020).

**Rejected.** Keeping the producers' manifests under one Archiwista view (the
split stays and a version is pinned only through a producer's task). A shared
project library imported by every tool (a new dependency between all
projects for a notion only Archiwista presents). Releasing the producers'
projects now and moving them later (the release would publish an interface
only to break it in the next one).

**Consequence.** DEV-19.18 no longer names a `project` command. The registry
drops `kartograf-project/1` and `imgw-project/1` and lists
`archiwista-project/1`; Retman drops its IMGWTools project module; the first
release set tags Kartograf, IMGWTools, Hydrolog and Retman without waiting
for Archiwista, which follows in its own session (REL-5.4).
