---
repo: commons
path: ~/projects/ship-cars-usa/commons
stack: Java 21 / Maven multi-module (10 modules under `ship.cars.commons:libs` 3.34.0-SNAPSHOT)
domain: platform
shape: multi-module
last-synced-commit: 10dbbbf0071df3de6fa2a0b8077855430e651a4e
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# commons

## What it is
The fleet's **framework-neutral parent commons library** — `ship.cars.commons:libs`. Holds utilities, DTOs, error/retry primitives, Datadog wiring, Temporal helpers, and reusable test scaffolding that any Java service (Quarkus *or* Spring) can compile against. Companion to two more specialized commons libraries:

- `quarkus-commons` (separate repo) — Quarkus-specific stuff (OTel/MDC bridge, structured JSON logging).
- `spring-commons` (separate repo) — Spring-specific stuff (`WebClientImpl`, `GlobalExceptionHandler`, `PubSubConsumer` template).

README explicitly documents the "Commons Split in 2024" — this repo is the framework-neutral nucleus left after the Quarkus and Spring extractions.

## How it fits

- **Compile-time consumers:** every Java service in the fleet (Quarkus + Spring) plus all three Quarkus extension repos (`quarkus-extension-webclient`, `quarkus-pubsub`, `quarkus-extension-persistence` all import `ship.cars.commons:bom`).
- **Consumes API of:** none — pure library.
- **Publishes events to:** none.
- **Owns data store:** none.

## Build / test / run
```
./mvnw clean install -DskipTests          # publishes to local Maven repo
./mvnw test
./build-project.sh                        # CI-style build script
./deploy-project.sh                       # publishes to internal Maven repository
```

Maven coordinates downstream consumers import:
```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>ship.cars.commons</groupId>
      <artifactId>bom</artifactId>
      <version>${ship-cars-commons.version}</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>
```

## Module map

| Module | Role |
|---|---|
| `bom` | Maven BOM — pins versions for the other modules + transitive third-party deps (`jakarta.validation-api`, `slf4j-api`, `logback-classic`). Single import for downstream consumers. |
| `commons` | Framework-neutral helpers + DTOs. Most fleet code touches this. |
| `commons-datadog` | Datadog APM/metrics integration helpers. |
| `error-handling` | The fleet's **error and retry framework**: `ErrorCode`, `ErrorDto`, `BusinessRuleException`, `ErrorUtils`, `RetryConfig`, `RetryUtils`, plus pluggable `ExceptionMessageExtractor`s for Constraint / gRPC / business-rule exceptions. Imported by `quarkus-extension-webclient` for its retry-on-business-rule logic. |
| `temporal-commons` | Helpers for Temporal workflow services (used by `posting-backend`, `loadboard-backend`, `inventory-backend`). |
| `test`, `test-data`, `test-error-handling`, `test-temporal`, `test-wiremock` | Reusable test scaffolding — fixtures, ErrorCode test helpers, Temporal test harnesses, WireMock setup. Imported as `<scope>test</scope>` by service repos. |

## Key abstractions

- **`cars.ship.commons.errors.ErrorCode`** + **`GeneralErrorCode`** — fleet-wide error-code enum; each repo extends with its own domain codes. `BusinessRuleException` carries the code through the call stack.
- **`cars.ship.commons.errors.RetryConfig`** + **`RetryUtils.isRetryableException(...)`** — retry policy primitives reused by `quarkus-extension-webclient.WebClientImpl` and ad-hoc retry call sites.
- **`cars.ship.commons.errors.ExceptionMessageExtractor`** + per-exception-type extractors (`ConstraintViolationExceptionMessageExtractor`, `GrpcStatusRuntimeExceptionMessageExtractor`, `BusinessRuleExceptionMessageExtractor`) — normalizes error messages from heterogeneous downstream libraries into a single shape.
- **`cars.ship.commons.MdcKeys`** — canonical MDC key names (correlation ID, user ID, …). Every structured-log message should set these via `MDC.put(MdcKeys.X, …)` to keep log shape consistent.
- **`cars.ship.commons.dtos.apigateway.UserContextDto`** — the typed user-context payload propagated through `api-gateway` → service. Any service that needs caller identity reads it from this shape.
- **`cars.ship.commons.dtos.IDResponseDto` / `PageDto` / `OptionalFieldDto` / `UrlResponseDto`** — wire-format DTOs that REST endpoints return; cross-repo callers depend on these field names.
- **`cars.ship.commons.jackson.JacksonMixedCaseDeserializer`** — special-case Jackson handling for legacy mixed-case JSON (e.g. fields like `UserId` instead of `userId`). Don't strip it; some upstream / external sources still emit mixed case.
- **`cars.ship.commons.SCCsvSanitizer`** + **`SCImageValidatorUtils`** + **`SCMimeTypeUtils`** — security-adjacent helpers (CSV-injection sanitization, image-content validation, MIME-sniffing). New file-handling code paths should reach for these rather than rolling their own.
- **`cars.ship.commons.SCTimeUtils`** + **`USZipCodeToTimeZoneUtils`** + **`USStateEnum`** — US-locale primitives. Any new feature that bakes in US-only assumptions should reference these so the assumption is at least discoverable.
- **`cars.ship.commons.ObjectSerializer`** — Jackson-backed serializer abstraction. `quarkus-extension-webclient.WebClientConfig` takes this as a constructor arg so all webclient calls use the same JSON behavior as the service's own serialization.

