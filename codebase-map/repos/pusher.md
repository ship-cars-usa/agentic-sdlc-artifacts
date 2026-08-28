---
repo: pusher
path: ~/projects/ship-cars-usa/pusher
stack: Java 21 / Quarkus 3.27.5
domain: communication
shape: multi-module (13 poms)
last-synced-commit: f6a173626aaf297623d91ce1d508b6697e02f3dc
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# pusher

## What it is
Quarkus 3.27.5 / Java 21 service — the **central event-driven notification hub / routing brain** for the fleet. Consumes ~9 Pub/Sub subscriptions (CTMS, LoadMate posting/quote-manager, LoadBoard, Metadata, UserManagement user/company, integrations), maintains a local PG cache of user/company/event-subscription state for routing, and fans each domain event out across channel processors: **socket** (WebSocket, via socket-server), **push** (FCM/APNS), **email**, **pub/sub** (integration/executor topics), and **integration** webhooks. Together with `notification-backend`, `notification-orchestrator`, `socket-server`, and `quarkus-notification-client` this is the communication domain; the boundary among them is implicit — pusher decides *which channels fire*; the others are channel-specific senders/relays. A small `db-syncer` module also exposes admin/dashboard REST for event subscriptions.

## How it fits
- Consumes API of: outbound HTTP via Vert.x `WebClient.create(vertx)` (**not `@RegisterRestClient`**) and a `media-proxy` MicroProfile REST client (`quarkus.rest-client.media-proxy.url`). **No connect/read timeouts** are set on either (bare `WebClient`, no `mp-rest` timeouts).
- Publishes events to: the notification topic (`ship.cars.notification.topic`) via `NotificationClient` and an integration/`executor-topic` via `PubSubPublisher` (`SenderImpl`). Socket messages are emitted for socket-server to relay.
- Subscribes to: **9 Pub/Sub subscriptions** — `ctms-subscription`, `integration-subscription`, `loadboard-backend`/`loadboard-v3-subscription`, `loadmate-posting-subscription`, `loadmate-posting-v2-subscription`, `loadmate-quote-manager-subscription`, `user-subscription-v2`, `company-subscription-v2`, `metadata-subscription` — all via `PubSubConsumerBlocking` listeners in `event-listener/infra`.
- Owns data store: primary PostgreSQL (JDBC, `max-size=10`) with tables for `company`, `user`, `event_subscription`, `event_subscription_source`. Also two **reactive** read datasources — `ctms-db` and `usermanagement-db` (`reactive.max-size=10`, `health-exclude=true`) — for recipient lookups.

## Build / test / run
```
./build-dev.sh                              # or ./mvnw -s .mvn/settings.xml clean install
utils/docker-compose/docker-compose.sh up -d # local Postgres + Pub/Sub emulator
./build-native.sh                           # -Pnative
# 13 modules: application, domain, db-entities, db-migration, db-syncer,
#             event-listener, notification-sender, commons, configuration,
#             api-dtos, integration-test, coverage-report, (root)
```

## Key abstractions
- Per-source Pub/Sub listeners — `event-listener/.../listener/infra/{Ctms,LoadMatePosting,LoadMatePostingV2,LoadMateQuoteManager,Loadboard,Metadata,UserManagementUser,UserManagementCompany}*Listener.java` — each a `PubSubConsumerBlocking`; convert the raw DTO into a `*ProcessEventCommand`.
- Per-source `*EventProcessorService` + `*NotificationModelFactory` — `event-listener/.../listener/services/impl/…` — turn a domain event into a `NotificationsDto` (list of `BaseDomainCommand`s: `SendSocket`, `SendPushNotification`, `SendEmail`, `SendPubSubNotification`, `SendIntegrationNotification`).
- `NotificationCommandProcessor` — `notification-sender/.../sender/services/impl/NotificationCommandProcessor.java` — switches each command to its channel processor, gated by Unleash feature toggles (`FeatureToggleOperations`).
- Channel processors — `notification-sender/.../services/processors/impl/…` — `SocketEventProcessorImpl`, `PushEventProcessorImpl`, `EmailEventProcessorImpl`, `PubSubEventProcessorImpl`, `IntegrationEventProcessorImpl`.
- `SenderImpl` — `notification-sender/.../services/impl/SenderImpl.java` — the outbound seam; wraps `NotificationClient` + `PubSubPublisher`, builds `PubsubMessage` with `orderingKey`.
- `MediaUrlProxyTransformer` — `notification-sender/.../services/impl/MediaUrlProxyTransformer.java` — rewrites attachment/media URLs through media-proxy before sending.
- `db-syncer` — `db-syncer/.../rest/{EventSubscriptionsController,DashboardController}.java` — admin REST + syncing of the local company/user/subscription cache.

