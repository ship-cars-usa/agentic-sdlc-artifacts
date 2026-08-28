---
repo: devops-tf-live-shipcars-platform-staging
path: ~/projects/ship-cars-usa/devops-tf-live-shipcars-platform-staging
stack: Terraform (live env) — `shipcars-platform-staging` GCP project (auto-classifier misread it as Docs because of mixed `.tf` + `.md` files)
domain: infrastructure
shape: live-env IaC (largest in the `platform-*` cohort: 308 files)
last-synced-commit: b93d990ca6b0c8631a8bd5181cc5c3e241c72e96
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# devops-tf-live-shipcars-platform-staging

## What it is
**Staging-environment Terraform live-env IaC** for `shipcars-platform-staging`. Largest of the `platform-*` cohort (308 files) — staging typically replicates production-scale infrastructure for full integration testing.

Mirrors `-dev` / `-qa` / `-prod` structurally. Last commit 2026-04-15 — actively maintained.

## How it fits

- **Provisions:** staging GCP-side resources, scaled close to production specs.
- **Validation tier:** the final tier before prod. Changes that pass staging usually proceed to prod.
- See **`devops-tf-live-shipcars-platform-prod.md`** for full breakdown + shared gotchas.

## Build / test / run
```
cd live/<category>
terraform init && terraform plan && terraform apply
```

## Don't-do-here / gotchas

- **Staging is the last validation tier.** Failures here block prod promotion. Coordinate with QA.
- **308 files** — largest live-env repo by file count. Use targeted paths for grep / read operations.
- See `devops-tf-live-shipcars-platform-prod.md` for shared caveats.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-platform-prod.md`.
- `~/projects/codebase-map/domains/infrastructure.md`.
