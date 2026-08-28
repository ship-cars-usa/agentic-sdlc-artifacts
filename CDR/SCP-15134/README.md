# [Montway][Faster Payments][Post Release] Loads eligible for Faster Pay in LoadScout Recommendations - CTMS

`SCP-15134` · **proposed** · 2026-08-28 · hristo.savov@ship.cars · groomed 2026-08-28

**Services:** `platform-frontend`, `load-recommender`, `cube`, `platform-backend`

**Legend:** 🟢 added · 🟡 updated · 🔴 removed · 🔵 reused

![Design diagram](./diagram.svg)

## Context

Show **Faster Pay Available** (label + info-icon tooltip with terms and fees), the **SmartHaul Payments** method, and the original **payment term** on the **CTMS LoadScout recommendation cards** — information only.

This is the LoadScout twin of the already-shipped **LoadBoard CTMS** feature (SCP-14956 / SCP-15059), with one decisive difference. The loadboard front-end reads postings **directly from cube**, which already carries the faster-pay flag (SCP-15099), so that work was front-end only. The LoadScout card instead renders a load object served by **load-recommender**, and that payload does **not** carry the flag — so this story needs **both back-end and front-end** work.

No new database table, Elasticsearch index, or Pub/Sub schema is introduced. The change is one additive DTO field on an existing REST + WebSocket contract, plus a client/read-model version bump so the value reaches load-recommender. Tooltip terms are reused as-is from platform-backend's Faster Payment configuration API, fetched by the front-end per shipper (they are not on the load payload).

## §4 · REST API & DTO (load-recommender)

*Field delta · LoadDto (embedded in LoadRecommendationDto.entity; served on GET /api/load-recommender/v1/recommendations AND the LOAD_RECOMMENDATION_* WebSocket push)*

| Field | Type | Change | Null | Source / notes |
| --- | --- | --- | --- | --- |
| `faster_payment_enabled` | `Boolean` | 🟢 added | y | from cube PostingReadDto (SCP-15099) after client bump; map in LoadDtoConverter.convertPostingReadDtoToOutDto |
| `payment_method_billing (proposed)` | `String` | 🟢 added | y | additive SmartHaul-capable method passthrough; existing coarse payment_method (BILLING/CASH/USHIP) can't express smarthaul_payments — see Q1 |
| `shipper_user_management_id` | `String` | 🔵 unchanged (consumed) | n | already present; FE tooltip key for the terms fetch |

## §4b · Upstream read model (cube / models-lib)

*Dependency / DTO alignment · PostingReadDto returned by load-recommender's cube client*

| Artifact / DTO | Change | Detail |
| --- | --- | --- |
| `loadboard-client 0.6.3 → 0.6.17+ (load-recommender pom.xml:116)` | 🟡 version bump | so the returned PostingReadDto carries faster_payment_enabled (already on cube out-DTO v2 :157-158) |
| `models-lib readmodels.es.PostingReadDto.faster_payment_enabled` | 🟢 only if bump route rejected | fallback: add + populate the field on the shared read model (wider blast radius) — see Q6 |

## §4c · Frontend consumption (platform-frontend)

*Consumed fields + package bump · LoadScout card (no new contract; renders the LoadDto above)*

| Item | Change | Detail |
| --- | --- | --- |
| `entities-frontend-package 20.0.0 → ^20.2.0; globals-frontend-package 6.22.1 → ^6.24.0` | 🟡 pkg bump | for Load.fasterPaymentEnabled, the fasterPaymentConfiguration model/selectors/thunk, AnalyticsEvent.FasterPayInfo |
| `load.fasterPaymentEnabled → Faster Pay label/tooltip; load.paymentMethod → SmartHaul logo` | 🔵 consumes | PaymentVehiclesInfo.tsx; terms via fetchFasterPaymentConfigurationByShipperIds([shipperUserManagementId]) → platform-backend |
| `Faster Pay Info event + property Source=LoadScout` | 🟡 analytics | AnalyticsEvent.FasterPayInfo call site fires with zero props today |

## Where it lives & how it's wired

| Aspect | Detail |
| --- | --- |
| service | load-recommender · api-dtos + services (LoadDto owner; REST + WS) |
| file | `api-dtos/.../dtos/out/LoadDto.java · services/.../converters/impl/LoadDtoConverter.java:16-79` |
| file | `resources/.../rest/RecommendationsController.java:158,189 (GET /api/load-recommender/v1/recommendations)` |
| dep | `pom.xml:116 loadboard-client 0.6.3 · pom.xml:108 models-lib 1.0.65` |
| service | platform-frontend · CTMS LoadScout micro-frontend |
| file | `src/Common/NotificationListItem/PaymentVehiclesInfo.tsx · NotificationListItem.tsx:391` |
| reuse | `loadboard-frontend/src/components/FasterPayLabel.tsx (port or extract — Q2)` |
| service | cube · loadboard read side (faster_payment_enabled already present, SCP-15099) |
| file | `cube/loadboard/loadboard-dtos/.../out/v2/PostingReadDto.java:157-158` |
| terms | platform-backend FasterPaymentConfigurationViewSet (api/api.py:90) — reused, no change |
| relay | notification-backend — opaque WS relay, no change |
| mobile | epod-ios / epod-android — consume the REST endpoint; additive field decode-safe, display out of scope |

## Rollout

> ⚠️ **§5 · rollout & sequencing**
>
> **Sequencing (upstream first).**
>
> 1. **cube / models-lib** — confirm or publish the client version whose PostingReadDto carries the faster-pay flag (already in cube via SCP-15099).
> 2. **load-recommender** — bump that dependency and add the field (plus the SmartHaul method passthrough, Q1) to the LoadDto and its converter. One converter feeds both the REST list and the WebSocket push, so both surfaces light up together.
> 3. **platform-frontend** — bump the entities/globals packages, port the Faster Pay component, add the card blocks, and add the Source=LoadScout Mixpanel property. Depends on step 2 being live.
> 4. **QA / automation** — cover eligible, not-eligible, tooltip terms, and the Mixpanel property.
>
> **Risk — Postings resync landmine (Q5).** The syncer resync SQL reads the raw, always-null faster-pay column (a copy of the orders landmine from SCP-15098). A Postings resync nulls the flag fleet-wide, and because load-recommender live-reads that index via cube, the LoadScout badge would vanish across all cards until re-synced from events. The fix belongs to syncer but degrades this surface.
>
> **Compatibility.** The contract change is additive and backward-compatible — both ePOD apps decode leniently — so no coordinated mobile release is required.
