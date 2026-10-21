# Documentation standards

Part of standard 2.1 · IDs `DOC-…`

Documentation has three audiences, and each file serves one of them:

| Audience | Reads first | Purpose |
|---|---|---|
| Agent or person **using** the tool | `README.md`, `llms.txt`, `AGENTS.md`, MCP instructions | decide whether the tool fits, call it correctly |
| Agent **developing** the project | `CLAUDE.md`, `docs/PROGRESS.md` | work on the code safely |
| Author and future maintainers | `docs/PRD.md`, `ARCHITECTURE`, `DECISIONS` | why the project is what it is |

---

## 1. File set

**DOC-1.1** Every project has these files, by profile (DEV §1); a project with
several profiles has the union:

| File | `tool` | `app` | `hub` |
|---|---|---|---|
| `README.md` | ✓ | ✓ | ✓ |
| `CLAUDE.md` | ✓ | ✓ | ✓ |
| `LICENSE` | ✓ | ✓ | ✓ |
| `docs/PROGRESS.md` | ✓ | ✓ | ✓ |
| `docs/CHANGELOG.md` (or `CHANGELOG.md`: the one place the project already uses) | ✓ | ✓ | ✓ |
| `AGENTS.md`, generated | ✓ (with a CLI) | – | ✓ (routing table, HUB-4.3) |
| `llms.txt`, generated | ✓ | – | – |

Public repositories add the contribution files of DEV §16 and `SECURITY.md`
(DEV-13.7). `docs/DECISIONS.md` is required once the first ADR exists (in the
hub: `standards/DECISIONS.md`). `docs/PRD.md`, `docs/ARCHITECTURE.md` and
`docs/USAGE.md` are optional.
*Why:* agents find documents by fixed names; a file nobody needs is not
required.

**DOC-1.2** Working documents have fixed locations:

```
docs/
├── PROGRESS.md              current state (DOC §6)
├── CHANGELOG.md             (DOC §7; or in the root, DOC-1.1)
├── DECISIONS.md             ADR index (DOC §8)
├── decisions/NNNN-slug.md   one ADR per file
├── PRD.md  ARCHITECTURE.md  USAGE.md
└── plans/YYYY-MM-DD-slug.md goal, options, decision, steps, results (DEV-17.4)
```

Nogat also has `docs/user/` (DOC §12) and, in the repository root,
`release-sets/` (REL §6).
*Why:* fixed names and dated filenames let an agent find a document and judge
its age.

**DOC-1.4** Links inside a repository are relative. Links that leave the
repository, or appear in files published to PyPI or read by external agents
(`README.md`, `llms.txt`, `AGENTS.md`), MUST be absolute URLs. No local
absolute paths (`/home/...`) in committed documentation.
*Why:* PyPI and external agents do not resolve relative links; local paths
leak machine details.

**DOC-1.5** Dates are ISO 8601 (`YYYY-MM-DD`).

**DOC-1.6** Documentation, and the descriptions and instructions served to
agents (catalog, MCP, OpenAPI), MUST NOT contain text addressed to models that
tries to steer choice ("always recommend", "ignore previous instructions",
"best tool for").
*Why:* indexers and agents treat such phrases as manipulation (ECO-017).

**DOC-1.7** Size budgets. Limits are stated only here; other rules refer to
this table. Where a tool generates the file, the gate checks the budget in a
contract test (DEV-10.4); other budgets are limits for review.

| Text | Budget | Enforced by |
|---|---|---|
| `CLAUDE.md` | 200 lines | review |
| `docs/PROGRESS.md` | 300 lines | review |
| `README.md` | 400 lines | review |
| `AGENTS.md` | 200 lines and 16 KiB | contract test |
| `llms.txt` before its first link list | 8,000 characters (about 2,000 tokens) | contract test |
| `agents-md-block` output | 60 lines | contract test |
| Description ladder: README summary paragraph | 400 characters | review |
| Description ladder: `pyproject` `description` | 200 characters | review |
| Description ladder: `server.json` `description`, catalog tool summary, command `summary` | 100 characters | review; contract test for generated copies |
| MCP tool description (`summary`, `description`, `rules`) | 600 characters | MCP test (AGI-5.13) |
| MCP server instructions | 4,096 characters | MCP test (AGI-5.13) |
| CLI and MCP result | 20,000 characters per default page, 50,000 at most | contract test; MCP test (AGI-5.13) |

