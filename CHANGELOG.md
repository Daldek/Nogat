# Changelog

All notable changes to Nogat are documented here. The format follows
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/); versions of
the standard are listed in [standards/README.md](standards/README.md).

## [Unreleased]

### Changed

- Release set `candidate-2`: Hydrolog `3b84db6` -> `759d7ef`, its
  `origin/develop` after it applied the set (Obserwator `f9f4ee7`, gate
  green), recorded by `set bump` after a fetch; README regenerated. Kartograf,
  Obserwator and Retman unchanged.
- The author's decisions of 2026-11-09 on the open questions of
  `docs/PROGRESS.md`: F6 is closed without a further rewrite of Hydrograf's
  `develop` or IMGWTools (rollback procedures and `candidate-1` name the
  current hashes); `affine<3` is a watch item until pyflwdir 0.5.13;
  Hydraulik stays `research` until `feature/sfincs-swmm` is merged; the
  merge order of `fix/hub-gaps` and `feature/data-output` is stale. Open:
  the publication of 1.0 and the root-owned legacy templates (the author's),
  `docs/CLA.md`, and the two plans below without a record of approval.
- `ecosystem.yaml`: Hydraulik's Kartograf edge names the BDOT10k GeoPackage
  (land cover and roads) that `terrain download` fetches; roads come from
  BDOT10k through Kartograf, not OpenStreetMap, and the entry keeps no direct
  data source. `docs/ECOSYSTEM_MAP.md` regenerated.
- `docs/plans/2026-10-25-integration-dry-run.md` and
  `docs/plans/2026-10-25-final-integration.md` carry `Approved: 2026-10-24`,
  the approval of the data-output plan whose step 7 they are (DEV-17.4);
  `2026-10-20-first-release-set.md` and `2026-10-20-unified-gui.md` have no
  record and keep none.

- The example of `nogat-handoff/1` carries Kamiennik's longest flow path (`flow_path_length_km` 15.88, `flow_path_slope_m_per_m` 0.0114), which Kirpich needs since Hydrolog `29138cc` (plan `docs/plans/2026-11-05-official-tc-inputs.md`); its `result` is Hydrolog's for it: 57.8786 m³/s at 400 min, 1,046,712.9 m³.

- Obserwator's registry `repo` is `https://github.com/Daldek/Obserwator` after the repository rename (plan step 5); HUB-3.1 and the ECO-057 note follow.

- IMGWTools becomes Obserwator with v3.0.0 (ECO-057, plan
  `docs/plans/2026-11-03-imgwtools-to-obserwator.md`, step 1). Registry: the
  project `Obserwator`, distribution and import name `obserwator`, the
  interfaces `obserwator`, `obserwator mcp` and `obserwator server`, its
  routes, the ids `obserwator-*` provided and consumed (`imgw-store/1` is
  `obserwator-store/1`, and likewise the others); the repository URL stays.
  HUB-3.1: a checkout is the directory named like the repository (the last
  segment of `repo`), so `deps` and `drift` read Obserwator from
  `IMGWTools/`; `drift` also matches a requirement by its
  `[tool.uv.sources]` URL, which finds Hydrograf's `imgwtools` pin. The
  standard texts (DEV-10.6, DEV-19.12 `obserwator-store.json`, the
  placeholders), ADOPTION_PLAN (6.1: the final `imgwtools` release points to
  `nogat-obserwator`), the error registry, the CI template's audit list, the
  design mark `obserwator.svg`, the token `--tool-obserwator` and the
  Hydrolog mockup follow; `AGENTS.md` and `docs/ECOSYSTEM_MAP.md` are
  regenerated. The provider IMGW-PIB and dated records keep their names.

- The standard is 1.0: numbers count from `main` (ECO-056). A version of the
  standard exists from its tag on `main` and `develop` carries the next one
  (HUB-6.1); a document's `<n>` increments only past a number released on
  the producer's `main` (AGI-4.1). The drafts called 2.0 and 2.1 are 1.0 in
  `standards/`, `ecosystem.yaml` and `error_registry.json`, to be tagged
  `std-1.0`; `standards/legacy/v1.0/` is now `standards/legacy/shared-2026-01/`,
  the shared standards of 2026-01-29 that preceded Nogat. Plan:
  `docs/plans/2026-11-03-numbering-from-main.md`, step 1.

- `docs/PROGRESS.md`: the stack is merged into `develop` (`ed3b8a0`,
  2026-11-03) and its topic branches deleted except
  `feature/hydrolog-gui-mockup`; Next 7 lists the tools' branches awaiting
  review and release.

- `docs/plans/2026-11-02-archiwista-sets-for-hydrograf.md`: status of
  2026-11-03 in Results: A1 to A3 and H1 done, A4 and A5 wait for the
  author, H2 and S5 postponed until after Hydrograf v0.5.0.

### Added

- Release set `candidate-2`, now the current one (REL-6.4, HUB-4.9):
  Kartograf `d0990c8`, Obserwator `f9f4ee7`, Hydrolog `3b84db6` and Retman
  `a9c04ad`, the heads of their `origin/develop` on 2026-11-10, recorded by
  `set bump`. Retman is recorded as a member of the first release set (D3 of
  `docs/plans/2026-10-31-archiwista-projects.md`); Archiwista stays outside
  it. `set check` reports `conflict` until the consumers apply it: all of
  them pin candidate-1's commits, Hydrograf Hydrolog `4fad769`. Hydrolog
  applies first, because uv carries its Obserwator pin into consumers that
  install its `pmaxtp`, `gui` or `all` extra. Heads, pins and their lag:
  `docs/PROGRESS.md`; the order of the moves and what each meets: Results of
  `docs/plans/2026-11-03-one-pin-set.md`.
- `SECURITY.md`, `CONTRIBUTING.md` and `CONTRIBUTORS.md`, adapted from
  Archiwista's to the hub (DEV-13.7, DEV-16.2, DEV-16.4); `docs/CLA.md` and
  the pull-request template's CLA box wait for the author's approval of the
  text, and the entry left the Deviations of `CLAUDE.md`.
- `hydrolog-testing` in the registry: Hydrolog provides it, and Hydraulik's
  edge to Hydrolog exchanges it, because Hydraulik's contract tests read the
  `route network` tables and the `precip hietogram` envelope as
  `hydrolog.testing` builds them (DEV-10.6, Hydrolog ADR-0011, Hydraulik
  ADR-0010); `docs/ECOSYSTEM_MAP.md` regenerated.

- A station's series from Archiwista to Hydrolog (plan
  `docs/plans/2026-11-05-archiwista-series-to-hydrolog.md`, D5): Hydrolog
  provides `hydrolog-series/1`, carried inside `nogat-handoff/1` (unchanged);
  Archiwista depends on Hydrolog (`kind: data`, `via: [file]`, `exchange:
  [hydrolog-series/1]`); `docs/ECOSYSTEM_MAP.md` regenerated.

