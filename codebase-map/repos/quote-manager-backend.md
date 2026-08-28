---
repo: quote-manager-backend
path: ~/projects/ship-cars-usa/quote-manager-backend
stack: Java/Spring Boot 3.2.12 (Java 21)
domain: pricing-billing
shape: single-module
last-synced-commit: 5ad3e9a7aaef36904c105c2f7b3f95ac117c0ded
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# quote-manager-backend

## What it is
Spring Boot 3.2.12 (Java 21) service managing transport-quote lifecycle and order-booking coordination, in a hexagonal (ports/adapters) layout. Acts as a **state facade** rather than the canonical pricing engine — it receives quotes from an external provider over Pub/Sub, stores quote rows with an `active` flag (canonical state marker on `BaseEntity`), broadcasts state-change events, and coordinates managed-order create/cancel with `posting-backend`. Quote pricing logic itself lives in `contract-pricing-backend` and the rate-engine ML services. **The only wired external provider today is Montway** (`MontwayProviderClientImpl` + generic `CommonProviderClientImpl`); **no RoadSync** integration exists in source. Uses spring-data-envers auditing, Unleash feature toggles, Keycloak OAuth2 resource-server. **Spring Boot, not Quarkus** despite `PROJECTS_INDEX.md`.

## How it fits
- Consumes API of: `posting-backend` (managed-orders, via `PostingServiceClientImpl`), `user-backend` (`UserManagementClientImpl`), Montway provider API (`MontwayProviderClientImpl`), `location-provider`, `metadata`, `notification-backend` — all via `WebClientImpl` cached by `WebClientImplFactory`.
- Publishes events to: Pub/Sub `posting-state`, `notification-state`, `quote-send-state` (outbound to CTMS), `quote-notification` (`application.properties:57-60`).
- Subscribes to: Pub/Sub `quote-receive-state` (inbound provider quotes → `QuoteStateConsumer` → `QuotePubSubDto`); `payment-notification` is **configured as a subscription but has NO consumer** (`application.properties:55` — see gotchas).
- Owns data store: PostgreSQL (`ddl-auto=validate`). HikariCP: `maximumPoolSize=10`, `connectionTimeout=120s`, `maxLifetime=180s`, `idle-timeout=90s`, `minimum-idle=2`, `leak-detection=90s` (`application.properties:107-113`).

## Build / test / run
```
./build-project.sh
./build-dev.sh
./utils/docker-compose/docker-compose-db-only.sh up -d
./mvnw clean test
./mvnw clean verify -Pintegration-tests
# Single-module Maven (1 pom). Local server.port=7045 (application-local); trusted-endpoints default 7098.
```

## Key abstractions
- `QuoteController` — `application/adapters/in/web/rest/controller/QuoteController.java` — `@RestController @RequestMapping("v1/quotes")`; REST entry point for quotes.
- `QuoteService implements QuoteOperations` — `domain/service/QuoteService.java:79` — core quote domain logic; port at `domain/ports/in/QuoteOperations.java`.
- `OrderService implements OrderOperations` — `domain/service/OrderService.java:57` — creates/cancels managed orders, calls posting + provider.
- `QuoteStateConsumer extends PubSubConsumer` — `application/adapters/in/pubsub/QuoteStateConsumer.java` — consumes `quote-receive-state`, delegates to `QuoteStateFacade.handleAddQuoteEvent`.
- `WebClientImplFactory` — `application/adapters/out/clients/WebClientImplFactory.java:52-69` — caches per-URI `WebClientImpl`; sets `.retryMaxAttempts(3)` (`:59`) but **no connect/read/response timeout**.
- `MessageSenderImpl implements MessageSender` — `application/adapters/out/pubsub/MessageSenderImpl.java:36-50` — direct Pub/Sub publish inside a Micrometer timer; no outbox.
- `QuoteRepositoryImpl` — `application/adapters/out/repo/QuoteRepositoryImpl.java:35` — `findByQuoteClientIdAndCompanyIdAndActiveTrue()` etc.; `active` flag is the pervasive canonical-state filter.