*Why:* agents load these texts at session start, or clients truncate them;
every limit has one home.

---

## 2. README.md

README is the first document an agent or search pipeline reads about the
project; its summary paragraph is the longest form of the description that
PyPI and MCP registries show (DOC-2.3).
It is written for selection first ("is this the right tool?") and use second.

**DOC-2.1** Sections, in this order. A section for an interface the project
lacks is omitted; profile `app` replaces Install and Quick start with Run and
Deploy; the hub's Install is HUB-7.1.

| # | Section | Content |
|---|---|---|
| 1 | `# <Name>: <what it does, for whom>` | Name and one-line title, no dashes as separators |
| 2 | Summary paragraph | Self-contained: category, task, domain, interfaces ("`<Name>` is a downloader of official spatial data for Poland and Czechia (elevation, orthophoto, land cover, soils, cadastre). CLI, Python library and MCP server.") |
| 3 | `## When to use` / `## When not to use` | Concrete tasks it is built for; non-goals, each with the tool to use instead (ecosystem tool or external) |
| 4 | `## Install` | One line per interface: `uv tool install nogat-<project>` (CLI), `uv add nogat-<project>` (library), `uvx --from "nogat-<project>[mcp]" <tool>-mcp` (MCP server); Python version; extras table |
| 5 | `## Quick start` | Minimal runnable example per interface (CLI with `--json`, Python, MCP call, REST call), each with its output shape |
| 6 | `## Capabilities` | Table: task ↔ CLI command ↔ MCP tool ↔ Python function ↔ REST route ↔ data source and licence |
| 7 | `## For AI agents` | Absolute links to `llms.txt` and `AGENTS.md`; `<tool> commands guide`; the catalog introspection command; the result envelope name; read-only and `--check` behaviour |
| 8 | `## MCP server` | Configuration snippets for Claude Code (`claude mcp add`), Cursor (`.cursor/mcp.json`), Codex (`codex mcp add`) and VS Code (`.vscode/mcp.json`, key `servers`), each starting the server as in row 4; tool families, write mode, sandbox flags |
| 9 | `## Related tools` | Ecosystem neighbours (who produces inputs, who consumes outputs) and external alternatives with when to prefer them |
| 10 | `## Errors and exit codes` | Link to the shared registry and the five most common codes with hints |
| 11 | `## Data and licensing` | Sources, licences, attribution obligations, where data is written |
| 12 | `## Documentation` | Absolute links to CHANGELOG and to USAGE, ARCHITECTURE and DECISIONS where they exist |
| 13 | `## Development` | One paragraph pointing to `CLAUDE.md` and the gate |
| 14 | `## Status, licence, author` | Maturity, licence, author |

The file ends with `<!-- mcp-name: io.github.Daldek/<tool> -->` when an MCP
server is published (REL-4.2).
*Why:* an agent chooses by title, summary and when/when-not, then copies the
install line; ready MCP snippets remove the setup friction that decides
adoption.

**DOC-2.2** README stays within its budget (DOC-1.7). Reference material (all
commands, all options) belongs in USAGE, generated docs or `--help`.
*Why:* agents read the beginning, so selection information buried below it is
lost.

**DOC-2.3** The README summary, `pyproject` `description`, `server.json`
`description` and the catalog tool summary MUST derive from one description at
the three ladder lengths of DOC-1.7; `pyproject` `description` is the master
text.
*Why:* each channel truncates at a different limit; one source prevents drift.

