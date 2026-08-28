---
repo: devops-tf-live-shipcars-platform-qa
path: ~/projects/ship-cars-usa/devops-tf-live-shipcars-platform-qa
stack: Terraform (live env) — `shipcars-platform-qa` GCP project
domain: infrastructure
shape: live-env IaC (same shape as `-dev`)
last-synced-commit: 0b4fab2fb6fae343eb9f460c8f70c0235eae353b
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# devops-tf-live-shipcars-platform-qa

## What it is
**QA-environment Terraform live-env IaC** for `shipcars-platform-qa`. Mirrors `-dev` and `-prod` structurally (`apis/buckets/cloudfunctions/cloudsql/firestore/gke/iam/monitoring/pubsub/redis/sm/tf-state/`). Used for pre-staging integration testing.

Last commit 2026-04-22 — actively maintained.

## How it fits

- **Provisions:** QA GCP-side resources. Typically validated after dev, before staging.
- See **`devops-tf-live-shipcars-platform-prod.md`** for full per-category breakdown + shared gotchas.

## Build / test / run
```
cd live/<category>
terraform init && terraform plan && terraform apply
```

## Don't-do-here / gotchas
See `devops-tf-live-shipcars-platform-prod.md` for shared caveats.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-platform-prod.md`.
- `~/projects/codebase-map/domains/infrastructure.md`.
