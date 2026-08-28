---
repo: quarkus-notification-client
path: ~/projects/ship-cars-usa/quarkus-notification-client
stack: Java 21 / Quarkus 3.27.5 extension (runtime + deployment + integration-tests) — `ship.cars.quarkus.extensions.notification`
domain: communication
shape: multi-module (runtime + deployment + integration-tests + coverage-report)
last-synced-commit: 1f5a74ce14212d420679bf4f6a100840fef4cb58
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# quarkus-notification-client

## What it is
**Quarkus extension library — not a deployed service.** A thin CDI producer that vends a fluent `NotificationClient` over GCP Pub/Sub. Consumers `@Inject NotificationClient`, call one of the send methods, and the client builds a `V1NotificationPubSubDto` and publishes it (via `quarkus-pubsub`'s `PubSubPublisher`) to a configured topic; downstream `pusher` drains the topic and fans out to channels. **Requires the `quarkus-pubsub` extension to be installed** (hard dependency, pinned at 3.27.5).

The interface exposes **5 notification types, each in a simple and a callback variant = 10 methods**: `sendWebSocket`, `sendEmail`, `sendPush`, `sendPushV2`, `sendSms`. Notification payload DTOs come from `notification-dtos` (`cars.ship.notification.dtos`, v1.2.0), e.g. `V1EmailNotificationDataDto`, `V1SmsNotificationDataDto`, `V2PushNotificationDataDto` — not `models-lib`.

## How it fits
- **What it provides:** the `NotificationClient` API + a CDI producer wiring it to a topic. Each message is tagged with a `senderService` attribute (`MSG_HEADER_SENDER_SERVICE`) resolved at construction from env `DD_SERVICE`, else `POD_ID`, else `UNKNOWN`.
- **Who consumes it (compile-time):** ~16 fleet repos reference `ship.cars.quarkus.extensions.notification` in their poms. (Prior sync's "40+ consumers" was over-stated for this artifact — the 40+/70-ish scale belongs to `quarkus-pubsub`, which this extension depends on transitively.) Still a high-blast-radius public API: a signature change forces every consumer to recompile.
- **Consumes API of:** n/a (library).
- **Publishes events to:** a configurable Pub/Sub topic (`ship.cars.notification.topic` / env `SHIP_CARS_NOTIFICATION_TOPIC`) via `PubSubPublisher`.
- **Owns data store:** none. Stateless producer.

## Build / test / run
```
./mvnw clean install       # builds runtime + deployment + integration-tests
./deploy-project.sh        # deploy to GitHub Packages (Argo CD on master)
```
Consumed via:
```xml
<dependency>
  <groupId>ship.cars.quarkus.extensions.notification</groupId>
  <artifactId>runtime</artifactId>
  <version>${ship-cars-quarkus-extensions-notification.version}</version>
</dependency>
```
Config (README):

| Property | Env var | Default | Meaning |
|---|---|---|---|
| `ship.cars.notification.topic` | `SHIP_CARS_NOTIFICATION_TOPIC` | (none) | Pub/Sub topic to publish to. |
| `ship.cars.notification.logs-enabled` | `SHIP_CARS_NOTIFICATION_LOGS_ENABLED` | `false` | When true, publish/success/error logs go at INFO; otherwise DEBUG. |

## Key abstractions
- `NotificationClient` — `runtime/.../NotificationClient.java` — public interface (10 methods; 5 types × simple/callback).
- `NotificationClientImpl` — `runtime/.../impl/NotificationClientImpl.java` — builds `V1NotificationPubSubDto`, restores MDC via `commons.MdcUtils`, publishes, wires success/error callbacks, then **blocks on `future.get()`**. Adds an `[NC-N]` MDC log prefix per call (`callCounter`).
- `NotificationsClientProducer` — `runtime/.../impl/NotificationsClientProducer.java` — CDI producer vending the singleton client from config.
- `NotificationClientRecord` — `runtime/.../impl/NotificationClientRecord.java` — immutable config wrapper (topic, senderService, logsEnabled).
- `WebSocketRoomUtils` — `runtime/.../impl/WebSocketRoomUtils.java` — user/company IDs → socket.io room names (`user_<id>`, `company_<id>`, `global`).
- `NotificationsClientConfig` — `runtime/.../config/NotificationsClientConfig.java` — `@ConfigMapping` for the two properties.
- `NotificationExtensionProcessor` — `deployment/.../NotificationExtensionProcessor.java` — build-step processor.

## Don't-do-here / gotchas
- **The "async" publish blocks.** `NotificationClientImpl.doSendNotification` calls `future.get()` on the Pub/Sub `ApiFuture` **with no timeout** (`NotificationClientImpl.java:235`). Every send therefore blocks the caller until Pub/Sub ACKs; Pub/Sub slowness propagates straight into every consumer's request thread. Same latency contract as `quarkus-pubsub`'s `PubSubPublisherSync`.
- **Callbacks run on `MoreExecutors.directExecutor()`** — a slow user-supplied `onSuccess`/`onError` blocks the shared Pub/Sub response thread. Keep callbacks trivial or hand off to a bounded executor.
- **`logs-enabled=false` by default** downgrades all publish/callback logs to DEBUG, so in prod (typically INFO) notification publishes are effectively silent. Note the callback-routing quirk: when a caller supplies its own callback *and* `logsEnabled=false`, the client calls the raw callback and skips its own logging entirely.
- **High-coupling public contract** — treat as a stable API; major-bump on breaking changes and use deprecation cycles.
- **No receiver-list validation** — empty receiver lists and malformed event names publish silently; only `pusher` guards server-side.
- **Room-name format (`user_<id>`, `company_<id>`, `global`) is coupled to `socket-server`'s middleware** — can't change unilaterally.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/quarkus-pubsub.md` — the required substrate; its `future.get()` is the same blocking pattern.
- `~/projects/codebase-map/repos/pusher.md` — downstream consumer of the notification topic.
- `~/projects/codebase-map/repos/socket-server.md` — websocket room conventions.
- `~/projects/codebase-map/domains/communication.md`.