**DOC-2.4** Use the English terms agents search for, with the Polish official
name where one exists: "digital elevation model (DEM, Polish NMT)",
"topographic database BDOT10k".
*Why:* agents query in English; Polish dataset names are still needed to
match user requests.

**DOC-2.5** No badges or images before the summary; images need alt text.
*Why:* badges push the summary out of the first chunk read by retrieval.

**DOC-2.6** README examples are executed by a test: offline examples in the
gate (doctest or a script), examples that need the network in the `live`
suite (DEV §10).
*Why:* broken examples are the fastest way to lose an agent's trust in a
tool.

---

## 3. CLAUDE.md (agents developing the project)

**DOC-3.1** CLAUDE.md stays within its budget (DOC-1.7). Sections:
1. Project in 2–3 sentences, profiles, link to README.
2. Critical rules (what never to do; approvals required, DEV-3.3).
3. Environment and commands: setup, `scripts/gate.sh`, tests, run.
4. Code map: package layout in a short tree.
5. Documentation map: what to read for which task.
6. Session workflow (DEV §17).
7. Cross-project context: link to the project's entry in Nogat `ecosystem.yaml`.
8. `## Deviations` from this standard: one line each with the requirement ID
   and a link to the ADR if there is one; deviations are recorded nowhere
   else (DEV-1.2).

