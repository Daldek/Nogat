# Changelog

All notable changes to Nogat are documented here. The format follows
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/); versions of
the standard are listed in [standards/README.md](standards/README.md).

## [Unreleased]

### Added

- The kit's charts (ECO-090, step 1 of
  `docs/plans/2026-11-24-unified-charts.md`): `design/kit/nogat-chart.js`,
  Obserwator's SVG engine with Hydrolog's short time axis in minutes and its
  PNG footer as one plain ES module, and `nogat-chart.css`, scoped by
  `.nogat-chart` with the tokens' light fallbacks. `drawChart` zooms a
  chart of a time or a value alike in every GUI: a drag selects the range
  (a rectangle of x and y with `zoom: "xy"`), Ctrl with the wheel or a
  trackpad's pinch zooms around the cursor while the wheel alone scrolls the
  page, Shift or the middle button pans, a double click, `0` and „Cały
  zakres” show the whole, two fingers pinch and pan on a phone, where a
  zoomable chart is drawn at the page's width; a lone „+” before a zoom,
  then the bar „−”, „+”, „Cały zakres” and the range shown, the y axis
  fitted to it; every zoom in stops at four points of the readout's series.
  For Archiwista and Hydrograf a second unit on a right-hand axis, gap
  spans, hollow and diamond points, an x axis without labels, `onReadout`,
  `onRange` with `plotWidth()` and `zoom.set`; for every GUI `CHART_TEXTS`
  and `spec.texts`, `spec.locale` and `spec.dateFormat`, and `toPng` with
  the providers' lines. The rule DEV-15.16, two charts in the specimen and
  `design/README.md`'s „Chart” and „Charts”; browser tests in Chromium under
  the GUIs' CSP at 1440 and 390 px in both themes, fingers by DevTools'
  touch events.
- PIG-PIB's groundwater monitoring in Obserwator `v3.3.0`, a plan
  (`docs/plans/2026-11-24-pig-groundwater.md`), reviewed and approved by
  Fable for the author on
  2026-11-24: the points, the monthly verified readings captured before each
  swap, the hourly automatic measurements as an operational tier harvested
  by `OBJECTID` watermark, the provider `PIG` of class `other` under CC BY
  4.0, the lines W, WP, WK and the terms line RW; an interim capture by the
  operator from 2026-11-24.
- Large basins in one Hydrograf instance, a plan
  (`docs/plans/2026-11-16-large-basins.md`), reviewed by Fable and approved
  by the author on 2026-11-24 with his answers to the review's three points:
  the network's topology first, then parts as sets of whole JCWP of at most
  90 M grid cells, checked before any bootstrap (every JCWP in one part,
  main-river outlet edges over 10 km², no cycle, the budget), on one grid per
  basin at the author's cell size (5 m for the Barycz and the Bóbr; 1 m only
  where every JCWP's window fits the budget), joined at main-river inlets,
  side channels cut, one database for several basins and the upgrade of
  existing instances; H4's seam report on the Orla goes to the author before
  H5; Hydrograf `0.9.0`, after the small steps of `0.7.0` and the move to
  MapLibre in `0.8.0`; gauges only a possible extension.
