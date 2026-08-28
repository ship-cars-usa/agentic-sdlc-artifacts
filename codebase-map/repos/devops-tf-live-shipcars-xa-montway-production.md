---
repo: devops-tf-live-shipcars-xa-montway-production
path: ~/projects/ship-cars-usa/devops-tf-live-shipcars-xa-montway-production
stack: Terraform (live env) — Montway-branded production GCP project ("xa" likely = "cross-account" / external partner namespace)
domain: infrastructure
shape: live-env IaC (32 files: cloudfunctions / gke / iam / keep / messaging / tf-state)
last-synced-commit: 0d03c5a4bade6d66996f026612b1cdbdfe95e97f
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# devops-tf-live-shipcars-xa-montway-production

## What it is
**Montway-branded production infrastructure** — Terraform live-env for a separate GCP project hosting Montway-specific production resources. Smaller scope than `-platform-prod` (32 files; just `cloudfunctions/gke/iam/keep/messaging/tf-state/`). Pairs with the Montway-customer-token usage in `home-delivery-backend` + the Montway-specific `asg-checkout-spa`.

Last commit 2025-07-14 — slow cadence.

## How it fits

- **Provisions:** Montway production-side resources separately from the main Ship.Cars platform.
- **Pairs with:** `home-delivery-backend` + `asg-checkout-spa` (Montway-customer-facing services).

## Build / test / run
```
terraform init && terraform plan && terraform apply
```

## Don't-do-here / gotchas

- **Montway partner-specific.** Coordinate changes with whoever owns the Montway relationship.
- **Separate GCP project** — credentials / state are isolated from `-platform-prod`.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/home-delivery-backend.md` — Montway-facing dealer widget.
- `~/projects/codebase-map/repos/asg-checkout-spa.md` — Montway Checkout SPA.
- `~/projects/codebase-map/domains/infrastructure.md`.
