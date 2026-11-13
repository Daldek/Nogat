"""The GUI kit in a browser: design/kit/ (DEV-15.4, DEV-15.5, DEV-15.7, DEV-20.5).

The kit is plain ES modules copied by every GUI, so it is tested where it
runs: Chromium through Playwright, on pages served from a throwaway
directory over HTTP. The schema checks of `nogat-handoff.js` are compared
with the Python `jsonschema` validator on the same documents. The terms page
is filled by the reference `fill`; it and the sources strip are served under
CSP `'self'`.
"""

from __future__ import annotations

import copy
import functools
import http.server
import json
import re
import shutil
import threading
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import jsonschema
import pytest
import terms
from playwright.sync_api import Browser, Locator, Page, Playwright, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
ENVELOPE: dict[str, Any] = json.loads(
    (ROOT / "schemas" / "exchange" / "handoff-1.schema.json").read_text(
        encoding="utf-8"
    )
)
INSECURE_HOST = "nogat.test"

PAGE = """<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="kit/nogat-app-menu.css">
<script type="module" src="kit/nogat-app-menu.js"></script>
</head>
<body>
<header><span id="before" tabindex="0">przed</span>
<nogat-app-menu current="hydrolog" marks="marks/"></nogat-app-menu></header>
<main><textarea id="field" hidden></textarea></main>
</body>
</html>
"""

SOURCES_PAGE = """<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="tokens.css">
<link rel="stylesheet" href="kit/nogat-sources.css">
<script type="module" src="kit/nogat-sources.js"></script>
</head>
<body>
<main><nogat-sources terms="regulamin.html"></nogat-sources>
<section id="welcome"></section></main>
</body>
</html>
"""

# The lines of the table of DEV §20, byte for byte.
LINES = {
    m["mark"]: m["line"]
    for m in re.finditer(
        r"^\| (?P<mark>[A-Z]{1,2}) \| (?P<line>.+) \|$",
        (ROOT / "standards" / "DEVELOPMENT_STANDARDS.md").read_text(encoding="utf-8"),
        re.MULTILINE,
    )
}
CP = "Dane ČHMÚ zostały przetworzone (agregacja do dobowych sum)"
OTHER = "Źródło: GUGiK"


TERMS_VALUES = {
    "service_name": "Hydrolog",
    "service_url": "./",
    "operator_name": "Jan Kowalski",
    "operator_email": "jan@example.org",
    "terms_effective": "2026-11-20",
    "processor": "Cloudflare, Inc.",
    "processor_transfer": "Dane mogą być przekazywane do USA.",
    "processor_cookie": "",
    "mail_provider": "Example Mail",
    "mail_transfer": "",
    "software_licence": "MIT",
    "source_url": "https://github.com/Daldek/Hydrolog",
    "tokens_href": "tokens.css",
    "kit_href": "kit/",
}


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        pass

    def end_headers(self) -> None:
        if self.path.startswith(("/regulamin.html", "/sources.html")):
            self.send_header("Content-Security-Policy", "default-src 'self'")
        super().end_headers()


@pytest.fixture(scope="module")
def site(tmp_path_factory: pytest.TempPathFactory) -> Iterator[str]:
    """Base URL of the kit, marks and a test page, served over HTTP."""
    directory = tmp_path_factory.mktemp("site")
    shutil.copytree(ROOT / "design" / "kit", directory / "kit")
    shutil.copytree(ROOT / "design" / "marks", directory / "marks")
    shutil.copy(ROOT / "design" / "tokens.css", directory / "tokens.css")
    (directory / "page.html").write_text(PAGE, encoding="utf-8")
    (directory / "sources.html").write_text(SOURCES_PAGE, encoding="utf-8")
    template = (ROOT / "design" / "kit" / "nogat-terms.html").read_text(
        encoding="utf-8"
    )
    (directory / "regulamin.html").write_text(
        terms.fill(template, TERMS_VALUES, list(terms.BLOCKS)), encoding="utf-8"
    )
    handler = functools.partial(_Quiet, directory=str(directory))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    thread.join()


