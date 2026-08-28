---
repo: devops-tf-live-shipcars-production-env
path: ~/projects/ship-cars-usa/devops-tf-live-shipcars-production-env
stack: Terraform (live env) — older `shipcars-production-env` GCP project (predecessor of `-platform-prod`)
domain: infrastructure
shape: live-env IaC (smaller than `-platform-prod`: 31 files)
last-synced-commit: 3575eef1c2be021c08735efa94645d4683d44674
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# devops-tf-live-shipcars-production-env

## What it is
**Older "production-env" Terraform live-env** — predecessor / sibling of `-platform-prod`. Smaller scope (31 files vs `-platform-prod`'s 399), likely housing legacy resources that haven't migrated to the newer `-platform-prod` layout yet.

Last commit 2025-07-14 — slower cadence than `-platform-prod`.

## How it fits

- **Predecessor / coexists with:** `-platform-prod`.
- **Provisions:** legacy production resources still living here.

## Build / test / run
```
cd live/<category>
terraform init && terraform plan && terraform apply
```

## Don't-do-here / gotchas

- **Production state.** Same caution as `-platform-prod`. Atlantis flow only.
- **Confirm scope vs `-platform-prod`** before assuming a resource lives in one or the other.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-platform-prod.md` — modern sibling.
- `~/projects/codebase-map/domains/infrastructure.md`.
