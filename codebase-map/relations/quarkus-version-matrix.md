# Quarkus Version-Drift Matrix

What every Quarkus service in the fleet has pinned for the **Quarkus platform** and the **Ship.Cars commons + Quarkus extension** libraries. Built 2026-05-12 to make the "silent BOM-vs-extension drift" observation from Phase 4.16 quantitative.

## Why this exists

`shipcars-quarkus-bom` pins the Quarkus platform (3.27.0 at HEAD) + a small set of Quarkiverse extensions, but **does NOT pin any Ship.Cars-internal extension** (`quarkus-commons`, `quarkus-pubsub`, `quarkus-extension-webclient`, `quarkus-notification-client`, `quarkus-extension-persistence`, `quarkus-request-filter`, …). Each consuming service pins those independently in its own `<properties>` block. The result is **invisible cross-version drift**: a service can be on BOM `3.27.0` but on `quarkus-pubsub` `3.20.2.2` or `quarkus-commons` `2.4.0`, and the build still works because the extension API surface has been mostly stable. The drift only surfaces during incident-driven debugging (a fix that landed in `quarkus-commons` 3.27.0 isn't actually deployed because the service is still on 3.22.1).

## Methodology

For each Quarkus service repo, the root `pom.xml`'s `<properties>` block was scanned for known property-name variants:

- **`shipcars-quarkus-bom.version`** / `ship-cars-quarkus-bom.version` → BOM column.
- **`quarkus.platform.version`** → Quarkus platform column. (Where set independently of BOM — usually they match.)
- **`ship-cars-quarkus-commons.version`** / `shipcars-quarkus-commons.version` / `quarkus-shipcars-commons.version` → qk-commons column.
- **`ship-cars-quarkus-pubsub.version`** / `ship-cars-quarkus-extensions-pubsub.version` / `ship-cars-extensions-pubsub.version` → pubsub column.
- **`ship-cars-extensions-web-client.version`** / `ship-cars-quarkus-webclient.version` → webclient column.
- **`ship-cars-notification-extension.version`** / `ship-cars-quarkus-extensions-notification.version` / `ship-cars.notification-extension.version` → notif column.
- **`ship-cars-extension-persistence.version`** / `ship-cars-quarkus-persistence.version` → persistence column.
- **`ship-cars-commons.version`** → commons (framework-neutral) column.
- **`ship-cars-models-lib.version`** / `ship.cars.models-lib.version` → models-lib column.

**Empty cell** = property not set in the root pom. Could mean (a) extension genuinely not used, or (b) version inherited transitively from another internal library, or (c) pinned in a sub-module pom rather than the root. Spot-check the service before treating an empty cell as definitive.

**The property-name set is itself part of the problem**: there is no fleet-wide convention for what to call these properties. The same dimension (e.g. quarkus-pubsub version) is named at least 3 different ways across the fleet. Standardizing on one canonical name per dimension would let the next regen of this matrix be more reliable.

## Matrix (sorted by Quarkus platform version, oldest to newest)

| Service | Platform | BOM | qk-commons | pubsub | webclient | notif-client | persistence | commons | models-lib |
|---|---|---|---|---|---|---|---|---|---|
| **archiver** | **2.9.1.Final** | n/a (direct deps) | – | – | – | – | – | – | – |
| **notification-orchestrator** | **3.8.3** (via `quarkus-plugin.version`) | n/a | 2.7.0 | (set) | – | 1.3.0 | – | 2.4.0 | 1.0.55 |
| **toolbox-service** | 3.15.0 | 1.1.0 | – | 3.0.0 | – | 3.2.0 | – | 3.0.0 | – |
| archival-service | 3.15.2 | 1.2.0 | – | 3.1.0 | – | – | – | 3.0.0 | – |
| company-cleanup-utils | 3.15.2 | 1.2.0 | – | – | – | 3.1.0 | – | 3.6.0 | – |
| fraud-detector | 3.15.2 | 1.2.0 | – | 3.1.0 | – | 3.1.0 | – | 3.6.0 | 1.101.7 |
| command-executor | 3.20.2.2 | 3.20.2.2 | – | 3.20.2.2 | 3.20.2.2 | 3.20.2.2 | – | 3.20.0 | – |
| contract-pricing-backend | 3.20.2.2 | 3.20.2.2 | – | 3.20.2.2 | – | – | – | 3.23.0 | – |
| integrators-data-bridge | 3.20.2.2 | 3.20.2.2 | – | – | – | – | – | 3.14.0 | – |
| metadata | 3.20.2.2 | 3.20.2.4 | – | 3.20.2.2 | – | – | – | 3.20.0 | – |
| payment-backend | 3.20.2.2 | 3.20.2.2 | – | 3.20.2.2 | – | 3.20.2.2 | – | 3.14.0 | 1.121.0 |
| pubsub-exception-handler | 3.20.2.2 | 3.20.2.2 | – | 3.20.2.2 | – | – | – | 3.16.0 | – |
| user-activity-tracker | 3.20.2.4 | 3.20.2.4 | – | 3.20.2.2 | – | 3.20.2.2 | – | 3.16.0 | – |
| invoices | 3.20.2.2 | 3.20.2.4 | – | 3.20.2.4 | 3.20.2.3 | 3.20.2.3 | 3.20.2.2 | 3.22.1 | 1.127.0 |
| uship-quotes | 3.20.2.2 | 3.20.2.4 | – | 3.20.2.4 | 3.20.2.3 | – | – | 3.21.0 | 1.125.0 |
| aaag-integration | 3.20.4 | 3.20.2.4 | – | 3.20.2.4 | – | – | – | 3.23.0 | – |
| attachment-backend | 3.20.2.4 (via BOM) | 3.20.4 | – | 3.20.2.4 | – | – | – | 3.22.1 | – |
| integration-executor | 3.20.4 | 3.20.2.4 | – | 3.20.2.4 | – | 3.20.2.3 | – | 3.22.1 | – |
| ai-dashboard-backend | 3.27.0 | 3.27.0 | – | 3.27.0 | – | 3.27.0 | 3.27.0 | 3.22.1 | – |
| axe-call-integration | 3.27.0 | 3.27.0 | – | 3.27.0 | – | 3.27.0 | 3.27.1 | 3.22.1 | – |
| bi-databricks-backend | 3.27.0 | 3.27.0 | – | 3.27.0 | – | 3.27.0 | 3.27.0 | 3.22.1 | – |
| crm-workflows | 3.27.0 | 3.27.0 | – | 3.27.0 | – | – | – | 3.22.1 | 1.129.0 |
| cube | 3.27.0 | 3.27.0 | – | 3.27.0 | 3.27.0 | – | – | 3.24.0 | 1.141.0 |
| dataone | 3.27.0 | 3.27.0 | – | – | – | – | – | 3.22.1 | – |
| load-bookmark-backend | 3.27.0 | 3.27.0 | – | 3.27.1 | 3.27.0 | 3.27.1 | – | 3.22.1 | 1.129.0 |
| loadboard-backend | 3.27.0 | 3.27.0 | – | 3.27.0 | – | – | – | 3.23.0 | – |
| location-history-backend | 3.27.0 | 3.27.0 | – | 3.27.1 | 3.27.0 | 3.27.1 | – | 3.22.1 | 1.129.0 |
| location-provider | 3.27.0 | 3.27.0 | – | 3.27.0 | 3.27.0 | – | – | 3.22.1 | – |
| negotiations-router | 3.27.0 | 3.27.0 | – | 3.27.0 | – | – | – | 3.6.0 | – |
| pusher | 3.27.0 | 3.27.0 | – | 3.27.0 | – | – | – | 3.22.1 | 1.125.0 |
| saved-search-handler | 3.27.0 | 3.27.0 | – | 3.27.0 | 3.27.1 | – | – | 3.22.1 | 1.126.0 |
| syncer | 3.27.1 (BOM/extn aligned) | 3.27.0 | – | 3.27.0 | 3.27.1 | – | – | 3.22.1 | 1.143.0 |
| synclink-backend | 3.27.0 | 3.27.0 | – | 3.27.0 | – | 3.27.0 | – | 3.22.1 | – |
| trip-planner | 3.27.0 | 3.27.0 | 3.27.1 | 3.27.0 | 3.27.0 | 3.27.1 | 3.27.0 | 3.25.0 | 1.139.0 |

Total Quarkus services scanned: **34** (33 BOM-importing + `archiver` which uses direct Quarkus deps).

## Distribution by Quarkus platform version

| Platform version | Service count | Services |
|---|---|---|
| **3.27.0 / 3.27.1** (HEAD) | **16** | ai-dashboard-backend, axe-call-integration, bi-databricks-backend, crm-workflows, cube, dataone, load-bookmark-backend, loadboard-backend, location-history-backend, location-provider, negotiations-router, pusher, saved-search-handler, syncer, synclink-backend, trip-planner |
| 3.20.4 | 3 | aaag-integration, attachment-backend, integration-executor |
| 3.20.2.4 (BOM) | 4 | invoices, uship-quotes (3.20.2.2 platform via 3.20.2.4 BOM), user-activity-tracker, plus attachment-backend's BOM path |
| 3.20.2.2 | 6 | command-executor, contract-pricing-backend, integrators-data-bridge, metadata, payment-backend, pubsub-exception-handler |
| 3.15.0 / 3.15.2 | 4 | archival-service, company-cleanup-utils, fraud-detector, toolbox-service |
| **3.8.3** | **1** | notification-orchestrator |
| **2.9.1.Final** | **1** | archiver |

Half the fleet is current (3.27.x); the other half splits across five older minor versions.

## Findings

### 1. Two services are major-version-EOL outliers
- **`archiver`** runs **Quarkus 2.9.1.Final** (2022). Three major versions behind. Uses **direct Quarkus deps** rather than importing `shipcars-quarkus-bom` — so it isn't part of the BOM bump cascade. Bumping it means rewriting its dependency block from scratch.
- **`notification-orchestrator`** runs **Quarkus 3.8.3** (Jan 2024) via a bare `quarkus-plugin.version` property. Doesn't import the BOM either. Together with `notification-backend` (Spring), it's responsible for fan-out to SendGrid — running on the oldest active Quarkus version in the fleet is a meaningful latent risk.

### 2. The `commons` (framework-neutral) versions are wildly out of sync
HEAD is `ship.cars.commons:libs` 3.28.0-SNAPSHOT. Fleet distribution:

| `commons` version | Services |
|---|---|
| 3.25.0 | trip-planner |
| 3.24.0 | cube |
| 3.23.0 | aaag-integration, contract-pricing-backend, loadboard-backend |
| 3.22.1 | ai-dashboard-backend, attachment-backend, axe-call-integration, bi-databricks-backend, crm-workflows, dataone, integration-executor, invoices, load-bookmark-backend, location-history-backend, location-provider, pusher, saved-search-handler, syncer, synclink-backend |
| 3.21.0 | uship-quotes |
| 3.20.0 | command-executor, metadata |
| 3.16.0 | pubsub-exception-handler, user-activity-tracker |
| 3.14.0 | integrators-data-bridge, payment-backend |
| 3.6.0 | company-cleanup-utils, fraud-detector, negotiations-router |
| 3.0.0 / 3.1.0 | archival-service, toolbox-service |
| **2.4.0** | **notification-orchestrator** |

The "most-common" commons version is 3.22.1 (15 services), six minors behind HEAD. **No service in the fleet is on the latest commons** (3.28.0-SNAPSHOT). `payment-backend` at 3.14.0 and `integrators-data-bridge` at 3.14.0 are 14 minors behind. `notification-orchestrator` at 2.4.0 is a different era.

### 3. `quarkus-pubsub`, `quarkus-extension-webclient`, `quarkus-notification-client` track the platform version closely
Where these are pinned at all, they typically align with the service's Quarkus platform version (e.g. a service on Quarkus 3.20.2.2 pins `quarkus-pubsub` 3.20.2.2; a service on 3.27.0 pins 3.27.x). **Drift within a single service is rare** — but **drift across services is universal** because Quarkus platform versions are scattered.

### 4. `quarkus-extension-persistence` is pinned by only 4 services in the property block
`ai-dashboard-backend`, `axe-call-integration`, `bi-databricks-backend`, `invoices`, `trip-planner`. The other 9 consumers identified in `relations/service-graph.md` likely inherit the version via `quarkus-imperative-boilerplate` / `quarkus-k8s-boilerplate` parent poms or via another transitive path. **The 14-consumer count in the service-graph is correct; the matrix just doesn't capture all of them because some inherit rather than pin directly.**

### 5. `models-lib` pin distribution
HEAD is 1.144.0-SNAPSHOT. Fleet distribution:

| `models-lib` version | Services |
|---|---|
| 1.143.0 | syncer |
| 1.141.0 | cube |
| 1.139.0 | trip-planner |
| 1.129.0 | crm-workflows, load-bookmark-backend, location-history-backend |
| 1.127.0 | invoices |
| 1.126.0 | saved-search-handler |
| 1.125.0 | pusher, uship-quotes |
| 1.121.0 | payment-backend |
| 1.101.7 | fraud-detector |
| **1.0.55** | **notification-orchestrator** |

`fraud-detector` at 1.101.7 is a meaningful outlier (~40 minors behind). `notification-orchestrator` at 1.0.55 is a different DTO era — any DTO field added in the last few years isn't in this service's compiled view.

### 6. Property naming is fleet-wide inconsistent
Same dimension, different names across services:

| Dimension | Variants seen |
|---|---|
| BOM | `shipcars-quarkus-bom.version`, `ship-cars-quarkus-bom.version` |
| qk-commons | `quarkus-shipcars-commons.version`, `shipcars-quarkus-commons.version`, `ship-cars-quarkus-commons.version` |
| pubsub | `ship-cars-quarkus-pubsub.version`, `ship-cars-quarkus-extensions-pubsub.version`, `ship-cars-extensions-pubsub.version` |
| webclient | `ship-cars-extensions-web-client.version`, `ship-cars-quarkus-webclient.version` |
| notif | `ship-cars-notification-extension.version`, `ship-cars-quarkus-extensions-notification.version`, `ship-cars.notification-extension.version` |
| persistence | `ship-cars-extension-persistence.version`, `ship-cars-quarkus-persistence.version` |

Standardizing on **one canonical name per dimension** would make this matrix regen-able by script. Today it requires the variant-enumeration heuristic above.

## Recommendations

1. **Treat `notification-orchestrator` (Quarkus 3.8.3, commons 2.4.0, models-lib 1.0.55) as a P1 lifecycle item** alongside `lead-parser` (Spring 2.1.4) and `rateengine` (Django 2.1.7). These three are the fleet's oldest active services across their respective stacks; together they cover the highest patch-debt surface.
2. **`archiver` is a special case** — re-evaluate whether the service is still load-bearing (`infrastructure-triage.md` candidate?) before bumping Quarkus. If it's truly archival-only and rarely runs, the cost-benefit of a Quarkus 2 → 3.27 rewrite may not pencil.
3. **Adopt a canonical property-name convention** so the next matrix regen is trivial. Proposed:
   ```
   shipcars-quarkus-bom.version
   shipcars-quarkus-commons.version
   shipcars-quarkus-pubsub.version
   shipcars-quarkus-webclient.version
   shipcars-quarkus-notification-client.version
   shipcars-quarkus-persistence.version
   shipcars-commons.version
   shipcars-models-lib.version
   ```
   Migration is one mechanical PR per repo.
4. **Pin Ship.Cars extensions in the BOM**, not per-consumer. The BOM already pins Quarkiverse extensions (`quarkus-logging-json`, `quarkus-google-cloud-pubsub`, `quarkus-unleash`, `quarkus-tika`); adding the Ship.Cars extensions to the same `<dependencyManagement>` block would eliminate the BOM-vs-extension drift class entirely. The cost is that bumping a single Ship.Cars extension requires a BOM bump and a fleet recompile — but that's already true for every Quarkiverse extension version in the BOM.
5. **`commons` (framework-neutral) drift is the biggest individual gap**. Bumping `commons` 3.22.1 → 3.28.0 across the 15-service "most-common" cohort is a single coordinated PR per service. Worth a quarter-scale push.

## Related
- `~/projects/codebase-map/repos/shipcars-quarkus-bom.md` — the BOM seed; documents what is and isn't pinned.
- `~/projects/codebase-map/repos/commons.md` — framework-neutral commons; carries the wildly-drifting `ship-cars-commons.version`.
- `~/projects/codebase-map/repos/models-lib.md` — DTO library; same drift pattern.
- `~/projects/codebase-map/relations/service-graph.md` — compile-time-edges table with fanout counts.
- `~/projects/codebase-map/domains/platform.md` — domain rollup.
