"""The reference module of formulas every project that computes copies (CMP-8.1)."""

from __future__ import annotations

import json
import math
import random
import tomllib
import warnings
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass, replace
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any, cast

import formula_toys as toys
import numpy as np
import pytest
from _pytest.outcomes import Skipped
from hypothesis import given, settings
from hypothesis.database import DirectoryBasedExampleDatabase
from nogat_formulas import (
    CARD_FORMAT,
    TRAPS,
    UNITS,
    Bounds,
    Case,
    Constant,
    Constraint,
    Coverage,
    Delegated,
    FormulaCalculationError,
    FormulaSpec,
    FormulaValidationError,
    Limit,
    Notice,
    Oracle,
    Output,
    Properties,
    Range,
    ReferenceCase,
    Scaling,
    Source,
    SpecError,
    Table,
    TierBSpec,
    Tolerance,
    Values,
    Variable,
    assert_case,
    assert_coverage,
    assert_interval_properties,
    assert_limits,
    assert_within,
    card,
    case_tolerance,
    check_outputs,
    convert,
    docstring_problems,
    formulas_markdown,
    load_cases,
    range_cases,
    read_frozen_oracle,
    register_profiles,
    rounding_tolerance,
    run_case,
    spec_problems,
    strategies,
    to_toml,
    tolerance_problems,
    type_cases,
    validate,
)

SRC = Source(citation="Unit-test source", locator="eq. 1")
X = Variable(
    name="x_m",
    symbol="x",
    unit="m",
    physical=Range(low=0.0, high=10.0, low_inclusive=False),
    applicability=Range(low=1.0, high=5.0, source=SRC),
    typical=Range(low=2.0, high=4.0, source=SRC),
)
Y = Variable(
    name="y_m",
    symbol="y",
    unit="m",
    physical=Range(low=0.0, test_high=100.0, test_reason="a test"),
    applicability="unstated",
    typical=Range(low=1.0, high=3.0, source=SRC),
)
Z = Output(name="z_m", unit="m", physical=Range(low=0.0, high=1000.0))
ONE = FormulaSpec(
    name="one",
    title="One input",
    function="test_nogat_formulas.one",
    family="empirical",
    equation="z = x",
    latex="z = x",
    variables=(X,),
    outputs=(Z,),
    sources=(SRC,),
    properties=Properties(units="unit_specific", monotonic={"x_m": 1}),
    traps={"singular_at_bound": "x_m-physical_low"},
    reference_cases=("cases.json",),
    validation="none",
    formula_version=1,
    status="referenced",
)


def _constraint(
    name: str, cls: Any, check: Callable[[Values], object], violated: dict[str, object]
) -> Constraint:
    return Constraint(
        name=name,
        cls=cls,
        check=check,
        text=name,
        source=SRC,
        satisfied={"x_m": 2.0, "y_m": 3.0},
        violated=violated,
    )


PAIR = replace(
    ONE,
    name="pair",
    variables=(X, Y),
    constraints=(
        _constraint(
            "not_twice",
            "physical",
            lambda v: v.real("x_m") <= 2 * v.real("y_m"),
            {"x_m": 7.0, "y_m": 3.0},
        ),
        _constraint(
            "distinct",
            "precondition",
            lambda v: v.real("x_m") != v.real("y_m"),
            {"x_m": 3.0, "y_m": 3.0},
        ),
        _constraint(
            "shorter",
            "applicability",
            lambda v: v.real("x_m") < v.real("y_m"),
            {"x_m": 3.0, "y_m": 2.0},
        ),
    ),
)


def one(x_m: float) -> dict[str, object]:
    """Echo of its input, spec ``one``."""
    x, notices = validate(ONE, {"x_m": x_m}, errors=toys.ERRORS)
    return {
        "z_m": check_outputs(ONE, {"z_m": x.real("x_m")}).real("z_m"),
        "notices": notices,
    }


def _refusal(spec: FormulaSpec, inputs: Mapping[str, object]) -> dict[str, object]:
    with pytest.raises(toys.ToyValidationError) as caught:
        validate(spec, inputs, errors=toys.ERRORS)
    return caught.value.details


# --- declarations ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"low": 1.0, "high": 0.0}, "empty"),
        ({"low": 1.0, "high": 1.0, "low_inclusive": False}, "empty"),
        ({"low": math.nan}, "no interval"),
        ({"low": math.inf}, "no interval"),
        ({"low": 0.0, "test_low": -1.0, "test_reason": "r"}, "finite end"),
        ({"low": 0.0, "test_high": -1.0, "test_reason": "r"}, "inner value"),
        ({"low": 0.0, "test_high": 0.0, "test_reason": "r"}, "inner value"),
        ({"low": 0.0, "test_high": 5.0}, "reason"),
        ({"test_low": 5.0, "test_high": 1.0, "test_reason": "r"}, "below"),
    ],
)
def test_range_refuses_what_is_no_range(kwargs: dict[str, Any], message: str) -> None:
    with pytest.raises(SpecError, match=message):
        Range(**kwargs)


def test_range_contains_its_ends_as_declared_and_never_nan() -> None:
    rng = Range(low=0.0, high=1.0, low_inclusive=False)
    values = np.array([0.0, 5e-324, 1.0, math.nextafter(1.0, 2.0), math.nan, -1.0])
    expected = [False, True, True, False, False, False]
    assert [rng.contains(float(v)) for v in values] == expected
    assert rng.mask(values).tolist() == expected
    assert rng.interval() == "(0.0, 1.0]"
    assert rng.details() == {
        "low": 0.0,
        "high": 1.0,
        "low_inclusive": False,
        "high_inclusive": True,
    }


def test_range_gives_test_bounds_for_unbounded_ends() -> None:
    rng = Range(test_low=-5.0, test_high=7.0, test_reason="data")
    assert (rng.lower, rng.upper) == (-5.0, 7.0)
    assert rng.interval() == "(-inf, inf)"
    assert rng.details()["low"] is None
    with pytest.raises(SpecError, match="no test bound"):
        _ = Range(low=0.0).upper


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"name": "Area"}, "snake_case"),
        ({"physical": None}, "no physical range"),
        ({"physical": Range(low=0.0)}, "test bound"),
        ({"applicability": None}, "unstated"),
        ({"applicability": Range(low=1.0, high=2.0)}, "its source"),
        ({"typical": None}, "typical range"),
        ({"typical": Range(low=2.0, high=4.0)}, "typical range"),
        (
            {"typical": Range(low=2.0, high=4.0, low_inclusive=False, source=SRC)},
            "closed",
        ),
        ({"typical": Range(low=-1.0, high=4.0, source=SRC)}, "not within"),
        ({"gaps_allowed": True}, "only an array"),
        ({"choices": ("a",)}, "only a choice"),
        ({"kind": "integer", "physical": Range(low=0.5, high=10.0)}, "whole"),
        ({"kind": "real_array", "min_length": 5, "max_length": 2}, "max_length"),
        ({"kind": "matrix"}, "unknown"),
    ],
)
def test_variable_refuses_an_incomplete_declaration(
    changes: dict[str, Any], message: str
) -> None:
    with pytest.raises(SpecError, match=message):
        replace(X, **changes)


def test_a_choice_has_distinct_choices_and_no_ranges() -> None:
    with pytest.raises(SpecError, match="distinct"):
        Variable(name="m", symbol="m", unit="-", kind="choice", choices=("a", "a"))
    with pytest.raises(SpecError, match="no ranges"):
        Variable(
            name="m",
            symbol="m",
            unit="-",
            kind="choice",
            choices=("a",),
            physical=X.physical,
        )


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"kind": "choice"}, "only a choice"),
        ({"physical": None}, "physical range"),
        ({"boundary_tolerance": -1.0}, "boundary_tolerance"),
        ({"gaps_allowed": True}, "only an array"),
        ({"kind": "real_array", "gaps_from": "x_m"}, "gaps_allowed"),
    ],
)
def test_output_refuses_an_incomplete_declaration(
    changes: dict[str, Any], message: str
) -> None:
    with pytest.raises(SpecError, match=message):
        replace(Z, **changes)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"reason": "why"}, "abs or rel"),
        ({"abs": 0.1, "reason": " "}, "reason"),
        ({"rel": -0.1, "reason": "why"}, ">= 0"),
        ({"abs": math.inf, "reason": "why"}, ">= 0"),
    ],
)
def test_tolerance_needs_a_size_and_a_reason(
    kwargs: dict[str, Any], message: str
) -> None:
    with pytest.raises(SpecError, match=message):
        Tolerance(**kwargs)