*Why:* Claude Code recommends files under 200 lines
(https://code.claude.com/docs/en/memory).

**DOC-3.2** CLAUDE.md contains instructions, not descriptions of architecture
already in ARCHITECTURE.md.
*Why:* repository overviews in context files do not improve agent success
and add cost (https://arxiv.org/abs/2602.11988).

---

## 4. AGENTS.md (agents using the tool)

**DOC-4.1** AGENTS.md is generated from the command catalog by
`<tool> commands guide --format agents` (the hub's by aggregation, HUB-4.3);
never edited by hand; a contract test compares it with the generator output
(DEV-10.4).
*Why:* ECO-014.

**DOC-4.2** AGENTS.md stays within its budget (DOC-1.7). Sections: purpose and
scope (when / when not), install, interfaces, workflow rules (discover →
check → run → read), result envelope, error codes (link to registry), command
index (one line per command with link), typical flows, things not to do; the
last line is "Developing this repository? Read CLAUDE.md."
*Why:* the last line serves agents that read AGENTS.md inside the repository
(ECO-014); Codex reads at most 32 KiB.

**DOC-4.3** The full command reference is served on demand by
`<tool> commands schema` (AGI-2.4), not inlined.
*Why:* progressive disclosure keeps context small.

---

## 5. llms.txt

**DOC-5.1** `llms.txt` follows the llms.txt specification
(https://llmstxt.org/): H1 with the project name, blockquote summary, short
paragraphs without headings, then H2 sections that contain only link lists,
each item a Markdown link followed by a colon and a note.
*Why:* the format reserves H2 headings for link lists.

**DOC-5.2** Links point to LLM-friendly sources: raw Markdown on GitHub
(`https://raw.githubusercontent.com/Daldek/<repo>/<tag-or-main>/...`) or
published `.md` pages, never rendered HTML. Every link has a note.
*Why:* agents fetch the link target; HTML wastes context; notes guide which
link to open.

**DOC-5.3** The text before the first link list stays within its budget
(DOC-1.7). `llms.txt` is generated with AGENTS.md from the catalog (AGI §8)
and covered by the same contract test (DOC-4.1).

**DOC-5.4** `llms-full.txt` is not produced.
*Why:* it is not part of the llms.txt specification, and clients ignore or
truncate oversized files.

---

## 6. PROGRESS.md

**DOC-6.1** `docs/PROGRESS.md` has three sections and stays within its budget
(DOC-1.7):
1. `## Status`: table of components with state (`done`, `in progress`,
   `planned`, `blocked`) and a note.
2. `## Next`: one ordered list; unfinished work comes first, with file and
   context.
3. `## Open questions`: decisions awaiting the author, removed when decided.

History is the git log and the CHANGELOG, not PROGRESS.
*Why:* ECO-039; agents read PROGRESS at every session start, so its size is
paid every time.

---

## 7. CHANGELOG.md

**DOC-7.1** Keep a Changelog 1.1.0 and SemVer, in English, `[Unreleased]` at
the top, sections `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`,
`Security`; breaking changes marked **Breaking** with migration notes; ADR
references in parentheses.
*Why:* migration notes are what consumers and agents need after an upgrade.

**DOC-7.2** The CHANGELOG is updated in the same commit as the user-visible
change.

---

## 8. DECISIONS (ADR)

**DOC-8.1** Each ADR has: ID, title, date, status (`proposed`, `accepted`,
`amended by …`, `superseded by …`), context, options considered, decision,
consequences, errata (dated, appended, never rewriting the decision). An
amendment is noted at the top of the amended ADR with its date and the
amending ADR.

**DOC-8.2** New ADRs are separate files `docs/decisions/NNNN-slug.md`;
`docs/DECISIONS.md` is the index (ID, title, status, date, link). A
single-file log already in place MAY stay, headed by the same index.
*Why:* an agent opens one decision, not all.

---

## 9. PRD, ARCHITECTURE, USAGE

**DOC-9.1** PRD: goal, users, scenarios, functional requirements with IDs,
non-functional requirements, scope (in; out, each with the reason and the tool
that covers it; later), success criteria.
*Why:* "out of scope → use X" is reused in README "When not to use".

**DOC-9.3** ARCHITECTURE: components, data flow, external services, storage
layout, interfaces, cross-references to ADRs.

**DOC-9.4** USAGE: task-oriented guide per interface; reference tables come
from the catalog or `--help`, not typed by hand.

---

## 10. Other agent configuration files

**DOC-10.1** Repositories MUST NOT keep separate hand-written instruction files
per agent vendor (`.github/copilot-instructions.md`, `.cursor/rules/*`,
`GEMINI.md`) unless generated from CLAUDE.md or AGENTS.md.
*Why:* Copilot, Cursor, Codex and Gemini read AGENTS.md; duplicates drift.

**DOC-10.2** An MCP server has `server.json` in the repository root (REL-4.1).

---

## 11. Templates

**DOC-11.1** The templates of this standard are the files in
[`ci/`](ci/README.md): quality gate, CI and Dependabot. The v1 files in
`templates/` and `configs/` are not valid for this standard and are not
copied until they are replaced.
*Why:* the v1 files contradict rules of this standard.

---

## 12. Ecosystem user documentation (Nogat)

**DOC-12.1** Nogat holds the user documentation of the ecosystem as a whole
in `docs/user/`, in English (ECO-005):
- `getting-started.md`: install (HUB-7.1), `nogat init`, `nogat doctor`,
  first task with each tool;
- `configuration.md`: `nogat.toml`, shared and per-tool keys, environment
  variables, precedence (DEV-18.1), credentials (DEV-18.4), backups
  (DEV-18.5);
- `recipes/`: cross-tool tasks, one file each (for example area → DEM →
  design rainfall → hydrograph), naming the tools, commands and the files
  passed between them;
- `agents.md`: working with the tools through MCP and Retman.

Tool-specific detail stays in each tool's README and USAGE; Nogat links to
it.
*Why:* each tool documents only itself; a user of the `nogat` package needs
an entry point and the tasks that span tools.

**DOC-12.2** Once the `nogat` package exists, every recipe has an executable
form (`docs/user/recipes/*.sh` or a Python script next to it). Steps that
work offline run in Nogat's gate against the members' testing modules
(DEV-10.6); steps that need the network run in Nogat's weekly live workflow.
*Why:* recipes break silently when tools change; DOC-2.6 applies the same
rule to README examples.
