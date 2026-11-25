"""The kit's catalogue of base maps, design/kit/nogat-basemaps.json (DEV-15.15).

A GUI's server reads the catalogue for its setting `basemaps`, its CSP and the
blocks of its regulamin, and its page draws the entries through the kit's
module, so the entries must have the catalogue's shape (the schema below), an
address on their origin, which the CSP names, bounds the requests stay in,
blocks the regulamin holds, the credits DEV-20.9 and the OpenStreetMap
Foundation's guideline ask for, and a default that is never one of GUGiK's
often unstable services. The browser keeps the person's choice, which the
regulamin's § 8 ust. 7 names, and the README documents what the element
observes.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import jsonschema
import pytest
import terms

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "design" / "kit"
CATALOGUE: dict[str, Any] = json.loads(
    (KIT / "nogat-basemaps.json").read_text(encoding="utf-8")
)
ENTRIES: list[dict[str, Any]] = CATALOGUE["entries"]
SCRIPT = (KIT / "nogat-basemaps.js").read_text(encoding="utf-8")
README = (ROOT / "design" / "README.md").read_text(encoding="utf-8")
STANDARD = (ROOT / "standards" / "DEVELOPMENT_STANDARDS.md").read_text(encoding="utf-8")
WORLD = (-180, -85.051129, 180, 85.051129)
# The box of GUGiK's services, Poland's (Hydrograf's orthophoto layer).
POLAND = (13.8, 48.8, 24.4, 55.0)
OSM_COPYRIGHT = "https://www.openstreetmap.org/copyright"

HTTPS = {"type": "string", "pattern": "^https://"}
SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["description", "entries"],
    "properties": {
        "description": {"type": "string", "minLength": 1},
        "entries": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/entry"}},
    },
    "$defs": {
        "entry": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "id",
                "label",
                "kind",
                "url",
                "origin",
                "minzoom",
                "maxzoom",
                "bounds",
                "grey",
                "default",
                "credit",
                "blocks",
            ],
            "properties": {
                "id": {"type": "string", "pattern": "^[a-z][a-z0-9-]*$"},
                "label": {"type": "string", "minLength": 1},
                "kind": {"enum": ["vector", "raster"]},
                "url": HTTPS,
                "origin": {"type": "string", "pattern": "^https://[^/]+$"},
                "minzoom": {"type": "integer", "minimum": 0, "maximum": 24},
                "maxzoom": {"type": "integer", "minimum": 0, "maximum": 24},
                "bounds": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 4,
                    "maxItems": 4,
                },
                "grey": {"type": "boolean"},
                "default": {"type": "boolean"},
                "credit": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["text", "links"],
                    "properties": {
                        "text": {"type": "string", "minLength": 1},
                        "links": {
                            "type": "array",
                            "items": {
                                "type": "array",
                                "prefixItems": [
                                    {"type": "string", "minLength": 1},
                                    HTTPS,
                                ],
                                "minItems": 2,
                                "maxItems": 2,
                            },
                        },
                    },
                },
                "blocks": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "uniqueItems": True,
                },
            },
        }
    },
}


def _ids(entries: list[dict[str, Any]]) -> list[str]:
    return [entry["id"] for entry in entries]


def test_the_catalogue_has_the_shape_the_gui_servers_read() -> None:
    jsonschema.Draft202012Validator.check_schema(SCHEMA)
    jsonschema.validate(CATALOGUE, SCHEMA)


def test_ids_are_unique_and_none_is_the_switchers_own() -> None:
    ids = _ids(ENTRIES)
    assert len(set(ids)) == len(ids)
    assert "none" not in ids


@pytest.mark.parametrize("entry", ENTRIES, ids=_ids(ENTRIES))
def test_an_entry_asks_only_its_https_origin(entry: dict[str, Any]) -> None:
    url = urlsplit(entry["url"])
    assert url.scheme == "https"
    assert f"{url.scheme}://{url.netloc}" == entry["origin"]


@pytest.mark.parametrize("entry", ENTRIES, ids=_ids(ENTRIES))
def test_a_raster_entry_is_a_tile_template(entry: dict[str, Any]) -> None:
    if entry["kind"] == "raster":
        assert all(part in entry["url"] for part in ("{z}", "{x}", "{y}"))
    else:
        assert "{" not in entry["url"]


@pytest.mark.parametrize("entry", ENTRIES, ids=_ids(ENTRIES))
def test_zooms_and_bounds_are_within_the_world(entry: dict[str, Any]) -> None:
    west, south, east, north = entry["bounds"]
    assert WORLD[0] <= west < east <= WORLD[2]
    assert WORLD[1] <= south < north <= WORLD[3]
    assert entry["minzoom"] <= entry["maxzoom"]


@pytest.mark.parametrize("entry", ENTRIES, ids=_ids(ENTRIES))
def test_gugik_entries_stay_within_polands_box(entry: dict[str, Any]) -> None:
    if "gugik" not in entry["blocks"]:
        return
    west, south, east, north = entry["bounds"]
    assert POLAND[0] <= west and POLAND[1] <= south
    assert east <= POLAND[2] and north <= POLAND[3]


@pytest.mark.parametrize("entry", ENTRIES, ids=_ids(ENTRIES))
def test_every_block_is_a_block_of_the_regulamin(entry: dict[str, Any]) -> None:
    source = terms.SOURCE.read_text(encoding="utf-8")
    assert set(entry["blocks"]) <= set(terms.blocks(source))


@pytest.mark.parametrize("entry", ENTRIES, ids=_ids(ENTRIES))
def test_each_link_of_a_credit_is_a_word_of_its_text(entry: dict[str, Any]) -> None:
    text = entry["credit"]["text"]
    for word, _ in entry["credit"]["links"]:
        assert word in text


@pytest.mark.parametrize("entry", ENTRIES, ids=_ids(ENTRIES))
def test_openstreetmap_is_credited_and_linked_to_its_copyright(
    entry: dict[str, Any],
) -> None:
    if "osm" not in entry["blocks"]:
        return
    assert "© autorzy OpenStreetMap" in entry["credit"]["text"]
    assert ["OpenStreetMap", OSM_COPYRIGHT] in entry["credit"]["links"]


def test_the_orthophoto_is_credited_as_dev_20_9_writes_it() -> None:
    rule = re.search(
        r"^\*\*DEV-20\.9\*\*.*?(?=^\*\*DEV-20\.10\*\*)",
        STANDARD,
        re.MULTILINE | re.DOTALL,
    )
    assert rule is not None
    quoted = re.findall(r"„([^”]+)”", " ".join(rule.group().split()))
    orthophoto = [entry for entry in ENTRIES if entry["id"] == "gugik-ortho"]
    assert [entry["credit"]["text"] for entry in orthophoto] == ["Ortofotomapa © GUGiK"]
    assert "Ortofotomapa © GUGiK" in quoted


def test_a_gugik_entry_is_never_the_default_and_the_first_entry_is() -> None:
    assert ENTRIES[0]["default"] is True
    assert all(not entry["default"] for entry in ENTRIES if "gugik" in entry["blocks"])


def test_the_regulamin_names_the_kept_base_map_among_the_browsers_settings() -> None:
    assert re.search(r'^const STORAGE = "nogat-basemap";$', SCRIPT, re.MULTILINE)
    for path in (terms.SOURCE, terms.OPERATOR_SOURCE):
        text = path.read_text(encoding="utf-8")
        rule = re.search(r"^7\. Ustawienia \(([^)]+)\)", text, re.MULTILINE)
        assert rule is not None, path.name
        assert "podkład mapy" in rule[1].split(", ")


def test_the_readme_documents_every_observed_attribute() -> None:
    observed = re.search(r"static observedAttributes = \[(?P<names>[^\]]+)\]", SCRIPT)
    assert observed is not None
    names = re.findall(r'"([a-z-]+)"', observed["names"])
    assert names == ["remember"]
    for name in names:
        assert f"| `{name}`" in README
