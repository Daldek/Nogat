# Plan: verified formulas in every project that computes

Approved: pending (requested by the author on 2026-11-18: „zaplanuj cały standard dla takich testów, który będzie dostępny na poziomie Nogata i zaciągany do pozostałych projektów”)

Status: steps 1 and 3 in progress.

Requirements: CMP §1 to CMP §9 (new, step 1), HUB-6.1, HUB-5.2, DEV-10.4, DEV-12.9 (the pattern of a reference module copied byte for byte), AGI notices, ERR-3.

## Goal

Every formula of Hydrolog, Obserwator, Hydrograf, Kartograf and Hydraulik is declared once, behaves defined at and beyond the limits of its inputs, and is verified against published reference cases, independent oracles and generated range, type and property tests, so that academics can audit it from the repository alone; defects found on the way are fixed, gross ones released at once.

## The author's decisions (2026-11-18)

- Scope: every project that computes, Hydrolog and Obserwator first.
- Physically impossible input → error; outside the formula's applicability → result with a warning; added on Fable's review: a failed precondition → error (CMP-3.2).
- Gross defect as CMP-9.1, released urgently (CMP-9.2); narrowed on Fable's review: a wrong equation or constant only in a document, with correct code, is an ordinary defect; a wrong unit or range in a user-facing document stays gross.
- Sources: open ones now; the author supplies scans or PDFs of Polish textbooks later (the list: step 9).
- Fable reviewed the first draft (`~/workspace/wt/logs/inventory/FABLE-REVIEW.md`); the standard of step 1 takes its issues 1–22 except: an `unreferenced` formula stays exported with an `info` notice (CMP-5.1) instead of being withdrawn; sensitivity tables and uncertainty propagation are left out, as it advised.
- A handbook of applied hydrology for Hydrolog: Polish, Markdown, CC BY 4.0 (step 8).

## State on 2026-11-18

Inventories of every slice by twelve read-only agents (`~/workspace/wt/logs/inventory/`):

| Project | What it computes | Today's checks | Today's tests |
|---|---|---|---|
| Hydrolog | ~300 formulas: tc, SCS-CN and CN tables, four unit hydrographs, convolution, hyetographs, areal precipitation, routing schemes, flood and low-flow frequency, trend and homogeneity tests, regime, characteristic values, meteo indices and SPI, morphometry, texture and HSG | `_ranges.py`: ~90 `TypicalRange` records with sources and notices `outside_typical_range`/`outside_unverified_range`; type and range checks spread over modules | routing: published cases (NEH 630 ex. 17-1, 17-4, Iowa), oracles, invariants; elsewhere mostly hand calculations, some with loose tolerances (Kirpich 80–92 min) |
| Obserwator | Tier B: status codes and missing values of IMGW-PIB and ČHMÚ, hydrological year, half-years, extremum times, coverage; PMAXTP cells; delegates every analysis to Hydrolog | per parser | parsing fixtures |
| Hydrograf | DEM processing, slopes, TWI, shape indices, CN of soil–cover complexes, PMAXTP Thiessen mean, reach measures; tc, UH and hyetographs through Hydrolog | per module | integration-heavy; no reference cases |
| Kartograf | texture and HSG (its own copy of the rules), SoilGrids units, sheet and bbox math, areas; transforms delegated to pyproj | strict | exhaustive simplex tests of texture rules |
| Hydraulik | rain tables, Manning n and CN per cell, SCS input of SFINCS, exchange laws of the coupling, mass balance | per module | unit tests |

Suspected issues to settle in step 3 (none confirmed yet): the Euler II hyetograph uses a fixed rank-decay exponent instead of the IDF curve; Hydrograf's AMC conversion (Hawkins) differs from Hydrolog's (Chow); Hydrograf's „watershed length” differs between code and documentation; the unit of SFINCS's SCS retention input; several conventions of Obserwator's parsers (trace flag, hour 24, `99999.999` compared with a tolerance).

## Steps

1. **Nogat: the standard.** `standards/COMPUTATIONS.md` (CMP), its row and prefix in `standards/README.md`, `computes: true` in `ecosystem.yaml` and its schema, an ECO decision with the choices above, standard 1.1 on `develop` (HUB-6.1: version line, `standard_version` in `ecosystem.yaml` and `error_registry.json`, the headers of the topic documents).
2. **Nogat: the reference module.** `standards/reference/nogat_formulas.py` (CMP-8.1), `schemas/nogat/formula-1.schema.json`, their tests with the deliberately wrong toy formula (CMP-8.2), `drift` over the copies, Hypothesis and mutmut in the release set (CMP-8.3).
3. **Research** (running): eleven literature studies, one per family, with verdicts on code and descriptions, reference cases with citations and handbook material in Polish (`~/workspace/wt/ct-research/`).
4. **Triage.** Each finding classified by CMP-9.1 after a second source (CMP-5.2). A gross defect becomes a `fix/<topic>` branch and an urgent patch of its project and consumers (CMP-9.2), before anything else; ordinary defects go into step 5–7 branches.
5. **Hydrolog** (`test/computation-standard`, then topic branches per family): the reference module copied; specs for every Tier A formula in the order SCS-CN and CN tables, tc, unit hydrographs, flood frequency, SPI and meteo indices, routing, other statistics, morphometry and soil; `_ranges.py` folded into the specs; the notice `outside_typical_range` becomes `outside_applicability` (a breaking change of notice codes: consumers Hydrograf, Obserwator and the GUIs updated in the same release); reference cases, frozen oracles, generated tests; `docs/FORMULAS.md`; `formula_version` on every result.
6. **Obserwator**: Tier B specs of the parsers and calendars with reference cases on real files (DST, 29 February, hour 24); `formula_version` of Hydrolog's formulas in every stored analysis.
7. **Hydrograf, Kartograf, Hydraulik**: their own Tier A and B formulas specified and tested; delegated computations listed (CMP-1.2); Kartograf's and Hydrolog's texture/HSG rules proven equal by one shared set of cases.
8. **Hydrolog's handbook**: `docs/podrecznik/`, Polish, Markdown, CC BY 4.0: theory, variables, applicability, typical use, interpretation of results and worked examples on real Polish data, every equation, constant and range included from the generated specs (CMP-2.7).
9. **Sources for the author**: the list of textbooks and papers whose scans would confirm `author-provided` items or move formulas from `oracle only` to `referenced`.
10. **Mutation testing**: nightly CI per project once the generated tests exist; the release condition of CMP-9.3.

Releases: without a gross defect, each project's work merges into `develop` and goes out with its next patch or minor release (minor where notice codes or result fields change). Worktrees `~/workspace/wt/ct-*` are removed when their branches are merged.

## Results

(filled as steps finish)
