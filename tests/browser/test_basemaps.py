"""The kit's base maps in a browser: design/kit/nogat-basemaps.* (DEV-15.15, ECO-089).

Each adapter is tested where it runs: Chromium through Playwright, on a page
of a GUI's kind served from a throwaway directory under a CSP built from the
catalogue, `maplibreBasemap` on MapLibre GL JS 6.14.0 (Obserwator's and
Archiwista's) and `leafletBasemap` on Leaflet 1.9.4 with maplibre-gl-leaflet
0.0.22 over MapLibre GL JS 4.7.1 (Hydrograf's), vendored in basemaps/ with
their licences. Every request to a provider is answered by a route from the
recorded tiles of basemaps/tiles/, nothing from the network; a request to
another origin or for an entry the page does not offer, a tile outside its
entry's bounds, an uncaught exception, a console error other than a refused
request, or a CSP violation fails the test.
"""

from __future__ import annotations

import functools
import http.server
import json
import math
import re
import shutil
import threading
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal
from urllib.parse import parse_qs, urlsplit

import pytest
from playwright.sync_api import (
    Browser,
    Page,
    Playwright,
    Route,
    ViewportSize,
    expect,
    sync_playwright,
)

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "design" / "kit"
FIXTURES = Path(__file__).resolve().parent / "basemaps"
TILES = FIXTURES / "tiles"
CATALOGUE: list[dict[str, Any]] = json.loads(
    (KIT / "nogat-basemaps.json").read_text(encoding="utf-8")
)["entries"]
IDS = [entry["id"] for entry in CATALOGUE]
PHONE: ViewportSize = {"width": 390, "height": 844}
DESKTOP: ViewportSize = {"width": 1440, "height": 900}
Theme = Literal["light", "dark"]
THEMES: tuple[Theme, ...] = ("dark", "light")
# The strip's muted text colour, --text-3, in each theme.
MUTED = {"light": "rgb(107, 101, 101)", "dark": "rgb(139, 148, 158)"}
HALF_WORLD = 20037508.342789244
EARTH_RADIUS = 6378137

# A deployment's own base maps (`basemap_extra`), as its server hands them to the page.
WMS = (
    "https://wms.example.org/wms?SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1"
    "&LAYERS=podklad&STYLES=&FORMAT=image%2Fpng&TRANSPARENT=TRUE&SRS=EPSG:3857"
    "&WIDTH=256&HEIGHT=256&BBOX={bbox-epsg-3857}"
)
OWN: list[dict[str, Any]] = [
    {
        "id": "gmina",
        "label": "Mapa gminy",
        "kind": "raster",
        "url": "https://kafle.example.org/gmina/{z}/{x}/{y}.png",
        "origin": "https://kafle.example.org",
        "grey": False,
        "default": False,
        "credit": {"text": "© Gmina Przykładowa"},
    },
    {
        "id": "wms",
        "label": "Mapa z WMS",
        "kind": "raster",
        "url": WMS,
        "origin": "https://wms.example.org",
        "grey": True,
        "default": False,
        "credit": {"text": "WMS © Wodociągi Przykładowe"},
    },
    {
        "id": "wektor",
        "label": "Kafle wektorowe",
        "kind": "vector",
        "url": "https://wektor.example.org/tiles.json",
        "origin": "https://wektor.example.org",
        "grey": True,
        "default": False,
        "credit": {
            "text": "Kafle własne, dane © autorzy OpenStreetMap",
            "links": [["OpenStreetMap", "https://www.openstreetmap.org/copyright"]],
        },
    },
]
OWN_IDS = [entry["id"] for entry in OWN]
ENTRIES = {entry["id"]: entry for entry in CATALOGUE + OWN}


def _csp(adapter: str, own: bool) -> str:
    """The page's CSP: the origins of the catalogue's entries (and of the own ones)."""
    entries = CATALOGUE + (OWN if own else [])
    remote = " ".join(sorted({entry["origin"] for entry in entries}))
    worker = "'self'" if adapter == "maplibre" else "blob:"
    return "; ".join(
        [
            "default-src 'self'",
            "script-src 'self'",
            "style-src 'self'",
            f"worker-src {worker}",
            "child-src blob:",
            f"img-src 'self' data: blob: {remote}",
            f"connect-src 'self' {remote}",
            "font-src 'self'",
            "object-src 'none'",
            "base-uri 'none'",
            "form-action 'self'",
            "frame-ancestors 'none'",
        ]
    )


