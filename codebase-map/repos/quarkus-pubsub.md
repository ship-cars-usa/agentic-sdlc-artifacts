---
repo: quarkus-pubsub
path: ~/projects/ship-cars-usa/quarkus-pubsub
stack: Java 21 / Quarkus 3.27.5 extension (runtime + deployment) — `ship.cars.quarkus.extensions.pubsub` 3.27.5.1-SNAPSHOT, GCP Pub/Sub (`google-cloud-pubsub`)
domain: platform
shape: multi-module (runtime + deployment + coverage-report)
last-synced-commit: a69b7b13e89a8711b92394acaefd464927eb915c
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# quarkus-pubsub

## What it is
**The fleet's GCP Pub/Sub publish-and-subscribe substrate for Quarkus services.** A Quarkus extension wrapping `google-cloud-pubsub` with:

- Typed consumer interfaces — `PubSubConsumerBlocking<T>` (`consume(T, meta)` returns void: no thrown exception ⇒ ACK, thrown exception ⇒ NACK) and `PubSubAckReplyConsumerBlocking<T>` (caller returns a `PubSubAckReply` ACK/NACK).
- `PubSubPublisher` (async, returns `ApiFuture<String>`) and `PubSubPublisherSync` (blocking, returns the message id). Both support raw `PubsubMessage` or typed `T`, optional attribute headers, and optional message ordering.
- Object↔message conversion via `PubSubMessageConverter` (Jackson-backed, honoring the service's `ObjectMapperConfigCustomizer` — same date/naming rules on the wire). No schema registry: **JSON DTOs only** — no Avro/Protobuf/Confluent.
- GCP-only subscriber provider (`GcpPubsubSubscriberProvider` + `FlowControlGcpPubSubSubscriberProviderConfigurer`). No Kafka, no in-memory bus — Pub/Sub is the fleet's sole async pattern.
- Optional emulator support (`ship.cars.pubsub.emulator-host`) and a global `ship.cars.pubsub.consumers-enabled` flag (default `true`) to start with publishers active but consumers paused.

OTel-aware (depends on `quarkus-opentelemetry` from quarkus-commons) so consumer execution shows as a span without per-consumer instrumentation.

## How it fits
- **What it provides:** the publish + consume API and the GCP subscriber wiring; topics/subscriptions are named by consumers.
- **Who consumes it (compile-time):** ~32 fleet repos reference `ship.cars.quarkus.extensions.pubsub` directly — nearly every Quarkus service (event routing: `pusher`, `notification-orchestrator`, `payment-backend`; listings/ML: `cube`, `load-recommender`, `loadboard-backend`, `saved-search-handler`, `trip-planner`, `location-history-backend`; Keycloak SPIs; integrations). Plus it is a **transitive** dependency of `quarkus-notification-client` and `quarkus-user-syncer`, so its real reach is wider than the direct count.
- **Consumes API of:** Google Cloud Pub/Sub (publish + subscribe). GCP credentials via `GOOGLE_APPLICATION_CREDENTIALS`; publisher falls back to ADC / workload identity otherwise.
- **Publishes events to:** n/a (library).
- **Owns data store:** none.

## Build / test / run
```
./mvnw clean install -DskipTests
./mvnw test
./deploy-project.sh      # deploy runtime + deployment to GitHub Packages
```
Consumed via:
```xml
<dependency>
  <groupId>ship.cars.quarkus.extensions.pubsub</groupId>
  <artifactId>runtime</artifactId>
  <version>${ship-cars-quarkus-extensions-pubsub.version}</version>
</dependency>
```
Config (`PubSubConfig`, prefix `ship.cars.pubsub`): `emulator-host` (optional), `consumers-enabled` (default `true`). That's the whole extension surface — everything else (topics, subscriptions, retry, DLQ, flow-control) is configured per-consumer or in GCP.

## Key abstractions
- `PubSubConsumerBlocking<T>` — `runtime/.../listener/PubSubConsumerBlocking.java` — implement `getSubscription()`, `getMessageClass()`, `consume(T, PubSubMessageMeta)`. The canonical fleet consumer shape.
- `PubSubAckReplyConsumerBlocking<T>` — `runtime/.../listener/PubSubAckReplyConsumerBlocking.java` — same shape, `consume` returns `PubSubAckReply` (ACK/NACK) for explicit control (e.g. ACK-and-drop a poison message).
- `PubSubMessageMeta` — `runtime/.../listener/PubSubMessageMeta.java` — messageId, publishTime, attributes; consumers read `attributes` for correlation IDs.
- `PubSubPublisher` / `PubSubPublisherImpl` — `runtime/.../publisher/` — async publish returning `ApiFuture<String>`.
- `PubSubPublisherSync` / `PubSubPublisherSyncImpl` — blocking publish; `PubSubPublisherSyncImpl.publish` does `future.get()` (`PubSubPublisherSyncImpl.java:78`) with **no timeout** and logs elapsed ms.
- `PubSubMessageConverter` — `runtime/.../common/PubSubMessageConverter.java` — Jackson object↔`PubsubMessage`.
- `PubsubMessageReceiver` / `PubsubAckReplyMessageReceiver` — `runtime/.../listener/impl/` — adapters to the GCP `MessageReceiver` SPI; where ACK/NACK actually fires.
- `GcpPubsubSubscriberProvider` + `FlowControlGcpPubSubSubscriberProviderConfigurer` — `runtime/.../listener/*gcp/` — wire GCP `FlowControlSettings` (max outstanding messages/bytes).
- `PubSubConfig` — `runtime/.../config/PubSubConfig.java` — the two-knob `@ConfigMapping`.
- `PubSubExtensionProcessor` — `deployment/.../PubSubExtensionProcessor.java`.

## Don't-do-here / gotchas
- **Retry & dead-lettering live in GCP, not in code.** The extension NACKs on exception and lets GCP redeliver. A consumer that throws on every message redelivers forever unless the subscription sets `Maximum delivery attempts` + a `Dead letter topic`. Every prod subscription should have both (README).
- **No in-code DLQ scaffolding** — draining/re-publishing a DLQ is an operator/consumer concern.
- **`PubSubPublisherSync.publish(...)` and any `future.get()` block with no timeout.** For low-latency request paths prefer async `PubSubPublisher`; if you must `.get()`, use `.get(N, TimeUnit.SECONDS)` at the call site or a stuck publisher hangs the caller. This is the same pattern that makes `quarkus-notification-client` propagate Pub/Sub latency into callers.
- **Auto-ACK is forgiving.** `PubSubConsumerBlocking` "no exception ⇒ ACK" means a consumer that returns early silently drops the message; prefer `PubSubAckReplyConsumerBlocking` whenever the logic branches. Several fleet P0s are flavors of this (see `relations/pubsub-firehose-consumer-map`).
- **`consumers-enabled=false` only gates new consumer startup** — not a graceful drain of in-flight consumers.
- **OTel propagation depends on `quarkus-opentelemetry`** — a service excluding it loses consumer-side spans.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/quarkus-notification-client.md` — consumer whose blocking `future.get()` is the canonical "Pub/Sub latency in caller's thread" case.
- `~/projects/codebase-map/repos/quarkus-user-syncer.md` — implements the `db-syncer` pattern on this extension.
- `~/projects/codebase-map/repos/pusher.md` — densest consumer / central router.
- `~/projects/codebase-map/relations/service-graph.md` — every Pub/Sub edge flows through this extension.
- `~/projects/codebase-map/domains/platform.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `PubSubMessageMeta` | dto | `runtime` | PubSubMessageMeta |
<!-- entities-end -->
