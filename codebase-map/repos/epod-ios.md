---
repo: epod-ios
path: ~/projects/ship-cars-usa/epod-ios
stack: iOS / Swift / Xcode workspace + CocoaPods / Clean Architecture (UIKit MVVM current; SwiftUI templates ready for future)
domain: operations
shape: Xcode workspace (`ShipCars.xcworkspace`, `ShipCars.xcodeproj`, `ShipCars/` source, separate Unit + UI test targets, CocoaPods)
last-synced-commit: d80a8ac5fbce3be844f124213bcdab5a4231d823
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# epod-ios

## What it is
The **ePOD (electronic Proof of Delivery) iOS app** for Ship.Cars drivers — Swift / Xcode counterpart to `epod-android`. Native iOS app for capturing pickup/delivery signoffs, photos, vehicle conditions, and odometer readings.

Architecture (per `ARCHITECTURE.md`):
- **Current**: UIKit + MVVM (the actively-used pattern; all production screens).
- **Future**: SwiftUI (templates exist; not yet used in production).
- Both share the same Domain + Data layers.

Build via Xcode workspace; dependencies managed by CocoaPods (`Podfile` + `Podfile.lock`, `Pods/` directory checked in — uncommon, but normal for some iOS shops). Three Info.plists for `Dev`, `QA`, and `Staging` build configurations; presumably a fourth for prod is selected via xcconfig in a build setting.

Last commit 2026-05-04 (`Release/3 21 0 (#221)`) — actively maintained, on a versioned-release cadence (v3.21.0). Counterpart to `epod-android`.

## How it fits

- **Consumes API of:** same Ship.Cars driver-facing backends as `epod-android` — likely `posting-backend`, `attachment-backend` (photo upload), `location-provider` / `location-history-backend`, `user-backend`. Auth via Keycloak (OAuth / OIDC); typically via `AppAuth` or a similar Swift library.
- **Publishes events to:** none directly.
- **Owns data store:** local (likely Core Data or Realm; verify in the `ShipCars/Data` layer).

## Build / test / run
```
# Open in Xcode
open ShipCars.xcworkspace

# Install pods first if needed
pod install

# CLI build (example, adjust scheme + config):
xcodebuild -workspace ShipCars.xcworkspace -scheme "ShipCars Dev" -configuration Debug build

# Tests
xcodebuild test -workspace ShipCars.xcworkspace -scheme "ShipCars Dev" -destination 'platform=iOS Simulator,name=iPhone 15'
./allure-reports.sh        # Allure test reporting (matches the Android pattern)
```

## Key abstractions

- `ShipCars.xcworkspace` — the **canonical entry point**; always open the workspace, not `ShipCars.xcodeproj`, because Pods is integrated at the workspace level.
- `ShipCars/` — the actual app source (Swift files organized per Clean-Architecture layers per `ARCHITECTURE.md`).
- `Podfile` + `Podfile.lock` — CocoaPods deps + lock.
- `Pods/` directory **checked into the repo** — uncommon for iOS shops in 2026 (most rely on `pod install` post-clone), but eliminates clone-time CocoaPods downloads + makes the build hermetic.
- `ShipCars Dev-Info.plist` / `QA-Info.plist` / `Staging-Info.plist` — per-env Info.plist files; selected by Xcode build configurations.
- `ShipCarsUnitTests/` — unit test target.
- `ShipCarsUITests/` — UI test target (likely XCTest-driven; separate from the Appium suite in `automation-epod-github-actions-test`).
- `Backlog/` — internal backlog notes (uncommon at repo top level; check for stale TODOs).
- `Gemfile` — Ruby deps for fastlane / CocoaPods tooling.
- `allure-reports.sh` — Allure report generation (parallel to `epod-android`).

## Don't-do-here / gotchas

- **Three Info.plists for dev / qa / staging only.** Production is selected via xcconfig; verify the prod build flow before assuming a config edit propagates.
- **`Pods/` checked into repo** is unusual. If you `pod install`, the diff churn can be large. Coordinate dep updates so the lockfile + Pods commits land together.
- **UIKit MVVM is current; SwiftUI is future-ready but unused.** Don't ship a SwiftUI screen as a new production feature without coordinating with the team — the Domain/Data layer interface from a SwiftUI view may differ from UIKit conventions.
- **No e2e tests live here.** XCTest UI tests cover smoke flows; comprehensive e2e is in `automation-epod-github-actions-test` (Appium). Don't duplicate.
- **`allure-reports.sh`** depends on the Allure binary being installed locally; CI has it.
- **Apple Developer signing** is required for any actual device build; CI handles this with fastlane match (probably — `Gemfile` suggests fastlane).
- **iOS deploy cadence** is slower than web — App Store review is 1-7 days; plan accordingly.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/epod-android.md` — Android counterpart with the same Clean-Architecture intent.
- `~/projects/codebase-map/repos/automation-epod-github-actions-test.md` — Appium-based mobile-test framework.
- `~/projects/codebase-map/repos/ios-epod-github-actions-test.md` — iOS-specific CI test harness (stub).
- `~/projects/codebase-map/repos/attachment-backend.md` — photo/signature upload target.
- `~/projects/codebase-map/domains/operations.md`.
