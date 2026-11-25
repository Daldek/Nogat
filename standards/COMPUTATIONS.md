# Computations: formulas, their limits and their verification

Part of standard 1.3 · IDs `CMP-…`

The tools compute hydrological, meteorological and geographical quantities
that engineers and researchers rely on, and academics audit the formulas. A
wrong constant, exponent, unit, table entry or calendar convention, or a
formula used silently outside the conditions it was derived for, can
invalidate every result that depends on it. This document says how a formula
is declared, how it behaves at and beyond the limits of its inputs, how it is
verified, and what happens when it is found wrong, so that its correctness can
be shown to an auditor from the repository alone.

It governs *verification*: that the code computes the published formula within
a stated tolerance. *Validation*, the formula's agreement with nature, belongs
to its sources; a spec reports what the source reports and claims nothing
more.

Requirements follow the reading rules of [README.md](README.md). They apply to
every project whose registry entry has `computes: true`.

---

## 1. Terms

**CMP-1.1** A *formula* is a function that turns numbers into numbers with a
physical or statistical meaning. *Tier A*: empirical equations, models and
numerical schemes, statistical estimators, tests and distribution fits,
indices, classifications by published thresholds or tables. *Tier B*: unit
conversions, aggregations and characteristic values by a calendar definition,
interpolations, and the conventions of codes, flags, gaps, days and years in
source data. Every function that returns a quantity is in one tier; a private
helper is covered by the formula that calls it.
*Why:* auditors' time goes to the formulas where a wrong exponent costs most;
conventions are tier B but never exempt.