@pytest.fixture(scope="module")
def playwright() -> Iterator[Playwright]:
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="module")
def browser(playwright: Playwright) -> Iterator[Browser]:
    # nogat.test resolves to 127.0.0.1 but is not a secure context, like a LAN address.
    browser = playwright.chromium.launch(
        args=[f"--host-resolver-rules=MAP {INSECURE_HOST} 127.0.0.1"]
    )
    yield browser
    browser.close()


@pytest.fixture
def page(browser: Browser, site: str) -> Iterator[Page]:
    context = browser.new_context(
        permissions=["clipboard-read", "clipboard-write"], accept_downloads=True
    )
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(f"http://{site}/page.html")
    page.wait_for_function("customElements.get('nogat-app-menu') !== undefined")
    yield page
    context.close()
    assert errors == []


def _set_apps(page: Page, apps: dict[str, str]) -> None:
    page.evaluate(
        "apps => { document.querySelector('nogat-app-menu').apps = apps; }", apps
    )


def _handoff(page: Page, script: str, *args: Any) -> Any:
    """Run `script` (a function of the module `h` and `args`) in the page."""
    return page.evaluate(
        f"async args => {{ const h = await import('/kit/nogat-handoff.js'); "
        f"return ({script})(h, ...args); }}",
        list(args),
    )


# The app menu (DEV-15.4)

APPS = {
    "hydrograf": "https://hydrograf.example/",
    "hydrolog": "http://127.0.0.1:8070/",
    "archiwista": "https://archiwista.example/",
}


def test_menu_is_not_drawn_without_another_gui(page: Page) -> None:
    menu = page.locator("nogat-app-menu")
    assert menu.is_hidden()
    _set_apps(page, {"hydrolog": "http://127.0.0.1:8070/"})
    assert menu.is_hidden()
    _set_apps(page, {"Hydrograf": "javascript:alert(1)", "archiwista": "ftp://x/"})
    assert menu.is_hidden()


def test_menu_resolves_a_path_against_the_page(page: Page, site: str) -> None:
    _set_apps(page, {"archiwista": "/archiwista/"})
    page.get_by_role("button", name="Aplikacje").click()
    link = page.locator("a.nogat-app-menu-item")
    assert link.evaluate("a => a.href") == f"http://{site}/archiwista/"


def test_menu_lists_the_table_in_order_with_the_current_gui_not_a_link(
    page: Page,
) -> None:
    _set_apps(page, APPS)
    page.get_by_role("button", name="Aplikacje").click()
    items = page.locator(".nogat-app-menu-item")
    assert items.all_inner_texts() == [
        "Hydrograf\nZlewnie i hydrogramy na mapie",
        "Hydrolog\nTa aplikacja",
        "Archiwista\nMagazyny danych: mapa, katalog, stacje",
    ]
    links = page.locator("a.nogat-app-menu-item")
    assert [
        (link.get_attribute("href"), link.get_attribute("target"))
        for link in links.all()
    ] == [
        ("https://hydrograf.example/", "nogat-hydrograf"),
        ("https://archiwista.example/", "nogat-archiwista"),
    ]
    assert page.locator('[aria-current="page"]').inner_text().startswith("Hydrolog")


def test_menu_takes_the_table_from_the_apps_attribute(page: Page) -> None:
    page.evaluate(
        "apps => document.querySelector('nogat-app-menu')"
        ".setAttribute('apps', JSON.stringify(apps))",
        {"obserwator": "http://127.0.0.1:8000/"},
    )
    page.get_by_role("button", name="Aplikacje").click()
    assert page.locator("a.nogat-app-menu-item").get_attribute("href") == (
        "http://127.0.0.1:8000/"
    )


def test_menu_closes_on_escape_outside_click_and_focus_leaving(page: Page) -> None:
    _set_apps(page, APPS)
    button = page.get_by_role("button", name="Aplikacje")
    listing = page.locator(".nogat-app-menu-list")
    button.click()
    assert listing.is_visible()
    assert button.get_attribute("aria-expanded") == "true"
    page.keyboard.press("Escape")
    assert listing.is_hidden()
    assert page.evaluate("document.activeElement.textContent") == "Aplikacje"
    button.click()
    page.mouse.click(5, 300)
    assert listing.is_hidden()
    button.click()
    page.locator("#before").focus()
    assert listing.is_hidden()
    assert button.get_attribute("aria-expanded") == "false"