## Don't-do-here / gotchas
- **No outbound REST/WebClient timeouts** — `WebClientConfig` returns a plain `WebClient.create(vertx)` with no `WebClientOptions`, and the media-proxy REST client sets no `connect-timeout`/`read-timeout`. Classic fleet retry-without-timeout exposure. Set explicit timeouts.
- **`future.get()` blocking on Pub/Sub publish ACK** inside `SenderImpl.sendIntegrationEvent()` — surfaces publish errors on the event-listener thread and blocks it until the ACK returns. Under Pub/Sub slowness, listener threads pile up. Prefer async callback + bounded executor.
- **Hardcoded WebSocket room prefixes** (`user_<id>`, `company_<id>`) — coordinated with socket-server's middleware; renaming requires a synchronized deploy across both.
- **Datasource pools** — primary JDBC `max-size=10` plus two reactive datasources at `reactive.max-size=10` each; tight under burst, and the reactive vs. JDBC split is easy to misconfigure.
- **Ordering-key dependency** — routing/replay relies on upstream sources setting `orderingKey`; if a source drops it, semantics break silently. Consider a startup assertion.
- **Communication-domain boundary is implicit** — pusher, `notification-backend`, and `notification-orchestrator` subscribe to overlapping topics; the same event can be handled by more than one service. Needs an explicit owner decision.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/notification-backend.md` — fellow communication-domain service.
- `~/projects/codebase-map/repos/notification-orchestrator.md` — fellow communication-domain service.
- `~/projects/codebase-map/repos/socket-server.md` — downstream WebSocket relay.
- `~/projects/codebase-map/repos/quarkus-notification-client.md` — used to publish.
- `~/projects/codebase-map/domains/communication.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `CompanyEntity` | jpa | `db-entities` | [Company](../domains/entities/Company.md) |
| `EventSubscriptionEntity` | jpa | `db-entities` | EventSubscription |
| `EventSubscriptionSourceEntity` | jpa | `db-entities` | EventSubscriptionSource |
| `UserEntity` | jpa | `db-entities` | [User](../domains/entities/User.md) |
| `Actions` | dto | `domain` | Actions |
| `ActivityLogDto` | dto | `event-listener` | [ActivityLog](../domains/entities/ActivityLog.md) |
| `ActivityLogModelDataVo` | dto | `domain` | ActivityLogModelDataVo |
| `AttachmentDto` | dto | `event-listener` | [Attachment](../domains/entities/Attachment.md) |
| `AttachmentModelDataVo` | dto | `domain` | AttachmentModelDataVo |
| `ChangeDto` | dto | `event-listener` | Change |
| `ChangeModelDataVo` | dto | `domain` | ChangeModelDataVo |
| `ChangeObjectDto` | dto | `event-listener` | ChangeObject |
| `ChangeObjectVo` | dto | `domain` | ChangeObjectVo |
| `Company` | dto | `commons` | [Company](../domains/entities/Company.md) |
| `CompanyIntegrationSubscription` | dto | `db-syncer` | CompanyIntegrationSubscription |
| `CompanyPubSubNotificationVo` | dto | `domain` | CompanyPubSubNotificationVo |
| `CompanyVo` | dto | `domain` | CompanyVo |
| `CtmsProcessEventCommand` | dto | `event-listener` | CtmsProcessEventCommand |
| `CtmsUserDto` | dto | `event-listener` | CtmsUser |
| `CtmsUserVo` | dto | `domain` | CtmsUserVo |
| `DashboardController` | dto | `db-syncer` | DashboardController |
| `DbCompanyDto` | dto | `db-syncer` | [Company](../domains/entities/Company.md) |
| `DbEventSubscriptionDto` | dto | `db-syncer` | DbEventSubscription |
| `DbUserDto` | dto | `db-syncer` | [User](../domains/entities/User.md) |
| `EventSubscription` | dto | `commons` | EventSubscription |
| `EventSubscriptionSource` | dto | `commons` | EventSubscriptionSource |
| `EventSubscriptionsController` | dto | `db-syncer` | EventSubscriptionsController |
| `EventSubscriptionsListDto` | dto | `commons` | EventSubscriptionsList |
| `EventSubscriptionsServiceImpl` | dto | `db-syncer` | EventSubscriptionsServiceImpl |
| `EventType` | dto | `domain` | EventType |
| `EventVo` | dto | `domain` | EventVo |
| `IntegrationMessageVo` | dto | `domain` | IntegrationMessageVo |
| `LoadDto` | dto | `event-listener` | [Load](../domains/entities/Load.md) |
| `LoadMateMessageVo` | dto | `domain` | LoadMateMessageVo |
| `LoadMatePostingEventObjectDto` | dto | `api-dtos` | LoadMatePostingEventObject |
| `LoadMatePostingMessageDto` | dto | `api-dtos` | LoadMatePostingMessage |
| `LoadMatePostingProcessEventCommand` | dto | `event-listener` | LoadMatePostingProcessEventCommand |
| `LoadMatePostingV2MessageDto` | dto | `api-dtos` | LoadMatePostingV2Message |
| `LoadMatePostingV2MessageVo` | dto | `domain` | LoadMatePostingV2MessageVo |
| `LoadMatePostingV2ProcessEventCommand` | dto | `event-listener` | LoadMatePostingV2ProcessEventCommand |
| `LoadMateQuoteManagerMessageDto` | dto | `api-dtos` | LoadMateQuoteManagerMessage |
| `LoadMateQuoteManagerMessageVo` | dto | `domain` | LoadMateQuoteManagerMessageVo |
| `LoadMateQuoteManagerProcessEventCommand` | dto | `event-listener` | LoadMateQuoteManagerProcessEventCommand |
| `LoadMateQuoteManagerQuoteDto` | dto | `api-dtos` | LoadMateQuoteManagerQuote |
| `LoadModelDataVo` | dto | `domain` | LoadModelDataVo |
| `LoadboardNegotiationVo` | dto | `domain` | LoadboardNegotiationVo |
| `LoadboardPostingVo` | dto | `domain` | LoadboardPostingVo |
| `LoadboardProcessEventCommand` | dto | `event-listener` | LoadboardProcessEventCommand |
| `LoadboardPubSubMessageDto` | dto | `event-listener` | LoadboardPubSubMessage |
| `LocationRequestDto` | dto | `event-listener` | [Location](../domains/entities/Location.md) |
| `LocationRequestModelDataVo` | dto | `domain` | LocationRequestModelDataVo |
| `MessageVo` | dto | `domain` | MessageVo |
| `MetadataMessageObjectDto` | dto | `api-dtos` | MetadataMessageObject |
| `MetadataProcessEventCommand` | dto | `event-listener` | MetadataProcessEventCommand |
| `NegotiationModelDataVo` | dto | `domain` | NegotiationModelDataVo |
| `NegotiationNotification` | dto | `domain` | NegotiationNotification |
| `NotificationRecipient` | dto | `commons` | NotificationRecipient |
| `NotificationsDto` | dto | `api-dtos` | Notifications |
| `PostingVo` | dto | `domain` | PostingVo |
| `PubSubEventSubscriptionDto` | dto | `api-dtos` | PubSubEventSubscription |
| `PubSubIntegrationMessageDto` | dto | `api-dtos` | PubSubIntegrationMessage |
| `PubSubMessageDto` | dto | `api-dtos` | PubSubMessage |
| `PushMessageDto` | dto | `api-dtos` | PushMessage |
| `PushMessageVo` | dto | `domain` | PushMessageVo |
| `PushNotificationConverter` | dto | `notification-sender` | PushNotificationConverter |
| `RecipientFilter` | dto | `commons` | RecipientFilter |
| `SendEmail` | dto | `domain` | SendEmail |
| `SendIntegrationNotification` | dto | `domain` | SendIntegrationNotification |
| `SendPubSubNotification` | dto | `domain` | SendPubSubNotification |
| `SendPushNotification` | dto | `domain` | SendPushNotification |
| `SendSocket` | dto | `domain` | SendSocket |
| `SocketDto` | dto | `api-dtos` | Socket |
| `SocketEventMessageDto` | dto | `api-dtos` | SocketEventMessage |
| `SocketEventMessageVo` | dto | `domain` | SocketEventMessageVo |
| `SocketMetadataRestrictionMessageDto` | dto | `api-dtos` | SocketMetadataRestrictionMessage |
| `SocketMetadataRestrictionMessageVo` | dto | `domain` | SocketMetadataRestrictionMessageVo |
| `SocketNotificationCreatedMessageDto` | dto | `api-dtos` | SocketNotificationCreatedMessage |
| `SocketNotificationCreatedMessageVo` | dto | `domain` | SocketNotificationCreatedMessageVo |
| `SocketNotificationUpdatedMessageDto` | dto | `api-dtos` | SocketNotificationUpdatedMessage |
| `SocketNotificationUpdatedMessageVo` | dto | `domain` | SocketNotificationUpdatedMessageVo |
| `User` | dto | `commons` | [User](../domains/entities/User.md) |
| `UserManagementCompanyProcessEventCommand` | dto | `event-listener` | UserManagementCompanyProcessEventCommand |
| `UserManagementMessageVo` | dto | `domain` | UserManagementMessageVo |
| `UserManagementUserProcessEventCommand` | dto | `event-listener` | UserManagementUserProcessEventCommand |
| `VehicleDto` | dto | `event-listener` | [Vehicle](../domains/entities/Vehicle.md) |
| `VehicleModelDataVo` | dto | `domain` | VehicleModelDataVo |
<!-- entities-end -->
