---
repo: quarkus-user-syncer
path: ~/projects/ship-cars-usa/quarkus-user-syncer
stack: Java 21 / Quarkus 3.27.5 extension (runtime + deployment) — `cars.ship.quarkus.extensions.usersyncer` 3.27.5.1-SNAPSHOT
domain: integrations
shape: multi-module (runtime + deployment + coverage-report)
last-synced-commit: 3fa7b91f51f48ce9770a55794b21db40384495c1
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# quarkus-user-syncer

## What it is
**Quarkus extension library — not a deployed service.** It gives a consuming service the reusable machinery to keep a **local read-model copy of User Management's users and companies** in sync off Pub/Sub events. It ships: Pub/Sub listeners (`UserPubSubListener`, `CompanyPubSubListener`) that implement `quarkus-pubsub`'s `PubSubConsumerBlocking`, abstract sync services with a last-write-wins fence, an `ExternallySynced`/`UserManagementDto` contract the consumer's entities implement, and an optional `UserManagementEventListener` SPI for the consumer to hook extra logic after each sync. This is the extension that underpins the fleet's **`db-syncer` pattern**.

Depends on `quarkus-pubsub` (3.27.5), a persistence extension (`ship.cars.quarkus.extensions.persistence` 3.27.5.1-SNAPSHOT, providing `TransactionalExecution`), and `usermanagement` DTOs 2.8.0 (canonical user/company event DTOs). (Prior sync's 2.0.4 / usermanagement-dtos 2.7.0 versions are stale.)

## How it fits
- **What it provides:** drop-in Pub/Sub consumers + sync services. A consumer constructs a `UserPubSubListener`/`CompanyPubSubListener` with its subscription name, its own `BaseUserManagementSyncService` subclass, and optional `UserManagementEventListener`s; the extension handles the subscribe→convert→transactional-upsert flow.
- **Who consumes it (compile-time):** ~7 fleet repos reference the extension — the `db-syncer` cluster (`notification-orchestrator`, `load-recommender`, `trip-planner`, `saved-search-handler`, and peers). Each keeps its own local `User`/`Company` mirror to avoid a synchronous call to user-management on the hot path.
- **Consumes API of:** Google Cloud Pub/Sub (indirectly, via `quarkus-pubsub`) — subscribes to the user/company event topics published by the user-management side.
- **Publishes events to:** none (consume + persist only).
- **Owns data store:** none itself — it writes into the *consumer's* DB via the consumer-provided `EntityOperationsManager` + persistence extension.

## Build / test / run
```
./mvnw clean install       # builds runtime + deployment; installs to local repo
./deploy-project.sh        # deploy to GitHub Packages
```
Consumed via:
```xml
<dependency>
  <groupId>cars.ship.quarkus.extensions.usersyncer</groupId>
  <artifactId>runtime</artifactId>
  <version>${ship-cars-quarkus-extensions-user-syncer.version}</version>
</dependency>
```
No extension config properties of its own; wiring is done in consumer code (subscription names, sync-service beans).

## Key abstractions
- `UserPubSubListener` / `CompanyPubSubListener` — `runtime/.../infra/` — `PubSubConsumerBlocking` implementations; on each event call `sync(...)` then fan out to the registered `UserManagementEventListener`s.
- `BaseUserManagementSyncService<E extends ExternallySynced, D extends UserManagementDto>` — `runtime/.../service/BaseUserManagementSyncService.java` — the core: runs the upsert in a new transaction (`TransactionalExecution`), **skips the event if it is older than the stored copy** (`shouldSkipUpdate`: `dto.lastModified < entity.externalUpdateTime`), and on a duplicate-key race sleeps 1s and retries once.
- `UserSyncService` / `CompanySyncService` / `UserWithCompanySyncService` — `runtime/.../service/` — concrete sync services.
- `ExternallySynced` — `runtime/.../ExternallySynced.java` — the interface a consumer entity implements (`Instant getExternalUpdateTime()`) so the LWW fence can compare.
- `UserManagementEventListener<T extends EventDto<?>>` — `runtime/.../UserManagementEventListener.java` — SPI for post-sync hooks.
- `EntityOperationsManager` / `DtoToEntityConverter` — `runtime/.../` — consumer-implemented find/persist + DTO→entity mapping.
- DTOs — `runtime/.../dtos/` — `UserAccountEventDto`, `CompanyEventDto`, `EventDto`, `UserAccountDtoWrapper`, `CompanyDtoWrapper`, `UserManagementDto`.
- `PersistenceLoggingFilter` — `runtime/.../config/PersistenceLoggingFilter.java`.
- `UserSyncerExtensionProcessor` — `deployment/.../UserSyncerExtensionProcessor.java`.

## Don't-do-here / gotchas
- **Last-write-wins by `externalUpdateTime`.** `shouldSkipUpdate` silently drops any event whose `lastModified` is before the stored `externalUpdateTime`. A replay/resync that re-emits events with a stale or clock-skewed `lastModified` will be *ignored*, not applied — the same class of LWW divergence documented for the CTMS orders syncer (`syncer_orders_es_version_check`). If a local mirror looks stale after a backfill, suspect this fence first.
- **Duplicate-key handling is a fixed 1s sleep + single retry** (`DEFAULT_SLEEP_MS`). Under a burst of concurrent creates for the same id this can still throw after the one retry; there is no exponential backoff.
- **No idempotency key** — dedup relies entirely on the timestamp fence and the duplicate-key catch (which matches on the Postgres error string `"duplicate key value violates unique constraint"`), so a driver/DB that phrases the error differently would bypass the retry.
- **Contract is implicit / lightly documented** — README is one line. New consumers should copy a working `db-syncer` module (e.g. `notification-orchestrator`) rather than infer the wiring.
- **Schema coupling via `usermanagement` DTOs (2.8.0)** — a breaking DTO change forces every consumer to recompile; treat as a stable public contract.
- **Auto-ACK semantics inherited from `quarkus-pubsub`** — the listeners use `PubSubConsumerBlocking` (no exception ⇒ ACK). A sync that throws NACKs and relies on GCP redelivery + DLQ config on the subscription.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/quarkus-pubsub.md` — the substrate; ACK/NACK + DLQ semantics apply here.
- `~/projects/codebase-map/repos/notification-orchestrator.md` — concrete `db-syncer` consumer / reference wiring.
- memory: `syncer_orders_es_version_check` — the analogous LWW/version-fence divergence pattern.
- `~/projects/codebase-map/domains/integrations.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `CompanyDtoWrapper` | dto | `runtime` | CompanyDtoWrapper |
| `CompanyEventDto` | dto | `runtime` | [Company](../domains/entities/Company.md) |
| `EventDto` | dto | `runtime` | — |
| `UserAccountDtoWrapper` | dto | `runtime` | AccountDtoWrapper |
| `UserAccountEventDto` | dto | `runtime` | [User](../domains/entities/User.md) |
<!-- entities-end -->
