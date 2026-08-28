---
repo: logging-manager
path: ~/projects/ship-cars-usa/logging-manager
stack: Go / standard HTTP server (`net/http`) / logrus / graceful-shutdown pattern
domain: platform
shape: K8s-aware microservice
last-synced-commit: 0e1f36a8fd0cda54f744e00cd6de0f69f76107cb
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# logging-manager

## What it is
**Logging-level admin service for the K8s cluster** — a Go microservice that exposes an HTTP API for **dynamically changing logger levels across Spring + Quarkus services without restarting them**. Both Spring Boot Actuator's `loggers/` endpoint and Quarkus's `q/logging-manager` endpoint expose runtime-mutable log levels; this service brokers calls to those endpoints across all services in the cluster, providing a single admin surface.

Standard Go layout: `api/handlers.go` + `api/router.go` + `cmd/main.go` (with graceful-shutdown pattern listening on SIGINT/SIGTERM and 10s drain) + `internal/{config, logger, services}/`. Has a `Makefile` for build automation.

Last commit 2025-10-10 (Claude-config sweep only) — content is older but the service is part of the operational toolkit.

## How it fits

- **Consumed by:** dev / SRE / on-call engineers via HTTP API or a future UI.
- **Drives:** runtime logger levels on every Spring + Quarkus service in the cluster.
- **Owns data store:** none — stateless broker.

## Build / test / run
```
make build
./logging-manager
```

## Don't-do-here / gotchas

- **Powerful operational tool** — can disable / verbose logging fleet-wide. Authentication is critical; verify before adding cluster-write permissions to the service account.
- **Spring Boot Actuator endpoints are usually internal-only** (port 9090 or admin port). Make sure this service has access to those endpoints across all services.
- **Quarkus logging endpoint is `quarkus-logging-manager`** (the Quarkiverse extension pinned in `shipcars-quarkus-bom`). Every Quarkus service in the fleet automatically exposes it via that BOM dependency.
- **Last real-content commit predates 2026.** Confirm whether the service still works against the current cluster configuration.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/shipcars-quarkus-bom.md` — pins `quarkus-logging-manager` Quarkiverse extension that this service drives.
- `~/projects/codebase-map/repos/spring-commons.md` — Spring Boot Actuator wiring on the Spring side.
- `~/projects/codebase-map/domains/platform.md`.
