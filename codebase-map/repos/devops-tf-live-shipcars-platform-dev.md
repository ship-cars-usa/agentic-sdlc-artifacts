---
repo: devops-tf-live-shipcars-platform-dev
path: ~/projects/ship-cars-usa/devops-tf-live-shipcars-platform-dev
stack: Terraform (live env) — `shipcars-platform-dev` GCP project
domain: infrastructure
shape: live-env IaC (`live/{apis,buckets,cloudfunctions,cloudsql,firestore,gke,iam,monitoring,pubsub,redis,sm,tf-state}/`)
last-synced-commit: 8a1b4e4a520e21f4d86d73bf44b0b8f51038abdb
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# devops-tf-live-shipcars-platform-dev

## What it is
**Dev-environment Terraform live-env IaC** for the `shipcars-platform-dev` GCP project. Same shape as `devops-tf-live-shipcars-platform-prod` but **without `bigquery/`** (analytics surface is prod-only or staging-tested). Includes `manual_steps.txt` at the top level — manual setup steps for the env.

Used by every fleet service's dev deployment. Last commit 2026-05-07 — 1 day ago at sync time. **Most actively-touched dev env**.

## How it fits

- **Provisions:** dev GCP-side resources for the entire fleet (smaller-spec instances vs prod).
- **Sibling envs:** `-qa`, `-staging`, `-prod` (see prod seed for full sibling list).
- See **`devops-tf-live-shipcars-platform-prod.md`** for the full per-category breakdown — this repo mirrors it.

## Build / test / run
```
cd live/<category>
terraform init && terraform plan && terraform apply
```

## Don't-do-here / gotchas

- **Dev env, but `terraform apply` still affects shared resources.** Coordinate with the team before destroying / re-creating dev-cluster components.
- **`manual_steps.txt`** documents the bootstrap order — read it before doing fresh setup.
- See `devops-tf-live-shipcars-platform-prod.md` for shared gotchas (Atlantis-flow, tf-state bootstrap caution, Pub/Sub audit landing here).

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-platform-prod.md` — canonical sibling seed with full details.
- `~/projects/codebase-map/domains/infrastructure.md`.
