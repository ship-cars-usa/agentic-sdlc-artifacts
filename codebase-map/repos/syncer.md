---
repo: syncer
path: ~/projects/ship-cars-usa/syncer
stack: Java/Quarkus 3.27.0 (shipcars-quarkus-bom 3.27.0), Java 21
domain: integrations
shape: multi-module (parent + 7 modules)
last-synced-commit: 71b131e2fabf3fce1bc4bedea056f470c776670e
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# syncer

## What it is
Quarkus / Java 21 **Elasticsearch-projection service** (package `cars.ship.syncer`). It is the write side of the fleet's CQRS read model: it consumes Pub/Sub change events from many upstream domains, converts each into an ES document, and bulk-indexes it. For full/backfill reindexing it **reads directly from ~7 other services' PostgreSQL databases** over reactive Quarkus datasources and streams rows into ES (the resyncer path). Ten Pub/Sub listeners (one per source stream) and eleven resyncers cover CTMS orders, CTMS loadboard postings, LBv3 postings/negotiations/trips, LM postings/contacts, company, saved-search percolate, location-log, and CTMS custom fields. **This is the service that owns the CTMS `loads` ES index that `cube` and others query** — not `cube` itself.

## How it fits
- Consumes API of: Elasticsearch (Quarkus `co.elastic.clients` extension — no `@RegisterRestClient`).
- Publishes events to: Pub/Sub notification topic `ship.cars.notification.topic` (`${SYNCER_NOTIFICATIONS_TOPIC}`) for error/failure notifications; also pushes WebSocket update payloads (`WebSocketDto`) alongside ES writes.
- Subscribes to (10 Pub/Sub subscriptions, all env-driven in `configuration/.../application.properties`): `lm-contacts`, `lm-posting`, `carrier` (CTMS orders — the CtmsOrdersIndexListener stream), `carrier-company`, `loadboard` (CTMS loadboard), `loadboard-v3` (LBv3 postings/negotiations/trips), `saved-search-percolate`, `load-location-log`, `metadata`, `trip-planner`. Note `ship.cars.pubsub.consumers-enabled=false` by default (enabled per-env).
- Owns data store: **writes Elasticsearch** (bulk, `VersionType.External`). **Reads 7 source PostgreSQL DBs read-only via reactive datasources** (each `reactive.max-size=4`, `health-exclude=true`): `lm-posting`, `saved-search`, `platform`, `lbv3`, `location-history`, `metadata`, `trip-planner`. Also Redis (`max-pool-size=10000`, `max-pool-waiting=10000`).

## Build / test / run
```
./mvnw clean package -DskipTests
./mvnw quarkus:dev
# Modules: application, resources, services, commons, configuration, api-dtos, coverage-report
# Bulk flush: syncer.es.config.flush-interval; resync: resync-max-operations=2000, resync-flush-interval=5
# CTMS-orders LWW guard toggle: syncer.ctms-orders.document-version-check-enabled (default true)
```

## Key abstractions
- `CtmsOrdersIndexListener` — `services/.../listeners/pubsub/CtmsOrdersIndexListener.java` — consumes the `carrier` subscription, routes by object type (load/order/sub_order/posting vs nested vehicle/attachment/activity_log) and writes the `loads` ES index. This is the CTMS orders index owner.
- `ElasticIndexManager` — `services/.../es/impl/ElasticIndexManager.java` — builds all ES bulk ops; `getIndexOperation`/`getUpdateOperation` use `.versionType(VersionType.External)` (l.418, l.450); `getUpdateOperationWithDocumentVersionCheck` (l.468) applies a Painless script that skips the write (`ctx.op='none'`) when the stored version is newer.
- `CtmsOrderDocumentConverter` — `services/.../converters/CtmsOrderDocumentConverter.java` — CTMS `LoadDto` → `CtmsOrderDocumentDto`; `calculateVersion(updateTime)` (l.734) = `update_time` epoch millis, applied at l.302/l.584.
- `CtmsMediaUrlTransformer` — `services/.../utils/CtmsMediaUrlTransformer.java` — glues `commonConfig.mediaBaseUrl()` onto stored attachment/media paths via `CommonUtil.addBaseUrlIfNeeded`. Applied to vehicle, attachment, and order documents during indexing.
- Ten per-stream listeners + eleven resyncers (`ResyncerBase` + per-index, e.g. `CtmsOrdersIndexResyncer`, `LoadboardV3IndexResyncer`) — resyncers stream from the source PG DB via SQL in `resources/files/sql/`.
- `BulkIngesterServiceImpl` / `BulkIngesterListener` — `services/.../es/impl/` — batched ES ingestion with ack/nack and version-carrying `BulkContext`.

