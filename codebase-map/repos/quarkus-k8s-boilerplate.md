---
repo: quarkus-k8s-boilerplate
path: ~/projects/ship-cars-usa/quarkus-k8s-boilerplate
stack: Java 21 / Quarkus 3.27.5 / Maven single-module (packaging=jar) / Postgres + Panache + Hibernate Envers / Flyway / Pub/Sub / Mandrel native-image
domain: platform
shape: single-module (one `pom.xml`, `src/main/java/cars/ship/boilerplate/...`)
last-synced-commit: 048c37b1d8882a2a2b452ea4d40b6b8711668e38
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# quarkus-k8s-boilerplate

## What it is
**The lightweight, single-module Quarkus microservice template** — the streamlined counterpart to `quarkus-imperative-boilerplate`. Root `pom.xml` is `packaging=jar`, groupId `ship.cars.quarkus.boilerplate`, artifactId `boilerplate`, version `0.1.0-SNAPSHOT`. Per `README.md` it is "optimized for Kubernetes (K8s), serverless deployments, and native compilation" and refactored from the multi-module architecture into one module, aimed at services with **5–20 REST endpoints** and small teams.

Same fleet conventions wired in by default (Envers audit via a `BaseDbEntity`/`CustomRevisionListener`, Pub/Sub config, MapStruct mappers, `PageDtoConverter`, `ActorContext`) but without the 10-module ceremony. Sample domain is `City` + `State`. HTTP port defaults to `7071` (`application.properties`).

At HEAD it pins **Quarkus 3.27.5**, imports **shipcars-quarkus-bom 3.27.5** and **ship.cars.commons:bom 3.33.0**, and pins the Ship.Cars Quarkus extensions at 3.27.5 (the `LITE-000 Update Quarkus bom to v3.27.5` HEAD commit). A repo-root `CLAUDE.md` points Claude at the `java-stack` plugin skills.

## How it fits

- **Not a runtime service.** Template only — no helm chart, no production DB.
- **What it provides:** a single-module starting point with the full fleet extension stack already listed as concrete `<dependencies>` (not just managed), plus the `Dockerfile`/`Dockerfile-migrate`/`Dockerfile-test` set and `scripts/` + `utils/docker-compose/` helpers.
- **Who is generated from it:** small-CRUD-with-audit Quarkus services; `metadata` is the closest in-fleet shape match (assumed, not a compile-time edge). No service imports it as a dependency.
- **Owns data store:** none.

## Build / test / run
```
./scripts/start-quarkus-dev.sh               # JVM dev, live reload (-x PORT debug, -s skip tests)
./utils/docker-compose/docker-compose.sh up -d   # local Postgres
./scripts/start-flyway.sh                    # run migrations
./scripts/build-dev.sh                       # JVM build
./scripts/build-native.sh                    # native build (mvnw clean install -Pnative -DskipTests)
./scripts/start-quarkus-native.sh            # run native binary
java -jar target/quarkus-app/quarkus-run.jar # run JVM jar
./mvnw clean test                            # unit tests
```
Native build uses the Mandrel builder image `quay.io/quarkus/ubi-quarkus-mandrel-builder-image:23.1.8.0-Final-java21` and `resources-config.json`.

## Key abstractions

Package layout under `src/main/java/cars/ship/boilerplate/`:
- `config/` — `PubSubConfig`, `ObjectSerializerConfig`. Standard fleet wiring.
- `entity/` — `CityEntity`, `StateEntity`; `entity/audit/` holds `BaseDbEntity`, `CustomRevisionListener`, `RevisionInfoEntity`, `RevisionData` (the Envers audit base classes).
- `dto/` — `CityDto`/`StateDto` + `PageDto` + `RevDto` + `RevPageDto` variants and `RevisionTypeEnum`; `dto/pubsub/CommandPubSubDto`. Demonstrates the "Page" + Envers-"Rev" pattern.
- `repository/` — `CityRepository`, `StateRepository` (Panache), `AuditRepository`.
- `service/` + `service/impl/` + `service/mapper/` — `CityService`/`StateService` interfaces, `*ServiceImpl`, MapStruct `CityConverter`/`StateConverter` + `ConverterUtils`.
- `resource/` — `CityResource`, `StateResource`, `ResourceUtils` (JAX-RS endpoints).
- `util/` — `ActorContext` (Envers audit attribution), `PageDtoConverter`, `util/enums/BoilerplateErrorCodeEnum`.
- `src/main/resources/db/migration/` — `V1.0__baseline.sql`, `V2.0__default_data.sql` (Flyway).

`pom.xml` declares the fleet stack as concrete deps: `quarkus-rest-jackson`, `quarkus-hibernate-orm-panache`, `-envers`, `-validator`, `quarkus-jdbc-postgresql`, `quarkus-flyway`, `quarkus-smallrye-openapi`/`-health`, `quarkus-info`, `quarkus-opentelemetry`, `quarkus-micrometer-registry-prometheus`, `quarkus-logging-json`, `quarkus-logging-manager`; plus Ship.Cars `commons`, `quarkus-opentelemetry`, `quarkus-logging-json-fix`, and the `request-filter`/`pubsub`/`persistence` extension `runtime` artifacts.

## Don't-do-here / gotchas

- **Copy-paste identity bugs carried from the imperative template:** `sonar.projectKey` is still `ship-cars-usa_quarkus-imperative-boilerplate_...` and `<distributionManagement>` still points at `maven.pkg.github.com/ship-cars-usa/quarkus-imperative-boilerplate`. Fix both when cloning (and when reading Sonar, don't confuse the two repos).
- **Rename "boilerplate" after clone** across groupId/artifactId/packages/keys — same as the imperative template.
- **Single-module trade-off:** no Maven-enforced boundaries — a `service` can reach a `dto` that should be private. Discipline by convention.
- **Delete the `City`/`State` sample domain** after cloning; don't ship it.
- **`schema-management.strategy=none`** — schema comes from Flyway, not Hibernate DDL; `hibernate-envers.store-data-at-delete=true`.
- **Updates don't auto-propagate** to derived services (no compile-time edge).
- Pick `quarkus-imperative-boilerplate` instead when the service needs a separate `db-migration` module / distinct migration lifecycle or strict module boundaries.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/quarkus-imperative-boilerplate.md` — the heavier multi-module sibling.
- `~/projects/codebase-map/repos/shipcars-quarkus-bom.md` — the BOM (3.27.5) this template imports.
- `~/projects/codebase-map/repos/metadata.md` — closest in-fleet shape match (assumed).
- `~/projects/codebase-map/domains/platform.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `CityEntity` | jpa | `quarkus-k8s-boilerplate` | City |
| `StateEntity` | jpa | `quarkus-k8s-boilerplate` | [State](../domains/entities/State.md) |
| `CityDto` | dto | `quarkus-k8s-boilerplate` | City |
| `CityRevDto` | dto | `quarkus-k8s-boilerplate` | CityRev |
| `CommandPubSubDto` | dto | `quarkus-k8s-boilerplate` | Command |
| `StateDto` | dto | `quarkus-k8s-boilerplate` | [State](../domains/entities/State.md) |
| `StateRevDto` | dto | `quarkus-k8s-boilerplate` | StateRev |
<!-- entities-end -->
