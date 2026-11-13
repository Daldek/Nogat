# CLAUDE.md

## Project

Nogat is the hub of the ecosystem: the shared standard (`standards/`), the
project registry (`ecosystem.yaml`) and the tooling that reads it. Profile:
`hub` (DEV §1). Overview: [README.md](README.md).

## Critical rules

- Without the author's approval in this session: no merges, tags, releases,
  force-pushes or history rewrites (DEV-3.3). `std-X.Y` tags included.
- Change only this repository; a need in another project is a GitHub issue
  labelled `request` in that project's repository (DEV-17.5).
- Scripts report failures by the error registry: last stderr line is the
  `nogat-error/1` document, exit code from `error_registry.json` (HUB-4.8).
- Never edit generated files or blocks: `docs/ECOSYSTEM_MAP.md` and `AGENTS.md`
  come from `ecosystem.yaml` (`uv run scripts/ecosystem.py map` and `agents`),
  the tables in `standards/ERROR_REGISTRY.md` from `error_registry.json`
  (`standard --write`).
- `standards/legacy/`, `standards/templates/` and `standards/configs/` hold
  files of the shared standards of 2026-01-29 that preceded Nogat, kept
  verbatim until replaced (DOC-11.1); do not edit or copy them.
- A requirement ID is never renumbered or reused; a deleted ID is listed in
  the changelog of `standards/README.md`.

## Environment and commands

```
uv sync --locked                         # environment in .venv
scripts/gate.sh                          # before every commit (DEV-7.6)
uv run pytest                            # tests only
uv run scripts/ecosystem.py validate     # registry
uv run scripts/ecosystem.py map          # regenerate docs/ECOSYSTEM_MAP.md
uv run scripts/ecosystem.py agents       # regenerate AGENTS.md, the routing table
uv run scripts/ecosystem.py deps|drift   # read sibling checkouts (HUB §3)
uv run scripts/ecosystem.py standard     # IDs, links, budgets; --write regenerates
uv run scripts/ecosystem.py set check    # consumers' pins against the release set
uv run scripts/ecosystem.py set apply --project P [--path DIR]   # pin P to the set
uv run scripts/ecosystem.py set bump P [--rev REF]   # move P, regenerate the README
uv run scripts/ecosystem.py set readme [--check]     # release-sets/candidate-<N>/README.md
```

Checkouts of the other projects are siblings of Nogat or under
`NOGAT_WORKSPACE`; `deps`, `drift` and `set check` only read them (`set check`
and `set bump` fetch first); `set apply` writes one consumer's manifests.

## Code map

```
scripts/ecosystem.py   registry: validate, map, agents, deps, drift, standard, set
scripts/guide.py       AGENTS.md: the routing table, from the registry's routes
scripts/standard.py    checks of the standard: IDs, links, budgets, copies
scripts/gate.sh        quality gate (standards/ci/gate.sh plus hub steps)
schemas/               JSON Schema of ecosystem.yaml
schemas/agent/         result, error (generated) and catalog schemas (AGI-4.1)
schemas/exchange/      nogat-handoff/1, the envelope of data handed between GUIs
schemas/log/           nogat-log/1, one record of a server's logs (DEV-12.4)
standards/             the standard; ci/ holds the templates projects copy
standards/reference/   nogat_logging.py, the server logs Python servers copy (DEV-12.9)
design/                visual identity of every GUI: tokens.css, marks/, guidelines, mockups (DEV-15.3)
tests/unit/            offline, single functions
tests/integration/     throwaway workspaces and git repositories
tests/contract/        the agent and hand-off schemas, AGENTS.md, Nogat's own error documents, design/
```

## Documentation map

| Task | Read |
|---|---|
| Change a rule | `standards/README.md` (how rules are written), the topic document, `standards/DECISIONS.md` for the reason |
| Change the registry or its tooling | `standards/ECOSYSTEM_HUB.md` §2 and §4 |
| Add or change a task of the routing table | `routes` of the project in `ecosystem.yaml` (HUB-2.9), then `uv run scripts/ecosystem.py agents`; the command must exist in the tool's `commands list` |
| Change a CI template | `standards/ci/README.md` |
| Plan cross-project work | `standards/ECOSYSTEM_HUB.md` §5, `docs/plans/` |
| Change the visual identity or a GUI mockup | `design/README.md`, `docs/plans/2026-11-01-visual-identity.md`, ECO-055 |

## Session workflow

Start: this file, `docs/PROGRESS.md`, `git status`, `git log --oneline -10`.
Work on a topic branch from `develop` (DEV-3.1). End: update
`docs/PROGRESS.md` and `CHANGELOG.md` (DEV-17.3, DOC-7.2).

## Cross-project context

Nogat's own entry and every project: [ecosystem.yaml](ecosystem.yaml).

## Deviations

- DEV-5.1: no `src/nogat/` until the `nogat` package exists (HUB §7); code
  lives in `scripts/` and `standards/reference/`, which coverage measures.
- DEV-13.6: no `pip-audit` job until the `nogat` package exists.
- DOC-2.1, DOC-1.4: README describes the hub with relative links until the
  `nogat` package is published (HUB-7.1).
