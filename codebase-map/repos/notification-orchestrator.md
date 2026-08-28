---
repo: notification-orchestrator
path: ~/projects/ship-cars-usa/notification-orchestrator
stack: Java / Quarkus 3.27.5 (LTS)
domain: communication
shape: multi-module (11 modules + parent pom)
last-synced-commit: 88b5ffefc53a3c615a25c43ad67d8dd84de82481
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# notification-orchestrator

## What it is
Quarkus 3.27.5 (LTS) service that **orchestrates email delivery directly to SendGrid** and stores the delivery audit trail. **Critical clarification of the fleet's notification topology**: this service does **not** wrap or call `notification-backend` — it has zero `@RegisterRestClient` declarations to it. Instead, it's the **email-channel parallel** to `notification-backend`'s general fan-out. Both services subscribe to Pub/Sub topics; both deliver via SendGrid; the boundary is currently undocumented and worth a deliberate design conversation.

> **🔄 Re-synced 2026-08-28 — two corrections since last sync:**
> 1. **Quarkus 3.8.3 → 3.27.5 LTS** (`pom.xml:46`; commit `SCP-000 Bump Quarkus version to 3.27.5`). The ship.cars pubsub / user-sync / persistence extensions were bumped to matching `3.27.5`. It is **no longer the fleet's laggard** — it is now on the current LTS.
> 2. **It DOES publish now.** `EmailService.sendEmail` publishes an email-update event to `emailEventsTopic` via `PubSubPublisherSync` (`EmailService.java:148`), and a new **`WebhookHandler` (`POST /webhook`)** ingests SendGrid delivery-event callbacks (`List<SendgridEmailEvent>` → `emailService.handleWebhookEvents`). The old "Publishes events to: None" claim was wrong.

## How it fits
- Consumes API of: **None as REST clients** (no `@RegisterRestClient` found). SendGrid integration via the `ship.cars.quarkus.extensions.notification` extension; user-data sync via `ship.cars.quarkus.extensions.user.syncer`; pubsub via `ship.cars.quarkus.extensions.pubsub` (all `3.27.5`).
- Publishes events to: GCP Pub/Sub **`emailEventsTopic`** (`PUBSUB_EMAIL_EVENTS_TOPIC`) — email-update/delivery events emitted from `EmailService` (`:148`). Also inbound: **`POST /webhook`** receives SendGrid delivery callbacks. JSON DTOs, no schema registry.
- Subscribes to: Pub/Sub `email-subscription` (consumes `SendEmailDto`), `user-subscription` (user-state replication into local DB), `company-subscription` (company-state replication) — `application.properties:67-69`.
- Owns data store: PostgreSQL primary (`Email`, `SendgridEmailEvent` audit tables) + a separate `usermanagement-db` reactive read-replica for sync (`max-size=10`, `health-exclude=true`).

## Build / test / run
```
./mvnw clean package -DskipTests
./mvnw -Pnative package           # GraalVM native
mvn quarkus:dev                   # dev mode
# HTTP port = ${PORT} (test profile: 9072)
# 11 modules: api-dtos, application, commons, configuration, coverage-report,
#             db-entities, db-migration, db-syncer, enums, resources, services
```

## Key abstractions
- `EmailListener` — `services/.../pubsub/EmailListener.java` — implements `PubSubConsumerBlocking<SendEmailDto>`; calls `emailService.sendEmail()` with safe consume-pattern semantics.
- `EmailService` — `services/.../EmailService.java` — orchestrates email workflows; persists `Email` + `SendgridEmailEvent` entities for audit; publishes email-update events to `emailEventsTopic` via `PubSubPublisherSync` (`:148`, publish failure caught-and-logged at `:151`); `handleWebhookEvents(...)` applies SendGrid delivery callbacks.
- `EmailController` — `resources/.../rest/EmailController.java` — `GET /emails/{id}` for retrieval / debugging.
- `WebhookHandler` — `resources/.../rest/WebhookHandler.java` — `POST /webhook`; parses a `List<SendgridEmailEvent>` and forwards to `EmailService.handleWebhookEvents` (SendGrid event ingestion).
- `UserManagementProducer` — `db-syncer/.../config/UserManagementProducer.java` — wires `CompanyPubSubListener` + `UserPubSubListener` from the user-syncer extension.
- `UserSyncService` / `CompanySyncService` — `db-syncer/...` — replicate user/company state into local DB so email lookups are local.

## Don't-do-here / gotchas
- **Quarkus is now on 3.27.5 LTS** (was 3.8.3 at the prior sync) — the earlier "significantly behind the fleet" warning is resolved; it is now current with `attachment-backend` and the rest of the 3.27.x cohort.
- **Boundary with `notification-backend` is undocumented (P1).** Risk: duplicate-channel sends if a Pub/Sub event lands on both services' subscriptions, or silent gaps if neither service consumes a particular topic. Action: write a 1-page note on which service handles which channel and which Pub/Sub subscriptions belong to which.
- **No REST-client timeouts visible** — but the service has no `@RegisterRestClient`s to time out. SendGrid is reached via the `notification-extension`; verify that *the extension* sets timeouts on its underlying HTTP client. If the extension doesn't, this service is exposed indirectly.
- **`PubSubConsumerBlocking` (blocking)** — under high mail volume, this can saturate the Quarkus blocking-worker thread pool. Confirm `quarkus.thread-pool.max-threads` (default 200) is high enough for the expected mail-send concurrency.
- **No outbox** — emails are inserted transactionally before SendGrid is called, but if the Pub/Sub `ack` fails *after* the email was sent, the same mail is sent again on redelivery. Confirm SendGrid idempotency or add a SendGrid-side dedup key.
- **`db-syncer` runs against a `usermanagement-db` read replica** (`health-exclude=true`, reactive pool max-size=10). If the replica lags, email-context lookups are stale. Tolerate or alert on lag explicitly.

## Relevant ADRs / docs
- `pom.xml:46` — Quarkus 3.27.5 confirmed.
- `configuration/application.properties:67-71` — user/company/email subscriptions + `email-events-topic` + `ship.cars.notification.topic` wiring.
- Extensions in use: `ship.cars.quarkus.extensions.pubsub` / `user.syncer` / persistence all at `3.27.5`; `ship.cars.quarkus.extensions.notification` (SendGrid).
- `~/projects/codebase-map/repos/notification-backend.md` — paired/parallel service. Boundary doc still missing.
- `~/projects/codebase-map/domains/communication.md` — re-read after seeding for the now-clearer picture.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `CompanyEntity` | jpa | `db-entities` | [Company](../domains/entities/Company.md) |
| `EmailEntity` | jpa | `db-entities` | Email |
| `UserEntity` | jpa | `db-entities` | [User](../domains/entities/User.md) |
| `DbCompany` | dto | `db-syncer` | [Company](../domains/entities/Company.md) |
| `DbUser` | dto | `db-syncer` | [User](../domains/entities/User.md) |
| `DbUserRow` | dto | `db-syncer` | DbUserRow |
| `Email` | dto | `services` | Email |
| `EmailDto` | dto | `api-dtos` | Email |
| `RecipientDto` | dto | `api-dtos` | Recipient |
| `SendEmailDto` | dto | `api-dtos` | SendEmail |
| `SendgridEmailEvent` | dto | `services` | SendgridEmailEvent |
<!-- entities-end -->
