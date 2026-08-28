---
repo: quarkus-extension-webclient
path: ~/projects/ship-cars-usa/quarkus-extension-webclient
stack: Java/Quarkus extension (runtime + deployment) — `ship.cars.quarkus.extensions.webclient:quarkus-extension-webclient` 3.27.5.1-SNAPSHOT (on shipcars-quarkus-bom / Quarkus 3.27.5), Vert.x WebClient
domain: platform
shape: multi-module (runtime + deployment)
last-synced-commit: 5e479941849417d1de7bd83a24a126877522b751
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# quarkus-extension-webclient

## What it is
**A programmatic Quarkus HTTP client** wrapping the **Vert.x Mutiny WebClient** (`io.vertx.mutiny.ext.web.client.WebClient`) — NOT MicroProfile Rest Client (it pulls `quarkus-rest-client-jackson` but the engine is Vert.x). `WebClientImpl` is a builder-style client carrying:

- **Timeout defaults** (`WebClientImpl` constants, `runtime/.../WebClientImpl.java` L34–46): `DEFAULT_CONNECT_TIMEOUT_MS=60_000`, `DEFAULT_READ_TIMEOUT_MS=30_000`, `DEFAULT_WRITE_TIMEOUT_MS=30_000`. **CRITICAL nuance:** these read/write values are applied as Vert.x **idle** timeouts (`options.setReadIdleTimeout` / `setWriteIdleTimeout`, L79–80) — plus TCP `connectTimeout` (L77). There is **NO overall request/response (call) timeout** anywhere (no `HttpRequest.timeout(...)`, no `.ifNoItem().after(...)`, no `call-timeout`). Idle timeouts fire only after N seconds of *zero socket activity*; a slow-drip / half-open peer keeps the connection alive indefinitely, so the effective call has no upper bound.
- A retry primitive built on `cars.ship.commons.errors.RetryUtils`: default 7 attempts (`DEFAULT_RETRY_MAX_ATTEMPTS=7`), 5–30 s exponential backoff (`DEFAULT_RETRY_MIN/MAX_BACKOFF`), 0.75 jitter — hand-rolled on Mutiny `Uni` (no resilience4j / MP Fault Tolerance dep).
- A per-call `WebClientCallConfig` override for retries / headers / query params (no timeout fields at call level — timeouts are client-construction-only).
- Built-in `BusinessRuleException` translation — 4xx/5xx bodies carrying `error-handling.ErrorDto` are rethrown as typed `BusinessRuleException` on the caller side via `BusinessRuleExceptionParser`.

This is **an alternative to MicroProfile's `@RegisterRestClient`** in Quarkus services. `mergeConfigs(callerConfig, DEFAULT_CONFIG)` (`WebClientConfigUtils`) fills any null field from the defaults — so a consumer that builds a `WebClientConfig` with only `objectSerializer` set silently inherits the full 60 s connect / 30 s idle / 7-retry profile. **It is "safe-by-default" only on connect + idle timeouts — NOT on total call duration**, which is unbounded (blocking callers do `uni.await().indefinitely()`, L749). Note also the extension **generates no CDI producer** — each consumer must supply its own `@Produces WebClientImpl`.

## How it fits

- **Compile-time consumers (runtime usage, verified 2026-08-28 — pom groupId `ship.cars.quarkus.extensions.webclient` AND `import ship.cars.quarkus.extensions.webclient`; count = Java files importing the runtime pkg):** 11 fleet repos —
  - `integrations-backend` (12), `saved-search-handler` (11), `loadboard-backend` (9), `integration-executor` (8), `cube` (7), `trip-planner` (5), `location-provider` (3), `command-executor` (2), `load-recommender` (2), `load-bookmark-backend` (2), `negotiations-router` (pom dep).
  - **Distinct from the Spring twin** in `spring-commons/spring-clients` (package `cars.ship.commons.spring.clients`) which `posting-backend`, `quote-manager-backend`, `inventory-backend`, `driveaway-backend`, `user-backend`, `chat-backend`, `notification-backend`, `attachment-backend`, `metadata`, etc. use instead — those match `WebClientImpl` by name but are NOT this extension.
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

Consumed via:
```xml
<dependency>
  <groupId>ship.cars.quarkus.extensions.webclient</groupId>
  <artifactId>runtime</artifactId>
  <version>${shipcars-quarkus-bom.version}</version>
</dependency>
```

## Key abstractions

