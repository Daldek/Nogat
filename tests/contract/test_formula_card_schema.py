"""The card of a formula, `nogat-formula-card/1` (schemas/formula/card-1.schema.json).

Every project that computes writes `formulas/<name>.toml` with the reference
module's `card()` and copies the schema byte for byte (CMP-2.6, CMP-8.1); these
tests pin that every card the module makes is what the schema admits, through
TOML too, and that the schema refuses what a broken generator would write.
"""

from __future__ import annotations

import copy
import json
import tomllib
from collections.abc import Callable
from dataclasses import replace
from fractions import Fraction
from pathlib import Path
from typing import Any

import formula_toys as toys
import jsonschema
import pytest
from nogat_formulas import (
    CARD_FORMAT,
    Constant,
    FormulaSpec,
    Limit,
    Oracle,
    Output,
    Range,
    Source,
    Symmetry,
    Table,
    Tolerance,
    card,
    to_toml,
)

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schemas/formula/card-1.schema.json"
SCHEMA: dict[str, Any] = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
VALIDATOR = jsonschema.Draft202012Validator(SCHEMA)
URL = "https://example.org/source"

FULL = replace(
    toys.CUMULATIVE,
    name="toy_full",
    sources=(
        Source(citation="Book", locator="p. 1", url=URL, access="author-provided"),
    ),
    constants=(
        Constant(
            name="half", value=Fraction(1, 2), unit="-", source=toys.TOY, symbol="h"
        ),
        Constant(name="g", value=9.81, unit="m s^-2", source=toys.TOY),
    ),
    outputs=(
        *toys.CUMULATIVE.outputs,
        Output(
            name="wet_class",
            unit="-",
            kind="choice",
            choices=("dry", "wet"),
            description="Class by the total",
        ),
        Output(
            name="wet_days",
            unit="d",
            kind="integer",
            physical=Range(low=0.0),
            boundary_tolerance=0.0,
            symbol="n",
        ),
    ),
    properties=replace(
        toys.CUMULATIVE.properties,
        limits=(
            Limit(name="zero", text="no rain, no depth", check=lambda run: None),
            Limit(
                name="one",
                text="one value",
                inputs={"rain_mm": [2.0]},
                expected={"depth_mm": [2.0]},
                tolerance=Tolerance(abs=0.0, reason="exact"),
                source=toys.TOY,
            ),
        ),
        symmetries=(
            Symmetry(
                name="none",
                text="the identity",
                inputs=lambda x: x,
                outputs=lambda y: y,
                tolerance=Tolerance(rel=0.0, reason="the same call"),
            ),
        ),
    ),
    conventions=("hydrological day 06-06 UTC",),
    assumptions=("no snow",),
    notices=("short_record",),
    oracles=(
        Oracle(
            kind="frozen",
            description="R 4.4",
            test="tests/oracles/r.csv",
            conventions=("both: running sums",),
        ),
    ),
    tables=(Table(path="t.csv", sha256="a" * 64, source=toys.TOY, comparison="c.txt"),),
    traps={},
    no_traps_reason="a toy",
)
SPECS = [toys.KIRPICH, toys.CUMULATIVE, toys.POSITION, toys.NO_PRECONDITION, FULL]


def _errors(data: Any) -> list[str]:
    return [e.message for e in VALIDATOR.iter_errors(data)]


def test_the_schema_is_a_2020_12_schema_titled_by_the_format() -> None:
    jsonschema.Draft202012Validator.check_schema(SCHEMA)
    assert SCHEMA["title"] == CARD_FORMAT
    assert SCHEMA["$id"].endswith("/schemas/formula/card-1.schema.json")


@pytest.mark.parametrize("spec", SPECS, ids=[s.name for s in SPECS])
def test_every_card_of_the_module_is_valid_also_through_toml(spec: FormulaSpec) -> None:
    data = card(spec)
    assert _errors(data) == []
    assert tomllib.loads(to_toml(data)) == data


def test_a_card_shows_constants_exactly_and_conservation_laws() -> None:
    data = card(FULL)
    constants = data["constants"]
    assert isinstance(constants, list)
    assert constants[0] == {
        "name": "half",
        "value": 0.5,
        "unit": "-",
        "source": {"citation": toys.TOY.citation, "access": "open", "locator": "eq. 1"},
        "symbol": "h",
        "exact": "1/2",
    }
    properties = data["properties"]
    assert isinstance(properties, dict)
    assert properties["conservation"] == [
        {
            "name": "total",
            "text": "the last depth is the sum of the rainfall",
            "tolerance": {
                "reason": "pairwise and running sums of 1,051 values",
                "abs": 1e-6,
            },
        }
    ]
    assert data["notices"] == ["short_record"]


def _drop(key: str) -> Callable[[dict[str, Any]], None]:
    return lambda data: data.pop(key)


def _set(path: tuple[Any, ...], value: object) -> Callable[[dict[str, Any]], None]:
    def change(data: dict[str, Any]) -> None:
        target: Any = data
        for step in path[:-1]:
            target = target[step]
        target[path[-1]] = value

    return change


@pytest.mark.parametrize(
    "change",
    [
        _drop("status"),
        _set(("status",), "verified"),
        _set(("comment",), "x"),
        _set(("formula_version",), 0),
        _set(("family",), "magic"),
        _set(("variables", 0, "applicability"), "none"),
        _set(("variables", 0, "typical"), {"low": 0.5, "low_inclusive": True}),
        _set(("variables", 0, "physical"), {"low": 0.0, "low_inclusive": False}),
        _set(("variables", 0, "physical", "high"), 2.0),
        _set(("variables", 0, "gaps_allowed"), True),
        _set(("variables", 0, "kind"), "choice"),
        _set(("outputs", 0, "physical"), None),
        _set(("constraints", 0, "class"), "advice"),
        _set(("constants", 0, "exact"), "0.0195"),
        _set(("properties", "monotonic", "length_km"), 2),
        _set(("properties", "units"), "homogeneous"),
        _set(("traps",), []),
        _set(("traps", 0, "name"), "luck"),
        _set(("sources",), []),
        _set(("sources", 0, "access"), "closed"),
    ],
)
def test_the_schema_refuses_a_broken_card(
    change: Callable[[dict[str, Any]], None],
) -> None:
    data = copy.deepcopy(card(toys.KIRPICH))
    change(data)
    assert _errors(data)


def test_the_schema_refuses_broken_parts_of_a_full_card() -> None:
    for path, value in (
        (("tables", 0, "sha256"), "abc"),
        (("oracles", 0, "kind"), "guess"),
        (("properties", "symmetries", 0, "tolerance"), {"abs": 0.0}),
        (("properties", "conservation", 0, "tolerance"), {"reason": "r"}),
        (("outputs", 1, "physical"), {"low": 0.0, "low_inclusive": True}),
        (("outputs", 2, "gaps_allowed"), False),
    ):
        data = copy.deepcopy(card(FULL))
        _set(path, value)(data)