class _Site(http.server.SimpleHTTPRequestHandler):
    """The test pages; every answer, a worker's script too, has the last page's CSP."""

    csp = ""
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".mjs": "text/javascript",
        ".js": "text/javascript",
        ".pbf": "application/x-protobuf",
    }

    def log_message(self, format: str, *args: Any) -> None:
        pass

    def end_headers(self) -> None:
        parts = urlsplit(self.path)
        if parts.path.endswith(".html"):
            own = parse_qs(parts.query).get("own") == ["1"]
            _Site.csp = _csp(Path(parts.path).stem, own)
        self.send_header("Content-Security-Policy", _Site.csp)
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


@pytest.fixture(scope="module")
def site(tmp_path_factory: pytest.TempPathFactory) -> Iterator[str]:
    """The kit, the tokens, the vendored libraries and the two pages, over HTTP."""
    directory = tmp_path_factory.mktemp("basemaps")
    shutil.copytree(FIXTURES, directory, dirs_exist_ok=True)
    shutil.copytree(KIT, directory / "kit")
    shutil.copy(ROOT / "design" / "tokens.css", directory / "tokens.css")
    (directory / "own.json").write_text(json.dumps(OWN), encoding="utf-8")
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


# The providers' answers: each request is told apart by its address, checked against
# the entries the page offers and their bounds, and answered from the recorded tiles.

POLAND: list[float] = ENTRIES["gugik-ortho"]["bounds"]
WORLD = [-180.0, -85.051129, 180.0, 85.051129]
VECTOR_TILE = re.compile(r"^/planet/\w+/(\d+)/(\d+)/(\d+)\.pbf$")
OSM_TILE = re.compile(
    r"^/wss/ext/OSM/BaseMap/wmts/osm_3857/GLOBAL_WEBMERCATOR/(\d+)/(\d+)/(\d+)\.png$"
)
ORTHO = "/wss/service/PZGIK/ORTO/WMTS/StandardResolution"
OWN_XYZ = re.compile(r"^/gmina/(\d+)/(\d+)/(\d+)\.png$")
OWN_VECTOR = re.compile(r"^/t/(\d+)/(\d+)/(\d+)\.pbf$")
# Each kind of request: the entry it serves and that entry's bounds.
KINDS: dict[str, tuple[str, list[float]]] = {
    "tilejson": ("openfreemap", WORLD),
    "vector": ("openfreemap", WORLD),
    "osm": ("gugik-osm", POLAND),
    "ortho": ("gugik-ortho", POLAND),
    "gmina": ("gmina", WORLD),
    "wms": ("wms", WORLD),
    "wektor-tilejson": ("wektor", WORLD),
    "wektor": ("wektor", WORLD),
}


def _tile_box(z: int, x: int, y: int) -> list[float]:
    """The box of an XYZ tile in degrees, [west, south, east, north]."""
    n = 2**z
    assert 0 <= x < n and 0 <= y < n, f"no tile {z}/{x}/{y}"

    def lat(row: int) -> float:
        return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * row / n))))

    return [x / n * 360 - 180, lat(y + 1), (x + 1) / n * 360 - 180, lat(y)]


def _mercator_box(bbox: str) -> list[float]:
    """The box of a WMS request given in EPSG:3857, in degrees."""
    west, south, east, north = (float(value) for value in bbox.split(","))
    assert west < east and south < north, f"BBOX {bbox}"

    def lon(value: float) -> float:
        return value / HALF_WORLD * 180

    def lat(value: float) -> float:
        return math.degrees(2 * math.atan(math.exp(value / EARTH_RADIUS)) - math.pi / 2)

    return [lon(west), lat(south), lon(east), lat(north)]


