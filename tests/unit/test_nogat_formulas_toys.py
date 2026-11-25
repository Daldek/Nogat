"""The generators and assertions of nogat_formulas against toy formulas (CMP-8.2).

The correct toys of formula_toys pass every generated and declared test, as a
project's formulas would. Each wrong toy carries one defect, and its test shows
which generator or assertion catches it, and that the others stay quiet where
the defect does not show.
"""

from __future__ import annotations

import itertools
import math
from collections.abc import Callable
from dataclasses import replace
from fractions import Fraction
from pathlib import Path
from typing import Any, cast

import formula_toys as toys
import numpy as np
import pytest
from hypothesis import given, settings
from nogat_formulas import (
    Bounds,
    Case,
    Coverage,
    FormulaSpec,
    IntervalFunction,
    Output,
    Properties,
    Range,
    ReferenceCase,
    Source,
    SpecError,
    Symmetry,
    Tolerance,
    Values,
    Variable,
    assert_case,
    assert_coverage,
    assert_interval_properties,
    assert_limits,
    assert_monotonic,
    assert_properties,
    assert_property_contract,
    assert_within,
    check_outputs,
    docstring_problems,
    load_cases,
    range_cases,
    read_frozen_oracle,
    run_case,
    spec_problems,
    strategies,
    tolerance_problems,
    type_cases,
    validate,
)

ROOT = Path(__file__).parents[1]
REFERENCE = load_cases(ROOT / "formula_toys_cases.json", "toy_kirpich")
TOYS: list[tuple[FormulaSpec, Callable[..., object]]] = [
    (toys.KIRPICH, toys.toy_kirpich),
    (toys.CUMULATIVE, toys.toy_cumulative_depth),
    (toys.POSITION, toys.toy_plotting_position),
    (toys.MEAN_INTERVAL, toys.toy_mean_interval),
]
NAMES = [spec.name for spec, _ in TOYS]


def _generated(spec: FormulaSpec) -> list[Case]:
    params = range_cases(spec) + type_cases(spec)
    return [param.values[0] for param in params if isinstance(param.values[0], Case)]


def _failing(spec: FormulaSpec, function: Callable[..., object]) -> set[str]:
    """Return the ids of the generated cases the function fails."""
    failing = set()
    for case in _generated(spec):
        try:
            run_case(spec, function, case, toys.ERRORS)
        except AssertionError:
            failing.add(case.id)
    return failing


def _ids(spec: FormulaSpec, keep: Callable[[Case], bool]) -> set[str]:
    return {case.id for case in _generated(spec) if keep(case)}


# --- the correct toys pass everything -----------------------------------------


@pytest.mark.formula
@pytest.mark.parametrize("case", range_cases(toys.KIRPICH) + type_cases(toys.KIRPICH))
def test_toy_kirpich_at_and_beyond_its_limits(case: Case) -> None:
    run_case(toys.KIRPICH, toys.toy_kirpich, case, toys.ERRORS)


@pytest.mark.formula
@pytest.mark.parametrize(
    "case", range_cases(toys.CUMULATIVE) + type_cases(toys.CUMULATIVE)
)
def test_toy_cumulative_depth_at_and_beyond_its_limits(case: Case) -> None:
    run_case(toys.CUMULATIVE, toys.toy_cumulative_depth, case, toys.ERRORS)


@pytest.mark.formula
@pytest.mark.parametrize("case", range_cases(toys.POSITION) + type_cases(toys.POSITION))
def test_toy_plotting_position_at_and_beyond_its_limits(case: Case) -> None:
    run_case(toys.POSITION, toys.toy_plotting_position, case, toys.ERRORS)


@pytest.mark.formula
@given(inputs=strategies(toys.KIRPICH))
def test_toy_kirpich_properties(inputs: dict[str, object]) -> None:
    assert_property_contract(toys.KIRPICH, toys.toy_kirpich, inputs, toys.ERRORS)
    assert_properties(toys.KIRPICH, toys.toy_kirpich, inputs, toys.ERRORS)


@pytest.mark.formula
@given(inputs=strategies(toys.CUMULATIVE))
def test_toy_cumulative_depth_properties(inputs: dict[str, object]) -> None:
    function = toys.toy_cumulative_depth
    assert_property_contract(toys.CUMULATIVE, function, inputs, toys.ERRORS)
    assert_properties(toys.CUMULATIVE, function, inputs, toys.ERRORS)


