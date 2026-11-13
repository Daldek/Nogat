"""The kit's terms template, design/kit/nogat-terms.* (DEV-15.7, ECO-061 to ECO-063).

Every GUI fills the template with the fields and blocks the kit's README
lists; these tests pin that the template, the reference filling and the
README name the same fields and blocks, that the provider lines are those
of DEV §20 and the statement of § 3 that of DEV-15.8 byte for byte, that
the version the regulamin names is the newest entry of its history, and
which fields a deployment may leave empty.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import terms

ROOT = Path(__file__).resolve().parents[2]
SOURCE = terms.SOURCE.read_text(encoding="utf-8")
PAGE = terms.PAGE.read_text(encoding="utf-8")
README = (ROOT / "design" / "README.md").read_text(encoding="utf-8")
STANDARD = (ROOT / "standards" / "DEVELOPMENT_STANDARDS.md").read_text(encoding="utf-8")
# Rows of the table of DEV §20: | Mark | Line |
LINE_ROW = re.compile(r"^\| (?P<mark>[A-Z]{1,2}) \| (?P<line>.+) \|$", re.MULTILINE)
LINES = {m["mark"]: m["line"] for m in LINE_ROW.finditer(STANDARD)}
# The statement every public GUI shows in its footer, quoted by DEV-15.8.
STATEMENT = re.search(
    r"^\*\*DEV-15\.8\*\*.*?„(?P<text>Serwis jest .+?)”",
    STANDARD,
    re.MULTILINE | re.DOTALL,
)
VERSION = re.compile(
    r"^Wersja (\d+\.\d+), obowiązuje od \{\{terms_effective\}\}$", re.MULTILINE
)
HISTORY_ENTRY = re.compile(r"^- \*\*(\d+\.\d+)\*\*: ", re.MULTILINE)


def test_the_page_is_built_from_the_source() -> None:
    assert terms.build(SOURCE) == PAGE


def test_the_page_has_exactly_the_documented_fields() -> None:
    assert terms.placeholders(PAGE) == set(terms.PLACEHOLDERS)
    assert terms.placeholders(SOURCE) == set(terms.PLACEHOLDERS) - {
        "tokens_href",
        "kit_href",
    }


def test_the_page_has_exactly_the_documented_blocks() -> None:
    assert set(terms.blocks(PAGE)) == set(terms.BLOCKS) | set(terms.DERIVED)
    assert terms.blocks(PAGE) == terms.blocks(SOURCE)
    assert PAGE.count("<!-- /block -->") == len(terms.blocks(PAGE))


@pytest.mark.parametrize("name", [*terms.PLACEHOLDERS, *terms.BLOCKS])
def test_the_readme_documents_every_field_and_block(name: str) -> None:
    assert f"| `{name}` |" in README


@pytest.mark.parametrize("mark", ["S", "P", "H", "PS", "PP", "M", "C", "N"])
def test_the_provider_lines_are_those_of_dev_20(mark: str) -> None:
    assert f"\n> {LINES[mark]}\n" in SOURCE


@pytest.mark.parametrize("mark", ["RD", "RH", "RK"])
def test_the_terms_of_imgw_pib_are_linked(mark: str) -> None:
    address = LINES[mark].removeprefix("Regulamin: ")
    assert f"Regulamin: <{address}>" in SOURCE


def test_section_3_opens_with_the_footer_statement_of_dev_15_8() -> None:
    assert STATEMENT is not None
    statement = " ".join(STATEMENT["text"].split())
    assert f"## 3. Charakter serwisu\n\n1. {statement}\n" in SOURCE


def test_the_version_is_the_newest_entry_of_the_history() -> None:
    body, history = SOURCE.split("\n## Historia zmian\n")
    assert "\n## " not in history
    entries = HISTORY_ENTRY.findall(history)
    assert VERSION.findall(body) == entries[:1]
    assert len(set(entries)) == len(entries)


def test_the_page_loads_no_script_and_nothing_remote() -> None:
    assert "<script" not in PAGE
    assert " style=" not in PAGE
    hrefs = re.findall(r'<link rel="stylesheet" href="([^"]+)">', PAGE)
    assert hrefs == ["{{tokens_href}}", "{{kit_href}}nogat-terms.css"]


@pytest.mark.parametrize(
    "listed",
    [[], list(terms.BLOCKS)],
    ids=["no-block", "every-block"],
)
def test_every_choice_of_blocks_fills_the_twelve_sections(listed: list[str]) -> None:
    values = dict.fromkeys(terms.PLACEHOLDERS, "x")
    page = terms.fill(PAGE, values, listed)
    assert "{{" not in page
    assert "<!-- block" not in page
    assert "<!-- /block" not in page
    assert re.findall(r"<h2>(\d+)\. ", page) == [str(n) for n in range(1, 13)]


@pytest.mark.parametrize(
    "name", ["processor_transfer", "processor_cookie", "mail_transfer"]
)
def test_a_deployment_may_leave_a_transfer_or_the_bot_cookie_empty(name: str) -> None:
    values = dict.fromkeys(terms.PLACEHOLDERS, "x")
    page = terms.fill(PAGE, {**values, name: ""}, [])
    assert "{{" not in page


@pytest.mark.parametrize("name", ["processor", "mail_provider"])
def test_the_processor_and_the_mail_service_are_always_named(name: str) -> None:
    values = dict.fromkeys(terms.PLACEHOLDERS, "x")
    with pytest.raises(ValueError, match=f"missing values: {name};"):
        terms.fill(PAGE, {**values, name: " "}, [])
