---
repo: keycloak-events-plugin
path: ~/projects/ship-cars-usa/keycloak-events-plugin
stack: Java 17 / Keycloak SPI plugin (Keycloak 24.0.4 SPI)
domain: identity
shape: single-module
last-synced-commit: 499d81d8bc5da903ae1608ef2d1ae8aa1ed35b19
last-synced-date: 2026-05-11
maintainer: unknown
status: seed
---

# keycloak-events-plugin

## What it is
**Keycloak SPI plugin (not a service)** — Java 17 JAR packaged with `maven-assembly-plugin` (jar-with-dependencies). Implements `EventListenerProvider` (provider ID: `pubsub-publisher`) to intercept every Keycloak authentication / user-lifecycle event and publish it to Google Pub/Sub. Each event is enriched with a `User` record (email, name, enabled, verified) before publish. Also ships a secondary `MixpanelEventListener` gated by an Unleash toggle (`common.mixpanel-events.frontend`). **The source-of-truth producer for the `keycloak-events-topic` consumed by `fraud-detector` and `pusher`**.

## How it fits
- Consumes API of: Keycloak SPI hooks (`onEvent(Event)`); Unleash (toggle lookup, in Mixpanel path); Mixpanel (optional).
- Publishes events to: Pub/Sub topic configured via `KC_SPI_EVENTS_TOPIC` / Keycloak config scope `events.topic`. Ordering key = `event.userId`.
- Subscribes to: not applicable — plugin is invoked synchronously by Keycloak.
- Owns data store: none.

## Build / test / run
```
./mvnw clean package
# Produces target/events-publisher-*-jar-with-dependencies.jar
# Drop into Keycloak's /opt/keycloak/providers/ directory (the `keycloak` repo's Dockerfile does this)
```

## Key abstractions
- `PublisherEventsListener` — `src/main/java/cars/ship/keycloak/extension/events/PublisherEventsListener.java:19-137` — implements `EventListenerProvider`; intercepts, enriches, serializes, publishes.
- `ExtendedEvent` — nested record in `PublisherEventsListener` (lines 89-136) — wraps Keycloak's `Event` with a `User` record.
- `PubSubPublisherProvider` — `src/main/java/cars/ship/keycloak/extension/events/PubSubPublisherProvider.java:1-54` — factory; wires `MessageConverter` + `publisherFactory` from `ship.cars.quarkus-pubsub` 1.0.0.
- `PublisherEventsListenerFactory` — `@AutoService`-registered SPI factory; provider ID `pubsub-publisher`.
- `MixpanelEventListener` — `src/main/java/cars/ship/keycloak/extension/events/mixpanel/MixpanelEventListener.java` — secondary; Unleash-gated.

## Don't-do-here / gotchas
- **SPI target version skew**: built against Keycloak **24.0.4** SPI; deployed alongside Keycloak **26.0.5**. SPI is generally stable across minor versions but verify on each KC upgrade. Add a compatibility test.
- **`PubSubPublisher` is a singleton** with lazy + synchronized init and **no refresh** — runtime config changes require Keycloak restart.
- **No error retry / DLQ on publish** — `IOException` during Pub/Sub publish is logged and swallowed (line ~ check `PublisherEventsListener`). **Failed events are silently lost.** Add a local file/DB outbox or surface to Keycloak's own event log.
- **Synchronous user enrichment** — every event triggers a Keycloak session lookup. High event-rate (e.g., bot login storm) can pressure the Keycloak request thread; consider caching the user record briefly.
- **Admin events are ignored** — `onEvent(AdminEvent, boolean)` is a no-op. Realm-config changes, role assignments, etc. are not published. If downstream needs admin visibility, this is the gap to fix.
- **Topic name silently nullable** — if `KC_SPI_EVENTS_TOPIC` is unset, `Config.getEventsTopic()` returns null and publish fails. Add a startup assertion.
- **Mixpanel toggle is feature-flag-coupled** — a Unleash outage may flip the toggle in either direction depending on the client's offline-default; verify the failure mode.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/keycloak.md` — the deployment image that bundles this plugin.
- `~/projects/codebase-map/repos/fraud-detector.md` — primary consumer of the published topic.
- `~/projects/codebase-map/repos/pusher.md` — likely secondary consumer (user-state subscription).
- `~/projects/codebase-map/domains/identity.md`.
