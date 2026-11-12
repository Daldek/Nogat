# Plan: links between the GUIs and one hand-off, stage 1 of the GUI platform

Approved: 2026-11-12, the author („przejdź do etapu 1”); the open questions
answered below by delegated authority, with the author's deployment of the
same day (question 1).

Requirements: HUB-5.2 (producers before consumers), DEV-17.4, DEV-15.1,
DEV-15.3, DEV-18.1, HUB-2.4, HUB-4.1, AGI-4.1, ECO-050, ECO-055, ECO-057;
`schemas/exchange/handoff-1.schema.json` (`nogat-handoff/1`). Stage 1 of the
[GUI platform](2026-11-01-nogat-gui-platform.md); its stage 2, the GUI hub,
waits for this plan.

## Goal

The author's request of 2026-11-12: Nogat stays without a GUI; one window for
every GUI waits. First each GUI of the ecosystem gets a menu that leads to the
others, and the hand-off by file and clipboard that already runs between them
is fixed and made the same everywhere.

1. From any GUI a person reaches every other one configured for that
   deployment in one click, from the same place of the top bar.
2. Every GUI hands data off and takes it in the same way: the same labels, file
   name, clipboard behaviour, checks and messages, from one copied piece of
   code.
3. Nogat sees which copy of its schemas, tokens and kit each project holds.

Not in this plan: one window, one sign-in, frames, a proxy (stage 2); new
hand-off directions (Hydrograf reading from Hydrolog, Obserwator's PMAXTP to
Hydrolog); visual identity steps 5 and 7 (Archiwista and Obserwator on the
tokens and the shell).

## Where it starts (2026-11-12)

Read from the `develop` (or `origin/develop`) of each repository.

| Fact | Consequence |
|---|---|
| Four GUIs on fixed local ports (PROGRESS, 2026-11-02): Obserwator 8000 (Jinja, HTMX), Hydrolog 8070 (`hydrolog gui serve`, Preact), Hydrograf 8080 (IIFE scripts), Archiwista 8090 (Preact); Hydroni (8081) and kaczawa2 (8082) are more Hydrograf instances; Hydrolog is reached through a Cloudflare tunnel, Hydrograf's production is public | addresses differ per deployment; the ports are only the local default |
| No GUI links to another: no menu, no address of another app in code; each names the others only in the hand-off labels („Wczytaj z Hydrografa”, „Kopiuj do Hydrologa”) | the menu is new everywhere |
| Hand-offs in use: Hydrograf → Hydrolog, a watershed (ADR-068) or a network with `node_provenance` (ADR-080), `hydrolog-network/1`; Archiwista → Hydrolog, a station's series (A-ADR-052, Hydrolog ADR-0020), `hydrolog-series/1`. Both by clipboard and by a `.handoff.json` file; Hydrolog opens them with „Wczytaj z …”, „Plik przekazania…”, „Wklej ze schowka”, and writes its own („Plik przekazania”, „Do schowka”) | the conventions exist; only their code is repeated |
| Three implementations: Hydrograf `frontend/js/handoff.js`, Archiwista `web/src/views/station-chart.js:277-383`, Hydrolog `gui/web/src/handoff/` and `ui/export-panel.js` | a fix or a change of the envelope is made three times |
| File names differ: Hydrograf replaces `\/:*?"<>\|` and control characters with `-`, collapses spaces, trims, falls back to `hydrograf` (`handoff.js:43-49`); Archiwista replaces only `\/:*?"<>\|`, has no fallback (`station-chart.js:327`); Hydrolog names the file after the section's file base, not the subject (`handoff/handoff.js:84-90`) | the same subject gives different names |
| Text differs: Hydrograf and Hydrolog write 2-space JSON with a final newline; Archiwista without the newline (`station-chart.js:321`) | byte-different files of the same document |
| Clipboard differs: Hydrograf falls back to a selected text field when the Clipboard API is missing or refused (`handoff.js:164-166`); Hydrolog only in a secure context (`ui/export-panel.js:66`); Archiwista calls the API without a fallback (`station-chart.js:324`) | copying fails on a plain-HTTP LAN address in Archiwista |
| Schema copies by hand: `schemas/nogat/handoff-1.schema.json` in Hydrograf and Hydrolog (`origin/develop`) is Nogat's (SHA-256 `84c6856d…`); Archiwista's `origin/develop` keeps the copy before `node_provenance` (`15c82f6a…`); Hydrograf's `schemas/nogat/README.md` names the commit and hash; `drift` checks dependency pins only, `standard` only Nogat's own copies | a copy falls behind unseen |
| Tokens: Hydrograf and Hydrolog copy `design/tokens.css` (Hydrolog with `web/nogat/nogat.json`: source, commit, SHA-256, checked by a contract test); Archiwista and Obserwator do not yet | a menu styled only by tokens looks broken in Archiwista and Obserwator today |
| `design/marks/` holds one mark per project; Hydrolog already copies four of them | the menu has its icons |