def test_limit_has_expected_outputs_or_a_check() -> None:
    with pytest.raises(SpecError, match="one"):
        Limit(name="l", text="t")
    with pytest.raises(SpecError, match="one"):
        Limit(name="l", text="t", expected={"z_m": 1.0}, check=lambda run: None)
    with pytest.raises(SpecError, match="tolerance"):
        Limit(name="l", text="t", expected={"z_m": 1.0})


def test_properties_pair_scalings_with_homogeneity() -> None:
    scaling = Scaling(
        name="s", inputs={}, outputs={}, tolerance=Tolerance(abs=0.0, reason="r")
    )
    with pytest.raises(SpecError, match="homogeneous"):
        Properties(units="homogeneous")
    with pytest.raises(SpecError, match="homogeneous"):
        Properties(units="unit_specific", scalings=(scaling,))
    with pytest.raises(SpecError, match="1 or -1"):
        Properties(units="unit_specific", monotonic={"x_m": cast(Any, 2)})
    assert not Properties(units="unit_specific").declared


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"family": "magic"}, "family"),
        ({"traps": {"moment_cancellation": "t"}}, "not of family"),
        ({"traps": {"singular_at_bound": " "}}, "its test"),
        ({"traps": {}}, "why none"),
        ({"outputs": (replace(Z, name="x_m"),)}, "repeat"),
        ({"formula_version": 0}, "formula_version"),
        ({"status": "verified"}, "status"),
        ({"base": {"q": 1.0}}, "unknown inputs"),
        (
            {"properties": Properties(units="unit_specific", monotonic={"q": 1})},
            "monotonic",
        ),
        ({"title": "two\nlines"}, "one line"),
        ({"validation": ""}, "validation"),
        ({"notices": ("Bad",)}, "snake_case"),
        (
            {
                "outputs": (
                    Output(
                        name="w",
                        unit="m",
                        kind="real_array",
                        physical=Range(low=0.0),
                        gaps_allowed=True,
                        gaps_from="x_m",
                    ),
                )
            },
            "no array",
        ),
    ],
)
def test_spec_refuses_what_breaks_the_standard(
    changes: dict[str, Any], message: str
) -> None:
    with pytest.raises(SpecError, match=message):
        replace(ONE, **changes)


@pytest.mark.parametrize(
    "make",
    [
        lambda: replace(X, unit=" "),
        lambda: replace(Z, unit=""),
        lambda: Constant(name="k", value=1.0, unit="", source=SRC),
        lambda: Limit(name="", text="t", check=lambda run: None),
        lambda: Oracle(kind="exact", description="d", test=""),
        lambda: Oracle(kind="exact", description="d", test="t", conventions=("",)),
        lambda: Table(path="", sha256="0" * 64, source=SRC, comparison="c"),
        lambda: Delegated(name="a", library="", versions="v", smoke_case="s", test="t"),
        lambda: TierBSpec(
            name="b", function="m.f", definition="", convention="c", source=SRC
        ),
        lambda: replace(ONE, function="one"),
        lambda: replace(ONE, conventions=("",)),
        lambda: replace(ONE, reference_cases=(" ",)),
        lambda: replace(Z, kind="choice", physical=None, choices=("",)),
    ],
)
def test_declarations_refuse_texts_a_card_could_not_hold(
    make: Callable[[], object],
) -> None:
    with pytest.raises(SpecError):
        make()


def test_spec_finds_its_parts_and_codes() -> None:
    assert toys.KIRPICH.constant("c") == 0.0195
    assert toys.KIRPICH.variable("length_km").unit == "km"
    assert toys.KIRPICH.output("tc_min").unit == "min"
    with pytest.raises(KeyError):
        toys.KIRPICH.constant("d")
    with pytest.raises(KeyError):
        toys.KIRPICH.variable("d")
    with pytest.raises(KeyError):
        toys.KIRPICH.output("d")
    assert toys.KIRPICH.notice_codes() == ("outside_applicability",)
    assert toys.POSITION.notice_codes() == ("unreferenced_formula",)
    assert replace(ONE, notices=("short_record",)).notice_codes() == (
        "outside_applicability",
        "short_record",
    )


def test_the_trap_checklist_holds_the_traps_of_the_standard() -> None:
    named = {trap.name for traps in TRAPS.values() for trap in traps}
    assert named >= {
        "difference_denominator",
        "singular_at_bound",
        "exp_overflow",
        "unbounded_iteration",
        "stability_bound",
        "gap_propagation",
        "many_small_terms",
        "moment_cancellation",
    }
    assert set(TRAPS) == {"empirical", "scheme", "statistic", "index", "classification"}


# --- validate (CMP §3, CMP-4.2) ------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [3, 3.0, np.int64(3), np.int32(3), np.uint8(3), np.float32(3.0), np.float64(3.0)],
    ids=lambda v: type(v).__name__,
)
def test_validate_turns_every_real_kind_into_a_float(value: object) -> None:
    values, _ = validate(ONE, {"x_m": value})
    assert type(values["x_m"]) is float
    assert values.real("x_m") == 3.0


@pytest.mark.parametrize(
    "value",
    [
        True,
        False,
        np.bool_(True),
        None,
        "3",
        Decimal("3"),
        complex(3, 0),
        np.complex128(3),
        [3.0],
        np.array(3.0),
        Fraction(3),
        np.timedelta64(3, "s"),
        np.datetime64("2026-11-18"),
    ],
    ids=lambda v: type(v).__name__,
)
def test_validate_refuses_what_is_not_a_real_number(value: object) -> None:
    details = _refusal(ONE, {"x_m": value})
    assert details["reason"] == "invalid_type"
    assert details["variable"] == "x_m"
    assert details["formula"] == "one"


@pytest.mark.parametrize(
    ("value", "shown"),
    [(math.nan, "nan"), (math.inf, "inf"), (-math.inf, "-inf"), (10**400, 10**400)],
    ids=["nan", "inf", "minus_inf", "huge_int"],
)
def test_validate_refuses_a_number_that_is_not_finite(
    value: float, shown: object
) -> None:
    details = _refusal(ONE, {"x_m": value})
    assert details["reason"] == "outside_physical_range"
    assert details["value"] == shown


@pytest.mark.parametrize("value", [0.0, -1.0, math.nextafter(10.0, 11.0)])
def test_validate_refuses_a_value_outside_its_physical_range(value: float) -> None:
    with pytest.raises(toys.ToyValidationError) as caught:
        validate(ONE, {"x_m": value}, errors=toys.ERRORS)
    assert caught.value.details == {
        "reason": "outside_physical_range",
        "formula": "one",
        "variable": "x_m",
        "value": value,
        "unit": "m",
        "range": X.physical.details() if X.physical else {},
    }
    assert "(0.0, 10.0]" in str(caught.value)


def test_validate_gives_one_applicability_notice_per_variable_and_constraint() -> None:
    _, inside = validate(PAIR, {"x_m": 2.0, "y_m": 3.0})
    assert inside == []
    _, notices = validate(PAIR, {"x_m": 6.0, "y_m": 5.0})
    assert [(n.level, n.code) for n in notices] == [
        ("warning", "outside_applicability")
    ] * 2
    assert notices[0].details == {
        "formula": "pair",
        "variable": "x_m",
        "unit": "m",
        "range": {
            "low": 1.0,
            "high": 5.0,
            "low_inclusive": True,
            "high_inclusive": True,
        },
        "source": "Unit-test source, eq. 1",
        "value": 6.0,
    }
    assert notices[1].details["constraint"] == "shorter"
    assert "Unit-test source, eq. 1" in notices[0].message
    assert notices[1].as_dict()["code"] == "outside_applicability"


def test_validate_refuses_physical_constraints_before_preconditions() -> None:
    assert (
        _refusal(PAIR, {"x_m": 7.0, "y_m": 3.0})["reason"] == "outside_physical_range"
    )
    details = _refusal(PAIR, {"x_m": 3.0, "y_m": 3.0})
    assert details["reason"] == "precondition_failed"
    assert details["constraint"] == "distinct"
    assert details["class"] == "precondition"


def test_validate_checks_types_and_ranges_in_the_specs_order() -> None:
    assert _refusal(PAIR, {"x_m": "a", "y_m": -1.0})["variable"] == "x_m"
    assert _refusal(PAIR, {"x_m": 2.0, "y_m": -1.0})["variable"] == "y_m"


def test_an_unreferenced_formula_says_so_on_every_result() -> None:
    _, notices = validate(toys.POSITION, {"rank": 2, "count": 3, "method": "weibull"})
    assert [(n.level, n.code) for n in notices] == [("info", "unreferenced_formula")]
    assert notices[0].details["formula_version"] == 2


