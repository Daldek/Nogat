# Plan: Hydrolog's GUI across the projects

Approved: 2026-11-02 (the author, with Hydrolog's plan, the choices on the
mockup's open questions and its deviations)

Requirements: HUB-5.2, DEV-17.4, DEV-3.4, DEV-15.1, DEV-15.3, ECO-050,
ECO-055. A pointer: the work and its decisions are Hydrolog's plan
[`docs/plans/2026-11-02-hydrolog-gui.md`](https://github.com/Daldek/Hydrolog/blob/feature/gui/docs/plans/2026-11-02-hydrolog-gui.md)
on Hydrolog's branch `feature/gui` (not pushed yet). This file lists the
projects in their order, producers first, and what the work proposes to
Nogat. It builds on the approved [mockup](../../design/mockups/hydrolog/index.html)
(`ed3473c`) and carries out steps 11 and 15 of the pending
[platform plan](2026-11-01-nogat-gui-platform.md), standalone first.

## Goal

The author's decisions of 2026-11-01: Hydrolog's GUI is a module of Nogat's
GUI platform and also runs alone. Five sections (Hydrogram zlewni with live
recompute, Sieć i trasowanie with the vertical schematic, Statystyka
przepływów, Kalkulatory, Wszystkie polecenia from the catalog), the layout
Dane | Wykresy | Wyniki, exports (CSV, JSON, Markdown report and print, PNG,
CLI line), hand-off with Hydrograf in `nogat-handoff/1` carrying
`hydrolog-network/1`, (i) explanations, both themes and phones. Alone it
serves 127.0.0.1:8070 (`hydrolog gui serve`), where a Cloudflare tunnel
already points.

## Order of the projects

| # | Project | Step | Size | Verified by | Before |
|---|---|---|---|---|---|
| N1 | Nogat | `schemas/exchange/handoff-1.schema.json` as item 6 of the platform plan describes it (`schema`, `created_at`, `producer`, `subject`, `provenance`, a `payload` of `hydrolog-network/1`, an optional `result`), with its contract test; pulled forward from step 1 | 0.5 | `scripts/gate.sh`; a complete form of the example in Hydrolog's plan (D15) validates | Hydrolog's S6 |
| H | Hydrolog | the GUI by its plan, in three waves: S0 catalog additions, S1 server, S2 and S2b frontend foundation and charts; S3 to S5 the sections; S6 hand-off, report and print, S7 guide and docs | 18.5-22.5 | Hydrolog's gate with Playwright tests; the smoke through the tunnel | – |
| N2 | Nogat | registry: Hydrolog's interface `gui` (`hydrolog gui serve`) and a route „Open Hydrolog's GUI in the browser”, then `agents`; PROGRESS | 0.5 | `validate`, `agents --check` | after Hydrolog's S0 |
| G | Hydrograf | „Przenieś do Hydrologa” and „Wczytaj z Hydrologa” with the field mapping (`Lc_km`, slope in %); step 12 of the platform plan, its own plan | its plan | the same request after a round trip | after N1 |

Until G exists, Hydrolog's „Wczytaj z Hydrografa” reads hand-off files only
(its own, or written by hand). Hydrograf computes with Hydrolog 0.6.3 in
production; a hand-off carries the producer's version and result, and
Hydrolog shows them beside its own numbers.

## What the work proposes to the platform

Inputs to steps 1, 3 and 8 of the platform plan, not decided here:

- The module: the entry point group `nogat.gui` names
  `hydrolog.gui:gui_module`, which returns `name`, `title`, the directory of
  the static files, the index page, the five sections and the ASGI app
  factory. The page uses relative URLs only and calls its routes under
  `api/` relative to itself; the routes are generic over commands-1
  (commands, one command's schema, JSON Schemas, run, format, files of a
  per-session work directory), so the host either mounts Hydrolog's app or
  answers them from its catalog bridge.
- The theme key is `nogat-theme`, as in the mockup, Hydrograf and the
  specimen; [design/README.md](../../design/README.md#theme) still names
  `theme`, which kit 0.1 settles.
- Until the kit exists, Hydrolog copies only `tokens.css` and marks from
  `29e7e1c` with SHA-256 per file; its form model, chart scales and
  schematic layout transform are pure ES modules that `<nogat-command-form>`,
  `chart-theme.js` and `<nogat-schematic>` can take over.
- The embedded mode: `?nogat=1` hides the chrome at first paint; the
  handshake waits for the kit's `embed.js`.

## The author's answers of 2026-11-02

1. N1 ahead of the rest of the platform plan: approved; recorded in the
   [platform plan](2026-11-01-nogat-gui-platform.md).
2. The tunnel's public address (to 127.0.0.1:8070) is behind Cloudflare
   Access, set up by the author; the GUI has no sign-in of its own.

## Results

- N1, 2026-11-02: `nogat-handoff/1` in
  [`schemas/exchange/handoff-1.schema.json`](../../schemas/exchange/handoff-1.schema.json);
  its example is the complete form of D15 in Hydrolog's plan (the
  watershed of Hydrogram's defaults), whose payload validates against
  `hydrolog-network/1` and through `hydrolog route network` gives the outlet
  peak 60.2148 m³/s at 380 min and 1,046,213.2 m³, the values of its
  `result`. Contract test `tests/contract/test_handoff_schema.py`; branch
  `feature/handoff-1`, not merged, not pushed.
- N2, 2026-11-02, after Hydrolog's wave A (S0, S1, S2, S2b; `888d77d` on
  Hydrolog's `feature/gui`): the registry's interfaces gain an optional
  `gui`, the command that serves a project's browser GUI (HUB-2.1, the
  schema); Hydrolog's is `hydrolog gui serve`, with the route „Open
  Hydrolog's GUI in the browser” and `hydrolog-gui` in its `provides`
  (alone on 127.0.0.1:8070 by default, or `hydrolog.gui:gui_module` of the
  entry point group `nogat.gui`). `AGENTS.md` lists the interface and routes
  the task; the map lists the service. Branch `feature/hydrolog-gui-registry`
  from `feature/handoff-1`, not merged, not pushed.
