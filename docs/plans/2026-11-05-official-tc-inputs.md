# Plan: time of concentration from the inputs its official sources define

Approved: 2026-11-05, the author („Chciałbym, żeby wszystkie obliczenia były oparte na tym, co jest oficjalne w danej metodzie”; scope: everything in Hydrograf v0.5.0); the decisions below by delegated authority.

Requirements: HUB-5.2 (producers before consumers), DEV-17.4, ECO-056.

## Goal

Hydrolog and Hydrograf compute every time of concentration method (Kirpich, NRCS lag, Giandotti, FAA, Kerby, Kerby–Kirpich) from the inputs its primary source defines, without substitutes, and a hand-off from Hydrograf lets Hydrolog compute the same method with the same tc.

## Facts

Research with quotes: `/tmp/tc-official-inputs.md` (sources in `/tmp/tc-src/`), summarised:

| Method | Length | Slope / other | Source |
|---|---|---|---|
| NRCS lag | longest flow path, divide to outlet | average watershed land slope Y (not the flow-path slope); CN | NEH 630 ch. 15 (2010), p. 15-5, eq. 15-4 |
| Kirpich | along the watercourse to the most remote point on the divide | (elevation of that point − outlet) / that length | Fang et al. 2005 (TxDOT 0-4696-1) eq. 3.14; Mota & Kobiyama 2015 |
| Giandotti | main channel | mean basin elevation − outlet elevation; area | Grimaldi et al. 2012 |
| FAA | overland distance to the inlet | overland surface slope (%); C from FAA Table I | FAA AC 150/5320-5B (1970), fig. 7 |
| Kerby | overland length up to a defined channel (≤ ~366 m) | overland slope; N from Kerby's table | Kerby 1959 via Roussel et al. 2005 supplement |
| Kerby–Kirpich | overland as Kerby; channel = flow path − overland | (divide − outlet) / whole flow path | Roussel et al. 2005 (TxDOT 0-4696-2) supplement; TxDOT HDM 11 |

Today Hydrolog takes Kirpich's and NRCS's length from the main channel with substitutes, and Hydrograf overrides fields before calling Hydrolog (NRCS correct, Kirpich with the channel slope, FAA/Kerby with the mean slope, C from CN, defaults 1.0 km and 0.01).

## Decisions

| # | Decision |
|---|---|
| D1 | Hydrolog's `WatershedParameters` gains optional `flow_path_length_km` (longest flow path, from the hydraulically most distant point of the watershed to the outlet) and `flow_path_slope_m_per_m` ((elevation of that point − outlet) / its length); the network schema follows. That point lies on a ridge, usually the divide, but it can be a ridge inside the watershed: NEH 630 ch. 15 p. 15-5 takes the longest flow path "to represent the hydraulically most distant point in the watershed", and Fang et al. 2005 eq. 3.14 measures from "the most remote point in the watershed" (erratum 2026-11-05; the computation was already so). |
| D2 | `TC_INPUTS` without substitutes: Kirpich = flow path length and slope; NRCS = flow path length, mean slope, CN; Giandotti = channel length, area, mean and min elevation; FAA and Kerby = overland length and slope plus C / N; Kerby–Kirpich = overland fields plus the flow path (channel = flow path − overland). A missing input is `validation_error` `missing_field` naming it. |
| D3 | `tc kerby-kirpich` changes to the flow-path fields (clean cut-over); its channel ranges are renamed to the flow-path fields. |
| D4 | FAA C and Kerby N are inputs; nothing derives them (no sourced class table). |
| D5 | Hydrograf measures the flow path's head elevation and the overland segment (to the DEM stream network at the delineation threshold) in preprocessing (migration plus backfill on production), carries them in the morphometry, computes every method through `WatershedParameters.calculate_tc` with no overrides, and hands the fields off with `runoff.tc_method` (no `tc_min`; `provenance.runoff.tc_min` keeps its value for the comparison). A user's overland length needs its slope too. |
| D6 | Citations fixed (NRCS: NEH 630 ch. 15, not TR-55; FAA: AC 5B; Kerby–Kirpich: TxDOT 0-6382-P1 for the low-slope offset). Hydrograf pins the new Hydrolog; the release set moves Hydrolog for every consumer. |

## Steps

