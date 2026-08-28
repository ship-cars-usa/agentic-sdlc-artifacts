---
repo: devops-tf-live-shipcars-ml-data-dev
path: ~/projects/ship-cars-usa/devops-tf-live-shipcars-ml-data-dev
stack: Terraform (live env) — GCS buckets + Databricks integration + Airbyte connectors for shipcars-ml-data-dev GCP project
domain: analytics
shape: live-env Terraform (`live/buckets/`, `live/tf-state/`, `live/iam/` — typical Ship.Cars `devops-tf-live-*` layout)
last-synced-commit: 510ef56ca8cdafd07999fc8da139e0f72a898b7d
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# devops-tf-live-shipcars-ml-data-dev

## What it is
**Terraform live-env IaC for the `shipcars-ml-data-dev` GCP project** — the dev side of the three-env triple (`-dev`, `-staging`, `-prod`) that provisions the ML / data-platform infrastructure.

Provisions:
- **GCS buckets** — `live/buckets/` has individual `.tf` files for `airbyte-platform-company-documents`, `airbyte-platform-production`, `airbyte-edge-user-activity-tracker`, `airbyte-core-posting`, and a `databricks.tf` for the Databricks-related buckets.
- **IAM** — `live/iam/` has `Add IAM roles and service accounts for Databricks integration` per the last commit message.
- **Terraform state** — `live/tf-state/` carries the per-env backend config.

Pattern matches `devops-tf-live-shipcars-logytext-integration` and the other `devops-tf-live-*` repos: per-product, per-env IaC supporting a specific service / data-platform component.

## How it fits

- **Provisions resources used by:** Databricks (data-warehouse compute + storage), Airbyte (data-ingestion connectors), `bi-databricks-backend`, `ai-dashboard-backend`, the `ml-*` services that read from the resulting buckets.
- **Consumes API of:** GCP (via `google` Terraform provider).
- **Owns data store:** Terraform state in GCS (per `live/tf-state/`).

## Build / test / run
```
cd live/buckets   # or live/iam, or live/tf-state
terraform init
terraform plan
terraform apply   # only via CI / coordinated runs
```

## Don't-do-here / gotchas

- **Probably belongs in `infrastructure` domain, not `analytics`.** Same observation as `devops-tf-live-shipcars-logytext-integration`. Flag for re-domain on next infrastructure-triage refresh.
- **One of three sibling repos** (`-dev`, `-staging`, `-prod`). Changes typically need to land in all three; verify before assuming a single-env apply propagates.
- **Airbyte bucket names** are checked into `.tf` files — they're the source of truth for connector config in `ml-data-hamal` / Airbyte. Renaming requires coordinated config updates.
- **`databricks.tf`** is the GCS-side of the Databricks workspace; pair with `ml-central-data-storage` (the Databricks-side asset bundle).

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-ml-data-staging.md` — staging sibling.
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-ml-data-prod.md` — prod sibling.
- `~/projects/codebase-map/repos/ml-central-data-storage.md` — Databricks-side asset bundle.
- `~/projects/codebase-map/repos/ml-data-hamal.md` — Airbyte-adjacent data porter.
- `~/projects/codebase-map/relations/infrastructure-triage.md` — flag for re-domain on next refresh.
- `~/projects/codebase-map/domains/analytics.md`.
