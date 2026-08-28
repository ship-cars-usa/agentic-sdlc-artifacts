---
repo: quarkus-imperative-boilerplate
path: ~/projects/ship-cars-usa/quarkus-imperative-boilerplate
stack: Java 21 / Quarkus 3.27.5 / Maven multi-module / Flyway / Postgres / Lombok + MapStruct / Mandrel native-image
domain: platform
shape: multi-module (10 Maven modules: api-dtos, application, commons, configuration, coverage-report, db-entities, db-migration, repositories, resources, services)
last-synced-commit: 6ea57c90d60bfe641fdfdcf3d4db980c34670ce2
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# quarkus-imperative-boilerplate

## What it is
The fleet's **canonical service template for new Quarkus imperative (DB-backed) services**. A clone-and-rename skeleton: root `pom.xml` is `packaging=pom` with groupId `ship.cars.quarkus.boilerplate`, artifactId `boilerplate`, version `0.1.0-SNAPSHOT`. It pre-wires the conventions every Ship.Cars Quarkus backend follows — Postgres + Flyway migrations, JPA entities, the module split between `resources`/`services`/`repositories`, and the fleet extension stack.

Per `README.md`: "When starting a new project, please replace the word 'boilerplate' with the actual name of your project throughout the codebase." The README explicitly notes it targets *small, highly performant imperative services* and does **not** strictly follow DDD.

At HEAD it pins **Quarkus 3.27.5** (`quarkus.platform.version` in `pom.xml`), imports **shipcars-quarkus-bom 3.27.5** and **ship.cars.commons:bom 3.33.0**, and pins the Ship.Cars Quarkus extensions at 3.27.5. There is now a `CLAUDE.md` at the repo root pointing Claude at the `java-stack` plugin skills and a Gradle-vs-Maven note.

## How it fits

- **Not deployed as a service.** Template repo — no helm chart, no Pub/Sub subscription, no production DB schema. (`db-migration` contains only the sample `City`/`State` baseline.)
- **What it provides:** the reference 10-module Maven layout, the standard `Dockerfile` / `Dockerfile-migrate` / `Dockerfile-test` set, the `start-*.sh` scripts, and the exact `<dependencyManagement>` a new imperative service should start from.
- **Who is generated from it:** imperative Quarkus services across the fleet share the identical module layout + start-script set and were clone-then-rename derivations (e.g. `command-executor`, `axe-call-integration`, `integration-executor` — assumed from structural match, not a compile-time edge).
- **Compile-time consumers:** none — no service imports the template as a dependency. Updates here do **not** auto-propagate; teams refresh their own skeletons by hand.
- **Owns data store:** none.

## Build / test / run
```
./start-quarkus-dev.sh                       # JVM dev, Postgres via utils/docker-compose
./start-quarkus-dev.sh -x 8000 -s            # debug on :8000, skip tests
./start-quarkus-native.sh                    # run native binary
./build-native.sh                            # native build (mvnw clean install -Pnative -DskipTests)
./start-flyway.sh                            # run Flyway migrations
utils/docker-compose/docker-compose.sh up -d # local Postgres container
./mvnw clean install                         # JVM build + unit tests
./mvnw clean verify                          # + integration tests (skipITs defaults true)
./execute-sonar.sh                           # SonarQube analysis
```
Native build uses the Mandrel builder image and `-H:ResourceConfigurationFiles=resources-config.json` (the `native` profile in `pom.xml`).

## Key abstractions

Module roles (from `README.md` + root `pom.xml` `<modules>`):

| Module | Role |
|---|---|
| `api-dtos` | REST API DTOs — wire-format types exposed to callers. |
| `commons` | Service-internal shared utilities + test helpers (published with a `tests` test-jar classifier). NOT the fleet-shared `ship.cars.commons`. |
| `configuration` | `application.properties` (exactly one file, per README) + config classes. |
| `db-entities` | JPA entity classes. |
| `db-migration` | Flyway SQL migration scripts. |
| `repositories` | Data-access layer over the entities. |
| `resources` | JAX-RS REST resource implementations (the HTTP endpoints). |
| `services` | Business logic, Pub/Sub listeners, REST-client wiring. |
| `application` | Aggregator module producing the deployable artifact. |
| `coverage-report` | Jacoco aggregate report (wired into Sonar). |

Root-`pom.xml` wiring worth knowing:
- **Fleet extensions pulled in via dependencyManagement:** `shipcars-quarkus-bom` (import), `ship.cars.commons:bom` + `commons`, `ship.cars.quarkus.commons:quarkus-opentelemetry`, `quarkus-logging-json-fix`, and the `request-filter` / `pubsub` / `persistence` extension `runtime` artifacts — all at 3.27.5.
- **Annotation processors** (`maven-compiler-plugin`): MapStruct 1.6.3 + `lombok-mapstruct-binding`, Hibernate processor 7.1.8.Final, `quarkus-panache-common`, Lombok 1.18.42.
- `utils/` — infrastructure scripts (deploy/sonar/db-tooling); a directory, **not** a Maven module.
- `lombok.config`, `mvnw`/`mvnw.cmd`, `.mvn/maven-update-rules.xml` (feeds `versions-maven-plugin`).

## Don't-do-here / gotchas

- **Renaming "boilerplate" after clone is manual** and spans groupId (`ship.cars.quarkus.boilerplate`), artifactIds, packages, and the Sonar/distribution keys. Forgetting produces an artifact still named `boilerplate`.
- **Updates to this template don't auto-propagate** to derived services — no compile-time edge exists. New conventions must be hand-merged into each service.
- **`configuration` holds exactly one `application.properties`** (README: "there should be only one configuration file"). Use `%dev.`/`%test.`/`%prod.` profile prefixes rather than fragmenting.
- **`commons` module is per-service**, distinct from fleet-shared `ship.cars.commons:commons`. Both are named `commons`.
- **`Dockerfile-migrate`** is the "run Flyway as a separate K8s Job" pattern — keep it separate from the app `Dockerfile`.
- **Native is the production path** — `resources-config.json` is load-bearing for reflection in native mode. There is **no `quarkus-auto-reflection` dependency** here (a prior version of this shadow claimed one; corrected — reflection config is `resources-config.json` only).
- **`coverage-report` is a real module** depending on every other; don't drop it when copying (Sonar consumes its aggregate).
- Sibling `quarkus-k8s-boilerplate` is the single-module variant — pick that for tiny services, this one for full DB-backed CRUD with a real Flyway lifecycle.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/quarkus-k8s-boilerplate.md` — sibling single-module template.
- `~/projects/codebase-map/repos/shipcars-quarkus-bom.md` — the BOM (3.27.5) this template imports.
- `~/projects/codebase-map/repos/command-executor.md` / `axe-call-integration.md` / `integration-executor.md` — assumed derivations (structural match).
- `~/projects/codebase-map/domains/platform.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `CityEntity` | jpa | `db-entities` | City |
| `StateEntity` | jpa | `db-entities` | [State](../domains/entities/State.md) |
| `CityDto` | dto | `api-dtos` | City |
| `CityRevDto` | dto | `api-dtos` | CityRev |
| `CommandPubSubDto` | dto | `api-dtos` | Command |
| `StateDto` | dto | `api-dtos` | [State](../domains/entities/State.md) |
| `StateRevDto` | dto | `api-dtos` | StateRev |
<!-- entities-end -->
