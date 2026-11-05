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
| D1 | Hydrolog's `WatershedParameters` gains optional `flow_path_length_km` (longest flow path, divide to outlet) and `flow_path_slope_m_per_m` ((elevation of its head on the divide − outlet) / its length); the network schema follows. |
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

Pending.
