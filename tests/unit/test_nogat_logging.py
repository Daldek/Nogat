"""The reference logging module every Python server copies (DEV-12.4 to DEV-12.9)."""

from __future__ import annotations

import asyncio
import io
import json
import logging
import threading
import time
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest
from nogat_logging import (
    AccessLog,
    ASGIApp,
    Message,
    Receive,
    Scope,
    Send,
    ServerLog,
    agent_class,
    redact_query,
    request_id,
    scrub,
)

CLIENT_V4 = "203.0.113.7"
CLIENT_V6 = "2001:db8:85a3::8a2e:370:7334"
PROXY = "198.51.100.23"


class Clock:
    """A clock the test moves by hand."""

    def __init__(self, moment: datetime) -> None:
        self.moment = moment

    def __call__(self) -> datetime:
        return self.moment


@pytest.fixture
def clock() -> Clock:
    return Clock(datetime(2026, 11, 13, 21, 4, 5, 123000, tzinfo=UTC))


@pytest.fixture
def stderr() -> io.StringIO:
    return io.StringIO()


@pytest.fixture
def log(tmp_path: Path, clock: Clock, stderr: io.StringIO) -> Iterator[ServerLog]:
    server = ServerLog(
        "hydrolog", "1.0.0", tmp_path / "logs", stream=stderr, clock=clock
    )
    yield server
    server.close()


@pytest.fixture
def started(log: ServerLog) -> Iterator[ServerLog]:
    log.start({"host": "127.0.0.1", "port": 8070})
    yield log
    log.stop()


def _records(directory: Path, kind: str | None = None) -> list[dict[str, Any]]:
    pattern = f"{kind}-*.jsonl" if kind else "*.jsonl"
    return [
        json.loads(line)
        for path in sorted(directory.glob(pattern))
        for line in path.read_text(encoding="utf-8").splitlines()
    ]


def _printed(stream: io.StringIO) -> list[dict[str, Any]]:
    return [json.loads(line) for line in stream.getvalue().splitlines()]


def _answer(status: int = 200, body: bytes = b"ok") -> ASGIApp:
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        await send({"type": "http.response.start", "status": status, "headers": []})
        await send({"type": "http.response.body", "body": body})

    return app


def _call(
    app: ASGIApp,
    path: str = "/",
    query: bytes = b"",
    headers: tuple[tuple[str, str], ...] = (),
    client: tuple[str, int] = (CLIENT_V4, 51234),
) -> list[Message]:
    scope: Scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "https",
        "path": path,
        "raw_path": path.encode(),
        "query_string": query,
        "root_path": "",
        "headers": [(k.lower().encode(), v.encode()) for k, v in headers],
        "client": client,
        "server": ("127.0.0.1", 8070),
    }
    sent: list[Message] = []

    async def receive() -> Message:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: Message) -> None:
        sent.append(message)

    async def call() -> None:
        # ASGIApp returns Awaitable[None]; asyncio.run needs a coroutine.
        await app(scope, receive, send)

    asyncio.run(call())
    return sent


@pytest.mark.parametrize(
    ("query", "logged"),
    [
        ("q=Jan+Kowalski&lat=51.2&lon=16.1", "q=&lat=51.2&lon=16.1"),
        ("lat=51.2&search=Z%C5%82otoryja", "lat=51.2&search="),
        ("%71=Kowalski&station=150160180", "%71=&station=150160180"),
        ("E-Mail=jan%40example.org&X-Api-Key=abc", "E-Mail=&X-Api-Key="),
        (
            "access_token=t&refresh-token=r&sessionid=s",
            "access_token=&refresh-token=&sessionid=",
        ),
        ("user=jan&password=p&sig=x&key=k", "user=&password=&sig=&key="),
        ("q&debug&v=1", "q&debug&v=1"),
        (
            "bbox=14.1,49.0,24.2,54.9&threshold=1000",
            "bbox=14.1,49.0,24.2,54.9&threshold=1000",
        ),
    ],
)
def test_query_parameters_that_may_be_personal_keep_only_their_name(
    query: str, logged: str
) -> None:
    assert redact_query(query) == logged


@pytest.mark.parametrize(
    ("user_agent", "kind"),
    [
        (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131.0.0.0",
            "browser",
        ),
        (
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "bot",
        ),
        (
            "Mozilla/5.0 (X11; Linux x86_64) HeadlessChrome/120.0.0.0 Safari/537.36",
            "bot",
        ),
        ("facebookexternalhit/1.1", "bot"),
        ("curl/8.14.1", "script"),
        ("python-httpx/0.28.1", "script"),
        ("", "none"),
        ("   ", "none"),
        (None, "none"),
    ],
)
def test_user_agent_is_reduced_to_its_class(user_agent: str | None, kind: str) -> None:
    assert agent_class(user_agent) == kind