@pytest.mark.formula
@given(inputs=strategies(toys.POSITION))
def test_toy_plotting_position_properties(inputs: dict[str, object]) -> None:
    function = toys.toy_plotting_position
    assert_property_contract(toys.POSITION, function, inputs, toys.ERRORS)
    assert_properties(toys.POSITION, function, inputs, toys.ERRORS)


@pytest.mark.formula
@given(inputs=strategies(toys.CUMULATIVE))
def test_toy_cumulative_depth_against_exact_sums(inputs: dict[str, object]) -> None:
    rain = inputs["rain_mm"]
    assert isinstance(rain, np.ndarray)
    depth = toys.toy_cumulative_depth(rain)["depth_mm"]
    assert isinstance(depth, np.ndarray)
    exact = [float(s) for s in itertools.accumulate(Fraction(x) for x in rain)]
    assert_within(
        depth,
        exact,
        rel=1e-13,
        abs=0.0,
        reason="a running float64 sum of at most 51 terms of one sign",
    )


@pytest.mark.formula
@pytest.mark.parametrize(("spec", "function"), TOYS, ids=NAMES)
def test_toy_limits(spec: FormulaSpec, function: Callable[..., object]) -> None:
    assert_limits(spec, function, toys.ERRORS)


@pytest.mark.formula
@pytest.mark.parametrize("case", REFERENCE, ids=lambda case: case.case_id)
def test_toy_kirpich_reference_cases(case: ReferenceCase) -> None:
    assert_case(toys.KIRPICH, toys.toy_kirpich, case, toys.ERRORS)


@pytest.mark.parametrize(("spec", "function"), TOYS, ids=NAMES)
def test_toy_specs_keep_the_standard(
    spec: FormulaSpec, function: Callable[..., object]
) -> None:
    assert spec_problems(spec, function, root=ROOT) == []


# --- every defect is caught -----------------------------------------------------


def test_a_wrong_exponent_is_caught_by_the_reference_cases() -> None:
    assert _failing(toys.KIRPICH, toys.wrong_exponent) == set()
    for case in REFERENCE:
        with pytest.raises(AssertionError, match=r"\(CMP-6\.1\)"):
            assert_case(toys.KIRPICH, toys.wrong_exponent, case, toys.ERRORS)


def test_a_missing_precondition_is_caught_by_range_cases_and_properties() -> None:
    spec, function = toys.NO_PRECONDITION, toys.missing_precondition
    assert _failing(spec, function) == {"slope_m_per_m-physical_low"}

    @settings(report_multiple_bugs=False)
    @given(inputs=strategies(spec))
    def contract(inputs: dict[str, object]) -> None:
        assert_property_contract(spec, function, inputs, toys.ERRORS)

    with pytest.raises(AssertionError, match="raised ZeroDivisionError"):
        contract()


def test_an_accepted_bool_is_caught_by_the_type_cases() -> None:
    failing = _failing(toys.KIRPICH, toys.accepts_bool)
    assert {"length_km-bool_true", "slope_m_per_m-numpy_bool"} <= failing
    assert failing == _ids(toys.KIRPICH, lambda case: case.reason == "invalid_type")


def test_an_output_outside_its_range_is_caught() -> None:
    assert _failing(toys.KIRPICH, toys.output_outside) == {
        "length_km-physical_low_inside"
    }

    @settings(report_multiple_bugs=False)
    @given(inputs=strategies(toys.KIRPICH))
    def contract(inputs: dict[str, object]) -> None:
        assert_property_contract(toys.KIRPICH, toys.output_outside, inputs, toys.ERRORS)

    with pytest.raises(AssertionError, match="outside its physical range"):
        contract()


def test_lost_notices_are_caught_by_the_range_and_type_cases() -> None:
    failing = _failing(toys.KIRPICH, toys.drops_notices)
    assert failing == _ids(toys.KIRPICH, lambda case: case.expect == "ok+notice")


def test_the_module_errors_instead_of_the_projects_are_caught() -> None:
    failing = _failing(toys.KIRPICH, toys.default_errors)
    expected = _ids(toys.KIRPICH, lambda case: case.expect == "validation_error")
    assert failing == expected


def test_a_wrong_monotonicity_is_caught_by_the_monotonic_property() -> None:
    @settings(report_multiple_bugs=False)
    @given(inputs=strategies(toys.KIRPICH))
    def monotonic(inputs: dict[str, object]) -> None:
        assert_monotonic(toys.KIRPICH, toys.wrong_sign, inputs, toys.ERRORS)

    with pytest.raises(AssertionError, match="decreasing in slope_m_per_m"):
        monotonic()
    assert _failing(toys.KIRPICH, toys.wrong_sign) == set()


