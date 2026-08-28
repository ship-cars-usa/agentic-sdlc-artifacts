---
repo: quarkus-auto-reflection
path: ~/projects/ship-cars-usa/quarkus-auto-reflection
stack: Java/Quarkus extension (runtime + deployment) — `ship.cars.quarkus.extensions.reflection:quarkus-auto-reflection` 3.27.5 (on shipcars-quarkus-bom / Quarkus 3.27.5)
domain: platform
shape: multi-module (runtime + deployment + coverage-report)
last-synced-commit: 01577ba8b318e705d5f9081deed3dc9efd61e8c0
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# quarkus-auto-reflection

## What it is
The fleet's **native-image reflection-config helper**. Quarkus native binaries (compiled via GraalVM Mandrel) need an explicit list of classes that should be reflectively accessible at runtime — Jackson DTOs, JPA entities, Hibernate proxies, anything looked up via `Class.forName(...)` or `Method.invoke(...)`. The native compiler can auto-detect many of these, but **fleet DTOs and reflection-driven serializers slip through the detector**. This extension provides a simple config-driven way to register them.

Surface is minimal — a single runtime config class:

```java
@ConfigMapping(prefix = "ship.cars.reflection")
@ConfigRoot(phase = ConfigPhase.BUILD_AND_RUN_TIME_FIXED)
public interface ReflectionConfig {
  Optional<Set<String>> className();    // exact classes to register
  Optional<Set<String>> packageName();  // entire packages to scan + register
}
```

The deployment-time processor (`deployment/.../ReflectionProcessor.java`) reads `ship.cars.reflection.class-name[*]` and `ship.cars.reflection.package-name[*]` from `application.properties` and emits Quarkus `ReflectiveClassBuildItem`s for each match — every item is registered with `.constructors().fields().methods().serialization()` (full reflective access + Jackson serialization). Resolution uses the Jandex `CombinedIndexBuildItem`: `class-name[i]` looks up an exact `ClassInfo`; `package-name[i]` matches **by prefix** — `clazz.name().packagePrefix().startsWith(packageName)` — so it now registers the package **and all its sub-packages** (the build log says "including sub-packages").

This is **build-time-fixed** (`ConfigPhase.BUILD_AND_RUN_TIME_FIXED`), so changing the property list requires a rebuild + redeploy, not a runtime config change.

> Drift note (2026-08-28): the README still says sub-packages are *not* reflected and must be declared separately. The **source contradicts this** — `handleReflectionByPackageName` matches on `startsWith`, so sub-packages ARE included. Trust the code; the README is stale.

## How it fits

- **Compile-time consumers (15 Quarkus services, verified 2026-08-28 by grepping `ship.cars.reflection.{package,class}-name` in `application.properties`):** `aaag-integration`, `axe-call-integration`, `bi-databricks-backend`, `command-executor`, `dataone`, `fraud-detector`, `integration-executor`, `integrations-backend`, `invoices`, `metadata`, `payment-backend`, `pusher`, `syncer`, `synclink-backend`, and the extension's own `deployment/src/test`. **The canonical example** is `command-executor`'s `application.properties` which carries `ship.cars.reflection.package-name[0..25]` covering 26 Posting / commons DTO packages.
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

Consumer-side usage in `application.properties`:

```properties
ship.cars.reflection.package-name[0]=cars.ship.posting.dtos
ship.cars.reflection.package-name[1]=cars.ship.posting.dtos.deprecated.v1
ship.cars.reflection.package-name[2]=cars.ship.posting.dtos.deprecated.v1.enums
...
ship.cars.reflection.package-name[25]=cars.ship.commons.dtos
ship.cars.reflection.class-name[0]=cars.ship.example.SpecificDto
```

## Key abstractions

- **`runtime/.../ReflectionConfig.java`** — the entire runtime surface (single config interface). No Java logic — it's just declarative.
- **`deployment/`** — where the actual `ReflectiveClassBuildItem` generation happens at build time (Quarkus deployment-module convention).

## Don't-do-here / gotchas

- **Native builds silently fail at runtime if a DTO isn't registered.** Symptom: `ClassNotFoundException` or `NoSuchMethodException` thrown from Jackson deserialization (or any reflection-based code), but **only in the native binary** — JVM mode works fine. Add the missing package or class to `ship.cars.reflection.{class-name,package-name}[*]` and rebuild.
- **Package-name registration is greedy AND recursive.** `package-name[i]=cars.ship.posting.dtos` registers every class in that package *and every sub-package* (prefix match), each with constructors+fields+methods+serialization. That's usually what you want, but it inflates native-binary size. Use `class-name[i]` for surgical inclusion when binary size matters. (Beware prefix collisions: `cars.ship.post` would also pull in `cars.ship.posting.*`.)
- **`BUILD_AND_RUN_TIME_FIXED` config phase** means you can't change the reflection list at runtime — a config change requires rebuild. Don't try to dynamically register classes; that's not what this extension does.
- **The deployment module is the load-bearing one.** A pure runtime change won't propagate into the native binary's reflection config unless the deployment module's build-time generator re-runs. CI cache invalidation matters here.
- **Test parity: JVM tests pass, native tests can still fail.** Tests should run in native mode for the consuming service before treating "reflection-config is correct" as proven. Use `./mvnw clean verify -Pnative` (per the boilerplate's pattern).
- **Stale entries don't error.** Adding a `package-name[i]=cars.ship.deleted.package` that no longer exists in the source tree is silently ignored. Periodically audit the entries against actual code; orphaned ones are dead weight in the binary.
- **No fleet-wide reflection-config defaults.** Each consumer maintains its own list; no shared file at this layer. If the fleet wants to ensure "every Quarkus native service registers `cars.ship.commons.dtos`," that convention is by-copy not by-inheritance. Worth a follow-up if reflection-config drift surfaces as a fleet incident.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/command-executor.md` — the canonical example (26 reflection-package entries in its `application.properties`).
- `~/projects/codebase-map/repos/quarkus-imperative-boilerplate.md` — the boilerplate-template that drops in the standard reflection-config block when a new service is scaffolded.
- `~/projects/codebase-map/repos/shipcars-quarkus-bom.md` — pins the Mandrel native-builder version (`23.1.8.0-Final-java21`).
- `~/projects/codebase-map/relations/service-graph.md` — compile-time-edges row.
- `~/projects/codebase-map/domains/platform.md`.
