---
repo: argo-wf-finalizer
path: ~/projects/ship-cars-usa/argo-wf-finalizer
stack: Go (tiny — `Dockerfile` + `main.go` + `go.mod` + 6 files total)
domain: infrastructure
shape: minimal Go binary
last-synced-commit: 0d157cfc9158f5c5ab478bf8fea1fecdfe0d1e70
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# argo-wf-finalizer

## What it is
**Argo Workflow Finalizer** — small Go binary that runs as a finalizer on Argo Workflow resources, presumably for cleanup tasks when a workflow completes (deleting artifacts, releasing locks, finalizing K8s state).

Minimal repo: 6 files. Last commit 2024-06-24 — ~683 days stale at sync time. Triage classified as `active` based on content presence; the staleness suggests "set-and-forget" infrastructure tooling.

## How it fits

- **Runs as:** finalizer on Argo Workflow resources (K8s mutating webhook or sidecar pattern).
- **Pairs with:** `argo` (the Argo CD/Workflows config repo), `argo-wf-notificator` (Go CLI sending status updates).

## Build / test / run
```
go build ./...
./argo-wf-finalizer
```

## Don't-do-here / gotchas

- **2-yrs-stale.** Verify whether it's still deployed and what Argo Workflows version it targets.
- **Finalizer semantics matter** — a buggy finalizer can block workflow deletion entirely. Test against a sample workflow before deploying any change.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/argo.md` — canonical Argo config.
- `~/projects/codebase-map/repos/argo-wf-notificator.md` — sibling Go tool.
- `~/projects/codebase-map/domains/infrastructure.md`.