def test_a_gap_that_spreads_is_caught_by_the_type_cases() -> None:
    assert _failing(toys.CUMULATIVE, toys.gap_spreads) == {"rain_mm-nan_element"}


def _cumulative(change: Callable[[np.ndarray], np.ndarray]) -> Callable[..., object]:
    def function(rain_mm: object) -> dict[str, object]:
        x, notices = validate(toys.CUMULATIVE, {"rain_mm": rain_mm}, errors=toys.ERRORS)
        rain = x.array("rain_mm")
        depth = change(np.nancumsum(rain))
        depth[np.isnan(rain)] = np.nan
        checked = check_outputs(toys.CUMULATIVE, {"depth_mm": depth}, inputs=x)
        return {"depth_mm": checked.array("depth_mm"), "notices": notices}

    return function


def _last_dropped(depth: np.ndarray) -> np.ndarray:
    if depth.size > 1:
        depth[-1] = depth[-2]
    return depth


@pytest.mark.parametrize(
    ("function", "message"),
    [
        (_cumulative(lambda depth: depth + 1.0), "scaling depth"),
        (_cumulative(_last_dropped), "conservation total"),
    ],
    ids=["offset", "lost_term"],
)
def test_a_broken_scaling_or_conservation_is_caught_by_the_properties(
    function: Callable[..., object], message: str
) -> None:
    @settings(report_multiple_bugs=False)
    @given(inputs=strategies(toys.CUMULATIVE))
    def properties(inputs: dict[str, object]) -> None:
        assert_properties(toys.CUMULATIVE, function, inputs, toys.ERRORS)

    with pytest.raises(AssertionError, match=message):
        properties()


GAUGE = Variable(
    name="a_mm",
    symbol="a",
    unit="mm",
    physical=Range(low=0.0, test_high=2000.0, test_reason="above any daily rainfall"),
    applicability="unstated",
    typical=Range(low=0.0, high=50.0, source=toys.DATA),
)
MEAN = FormulaSpec(
    name="toy_mean_of_two",
    title="Mean rainfall of two gauges (toy)",
    function="test_nogat_formulas_toys.mean_of_two",
    family="index",
    equation="m = (a + b) / 2",
    latex=r"m = \frac{a + b}{2}",
    variables=(GAUGE, replace(GAUGE, name="b_mm", symbol="b")),
    outputs=(Output(name="mean_mm", unit="mm", physical=Range(low=0.0)),),
    sources=(toys.TOY,),
    properties=Properties(
        units="unit_specific",
        monotonic={"a_mm": 1, "b_mm": 1},
        symmetries=(
            Symmetry(
                name="gauges",
                text="the gauges can swap",
                inputs=lambda x: {"a_mm": x["b_mm"], "b_mm": x["a_mm"]},
                outputs=lambda y: {"mean_mm": y["mean_mm"]},
                tolerance=Tolerance(abs=0.0, reason="a + b is b + a in IEEE 754"),
            ),
        ),
    ),
    no_traps_reason="a sum of two terms of one sign",
    validation="none",
    formula_version=1,
    status="unreferenced",
)


def _mean(weight: float) -> Callable[..., object]:
    def mean_of_two(a_mm: float, b_mm: float) -> dict[str, object]:
        x, notices = validate(MEAN, {"a_mm": a_mm, "b_mm": b_mm}, errors=toys.ERRORS)
        mean = (x.real("a_mm") + weight * x.real("b_mm")) / (1 + weight)
        out = check_outputs(MEAN, {"mean_mm": mean}, errors=toys.ERRORS)
        return {"mean_mm": out.real("mean_mm"), "notices": notices}

    return mean_of_two


def test_a_broken_symmetry_is_caught_by_the_properties() -> None:
    assert_properties(MEAN, _mean(1.0), {"a_mm": 1.0, "b_mm": 3.0}, toys.ERRORS)
    with pytest.raises(AssertionError, match="symmetry gauges"):
        assert_properties(MEAN, _mean(2.0), {"a_mm": 1.0, "b_mm": 3.0}, toys.ERRORS)


def test_a_wrong_limit_is_caught() -> None:
    def broken(rank: int, count: int, method: str) -> dict[str, object]:
        result = toys.toy_plotting_position(rank, count, method)
        return result | {"probability": float(rank) / (count + 2)}

    with pytest.raises(AssertionError, match="limit median_of_three"):
        assert_limits(toys.POSITION, broken, toys.ERRORS)


