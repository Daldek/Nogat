# Plan: a portfolio for public-sector work as a subcontractor

Approved: pending

Status: a draft of 2026-11-17 from the author's direction of the same day. It is not approved, so no code starts (DEV-17.4). The design marks its own proposals „[proposed]”. It changes the order of future work, not the decisions already made; where it meets one, Conflicts names it with options for the author.

Requirements: DEV-17.4, DEV-17.5 and DEV-3.4 (each project in its own session and branch), DEV-17.2 (decisions as ADRs), DEV-3.3 (merges and tags with the author's approval), DEV-2.1 (language), DEV §15 (GUIs), DEV §20 (provider attribution), REL (releases).

## Goal

The ecosystem's work can be shown to a general contractor of a public-sector project as proof of competence in water and environmental data, so that its author can join such projects as a subcontractor or data and map specialist. The proof is a portfolio of public, verifiable results, not a product for sale.

## The author's direction (2026-11-17)

- The target is the public sector (local government, water administration, universities), first as a subcontractor; small direct orders and own tenders come later, if ever.
- The clients are public institutions that can obtain their own data licences (IMGW-PIB included), so the licences of the ecosystem's sources do not block this work. [proposed] A deployment still names whose licence covers which data: as a subcontractor the author processes the client's data on the client's licence.
- The niche is water and environmental data; the advantage is domain knowledge, not general portal building.

## What a general contractor checks [proposed]

1. Results on real public data that anyone can open: a running instance, a map, a dataset.
2. Compliance with the standards that public tenders name: metadata (DCAT-AP-PL, GeoDCAT-AP, INSPIRE where required), OGC services (WMS/WMTS), coordinate systems (EPSG:2180 in Poland), accessibility (WCAG 2.1 AA, the act on digital accessibility), personal data (RODO).
3. Work that can be handed over: a reproducible installation, documentation in Polish, tests, versions and a changelog.
4. Short case descriptions that a reference or an offer can quote.

## What exists (2026-11-17)

| Need | In the ecosystem |
|---|---|
| Real results on public data | Hydrograf at hydrograf-test (the Kaczawa, 792 km², set `kaczawa/2026-2`), Hydroni (area h07, 2,941 km²), Obserwator at obserwator-test (IMGW-PIB and ČHMÚ series and analyses, 4,036 stations), Hydrolog at hydrolog-test, Archiwista at archiwista-test, the SFINCS model of the Kamiennik (Hydraulik) |
| Provenance and licences | Kartograf's sidecars (`kartograf-meta/1`: request, CRS, licence, dates, SHA-256), Obserwator's stores, Archiwista's closed sets with `pins_sha256`, the attribution lines of DEV §20 |
| Coordinate systems and formats | EPSG:2180 (PL) and EPSG:5514 (CZ) in Kartograf; GeoPackage and GeoTIFF |
| Versions, tests, changelogs | REL, the gates, the release set `v0.1.0` |
| RODO | the regulamin 1.0 of the GUIs, minimal feedback data |
| Polish user texts | the GUIs; Hydrograf's guide and presentation |
| Reproducible installation | Hydrograf's Docker Compose; the others as `uv` packages run by systemd units |

Missing: metadata in DCAT-AP-PL or GeoDCAT-AP, OGC services (WMS/WMTS), an accessibility rule and its checks, one installation path for every GUI, documented backups and updates, case descriptions, and a register of references.

## Conflicts with existing decisions

- C1. Archiwista is already a catalog of the stores and projects. The direction says „no own catalog”. Options:
  - **A.** Archiwista stays an internal tool and exports DCAT for a public CKAN;
  - **B.** Archiwista also serves a DCAT endpoint that dane.gov.pl or CKAN harvests.

  A is safer for a client, B cheaper. [proposed] A first; B only if a client asks.
- C2. DEV-2.1 keeps all documentation in English; deliverables for Polish clients need Polish. [proposed] A deviation: user and deployment guides of a delivered component may be Polish, as the GUIs' texts and Hydrograf's guide already are; developer documentation stays English.
- C3. The register of references cannot live in Nogat: its repository is public, and a client's name, scope and acceptance protocol may be confidential. [proposed] A private place outside every public repository, chosen by the author; Nogat keeps only public case descriptions approved by the client.
- C4. Nogat „downloads and computes nothing itself”. A demo stack (CKAN, map server) is deployment, not a tool. Options:
  - **A.** a new private or public deployment repository;
  - **B.** `deploy/` in Nogat, as configuration only.

  [proposed] A, to keep the hub's scope.

## Steps [proposed]

Each step is small enough to be one branch of one project, and each ends in something that can be shown.

| Step | Project | Result | Shows |
|---|---|---|---|
| P1 | Nogat | DEV §15 gains an accessibility rule (WCAG 2.1 AA for every GUI, a declaration of accessibility per deployment); the e2e suites of the four GUIs run axe-core on their main views | WCAG |
| P2 | each GUI | the violations P1 finds fixed, the declaration of accessibility per public instance | WCAG |
| P3 | Archiwista | export of a closed set to DCAT-AP-PL (JSON-LD and Turtle) from the existing sidecars and pins, validated by SHACL in its tests; GeoDCAT-AP fields where the sidecars have them | metadata |
| P4 | deployment (C4) | a demo: one closed set → its DCAT in CKAN (Docker) → one Hydrograf result and one Kartograf product as WMS from QGIS Server with a QML style, EPSG:2180 | the whole chain |
| P5 | Kartograf, Hydrograf | GeoTIFF outputs as COG where they are served; styles (QML, SLD) shipped beside the products the demo serves | OGC readiness |
| P6 | each GUI | one installation path (Docker Compose or one documented `uv` path), backup and update runbooks in Polish | handover |
| P7 | Nogat (public) | case descriptions in Polish: the Kaczawa (watershed parameters from a closed data set, 792 km²), the h07 area (2,941 km² by PGW units), the Kamiennik flood model, the IMGW-PIB and ČHMÚ station archive with analyses; each with its data, method, standards and a link | portfolio |
| P8 | private (C3) | the register of references: client, year, scope, acceptance document, how metadata and maps were done | references |

Order: P1, P3 and P7 first (cheap and visible), then P4 (the demo), then P2, P5 and P6. INSPIRE (ISO 19115/19139) only when a client is bound by it.

## Out of scope

- A portal or catalog of our own beyond Archiwista.
- Being the general contractor of a public tender, SLA guarantees, or a company structure: not before references exist.
- Commercial offers to companies (the author's decision of 2026-11-17).

## Open questions

1. C1: Archiwista's DCAT as an export only (A) or also as a harvest endpoint (B).
2. C2: the deviation for Polish deployment documentation.
3. C3: where the register of references lives.
4. C4: where the demo stack lives.
5. Which public datasets the demo publishes first: the Kaczawa set, an Obserwator series, or both.
6. Whether dane.gov.pl harvests DCAT-AP-PL directly, or only through its own formats: to be checked before P3 fixes its output.
