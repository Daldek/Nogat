"""The tables of provider lines of DEV §20 (DEV-20.4, ECO-087).

Producers order the lines of a product by the column Order of the table of
provider lines and name each line by its code, so the orders run from 1
without a gap or a repeat, a code names one line, a row has a processed
code exactly when it has a processed text, and a short form shortens a line
of the table.
"""

from __future__ import annotations

from provider_lines import CODES, NONE, ROWS, SHORT_FORMS


def test_the_rows_run_in_their_order_from_1_without_a_gap() -> None:
    assert ROWS
    assert [row.order for row in ROWS] == list(range(1, len(ROWS) + 1))


def test_a_code_names_one_line() -> None:
    assert len(CODES) == len(set(CODES))


def test_a_row_has_a_processed_code_exactly_with_a_processed_text() -> None:
    for row in ROWS:
        assert (len(row.codes) == 2) == (row.processed != NONE), row.codes


def test_a_short_form_shortens_a_text_of_the_table() -> None:
    texts = {row.codes[0] for row in ROWS}
    assert {of for _, of in SHORT_FORMS.values()} <= texts
