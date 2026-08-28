---
repo: devops-tf-module-google-iam-management
path: ~/projects/ship-cars-usa/devops-tf-module-google-iam-management
stack: Terraform module — Google Cloud IAM
domain: infrastructure
shape: reusable Terraform module (9 files)
last-synced-commit: 75e0a9118f97b3a2a2797b4956bb46ad647d9397
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# devops-tf-module-google-iam-management

## What it is
**Reusable Terraform module for managing Google Cloud IAM bindings** — service accounts, role assignments, member bindings across GCP projects. Small module (9 files). Last commit 2025-10-14.

## How it fits

- **Consumed by:** every `live/iam/` directory across the Terraform live-env repos.
- **Sibling:** `devops-tf-module-local-cloudsql-users` (DB-specific user management).

## Build / test / run
```
# In a consuming live-env's iam/ subdir
terraform init && terraform plan && terraform apply
```

## Don't-do-here / gotchas

- **Cluster-wide blast radius via IAM.** A wrong binding granted via this module's consumers can over-privilege a service account fleet-wide.
- **Module breaking changes** cascade through every `live/iam/`.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-gcp-projects-access.md` — cross-project IAM consumer.
- `~/projects/codebase-map/domains/infrastructure.md`.
