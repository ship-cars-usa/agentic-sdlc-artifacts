---
repo: metadata
path: ~/projects/ship-cars-usa/metadata
stack: Java/Quarkus 3.27.5
domain: platform
shape: multi-module (14 poms)
last-synced-commit: 42c5ac08620be3e5a7727b13d84549294761103c
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# metadata

## What it is
Quarkus 3.27.5 / Java 21 **central key-value store** for company- and system-scoped metadata: dropdown values, vehicle specs / types, rate-rule lookups, restriction flags, business-logic toggles. Used as the canonical config / lookup registry by `invoices`, `posting-backend`, `inventory-backend`, `loadboard-backend`, `quote-manager-backend`, `autoims-backend`, and `user-backend`. Publishes a change event to a GCP Pub/Sub topic on every create/update/delete so downstream caches can invalidate. Read-mostly, but the publish-on-write contract is what keeps it correct at scale. NOTE: stack was previously mis-recorded as Quarkus 3.20.2.2 — it is now on the 3.27.5 platform.

## How it fits
- Consumes API of: none (no `@RegisterRestClient` in main code).
- Publishes events to: GCP Pub/Sub `config.pubsub.metadata-topic` (`${PUBSUB_METADATA_TOPIC}`, `configuration/.../application.properties:47`) via `PubSubMessagePublisherImpl` (`PubSubPublisherSync`) on every metadata create/update/delete. Ordering key passed as a header (`PUBSUB_ORDERING_KEY`). **Direct publish, no outbox** (only logs on failure) — see Don't-do-here. JSON DTOs over Pub/Sub — no schema registry.
- Subscribes to: none observed.
- Owns data store: PostgreSQL (`metadata` db; `jdbc.max-size=16` in dev, prod pool via env), Panache, Flyway. Two tables via entities `MetadataEntity` (`metadata`) and `CompanyMetadataRestrictionEntity`.
- Ships an in-repo **`spring-client` module** (`MetadataClient` interface + `MetadataClientImpl` + `MetadataClientConfig`) — compile-time client used by Spring consumers; Quarkus consumers reuse the DTOs.

## Build / test / run
```
./mvnw clean package -DskipTests
./mvnw quarkus:dev
# 14 poms: root + application, api-quarkus, api-dtos, api-enums, services, configuration,
#          db-entities, db-migration, repositories, resources, commons, spring-client
```

## Key abstractions
- `CompanyMetadataResource` — `resources/.../rest/CompanyMetadataResource.java:45` — `/v1/companies/{companyId}/metadata` CRUD + paginated `search(page, size)`.
- `SystemMetadataResource` — `resources/.../rest/SystemMetadataResource.java:40` — `/v1/companies/{companyId}/system/metadata`, same shape at system scope.
- `CompanyMetadataRestrictionResource` — `resources/.../rest/CompanyMetadataRestrictionResource.java` — CRUD for per-company metadata restriction flags.
- `MetadataServiceImpl` — `services/.../services/impl/MetadataServiceImpl.java` — CRUD + filter/search orchestration.
- `PubSubMessagePublisherImpl` — `services/.../services/impl/PubSubMessagePublisherImpl.java:26` — change-event publish (blocking, ordering-key header).
- `MetadataConverter` / `CompanyMetadataRestrictionConverter` — `services/.../services/converters/` — DTO ↔ entity mapping.

## Entities
- `MetadataEntity` — `db-entities/.../entities/MetadataEntity.java` — `@Table("metadata")`; columns: `company_id` (NOT NULL), `entity_type` (enum `MetadataEntityTypeEnum`, `@Enumerated(STRING)`, NOT NULL — note the column is `entity_type`, not `entity_type_enum`), `entity_id` (NOT NULL), `type` (enum `MetadataTypeEnum`, STRING), `updatable` (boolean), `key` (NOT NULL), `value` (TEXT, nullable).
- `CompanyMetadataRestrictionEntity` — `db-entities/.../entities/CompanyMetadataRestrictionEntity.java` — per-company restriction rows.