def _classify(url: str) -> tuple[str, list[float] | None]:
    """The kind of a provider's request and the box it covers (None: not a tile)."""
    parts = urlsplit(url)
    origin = f"{parts.scheme}://{parts.netloc}"
    query = parse_qs(parts.query)
    tile: re.Match[str] | None = None
    if origin == "https://tiles.openfreemap.org":
        if parts.path == "/planet":
            return "tilejson", None
        if tile := VECTOR_TILE.match(parts.path):
            return "vector", _tile_box(*map(int, tile.groups()))
    if origin == "https://mapy.geoportal.gov.pl":
        if tile := OSM_TILE.match(parts.path):
            return "osm", _tile_box(*map(int, tile.groups()))
        if parts.path == ORTHO and query.get("LAYER") == ["ORTOFOTOMAPA"]:
            z = int(query["TILEMATRIX"][0].removeprefix("EPSG:3857:"))
            row, column = int(query["TILEROW"][0]), int(query["TILECOL"][0])
            return "ortho", _tile_box(z, column, row)
    if origin == "https://kafle.example.org" and (tile := OWN_XYZ.match(parts.path)):
        return "gmina", _tile_box(*map(int, tile.groups()))
    if origin == "https://wms.example.org" and query.get("REQUEST") == ["GetMap"]:
        return "wms", _mercator_box(query["BBOX"][0])
    if origin == "https://wektor.example.org":
        if parts.path == "/tiles.json":
            return "wektor-tilejson", None
        if tile := OWN_VECTOR.match(parts.path):
            return "wektor", _tile_box(*map(int, tile.groups()))
    raise AssertionError(f"a request to no entry: {url}")


def _overlaps(one: list[float], other: list[float]) -> bool:
    return (
        one[0] < other[2]
        and one[2] > other[0]
        and one[1] < other[3]
        and one[3] > other[1]
    )


def _tilejson(tiles: str) -> bytes:
    """The recorded TileJSON with its tiles at `tiles`."""
    doc = json.loads((TILES / "openfreemap-planet.json").read_text(encoding="utf-8"))
    return json.dumps({**doc, "tiles": [tiles]}).encode()


VECTOR = ("application/x-protobuf", (TILES / "openfreemap.pbf").read_bytes())
RASTER = ("image/png", (TILES / "gugik-osm.png").read_bytes())
RECORDED: dict[str, tuple[str, bytes]] = {
    "tilejson": ("application/json", (TILES / "openfreemap-planet.json").read_bytes()),
    "vector": VECTOR,
    "osm": RASTER,
    "ortho": ("image/jpeg", (TILES / "gugik-ortho.jpg").read_bytes()),
    "gmina": RASTER,
    "wms": RASTER,
    "wektor-tilejson": (
        "application/json",
        _tilejson("https://wektor.example.org/t/{z}/{x}/{y}.pbf"),
    ),
    "wektor": VECTOR,
}
# A TileJSON whose tiles leave the entry's origin.
ESCAPING = _tilejson("https://tiles.example.net/{z}/{x}/{y}.pbf")


# Whether the base map chosen last is drawn with its tiles, has failed, or is none.
SETTLED = {
    "maplibre": """t => {
      if (t.switcher.failed.includes(t.shown)) return true;
      const m = t.map;
      if (!m.getSource("nogat-basemap")) return t.shown === "none";
      return m.loaded() && m.areTilesLoaded() && m.isSourceLoaded("nogat-basemap");
    }""",
    "leaflet": """t => {
      if (t.switcher.failed.includes(t.shown)) return true;
      const layer = t.layer();
      if (!layer) return t.shown === "none";
      const gl = t.gl();
      if (gl) {
        return gl.loaded() && gl.areTilesLoaded() && gl.isSourceLoaded("nogat-basemap");
      }
      return !layer.isLoading()
        && layer.getContainer().querySelectorAll(".leaflet-tile-loaded").length > 0;
    }""",
}


