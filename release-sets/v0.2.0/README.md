# Release set v0.2.0

The release set of the round of 2026-11-21 (REL-6.6, HUB-7.2): the
candidate [candidate-12](../candidate-12/) with each member's commit
replaced by its release tag. Every tag is annotated and points at the merge
commit of the release on the member's `main`. Against
[v0.1.1](../v0.1.1/README.md) it brings Hydrolog 0.9.0, with the fixes of
the formula audit of 2026-11-18 and its formulas declared by specs with
`formula_versions` (Nogat's computation standard), and its consumers
(plan `docs/plans/2026-11-19-hydrolog-0.9.0-consumers.md`): Obserwator
3.1.0, with the analyses of Hydrolog 0.9.0, an operator's instance and
ČHMÚ's national identifiers, Hydrograf 0.6.0 and Archiwista 0.3.3. Every
GUI carries kit `1.1.0`, the providers are named by their national acronyms
(ECO-082) and the files a tool hands to a person follow one pattern
(ECO-083), by standard 1.1. Kartograf stays at 0.8.2.

| Member | Tag | Commit | Installed by this set |
|---|---|---|---|
| Kartograf | [`v0.8.2`](https://github.com/Daldek/Kartograf/releases/tag/v0.8.2) | `66197871f468869b437e8256e04bd00a0ea7c6aa` | `kartograf[mcp]==0.8.2` |
| Obserwator | [`v3.1.0`](https://github.com/Daldek/Obserwator/releases/tag/v3.1.0) | `0ce9514c5d057ee9be7b03cdda1e44c0dd117990` | `obserwator[full]==3.1.0` |
| Hydrolog | [`v0.9.0`](https://github.com/Daldek/Hydrolog/releases/tag/v0.9.0) | `6520f487bf76907546a49ca5df22b8567cb19ec5` | `hydrolog[all]==0.9.0` |
| Hydrograf | [`v0.6.0`](https://github.com/Daldek/Hydrograf/releases/tag/v0.6.0) | `7b068ad54ec75ac7643b2e4b6a1b386c44d07137` | no: an app on its own lock (ECO-074, ECO-077) |
| Archiwista | [`v0.3.3`](https://github.com/Daldek/Archiwista/releases/tag/v0.3.3) | `c0ed395d71db49680fec4b37fe417a3011343018` | `archiwista[obserwator]==0.3.3` |

`pyproject.toml` and `uv.lock` give the installable members at their tags
and every third-party package at one version for Linux, macOS and Windows:
the same 136 packages and third-party versions as candidate-12's lock.
candidate-12 verified each member at the commit its release branch started
from (Obserwator `e66d473`, Hydrolog `829261a`, Hydrograf `e699b59` and
Archiwista `787a603`; Kartograf at its tag); a tag adds only the release
commit, which sets the version, the CHANGELOG heading and the lock and
replaces the commit pins with these tags, their ranges narrowed to the
releases (REL-2.1, REL-5.6). The `nogat` package (HUB §7) does not exist
yet, so the set is installed as an environment, not with `uv tool install`:

```bash
git clone --branch v0.2.0 https://github.com/Daldek/Nogat
cd Nogat/release-sets/v0.2.0
uv sync --locked --no-dev --python 3.12
```

The members' commands (`kartograf`, `obserwator`, `hydrolog`, `archiwista`)
are then in `.venv/bin/`.

## Verification

candidate-12 passed the workflow verify-candidate on Linux, macOS and Windows
with Python 3.12 and 3.15,
[run 45048681845](https://github.com/Daldek/Nogat/actions/runs/45048681845),
on its first attempt. The members' release commits then passed their full
gates (Obserwator 3,711 tests, Hydrolog 18,344, Hydrograf 2,489 and Archiwista 3,060). This set installs from its lock with
`uv sync --locked --no-dev --python 3.12`, and each member reports its
release version.