def _opens_in_a_new_tab(page: Page, link: Locator, address: str) -> None:
    """A click on `link` opens `address` in a new tab, no opener; `page` stays."""
    assert (link.get_attribute("target"), link.get_attribute("rel")) == (
        "_blank",
        "noopener",
    )
    before = page.url
    with page.context.expect_page() as info:
        link.click()
    tab = info.value
    tab.wait_for_load_state()
    assert tab.url == address
    assert tab.evaluate("window.opener") is None
    tab.close()
    assert page.url == before


def test_menu_ends_with_the_terms_link_when_given(page: Page, site: str) -> None:
    _set_apps(page, APPS)
    page.get_by_role("button", name="Aplikacje").click()
    assert page.locator(".nogat-app-menu-terms").count() == 0
    page.evaluate(
        "() => document.querySelector('nogat-app-menu')"
        ".setAttribute('terms', 'regulamin.html')"
    )
    page.get_by_role("button", name="Aplikacje").click()
    link = page.get_by_role("link", name="Regulamin")
    _opens_in_a_new_tab(page, link, f"http://{site}/regulamin.html")
    page.evaluate(
        "() => document.querySelector('nogat-app-menu')"
        ".setAttribute('terms', 'javascript:alert(1)')"
    )
    assert page.locator(".nogat-app-menu-terms").count() == 0


def test_menu_keeps_only_its_icon_on_a_phone(page: Page) -> None:
    _set_apps(page, APPS)
    page.set_viewport_size({"width": 390, "height": 800})
    assert page.locator(".nogat-app-menu-label").is_hidden()
    page.get_by_role("button", name="Aplikacje").click()
    box = page.locator(".nogat-app-menu-list").bounding_box()
    assert box is not None
    assert box["x"] == 8
    assert box["width"] == 390 - 16


# The terms page (DEV-15.7)


@pytest.fixture
def terms_page(browser: Browser, site: str) -> Iterator[tuple[Page, list[str]]]:
    """The filled terms page and the addresses it requested; no console error."""
    context = browser.new_context()
    page = context.new_page()
    requested: list[str] = []
    problems: list[str] = []
    page.on("request", lambda r: requested.append(r.url))
    page.on("console", lambda m: problems.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: problems.append(str(e)))
    page.goto(f"http://{site}/regulamin.html")
    yield page, requested
    context.close()
    assert problems == []


def test_terms_page_shows_twelve_sections_with_every_field_filled(
    terms_page: tuple[Page, list[str]], site: str
) -> None:
    page, requested = terms_page
    assert page.title() == "Regulamin serwisu Hydrolog"
    sections = page.locator("main h2").all_inner_texts()
    assert [s.split(".")[0] for s in sections] == [
        *(str(n) for n in range(1, 13)),
        "Historia zmian",
    ]
    text = page.locator("body").inner_text()
    assert "{{" not in text
    assert "Jan Kowalski" in text
    assert page.get_by_role("link", name="jan@example.org").first.get_attribute(
        "href"
    ) == ("mailto:jan@example.org")
    assert {url.split("/")[2] for url in requested} == {site}
    assert sorted(url.rsplit("/", 1)[1] for url in requested) == [
        "nogat-terms.css",
        "regulamin.html",
        "tokens.css",
    ]


def test_terms_page_is_styled_in_both_themes(
    terms_page: tuple[Page, list[str]],
) -> None:
    page, _ = terms_page
    main = page.locator("main.nogat-terms")
    assert main.evaluate("e => getComputedStyle(e).maxWidth") == "768px"
    background = "e => getComputedStyle(document.body).backgroundColor"
    page.emulate_media(color_scheme="light")
    assert main.evaluate(background) == "rgb(250, 248, 248)"
    page.emulate_media(color_scheme="dark")
    assert main.evaluate(background) == "rgb(13, 17, 23)"


# The sources strip (DEV-20.5, DEV-20.7, ECO-064)


@pytest.fixture
def sources(browser: Browser, site: str) -> Iterator[tuple[Page, list[str]]]:
    """The strip's page at 1440 px under CSP `'self'`, and the addresses it requested.

    A CSP violation, a console error or an uncaught exception fails the test.
    """
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()
    requested: list[str] = []
    problems: list[str] = []
    page.on("request", lambda r: requested.append(r.url))
    page.on("console", lambda m: problems.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: problems.append(str(e)))
    page.goto(f"http://{site}/sources.html")
    page.wait_for_function("customElements.get('nogat-sources') !== undefined")
    yield page, requested
    context.close()
    assert problems == []


