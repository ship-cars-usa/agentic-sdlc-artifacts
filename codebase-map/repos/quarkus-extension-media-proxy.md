---
repo: quarkus-extension-media-proxy
path: ~/projects/ship-cars-usa/quarkus-extension-media-proxy
stack: Java multi-module — Quarkus extension (`ship.cars.quarkus.extensions.mediaproxy:quarkus-mediaproxy-client` 3.27.5, on shipcars-quarkus-bom / Quarkus 3.27.5) + sibling Spring client + shared DTOs
domain: platform
shape: multi-module (api-dtos + api-enums + commons + deployment + runtime + spring-client + coverage-report)
last-synced-commit: d9094bf782da297050f61d1ead90a047c1bf9ecd
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# quarkus-extension-media-proxy

## What it is
The fleet's **client library for the Go `media-proxy` service** — and one of the few cross-stack libraries that ships **both a Quarkus extension and a Spring client** out of the same multi-module repo. Same wire types (`MediaProxyKeyRequestDto`, `MediaProxyKeyResponseDto`, `MediaProxyKeyInfoDto`, `MediaProxyKeyMetaDto`, `MediaProxyKeyTypeEnum`), same operations, different DI shape:

- **Quarkus side** — inject `MediaProxyClient` (interface) via CDI; backed by `MediaProxyClientImpl` which delegates to a `MediaProxyRestClient` (`@RegisterRestClient(configKey = "media-proxy")`).
- **Spring side** — `spring-client/` module provides a Spring-friendly client bean for the Spring services (`chat-backend`, `inventory-backend`, `loadbuilder-backend`, `posting-backend`, `driveaway-backend`, `public-tracking-backend`, `user-backend`).

API surface (per README + runtime source):

- **`requestKey(...)`** — request a time-limited access key for a set of media-resource scope URLs. Three overloads (simple, with-metadata, full-request-object).
- **`revokeKey(...)`** — revoke an issued key.
- **`getKeyInfo(...)`** — fetch metadata about an active key.
- **`convertToInternalDownloadURI(...)`** — translate an external media URI to an internal one for backend-to-backend transfers.

The companion service `media-proxy` (Go, seeded earlier) generates and validates these keys, sits in front of GCS, and serves the actual bytes.

## How it fits

- **Compile-time consumers (13 fleet repos, verified 2026-08-28):**
  - **Quarkus (depend on `runtime`, inject `...mediaproxy.runtime.MediaProxyClient`):** `cube`, `integration-executor`, `integrations-backend`, `invoices`, `loadboard-backend`, `pusher`.
  - **Spring (depend on `spring-client`, autowire `cars.ship.mediaproxy.spring.client.MediaProxyClient`):** `chat-backend` (service-name `lm-chat`), `driveaway-backend`, `inventory-backend`, `loadbuilder-backend`, `posting-backend` (`lm-posting`), `public-tracking-backend` (`lm-public-tracking`), `user-backend`.
  - Confirms the cross-stack split — one repo, two client implementations.
- **Consumes API of:** the `media-proxy` service (`quarkus.rest-client.media-proxy.url` for Quarkus; `config.mediaproxy.client.base-uri` for Spring).
- **Publishes events to:** none.
- **Owns data store:** none.

## Build / test / run
```
./mvnw clean install -DskipTests
./mvnw test
./build-project.sh
./deploy-project.sh
```

Quarkus consumer:
```xml
<dependency>
  <groupId>ship.cars.quarkus.extensions.mediaproxy</groupId>
  <artifactId>runtime</artifactId>
  <version>${shipcars-quarkus-extensions-mediaproxy.version}</version>
</dependency>
```

Spring consumer:
```xml
<dependency>
  <groupId>ship.cars.quarkus.extensions.mediaproxy</groupId>
  <artifactId>spring-client</artifactId>
  <version>${shipcars-quarkus-extensions-mediaproxy.version}</version>
</dependency>
```

## Configuration

**Quarkus** (standard MP REST-client keys, configKey `media-proxy`, plus one `config.mediaproxy.client.*` key the impl reads via `@ConfigProperty`):

```properties
quarkus.rest-client.media-proxy.url=https://your-media-proxy-service.com   # required
config.mediaproxy.client.service-name=my-service                          # required (asserted non-empty in @PostConstruct)
# README documents these defaults but the extension ships NO application.properties setting them:
quarkus.rest-client.media-proxy.connect-timeout=5000
quarkus.rest-client.media-proxy.read-timeout=10000
```

**Spring** (`@ConfigurationProperties(prefix = "config.mediaproxy.client")`):

```properties
config.mediaproxy.client.enabled=true          # default true (matchIfMissing)
config.mediaproxy.client.base-uri=...          # required
config.mediaproxy.client.service-name=...       # required
config.mediaproxy.client.log-level=INFO        # default INFO
```

