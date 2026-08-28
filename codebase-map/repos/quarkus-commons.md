---
repo: quarkus-commons
path: ~/projects/ship-cars-usa/quarkus-commons
stack: Java 21 / Quarkus 3.27.5 — `ship.cars.quarkus.commons:libs` 3.27.5.1-SNAPSHOT (3 library modules)
domain: platform
shape: multi-module (root `libs` + quarkus-commons + quarkus-opentelemetry + quarkus-logging-json-fix)
last-synced-commit: 506da35ae128e30e88c9216768fe3e2d602a53d3
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# quarkus-commons

## What it is
Shared Quarkus library suite (groupId `ship.cars.quarkus.commons`, root artifact `libs`) consumed across the Quarkus fleet. **Not a BOM** — it consumes the external `shipcars-quarkus-bom` (3.27.5) and depends on `ship.cars.commons` (`ship-cars-commons` 3.33.0) for the heavy lifting. Released to GitHub Packages; current version 3.27.5.1-SNAPSHOT. It provides three focused modules: MDC/OTel propagation, a structured-JSON `LogData` helper, and a startup fix for `quarkus-logging-json`.

## How it fits
- **What it provides / who consumes it:** ~41 fleet repos reference `quarkus-opentelemetry` (the most-used module); the observability/MDC baseline in most Quarkus services originates here. `quarkus-request-filter` and `quarkus-pubsub` both build on its `QuarkusMdcUtils` / structured-logging helpers.
- **Publishes events to:** n/a (compile-time library).
- **Owns data store:** none.
- **Companions:** `shipcars-quarkus-bom` (the BOM, separate repo) and `commons` (the `ship.cars.commons` Java utilities). Part of the 2024 split into `commons` / `quarkus-commons` / `spring-commons` / `docker-utils`.

## Build / test / run
```
mvn -s ./.mvn/settings.xml clean deploy        # deploy to GitHub Packages
./mvnw -s .mvn/settings.xml test                # unit tests
./mvnw -s .mvn/settings.xml test -Pintegration-tests
./deploy-project.sh                             # wrapper
```
`GITHUB_TOKEN` / `GITHUB_USERNAME` must be exported. Commit-message hook enforces `LITE-*` / `Merge` prefix. JavaDoc: https://ship-cars-usa.github.io/quarkus-commons/javadoc/

## Key abstractions / what it provides
- **`quarkus-opentelemetry` module** (`ship.cars.quarkus.commons:quarkus-opentelemetry`):
  - `QuarkusMdcUtils` — `quarkus-opentelemetry/.../cars/ship/commons/quarkus/QuarkusMdcUtils.java` — `executeWithNewMdcData()` / `executeWithMdcData()` propagate MDC (user, company, request id, message id) across async/thread-pool boundaries. The canonical pattern for keeping trace context attached; used by `quarkus-request-filter`.
  - `QuarkusMdcData` — same package — typed MDC-field container.
  - Wires `io.quarkus:quarkus-opentelemetry`; depends on `ship.cars.commons:error-handling` for error classification.
- **`quarkus-commons` module** (`ship.cars.quarkus.commons:quarkus-commons`):
  - `LogData` — `quarkus-commons/.../cars/ship/commons/quarkus/utils/LogData.java` — level-guarded structured logging that attaches a serialized object under the `data` key via `kv(...)`, zipping large payloads (`toZipOrPlainObject`). Uses `ObjectSerializer.toStringSuppressLog` so serialization failures don't blow up the log call.
- **`quarkus-logging-json-fix` module** (`ship.cars.quarkus.commons:quarkus-logging-json-fix`):
  - `QuarkusLoggingJsonStartupFix` + `CustomJacksonJsonFactory`/`CustomJacksonJsonGenerator` — `quarkus-logging-json-fix/.../loggingjson/` — patch `quarkus-logging-json` (3.4.0) so structured-JSON logs serialize correctly (Jackson wiring at startup).
- Error codes, retry helpers, object serialization, UUIDs live in the separate `ship.cars.commons:commons` (3.33.0) — see the `commons` shadow.

## Don't-do-here / gotchas / conventions imposed on consumers
- **No REST-client baseline.** `quarkus.rest-client.*.connect-timeout` / `read-timeout` are still *not* set fleet-wide here. Every consuming service must configure timeouts itself — the systemic gap from the fleet review (`~/projects/quarkus-rest-client-timeout-anti-pattern.md`). Publishing a baseline-properties module remains the single highest-leverage change to this repo.
- **No `@Retry` jitter helper.** Services that retry (e.g. `aaag-integration`, `bi-databricks-backend`) each roll fixed backoff individually; a shared helper here would retire that risk.
- **MDC propagation is mandatory for async work** — spawning async/thread-pool work without `QuarkusMdcUtils.executeWithNewMdcData()` loses trace context.
- **Jandex indexing required** — every module uses `jandex-maven-plugin`; consumers extending these libs must too, or bean discovery / hot-reload can miss classes.
- **Version skew risk** — SNAPSHOT deps must not reach staging/prod (see README release process); pull `commons` + this in lockstep against the BOM.

## Relevant ADRs / docs
- `README.md` — the 2024 four-repo split and the SNAPSHOT-on-QA / stable-on-staging release hygiene.
- `utils/release/README.md` — version-bump and release process.
- `~/projects/quarkus-fleet-review-2026-05-07.md` — the consistent observability baseline across services originates here.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `QuarkusMdcData` | dto | `quarkus-opentelemetry` | QuarkusMdcData |
<!-- entities-end -->
