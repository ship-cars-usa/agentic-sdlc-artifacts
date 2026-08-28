---
repo: argo-wf-notificator
path: ~/projects/ship-cars-usa/argo-wf-notificator
stack: Go / Makefile-driven / sends to Slack + GitHub
domain: infrastructure
shape: small Go CLI (58 files)
last-synced-commit: 2da187a2f5991149c6200c124a14e7a52a094366
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# argo-wf-notificator

## What it is
**Argo Workflow Notificator** — Go CLI that sends Argo Workflow status updates to **Slack channels** and **GitHub PRs** (via PR comments and optional GitHub check runs). Concurrent notification dispatch per the README.

Features (per README):
- Slack channel notifications.
- GitHub PR comment updates / additions.
- Optional GitHub check-runs for status visibility.
- Concurrent notification sending.

Has `CHANGELOG.md`, `Makefile`, `VERSIONING.md`, `golangrules.md` — well-versioned tool. Last commit 2026-01-24 — actively maintained on a slow cadence.

## How it fits

- **Drives:** Slack + GitHub notification side-effects from Argo Workflow runs.
- **Pairs with:** `argo` + `argo-wf-finalizer` (the workflow-runtime trio).

## Build / test / run
```
make build
./argo-wf-notificator --workflow <name> --slack-channel ... --github-pr ...
```

## Don't-do-here / gotchas

- **Concurrent send** — care with rate limits on Slack + GitHub. Misconfigured concurrency can blow per-channel rate limits.
- **Credentials** for Slack webhook + GitHub PAT — verify they're injected via env vars / K8s secrets, not hardcoded.
- **Pairs with the rest of the argo* cohort** — coordinate changes to workflow-event semantics with `argo-wf-finalizer`.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/argo.md` — canonical Argo config.
- `~/projects/codebase-map/repos/argo-wf-finalizer.md` — sibling.
- `~/projects/codebase-map/domains/infrastructure.md`.
