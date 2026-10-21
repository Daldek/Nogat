# Ecosystem standard

Standard 2.1 · tag `std-2.1` once committed

Shared rules for Kartograf, IMGWTools, Hydrolog, Hydrograf, Hydraulik,
Retman, Archiwista and Nogat. AI agents are their primary operators, so the
tools must be easy to discover, judge and call correctly, and safe to develop.

## Zen of Nogat

1. One obvious way: one name, one place, one tool for each job.
2. Facts live where they are made; everything else is generated or linked, never retyped.
3. Generated files are never edited, and a check proves they are fresh.
4. A rule without a check is a wish: gate it, shorten it, or delete it.
5. Test before you declare: no version, pin or claim without a green run.
6. Boring tools, default settings: uv, ruff, mypy, pytest, GitHub Actions.
7. Context is the scarce resource: short files, details on demand, nothing the agent would do anyway.
8. Safe by default: read before write, check before change; the author approves merges, tags and releases.
9. Machines read English and stable codes; people read Polish.
10. Each project works alone; the hub adds, it never requires.
11. Write the rule when the second project needs it, not before.
12. Break freely before 1.0, but leave no shim behind.

## How to read the rules

- Every requirement is mandatory. `MAY` marks an option; there is no SHOULD.
  Capitalised MUST and MUST NOT only stress: unmarked text in a requirement
  binds equally.
- A requirement is one or two sentences, optionally followed by `*Why:*` and
  one line (a reason or an ECO reference). Dated facts and the state of named
  projects stay out of rules.
- Requirement IDs are `PREFIX-n.m` (`ERR-n` in the error registry), with
  prefix `DEV`, `DOC`, `AGI`, `ERR`, `REL` or `HUB`; a section is cited as
  `PREFIX §n`, for example `DEV §18`; `ECO-nnn` is a decision in
  [DECISIONS.md](DECISIONS.md).
- IDs are stable: never renumbered, never reused. A deleted requirement
  disappears and the changelog lists it. Cite IDs in ADRs, plans and commit
  bodies.
- Profiles are `tool` (installable Python package; CLI, MCP and REST
  optional), `app` (deployed service) and `hub` (Nogat), defined in DEV §1. A
  requirement or section that names a profile applies only to projects that
  have it.
- Placeholders, defined here once:
  - `<project>`: the project name in lower case as in `nogat-<project>`:
    kartograf, imgwtools, hydrolog, hydrograf, hydraulik, retman, archiwista;
  - `<Project>`: the project name as in the registry (Kartograf, IMGWTools, …);
  - `<tool>`: the CLI name, `interfaces.cli` in `ecosystem.yaml`: kartograf,
    imgw, hydrolog, retman, archiwista, hydraulik; `<TOOL>` is its upper
    case;
  - `<package>`: the Python import name (`distribution.import_name`).

## Documents

| Document | Covers |
|---|---|
| [DECISIONS.md](DECISIONS.md) | Decisions behind the standard, with reasons and rejected options (ECO-…) |
| [DEVELOPMENT_STANDARDS.md](DEVELOPMENT_STANDARDS.md) | Profiles, language, git, commits, layout, uv, quality gate, naming, tests, errors, logging, security, licence and contributions, agent workflow, user environment (DEV-…) |
| [DOCUMENTATION_STANDARDS.md](DOCUMENTATION_STANDARDS.md) | File set and size budgets, README for agents and people, CLAUDE.md, AGENTS.md, llms.txt, PROGRESS, CHANGELOG, ADR, PRD, ARCHITECTURE, USAGE, templates, ecosystem user documentation (DOC-…) |
| [AGENT_INTERFACE.md](AGENT_INTERFACE.md) | Command catalog, CLI, result and error documents, MCP, REST, Python library, generated guides, languages, discoverability (AGI-…) |
| [ERROR_REGISTRY.md](ERROR_REGISTRY.md) + [error_registry.json](error_registry.json) | Shared error codes, exit codes, HTTP statuses (ERR-…) |
| [RELEASE_AND_DISTRIBUTION.md](RELEASE_AND_DISTRIBUTION.md) | Versioning, release procedure, channels (PyPI, GitHub Releases, MCP Registry), MCP Registry entry, dependencies between projects, release sets, support (REL-…) |
| [ECOSYSTEM_HUB.md](ECOSYSTEM_HUB.md) | Nogat role, `ecosystem.yaml`, local workspace, generated outputs, cross-project plans and requests, standard versioning, the `nogat` package (HUB-…) |
| [ADOPTION_PLAN.md](ADOPTION_PLAN.md) | Per-project changes by phase, history rewrite procedure, order |
| [ci/](ci/README.md) | Templates for `scripts/gate.sh`, the commit-message check, GitHub Actions workflows and Dependabot (DEV-7.6, DEV-7.7, DEV-13.6) |

