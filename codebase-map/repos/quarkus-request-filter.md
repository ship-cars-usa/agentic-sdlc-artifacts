---
repo: quarkus-request-filter
path: ~/projects/ship-cars-usa/quarkus-request-filter
stack: Java 21 / Quarkus 3.27.5 extension (runtime + deployment) — `ship.cars.quarkus.extensions.request-filter` 3.27.5-2-SNAPSHOT
domain: platform
shape: multi-module (runtime + deployment + coverage-report)
last-synced-commit: bf74776e2b2baf8e60c222339a62d49563104a66
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# quarkus-request-filter

## What it is
The fleet's **per-request context-propagation + MDC + request/response logging + exception-mapping layer** for Quarkus services. Responsibilities:

1. **Context extraction.** On every inbound REST request (`RequestResponseFilters`, a pre-matching `@ServerRequestFilter`), it parses `context-company`/`context-user` from either the **API-Gateway context header** (`ContextDto` JSON) or **path parameters** (`/context-company/{id}/context-user/{id}/...`). The extracted user/company IDs land in the Jakarta `ContainerRequestContext` (via `RequestConstants` property keys) and in **SLF4J MDC** (`MDC_COMPANY_ID`/`MDC_USER_ID` from `commons.MdcKeys`), so every log line carries them. Path-param mode strips the context segments from the URL and rewrites the request URI so business resources see clean paths. User roles are pulled from the API-Gateway header when present.
2. **Request/response logging.** Logs each request (method, URI, user, client IP from `X-Forwarded-For`/`X-Real-IP`) at INFO, request body at DEBUG, and response bodies for 4xx (WARN) / 5xx (ERROR). Skips `/health`, `/metrics`, `/internal/`, `/q/`.
3. **Exception mapping.** `ExceptionMapper` (catch-all), `ConstraintViolationExceptionMapper` (+ `Reactive` variant), and `ClientResponseExceptionMapper` translate exceptions to fleet-canonical `ErrorDto` via `ErrorModelConvertor`.

Also bundles `ObjectMapperConfigCustomizer` + `ObjectSerializerProvider` for fleet-standard Jackson wiring. Optional `MdcPopulator` SPI (default `MdcPopulatorEmpty`) lets a service add extra MDC fields.

## How it fits
- **What it provides:** the MDC/context invariant and standardized error shape almost every Quarkus service depends on.
- **Who consumes it (compile-time):** ~34 fleet repos reference `ship.cars.quarkus.extensions.request-filter` — essentially every active Quarkus service.
- **Consumes API of:** none (server-side request handling).
- **Publishes events to:** none.
- **Owns data store:** none.

## Configuration

| Property | Env var | Default | Description |
|---|---|---|---|
| `ship.cars.request.filter.log-headers` | `SHIP_CARS_REQUEST_FILTER_LOG_HEADERS` | `true` | Whether request headers are logged at all. |
| `ship.cars.request.filter.redacted-header-fragments` | `SHIP_CARS_REQUEST_FILTER_REDACTED_HEADER_FRAGMENTS` | `password,passwd,pwd,passphrase,secret,token,credential,auth,key,cookie,session,signature,bearer,jwt,otp,cvv,card,ssn,username,clientid,email,phone` | Header-name fragments whose values are masked with `***REDACTED***`. Substring match, case-insensitive (so `secret` covers `Clientsecret`). **Setting this replaces the whole list.** |
| `ship.cars.request.filter.additional-redacted-header-fragments` | `SHIP_CARS_REQUEST_FILTER_ADDITIONAL_REDACTED_HEADER_FRAGMENTS` | *(empty)* | Extra fragments **merged with** the defaults — the safe way to add without dropping built-ins. |