def test_validate_raises_the_module_errors_by_default() -> None:
    with pytest.raises(FormulaValidationError) as caught:
        validate(ONE, {"x_m": True})
    assert isinstance(caught.value, ValueError)
    assert caught.value.code == "validation_error"
    assert caught.value.details["reason"] == "invalid_type"
    assert caught.value.message.startswith("one: x_m must be a real number")


def test_validate_takes_exactly_the_specs_inputs() -> None:
    with pytest.raises(TypeError, match=r"missing \['x_m'\], unknown \['q'\]"):
        validate(ONE, {"q": 1.0})


@pytest.mark.parametrize(
    "value",
    [[1.0, 2, np.float32(3)], (1.0, 2.0, 3.0), np.array([1, 2, 3], dtype=np.int16)],
    ids=["list", "tuple", "int16"],
)
def test_validate_makes_a_new_float64_array(value: object) -> None:
    values, _ = validate(toys.CUMULATIVE, {"rain_mm": value})
    array = values.array("rain_mm")
    assert array.dtype == np.float64
    assert array.tolist() == [1.0, 2.0, 3.0]


def test_a_checked_array_is_a_copy() -> None:
    given_array = np.array([1.0, 2.0])
    values, _ = validate(toys.CUMULATIVE, {"rain_mm": given_array})
    values.array("rain_mm")[0] = 9.0
    assert given_array[0] == 1.0


@pytest.mark.parametrize(
    ("value", "reason"),
    [
        (np.ma.masked_array([1.0, 2.0]), "invalid_type"),
        (np.array([True, False]), "invalid_type"),
        (np.array([1.0, 2.0], dtype=object), "invalid_type"),
        (np.array([1 + 0j]), "invalid_type"),
        ([1.0, None], "invalid_type"),
        ([1.0, True], "invalid_type"),
        ([1.0, np.timedelta64(1, "s")], "invalid_type"),
        (np.array([1, 2], dtype="timedelta64[s]"), "invalid_type"),
        ([[1.0], [2.0, 3.0]], "invalid_shape"),
        (np.ones((2, 2)), "invalid_shape"),
        (np.ones(0), "invalid_shape"),
        (np.ones(1001), "invalid_shape"),
        (3.0, "invalid_type"),
        ([1.0, math.inf], "outside_physical_range"),
        ([1.0, -2.0], "outside_physical_range"),
        ([10**400], "outside_physical_range"),
    ],
)
def test_validate_refuses_a_wrong_array(value: object, reason: str) -> None:
    assert _refusal(toys.CUMULATIVE, {"rain_mm": value})["reason"] == reason


def test_an_array_names_the_first_element_outside() -> None:
    details = _refusal(toys.CUMULATIVE, {"rain_mm": [1.0, 2500.0, -2.0, -1.0]})
    assert (details["index"], details["value"]) == ([2], -2.0)


def test_gaps_pass_only_where_the_spec_allows_them() -> None:
    values, _ = validate(toys.CUMULATIVE, {"rain_mm": [1.0, math.nan]})
    assert math.isnan(values.array("rain_mm")[1])
    no_gaps = replace(
        toys.CUMULATIVE,
        variables=(replace(toys.CUMULATIVE.variables[0], gaps_allowed=False),),
        outputs=(
            replace(toys.CUMULATIVE.outputs[0], gaps_allowed=False, gaps_from=None),
        ),
    )
    details = _refusal(no_gaps, {"rain_mm": [1.0, math.nan]})
    assert (details["reason"], details["index"]) == ("outside_physical_range", [1])


def test_an_array_outside_its_applicability_gives_one_notice_with_a_count() -> None:
    spec = replace(
        toys.CUMULATIVE,
        variables=(
            replace(
                toys.CUMULATIVE.variables[0],
                applicability=Range(low=0.0, high=100.0, source=SRC),
            ),
        ),
    )
    _, notices = validate(spec, {"rain_mm": [1.0, 150.0, math.nan, 120.0]})
    assert len(notices) == 1
    assert notices[0].details["count"] == 2
    assert notices[0].details["index"] == [1]


def test_integers_and_choices_keep_their_kinds() -> None:
    values, _ = validate(
        toys.POSITION, {"rank": np.int64(2), "count": 3, "method": np.str_("weibull")}
    )
    assert type(values["rank"]) is int
    assert type(values["method"]) is str
    assert (values.integer("rank"), values.choice("method")) == (2, "weibull")
    with pytest.raises(TypeError):
        values.real("rank")
    with pytest.raises(TypeError):
        values.array("rank")
    with pytest.raises(TypeError):
        values.integer("method")
    with pytest.raises(TypeError):
        values.choice("rank")


@pytest.mark.parametrize(
    ("inputs", "reason"),
    [
        ({"rank": 2.0}, "invalid_type"),
        ({"rank": True}, "invalid_type"),
        ({"rank": 0}, "outside_physical_range"),
        ({"rank": 10**400}, "outside_physical_range"),
        ({"rank": np.timedelta64(5, "ns")}, "invalid_type"),
        ({"method": b"weibull"}, "invalid_type"),
        ({"method": "hazen"}, "invalid_choice"),
    ],
)
def test_integers_and_choices_refuse_other_values(
    inputs: dict[str, object], reason: str
) -> None:
    point = {"rank": 2, "count": 3, "method": "weibull"} | inputs
    assert _refusal(toys.POSITION, point)["reason"] == reason


# --- check_outputs (CMP-3.4) ----------------------------------------------------------


def _calc_reason(spec: FormulaSpec, outputs: Mapping[str, object], **kw: Any) -> object:
    with pytest.raises(toys.ToyCalculationError) as caught:
        check_outputs(spec, outputs, errors=toys.ERRORS, **kw)
    return caught.value.details["reason"]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (5.0, 5.0),
        (np.float32(2.5), 2.5),
        (-1e-323, 0.0),
        (math.nextafter(1000.0, 2000.0), 1000.0),
    ],
)
def test_check_outputs_keeps_or_snaps_a_value_within_four_ulp(
    value: object, expected: float
) -> None:
    assert check_outputs(ONE, {"z_m": value}).real("z_m") == expected


@pytest.mark.parametrize(
    ("value", "reason"),
    [
        (math.nan, "non_finite_output"),
        (math.inf, "non_finite_output"),
        (-1e-300, "output_outside_physical_range"),
        (1000.0 + 1e-9, "output_outside_physical_range"),
    ],
)
def test_check_outputs_raises_a_calculation_error(value: float, reason: str) -> None:
    assert _calc_reason(ONE, {"z_m": value}) == reason


def test_check_outputs_uses_a_stated_tolerance_and_excluded_ends() -> None:
    tolerant = replace(ONE, outputs=(replace(Z, boundary_tolerance=1e-12),))
    assert check_outputs(tolerant, {"z_m": -1e-17}).real("z_m") == 0.0
    with pytest.raises(FormulaCalculationError) as caught:
        check_outputs(tolerant, {"z_m": -1e-11})
    assert isinstance(caught.value, ArithmeticError)
    assert caught.value.code == "calculation_error"
    excluded = replace(
        ONE, outputs=(replace(Z, physical=Range(low=0.0, low_inclusive=False)),)
    )
    assert check_outputs(excluded, {"z_m": 0.0}).real("z_m") == 5e-324


def test_check_outputs_allows_a_gap_only_where_the_input_had_one() -> None:
    rain = np.array([1.0, math.nan, 2.0])
    checked = check_outputs(
        toys.CUMULATIVE, {"depth_mm": [1.0, math.nan, 3.0]}, inputs={"rain_mm": rain}
    )
    assert np.isnan(checked.array("depth_mm")[1])
    spread = {"depth_mm": np.array([1.0, math.nan, math.nan])}
    reason = _calc_reason(toys.CUMULATIVE, spread, inputs={"rain_mm": rain})
    assert reason == "non_finite_output"
    infinite = {"depth_mm": np.array([1.0, math.nan, math.inf])}
    assert _calc_reason(toys.CUMULATIVE, infinite, inputs={"rain_mm": rain}) == (
        "non_finite_output"
    )


def test_check_outputs_snaps_array_elements_near_a_bound() -> None:
    inputs = {"rain_mm": np.zeros(3)}
    checked = check_outputs(
        toys.CUMULATIVE, {"depth_mm": [-1e-323, 0.0, 1.0]}, inputs=inputs
    )
    assert checked.array("depth_mm").tolist() == [0.0, 0.0, 1.0]
    reason = _calc_reason(
        toys.CUMULATIVE, {"depth_mm": [0.0, -0.5, 1.0]}, inputs=inputs
    )
    assert reason == "output_outside_physical_range"


