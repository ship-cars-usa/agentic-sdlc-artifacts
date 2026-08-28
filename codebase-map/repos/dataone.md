---
repo: dataone
path: ~/projects/ship-cars-usa/dataone
stack: Java/Quarkus 3.27.5 (Java 21)
domain: platform
shape: multi-module
last-synced-commit: 04fc9814fede3710a065ee81dce588e020dadeb0
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# dataone

## What it is
Quarkus 3.27.5 / Java 21 **local vehicle-catalog + VIN-decode service** (`ship-cars-dataone`). Despite the name it is **not** a runtime adapter to the external DataOne vendor: there are **no outbound REST clients**. It serves the canonical Ship.Cars catalog of makes / models / years and VIN decodes for passenger cars, trucks, motorcycles, and power-sports from its own PostgreSQL DB (JOOQ queries + materialized views), fronted by a per-JVM Caffeine cache. The DB is populated **offline** from DataOne vendor SQL/CSV exports via shell + SQL scripts (`utils/`, `ddl-sql/`, `data-sql/`) — see `README_DATA_UPDATE.md`. It is one of the highest-fanout read-only callees in the fleet (inbound REST from `inventory-backend`, `fraud-detector`, `autoims-backend`, `quote-manager-backend`, `posting-backend`, `loadboard-backend`, `rateengine`, `ml-service-dispatcher` per the service graph).

## How it fits
- **Consumes API of:** **none** — no `@RegisterRestClient` anywhere. Config keys `dataone.api-key`/`export-key`/`image-base-url` exist but no runtime HTTP client uses them; they relate to the offline data pipeline.
- **Publishes events to:** none.
- **Subscribes to:** none (no Pub/Sub, no reactive-messaging).
- **Owns data store:** PostgreSQL db `dataone` with **JOOQ 3.20.9** typesafe queries + materialized views (`mv_make`, `mv_make_mc`, `mv_vin_lookup`, `mv_fuel_types`, ...). Per-JVM Quarkus **Caffeine** cache (max 10 000 entries, `expire-after-write=1400h` ≈ 58 days). Pool `max-size=4` (single global value, no dev/prod split). **Redis** is wired but effectively dev-only (see gotchas).

## Build / test / run
```
./mvnw clean install         # JVM build + tests; native supported
./start-quarkus-dev.sh       # dev; Swagger UI at /q/swagger-ui/ (:8871 in test/dev)
./build-native.sh            # native build (GraalVM/Mandrel)
# 11 poms (parent + application, resources, services, db-entities, api-dtos,
#          commons, configuration, coverage-report, integration-test, mv-tests)
# Data refresh is offline: see README_DATA_UPDATE.md (FTP → DDL → CSV import → data fixes → REFRESH MATERIALIZED VIEW)
```

## Key abstractions
- `DataOneServiceImpl` — `services/src/main/java/cars/ship/dataone/app/services/impl/DataOneServiceImpl.java` — core catalog/VIN service (`@ApplicationScoped`); `findAllYearMakeModel`, `findAllTruckYearMakeModel`, `findAllPowerSportsYearMakeModel`, `findVehicleByVin`, and per-domain make/model/year finders. Injects `SqlClientService` + `RedisClientService`.
- `SqlClientServiceImpl` — `services/.../impl/SqlClientServiceImpl.java` — JOOQ query execution (`executeQuery(query, EntityClass)`).
- `RedisClientServiceImpl` — `services/.../impl/RedisClientServiceImpl.java` — wraps `RedisDataSource`; get/set with a key prefix, failures caught+logged returning null.
- REST resources in `resources/src/main/java/cars/ship/dataone/rest/` (all with `@CacheResult`):
  - `VehicleController` — `@Path("")` (root): `/years`, `/makes`, `/models`, `/vehicles`, `/vehicles/fuzzy`, `/vehicles/json`, `/vin/{vin}`.
  - `TruckController` — `@Path("/trucks")`: `/makes`, `/models`, `/vehicles/json`, `/vin/{vin}`.
  - `MotorcycleController` — `@Path("/mc")`: `/years`, `/makes`, `/models`, `/vehicles`, `/vehicles/json`.
  - `PowerSportsController` — `@Path("/powersports")`: `/makes`, `/models`, `/vehicles/json`, `/vin/{vin}`.
  - `UnifiedVehicleController` — `@Path("/unified")`: `/vin/{vin}`, `/years`, `/makes`, `/models`, `/vehicles`.
  - `OperationsController` — `@Path("/api/operations")`: import-statistics reporting, `POST /data-fix/*`, `DELETE /cache/clear`.
