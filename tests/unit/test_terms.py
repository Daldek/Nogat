"""The terms template's builder and its reference filling (scripts/terms.py)."""

from __future__ import annotations

import pytest
import terms

VALUES = {
    "service_name": "Hydrograf",
    "service_url": "https://hydrograf.example/",
    "operator_name": "Jan Kowalski",
    "operator_email": "jan@example.org",
    "terms_effective": "2026-11-20",
    "processor": "Example Inc",
    "processor_transfer": "Dane mogą być przekazywane poza EOG.",
    "software_licence": "MIT",
    "source_url": "https://github.com/Daldek/Hydrograf",
    "tokens_href": "css/tokens.css",
    "kit_href": "nogat/",
}

SOURCE = """# Regulamin {{service_name}}

Tekst z **pogrubieniem**, `kodem` i [linkiem](mailto:{{operator_email}}).
Druga linia akapitu <https://example.org> & <{{source_url}}>.

## 1. Lista

1. Pierwszy.
<!-- block: chmi -->
2. ČHMÚ.
<!-- /block -->
3. Trzeci: {{processor}}. {{processor_transfer}}

- punkt
- drugi

> Linia pierwsza
> Linia druga

<!-- block: imgw -->
### IMGW

Dane.
<!-- /block -->

<!-- block: osm -->
Mapa.
<!-- /block -->
"""


def test_build_renders_the_subset() -> None:
    page = terms.build(SOURCE)
    assert "<title>Regulamin {{service_name}}</title>" in page
    assert "<h1>Regulamin {{service_name}}</h1>" in page
    assert (
        "<p>Tekst z <strong>pogrubieniem</strong>, <code>kodem</code> i "
        '<a href="mailto:{{operator_email}}">linkiem</a>. Druga linia akapitu '
        '<a href="https://example.org">https://example.org</a> &amp; '
        '<a href="{{source_url}}">{{source_url}}</a>.</p>'
    ) in page
    assert "<blockquote>\n<p>Linia pierwsza</p>\n<p>Linia druga</p>\n</blockquote>" in (
        page
    )
    assert "<ul>\n<li>punkt</li>\n<li>drugi</li>\n</ul>" in page
    assert "<h3>IMGW</h3>" in page


def test_build_keeps_a_list_open_across_block_markers() -> None:
    page = terms.build(SOURCE)
    assert (
        "<ol>\n<li>Pierwszy.</li>\n<!-- block: chmi -->\n<li>ČHMÚ.</li>\n"
        "<!-- /block -->\n<li>Trzeci: {{processor}}. {{processor_transfer}}</li>\n</ol>"
    ) in page


def test_build_refuses_a_source_without_a_title() -> None:
    with pytest.raises(ValueError, match="title"):
        terms.build("## no title\n")


def test_placeholders_and_blocks_of_a_template() -> None:
    page = terms.build(SOURCE)
    assert terms.placeholders(page) == {
        "service_name",
        "operator_email",
        "source_url",
        "processor",
        "processor_transfer",
        "service_url",
        "tokens_href",
        "kit_href",
    }
    assert terms.blocks(page) == ["chmi", "imgw", "osm"]


@pytest.mark.parametrize(
    ("listed", "kept"),
    [
        ([], set()),
        (["pmaxtp"], {"pmaxtp"}),
        (["chmi", "osm"], {"chmi", "osm"}),
    ],
)
def test_kept_keeps_only_the_listed_blocks(listed: list[str], kept: set[str]) -> None:
    assert terms.kept(listed) == kept


# `feedback` was a block of kit 0.2.0 and `imgw-terms` a derived one until kit
# 0.6.0: a GUI that still lists either is told so.
@pytest.mark.parametrize("name", ["imgw-terms", "feedback", "ads"])
def test_kept_refuses_unknown_blocks(name: str) -> None:
    with pytest.raises(ValueError, match=name):
        terms.kept([name])


def test_fill_keeps_listed_blocks_and_drops_the_rest() -> None:
    page = terms.fill(terms.build(SOURCE), VALUES, ["imgw"])
    assert "<li>ČHMÚ.</li>" not in page
    assert (
        "<li>Pierwszy.</li>\n"
        "<li>Trzeci: Example Inc. Dane mogą być przekazywane poza EOG.</li>"
    ) in page
    assert "<h3>IMGW</h3>" in page
    assert "Mapa." not in page
    assert "<!--" not in page.split("-->", 1)[1]
    assert "{{" not in page


def test_fill_escapes_values_in_markup_only() -> None:
    values = {**VALUES, "service_name": 'A & "B" <c>'}
    page = terms.fill(terms.build(SOURCE), values, [])
    assert "<h1>Regulamin A &amp; &quot;B&quot; &lt;c&gt;</h1>" in page
    source = terms.fill(SOURCE, values, [], markup=False)
    assert source.startswith('# Regulamin A & "B" <c>\n')


def test_fill_takes_an_empty_processor_transfer() -> None:
    page = terms.fill(terms.build(SOURCE), {**VALUES, "processor_transfer": ""}, [])
    assert "<li>Trzeci: Example Inc. </li>" in page
    assert "{{" not in page


@pytest.mark.parametrize(
    ("values", "message"),
    [
        ({k: v for k, v in VALUES.items() if k != "operator_email"}, "operator_email"),
        ({**VALUES, "operator_email": " "}, "operator_email"),
        ({**VALUES, "processor": ""}, "missing values: processor;"),
        (
            {k: v for k, v in VALUES.items() if k != "processor_transfer"},
            "missing values: processor_transfer;",
        ),
        ({**VALUES, "theme": "dark"}, "unknown values: theme"),
    ],
)
def test_fill_refuses_missing_empty_and_unknown_values(
    values: dict[str, str], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        terms.fill(terms.build(SOURCE), values, [])
