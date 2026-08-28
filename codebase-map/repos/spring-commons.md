---
repo: spring-commons
path: ~/projects/ship-cars-usa/spring-commons
stack: Java 21 / Spring Boot 3.2.12 / Maven multi-module — `ship.cars.spring.commons:libs` 3.35.1-SNAPSHOT
domain: platform
shape: multi-module (15 poms, 14 modules)
last-synced-commit: 0eeed7b5bf51b668e1c1e1eb91b11ff5d234fb16
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# spring-commons

## What it is
Shared Spring Boot library suite — 14 child modules — consumed by every Spring service in the fleet. Provides global error handling, REST-client baseline (WebClient with explicit timeout/retry knobs), Pub/Sub consumer template, structured-JSON logging, Keycloak resource-server wiring, and a dedicated BOM (`spring-bom`) for transitive dependency management. GroupId `ship.cars.spring.commons` (artifactId `libs`). Java 21, Maven 3.9.16, Spring Boot 3.2.12, Spring Security 6.2.8. Current version: 3.35.1-SNAPSHOT.

## How it fits
- Consumed by: at least 12 confirmed Spring services in the fleet — `chat-backend`, `autoims-backend`, `driveaway-backend`, `inventory-backend`, `loadbuilder-backend`, `notification-backend`, `posting-backend`, `public-tracking-backend`, `quote-manager-backend`, `user-backend`, plus the 7 Spring-misclassified-as-Quarkus repos identified during Phase 2.
- Publishes events to: n/a (compile-time library + auto-configs)
- Owns no runtime; pure library: false (nuance) — exports starters and auto-configs (`spring-boot-starter-webflux`, `spring-boot-starter-security`, `spring-cloud-gcp-starter-pubsub`) that consumers register at runtime.

## Build / test / run
```
./mvnw -s .mvn/settings.xml test                                 # unit tests
./mvnw -s .mvn/settings.xml -pl spring-clients test              # one module
./mvnw -s .mvn/settings.xml test -Pintegration-tests
./mvnw -s .mvn/settings.xml clean deploy                         # GitHub Packages
./mvnw -s .mvn/settings.xml versions:display-dependency-updates
```

## Key abstractions / what it provides
- `WebClientImpl` + `WebClientConfig` — `spring-clients/src/main/java/cars/ship/commons/spring/clients/` — fluent ReactorNetty HTTP client with explicit `connectTimeoutMs`, `readTimeoutMs`, `responseTimeoutMs`, `writeTimeoutMs`, `retryMaxAttempts`, `retryMinBackoff`, `retryMaxBackoff`, `retryJitterFactor`, MDC context propagation, structured logging.
- `GlobalExceptionHandler` — `spring-error-handling/src/main/java/cars/ship/commons/spring/errors/GlobalExceptionHandler.java` — `@ControllerAdvice` intercepting all Spring exceptions; delegates to `ErrorResolverImpl`, transforms to `ErrorDto`, registers per-error-code Prometheus counters, gracefully handles client disconnects, obfuscates sensitive messages.
- `BusinessRuleExceptionFilter` — `spring-error-handling/src/main/java/cars/ship/commons/spring/errors/BusinessRuleExceptionFilter.java` — servlet filter that catches `BusinessRuleException`, preserves MDC, forwards to the global handler.
- `PubSubConsumer` (abstract base) — `spring-pubsub-client-impl/src/main/java/cars/ship/commons/spring/pubsub/client/impl/PubSubConsumer.java` — **the canonical "good template"**: wraps message processing in `executeWithNewMdcData()`, skips when `DataMigrationInProgressService` reports an in-flight schema migration, calls `ack()` / `nack()` correctly, emits a lost-message counter every 50 messages.
- `WebKeycloakSecurityConfig` + `WebPublicSecurityConfig` + `SecurityUser` — `spring-rest-api-config/src/main/java/cars/ship/commons/spring/rest/security/` — Keycloak OAuth2 resource-server wiring with a dual-config pattern for public-vs-secured endpoints; `RequestResponseLoggingFilter` logs inbound URI + response status + user/company MDC.
- `SCStructuredArgument` — `spring-commons/src/main/java/cars/ship/commons/spring/utils/SCStructuredArgument.java` — wraps `logstash-logback-encoder` (7.4) for structured JSON field emission with SLF4J markers + MDC.
- `TransactionalExecution`, `TransactionalBatchesExecution` — `spring-commons/src/main/java/cars/ship/commons/spring/services/` — safe batch JPA wrappers with rollback semantics. `integrations-backend` uses these (correctly outside HTTP calls; the QuickBooks bug is the exception that proves the rule).
- `CheckSelfActuatorHealth` — `spring-actuator/src/main/java/cars/ship/commons/spring/actuator/CheckSelfActuatorHealth.java` — Spring Boot Actuator health endpoint.

