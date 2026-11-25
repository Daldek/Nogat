"""The kit's charts in a browser: design/kit/nogat-chart.* (DEV-15.16, ECO-090).

The module is tested where it runs: Chromium through Playwright, on a page of a
GUI's kind (chart/chart.html, its .btn.sm, a page long enough to scroll)
served from a throwaway directory under the GUIs' CSP, `default-src 'self';
img-src 'self' data: blob:`, at 1440 × 900 and at 390 × 844 px with touch, in
both themes. A mouse, a wheel and keys are Playwright's; fingers are DevTools'
`Input.dispatchTouchEvent`, so the browser's own touch-action decides what
scrolls. An uncaught exception, a console error or a CSP violation fails the
test.
"""

from __future__ import annotations

import functools
import http.server
import math
import re
import shutil
import threading
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Literal

import pytest
from playwright.sync_api import (
    Browser,
    CDPSession,
    Page,
    Playwright,
    ViewportSize,
    sync_playwright,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "chart"
CSP = "default-src 'self'; img-src 'self' data: blob:"
PHONE: ViewportSize = {"width": 390, "height": 844}
DESKTOP: ViewportSize = {"width": 1440, "height": 900}
Theme = Literal["light", "dark"]
THEMES: tuple[Theme, ...] = ("light", "dark")
# The daily chart's days: day numbers from 2020-01-01 (18262), 3000 of them.
FIRST = 18262
DAYS = 3000
# --series-1 (--info) and --text-3 in each theme; the light ones without tokens.css.
SERIES = {"light": "rgb(29, 78, 216)", "dark": "rgb(88, 166, 255)"}
MUTED = {"light": "rgb(107, 101, 101)", "dark": "rgb(139, 148, 158)"}
# The words of CHART_TEXTS, which a GUI in another language replaces.
POLISH = ["Przybliż", "Oddal", "Cały zakres", "Strzałki", "lata", "lat"]


class _Site(http.server.SimpleHTTPRequestHandler):
    """The test pages and the kit, every answer under the GUIs' CSP."""

    def log_message(self, format: str, *args: Any) -> None:
        pass

    def end_headers(self) -> None:
        self.send_header("Content-Security-Policy", CSP)
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


@pytest.fixture(scope="module")
def site(tmp_path_factory: pytest.TempPathFactory) -> Iterator[str]:
    """The kit, the tokens and the test pages, over HTTP."""
    directory = tmp_path_factory.mktemp("chart")
    shutil.copytree(FIXTURES, directory, dirs_exist_ok=True)
    shutil.copytree(ROOT / "design" / "kit", directory / "kit")
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
    """A test page with a chart: what it draws, where its plot is, what it shows."""

    page: Page
    problems: list[str] = field(default_factory=list)
    requests: list[str] = field(default_factory=list)
    cdp: CDPSession | None = None

    def js(self, body: str, arg: Any = None) -> Any:
        """Evaluate `body`, an expression of `t` (window.chartTest) and `arg`."""
        return self.page.evaluate(
            f"async (arg) => {{ const t = window.chartTest; return {body}; }}", arg
        )

    def until(self, condition: str) -> None:
        """Wait for a condition of the page, polled in it (no eval under its CSP)."""
        self.page.evaluate(
            "async () => { for (let n = 0; n < 300; n += 1) {"
            f" if ({condition}) return;"
            " await new Promise((resolve) => setTimeout(resolve, 10)); }"
            f" throw new Error({condition!r}); }}"
        )

    def draw(self, name: str, **options: Any) -> None:
        self.js("t.draw(arg[0], arg[1])", [name, options])

    def state(self) -> dict[str, Any]:
        state: dict[str, Any] = self.js("t.state()")
        return state

    def ranges(self) -> list[Any]:
        ranges: list[Any] = self.js("t.ranges")
        return ranges

    def at(self, fx: float, fy: float = 0.5) -> tuple[float, float]:
        """The screen point at shares of the plot, x from the left, y from the top."""
        plot = self.js("t.plot()")
        x = plot["left"] + fx * (plot["right"] - plot["left"])
        y = plot["top"] + fy * (plot["bottom"] - plot["top"])
        cx, cy = self.js("t.toClient(arg[0], arg[1])", [x, y])
        return float(cx), float(cy)

    def x_at(self, point: tuple[float, float], whole: tuple[float, float]) -> float:
        """The value of x under a screen point, by the range shown (or the whole)."""
        plot = self.js("t.plot()")
        vx, _ = self.js("t.toView(arg[0], arg[1])", list(point))
        shown = self.state()["range"] or {"min": whole[0], "max": whole[1]}
        share = (vx - plot["left"]) / (plot["right"] - plot["left"])
        return float(shown["min"] + share * (shown["max"] - shown["min"]))

    def drag(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        *,
        button: Literal["left", "middle"] = "left",
        shift: bool = False,
    ) -> None:
        if shift:
            self.page.keyboard.down("Shift")
        self.page.mouse.move(*start)
        self.page.mouse.down(button=button)
        self.page.mouse.move(*end, steps=6)
        self.page.mouse.up(button=button)
        if shift:
            self.page.keyboard.up("Shift")

    def press(self, *keys: str) -> None:
        self.page.focus("#chart svg")
        for key in keys:
            self.page.keyboard.press(key)

    def touch(self, kind: str, points: list[tuple[float, float]]) -> None:
        """A touch event of DevTools: start, move or end, at screen points."""
        if self.cdp is None:
            self.cdp = self.page.context.new_cdp_session(self.page)
        touches = [{"x": x, "y": y, "id": n} for n, (x, y) in enumerate(points)]
        self.cdp.send(
            "Input.dispatchTouchEvent", {"type": kind, "touchPoints": touches}
        )


@pytest.fixture
def tabs(browser: Browser, site: str) -> Iterator[Callable[..., Tab]]:
    """Open a test page in a new context; a fault of the page fails the test."""
    opened: list[Tab] = []

    def open_tab(
        *,
        viewport: ViewportSize = DESKTOP,
        theme: Theme = "light",
        touch: bool = False,
        page: str = "chart.html",
    ) -> Tab:
        context = browser.new_context(
            viewport=viewport, color_scheme=theme, has_touch=touch
        )
        tab = Tab(context.new_page())
        tab.page.on(
            "console",
            lambda m: tab.problems.append(m.text) if m.type == "error" else None,
        )
        tab.page.on("pageerror", lambda e: tab.problems.append(str(e)))
        tab.page.on("request", lambda r: tab.requests.append(r.url))
        tab.page.goto(f"{site}/{page}")
        tab.until("window.chartTest && window.chartTest.ready")
        opened.append(tab)
        return tab

    yield open_tab
    problems: list[str] = []
    for tab in opened:
        page, csp = tab.js("[t.problems, t.cspViolations]")
        problems += [f"page: {p}" for p in page] + [f"CSP: {v}" for v in csp]
        problems += tab.problems
        tab.page.context.close()
    assert problems == []


def _day(day: float) -> str:
    """A day number as the module writes it in Polish, dd.mm.rrrr, rounded half up."""
    when = date(1970, 1, 1) + timedelta(days=math.floor(day + 0.5))
    return when.strftime("%d.%m.%Y")


def _width(shown: dict[str, Any]) -> float:
    return float(shown["max"] - shown["min"])


WHOLE = (float(FIRST), float(FIRST + DAYS - 1))


# --- mouse and trackpad --------------------------------------------------------------


@pytest.mark.parametrize("theme", THEMES)
def test_a_drag_selects_x_the_y_axis_fits_and_the_bar_shows_the_range(
    tabs: Callable[..., Tab], theme: Theme
) -> None:
    tab = tabs(theme=theme)
    tab.draw("daily", days=DAYS)
    before = tab.state()
    assert before["range"] is None
    assert before["bar"] == {
        "zoomIn": True,
        "zoomOut": False,
        "reset": False,
        "range": None,
    }
    assert before["yTicks"][-1] == "600"  # the flood of July 2020

    tab.drag(tab.at(0.4), tab.at(0.6))
    after = tab.state()
    shown = after["range"]
    assert 0.19 < _width(shown) / (DAYS - 1) < 0.21
    top = float(after["yTicks"][-1].replace(",", "."))
    assert top < 300  # the y axis fits the part shown
    expected = f"{_day(shown['min'])} – {_day(shown['max'])}"
    assert after["bar"] == {
        "zoomIn": True,
        "zoomOut": True,
        "reset": True,
        "range": expected,
    }
    assert after["live"] == expected
    width = tab.js("t.chart.plotWidth()")
    assert tab.ranges() == [{**shown, "width": width}]
    assert width == pytest.approx(tab.js("t.plot().right - t.plot().left"), abs=1)


def test_a_drag_shorter_than_six_units_is_a_click(tabs: Callable[..., Tab]) -> None:
    tab = tabs()
    tab.draw("daily", days=DAYS)
    start = tab.at(0.5)
    tab.drag(start, (start[0] + 4, start[1]))
    assert tab.state()["range"] is None
    assert tab.ranges() == []


def test_a_rectangle_zooms_x_and_y_of_a_chart_of_points(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs()
    tab.draw("rating")
    assert tab.state()["xTicks"][-1] == "160" and tab.state()["yTicks"][-1] == "600"

    tab.drag(tab.at(0.2, 0.3), tab.at(0.5, 0.7))
    shown = tab.state()["range"]
    assert shown["min"] == pytest.approx(32, abs=0.5)
    assert shown["max"] == pytest.approx(80, abs=0.5)
    assert shown["y"]["min"] == pytest.approx(180, abs=2)
    assert shown["y"]["max"] == pytest.approx(420, abs=2)
    assert tab.state()["bar"]["range"] == "Q: 32,00 – 80,00, H: 180 – 420"

    # A drag along x alone zooms x and leaves y whole
    tab.js("t.chart.zoom.reset()")
    tab.drag(tab.at(0.2, 0.5), tab.at(0.5, 0.505))
    shown = tab.state()["range"]
    assert shown["max"] - shown["min"] == pytest.approx(48, abs=0.5)
    assert shown["y"] == {"min": 0, "max": 600}


def test_ctrl_with_the_wheel_zooms_around_the_cursor_the_wheel_alone_scrolls(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs()
    tab.draw("daily", days=DAYS, fixedY=True)
    tab.js(
        "(window.wheels = [], window.addEventListener('wheel',"
        " (e) => window.wheels.push([e.ctrlKey, e.defaultPrevented])))"
    )
    cursor = tab.at(0.3)
    under = tab.x_at(cursor, WHOLE)
    tab.page.mouse.move(*cursor)
    tab.page.keyboard.down("Control")
    tab.page.mouse.wheel(0, -100)
    tab.page.keyboard.up("Control")
    tab.page.wait_for_timeout(300)
    shown = tab.state()["range"]
    assert _width(shown) == pytest.approx((DAYS - 1) / 1.25, rel=1e-6)
    assert tab.x_at(cursor, WHOLE) == pytest.approx(under, abs=0.5)
    assert tab.ranges() == [{**shown, "width": tab.js("t.chart.plotWidth()")}]

    # A trackpad's small step zooms in proportion
    tab.page.keyboard.down("Control")
    tab.page.mouse.wheel(0, -10)
    tab.page.keyboard.up("Control")
    tab.page.wait_for_timeout(50)
    assert _width(tab.state()["range"]) == pytest.approx(_width(shown) / 1.25**0.1)

    # The wheel alone is the page's: it scrolls, the chart stays as it was
    kept = tab.state()["range"]
    tab.page.mouse.wheel(0, 400)
    tab.until("window.scrollY > 0")
    assert tab.state()["range"] == kept
    assert tab.js("window.wheels") == [[True, True], [True, True], [False, False]]


def test_shift_with_a_drag_and_a_middle_button_drag_pan_within_the_whole(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs()
    tab.draw("daily", days=DAYS)
    tab.press("+", "+")
    start = tab.state()["range"]
    size = _width(start)
    tab.drag(tab.at(0.6), tab.at(0.4), shift=True)
    tab.page.wait_for_timeout(50)
    moved = tab.state()["range"]
    assert moved["min"] - start["min"] == pytest.approx(0.2 * size, rel=0.02)
    assert _width(moved) == pytest.approx(size)
    tab.drag(tab.at(0.4), tab.at(0.6), button="middle")
    tab.page.wait_for_timeout(50)
    back = tab.state()["range"]
    assert back["min"] == pytest.approx(start["min"], abs=0.01 * size)
    assert len(tab.ranges()) == 4  # two keys, two pans

    # Held within the whole: the range stops at its start
    for _ in range(4):
        tab.drag(tab.at(0.05), tab.at(0.95), shift=True)
    tab.page.wait_for_timeout(50)
    held = tab.state()["range"]
    assert held["min"] == FIRST
    assert _width(held) == pytest.approx(size)


@pytest.mark.parametrize("way", ["double click", "key 0", "button"])
def test_a_double_click_the_key_0_and_the_button_show_the_whole(
    tabs: Callable[..., Tab], way: str
) -> None:
    tab = tabs()
    tab.draw("daily", days=DAYS)
    tab.drag(tab.at(0.4), tab.at(0.6))
    assert tab.state()["range"] is not None
    if way == "double click":
        tab.page.mouse.dblclick(*tab.at(0.5))
    elif way == "key 0":
        tab.press("0")
    else:
        tab.page.click(".nogat-chart-zoom-reset")
    after = tab.state()
    assert after["range"] is None
    assert after["bar"] == {
        "zoomIn": True,
        "zoomOut": False,
        "reset": False,
        "range": None,
    }
    assert after["live"].endswith("Cały zakres")
    assert tab.ranges()[-1] is None


def test_the_lone_plus_zooms_and_comes_back_after_a_reset(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs()
    tab.draw("daily", days=DAYS)
    tab.page.click(".nogat-chart-zoom-in")
    shown = tab.state()["range"]
    assert _width(shown) == pytest.approx((DAYS - 1) / 2)
    assert (shown["min"] + shown["max"]) / 2 == pytest.approx(sum(WHOLE) / 2)
    assert tab.state()["bar"]["zoomOut"]
    tab.page.click(".nogat-chart-zoom-out")
    assert tab.state()["range"] is None
    assert tab.state()["bar"]["zoomOut"] is False
    # The button pressed left with the zoom: focus stays in the bar, on „+”
    assert tab.js("document.activeElement.classList.contains('nogat-chart-zoom-in')")
    names = tab.js(
        "[...document.querySelectorAll('.nogat-chart-zoom button')]"
        ".map((b) => b.getAttribute('aria-label') || b.textContent)"
    )
    assert names == ["Oddal", "Przybliż", "Cały zakres"]


def test_keys_zoom_around_the_readout_and_move_the_range_past_its_edge(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs()
    tab.draw("daily", days=DAYS)
    tab.press("End")
    reading = tab.state()["live"]
    assert reading.startswith(f"{_day(WHOLE[1])} · Q: ")
    tab.press("+")
    shown = tab.state()["range"]
    assert shown == {"min": WHOLE[1] - (DAYS - 1) / 2, "max": WHOLE[1]}
    # The live region says the readout, which stays on its day, and the range
    expected = f"{reading} · {_day(shown['min'])} – {_day(shown['max'])}"
    assert tab.state()["live"] == expected
    tab.press("-", "-")
    assert tab.state()["range"] is None

    tab.press("+", "+", "Home")
    before = tab.state()
    tab.press("ArrowLeft")
    after = tab.state()
    assert after["range"]["min"] == pytest.approx(
        before["range"]["min"] - _width(before["range"]) / 4
    )
    # The readout steps one day past the first day it read, the range a quarter on
    assert after["index"] == before["index"] - 1
    tab.press("0")
    assert tab.state()["range"] is None


# --- phone ---------------------------------------------------------------------------


@pytest.mark.parametrize("theme", THEMES)
def test_on_a_phone_one_finger_scrolls_or_reads_and_two_pinch_and_pan(
    tabs: Callable[..., Tab], theme: Theme
) -> None:
    tab = tabs(viewport=PHONE, touch=True, theme=theme)
    tab.draw("daily", days=DAYS, fit=False)  # a wide chart of fixed size
    host = tab.js(
        "(() => { const h = document.getElementById('chart');"
        " const s = h.querySelector('svg');"
        " return [h.clientWidth, h.scrollWidth, s.getBoundingClientRect().width,"
        " getComputedStyle(s).touchAction]; })()"
    )
    assert host[0] == host[1] == 358 and host[2] == pytest.approx(358, abs=1)
    assert host[3] == "pan-y"

    # One finger along the plot moves the readout and never selects
    start = tab.at(0.2)
    tab.touch("touchStart", [start])
    first = tab.state()["index"]
    for step in range(1, 9):
        tab.touch("touchMove", [(start[0] + 15 * step, start[1])])
    tab.js("t.frames()")
    moved = tab.state()["index"]
    tab.touch("touchEnd", [])
    assert first is not None and moved > first
    assert tab.state()["range"] is None and tab.ranges() == []

    # Two fingers apart zoom around their middle, together they pan
    middle = tab.at(0.5)
    under = tab.x_at(middle, WHOLE)
    left, right = (middle[0] - 30, middle[1]), (middle[0] + 30, middle[1])
    tab.touch("touchStart", [left, right])
    for step in range(1, 9):
        apart = 10 * step
        tab.touch(
            "touchMove", [(left[0] - apart, left[1]), (right[0] + apart, right[1])]
        )
    tab.js("t.frames()")  # moves of a touch reach the page at animation frames
    pinched = tab.state()["range"]
    assert _width(pinched) == pytest.approx((DAYS - 1) * 60 / 220, rel=0.05)
    assert tab.x_at(middle, WHOLE) == pytest.approx(under, abs=0.01 * _width(pinched))
    for step in range(1, 5):
        shift = 10 * step
        moved_to = [(left[0] - 80 + shift, left[1]), (right[0] + 80 + shift, right[1])]
        tab.touch("touchMove", moved_to)
    tab.touch("touchEnd", [])
    tab.page.wait_for_timeout(50)
    panned = tab.state()["range"]
    assert panned["min"] < pinched["min"]
    assert _width(panned) == pytest.approx(_width(pinched), rel=0.01)
    assert tab.ranges() == [{**panned, "width": tab.js("t.chart.plotWidth()")}]

    # The bar is one line, its buttons at least 24 px
    boxes = tab.js(
        "[...document.querySelectorAll('.nogat-chart-zoom > *')]"
        ".filter((e) => !e.hidden)"
        ".map((e) => { const r = e.getBoundingClientRect();"
        " return [r.top + r.height / 2, r.width, r.height, e.tagName]; })"
    )
    assert len(boxes) == 4
    assert max(box[0] for box in boxes) - min(box[0] for box in boxes) < 1
    assert all(box[1] >= 24 and box[2] >= 24 for box in boxes if box[3] == "BUTTON")

    # One finger up the plot scrolls the page; the chart stays as it was
    start = tab.at(0.5, 0.8)
    tab.touch("touchStart", [start])
    for step in range(1, 9):
        tab.touch("touchMove", [(start[0], start[1] - 20 * step)])
    tab.touch("touchEnd", [])
    tab.until("window.scrollY > 0")
    assert tab.state()["range"] == panned


def test_on_a_phone_a_chart_that_does_not_zoom_keeps_the_page_touch_and_its_width(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs(viewport=PHONE, touch=True)
    tab.draw("daily", days=300, fit=False, zoom=False)
    host = tab.js(
        "(() => { const h = document.getElementById('chart');"
        " const s = h.querySelector('svg');"
        " return [h.clientWidth, h.scrollWidth, getComputedStyle(s).touchAction]; })()"
    )
    assert host == [358, 560, "auto"]
    assert tab.state()["bar"] is None


# --- exports, callbacks, words -------------------------------------------------------


def test_to_png_draws_the_range_shown_without_the_readout_with_the_lines_under_it(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs()
    tab.draw("hydrograph", readout=True)
    tab.press("+", "ArrowRight")  # a range of 180 to 540 min, the readout at its start
    lines = [
        (
            "Źródłem pochodzenia danych jest Instytut Meteorologii i Gospodarki Wodnej"
            " – Państwowy Instytut Badawczy"
        ),
        (
            "Dane Instytutu Meteorologii i Gospodarki Wodnej – Państwowego Instytutu"
            " Badawczego zostały przetworzone"
        ),
    ]
    image = tab.js(
        """(async () => {
          const svg = t.chart.svg;
          // A GUI hides what a picture leaves out under nogat-chart-exporting
          const rule = document.styleSheets[0].insertRule(
            '.nogat-chart-exporting .peak-box { display: none; }');
          const text = t.kit.svgText(svg).text;
          const blob = await t.kit.toPng(svg, { footer: arg });
          document.styleSheets[0].deleteRule(rule);
          const bitmap = await createImageBitmap(blob);
          const canvas = new OffscreenCanvas(bitmap.width, bitmap.height);
          const context = canvas.getContext('2d');
          context.drawImage(bitmap, 0, 0);
          const box = svg.getBoundingClientRect();
          const below = context.getImageData(0, Math.round(box.height) * 2,
            bitmap.width, bitmap.height - Math.round(box.height) * 2).data;
          let ink = 0;
          for (let i = 0; i < below.length; i += 4) if (below[i] < 128) ink += 1;
          return { type: blob.type, size: [bitmap.width, bitmap.height],
                   drawn: [Math.round(box.width), Math.round(box.height)], text, ink };
        })()""",
        lines,
    )
    assert image["type"] == "image/png"
    width, height = image["drawn"]
    # Two lines under the chart: margins of 8 px and 1.4 lines of 11 px each
    assert image["size"] == [2 * width, 2 * (height + 47)]
    assert image["ink"] > 500  # the lines are written
    text = image["text"]
    assert 'class="readout' not in text and "zoom-selection" not in text
    assert re.search(r'class="peak-box"[^>]*style="[^"]*display: none', text)
    zoomed = tab.state()["xTicks"]
    assert zoomed and all(f">{tick}</text>" in text for tick in zoomed)


def test_on_range_tells_a_settled_range_and_zoom_set_takes_one_back_silently(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs()
    tab.draw("daily", days=DAYS)
    tab.js("t.chart.zoom.set(t.FIRST + 100, t.FIRST + 400)")
    assert tab.state()["range"] == {"min": FIRST + 100, "max": FIRST + 400}
    assert tab.state()["bar"]["range"] == f"{_day(FIRST + 100)} – {_day(FIRST + 400)}"
    tab.js("t.chart.zoom.reset()")
    assert tab.state()["range"] is None
    assert tab.ranges() == []

    # A range the GUI gave back (its address's) that a person resets: the GUI is told
    tab.js("t.chart.zoom.set(t.FIRST + 100, t.FIRST + 400)")
    tab.press("0")
    assert tab.ranges() == [None]
    tab.js("t.ranges.length = 0")

    # A burst of the wheel settles 200 ms after its last notch: one call
    tab.js(
        """(() => {
          const [x, y] = t.toClient((t.plot().left + t.plot().right) / 2, 100);
          const wheel = () => new WheelEvent('wheel',
            { deltaY: -50, ctrlKey: true, clientX: x, clientY: y, cancelable: true });
          for (let n = 0; n < 5; n += 1) t.chart.svg.dispatchEvent(wheel());
        })()"""
    )
    assert tab.ranges() == []
    tab.page.wait_for_timeout(350)
    assert tab.ranges() == [
        {**tab.state()["range"], "width": tab.js("t.chart.plotWidth()")}
    ]


def test_on_readout_gives_the_index_of_the_readout_series(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs()
    tab.draw("daily", days=DAYS)
    tab.press("ArrowRight", "ArrowRight", "Escape")
    tab.js("t.chart.readout.show(10)")
    assert tab.state()["index"] == 10
    tab.js("t.chart.readout.hide()")
    assert tab.js("t.readouts") == [0, 1, None, 10, None]


def test_spec_texts_replace_every_word_of_the_module(tabs: Callable[..., Tab]) -> None:
    tab = tabs()
    keys: list[str] = tab.js("Object.keys(t.kit.CHART_TEXTS)")
    texts = {key: f"<{key}>" for key in keys}
    texts["range"] = "{from} .. {to}"
    texts["rangeXY"] = "{x} {xFrom}..{xTo} {y} {yFrom}..{yTo}"
    texts["probabilityReadout"] = "P {p} T {years}"
    words: list[str] = []
    for name in ("daily", "rating", "probability"):
        tab.draw(name, texts=texts)
        tab.press("End", "+")
        words.append(
            tab.js(
                "(() => { const h = document.getElementById('chart');"
                " const names = ['aria-label', 'aria-description', 'title'];"
                " const attrs = [...h.querySelectorAll('*')].flatMap((e) =>"
                " names.map((a) => e.getAttribute(a) || ''));"
                " return [h.textContent, ...attrs].join(' | '); })()"
            )
        )
    # The error of an image the browser could not write: a canvas of no size
    words.append(
        tab.js(
            "t.kit.toPng(t.chart.svg, { scale: 0, texts: arg })"
            ".then(() => 'written', (error) => error.message)",
            texts,
        )
    )
    shown = " ".join(words)
    for word in POLISH:
        assert not re.search(rf"\b{word}\b", shown), word
    used = {key for key in keys if f"<{key}>" in shown}
    assert used == set(keys) - {"range", "rangeXY", "probabilityReadout"}
    assert re.search(r"\d{2}\.\d{2}\.\d{4} \.\. \d{2}\.\d{2}\.\d{4}", words[0])
    assert re.search(r"Q [\d,]+\.\.[\d,]+ H \d+\.\.\d+", words[1])
    assert re.search(r"P [\d,]+ T [\d,]+", words[2])


def test_a_locale_writes_numbers_and_dates_in_its_language(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs()
    tab.draw("daily", days=DAYS, locale="en-GB")
    tab.press("End", "+")
    state = tab.state()
    assert "Jan 2025" in state["xTicks"] and "Jul" in state["xTicks"]
    assert state["live"].startswith(
        "18/03/2028 · Q: 151.9\u00a0m³/s · 09/02/2024 – 18/03/2028"
    )
    # A GUI's language switch: the same data drawn again, the range kept
    tab.js("t.redraw({ locale: 'pl-PL' })")
    assert tab.state()["range"] == state["range"]
    assert "sty 2025" in tab.state()["xTicks"]


def test_a_date_format_writes_the_ticks_the_readout_and_the_bar(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs()
    tab.draw("daily", days=DAYS, dateFormat="YYYY.MM.DD")
    tab.js("t.chart.zoom.set(t.FIRST + 61, t.FIRST + 80)")
    tab.press("Home")
    state = tab.state()
    assert state["xTicks"][:3] == ["2020.03.03", "03.05", "03.07"]
    assert state["live"] == "2020.03.02"  # a day of the gap: its date alone
    assert state["bar"]["range"] == "2020.03.02 – 2020.03.21"
    tab.js("t.chart.zoom.set(t.FIRST, t.FIRST + 300)")
    assert tab.state()["xTicks"][:3] == ["2020.01", "2020.02", "2020.03"]


def test_a_time_axis_shown_under_an_hour_is_labelled_in_minutes(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs()
    tab.draw("hydrograph")
    label = (
        "[...t.chart.svg.querySelectorAll('text.axis-label')]"
        ".map((text) => text.textContent).filter((text) => text.startsWith('czas'))"
    )
    assert tab.js(label) == ["czas [h]"]
    assert tab.state()["xTicks"] == [str(hour) for hour in range(13)]
    tab.js("t.chart.zoom.set(0, 60)")
    assert tab.js(label) == ["czas [min]"]
    assert tab.state()["xTicks"] == [str(minute) for minute in range(0, 61, 5)]


# --- speed, limits, loading ----------------------------------------------------------


def test_fifty_thousand_points_draw_under_200_ms_and_a_burst_draws_once_a_frame(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs()
    times: list[float] = tab.js(
        """(() => {
          const times = [];
          for (let run = 0; run < 3; run += 1) {
            const started = performance.now();
            t.draw('daily', { days: 50000 });
            t.chart.svg.getBBox();
            times.push(performance.now() - started);
          }
          return times;
        })()"""
    )
    assert min(times) < 200, times
    drawn = tab.js(
        "(t.chart.svg.querySelector('path.ser').getAttribute('d')"
        ".match(/[ML]/g) || []).length"
    )
    assert 0 < drawn <= 5 * DESKTOP["width"]  # at most five points a column of the plot

    counts = tab.js(
        """(async () => {
          const svg = t.chart.svg;
          const plot = t.plot();
          const middle = [(plot.left + plot.right) / 2, (plot.top + plot.bottom) / 2];
          const [x, y] = t.toClient(...middle);
          const counts = [];
          t.renders = 0;
          const wheel = () => new WheelEvent('wheel',
            { deltaY: -20, ctrlKey: true, clientX: x, clientY: y, cancelable: true });
          for (let n = 0; n < 30; n += 1) svg.dispatchEvent(wheel());
          counts.push(t.renders);
          await t.frames();
          counts.push(t.renders);
          // Two fingers of a pinch, thirty moves apart
          const finger = (type, id, at) => svg.dispatchEvent(new PointerEvent(type, {
            pointerId: id, pointerType: 'touch', clientX: at, clientY: y,
            isPrimary: id === 1,
          }));
          t.renders = 0;
          finger('pointerdown', 1, x - 20);
          finger('pointerdown', 2, x + 20);
          for (let n = 1; n <= 30; n += 1) {
            finger('pointermove', 1, x - 20 - n);
            finger('pointermove', 2, x + 20 + n);
          }
          counts.push(t.renders);
          await t.frames();
          counts.push(t.renders);
          finger('pointerup', 1, x - 50);
          finger('pointerup', 2, x + 50);
          return counts;
        })()"""
    )
    assert counts == [0, 1, 0, 1]


@pytest.mark.parametrize("way", ["plus", "wheel", "drag"])
def test_every_zoom_in_stops_at_four_points_of_the_readout_series(
    tabs: Callable[..., Tab], way: str
) -> None:
    tab = tabs()
    tab.draw("daily", days=100, fixedY=True)
    if way == "plus":
        tab.press(*["+"] * 12)
    elif way == "wheel":
        tab.page.mouse.move(*tab.at(0.5))
        tab.page.keyboard.down("Control")
        for _ in range(40):
            tab.page.mouse.wheel(0, -100)
        tab.page.keyboard.up("Control")
        tab.page.wait_for_timeout(50)
    else:
        for _ in range(6):
            tab.drag(tab.at(0.45), tab.at(0.55))
    shown = tab.state()["range"]
    within = [
        day for day in range(FIRST, FIRST + 100) if shown["min"] <= day <= shown["max"]
    ]
    assert len(within) == 4, shown
    tab.press("+")
    assert tab.state()["range"] == shown


@pytest.mark.parametrize("name", ["hydrograph", "scatter"])
def test_without_a_readout_series_a_zoom_in_stops_at_a_thousandth_of_the_whole(
    tabs: Callable[..., Tab], name: str
) -> None:
    tab = tabs()
    tab.draw(name)
    tab.press("+")
    half = tab.state()["range"]
    wholes = {"x": 2 * _width(half)}
    if name == "scatter":
        wholes["y"] = 2 * _width(half["y"])
    tab.press(*["+"] * 14)
    shown = tab.state()["range"]
    assert _width(shown) == pytest.approx(wholes["x"] / 1000)
    if name == "scatter":
        assert _width(shown["y"]) == pytest.approx(wholes["y"] / 1000)
    tab.press("+")
    assert tab.state()["range"] == shown


def test_nothing_is_loaded_but_the_kit(tabs: Callable[..., Tab], site: str) -> None:
    tab = tabs()
    tab.draw("daily", days=DAYS)
    tab.drag(tab.at(0.4), tab.at(0.6))
    tab.press("End", "+")
    tab.js(
        "t.kit.toPng(t.chart.svg, { footer: ['Źródło: przykład'] }).then(() => true)"
    )
    paths = {
        url.removeprefix(site) for url in tab.requests if not url.startswith("blob:")
    }
    assert paths == {
        "/chart.html",
        "/tokens.css",
        "/kit/nogat-chart.css",
        "/page.css",
        "/chart.js",
        "/kit/nogat-chart.js",
    }


# --- drawing -------------------------------------------------------------------------


def test_a_range_survives_a_redraw_of_the_same_data_and_resets_with_new_data(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs()
    tab.draw("daily", days=DAYS)
    tab.drag(tab.at(0.4), tab.at(0.6))
    shown = tab.state()["range"]
    tab.js("t.redraw({ title: 'Inny tytuł' })")
    assert tab.state()["range"] == shown
    tab.js(
        "t.redraw({ series: [{ ...t.spec.series[0],"
        " data: t.spec.series[0].data.slice(0, 2000) }] })"
    )
    assert tab.state()["range"] is None
    assert tab.ranges() == [{**shown, "width": tab.js("t.chart.plotWidth()")}]


@pytest.mark.parametrize(
    ("name", "zooms"),
    [
        ("daily", True),
        ("hourly", True),
        ("hydrograph", True),
        ("rating", True),
        ("duration", True),
        ("probability", False),
        ("months", False),
        ("shares", False),
    ],
)
def test_a_chart_of_a_time_or_a_value_zooms_one_of_probabilities_or_months_does_not(
    tabs: Callable[..., Tab], name: str, zooms: bool
) -> None:
    tab = tabs()
    tab.draw(name)
    assert (tab.state()["bar"] is not None) == zooms
    zoomable = tab.js(
        "document.getElementById('chart').classList.contains('nogat-chart-zoomable')"
    )
    assert zoomable == zooms
    description = tab.js("t.chart.svg.getAttribute('aria-description') || ''")
    assert ("Ctrl z kółkiem myszy" in description) == zooms
    assert tab.js("t.chart.svg.getAttribute('role')") == "img"


@pytest.mark.parametrize("theme", THEMES)
@pytest.mark.parametrize("page", ["chart.html", "bare.html"])
def test_colours_follow_the_theme_and_take_the_light_tokens_without_tokens_css(
    tabs: Callable[..., Tab], theme: Theme, page: str
) -> None:
    tab = tabs(theme=theme, page=page)
    tab.draw("daily", days=300)
    colours = tab.js(
        "[getComputedStyle(document.querySelector('#chart path.ser')).stroke,"
        " getComputedStyle(document.querySelector('#chart text.tick')).fill]"
    )
    shown: Theme = theme if page == "chart.html" else "light"
    assert colours == [SERIES[shown], MUTED[shown]]


def test_a_second_unit_on_the_right_gaps_point_shapes_and_an_axis_without_labels(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs()
    tab.draw("extras")
    drawn = tab.js(
        """(() => {
          const svg = t.chart.svg;
          const plot = t.plot();
          const span = svg.querySelector('.framed > rect.span');
          return {
            plot,
            right: [...svg.querySelectorAll('text.tick[text-anchor=start]')]
              .map((tick) => [tick.textContent, Number(tick.getAttribute('x'))]),
            span: [Number(span.getAttribute('x')), Number(span.getAttribute('width'))],
            shapes: [...svg.querySelectorAll('.emp > *')]
              .map((mark) => `${mark.tagName}.${mark.getAttribute('class') || ''}`),
            xLabels: svg.querySelectorAll('text.tick[text-anchor=middle]').length,
            label: [...svg.querySelectorAll('text.axis-label')]
              .map((text) => text.textContent),
          };
        })()"""
    )
    plot = drawn["plot"]
    assert plot["left"] == 64 and drawn["xLabels"] == 0
    assert [tick[0] for tick in drawn["right"]] == ["0", "2", "4", "6", "8", "10"]
    assert all(tick[1] == plot["right"] + 6 for tick in drawn["right"])
    assert drawn["label"] == ["H [cm]", "Q [m³/s]"]
    day = (plot["right"] - plot["left"]) / 59
    assert drawn["span"][0] == pytest.approx(plot["left"] + 30 * day, abs=0.1)
    assert drawn["span"][1] == pytest.approx(5 * day, abs=0.1)
    assert drawn["shapes"] == ["circle.hollow", "path.diamond", "circle."]
    # The readout of the main series reads the right-hand axis's series too
    tab.press("ArrowRight")
    assert tab.state()["live"] == "01.01.2020 · H: 200,0\u00a0cm · Q: 3,00\u00a0m³/s"
