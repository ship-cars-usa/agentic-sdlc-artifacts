---
repo: devops-tf-live-shipcars-ml-data-prod
path: ~/projects/ship-cars-usa/devops-tf-live-shipcars-ml-data-prod
stack: Terraform (live env) — GCS buckets + Databricks integration for shipcars-ml-data-prod GCP project
domain: analytics
shape: live-env Terraform (`live/buckets/`, `live/tf-state/`)
last-synced-commit: 78d0b7de1b4abb76f5758eb09c2cd3cc54a282d9
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# devops-tf-live-shipcars-ml-data-prod

## What it is
**Production sibling** of `devops-tf-live-shipcars-ml-data-dev` and `-staging`. Provisions the `shipcars-ml-data-prod` GCP project's data-platform resources (Databricks-related buckets, `tf-state` backend). Layout matches the staging sibling closely (no `live/iam/` at HEAD — narrower than dev).

Last commit 2026-03-31 (`Add Terraform infrastructure for shipcars-ml-data-prod`) — fresh setup, just after staging.

## How it fits

- **Provisions** the production data-platform GCS surface that `bi-databricks-backend` and `ai-dashboard-backend` read from.
- **Consumes API of:** GCP via `google` Terraform provider.
- **Owns data store:** Terraform state in GCS (per the `tf-state` backend).

## Build / test / run
```
cd live/buckets        # or live/tf-state
terraform init
terraform plan
terraform apply        # only via CI / coordinated runs — production state
```

## Don't-do-here / gotchas

- **Production state.** Misapplied changes affect prod data ingestion / Databricks. Never `terraform apply` from a personal machine; CI / pipeline only.
- **Same `infrastructure` re-domain candidate** as the dev / staging siblings.
- **Coordinate with the dev + staging siblings.** Production changes should usually have been validated in dev + staging first.
- **`live/iam/` missing at HEAD** (vs. the dev sibling which has it) — confirm whether IAM provisioning happens here too or is split across another repo / project.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-ml-data-dev.md` — dev sibling (richer layout).
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-ml-data-staging.md` — staging sibling.
- `~/projects/codebase-map/repos/ml-central-data-storage.md` — Databricks-side asset bundle.
- `~/projects/codebase-map/relations/infrastructure-triage.md` — flag for re-domain on next refresh.
- `~/projects/codebase-map/domains/analytics.md`.
