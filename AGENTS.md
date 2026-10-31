# Nogat - guide for agents

> Generated from `ecosystem.yaml`: `uv run scripts/ecosystem.py agents`. Do not edit it by hand.

## Purpose and scope

Nogat is the hub of an ecosystem of tools for hydrology, meteorology and geodata in Poland and Czechia: Kartograf, IMGWTools, Hydrolog, Hydrograf, Hydraulik, Retman and Archiwista. It holds the shared standard, the project registry and the map of what feeds what. It downloads and computes nothing itself.

Use it to find the tool for a task and the command to start with, then read that tool's guide, linked in the table; and to plan a change that spans projects: a plan in `docs/plans/` comes first, producers before consumers.

Not for running a task: call the tool. Its guide gives its options, flows and error codes.

## Routing table

One row per task. A tool that is not `active` is marked in its row; an app has no AGENTS.md, so its link is its README.

| Task | Tool | Entry command |
|---|---|---|
| Download elevation models (NMT, NMPT), LAZ point clouds or contours of an area | [Kartograf][kartograf] | `kartograf elevation download` |
| Download orthophotos of an area | [Kartograf][kartograf] | `kartograf imagery download` |
| Download land cover of an area (BDOT10k, CORINE and others) | [Kartograf][kartograf] | `kartograf landcover download` |
| Download a SoilGrids soil layer of an area | [Kartograf][kartograf] | `kartograf soil download` |
| Classify hydrologic soil groups (HSG) of an area from SoilGrids texture it downloads itself | [Kartograf][kartograf] | `kartograf soil hsg` |
| Download boundaries, cadastre, 3D models, names, maps or geodetic data (find the group first) | [Kartograf][kartograf] | `kartograf commands list` |
| Read what a Kartograf store already holds | [Kartograf][kartograf] | `kartograf store overview` |
| Find IMGW-PIB or ČHMÚ stations by name, river or code | [IMGWTools][imgwtools] | `imgw stations find` |
| Download archive data of stations into a versioned store | [IMGWTools][imgwtools] | `imgw store sync` |
| Download archive files as published, as plain files | [IMGWTools][imgwtools] | `imgw datasets download` |
| Read the series of a station from the store | [IMGWTools][imgwtools] | `imgw series read` |
| Export the series of a station as CSV with the provider's attribution | [IMGWTools][imgwtools] | `imgw series export` |
| Fetch current hydrological data of IMGW-PIB stations (live, not stored) | [IMGWTools][imgwtools] | `imgw current hydro` |
| Get PMAXTP design precipitation of a point in Poland | [IMGWTools][imgwtools] | `imgw pmaxtp fetch` |
| Compute the time of concentration of a watershed | [Hydrolog][hydrolog] | `hydrolog tc watershed` |
| Compute effective precipitation of a rain by SCS-CN | [Hydrolog][hydrolog] | `hydrolog scs effective` |
| Build a design hyetograph (block, triangular, Beta, Euler II) | [Hydrolog][hydrolog] | `hydrolog precip hietogram` |
| Compute the design direct-runoff hydrograph of a watershed | [Hydrolog][hydrolog] | `hydrolog hydrograph generate` |
| Route a hydrograph through a reach, a reservoir or a river network | [Hydrolog][hydrolog] | `hydrolog route network` |
| Compute morphometry indicators of a watershed | [Hydrolog][hydrolog] | `hydrolog morphometry watershed` |
| Compute flood quantiles from annual maxima, for example of an IMGWTools export | [Hydrolog][hydrolog] | `hydrolog stats flood-frequency` |
| Classify hydrologic soil groups (HSG) from clay, sand and silt rasters you already have | [Hydrolog][hydrolog] | `hydrolog soil hsg` |
| Delineate the watershed of a point in Poland and read its parameters | [Hydrograf][hydrograf] | `POST /api/delineate-watershed` |
| Generate a design hydrograph for a point in Poland from PMAXTP rainfall | [Hydrograf][hydrograf] | `POST /api/generate-hydrograph` |
| Cut a terrain profile along a line | [Hydrograf][hydrograf] | `POST /api/terrain-profile` |
| Check which engines (SFINCS, SWMM) this machine can run | [Hydraulik][hydraulik] (research) | `hydraulik engines check` |
| Fetch terrain, land cover and soil groups of a model area through Kartograf | [Hydraulik][hydraulik] (research) | `hydraulik terrain download` |
| Write a design rain table from a Hydrolog shape and a PMAXTP depth | [Hydraulik][hydraulik] (research) | `hydraulik rainfall build` |
| Build a SFINCS flood model directory from terrain and rain | [Hydraulik][hydraulik] (research) | `hydraulik model build` |
| Run a SFINCS flood model and read its maxima and water balance | [Hydraulik][hydraulik] (research) | `hydraulik model run` |
| Couple a SFINCS model with an EPA SWMM sewer network | [Hydraulik][hydraulik] (research) | `hydraulik model couple` |
| Run a SWMM sewer network alone with an inflow hydrograph | [Hydraulik][hydraulik] (research) | `hydraulik swmm run` |
| Plan a data download or export written in Polish, then run it once confirmed | [Retman][retman] | `retman plan run` |
| Browse a Kartograf store on a map in the browser | [Archiwista][archiwista] | `archiwista serve` |
| Search the file catalog of a Kartograf store from a script | [Archiwista][archiwista] | `archiwista search` |
| Export the input data of a project's set (one year, one purpose) as flat category folders or a ZIP | [Archiwista][archiwista] | `archiwista project-export` |

