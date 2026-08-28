---
repo: devops-tf-live-shipcars-sf-lm-qa
path: ~/projects/ship-cars-usa/devops-tf-live-shipcars-sf-lm-qa
stack: Terraform (live env) — `shipcars-sf-lm-qa` GCP project (Salesforce ↔ Loadmate QA)
domain: infrastructure
shape: live-env IaC (mirrors `-sf-lm-prd`)
last-synced-commit: 9af99651d5fc87497f01834890314f13ee3ad5d2
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# devops-tf-live-shipcars-sf-lm-qa

## What it is
**QA** Terraform live-env for Salesforce ↔ Loadmate integration. Last commit 2026-02-06. See **`devops-tf-live-shipcars-sf-lm-prd.md`** for the canonical description.

## Build / test / run
```
terraform init && terraform plan && terraform apply
```

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-sf-lm-prd.md` — canonical sibling.
- `~/projects/codebase-map/domains/infrastructure.md`.
