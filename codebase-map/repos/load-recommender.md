---
repo: load-recommender
path: ~/projects/ship-cars-usa/load-recommender
stack: Java/Quarkus 3.27.5
domain: listings-trade
shape: multi-module (13 poms)
last-synced-commit: 6e67d1d86d5827be8e0d8c65cbb16fe5e5d31673
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# load-recommender

## What it is
Quarkus 3.27.5 / Java 21 service (project version 0.3.0) that **recommends freight loads to carriers** from saved preferences and ML signals. Subscribes to ML-recommendation output and CTMS load events, fetches posting details from `posting-backend` (directly and via `impersonator` for company-scoped reads), applies per-user daily email caps, and emits email + push notifications through `notification-orchestrator`. Tracks notification status (sent/seen/read) and keeps a sliding window of sent-emails for dedup. `README.md:1`: "Service for storing and managing load recommendations." Sister to `saved-search-handler` — same notification surface, different source (ML here vs. user-saved filters there).

## How it fits
- Consumes API of: `posting-backend` (via `PostingsClient` and `PostingsImpersonatorClient`, both built on the Ship.Cars `quarkus-webclient` extension `WebClientImpl` — wired in `services/.../config/PostingsClientProvider.java:16-31`). URLs come from plain props `load-recommender.postings-service-url` / `.impersonator-service-url` (`application.properties:69-70`), **not** `quarkus.rest-client.*`. The prod `WebClientImpl` producer sets **no connect/read timeout and no retry** (`WebClientImplConfig.java:16-23`); only the dev/test producer sets `connectTimeoutMs=5000` + retry.
- Publishes events to: Pub/Sub `events-topic` (via `EventsService`), `notification-orchestrator.email-topic` (via `NotificationOrchestratorClient`), and `ship.cars.notification.topic` (notification extension, used by `NotificationSenderService`).
- Subscribes to: Pub/Sub `ml-recommender-subscription` (ML output → `LoadRecommendationListener`), `ctms-subscription` (load + company-label events → `CtmsPubSubListener`), `sent-emails-subscription` (→ `SavedSearchSentEmailsListener`), `notification-orchestrator.email-events-subscription` (→ `NotificationOrchestratorEmailEventListener`), and `company-subscription-v2` / `user-subscription-v2` (handled by the Ship.Cars user-syncer extension, `db-syncer/.../sync/config/UserManagementSyncConfig.java:32-34`).
- Owns data store: PostgreSQL default datasource (JDBC, Hibernate ORM `validate`, `jdbc.max-size=16`, `application.properties:3-6,22-24`); plus two **reactive** secondary datasources `usermanagement-db` and `ctms-db` (both `reactive.max-size=10`, `health-exclude=true`, lines 8-20) holding replicated user/company/CTMS state.

## Build / test / run
```
./mvnw clean package -DskipTests
./mvnw quarkus:dev
# 13 poms (root + 12 modules): application, services, db-entities, db-migration,
#   db-syncer, resources, api-dtos, commons, configuration, infra, test-utils,
#   coverage-report. Native build via GraalVM/Mandrel.
```

## Key abstractions
- `RecommendationService` — `services/.../services/RecommendationService.java` — paginated recommendations by status; sort/filter; dedup window. Also fans work out over the in-JVM Vert.x `eventBus` (`RECOMMENDATIONS_CREATED_ADDRESS`, `SEND_PUSH_NOTIFICATIONS_ADDRESS`, ~lines 911-949) which then feeds the Pub/Sub publishers.
- `CtmsPubSubListener` — `services/.../services/listeners/CtmsPubSubListener.java` — consumes `ctms-subscription`; `handleCompanyLabelMessage` maintains private-load eligibility (see gotchas).
- `LoadRecommendationListener` — `services/.../services/listeners/LoadRecommendationListener.java:25-38` — consumes `ml-recommender-subscription`; turns model picks into per-user recommendation rows.
- `CarrierRecommendationService` — `services/.../services/CarrierRecommendationService.java` — fetches posting details from `posting-backend` for a recommended load.
- `NotificationSenderService` — `services/.../services/NotificationSenderService.java` — dispatches email + push; enforces daily email limits; `publishFallbackEmail` at line 182.
- `EventsService` — `services/.../services/EventsService.java:42-59` — publishes read/seen/sent state to `events-topic` via `PubSubPublisherSync`.
- `NotificationOrchestratorClient` — `services/.../NotificationOrchestratorClient.java:33` — publishes to `notification-orchestrator.email-topic`.