- Interval estimation beside point estimation, a plan
  (`docs/plans/2026-11-24-interval-estimation.md`; Obserwator feedback #13),
  reviewed by Fable and approved by the author on 2026-11-24 with the
  answers to its six questions: confidence intervals of the flood,
  precipitation and low-flow quantiles computed by Hydrolog — a parametric
  bootstrap of the L-moments fits from the refits that already give the
  critical values of A², KZGW 2017's delta method for the maximum-likelihood
  fits — at 95 % and 68 % (KZGW's upper bound at β = 84 %), both stored by
  Obserwator and selectable there as bands and „[dolna–górna]”; its step N1
  adds CMP-2.3's conventions of an interval and a rule of CMP §6 on the
  coverage of interval estimators.
- Goniec, a QGIS plugin over Obserwator's server, a plan
  (`docs/plans/2026-11-24-qgis-plugin.md`, approved by the author on
  2026-11-24 with the answers to its five questions): a shell (connections,
  attribution and regulamin, HTTP caching, CSV, clipboard and HEC exports)
  with one module per kind of server, 0.1 with Obserwator's; OGC API –
  Features and a public read-only `/api/v1` in Obserwator `v3.6.0` with
  caching headers by resource class, HEC-RAS and HEC-HMS tables and HEC-DSS
  files built on the server, every daily series PER-AVER at `2400`;
  GPL-2.0-or-later.
- Latarnik, the access point and the GUI hub, a plan
  (`docs/plans/2026-11-24-latarnik.md`, approved by the author on 2026-11-24
  with the answers to its six questions) replacing stage 2
  of the GUI platform: an optional project in front of the tools' servers,
  each tool still alone; `nogat-server/1` at `GET /api/v1/server` on every
  server, `/<tool>/v1/…` passed through, limits, caching, CORS and logs at one
  door, jobs as `nogat-job/1`, flows over the registry's exchanges; a server
  for Hydrolog; every GUI a static client of its tool's `/api/v1`.
- One set of base maps in the kit, shared by every GUI, a plan
  (`docs/plans/2026-11-24-shared-base-maps.md`; the author's direction for
  Kartograf's GUI), reviewed by Fable and approved by the author on
  2026-11-24 with the answers to its nine questions: Hydrograf's three base
  maps as the catalogue `nogat-basemaps.json`, a kit module and the switcher
  `<nogat-basemaps>` with adapters for MapLibre and Leaflet (Hydrograf's move
  to MapLibre a plan of its own), the kit's grey OpenFreeMap style, Polish
  credits in the map's attribution, the setting `basemaps` with a
  deployment's copies in `basemap_mirrors`, the choice remembered in the
  browser (`nogat-basemap`, named by § 8 ust. 7 of regulamin 1.1), never a
  GUGiK entry as the default, a deployment's own base maps in its server
  settings (`basemap_extra`, Archiwista's `BasemapConfig` form) with their
  credits and their exact origins in the CSP, and Obserwator `v3.5.0`
  deprecating `gui_basemap_url` and `gui_basemap_attribution`, translated
  at start into the new settings (amended 2026-11-24, below).
- Hydrograf's map on MapLibre, a plan
  (`docs/plans/2026-11-24-hydrograf-maplibre.md`; the author's direction of
  2026-11-24), reviewed by Fable and approved by the author on 2026-11-24
  with its eight questions answered as recommended: Hydrograf's whole map
  off Leaflet and VectorGrid onto MapLibre GL JS 6.14.0 as Obserwator and
  Archiwista vendor it, in a minor after the one with the shared base maps,
  after browser tests of today's map that pass unchanged across the move;
  every zoom number one less, the pre-generated vector tiles from level 7
  and the sewer's from 9 so that each layer appears at today's scale, WebGL 2
  required, `Hydrograf.map` the only owner of the library; then the kit's
  Leaflet adapter retired (a kit minor, with the author's consent) and
  MapLibre recorded as the ecosystem's map library.
- Obserwator `v3.2.0`, two plans approved on 2026-11-23 (Fable for the
  author): `docs/plans/2026-11-16-operational-series.md` — nightly captures
  of hydro-back's hourly operational data and ČHMÚ's `recent` day by user
  systemd timers, kept as an unverified tier, replaced by precedence with
  IMGW-PIB's monthly telemetry and ČHMÚ's validated hourly year, hourly
  series with a tier column within `obserwator-series/1`, a chart of the
  current readings, `rsync` snapshots of the store on the NAS — and
  `docs/plans/2026-11-20-hydromet-providers.md` — provider adapters,
  captures of every answer (P14–P16), provider credentials, `time_unit`
  `hour`, ČHMÚ's groundwater. Step N0 of the first plan is in this entry.
  Released 2026-11-23 as Obserwator `v3.2.0` with Archiwista `v0.4.0`
  outside a release set (a REL-6.6 deviation; Nogat's release waits by the
  author's decision); the plans' Results record them, and the registry
  describes the captures and the hourly series as released.
- The reasons `missing_credentials` and `invalid_credentials` of `forbidden`
  in the error registry, for a data provider's credential that is missing
  or rejected (ERR-1); its tables regenerated. `ecosystem.yaml` describes
  the captures of `obserwator-store/1` and the hourly series of
  `obserwator-series/1`, both planned for Obserwator `v3.2.0`.
- CAMELS-PL as a data source (ECO-086, step 1 of
  `docs/plans/2026-11-22-camels-pl.md`): DEV §20 rows L and LP (the exact
  release, its DOI, CC BY 4.0), E (the E-OBS acknowledgement) and D
  (G2DC-PL+, CC0 1.0) and the terms line RE (the ECA&D/E-OBS data policy);
  DEV-20.12 says what carries them, and a GUI or REST API serves the
  E-OBS series only where the deployment turns them on; CMP-6.10 pins the
  reference cases of a published data set, such as CAMELS-PL's signatures,
  to its release. The regulamin's template and the operator's draft gain
  the blocks `camels-pl` and `e-obs`. `ecosystem.yaml`: the data source
  `camels-pl`, Kartograf's planned product `kartograf-camels-pl`,
  Obserwator's planned provider CAMELS and the planned optional edge
  Obserwator → Kartograf; `docs/ECOSYSTEM_MAP.md` regenerated.
- The kit's `<nogat-sources>` shows the lines a GUI declares for its strip,
  the attribute `screen-lines` or the property `screenLines`
  (`{text, short, links}`), after its own lines while the view's data
  carry them, such as the line of Obserwator's provider fed by files
  (ECO-087, I13 of `2026-11-21-obserwator-instance.md`); without it every
  rendering is unchanged. Documented in `design/README.md` and shown in
  the specimen.

### Changed

- Standard 1.2 opens on `develop` (HUB-6.1). DEV-20.8 is amended: the
  operational data of hydro.imgw.pl and its backend, IMGW-PIB's
  current-data API and telemetry, and ČHMÚ's `now` and `recent` are kept as
  they came, as captures in the raw root, in a dataset of the tier
  `operational` or `telemetry`; they are shown and exported only as that
  tier („dane operacyjne, niezweryfikowane”), never as the verified
  archive, and the operator sets per source whether they are served to the
  public (ECO-084). ECO-059 is amended: the deployment's timers run
  Obserwator's commands that write the raw root, and the backup of both
  roots is the deployment's `rsync` timer, not an Archiwista job.
- ECO-085, AGI-4.1: a new value of an existing field or a new form of an
  identifier stays within `/N` of a released document when a reader that
  does not know it can skip it, and every consumer that distinguishes by
  the field changes in the same plan and is deployed first; first uses are
  `time_unit` `hour` and the monthly slot of `obserwator-series/1`.
- DEV §20 is one table of provider lines (codes, text, processed text,
  order) that DEV-20.4 orders, with the short forms and the terms lines in
  tables of their own; every line keeps its code and its wording, and the
  line of a provider the table does not hold, declared by a deployment,
  follows them (ECO-087, P9 of `2026-11-20-hydromet-providers.md`).
- The GUI kit is `1.2.0` (`screen-lines`, the blocks `camels-pl` and
  `e-obs`; REL-1.4, ECO-086); regulamin 1.0 stays.
- ECO-088, the author's decisions of 2026-11-24 on CAMELS-PL: DEV-20.12
  gives what CAMELS-PL took from IMGW-PIB (discharge, water levels,
  catchment boundaries) and what is derived from it the terms line RD as
  well as S and P, and DEV-20.7's sentence that CAMELS-PL's data take no
  terms line now covers only its other data; CAMELS-PL's licence is that of
  its release's Zenodo record (2.1.0: CC BY 4.0, the E-OBS catchment series
  excluded), the data description's CC BY-NC 4.0 disregarded. ECO-060 and
  ECO-086 are amended; `kartograf-camels-pl` in `ecosystem.yaml` names RD
  and `docs/ECOSYSTEM_MAP.md` is regenerated; the CAMELS-PL plan records
  the decisions, BFI's discrepancy not reported to CAMELS-PL's authors for
  now.
- Amended the shared base-maps plan
  (`docs/plans/2026-11-24-shared-base-maps.md`) with the author's decisions
  of 2026-11-24: no base map a visitor adds in the browser, whose
  `connect-src https:` would let an injected script send data to any HTTPS
  server, but a deployment's own base maps in its server settings, each
  origin named in the CSP; and no REL-1.1 deviation in Obserwator `v3.5.0`,
  which keeps its two base-map settings deprecated and translates them at
  start.
- The GUI kit is `1.3.0` (its charts; REL-1.4, by the author's answer to
  question 2 of the charts plan, since the members of Nogat `v0.3.0`'s
  round carry `1.2.0`). The GUI platform plan's `chart-theme.js` points to
  the charts plan.

## [0.2.0] - 2026-11-22

### Added

- Release set `v0.2.0` (`release-sets/v0.2.0/`, REL-6.6, HUB-7.2), the
  release set of the round of 2026-11-21: the candidate verified by the
  workflow `verify-candidate` with each member's commit replaced by its
  annotated release tag, Kartograf `v0.8.2`, Obserwator `v3.1.0`, Hydrolog
  `v0.9.0`, Hydrograf `v0.6.0` (an app on its own lock, not installed by the
  set) and Archiwista `v0.3.3`. It carries Hydrolog 0.9.0, with the fixes
  of the formula audit of 2026-11-18 and the computation standard, and its
  consumers (plan `docs/plans/2026-11-19-hydrolog-0.9.0-consumers.md`), kit
  `1.1.0` in every GUI, the providers named by their national acronyms
  (ECO-082) and one pattern of file names (ECO-083). As before, the set is
  installed as an environment, `uv sync --locked --no-dev --python 3.12` in
  `release-sets/v0.2.0/`, not with `uv tool install` (a deviation from
  HUB-7.1, HUB-7.2 and REL-6.1).
- Standard 1.1 is published: it reaches `main` with this release, and the
  merge commit is tagged `std-1.1` (HUB-6.1); its changes are listed in
  `standards/README.md`.
- The topic document `standards/COMPUTATIONS.md`, prefix `CMP` (ECO-078):
  every formula of a project that computes is declared once by a spec,
  refuses physically impossible input and failed preconditions, warns
  outside its applicability range, never returns a non-finite or impossible
  value, and is verified by reference cases, oracles and generated range,
  type and property tests; gross defects are released at once. The
  registry's optional `computes` (HUB-2.1, its schema) marks such a
  project: Kartograf, Obserwator, Hydrolog, Hydrograf and Hydraulik. The
  topic documents, `ecosystem.yaml` and `error_registry.json` carry
  standard 1.1. Plan `docs/plans/2026-11-18-computation-standard.md`,
  step 1.
- ECO-079: an instance of a GUI that an operator other than the author runs
  may show the operator's logo and name in the top bar beside the project's
  mark, which stays as the favicon and in the top bar, the logo served from
  the GUI's own origin (DEV-15.3); it serves the operator's own regulamin in
  place of regulamin 1.0, whose statement of § 3 belongs to the author's
  instances (DEV-15.7, DEV-15.8). Plan
  `docs/plans/2026-11-21-obserwator-instance.md`, step 1.
- The kit's draft regulamin for operators, `design/kit/nogat-terms-operator.md`,
  in Polish, a template and not legal advice: the operator is the service
  provider and the controller of personal data, the software is provided as
  is under its licence, keeping the data providers' terms is the operator's
  and the author's part ends with the deployment; the fields and source
  blocks of regulamin 1.0, so a GUI builds and fills it the same way, plus
  two fields the operator writes in (`BY_HAND` in `scripts/terms.py`). Its
  hash is in `nogat-kit.json`, kit `1.1.0` (ECO-081).
- The registry names Obserwator's GUI, `obserwator gui serve`, and its
  service `obserwator-gui` with the instance section `[obserwator.instance]`
  of `nogat.toml`.
- The reference module of formulas, `standards/reference/nogat_formulas.py`
  (CMP-8.1), which every project that computes copies byte for byte:
  `FormulaSpec` and `TierBSpec` with sources, physical, applicability and
  typical ranges, test bounds, constraints, constants, outputs, properties
  and the trap checklist per family; `validate` and `check_outputs` (CMP §3,
  CMP §4) raising the project's own exceptions through a small `Errors`
  protocol and returning notices; the exact units table and `convert`; the
  generated range and type cases, `run_case`, the Hypothesis profiles and
  strategies and the property assertions (CMP-6.5, CMP-6.9); `assert_within`
  with reasons, reference cases with the tolerance of CMP-6.1 and the
  frozen-oracle reader (CMP-6.4); cards, `docs/FORMULAS.md` and the
  docstring, tolerance and spec checks (CMP-2.6, CMP-2.7, CMP-6.8). Its tests
  run it against a correct toy formula and wrong ones, each with one defect
  that a generator or an assertion catches (CMP-8.2).
- `schemas/formula/card-1.schema.json`, `nogat-formula-card/1`, the schema of
  the generated cards; `drift` reports the projects' copies of it and of the
  module.
- Hypothesis, mutmut and NumPy in the development dependencies (CMP-8.3).

### Changed

- ECO-083, DEV-19.21, DEV-15.5 (the author, 2026-11-21): a file a tool names
  for a user, a GUI's download, a REST attachment or a file a command writes
  into `output_dir` under a name it picks, is
  `<tool>_<content>_<qualifiers>.<extension>`. The kit's statistics file is
  `<project>_stats_<first>_<last>.csv` (`nogat` when the element names no
  project), was `<project>-stats-<first>-<last>.csv`; the hand-off file is
  `<producer>_handoff_<subject>.json`, the subject in lower-case ASCII with
  `-`, was `<subject>.handoff.json`; `nogat-handoff.js` exports that
  reduction as `nameSlug`. Their hashes are in `nogat-kit.json`, whose
  version stays `1.1.0`; `design/README.md`. Migration: a GUI copies the
  kit again and names its own downloads by the rule; a manual or label that
  names `….handoff.json` names the new file. Plan
  `docs/plans/2026-11-21-download-file-names.md`, step 1.
- ECO-082, DEV-2.5, DEV-20.5, DEV-20.6 (the author, 2026-11-21): an
  identifier naming a data provider uses its national acronym without
  diacritics and without its legal suffix, so ČHMÚ is `chmu` where it was
  `chmi` and IMGW-PIB `imgw` where it was `imgw-pib`: the registry's data
  sources `imgw` and `chmu` and exchange format `chmu-json/1`, the
  regulamin's block `chmu` in `nogat-terms.md`, `nogat-terms-operator.md`
  and `nogat-terms.html` (their hashes in `nogat-kit.json`, whose version
  stays `1.1.0`), `BLOCKS` of `scripts/terms.py` and `design/README.md`;
  texts for people keep „IMGW-PIB” and „ČHMÚ” and the address
  `opendata.chmi.cz` stays. A CSV's
  attribution columns are `attribution` and `terms_notice` only. Migration:
  a GUI lists the block `chmu` in its regulamin filling (`chmi` is refused)
  and copies the kit again; a project drops the CSV columns
  `attribution_source` and `attribution_processed`. Plan
  `docs/plans/2026-11-21-national-provider-names.md`, step 1.
- ECO-081: the GUI kit's version becomes `1.1.0` (the author, 2026-11-21),
  for the draft regulamin for operators (ECO-079) and the strip folded on a
  phone (ECO-080); every GUI copies the manifest for the round's releases.
  Plans `2026-11-18-computation-standard.md` and
  `2026-11-19-hydrolog-0.9.0-consumers.md` approved.
- ECO-080, DEV-20.5: on a screen up to 860 px wide the kit's
  `<nogat-sources>` folds its strip to one line, the lines cut with an
  ellipsis, then „więcej”, shown while the line cuts them, which unfolds the
  strip in place („zwiń” folds it again), and „Źródła i warunki”; wider
  screens are unchanged. The element's `expanded` property and attribute
  hold the state, `clipped` marks a cut line. Kit `1.1.0` (ECO-081). Plan
  `docs/plans/2026-11-21-phone-sources-strip.md`.
- README installs the set `v0.2.0` and names standard 1.1.

### Fixed

- The first example of `nogat-handoff/1` records Hydrolog 0.9.0's result
  (formula audit of 2026-11-18): 57.9 m³/s at 400 min and 1,046,737.6 m³,
  was 57.8786 m³/s and 1,046,712.9 m³. The Beta hyetograph is built from
  exact differences of its distribution function (audit item T35) and
  Kirpich's time of concentration uses the source's constant 0.0078 for feet
  with the exact foot (−0.136 %, item T8). The schema itself is unchanged;
  Obserwator, Hydrolog, Hydrograf and Archiwista carry the new copy in their
  releases of this set (SHA-256 `10de3e18…`).
- `set verify` syncs the core dependencies of each member's own lock into a
  throwaway environment before the member's suite, so the uv cache holds
  them for its offline install tests, as in the member's own CI. On a fresh
  cache (`verify-candidate` of candidate-7, every runner) Obserwator's
  library-install tests could not install `pydantic-core` 2.50.1 of its own
  lock offline, since the candidate's sync had cached only the set's 2.50.4.

## [0.1.1] - 2026-11-20

### Added

- Release set `v0.1.1` (`release-sets/v0.1.1/`, REL-6.6, HUB-7.2), a patch
  release set: candidate-10 (`release-sets/candidate-10/`, verified by run
  44775327473 of verify-candidate) with each member's commit replaced by its
  annotated release tag, Kartograf `v0.8.2`, Obserwator `v3.0.1`, Hydrolog
  `v0.8.1`, Hydrograf `v0.5.2` (an app on its own lock, not installed by the
  set) and Archiwista `v0.3.2`; the same 127 packages and third-party
  versions as candidate-10's lock. It carries Hydrograf's pinned images with
  nginx 1.31.9, a security fix between sets (REL-6.6), Kartograf's hotfix of
  the USDA texture classes at clay = 20 % and 27 % (HSG B becomes C on those
  cells) and the members' defect fixes of 2026-11-18. Released from a branch
  of `main` (REL-2.4), so standard 1.1, in preparation on `develop`, is not
  part of it; the published standard stays 1.0.

### Changed

- README installs the set `v0.1.1`.

## [0.1.0] - 2026-11-17

### Added

- Release set `v0.1.0` (`release-sets/v0.1.0/`, REL-6.6, HUB-7.2), the first
  release of the ecosystem: candidate-6 with each member's commit replaced
  by its annotated release tag on the member's `main`, Kartograf `v0.8.0`,
  Obserwator `v3.0.0`, Hydrolog `v0.8.0`, Hydrograf `v0.5.0` (an app on its
  own lock, not installed by the set) and Archiwista `v0.3.0`; the same 127
  packages as candidate-6's lock. The `nogat` package (HUB §7, ADOPTION_PLAN
  5.4) does not exist yet, so the set is installed as an environment,
  `uv sync --locked --no-dev --python 3.12` in `release-sets/v0.1.0/`, not with
  `uv tool install` (a deviation from HUB-7.1, HUB-7.2 and REL-6.1).
- Standard 1.0 is published: it reaches `main` with this release, and the
  merge commit is tagged `std-1.0` (HUB-6.1, ADOPTION_PLAN 0.4). Known
  deviations: the legacy `standards/templates/` and `standards/configs/`
  are owned by root, so they reach `main` unchanged and replacing them
  stays the author's step (ADOPTION_PLAN 0.1, DOC-11.1); candidate-6 was
  verified only on the author's machine by `set verify`, not by the
  workflow `verify-candidate`, which reaches `main` with this release
  (REL-6.5); with the author's approval, `develop` and `main` are merged
  locally without pull requests, as the members were, because `gh` is not
  installed (DEV-3.6, REL-2.1).
- `release-sets/candidate-5/pyproject.toml` and its `uv.lock`, universal for
  Linux, macOS and Windows (REL-6.4): Kartograf `[mcp]`, Obserwator
  `[full]`, Hydrolog `[all]` and Archiwista `[obserwator]` at the set's
  commits, the union of their `dev` groups; 127 packages, one version each.
  Hydrograf, an app, is not installed (REL-6.1).
- `scripts/ecosystem.py set verify --workdir DIR [--member P]` and the
  workflow `.github/workflows/verify-candidate.yml` (REL-6.5, ECO-077): each
  member's offline suite at its commit, in the candidate's environment or,
  for an app, on its own lock; members without the profile `tool` on Linux
  only. `set bump` moves the member's `rev` in the candidate's
  `pyproject.toml` and drops the recorded runs; `set readme --check` fails
  when the `pyproject.toml` installs other commits; `members.toml` records
  passing runs as `runs`, shown in the README.
- ECO-076, the author's decision of 2026-11-16: the first `nogat` release is
  `0.1.0` and `nogat` stays `0.y` until the author makes a release `1.0.0`
  (HUB-7.4); `pyproject.toml` and `uv.lock` carry `0.1.0`.
- The integration run of candidate-5 (`docs/plans/2026-11-16-candidate-5-integration.md`),
  the repeat the final integration run of 2026-10-25 left open: every
  member's suite in the candidate's environment and on its own lock, and
  eight flows offline. The known failures C1 to C6 (Kartograf does not treat
  `obserwator-data.json` as a store; an Archiwista test that depends on the
  umask; two Archiwista Firefox tests crashing with Playwright 1.65.2; three
  hints and plan rows; an Archiwista test that depends on timing under load)
  are left to the members' next releases.
- Release set `candidate-6` (REL-6.4): the members after their release
  documentation; `set verify` on the author's machine passes except the
  known C2 and C3, and the gate of Obserwator's release commit adds C7, a
  test that depends on the length of `TMPDIR`. The members are released
  from it, producers first: Kartograf `v0.8.0`, Obserwator `v3.0.0`,
  Hydrolog `v0.8.0`, Hydrograf `v0.5.0`, Archiwista `v0.3.0` (the plan of
  the integration run of candidate-5, „candidate-6 and the releases”).
  Documentation-only and pin-only commits ran reduced checks instead of the
  whole gate (the author's decision of 2026-11-16, a deviation from
  DEV-7.6).
- Release set `candidate-5` (REL-6.4), the members of the first joint release
  (ECO-074): Kartograf `e14bc78`, Obserwator `f4f6a8d`, Hydrolog `3ce7ee8`,
  Hydrograf `939b55f` and Archiwista `800231c`; every pin between them
  matches the set. Retman and Hydraulik apply it in their own sessions.
- `schemas/agent/command-list-1.schema.json`: the summary
  `<tool>-command-list/1` of `commands list --json` gets its schema; AGI-2.4
  no longer says that `commands list` returns `<tool>-commands/1` (ECO-075).
  Kartograf's, Obserwator's and Hydrolog's lists validate against it
  unchanged.
- ECO-074: the author names the members of a release set (REL-6.1). The
  first set is Kartograf, Hydrograf, Hydrolog, Obserwator and Archiwista;
  Retman and Hydraulik join a later set;
  Hydrolog's next release is 0.8.0. ECO-054 and the first-release-set plan
  are marked as amended.
- Release set `candidate-4` (REL-6.4), the members of the first release
  (the author's scope of 2026-11-14): Kartograf `c9afdd3`, Obserwator
  `0394af7`, Hydrolog `9e2cb61`, Retman `f6d9154`, and Archiwista as a new
  member at `0ff788e`; every consumer applied it except Hydraulik, which joins
  a later set. DEV-19.12 names Obserwator's data-root marker
  `obserwator-data.json`.

- DEV-17.6 and ECO-073 (the author's rule of 2026-11-15): an agent runs a
  job that may last more than about 10 minutes as a user systemd unit with
  its output in files, not as a background job of its session, which ends
  with the session.

- Info texts of a GUI, the author's request of 2026-11-14 (ECO-069):
  DEV-15.14 gives every text behind „(i)”, in a help popover or in
  „Objaśnienie metod” one shape (a definition, then the formula with its
  symbols and units, how to read the value and the sources), Polish and
  impersonal, without the author's or operator's experience, internal
  identifiers, development status or implementation detail the user cannot
  act on, at most about 400 characters without the formula and the sources;
  `design/README.md` gains the section „Info texts” with one example.
- The path away from IMGW-PIB after the first joint release, a draft plan
  (`docs/plans/2026-11-14-independence-from-imgw.md`, `Approved: pending`)
  with the research on ERA5 instead of PMAXTP, translated into English with
  its sources: the author's decisions of 2026-11-14 (non-commercial today;
  the release scope; D, then R, A as its check, C only on demand; a written
  question to IMGW-PIB before any commercial start), Hydrograf's parts that
  depend on PMAXTP, steps for Nogat, Obserwator, Hydrolog and Hydrograf, and
  the open questions.
- One admin panel for every GUI, the author's decision of 2026-11-13
  (`docs/plans/2026-11-13-admin-panel.md`, step 1; ECO-067): DEV-15.13 puts
  the panel at `/admin/` (`/admin` answers `308`) and its API under
  `/api/admin/`, nothing else, so a deployment protects three paths; every
  admin route checks `X-Admin-Key` in constant time against
  `<PREFIX>ADMIN_API_KEY` or `<PREFIX>ADMIN_API_KEY_FILE`, read per request,
  and refuses with `401 unauthorized` and the reason
  `admin_key_not_configured`, `admin_key_missing` or `admin_key_invalid`;
  no key is generated or logged; one core API (`feedback`, `stats`,
  `status`); the page has no footer statement, regulamin link, app menu or
  stats count, `noindex`, `Cache-Control: no-store` and CSP `'self'`.
  DEV-15.12 sends its operator routes to DEV-15.13, DEV-15.4, DEV-15.7,
  DEV-15.8 and DEV-15.11 leave out the admin page, ERR-1 points to the new
  reasons. GUI kit 0.7.0 adds `nogat-admin.js` and `.css`: the shell
  `<nogat-admin>` (top bar, key prompt, „Zgłoszenia”, „Statystyki”, „Stan”
  and the app's own sections, the section in the URL hash, `adminFetch`,
  `auth="session"`) and the views `<nogat-admin-feedback>`,
  `<nogat-admin-stats>` (CSV built in the browser) and
  `<nogat-admin-status>`, each usable alone; `design/README.md`, the
  specimen `specimen-admin.html` on a fake API in the page, contract tests
  and browser tests against a fake API under CSP `'self'`.
- Lines for GUGiK, ISRIC SoilGrids and ČÚZK data, step 1 of
  `docs/plans/2026-11-13-terms-fix.md` (ECO-068, amending ECO-060 and
  ECO-064): DEV §20 gains G, SG and Z with the strip forms GK, SK and ZK,
  and DEV-20.9 to DEV-20.11; DEV-20.4 orders S, P, PS, PP, M, C, CP, G, SG,
  Z; `<products>`, `<period>` and `<date>` have one written form; a basemap
  loaded live from GUGiK is credited on the map. DEV-15.7: a GUI loads no
  script, style or font from another server. Kit 0.6.2: `<nogat-sources>`
  shows one GK naming the products of every G of the view, SK and ZK, with
  „CC BY 4.0” linked; contract and browser tests, the strip's line budget
  at 1440 px included.
- One logging convention for every server, the author's request of
  2026-11-13 (`docs/plans/2026-11-13-unified-logging.md`, step 1; ECO-066,
  amending ECO-062 and ECO-063): DEV-12.4 to DEV-12.9 define the access,
  application and lifecycle records of `nogat-log/1` (JSON Lines with fixed
  keys, `schemas/log/record-1.schema.json`), files
  `<state_dir>/<project>/logs/<kind>-YYYY-MM-DD.jsonl` that the server deletes
  after 14 days, standard output and error with lifecycle records and errors
  reduced to their type, the User-Agent as a class (`browser`, `bot`,
  `script`, `none`), query parameters that may carry personal data without
  their values, uvicorn's and nginx's own logs off and Docker's `local`
  driver; DEV-15.10 points to them and `state_dir` joins DEV-18.1 and
  DEV-18.2. The reference module `standards/reference/nogat_logging.py`
  (standard library only) implements them, with unit and contract tests;
  `drift` reports copies of the module and of `schemas/log/` (HUB-4.1,
  DEV-15.6); mypy, pytest and coverage take in `standards/reference/`. Kit
  0.6.1: § 8 ust. 3 of regulamin 1.0 says what reaches the journal and that
  the access log keeps only the kind of program.
- One compact strip of provider lines per GUI view, the author's request of
  2026-11-13 (`docs/plans/2026-11-13-compact-attribution.md`, step 1;
  ECO-064, amending ECO-060): DEV-20.5 and DEV-20.7 put on screen only S, P,
  PS, PP and CK, the new short ČHMÚ line „Źródło: ČHMÚ, CC BY 4.0”, each
  once, with „Źródła i warunki” opening every line and the terms; products
  keep the full lines. Kit 0.5.0 adds `<nogat-sources>`
  (`nogat-sources.js` and `.css`), which derives the strip from the API's
  `attribution` and `terms_notice`, and `fillSources()` for a GUI's welcome
  window; contract and browser tests, the specimen and `design/README.md`.
- Rules for public GUIs, the author's decisions of 2026-11-13 on the
  regulamin (`docs/plans/2026-11-13-gui-terms.md`, step 2; ECO-062, amending
  ECO-061): Hydrograf, Hydrolog and Obserwator are used without signing in,
  Cloudflare Access guarding only the operator's admin parts, and Archiwista,
  private, serves no terms. DEV-15.8: the statement of what the services are
  in every footer; DEV-15.9: a rate limit per IP address held in memory only
  (300 requests in 60 s by default, `request_limit` and `request_window`;
  `429` with `Retry-After` and a Polish message); DEV-15.10: access logs
  without IP addresses, deleted after 14 days; DEV-15.11: anonymous daily
  statistics (an HMAC of IP address and User-Agent under a daily salt, in
  memory; daily totals in `<data_dir>/<project>/stats.jsonl`); DEV-15.12:
  „Zgłoś uwagę” without contact fields, with an automatic context and one
  report format, as JSON Lines in a GUI without a database. The plan records
  the nine decisions and the adoption in each public GUI, Obserwator's new
  form included.
- Station data and analyses, step N1 (`docs/plans/2026-11-12-station-data-and-analyses.md`,
  approved 2026-11-13): ECO-059, amending ECO-054, gives the station data
  of IMGW-PIB and ČHMÚ one role per project: raw data in Archiwista,
  downloaded through Obserwator's library; the production data root
  (harmonized series, catalogs, analysis results) in Obserwator, with a
  backup in Archiwista; every computation in Hydrolog. The registry's
  planned edges Obserwator → Archiwista and Obserwator → Hydrolog, the
  planned items `archiwista-raw-root`, `obserwator-data` and
  `obserwator-analyses`, and the notes of Archiwista → Obserwator and
  Hydrolog → Obserwator; `docs/ECOSYSTEM_MAP.md` regenerated.
- One regulamin for every GUI, the author's order of 2026-11-13
  (`docs/plans/2026-11-13-gui-terms.md`, step 1): GUI kit 0.2.0 adds the
  Polish template `nogat-terms.md`, the page `nogat-terms.html` generated
  from it by `ecosystem.py standard --write` (checked by the gate) and
  `nogat-terms.css`; fields filled from `[nogat.operator]` and `[nogat.gui]`
  of `nogat.toml` and from the project, blocks for data sources and personal
  data, the reference filling in `scripts/terms.py`. The app menu takes a
  `terms` attribute and ends its list with „Regulamin”. DEV-15.7 (the page
  at `regulamin.html`, the link in every view), the table `operator` in
  DEV-18.1, ECO-061; unit, contract and browser tests (the filled page under
  CSP `'self'` in both themes).
- Provider attribution in every product, the author's order of 2026-11-13
  (`docs/plans/2026-11-13-provider-attribution.md`, step 1): DEV §20 and
  ECO-060 hold the IMGW-PIB lines S and P (danepubliczne.imgw.pl and
  hydro.imgw.pl, with H for the latter), PS, PP and the monograph M for
  PMAXTP, C and CP for ČHMÚ under CC BY 4.0, verbatim; the IMGW-PIB
  terms-of-use notice N with the addresses of the terms; the surfaces and
  the forms in CSV, JSON, Parquet, ZIP, images, reports, API and CLI; data of
  hydro.imgw.pl never shown as archive. `nogat-handoff/1` gains the
  optional arrays `attribution` and `terms_notice` and stays `/1`
  (AGI-4.1); its examples carry the PMAXTP lines, and contract tests cover
  both fields. Projects copy the schema in their own branches (DEV-15.6).
- GUI platform stage 1, Nogat's steps 1 to 3
  (`docs/plans/2026-11-12-gui-links-and-handoff.md`, approved 2026-11-12):
  ECO-058 and DEV-15.4 to DEV-15.6 (the app menu, the hand-off, copies byte
  for byte); `[nogat] gui` in DEV-18.1; HUB-1.1 and ECO-050 name
  `schemas/exchange/`. The GUI kit 0.1.0 in `design/kit/`: the custom
  element `<nogat-app-menu>`, `nogat-handoff.js` (file name, text, clipboard
  with a fallback field, download, the schema check with Polish messages)
  and `nogat-kit.json`; the menu in the specimen and both mockups. Browser
  tests in `tests/browser/` (Playwright in the dev group; CI installs
  Chromium). `drift` reports each project's copies of Nogat's schemas, error
  registry, tokens, marks and kit as current, behind or modified (HUB-4.1).
- `node_provenance` in `nogat-handoff/1`, which stays `/1` (AGI-4.1): the
  optional origin of each node of a network payload, keyed by node id, each
  entry keyed by input like `provenance` (`watershed`, `runoff`, `rainfall`,
  `node` for a node's own fields) and taking precedence over it for its node.
  The schema's second example is a network of three subcatchments from
  Hydrograf; consumers on an older copy accept and ignore the field. Plan
  `docs/plans/2026-11-10-node-provenance-in-handoff.md` (step 1; B7 of
  Hydrograf's network delineation): Hydrograf's `delineate-network` writes
  it, Hydrolog's Sieć shows it and writes it back.
- Release set `candidate-3`, now the current one (REL-6.4): candidate-2's
  members with Hydrolog `759d7ef` -> `930915d`, its `origin/develop` with
  `nash_estimation` (W1) and structure-only networks (W2); Kartograf
  `d0990c8`, Obserwator `f9f4ee7` and Retman `320a7d6` unchanged. A
  candidate, not a release: no tags. `set check` reports `conflict` (exit 4)
  in Hydrograf, Hydraulik and Retman, which pin Hydrolog `759d7ef`, until
  each applies the set; candidate-2 is unchanged.
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

- The documentation states the released `v0.1.0` and `std-1.0`: the README
  installs the set from `release-sets/v0.1.0/`; `standards/README.md`,
  `standards/ADOPTION_PLAN.md` (0.1, 0.3, 0.4, 5.2 to 5.4),
  `docs/PROGRESS.md` (Status, Next, Open questions) and the plans of the
  first release set, the integration run of candidate-5, numbers from
  `main`, one set of pins, Archiwista's sets and the path away from
  IMGW-PIB record the releases and their deviations; `CLAUDE.md` records
  the deviation from HUB-7.1, HUB-7.2 and REL-6.1 until the `nogat` package
  exists. PROGRESS and the plan of Archiwista's sets record A4 and A5 as
  done (project `kaczawa`, set `2026-1`, closed 2026-11-15) and the next
  steps: Hydrograf re-processes its production from that set into a
  separate staging instance, compared with production, which switches only
  on the author's acceptance; Obserwator rebuilds its analyses with
  Hydrolog 0.8.0 after the series of the ČHMÚ stations are downloaded.
- Documentation audited on 2026-11-15 before release-set candidate-5:
  `docs/PROGRESS.md` gains the separator row of its Status table and states
  the author's scope of the first joint release (Nogat, Hydrograf, Hydrolog,
  Obserwator and Archiwista; Kartograf a pinned producer; Retman and
  Hydraulik later), the members' heads and the pins `set check` reports as
  different, the kit copies the four GUIs carry, Archiwista's step 6 of the
  unified logging and the missing candidate lock (REL-6.4) and
  `verify-candidate` (REL-6.5); the plans of the unified logging and of the
  regulamin link without a footer record their merges; `CHANGELOG.md` keeps
  one heading per kind of change under `[Unreleased]`.
- Everything is version 1 until the first release, the author's rule of
  2026-11-14 (REL-1.4, ECO-072): every schema, document type, file format,
  protocol, the GUI kit and the regulamin stay version 1 until Nogat's
  release tag on `main`, then each project's; only the author's consent
  changes a version, and agents never raise one on their own. The kit's
  `nogat-kit.json` says `1.0.0` instead of 0.7.1, its files and hashes
  unchanged; copies are compared by hashes. AGI-4.1 needs the author's
  consent to raise a released schema number; DEV-15.7 and `design/README.md`
  refill the regulamin with each copy of the kit. Nogat's own schemas are
  all `/1`.
- One place for the admin keys of a deployment, the author's decision of
  2026-11-14: DEV-15.13 and the admin section of `design/README.md` keep each
  GUI's key in `~/.config/nogat/keys/<project>-admin.key` (mode `0600`, or
  `0640` with a container's group) and hand the app only its path in
  `<PREFIX>ADMIN_API_KEY_FILE`.
- Processing lines do not describe the processing (ECO-071, the author's
  decision of 2026-11-14). CP is exactly „Dane ČHMÚ zostały przetworzone”,
  once for modified ČHMÚ data; P, PP, G, SG and Z already have detail-free
  wording and stay unchanged. Readers recognise old parenthetical CP lines
  as CP and deduplicate them; kit 0.7.1 adds CP to `LINES` and normalises
  old lines in its sources viewer. The regulamin's ČHMÚ example changes in
  place; the regulamin stays version 1.0 (only the author raises it)
  (DEV §20, DEV-20.3, DEV-20.4).
- The regulamin link without a footer, the author's decision of 2026-11-14
  (`docs/plans/2026-11-14-no-footer.md`, step 1; ECO-070, amending ECO-061,
  ECO-062 and ECO-064): DEV-15.7 links „Regulamin” in exactly the app menu,
  a small, quiet link at the foot of the left rail (the last small item of
  a phone's bottom bar or sheet) and the welcome window, where the
  „Regulamin serwisu” of `fillSources()` is its only link; no footer or
  status bar carries the link or a statement. DEV-15.8 keeps the statement
  as the opening of § 3 only, DEV-15.13 and DEV-20.5 lose their footer.
  `design/README.md` describes `.rail-terms`; the specimen and both mockups
  link „Regulamin” from the menu and the rail. A browser test pins the
  welcome window's link; the kit and regulamin 1.0 are unchanged.
- Documentation audited against the code of 2026-11-14: `docs/PROGRESS.md`
  holds only Status, Next and Open questions, without the dated snapshots
  and the finished items (DOC-6.1); the plans of the admin panel, the
  unified logging, the terms fix and the compact attribution record their
  Status and Results in every project; README, `CLAUDE.md`'s code map,
  `standards/README.md` and `design/README.md` name the GUI kit,
  `scripts/terms.py`, `tests/browser/`, the `set` commands, what `drift`
  and the gate check, the four GUIs, `test_kit_manifest.py` and the
  republication of regulamin 1.0 on 2026-11-14.

- Products carry only what the providers require and link the rest, the
  author's principle of 2026-11-13 (ECO-065, amending ECO-060 and ECO-064;
  amendments of `docs/plans/2026-11-13-provider-attribution.md` and
  `docs/plans/2026-11-13-gui-terms.md`). DEV §20 drops the terms-of-use
  notice N, our summary of the IMGW-PIB terms that also mis-stated their
  §3 ust. 2, and H, which no terms require; the terms lines name what they
  link: RD „Regulamin danych IMGW-PIB: …”, RH „Regulamin serwisu
  hydrologicznego IMGW-PIB: …”, RK „Regulamin danych PMAXTP: …”, and
  `terms_notice` holds only them. DEV-20.4 orders S, P, PS, PP, M, C, CP;
  DEV-20.7 forbids restating a provider's terms. GUI kit 0.6.0: the
  regulamin's source blocks hold the provider, its lines and the link to
  its terms or licence; `imgw-terms`, „W skrócie…” and every description
  of what a provider allows are gone; § 5 says once that the providers'
  terms govern data taken from the service, § 6, § 7 and § 9 no longer
  repeat it; regulamin still 1.0. `scripts/terms.py` has no derived
  blocks. The examples of `handoff-1.schema.json` carry RK alone; the
  hand-off stays `/1`. The provider-attribution plan lists what each
  project changes and which stored files it rebuilds.
- Regulamin 1.0 after its legal review, GUI kit 0.4.0 (ECO-063, amending
  ECO-062; `docs/plans/2026-11-13-gui-terms.md`): the review's text, about a
  third shorter with the same twelve sections, fields and blocks, and the
  operator's decisions on it. § 3 says the service is not one of IMGW-PIB,
  ČHMÚ or another provider and shows their data processed; § 8 names the
  processor's whole traffic and its own security logs, the statistics
  without „anonimowe”, the art. 11 RODO limit of the rights, no sentence on
  automated decisions, no `sessionStorage`; § 7 „na własne ryzyko” and no
  liability for linked sites; § 12 the Polish text binding; „W skrócie…”
  before the IMGW-PIB notice. DEV-15.10 covers every log, error and
  application logs included (nginx's `limit_req_log_level` under its
  `error_log` level; app loggers without `client`). `[nogat] operator`
  (DEV-18.1) gains `mail_provider`, named in § 8, and the optional
  `mail_transfer` and `processor_cookie`; `scripts/terms.py` lets the three
  optional fields be empty, and contract tests pin which fields may be.
  The plan records the review, the decisions and the author's open points,
  with drafts of an e-mail to IMGW-PIB and of a register of processing in
  `docs/plans/2026-11-13-gui-terms/`.
- The regulamin template is version 1.0, in GUI kit 0.3.0, rewritten to the
  author's decisions of 2026-11-13: one version and one date for the three
  public GUIs, a „Historia zmian” linked to the template's history; no
  reference to the act on electronic services; liability excluded except
  for intentional damage; contact by e-mail only; RODO requests answered
  within a month; the processor in two fields; the user addressed as „Ty”.
  The personal-data blocks (`cloudflare-access`, `accounts`,
  `session-cookie`, `feedback`, the derived `no-cookies`) and the field
  `log_retention_days` are gone; the data-source blocks stay. DEV-15.7
  covers public GUIs only; `[nogat] operator` (DEV-18.1) holds `name`,
  `email`, `terms_effective`, `processor` and `processor_transfer`, without
  `log_retention_days` and `cloudflare_access`. `scripts/terms.py` lets
  only `processor_transfer` be empty; contract tests pin the statement of
  DEV-15.8 in § 3 and the version against the history. The Hydrograf
  mockup's form loses its contact field.
- GUI platform stage 1 done (2026-11-12): Hydrolog, Hydrograf, Archiwista and
  Obserwator carry the kit's app menu and hand-off, merged and deployed at the
  author's request; the plan's Results record the commits, the public
  addresses (Obserwator's a placeholder on :8060 for now), the `drift`
  outcome and the candidates for kit 0.1.1. PROGRESS lists port 8060 and the
  public hosts.
- GUI plans split in two stages (the author, 2026-11-12): Nogat stays `hub`
  without a GUI. Stage 1, new plan
  `docs/plans/2026-11-12-gui-links-and-handoff.md`: a menu in every GUI
  leading to the others, one hand-off by file and clipboard (a DEV §15 rule
  and the kit's `nogat-handoff.js`), and a report of schema, token and kit copies
  in `drift`. Stage 2, `docs/plans/2026-11-01-nogat-gui-platform.md`
  retitled „the GUI hub”: one window and one sign-in in a new project
  (working name `guihub`; C1), the kit kept in Nogat `design/kit/` (C2),
  deferred until stage 1 (C3); Hydrolog's existing GUI, the published
  hand-off and Obserwator's name taken in. Stage 1 approved 2026-11-12;
  stage 2 `Approved: pending`.
- Registry: Hydrograf's routes gain „Preview a network of subcatchments while
  placing control points (areas, reach lengths, outlines)” -> `POST
  /api/delineate-network/preview` (its ADR-081, `develop` `97498bb`);
  `AGENTS.md` regenerated. `docs/PROGRESS.md`: the state of 2026-11-11
  (heads, pins, the instances, the author's open decisions) replaces the
  heads of 2026-11-10; the superseded rows of 2026-11-04 are dropped.
- Registry: Hydrograf's edge to Hydrolog gains `via: file` and the exchange
  `hydrolog-network/1`, with a note on the hand-offs (a watershed, ADR-068;
  a network, ADR-080, whose hand-off carries `node_provenance`), and
  Hydrograf's routes gain „Delineate a network of subcatchments at control
  points (closing section, tributaries, gauges)” -> `POST
  /api/delineate-network`; `AGENTS.md` and `docs/ECOSYSTEM_MAP.md`
  regenerated. Step 4 closes `docs/plans/2026-11-10-node-provenance-in-handoff.md`
  (Status done 2026-11-11, Results of steps 2 to 4: Hydrograf `824bebd`,
  Hydrolog `3b28b15`). `docs/PROGRESS.md`: Next 13 done; the release-set row
  and Next 10 name `candidate-3`, applied by Hydrograf, not yet by Retman and
  Hydraulik.
- Release set `candidate-2`: Retman `a9c04ad` -> `320a7d6` by `set bump`
  after a fetch, its `develop` once it applied the set (plan
  `docs/plans/2026-11-03-one-pin-set.md`, step 3); README regenerated.
- Every consumer applied release set `candidate-2` on 2026-11-10: Hydrograf
  `develop` `01ab00a` (head `fd0b533` after its docs), Retman `develop`
  `320a7d6`, Hydraulik `feature/sfincs-swmm` `d0f3938` (CN of water follows
  Hydrolog, 98), Archiwista `develop` `a656ee1`. `set check` after a fetch:
  every pin `ok`, exit 0; Hydraulik's Kartograf stays "not declared" (it
  calls the CLI). `docs/PROGRESS.md` (heads and pins, Next 10), the Results
  of `docs/plans/2026-11-03-one-pin-set.md` and of
  `docs/plans/2026-11-06-hydroni-instance.md` (Hydroni on set `2026-3` and
  `fd0b533`, production on `894810c`, the open items of 2026-11-08) follow.
- `CHANGELOG.md`: one `### Changed` in `[Unreleased]` (the entries of the
  second are merged into it) and the Obserwator `repo` entry once.
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
  `standards/`, `ecosystem.yaml` and `error_registry.json`, tagged
  `std-1.0` with this release; `standards/legacy/v1.0/` is now
  `standards/legacy/shared-2026-01/`, the shared standards of 2026-01-29
  that preceded Nogat. Plan: `docs/plans/2026-11-03-numbering-from-main.md`,
  step 1.

- `docs/PROGRESS.md`: the stack is merged into `develop` (`ed3b8a0`,
  2026-11-03) and its topic branches deleted except
  `feature/hydrolog-gui-mockup`; Next 7 lists the tools' branches awaiting
  review and release.

- `docs/plans/2026-11-02-archiwista-sets-for-hydrograf.md`: status of
  2026-11-03 in Results: A1 to A3 and H1 done, A4 and A5 wait for the
  author, H2 and S5 postponed until after Hydrograf v0.5.0.

- `scripts/gate.sh` follows `standards/ci/gate.sh`: `uv sync --locked`, the
  DEV-7.2 rule set, mypy over `scripts/` and `tests/`, pytest with coverage.
- **Breaking:** `scripts/ecosystem.py` reports failures by the error
  registry (HUB-4.8, ECO-044): exit 7 `data_error` for an invalid registry or
  standard, 3 `not_found` for a missing file, 4 `conflict` for a stale map,
  stale generated tables or incompatible ranges, 2 `validation_error` for a
  wrong call, 1 only for a defect; the last stderr line is the
  `nogat-error/1` document. Migration: scripts that tested for exit 1 test
  for a non-zero exit or read the document.
- Standard 2.1, the draft published as 1.0 (ECO-056), settles the
  contradictions found in its review (ECO-042 to ECO-049 and consistency
  fixes; list in `standards/README.md`). The CI template and Nogat's CI
  check commits of `hotfix/*` pull requests into `main` (DEV-4.5).
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

### Removed

- Dead and duplicated code in `scripts/`: the two Markdown cell escapers of
  `ecosystem.py` and `guide.py` are one, `guide.cell`, which now also escapes
  `<` and `>` in AGENTS.md (no current entry has one; the files are
  unchanged); `load` reads `ecosystem.yaml` through `_read`, so an unreadable
  or non-UTF-8 registry is reported like every other file; `drift` no longer
  repeats the `no tags` case `_state` already gives; `terms.fill` loses its
  `markup` option, which only a test used (GUIs fill the HTML).

### Fixed

- The registry's Obserwator entry after its ADR-017: `obserwator-store/1` is
  the raw root (`<data_dir>/obserwator-raw`, `OBSERWATOR_RAW_ROOT`), and the
  data root and the stored analyses are `obserwator-data/1` and
  `obserwator-analyses/1`, implemented rather than planned; the edges
  Obserwator → Hydrolog (analyses build runs Hydrolog's `commands batch`) and
  Archiwista → Obserwator (its adapter reads the data root) are active.

- A flaky browser test of the admin panel: the section links of the
  navigation were read once, right after signing in, and CI (run of
  `3859a30`) read none; the test now waits for the four links.

- mypy on CI: `tests/unit/test_nogat_logging.py` passed the ASGI app's
  `Awaitable[None]` to `asyncio.run`, which takes a coroutine; the test now
  wraps the call in a coroutine.

- Regulamin 1.0, published in Hydrograf and Hydrolog on 2026-11-13, is
  corrected in place on the author's decision (ECO-068, kit 0.6.2): the
  block `gugik` names „Główny Urząd Geodezji i Kartografii – GUGiK” and
  links GUGiK's conditions of reuse instead of the geoportal's terms; the
  block `esri` is gone (Esri's basemaps need Esri software or an ArcGIS
  subscription) and `scripts/terms.py` refuses it; § 8 ust. 5 names the map
  layers of other providers beside the basemap; „Historia zmian” links the
  template's history on `develop`. `design/README.md` records the version
  and each GUI's blocks; the regulamin plan and its draft register of
  processing follow.
- GUI kit 0.5.1: „Regulamin” in the app menu and „Regulamin serwisu” in the
  `<nogat-sources>` dialog and in `fillSources()` open in a new tab
  (`target="_blank"`, `rel="noopener"`); they replaced the GUI's own tab,
  which in Hydrolog ended the in-memory session and deleted the uploaded
  files. DEV-15.7 requires it of every regulamin link; browser tests click
  both links and check that the GUI's tab stays.
- Registry: Hydrolog's edge to Kartograf named the HSG rules „Hydrolog
  ADR-025”; they are Kartograf's ADR-025 (Hydrolog's ADR-0025 is the
  structure alone in the schematic). Map regenerated.
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

[Unreleased]: https://github.com/Daldek/Nogat/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/Daldek/Nogat/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/Daldek/Nogat/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/Daldek/Nogat/releases/tag/v0.1.0