@dataclass
class Tab:
    """A page of a GUI's kind and what it asked of the providers."""

    page: Page
    adapter: str
    url: str
    allowed: list[str]
    answers: dict[str, str | int] = field(default_factory=dict)
    asked: list[tuple[str, str]] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)

    def answer(self, route: Route) -> None:
        """Answer a provider's request from the recorded tiles, or as `answers` say."""
        url = route.request.url
        try:
            kind, covered = _classify(url)
        except AssertionError as error:
            self.problems.append(str(error))
            route.abort()
            return
        entry, bounds = KINDS[kind]
        if entry not in self.allowed:
            self.problems.append(f"a request for {entry}, not offered: {url}")
        if covered is not None and not _overlaps(covered, bounds):
            self.problems.append(f"a tile outside the bounds of {entry}: {url}")
        self.asked.append((kind, url))
        answer = self.answers.get(kind, "ok")
        headers = {"Access-Control-Allow-Origin": "*"}
        if answer == "abort":
            route.abort()
        elif answer == "escape":
            route.fulfill(
                body=ESCAPING, content_type="application/json", headers=headers
            )
        elif isinstance(answer, int):
            route.fulfill(status=answer, body=b"", headers=headers)
        else:
            content_type, body = RECORDED[kind]
            route.fulfill(body=body, content_type=content_type, headers=headers)

    def run(self, script: str, arg: Any = None) -> Any:
        """The value of `script`, a function of the page's `basemapTest` and `arg`."""
        return self.page.evaluate(
            f"([arg]) => ({script})(window.basemapTest, arg)", [arg]
        )

    def wait(self, script: str, arg: Any = None) -> None:
        """Wait until `script`, a function of `basemapTest` and `arg`, holds."""
        self.page.wait_for_function(
            f"([arg]) => window.basemapTest && ({script})(window.basemapTest, arg)",
            arg=[arg],
            timeout=15000,
        )

    def load(self) -> None:
        """Open the page and wait until the base map it opens on is drawn."""
        self.page.goto(self.url)
        self.wait("t => t.ready")
        self.settle()

    def settle(self) -> None:
        """Wait until the base map chosen last is drawn, has failed, or is none."""
        self.page.evaluate("() => window.basemapTest.pending")
        self.wait(SETTLED[self.adapter])

    def choose(self, entry_id: str) -> None:
        """Choose an entry in the switcher, as a person does, and wait for it."""
        self.page.locator(f'nogat-basemaps input[value="{entry_id}"]').check()
        self.settle()


@pytest.fixture
def tabs(browser: Browser, site: str) -> Iterator[Callable[..., Tab]]:
    """Open a page in a new context, its providers answered by `Tab.answer`."""
    opened: list[Tab] = []

    def open_tab(
        adapter: str,
        *,
        viewport: ViewportSize = PHONE,
        theme: Theme = "light",
        allowed: list[str] | None = None,
        own: bool = False,
        lang: str = "pl",
        answers: dict[str, str | int] | None = None,
        touch: bool = False,
        kept: str | None = None,
    ) -> Tab:
        query = [f"allowed={','.join(allowed)}"] if allowed is not None else []
        query += ["own=1"] if own else []
        query += ["lang=en"] if lang == "en" else []
        url = f"{site}/{adapter}.html" + (f"?{'&'.join(query)}" if query else "")
        context = browser.new_context(
            viewport=viewport, color_scheme=theme, has_touch=touch
        )
        if kept is not None:
            context.add_init_script(f"localStorage.setItem('nogat-basemap', '{kept}')")
        page = context.new_page()
        offered = (IDS if allowed is None else allowed) + (OWN_IDS if own else [])
        tab = Tab(page, adapter, url, offered, answers or {})

        def note(text: str, kind: str) -> None:
            if kind == "error" and not text.startswith("Failed to load resource"):
                tab.problems.append(text)

        def route(route: Route) -> None:
            if route.request.url.startswith(site):
                route.continue_()
            else:
                tab.answer(route)

        context.route("**/*", route)
        page.on("console", lambda m: note(m.text, m.type))
        page.on("pageerror", lambda e: tab.problems.append(str(e)))
        opened.append(tab)
        tab.load()
        return tab

    yield open_tab
    problems: list[str] = []
    for tab in opened:
        state = tab.page.evaluate(
            "() => { const t = window.basemapTest || {};"
            " return [t.problems || [], t.cspViolations || [], t.rejections || []]; }"
        )
        problems += [f"page: {p}" for p in state[0]]
        problems += [f"CSP: {v}" for v in state[1]]
        problems += [f"rejected: {r}" for r in state[2]]
        problems += tab.problems
        tab.page.context.close()
    assert problems == []


def _view(tab: Tab) -> list[float]:
    """The map's centre and zoom, rounded."""
    view = tab.run(
        "t => [t.map.getCenter().lng, t.map.getCenter().lat, t.map.getZoom()]"
    )
    return [round(value, 6) for value in view]