## Don't-do-here / gotchas / conventions imposed on consumers
- **REST-client timeouts are NOT defaulted** — `WebClientImpl` requires explicit `connectTimeoutMs` / `readTimeoutMs` / etc. per call site. Same systemic gap as `quarkus-commons`. Pair both repos with a baseline-properties module.
- **Retry jitter is opt-in, off by default** — `retryJitterFactor` defaults to `null`; if set, must be `>0 && ≤1`. Most services don't set it.
- **Pub/Sub consumers MUST extend `PubSubConsumer`** — don't call Google Cloud PubSub API directly. The base class handles MDC, data-migration skip, safe ack/nack. Skipping it leads to the `LogytextPubSubConsumer` anti-template (silent drop on exception).
- **`spring-bom` must be imported FIRST** — any service using spring-commons must `<scope>import</scope>` `spring-bom:3.35.1-SNAPSHOT` in `<dependencyManagement>` before pulling individual modules, or Spring Security / Keycloak version conflicts arise.
- **Keycloak versions in spring-bom are pinned but diverged** — `keycloak-admin-client:26.0.11` and `keycloak-adapter-bom:25.0.6` are different majors. Consumers must not override either without coordination.
- **`spring-data-envers` is declared in spring-bom but commons exposes no Envers base class** — soft-delete and multi-tenancy are *not* provided. Consumers wire these themselves.
- **No JPA base entity / no `@Version` base class here.** spring-commons ships no `@MappedSuperclass` optimistic-locking base — the fleet-wide "inert `@Version` (wrong import)" pattern is a *consumer-side* defect (see the @Version optimistic-lock fleet audit), not something originated or fixed in this library. Don't expect a shared entity superclass from spring-commons.
- **Hibernate 6.6.54.Final, JPA 3.1 (`jakarta.*`)** — pinned in spring-bom.
- **`DataMigrationInProgressService`** is referenced by both error-handling and pubsub layers; consumers performing rolling schema migrations pull `spring-data-migration` and `spring-data-migration-interfaces`.
- **Trust the pom for the version** — root pom is 3.35.1-SNAPSHOT at HEAD; the `CLAUDE.md`/`README.md` don't pin a current version number, only the upgrade procedure.

## Relevant ADRs / docs
- `README.md` — release/version process.
- `spring-bom/pom.xml` — comprehensive dependency pinning (Spring Boot 3.2.12, Spring Security 6.2.8, Hibernate 6.6.54.Final, keycloak-admin-client 26.0.11, keycloak-adapter-bom 25.0.6, Logstash 7.4, Micrometer 1.12.13, Flyway 9.22.3 — note: 9.x, pre-Flyway-10; Maven 3.9.16).
- `~/projects/quarkus-fleet-review-2026-05-07.md#4-chat-backend` — the swallow-and-log anti-pattern in `chat-backend.NotificationServiceImpl.broadcastChanges()` is *not* a `spring-commons` issue; commons provides the right primitives, the consumer didn't use them.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `DataMigrationVersion` | jpa | `spring-data-migration` | DataMigrationVersion |
| `BatchConfig` | dto | `spring-commons` | BatchConfig |
| `CheckSelfActuatorHealth` | dto | `spring-actuator` | CheckSelfActuatorHealth |
| `ContextAuthRequestForwardFilter` | dto | `spring-rest-api-config` | ContextAuthRequestForwardFilter |
| `DataMigrationServiceImpl` | dto | `spring-data-migration` | DataMigrationServiceImpl |
| `DateTimeFetcherService` | dto | `spring-commons` | DateTimeFetcherService |
| `FileContentDto` | dto | `spring-gcp-storage-client-impl` | [FileContent](../domains/entities/FileContent.md) |
| `GlobalExceptionHandler` | dto | `spring-error-handling` | GlobalExceptionHandler |
| `OAuth2Config` | dto | `spring-clients` | OAuth2Config |
| `OpenApiV3Config` | dto | `spring-rest-api-config` | OpenApiV3Config |
| `ProxySettings` | dto | `spring-clients` | ProxySettings |
| `PubSubPublisherFactory` | dto | `spring-pubsub-client-impl` | PubSubPublisherFactory |
| `RequestResponseLoggingFilter` | dto | `spring-rest-api-config` | RequestResponseLoggingFilter |
| `SecurityUser` | dto | `spring-rest-api-config` | SecurityUser |
| `TrustedEndpointsConfig` | dto | `spring-rest-api-config` | TrustedEndpointsConfig |
| `WebClientCallConfig` | dto | `spring-clients` | WebClientCallConfig |
| `WebClientConfig` | dto | `spring-clients` | WebClientConfig |
| `WebClientImpl` | dto | `spring-clients` | WebClientImpl |
| `WebKeycloakSecurityConfig` | dto | `spring-rest-api-config` | WebKeycloakSecurityConfig |
<!-- entities-end -->
