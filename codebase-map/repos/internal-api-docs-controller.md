---
repo: internal-api-docs-controller
path: ~/projects/ship-cars-usa/internal-api-docs-controller
stack: Go / `k8s.io/client-go` (in-cluster Kubernetes API watch) / logrus JSON logging
domain: platform
shape: small Kubernetes controller
last-synced-commit: f10e31a429731fdecef2efd2468ed09da5050f56
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# internal-api-docs-controller

## What it is
A **Kubernetes controller** that watches a configmap (`APP_CONFIGMAP=ship-cars-api-docs-paths`) and reacts to changes — likely **dynamically updating the API-doc paths** that `internal-api-docs` / `api-documentation-builder` aggregate. Reads in-cluster `rest.InClusterConfig()` or falls back to `$HOME/.kube/config` for local dev.

Uses `k8s.io/client-go`'s informers pattern (`informers.SharedInformerFactory`) for efficient event watching.

**Last commit 2023-03-14** (`make it for the whole cluster`) — **3 years stale**. Either:
1. The controller is still running but hasn't needed updates in 3 years (mature, stable), or
2. The dynamic-config approach was abandoned in favor of static config.

## How it fits

- **Consumes:** Kubernetes API (configmap watcher + presumably pod / service watchers for the API-docs paths).
- **Drives:** likely the path-to-spec mapping consumed by `api-documentation-builder` or `internal-api-docs`.
- **Owns data store:** none (config lives in the watched configmap).

## Build / test / run
```
go build ./...
./internal-api-docs-controller   # requires kubeconfig or in-cluster service account
```

## Don't-do-here / gotchas

- **3-year-stale.** Verify whether this controller is still running in any environment before changing anything. If retired, archive-candidate.
- **K8s permissions** — needs ClusterRole for configmap watch. Don't over-grant.
- **Requires `client-go` deps that may be tied to specific K8s API versions.** A cluster upgrade can silently break the watcher if API resources have shifted.
- **Separate from `logging-manager`'s K8s integration** — both Go services touch K8s but for different purposes.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/internal-api-docs.md` — Node service this controller likely supports.
- `~/projects/codebase-map/repos/api-documentation-builder.md` — companion that builds the combined spec.
- `~/projects/codebase-map/relations/infrastructure-triage.md` — flag for re-evaluation if 3-year-stale = retired.
- `~/projects/codebase-map/domains/platform.md`.