@pytest.mark.parametrize(
    ("text", "scrubbed"),
    [
        (f"refused {CLIENT_V4}.", "refused [ip]."),
        (f"{CLIENT_V4}:51234 - GET /", "[ip]:51234 - GET /"),
        (f"for={CLIENT_V6}", "for=[ip]"),
        (f"[{CLIENT_V6}]:443", "[[ip]]:443"),
        ("2001:db8::7:51234 left", "[ip]:51234 left"),
        (f"client:{CLIENT_V4}", "client:[ip]"),
        ("::ffff:203.0.113.7", "::ffff:[ip]"),
        ("at 21:04:05.123 on 2026.11.13", "at 21:04:05.123 on 2026.11.13"),
        (
            "request 3f2a9c1b8e7d6c5a, version 0.5.0.dev0",
            "request 3f2a9c1b8e7d6c5a, version 0.5.0.dev0",
        ),
        ("values[1::2] and 999.1.1.1", "values[1::2] and 999.1.1.1"),
    ],
)
def test_ip_addresses_are_scrubbed_from_text(text: str, scrubbed: str) -> None:
    assert scrub(text) == scrubbed


def test_no_ip_address_reaches_any_log_even_behind_proxy_headers(
    started: ServerLog, stderr: io.StringIO
) -> None:
    forwarded = f"{CLIENT_V4}, {CLIENT_V6}"

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        headers = dict(scope["headers"])
        logging.getLogger("hydrolog.gui").warning(
            "suspicious request from %s", headers[b"x-forwarded-for"].decode()
        )
        raise RuntimeError(f"refused {headers[b'cf-connecting-ip'].decode()}")

    with pytest.raises(RuntimeError):
        _call(
            AccessLog(app, started),
            path="/api/run",
            query=f"lat=51.2&ip={CLIENT_V4}".encode(),
            headers=(
                ("X-Forwarded-For", forwarded),
                ("X-Real-IP", CLIENT_V4),
                ("CF-Connecting-IP", CLIENT_V6),
                ("Forwarded", f'for={CLIENT_V4};proto=https, for="[{CLIENT_V6}]"'),
                ("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) Chrome/131.0.0.0"),
                ("Cookie", "hydrolog_gui=secret-session"),
                ("Authorization", "Bearer secret-token"),
            ),
            client=(PROXY, 443),
        )
    _call(AccessLog(_answer(), started), path="/", client=(CLIENT_V6, 443))

    written = "".join(p.read_text("utf-8") for p in started.directory.iterdir())
    for secret in (CLIENT_V4, CLIENT_V6, PROXY, "secret-session", "secret-token"):
        assert secret not in written
        assert secret not in stderr.getvalue()
    access = _records(started.directory, "access")
    assert [r["path"] for r in access] == ["/api/run?lat=51.2&ip=[ip]", "/"]
    assert access[0]["agent"] == "browser"
    errors = _records(started.directory, "app")
    assert [r["message"] for r in errors] == [
        "suspicious request from [ip], [ip]",
        "unhandled exception",
    ]
    assert errors[1]["error"]["message"] == "refused [ip]"


def test_an_exception_is_one_app_record_of_its_request_and_a_500(
    started: ServerLog, stderr: io.StringIO
) -> None:
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        raise KeyError("lat")

    with pytest.raises(KeyError) as raised:
        _call(AccessLog(app, started), path="/api/delineate", query=b"q=Kowalski")
    # uvicorn then reports the same exception; it is not written again
    logging.getLogger("uvicorn.error").error(
        "Exception in ASGI application\n", exc_info=raised.value
    )

    (access,) = _records(started.directory, "access")
    (error,) = _records(started.directory, "app")
    assert (access["status"], access["path"]) == (500, "/api/delineate?q=")
    assert error["request_id"] == access["request_id"]
    assert error["event"] == "unhandled_exception"
    assert error["error"]["type"] == "KeyError"
    assert "Traceback" in error["error"]["stack"]
    reduced = [r for r in _printed(stderr) if r["kind"] == "app"]
    assert reduced == [
        {
            **{k: error[k] for k in ("time", "level", "app", "version", "kind")},
            "request_id": None,
            "event": "unhandled_exception",
            "message": None,
            "error": {"type": "KeyError"},
        }
    ]


def test_standard_error_gets_only_lifecycle_and_reduced_errors(
    started: ServerLog, stderr: io.StringIO
) -> None:
    logger = logging.getLogger("hydrolog.gui")
    logger.info("not logged at all")
    logger.warning("slow computation for station %s", "150160180")
    logger.error(
        "analysis failed for /api/run?q=Kowalski", extra={"event": "analysis_failed"}
    )
    _call(
        AccessLog(_answer(), started),
        path="/api/run",
        headers=(("User-Agent", "curl/8"),),
    )

    printed = _printed(stderr)
    assert [(r["kind"], r["event"]) for r in printed] == [
        ("lifecycle", "start"),
        ("app", "analysis_failed"),
    ]
    assert printed[1]["message"] is None and printed[1]["request_id"] is None
    assert printed[0]["settings"] == {"host": "127.0.0.1", "port": 8070}
    written = _records(started.directory, "app")
    assert [(r["level"], r["event"]) for r in written] == [
        ("warning", "hydrolog.gui"),
        ("error", "analysis_failed"),
    ]
    assert all(r["request_id"] is None for r in written)


