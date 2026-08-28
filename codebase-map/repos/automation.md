---
repo: automation
path: ~/projects/ship-cars-usa/automation
stack: Java 21 / Gradle (wrapper, Gradle 8.6 in CI) / TestNG / Selenium 4 / REST Assured / Allure / SonarQube — Docker + Jenkins CI
domain: infrastructure
shape: single Gradle project (test sources only, ~1600 files)
last-synced-commit: 03f037c5cfd4f452ba26b412fe62da90664c4052
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# automation

## What it is
**The fleet's primary end-to-end test-automation framework.** A Java 21 + Gradle suite (`com.ship.cars:automation:0.0.1-SNAPSHOT`) that drives Ship.Cars products through both their **UIs (Selenium 4 / Chrome)** and their **REST APIs / websockets (REST Assured, socket.io, Java-WebSocket)**, runs in CI on Jenkins + Kubernetes, and publishes **Allure** reports. All sources live under `src/test/java/com/ship/cars/automation/` — there is no `src/main`.

Per `README.md`, the suites cover: **Carrier TMS** (UI, REST, websockets, Cube, Trip Planner, Invoices, Loadboard backend), **Shipper TMS** (UI, Admin/Checkout/Gateway APIs, uShip), **Loadboard** (UI + API regression), **Loadmate** (UI + API), **Core/CRM workflows**, and **cross-product shipper⇄carrier** integration flows. Test-source top-level packages: `carriertms`, `shippertms`, `loadboard`, `loadmate`, `core`, `crmworkflows`, `integrationApiTests`, `uship`, `carrierpovshipperpov`, plus `*pages` page-object packages and `config`/`utils`.

## How it fits

- **Drives:** live end-to-end tests against real environments (`dev`/`qa`/`staging`/`prod`). These are slow integration/UI runs hitting external providers.
- **Consumes (compile-time):** DTO/enum artifacts published to GitHub Packages by ~20 fleet backends — `autoims-backend`, `commons` (incl. `test`/`test-data`/`error-handling`), `contract-pricing-backend`, `cube` (ctms-orders + loadboard DTOs), `driveaway-backend`, `inventory-backend`, `loadbuilder-backend`, `models-lib`, `notification-manager`, `trip-planner`, `posting-backend`, `invoices-backend`, `user-backend` (usermanagement DTOs), `integrations-backend` (QuickBooks), `attachment-backend`, `locationprovider`, `loadboard-backend`, `command-executor`, `notification-client`, `metadata`. So it imports real service contracts rather than re-declaring them.
- **Also pulls:** Stripe SDK, QuickBooks SDK, Google Cloud Pub/Sub + Secret Manager clients, PDFBox, jakarta.mail/angus-mail (email assertions), Awaitility, AssertJ/Hamcrest/json-unit/jsonassert.
- **Companion:** `automation-epod-github-actions-test` (mobile/Appium side).
- **Owns:** test code + fixtures + TestNG suite XMLs; nothing in production.

## Build / test / run
```
./gradlew build
./gradlew test -PsuiteFile=critical_path_shipper_QA.xml         # run a TestNG suite by name (92 XMLs in tests/)
ACTIVE_PROFILE=staging ./gradlew test -PsuiteFile=critical_path_shipper_Staging.xml
./gradlew :test --tests "com.ship.cars.automation.loadmate.api.managedservices.ManagedServicesApiTest"
./gradle-sonar-compile-only.sh                                  # Sonar static analysis (test code only)
# CI: Jenkinsfile.groovy (Docker: Dockerfile-automation-base -> Dockerfile, entrypoint.sh)
```
- **Environment selection:** `ACTIVE_PROFILE` env var → `src/test/resources/application-{env}.properties` (`dev`/`qa`/`staging`/`prod`, defaults to `qa`).
- **Secrets:** loaded from `credentials/secrets-common.json` + `credentials/secrets-{env}.json` (fixtures like `${LM_DEV_ACC1_USR}` resolve from these files, NOT shell env). Dependency resolution needs `GITHUB_USERNAME` / `GITHUB_READ_TOKEN`.
- **Headless:** `HEADLESS=true` reproduces CI Chrome; the driver factory uses WebDriverManager.
- Build plugins: Allure Gradle plugin 2.12.0, SonarQube plugin 6.3.1.5724; test runner TestNG 7.12.0, Allure-TestNG 2.35.3.

## Key abstractions
- `tests/*.xml` — 92 TestNG suite definitions (per-product, per-environment: `carrier_tms_regression_qa_part{1,2,3}.xml`, `critical_path_shipper_*.xml`, `cube_tests*.xml`, `core_regression_test_*.xml`, `gateway_api_tests_*.xml`, etc.). Selected via `-PsuiteFile`.
- `src/test/java/com/ship/cars/automation/shippertms/BaseTest.java` — driver factory / `HEADLESS` handling; per-product `BaseTest` classes exist.
- `*pages` packages (`carriertmspages`, `shippertmspages`, `loadmatepages`, `cdpages`) — Selenium page objects.
- `.run/<TestClass> <Env>.run.xml` — IntelliJ Gradle run configs; per `CLAUDE.md` these are the authoritative record of how each test launches per environment (extract `ACTIVE_PROFILE` + the `--tests` filter).
- `SONARQUBE.md` + `gradle-sonar-compile-only.sh` — Sonar runs static analysis over `src/test/java` only (`sonar.tests` disabled, no coverage).

## Don't-do-here / gotchas
- **~1600 files.** IDE indexing is heavy; scope work to a sub-package.
- **Tests are live and slow** — real environments, external provider calls, long `wait180sUntil`/Awaitility polls. Log to a file and run in the background; failures can be environmental, not code.
- **Secrets come from `credentials/*.json`, not shell env** — a missing/incorrect `secrets-{env}.json` looks like a test bug but isn't.
- **Test failures here gate fleet deploys** (Jenkins) — coordinate with QA/SRE before disabling tests or touching shared utils.
- **Multi-stage Docker:** `Dockerfile-automation-base` carries JDK 21 + Gradle + Chrome; `Dockerfile` layers the test code. Base-layer cache invalidation rebuilds everything downstream.
- **Sonar config is static-analysis-only** — don't expect coverage numbers from it.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/automation-epod-github-actions-test.md` — mobile-side counterpart.
- `~/projects/codebase-map/relations/infrastructure-triage.md` — active repo (HEAD 2026-08-28).
- `~/projects/codebase-map/domains/infrastructure.md`.
