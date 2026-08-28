---
repo: uship-quotes
path: ~/projects/ship-cars-usa/uship-quotes
stack: Java/Quarkus 3.27.5 (Java 21)
domain: pricing-billing
shape: multi-module (11 poms)
last-synced-commit: c858aedf74803ff1e229facadd4fed6a27308c23
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# uship-quotes

## What it is
Quarkus 3.20.2.2 / Java 21 service that **integrates Ship.Cars with the uShip marketplace**: manages per-company quote configs, automated bidding rules, and the two-way bid flow. Calls **Pricetron** (the uShip-side pricing engine) and **`rateengine`** for alternative pricing, then submits bids to uShip via one of two modes:
- **API mode**: direct REST against uShip's public API.
- **BYPASS_SERVICE mode**: routes through a Node.js + Playwright "webbot" sidecar service that performs browser automation against uShip's Okta-protected UI.

Tracks bot statistics, Envers-audited revision history, and ShedLock-coordinated scheduled bidding cron (default every 2 hours). Supports multiple bot accounts (Montway, ASG, CDT) each with separate uShip credentials. Notable because **the webbot fallback indicates uShip's API doesn't cover every flow**.

## How it fits
- Consumes API of: Pricetron (`pricetron`, `pricetronauth` `@RegisterRestClient`s, `services/.../clients/impl/`); `rateengine` (`rateengine` `@RegisterRestClient`); Webbot (`webbot` `@RegisterRestClient`, `bot/clients/WebbotClient.java` — **`connect-timeout=10000ms`, `read-timeout=120000ms`**, `application.properties:90-91` — fleet-rare explicit timeouts); location-provider (via the external ship-cars `locationprovider` extension, wrapped by `LocationsResolverClient` — **not** a `@RegisterRestClient`); uShip listings + login (`ListingsClient`, `LoginClient` — plain interfaces, **not** `@RegisterRestClient`).
- Publishes events to: `ship.cars.notification.topic=${NOTIFICATION_TOPIC}` (`application.properties:166`) for failed-bid emails, via the ship-cars notification extension `NotificationClient` (not a repo-local outbox table).
- Subscribes to: none observed (listens internally for scheduler ticks).
- Owns data store: PostgreSQL (`uship_quotes`). Flyway **V1–V25** migrations (V23 email-tracking, V24 modified-vehicle, V25 excluded-states). Hibernate + **Envers** auditing on **both** `CompanyConfigEntity` and `BotListingStatsEntity` (custom revision entity/listener). **Caffeine cache: `maximum-size=10000`, `expire-after-write=5400h`** (`application.properties:22-23`) — ~225 days; verified still that odd value.

## Build / test / run
```
./mvnw clean package -DskipTests
./mvnw quarkus:dev
# Port 9271 (test/ddl 9272)
# 11 poms: application, resources, services, db-entities, db-migration,
#          api-dtos, repositories, commons, configuration, coverage-report (+ root)
# Scheduled bot tick: cron 0 0 */2 * * ? (every 2 hours); ShedLock lock-at-most-for PT60M
```

