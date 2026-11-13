"""The kit's sources strip, design/kit/nogat-sources.js (DEV-20.5, ECO-064).

The element recognises the on-screen lines byte for byte, so its copies of
them must be the lines of the table of DEV §20; its button carries the label
DEV-20.5 names; and every attribute it observes is documented for the GUIs.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (ROOT / "design" / "kit" / "nogat-sources.js").read_text(encoding="utf-8")
README = (ROOT / "design" / "README.md").read_text(encoding="utf-8")
STANDARD = (ROOT / "standards" / "DEVELOPMENT_STANDARDS.md").read_text(encoding="utf-8")
TABLE = {
    m["mark"]: m["line"]
    for m in re.finditer(
        r"^\| (?P<mark>[A-Z]{1,2}) \| (?P<line>.+) \|$", STANDARD, re.MULTILINE
    )
}
SCRIPT_LINES = {
    m["mark"]: m["line"]
    for m in re.finditer(
        r'^  (?P<mark>[A-Z]{1,2}): "(?P<line>[^"]+)",$', SCRIPT, re.MULTILINE
    )
}
RULE = re.search(
    r"^\*\*DEV-20\.5\*\*.*?(?=^\*\*DEV-20\.6\*\*)", STANDARD, re.MULTILINE | re.DOTALL
)


def test_the_element_knows_exactly_the_on_screen_lines() -> None:
    assert set(SCRIPT_LINES) == {"S", "P", "PS", "PP", "C", "CK"}


@pytest.mark.parametrize("mark", ["S", "P", "PS", "PP", "C", "CK"])
def test_each_line_is_that_of_dev_20(mark: str) -> None:
    assert SCRIPT_LINES[mark] == TABLE[mark]


def test_the_button_is_named_as_dev_20_5_says() -> None:
    assert RULE is not None
    label = re.search(r'^  button: "(?P<text>[^"]+)",$', SCRIPT, re.MULTILINE)
    assert label is not None
    assert f"„{label['text']}”" in " ".join(RULE.group().split())


def test_the_readme_documents_every_observed_attribute() -> None:
    observed = re.search(r"static observedAttributes = \[(?P<names>[^\]]+)\]", SCRIPT)
    assert observed is not None
    names = re.findall(r'"([a-z-]+)"', observed["names"])
    assert names == ["attribution", "terms-notice", "terms"]
    for name in names:
        assert f"| `{name}`" in README