def test_check_outputs_of_integers_and_choices() -> None:
    counted = replace(
        ONE,
        outputs=(Output(name="n", unit="-", kind="integer", physical=Range(low=0.0)),),
    )
    assert check_outputs(counted, {"n": np.int64(4)}).integer("n") == 4
    assert _calc_reason(counted, {"n": -1}) == "output_outside_physical_range"
    classed = replace(
        ONE, outputs=(Output(name="c", unit="-", kind="choice", choices=("A", "B")),)
    )
    assert check_outputs(classed, {"c": "B"}).choice("c") == "B"
    assert _calc_reason(classed, {"c": "D"}) == "output_outside_physical_range"
    with pytest.raises(TypeError):
        check_outputs(counted, {"n": 1.5})
    with pytest.raises(TypeError):
        check_outputs(classed, {"c": 1})


def test_check_outputs_refuses_a_defect_of_the_formula_module() -> None:
    with pytest.raises(TypeError, match="missing"):
        check_outputs(ONE, {"w": 1.0})
    with pytest.raises(TypeError):
        check_outputs(ONE, {"z_m": "5"})
    with pytest.raises(TypeError, match="needs the inputs"):
        check_outputs(toys.CUMULATIVE, {"depth_mm": [1.0]})
    with pytest.raises(TypeError, match="shape"):
        check_outputs(
            toys.CUMULATIVE, {"depth_mm": [1.0]}, inputs={"rain_mm": [1.0, 2.0]}
        )
    with pytest.raises(TypeError):
        check_outputs(toys.CUMULATIVE, {"depth_mm": 1.0}, inputs={"rain_mm": [1.0]})


# --- units (CMP-4.3) ---------------------------------------------------------


def test_the_units_table_holds_the_exact_constants_it_cites() -> None:
    foot = Fraction("0.3048")
    expected = {
        "m2": (Fraction(1), 0),
        "km2": (Fraction(10**6), 0),
        "ha": (Fraction(10**4), 0),
        "acre": (Fraction("4046.8564224"), 0),
        "m": (Fraction(1), 0),
        "mm": (Fraction("0.001"), 0),
        "cm": (Fraction("0.01"), 0),
        "km": (Fraction(1000), 0),
        "in": (Fraction("0.0254"), 0),
        "ft": (foot, 0),
        "mi": (Fraction("1609.344"), 0),
        "m3_per_s": (Fraction(1), 0),
        "l_per_s": (Fraction("0.001"), 0),
        "ft3_per_s": (Fraction("0.028316846592"), 0),
        "s": (Fraction(1), 0),
        "min": (Fraction(60), 0),
        "h": (Fraction(3600), 0),
        "d": (Fraction(86400), 0),
        "K": (Fraction(1), 0),
        "degC": (Fraction(1), Fraction("273.15")),
        "degF": (Fraction(5, 9), Fraction("459.67") * Fraction(5, 9)),
    }
    assert {name: (u.factor, u.offset) for name, u in UNITS.items()} == expected
    assert all(u.source.citation and u.source.locator for u in UNITS.values())


@pytest.mark.parametrize(
    ("value", "units", "expected"),
    [
        (32.0, ("degF", "degC"), 0.0),
        (212.0, ("degF", "degC"), 100.0),
        (-40.0, ("degF", "degC"), -40.0),
        (0.0, ("degC", "K"), 273.15),
        (1.0, ("in", "mm"), 25.4),
        (1.0, ("mi", "km"), 1.609344),
        (1.0, ("acre", "m2"), 4046.8564224),
        (1.0, ("ft3_per_s", "m3_per_s"), 0.028316846592),
        (2.0, ("d", "h"), 48.0),
        (90.0, ("min", "h"), 1.5),
        (250.0, ("ha", "km2"), 2.5),
    ],
)
def test_convert_gives_the_published_values(
    value: float, units: tuple[str, str], expected: float
) -> None:
    assert convert(value, *units) == expected


def _samples() -> list[float]:
    generator = random.Random(20261118)
    values = [0.0, -0.0, 5e-324, 1e-300, 0.1, 1.0, 3.0, 12345.678, 1e15, 1e300]
    values += [generator.uniform(-1e4, 1e4) for _ in range(40)]
    return values + [10 ** generator.uniform(-30, 30) for _ in range(40)]


PAIRS = [
    (a, b)
    for a in UNITS
    for b in UNITS
    if a != b and UNITS[a].quantity == UNITS[b].quantity
]


@pytest.mark.parametrize(("source", "target"), PAIRS, ids=lambda u: str(u))
def test_convert_is_the_exact_conversion_correctly_rounded(
    source: str, target: str
) -> None:
    a, b = UNITS[source], UNITS[target]
    for value in _samples():
        exact = (Fraction(value) * a.factor + a.offset - b.offset) / b.factor
        try:
            expected = float(exact)
        except OverflowError:
            expected = math.copysign(math.inf, exact)
        assert convert(value, source, target) == expected, value
        back = convert(convert(value, source, target), target, source)
        if math.isfinite(back):
            converted = convert(value, source, target)
            affine = a.offset != b.offset
            allowed = math.ulp(value) + (math.ulp(converted) if affine else 0.0)
            assert abs(back - value) <= allowed, value


def test_convert_of_an_array_is_the_conversion_of_each_value() -> None:
    values = np.array(_samples())
    for source, target in PAIRS:
        converted = convert(values, source, target)
        assert converted.tolist() == [convert(float(v), source, target) for v in values]
    assert convert(np.array([math.nan, math.inf]), "degF", "degC")[1] == math.inf


def test_convert_refuses_units_of_different_quantities() -> None:
    with pytest.raises(ValueError, match="measures"):
        convert(1.0, "km", "h")
    with pytest.raises(KeyError):
        convert(1.0, "km", "league")


def test_convert_overflows_to_infinity_without_a_warning() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert convert(np.array([1e308]), "km", "m").tolist() == [math.inf]
        assert convert(np.array([1e308]), "mi", "mm").tolist() == [math.inf]
        assert convert(1e308, "km", "m") == math.inf


# --- generated cases (CMP-6.5) -----------------------------------------------


def _cases(params: list[Any]) -> list[Case]:
    return [cast(Case, param.values[0]) for param in params]


def test_range_cases_are_the_points_of_the_standard() -> None:
    nudge_low, nudge_high = math.nextafter(1.0, 0.0), math.nextafter(5.0, 9.0)
    expected = [
        ("x_m-typical_low", 2.0, "ok", None),
        ("x_m-typical_middle", 3.0, "ok", None),
        ("x_m-typical_high", 4.0, "ok", None),
        ("x_m-applicability_low", 1.0, "ok", None),
        ("x_m-applicability_low_beyond", nudge_low, "ok+notice", None),
        ("x_m-applicability_low_beyond_1pct", 0.99, "ok+notice", None),
        ("x_m-applicability_high", 5.0, "ok", None),
        ("x_m-applicability_high_beyond", nudge_high, "ok+notice", None),
        ("x_m-applicability_high_beyond_1pct", 5.05, "ok+notice", None),
        ("x_m-physical_low", 0.0, "validation_error", "outside_physical_range"),
        ("x_m-physical_low_inside", 5e-324, "ok+notice", None),
        (
            "x_m-physical_low_beyond",
            -5e-324,
            "validation_error",
            "outside_physical_range",
        ),
        (
            "x_m-physical_low_beyond_1pct",
            -0.02,
            "validation_error",
            "outside_physical_range",
        ),
        ("x_m-physical_high", 10.0, "ok+notice", None),
        (
            "x_m-physical_high_beyond",
            math.nextafter(10.0, 11.0),
            "validation_error",
            "outside_physical_range",
        ),
        (
            "x_m-physical_high_beyond_1pct",
            10.1,
            "validation_error",
            "outside_physical_range",
        ),
    ]
    got = [
        (c.id, c.inputs["x_m"], c.expect, c.reason) for c in _cases(range_cases(ONE))
    ]
    assert got == expected
    assert all(
        c.notices == (("x_m",) if c.expect == "ok+notice" else ())
        for c in _cases(range_cases(ONE))
    )


