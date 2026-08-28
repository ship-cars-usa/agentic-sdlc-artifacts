---
repo: quarkus-locationprovider-client
path: ~/projects/ship-cars-usa/quarkus-locationprovider-client
stack: Java 21 / Quarkus 3.27.5 extension (runtime + deployment) — `ship.cars.quarkus.extensions.locationprovider`, MicroProfile REST Client (reactive) + SmallRye Fault Tolerance
domain: operations
shape: multi-module (runtime + deployment + coverage-report)
last-synced-commit: 5762e8144c83ba82bd18767114c4a5a9e0173ba5
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# quarkus-locationprovider-client

## What it is
The Quarkus typed-client extension around the `location-provider` REST service. Consumers `@Inject LocationProviderClient` instead of hand-rolling a `@RegisterRestClient` interface, and get typed DTOs back for the six operations `location-provider` exposes (all under `/api/v2`, per `LocationProviderRestClient`):

- `getDirections` — `RouteQueryDto` → `DirectionsResponseDto` (route geometry + distance + duration).
- `getPlaceLocation` — geocode/locations lookup → `GeocodeDetailsResponseDto`.
- `getAutocompletePredictions` — text prefix → `List<AutocompletePlaceDto>`.
- `searchByZipCityState` — custom-autocomplete ZIP/city/state lookup → `List<LocationInfoDto>`.
- `getStates` — `List<StateInfoDto>` (US states).
- `optimizeTours` — `OptimizeToursRequestDto` → `OptimizeToursResponseDto` (Google Route Optimization surface).

Every operation carries a `ServiceNameEnum` argument sent as the `X-Service-Name` header (`RoutesConfig.SERVICE_HEADER`), which `location-provider` uses to attribute usage / pick provider.

Root pom version at HEAD is **3.27.5** (aligned with `shipcars-quarkus-bom` 3.27.5). It pulls DTOs from the separate `ship.cars.locationprovider` artifact pinned at `ship-cars-location-provider.version=3.28.0`, and `ship-cars-commons` 3.33.0.

## How it fits
- **What it provides:** a single injectable `LocationProviderClient` bean plus the retry/error-mapping policy baked into `LocationProviderRestClient`. Consumers avoid re-declaring the REST client and get fleet-standard error translation for free.
- **Who consumes it (compile-time):** ~5 fleet repos reference `ship.cars.quarkus.extensions.locationprovider` in their poms (e.g. `trip-planner`, `uship-quotes`). Note that several other services that talk to `location-provider` do so via their **own** `@RegisterRestClient` declarations and bypass this extension entirely — so the extension is *not* the only path to `location-provider` (see `relations/service-graph.md`).
- **Consumes API of:** `location-provider` (configKey `location-provider`, base URL from `quarkus.rest-client.location-provider.url`).
- **Publishes events to:** none.
- **Owns data store:** none.
- **Depends on (compile-time):** `ship.cars.locationprovider` DTO artifact (3.28.0) — a separate DTO library, not `models-lib`; every consumer transitively pulls it too.

## Build / test / run
```
./mvnw clean install -DskipTests
./mvnw test
./deploy-project.sh      # deploy runtime + deployment to GitHub Packages (Argo CD does this on master)
```
`GITHUB_TOKEN` / `GITHUB_READ_TOKEN` / `GITHUB_USERNAME` must be exported. Commit-message hook enforces `LITE-*` / `Merge` prefix.

Consumed via:
```xml
<dependency>
  <groupId>ship.cars.quarkus.extensions.locationprovider</groupId>
  <artifactId>runtime</artifactId>
  <version>${ship-cars-locationclient.version}</version>
</dependency>
```
Required config (the only extension property, per README):
```
quarkus.rest-client.location-provider.url=https://...
```

## Key abstractions
- `LocationProviderClient` — `runtime/.../client/LocationProviderClient.java` — public interface (6 methods); what consumers inject.
- `LocationProviderClientImpl` — `runtime/.../client/impl/LocationProviderClientImpl.java` — `@ApplicationScoped`, delegates each method to the REST client, adds debug/trace logging; no business logic.
- `LocationProviderRestClient` — `runtime/.../client/LocationProviderRestClient.java` — `@RegisterRestClient(configKey = "location-provider")` MicroProfile client. Carries the JAX-RS + fault-tolerance annotations on every method, plus a `static @ClientExceptionMapper toException(Response)` that turns 4xx/5xx into `BusinessRuleException` via `commons.errors.ErrorUtils.toBusinessRuleException`.
- `LocationProviderClientProcessor` — `deployment/.../LocationProviderClientProcessor.java` — build-step processor registering the extension.
- **Retry policy on every endpoint** (unchanged from prior sync):
  ```
  @Retry(delayUnit = SECONDS, delay = 1, maxRetries = 7)
  @RetryWhen(exception = IsRetryable.class)
  @ExponentialBackoff
  ```
  `IsRetryable` (`commons.errors.RetryUtils.IsRetryable`) filters retry-eligible exceptions; `@ExponentialBackoff` (SmallRye) shapes delays. **No `@Timeout`, no `@CircuitBreaker`, and no connect/read-timeout in the configKey by default.**

## Don't-do-here / gotchas
- **Retry-without-timeout on every method.** 7 retries with 1s exponential backoff and no `@Timeout` means the wall-clock budget per call is bounded only by `location-provider`'s response behavior — under a slow-but-not-down upstream a single call can burn well into the minutes. Set `quarkus.rest-client.location-provider.connect-timeout` + `read-timeout` in **every consumer's** `application.properties`; the extension sets no defaults. Canonical case of the fleet anti-pattern (`~/projects/quarkus-rest-client-timeout-anti-pattern.md`).
- **No `@CircuitBreaker`.** A `location-provider` outage is retried to exhaustion on every call; under burst the impact multiplies. Consider adding one at consumer level if the upstream gets flaky.
- **Two parallel paths to `location-provider`** — this extension (retries + error translation) vs. per-consumer `@RegisterRestClient`. Retry policy, error shape, and DTO version pinning differ between them; when a call site misbehaves, first determine which path it's on.
- **Separate DTO artifact** (`ship.cars.locationprovider` 3.28.0) — not `models-lib`. Bumping it requires coordinated version pins across consumers; watch for DTO surface drift when a consumer pins an older extension against a newer `location-provider` service.
- `LocationProviderClientImpl` is `@ApplicationScoped` (single shared instance) — fine because it holds no mutable state, but per-request configuration would need rework.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/location-provider.md` — the upstream service (HikariCP `max-size=4`; cache-miss-then-Maps risk).
- `~/projects/quarkus-rest-client-timeout-anti-pattern.md` — canonical write-up of the retry-without-timeout shape this client exhibits.
- `~/projects/codebase-map/relations/service-graph.md` — `location-provider` inbound REST edges across the fleet.
- `~/projects/codebase-map/domains/operations.md`.
