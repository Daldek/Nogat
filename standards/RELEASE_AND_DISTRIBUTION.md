# Release and distribution

Version 2.0 · 2026-10-19 · IDs `REL-…` · keywords per RFC 2119.

---

## 1. Versioning

**REL-1.1** Semantic Versioning 2.0.0. In `0.y.z`, a minor bump may break;
from `1.0.0`, only a major bump may break.

**REL-1.2** The package version has one source (`[project] version` or
`__version__` read dynamically); development builds report
`X.Y.Z.devN+g<sha>`.
*Why:* agents report which build they used; Kartograf already derives the
version this way.

**REL-1.3** Document schemas (`<prefix>-<kind>/<n>`) are versioned
independently of the package (AGI-4.1).

## 2. Release procedure

**REL-2.1** A release requires the author's approval (DEV-3.3) and passes, in
order:
1. Gate green on `develop`.
2. CHANGELOG `[Unreleased]` renamed to `[X.Y.Z] - YYYY-MM-DD` with
   migration notes for breaking changes.
3. Version bumped.
4. Merge `develop` → `main`.
5. Annotated tag `vX.Y.Z`.
6. CI builds sdist and wheel, runs the release items of the agent-readiness
   checklist (AGI §11), publishes to the channels of §3.
7. GitHub Release created with the CHANGELOG section.
8. `ecosystem.yaml` in Nogat updated (version, consumers to upgrade).

**REL-2.2** Publishing uses PyPI Trusted Publishing (GitHub Actions OIDC); no
API tokens stored in repositories.

**REL-2.3** Wheels MUST contain all package data and `py.typed`; a CI job
installs the built wheel in a clean environment and runs the contract tests
against it.
*Why:* catches missing package data before users do (ECO-011).

## 3. Channels

Ordered by priority. "Profiles" refers to DEVELOPMENT §1.

| # | Channel | For | Status | Why |
|---|---|---|---|---|
| 1 | **PyPI** | every distributable package | required | One-line install (`uv add`, `pip`, `uvx`); prerequisite for the MCP Registry and conda-forge recipes |
| 2 | **GitHub Releases** | every project | required | Release notes and tags already used by consumers |
| 3 | **MCP Registry** (`registry.modelcontextprotocol.io`) | every MCP server | required after PyPI | Official discovery index used by MCP clients; stores metadata pointing at the PyPI package |
| 4 | **conda-forge** | Kartograf, Hydraulik, Hydrolog, IMGWTools | planned after PyPI | Solves GDAL/PROJ/rasterio binaries on Windows and in scientific environments; `noarch: python` recipes generated with grayskull |
| 5 | **Container images on GHCR** | Hydrograf, Archiwista, IMGWTools API, Hydraulik compute node, MCP servers with native stacks | planned | Reproducible deployment; MCP clients can start servers with `docker run` when native libraries are hard to install |
| 6 | **Claude Code plugin marketplace** (one marketplace in Nogat, one plugin per tool: MCP config + skills) | tools | optional | Installs MCP server and usage skills in one step for Claude Code users |
| 7 | **Zenodo DOI** via GitHub integration, with `CITATION.cff` | Hydrolog, Kartograf, IMGWTools, Hydraulik | optional | Hydrology users are researchers who need citable versions |
| 8 | **QGIS Plugin Repository** | Kartograf QGIS plugin (Kartograf roadmap) | when the plugin exists | Where GIS users look for data downloaders |
| 9 | **Context7 and DeepWiki indexing** | public repositories | optional | Documentation sources used by coding agents |

Not planned: Homebrew, apt, winget (`uvx` covers command-line installs),
Docker Hub (GHCR suffices), MCPB bundles (the Anthropic directory no longer
accepts local bundles; plugins replace them,
https://claude.com/docs/connectors/building/submission).

**REL-3.1** Distribution names must be reserved on PyPI before the first
release. On 2026-10-19:
- `hydrolog`, `hydrograf`, `hydraulik`, `retman`, `archiwista` and `nogat`
  are free.
- `imgwtools` belongs to this ecosystem.
- `kartograf` belongs to an unrelated project on PyPI and conda-forge.

All distributed packages share one name pattern (ECO-022, preferred
`nogat-<name>`, to be confirmed before the first release).

## 4. MCP Registry entry

**REL-4.1** Each MCP server has `server.json` in the repository root:
- `name` `io.github.Daldek/<server>`;
- `title` and `description` of at most 100 characters (from the description
  ladder, DOC-2.3);
- `version` equal to the package version;
- a `packages` entry with `registryType: "pypi"`, `identifier`, `version`,
  `runtimeHint: "uvx"`, `transport: {"type": "stdio"}` and the environment
  variables it reads.

The schema is
https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json.

**REL-4.2** README ends with `<!-- mcp-name: io.github.Daldek/<server> -->`;
the registry uses it to verify PyPI ownership.

**REL-4.3** Publishing to the registry runs in the release workflow
(`mcp-publisher` with GitHub OIDC).

## 5. Dependencies between ecosystem projects

**REL-5.1** Before a project is on PyPI, consumers pin a release tag:
`kartograf @ git+https://github.com/Daldek/Kartograf@v0.9.0`.

**REL-5.2** After it is on PyPI:
- Libraries and tools depend on a compatible range: `>=0.9,<0.10` while the
  producer is `0.y`, `>=1.2,<2` from `1.0`.
- Applications lock exact versions through `uv.lock`.

**REL-5.3** Commit-SHA pins, branch pins and editable sibling installs are
allowed only temporarily, while a producer release is pending. Each one is
recorded in `ecosystem.yaml` with reason and the release that removes it.
*Why:* ECO-016; Retman (SHA) and Archiwista (editable branch) depend on
unreleased Kartograf 0.8.0 today.

**REL-5.4** When a producer releases, Nogat reports the consumers whose pins
are behind, and each consumer upgrades in its own session.

**REL-5.5** A producer MUST NOT change its public API for one consumer without
an entry in its own backlog or ADR (DEV-17.5).
