# Ecosystem standard

Standard 1.3 · in preparation on `develop`; the published version is 1.2, tagged `std-1.2` (HUB-6.1)

Shared rules for Kartograf, Obserwator, Hydrolog, Hydrograf, Hydraulik,
Retman, Archiwista and Nogat. AI agents are their primary operators, so the
tools must be easy to discover, judge and call correctly, and safe to develop.

## Zen of Nogat

1. One obvious way: one name, one place, one tool for each job.
2. Facts live where they are made; everything else is generated or linked, never retyped.
3. Generated files are never edited, and a check proves they are fresh.
4. A rule without a check is a wish: gate it, shorten it, or delete it.
5. Test before you declare: no version, pin or claim without a green run.
6. Boring tools, default settings: uv, ruff, mypy, pytest, GitHub Actions.
7. Context is the scarce resource: short files, details on demand, nothing the agent would do anyway.
8. Safe by default: read before write, check before change; the author approves merges, tags and releases.
9. Agents, code and documents use English and stable codes; end users read Polish.
10. Each project works alone; the hub adds, it never requires.
11. Write the rule when the second project needs it, not before.
12. Break freely before 1.0, but leave no shim behind.

## How to read the rules

- Every requirement is mandatory. `MAY` marks an option; there is no SHOULD.
  Capitalised MUST and MUST NOT only stress: unmarked text in a requirement
  binds equally.
- When two requirements conflict, safety and the author's approvals
  (DEV-3.3, DEV §13) come first, then the requirement that names a profile
  or is narrower, then the general one. The agent follows the higher one and
  reports the conflict as an issue in Nogat labelled `standard` (ECO-045).
- A requirement is one or two sentences, optionally followed by `*Why:*` and
  one line (a reason or an ECO reference). Dated facts and the state of named
  projects stay out of rules.
- Requirement IDs are `PREFIX-n.m` (`ERR-n` in the error registry), with
  prefix `DEV`, `DOC`, `AGI`, `ERR`, `REL`, `HUB` or `CMP`; a section is cited as
  `PREFIX §n`, for example `DEV §18`; `ECO-nnn` is a decision in
  [DECISIONS.md](DECISIONS.md).
- IDs are stable: never renumbered, never reused. A deleted requirement
  disappears and the changelog lists it. Cite IDs in ADRs, plans and commit
  bodies.
- Profiles are `tool` (installable Python package; CLI, MCP and REST
  optional), `app` (deployed service) and `hub` (Nogat), defined in DEV §1. A
  requirement or section that names a profile applies only to projects that
  have it.
- Placeholders, defined here once:
  - `<project>`: the project name in lower case as in `nogat-<project>`:
    kartograf, obserwator, hydrolog, hydrograf, hydraulik, retman, archiwista;
  - `<Project>`: the project name as in the registry (Kartograf, Obserwator, …);
  - `<tool>`: the CLI name, `interfaces.cli` in `ecosystem.yaml`: kartograf,
    obserwator, hydrolog, retman, archiwista, hydraulik; `<TOOL>` is its upper
    case;
  - `<package>`: the Python import name (`distribution.import_name`).

## Documents

