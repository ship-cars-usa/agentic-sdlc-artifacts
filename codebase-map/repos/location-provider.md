---
repo: location-provider
path: ~/projects/ship-cars-usa/location-provider
stack: Java/Quarkus 3.27.5
domain: operations
shape: multi-module (13 poms)
last-synced-commit: 9313d7a60e6fde3f1a8413632c3eaddc6474efe7
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# location-provider

## What it is
Quarkus 3.27.5 (Java 21, project `3.29.0-SNAPSHOT`) façade over Google Maps / GCP APIs (Geocoding, Directions, Places, ETA, Route Optimization). Caches results in Redis (ETA, route optimization) and Elasticsearch (geocoding, directions) with TTL-based expiry, and persists every route-distance calculation to a small PostgreSQL table (`route_distance`) as a historical feed for the ML team. **No async messaging** — every call is synchronous HTTP or an internal method call. Ships two in-repo consumer client libraries (`spring-client`, `location-client`); long-term location history lives in the separate `location-history-backend`.

## How it fits
- Consumes API of: **Google Maps** via `com.google.maps:google-maps-services` v2.2.0 (`pom.xml:96,608-610`) + `google-auth-library-oauth2-http` 1.50.0; **GCP Route Optimization API** called through the raw JDK `java.net.http.HttpClient` in `RouteOptimizationServiceImpl.java` (not a REST-client). Auth via `GCP_API_KEY` env (`application.properties:40`, Helm-managed). **No `@RegisterRestClient` clients anywhere** — nothing to time out on the outbound MP-RestClient side.
- Publishes events to: none (no `@Outgoing`/Kafka/Pub-Sub).
- Subscribes to: none.
- Owns data store: **PostgreSQL** (`route_distance` historical table; `application.properties:9` `jdbc.max-size=4` prod, `:104` `=16` dev; `schema-management.strategy=none`); **Redis** (ETA + route-optimization cache, `application.properties:71-93`); **Elasticsearch** (geocoding/directions cache, ES host configured externally).

## Build / test / run
```
./start-quarkus-dev.sh    # DEV with Elasticsearch + Kibana (README:25)
./build-dev.sh            # build + tests
./build-native.sh         # native compile
mvn clean verify
```

## Key abstractions
- `GeocodingServiceImpl` — `services/.../services/impl/GeocodingServiceImpl.java` — Redis-first lookup, GCP fallback on miss, result cached in Redis with a **30-day** TTL (`:43` `CACHE_EXPIRATION = SECONDS.convert(30, DAYS)`, applied `:103`) and in Elasticsearch.
- `RouteOptimizationServiceImpl` — `services/.../services/impl/RouteOptimizationServiceImpl.java` — GCP Route Optimization via raw `HttpClient` (`:103`); Redis-cached with `route-optimization.cache-ttl-seconds` (default 300s).
- `RedisCacheServiceImpl` / `EtaGeoCacheServiceImpl` — `services/.../cache/impl/` — Redis GET/SET + TTL; ETA cache keyed on proximity radius / max-age.
- `ESCacheServiceImpl` — `services/.../cache/impl/ESCacheServiceImpl.java` — Elasticsearch cache-index get/put/delete/deleteByPrefix.
- `GcpServiceProducer` — `services/.../config/` — singleton `GeoApiContext` (Google Maps client) built with the API key.
- REST resources — `resources/.../rest/` — `AppResource` (v1 `/app` admin: resync-city-state-zip, recreate/delete cache), `GeocodingResource` (v2 `/geocode`), `DirectionResource` (v2 `/directions`, also hosts `/geocode` and **`/eta`** — no standalone ETA resource), `PlaceResource` (v2 `/place`, autocomplete/states/nearby), `RouteOptimizationResource` (v2 `/route-optimization`), plus a `rest/deprecated/` set.
- `spring-client` / `location-client` — in-repo **consumer** stubs (Spring `@Service` `WebClientImpl` wrapper, and Quarkus `WebClientImpl`/`WebClientCallConfig` wrapper respectively) for other services to call this one.

## Don't-do-here / gotchas
- **Production datasource `max-size=4`** (`application.properties:9`; dev `=16` at `:104`) for the `route_distance` write path. `default-transaction-timeout=120s` (`:16`) is generous — confirm it isn't masking a real-time SLA violation on batch inserts.
- **No auth on REST endpoints** — no `@RolesAllowed`/`@Authenticated`/`@PermitAll`/SecurityScheme in `resources/src/main/java`; endpoints are effectively public unless protected at the gateway/network. Confirm this is private-network-only.
- **Google Maps / GCP clients have no explicit per-request timeout** in code — a slow GCP call cascades back onto the Quarkus REST handler thread (no request-scoped deadline visible; OTel traces to Datadog).
- **Cache stampede on geocoding miss** — Redis miss + slow ES read lets concurrent requests all hit GCP; no request coalescing.
- **API-key rotation** — `GCP_API_KEY` is env-injected, no rotation mechanism in code.
- **Boundary with `location-history-backend`** — the `route_distance` table here is a write feed for the ML team (`README:53-66`); long-term historical *reads* belong to `location-history-backend`, not here.

