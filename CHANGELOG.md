# Changelog

All notable changes to Nogat are documented here. The format follows
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/); versions of
the standard are listed in [standards/README.md](standards/README.md).

## [Unreleased]

### Added

- `pyproject.toml` and `uv.lock`: the registry tooling runs in the locked
  project environment; ruff, mypy, pytest, shellcheck and actionlint come
  from the lock (DEV-5.3, DEV-6.3).
- Tests of `scripts/ecosystem.py` in `tests/`, run by the gate with an 80%
  coverage floor (DEV-7.5, DEV-7.6).
- `.gitattributes`, `.editorconfig` and `.env.example`; `.gitignore` in
  English and ignores `.env` (DEV-13.1, DEV-14.1).
- `CLAUDE.md` with the hub's deviations, `docs/PROGRESS.md` and this
  changelog (DOC-1.1, DEV-1.2).
- `uv run scripts/ecosystem.py standard`, run by the gate: every cited
  requirement ID, section and decision resolves; IDs are defined once and
  in their document; relative links and anchors resolve; Nogat's files keep
  the DOC-1.7 budgets; the project lists typed in prose match
  `ecosystem.yaml`; the generated tables are fresh.
- The tables of `standards/ERROR_REGISTRY.md` §1 and §2 are generated from
  `error_registry.json` (`standard --write`); their wording is now the
  registry's.
- `schemas/agent/`: canonical JSON Schemas of `<tool>-result/1`,
  `<tool>-error/1` (generated from `error_registry.json` by
  `standard --write`) and `<tool>-commands/1`, with contract tests of the
  rules they enforce and of Nogat's own error documents (AGI-4.1, ECO-050).
- ECO-051 and DEV §19: one data-output convention for tools with a versioned
  store. Plain files (`--output-dir`, `-o`, `--output`) or the store
  (`--root`), the default store at `<data_dir>/<tool>`, preflight, staging and
  `--force`, store markers, the sidecar core and `files[]`; AGI-1.3, AGI-2.3,
  AGI-3.4, AGI-4.3, AGI-5.8, ERR-1, DEV-18.2, DEV-18.5 and DEV-18.6 refer to
  it.

### Changed

- `scripts/gate.sh` follows `standards/ci/gate.sh`: `uv sync --locked`, the
  DEV-7.2 rule set, mypy over `scripts/` and `tests/`, pytest with coverage.
- **Breaking:** `scripts/ecosystem.py` reports failures by the error
  registry (HUB-4.8, ECO-044): exit 7 `data_error` for an invalid registry or
  standard, 3 `not_found` for a missing file, 4 `conflict` for a stale map,
  stale generated tables or incompatible ranges, 2 `validation_error` for a
  wrong call, 1 only for a defect; the last stderr line is the
  `nogat-error/1` document. Migration: scripts that tested for exit 1 test
  for a non-zero exit or read the document.
- Standard 2.1, not yet published, settles the contradictions found in its
  review (ECO-042 to ECO-049 and consistency fixes; list in
  `standards/README.md`). The CI template and Nogat's CI check commits of
  `hotfix/*` pull requests into `main` (DEV-4.5).
- `ecosystem.yaml` and the map: `kartograf-store` and `imgw-store/1` name their
  root markers, and IMGWTools exchanges only `kartograf-store` with Kartograf
  because nested stores are refused by marker file name (DEV-19.12,
  DEV-19.14).

### Fixed

- `deps` no longer reports conflicts between overlapping ranges such as
  `<3` and `>2.5`.
- `drift` keeps VCS refs containing `/` (`@release/0.8`), labels a project
  without manifests "no manifest", and takes the newest final release tag as
  latest instead of a release candidate sorted after it.
- Requirements files are read as pip reads them: line continuations,
  `--hash` options and `-r` includes.
- A missing or malformed `ecosystem.yaml`, JSON or manifest gives a one-line
  error naming the file instead of a traceback; `deps --installed` notes an
  environment it cannot list.
- `validate` reports a topic document of the standard without its
  "Part of standard X.Y" line.
- `standards/ci/check-commits.sh` rejects AI co-author trailers by the
  trailer name or the e-mail of the tool (Devin and GitHub bot addresses
  included) and no longer rejects people or prose that only mention a tool;
  only git's own `Revert "…"` subjects are exempt (DEV-4.1, DEV-4.3).
