---
repo: quarkus-extension-persistence
path: ~/projects/ship-cars-usa/quarkus-extension-persistence
stack: Java/Quarkus extension (runtime + deployment) — `ship.cars.quarkus.extensions.persistence:quarkus-extension-persistence` 3.27.5 (on shipcars-quarkus-bom / Quarkus 3.27.5), JTA + Hibernate ORM
domain: platform
shape: multi-module (runtime + deployment + coverage-report)
last-synced-commit: 7ae5647982088dde590e3c1516650c2c5259a1ad
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# quarkus-extension-persistence

## What it is
A **narrowly-scoped Quarkus extension that provides explicit JTA transaction-control helpers** for use outside the standard `@Transactional` annotation surface. Despite the broad name, it does **not** do Hibernate config, Hikari pool tuning, repository scaffolding, or anything else "persistence-shaped" — it's two service interfaces and their implementations:

- **`TransactionalExecution`** — programmatic transaction wrapper: `executeInTransaction(Supplier<T>)`, `executeInTransaction(Runnable)`, `executeInNewTransaction(...)` (which requires no active transaction), plus `ensureInTransaction()` / `ensureNotInTransaction()` assertions.
- **`TransactionalBatchesExecution`** — same idea, but for batched operations where each batch should commit independently (e.g. ETL-style bulk inserts where one bad batch shouldn't roll back the whole job).

The implementations check `TransactionManager` status before delegating, so calling `executeInTransaction(...)` inside an already-active transaction is a no-op (just runs the supplier); calling `executeInNewTransaction(...)` inside an active transaction throws `IllegalStateException`. This is the right primitive for code that needs to commit a sub-unit-of-work mid-flow (the canonical example: an outbox poller that wants each successfully-published row to commit independently rather than batching all-or-nothing).

## How it fits

- **Compile-time consumers:** ~25 fleet repos declare `ship.cars.quarkus.extensions.persistence:runtime` (verified 2026-08-28) —
  - `ai-dashboard-backend`, `bi-databricks-backend`, `cube`, `integrations-backend`, `invoices`, `load-recommender`, `loadboard-backend`, `metadata`, `montway-payments-backend`, `notification-orchestrator`, `pusher`, `synclink-backend`, `toolbox-service`, `trip-planner`, `user-activity-tracker`.
  - Both Quarkus boilerplate repos (`quarkus-imperative-boilerplate`, `quarkus-k8s-boilerplate`) — meaning every service spun up from those templates inherits this dependency by default.
  - `quarkus-user-syncer` (runtime + deployment) — its `db-syncer` consumers (`notification-orchestrator`, `load-recommender`, `trip-planner`, `saved-search-handler`) get it transitively.
- **Consumes API of:** none.
- **Publishes events to:** none.
- **Owns data store:** none.

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
  <groupId>ship.cars.quarkus.extensions.persistence</groupId>
  <artifactId>runtime</artifactId>
  <version>${shipcars-quarkus-bom.version}</version>
</dependency>
```

## Key abstractions

- **`TransactionalExecution` (interface) + `TransactionalExecutionImpl` (`@ApplicationScoped`)** — the main entry point. `executeInTransaction` joins an existing transaction; `executeInNewTransaction` requires no active transaction. The "join existing if present" semantics make this safer than rolling your own `@Transactional` wrapper.
- **`TransactionalBatchesExecution` + `TransactionalBatchesExecutionImpl`** — batched variant. Each batch runs in its own transaction so partial progress survives a failure mid-job.
- **`TransactionalExecutionHelper`** (`@ApplicationScoped`) — internal CDI bean the impl delegates to; wraps `QuarkusTransaction.requiringNew()` and calls **`entityManager.clear()` before running the supplied work**. Lets the impl be a thin "check status then delegate" layer, testable without mocking `TransactionManager`.
- **`BatchConfig`** (`@Builder/@Value`) — config for `TransactionalBatchesExecution`: `batchSize` (default 100), `executeInParallel`, `executeInTransaction`, `LogBatchProgress` callback.
- **`QuarkusExtensionsPersistenceProcessor`** (`deployment/`) — the only build-step class: registers `FeatureBuildItem("ship-cars-Extension-Persistence")` and an `AdditionalBeanBuildItem` marking the three impls unremovable. Beans are wired **only** via this build step (no `beans.xml`/annotation discovery in runtime) — using the classes without the extension's deployment module leaves them unregistered.
- **No `@ConfigMapping`, no config properties** — this extension has no runtime knobs (confirmed: zero `@ConfigMapping`/`@ConfigRoot`/prefix in source).

## Don't-do-here / gotchas

- **Despite the name, this is not where Hikari / JDBC pool defaults live.** The pool-size outlier table in `~/projects/codebase-map/relations/data-stores.md` (8 services with `max-size ≤ 10`, including `notification-backend` 5, `public-tracking-backend` 5, `dataone` 4, `load-bookmark-backend` 4 prod) is **NOT** caused by anything in this repo. Hikari/Quarkus pool config flows through standard `quarkus.datasource.jdbc.*` properties per repo. A "fleet-wide pool-size right-sizing" change would be many-line changes across many `application.properties`, not a one-liner here.
- **No baseline JTA timeout.** Neither this extension nor `quarkus-commons` sets a default `quarkus.transaction-manager.default-transaction-timeout`. A long-running supplier inside `executeInTransaction(...)` can hold a transaction (and its underlying JDBC connection) for the default JTA timeout (60 s in Narayana). Combined with `max-size=4` pools (`dataone`, `load-bookmark-backend`, `location-history-backend`, `location-provider`), a single hung call can exhaust the pool quickly.
- **`executeInTransaction(Supplier<T>)` joining an existing transaction is sometimes the wrong default.** A caller already inside a 30-s transaction who calls this expecting a fresh transaction will get the existing one — and any rollback they trigger will roll back the parent's work too. If you need isolation, use `executeInNewTransaction(...)` and accept that you must not already be in a transaction.
- **`executeInNewTransaction(...)` throws `IllegalStateException` if already in a transaction.** Don't wrap it in `try { ... } catch (IllegalStateException ignored) {}` — the assertion is load-bearing for correctness. Restructure the caller to be outside the transaction before entering, e.g. by suspending via `@Transactional(REQUIRES_NEW)` semantics in the call chain.
- **Public API is tiny but every service in the fleet that does anything ETL-like depends on it.** Adding methods (e.g. `executeInReadOnlyTransaction`) is fine; renaming or removing them is a fleet-wide change. Treat the two interface signatures as semi-versioned.
- **No Hibernate-session helpers** — services that need to flush, evict, or detach a session do it directly against the injected `EntityManager`. If you find yourself adding "session lifecycle" helpers here, consider whether they belong in a per-domain `*PersistenceCommons` library instead.
- **`TransactionalExecutionHelper` calls `entityManager.clear()` at the start of every new transaction.** This detaches any managed entities the caller was holding — references become stale/detached after the call. Don't hold a managed entity across an `executeInNewTransaction(...)` boundary expecting it to stay attached.
- **`TransactionalBatchesExecution` defaults to `parallelStream` + a new transaction per batch.** Both flags default true when the `BatchConfig` fields are null; parallel batches run on the common ForkJoinPool, each with its own tx/`EntityManager` context. Cross-batch ordering and shared-state assumptions do not hold, and a mid-run failure leaves earlier batches **committed** (no all-or-nothing).
- **This is NOT the fleet's base-entity / `@Version` / auditing layer.** Confirmed by exhaustive grep: no `@Entity`, `@MappedSuperclass`, `@Version` (neither the Hibernate nor the Jakarta import), `@PrePersist`, `Converter`, or Panache base class exists here. Optimistic locking / auditing / JSONB converters that the fleet relies on live elsewhere (commons / per-service `db-entities` modules), not in this extension — don't cite this repo as their source.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/commons.md` — depends on the parent commons BOM.
- `~/projects/codebase-map/repos/quarkus-commons.md` — the broader Quarkus commons (OTel/MDC). Pool-size knobs come through Quarkus config, not either of these.
- `~/projects/codebase-map/relations/data-stores.md` — documents the pool-size outliers; this seed corrects the assumption that the fix could land in a single shared extension.
- `~/projects/codebase-map/domains/platform.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `BatchConfig` | dto | `runtime` | BatchConfig |
<!-- entities-end -->
