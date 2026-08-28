---
repo: docker-utils
path: ~/projects/ship-cars-usa/docker-utils
stack: Dockerfile base images (`argo-wf/`, `atlantis/`, `build-fe-docker-base/`, `builder-docker-base/`, `builder-native-docker-base/`, `builder-quarkus-not-native-docker-base/`, `builder-spring-app-docker-base/`, `flyway-docker-base/`)
domain: infrastructure
shape: monorepo of Dockerfile base images (145 files)
last-synced-commit: 80d5ca64379bc5989b044df21cfd9c2719a1d931
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# docker-utils

## What it is
**The fleet's central Dockerfile base-image repo.** Hosts the base Docker images that every fleet service's `Dockerfile` extends. Subdirectories: `argo-wf/`, `atlantis/`, `build-fe-docker-base/`, `builder-docker-base/`, `builder-native-docker-base/` (for Quarkus native builds via Mandrel), `builder-quarkus-not-native-docker-base/` (for Quarkus JVM builds), `builder-spring-app-docker-base/`, `flyway-docker-base/` (for the per-service `Dockerfile-migrate` pattern).

Last commit 2026-02-17.

## How it fits

- **Provides:** the base images that per-service `Dockerfile` files reference (`FROM us-central1-docker.pkg.dev/shipcars-system-env/shipcars/<base-image>`).
- **Pairs with:** `helm` (the consuming chart monorepo) + `devops-tf-live-shipcars-system-env/live/repositories/` (the OCI registry provisioning).
- **Cache-busting** these base images triggers rebuilds across the fleet — careful with bumps.

## Build / test / run
```
cd <base-name>
docker build -t shipcars/<base-name>:<version> .
docker push us-central1-docker.pkg.dev/shipcars-system-env/shipcars/<base-name>:<version>
```

## Don't-do-here / gotchas

- **Base-image bumps cascade.** Every service's Docker build re-runs when its base updates. CI duration can balloon if multiple base images change in the same window.
- **`flyway-docker-base`** is the canonical migrate-image base; pairs with the per-service `Dockerfile-migrate` pattern.
- **`builder-native-docker-base`** uses GraalVM Mandrel (per `shipcars-quarkus-bom`'s `quarkus.native.builder-image=quay.io/quarkus/ubi-quarkus-mandrel-builder-image:23.1.8.0-Final-java21`).
- **Argo-wf base** — for Argo Workflows step containers.
- **`atlantis/`** — the Atlantis service runs from this base (PR-based Terraform applies).

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/helm.md` — consumer.
- `~/projects/codebase-map/repos/shipcars-quarkus-bom.md` — references the Mandrel native-builder version that lives here.
- `~/projects/codebase-map/repos/quarkus-imperative-boilerplate.md` / `quarkus-k8s-boilerplate.md` — templates that reference these base images.
- `~/projects/codebase-map/domains/infrastructure.md`.