def _lines(page: Page, attribution: list[str], notice: list[str]) -> None:
    page.evaluate(
        "([a, n]) => { const s = document.querySelector('nogat-sources');"
        " s.attribution = a; s.termsNotice = n; }",
        [attribution, notice],
    )


def _strip_lines(page: Page) -> int:
    """The number of text lines the strip takes."""
    height, line = page.locator(".nogat-sources-strip").evaluate(
        "e => [e.getBoundingClientRect().height,"
        " parseFloat(getComputedStyle(e).lineHeight)]"
    )
    return round(float(height) / float(line))


IMGW = [LINES[m] for m in ("S", "P", "H")]
PMAXTP = [LINES[m] for m in ("PS", "PP", "M")]
NOTICE = [LINES[m] for m in ("N", "RD", "RH", "RK")]


def test_strip_shows_the_on_screen_lines_once_in_order(
    sources: tuple[Page, list[str]],
) -> None:
    page, _ = sources
    full = [OTHER, LINES["C"], CP, *reversed(PMAXTP), *IMGW, LINES["S"]]
    _lines(page, full, NOTICE)
    strip = page.locator(".nogat-sources-strip")
    assert page.locator(".nogat-sources-line").all_text_contents() == [
        *(LINES[m] for m in ("S", "P", "PS", "PP", "CK")),
    ]
    assert strip.evaluate("e => getComputedStyle(e).fontSize") == "12px"
    assert page.get_by_role("button", name="Źródła i warunki").is_visible()
    links = page.locator(".nogat-sources-line a")
    assert [(a.text_content(), a.get_attribute("href")) for a in links.all()] == [
        ("https://klimat.imgw.pl/opady-maksymalne",) * 2,
        ("https://klimat.imgw.pl/opady-maksymalne",) * 2,
        ("ČHMÚ", "https://opendata.chmi.cz"),
        ("CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/"),
    ]


@pytest.mark.parametrize(
    ("attribution", "most"),
    [
        ([*IMGW, LINES["C"]], 2),
        ([*PMAXTP, LINES["C"]], 2),
        ([*IMGW, *PMAXTP, LINES["C"], CP], 3),
    ],
    ids=["imgw-chmi", "pmaxtp-chmi", "both-families-chmi"],
)
def test_strip_takes_at_most_two_lines_per_imgw_family_at_1440_px(
    sources: tuple[Page, list[str]], attribution: list[str], most: int
) -> None:
    page, _ = sources
    _lines(page, attribution, NOTICE)
    assert _strip_lines(page) <= most


def test_strip_takes_the_lines_from_the_attributes_and_hides_without_any(
    sources: tuple[Page, list[str]],
) -> None:
    page, _ = sources
    element = page.locator("nogat-sources")
    assert element.is_hidden()
    page.evaluate(
        "([a, n]) => { const s = document.querySelector('nogat-sources');"
        " s.setAttribute('attribution', JSON.stringify(a));"
        " s.setAttribute('terms-notice', JSON.stringify(n)); }",
        [[LINES["H"]], NOTICE[:3]],
    )
    assert page.locator(".nogat-sources-line").count() == 0
    page.get_by_role("button", name="Źródła i warunki").click()
    assert page.locator("dialog li").all_text_contents() == [LINES["H"], *NOTICE[:3]]
    page.keyboard.press("Escape")
    page.evaluate(
        "() => { const s = document.querySelector('nogat-sources');"
        " s.setAttribute('attribution', '{nie'); s.removeAttribute('terms-notice'); }"
    )
    assert element.is_hidden()


