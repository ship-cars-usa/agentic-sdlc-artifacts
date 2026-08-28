---
repo: contract-pricing-backend
path: ~/projects/ship-cars-usa/contract-pricing-backend
stack: Java/Quarkus 3.27.5 (Java 21)
domain: pricing-billing
shape: multi-module (11 poms)
last-synced-commit: c49bf4b7e4212bdd4c5f77ebb8abeb1b6c2d4647
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# contract-pricing-backend

## What it is
Quarkus 3.27.5 / Java 21 service (v1.8.0-SNAPSHOT) for contract pricing calculations + carrier/customer/contract management. Hibernate ORM + Panache + Envers auditing. Reads company/carrier data from the CTMS Django platform **via the impersonator REST client** (there is no separate "django carriers" client), plus user-management and the location-provider extension; subscribes to a company Pub/Sub topic and forwards CARRIER events onto the in-process Vert.x EventBus. **Fleet-review verdict (2026-05): do-not-ship-without-rework** — the P0 bugs below were re-verified against HEAD and are **all still unfixed**.

## How it fits
- Consumes API of: CTMS Django platform companies (via `ImpersonatorClient`, `@RegisterRestClient configKey=impersonator`), `user-management` (`UserManagementClient`), location-provider (via the `cars.ship.locationprovider` extension), `dataone` — all REST, **no connect/read timeouts configured**.
- Publishes events to: **no outbound Pub/Sub topic.** `CompanyPubSubListener` only forwards to the in-process Vert.x EventBus (`COMMAND_SYNC_COMPANY`, `CompanyPubSubListener.java:44-49`).
- Subscribes to: Pub/Sub company subscription (`contract.pricing.pubsub.company-subscription`) via `CompanyPubSubListener` (`PubSubConsumerBlocking<CompanyEventPubSubDto>`).
- Owns data store: PostgreSQL (Flyway-migrated **V1–V23**; `hibernate.generation=none`, Flyway-managed).

## Build / test / run
```
mvn clean package
mvn test
mvn quarkus:dev
mvn package -Pnative   # native compilation supported
# 11 poms: application, commons, configuration, contract-pricing-dtos,
#          contract-pricing-enums, coverage-report, db-entities, db-migration, resources, services
# Server port 7123 (dev/test 7124)
```

## Key abstractions
- `DjangoServiceImpl` — `services/.../services/impl/DjangoServiceImpl.java` — converts impersonator/Django company results to `CarrierDto` pages; *contains the broken pagination math* (`:37`).
- `ImpersonatorClient` — `services/.../clients/ImpersonatorClient.java` — `@RegisterRestClient(configKey="impersonator")`; the actual "Django carriers" client (`/impersonate/company/{id}/api/platform/companies`).
- `UserManagementClient` — `services/.../clients/UserManagementClient.java` — `/internal/v2/companies/search`. REST clients have **no timeouts**.
- `LocationServiceImpl` — `services/.../services/impl/LocationServiceImpl.java:187-210` — geo lookups via `CompletableFuture.runAsync(...).orTimeout(...)`; *exception unwrap is broken* (see gotchas). Location access is through the locationprovider extension, not a repo-local `LocationProviderClient`.
- `ContractCRUDServiceImpl` — `services/.../services/impl/ContractCRUDServiceImpl.java` — kitchen-sink: query building + mapping + business logic; drives the per-contract N+1 via `ContractConverter.buildContractDto`.
- `ContractOperationsServiceImpl` — `services/.../services/impl/ContractOperationsServiceImpl.java:126` — the price-`calculatePrice` service (there is no class literally named `*CalculationService`); exposed via `ContractPricingCalculationsController` (rate-limited).
- `ContractPricingController` — `resources/.../rest/ContractPricingController.java` — `@Path(V1_ENDPOINT_CONTRACTS)`.
- `CompanyPubSubListener` — `services/.../listeners/CompanyPubSubListener.java` — `PubSubConsumerBlocking`.

## Don't-do-here / gotchas (P0s — re-verified unfixed at HEAD c49bf4b)
- **Pagination math is mathematically wrong** — `DjangoServiceImpl.java:37`: `final int totalPages = page == 0 ? 1 : size / page;` divides page-size by page-number instead of `(totalCount + size - 1) / size`. Propagated into `hasNext`/`isLast` (method `getAllCarriersByName`, `:62-94`; `convertPageDto` `:30-51`). **Critical, still present.**
- **No REST-client timeouts anywhere** — `configuration/.../application.properties` sets base URLs for `user-management`/`impersonator`/`location-provider`/`dataone` but no `connect-timeout`/`read-timeout`. Combined with no retry, a hung downstream silently consumes worker threads. (The only "timeout" keys are app-level `contract.pricing.locationprovider.timeout-per-location` and `...eventbus.delivery-timeout-in-millis`.)
- **`LocationServiceImpl.java:187-210`** — `runAsync(...).orTimeout(...)` then `catch (Exception e)` only matches `e.getCause() instanceof BusinessRuleException` (`:204`). A `TimeoutException` arrives wrapped in `CompletionException`, so the timeout cause is never surfaced — it's rethrown as a generic `BusinessRuleException("Failed to validate location")` (`:208`). Silent on slow geo lookups. Still present.
- **`DjangoServiceImpl.java:82-93`** — `getAllCarriersByName` catches `Exception` and re-wraps as `BusinessRuleException`; combined with no timeout, an indefinitely-hanging Django call is invisible at the API surface. Still present.
- **N+1 on contract list** — `ContractCRUDServiceImpl.convertContracts` (`:262-269`) loops every contract → `ContractConverter.buildContractDto` (`converters/impl/ContractConverter.java:85`) which issues ~4 separate queries per contract (`RegionEntity.findByContractId`, `CarrierToContractEntity.findAll...`, `SurchargeEntity.findByContractId`, `DiscountEntity.findByContractId`). Use `LEFT JOIN FETCH` or projection. Still present.

