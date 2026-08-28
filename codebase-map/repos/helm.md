---
repo: helm
path: ~/projects/ship-cars-usa/helm
stack: Helm charts (one per fleet service, all under `helm/ship-cars-usa/`)
domain: infrastructure
shape: **monorepo of per-service Helm charts** (1904 files, ~100+ subcharts)
last-synced-commit: 8c08b554782a531f30ad830cb35419729c5cee7d
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# helm

## What it is
**The fleet's central Helm-chart monorepo.** Contains one Helm chart per deployable service under `helm/ship-cars-usa/<service>/` — Charts for essentially every service in the fleet (`aaag-integration`, `airbyte`, `allure`, `api-gateway`, `attachment-backend`, `chat-backend`, `command-executor`, `cube`, `dataone`, `pusher`, `posting-backend`, `socket-server`, `socket-server-old`, etc., plus infrastructure components like `cert-manager`, `clickhouse`, `datadog`, `custom-metrics-stackdriver-adapter`).

Many of the fleet's load-bearing operational facts live here: `socket-server-old/values-production.yaml` carries the hardcoded HS256 JWT secret flagged in the `socket-server-old` seed; per-service `secretConfig:` / `externalSecrets:` blocks carry the credentials wiring; `replicaCount`, `resources`, `autoscaling`, `nodeSelector`, `affinity` define every service's K8s footprint. **This is the catalog's authoritative source for "what runs in production and at what shape."**

Includes a top-level `atlantis.yaml` (Atlantis-managed PR-based Helm deploys) and `scripts/` for utility tasks. Last commit 2026-05-07 (0 days ago — **most-frequently-touched repo in the catalog**).

## How it fits

- **Consumed by:** ArgoCD (likely; per `argo` repo's presence) and/or Atlantis (per top-level `atlantis.yaml`) for K8s deploys of every fleet service.
- **Pairs with:**
  - **`helm-common-chart`** — the reusable Helm template library this repo's charts depend on.
  - **`docker-utils`** — the base Docker images these charts reference.
  - **`argo`** — Argo CD + Workflows infrastructure config.
- **Owns:** per-service prod / staging / qa / dev values files + chart templates.

## Build / test / run
```
cd ship-cars-usa/<service>
helm dependency update
helm lint .
helm template . -f values-production.yaml
helm install --dry-run --debug -f values-production.yaml ...
```

Atlantis runs `helm plan` / `helm apply` on PR merges per the top-level `atlantis.yaml`.

## Key abstractions

- `ship-cars-usa/<service>/Chart.yaml` — per-service chart metadata (`appVersion` mirrors the service's image tag).
- `ship-cars-usa/<service>/values-{dev,qa,staging,production,template}.yaml` — per-env values.
- `ship-cars-usa/<service>/templates/` — K8s manifest templates.
- `ship-cars-usa/<service>/charts/` — local dep cache (after `helm dependency update`).
- `atlantis.yaml` — Atlantis project config; orchestrates PR-based applies across services.
- `scripts/` — utility scripts (probably bulk-template-render, value-validation, etc.).

## Don't-do-here / gotchas

- **The catalog's source of truth for production state.** When a shadow doc says "service X has 2 replicas" or "service Y has pool-size=5," those facts come from this repo's `values-*.yaml`. A change here without a parallel shadow-doc update silently drifts the catalog.
- **`socket-server-old` JWT secret is in `helm/ship-cars-usa/socket-server-old/values-*.yaml`** — same plaintext secret across all 4 envs (per the seed). Fix lives in this repo, not in `socket-server-old`.
- **Atlantis-driven PR-based applies** mean every helm change goes through `atlantis plan` + `atlantis apply` comments in the PR. Manual `helm apply` from a developer machine is not the canonical path; coordinate via PR.
- **1904 files = large repo.** Cloning + grep operations can be slow. Use targeted `helm/ship-cars-usa/<service>/` paths.
- **Per-service charts vary in maturity.** Older charts (e.g. `socket-server-old`) carry legacy patterns; newer charts use `externalSecrets` + GCP Secret Manager. Don't copy-paste a chart pattern without checking how recent the source is.
- **`appVersion` lock-step** — chart `appVersion` tracks the service image tag. When a service ships a new image, the corresponding chart's `appVersion` (or the `image.tag` in `values-*.yaml`) needs to update.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/helm-common-chart.md` — shared Helm template lib used by these charts.
- `~/projects/codebase-map/repos/docker-utils.md` — base Docker images referenced.
- `~/projects/codebase-map/repos/argo.md` — Argo CD / Workflows config.
- `~/projects/codebase-map/repos/socket-server-old.md` — credential leak documented here.
- Per-service shadow docs reference `helm/ship-cars-usa/<service>/values-production.yaml` for deploy facts.
- `~/projects/codebase-map/domains/infrastructure.md`.
