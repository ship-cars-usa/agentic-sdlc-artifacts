---
repo: archiver
path: ~/projects/ship-cars-usa/archiver
stack: Java 17 / **Quarkus 2.9.1.Final (2022 — three majors behind fleet HEAD)** / Maven multi-module (6 poms)
domain: platform
shape: legacy archival service (Quarkus 2.9 — fleet major-version laggard)
last-synced-commit: 7da7ca5eaaf6d8107a3b5f6f6bfe22f84018ce85
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# archiver

## What it is
**The fleet's oldest active Quarkus service** — **Quarkus 2.9.1.Final** (released March 2022). Three major Quarkus versions behind HEAD (3.27.0). Per the version-matrix this is one of the two major-version-laggard outliers (the other being `notification-orchestrator` on Quarkus 3.8.3). **Uses direct Quarkus dependency declarations** — does NOT import `shipcars-quarkus-bom`, so it's outside the BOM-bump cascade.

Multi-module (6 poms). Predecessor / sibling to `archival-service` (Quarkus 3.15.2) — `archival-service` is the newer reimplementation; this one is the original. Whether both are still deployed or `archival-service` has fully taken over is unclear from the catalog.

Last commit 2022-05-26 (`Updates java version from 11 to 17`) — **3+ years stale**. No further updates in the years since. **Strong archive-candidate** unless someone confirms it's still serving production traffic.

## How it fits

- **Standalone Quarkus deps** — no BOM-importing path; lives outside the fleet's normal version-bump cascade.
- **Pairs with:** `archival-service` (the modern successor) + `archival-data-verification` (Go verifier).

## Build / test / run
```
./build-native.sh
./build-dev.sh
```

## Don't-do-here / gotchas

- **P1 lifecycle item.** Quarkus 2.9.1.Final is EOL (Quarkus 2.x community support ended 2023). Same severity as `lead-parser` (Spring 2.1.4) and `rateengine` (Django 2.1.7).
- **No BOM import.** Bumping requires rewriting the Quarkus dependency block from scratch — won't be a `<dependencyManagement>` import fix. Confirm whether the bump is worth doing or whether retiring this service (in favor of `archival-service`) is the cleaner path.
- **3-year-stale.** Likely either still serving niche archival traffic OR retired-but-not-removed. Check helm chart status before any work here.
- **Recommendation:** drive a retire-or-bump decision. If retire, archive. If bump, plan for a 3-major-Quarkus migration.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/archival-service.md` — modern Quarkus 3.15.2 sibling / successor.
- `~/projects/codebase-map/repos/archival-data-verification.md` — Go verifier.
- `~/projects/codebase-map/repos/lead-parser.md` / `rateengine.md` / `platform-backend.md` — the other EOL-language lifecycle items.
- `~/projects/codebase-map/relations/quarkus-version-matrix.md` — quantifies this service as a fleet outlier.
- `~/projects/codebase-map/relations/infrastructure-triage.md` — flag for retire-or-bump decision.
- `~/projects/codebase-map/domains/platform.md`.
