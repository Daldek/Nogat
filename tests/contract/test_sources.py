"""The kit's sources strip, design/kit/nogat-sources.js (DEV-20.5, ECO-064, ECO-071).

The element recognises the on-screen lines byte for byte, the values of G and
Z by their place, so its copies of them and CP must be the lines of the
tables of DEV §20, and it shows them in the order of the table of provider
lines (DEV-20.4); its button carries the label DEV-20.5 names; and every
attribute it observes is documented for the GUIs.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from provider_lines import LINES, ROWS, SHORT_FORMS, STANDARD

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (ROOT / "design" / "kit" / "nogat-sources.js").read_text(encoding="utf-8")
README = (ROOT / "design" / "README.md").read_text(encoding="utf-8")
SCRIPT_LINES = {
    m["mark"]: m["line"]
    for m in re.finditer(
        r'^  (?P<mark>[A-Z]{1,2}): "(?P<line>[^"]+)",$', SCRIPT, re.MULTILINE
    )
}
RULE = re.search(
    r"^\*\*DEV-20\.5\*\*.*?(?=^\*\*DEV-20\.6\*\*)", STANDARD, re.MULTILINE | re.DOTALL
)


# The lines shown, the full lines whose short forms are shown, and CP and WP in the
# dialog.
KNOWN = [
    *("S", "P", "PS", "PP", "C", "CK", "CP", "W", "WK", "WP"),
    *("G", "GK", "SG", "SK", "Z", "ZK"),
]


def test_the_element_knows_exactly_the_provider_lines_it_recognises() -> None:
    assert set(SCRIPT_LINES) == set(KNOWN)


@pytest.mark.parametrize("mark", KNOWN)
def test_each_line_is_that_of_dev_20(mark: str) -> None:
    assert SCRIPT_LINES[mark] == LINES[mark]


def test_the_strip_shows_its_lines_as_the_tables_say_in_their_order() -> None:
    screen = re.search(r"^const SCREEN = \{ (?P<pairs>[^}]+) \};$", SCRIPT, re.M)
    assert screen is not None
    shown = dict(re.findall(r'(\w+): "(\w+)"', screen["pairs"]))
    order = [code for row in ROWS for code in row.codes]
    assert list(shown) == [code for code in order if code in shown]
    for full, form in shown.items():
        assert form == full or SHORT_FORMS[form][1] == full


def test_the_button_is_named_as_dev_20_5_says() -> None:
    assert RULE is not None
    label = re.search(r'^  button: "(?P<text>[^"]+)",$', SCRIPT, re.MULTILINE)
    assert label is not None
    assert f"„{label['text']}”" in " ".join(RULE.group().split())


def test_the_readme_documents_every_observed_attribute() -> None:
    observed = re.search(r"static observedAttributes = \[(?P<names>[^\]]+)\]", SCRIPT)
    assert observed is not None
    names = re.findall(r'"([a-z-]+)"', observed["names"])
    assert names == ["attribution", "terms-notice", "terms", "screen-lines"]
    for name in names:
        assert f"| `{name}`" in README
