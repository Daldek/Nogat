# Adoption plan for standard 2.1

Part of standard 2.1 · no requirement IDs

Each item names the requirement it implements. Work happens in later
sessions, one project per session, on a `docs/standard-2.1` or
`chore/standard-2.1` branch, with the author's approval for merges, tags,
force-pushes and history rewrites (DEV-3.3); pushing the topic branch needs
none. The phases run in order: 0 Nogat, 1
history rewrite, 2 tooling, 3 documentation, 4 agent interfaces, 5 releases
as git tags, 6 PyPI.

---

## Phase 0: Nogat

| # | Item | Requirement |
|---|---|---|
| 0.1 | Templates: the gate and CI templates are in `standards/ci/` (done); document templates and configs replace the v1 `standards/templates/` and `standards/configs/`, which are owned by root, so the author replaces them; until then the v1 files are not valid | DOC-11.1, DEV-7.6, DEV-7.7 |
| 0.2 | Registry (`ecosystem.yaml`, schema, `scripts/ecosystem.py`, generated `docs/ECOSYSTEM_MAP.md`) and the hub README in English (done) | HUB §2, HUB §4, ECO-005 |
| 0.3 | Pending Nogat work committed in small Conventional commits as Daldek on a topic branch and merged by pull request | DEV-4.1, DEV-4.2, DEV-3.3 |
| 0.4 | Standard 2.1 merged to `main` and tagged `std-2.1` | HUB-6.1, ERR-3 |
| 0.5 | Nogat `CLAUDE.md` and generated `AGENTS.md`, both done: the routing table with links to the tools' AGENTS.md | DOC §3, DOC §4, HUB-4.3 |
| 0.6 | Ruleset for `main` and `develop`, tag ruleset for `v*`, private vulnerability reporting, contribution files (`SECURITY.md`, `CONTRIBUTING.md`, `docs/CLA.md`, `CONTRIBUTORS.md`, pull-request template with the CLA box) | DEV-3.6, DEV-13.7, DEV-16.2, DEV-16.4 |

## Phase 1: identity and history (one-off)

Preconditions, checked per repository before starting:
- no uncommitted changes and no stash, which `git-filter-repo` does not
  rewrite. On 2026-10-19: Hydrolog 42 changed files, Hydrograf 1, Hydraulik 8
  plus its worktree, IMGWTools 1 stash;
- local-only commits pushed or consciously included. On 2026-10-19: Hydrograf
  67, IMGWTools 15, Hydrolog 3, Kartograf 1;
- the rewrite happens before any release tag of phase 5, because tags created
  earlier would move.

Procedure per repository (ECO-007), proven in a dry run on mirror copies on
2026-10-19:
1. `git bundle create <backup>.bundle --all` outside the repository.
2. Fresh `git clone --mirror`.
3. `git-filter-repo` with a mailmap. Every identity, `Claude <agent@local>`,
   `Claude <noreply@anthropic.com>` (Claude Code web sessions) and the Daldek
   variants `piotr.de.bever@gmail.com`,
   `38719982+Daldek@users.noreply.github.com` and `Piotr <…noreply…>`,
   becomes `Daldek <git@debever.pl>`. A message callback removes
   `Co-authored-by:` lines naming Claude, Anthropic or Copilot,
   `Claude-Session:` lines and "🤖 Generated with [Claude Code]" lines. The
   third-party author `PL1B5J <1b5j@sweco.dk>` stays.
4. Verify: zero AI trailers, zero foreign identities, same commit count, the
   tree of every branch and tag equal to the original.
5. Force-push branches and tags (approval).
6. Re-synchronise every working copy, worktree and other machine (reset to
   the rewritten branches); delete stale local branches.
7. Remap SHA references in current documentation with the commit map
   (roughly 890 backticked hashes in Kartograf, 93 Archiwista, 59 Retman, 56
   Hydrograf, 25 IMGWTools; approximate counts).
8. Update SHA pins in consumers (Retman `pyproject.toml` and `uv.lock`).

Out of reach: old commits stay reachable on GitHub through IMGWTools pull
request #1 until GitHub Support removes them. Five GitHub-signed IMGWTools
commits lose their signature.

Retman, Archiwista and Nogat need only DEV-4.2. Nogat's 8 commits use the
noreply address and are included in step 3 if the author wants a single
address everywhere; its ruleset (phase 0) is then disabled for the push and
re-enabled afterwards, and the author notes it in PROGRESS (DEV-3.6).

## Phase 2: repository structure and tooling