## Relevant ADRs / docs
- `README.md` — Architecture, DB schema, Spring + Quarkus client libraries.
- `configuration/src/main/resources/application.properties` — full config incl. dev/test profiles, ETA (3600s) / route-optimization (300s) cache TTLs, Redis/ES wiring.
- `~/projects/quarkus-fleet-review-2026-05-07.md#5-contract-pricing-backend` — caller-side `CompletableFuture.orTimeout` exception-unwrap bug masks a slow location-provider call.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `RouteDistanceEntity` | jpa | `db-entities` | RouteDistance |
| `AutocompletePlaceDto` | dto | `api-dtos` | AutocompletePlace |
| `BreakRuleDto` | dto | `api-dtos` | BreakRule |
| `CacheItemVo` | dto | `commons` | CacheItemVo |
| `DirectionRouteDistanceResponseDto` | dto | `api-dtos` | DirectionRouteDistance |
| `DirectionsResponseDto` | dto | `api-dtos` | Directions |
| `DirectionsResponseDto` | dto | `spring-client` | Directions |
| `DirectionsVo` | dto | `commons` | DirectionsVo |
| `DistanceLimitDto` | dto | `api-dtos` | DistanceLimit |
| `DurationLimitDto` | dto | `api-dtos` | DurationLimit |
| `ESCacheServiceImpl` | dto | `services` | ESCacheServiceImpl |
| `EncodedPolylineDto` | dto | `api-dtos` | EncodedPolyline |
| `EtaCacheEntryVo` | dto | `commons` | EtaCacheEntryVo |
| `EtaQueryDto` | dto | `api-dtos` | EtaQuery |
| `EtaResponseDto` | dto | `api-dtos` | Eta |
| `GeocodeDetailsResponseDto` | dto | `api-dtos` | GeocodeDetails |
| `GeocodeDetailsResponseDto` | dto | `spring-client` | GeocodeDetails |
| `GeocodeResponseDto` | dto | `api-dtos` | Geocode |
| `GeocodedRouteQueryDto` | dto | `api-dtos` | GeocodedRouteQuery |
| `GeocodingQueryDto` | dto | `api-dtos` | GeocodingQuery |
| `LatLngDto` | dto | `api-dtos` | LatLng |
| `LoadDto` | dto | `api-dtos` | [Load](../domains/entities/Load.md) |
| `LoadLimitDto` | dto | `api-dtos` | LoadLimit |
| `LocationDto` | dto | `api-dtos` | [Location](../domains/entities/Location.md) |
| `LocationInfoDto` | dto | `api-dtos` | LocationInfo |
| `LocationInfoDto` | dto | `spring-client` | LocationInfo |
| `LocationPointDto` | dto | `api-dtos` | LocationPoint |
| `LocationPointDto` | dto | `spring-client` | LocationPoint |
| `LocationProviderClientConfig` | dto | `spring-client` | LocationProviderClientConfig |
| `LocationQueryDto` | dto | `api-dtos` | LocationQuery |
| `LocationQueryDto` | dto | `spring-client` | LocationQuery |
| `NearbySearchQueryDto` | dto | `api-dtos` | NearbySearchQuery |
| `OptimizeToursRequestDto` | dto | `api-dtos` | OptimizeTours |
| `OptimizeToursResponseDto` | dto | `api-dtos` | OptimizeTours |
| `PlaceAutocompleteQueryDto` | dto | `api-dtos` | PlaceAutocompleteQuery |
| `PlaceLocationQueryDto` | dto | `api-dtos` | PlaceLocationQuery |
| `PlaceLocationQueryDto` | dto | `spring-client` | PlaceLocationQuery |
| `RedisCacheServiceImpl` | dto | `services` | RedisCacheServiceImpl |
| `RouteModifiersDto` | dto | `api-dtos` | RouteModifiers |
| `RouteQueryDto` | dto | `api-dtos` | RouteQuery |
| `RouteQueryDto` | dto | `spring-client` | RouteQuery |
| `ShipmentDto` | dto | `api-dtos` | [Load](../domains/entities/Load.md) |
| `ShipmentModelDto` | dto | `api-dtos` | [Load](../domains/entities/Load.md) |
| `ShipmentRouteDto` | dto | `api-dtos` | ShipmentRoute |
| `SkippedShipmentDto` | dto | `api-dtos` | SkippedShipment |
| `StateInfoDto` | dto | `api-dtos` | StateInfo |
| `TimeWindowDto` | dto | `api-dtos` | TimeWindow |
| `TransitionDto` | dto | `api-dtos` | Transition |
| `VehicleDto` | dto | `api-dtos` | [Vehicle](../domains/entities/Vehicle.md) |
| `VisitDto` | dto | `api-dtos` | Visit |
| `VisitRequestDto` | dto | `api-dtos` | Visit |
| `WaypointDto` | dto | `api-dtos` | Stop |
<!-- entities-end -->
