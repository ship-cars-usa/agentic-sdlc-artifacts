---
repo: quarkus-data-migration
path: ~/projects/ship-cars-usa/quarkus-data-migration
stack: Java/Quarkus extension (runtime + deployment) — `ship.cars.quarkus.extensions.data-migration:quarkus-data-migration` 3.27.5 (on shipcars-quarkus-bom / Quarkus 3.27.5), JTA + Hibernate ORM
domain: platform
shape: multi-module (runtime + deployment + coverage-report)
last-synced-commit: 6cba94762ba0420eb35d0a80afcc03ecbf026746
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# quarkus-data-migration

## What it is
A **code-based data-migration framework** that runs Java migrations automatically at Quarkus startup. It is **not** schema tooling — there is no Liquibase, no Flyway, no bundled JDBC driver, and no DDL generation. It complements schema migration by running application-level data transforms (with full CDI + Hibernate ORM **Panache** access) exactly once each, tracked in a per-service version table. Java package is `ship.cars.quarkus.extensions.datamigration.*` (note: `datamigration`, one word).

How a consumer uses it: define migration classes that extend `DataMigrationBase`, implementing `getVersion()` (unique ascending `int`) + `doDataMigrate()` (the transform body). On the Quarkus `StartupEvent`, `DataMigrationStarter` (if enabled) calls `DataMigrationServiceImpl.executeDataMigration()`, which discovers all `DataMigration` CDI beans, orders them by version ascending, runs each one not already recorded, and records completion (`"V"+version`) in the `data_migration_versions` table.

Public API:

- **`DataMigration`** — SPI interface: `getVersion()` + `execute()`.
- **`DataMigrationBase`** — abstract base consumers extend; wraps `doDataMigrate()` with timing/logging.
- **`DataMigrationService` / `DataMigrationServiceImpl`** — orchestrator: discover `DataMigration` beans → sort by version → run each un-recorded one → mark done.
- **`DataMigrationStarter`** — CDI observer of `StartupEvent`; triggers execution when `execution-enabled` is true.
- **`DataMigrationInProgressService`** — exposes `inProgress()` so a service can gate readiness/consumers until migrations finish. **NOT** a cross-replica lock (no ShedLock, no row lock) — just an in-JVM "am I still migrating" flag.
- **`DataMigrationVersionEntity` + `DataMigrationVersionRepository`** — Panache-backed record of which versions have run. Maps table **`data_migration_versions`** (`version` PK String, `migrated_at` Instant). **The consumer must pre-create this table** (README ships the DDL); the extension does not create it.
- **`DataMigrationConfig`** — `@ConfigMapping(prefix = "quarkus.data.migration")`, `@ConfigRoot(RUN_TIME)`; single property `execution-enabled` (boolean, default `true`).

The JavaDoc URL is public: `https://ship-cars-usa.github.io/quarkus-data-migration/javadoc/` (per README).

## How it fits

- **Compile-time consumers (verified 2026-08-28):** **`contract-pricing-backend`** is the only real consumer of this Quarkus extension — its `services/pom.xml` declares `ship.cars.quarkus.extensions.data-migration`, and it has `V1DataMigration`/`V2DataMigration` extending the extension's `DataMigrationBase`. (`crm-workflows` has only a leftover `%test.quarkus.data-migration.execution-enabled=false` config line with no pom dep and no usage — a copied remnant, not a consumer.)
- **Important — a separate Spring twin does the heavy lifting fleet-wide.** ~34 migration classes across `driveaway-backend`, `inventory-backend`, `public-tracking-backend`, `user-backend`, `notification-backend`, `posting-backend`, `quote-manager-backend`, `chat-backend`, etc. extend `cars.ship.commons.spring.datamigration.impl.DataMigrationBase` from `spring-commons/spring-data-migration` — **not** this Quarkus extension. So the earlier "no active consumers" note was wrong on both counts: this extension has one Quarkus consumer, and the pattern it implements is heavily used via the Spring sibling.
- **Consumes API of:** none — pure library (on Hibernate ORM Panache).
- **Publishes events to:** none.
- **Owns data store:** each consumer owns its own `data_migration_versions` table (must be pre-created).

## Build / test / run
```
./mvnw clean install -DskipTests
./mvnw test
./build-project.sh
./deploy-project.sh
```

Consumed via:
```xml
<dependency>
  <groupId>ship.cars.quarkus.extensions.data-migration</groupId>
  <artifactId>runtime</artifactId>
  <version>${shipcars-quarkus-data-migration.version}</version>
</dependency>
```

Then extend `DataMigrationBase` per migration and register it as a CDI bean:

