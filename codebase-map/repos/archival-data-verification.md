---
repo: archival-data-verification
path: ~/projects/ship-cars-usa/archival-data-verification
stack: Go / standard HTTP server / logrus / graceful-shutdown pattern
domain: platform
shape: small Go microservice (api/ + cmd/ + configs/ + internal/)
last-synced-commit: 4a47d7d9dcf7b9fa3349e69e61ae18ce48f81a61
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# archival-data-verification

## What it is
**Archival Data Verification Tool** (per README) — a Go service that **compares records across source + target databases** to verify data consistency during archival / migration moves. Provides a RESTful API for triggering verifications and querying status, with support for multiple labeled source databases (per the README: `PUSHER`, `USER`, `TARGET`).

Standard small-Go-service layout matching `logging-manager`'s shape: `cmd/main.go` (graceful-shutdown / SIGTERM handling), `api/` (handlers + router), `internal/{config, database, server}/`, `configs/`. Has a `Makefile`.

Pairs with the broader `archival-service` / `archiver` Quarkus services. Last commit 2025-10-10 (Claude-config sweep only).

## How it fits

- **Consumes:** source databases (configured per `PUSHER`, `USER`, etc.) + target database.
- **API:** RESTful verification + status endpoints (per README features: "RESTful API for data verification and status checking", "Table-level verification", "Transfer state history tracking").
- **Owns data store:** none for verification; presumably owns a small audit table for transfer-state-history.

## Build / test / run
```
make build
./archival-data-verification
```

## Don't-do-here / gotchas

- **Pairs with `archival-service` / `archiver`** — the verifier supplements the mover. Pair-failure consideration: if archival fails but verification reports OK (or vice versa), the data is in a confused state.
- **Multiple source DBs.** `PUSHER` (the Quarkus router service's PG), `USER` (`user-backend`'s PG), `TARGET` (the archival sink). Adding a new source = code + config change.
- **Low-touch operational tool.** Last real content predates 2026; verify it still runs against current schemas.
- **Same Go-service template** as `logging-manager` — graceful shutdown, logrus, simple HTTP API.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/archival-service.md` — the Quarkus archival mover (stub).
- `~/projects/codebase-map/repos/archiver.md` — the Quarkus 2.9.1.Final EOL archiver (stub).
- `~/projects/codebase-map/repos/pusher.md` — owner of the `PUSHER` source DB.
- `~/projects/codebase-map/repos/user-backend.md` — owner of the `USER` source DB.
- `~/projects/codebase-map/domains/platform.md`.
