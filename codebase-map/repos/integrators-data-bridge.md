---
repo: integrators-data-bridge
path: ~/projects/ship-cars-usa/integrators-data-bridge
stack: Java 21 / Quarkus 3.27.5 (Apache Camel routes)
domain: integrations
shape: multi-module (7 poms)
last-synced-commit: 188b0b69f20388d29b8befed5d6de264bbd38fe0
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# integrators-data-bridge

## What it is
Apache Camel-based ETL bridge. Migrates data from a set of source PostgreSQL databases into one centralized target DB via time-windowed polling, filtered by a configured set of company ids (`company_ids.json`). Per the README: "a bridge between the integrators and the data providers … migrate data from one/set of database to another/set of database." Batch-style: it runs the sync, logs total duration, then gracefully stops Camel and exits the Quarkus process (`Quarkus.asyncExit()`) — it is not a long-running server.

Four source domains are wired today: **posting**, **inventory**, **autoims**, **contract-pricing** (`BaseController.configure()` multicasts to `LOAD_LEG`, `INVENTORY`, `CONTRACT_PRICING`, `AUTOIMS` routes). SQL-only data path — **no JAX-RS REST clients**.

## How it fits
- Consumes API of: none (no REST clients).
- Reads from: 4 source PostgreSQL datasources — `sourcePosting`, `sourceInventory`, `sourceAutoIms`, `sourceContractPricing` (`configuration/.../application.properties`).
- Writes to: 1 centralized `targetDataSource` PostgreSQL (upsert via Camel `sql:` endpoints).
- Publishes events to: none (no Pub/Sub).
- Owns data store: the target-side tables (write path). Requires the AAAG DB user to have grants on any newly added source tables — README says to have DevOps re-run terraform after adding tables.

## Build / test / run
```
./start-quarkus-dev.sh      # dev mode + local Postgres container
./mvnw clean package
./mvnw test
# 7 modules: application, services, commons, configuration, db-migration,
#            coverage-report, (root)
# Requires SOURCE_DB_* / TARGET_DATASOURCE_* env + CONFIG_COMPANY_IDS_FILE
```

## Key abstractions
- `BaseController` — `services/.../services/BaseController.java` — extends Camel `RouteBuilder`; `configure()` multicasts `direct:start` across the 4 domain routes, times the run, then stops Camel + exits Quarkus.
- `BaseProcessor` — `services/.../services/BaseProcessor.java` — interface (`getInsertQuery()`, `getSourceTableName()`) implemented by every per-table processor.
- Per-table processors — `services/.../services/{posting,inventory,autoims,contractpricing}/*Processor.java` — ~45 of them (e.g. `LoadProcessor`, `LoadLegProcessor`, `InventoryProcessor`, `AutoImsProcessor`, `ContractProcessor`, `PricingOptionProcessor`); each defines the source `SELECT` and the target upsert.
- `RouteUtils` — `commons/.../commons/utils/RouteUtils.java` — `buildInsertUpdateQuery()` (INSERT … ON CONFLICT DO UPDATE), `findIdColumn()`, `fixLastHours()`.

## Don't-do-here / gotchas
- **Unbounded `SELECT *` on source tables** — `services/.../posting/LoadProcessor.java:59`, `services/.../posting/LoadLegProcessor.java:133` and `:148` build `"sql:SELECT * FROM " + …` with no `LIMIT` and no `WHERE` time-window. First sync of a large source table is an OOM risk. Add a watermark + chunked `LIMIT`.
- **Camel shutdown on a raw `new Thread()` + `Thread.sleep()`** — `BaseController.java` `EndTimer` spawns an unmanaged thread that sleeps `config.sleepInterval()` seconds, stops the Camel context, then calls `Quarkus.asyncExit()`. If SIGTERM arrives during the sleep the interrupt path is fragile; the pod can hang until `terminationGracePeriodSeconds`. Prefer `@Observes ShutdownEvent`.
- **No `acquisition-timeout` on the 5 datasources** — each source + target sets `jdbc.max-size=16` (80 pooled connections total) with no `acquisition-timeout`. A slow source DB silently drains its pool. Add `quarkus.datasource.<name>.jdbc.acquisition-timeout`.
- **`multicast()` with no `onException().handled(true)`** — `BaseController.configure()`; one route's failure has unclear effect on the sibling routes.
- **`RouteUtils.buildInsertUpdateQuery()` interpolates `tableName` and `idColumn` straight into SQL** — hardcoded call sites today, but the API is a SQL-injection foot-gun; assert names against an allow-list.
- **`RouteUtils.findIdColumn()` returns the first column whose name *contains* `"id"`** (so `created_id`/`void_id` could beat `id`). Use an exact match.
- **24-hour default sync window, no resume-from-watermark** — `*-last-hours-to-sync` defaults to 24 with no persisted last-run marker; a crashed run permanently skips that window.
- **`totalDuration` accumulates across runs** (`BaseController`) — never reset.

## Relevant ADRs / docs
- `~/projects/quarkus-fleet-review-2026-05-07.md#7-integrators-data-bridge` — original fleet review.
- `~/projects/codebase-map/domains/integrations.md`.
