---
repo: crm-workflows
path: ~/projects/ship-cars-usa/crm-workflows
stack: Java/Quarkus 3.27.5 (Java 21, Maven multi-module)
domain: platform
shape: multi-module
last-synced-commit: 8c307ca35354084045be3f230a8b48dee37c6dd9
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# crm-workflows

## What it is
**CRM Workflows** — Quarkus 3.27.5 / Java 21 service that **synchronizes Ship.Cars data into the Freshsales CRM**. It is Pub/Sub-consume + HTTP-push: it consumes four internal event streams (company, user, load-leg, CTMS subscription), persists a thin `CompanyEntity` sync-tracking row locally, and pushes accounts / contacts / marketing-events to Freshsales, writing back an `external_crm_id` and a `CrmSyncStatus`. Port **7123**. Templated from `quarkus-imperative-boilerplate` (10 poms: root + `application`, `api-dtos`, `services`, `db-entities`, `db-migration`, `commons`, `crm-workflows-enums`, `configuration`, `resources`).

## How it fits
- **Consumes API of (REST out):**
  - **Freshsales** — `SalesAccountsClient` + `SalesContactsClient` (both `@Path("/api")` → `freshsales.sales-url`) and `SalesEventClient` (→ `freshsales.events-url`). Auth header `Authorization: Token token=<apiKey>` built in `commons/.../config/FreshSalesClientHeader.java`.
  - `user-backend` — `UserManagementClient` (→ `crm.workflows.user.api-url`, e.g. `.../internal/v2/users`) for user lookup.
- **Subscribes to (Pub/Sub consumers, `PubSubConsumerBlocking<T>`):** JSON DTOs, no schema registry —
  - `crm.workflows.pubsub.company-subscription` — `CompanyPubSubListener` → `CompanyEventProcessorService`.
  - `crm.workflows.pubsub.user-subscription` — `UserPubSubListener` → `UserEventProcessorService`.
  - `crm.workflows.pubsub.load-leg-subscription` — `LoadLegPubSubListener` → `LoadLegEventProcessorService` (emits Freshsales marketing events, prefix `"LM Load "`).
  - `crm.workflows.pubsub.ctms-company-subscription` — `CompanySubscriptionPubSubListener` → `CompanySubscriptionProcessorService`.
- **Publishes events to:** **none** — consume-only for Pub/Sub; the only outbound is HTTP to Freshsales.
- **Owns data store:** two PostgreSQL datasources — **default** (`CRM_WORKFLOWS_POSTGRESQL_URI`, owns the `companies` sync-tracking table) and a read-only **`ctms`** datasource (`CRM_WORKFLOWS_CTMS_POSTGRESQL_URI`) for the CTMS company batch sync. Both pools `max-size=16`. **Redis** (`redis://...:8033`) for company-cache. Flyway owns schema (`schema-management.strategy=none`).

## Build / test / run
```
./utils/docker-compose/rebuild.sh   # Pub/Sub emulator + Redis (:8033)
./start-quarkus-dev.sh              # dev; app on :7123, Swagger at /swagger
./build-dev.sh                      # JVM build + tests
./mvnw clean install -Pnative      # native build
```

## Key abstractions
- `CompanyEntity` — `db-entities/src/main/java/cars/ship/crm/workflows/entities/CompanyEntity.java` — the only `@Entity` (`@Table(name="companies")`, extends `BaseDbEntity`); tracks CRM sync state (`externalCrmId`, `crmSyncStatus`, subscription/trial fields).
- `CompanySyncService` — `services/.../services/sync/CompanySyncService.java` — `syncCompanyToCrmAndUpdateStatus(company)`: pushes a company to a Freshsales sales_account and sets `CrmSyncStatus`.
- `CtmsCompanySyncService` — reads companies from the CTMS datasource in offset pages, persists locally, syncs one-by-one; triggered by `POST /private/sync/ctms`.
- `CompaniesSyncScheduledService` — `@Scheduled(cron=${crm.workflows.config.company-sync-cron-expression})`, retries `PENDING`/`FAILED` rows.
- `*EventProcessorService` (`Company`, `User`, `LoadLeg`, `CompanySubscription`) — one per Pub/Sub stream; translate events into Freshsales account/contact/event calls.
- `SalesAccountServiceImpl` / `SalesContactServiceImpl` / `SalesEventServiceImpl` — wrap the Freshsales REST clients (lookup/create/update).
- `CompanyService` — `@Transactional` JPA persistence + status transitions (`updateSuccessfulSyncedStatus`, `updateFailedSyncStatus`, `findCompaniesBySyncedStatus`).
- `services/.../services/cache/` (`RedisCacheServiceImpl`, `RedisKeyGeneratorService`) + `CompanyCacheRetrieverService` — Redis company caching.
- `DbSyncController` — `resources/.../rest/DbSyncController.java` — `@Path("/private/sync")`, `POST /ctms`.
- `EventController` — `resources/.../rest/EventController.java` — `@Path("/email")`, `POST /{email}/event/{event}`.
- `crm-workflows-enums` module — `CompanyType {SHIPPER, CARRIER, API_INTEGRATOR}`, `CrmSyncStatus {SYNCED, PENDING, FAILED}`.

