---
repo: devops-tf-module-postgres-cloudsql
path: ~/projects/ship-cars-usa/devops-tf-module-postgres-cloudsql
stack: Terraform module — Google Cloud SQL PostgreSQL (`>=7.0.0` provider, `>=1.5.0` Terraform)
domain: infrastructure
shape: reusable Terraform module
last-synced-commit: 9364cdefad806445562de32e024c3c2d949f29ad
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# devops-tf-module-postgres-cloudsql

## What it is
**Reusable Terraform module for Google Cloud SQL PostgreSQL instances.** Provides the canonical Ship.Cars wrapper around CloudSQL with built-in features (per README): **read replicas, user management, database roles, and DNS records**. Required versions: Terraform `>=1.5.0` + Google provider `>=7.0.0`.

Has `examples/` showing usage + `CHANGELOG.md` + standard `main.tf`/`variables.tf`/`output.tf`/`versions.tf`/`locals.tf` layout. The README includes a Mermaid architecture diagram.

Last commit 2026-02-18.

## How it fits

- **Consumed by:** the per-env Terraform live-envs' `live/cloudsql/` directories. Every fleet Postgres database (`posting` PG, `loadboard` PG, `chat` PG, etc.) is provisioned via this module.
- **Pairs with:** `devops-tf-module-local-cloudsql-users` (sister user-management module).
- **Influence:** any fleet-wide Postgres-config standardization (e.g. enforcing a connection-flag default, requiring a specific maintenance window) lands here.

## Build / test / run
```
# In a consuming live-env:
terraform init
terraform plan
terraform apply
```

## Don't-do-here / gotchas

- **Module breaking changes cascade.** Every consumer's `terraform plan` re-evaluates. Use semver disciplined version pins.
- **Read-replica config is a one-shot operation** — adding a replica triggers a fresh sync from primary; large DBs take time.
- **User-management** semantics differ from `devops-tf-module-local-cloudsql-users`. Coordinate which module owns which auth path.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/devops-tf-module-local-cloudsql-users.md` — sibling user-management module.
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-platform-prod.md` — primary consumer (via `live/cloudsql/`).
- `~/projects/codebase-map/domains/infrastructure.md`.
