---
repo: command-executor
path: ~/projects/ship-cars-usa/command-executor
stack: Java/Quarkus 3.27.5 (Java 21, multi-module, native-buildable)
domain: integrations
shape: multi-module
last-synced-commit: 6596a5dc4a9972671a14534ebe97f6dfbe07be54
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# command-executor

## What it is
A Pub/Sub-driven **inbound integration command processor** that consumes webhook-shaped events from four external auto-transport platforms and turns them into Ship.Cars-side `CreateQuoteAndOrderDto` actions, created through the `impersonator` so each order is attributed to the right Ship.Cars user. Listens on `:7071` (test 7072). Designed for native-image production builds (Mandrel/GraalVM, Java 21). **Version note: bumped from the 3.20.x cohort to Quarkus 3.27.5** — no longer a laggard.

Each integration is its own `services/.../<integration>/` package with a `*PubSubListener` (`PubSubConsumerBlocking<T>`), converters to the canonical `CreateQuoteAndOrderDto`, and service glue:
- **Acertus** — webhook subscription `commandexecutor.pubsub.acertus-webhook-subscription`; `AcertusLoadDtoToCreateQuoteAndOrderDtoMapper`.
- **CarsArrive** — webhook subscription `commandexecutor.pubsub.cars-arrive-webhook-subscription`; `CarsArriveDataToCreateQuoteAndOrderDtoMapper`. Also exposes **HTTP webhook + quote REST resources** and a Montway quote round-trip (see below).
- **SuperDispatch** — webhook subscription `commandexecutor.pubsub.super-dispatch-webhook-subscription`; `SuperDispatchDataToCreateQuoteAndOrderDtoMapper`. Calls SuperDispatch back via a custom `WebClient` with per-company OAuth.
- **EDI Orderful** — inbound EDI 204/120 via `commandexecutor.pubsub.edi-orderful-inbound-subscription`. Correlates 204↔120 in a **Firestore** pending-transaction store; builds `CreateQuoteAndOrderDto` inline in `EdiOrderfulServiceImpl`.

## How it fits
- **Consumes (Pub/Sub subscriptions):** 4 subscriptions, one per integration (Acertus, CarsArrive, SuperDispatch, EDI Orderful). JSON DTOs, no schema registry.
- **Publishes events to:** CarsArrive publish topic `commandexecutor.pubsub.cars-arrive-publish-topic` (quote/response fan-out for the CarsArrive flow). No general notification publisher.
- **Calls (REST/HTTP out):**
  - `impersonator` — `ImpersonatorClient` (`@RegisterRestClient`, configKey `impersonator`) — the single out-edge for order creation; every integration funnels through it.
  - **SuperDispatch** public OAuth + orders API — `SuperDispatchClient`/`SuperDispatchClientImpl` built on the ship.cars `webclient` extension (NOT a `@RegisterRestClient`), per-company client credentials.
- **Owns data store:** **Firestore** for EDI pending-transaction correlation (`EdiOrderfulPendingTransactionEntity` extends `StorageEntity`). No relational/JPA datasource observed — the other integrations are stateless.

## Build / test / run
```
./start-quarkus-dev.sh                  # JVM dev, hot-reload, :7071
./start-quarkus-native.sh               # run native binary
./build-native.sh                       # native build (-Pnative, xmx 8g)
./mvnw clean install                    # JVM build + tests
./mvnw clean install -Pnative -DskipTests
```

## Key abstractions
- `application/` — Quarkus aggregator entry point. Modules (7 + parent): `api-dtos`, `application`, `commons`, `configuration`, `coverage-report`, `resources`, `services`.
- `configuration/src/main/resources/application.properties` — full config surface: 4 Pub/Sub subscription keys, CarsArrive publish topic, per-company SuperDispatch creds (env-backed `default:...,c1:...` maps), EDI VIN-prefix map, impersonator URL, SuperDispatch retry config, and `ship.cars.reflection.package-name[0..25]` (26 entries) for native-image reflection.
- `services/.../<integration>/listeners/*PubSubListener.java` — `AcertusPubSubListener`, `CarsArrivePubSubListener`, `SuperDispatchPubSubListener`, `EdiOrderfulPubSubListener`. Subscriptions come from `PubSubConfig` (`@ConfigMapping(prefix="commandexecutor.pubsub")`).
- `services/.../clients/ImpersonatorClient.java` — REST client to `impersonator`; `@Retry(delay=1s, maxRetries=7)` + `@RetryWhen(IsRetryable)` + `@ExponentialBackoff`, **no `@Timeout`/`@CircuitBreaker`**.
- `services/.../superdispatch/clients/impl/SuperDispatchClientImpl.java` — outbound SuperDispatch (OAuth + order details) over the `webclient` extension; retry bounded by properties (3 attempts, 1–5s backoff).
- `services/.../ediorderful/services/impl/EdiOrderfulServiceImpl.java` — EDI 204/120 processing; builds `CreateQuoteAndOrderDto` inline (~line 699). `RIVIAN_MAKE` constant used for 204 client make.
- `services/.../quotemanager/services/VinMakeResolverServiceImpl.java` — longest-prefix VIN→make/body-type resolution from the `vin-makes` config.
- `resources/.../carsarrive/rest/CarsArriveWebhookResource.java` (`@Path("/v1/carsarrive/webhook")`) and `CarsArriveQuoteResource.java` (`@Path("/v1/carsarrive/quotes")`) — the only JAX-RS server endpoints.