def test_request_id_is_random_per_request_and_never_sent(started: ServerLog) -> None:
    seen: list[str | None] = []

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        seen.append(request_id())
        await _answer()(scope, receive, send)

    first = _call(AccessLog(app, started))
    _call(AccessLog(app, started))

    ids = [r["request_id"] for r in _records(started.directory, "access")]
    assert ids == seen and len(set(ids)) == 2
    assert all(len(i) == 16 and int(i, 16) >= 0 for i in ids)
    assert request_id() is None
    assert all(ids[0].encode() not in value for _, value in first[0]["headers"])


def test_static_content_is_logged_only_when_it_fails(log: ServerLog) -> None:
    quiet = r"^/js/|/tiles/\d+/\d+/\d+\.png$"
    _call(AccessLog(_answer(200), log, quiet=quiet), path="/js/app.js")
    _call(
        AccessLog(_answer(200), log, quiet=quiet),
        path="/api/v1/stores/nmt/versions/3/tiles/12/2234/1356.png",
        query=b"style=hillshade",
    )
    _call(AccessLog(_answer(404), log, quiet=quiet), path="/js/missing.js")
    _call(AccessLog(_answer(200, b"<html>"), log, quiet=quiet), path="/index.html")

    assert [(r["path"], r["status"], r["bytes"]) for r in _records(log.directory)] == [
        ("/js/missing.js", 404, 2),
        ("/index.html", 200, 6),
    ]


def test_files_are_daily_by_utc_date(log: ServerLog, clock: Clock) -> None:
    clock.moment = datetime(2026, 11, 14, 0, 30, tzinfo=timezone(timedelta(hours=1)))
    log.lifecycle("start", "started")
    clock.moment = datetime(2026, 11, 14, 0, 0, 0, 1000, tzinfo=UTC)
    log.lifecycle("stop", "stopped")

    names = sorted(p.name for p in log.directory.iterdir())
    assert names == ["lifecycle-2026-11-13.jsonl", "lifecycle-2026-11-14.jsonl"]
    times = [r["time"] for r in _records(log.directory)]
    assert times == ["2026-11-13T23:30:00.000Z", "2026-11-14T00:00:00.001Z"]


def test_files_are_deleted_once_14_days_old(
    log: ServerLog, clock: Clock, stderr: io.StringIO
) -> None:
    log.directory.mkdir()
    names = [
        "access-2026-11-12.jsonl",
        "app-2026-11-13.jsonl",
        "lifecycle-2026-11-14.jsonl",
        "access-2026-11-27.jsonl",
        "access-2026-13-01.jsonl",
        "notes.txt",
    ]
    for name in names:
        (log.directory / name).write_text("{}\n", encoding="utf-8")

    clock.moment = datetime(2026, 11, 26, 23, 59, 59, tzinfo=UTC)
    assert log.prune() == [log.directory / "access-2026-11-12.jsonl"]
    # a record written at 2026-11-13T00:00Z is 14 days old at 2026-11-27T00:00Z
    clock.moment = datetime(2026, 11, 27, 0, 0, tzinfo=UTC)
    assert log.prune() == [log.directory / "app-2026-11-13.jsonl"]

    assert sorted(p.name for p in log.directory.iterdir()) == [
        "access-2026-11-27.jsonl",
        "access-2026-13-01.jsonl",
        "lifecycle-2026-11-14.jsonl",
        "lifecycle-2026-11-26.jsonl",
        "lifecycle-2026-11-27.jsonl",
        "notes.txt",
    ]
    assert [r["message"] for r in _printed(stderr)] == [
        "deleted 1 log files dated 2026-11-12 or earlier",
        "deleted 1 log files dated 2026-11-13 or earlier",
    ]


def test_old_files_go_at_start_and_at_00_utc(log: ServerLog, clock: Clock) -> None:
    log.directory.mkdir()
    for day in ("2026-10-30", "2026-10-31"):
        (log.directory / f"access-{day}.jsonl").write_text("{}\n", encoding="utf-8")
    clock.moment = datetime(2026, 11, 13, 23, 59, 59, 900000, tzinfo=UTC)

    log.start()
    try:
        assert not (log.directory / "access-2026-10-30.jsonl").exists()
        assert (log.directory / "access-2026-10-31.jsonl").exists()
        clock.moment = datetime(2026, 11, 14, 0, 0, 1, tzinfo=UTC)
        deadline = time.monotonic() + 5
        while (log.directory / "access-2026-10-31.jsonl").exists():
            assert time.monotonic() < deadline, "not deleted at 00:00 UTC"
            time.sleep(0.05)
    finally:
        log.stop()


def test_stop_restores_logging(log: ServerLog) -> None:
    root = logging.getLogger()
    before = (list(root.handlers), threading.excepthook)

    log.start()
    log.stop()

    assert (list(root.handlers), threading.excepthook) == before
    assert [r["event"] for r in _records(log.directory, "lifecycle")] == [
        "start",
        "stop",
    ]
