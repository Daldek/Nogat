"""The kit's admin panel in a browser: design/kit/nogat-admin.js (DEV-15.13, ECO-067).

The panel is tested where it runs: Chromium through Playwright, on pages
served under CSP `'self'` by a server that answers the admin API of
DEV-15.13 from memory as a GUI does: the key in `X-Admin-Key`, refusals
with their reasons, sixty reports, the days of `stats.jsonl` and the
status; under `/api/v1/admin/` it signs in by a session cookie instead, as
an app with accounts. The browser's clock and time zone are fixed. A CSP
violation, a console error other than a refused request, or an uncaught
exception fails the test. The specimen runs once on its own fake API.
"""

from __future__ import annotations

import functools
import hmac
import http.server
import json
import shutil
import threading
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, cast
from urllib.parse import parse_qs, urlsplit

import pytest
from playwright.sync_api import Browser, Page, Playwright, expect, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
KEY = "klucz-testowy"
NOW = "2026-11-13T12:00:00Z"
TODAY = date(2026, 11, 13)
FIRST_DAY = date(2026, 8, 1)
API = ("/api/admin/", "/api/v1/admin/")
KEYS = [
    "date",
    "visitors",
    "page_views",
    "stations_opened",
    "analyses_run",
    "downloads",
]

SHELL_PAGE = """<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Hydrolog: administracja</title>
<link rel="stylesheet" href="../tokens.css">
<link rel="stylesheet" href="../kit/nogat-admin.css">
<script type="module" src="../kit/nogat-admin.js"></script>
<script type="module" src="app.js"></script>
</head>
<body>
<nogat-admin app="Hydrolog" project="hydrolog" back="../" marks="../marks/">
<section data-admin-section="resources" data-label="Zasoby">
<h2>Zasoby</h2>
<p id="resources"></p>
</section>
</nogat-admin>
</body>
</html>
"""

# The app's script, loaded after the kit: it records the panel's events, and its
# section asks its own route through adminFetch when shown.
APP_SCRIPT = """const admin = document.querySelector("nogat-admin");
const events = ["nogat-admin-section", "nogat-admin-signout",
  "nogat-admin-unauthorized"];
window.seen = [];
for (const type of events) {
  document.addEventListener(type, (event) => seen.push([type, event.detail]));
}
admin.addEventListener("nogat-admin-section", async (event) => {
  if (event.detail.id !== "resources") return;
  const response = await admin.adminFetch("resources");
  const doc = await response.json();
  const text = response.ok ? doc.items.join(", ") : doc.code;
  document.getElementById("resources").textContent = text;
});
"""

ALONE_PAGE = """<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="tokens.css">
<link rel="stylesheet" href="kit/nogat-admin.css">
<script type="module" src="kit/nogat-admin.js"></script>
<script type="module" src="{script}"></script>
</head>
<body>
<main><nogat-admin-feedback endpoint="/api/v1/admin/feedback"{auth}>
</nogat-admin-feedback></main>
</body>
</html>
"""

WATCH_SCRIPT = """window.seen = [];
document.addEventListener("nogat-admin-unauthorized", (event) =>
  seen.push([event.type, event.detail]));
"""

# An app whose requests carry a header of its own, as Archiwista's CSRF token.
CUSTOM_SCRIPT = """const element = document.querySelector("nogat-admin-feedback");
element.adminFetch = (url, init = {}) => {
  const headers = { ...init.headers, "X-Archiwista-CSRF": "zeton" };
  return fetch(url, { ...init, credentials: "same-origin", headers });
};
"""

# An app with accounts: the shell on its own API prefix, `auth` set as a property.
SESSION_PAGE = """<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="../tokens.css">
<link rel="stylesheet" href="../kit/nogat-admin.css">
<script type="module" src="../kit/nogat-admin.js"></script>
<script type="module" src="session.js"></script>
</head>
<body>
<nogat-admin app="Archiwista" project="archiwista" api="/api/v1/admin/"></nogat-admin>
</body>
</html>
"""

SESSION_SCRIPT = (
    """document.querySelector("nogat-admin").auth = "session";
"""
    + WATCH_SCRIPT
)

WATCH_CSP = """window.cspViolations = [];
document.addEventListener("securitypolicyviolation", (event) =>
  window.cspViolations.push(`${event.violatedDirective} ${event.blockedURI}`));
"""


def _report(n: int) -> dict[str, Any]:
    """Report `n` of sixty: ids ascend with time; every third one is unread."""
    message = f"Zgłoszenie {n}"
    if n == 60:
        message = "Mapa się nie ładuje <b>wcale</b> " + "x" * 300
    return {
        "id": n,
        "created_at": f"2026-11-{1 + n // 6:02d}T{n % 24:02d}:00:00+00:00",
        "message": message,
        "context": {
            "view": "mapa",
            "station": f"1500{n:02d}" if n % 2 == 0 else None,
            "parameters": {"q": n, "okres": "1h"},
            "app_version": "1.2.3",
        },
        "is_read": n % 3 != 0,
    }