## Don't-do-here / gotchas
- **CORRECTION vs. prior shadow — now Quarkus 3.27.5, not 3.20.2.2.** The version-matrix cohort claim is stale; this is on the current fleet cluster.
- **CORRECTION — EDI pending-transaction state is Firestore, not JPA/Postgres.** `EdiOrderfulPendingTransactionEntity` is a `StorageEntity` (`@RegisterForReflection`, `@SuperBuilder`), keyed `{prefix}/{ediShipmentId}`. There is no `db-entities` module and no relational datasource here — reset/replay logic must respect the Firestore doc lifecycle, don't assume a SQL table.
- **CORRECTION — the VIN prefix→make map is config-driven, not hardcoded.** Property `commandexecutor.edi-orderful.vin-makes` (env `CONFIG_EDI_ORDERFUL_VIN_MAKES`, dev/test default `7PD:Rivian;SUV,7FC:Rivian;Truck,5YJ:Tesla;Car`), parsed by `EdiOrderfulConfig.vinMakes()`. Adding a prefix is a config change, not a code change. (One residual `RIVIAN_MAKE` constant remains in code.)
- **CORRECTION — SuperDispatch is a `WebClient`, not a `@RegisterRestClient`.** Only `ImpersonatorClient` is an MP REST client. Repo-wide grep for `@Timeout`/`@CircuitBreaker`/`connect-timeout`/`read-timeout` returns nothing.
- **`ImpersonatorClient` is retry-without-timeout** — 7 retries, exponential backoff, no `@Timeout` and no `connect-timeout`/`read-timeout` property. Under impersonator slowness the worker thread hangs and retries pile latency. This is the fleet anti-pattern.
- **`ImpersonatorClient` is the single out-edge for order creation** — an impersonator outage stalls all four integrations at once. Consider during impersonator deploys.
- **SuperDispatch outbound has bounded retry (3 attempts, 1–5s) but no explicit connect/read timeout** — tighter than the fleet default, but still no hard per-call timeout.
- **Native-image is the production path.** `quarkus.native.builder-image=quay.io/quarkus/ubi-quarkus-mandrel-builder-image:23.1.11.0-Final-java21`. All reflection-registered classes (`ship.cars.reflection.package-name[0..25]`) must stay current — a missing entry is a runtime `ClassNotFoundException` only in the native binary, never in JVM tests. Adding a new Posting/commons DTO subpackage requires updating this list; keep index `[25]=cars.ship.commons.dtos`.
- **Per-company SuperDispatch creds and per-integration user-id maps live as `default:...,c1:...` property maps** (env-backed for prod) — onboarding a new company is a config change but the flat-map pattern doesn't scale gracefully.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/impersonator.md` — the user-attribution gateway every order-creation call traverses.
- `~/projects/codebase-map/repos/posting-backend.md` — downstream target of `CreateQuoteAndOrderDto` via impersonator.
- `~/projects/codebase-map/relations/service-graph.md` — Pub/Sub-subscription edges for `command-executor`.
- `~/projects/codebase-map/domains/integrations.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `AcertusAssignedEvent` | dto | `api-dtos` | AcertusAssignedEvent |
| `AcertusCarrierDto` | dto | `api-dtos` | AcertusCarrier |
| `AcertusDriverDto` | dto | `api-dtos` | AcertusDriver |
| `AcertusLoadDto` | dto | `api-dtos` | AcertusLoad |
| `AcertusLocationDto` | dto | `api-dtos` | AcertusLocation |
| `AcertusVehicleDto` | dto | `api-dtos` | AcertusVehicle |
| `CarsArriveContact` | dto | `api-dtos` | CarsArriveContact |
| `CarsArriveLoad` | dto | `api-dtos` | CarsArriveLoad |
| `CarsArriveLoadEventData` | dto | `api-dtos` | CarsArriveLoadEventData |
| `CarsArriveLocation` | dto | `api-dtos` | CarsArriveLocation |
| `CarsArriveOrderEvent` | dto | `api-dtos` | CarsArriveOrderEvent |
| `CarsArriveVehicle` | dto | `api-dtos` | CarsArriveVehicle |
| `ContactDto` | dto | `api-dtos` | [Contact](../domains/entities/Contact.md) |
| `CreateQuoteAndOrderDto` | dto | `api-dtos` | CreateQuoteAndOrder |
| `EdiOrderful120BVS` | dto | `api-dtos` | EdiOrderful120BVS |
| `EdiOrderful120DateTime` | dto | `api-dtos` | EdiOrderful120DateTime |
| `EdiOrderful120G62Loop` | dto | `api-dtos` | EdiOrderful120G62Loop |
| `EdiOrderful120N1` | dto | `api-dtos` | EdiOrderful120N1 |
| `EdiOrderful120N3` | dto | `api-dtos` | EdiOrderful120N3 |
| `EdiOrderful120N4` | dto | `api-dtos` | EdiOrderful120N4 |
| `EdiOrderful120TransactionSet` | dto | `api-dtos` | EdiOrderful120TransactionSet |
| `EdiOrderful120TransactionSetHeader` | dto | `api-dtos` | EdiOrderful120TransactionSetHeader |
| `EdiOrderful120TransactionSetTrailer` | dto | `api-dtos` | EdiOrderful120TransactionSetTrailer |
| `EdiOrderful120VC` | dto | `api-dtos` | EdiOrderful120VC |
| `EdiOrderful120VCLoop` | dto | `api-dtos` | EdiOrderful120VCLoop |
| `EdiOrderful120VehicleDetail` | dto | `api-dtos` | EdiOrderful120VehicleDetail |
| `EdiOrderful120VehicleShippingOrder` | dto | `api-dtos` | EdiOrderful120VehicleShippingOrder |
| `EdiOrderful204AT8` | dto | `api-dtos` | EdiOrderful204AT8 |
| `EdiOrderful204B2` | dto | `api-dtos` | EdiOrderful204B2 |
| `EdiOrderful204B2A` | dto | `api-dtos` | EdiOrderful204B2A |
| `EdiOrderful204G61` | dto | `api-dtos` | EdiOrderful204G61 |
| `EdiOrderful204G61Loop` | dto | `api-dtos` | EdiOrderful204G61Loop |
| `EdiOrderful204G62` | dto | `api-dtos` | EdiOrderful204G62 |
| `EdiOrderful204L11` | dto | `api-dtos` | EdiOrderful204L11 |
| `EdiOrderful204L3` | dto | `api-dtos` | EdiOrderful204L3 |
| `EdiOrderful204L5` | dto | `api-dtos` | EdiOrderful204L5 |
| `EdiOrderful204L5Loop` | dto | `api-dtos` | EdiOrderful204L5Loop |
| `EdiOrderful204MotorCarrierLoadTender` | dto | `api-dtos` | EdiOrderful204MotorCarrierLoadTender |
| `EdiOrderful204N1` | dto | `api-dtos` | EdiOrderful204N1 |
| `EdiOrderful204N1Loop` | dto | `api-dtos` | EdiOrderful204N1Loop |
| `EdiOrderful204N3` | dto | `api-dtos` | EdiOrderful204N3 |
| `EdiOrderful204N4` | dto | `api-dtos` | EdiOrderful204N4 |
| `EdiOrderful204OID` | dto | `api-dtos` | EdiOrderful204OID |
| `EdiOrderful204OIDLoop` | dto | `api-dtos` | EdiOrderful204OIDLoop |
| `EdiOrderful204S5` | dto | `api-dtos` | EdiOrderful204S5 |
| `EdiOrderful204S5Loop` | dto | `api-dtos` | EdiOrderful204S5Loop |
| `EdiOrderful204TransactionSet` | dto | `api-dtos` | EdiOrderful204TransactionSet |
| `EdiOrderful204TransactionSetHeader` | dto | `api-dtos` | EdiOrderful204TransactionSetHeader |
| `EdiOrderful204TransactionSetTrailer` | dto | `api-dtos` | EdiOrderful204TransactionSetTrailer |
| `EdiOrderfulFunctionalGroupHeader` | dto | `api-dtos` | EdiOrderfulFunctionalGroupHeader |
| `EdiOrderfulInboundTransaction` | dto | `api-dtos` | EdiOrderfulInboundTransaction |
| `EdiOrderfulInterchangeControlHeader` | dto | `api-dtos` | EdiOrderfulInterchangeControlHeader |
| `EdiOrderfulParty` | dto | `api-dtos` | EdiOrderfulParty |
| `EdiOrderfulTransactionType` | dto | `api-dtos` | EdiOrderfulTransactionType |
| `SuperDispatchCarrierDto` | dto | `api-dtos` | SuperDispatchCarrier |
| `SuperDispatchContactDto` | dto | `api-dtos` | SuperDispatchContact |
| `SuperDispatchData` | dto | `api-dtos` | SuperDispatchData |
| `SuperDispatchLocationDto` | dto | `api-dtos` | SuperDispatchLocation |
| `SuperDispatchObject` | dto | `api-dtos` | SuperDispatchObject |
| `SuperDispatchOrderDto` | dto | `api-dtos` | SuperDispatchOrder |
| `SuperDispatchOrderEvent` | dto | `api-dtos` | SuperDispatchOrderEvent |
| `SuperDispatchVehicleDto` | dto | `api-dtos` | SuperDispatchVehicle |
| `TokenResultDto` | dto | `api-dtos` | TokenResult |
| `VehicleDetailsDto` | dto | `api-dtos` | VehicleDetails |
| `VinMakeInfo` | dto | `services` | VinMakeInfo |
| `EdiOrderfulPendingTransactionEntity` | other | `services` | EdiOrderfulPendingTransaction |
<!-- entities-end -->
