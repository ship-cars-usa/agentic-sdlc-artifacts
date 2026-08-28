---
repo: chat-backend
path: ~/projects/ship-cars-usa/chat-backend
stack: Java 21 / Spring Boot 3.2.12
domain: communication
shape: single-module
last-synced-commit: 978961435b67c153f606c03317f180abc1c46e13
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# chat-backend

## What it is
Real-time discussion / chat service (load-scoped message threads, WebSocket live updates, notification + email bridging). **Spring Boot 3.2.12 / Java 21, not Quarkus** despite `PROJECTS_INDEX.md` listing it under the Quarkus section (verified in `pom.xml:10-12`: `spring-boot-starter-parent` 3.2.12, plus `spring-boot-starter-web`, `-data-jpa`, `-oauth2-resource-server`, `-integration`, `-cache`, `-actuator`, OWASP html-sanitizer).

> **🔄 Re-synced 2026-08-28 — repo refactored to hexagonal architecture.** Source moved from a flat `service/…` layout to `application/{service,adapters/in,adapters/out}` + `domain/{model,ports}` + `config/`. All prior file:line references were re-grounded. New since last sync: a **`PostingClient`** REST client to `posting-backend` (`LITE-8046 extend-pub-sub-update-posting-dtos`, pulls in `posting-dtos`), a second Pub/Sub consumer **`CompanyStateConsumer`** (alongside `UserStateConsumer`), and OWASP-based `HtmlSanitizationServiceImpl` + `IdHashingServiceImpl`.

## How it fits
- Consumes API of: `user-backend` (`UserManagementClientImpl`), `media-proxy` (`MediaProxyService`), `posting-backend` (`PostingClientImpl`, new), and `notification-backend` (via the notification-client library).
- Publishes events to: live chat updates + notifications via `NotificationServiceImpl` (`application/adapters/out/pubsub/NotificationServiceImpl.java`) — `broadcastChanges()` (WebSocket/live), `publishEmail()` and `sendNotificationForUser()` (`@Async`).
- Subscribes to: GCP Pub/Sub — `UserStateConsumer` (user-state replication) and `CompanyStateConsumer` (company-state replication), wired in `config/pubsub/PubSubConsumersConfig`. JSON DTOs, no schema registry.
- Owns data store: PostgreSQL (discussions, messages, participants, replicated user/company state).

## Build / test / run
```
mvn clean package
mvn test
mvn spring-boot:run
```

## Key abstractions
- `DiscussionService` — `domain/ports/service/DiscussionService.java` — concrete discussion CRUD/read/mark-read logic (implements `DiscussionOperations`); contains the in-memory load-scoped filter at `:244-248` (see gotchas).
- `DiscussionController` — `application/adapters/in/web/rest/controller/DiscussionController.java` — REST boundary; calls `mediaProxyService.addMediaProxyAccess()` synchronously after retrieval.
- `NotificationServiceImpl` — `application/adapters/out/pubsub/NotificationServiceImpl.java` — `broadcastChanges()` (`:71`) for WebSocket live updates + `@Async` `publishEmail()` (`:90`) / `sendNotificationForUser()` (`:124`); all three catch-and-log only.
- `UserStateConsumer` / `CompanyStateConsumer` — `application/adapters/in/pubsub/` — Pub/Sub consumers replicating user/company state into the local DB.
- `PostingClientImpl` — `application/adapters/out/clients/PostingClientImpl.java` — REST client to `posting-backend` (new).
- `HtmlSanitizationServiceImpl` — `application/service/HtmlSanitizationServiceImpl.java` — OWASP html-sanitizer over inbound message bodies (XSS guard).

## Don't-do-here / gotchas
- **Spring Boot, not Quarkus** — `PROJECTS_INDEX.md` miscategorizes this. Don't reach for Quarkus annotations / config keys (`quarkus.datasource.*` doesn't apply; use `spring.datasource.*`). `application.properties` uses `spring.security.oauth2.resourceserver.*` keys (`:26-27`).
- **`NotificationServiceImpl.java:71-86`** — `broadcastChanges()` catches `Exception` and only logs (`:84-86`). If the downstream is down, callers see HTTP 200 but recipients never get the change. Either propagate, or queue with retry + DLQ.
- **`NotificationServiceImpl.java:90-114` / `:124-161`** — `@Async` `publishEmail()` / `sendNotificationForUser()` catch-and-log only; silent loss on notification-service outage.
- **`DiscussionService.java:244-248`** — the private `getDiscussion()` calls `discussionRepository.findAllDiscussionsByLoadId(loadId).stream().filter(...)` — loads all threads for a `loadId` and filters in-memory. For loads with many threads this is unbounded memory + CPU. Push the filter into the repository query and paginate.
- **`DiscussionService.java:140-147` (and `:411-419`)** — `discussionRepository.save(...)` followed by `broadcastChanges(...)` are not transactionally coordinated; a broadcast failure after save means the message is persisted but invisible. Use an outbox or pre-persist + retried broadcast.
- **`application.properties:133-134`** — HikariCP `maximumPoolSize=5`, `connectionTimeout=20000`. Starvation territory under any concurrent load. Bump to 20+.
- **`DiscussionController`** — synchronous `mediaProxyService.addMediaProxyAccess()` after main retrieval; Media Proxy slowness fully fails discussion fetch. Add timeout + degrade gracefully without media URLs.
- No explicit REST-client timeouts observed for the `UserManagement`, `MediaProxy`, `Posting`, `Notification` clients — confirm each sets connect/read timeouts.

## Relevant ADRs / docs
- `~/projects/quarkus-fleet-review-2026-05-07.md#4-chat-backend-spring-boot-3-2-12-not-quarkus` — full review
- User memory `chat_backend_stack.md` — the Spring/Quarkus miscategorization fact


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `Company` | jpa | `chat-backend` | [Company](../domains/entities/Company.md) |
| `Discussion` | jpa | `chat-backend` | Discussion |
| `Message` | jpa | `chat-backend` | ChatMessage |
| `Participant` | jpa | `chat-backend` | Participant |
| `AppConfigImpl` | dto | `chat-backend` | AppConfigImpl |
| `CompanyEventPubSubDto` | dto | `chat-backend` | CompanyEvent |
| `DiscussionDto` | dto | `chat-backend` | Discussion |
| `DiscussionService` | dto | `chat-backend` | DiscussionService |
| `Filter` | dto | `chat-backend` | [Filter](../domains/entities/Filter.md) |
| `MediaProxyService` | dto | `chat-backend` | MediaProxyService |
| `MessageDto` | dto | `chat-backend` | ChatMessage |
| `ParticipantDto` | dto | `chat-backend` | Participant |
| `UnreadDiscussionInfoDto` | dto | `chat-backend` | UnreadDiscussionInfo |
| `UnreadDiscussionInfoVo` | dto | `chat-backend` | UnreadDiscussionInfoVo |
| `User` | dto | `chat-backend` | [User](../domains/entities/User.md) |
| `UserEventPubSubDto` | dto | `chat-backend` | UserEvent |
| `WebSocketChatData` | dto | `chat-backend` | WebSocketChatData |
<!-- entities-end -->