## Don't-do-here / gotchas
- **CTMS orders LWW divergence (root cause of accept-vs-archive races).** `loads`-index updates use `VersionType.External` with version = `update_time` epoch millis (`getUpdateOperationWithDocumentVersionCheck` + `calculateVersion`). Any event whose `update_time` is not strictly newer than the stored doc is silently dropped (`ctx.op='none'`). Out-of-order or same-millisecond events → last-writer-wins → ES can diverge from the source of truth. Toggle: `syncer.ctms-orders.document-version-check-enabled`.
- **Media-URL assembly lives HERE, not in Django `_url()`.** `CtmsMediaUrlTransformer` glues a `/media`-carrying base onto the bare stored path — the SCP-14564 fix site. A wrong `SYNCER_MEDIA_BASE_URL` breaks every CTMS order/loadboard attachment link fleet-wide.
- **Direct-PG reader of 7 services (shadow caller).** No API contract enforces compatibility: a column rename in `posting-backend`, `metadata`, `trip-planner`, `loadboard-backend` (lbv3), `saved-search`, or `location-history` silently breaks the resync SQL in `resources/files/sql/`.
- **faster_payment resync null trap (SCP-15098 area).** SCP-15098 added faster-payment postings index sync (`CtmsFasterPaymentConfigurationEntityReadDto`, `fasterPaymentEnabled` in the posting/order converters). The event path is correct, but the loads-index **resync** SQL reads the raw always-null platform column, so a resync can null `faster_payment_enabled` on all orders — see `faster_payment_resync_null_trap` memory.
- **`keyword-properties-ignore-above-chars=250`** — long text is truncated for `keyword` indexing; exact-match search on long strings misses.
- **Redis `max-pool-waiting=10000`** — extreme; right-size after observing wait metrics.
- **No outbox on the failure-notification publish** — if Pub/Sub is down when indexing fails, the operator is silently uninformed.

