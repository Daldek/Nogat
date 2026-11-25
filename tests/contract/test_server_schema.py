"""The discovery document `nogat-server/1` (schemas/exchange/server-1.schema.json).

A client reads it at `GET /api/v1/server` of a tool's own server or of
Latarnik (ECO-094); these tests pin what a client relies on: every service
names its tool, version, API majors and capabilities, a capability is a
tool's own word, and an unknown field keeps the version (AGI-4.1).
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import jsonschema
import pytest

SCHEMAS = Path(__file__).resolve().parents[2] / "schemas" / "exchange"
SCHEMA_PATH = SCHEMAS / "server-1.schema.json"
SCHEMA: dict[str, Any] = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
VALIDATOR = jsonschema.Draft202012Validator(
    SCHEMA, format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER
)


def _errors(document: Any) -> list[str]:
    return [e.message for e in VALIDATOR.iter_errors(document)]


def _service(**changes: Any) -> dict[str, Any]:
    """The tool's own server of the first example, its one service changed."""
    document: dict[str, Any] = copy.deepcopy(SCHEMA["examples"][0])
    document["services"][0].update(changes)
    return document


def _service_without(key: str) -> dict[str, Any]:
    document: dict[str, Any] = copy.deepcopy(SCHEMA["examples"][0])
    del document["services"][0][key]
    return document


def test_schema_is_valid_draft_2020_12() -> None:
    jsonschema.Draft202012Validator.check_schema(SCHEMA)


@pytest.mark.parametrize("index", range(len(SCHEMA["examples"])))
def test_examples_validate(index: int) -> None:
    assert _errors(SCHEMA["examples"][index]) == []


@pytest.mark.parametrize("key", ["tool", "version", "api", "capabilities"])
def test_a_service_without_what_a_client_needs_is_refused(key: str) -> None:
    assert _errors(_service_without(key))


@pytest.mark.parametrize(
    "document",
    [
        {"schema": "nogat-server/1", "services": []},
        {"schema": "nogat-server/2", "services": SCHEMA["examples"][0]["services"]},
        _service(api={}),
        _service(api={"v1": "/api/v1"}),
        _service(api={"0": "/api/v0"}),
        _service(tool="Obserwator"),
        _service(capabilities=["series", "series"]),
        _service(terms={"url": "/regulamin.html"}),
        _service(terms={"url": "/regulamin.html", "version": "1"}),
        _service(state="down"),
    ],
    ids=[
        "no-service",
        "other-version",
        "no-major",
        "major-not-a-number",
        "major-zero",
        "tool-not-lower-case",
        "capability-twice",
        "terms-without-version",
        "terms-version-not-x-y",
        "unknown-state",
    ],
)
def test_malformed_documents_are_refused(document: dict[str, Any]) -> None:
    assert _errors(document)


def test_capabilities_are_the_tools_own_words() -> None:
    # Kartograf's words are not Obserwator's; the schema keeps no closed list.
    words = ["catalog", "plan", "script"]
    assert _errors(_service(tool="kartograf", capabilities=words)) == []


def test_a_major_beside_v1_and_an_absolute_base_are_taken() -> None:
    api = {"1": "/api/v1", "2": "https://hydrolog.example.org/api/v2"}
    assert _errors(_service(api=api)) == []


def test_unknown_fields_keep_the_version() -> None:
    document = _service(queue={"waiting": 2})
    document["generated_at"] = "2027-01-01T00:00:00Z"
    assert _errors(document) == []
