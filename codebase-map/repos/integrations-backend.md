---
repo: integrations-backend
path: ~/projects/ship-cars-usa/integrations-backend
stack: Java 21 / Quarkus 3.27.5
domain: integrations
shape: multi-module (28 poms)
last-synced-commit: ffc9bc6adb9ff11c3f8c30a83b28424097d757a5
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# integrations-backend

## What it is
Quarkus 3.27.5 / Java 21 multi-tenant integration gateway — separate top-level modules for **Logytext, QuickBooks, Axe, Twilio** (plus shared `attachment`, `db-entities`, `services`, `resources`, `integrations-backend-dtos`/`-enums`, `commons`, `utils`). Each SaaS module brokers between Ship.Cars and one external provider. Inbound paths include Pub/Sub-routed webhooks (Logytext, Axe). 28 poms total (per-module `db-entities`/`services`/`resources` sub-poms inflate the count above the ~4 logical integrations).

## How it fits
- Consumes API of: Logytext, QuickBooks (Intuit OAuth SDK), Axe (assistants/calls), Twilio — all external SaaS; plus internal `attachment-backend` (`AttachmentClient`), CTMS/orders (`CtmsClient`, `OrdersClient` in quickbooks), and `cube` (`CubeClient` in axe). All HTTP goes through the in-house `WebClientImpl` / `WebClientCallConfig` extension, **not** MicroProfile `@RegisterRestClient`.
- Publishes events to: internal eventbus + Pub/Sub for downstream consumers.
- Subscribes to: `integrations-backend.pubsub.logytext-hooks-subscription` (`LogytextPubSubConsumer`), `integrations-backend.pubsub.axe-webhook-subscription` (`AxeWebhookPubSubConsumer`).
- Owns data store: PostgreSQL — `IntegrationEntity`, `IntegrationErrorEntity` (shared `db-entities`); `QuickbooksConfigEntity`, `QuickbooksCredentialsEntity`, `QuickbooksOauthCsrf` (quickbooks); `AssistantCallRecordEntity` (unique `call_id`), `AssistantAudioSyncEntity` (axe). Flyway migrations.

## Build / test / run
```
source ./start-quarkus-env.sh   # sets required env vars
mvn clean install
mvn quarkus:dev                 # needs local PostgreSQL + flyway migration
```

## Key abstractions
- `LogytextPubSubConsumer` — `logytext/services/.../pubsub/consumers/LogytextPubSubConsumer.java:28` — implements `PubSubConsumerBlocking<LogytextPubSubMessageDto>`; `consume` → `processMessage` routes by `objectType` (see gotchas).
- `AxeWebhookPubSubConsumer` — `axe/services/.../pubsub/consumers/AxeWebhookPubSubConsumer.java:21` — implements `PubSubAckReplyConsumerBlocking<AxeWebhookRequestDto>`; uses `safeAckMessage` / `safeNackMessage` (`:61,:75,:85`) — the good template.
- `QuickbooksFacade` — `quickbooks/services/.../services/QuickbooksFacade.java` — token refresh + downstream op; now injects `TransactionalExecution` (`:31`) and `refreshTokenAndUpdate` (`:93`).
- `OAuth2ClientFactory` — `quickbooks/services/.../services/OAuth2ClientFactory.java:18-19` — `clientSecret` via `@ConfigProperty("integrations-backend.quickbooks.client-secret")`.
- `AxeClient` — `axe/services/.../client/AxeClient.java:28` — `WebClientImpl`-based Axe API calls (`createAssistant`, `assignPhoneNumber`, `getCallRecordingUrl`, …); no MicroProfile fault-tolerance annotations.
- `AssistantCallRecordEntity` — `axe/db-entities/.../entities/AssistantCallRecordEntity.java` — Axe dedup; `call_id` `unique=true` (`:46`), separate unique id (`:31`), non-unique `public_call_id` (`:61`).

## Don't-do-here / gotchas
- **Logytext webhook authenticity is still not verified** — `LogytextPubSubConsumer` (`:52` `consume`, `processMessage` below it) has zero `signature`/`hmac`/`verify` references. If the topic ACL is loosened or shared, anyone with publish rights can spoof Logytext events. Add HMAC validation against Logytext's signing key.
- **Logytext consumer drops on the non-ack path** — it implements `PubSubConsumerBlocking` (not the ack/reply variant); an unknown `objectType` is logged at error and silently dropped, and there's no explicit `nack` on failure. Contrast `AxeWebhookPubSubConsumer`, which safe-acks/nacks explicitly.
- **Production `quarkus.datasource.jdbc.max-size=4`** — `configuration/.../application.properties:4`, still 4. For a service with multiple Pub/Sub consumers plus the QuickBooks SDK this is alarmingly small; bump to 16+.
- **No MicroProfile fault tolerance anywhere** — zero `@Retry`/`@Timeout`/`@CircuitBreaker` in the repo; all resilience must come from `WebClientCallConfig` (verify per-call connect/read timeouts are actually set, e.g. `AxeClient.buildApiKeyConfig` at `:187`). A hung Axe/QuickBooks call otherwise blocks consumer threads.
- **QuickBooks refresh atomicity — now partly addressed** — `QuickbooksFacade` uses `TransactionalExecution`; the old "token persisted while op half-executes" concern is mitigated, but confirm the refresh + downstream op share one transactional boundary.
- **Axe dedup key** — dedup is on `call_id` (unique). There is no `event_id` column; if Axe's at-least-once delivery keys on anything other than `call_id`, dedup would miss. Confirm the upstream idempotency field.
- `OAuth2ClientFactory.clientSecret` `@ConfigProperty` is not marked sensitive — verify it is never echoed by `/q/info` or logged (compare the fleet secrets-in-logs findings).