def _drawn_under_overlays(tab: Tab, entry_id: str) -> None:
    """The entry is on the map below the page's overlays, with its tiles."""
    kinds = [kind for kind, (entry, _) in KINDS.items() if entry == entry_id]
    assert any(kind in kinds for kind, _ in tab.asked), f"no tile of {entry_id}"
    entry = ENTRIES[entry_id]
    if tab.adapter == "maplibre":
        order = tab.run("t => t.map.getStyle().layers.map(l => l.id)")
        mine = [
            i for i, layer in enumerate(order) if layer.startswith("nogat-basemap-")
        ]
        assert mine and order[0] == "background" and min(mine) == 1
        assert max(mine) < order.index("overlay-fill") < order.index("overlay-point")
        if entry["kind"] == "vector":
            features = tab.run(
                "t => t.map.queryRenderedFeatures({layers: t.map.getStyle().layers"
                ".filter(l => l.id.startsWith('nogat-basemap-') && l.source)"
                ".map(l => l.id)}).length"
            )
            assert features > 0
        else:
            saturation = tab.run(
                "t => t.map.getPaintProperty("
                "'nogat-basemap-raster', 'raster-saturation')"
            )
            assert saturation == (-1 if entry["grey"] else None)
        return
    found = tab.run(
        """t => {
          const base = t.layer().getContainer();
          const overlays = t.map.getPane("overlayPane");
          return {
            pane: base.parentElement.className,
            grey: base.classList.contains("nogat-basemap-grey"),
            overlays: overlays.querySelectorAll("path").length,
            below: Number(getComputedStyle(base.parentElement).zIndex)
              < Number(getComputedStyle(overlays).zIndex),
          };
        }"""
    )
    assert found["pane"] == "leaflet-pane leaflet-tile-pane"
    assert found["below"] and found["overlays"] == 2
    if entry["kind"] == "vector":
        features = tab.run(
            "t => t.gl().queryRenderedFeatures({layers: t.gl().getStyle().layers"
            ".filter(l => l.source).map(l => l.id)}).length"
        )
        assert features > 0
    else:
        assert found["grey"] is entry["grey"]


def _credit(tab: Tab) -> dict[str, Any]:
    """The map's attribution: its text, links, size, colour, corner, whether shown."""
    box, inner = {
        "maplibre": (".maplibregl-ctrl-attrib", ".maplibregl-ctrl-attrib-inner"),
        "leaflet": (".leaflet-control-attribution", ".leaflet-control-attribution"),
    }[tab.adapter]
    found: dict[str, Any] = tab.page.evaluate(
        """([box, inner]) => {
          const control = document.querySelector(box);
          const text = document.querySelector(inner);
          const style = getComputedStyle(control);
          const corners = ".maplibregl-ctrl-bottom-right, .leaflet-right.leaflet-bottom"
            .trim();
          return {
            text: text.innerText,
            links: [...text.querySelectorAll("a")]
              .map(a => [a.textContent, a.getAttribute("href")]),
            size: style.fontSize,
            color: style.color,
            corner: control.closest(corners) !== null,
            shown: getComputedStyle(text).display !== "none"
              && text.getBoundingClientRect().width > 30 && style.fontSize !== "0px",
          };
        }""",
        [box, inner],
    )
    return found


def _href(address: str) -> str:
    """An address as a browser writes it: a bare origin gains its "/"."""
    return address + "/" if urlsplit(address).path == "" else address


def _credited(tab: Tab, entry: dict[str, Any], theme: Theme = "light") -> None:
    """The entry's own credit, not the TileJSON's, in the map's corner at 12 px."""
    credit = _credit(tab)
    assert entry["credit"]["text"] in credit["text"]
    assert "Data from" not in credit["text"]
    for word, address in entry["credit"].get("links", []):
        assert [word, _href(address)] in credit["links"]
    assert credit["size"] == "12px" and credit["color"] == MUTED[theme]
    assert credit["corner"] and credit["shown"]


@pytest.mark.parametrize("adapter", ["maplibre", "leaflet"])
@pytest.mark.parametrize("viewport", [DESKTOP, PHONE], ids=["1440", "390"])
def test_each_entry_is_drawn_under_the_overlays_with_its_credit_in_both_themes(
    tabs: Callable[..., Tab], adapter: str, viewport: ViewportSize
) -> None:
    tab = tabs(adapter, viewport=viewport)
    assert tab.run("t => t.switcher.value") == "openfreemap"
    view = _view(tab)
    for entry in CATALOGUE:
        if entry["id"] != "openfreemap":
            tab.choose(entry["id"])
        _drawn_under_overlays(tab, entry["id"])
        assert _view(tab) == view
        for theme in THEMES:
            tab.page.emulate_media(color_scheme=theme)
            _credited(tab, entry, theme)
    tab.choose("none")
    assert _view(tab) == view
    assert tab.run("t => t.failures") == []


