---
repo: negotiations-router
path: ~/projects/ship-cars-usa/negotiations-router
stack: Java/Quarkus 3.27.5, Java 21
domain: operations
shape: multi-module (parent + 7 modules)
last-synced-commit: b5f5ecf63ec221d47c60cf4a7c48651313236802
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# negotiations-router

## What it is
Quarkus 3.27.5 / Java 21 **stateless routing service** (package `cars.ship.negotiations`) between two backends: **CTMS** (legacy Django) and **`loadboard-backend` v3 (LBv3)**. It receives negotiation/posting operations, resolves who owns the posting via LBv3's internal owner API, and — gated by an Unleash toggle — routes each operation to CTMS or LBv3, translating responses into a CTMS-shaped contract so callers see one API. Zero local persistence, no Pub/Sub. Sits in the CTMS→LBv3 migration path and can be retired with CTMS. Recently refactored: ownership resolution extracted into a cached `PostingOwnerService`, routing generalized into a single `route()` method, and a new offer-review-status operation added. HTTP port 7071.

## How it fits
- Consumes API of:
  - `loadboard-backend` v3 via `@RegisterRestClient` configKey `loadboard-backend` (`quarkus.rest-client.loadboard-backend.url`) — offer/accept/cancel/claim/cancel-posting/review-status plus internal owner lookups (`getPostingOwner`, `getPostingOwnerByNegotiation`).
  - CTMS via `@RegisterRestClient` configKey `ctms` (`quarkus.rest-client.ctms.url`) — equivalent operations with an `Authorization` header.
  - Unleash for the routing toggle.
- Publishes events to: none.
- Subscribes to: none.
- Owns data store: **none** (stateless). Uses in-process Caffeine caches only (`posting-owner`, `negotiation-owner`).

## Build / test / run
```
./mvnw clean package -DskipTests
./mvnw quarkus:dev
# Modules: application, resources, services, api-dtos, commons, configuration, coverage-report
# Port: 7071 (quarkus.http.port)
```

## Key abstractions
- `RouterController` — `resources/.../rest/RouterController.java:32` — JAX-RS endpoints under `API_PATH`:
  - `POST /postings/{postingId}/offer` → `createOffer` (l.38)
  - `POST /negotiations/{negotiationId}/cancel` → `cancelNegotiation` (l.52)
  - `POST /negotiations/{negotiationId}/offers/{offerId}/accept` → `acceptNegotiation` (l.65)
  - `POST /negotiations/{negotiationId}/offers/{offerId}/review-status` → `setOfferReviewStatus` (l.78, **new**)
  - `POST /postings/{postingId}/claim` → `claimPosting` (l.95)
  - `POST /postings/{postingId}/cancel` → `cancelPosting` (l.109)
- `RouterService` — `services/.../impl/RouterService.java:22` — one generic `route(operation, resourceId, ownerResolver, ctmsFn, lbFn)` (l.124): if `featureToggle.isRoutingEnabled()` is false → CTMS; else resolve owner → `LOADBOARD_BACKEND` routes to LBv3, anything else (or a null owner, l.173) → CTMS default.
- `PostingOwnerService` — `services/.../impl/PostingOwnerService.java` (**new**) — `@CacheResult`-cached ownership lookups: `getPostingOwner` (cache `posting-owner`) and `getPostingOwnerByNegotiation` (cache `negotiation-owner`), each backed by `LoadboardBackendRestClient`; throws if no owner is returned.
- `FeatureToggleOperations` — `configuration/.../config/FeatureToggleOperations.java` — Unleash adapter; toggle `lbv2.negotiation-router.enable-loadboard-backend` (config key `config.unleash.toggles.route-offer-toggle`).
- `LoadboardBackendRestClient` / `CtmsRestClient` (+ `LoadboardBackendClient` / `CtmsClient` impls) — the two outbound clients.
- `NegotiationConverter` — `services/.../converters/NegotiationConverter.java:18` — maps LBv3 DTOs to CTMS-shaped read DTOs (`convertToCtmsNegotiationReadDto`, `convertToCtmsOfferReadDto`, `convertToLBv3NegotiationCancelDto`) so responses are contract-consistent across backends.

## Don't-do-here / gotchas
- **Ownership lookups are now cached (15-min TTL)** — corrected from the previous shadow's "cache them briefly" suggestion: `PostingOwnerService` uses Caffeine caches `posting-owner`/`negotiation-owner` (`expire-after-write=15M`, `maximum-size=5000`). Trade-off: an ownership change (posting migrated CTMS↔LBv3) can be routed to the wrong backend for up to 15 minutes. Consider invalidation on migration events if that window matters.
- **Still no `connect-timeout` / `read-timeout`** on the `ctms` or `loadboard-backend` rest clients (confirmed absent in `application.properties`) — inherits Quarkus defaults; no explicit retry/circuit-breaker.
- **No compensation across the two backends** — a toggle flip or ownership change mid-conversation can split an operation's steps across CTMS and LBv3. No transaction semantics.
- **Null-owner fallback is silent CTMS** (`RouterService.getPostingOwner`, l.173) — if the LBv3 owner lookup returns null it logs a warning and defaults to CTMS; a genuinely LBv3-owned posting could be misrouted if the lookup flakes.
- **Retirement tied to CTMS deprecation** — when CTMS is retired, switch callers to LBv3 directly and drop this service.

## Relevant ADRs / docs
- `docs/tech-project-overview.md` (in-repo) — current architecture overview.
- `~/projects/codebase-map/repos/loadboard-backend.md` — LBv3 backend and migration plan.
- `~/projects/codebase-map/repos/trip-planner.md` — also bridges CTMS via `CtmsClient`.
- `~/projects/codebase-map/relations/rest-client-registry.md` — fleet timeout audit.
- `~/projects/codebase-map/domains/operations.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `AcceptNegotiationDto` | dto | `api-dtos` | AcceptNegotiation |
| `CTMSCancelNegotiationDto` | dto | `api-dtos` | CTMSCancelNegotiation |
| `CTMSClaimPostingDto` | dto | `api-dtos` | CTMSClaimPosting |
| `CTMSCompanyInfoDto` | dto | `api-dtos` | CTMSCompanyInfo |
| `CTMSDateRangeDto` | dto | `api-dtos` | CTMSDateRange |
| `CTMSNegotiationReadDto` | dto | `api-dtos` | CTMSNegotiation |
| `CTMSOfferActivityLogDto` | dto | `api-dtos` | CTMSOfferActivityLog |
| `CTMSOfferDetailsDto` | dto | `api-dtos` | CTMSOfferDetails |
| `CTMSOfferReadDto` | dto | `api-dtos` | CTMSOffer |
| `CTMSOfferReviewStatusDto` | dto | `api-dtos` | CTMSOfferReviewStatus |
| `CreateOfferDto` | dto | `api-dtos` | CreateOffer |
| `OfferReviewStatusDto` | dto | `api-dtos` | OfferReviewStatus |
| `UpstreamPassThroughException` | dto | `commons` | UpstreamPassThroughException |
<!-- entities-end -->
