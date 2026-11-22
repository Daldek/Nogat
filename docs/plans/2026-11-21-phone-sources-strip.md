# Plan: the sources strip folded to one line on a phone

Approved: 2026-11-21, the author (in session: „Pasek na telefonie do zwinięcia”, then the choice „Zwinąć do jednej linii” out of: fold behind „Źródła i warunki”, fold to one line, keep the lines and move the strip)

Status: steps 1 to 3 done on 2026-11-21, each full gate passed and merged into `develop`: Nogat (`5f8cce0`), Obserwator (`64f6abb`; the foot of „Stacje” at 390 × 844 px is 76 px, 143 px unfolded, against 127 px wrapped) and Hydrolog (`47d492f`). Step 4: Hydrograf merged (`3a4ecf9`, gate passed); Archiwista on its `chore/round-integration` (2026-11-22). Not deployed.

Requirements: DEV-20.5, DEV-15.4 to DEV-15.6, REL-1.4, ECO-064, ECO-072. Raised by Obserwator's open question of its 3.1.0 quick fixes: on an iPhone 13 (390 × 844 px) its „Stacje” view gives the strip 127 px, five wrapped lines over the map.

## Decision

On a screen up to 860 px wide (the kit's phone, as `nogat-app-menu.css`) the strip of `<nogat-sources>` is one line: the on-screen lines start on it and are cut with an ellipsis where they no longer fit, followed by the button „więcej”, which unfolds the strip in place (then „zwiń”), and by „Źródła i warunki”. The button shows only while the lines do not fit; wider screens are unchanged. The lines are never only in the dialog: their beginning stays on the product, one tap unfolds them where they stand.

Rejected by the author: the strip as „Źródła i warunki” only (the IMGW-PIB and PMAXTP sentences behind a dialog, rejected before by ECO-064); the lines kept wrapped and the strip moved below the view's content.

Risk, named to the author: § 5 ust. 3 and 4 of the IMGW-PIB terms and ust. 1 and 2 of the PMAXTP terms want their sentences on the product; a folded line shows their beginning, not their whole text, until it is unfolded.

## Steps

| # | Repository, branch | Change |
|---|---|---|
| 1 | Nogat, `feat/phone-sources-strip` | ECO-080, DEV-20.5 amended; `nogat-sources.js` and `.css` fold the strip, the kit's hashes; `design/README.md` „Kit”; browser tests of the folded and unfolded strip. The kit's version stays `1.0.0` (REL-1.4, ECO-072) |
| 2 | Obserwator, `feat/phone-sources-strip` | the kit's copy; its foot runs the basemap's credit after the strip only above 860 px, below it on its own line |
| 3 | Hydrolog, `feat/phone-sources-strip` | the kit's copy |
| 4 | Hydrograf, Archiwista | the kit's copy with their next change (`drift` names them until then) |

Obserwator's and Hydrolog's copies are part of `v3.1.0` and `v0.9.0`; nothing is tagged before the round ends.