def test_dialog_shows_every_line_and_the_terms_and_traps_focus(
    sources: tuple[Page, list[str]], site: str
) -> None:
    page, _ = sources
    full = [*IMGW, *PMAXTP, LINES["C"], CP]
    _lines(page, full, NOTICE)
    page.evaluate(
        "() => { window.seen = []; for (const t of ['nogat-sources-open',"
        " 'nogat-sources-close']) document.addEventListener(t, () => seen.push(t)); }"
    )
    button = page.get_by_role("button", name="Źródła i warunki")
    button.click()
    dialog = page.get_by_role("dialog", name="Źródła danych i warunki korzystania")
    assert dialog.is_visible()
    assert dialog.locator("li").all_text_contents() == [*full, *NOTICE]
    regulamin = dialog.get_by_role("link", name="Regulamin serwisu")
    assert regulamin.evaluate("a => a.href") == f"http://{site}/regulamin.html"
    inside = "() => !!document.activeElement.closest('dialog')"
    for _ in range(dialog.locator("a, button").count() + 2):
        page.keyboard.press("Tab")
        assert page.evaluate(inside)
    page.keyboard.press("Shift+Tab")
    assert page.evaluate(inside)
    page.keyboard.press("Escape")
    assert dialog.is_hidden()
    assert page.evaluate("document.activeElement.textContent") == "Źródła i warunki"
    button.click()
    dialog.get_by_role("button", name="Zamknij").click()
    assert dialog.is_hidden()
    button.click()
    page.mouse.click(5, 5)
    assert dialog.is_hidden()
    assert page.evaluate("seen") == ["nogat-sources-open", "nogat-sources-close"] * 3
    button.click()
    _opens_in_a_new_tab(page, regulamin, f"http://{site}/regulamin.html")
    assert dialog.is_visible()


def test_welcome_window_gets_the_dialogs_content(
    sources: tuple[Page, list[str]],
) -> None:
    page, _ = sources
    full = [*IMGW, LINES["C"]]
    _lines(page, full, NOTICE)
    page.evaluate(
        "async ([a, n]) => { const m = await import('/kit/nogat-sources.js');"
        " m.fillSources(document.getElementById('welcome'),"
        " {attribution: a, termsNotice: n, terms: 'javascript:alert(1)'}); }",
        [full, NOTICE],
    )
    welcome = page.locator("#welcome")
    assert welcome.locator("li").all_text_contents() == [*full, *NOTICE]
    assert welcome.locator(".nogat-sources-regulamin").count() == 0
    page.get_by_role("button", name="Źródła i warunki").click()
    body = page.locator("dialog .nogat-sources-content")
    assert body.locator("li").all_text_contents() == [*full, *NOTICE]


def test_strip_and_dialog_follow_both_themes(sources: tuple[Page, list[str]]) -> None:
    page, _ = sources
    _lines(page, IMGW, NOTICE)
    page.get_by_role("button", name="Źródła i warunki").click()
    style = (
        "() => [getComputedStyle(document.querySelector('.nogat-sources-strip')).color,"
        " getComputedStyle(document.querySelector('dialog')).backgroundColor,"
        " getComputedStyle(document.querySelector('dialog')).color]"
    )
    page.emulate_media(color_scheme="light")
    assert page.evaluate(style) == [
        "rgb(107, 101, 101)",
        "rgb(255, 255, 255)",
        "rgb(43, 43, 43)",
    ]
    page.emulate_media(color_scheme="dark")
    assert page.evaluate(style) == [
        "rgb(139, 148, 158)",
        "rgb(22, 27, 34)",
        "rgb(230, 237, 243)",
    ]


def test_strip_wraps_and_dialog_fits_a_phone(sources: tuple[Page, list[str]]) -> None:
    page, _ = sources
    page.set_viewport_size({"width": 390, "height": 800})
    _lines(page, [*IMGW, *PMAXTP, LINES["C"]], NOTICE)
    assert _strip_lines(page) > 3
    assert page.evaluate("document.documentElement.scrollWidth") <= 390
    page.get_by_role("button", name="Źródła i warunki").click()
    box = page.locator("dialog").bounding_box()
    assert box is not None
    assert box["x"] >= 0
    assert box["x"] + box["width"] <= 390
    assert box["y"] >= 0
    assert box["y"] + box["height"] <= 800
    last = page.locator("dialog .nogat-sources-regulamin a")
    last.scroll_into_view_if_needed()
    assert last.is_visible()


def test_strip_loads_nothing_but_the_kit(
    sources: tuple[Page, list[str]], site: str
) -> None:
    page, requested = sources
    _lines(page, [*IMGW, *PMAXTP, LINES["C"]], NOTICE)
    page.get_by_role("button", name="Źródła i warunki").click()
    assert {url.split("/")[2] for url in requested} == {site}
    assert sorted(url.rsplit("/", 1)[1] for url in requested) == [
        "nogat-sources.css",
        "nogat-sources.js",
        "sources.html",
        "tokens.css",
    ]


