---
repo: devops-tf-live-shipcars-sf-lm-uat
path: ~/projects/ship-cars-usa/devops-tf-live-shipcars-sf-lm-uat
stack: Terraform (live env) — `shipcars-sf-lm-uat` GCP project (Salesforce ↔ Loadmate UAT — User Acceptance Testing tier)
domain: infrastructure
shape: live-env IaC (mirrors `-sf-lm-prd`)
last-synced-commit: 808f5c6f6b525988da340bc43f72e1fd7f2e0970
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# devops-tf-live-shipcars-sf-lm-uat

## What it is
**UAT** (User Acceptance Testing) Terraform live-env for Salesforce ↔ Loadmate integration. Last commit 2026-02-06. The UAT tier is **Salesforce-convention** — sits between QA and prod for stakeholder sign-off. See **`devops-tf-live-shipcars-sf-lm-prd.md`** for the canonical description.

## Build / test / run
```
terraform init && terraform plan && terraform apply
```

## Don't-do-here / gotchas
- **UAT-tier is Salesforce-convention.** Unlike `-staging` (technical staging), UAT is stakeholder-facing. Changes here may be seen by business users.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-sf-lm-prd.md` — canonical sibling.
- `~/projects/codebase-map/domains/infrastructure.md`.