def test_digits_in_a_docstring_are_caught() -> None:
    [problem] = docstring_problems(toys.KIRPICH, toys.digits_in_docstring)
    assert "(CMP-2.7)" in problem
    problems = spec_problems(toys.KIRPICH, toys.digits_in_docstring, root=ROOT)
    assert any("digits_in_docstring" in p for p in problems)


def test_a_tolerance_without_its_reason_is_caught() -> None:
    with pytest.raises(ValueError, match="CMP-6.8"):
        assert_within(13.7, 13.748, abs=0.1, reason="")
    assert tolerance_problems("assert tc == pytest.approx(13.7)\n", "t.py") == [
        "t.py:1: approx() without an explicit tolerance (CMP-6.8)"
    ]


def test_a_frozen_oracle_without_its_versions_is_caught(tmp_path: Path) -> None:
    path = tmp_path / "oracle.csv"
    path.write_text("# tool: R\n# date: 2026-11-18\nx,y\n1,2\n", encoding="utf-8")
    with pytest.raises(
        ValueError, match=r"missing \['packages', 'platform', 'script'\]"
    ):
        read_frozen_oracle(path)


def test_a_predicate_contradicting_its_points_is_caught() -> None:
    wrong = replace(
        toys.KIRPICH.constraints[0], check=lambda x: x.real("slope_m_per_m") >= 0
    )
    with pytest.raises(SpecError, match="violated point"):
        range_cases(replace(toys.KIRPICH, constraints=(wrong,)))


def test_a_stale_status_is_caught() -> None:
    stale = replace(toys.CUMULATIVE, status="referenced")
    assert spec_problems(stale, toys.toy_cumulative_depth) == [
        "toy_cumulative_depth: status 'referenced', its evidence gives 'oracle only' "
        "(CMP-2.6)"
    ]
    unsourced = replace(
        toys.KIRPICH,
        reference_cases=(),
        properties=Properties(units="unit_specific"),
        sources=(Source(citation="Toy"),),
    )
    problems = spec_problems(unsourced)
    assert any("CMP-5.1 needs two" in p for p in problems)
    assert any("unit-specific formula needs reference cases" in p for p in problems)


def test_the_generated_cases_name_the_failing_input() -> None:
    with pytest.raises(AssertionError) as caught:
        run_case(
            toys.KIRPICH,
            toys.accepts_bool,
            next(c for c in _generated(toys.KIRPICH) if c.id == "length_km-bool_true"),
            toys.ERRORS,
        )
    assert str(caught.value).startswith(
        "toy_kirpich [length_km-bool_true]: accepts_bool"
    )


def test_values_of_the_toys_reach_the_formula_as_float64() -> None:
    values: Values = validate(toys.KIRPICH, {"length_km": 1, "slope_m_per_m": 1})[0]
    assert values == {"length_km": 1.0, "slope_m_per_m": 1.0}


# --- intervals and their coverage (CMP-6.11) ------------------------------------

SIGMA = 2.0
MU = 10.0
LEVELS = (0.95, 0.68)


def _normal(generator: np.random.Generator, size: int) -> np.ndarray:
    return generator.normal(MU, SIGMA, size)


def _interval(function: Callable[..., dict[str, object]]) -> IntervalFunction:
    """The toy's interval at every level asked, as assert_coverage calls it."""

    def interval(sample: np.ndarray, levels: tuple[float, ...]) -> list[Bounds]:
        results = [function(sample, SIGMA, c) for c in levels]
        return [(cast(float, r["lower_m"]), cast(float, r["upper_m"])) for r in results]

    return interval


def _coverage(
    function: Callable[..., dict[str, object]], **kwargs: Any
) -> list[Coverage]:
    arguments: dict[str, Any] = {
        "setting": f"normal, mean {MU}, sigma {SIGMA}",
        "size": 30,
        "confidence_level": LEVELS,
        "seed": 20261125,  # fixed once, the day written, never chosen to pass
        "reason": "the interval of a normal mean with sigma known is exact",
        **kwargs,
    }
    return assert_coverage(
        toys.MEAN_INTERVAL, _interval(function), _normal, MU, **arguments
    )


