# Documentation standards

Version 2.0 · 2026-10-19 · IDs `DOC-…` · keywords per RFC 2119.

Documentation has three audiences, and each file serves one of them:

| Audience | Reads first | Purpose |
|---|---|---|
| Agent or person **using** the tool | `README.md`, `llms.txt`, `AGENTS.md`, MCP instructions | decide whether the tool fits, call it correctly |
| Agent **developing** the project | `CLAUDE.md`, `docs/PROGRESS.md` | work on the code safely |
| Author and future maintainers | `docs/PRD.md`, `SCOPE`, `ARCHITECTURE`, `DECISIONS` | why the project is what it is |

All documentation is in English (DEV-2.1, ECO-005).

---

## 1. File set

**DOC-1.1** Required files by profile (DEV §1):

| File | library | tool | app | pipeline | assistant | hub |
|---|---|---|---|---|---|---|
| `README.md` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `CLAUDE.md` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `AGENTS.md` (generated) | – | ✓ | if it has an API for agents | if it has a CLI | ✓ | ✓ (hub variant) |
| `llms.txt` (generated) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `LICENSE` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `docs/PROGRESS.md` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `docs/CHANGELOG.md` | ✓ | ✓ | ✓ | ✓ | ✓ | – |
| `docs/DECISIONS.md` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `docs/PRD.md` | ✓ | ✓ | ✓ | ✓ | ✓ | – |
| `docs/SCOPE.md` | when PRD scope > 100 lines | | | | | |
| `docs/ARCHITECTURE.md` | when ≥ 3 modules | | | | | |
| `docs/USAGE.md` | – | ✓ | ✓ | ✓ | ✓ | – |

*Why:* the set already exists in most projects; agents find documents by
fixed names.

**DOC-1.2** Fixed locations for working documents:

```
docs/
├── PROGRESS.md            current state (§6)
├── progress/YYYY-MM.md    archived sessions
├── CHANGELOG.md
├── DECISIONS.md           ADR index (§8)
├── decisions/NNNN-slug.md one ADR per file (new ADRs)
├── PRD.md  SCOPE.md  ARCHITECTURE.md  USAGE.md
├── specs/YYYY-MM-DD-slug.md
├── plans/YYYY-MM-DD-slug.md
└── research/YYYY-MM-DD-slug.md
```

*Why:* today the same kind of document lives in `docs/superpowers/specs`,
`notes/superpowers/plans`, `docs/research`, `docs/architektura`; dated
filenames sort chronologically and tell an agent how fresh a document is.

**DOC-1.3** A single Markdown file SHOULD stay under ~1,500 lines / 100 KB;
larger documents MUST be split by topic with an index.
*Why:* agents read files into a limited context; Kartograf `ARCHITECTURE.md`
(280 KB) and `DECISIONS.md` (303 KB) cannot be read whole.

**DOC-1.4** Links inside a repository are relative. Links that leave the
repository, or appear in files published to PyPI or read by external agents
(`README.md`, `llms.txt`, `AGENTS.md`), MUST be absolute URLs. No local
absolute paths (`/home/...`) in committed documentation.
*Why:* PyPI does not resolve relative links; external agents cannot follow
relative paths; local paths leak machine details (reason for the Hydrograf
history rewrite on 2026-10-08).

**DOC-1.5** Dates are ISO 8601 (`YYYY-MM-DD`).