def test_range_cases_of_integers_choices_and_constraints() -> None:
    cases = {c.id: c for c in _cases(range_cases(toys.POSITION))}
    assert [
        cases[f"count-{k}"].inputs["count"]
        for k in ("physical_low", "physical_low_beyond")
    ] == [1, 0]
    assert cases["count-physical_high_test_bound"].inputs["count"] == 10_000
    assert cases["rank-typical_high"].reason == "outside_physical_range"
    assert cases["method-choice_unknown"].reason == "invalid_choice"
    assert cases["rank_within_count-boundary"].expect == "ok"
    assert cases["rank_within_count-violated"].reason == "outside_physical_range"
    arrays = {c.id: c for c in _cases(range_cases(toys.CUMULATIVE))}
    rain = cast(
        np.ndarray, arrays["rain_mm-physical_high_test_bound"].inputs["rain_mm"]
    )
    assert rain[0] == 2000.0 and len(rain) == 10


def test_a_constraint_that_contradicts_its_points_is_a_spec_error() -> None:
    wrong = Constraint(
        name="positive_slope",
        cls="precondition",
        check=lambda x: x.real("slope_m_per_m") > 0.01,
        text="S > 0",
        source=SRC,
        satisfied={"slope_m_per_m": 0.05},
        boundary={"slope_m_per_m": 5e-324},
        violated={"slope_m_per_m": 0.0},
    )
    with pytest.raises(SpecError, match="boundary point"):
        range_cases(replace(toys.KIRPICH, constraints=(wrong,)))
    refused = replace(wrong, check=lambda x: True, satisfied={"slope_m_per_m": -1.0})
    with pytest.raises(SpecError, match="refused"):
        range_cases(replace(toys.KIRPICH, constraints=(refused,)))


def test_type_cases_pass_every_kind_of_value() -> None:
    cases = {c.id: c for c in _cases(type_cases(toys.KIRPICH))}
    refused = {k: c.reason for k, c in cases.items() if k.startswith("length_km-")}
    assert refused == {
        "length_km-float": None,
        "length_km-numpy_float64": None,
        "length_km-numpy_float32": None,
        "length_km-int": None,
        "length_km-numpy_int64": None,
        "length_km-numpy_int32": None,
        "length_km-bool_true": "invalid_type",
        "length_km-bool_false": "invalid_type",
        "length_km-numpy_bool": "invalid_type",
        "length_km-none": "invalid_type",
        "length_km-str": "invalid_type",
        "length_km-decimal": "invalid_type",
        "length_km-complex": "invalid_type",
        "length_km-numpy_complex": "invalid_type",
        "length_km-numpy_timedelta": "invalid_type",
        "length_km-nan": "outside_physical_range",
        "length_km-inf": "outside_physical_range",
        "length_km-minus_inf": "outside_physical_range",
    }
    arrays = {c.id: (c.expect, c.reason) for c in _cases(type_cases(toys.CUMULATIVE))}
    assert arrays["rain_mm-nan_element"] == ("ok", None)
    assert arrays["rain_mm-too_long"] == ("validation_error", "invalid_shape")
    assert arrays["rain_mm-empty"] == ("validation_error", "invalid_shape")
    assert arrays["rain_mm-list_with_bool"] == ("validation_error", "invalid_type")
    assert "rain_mm-too_short" not in arrays
    others = {c.id: c.reason for c in _cases(type_cases(toys.POSITION))}
    assert others["rank-float"] == others["method-bytes"] == "invalid_type"
    assert others["method-numpy_str"] is None


def test_type_cases_of_huge_values_leave_out_numpy_integers() -> None:
    huge = replace(
        X,
        physical=Range(low=0.0, high=1e308),
        applicability="unstated",
        typical=Range(low=1e300, high=1e308, source=SRC),
    )
    ids = {c.id for c in _cases(type_cases(replace(ONE, variables=(huge,))))}
    assert "x_m-int" in ids
    assert "x_m-numpy_int64" not in ids


def test_run_case_passes_a_correct_formula() -> None:
    for case in _cases(range_cases(ONE) + type_cases(ONE)):
        run_case(ONE, one, case, toys.ERRORS)


def _case(expect: Any = "ok", reason: str | None = None, *notices: str) -> Case:
    return Case("c", {"x_m": 2.0}, expect, reason, notices)


TWO = replace(ONE, outputs=(Z, replace(Z, name="w")))
COUNT = replace(
    ONE, outputs=(Output(name="n", unit="-", kind="integer", physical=Range(low=0.0)),)
)
CLASS = replace(
    ONE, outputs=(Output(name="c", unit="-", kind="choice", choices=("A",)),)
)
SERIES = replace(
    ONE,
    outputs=(Output(name="w", unit="m", kind="real_array", physical=Range(low=0.0)),),
)


@pytest.mark.parametrize(
    ("spec", "function", "case", "message"),
    [
        (ONE, lambda x_m: {"z_m": 1.0}, _case("validation_error", "x"), "returned"),
        (ONE, lambda x_m: float("x"), _case(), "ValueError.*expected a result"),
        (
            ONE,
            lambda x_m: validate(ONE, {"x_m": "a"}),
            _case("validation_error", "invalid_type"),
            "expected the project's ToyValidationError",
        ),
        (
            ONE,
            lambda x_m: validate(ONE, {"x_m": "a"}, errors=toys.ERRORS),
            _case("validation_error", "outside_physical_range"),
            "reason 'invalid_type'",
        ),
        (
            ONE,
            lambda x_m: check_outputs(ONE, {"z_m": -1.0}, errors=toys.ERRORS),
            _case(),
            "calculation_error for accepted inputs",
        ),
        (ONE, lambda x_m: {"z_m": math.nan}, _case(), "not finite or outside"),
        (ONE, lambda x_m: {"z_m": "1"}, _case(), "not a real number"),
        (ONE, lambda x_m: {"z_m": 1.0}, _case("ok+notice", None, "x_m"), "notices"),
        (ONE, lambda x_m: {"w": 1.0}, _case(), "no output"),
        (TWO, lambda x_m: object(), _case(), "no outputs"),
        (COUNT, lambda x_m: {"n": -1}, _case(), "outside its physical range"),
        (COUNT, lambda x_m: {"n": 1.5}, _case(), "not an integer"),
        (CLASS, lambda x_m: {"c": "B"}, _case(), "not one of"),
        (SERIES, lambda x_m: {"w": [1.0, math.nan]}, _case(), "non-finite value"),
        (SERIES, lambda x_m: {"w": [1.0, -1.0]}, _case(), r"lies outside \[0.0, inf\)"),
        (SERIES, lambda x_m: {"w": 1.0}, _case(), "not an array"),
        (SERIES, lambda x_m: {"w": ["a"]}, _case(), "not an array of numbers"),
        (
            toys.CUMULATIVE,
            lambda rain_mm: {"depth_mm": [1.0]},
            Case("c", {"rain_mm": [1.0, 2.0]}, "ok"),
            "has shape",
        ),
    ],
)
def test_run_case_names_what_differs(
    spec: FormulaSpec, function: Callable[..., object], case: Case, message: str
) -> None:
    with pytest.raises(AssertionError, match=message):
        run_case(spec, function, case, toys.ERRORS)


@dataclass
class _Result:
    z_m: float


class _HydrologStyle(UserWarning):
    level = "warning"

    def __init__(self, details: dict[str, object]) -> None:
        super().__init__("outside")
        self.details = details

    def code(self) -> str:
        return "outside_applicability"


@pytest.mark.parametrize(
    "result",
    [
        lambda: {
            "z_m": 6.0,
            "notices": [
                {"code": "outside_applicability", "details": {"variable": "x_m"}}
            ],
        },
        lambda: 6.0,
        lambda: _Result(6.0),
    ],
    ids=["mapping", "value", "attribute"],
)
def test_run_case_reads_outputs_and_notices_of_many_shapes(
    result: Callable[[], object],
) -> None:
    def function(x_m: float) -> object:
        made = result()
        if not isinstance(made, dict):
            warnings.warn(_HydrologStyle({"variable": "x_m"}), stacklevel=2)
        return made

    run_case(ONE, function, Case("c", {"x_m": 6.0}, "ok+notice", None, ("x_m",)))
    run_case(TWO, lambda x_m: (2.0, 3.0), Case("c", {"x_m": 2.0}, "ok"))


def test_run_case_wants_the_notice_of_an_unreferenced_formula() -> None:
    case = _cases(range_cases(toys.POSITION))[0]
    with pytest.raises(AssertionError, match="unreferenced_formula"):
        run_case(
            toys.POSITION,
            lambda rank, count, method: {"probability": 0.5},
            case,
            toys.ERRORS,
        )


# --- Hypothesis (CMP-6.5, CMP-6.9) -------------------------------------------