@pytest.mark.parametrize("adapter", ["maplibre", "leaflet"])
def test_no_base_map_asks_nothing_outside_the_page(
    tabs: Callable[..., Tab], adapter: str
) -> None:
    tab = tabs(adapter, kept="none")
    assert tab.run("t => [t.switcher.value, t.shown]") == ["none", "none"]
    tab.run("t => { t.map.setZoom(t.map.getZoom() + 1); }")
    tab.page.wait_for_timeout(300)
    assert tab.asked == []
    tab.choose("gugik-osm")
    tab.choose("none")
    asked = len(tab.asked)
    tab.run("t => { t.map.panBy([200, 100], {animate: false}); }")
    tab.page.wait_for_timeout(300)
    assert len(tab.asked) == asked


@pytest.mark.parametrize("adapter", ["maplibre", "leaflet"])
@pytest.mark.parametrize(
    ("failing", "answer", "entry"),
    [
        ("tilejson", 503, "openfreemap"),
        ("ortho", "abort", "gugik-ortho"),
    ],
)
def test_a_failing_provider_is_marked_and_the_map_stays_usable(
    tabs: Callable[..., Tab], adapter: str, failing: str, answer: str | int, entry: str
) -> None:
    tab = tabs(adapter, answers={failing: answer})
    if entry != "openfreemap":
        tab.choose(entry)
    tab.wait("(t, id) => t.failures.includes(id)", entry)
    assert tab.run("t => t.failures") == [entry]
    if failing == "tilejson":
        assert tab.run("t => t.rejections.map(([id]) => id)") == [entry]
        tab.run("t => { t.rejections.length = 0; }")
    radio = tab.page.locator(f'nogat-basemaps input[value="{entry}"]')
    row = tab.page.locator("nogat-basemaps label").filter(
        has=tab.page.locator(f'input[value="{entry}"]')
    )
    expect(row).to_contain_text("Podkład nie odpowiada")
    assert tab.run("t => [t.switcher.value, t.switcher.failed]") == [entry, [entry]]
    assert radio.is_checked()
    if adapter == "maplibre":
        layers = tab.run("t => t.map.getStyle().layers.map(l => l.id)")
        assert layers == ["background", "overlay-fill", "overlay-point"]
    else:
        assert tab.run("t => t.map.getPane('tilePane').children.length") == 0
        paths = tab.run(
            "t => t.map.getPane('overlayPane').querySelectorAll('path').length"
        )
        assert paths == 2
    other = "gugik-ortho" if entry != "gugik-ortho" else "gugik-osm"
    tab.choose(other)
    _drawn_under_overlays(tab, other)
    expect(row).to_contain_text("Podkład nie odpowiada")
    tab.answers.clear()
    tab.choose(entry)
    expect(row).not_to_contain_text("Podkład nie odpowiada")
    _drawn_under_overlays(tab, entry)


@pytest.mark.parametrize("adapter", ["maplibre", "leaflet"])
def test_a_tilejson_whose_tiles_leave_the_origin_is_refused_before_any_tile(
    tabs: Callable[..., Tab], adapter: str
) -> None:
    tab = tabs(adapter, answers={"tilejson": "escape"})
    tab.wait("t => t.failures.includes('openfreemap')")
    assert tab.run("t => t.rejections") == [
        [
            "openfreemap",
            "TileJSON https://tiles.openfreemap.org/planet: "
            "tiles on https://tiles.example.net",
        ]
    ]
    tab.run("t => { t.rejections.length = 0; }")
    assert [kind for kind, _ in tab.asked] == ["tilejson"]


def _drag(tab: Tab, dx: int, dy: int) -> None:
    box = tab.page.locator("#the-map").bounding_box()
    assert box is not None
    x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    tab.page.mouse.move(x, y)
    tab.page.mouse.down()
    tab.page.mouse.move(x + dx, y + dy, steps=3)
    tab.page.mouse.up()


