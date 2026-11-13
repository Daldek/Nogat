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
    "log_retention_days": "30",
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
<!-- block: feedback -->
2. Zgłoszenia.
<!-- /block -->
3. Trzeci.

- punkt
- drugi

> Linia pierwsza
> Linia druga

<!-- block: imgw -->
### IMGW

Dane.
<!-- /block -->

<!-- block: imgw-terms -->
Warunki.
<!-- /block -->

<!-- block: no-cookies -->
Bez cookie.
<!-- /block -->

<!-- block: session-cookie -->
Cookie sesji.
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
        "<ol>\n<li>Pierwszy.</li>\n<!-- block: feedback -->\n<li>Zgłoszenia.</li>\n"
        "<!-- /block -->\n<li>Trzeci.</li>\n</ol>"
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
        "service_url",
        "tokens_href",
        "kit_href",
    }
    assert terms.blocks(page) == [
        "feedback",
        "imgw",
        "imgw-terms",
        "no-cookies",
        "session-cookie",
    ]


@pytest.mark.parametrize(
    ("listed", "kept"),
    [
        ([], {"no-cookies"}),
        (["pmaxtp"], {"pmaxtp", "imgw-terms", "no-cookies"}),
        (["session-cookie", "chmi"], {"session-cookie", "chmi"}),
    ],
)
def test_kept_adds_the_derived_blocks(listed: list[str], kept: set[str]) -> None:
    assert terms.kept(listed) == kept


@pytest.mark.parametrize("name", ["imgw-terms", "no-cookies", "ads"])
def test_kept_refuses_derived_and_unknown_blocks(name: str) -> None:
    with pytest.raises(ValueError, match=name):
        terms.kept([name])


def test_fill_keeps_listed_blocks_and_drops_the_rest() -> None:
    page = terms.fill(terms.build(SOURCE), VALUES, ["imgw"])
    assert "<li>Zgłoszenia.</li>" not in page
    assert "<li>Pierwszy.</li>\n<li>Trzeci.</li>" in page
    assert "<h3>IMGW</h3>" in page
    assert "Warunki." in page
    assert "Bez cookie." in page
    assert "Cookie sesji." not in page
    assert "<!--" not in page.split("-->", 1)[1]
    assert "{{" not in page


def test_fill_escapes_values_in_markup_only() -> None:
    values = {**VALUES, "service_name": 'A & "B" <c>'}
    page = terms.fill(terms.build(SOURCE), values, [])
    assert "<h1>Regulamin A &amp; &quot;B&quot; &lt;c&gt;</h1>" in page
    source = terms.fill(SOURCE, values, [], markup=False)
    assert source.startswith('# Regulamin A & "B" <c>\n')


@pytest.mark.parametrize(
    ("values", "message"),
    [
        ({k: v for k, v in VALUES.items() if k != "operator_email"}, "operator_email"),
        ({**VALUES, "operator_email": " "}, "operator_email"),
        ({**VALUES, "theme": "dark"}, "unknown values: theme"),
    ],
)
def test_fill_refuses_missing_empty_and_unknown_values(
    values: dict[str, str], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        terms.fill(terms.build(SOURCE), values, [])
