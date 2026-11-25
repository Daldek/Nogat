"""A server's job `nogat-job/1` (schemas/exchange/job-1.schema.json).

A client starts a long run with `POST /api/v1/jobs` and follows it at
`GET /api/v1/jobs/<id>` on a tool's own server or on Latarnik (AGI-6.10,
ECO-095); these tests pin what a client relies on: an unguessable id, the
seven states and the times each one implies, the body that starts a job, and
an unknown field keeping the version (AGI-4.1).
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import jsonschema
import pytest
from referencing import Registry, Resource

SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "schemas" / "exchange" / "job-1.schema.json"
)
SCHEMA: dict[str, Any] = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
VALIDATOR = jsonschema.Draft202012Validator(
    SCHEMA, format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER
)
START = jsonschema.Draft202012Validator(
    {"$ref": f"{SCHEMA['$id']}#/$defs/start"},
    registry=Registry().with_resource(SCHEMA["$id"], Resource.from_contents(SCHEMA)),
)
RUNNING: dict[str, Any] = SCHEMA["examples"][0]
T0, T1 = "2027-01-04T10:15:02+01:00", "2027-01-04T10:17:40+01:00"


def _errors(document: Any) -> list[str]:
    return [e.message for e in VALIDATOR.iter_errors(document)]


def _job(**changes: Any) -> dict[str, Any]:
    document = copy.deepcopy(RUNNING)
    document.update(changes)
    return document


def _without(key: str) -> dict[str, Any]:
    document = copy.deepcopy(RUNNING)
    del document[key]
    return document


def test_schema_is_valid_draft_2020_12() -> None:
    jsonschema.Draft202012Validator.check_schema(SCHEMA)


@pytest.mark.parametrize("index", range(len(SCHEMA["examples"])))
def test_examples_validate(index: int) -> None:
    assert _errors(SCHEMA["examples"][index]) == []


@pytest.mark.parametrize("key", ["id", "tool", "command", "state", "created_at"])
def test_a_job_without_what_a_client_needs_is_refused(key: str) -> None:
    assert _errors(_without(key))


@pytest.mark.parametrize(
    "document",
    [
        _job(schema="nogat-job/2"),
        _job(id="42"),
        _job(id="3f9c2a7b/e1d04c56a8e2b7f01d9c4e6a"),
        _job(state="done"),
        _job(command="batch"),
        _job(tool="Hydrolog"),
        _job(progress={"done": -1}),
        _job(progress={"total": 40}),
        _job(created_at="yesterday"),
        _job(state="queued", started_at=T0, finished_at=None),
        _job(state="queued", started_at=None, finished_at=T1),
        _job(started_at=None),
        _without("started_at"),
        _job(finished_at=T1),
        _job(state="succeeded", finished_at=None),
        _job(state="interrupted", finished_at=None),
    ],
    ids=[
        "other-version",
        "id-too-short-to-be-unguessable",
        "id-not-url-safe",
        "unknown-state",
        "command-not-group-verb",
        "tool-not-lower-case",
        "negative-progress",
        "progress-without-done",
        "created-not-a-time",
        "queued-but-started",
        "queued-but-finished",
        "running-not-started",
        "running-without-start",
        "running-but-finished",
        "succeeded-without-end",
        "interrupted-without-end",
    ],
)
def test_malformed_jobs_are_refused(document: dict[str, Any]) -> None:
    assert _errors(document)


def test_a_job_cancelled_while_queued_never_started() -> None:
    document = _job(state="cancelled", started_at=None, finished_at=T1)
    assert _errors(document) == []


@pytest.mark.parametrize("state", ["succeeded", "partial", "failed"])
def test_an_ended_job_has_its_end(state: str) -> None:
    assert _errors(_job(state=state, finished_at=T1)) == []


def test_a_queued_job_has_no_times_but_its_creation() -> None:
    document = _job(state="queued", started_at=None, finished_at=None)
    del document["progress"]
    assert _errors(document) == []


def test_a_flow_of_latarnik_is_a_job_too() -> None:
    document = _job(tool="latarnik", command="flows point-design-hydrograph")
    assert _errors(document) == []


def test_unknown_fields_keep_the_version() -> None:
    assert _errors(_job(expires_at="2027-01-04T11:17:40+01:00", queue=1)) == []


@pytest.mark.parametrize(
    ("body", "valid"),
    [
        ({"command": "commands batch", "options": {"path": "x"}}, True),
        ({"command": "route network"}, True),
        ({"options": {}}, False),
        ({"command": "batch"}, False),
        ({"command": "route network", "options": ["x"]}, False),
    ],
    ids=[
        "with-options",
        "options-default",
        "no-command",
        "not-group-verb",
        "options-list",
    ],
)
def test_the_body_that_starts_a_job(body: dict[str, Any], valid: bool) -> None:
    assert (list(START.iter_errors(body)) == []) is valid