- Cache names: `years`, `makes`, `models`, `mc_years`, `mc_makes`, `mc_models` (controllers) and `truck_*`, `powersports_*` (service layer).

## Don't-do-here / gotchas
- **CORRECTION vs. prior shadow — controller paths.** Motorcycles are under `@Path("/mc")` (not `/motorcycles`); `VehicleController` is mounted at root (`@Path("")`). There is also a `/unified` controller.
- **CORRECTION — there is no `db-migration` module.** The repo is 11 poms; schema/DDL and data live in `ddl-sql/`, `data-sql/`, and `utils/` scripts, applied offline (not Flyway-at-start). `ImportStatistics*` only records/reports import stats via `OperationsController`; it does not perform the load.
- **CORRECTION — `RedisClientService` is not dead code.** It is injected and called (VIN lookups + generic cache path) in `DataOneServiceImpl` and `OperationsController`. BUT `quarkus.redis.hosts` is commented out for prod (managed via Helm) and only set under `%dev`; get/set swallow failures and return null. So Redis is live in dev, effectively inactive/degraded in prod — Caffeine is the real production cache.
- **Caffeine `expire-after-write=1400h` (~58 days)** — a single global default across every named cache. When vehicle specs change (year-model rollover, VIN-table refresh) hot pods won't pick it up for ~8 weeks, and the cache is per-JVM so replicas diverge. `DELETE /api/operations/cache/clear` exists as the manual bust; consider a shorter TTL.
- **HikariCP `max-size=4`** — extreme outlier for one of the highest-fanout callees in the fleet. Cache miss + JOOQ query + tiny pool exhausts fast. Raise it. There is no separate prod override.
- **CORS open to `*`** (methods `GET,POST,DELETE`, allow-credentials=true) — accept for an internal lookup service but document the deliberate decision.
- **No outbound resilience concerns** (no REST clients), but callers should circuit-break to this service since it's a hot dependency; `ml-service-dispatcher` enforces a 30s caller-side timeout.
- **Naming confusion**: integrators may assume "DataOne" wraps the external vendor at runtime — it does not. The vendor coupling is offline-only.

## Relevant ADRs / docs
- `~/projects/codebase-map/relations/service-graph.md` — inbound REST edges from the seeded consumers.
- `~/projects/codebase-map/relations/data-stores.md` — pool-size outlier table.
- `~/projects/ship-cars-usa/dataone/README_DATA_UPDATE.md` — the offline data-refresh runbook.
- `~/projects/codebase-map/domains/platform.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `ImportStatisticsEntity` | jpa | `db-entities` | ImportStatistics |
| `MakeEntity` | jpa | `db-entities` | Make |
| `VinLookupEntity` | jpa | `db-entities` | VinLookup |
| `DataOneServiceImpl` | dto | `services` | DataOneServiceImpl |
| `ImportSessionSummaryDto` | dto | `api-dtos` | ImportSessionSummary |
| `ImportStatisticsDashboardDto` | dto | `api-dtos` | ImportStatisticsDashboard |
| `MakeDto` | dto | `api-dtos` | Make |
| `ModelDto` | dto | `api-dtos` | — |
| `MotorcycleController` | dto | `resources` | MotorcycleController |
| `PagedResponseDto` | dto | `api-dtos` | Paged |
| `RedisClientServiceImpl` | dto | `services` | RedisClientServiceImpl |
| `SqlClientServiceImpl` | dto | `services` | SqlClientServiceImpl |
| `TableStatisticsDto` | dto | `api-dtos` | TableStatistics |
| `VehicleController` | dto | `resources` | VehicleController |
| `VehicleDto` | dto | `api-dtos` | [Vehicle](../domains/entities/Vehicle.md) |
| `VehicleFullDto` | dto | `api-dtos` | VehicleFull |
| `VehiclePriceDto` | dto | `api-dtos` | VehiclePrice |
| `VehicleYearDto` | dto | `api-dtos` | VehicleYear |
| `YearFilterSpec` | dto | `services` | YearFilterSpec |
| `PowerSportsModelEntity` | other | `db-entities` | PowerSports |
| `TruckModelEntity` | other | `db-entities` | [Vehicle](../domains/entities/Vehicle.md) |
<!-- entities-end -->
