"""Record the providers' answers that test_basemaps.py replays (DEV-15.15).

The browser tests answer every request to a base map's provider from these
files, so they ask nothing of the network. They are recorded again when a
provider's tiles or OpenMapTiles' schema change (the shared base-maps plan,
Risks), from Nogat's root and with network access::

    uv run python tests/browser/basemaps/record.py

then the hashes and the date of `tiles` in fixtures.json are updated.
OpenFreeMap's TileJSON is kept as it comes; of its vector tile of Warsaw
only the layers the kit's grey style reads are kept, so the fixture stays
small; GUGiK's two raster tiles of Warsaw are kept as they come.
"""

from __future__ import annotations

import json
import urllib.request
from collections.abc import Iterator
from pathlib import Path

TILES = Path(__file__).resolve().parent / "tiles"
TILEJSON = "https://tiles.openfreemap.org/planet"
Z, X, Y = 8, 142, 84
GUGIK_OSM = (
    "https://mapy.geoportal.gov.pl/wss/ext/OSM/BaseMap/wmts/osm_3857/"
    f"GLOBAL_WEBMERCATOR/{Z}/{X}/{Y}.png"
)
GUGIK_ORTHO = (
    "https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WMTS/StandardResolution"
    "?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=ORTOFOTOMAPA&STYLE=default"
    f"&FORMAT=image/jpeg&TILEMATRIXSET=EPSG:3857&TILEMATRIX=EPSG:3857:{Z}"
    f"&TILEROW={Y}&TILECOL={X}"
)
# The source layers nogat-basemaps.js draws.
KEPT = {
    b"boundary",
    b"landuse",
    b"place",
    b"transportation",
    b"water",
    b"water_name",
    b"waterway",
}


def _get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "nogat-tests"})
    with urllib.request.urlopen(request, timeout=60) as response:
        body: bytes = response.read()
    return body


def _varint(data: bytes, at: int) -> tuple[int, int]:
    value = shift = 0
    while True:
        byte = data[at]
        at += 1
        value |= (byte & 0x7F) << shift
        shift += 7
        if not byte & 0x80:
            return value, at


def _fields(data: bytes) -> Iterator[tuple[int, bytes, bytes]]:
    """Each protobuf field: its number, its length-delimited value and its raw bytes."""
    at = 0
    while at < len(data):
        start = at
        key, at = _varint(data, at)
        wire = key & 7
        value = b""
        if wire == 0:
            _, at = _varint(data, at)
        elif wire == 1:
            at += 8
        elif wire == 2:
            size, at = _varint(data, at)
            value = data[at : at + size]
            at += size
        elif wire == 5:
            at += 4
        else:
            raise ValueError(f"protobuf wire type {wire}")
        yield key >> 3, value, data[start:at]


def trimmed(tile: bytes) -> bytes:
    """A vector tile with only the layers the grey style reads (field 3, named by 1)."""
    kept = bytearray()
    for number, value, raw in _fields(tile):
        if number == 3:
            name = next(v for n, v, _ in _fields(value) if n == 1)
            if name not in KEPT:
                continue
        kept += raw
    return bytes(kept)


def main() -> None:
    """Record the TileJSON and the three tiles into tiles/."""
    planet = _get(TILEJSON)
    template = json.loads(planet)["tiles"][0]
    vector = _get(template.format(z=Z, x=X, y=Y))
    (TILES / "openfreemap-planet.json").write_bytes(planet)
    (TILES / "openfreemap.pbf").write_bytes(trimmed(vector))
    (TILES / "gugik-osm.png").write_bytes(_get(GUGIK_OSM))
    (TILES / "gugik-ortho.jpg").write_bytes(_get(GUGIK_ORTHO))


if __name__ == "__main__":
    main()