## Open decisions

None.

## Legacy

Standard v1.0 (2026-01-29) is archived in [legacy/v1.0/](legacy/v1.0/). The
root-owned `templates/` and `configs/` directories are v1 files and not valid
for 2.1; the author replaces them (ADOPTION_PLAN 0.1, DOC-11.1).

## Changelog

- 2.1 (2026-10-20):
  - Zen of Nogat; every requirement mandatory, `MAY` for options, no SHOULD
    (ECO-033).
  - The registry holds structure only; the drift command reads versions and
    pins from the repositories (HUB §2, HUB-4.1, ECO-034).
  - Minimal support (the latest release, on the CI platforms) and three
    channels, PyPI, GitHub Releases and the MCP Registry; the rest waits for a
    user (REL §3, REL-7.1, ECO-035, supersedes ECO-032).
  - Three profiles, `tool`, `app` and `hub` (DEV §1, ECO-036).
  - One release path: release pull request, merge commit into `main`,
    annotated tag, hotfix branch; the `verify-candidate` workflow for release
    sets; `nogat` installed from its git tag until its members are on PyPI
    (REL §2, REL §6, HUB §7, DEV-3.6, ECO-037).
  - Commit messages and authors are checked once, on entry to `develop`
    (DEV-4.5, ECO-038).
  - One plan kind, one request list, a short PROGRESS (DEV-17.4, DEV-17.5,
    DOC §6, ECO-039).
  - Dependabot for GitHub Actions only; the audit informs (DEV-13.6,
    ECO-040).
  - Open decisions settled: Hydraulik stays MIT (ECO-041), the `nogat`
    package ships the registry (HUB-7.3), the MCP start form is settled at the
    rename (ADOPTION_PLAN 6.1).
  - Added to 2.0 earlier the same day and now part of 2.1: exchanged data in
    the registry (ECO-024, HUB-2.5 to HUB-2.7); release sets and the `deps`
    comparison (ECO-025, REL §6, HUB-4.6); the user package `nogat` and the
    `nogat-` prefix (ECO-026, ECO-022, HUB §7); removal of Nogat's legacy
    scripts and data (ECO-027); one user environment for all tools (ECO-028,
    DEV §18); producers' testing modules (DEV-10.6); protected branches
    (ECO-030, DEV-3.6); external contributors keep their identity (ECO-031,
    DEV-16.5); ecosystem user documentation (DOC §12); gate and CI templates
    in `ci/`, with Nogat's own gate in CI; generated `docs/ECOSYSTEM_MAP.md`
    (HUB-4.5).
  - Merged IDs: DEV-6.6 into DEV-6.4, REL-1.2 into REL-1.1, REL-6.3 into
    REL-6.2, REL-7.2 and REL-7.3 into REL-7.1.
  - Deleted IDs: DEV-3.2, DEV-8.4, DEV-11.2, DEV-16.3, DOC-1.3, DOC-5.5,
    DOC-6.2, DOC-9.2, AGI-10.2, AGI-10.3, AGI §11, REL-5.5, HUB-2.2, HUB-4.4,
    HUB-5.1, HUB-6.2, and the third-party tools item of HUB-1.1.
- 2.0 (2026-10-19): rewritten from project practice; English-only
  documentation; agent-first interface standard; shared error registry;
  `src` layout; uv; release and distribution channels; hub requirements.
- 1.0 (2026-01-29): first shared standard.
