# REST-Client Registry

Auto-generated 2026-05-08 by scanning every Java file under `~/projects/ship-cars-usa/` for `@RegisterRestClient` and matching its `configKey` against `quarkus.rest-client.<key>.url` in any `application*.properties` profile. Spring services (`WebClient`-based) are NOT included here because they don't use `@RegisterRestClient`.

**Counts:** 36 Quarkus REST clients across 15 repos.

## Per-repo registry

### `aaag-integration`

| Interface | configKey | URL bindings | Timeouts |
|---|---|---|---|
| `AsiAuthClient` | `asi-auth` | `dev`: `http://localhost:8472`<br>`test`: `http://localhost:8472` | **none configured** |
| `AttachmentClient` | `attachment` | — | **none configured** |
| `InventoryClient` | `impersonator` | — | **none configured** |
| `PostingClient` | `impersonator` | — | **none configured** |
| `MetadataClient` | `metadata` | `dev`: `http://localhost:8471`<br>`test`: `http://localhost:8471` | **none configured** |
| `UserManagementClient` | `user-management` | `dev`: `http://localhost:7011`<br>`test`: `http://localhost:7011` | **none configured** |

### `axe-call-integration`

| Interface | configKey | URL bindings | Timeouts |
|---|---|---|---|
| `AxeApiClient` | `axe-api` | `default`: `https://agent.joinaxe.ai`<br>`test`: `http://localhost:${quarkus.wiremock.devservices.port}` | **none configured** |
| `AxeCampaignApiClient` | `axe-api` | `default`: `https://agent.joinaxe.ai`<br>`test`: `http://localhost:${quarkus.wiremock.devservices.port}` | **none configured** |
| `ImpersonatorServiceClient` | `impersonator-service` | `default`: `${IMPERSONATOR_SERVICE_BASE_URL}`<br>`test`: `http://localhost:${quarkus.wiremock.devservices.port}` | **none configured** |

### `bi-databricks-backend`

| Interface | configKey | URL bindings | Timeouts |
|---|---|---|---|
| `DatabricksRestClient` | `databricks-api` | `default`: `${DATABRICKS_WORKSPACE_URL}`<br>`test`: `http://localhost:${quarkus.wiremock.devservices.port}` | **none configured** |
| `UserManagementClient` | `user-management` | `default`: `${USER_MANAGEMENT_URL}`<br>`dev`: `${USER_MANAGEMENT_URL:http://localhost:8080}`<br>`test`: `http://localhost:${quarkus.wiremock.devservices.port}` | **none configured** |

### `command-executor`

| Interface | configKey | URL bindings | Timeouts |
|---|---|---|---|
| `ImpersonatorClient` | `impersonator` | `dev`: `http://localhost:7041`<br>`test`: `http://test.url` | **none configured** |

### `contract-pricing-backend`

| Interface | configKey | URL bindings | Timeouts |
|---|---|---|---|
| `ImpersonatorClient` | `impersonator` | `default`: `${CONFIG_IMPERSONATOR_BASE_URL}`<br>`test`: `http://test.url`<br>`dev`: `http://localhost:7014` | **none configured** |
| `UserManagementClient` | `user-management` | `default`: `${CONFIG_USERMANAGEMENT_INTERNAL_BASE_URL}`<br>`test`: `http://test.url`<br>`dev`: `http://localhost:7011` | **none configured** |

### `crm-workflows`

| Interface | configKey | URL bindings | Timeouts |
|---|---|---|---|
| `SalesAccountsClient` | `—` | — | **none configured** |
| `SalesContactsClient` | `—` | — | **none configured** |
| `SalesEventClient` | `—` | — | **none configured** |
| `UserManagementClient` | `—` | — | **none configured** |

### `fraud-detector`

| Interface | configKey | URL bindings | Timeouts |
|---|---|---|---|
| `SlackClient` | `slack-client` | `default`: `${FRAUD_DETECTOR_SLACK_URL}` | **none configured** |
| `VehicleClient` | `https://done.ship.cars` | baseUri=`https://done.ship.cars` | **none configured** |

### `integration-executor`

| Interface | configKey | URL bindings | Timeouts |
|---|---|---|---|
| `AttachmentClient` | `attachment` | `default`: `${CONFIG_ATTACHMENT_BASE_URL:http://localhost:8080}`<br>`dev`: `http://localhost:8671` | connect/default: 30000<br>read/default: 60000 |

### `invoices`