- One set of pins (plan `docs/plans/2026-11-03-one-pin-set.md`, step 1):
  `release-sets/candidate-1/members.toml` holds Kartograf, Obserwator and
  Hydrolog at the heads of `origin/develop`, and its `README.md` is generated
  from it (gate: `set readme --check`). `scripts/ecosystem.py set check`
  lists every consumer's pin, read at `origin/<branch>` after a fetch,
  against the set and fails with `conflict` when one differs; `set apply
  --project P [--path DIR]` rewrites P's `[tool.uv.sources]` `rev` and
  `git+` URL refs to the full commits; `set bump P [--rev REF]` records a
  member's commit. The registry's optional `branch` names where a project's
  code lives (Hydraulik `feature/sfincs-swmm`); plan D2 says `conflict`
  (exit 4, HUB-4.8) instead of exit 1 (REL-6.4, HUB-2.1, HUB-4.9).

- `docs/plans/2026-11-02-archiwista-sets-for-hydrograf.md` (decided by the
  author on 2026-11-02, D6 and D12 open): Archiwista alone writes Kartograf
  data into the store it shares with Hydrograf; Hydrograf's bootstrap reads
  one closed set of a project strictly (`--project`, `--set`, the SHA-256 of
  every pin, the set's `pins_sha256`, registry codes with hints naming
  Archiwista's actions) and refuses `--bbox`, `--sheets` and
  `--boundary-file` against the shared store. Steps Kartograf (optional),
  Archiwista (the area fix; draft sets, „zestaw w budowie”, with
  `state`, `closed_at`, `closed_by` and `pins_sha256` in
  `archiwista-project/1`, a closed set frozen; the deploy on :8090;
  Kaczawa's directory; the set of NMT 5 m 2020, BDOT10k and HSG built and
  closed by the author in the web interface), Hydrograf (ADR-067, staging),
  S5 and the registry, whose `archiwista-project/1` gains the rule that
  consumers read only closed sets; the coverage of the Kaczawa area, the
  modes Kartograf's writers leave and the author's decisions D1 to D12
  (HUB-5.2, DEV-17.4).

- Registry: an optional `gui` interface, the command that serves a project's
  browser GUI (HUB-2.1, `schemas/ecosystem.schema.json`), listed in the
  interfaces of `AGENTS.md`. Hydrolog's is `hydrolog gui serve` (127.0.0.1:8070
  by default, or the module `hydrolog.gui:gui_module` of the entry point group
  `nogat.gui`), with the route „Open Hydrolog's GUI in the browser” and
  `hydrolog-gui` in its `provides`. N2 of
  `docs/plans/2026-11-02-hydrolog-gui.md`.

