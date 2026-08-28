---
repo: quarkus-extension-firestore-storage
path: ~/projects/ship-cars-usa/quarkus-extension-firestore-storage
stack: Java/Quarkus extension — `ship.cars.quarkus.extensions.firestore.storage:quarkus-extension-firestore-storage` 3.27.5 (on shipcars-quarkus-bom / Quarkus 3.27.5), Google Cloud Firestore
domain: platform
shape: multi-module (runtime + deployment + coverage-report)
last-synced-commit: 75c54e5c5e96065c0aae1e5f550359640c6ffce1
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# quarkus-extension-firestore-storage

## What it is
A **high-level CRUD wrapper around Google Cloud Firestore**, exposed as a typed `StorageClient` to Quarkus services. Abstracts Firestore's document-store API behind a fleet-conventional interface with:

- **Version management** — every stored entity carries a version field; updates check + bump it.
- **Optimistic concurrency control** — concurrent modifications throw `StorageConcurrentModificationDetectedException` rather than silently overwriting.
- **TTL auto-deletion** — per the README, the extension supports TTL-based document expiration (Firestore's native TTL feature).
- **Typed exception hierarchy** — `StorageKeyNotFoundException`, `StorageKeyAlreadyExistsException`, `StorageConcurrentModificationDetectedException` for the common error paths.

It is **Firestore-only despite the "storage" name** — there is no `google-cloud-storage`/GCS dependency. "Storage" means structured document storage. It wraps the Quarkiverse `quarkus-google-cloud-firestore` extension (2.22.0); the underlying `Firestore` bean is produced by Quarkiverse, and this extension adds the CRUD/versioning/TTL/retry layer on top. Java package is `cars.ship.quarkus.extensions.firestore.storage.*` (note: `cars.ship`, not `ship.cars`).

As of 3.27.5 it is **in step with the fleet HEAD** (previously lagged at `3.20.2.3-SNAPSHOT`; that "behind the fleet" caveat no longer applies).

## How it fits

- **Compile-time consumers:** **1 confirmed (`command-executor`)** — pins `ship-cars-quarkus-extensions-firestore-storage.version=3.27.5`, declares the `runtime` dep in `services/pom.xml`, and uses it in the `ediorderful` package (`EdiOrderfulPendingTransactionEntity` + `...Repository`). Used when a service has small, key-value/document-shaped state that doesn't justify a Postgres schema. **Note:** `aaag-integration` is *not* a consumer of this in-house extension — it depends directly on the raw Quarkiverse `quarkus-google-cloud-firestore` (2.18.0) and only matched a generic firestore grep.
- **Consumes API of:** Google Cloud Firestore (via the Quarkiverse `quarkus-google-cloud-firestore` extension). Auth via `GOOGLE_APPLICATION_CREDENTIALS` env var, default ADC, or Quarkus dev services.
- **Publishes events to:** none.
- **Owns data store:** none directly — consumers own their Firestore collections / documents.

Configuration — **this extension defines no config properties of its own** (no `@ConfigMapping`/`@ConfigRoot`/`@ConfigProperty` anywhere). All config is delegated to the underlying Quarkiverse extension; collections are derived at runtime from the key path, not from config:
```properties
quarkus.google.cloud.project-id=your-project-id
# Optional (usually set via env QUARKUS_GOOGLE_CLOUD_FIRESTORE_DATABASE_ID):
# quarkus.google.cloud.firestore.database-id=your-database-id
```

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
  <groupId>ship.cars.quarkus.extensions.firestore.storage</groupId>
  <artifactId>runtime</artifactId>
  <version>${shipcars-quarkus-extensions-firestore-storage.version}</version>
</dependency>
```

## Key abstractions

- **`StorageClient`** — `runtime/src/main/java/cars/ship/quarkus/extensions/firestore/storage/runtime/StorageClient.java` — public interface consumers inject: `getEntity` / `createEntity` / `updateEntity` / `isExists` / `delete` / `deleteAll`.
- **`StorageClientImpl`** — `runtime/.../runtime/impl/StorageClientImpl.java` — `@ApplicationScoped @UnlessBuildProfile("test")`; constructor-injected `Firestore` + `ObjectMapper`; maps keys → collection/doc, optimistic locking via `Precondition.updatedAt`, retries, structured JSON logging.
- **`StorageEntity`** — `runtime/.../runtime/dtos/StorageEntity.java` — abstract `@SuperBuilder` base entity: `id`, `createdAt`, `modifiedAt`, `expiresAt` (TTL), `version` (`@JsonIgnore`, long, encoded from the Firestore update timestamp).
- **`StorageUtils`** — `runtime/.../runtime/StorageUtils.java` — `constructKey(...)` + `retryStorageConcurrentOperation(...)` (up to **50** retries, randomized 50–750 ms × retry backoff).
- **`KeyUtils`** — `runtime/.../runtime/impl/KeyUtils.java` — internal key sanitization (strips whitespace, collapses slashes).
- **`StorageKeyNotFoundException` / `StorageKeyAlreadyExistsException` / `StorageConcurrentModificationDetectedException`** — `runtime/.../runtime/*.java` — domain exceptions (missing-on-update / duplicate-on-create / version conflict).
- **`FirestoreStorageProcessor`** — `deployment/.../deployment/FirestoreStorageProcessor.java` — build-time: registers feature `firestore-storage`, adds `StorageClientImpl` as an unremovable bean, and wires reflection/runtime-init for `StorageClient`, `StorageEntity`, `ErrorDto` (native-image support).

## Don't-do-here / gotchas

- **Only one known fleet consumer (`command-executor`).** Either niche-but-real usage, or this extension is under-adopted. A second consumer should reference this seed before assuming patterns are universal.
- **`3.20.2.3-SNAPSHOT` is behind the fleet HEAD** (3.27.x). Verify version compatibility before importing into a newer service.
- **Firestore is GCP-only.** Don't propose this extension for a service that needs cloud-portability — pin to Postgres or another portable store.
- **Optimistic concurrency is timestamp-based and its detection is brittle.** `version` is encoded from the Firestore update timestamp (micros) and enforced via `Precondition.updatedAt`. A conflict surfaces as `FailedPreconditionException` — or as an `InvalidArgumentException` whose message contains "invalid base version", which the impl matches by **lowercased substring**. If Google changes that message text, conflict detection silently breaks. Callers still must read → modify → write back the same version.
- **Retries can add real latency.** Two layers: a low-level `executeWithRetry` (commons `RetryConfig`, additionally retries `DeadlineExceededException`) and `StorageUtils.retryStorageConcurrentOperation` which defaults to **50 attempts** with blocking randomized backoff (50–750 ms × retry). Under contention this can block a caller thread for seconds.
- **`deleteAll` is recursive and unbounded** — walks documents + subcollections issuing individual deletes in a loop, no batching. Slow / many round-trips on large trees.
- **Test-profile swap.** `StorageClientImpl` is `@UnlessBuildProfile("test")`, so no real bean exists under the `test` profile — tests must supply their own (e.g. in-memory) `StorageClient` or injection fails.
- **TTL (`expiresAt`) needs one-time Terraform setup and is eventual.** Each collection group needs a `google_firestore_field` TTL policy; documents stay query-visible until Firestore reaps them (~24 h lag), and TTL does **not** cascade to subcollections. Don't use TTL as a security boundary.
- **No fleet-wide schema** — each consumer designs its own document shape. `StorageEntity` provides the wrapper; the payload is service-specific.
- **Firestore credentials caveat** — `GOOGLE_APPLICATION_CREDENTIALS` is the standard path; missing the env var falls through to ADC which may silently use the wrong project. There is no GCS/bucket handling here despite the "storage" name.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/command-executor.md` — the one confirmed consumer.
- `~/projects/codebase-map/repos/loadbuilder-backend.md` — Spring service using GCS-as-DB rather than Firestore; useful contrast for "when do you reach for Firestore vs GCS vs Postgres?"
- `~/projects/codebase-map/repos/quarkus-pubsub.md` — sibling GCP-integration extension.
- `~/projects/codebase-map/domains/platform.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `StorageConcurrentModificationDetectedException` | dto | `runtime` | StorageConcurrentModificationDetectedException |
| `StorageKeyAlreadyExistsException` | dto | `runtime` | StorageKeyAlreadyExistsException |
| `StorageKeyNotFoundException` | dto | `runtime` | StorageKeyNotFoundException |
<!-- entities-end -->
