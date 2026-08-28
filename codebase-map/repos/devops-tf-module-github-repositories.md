---
repo: devops-tf-module-github-repositories
path: ~/projects/ship-cars-usa/devops-tf-module-github-repositories
stack: Terraform module — GitHub repos managed via the `integrations/github` Terraform provider (with Node-based helper scripts)
domain: infrastructure
shape: reusable Terraform module (47 files; has `package.json` for helper scripts)
last-synced-commit: e3c5b9a96b8895f42f948b01eb61b651a5bb8b7d
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# devops-tf-module-github-repositories

## What it is
**Reusable Terraform module for managing GitHub repositories as code** — manages repo settings (visibility, default branch, branch protection rules, collaborators, webhooks, etc.) for the Ship.Cars GitHub org via Terraform. Has Node-based helper scripts (`package.json`) for ergonomic configuration.

Pairs with `devops-tf-live-shipcars-system-env/live/repositories/` which is the live-env consumer of this module.

**Has a typo'd archive-candidate sibling**: `devops-tf-module-githuib-repositories` (`githuib` typo). Per infrastructure-triage, the typo'd version is flagged archive-candidate.

Last commit 2025-08-12.

## How it fits

- **Consumed by:** `devops-tf-live-shipcars-system-env/live/repositories/`.
- **Manages:** the GitHub repo settings for all 232 Ship.Cars repos (via the GitHub Terraform provider).
- **Helper scripts** (Node-based, `package.json`) probably translate spreadsheet / YAML config into Terraform variables.

## Build / test / run
```
npm install   # for helper scripts
# In consuming live-env:
terraform init && terraform plan && terraform apply
```

## Don't-do-here / gotchas

- **GitHub repo modifications are partly visible to outsiders** (visibility, default branch) and partly invisible (branch protection rules). A wrong setting can either leak code or block deploys.
- **`terraform destroy` here can delete GitHub repos.** Treat as the highest-blast-radius module in the catalog.
- **Coordinate with the typo'd sibling** (`devops-tf-module-githuib-repositories`) — ensure no consumer accidentally pins to the typo. Archive the typo'd repo to remove the ambiguity.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-system-env.md` — consumer.
- `~/projects/codebase-map/relations/infrastructure-triage.md` — typo'd sibling flagged.
- `~/projects/codebase-map/domains/infrastructure.md`.
