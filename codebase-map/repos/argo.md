---
repo: argo
path: ~/projects/ship-cars-usa/argo
stack: Helm charts / Argo CD + Argo Workflows + Argo Events config
domain: infrastructure
shape: argo/ + charts/ + misc/ (195 files)
last-synced-commit: bec1e1dce9deaf688311fd2df7fead1795e03d24
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# argo

## What it is
**Argo CD / Argo Workflows / Argo Events config + Helm charts** for the Ship.Cars K8s cluster. Includes the `argo/charts/platform/templates/sensor-github-common-cd-*.yaml` files referenced earlier (in the `socket-server-old` probe — Argo Events sensors that listen for GitHub events and trigger CD pipelines).

The repo manages:
- **Argo CD** — GitOps continuous deployment, syncing `helm/` repo state into K8s clusters.
- **Argo Workflows** — pipeline-style CI/CD jobs (build, test, deploy).
- **Argo Events** — event-driven triggers (GitHub PR events, webhooks, etc.) that kick off Workflows.

Last commit 2026-04-15 (~23 days ago at sync time). Actively maintained.

## How it fits

- **Drives:** every fleet service's GitOps deploy via Argo CD watching `helm/` repo state.
- **Pairs with:**
  - **`helm`** — the source-of-truth Helm-chart repo Argo CD syncs from.
  - **`argo-stresstests`** — Argo CD stress-test repo (sibling, also Helm chart, 717-day-stale per triage).
  - **`argo-wf-finalizer`** — Go service that finalizes Argo Workflow runs (cleanup hooks).
  - **`argo-wf-notificator`** — Go CLI sending workflow status to Slack + GitHub.
- **Owns:** Argo CD `Application` definitions, Argo Workflows templates, Argo Events sensors.

## Build / test / run
```
helm lint argo/
helm template argo/
# Argo CD: applied via cluster admin path
```

## Don't-do-here / gotchas

- **Argo CD has cluster-wide write access** — misconfigured Application + auto-sync can re-create deleted resources or roll back manual changes. Tread carefully.
- **GitHub-event-triggered Workflows** — a malicious or accidental PR can trigger CD pipelines. Verify Argo Events signature validation.
- **Pairs with `helm`** as the authoritative GitOps source. Don't make K8s-state changes outside this pair.
- **`argo-stresstests`** sibling is older (last commit 2024-05-20) — verify whether it's actively used or archive-candidate.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/argo-stresstests.md` — sibling.
- `~/projects/codebase-map/repos/argo-wf-finalizer.md` — Go finalizer.
- `~/projects/codebase-map/repos/argo-wf-notificator.md` — Go notificator.
- `~/projects/codebase-map/repos/helm.md` — GitOps source.
- `~/projects/codebase-map/domains/infrastructure.md`.
