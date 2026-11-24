"""Toy formulas for the tests of the reference module nogat_formulas (CMP-8.2).

A project that computes is imitated here: its own exceptions with a registry
code, a correct Kirpich-like formula, wrong copies of it with one defect each, an
array formula with gaps and an integer formula with a choice. The constants,
ranges and sources are made up for these tests and stand for no published value.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, replace

import numpy as np
from nogat_formulas import (
    Conservation,
    Constant,
    Constraint,
    FormulaSpec,
    Limit,
    Notice,
    Oracle,
    Output,
    Properties,
    Range,
    Scaling,
    Source,
    Tolerance,
    Values,
    Variable,
    assert_within,
    check_outputs,
    convert,
    validate,
)
from numpy.typing import NDArray


class ToyError(Exception):
    """An error of the toy project: a registry code and details (ERR-1)."""

    def __init__(self, message: str, *, code: str, details: dict[str, object]) -> None:
        super().__init__(message)
        self.code = code
        self.details = details


class ToyValidationError(ToyError, ValueError):
    """The toy project's ``validation_error``."""


class ToyCalculationError(ToyError, ArithmeticError):
    """The toy project's ``calculation_error``."""


class ToyErrors:
    """The toy project's :class:`nogat_formulas.Errors`."""

    def validation(self, message: str, details: dict[str, object]) -> Exception:
        """Return a ToyValidationError."""
        return ToyValidationError(message, code="validation_error", details=details)

    def calculation(self, message: str, details: dict[str, object]) -> Exception:
        """Return a ToyCalculationError."""
        return ToyCalculationError(message, code="calculation_error", details=details)


ERRORS = ToyErrors()
TOY = Source(citation="Toy source of the tests, no published value", locator="eq. 1")
DATA = Source(citation="Toy data of the tests", locator="table 1")


def _vanishing_length(run: Callable[..., Values]) -> None:
    tc = run(length_km=1e-12).real("tc_min")
    assert_within(tc, 0.0, abs=1e-6, reason="tc grows like L**a: about 6e-9 min")


KIRPICH = FormulaSpec(
    name="toy_kirpich",
    title="Kirpich-like time of concentration (toy)",
    function="formula_toys.toy_kirpich",
    family="empirical",
    equation="tc = c * (1000 L)**a * S**b",
    latex=r"t_c = c \, (1000 L)^{a} S^{b}",
    variables=(
        Variable(
            name="length_km",
            symbol="L",
            unit="km",
            description="Length of the flow path.",
            physical=Range(
                low=0.0,
                low_inclusive=False,
                test_high=1100.0,
                test_reason="longer than the Vistula, 1047 km",
            ),
            applicability=Range(low=0.12, high=1.22, source=TOY),
            typical=Range(low=0.5, high=30.0, source=DATA),
        ),
        Variable(
            name="slope_m_per_m",
            symbol="S",
            unit="m/m",
            physical=Range(
                low=0.0, test_high=10.0, test_reason="steeper than any path in the data"
            ),
            applicability=Range(low=0.03, high=0.1, source=TOY),
            typical=Range(low=0.001, high=0.2, source=DATA),
        ),
    ),
    outputs=(
        Output(
            name="tc_min",
            unit="min",
            symbol="t_c",
            physical=Range(low=0.0, low_inclusive=False),
        ),
    ),
    constraints=(
        Constraint(
            name="positive_slope",
            cls="precondition",
            check=lambda x: x.real("slope_m_per_m") > 0,
            text="S > 0",
            source=TOY,
            satisfied={"slope_m_per_m": 0.05},
            boundary={"slope_m_per_m": 5e-324},
            violated={"slope_m_per_m": 0.0},
        ),
    ),
    constants=(
        Constant(name="c", value=0.0195, unit="min m^-0.77", source=TOY),
        Constant(name="a", value=0.77, unit="-", source=TOY),
        Constant(name="b", value=-0.385, unit="-", source=TOY),
    ),
    sources=(TOY,),
    properties=Properties(
        units="unit_specific",
        monotonic={"length_km": 1, "slope_m_per_m": -1},
        limits=(
            Limit(
                name="vanishing_length",
                text="tc tends to 0 as L tends to 0",
                check=_vanishing_length,
            ),
        ),
    ),
    traps={"singular_at_bound": "range case slope_m_per_m-physical_low"},
    reference_cases=("formula_toys_cases.json",),
    conventions=("SI inside the formula: L in m from km by the units table",),
    validation="none",
    formula_version=1,
    status="referenced",
)


