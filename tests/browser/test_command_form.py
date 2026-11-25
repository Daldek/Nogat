"""The kit's command builder in a browser: design/kit/nogat-command-form.*.

DEV-15.17 and ECO-093.

The element is tested where it runs: Chromium through Playwright, on a page of a GUI's
kind served from a throwaway directory under CSP `'self'`, with the GUI's bindings of a
tool's format_command and parse_command made up in command_form/page.js. The catalog
entries of command_form/catalogs.json are the tools' own (Kartograf's `elevation
download`, Hydrolog's `cn weighted`, Obserwator's `series export` and `datasets
download`) with the rules and sections each tool declares written in the optional fields
of commands-1 (AGI-2.3); `toy run` is made up to hold every kind of field and rule. An
uncaught exception, a console error, an unhandled rejection, a CSP violation or an event
of a control escaping the element fails the test.
"""

from __future__ import annotations

import functools
import http.server
import shutil
import threading
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import pytest
from playwright.sync_api import (
    Browser,
    Locator,
    Page,
    Playwright,
    ViewportSize,
    expect,
    sync_playwright,
)

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "design" / "kit"
FIXTURES = Path(__file__).resolve().parent / "command_form"
PHONE: ViewportSize = {"width": 390, "height": 844}
DESKTOP: ViewportSize = {"width": 1440, "height": 900}
Theme = Literal["light", "dark"]
# The tokens --surface and --code-bg in each theme.
SURFACE = {"light": "rgb(255, 255, 255)", "dark": "rgb(22, 27, 34)"}
CODE_BG = {"light": "rgb(13, 17, 23)", "dark": "rgb(1, 4, 9)"}
CSP = "; ".join(
    [
        "default-src 'self'",
        "script-src 'self'",
        "style-src 'self'",
        "img-src 'self' data:",
        "connect-src 'self'",
        "font-src 'self'",
        "object-src 'none'",
        "base-uri 'none'",
        "form-action 'self'",
        "frame-ancestors 'none'",
    ]
)
SHEET = "N-34-130-D-d-2-4"
MISSING = "Podaj wartość: opcja wymagana · required"


class _Site(http.server.SimpleHTTPRequestHandler):
    """The test page, the fixtures, the kit and the tokens, each under the GUI's CSP."""

    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".js": "text/javascript",
    }

    def log_message(self, format: str, *args: Any) -> None:
        pass

    def end_headers(self) -> None:
        self.send_header("Content-Security-Policy", CSP)
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


@pytest.fixture(scope="module")
def site(tmp_path_factory: pytest.TempPathFactory) -> Iterator[str]:
    """The page over HTTP, the kit as a GUI copies it."""
    directory = tmp_path_factory.mktemp("command_form")
    shutil.copytree(FIXTURES, directory, dirs_exist_ok=True)
    shutil.copytree(KIT, directory / "kit")
    shutil.copy(ROOT / "design" / "tokens.css", directory / "tokens.css")
    handler = functools.partial(_Site, directory=str(directory))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    thread.join()


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
    """The page with one form, and what the browser said."""

    page: Page
    problems: list[str] = field(default_factory=list)

    def run(self, script: str, arg: Any = None) -> Any:
        """The value of `script`, a function of the page's `formTest` and `arg`."""
        return self.page.evaluate(f"([arg]) => ({script})(window.formTest, arg)", [arg])

    def wait(self, script: str, arg: Any = None) -> None:
        """Wait until `script`, a function of `formTest` and `arg`, holds."""
        self.page.wait_for_function(
            f"([arg]) => window.formTest && window.formTest.ready"
            f" && ({script})(window.formTest, arg)",
            arg=[arg],
            timeout=10000,
        )

    def field(self, name: str) -> Locator:
        """The box of an option's field."""
        return self.page.locator(f'nogat-command-form [data-option="{name}"]')

    def control(self, name: str) -> Locator:
        """The text, select or textarea of an option."""
        return self.field(name).locator("input[type=text], select, textarea").first

    def message(self, name: str) -> Locator:
        """The message under an option's field."""
        return self.field(name).locator(".nogat-command-form-message")

    def flag(self, name: str) -> Locator:
        """The flag beside an option's name: „wymagane”, „domyślnie …”."""
        return self.field(name).locator(".nogat-command-form-flag")

    def choice(self, group: str) -> Locator:
        """The fieldset of a choice of `one_of`."""
        return self.page.locator(f'nogat-command-form [data-group="{group}"]')

    def pick(self, group: str, label: str) -> None:
        """Choose an alternative of a choice, as a person does."""
        radios = self.choice(group).locator(":scope > .nogat-command-form-radios")
        radios.get_by_label(label, exact=True).check()

    def radio(self, name: str, value: str) -> Locator:
        """The radio of a value of a choice field."""
        return self.field(name).get_by_label(value, exact=True)

    def options(self) -> dict[str, Any]:
        """The call the form gives."""
        result: dict[str, Any] = self.run("t => t.form.options")
        return result

    def shown(self) -> list[str]:
        """The options whose fields are shown, in order."""
        names: list[str] = self.run(
            "t => [...t.form.querySelectorAll('[data-option]')]"
            ".map(e => e.dataset.option)"
        )
        return names

    def line(self) -> Locator:
        """The text of the line."""
        return self.page.locator("nogat-command-form .nogat-command-form-line-text")


