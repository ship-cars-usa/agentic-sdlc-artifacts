---
repo: company-cleanup-utils
path: ~/projects/ship-cars-usa/company-cleanup-utils
stack: Java/Quarkus 3.15.2 / Maven multi-module / templated from `quarkus-imperative-boilerplate`
domain: platform
shape: multi-module Quarkus utility service
last-synced-commit: 60794d359a46e0df90effbad567b4e9e51773887
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# company-cleanup-utils

## What it is
**Company Cleanup Utils** — Quarkus service for **cleanup of test data** (per the README: "do cleanup of all data used in testing"). Used in dev / qa / staging environments to wipe test companies / users / loads / etc. created during automated testing runs.

Quarkus 3.15.2 per the version-matrix (older Quarkus minor cohort). Templated from `quarkus-imperative-boilerplate`. Multi-module standard layout. Native-buildable.

Last commit 2025-10-10 (Claude config sweep only) — content older.

## How it fits

- **Consumes:** likely the source-of-truth backends (`user-backend` to identify test companies; `posting-backend` / `inventory-backend` / etc. to delete their data).
- **Destructive operation.** Deletes data across multiple services.
- **Owns data store:** likely a small Postgres for tracking cleanup-run state.

## Build / test / run
```
./start-quarkus-dev.sh
./mvnw clean install -Pnative
```

## Don't-do-here / gotchas

- **NEVER deploy / run against production.** The whole point is data deletion; a misconfigured target = catastrophic data loss. Verify environment guards at every entry point.
- **Test-data-identification heuristic** — likely by company name prefix, email pattern, or a flag. A change to the test-data convention upstream must coordinate with this service.
- **Cross-service deletion = transactional impossibility.** This service's cleanup is best-effort; partial cleanups can leave stale data in some services and clean in others. The on-call story is "if dev/qa has orphaned data, run this service again."
- **Quarkus 3.15.2** — older cohort. Bump to current per the version-matrix recommendations when convenient.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/quarkus-imperative-boilerplate.md` — template.
- `~/projects/codebase-map/repos/user-backend.md` — primary upstream.
- `~/projects/codebase-map/relations/quarkus-version-matrix.md` — version drift context.
- `~/projects/codebase-map/domains/platform.md`.
