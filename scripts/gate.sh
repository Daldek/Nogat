#!/usr/bin/env bash
# Nogat quality gate (DEV-7.6, HUB-2.3). Nogat has no package yet, so it does
# not use the project template; it checks the registry tooling, the registry
# and generated map, the CI templates it ships, and commit messages.
#
# Usage: scripts/gate.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

step() { printf '\n== %s\n' "$1"; }
command -v uv >/dev/null || { echo "gate: uv not found (DEV-6.2)" >&2; exit 1; }
started=$SECONDS

step "ruff format --check"
uvx ruff@0.15.0 format --check scripts

step "ruff check"
uvx ruff@0.15.0 check scripts

step "mypy"
uvx --with types-PyYAML --with types-jsonschema --with packaging \
  mypy@1.19.1 --strict scripts/ecosystem.py

step "registry (HUB-2.3)"
uv run scripts/ecosystem.py validate

step "ecosystem map (HUB-4.5)"
uv run scripts/ecosystem.py map --check

step "shellcheck"
uvx --from shellcheck-py@0.11.0.1 shellcheck standards/ci/*.sh scripts/*.sh

step "actionlint"
uvx --from actionlint-py@1.7.12.25 actionlint .github/workflows/*.yml \
  standards/ci/ci.yml standards/ci/live.yml

step "commit step"
bash standards/ci/check-commits.sh

printf '\nGATE OK (%d s)\n' "$((SECONDS - started))"