## Don't-do-here / gotchas
- **CORRECTION vs. prior shadow — event sources are known, not "likely posting/user".** It subscribes to company, user, load-leg, and CTMS-subscription streams (see How it fits); it does NOT consume posting-backend loads/quotes directly.
- **No REST resilience whatsoever.** All four `@RegisterRestClient` interfaces have **no `@Timeout`, `@Retry`, `@CircuitBreaker`, `@Fallback`**, and no `connect-timeout`/`read-timeout` properties. The retry-without-timeout question is moot — there is neither. A slow/unreachable Freshsales hangs the calling thread with no bound. `SalesAccountsClient`/`SalesContactsClient` only map non-200 to a `RuntimeException` via `@ClientExceptionMapper`. Consider adding at least connect/read timeouts.
- **CORRECTION — there is no rate-limiter.** Prior shadow assumed a Freshsales rate-limit strategy; grep finds none (Redis is a cache, not a limiter). A bulk/scheduled sync can blow the Freshsales per-account budget — validate before large re-syncs.
- **Silent-sync-failure risk.** A failed Freshsales push sets `CrmSyncStatus=FAILED` and relies on the scheduled retry; there is no alerting on stuck `FAILED` rows — stale CRM is possible if the retry keeps failing.
- **Two datasources** — the `ctms` datasource is a read source for the batch sync; don't write to it. The default datasource owns only sync-tracking state; the source of truth for company data is Freshsales + CTMS, not this DB.
- **`models-lib`/posting-DTO version coupling** — DTOs deserialized from Pub/Sub track shared model versions; coordinate `models-lib` bumps.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/quarkus-imperative-boilerplate.md` — the template.
- `~/projects/codebase-map/repos/user-backend.md` — `UserManagementClient` upstream + likely event source.
- `~/projects/codebase-map/relations/service-graph.md` — Pub/Sub-subscription edges.
- `~/projects/codebase-map/domains/platform.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `CompanyEntity` | jpa | `db-entities` | [Company](../domains/entities/Company.md) |
| `AccountDto` | dto | `api-dtos` | [User](../domains/entities/User.md) |
| `AccountResponseDto` | dto | `api-dtos` | [User](../domains/entities/User.md) |
| `Company` | dto | `services` | [Company](../domains/entities/Company.md) |
| `CompanyMessageDto` | dto | `api-dtos` | CompanyMessage |
| `CrmAccount` | dto | `services` | CrmAccount |
| `CrmAccountCustomFieldDto` | dto | `api-dtos` | CrmAccountCustomField |
| `CrmAccountCustomFieldResponseDto` | dto | `api-dtos` | CrmAccountCustomField |
| `CrmAccountDto` | dto | `api-dtos` | CrmAccount |
| `CrmAccountFilterResponseDto` | dto | `api-dtos` | CrmAccountFilter |
| `CrmAccountResponseDto` | dto | `api-dtos` | CrmAccount |
| `CrmCompanyCacheDto` | dto | `api-dtos` | CrmCompanyCache |
| `CrmContactDto` | dto | `api-dtos` | CrmContact |
| `CrmContactFilterResponseDto` | dto | `api-dtos` | CrmContactFilter |
| `CrmEventRequestDto` | dto | `api-dtos` | CrmEvent |
| `CrmEventResponseDto` | dto | `api-dtos` | CrmEvent |
| `CrmFilterRequestDto` | dto | `api-dtos` | CrmFilter |
| `CrmUserBaseInfoDto` | dto | `api-dtos` | CrmUserBaseInfo |
| `CtmsCompanyInfo` | dto | `api-dtos` | CtmsCompanyInfo |
| `CtmsSubscriptionEventDto` | dto | `api-dtos` | CtmsSubscription |
| `CtmsSubscriptionMessageDto` | dto | `api-dtos` | CtmsSubscriptionMessage |
| `UserMessageDto` | dto | `api-dtos` | UserMessage |
<!-- entities-end -->
