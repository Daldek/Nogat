"""Canonical agent-interface schemas (AGI-4.1 to AGI-4.3, AGI §2).

The schemas in schemas/agent/ are what every tool's documents are validated
against; these tests pin the rules they enforce and check that Nogat's own
error documents conform (HUB-4.8).
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import ecosystem
import jsonschema
import pytest
from referencing import Registry, Resource

SCHEMAS = Path(__file__).resolve().parents[2] / "schemas" / "agent"


def _registry() -> Registry:
    resources = []
    for path in sorted(SCHEMAS.glob("*.schema.json")):
        contents = json.loads(path.read_text(encoding="utf-8"))
        resources.append((contents["$id"], Resource.from_contents(contents)))
    return Registry().with_resources(resources)


REGISTRY = _registry()


def _errors(kind: str, document: Any) -> list[str]:
    schema = json.loads((SCHEMAS / f"{kind}-1.schema.json").read_text("utf-8"))
    validator = jsonschema.Draft202012Validator(schema, registry=REGISTRY)
    return [e.message for e in validator.iter_errors(document)]


@pytest.mark.parametrize("path", sorted(SCHEMAS.glob("*.schema.json")), ids=str)
def test_schema_is_valid_draft_2020_12(path: Path) -> None:
    jsonschema.Draft202012Validator.check_schema(json.loads(path.read_text("utf-8")))


RESULT: dict[str, Any] = {
    "schema": "kartograf-result/1",
    "tool": "kartograf",
    "version": "0.8.0",
    "command": "dem download",
    "check": False,
    "status": "ok",
    "result": {"schema": "kartograf-download/1", "files": []},
}


def _with(base: dict[str, Any], **changes: Any) -> dict[str, Any]:
    document = copy.deepcopy(base)
    document.update(changes)
    return document


OK = {"id": "N-34-1", "status": "ok"}
FAILED = {
    "id": "N-34-2",
    "status": "failed",
    "code": "no_data",
    "reason": "no_coverage",
}


@pytest.mark.parametrize(
    "document",
    [
        RESULT,
        _with(RESULT, result=None, status="cancelled"),
        _with(RESULT, result=[{"schema": "kartograf-sheet/1"}]),
        _with(RESULT, status="partial", items=[OK, FAILED]),
        _with(RESULT, status="failed", items=[FAILED], result=None),
        _with(RESULT, page={"truncated": True, "next_cursor": "abc", "total": 40}),
        _with(RESULT, page={"truncated": False}, extra_field="allowed"),
        _with(
            RESULT, notices=[{"level": "warning", "code": "old_data", "message": "x"}]
        ),
    ],
)
def test_result_valid(document: dict[str, Any]) -> None:
    assert _errors("result", document) == []


@pytest.mark.parametrize(
    "document",
    [
        _with(RESULT, status="partial", items=[OK]),
        _with(RESULT, status="partial"),
        _with(RESULT, status="failed", items=[OK, FAILED]),
        _with(RESULT, status="failed", items=[]),
        _with(RESULT, status="partial", items=[OK, {"id": 1, "status": "failed"}]),
        _with(RESULT, items=[{"id": 1, "status": "failed", "code": "made_up"}]),
        _with(RESULT, page={"truncated": True}),
        _with(RESULT, result={"files": []}),
        _with(RESULT, schema="kartograf-result/2"),
        _with(RESULT, command="download"),
        {k: v for k, v in RESULT.items() if k != "check"},
    ],
)
def test_result_invalid(document: dict[str, Any]) -> None:
    assert _errors("result", document) != []


ERROR: dict[str, Any] = {
    "schema": "obserwator-error/1",
    "code": "validation_error",
    "title": "Invalid input",
    "message": "unknown station",
    "hint": "run: obserwator stations list",
    "details": {"reason": "unknown_station", "option": "station"},
    "exit_code": 2,
    "command": "series fetch",
}


@pytest.mark.parametrize(
    "document",
    [
        ERROR,
        _with(ERROR, code="rate_limited", exit_code=None),
        _with(ERROR, code="cancelled", exit_code=130, details={}),
    ],
)
def test_error_valid(document: dict[str, Any]) -> None:
    assert _errors("error", document) == []


@pytest.mark.parametrize(
    "document",
    [
        _with(ERROR, code="invalid_input"),
        _with(ERROR, exit_code=1),
        _with(ERROR, code="rate_limited", exit_code=1),
        _with(ERROR, details={"reason": "Unknown Station"}),
        {k: v for k, v in ERROR.items() if k != "details"},
    ],
)
def test_error_invalid(document: dict[str, Any]) -> None:
    assert _errors("error", document) != []


def test_error_schema_codes_are_the_registry() -> None:
    schema = json.loads((SCHEMAS / "error-1.schema.json").read_text("utf-8"))
    registry = json.loads(
        (ecosystem.STANDARDS / "error_registry.json").read_text("utf-8")
    )
    assert schema["$defs"]["code"]["enum"] == [e["code"] for e in registry["errors"]]


COMMAND: dict[str, Any] = {
    "name": "dem download",
    "operation_id": "kartograf_dem_download",
    "function": "kartograf.download_dem",
    "summary": "Download a DEM for an area.",
    "description": "When to use: ... When not to use: ...",
    "options": [
        {
            "name": "bbox",
            "type": "array",
            "required": True,
            "description": "min_x,min_y,max_x,max_y",
            "one_of": "area",
        },
        {
            "name": "resolution",
            "type": "number",
            "unit": "m",
            "required": False,
            "default": 1,
            "enum": [{"value": 1, "meaning": "1 m grid"}],
            "description": "grid resolution",
        },
        {
            "name": "output_dir",
            "type": "string",
            "required": False,
            "description": "where to write",
            "path_role": "output",
        },
    ],
    "result": {"schema": "kartograf-download/1", "cardinality": "bounded"},
    "effects": {
        "read_only": False,
        "writes": "add",
        "idempotent": True,
        "network": True,
        "destructive": False,
    },
    "check": "dem check",
    "families": ["core", "dem"],
    "rules": ["Run dem check first."],
    "examples": [
        {"call": "kartograf dem download --bbox 1,2,3,4 --json", "result": {}}
    ],
    "errors": ["validation_error", "source_unavailable"],
    "i18n": {"pl": {"summary": "Pobiera NMT dla obszaru."}},
}
CATALOG: dict[str, Any] = {
    "schema": "kartograf-commands/1",
    "tool": "kartograf",
    "version": "0.8.0",
    "commands": [COMMAND],
}


def _command(**changes: Any) -> dict[str, Any]:
    return _with(CATALOG, commands=[_with(COMMAND, **changes)])


def test_catalog_valid() -> None:
    assert _errors("commands", CATALOG) == []


@pytest.mark.parametrize(
    "document",
    [
        _command(operation_id="kartograf_" + "x" * 40 + "_download"),
        _command(operation_id="kartograf_download"),
        _command(name="download"),
        _command(effects={**COMMAND["effects"], "read_only": True}),
        _command(examples=[]),
        _command(errors=["made_up"]),
        _command(i18n={}),
        _command(options=[{"name": "bbox", "type": "tuple", "required": True}]),
        _command(families=["Core"]),
        _with(CATALOG, schema="kartograf-catalog/1"),
        _with(CATALOG, commands=[]),
    ],
)
def test_catalog_invalid(document: dict[str, Any]) -> None:
    assert _errors("commands", document) != []


def _option(**changes: Any) -> dict[str, Any]:
    return _command(options=[_with(COMMAND["options"][0], **changes)])


# The optional fields a command builder reads (AGI-2.3, DEV-15.17, ECO-093).
FORM = _command(
    one_of=[["sheet"], ["bbox", "bbox_crs"]],
    options=[
        {
            "name": "sheet",
            "type": "string",
            "required": False,
            "description": "sheet code",
            "one_of": "area",
            "section": "Product and area",
            "i18n": {"pl": {"description": "Godło", "section": "Produkt i obszar"}},
        },
        {
            "name": "bbox",
            "type": "array",
            "items": "number",
            "required": False,
            "description": "area",
            "one_of": "area",
            "requires": ["bbox_crs"],
        },
        {
            "name": "bbox_crs",
            "type": "string",
            "required": False,
            "description": "CRS of bbox",
            "applies_to": {"bbox": True},
            "enum": [{"value": "EPSG:2180", "meaning": "PL-1992"}],
            "i18n": {"pl": {"enum": {"EPSG:2180": "PL-1992, metry"}}},
        },
        {
            "name": "years",
            "type": "array",
            "items": {"type": "integer", "minimum": 1},
            "required": False,
            "description": "years",
        },
        {
            "name": "depth",
            "type": "number",
            "required": False,
            "description": "depth",
            "exclusive_minimum": 0,
            "exclusive_maximum": 500,
            "required_when": {"product": ["nmt", "nmpt"], "cutout": True},
            "excludes": ["years"],
        },
        {
            "name": "start",
            "type": "string",
            "format": "date",
            "required": False,
            "description": "first day",
        },
    ],
)


def test_catalog_with_the_fields_of_a_form_valid() -> None:
    assert _errors("commands", FORM) == []


@pytest.mark.parametrize(
    "document",
    [
        _command(one_of=[["bbox"]]),
        _command(one_of=[["bbox"], []]),
        _command(one_of=[["bbox"], ["Sheet"]]),
        _option(items="tuple"),
        _option(requires="output_dir"),
        _option(excludes=["Output"]),
        _option(applies_to={}),
        _option(applies_to={"cutout": False}),
        _option(required_when={"product": []}),
        _option(exclusive_minimum="0"),
        _option(section=""),
        _option(format=""),
        _option(i18n={"pl": {"enum": {"1": 1}}}),
    ],
)
def test_catalog_with_wrong_fields_of_a_form_invalid(document: dict[str, Any]) -> None:
    assert _errors("commands", document) != []


ENTRY: dict[str, Any] = {
    "name": "dem download",
    "operation_id": "kartograf_dem_download",
    "summary": "Download a DEM for an area.",
    "read_only": False,
    "families": ["core", "dem"],
}
COMMAND_LIST: dict[str, Any] = {
    "schema": "kartograf-command-list/1",
    "tool": "kartograf",
    "version": "0.8.0",
    "commands": [ENTRY],
}


def _entry(**changes: Any) -> dict[str, Any]:
    return _with(COMMAND_LIST, commands=[_with(ENTRY, **changes)])


def test_command_list_valid() -> None:
    assert _errors("command-list", COMMAND_LIST) == []


@pytest.mark.parametrize(
    "document",
    [
        _with(COMMAND_LIST, schema="kartograf-commands/1"),
        _with(COMMAND_LIST, commands=[]),
        _entry(name="download"),
        _entry(operation_id="kartograf_download"),
        _entry(read_only="no"),
        _with(
            COMMAND_LIST, commands=[{k: v for k, v in ENTRY.items() if k != "summary"}]
        ),
    ],
)
def test_command_list_invalid(document: dict[str, Any]) -> None:
    assert _errors("command-list", document) != []


@pytest.mark.parametrize(
    "argv",
    [["map", "--chek"], ["no-such-command"]],
)
def test_nogat_errors_conform(
    argv: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    ecosystem.main(argv)
    document = json.loads(capsys.readouterr().err.strip().splitlines()[-1])
    assert _errors("error", document) == []


def test_nogat_conflict_conforms(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    stale = tmp_path / "ECOSYSTEM_MAP.md"
    stale.write_text("old\n", encoding="utf-8")
    monkeypatch.setattr(ecosystem, "MAP", stale)
    assert ecosystem.main(["map", "--check"]) == 4
    document = json.loads(capsys.readouterr().err.strip().splitlines()[-1])
    assert _errors("error", document) == []