## Relevant ADRs / docs
- README is substantive (env bootstrap + module layout) — not a template stub.
- `~/projects/quarkus-fleet-review-2026-05-07.md#6-integrations-backend` — full review (its Quarkus 3.15.2 + QuickBooks-atomicity findings are now stale).


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `AssistantAudioSyncEntity` | jpa | `axe` | AssistantAudioSync |
| `AssistantCallRecordEntity` | jpa | `axe` | AssistantCall |
| `IntegrationEntity` | jpa | `db-entities` | Integration |
| `IntegrationErrorEntity` | jpa | `db-entities` | IntegrationError |
| `QuickbooksConfigEntity` | jpa | `quickbooks` | QuickbooksConfig |
| `QuickbooksCredentialsEntity` | jpa | `quickbooks` | QuickbooksCredentials |
| `QuickbooksOauthCsrf` | jpa | `quickbooks` | QuickbooksOauthCsrf |
| `AssignPhoneNumberRequestDto` | dto | `axe` | AssignPhoneNumber |
| `AssignPhoneNumberResponseDto` | dto | `axe` | AssignPhoneNumber |
| `AssistantCallAudioResponseDto` | dto | `axe` | AssistantCallAudio |
| `AssistantCallRecordResponseDto` | dto | `axe` | AssistantCall |
| `AttachmentDetailsDto` | dto | `attachment` | AttachmentDetails |
| `AuthConfigDto` | dto | `axe` | AuthConfig |
| `AvailablePhoneNumberDto` | dto | `twilio` | AvailablePhoneNumber |
| `AxeWebhookRequestDto` | dto | `axe` | AxeWebhook |
| `BodyFieldConfigDto` | dto | `axe` | BodyFieldConfig |
| `CallCountersResponseDto` | dto | `axe` | CallCounters |
| `CallEventDataDto` | dto | `axe` | CallEventData |
| `CallRecordingUrlResponseDto` | dto | `axe` | CallRecordingUrl |
| `ChannelStateDto` | dto | `integrations-backend-dtos` | ChannelState |
| `CompanyConfig` | dto | `quickbooks` | [CompanyConfig](../domains/entities/CompanyConfig.md) |
| `CompanyContextDto` | dto | `integrations-backend-dtos` | CompanyContext |
| `ConnectionStatusAndConfigDto` | dto | `quickbooks` | ConnectionStatusAndConfig |
| `ConnectionStatusDto` | dto | `quickbooks` | ConnectionStatus |
| `ContextDto` | dto | `integrations-backend-dtos` | Context |
| `CreateAssistantEndpointRequestDto` | dto | `axe` | CreateAssistantEndpoint |
| `CreateAssistantRequestDto` | dto | `axe` | CreateAssistant |
| `CreateAssistantResponseDto` | dto | `axe` | CreateAssistant |
| `CreateByopPhoneNumberRequestDto` | dto | `axe` | CreateByopPhoneNumber |
| `CreateByopPhoneNumberResponseDto` | dto | `axe` | CreateByopPhoneNumber |
| `CreateInvoiceDto` | dto | `quickbooks` | CreateInvoice |
| `CreateTransferToolRequestDto` | dto | `axe` | CreateTransferTool |
| `CreateTransferToolResponseDto` | dto | `axe` | CreateTransferTool |
| `DemoCallOrderDetails` | dto | `axe` | DemoCallOrderDetails |
| `DemoCallResponseDto` | dto | `axe` | DemoCall |
| `HeaderConfigDto` | dto | `axe` | HeaderConfig |
| `Integration` | dto | `services` | Integration |
| `IntegrationDto` | dto | `integrations-backend-dtos` | Integration |
| `IntegrationError` | dto | `services` | IntegrationError |
| `IntegrationEvent` | dto | `services` | IntegrationEvent |
| `IntegrationEventMessageDto` | dto | `integrations-backend-dtos` | IntegrationEventMessage |
| `InvoiceDto` | dto | `quickbooks` | Invoice |
| `LogytextChannelStateDto` | dto | `logytext` | LogytextChannelState |
| `LogytextIntegrationEvent` | dto | `logytext` | LogytextIntegrationEvent |
| `LogytextIntegrationPubSubDto` | dto | `logytext` | LogytextIntegration |
| `LogytextPubSubMessageDto` | dto | `logytext` | LogytextPubSubMessage |
| `LogytextUnreadChannelDto` | dto | `logytext` | LogytextUnreadChannel |
| `OAuth2ClientFactory` | dto | `quickbooks` | OAuth2ClientFactory |
| `OrderDetailsBasicDto` | dto | `axe` | OrderDetailsBasic |
| `PersonaConfigDto` | dto | `axe` | PersonaConfig |
| `StructuredDataDto` | dto | `axe` | StructuredData |
| `TranscriptEntryDto` | dto | `axe` | TranscriptEntry |
| `TwilioCredentialsDto` | dto | `twilio` | TwilioCredentials |
| `UnreadChannelDto` | dto | `integrations-backend-dtos` | UnreadChannel |
| `UserContextDto` | dto | `integrations-backend-dtos` | UserContext |
| `VoiceConfigDto` | dto | `axe` | VoiceConfig |
| `WebhookAuthHeaderDto` | dto | `axe` | WebhookAuthHeader |
<!-- entities-end -->
