---
repo: devops-tf-live-shipcars-sf-lm-dev
path: ~/projects/ship-cars-usa/devops-tf-live-shipcars-sf-lm-dev
stack: Terraform (live env) — `shipcars-sf-lm-dev` GCP project (Salesforce ↔ Loadmate integration dev)
domain: infrastructure
shape: live-env IaC (mirrors `-sf-lm-prd`)
last-synced-commit: 7933e9db7854453dc4255f60bb0f82bdbb6ab580
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# devops-tf-live-shipcars-sf-lm-dev

## What it is
**Dev** Terraform live-env for Salesforce ↔ Loadmate integration. Same shape as `-sf-lm-prd` / `-qa` / `-uat`. Last commit 2025-11-05.

See **`devops-tf-live-shipcars-sf-lm-prd.md`** for the full description.

## How it fits
- See `devops-tf-live-shipcars-sf-lm-prd.md`.

## Build / test / run
```
terraform init && terraform plan && terraform apply
```

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-sf-lm-prd.md` — canonical sibling.
- `~/projects/codebase-map/domains/infrastructure.md`.