def test_register_profiles_registers_the_three_profiles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HYPOTHESIS_PROFILE", "nightly")
    try:
        assert register_profiles() == "nightly"
        assert settings.get_current_profile_name() == "nightly"
        gate = settings.get_profile("gate")
        assert (gate.max_examples, gate.derandomize, gate.database, gate.deadline) == (
            50,
            True,
            None,
            None,
        )
        ci = settings.get_profile("ci")
        assert ci.max_examples == 1000
        assert isinstance(ci.database, DirectoryBasedExampleDatabase)
        assert settings.get_profile("nightly").max_examples == 20_000
    finally:
        monkeypatch.delenv("HYPOTHESIS_PROFILE")
        assert register_profiles() == "gate"


@given(inputs=strategies(toys.KIRPICH))
def test_strategies_draw_finite_values_of_the_physical_ranges(
    inputs: dict[str, object],
) -> None:
    for variable in toys.KIRPICH.variables:
        value = inputs[variable.name]
        physical = variable.physical
        assert isinstance(value, float) and physical is not None
        assert physical.contains(value)
        assert physical.lower <= value <= physical.upper


@given(inputs=strategies(toys.CUMULATIVE))
def test_strategies_draw_arrays_of_the_declared_lengths(
    inputs: dict[str, object],
) -> None:
    rain = inputs["rain_mm"]
    assert isinstance(rain, np.ndarray) and rain.dtype == np.float64
    assert 1 <= len(rain) <= 51
    assert np.isfinite(rain).all() and (rain >= 0).all() and (rain <= 2000).all()


@given(inputs=strategies(toys.POSITION))
def test_strategies_draw_integers_and_choices(inputs: dict[str, object]) -> None:
    assert isinstance(inputs["rank"], int) and 1 <= inputs["rank"] <= 10_000
    assert inputs["method"] in ("weibull", "gringorten")


def test_assert_limits_runs_both_kinds_of_limit() -> None:
    def far(run: Callable[..., Values]) -> None:
        assert_within(run(x_m=9.0).real("z_m"), 9.0, abs=0.0, reason="an echo")

    spec = replace(
        ONE,
        properties=Properties(
            units="unit_specific",
            limits=(
                Limit(
                    name="echo",
                    text="z = x",
                    inputs={"x_m": 4.0},
                    expected={"z_m": 4.0},
                    tolerance=Tolerance(abs=0.0, reason="an echo"),
                ),
                Limit(name="far", text="z = x far away", check=far),
            ),
        ),
    )
    assert_limits(spec, one, toys.ERRORS)
    refused = Limit(
        name="refused",
        text="below the physical range",
        inputs={"x_m": -1.0},
        expected={"z_m": 0.0},
        tolerance=Tolerance(abs=0.0, reason="r"),
    )
    with pytest.raises(AssertionError, match="limit refused is refused"):
        assert_limits(
            replace(spec, properties=replace(spec.properties, limits=(refused,))),
            one,
            toys.ERRORS,
        )
    wrong = replace(
        spec.properties.limits[0],
        expected={"z_m": 5.0},
        tolerance=Tolerance(abs=0.5, reason="r"),
    )
    with pytest.raises(AssertionError, match="limit echo: r"):
        assert_limits(
            replace(spec, properties=replace(spec.properties, limits=(wrong,))),
            one,
            toys.ERRORS,
        )


# --- assert_within (CMP-6.8) -------------------------------------------------


def test_assert_within_holds_within_abs_plus_rel() -> None:
    assert_within(10.3, 10.0, abs=0.2, rel=0.02, reason="sum of both")
    assert_within(
        [1.0, math.nan, math.inf], [1.0, math.nan, math.inf], abs=0.0, reason="r"
    )
    with pytest.raises(
        AssertionError, match=r"10.5 differs from 10.0 by 0.5, more than 0.4"
    ):
        assert_within(10.5, 10.0, abs=0.2, rel=0.02, reason="sum of both")
    with pytest.raises(AssertionError, match=r"at \[1\].*1 of 3 beyond\): because"):
        assert_within([1.0, 2.0, 3.0], [1.0, 2.5, 3.0], abs=0.1, reason="because")
    with pytest.raises(AssertionError, match="shape"):
        assert_within([1.0], [1.0, 2.0], abs=1.0, reason="r")
    with pytest.raises(AssertionError):
        assert_within(math.nan, 1.0, abs=1.0, reason="r")
    for actual in (5.0, -math.inf):
        with pytest.raises(AssertionError):
            assert_within(actual, math.inf, rel=1e-9, reason="r")
    assert_within([1.0, math.inf], [1.0, math.inf], rel=1e-9, reason="r")


@pytest.mark.parametrize(
    ("abs_", "rel", "reason"),
    [(None, None, "why"), (0.1, None, ""), (-1.0, None, "why")],
)
def test_assert_within_needs_a_tolerance_and_its_reason(
    abs_: float | None, rel: float | None, reason: str
) -> None:
    with pytest.raises(ValueError):
        assert_within(1.0, 1.0, abs=abs_, rel=rel, reason=reason)


# --- reference cases (CMP-6.1) -----------------------------------------------

CASE = {
    "formula": "one",
    "case_id": "c1",
    "source": {
        "citation": "Book",
        "locator": "p. 3",
        "url": "https://example.org",
        "access": "open",
    },
    "inputs": {"x_m": 2.5},
    "expected": {"z_m": 2.5},
    "printed_precision": {"x_m": 0.1, "z_m": 0.1},
    "intermediate_rounding": [{"step": "x rounded", "effect": {"z_m": 0.01}}],
    "tolerance": {"abs": 0.001, "reason": "the source's g"},
    "conventions": ["SI"],
    "second_source": {"citation": "Paper", "access": "author-provided"},
    "status": "second_source",
}


def _write_cases(tmp_path: Path, cases: list[dict[str, Any]]) -> Path:
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(cases), encoding="utf-8")
    return path


def test_load_cases_reads_the_cases_of_a_formula(tmp_path: Path) -> None:
    other = CASE | {"formula": "two"}
    [case] = load_cases(_write_cases(tmp_path, [CASE, other]), "one")
    assert case.source.text() == "Book, p. 3"
    assert (
        case.second_source is not None
        and case.second_source.access == "author-provided"
    )
    assert case.intermediate_rounding[0].effect == {"z_m": 0.01}
    assert case.tolerance == Tolerance(abs=0.001, reason="the source's g")
    assert case.conventions == ("SI",)


@pytest.mark.parametrize(
    "change",
    [
        {"status": "fine"},
        {"status": "discrepancy"},
        {"status": "second_source", "second_source": None},
        {"extra": 1},
        {"source": {"citation": ""}},
        {"source": {"citation": "a", "access": "closed"}},
        {"source": "Book"},
        {"tolerance": {"abs": 0.1}},
        {"tolerance": {"abs": 0.1, "reason": "r", "x": 1}},
        {"printed_precision": {"x_m": -1}},
        {"intermediate_rounding": [{"step": "s"}]},
        {"intermediate_rounding": {}},
        {"conventions": "SI"},
        {"inputs": [1.0]},
    ],
)
def test_load_cases_refuses_a_malformed_case(
    tmp_path: Path, change: dict[str, Any]
) -> None:
    with pytest.raises(ValueError):
        load_cases(_write_cases(tmp_path, [CASE | change]), "one")


def test_load_cases_refuses_a_malformed_file(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="repeat"):
        load_cases(_write_cases(tmp_path, [CASE, CASE]), "one")
    with pytest.raises(ValueError, match="array"):
        load_cases(_write_cases(tmp_path, cast(Any, {"a": 1})), "one")
    (tmp_path / "bad.json").write_text("[", encoding="utf-8")
    with pytest.raises(ValueError, match="not JSON"):
        load_cases(tmp_path / "bad.json", "one")
    without = {k: v for k, v in CASE.items() if k != "expected"}
    with pytest.raises(ValueError, match="missing"):
        load_cases(_write_cases(tmp_path, [without]), "one")


LINEAR = FormulaSpec(
    name="linear",
    title="A linear test formula",
    function="test_nogat_formulas.linear",
    family="empirical",
    equation="z = 3 x - 2 y",
    latex="z = 3x - 2y",
    variables=(X, Y),
    outputs=(Z,),
    sources=(SRC,),
    properties=Properties(units="unit_specific"),
    no_traps_reason="linear",
    validation="none",
    formula_version=1,
    status="unreferenced",
)


def linear(x_m: float, y_m: float) -> float:
    """A linear test formula, spec ``linear``."""
    if not 0 < x_m <= 10:
        raise FormulaValidationError("x", {"reason": "outside_physical_range"})
    return 3 * x_m - 2 * y_m + 100