# The hand-off (DEV-15.5)


@pytest.mark.parametrize(
    ("subject", "name"),
    [
        ("Kamiennik — Świerzawa", "Kamiennik — Świerzawa.handoff.json"),
        ('a/b\\c:d*e?f"g<h>i|j', "a-b-c-d-e-f-g-h-i-j.handoff.json"),
        ("  dwa   słowa  ", "dwa słowa.handoff.json"),
        ("tab\t\nnowa", "tab-nowa.handoff.json"),
        ("x\u0000\u001fy", "x-y.handoff.json"),
        ("", "hydrograf.handoff.json"),
        (" /// ", "-.handoff.json"),
    ],
)
def test_file_name_of_a_handoff(page: Page, subject: str, name: str) -> None:
    assert _handoff(page, "(h, s) => h.fileName(s, 'hydrograf')", subject) == name


def test_download_writes_two_space_json_with_a_final_newline(page: Page) -> None:
    doc = ENVELOPE["examples"][0]
    with page.expect_download() as info:
        name = _handoff(page, "(h, d) => h.downloadHandoff(d)", doc)
    download = info.value
    assert download.suggested_filename == name == "Kamiennik — Świerzawa.handoff.json"
    text = download.path().read_text(encoding="utf-8")
    assert json.loads(text) == doc
    assert text.startswith('{\n  "schema": "nogat-handoff/1",\n  "created_at"')
    assert text.endswith("\n}\n")


def test_copy_uses_the_clipboard_in_a_secure_context(page: Page) -> None:
    doc = ENVELOPE["examples"][0]
    where = _handoff(
        page, "(h, d) => h.copyHandoff(d, document.getElementById('field'))", doc
    )
    assert where == "clipboard"
    assert page.locator("#field").is_hidden()
    text = _handoff(page, "h => h.readClipboard()")
    assert json.loads(text) == doc
    assert text.endswith("}\n")


def test_copy_falls_back_to_a_selected_field_without_a_secure_context(
    browser: Browser, site: str
) -> None:
    context = browser.new_context()
    page = context.new_page()
    page.goto(f"http://{site.replace('127.0.0.1', INSECURE_HOST)}/page.html")
    assert page.evaluate("isSecureContext") is False
    doc = ENVELOPE["examples"][0]
    where = _handoff(
        page, "(h, d) => h.copyHandoff(d, document.getElementById('field'))", doc
    )
    assert where == "field"
    field = page.locator("#field")
    assert field.is_visible()
    selected = page.evaluate(
        "() => { const f = document.getElementById('field');"
        " return f.value.slice(f.selectionStart, f.selectionEnd); }"
    )
    assert json.loads(selected) == doc
    assert _handoff(page, "h => h.readClipboard()") is None
    with pytest.raises(Exception, match="clipboard unavailable"):
        _handoff(page, "(h, d) => h.copyHandoff(d)", doc)
    context.close()


def test_read_handoff_names_what_is_not_a_handoff(page: Page) -> None:
    read = "(h, text, schema) => h.readHandoff(text, schema)"
    bad_json = _handoff(page, read, "{nie json", ENVELOPE)
    assert bad_json["doc"] is None
    assert bad_json["problems"][0]["keyword"] == "json"
    assert bad_json["problems"][0]["message"].startswith("To nie jest tekst JSON")
    other = _handoff(page, read, '{"schema": "hydrolog-network/1"}', ENVELOPE)
    assert other["problems"] == [
        {
            "path": "",
            "keyword": "schema",
            "message": "To nie jest przekazanie nogat-handoff/1.",
        }
    ]
    doc = copy.deepcopy(ENVELOPE["examples"][0])
    del doc["subject"]
    doc["producer"]["tool"] = "Hydrograf"
    result = _handoff(page, read, json.dumps(doc), ENVELOPE)
    assert result["doc"]["schema"] == "nogat-handoff/1"
    assert sorted((p["path"], p["message"]) for p in result["problems"]) == [
        ("", "brak pola „subject”"),
        ("/producer/tool", "niezgodne ze wzorem ^[a-z][a-z0-9]*$"),
    ]