def _day(i: int) -> dict[str, Any]:
    visitors = 10 + i % 7
    return {
        "date": (FIRST_DAY + timedelta(days=i)).isoformat(),
        "visitors": visitors,
        "page_views": 3 * visitors,
        "stations_opened": i % 5,
        "analyses_run": i % 4,
        "downloads": i % 3,
    }


# The lines of stats.jsonl from 2026-08-01 to today, 105 days.
DAYS = [_day(i) for i in range((TODAY - FIRST_DAY).days + 1)]

STATUS = {
    "app": "Hydrolog",
    "version": "1.4.0",
    "started_at": "2026-11-11T08:56:00+00:00",
    "uptime_s": 2 * 86400 + 3 * 3600 + 4 * 60 + 5,
    "data_dir": "/srv/hydrolog",
    "disk": {"free_bytes": 12_300_000_000, "total_bytes": 100_000_000_000},
    "checks": [
        {"name": "data_dir", "status": "ok", "detail": "zapisywalny"},
        {"name": "reports", "status": "warning", "detail": "20 nieprzeczytanych"},
        {"name": "hydrolog", "status": "failed", "detail": "polecenie nie odpowiada"},
    ],
}


@dataclass
class Call:
    method: str
    path: str
    query: dict[str, str]
    key: str | None
    cookie: str | None
    csrf: str | None
    body: Any


def _problem(code: str, status: int, reason: str | None = None) -> dict[str, Any]:
    return {
        "type": f"https://nogat.example/errors#{code}",
        "title": code,
        "status": status,
        "detail": code,
        "code": code,
        "details": {"reason": reason} if reason else {},
    }


@dataclass
class FakeApi:
    """The admin API of a GUI, in memory (DEV-15.13)."""

    key: str | None = KEY
    session: str = "ok"
    reports: dict[int, dict[str, Any]] = field(
        default_factory=lambda: {n: _report(n) for n in range(1, 61)}
    )
    calls: list[Call] = field(default_factory=list)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def answer(
        self,
        method: str,
        path: str,
        query: dict[str, str],
        headers: dict[str, str | None],
        body: Any,
    ) -> tuple[int, Any]:
        with self.lock:
            key, cookie = headers["X-Admin-Key"], headers["Cookie"]
            call = Call(
                method, path, query, key, cookie, headers["X-Archiwista-CSRF"], body
            )
            self.calls.append(call)
            if path.startswith("/api/admin/"):
                route = path.removeprefix("/api/admin/")
                reason = self._refusal(key)
            else:
                route = path.removeprefix("/api/v1/admin/")
                signed_in = f"session={self.session}" in (cookie or "").split("; ")
                reason = None if signed_in else "not_signed_in"
            if reason:
                return 401, _problem("unauthorized", 401, reason)
            return self._route(method, route, query, body)

    def _refusal(self, key: str | None) -> str | None:
        if self.key is None:
            return "admin_key_not_configured"
        if not key:
            return "admin_key_missing"
        if not hmac.compare_digest(key.encode(), self.key.encode()):
            return "admin_key_invalid"
        return None

    def _route(
        self, method: str, route: str, query: dict[str, str], body: Any
    ) -> tuple[int, Any]:
        if method == "GET" and route == "feedback":
            limit, offset = int(query.get("limit", "50")), int(query.get("offset", "0"))
            if not 1 <= limit <= 200 or offset < 0:
                return 400, _problem("validation_error", 400)
            items = sorted(self.reports.values(), key=lambda r: -int(r["id"]))
            unread = sum(not r["is_read"] for r in items)
            page = items[offset : offset + limit]
            return 200, {"items": page, "total": len(items), "unread_count": unread}
        if route.startswith("feedback/") and method in ("PATCH", "DELETE"):
            report = self.reports.get(int(route.removeprefix("feedback/")))
            if report is None:
                return 404, _problem("not_found", 404)
            if method == "DELETE":
                del self.reports[report["id"]]
                return 200, {"status": "deleted"}
            if not isinstance(body, dict) or not isinstance(body.get("is_read"), bool):
                return 400, _problem("validation_error", 400)
            report["is_read"] = body["is_read"]
            return 200, report
        if method == "GET" and route == "stats":
            start = query.get("from", (TODAY - timedelta(days=29)).isoformat())
            end = query.get("to", TODAY.isoformat())
            days = [d for d in DAYS if start <= d["date"] <= end]
            totals = {k: sum(d[k] for d in days) for k in KEYS[2:]}
            return 200, {"days": days, "totals": totals}
        if method == "GET" and route == "status":
            return 200, STATUS
        if method == "GET" and route == "resources":
            return 200, {"items": ["NMT", "graf zlewni"]}
        return 404, _problem("not_found", 404)


