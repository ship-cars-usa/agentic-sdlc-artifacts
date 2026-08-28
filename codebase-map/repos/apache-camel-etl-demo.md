---
repo: apache-camel-etl-demo
path: ~/projects/ship-cars-usa/apache-camel-etl-demo
stack: Java 17 / Apache Camel Quarkus 3.4.1 (demo / example)
domain: infrastructure
shape: single-module
last-synced-commit: acc0517ea3a77677e77bad26f041f30ef89bcc32
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# apache-camel-etl-demo

## What it is
**Self-described as a "Camel Quarkus example"** in its own README.adoc — a small Java 17 / Camel Quarkus 3.4.1 demo of timer-driven PostgreSQL-to-PostgreSQL incremental sync. Two Camel routes (`CustomersRoutes`, `CarsRoutes`) fire every 3 s, read `MAX(last_modified)` from the target DB, fetch new rows from the source DB, and upsert into the target using `ON CONFLICT DO UPDATE` with parallel processing. **Likely not production**; the demo framing + the hardcoded poll interval + the lack of error handling are all signals. Worth flagging in `infrastructure-triage.md` as an **archive-candidate** or formalizing into a production ETL pattern if anyone actually depends on it.

## How it fits
- Consumes API of: none (DB-to-DB only).
- Publishes events to: none.
- Subscribes to: none.
- Owns data store: dual PostgreSQL — source `jdbc:postgresql://localhost:5002/shipcars` (pool 16); target `jdbc:postgresql://localhost:6002/shipcars` (pool 16). Reads/writes `customers` + `cars` tables.

## Build / test / run
```
./mvnw clean package -DskipTests
./mvnw quarkus:dev
# Single-module Quarkus + Camel
# Two routes auto-start; timer fires every 3 seconds
```

## Key abstractions
- `BaseRoute` — `src/main/java/org/camel/demo/BaseRoute.java:9` — abstract `RouteBuilder`; timer-driven incremental sync template; parallel processing.
- `CustomersRoutes` — concrete route for `customers` table.
- `CarsRoutes` — concrete route for `cars` table.
- `StartTimer` / `EndTimer` processors — measure sync duration; log cumulative runtime.

## Don't-do-here / gotchas
- **Likely not production**. README.adoc explicitly calls it "A Camel Quarkus example" with "demo data" setup scripts. Confirm with owners before relying on this for anything; otherwise add to `infrastructure-triage.md` as an archive-candidate.
- **Java 17, not Java 21** — version drift relative to the rest of the fleet (`location-history-backend`, `negotiations-router`, `cube`, etc. are all Java 21). If this repo is promoted to production, align the JDK first.
- **3-second timer is hardcoded** — no config property. High overhead for low-velocity tables.
- **No idempotency keys** — parallel processing without per-row dedup means a duplicate timer fire (e.g., overlapping sync runs) can produce duplicate inserts under contention. The `ON CONFLICT DO UPDATE` upsert masks this for primary-key collisions but doesn't help if the source-side cursor (`MAX(last_modified)`) drifts.
- **`MAX(last_modified)` cursor assumes synchronized clocks** between source and target. Clock skew can lose rows.
- **`SELECT ... LIMIT 770`** hardcoded batch size — no back-pressure if target DB is slow.
- **No error handling** — Camel route has no `errorHandler` or `try/catch` visible. Failures leave the route in an undefined state.
- **No metrics / structured logging beyond timer-duration** — operational opacity.

## Relevant ADRs / docs
- `~/projects/codebase-map/relations/infrastructure-triage.md` — likely an archive-candidate row.
- `~/projects/codebase-map/domains/infrastructure.md`.