**CMP-1.2** A computation delegated to a third-party library (pyproj, GDAL,
Shapely, SciPy's optimisers) is not a formula of this standard. It is listed
in `docs/FORMULAS.md` with the library, its version range and one smoke
reference case (for example the area of a known polygon in EPSG:2180).

**CMP-1.3** Every input has a *physical range*: the values that can exist. An
unbounded end carries a *test bound* with its reason (the land area of the
Earth, the world record of daily precipitation, ten times the largest value in
the project's data), used wherever a test needs a finite end.

**CMP-1.4** Where a source states one, an input has an *applicability range*:
the values for which the formula was derived or validated, with the source
that states it. Where none is stated, the spec says `unstated`.

**CMP-1.5** Every input has a *typical range*: the values met in the
ecosystem's use, from the project's data or a named Polish or Czech source. It
lies within the physical range and MAY lie partly or wholly outside the
applicability range; the spec then says so.
*Why:* Kirpich was fitted on plots under 0.5 km²; Polish practice applies it
to larger catchments, and the result must say so.

**CMP-1.6** A *precondition* is a condition without which the formula is
undefined or its estimate degenerate: a minimum sample size, a positive
argument of a logarithm, a non-constant series for a trend test, a time step
within a scheme's stability bound. A *constraint* is a relation between inputs
(Muskingum's `2KX ≤ Δt ≤ 2K(1−X)`), of class `physical`, `precondition` or
`applicability`, with a boolean expression and a source.

**CMP-1.7** A *reference case* is a set of inputs with the output a source
publishes for them. An *oracle* is an independent way to get the output: an
exact solution, a different algorithm, or an established implementation. A
*frozen oracle* is an oracle's output stored as data (CMP-6.4).

---

## 2. Specs: one declaration per formula

**CMP-2.1** Every Tier A formula is declared once, in code, by a `FormulaSpec`
of the reference module (CMP §8) next to its function: import path, equation
(plain text and LaTeX), each variable with symbol, unit, type, physical range
or test bound, applicability range with source, and typical range with source;
preconditions and constraints; named constants with values; outputs with unit,
physical range and boundary tolerance; sources; conventions (CMP-2.3);
assumptions; notices it emits; numerical risks (CMP-6.6); properties that hold
(CMP-6.5); reference-case files; `validation` (what the source reports of the
formula's agreement with observations, or `none`); `formula_version`. The spec
drives the run-time checks of CMP §3 and §4 and the generated tests of
CMP §6.
*Why:* a range written twice is a range that will differ.

**CMP-2.2** A Tier B formula is declared in one table per module (a
`TierBSpec` list): definition, source, exact or rational constants, and the
convention it implements.

**CMP-2.3** A spec lists the conventions its source and its code follow
wherever a choice exists: system of units, exceedance or non-exceedance
probability, the sign of the GEV shape, plotting position, the estimator of
moments or L-moments, `λ` of SCS-CN, the hydrological year and half-years, the
measurement day and time zone, the treatment of gaps, ties and zero values,
and the side and confidence level of an interval and its method: the delta
method with its information (observed or expected), its scale and the
parameters it holds at their estimates; a bootstrap with its kind, sample
count, seed and empirical-quantile rule; order statistics.

**CMP-2.4** A source confirms a constant, exponent or table entry only as the
primary source or as two independent secondary sources, cited with equation,
table or page. A source the auditor cannot open (`author-provided`) MAY supply
reference cases and ranges; a constant of a Tier A formula needs an open
confirmation too, except a formula published only in Polish or Czech
literature, whose spec says so.

**CMP-2.5** A published table (CN tables, ordinates of a dimensionless unit
hydrograph, critical values of a test, texture class limits) is a data file
with its source, edition and page, and the spec records its SHA-256. It is
transcribed twice independently and the transcriptions are compared before
the file is accepted; the comparison is kept in `tests/oracles/`. A table is
never written into code.

**CMP-2.6** `docs/FORMULAS.md` and `formulas/<id>.toml` are generated from the
specs and checked fresh (DEV-10.4). They show per formula the equation,
sources, ranges, conventions, reference cases, the tests of each class of
CMP §6, the mutation score (CMP §7) and a status: `referenced` (a reference
case passes), `oracle only` (no reference case; an oracle passes) or
`unreferenced`. Nogat gathers the projects' catalogues into one.

**CMP-2.7** A formula's docstring gives its one-line purpose and its spec's
name and says no constant, unit, range or equation; user documentation and
reports reproduce equations, constants and ranges only by including fragments
generated from the specs. A contract test fails on a digit in a Tier A
docstring outside the spec's name.
*Why:* a description cannot contradict the code if it never restates it.

**CMP-2.8** `formula_version` is an integer incremented with every change of
a formula's results. Every result a project stores or exports carries the
project's version and the `formula_version` of each Tier A formula it depends
on.
*Why:* after a defect, the affected stored results must be found by query.

---

## 3. Behaviour at and beyond the limits

**CMP-3.1** An input outside its physical range, a violated physical
constraint, or a value that is not a finite number where one is required, is
refused with `validation_error`, `details.reason = "outside_physical_range"`,
naming the variable, its value and its range, before any computation.

**CMP-3.2** A failed precondition is refused with `validation_error`,
`details.reason = "precondition_failed"`, naming the condition, before any
computation.

**CMP-3.3** An input inside its physical range but outside its applicability
range, or a violated applicability constraint, gives the result with one
notice per violated variable or constraint, in the order of the spec, level
`warning`, code `outside_applicability`, naming the variable, its value, the
range and the range's source (AGI notices carry it to every interface).
*Why:* the author's decision of 2026-11-18: an engineer may compute outside a
formula's range knowingly, never unknowingly.

**CMP-3.4** A formula never returns a non-finite scalar, a non-finite element
where the spec forbids gaps or the corresponding input was finite, or a value
outside the output's physical range by more than its boundary tolerance
(stated; default four units in the last place of the bound). A value within the
tolerance is set to the bound. If the computation would produce such a value
for accepted inputs, it raises `calculation_error` naming the cause; each such
error found by a test or a user is a defect of the spec until a precondition
or constraint prevents it.

**CMP-3.5** All checks of CMP-3.1 to CMP-3.4 and CMP §4 are made by the
reference module's `validate(spec, **inputs)` and `check_outputs(spec, …)`; a
formula module contains no checks of its own.

**CMP-3.6** Computation is in `float64` throughout; sums of many terms use
`math.fsum` or NumPy's pairwise sum; `log1p` and `expm1` are used near zero;
moments are never computed as `E[x²] − E[x]²`. Results are reproducible across
platforms within the stated tolerances.

---

## 4. Types and units of inputs

**CMP-4.1** Formula signatures are fully annotated and pass mypy without `Any`
in public signatures. A real scalar is annotated `float`; an array names its
element type and dimension (`NDArray[np.float64]`).

**CMP-4.2** A real input accepts Python `int` and `float` and NumPy integer and
floating scalars, converted to `float64` on entry; it refuses `bool`,
`numpy.bool_`, `None`, strings, `Decimal` and complex numbers. An array input
refuses a wrong dimension, length or dtype, an empty array where the spec
needs values, and a non-finite element where the spec forbids gaps.

**CMP-4.3** Units are part of a variable's public name (`area_km2`,
`slope_m_per_m`, `duration_min`). Every conversion is an entry of the units
table of the reference module, an exact rational or published constant with
its source; no formula module contains a conversion literal.

---

## 5. Evidence for a formula

**CMP-5.1** Every Tier A formula has at least two of: a reference case
(CMP-6.1), an oracle (CMP-6.2 to CMP-6.4), and the properties of CMP-6.5. A
Tier A formula with status `unreferenced` emits the notice `unreferenced_formula`
at level `info` on every result.
*Why:* for many schemes the literature gives no worked example precise enough
to test; limits and conservation laws are then the stronger evidence.

**CMP-5.2** Before a difference from a reference case is classified as a
defect of the formula, the case is checked against a second source. A wrong
case is a defect of the tests; a difference two sources share is recorded on
the case as a `discrepancy` with its suspected cause, and the formula is
`oracle only` until resolved.

---

## 6. Tests

**CMP-6.1** *Reference cases.* Stored as data with the citation. The
tolerance is half a unit of the last printed digit of the output, plus the
effect of half a unit of each printed input (evaluated at the corners of the
input rounding intervals by the reference module), plus each intermediate
rounding of the source, which the case lists step by step. Where the source
allows, three or more cases span the typical range.

**CMP-6.2** *Oracles in tests.* Where an exact solution or an independent
algorithm exists, the formula is compared with it over the typical range. A
hand calculation counts only when written in a different form from the code
(for example evaluated with `mpmath` at 50 digits, or with `fractions` for
rational Tier B arithmetic).

**CMP-6.3** *Established implementations.* SciPy and other packages of
Nogat's release set run in the tests; each comparison names the conventions of
both sides (CMP-2.3), and the GEV sign convention of SciPy is asserted by one
dedicated test.

**CMP-6.4** *Frozen oracles.* R packages (`lmom`, `trend`, `Kendall`, `SPEI`,
`climdex.pcic`), published programs and spreadsheets are run once by a script
kept in `tests/oracles/`; their outputs are stored as CSV with the tool's and
packages' versions, the platform and the date, and are never regenerated into
the same file. Published data sets with published results come first; seeded
samples from known distributions complement them.

**CMP-6.5** *Ranges, types and properties, generated.* The reference module
generates from the spec, for every input, constraint and precondition: tests
at points of the typical range, at the extremes of the applicability range and
of the physical range or test bound, at each bound exactly and just beyond it
(`math.nextafter` and ±1 % of the bound's magnitude), each expecting the
outcome of CMP §3; and tests passing every kind of value of CMP-4.2. Property
tests (Hypothesis) draw from the typical, applicability and physical ranges in
turn and assert that every result is finite and inside its physical range or
that the declared error is raised, and the properties the spec lists:
monotonicity in each input the source states, conservation within a stated
tolerance, limits, symmetry, and for a formula marked `homogeneous` the
scaling of the output with the units of the inputs; a formula marked
`unit-specific` instead has a reference case in each unit system its sources
publish. A hand-written test of these classes is allowed only for what the
generator cannot express, and says why.

**CMP-6.6** *Numerical traps.* The reference module lists traps per formula
family: a denominator that is a difference of inputs, `log` or `sqrt` at a
bound, `exp` of a scaled input at its test bound, an iteration without a
bounded count, a stability bound of a scheme, a gap that propagates, a sum of
many small terms, cancellation in moments. A spec names the traps of its
family that apply, or says why none does; each named trap has a test that
expects a finite value within tolerance or the error of CMP §3.

**CMP-6.7** *Statistical procedures* are also tested on small samples, ties,
zeros and constant series, against the source's definitions; randomness in
tests is always seeded.

**CMP-6.8** Every tolerance passed to an assertion carries a `reason`; formula
tests use the reference module's assertions, and a bare `pytest.approx()` or
`assert_allclose()` without explicit tolerances fails a repository test.
Formula tests carry the marker `formula`.

**CMP-6.9** Hypothesis runs with three profiles of the reference module:
`gate` (deterministic, 50 examples), `ci` (1,000 examples, cached database)
and `nightly` (20,000 examples). Every counterexample found is pinned with
`@example` beside its property.

**CMP-6.10** *Published data sets.* A data set that publishes both the
inputs of a formula and its authors' outputs (CAMELS-PL's daily discharge
and its hydrological signatures) gives reference cases pinned to one
release: its record, version, DOI and the SHA-256 of each file read are
stored with the cases, each case names the authors' conventions (CMP-2.3),
and a newer release changes the cases only by a deliberate change of the
tests. Such outputs are computed, not measured, so a difference is checked
against a second source before it counts against the formula (CMP-5.2).
*Why:* a release may correct values of the one before it (ECO-086).

**CMP-6.11** *Interval estimators.* Besides its reference cases and oracles,
an interval's coverage, the share of intervals that hold the true value, is
simulated, seeded, from the distributions the formula fits, at the sample
sizes of the ecosystem's use (30 and 60 values for annual series) with at
least 1,000 samples per setting, nightly and before each release, never in
the gate (as CMP-7.1), and reported per setting in `docs/FORMULAS.md`. A test
asserts, per level and per element, an exact method's coverage c (order
statistics, Student's t on normal samples; for order statistics their
binomial coverage) within the Monte Carlo error 3√(c(1 − c)/m) of its m
samples, and an approximate method's as its source reports it for the
setting, or above a stated bound with its reason (CMP-6.8); its seed is fixed
once in the test and recorded, never chosen to pass. The generated properties
are lower ≤ upper and the interval of a smaller c inside that of a larger one
on the same sample. The reference module's `assert_coverage` and
`assert_interval_properties` make these checks.
*Why:* an interval can be right digit by digit and still not cover what it
says; an approximate method's coverage at 30 values is the method's, not the
code's, so it is reported, not forced to c. Two standard errors would fail a
right interval in about one assertion of 22, whatever m, and a formula asserts
one per return period and level (ECO-091).

---

## 7. Strength of the tests

**CMP-7.1** Mutation testing (`mutmut`) runs over the formula modules, with
the `formula` tests and the `gate` profile, nightly and before each release,
never in the gate. A mutant surviving in a Tier A function is killed by a new
test or the line carries `# pragma: no mutate` with the reason; a release is
not made while an unannotated mutant survives in Tier A. The score per module
is reported in `docs/FORMULAS.md`; Tier B is reported, not gated.
*Why:* passing tests with loose tolerances prove little; a surviving mutant
names the change the tests would not notice.

---

## 8. Shared tools

**CMP-8.1** Every project that computes copies
[standards/reference/nogat_formulas.py](reference/nogat_formulas.py) byte for
byte into its package and the schema of generated cards
[schemas/formula/card-1.schema.json](../schemas/formula/card-1.schema.json)
into `schemas/nogat/`; `drift` names every copy that is behind or edited. The
module provides `FormulaSpec`, `TierBSpec`, `validate`, `check_outputs`, the
units table, the generators of CMP-6.5, the Hypothesis profiles and
strategies, the trap checklist, the assertions with reasons, the frozen-oracle
reader and the generator of cards and `docs/FORMULAS.md`.

**CMP-8.2** The reference module is tested in Nogat, including a deliberately
wrong toy formula whose every defect each generator and assertion must catch.

**CMP-8.3** Hypothesis and mutmut are development dependencies of every
project that computes, at the versions of Nogat's release set, which pins
NumPy and SciPy to minor versions.

---

## 9. Defects in formulas

**CMP-9.1** A *gross defect* is any of: (1) a result for inputs inside the
typical range that is wrong beyond the tolerance, however discovered (a wrong
constant, exponent, unit, table entry, calendar or code convention); (2) a
non-finite value or a value outside the physical range returned silently for
accepted inputs; (3) a user-facing document that states a different unit or
range of an input or output than the code uses. A missing check of an extreme
or out-of-range input, and a wrong equation or constant in a document while
the code is right, are ordinary defects.
*Why:* a reader who trusts a wrong unit feeds wrong inputs; a misprinted
equation beside correct code misleads no result.

**CMP-9.2** A gross defect is fixed on a topic branch and released at once,
outside the release plan, as the next release of the project (a patch, or a
minor when the fix changes the interface, REL-1.1) and of every consumer that
re-exports or stores its results. The CHANGELOG names the formula, its
`formula_version`s before and after, the affected range of inputs, the size of
the error, and how to find and recompute stored results.

**CMP-9.3** A release of a project that computes requires: every Tier A
formula `referenced` or `oracle only`, or `unreferenced` with its notice; the
generated range, type and property tests passing; no unannotated surviving
mutant in Tier A; `docs/FORMULAS.md` fresh.
