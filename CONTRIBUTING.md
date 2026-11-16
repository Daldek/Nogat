# Contributing to Nogat

Thanks for your interest in Nogat! Reports, feedback on the standard, fixes
of the registry and its scripts, and documentation are welcome.

## Getting started

```bash
# Install the locked environment (uv: https://docs.astral.sh/uv/)
uv sync --locked

# Run the gate before opening a pull request: ruff, mypy, tests with coverage,
# the registry, the generated files, shellcheck and actionlint over the CI
# templates, and the commit check (contributors keep their own identity, so
# skip the author check). shellcheck and actionlint must be on PATH.
GATE_CHECK_AUTHOR=0 scripts/gate.sh
```

Nogat is the hub of the ecosystem, not a tool: it holds the standard
(`standards/`), the project registry (`ecosystem.yaml`) and the scripts that
read it (`scripts/`); the `nogat` package does not exist yet. A change of a
rule, of the registry's schema or of work that spans projects starts with a
plan in `docs/plans/` that the maintainer approves: plan → implementation.
Start with:

- [`standards/README.md`](standards/README.md): how rules are written;
- [`standards/DECISIONS.md`](standards/DECISIONS.md): why the rules are what
  they are;
- [`standards/ECOSYSTEM_HUB.md`](standards/ECOSYSTEM_HUB.md): the registry and
  its tooling.

[`CLAUDE.md`](CLAUDE.md) lists the rules of the project for people and agents
who develop it.

## Contribution guidelines

- **Project boundaries.** A pull request changes Nogat only. A need in
  another project of the ecosystem is a GitHub issue labelled `request` in
  that project's repository (DEV-17.5).
- **Generated files.** `docs/ECOSYSTEM_MAP.md` and `AGENTS.md` come from
  `ecosystem.yaml` (`uv run scripts/ecosystem.py map` and `agents`), the
  tables of `standards/ERROR_REGISTRY.md` from `error_registry.json`
  (`uv run scripts/ecosystem.py standard --write`); change the source and
  regenerate, never the output.
- **Requirement IDs.** An ID is never renumbered or reused; a deleted ID is
  listed in the changelog of `standards/README.md`.
- **Language.** Code, identifiers, comments, tests, documentation, commit
  messages and contributor-facing files are in English.
- **Commits.** Use [Conventional Commits](https://www.conventionalcommits.org/)
  in English, for example `docs(standards): clarify DEV-19.5`. Messages carry
  no AI attribution.
- **Branches.** Open pull requests against `develop`; address one concern per
  pull request.

## Contributor License Agreement (CLA)

Every public project of the ecosystem asks contributors to sign a
Contributor License Agreement (DEV-16.2). Nogat's CLA text is not published
yet, so external pull requests cannot be merged until it is. When it is, it
lives in `docs/CLA.md`, the pull-request template carries its checkbox, and a
contributor signs it by ticking the box and adding their line to
[`CONTRIBUTORS.md`](CONTRIBUTORS.md) in the same pull request (DEV-16.5).
Signing does not change the licence: the project and the contribution remain
under the [MIT License](LICENSE).

## Reporting issues

Found a contradiction in the standard, a wrong registry entry or a bug in a
script? Open a GitHub issue with steps to reproduce, expected and actual
behaviour, and the commit of Nogat you used.

Security problems are not reported as public issues: see
[`SECURITY.md`](SECURITY.md).
