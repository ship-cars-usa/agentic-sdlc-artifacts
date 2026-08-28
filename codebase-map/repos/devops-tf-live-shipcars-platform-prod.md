---
repo: devops-tf-live-shipcars-platform-prod
path: ~/projects/ship-cars-usa/devops-tf-live-shipcars-platform-prod
stack: Terraform (live env) — `shipcars-platform-prod` GCP project
domain: infrastructure
shape: live-env IaC (`live/{apis,bigquery,buckets,cloudfunctions,cloudsql,firestore,gke,iam,monitoring,pubsub,redis,sm,tf-state}/`)
last-synced-commit: d110047d262298a470659b7a02fd3291d293444b
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# devops-tf-live-shipcars-platform-prod

## What it is
**Production-environment Terraform live-env IaC** for the `shipcars-platform-prod` GCP project — provisions every GCP resource the production fleet runs on. 13 resource categories:

| Category | Manages |
|---|---|
| `apis/` | enabled GCP APIs |
| `bigquery/` | BigQuery datasets / tables (analytics surface) |
| `buckets/` | GCS buckets |
| `cloudfunctions/` | Cloud Functions deployments |
| `cloudsql/` | Cloud SQL instances (Postgres for most fleet services) |
| `firestore/` | Firestore databases (consumed by `quarkus-extension-firestore-storage` users like `command-executor`) |
| `gke/` | GKE clusters (where every fleet service runs) |
| `iam/` | service accounts, IAM bindings |
| `monitoring/` | Cloud Monitoring / Datadog hooks |
| `pubsub/` | Pub/Sub topics + subscriptions for the fleet's async substrate |
| `redis/` | Memorystore Redis instances (consumed by `socket-server` etc.) |
| `sm/` | Secret Manager secrets |
| `tf-state/` | Terraform state bucket bootstrap |

**Last commit 2026-05-07 — 1 day ago at sync time.** Among the most-frequently-touched infra repos in the catalog.

## How it fits

- **Provisions:** production GCP-side of the entire Ship.Cars fleet.
- **Consumed by:** Atlantis-managed PR-based Terraform applies (likely via the top-level `atlantis.yaml` pattern seen in `helm`).
- **Sibling envs:**
  - `devops-tf-live-shipcars-platform-dev` (224 files)
  - `devops-tf-live-shipcars-platform-qa` (232 files)
  - `devops-tf-live-shipcars-platform-staging` (308 files)
  - `devops-tf-live-shipcars-system-env` (system/shared resources across all envs)
  - `devops-tf-live-shipcars-development-env` (older dev-env bootstrap)
  - `devops-tf-live-shipcars-production-env` (older prod bootstrap; smaller)
- **Source-of-truth for:** Pub/Sub topic config (max-delivery-attempts, DLQ), GKE cluster sizing, Cloud SQL instance specs, Redis cluster sizing, IAM bindings, Secret Manager secrets.

## Build / test / run
```
cd live/<category>     # e.g. cd live/pubsub
terraform init
terraform plan
terraform apply        # CI / Atlantis only — production state
```

## Don't-do-here / gotchas

- **Production state.** Misapplied changes affect prod traffic / data. Never `terraform apply` from a personal machine. Use Atlantis PR-flow.
- **Atlantis-driven** (likely; per the `helm` repo pattern). The PR is the canonical interface.
- **Pub/Sub subscription audit lives here.** The fleet-wide "every prod subscription has `Maximum delivery attempts` + `Dead letter topic`" question (from `quarkus-pubsub` seed) is answered by walking `live/pubsub/`. The audit gap deferred per user feedback would land in this repo's review.
- **Coordinate with sibling envs.** Resource shapes typically validated in dev → qa → staging → prod. A direct prod change without prior-env validation is a bigger risk.
- **`tf-state/` bootstrap is foundational** — touching it requires extreme care.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-platform-dev.md` / `-qa.md` / `-staging.md` — sibling envs.
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-system-env.md` — system/shared env.
- `~/projects/codebase-map/repos/helm.md` — pairs with this for K8s-state.
- `~/projects/codebase-map/repos/quarkus-pubsub.md` — fleet's Pub/Sub substrate; subscriptions provisioned here.
- `~/projects/codebase-map/domains/infrastructure.md`.
