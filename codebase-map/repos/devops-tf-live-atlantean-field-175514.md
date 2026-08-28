---
repo: devops-tf-live-atlantean-field-175514
path: ~/projects/ship-cars-usa/devops-tf-live-atlantean-field-175514
stack: Terraform (live env) — older GCP project `atlantean-field-175514` (project-ID-named, predating the `shipcars-*` naming convention)
domain: infrastructure
shape: live-env IaC (`buckets/cloudfunctions/gke/iam/messaging-prod/monitoring/tf-state/`)
last-synced-commit: 9b18130089cfb236c5b6a2f0713cc047af952bc0
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# devops-tf-live-atlantean-field-175514

## What it is
**Older GCP project `atlantean-field-175514`** — pre-rebrand project name, predating the `shipcars-*` naming convention. The project ID is a GCP-generated random name (`atlantean-field-175514` = adjective-noun-number = classic GCP auto-naming).

**Specifically referenced** by `ml-model-rate-confidence-absolute` (and the rest of the `ml-model-*` family) — its `settings.py` carries:
```python
"gcs": {
  "project_id": "atlantean-field-175514",
  "bucket_name": "production-rate-engine-model",
  ...
}
```

So this project still hosts the **ML model artifacts GCS bucket** used by the entire rate / confidence / multivehicle inference fleet. **Effectively a legacy-but-load-bearing GCP project**.

Last commit 2025-12-12.

## How it fits

- **Hosts:** ML model artifact GCS bucket (`production-rate-engine-model`) consumed by `ml-model-rate`, `ml-model-rate-confidence-absolute`, `ml-model-rate-confidence-percentage`, `ml-model-rate-multivehicle`, `ml-model-training`.
- **Pre-rebrand project.** Naming exception in the fleet — most other Terraform live envs use the `shipcars-*` convention.

## Build / test / run
```
terraform init && terraform plan && terraform apply
```

## Don't-do-here / gotchas

- **Renaming the project is impossible** without a coordinated migration of every ML-model service's `settings.py`. Don't try.
- **`messaging-prod/`** + `monitoring/` + `gke/` suggest the project still hosts some production resources beyond just the GCS bucket. Confirm scope before assuming "just ML artifacts."
- **Likely the oldest active GCP project** in the fleet.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/ml-model-rate.md` / `ml-model-rate-confidence-absolute.md` / `ml-model-rate-confidence-percentage.md` / `ml-model-rate-multivehicle.md` / `ml-model-training.md` — consumers of the GCS bucket in this project.
- `~/projects/codebase-map/domains/infrastructure.md`.
