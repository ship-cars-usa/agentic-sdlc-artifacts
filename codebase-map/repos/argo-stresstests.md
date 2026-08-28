---
repo: argo-stresstests
path: ~/projects/ship-cars-usa/argo-stresstests
stack: Helm charts / Argo Workflows stress-test scenarios
domain: infrastructure
shape: argo/ + charts/ + misc/ (151 files; mirror of `argo` layout)
last-synced-commit: bac4c53f1552005446de6ac648807ebf0ed033e9
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# argo-stresstests

## What it is
**Stress-test configuration for Argo Workflows.** Sibling repo of `argo` — same `argo/ + charts/ + misc/` layout. Contains workflow definitions for load-testing the Argo Workflows controller (probably "fire 100 workflows in parallel" or "long-running workflow scaling tests").

Last commit 2024-05-20 — **~717 days stale at sync time**. Triage classified as `active` based on content presence (151 files), but the staleness suggests it's a "ran once, kept around for re-running" rather than active development.

## How it fits

- **Drives:** stress-test scenarios against Argo Workflows.
- **Sibling:** `argo` (the canonical Argo config repo).

## Build / test / run
```
helm lint .
helm template .
kubectl apply -f charts/...
```

## Don't-do-here / gotchas

- **2-yrs-stale.** Verify whether it's still runnable against the current Argo Workflows version before assuming any stress-test scenario works.
- **Don't run stress tests against prod.** The naming makes the audience obvious, but worth saying.
- **Confirm with the SRE / DevOps owner** whether this repo is still meaningful or should be archived.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/argo.md` — canonical Argo config sibling.
- `~/projects/codebase-map/domains/infrastructure.md`.