| Document | Covers |
|---|---|
| [DECISIONS.md](DECISIONS.md) | Decisions behind the standard, with reasons and rejected options (ECO-…) |
| [DEVELOPMENT_STANDARDS.md](DEVELOPMENT_STANDARDS.md) | Profiles, language, git, commits, layout, uv, quality gate, naming, docstrings, tests, errors, logging, security, files and encoding, frontend (visual identity, GUI kit, regulamin, admin panel, info texts, base maps, charts), licence and contributions, agent workflow, user environment, data output, provider attribution (DEV-…) |
| [DOCUMENTATION_STANDARDS.md](DOCUMENTATION_STANDARDS.md) | File set and size budgets, README for agents and people, CLAUDE.md, AGENTS.md, llms.txt, PROGRESS, CHANGELOG, ADR, PRD, ARCHITECTURE, USAGE, templates, ecosystem user documentation (DOC-…) |
| [AGENT_INTERFACE.md](AGENT_INTERFACE.md) | Command catalog, CLI, result and error documents, MCP, REST, Python library, generated guides, languages, discoverability (AGI-…) |
| [COMPUTATIONS.md](COMPUTATIONS.md) | Formulas: tiers, ranges, preconditions, specs, errors and notices at the limits, input types and units, reference cases, oracles, generated range, type and property tests, the coverage of intervals, mutation testing, gross defects (CMP-…) |
| [ERROR_REGISTRY.md](ERROR_REGISTRY.md) + [error_registry.json](error_registry.json) | Shared error codes, exit codes, HTTP statuses (ERR-…) |
| [RELEASE_AND_DISTRIBUTION.md](RELEASE_AND_DISTRIBUTION.md) | Versioning, release procedure, channels (PyPI, GitHub Releases, MCP Registry), MCP Registry entry, dependencies between projects, release sets, support (REL-…) |
| [ECOSYSTEM_HUB.md](ECOSYSTEM_HUB.md) | Nogat role, `ecosystem.yaml`, local workspace, generated outputs, cross-project plans and requests, standard versioning, the `nogat` package (HUB-…) |
| [ADOPTION_PLAN.md](ADOPTION_PLAN.md) | Per-project changes by phase, history rewrite procedure, order |
| [ci/](ci/README.md) | Templates for `scripts/gate.sh`, the commit-message check, GitHub Actions workflows and Dependabot (DEV-7.6, DEV-7.7, DEV-13.6) |
| [reference/](reference/nogat_logging.py) | The reference module of server logs, `nogat_logging.py`, that every Python server copies byte for byte (DEV-12.9) |
| [reference/nogat_formulas.py](reference/nogat_formulas.py) | The reference module of formula specs, checks and generated tests, copied byte for byte by every project that computes (CMP-8.1) |

## Open decisions

None.

## Legacy

[legacy/shared-2026-01/](legacy/shared-2026-01/) holds the shared standards of
2026-01-29 that preceded Nogat; they were never a standard on Nogat's `main`
(ECO-056), which holds them only as this archive.
The root-owned `templates/` and `configs/` directories come from them and are
not valid for this standard; they reached `main` unchanged with `std-1.0`,
and the author replaces them (ADOPTION_PLAN 0.1, DOC-11.1).

## Changelog