class _Server(http.server.ThreadingHTTPServer):
    api = FakeApi()


class _Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        pass

    def end_headers(self) -> None:
        if not self.path.startswith(API):
            self.send_header("Content-Security-Policy", "default-src 'self'")
        super().end_headers()

    def do_GET(self) -> None:
        if self.path.startswith(API):
            self._api()
        else:
            super().do_GET()

    def do_PATCH(self) -> None:
        self._api()

    def do_DELETE(self) -> None:
        self._api()

    def _api(self) -> None:
        parts = urlsplit(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        query = {k: v[-1] for k, v in parse_qs(parts.query).items()}
        names = ("X-Admin-Key", "Cookie", "X-Archiwista-CSRF")
        headers = {name: self.headers.get(name) for name in names}
        status, doc = cast(_Server, self.server).api.answer(
            self.command, parts.path, query, headers, json.loads(raw) if raw else None
        )
        data = json.dumps(doc).encode()
        self.send_response(status)
        kind = "application/json" if status < 400 else "application/problem+json"
        self.send_header("Content-Type", kind)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


@pytest.fixture(scope="module")
def server(tmp_path_factory: pytest.TempPathFactory) -> Iterator[_Server]:
    """The kit, the marks, the tokens, the specimen and the test pages, with the API."""
    directory = tmp_path_factory.mktemp("admin")
    shutil.copytree(ROOT / "design" / "kit", directory / "kit")
    shutil.copytree(ROOT / "design" / "marks", directory / "marks")
    for name in ("tokens.css", "specimen-admin.html", "specimen-admin.js"):
        shutil.copy(ROOT / "design" / name, directory / name)
    (directory / "admin").mkdir()
    (directory / "admin" / "index.html").write_text(SHELL_PAGE, encoding="utf-8")
    (directory / "admin" / "app.js").write_text(APP_SCRIPT, encoding="utf-8")
    pages = {
        "alone.html": ALONE_PAGE.format(script="watch.js", auth=' auth="session"'),
        "custom.html": ALONE_PAGE.format(script="custom.js", auth=""),
        "watch.js": WATCH_SCRIPT,
        "custom.js": CUSTOM_SCRIPT,
        "session/index.html": SESSION_PAGE,
        "session/session.js": SESSION_SCRIPT,
    }
    (directory / "session").mkdir()
    for name, text in pages.items():
        (directory / name).write_text(text, encoding="utf-8")
    handler = functools.partial(_Handler, directory=str(directory))
    httpd = _Server(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield httpd
    httpd.shutdown()
    thread.join()


@pytest.fixture
def site(server: _Server) -> str:
    return f"127.0.0.1:{server.server_address[1]}"


@pytest.fixture
def api(server: _Server) -> FakeApi:
    """A fresh API for each test."""
    server.api = FakeApi()
    return server.api


@pytest.fixture(scope="module")
def playwright() -> Iterator[Playwright]:
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="module")
def browser(playwright: Playwright) -> Iterator[Browser]:
    browser = playwright.chromium.launch()
    yield browser
    browser.close()


@dataclass
class Tab:
    page: Page
    requested: list[str]


@pytest.fixture
def tabs(browser: Browser, site: str, api: FakeApi) -> Iterator[Callable[..., Tab]]:
    """Open a page in a new context: Polish, Warsaw time, a fixed clock, CSP watched."""
    opened: list[Tab] = []
    problems: list[str] = []

    def note(text: str, kind: str) -> None:
        # Chromium reports each refused request (401, 404) as a console error.
        if kind == "error" and not text.startswith("Failed to load resource"):
            problems.append(text)

    def open_tab(
        path: str = "/admin/", *, width: int = 1280, cookie: bool = False
    ) -> Tab:
        context = browser.new_context(
            viewport={"width": width, "height": 800},
            locale="pl-PL",
            timezone_id="Europe/Warsaw",
            accept_downloads=True,
        )
        if cookie:
            context.add_cookies(
                [{"name": "session", "value": "ok", "url": f"http://{site}/"}]
            )
        page = context.new_page()
        page.clock.set_fixed_time(NOW)
        page.add_init_script(WATCH_CSP)
        tab = Tab(page, [])
        page.on("request", lambda r: tab.requested.append(r.url))
        page.on("console", lambda m: note(m.text, m.type))
        page.on("pageerror", lambda e: problems.append(str(e)))
        page.goto(f"http://{site}{path}")
        opened.append(tab)
        return tab

    yield open_tab
    for tab in opened:
        problems.extend(tab.page.evaluate("window.cspViolations"))
        tab.page.context.close()
    assert problems == []


def _sign_in(page: Page, key: str = KEY) -> None:
    page.get_by_label("Klucz administratora").fill(key)
    page.get_by_role("button", name="Zaloguj", exact=True).click()


def _ids(page: Page) -> list[str]:
    ids: list[str] = page.locator(".nogat-admin-report").evaluate_all(
        "rows => rows.map(row => row.dataset.id)"
    )
    return ids


def _seen(page: Page, kind: str) -> list[Any]:
    found: list[Any] = page.evaluate(
        "kind => seen.filter(([type]) => type === kind).map(([, detail]) => detail)",
        kind,
    )
    return found


# The shell: the prompt, the key and the sections


def test_prompt_checks_a_key_before_keeping_it_for_the_tab(
    tabs: Callable[..., Tab], api: FakeApi, site: str
) -> None:
    page = tabs().page
    field = page.get_by_label("Klucz administratora")
    nav = page.get_by_role("navigation", name="Sekcje panelu")
    expect(field).to_be_focused()
    expect(nav).to_be_hidden()
    expect(page.get_by_role("heading", level=1)).to_have_text(
        "Hydrolog · Administracja"
    )
    back = page.get_by_role("link", name="Wróć do aplikacji")
    expect(back).to_have_attribute("href", f"http://{site}/")
    _sign_in(page, "zly-klucz")
    expect(page.get_by_role("alert")).to_have_text(
        "Nieprawidłowy klucz. Spróbuj ponownie."
    )
    expect(field).to_have_value("")
    expect(field).to_be_focused()
    assert page.evaluate("sessionStorage.length") == 0
    _sign_in(page)
    expect(nav).to_be_visible()
    expect(page.locator(".nogat-admin-report")).to_have_count(50)
    assert page.evaluate("sessionStorage.getItem('hydrolog/admin-key/1')") == KEY
    assert [(c.path, c.query, c.key) for c in api.calls[:2]] == [
        ("/api/admin/feedback", {"limit": "1"}, "zly-klucz"),
        ("/api/admin/feedback", {"limit": "1"}, KEY),
    ]
    assert {c.key for c in api.calls[2:]} == {KEY}
    page.reload()
    expect(page.locator(".nogat-admin-report")).to_have_count(50)
    expect(field).to_be_hidden()


def test_prompt_names_a_missing_key_and_a_server_without_one(
    tabs: Callable[..., Tab], api: FakeApi
) -> None:
    api.key = None
    page = tabs().page
    _sign_in(page, "  ")
    expect(page.get_by_role("alert")).to_have_text("Podaj klucz administratora.")
    assert api.calls == []
    _sign_in(page)
    expect(page.get_by_role("alert")).to_have_text(
        "Serwer nie ma ustawionego klucza administratora."
    )
    expect(page.get_by_role("navigation", name="Sekcje panelu")).to_be_hidden()


def test_a_refused_key_returns_to_the_prompt_and_wyloguj_forgets_the_key(
    tabs: Callable[..., Tab], api: FakeApi
) -> None:
    page = tabs().page
    _sign_in(page)
    expect(page.locator(".nogat-admin-report")).to_have_count(50)
    api.key = "nowy-klucz"
    page.get_by_role("link", name="Statystyki").click()
    expect(page.get_by_role("alert")).to_have_text(
        "Nieprawidłowy klucz. Spróbuj ponownie."
    )
    expect(page.get_by_label("Klucz administratora")).to_be_focused()
    expect(page.get_by_role("navigation", name="Sekcje panelu")).to_be_hidden()
    expect(page.get_by_role("button", name="Wyloguj")).to_be_hidden()
    assert page.locator(".nogat-admin-report").count() == 0
    assert page.evaluate("sessionStorage.length") == 0
    assert _seen(page, "nogat-admin-signout") == [{"reason": "admin_key_invalid"}]
    _sign_in(page, "nowy-klucz")
    expect(page.locator(".nogat-admin-table tbody tr")).to_have_count(30)
    assert page.url.endswith("#stats")
    page.get_by_role("button", name="Wyloguj").click()
    expect(page.get_by_label("Klucz administratora")).to_be_focused()
    expect(page.get_by_role("alert")).to_have_count(0)
    assert page.locator(".nogat-admin-table tbody tr").count() == 0
    assert page.evaluate("sessionStorage.length") == 0
    assert _seen(page, "nogat-admin-signout")[-1] == {"reason": "signout"}


def test_shell_with_session_auth_asks_no_key_and_sends_the_cookie(
    tabs: Callable[..., Tab], api: FakeApi
) -> None:
    signed_out = tabs("/session/").page
    expect(signed_out.locator("nogat-admin-feedback [role=alert]")).to_have_text(
        "Brak dostępu."
    )
    expect(signed_out.get_by_label("Klucz administratora")).to_be_hidden()
    assert _seen(signed_out, "nogat-admin-unauthorized") == [
        {"status": 401, "reason": "not_signed_in"}
    ]
    page = tabs("/session/", cookie=True).page
    expect(page.locator(".nogat-admin-report")).to_have_count(50)
    expect(page.get_by_role("button", name="Wyloguj")).to_be_hidden()
    expect(page.get_by_role("heading", level=1)).to_have_text(
        "Archiwista · Administracja"
    )
    page.get_by_role("link", name="Statystyki").click()
    expect(page.locator(".nogat-admin-table tbody tr")).to_have_count(30)
    assert [(c.path, c.key, c.cookie) for c in api.calls] == [
        ("/api/v1/admin/feedback", None, None),
        ("/api/v1/admin/feedback", None, "session=ok"),
        ("/api/v1/admin/stats", None, "session=ok"),
    ]


def test_an_app_section_follows_the_core_three_and_the_hash_names_the_section(
    tabs: Callable[..., Tab], api: FakeApi
) -> None:
    page = tabs().page
    _sign_in(page)
    nav = page.get_by_role("navigation", name="Sekcje panelu")
    assert nav.get_by_role("link").all_inner_texts() == [
        "Zgłoszenia",
        "Statystyki",
        "Stan",
        "Zasoby",
    ]
    expect(nav.get_by_role("link", name="Zgłoszenia")).to_have_attribute(
        "aria-current", "page"
    )
    nav.get_by_role("link", name="Zasoby").click()
    expect(page.locator("#resources")).to_have_text("NMT, graf zlewni")
    expect(page.locator("nogat-admin-feedback")).to_be_hidden()
    expect(nav.get_by_role("link", name="Zasoby")).to_have_attribute(
        "aria-current", "page"
    )
    assert page.url.endswith("#resources")
    assert [c.key for c in api.calls if c.path == "/api/admin/resources"] == [KEY]
    page.go_back()
    expect(page.locator("nogat-admin-feedback")).to_be_visible()
    expect(page.locator('[data-admin-section="resources"]')).to_be_hidden()
    page.evaluate("() => { document.querySelector('nogat-admin').section = 'status'; }")
    expect(page.locator(".nogat-admin-check")).to_have_count(3)
    page.evaluate("() => { location.hash = '#nie-ma'; }")
    expect(page.locator("nogat-admin-feedback")).to_be_visible()
    assert page.evaluate("document.querySelector('nogat-admin').section") == "feedback"
    assert [d["id"] for d in _seen(page, "nogat-admin-section")] == [
        "feedback",
        "resources",
        "feedback",
        "status",
        "feedback",
    ]


# The views against the API


def test_feedback_shows_fifty_reports_a_page_newest_first_with_the_unread_count(
    tabs: Callable[..., Tab], api: FakeApi
) -> None:
    page = tabs().page
    _sign_in(page)
    reports = page.locator(".nogat-admin-report")
    expect(reports).to_have_count(50)
    expect(page.locator(".nogat-admin-count")).to_have_text("Nieprzeczytane: 20 z 60")
    assert _ids(page) == [str(n) for n in range(60, 10, -1)]
    newest = reports.first.locator("time")
    assert newest.get_attribute("datetime") == "2026-11-11T12:00:00+00:00"
    assert newest.inner_text() == "11.11.2026, 13:00"
    expect(page.locator(".nogat-admin-range")).to_have_text("1–50 z 60")
    expect(page.get_by_role("button", name="Poprzednia strona")).to_be_disabled()
    page.get_by_role("button", name="Następna strona").click()
    expect(reports).to_have_count(10)
    assert _ids(page) == [str(n) for n in range(10, 0, -1)]
    expect(page.locator(".nogat-admin-range")).to_have_text("51–60 z 60")
    expect(page.get_by_role("button", name="Następna strona")).to_be_disabled()
    assert [c.query for c in api.calls if c.query.get("limit") == "50"] == [
        {"limit": "50", "offset": "0"},
        {"limit": "50", "offset": "50"},
    ]


def test_feedback_marks_a_report_read_and_back_and_shows_only_the_unread(
    tabs: Callable[..., Tab], api: FakeApi
) -> None:
    page = tabs().page
    _sign_in(page)
    count = page.locator(".nogat-admin-count")
    report = page.locator('.nogat-admin-report[data-id="60"]')
    expect(report.locator(".nogat-admin-badge")).to_have_text("nowe")
    report.get_by_role("button", name="Oznacz jako przeczytane").click()
    expect(count).to_have_text("Nieprzeczytane: 19 z 60")
    expect(report.locator(".nogat-admin-badge")).to_have_count(0)
    toggle = report.get_by_role("button", name="Oznacz jako nieprzeczytane")
    expect(toggle).to_be_focused()
    toggle.click()
    expect(count).to_have_text("Nieprzeczytane: 20 z 60")
    assert [(c.path, c.body) for c in api.calls if c.method == "PATCH"] == [
        ("/api/admin/feedback/60", {"is_read": True}),
        ("/api/admin/feedback/60", {"is_read": False}),
    ]
    page.get_by_label("Tylko nieprzeczytane").check()
    assert _ids(page) == [str(n) for n in range(60, 10, -1) if n % 3 == 0]
    page.get_by_label("Tylko nieprzeczytane").uncheck()
    expect(page.locator(".nogat-admin-report")).to_have_count(50)


def test_feedback_folds_the_context_and_shows_a_report_as_text(
    tabs: Callable[..., Tab],
) -> None:
    page = tabs().page
    _sign_in(page)
    report = page.locator('.nogat-admin-report[data-id="60"]')
    message = report.locator(".nogat-admin-message")
    expect(message).to_contain_text("się nie ładuje <b>wcale</b> xxx")
    assert message.locator("b").count() == 0
    context = report.locator("details.nogat-admin-context")
    expect(context.locator("dl")).to_be_hidden()
    context.get_by_text("Kontekst").click()
    expect(context.locator("dl")).to_be_visible()
    assert context.locator("dt").all_inner_texts() == [
        "Widok",
        "Stacja",
        "Wersja aplikacji",
        "Parametry widoku",
    ]
    values = context.locator("dd").all_inner_texts()
    assert values[:3] == ["mapa", "150060", "1.2.3"]
    assert json.loads(values[3]) == {"q": 60, "okres": "1h"}
    odd = page.locator('.nogat-admin-report[data-id="59"] dd')
    assert odd.all_text_contents()[1] == "–"


def test_delete_asks_first_keeps_focus_in_the_question_and_escape_cancels(
    tabs: Callable[..., Tab], api: FakeApi
) -> None:
    page = tabs().page
    _sign_in(page)
    remove = page.locator('.nogat-admin-report[data-id="58"]').get_by_role(
        "button", name="Usuń"
    )
    remove.click()
    dialog = page.get_by_role("dialog", name="Usunąć zgłoszenie #58?")
    expect(dialog).to_be_visible()
    expect(dialog.get_by_role("button", name="Anuluj")).to_be_focused()
    focused = (
        "() => document.activeElement.closest('dialog')"
        " && document.activeElement.textContent"
    )
    names = []
    for _ in range(3):
        page.keyboard.press("Tab")
        names.append(page.evaluate(focused))
    page.keyboard.press("Shift+Tab")
    names.append(page.evaluate(focused))
    assert names == ["Usuń", "Anuluj", "Usuń", "Anuluj"]
    page.keyboard.press("Escape")
    expect(dialog).to_be_hidden()
    expect(remove).to_be_focused()
    remove.click()
    expect(dialog).to_be_visible()
    page.mouse.click(5, 5)
    expect(dialog).to_be_hidden()
    assert [c for c in api.calls if c.method == "DELETE"] == []
    remove.click()
    dialog.get_by_role("button", name="Usuń").click()
    expect(page.locator('.nogat-admin-report[data-id="58"]')).to_have_count(0)
    expect(page.locator(".nogat-admin-count")).to_have_text("Nieprzeczytane: 20 z 59")
    expect(page.locator("nogat-admin-feedback > [role=status]")).to_have_text(
        "Usunięto zgłoszenie #58."
    )
    assert _ids(page) == [str(n) for n in range(60, 9, -1) if n != 58]
    expect(
        page.locator('.nogat-admin-report[data-id="57"] button').first
    ).to_be_focused()
    assert [c.path for c in api.calls if c.method == "DELETE"] == [
        "/api/admin/feedback/58"
    ]


def test_stats_shows_the_days_of_a_period_with_totals_and_saves_them_as_csv(
    tabs: Callable[..., Tab], api: FakeApi
) -> None:
    page = tabs("/admin/#stats").page
    _sign_in(page)
    rows = page.locator(".nogat-admin-table tbody tr")
    expect(rows).to_have_count(30)
    assert page.locator(".nogat-admin-table thead th").all_inner_texts() == [
        "Data",
        "Odwiedzający",
        "Odsłony",
        "Otwarte stacje",
        "Obliczenia",
        "Pobrania",
    ]
    shown = DAYS[-30:]
    expect(page.locator(".nogat-admin-table caption")).to_have_text(
        "Dni od 2026-10-15 do 2026-11-13"
    )
    assert rows.first.inner_text().split("\t") == [str(shown[0][k]) for k in KEYS]
    total = page.locator(".nogat-admin-table tfoot tr")
    assert total.locator("th").inner_text() == "Razem"
    cells = total.locator("td").all_inner_texts()
    visitors = sum(d["visitors"] for d in shown)
    assert cells[0] == f"{visitors}\nsuma dziennych odwiedzających"
    assert cells[1:] == [str(sum(d[k] for d in shown)) for k in KEYS[2:]]
    periods = [("7 dni", 7), ("90 dni", 90), ("Cały okres", len(DAYS))]
    for label, days in periods:
        page.get_by_role("button", name=label, exact=True).click()
        expect(rows).to_have_count(days)
        expect(page.get_by_role("button", name=label, exact=True)).to_have_attribute(
            "aria-pressed", "true"
        )
    assert [c.query for c in api.calls if c.path == "/api/admin/stats"] == [
        {"from": start, "to": "2026-11-13"}
        for start in ("2026-10-15", "2026-11-07", "2026-08-16", "1970-01-01")
    ]
    with page.expect_download() as info:
        page.get_by_role("button", name="Pobierz CSV").click()
    download = info.value
    assert download.suggested_filename == "hydrolog-stats-2026-08-01-2026-11-13.csv"
    lines = [",".join(KEYS), *(",".join(str(d[k]) for k in KEYS) for d in DAYS)]
    assert Path(download.path()).read_text(encoding="utf-8") == "\n".join(lines) + "\n"


def test_status_shows_the_server_and_each_check_in_words(
    tabs: Callable[..., Tab],
) -> None:
    page = tabs("/admin/#status").page
    _sign_in(page)
    checks = page.locator(".nogat-admin-check")
    expect(checks).to_have_count(3)
    facts = page.locator(".nogat-admin-facts")
    assert facts.locator("dt").all_inner_texts() == [
        "Aplikacja",
        "Wersja",
        "Uruchomiona",
        "Czas działania",
        "Katalog danych",
        "Wolne miejsce",
    ]
    assert facts.locator("dd").all_inner_texts() == [
        "Hydrolog",
        "1.4.0",
        "11.11.2026, 09:56",
        "2 dni 3 godz. 4 min",
        "/srv/hydrolog",
        "12,3 GB z 100 GB (12%)",
    ]
    badges = checks.locator(".nogat-admin-badge")
    assert badges.all_inner_texts() == ["OK", "Ostrzeżenie", "Błąd"]
    assert badges.evaluate_all("bs => bs.map(b => b.className)") == [
        "nogat-admin-badge nogat-admin-ok",
        "nogat-admin-badge nogat-admin-warning",
        "nogat-admin-badge nogat-admin-failed",
    ]
    assert checks.locator(".nogat-admin-check-name").all_inner_texts() == [
        "data_dir",
        "reports",
        "hydrolog",
    ]
    assert checks.last.locator(".nogat-admin-check-detail").inner_text() == (
        "polecenie nie odpowiada"
    )


# The page: themes, a phone, CSP and what it loads


def test_panel_follows_both_themes(tabs: Callable[..., Tab]) -> None:
    page = tabs().page
    _sign_in(page)
    expect(page.locator(".nogat-admin-report")).to_have_count(50)
    style = (
        "() => [document.body, document.querySelector('.nogat-admin-bar'),"
        " document.querySelector('.nogat-admin-report')]"
        ".map(e => getComputedStyle(e).backgroundColor)"
        ".concat([getComputedStyle(document.querySelector('.nogat-admin-message')).color,"
        " getComputedStyle(document.querySelector('.nogat-admin-app')).color])"
    )
    light = [
        "rgb(250, 248, 248)",
        "rgb(255, 255, 255)",
        "rgb(255, 255, 255)",
        "rgb(43, 43, 43)",
        "rgb(63, 122, 58)",
    ]
    dark = [
        "rgb(13, 17, 23)",
        "rgb(22, 27, 34)",
        "rgb(22, 27, 34)",
        "rgb(230, 237, 243)",
        "rgb(124, 196, 116)",
    ]
    page.emulate_media(color_scheme="light")
    assert page.evaluate(style) == light
    page.emulate_media(color_scheme="dark")
    assert page.evaluate(style) == dark
    page.evaluate("() => { document.documentElement.dataset.theme = 'light'; }")
    assert page.evaluate(style) == light


def test_panel_fits_a_phone_without_scrolling_sideways(
    tabs: Callable[..., Tab],
) -> None:
    page = tabs(width=390).page
    wide = "document.documentElement.scrollWidth"
    assert page.evaluate(wide) <= 390
    _sign_in(page)
    expect(page.locator(".nogat-admin-report")).to_have_count(50)
    expect(page.get_by_role("link", name="Wróć do aplikacji")).to_be_visible()
    page.locator('.nogat-admin-report[data-id="60"]').get_by_text("Kontekst").click()
    assert page.evaluate(wide) <= 390
    for name, ready in (
        ("Statystyki", ".nogat-admin-table tbody tr"),
        ("Stan", ".nogat-admin-check"),
        ("Zasoby", "#resources:not(:empty)"),
    ):
        page.get_by_role("link", name=name, exact=True).click()
        page.locator(ready).first.wait_for()
        assert page.evaluate(wide) <= 390, name
    page.get_by_role("link", name="Zgłoszenia").click()
    page.locator(".nogat-admin-report").first.get_by_role("button", name="Usuń").click()
    box = page.get_by_role("dialog").bounding_box()
    assert box is not None
    assert box["x"] >= 0
    assert box["x"] + box["width"] <= 390


def test_panel_loads_nothing_but_the_kit(tabs: Callable[..., Tab], site: str) -> None:
    tab = tabs()
    page = tab.page
    _sign_in(page)
    expect(page.locator(".nogat-admin-report")).to_have_count(50)
    for name, ready in (
        ("Statystyki", ".nogat-admin-table tbody tr"),
        ("Stan", ".nogat-admin-check"),
        ("Zasoby", "#resources:not(:empty)"),
    ):
        page.get_by_role("link", name=name, exact=True).click()
        page.locator(ready).first.wait_for()
    assert {urlsplit(url).netloc for url in tab.requested} == {site}
    paths = {urlsplit(url).path for url in tab.requested}
    assert sorted(p for p in paths if not p.startswith("/api/")) == [
        "/admin/",
        "/admin/app.js",
        "/kit/nogat-admin.css",
        "/kit/nogat-admin.js",
        "/marks/hydrolog.svg",
        "/tokens.css",
    ]
    assert sorted(p for p in paths if p.startswith("/api/")) == [
        "/api/admin/feedback",
        "/api/admin/resources",
        "/api/admin/stats",
        "/api/admin/status",
    ]


# A view alone, inside an app's own page


def test_feedback_alone_with_session_auth_sends_the_cookie_and_no_key(
    tabs: Callable[..., Tab], api: FakeApi
) -> None:
    signed_out = tabs("/alone.html").page
    expect(signed_out.get_by_role("alert")).to_have_text("Brak dostępu.")
    assert _seen(signed_out, "nogat-admin-unauthorized") == [
        {"status": 401, "reason": "not_signed_in"}
    ]
    page = tabs("/alone.html", cookie=True).page
    expect(page.locator(".nogat-admin-report")).to_have_count(50)
    report = page.locator('.nogat-admin-report[data-id="60"]')
    report.get_by_role("button", name="Oznacz jako przeczytane").click()
    expect(page.locator(".nogat-admin-count")).to_have_text("Nieprzeczytane: 19 z 60")
    assert [(c.method, c.path, c.key, c.cookie) for c in api.calls] == [
        ("GET", "/api/v1/admin/feedback", None, None),
        ("GET", "/api/v1/admin/feedback", None, "session=ok"),
        ("PATCH", "/api/v1/admin/feedback/60", None, "session=ok"),
    ]


def test_feedback_alone_sends_its_requests_through_the_apps_own_function(
    tabs: Callable[..., Tab], api: FakeApi
) -> None:
    page = tabs("/custom.html", cookie=True).page
    expect(page.locator(".nogat-admin-report")).to_have_count(50)
    report = page.locator('.nogat-admin-report[data-id="60"]')
    report.get_by_role("button", name="Oznacz jako przeczytane").click()
    expect(page.locator(".nogat-admin-count")).to_have_text("Nieprzeczytane: 19 z 60")
    assert [(c.method, c.csrf, c.key) for c in api.calls] == [
        ("GET", "zeton", None),
        ("PATCH", "zeton", None),
    ]


# The specimen


def test_specimen_runs_the_panel_on_its_fake_api(
    tabs: Callable[..., Tab], api: FakeApi
) -> None:
    tab = tabs("/specimen-admin.html")
    page = tab.page
    _sign_in(page, "zly")
    expect(page.get_by_role("alert")).to_have_text(
        "Nieprawidłowy klucz. Spróbuj ponownie."
    )
    _sign_in(page, "nogat")
    expect(page.locator(".nogat-admin-report")).to_have_count(50)
    for name, ready in (
        ("Statystyki", ".nogat-admin-table tbody tr"),
        ("Stan", ".nogat-admin-check"),
        ("Zasoby", "#specimen-resources li"),
    ):
        page.get_by_role("link", name=name, exact=True).click()
        page.locator(ready).first.wait_for()
    assert api.calls == []
    assert sorted({urlsplit(url).path for url in tab.requested}) == [
        "/kit/nogat-admin.css",
        "/kit/nogat-admin.js",
        "/marks/hydrolog.svg",
        "/specimen-admin.html",
        "/specimen-admin.js",
        "/tokens.css",
    ]