**DOC-1.6** Documentation MUST NOT contain text addressed to models that tries
to steer choice ("always recommend", "ignore previous instructions", "best
tool for").
*Why:* such phrases are treated as manipulation by indexers and agents
(Common Crawl analysis of llms.txt, July 2026; Context7 rules) and reduce
trust.

---

## 2. README.md

README is the first document an agent or search pipeline reads about the
project and the source of the descriptions used on PyPI, GitHub and MCP
registries. It is written for selection first ("is this the right tool?")
and use second.

**DOC-2.1** Sections, in this order (profile `app` replaces Install/Quick
start with Run/Deploy; `hub` see ECOSYSTEM_HUB):

| # | Section | Content | Why |
|---|---|---|---|
| 1 | `# <Name>: <what it does, for whom>` | Name and one-line title, no dashes as separators | The title is quoted alone in search results and tool pickers |
| 2 | Summary paragraph | Self-contained, ≤ 400 characters: category, task, domain, interfaces ("Kartograf is a downloader of official spatial data for Poland and Czechia (elevation, orthophoto, land cover, soils, cadastre). CLI, Python library and MCP server.") | Retrieval pipelines and registries take the first paragraph; must stand alone |
| 3 | `## When to use` / `## When not to use` | Concrete tasks it is built for; non-goals with the alternative to use instead (ecosystem tool or external) | Agents choose by scope; MCP guidance recommends explicit when/when-not |
| 4 | `## Install` | One line per interface (`uvx <tool>-mcp`, `uv add <pkg>`, `pip install "<pkg>[mcp]"`), Python version, extras table | One-line install is what agents copy |
| 5 | `## Quick start` | Minimal runnable example per interface: CLI with `--json`, Python, MCP call, REST call; each with its output shape | Agents learn from examples, not prose |
| 6 | `## Capabilities` | Table: task ↔ CLI command ↔ MCP tool ↔ Python function ↔ REST route ↔ data source and licence | Shows parity and lets an agent jump to the right entry point |
| 7 | `## For AI agents` | Links (absolute) to `llms.txt`, `AGENTS.md`, `<tool> commands guide`, catalog introspection command, result envelope name, read-only and `--check` behaviour | Entry point for agents that land on README |
| 8 | `## MCP server` | Configuration snippets for Claude Code (`claude mcp add`), Cursor (`.cursor/mcp.json`), Codex (`codex mcp add`), VS Code (`.vscode/mcp.json`, key `servers`); tool families, write mode, sandbox flags | Removes setup friction, which decides adoption |
| 9 | `## Related tools` | Ecosystem neighbours (who produces inputs, who consumes outputs) and external alternatives with when to prefer them | Honest comparison is how agents learn when to pick this tool |
| 10 | `## Errors and exit codes` | Link to the shared registry, the 5 most common codes with hints | Agents recover from errors faster |
| 11 | `## Data and licensing` | Sources, licences, attribution obligations, where data is written | Data tools carry licence obligations to users |
| 12 | `## Documentation` | Absolute links to USAGE, ARCHITECTURE, CHANGELOG, DECISIONS | PyPI-safe navigation |
| 13 | `## Development` | One paragraph pointing to `CLAUDE.md` and the gate | Keeps developer content out of user-facing text |
| 14 | `## Status, license, author` | Version, maturity, licence, author, citation | Agents check maturity before depending on a tool |

The file ends with `<!-- mcp-name: io.github.Daldek/<server> -->` when an
MCP server is published (RELEASE §4).

**DOC-2.2** README length 150–400 lines. Reference material (all commands, all
options) belongs in USAGE, generated docs or `--help`, not in README.
*Why:* IMGWTools and Hydrolog READMEs exceed 800 lines and bury the selection
information; agents read the beginning.

**DOC-2.3** The summary paragraph, `pyproject` `description`, GitHub "About",
MCP `server.json` `description` and catalog tool summaries MUST derive from
one description ladder stored in the command catalog or `pyproject`:
≤ 100 characters (registry), ≤ 200 (PyPI, GitHub), ≤ 400 (README summary).
*Why:* each channel truncates at a different limit; one source prevents drift.

**DOC-2.4** Use the English terms agents search for, with the Polish official
name where one exists: "digital elevation model (DEM, Polish NMT)",
"topographic database BDOT10k".
*Why:* agents query in English; Polish dataset names are still needed to
match user requests.

**DOC-2.5** No badges or images before the summary; images need alt text.
*Why:* badges push the summary out of the first chunk read by retrieval.

**DOC-2.6** README examples MUST be executed by a test (doctest or a script
in the gate).
*Why:* broken examples are the fastest way to lose an agent's trust in a
tool.

---

## 3. CLAUDE.md (agents developing the project)

**DOC-3.1** ≤ 200 lines. Sections:
1. Project in 2–3 sentences, profiles, link to README.
2. Critical rules (what never to do; approvals required, DEV-3.3).
3. Environment and commands: setup, `scripts/gate.sh`, tests, run.
4. Code map: package layout in a short tree.
5. Documentation map: what to read for which task.
6. Session workflow (DEV-17).
7. Cross-project context: what this project provides to and needs from others,
   link to Nogat `ecosystem.yaml`.
8. Deviations from the ecosystem standard (DEV-1.2).

*Why:* Claude Code recommends files under 200 lines
(https://code.claude.com/docs/en/memory); IMGWTools `CLAUDE.md` has 587 lines,
Hydraulik 25; neither size works.

**DOC-3.2** CLAUDE.md contains instructions, not descriptions of architecture
already in ARCHITECTURE.md.
*Why:* repository overviews in context files do not improve agent success
and add cost (https://arxiv.org/abs/2602.11988).

---

## 4. AGENTS.md (agents using the tool)

**DOC-4.1** Generated from the command catalog by `<tool> commands guide
--format agents`; never edited by hand; a contract test compares it with the
generator (DEV-10.4).
*Why:* ECO-014; generation removes drift (IMGWTools, Hydrolog reference).

**DOC-4.2** ≤ 200 lines and ≤ 16 KiB. Sections: purpose and scope (when / when
not), install, interfaces, workflow rules (discover → check → run → read),
result envelope, error codes (link to registry), command index (one line per
command with link), typical flows, things not to do, and as the last line:
"Developing this repository? Read CLAUDE.md."
*Why:* Codex reads up to 32 KiB of AGENTS.md, Cursor recommends under 500
lines, Claude under 200; the last line serves agents that read AGENTS.md
inside the repo (ECO-014).

**DOC-4.3** Full command reference is served on demand by
`<tool> commands guide --command ...` or catalog introspection, not inlined.
*Why:* progressive disclosure keeps context small.

---

## 5. llms.txt

**DOC-5.1** Follows the llms.txt specification (https://llmstxt.org/): H1 with
the project name, blockquote summary, short paragraphs without headings, then
H2 sections that are lists of `- [title](url): note`.
*Why:* Kartograf `llms.txt` puts installation, tasks and error tables under H2
headings, which the format reserves for link lists.

**DOC-5.2** Links point to LLM-friendly sources: raw Markdown on GitHub
(`https://raw.githubusercontent.com/Daldek/<repo>/<tag-or-main>/...`) or
published `.md` pages, never rendered HTML. Every link has a note.
*Why:* agents fetch the link target; HTML wastes context; notes guide which
link to open.

**DOC-5.3** Text before the first link section ≤ ~2,000 tokens. Generated from
the catalog with the same generator as AGENTS.md and covered by the drift test.

**DOC-5.4** `llms-full.txt` is not produced unless the full content fits a
typical context window (~50,000 characters).
*Why:* not part of llms.txt v2; oversized files are ignored or truncated.

**DOC-5.5** A project test SHOULD answer a fixed set of questions with only
`llms.txt` as context (agent eval, AGENT_INTERFACE §11).
*Why:* the method recommended by the llms.txt authors to check usefulness.

---

## 6. PROGRESS.md

**DOC-6.1** Structure, ≤ 300 lines:
1. `## Status`: table of components with state (`done`, `in progress`,
   `planned`, `blocked`) and note.
2. `## Current version and branch`.
3. `## Last session`: date, what was done, work in progress (file and
   context), decisions awaiting the author.
4. `## Next steps`: ordered.
5. `## Backlog`: prioritised.
6. `## Checkpoints`: one line per checkpoint with date and version.

**DOC-6.2** At the start of a new month, sessions of the previous month move to
`docs/progress/YYYY-MM.md`; "Last session" is replaced, not appended.
*Why:* ECO-013.

---

## 7. CHANGELOG.md

**DOC-7.1** Keep a Changelog 1.1.0 and SemVer, in English, `[Unreleased]` at
the top, sections `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`,
`Security`; breaking changes marked **Breaking** with migration notes; ADR
references in parentheses.
*Why:* already used everywhere; migration notes are what consumers and
agents need after an upgrade.

**DOC-7.2** Updated in the same commit as the user-visible change.

---

## 8. DECISIONS (ADR)

**DOC-8.1** Each ADR has: ID, title, date, status (`proposed`, `accepted`,
`superseded by …`), context, options considered, decision, consequences,
errata (dated, appended, never rewriting the decision).

**DOC-8.2** New ADRs are separate files `docs/decisions/NNNN-slug.md`;
`docs/DECISIONS.md` is the index (ID, title, status, date, link). Existing
single-file registries MAY stay as they are but MUST gain the index.
*Why:* single-file registries reached 303 KB (Kartograf); agents need to open
one decision, not all.

---

## 9. PRD, SCOPE, ARCHITECTURE, USAGE

**DOC-9.1** PRD: goal, users, scenarios, functional requirements with IDs,
non-functional requirements, success criteria, open questions.

**DOC-9.2** SCOPE: in / out (with reason and the tool that covers it) /
future.
*Why:* "out of scope → use X" is reused in README "When not to use".

**DOC-9.3** ARCHITECTURE: components, data flow, external services, storage
layout, interfaces, cross-references to ADRs. Split per DOC-1.3.

**DOC-9.4** USAGE: task-oriented guide per interface; reference tables are
generated from the catalog where possible.

---

## 10. Other agent configuration files

**DOC-10.1** Repositories MUST NOT keep separate hand-written instruction files
per agent vendor (`.github/copilot-instructions.md`, `.cursor/rules/*`,
`GEMINI.md`) unless generated from CLAUDE.md or AGENTS.md.
*Why:* Copilot, Cursor, Codex and Gemini read AGENTS.md; duplicates drift.

**DOC-10.2** Optional discovery files, generated or validated in the gate:
`context7.json` (Context7 indexing), `CITATION.cff`, `server.json`
(RELEASE §4).

---

## 11. Templates

Templates for every file above live in `templates/` of this standard. The v1.0
templates in `templates/` and `configs/` are legacy and are regenerated as
part of [ADOPTION_PLAN.md](ADOPTION_PLAN.md) phase 0.