- **`WebClientImpl`** (`runtime/.../WebClientImpl.java`) — the main entry point. Constructor takes a `Vertx` and a `WebClientConfig`; internally `mergeConfigs(userConfig, DEFAULT_CONFIG)` so any null value falls through to the safe default. Exposes blocking + non-blocking (`getAbsNonBlocking`, `postJsonAbs`, …) variants returning `Uni<T>`. Generic-T responses go through `ClassTypeProvider<T>` from `commons`.
- **`WebClientImpl.DEFAULT_CONFIG`** — the fleet-baseline numbers documented above. Caller doesn't have to know about them; just constructing a client with a minimal config is safe.
- **`WebClientConfig`** — caller-supplied config (timeouts, retry policy, default headers, on-which-exceptions-retry predicates). All numeric fields validated via `SCObjectUtils.validateNullOrPositive(...)` — nulls allowed (fall through to defaults), but negatives rejected at construction.
- **`WebClientCallConfig`** — per-call override (record). Carries only headers, query, and retry overrides — **no timeout fields**, so per-call timeout tuning is not possible; timeouts are fixed at client construction.
- **`WebClientConfigUtils`** — merges call/client/DEFAULT_CONFIG (null-coalescing: an omitted field silently falls back to the default) and validates (`retryMaxBackoff > retryMinBackoff`; timeouts null-or-positive).
- **`HttpStatusUtils.isErrorStatusCode(...)`** — utility that callers use to decide whether to treat a 2xx/3xx as success.
- **`BusinessRuleExceptionParser`** — extracts `BusinessRuleException` payloads from downstream HTTP error bodies; the client throws the typed exception on the caller's thread.
- **`UriUtils`** — URL composition helpers (defaults scheme to HTTPS, via Apache `URIBuilder`).
- **`QuarkusWebClientProcessor`** (`deployment/`) — the only build step: registers `FeatureBuildItem("ship-cars-extension-webclient")` and `ReflectiveClassBuildItem`s for `BusinessRuleException`, `ErrorDto`, `WebClientCallConfig`, `WebClientConfig`. **No CDI producer is generated** — consumers must write their own `@Produces WebClientImpl`.

## Don't-do-here / gotchas

- **The `DEFAULT_CONFIG` numbers are aggressive AND the read/write timeouts are idle-only.** 7 retries × 5–30 s backoff means a single failing call occupies a caller thread for minutes; worse, because the "read/write timeout" is a Vert.x *idle* timeout (not a total-call timeout) and blocking callers do `await().indefinitely()`, a downstream that trickles bytes can hang a call **unbounded** — the "~5 minutes" a reader might estimate from the numbers is optimistic. This is the fleet retry-without-timeout anti-pattern manifesting even in the "safe path" client. Services on the request path should override `retryMaxAttempts` (3 is a reasonable ceiling) and, since there is no call-timeout knob, wrap the returned `Uni` with their own `.ifNoItem().after(...)` bound.
- **`mergeConfigs(caller, DEFAULT_CONFIG)` is the safety net, not a contract.** A caller can still pass an `Integer` 0 / 1 ms for any timeout and bypass the safety. The validation only rejects negatives. Audit any new `WebClientConfig.builder().connectTimeoutMs(...)` call for "is this number sensible?"
- **Not the same path as `@RegisterRestClient`.** Services that use the MicroProfile annotation path do NOT inherit any of these defaults. The fleet's REST-client timeout gap (33 of 36 missing timeouts in `rest-client-registry.md`) is a story about MicroProfile rest-client config, not this extension. Recommending "switch to WebClientImpl" is one viable remediation; the other is fleet-wide `quarkus.rest-client.<key>.connect-timeout` / `read-timeout` defaults via `quarkus.config.locations`.
- **Vert.x WebClient is reactive under the hood.** Even though `getAbs(...)` returns synchronously via `awaitAsyncResult`, the call still passes through the Vert.x event loop. Blocking-thread callers may pay a context-switch cost vs. `@RegisterRestClient`'s Apache HttpClient5 path. For very high-throughput servers this can matter; for most fleet services it doesn't.
- **Retry replays the entire request body.** `MultipartForm` / large JSON bodies will be re-serialized and re-sent on each retry — sufficient backoff is critical to avoid amplifying load on a struggling downstream.
- **The retry predicate stack** (`retryOnExceptionClasses`, `retryOnExceptionClassNames`, `retryOnExceptionMessages`, `retryOnBusinessRuleExceptions`, `retryOnExceptions`) is OR'd. **Default behavior retries on any IOException / connect timeout / read timeout**, which is desirable for transient failures but can mask a real downstream outage (the caller appears merely "slow"). Pair generous retries with a circuit breaker if the downstream is known-flaky.
- **`BusinessRuleException` translation requires the upstream to use `error-handling.ErrorDto`.** If a downstream returns its own custom error JSON, the parser silently falls back to a raw HTTP error — the caller has to fall back to `HttpStatusUtils` checks. Coordinate error shapes across service boundaries.
- **Not tied to OTel.** This extension doesn't auto-instrument spans. OTel propagation comes from `quarkus-commons` / `quarkus-opentelemetry`; if a service doesn't depend on those, calls through `WebClientImpl` may not be traced.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/commons.md` — depends on `error-handling`'s `RetryConfig` + `BusinessRuleException`.
- `~/projects/codebase-map/repos/spring-commons.md` — its `WebClientImpl` is the **Spring-side analogue**, but unlike this Quarkus version it does **not** default timeouts; consumers must configure them programmatically (only 2 fleet services actually do).
- `~/projects/codebase-map/relations/rest-client-registry.md` — quantifies the `@RegisterRestClient` gap that this extension's `DEFAULT_CONFIG` would close if more services adopted it.
- `~/projects/quarkus-rest-client-timeout-anti-pattern.md` — canonical write-up of the retry-without-timeout anti-pattern.
- `~/projects/codebase-map/domains/platform.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `WebClientCallConfig` | dto | `runtime` | WebClientCallConfig |
| `WebClientConfig` | dto | `runtime` | WebClientConfig |
<!-- entities-end -->
