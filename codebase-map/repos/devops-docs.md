---
repo: devops-docs
path: ~/projects/ship-cars-usa/devops-docs
stack: Docs/Markdown
domain: infrastructure
shape: documentation repo (markdown-only)
last-synced-commit: 32718faddf28b1135e606ef33f7c20090fa6c964
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# devops-docs

## What it is
**The DevOps team's technical-documentation repo.** Markdown-only. Per README, the convention is "every document in a dedicated directory with `README.md` as the entry point" — GitHub renders the directory README on directory navigation.

Top-level directories include: `argo/`, `certificate-rotation/`, `env-setup-guide/`, `git-pr-guide/`, `gke-clusters/`, `godaddy-tls-k8s-secret-operations/`, `ip-address-management-guide/`, `jenkins-k8s/`, `k8s_best_practices/`. Covers cluster ops, certificate rotation, TLS / GoDaddy, IP management, GitHub PR guide, Jenkins-K8s, K8s best practices.

Last commit 2025-10-16.

## How it fits

- **Reference documentation** for DevOps operations. Read-mostly.
- **Not deployed.** Just markdown.

## Build / test / run
```
# Markdown only — no build step. Read via GitHub UI or local editor.
```

## Don't-do-here / gotchas

- **Documentation lag.** Markdown docs drift from operational reality. Verify any documented procedure against current cluster state before relying on it.
- **GoDaddy TLS** procedure is a brittle vendor-specific manual flow — read carefully if doing cert rotations.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/devops-helpers.md` — sibling utility-scripts repo.
- `~/projects/codebase-map/repos/knowledge.md` — broader engineering-knowledge repo.
- `~/projects/codebase-map/domains/infrastructure.md`.