No credentials/bucket config exists in the client at all — only a plaintext `X-Service` header identifies the caller. Base URLs are env-injected fleet-wide (`MEDIA_PROXY_SERVICE_URL` / `CONFIG_MEDIA_PROXY_BASE_URI`). Note the Quarkus split: the URL lives under `quarkus.rest-client.media-proxy.*` while `service-name` lives under the unrelated `config.mediaproxy.client.*` namespace — easy to misconfigure.

## Key abstractions

- **`api-dtos/`** — `MediaProxyKeyRequestDto`, `MediaProxyKeyResponseDto`, `MediaProxyKeyInfoDto`, `MediaProxyKeyMetaDto` — the wire-format types shared between Quarkus + Spring clients.
- **`api-enums/`** — `MediaProxyKeyTypeEnum` (e.g. `PER_SCOPE` per the README example).
- **`commons/`** — shared utilities used by both Quarkus and Spring clients.
- **`runtime/.../MediaProxyClient.java`** — Quarkus-side interface (the public API).
- **`runtime/.../impl/MediaProxyClientImpl.java`** — Quarkus impl that delegates to the REST client.
- **`runtime/.../impl/MediaProxyRestClient.java`** — `@RegisterRestClient(configKey = "media-proxy")` interface; JAX-RS-annotated methods.
- **`runtime/.../MediaProxyUtils.java`** — URI / metadata helpers.
- **`spring-client/`** — parallel Spring client implementation.

## Don't-do-here / gotchas

- **Cross-stack contract.** Every change to `api-dtos` or `api-enums` ripples through **both** Quarkus and Spring consumers (13 services). Version-bump churn is large; coordinate breaking changes carefully.
- **Retry-without-timeout anti-pattern is present in the Quarkus REST client.** `MediaProxyRestClient` annotates all three methods with `@Retry(delayUnit=SECONDS, delay=1, maxRetries=7)` + `@ExponentialBackoff` + `@RetryWhen`. The extension ships **no** `application.properties`, so no timeouts are baked in — only the README documents 5000/10000 ms. Across the fleet **only `integration-executor`** actually sets timeouts (`connect-timeout=30000`, `read-timeout=60000`); every other Quarkus consumer relies on defaults. 60 s read-timeout × up to 7 retries is exactly the stack that hangs a caller — this is a live instance of the fleet retry-without-timeout anti-pattern (see `~/projects/quarkus-rest-client-timeout-anti-pattern.md`). The **Spring** impl has NO retry logic (relies on per-call `WebClientCallConfig`).
- **Silent failure fallback on the map overloads.** `requestKey(urls, ttl, ...)` (both runtime and Spring) catches all exceptions, logs, and **returns the original *unsigned* URLs** (`toMap(url->url, url->url)`). Callers can unknowingly serve un-keyed media when the proxy is down. The typed `requestKey`/`revokeKey`/`getKeyInfo` methods instead rethrow as `BusinessRuleException`.
- **`PER_SCOPE` vs other key types** — the enum gives multiple key-issuance semantics; pick the right one for the workload. Misuse (e.g. issuing a global key when scope-restricted would do) widens the blast radius of a key leak.
- **`convertToInternalDownloadURI` is the in-cluster path.** It bypasses the public CDN-fronted URL and goes directly to media-proxy via cluster DNS. Use it for backend-to-backend transfers; never expose the internal URI to clients.
- **`MediaProxyKeyMetaDto.properties` is `Map<String, String>`** (arbitrary key-value pairs). Don't put PII in there — the metadata is logged by `media-proxy` for audit.
- **TTL units differ across overloads** — `Duration` in some signatures, `int ttlSeconds` in `MediaProxyKeyRequestDto`. Don't confuse them.
- **Quarkus + Spring versions are coordinated.** Both clients in this repo share the same version (`3.27.0.2-SNAPSHOT` at HEAD). A version bump must update both consumers' `<dependencyManagement>` blocks. Spring services often pin to older versions (see `relations/quarkus-version-matrix.md` — fleet drift applies here too).

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/media-proxy.md` — the Go server this extension fronts.
- `~/projects/codebase-map/repos/attachment-backend.md` — primary consumer (most fleet media goes through both).
- `~/projects/codebase-map/relations/rest-client-registry.md` — context for why explicit timeouts in this extension's config matter.
- `~/projects/codebase-map/relations/service-graph.md` — compile-time-edges row.
- `~/projects/codebase-map/domains/platform.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `MediaProxyClientConfig` | dto | `spring-client` | MediaProxyClientConfig |
| `MediaProxyKeyInfoDto` | dto | `api-dtos` | MediaProxyKeyInfo |
| `MediaProxyKeyMetaDto` | dto | `api-dtos` | MediaProxyKeyMeta |
| `MediaProxyKeyRequestDto` | dto | `api-dtos` | MediaProxyKey |
| `MediaProxyKeyResponseDto` | dto | `api-dtos` | MediaProxyKey |
<!-- entities-end -->
