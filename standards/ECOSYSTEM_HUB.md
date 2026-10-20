# Ecosystem hub (Nogat)

Version 2.0 · 2026-10-19 · IDs `HUB-…` · keywords per RFC 2119.

Requirements for Nogat as the hub of the ecosystem (ECO-001, ECO-002).

---

## 1. Role

**HUB-1.1** Nogat holds:
1. this standard (`standards/`);
2. the project registry (`ecosystem.yaml`);
3. tooling that reads the registry (drift report, workspace sync, MCP
   configuration, aggregated agent guide);
4. the collection of scripts and third-party tools for meteorology, hydrology,
   oceanography and hydraulics, including the existing Copernicus Marine
   scripts and R plotting.

**HUB-1.2** Nogat does not contain code of other projects, as submodules,
copies or vendored packages.
*Why:* submodules pin commits and conflict with active development and
history rewrites; the registry references repositories instead.

## 2. Registry `ecosystem.yaml`

**HUB-2.1** One entry per project with at least:

```yaml
schema: nogat-ecosystem/1
standard_version: "2.0"
projects:
  - name: Retman
    summary: Polish natural-language command layer over the ecosystem tools.   # ≤ 100 chars
    profiles: [assistant]
    status: active            # active | research | paused | archived
    repo: https://github.com/Daldek/Retman
    visibility: public        # public | private | local (no remote)
    default_branch: main
    distribution:
      pypi: null              # null until published
      conda_forge: null
      import_name: retman
    version:
      released: null          # latest tag
      development: 0.1.0.dev0 # on develop
    interfaces:
      cli: retman
      mcp: null
      rest: null
      python: retman
      llms_txt: https://raw.githubusercontent.com/Daldek/Retman/main/llms.txt
      agents_md: https://raw.githubusercontent.com/Daldek/Retman/main/AGENTS.md
    data_sources: []
    depends_on:
      - project: Kartograf
        kind: optional        # runtime | optional | dev | data   (data = reads another project's store)
        pin: "8e9bcbb"
        temporary: {reason: "Kartograf 0.8.0 not tagged", until: "Kartograf v0.8.0"}
      - project: IMGWTools
        kind: optional
        pin: "0d98f3b"
        temporary: {reason: "IMGWTools 3.0.0 not tagged", until: "IMGWTools v3.0.0"}
    standard:
      version: "1.0"          # standard version the project currently complies with
      deviations: []          # requirement IDs with ADR links
```

*Why:* every field answers a question an orchestrating agent asked during
the 2026-10-19 survey, such as which versions consumers pin, which repository
is private and where an agent finds the tool's guide.

**HUB-2.2** Third-party tools in the collection have entries with
`owner`, `licence`, `repo`, `summary`, `profiles: [external]` and `used_by`.
*Why:* Nogat's original purpose is collecting tools of other authors; agents
need to know their licence before reuse.

**HUB-2.3** The registry is validated by a JSON Schema in the gate.

**HUB-2.4** No local paths in `ecosystem.yaml`.

## 3. Local workspace

**HUB-3.1** By default, repositories are resolved as siblings of Nogat:
`<parent of Nogat>/<name>`.

**HUB-3.2** A different layout is configured in `ecosystem.local.yaml`
(git-ignored) or with `NOGAT_WORKSPACE`. Per-project overrides are allowed.

**HUB-3.3** `nogat workspace sync` clones missing repositories into the
configured root and reports dirty trees, unpushed commits and branches that
differ from the standard. It never pulls or modifies dirty repositories.
*Why:* users with another directory layout, other machines and CI must work
without editing committed files. Users of the tools need no clones at all,
because they install packages (RELEASE §3).

## 4. Generated outputs

**HUB-4.1** `nogat report drift`: for each consumer, pins behind the producer's
latest release; temporary pins past their `until`; projects behind the
current standard version.

**HUB-4.2** `nogat mcp config --client claude|cursor|codex|vscode` prints a
configuration with every ecosystem MCP server, from registry data.

**HUB-4.3** Nogat `AGENTS.md` aggregates the injected blocks of all tools
(AGI-8.2) and a routing table: task → tool → entry command.
*Why:* an agent working from Nogat should know which tool covers a task
without opening every repository.

**HUB-4.4** Nogat README is generated in part from the registry (project table
with summaries and status).

## 5. Agents operating from Nogat

**HUB-5.1** An agent in Nogat that changes another project follows DEV-3.4:
dedicated branch in the target, target `CLAUDE.md` rules, PROGRESS and
CHANGELOG entries in the target, no merge, push or tag without approval.

**HUB-5.2** Cross-project changes start with a plan in Nogat
(`docs/plans/YYYY-MM-DD-slug.md`) listing the affected projects, order and
pins to update.

**HUB-5.3** Requirements discovered for another project (missing API, bug)
are recorded in Nogat `docs/requests/<project>.md` and copied into the
project's backlog in its next session.
*Why:* DEV-17.5; today such requirements live in consumer documents (for
example Hydrograf plans listing Kartograf requirements A1–A13 and N1–N20)
and are easy to lose.

## 6. Standard versioning

**HUB-6.1** The standard has a version (`2.0`); changes are recorded in
`standards/DECISIONS.md` and in a changelog section of `standards/README.md`.
Projects record which version they comply with in `ecosystem.yaml`.

**HUB-6.2** Error registry and templates are versioned with the standard;
projects pin the version they vendor (ERR-3).
