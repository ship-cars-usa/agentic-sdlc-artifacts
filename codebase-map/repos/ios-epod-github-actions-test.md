---
repo: ios-epod-github-actions-test
path: ~/projects/ship-cars-usa/ios-epod-github-actions-test
stack: iOS / Xcode workspace (CocoaPods) — README-empty stub of `epod-ios`
domain: operations
shape: snapshot / CI test harness (no distinct test content visible at top level)
last-synced-commit: 5406e96feaf06928dbb7c8b8ca65c347352785ff
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# ios-epod-github-actions-test

## What it is
**A snapshot / test harness of `epod-ios`** used by CI. The top-level layout mirrors `epod-ios` exactly (`ShipCars/`, `ShipCars.xcworkspace`, `ShipCars.xcodeproj`, `Podfile`/`Podfile.lock`, `Pods/`, three env Info.plists, `ShipCars Dev-Info.plist` / `QA-Info.plist` / `Staging-Info.plist`, `ReadMe.md` — same shape) but the **`ReadMe.md` is empty** (just an empty file) and the repo carries a `.github` history of being a CI-only test artifact (the name itself: `*-github-actions-test`).

Last commit 2025-05-14 (`Remove driver install step`) — minor maintenance only. The repo's purpose is **CI plumbing**, not a separate active iOS surface.

## How it fits

- **Drives nothing in production.** This is a CI artifact, parallel to `automation-epod-github-actions-test` (the cross-platform mobile-automation framework). The naming pattern (`*-github-actions-test`) suggests it was originally part of GitHub Actions CI for iOS — now possibly run via Jenkins (matching `automation-epod-github-actions-test`'s migration).
- **Likely an archive-candidate** unless someone confirms an active CI job points here. Verify the Jenkins / GitHub Actions config before treating it as load-bearing.

## Build / test / run
Not applicable — no production deploy surface. If a CI job builds it, the pipeline is the source of truth, not the repo's local commands.

## Key abstractions

- `ShipCars.xcworkspace` — Xcode workspace; opens the same shape as `epod-ios`.
- `Podfile` + `Podfile.lock` + `Pods/` — CocoaPods deps + checked-in Pods.
- Three env Info.plists — same per-env pattern as `epod-ios`.
- `ReadMe.md` — empty.

## Don't-do-here / gotchas

- **Confirm whether this repo is active before editing.** The empty README + `Remove driver install step` last commit + `-github-actions-test` naming all suggest it's a leftover from a CI migration that may have moved on. Verify CI config first.
- **Don't pattern-match this repo as a primary iOS surface.** The active iOS app is `epod-ios`. Treat this as throwaway / CI-only.
- **If this is dead**, archive it on the next `infrastructure-triage.md` refresh alongside the other archive-candidates already flagged (`ml-model-time-to-dispatch`, `aaag-poc`, `aaag-integration-logs-ARCHIVED`, `apache-camel-etl-demo`).

## Status / recommendation
**Archive-candidate.** Flag for the next triage refresh.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/epod-ios.md` — the active iOS app this repo mirrors.
- `~/projects/codebase-map/repos/automation-epod-github-actions-test.md` — the canonical mobile-automation framework.
- `~/projects/codebase-map/relations/infrastructure-triage.md` — flag for archive on next refresh.
- `~/projects/codebase-map/domains/operations.md`.
