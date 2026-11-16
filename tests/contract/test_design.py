"""The shared visual identity in design/ (plan 2026-11-01-visual-identity).

Apps link design/tokens.css and the marks in design/marks/; these tests pin
what the guidelines promise them: readable text in both themes (WCAG 2.2 AA)
and one mark and one accent for every project of the registry.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import ecosystem
import pytest

DESIGN = Path(__file__).resolve().parents[2] / "design"
TOKEN = re.compile(r"--(?P<name>[a-z0-9-]+):\s*(?P<value>[^;]+);")
BLOCK = re.compile(r"(?P<selector>[^{}]+)\{(?P<body>[^{}]*)\}")
SVG = "{http://www.w3.org/2000/svg}"

# Text on background pairs the guidelines allow for body text: 4.5:1.
TEXT_PAIRS = [
    ("text", "bg"),
    ("text", "surface"),
    ("text", "surface-2"),
    ("text-2", "bg"),
    ("text-2", "surface"),
    ("text-3", "bg"),
    ("text-3", "surface"),
    ("accent", "bg"),
    ("accent", "surface"),
    ("accent-ink", "accent"),
    ("ok-ink", "ok-bg"),
    ("warn-ink", "warn-bg"),
    ("bad-ink", "bad-bg"),
    ("info-ink", "info-bg"),
    ("code-text", "code-bg"),
    ("rail-ink", "rail-bg"),
    ("rail-ink-active", "rail-active"),
]
# Focus rings and status dots are non-text UI: 3:1 (WCAG 1.4.11).
UI_PAIRS = [
    ("focus", "bg"),
    ("focus", "surface"),
    ("ok", "surface"),
    ("warn", "surface"),
    ("bad", "surface"),
    ("info", "surface"),
]


def _themes() -> tuple[dict[str, str], dict[str, str]]:
    """Return the light tokens and the dark overrides of tokens.css."""
    text = (DESIGN / "tokens.css").read_text("utf-8")
    css = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    light: dict[str, str] = {}
    dark_blocks: list[dict[str, str]] = []
    for block in BLOCK.finditer(css):
        body = block["body"]
        tokens = {m["name"]: m["value"].strip() for m in TOKEN.finditer(body)}
        if 'data-theme="dark"' in block["selector"] or ":not(" in block["selector"]:
            dark_blocks.append(tokens)
        elif block["selector"].strip().endswith(":root"):
            light.update(tokens)
    assert len(dark_blocks) == 2, "dark theme: the media query and [data-theme=dark]"
    assert dark_blocks[0] == dark_blocks[1], "both dark blocks hold the same values"
    return light, dark_blocks[0]


LIGHT, DARK_OVERRIDES = _themes()
THEMES = {"light": LIGHT, "dark": {**LIGHT, **DARK_OVERRIDES}}


def _luminance(colour: str) -> float:
    channels = [int(colour[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [
        c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(theme: dict[str, str], fg: str, bg: str) -> float:
    high, low = sorted((_luminance(theme[fg]), _luminance(theme[bg])), reverse=True)
    return (high + 0.05) / (low + 0.05)


def _projects() -> list[str]:
    return sorted(p["name"].lower() for p in ecosystem.load()["projects"])


@pytest.mark.parametrize("theme", sorted(THEMES))
@pytest.mark.parametrize(("fg", "bg"), TEXT_PAIRS, ids="-on-".join)
def test_text_pairs_meet_aa(theme: str, fg: str, bg: str) -> None:
    assert _contrast(THEMES[theme], fg, bg) >= 4.5


@pytest.mark.parametrize("theme", sorted(THEMES))
@pytest.mark.parametrize(("fg", "bg"), UI_PAIRS, ids="-on-".join)
def test_ui_pairs_meet_non_text_contrast(theme: str, fg: str, bg: str) -> None:
    assert _contrast(THEMES[theme], fg, bg) >= 3


def test_dark_theme_sets_every_light_colour() -> None:
    colours = {k for k, v in LIGHT.items() if v.startswith(("#", "rgba("))}
    # A colour the dark theme does not set would keep its light value.
    assert colours - DARK_OVERRIDES.keys() == set()


@pytest.mark.parametrize("project", _projects())
def test_every_project_has_an_accent_readable_in_both_themes(project: str) -> None:
    token = f"tool-{project}"
    # A tool accent marks text such as a name in a header: 4.5:1 on the page.
    assert _contrast(THEMES["light"], token, "surface") >= 4.5
    assert _contrast(THEMES["dark"], token, "bg") >= 4.5


@pytest.mark.parametrize("project", _projects())
def test_every_project_has_a_mark_in_the_shared_frame(project: str) -> None:
    root = ET.parse(DESIGN / "marks" / f"{project}.svg").getroot()
    frame = root.find(f"{SVG}rect")
    strokes = {e.get("stroke") for e in root.iter() if e.get("stroke")}

    assert root.get("viewBox") == "0 0 32 32"
    assert frame is not None and frame.get("fill") == LIGHT["mark-frame"]
    # The glyph is drawn in the tool's dark accent: the frame is dark in any theme.
    assert strokes == {THEMES["dark"][f"tool-{project}"]}