@dataclass(frozen=True)
class TcResult:
    """A result of the toy project: the output, its notices, its formula version."""

    tc_min: float
    notices: tuple[Notice, ...]
    formula_version: int


def _tc(x: Values, exponent: float) -> float:
    length_m = convert(x.real("length_km"), "km", "m")
    slope = x.real("slope_m_per_m")
    return float(
        KIRPICH.constant("c") * length_m**exponent * slope ** KIRPICH.constant("b")
    )


def toy_kirpich(length_km: float, slope_m_per_m: float) -> TcResult:
    """Kirpich-like time of concentration, spec ``toy_kirpich``."""
    inputs = {"length_km": length_km, "slope_m_per_m": slope_m_per_m}
    x, notices = validate(KIRPICH, inputs, errors=ERRORS)
    tc = _tc(x, KIRPICH.constant("a"))
    out = check_outputs(KIRPICH, {"tc_min": tc}, errors=ERRORS)
    return TcResult(out.real("tc_min"), tuple(notices), KIRPICH.formula_version)


def wrong_exponent(length_km: float, slope_m_per_m: float) -> TcResult:
    """Kirpich-like toy with a wrong exponent, spec ``toy_kirpich``."""
    inputs = {"length_km": length_km, "slope_m_per_m": slope_m_per_m}
    x, notices = validate(KIRPICH, inputs, errors=ERRORS)
    out = check_outputs(KIRPICH, {"tc_min": _tc(x, 0.7)}, errors=ERRORS)
    return TcResult(out.real("tc_min"), tuple(notices), 1)


NO_PRECONDITION = replace(
    KIRPICH,
    name="toy_kirpich_no_precondition",
    function="formula_toys.missing_precondition",
    constraints=(),
)


def missing_precondition(length_km: float, slope_m_per_m: float) -> TcResult:
    """Kirpich-like toy dividing by a power of the slope, spec ``toy_kirpich``."""
    inputs = {"length_km": length_km, "slope_m_per_m": slope_m_per_m}
    x, notices = validate(NO_PRECONDITION, inputs, errors=ERRORS)
    length_m = convert(x.real("length_km"), "km", "m")
    tc = 0.0195 * length_m**0.77 / x.real("slope_m_per_m") ** 0.385
    out = check_outputs(NO_PRECONDITION, {"tc_min": tc}, errors=ERRORS)
    return TcResult(out.real("tc_min"), tuple(notices), 1)


def accepts_bool(length_km: float, slope_m_per_m: float) -> TcResult:
    """Kirpich-like toy that makes floats of its inputs first, spec ``toy_kirpich``."""
    return toy_kirpich(float(length_km), float(slope_m_per_m))


def output_outside(length_km: float, slope_m_per_m: float) -> TcResult:
    """Kirpich-like toy with a stray term and no output check, spec ``toy_kirpich``."""
    inputs = {"length_km": length_km, "slope_m_per_m": slope_m_per_m}
    x, notices = validate(KIRPICH, inputs, errors=ERRORS)
    return TcResult(_tc(x, KIRPICH.constant("a")) - 0.5, tuple(notices), 1)


def drops_notices(length_km: float, slope_m_per_m: float) -> TcResult:
    """Kirpich-like toy that loses its notices, spec ``toy_kirpich``."""
    result = toy_kirpich(length_km, slope_m_per_m)
    return TcResult(result.tc_min, (), result.formula_version)