@pytest.fixture
def tabs(browser: Browser, site: str) -> Iterator[Callable[..., Tab]]:
    """Open the page in a new context, `query` its parameters (catalog, format…)."""
    opened: list[Tab] = []

    def open_tab(
        query: str = "catalog=kartograf",
        *,
        viewport: ViewportSize = DESKTOP,
        theme: Theme = "light",
    ) -> Tab:
        context = browser.new_context(viewport=viewport, color_scheme=theme)
        context.grant_permissions(["clipboard-read", "clipboard-write"], origin=site)
        page = context.new_page()
        tab = Tab(page)

        def note(text: str, kind: str) -> None:
            if kind == "error":
                tab.problems.append(text)

        page.on("console", lambda m: note(m.text, m.type))
        page.on("pageerror", lambda e: tab.problems.append(str(e)))
        page.goto(f"{site}/page.html?{query}")
        tab.wait("t => t.form.querySelector('.nogat-command-form')")
        opened.append(tab)
        return tab

    yield open_tab
    problems: list[str] = []
    for tab in opened:
        state = tab.run("t => [t.cspViolations, t.rejections, t.escaped]")
        problems += [f"CSP: {v}" for v in state[0]]
        problems += [f"rejected: {r}" for r in state[1]]
        problems += [f"{state[2]} events of the controls escaped"] if state[2] else []
        problems += tab.problems
        tab.page.context.close()
    assert problems == []


# The fields


