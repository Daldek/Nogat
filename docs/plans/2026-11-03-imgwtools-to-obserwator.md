# Plan: IMGWTools becomes Obserwator

Approved: 2026-11-03 (the author: the full change, code included; the frozen
Kartograf and Hydrograf change too; dated records keep the old name). The
name map below was decided by delegated approval.

Requirements: ECO-022, ECO-056, ECO-057, HUB-3.1, HUB-5.2, AGI-4.1, AGI-5.2,
DEV-18.2, DEV-18.3, DEV §19.

## Goal

With v3.0.0 the tool released as IMGWTools 2.1.1 is called Obserwator: the
product, the distribution, the import package, the command and every name
derived from them. The data provider keeps its name: IMGW-PIB is an
institute, not the tool. The GitHub repository is renamed later by the
author; until then its URL and the local directory `IMGWTools` stay.

## Facts

- The only release is v2.1.1 on `main` (distribution `imgwtools` on PyPI,
  no store, no `IMGW_ROOT`). Every document id `imgw-<kind>/1`, the store
  marker and the data directory exist only on `develop`, so they are renamed
  without an alias or a migration (ECO-056). No store written by the tool
  exists outside test directories on this machine (searched 2026-11-03).
- `obserwator` and `nogat-obserwator` are free on PyPI (2026-11-03).
- Couplings outside the producer: Archiwista (imports, `imgwtools.testing`,
  `IMGW_ROOT`, `imgw-store/1`, `imgw-meta/1`, its adapter), Retman (imports,
  `imgw-plan/1`, `imgw-result/1`, `imgw-store/1`, its tool calls), Hydraulik
  (`fetch_pmaxtp`, `imgw pmaxtp fetch`, the exceptions), Hydrograf
  (`fetch_pmaxtp`, the exceptions), Hydrolog (its agent guide names `imgw`
  commands; a fixture `imgwtools_series_export.csv`), Kartograf (the marker
  `imgw-store.json` in `marker.STORE_MARKERS`, DEV-19.11), Nogat (registry,
  standards, error registry, design marks).

## Name map

| Was | Becomes |
|---|---|
| product IMGWTools | Obserwator |
| distribution `imgwtools` | `obserwator`; `nogat-obserwator` at ADOPTION_PLAN 6.1, where the final `imgwtools` release points to it |
| import package `imgwtools` | `obserwator` |
| command `imgw`, `imgw mcp`, `imgw server` | `obserwator`, `obserwator mcp`, `obserwator server` (REST paths `/api/v1` unchanged) |
| MCP tools `imgw_<group>_<verb>` | `obserwator_<group>_<verb>` (the longest stays under 48 characters) |
| variables `IMGW_<KEY>` | `OBSERWATOR_<KEY>`; a key naming an IMGW-PIB endpoint keeps the provider: `IMGW_API_URL` → `OBSERWATOR_IMGW_API_URL` |
| `nogat.toml` `[imgw]`, `<data_dir>/imgw`, `<cache_dir>/imgw` | `[obserwator]`, `<data_dir>/obserwator`, `<cache_dir>/obserwator` |
| document ids `imgw-<kind>/1` | `obserwator-<kind>/1` |
| `imgw-store.json`, `.imgw-incoming/` | `obserwator-store.json`, `.obserwator-incoming/` |
| catalog extensions `x-imgw*` | `x-obserwator*` |
| exceptions `IMGWError` and its subclasses | `ObserwatorError`, `ObserwatorValidationError`, … |
| other identifiers naming the tool (`ImgwGroup`, Archiwista's `imgw_store`, Retman's `imgw_calls`, Nogat's mark `imgwtools.svg`) | the same with `obserwator` / `Obserwator` |

Unchanged: IMGW-PIB and IMGW as the institute; dataset ids `pl.imgw.*`;
provider URLs; identifiers naming the provider (Retman's `imgw_pib`); the
repository URL and the workspace directory until the author's rename; dated
records (released CHANGELOG sections, HISTORY, dated plans, research
reports, decisions describing their time), which may gain "(now
Obserwator)" on first mention at most.

## Steps (producers first, HUB-5.2)

| # | Project | Change | Verified by |
|---|---|---|---|
| 1 | Nogat | ECO-057; the registry entry (name, distribution, interfaces, routes, ids); current standard texts, ADOPTION_PLAN, error registry, design marks and mockups; regenerated `AGENTS.md` and `docs/ECOSYSTEM_MAP.md` | its gate |
| 2 | Obserwator (`IMGWTools` repo) | the name map in code, tests, fixtures and docs; ADR-009; CHANGELOG breaking entry with the map; regenerated `AGENTS.md`, `llms.txt` | its gate, CI matrix |
| 3 | Archiwista, Retman, Hydraulik (`feature/sfincs-swmm`), Hydrolog | pin the step-2 commit; imports, commands, variables, ids, identifiers, docs | each gate, `uv lock --check` |
| 4 | Kartograf, Hydrograf (frozen) | Kartograf: `STORE_MARKERS` names `obserwator-store.json` (an API break of the producer, which its freeze admits) and docs; Hydrograf: docs only, its pin `71bae77` and imports of `imgwtools` stay until after v0.5.0 (its PROGRESS) | each gate |
| 5 | the author | renames the GitHub repository; then the URLs in every repository follow | `drift` |

## Results

Step 1 (Nogat), 2026-11-03, branch `feature/obserwator`: ECO-057; the
registry entry Obserwator (distribution, interfaces, routes, `obserwator-*`
ids and the consumers' edges); HUB-3.1 and `scripts/ecosystem.py` find a
checkout by the last segment of `repo`, so `deps` and `drift` read
`IMGWTools/` for Obserwator, and `drift` matches a requirement by its
`[tool.uv.sources]` URL too (Hydrograf's `imgwtools` pinned in its sources
is still found); standard texts, ADOPTION_PLAN 6.1, the error registry, the
CI template's audit list, the mark `obserwator.svg`, the token
`--tool-obserwator` and the Hydrolog mockup; `AGENTS.md` and
`docs/ECOSYSTEM_MAP.md` regenerated.

Steps 2–4 (2026-11-03/04, all merged and pushed): the producer `IMGWTools`
`develop` `ea158dc` (package, command, variables, ids, marker, MCP names,
exceptions; ADR-009; gate and the CI matrix green); Retman `bad0ac1`,
Archiwista `e479219` (with its feedback), Hydraulik `feature/sfincs-swmm`
`6a74b5a`, Hydrolog `38855a1`, Kartograf `9deaa314` (the marker, admitted
under its freeze), Hydrograf `63bd2c6` (docs) and `f4dca77` (pins and
imports, plan `2026-11-03-one-pin-set.md` D5). Step 5 is the author's.
