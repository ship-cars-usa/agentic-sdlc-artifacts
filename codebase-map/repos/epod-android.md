---
repo: epod-android
path: ~/projects/ship-cars-usa/epod-android
stack: Android / Kotlin / Gradle KTS / Clean Architecture (MVVM + Jetpack Compose for new features; MVP legacy for older features) / Firebase (`google-services.json`)
domain: operations
shape: multi-module Android app (`app/`, `module_presentation`, `module_domain`, `module_data`)
last-synced-commit: e1a5040383c097bf02481bd8cc3909f85593a538
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# epod-android

## What it is
The **ePOD (electronic Proof of Delivery) Android app** for Ship.Cars drivers. Native Android, Kotlin-first, Gradle KTS build, structured as a Clean-Architecture multi-module project (per `ARCHITECTURE.md`). Used by drivers in the field to capture pickup/delivery signoffs, photos, vehicle-condition reports, and odometer readings on a phone or tablet.

Architecture (per `ARCHITECTURE.md`):
- **Modern pattern** — MVVM + Jetpack Compose for new features.
- **Legacy pattern** — MVP for older features still being phased out.
- Both share the same Domain (use cases) + Data (repositories, remote, local) layers.
- DI via a `DependencyInjector` in `di/`.
- Navigation via `AppNavigator` in `navigation/`.

Module structure:
```
app/                  — the Android application module (Gradle main)
module_presentation   — Presentation layer (MVVM or MVP)
module_domain         — Domain layer (Use Cases)
module_data           — Data layer (Repositories, Remote, Local)
di/                   — Dependency Injection
navigation/           — Navigation
```

Last commit 2026-04-28 — actively maintained. Counterpart to `epod-ios` (same architecture intent, native Swift).

## How it fits

- **Consumes API of:** the Ship.Cars driver-facing backends — likely `posting-backend`, `attachment-backend` (for photo upload), `location-provider` / `location-history-backend` (for live position), `user-backend` for auth, plus Keycloak for OAuth. Confirm against the `module_data/.../remote/` package.
- **Owns data store:**
  - Local: Room database (standard Android Clean-Architecture pattern; verify in `module_data/.../local/`).
  - Remote: backend services.
  - Firebase (Crashlytics / FCM push) via `google-services.json`.
- **Publishes events to:** likely Pub/Sub indirectly via the backends; no direct event bus visible in the architecture.
- **Auth:** Keycloak via OAuth (standard fleet pattern).

## Build / test / run
```
./gradlew assembleDebug          # debug APK
./gradlew assembleRelease        # release APK
./gradlew test                   # unit tests
./gradlew connectedAndroidTest   # instrumented tests
./allure-reports.sh              # Allure test reports
```

CI surface includes Allure-reports for test results — same pattern as `epod-ios` and the `automation-epod-github-actions-test` mobile-test framework.

## Key abstractions

- `app/build.gradle.kts` — main Android-app Gradle module.
- `app/google-services.json` — Firebase config (Crashlytics, FCM push, possibly Analytics).
- `app/proguard-rules.pro` + `app/proguard-rules-no-logging.pro` — release-build code-shrinking + obfuscation rules (two variants: with and without logging).
- `app/src/` — application source (Kotlin).
- `app/publish/` — Play Store metadata / fastlane-style publish config.
- `ARCHITECTURE.md` — the canonical architecture guide; consult before adding new features.
- `scripts/` — build / release helper scripts.

## Don't-do-here / gotchas

- **Two presentation patterns coexist** (MVVM+Compose for new; MVP for legacy). New features should use the modern pattern; touching legacy MVP screens to fix bugs is fine but don't add new MVP code.
- **`proguard-rules-no-logging.pro` exists separately** from the main proguard rules — release builds either include or exclude logging. Confirm which variant the prod build uses; misconfigured logging in release can leak PII or fail to log diagnostic info.
- **Native mobile = a separate deploy cadence and release pipeline.** Play Store review can delay a fix by 1-7 days; Apple TestFlight + App Store similarly for iOS. Plan accordingly.
- **Firebase `google-services.json` is checked in** — this contains the Firebase project + Google API key for FCM push. It's not strictly a secret (Firebase keys are scoped by SHA-1 cert hash + package name), but auditable.
- **No e2e tests in this repo** — they live in `automation-epod-github-actions-test` (Java/Appium suite). Don't add Appium tests here; add them there.
- **Targets a real driver in the field** — UX/UI considerations are different from a desk-side web app. Offline-first / spotty-connectivity / hot-truck-cab readability all matter. Test on a real device, not just an emulator.
- **`google-services.json` in `app/`** ties this app to a specific Firebase project ID; multi-env testing (dev/qa/staging) requires either build variants with separate config files or runtime env routing.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/epod-ios.md` — iOS counterpart with the same Clean-Architecture intent.
- `~/projects/codebase-map/repos/automation-epod-github-actions-test.md` — Appium-based mobile-test framework that exercises both this and the iOS app.
- `~/projects/codebase-map/repos/attachment-backend.md` — photo/signature upload target.
- `~/projects/codebase-map/repos/posting-backend.md` — primary backend for load/delivery context.
- `~/projects/codebase-map/domains/operations.md`.