def test_rounding_tolerance_takes_the_worst_corner() -> None:
    printed = {"x_m": 0.1, "y_m": 0.2}
    effect = rounding_tolerance(LINEAR, linear, {"x_m": 2.0, "y_m": 1.0}, printed)
    assert_within(effect["z_m"], 3 * 0.05 + 2 * 0.1, rel=1e-12, reason="rounding")
    edge = rounding_tolerance(LINEAR, linear, {"x_m": 10.0, "y_m": 1.0}, {"x_m": 0.2})
    assert_within(edge["z_m"], 0.3, rel=1e-12, reason="the refused corner is skipped")
    names = [f"v{i}" for i in range(17)]
    spec = replace(LINEAR, variables=tuple(replace(Y, name=n) for n in names))
    with pytest.raises(ValueError, match="corners"):
        rounding_tolerance(
            spec, lambda **kw: 1.0, dict.fromkeys(names, 1.0), dict.fromkeys(names, 0.1)
        )


def test_rounding_tolerance_lets_other_errors_through() -> None:
    def broken(x_m: float, y_m: float) -> float:
        if x_m != 2.0:
            raise ZeroDivisionError
        return 1.0

    with pytest.raises(ZeroDivisionError):
        rounding_tolerance(LINEAR, broken, {"x_m": 2.0, "y_m": 1.0}, {"x_m": 0.1})


def test_case_tolerance_adds_the_parts_of_cmp_6_1() -> None:
    case = ReferenceCase(
        formula="linear",
        case_id="c",
        source=SRC,
        inputs={"x_m": 2.0, "y_m": 1.0},
        expected={"z_m": 104.0},
        printed_precision={"x_m": 0.1, "z_m": 1.0},
        intermediate_rounding=(),
        tolerance=Tolerance(rel=0.01, reason="the source's constant"),
    )
    assert case_tolerance(LINEAR, linear, case)["z_m"] == pytest.approx(
        0.5 + 0.15 + 1.04, rel=1e-12
    )


def test_assert_case_skips_a_discrepancy() -> None:
    case = ReferenceCase(
        formula="one",
        case_id="d",
        source=SRC,
        inputs={"x_m": 2.0},
        expected={"z_m": 3.0},
        second_source=SRC,
        status="discrepancy",
        discrepancy="both sources print 3",
    )
    with pytest.raises(Skipped, match="both sources print 3"):
        assert_case(ONE, one, case, toys.ERRORS)


def test_assert_case_of_a_choice_compares_exactly() -> None:
    spec = replace(
        ONE, outputs=(Output(name="c", unit="-", kind="choice", choices=("A", "B")),)
    )

    def classify(x_m: float) -> dict[str, object]:
        x, notices = validate(spec, {"x_m": x_m}, errors=toys.ERRORS)
        return {"c": "A" if x.real("x_m") < 3 else "B", "notices": notices}

    case = ReferenceCase(
        formula="one", case_id="k", source=SRC, inputs={"x_m": 2.0}, expected={"c": "B"}
    )
    with pytest.raises(AssertionError, match="'A', not 'B'"):
        assert_case(spec, classify, case, toys.ERRORS)
    assert_case(spec, classify, replace(case, expected={"c": "A"}), toys.ERRORS)


# --- frozen oracles (CMP-6.4) ------------------------------------------------

ORACLE = """# tool: R 4.4.1
# packages: lmom 3.0
# platform: x86_64-pc-linux-gnu
# date: 2026-11-18
# script: tests/oracles/lmom_gev.R
# note: seeded sample
case,x,expected
a,1.5,0.25
b,2.5,NA
"""


def test_read_frozen_oracle_reads_its_header_and_rows(tmp_path: Path) -> None:
    path = tmp_path / "oracle.csv"
    path.write_text(ORACLE, encoding="utf-8")
    oracle = read_frozen_oracle(path)
    assert oracle.metadata["packages"] == "lmom 3.0"
    assert oracle.metadata["note"] == "seeded sample"
    assert oracle.columns == ("case", "x", "expected")
    assert oracle.rows[0] == {"case": "a", "x": "1.5", "expected": "0.25"}
    assert oracle.floats("x").tolist() == [1.5, 2.5]
    assert math.isnan(oracle.floats("expected")[1])
    with pytest.raises(KeyError):
        oracle.floats("y")


@pytest.mark.parametrize(
    ("text", "message"),
    [
        (ORACLE.replace("# platform: x86_64-pc-linux-gnu\n", ""), "platform"),
        (ORACLE.replace("2026-11-18", "18.11.2026"), "ISO"),
        (ORACLE.split("case,")[0], "no rows"),
        (ORACLE + "c,1\n", "cells"),
        ("case,x\na,1\n", "missing"),
    ],
)
def test_read_frozen_oracle_refuses_a_file_without_its_metadata(
    tmp_path: Path, text: str, message: str
) -> None:
    path = tmp_path / "oracle.csv"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        read_frozen_oracle(path)


# --- generated documents and contract checks (CMP-2.6, CMP-2.7, CMP-6.8) -----


def test_card_states_the_spec_in_toml_ready_values() -> None:
    data = card(toys.KIRPICH)
    assert data["schema"] == CARD_FORMAT
    variables = cast(list[dict[str, Any]], data["variables"])
    assert variables[0]["physical"] == {
        "low": 0.0,
        "low_inclusive": False,
        "test_high": 1100.0,
        "test_reason": "longer than the Vistula, 1047 km",
    }
    position = card(toys.POSITION)
    assert (
        cast(list[dict[str, Any]], position["variables"])[0]["applicability"]
        == "unstated"
    )
    exact = replace(
        ONE, constants=(Constant(name="k", value=Fraction(1, 3), unit="-", source=SRC),)
    )
    constant = cast(list[dict[str, Any]], card(exact)["constants"])[0]
    assert (constant["value"], constant["exact"]) == (1 / 3, "1/3")


def test_to_toml_round_trips_through_tomllib() -> None:
    data: dict[str, object] = {
        "plain": 'a "quoted" \\ text\n\twith\x01 control',
        "spaced key": True,
        "number": -0.0,
        "big": 1e300,
        "small": 5e-324,
        "count": 3,
        "texts": ["a", "b"],
        "empty": [],
        "table": {"inner": {"deep": 1}, "rows": [{"a": 1, "sub": {"b": 2}}, {"a": 2}]},
        "rows": [{"x": [1.0, 2.0]}],
    }
    assert tomllib.loads(to_toml(data)) == data
    for spec in (toys.KIRPICH, toys.CUMULATIVE, toys.POSITION):
        assert tomllib.loads(to_toml(card(spec))) == card(spec)


@pytest.mark.parametrize(
    ("value", "error"), [(None, TypeError), (math.inf, ValueError)]
)
def test_to_toml_refuses_what_toml_cannot_hold(
    value: object, error: type[Exception]
) -> None:
    with pytest.raises(error):
        to_toml({"x": value})


def test_formulas_markdown_shows_every_part_of_a_formula() -> None:
    tier_b = TierBSpec(
        name="hydrological_year",
        function="obs.calendar.hydrological_year",
        definition="The year from 1 November to 31 October",
        convention="named by the year of its end",
        source=SRC,
        constants=(
            Constant(name="start_month", value=Fraction(11), unit="month", source=SRC),
        ),
    )
    delegated = Delegated(
        name="Area in EPSG:2180",
        library="pyproj",
        versions=">=3.6,<4",
        smoke_case="a 1 km square has 1 km2",
        test="tests/test_area.py::test_square",
    )
    text = formulas_markdown(
        [toys.KIRPICH, toys.POSITION],
        [tier_b],
        {"formula_toys": 0.875},
        delegated=[delegated],
    )
    assert text.startswith("# Formulas\n")
    assert '<a id="toy_kirpich"></a>' in text
    assert "$$\nt_c = c \\, (1000 L)^{a} S^{b}\n$$" in text
    assert (
        "| `length_km` | $L$ | km | real | (0.0, inf), test bound high 1100.0" in text
    )
    assert "[0.12, 1.22]: Toy source of the tests, no published value, eq. 1" in text
    assert "status **referenced**" in text and "mutation score 88%" in text
    assert "| `positive_slope` | precondition | S > 0 |" in text
    assert "`singular_at_bound`: range case slope_m_per_m-physical_low" in text
    assert "None applies: every denominator is at least 1.12" in text
    assert "reference cases (CMP-6.1)" in text
    assert "| `hydrological_year` | `obs.calendar.hydrological_year` |" in text
    assert "| Area in EPSG:2180 | pyproj | >=3.6,<4 |" in text
    assert "| `formula_toys` | 88% |" in text
    assert formulas_markdown([toys.KIRPICH]) == formulas_markdown([toys.KIRPICH])
    assert "not measured" in formulas_markdown([toys.CUMULATIVE])