| Project | Items |
|---|---|
| all | `develop` carries `X.Y.Z.devN` of the next release and the CHANGELOG `[Unreleased]` section (REL-1.1); local git identity (DEV-4.2); `.editorconfig` and `.gitattributes` (DEV-14.1); `scripts/gate.sh` and `scripts/check-commits.sh` from `standards/ci/` (DEV-7.6, DEV-4.5); CI (DEV-7.7); Dependabot for Actions, Dependabot security updates and `pip-audit` (DEV-13.6); rulesets for `main`, `develop` and `v*` tags (DEV-3.6); `SECURITY.md` and private vulnerability reporting (DEV-13.7); contribution files (DEV-16.2, DEV-16.4); uv and `uv.lock` (DEV-6.2, DEV-6.3); markers `live`, `db`, `slow` and the `tests/` tree (DEV-10.1); coverage floor (DEV-7.5) |
| tools (Kartograf, IMGWTools, Hydrolog, Retman, Hydraulik) | shared settings, data and cache directories, variable names, credentials from the environment, `<tool> config show --json` and backup notes for versioned stores (DEV §18) |
| producers of stores and files (Kartograf, IMGWTools) | public `<package>.testing` module; consumers' contract tests use it (DEV-10.6) |
| Kartograf | `src/` layout (ECO-011); mypy per-module overrides listed in `CLAUDE.md` (DEV-7.3); `docs/DECISIONS.md` CRLF → LF (DEV-14.1) |
| Hydrolog | Black and flake8 → ruff (ECO-009); `src/` layout; package data test for agent templates (DEV-5.4) |
| IMGWTools | branches `master`/`slave` → `main`/`develop`, default branch on GitHub (ECO-008); pyright → mypy (ECO-010); links in `llms.txt` and docs from `master` to `main` |
| Hydrograf | uv and lock for `backend/` (replaces pinned `requirements.txt`, keeps documented caps); gate beyond ruff-only pre-commit; mypy in CI |
| Hydraulik | commit the proof of concept from the worktree into `develop` (DEV-3.5, author's decision); `main` as default branch; mypy; English identifiers in `roads.py` (DEV-2.4); state in README/CLAUDE.md that SFINCS is external and not distributed (ECO-041) |
| Retman | `src/` layout; logging (DEV §12) |
| Archiwista | `src/` layout; `requirements.lock` → `uv.lock`, with Kartograf pinned by commit instead of installed editable (REL-5.3); `main` pushed and made the default branch on GitHub (ECO-008) |

## Phase 3: documentation

| Project | Items |
|---|---|
| all | translate documentation to English, project by project (ECO-005); required files (DOC-1.1); README (DOC §2) and `CLAUDE.md` (DOC §3) within their budgets (DOC-1.7), `CLAUDE.md` with a "Deviations" section (DEV-1.2); `docs/PROGRESS.md` as Status, Next and Open questions (DOC §6); ADR files (DOC §8); `docs/DEVELOPMENT_STANDARDS.md` deleted, its deviations moved to `CLAUDE.md` (DEV-1.3); new plans in `docs/plans/` (DEV-17.4) |
| Kartograf | remove the "no AGENTS.md" rule; generate AGENTS.md (ECO-014); `llms.txt` to link-list format with raw links (DOC §5) |
| IMGWTools | `CLAUDE.md` (587 lines) and README (~830 lines) within budget |
| Hydrolog | README (~810 lines) within budget |
| Hydrograf | PROGRESS (145 KB) cut to its three sections; `notes/superpowers/*` into `docs/plans/`; `CROSS_PROJECT_ANALYSIS.md` migrated into the Nogat registry and `request` issues in the producers' repositories (DEV-17.5) |
| Hydraulik | full documentation set; `CLAUDE.md` beyond 25 lines; CHANGELOG |
| Retman | AGENTS.md, llms.txt |

## Phase 4: agent interfaces

| Project | Items |
|---|---|
| Kartograf | envelope `kartograf-result/1` with `status` (AGI-4.2); errors on last stderr line (ECO-019); registry mapping (ERR §4); MCP tool prefix `kartograf_` (ECO-018), annotations, `outputSchema`, English descriptions with when/when-not (AGI §5); `commands guide` generator (AGI §8); shared option names (AGI-3.4) |
| IMGWTools | MCP prefix `imgw_` and annotations; `forbidden` exit 12; agent surfaces always English (AGI-9.2); OpenAPI `operationId` = catalog ids (AGI-6.2) |
| Hydrolog | registry numbers (13, 12); finish catalog fields (AGI-2.2); MCP per AGI §5 |
| Hydrograf | REST problem+json with registry codes (AGI-6.3); OpenAPI ids (AGI-6.2) |
| Hydraulik | catalog, `--json` envelope, registry codes for the CLI; job and result JSON Schemas kept as domain documents (`hydraulik-<kind>/1`) |
| Retman | registry codes for exits; consume tools through `list_commands`/`command_schema`/`run_command` (AGI-2.1) instead of per-tool handlers where possible |
| Archiwista | problem+json with registry codes (AGI-6.3); OpenAPI ids (AGI-6.2) |
| all tools | `pyproject` metadata for discovery: keywords, classifiers, project URLs (AGI-10.1); copy of `schemas/agent/` and contract tests that validate the envelope, error documents and catalog against it (AGI-4.1); catalog published as `<tool>-commands/1` (the registry's `*-catalog` ids follow, HUB-2.5) and MCP catalog tools `<tool>_commands_list`/`<tool>_commands_schema` (AGI-5.9) |

### Data output (DEV §19)

Detail and state per project: [data output](../docs/plans/2026-10-24-data-output.md).
A producer does this after its own standard 2.1 items; a consumer after the
producers' development heads have it.

| Project | Items | State on 2026-10-25 |
|---|---|---|
| Kartograf | `--output-dir` (`-o`) for plain files and `--root` for the store instead of the store-only `-o`; `root` for every store-root parameter, `Project.output_dir` included; default root `<data_dir>/kartograf`, `KARTOGRAF_ROOT`, cache in `<cache_dir>/kartograf`; plain mode with preflight, `.kartograf-incoming/` and `--force`; newest full flight for PL sheets in plain mode; `--check` instead of `--check-updates`; marker `kartograf-store.json` and `store init`; nested-store check by marker names; `files[]` and `skipped[]`; `producer` and `producer_version` in `kartograf-meta/1`; a new ADR supersedes ADR-048 of the branch `claude/vigilant-faraday-finqvd` (DEV-19.1 to DEV-19.19, DEV-18.2) | in progress on `feature/data-output`: ADR-054, `root`, the default root, the marker and `store init`, `--check`, `producer`, `files[]` and `skipped[]` are committed; plain mode, the `output_dir`/`root` group and the documents are open |
| IMGWTools | `--output-dir` (`-o`) for the plain download, `--output` for exports instead of `--path`; plain mode with preflight, `.imgw-incoming/` and `--force`; default root `<data_dir>/imgw` and `IMGW_ROOT` instead of `IMGW_STORE_ROOT`; marker with `tool` and `producer_version`, created by the first write, `store init` verifying the layout; nested stores by marker name only; `files[]` with the status `new` instead of `created` (DEV-19.1 to DEV-19.19, DEV-18.2) | done on `feature/data-output` (ADR-007, consumer migration guide in its CHANGELOG) |
| Archiwista | `root` for Kartograf store roots in the adapter, the read-API contract test, the store fixture (with the marker) and SPEC §12 (DEV-19.1, DEV-19.12) | not started: waits for Kartograf's development head |
| Retman | `root=` in the Kartograf calls of the client and handlers (DEV-19.1) | the IMGWTools calls are migrated on `feature/imgwtools-data-output` (ADR-024); the Kartograf calls wait for Kartograf |
| Hydrolog | documents only: the Kartograf examples in `docs/INTEGRATION.md` and the agent guide use `--output-dir` and `files[].path` (DEV-19.1, DEV-19.19) | done on `chore/nogat-2.1`; the names are confirmed when the producers' releases land |
| Hydrograf, Hydraulik | after the first release set: calls of `DownloadManager` and `kartograf download` follow the new names (DEV-19.1) | Hydraulik is done ahead of the set on `feature/sfincs-swmm` (`terrain download` runs `kartograf` with `--output-dir`; not yet run against the real Kartograf); Hydrograf follows the first release set |

## Phase 5: releases as git tags

Detail: [first release set](../docs/plans/2026-10-20-first-release-set.md).
Until the rename of phase 6, a pin names each distribution as the tag's
`pyproject.toml` spells it.

| # | Item | Requirement |
|---|---|---|
| 5.1 | Consumers that cannot run on a producer's development head migrate on a branch that pins the producer's commit, and declare the range from the producer's development version | REL-5.3, REL-5.6, DEV-3.4 |
| 5.2 | `verify-candidate` workflow in Nogat, merged to `main`; candidates, fixed and repeated until the run is green | REL-6.4, REL-6.5 |
| 5.3 | Member releases, producers first (release pull request, merge commit, annotated tag); commit pins replaced by tags and supported ranges narrowed to the release | REL-2.1, REL-5.6, REL-6.6 |
| 5.4 | `nogat` package (`src/nogat/`, the commands of HUB-7.3, the members' commands in `[project.scripts]`, dependency list generated from the lock), released as a git tag | HUB §7, REL-6.6, ECO-026 |
| 5.5 | Ecosystem user documentation `docs/user/` with executable recipes | DOC §12 |

## Phase 6: PyPI

| # | Item | Requirement |
|---|---|---|
| 6.1 | Trusted Publishing workflows; each distribution renamed to `nogat-<project>`, with consumers changing name and pin together; IMGWTools publishes a final `imgwtools` release that points to `nogat-imgwtools`, with no code shim; the MCP start form `uvx --from "nogat-<project>[mcp]" <tool>-mcp` and the `packages` entry of `server.json` are settled in the same step | REL-2.2, REL-3.1, ECO-022, ECO-020, AGI-5.1, REL-4.1 |
| 6.2 | First PyPI releases of the members; the first upload reserves each name | REL-3.1, REL-2.1 |
| 6.3 | `server.json` and MCP Registry entries for the MCP servers (Kartograf, IMGWTools, Hydrolog) | REL §4 |
| 6.4 | Consumers switch from git tags to PyPI ranges | REL-5.2 |
| 6.5 | `nogat` on PyPI once every member is there: a new candidate verifies the renamed releases, and the release depends on exact PyPI versions | REL §6, HUB-7.1, HUB-7.2 |

## Ordering constraints

- Phase 1 before any release tag, because tags created earlier would move.
- Phase 2 before phase 5: verification needs `uv.lock`, testing modules and
  `config show` in the members.
- Phase 4 before phase 5, so the first set carries the breaking interface
  changes (ECO-020) instead of being replaced at once.
- Producers before consumers in phases 4 to 6, in the dependency order of
  `ecosystem.yaml`.
- DEV §19: Kartograf and IMGWTools in parallel, each after its own standard
  2.1 items, then the consumers and the integration check; Hydrograf and
  Hydraulik after the first release set.
- Do not start a project while its own active work is uncommitted.

## Historical progress on 2026-10-25

This is the early adoption snapshot, before the final integration fixes and
pushes, not the current completion or publication status. The branch audit
of 2026-10-28 is in [PROGRESS](../docs/PROGRESS.md#project-evidence-on-2026-10-28):
Hydrograf's quality tooling and producer migration, Archiwista's English
documentation and message catalog, and Kartograf's message catalog have
progressed beyond the cells below. `hydrolog.testing` is implemented on
the routing branches. Publication does not close merges, releases, CLA,
GitHub settings or the history rewrite.

| Project | Branch | Phase 2 | Phase 3 | Phase 4 |
|---|---|---|---|---|
| Kartograf | `chore/nogat-2.1` | done, except the contribution files (`SECURITY.md`, `CONTRIBUTING.md`, `CONTRIBUTORS.md`, the pull request template), which its PROGRESS leaves to the author | in progress: only the frozen records of `docs/research` and `docs/superpowers` are still Polish | in progress: the envelope, the error mapping, the catalog, the MCP server and the generated guide are done; the message catalog (ADR-053, area by area), `kartograf mcp` (AGI-3.8) and the domain JSON Schemas (AGI-4.1) are open |
| IMGWTools | `chore/nogat-2.1`, then `feature/data-output` | done, except `SECURITY.md` | in progress: README, USAGE and parts of CHANGELOG and DECISIONS are still Polish | in progress: the MCP prefix and annotations, `forbidden` 12, the English surfaces and the OpenAPI ids are done; the copy of `schemas/agent/` with its contract tests (AGI-4.1) is open |
| Hydrolog | `chore/nogat-2.1` | done | in progress: the example notebooks are still Polish | done |
| Retman | `chore/nogat-2.1` | done | in progress: `docs/research/` and `docs/specs/` are still Polish | done |
| Archiwista | `chore/nogat-2.1` | done | in progress: README, ARCHITECTURE, DECISIONS, SPEC, the plans and the reports are still Polish | in progress: error texts by `Accept-Language` and the message catalog (parked on `wip/message-catalog`); the error registry and problem+json are done |
| Hydrograf | `chore/nogat-2.1` | in progress: uv with its lock, formatting and the ruff rule set are done; mypy, the test tree, the gate, CI, Dependabot and the contribution files are planned | in progress: PROGRESS and BACKLOG are done | planned |
| Hydraulik | `feature/sfincs-swmm` | done; committing the proof of concept stays the author's decision | done | done |

Nogat (phase 0): 0.1 for the gate and CI templates, 0.2 and 0.5 (`CLAUDE.md`,
and the generated `AGENTS.md`) are done; 0.3 is on the topic branches
`fix/hub-gaps` and `feature/data-output`, whose merge waits; 0.4 and 0.6 are
open.
