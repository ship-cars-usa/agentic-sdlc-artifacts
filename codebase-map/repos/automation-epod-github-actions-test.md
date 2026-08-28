---
repo: automation-epod-github-actions-test
path: ~/projects/ship-cars-usa/automation-epod-github-actions-test
stack: Java / Gradle / Appium (cross-platform Android + iOS UI automation) / YAML test config / Jenkinsfile
domain: operations
shape: single-module test-framework repo
last-synced-commit: 7bbfca8813fb44eddf872ffa9de1fbd12520e393
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# automation-epod-github-actions-test

## What it is
The **mobile automation test framework** for the ePOD apps. Runs Appium-driven UI tests against both `epod-android` and `epod-ios` from a single Java test suite. YAML-based config for login credentials + test roles; supports parallel execution across platforms and test groups. Distributed via two Dockerfiles (`Dockerfile`, `Dockerfile-automation-base`) and a `Jenkinsfile.groovy` for CI orchestration. The repo name suggests it was originally a GitHub Actions test harness; it's now run via Jenkins (the Jenkinsfile is the canonical CI entry).

Last commit 2025-10-10 — actively maintained, but on a slower cadence than the apps it tests.

## How it fits

- **Drives:** `epod-android` (any OS can run Android tests) and `epod-ios` (iOS tests require an Apple device — macOS host).
- **Consumes API of:** none directly. Tests **simulate user interaction** in the app UI; the apps themselves talk to the real Ship.Cars backends or to a test-double surface, depending on the test environment.
- **Publishes events to:** none.
- **Owns data store:** none (test-state only).
- **Auth:** uses test-account credentials checked into YAML config (or injected at CI time).

## Build / test / run
```
# Local Android test setup (per README):
# 1. Install Android Studio + emulators
# 2. Match emulator names to the capability names in DriverManager.java
./gradlew build
./gradlew test                # runs the configured test groups

# Docker-based CI execution:
docker build -f Dockerfile-automation-base -t epod-automation-base .
docker build -t epod-automation .
docker run epod-automation     # entrypoint via entrypoint.sh

# Jenkins: the Jenkinsfile.groovy is the canonical pipeline.
```

iOS tests **only run on macOS hosts** — the Jenkins pipeline / CI must route iOS test jobs to Mac executors.

## Key abstractions

- `src/test/java/com/ship/cars/automation/epod/core/driver/DriverManager.java` (per README) — manages the Appium driver lifecycle. Holds the Android + iOS capability sets; **emulator names in `getAndroidDriver()` must match the names you give your virtual devices** for the tests to find them.
- `Jenkinsfile.groovy` — CI pipeline; canonical execution surface in prod.
- `Dockerfile-automation-base` — base image carrying the Appium / Java / Gradle / Android-SDK toolchain.
- `Dockerfile` — the test-runner image built on top of the base.
- `entrypoint.sh` — container entry; sets up the test environment + runs gradle.
- `docs/` — additional documentation (worth reading for the test-group taxonomy).
- `build.gradle` (Groovy DSL, not KTS — older Gradle pattern).

## Don't-do-here / gotchas

- **Don't add Appium tests in `epod-android` or `epod-ios`** — they live here. Both app repos have their own light XCTest / JUnit-instrumented test scaffolding, but cross-platform UI automation centralizes here.
- **iOS tests = macOS-only.** CI configuration must respect this; trying to run iOS automation on a Linux runner will silently fail in confusing ways.
- **`Jenkinsfile.groovy` is the source of truth for CI**, not a `.github/workflows/*.yml`, despite the repo name. The name is a leftover; the CI moved to Jenkins.
- **Emulator-name matching to capabilities** is a real footgun for local devs. The README warns: name your Android virtual devices to match the names in `DriverManager.java:getAndroidDriver()`.
- **Test credentials in YAML config** — verify these are test-account-only and not real user credentials. PII / production-account exposure here would be a real issue.
- **Two-stage Docker build** (`Dockerfile-automation-base` + `Dockerfile`). Cache-busting the base for a toolchain update means downstream builds rebuild from scratch.
- **Groovy `build.gradle` (not KTS).** Older Gradle pattern; differs from `epod-android`'s KTS build files. Don't try to share Gradle conventions cross-repo without translating the syntax.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/epod-android.md` — Android target.
- `~/projects/codebase-map/repos/epod-ios.md` — iOS target.
- `~/projects/codebase-map/repos/ios-epod-github-actions-test.md` — companion iOS-specific test repo.
- `~/projects/codebase-map/domains/operations.md`.
