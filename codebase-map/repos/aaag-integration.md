---
repo: aaag-integration
path: ~/projects/ship-cars-usa/aaag-integration
stack: Java 21 / Quarkus 3.27.5
domain: integrations
shape: multi-module (7 poms)
last-synced-commit: 5d24dace0de13a9f24ea6c181d7f978c4bdca1a5
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# aaag-integration

## What it is
Quarkus 3.27.5 / Java 21 async command executor for the **AAAG / ASI (Auction Edge)** carrier integration (distinct from the archived Python `aaag-integration-logs`). Receives Pub/Sub events (`AuctionEdgePubSubListener`, `PostingPubSubListener`), fans them onto the Vert.x event bus, and pushes to ASI's transport API — over **GraphQL by default** (`asi-transport-api=graphql`) with a REST implementation as the alternate. State (locks, load-leg / transportation / check-in records) is persisted in **Google Firestore**, not a relational DB. A per-load-leg lock document plus Firestore optimistic concurrency (updateTime `Precondition`) defuses Pub/Sub redeliveries.

## How it fits
- Consumes API of: ASI transport (external — GraphQL client `smallrye-graphql-client.asi`, REST clients configKeys `asi-rest` / `asi-auth`); internal `posting-internal`, `metadata`, `impersonator`, `attachment`, `user-management` REST clients.
- Publishes events to: internal Vert.x event bus via `eventBus.send()` (`POSTING_EVENT_RECEIVED`, `AUCTION_EDGE_EVENT_RECEIVED`); downstream `…EventProcessServiceImpl` consumers do the ASI push and own the `PubSubAckReply`.
- Subscribes to: Pub/Sub `aaag-integration.pubsub.posting-subscription` (`LoadLegMsgPubSubDto`) and `aaag-integration.pubsub.auction-edge-subscription` (`JsonNode`).
- Owns data store: **Google Firestore** — `StorageClient`/`StorageClientImpl` over `com.google.cloud.firestore`; document types `LoadLegProcessingLockStorageEntity`, `LoadLegsStorageEntity`, `TransportationDoneStorageEntity`, `TransportationUpdateStorageEntity`, `CheckInStorageEntity`, `CheckInNotMatchedIndexStorageEntity`. **No PostgreSQL / Hibernate / Envers.** `StorageCleanupServiceImpl` prunes old documents.

## Build / test / run
```
mvn clean install
mvn quarkus:dev   # http://localhost:8571/q/dev-ui , swagger at /q/swagger-ui
# 7 poms: root + api-dtos, application, commons, configuration, coverage-report, services
```

