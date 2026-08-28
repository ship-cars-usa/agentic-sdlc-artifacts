---
repo: knowledge-products
path: ~/projects/ship-cars-usa/knowledge-products
stack: Docs / per-product subfolders (`ctms/`, `loadmate/`)
domain: infrastructure
shape: product-specific docs (30 files)
last-synced-commit: a1067a6ff341c41eb918057c1ad6719cc825bddc
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# knowledge-products

## What it is
**Product-specific knowledge repo** — companion to `knowledge` (the broader engineering KB). Top-level folders for each product: `ctms/` and `loadmate/` — the two main Ship.Cars product lines.

Has `Dockerfile` (matching `knowledge`'s pattern — likely served as containerized docs at an internal URL).

Last commit 2026-03-20.

## How it fits

- **Product-specific knowledge** for CTMS (legacy load-board system) + Loadmate (modern Ship.Cars app).
- **Pairs with:** `knowledge` (broader KB) + `devops-docs` (DevOps-specific).

## Build / test / run
```
docker build .         # if served via Dockerfile
```

## Don't-do-here / gotchas

- **CTMS retirement.** `ctms/` documents a system that's being phased out (per `negotiations-router`'s seed). Confirm whether the docs are still being kept current.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/knowledge.md` — sibling broader KB.
- `~/projects/codebase-map/repos/negotiations-router.md` — CTMS retirement plan.
- `~/projects/codebase-map/domains/infrastructure.md`.
