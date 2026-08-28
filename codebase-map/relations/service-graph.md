# Service Graph

Cross-service "who calls whom" relationships. Edges below come from the **130 seed shadow docs** to date (v1: 7; depth-pass 1: +7; depth-pass 2: +6; depth-pass 3: +8; depth-pass 4: +7; depth-pass 5: +9; depth-pass 6: +8; depth-pass 7: +6; depth-pass 8: +4; depth-pass 9: +6; depth-pass 10 / Phase 4.14: +4 (communication complete); depth-pass 11 / Phase 4.15: +4 platform-extension libs; depth-pass 12 / Phase 4.16: +2; depth-pass 13 / Phase 4.17: version-matrix; depth-pass 14 / Phase 4.18: +4 operations; depth-pass 15 / Phase 4.19: +5 closing identity + integrations; depth-pass 16 / Phase 4.20: +6 closing listings-trade; depth-pass 17 / Phase 4.21: +6 closing pricing-billing; depth-pass 18 / Phase 4.22: +8 closing operations; depth-pass 19 / Phase 4.23: +4 platform extensions; depth-pass 20 / Phase 4.24: +15 closing analytics; depth-pass 21 / Phase 4.25: +4 trailing Quarkus extensions (Quarkus-extension catalog now **14/14 complete**). **7 of 9 domains catalog-complete**.

## Conventions

- Rows are directed: **caller → callee**.
- `protocol` is one of: `REST`, `Kafka`, `Pub/Sub`, `gRPC`, `JDBC`, `Mongo`, `Redis`, `webhook`, `EventBus` (Vert.x in-process), `external` (third-party SaaS).
- `evidence` is `path:line` when available, else `shadow:<repo-name>` if the only source is the shadow doc.
- `last-confirmed` — `YYYY-MM-DD`. Treats fleet-review on 2026-05-07 and the 2026-05-08 deepening pass as authoritative until re-checked.

## Edges (REST + EventBus + Pub/Sub fan-out)

### From the original fleet-review seeds

| Caller | Callee | Protocol | Evidence | Last confirmed |
|---|---|---|---|---|
| `aaag-integration` | ASI GraphQL (external Auction Edge) | external | `services/.../AsiPushServiceImpl.java:130-161` | 2026-05-07 |
| `aaag-integration` | Auction Edge Pub/Sub topic *(consumes)* | Pub/Sub | `services/.../listeners/AuctionEdgePubSubListener.java` | 2026-05-07 |
| `aaag-integration` | (internal subscribers) via `eventBus.send()` | EventBus | `services/.../listeners/PostingPubSubListener.java:57-60` | 2026-05-07 |
| `bi-databricks-backend` | Databricks OAuth + Workspace API | external | `service/DatabricksRestClient.java` | 2026-05-07 |
| `chat-backend` | `notification-backend` | REST | `NotificationServiceImpl.broadcastChanges()` *(synchronous, swallows errors)* | 2026-05-07 |
| `chat-backend` | `user-backend` | REST | shadow:chat-backend | 2026-05-07 |
| `chat-backend` | `media-proxy` | REST | `DiscussionController.java:86, 132` | 2026-05-07 |
| `chat-backend` | UserState Pub/Sub *(consumes)* | Pub/Sub | `UserStateConsumer.java:90-103` | 2026-05-07 |
| `contract-pricing-backend` | Django carriers service | REST | `services/.../DjangoServiceImpl.java` | 2026-05-07 |
| `contract-pricing-backend` | `impersonator` | REST | `ImpersonatorClient.java` *(no caller-side timeout)* | 2026-05-07 |
| `contract-pricing-backend` | `user-backend` | REST | `UserManagementServiceImpl.java:84-99` | 2026-05-07 |
| `contract-pricing-backend` | `location-provider` | REST | `LocationServiceImpl.java:187-210` | 2026-05-07 |
| `contract-pricing-backend` | Company Pub/Sub *(consumes)* | Pub/Sub | `CompanyPubSubListener.java:39-50` | 2026-05-07 |
| `integrations-backend` (logytext) | Logytext API | external | shadow:integrations-backend | 2026-05-07 |
| `integrations-backend` (logytext) | Logytext webhook Pub/Sub *(consumes)* | Pub/Sub | `logytext/.../LogytextPubSubConsumer.java:58-120` *(no HMAC verification)* | 2026-05-07 |
| `integrations-backend` (quickbooks) | QuickBooks API | external | `quickbooks/.../QuickbooksFacade.java:37-65` | 2026-05-07 |
| `integrations-backend` (axe) | Axe API | external | `axe/.../client/AxeClient.java:44-68` | 2026-05-07 |
| `integrations-backend` (axe) | Axe webhook Pub/Sub *(consumes)* | Pub/Sub | `axe/.../AxeWebhookPubSubConsumer` | 2026-05-07 |
| `integrations-backend` (twilio) | Twilio API | external | shadow:integrations-backend | 2026-05-07 |
| `integrators-data-bridge` | `posting-backend` Postgres *(reads)* | JDBC | `services/.../posting/LoadLegProcessor.java:117, 133, 148` | 2026-05-07 |
| `integrators-data-bridge` | `inventory-backend` Postgres *(reads)* | JDBC | `services/.../InventoryProcessor` | 2026-05-07 |
| `integrators-data-bridge` | `autoims-backend` Postgres *(reads)* | JDBC | `services/.../autoims/AutoImsProcessor.java:99-100` | 2026-05-07 |
| `integrators-data-bridge` | `contract-pricing-backend` Postgres *(reads)* | JDBC | `services/.../ContractPricingProcessor` | 2026-05-07 |
| `integrators-data-bridge` | centralized target Postgres *(writes)* | JDBC | `application.properties:74` | 2026-05-07 |

### Added 2026-05-08 from the platform-services deepening

| Caller | Callee | Protocol | Evidence | Last confirmed |
|---|---|---|---|---|
| `user-backend` | `notification-backend` (via notification-client lib) | REST | shadow:user-backend | 2026-05-08 |
| `user-backend` | `attachment-backend` | REST | shadow:user-backend (3-min hardcoded timeout) | 2026-05-08 |
| `user-backend` | `metadata` | REST | shadow:user-backend | 2026-05-08 |
| `user-backend` | `media-proxy` | REST | shadow:user-backend | 2026-05-08 |
| `user-backend` | Keycloak Admin API | external | shadow:user-backend | 2026-05-08 |
| `user-backend` | `user-state-v2` Pub/Sub topic *(publishes via outbox)* | Pub/Sub | `OutboxPollerImpl.java` (cron 0/10) | 2026-05-08 |
| `user-backend` | `company-state-v2` Pub/Sub topic *(publishes via outbox)* | Pub/Sub | `OutboxPollerImpl.java` | 2026-05-08 |
| `user-backend` | `notification` Pub/Sub topic *(publishes via outbox)* | Pub/Sub | `OutboxPollerImpl.java` | 2026-05-08 |
| `user-backend` | `payment-backend` Pub/Sub subscription *(consumes Stripe webhooks)* | Pub/Sub | `PaymentBackendConsumer.java` | 2026-05-08 |
| `user-backend` | `usage-record` Pub/Sub subscription *(consumes)* | Pub/Sub | shadow:user-backend | 2026-05-08 |
| `notification-backend` | `user-backend` | REST | `UserManagementClientImpl` `GET /internal/v2/users/{id}` | 2026-05-08 |
| `notification-backend` | `notification-state` Pub/Sub *(consumes)* | Pub/Sub | `NotificationConsumer.java` *(silent ack on exception, P0)* | 2026-05-08 |
| `notification-backend` | `user-state` Pub/Sub *(consumes)* | Pub/Sub | `UserStateConsumer` | 2026-05-08 |
| `notification-backend` | `loadboard-state` Pub/Sub *(consumes)* | Pub/Sub | shadow:notification-backend | 2026-05-08 |
| `notification-backend` | `notification` Pub/Sub topic *(publishes)* | Pub/Sub | shadow:notification-backend | 2026-05-08 |
| `notification-backend` | SendGrid (email) | external | Firebase / Twilio / SendGrid SDKs in classpath | 2026-05-08 |
| `notification-backend` | Twilio (SMS) | external | shadow:notification-backend | 2026-05-08 |
| `notification-backend` | Firebase (push) | external | shadow:notification-backend | 2026-05-08 |
| `media-proxy` | Google Cloud Storage | external | `service/gcs_storage.go` | 2026-05-08 |
| `impersonator` | Keycloak (token-exchange + refresh) | external | `service/keycloak.go:50-99` *(no http.Client.Timeout, P0)* | 2026-05-08 |
| `impersonator` | `user-backend` (`/internal/v2/companies/{id}/owner` — symbolic name `company-owner-api`) | REST | `service/auth.go:40, 67`; verified vs `V2InternalCompanyController` | 2026-05-11 |
| `impersonator` | `user-backend` (`/internal/v2/users/{id}` — symbolic name `user-api`) | REST | `service/auth.go:40, 67`; verified vs `V2InternalUserAccountController` | 2026-05-11 |
| `impersonator` | API gateway *(proxy target)* | REST | `service/proxy.go` `API_GATEWAY_BASE_URL` | 2026-05-08 |
| `location-provider` | Google Maps API | external | `services/config/GcpServiceProducer.java` | 2026-05-08 |
| `location-provider` | Elasticsearch *(cache)* | external | `services/cache/impl/ESCacheServiceImpl.java` | 2026-05-08 |
| `location-provider` | Redis *(cache)* | external | `services/cache/impl/RedisCacheServiceImpl.java` | 2026-05-08 |

### Added 2026-05-08 (Phase 4.6) from request-path-critical seeds

| Caller | Callee | Protocol | Evidence | Last confirmed |
|---|---|---|---|---|
| `payment-backend` | `user-backend` | REST | `@RegisterRestClient(configKey="user-management")` *(`@Retry(7×)` no timeout, P0)* | 2026-05-08 |
| `payment-backend` | RoadSync API | external | `@RegisterRestClient(configKey="roadsync-api")` *(retry no timeout)* | 2026-05-08 |
| `payment-backend` | Stripe API | external | Stripe SDK; webhook signature validated | 2026-05-08 |
| `payment-backend` | `topics-payment-notification` *(publishes)* | Pub/Sub | `MessageSenderServiceImpl` | 2026-05-08 |
| `payment-backend` | `topics-payment-update` *(publishes)* | Pub/Sub | shadow:payment-backend | 2026-05-08 |
| `payment-backend` | `topics-transaction-update` *(publishes)* | Pub/Sub | shadow:payment-backend | 2026-05-08 |
| `payment-backend` | `topics-bank-account-update` *(publishes)* | Pub/Sub | shadow:payment-backend | 2026-05-08 |
| `payment-backend` | `subscription-bank-account-update` *(consumes from user-backend)* | Pub/Sub | `BankAccountUpdatePubSubListener` | 2026-05-08 |
| `quote-manager-backend` | `posting-backend` (managed-orders v1/v3/v4) | REST | shadow:quote-manager-backend *(WebClient, no timeout)* | 2026-05-08 |
| `quote-manager-backend` | `location-provider` | REST | shadow:quote-manager-backend | 2026-05-08 |
| `quote-manager-backend` | `user-backend` (v2 company endpoint) | REST | shadow:quote-manager-backend | 2026-05-08 |
| `quote-manager-backend` | `metadata` | REST | shadow:quote-manager-backend | 2026-05-08 |
| `quote-manager-backend` | `notification-backend` | REST | shadow:quote-manager-backend | 2026-05-08 |
| `quote-manager-backend` | `quote-send-state` *(publishes)* | Pub/Sub | `MessageSenderImpl` | 2026-05-08 |
| `quote-manager-backend` | `quote-notification` *(publishes)* | Pub/Sub | shadow:quote-manager-backend | 2026-05-08 |
| `quote-manager-backend` | `notification-state` *(publishes)* | Pub/Sub | shadow:quote-manager-backend | 2026-05-08 |
| `quote-manager-backend` | `posting-state` *(publishes)* | Pub/Sub | shadow:quote-manager-backend | 2026-05-08 |
| `quote-manager-backend` | `quote-receive-state` *(consumes)* | Pub/Sub | `QuoteStateConsumer` | 2026-05-08 |
| `quote-manager-backend` | `payment-notification` *(consumes)* | Pub/Sub | shadow:quote-manager-backend | 2026-05-08 |
| `loadboard-backend` | CTMS Django (sync REST) | external | shadow:loadboard-backend | 2026-05-08 |
| `loadboard-backend` | `location-provider` | REST | `quarkus.rest-client.location-provider.url` *(no timeout)* | 2026-05-08 |
| `loadboard-backend` | `media-proxy` | REST | `quarkus.rest-client.media-proxy.url` *(no timeout)* | 2026-05-08 |
| `loadboard-backend` | `metadata`, `attachment-backend`, `dataone` | REST | shadow:loadboard-backend | 2026-05-08 |
| `loadboard-backend` | Keycloak (OIDC) | external | shadow:loadboard-backend | 2026-05-08 |
| `loadboard-backend` | `temporal-workflows-events-topic` *(publishes)* | Pub/Sub | shadow:loadboard-backend | 2026-05-08 |
| `loadboard-backend` | `loadboard-events-topic` *(publishes)* | Pub/Sub | shadow:loadboard-backend | 2026-05-08 |
| `loadboard-backend` | `loadboard-notifications-topic` *(publishes)* | Pub/Sub | shadow:loadboard-backend | 2026-05-08 |
| `loadboard-backend` | `notification` topic *(publishes stale-posting alerts)* | Pub/Sub | shadow:loadboard-backend | 2026-05-08 |
| `loadboard-backend` | `ctms-subscription` *(consumes)* | Pub/Sub | `LoadboardPubSubListener` | 2026-05-08 |
| `loadboard-backend` | `user-subscription` *(consumes)* | Pub/Sub | `LoadboardPubSubListener` | 2026-05-08 |
| `loadboard-backend` | `company-subscription` *(consumes)* | Pub/Sub | `LoadboardPubSubListener` | 2026-05-08 |
| `inventory-backend` | `posting-backend` *(via `impersonator` prefix)* | REST | `PostingClientImpl` (no timeout) | 2026-05-08 |
| `inventory-backend` | `location-provider`, `media-proxy`, `dataone`, `user-backend`, `attachment-backend` | REST | shadow:inventory-backend | 2026-05-08 |
| `inventory-backend` | `notification` topic *(publishes)* | Pub/Sub | shadow:inventory-backend | 2026-05-08 |
| `inventory-backend` | `events` topic *(publishes)* | Pub/Sub | shadow:inventory-backend | 2026-05-08 |
| `posting-backend` | `inventory-backend` (`/v1/units`) | REST | `InventoryClientImpl` *(via impersonator prefix)* | 2026-05-08 |
| `posting-backend` | `loadboard-backend` (legacy + v3) | REST | `ShipcarsLoadBoardClientImpl` *(read=PT150S, connect=PT60S, retry 5×)* — **the only fleet client with explicit timeouts** | 2026-05-08 |
| `posting-backend` | `user-backend`, `attachment-backend`, `contract-pricing-backend`, `rateengine`, `driveaway-backend`, `quote-manager-backend`, `payment-backend`, `location-provider`, `media-proxy`, `metadata` | REST | shadow:posting-backend | 2026-05-08 |
| `posting-backend` | central-dispatch (external) | external | shadow:posting-backend | 2026-05-08 |
| `posting-backend` | `posting-state`, `posting-v2-state`, `contacts-state`, `um-usage-record` *(publishes via outbox)* | Pub/Sub | `OutboxMessageService` (`application.properties:264-283`, ShedLock 225s, max-retries 5) | 2026-05-08 |
| `posting-backend` | `loadboard-state`, `quote-state`, `company-state`, `user-state`, `loadboard-v3-events`, `ml-bot-order`, `posting-job-events` *(consumes)* | Pub/Sub | various `PubSubConsumer` impls | 2026-05-08 |
| `notification-orchestrator` | SendGrid (email) | external | via `ship.cars.quarkus.extensions.notification` 1.3.0 | 2026-05-08 |
| `notification-orchestrator` | `email-subscription` *(consumes `SendEmailDto`)* | Pub/Sub | `EmailListener` | 2026-05-08 |
| `notification-orchestrator` | `user-subscription` *(consumes for local user-state replication)* | Pub/Sub | `UserManagementProducer` (db-syncer) | 2026-05-08 |
| `notification-orchestrator` | `company-subscription` *(consumes for local company-state replication)* | Pub/Sub | `UserManagementProducer` | 2026-05-08 |

### Added 2026-05-11 (Phase 4.7) from depth-pass 3 seeds

| Caller | Callee | Protocol | Evidence | Last confirmed |
|---|---|---|---|---|
| `load-recommender` | `posting-backend` *(via `impersonator`)* | REST | `PostingsClient` / `PostingsImpersonatorClient` *(no timeout)* | 2026-05-11 |
| `load-recommender` | `events-topic` *(publishes)* | Pub/Sub | shadow:load-recommender | 2026-05-11 |
| `load-recommender` | `notifications-topic` *(publishes to `notification-orchestrator`)* | Pub/Sub | shadow:load-recommender | 2026-05-11 |
| `load-recommender` | `ml-recommender-subscription`, `ctms-subscription`, `company-subscription-v2`, `user-subscription-v2`, `sent-emails-subscription` *(consumes)* | Pub/Sub | shadow:load-recommender | 2026-05-11 |
| `saved-search-handler` | `loadboard-backend` | REST | `LoadboardFetcherSyncService` *(no timeout)* | 2026-05-11 |
| `saved-search-handler` | Elasticsearch *(percolate queries, size=10000)* | external | shadow:saved-search-handler | 2026-05-11 |
| `saved-search-handler` | `notifications-topic`, `sent-emails-topic`, `sync-topic` *(publishes)* | Pub/Sub | shadow:saved-search-handler | 2026-05-11 |
| `saved-search-handler` | `ctms-subscription`, `user-subscription-v2`, `company-subscription` *(consumes)* | Pub/Sub | `LoadEventProcessor` | 2026-05-11 |
| `load-bookmark-backend` | `posting-backend` | REST | `PostingClientProvider` *(no timeout)* | 2026-05-11 |
| `load-bookmark-backend` | `notification-topic` *(publishes)* | Pub/Sub | `BookmarkChangeListener` | 2026-05-11 |
| `load-bookmark-backend` | carrier-TMS subscription *(consumes posting/vehicle events)* | Pub/Sub | `PlatformEventsListener` | 2026-05-11 |
| `load-bookmark-service` | etcd v3 *(writes bookmark JSON, no CAS, `eval()` on reads — P0)* | external | `service/synchronize_*.py` | 2026-05-11 |
| `load-bookmark-service` | Pub/Sub `subscriptions/dido` *(consumes, always-ACK pattern)* | Pub/Sub | `Subscriber` + `on_pubsub_message` | 2026-05-11 |
| `invoices` | `payment-backend` | REST | `PaymentClient` *(`@Retry` no timeout, P0)* | 2026-05-11 |
| `invoices` | `posting-backend` *(via `impersonator`)* | REST | `PostingClient` | 2026-05-11 |
| `invoices` | `attachment-backend` | REST | `AttachmentClient` | 2026-05-11 |
| `invoices` | `user-backend` | REST | `UserManagementClient` | 2026-05-11 |
| `invoices` | `invoices-carrier-topic` *(publishes, no outbox)* | Pub/Sub | shadow:invoices | 2026-05-11 |
| `invoices` | `posting-subscription`, `ctms-subscription`, `payment-transactions-subscription` *(consumes)* | Pub/Sub | `PostingPubSubListener`, `PaymentTransactionPubSubListener` | 2026-05-11 |
| `fraud-detector` | `https://done.ship.cars` *(MSRP lookup, baseUri hardcoded)* | external | `VehicleClient` `@RegisterRestClient(baseUri=...)` | 2026-05-11 |
| `fraud-detector` | Slack | external | `SlackClient` *(no timeout)* | 2026-05-11 |
| `fraud-detector` | DataOne | external | shadow:fraud-detector | 2026-05-11 |
| `fraud-detector` | `fraud-alerts-topic` *(publishes, no outbox)* | Pub/Sub | shadow:fraud-detector | 2026-05-11 |
| `fraud-detector` | `platform-subscription`, `keycloak-subscription`, `user-management-user-subscription`, `user-management-company-subscription` *(consumes)* | Pub/Sub | `PlatformPubSubListener`, `KeyCloakPubSubListener`, etc. | 2026-05-11 |
| `autoims-backend` | AutoIMS *(external SOAP/REST)* | external | `AutoImsClientImpl` *(WebClient timeouts set programmatically)* | 2026-05-11 |
| `autoims-backend` | `location-provider` | REST | `LocationProviderClientImpl` (location-provider-spring-client 2.12.0) | 2026-05-11 |
| `autoims-backend` | `inventory-backend` *(via inventory client lib)* | REST | `InventoryClient` (ship-cars-inventory 2.16.0) | 2026-05-11 |
| `autoims-backend` | `metadata` | REST | `MetadataClient` (ship-cars-metadata 0.7.0) | 2026-05-11 |
| `lead-parser` | ShipperTMS *(target URL via env)* | REST | `ParseService` *(raw `new RestTemplate()`, no timeout, no retry, no error handling — P0)* | 2026-05-11 |

### Added 2026-05-11 (Phase 4.8) from platform + operations + analytics seeds

| Caller | Callee | Protocol | Evidence | Last confirmed |
|---|---|---|---|---|
| `driveaway-backend` | `location-provider` | REST | spring-client v3.20.0 *(no timeout)* | 2026-05-11 |
| `driveaway-backend` | `media-proxy` | REST | shadow:driveaway-backend *(no timeout)* | 2026-05-11 |
| `driveaway-backend` | `notification-backend` | REST | via notification-client lib *(no timeout)* | 2026-05-11 |
| `driveaway-backend` | `posting-backend` | REST | via posting-dtos *(no timeout)* | 2026-05-11 |
| `driveaway-backend` | `metadata` | REST | shadow:driveaway-backend | 2026-05-11 |
| `driveaway-backend` | Google Cloud Vision | external | `DecodingController` (vision API 3.73.0) | 2026-05-11 |
| `driveaway-backend` | Fingerprint Pro Server API | external | classpath v7.0.0 | 2026-05-11 |
| `public-tracking-backend` | Google reCAPTCHA | external | `CaptchaService` *(no explicit timeout)* | 2026-05-11 |
| `public-tracking-backend` | `location-provider` | REST | location-provider-spring-client 3.20.0 | 2026-05-11 |
| `public-tracking-backend` | `media-proxy` | REST | shadow:public-tracking-backend | 2026-05-11 |
| `public-tracking-backend` | Unleash | external | feature-toggle service | 2026-05-11 |
| `public-tracking-backend` | `load-info-state` *(consumes)* | Pub/Sub | `application.properties` | 2026-05-11 |
| `public-tracking-backend` | `ctms-state` *(consumes)* | Pub/Sub | `application.properties` | 2026-05-11 |
| `trip-planner` | CTMS (legacy Django) | REST | `CtmsClient` `@RegisterRestClient(configKey="ctms-api")` *(no timeout, P0)* | 2026-05-11 |
| `trip-planner` | `location-provider` | REST | `ship-cars-locationclient` 3.28.0 | 2026-05-11 |
| `trip-planner` | `user-backend` | REST | `usermanagement-dtos` 2.7.0 | 2026-05-11 |
| `trip-planner` | trip lifecycle / route-change topics *(publishes via `MessagePublisher` with orderingKey)* | Pub/Sub | shadow:trip-planner | 2026-05-11 |
| `user-activity-tracker` | `useractivitytracker.internal-subscription` *(consumes own published events)* | Pub/Sub | `UserActivityTrackerListener` | 2026-05-11 |
| `attachment-backend` | (URL-fetch via Vert.x WebClient) | external | `CONFIG_DOWNLOAD_*_TIMEOUT=PT60S` *(timeouts present — fleet-rare)* | 2026-05-11 |
| `attachment-backend` | `ATTACHMENT_CREATED_CHANNEL` *(in-process)* | EventBus | `AttachmentServiceImpl` *(single-node only; not cross-replica)* | 2026-05-11 |
| `metadata` | `${PUBSUB_METADATA_TOPIC}` *(publishes change events with per-tenant ordering key)* | Pub/Sub | `PubSubMessagePublisherImpl` *(no outbox — stale-cache risk)* | 2026-05-11 |
| `rateengine` | central-dispatch *(external)* | REST | `app/external/central_dispatch.py` `requests.Session()` *(no timeout — P0)* | 2026-05-11 |

### Inbound edges confirmed for newly-seeded callees

| Callee | Confirmed inbound from | Notes |
|---|---|---|
| `attachment-backend` | `user-backend`, `posting-backend`, `inventory-backend`, `invoices`, `loadboard-backend`, `notification-backend` | Highest-fanout platform callee in the fleet so far. |
| `metadata` | `invoices`, `posting-backend`, `quote-manager-backend`, `autoims-backend`, `loadboard-backend`, `inventory-backend`, `user-backend`, `driveaway-backend` | Read-mostly registry; its publish-on-write contract is the load-bearing piece. |
| `rateengine` | `posting-backend` | Quote-manager-backend / contract-pricing-backend likely also call it (REST clients exist there but not confirmed by grep in this pass). |
| `location-provider` | `contract-pricing-backend`, `loadboard-backend`, `inventory-backend`, `quote-manager-backend`, `public-tracking-backend`, `driveaway-backend`, `trip-planner`, `autoims-backend`, `posting-backend` | Highest-fanout operations callee. |

### Added 2026-05-11 (Phase 4.9) from integrations + communication seeds

| Caller | Callee | Protocol | Evidence | Last confirmed |
|---|---|---|---|---|
| `axe-call-integration` | AXE API (`https://agent.joinaxe.ai`) | external | `AxeApiClient` `@RegisterRestClient` *(`@Timeout(5000)` + `@Retry` + `@CircuitBreaker` — fleet-good pattern)* | 2026-05-11 |
| `axe-call-integration` | `impersonator` → `posting-backend` | REST | `ImpersonatorServiceClient` | 2026-05-11 |
| `axe-call-integration` | `${PUBSUB_NOTIFICATIONS_TOPIC}` *(publishes via `quarkus-notification-client`)* | Pub/Sub | shadow:axe-call-integration | 2026-05-11 |
| `axe-call-integration` | AXE webhook subscription *(consumes `call.ended`)* | Pub/Sub | `AxeWebhookPubSubListener` | 2026-05-11 |
| `integration-executor` | `attachment-backend` | REST | `AttachmentClient` *(`connect-timeout=30000`, `read-timeout=60000` — fleet-rare timeouts)* | 2026-05-11 |
| `integration-executor` | Acertus / Ally / CarsArrive / RunBuggy / SuperDispatch / Webhook / Logytext (external) | external | per-executor classes in `event-listener/executors/` | 2026-05-11 |
| `integration-executor` | `${executor.pubsub.logytext-topic}` *(publishes user-management events)* | Pub/Sub | shadow:integration-executor | 2026-05-11 |
| `integration-executor` | `${executor.pubsub.subscription}` *(consumes `IntegrationMessageDto`)* | Pub/Sub | `IntegrationMessageListener` | 2026-05-11 |
| `syncer` | `lm-posting`, `saved-search`, `platform`, `lbv3`, `location-history`, `metadata`, `trip-planner` PGs *(direct reads)* | JDBC | 6+ reactive datasources, `max-size=4` each | 2026-05-11 |
| `syncer` | Elasticsearch *(bulk writes)* | external | Quarkus ES extension | 2026-05-11 |
| `syncer` | `ship.cars.notification.topic` *(failure notifications via `quarkus-notification-client`)* | Pub/Sub | shadow:syncer | 2026-05-11 |
| `syncer` | `lm-contacts`, `lm-posting`, `carrier-company`, `carrier`, `loadboard`, `loadboard-v3`, `saved-search-percolate`, `load-location-log`, `metadata`, `trip-planner` *(consumes ~10 subs)* | Pub/Sub | per-source listeners | 2026-05-11 |
| `synclink-backend` | `impersonator` → `posting-backend` | REST | `ImpersonatorServiceClient` *(no timeout)* | 2026-05-11 |
| `synclink-backend` | `synclink-chrome-extension` *(inbound HTTP)* | REST | `LoadStateResource` | 2026-05-11 |
| `webhook-relay` | GitHub *(inbound webhooks)* | webhook | `handlers/webhooks.go` (HMAC-SHA256 verified) | 2026-05-11 |
| `webhook-relay` | N configured downstream URLs *(fan-out)* | REST | `services/forwarding.go` *(sequential, exponential backoff, no DLQ)* | 2026-05-11 |
| `pusher` | `ship.cars.notification.topic` *(publishes via `quarkus-notification-client`)* | Pub/Sub | shadow:pusher | 2026-05-11 |
| `pusher` | Redis (socket.io emitter → `socket-server`) | external | shadow:pusher | 2026-05-11 |
| `pusher` | `ctms-db`, `usermanagement-db` *(read-only PG)* | JDBC | shadow:pusher | 2026-05-11 |
| `pusher` | `ctms-subscription`, `loadmate-posting-subscription`, `loadmate-posting-v2-subscription`, `loadmate-quote-manager-subscription`, `user-subscription-v2`, `company-subscription-v2`, `metadata-subscription`, `integration-subscription`, `loadboard-v3-subscription` *(consumes ~10)* | Pub/Sub | per-source `PubSubConsumerBlocking` | 2026-05-11 |
| `socket-server` | Redis (`@socket.io/redis-emitter`) | external | shadow:socket-server | 2026-05-11 |
| `socket-server` | Keycloak (public-key fetch, 15-min cache) | external | shadow:socket-server | 2026-05-11 |
| `socket-server` | connected clients *(outbound WebSocket)* | WebSocket | shadow:socket-server | 2026-05-11 |
| `quarkus-notification-client` *(library)* | `ship.cars.notification.topic` *(blocking `future.get()` publish)* | Pub/Sub | `NotificationClientImpl` line ~235 | 2026-05-11 |

### Inbound edges confirmed in this pass

| Callee | Confirmed inbound from |
|---|---|
| `quarkus-notification-client` *(library; compile-time)* | 40+ Quarkus services in the fleet (single-highest binary-compat coupling) |
| `quarkus-user-syncer` *(library; compile-time)* | `notification-orchestrator`, `load-recommender`, `trip-planner`, `saved-search-handler` (via `db-syncer` modules) |
| `attachment-backend` | `integration-executor` (with explicit timeouts — adds to the 6 inbound from previous pass) |
| `posting-backend` *(via `impersonator`)* | `axe-call-integration`, `synclink-backend` |
| `socket-server` | `pusher` (via Redis emitter — confirms the parallel-emit pattern) |

### Added 2026-05-11 (Phase 4.10) from identity + ML + loadbuilder seeds

| Caller | Callee | Protocol | Evidence | Last confirmed |
|---|---|---|---|---|
| `keycloak` *(deployment image)* | GitHub Packages (Maven) *(build-time only)* | external | `Dockerfile` (4 plugin JAR fetches; requires `GITHUB_READ_TOKEN`) | 2026-05-11 |
| `keycloak` → `keycloak-events-plugin` *(bundled SPI)* → `${KC_SPI_EVENTS_TOPIC}` *(publishes enriched Keycloak events)* | Pub/Sub | `PublisherEventsListener` (ordering key = `event.userId`) | 2026-05-11 |
| `keycloak-events-plugin` | Mixpanel *(optional, Unleash-gated)* | external | `MixpanelEventListener` | 2026-05-11 |
| `keycloak-events-plugin` | Unleash *(toggle lookup)* | external | shadow:keycloak-events-plugin | 2026-05-11 |
| `keycloak-password-reset-link` | Keycloak session API *(in-process)* | in-process | `ResetPasswordResource` | 2026-05-11 |
| `hasher` | none | – | pure stateless service | 2026-05-11 |
| `ml-service-listener` | `location-provider` | REST | `httpx` async client *(no explicit timeout split, global `ML_SERVICE_TIMEOUT=1s`)* | 2026-05-11 |
| `ml-service-listener` | `cube.search-posting-events`, `load-recommender.feedback-events` *(consumes)* | Pub/Sub | `SearchSubscriber`, `FeedbackSubscriber` | 2026-05-11 |
| `ml-service-dispatcher` | `ml-model-rate`, `ml-model-confidence-{abs,pct}`, `ml-model-time-to-dispatch`, `ml-model-rate-multivehicle` | REST | `httpx` clients *(`ML_SERVICE_TIMEOUT=20s` shared; pool `max_connections=100`)* | 2026-05-11 |
| `ml-service-dispatcher` | DataOne *(vehicle specs)* | external | `services/dataone.py` *(timeout 30s, CSV fallback)* | 2026-05-11 |
| `ml-service-dispatcher` | Elasticsearch *(audit logs)* | external | `services/audit_logger.py` | 2026-05-11 |
| `ml-service-recommender` | `cars.ship.prod.ml.recommender` *(publishes)* | Pub/Sub | `services/pubsub/publisher` — consumed by `load-recommender` as `ml-recommender-subscription` | 2026-05-11 |
| `ml-service-recommender` | `cars.ship.prod.carrierlb.events-ml-recommender` *(consumes)* | Pub/Sub | shadow:ml-service-recommender | 2026-05-11 |
| `loadbuilder-backend` | `posting-backend`, `inventory-backend`, `quote-manager-backend`, `notification-backend`, `attachment-backend`/`media-proxy` | REST | spring-commons `WebClientImpl` *(no per-client timeouts)* | 2026-05-11 |
| `loadbuilder-backend` | `config.pubsub.topics.{worker,notification}` *(publishes)* | Pub/Sub | `InfraPubSubPublisherImpl` | 2026-05-11 |
| `loadbuilder-backend` | `config.pubsub.subscriptions.{worker,quoteManagerNotifications}` *(consumes)* | Pub/Sub | worker-app + api-app | 2026-05-11 |
| `loadbuilder-backend` | **GCS as primary store** *(serialized Java objects + JSON, optimistic locking)* | external | `StorageClientImpl` | 2026-05-11 |

### Recommendation chain now confirmed end-to-end (2026-05-11)

```
ml-service-recommender  (Python; PG x2; A/B; algorithms)
  ↓  publishes → cars.ship.prod.ml.recommender
load-recommender        (Quarkus; ml-recommender-subscription consumer; per-user dedup)
  ↓  publishes → notifications-topic
notification-orchestrator (Quarkus; SendGrid email)
  ↓  external SendGrid
user inbox / email
```

Feedback loop:
```
load-recommender (carrier interactions)
  ↓  publishes → load-recommender.feedback-events
ml-service-listener     (Python; PG sink for offline training)
```

### Added 2026-05-12 (Phase 4.11) from identity + ML + documents seeds

| Caller | Callee | Protocol | Evidence | Last confirmed |
|---|---|---|---|---|
| `keycloak-mfa-plugin` *(bundled SPI)* | `${mfa.notification-topic}` *(publishes SMS/email-code requests via `quarkus-notification-client`)* | Pub/Sub | shadow:keycloak-mfa-plugin | 2026-05-12 |
| `keycloak-mfa-plugin` | Keycloak `EventBuilder` *(`MFA_REQUESTED`/`MFA_SEND`/`MFA_CODE_*`/`MFA_RESEND` flow through `keycloak-events-plugin`)* | in-process | shadow:keycloak-mfa-plugin | 2026-05-12 |
| `keycloak-phone-login-plugin` *(bundled SPI)* | External URL shortener *(`phone-login.shortener_url`)* | REST | `UrlShortener` Apache HttpClient *(no timeout)* | 2026-05-12 |
| `keycloak-phone-login-plugin` | Optional Django legacy-auth backend | REST | `DjangoAuthenticator` *(inherits Keycloak HttpClientProvider ~30s)* | 2026-05-12 |
| `keycloak-phone-login-plugin` | Firebase Dynamic Links (`ydqx9.app.goo.gl`) *(deprecated by Google)* | external | `DeepLinkProvider` | 2026-05-12 |
| `keycloak-phone-login-plugin` | SMS topic *(via `quarkus-notification-client`)* | Pub/Sub | shadow:keycloak-phone-login-plugin | 2026-05-12 |
| `ml-bot-order-v2` | `oib-outbound-lm` + `oib-outbound-sf` *(publishes `ContractMessage` v2)* — **the source of `posting-backend`'s `ml-bot-order` subscription** | Pub/Sub | `OutboundPublisher` (`code/services/pubsub/publishers/outbound.py`) | 2026-05-12 |
| `ml-bot-order-v2` | `oib-inbound-lm` + `oib-inbound-sf` *(consumes `InboundIngestMessage`)* | Pub/Sub | `code/services/pubsub/subscribers/*` | 2026-05-12 |
| `ml-bot-order-v2` | LLM provider (Gemini 2.5-flash primary, 2.0-flash fallback) via LiteLLM Router *(60 s timeout)* | external | `code/services/llm/*` | 2026-05-12 |
| `ml-bot-order-v2` | `attachment-backend` *(signed URLs + form upload)* | REST | `httpx.AsyncClient` *(10 s per-request, `max_connections=100`, `max_keepalive=20`)* | 2026-05-12 |
| `ml-demand-forecasting` *(batch pipeline)* | source production PG *(`SOURCE_DB_*` — shadow caller pattern)* | JDBC | `code/data/*.py` *(direct reads from upstream service's PG)* | 2026-05-12 |
| `ml-demand-forecasting` | GCS `shipcars-platform-dev-demand-forecasting` *(model checkpoint)* | external | `code/model.py:load_model()` | 2026-05-12 |
| `ml-demand-forecasting` | sink PG (`ppm_fc`, `lpc_fc`, `rr_fc`) | JDBC | bulk pandas `to_sql` | 2026-05-12 |
| `ml-document-parser` | `cars.ship.qa.notification` *(hardcoded — same as `company-documents`)* | Pub/Sub | `code/settings.py` | 2026-05-12 |
| `company-documents` | `cars.ship.qa.notification` *(publishes shipper/carrier doc-lifecycle events)* | Pub/Sub | `pubsub/__init__.py:emit_message()` *(sync in async — risk)* | 2026-05-12 |
| `company-documents` | `media-proxy` *(file-fetch via `requests` sync client, 25 s timeout — fleet-rare)* | REST | `app/media_proxy.py` | 2026-05-12 |

### Sanctioned cross-DB read edges (ADR-0003 implementation)

| Reader | Source | Contract doc | Status |
|---|---|---|---|
| `integrators-data-bridge` | `posting-backend` PG | `relations/db-contracts/integrators-data-bridge--posting-backend.md` | draft v0.1 — column list pending |
| `integrators-data-bridge` | `inventory-backend` PG | `relations/db-contracts/integrators-data-bridge--inventory-backend.md` | draft v0.1 — column list pending |
| `integrators-data-bridge` | `autoims-backend` PG | `relations/db-contracts/integrators-data-bridge--autoims-backend.md` | draft v0.1 — column list pending |
| `integrators-data-bridge` | `contract-pricing-backend` PG | `relations/db-contracts/integrators-data-bridge--contract-pricing-backend.md` | draft v0.1 — column list pending |
| `syncer` | 6 upstream PGs (`lm-posting`, `saved-search`, `platform`/`lbv3`, `location-history`, `metadata`, `trip-planner`) | `relations/db-contracts/syncer--multi-source.md` | draft v0.1 — column list pending |
| `pusher` | `ctms-db`, `usermanagement-db` (read replicas) | `relations/db-contracts/pusher--user-and-ctms-dbs.md` | draft v0.1 — best migration target (user-state outbox already exists) |
| `ml-demand-forecasting` | source production PG | `relations/db-contracts/ml-demand-forecasting--source-pg.md` | draft v0.1 — **source service unidentified** |
| `ml-pricing-app` | `MONTWAY` MySQL + `RATE_ENGINE` PG | `relations/db-contracts/ml-pricing-app--montway-and-rate-engine.md` | draft v0.1 — **`MONTWAY` ownership unidentified**; ties to ADR-0005 rewrite |

**All 8 ADR-0003 contract docs published as drafts.** Each has a column-list TODO requiring reader-owner human input to close. Together they document the full **14 cross-service direct-DB-read edges** in the fleet.

### Added 2026-05-12 (Phase 4.12) from pricing + ML seeds

| Caller | Callee | Protocol | Evidence | Last confirmed |
|---|---|---|---|---|
| `ml-bot-order` *(v1)* | `posting-backend` *(via `impersonator`)* | REST | `httpx.AsyncClient` *(timeout=20s, max_connections=10)* | 2026-05-12 |
| `ml-bot-order` *(v1)* | Elasticsearch `lm-contacts` *(address resolution, no timeout)* | external | `code/services/ml/botordy/*` | 2026-05-12 |
| `ml-bot-order` *(v1)* | Google Gemini *(via legacy `google-genai` SDK; 15 s timeout)* | external | `GeminiClient` | 2026-05-12 |
| `ml-bot-order` *(v1)* | `sms-events` *(consumes)* | Pub/Sub | `SMSSubscriber` | 2026-05-12 |
| `ml-model-rate` | GCS `production-rate-engine-model` *(model artifacts at startup)* | external | `PredictorWorker.__await__` | 2026-05-12 |
| `ml-service-dispatcher` *(seeded earlier)* → `ml-model-rate` | REST | `RateClient` `httpx` *(`ML_SERVICE_TIMEOUT=20s`)* | confirmed via shadow:ml-service-dispatcher | 2026-05-12 |
| `uship-quotes` | Pricetron *(`pricetron`, `pricetronauth`)* | REST | `@RegisterRestClient` | 2026-05-12 |
| `uship-quotes` | `rateengine` | REST | `@RegisterRestClient` *(retry-on-rate-limit=5, no backoff)* | 2026-05-12 |
| `uship-quotes` | `location-provider` | REST | `@RegisterRestClient` | 2026-05-12 |
| `uship-quotes` | Node.js Playwright **webbot** *(BYPASS_SERVICE mode)* | REST | `@RegisterRestClient(configKey="webbot")` *(`connect-timeout=10s`, `read-timeout=120s` — fleet-rare timeouts)* | 2026-05-12 |
| `uship-quotes` | uShip listings + bidding API | external | `BotService` | 2026-05-12 |
| `uship-quotes` | `${NOTIFICATION_TOPIC}` *(publishes failed-bid alerts via outbox)* | Pub/Sub | shadow:uship-quotes | 2026-05-12 |
| `ml-pricing-app` *(batch + Streamlit)* | `MONTWAY` MySQL *(reads dispatched orders — shadow caller)* | JDBC | `fetch_matchings.py` | 2026-05-12 |
| `ml-pricing-app` *(batch)* | `RATE_ENGINE` PG *(reads predictions — shadow caller)* | JDBC | shadow:ml-pricing-app | 2026-05-12 |
| `ml-pricing-app` *(batch)* | `MONITORING` PG *(writes matched rows)* | JDBC | shadow:ml-pricing-app | 2026-05-12 |

### Added 2026-05-12 (Phase 4.13) from platform + operations + infrastructure seeds

| Caller | Callee | Protocol | Evidence | Last confirmed |
|---|---|---|---|---|
| `api-gateway` | every public-facing internal service (~13 upstreams: `cube`, `posting-backend`, `location-history-backend`, `user-backend`, `driveaway-backend`, `company-documents`, `crm-workflow`, `bookmarks`, `rateengine`, `saved-search-handler`, `public-tracking-backend`, plus legacy-token and rate-limits endpoints) | REST | `config/*.yaml` | 2026-05-12 |
| `api-gateway` | Keycloak (JWT verification, RSA public key) | external | `core/auth.go` | 2026-05-12 |
| `api-gateway` | Redis (rate-limit counters + legacy-token cache) | external | `core/rate_limit_manager.go` | 2026-05-12 |
| `cube` | `location-provider` | REST | `quarkus.rest-client.location-provider.url` *(no timeout)* | 2026-05-12 |
| `cube` | `media-proxy` | REST | `quarkus.rest-client.media-proxy.url` *(no timeout)* | 2026-05-12 |
| `cube` | `cube.search-posting-events` *(publishes search-event signals)* | Pub/Sub | `DomainEvents.SEARCH_POSTING_EVENT` — **the source of the topic consumed by `ml-service-listener` and `saved-search-handler`** | 2026-05-12 |
| `cube` | UM events *(consumes via `quarkus-user-syncer` extension)* | Pub/Sub | `db-sync/.../UserSyncConfig` | 2026-05-12 |
| `cube` | CTMS-orders / Loadmate event streams *(consumes)* | Pub/Sub | per-module event-listeners | 2026-05-12 |
| `cube` | Elasticsearch *(primary read-query backend)* | external | repo README: "Elasticsearch read query microservice" | 2026-05-12 |
| `location-history-backend` | `cars.ship.*.carrierlb.events`, `cars.ship.*.lh-load-location-log.events` *(consumes)* | Pub/Sub | `PlatformEventsListener` | 2026-05-12 |
| `location-history-backend` | `cars.ship.*.notification` *(publishes real-time location updates)* | Pub/Sub | `SocketNotificationsPublisher` + `PubSubPublisher` | 2026-05-12 |
| `syncer` *(seeded earlier)* | `location-history-backend` PG *(direct read — sanctioned)* | JDBC | shadow:location-history-backend + `db-contracts/syncer--multi-source.md` | 2026-05-12 |
| `negotiations-router` | `loadboard-backend` *(v3)* | REST | `@RegisterRestClient(configKey="loadboard-backend")` *(no timeout)* | 2026-05-12 |
| `negotiations-router` | CTMS legacy *(Django)* | REST | `@RegisterRestClient(configKey="ctms")` *(no timeout)* | 2026-05-12 |
| `negotiations-router` | Unleash *(routing toggle)* | external | shadow:negotiations-router | 2026-05-12 |
| `apache-camel-etl-demo` | source PG → target PG *(timer-driven incremental sync, every 3 s)* | JDBC | `BaseRoute` + `CustomersRoutes` + `CarsRoutes` | 2026-05-12 |

### Inbound edges confirmed in this pass

| Callee | Confirmed inbound |
|---|---|
| `dataone` | 8 services — `inventory-backend`, `fraud-detector`, `autoims-backend`, `quote-manager-backend`, `posting-backend`, `loadboard-backend`, `rateengine`, `ml-service-dispatcher`. **One of the highest-fanout read-only callees in the fleet.** |
| `api-gateway` | edge of the fleet — every external client goes through it. |
| every-public-facing-service | `api-gateway`'s outbound list confirms ~13 inbound edges (most already in the graph). |

### Added 2026-05-12 (Phase 4.14) from communication-domain depth pass

| Caller | Callee | Protocol | Evidence | Last confirmed |
|---|---|---|---|---|
| `ml-ui-chat` (Streamlit "Sofia" UI) | `ml-service-chat` `/customer/chat/conversation/{init,question,question/rate}` | REST | `code/app.py` *(`requests.post()` **no timeout** — fleet anti-pattern at the Python layer)* | 2026-05-12 |
| `ml-service-chat` | OpenAI Chat Completions (`gpt-4o-2024-05-13`, `temperature=0`, `seed=23`) | external | `services/ml/{carrier,customer}_chatgpt/service.py` *(uses legacy `openai.ChatCompletion.acreate` API removed in `openai>=1.0`; verify if alive)* | 2026-05-12 |
| `ml-service-chat` | `production` PG as user `rateengine` *(via `db-source` Tortoise connection — shadow caller)* | JDBC | `code/settings.py:TORTOISE_ORM[connections][db-source]` | 2026-05-12 |
| `chat-frontend` (`@shipcars/chat` single-spa MFE) | `chat-backend` REST API | REST | `src/services/http.service.ts` *(axios; no `timeout` configured; Bearer-token from `localStorage`)* | 2026-05-12 |
| `chat-frontend` ← *(DOM CustomEvent bridge)* | `new_socket_events.chatUpdated` *(receives events that originate at `socket-server` and are re-dispatched on `document` by the parent shell)* | DOM CustomEvent | `src/services/socket.service.ts` + `src/Chat/useSocket.tsx` | 2026-05-12 |
| `socket-server-old` *(deployed but frozen)* | Redis `main.redis.shipcars-platform-prod...` *(Socket.IO adapter cluster mode — **different Redis cluster from `socket-server`'s `socket.redis...`**)* | Redis | `helm/.../values-production.yaml` `configmap.REDIS_URL` | 2026-05-12 |
| *(legacy HS256 clients)* | `socket-server-old` *(Socket.IO 2.0.4 + HS256 JWT — parallel to Keycloak-RS256 `socket-server`)* | WebSocket | `index.js` + `helm/.../values-*.yaml` | 2026-05-12 |

**Communication domain is now catalog-complete for active services**: 10 of 12 stubs reached `seed` status (the remaining 2 — `devops-kubernetes-notificationss` + the `devops-tf-module-google-gke-cluster-notifications` Terraform module — are infrastructure config, not services, and were probably miscategorized into `communication` by name; they belong in `infrastructure`).

### New shadow-caller edge — sanctioned-DB-read addendum

| Reader | Source | Contract doc | Status |
|---|---|---|---|
| `ml-service-chat` | `rateengine` `production` PG (as user `rateengine`) | *(TODO — draft `db-contracts/ml-service-chat--rateengine-production-pg.md`)* | unsanctioned — needs ADR-0003 contract |

This brings the fleet total to **15 cross-service direct-DB-read edges** (was 14). Ties to ADR-0005 (`rateengine` EOL rewrite) — when `rateengine` migrates off Django 2.1.7 / its current PG schema, this read path must move with it.

### Added 2026-05-12 (Phase 4.17) — Quarkus version-drift matrix

No new edges in this pass. Published **`relations/quarkus-version-matrix.md`** quantifying the BOM-vs-extension version drift across the 34 Quarkus services. Key findings:

- **16 services on Quarkus 3.27.x (HEAD)**; remaining 18 split across 5 older minor versions (3.20.x, 3.15.x, 3.8.3, 2.9.1.Final).
- **`notification-orchestrator` (3.8.3) and `archiver` (2.9.1.Final) are the two major-version-lag outliers**; both **don't import the BOM** (they pin Quarkus directly), so they aren't part of the BOM bump cascade. Treat as P1 lifecycle items alongside `lead-parser` (Spring 2.1.4) and `rateengine` (Django 2.1.7).
- **`commons` (framework-neutral) drift is the biggest gap**: 15 services on 3.22.1, none on HEAD (3.28.0-SNAPSHOT); `notification-orchestrator` 2.4.0 and `payment-backend` 3.14.0 are the worst stragglers.
- **Property-name conventions are fleet-wide inconsistent** — the same dimension is named at least 3 different ways across the fleet. Standardizing is a one-mechanical-PR-per-repo job.
- **The fix-once recommendation**: pin Ship.Cars extensions in the BOM itself (alongside the existing Quarkiverse pins), eliminating the silent-drift class entirely.

### Added 2026-05-12 (Phase 4.16) from BOM + models-lib seeds

No new runtime edges (both seeds are libraries). The compile-time-edges table was updated with quantitative detail for both:

- **`shipcars-quarkus-bom` (~40+ consumers)** pins Quarkus 3.27.0 + Java 21 + 6 Quarkiverse extensions + Maven plugin versions. **Does NOT pin any Ship.Cars extension** — explains why a service can be on BOM 3.27.1-SNAPSHOT but on `quarkus-pubsub` 3.20.x. Version drift between BOM and extensions is silent.
- **`models-lib` (17 consumers)** is the fleet's shared Java DTO library. 5 modules covering business-domain DTOs, per-consumer REST DTOs, ES-indexable read-models, data→read converters, and the rateengine `ml-dtos` interface. Heaviest readers are the ES-indexing pipeline (`syncer`/`cube`/`saved-search-handler`).

**Java-commons-shared-library group is now closed**: 6 of 6 fleet-cross-cutting Java commons artifacts are at `seed` (`commons`, `quarkus-commons`, `spring-commons`, `shipcars-quarkus-bom`, `models-lib`, plus the 5 Ship.Cars Quarkus extensions seeded in Phases 4.15 + earlier). Together they capture the entire compile-time substrate that every Java service in the fleet recompiles against.

### Added 2026-05-12 (Phase 4.15) from platform-extension depth pass

No new runtime edges in this pass — the four seeds are libraries, not services. The compile-time-edges table above was rewritten with confirmed fanout numbers (9 / 14 / 29 / ~50+ consumers). Key takeaways added:

- **`quarkus-extension-webclient` is the fleet's safe-path Quarkus REST client** with built-in baseline timeouts and retry. Only 9 services use it; the other ~30 Quarkus services use `@RegisterRestClient` (silent-by-default on timeouts). This is the structural reason the rest-client-registry shows 33 of 36 missing timeouts: most services chose the silent-by-default path.
- **`quarkus-extension-persistence` does NOT carry Hikari pool defaults.** This corrects an earlier implicit assumption. The pool-size outliers (`notification-backend` 5, `dataone` 4, `public-tracking-backend` 5, `load-bookmark-backend` 4 prod, `location-history-backend` 4, `location-provider` 4, `autoims-backend` 10, `driveaway-backend` 10) are per-repo `application.properties` choices — no single-line fleet-wide fix exists for them.
- **`quarkus-pubsub`'s retry/DLQ semantics live in GCP**, not in code. A consumer that throws on every message redelivers forever unless the subscription has `Maximum delivery attempts` + a `Dead letter topic`. Verifying every prod subscription has both is a separate audit worth running.
- **`commons:libs` 3.28.0-SNAPSHOT is the framework-neutral nucleus** left after the 2024 Quarkus / Spring split. ~50+ Java services depend on it. Any breaking change to `ErrorCode`, `UserContextDto`, `IDResponseDto`, `PageDto`, or any `SC*Utils` propagates fleet-wide on recompile.

### Communication-domain topology update (post-Phase 4.14)

```
ml-ui-chat (Streamlit /chat/)                    chat-frontend (@shipcars/chat MFE)
  ↓ REST (no timeout)                                ↓ REST (axios, no timeout)
ml-service-chat (FastAPI + GPT-4o)               chat-backend (Spring Boot)
  ↓ JDBC: ml_service_chat                            ↓ REST → notification-backend (silent on error)
  ↓ JDBC (shadow): rateengine.production             ↓ REST → user-backend, media-proxy
  ↓ external: OpenAI                                 ↓ Pub/Sub: UserStateConsumer
  ↑ none                                             ↓ ----
                                                  pusher ─→ ship.cars.notification ─→ socket-server (RS256/Keycloak)
                                                       ─→ (different Redis cluster) ─→ socket-server-old (HS256/legacy)
                                                  socket-server / socket-server-old
                                                       ─→ WebSocket ─→ browser ─→ DOM CustomEvent ─→ chat-frontend.useSocket
```

Two parallel WebSocket gateways on **different Redis clusters** is a meaningful topology fact — `pusher`'s Redis-emitter target determines which gateway sees its broadcasts. Worth a follow-up to confirm whether `pusher` publishes to one or both, and which client populations connect to each.

### New P0 / fleet-significant findings from this pass

- **`socket-server-old`**: JWT signing secret (`SECRET_KEY`) committed to git as a plaintext literal in `index.js` AND identically across all four `helm/.../values-{dev,qa,staging,production}.yaml`. Anyone with read access to the repo can forge a valid HS256 JWT and connect as any user / join any room in any environment. The secret has not been rotated since the 2022-11-29 init commit. **Compensating control**: move to `externalSecrets`+`gcp-secret-manager` (`pusher`'s pattern) and rotate; full retirement requires migrating legacy clients to Keycloak-issued JWTs handled by `socket-server`.
- **`ml-service-chat`**: hardcoded ~70-entry carrier/customer token whitelist in `settings.py` (`CARRIER_TOKENS` / `CUSTOMER_TOKENS`). Adding a caller requires a code change + deploy. Reasonable for pilot stage; problematic if scaled.
- **`ml-service-chat`**: `openai==1.30.1` dep + `openai.ChatCompletion.acreate(...)` call site — incompatible APIs (v0 surface removed in v1). Verify the runtime path is alive before treating it as load-bearing.
- **`ml-ui-chat`**: `requests.post(...)` to `ml-service-chat` with no `timeout=` — a hung backend stalls the UI worker. Same anti-pattern as `lead-parser` / `rateengine` at the Python layer.
- **`chat-frontend`**: `axios.create()` with no default `timeout`. Same fix recipe at the browser layer.

## Compile-time edges (libraries)

These are not runtime calls but are load-bearing for the fleet's behavior. **Fanout numbers are runtime-only — test-only usage is excluded.**

| Consumer count | Library | Why it matters |
|---|---|---|
| ~40+ (all Quarkus services) | `quarkus-commons` (`~/projects/ship-cars-usa/quarkus-commons/`) | OTel/MDC bridge + structured-JSON fix. **Does not** set baseline REST-client timeouts → systemic gap. |
| ~40+ (all Quarkus services) | **`shipcars-quarkus-bom` (`ship.cars.quarkus:shipcars-quarkus-bom` 3.27.1-SNAPSHOT)** | BOM pinning Quarkus platform 3.27.0 + Java 21 + Quarkiverse extensions (`quarkus-logging-json` 3.4.0, `quarkus-logging-manager` 3.4.1, `quarkus-google-cloud-pubsub` 2.18.0, `quarkus-unleash` 1.11.0, `quarkus-tika` 2.2.1, `quarkus-wiremock` 1.5.1) + Maven plugin versions. **Does NOT pin any Ship.Cars extension** — those are pinned independently per consumer. BOM version drift is the source of "outlier" fleet Quarkus versions (`archiver` 2.9.1.Final, `notification-orchestrator` 3.8.3, 3.15.x / 3.20.x services). |
| ~50+ (all Java services, Quarkus + Spring) | **`commons` (`ship.cars.commons:libs` 3.28.0-SNAPSHOT)** | Error codes (`ErrorCode`, `BusinessRuleException`, `ErrorDto`), retry primitives (`RetryConfig`, `RetryUtils`), MDC keys, exception-message extractors, `UserContextDto`, JSON DTOs (`IDResponseDto`, `PageDto`, `OptionalFieldDto`), Datadog wiring, Temporal commons, US-locale helpers, security-adjacent CSV/image/MIME validators. **Public API stability is load-bearing for the entire Java fleet.** |
| **17 services** | **`models-lib` (`ship.cars.models-lib:models-lib` 1.144.0-SNAPSHOT)** | 5-module Java DTO library: `data-models` (~35 entity DTOs — `PostingDto`, `LoadDto`, `CompanyDto`, `VehicleDto`, …), `api-dtos` (REST DTOs scoped per-consumer), `read-models` (ES-document tier, `Indexable` marker), `converters` (data→read), `ml-dtos` (rateengine Java-side contract). Heaviest users are the ES-indexing pipeline (`syncer` + `cube` + `saved-search-handler`). Independently versioned from the Quarkus BOM. Field renames cascade through converters into ES; `ml-dtos` is the contract surface for the ADR-0005 rateengine rewrite. |
| 10+ Spring services | `spring-commons` | Includes `spring-bom`, `WebClientImpl` (with explicit timeout knobs that consumers must set — only `posting-backend` and `autoims-backend` do), `GlobalExceptionHandler`, **`PubSubConsumer`** (canonical good template), Keycloak resource-server wiring. |
| **40+ Quarkus services** | `quarkus-notification-client` | The notification fan-out edge from many services routes through this library. **Highest-coupled binary-compat dependency in the fleet.** Synchronous `future.get()` propagates Pub/Sub latency into every caller. |
| **29 Quarkus services** | **`quarkus-pubsub` (`ship.cars.quarkus.extensions.pubsub` 3.27.1-SNAPSHOT)** | The fleet's GCP Pub/Sub publish-and-subscribe substrate. Typed `PubSubConsumerBlocking<T>` + `PubSubAckReplyConsumerBlocking<T>` interfaces; `PubSubPublisher` (async) / `PubSubPublisherSync` (blocking via `future.get()`). Retry/DLQ is GCP-side (configured in the subscription, not in code). `quarkus-notification-client` and `quarkus-user-syncer` both depend on it, so the transitive consumer count is even higher. |
| **14 Quarkus services** | **`quarkus-extension-persistence` (`ship.cars.quarkus.extensions.persistence` 3.27.1-SNAPSHOT)** | Provides `TransactionalExecution` + `TransactionalBatchesExecution` programmatic JTA helpers (`executeInTransaction`, `executeInNewTransaction`, batched-commit). **Does NOT** carry Hikari/JDBC defaults — pool-size outliers in `data-stores.md` are per-service `application.properties`, not inherited from this extension. Pulled in by both `quarkus-imperative-boilerplate` and `quarkus-k8s-boilerplate` templates, so new services inherit it by default. |
| **9 Quarkus services** | **`quarkus-extension-webclient` (`ship.cars.quarkus.extensions.webclient` 3.27.1-SNAPSHOT)** | The fleet's **safe-path Quarkus REST client**: `WebClientImpl.DEFAULT_CONFIG` provides baseline timeouts (connect 60 s / read 30 s / write 30 s) + retry (7 attempts, 5–30 s backoff, jitter 0.75) + business-rule-exception translation. **Alternative to MicroProfile's `@RegisterRestClient`** which is silent-by-default (33 of 36 fleet declarations missing timeouts per `rest-client-registry.md`). Worst-case call budget: ~5 min if retry exhausts at max backoff. Used by: `cube`, `integrations-backend`, `load-bookmark-backend`, `load-recommender`, `loadboard-backend`, `location-provider`, `saved-search-handler`, `trip-planner`, `command-executor`. |
| Quarkus services with location lookups | `quarkus-locationprovider-client` | Wraps the `location-provider` REST client; bundle of typed DTOs + retry helpers. Used by `trip-planner`, `uship-quotes`. |
| **13 services (Quarkus + Spring)** | **`quarkus-extension-media-proxy` (`ship.cars.quarkus.extensions.mediaproxy:quarkus-mediaproxy-client` 3.27.0.2-SNAPSHOT)** | Companion to the Go `media-proxy` service. Multi-module: Quarkus runtime + **Spring client** + shared `api-dtos`/`api-enums`/`commons` — one of the few cross-stack libraries. Consumers: chat-backend, cube, driveaway-backend, integration-executor, integrations-backend, inventory-backend, invoices, loadboard-backend, loadbuilder-backend, posting-backend, public-tracking-backend, pusher, user-backend. README documents `connect-timeout=5000` / `read-timeout=10000` knobs (rare in the fleet). |
| **33 Quarkus services** (essentially every active one) | **`quarkus-request-filter` (`ship.cars.quarkus.extensions.request-filter` 3.27.5-SNAPSHOT)** | Per-request **context-company / context-user extraction** from API-Gateway header or path params → SLF4J MDC + `ContainerRequestContext`. **The fleet's load-bearing logging-context layer.** Also bundles `ConstraintViolationExceptionMapper` (+Reactive variant), generic `ExceptionMapper`, and `ClientResponseExceptionMapper` that translate exceptions to fleet `ErrorDto` responses. `MdcPopulator` SPI lets services add custom MDC fields. One knob: `ship.cars.request.filter.log-headers` (default true). |
| **10+ Quarkus services with native-image builds** | **`quarkus-auto-reflection` (`ship.cars.quarkus.extensions.reflection` 3.27.1-SNAPSHOT)** | Provides `ship.cars.reflection.{class-name,package-name}[*]` properties for registering classes/packages for native-image reflection. Build-time-fixed phase. `command-executor` is the canonical example with 26 `package-name[*]` entries. Consumers: aaag-integration, axe-call-integration, bi-databricks-backend, command-executor, dataone, fraud-detector, integration-executor, integrations-backend, invoices, metadata, etc. |
| Influence-only template | **`quarkus-imperative-boilerplate` (`ship.cars.quarkus.boilerplate:boilerplate` 0.1.0-SNAPSHOT)** | Canonical 9-module Quarkus imperative-service template (api-dtos / application / commons / configuration / db-entities / db-migration / repositories / resources / services / utils). **Not imported as a dependency** — services clone-and-rename from this. `command-executor`, `axe-call-integration`, `integration-executor`, similar imperative Quarkus services share the identical layout + start-script set. Updates here don't auto-propagate; teams hand-merge. |
| Influence-only template | **`quarkus-k8s-boilerplate` (`ship.cars.quarkus.boilerplate:boilerplate` 0.1.0-SNAPSHOT)** | **Lightweight single-module** Quarkus microservice template (counterpart to `quarkus-imperative-boilerplate`'s 9-module shape). Optimized for 5-20-endpoint services, native-image, serverless deploys. Ships standard fleet wiring: `ActorContext` for Envers audit, Pub/Sub config, `ObjectSerializerConfig`. Sample `City`/`State` domain illustrates the "Page" + "Rev" (Envers revision) pattern. Same clone-and-rename + hand-merge convention. |
| Influence-only template | **`quarkus-extension-bootstrap` (`ship.cars.quarkus.extensions.bootstrap` 1.0.0-SNAPSHOT)** | Template **for new Ship.Cars Quarkus extensions** (not services). All Ship.Cars extensions visible in this table (webclient / pubsub / persistence / mediaproxy / locationprovider-client / auto-reflection / request-filter / data-migration / firestore-storage) share the same "multi-module: runtime + deployment + coverage-report" layout — they were likely all scaffolded from this template. Don't import at runtime. |
| 1 confirmed (`command-executor`) | **`quarkus-extension-firestore-storage` (`ship.cars.quarkus.extensions.firestore.storage` 3.20.2.3-SNAPSHOT)** | Typed `StorageClient` over Google Cloud Firestore. Versioned CRUD + optimistic concurrency (`StorageConcurrentModificationDetectedException`) + TTL auto-deletion. Slightly behind fleet HEAD; only `command-executor` consumes it today. |
| 0 detected | **`quarkus-data-migration` (`ship.cars.quarkus.extensions.data-migration` 3.27.1-SNAPSHOT)** | Java-typed data-migration framework complementing Flyway. Auto-runs `DataMigration` beans at startup; tracks versions via `DataMigrationVersionEntity`. **No active fleet consumers detected** — extension is published and versioned but apparently unused, or imported transitively via the boilerplates without showing in direct grep. |

## Notable observations from the 78-seed graph

- **`user-backend` is the highest-blast-radius callee** with **10 inbound REST edges** now confirmed: `chat-backend`, `contract-pricing-backend`, `notification-backend`, `impersonator` (×2: `company-owner-api` and `user-api` — both resolve to `user-backend`), `payment-backend`, `quote-manager-backend`, `invoices`, `trip-planner`, `inventory-backend`. A `user-backend` outage takes down most of the fleet's request path.
- **`attachment-backend` and `metadata` are the two highest-fanout *platform* callees**, with 6 and 8 confirmed inbound REST edges respectively. Both have pool-size and outbox gaps worth flagging in their shadows; see `data-stores.md` for the pool-size outliers table.
- **`location-provider` is the highest-fanout *operations* callee** with 9 confirmed inbound REST edges across pricing, listings, and operations domains — and a HikariCP pool of 4 (`route_distance` PG). Cache miss + slow Maps = pool exhaustion fast.
- **`quarkus-notification-client` is the single highest-coupled binary-compat dependency in the fleet** with **40+ compile-time consumers**. A breaking change here means a fleet-wide redeploy. Treat as the most stable public Java contract in the codebase.
- **Two new "shadow caller" patterns confirmed** beside the original `integrators-data-bridge`:
  - **`syncer`** is the second-largest direct-PG reader — it reads from **6 other services' PostgreSQL databases** (lm-posting, saved-search, platform/lbv3, location-history, metadata, trip-planner) via reactive datasources. Same risk pattern: a schema migration upstream silently breaks ES indexing.
  - **`pusher`** holds read-only connections to `ctms-db` and `usermanagement-db` for routing-decision lookups. Smaller blast-radius than `syncer`, but the pattern adds up.
  - Net: **at least 11 cross-service direct-DB-read edges** now in the graph (`integrators-data-bridge` 4 + `syncer` 6 + `pusher` 2 — minus overlap on `metadata`/etc.). Worth a fleet-wide decision: ratify with API contracts, or migrate to Pub/Sub replication.
- **Communication-domain topology is now clear**: `pusher` (router) → `quarkus-notification-client` → `ship.cars.notification.topic` → `notification-backend` + `notification-orchestrator` (per-channel senders) and Redis emitter → `socket-server` (WebSocket). The still-open question is whether `notification-backend` and `notification-orchestrator` should subscribe to **the same** topic — currently both can, by config.
- **`posting-backend` is the central listings-trade hub**: 12+ outbound REST edges plus 7 Pub/Sub subscriptions plus 4 outbox-published topics. Its inbound REST edges now include `inventory-backend`, `load-recommender`, `load-bookmark-backend`, `saved-search-handler`'s sibling (`loadboard-backend`), `invoices` — making it the densest *both-directions* node and the single biggest blast-radius callee inside the listings-trade domain.
- **`posting-backend.ShipcarsLoadBoardClientImpl` is the only Spring-side REST client with explicit timeouts** (`read=PT150S`, `connect=PT60S`, `application.properties:216-222`). Every other Spring fleet client falls back to whatever `spring-commons.WebClientImpl` defaults to (most likely infinite). If a single-service fix were prioritized, it would be making this the rule rather than the exception.
- **`user-backend` ↔ `notification-backend` cycle** still holds: `notification-backend` REST-calls `user-backend`; `user-backend` publishes to `notification` topic that `notification-backend` consumes. A `user-backend` outage degrades `notification-backend`'s consume path with no obvious call-site log.
- **`integrators-data-bridge` reads `posting-backend` and `inventory-backend` Postgres directly** — confirmed in both seeds. Schema changes in either repo can silently break the bridge; no API contract enforces compatibility.
- **`notification-backend` and `notification-orchestrator` are parallels, not a stack.** `notification-orchestrator` does **not** call `notification-backend` (zero `@RegisterRestClient`). They both consume Pub/Sub and both reach SendGrid. This is the answer to a long-standing fleet question — and it raises the next one: who decides which subscription belongs to which service?
- **Outbox pattern is uneven across the Spring fleet:** `user-backend` and `posting-backend` use ShedLock-based outbox; `quote-manager-backend`, `notification-backend`, `notification-orchestrator`, `invoices`, `fraud-detector` are fire-and-forget. The two outbox-using services are the most data-critical writers — possibly intentional, possibly accidental.
- **No Kafka edges** in the 28-seed sample. Pub/Sub remains the only async pattern observed.
- **Fleet-wide REST-client timeout audit:** see `rest-client-registry.md` — **33 of 36 Quarkus REST clients** have neither `connect-timeout` nor `read-timeout` configured (92% exposure). Spring services use `WebClientImpl` and require programmatic timeouts that nobody except `posting-backend.ShipcarsLoadBoardClientImpl` and `autoims-backend.AutoImsWebClientFactory` actually sets.
- **`lead-parser` is the single biggest lifecycle/security flag in the fleet**: Spring Boot 2.1.4 + Java 8 + raw `new RestTemplate()` + silent 200-OK on downstream failure. Replace-not-patch.
- **`load-bookmark-service` is the single biggest correctness flag in the fleet**: `eval()` on etcd values and always-ACK on Pub/Sub. Two-line code change for the first; rework needed for the second.
- **Two unresolved sibling-service boundaries**: `notification-backend` ↔ `notification-orchestrator` (parallel email paths) and `load-bookmark-backend` ↔ `load-bookmark-service` (JVM bookmark API vs. Python etcd sidecar). Both need an explicit owner decision rather than continued accretion.

### Added 2026-05-12 — MFE → backend edges (carrier-persona surface)

Sourced by grepping every `/api/...` literal inside the 4 carrier-facing MFE repos AND the 4 shared FE packages they import. Classified by URL convention: unversioned `/api/<noun>/` (trailing slash) = Django REST framework, routes to `platform-backend`; versioned `/api/<svc>/v<N>/...` = Java/Quarkus or Python/FastAPI target. The fleet `api-gateway` (Go/Fiber) enforces the routing.

| Caller | Callee | Protocol | Evidence | Last confirmed |
|---|---|---|---|---|
| `ctms-frontend` | `platform-backend` (Django) | REST | in-repo `/api/users/me/`; transitive via `entities-frontend-package` `/api/loads/`, `/api/orders/`, `/api/negotiations/`, `/api/offers/`, `/api/postings/` (unversioned), `/api/contacts/`, `/api/carrier_companies/`, `/api/network_companies/`, `/api/companies/`, `/api/carriers/`, `/api/vehicles/` | 2026-05-12 |
| `ctms-frontend` | `cube` (Quarkus) | REST | via `entities-frontend-package` `/api/cube/ctms/v1/...`, `/api/cube/loadboard/v3,v4/...` | 2026-05-12 |
| `ctms-frontend` | `trip-planner` (Quarkus) | REST | in-repo `/api/tripplanner/v1/trips/...` | 2026-05-12 |
| `ctms-frontend` | `location-provider`, `negotiations-router`, `user-backend`, `attachment-backend`, `metadata`, `load-bookmark-backend`, `saved-search-handler`, `load-recommender`, `invoices`, `payment-backend`, `location-history-backend`, `crm-workflows`, `user-activity-tracker`, `axe-call-integration` | REST | via `entities-frontend-package` (`/api/<svc>/v<N>/...` paths) | 2026-05-12 |
| `loadboard-frontend` | `platform-backend` (Django) | REST | in-repo `/api/postings/`, `/api/network_companies/`, `/api/network_companies/${id}/safer_watch/`, `/api/carrier_companies/`, `/api/shipper_companies/`, `/api/generic_change_log/` | 2026-05-12 |
| `loadboard-frontend` | `company-documents` (Python / FastAPI) | REST | in-repo `/api/company-documents/carrier/${id}/documents/`, `/request/`, `/api/company-documents/documents/${id}/wrapper/`, `/share/` — **only carrier MFE that hits this FastAPI service directly** | 2026-05-12 |
| `loadboard-frontend` | `loadboard-backend` (Quarkus) | REST | in-repo `/api/loadboard/v3/companies/carriers`, `/api/loadboard/v3/companies/shippers` (legacy v3; cube absorbs v4) | 2026-05-12 |
| `loadboard-frontend` | `cube` (Quarkus) | REST | via `entities-frontend-package` `/api/cube/loadboard/v3,v4/platform-web/postings/...` | 2026-05-12 |
| `loadboard-frontend` | `trip-planner` (Quarkus) | REST | in-repo `/api/tripplanner/v1/trips/...` (load→trip transfer, posting attach/detach) | 2026-05-12 |
| `loadboard-frontend` | `location-provider`, `user-activity-tracker`, + the broad shared set | REST | in-repo + shared package | 2026-05-12 |
| `trip-planner-frontend` | `platform-backend` (Django) | REST | in-repo `/api/loads/`, `/api/trips/${id}`, `/api/trips/${id}/assign/`, `/api/trips/${id}/reassign/`, `/api/users/`, `/api/extra/loads/next_shipper_id/` — **dual-surface with `trip-planner`** (Django + Quarkus coexist) | 2026-05-12 |
| `trip-planner-frontend` | `trip-planner` (Quarkus) | REST | in-repo `/api/tripplanner/v1/trips/...`, `/optimize-route`, `/transfer` | 2026-05-12 |
| `carrier-order-importer-frontend` | `platform-backend` (Django) | REST | in-repo `/api/contacts/`, `/api/contacts/${id}/`, `/api/extra/loads/next_shipper_id/`, `/api/vehicles/${id}/`, `/api/vehicles/${vin}/vin/` — **the MFE's entire direct API surface is on Django** | 2026-05-12 |
| `entities-frontend-package` *(shared FE library; transitive)* | `platform-backend` (Django) + ~14 Quarkus / Spring services + `payment-backend` + `location-provider` | REST | ~100 endpoint paths declared in the package; every MFE that imports `actions/*` or `models/*` makes these calls transitively | 2026-05-12 |

### Inbound edges confirmed in this pass

| Callee | Confirmed inbound from |
|---|---|
| `platform-backend` (Django monolith) | **all 4 carrier-persona MFEs** (`ctms-frontend`, `loadboard-frontend`, `trip-planner-frontend`, `carrier-order-importer-frontend`) — not peripheral; owns the operational core (loads / orders / negotiations / companies / carriers / contacts / postings / users / vehicles) for the carrier flow |
| `company-documents` (FastAPI) | `loadboard-frontend` (only) — carrier-document compliance flow |
| `cube` (Quarkus) | `ctms-frontend` (heavy — primary CTMS read API), `loadboard-frontend` (v4 postings read), transitively all MFEs via `entities-frontend-package` |
| `negotiations-router`, `load-bookmark-backend`, `saved-search-handler`, `load-recommender`, `invoices`, `location-history-backend`, `crm-workflows`, `user-activity-tracker`, `axe-call-integration` | all 4 carrier MFEs (transitive, via `entities-frontend-package`) |

### Carrier-MFE Django/Java URL convention (load-bearing fact for fleet routing)

```
/api/<noun>/         (trailing slash)  → platform-backend (Django REST framework)
/api/<service>/v<N>/                   → Java / Quarkus or Spring service
/api/<service>/...                     → Python / FastAPI (company-documents)
```

Enforced by `api-gateway` (Go/Fiber) — JWT verification + sliding-window rate limit + template-expanded routing per `config/` entry.

**Dual-surface nouns** (same resource served by both Django and an extracted service — MFEs hit both):

| Noun | Django path (`platform-backend`) | Extracted path |
|---|---|---|
| trips | `/api/trips/` | `/api/tripplanner/v1/trips/` (`trip-planner`) |
| users | `/api/users/` | `/api/usermanagement/v2,v3/` (`user-backend`) |
| postings | `/api/postings/` (unversioned) | `/api/loadboard/v3/postings/`, `/api/cube/loadboard/v4/postings/` |
| invoices | `/api/invoices/`, `/api/revised_invoices/` | `/api/loadmate/invoices/v1/` (`invoices`) |
| negotiations | `/api/negotiations/` | `/api/negotiations-router/v1/` |
| reports / metadata / etc. | `/api/reports/templates/` | `/api/metadata/v1/` (`metadata`) |

Extraction is **incomplete**; production traffic still routes to both surfaces. Schema changes that touch a dual-served noun require coordinating both backends + the shared `entities-frontend-package` typed models.

### Smoking gun for ongoing Django consumption

`globals-frontend-package/src/utils/errors.ts` exports **both** `parseDjangoErrorMessage` and `parseJavaErrorMessage` (lines 6, 14, 32, 44, 75). The shared FE library has dedicated error parsers for both backend ecosystems because every Loadmate request path needs to handle either shape. If Django consumption were a tail / legacy concern, this helper would not exist — its presence confirms the dual-backend pattern is a routine, supported request shape.

## Open questions

- The boundary between `notification-backend` and `notification-orchestrator` needs an explicit owner decision — which service handles which channels and which Pub/Sub subscriptions? Right now this is an empirical observation, not a design.
- The boundary between `load-bookmark-backend` (JVM, PG, REST API + Pub/Sub) and `load-bookmark-service` (Python, etcd, Pub/Sub) is undocumented. Which is the source of truth? If both, what's the contract?
- `integrators-data-bridge`'s direct Postgres reads against `posting-backend`, `inventory-backend`, `autoims-backend`, and `contract-pricing-backend` bypass service ownership — confirm whether the source services consider this an acceptable contract or shadow IT.
- `relations/rest-client-registry.md` resolves env-templated URLs to friendly configKeys but does NOT resolve those keys to concrete callee repos. Adding a `configKey → callee-repo` lookup is a follow-up. The Spring side (WebClient) is not covered at all — would need a separate Spring-aware scanner.

## Related

- `data-stores.md` — service → data store edges (different graph; will be deepened with the new seeds in a follow-up pass).
- `ownership.md` — team → service edges (still placeholder; needs a SoT decision).
- `infrastructure-triage.md` — one-shot triage of the 68 `infrastructure` shadows into active / archive-candidate / unsure.
- `rest-client-registry.md` — Quarkus `@RegisterRestClient` audit (33 of 36 missing timeouts).
- `quarkus-version-matrix.md` — per-service BOM + Ship.Cars-extension version pins, surfaces silent drift.
- `db-contracts/` — ADR-0003 contract drafts for the 14 sanctioned cross-service direct-DB-read edges.
- `../domains/<domain>.md` — per-domain subgraphs, populated for all 9 domains.