def default_errors(length_km: float, slope_m_per_m: float) -> TcResult:
    """Kirpich-like toy that raises the module's errors, spec ``toy_kirpich``."""
    inputs = {"length_km": length_km, "slope_m_per_m": slope_m_per_m}
    x, notices = validate(KIRPICH, inputs)
    out = check_outputs(KIRPICH, {"tc_min": _tc(x, KIRPICH.constant("a"))})
    return TcResult(out.real("tc_min"), tuple(notices), 1)


def wrong_sign(length_km: float, slope_m_per_m: float) -> TcResult:
    """Kirpich-like toy rising with the slope, spec ``toy_kirpich``."""
    inputs = {"length_km": length_km, "slope_m_per_m": slope_m_per_m}
    x, notices = validate(KIRPICH, inputs, errors=ERRORS)
    length_m = convert(x.real("length_km"), "km", "m")
    tc = 0.0195 * length_m**0.77 * x.real("slope_m_per_m") ** 0.385
    out = check_outputs(KIRPICH, {"tc_min": tc}, errors=ERRORS)
    return TcResult(out.real("tc_min"), tuple(notices), 1)


def digits_in_docstring(length_km: float, slope_m_per_m: float) -> TcResult:
    """Kirpich time of concentration, tc = 0.0195 L^0.77 S^-0.385 (toy_kirpich)."""
    return toy_kirpich(length_km, slope_m_per_m)


def _total_residual(inputs: Values, outputs: Values) -> float:
    depth = outputs.array("depth_mm")
    finite = depth[~np.isnan(depth)]
    last = float(finite.max()) if finite.size else 0.0
    return float(np.nansum(inputs.array("rain_mm"))) - last


def _all_gaps(run: Callable[..., Values]) -> None:
    depth = run(rain_mm=[math.nan, math.nan]).array("depth_mm")
    assert_within(depth, [math.nan, math.nan], abs=0.0, reason="gaps stay gaps")


CUMULATIVE = FormulaSpec(
    name="toy_cumulative_depth",
    title="Cumulative rainfall depth over a series with gaps (toy)",
    function="formula_toys.toy_cumulative_depth",
    family="index",
    equation="P_k = sum of p_i for i <= k; a gap stays a gap",
    latex=r"P_k = \sum_{i \le k} p_i",
    variables=(
        Variable(
            name="rain_mm",
            symbol="p",
            unit="mm",
            kind="real_array",
            gaps_allowed=True,
            max_length=1000,
            physical=Range(
                low=0.0, test_high=2000.0, test_reason="above any daily rainfall"
            ),
            applicability="unstated",
            typical=Range(low=0.0, high=50.0, source=DATA),
        ),
    ),
    outputs=(
        Output(
            name="depth_mm",
            unit="mm",
            kind="real_array",
            physical=Range(low=0.0),
            gaps_allowed=True,
            gaps_from="rain_mm",
        ),
    ),
    sources=(TOY,),
    properties=Properties(
        units="homogeneous",
        monotonic={"rain_mm": 1},
        scalings=(
            Scaling(
                name="depth",
                inputs={"rain_mm": 1.0},
                outputs={"depth_mm": 1.0},
                tolerance=Tolerance(abs=0.0, reason="a power of two scales exactly"),
            ),
        ),
        conservation=(
            Conservation(
                name="total",
                text="the last depth is the sum of the rainfall",
                residual=_total_residual,
                tolerance=Tolerance(
                    abs=1e-6, reason="pairwise and running sums of 1,051 values"
                ),
            ),
        ),
        limits=(
            Limit(
                name="all_gaps", text="a series of gaps is all gaps", check=_all_gaps
            ),
        ),
    ),
    traps={
        "gap_propagation": "type case rain_mm-nan_element",
        "many_small_terms": "the conservation property",
    },
    oracles=(
        Oracle(
            kind="exact",
            description="Sums of fractions.Fraction",
            test="tests/unit/test_nogat_formulas_toys.py",
        ),
    ),
    validation="none",
    formula_version=1,
    status="oracle only",
)


