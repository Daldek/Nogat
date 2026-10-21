# CI templates

Templates for the quality gate (DEV-7.6), CI (DEV-7.7) and dependency updates
(DEV-13.6). Copy them into a project; edit only where marked.

| File | Copy to | Edit |
|---|---|---|
| [`gate.sh`](gate.sh) | `scripts/gate.sh` | the project settings at the top |
| [`check-commits.sh`](check-commits.sh) | `scripts/check-commits.sh` | nothing |
| [`ci.yml`](ci.yml) | `.github/workflows/ci.yml` | the newest Python, accepted audit findings (`app` variant below) |
| [`live.yml`](live.yml) | `.github/workflows/live.yml` | only in projects with `live` tests |
| [`dependabot.yml`](dependabot.yml) | `.github/dependabot.yml` | nothing |

## What the gate runs

1. `uv sync --locked --all-extras` (fails when `uv.lock` is stale, DEV-6.3);
2. `ruff format --check`, `ruff check` (DEV-7.1, DEV-7.2);
3. `mypy` over the configured paths (DEV-7.3);
4. one `pytest` call over `tests/` with coverage and `OFFLINE` as the marker
   expression (`not live`; `not live and not db` in an `app` without a local
   database); contract tests in `tests/contract` are part of it (DEV-10.1,
   DEV-10.4, DEV-7.5);
5. the commit step, `check-commits.sh` (DEV-4.5):
   - locally (`GATE_COMMIT_RANGE` unset) it starts with an identity preflight:
     `git var GIT_AUTHOR_IDENT` must carry `git@debever.pl`, otherwise it fails
     with the hint `git config user.email`. It then checks the unpushed
     commits, or without an upstream the commits since `origin/develop`
     (`HEAD` alone when that is missing): Conventional Commits, no AI
     attribution (including `Claude-Session:` lines), author;
   - in CI, `GATE_COMMIT_RANGE` is `origin/develop..HEAD` on pull requests
     into `develop`, `origin/main..HEAD` on pull requests from `hotfix/*`
     into `main`, and `none` everywhere else, which skips the step;
     `GATE_CHECK_AUTHOR=1` only for those pull requests from the
     repository's own branches, not from forks and not opened by Dependabot
     (DEV-16.5).

Contributors keep their own identity and run
`GATE_CHECK_AUTHOR=0 scripts/gate.sh` (DEV-16.4).

In a git worktree uv creates the worktree's own `.venv`, so the gate tests the
code of the checkout it runs from. The scripts run in bash 3.2 (macOS), bash 5
(Linux) and Git Bash (Windows).

## Required project configuration

`pyproject.toml`:

```toml
[dependency-groups]
dev = ["ruff", "mypy", "pytest", "pytest-cov"]

[tool.pytest.ini_options]
# `app` without a local database: -m 'not live and not db'
addopts = "--strict-markers -m 'not live'"
markers = [
  "live: real network services",
  "slow: more than ~10 s or Docker",
  "db: needs a database",
]

[tool.coverage.report]
fail_under = 80   # the floor; lower values are deviations (DEV-7.5)
```

and a committed `uv.lock`.

## CI matrix, audit and updates

`ci.yml` runs the gate on Linux, macOS and Windows with Python 3.12 (required)
and the newest stable Python (reported; a failure does not fail the workflow,
because wheels of geospatial dependencies often arrive later). Raise the
newest version when a new Python is released.

The `audit` job exports the locked dependencies with hashes, leaves out the
ecosystem's own distributions (`kartograf`, `imgwtools`, `hydrolog`, `retman`,
`archiwista`, `hydraulik`, `hydrograf` and their `nogat-<project>` names: they
come from git tags until they are on PyPI and carry no hashes) and runs
`pip-audit` on push, on pull requests and weekly. It informs and is not a
required check. An accepted finding gets `--ignore-vuln <ID>` and a comment.

Actions are pinned by commit SHA with the version in a comment; Dependabot
updates them weekly. Python vulnerabilities come from GitHub's "Dependabot
security updates" (DEV-13.6).

## Repository settings on GitHub

- Branch ruleset (Settings → Rules → Rulesets → New branch ruleset): target
  `main` and `develop`, enforcement Active, no bypass actors (DEV-3.6):
  - require a pull request before merging, approvals 0, allowed merge
    methods: merge commit only;
  - require status checks: the three `gate (…, Python 3.12)` jobs (they appear
    in the list after the first CI run), and `db` in an `app` project; not
    `dependency audit`;
  - block force pushes, restrict deletions.
- Tag ruleset: target tags `v*`, restrict updates and deletions.
- Code security: enable Dependabot security updates (DEV-13.6) and private
  vulnerability reporting (DEV-13.7).
- History rewrite: the author sets the branch ruleset to Disabled, rewrites,
  sets it to Active again and notes it in PROGRESS.

## `app` variant (database)

Service containers run only on Linux runners. A project whose tests need a
database keeps `ci.yml` for the platform matrix with `db` tests excluded
(`OFFLINE="not live and not db"` in `gate.sh`) and adds a Linux job with the
service:

```yaml
  db:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgis/postgis:16-3.4
        env: {POSTGRES_DB: test, POSTGRES_USER: test, POSTGRES_PASSWORD: test}
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U test -d test"
          --health-interval 10s --health-timeout 5s --health-retries 5
    env:
      DATABASE_URL: postgresql://test:test@localhost:5432/test
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
      - uses: astral-sh/setup-uv@1c37ad07a6a961277cf70c0d37d6f313000f5884  # v10.3.0
        with: {python-version: "3.12", enable-cache: true}
      - run: uv sync --locked --all-extras
      - run: uv run --no-sync pytest tests -m db -q
```