## Relevant ADRs / docs
- `~/projects/codebase-map/relations/media-url-flows.md` — syncer owns hop 3 (base-URL glue); SCP-14564.
- `~/projects/codebase-map/repos/cube.md` — read side that queries the indexes syncer writes (cube does NOT write the orders index).
- `~/projects/codebase-map/repos/saved-search-handler.md` — owns percolate queries; syncer maintains the percolate index.
- `~/projects/codebase-map/relations/data-stores.md` — shadow-caller pattern.
- `~/projects/codebase-map/domains/integrations.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `BulkContext` | dto | `services` | BulkContext |
| `CtmsActivityLogDocumentDto` | dto | `api-dtos` | CtmsActivityLogDocument |
| `CtmsActivityLogEntityReadDto` | dto | `services` | CtmsActivityLog |
| `CtmsAttachmentDocumentDto` | dto | `api-dtos` | CtmsAttachmentDocument |
| `CtmsAttachmentEntityReadDto` | dto | `services` | [Attachment](../domains/entities/Attachment.md) |
| `CtmsCompanyInfoDocumentDto` | dto | `api-dtos` | CtmsCompanyInfoDocument |
| `CtmsCompanyInfoEntityReadDto` | dto | `services` | CtmsCompanyInfo |
| `CtmsCustomFieldsDocumentDto` | dto | `api-dtos` | CtmsCustomFieldsDocument |
| `CtmsDamageEntryDocumentDto` | dto | `api-dtos` | CtmsDamageEntryDocument |
| `CtmsDamageEntryEntityReadDto` | dto | `services` | CtmsDamageEntry |
| `CtmsExtraObjectDocumentDto` | dto | `api-dtos` | CtmsExtraObjectDocument |
| `CtmsExtraObjectEntityReadDto` | dto | `services` | CtmsExtraObject |
| `CtmsFasterPaymentConfigurationDocumentDto` | dto | `api-dtos` | CtmsFasterPaymentConfigurationDocument |
| `CtmsFasterPaymentConfigurationEntityReadDto` | dto | `services` | CtmsFasterPaymentConfiguration |
| `CtmsGeoPointEntityReadDto` | dto | `services` | CtmsGeoPoint |
| `CtmsImageDocumentDto` | dto | `api-dtos` | CtmsImageDocument |
| `CtmsImageEntityReadDto` | dto | `services` | CtmsImage |
| `CtmsInspectionConfigurationCustomPhotoDto` | dto | `api-dtos` | CtmsInspectionConfigurationCustomPhoto |
| `CtmsInspectionConfigurationCustomPhotoEntityReadDto` | dto | `services` | CtmsInspectionConfigurationCustomPhoto |
| `CtmsInspectionConfigurationDocumentDto` | dto | `api-dtos` | CtmsInspectionConfigurationDocument |
| `CtmsInspectionConfigurationEntityReadDto` | dto | `services` | CtmsInspectionConfiguration |
| `CtmsLoadEntityReadDto` | dto | `services` | CtmsLoad |
| `CtmsM22DamageDocumentDto` | dto | `api-dtos` | CtmsM22DamageDocument |
| `CtmsNegotiationDocumentDto` | dto | `api-dtos` | CtmsNegotiationDocument |
| `CtmsNegotiationEntityReadDto` | dto | `services` | [Negotiation](../domains/entities/Negotiation.md) |
| `CtmsOfferActivityLogDocumentDto` | dto | `api-dtos` | CtmsOfferActivityLogDocument |
| `CtmsOfferActivityLogEntityReadDto` | dto | `services` | CtmsOfferActivityLog |
| `CtmsOfferDetailsDocumentDto` | dto | `api-dtos` | CtmsOfferDetailsDocument |
| `CtmsOfferDetailsEntityReadDto` | dto | `services` | CtmsOfferDetails |
| `CtmsOfferDocumentDto` | dto | `api-dtos` | CtmsOfferDocument |
| `CtmsOfferEntityReadDto` | dto | `services` | CtmsOffer |
| `CtmsOrderDocumentDto` | dto | `api-dtos` | CtmsOrderDocument |
| `CtmsPostingDocumentDto` | dto | `api-dtos` | CtmsPostingDocument |
| `CtmsPostingEntityReadDto` | dto | `services` | [Posting](../domains/entities/Posting.md) |
| `CtmsPostingVehicleDocumentDto` | dto | `api-dtos` | CtmsPostingVehicleDocument |
| `CtmsPostingVehicleEntityReadDto` | dto | `services` | CtmsPostingVehicle |
| `CtmsSpecificationDocumentDto` | dto | `api-dtos` | CtmsSpecificationDocument |
| `CtmsSpecificationEntityReadDto` | dto | `services` | CtmsSpecification |
| `CtmsSpecificationsDocumentDto` | dto | `api-dtos` | CtmsSpecificationsDocument |
| `CtmsSpecificationsEntityReadDto` | dto | `services` | CtmsSpecifications |
| `CtmsTripDocumentDto` | dto | `api-dtos` | CtmsTripDocument |
| `CtmsTripEntityReadDto` | dto | `services` | CtmsTrip |
| `CtmsVehicleDocumentDto` | dto | `api-dtos` | CtmsVehicleDocument |
| `CtmsVehicleEntityReadDto` | dto | `services` | [Vehicle](../domains/entities/Vehicle.md) |
| `CtmsVehicleM22DamagesEntityReadDto` | dto | `services` | CtmsVehicleM22Damages |
| `IndexConfiguration` | dto | `api-dtos` | IndexConfiguration |
| `IndexSettings` | dto | `api-dtos` | IndexSettings |
| `LoadLocationLogDocumentDto` | dto | `services` | LoadLocationLogDocument |
| `LoadboardV3NegotiationEntityRead` | dto | `services` | LoadboardV3NegotiationEntityRead |
| `LoadboardV3PostingEntityRead` | dto | `services` | LoadboardV3PostingEntityRead |
| `MetadataEntityReadDto` | dto | `services` | Metadata |
| `MetadataMessageObjectDto` | dto | `api-dtos` | MetadataMessageObject |
| `RedisNotificationDto` | dto | `api-dtos` | RedisNotification |
| `ResyncRequestDto` | dto | `api-dtos` | Resync |
| `SavedSearchDto` | dto | `api-dtos` | [SavedSearch](../domains/entities/SavedSearch.md) |
| `SavedSearchReadDto` | dto | `api-dtos` | [SavedSearch](../domains/entities/SavedSearch.md) |
| `SyncerStateDto` | dto | `api-dtos` | SyncerState |
| `TripEntityReadDto` | dto | `services` | [Trip](../domains/entities/Trip.md) |
| `TripLoadEntityReadDto` | dto | `services` | TripLoad |
| `V3PubSubObjectDto` | dto | `api-dtos` | PubSubObject |
| `WebSocketDataDto` | dto | `api-dtos` | WebSocketData |
| `WebSocketDto` | dto | `api-dtos` | WebSocket |
<!-- entities-end -->