## Don't-do-here / gotchas (P1s)
- `LocationServiceImpl.java:189-193` — one slow location fails the whole batch (no partial success).
- `UserManagementServiceImpl.java:84-99` — no `@Retry` / `@CircuitBreaker` on the `user-management` client.
- `ContractPricingController.java` — `getContractByCarrierId()` has no max-page-size validation.
- `CompanyPubSubListener.java` — `eventBus.send().setSendTimeout(...)` without `.onFailure()` handler.
- **Inbound-header secrets leak (upstream, not repo-local).** The "logs full inbound headers (Clientsecret/Password)" behavior is NOT in this repo's source — no header-dumping filter here. It originates in the shared `ship.cars.quarkus.extensions.request-filter` extension (dependency in `pom.xml`, 3.27.5). Flag as an upstream/extension gotcha.
- **No JPA `@Version` optimistic locking.** `db-entities/.../entities/BaseDbEntity.java` (`@MappedSuperclass`, `@Audited`, `PanacheEntityBase`) manages `createdAt`/`lastModified` via `@PrePersist`/`@PreUpdate` (`:46-55`) plus Envers — no optimistic-lock version column. (`ContractHistoryEntity.version` is a plain domain long, not JPA `@Version`.) Concurrent contract edits are not guarded by the DB.

## Relevant ADRs / docs
- `~/projects/quarkus-fleet-review-2026-05-07.md#5-contract-pricing-backend` — full review (verdict: do-not-ship-without-rework).
- `~/projects/quarkus-rest-client-timeout-anti-pattern.md` — the systemic timeout gap.
- `docs/tech-project-overview.md` — STALE (still says Quarkus 3.20.2.2 / v1.5.0); the repo is 3.27.5 / v1.8.0-SNAPSHOT.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `CarrierEntity` | jpa | `db-entities` | [Company](../domains/entities/Company.md) |
| `CarrierToContractEntity` | jpa | `db-entities` | CarrierToContract |
| `ContractEntity` | jpa | `db-entities` | Contract |
| `ContractHistoryEntity` | jpa | `db-entities` | ContractHistory |
| `CustomerEntity` | jpa | `db-entities` | [Company](../domains/entities/Company.md) |
| `CustomerToContractEntity` | jpa | `db-entities` | CustomerToContract |
| `DiscountEntity` | jpa | `db-entities` | Discount |
| `LocationEntity` | jpa | `db-entities` | [Location](../domains/entities/Location.md) |
| `MileageBandEntity` | jpa | `db-entities` | MileageBand |
| `PowerLaneEntity` | jpa | `db-entities` | PowerLane |
| `PricingOptionEntity` | jpa | `db-entities` | PricingOption |
| `RegionEntity` | jpa | `db-entities` | Region |
| `RegionToStateEntity` | jpa | `db-entities` | RegionToState |
| `SurchargeEntity` | jpa | `db-entities` | Surcharge |
| `CalculationRequestDto` | dto | `contract-pricing-dtos` | Calculation |
| `CalculationResponseDto` | dto | `contract-pricing-dtos` | Calculation |
| `CarrierDto` | dto | `contract-pricing-dtos` | [Company](../domains/entities/Company.md) |
| `CompanyEventPubSubDto` | dto | `services` | CompanyEvent |
| `ContractDto` | dto | `contract-pricing-dtos` | Contract |
| `ContractOperationsServiceImpl` | dto | `services` | ContractOperationsServiceImpl |
| `CustomerDto` | dto | `contract-pricing-dtos` | [Company](../domains/entities/Company.md) |
| `DiscountDto` | dto | `contract-pricing-dtos` | Discount |
| `DistanceDto` | dto | `contract-pricing-dtos` | Distance |
| `DjangoCompanyDto` | dto | `contract-pricing-dtos` | DjangoCompany |
| `DjangoCompanyWrapperDto` | dto | `contract-pricing-dtos` | DjangoCompanyWrapper |
| `FieldDto` | dto | `contract-pricing-dtos` | Field |
| `LineItemDto` | dto | `contract-pricing-dtos` | LineItem |
| `LoadInformationDto` | dto | `contract-pricing-dtos` | LoadInformation |
| `LocationDto` | dto | `contract-pricing-dtos` | [Location](../domains/entities/Location.md) |
| `MileageBandDto` | dto | `contract-pricing-dtos` | MileageBand |
| `OptionDto` | dto | `contract-pricing-dtos` | Option |
| `PowerLaneCsvDto` | dto | `services` | PowerLaneCsv |
| `PowerLaneDto` | dto | `contract-pricing-dtos` | PowerLane |
| `PrePopulatedDataDto` | dto | `contract-pricing-dtos` | PrePopulatedData |
| `PricingOptionDto` | dto | `contract-pricing-dtos` | PricingOption |
| `RegionDto` | dto | `contract-pricing-dtos` | Region |
| `StateDto` | dto | `contract-pricing-dtos` | [State](../domains/entities/State.md) |
| `SurchargeDto` | dto | `contract-pricing-dtos` | Surcharge |
| `ValidationDto` | dto | `contract-pricing-dtos` | Validation |
| `VehicleDto` | dto | `contract-pricing-dtos` | [Vehicle](../domains/entities/Vehicle.md) |
<!-- entities-end -->
