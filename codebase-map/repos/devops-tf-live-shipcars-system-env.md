---
repo: devops-tf-live-shipcars-system-env
path: ~/projects/ship-cars-usa/devops-tf-live-shipcars-system-env
stack: Terraform (live env) — `shipcars-system-env` GCP project (system/shared resources)
domain: infrastructure
shape: live-env IaC (system/cross-env resources: cert authority, DNS, Cloudflare, Jenkins, OpenVPN connectors, SSL, repositories)
last-synced-commit: 937930febebbe533501947900064f08e41fb4c24
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# devops-tf-live-shipcars-system-env

## What it is
**Cross-environment system-level infrastructure** for the `shipcars-system-env` GCP project — resources shared across dev/qa/staging/prod rather than tied to a single env. 17 resource categories:

- `buckets/`, `cloudfunctions/`, `cloudsql/`, `gke/`, `iam/`, `redis/`, `tf-state/` — same shapes as `-platform-*`.
- `certificate-authority/` — internal CA for TLS certs.
- `clouddns/` + `dns/` — DNS records.
- `cloudflare/` — Cloudflare integration (DNS, WAF, CDN).
- `jenkins/` — Jenkins-master Terraform setup (companion to `jenkins-master-system-env` repo).
- `messaging/` — system-wide Pub/Sub / messaging.
- `network/` — VPC / subnets / firewalls.
- `openvpn-connectors/` — VPN connectivity.
- `repositories/` — GitHub repos managed via Terraform (likely uses `devops-tf-module-github-repositories`).
- `ssl/` — SSL cert provisioning.

Last commit 2026-04-28 — actively maintained.

## How it fits

- **Provisions:** everything that doesn't live in a single env — TLS, DNS, networking, Jenkins, the GitHub Artifact Registry containers Helm charts publish to (`oci://us-central1-docker.pkg.dev/shipcars-system-env/shipcars`).
- **Sibling envs:** `-platform-{dev,qa,staging,prod}`, `-production-env`, `-development-env`, `-xa-montway-production`, the 4 `-sf-lm-*`, `-atlantean-field-175514`, `-gcp-projects-access`.
- **OCI registry path** `us-central1-docker.pkg.dev/shipcars-system-env/shipcars` is provisioned here — referenced by `helm-common-chart` and the per-service Helm charts.

## Build / test / run
```
cd live/<category>
terraform init && terraform plan && terraform apply
```

## Don't-do-here / gotchas

- **System-wide blast radius.** A misconfigured DNS / Cloudflare / SSL change affects every env. Even more dangerous than per-env changes.
- **Pairs with `jenkins-master-system-env`** for the Jenkins-master container build/config.
- **`repositories/`** — Terraform-managed GitHub repos. A `terraform destroy` here can delete repos. Extreme caution.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-platform-prod.md` — sibling.
- `~/projects/codebase-map/repos/jenkins-master-system-env.md` — pairs with `live/jenkins/`.
- `~/projects/codebase-map/repos/devops-tf-module-github-repositories.md` — consumed by `live/repositories/`.
- `~/projects/codebase-map/repos/helm-common-chart.md` — published to the OCI registry provisioned here.
- `~/projects/codebase-map/domains/infrastructure.md`.