| Interface | configKey | URL bindings | Timeouts |
|---|---|---|---|
| `AttachmentClient` | `attachment` | `default`: `${CONFIG_ATTACHMENT_BASE_URL}`<br>`dev`: `http://localhost:8671`<br>`test`: `http://localhost:${quarkus.wiremock.devservices.port}` | **none configured** |
| `PostingClient` | `impersonator` | `default`: `${CONFIG_IMPERSONATOR_BASE_URL}`<br>`dev`: `http://localhost:7014`<br>`test`: `http://localhost:${quarkus.wiremock.devservices.port}` | **none configured** |
| `PaymentClient` | `payment` | `default`: `${CONFIG_PAYMENT_BASE_URL}`<br>`dev`: `http://localhost:9571`<br>`test`: `http://localhost:${quarkus.wiremock.devservices.port}` | **none configured** |
| `UserManagementClient` | `user-management` | `default`: `${CONFIG_USERMANAGEMENT_INTERNAL_BASE_URL}`<br>`dev`: `http://localhost:7011`<br>`test`: `http://localhost:${quarkus.wiremock.devservices.port}` | **none configured** |

### `negotiations-router`

| Interface | configKey | URL bindings | Timeouts |
|---|---|---|---|
| `CtmsRestClient` | `ctms` | `default`: `${CTMS_BASE_URL}`<br>`test`: `http://localhost:8082` | **none configured** |
| `LoadboardBackendRestClient` | `loadboard-backend` | `default`: `${CONFIG_LOADBOARD_BACKEND_URL}`<br>`test`: `http://localhost:8082` | **none configured** |

### `payment-backend`

| Interface | configKey | URL bindings | Timeouts |
|---|---|---|---|
| `RoadSyncClient` | `roadsync-api` | `default`: `${CONFIG_ROADSYNC_API_BASE_URL:https://test.api.roadsync.app}`<br>`dev`: `https://test.api.roadsync.app`<br>`test`: `http://localhost:${quarkus.wiremock.devservices.port}` | **none configured** |
| `UserManagementRestClient` | `user-management` | `default`: `${CONFIG_USERMANAGEMENT_INTERNAL_BASE_URL}`<br>`dev`: `http://localhost:7011`<br>`test`: `http://localhost:${quarkus.wiremock.devservices.port}` | **none configured** |

### `quarkus-extension-media-proxy`

| Interface | configKey | URL bindings | Timeouts |
|---|---|---|---|
| `MediaProxyRestClient` | `media-proxy` | `default`: `http://localhost:8081`<br>`test`: `http://localhost:${quarkus.wiremock.devservices.port}`<br>`default`: `http://localhost:8080` | connect/default: 5000<br>read/default: 10000<br>connect/test: 2000<br>read/test: 3000 |

### `quarkus-locationprovider-client`

| Interface | configKey | URL bindings | Timeouts |
|---|---|---|---|
| `LocationProviderRestClient` | `location-provider` | `test`: `http://localhost:${quarkus.wiremock.devservices.port}` | **none configured** |

### `synclink-backend`

| Interface | configKey | URL bindings | Timeouts |
|---|---|---|---|
| `ImpersonatorServiceClient` | `impersonator-service` | — | **none configured** |

### `uship-quotes`

| Interface | configKey | URL bindings | Timeouts |
|---|---|---|---|
| `PricetronClientInt` | `pricetron` | — | **none configured** |
| `PricetronClientAuthInt` | `pricetronauth` | — | **none configured** |
| `RateEngineClientInt` | `rateengine` | — | **none configured** |
| `WebbotClient` | `webbot` | `default`: `${QUARKUS_REST_CLIENT_WEBBOT_URL:http://localhost:3000}` | read/default: 120000<br>connect/default: 10000 |

## Fleet-wide observations

- **3/36** Quarkus REST clients have at least one of `connect-timeout` / `read-timeout` configured for their `configKey`.
- **33/36** have **NEITHER** timeout configured anywhere — these are the ones at risk of the retry-without-timeout cascade documented at `~/projects/quarkus-rest-client-timeout-anti-pattern.md`.

Spring services use `spring-commons.WebClientImpl` instead — those timeouts are set programmatically at construction time and don't appear here. Audit each Spring service's `WebClientConfig` bean for actual values.

## How to use this

When inspecting a service's outbound dependencies:

1. Look up the repo in the per-repo table.
2. The `configKey` is what appears in code as `@RegisterRestClient(configKey = "X")`.
3. The URL bindings show which profile gets which URL. `default` is the base `application.properties`; `dev` / `prod` / etc. are profile overrides.
4. Anything reading `**none configured**` in the Timeouts column is exposed to the retry-without-timeout pattern if the service also has `@Retry` on the same client.

## Re-run

Inline script in `~/projects/codebase-map/PLAN.md`. Promote to `scripts/build_rest_client_registry.py` if regenerated regularly.
