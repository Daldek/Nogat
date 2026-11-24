# Plan: interval estimation beside point estimation — Hydrolog computes the intervals, Obserwator shows them

Approved: pending

Status: proposed on 2026-11-24 from the author's feedback #13 to Obserwator; not approved, so no code starts (DEV-17.4). The facts below were checked that day on `develop` of Hydrolog (`34563ef`, 0.10.0.dev0), Obserwator (`b5a1c1a`, 3.3.0.dev0), Archiwista (`8805a78`) and Hydrograf, in the KZGW 2017 methodology and in the public Obserwator's logs. Design decisions marked [proposed] wait for the author; the open questions are at the end.

Requirements: HUB-5.2 (producers first), DEV-17.4, DEV-17.5, AGI-4.1, ECO-085 (additions within version 1), ECO-059 (computed by Hydrolog, shown by Obserwator), CMP-1.1, CMP-2.1, CMP-2.3, CMP-2.5, CMP-2.8, CMP §5, CMP-6.1, CMP-6.4, CMP-6.7, CMP-6.9, DEV-15.14 (Polish info texts: decimal comma, range with an en dash). Hydrolog ADR-0048 (the parametric bootstrap of A²), ADR-0049 (batch means); Obserwator ADR-016 (stored analyses), ADR-028 (the long CSV of analyses).

## The request (2026-11-24)

„Rozważyć wprowadzenie estymacji przedziałowej, obok punktowej. Zadanie dla Obserwatora (wizualizacja) i Hydrologa (obliczenia).”

## What exists (checked on 2026-11-24)

**Intervals Hydrolog already gives, and Obserwator shows:**

- The long-term mean of a calendar month: spec `mean_interval_half_width` (`statistics/characteristic.py:1562`), Student's t on the k yearly means of the month (batch means, ADR-0049; `characteristic.py:1776-1780`), fields `ci_lower`, `ci_upper`, `confidence_level` of `stats monthly`; Obserwator stores `monthly.Q` with `confidence_level` 0.95 (`store/analysis_registry.py:837-852`), draws it as a `band` („przedział ufności {level} %”, `gui/web/src/sections/hydro/regime.js:79`, `messages/gui/hydro_regime.py:305-307`) and gives the column „PU {level} %” as „dolna–górna” (`regime.js:228-233`).
- Sen's slope: spec `sen_interval` (`statistics/stationarity.py:1183`), Gilbert's interval, `alpha` 0.05 (Obserwator `analysis_registry.py:609`), limits `null` when their ranks fall outside the slopes (`stationarity.py:1457-1458`); Obserwator gives it in the trends table as „slope (dolna … górna)” (`sections/hydro/trends.js:98-106`), not on the chart.

**Point estimates without an interval:**

- Flood quantiles Q_p, `stats flood-frequency` (`statistics/high_flows.py`, `frequency.py`): four distributions (log-normal, GEV, Pearson III, Weibull) by four methods (`l_moments` by default, `mle`, `moments`, `least_squares`; `high_flows.py:71-86`); `FrequencyAnalysisResult` carries `quantiles` and no bounds (`high_flows.py:99-153`). Hydrolog's handbook says so: „Hydrolog tej poprawki ani przedziału ufności nie liczy” (`docs/podrecznik/07-przeplywy-maksymalne.md:1081-1085`), after the regulation (Dz.U. 2026 poz. 692, annex 3, note 3: (1 + δ)Q_k with δ at confidence 0.84 for mountain rivers) and KZGW 2017, which gives the upper limit of a one-sided interval.
- Precipitation quantiles P_max,p: the same command, run by Obserwator as `precipitation_quantiles[.2d|.3d|.5d|.10d]` (`analysis_registry.py:1030-1063`) and shown in „Opady” beside PMAXTP (`sections/meteo/opady.js:1-18`), whose upper bounds of the confidence interval of the quantiles Obserwator already shows („Górna granica”, `messages/gui/pmaxtp.py:92-95`).
- Low-flow quantiles NQ_T, `stats low-flow`: the GEV of the negated annual minima by maximum likelihood (`statistics/low_flows.py:739-760`, `:1008`); a quantile below 0 is `null` with the notice `negative_quantiles`.
- The flow-duration curve, `stats duration-curve`: the period-of-record curve, eq. (3) of Vogel and Fennessey (1994) (`statistics/duration.py:7-9`); its spec says „its confidence intervals (Vogel and Fennessey, sect. 5) are not computed” (`duration.py:457-458`).
- The characteristic flows SSQ, SWQ, SNQ (`stats characteristic`): means of yearly values by IMGW-PIB's calendar definitions, Tier B (CMP-1.1).