def _mean_bounds(sample: np.ndarray, levels: tuple[float, ...]) -> list[Bounds]:
    mean = float(np.mean(sample))
    return [(mean - c, mean + c) for c in levels]


def _draw(generator: np.random.Generator, size: int) -> np.ndarray:
    return generator.normal(0.0, 1.0, size)


COVERAGE_ARGUMENTS: dict[str, Any] = {
    "setting": "standard normal",
    "size": 30,
    "confidence_level": (0.95, 0.68),
    "seed": 1,
    "reason": "a test of the arguments",
}


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"samples": 999}, "samples is an integer of at least 1000"),
        ({"size": True}, "size is an integer"),
        ({"seed": -1}, "seed is an integer of at least 0"),
        ({"reason": " "}, "needs its reason"),
        ({"setting": ""}, "needs its setting"),
        ({"confidence_level": 1.0}, r"in \(0, 1\), not 1\.0"),
        ({"confidence_level": (0.95, 0.95)}, "not distinct"),
        ({"confidence_level": ()}, "not distinct"),
        ({"expected": {0.9: 0.9}}, "not a level asked"),
        ({"at_least": {0.95: 1.5}}, r"not a share in \[0, 1\]"),
        ({"expected": {0.95: [0.9, 0.9]}}, r"has the shape \(2,\), not \(\)"),
        (
            {"expected": {0.95: 0.95}, "at_least": {0.95: 0.9}},
            "both a coverage and a bound",
        ),
    ],
)
def test_assert_coverage_refuses_what_is_no_simulation(
    change: dict[str, Any], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        assert_coverage(
            toys.MEAN_INTERVAL,
            _mean_bounds,
            _draw,
            0.0,
            **{**COVERAGE_ARGUMENTS, **change},
        )


def test_assert_coverage_refuses_a_true_value_that_is_not_finite() -> None:
    with pytest.raises(ValueError, match="the true value is not finite"):
        assert_coverage(
            toys.MEAN_INTERVAL, _mean_bounds, _draw, math.nan, **COVERAGE_ARGUMENTS
        )


def test_assert_coverage_names_a_sample_or_bounds_of_the_wrong_shape() -> None:
    with pytest.raises(AssertionError, match=r"a sample of shape \(29,\), not 30"):
        assert_coverage(
            toys.MEAN_INTERVAL,
            _mean_bounds,
            lambda generator, size: _draw(generator, size - 1),
            0.0,
            **COVERAGE_ARGUMENTS,
        )
    with pytest.raises(AssertionError, match=r"bounds of shape \(\), not \(2,\)"):
        assert_coverage(
            toys.MEAN_INTERVAL, _mean_bounds, _draw, [0.0, 0.0], **COVERAGE_ARGUMENTS
        )
    with pytest.raises(AssertionError, match="1 pairs of bounds for the 2 levels"):
        assert_interval_properties(
            lambda sample, levels: _mean_bounds(sample, levels[:1]), [0.0], (0.9, 0.5)
        )


def test_a_coverage_record_round_trips_and_is_reported_under_its_formula() -> None:
    records = assert_coverage(
        toys.MEAN_INTERVAL,
        _mean_bounds,
        _draw,
        0.0,
        **COVERAGE_ARGUMENTS,
        at_least={0.95: 0.9, 0.68: 0.9},
    )
    kept = json.loads(json.dumps([asdict(record) for record in records]))
    assert [Coverage(**record) for record in kept] == records
    text = formulas_markdown([toys.KIRPICH, toys.MEAN_INTERVAL], coverage=records)
    kirpich, interval = text.split('<a id="toy_mean_interval"></a>')
    assert "CMP-6.11" not in kirpich
    assert "**Coverage of its intervals (CMP-6.11)**" in interval
    assert "- standard normal, n = 30, c = 0.95: coverage 1.000, asserted against " in (
        interval
    )
    assert "at least 0.900 within the Monte Carlo error; 1000 samples, seed 1, " in (
        interval
    )
    assert "; coverage (CMP-6.11)." in interval
    with pytest.raises(ValueError, match=r"coverage of \['toy_mean_interval'\]"):
        formulas_markdown([toys.KIRPICH], coverage=records)
    with pytest.raises(SpecError, match="one entry per element"):
        replace(records[0], undefined=())


def test_docstring_problems_find_digits_and_a_missing_name() -> None:
    assert docstring_problems(toys.KIRPICH, toys.toy_kirpich) == []
    problems = docstring_problems(toys.KIRPICH, toys.digits_in_docstring)
    assert len(problems) == 1 and "['0', '0195', '0', '77', '0', '385']" in problems[0]
    assert (
        "does not name its spec"
        in docstring_problems(toys.POSITION, toys.toy_kirpich)[0]
    )
    [problem] = docstring_problems(toys.KIRPICH, lambda: None)
    assert problem.endswith("<lambda>: no docstring (CMP-2.7)")


def test_tolerance_problems_find_comparisons_without_a_tolerance() -> None:
    source = """
import math, numpy as np, pytest
from math import isclose
from numpy.testing import assert_allclose
assert x == pytest.approx(1.0)
assert x == pytest.approx(1.0, rel=1e-3)
assert x == approx(1.0, 1e-3)
np.testing.assert_allclose(a, b)
assert_allclose(a, b, atol=1e-9)
assert_allclose(a, b, 1e-7)
assert np.isclose(a, b)
assert np.allclose(a, b, rtol=1e-3)
assert math.isclose(a, b)
assert isclose(a, b, rel_tol=1e-9)
"""
    lines = [p.split(":")[1] for p in tolerance_problems(source, "t.py")]
    assert lines == ["5", "8", "11", "13"]


def test_spec_problems_of_correct_specs_are_none(tmp_path: Path) -> None:
    _write_cases(tmp_path, [CASE])
    assert spec_problems(ONE, one, root=tmp_path) == []
    assert spec_problems(toys.POSITION, toys.toy_plotting_position) == []


def test_spec_problems_name_each_break(tmp_path: Path) -> None:
    table = tmp_path / "table.csv"
    table.write_text("a,b\n", encoding="utf-8")
    spec = replace(
        ONE,
        function="elsewhere.one",
        reference_cases=("cases.json", "missing.json"),
        tables=(
            Table(path="table.csv", sha256="0" * 64, source=SRC, comparison="c.txt"),
        ),
    )
    _write_cases(tmp_path, [CASE | {"formula": "two"}])

    def one_renamed(z: float) -> float:
        """Echo, spec ``one`` 2."""
        return z

    problems = spec_problems(spec, one_renamed, root=tmp_path)
    assert any("docstring line 1" in p for p in problems)
    assert any("the function is test_nogat_formulas" in p for p in problems)
    assert any("takes ['z']" in p for p in problems)
    assert any("cases.json has no case" in p for p in problems)
    assert any("missing.json" in p for p in problems)
    assert any("table table.csv has SHA-256" in p for p in problems)
    assert any("evidence gives 'unreferenced'" in p for p in problems)
    bare = replace(
        ONE, reference_cases=(), properties=Properties(units="unit_specific")
    )
    problems = spec_problems(bare)
    assert any("CMP-5.1 needs two" in p for p in problems)
    assert any("unit-specific formula needs reference cases" in p for p in problems)
    oracle = Oracle(kind="exact", description="d", test="t")
    assert spec_problems(replace(ONE, oracles=(oracle,), status="oracle only")) == [
        "one: status 'oracle only', its evidence gives 'referenced' (CMP-2.6)"
    ]
    absent = replace(ONE, tables=(replace(spec.tables[0], path="none.csv"),))
    _write_cases(tmp_path, [CASE])
    assert "No such file" in spec_problems(absent, root=tmp_path)[0]


def test_spec_problems_report_constraint_points() -> None:
    wrong = replace(toys.KIRPICH.constraints[0], boundary_holds=False)
    problems = spec_problems(replace(toys.KIRPICH, constraints=(wrong,)))
    assert any("boundary point" in p for p in problems)


def test_notice_as_dict_is_an_agi_notice() -> None:
    notice = Notice("info", "unreferenced_formula", "m", {"formula": "f"})
    assert notice.as_dict() == {
        "level": "info",
        "code": "unreferenced_formula",
        "message": "m",
        "details": {"formula": "f"},
    }