## Don't-do-here / gotchas
- **preferred_carrier vs. verified naming trap (SCP-15133, this HEAD).** `CtmsPubSubListener.handleCompanyLabelMessage` now gates private-load eligibility on the company label **`preferred_carrier`** (constant `PREFERRED_CARRIER_KEY`, `CtmsPubSubListener.java:33`; condition ~lines 171-181), **not** `verified`. But the table (`shipper_verified_carriers`), entity (`ShipperVerifiedCarrierEntity`), repo, and methods (`setVerifiedBy` / `removeVerifiedBy`) still carry the legacy "verified" naming. When reading this code, remember the *semantic* driver is the `preferred_carrier` label; the "verified" names are historical. Also updated `resources/.../fetch-shipper-verified-carriers.sql`. Ties to memory note `scp14054_preferred_carrier_label_mismatch` — this is the fix side.
- **No prod REST-client timeouts.** The `WebClientImpl` prod producer (`WebClientImplConfig.java:16-23`) applies defaults only; a slow `posting-backend` stalls the recommendation/send path. (Not a `quarkus.rest-client.*` service — there are no MP REST clients here.)
- **Datasource pools: JDBC 16 + two reactive 10** — recommendation flushes are bursty; size up if ML output rate climbs.
- **No transactional outbox** — notifications publish directly to Pub/Sub. A commit-then-publish-fail loses an email; ack-after-publish can duplicate. Confirm listener retry posture on publish failure.
- **`ctms-db` and `usermanagement-db` are `health-exclude=true`** — their outages will not surface in the readiness probe; monitor them separately.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/posting-backend.md` — primary upstream.
- `~/projects/codebase-map/repos/notification-orchestrator.md` — email-channel sink (topic + events-subscription).
- `~/projects/codebase-map/repos/saved-search-handler.md` — sister service; got the parallel `preferred_carrier` fix (SCP-15132).
- `~/projects/codebase-map/relations/rest-client-registry.md` — no-timeout posture.
- `~/projects/codebase-map/domains/listings-trade.md` — domain context.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `CarrierRecommendationEntity` | jpa | `db-entities` | CarrierRecommendation |
| `CompanyEntity` | jpa | `db-entities` | [Company](../domains/entities/Company.md) |
| `DeletedLoadEntity` | jpa | `db-entities` | DeletedLoad |
| `NotificationSettingsEntity` | jpa | `db-entities` | NotificationSettings |
| `RecommendationEntity` | jpa | `db-entities` | Recommendation |
| `SentEmailEntity` | jpa | `db-entities` | SentEmail |
| `SentPushNotificationEntity` | jpa | `db-entities` | SentPushNotification |
| `ShipperVerifiedCarrierEntity` | jpa | `db-entities` | ShipperVerifiedCarrier |
| `UserEntity` | jpa | `db-entities` | [User](../domains/entities/User.md) |
| `CarrierRecommendation` | dto | `services` | CarrierRecommendation |
| `CtmsGeoPointDto` | dto | `services` | CtmsGeoPoint |
| `CtmsLoadMessageDto` | dto | `services` | CtmsLoadMessage |
| `DbCompany` | dto | `db-syncer` | [Company](../domains/entities/Company.md) |
| `DbUser` | dto | `db-syncer` | [User](../domains/entities/User.md) |
| `DbUserRow` | dto | `db-syncer` | DbUserRow |
| `EmailDataDto` | dto | `services` | EmailData |
| `EmailNotification` | dto | `services` | EmailNotification |
| `EventDto` | dto | `api-dtos` | — |
| `LoadDto` | dto | `api-dtos` | [Load](../domains/entities/Load.md) |
| `LoadRecommendationDto` | dto | `api-dtos` | LoadRecommendation |
| `LoadRecommenderNotificationDto` | dto | `services` | LoadRecommenderNotification |
| `LoadSyncDto` | dto | `services` | LoadSync |
| `MarkNotificationsDto` | dto | `resources` | MarkNotifications |
| `NotificationSettings` | dto | `services` | NotificationSettings |
| `NotificationSettingsDto` | dto | `api-dtos` | NotificationSettings |
| `PushNotification` | dto | `services` | PushNotification |
| `Recommendation` | dto | `services` | Recommendation |
| `RecommendationMessageDto` | dto | `api-dtos` | RecommendationMessage |
| `RecommendationScore` | dto | `api-dtos` | RecommendationScore |
| `RecommendationSort` | dto | `api-dtos` | RecommendationSort |
<!-- entities-end -->