## Options

**A. Where the menu lives.**

| Option | Verdict |
|---|---|
| A1. Each app writes its own menu after a guideline | Rejected: the fourth copy of the same code |
| A2. A custom element `<nogat-app-menu>` in Nogat's kit, without shadow DOM, copied like the tokens | Recommended: one code for Preact, IIFE and Jinja pages; C2 of the platform plan puts the kit in Nogat |
| A3. A page served by Nogat or a hub listing the apps | Rejected: Nogat runs no server (author, 2026-11-12); a hub is stage 2 |

**B. Where the addresses come from.**

| Option | Verdict |
|---|---|
| B1. The registry | Rejected: no addresses or ports in `ecosystem.yaml` (HUB-2.4), and they differ per deployment |
| B2. Built-in local defaults (8000, 8070, 8080, 8090) | Rejected: wrong behind a tunnel and on the public instances |
| B3. Each deployment's configuration: `[nogat.gui]` of `nogat.toml`, one key per app (DEV-18.1 shared keys), read by Archiwista, Hydrolog and Obserwator; Hydrograf, in Docker, from an environment variable of its compose file | Recommended: one file for all apps on one machine; an app not configured is not shown |

**C. The hand-off code.** C1: a rule in the standard only; C2: the rule and a
kit module `nogat-handoff.js` that every GUI copies (recommended: the rule says
what, the module makes it the same).

## Decisions

Proposed; they wait for the author's approval.