## Don't-do-here / gotchas
- **No transactional outbox**: the Pub/Sub publish sits outside the JPA transaction and only logs on failure. A DB commit + publish failure leaves downstream caches stale with no retry — the canonical correctness gap for this registry. Add an outbox (as `posting-backend` does) or make the publish rollback-on-failure.
- **`spring-client` ships in this repo** — Spring consumers depend on `MetadataClient`; an API rename breaks every Spring downstream silently at the next dependency bump. Treat it as a stable public contract and bump major on a breaking change.
- **Search page-size cap unverified** — `CompanyMetadataResource.search` takes a raw `@QueryParam("size") int` handed to `PageDtoConverter.toPageable(page, size)` (`:101-103`); confirm the converter caps it, otherwise `?size=1000000` risks returning the whole table (assumed).
- **Hard deletes, no soft-delete/audit table** observed — correctness relies on consumers preserving the Pub/Sub event log; if audit is ever required, the topic must be retained.
- **Substring search on `value`** likely costs an `ILIKE '%...%'` scan — verify a `pg_trgm` GIN index exists before the `metadata` table grows large (assumed).
- **Per-tenant ordering key only** — global ordering across tenants is not guaranteed; downstream consumers must not assume cross-tenant order.

## Relevant ADRs / docs
- `~/projects/codebase-map/relations/service-graph.md` — inbound from `invoices`, `posting-backend`, `quote-manager-backend`, `autoims-backend`, `loadboard-backend`, `inventory-backend`, `user-backend`.
- `~/projects/codebase-map/domains/platform.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `CompanyMetadataRestrictionEntity` | jpa | `db-entities` | CompanyMetadataRestriction |
| `MetadataEntity` | jpa | `db-entities` | Metadata |
| `CompanyMetadataPubSubDataDto` | dto | `api-dtos` | CompanyMetadataPubSubData |
| `CompanyMetadataRestrictionDto` | dto | `api-dtos` | CompanyMetadataRestriction |
| `CompanyMetadataRestrictionPubSubDataDto` | dto | `api-dtos` | CompanyMetadataRestrictionPubSubData |
| `CreateCompanyMetadataRestrictionDto` | dto | `api-dtos` | CreateCompanyMetadataRestriction |
| `CreateCompanyMetadataRestrictionVo` | dto | `repositories` | CreateCompanyMetadataRestrictionVo |
| `CreateMetadataDto` | dto | `api-dtos` | CreateMetadata |
| `CreateMetadataVo` | dto | `repositories` | CreateMetadataVo |
| `DeleteMetadataByKeyVo` | dto | `repositories` | DeleteMetadataByKeyVo |
| `MetadataClientConfig` | dto | `spring-client` | MetadataClientConfig |
| `MetadataCreationResultVo` | dto | `services` | MetadataCreationResultVo |
| `MetadataDto` | dto | `api-dtos` | Metadata |
| `MetadataIdentityVo` | dto | `repositories` | MetadataIdentityVo |
| `MetadataSearchDto` | dto | `api-dtos` | MetadataSearch |
| `MetadataSearchVo` | dto | `repositories` | MetadataSearchVo |
| `PubSubMessageDto` | dto | `api-dtos` | PubSubMessage |
| `UpdateCompanyMetadataRestrictionDto` | dto | `api-dtos` | UpdateCompanyMetadataRestriction |
| `UpdateCompanyMetadataRestrictionResultVo` | dto | `services` | UpdateCompanyMetadataRestrictionResultVo |
| `UpdateCompanyMetadataRestrictionVo` | dto | `repositories` | UpdateCompanyMetadataRestrictionVo |
| `UpdateMetadataDto` | dto | `api-dtos` | UpdateMetadata |
| `UpdateMetadataKeyVo` | dto | `repositories` | UpdateMetadataKeyVo |
| `UpdateMetadataVo` | dto | `repositories` | UpdateMetadataVo |
<!-- entities-end -->
