"""The kit's charts, design/kit/nogat-chart.js (DEV-15.16, ECO-090).

A GUI in another language replaces the module's words through `spec.texts`
by the keys design/README.md gives, so the README's table of words is the
module's `CHART_TEXTS`, key for key and word for word, and the words the
rule quotes are the module's own.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (ROOT / "design" / "kit" / "nogat-chart.js").read_text(encoding="utf-8")
README = (ROOT / "design" / "README.md").read_text(encoding="utf-8")
STANDARD = (ROOT / "standards" / "DEVELOPMENT_STANDARDS.md").read_text(encoding="utf-8")
# The texts of the bar's buttons „−” and „+”, beside the words of CHART_TEXTS.
GLYPHS = {"\u2212", "+"}


def _texts() -> dict[str, str]:
    """CHART_TEXTS: each key and its string, a sum of literals joined."""
    block = re.search(
        r"^export const CHART_TEXTS = \{\n(?P<body>.*?)^\};$",
        SCRIPT,
        re.MULTILINE | re.DOTALL,
    )
    assert block is not None
    entries = re.split(r"^  (\w+):", block["body"], flags=re.MULTILINE)[1:]
    return {
        key: "".join(re.findall(r'"((?:[^"\\\n]|\\.)*)"', value))
        for key, value in zip(entries[::2], entries[1::2], strict=True)
    }


TEXTS = _texts()
WORD_ROW = re.compile(
    r"^\| `(?P<key>\w+)` \| (?P<text>[^|]+) \| [^|]+ \|$", re.MULTILINE
)


def test_the_readme_gives_every_word_of_chart_texts_as_the_module_has_it() -> None:
    section = re.search(r"^Chart \(DEV-15\.16.*?^## ", README, re.MULTILINE | re.DOTALL)
    assert section is not None
    listed = {m["key"]: m["text"] for m in WORD_ROW.finditer(section.group())}
    assert listed == TEXTS


def test_the_words_dev_15_16_quotes_are_the_modules() -> None:
    rule = re.search(
        r"^\*\*DEV-15\.16\*\*.*?(?=^\*\*|^---$)", STANDARD, re.MULTILINE | re.DOTALL
    )
    assert rule is not None
    quoted = set(re.findall(r"„([^”]+)”", rule.group()))
    assert quoted == GLYPHS | {TEXTS["reset"]}
