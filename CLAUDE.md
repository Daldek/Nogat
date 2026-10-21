# CLAUDE.md

## Project

Nogat is the hub of the ecosystem: the shared standard (`standards/`), the
project registry (`ecosystem.yaml`) and the tooling that reads it. Profile:
`hub` (DEV §1). Overview: [README.md](README.md).

## Critical rules

- Without the author's approval in this session: no merges, tags, releases,
  force-pushes or history rewrites (DEV-3.3). `std-X.Y` tags included.
- Change only this repository; a need in another project is an entry in
  `docs/requests/<Project>.md` (DEV-17.5).
- Never edit generated files or blocks: `docs/ECOSYSTEM_MAP.md` comes from
  `ecosystem.yaml` (`uv run scripts/ecosystem.py map`), the tables in
  `standards/ERROR_REGISTRY.md` from `error_registry.json` (`standard --write`).
- `standards/legacy/`, `standards/templates/` and `standards/configs/` are v1
  files kept verbatim until replaced (DOC-11.1); do not edit or copy them.
- A requirement ID is never renumbered or reused; a deleted ID is listed in
  the changelog of `standards/README.md`.

## Environment and commands

```
uv sync --locked                         # environment in .venv
scripts/gate.sh                          # before every commit (DEV-7.6)
uv run pytest                            # tests only
uv run scripts/ecosystem.py validate     # registry
uv run scripts/ecosystem.py map          # regenerate docs/ECOSYSTEM_MAP.md
uv run scripts/ecosystem.py deps|drift   # read sibling checkouts (HUB §3)
uv run scripts/ecosystem.py standard     # IDs, links, budgets; --write regenerates
```

Checkouts of the other projects are siblings of Nogat or under
`NOGAT_WORKSPACE`; `deps` and `drift` only read them.

## Code map

```
scripts/ecosystem.py   registry: validate, map, deps, drift, standard
scripts/standard.py    checks of the standard: IDs, links, budgets, copies
scripts/gate.sh        quality gate (standards/ci/gate.sh plus hub steps)
schemas/               JSON Schema of ecosystem.yaml
standards/             the standard; ci/ holds the templates projects copy
tests/unit/            offline, single functions
tests/integration/     throwaway workspaces and git repositories
```

## Documentation map

| Task | Read |
|---|---|
| Change a rule | `standards/README.md` (how rules are written), the topic document, `standards/DECISIONS.md` for the reason |
| Change the registry or its tooling | `standards/ECOSYSTEM_HUB.md` §2 and §4 |
| Change a CI template | `standards/ci/README.md` |
| Plan cross-project work | `standards/ECOSYSTEM_HUB.md` §5, `docs/plans/` |

## Session workflow

Start: this file, `docs/PROGRESS.md`, `git status`, `git log --oneline -10`.
Work on a topic branch from `develop` (DEV-3.1). End: update
`docs/PROGRESS.md` and `CHANGELOG.md` (DEV-17.3, DOC-7.2).

## Cross-project context

Nogat's own entry and every project: [ecosystem.yaml](ecosystem.yaml).

## Deviations

- DEV-5.1: no `src/nogat/` until the `nogat` package exists (HUB §7); code
  lives in `scripts/`, coverage measures `scripts/`.
- DEV-7.7: CI runs the gate on Linux only until the `nogat` package exists.
- DEV-13.6: no `pip-audit` job until the `nogat` package exists.
- DOC-1.1: no aggregated `AGENTS.md` yet (HUB-4.3 not implemented).
- DOC-2.1, DOC-1.4: README describes the hub with relative links until the
  `nogat` package is published (HUB-7.1).
- DEV-13.7, DEV-16.2: `SECURITY.md`, `CONTRIBUTING.md`, `docs/CLA.md` and
  `CONTRIBUTORS.md` await the author.