**What the cost has to fit into:**

- On request (a person's options), Obserwator runs at most two Hydrolog computations at a time, 30 s each, held in memory only (`gui/_analyses.py:1-15`, `TIMEOUT_S` `:52`). Requests wait in that queue: the public instance answered `GET /api/analysis/351220495/mann_kendall.temperature.frost_days?first_year=2010&last_year=2026` in 184.8 s on 2026-11-23 08:42 UTC, with six other on-request trends of the same station queued at 140–178 s (`~/.local/state/nogat/obserwator/logs/access-2026-11-23.jsonl`). `flood_frequency.Q` itself answered in 0.07 s median, 3.4 s at most (61 requests, 2026-11-20 to 24).
- Stored: `analyses build` computed 5,561 stations (3,240 IMGW-PIB, 2,321 ČHMÚ), about 150,000 results, in 28,334 s with 3 workers on 2026-11-23 (`~/data/obserwator-310/build.log`, `out-analyses.json`); a new Hydrolog version computes every station again (`store/analyses.py:16-22`).
- A parametric bootstrap already runs in every L-moments fit: `ad_critical_values` from 999 samples drawn from the fitted distribution, each refitted by L-moments, seed 20261118 (`high_flows.py:64-69`, `:156-192`). Its ADR-0048 measured the refits: about 0.2 s for the four distributions by L-moments; about 0.15 s for one maximum-likelihood GEV, so 999 of them take minutes, and the moments solve the GEV shape numerically too.

**Display and consumers:**

- Obserwator's chart engine has `band` series, `[x, lo, hi]` filled between (`gui/web/src/charts/chart.js:24-26`), used by the regime and the low-flow deficit; flood and low-flow curves are drawn on its `gumbel` x axis (`sections/hydro/extremes.js:150-161`, `:232-251`); the quantile tables (`extremes.js:83-90`) and the figures „Q1% (T = 100)” and „NQ 10-letni” (`extremes.js:191`, `:293`).
- Exports: `obserwator-analyses-export/1` carries Hydrolog's `result` whole, and the CSV has one row per scalar leaf of it with a JSON Pointer `path` (`store/analyses.py:2284-2301`, ADR-028), so new fields of the result reach both without code.
- `obserwator-analyses/1` holds the registry's digest, not results (`definitions`); `obserwator-station-analyses/1` holds per result its `options` and `formula_versions`; the result is Hydrolog's answer line byte for byte (`store/analyses.py:1-29`).
- Hydrolog's own GUI shows the quantiles as tiles and exports them as CSV (`gui/web/src/sections/statystyka/results-panel.js:6-8`, `:245-247`); its chart module has no fill-between series (`charts/chart.js:17-18` knows only a `band` y scale).
- Archiwista indexes stored analyses only as versions of the slot `analyses:<key>` and never reads a result (`adapter/obserwator/adapter.py:151-156`, `:391-432`). Hydrograf calls none of these commands.

## Inventory and ranking

| Rank | Estimate | Analysis (stored by Obserwator) | Shown in Obserwator | Interval today | Why this rank |
|---|---|---|---|---|---|
| 1 | Flood quantile Q_p | `flood_frequency.Q` | „Ekstrema”: table of Q_p, curves on the Gumbel grid, „Q1% (T = 100)” | none | design values; T of 100–1000 years from 30–60 maxima is an extrapolation (handbook 7.8); the regulation and KZGW ask for the upper limit |
| 2 | Precipitation quantile P_max,p of 1–10 days | `precipitation_quantiles[.Nd]` | „Opady”, beside PMAXTP and its upper bounds | none | the same code as rank 1; beside PMAXTP the reader compares a point with an interval |
| 3 | Low-flow quantile NQ_T | `low_flow.Q` | „Ekstrema”: curve, table, „NQ 10-letni” | none | a design value for water permits; one ML fit, cheap by the delta method |
| 4 | Flow-duration curve Q_p% | `duration_curve.Q`, `.H` | „Krzywa czasu trwania” | none (by spec) | descriptive of the period in Hydrolog's spec; an interval needs the annual interpretation of Vogel and Fennessey, another estimand |
| 5 | Means of yearly values SSQ, SWQ, SNQ | `characteristic.Q` | „Charakterystyki” | none | the spec of the monthly interval applies as is, but IMGW-PIB publishes them as characteristic values of the record (question 4) |
| — | Monthly long-term mean | `monthly.Q` | „Reżim”: band and column | yes | done; only the wording is unified (below) |
| — | Sen's slope | `mann_kendall.*` | trends table | yes | done; the table's „(dolna … górna)” becomes the common form |

Not given intervals, by design: observed extremes (WWQ, NNQ, maxima of a year), counts of days, the baseflow index and the CAMELS signatures (descriptions of the record, compared as points in Hydrolog's reference cases), test statistics (Mann–Kendall, Pettitt, homogeneity: their p-value is their statement of uncertainty), Pardé's coefficients, seasonality, harmonics, SPI and runoff volumes. The rating curve is a fit whose interval matters in hydrometry; it is outside this plan (question 6).

## Methods [proposed]

One parameter for every interval: `confidence_level` c, the two-sided central interval, as `stats monthly` has it; default 0.95 (as `stats monthly` and Sen's `alpha` 0.05) [proposed, question 1]. KZGW's one-sided β upper limit is the upper limit of the central interval at c = 2β − 1: β = 84 % is c = 0.68, u_0.84 = 0.994 (KZGW 2017, eq. 3.12 and 3.26), so `confidence_level=0.68` gives KZGW's limit exactly by the delta method and as the 84th percentile by the bootstrap.

| Estimate, fit | Method | Source | Cost | Reference cases and oracles (CMP §5, §6) |
|---|---|---|---|---|
| Q_p and P_max,p, `l_moments` (default, stored) | parametric bootstrap, percentile interval: the quantiles at every T of the 999 refits that already give `ad_critical_values` (same samples, same seed); samples the L-moments cannot fit are left out and counted | Efron and Tibshirani (1993), ch. 13 (percentile interval); Hosking and Wallis (1997), the accuracy of quantile estimates by simulation; Kyselý (2008), J. Appl. Meteor. Climatol. 47, 3236–3251 (parametric before nonparametric bootstrap for short extreme-value samples) | none beyond today's: the refits run already; one `isf` over 999 × 25 periods per distribution | frozen oracle: R `lmomco` `genci.simple` (CMP-6.4) within a Monte Carlo tolerance (different generators); coverage (the new rule of CMP §6 below) |
| Q_p and P_max,p, `mle` (on request) | delta method with the observed information: Var(Q_T) = ∇Q_Tᵀ I⁻¹ ∇Q_T, I by finite differences of the log-likelihood at the estimate; Q_T ± z σ | Coles (2001), sect. 2.6.4 and 3.3.3; Stedinger, Vogel and Foufoula-Georgiou (1993), ch. 18 | milliseconds: about 20 log-likelihood evaluations per fit | KZGW 2017 (`zal-2-do-OPZ-ujednolicony-1.pdf`): ex. 3.2 Czarna–Polana, Pearson III by ML, σ(Q_max,p) and Q^84% in table 3.9 (the 34 maxima of table 3.5, already Hydrolog's handbook example 7.9); log-normal eq. 3.41 (Stedinger et al. 1993) with ex. 3.3, table 3.12; Weibull eq. 3.57 (Heo et al. 2001) with ex. 3.4, table 3.15; P_max log-normal eq. 2.9, table 2.3; frozen oracle R `extRemes` `ci.fevd(method = "normal")` for the GEV |
| Q_p, `moments`, `least_squares` | none: fields `null`, notice `interval_not_computed` (`details.reason` `fit_method`) [proposed, question 2] | — | a bootstrap would take minutes (ADR-0048), above the 30 s of a request | — |
| NQ_T (GEV of negated minima, ML) | the delta method above on the negated sample, bounds negated and swapped; a bound below 0 is `null` with `negative_quantiles`, as the quantile | Coles (2001), sect. 3.3.3; WMO-No. 1029 (2009), sect. 7.5 | milliseconds | frozen oracle `extRemes` on the negated minima |
| Flow-duration curve | Vogel and Fennessey (1994), sect. 5: one curve per complete hydrological year; per exceedance percentage the median of the N annual values (the median annual curve) and its nonparametric interval from their order statistics (binomial), the years taken as independent; the period-of-record curve stays unchanged beside it [proposed, question 3] | Vogel and Fennessey (1994), J. Water Resour. Plann. Manage. 120(4), 485–504, sect. 5 (the authors' copy Hydrolog cites, `duration.py:122-127`; the locator is checked against it in H1) | milliseconds: N sorts of one year of days | the paper's example if it prints one; oracle: the binomial bounds in exact arithmetic (CMP-6.2) |
| SSQ, SWQ, SNQ | Student's t of spec `mean_interval_half_width` on the yearly means, maxima or minima [proposed, question 4] | as the monthly interval (ADR-0049) | none | the spec's own cases |

Rejected: a bootstrap for every fit method (minutes per request, ADR-0048); the profile likelihood (Coles 2001, sect. 3.3.3), better than the delta method at large T but one constrained search per period, 25 per fit; a nonparametric bootstrap of the annual maxima (too narrow for 30–60 values, Kyselý 2008); reading KZGW's tables A.3 and A.4 into code: Hydrolog computes the information itself, and the printed σ of the examples serve as reference values only, so no published table enters the code (CMP-2.5 does not apply). KZGW's Pearson III and Weibull take the lower bound ∈ as known, Hydrolog estimates it: each case states the convention (CMP-2.3), and a difference two sources share is a `discrepancy` (CMP-5.2).

## Specs and the standard (CMP)

- **Nogat, standard 1.2 [proposed]:** CMP-2.3 adds to the conventions a spec lists „the side and confidence level of an interval, its method (delta, bootstrap and its kind, profile likelihood), the bootstrap's sample count and seed”. A new rule of CMP §6, after CMP-6.10, *Interval estimators*: besides their reference cases, their coverage is tested by seeded simulation from known distributions at the typical sample sizes (30 and 60 values for annual series), the share of intervals that hold the true value within the Monte Carlo error 2√(c(1 − c)/m) of c, in the `nightly` profile (CMP-6.9); the properties lower ≤ upper, a width that grows with c and shrinks with n are generated tests. The reference module gains the assertion of a coverage with its `reason` (CMP-6.8), tested in Nogat (CMP-8.2). One ECO decision (the next free number at merge, ECO-085's rule) records the convention: intervals are computed by Hydrolog and shown by Obserwator, one `confidence_level` two-sided, the field names below.
- **Hydrolog:** new Tier A specs, `formula_version` 1 each: `quantile_interval_bootstrap` (L-moments), `quantile_interval_delta` (ML, per distribution), `duration_curve_annual_median_interval`; `low_flow` uses the delta spec on negated minima. The point specs keep their versions, since no point result changes (CMP-2.8); a result's `formula_versions` names the interval specs it used. `docs/FORMULAS.md` and `formulas/<id>.toml` regenerated (CMP-2.6).

## The result shape [proposed]

Additions within `hydrolog-result/1` and its domain documents `hydrolog-stats-flood-frequency/1`, `hydrolog-stats-low-flow/1` and `hydrolog-stats-duration-curve/1`: optional fields only, so every version stays `/1` (AGI-4.1, ECO-085). Names as `stats monthly`'s:

```json
"confidence_level": 0.95,
"ci_method": "parametric_bootstrap",
"ci_lower": [12.1, 14.0, ...],
"ci_upper": [15.8, 19.6, ...],
"ci_samples": 997
```

- Per fit of `stats flood-frequency`; once in `stats low-flow`; in `stats duration-curve` beside `curve_values`, with the median annual curve as `annual_median_values`. `ci_lower` and `ci_upper` align with `quantiles` (or the curve's percentages); an element is `null` where undefined. `ci_method` is `parametric_bootstrap`, `delta` or `order_statistics`; `ci_samples` the bootstrap samples kept of 999, `null` otherwise.
- Not computed: the four fields `null` and the notice `interval_not_computed` (`details.reason`: `fit_method`, `too_few_values`, `no_bootstrap_samples`, `too_few_complete_years`).
- The option `confidence_level`, number in (0, 1), on the three commands, default 0.95, as `stats monthly`'s.
- `obserwator-analyses/1` changes only through the registry's digest; `obserwator-station-analyses/1` gains `confidence_level` in the `options` of these results and the interval specs in their `formula_versions`: new keys of open maps, additive. `obserwator-analyses-export/1` and its CSV carry the fields as rows beside `quantiles` without change.
- The consumers that read the fields are Obserwator and Hydrolog's GUI, both changed in this plan; Archiwista and Hydrograf do not read these results (above), so ECO-085's condition holds.

## Display in Obserwator [proposed]

- **Charts:** a `band` series under each curve with an interval: the flood and precipitation curves on the Gumbel grid (one band, of the stressed fit when several are drawn, so bands do not overlap), the low-flow curve, the median annual FDC beside the period-of-record curve. Legend and readout „przedział ufności 95 %” (the regime's key `hydro.regime.ci`); the readout of a band says „dolna–górna”, not „min–maks” (`charts/draw.js:95-100`).
- **Tables:** in the cell „Q_p [dolna–górna]”: „412 [356–498]”; the head „Q_p [m³/s], przedział ufności 95 %”; the same for P_max,p and NQ_T. A bound below zero is written with the minus sign and a spaced en dash („0,60 [−0,30 – 1,35]”); Sen's column takes this form instead of „(… … …)”, the regime's column keeps „dolna–górna”. „–” where a bound is `null`.
- **Figures:** „Q1% (T = 100)” and „NQ 10-letni” get the interval as their note.
- **Texts (Polish, DEV-15.14):** an info text per view, e.g. „Przedział ufności 95 % kwantyla: zakres, który przy wielokrotnym powtórzeniu obserwacji tej samej długości obejmowałby prawdziwy kwantyl w 95 % przypadków. Wyznaczony bootstrapem parametrycznym z 999 prób (L-momenty) albo metodą delta (największa wiarygodność). Dla T dłuższego niż ciąg obserwacji kwantyl jest ekstrapolacją, a przedział szybko się rozszerza.”; the notice for a method without an interval: „Dla metody momentów i najmniejszych kwadratów przedział ufności nie jest wyznaczany.”; the CMP-2.7 rule holds: equations and constants only from the specs.
- **Options:** `confidence_level` overridable in the registry, chosen in the view as „Poziom ufności: 68 % / 90 % / 95 %” (68 % named „górna granica wg KZGW (84 %)”); a choice other than the stored one is computed on request, at today's cost.
- **Exports:** nothing to build; the manual (USAGE) names the new paths of the CSV.

## Steps

| # | Project, release | Change |
|---|---|---|
| N1 | Nogat, standard 1.2 [proposed] | CMP-2.3 and the new rule of CMP §6 on interval estimators; the coverage assertion in `standards/reference/nogat_formulas.py` with its tests; the ECO decision; CHANGELOG and PROGRESS |
| H1 | Hydrolog, its next minor (`0.10.0` [proposed], with the CAMELS-PL cases already on `develop`) | the three specs and their reference cases and oracles (KZGW 2017 examples 3.2–3.4 and table 2.3, `lmomco`, `extRemes`, Vogel and Fennessey), coverage tests; `confidence_level`, the fields and `interval_not_computed` in the three commands and their catalog entries; the handbook's sentence (`07-przeplywy-maksymalne.md:1084`) and `duration.py:457-458` rewritten; Hydrolog's GUI: a fill-between series in its chart module, the band on its probability plot, „[dolna–górna]” in its quantile tiles and CSV; one ADR (0074); USAGE, CHANGELOG |
| O1 | Obserwator, the first minor after `v3.4.0` (CAMELS-PL), `v3.5.0` [proposed] | the registry's `confidence_level` (stored 0.95 or the author's choice) for `flood_frequency.Q`, `low_flow.Q`, `duration_curve.*`, `precipitation_quantiles*`; Hydrolog of H1 as its program; the display above in „Ekstrema”, „Krzywa czasu trwania”, „Opady”, „Charakterystyki” if question 4 says so, the trends column; Polish messages and info texts; manual; ADR |
| — | Archiwista | none: it indexes versions of `analyses:<key>`, whose grammar does not change, and reads no result; its next round only re-runs its adapter tests on a data root built in O1 |
| D1 | deployment, with the author's approval | Hydrolog of H1 in the public instance's program venv, then `analyses build` (about 8 h with 3 workers, as on 2026-11-23) as a long job (ECO-073), then Obserwator O1 |

N1, then H1 (its specs follow the new CMP rule), then O1, released in one round (ECO-085); D1 after the round.

## Open questions for the author

1. Poziom ufności domyślny: 95 % dwustronnie (jak dziś średnie miesięczne i nachylenie Sena), czy górna granica wg KZGW 2017 przy β = 84 % (dwustronnie 68 %), której używa rozporządzenie ((1 + δ)Q_k) i z którą można porównać górne granice PMAXTP? Czy Obserwator ma przechowywać oba?
2. Metody momentów i najmniejszych kwadratów: bez przedziału (pole puste z komunikatem), czy bootstrap tylko na żądanie, kosztem minut na jedno obliczenie, ponad dzisiejsze 30 s Obserwatora?
3. Krzywa czasu trwania: dodać obok krzywej z całego okresu medianową krzywą roczną Vogela i Fennessey z jej przedziałem (inna wielkość, wymaga pełnych lat), czy zostawić krzywą bez przedziału?
4. SSQ, SWQ, SNQ: przedział t-Studenta średniej z wartości rocznych (tani, gotowa specyfikacja), czy zostają charakterystykami okresu wg IMGW-PIB, bez przedziału?
5. Wydania: przedziały w Hydrologu `0.10.0` razem z przypadkami CAMELS-PL, a w Obserwatorze w `v3.5.0` po `v3.4.0` z CAMELS-PL, czy wcześniej?
6. Krzywa natężenia przepływu (dopasowanie, przedział wg ISO 18320): osobny plan później, czy poza zakresem?

## Results

None yet.
