# Nogat

Hub of an ecosystem of tools for hydrology, meteorology and geodata in
Poland and Czechia: Kartograf, Obserwator, Hydrolog, Hydrograf, Hydraulik,
Retman, Archiwista and Goniec.

Nogat holds:

- the shared standard for all projects, 1.2 (tag `std-1.2`):
  [`standards/`](standards/README.md);
- the project registry: [`ecosystem.yaml`](ecosystem.yaml), validated by
  [`schemas/ecosystem.schema.json`](schemas/ecosystem.schema.json);
- the map of dependencies and exchanged data, generated from the registry:
  [`docs/ECOSYSTEM_MAP.md`](docs/ECOSYSTEM_MAP.md);
- the routing table for agents, task to tool to entry command with a link to
  each tool's guide, generated from the registry: [`AGENTS.md`](AGENTS.md);
- cross-project plans: [`docs/plans/`](docs/plans/);
- the visual identity of every GUI (tokens, marks, guidelines) and the GUI
  kit every GUI copies: [`design/`](design/README.md);
- the reference module of server logs every Python server copies:
  [`standards/reference/`](standards/reference/nogat_logging.py);
- the reference module of formulas every project that computes copies, with
  the schema of its formula cards:
  [`standards/reference/nogat_formulas.py`](standards/reference/nogat_formulas.py),
  [`schemas/formula/`](schemas/formula/card-1.schema.json).

The ecosystem's current release, `v0.3.0`, is the release set
[`release-sets/v0.3.0/`](https://github.com/Daldek/Nogat/tree/v0.3.0/release-sets/v0.3.0):
Kartograf 0.9.0, Obserwator 3.2.1, Hydrolog 0.9.1 and Archiwista 0.4.1 at
their release tags, with every third-party package at one verified version;
Hydrograf 0.6.1, an app, is released by its own tag at the same producers.
It publishes standard 1.2. Install it as an environment:

```bash
git clone --branch v0.3.0 https://github.com/Daldek/Nogat
cd Nogat/release-sets/v0.3.0
uv sync --locked --no-dev --python 3.12
```

The members' commands are then in `.venv/bin/`.

Nogat will also be the `nogat` package that installs every tool with one
command ([HUB §7](standards/ECOSYSTEM_HUB.md)); it does not exist yet.

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
uv run scripts/ecosystem.py drift            # compare consumers' pins with producers' latest tags, and copies of Nogat's files
uv run scripts/ecosystem.py standard         # check the standard's IDs, links, budgets, generated tables
uv run scripts/ecosystem.py set check        # compare consumers' pins with the release set candidate
```

`deps` and `drift` read the projects' checkouts next to Nogat, or under
`NOGAT_WORKSPACE`. Once the `nogat` package exists they are
`nogat ecosystem deps` and `nogat ecosystem drift` (HUB-7.3). The registry
holds structure only; versions and pins are read from the repositories.

`scripts/gate.sh` sets up the environment from `uv.lock` and checks the
scripts (ruff, mypy, pytest with coverage), the registry, the map,
AGENTS.md and the release set's README, the standard, the CI templates
(shellcheck, actionlint) and commit messages; CI runs it on every push and
pull request. Working on Nogat itself: [CLAUDE.md](CLAUDE.md).

## Issues

Report problems in [Issues](https://github.com/Daldek/Nogat/issues).

## Licence

MIT, see [LICENSE](LICENSE).

## Author

[Piotr de Bever](https://debever.pl/) ·
[LinkedIn](https://www.linkedin.com/in/piotr-de-bever/)