def test_labels_name_the_target_in_its_case(page: Page) -> None:
    labels = _handoff(
        page,
        "h => [h.TEXTS.copyTo('hydrolog'), h.TEXTS.loadFrom('archiwista'),"
        " h.TEXTS.open('archiwista'), h.TEXTS.open('nowy')]",
    )
    assert labels == [
        "Kopiuj do Hydrologa",
        "Wczytaj z Archiwisty",
        "Otwórz Archiwistę",
        "Otwórz Nowy",
    ]


# The schema check, against Python's jsonschema

KEYWORDS: dict[str, Any] = {
    "$defs": {"id": {"type": "string", "pattern": "^\\w[\\w.-]*$", "maxLength": 8}},
    "type": "object",
    "required": ["kind"],
    "properties": {
        "kind": {"enum": ["a", "b", {"c": [1]}]},
        "fixed": {"const": {"x": [1, 2]}},
        "count": {"type": "integer", "minimum": 1, "maximum": 9},
        "share": {"type": "number", "exclusiveMinimum": 0, "exclusiveMaximum": 1},
        "step": {"multipleOf": 0.5},
        "name": {"type": "string", "minLength": 2, "maxLength": 3},
        "id": {"$ref": "#/$defs/id"},
        "ids": {"type": "array", "items": {"$ref": "#/$defs/id"}, "uniqueItems": True},
        "pair": {
            "type": "array",
            "prefixItems": [{"type": "string"}, {"type": "number"}],
            "items": False,
            "minItems": 2,
        },
        "nested": {
            "type": "object",
            "additionalProperties": False,
            "properties": {"a": {"type": ["string", "null"]}},
            "patternProperties": {"^x_": {"type": "boolean"}},
            "propertyNames": {"maxLength": 4},
            "maxProperties": 2,
        },
        "either": {"anyOf": [{"type": "string"}, {"type": "number", "minimum": 10}]},
        "one": {"oneOf": [{"type": "integer"}, {"type": "number", "minimum": 5}]},
        "never": {"not": {"type": "string"}},
        "shape": {
            "type": "object",
            "if": {"properties": {"k": {"const": "circle"}}},
            "then": {"required": ["r"]},
            "else": {"required": ["w"]},
        },
        "all": {"allOf": [{"minLength": 1}, {"pattern": "^[ąę]+$"}]},
    },
    "dependentRequired": {"count": ["name"]},
}

KEYWORD_CASES: list[Any] = [
    {"kind": "a"},
    {"kind": {"c": [1]}},
    {"kind": {"c": [2]}},
    {},
    [],
    {"kind": "a", "fixed": {"x": [1, 2]}},
    {"kind": "a", "fixed": {"x": [2, 1]}},
    {"kind": "a", "count": 3, "name": "ab"},
    {"kind": "a", "count": 3},
    {"kind": "a", "count": 3.0, "name": "ab"},
    {"kind": "a", "count": 3.5, "name": "ab"},
    {"kind": "a", "count": 0, "name": "ab"},
    {"kind": "a", "count": 10, "name": "ab"},
    {"kind": "a", "share": 0},
    {"kind": "a", "share": 0.5},
    {"kind": "a", "share": 1},
    {"kind": "a", "step": 2.5},
    {"kind": "a", "step": 2.3},
    {"kind": "a", "name": "a"},
    {"kind": "a", "name": "abcd"},
    {"kind": "a", "name": "😀😀"},
    {"kind": "a", "id": "Z1"},
    {"kind": "a", "id": "-Z1"},
    {"kind": "a", "id": "Zbyt_dlugie"},
    {"kind": "a", "ids": ["Z1", "Z2"]},
    {"kind": "a", "ids": ["Z1", "Z1"]},
    {"kind": "a", "ids": ["Z1", 2]},
    {"kind": "a", "pair": ["x", 1]},
    {"kind": "a", "pair": ["x", "y"]},
    {"kind": "a", "pair": ["x", 1, 2]},
    {"kind": "a", "pair": ["x"]},
    {"kind": "a", "nested": {"a": None, "x_on": True}},
    {"kind": "a", "nested": {"a": 1}},
    {"kind": "a", "nested": {"b": "?"}},
    {"kind": "a", "nested": {"x_on": "tak"}},
    {"kind": "a", "nested": {"x_long": True}},
    {"kind": "a", "nested": {"a": "", "x_1": True, "x_2": False}},
    {"kind": "a", "either": "x"},
    {"kind": "a", "either": 12},
    {"kind": "a", "either": 3},
    {"kind": "a", "one": 3},
    {"kind": "a", "one": 5.5},
    {"kind": "a", "one": 6},
    {"kind": "a", "one": "x"},
    {"kind": "a", "never": 1},
    {"kind": "a", "never": "x"},
    {"kind": "a", "shape": {"k": "circle", "r": 1}},
    {"kind": "a", "shape": {"k": "circle", "w": 1}},
    {"kind": "a", "shape": {"k": "square", "w": 1}},
    {"kind": "a", "shape": {"k": "square"}},
    {"kind": "a", "all": "ąę"},
    {"kind": "a", "all": "ae"},
    {"kind": "a", "all": ""},
]