## Key abstractions
- `AsiTransportClient` — `services/.../services/asi/AsiTransportClient.java` — SPI with two impls: `AsiGraphqlTransportClient` (active) and `AsiRestTransportClient`, selected by `AsiTransportApiEnum` / `asi-transport-api`.
- `AsiAuthenticatedPushClient` — `services/.../services/impl/AsiAuthenticatedPushClient.java` — token-cached push wrapper (replaces the old `AsiPushServiceImpl`).
- `AsiAuthenticationService` / `AsiRestAuthenticationService` — token fetch + single-flight refresh with dedicated auth retry.
- `AsiRestClient` / `AsiRestAuthClient` / `AsiPushClient` — `services/.../clients/` — `@RegisterRestClient` ASI REST clients.
- `AsiRestClientLoggingFilter` — `services/.../clients/AsiRestClientLoggingFilter.java` — wire log for `AsiRestClient`; **response severity keyed to status (5xx→error, 4xx→warn, 404-on-charge-delete→info)** (SCP HEAD change, #449). Deliberately NOT registered on `AsiRestAuthClient` so the password/bearer token are never logged; business bodies carry no secrets (token travels as an unlogged header).
- `AuctionEdgePubSubListener` / `PostingPubSubListener` — `services/.../listeners/` — both implement `PubSubAckReplyConsumerBlocking`; thread the `PubSubAckReply` through `EventMsg` to the event-bus consumer.
- `StorageClientImpl` — `services/.../storage/impl/StorageClientImpl.java` — Firestore CRUD with optimistic concurrency; `ResourceExhaustedException` retried with equal-jitter exponential backoff (`RetryUtils.executeWithRetry`).

## Don't-do-here / gotchas
- **REST-client timeouts are now set** — `asi-rest` and `asi-auth` both have `connect-timeout=5000` / `read-timeout=10000` (`application.properties:118-119,127-128`). The old fleet-review P0 (no ASI timeouts) is resolved for the REST path. **But the active GraphQL client (`smallrye-graphql-client.asi`) has no explicit timeout configured** (only URL, `:92`) — the default transport path is still exposed. Verify the smallrye GraphQL client timeout.
- **ASI push retry is fixed-delay (no jitter)** — `asi-max-retries=5`, `asi-backoff-per-retry-delay-ms=250` (`application.properties:104-105`); auth has its own `asi-auth-max-retries=3` / `1000ms` (`:112-113`). Firestore/storage retries DO use equal jitter; the ASI push path does not — add jitter to avoid synchronized retry bursts. No `@CircuitBreaker` on the ASI clients.
- **`PostingPubSubListener.consume` does not guard `eventBus.send()`** (`PostingPubSubListener.java:57-60`): the `PubSubAckReply` is passed into `EventMsg` for the event-bus consumer to ack/nack, and the send has a 30s `setSendTimeout`, but if `eventBus.send` itself throws before delivery the message is neither acked nor nacked. `AuctionEdgePubSubListener` explicitly `nack()`s on parse failure (`:92`) and meters it — better shaped.
- **Firestore RESOURCE_EXHAUSTED is the scaling ceiling** — write/read bandwidth caps trigger the equal-jitter retry; sustained load can exhaust attempts. Watch Firestore quota, not a DB pool.
- No relational datasource exists — ignore any prior "Hikari max-size" note; it does not apply.

## Relevant ADRs / docs
- `~/projects/quarkus-fleet-review-2026-05-07.md#1-aaag-integration` — full review (note: its Postgres/timeout findings are now stale — store is Firestore, ASI-REST timeouts added).
- `~/projects/quarkus-rest-client-timeout-anti-pattern.md` — fleet-wide retry-without-timeout pattern (GraphQL path still applies).


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `AaagChargesDto` | dto | `api-dtos` | AaagCharges |
| `AaagFileSourceDto` | dto | `api-dtos` | AaagFileSource |
| `AaagImportFileReceivedDto` | dto | `api-dtos` | AaagImportFileReceived |
| `AaagPullEventDto` | dto | `api-dtos` | AaagPull |
| `AaagTransportationDoneDataDto` | dto | `api-dtos` | AaagTransportationDoneData |
| `AaagTransportationUpdateDataDto` | dto | `api-dtos` | AaagTransportationUpdateData |
| `AsiAuthDto` | dto | `services` | AsiAuth |
| `AsiAuthParametersDto` | dto | `services` | AsiAuthParameters |
| `AsiAuthResponseDto` | dto | `services` | AsiAuth |
| `AsiAuthTokenResponseDto` | dto | `services` | AsiAuthToken |
| `AuctionEdgeCheckInDto` | dto | `services` | AuctionEdgeCheckIn |
| `AuctionEdgeEventDetailDto` | dto | `services` | AuctionEdgeEventDetail |
| `AuctionEdgeEventDto` | dto | `services` | AuctionEdge |
| `AuctionEdgeSellerDto` | dto | `services` | AuctionEdgeSeller |
| `ChargesEventDto` | dto | `api-dtos` | Charges |
| `CheckInInfoDto` | dto | `services` | CheckInInfo |
| `EventMsg` | dto | `services` | EventMsg |
| `InboundTransportationAddCharge` | dto | `services` | InboundTransportationAddCharge |
| `InboundTransportationAddChargeResponse` | dto | `services` | InboundTransportationAddCharge |
| `InboundTransportationNotice` | dto | `services` | InboundTransportationNotice |
| `InboundTransportationNoticeResponse` | dto | `services` | InboundTransportationNotice |
| `InboundTransportationResponse` | dto | `services` | InboundTransportation |
| `LoadLegInfoDto` | dto | `services` | LoadLegInfo |
| `LoadLegProcessingLockStorageEntity` | dto | `services` | LoadLegProcessingLockStorage |
| `MatchNonDescriptCheckInEventServiceImpl` | dto | `services` | MatchNonDescriptCheckInEventServiceImpl |
| `TransportationDoneEventProcessServiceImpl` | dto | `services` | TransportationDoneEventProcessServiceImpl |
| `TransportationProcessingUtils` | dto | `services` | TransportationProcessingUtils |
| `TransportationUpdateEventProcessServiceImpl` | dto | `services` | TransportationUpdateEventProcessServiceImpl |
| `CheckInNotMatchedIndexStorageEntity` | other | `services` | CheckInNotMatchedIndexStorage |
| `CheckInStorageEntity` | other | `services` | CheckInStorage |
| `LoadLegsStorageEntity` | other | `services` | LoadLegsStorage |
| `TransportationDoneStorageEntity` | other | `services` | TransportationDoneStorage |
| `TransportationUpdateStorageEntity` | other | `services` | TransportationUpdateStorage |
<!-- entities-end -->
