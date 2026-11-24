"""The lines of DEV §20 as the tests read them (DEV-20.4, ECO-087).

DEV §20 holds three tables: the provider lines (codes, text, processed text,
order), the short forms of the strip and the terms lines. `LINES` maps every
code of the three to its line, byte for byte; `ROWS` keeps the rows of the
first in their order and `CODES` every code as the tables write it.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple

STANDARD = (
    Path(__file__).resolve().parents[1] / "standards" / "DEVELOPMENT_STANDARDS.md"
).read_text(encoding="utf-8")
CODE = r"[A-Z]{1,2}"
NONE = "—"


class Row(NamedTuple):
    """A row of the table of provider lines."""

    codes: tuple[str, ...]
    text: str
    processed: str
    order: int


ROWS = [
    Row(tuple(m["codes"].split(", ")), m["text"], m["processed"], int(m["order"]))
    for m in re.finditer(
        rf"^\| (?P<codes>{CODE}(?:, {CODE})?) \| (?P<text>[^|]+) "
        rf"\| (?P<processed>[^|]+) \| (?P<order>\d+) \|$",
        STANDARD,
        re.MULTILINE,
    )
]
_SHORT = re.findall(rf"^\| ({CODE}) \| ([^|]+) \| ({CODE}) \|$", STANDARD, re.MULTILINE)
_TERMS = re.findall(r"^\| (R[A-Z]) \| (Regulamin [^|]+) \|$", STANDARD, re.MULTILINE)

SHORT_FORMS = {code: (line, of) for code, line, of in _SHORT}
TERMS = dict(_TERMS)
CODES = [
    *(code for row in ROWS for code in row.codes),
    *(code for code, _, _ in _SHORT),
    *(code for code, _ in _TERMS),
]


def _lines() -> dict[str, str]:
    found: dict[str, str] = {}
    for row in ROWS:
        found[row.codes[0]] = row.text
        if len(row.codes) == 2:
            found[row.codes[1]] = row.processed
    found.update({code: line for code, (line, _) in SHORT_FORMS.items()})
    found.update(TERMS)
    return found


LINES = _lines()
