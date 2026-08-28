---
repo: devops-tf-module-local-cloudsql-users
path: ~/projects/ship-cars-usa/devops-tf-module-local-cloudsql-users
stack: Terraform module — Cloud SQL local-user (DB-side `CREATE USER`) management
domain: infrastructure
shape: reusable Terraform module (9 files)
last-synced-commit: 3104b2224d51c950d5fdcba90014b636a7a163ee
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# devops-tf-module-local-cloudsql-users

## What it is
**Reusable Terraform module for managing DB-side users on a Cloud SQL instance** — distinct from the IAM-side service-account → IAM-DB-user mapping. "Local" means **PostgreSQL-native users** (`CREATE USER ... WITH PASSWORD ...`) rather than IAM-authenticated users.

Companion to `devops-tf-module-postgres-cloudsql` (which provisions the instance itself). Last commit 2025-09-03.

## How it fits

- **Consumed by:** `live/cloudsql/` per-env Terraform when each fleet service needs a PG user provisioned. The per-service user creds are typically stored in Secret Manager and referenced by the service's helm `externalSecrets` block.
- **Pairs with:** `devops-tf-module-postgres-cloudsql` (the instance module).

## Build / test / run
```
terraform init && terraform plan && terraform apply
```

## Don't-do-here / gotchas

- **PG password generation** — verify whether the module generates passwords or expects them as input. Generated passwords need to be captured into Secret Manager.
- **User deletion** triggers PG-level disconnects. Coordinate with running services.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/devops-tf-module-postgres-cloudsql.md` — sibling instance module.
- `~/projects/codebase-map/domains/infrastructure.md`.
