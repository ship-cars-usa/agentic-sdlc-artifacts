---
repo: bi-databricks-backend
path: ~/projects/ship-cars-usa/bi-databricks-backend
stack: Java/Quarkus 3.27.5 (Java 21)
domain: analytics
shape: single-module
last-synced-commit: e3583d7f49ca82d6cb63c13e669ce7a1c1e18939
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# bi-databricks-backend

## What it is
Databricks OAuth-token + dashboard **embed-token broker** on Quarkus 3.27.5 / Java 21. Stores per-company Databricks service-principal credentials encrypted at rest (AES-256-GCM), runs the 3-legged Databricks OAuth flow (service-principal token → token-info → scoped embed token), and mints embed tokens for embedded dashboards. Also resolves company hierarchy (via `user-management`) to build a Base64-encoded global filter that scopes what a company sees. Port **7071** (test 9373). Single-module, native-buildable.

## How it fits
- **Consumes API of:**
  - External **Databricks** OAuth + Workspace API — `DatabricksRestClient` (configKey `databricks-api`, base `${DATABRICKS_WORKSPACE_URL}`).
  - `user-management` — `UserManagementClient` (configKey `user-management`) for company lookup / hierarchy (drives the global-filter scoping).
- **Publishes events to:** none. (Pub/Sub consumers disabled in test; no publisher/subscriber code exists — only residual config toggles.)
- **Subscribes to:** none.
- **Owns data store:** PostgreSQL db `bi_databricks_backend` (Agroal, dev `max-size=16`; no prod pool block in-repo). `company_config` + `company_dashboards` tables hold encrypted secrets; Hibernate Envers audit; Flyway migrations.

## Build / test / run
```
mvn clean package        # or ./mvnw
mvn test
mvn quarkus:dev          # app on :7071 (test :9373)
```

## Key abstractions
- `DashboardResource` — `src/main/java/cars/ship/databricks/resource/DashboardResource.java` — `@Path("/api/dashboards")`, `GET /{userId}/{companyId}` mints an embed token (sets `X-Frame-Options: SAMEORIGIN`, `X-Content-Type-Options: nosniff`).
- `CompanyConfigResource` — `resource/CompanyConfigResource.java` — `@Path("/internal/company-config")`, `GET /{companyId}`, `PUT /{companyId}` (create-or-update).
- `DatabricksOAuthService` — `service/DatabricksOAuthService.java` — orchestrates the 3-call OAuth → embed-token flow; resolves clientId/secret via `SecretResolverService` and validates args.
- `CompanyConfigService` — `service/CompanyConfigService.java` — CRUD for `CompanyConfig`; `createOrUpdate` runs in `QuarkusTransaction.requiringNew()`.
- `CompanyHierarchyService` — `service/CompanyHierarchyService.java` — calls `UserManagementClient`, determines parent-level access, builds the Base64 global filter.
- `AesGcmEncryptionService` — `service/crypto/AesGcmEncryptionService.java` — `AES/GCM/NoPadding`, 12-byte random IV (prepended), 128-bit tag, enforced 32-byte (256-bit) key. Wired to entity fields via `EncryptedStringConverter`.
- `SecretResolverService` — `service/secrets/SecretResolverService.java` — wraps commons `SecretResolver` over a JSON secrets file (`sm.secrets.file-path`).

## Don't-do-here / gotchas
- **The retry-without-timeout anti-pattern STILL LIVES here.** Both `DatabricksRestClient` (all 3 methods) and `UserManagementClient.getCompany` carry `@Retry(delay=1, unit=SECONDS, maxRetries=7)` + `@RetryWhen(IsRetryable.class)` + `@ExponentialBackoff` with **no `@Timeout`, no `@CircuitBreaker`**, and no `quarkus.rest-client.databricks-api.connect-timeout`/`read-timeout` (nor for `user-management`) — a grep for `timeout` in resources returns nothing. Worst case is 8 attempts hanging per request. Fix: add `connect-timeout`/`read-timeout` properties and a `@Timeout`. This service is the worked example in the fleet anti-pattern doc.
- **`DatabricksOAuthService.java:63-72` collapses all failures into one `BusinessRuleException`** — a single broad `catch (Exception)` wraps the whole 3-call flow, so 4xx, 5xx, and retry-exhaustion are indistinguishable to callers (a 503 looks like a 400). No status-code discrimination.
- **CORRECTION vs. prior shadow — the `UNIQUE(company_id)` race is fixed.** `CompanyConfig.java:43` now has `@Column(unique = true)` and migration `V2.0__add_databricks_company_config.sql:8` declares `company_id VARCHAR(128) NOT NULL UNIQUE`. The duplicate-row window no longer exists.
- **CORRECTION vs. prior shadow — clientSecret validation moved.** The null/empty check is NOT in `DashboardResource` (which passes `getClientSecret()` straight through at `:118-124`); it lives in `DatabricksOAuthService.java:43-44` (`isValidArgument(isNotEmpty(clientSecret), ...)`).
- **No prod pool sizing in-repo** — only `%dev.max-size=16`; Agroal (not HikariCP) is the pool.

## Relevant ADRs / docs
- `~/projects/quarkus-rest-client-timeout-anti-pattern.md` — this service is the worked example.
- `~/projects/quarkus-fleet-review-2026-05-07.md#3-bi-databricks-backend` — original review (note: the UNIQUE and clientSecret-validation findings there are now stale, see above).
- `~/projects/codebase-map/repos/user-backend.md` — `user-management` upstream.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `CompanyConfig` | jpa | `bi-databricks-backend` | [CompanyConfig](../domains/entities/CompanyConfig.md) |
| `CompanyDashboard` | jpa | `bi-databricks-backend` | CompanyDashboard |
| `CompanyConfigDto` | dto | `bi-databricks-backend` | [CompanyConfig](../domains/entities/CompanyConfig.md) |
| `CompanyDashboardConfigDto` | dto | `bi-databricks-backend` | CompanyDashboardConfig |
| `EmbedTokenResponseDto` | dto | `bi-databricks-backend` | EmbedToken |
| `GlobalFilterResult` | dto | `bi-databricks-backend` | GlobalFilterResult |
| `ServicePrincipalTokenDto` | dto | `bi-databricks-backend` | ServicePrincipalToken |
| `TokenInfoResponseDto` | dto | `bi-databricks-backend` | TokenInfo |
<!-- entities-end -->
