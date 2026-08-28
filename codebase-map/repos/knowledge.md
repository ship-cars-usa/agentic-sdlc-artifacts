---
repo: knowledge
path: ~/projects/ship-cars-usa/knowledge
stack: Mixed docs / `INDEX.md` + `adr/` + `contracts/` + `conventions/` + `domain/` + `guides/` + `SHIP_CARS_DOCS.md`
domain: infrastructure
shape: engineering-knowledge-base repo (107 files)
last-synced-commit: 11a40d060779fed0ba80eaec1a43a5fcb732a8a6
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# knowledge

## What it is
**The Ship.Cars engineering-knowledge-base repo** — broader-scope companion to `devops-docs`. Top-level structure suggests Architecture Decision Records (`adr/`), service-contract docs (`contracts/`), coding/operational conventions (`conventions/`), business-domain documentation (`domain/`), how-to guides (`guides/`), plus `INDEX.md` and `SHIP_CARS_DOCS.md` as entry points.

Notably has a `Dockerfile` — implies the docs are containerized (perhaps served via a static site at an internal URL like `docs.internal.ship.cars`).

Last commit 2026-03-20.

## How it fits

- **Source of truth for:** ADRs, contract docs, conventions — the kinds of artifacts that `codebase-map/` shadow docs cross-reference.
- **Pairs with:** `knowledge-products` (product-specific knowledge: `ctms/`, `loadmate/`), `devops-docs` (DevOps-specific), `dev-hub` (AI/dev-tooling repo flagged `unsure` in triage).

## Build / test / run
```
docker build .         # if served via Dockerfile
# Otherwise: browse markdown via GitHub UI or local editor
```

## Don't-do-here / gotchas

- **Multi-purpose docs repo** — coordinate where things live (`adr/` here vs. `~/projects/codebase-map/adr/` which has its own ADR collection; verify the distinction).
- **The `codebase-map/` shadow docs reference ADR numbers** that may or may not match what's in `knowledge/adr/`. Cross-check on any specific ADR.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/knowledge-products.md` — sibling for product-specific knowledge.
- `~/projects/codebase-map/repos/devops-docs.md` — DevOps-specific.
- `~/projects/codebase-map/domains/infrastructure.md`.
