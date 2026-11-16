"""The kit's admin panel, design/kit/nogat-admin.js (DEV-15.13, ECO-067).

Every GUI builds its admin page on this shell and answers its core API, so
the routes and answers design/README.md gives the GUIs are those of
DEV-15.13, the views ask those routes, the statistics table has the keys of
DEV-15.11, the prompt knows exactly the refusal reasons of DEV-15.13, the
labels the standard and the README quote are the kit's own, and every
attribute the elements observe and every event they fire is documented.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (ROOT / "design" / "kit" / "nogat-admin.js").read_text(encoding="utf-8")
README = (ROOT / "design" / "README.md").read_text(encoding="utf-8")
STANDARD = (ROOT / "standards" / "DEVELOPMENT_STANDARDS.md").read_text(encoding="utf-8")


def _block(text: str, start: str, end: str) -> str:
    found = re.search(rf"^{start}.*?(?=^{end})", text, re.MULTILINE | re.DOTALL)
    assert found is not None, f"{start} not found"
    return found.group()


RULE = _block(STANDARD, r"\*\*DEV-15\.13\*\*", r"---$")
STATS_RULE = _block(STANDARD, r"\*\*DEV-15\.11\*\*", r"\*\*DEV-15\.12\*\*")
SECTION = _block(README, r"Admin panel \(DEV-15\.13", r"## ")
# Every double-quoted string of the kit's module.
STRINGS = set(re.findall(r'"((?:[^"\\\n]|\\.)*)"', SCRIPT))
ROUTE_ROW = re.compile(
    r"^\| (?P<route>`(?:GET|PATCH|DELETE) [^|]+) \| (?P<answer>.+) \|$", re.MULTILINE
)


def _routes(text: str) -> list[tuple[str, str]]:
    return [(m["route"], m["answer"]) for m in ROUTE_ROW.finditer(text)]


def _const(name: str) -> str:
    found = re.search(
        rf"^export const {name} = (?P<value>.+?);$", SCRIPT, re.MULTILINE | re.DOTALL
    )
    assert found is not None, f"{name} not found"
    return found["value"]


def _protected(text: str) -> list[str]:
    """The paths of the sentence "… protects exactly `a`, `b` and `c` …"."""
    paths = r"protects exactly (?P<paths>`[^`]+`(?:(?:, | and )`[^`]+`)*)"
    sentence = re.search(paths, " ".join(text.split()))
    assert sentence is not None
    return re.findall(r"`(/[^`]*)`", sentence["paths"])


def test_the_readme_gives_the_core_routes_and_answers_of_dev_15_13() -> None:
    routes = _routes(RULE)
    assert [route.split("`")[1] for route, _ in routes] == [
        "GET /api/admin/feedback?limit=&offset=",
        "PATCH /api/admin/feedback/{id}",
        "DELETE /api/admin/feedback/{id}",
        "GET /api/admin/stats?from=&to=",
        "GET /api/admin/status",
    ]
    assert _routes(SECTION) == routes


def test_the_readme_protects_the_paths_dev_15_13_names() -> None:
    assert _protected(RULE) == ["/admin", "/admin/*", "/api/admin/*"]
    assert _protected(SECTION) == _protected(RULE)


def test_the_views_ask_the_core_routes_from_the_page_at_admin() -> None:
    api = _const("ADMIN_API").strip('"')
    readings = {
        urlsplit(route.split("`")[1].split(" ")[1]).path
        for route, _ in _routes(RULE)
        if route.startswith("`GET")
    }
    views = re.findall(r'static route = "(\w+)";', SCRIPT)
    assert views == ["feedback", "stats", "status"]
    page = "https://gui.example/admin/"
    assert {urlsplit(urljoin(page, api + view)).path for view in views} == readings


def test_the_stats_table_has_the_keys_of_dev_15_11_with_the_readmes_headings() -> None:
    keys = re.findall(r"^\| `(\w+)` \|", STATS_RULE, re.MULTILINE)
    columns = re.findall(r'\["(\w+)", "([^"]+)"\]', _const("STATS_COLUMNS"))
    assert [key for key, _ in columns] == keys
    assert keys[0] == "date"
    for _, heading in columns:
        assert f"„{heading}”" in SECTION


def test_the_prompt_knows_exactly_the_reasons_of_dev_15_13() -> None:
    named = re.findall(r"`(admin_key_\w+)`", RULE)
    known = re.findall(r"^  (admin_key_\w+): ", _const("ADMIN_REASONS"), re.MULTILINE)
    assert sorted(known) == sorted(set(named))
    assert len(known) == 3


def test_the_labels_of_the_standard_are_the_kits() -> None:
    rule = " ".join(RULE.split())
    navigation = [
        re.search(rf'^  {key}: "([^"]+)",$', SCRIPT, re.MULTILINE)
        for key in ("feedback", "stats", "status")
    ]
    labels = [found.group(1) for found in navigation if found is not None]
    assert labels == ["Zgłoszenia", "Statystyki", "Stan"]
    assert f"„{labels[0]}”, „{labels[1]}” and „{labels[2]}”" in rule
    assert "„Wyloguj”" in rule
    assert "Wyloguj" in STRINGS


def test_every_label_the_readme_quotes_is_the_kits() -> None:
    quoted = re.findall(r"„([^”]+)”", SECTION)
    assert quoted
    assert [text for text in quoted if text not in STRINGS] == []


def test_the_readme_documents_every_attribute_and_event() -> None:
    observed = re.findall(r"static observedAttributes = \[(?P<names>[^\]]+)\]", SCRIPT)
    names = {name for found in observed for name in re.findall(r'"([a-z-]+)"', found)}
    assert names == {"endpoint", "auth", "app", "project", "back", "api", "marks"}
    for name in names:
        assert f"| `{name}`" in SECTION
    events = set(re.findall(r'new CustomEvent\("([a-z-]+)"', SCRIPT))
    assert events == {
        "nogat-admin-section",
        "nogat-admin-signout",
        "nogat-admin-unauthorized",
    }
    for event in events:
        assert f"| `{event}` |" in SECTION
