---
repo: fe-exercise-inventory-ui
path: ~/projects/ship-cars-usa/fe-exercise-inventory-ui
stack: Docs / Markdown
domain: listings-trade
shape: single-module (README-only)
last-synced-commit: 575f59fc06023268d4dba2412e7b799960be847e
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# fe-exercise-inventory-ui

## What it is
**Hiring artifact — not a production service.** A README-only "starting-point" repo handed to candidates for the Ship.Cars Front-End Developer coding challenge. Candidates clone it, build a small React app per their interviewer's brief, and point it at the sibling `fe-exercise-inventory-api` (Express + Mongoose) for data. The repo contents are intentionally minimal — the README welcomes the candidate and tells them to ask clarifying questions if needed.

Last commit 2025-07-25 (`Add Readme file`). No source code, no fleet integration.

## How it fits

- **Not part of any production data flow.** Pair with `fe-exercise-inventory-api`.

## Build / test / run
```
# README-only — no build, no tests.
# Candidates start their own scaffolding (CRA / Vite / Next.js / etc.) inside the repo.
```

## Key abstractions
- `README.md` — the candidate-facing prompt.

## Don't-do-here / gotchas
- **Currently sits in `listings-trade`** by name-match (`inventory`). Re-domain candidate to `infrastructure` or mark as a hiring artifact on the next infrastructure-triage refresh.
- **Don't pattern-match production MFEs after this repo.** It's deliberately empty.
- **Shared externally with interview candidates.** Don't add Ship.Cars-internal documentation or examples here.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/fe-exercise-inventory-api.md` — the API half of the same coding challenge.
- `~/projects/codebase-map/relations/infrastructure-triage.md` — flag for re-domain on next refresh.
- `~/projects/codebase-map/domains/listings-trade.md`.