def test_each_option_is_a_field_of_its_type_in_its_section_in_polish(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs()
    sections = tab.page.locator(
        "nogat-command-form .nogat-command-form-section > legend"
    )
    expect(sections).to_have_text(
        [
            "Produkt i obszar",
            "Parametry produktu",
            "Arkusze obszaru",
            "Wycinek zamiast arkuszy",
            "Rok danych, loty i kafle (tylko PL)",
            "Wynik i aktualizacja",
        ]
    )
    product = tab.field("product")
    expect(product.locator("input[type=radio]")).to_have_count(4)
    expect(product.locator("legend code")).to_have_text("product")
    expect(tab.flag("product")).to_have_text("wymagane")
    expect(product.locator(".nogat-command-form-hint")).to_have_text(
        "Produkt (wymagany)."
    )
    tab.radio("product", "laz").check()
    expect(product.locator(".nogat-command-form-meaning")).to_have_text(
        "laz Chmura punktow LIDAR; PL i CZ."
    )
    expect(tab.field("resolution").locator("select")).to_have_count(1)
    expect(tab.field("cutout").locator("input[type=checkbox]")).to_have_count(1)
    year = tab.control("year")
    expect(year).to_have_attribute("inputmode", "numeric")
    expect(tab.control("plan")).to_have_js_property("tagName", "TEXTAREA")
    expect(tab.control("workers")).to_have_attribute("placeholder", "4")
    expect(tab.flag("workers")).to_have_text("domyślnie 4")
    # English where the catalog has no Polish text; the rules in Polish only.
    expect(tab.field("layer").locator(".nogat-command-form-hint")).to_have_text(
        "GPKG layer of geometry (default: the first one)."
    )
    expect(tab.page.locator(".nogat-command-form-rules")).to_contain_text("Zasady: ")
    tab.pick("one_of", "bbox")
    expect(tab.control("bbox")).to_have_attribute(
        "placeholder", "np. 565000; 242000; 566000; 243000"
    )


def test_a_choice_value_keeps_its_catalog_type_and_optional_ones_wait_closed(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs("catalog=toy")
    level = tab.field("level")
    expect(level.locator("input[type=radio]")).to_have_count(3)
    tab.radio("level", "2").check()
    expect(level.locator(".nogat-command-form-meaning")).to_have_text("2 Średni.")
    assert tab.options() == {"level": 2}
    more = tab.page.locator("nogat-command-form details.nogat-command-form-more")
    expect(more).not_to_have_attribute("open", "")
    expect(more.locator("summary")).to_have_text("Opcje dodatkowe 3")
    more.locator("summary").click()
    expect(tab.control("start")).to_have_attribute("placeholder", "RRRR-MM-DDTgg:mm")
    expect(tab.control("tags")).to_have_attribute(
        "placeholder", "Wartości oddziel przecinkiem."
    )
    expect(tab.control("settings")).to_have_js_property("tagName", "TEXTAREA")
    expect(tab.control("report")).to_have_attribute("placeholder", "ścieżka zapisu")


# The choices of one_of


def test_exactly_one_alternative_is_given_and_only_it_is_sent(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs()
    area = tab.choice("one_of")
    expect(area.locator(":scope > legend")).to_have_text("Sposób podania jedna z 3")
    radios = area.locator(":scope > .nogat-command-form-radios label")
    expect(radios).to_have_text(["sheet", "bbox", "geometry"])
    expect(area.get_by_label("sheet", exact=True)).to_be_checked()
    expect(tab.flag("sheet")).to_have_text("wymagane")
    tab.control("sheet").fill(SHEET)
    tab.pick("one_of", "bbox")
    assert "sheet" not in tab.shown()
    tab.control("bbox").fill("565000 242000 566000 243000")
    assert tab.options() == {"bbox": [565000, 242000, 566000, 243000]}
    tab.pick("one_of", "sheet")
    expect(tab.control("sheet")).to_have_value(SHEET)
    assert tab.options() == {"sheet": SHEET}


def test_at_most_one_option_of_a_group_is_given(tabs: Callable[..., Tab]) -> None:
    tab = tabs()
    target = tab.choice("target")
    expect(target.locator(":scope > legend")).to_have_text("target najwyżej jedna z 2")
    expect(target.get_by_label("—", exact=True)).to_be_checked()
    assert "output_dir" not in tab.shown() and "root" not in tab.shown()
    tab.pick("target", "output_dir")
    expect(tab.flag("output_dir")).to_have_text("wymagane")
    expect(tab.control("output_dir")).to_have_attribute("placeholder", "ścieżka zapisu")
    tab.control("output_dir").fill("./dane")
    assert tab.options() == {"output_dir": "./dane"}
    tab.pick("target", "—")
    assert tab.options() == {}


def test_a_boolean_alternative_and_a_field_that_applies_only_with_one(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs("catalog=toy")
    tab.radio("level", "1").check()
    pane = tab.choice("one_of").locator(".nogat-command-form-pane")
    expect(pane.locator("[data-option]")).to_have_count(2)
    assert tab.shown()[:2] == ["point", "point_crs"]
    tab.control("point").fill("16,5; 51,1")
    tab.radio("point_crs", "EPSG:4326").check()
    assert tab.options() == {
        "point": [16.5, 51.1],
        "point_crs": "EPSG:4326",
        "level": 1,
    }
    tab.pick("one_of", "everywhere")
    assert "point_crs" not in tab.shown()
    expect(pane.locator("[data-option=everywhere] input")).to_have_count(0)
    assert tab.options() == {"everywhere": True, "level": 1}


def test_alternatives_of_several_options_share_one(tabs: Callable[..., Tab]) -> None:
    tab = tabs("catalog=hydrolog")
    labels = tab.choice("one_of").locator(":scope > .nogat-command-form-radios label")
    expect(labels).to_have_text(["parts", "cn_values + areas", "cn_values + fractions"])
    tab.run("t => { t.form.options = {cn_values: [55, 79], fractions: [0.6, 0.4]}; }")
    expect(tab.choice("one_of").get_by_label("cn_values + fractions")).to_be_checked()
    expect(tab.control("cn_values")).to_have_value("55; 79")
    expect(tab.control("fractions")).to_have_value("0,6; 0,4")
    assert tab.shown() == ["cn_values", "fractions"]
    expect(tab.flag("fractions")).to_have_text("wymagane")
    assert tab.options() == {"cn_values": [55, 79], "fractions": [0.6, 0.4]}


# Paths the app owns, options it supplies


def test_paths_and_supplied_options_are_neither_shown_nor_sent(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs("catalog=kartograf&paths=hidden&hide=check,plan")
    shown = tab.shown()
    for name in ("geometry", "output_dir", "root", "check", "plan"):
        assert name not in shown
    expect(tab.choice("target")).to_have_count(0)
    labels = tab.choice("one_of").locator(":scope > .nogat-command-form-radios label")
    expect(labels).to_have_text(["sheet", "bbox"])
    tab.run("t => t.form.setOption('geometry', 'obszar.gpkg')")
    tab.run("t => { t.form.options = {product: 'nmt', root: '/data', check: true}; }")
    assert tab.options() == {"product": "nmt"}


def test_an_alternative_left_alone_is_required(tabs: Callable[..., Tab]) -> None:
    tab = tabs("catalog=obserwator&paths=hidden")
    expect(tab.choice("one_of")).to_have_count(0)
    assert "version" not in tab.shown() and "root" not in tab.shown()
    expect(tab.flag("dataset")).to_have_text("wymagane")
    # `force` requires `output`, which the app supplies: no message names it.
    tab.field("force").locator("input").check()
    assert tab.run("t => t.form.check()") is False
    expect(tab.message("force")).to_be_hidden()
    expect(tab.message("dataset")).to_have_text(MISSING)


# The rules


def test_a_field_applies_only_where_its_rule_holds(tabs: Callable[..., Tab]) -> None:
    tab = tabs()
    assert "min_density" not in tab.shown() and "model" not in tab.shown()
    tab.radio("product", "laz").check()
    assert {"min_density", "model"} <= set(tab.shown())
    tab.control("min_density").fill("4")
    assert tab.options()["min_density"] == 4
    tab.radio("product", "nmt").check()
    assert "min_density" not in tab.shown()
    assert "min_density" not in tab.options()
    assert "horizontal_crs" not in tab.shown()
    tab.field("cutout").locator("input").check()
    expect(tab.flag("horizontal_crs")).to_have_text("wymagane")


def test_a_given_option_disables_those_it_excludes(tabs: Callable[..., Tab]) -> None:
    tab = tabs()
    tab.control("year").fill("2020")
    for name in ("min_year", "max_year"):
        expect(tab.control(name)).to_be_disabled()
        expect(tab.flag(name)).to_have_text("nie razem z year")
    tab.control("year").fill("")
    expect(tab.control("min_year")).to_be_enabled()
    expect(tab.flag("min_year")).to_have_text("")
    tab.field("cutout").locator("input").check()
    expect(tab.control("sheet")).to_be_disabled()
    expect(tab.flag("sheet")).to_have_text("nie razem z cutout")


def test_an_option_is_required_where_its_rule_says(tabs: Callable[..., Tab]) -> None:
    tab = tabs("catalog=toy")
    tab.radio("level", "1").check()
    expect(tab.flag("depth")).to_have_text("")
    tab.radio("level", "3").check()
    expect(tab.flag("depth")).to_have_text("wymagane")
    expect(tab.flag("report")).to_have_text("")
    tab.field("strict").locator("input").check()
    expect(tab.flag("report")).to_have_text("wymagane")
    tab.field("fast").locator("input").check()
    expect(tab.control("depth")).to_be_disabled()
    tab.control("point").fill("16.5, 51.1")
    tab.control("report").fill("out/raport.csv")
    assert tab.run("t => t.form.check()") is True
    assert tab.options() == {
        "point": [16.5, 51.1],
        "level": 3,
        "fast": True,
        "strict": True,
        "report": "out/raport.csv",
    }


# The messages


def test_check_shows_each_message_under_its_field(tabs: Callable[..., Tab]) -> None:
    tab = tabs()
    expect(tab.page.locator(".nogat-command-form-message:visible")).to_have_count(0)
    tab.control("workers").fill("0")
    tab.control("year").fill("20x")
    assert tab.run("t => t.form.check()") is False
    expect(tab.message("product")).to_have_text(MISSING)
    expect(tab.message("sheet")).to_have_text(MISSING)
    expect(tab.message("workers")).to_have_text("Najmniej 1 (podano 0) · minimum")
    expect(tab.message("year")).to_have_text("Podaj liczbę całkowitą · type")
    expect(tab.control("year")).to_have_attribute("aria-invalid", "true")
    described = tab.control("year").get_attribute("aria-describedby") or ""
    assert tab.message("year").get_attribute("id") in described.split()
    tab.pick("one_of", "bbox")
    tab.control("bbox").fill("565000,242000,566000,243000")
    expect(tab.message("bbox")).to_have_text(
        "Wartość 1 („565000,242000,566000,243000”) nie jest liczbą · type"
    )
    tab.control("bbox").fill("16.5,51.0,16.6,51.1")
    tab.radio("product", "nmt").check()
    tab.control("workers").fill("2")
    tab.control("year").fill("2020")
    expect(tab.page.locator(".nogat-command-form-message:visible")).to_have_count(0)
    assert tab.run("t => t.form.check()") is True


def test_a_field_left_wrong_says_so_and_is_quiet_once_right(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs("catalog=obserwator")
    start = tab.control("start")
    tab.page.locator("details.nogat-command-form-more summary").click()
    start.fill("2024-02-30")
    expect(tab.message("start")).to_be_hidden()
    start.press("Tab")
    expect(tab.message("start")).to_have_text(
        "Podaj datę w formacie RRRR-MM-DD · format"
    )
    start.fill("2024-02-29")
    expect(tab.message("start")).to_be_hidden()
    tab.control("station").fill("15016018")
    tab.control("station").press("Tab")
    expect(tab.message("station")).to_contain_text("Nie pasuje do wzorca")


def test_a_wrong_value_in_a_closed_section_opens_it(tabs: Callable[..., Tab]) -> None:
    tab = tabs("catalog=toy")
    tab.run(
        "t => { t.form.options = {station: '150160180', level: 1, settings: '[1]'}; }"
    )
    more = tab.page.locator("details.nogat-command-form-more")
    expect(more).not_to_have_attribute("open", "")
    assert tab.run("t => t.form.check()") is False
    expect(more).to_have_attribute("open", "")
    expect(tab.message("settings")).to_have_text("Podaj obiekt JSON: {…} · type")


def test_an_error_document_stands_under_the_option_it_names(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs()
    tab.run(
        "t => t.form.showError({code: 'validation_error',"
        " message: 'unknown sheet code',"
        " details: {option: 'sheet', reason: 'unknown_sheet'}})"
    )
    expect(tab.message("sheet")).to_have_text("unknown sheet code · unknown_sheet")
    loose = tab.page.locator("nogat-command-form .nogat-command-form-errors")
    expect(loose).to_be_hidden()
    tab.control("sheet").fill(SHEET)
    expect(tab.message("sheet")).to_be_hidden()
    tab.run(
        "t => t.form.showError({code: 'validation_error', message: 'not a file',"
        " details: {option: 'geometry', reason: 'invalid_path'}})"
    )
    expect(loose.locator("strong")).to_have_text("Popraw polecenie")
    expect(loose.locator("li")).to_have_text(["geometry not a file · invalid_path"])
    tab.run("t => t.form.showError({code: 'source_unavailable', message: 'down'})")
    expect(loose.locator("li")).to_have_text(["down"])
    tab.run("t => { t.form.errors = {}; }")
    expect(loose).to_be_hidden()


# The line and the pasted line


def _fill_nmt_sheet(tab: Tab) -> None:
    """The options of a whole call: NMT of one sheet in EVRF2007."""
    tab.radio("product", "nmt").check()
    tab.control("sheet").fill(SHEET)
    tab.radio("vertical_crs", "EVRF2007").check()


LINE = (
    "kartograf elevation download --product nmt"
    f" --sheet {SHEET} --vertical-crs EVRF2007"
)


def test_the_line_is_written_by_the_tool_and_copied(tabs: Callable[..., Tab]) -> None:
    tab = tabs("catalog=kartograf&format=1")
    line = tab.page.locator("nogat-command-form .nogat-command-form-line")
    copy = line.get_by_role("button", name="Kopiuj")
    expect(tab.line()).to_have_text("Uzupełnij albo popraw: product, sheet")
    expect(copy).to_be_disabled()
    _fill_nmt_sheet(tab)
    expect(tab.line()).to_have_text(LINE)
    assert tab.run("t => t.form.line") == LINE
    copy.click()
    expect(line.locator(".nogat-command-form-status")).to_have_text(
        "Skopiowano do schowka"
    )
    assert tab.page.evaluate("() => navigator.clipboard.readText()") == LINE


def test_a_refused_line_places_the_tools_message(tabs: Callable[..., Tab]) -> None:
    tab = tabs("catalog=kartograf&format=1")
    _fill_nmt_sheet(tab)
    expect(tab.line()).to_have_text(LINE)
    tab.control("sheet").fill("X-0")
    expect(tab.message("sheet")).to_have_text("unknown sheet code X-0 · unknown_sheet")
    expect(tab.line()).to_have_text(
        "Nie udało się zapisać polecenia: unknown sheet code X-0"
    )
    tab.control("sheet").fill(SHEET)
    expect(tab.line()).to_have_text(LINE)
    expect(tab.message("sheet")).to_be_hidden()
    tab.control("workers").fill("99")
    expect(tab.line()).to_have_text(
        "Nie udało się zapisać polecenia: the server does not answer"
    )
    expect(tab.message("workers")).to_be_hidden()


def test_the_line_is_asked_once_typing_stops_and_the_last_answer_wins(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs("catalog=kartograf&format=1")
    _fill_nmt_sheet(tab)
    expect(tab.line()).to_have_text(LINE)
    before = tab.run("t => t.formatted.length")
    tab.control("year").press_sequentially("2021", delay=10)
    expect(tab.line()).to_have_text(f"{LINE} --year 2021")
    assert tab.run("t => t.formatted.length") - before <= 2
    tab.run("t => { t.slow = {option: 'workers', value: 7, ms: 700}; }")
    tab.control("workers").fill("7")
    tab.wait("t => t.formatted.some(call => call.options.workers === 7)")
    tab.control("workers").fill("8")
    expect(tab.line()).to_have_text(f"{LINE} --year 2021 --workers 8")
    tab.page.wait_for_timeout(900)
    expect(tab.line()).to_have_text(f"{LINE} --year 2021 --workers 8")


def test_a_pasted_line_fills_the_form(tabs: Callable[..., Tab]) -> None:
    tab = tabs("catalog=kartograf&parse=1")
    paste = tab.page.locator("nogat-command-form .nogat-command-form-paste")
    field_ = paste.get_by_label("Wklej polecenie")
    field_.fill(
        "kartograf elevation download --product laz --bbox 565000,242000,566000,243000"
        " --vertical-crs KRON86 --min-density 4"
    )
    field_.press("Enter")
    expect(tab.radio("product", "laz")).to_be_checked()
    expect(tab.choice("one_of").get_by_label("bbox", exact=True)).to_be_checked()
    expect(tab.control("bbox")).to_have_value("565000; 242000; 566000; 243000")
    expect(tab.control("min_density")).to_have_value("4")
    expect(field_).to_have_value("")
    options = {
        "product": "laz",
        "bbox": [565000, 242000, 566000, 243000],
        "vertical_crs": "KRON86",
        "min_density": 4,
    }
    assert tab.options() == options
    assert tab.run("t => t.changes.at(-1)") == {"options": options, "valid": True}
    field_.fill("kartograf elevation download --colour red")
    paste.get_by_role("button", name="Wczytaj").click()
    expect(paste.locator(".nogat-command-form-message")).to_have_text(
        "Nie udało się odczytać polecenia: unknown option --colour"
    )
    field_.fill("hydrolog tc kirpich --length-km 2")
    field_.press("Enter")
    expect(paste.locator(".nogat-command-form-message")).to_have_text(
        "Nie udało się odczytać polecenia: not a kartograf line"
    )
    assert tab.options() == options


def test_a_pasted_line_of_another_command_goes_to_the_gui(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs("catalog=obserwator&parse=1")
    paste = tab.page.locator("nogat-command-form .nogat-command-form-paste")
    line = (
        "obserwator datasets download --dataset pl.imgw.hydro_semiannual --params H,Q"
    )
    paste.get_by_label("Wklej polecenie").fill(line)
    paste.get_by_role("button", name="Wczytaj").click()
    expect(paste.locator(".nogat-command-form-message")).to_have_text(
        "To polecenie datasets download, nie series export"
    )
    tab.run("t => { t.switches = true; }")
    paste.get_by_role("button", name="Wczytaj").click()
    tab.wait("t => t.form.command.name === 'datasets download'")
    params = tab.field("params")
    expect(params.locator("input[type=checkbox]")).to_have_count(3)
    expect(params.get_by_label("H", exact=True)).to_be_checked()
    expect(params.get_by_label("T", exact=True)).not_to_be_checked()
    assert tab.options() == {
        "dataset": "pl.imgw.hydro_semiannual",
        "params": ["H", "Q"],
    }
    assert tab.run("t => t.pastes.map(p => p.command)") == ["datasets download"] * 2


# The values and the events


def test_options_set_by_the_gui_come_back_as_they_went(
    tabs: Callable[..., Tab],
) -> None:
    toy = {
        "point": [16.5, 51.1],
        "point_crs": "EPSG:4326",
        "level": 3,
        "depth": 12.5,
        "start": "2024-05-01T12:30",
        "strict": True,
        "report": "out/raport.csv",
        "tags": ["a", "b"],
        "tag_colour": "red",
        "settings": {"x": 1},
    }
    tab = tabs("catalog=toy")
    tab.run("(t, options) => { t.form.options = options; }", toy)
    assert tab.options() == toy
    expect(tab.control("depth")).to_have_value("12,5")
    expect(tab.control("point")).to_have_value("16,5; 51,1")
    assert tab.run("t => t.form.valid") is True
    kartograf = {
        "product": "nmt",
        "bbox": [16.5, 51.0, 16.6, 51.1],
        "bbox_crs": "EPSG:4326",
        "vertical_crs": "EVRF2007",
        "cutout": True,
        "horizontal_crs": "EPSG:2180",
        "output_dir": "./dane",
        "workers": 2,
    }
    tab = tabs()
    tab.run("(t, options) => { t.form.options = options; }", kartograf)
    assert tab.options() == kartograf
    assert tab.run("t => t.changes.length") == 0


def test_the_map_sets_one_option_and_its_alternative_follows(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs()
    tab.control("sheet").fill(SHEET)
    edits = tab.run("t => t.changes.length")
    tab.run("t => t.form.setOption('bbox', [16.5, 51.0, 16.6, 51.1])")
    expect(tab.choice("one_of").get_by_label("bbox", exact=True)).to_be_checked()
    expect(tab.control("bbox")).to_have_value("16,5; 51; 16,6; 51,1")
    assert tab.options() == {"bbox": [16.5, 51.0, 16.6, 51.1]}
    tab.run("t => t.form.setOption('bbox', undefined)")
    expect(tab.control("bbox")).to_have_value("")
    assert tab.run("t => t.changes.length") == edits


def test_change_carries_the_call_and_the_controls_events_stay_inside(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs()
    tab.control("sheet").press_sequentially("N-34")
    assert tab.run("t => t.changes.at(-1)") == {
        "options": {"sheet": "N-34"},
        "valid": False,
    }
    tab.radio("product", "nmpt").check()
    assert tab.run("t => t.changes.at(-1)") == {
        "options": {"product": "nmpt", "sheet": "N-34"},
        "valid": True,
    }


def test_typing_keeps_its_place_when_the_form_is_drawn_again(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs("catalog=toy")
    tab.page.locator("details.nogat-command-form-more summary").click()
    assert "tag_colour" not in tab.shown()
    tags = tab.control("tags")
    tags.press_sequentially("ab")
    expect(tab.field("tag_colour")).to_have_count(1)
    focused = tab.run(
        "t => [document.activeElement.id, document.activeElement.value,"
        " document.activeElement.selectionStart]"
    )
    assert focused == [tags.get_attribute("id"), "ab", 2]
    tags.press_sequentially(", c")
    expect(tags).to_have_value("ab, c")
    assert tab.options()["tags"] == ["ab", "c"]


def test_another_language_passes_its_own_words(tabs: Callable[..., Tab]) -> None:
    tab = tabs("catalog=toy")
    tab.run(
        "t => { t.form.texts = {required: 'required', more: 'More options',"
        " choice: 'Given as', exactlyOne: 'one of {count}'}; }"
    )
    legend = tab.choice("one_of").locator(":scope > legend")
    expect(legend).to_have_text("Given as one of 3")
    expect(tab.flag("level")).to_have_text("required")
    expect(tab.page.locator("details summary")).to_have_text("More options 3")
    expect(tab.flag("point")).to_have_text("required")


# The look


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_the_form_fits_a_phone_in_both_themes(
    tabs: Callable[..., Tab], theme: Theme
) -> None:
    tab = tabs("catalog=kartograf&format=1&parse=1", viewport=PHONE, theme=theme)
    tab.pick("one_of", "bbox")
    tab.control("bbox").fill("16.5,51.0,16.6,51.1")
    width = tab.page.evaluate("() => document.documentElement.scrollWidth")
    assert width <= PHONE["width"]
    look = tab.page.evaluate(
        """() => {
          const form = "nogat-command-form";
          const input = document.querySelector(`${form} [data-option=sheet] input,`
            + ` ${form} [data-option=bbox] input`);
          const line = document.querySelector(".nogat-command-form-line-text");
          const radio = document.querySelector(`${form} .nogat-command-form-radio`);
          return {
            surface: getComputedStyle(input).backgroundColor,
            line: getComputedStyle(line).backgroundColor,
            height: input.getBoundingClientRect().height,
            radio: radio.getBoundingClientRect().height,
          };
        }"""
    )
    assert look["surface"] == SURFACE[theme]
    assert look["height"] >= 32 and look["radio"] >= 24
    tab.radio("product", "nmt").check()
    tab.radio("vertical_crs", "EVRF2007").check()
    expect(tab.line()).to_contain_text("kartograf elevation download")
    assert (
        tab.page.evaluate(
            "() => getComputedStyle(document.querySelector("
            "'.nogat-command-form-line-text')).backgroundColor"
        )
        == CODE_BG[theme]
    )
    assert tab.page.evaluate("() => document.documentElement.scrollWidth") <= 390