| # | Decision |
|---|---|
| D1 | Two stages (author, 2026-11-12): this plan is stage 1; the GUI hub (one window, one sign-in) is stage 2 in the [platform plan](2026-11-01-nogat-gui-platform.md), a new project that Nogat does not host. The kit stays in Nogat, `design/kit/` (C2 there). |
| D2 | The menu: `<nogat-app-menu>` in the top bar beside the theme switch, a button „Aplikacje” with a grid icon; its list shows each configured app's mark, name and one line of what it does, the current app marked and not a link. With no other app configured the button is not drawn. On a phone the list is a sheet. |
| D3 | A menu entry opens the app in a tab named after it (`target="nogat-<tool>"`), so a second click returns to that tab instead of a new one. Whether a browser reuses the tab across origins with COOP (Hydrolog sends it, its plan D8) is checked in step 2; if not, the cost is one more tab per click. |
| D4 | Addresses (B3): `[nogat.gui]` in `nogat.toml`, `archiwista = "http://127.0.0.1:8090/"` and so on, one key per registry name in lower case; Hydrograf reads the same list from an environment variable named in its own plan. The app hands the list to its page (an API route or a value in `index.html`, its choice) and sets the element's `apps` property. No defaults. |
| D5 | The element takes its texts in Polish (DEV-15.2), the marks from the kit, and styles itself with the tokens with fallbacks (`var(--surface, #fff)`), so Archiwista and Obserwator show it before they adopt the identity. |
| D6 | The hand-off rule (new in DEV §15, profile `app`): a producer offers „Kopiuj do <app in genitive>” (clipboard) and „Plik przekazania” (file); a consumer offers „Wczytaj z <app in genitive>” with „Plik przekazania…” and „Wklej ze schowka”. The file is `<subject>.handoff.json`: `\/:*?"<>\|` and control characters become `-`, runs of white space one space, trimmed, empty becomes the producer's tool name; UTF-8, 2-space JSON, a final newline. Copying uses the Clipboard API in a secure context and otherwise, or when refused, a selected text field with Ctrl+C (Hydrograf's way). After a copy or a download the status names the target and, when the menu knows its address, links to it („Otwórz Hydrologa”). A consumer checks the envelope against its copy of `handoff-1`, the payload against its owner's schema, and names each problem in Polish by keyword (Hydrolog's messages). |
| D7 | The kit module `nogat-handoff.js` does D6: file name, text, copy with fallback, download, reading a file or the clipboard, the envelope check (a keyword validator grown from Hydrolog's `handoff/validate.js`). Building the document and checking the payload stay each app's: they know the domain. |
| D8 | Kit 0.1 (`design/kit/`): `nogat-app-menu.js`, `nogat-app-menu.css`, `nogat-handoff.js`, `nogat-kit.json` (kit version, SemVer, and SHA-256 per file); the menu takes the marks of `design/marks/`. File names carry `nogat-` so a copy is found by its name beside an app's own `handoff.js`. Plain ES modules (DEV-15.1); Hydrograf loads them with `<script type="module">` beside its IIFE scripts. A project copies kit files byte for byte and never edits them; the copied `nogat-kit.json` names the kit version, and `drift` finds the Nogat commit by hash (D9), so no per-copy manifest is needed. |
| D9 | Copies are checked: `drift` (HUB-4.1) gains a report of each project's copies of `schemas/agent/`, `schemas/exchange/`, `standards/error_registry.json`, `design/tokens.css`, `design/marks/` and kit files in the sibling checkouts: current, behind (an older Nogat file, its commit named) or modified (no Nogat commit has it). A token copy's leading `Copied from Nogat …` comment (DEV-15.3) is left out of the hash. ECO-050 names `schemas/exchange/` beside `schemas/agent/`. The copies are no registry edges, as today. |

## Steps

Producers before consumers (HUB-5.2): Nogat's rule and kit, then each GUI in
its own session on a topic branch (DEV-3.4), with its gate, ADR, CHANGELOG and
PROGRESS. Sizes are estimates in sessions.

| # | Owner | Step | Size | Verified by |
|---|---|---|---|---|
| 1 | Nogat | An ECO decision (D1 to D9; stage 2 and C1, C2 of the platform plan); the hand-off rule and the menu rule in DEV §15; DEV-18.1 names `[nogat.gui]`; ECO-050 names `schemas/exchange/` | 1 | gate: `standard` |
| 2 | Nogat | Kit 0.1 (D8): `nogat-app-menu.*`, `nogat-handoff.js`, `nogat-kit.json`; the menu in the specimen and both mockups; browser tests (Playwright, as Hydrolog's e2e) of the menu, the tab reuse of D3 across two origins, the file name, the text and the copy fallback | 2 | the specimen with the menu in both themes and on a phone; tests green |
| 3 | Nogat | The copy report in `drift` (D9) | 1 | `drift` names Archiwista's `handoff-1` copy behind and Hydrograf's tokens behind or current |
| 4 | Hydrolog | Kit copy; the menu in its top bar; `nogat-handoff.js` instead of its own file, text and clipboard code; the file named after the subject; `[nogat.gui]` read and given to the page | 1-1.5 | its e2e: the menu, a hand-off from Hydrograf's and Archiwista's fixtures opens as before |
| 5 | Hydrograf | Kit copy; the menu; `nogat-handoff.js` in `frontend/js/handoff.js`; the address list from its compose file into the page | 1-1.5 | a copied and a downloaded hand-off open in Hydrolog; the same bytes as before except the name rule |
| 6 | Archiwista | Kit copy; the menu in its shell; `nogat-handoff.js` on the station card (the copy fallback, the final newline, the name rule); `handoff-1` copied again; `[nogat.gui]` | 1-1.5 | its e2e of the station card; copying works on a plain-HTTP address |
| 7 | Obserwator | Kit copy; the menu in `templates/base.html`; `[nogat.gui]` (question 3) | 0.5 | the web pages show the menu |
| 8 | Nogat | Results, PROGRESS, CHANGELOG; `drift` shows every copy current | 0.5 | gate |

About 8.5 to 10 sessions. Steps 4 to 7 are independent of each other after
step 2; step 3 may run beside them.

## Risks

| Risk | Effect | Mitigation |
|---|---|---|
| A menu that points nowhere | a link to a stopped app or a wrong address | only configured apps are shown (D4); a failed page is the browser's, the menu promises nothing more |
| Tabs not reused across origins (D3) | one more tab per click | checked in step 2; accepted if so |
| Kit copies drift | the menu and the hand-off split again | `nogat-kit.json` hashes, the report of step 3 |
| The new name rule changes a file name a person relies on | an old file keeps its name; a new one is named differently in Hydrolog | the content does not change; only Hydrolog's names move to the subject |
| Stage 1 work done twice by stage 2 | effort lost | none of it is: stage 2 keeps the menu (hidden in the embedded mode), `nogat-handoff.js` and the copy report, and adds `nogat:handoff` through the shell |

## Answers to the open questions (2026-11-12)

1. Addresses per deployment. The public test deployment the author chose on
   2026-11-12 lists Hydrograf (Kaczawa only, no Hydroni), Hydrolog and
   Archiwista (browsing only, downloads off); the workstation lists its
   local ports. Obserwator's web pages are in neither public list.
2. A tab per app (D3), as recommended; step 2 records what browsers do.
3. Yes: step 7 is half a session, and the pages serve until stage 2 (B6).
4. „Aplikacje”, as proposed. Nogat has no GUI, so its mark is not in the
   menu.

## Results

- 2026-11-12, step 1 (branch `plan/gui-hub`): ECO-058; DEV-15.4 (the app
  menu), DEV-15.5 (the hand-off), DEV-15.6 (copies byte for byte, reported
  by `drift`); DEV-18.1 names the table `gui` of `[nogat]`; HUB-1.1 names
  `schemas/exchange/` and `design/` and says Nogat runs no GUI; ECO-050
  amended; the standard's changelog.
- 2026-11-12, step 2: kit 0.1.0 in `design/kit/` (`nogat-app-menu.js`,
  `nogat-app-menu.css`, `nogat-handoff.js`, `nogat-kit.json`); the menu in
  the specimen and both mockups (seen in Chromium at 1440 px light and dark
  and at 390 px); `tests/browser/test_kit.py` (Playwright 1.65.1 in the dev
  group, Chromium installed by CI) checks the menu, the file name, the text,
  the clipboard and its fallback outside a secure context, and the schema
  check against Python's `jsonschema` on 53 keyword cases and 20 envelope
  cases; `tests/contract/test_kit_manifest.py` checks the manifest. D3
  measured in Chromium 158 with two origins and three clicks on one entry:
  two tabs without COOP (the tab is reused), three when either page sends
  `Cross-Origin-Opener-Policy: same-origin` (one extra tab); Hydrolog sends
  it, so links from and to Hydrolog cost that tab.
- 2026-11-12, step 3: `drift` prints a copies table after the pins
  (`copy_rows` in `scripts/ecosystem.py`, tests in
  `tests/integration/test_workspace.py` and `tests/unit/test_ecosystem.py`);
  HUB-4.1 names it. First run on the workspace checkouts: behind are
  Archiwista's `handoff-1` (`8727f6e`, before `node_provenance`),
  Hydrograf's `tokens.css` (`29e7e1c`), the `error_registry.json` of
  Archiwista, Hydrograf, Hydrolog and Retman (`bc72b92`), and Hydrolog's
  `handoff-1` in its local checkout (`chore/pins-candidate-2`; its
  `origin/develop` holds the current one); everything else current.