## Key abstractions
- `BotService` — `services/.../bot/services/BotService.java` — orchestrates listing retrieval, bidding, failure tracking.
- `QuotesService` — `services/.../quotes/services/QuotesService.java` — quote creation + retrieval; consults Pricetron + `rateengine`.
- `CompanyConfigService` + `CompanyBotConfigService` — `services/.../quotes|bot/services/` — config CRUD with Envers revision history.
- `WebbotClient` — `services/.../bot/clients/WebbotClient.java:11` — `@RegisterRestClient(configKey="webbot")`, single `POST /submit-bid` → `WebbotResponse`, explicit timeouts.
- `PricetronClient`, `RateEngineClient` — `services/.../quotes/clients/` — outbound REST clients (impls `RateEngineClientImpl` / `PricetronClientInt` + `PricetronClientAuthInt`).
- `LocationsResolverClient` — `services/.../quotes/clients/LocationsResolverClient.java` — geo lookups via the external locationprovider extension (renamed from the old doc's "LocationProviderClient").
- `BotScheduleServiceImpl` — `services/.../BotScheduleServiceImpl.java:90-91` — `@Scheduled(cron)` + `@SchedulerLock(name="tickBot")` scheduled bidding.
- `QuotesResource`, `CompanyConfigsResource`, `CompanyBotConfigsResource` — `resources/.../rest/` JAX-RS surfaces.

## Don't-do-here / gotchas
- **Webbot integration is synchronous** with a 120 s read timeout (`application.properties:90`); called blocking at `WebbotBidCreator.java:65`. If the Node.js Playwright sidecar is slow/down, the bidding thread blocks for two minutes.
- **Bid-creation mode default is `BYPASS_SERVICE`** (webbot), `config.bot.bid-creation-mode` (`application.properties:148-152`). Mode is resolved **per bot-config at runtime** (`ListingsClientRateLimitedImpl.java:121-133`), not a single global switch — but the default still comes from `CONFIG_BOT_BID_CREATION_MODE`. Enum `BidCreationModeEnum {API, BYPASS_SERVICE}`.
- **`RateEngine` retry-on-rate-limit** = 5 (`config.rateengine.retry-on-rate-limit:5`, `application.properties:100`) **without exponential/jittered backoff** — `RateEngineClientImpl.java:56-87` loops, sleeping only for a server-provided retry-after when present, else no delay. Under sustained slowness this hammers the engine.
- **Pricetron/RateEngine REST timeouts are NOT pinned** in properties — only `webbot` sets connect/read timeouts. The Pricetron/RateEngine clients rely on Quarkus defaults; implicit-default risk.
- **Pricetron client_secret in env** with no rotation mechanism visible. Long-lived secret risk.
- **Multiple uShip bot accounts** (Montway, ASG, CDT — `application.properties:122-135`) each with their own auth token; per-account refresh. Token expiry mid-cron-tick can produce silent bid failures.
- **Caffeine cache `expire-after-write=5400h`** (~225 days) — either intentional "effectively forever" or a typo of `5400s`. If it's hours, the cache holds stale config across many config changes.
- **ShedLock `lock-at-most-for=PT60M`** with a 2-hour cron — the lock releases well before the next tick; safe at 2h spacing but the lock does not span a full inter-tick window.
- **CLAUDE.md is stale** (says Quarkus 3.15.4, Maven 3.9.9, "V22") — the repo is actually Quarkus 3.27.5, Flyway V25.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/quote-manager-backend.md` — fleet-internal quote-state facade; complements uShip-specific path.
- `~/projects/codebase-map/repos/contract-pricing-backend.md` — per-customer overlay (when bids land for a customer with a contract).
- `~/projects/codebase-map/repos/rateengine.md` — alternative pricing consulted by `QuotesService`.
- `~/projects/codebase-map/adr/0005-rateengine-eol-rewrite.md` — the rateengine rewrite affects this caller.
- `~/projects/codebase-map/relations/rest-client-registry.md` — `webbot` client is one of the few timeout-clean Quarkus clients.
- `~/projects/codebase-map/domains/pricing-billing.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `BotListingStatsEntity` | jpa | `db-entities` | BotListingStats |
| `CompanyConfigEntity` | jpa | `db-entities` | [CompanyConfig](../domains/entities/CompanyConfig.md) |
| `CompanyQuotesEntity` | jpa | `db-entities` | CompanyQuotes |
| `QuotesEntity` | jpa | `db-entities` | Quotes |
| `RequestQuotesCompanyConfigEntity` | jpa | `db-entities` | RequestQuotesCompanyConfig |
| `RequestQuotesEntity` | jpa | `db-entities` | RequestQuotes |
| `RequestQuotesVehicleEntity` | jpa | `db-entities` | RequestQuotesVehicle |
| `AddressDto` | dto | `api-dtos` | [Location](../domains/entities/Location.md) |
| `AmountDto` | dto | `api-dtos` | Amount |
| `AmountValueDto` | dto | `api-dtos` | AmountValue |
| `AttributesDto` | dto | `api-dtos` | Attributes |
| `BidResultDto` | dto | `services` | BidResult |
| `BidRulesDto` | dto | `api-dtos` | BidRules |
| `BidderDto` | dto | `api-dtos` | Bidder |
| `BidderInfoDto` | dto | `services` | BidderInfo |
| `BotListingStatsDto` | dto | `api-dtos` | BotListingStats |
| `BotListingStatsPagedDto` | dto | `api-dtos` | BotListingStatsPaged |
| `BotServiceImpl` | dto | `services` | BotServiceImpl |
| `CompanyBotConfigDto` | dto | `api-dtos` | CompanyBotConfig |
| `CompanyBotConfigJsonVo` | dto | `db-entities` | CompanyBotConfigJsonVo |
| `CompanyConfigDto` | dto | `api-dtos` | [CompanyConfig](../domains/entities/CompanyConfig.md) |
| `CompanyConfigJsonVo` | dto | `db-entities` | CompanyConfigJsonVo |
| `CompanyConfigRevDto` | dto | `api-dtos` | CompanyConfigRev |
| `CompanyConfigRevPagedDto` | dto | `api-dtos` | CompanyConfigRevPaged |
| `CompanyConfigVo` | dto | `services` | CompanyConfigVo |
| `CompanyPreviewQuoteDto` | dto | `api-dtos` | CompanyPreviewQuote |
| `CompanyQuoteDetailsDto` | dto | `api-dtos` | CompanyQuoteDetails |
| `CompanyQuoteDetailsVo` | dto | `services` | CompanyQuoteDetailsVo |
| `CompanyQuoteVo` | dto | `services` | CompanyQuoteVo |
| `CreateQuotesDto` | dto | `api-dtos` | CreateQuotes |
| `DistanceDto` | dto | `api-dtos` | Distance |
| `EmailNotificationDto` | dto | `services` | EmailNotification |
| `FeedbackDto` | dto | `api-dtos` | Feedback |
| `HrefDto` | dto | `api-dtos` | Href |
| `ItemDto` | dto | `api-dtos` | Item |
| `ItemsDto` | dto | `api-dtos` | Items |
| `ItineraryDto` | dto | `api-dtos` | Itinerary |
| `LinkDto` | dto | `api-dtos` | Link |
| `ListerDto` | dto | `api-dtos` | Lister |
| `ListingBidItemDto` | dto | `api-dtos` | ListingBidItem |
| `ListingCreateBidItemDto` | dto | `api-dtos` | ListingCreateBidItem |
| `ListingIdDto` | dto | `api-dtos` | ListingId |
| `ListingInfoDto` | dto | `api-dtos` | ListingInfo |
| `ListingItemDto` | dto | `api-dtos` | ListingItem |
| `LocationDto` | dto | `api-dtos` | [Location](../domains/entities/Location.md) |
| `MileageBandDto` | dto | `api-dtos` | MileageBand |
| `MileageBandJsonVo` | dto | `db-entities` | MileageBandJsonVo |
| `OktaIdentifyCredentialsReqDto` | dto | `services` | OktaIdentifyCredentialsReq |
| `OktaIdentifyReqDto` | dto | `services` | OktaIdentifyReq |
| `OktaIntrospectResDto` | dto | `services` | OktaIntrospectRes |
| `OktaLoginDto` | dto | `services` | OktaLogin |
| `OktaLoginSuccessDto` | dto | `services` | OktaLoginSuccess |
| `PricetronErrorDto` | dto | `services` | PricetronError |
| `PricetronInputDto` | dto | `services` | PricetronInput |
| `PricetronOutputValuesDto` | dto | `services` | PricetronOutputValues |
| `PricetronRequestDto` | dto | `services` | Pricetron |
| `PricetronRetailVehicleActionDto` | dto | `services` | PricetronRetailVehicleAction |
| `PricetronTokenResponseDto` | dto | `services` | PricetronToken |
| `PricetronVehicleDto` | dto | `services` | PricetronVehicle |
| `PricingDto` | dto | `api-dtos` | Pricing |
| `QuoteDto` | dto | `api-dtos` | [Quote](../domains/entities/Quote.md) |
| `RouteDto` | dto | `api-dtos` | [Trip](../domains/entities/Trip.md) |
| `SlidingScaleDto` | dto | `api-dtos` | SlidingScale |
| `SlidingScaleJsonVo` | dto | `db-entities` | SlidingScaleJsonVo |
| `SurchargeDto` | dto | `api-dtos` | Surcharge |
| `SurchargeJsonVo` | dto | `db-entities` | SurchargeJsonVo |
| `TimeFrameDto` | dto | `api-dtos` | TimeFrame |
| `TimeFrameJsonVo` | dto | `db-entities` | TimeFrameJsonVo |
| `TimeFrameValueDto` | dto | `api-dtos` | TimeFrameValue |
| `UShipClientImpl` | dto | `services` | UShipClientImpl |
| `UShipPaymentsDto` | dto | `api-dtos` | UShipPayments |
| `UpdateCompanyBotConfigDto` | dto | `api-dtos` | UpdateCompanyBotConfig |
| `UpdateCompanyConfigDto` | dto | `api-dtos` | UpdateCompanyConfig |
| `UpdateMileageBandDto` | dto | `api-dtos` | UpdateMileageBand |
| `UserContext` | dto | `commons` | UserContext |
| `ValueObjDto` | dto | `api-dtos` | ValueObj |
| `WayPointDto` | dto | `api-dtos` | WayPoint |
| `WebbotRequest` | dto | `services` | Webbot |
| `WebbotResponse` | dto | `services` | Webbot |
<!-- entities-end -->