| # | Project | Change | Verified by |
|---|---|---|---|
| 1 | Hydrolog | D1–D4, D6 in the library, catalog, reports and GUI (fields, labels, info texts, Kalkulatory) | gate; e2e |
| 2 | Hydrograf | D5: migration, preprocessing and backfill, morphometry, `_calculate_tc`, hand-off, frontend; pin step 1 | gate; production backfill; recompute test of every method from a hand-off |
| 3 | Nogat | `set bump Hydrolog`; consumers (Retman, Hydraulik, Hydrograf) `set apply` | `set check`, consumer gates |
| 4 | Production | Hydrograf and Hydrolog GUI deployed; the author confirms; Hydrograf v0.5.0 | smoke; hand-off comparison „zgodny” for each method |

## Results

Done on 2026-11-05.

1. **Hydrolog** `29138cc` (merge of `feature/official-tc-inputs`, ADR-0019): `WatershedParameters.flow_path_length_km` and `flow_path_slope_m_per_m`; strict inputs per method, no substitutes; Kerby–Kirpich takes the flow path; citations fixed (NEH 630 ch. 15, AC 150/5320-5B, TxDOT 0-6382-P1, Fang et al. 2005). Gate 6856 passed. `1ffcd6b` adds the re-copied example of `nogat-handoff/1` (Nogat `8727f6e`, which gave it Kamiennik's flow path and Hydrolog's result, 57.8786 m³/s at 400 min).
2. **Hydrograf** `a8a89e9` on `develop`: preprocessing measures the flow path head, the overland segment and the channel source (ADR-070, migration 004); tc only through `WatershedParameters.calculate_tc`, C and N given by the user, no defaults; the hand-off carries the flow-path and overland fields and `runoff.tc_method`. With it: the tester reports #13, #14 (without the dry-valley length), #16, #20, #23–#27, #35, #37, #39, #40 (the PMAXTP depth is the watershed mean by Thiessen polygons, ADR-069, with an optional areal reduction factor of the user). Gate 1512 passed.
3. **Set** `candidate-1`: Hydrolog `1ffcd6b` (Nogat `0a2b054`); applied in Hydrograf, Retman `d03cf24` (its mapping of `missing_field` to „ask for the method again” follows Hydrolog's `details.method` and `details.missing`) and Hydraulik `feature/sfincs-swmm` `1225172`; `set check` ok.
4. **Production** 2026-11-05 12:38–12:53 UTC by Hydrograf's runbook `docs/runbooks/2026-11-v050-reprocessing.md` (backup `/data/nmt/hydrograf-backup-2026-11-05-v050`, image `hydrograf-api:pre-v050`): backfill of 41 277 + 4 492 sub-catchments from the rasters before the cut, thresholds 1 and 10 km² (479 and 49 segments), their tiles; API down about 10 s. Hydrolog's GUI on :8070 serves `1ffcd6b`. Smoke on Kamiennik (134.93 km², flow path 22.2789 km at 0.016038): for each of the six methods Hydrolog's `route network` on Hydrograf's hand-off gives Hydrograf's result exactly (Kirpich tc 213.25 min, NRCS 360.69, Giandotti 466.20, FAA 16.46 with C 0.3, Kerby 19.17 with N 0.4, Kerby–Kirpich 230.52); FAA without C is 400 `validation_error` naming `tc_runoff_coeff`.
5. **The author's review, same day** (Hydrograf `develop` `569c3fe`, Hydrolog `c16976e`, both in production; no tag yet, by the author):
   - Wording: the longest flow path starts at the hydraulically most distant point, usually on the divide but possibly on a ridge inside the watershed (D1 erratum; Hydrolog and Hydrograf texts). The computation already did so.
   - The longest flow path from the watershed boundary was sampled at boundary polygon vertices, which fall into neighbouring watersheds (37.23 km²: 17.59 km against a longest path of 16.05 km). It now comes from the watershed's own boundary cells (`core/divide_flow_path.py`), never exceeds the longest path, and is shown only when it is a different path, the map line only for its own stretch.
   - Both lines are drawn in full along D8 cell centres without simplification (the longest one was only its head sub-catchment's 2.2 km), and a legend „Zlewnia” names every line.
   - Overland + main channel ≠ longest flow path is by definition: the main channel follows the tributary with the larger area, the longest path a longer one (34 of 38 segments shared at 37.23 km²); along one route the 31 m left is stream above the point where the path joins it laterally. The (i) texts say so; a test checks overland + route segments = flow path.