[kartograf]: https://raw.githubusercontent.com/Daldek/Kartograf/main/AGENTS.md
[imgwtools]: https://raw.githubusercontent.com/Daldek/IMGWTools/main/AGENTS.md
[hydrolog]: https://raw.githubusercontent.com/Daldek/Hydrolog/main/AGENTS.md
[hydrograf]: https://raw.githubusercontent.com/Daldek/Hydrograf/main/README.md
[hydraulik]: https://raw.githubusercontent.com/Daldek/Hydraulik/main/AGENTS.md
[retman]: https://raw.githubusercontent.com/Daldek/Retman/main/AGENTS.md
[archiwista]: https://raw.githubusercontent.com/Daldek/Archiwista/main/README.md

## Tools

| Tool | Status | Interfaces | What it is |
|---|---|---|---|
| Kartograf | active | CLI `kartograf`, MCP `kartograf-mcp`, Python `kartograf` | Downloads Polish and Czech geodata (DEM, imagery, land cover, soil) as plain files or a store. |
| IMGWTools | active | CLI `imgw`, MCP `imgw mcp`, REST `imgw server (/api/v1)`, Python `imgwtools` | IMGW-PIB and ČHMÚ hydro-meteo data, PMAXTP; plain files or a versioned store with Parquet series. |
| Hydrolog | active | CLI `hydrolog`, MCP `hydrolog mcp`, Python `hydrolog` | Hydrological calculations (tc, SCS-CN, hydrographs, routing, statistics, HSG); library, CLI, MCP. |
| Hydrograf | active | REST `/api` | Web app (FastAPI + PostGIS) for watershed delineation and design hydrographs. |
| Hydraulik | research | CLI `hydraulik`, Python `hydraulik` | Builds and runs SFINCS flood models from terrain and design rain; optional EPA SWMM sewer coupling. |
| Retman | active | CLI `retman`, Python `retman` | Polish natural-language command layer over the ecosystem tools. |
| Archiwista | active | CLI `archiwista`, REST `/api/v1` | Web browser and manager of Kartograf and IMGWTools stores. |

## Calling a tool

Every tool (profile `tool`) is called the same way:

1. **Discover, do not guess:** `<tool> commands list` lists the commands; `<tool> commands schema --command "<group> <verb>"` gives the options of one, with values and examples.
2. **Check, then run:** a command that writes has `--check`, which plans without effects; run the plan first.
3. **Read the result:** `status` of the envelope is `ok`, `partial` or `failed` (exit 0, 10, 11); `partial` and `failed` are results, not errors: read `items` and retry only the failed units.
4. **Decide by code:** an error is a document on the last line of stderr; its `code` and exit code come from the shared error registry (below).
5. **Know where data goes:** `--output-dir` (`-o`) writes plain files and `--output` one file; `--root` writes the versioned store of Kartograf and IMGWTools (default `<data_dir>/<tool>`); `--force` replaces existing files and nothing else is overwritten; an `--output-dir` inside a store is refused with `conflict`.

## More

- [Ecosystem map](https://raw.githubusercontent.com/Daldek/Nogat/main/docs/ECOSYSTEM_MAP.md): data flow, what each project provides and who consumes it
- [Registry](https://raw.githubusercontent.com/Daldek/Nogat/main/ecosystem.yaml): the projects, their interfaces, routes and exchanged data
- [Error registry](https://raw.githubusercontent.com/Daldek/Nogat/main/standards/ERROR_REGISTRY.md): the codes and exit codes of every tool
- [Agent interface standard](https://raw.githubusercontent.com/Daldek/Nogat/main/standards/AGENT_INTERFACE.md): the catalog, CLI, result and error documents every tool follows

Developing this repository? Read CLAUDE.md.
