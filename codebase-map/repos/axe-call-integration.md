---
repo: axe-call-integration
path: ~/projects/ship-cars-usa/axe-call-integration
stack: Java/Quarkus 3.27.0 (Java 21)
domain: integrations
shape: single-module
last-synced-commit: d9a2609969f7f0c1c2c2d8ff66c5d545ed7619f6
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# axe-call-integration

## What it is
Quarkus 3.27.0 / Java 21 single-module microservice that **bridges Ship.Cars loads to AXE's AI-driven outbound phone-call service** (`https://agent.joinaxe.ai`). Initiates calls per load, polls call status/detail, syncs AXE campaigns, and consumes `call.ended` webhooks via Pub/Sub, then fans out an email notification. Layered `resource → service → repository → entity`, PostgreSQL 17 + Flyway + Panache + MapStruct + Lombok. Runs on port **7071** (test 7072). **Fleet-rarity**: one of the very few services with MicroProfile Fault Tolerance actually wired on its `@RegisterRestClient` interfaces (`@Timeout(5000)` + `@Retry` + `@CircuitBreaker` on every AXE method) — the correct posture, though the timeout is hardcoded in the annotation, not externalized.

## How it fits
- **Consumes API of:**
  - External **AXE API** — `AxeApiClient` (configKey `axe-api`, `@Path("/api/v1/phone/")`, base `https://agent.joinaxe.ai`) and `AxeCampaignApiClient` (same configKey `axe-api`, `@Path("/api/v1/campaigns")`). Every method carries `@Timeout(5000)` + `@Retry` (maxRetries 2–3) + `@CircuitBreaker`; campaign methods add `@RetryWhen(IsRetryable.class)`.
  - `impersonator` — `ImpersonatorServiceClient` (configKey `impersonator-service`, `@Path("/impersonate/user/{userId}/api/posting/v4")`) for user-attributed calls into posting. **No fault-tolerance annotations on this client** (see gotchas).
- **Publishes events to:** Pub/Sub notifications topic `ship.cars.notification.topic=${PUBSUB_NOTIFICATIONS_TOPIC}` via the ship.cars `notification` Quarkus extension (`NotificationClient`, injected in `AxeCallServiceImpl`). JSON DTOs, no schema registry.
- **Subscribes to:** Pub/Sub subscription `axe.config.webhook-subscription=${WEBHOOK_SUBSCRIPTION}` via `AxeWebhookPubSubListener` (ship.cars `pubsub` extension), handling only `call.ended` events.
- **Owns data store:** PostgreSQL db `axe_call_integration` (dev port 7030, dev pool `max-size=16`; no in-repo prod pool block). Hibernate Envers audit on all three entities; Flyway owns schema (`schema-management.strategy=none`).

## Build / test / run
```
./mvnw clean package -DskipTests
./mvnw quarkus:dev              # dev; app on :7071 (test :7072)
# Single-module Quarkus; native build supported (GraalVM)
```

## Key abstractions
- `AxeCallResource` — `src/main/java/cars/ship/axecallintegration/resource/AxeCallResource.java` — `@Path("/api/v1/loads")`: `POST /{loadId}/calls` (initiate), `GET /{loadId}/calls` (list, paginated), `GET /{loadId}/calls/{callId}/status`, `GET /calls/{callId}` (detail).
- `AxeCampaignResource` — `resource/AxeCampaignResource.java` — `@Path("/api/v1/campaigns")`: `POST /sync` (upserts campaigns + call records from AXE; defaults to last 1 campaign).
- `AxeApiClient` — `client/AxeApiClient.java` — the **good** REST-client pattern: `@Timeout(5000)` + `@Retry` + `@CircuitBreaker` + `@CircuitBreakerName` per method.
- `AxeCampaignApiClient` — `client/AxeCampaignApiClient.java` — same posture plus `@RetryWhen(IsRetryable.class)`.
- `ImpersonatorServiceClient` — `client/ImpersonatorServiceClient.java` — REST client (not a service); no fault tolerance.
- `AxeCallServiceImpl` — `service/impl/AxeCallServiceImpl.java` — core call orchestration: AXE calls, `call.ended` processing, notification publish.
- `AxeCampaignServiceImpl` — `service/impl/AxeCampaignServiceImpl.java` — fetch + upsert campaigns/call records.
- `AxeWebhookPubSubListener` — `service/listeners/AxeWebhookPubSubListener.java` — blocking Pub/Sub consumer (`PubSubAckReplyConsumerBlocking<WebhookEventDto>`) for `call.ended`.

## Don't-do-here / gotchas
- **`@Timeout(5000)` is hardcoded in the AXE client interface annotations** — an AXE SLA change requires a code change + redeploy. No `quarkus.rest-client.axe-api.connect-timeout`/`read-timeout` properties exist; externalize if the SLA is expected to move.
- **`ImpersonatorServiceClient` has NO timeout/retry/circuit-breaker** and no `connect-timeout`/`read-timeout` property — the one unprotected out-edge. An impersonator slowdown hangs the worker thread indefinitely. This is the retry-without-timeout family, minus the retry.
- **Notifications publish is fire-and-forget** — a Pub/Sub publish failure silently loses the downstream email notification; no outbox.
- **No explicit webhook idempotency key** — relies on AXE call-ID uniqueness in local PG against at-least-once Pub/Sub redelivery; the upsert path must stay idempotent.
- **No prod pool sizing in-repo** — only `%dev.max-size=16`; prod pool comes from deploy/env config, not this file.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/impersonator.md` — the user-attribution gateway the impersonator client traverses.
- `~/projects/codebase-map/repos/posting-backend.md` — downstream (impersonator route).
- `~/projects/codebase-map/relations/rest-client-registry.md` — AXE clients are timeout-clean; the impersonator client is not.
- `~/projects/codebase-map/domains/integrations.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `AxeCallEntity` | jpa | `axe-call-integration` | AxeCall |
| `AxeCallRecordEntity` | jpa | `axe-call-integration` | AxeCall |
| `AxeCampaignEntity` | jpa | `axe-call-integration` | AxeCampaign |
| `CallDetailViewDto` | dto | `axe-call-integration` | CallDetailView |
| `CallDetailsResponseDto` | dto | `axe-call-integration` | CallDetails |
| `CallEndedEventDataDto` | dto | `axe-call-integration` | CallEndedEventData |
| `CallRecordDto` | dto | `axe-call-integration` | Call |
| `CallResponseDto` | dto | `axe-call-integration` | Call |
| `CallStatusResponseDto` | dto | `axe-call-integration` | CallStatus |
| `CallsPageResponseDto` | dto | `axe-call-integration` | CallsPage |
| `CallsPageViewDto` | dto | `axe-call-integration` | CallsPageView |
| `CampaignDto` | dto | `axe-call-integration` | Campaign |
| `CampaignListResponseDto` | dto | `axe-call-integration` | CampaignList |
| `CampaignSyncResponseDto` | dto | `axe-call-integration` | CampaignSync |
| `CreateCallRequestDto` | dto | `axe-call-integration` | CreateCall |
| `CreateCallResponseDto` | dto | `axe-call-integration` | CreateCall |
| `InitiateCallRequestDto` | dto | `axe-call-integration` | InitiateCall |
| `InitiateCallResponseDto` | dto | `axe-call-integration` | InitiateCall |
| `TranscriptSegmentDto` | dto | `axe-call-integration` | TranscriptSegment |
| `WebhookEventDto` | dto | `axe-call-integration` | Webhook |
<!-- entities-end -->
