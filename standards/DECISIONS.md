# Ecosystem standard decisions

Decision log for the shared standard (1.x). Each entry records what was
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
| [ECO-004](#eco-004-standard-v20-is-rewritten-from-practice) | Standard v2.0 is rewritten from practice | amended by ECO-056 | 2026-10-19 |
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
| [ECO-046](#eco-046-the-standard-is-tagged-when-published) | The standard is tagged when published | amended by ECO-056 | 2026-10-21 |
| [ECO-047](#eco-047-plan-approval-is-a-line-in-the-plan) | Plan approval is a line in the plan | accepted | 2026-10-21 |
| [ECO-048](#eco-048-nogats-agentsmd-routes-and-links) | Nogat's AGENTS.md routes and links | accepted | 2026-10-21 |
| [ECO-049](#eco-049-hotfix-commits-are-checked-on-entry-to-main) | Hotfix commits are checked on entry to main | accepted | 2026-10-21 |
| [ECO-050](#eco-050-agent-documents-have-canonical-schemas-in-nogat) | Agent documents have canonical schemas in Nogat | amended by ECO-058, ECO-075 | 2026-10-21 |
| [ECO-051](#eco-051-one-data-output-convention) | One data-output convention | accepted | 2026-10-24 |
| [ECO-052](#eco-052-the-routing-table-is-registry-data) | The routing table is registry data | accepted | 2026-10-25 |
| [ECO-053](#eco-053-development-versions-of-a-pinned-producer-and-tests-in-a-wheel) | Development versions of a pinned producer, and tests in a wheel | accepted | 2026-10-25 |
| [ECO-054](#eco-054-projects-belong-to-archiwista) | Projects belong to Archiwista | amended by ECO-059, ECO-074 | 2026-10-31 |
| [ECO-055](#eco-055-one-visual-identity-for-every-gui) | One visual identity for every GUI | amended by ECO-079 | 2026-11-01 |
| [ECO-056](#eco-056-numbers-count-from-main) | Numbers count from main | accepted | 2026-11-03 |
| [ECO-057](#eco-057-imgwtools-becomes-obserwator) | IMGWTools becomes Obserwator | accepted | 2026-11-03 |
| [ECO-058](#eco-058-guis-link-to-each-other-and-hand-off-one-way) | GUIs link to each other and hand off one way | accepted | 2026-11-12 |
| [ECO-059](#eco-059-station-data-raw-in-archiwista-harmonized-in-obserwator-computed-by-hydrolog) | Station data: raw in Archiwista, harmonized in Obserwator, computed by Hydrolog | amended by ECO-084 | 2026-11-13 |
| [ECO-060](#eco-060-every-product-carries-the-providers-attribution) | Every product carries the providers' attribution | amended by ECO-064, ECO-065, ECO-068, ECO-082, ECO-084, ECO-087 | 2026-11-13 |
| [ECO-061](#eco-061-every-gui-serves-one-regulamin-from-nogats-template) | Every GUI serves one regulamin from Nogat's template | amended by ECO-062, ECO-070, ECO-079 | 2026-11-13 |
| [ECO-062](#eco-062-public-guis-no-sign-in-no-stored-ip-addresses-regulamin-10) | Public GUIs: no sign-in, no stored IP addresses, regulamin 1.0 | amended by ECO-063, ECO-066, ECO-070, ECO-079 | 2026-11-13 |
| [ECO-063](#eco-063-regulamin-10-after-its-review-no-ip-address-in-any-log) | Regulamin 1.0 after its review: no IP address in any log | amended by ECO-066 | 2026-11-13 |
| [ECO-064](#eco-064-one-compact-strip-of-provider-lines-per-gui-view) | One compact strip of provider lines per GUI view | amended by ECO-065, ECO-068, ECO-070, ECO-080, ECO-087 | 2026-11-13 |
| [ECO-065](#eco-065-products-link-the-providers-terms-and-never-restate-them) | Products link the providers' terms and never restate them | accepted | 2026-11-13 |
| [ECO-066](#eco-066-one-logging-convention-for-every-server-without-root) | One logging convention for every server, without root | accepted | 2026-11-13 |
| [ECO-067](#eco-067-one-admin-panel-for-every-gui) | One admin panel for every GUI | accepted | 2026-11-13 |
| [ECO-068](#eco-068-regulamin-10-corrected-in-place-gugik-isric-and-čúzk-lines) | Regulamin 1.0 corrected in place; GUGiK, ISRIC and ČÚZK lines | accepted | 2026-11-13 |
| [ECO-069](#eco-069-info-texts-of-a-gui) | Info texts of a GUI | accepted | 2026-11-14 |
| [ECO-070](#eco-070-the-regulamin-link-in-the-menu-the-rail-and-the-welcome-window) | The regulamin link in the menu, the rail and the welcome window | accepted | 2026-11-14 |
| [ECO-071](#eco-071-processing-lines-never-name-the-processing) | Processing lines never name the processing | accepted | 2026-11-14 |
| [ECO-072](#eco-072-everything-is-version-1-until-the-first-release) | Everything is version 1 until the first release | accepted | 2026-11-14 |
| [ECO-073](#eco-073-long-jobs-run-outside-the-agents-session) | Long jobs run outside the agent's session | accepted | 2026-11-15 |
| [ECO-074](#eco-074-the-author-names-the-members-of-a-release-set) | The author names the members of a release set | accepted | 2026-11-15 |
| [ECO-075](#eco-075-the-catalog-summary-is-its-own-document) | The catalog summary is its own document | accepted | 2026-11-15 |
| [ECO-076](#eco-076-nogat-starts-at-010) | Nogat starts at 0.1.0 | accepted | 2026-11-16 |
| [ECO-077](#eco-077-verify-candidate-runs-an-app-on-its-own-lock) | verify-candidate runs an app on its own lock | accepted | 2026-11-16 |
| [ECO-078](#eco-078-formulas-are-declared-once-checked-at-their-limits-and-verified) | Formulas are declared once, checked at their limits and verified | accepted | 2026-11-18 |
| [ECO-079](#eco-079-an-operators-instance-its-name-and-logo-beside-the-mark-its-own-regulamin) | An operator's instance: its name and logo beside the mark, its own regulamin | accepted | 2026-11-21 |
| [ECO-080](#eco-080-the-sources-strip-folds-to-one-line-on-a-phone) | The sources strip folds to one line on a phone | accepted | 2026-11-21 |
| [ECO-081](#eco-081-the-kit-becomes-110-with-nogat-020) | The kit becomes 1.1.0 with Nogat 0.2.0 | accepted | 2026-11-21 |
| [ECO-082](#eco-082-providers-named-by-their-national-acronyms-two-attribution-columns-in-a-csv) | Providers named by their national acronyms; two attribution columns in a CSV | accepted | 2026-11-21 |
| [ECO-083](#eco-083-one-pattern-for-the-files-a-tool-names-for-a-user) | One pattern for the files a tool names for a user | accepted | 2026-11-21 |
| [ECO-084](#eco-084-operational-data-are-kept-as-captures-of-an-unverified-tier-serving-them-is-the-operators-decision) | Operational data are kept as captures of an unverified tier; serving them is the operator's decision | accepted | 2026-11-23 |
| [ECO-085](#eco-085-additions-within-version-1-of-a-released-document) | Additions within version 1 of a released document | accepted | 2026-11-23 |
| [ECO-087](#eco-087-provider-lines-in-one-table-a-gui-declares-a-line-the-kit-does-not-know) | Provider lines in one table; a GUI declares a line the kit does not know | accepted | 2026-11-23 |

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

**Amended by ECO-056 (2026-11-03):** v1.0 is the shared standards of
2026-01-29 that preceded Nogat, archived in `legacy/shared-2026-01/`; v2.0
is a draft of standard 1.0.

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
tools stayed as registry entries until ECO-036 removed them.

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

**Decision.** The standard starts from twelve principles (standards/README.md,
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

**Amended by ECO-056 (2026-11-03):** a version exists from its tag on
`main`; the version `develop` carries may be renumbered until then.

**Decision.** Changes of the standard accumulate on `develop` under the next
version and its changelog; the merge into `main` is tagged `std-X.Y`, and
the next change starts X.(Y+1).

**Why.** ECO-033 bumped and tagged at every change. The standard changed many
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

**Amended by ECO-058 (2026-11-12):** the envelope `nogat-handoff/1` that
GUIs exchange is a canonical schema too, in `schemas/exchange/`, copied and
checked the same way; `drift` reports every copy (DEV-15.6).

**Amended by ECO-075 (2026-11-15):** the summary of the catalog,
`<tool>-command-list/1`, has its own schema `command-list-1`.

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

**Amended by ECO-059 (2026-11-13):** for the station data of IMGW-PIB and
ČHMÚ, Archiwista orders the downloads, through Obserwator's library, and
keeps the raw data; Obserwator keeps the harmonized series, catalogs and
analysis results in a data root of its own.

**Amended by ECO-074 (2026-11-15):** Archiwista is a member of the first
release set; its consequence for the set's order no longer applies.

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

## ECO-055 One visual identity for every GUI

**Amended by ECO-079 (2026-11-21):** an instance that an operator other than
the author runs may show the operator's logo and name beside the project's
mark, which stays as the favicon and in the top bar.

**Decision.** Every GUI of the ecosystem (Archiwista, Hydrograf, the web GUI
of IMGWTools and any later one) uses the identity in Nogat `design/`: shared
tokens in one plain CSS file, light and dark, with the brand of debever.pl
and the working interface of Archiwista; one mark and one accent pair per
project; Archiwista's shell of top bar, navigation rail and resizable side
panel (DEV-15.3). Plan: `docs/plans/2026-11-01-visual-identity.md`.

**Why.** The same person moves between the GUIs; each looked unrelated
(Archiwista indigo and dense, Hydrograf Apple-style glass, no shared mark),
so every screen had to be learnt again.

**Rejected.** Sharing only the marks (the screens stay unrelated). A shared
CSS framework or component package (a build step in apps that are build-free
under CSP `'self'`, and a dependency between apps).

**Consequence.** Each GUI adopts the identity in its own session and plan;
until then the gap is a deviation in its `CLAUDE.md` (DEV-1.2). A new project
in `ecosystem.yaml` gets its mark and accent pair in `design/`; Nogat's
contract test fails without them.

## ECO-056 Numbers count from main

**Decision.** Only a repository's `main` fixes a number; what `develop` and
topic branches carry binds no user. A version of the standard exists from
its tag `std-X.Y` on Nogat's `main`, and `develop` carries the next one
(HUB-6.1). A document's `<n>` in `<tool>-<kind>/<n>` increments only past a
number released on the producer's `main`; a breaking change to an unreleased
document keeps its number (AGI-4.1). The first standard published to `main`
is 1.0, tagged `std-1.0`: the drafts called 2.0 and 2.1 on `develop` are
1.0, and earlier entries keep those draft names. The shared standards of
2026-01-29, which preceded Nogat and were never on its `main`, are archived
as `legacy/shared-2026-01/`, so 1.0 names one thing. Plan:
`docs/plans/2026-11-03-numbering-from-main.md`.

**Why.** Nogat's `main` holds no standard and `origin` has no tags; read
from `main`, 2.1 would follow no 1.0 or 2.0. Bumping a document number for a
format never released (`archiwista-state/2`) leaves consumers a gap with no
document behind it.

**Rejected.** Keeping 2.1 and explaining the gap (every project would cite
a version that was never published). Calling the legacy shared standards 1.0
(two things named 1.0). Incrementing `<n>` at every breaking change on any
branch (numbers no consumer ever read).

## ECO-057 IMGWTools becomes Obserwator

**Decision.** From v3.0.0 the tool released as IMGWTools 2.1.1 is called
Obserwator: the product, the distribution and import package `obserwator`
(`nogat-obserwator` at ADOPTION_PLAN 6.1, where a final `imgwtools` release
points to it), the command `obserwator`, and every name derived from the
tool: `OBSERWATOR_<KEY>` (`OBSERWATOR_IMGW_API_URL` for a provider
endpoint), `[obserwator]` in `nogat.toml`, `<data_dir>/obserwator`, document
ids `obserwator-<kind>/1`, the marker `obserwator-store.json`, MCP tools
`obserwator_*`, `x-obserwator*`, `ObserwatorError` and its subclasses. The
institute keeps its name: IMGW-PIB, the dataset ids `pl.imgw.*` and
identifiers naming the provider stay. The repository URL and the workspace
directory `IMGWTools` stay until the author renames the repository, so a
checkout is found by the repository's name, not the registry `name`
(HUB-3.1). Dated records keep the old name. On 2026-11-04 the author
renamed the repository to `Daldek/Obserwator`; the registry `repo` and the
checkout directory `Obserwator` follow (plan step 5). Plan:
`docs/plans/2026-11-03-imgwtools-to-obserwator.md`.

**Why.** The author's decision of 2026-11-03: IMGW-PIB is an institute, not
the tool, which reads ČHMÚ as well. Before the first release from `develop`
is the cheapest time: the only release, 2.1.1 on `main`, has no store and
none of the document ids, which exist only on `develop`, so they are renamed
without an alias or a migration (ECO-056).

**Rejected.** Renaming only the product and keeping `imgw` for the command,
the package and the ids (two names for one tool, and the institute's name
on every identifier). Aliases for the old ids, variables and marker (a
compatibility layer for formats no user has, ECO-056). Renaming the
repository in the same step (every URL in every repository changes at once;
the author does it later).

**Consequence.** Producers first (HUB-5.2): Nogat, then Obserwator, then
Archiwista, Retman, Hydraulik and Hydrolog, then the frozen Kartograf
(`STORE_MARKERS`) and Hydrograf (documents only; its pin and imports of
`imgwtools` stay until after its v0.5.0).

## ECO-058 GUIs link to each other and hand off one way

**Decision.** The GUI platform comes in two stages. Stage 1: every GUI of the
ecosystem shows the kit's app menu, which leads to the other GUIs the
deployment configures in `[nogat.gui]` of `nogat.toml`, and hands data off by
file and clipboard through the kit's `nogat-handoff.js` (DEV-15.4, DEV-15.5).
The kit lives in Nogat `design/kit/` beside the tokens: plain files copied
byte for byte, which `drift` checks by hash (DEV-15.6). Nogat runs no GUI;
one window with one sign-in is stage 2, a new project with its own
repository that copies the kit like every other GUI. Plans:
`docs/plans/2026-11-12-gui-links-and-handoff.md` (stage 1) and
`docs/plans/2026-11-01-nogat-gui-platform.md` (stage 2).

**Why.** The author's decision of 2026-11-12. No GUI linked to another, and
the hand-off ran through three implementations that differed in file name,
text and clipboard behaviour, while Archiwista's copy of `handoff-1` fell
behind unseen. Links and one hand-off take about ten sessions and stay useful
under a hub; the hub with frames, a proxy and one sign-in takes over thirty.

**Rejected.** Nogat hosting the GUIs (the standard's repository would carry a
web server and a sign-in). Each GUI writing its own menu (a fourth copy of
the same code). Addresses in the registry (they differ per deployment,
HUB-2.4). The kit in the hub's repository (every GUI would depend on an app).

**Consequence.** Each GUI adopts the kit in its own session (steps 4 to 7 of
the stage 1 plan); until then the gap is a deviation in its `CLAUDE.md`
(DEV-1.2).

## ECO-059 Station data: raw in Archiwista, harmonized in Obserwator, computed by Hydrolog

**Amended by ECO-084 (2026-11-23):** Obserwator's commands run by the
deployment's user systemd timers write the raw root beside the downloads
Archiwista orders; operational data are archived as captures; the backup
copy of the raw and data roots is the deployment's `rsync` timer, documented
by Obserwator, not an Archiwista job.

**Decision.** For the hydro-meteorological station data of IMGW-PIB and
ČHMÚ each project has one role. Archiwista orders every download and keeps
the raw data (the archives as published with their sidecars, the archived
station metadata, the PMAXTP cells) in a raw root of the `obserwator-store/1`
layout; the download code stays Obserwator's library, which Archiwista calls
into that root. Obserwator reads the raw root without writing it, parses it
into harmonized series and station catalogs in a data root of its own,
stores there the results of the analyses, and serves both (GUI, files, REST,
MCP); Obserwator holds the production data root, and Archiwista keeps a
backup copy of the whole data root. Hydrolog computes every analysis;
Obserwator starts Hydrolog's program and does not import it. Everything is
computed once, at the start; once a year, when IMGW-PIB and ČHMÚ publish new
packages, they are downloaded and the data root is rebuilt and recomputed. A
result for a subset a person chooses is computed on the fly and never
stored. Operational data, such as IMGW-PIB's warning and alarm levels, are
not archived. Kartograf's data and roles do not change. Plan:
`docs/plans/2026-11-12-station-data-and-analyses.md`.

**Why.** The author's decisions of 2026-11-12 and 2026-11-13. One Obserwator
store held the raw archives, the series, the catalogs and the PMAXTP cells,
so a public Obserwator would carry every raw archive; Archiwista already
ordered its downloads through Obserwator's library; and the author's
analyses had no home, as Obserwator's PRD and Archiwista's scope both leave
statistics to Hydrolog.

**Rejected.** Moving the download code to Archiwista (about 7,900 lines and
their tests move, and the archive contracts leave the code that writes
them). One root with each project's directories (a public Obserwator would
carry every raw archive). Obserwator computing the simple analyses itself
(two codes for one number). Obserwator importing Hydrolog (Hydrolog is not
on PyPI and depends on Obserwator optionally). Every result computed on
request (the cost on a small server). Storing the results of a person's
subsets (data no one asked to keep).

**Consequence.** ECO-054's producers that download, check and keep the
versioned store are, for these data, Obserwator's library called by
Archiwista and Archiwista's raw root. Obserwator, Archiwista and Hydrolog
change in their own sessions and plans, producers first (HUB-5.2); until
then the registry lists the new edges as `planned`.

## ECO-060 Every product carries the providers' attribution

**Amended by ECO-064 (2026-11-13):** a GUI view shows one compact strip with
S, P, PS, PP and the short form CK of C, and the full lines and terms in a
dialog behind „Źródła i warunki”; products keep the full lines.

**Amended by ECO-065 (2026-11-13):** the terms-of-use notice N and the line
H are gone; `terms_notice` holds only the links RD, RH and RK, each naming
the terms it links.

**Amended by ECO-068 (2026-11-13):** products with GUGiK, ISRIC SoilGrids or
ČÚZK data carry G, SG or Z, after CP in the order of the lines, and a GUI
view's strip shows them as GK, SK and ZK.

**Amended by ECO-082 (2026-11-21):** a CSV carries the lines in its trailing
columns `attribution` and `terms_notice` only; no column a project had
before repeats them.

**Amended by ECO-084 (2026-11-23):** operational data are kept as captures
of a labelled, unverified tier and served to the public only at the
operator's decision per source (DEV-20.8).

**Amended by ECO-087 (2026-11-23):** the lines are one table of provider
lines that DEV-20.4 orders, a new provider a row of it; the line of a
provider it does not hold, declared by a deployment, follows them.

**Decision.** Every product made with data of IMGW-PIB or ČHMÚ carries the
lines their terms prescribe, verbatim, on every surface (DEV §20): S and P
for data of danepubliczne.imgw.pl and hydro.imgw.pl, with H naming the
hydrological service; PS, PP and the monograph M for PMAXTP; C and CP for
ČHMÚ. Products with IMGW-PIB data also show the notice of its terms of use
with the addresses of the terms that apply. JSON documents, results and
`nogat-handoff/1` carry the lines in two optional arrays of strings,
`attribution` and `terms_notice`, so a consumer shows them and carries them
on; the hand-off stays `/1` (AGI-4.1). Operational data of hydro.imgw.pl
are only shown live, never stored; its station locations are reference data
that may be kept with their lines (DEV-20.8, the author's decision of
2026-11-13). Plan: `docs/plans/2026-11-13-provider-attribution.md`.

**Why.** The author's order of 2026-11-13, read against the terms that day:
§5 ust. 1, 3 and 4 and §2 pkt 3 of the IMGW-PIB terms
(https://danepubliczne.imgw.pl/regulations), ust. 1 and 2 of the PMAXTP
terms, the terms of the hydrological service
(https://hydro.imgw.pl/#/regulamin) and CC BY 4.0 §3(a)(1) of ČHMÚ's open
data. Results pass through several tools (PMAXTP from Obserwator into
Hydrolog, Hydrograf and Hydraulik), and a line lost on the way is a breach in
the last product.

**Rejected.** The lines in `provenance` (it holds keyed origins, not text a
person reads). Objects with a provider, a data set and texts (lines equal
byte for byte merge without them, and the consumer only shows text). The
lines in an About page or a tooltip only (the terms bind the product
itself). One English wording (the terms prescribe the Polish sentences).

**Consequence.** Each project applies DEV §20 in its own branch and copies
the new `handoff-1.schema.json` byte for byte (DEV-15.6); until then a copy
of today accepts both fields as unknown.

## ECO-061 Every GUI serves one regulamin from Nogat's template

**Amended by ECO-062 (2026-11-13):** the public GUIs are Hydrograf, Hydrolog
and Obserwator, used without signing in, and Archiwista serves no terms; the
template keeps blocks for data sources only, states fixed rules for logs,
statistics, cookies and „Zgłoś uwagę”, and names its processor in two fields.

**Amended by ECO-070 (2026-11-14):** „Regulamin” is linked from the app
menu, the foot of the left rail and the welcome window, not from a footer.

**Amended by ECO-079 (2026-11-21):** an instance that an operator other than
the author runs serves the operator's own regulamin, drafted from the kit's
`nogat-terms-operator.md`, in place of regulamin 1.0.

**Decision.** A GUI open to other people serves its terms at
`regulamin.html`, filled from the kit's template `nogat-terms.md` and the
`nogat-terms.html` generated from it, and links „Regulamin” from every view
and from the app menu (DEV-15.7). The template is Polish, carries the lines
of DEV §20, and has fields filled from `[nogat.operator]` and `[nogat.gui]`
of `nogat.toml` and from the project, and blocks a project keeps for its data
sources and the personal data it processes. The filled page is plain HTML
without a script. Plan: `docs/plans/2026-11-13-gui-terms.md`.

**Why.** The author's order of 2026-11-13: every GUI needs terms. A service
offered to others by electronic means needs terms (art. 8 of the Polish act
on electronic services), the person whose data it processes must be told
what and why (RODO art. 13), and the providers' terms bind whoever reuses
their data. One text written once keeps four GUIs consistent.

**Rejected.** Terms written by each project (four texts drifting apart).
Filling in the browser from a JSON file (a legal page should read without a
script). One page served by Nogat (Nogat runs no GUI, ECO-058). The link only
in the app menu (it is not drawn without another GUI).

**Consequence.** Each GUI adopts the template in its own session; the
operator's identity, contact and retention periods are the author's to set
in `nogat.toml` before a deployment is opened to others.

## ECO-062 Public GUIs: no sign-in, no stored IP addresses, regulamin 1.0

**Amended by ECO-063 (2026-11-13):** no log of a public GUI holds an IP
address, error and application logs included; the regulamin names the
operator's mail service and may name the processor's cookie against bots,
in three more keys of `[nogat.operator]`.

**Amended by ECO-066 (2026-11-13):** every server logs as DEV §12 says; the
access log keeps the class of the User-Agent, not the User-Agent.

**Amended by ECO-070 (2026-11-14):** no footer or status bar shows the
statement; it opens § 3 of the regulamin only.

**Amended by ECO-079 (2026-11-21):** the statement of DEV-15.8 and regulamin
1.0 belong to the instances the author runs.

**Decision.** Hydrograf, Hydrolog and Obserwator are public GUIs: anyone
uses them without signing in, and Cloudflare Access guards only the parts the
operator alone uses, so no user's e-mail address is collected. Archiwista is
the operator's private tool behind Access and serves no terms. A public GUI
shows the author's statement of what the services are in every footer
(DEV-15.8); limits requests per IP address, held in memory only, with `429`
and `Retry-After` (DEV-15.9); logs requests without IP addresses and keeps
the logs 14 days (DEV-15.10); counts visitors by a hash of IP address and
User-Agent under a daily salt kept in memory, stores daily totals only and
sets no cookie (DEV-15.11); and takes „Zgłoś uwagę” reports without contact
fields, in one format, kept until handled (DEV-15.12). The regulamin becomes
version 1.0, one version and one date for the three services: the operator,
a private person named in `nogat.toml`, is reached by e-mail only; the
processor that carries the traffic is two fields, so leaving Cloudflare
changes values, not text; the act on electronic services is not invoked,
since the operator acts outside any gainful or professional activity (its
art. 2 pkt 6); liability is excluded except for intentional damage (art. 473
§ 2 KC); RODO requests are answered within a month (art. 12 ust. 3) and other
reports as time allows; a complaint goes to the President of UODO; a new
version takes effect on publication, and a change history at the end links
the template's history in Nogat. Plan: `docs/plans/2026-11-13-gui-terms.md`.

**Why.** The author's nine decisions of 2026-11-13 on the template of
ECO-061. Data a service never keeps need no retention period, no answer to an
access request and no consent banner; an address held only for a rate window,
or hashed under a salt gone the next day, protects the service and counts its
use without following anyone. One statement and one text keep the three
services saying the same, and one report format lets the operator read every
GUI's reports the same way.

**Rejected.** Cloudflare Access for every user (each would sign in with an
e-mail address the operator then processes, and the services are meant to be
public). Access logs with IP addresses (the limit and the statistics need
them only in memory). Analytics with cookies or a third party (a consent
banner and transfers for counts the server makes itself). A contact field in
„Zgłoś uwagę” (personal data a report does not need; e-mail serves whoever
wants an answer). One answer time for every report (one person runs the
services; RODO's month stays for data requests). Retention and Cloudflare
Access as deployment fields (one period, and no sign-in, in every public
GUI). A postal address of the operator or of UODO (the author's choice:
e-mail, and the office's web address).

**Consequence.** ECO-061's blocks for Cloudflare Access, accounts, the
session cookie and the feedback form, the derived block for no cookies and
the retention field are gone; kit 0.3.0 carries regulamin 1.0. Hydrograf,
Hydrolog and Obserwator adopt DEV-15.7 to DEV-15.12 in their own branches,
Obserwator gaining „Zgłoś uwagę”; the author sets `[nogat.operator]` and one
`terms_effective` before the three are opened.

## ECO-063 Regulamin 1.0 after its review: no IP address in any log

**Amended by ECO-066 (2026-11-13):** nginx keeps no error log instead of one
at `crit`, which still names the client of a failed TLS handshake; § 8 ust. 3
says what reaches the journal and that the access log keeps only the kind of
program.

**Decision.** Before its first publication, regulamin 1.0 is replaced by the
shortened text of a legal review of 2026-11-13, with the operator's decisions
on it, in kit 0.4.0; the version stays 1.0, since no GUI has published it. No
log of a public GUI or of its proxy, access, error or application, holds the
client's IP address (DEV-15.10): nginx logs the rejections of its limits
below the level of its error log, and the app's loggers name no client. The
processor's sentence covers the whole traffic, the IP address included, and
the processor's own security logs. § 3 says the service is not a service of
IMGW-PIB, ČHMÚ or another provider and shows their data processed, instead
of denying that the data are theirs. Three keys join `[nogat.operator]`
(DEV-18.1): `mail_provider`, the service holding the operator's mailbox,
named in § 8; `mail_transfer`, the sentence on its processing outside the
EEA; and `processor_cookie`, the sentence on a cookie the processor sets
against bots, empty while it sets none. The operator stays a private person
outside any gainful or professional activity, and liability stays excluded
except for intentional damage. Plan: `docs/plans/2026-11-13-gui-terms.md`.

**Why.** The review found that nginx writes the client's address to its
error log when `limit_req` rejects a request and that tracebacks may carry
it, which would make the regulamin's „nie zapisuje adresów IP” untrue
(RODO art. 5 ust. 1 lit. a, art. 13); that Cloudflare processes more than
addresses; and that the mailbox is a recipient of personal data (art. 13
ust. 1 lit. e). A shorter text loses no protection and is read.

**Rejected.** A regulamin that admits addresses in the error log for 14 days
(the operator keeps the promise and changes the logs instead). Gross
negligence beside intent in the exclusion of liability (the operator's
choice). A hosting processor (the server is the operator's own hardware).
The cookie sentence fixed in the text (the processor's settings are not yet
known, and the text must stay true either way). A postal address (the
operator acts outside any gainful or professional activity, which he
confirmed).

**Consequence.** Kit 0.4.0. Hydrograf, Hydrolog and Obserwator adopt the
wider DEV-15.10 with the rest of ECO-062; the operator sets the three keys,
checks the Cloudflare zone and keeps a one-page register of processing.

## ECO-064 One compact strip of provider lines per GUI view

**Amended by ECO-065 (2026-11-13):** the dialog holds the lines and the
links RD, RH and RK, without H and N.

**Amended by ECO-068 (2026-11-13):** the strip also holds GK, SK and ZK, the
short forms of G, SG and Z, and the dialog G, SG and Z.

**Amended by ECO-070 (2026-11-14):** the welcome window's „Regulamin
serwisu” is its only regulamin link, and no footer reaches the dialog.

**Amended by ECO-080 (2026-11-21):** on a screen up to 860 px wide the strip
folds to one line, unfolded in place by „więcej”.

**Amended by ECO-087 (2026-11-23):** after the kit's own lines the strip
shows the lines the GUI declares for it (`screen-lines`), such as the line
of an operator's own network.

**Decision.** A GUI view shows the providers' lines once, in one compact
strip of 12 px muted text, not under every panel, card, chart or popup
(DEV-20.5). The strip holds only the sentences the providers require on the
product, S and P for IMGW-PIB data and PS and PP for PMAXTP, with ČHMÚ in
the short form CK, „Źródło: ČHMÚ, CC BY 4.0”, linked to its open-data site
and the licence; each once in the order of DEV-20.4. It ends with „Źródła i
warunki”, a dialog with every line (H, M, the full C and CP included), the
terms notice N with RD, RH and RK, and „Regulamin” where the GUI serves one;
a GUI's welcome window shows the same on the first visit. The strip takes at
most two lines at 1440 px for one IMGW-PIB family with ČHMÚ, and a third
only in a view with both IMGW-PIB families (the five sentences measure 3306 px
at 12 px Lato, more than two lines of 1440 px). Files, exports, images, print
views, hand-offs and `attribution` and `terms_notice` keep the full lines.
The kit's `<nogat-sources>` (kit 0.5.0) derives the strip from the full
lines, so a GUI passes the API's arrays unchanged. Plan:
`docs/plans/2026-11-13-compact-attribution.md`.

**Why.** The author's request of 2026-11-13: the lines took too much of every
GUI, Obserwator's most, about six lines under the map and a block under every
card of its station panel. The legal floor stays: §5 ust. 3 and 4 of the
IMGW-PIB terms and ust. 1 and 2 of the PMAXTP terms require their sentences
on the product itself, so they stay on screen verbatim; CC BY 4.0 §3(a)(2)
lets the attribution be given in any reasonable manner, a link to a page
with the full information included, so ČHMÚ's line shrinks to a linked
short form; H, M, CP, N and the terms' addresses are not sentences the terms
require beside the data and move one click away.

**Rejected.** The lines in a tooltip, a footer link or the regulamin only
(the IMGW-PIB and PMAXTP sentences belong on the product). Shortened or
merged IMGW-PIB sentences, such as S dropped because PS starts with it (PS
names klimat.imgw.pl as the source, untrue of station data). Text below
12 px (the five sentences still need three lines at 11 px). One strip per
panel or card (the clutter the author asked to remove).

**Consequence.** DEV-20.5 and DEV-20.7 are amended and kit 0.5.0 ships
`<nogat-sources>`. Hydrograf, Hydrolog, Archiwista and Obserwator replace
their per-panel lines with one strip per view in their own branches.

## ECO-065 Products link the providers' terms and never restate them

**Decision.** A product carries only what the providers require verbatim and
links to each provider's own terms, never a summary or paraphrase of them.
The terms-of-use notice N („Dane IMGW-PIB można wykorzystywać
nieodpłatnie…”) is dropped everywhere. H („Dane pochodzą z serwisu
hydrologicznego IMGW-PIB https://hydro.imgw.pl”) is dropped too: neither
the IMGW-PIB terms nor those of hydro.imgw.pl require it, and S and P with
RH cover data of hydro.imgw.pl. The terms lines become plain links named
after the terms they open: RD „Regulamin danych IMGW-PIB:
https://danepubliczne.imgw.pl/regulations”, RH „Regulamin serwisu
hydrologicznego IMGW-PIB: https://hydro.imgw.pl/#/regulamin”, RK
„Regulamin danych PMAXTP: https://klimat.imgw.pl/opady-maksymalne”, and
`terms_notice` holds only them; ČHMÚ needs none, since C names the licence
with its link. S, P, PS, PP, M, C, CP and the on-screen CK are unchanged.
The regulamin's source blocks keep the provider's name, the required lines
and the link to its terms or licence; the block `imgw-terms` and every
description of what a provider allows are gone, and § 5 and § 6 say once
that use of data taken from the service is governed by the providers' terms
linked in § 5. The author's statement of decision 1 of ECO-062, in the
footer and § 3, stays: it describes the service, not a provider's terms.
Regulamin 1.0, still unpublished, is revised in place in kit 0.6.0. Plans:
`docs/plans/2026-11-13-provider-attribution.md`,
`docs/plans/2026-11-13-gui-terms.md`.

**Why.** The author's principle of 2026-11-13: „Tam, gdzie się da,
odsyłamy do regulaminu dostawcy danych. Treści w naszych produktach mają być
ograniczone do minimum.” N was our paraphrase and mis-stated §3 ust. 2 of
the IMGW-PIB terms: its example „planowanie w gospodarowaniu wodami, art. 317
Prawa wodnego” was our pick, and „art. 317” shortened „art. 317 ust. 1”. A
link cannot drift from the text it opens; a summary can. H was not required
(the legal review of 2026-11-13 noted it).

**Rejected.** A corrected N (still our wording of terms that only the
provider's text states bindingly). Dropping `terms_notice` and putting the
links in `attribution` (the IMGW-PIB lines and the links serve different
purposes, and every project already carries both arrays). One line linking
all IMGW-PIB terms (each product names only the terms of the data it holds).
A terms line for ČHMÚ (C already links the licence).

**Consequence.** DEV §20 loses H and N, DEV-20.4 orders S, P, PS, PP, M, C,
CP, and DEV-20.7 forbids restating a provider's terms; kit 0.6.0 carries the
shortened regulamin and `scripts/terms.py` loses the derived block. The
`handoff-1.schema.json` examples carry RK alone in `terms_notice`; the
hand-off stays `/1`. Obserwator, Hydrograf, Hydrolog, Archiwista, Hydraulik
and Retman change their constants and tests in their own branches and copy
kit 0.6.0 and the schema; files already written with H or N are rewritten
when next produced, never edited by hand.

## ECO-066 One logging convention for every server, without root

**Decision.** Every server of the ecosystem, Hydrograf, Hydrolog's GUI,
Obserwator's GUI and REST server and Archiwista, logs the same way (DEV-12.4
to DEV-12.9): access, application and lifecycle records in one JSON Lines
format, `nogat-log/1`, with fixed keys and no other; daily files
`<state_dir>/<project>/logs/<kind>-YYYY-MM-DD.jsonl` that the server itself
deletes once 14 days old, at start and at 00:00 UTC; on standard output and
error only lifecycle records and errors reduced to their type; uvicorn's
access log off and the app's middleware writing it; nginx without logs of
its own; Docker's `local` driver capped at three files of 1 MB. No log holds
an IP address, a cookie, a credential header, a request body or an uploaded
file's name; the User-Agent becomes a class, `browser`, `bot`, `script` or
`none`; query parameters that may carry personal data keep only their name;
the request id never reaches the client. `state_dir` joins `[nogat]`
(DEV-18.1), by default `platformdirs.user_state_path("nogat")`, mounted into a
container. The reference module `standards/reference/nogat_logging.py` with
the schema `schemas/log/record-1.schema.json` implements it; both are copied
byte for byte and reported by `drift`. Regulamin 1.0, still unpublished, is
revised in place in § 8 ust. 3 (kit 0.6.1). Plan:
`docs/plans/2026-11-13-unified-logging.md`.

**Why.** The author's request of 2026-11-13: „Czy możesz ujednolicić
logowanie we wszystkich aplikacjach i zdefiniować je w Nogacie?”. Four
servers logged four ways, Hydrograf's nginx and API to the system journal,
Hydrolog one line per request to the user journal, Obserwator's GUI to files
of its own and its mockup uvicorn's lines with client addresses to the user
journal, and both journals keep entries without a time limit. A time limit
in journald needs root and changes the whole host, so each server deletes
its own files, and what reaches the journal or Docker names no request. A
full User-Agent with a time and a path can single out a person (the legal
review of 2026-11-13); its class still tells robots, scripts and browsers
apart. nginx names the client in errors of a request at every level, `crit`
included for failed TLS handshakes on a server that terminates TLS, as the
dedicated server outside Cloudflare will; the app sees every request worth a
record, pages included through `X-Accel-Redirect`.

**Rejected.** `MaxRetentionSec` in journald (root, the whole host;
Hydrograf's `docker/journald.conf` was never installed). nginx writing daily
files that the API deletes (its `log_format` cannot drop query parameters,
write `duration_ms` or a time in UTC with `Z`, and would be a second writer
of one format). The full User-Agent (personal data the operation does not
need) and none at all (robots not told apart). `error_log` at `crit` (TLS
errors name the client). Logs in `data_dir` (state, not data to back up).
Docker's `journald` or `json-file` drivers (no time limit; `json-file` grows
without `max-size`). The request id in a response header (a person could
quote it and tie a record to themselves).

**Consequence.** DEV-15.10 points to DEV §12, amending ECO-062 and ECO-063;
kit 0.6.1 carries the revised § 8 ust. 3. Hydrograf, Hydrolog, Obserwator and
Archiwista copy the module and the schema and migrate in their own branches;
the journal entries written before the migration are removed as the plan
says.

## ECO-067 One admin panel for every GUI

**Decision.** A GUI that stores reports or statistics serves its admin panel
at `/admin/` and its admin API under `/api/admin/`, an app's own API prefix
kept (Archiwista's `/api/v1/admin/`), and no other admin path, so a
deployment protects exactly `/admin`, `/admin/*` and `/api/admin/*`
(Cloudflare Access on the test deployment). Every admin route checks
`X-Admin-Key` in constant time against `admin_api_key`, read per request from
`<PREFIX>ADMIN_API_KEY` or the file `<PREFIX>ADMIN_API_KEY_FILE` names
(Hydrograf no prefix, Hydrolog `HYDROLOG_`, Obserwator `OBSERWATOR_`); a
refusal is `401 unauthorized` with the reason `admin_key_not_configured`,
`admin_key_missing` or `admin_key_invalid`; no key is generated and none is
logged; an app with accounts checks its own role instead and keeps the rest.
Every panel is the kit's `<nogat-admin>` (kit 0.7.0): „Zgłoszenia”,
„Statystyki” and „Stan” on one core API of five routes, the same in every
GUI, then the app's own functions as further sections with routes of their
own under `/api/admin/`; each view also works alone inside an app's own
view. The page is the operator's, not a public view: no footer statement,
regulamin link, app menu or stats count, `noindex`, `Cache-Control:
no-store`, CSP `'self'`, the rate limit kept (DEV-15.13). Plan:
`docs/plans/2026-11-13-admin-panel.md`.

**Why.** The author's decision of 2026-11-13: the operator handles each GUI
in the same place and the same way. Each GUI did it differently. Hydrograf
had a Bootstrap page at `/admin.html`, the only Bootstrap page of the app,
with reports, resources, DEM bootstrap, cleanup and uploads, and without a
configured key it drew a random one and logged it. Hydrolog had a Preact page
at `/admin/` with reports only, its key read per request, `401
admin_key_not_configured` without one. Obserwator had no page: its reports
were read with `jq` from `feedback.jsonl`, a deviation from DEV-15.12
recorded in its `CLAUDE.md`. Archiwista showed reports in a view of its own
behind its accounts. Four paths, four sign-ins and three ways to read the
same report format left four things to protect and learn; a key written to a
log is a secret in every copy of the log.

**Rejected.** Each GUI keeping its own panel (the four ways above). A key
generated when none is set (Hydrograf's, written to its log; without a key
the routes refuse with `admin_key_not_configured`). Left out of the
decision: logs in the panel (the unified logging writes files the operator
reads directly), accounts for the public GUIs, and one admin across the GUIs
(the GUI hub, stage 2 of ECO-058).

**Consequence.** DEV-15.13 is new; DEV-15.12 sends its operator routes to
it, and DEV-15.4, DEV-15.7, DEV-15.8 and DEV-15.11 name the admin page as
the exception it was: the operator's, not a public view. Kit 0.7.0 ships
`nogat-admin.js` and `nogat-admin.css`. In their own branches Hydrolog
replaces its Preact page with the kit and adds `stats` and `status`;
Hydrograf moves `/admin.html` to `/admin/` on the kit, rewrites its own
sections on the tokens with `adminFetch`, folds its dashboard into `status`,
drops Bootstrap and its generated key; Obserwator gains
`OBSERWATOR_ADMIN_API_KEY`, the routes over `feedback.jsonl` and the page,
and drops the deviation and its `jq` instructions; Archiwista shows
`<nogat-admin-feedback>` in its own view behind its accounts. The author
sets each key and Cloudflare Access on the three paths of the test
deployment.

## ECO-068 Regulamin 1.0 corrected in place; GUGiK, ISRIC and ČÚZK lines

**Decision.** Regulamin 1.0, published in Hydrograf and Hydrolog on
2026-11-13, is corrected and published again under the same number, on the
author's decision; `terms_effective` becomes the day of the republication,
from which any change raises the version. The block `gugik` names „Główny
Urząd Geodezji i Kartografii – GUGiK” and links GUGiK's conditions of reuse
instead of the geoportal's terms; the block `esri` is gone and `copernicus`
stays for a later GUI; § 8 ust. 5 says that the basemap and the map layers
of other providers come to the visitor's browser from their servers, and a
GUI loads no script, style or font from another server (DEV-15.7).
„Historia zmian” links the template's history on `develop`, where the
published text lives. DEV §20 gains G for GUGiK data, SG for ISRIC
SoilGrids and Z for ČÚZK (DEV-20.9 to DEV-20.11), after CP in the order of
DEV-20.4, with the strip forms GK, SK and ZK that `<nogat-sources>` derives
from them as it derives CK from C, one GK naming the products of every G of
a view; a basemap loaded live from GUGiK is credited on the map
(„Ortofotomapa © GUGiK”). Kit 0.6.2. Plan:
`docs/plans/2026-11-13-terms-fix.md`.

**Why.** The published text was untrue in three places and linked terms
that do not bind: Hydrograf's results and files from GUGiK data (NMT,
BDOT10k) and SoilGrids carried no source line, though pkt 1 and 2 of
GUGiK's conditions of reuse
(https://www.gov.pl/web/gugik/ponowne-wykorzystanie-informacji-sektora-publicznego)
require its full name, the time the data were created and acquired and a
note that they were processed, and CC BY 4.0 the creator, the licence and a
note of changes; those conditions, not the geoportal's terms, bind reuse;
Hydrograf's pipeline uses no CORINE (its ADR-061), and Esri's basemaps may
be used only with Esri software or an ArcGIS subscription
(https://www.esri.com/content/dam/arcgisonline/docs/tou_summary.pdf), which
Hydrograf has not; and the flood map overlay of wody.isok.gov.pl and the
script CDNs unpkg.com and cdn.jsdelivr.net also received the visitor's IP
address. Obserwator's borders come from PRG and RÚIAN instead of Natural
Earth (the author, 2026-11-13), which needs GUGiK's and ČÚZK's lines.
`main` is released only on the author's word, so the history it linked did
not hold the published text.

**Rejected.** Version 1.1 (the author kept 1.0; the 1.1 of the logging
branch was dropped before it was pushed). A terms line for GUGiK, ISRIC or
ČÚZK (§ 5 of the regulamin links GUGiK's conditions; SG and Z name their
licence). The block `esri` kept for a later GUI (no GUI uses Esri). Scripts
from CDNs named in § 8 ust. 5 (vendored files give nobody the address). One
GK for each G (a view's strip names each GUGiK product once).

**Consequence.** DEV-20.4, DEV-20.5 and DEV-20.7 are amended, and with them
ECO-060 and ECO-064; kit 0.6.2 carries the corrected regulamin and the strip
forms. Hydrograf takes GUGiK's orthophoto instead of Esri's imagery, drops
`copernicus` and `esri`, vendors its CDN files and carries G and SG;
Obserwator builds its borders from PRG and RÚIAN and keeps `gugik` and
`cuzk`; Hydrolog copies kit 0.6.2; Hydrograf and Hydrolog publish the
corrected text on one day, Obserwator at its switch.

## ECO-069 Info texts of a GUI

**Decision.** Every info text of a GUI, behind „(i)”, in a help popover or in
a section's „Objaśnienie metod”, has one shape (DEV-15.14): a definition of
one or two sentences, then, where they apply, the formula with its symbols
and units, how to read the value and the sources. It is Polish, impersonal
and descriptive, „Ty” only in an instruction as in the regulamin; it says
nothing of the author's or operator's experience, opinions or past work,
no internal identifier, no development status, no implementation detail the
user cannot act on unless a licence requires it, and no long list of fields
or file contents; it has at most about 400 characters without the formula
and the sources, and a longer explanation of a method goes to the GUI's
guide. Units follow a space, decimals a comma, ranges an en dash.
`design/README.md` shows one example.

**Why.** The author's request of 2026-11-14: one standard and no needless
detail. The GUIs explain their values in different shapes: Hydrograf's
entries have up to twelve fields, among them a second paragraph on how
Hydrograf uses the value, and run to several hundred characters; Hydrolog's
have seven; Obserwator and Archiwista explain in titles and short
descriptions. A user who opens two GUIs reads two styles, and detail the
user cannot act on hides the definition.

**Rejected.** Each GUI keeping its own shape (one job, one way). A kit
component for info texts (the rule fixes the content; each GUI keeps its
popover and its formula typesetting). A hard character limit checked by the
gate (the texts live in each GUI's own resources, in different shapes).

**Consequence.** DEV-15.14 is added. Hydrograf, Hydrolog, Obserwator and
Archiwista revise their info texts in their own repositories (DEV-17.5),
moving method detail beyond the limit to their guides.

## ECO-070 The regulamin link in the menu, the rail and the welcome window

**Decision.** A public GUI links „Regulamin”, in a new tab, in exactly three
places (DEV-15.7): the end of the app menu, as before; a small, quiet link
at the foot of its left navigation rail, or of its left navigation where it
has no rail, kept as the last small item where the rail becomes a bottom bar
or sheet on a phone; and its welcome window, where it has one, through the
„Regulamin serwisu” that `fillSources()` writes there, never a second link.
No footer or status bar carries the link or the author's statement of what
the services are; the statement stays as the opening of § 3 of the
regulamin (DEV-15.8), whose text and version 1.0 do not change. The strip
`<nogat-sources>` and its dialog „Źródła i warunki” with „Regulamin
serwisu” stay as they are. Plan: `docs/plans/2026-11-14-no-footer.md`.

**Why.** The author's decision of 2026-11-14: the footer statement takes
space and the link is easy to reach elsewhere. The rail is in every view of
a GUI, so a link at its foot replaces the footer's as the one the app menu,
not drawn without another GUI, cannot be. The provider lines stay on screen,
since § 5 of the IMGW-PIB terms requires them on the product (ECO-064).

**Rejected.** Keeping the footer with the link alone (the space is the
point). The statement in the status bar, the welcome window or a tooltip
(the regulamin says it, one click away). The link only in the menu and the
strip's dialog (the menu is not always drawn, and a dialog about the
providers is not where a visitor looks for the service's terms). A second
link in a welcome window beside „Regulamin serwisu” (one link per place).

**Consequence.** DEV-15.7 lists the three places, DEV-15.8 keeps the
statement in § 3 only, DEV-15.13 and DEV-20.5 lose their footer; the kit
and regulamin 1.0 are unchanged. Hydrograf, Hydrolog and Obserwator remove
their footer statement and link and add the rail's link in their own
repositories (DEV-17.5); Archiwista serves no regulamin.

## ECO-071 Processing lines never name the processing

**Decision.** A processing line states that the data were processed, never how.
CP in DEV §20 is exactly „Dane ČHMÚ zostały przetworzone”, once on a
product with modified ČHMÚ data. P, PP, G, SG and Z already have this form
and do not change. A reader of an older file treats any „Dane ČHMÚ zostały
przetworzone (…)” as CP, irrespective of the words in parentheses, and
deduplicates it with the new line. Kit 0.7.1 includes CP in `LINES`, and
its sources viewer renders the canonical line when reading an old file.

**Why.** The author's decision of 2026-11-14: a processing line never
describes what was done. One fixed line is shorter, works unchanged across
products and merges without duplicates.

**Rejected.** A parenthetical summary, even a short one (the line then
varies with each producer). Leaving earlier lines unrecognised (old files
must still be readable).

**Consequence.** DEV-20.3 and DEV-20.4, the CP table entry and the ČHMÚ
example in the regulamin change. The regulamin stays version 1.0, corrected
in place (the author, 2026-11-14: only the author raises its version), with
no new `terms_effective`. Producers update their lines and copy kit 0.7.1
in their repositories (DEV-17.5); old files are not edited in place.

## ECO-072 Everything is version 1 until the first release

**Decision.** Until the first official release, Nogat's tag on `main` and
then each project's, every schema, document type, file format, protocol,
the GUI kit and the regulamin are version 1 (REL-1.4). Only the author's
consent changes a version, and only a release with its tag on `main`
confirms one. An agent never raises on its own a repository's package
version, a schema id (`<name>/N`, `<name>-N.schema.json`), a file or
database format number, a protocol number, the kit version or the regulamin
version. The kit, at 0.7.1, becomes `1.0.0` with its files unchanged, and
stays `1.0.0` until the author decides; a GUI's copy is compared with
Nogat's by the hash of each file (DEV-15.6), never by the version.

**Why.** The author's rule of 2026-11-14. Nothing has been released, so a
number raised on a branch marks no version any user could have, as ECO-056
found for the standard and its documents; the kit's eleven 0.x versions of
2026-11-12 to 2026-11-14 said only that files changed, which the hashes
already say.

**Rejected.** Raising the kit version per change (no copy is compared by
it). Keeping 0.7.1 (the kit would carry a number the author never chose).
Letting agents raise a schema or format number at a breaking change before
the release (AGI-4.1 already keeps an unreleased number).

**Consequence.** REL-1.4; AGI-4.1 raises a released number only with the
author's consent. `design/kit/nogat-kit.json` says `1.0.0`; DEV-15.7
and `design/README.md` refill a GUI's regulamin with each copy of the kit,
not each kit version. Nogat's own schemas are already `/1`. Past entries of
the CHANGELOG, the plans' results and the ECO records keep the kit versions
they named.

## ECO-073 Long jobs run outside the agent's session

**Decision.** A job that may last more than about 10 minutes runs as a user
systemd unit with its output in files, not as a background job of the
agent's session (DEV-17.6). A producer whose long command builds many
independent parts keeps the parts it has finished and resumes from them
after an interruption, where the parts' inputs are unchanged.

**Why.** On 2026-11-15 the agent's session ended during Obserwator's
`analyses build` for the deployment, at station 2332 of 3240 after about
2 hours; the build was the session's background job and ended with it, and
its next start removes the staged stations as leftovers, so the work was
lost. A user unit on a lingering account outlives the session and the
login.

**Rejected.** `nohup` or `setsid` (no state to query, no name). Shortening
the jobs (the deployment needs them whole).

**Consequence.** DEV-17.6. Obserwator resumes an interrupted
`analyses build` from its staged stations in its release 3.0.1.

## ECO-074 The author names the members of a release set

**Decision.** The members of a release set are the active projects the
author names for it (REL-6.1), not every active project with a package. The
first set holds Kartograf, Hydrograf, Hydrolog, Obserwator and Archiwista;
Retman and Hydraulik join a later set. An app among the members, Hydrograf, is
released by its own tag at the set's commits of its producers and is not
installed by `nogat`. Hydrolog's next release is 0.8.0, the version its
`develop` carries (`0.8.0.dev0`).

**Why.** The author's decision of 2026-11-15. The four GUIs share the kit,
the regulamin and one deployment, so they ship together, and Kartograf is
the producer two of them pin, whose tag their release pull requests need
(REL-2.1, REL-6.6); the rule of `import_name` would have taken Retman,
which waits for its evaluation, and left out Hydrograf, the GUI most users
reach first.

**Rejected.** Membership by `distribution.import_name` alone (the previous
REL-6.1). A registry field for membership (a set is a decision of one
release, not a property of a project).

**Consequence.** REL-6.1. `release-sets/candidate-5/members.toml` records
Kartograf, Obserwator, Hydrolog, Hydrograf and Archiwista. `set check`
still reads every consumer, so it reports Retman's and Hydraulik's pins
until they apply the set in their own sessions. Decision D3 of
`docs/plans/2026-10-31-archiwista-projects.md` and
the members named in `docs/plans/2026-10-20-first-release-set.md` are
superseded.

## ECO-075 The catalog summary is its own document

**Decision.** `<tool> commands list --json` and `<tool>_commands_list`
return the summary `<tool>-command-list/1`: one entry per command with at
least `name`, `operation_id`, `summary` and `read_only`, other fields
allowed. `<tool> commands schema --json` and `<tool>_commands_schema` return
the full catalog `<tool>-commands/1`. Nogat's `schemas/agent/` holds
`command-list-1.schema.json` beside `commands-1.schema.json` (AGI-2.4,
AGI-4.1).

**Why.** AGI-2.4 said both commands return `<tool>-commands/1`, while
AGI-5.9 called the list a summary, the registry declared
`<tool>-command-list/1` for Kartograf, Obserwator and Hydrolog, and all
three return it; the plan of 2026-11-04 left the wording to the standard.
The end-to-end run of 2026-11-15 found the conflict again. The three tools'
lists validate against the new schema unchanged.

**Rejected.** A full catalog from `commands list` (an API change in three
producers before their release, and every command's options in the first
answer of a discovery, against AGI-5.9). No schema for the summary (a
document nobody validates drifts, ECO-050).

**Consequence.** AGI-2.4, AGI-4.1. The tools copy the new schema with the
next copy of `schemas/agent/` and validate their list in contract tests;
`drift` reports the copy. No document changes its number (REL-1.4).

## ECO-076 Nogat starts at 0.1.0

**Decision.** The first `nogat` release, the first release set, is tagged
`v0.1.0`, and `develop` carries `0.1.0.dev0` until then (REL-1.1). `nogat`
stays `0.y` until every tool of the ecosystem is in a set, the tools are
stable and users have tested them; only then, and only by the author's
decision, is a release `1.0.0`. Until then HUB-7.4 numbers each release
within `0.y`. The standard's own version, 1.0 with its tag `std-1.0`
(HUB-6.1, ECO-056), is a separate number and does not change.

**Why.** The author's decision of 2026-11-16: Nogat is still in development,
and a `1.0.0` would promise users a stability that neither the set nor
its tools have yet. In `0.y` a minor release may break (REL-1.1), which
matches a set whose members still change their interfaces.

**Rejected.** `1.0.0` for the first set (it claims stability before users
have tested anything). Keeping `0.0.0` until the release (REL-1.1 asks
`develop` to carry the version of the next release).

**Consequence.** HUB-7.4. Nogat's `pyproject.toml` and the candidate's carry
`0.1.0.dev0`; the release pull request of the first set sets `0.1.0`
(REL-2.1, REL-6.6).

## ECO-077 verify-candidate runs an app on its own lock

**Decision.** `verify-candidate` runs `uv run scripts/ecosystem.py set
verify`. A member with a package runs its offline suite from its checkout in
the candidate's environment, its marker expression and coverage floor being
its own pytest and coverage settings. An app among the members (Hydrograf),
which the candidate's lock does not install (REL-6.1), runs its suite on its
own lock, whose pins of the producers `set check` holds at the set's
commits. A member whose profiles hold no `tool` (Hydrograf, Archiwista) runs
on Linux only, as its own CI does (DEV-7.7). The URL of a passing run is the
top-level `runs` of `members.toml`, from which the README is generated; `set
bump` drops it with the old commit. `set readme --check` fails when the
candidate's `pyproject.toml` installs other commits than `members.toml`.

**Why.** ECO-074 made an app a member after REL-6.5 was written, and
Hydrograf cannot share the candidate's environment: it caps `affine<3`
(its ADR-062, until pyflwdir 0.5.13) while Archiwista needs `affine>=3`.
Hydrograf and Archiwista are Linux applications until their ports, so their
suites on macOS and Windows would report the platform, not the set. The
README is generated, so the record of a run needs a place in the file it is
generated from.

**Rejected.** One lock with conflicting groups (uv `conflicts`), which would
hold two versions of `affine`, against REL-6.2. Leaving Hydrograf unverified
(it is the GUI most users reach first, ECO-074). A matrix job per member
(the members of a set change; one job per platform keeps the workflow
independent of them). A hand-edited README (the gate would call it stale).

**Consequence.** REL-6.4, REL-6.5, HUB-4.9.
`.github/workflows/verify-candidate.yml`; `release-sets/candidate-5/` holds
`pyproject.toml` and `uv.lock`.

## ECO-078 Formulas are declared once, checked at their limits and verified

**Decision.** A project that computes (`computes: true`) declares each Tier A
formula once, in code, by a `FormulaSpec` of Nogat's reference module
`nogat_formulas.py`, copied byte for byte; the spec drives the run-time checks,
the generated range, type and property tests, and the generated cards and
`docs/FORMULAS.md`. Physically impossible input and a failed precondition are
refused with `validation_error`; input outside the applicability range gives
the result with the notice `outside_applicability`; a formula never returns a
non-finite or impossible value. Evidence is at least two of reference cases,
oracles and properties; R and other external tools are frozen oracles stored as
data; tables are transcribed twice; mutation testing gates releases for
Tier A. A gross defect (CMP-9.1) is released at once (CMP-9.2).

**Why.** The author, 2026-11-18: correctness of the formulas is the
ecosystem's foundation and academics will audit them; tests must cover
typical, extreme, boundary and out-of-range inputs, declared types, numerical
traps and impossible values. The author chose error for impossible input and
a warning outside applicability, every project that computes as the scope, the
definition of a gross defect, and open sources first. Fable reviewed the first
draft: one declaration instead of a card beside the code (a range written
twice will differ), tiers (auditors' time goes to Tier A), preconditions as a
third class, generated tests (a hundred formulas times every input and kind of
value cannot be written by hand consistently), frozen oracles (R in CI is
fragile and hides versions), double transcription of tables (the riskiest
artefacts), `formula_version` on stored results (a defect's results must be
found), and verification kept apart from validation.

**Rejected.** Hand-written TOML cards reconciled with the code by a test
(checks only what it enumerates). A card per unit conversion (one units table
instead). Running R in the tests. Withdrawing an `unreferenced` formula from
the public interface (an `info` notice instead: Hydrolog's users rely on
formulas that no open worked example covers yet). Propagating the
uncertainty of empirical formulas and tables of sensitivity (research, not
verification). A wrong equation or constant only in a document, with correct
code, as a gross defect (it misleads no result; a wrong unit or range stays
gross).

**Consequence.** CMP §1 to CMP §9, HUB-2.1 (`computes`). Plan
`docs/plans/2026-11-18-computation-standard.md`.

## ECO-079 An operator's instance: its name and logo beside the mark, its own regulamin

**Decision.** An instance of a GUI that an operator other than the author
runs on its own infrastructure may show the operator's logo and name in the
top bar beside the project's mark; the project's mark stays as the favicon
and first in the top bar and is never replaced, and the logo is a file of
the deployment served from the GUI's own origin (DEV-15.3). Such an instance
serves the operator's own regulamin in place of regulamin 1.0, which names
the author as a private, non-commercial operator and stays for the author's
instances with the statement of DEV-15.8 (DEV-15.7). The kit carries a
draft for operators, `nogat-terms-operator.md`, in the Markdown and with the
fields and data-source blocks of regulamin 1.0, so a GUI builds and fills
it the same way: the operator is the service provider and the controller of
personal data; the software is provided as is under its licence, without
warranty or liability for availability, data or results; keeping the data
providers' terms (DEV §20) is the operator's; the author's part ends with
the deployment; the operator handles contact and complaints. The draft is a
template, not legal advice, and says so; a lawyer of the author's choice
reviews it before an operator gets it. Plan:
`docs/plans/2026-11-21-obserwator-instance.md` (I14, I15).

**Why.** The author's answers of 2026-11-21: a client runs Obserwator on his
own infrastructure with his name and logo; the payment is only for the
deployment, operating the instance is the client's, and so is the
regulamin, for which the author prepares only a draft that protects his
interests. The project's mark names the software and keeps the family of
tools recognisable (ECO-055); the operator's name tells a visitor who runs
the service. A logo from the GUI's own origin needs no new origin in the
CSP and keeps DEV-15.7's rule that a GUI loads nothing but maps from other
servers. Regulamin 1.0 does not invoke the act on electronic services,
since its operator acts outside any gainful activity (ECO-062); an operator
in business is a service provider under that act, so the draft adds the
technical requirements, the conclusion of the contract and complaints.

**Rejected.** The operator's logo in place of the project's mark or as the
favicon (the instance would pass for another product). A logo loaded from
the operator's server (a remote resource and a new CSP origin). Regulamin
1.0 filled with the operator's values (its § 2, § 3 and § 8 would state what
is false for him). A regulamin the author writes and keeps for each client
(the author does not operate the instance and gives no legal advice). A new
kit version for the added draft (only the author changes it, REL-1.4).

**Consequence.** DEV-15.3, DEV-15.7 and DEV-15.8 are amended. The kit adds
`nogat-terms-operator.md` with its hash; its version stays `1.0.0` until the
author decides (REL-1.4). Obserwator implements both for `v3.1.0` (plan
steps 2 to 4); another GUI adopts them when an operator needs it
(DEV-17.5).

## ECO-080 The sources strip folds to one line on a phone

**Decision.** On a screen up to 860 px wide, the kit's phone, the strip of
`<nogat-sources>` takes one line (DEV-20.5): its on-screen lines start on it
in the order of DEV-20.4 and are cut with an ellipsis where they no longer
fit, then come the button „więcej” and „Źródła i warunki”. „więcej” shows
only while the line cuts them; it unfolds the strip in place, wrapped as on
a wider screen, and then reads „zwiń”. A wider screen is unchanged. The
element keeps the state as its attribute `expanded` and marks a cut line
with `clipped`. Plan: `docs/plans/2026-11-21-phone-sources-strip.md`.

**Why.** The author's decision of 2026-11-21: Obserwator's view „Stacje” on
an iPhone 13 (390 × 844 px) gave the wrapped strip 127 px, five lines over
the map. Folded, the lines still begin on the product and one tap shows
them whole where they stand, so the IMGW-PIB and PMAXTP sentences are never
only in the dialog, which ECO-064 rejected. The remaining risk, named to the
author: § 5 ust. 3 and 4 of the IMGW-PIB terms and ust. 1 and 2 of the
PMAXTP terms want their sentences on the product, and the folded line shows
their beginning only.

**Rejected.** The strip as „Źródła i warunki” alone on a phone (the
sentences behind the dialog, as ECO-064 rejected). The lines kept wrapped
and the strip moved below the view's content (the author's choice). A fold
wider than a phone (a desktop strip takes at most three lines, ECO-064).

**Consequence.** DEV-20.5 is amended. The kit's `nogat-sources.js` and
`nogat-sources.css` change with their hashes; its version stays `1.0.0`
(REL-1.4, ECO-072). Obserwator and Hydrolog copy them for `v3.1.0` and
`v0.9.0`, Hydrograf and Archiwista with their next change.

## ECO-081 The kit becomes 1.1.0 with Nogat 0.2.0

**Decision.** The GUI kit's version becomes `1.1.0` in
`design/kit/nogat-kit.json`, confirmed by Nogat's `v0.2.0` on `main`
(REL-1.4). Every GUI of the round copies the manifest with the kit's files.

**Why.** The author's decision of 2026-11-21 („5 - zgodnie z propozycja”).
Kit `1.0.0` was released with Nogat `v0.1.0` and `v0.1.1`; since then the
kit gained a file, the draft regulamin for operators (ECO-079), and a
behaviour, the strip folded on a phone (ECO-080), with no file removed and no
attribute or event of an element changed, so the change is minor.

**Rejected.** Keeping `1.0.0` (a released number would name two different
sets of files).

**Consequence.** ECO-072's rule stands: the version moves only with the
author's consent and copies are compared by their hashes (DEV-15.6); the
manifest's own hash changes, so `drift` names every GUI copy until it is
refreshed. Obserwator, Hydrolog, Hydrograf and Archiwista copy it for the
round's releases. The regulamin stays 1.0.

## ECO-082 Providers named by their national acronyms; two attribution columns in a CSV

**Decision.** An identifier naming a data provider uses its national
acronym without diacritics and without its legal suffix (DEV-2.5): ČHMÚ is
`CHMU` / `chmu` where the code said the English `CHMI` / `chmi`, in
Obserwator's provider id, dataset keys `cz.chmu.*`, slugs `chmu_*` and the
store directories named by them, in Nogat's registry ids `chmu` and
`chmu-json/1` and in the regulamin's block `chmu`; IMGW-PIB is `IMGW` /
`imgw` where the code said `IMGW-PIB` / `imgw-pib` (Obserwator's provider
id, Nogat's registry id, file names), its `pl.imgw.*` keys unchanged (the
author, later the same day: „IMGW-PIB moze byc skracane do IMGW”); every
slug and store directory of one provider starts with its acronym, so
IMGW-PIB's `hydro_daily` becomes `imgw_hydro_daily` and its catalog moves
from `stations/versions` to `stations/versions/imgw_stations` beside
`chmu_stations` (the author: „katalog serii tez do ujednolicenia”). Text for
people keeps „IMGW-PIB” and „ČHMÚ”, and the provider's addresses
(`opendata.chmi.cz`) stay. A CSV's attribution columns are `attribution`
and `terms_notice` only (DEV-20.5): `attribution_source` and
`attribution_processed` go. No old name is accepted as input beside the new
one; files a tool stored under an old name are read under the new one, so
they need no download again. Every schema and format stays `/1`. Plan:
`docs/plans/2026-11-21-national-provider-names.md`.

**Why.** The author's decision of 2026-11-21: the code mixed the Polish
acronym of IMGW-PIB with the English one of ČHMÚ. The two dropped columns
repeated the first two cells of `attribution` (the stations export of
2026-11-21: S and P for IMGW-PIB, C and CP for ČHMÚ). The ecosystem is
still in development, so the change is minor and keeps `/1`.

**Rejected.** The English acronyms for both providers (IMGW-PIB has none in
use). Aliases for the old names (a second way, ECO-056). The two columns kept
beside `attribution` (the same lines twice). A new major version of the
formats (the author's choice for a development stage).

**Consequence.** DEV-2.5 is new; DEV-20.5 and DEV-20.6 are amended, and with
them ECO-060. The kit's `nogat-terms.md`, `nogat-terms-operator.md` and
`nogat-terms.html` change with their hashes; its version stays `1.1.0`
(ECO-081). A GUI that lists the block `chmi` is refused until it lists
`chmu`. Obserwator, Hydrolog, Archiwista and Hydrograf follow in their own
branches (plan steps 2 to 5); Hydrolog still reads the two old columns in
files written before, as lines, not data. Dated records keep the old names.

## ECO-083 One pattern for the files a tool names for a user

**Decision.** A file whose name a project chooses for a user (a GUI's
download, a REST attachment, a file a command writes into `output_dir` under
a name it picks) is named `<tool>_<content>_<qualifiers>.<extension>`
(DEV-19.21): the registry name first, the content in English words joined by
`-`, the qualifiers after `_` with identifiers unchanged, ISO dates and a
person's text reduced to lower-case ASCII with `-`, only ASCII letters,
digits, `.`, `-` and `_`. The kit's statistics file becomes
`<project>_stats_<first>_<last>.csv` (`nogat` when the element names no
project, as the shell does) and its hand-off file
`<producer>_handoff_<subject>.json`, the producer being the envelope's
`producer.tool`, which the schema requires; `nogat-handoff.js` exports the
reduction of a person's text as `nameSlug`. Plan:
`docs/plans/2026-11-21-download-file-names.md`.

**Why.** The author's decision of 2026-11-21 („Cały ekosystem w tej
rundzie”, „Angielskie”, „Tak, z nazwą narzędzia na początku”), after
Obserwator's station list: each tool named its files its own way, with
Polish and English words, `-` and `_`, the tool's name and the station's
code each in a different place, and a downloads folder did not tell which
tool wrote a file. The hand-off loses `.handoff.json`: no reader needs the
suffix, since the kit's `readFile` reads any picked file and Hydrolog's
pickers accept `.json,application/json`, and the content word `handoff`
marks the file as the suffix did, so a second pattern for one kind of file
is not kept. The subject, a person's text, was kept with spaces and
diacritics, which the rule leaves out of names.

**Rejected.** Polish content words (the code, the schemas and the
identifiers are English, DEV-2.1). Names without the tool's name (the
author's choice). `<subject>.handoff.json` kept as an exception (a reader
would need it, none does). The tool's name last (the author's choice). `-`
between the parts (content words, dates and a person's text hold `-`, so the
parts could not be told apart).

**Consequence.** DEV-19.21 is new and DEV-15.5 is amended. The kit's
`nogat-admin.js` and `nogat-handoff.js` change with their hashes; its
version stays `1.1.0` (ECO-081). Obserwator, Hydrolog, Hydrograf and
Archiwista rename their downloads, attachments and default output names in
their own branches and copy the kit (plan steps 2 to 5), with their
manuals and labels that name `….handoff.json`; Kartograf keeps the names
of plain mode (DEV-19.5). No old name is kept beside a new one.

## ECO-084 Operational data are kept as captures of an unverified tier; serving them is the operator's decision

**Decision.** Every answer a provider adapter of Obserwator receives —
archive and file downloads, files an operator feeds, API answers, the GUI's
live fetches, warnings and water-state classes included — is written to the
raw root as it came, with an `obserwator-meta/1` sidecar (the time, the
address without any credential, the provider, the licence, the tier and the
publication state). Polled answers are gathered per source and UTC day into
one capture version of a dataset whose `tier` is `operational` (`telemetry`
for IMGW-PIB's monthly telemetry; `verified` for the published archives and
validated sets); a capture is an archive version of the raw root like any
other (`archive:<key>:<YYYY-MM-DD>`), not a kind of its own. Operational
tiers are stored, shown and exported only as such; in a derived series a
higher tier replaces a lower one by precedence per point, and the captured
answers stay. Per source the deployment's `nogat.toml` says `public` (shown
and downloadable in Obserwator and Archiwista) or `private` (stored; read by
the operator's CLI and library and by Archiwista's signed-in users only);
the default of a source follows its terms and is shown in `config show`. The
rate at which a source is polled is a ceiling its adapter declares; the
deployment's timers may run slower, never faster. DEV-20.8 is amended
accordingly. ECO-059 is amended in three points: Obserwator's commands run
by the deployment's user systemd timers write the raw root beside the
downloads Archiwista orders; operational data are archived as captures; the
backup copy of the raw and data roots is the deployment's `rsync` timer,
documented by Obserwator (DEV-18.5), not an Archiwista job. Nothing is
deleted; superseded derived versions may be pruned on an explicit command
only, by a later plan. Plans: `docs/plans/2026-11-16-operational-series.md`,
`docs/plans/2026-11-20-hydromet-providers.md`.

**Why.** The author's decisions of 2026-11-22: „potrzebne jest mi… archiwum
na wszystko co przychodzi”; „To nadal nie jest działalność gospodarcza, bo
mój serwis jest darmowy, nie ma reklam, nie zarabia […] jest to decyzja
operatora, nie moja”; „częstotliwość powinna być dostosowana do źródła”;
„timer systemd”. hydro.imgw.pl forgets its operational data after six weeks
and IMGW-PIB publishes no sub-daily verified set, so a nightly capture is
the only continuous record up to yesterday; a client's instance runs
Obserwator and Hydrolog without Archiwista, so the schedule cannot live in
Archiwista's queue.

**Rejected.** Keeping only what a series needs (the author wants the whole).
A capture beside the adapter (a provider could forget it). A raw-root kind
of its own for captures (Archiwista 0.3.3 indexes archive versions already;
a new kind would break its scan). A rule in the code that forbids serving a
source (the operator's decision, not the software's). One polling rate for
every source. The schedule in Archiwista's queue (an instance without
Archiwista would lose it).

**Consequence.** DEV-20.8 and ECO-059 read as above; `obserwator-store/1`
and `obserwator-meta/1` stay `/1` (the optional sidecar fields `tier` and
`publication`, ECO-085). Obserwator records the captures, the tiers and the
GUI's spool in an ADR amending ADR-003 D4, ADR-013 D5 and ADR-015 D5;
Archiwista shows the tier and the publication state of a version (its A1)
and honours `private` in its downloads in a later minor. The pruning of
superseded versions and Archiwista's pins wait for the plan of `store prune`
(`v3.5.0` at the earliest).

## ECO-085 Additions within version 1 of a released document

**Decision.** A released document, store layout or identifier grammar stays
at its `/N` when a change only adds an optional field (AGI-4.1), a new value
of an existing field, or a new form of an identifier (a slot, a directory
name, a time unit), provided that a reader of `/N` that does not know the
addition can leave that entry out without failing, and that every consumer
in the registry that distinguishes by the field is changed in the same plan,
released in the same round, producers first (HUB-5.2), and deployed on a
shared store before the producer writes the addition there. A change that
alters the meaning of an existing field or value, or that an unknowing
reader cannot skip, increments `/N` with the author's consent (REL-1.4).
First uses: `time_unit` `hour` and the monthly slot `series:<key>:<YYYY-MM>`
of `obserwator-series/1` and `obserwator-data/1` (Archiwista's adapter
changed in the same plan); the fields `basins` and `parts` of Hydrograf's
`instance.json` (plan `2026-11-16-large-basins.md`, topic 1).

**Why.** AGI-4.1 settles fields, not values or forms, and two plans asked
the same question (Q8 of the operational-series plan, topic 1 of
large-basins). The author's position of 2026-11-21: „Na razie zostajemy we
wszystkich schematach przy `/1`, bo jest to wciąż wersja rozwojowa”.
Archiwista 0.3.3 shows the condition is not empty: its adapter refuses a
series of an unknown `time_unit` (`source.obserwator_series_unit`) and its
index's `CHECK (time_unit IN ('day', 'month', 'half_year'))` would reject
the row, so a new value is additive only when the consumer is changed first.

**Rejected.** A `/2` for every new value (every consumer would follow a
number for a change it can skip). Any new value as additive without the
consumer condition (the Archiwista case above).

**Consequence.** AGI-4.1 gains one sentence: „A new value of an existing
field or a new form of an identifier is additive under the conditions of
ECO-085.” A consumer that reads a shared store treats an unknown value it
cannot show as a skipped entry with a warning record, not as a failure
(Archiwista does so from its A1). The second plan to merge takes the next
free ECO number (as PROGRESS numbering, Q12).

## ECO-087 Provider lines in one table; a GUI declares a line the kit does not know

**Decision.** DEV §20 gives the providers' lines in one table of provider
lines, a row per line a provider requires with its data: the code of its
text and, after it, that of its processed text; the text; the processed
text, which a product adds once the data were processed; and the order.
DEV-20.4 orders a product's lines by that order, each text before its
processed text, so a new provider is a row, not a rule; the short forms of
the strip and the terms lines keep tables of their own, and every existing
line keeps its code and its wording. The line of a provider the table does
not hold, which a deployment declares for its own network (an operator's
instance), follows every line of the table, in the order the deployment
declares, its text before its processed text. The kit's `<nogat-sources>`
shows such a line, or any other line of the view's data, on the strip when
the GUI declares it: the attribute `screen-lines` (JSON) or the property
`screenLines` holds `{text, short, links}` per line; a declared line is
shown when the view's `attribution` carries its `text` byte for byte, after
the kit's own lines, in the order declared, as `short` where given, its
`links` (a word and an http or https address each) linking words of it,
else with its addresses linked; a line the kit shows itself is not shown
twice, and without the attribute every rendering stays as it was (DEV-20.5).
Plans: `docs/plans/2026-11-20-hydromet-providers.md` (P9),
`docs/plans/2026-11-21-obserwator-instance.md` (I13).

**Why.** P9 of the plan of hydro-meteorological providers (approved
2026-11-23, Fable for the author): offices, municipal companies and
universities join as providers, and a rule each would grow DEV §20 by a
rule per provider; the author's decision of 2026-11-23 that Nogat's
`develop` takes the producer steps the other projects need moves the table
ahead of the plan's step 5. Obserwator's provider fed by files (I13,
`v3.3.0`) declares its line in a provider file beside `nogat.toml`, but the
kit showed on the strip only the lines it knows (S, P, PS, PP and the short
forms), so that line would reach only the dialog; the author kept the kit's
order of the strip on an operator's instance and marks the featured
provider on the map instead (I6, 2026-11-21). A declaration by the GUI
keeps every operator's text out of the kit and keeps that order.

**Rejected.** A rule per provider (P9). An operator's line before G, SG and
Z, or first on the strip (its place would move as the table grows, and the
author kept the kit's order). Child elements of `<nogat-sources>` (the
element redraws its children from its attributes). The kit holding the
lines of operators (its code would name a client). A short form a GUI
invents for a line of the table (only the table's short forms shorten its
lines).

**Consequence.** DEV §20, DEV-20.4 and DEV-20.5 read as above; every code
and every line stays, so no product changes. The kit's `nogat-sources.js`
changes with its hash. Obserwator declares the line of its provider fed by
files for `v3.3.0`; Gdańskie Wody gets its row once its terms give the
wording (P9).