def _envelope_cases() -> list[Any]:
    example = ENVELOPE["examples"][0]
    cases: list[Any] = [copy.deepcopy(e) for e in ENVELOPE["examples"]]

    def changed(**fields: Any) -> dict[str, Any]:
        doc: dict[str, Any] = copy.deepcopy(example)
        doc.update(fields)
        return doc

    cases += [
        changed(schema="nogat-handoff/2"),
        changed(created_at="2026-11-02 10:15"),
        changed(created_at="2026-11-02T10:15:00+01:00"),
        changed(subject=""),
        changed(provenance={}),
        changed(provenance={"Rain": {"source": "pmaxtp"}}),
        changed(provenance={"rainfall": {}}),
        changed(provenance={"rainfall": {"source": "PMAXTP"}}),
        changed(node_provenance={}),
        changed(node_provenance={"Z1": {}}),
        changed(node_provenance={"Z1": {"watershed": {"source": "hydrograf"}}}),
        changed(payload={"name": "bez schematu"}),
        changed(payload={"schema": "hydrolog-network"}),
        changed(result={}),
        changed(result={"peak_discharge_m3s": -1}),
        changed(result={"computed_with": {"tool": "hydrolog"}}),
        changed(producer={"tool": "hydrograf"}),
        changed(extra_field=1),
    ]
    return cases


def _js_problems(page: Page, cases: list[Any], schema: Any) -> list[list[str]]:
    found: list[list[str]] = _handoff(
        page,
        "(h, cases, schema) =>"
        " cases.map(c => h.validate(c, schema).map(p => p.keyword))",
        cases,
        schema,
    )
    return found


@pytest.mark.parametrize(
    ("schema", "cases"),
    [(KEYWORDS, KEYWORD_CASES), (ENVELOPE, _envelope_cases())],
    ids=["keywords", "envelope"],
)
def test_validate_agrees_with_jsonschema(
    page: Page, schema: dict[str, Any], cases: list[Any]
) -> None:
    validator = jsonschema.Draft202012Validator(schema)
    found = _js_problems(page, cases, schema)
    for case, keywords in zip(cases, found, strict=True):
        assert (keywords == []) == validator.is_valid(case), (case, keywords)
    assert {k for ks in found for k in ks} >= (
        {
            "type",
            "required",
            "const",
            "enum",
            "minimum",
            "maximum",
            "exclusiveMinimum",
            "exclusiveMaximum",
            "multipleOf",
            "minLength",
            "maxLength",
            "pattern",
            "uniqueItems",
            "minItems",
            "false",
            "additionalProperties",
            "propertyNames",
            "maxProperties",
            "anyOf",
            "oneOf",
            "not",
            "dependentRequired",
        }
        if schema is KEYWORDS
        else {"const", "pattern", "minLength", "required", "minProperties", "minimum"}
    )


def test_every_problem_has_a_polish_message(page: Page) -> None:
    messages = _handoff(
        page,
        "(h, cases, schema) => cases.flatMap(c => h.validate(c, schema))"
        ".map(p => p.message)",
        KEYWORD_CASES,
        KEYWORDS,
    )
    assert messages
    assert all(isinstance(m, str) and m and "undefined" not in m for m in messages)
