---
repo: devops-tf-live-shipcars-development-env
path: ~/projects/ship-cars-usa/devops-tf-live-shipcars-development-env
stack: Terraform (live env) — older `shipcars-development-env` GCP project (combined dev+qa)
domain: infrastructure
shape: live-env IaC with paired dev+qa categories
last-synced-commit: 65ae5c90d78befacc2aace57f108cf5026cf5670
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# devops-tf-live-shipcars-development-env

## What it is
**Older "combined dev+qa" Terraform live-env** for the legacy `shipcars-development-env` GCP project, predating the per-env split (`-platform-dev` / `-platform-qa`). Per `live/` layout: paired categories like `databases-dev/` + `databases-qa/`, `media-dev/` + `media-qa/`, `messaging-dev/` + `messaging-qa/`, plus shared `gke/`, `iam/`, `iap/`, `cloudfunctions/`, `persistent-disks/`, `tf-state/`.

Last commit 2025-08-19 — older than the per-env repos but still maintained.

## How it fits

- **Predecessor / coexists with:** `-platform-dev`, `-platform-qa`. Likely some resources still live here while others have migrated.
- **Provisions:** combined dev+qa resources for legacy services.

## Build / test / run
```
cd live/<category>
terraform init && terraform plan && terraform apply
```

## Don't-do-here / gotchas

- **Older / split-style.** Coordinate with `-platform-dev` / `-platform-qa` to avoid duplicate provisioning.
- **Confirm which env each `live/<category>` actually serves** before assuming the naming is current.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-platform-dev.md` / `-qa.md` — modern split.
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-platform-prod.md` — canonical sibling seed.
- `~/projects/codebase-map/domains/infrastructure.md`.
