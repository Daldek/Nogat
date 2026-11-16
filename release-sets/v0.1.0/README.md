# Release set v0.1.0

The first release set of the ecosystem (REL-6.6, HUB-7.2, ECO-076): the
candidate [candidate-6](../candidate-6/) with each member's commit replaced
by its release tag. Every tag is annotated and points at the merge commit of
the release on the member's `main`.

| Member | Tag | Commit | Installed by this set |
|---|---|---|---|
| Kartograf | [`v0.8.0`](https://github.com/Daldek/Kartograf/releases/tag/v0.8.0) | `333ef5cfff789ee679392bbd0578400f36b23380` | `kartograf[mcp]==0.8.0` |
| Obserwator | [`v3.0.0`](https://github.com/Daldek/Obserwator/releases/tag/v3.0.0) | `707b4a506e80f68b7ba946de9bf080fa3e612848` | `obserwator[full]==3.0.0` |
| Hydrolog | [`v0.8.0`](https://github.com/Daldek/Hydrolog/releases/tag/v0.8.0) | `3353fc5e955768627ac656d463f687b1936cd350` | `hydrolog[all]==0.8.0` |
| Hydrograf | [`v0.5.0`](https://github.com/Daldek/Hydrograf/releases/tag/v0.5.0) | `634fce621029b6ef4b132608f4e6fac267a382eb` | no: an app on its own lock (ECO-074, ECO-077) |
| Archiwista | [`v0.3.0`](https://github.com/Daldek/Archiwista/releases/tag/v0.3.0) | `7fd25e872d565002b9ce390fa245746d075f7428` | `archiwista[obserwator]==0.3.0` |

`pyproject.toml` and `uv.lock` give the installable members at their tags
and every third-party package at one version for Linux, macOS and Windows:
the same 127 packages and third-party versions as candidate-6's lock. The
`nogat` package (HUB §7) does not exist yet, so the set is installed as an
environment, not with `uv tool install`:

```bash
git clone --branch v0.1.0 https://github.com/Daldek/Nogat
cd Nogat/release-sets/v0.1.0
uv sync --locked --no-dev
```

The members' commands (`kartograf`, `obserwator`, `hydrolog`, `archiwista`)
are then in `.venv/bin/`.

## Verification

candidate-6 was verified on Linux by `uv run scripts/ecosystem.py set verify`
on the author's machine, not by the workflow `verify-candidate`, which runs
only from `main` (REL-6.5 deviation): every member passed except the known
failures C2 and C3 of Archiwista's tests
([the integration run](../../docs/plans/2026-11-16-candidate-5-integration.md)).
Each member's release commit then passed its full gate. This set installs
from its lock with `uv sync --locked --no-dev`, and each member reports its
release version.
