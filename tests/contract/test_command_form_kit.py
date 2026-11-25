"""The kit's command builder, design/kit/nogat-command-form.js (DEV-15.17, ECO-093).

A GUI in another language replaces the element's words through `texts` by the
keys design/README.md gives, so the README's table of words is the module's
`COMMAND_FORM_TEXTS`, key for key and word for word, and the words the rule
quotes are the module's own. The catalog entries the element is tested on in
a browser are commands-1 documents, so the fields it reads are the schema's.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import jsonschema
import pytest
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (ROOT / "design" / "kit" / "nogat-command-form.js").read_text(encoding="utf-8")
README = (ROOT / "design" / "README.md").read_text(encoding="utf-8")
STANDARD = (ROOT / "standards" / "DEVELOPMENT_STANDARDS.md").read_text(encoding="utf-8")
SCHEMAS = ROOT / "schemas" / "agent"
CATALOGS: dict[str, Any] = json.loads(
    (ROOT / "tests" / "browser" / "command_form" / "catalogs.json").read_text(
        encoding="utf-8"
    )
)


def _texts() -> dict[str, str]:
    """COMMAND_FORM_TEXTS: each key and its string."""
    block = re.search(
        r"^export const COMMAND_FORM_TEXTS = \{\n(?P<body>.*?)^\};$",
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


def test_the_readme_gives_every_word_of_the_module_as_it_has_it() -> None:
    section = re.search(
        r"^Command builder \(DEV-15\.17.*?^Terms \(DEV-15\.7",
        README,
        re.MULTILINE | re.DOTALL,
    )
    assert section is not None
    listed = {m["key"]: m["text"] for m in WORD_ROW.finditer(section.group())}
    assert listed == TEXTS


def test_the_words_dev_15_17_quotes_are_the_modules() -> None:
    rule = re.search(
        r"^\*\*DEV-15\.17\*\*.*?(?=^\*\*|^---$)", STANDARD, re.MULTILINE | re.DOTALL
    )
    assert rule is not None
    quoted = set(re.findall(r"„([^”]+)”", rule.group()))
    assert quoted <= set(TEXTS.values())


def _validator() -> jsonschema.Draft202012Validator:
    resources = []
    for path in sorted(SCHEMAS.glob("*.schema.json")):
        contents = json.loads(path.read_text(encoding="utf-8"))
        resources.append((contents["$id"], Resource.from_contents(contents)))
    schema = json.loads((SCHEMAS / "commands-1.schema.json").read_text("utf-8"))
    registry: Registry = Registry().with_resources(resources)
    return jsonschema.Draft202012Validator(schema, registry=registry)


@pytest.mark.parametrize("key", sorted(k for k in CATALOGS if k != "_note"))
def test_the_catalogs_of_the_browser_tests_are_commands_1(key: str) -> None:
    errors = [e.message for e in _validator().iter_errors(CATALOGS[key])]
    assert errors == []
