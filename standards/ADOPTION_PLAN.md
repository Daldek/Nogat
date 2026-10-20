# Adoption plan for standard v2.0

Status 2026-10-19: requirements written; no project changed yet. Each item
names the requirement it implements. Work happens in later sessions, one
project per session, on a `docs/standard-v2` or `chore/standard-v2` branch,
with the author's approval for merges, pushes, tags and history rewrites
(DEV-3.3).

---

## Phase 0: Nogat

| # | Item | Requirement |
|---|---|---|
| 0.1 | Templates v2 in `standards/templates/` (README, CLAUDE, AGENTS and llms.txt generator templates, PROGRESS, CHANGELOG, ADR, PRD, server.json, context7.json, CITATION.cff) and configs (`pyproject` fragment with ruff/mypy/pytest/coverage, `.editorconfig`, `.gitattributes`, `gate.sh`, CI workflow). The v1.0 `templates/` and `configs/` directories are owned by root and must be replaced by the author or with elevated rights | DOC §11 |
| 0.2 | `ecosystem.yaml` with all eight projects and its JSON Schema | HUB-2 |
| 0.3 | Nogat README rewritten for the hub role (English) | HUB-4.4, ECO-005 |
| 0.4 | `develop` branch; `.gitignore` for `ecosystem.local.yaml` | ECO-008, HUB-3.2 |
| 0.5 | Hub tooling: registry validation, `workspace sync`, `report drift`, `mcp config` | HUB-3, HUB-4 |
| 0.6 | Confirm ECO-022 (preferred `nogat-<name>`); then reserve `nogat-kartograf`, `nogat-hydrolog`, `nogat-imgwtools`, `nogat-hydrograf`, `nogat-hydraulik`, `nogat-retman`, `nogat-archiwista` on PyPI | REL-3.1 |

## Phase 1: identity and history (one-off)

Preconditions, checked per repository before starting:
- no uncommitted changes and no stash, which `git-filter-repo` does not
  rewrite. On 2026-10-19: Hydrolog 42 changed files, Hydrograf 1, Hydraulik 8
  plus its worktree, IMGWTools 1 stash;
- local-only commits pushed or consciously included. On 2026-10-19: Hydrograf
  67, IMGWTools 15, Hydrolog 3, Kartograf 1;
- the rewrite happens before tagging Kartograf v0.8.0 and IMGWTools v3.0.0.

Procedure per repository (ECO-007), proven in a dry run on mirror copies on
2026-10-19:
1. `git bundle create <backup>.bundle --all` outside the repository.
2. Fresh `git clone --mirror`.
3. `git-filter-repo` with a mailmap. Every identity, `Claude <agent@local>`
   and the Daldek variants `piotr.de.bever@gmail.com`,
   `38719982+Daldek@users.noreply.github.com` and `Piotr <…noreply…>`,
   becomes `Daldek <git@debever.pl>`. A message callback removes
   `Co-authored-by:` lines naming Claude, Anthropic or Copilot and
   "🤖 Generated with [Claude Code]" lines. The third-party author
   `PL1B5J <1b5j@sweco.dk>` stays.
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
address everywhere.

## Phase 2: repository structure and tooling

