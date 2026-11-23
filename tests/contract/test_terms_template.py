"""The kit's terms template, design/kit/nogat-terms.* (DEV-15.7, ECO-061 to ECO-068).

Every GUI fills the template with the fields and blocks the kit's README
lists; these tests pin that the template, the reference filling and the
README name the same fields and blocks, that the provider lines are those
of DEV §20 and the statement of § 3 that of DEV-15.8 byte for byte, that a
data-source block holds only its provider's lines and the link to its terms
(DEV-20.7), that the version the regulamin names is the newest entry of its
history, which links the published text on `develop`, and which fields a
deployment may leave empty.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import terms
from provider_lines import LINES, STANDARD

ROOT = Path(__file__).resolve().parents[2]
SOURCE = terms.SOURCE.read_text(encoding="utf-8")
PAGE = terms.PAGE.read_text(encoding="utf-8")
README = (ROOT / "design" / "README.md").read_text(encoding="utf-8")
# The statement that opens § 3, quoted by DEV-15.8.
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
    assert set(terms.blocks(PAGE)) == set(terms.BLOCKS)
    assert terms.blocks(PAGE) == terms.blocks(SOURCE)
    assert PAGE.count("<!-- /block -->") == len(terms.blocks(PAGE))


@pytest.mark.parametrize("name", [*terms.PLACEHOLDERS, *terms.BLOCKS])
def test_the_readme_documents_every_field_and_block(name: str) -> None:
    assert f"| `{name}` |" in README


@pytest.mark.parametrize("mark", ["S", "P", "PS", "PP", "M", "C"])
def test_the_provider_lines_are_those_of_dev_20(mark: str) -> None:
    assert f"\n> {LINES[mark]}\n" in SOURCE


@pytest.mark.parametrize("mark", ["RD", "RH", "RK"])
def test_the_terms_of_imgw_pib_are_linked_as_dev_20_names_them(mark: str) -> None:
    label, address = LINES[mark].split(": ", 1)
    assert f"\n{label}: <{address}>\n" in SOURCE


def test_the_gugik_block_names_gugik_as_g_does() -> None:
    name = LINES["G"].split(", `<products>`")[0]
    assert f"<!-- block: gugik -->\n### GUGiK\n\n> {name}\n" in SOURCE


def test_no_block_offers_esri_imagery() -> None:
    # Esri's basemaps need Esri software or an ArcGIS subscription (ECO-068).
    assert "esri" not in terms.blocks(SOURCE)


# A provider's name, its required lines, then at most one link to its terms.
SOURCE_BLOCK = re.compile(
    r"### [^\n]+\n\n(?:> [^\n]+\n)+(?:\n[^<>:\n]+: <https://[^>\n]+>\n)?"
)


@pytest.mark.parametrize("name", list(terms.BLOCKS))
def test_a_source_block_holds_only_its_provider_lines_and_terms(name: str) -> None:
    block = re.search(
        rf"^<!-- block: {name} -->\n(?P<body>.*?)^<!-- /block -->$",
        SOURCE,
        re.MULTILINE | re.DOTALL,
    )
    assert block is not None
    assert SOURCE_BLOCK.fullmatch(block["body"])


def test_section_3_opens_with_the_statement_of_dev_15_8() -> None:
    assert STATEMENT is not None
    statement = " ".join(STATEMENT["text"].split())
    assert f"## 3. Charakter serwisu\n\n1. {statement}\n" in SOURCE


def test_the_version_is_the_newest_entry_of_the_history() -> None:
    body, history = SOURCE.split("\n## Historia zmian\n")
    assert "\n## " not in history
    entries = HISTORY_ENTRY.findall(history)
    assert VERSION.findall(body) == entries[:1]
    assert len(set(entries)) == len(entries)


def test_the_history_links_the_template_on_develop() -> None:
    # The published text lives on develop; main waits for the author (ECO-068).
    history = SOURCE.split("\n## Historia zmian\n")[1]
    assert history.endswith(
        ": <https://github.com/Daldek/Nogat/commits/develop/design/kit/nogat-terms.md>\n"
    )


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


# The operator's draft (DEV-15.7, ECO-079): a template whose opening comment
# the operator removes once a lawyer has reviewed the text.
OPERATOR = terms.OPERATOR_SOURCE.read_text(encoding="utf-8")
NOTICE = re.compile(r"\A<!--\n(?P<text>.*?)\n-->\n", re.DOTALL)


def _operator_copy() -> str:
    """The draft as an operator publishes it: no notice, its own fields written in."""
    copy = NOTICE.sub("", OPERATOR, count=1)
    for name in terms.BY_HAND:
        copy = copy.replace(f"{{{{{name}}}}}", "x")
    return copy


def test_the_operator_draft_says_it_is_a_template_not_legal_advice() -> None:
    notice = NOTICE.match(OPERATOR)
    assert notice is not None
    assert notice["text"].startswith("WZÓR REGULAMINU. NIE JEST PORADĄ PRAWNĄ.\n")
    assert "prawnik" in notice["text"]


def test_the_operator_draft_is_not_served_with_its_notice() -> None:
    with pytest.raises(ValueError, match="must start with a `# ` title"):
        terms.build(OPERATOR)


def test_the_operator_draft_has_the_fields_of_1_0_and_its_own() -> None:
    body = NOTICE.sub("", OPERATOR, count=1)
    assert terms.placeholders(body) == (
        set(terms.PLACEHOLDERS) - {"tokens_href", "kit_href"}
    ) | set(terms.BY_HAND)
    assert not set(terms.BY_HAND) & set(terms.PLACEHOLDERS)


@pytest.mark.parametrize("name", list(terms.BY_HAND))
def test_a_copy_keeping_a_field_of_the_operator_is_refused(name: str) -> None:
    copy = NOTICE.sub("", OPERATOR, count=1)
    for other in terms.BY_HAND:
        if other != name:
            copy = copy.replace(f"{{{{{other}}}}}", "x")
    values = dict.fromkeys(terms.PLACEHOLDERS, "x")
    with pytest.raises(ValueError, match=f"missing values: {name};"):
        terms.fill(terms.build(copy), values, [])


@pytest.mark.parametrize("name", list(terms.BY_HAND))
def test_the_readme_documents_every_field_of_the_operator(name: str) -> None:
    assert f"| `{name}` |" in README


def test_the_operator_draft_keeps_the_source_blocks_of_1_0() -> None:
    assert terms.blocks(OPERATOR) == terms.blocks(SOURCE)
    for name in terms.BLOCKS:
        pattern = rf"^<!-- block: {name} -->\n.*?^<!-- /block -->$"
        flags = re.MULTILINE | re.DOTALL
        mine = re.search(pattern, OPERATOR, flags)
        theirs = re.search(pattern, SOURCE, flags)
        assert mine is not None and theirs is not None
        assert mine[0] == theirs[0]


@pytest.mark.parametrize(
    "listed",
    [[], list(terms.BLOCKS)],
    ids=["no-block", "every-block"],
)
def test_an_operator_copy_renders_and_fills_like_1_0(listed: list[str]) -> None:
    values = dict.fromkeys(terms.PLACEHOLDERS, "x")
    page = terms.fill(terms.build(_operator_copy()), values, listed)
    assert "{{" not in page
    assert "<!-- block" not in page
    assert "WZÓR" not in page
    assert re.findall(r"<h2>(\d+)\. ", page) == [str(n) for n in range(1, 13)]