- 1.3 (in preparation on `develop`):
  - A GUI with a map draws its base maps only from the kit's catalogue
    `nogat-basemaps.json`, through `nogat-basemaps.js`, and offers them in
    `<nogat-basemaps>`: the catalogue's entries in its order, the
    deployment's own base maps after them, „bez podkładu” last, the choice
    kept in the browser and never a GUGiK entry as the default; each base
    map carries its credit in the map's own attribution; the shared keys
    `basemaps`, `basemap_mirrors` and `basemap_extra` set which entries a
    deployment allows, its copies of them and its own base maps; the CSP
    names each origin and no scheme source, and an admin page's map adds
    only its one base map's origin (DEV-15.15, DEV-15.13, DEV-18.1,
    DEV-20.9, ECO-089).
  - A GUI draws its charts over axes with the kit's chart module
    `nogat-chart.js` and `nogat-chart.css`, never with a chart library or a
    drawing of its own, a circular chart or warming stripes excepted; a
    chart whose x is a time or a value, not one of a year's months or days,
    of named bars or of probabilities, zooms and pans alike in every GUI: a
    drag selects the range (of x and y on a chart of points), Ctrl with the
    wheel zooms around the cursor while the wheel alone scrolls the page,
    Shift with a drag or the middle button pans, a double click, the key 0
    and „Cały zakres” show the whole, two fingers pinch and pan; „+” under
    a chart not yet zoomed, „−”, „+”, „Cały zakres” and the range under a
    zoomed one, whose y axis fits the values shown; a PNG is the chart as
    shown with the providers' lines, a CSV the whole series (DEV-15.16,
    ECO-090).
  - A spec lists the side and confidence level of an interval and its
    method among its conventions; an interval estimator's coverage is
    simulated, seeded, from the distributions the formula fits at 30 and 60
    values with at least 1,000 samples, nightly and before each release,
    reported in `docs/FORMULAS.md` and asserted per level and element within
    three Monte Carlo standard errors for an exact method, as its source
    reports it or above a stated bound for an approximate one, with lower ≤
    upper and the intervals of the levels nested; the reference module
    gains `assert_coverage` and `assert_interval_properties`. Intervals
    beside point estimates are computed by Hydrolog and shown by
    Obserwator, which stores the levels 0.95 and 0.68 (CMP-2.3, CMP-6.11,
    ECO-091).
  - PIG-PIB's Monitoring Wód Podziemnych is a data source of the
    ecosystem: a product with its points, readings or automatic
    measurements carries W (PIG-PIB, the times of creation and acquisition,
    CC BY 4.0 by dane.gov.pl's dataset 170), WP once processed and the
    terms line RW, which links PIG-PIB's terms of reuse; a GUI view's strip
    shows W as WK; the automatic measurements without validation
    (`mwp_auto`) are operational data and the readings of the MWP database
    verified ones; G, SG and Z take the orders 9 to 11, their order
    unchanged; the regulamin's template gains the block `pig`, in place
    (DEV §20, DEV-20.5, DEV-20.7, DEV-20.8, DEV-20.13, ECO-092).
  - The GUI kit becomes version 1.3.0: the base maps `nogat-basemaps.json`,
    `.js` and `.css`, the chart module `nogat-chart.js` and `nogat-chart.css`,
    the lines W, WP and WK of `<nogat-sources>`, and regulamin 1.1, whose
    § 8 ust. 7 names the base map among the settings the browser keeps and
    whose § 5 holds the block `pig` (ECO-089, ECO-090, ECO-092).
- 1.2 (published with Nogat `v0.3.0` on 2026-11-25, tag `std-1.2`):
  - A released document, store layout or identifier grammar stays at its
    `/N` when a change adds a new value of an existing field or a new form
    of an identifier that a reader not knowing it can skip, and every
    consumer that distinguishes by the field is changed in the same plan
    and deployed on a shared store before the producer writes the addition
    there (AGI-4.1, ECO-085).
  - Operational data (hydro.imgw.pl and its backend, IMGW-PIB's
    current-data API and telemetry, ČHMÚ's `now` and `recent`) are kept as
    they came, as captures in the raw root, in a dataset of the tier
    `operational` or `telemetry`, stored, shown and exported only as that
    tier with „dane operacyjne, niezweryfikowane”, never as or within the
    verified archive; whether they are served to the public is the
    operator's setting per source. Obserwator's commands run by the
    deployment's timers write the raw root, and the backup of the raw and
    data roots is the deployment's `rsync` timer, not an Archiwista job
    (DEV-20.8, ECO-084, ECO-059).
  - A data provider's credential missing or rejected is `forbidden` with
    `details.reason` `missing_credentials` or `invalid_credentials` (ERR-1,
    `error_registry.json`).
  - DEV §20 gives the providers' lines in one table of provider lines
    (codes, text, processed text, order) that DEV-20.4 orders, a new
    provider a row of it, with the short forms and the terms lines in
    tables of their own; every line keeps its code and its wording. The
    line of a provider the table does not hold, declared by a deployment
    (an operator's own network), follows the table's lines, and a GUI
    view's strip shows, after the kit's own lines, the lines the GUI
    declares for it (`screen-lines` of `<nogat-sources>`) (DEV §20,
    DEV-20.4, DEV-20.5, ECO-087).
  - CAMELS-PL is a data source of the ecosystem: a product with its data
    carries L, naming the exact release with its DOI and CC BY 4.0, and LP
    once processed; what it took from IMGW-PIB carries S and P, what is
    derived from E-OBS the acknowledgement E and the terms line RE (the
    E-OBS data policy: non-commercial research and education), its E-OBS
    series served by a GUI or a REST API only where the deployment turns
    them on, and what is derived from G2DC-PL+ (CC0 1.0) its citation D;
    the regulamin's template gains the blocks `camels-pl` and `e-obs`, in
    place, and the reference cases of a published data set are pinned to
    its release (DEV §20, DEV-20.7, DEV-20.12, CMP-6.10, ECO-086).
  - What CAMELS-PL took from IMGW-PIB and what is derived from it carry the
    terms line RD as well as S and P; its other data take no terms line,
    except RE on what is derived from E-OBS. CAMELS-PL's licence is that of
    its release's Zenodo record; the data description's CC BY-NC 4.0 is
    disregarded (DEV-20.7, DEV-20.12, ECO-088).
  - The GUI kit becomes version 1.2.0: `screen-lines` of `<nogat-sources>`
    and the blocks `camels-pl` and `e-obs` of the regulamin (ECO-086,
    ECO-087).
- 1.1 (published with Nogat `v0.2.0`, tag `std-1.1`):
  - A file a tool names for a user (a GUI's download, a REST attachment, a
    file a command writes into `output_dir` under a name it picks) is
    `<tool>_<content>_<qualifiers>.<extension>`: the registry name, English
    content words, identifiers unchanged, ISO dates and a person's text in
    lower-case ASCII with `-`; the hand-off file is
    `<producer>_handoff_<subject>.json` (DEV-19.21, DEV-15.5, ECO-083).
  - An identifier naming a data provider uses its national acronym without
    diacritics and without its legal suffix (`IMGW`, `pl.imgw.*`, `imgw` for
    IMGW-PIB; `CHMU`, `cz.chmu.*`, `chmu` for ČHMÚ), a slug or a store
    directory of one provider's data starts with it (`imgw_hydro_daily`,
    `imgw_stations`), and a CSV carries the lines in `attribution` and
    `terms_notice` only (DEV-2.5, DEV-20.5, DEV-20.6, ECO-082).
  - On a screen up to 860 px wide the GUI sources strip folds to one line,
    the lines cut with an ellipsis and unfolded in place by „więcej”
    (DEV-20.5, ECO-080).
  - The GUI kit becomes version 1.1.0: the draft regulamin for operators and
    the strip folded on a phone (ECO-081).
  - An instance that an operator other than the author runs may show the
    operator's logo and name beside the project's mark, which stays as the
    favicon and in the top bar, with the logo served from the GUI's own
    origin; it serves the operator's own regulamin, drafted from the kit's
    `nogat-terms-operator.md`, in place of regulamin 1.0, whose statement of
    § 3 belongs to the author's instances (DEV-15.3, DEV-15.7, DEV-15.8,
    ECO-079).
  - New topic document COMPUTATIONS.md with the prefix `CMP`: every formula
    of a project that computes (`computes: true` in the registry) is
    declared once by a spec, refuses physically impossible input and failed
    preconditions, warns outside its applicability range, never returns a
    non-finite or impossible value, and is verified by reference cases,
    oracles and generated range, type and property tests; gross defects are
    released at once (CMP §1 to CMP §9, ECO-078).
- 1.0 (published 2026-11-17, tag `std-1.0`):
  - The first `nogat` release is `0.1.0`; `nogat` stays `0.y` until the
    author makes a release `1.0.0` (HUB-7.4, ECO-076).
  - `verify-candidate` runs `set verify`: members with a package in the
    candidate's environment, an app on its own lock, a member without the
    profile `tool` on Linux only; the run URL is `runs` in `members.toml`
    (REL-6.4, REL-6.5, HUB-4.9, ECO-077).
  - `commands list --json` returns the summary `<tool>-command-list/1`,
    with its schema `command-list-1`; `commands schema --json` returns the
    catalog `<tool>-commands/1` (AGI-2.4, AGI-4.1, ECO-075).
  - The author names the members of a release set; an app among them is
    released by its own tag at the set's commits and is not installed by
    `nogat` (REL-6.1, ECO-074).
  - Everything is version 1 until the first release with its tag on `main`,
    Nogat's first, then each project's: schemas, document types, file and
    database formats, protocols, the GUI kit (`1.0.0`, from 0.7.1 with its
    files unchanged) and the regulamin (1.0). Only the author's consent
    changes a version; an agent never raises a package version, a schema
    id, a format or protocol number, the kit version or the regulamin
    version on its own; kit copies are compared by hashes, not by version
    (REL-1.4, AGI-4.1, DEV-15.7, ECO-072).
  - A processing line never names the processing: CP is exactly „Dane ČHMÚ
    zostały przetworzone”; a reader treats old CP lines with parenthetical
    detail as CP, once. P, PP, G, SG and Z keep their existing detail-free
    wording. Kit 0.7.1 carries CP in `LINES` and the regulamin 1.0 with the
    ČHMÚ example corrected in place (DEV-20.3, DEV-20.4, ECO-071).
  - A public GUI links „Regulamin” in exactly the app menu, the foot of its
    left rail and its welcome window, through `fillSources()`; no footer or
    status bar carries the link or the statement, which opens § 3 of the
    regulamin only (DEV-15.7, DEV-15.8, DEV-15.13, DEV-20.5, ECO-070).
  - One shape for a GUI's info texts, behind „(i)”, in a help popover or in
    „Objaśnienie metod”: a definition, then the formula, how to read the
    value and the sources where they apply; Polish and impersonal; no
    personal experience, internal identifier, development status or
    implementation detail the user cannot act on; at most about 400
    characters without the formula and the sources, the rest in the GUI's
    guide (DEV-15.14, ECO-069).
  - One admin panel for every GUI that stores reports or statistics: the
    page at `/admin/` and the API under `/api/admin/`, nothing else to
    protect; every admin route checks `X-Admin-Key` against
    `<PREFIX>ADMIN_API_KEY` or `<PREFIX>ADMIN_API_KEY_FILE`, read per
    request, and refuses with `401 unauthorized` and the reason
    `admin_key_not_configured`, `admin_key_missing` or `admin_key_invalid`;
    no key is generated or logged; one core API for the reports, the
    statistics and the status; the page is the kit's `<nogat-admin>`, with
    no footer statement, regulamin link, app menu or stats count (DEV-15.13,
    DEV-15.4, DEV-15.7, DEV-15.8, DEV-15.11, DEV-15.12, ERR-1, ECO-067, kit
    0.7.0).
  - Products with GUGiK, ISRIC SoilGrids or ČÚZK data carry the new lines
    G, SG or Z, after CP, and a GUI view's strip their short forms GK, SK
    and ZK; a GUI loads no script, style or font from another server;
    regulamin 1.0, published on 2026-11-13, is corrected in place: the
    block `gugik` links GUGiK's conditions of reuse, the block `esri` is
    gone, § 8 ust. 5 names the map layers of other providers, and the
    history links `develop` (DEV §20, DEV-20.4, DEV-20.5, DEV-20.7,
    DEV-20.9 to DEV-20.11, DEV-15.7, ECO-068, kit 0.6.2).
  - One logging convention for every server: access, application and
    lifecycle records in `nogat-log/1` JSON Lines under
    `<state_dir>/<project>/logs/`, deleted by the server after 14 days;
    standard output and error get only lifecycle records and errors reduced
    to their type; the User-Agent as a class of four values; query parameters
    that may carry personal data without their values; uvicorn's and nginx's
    own logs off; Docker's `local` driver; `state_dir` in `[nogat]`; the
    reference module `reference/nogat_logging.py` and the schema
    `schemas/log/record-1.schema.json`, reported by `drift`; regulamin 1.0
    § 8 ust. 3 revised in place in kit 0.6.1 (DEV-12.4 to DEV-12.9,
    DEV-15.6, DEV-15.10, DEV-18.1, DEV-18.2, HUB-4.1, ECO-066).
  - Products carry only what the providers require and link their terms:
    the terms-of-use notice N and the line H are gone, the terms lines RD,
    RH and RK name the terms they link („Regulamin danych IMGW-PIB: …”),
    and no product restates a provider's terms; the regulamin's source
    blocks hold only the provider, its lines and the link (DEV §20,
    DEV-20.4, DEV-20.7, ECO-065, kit 0.6.0).
  - Every link to a GUI's regulamin, in its footer, the app menu and
    `<nogat-sources>`, opens a new tab, so the GUI's session stays
    (DEV-15.7, kit 0.5.1).
  - A GUI view shows the providers' lines in one compact strip, the kit's
    `<nogat-sources>`: S, P, PS, PP and CK, the new short form of C, each
    once, then „Źródła i warunki”, a dialog with every line and the terms,
    also in a welcome window; products keep the full lines (DEV-20.5,
    DEV-20.7, ECO-064).
  - No log of a public GUI or its proxy, access, error or application,
    holds the client's IP address; `[nogat] operator` gains
    `mail_provider`, `mail_transfer` and `processor_cookie` (DEV-15.10,
    DEV-18.1, ECO-063).
  - Public GUIs (Hydrograf, Hydrolog, Obserwator) are used without signing
    in; each shows the statement of what the services are in every footer,
    limits requests per IP address held in memory only, logs without IP
    addresses for 14 days, counts visitors in anonymous daily totals and
    takes „Zgłoś uwagę” reports without contact fields in one format; the
    regulamin is version 1.0, its processor two keys of `[nogat] operator`
    (DEV-15.7 to DEV-15.12, DEV-18.1, ECO-062).
  - A GUI open to other people serves one regulamin filled from the kit's
    template at `regulamin.html` and links „Regulamin” from every view and
    the app menu; `[nogat] operator` holds who runs the deployment
    (DEV-15.7, DEV-18.1, ECO-061).
  - Every product with IMGW-PIB or ČHMÚ data carries the lines their terms
    prescribe, verbatim, on every surface: S and P (danepubliczne.imgw.pl,
    hydro.imgw.pl with H), PS, PP and the monograph for PMAXTP, C and CP for
    ČHMÚ under CC BY 4.0, and the notice of the IMGW-PIB terms of use with
    their addresses; data of hydro.imgw.pl are never shown as archive;
    `nogat-handoff/1` gains the optional `attribution` and `terms_notice`
    and stays `/1` (DEV §20, DEV-15.5, AGI-4.1, ECO-060).
  - Numbers count from `main`: a version of the standard exists from its tag
    on `main`, and `develop` carries the next one; a document's `<n>`
    increments only past a number released on the producer's `main`. The
    drafts called 2.0 and 2.1 on `develop` are published as 1.0, and the
    shared standards of 2026-01-29 are archived as `legacy/shared-2026-01/`
    (HUB-6.1, AGI-4.1, ECO-056).
  - Agent-facing text by channel: `--json`, MCP and REST without
    `Accept-Language` are English, human-readable output follows `lang`
    (AGI-9.2, AGI-6.4, DEV-2.2, ERR-6, Zen 9, ECO-042).
  - Needs between projects are GitHub issues labelled `request` in the
    target repository; `docs/requests/` is gone (DEV-17.1, DEV-17.5,
    ECO-043).
  - Nogat's tooling reports errors by the shared registry (HUB §4, ECO-044).
  - Precedence of conflicting requirements (How to read the rules, ECO-045).
  - The standard is tagged when published to `main`, not at every change
    (HUB-6.1, ECO-046).
  - An approved plan carries an `Approved:` line (DEV-17.4, ECO-047).
  - Nogat's AGENTS.md is a routing table with links, generated from the
    `routes` of the registry and checked by the gate (HUB-2.9, HUB-4.3,
    ECO-048, ECO-052).
  - Hotfix commits are checked on entry to `main`; messages are checked on
    every pull request into `develop` (DEV-4.5, ECO-049).
  - Canonical schemas of the result envelope, error document and catalog in
    Nogat `schemas/agent/`, copied by projects with the error registry; the
    contract they encode: stdout on errors and outcomes, failed units with a
    code, `validate_command`, MCP catalog tool names, MCP families
    (AGI-2.1, AGI-2.2, AGI-3.2, AGI-3.3, AGI-4.1, AGI-4.2, AGI-5.9, ERR-3,
    ECO-050).
  - One data-output convention for tools with a versioned store: plain files
    or the store, the same options, defaults, errors and result in every tool;
    `standard` checks the marker list against the registry (DEV §19, AGI-3.4,
    AGI-4.3, DEV-18.2, ERR-1, HUB-4.7, ECO-051).
  - A consumer that pins a producer by commit supports the producer's
    development versions of the pending release (`>=0.8.0.dev0,<0.9`) and
    checks versions with that range; tests find repository files from their
    own location, not through the installed package, because members are
    installed as wheels; producers ship `<package>.testing` in the wheel
    (REL-5.6, REL-2.5, REL-6.5, DEV-10.6, ECO-053).
  - A tool whose CLI lines other projects store or pass on exposes
    `parse_command` and `format_command`; catalog example calls are canonical
    lines (AGI-2.1).
  - Projects belong to Archiwista; a `project` command is no longer an
    example of a store-only command (DEV-19.18, ECO-054).
  - Every GUI follows the visual identity in Nogat `design/`: tokens, both
    themes, the project's mark, Archiwista's shell (DEV-15.3, ECO-055).
  - Every GUI links to the others through the kit's app menu and hands data
    off as `nogat-handoff/1` through the kit's `nogat-handoff.js`; copies of
    Nogat's kit, tokens, marks and schemas are byte-identical and reported by
    `drift`; Nogat runs no GUI (DEV-15.4 to DEV-15.6, DEV-18.1, HUB-1.1,
    HUB-4.1, ECO-050, ECO-058).
  - Station data of IMGW-PIB and ČHMÚ: Archiwista orders the downloads
    through Obserwator's library and keeps the raw data, Obserwator keeps
    the harmonized series, catalogs and analysis results, Hydrolog computes
    every analysis; amends ECO-054 (ECO-059).
  - The registry's optional `gui` interface: the command that serves a
    project's browser GUI (HUB-2.1).
  - A candidate's `members.toml` holds the commit every consumer pins; the
    `set` commands check, write and move the pins, and the registry's
    optional `branch` names where a project's code lives (REL-6.4, HUB-2.1,
    HUB-4.8, HUB-4.9).
  - Consistency fixes: approvals in ADOPTION_PLAN follow DEV-3.3; DEV-3.6
    covers the `main` → `develop` pull request and claims only what the
    ruleset enforces; DEV-6.3 covers environments, not wheel checks; a
    security fix is a patch release set (HUB-7.4, DEV-13.6); AGENTS.md is
    required for tools with a CLI (DOC-1.1); the hub's CI (DEV-7.7);
    `nogat doctor` reads tool members (HUB-7.3); description limits only in
    DOC-1.7; DOC §2 names `pyproject` as the master description; the error
    tables are generated from `error_registry.json` with an anchor per code
    (ERR-4); ADR statuses include `amended by …` with a date (DOC-8.1).
  - Zen of Nogat; every requirement mandatory, `MAY` for options, no SHOULD
    (ECO-033).
  - The registry holds structure only; the drift command reads versions and
    pins from the repositories (HUB §2, HUB-4.1, ECO-034).
  - Minimal support (the latest release, on the CI platforms) and three
    channels, PyPI, GitHub Releases and the MCP Registry; the rest waits for a
    user (REL §3, REL-7.1, ECO-035, supersedes ECO-032).
  - Three profiles, `tool`, `app` and `hub` (DEV §1, ECO-036).
  - One release path: release pull request, merge commit into `main`,
    annotated tag, hotfix branch; the `verify-candidate` workflow for release
    sets; `nogat` installed from its git tag until its members are on PyPI
    (REL §2, REL §6, HUB §7, DEV-3.6, ECO-037).
  - Commit messages and authors are checked once, on entry to `develop`
    (DEV-4.5, ECO-038).
  - One plan kind, one request list, a short PROGRESS (DEV-17.4, DEV-17.5,
    DOC §6, ECO-039).
  - Dependabot for GitHub Actions only; the audit informs (DEV-13.6,
    ECO-040).
  - Open decisions settled: Hydraulik stays MIT (ECO-041), the `nogat`
    package ships the registry (HUB-7.3), the MCP start form is settled at the
    rename (ADOPTION_PLAN 6.1).
  - Added to the 2.0 draft earlier the same day: exchanged data in
    the registry (ECO-024, HUB-2.5 to HUB-2.7); release sets and the `deps`
    comparison (ECO-025, REL §6, HUB-4.6); the user package `nogat` and the
    `nogat-` prefix (ECO-026, ECO-022, HUB §7); removal of Nogat's legacy
    scripts and data (ECO-027); one user environment for all tools (ECO-028,
    DEV §18); producers' testing modules (DEV-10.6); protected branches
    (ECO-030, DEV-3.6); external contributors keep their identity (ECO-031,
    DEV-16.5); ecosystem user documentation (DOC §12); gate and CI templates
    in `ci/`, with Nogat's own gate in CI; generated `docs/ECOSYSTEM_MAP.md`
    (HUB-4.5).
  - Merged IDs: DEV-6.6 into DEV-6.4, REL-1.2 into REL-1.1, REL-6.3 into
    REL-6.2, REL-7.2 and REL-7.3 into REL-7.1.
  - Deleted IDs: DEV-3.2, DEV-8.4, DEV-11.2, DEV-16.3, DOC-1.3, DOC-5.5,
    DOC-6.2, DOC-9.2, AGI-10.2, AGI-10.3, AGI §11, REL-5.5, HUB-2.2, HUB-4.4,
    HUB-5.1, HUB-5.3, HUB-6.2, and the third-party tools item of HUB-1.1.
  - The draft called 2.0 (2026-10-19): rewritten from project practice;
    English-only documentation; agent-first interface standard; shared error
    registry; `src` layout; uv; release and distribution channels; hub
    requirements (ECO-004).
