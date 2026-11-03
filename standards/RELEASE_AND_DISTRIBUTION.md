# Release and distribution

Part of standard 2.1 · IDs `REL-…`

---

## 1. Versioning

**REL-1.1** Releases are SemVer `X.Y.Z`, which is also a valid PEP 440
version; no pre-releases are published. Between releases `develop` carries
the PEP 440 version `X.Y.Z.devN` of the next release, which the first change
after a release sets. Tags are annotated `vX.Y.Z` on `main`. In `0.y.z` a
minor bump may break; from `1.0.0` only a major bump may break. The version
has one source: `[project] version`, or `__version__` read dynamically.
*Why:* `X.Y.Z` means the same in both schemes; `.devN` is the only spelling
of an unreleased version.

**REL-1.3** Document schemas (`<tool>-<kind>/<n>`) are versioned independently
of the package (AGI-4.1).

## 2. Release procedure

**REL-2.1** A release needs the author's approval for each merge and for the
tag (DEV-3.3), and runs in this order:
1. The code is verified: CI is green on `develop`; for a release that is part
   of a release set, the candidate passed REL §6.
2. A pull request `chore/release-X.Y.Z` into `develop` changes only the
   version (`[project] version` or `__version__`, and `server.json` for an MCP
   server), the CHANGELOG heading and date (`[Unreleased]` becomes
   `[X.Y.Z] - YYYY-MM-DD`; breaking changes already carry migration notes),
   `uv.lock` and, in consumers, the pins of ecosystem producers (commit → tag,
   REL-5.3).
3. A pull request `develop` → `main` is merged (DEV-3.6).
4. The author tags that merge commit with the annotated tag `vX.Y.Z`.
5. CI builds the sdist and wheel, checks them (REL-2.3, AGI-10.1), publishes
   to the channels of REL §3 and creates the GitHub Release from the
   CHANGELOG section.

**REL-2.2** Publishing uses PyPI Trusted Publishing (GitHub Actions OIDC); no
API tokens are stored in repositories.

**REL-2.3** A CI job installs the built wheel in a clean environment and runs
the contract tests against it.
*Why:* catches missing package data and `py.typed` before users do (ECO-011).

**REL-2.4** A hotfix is a branch `hotfix/<topic>` from `main`. Its pull
request into `main` carries the fix, the version and the CHANGELOG entry; the
author tags the merge commit; then a pull request `main` → `develop` brings
the fix back (DEV-3.6).

**REL-2.5** A test MUST NOT locate the repository through the path of the
installed package (`Path(<package>.__file__).parents[…]`), and MUST NOT depend
on the package being an editable install. A test that needs a repository file
(`pyproject.toml`, `CHANGELOG.md`, `server.json`, documents) resolves it from
the test file's location (`Path(__file__).resolve().parents[…]`). Members are
installed as wheels by REL-2.3 and by `verify-candidate` (REL-6.5), and a
wheel holds no repository.
*Why:* ECO-053; on 2026-10-25 four tests of Kartograf and the collection of
Archiwista's suite failed in a wheel and passed in an editable install.

## 3. Channels

| Channel | For | Why |
|---|---|---|
| **PyPI** | every package: `nogat-<project>` and `nogat` | One-line install: `uv tool install nogat-<project>` (CLI), `uv add nogat-<project>` (library), `uvx --from "nogat-<project>[mcp]" <tool>-mcp` (MCP server); prerequisite for the MCP Registry |
| **GitHub Releases** | every project | Release notes and tags that consumers pin (REL §5) |
| **MCP Registry** (`registry.modelcontextprotocol.io`) | every MCP server, after its PyPI upload | Official discovery index; stores metadata that points at the PyPI package |

Later, when a user asks: conda-forge (GDAL stack), container images on GHCR
(apps), Zenodo.

**REL-3.1** Distributions are named `nogat-<project>` (ECO-022), and the user
package is `nogat` (HUB §7). A name is reserved by its first upload.

## 4. MCP Registry entry

**REL-4.1** Each MCP server has `server.json` in the repository root:
- `name` `io.github.Daldek/<tool>`;
- `title` and `description` within the budget of DOC-1.7 (DOC-2.3);
- `version` equal to the package version;
- a `packages` entry with `registryType: "pypi"`, `identifier`
  `nogat-<project>`, `version`, `runtimeHint: "uvx"`,
  `transport: {"type": "stdio"}` and the environment variables it reads.

The schema is
https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json.

**REL-4.2** README ends with `<!-- mcp-name: io.github.Daldek/<tool> -->`;
the registry uses it to verify PyPI ownership.

**REL-4.3** Publishing to the registry runs in the release workflow after the
PyPI upload (`mcp-publisher` with GitHub OIDC).

## 5. Dependencies between ecosystem projects

**REL-5.1** Before a project is on PyPI, consumers pin its release tag:
`nogat-<project> @ git+https://github.com/Daldek/<Project>@vX.Y.Z`.

