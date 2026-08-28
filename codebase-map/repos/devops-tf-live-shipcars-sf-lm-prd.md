---
repo: devops-tf-live-shipcars-sf-lm-prd
path: ~/projects/ship-cars-usa/devops-tf-live-shipcars-sf-lm-prd
stack: Terraform (live env) — `shipcars-sf-lm-prd` GCP project (likely Salesforce ↔ Loadmate integration prod)
domain: infrastructure
shape: live-env IaC (`apis/iam/messaging/monitoring/sm/tf-state/`)
last-synced-commit: 3eff8c6c014f9e626ca206020ffd213320d536d5
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# devops-tf-live-shipcars-sf-lm-prd

## What it is
**Production** Terraform live-env for `shipcars-sf-lm-prd` GCP project. The "sf-lm" prefix likely = **Salesforce ↔ Loadmate integration** — a Pub/Sub-driven bridge between Ship.Cars's operational systems and Salesforce CRM. Lean shape (6 categories: APIs, IAM, Pub/Sub messaging, monitoring, Secret Manager, tf-state). No GKE / Cloud SQL — implies the integration runs as Cloud Functions or via cross-project Pub/Sub rather than dedicated services.

Last commit 2026-01-28.

## How it fits

- **Provisions:** Salesforce ↔ Loadmate integration production resources (Pub/Sub topics, IAM, secrets).
- **Pairs with sibling envs:** `-sf-lm-dev`, `-sf-lm-qa`, `-sf-lm-uat`. Four-env progression (dev → qa → uat → prd) instead of the platform side's three (dev → qa → staging → prod).
- **Possible relationship to `crm-workflows`** (the Quarkus Freshsales sync service) — though Freshsales ≠ Salesforce, they're both CRM systems.

## Build / test / run
```
terraform init && terraform plan && terraform apply
```

## Don't-do-here / gotchas

- **Production state.** Same caution as other prod live-envs.
- **4-env progression (dev/qa/uat/prd)** — unusual in the fleet, which mostly uses dev/qa/staging/prod. The `uat` env is Salesforce-convention.
- **Pub/Sub-heavy** — coordinate `messaging/` changes with downstream consumers.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-sf-lm-dev.md` / `-qa.md` / `-uat.md` — sibling envs.
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-platform-prod.md` — canonical sibling pattern.
- `~/projects/codebase-map/domains/infrastructure.md`.
