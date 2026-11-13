"""The terms template of the GUI kit: its HTML from Markdown, and how it is filled.

`design/kit/nogat-terms.md` is the source of the regulamin every GUI serves
(DEV-15.7); `build` turns it into `design/kit/nogat-terms.html`, which
`ecosystem.py standard` keeps fresh. Both carry `{{placeholder}}` fields and
optional blocks between `<!-- block: <name> -->` and `<!-- /block -->` lines.
`fill` is the reference of the filling every GUI does for its deployment.

The Markdown is a small subset: `#` to `###` headings, paragraphs, `-` and
`1.` lists (a block marker inside a list keeps it open), `>` quotes with one
line per paragraph, `**strong**`, `` `code` ``, `[text](href)` and `<href>`.
"""

from __future__ import annotations

import html
import re
from collections.abc import Iterable, Mapping
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KIT = ROOT / "design" / "kit"
SOURCE = KIT / "nogat-terms.md"
PAGE = KIT / "nogat-terms.html"

# Every placeholder of the template and where its value comes from (DEV-15.7).
PLACEHOLDERS: dict[str, str] = {
    "service_name": "project: its name in the registry, e.g. `Hydrograf`",
    "service_url": "deployment: the project's entry of `[nogat.gui]` in `nogat.toml`",
    "operator_name": "deployment: `[nogat.operator] name` in `nogat.toml`",
    "operator_email": "deployment: `[nogat.operator] email` in `nogat.toml`",
    "terms_effective": "deployment: `[nogat.operator] terms_effective` in "
    "`nogat.toml`, the date the filled terms take effect",
    "processor": "deployment: `[nogat.operator] processor` in `nogat.toml`, "
    "who carries the traffic and processes IP addresses for the operator",
    "processor_transfer": "deployment: `[nogat.operator] processor_transfer` "
    "in `nogat.toml`, the sentence on the processor's transfers outside the "
    "EEA; empty without them",
    "processor_cookie": "deployment: `[nogat.operator] processor_cookie` in "
    "`nogat.toml`, the sentence on the cookie the processor sets to protect "
    "the service from bots; empty while it sets none",
    "mail_provider": "deployment: `[nogat.operator] mail_provider` in "
    "`nogat.toml`, the service holding the operator's mailbox",
    "mail_transfer": "deployment: `[nogat.operator] mail_transfer` in "
    "`nogat.toml`, the sentence on that mail service's processing outside "
    "the EEA; empty without it",
    "software_licence": "project: `license` of its `pyproject.toml`, e.g. `MIT`",
    "source_url": "project: `repo` of its entry in `ecosystem.yaml`",
    "tokens_href": "project: the address of its copy of `tokens.css`, "
    "relative to the page",
    "kit_href": "project: the address of its copy of the kit directory with a "
    "final slash, relative to the page, e.g. `nogat/`",
}

# The only placeholders whose value may be empty (it must still be given).
OPTIONAL = frozenset({"processor_transfer", "processor_cookie", "mail_transfer"})

# Blocks a project keeps for its data sources by listing them; the rest are
# dropped (DEV-15.7).
BLOCKS: dict[str, str] = {
    "imgw": "IMGW-PIB data of danepubliczne.imgw.pl",
    "imgw-hydro": "IMGW-PIB data of hydro.imgw.pl and hydro-back.imgw.pl",
    "pmaxtp": "PMAXTP of IMGW-PIB",
    "chmi": "ČHMÚ open data",
    "gugik": "GUGiK data (geoportal.gov.pl)",
    "cuzk": "ČÚZK data",
    "copernicus": "Copernicus data (CORINE and other CLMS layers)",
    "isric": "ISRIC SoilGrids",
    "wody-polskie": "flood hazard maps of Wody Polskie",
    "osm": "OpenStreetMap basemaps (OpenFreeMap, the OSM basemap of geoportal)",
    "esri": "the Esri World Imagery basemap",
}

# Blocks that follow from the listed ones and are never listed themselves.
IMGW_BLOCKS = frozenset({"imgw", "imgw-hydro", "pmaxtp"})
DERIVED: dict[str, str] = {
    "imgw-terms": "kept with any of imgw, imgw-hydro and pmaxtp",
}

PLACEHOLDER = re.compile(r"\{\{([a-z][a-z0-9_]*)\}\}")
BLOCK_OPEN = re.compile(r"^<!-- block: ([a-z][a-z0-9-]*) -->$", re.MULTILINE)
MARKER = re.compile(r"^<!-- (?:block: (?P<name>[a-z][a-z0-9-]*)|/block) -->$")
BLOCK = re.compile(
    r"^<!-- block: (?P<name>[a-z][a-z0-9-]*) -->\n(?P<body>.*?)^<!-- /block -->\n",
    re.MULTILINE | re.DOTALL,
)
HEADING = re.compile(r"^(?P<level>#{2,3}) (?P<text>.+)$")
BULLET = re.compile(r"^- (?P<text>.+)$")
NUMBERED = re.compile(r"^\d+\. (?P<text>.+)$")
QUOTE = re.compile(r"^> (?P<text>.+)$")
INLINE = re.compile(
    r"\[(?P<text>[^\]]+)\]\((?P<href>[^)\s]+)\)"
    r"|<(?P<auto>https?://[^>\s]+|\{\{[a-z][a-z0-9_]*\}\})>"
    r"|\*\*(?P<strong>.+?)\*\*"
    r"|`(?P<code>[^`]+)`"
)