**REL-5.2** After it is on PyPI, a `tool` depends on a compatible range:
`>=0.9,<0.10` while the producer is `0.y`, `>=1.2,<2` from `1.0`. An `app`
locks exact versions through `uv.lock`.

**REL-5.3** While a producer release is pending, a consumer MAY pin the
producer's commit; it needs the unreleased API to migrate and to pass its own
CI. The consumer's release pull request replaces the commit with the tag
(REL-2.1). Branch pins and editable installs are not committed.
*Why:* ECO-016.

**REL-5.4** The drift report (HUB-4.1; `uv run scripts/ecosystem.py drift`,
`nogat ecosystem drift` once the package exists) reads the pins from the consumers'
manifests and the latest tags from the producers' checkouts and lists the
pins that are behind. Each consumer upgrades in its own session.

**REL-5.6** While a consumer pins a producer by commit (REL-5.3), the range of
producer versions the consumer declares as supported admits the producer's
development versions of the release that is pending: `>=X.Y.0.dev0,<X.(Y+1)`
(`>=0.8.0.dev0,<0.9` for `0.8.0.dev0`; from `1.0` the upper bound is that of
REL-5.2). The consumer's release pull request narrows it to `>=X.Y.0` with
the upper bound of REL-5.2, in the same change that replaces the commit with
the tag (REL-2.1). Every runtime check of the producer's version (a version
gate, a doctor, a manifest, a table of capabilities) uses the declared range
itself, tested with `packaging` `SpecifierSet(range).contains(version,
prereleases=True)`, not a second copy and not a comparison with `X.Y.0`.
*Why:* ECO-053; PEP 440 puts `0.8.0.dev0` below `0.8.0`, so a range that
starts at `0.8.0` refuses the producer's `develop`, which carries the
development version (REL-1.1), and the consumer cannot pass its own CI against
the commit it pins.

## 6. Ecosystem release sets

**REL-6.1** A release set is what one `nogat` release installs: every member
at one release and every third-party package at one exact version, verified
together (REL-6.5). Members are the active projects, other than Nogat, whose
registry entry sets `distribution.import_name`. The published set is the
`nogat` repository at tag `vX.Y.Z`: its `pyproject.toml` and its `uv.lock`,
universal for Linux, macOS and Windows (`[tool.uv] environments`). It is not
copied elsewhere, and the registry does not record it.
*Why:* ECO-025, ECO-037.

**REL-6.2** Each third-party package has one version across the set,
development tools (ruff, mypy, pytest, pytest-cov) included. Each member
applies the set through `[tool.uv] constraint-dependencies`, exported from the
set's `uv.lock` and limited to the packages in the member's own lock. Declared
ranges stay ranges (REL-5.2) and contain the set's version.

**REL-6.4** A candidate is a set that is not yet released:
`release-sets/candidate-<N>/` in Nogat holds its `pyproject.toml` and
`uv.lock` (as in REL-6.1) and a README with the commit of each member.
Members' development heads may be pinned by commit (REL-5.3).
*Why:* nothing is released without a green run (ECO-025).

**REL-6.5** A candidate is verified by the Nogat workflow `verify-candidate`
(`workflow_dispatch`, defined on `main`). On the CI runners and Python
versions of REL-7.1 it installs the candidate's lock and runs, from each
member checked out at its recorded commit, the offline test suite and the
contract tests, which use the producers' public `<package>.testing` modules
(`kartograf.testing`, `imgwtools.testing`; the registry lists each in the
producer's `exchange` as `<tool>-testing`; DEV-10.6). The members are
installed as wheels (REL-2.5). The run URL, recorded in the candidate's
README, is the verification record. The author MAY also run on their own
machines what CI cannot, such as network shares. A failure is fixed in the
member and produces a new candidate.
*Why:* ECO-037, ECO-053.

**REL-6.6** After verification each member is released by REL-2.1; its
release pull request changes only what REL-2.1 lists, and any other change
needs a new candidate. Members are released producers first, in the
dependency order of the registry (`depends_on`, planned edges included).
`nogat` is released last by the same procedure; its release pull request puts
the candidate's set in place (`pyproject.toml` and `uv.lock`) with each
member's commit replaced by its tag (HUB-7.2). A security fix between sets is
a patch release of the member and of `nogat`, verified by the same workflow.

## 7. Support

**REL-7.1** Supported: the latest release set (the latest `nogat` release)
and the latest release of each member, on Linux x86_64, macOS arm64 and
Windows x86_64 (the CI runners), Python 3.12 or newer as verified.
`requires-python` is `>=3.12`; a set is verified on 3.12 and on the newest
stable Python that CI runs, and the supported Pythons are those the latest set
verified. Nothing else is promised; fixes go forward.
*Why:* ECO-035; one maintainer can support one line.
