---
domain: operations
status: draft
owner-team: unknown
member-services: 18
last-reviewed: 2026-05-12
---

# Domain — operations

## Purpose
Carrier execution side: physically tracking the vehicle from pickup to delivery, planning the trip, verifying location, capturing electronic proof of delivery (ePOD), routing negotiations.

## Member services
| Repo | Role | Stack |
|---|---|---|
| public-tracking-backend | public-facing tracking API | Java/Spring Boot 3.2.12 |
| public-tracking-frontend | public tracking UI | React/Vite SPA |
| location-history-backend | historical location store | Java/Quarkus 3.27.0 |
| location-provider | live location service | Java/Quarkus 3.27.0 |
| quarkus-locationprovider-client | Quarkus client for location-provider | Java/Quarkus 3.27.0 |
| driveaway-backend | Driveaway REST API | Java/Spring Boot 3.2.12 |
| driveaway-public-tracking-frontend | Driveaway tracking UI | React/Vite SPA |
| chase-driver-tracking-frontend | Chase driver tracking | React/Vite SPA |
| trip-planner | trip-planning service | Java/Quarkus 3.27.0 |
| trip-planner-frontend | trip-planner UI | React/Vite SPA |
| negotiations-router | route negotiations between parties | Java/Quarkus 3.27.0 |
| asg-checkout-spa | ASG checkout SPA | React/Vite |
| epod-android | ePOD Android app | Android (Gradle KTS) |
| epod-ios | ePOD iOS app | iOS / Swift / CocoaPods |
| ios-epod-github-actions-test | iOS ePOD CI test harness | iOS / GitHub Actions |
| automation-epod-github-actions-test | ePOD test automation | Java/Gradle |
| home-delivery-backend | home delivery backend | Node/TypeScript |
| synclink-backend | sync Chrome extension load state with Posting | Java/Quarkus 3.27.0 |
| synclink-chrome-extension | Chrome extension for sync | Browser extension |

## Key flows
- **Live tracking:** ePOD apps + `location-provider` ingest locations → `location-history-backend` persists → `public-tracking-backend` (and Driveaway peer) serves to the public UI.
- **Trip planning:** `trip-planner` consumes route + carrier inputs and emits a sequence of stops; `negotiations-router` handles back-and-forth.
- **Synclink:** the Chrome extension syncs local Keycloak state with `synclink-backend` and posting.

## Data stores
- `location-history-backend`: presumably a time-series-friendly store (Postgres + indexes, or possibly a specialized DB). TBD.
- `driveaway-backend`: Postgres.

## Cross-cutting concerns
- Both backend Java services here are Spring Boot, not Quarkus, despite `PROJECTS_INDEX.md` listing them as Quarkus (`driveaway-backend`, `public-tracking-backend`).
- ePOD has Android + iOS native apps, not a shared codebase.
- Privacy: ingesting and serving live location requires explicit consent / retention policy. Confirm where that's documented.

## Open questions / known gaps
- The relationship between `location-provider` (live) and `location-history-backend` (historical) — write-path? Topic? REST? **Resolved (Phase 4.13):** both consume `cars.ship.*.carrierlb.events` + `lh-load-location-log.events`. The split is parallel Pub/Sub consumption, not write-through.
- ~~Does `chase-driver-tracking-frontend` consume the same APIs as `public-tracking-frontend`?~~ **Partially resolved (Phase 4.22):** `chase-driver-tracking-frontend` is a Loadmate-internal driver-tracking surface; the two public-* frontends serve public-facing tracking pages at `public-dev.ship.cars` / `public.ship.cars`. They overlap in the location data they show but differ in audience (logged-in dispatcher vs. anonymous recipient).
- ~~Are the `epod-*-github-actions-test` repos active CI artifacts or archive candidates?~~ **Resolved (Phase 4.22):** `automation-epod-github-actions-test` is the canonical Appium-based mobile-automation framework, actively maintained (last commit 2025-10-10), now driven by Jenkinsfile. `ios-epod-github-actions-test` is an empty-README CI snapshot of `epod-ios` and is **archive-candidate**.
- **`synclink-chrome-extension`** is currently `operations` but `synclink-backend` was re-domained to `integrations` in Phase 4.9. The extension belongs in `integrations` too — re-domain pending.
- **`home-delivery-backend`** is a dealer-facing widget bridge — could be argued as `integrations` (external-dealer integration) rather than `operations`. Left in `operations` for now to stay aligned with the existing rollup.
- **`asg-checkout-spa`** is a Montway-branded checkout SPA on a **2017-era React 15 + Redux 3 + Node 5 stack** — could be argued as `integrations` (Montway-facing) rather than `operations`. **Archive-candidate** if Montway has migrated to a newer surface.
- Two parallel paths to `location-provider`: `quarkus-locationprovider-client` (typed wrapper, used by `trip-planner` + `uship-quotes`) vs. direct `@RegisterRestClient` declarations in other callers (`contract-pricing-backend`, `cube`, `aaag-integration`, etc.). The fleet hasn't standardized on either.

## Related ADRs
- None recorded yet.

## Coverage
**18 of 18 shadows are `seed`** — operations is **catalog-complete** as of 2026-05-12 (Phase 4.22). Newly seeded in Phase 4.22:
- `public-tracking-frontend` — unusual two-build single-spa repo (own root + own app-parcel) for the standalone public deployment at `public.ship.cars` (not Loadmate-mounted).
- `driveaway-public-tracking-frontend` — Driveaway-side public tracking UI; uses **react-router 7.13** (newest in the fleet) + matching `single-spa` 6 generation.
- `chase-driver-tracking-frontend` — Loadmate-internal driver-tracking MFE; modern single-spa-react 6 / MUI 6.4 stack.
- `asg-checkout-spa` — **Montway Checkout SPA on a 2017-era stack** (React 15.6, Redux 3.6, react-router 3, Node 5, axios 0.16, node-sass 4). Frozen-but-still-deployed legacy. P1 lifecycle item alongside `lead-parser` (Spring 2.1.4) and `rateengine` (Django 2.1.7).
- `epod-android` — native Kotlin Clean-Architecture app (MVVM + Compose modern; MVP legacy). Multi-module (`module_presentation`, `module_domain`, `module_data`, `di`, `navigation`). Firebase integrated.
- `epod-ios` — Swift Clean-Architecture counterpart (UIKit MVVM current; SwiftUI ready for future). CocoaPods, three env Info.plists, `Pods/` checked in.
- `automation-epod-github-actions-test` — Appium-driven Java mobile-automation framework; cross-platform Android + iOS UI tests. Driven by Jenkinsfile (despite the repo name suggesting GitHub Actions). Two-stage Docker build.
- `ios-epod-github-actions-test` — empty-README iOS snapshot; **archive-candidate** (added to the archive-candidates list).

**Archive-candidates accumulated from this pass:** `asg-checkout-spa` (Montway legacy), `ios-epod-github-actions-test` (empty CI mirror).
