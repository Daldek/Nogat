"""The hand-off envelope `nogat-handoff/1` (schemas/exchange/handoff-1.schema.json).

Projects copy the schema like schemas/agent/ (ECO-050); these tests pin what
the envelope requires and what it leaves to the payload's owner, and that
the schema's own example, the complete form of Hydrolog's GUI plan (D15),
validates.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import jsonschema
import pytest

SCHEMAS = Path(__file__).resolve().parents[2] / "schemas" / "exchange"
SCHEMA_PATH = SCHEMAS / "handoff-1.schema.json"
SCHEMA: dict[str, Any] = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
VALIDATOR = jsonschema.Draft202012Validator(SCHEMA)
EXAMPLE: dict[str, Any] = SCHEMA["examples"][0]


def _errors(document: Any) -> list[str]:
    return [e.message for e in VALIDATOR.iter_errors(document)]


def _with(**changes: Any) -> dict[str, Any]:
    document = copy.deepcopy(EXAMPLE)
    document.update(changes)
    return document


def _without(*keys: str) -> dict[str, Any]:
    return {k: v for k, v in copy.deepcopy(EXAMPLE).items() if k not in keys}


def test_schema_is_valid_draft_2020_12() -> None:
    jsonschema.Draft202012Validator.check_schema(SCHEMA)


@pytest.mark.parametrize("index", range(len(SCHEMA["examples"])))
def test_examples_validate(index: int) -> None:
    assert _errors(SCHEMA["examples"][index]) == []


@pytest.mark.parametrize(
    "document",
    [
        _without("result"),
        _with(producer={"tool": "hydrograf", "version": "0.9.0"}),
        _with(provenance={}),
        _with(created_at="2026-11-02T11:15:00.123+01:00"),
        _with(payload={"schema": "obserwator-pmaxtp/1", "depth_mm": 105.0}),
        _with(
            result={
                "command": "POST /api/generate-hydrograph",
                "computed_with": {"tool": "hydrolog", "version": "0.6.3"},
                "peak_discharge_m3s": 58.9,
            }
        ),
        _with(origin_page_title="unknown fields are allowed (AGI-4.1)"),
    ],
    ids=[
        "no-result",
        "no-page",
        "empty-provenance",
        "offset-and-fraction",
        "other-payload-kind",
        "result-by-another-engine",
        "unknown-field",
    ],
)
def test_handoff_valid(document: dict[str, Any]) -> None:
    assert _errors(document) == []


@pytest.mark.parametrize(
    "required", ["schema", "created_at", "producer", "subject", "provenance", "payload"]
)
def test_required_field(required: str) -> None:
    assert _errors(_without(required)) != []


@pytest.mark.parametrize(
    "document",
    [
        _with(schema="nogat-handoff/2"),
        _with(created_at="2026-11-02T10:15:00"),
        _with(created_at="2026-11-02"),
        _with(producer={"tool": "Hydrolog", "version": "1.0.0"}),
        _with(producer={"tool": "hydrolog"}),
        _with(producer={"tool": "hydrolog", "version": "1.0.0", "page": ""}),
        _with(subject=""),
        _with(provenance={"rainfall": {"probability_percent": 1}}),
        _with(provenance={"Rainfall": {"source": "pmaxtp"}}),
        _with(provenance={"rainfall": "pmaxtp"}),
        _with(payload={"name": "no schema", "nodes": []}),
        _with(payload={"schema": "network"}),
        _with(payload={"schema": "hydrolog-network/0"}),
        _with(result={}),
        _with(result={"peak_discharge_m3s": -1.0}),
        _with(result={"peak_discharge_m3s": "60,2"}),
        _with(result={"computed_with": {"tool": "hydrolog"}}),
    ],
    ids=[
        "schema-version",
        "time-without-offset",
        "date-only",
        "tool-not-lowercase",
        "producer-without-version",
        "empty-page",
        "empty-subject",
        "origin-without-source",
        "input-name-not-lowercase",
        "origin-not-object",
        "payload-without-schema",
        "payload-schema-not-a-kind",
        "payload-version-zero",
        "empty-result",
        "negative-peak",
        "peak-as-text",
        "engine-without-version",
    ],
)
def test_handoff_invalid(document: dict[str, Any]) -> None:
    assert _errors(document) != []