| Project | Items |
|---|---|
| all | local git identity (DEV-4.2); `.editorconfig` and `.gitattributes` (DEV-14.1); `scripts/gate.sh` with commit-message check (DEV-7.6, DEV-4.3); CI (DEV-7.7); uv and `uv.lock` (DEV-6.2, DEV-6.3); markers (DEV-10.1); coverage ratchet (DEV-7.5) |
| Kartograf | `src/` layout (ECO-011); mypy baseline ratchet (DEV-7.3); `docs/DECISIONS.md` CRLF → LF (DEV-14.1) |
| Hydrolog | Black and flake8 → ruff (ECO-009); `src/` layout; package data test for agent templates (DEV-5.4); `.editorconfig`/`.gitattributes` |
| IMGWTools | branches `master`/`slave` → `main`/`develop`, default branch on GitHub (ECO-008); pyright → mypy (ECO-010); links in `llms.txt` and docs from `master` to `main` |
| Hydrograf | uv and lock for `backend/` (replaces pinned `requirements.txt`, keeps documented caps); gate beyond ruff-only pre-commit; mypy in CI |
| Hydraulik | commit the proof of concept from the worktree into `develop` (DEV-3.5, author's decision); `main` as default branch; mypy; English identifiers in `roads.py` (DEV-2.4); investigate GPL-3.0 implications of `hydromt_sfincs` and set visibility and licence notes accordingly (DEV-13.5, separate session) |
| Retman | `src/` layout; logging (DEV-12) |
| Archiwista | `src/` layout; `requirements.lock` → `uv.lock`; Kartograf pin to a tag after v0.8.0 (REL-5.3); remote repository decision (currently none) |

## Phase 3: documentation

| Project | Items |
|---|---|
| all | translate documentation to English (ECO-005); restructure README (DOC-2); CLAUDE.md ≤ 200 lines with deviations section (DOC-3); PROGRESS split and monthly archive (DOC-6); ADR index and one file per new ADR (DOC-8); `docs/specs`, `docs/plans`, `docs/research` naming (DOC-1.2); split documents above ~1,500 lines (DOC-1.3); project `DEVELOPMENT_STANDARDS.md` reduced to deviations (DEV-1.3) |
| Kartograf | remove the "no AGENTS.md" rule; generate AGENTS.md (ECO-014); `llms.txt` to link-list format with raw links (DOC-5) |
| IMGWTools | `CLAUDE.md` from 587 lines to ≤ 200; README from ~830 lines to ≤ 400 |
| Hydrolog | README from ~810 lines to ≤ 400 |
| Hydrograf | PROGRESS archive (145 KB); move `notes/superpowers/*` to `docs/specs` and `docs/plans`; migrate `CROSS_PROJECT_ANALYSIS.md` into Nogat registry and requests |
| Hydraulik | full documentation set; CLAUDE.md beyond 25 lines; CHANGELOG |
| Retman | AGENTS.md, llms.txt |
| Archiwista | llms.txt; AGENTS.md from `docs/AGENT_API.md` |

## Phase 4: agent interfaces

| Project | Items |
|---|---|
| Kartograf | envelope `kartograf-result/1` with `status` (AGI-4.2); errors on last stderr line (ECO-019); registry mapping (ERROR_REGISTRY §4); MCP tool prefixes `kartograf_` (ECO-018), annotations, `outputSchema`, English descriptions with when/when-not (AGI-5); `commands guide` generator (AGI-8); shared option names (AGI-3.4) |
| IMGWTools | MCP prefix `imgw_` and annotations; `forbidden` exit 12; English default for agent surfaces (AGI-9.2); OpenAPI `operationId` = catalog ids (AGI-6.2) |
| Hydrolog | registry numbers (13, 12); finish catalog fields (AGI-2.2); MCP per AGI-5 |
| Hydrograf | catalog for scripts with `--json` (bootstrap, downloads); REST problem+json with registry codes; OpenAPI ids; consider an MCP server for watershed and hydrograph queries |
| Hydraulik | catalog, `--json` envelope, registry codes for the CLI; job and result JSON Schemas kept as domain documents (`hydraulik-<kind>/1`) |
| Retman | registry codes for exits; consume tools through `list_commands`/`command_schema`/`run_command` (AGI-2.1) instead of per-tool handlers where possible |
| Archiwista | registry codes in problem+json; `--json` CLI envelope; OpenAPI ids |
| all tools | agent-readiness checklist in the gate (AGI §11); `context7.json`; GitHub topics and About (AGI-10) |

## Phase 5: distribution

| Item | Requirement |
|---|---|
| Trusted Publishing workflows; first PyPI releases | REL-2.2, REL-3 |
| `server.json` and MCP Registry entries for Kartograf, IMGWTools, Hydrolog | REL-4 |
| Consumers switch from git tags to PyPI ranges | REL-5.2 |
| conda-forge recipes (Kartograf, Hydraulik, Hydrolog, IMGWTools) | REL-3 #4 |
| GHCR images for applications | REL-3 #5 |
| Optional: plugin marketplace, Zenodo, QGIS repository | REL-3 #6–8 |

## Ordering constraints

- Phase 1 before any new tags, because tags created earlier would move.
- Kartograf v0.8.0 and IMGWTools v3.0.0: tag after Phase 1, before Phase 4
  breaking changes (those go into the next version).
- Producers before consumers in Phase 4: Kartograf, IMGWTools, Hydrolog first;
  Retman, Archiwista, Hydrograf, Hydraulik follow.
- Do not start a project while its own active work is uncommitted (Retman had
  85 changed files on 2026-10-19).
