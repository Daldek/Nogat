"""The log record `nogat-log/1` (schemas/log/record-1.schema.json).

Every server writes its records with Nogat's reference module, which projects
copy byte for byte like the schema (DEV-12.4 to DEV-12.9, DEV-15.6); these
tests pin that the module's records are what the schema admits and that the
schema admits nothing that could name a client.
"""

from __future__ import annotations

import asyncio
import copy
import io
import json
import logging
from pathlib import Path
from typing import Any

import jsonschema
import pytest
from nogat_logging import FORMAT, AccessLog, Message, Receive, Scope, Send, ServerLog

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schemas/log/record-1.schema.json"
SCHEMA: dict[str, Any] = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
VALIDATOR = jsonschema.Draft202012Validator(SCHEMA)
ACCESS, APP, REDUCED, LIFECYCLE = (SCHEMA["examples"][i] for i in range(4))


def _errors(record: Any) -> list[str]:
    return [e.message for e in VALIDATOR.iter_errors(record)]


def _with(record: dict[str, Any], **changes: Any) -> dict[str, Any]:
    changed = copy.deepcopy(record)
    changed.update(changes)
    return changed


def test_schema_is_valid_draft_2020_12_and_named_like_the_module() -> None:
    jsonschema.Draft202012Validator.check_schema(SCHEMA)
    assert SCHEMA["title"] == FORMAT


@pytest.mark.parametrize("index", range(len(SCHEMA["examples"])))
def test_examples_validate(index: int) -> None:
    assert _errors(SCHEMA["examples"][index]) == []


def test_records_of_the_reference_module_validate(tmp_path: Path) -> None:
    stderr = io.StringIO()
    log = ServerLog("hydrograf", "0.5.0.dev0", tmp_path / "logs", stream=stderr)
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "access-2026-01-01.jsonl").write_text("{}\n", "utf-8")

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        if scope["path"] == "/fail":
            raise ValueError("no such station")
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"{}"})

    async def receive() -> Message:
        return {"type": "http.request", "body": b""}

    async def send(message: Message) -> None:
        pass

    def call(path: str, query: bytes, headers: list[tuple[bytes, bytes]]) -> None:
        scope = {"type": "http", "method": "POST", "path": path, "query_string": query}
        asyncio.run(AccessLog(app, log)({**scope, "headers": headers}, receive, send))

    log.start({"host": "0.0.0.0", "port": 8000, "data_dir": tmp_path, "public": True})
    try:
        call("/api/delineate-watershed", b"q=x&lat=51.2", [(b"user-agent", b"curl/8")])
        call("/", b"", [])
        with pytest.raises(ValueError):
            call("/fail", b"", [(b"user-agent", b"Mozilla/5.0 Googlebot/2.1")])
        logging.getLogger("api").warning("slow query")
        logging.getLogger("api").error("database unreachable", exc_info=OSError(5, "x"))
    finally:
        log.stop()

    files = [
        json.loads(line)
        for path in sorted((tmp_path / "logs").glob("*.jsonl"))
        for line in path.read_text("utf-8").splitlines()
    ]
    printed = [json.loads(line) for line in stderr.getvalue().splitlines()]
    assert {(r["kind"], r.get("event")) for r in files} >= {
        ("access", None),
        ("app", "api"),
        ("app", "unhandled_exception"),
        ("lifecycle", "start"),
        ("lifecycle", "prune"),
        ("lifecycle", "stop"),
    }
    assert {r["kind"] for r in printed} == {"app", "lifecycle"}
    for record in files + printed:
        assert _errors(record) == [], record


@pytest.mark.parametrize(
    "record",
    [
        _with(ACCESS, ip="203.0.113.7"),
        _with(ACCESS, client="203.0.113.7"),
        _with(ACCESS, user_agent="Mozilla/5.0"),
        _with(ACCESS, agent="Mozilla/5.0 (X11; Linux x86_64)"),
        _with(ACCESS, headers={"cookie": "x"}),
        _with(ACCESS, request_id=None),
        _with(ACCESS, request_id="0123456789abcdef0123456789abcdef"),
        _with(ACCESS, time="2026-11-13T22:04:05.123+01:00"),
        _with(ACCESS, level="error"),
        _with(APP, error={"type": "KeyError", "locals": {"ip": "203.0.113.7"}}),
        _with(APP, body="{}"),
        _with(REDUCED, error={"message": "x"}),
        _with(LIFECYCLE, request_id="3f2a9c1b8e7d6c5a"),
        _with(LIFECYCLE, settings={"operator": {"email": "jan@example.org"}}),
        {k: v for k, v in ACCESS.items() if k != "agent"},
        {k: v for k, v in APP.items() if k != "error"},
    ],
)
def test_schema_admits_nothing_beyond_the_named_keys(record: dict[str, Any]) -> None:
    assert _errors(record) != []