@pytest.mark.parametrize("adapter", ["maplibre", "leaflet"])
def test_the_credit_folds_at_the_first_drag_on_a_phone_and_a_tap_shows_it(
    tabs: Callable[..., Tab], adapter: str
) -> None:
    tab = tabs(adapter, viewport=PHONE, touch=True)
    assert _credit(tab)["shown"]
    _drag(tab, 40, 30)
    expect(
        tab.page.locator(
            ".maplibregl-ctrl-attrib-inner, .leaflet-control-attribution a"
        ).first
    ).to_be_hidden()
    assert not _credit(tab)["shown"]
    toggle = tab.page.locator(
        ".maplibregl-ctrl-attrib-button"
        if adapter == "maplibre"
        else ".nogat-basemap-credit-toggle"
    )
    expect(toggle).to_be_visible()
    toggle.tap()
    expect(toggle).to_be_visible()
    _credited(tab, ENTRIES["openfreemap"])


@pytest.mark.parametrize("adapter", ["maplibre", "leaflet"])
def test_the_credit_stays_on_a_wide_screen(
    tabs: Callable[..., Tab], adapter: str
) -> None:
    tab = tabs(adapter, viewport=DESKTOP)
    # MapLibre's control folds on `drag`, the Leaflet adapter's on `dragstart`.
    tab.run("t => { t.map.fire('dragstart'); t.map.fire('drag'); }")
    _credited(tab, ENTRIES["openfreemap"])
    toggle = ".maplibregl-ctrl-attrib-button, .nogat-basemap-credit-toggle"
    expect(tab.page.locator(toggle)).to_be_hidden()


def test_the_radios_work_by_keys(tabs: Callable[..., Tab]) -> None:
    tab = tabs("maplibre")
    group = tab.page.get_by_role("radiogroup", name="Podkład kartograficzny")
    radios = group.get_by_role("radio")
    assert radios.count() == 4
    radios.first.focus()
    tab.page.keyboard.press("ArrowDown")
    tab.settle()
    assert tab.run("t => [t.switcher.value, t.shown]") == ["gugik-osm", "gugik-osm"]
    _drawn_under_overlays(tab, "gugik-osm")
    tab.page.keyboard.press("ArrowDown")
    tab.page.keyboard.press("ArrowDown")
    tab.settle()
    assert tab.run("t => [t.switcher.value, t.shown]") == ["none", "none"]
    tab.page.keyboard.press("ArrowUp")
    tab.settle()
    assert tab.run("t => t.shown") == "gugik-ortho"
    expect(radios.nth(2)).to_be_focused()


