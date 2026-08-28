---
repo: devops-tf-live-shipcars-ml-data-staging
path: ~/projects/ship-cars-usa/devops-tf-live-shipcars-ml-data-staging
stack: Terraform (live env) — GCS buckets + Databricks integration for shipcars-ml-data-staging GCP project
domain: analytics
shape: live-env Terraform (`live/buckets/`, `live/tf-state/`)
last-synced-commit: 3532838029355be01f305a6dbe6813d2b3f7eb07
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# devops-tf-live-shipcars-ml-data-staging

## What it is
**Staging sibling** of `devops-tf-live-shipcars-ml-data-dev` and `devops-tf-live-shipcars-ml-data-prod`. Provisions the `shipcars-ml-data-staging` GCP project's data-platform resources via Terraform.

The repo has a slightly thinner layout than the dev variant (no separate `live/iam/` directory at HEAD — IAM may be folded into `live/buckets/` here, or staging hasn't yet absorbed the same IAM scope as dev). Carries `live/buckets/databricks.tf` + `backend.tf` + `locals.tf` plus the standard `live/tf-state/` bootstrap.

Last commit 2026-03-30 (`Add Terraform infrastructure for shipcars-ml-data-staging project`) — fresh setup that hasn't diverged much from prod's structure.

## How it fits

- **Provisions resources used by:** staging copies of the Databricks workspace + the airbyte data-ingestion connectors that prod consumes (per the dev sibling's layout).
- **Consumes API of:** GCP via `google` Terraform provider.
- **Owns data store:** Terraform state in GCS.

## Build / test / run
```
cd live/buckets        # or live/tf-state
terraform init
terraform plan
terraform apply
```

## Don't-do-here / gotchas

- **Same `infrastructure` re-domain candidate** as the dev / prod siblings.
- **Smaller surface than dev** — staging hasn't yet picked up IAM / Airbyte bucket definitions that dev has. Verify before treating it as a 1:1 mirror.
- **Coordinate with dev + prod siblings.** Changes to one env should typically land in all three (with appropriate per-env overrides).

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-ml-data-dev.md` — dev sibling (richer layout).
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-ml-data-prod.md` — prod sibling.
- `~/projects/codebase-map/repos/ml-central-data-storage.md` — Databricks-side asset bundle.
- `~/projects/codebase-map/relations/infrastructure-triage.md` — flag for re-domain on next refresh.
- `~/projects/codebase-map/domains/analytics.md`.
