---
repo: shipcars-quarkus-bom
path: ~/projects/ship-cars-usa/shipcars-quarkus-bom
stack: Java 21 / Maven BOM (`packaging=pom`) — `ship.cars.quarkus:shipcars-quarkus-bom` 3.27.5.1-SNAPSHOT, pins Quarkus platform 3.27.5
domain: platform
shape: single-module (pure BOM)
last-synced-commit: 29b25f22eb702aa8a56fa34962b2f3ef5a31f855
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# shipcars-quarkus-bom

## What it is
The fleet's **Quarkus version-of-truth BOM**. A `packaging=pom` artifact (`ship.cars.quarkus:shipcars-quarkus-bom`) that imports the Quarkus platform BOM and layers on a curated set of Quarkiverse extensions + test/build plugin versions, then republishes them under one importable POM so every downstream Quarkus repo inherits the same versions from a single import. No code — just `<dependencyManagement>` + `<pluginManagement>` + the Java-21 / Sonar settings.

At HEAD the BOM version is **3.27.5.1-SNAPSHOT** and it pins **Quarkus platform 3.27.5** (`quarkus.platform.version`). The imperative and k8s boilerplates and the Ship.Cars Quarkus extensions all track 3.27.5, which is why "the fleet is on Quarkus 3.27.5" describes the same checkpoint.

> Note: the in-repo `README.md` usage example still shows `<version>3.27.1-SNAPSHOT</version>` — that is stale doc text; the authoritative version is the `<version>` in `pom.xml` (3.27.5.1-SNAPSHOT).

## How it fits

- **What it provides:** the pinned Quarkus platform + Quarkiverse extension set + test-framework + Maven-plugin versions, importable as one BOM.
- **Compile-time consumers:** every Quarkus service in the fleet imports it at the top of its own `<dependencyManagement>` (~40 services), typically via a `${ship-cars-quarkus-bom.version}` property.
- **Consumes API of / publishes events to:** none.
- **Owns data store:** none.
- **Distribution:** GitHub Packages Maven at `maven.pkg.github.com/ship-cars-usa/shipcars-quarkus-bom`.

## Build / test / run
```
./build-project.sh
./deploy-project.sh
./mvnw clean install -DskipTests   # publish to local ~/.m2
./mvnw deploy                      # publish to GitHub Packages
```
Consumed via:
```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>ship.cars.quarkus</groupId>
      <artifactId>shipcars-quarkus-bom</artifactId>
      <version>${ship-cars-quarkus-bom.version}</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>
```

## Pinned versions (at HEAD, from `pom.xml`)

| Dependency | Version | Notes |
|---|---|---|
| **Quarkus platform** (`io.quarkus.platform:quarkus-bom`, import) | **3.27.5** | Pulls the entire `io.quarkus:*` / `io.smallrye:*` / `io.vertx:*` universe. Single biggest lever. |
| **Java** (`maven.compiler.release`) | **21** | Fleet-wide target. |
| `quarkus-logging-json` (Quarkiverse) | 3.4.0 | Structured JSON logging. |
| `quarkus-logging-manager` (Quarkiverse) | 3.4.2 | Runtime log-level admin endpoint. |
| `quarkus-google-cloud-pubsub` + `-deployment` | 2.18.0 | Native Quarkus binding for GCP Pub/Sub. |
| `quarkus-unleash` (Quarkiverse) | 1.14.0 | Feature-flag client (Unleash). |
| `quarkus-tika` (Quarkiverse) | 2.3.2 | Apache Tika content-type detection. **`commons-logging` excluded** to avoid SLF4J double-binding. |
| `quarkus-wiremock` + `-test` (Quarkiverse) | 1.6.3 | WireMock for tests (`provided` + `test`). |
| Tests: `quarkus-junit5`, `-junit5-mockito`, `-jacoco` | 3.27.5 (platform) | test scope. |

`<pluginManagement>` pins the shared toolchain: `maven-jar-plugin` 3.5.0, `maven-resources-plugin` 3.5.0, `build-helper-maven-plugin` 3.6.1, `maven-surefire-plugin` 3.5.6, `maven-deploy-plugin` 3.1.4, `jacoco-maven-plugin` 0.8.15, `sonar-maven-plugin` 5.7.0.6970. The `build-helper` config also wires `src/it/java` + `src/it/resources` as extra test source/resource roots for consumers.

## Don't-do-here / gotchas

- **BOM bumps are fleet-coordinated events.** Bumping Quarkus here cascades to every importing service. Lagging services (on older Quarkus, e.g. 3.20.x/3.15.x/3.8.x, or on Spring — a separate stack) are pinned to older BOM snapshots; each is one bump-coordination job from current.
- **No Ship.Cars extension is pinned in this BOM.** `quarkus-commons`, `quarkus-pubsub`, `quarkus-extension-persistence`, `quarkus-request-filter`, `quarkus-notification-client`, the boilerplates, etc. are **not** here — each consumer pins them in its own `<dependencyManagement>` (usually reusing the `${ship-cars-quarkus-bom.version}` property even though the BOM doesn't define those artifacts). Consequence: a service can be on BOM 3.27.5 but on `quarkus-pubsub` 3.20.x — drift between Quarkus and the Ship.Cars extensions is silent.
- **Quarkiverse versions are hand-pinned** (pubsub 2.18.0, unleash 1.14.0, tika 2.3.2, wiremock 1.6.3, logging-json 3.4.0, logging-manager 3.4.2). Bumping Quarkus does not auto-bump these; audit each against Quarkiverse periodically.
- **`commons-logging` exclusion on `quarkus-tika`** prevents an SLF4J conflict — don't remove it.
- **Distribution is GitHub Packages**, not Maven Central. "Can't resolve shipcars-quarkus-bom" locally is almost always a missing `settings.xml` credential (GitHub PAT with `read:packages`), not a missing repo.
- **README version string is stale** (3.27.1-SNAPSHOT) — trust `pom.xml`.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/quarkus-commons.md` / `quarkus-pubsub.md` / `quarkus-extension-persistence.md` — Ship.Cars extensions, separately versioned; not pinned here.
- `~/projects/codebase-map/repos/quarkus-imperative-boilerplate.md` / `quarkus-k8s-boilerplate.md` — templates that import this BOM at 3.27.5.
- `~/projects/codebase-map/repos/commons.md` — framework-neutral commons (`ship.cars.commons`), independently versioned (bom 3.33.0 in the boilerplates).
- `~/projects/codebase-map/relations/service-graph.md` — compile-time edges to this BOM.
- `~/projects/codebase-map/domains/platform.md`.