- `schemas/exchange/handoff-1.schema.json`: `nogat-handoff/1`, the envelope
  of data handed from one tool's GUI to another's (`created_at`, `producer`,
  `subject`, `provenance`, a domain-document `payload` such as
  `hydrolog-network/1`, an optional `result` for comparison), copied by
  projects like `schemas/agent/`; its example is the complete hand-off of
  Hydrolog's GUI plan (D15); `tests/contract/test_handoff_schema.py`. Item 6
  of `docs/plans/2026-11-01-nogat-gui-platform.md`, approved by the author on
  2026-11-02 ahead of the rest as N1 of `docs/plans/2026-11-02-hydrolog-gui.md`.

- `design/`: the shared visual identity of the ecosystem's GUIs, from
  debever.pl and Archiwista: `tokens.css` (light and dark), one 32 px mark
  per project in `marks/`, guidelines in `README.md` and `specimen.html`;
  `tests/contract/test_design.py` checks WCAG 2.2 AA contrast and a mark and
  accent for every project of `ecosystem.yaml`. Plan
  `docs/plans/2026-11-01-visual-identity.md`, approved 2026-11-01.
- DEV-15.3 and ECO-055: every GUI follows the identity in `design/`, with
  Archiwista's shell (top bar, navigation rail, resizable side panels); the
  `--rail-*` tokens and the layout guidelines; adoption rows for Archiwista,
  Hydrograf and IMGWTools in `standards/ADOPTION_PLAN.md`.
- `design/mockups/hydrograf/`: a static, clickable mockup of Hydrograf in the
  identity and Archiwista's shell (map and charts as inline SVG).
- `design/mockups/hydrolog/`: a static, clickable mockup of Hydrolog's GUI
  with numbers from the real CLI. The hydrograph section has no compute
  button and no variants: its result follows every change of the data. The
  network section draws the schematic vertically (sources at the top), opens
  the settings of any node in `hydrolog-network/1` terms on click and keeps
  an explicit compute.
- AGI-2.1: a tool whose CLI lines other projects store or pass on exposes
  `parse_command(line)` and `format_command(command, options=…, run=…)`, the
  canonical line being the form of every catalog example call; other tools
  MAY (Kartograf and IMGWTools have both).
- DEV-19.2 names `store_root()` as the shared read-only accessor of the default store root in
  the library of every producer (Kartograf and IMGWTools have it).
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
- `docs/plans/2026-10-25-final-integration.md`: the record of the final run at
  the data-output heads (the eight heads in one environment, each member's own
  gate, eight cross-tool flows), its failures F1 to F8 with causes and owners,
  and the commits that fixed them; Hydrograf and Archiwista stay a known
  incompatible pair (`affine`) until pyflwdir 0.5.13 (REL-6.5, DEV-10.1).
- ECO-053: a consumer that pins a producer by commit declares a supported
  range from the producer's development version (`>=0.8.0.dev0,<0.9`),
  narrowed to the release with the tag, and checks versions with that range
  and `prereleases=True` (REL-5.6); tests find repository files from the test
  file, not through the installed package (REL-2.5); DEV-10.6 and REL-6.5
  name `<package>.testing` as the producers' module in the wheel.