## Key abstractions
- `RequestResponseFilters` — `runtime/.../filter/RequestResponseFilters.java` — the request + response filters; runs on every call. Load-bearing.
- `HeaderRedactor` — `runtime/.../filter/HeaderRedactor.java` — static utility masking sensitive header values before logging; merges default + additional fragments, substring/case-insensitive match, preserves header name and value count.
- `PathParser` / `PathParams` — `runtime/.../filter/` — recognize `/context-company/{id}/context-user/{id}` and split off the remaining path.
- `MdcPopulator` / `MdcPopulatorEmpty` — `runtime/.../filter/` — SPI to add extra per-request MDC fields (application-scoped; one impl per service).
- `RequestConstants` — `runtime/.../constants/RequestConstants.java` — canonical property keys + header names (`CONTEXT_HEADER_NAME`, `COMPANY_ID`, `USER_ID`, …). Use these, not literals.
- `ConstraintViolationExceptionMapper` / `ReactiveConstraintViolationExceptionMapper` / `ExceptionMapper` / `ClientResponseExceptionMapper` — `runtime/.../ctx|filter/` — exception → `ErrorDto`.
- `ErrorModelConvertor` — `runtime/.../ctx/ErrorModelConvertor.java` — shape converter (uses `commons.errors` extractor chain).
- `RequestFilterConfig` — `runtime/.../config/RequestFilterConfig.java` — `@ConfigMapping(prefix="ship.cars.request.filter")`.
- `ObjectMapperConfigCustomizer` / `ObjectSerializerProvider` — `runtime/.../config/` — Jackson wiring.
- `RequestFilterExtensionProcessor` — `deployment/.../RequestFilterExtensionProcessor.java`.

## Don't-do-here / gotchas
- **Sensitive request headers ARE redacted by default now** (corrects a prior sync). `RequestResponseFilters.logRequest` runs `HeaderRedactor.redact(...)` before logging, and the default fragment list covers `authorization` (via `auth`), `token`, `bearer`, `jwt`, `cookie`, `secret`/`Clientsecret`, `password`, `key`, plus PII (`email`, `phone`, `ssn`, `card`, `cvv`). So `Authorization`, `Clientsecret`, `Password` headers no longer leak into request logs at the default config. **Do not disable this by narrowing `redacted-header-fragments`** — use `additional-redacted-header-fragments` to extend it instead.
- **Redaction only covers HEADERS.** The request **body** is logged verbatim at DEBUG, and 4xx/5xx **response bodies** are serialized into logs — neither is passed through `HeaderRedactor`. A secret in a body/response still leaks if DEBUG is on or the endpoint errors. (This is the header-side complement to the fleet body-logging issue in `secrets_in_cloud_logging`.)
- **`pin` is deliberately NOT in the default list** — `shipping` contains it, so masking `pin` would redact every `X-Shipping-*` header on a car-shipping platform.
- **The MDC + `ContainerRequestContext` invariant is load-bearing fleet-wide.** A regression in `PathParser`/`RequestResponseFilters` (e.g. URL-segment stripping that fails for a new path pattern) makes incident logs across the fleet unattributable. Treat changes here as high-risk.
- **Path-segment stripping** removes `context-company/<id>/context-user/<id>` from the URI. A resource whose `@Path` uses those literal segments won't match — read the values from `ContainerRequestContext`, don't parse the URL.
- **One `MdcPopulator` per service** — the default `MdcPopulatorEmpty` is used when none is provided; don't register multiples.
- **Not a REST-client config layer** — this is server-side; the fleet REST-client timeout gap is unrelated to this extension.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/quarkus-commons.md` — partner extension carrying OTel/MDC utils + structured-JSON logging (`kv(...)` used here).
- `~/projects/codebase-map/repos/api-gateway.md` — produces the context header this extension consumes.
- memory: `secrets_in_cloud_logging` — body/response logging remains the residual secret-in-logs risk here.
- `~/projects/codebase-map/relations/service-graph.md`; `~/projects/codebase-map/domains/platform.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `PathParams` | dto | `runtime` | PathParams |
<!-- entities-end -->
