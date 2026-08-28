---
repo: devops-tf-live-shipcars-gcp-projects-access
path: ~/projects/ship-cars-usa/devops-tf-live-shipcars-gcp-projects-access
stack: Terraform (live env) — cross-project IAM access bindings
domain: infrastructure
shape: live-env IaC (91 files) — IAM-only across all Ship.Cars GCP projects
last-synced-commit: 4d4d4f552a6c88bb06d55a7ef3e5203fb2b1c787
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# devops-tf-live-shipcars-gcp-projects-access

## What it is
**Cross-GCP-project IAM access** — Terraform managing which humans + service accounts have which IAM roles across the family of Ship.Cars GCP projects (`shipcars-platform-{dev,qa,staging,prod}`, `shipcars-system-env`, `shipcars-development-env`, `shipcars-production-env`, `shipcars-ml-data-{dev,staging,prod}`, etc.).

**Has a typo'd archive-candidate sibling: `ddevops-tf-live-shipcars-gcp-projects-access`** (double `dd` prefix; per the infrastructure-triage, flagged for archival).

Last commit 2026-04-06.

## How it fits

- **Provisions:** cross-project IAM bindings only — no per-project compute / storage / etc.
- **Pairs with:** the per-project IAM provisioning inside `-platform-prod/live/iam/`, `-system-env/live/iam/`, etc. This repo handles **cross-project** bindings; per-project bindings live in their respective env repos.

## Build / test / run
```
terraform init && terraform plan && terraform apply
```

## Don't-do-here / gotchas

- **IAM blast radius is fleet-wide.** A wrong binding here can grant cross-project access by accident.
- **Typo'd sibling `ddevops-tf-live-shipcars-gcp-projects-access` is archive-candidate** per the infrastructure-triage; ensure nothing references it.

## Relevant ADRs / docs
- `~/projects/codebase-map/relations/infrastructure-triage.md` — flags the typo'd duplicate.
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-platform-prod.md`.
- `~/projects/codebase-map/domains/infrastructure.md`.
