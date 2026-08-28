---
repo: elk-backup-restore
path: ~/projects/ship-cars-usa/elk-backup-restore
stack: Python / `kubectl`-based access (`.kubeconfig`) to ELK clusters
domain: analytics
shape: single-module operational script
last-synced-commit: 7d284221b718d35f7967c6e38ada0069f9d2b1e9
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# elk-backup-restore

## What it is
**ELK snapshot / restore operational script.** Creates and restores Elasticsearch snapshots for designated indices, parametrized by config / env vars. Connects to source and destination ELK clusters via local `.kubeconfig` files; **operator-run**, not a service.

Verifies the snapshot repository is enabled in the target ELK cluster before attempting any snapshot operation — and fails fast if not.

Last commit 2024-11-15 (`update defaults.py`). The repo is operationally important during incident response or cluster migrations but doesn't run on a schedule by itself.

## How it fits

- **Consumes:** Elasticsearch HTTP API on the source + destination clusters, routed through `kubectl port-forward` (the `.kubeconfig` is the mechanism). Both clusters must be reachable via the local kubeconfig.
- **Writes to:** the destination ELK cluster (restore) or a snapshot repository (backup).
- **Owns data store:** none directly — operates on ELK clusters owned by ops.

## Build / test / run
```
pip install -r requirements.txt
# Ensure ~/.kube/config has contexts for both clusters.
cd src
python main.py        # configured via src/config.py + env vars
```

`src/config.py` reads from env vars first, falling back to `src/defaults.py` values.

## Key abstractions

- `src/config.py` — env-var-driven config; falls through to `defaults.py`.
- `src/defaults.py` — fallback values (most recently touched).
- `src/main.py` (presumed entry) — snapshot / restore orchestration.

## Don't-do-here / gotchas

- **Operator-run.** Wrong cluster context = restoring snapshot data to the wrong cluster, which can clobber production indices. Verify `kubectl config current-context` before running.
- **Snapshot repository must be enabled** in the target ELK cluster — the script fails fast if not, but the operator must know how to enable it (this isn't documented inside the repo).
- **Old last-commit (2024-11-15)** — verify the script still works against the current ELK cluster versions before assuming it's ready in an incident.
- **No tests, no CI** — operational script. Treat as untested.
- **`.kubeconfig`-dependent** — operator must have access to both clusters via kubeconfig, including correct service-account permissions.
- **Probably belongs in `infrastructure`** rather than `analytics` — it's a cluster-ops tool, not an analytics service. Flag for the next infrastructure-triage refresh.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/syncer.md` — writes to Elasticsearch (the snapshot target).
- `~/projects/codebase-map/repos/cube.md` — reads from Elasticsearch.
- `~/projects/codebase-map/relations/infrastructure-triage.md` — flag for re-domain on next refresh.
- `~/projects/codebase-map/domains/analytics.md`.
