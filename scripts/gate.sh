#!/usr/bin/env bash
# Nogat quality gate (DEV-7.6, HUB-2.3). It follows standards/ci/gate.sh and
# adds the hub's own steps: the registry and generated map, and shellcheck and
# actionlint over the CI templates Nogat ships. Tool versions come from
# uv.lock. Coverage measures scripts/ until the `nogat` package exists
# (deviation DEV-5.1 in CLAUDE.md).
#
# Usage: scripts/gate.sh [extra pytest arguments]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

step() { printf '\n== %s\n' "$1"; }
fail() { printf 'gate: %s\n' "$1" >&2; exit 1; }

command -v uv >/dev/null || fail "uv not found (DEV-6.2): https://docs.astral.sh/uv/"

started=$SECONDS

step "uv sync --locked"
uv sync --locked

run() { uv run --no-sync "$@"; }

step "ruff format --check"
run ruff format --check .

step "ruff check"
run ruff check .

step "mypy"
run mypy

step "pytest (tests/, coverage)"
# ${@+"$@"} keeps an empty argument list safe under set -u on macOS bash 3.2.
run pytest tests -m "not live" --cov --cov-report=term-missing:skip-covered \
  -q ${@+"$@"}

step "registry (HUB-2.3)"
run python scripts/ecosystem.py validate

step "ecosystem map (HUB-4.5)"
run python scripts/ecosystem.py map --check

step "standard (HUB-4.7: IDs, links, budgets, generated outputs)"
run python scripts/ecosystem.py standard

step "shellcheck"
run shellcheck standards/ci/*.sh scripts/*.sh

step "actionlint"
run actionlint .github/workflows/*.yml standards/ci/ci.yml standards/ci/live.yml

step "commit step"
bash standards/ci/check-commits.sh

printf '\nGATE OK (%d s)\n' "$((SECONDS - started))"