## Don't-do-here / gotchas
- **`payment-notification` subscription is orphaned.** It's declared at `application.properties:55` and auto-subscribed by `PubSubConsumersConfig.subscribeConsumers()` (`config/pubsub/PubSubConsumersConfig.java:22-27`), but no `PubSubConsumer` bean targets it — `QuoteStateConsumer` (subscription `quote-receive-state`) is the only one. Nothing consumes payment-lifecycle events here; verify against the carrier-payment contract before assuming this path works.
- **No REST-client timeouts (P0).** `WebClientImplFactory` builds `spring-commons.WebClientImpl` with `retryMaxAttempts=3` and no `connectTimeoutMs`/`readTimeoutMs`/`responseTimeoutMs` (`:52-69`). Retry-without-timeout cascade; fix in the factory.
- **`@Version` optimistic locking is INERT.** `domain/model/common/BaseEntity.java:37` annotates `lastModified` with `@Version`, but the import at `:18` is `org.springframework.data.annotation.Version` (Spring Data), which Hibernate ignores — not `jakarta.persistence.Version`. The same field also carries `@LastModifiedDate` (`:38`), i.e. it's an audit timestamp, not a real version column. No optimistic locking is enforced.
- **No outbox** — `MessageSenderImpl.send()` publishes directly after the DB commit; a publish failure loses the event downstream. (`QuoteGenerationEventListener.java:18` uses in-JVM `@Async`, not a persisted outbox.) `posting-backend` (also Spring) has a real outbox; this service does not.
- **No `@CircuitBreaker` / `@Retryable`.** Only WebClient's built-in `retryMaxAttempts=3`.
- **HikariCP `connectionTimeout=120s` is generous** — paired with missing query timeouts, a slow Postgres can stall request threads for two minutes.
- **Flyway disabled in K8s** — `spring.flyway.enabled=false` (`:66`); migrations run via a separate job. `ddl-auto=validate`. Don't rely on app-startup migrations.
- **Quote-cleanup job** (`config.quote-cleanup.*`, `application.properties:181-190`) is new and shipped **DISABLED** by default (`enabled` default false). Its replica-lag checker was removed in the latest commit (`5ad3e9a7`, LITE-8014); no consumer behavior changed.