def test_english_words_replace_the_texts_and_the_names(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs("maplibre", lang="en", answers={"osm": 503})
    group = tab.page.get_by_role("radiogroup", name="Base map")
    assert group.locator(".nogat-basemaps-label").all_inner_texts() == [
        "OpenFreeMap grey",
        "OSM GUGiK grey (Poland only)",
        "GUGiK orthophoto",
        "no base map",
    ]
    names = tab.run("t => t.map.getLayoutProperty('nogat-basemap-city', 'text-field')")
    assert names == [
        "coalesce",
        ["get", "name:en"],
        ["get", "name:latin"],
        ["get", "name"],
    ]
    expect(tab.page.locator(".maplibregl-ctrl-attrib-button")).to_have_attribute(
        "aria-label", "Show or hide the base map's credit"
    )
    tab.choose("gugik-osm")
    tab.wait("t => t.failures.includes('gugik-osm')")
    expect(group).to_contain_text("Base map not responding")
    tab.choose("openfreemap")
    _credited(tab, ENTRIES["openfreemap"])


def test_names_are_polish_by_default(tabs: Callable[..., Tab]) -> None:
    tab = tabs("maplibre")
    city = "{layers: ['nogat-basemap-city']}"
    # Tiles loaded is not labels placed: under load the symbols come frames later,
    # so wait for a repaint to end idle and for the layer's labels to be drawn.
    tab.page.evaluate(
        "() => new Promise(done => { const m = window.basemapTest.map;"
        " m.once('idle', done); m.triggerRepaint(); })"
    )
    tab.wait(f"t => t.map.queryRenderedFeatures({city}).length > 0")
    names = tab.run(
        f"t => t.map.queryRenderedFeatures({city})"
        ".map(f => f.layer.layout['text-field'].sections.map(s => s.text).join(''))"
    )
    assert "Warszawa" in names and "Warsaw" not in names


@pytest.mark.parametrize("adapter", ["maplibre", "leaflet"])
def test_a_change_of_theme_repaints_the_vector_entry(
    tabs: Callable[..., Tab], adapter: str
) -> None:
    tab = tabs(adapter)
    gl = "t.map" if adapter == "maplibre" else "t.gl()"
    paint = f"(t, [id, key]) => {gl}.getPaintProperty(id, key)"
    background = ["nogat-basemap-background", "background-color"]
    water = ["nogat-basemap-water", "fill-color"]
    city = ["nogat-basemap-city", "text-color"]
    assert tab.run(paint, background) == "#eef0f3"
    tab.page.evaluate("() => { document.documentElement.dataset.theme = 'dark'; }")
    tab.run("t => t.repaint()")
    assert tab.run(paint, background) == "#1b2028"
    assert tab.run(paint, water) == "#0f141a"
    assert tab.run(paint, city) == "#c9d1d9"
    assert _credit(tab)["color"] == MUTED["dark"]


@pytest.mark.parametrize("adapter", ["maplibre", "leaflet"])
def test_a_reload_opens_on_the_kept_choice_kept_only_in_the_browser(
    tabs: Callable[..., Tab], adapter: str, site: str
) -> None:
    tab = tabs(adapter)
    sent: list[str] = []
    tab.page.on(
        "request",
        lambda r: (
            sent.append(f"{r.method} {r.url}") if r.url.startswith(site) else None
        ),
    )
    tab.choose("gugik-ortho")
    kept = "() => localStorage.getItem('nogat-basemap')"
    assert tab.page.evaluate(kept) == "gugik-ortho"
    tab.load()
    assert tab.run("t => [t.switcher.value, t.shown]") == ["gugik-ortho", "gugik-ortho"]
    _drawn_under_overlays(tab, "gugik-ortho")
    assert tab.page.locator('nogat-basemaps input[value="gugik-ortho"]').is_checked()
    assert sent and all(r.startswith("GET ") and "ortho" not in r for r in sent)
    assert tab.page.context.cookies() == []
    tab.url = f"{site}/{adapter}.html?allowed=openfreemap,gugik-osm"
    tab.allowed = ["openfreemap", "gugik-osm"]
    tab.load()
    assert tab.run("t => [t.switcher.value, t.shown]") == ["openfreemap", "openfreemap"]
    assert tab.page.evaluate(kept) == "gugik-ortho"


def test_with_only_gugik_allowed_the_map_opens_without_a_base_map(
    tabs: Callable[..., Tab],
) -> None:
    tab = tabs("maplibre", allowed=["gugik-osm", "gugik-ortho"])
    assert tab.run("t => [t.switcher.value, t.shown]") == ["none", "none"]
    checked = tab.page.locator("nogat-basemaps input:checked")
    assert checked.get_attribute("value") == "none"
    assert tab.asked == []


def test_with_no_entry_allowed_there_is_no_switcher(tabs: Callable[..., Tab]) -> None:
    tab = tabs("maplibre", allowed=[], kept="gugik-osm")
    expect(tab.page.locator("nogat-basemaps")).to_be_hidden()
    assert tab.run("t => [t.switcher.value, t.shown]") == ["none", "none"]
    assert tab.asked == []


@pytest.mark.parametrize("adapter", ["maplibre", "leaflet"])
def test_a_deployments_own_base_maps_follow_the_catalogue_with_their_credit(
    tabs: Callable[..., Tab], adapter: str
) -> None:
    tab = tabs(adapter, own=True)
    csp = tab.page.evaluate(
        "async () => (await fetch(location.href))"
        ".headers.get('content-security-policy')"
    )
    for directive in re.findall(r"(?:img|connect)-src ([^;]+)", csp):
        sources = directive.split()
        assert "https:" not in sources and "*" not in sources
        assert {entry["origin"] for entry in OWN} <= set(sources)
    labels = tab.page.locator("nogat-basemaps .nogat-basemaps-label").all_inner_texts()
    assert labels == [
        *(entry["label"] for entry in CATALOGUE),
        *(entry["label"] for entry in OWN),
        "bez podkładu",
    ]
    for entry in OWN:
        tab.choose(entry["id"])
        _drawn_under_overlays(tab, entry["id"])
        _credited(tab, entry)
        asked = [url for kind, url in tab.asked if KINDS[kind][0] == entry["id"]]
        assert {urlsplit(url).netloc for url in asked} == {
            urlsplit(entry["origin"]).netloc
        }
    tab.load()
    assert tab.run("t => [t.switcher.value, t.shown]") == ["wektor", "wektor"]
    _drawn_under_overlays(tab, "wektor")
