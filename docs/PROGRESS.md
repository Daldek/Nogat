# Progress

## Status

| Component | State | Note |
|---|---|---|
| Standard 2.1 | in progress | not yet published to `main`; tagged `std-2.1` when it is (HUB-6.1) |
| Registry and schema | done | `ecosystem.yaml`, `schemas/ecosystem.schema.json` |
| `validate`, `map`, `deps`, `drift` | done | `scripts/ecosystem.py`, errors by the registry (HUB-4.8) |
| Hub gate and CI | done | `scripts/gate.sh` on `uv.lock`, tests in `tests/` |
| Standard checks | done | `uv run scripts/ecosystem.py standard`, in the gate |
| Contradictions in standard 2.1 | done | ECO-042 to ECO-049 and consistency fixes |
| Canonical agent-interface schemas | planned | envelope, error, catalog; conformance test |
| Generated `AGENTS.md` (HUB-4.3) | planned | routing table with links |
| `nogat` package (HUB §7) | planned | |
| Adoption in the projects | planned | ADOPTION_PLAN phases 1 to 6 |

## Next

1. Canonical schemas in `schemas/` for `<tool>-result/1`, `<tool>-error/1`
   and `<tool>-commands/1`, with a conformance test.

## Open questions

- Hydraulik's registry entry declares a CLI and package that are not
  committed (code in an uncommitted worktree): commit it, or mark the entry
  `research` until then?
- Publishing 2.1 to `main` (and its tag) and replacing the v1 `templates/`
  and `configs/` (root-owned files).
- The plans in `docs/plans/` predate DEV-17.4's `Approved:` line: add it to
  the ones the author approved.