## Relevant ADRs / docs
- README documents Docker setup only; CLAUDE.md is a skill-loading stub.
- Single-module structure is unusual versus the multi-module Quarkus norm in the fleet.
- `~/projects/contracts/carrier-payment/` — carrier-payment contract; documents the orphaned payment-notification consumer.
- `~/projects/codebase-map/repos/contract-pricing-backend.md` — the actual pricing logic. quote-manager is downstream of it.
- `~/projects/codebase-map/repos/spring-commons.md` — `WebClientImpl` / `WebClientConfig` timeout knobs that should be set here.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `BookingDetails` | jpa | `quote-manager-backend` | BookingDetails |
| `ManagedServiceProvider` | jpa | `quote-manager-backend` | ManagedServiceProvider |
| `ProviderApiKey` | jpa | `quote-manager-backend` | ProviderApiKey |
| `Quote` | jpa | `quote-manager-backend` | [Quote](../domains/entities/Quote.md) |
| `Vehicle` | jpa | `quote-manager-backend` | [Vehicle](../domains/entities/Vehicle.md) |
| `AdditionalVehicleInfoVo` | dto | `quote-manager-backend` | AdditionalVehicleInfoVo |
| `AppConfigImpl` | dto | `quote-manager-backend` | AppConfigImpl |
| `BaseContactVo` | dto | `quote-manager-backend` | BaseContactVo |
| `BaseEntityDetached` | dto | `quote-manager-backend` | BaseEntityDetached |
| `BaseRequestResponseDto` | dto | `quote-manager-backend` | Base |
| `BookingDetailsCountWrapperDto` | dto | `quote-manager-backend` | BookingDetailsCountWrapper |
| `BookingDetailsCreateVo` | dto | `quote-manager-backend` | BookingDetailsCreateVo |
| `BookingDetailsDetached` | dto | `quote-manager-backend` | BookingDetailsDetached |
| `BookingDetailsDto` | dto | `quote-manager-backend` | BookingDetails |
| `BookingDetailsFilter` | dto | `quote-manager-backend` | BookingDetailsFilter |
| `BookingDetailsFilterDto` | dto | `quote-manager-backend` | BookingDetailsFilter |
| `BookingDetailsGroupInformationDto` | dto | `quote-manager-backend` | BookingDetailsGroupInformation |
| `BookingDetailsUpdateVo` | dto | `quote-manager-backend` | BookingDetailsUpdateVo |
| `CancelOrderDto` | dto | `quote-manager-backend` | CancelOrder |
| `CancelOrderVo` | dto | `quote-manager-backend` | CancelOrderVo |
| `CombinedBookingPayload` | dto | `quote-manager-backend` | CombinedBookingPayload |
| `CompanyDto` | dto | `quote-manager-backend` | [Company](../domains/entities/Company.md) |
| `CompanyVo` | dto | `quote-manager-backend` | CompanyVo |
| `ContactDto` | dto | `quote-manager-backend` | [Contact](../domains/entities/Contact.md) |
| `ContactVo` | dto | `quote-manager-backend` | ContactVo |
| `CreateQuoteAndOrderDto` | dto | `quote-manager-backend` | CreateQuoteAndOrder |
| `DistanceDto` | dto | `quote-manager-backend` | Distance |
| `DistanceInformationCollectionDto` | dto | `quote-manager-backend` | DistanceInformationCollection |
| `DistanceInformationDto` | dto | `quote-manager-backend` | DistanceInformation |
| `DropdownFieldDto` | dto | `quote-manager-backend` | DropdownField |
| `EntityId` | dto | `quote-manager-backend` | EntityId |
| `Filter` | dto | `quote-manager-backend` | [Filter](../domains/entities/Filter.md) |
| `GeoComponentDto` | dto | `quote-manager-backend` | GeoComponent |
| `GeoDataVo` | dto | `quote-manager-backend` | GeoDataVo |
| `GeometryDto` | dto | `quote-manager-backend` | Geometry |
| `GoogleDistanceResponseDto` | dto | `quote-manager-backend` | GoogleDistance |
| `LocationDto` | dto | `quote-manager-backend` | [Location](../domains/entities/Location.md) |
| `LoggingRestMessage` | dto | `quote-manager-backend` | LoggingRestMessage |
| `ManagedProviderVo` | dto | `quote-manager-backend` | ManagedProviderVo |
| `ManagedServiceProviderDetached` | dto | `quote-manager-backend` | ManagedServiceProviderDetached |
| `ManagedServiceProviderDto` | dto | `quote-manager-backend` | ManagedServiceProvider |
| `ManagedServiceProviderInternalDto` | dto | `quote-manager-backend` | ManagedServiceProviderInternal |
| `ManagedServiceProviderPubSubDto` | dto | `quote-manager-backend` | ManagedServiceProvider |
| `ManagedServiceProviderPubSubDto` | dto | `quote-manager-backend` | ManagedServiceProvider |
| `MontwayBaseContactDto` | dto | `quote-manager-backend` | MontwayBaseContact |
| `MontwayCancelOrderRequestDto` | dto | `quote-manager-backend` | MontwayCancelOrder |
| `MontwayCustomerContactDto` | dto | `quote-manager-backend` | MontwayCustomerContact |
| `MontwayErrorResponseVo` | dto | `quote-manager-backend` | MontwayErrorResponseVo |
| `MontwayErrorVo` | dto | `quote-manager-backend` | MontwayErrorVo |
| `MontwayGatePassInformation` | dto | `quote-manager-backend` | MontwayGatePassInformation |
| `MontwayMultiVehicleResponseDto` | dto | `quote-manager-backend` | MontwayMultiVehicle |
| `MontwayOrderDto` | dto | `quote-manager-backend` | MontwayOrder |
| `MontwayPaymentOrderRequestDto` | dto | `quote-manager-backend` | MontwayPaymentOrder |
| `MontwayPickupDeliveryContactDto` | dto | `quote-manager-backend` | MontwayPickupDeliveryContact |
| `MontwayQuoteRequestDto` | dto | `quote-manager-backend` | MontwayQuote |
| `MontwayQuoteResponseDto` | dto | `quote-manager-backend` | MontwayQuote |
| `MontwayRatesDto` | dto | `quote-manager-backend` | MontwayRates |
| `MontwayResponseDto` | dto | `quote-manager-backend` | Montway |
| `MontwaySingleVehicleResponseDto` | dto | `quote-manager-backend` | MontwaySingleVehicle |
| `MontwayTransitTimeDto` | dto | `quote-manager-backend` | MontwayTransitTime |
| `MontwayTransportClientDto` | dto | `quote-manager-backend` | MontwayTransportClient |
| `MontwayVehicleDto` | dto | `quote-manager-backend` | MontwayVehicle |
| `NotificationEventDto` | dto | `quote-manager-backend` | Notification |
| `OrderDto` | dto | `quote-manager-backend` | Order |
| `OrderResponse` | dto | `quote-manager-backend` | Order |
| `OrderVo` | dto | `quote-manager-backend` | OrderVo |
| `PagedResponseDto` | dto | `quote-manager-backend` | Paged |
| `PaymentLinkRequestDto` | dto | `quote-manager-backend` | PaymentLink |
| `PaymentLinkResponseDto` | dto | `quote-manager-backend` | PaymentLink |
| `PaymentLinkSatusDto` | dto | `quote-manager-backend` | PaymentLinkSatus |
| `PaymentOrderVo` | dto | `quote-manager-backend` | PaymentOrderVo |
| `PostingPayload` | dto | `quote-manager-backend` | PostingPayload |
| `ProviderApiKeyDetached` | dto | `quote-manager-backend` | ProviderApiKeyDetached |
| `ProviderApiKeyDto` | dto | `quote-manager-backend` | ProviderApiKey |
| `ProviderAuthConfig` | dto | `quote-manager-backend` | ProviderAuthConfig |
| `ProviderCancelOrderRequestDto` | dto | `quote-manager-backend` | ProviderCancelOrder |
| `ProviderConfigDetached` | dto | `quote-manager-backend` | ProviderConfigDetached |
| `ProviderConfigVo` | dto | `quote-manager-backend` | ProviderConfigVo |
| `ProviderContactDto` | dto | `quote-manager-backend` | ProviderContact |
| `ProviderErrorResponseVo` | dto | `quote-manager-backend` | ProviderErrorResponseVo |
| `ProviderLocationDto` | dto | `quote-manager-backend` | ProviderLocation |
| `ProviderOrderRequestDto` | dto | `quote-manager-backend` | ProviderOrder |
| `ProviderOrderResponseDto` | dto | `quote-manager-backend` | ProviderOrder |
| `ProviderQuoteRequestDto` | dto | `quote-manager-backend` | ProviderQuote |
| `ProviderQuoteResponseDto` | dto | `quote-manager-backend` | ProviderQuote |
| `ProviderRateDto` | dto | `quote-manager-backend` | ProviderRate |
| `ProviderSettingsDto` | dto | `quote-manager-backend` | ProviderSettings |
| `ProviderSettingsInternalDto` | dto | `quote-manager-backend` | ProviderSettingsInternal |
| `ProviderSettingsVo` | dto | `quote-manager-backend` | ProviderSettingsVo |
| `ProviderTransitTimeDto` | dto | `quote-manager-backend` | ProviderTransitTime |
| `ProviderVehicleDto` | dto | `quote-manager-backend` | ProviderVehicle |
| `ProvidersPayloadDto` | dto | `quote-manager-backend` | ProvidersPayload |
| `ProvidersPayloadVo` | dto | `quote-manager-backend` | ProvidersPayloadVo |
| `QuoteCreateVo` | dto | `quote-manager-backend` | QuoteCreateVo |
| `QuoteDetached` | dto | `quote-manager-backend` | QuoteDetached |
| `QuoteDetachedAndResponse` | dto | `quote-manager-backend` | QuoteDetachedAnd |
| `QuoteDto` | dto | `quote-manager-backend` | [Quote](../domains/entities/Quote.md) |
| `QuoteDto` | dto | `quote-manager-backend` | [Quote](../domains/entities/Quote.md) |
| `QuoteErrorVo` | dto | `quote-manager-backend` | QuoteErrorVo |
| `QuoteGenerationEvent` | dto | `quote-manager-backend` | QuoteGenerationEvent |
| `QuotePubSubDto` | dto | `quote-manager-backend` | [Quote](../domains/entities/Quote.md) |
| `QuotePubSubDto` | dto | `quote-manager-backend` | [Quote](../domains/entities/Quote.md) |
| `QuoteRequestBaseDto` | dto | `quote-manager-backend` | QuoteRequestBase |
| `QuoteRequestDto` | dto | `quote-manager-backend` | [Quote](../domains/entities/Quote.md) |
| `QuoteRequestPubSubDto` | dto | `quote-manager-backend` | [Quote](../domains/entities/Quote.md) |
| `QuoteRequestPubSubDto` | dto | `quote-manager-backend` | [Quote](../domains/entities/Quote.md) |
| `QuoteRequestVo` | dto | `quote-manager-backend` | QuoteRequestVo |
| `QuoteRequestWithExternalClientDto` | dto | `quote-manager-backend` | QuoteRequestWithExternalClient |
| `QuoteRequestWithProviderDto` | dto | `quote-manager-backend` | QuoteRequestWithProvider |
| `QuoteResponse` | dto | `quote-manager-backend` | [Quote](../domains/entities/Quote.md) |
| `QuoteResponseDto` | dto | `quote-manager-backend` | [Quote](../domains/entities/Quote.md) |
| `QuoteResponseRatesDto` | dto | `quote-manager-backend` | QuoteResponseRates |
| `QuoteResponseTransitTimeDto` | dto | `quote-manager-backend` | QuoteResponseTransitTime |
| `QuoteSelectedDetailsDto` | dto | `quote-manager-backend` | QuoteSelectedDetails |
| `QuotesReceivedNotificationDto` | dto | `quote-manager-backend` | QuotesReceivedNotification |
| `RatesVo` | dto | `quote-manager-backend` | RatesVo |
| `RequestDto` | dto | `quote-manager-backend` | — |
| `ResponseDto` | dto | `quote-manager-backend` | — |
| `SocketMessageActionDto` | dto | `quote-manager-backend` | SocketMessageAction |
| `SortDto` | dto | `quote-manager-backend` | Sort |
| `StripeDetailsDto` | dto | `quote-manager-backend` | StripeDetails |
| `TransitTimeDto` | dto | `quote-manager-backend` | TransitTime |
| `TransitTimeMinMaxDto` | dto | `quote-manager-backend` | TransitTimeMinMax |
| `TransitTimeRequestDto` | dto | `quote-manager-backend` | TransitTime |
| `TransitTimeVo` | dto | `quote-manager-backend` | TransitTimeVo |
| `UpdatableFieldDto` | dto | `quote-manager-backend` | UpdatableField |
| `VehicleDetached` | dto | `quote-manager-backend` | VehicleDetached |
| `VehicleDetailsDto` | dto | `quote-manager-backend` | VehicleDetails |
| `VehicleRequestPubSubDto` | dto | `quote-manager-backend` | [Vehicle](../domains/entities/Vehicle.md) |
| `VehicleRequestPubSubDto` | dto | `quote-manager-backend` | [Vehicle](../domains/entities/Vehicle.md) |
| `VehicleVo` | dto | `quote-manager-backend` | VehicleVo |
<!-- entities-end -->
