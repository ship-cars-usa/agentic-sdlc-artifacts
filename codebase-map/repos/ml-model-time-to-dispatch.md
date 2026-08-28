---
repo: ml-model-time-to-dispatch
path: ~/projects/ship-cars-usa/ml-model-time-to-dispatch
stack: Python (placeholder — `pyproject.toml` + dev tooling only; no implementation)
domain: pricing-billing
shape: empty placeholder (README + pyproject + requirements-dev only)
last-synced-commit: 5108056ce0be7cd3097b0055036f104d3fcac9d5
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# ml-model-time-to-dispatch

## What it is
**Empty placeholder repo.** Intended to be the time-to-dispatch ML model service (sibling of the rate / confidence / multivehicle models under `ml-service-dispatcher`), but **the implementation was never committed**. The entire repo is:

- `README.md` — one line: "ML Model Services for Time to Dispatch Model".
- `pyproject.toml` — black + isort + pytest config; black `target-version=["py36","py37","py38"]` (the same out-of-date Python targets as the active ml-model siblings).
- `requirements-dev.txt` — dev-only deps.
- `CLAUDE.md` — Claude Code rules.

No `code/`, no `builder/`, no `Dockerfile`, no source code, no model artifact references. **Not deployed anywhere** (no helm chart was found by quick grep; verify on next deploy-config probe).

Last commit 2025-10-10 (`LITE-6539 Add Claude Code configuration files`) — that touched only the Claude config. No actual model code has ever been committed.

## How it fits

- **Not in any data flow.** No callers, no callees, no data store.
- **If activated:** would be called by `ml-service-dispatcher` alongside the other `ml-model-*` services, presumably predicting "how long until this load gets dispatched" given its current attributes.

## Build / test / run

Not applicable — no implementation. The repo is a name-reservation / scaffolding stub.

## Key abstractions

None — the repo is empty of source code.

## Don't-do-here / gotchas

- **Either implement or archive.** This is a name-reserved repo without an implementation — it sits as a stub in the catalog purely because the repo exists in `~/projects/ship-cars-usa/`. If the time-to-dispatch model is a real upcoming feature, the repo can be filled in using `ml-model-rate-multivehicle` as the template. If it's abandoned, retire the repo to clean up the catalog.
- **`PROJECTS_INDEX.md` lists this as Python** — not wrong, but misleading; consumers expect a working service.
- **Don't pattern-match production ML services after this repo.** Use `ml-model-rate-multivehicle` or `ml-model-rate-confidence-absolute` as the canonical template.

## Status / recommendation

**Archive-candidate** unless there's a roadmap commitment to fill it in. Flag for the next `infrastructure-triage.md` refresh.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/ml-model-rate.md` — template the implementation would follow.
- `~/projects/codebase-map/repos/ml-model-rate-multivehicle.md` — sibling with a different request shape; either template works.
- `~/projects/codebase-map/repos/ml-service-dispatcher.md` — the upstream caller this service would plug into if implemented.
- `~/projects/codebase-map/relations/infrastructure-triage.md` — flag for archive on next refresh.
- `~/projects/codebase-map/domains/pricing-billing.md`.
