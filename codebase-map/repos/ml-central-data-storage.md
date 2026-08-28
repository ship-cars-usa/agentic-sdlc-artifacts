---
repo: ml-central-data-storage
path: ~/projects/ship-cars-usa/ml-central-data-storage
stack: Databricks workspace config (`databricks.yml`) + per-folder transformations / governance / dashboards / utilities
domain: analytics
shape: Databricks Asset Bundle (YAML + SQL / Python transformations)
last-synced-commit: 737dab9c50b7dbee8527a9b5fe6ca57d4891a9c6
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# ml-central-data-storage

## What it is
The **Databricks-side data-platform configuration repo** — not a runtime service. Holds the canonical Databricks workspace + asset bundle definition (`databricks.yml`) plus four content folders:

- **`transformations/`** — SQL / Python transformations that produce derived datasets.
- **`dashboards/`** — Databricks dashboard definitions.
- **`governance/`** — data-governance config (table ACLs, lineage tagging, retention).
- **`utilities/`** — helper scripts / notebooks.

Pairs with `bi-databricks-backend` (Quarkus service that talks to Databricks SQL Warehouse) and the executive dashboard frontends (`executive-dashboard-frontend`, `ai-dashboard-backend`).

Last commit 2026-05-04 — actively maintained.

## How it fits

- **Defines:** the Databricks workspace's assets — transformations, dashboards, governance policies.
- **Consumed by:** Databricks itself (via `databricks bundle deploy` or similar Asset Bundle commands).
- **Read by:** `bi-databricks-backend` queries the resulting tables; `executive-dashboard-frontend` renders dashboards defined here.

## Build / test / run
```
# Requires the Databricks CLI installed and authenticated.
databricks bundle validate
databricks bundle deploy
```

## Don't-do-here / gotchas

- **Not a service.** Don't expect runtime artifacts here.
- **Production deployments touch the Databricks workspace.** Changes are not isolated by branch — `databricks bundle deploy` against a prod target updates live tables / dashboards. Test in dev first.
- **No CI visible** at the repo level — coordinate deploys manually or via a Databricks-side pipeline.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/bi-databricks-backend.md` — the JVM-side bridge to Databricks SQL.
- `~/projects/codebase-map/repos/ai-dashboard-backend.md` — Spring service powering dashboards.
- `~/projects/codebase-map/repos/executive-dashboard-frontend.md` — UI for executive metrics.
- `~/projects/codebase-map/domains/analytics.md`.
