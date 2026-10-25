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
  the DOC-1.7 budgets; the project lists typed in prose and the store markers
  of DEV-19.12 match `ecosystem.yaml`; the generated tables are fresh.
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
- `docs/plans/2026-10-24-data-output.md`: the approved plan to adopt DEV §19
  in the projects, producers first, then consumers, the integration check and
  the first release set (HUB-5.2, DEV-17.4); ADOPTION_PLAN phase 4 lists the
  items per project.
- `routes` in `ecosystem.yaml` and its schema: for each project the tasks that
  tool covers and the command that starts each, in the names of the tool's
  branch recorded in the registry (the CLI of the project, or an HTTP method
  for Hydrograf's REST API). `validate` checks that a route starts with its
  project's CLI, that a task is routed once and that every project but the hub
  has a route (HUB-2.9, ECO-052).
- `AGENTS.md`, generated from the registry by `uv run scripts/ecosystem.py
  agents` (`scripts/guide.py`): a routing table of task, tool and entry
  command, each row linking the tool's AGENTS.md as raw Markdown on `main`
  (the README of an app), the tools' blocks not inlined. `agents --check`
  fails with `conflict` when it is stale and is a step of `scripts/gate.sh`;
  a contract test compares the file with the generator and with the budget
  of DOC-1.7 (HUB-4.3, ECO-048, ECO-052). `nogat guide` and
  `nogat ecosystem agents` follow once the package exists (HUB-7.3).
- `docs/plans/2026-10-25-integration-dry-run.md`: the record of a dry run of
  step 7 of the data-output plan: the six heads in one environment, each
  member's offline suite, four cross-tool flows, and the failures across
  members with their causes and owners (REL-6.4, REL-6.5, DEV-10.6).
- ECO-053: a consumer that pins a producer by commit declares a supported
  range from the producer's development version (`>=0.8.0.dev0,<0.9`),
  narrowed to the release with the tag, and checks versions with that range
  and `prereleases=True` (REL-5.6); tests find repository files from the test
  file, not through the installed package (REL-2.5); DEV-10.6 and REL-6.5
  name `<package>.testing` as the producers' module in the wheel.

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
- `ecosystem.yaml` and the map follow the Kartograf and IMGWTools branches of
  the data-output work (ECO-051): plain files beside the store (`--output-dir`),
  `files[]` and the `--check` plan with its plain actions, the default roots and
  `store init`. The catalogs are the published `<tool>-command-list/1` and
  `<tool>-commands/1` (AGI-2.4, HUB-2.5) instead of `kartograf-catalog/1` and
  `imgw-catalog`, in the HUB-2.1 example too; `kartograf-store` is
  `kartograf-store/1`, the schema of its marker (DEV-19.12), as `imgw-store/1`
  is; new ids: `kartograf-result/1`, `kartograf-testing`, `imgw-archives` and
  `imgw-testing` (DEV-10.6). Retman's exchanges with both tools follow.
- `ecosystem.yaml` and the map follow Hydrolog's flood-routing branch
  (`feature/routing-network`): the documents `hydrolog-network/1` (the river
  network read by `route network`) and `hydrolog-hydrograph-csv` (the
  hydrograph table of every `route` command and, one `<id>.csv` per node, of
  `route network --output-dir`), the routing classes of `hydrolog-python-api`
  and the catalog documents `hydrolog-command-list/1` and `hydrolog-commands/1`
  instead of `hydrolog-catalog`; the notes on the IMGWTools and Kartograf files
  name `--output FILE` and `--output-dir`. Retman's planned exchange follows.
- `ecosystem.yaml` and the map follow Hydraulik's branch `feature/sfincs-swmm`:
  the three edges are `optional` (the user's own rasters and rain need none of
  them) with the facts of the code. Kartograf is a program that Hydraulik starts
  with `--output-dir` and `--check`, reading its `commands schema`, envelope and
  plan; IMGWTools and Hydrolog are the extra `rainfall` (`fetch_pmaxtp`, the four
  hietogram classes) or the documents their CLIs print, and `swmm run` and
  `model couple` read the hydrograph tables of `route network`
  (`hydrolog-hydrograph-csv`). The entry lists its `pyproject.toml`, has no
  direct data source (the `osm` access of the proof of concept is gone) and keeps
  the status `research`.
- `docs/plans/2026-10-24-data-output.md`: the Results hold the state of every
  project's branch on 2026-10-25, the pins of one project on another and the
  integration rule: until the author pushes, a pin names a local commit that
  only the uv git cache of one machine holds, so the producers (IMGWTools,
  Kartograf, Hydrolog) are pushed before the consumers.
- `standards/ADOPTION_PLAN.md`: the data-output table has a state column, and
  a table at the end gives the progress of phases 2 to 4 per project on
  2026-10-25, from each project's PROGRESS and branch; the items that wait for
  the author are named as such.

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