## Don't-do-here / gotchas

- **Public API stability is load-bearing.** Every Java service in the fleet recompiles against this. A breaking change to `ErrorCode`, `UserContextDto`, `IDResponseDto`, or any `SC*Utils` ripples through every consumer. Treat method signatures and DTO field names as semi-versioned: deprecate first, remove a major later.
- **Pre-2024 the repo carried Quarkus and Spring specifics** — that split is now done, but cross-references in older service code may still expect classes that have moved to `quarkus-commons` or `spring-commons`. If a class isn't where you expect, check the other two repos.
- **`commons-datadog` is opt-in** — services that don't include it run without Datadog integration. Don't assume Datadog tracer/metrics methods are universally available across the fleet.
- **`temporal-commons` is only useful when the consuming service runs Temporal workers.** Don't add this dependency to services that don't.
- **`error-handling` lives in its own module** to avoid a hard dependency on the wider `commons` set for low-level libraries (`quarkus-extension-webclient`'s `BusinessRuleExceptionParser` reaches only into `error-handling`, not the whole commons surface). Preserve that split when adding new error primitives — don't promote them to `commons` unless they're truly framework-neutral primitives.
- **No retries policy lives here** — `RetryConfig`/`RetryUtils` are the primitives, but the **defaults** (retry-attempts, backoff, jitter) are set by each caller. `quarkus-extension-webclient.WebClientImpl.DEFAULT_CONFIG` sets fleet-baseline defaults for the WebClient path; there is no analogue for `@RegisterRestClient` callers.
- **Test modules are `<scope>test</scope>` in consumers** — don't accidentally pull them into runtime. If a class needs to be runtime-visible, promote it from `test` → `commons` (or `error-handling`).

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/quarkus-commons.md` — Quarkus-specific commons (OTel/MDC bridge, structured-JSON fix). **Does not** set baseline REST-client timeouts; that gap is the systemic risk in `rest-client-registry.md`.
- `~/projects/codebase-map/repos/spring-commons.md` — Spring-specific companion (`WebClientImpl`, `GlobalExceptionHandler`, `PubSubConsumer` template).
- `~/projects/codebase-map/repos/quarkus-extension-webclient.md` — depends on `error-handling`'s `RetryConfig` + `BusinessRuleException` extractors; provides the fleet's safe-default Quarkus REST client path.
- `~/projects/codebase-map/relations/rest-client-registry.md` — quantifies the gap left by no fleet-wide timeout defaults here.
- `~/projects/codebase-map/domains/platform.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `BusinessRuleException` | dto | `error-handling` | BusinessRuleException |
| `ClassTypeProvider` | dto | `commons` | ClassTypeProvider |
| `CompanyContextDto` | dto | `commons` | CompanyContext |
| `ContextDto` | dto | `commons` | Context |
| `IDResponseDto` | dto | `commons` | ID |
| `MdcData` | dto | `commons-datadog` | MdcData |
| `ObjectSerializerImpl` | dto | `commons` | ObjectSerializerImpl |
| `OptionalFieldDto` | dto | `commons` | OptionalField |
| `PaymentDetailsDto` | dto | `commons` | PaymentDetails |
| `RetryConfig` | dto | `error-handling` | RetryConfig |
| `SCImageValidatorUtils` | dto | `commons` | SCImageValidatorUtils |
| `USRealAddress` | dto | `test-data` | USRealAddress |
| `USRealAddressCoordinatesDto` | dto | `test-data` | USRealAddressCoordinates |
| `USRealAddressDto` | dto | `test-data` | USRealAddress |
| `UnicodeToSafePathAsciiMap` | dto | `commons` | UnicodeToSafePathAsciiMap |
| `UrlResponseDto` | dto | `commons` | Url |
| `UserContextDto` | dto | `commons` | UserContext |
| `WorkflowExecutionTime` | dto | `temporal-commons` | WorkflowExecutionTime |
<!-- entities-end -->
