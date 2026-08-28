---
repo: archival-service
path: ~/projects/ship-cars-usa/archival-service
stack: Java/Quarkus 3.15.2 / Maven multi-module (11 poms) / templated from `quarkus-imperative-boilerplate`
domain: platform
shape: multi-module Quarkus service (with `Dockerfile-migrate` → has Flyway migrations)
last-synced-commit: 401d9c48844951f25d9c0134a2b3e0f81374d7ff
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# archival-service

## What it is
**Archival Service** — modern Quarkus 3.15.2 service for moving aged data from active service Postgres DBs to an archival store. Successor / sibling to the much older `archiver` (Quarkus 2.9.1.Final). Pairs with `archival-data-verification` (Go) which verifies the moves were correct.

Templated from `quarkus-imperative-boilerplate`. Multi-module (11 poms — slightly larger than the standard 9 from the template, may have added archival-specific modules).

Last commit 2025-10-10 (Claude-config sweep only) — content older.

## How it fits

- **Consumes:** the source databases of services whose data is being archived (likely identified by row age or status).
- **Writes to:** an archival store (BigQuery? GCS? Specific archive Postgres? Confirm against `application.properties`).
- **Pairs with:**
  - `archiver` — older Quarkus 2.9.1.Final sibling; likely the legacy implementation being migrated to this newer service.
  - `archival-data-verification` — Go verifier that compares source vs archived records.

## Build / test / run
```
./start-quarkus-dev.sh
./mvnw clean install -Pnative
```

## Don't-do-here / gotchas

- **Two archival services in the fleet** — `archival-service` (Quarkus 3.15.2, this one) and `archiver` (Quarkus 2.9.1.Final, the major-version-laggard). The split is probably "newer is migrating off the older." Confirm which is canonical for which data path before changing either.
- **Destructive operation** — moving data permanently from source to archive. Misconfiguration = data loss. Verify retention policy + source-deletion logic.
- **Quarkus 3.15.2** — older cohort; bump-eligible per the version-matrix.
- **`Dockerfile-migrate` present** → has Flyway-managed schema. Deploy as separate K8s Job (standard fleet pattern).

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/archiver.md` — older Quarkus 2.9.1.Final sibling.
- `~/projects/codebase-map/repos/archival-data-verification.md` — Go verifier companion.
- `~/projects/codebase-map/repos/quarkus-imperative-boilerplate.md` — template.
- `~/projects/codebase-map/relations/quarkus-version-matrix.md`.
- `~/projects/codebase-map/domains/platform.md`.