def toy_cumulative_depth(rain_mm: NDArray[np.float64]) -> dict[str, object]:
    """Cumulative rainfall depth with gaps, spec ``toy_cumulative_depth``."""
    x, notices = validate(CUMULATIVE, {"rain_mm": rain_mm}, errors=ERRORS)
    rain = x.array("rain_mm")
    depth = np.nancumsum(rain)
    depth[np.isnan(rain)] = np.nan
    out = check_outputs(CUMULATIVE, {"depth_mm": depth}, inputs=x, errors=ERRORS)
    return {"depth_mm": out.array("depth_mm"), "notices": notices}


def gap_spreads(rain_mm: NDArray[np.float64]) -> dict[str, object]:
    """Cumulative depth whose gaps spread on, spec ``toy_cumulative_depth``."""
    x, notices = validate(CUMULATIVE, {"rain_mm": rain_mm}, errors=ERRORS)
    depth = np.cumsum(x.array("rain_mm"))
    out = check_outputs(CUMULATIVE, {"depth_mm": depth}, inputs=x, errors=ERRORS)
    return {"depth_mm": out.array("depth_mm"), "notices": notices}


POSITION = FormulaSpec(
    name="toy_plotting_position",
    title="Plotting position of a ranked value (toy)",
    function="formula_toys.toy_plotting_position",
    family="statistic",
    equation="p = m / (n + 1) (weibull), (m - 0.44) / (n + 0.12) (gringorten)",
    latex=r"p = \frac{m - a}{n + 1 - 2a}",
    variables=(
        Variable(
            name="rank",
            symbol="m",
            unit="-",
            kind="integer",
            physical=Range(low=1.0, test_high=10_000.0, test_reason="long records"),
            applicability="unstated",
            typical=Range(low=1.0, high=100.0, source=DATA),
        ),
        Variable(
            name="count",
            symbol="n",
            unit="-",
            kind="integer",
            physical=Range(low=1.0, test_high=10_000.0, test_reason="long records"),
            applicability="unstated",
            typical=Range(low=10.0, high=100.0, source=DATA),
        ),
        Variable(
            name="method",
            symbol=r"\mathrm{method}",
            unit="-",
            kind="choice",
            choices=("weibull", "gringorten"),
        ),
    ),
    outputs=(
        Output(
            name="probability",
            unit="-",
            physical=Range(
                low=0.0, high=1.0, low_inclusive=False, high_inclusive=False
            ),
        ),
    ),
    constraints=(
        Constraint(
            name="rank_within_count",
            cls="physical",
            check=lambda x: x.integer("rank") <= x.integer("count"),
            text="m <= n",
            source=TOY,
            satisfied={"rank": 5, "count": 10},
            boundary={"rank": 10, "count": 10},
            violated={"rank": 11, "count": 10},
        ),
    ),
    sources=(TOY,),
    properties=Properties(
        units="homogeneous",
        monotonic={"rank": 1, "count": -1},
        scalings=(
            Scaling(
                name="dimensionless",
                inputs={},
                outputs={},
                tolerance=Tolerance(abs=0.0, reason="no input has a unit"),
            ),
        ),
        limits=(
            Limit(
                name="median_of_three",
                text="the second of three values lies at 1/2 by Weibull",
                inputs={"rank": 2, "count": 3, "method": "weibull"},
                expected={"probability": 0.5},
                tolerance=Tolerance(abs=0.0, reason="2/4 is exact in binary"),
            ),
        ),
    ),
    no_traps_reason="every denominator is at least 1.12",
    validation="none",
    formula_version=2,
    status="unreferenced",
)


def toy_plotting_position(rank: int, count: int, method: str) -> dict[str, object]:
    """Plotting position of a ranked value, spec ``toy_plotting_position``."""
    inputs = {"rank": rank, "count": count, "method": method}
    x, notices = validate(POSITION, inputs, errors=ERRORS)
    shift = 0.0 if x.choice("method") == "weibull" else 0.44
    m, n = x.integer("rank"), x.integer("count")
    out = check_outputs(
        POSITION, {"probability": (m - shift) / (n + 1 - 2 * shift)}, errors=ERRORS
    )
    return {"probability": out.real("probability"), "notices": notices}
