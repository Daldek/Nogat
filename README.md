# Nogat

Hub of an ecosystem of tools for hydrology, meteorology and geodata in
Poland and Czechia: Kartograf, IMGWTools, Hydrolog, Hydrograf, Hydraulik,
Retman and Archiwista.

Nogat holds:

- the shared standard for all projects: [`standards/`](standards/README.md);
- the project registry: [`ecosystem.yaml`](ecosystem.yaml), validated by
  [`schemas/ecosystem.schema.json`](schemas/ecosystem.schema.json);
- the map of dependencies and exchanged data, generated from the registry:
  [`docs/ECOSYSTEM_MAP.md`](docs/ECOSYSTEM_MAP.md);
- the routing table for agents, task to tool to entry command with a link to
  each tool's guide, generated from the registry: [`AGENTS.md`](AGENTS.md);
- cross-project plans: [`docs/plans/`](docs/plans/).

Nogat will also be the `nogat` package that installs every tool with one
command (`uv tool install nogat`, [HUB §7](standards/ECOSYSTEM_HUB.md));
it is not published yet.

Templates for every project's quality gate and CI are in
[`standards/ci/`](standards/ci/README.md).

## Registry tooling

```
uv run scripts/ecosystem.py validate         # check ecosystem.yaml
uv run scripts/ecosystem.py map              # regenerate docs/ECOSYSTEM_MAP.md
uv run scripts/ecosystem.py map --check      # fail when the map is stale
uv run scripts/ecosystem.py agents           # regenerate AGENTS.md, the routing table
uv run scripts/ecosystem.py agents --check   # fail when AGENTS.md is stale
uv run scripts/ecosystem.py deps             # compare third-party dependencies across checkouts
uv run scripts/ecosystem.py drift            # compare consumers' pins with producers' latest tags
uv run scripts/ecosystem.py standard         # check the standard's IDs, links, budgets, generated tables
```

`deps` and `drift` read the projects' checkouts next to Nogat, or under
`NOGAT_WORKSPACE`. Once the `nogat` package exists they are
`nogat ecosystem deps` and `nogat ecosystem drift` (HUB-7.3). The registry
holds structure only; versions and pins are read from the repositories.

`scripts/gate.sh` sets up the environment from `uv.lock` and checks the
scripts (ruff, mypy, pytest with coverage), the registry, the map and
AGENTS.md, the CI templates (shellcheck, actionlint) and commit messages; CI
runs it on every push and pull request. Working on Nogat itself:
[CLAUDE.md](CLAUDE.md).

## Issues

Report problems in [Issues](https://github.com/Daldek/Nogat/issues).

## Licence

MIT, see [LICENSE](LICENSE).

## Author

[Piotr de Bever](https://debever.pl/) ·
[LinkedIn](https://www.linkedin.com/in/piotr-de-bever/)