HEADER = """<!doctype html>
<!--
  Nogat GUI kit: the terms page (DEV-15.7). Generated from nogat-terms.md by
  `uv run scripts/ecosystem.py standard --write`; copy byte for byte (DEV-15.6),
  fill its fields and blocks per deployment as the kit's README says.
-->
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="{{{{tokens_href}}}}">
<link rel="stylesheet" href="{{{{kit_href}}}}nogat-terms.css">
</head>
<body>
<main class="nogat-terms">
"""

FOOTER = """</main>
<footer class="nogat-terms-footer">
<a href="{{service_url}}">Wróć do serwisu {{service_name}}</a>
</footer>
</body>
</html>
"""


def _inline(text: str) -> str:
    """Return the HTML of one line of text with its inline marks."""
    out = []
    end = 0
    for m in INLINE.finditer(text):
        out.append(html.escape(text[end : m.start()], quote=False))
        if m["text"] is not None:
            href = html.escape(m["href"])
            out.append(f'<a href="{href}">{html.escape(m["text"], quote=False)}</a>')
        elif m["auto"] is not None:
            href = html.escape(m["auto"])
            out.append(f'<a href="{href}">{html.escape(m["auto"], quote=False)}</a>')
        elif m["strong"] is not None:
            out.append(f"<strong>{html.escape(m['strong'], quote=False)}</strong>")
        else:
            out.append(f"<code>{html.escape(m['code'], quote=False)}</code>")
        end = m.end()
    out.append(html.escape(text[end:], quote=False))
    return "".join(out)


def build(source: str) -> str:
    """Return the HTML template of the Markdown terms `source`.

    Raises
    ------
    ValueError
        When the source does not start with a `#` title.
    """
    lines = source.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError("the terms must start with a `# ` title")
    title = lines[0][2:]
    body = [f"<h1>{_inline(title)}</h1>"]
    paragraph: list[str] = []
    open_list: str | None = None
    quoting = False

    def close(*, keep_list: bool = False) -> None:
        nonlocal open_list, quoting
        if paragraph:
            body.append(f"<p>{_inline(' '.join(paragraph))}</p>")
            paragraph.clear()
        if quoting:
            body.append("</blockquote>")
            quoting = False
        if open_list and not keep_list:
            body.append(f"</{open_list}>")
            open_list = None

    for line in lines[1:]:
        if MARKER.match(line):
            close(keep_list=True)
            body.append(line)
        elif not line.strip():
            close()
        elif m := HEADING.match(line):
            close()
            level = len(m["level"])
            body.append(f"<h{level}>{_inline(m['text'])}</h{level}>")
        elif (m := BULLET.match(line)) or (m := NUMBERED.match(line)):
            kind = "ul" if line.startswith("- ") else "ol"
            close(keep_list=open_list == kind)
            if open_list != kind:
                body.append(f"<{kind}>")
                open_list = kind
            body.append(f"<li>{_inline(m['text'])}</li>")
        elif m := QUOTE.match(line):
            if not quoting:
                close()
                body.append("<blockquote>")
                quoting = True
            body.append(f"<p>{_inline(m['text'])}</p>")
        else:
            if quoting or open_list:
                close()
            paragraph.append(line)
    close()
    return HEADER.format(title=html.escape(title, quote=False)) + (
        "\n".join(body) + "\n" + FOOTER
    )


def placeholders(template: str) -> set[str]:
    """Return the names of the placeholders in a template."""
    return set(PLACEHOLDER.findall(template))


def blocks(template: str) -> list[str]:
    """Return the names of the blocks of a template, in order."""
    return BLOCK_OPEN.findall(template)


def kept(listed: Iterable[str]) -> set[str]:
    """Return the blocks kept for the `listed` ones, with the derived blocks.

    Raises
    ------
    ValueError
        When a name is no block or is a derived one.
    """
    chosen = set(listed)
    unknown = sorted(chosen - set(BLOCKS))
    if unknown:
        raise ValueError(f"not a block of the terms: {', '.join(unknown)}")
    if chosen & IMGW_BLOCKS:
        chosen.add("imgw-terms")
    return chosen


def fill(
    template: str,
    values: Mapping[str, str],
    listed: Iterable[str],
    *,
    markup: bool = True,
) -> str:
    """Return the template with its blocks chosen and its placeholders filled.

    A block named in `listed` (or derived from them) keeps its lines and
    loses its two marker lines; any other block goes with its markers. Each
    `{{name}}` becomes its value, HTML-escaped when `markup` is true (the
    `.html` template) and as is for the `.md` source. Every placeholder
    needs a value; only those in `OPTIONAL` may be empty.

    Raises
    ------
    ValueError
        When a block is unknown, or a value is missing, empty or unknown.
    """
    keep = kept(listed)
    names = placeholders(template)
    missing = sorted(
        n
        for n in names
        if n not in values or (n not in OPTIONAL and not str(values[n]).strip())
    )
    unknown = sorted(set(values) - set(PLACEHOLDERS))
    if missing or unknown:
        raise ValueError(
            f"missing values: {', '.join(missing) or 'none'}; "
            f"unknown values: {', '.join(unknown) or 'none'}"
        )
    text = BLOCK.sub(
        lambda m: m["body"] if m["name"] in keep else "",
        template,
    )
    text = re.sub(r"\n{3,}", "\n\n", text)

    def value(m: re.Match[str]) -> str:
        raw = str(values[m[1]])
        return html.escape(raw) if markup else raw

    return PLACEHOLDER.sub(value, text)