@pytest.mark.formula
@pytest.mark.parametrize("size", [30, 60])
def test_an_exact_interval_covers_at_its_levels(size: int) -> None:
    records = _coverage(toys.toy_mean_interval, size=size)
    assert [(r.confidence_level, r.check, r.size) for r in records] == [
        (0.95, "exact", size),
        (0.68, "exact", size),
    ]
    assert all(r.undefined == (0,) and r.samples == 1000 for r in records)


def test_a_too_narrow_interval_is_caught_by_its_coverage() -> None:
    with pytest.raises(
        AssertionError, match=r"c = 0\.95: coverage 0\.\d+, not 0\.95 ±"
    ):
        _coverage(toys.too_narrow)


def test_a_bound_takes_a_lower_coverage_and_catches_one_below_it() -> None:
    [record] = _coverage(
        toys.too_narrow,
        confidence_level=0.95,
        at_least={0.95: 0.2},
        reason="a bound the narrow toy keeps",
    )
    assert record.check == "bound" and 0.2 < record.coverage[0] < 0.5
    with pytest.raises(AssertionError, match=r"not at least 0\.5 - 0\.0474 \(bound"):
        _coverage(toys.too_narrow, confidence_level=0.95, at_least={0.95: 0.5})


def test_an_expected_coverage_is_asserted_instead_of_the_level() -> None:
    [record] = _coverage(
        toys.toy_mean_interval, confidence_level=0.95, expected={0.95: 0.95}
    )
    assert record.check == "expected" and record.target == (0.95,)
    with pytest.raises(AssertionError, match=r"not 0\.9 ± 0\.0285 \(expected"):
        _coverage(toys.toy_mean_interval, confidence_level=0.95, expected={0.95: 0.9})


def test_swapped_bounds_are_caught_on_the_first_sample() -> None:
    with pytest.raises(
        AssertionError, match=r"sample 0 of seed 20261125: at c = 0\.95 the lower bound"
    ):
        _coverage(toys.bounds_swapped)


def test_crossed_levels_are_caught_by_the_nesting_of_intervals() -> None:
    sample = _normal(np.random.default_rng(1), 30)
    assert_interval_properties(_interval(toys.toy_mean_interval), sample, LEVELS)
    assert_interval_properties(_interval(toys.levels_crossed), sample, 0.95)
    with pytest.raises(
        AssertionError, match=r"at c = 0\.68, \[.*\], is not inside that at c = 0\.95"
    ):
        assert_interval_properties(_interval(toys.levels_crossed), sample, LEVELS)


def test_a_bound_not_computed_holds_nothing_and_breaks_no_property() -> None:
    def lower_missing(sample: np.ndarray, levels: tuple[float, ...]) -> list[Bounds]:
        return [
            (math.nan, upper)
            for _, upper in _interval(toys.toy_mean_interval)(sample, levels)
        ]

    records = assert_coverage(
        toys.MEAN_INTERVAL,
        lower_missing,
        _normal,
        MU,
        setting="normal",
        size=30,
        confidence_level=LEVELS,
        seed=1,
        at_least={0.95: 0.0, 0.68: 0.0},
        reason="no lower bound is computed",
    )
    assert [(r.coverage, r.undefined) for r in records] == [((0.0,), (1000,))] * 2


def test_the_coverage_of_each_element_is_asserted() -> None:
    truth = np.array([MU, 2 * MU])

    def draw(generator: np.random.Generator, size: int) -> np.ndarray:
        return generator.normal(truth, SIGMA, (size, 2))

    def interval(sample: np.ndarray, levels: tuple[float, ...]) -> list[Bounds]:
        right = _interval(toys.toy_mean_interval)
        narrow = _interval(toys.too_narrow)
        pairs = zip(
            right(sample[:, 0], levels), narrow(sample[:, 1], levels), strict=True
        )
        return [
            (np.array([lo0, lo1]), np.array([hi0, hi1]))
            for (lo0, hi0), (lo1, hi1) in pairs
        ]

    arguments: dict[str, Any] = {
        "setting": "two normal means",
        "size": 30,
        "confidence_level": 0.95,
        "seed": 7,
        "reason": "exact on the first, a bound on the second",
    }
    [record] = assert_coverage(
        toys.MEAN_INTERVAL,
        interval,
        draw,
        truth,
        at_least={0.95: [0.95, 0.2]},
        **arguments,
    )
    assert record.target == (0.95, 0.2) and len(record.coverage) == 2
    with pytest.raises(AssertionError, match=r"coverage 0\.\d+ at \[1\], not 0\.95 ±"):
        assert_coverage(toys.MEAN_INTERVAL, interval, draw, truth, **arguments)
