---
repo: jenkins-master-system-env
path: ~/projects/ship-cars-usa/jenkins-master-system-env
stack: Jenkins master config (`Dockerfile` + `audit-trail.xml` + `jobConfigHistory.xml` + `plugins.txt`)
domain: infrastructure
shape: Jenkins-master containerized config (8 files)
last-synced-commit: d4adb07a7a55cbe15ae812387e540d273874fa8e
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# jenkins-master-system-env

## What it is
**Jenkins-master container configuration** for the Ship.Cars Jenkins server (the CI orchestrator for the fleet — Quarkus services, automation tests, mobile builds all reference Jenkins). Contains:

- `Dockerfile` — builds the Jenkins master image.
- `plugins.txt` — pinned Jenkins plugin list.
- `audit-trail.xml` — audit trail plugin config (who triggered what).
- `jobConfigHistory.xml` — job-config-history plugin config (versioned job changes).

Pairs with `devops-tf-live-shipcars-system-env/live/jenkins/` which provisions the Jenkins-server infrastructure (VM / GKE node / persistent volumes / DNS / TLS).

Last commit 2025-03-28 — older than most active infra repos but still maintained.

## How it fits

- **Produces:** the Jenkins-master Docker image deployed by the system-env Terraform.
- **Pairs with:** `devops-tf-live-shipcars-system-env/live/jenkins/`.
- **Drives:** every Jenkinsfile-based CI pipeline in the fleet (`automation/Jenkinsfile.groovy`, `automation-epod-github-actions-test/Jenkinsfile.groovy`, `ml-model-training/Jenkinsfile`, `platform-backend/Jenkinsfile-test.groovy`, `archiver/.../Jenkinsfile`, `argo-stresstests`, etc.).

## Build / test / run
```
docker build -t shipcars/jenkins-master .
docker run shipcars/jenkins-master
```

## Don't-do-here / gotchas

- **Plugin updates** can break running pipelines if plugin compatibility shifts. Bump conservatively.
- **`plugins.txt` is the source of truth** — adding a plugin via the Jenkins UI doesn't persist across container restarts unless added here.
- **`audit-trail.xml` is security-relevant** — verify it's not disabled by accident.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/devops-tf-live-shipcars-system-env.md` — pairs with `live/jenkins/`.
- `~/projects/codebase-map/repos/automation.md` — primary Jenkins-driven CI surface.
- `~/projects/codebase-map/domains/infrastructure.md`.