- `docs/plans/2026-10-31-archiwista-projects.md` (approved 2026-10-31):
  projects leave Kartograf and IMGWTools before their first tags and belong
  to Archiwista alone (`archiwista-project/1`: area, pins of any producer,
  activity, exports); each producer keeps download, check and the store and
  gains the command of a stored version; steps producers first, decisions D1
  to D7 settled as recommended (HUB-5.2, DEV-17.4).
- ECO-054: projects belong to Archiwista. The registry lists
  `archiwista-project/1` and drops `kartograf-project/1` and
  `imgw-project/1` from Kartograf, IMGWTools and the edges of Retman and
  Archiwista; `kartograf.testing` no longer builds projects; the store read
  APIs name `command_for_file` and `command_for_version`.
- Archiwista's route `archiwista project-export`: the input data of a
  project's set as flat category folders or a ZIP (ECO-054).

### Changed

- Obserwator's registry `repo` is `https://github.com/Daldek/Obserwator` after the repository rename (plan step 5); HUB-3.1 and the ECO-057 note follow.

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
- `ecosystem.yaml`: Hydrograf's `python_manifests` is `backend/pyproject.toml` alone.
  Hydrograf replaced `backend/requirements.txt` with uv and `backend/uv.lock`
  (`a115135`), and `deps` noted the missing file.
- `ecosystem.yaml`: `uses` of Hydrograf's edge to Kartograf names the calls of its
  migration (`download_landcover`, `calculate_hsg`, `hsg_statistics`, `iter_store`,
  `list_segments`) instead of the removed `LandCoverManager` and `HSGCalculator`,
  and drops `Bdot10kProvider`, which only Hydrograf's tests patch.
- `docs/plans/2026-10-24-data-output.md`: the Results hold the state of every
  project's branch on 2026-10-25, the pins of one project on another and the
  integration rule: until the author pushes, a pin names a local commit that
  only the uv git cache of one machine holds, so the producers (IMGWTools,
  Kartograf, Hydrolog) are pushed before the consumers.
- `standards/ADOPTION_PLAN.md`: the data-output table has a state column, and
  a table at the end gives the progress of phases 2 to 4 per project on
  2026-10-25, from each project's PROGRESS and branch; the items that wait for
  the author are named as such.
- DEV-19.6, DEV-19.10, DEV-19.11 and DEV-19.20: a plain `output_dir` that is,
  or lies in, a store is refused before any request with `details.paths` the
  output directory (a store only below it is reported for each target's
  path); in store mode `--check` lists a root that is a `conflict`
  (`nested_store`, `not_empty`) as one `conflict` action of a successful plan
  and raises `store_unavailable` (`no_marker`) and an unreadable marker
  (`data_error`); both producers do the same.

### Fixed

- `tests/integration/test_check_commits.py` pins the commit check's settings
  (`GATE_CHECK_AUTHOR=1`, `GATE_AUTHOR_EMAIL`): it inherited CI's
  `GATE_CHECK_AUTHOR=0`, so the author test failed in every CI run since
  2026-11-04.
- Audit the 2026-10-28 project branch heads and manifests in
  `docs/PROGRESS.md`; mark the early adoption and data-output snapshots as
  historical, and record completed `hydrolog.testing`, consumer migrations,
  remaining smoke/documentation work and the still-open integration repeat.
- `docs/PROGRESS.md` reconciles adoption and integration status with the
  recorded 2026-10-25 fixes and pushed consumer pins; removes the stale
  “nothing is pushed” claim and makes the pending integration repeat, F6
  history work and separate-environment requirement explicit.
- `deps` no longer reports conflicts between overlapping ranges such as
  `<3` and `>2.5`.
- `drift` keeps VCS refs containing `/` (`@release/0.8`), labels a project
  without manifests "no manifest", and takes the newest final release tag as
  latest instead of a release candidate sorted after it.
- `drift` reads `[tool.uv.sources]` of a `pyproject.toml`: a `git` source
  with `rev`, `tag` or `branch`, a `path` or a `url` replaces the
  requirement's own pin, as uv installs it, so Hydrograf's commit pins of
  Kartograf, Hydrolog and IMGWTools are no longer shown as ranges that
  exclude the latest tag.
- `docs/PROGRESS.md`: Hydrograf's row of 2026-11-03 names `develop`
  `d62646c`, the `certifi` exception to its freeze, the rebuild and the
  rollback image; Next 4 no longer says `feature/visual-identity` is
  unmerged.
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