```java
@ApplicationScoped
public class V1DataMigration extends DataMigrationBase {
  @Override public int getVersion() { return 1; }
  @Override public void doDataMigrate() { /* typed work over Panache entities */ }
}
```

Also pre-create the tracking table (README DDL) — the extension does not create it:

```sql
CREATE TABLE data_migration_versions (version VARCHAR PRIMARY KEY, migrated_at TIMESTAMP);
```

Disable at startup with `quarkus.data.migration.execution-enabled=false` (note the **dotted** prefix — see gotchas).

## Key abstractions

All under `runtime/src/main/java/ship/cars/quarkus/extensions/datamigration/runtime/`:

- **`DataMigration.java`** — SPI interface (`getVersion()` + `execute()`).
- **`impl/DataMigrationBase.java`** — abstract base consumers extend (`getVersion()` + `doDataMigrate()`); wraps the body with timing/logging.
- **`DataMigrationService.java`** + **`impl/DataMigrationServiceImpl.java`** — orchestrator: discover `DataMigration` beans → dedupe/sort by version → run each un-recorded one → `markMigrated`.
- **`impl/DataMigrationStarter.java`** — CDI `StartupEvent` observer; triggers execution when `execution-enabled()`.
- **`DataMigrationInProgressService.java`** — `inProgress()` readiness flag (in-JVM; **not** a cross-replica lock).
- **`entities/DataMigrationVersionEntity.java`** + **`impl/DataMigrationVersionRepository.java`** — Panache repo/entity for the `data_migration_versions` table; `existsById(version)`, `@Transactional markMigrated(version)`.
- **`config/DataMigrationConfig.java`** — `@ConfigMapping(prefix="quarkus.data.migration")` `@ConfigRoot(RUN_TIME)`; `execution-enabled` (default true).
- **`deployment/.../DataMigrationExtensionProcessor.java`** — build step registering feature `data-migration-extension`.

## Don't-do-here / gotchas

- **Latent config-prefix bug.** The `@ConfigMapping` prefix is `quarkus.data.migration` (dotted) → property `quarkus.data.migration.execution-enabled`. But consumers write the **hyphenated** `quarkus.data-migration.execution-enabled` (`contract-pricing-backend/.../application.properties:150`, `crm-workflows/.../application.properties:131`). The hyphen form does **not** match the mapping, so those `%test` overrides likely do NOT actually disable migrations. Use the dotted form.
- **NO cross-replica locking.** `DataMigrationInProgressService` is an in-JVM readiness flag, not ShedLock or a row lock. On a multi-replica rollout, every pod runs `executeDataMigration()` concurrently at startup. Safety rests only on the `data_migration_versions` PK: two pods running the same version race on `markMigrated` (one gets a duplicate-key error) and the `doDataMigrate()` bodies can both execute. Make migration bodies idempotent; don't assume single-runner semantics.
- **Not idempotent end-to-end.** `markMigrated` is `@Transactional`, but the `doDataMigrate()` body is not wrapped in the same transaction. If the body succeeds but marking fails, the migration re-runs on the next boot.
- **Distinct from Flyway/Liquibase.** This runs Java data transforms at startup; it does no DDL and ships no schema tooling. They're complementary, not substitutes.
- **Consumer must pre-create the `data_migration_versions` table** (README DDL) — the extension does not create it. Missing table → startup failure.
- **Duplicate/failing versions fail the boot.** A duplicate `getVersion()` throws `RuntimeException("Multiple versions found for version N")`; any exception in `doDataMigrate()` propagates out of the `StartupEvent` observer and aborts application startup (fail-fast). No rollback of prior migrations in the batch.
- **Migrations run at startup and delay pod-ready.** A slow migration delays readiness → affects rolling deploys. Long-running transforms belong in background jobs, not startup migrations.
- **No rollback / down-migration.** Rolling back means writing a new forward migration that undoes the prior one.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/quarkus-imperative-boilerplate.md` — the canonical Quarkus-service template; potentially the place where this extension gets pulled in by default.
- `~/projects/codebase-map/repos/quarkus-k8s-boilerplate.md` — the lightweight template.
- `~/projects/codebase-map/repos/quarkus-extension-persistence.md` — runs JTA-wrapped transactions; data migrations can use it for atomic blocks.
- `~/projects/codebase-map/repos/commons.md` — DataMigrationBase likely uses `commons.errors` for migration-failure handling.
- `~/projects/codebase-map/domains/platform.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `DataMigrationVersionEntity` | jpa | `runtime` | DataMigrationVersion |
<!-- entities-end -->
