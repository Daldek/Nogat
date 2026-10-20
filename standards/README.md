# Ecosystem standard

Version 2.0 · 2026-10-19 · status: requirements written, adoption pending
([ADOPTION_PLAN.md](ADOPTION_PLAN.md)).

Shared rules for Kartograf, Hydrolog, IMGWTools, Hydrograf, Hydraulik, Retman,
Archiwista and Nogat. Priority: AI agents are the primary operators of these
projects, so the tools must be easy for agents to discover, judge and call
correctly, and safe for agents to develop.

| Document | Covers |
|---|---|
| [DECISIONS.md](DECISIONS.md) | Decisions behind the standard, with reasons and rejected options (ECO-…) |
| [DEVELOPMENT_STANDARDS.md](DEVELOPMENT_STANDARDS.md) | Profiles, language, git, commits, layout, uv, quality gate, naming, tests, errors, logging, security, agent workflow (DEV-…) |
| [DOCUMENTATION_STANDARDS.md](DOCUMENTATION_STANDARDS.md) | File set, README for agents and people, CLAUDE.md, AGENTS.md, llms.txt, PROGRESS, CHANGELOG, ADR (DOC-…) |
| [AGENT_INTERFACE.md](AGENT_INTERFACE.md) | Command catalog, CLI, result and error documents, MCP, REST, Python library, generated guides, languages, discoverability, agent-readiness checklist (AGI-…) |
| [ERROR_REGISTRY.md](ERROR_REGISTRY.md) + [error_registry.json](error_registry.json) | Shared error codes, exit codes, HTTP statuses (ERR-…) |
| [RELEASE_AND_DISTRIBUTION.md](RELEASE_AND_DISTRIBUTION.md) | Versioning, release procedure, PyPI, MCP Registry, conda-forge and other channels, ecosystem pins (REL-…) |
| [ECOSYSTEM_HUB.md](ECOSYSTEM_HUB.md) | Nogat role, `ecosystem.yaml`, local workspace, generated outputs, cross-repo agent rules (HUB-…) |
| [ADOPTION_PLAN.md](ADOPTION_PLAN.md) | Per-project changes, history rewrite procedure, order |

Keywords MUST, SHOULD, MAY follow RFC 2119. Requirement IDs are stable; cite
them in ADRs, plans and commit bodies.

## Open decisions

- ECO-022: common distribution name pattern for PyPI and conda-forge;
  preferred `nogat-<name>`, awaiting final confirmation.
- Hydraulik: whether the GPL-3.0 dependency `hydromt_sfincs` imposes
  obligations (DEV-13.5); separate investigation.

## Legacy

Standard v1.0 (2026-01-29) is archived in
[legacy/v1.0/](legacy/v1.0/). The v1.0 `templates/` and `configs/`
directories remain in place until v2.0 templates replace them (ADOPTION_PLAN
0.1); they do not reflect v2.0.

## Changelog

- 2.0 (2026-10-19): rewritten from project practice; English-only
  documentation; agent-first interface standard; shared error registry;
  `src` layout; uv; release and distribution channels; hub requirements.
- 1.0 (2026-01-29): first shared standard.
