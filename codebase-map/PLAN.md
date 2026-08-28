# Codebase Mapping System for `~/projects/ship-cars-usa/`

## Context

The user maintains 232 sibling git repos under `~/projects/ship-cars-usa/`. Their only existing map is `~/projects/PROJECTS_INDEX.md` (327 lines, one-line/repo by tech category, regenerated 2026-05-07). Earlier this session we surveyed 2025–2026 options for representing large polyglot codebases and recommended a 4-layer architecture: per-repo CLAUDE.md → architectural catalog (Backstage) → symbol xref (SCIP) → semantic embeddings, with a virtual-monorepo orchestrator on top.

This task **starts implementing that architecture** with a critical adjustment driven by user constraints:

- **No files may be added inside any of the 232 repos.**
- **No existing files at `~/projects/` may be modified** (PROJECTS_INDEX.md, the two recent quarkus review docs, `claude-agentic-use.md`, `clone_repos.sh` all stay untouched).
- A top-level `~/projects/CLAUDE.md` does **not** exist today, so creating one is an addition, not a modification.

These constraints invert the standard pattern: instead of distributing artifacts *into* each repo, we maintain **shadow** artifacts in a new central folder, indexed by repo name. Existing repos stay pristine; the map is independently versionable, regenerable, and movable.

The work is iterative — v1 lays the skeleton and seeds the **top 30 backend services**. Later sessions extend coverage, add Backstage-format YAMLs, hook up embeddings, etc. The plan therefore persists *with the work* (`codebase-map/PLAN.md`) so future Claude sessions resume cleanly.

## Goal of v1 (this session)

1. Create `~/projects/codebase-map/` skeleton (folders + scaffolding files + scripts + templates).
2. Create `~/projects/CLAUDE.md` — the orchestrator that points Claude at the map.
3. Create `~/projects/codebase-map/PLAN.md` — the persistent multi-session work plan (mirror of this file).
4. Seed shadow docs for the **top 30 backend services** (Java/Quarkus + Spring), grounded in real repo content.

## Hard constraints

- No edits to any existing file at `~/projects/`. Additions only.
- No files added inside `~/projects/ship-cars-usa/<repo>/`. All artifacts live under `~/projects/codebase-map/` and `~/projects/CLAUDE.md`.
- Plan persists in two places: this planning-session copy at `~/.claude/plans/pick-at-random-and-effervescent-aurora.md` and the permanent companion at `~/projects/codebase-map/PLAN.md`. They start identical; on future sessions the `codebase-map/PLAN.md` copy is canonical.
- All scripts use only `python3` (stdlib), `jq`, `rg`, and shell-out to `git`. No `node`, `yq`, `tree`, or `fd` (not installed).

## Target folder structure

```
~/projects/
├── PROJECTS_INDEX.md                  (existing, UNTOUCHED)
├── CLAUDE.md                          (NEW — orchestrator that routes Claude to the map)
├── codebase-map/                      (NEW — entire mapping system)
│   ├── README.md                      (what this is, how to use it, how to extend)
│   ├── PLAN.md                        (persistent multi-session work plan)
│   ├── repos/
│   │   ├── _index.md                  (alpha-sorted list of shadow docs that exist)
│   │   ├── aaag-integration.md
│   │   ├── ai-dashboard-backend.md
│   │   └── ... (30 files in v1; more added in later phases)
│   ├── domains/                       (logical-domain rollups — phase 4)
│   │   └── _placeholder.md
│   ├── catalog/                       (Backstage catalog-info.yaml shadows — phase 3)
│   │   ├── components/
│   │   └── _placeholder.md
│   ├── relations/                     (cross-cutting facts; seeded skeletons in v1)
│   │   ├── service-graph.md
│   │   ├── data-stores.md
│   │   └── ownership.md
│   ├── adr/                           (decisions about the *map itself*)
│   │   └── 0001-shadow-catalog-pattern.md
│   ├── workspaces/                    (VS Code multi-root workspaces, per domain)
│   │   ├── all-backend.code-workspace
│   │   └── README.md
│   ├── scripts/                       (regen / bootstrap / drift-check)
│   │   ├── bootstrap_repo_md.py
│   │   ├── drift_check.py
│   │   ├── verify_links.py
│   │   └── README.md
│   └── templates/
│       ├── repo.md.template
│       ├── domain.md.template
│       └── catalog-component.yaml.template
```

## Shadow doc format (`codebase-map/repos/<repo>.md`)

YAML frontmatter + structured Markdown body. Carries the content a per-repo CLAUDE.md would otherwise carry:

```yaml
---
repo: <repo-name>
path: ~/projects/ship-cars-usa/<repo-name>
stack: <tech>                       # e.g., "Java/Quarkus 3.10, Maven multi-module"
domain: <logical-domain>            # e.g., "payments"; "unassigned" if not yet mapped
shape: <single-module|multi-module>
last-synced-commit: <git rev-parse HEAD at sync time>
last-synced-date: <YYYY-MM-DD>
maintainer: <unknown|team-name>     # placeholder until ownership phase
status: seed|stub|verified|stale    # seed=hand-authored from review; stub=auto-thin; verified=human-reviewed; stale=drift detected
---

# <repo-name>

## What it is
<one-paragraph what-and-why>

## How it fits
- Consumes API of: <repos>
- Publishes events to: <repos / Kafka topics>
- Owns data store: <Postgres schema | Mongo collection | none>

## Build / test / run
<commands>

## Key abstractions
- `<symbol>` — `<file path inside repo>` — <one-line>

## Don't-do-here / gotchas
- <items>

## Relevant ADRs / docs
- <pointers, including back to ~/projects/quarkus-fleet-review-2026-05-07.md when applicable>
```

## Selection criteria for the top 30 backend services

Pick from `PROJECTS_INDEX.md` Java/Quarkus (65) + Java/Spring (5–6) sections, in priority order:

1. **The 7 already-reviewed services** (we have material): `aaag-integration`, `ai-dashboard-backend`, `bi-databricks-backend`, `chat-backend`, `contract-pricing-backend`, `integrations-backend`, `integrators-data-bridge`.
2. **Core-domain services identified by name** in `PROJECTS_INDEX.md` — those whose names indicate central business roles: payments-*, auction-*, listing-*, user-*, auth-*, ordering-*, `notification-backend`, `quote-manager-backend`, `lead-parser`, `autoims-backend`, `spring-commons`.
3. **Most-recently-touched among remaining backend repos** — break ties using `git -C <repo> log -1 --format=%ct` (commit timestamp) to favor active services.
4. Stop at 30.

The final selected list is written into `codebase-map/PLAN.md` for traceability before any shadow doc is created.

## Per-repo seeding methodology

For each of the 30 selected repos:

1. **Read the repo top-level**: `pom.xml` (root + each module if multi-module), `application.properties` / `application.yaml`, the README if present, a representative `*Resource.java` and `*Service.java`, the Dockerfile.
2. **Fill the template** from observed code, NOT speculation. Mark `unknown` / `unassigned` for things not visible; never fabricate.
3. **Pull from existing review material** for the 7 already-reviewed services (`~/projects/quarkus-fleet-review-2026-05-07.md`, `~/projects/quarkus-rest-client-timeout-anti-pattern.md`) — these are the highest-quality seeds.
4. Set `status: seed` for the 7 review-derived files; `status: stub` for the other 23 (faster pass, lower depth — better than nothing, signals where deeper passes are still needed).
5. Capture `last-synced-commit` via `git -C <repo> rev-parse HEAD` at the moment of writing each shadow.

Realistic time budget per repo at this depth: 15–25 min for stubs, 30–45 min for the 7 seeds. Total v1 effort: ~10–15 focused hours, parallelizable across multiple Claude sessions if needed.

## Top-level `~/projects/CLAUDE.md` (orchestrator)

Concise (~150 lines). Tells Claude Code:

- The 232-repo layout (mirrors `codebase_layout.md` memory but explicit at this entry point).
- **Read first**: for any repo with a `codebase-map/repos/<repo>.md` shadow, read that BEFORE diving into the repo source. It's the authoritative summary.
- **Fall back** to `PROJECTS_INDEX.md` for repos without a shadow yet (most repos in v1).
- For "who calls whom" questions, consult `codebase-map/relations/service-graph.md`.
- For domain context, consult `codebase-map/domains/<domain>.md` (populated phase 4+).
- Before trusting a shadow that hasn't been resynced recently, run `python3 codebase-map/scripts/drift_check.py <repo>` and re-read the source if drift is reported.
- The map is in active iteration — partial coverage is normal; absence of a shadow is not a bug in v1.

## Scripts (Python 3 stdlib + git shell-out)

- **`bootstrap_repo_md.py <repo-name>`** — given a repo name, populate a stub shadow doc by parsing `pom.xml` (root only), `application.properties`, and grepping for module declarations. Output goes to `repos/<repo>.md` with `status: stub`.
- **`drift_check.py [<repo>|--all]`** — for each shadow, compare its frontmatter `last-synced-commit` to the current `git -C <path> rev-parse HEAD`. Mark drift in stdout; with `--mark-stale` flag, update frontmatter `status: stale` in place.
- **`verify_links.py`** — lint pass: every shadow's `path` field exists; no duplicate `repo:` keys; no broken `[…](…)` cross-references; `_index.md` matches the actual file list.

All three are <200 lines each, no external deps.

## Templates

- **`repo.md.template`** — the YAML+Markdown skeleton above with `<>` placeholders and a comment block at the top explaining each field.
- **`domain.md.template`** — for phase 4: name, member services, key flows, key data stores, on-call rotation, ADRs.
- **`catalog-component.yaml.template`** — Backstage v1 Component schema (kind, metadata, spec.type, spec.lifecycle, spec.owner, spec.dependsOn, spec.providesApis). Unused in v1 but documents the eventual phase 3 shape.

## ADR 0001 — Shadow Catalog Pattern

A 1-page ADR recording **why** we chose centralized shadow docs over per-repo CLAUDE.md, the tradeoff (drift risk vs. clean repos), and the migration path if the constraint is later relaxed (a script to push shadow content into per-repo CLAUDE.md). This documents the inversion for future-us.

## Critical files to create in v1 (~50 files total)

| Path | Purpose |
|---|---|
| `~/projects/CLAUDE.md` | Orchestrator (~150 lines) |
| `~/projects/codebase-map/README.md` | What this is, how it's organized |
| `~/projects/codebase-map/PLAN.md` | Persistent plan (mirror of this file) |
| `~/projects/codebase-map/templates/repo.md.template` | Shadow doc skeleton |
| `~/projects/codebase-map/templates/domain.md.template` | Domain rollup skeleton |
| `~/projects/codebase-map/templates/catalog-component.yaml.template` | Backstage Component schema |
| `~/projects/codebase-map/scripts/bootstrap_repo_md.py` | Auto-stub a repo |
| `~/projects/codebase-map/scripts/drift_check.py` | Detect divergence between shadow and repo HEAD |
| `~/projects/codebase-map/scripts/verify_links.py` | Lint shadows + cross-refs |
| `~/projects/codebase-map/scripts/README.md` | How to run each script |
| `~/projects/codebase-map/adr/0001-shadow-catalog-pattern.md` | Records the design choice |
| `~/projects/codebase-map/workspaces/all-backend.code-workspace` | VS Code multi-root for backend domain |
| `~/projects/codebase-map/workspaces/README.md` | Workspace usage |
| `~/projects/codebase-map/relations/service-graph.md` | Skeleton — populated incrementally |
| `~/projects/codebase-map/relations/data-stores.md` | Skeleton |
| `~/projects/codebase-map/relations/ownership.md` | Skeleton |
| `~/projects/codebase-map/domains/_placeholder.md` | Marks the dir; explains phase 4 fills it |
| `~/projects/codebase-map/catalog/_placeholder.md` | Marks the dir; explains phase 3 fills it |
| `~/projects/codebase-map/repos/_index.md` | Alpha index of existing shadows |
| `~/projects/codebase-map/repos/<repo>.md` × 30 | The seeded shadow docs |

## Verification (run from `~/projects/`)

1. **Structure exists:** `ls codebase-map/` shows all expected subfolders; `find codebase-map -type f | wc -l` reports ~50.
2. **Shadow lint passes:** `python3 codebase-map/scripts/verify_links.py` exits 0 (no broken refs, no missing frontmatter fields, no `path` pointing at a nonexistent repo).
3. **Drift baseline clean:** `python3 codebase-map/scripts/drift_check.py --all` reports 0 drifted (true at creation time).
4. **Manual sanity:** `cat codebase-map/repos/_index.md` lists exactly 30 entries; spot-check 3 shadow docs against actual repo content for accuracy (esp. the 7 review-seeded ones — they should match the fleet review).
5. **Orchestrator works:** open a fresh Claude Code session in `~/projects/`, ask "what is `chat-backend`?" — answer should reflect the shadow doc (Spring Boot 3.2.12, etc.) without re-grepping the repo.
6. **Constraint compliance:** `find ~/projects/ship-cars-usa -type f -newer ~/projects/codebase-map/PLAN.md | head` returns nothing inside repo folders. None of `PROJECTS_INDEX.md`, `quarkus-fleet-review-2026-05-07.md`, `quarkus-rest-client-timeout-anti-pattern.md`, `claude-agentic-use.md`, `clone_repos.sh` have been modified (mtime check).

## v1 selected services (executed 2026-05-08)

The 30 backend repos chosen for v1 seeding, in the priority order from the Selection criteria above:

**Tier 1 — already reviewed (7):**
1. aaag-integration
2. ai-dashboard-backend
3. bi-databricks-backend
4. chat-backend *(Spring Boot — PROJECTS_INDEX.md miscategorizes under Quarkus)*
5. contract-pricing-backend
6. integrations-backend
7. integrators-data-bridge

**Tier 2 — Spring services (all 5, named-as-core):**
8. autoims-backend
9. lead-parser
10. notification-backend
11. quote-manager-backend
12. spring-commons

**Tier 2 — Quarkus core-domain by name (12):**
13. payment-backend
14. user-backend
15. inventory-backend
16. loadboard-backend
17. loadbuilder-backend
18. driveaway-backend
19. posting-backend
20. attachment-backend
21. public-tracking-backend
22. notification-orchestrator
23. invoices
24. fraud-detector

**Tier 2 — heavily-shared Quarkus libraries / BOM (3):**
25. quarkus-commons
26. commons
27. shipcars-quarkus-bom

**Tier 3 — active services to round to 30 (3):**
28. load-recommender
29. trip-planner
30. user-activity-tracker

The 7 in Tier 1 receive `status: seed` (deepened from review material). The other 23 are `status: stub` (frontmatter accurate, body placeholder) and are deeper passes for future sessions.

---

## Phase status (updated 2026-05-08)

| Phase | Status | Notes |
|---|---|---|
| v1 — skeleton + 30 backend seeds/stubs | **done 2026-05-08** | 7 seeds, 23 stubs |
| Phase 2 — wide coverage | **done 2026-05-08** | All 232 repos now have shadow docs (7 seed, 225 stub). `bootstrap_repo_md.py` was extended to detect Spring Boot before Quarkus, frontend vs. node, terraform live envs / modules, helm, mobile, browser-ext, docs. `gen_index.py` script added; `_index.md` is now generated, not hand-edited. |
| Phase 3 — catalog YAMLs | **deferred** | Premature without Backstage actually deployed; the `catalog-component.yaml.template` documents the eventual shape. Revisit when Backstage is on the table. |
| Phase 4 — domains + service graph | **done 2026-05-08** | 9 domains: `listings-trade`, `pricing-billing`, `operations`, `integrations`, `identity`, `communication`, `analytics`, `platform`, `infrastructure`. Each shadow's `domain:` frontmatter is assigned via name-pattern rules. 9 rollup files in `domains/`. `relations/service-graph.md` populated from the 7 seed shadows (24 edges; the rest grow as more shadows reach `seed`). |
| Phase 5 — semantic layer | **deferred 2026-05-08** | User chose to defer until a specific question demonstrates grep is insufficient. Revisit when that question shows up. |
| Phase 6 — drift CI | **done 2026-05-08** | `scripts/run-drift-check.sh` wraps `drift_check.py --all --mark-stale` and appends to `relations/drift-log.md`. launchd plist at `~/Library/LaunchAgents/cars.codebase-map.drift.plist` runs it Mondays 09:00. **Note:** `launchctl load` is sandbox-blocked from this session — user must run it once: `launchctl load ~/Library/LaunchAgents/cars.codebase-map.drift.plist`. Manual seed run already populated drift-log.md (0 drifted at baseline). |
| Phase 7 — constraint kept | **decided 2026-05-08** | No-files-in-repos constraint re-confirmed. See `adr/0002-keep-no-files-in-repos-constraint.md`. Closes Phase 7 as a question. |

## Phase 2 outcome (extras worth recording)

- Stack distribution across the full fleet of 232: 34 React/Vite frontends, 30 Docs/Markdown, 28 Quarkus 3.27.0, 27 Python, 18 unknown (mostly empty placeholders or oddballs), 12 Go, 10 Spring Boot 3.2.12, 10 Terraform live env, 10 Quarkus 3.20.2.2, plus the long tail.
- The detector now correctly handles 7 archetypes (Spring/Quarkus/Frontend/Node/Python/Go/Terraform/Helm/Mobile/Browser-ext/Docs); 18 repos still come back `unknown`, mostly because they're empty placeholders (`kubernetes/`, `terraform/`) or repos with no recognizable manifest at any depth.
- Drift baseline is clean across all 232 (`drift_check.py --all` reports 0 drifted, with empty-placeholder shadows handled via the `last-synced-commit: unknown` convention added during Phase 2).

## Phase 4 outcome (extras worth recording)

- **9-domain taxonomy** (renamed from the narrower seed-domain choices): `listings-trade`, `pricing-billing`, `operations`, `integrations`, `identity`, `communication`, `analytics`, `platform`, `infrastructure`.
- Largest two domains by repo count: `infrastructure` (68) and `platform` (56). Together they hold half the fleet — most of the rest splits across the 7 product domains.
- The `_placeholder.md` in `domains/` was removed (now superseded by the 9 real rollup files).
- `relations/service-graph.md` has 24 edges from the 7 seed shadows. Notable observations: `notification-backend`, `user-backend`, `media-proxy`, `impersonator`, `location-provider` are the most-called platform services even on a 7-shadow sample → highest blast-radius failures in the fleet. `integrators-data-bridge` reads directly from 4 source Postgres DBs, bypassing the source services' API contracts ("shadow caller"). No Kafka edges in the seed sample — confirm whether Kafka is actually used by `rg "@Incoming|@Outgoing|@Channel" --type java`.

## Phase 6 outcome

- Wrapper: `scripts/run-drift-check.sh` (bash, idempotent header on first run, exit code matches `drift_check.py`).
- Launchd plist: `~/Library/LaunchAgents/cars.codebase-map.drift.plist` (Weekday=1, Hour=9, Minute=0; `RunAtLoad: false`; absolute paths to `/bin/bash` and `/usr/bin/python3`).
- Validated with `plutil -lint` (clean).
- Stdout/stderr captured to `relations/drift-launchd.{out,err}` (separate from the `drift-log.md` content log).
- **Activation step left to the user:** `launchctl load ~/Library/LaunchAgents/cars.codebase-map.drift.plist` (sandbox-blocked from this session).
- Verify after loading: `launchctl list | grep cars.codebase-map`.
- To remove: `launchctl unload ~/Library/LaunchAgents/cars.codebase-map.drift.plist && rm ~/Library/LaunchAgents/cars.codebase-map.drift.plist`.

## Phase 7 outcome — constraint kept

User re-confirmed the no-files-in-repos rule on 2026-05-08, after the shadow catalog was working at full coverage. ADR `adr/0002-keep-no-files-in-repos-constraint.md` records this so future sessions don't naively migrate shadows into per-repo CLAUDE.md files. The migration recipe still lives in ADR 0001 if the decision is ever reversed.

## What's next

The plan's structural phases are now closed (v1, 2, 4, 6) or explicitly deferred/decided (3, 5, 7). The remaining work is *content depth*, not structure:

- Promote stubs to seeds where it matters most. The "highest-leverage next deepening passes" list above (Phase 4.5) is the recommended priority order.
- Clean up the `infrastructure` domain — 68 stubs include several known typos and duplicates and probably some archive candidates. A single triage pass (output: a Markdown table of `active | archive-candidate | unsure`) is much higher value than 68 deepening passes.
- Re-run `gen_index.py` after any add/rename of shadow docs.
- Re-confirm Phase 5 if/when a specific question shows up that grep + the shadow catalog can't answer well.

## Depth pass 1 — done 2026-05-08

Seeded 7 more shadows (now **14 seeds, 218 stubs, 232 total**):

- `quarkus-commons` (platform) — captures the systemic absence of fleet-wide REST-client timeout / retry-jitter defaults; this is where the highest-leverage cross-cutting fix should land.
- `spring-commons` (platform) — documents `WebClientImpl`, `GlobalExceptionHandler`, the canonical `PubSubConsumer` template, and the dependency-pinning surface (Spring Boot 3.2.12, Hibernate 6.6.37, Flyway 9.22.3).
- `user-backend` (identity) — system-of-record; outbox + ShedLock pattern; consumes payment-backend Stripe events. Confirmed cyclic edge with notification-backend.
- `notification-backend` (communication) — fan-out to SendGrid/Twilio/Firebase; **silent ack on exception** P0 in `NotificationConsumer.java:126`; HikariCP pool=5 hardcoded.
- `media-proxy` (platform) — Go service; opaque-token auth (no JWT signing); no per-route HTTP timeout (combines with chat-backend's synchronous call to produce stalled threads under slow GCS).
- `impersonator` (identity) — Go service; **no `http.Client.Timeout`** P0; no audit log of impersonations.
- `location-provider` (operations) — Quarkus 3.27.0 façade over Google Maps; no Maps-client timeout configured; `route_distance` PG with `max-size=4`.

The 14-seed service graph (`relations/service-graph.md`) now shows `user-backend` as the most-called REST callee (4 inbound edges) and reveals a `user-backend ↔ notification-backend` cycle (REST one way, Pub/Sub fan-out the other) worth flagging in incident response.

## Depth pass 1 — infrastructure triage done 2026-05-08

`relations/infrastructure-triage.md` classifies all 68 `infrastructure` shadows:

| Classification | Count | Action |
|---|---|---|
| **active** | 33 | safe to rely on |
| **archive-candidate** | 12 | typo'd duplicates, `_ARCHIVED` / `DEPRECATED`, hackathon repos, empty placeholders |
| **unsure** | 23 | needs human eyes — mostly AI-tooling experiments and stale dev-tooling |

The 12 archive-candidates are the cleanest single-pass cleanup win — drop them and the `infrastructure` count goes from 68 to 56, which makes the domain much easier to reason about.

## Depth pass 2 (Phase 4.6) — done 2026-05-08

Seeded 6 more shadows (now **20 seeds, 212 stubs, 232 total**):

- `payment-backend` (pricing-billing) — Quarkus; Stripe webhooks + RoadSync; `@Retry(7×)` without `@Timeout` on both REST clients; Stripe event-source feeding `user-backend.PaymentBackendConsumer`.
- `quote-manager-backend` (pricing-billing) — Spring Boot; **state facade**, not the canonical pricing engine; uses `WebClientImplFactory` with `retryMaxAttempts=3` but no timeouts; no outbox; consumes `quote-receive-state`, publishes `quote-send-state` / `quote-notification`.
- `loadboard-backend` (listings-trade) — Quarkus 3.27.0; **3 PostgreSQL databases** (primary + users + ctms); Temporal-orchestrated workflows; ID-only read path (search lives in CTMS).
- `inventory-backend` (listings-trade) — Spring Boot; Temporal for CSV/batch; **direct-PG-read consumer in `integrators-data-bridge` is invisible**; no inventory-mutation Pub/Sub topic observed.
- `posting-backend` (listings-trade) — Spring Boot; **the only fleet client with explicit timeouts** (`ShipcarsLoadBoardClientImpl`, read=PT150S, connect=PT60S); ShedLock-based outbox; densest dependency fan-out in the graph (12+ outbound REST edges).
- `notification-orchestrator` (communication) — Quarkus 3.8.3 (**fleet-stale**, behind 3.20.x/3.27.x peers); **does not call `notification-backend`** — they're parallel email-paths to SendGrid, not a stack; uses `db-syncer` to replicate user/company state locally.

## Phase 4.6 — REST-client registry built (`relations/rest-client-registry.md`)

Quantitative confirmation of the systemic risk from the fleet review:

- **36** Quarkus `@RegisterRestClient` declarations across **15** repos.
- **3** have at least one of `connect-timeout` / `read-timeout` configured.
- **33** have **NEITHER** timeout configured anywhere — exposed to the retry-without-timeout cascade if the same client also has `@Retry`.

Spring services (10 in the fleet) use `spring-commons.WebClientImpl` instead, with timeouts set programmatically. **Only `posting-backend.ShipcarsLoadBoardClientImpl` actually sets them** — every other Spring REST call site falls back to whatever `WebClientImpl` defaults to.

This makes a single-line baseline change in `quarkus-commons` (publish a `quarkus.rest-client.<key>.connect-timeout` / `read-timeout` defaults file consumed via `quarkus.config.locations`) the highest-leverage fleet-wide fix available. The change retires risk #1 from `~/projects/quarkus-fleet-review-2026-05-07.md` and brings 33 services into a defensible posture in one commit.

## 20-seed service-graph highlights

After Phase 4.6, `relations/service-graph.md` confirms:

- **`user-backend` is the highest-blast-radius callee in the fleet** with 6 inbound REST edges (chat-backend, contract-pricing-backend, notification-backend, impersonator, payment-backend, quote-manager-backend).
- **`posting-backend` is the densest node** — 12+ outbound REST edges + 7 inbound Pub/Sub subscriptions + 4 outbox-published topics.
- **No Kafka edges yet** across 20 seeds. Pub/Sub remains the sole async pattern.
- **Notification topology is now clarified**: `notification-backend` and `notification-orchestrator` are parallel SendGrid-bound services, not a stack. Boundary needs an explicit owner decision.

## Recommended next deepening passes (Phase 4.7, optional)

1. **Make the highest-leverage fleet-wide fix.** Publish a `quarkus-commons` baseline-properties module that sets default `connect-timeout` and `read-timeout` for every `quarkus.rest-client.*`. 33-of-36 exposure → 0 in one well-tested release.
2. **Resolve the `notification-backend` ↔ `notification-orchestrator` boundary.** Owner decision + a 1-page note. Action falls on the comms team.
3. **Resolve `infrastructure-triage.md` `unsure` set** with one-line decisions per repo (23 rows). Best done alongside whoever owns dev tooling.
4. **Remaining listings-trade depth**: seed `load-recommender`, `saved-search-handler`, `load-bookmark-backend`, `load-bookmark-service`. The recommender path is currently a black box from the seed-only graph.
5. **Remaining pricing-billing depth**: seed `invoices`, `fraud-detector`, `autoims-backend`, `lead-parser`. `lead-parser` on Spring Boot 2.1.4.RELEASE is a security/EOL flag worth a dedicated seed pass.
6. **Resolve `impersonator`'s `company-owner-api` / `user-api` ambiguity** — confirm whether they both resolve to `user-backend` or whether `company-owner-api` is a distinct service. Either way, write the answer into `impersonator`'s shadow.

## Depth pass 3 / Phase 4.7 — done 2026-05-11

Seeded 8 more shadows + closed the `impersonator` company-owner-api / user-api ambiguity (now **28 seeds, 204 stubs, 232 total**):

**listings-trade depth (4 seeds):**
- `load-recommender` (Quarkus 3.27.0) — ML-recommendation path; subscribes to `ml-recommender-subscription` + `ctms-subscription`; pushes to `notification-orchestrator` via `notifications-topic`; no REST-client timeouts.
- `saved-search-handler` (Quarkus 3.27.0) — Elasticsearch **percolate** pattern; 3 datasources (main + users + ctms); `LoadEventProcessor` batches via `@Scheduled`; silent-ACK on non-match needs review.
- `load-bookmark-backend` (Quarkus 3.27.0) — JVM-side bookmark API. **HikariCP `max-size=4` in prod** (extreme outlier; raise to 16+).
- `load-bookmark-service` (Python 3.10 / FastAPI) — etcd sidecar. **`eval()` on etcd values (P0 security)** and **always-ACK on Pub/Sub (P0 correctness)**. Replace `eval` with `json.loads`; gate ACK on success.

**pricing-billing depth (3 seeds) + operations (1 seed):**
- `invoices` (Quarkus 3.20.2.2) — carrier/customer invoice lifecycle; revision tracking via `latest` flag; 4 REST clients all without timeouts; `@Retry` on PaymentClient without `@Timeout`.
- `fraud-detector` (Quarkus 3.15.2) — risk scoring; **`VehicleClient.baseUri` hardcoded to `https://done.ship.cars`** (not env-overridable); two minors behind fleet.
- `autoims-backend` (Spring Boot 3.2.12) — AutoIMS sync. **One of only two Spring services that actually sets WebClient timeouts** (via `AutoImsWebClientFactory`). `@Scheduled` without ShedLock = concurrent runs on multi-replica deploys.
- `lead-parser` (**Spring Boot 2.1.4.RELEASE / Java 8 — EOL since 2019**) — single biggest lifecycle/security flag in the fleet. Raw `new RestTemplate()`, no timeouts, silent 200-OK on downstream failure. Replace-not-patch.

**Resolved ambiguity:**
- `impersonator`'s `company-owner-api` and `user-api` env-vars both resolve to **`user-backend`** (`/internal/v2/companies/{id}/owner` and `/internal/v2/users/{id}` respectively, verified against `V2InternalCompanyController` + `V2InternalUserAccountController`). Open question retired; impersonator shadow updated; service-graph rows now point to `user-backend` definitively.

**Service-graph delta:** +33 edges (now ~128 total). `user-backend` inbound REST edges grew from 6 to 8 (added `invoices`; impersonator now counts twice via two distinct routes). `posting-backend` is now confirmed as the densest both-directions node — every listings-trade seed touches it.

## Phase 4.7 priorities — status

1. ~~Make timeout-baseline fix in `quarkus-commons` (highest-leverage; 33→0 exposure)~~ — **deferred**: violates no-files-in-repos constraint.
2. ~~Resolve `notification-backend` ↔ `notification-orchestrator` boundary~~ — **still open**: needs comms team.
3. ~~Walk 23 `unsure` rows in `infrastructure-triage.md`~~ — **still open**: needs dev-tooling owner.
4. ~~Continue depth: `load-recommender`, `saved-search-handler`, `invoices`, `fraud-detector`, `autoims-backend`, `lead-parser` (Spring Boot 2.1.4 EOL flag)~~ — **done 2026-05-11** as above (plus `load-bookmark-backend` and `load-bookmark-service` for listings-trade completeness).
5. ~~Resolve `impersonator`'s `company-owner-api` / `user-api` ambiguity~~ — **done 2026-05-11**: both → `user-backend`.

## Recommended next deepening passes (Phase 4.8, optional)

1. **Two P0 fixes from depth-pass 3 that the user can act on without violating the constraint** (these are user-actionable on the actual repos, not catalog edits):
   - `load-bookmark-service`: replace `eval(bookmark_info)` with `json.loads(...)` (2-line PR; eliminates RCE risk on a compromised etcd).
   - `lead-parser`: at minimum, configure `RestTemplate` with `SimpleClientHttpRequestFactory` timeouts (5 s connect / 10 s read). Larger ask: stand up a Quarkus 3.27.0 replacement.
2. **Communication-domain depth**: seed `notification-state-syncer`, `chat-state-syncer`, `email-aggregator` (whichever exist). The current 3 seeds (chat-backend, notification-backend, notification-orchestrator) leave the parallel-paths question unanswered.
3. **Identity-domain depth**: seed `user-state-syncer`, `keycloak-event-handler`, any company-management subservices. With user-backend already deep, the rest of identity should be a fast pass.
4. **Operations-domain depth**: 19 stubs, 1 seed (location-provider). Pick 3 highest-traffic services (likely `driveaway-backend`, `public-tracking-backend`, `trip-planner`).
5. **Tighten `data-stores.md`**: 28 seed shadows now have datastore details. Roll them into a single comparison table (service → engine → schema → pool size → audit-table presence). Easy single-pass win.
6. **Re-domain `autoims-backend`** from `pricing-billing` to `integrations` — it's an AutoIMS integration shim, not a billing service. Trivial frontmatter edit + service-graph cross-ref update.

## All deepening history (chronological)

1. **v1 (2026-05-08)** — 7 seeds from the fleet review: `aaag-integration`, `ai-dashboard-backend`, `bi-databricks-backend`, `chat-backend`, `contract-pricing-backend`, `integrations-backend`, `integrators-data-bridge`.
2. **Depth pass 1 (2026-05-08)** — +7 seeds: `quarkus-commons`, `spring-commons`, `user-backend`, `notification-backend`, `media-proxy`, `impersonator`, `location-provider`. Plus `infrastructure-triage.md`.
3. **Depth pass 2 / Phase 4.6 (2026-05-08)** — +6 seeds: `payment-backend`, `quote-manager-backend`, `loadboard-backend`, `inventory-backend`, `posting-backend`, `notification-orchestrator`. Plus `rest-client-registry.md`.
4. **Depth pass 3 / Phase 4.7 (2026-05-11)** — +8 seeds: `load-recommender`, `saved-search-handler`, `load-bookmark-backend`, `load-bookmark-service`, `invoices`, `fraud-detector`, `autoims-backend`, `lead-parser`. Plus impersonator company-owner-api resolution and +33 service-graph edges. **Two new P0 flags surfaced**: `load-bookmark-service.eval()` (RCE) and `lead-parser` Spring Boot 2.1.4 (EOL).
5. **Depth pass 4 / Phase 4.8 (2026-05-11)** — +7 seeds: `driveaway-backend`, `public-tracking-backend`, `trip-planner`, `user-activity-tracker`, `attachment-backend`, `metadata`, `rateengine`. Plus `autoims-backend` re-domained `pricing-billing` → `integrations`; `user-activity-tracker` re-domained `identity` → `analytics`. Built `relations/data-stores.md` from all 35 seeds. New P0 surfaced in `rateengine` (Django 2.1.7 + DRF 3.8.2 + `requests.Session()` no-timeout — second-biggest fleet lifecycle flag after `lead-parser`).
6. **Depth pass 5 / Phase 4.9 (2026-05-11)** — +9 seeds: `axe-call-integration`, `integration-executor`, `quarkus-user-syncer`, `syncer`, `synclink-backend`, `webhook-relay`, `pusher`, `socket-server`, `quarkus-notification-client`. Plus re-domains: `synclink-backend` (operations→integrations) and `webhook-relay` (platform→integrations).
7. **Depth pass 6 / Phase 4.10 (2026-05-11)** — +8 seeds: `keycloak`, `keycloak-events-plugin`, `keycloak-password-reset-link`, `hasher`, `ml-service-listener`, `ml-service-dispatcher`, `ml-service-recommender`, `loadbuilder-backend`. Plus `adr/0003-cross-service-db-read-policy.md` (proposed policy on direct cross-service DB reads).
8. **Depth pass 7 / Phase 4.11 (2026-05-12)** — +6 seeds: `keycloak-mfa-plugin`, `keycloak-phone-login-plugin`, `ml-bot-order-v2`, `ml-demand-forecasting`, `ml-document-parser`, `company-documents`. Plus 2 ADR-0003 contract-doc starters in `relations/db-contracts/`, `pricing-billing` domain note resolving the rateengine / ml-service-dispatcher boundary, and `ml-bot-order-v2` re-domained `pricing-billing` → `integrations`.
9. **Depth pass 8 / Phase 4.12 (2026-05-12)** — +4 seeds: `ml-bot-order` (v1), `ml-model-rate`, `uship-quotes`, `ml-pricing-app`. Plus 5 more ADR-0003 contract drafts (`autoims-backend`, `contract-pricing-backend`, `syncer-multi-source`, `pusher--user-and-ctms-dbs`, `ml-demand-forecasting--source-pg`), `adr/0004-firebase-dynamic-links-migration.md`, `adr/0005-rateengine-eol-rewrite.md`. Re-domains: `ml-bot-order` → integrations; `ml-pricing-app` → analytics. **Two new shadow-caller edges surfaced** (`ml-pricing-app` → MONTWAY MySQL + RATE_ENGINE PG).
10. **Depth pass 9 / Phase 4.13 (2026-05-12)** — +6 seeds: `api-gateway`, `dataone`, `cube`, `location-history-backend`, `negotiations-router`, `apache-camel-etl-demo`. Plus the 8th ADR-0003 contract draft (`ml-pricing-app--montway-and-rate-engine`), ADR-0006 (`ml-bot-order` v1 retirement), and re-domain `cube` → listings-trade.
11. **Depth pass 10 / Phase 4.14 (2026-05-12)** — +4 seeds: `ml-service-chat`, `ml-ui-chat`, `chat-frontend`, `socket-server-old`. **Communication domain reaches catalog-complete coverage** (10 seeds / 12 total; remaining 2 are devops repos). Two P0 findings: hardcoded JWT secret in git for `socket-server-old` across all environments, and `openai==1.30.1` + legacy `ChatCompletion.acreate` incompatibility in `ml-service-chat`. **One new shadow-caller edge** (`ml-service-chat` → `rateengine.production` PG — now 15 total). New parallel-Redis WebSocket topology fact (socket-server and socket-server-old run on different Redis clusters).
12. **Depth pass 11 / Phase 4.15 (2026-05-12)** — +4 platform-extension seeds: `commons`, `quarkus-extension-webclient`, `quarkus-pubsub`, `quarkus-extension-persistence`. **Compile-time fanout numbers quantified for the first time** (commons ~50+; quarkus-pubsub 29; quarkus-extension-persistence 14; quarkus-extension-webclient 9). Key structural insight: **the REST-client-timeout gap is a path choice, not a config choice** — 9 services use `WebClientImpl` (safe-by-default), ~30 use `@RegisterRestClient` (silent-by-default). The fleet hasn't picked a canonical path. Correction recorded: `quarkus-extension-persistence` does **not** carry Hikari pool defaults, so the pool-size outliers can't be fixed centrally. Two long-standing open questions retired (commons-split semantics; cube/dataone purpose).
13. **Depth pass 12 / Phase 4.16 (2026-05-12)** — +2 seeds closing the Java-commons-shared-library group: `shipcars-quarkus-bom` (BOM pinning Quarkus 3.27.0 + Java 21 + 6 Quarkiverse extensions; ~40+ consumers; **does NOT pin Ship.Cars extensions** — silent BOM-vs-extension version drift) and `models-lib` (`1.144.0-SNAPSHOT`; 17 fleet consumers; 5 modules: data-models / api-dtos / read-models / converters / ml-dtos; heaviest reader is the ES-indexing pipeline `syncer`/`cube`/`saved-search-handler`; `ml-dtos` is the rateengine Java-side contract). **Java compile-time substrate is now fully catalogued** (7 of 7 fleet-cross-cutting Java commons artifacts + Quarkus extensions). Platform domain coverage 11 → 13 of 54.
14. **Depth pass 13 / Phase 4.17 (2026-05-12)** — built **`relations/quarkus-version-matrix.md`**: row-per-service view of BOM + Quarkus platform + 5 Ship.Cars-extension + `commons` + `models-lib` version pins for all 34 Quarkus services in the fleet. No new seeds. **Quantifies the BOM-vs-extension drift hypothesis from 4.16**: 16 services on Quarkus 3.27.x (HEAD), 18 on 5 older minor versions; `notification-orchestrator` (3.8.3) + `archiver` (2.9.1.Final) are the two major-version laggards (both bypass the BOM, both belong on the P1 lifecycle list alongside `lead-parser` + `rateengine`); `commons` drift is the biggest individual gap (most-common version is 3.22.1, six minors behind HEAD; no service on HEAD). Property naming is fleet-wide inconsistent. **Headline fix-once recommendation: pin Ship.Cars extensions in the BOM itself** to eliminate the silent-drift class entirely.
15. **Depth pass 14 / Phase 4.18 (2026-05-12)** — +4 operations seeds: `home-delivery-backend` (Fastify dealer-widget proxy; **P0 hardcoded Montway tokens + Keycloak client secrets in git**), `quarkus-locationprovider-client` (Quarkus typed-client wrapper around `location-provider`; canonical 7-retry-no-timeout fleet pattern; 2 explicit consumers + others via direct `@RegisterRestClient`), `synclink-chrome-extension` (MV3 browser extension companion to `synclink-backend`; `HASHABLE_FIELD_PATHS` is a hard cross-repo contract; double-slash typo in prod/staging/qa sync URLs), `trip-planner-frontend` (single-spa MFE; same DOM-CustomEvent socket-bridge pattern as `chat-frontend`; **axios 0.21.1 has known CVEs**). Operations domain coverage 6 → 10 of 18.
16. **Depth pass 15 / Phase 4.19 (2026-05-12)** — +5 seeds closing **two domains to catalog-complete**: identity (`user-frontend` — `@shipcars/user` single-spa MFE with the broadest service-surface in the fleet; 9/9 identity shadows now seed) and integrations (`command-executor` — inbound Pub/Sub processor for 4 external platforms; `aaag-poc` — archive-candidate Python POC; `aaag-integration-logs-ARCHIVED` — already-archived log shipper; `devops-tf-live-shipcars-logytext-integration` — Terraform IaC for the Logytext integration, recommended for re-domain to `infrastructure`; 16/16 integrations shadows now seed). **Catalog now has 3 of 9 domains catalog-complete**: communication, identity, integrations.
17. **Depth pass 16 / Phase 4.20 (2026-05-12)** — +6 seeds closing **listings-trade** to catalog-complete: 4 active single-spa MFEs (`posting-frontend` + `inventory-frontend` on the **modern** single-spa-react 6 / webpack 5.10x / axios 1.15 / MUI 6.x generation; `loadboard-frontend` + `carrier-order-importer-frontend` on the **older** single-spa 5 / axios 0.21 generation) plus 2 hiring artifacts (`fe-exercise-inventory-api` + `fe-exercise-inventory-ui` — recommended re-domain to `infrastructure`). The seed pass surfaces the **single-spa generation drift** across the listings-trade MFEs (2 modern + 2 older + 1 mid-gen elsewhere). Listings-trade rollup gained a quantified data-stores table + a confirmed posting→loadboard→recommendation→match flow. **Catalog now has 4 of 9 domains catalog-complete**: communication, identity, integrations, listings-trade.
18. **Depth pass 17 / Phase 4.21 (2026-05-12)** — +6 seeds closing **pricing-billing** to catalog-complete: `contract-pricing-frontend` (modern single-spa-react 6 MFE, narrow `CONTRACT_PRICING_API` scope), `pricing-frontend-components-package` (Rollup-built shared FE library on MUI 5 peer — blocks adoption by MUI-6-generation MFEs), and the 4 sibling `ml-model-*` services (`-rate-confidence-absolute`, `-rate-confidence-percentage`, `-rate-multivehicle`, `-time-to-dispatch`). The first 3 ML models are templated identically to `ml-model-rate` (FastAPI / CatBoost / GCS-loaded artifacts / Datadog tracking); the 4th (`-time-to-dispatch`) is an **empty placeholder** — README + pyproject only, no source code, name-reservation only. Pricing-billing member list cleaned up (re-domains accumulated through earlier phases: `autoims-backend`, `ml-bot-order`, `ml-bot-order-v2`, `ml-pricing-app` were all in the original 19-member list; current actual count is 15). **Catalog now has 5 of 9 domains catalog-complete**: communication, identity, integrations, listings-trade, pricing-billing.
19. **Depth pass 18 / Phase 4.22 (2026-05-12)** — +8 seeds closing **operations** to catalog-complete: 3 modern single-spa MFEs (`public-tracking-frontend` — unusual two-build root+parcel repo for the standalone `public.ship.cars` deployment; `driveaway-public-tracking-frontend` — uses fleet-newest react-router 7.13; `chase-driver-tracking-frontend` — Loadmate-internal driver-tracking MFE), `asg-checkout-spa` (**Montway Checkout SPA on a 2017-era React 15 / Redux 3 / Node 5 stack** — P1 lifecycle item alongside `lead-parser` + `rateengine`), `epod-android` (Kotlin Clean-Architecture multi-module app, MVVM+Compose modern + MVP legacy), `epod-ios` (Swift Clean-Architecture counterpart, UIKit MVVM current + SwiftUI ready), `automation-epod-github-actions-test` (Appium Java cross-platform mobile-test framework, Jenkins-driven), and `ios-epod-github-actions-test` (empty-README iOS CI snapshot — **archive-candidate**). Operations rollup closed 3 long-standing open questions (`location-provider` ↔ `location-history-backend` topology; `chase-driver-tracking-frontend` vs public-tracking-* relationship; `epod-*-github-actions-test` archive status). **Catalog now has 6 of 9 domains catalog-complete**: communication, identity, integrations, listings-trade, pricing-billing, operations.
20. **Depth pass 19 / Phase 4.23 (2026-05-12)** — +4 platform-extension seeds quantifying the last load-bearing parts of the Quarkus substrate: `quarkus-request-filter` (**33 fleet consumers** — the fleet's per-request context-company / context-user → MDC + `ContainerRequestContext` layer, plus `ConstraintViolationExceptionMapper` and exception-to-`ErrorDto` translation); `quarkus-extension-media-proxy` (**13 fleet consumers, Quarkus + Spring** — one of the few cross-stack libraries; ships both Quarkus runtime and a sibling Spring client; **rare in the fleet for documenting timeout knobs in its README**); `quarkus-auto-reflection` (native-image reflection-config helper; 10+ consumers using `ship.cars.reflection.package-name[*]`, `command-executor` is the canonical example with 26 package entries); `quarkus-imperative-boilerplate` (**canonical clone-and-rename service template** that ~10+ fleet imperative-Quarkus services were derived from — `command-executor`, `axe-call-integration`, `integration-executor`, etc.). Platform domain coverage 13 → 17 of 54. **Quarkus-extension catalog now near-complete** (12 of 14 extensions / commons libs seeded; 4 trailing extensions left: `quarkus-data-migration`, `quarkus-extension-firestore-storage`, `quarkus-extension-bootstrap`, `quarkus-k8s-boilerplate`).
21. **Depth pass 20 / Phase 4.24 (2026-05-12)** — +15 seeds closing **analytics** to catalog-complete in a single big pass: 6 substantive Python ML services (`ai-testgen` — Claude + Jira + Figma test-case generator; `ml-data-hamal` — source-to-sink DB porter; `ml-experiments` — historical research repo; `ml-experiments-template` — canonical DVC+GCS+dev-container experiment template; `ml-lib-extraction` — well-documented async LiteLLM extraction library; `ml-model-training` — Jenkins-driven training pipeline producing artifacts for the `ml-model-*` family, **new shadow-caller edge to `rateengine` MySQL** — count now 16; `elk-backup-restore` — operational ELK snapshot/restore script), 2 frontends (`executive-dashboard-frontend`, `databricks-embedding-test`), 3 docs/archive (`ml-central-data-storage` — Databricks Asset Bundle config; `ml-notebooks-archive`; `ml-playground` — both archive-candidates), 3 Terraform live-envs (`devops-tf-live-shipcars-ml-data-{dev,staging,prod}` — all flagged for re-domain to `infrastructure`). **Catalog now has 7 of 9 domains catalog-complete**: communication, identity, integrations, listings-trade, pricing-billing, operations, analytics.
22. **Depth pass 21 / Phase 4.25 (2026-05-12)** — +4 seeds closing the **trailing Quarkus extensions** to bring the Quarkus-extension catalog to **14/14 complete**: `quarkus-data-migration` (Java-typed data-migration framework auto-running at startup; tracks versions via `DataMigrationVersionEntity`; **no active fleet consumers detected**), `quarkus-extension-firestore-storage` (typed `StorageClient` over GCP Firestore w/ versioned CRUD + optimistic concurrency + TTL; **1 confirmed consumer `command-executor`**), `quarkus-extension-bootstrap` (template repo for scaffolding new Ship.Cars Quarkus extensions; explains the shared multi-module `runtime + deployment + coverage-report` layout across the fleet's extensions), `quarkus-k8s-boilerplate` (lightweight single-module Quarkus service template; counterpart to the 9-module `quarkus-imperative-boilerplate`; optimized for 5-20-endpoint serverless / native-image services). Platform domain coverage 17 → 21 of 54. **Quarkus substrate now fully catalogued**: 14 of 14 extensions / commons libs / boilerplates at seed.
23. **Depth pass 22 / Phase 4.26 (2026-05-12)** — +8 seeds covering the **public-site shell + shared FE-package cohort**: `public-root-app-frontend` (single-spa root config for `public.ship.cars`, two-build standalone deploy), `public-common-frontend` (shared chrome parcel), `ui-commons` (fleet's largest standalone shared component library, Gulp-built, Storybook 7.6, MUI 5+ peer, version 1.16.18), `carrier-packages-frontend` (**Nx monorepo housing 4 published FE packages** — `globals-frontend-package`, `entities-frontend-package`, `ui-components-frontend-package`, `ctmslb-components-frontend-package`), plus the 4 standalone-repo versions of those packages. **Critical structural finding: dual-existence between standalone repos and the monorepo** — both receive April-May 2026 commits, but the monorepo versions are 0.5-5 minor versions ahead (e.g. `globals` standalone 5.22.0 vs monorepo 5.27.1; `entities` 16.36.0 vs 16.37.6; `ui-components` 1.2.0 vs 1.3.4; `ctmslb` 1.28.0 vs 1.30.0). Either deprecated-but-receiving-backports or gradual phase-out — needs a single-decision clarification. Platform domain coverage 21 → 29 of 54.
24. **Depth pass 23 / Phase 4.27 (2026-05-12)** — +14 seeds covering the **platform-domain tail** (Loadmate root, MFE-domain frontends, Go services, the Django monolith): `platform-frontend` (Loadmate `@ship-cars/root-config`, active PR #1835, contains in-repo parcels that dual-exist with extracted MFEs `contract-pricing-frontend` / `executive-dashboard-frontend` / `chat-frontend`), `ctms-frontend` (the **only fleet repo using paid MUI X Premium tier**), `settings-frontend` / `gallery-frontend` / `inspection-requirements-frontend` (older single-spa-5 MFEs), `documentation` (3.5-yrs-stale Grunt static-docs site for `docs.ship.cars` — **archive-candidate**), `website` (3.5-yrs-stale Gatsby 2.x marketing site for `ship.cars` — **archive-candidate**), `platform-backend` (**Django+Daphne Python 3.6 monolith**; PR #2780 — highest PR count in the fleet; the original Loadmate backend; **third EOL Python/Spring service alongside `lead-parser` + `rateengine`, but the most actively maintained**), `import-map-deployer` (Go single-spa import-map manager; SPOF for fleet-wide MFE deploys), `logging-manager` (Go service brokering Spring + Quarkus logger-level changes cluster-wide), `archival-data-verification` (Go DB-consistency verifier), `api-documentation-builder` (Node tool combining per-service swagger files + publishing to Readme.com), `internal-api-docs` (tiny Express + swagger-ui-express server), `internal-api-docs-controller` (3-year-stale K8s controller — **archive-candidate**). Platform domain coverage 29 → 43 of 54.
25. **Depth pass 24 / Phase 4.28 (2026-05-12)** — +11 seeds closing **platform** to catalog-complete. **Backoffice cohort (5):** `backoffice-backend` + `backoffice-frontend` (modern Vite 6 + **React 19.2** + pnpm 10 — fleet's newest React major) and the uShip pair `uship-backoffice-backend` + `uship-backoffice-frontend` (older CRA 5 + React 18.2 — stack drift between the two BackOffice fronts), plus `backoffice-app-ARCHIVED` (archived Python Flask 2.3 predecessor, 2.5-yrs-stale). **Small Quarkus services (6):** `crm-workflows` (Freshsales-sync), `company-cleanup-utils` (test-data cleanup), `archival-service` (Quarkus 3.15.2 modern archival), `toolbox-service` (catch-all utility service), `archiver` (**Quarkus 2.9.1.Final — fleet's oldest active Quarkus, 3-yrs-stale, P1 lifecycle item**), `pubsub-exception-handler` (fleet-wide DLQ-message capture). **Platform domain catalog-complete (54/54). Catalog now has 8 of 9 domains catalog-complete.**
26. **Depth pass 25 / Phase 4.29 (2026-05-12)** — +33 infrastructure seeds in one big "tail-down" pass, closing the **active-classified subset** per `relations/infrastructure-triage.md`. Coverage: 13 Terraform live envs (the canonical 4-tier platform `dev/qa/staging/prod` + `system-env` cross-env + 2 older predecessor envs + `gcp-projects-access` for cross-project IAM + `xa-montway-production` separate partner project + legacy `atlantean-field-175514` hosting the ML model GCS bucket + 4 sf-lm Salesforce-Loadmate envs); 4 Terraform modules (`postgres-cloudsql`, `local-cloudsql-users`, `google-iam-management`, `github-repositories`); 4 Helm+K8s repos (`helm` — **1904 files, fleet's authoritative Helm-chart monorepo and most-frequently-touched repo in the catalog**; `helm-common-chart` OCI library; `argo` Argo CD+Workflows config; `argo-stresstests`); 4 Go/Node services (`catch-me`, `argo-wf-finalizer`, `argo-wf-notificator`, `automation` — 1461-file Jenkins-driven test framework); 5 docs/knowledge repos (`knowledge`, `knowledge-products`, `devops-docs`, `devops-helpers`, `sc-reusable-workflows`); 3 CI/Docker (`docker-utils` — 8 base Docker images extended by every fleet `Dockerfile`; `jenkins-master-system-env`; `automation` covered above). **Infrastructure: 34 of 68 seeds; remaining 34 stubs are 12 archive-candidates + 23 unsure deliberately preserved for human triage. Catalog: 196/232 seeds (84.5%). 8 of 9 domains catalog-complete for active services; infrastructure complete for active subset.**
27. **Phase 4.30+** — see "Recommended next deepening passes" below for the final consolidation options.

## Depth pass 9 / Phase 4.13 — done 2026-05-12

Seeded 6 more shadows + 1 contract draft + 1 ADR (now **68 seeds, 164 stubs, 232 total**):

**Platform depth (3 seeds) — all high-fanout:**
- `api-gateway` (Go 1.25 + Fiber v2) — fleet edge gateway. **No upstream HTTP-client timeout** = an unresponsive upstream hangs the gateway indefinitely; the single biggest reliability flag on the edge. JWT (Keycloak RSA) + legacy-auth fallback + Redis-backed rate limits.
- `dataone` (Quarkus 3.27.0) — **important correction**: NOT an external-DataOne adapter, but a **local vehicle catalog** with Caffeine `1400 h` TTL + HikariCP `max-size=4` + **8 inbound REST edges**. Highest-fanout read-only callee + smallest pool + 58-day cache TTL = pool/cache coherence concern. Pool-size outlier added to `data-stores.md`.
- `cube` (Quarkus 3.27.0, 28 poms / 13 logical modules) — the fleet's largest multi-module. **Confirms the source of `cube.search-posting-events`** (consumed by `ml-service-listener` + `saved-search-handler`). Self-described as "Elasticsearch read query microservice". **Re-domained `platform` → `listings-trade`**.

**Operations depth (2 seeds):**
- `location-history-backend` (Quarkus 3.27.0) — driver + load location tracking; custom PostGIS-style `PointType`; **directly read by `syncer`** (shadow-caller pattern, contract draft published earlier). `max-size=4` prod (added to pool outliers).
- `negotiations-router` (Quarkus 3.27.0) — pure stateless router between CTMS (legacy) and `loadboard-backend` v3, Unleash-toggle-driven. **Retirement path**: once CTMS is fully deprecated, this router can be retired with it.

**Infrastructure depth (1 seed):**
- `apache-camel-etl-demo` (Java 17 / Camel Quarkus 3.4.1) — **explicitly self-described as a demo/example** in its README. Likely an `infrastructure-triage.md` archive-candidate. Java 17 vs fleet's 21 is a version-drift flag.

**ADR-0003 implementation — 8th contract draft published:**
- `ml-pricing-app--montway-and-rate-engine.md` — covers the two newly-surfaced shadow-caller edges from depth-pass 8 (`MONTWAY` MySQL + `RATE_ENGINE` PG). **`MONTWAY` ownership unidentified** (likely partner DB); ties to ADR-0005 rewrite for the `RATE_ENGINE` PG migration.

**ADR-0006 — `ml-bot-order` v1 retirement plan**: three-stage path (parity audit → traffic mirror → cutover) over one quarter. Closes the v1/v2 fleet question with a concrete decision and migration sequence.

**Service-graph delta:** +16 edges + 3 new inbound-fanout rows. `dataone`'s 8 inbound REST edges now formally documented.

**Data-stores delta:** +5 rows (4 new PG-owning services + 1 stateless gateway). Pool-size outliers list grew to 8 entries with `dataone` (4) and `location-history-backend` (4) added.

**Fleet-level numbers:**
- Direct-DB read edges: **14** (no change this pass).
- ADRs: **6** (ADR-0006 added).
- Contract docs: **8** (the `ml-pricing-app` contract added).
- Cumulative re-domains: `autoims-backend`, `user-activity-tracker`, `ml-bot-order-v2`, `ml-bot-order`, `ml-pricing-app`, `synclink-backend`, `webhook-relay`, `cube` (8 re-domains across the depth passes).

## Depth pass 10 / Phase 4.14 — done 2026-05-12

Seeded the remaining active services in the **communication** domain (now **72 seeds, 160 stubs, 232 total**):

**Communication depth (4 seeds — domain now catalog-complete for active services):**
- `ml-service-chat` (Python 3.9 / FastAPI 0.95.2 / Tortoise 0.19.3 / OpenAI 1.30.1 / LlamaIndex 0.10.23) — LLM-backed carrier+customer chat assistant API. GPT-4o (`temperature=0`, `seed=23`) with Postgres vector store. **~70-entry hardcoded `CARRIER_TOKENS` / `CUSTOMER_TOKENS` whitelist** in `settings.py`. **New shadow-caller edge**: Tortoise `db-source` reads `rateengine`'s `production` PG directly. **P0 to verify**: `openai==1.30.1` + legacy `openai.ChatCompletion.acreate(...)` call site is API-incompatible (v0 surface removed in v1). Three Tortoise connections, two of which point at the same DB (`ml_service_chat`) with separate logical apps.
- `ml-ui-chat` (Python 3.9 / Streamlit 1.27.0) — single-file (~253 LOC) Streamlit UI ("Sofia") served at `/chat/`. Calls `ml-service-chat /customer/*` via `requests.post(...)` **with no timeout**. Uses deprecated `st.experimental_get_query_params()` (removed in Streamlit ≥ 1.30) — blocks any version bump without code change. Token in URL query string (PII-in-logs risk).
- `chat-frontend` (TS 4.9 / React 18 / single-spa 6 / Webpack 5 / MUI 6.1 / axios 1.15) — `@shipcars/chat` single-spa MFE (corrects earlier "React/Vite" miscategorization). Does **not** open its own WebSocket; subscribes to **DOM `CustomEvent`s** under `new_socket_events.*` that the parent shell re-dispatches from the actual socket-server connection. `axios.create()` with **no default `timeout`** + Bearer-token in `localStorage`.
- `socket-server-old` (Node 16.6.2 + Socket.IO 2.0.4 + socketio-auth + HS256 JWT) — **frozen but still deployed** (helm chart with 2 replicas in production; single Init commit 2022-11-29). **Reclassified** from "archive candidate" (earlier triage) to **"frozen but deployed; retirement-blocked-on-client-migration"** — parallel to `socket-server` because the two use different JWT schemes (HS256 vs Keycloak RS256). **P0**: HS256 signing secret committed plaintext in `index.js` AND identically across `helm/.../values-{dev,qa,staging,production}.yaml`. Anyone with repo read access can forge JWTs accepted in any environment. Has not been rotated since 2022-11-29.

**Topology delta (`relations/service-graph.md`):**
- +7 edges (4 REST/DOM + 1 external + 1 Redis + 1 WebSocket).
- **The two socket-servers run on different Redis clusters** (`socket.redis.shipcars-platform-prod...` vs `main.redis.shipcars-platform-prod...`). `pusher`'s Redis-emitter target determines which gateway sees its broadcasts — open question to resolve in the next pass.
- New domain-topology diagram added to the service-graph.

**Data-stores delta (`relations/data-stores.md`):**
- +2 PG rows (`ml-service-chat` owns `ml_service_chat`; `ml-service-chat` reads `rateengine.production` as shadow caller).
- +1 Redis row (`socket-server-old` separates out from `socket-server`).
- **Cross-service direct-DB-read edges: 14 → 15.** One unsanctioned edge needs an ADR-0003 contract draft: `db-contracts/ml-service-chat--rateengine-production-pg.md`.

**Domain rollup (`domains/communication.md`):**
- Refreshed seed status: 1 → 10 of 12.
- Folded in the LLM-chat path, the parallel-Redis WebSocket topology, and the new pool-size / P0 findings.
- Flagged that the 2 remaining stubs are devops repos that were probably name-matched into `communication` and belong in `infrastructure`.

**P0 / fleet-significant findings from this pass:**
- **`socket-server-old`** hardcoded JWT secret in git × 4 environments (above). **Compensating control before client migration**: move to `gcp-secret-manager`/`externalSecrets` and rotate; full retirement requires Keycloak-JWT migration of remaining HS256 clients.
- **`ml-service-chat`** openai SDK / call-site mismatch — needs runtime verification.
- **`ml-ui-chat`** + **`chat-frontend`** no-timeout REST clients — same anti-pattern as Quarkus fleet, but at the Python/browser layers. Two-line fixes each.

**Phase 4.14 also closes the "what do `ml-service-chat` / `ml-ui-chat` actually do?" open question** that the communication-domain rollup had carried since v1.

## Depth pass 11 / Phase 4.15 — done 2026-05-12

Seeded 4 platform-extension libraries (now **76 seeds, 156 stubs, 232 total**):

**Platform-extension depth (4 seeds):**
- `commons` (Java 17 / Maven 10-module under `ship.cars.commons:libs` 3.28.0-SNAPSHOT) — the fleet's framework-neutral parent commons. Modules: `bom`, `commons`, `commons-datadog`, `error-handling`, `temporal-commons`, + 5 test modules. **Public API stability is load-bearing for the entire Java fleet (~50+ consumers)**: any breaking change to `ErrorCode`, `UserContextDto`, `IDResponseDto`, `PageDto`, `SC*Utils` propagates fleet-wide. The 2024 Commons Split (per README) is now formally documented — `commons` is framework-neutral, `quarkus-commons` is Quarkus-specific, `spring-commons` is Spring-specific.
- `quarkus-extension-webclient` (Quarkus extension, Vert.x WebClient + Apache HttpClient5) — **the fleet's safe-path Quarkus REST client**: `WebClientImpl.DEFAULT_CONFIG` provides baseline timeouts (connect 60 s / read 30 s / write 30 s) + retry (7 attempts, 5–30 s backoff, 0.75 jitter) + automatic `BusinessRuleException` translation. Used by **9 services**: `cube`, `integrations-backend`, `load-bookmark-backend`, `load-recommender`, `loadboard-backend`, `location-provider`, `saved-search-handler`, `trip-planner`, `command-executor`. **Worst-case call budget: ~5 min if retry exhausts at max backoff** — request-path callers should override `retryMaxAttempts`.
- `quarkus-pubsub` (Quarkus extension wrapping `google-cloud-pubsub`) — **the fleet's GCP Pub/Sub publish-and-subscribe substrate**. **29 fleet consumers**, plus transitive dependencies via `quarkus-notification-client` (40+) and `quarkus-user-syncer`. Provides typed `PubSubConsumerBlocking<T>` + `PubSubAckReplyConsumerBlocking<T>` + async `PubSubPublisher` / blocking `PubSubPublisherSync`. **Retry / DLQ is GCP-side, not in code** — every prod subscription needs `Maximum delivery attempts` + `Dead letter topic`, audit worth running.
- `quarkus-extension-persistence` (Quarkus extension, JTA helpers) — narrow scope despite the broad name: provides `TransactionalExecution` + `TransactionalBatchesExecution` for programmatic JTA transaction control. **14 consumers**. **Important correction recorded: does NOT carry Hikari pool defaults.** Pool-size outliers (`notification-backend` 5, `dataone` 4, `public-tracking-backend` 5, `load-bookmark-backend` 4 prod, `location-history-backend` 4, `location-provider` 4) are per-repo `application.properties` choices — no single-line fleet-wide pool fix possible.

**Service-graph updates:**
- Compile-time-edges table rewritten with confirmed fanout numbers (was qualitative; now quantitative).
- New Phase 4.15 observation block: REST-client-timeout gap is structural (path choice) not configurational; Pub/Sub retry/DLQ posture is GCP-side; pool-size outliers can't be fixed centrally.

**Platform domain rollup updates:**
- Seed count 5 → 11 of 54 platform shadows.
- Two long-standing open questions retired: (a) commons-split semantics (resolved via the 2024-split-as-documented-in-`commons/README.md` finding), (b) cube/dataone purpose (resolved earlier in Phase 4.13; rollup updated).
- New seam documented: `quarkus-extension-webclient` (9) vs. `@RegisterRestClient` (~30) — fleet hasn't picked canonical path.
- New audit gap documented: which prod Pub/Sub subscriptions have `Maximum delivery attempts` + `Dead letter topic`.

## Depth pass 12 / Phase 4.16 — done 2026-05-12

Seeded 2 more libraries closing the Java-commons-shared-library group (now **78 seeds, 154 stubs, 232 total**):

**Platform-commons depth (2 seeds — Java-commons group complete):**
- `shipcars-quarkus-bom` (`ship.cars.quarkus:shipcars-quarkus-bom` 3.27.1-SNAPSHOT) — the fleet's Quarkus version-of-truth BOM. Pins Quarkus platform 3.27.0 + Java 21 + 6 Quarkiverse extensions (`quarkus-logging-json` 3.4.0, `quarkus-logging-manager` 3.4.1, `quarkus-google-cloud-pubsub` 2.18.0, `quarkus-unleash` 1.11.0, `quarkus-tika` 2.2.1, `quarkus-wiremock` 1.5.1) + Maven plugin versions. **Crucial finding**: **does NOT pin any Ship.Cars extension** — `quarkus-commons`, `quarkus-pubsub`, etc. are pinned per-consumer. This explains the fleet's silent BOM-vs-extension version drift. Lagging fleet Quarkus versions (`archiver` 2.9.1.Final, `notification-orchestrator` 3.8.3, 3.15.x / 3.20.x services) correspond to older BOM snapshots, each one bump-coordination job away from current.
- `models-lib` (`ship.cars.models-lib:models-lib` 1.144.0-SNAPSHOT) — the fleet's shared Java DTO library. 5 modules: `data-models` (~35 entity DTOs — `PostingDto`, `LoadDto`, `CompanyDto`, `VehicleDto`, …), `api-dtos` (REST DTOs scoped per-consumer), `read-models` (ES-document tier, `Indexable` marker), `converters` (data→read DTO conversion pipeline), `ml-dtos` (rateengine Java-side contract). **17 fleet consumers** (compile-time). **Heaviest reader is the ES-indexing pipeline** (`syncer` + `cube` + `saved-search-handler`). Independently versioned from the Quarkus BOM. `ml-dtos` is the Java-side contract surface that ADR-0005's rateengine rewrite must preserve.

**Java compile-time substrate fully catalogued:**

| Library | Consumers | Version |
|---|---|---|
| `commons` (framework-neutral) | ~50+ | 3.28.0-SNAPSHOT |
| `quarkus-commons` | ~40+ | 3.27.1-SNAPSHOT |
| `spring-commons` | 10+ | (tracks Spring Boot 3.2.12) |
| `shipcars-quarkus-bom` | ~40+ | 3.27.1-SNAPSHOT |
| `models-lib` | 17 | 1.144.0-SNAPSHOT |
| `quarkus-notification-client` | 40+ | 3.27.1-SNAPSHOT |
| `quarkus-pubsub` | 29 | 3.27.1-SNAPSHOT |
| `quarkus-extension-persistence` | 14 | 3.27.1-SNAPSHOT |
| `quarkus-extension-webclient` | 9 | 3.27.1-SNAPSHOT |

**Service-graph updates:**
- Compile-time-edges table extended with two new high-detail rows.
- Phase 4.16 observation block added — the "fleet substrate now fully catalogued" milestone is recorded.

**Platform domain rollup:**
- Seed count 11 → 13 of 54.
- Coverage section now lists the closed Java-commons group as 7 of 7.

## Recommended next deepening passes (Phase 4.30, optional)

Seeds-only per the saved feedback. Per-domain status after Phase 4.29:

| Domain | Seeds | Stubs | Total | Catalog status |
|---|---|---|---|---|
| **communication** | 10 | 2 (devops only) | 12 | **complete** |
| **identity** | 9 | 0 | 9 | **complete** |
| **integrations** | 16 | 0 | 16 | **complete** |
| **listings-trade** | 16 | 0 | 16 | **complete** |
| **pricing-billing** | 15 | 0 | 15 | **complete** |
| **operations** | 18 | 0 | 18 | **complete** |
| **analytics** | 24 | 0 | 24 | **complete** |
| **platform** | 54 | 0 | 54 | **complete** |
| infrastructure | 34 | 34 | 68 | **active subset complete** (archive + unsure remain) |

**Catalog: 196 / 232 seeds (84.5%).** 8 of 9 domains catalog-complete for active services; infrastructure complete for active subset.

**The catalog has reached a natural stopping point.** Remaining work is either (a) decisions humans need to make (which archive-candidates to actually archive, which unsure repos to keep vs. retire), or (b) the deferred meta-items.

1. **Triage the 12 archive-candidates** per `infrastructure-triage.md` — one PR per repo to add a top-level `ARCHIVED.md` marker, or formal removal. Single-decision-per-repo work.
2. **Triage the 23 unsure** — one-line decision per repo from the dev-tooling area owner. Some are AI-coding experiments (`claude-code-plugins`, `dev-hub`, `sdlc-agents`, `codex-cli-ai-code-reviewer`, `figma-mcp-code-connect`, `ai-actions-test`) plausibly active OR experiments. Each closes a stub.
3. **Tackle deferred meta-items** (per saved-feedback these were on the back burner; the seed catalog is now 84.5% complete, so they're a natural next focus):
   - **ADR-0007** (canonical Quarkus REST-client path — `WebClientImpl` vs `@RegisterRestClient`).
   - **ADR-0008** (pin Ship.Cars extensions in `shipcars-quarkus-bom` — eliminate silent BOM-vs-extension version drift).
   - **Pub/Sub subscription audit** (`relations/pubsub-subscriptions.md`) — walk `devops-tf-live-shipcars-platform-prod/live/pubsub/` for `Maximum delivery attempts` + `Dead letter topic` per subscription.
   - **`models-lib` DTO ownership matrix.**
   - **9th ADR-0003 contract** for `ml-service-chat → rateengine.production`.
   - **Pusher Redis-cluster confirmation** (closes `socket-server-old` retirement plan).
   - **`infrastructure-triage.md` refresh** (the 2026-05-08 triage is 5 days old; the new archive-candidates flagged through depth passes 4.14–4.28 add to the list).
   - **Coordinated bump plan** for the 5 P1 lifecycle laggards (`lead-parser` Spring 2.1.4, `rateengine` Django 2.1.7, `platform-backend` Python 3.6, `archiver` Quarkus 2.9.1, `notification-orchestrator` Quarkus 3.8.3).
   - **Fleet review v2** — at 196 / 232 seeds + the full set of `relations/*` artifacts, the synthesis is well-prepared. Recommended scope: timeouts (33 of 36 `@RegisterRestClient` missing), pool-size outliers (8 services on `max-size≤10`), 16 shadow-caller DB-read edges, the 5 EOL stacks, FDL deprecation, hardcoded-secret cases (`socket-server-old`, `home-delivery-backend`, `load-bookmark-service`), the REST-client-path seam, Pub/Sub audit gap, BOM-vs-extension drift, archive-candidates + unsure-triage-needed counts.
4. **Verify existing seeds against current code** — at 196 seeds spanning ~2 weeks, some may have drifted. Run `scripts/drift_check.py --all --mark-stale` and re-seed any drifted.
5. **Consider the work done.** The catalog has reached a clear stopping point.

Accumulated re-domain housekeeping (5 small PRs):
- `devops-tf-live-shipcars-logytext-integration`: `integrations` → `infrastructure`.
- `synclink-chrome-extension`: `operations` → `integrations`.
- `fe-exercise-inventory-api` + `fe-exercise-inventory-ui`: `listings-trade` → `infrastructure` (or `hiring-artifacts`).
- `devops-tf-live-shipcars-ml-data-{dev,staging,prod}` (3 repos): `analytics` → `infrastructure`.
- `elk-backup-restore`: `analytics` → `infrastructure`.

Re-domain housekeeping accumulated (small, mechanical):
- `devops-tf-live-shipcars-logytext-integration`: `integrations` → `infrastructure`.
- `synclink-chrome-extension`: `operations` → `integrations`.
- `fe-exercise-inventory-api` + `fe-exercise-inventory-ui`: `listings-trade` → `infrastructure` (or `hiring-artifacts`).
- `devops-tf-live-shipcars-ml-data-{dev,staging,prod}` (3 repos): `analytics` → `infrastructure`.
- `elk-backup-restore`: `analytics` → `infrastructure`.

Archive-candidates accumulated (for next infrastructure-triage refresh):
- `ml-model-time-to-dispatch` (empty placeholder).
- `aaag-poc`, `aaag-integration-logs-ARCHIVED` (Python predecessors).
- `apache-camel-etl-demo`.
- `ios-epod-github-actions-test`, `asg-checkout-spa`, `ml-playground`, `ml-notebooks-archive`, `databricks-embedding-test`.
- `documentation`, `website` (3.5-yrs-stale platform docs site + Gatsby marketing).
- `internal-api-docs-controller` (3-yrs-stale K8s controller).
- `backoffice-app-ARCHIVED` (Flask predecessor).
- `archiver` — pending retire-or-bump decision.

Deferred meta-items (keep on the back burner per user feedback):
- ADR-0007 / ADR-0008, Pub/Sub audit, `models-lib` DTO ownership matrix, 9th ADR-0003 contract, pusher Redis confirmation, `infrastructure-triage.md` refresh, coordinated bump plan, Fleet review v2.

Re-domain housekeeping accumulated through Phase 4.25 (small, mechanical):
- `devops-tf-live-shipcars-logytext-integration`: `integrations` → `infrastructure`.
- `synclink-chrome-extension`: `operations` → `integrations`.
- `fe-exercise-inventory-api` + `fe-exercise-inventory-ui`: `listings-trade` → `infrastructure` (or `hiring-artifacts`).
- `devops-tf-live-shipcars-ml-data-{dev,staging,prod}` (3 repos): `analytics` → `infrastructure`.
- `elk-backup-restore`: `analytics` → `infrastructure` (operational ELK admin tool).

Archive-candidates accumulated (for next infrastructure-triage refresh):
- `ml-model-time-to-dispatch` (empty placeholder; no `code/`).
- `aaag-poc`, `aaag-integration-logs-ARCHIVED` (Python predecessors of `aaag-integration`).
- `apache-camel-etl-demo` (self-described demo per Phase 4.13).
- `ios-epod-github-actions-test` (empty-README iOS CI snapshot).
- `asg-checkout-spa` (2017-era Montway Checkout SPA; confirm Montway hasn't migrated).
- `ml-playground` (3-years-stale ChatGPT learning repo).
- `ml-notebooks-archive` (historical Jupyter dump; descendants productionized).
- `databricks-embedding-test` (one-off Databricks-embed test harness).

Deferred meta-items (keep on the back burner per user feedback):
- ADR-0007 / ADR-0008, Pub/Sub audit, `models-lib` DTO ownership matrix, 9th ADR-0003 contract, pusher Redis confirmation, `infrastructure-triage.md` refresh, coordinated bump plan, Fleet review v2.

## Original Phase 4.18 backlog (superseded — kept for traceability)

User redirected: "focus on the actual mapping — seeds/stubs and not on the timeouts/issues." Phase 4.18 executed an operations depth pass instead.

- Items 1, 2 (ADR-0007, ADR-0008): deferred per user feedback.
- Items 3, 4, 5, 6, 7, 8, 9: deferred per user feedback (carried to Phase 4.19 deferred-carryovers list).

## Original Phase 4.17 backlog (superseded — kept for traceability)

- Items 1, 2, 5, 6, 7 carry forward unchanged into Phase 4.18 (as items 1, 3, 5, 6, 7).
- Item 3 (Quarkus version-drift matrix) **done in this pass** (`relations/quarkus-version-matrix.md`).
- Item 4 (`models-lib` DTO ownership matrix) carried unchanged.
- Item 8 (more Quarkus extensions) deferred — the matrix now confirms the substrate is well-understood; specific extension seeds would be lower leverage than the new ADR-0008 recommendation.
- Item 9 (fleet review v2) carried unchanged.

## Original Phase 4.16 backlog (superseded — kept for traceability)

- Items 1, 2 carry to Phase 4.17 as items 1, 2.
- Item 3 (9th ADR-0003) carries as item 5.
- Item 4 (pusher Redis target) carries as item 6.
- Item 5 (infrastructure triage) carries as item 7.
- Item 6 (BOM + models-lib) **done in this pass**.
- Item 7 (more Quarkus extensions) carries as item 8.
- Item 8 (other-domain depth) deferred — the substrate is now closed and the remaining stubs are lower-leverage.
- Item 9 (fleet review v2) carries as item 9.

## Original Phase 4.15 backlog (superseded — kept for traceability)

Items 3, 4, 5 carry forward into the Phase 4.16 list above as items 3, 4, 5. Items 1, 2 were user-actionable repo fixes already documented in shadow docs. Items 6, 7, 8 are all carried as items 6, 7, 8 in the new list. Items 9 (fleet review v2) is item 9. The platform-extensions pass completed itself in this Phase 4.15.

## Original Phase 4.14 backlog (superseded — kept for traceability)

Items 1, 6, 7 carry forward into the Phase 4.15 list above. Items 2, 3, 4 are user-actionable repo fixes documented in their shadow docs (`dataone.md`, `notification-backend.md`, `location-history-backend.md`, `api-gateway.md`) — not catalog work. Item 5 was completed by this pass.

1. ~~`infrastructure-triage.md` update~~ — carried to Phase 4.15 item 5.
2. ~~Pool-size right-sizing PR sweep~~ — user-actionable; documented in shadow docs.
3. ~~`api-gateway` upstream-timeout fix~~ — user-actionable; documented in `api-gateway.md`.
4. ~~`dataone` cache TTL reduction~~ — user-actionable; documented in `dataone.md`.
5. ~~Continue communication-domain depth~~ — **done in this pass.**
6. ~~Continue listings-trade depth~~ — carried to Phase 4.15 item 6.
7. ~~Fleet-wide write-up~~ — carried to Phase 4.15 item 9.

## Depth pass 8 / Phase 4.12 — done 2026-05-12

Seeded 4 more shadows + wrote 5 ADR-0003 contract drafts + ADR-0004 + ADR-0005 (now **62 seeds, 170 stubs, 232 total**):

**New seeds:**
- `ml-bot-order` (v1) — Python 3.11 / FastAPI / **legacy `google-genai` SDK** (not LiteLLM). **Does NOT publish a Pub/Sub topic** — confirms v2 is the sole producer of the `ml-bot-order` topic that `posting-backend` consumes. Re-domained `pricing-billing` → `integrations` to match v2.
- `ml-model-rate` — Python / FastAPI / **LightGBM 3.2.1**. Stateless inference service; called by `ml-service-dispatcher`. **Hardcoded model filenames + hardcoded user-email feature mapping** — model rollback requires code change.
- `uship-quotes` — Quarkus 3.20.2.2. uShip marketplace integration with **two bidding modes** (API + Node/Playwright webbot bypass). **`webbot` is one of the few fleet REST clients with explicit timeouts** (`PT10S` / `PT120S`). Caffeine `expire-after-write=5400h` (~7.5 months — verify typo).
- `ml-pricing-app` — **Streamlit 0.65.1 + SQLAlchemy 1.3.19 (both 2019-2020)**. BI dashboard + daily cron for pricing-accuracy monitoring. **Re-domained `pricing-billing` → `analytics`** — this is analytics, not pricing. **New shadow-caller edges** (MONTWAY MySQL + RATE_ENGINE PG).

**ADR-0003 implementation — all 7 first-tier contract drafts published:**
- `integrators-data-bridge--{posting-backend, inventory-backend, autoims-backend, contract-pricing-backend}.md`
- `syncer--multi-source.md` (covers all 6 upstream PGs)
- `pusher--user-and-ctms-dbs.md` (flags `user-backend`'s outbox as the cleanest migration target)
- `ml-demand-forecasting--source-pg.md` (source service unidentified — that's the contract's biggest TODO)

Each has a column-list TODO that requires the reader-owner's human input. The template is now established; the remaining `ml-pricing-app` → MONTWAY / RATE_ENGINE edges can be drafted by copy-paste.

**ADR-0004 — Firebase Dynamic Links migration**: proposes Option A (App Links + Universal Links on a Ship.Cars-owned domain) as the post-FDL deep-link path. Sequenced cutover + bridging plan documented.

**ADR-0005 — `rateengine` EOL rewrite**: proposes Option A (full rewrite to Python 3.12 + FastAPI on `ml-bot-order-v2` conventions). Behavioral-parity test harness as the gating mechanism; 6-9 person-months total effort. References the user's `ml-bot-order-v2` skills as the convention template.

**Fleet-level numbers:**
- **Direct-DB read edges**: 14 total (was 12).
- **ADR count**: 5 (3 originally + 2 this pass).
- **Cross-cutting contract docs**: 7 (all draft v0.1).
- **Domains rebalanced**: `pricing-billing` 18→16; `integrations` 15→16; `analytics` 23→24.

## Recommended next deepening passes (Phase 4.13, optional)

1. **Draft the 8th ADR-0003 contract** for `ml-pricing-app` → MONTWAY MySQL + RATE_ENGINE PG. Copy the existing template; 30 minutes.
2. **Fill column-list TODOs** in any of the 7 draft contracts that have a known reader-owner. Each one closes when ~10 column names are filled in.
3. **Continue depth on the highest-traffic stubs in the remaining domains**:
   - **`platform`**: still has 55 stubs / 5 seeds. `attachment-backend`, `metadata`, `media-proxy`, `location-provider`, `impersonator` are seeded; pick 3 more from the long tail.
   - **`infrastructure`**: 68 stubs / 0 seeds. The previous `infrastructure-triage.md` flagged 33 "active" candidates. Pick 3-5 that block downstream work.
   - **`operations`**: 18 stubs / 4 seeds. `chat-state-syncer` (if real), `dispatcher-frontend`, `tracking-frontend` (likely FE-heavy and lower priority).
4. **Open communication boundary decision** still requires a human owner (`notification-backend` ↔ `notification-orchestrator`).
5. **`ml-bot-order` v1 retirement plan**: v2 ships everything v1 does plus more; ADR-0006 candidate.

## Depth pass 7 / Phase 4.11 — done 2026-05-12

Seeded 6 more shadows + 2 ADR-0003 contract docs + 1 domain boundary clarification (now **58 seeds, 174 stubs, 232 total**):

**Identity depth (2 seeds):**
- `keycloak-mfa-plugin` (Java 21 / Keycloak SPI) — `Authenticator` + `ConditionalAuthenticator` + `CredentialProvider<TrustedDeviceCredentialModel>`. Inherits `quarkus-notification-client`'s blocking `future.get()` problem → a hung Pub/Sub stalls user logins.
- `keycloak-phone-login-plugin` (Java 17 / Keycloak SPI) — 3 custom authenticators for phone-based login + SMS-link password reset. **Uses Firebase Dynamic Links** (`ydqx9.app.goo.gl`) — **Google has deprecated this product with an announced shutdown**, so every link this plugin emits will eventually break. **Migration plan required.**

**Analytics/integrations depth (4 seeds):**
- `ml-bot-order-v2` (Python 3.12 / FastAPI / LiteLLM / Gemini 2.5-flash) — **confirms the source of `posting-backend`'s `ml-bot-order` subscription**: publishes `oib-outbound-lm` + `oib-outbound-sf`. **Best-documented service in the fleet** (ARCHITECTURE.md, AGENTS.md, LESSONS.md, STATE.md). **Re-domained `pricing-billing` → `integrations`** — unstructured-text-to-DTO extraction is integrations work.
- `ml-demand-forecasting` (Python / PyTorch / TempoPFN 38M) — quarterly batch forecasting; **new shadow-caller edge surfaced** (reads a source production PG); GPU-only, no CPU fallback.
- `ml-document-parser` (Python / FastAPI) — pluggable document-parsing surface; hardcoded QA Pub/Sub topic (same fleet pattern as `company-documents`).
- `company-documents` (Python / FastAPI / sync SQLAlchemy + psycopg2) — document storage + lifecycle notifications; **synchronous emit_message() inside async FastAPI handlers** is the load-bearing risk; 25 s media-proxy timeout is fleet-rare-clean.

**ADR-0003 implementation started:**
- `relations/db-contracts/integrators-data-bridge--posting-backend.md` (draft v0.1)
- `relations/db-contracts/integrators-data-bridge--inventory-backend.md` (draft v0.1)
- Both have column-list TODOs for the reader owner. Establishes the template for the remaining 10+ edges.

**Pricing-stack boundary clarified** in `domains/pricing-billing.md`:
- `contract-pricing-backend` owns per-customer overrides.
- `quote-manager-backend` owns the lifecycle state of a quote.
- `rateengine` is the actual base-rate engine (EOL Django).
- `ml-service-dispatcher` is the synchronous gateway to ML model services beneath `rateengine`.

**Recommendation-chain confirmation extended**:
```
ml-bot-order-v2 (LLM extraction)
  ↓ publishes oib-outbound-lm  (= ml-bot-order topic in posting-backend's config)
posting-backend (load creation + reconciliation)
```

**New fleet-wide flag**: **Firebase Dynamic Links deprecation** affects `keycloak-phone-login-plugin`. Every SMS password-reset link is wrapped with `ydqx9.app.goo.gl/?link=...`. Google's announced shutdown means: links that already exist in user inboxes / SMS history will break; new links must use App Links / Universal Links / an in-house gateway.

**Service-graph delta:** +16 edges (mostly the 4 ML/document seeds). New sanctioned-cross-DB-reads section seeded with 2 contract docs.

**Data-stores delta:** +4 rows (4 new PG-owning services), `ml-demand-forecasting` flagged as a new shadow caller.

## Recommended next deepening passes (Phase 4.12, optional)

1. **Fill the column-list TODOs** in the two ADR-0003 contract drafts (`integrators-data-bridge` ↔ `{posting,inventory}-backend`). Both drafts call out exactly what's missing; an hour with the reader-owner closes them.
2. **Draft the next 5 ADR-0003 contracts** following the same template: `integrators-data-bridge` ↔ `autoims-backend` / `contract-pricing-backend`; `syncer` ↔ each of the 6 upstream PGs; `pusher` ↔ `ctms-db` + `usermanagement-db`; `ml-demand-forecasting` ↔ source production PG.
3. **Migrate `keycloak-phone-login-plugin` off Firebase Dynamic Links** — Google's shutdown is the forcing function. Catalog work would be to write a new ADR (0004) on the link-gateway choice.
4. **Pricing-stack EOL**: the boundary-clarification note in `domains/pricing-billing.md` now makes the `rateengine` rewrite a tractable proposal. Draft an ADR (0005) on whether to rewrite or to wrap with a thin Python-FastAPI shell while keeping Django for inference.
5. **`ml-document-parser` + `company-documents` hardcoded-QA-topic fix** — both publish to `cars.ship.qa.notification` regardless of environment. Verify the env-var convention and fix.
6. **Communication boundary decision** — `notification-backend` ↔ `notification-orchestrator` still open (carried from Phase 4.7).

## Depth pass 6 / Phase 4.10 — done 2026-05-11

Seeded 8 more shadows + wrote ADR-0003 (now **52 seeds, 180 stubs, 232 total**):

**Identity depth (4 seeds):**
- `keycloak` (Keycloak 26.0.5 / Quarkus distribution) — custom Docker image bundling 4 SPI plugins + Ship.Cars theme; the deploy/build boundary for the fleet OIDC provider. **Version drift between `docker-compose.yml` (KC 12.0.2) and the Dockerfile (KC 26.0.5)** is a real maintenance gotcha.
- `keycloak-events-plugin` (Java 17 SPI plugin, built against KC 24.0.4) — **the source-of-truth producer of every Keycloak event** consumed by `fraud-detector` and `pusher`. Has `@AutoService`-registered `EventListenerProvider`; **silently swallows publish IOExceptions** (no DLQ).
- `keycloak-password-reset-link` (Java 11 SPI plugin, built against KC 26.0.5) — `POST /realms/{realm}/reset-password` admin endpoint returning reset-password links directly to the caller. **No audit log of who-generated-a-link-for-whom** is the SOC2/SOX gap.
- `hasher` (Go 1.18 / Fiber) — tiny stateless ID-obfuscation service. **Not a security control** — Hashids is reversible by anyone with salt + alphabet.

**Analytics depth (2 seeds):**
- `ml-service-listener` (Python / FastAPI) — Pub/Sub event sink for `cube.search-posting-events` + `load-recommender.feedback-events`. Default `PUBSUBS_PROJECT_ID` literally `"SHOULD-BE-CHANGED"`.
- `ml-service-dispatcher` (Python / FastAPI) — synchronous ML-prediction gateway; 5 model clients + DataOne; **<5% test coverage** by self-report; explicit `httpx` pool sizing (`max_connections=100`); writes audit to Elasticsearch + DB.

**Listings-trade depth (2 seeds):**
- `ml-service-recommender` (Python / FastAPI) — **completes the recommendation chain**: this service publishes `cars.ship.prod.ml.recommender` → consumed by `load-recommender` → fans out via `notification-orchestrator`. Hardcoded GCP project default = prod's project. Dual PG (`mlrecommender` + `recommender`).
- `loadbuilder-backend` (Spring Boot 3.2.12) — **the only Spring service in the fleet without an RDBMS**: persists entity state to **GCS as serialized Java + JSON, optimistic-locking via a `version` field**. Two deployables (api-app port 7065 + worker-app via Pub/Sub).

**ADR-0003 published**: `adr/0003-cross-service-db-read-policy.md` proposes a two-tier policy for the 11+ cross-service direct-PG-read edges: sanction existing edges with named, versioned, consumer-tested contracts; reject new ones in favor of REST / Pub/Sub / dedicated replicas.

**Recommendation chain confirmed end-to-end** in `relations/service-graph.md`:

```
ml-service-recommender → cars.ship.prod.ml.recommender → load-recommender
   → notifications-topic → notification-orchestrator → SendGrid → user

load-recommender (feedback) → load-recommender.feedback-events → ml-service-listener (PG)
```

**Data-stores delta**: +5 rows (3 ML services, `loadbuilder-backend` as the lone GCS-as-DB service, audit-log ES). The `pool-size outliers` table is unchanged from depth-pass 5.

## Recommended next deepening passes (Phase 4.11, optional)

1. **Implement ADR-0003** — write the per-edge contract docs starting with `integrators-data-bridge` ↔ `posting-backend` and `integrators-data-bridge` ↔ `inventory-backend` (the highest-traffic edges).
2. **Resolve `ml-service-dispatcher` vs. `rateengine` overlap.** Both compute ML-based pricing in Python. The boundary is implicit. A 1-page note in `domains/pricing-billing.md` resolving the split (who owns rate quotation? who owns ML predictions feeding it?) is overdue.
3. **The `ml-bot-order` Pub/Sub topic** (consumed by `posting-backend`) source is still unconfirmed. Not produced by `ml-service-dispatcher` (REST-only). Probably one of `ml-bot`, `ml-bot-engine`, `ml-orders-bot`, or a sibling. Worth a single-grep follow-up.
4. **Continue analytics depth** — 20 stubs remain. `ml-demand-forecasting`, `ml-document-parser`, `ml-data-hamal`, `ai-testgen`, `company-documents` are the most-likely real services.
5. **Continue identity depth** — `keycloak-mfa-plugin`, `keycloak-phone-login-plugin` (the remaining bundled plugins; both real and small).
6. **Communication boundary decision** still open (carried from Phase 4.7).

## Depth pass 5 / Phase 4.9 — done 2026-05-11

Seeded 9 more shadows (now **44 seeds, 188 stubs, 232 total**):

**Integrations depth (6 seeds):**
- `axe-call-integration` (Quarkus 3.27.0) — AXE AI-call bridge; **rare fleet-good pattern**: `@RegisterRestClient` with `@Timeout(5000)` + `@Retry` + `@CircuitBreaker` (but timeout hardcoded in annotation, not externalized). Webhooks via Pub/Sub.
- `integration-executor` (Quarkus 3.20.4) — message router to 7 external platforms (Acertus, Ally, CarsArrive, RunBuggy, SuperDispatch, Webhook, Logytext); persistent retry table + EDI hash dedup. **`AttachmentClient` has explicit timeouts** (one of the few in the fleet).
- `quarkus-user-syncer` (Quarkus extension library) — provides the `db-syncer` pattern used by `notification-orchestrator`, `load-recommender`, `trip-planner`, `saved-search-handler`. README is one-liner; contract is implicit.
- `syncer` (Quarkus 3.27.0) — **second-largest "shadow caller" in the fleet** after `integrators-data-bridge`: directly reads 6 other services' PGs (lm-posting, saved-search, platform/lbv3, location-history, metadata, trip-planner) and pushes to Elasticsearch in bulk. Same schema-coordination risk.
- `synclink-backend` (Quarkus 3.27.0) — Chrome-extension load-state bridge to `posting-backend`; SHA-256 change detection; Envers audit with `ActorContext` `ThreadLocal`. **Re-domained operations→integrations.**
- `webhook-relay` (Go) — stateless GitHub-webhook gateway with HMAC validation + IP whitelist + fan-out. No persistent retry queue. **Re-domained platform→integrations.**

**Communication depth (3 seeds):**
- `pusher` (Quarkus 3.27.0) — **central event-routing brain** for the communication domain. Consumes ~10 Pub/Sub subscriptions, routes to 5 channels (WebSocket, push, email, SMS, integration). Reads `ctms-db` + `usermanagement-db` directly. Three datasources at `max-size=10` each.
- `socket-server` (Node + Socket.IO 2.0.4 + Express 4.17.1) — pure WebSocket relay; Redis adapter for cluster mode; Keycloak public-key cached 15 min; no graceful shutdown.
- `quarkus-notification-client` (Quarkus extension library) — **most binary-coupled component in the fleet**: 40+ Quarkus services depend on its `NotificationClient` interface at compile time. **Synchronous `future.get()` blocks the caller** on every publish — propagates Pub/Sub latency across the fleet. Public-API stability is load-bearing.

**Service-graph delta:** +27 new edges + new inbound-fanout rows. The 44-seed graph now confirms:
- `quarkus-notification-client` is the single highest-coupled compile-time dependency in the fleet (40+ consumers).
- **11+ cross-service direct-DB-read edges** total (`integrators-data-bridge` 4 + `syncer` 6 + `pusher` 2 — overlap accounted). Fleet-wide pattern decision needed.
- Communication topology is now legible: `pusher` (router) → `quarkus-notification-client` → topic → `notification-backend` + `notification-orchestrator` (channel senders) + Redis → `socket-server` (WebSocket).

**Data-stores rollup updated** with `axe-call-integration`, `integration-executor`, `pusher` (3 datasources), `syncer` (reactive shadow reads), `synclink-backend`, plus Redis and Elasticsearch additions.

## Recommended next deepening passes (Phase 4.10, optional)

1. **Two timeout fixes now confirmed worth doing on the actual repos** (carried from earlier passes; not in scope for this catalog work):
   - `trip-planner.CtmsClient`: add `quarkus.rest-client.ctms-api.connect-timeout` + `read-timeout`.
   - `rateengine`: add `timeout=(5, 30)` to `requests.Session()` calls.
2. **`quarkus-notification-client` async-ification** — replace the blocking `future.get()` with a true async pattern. Fleet-wide latency impact; same effort.
3. **Identity-domain depth**: 8 stubs after re-domains. Likely candidates: `user-state-syncer` (if it exists; was missing in earlier probe), other `keycloak-*` services. Diminishing returns relative to depth in other domains.
4. **Analytics-domain depth**: 20+ stubs, 3 seeds (`bi-databricks-backend`, `ai-dashboard-backend`, `user-activity-tracker`). Worth probing the stubs to find real services vs. data pipelines.
5. **Fleet-wide direct-DB-read decision**: with 11+ such edges confirmed, the fleet should pick a stance — either formalize the cross-DB reads as a documented contract (with consumer-driven contract testing) or migrate to Pub/Sub-based replication. Worth a 1-page ADR (`adr/0003-cross-service-db-read-policy.md`).
6. **Pool-size right-sizing PR sweep** (carried from previous passes; still actionable): `notification-backend` 5 → 16; `public-tracking-backend` 5 → 16; `load-bookmark-backend` 4 prod → 16; `location-provider` 4 → 16; **`pusher`'s three 10-sized pools** worth a similar look.
7. **Listings-trade trailing stubs**: pick 2-3 — `loadbuilder-backend`, `central-dispatch-integration` (if exists), `load-history-service` (if exists). Verify which exist first.

## Depth pass 4 / Phase 4.8 — done 2026-05-11

Seeded 7 more shadows (now **35 seeds, 197 stubs, 232 total**):

**Operations depth (3 seeds):**
- `driveaway-backend` (Spring Boot 3.2.12) — driver coordination + Cloud Vision for ID/photo decoding; pool 10; no REST timeouts; Fingerprint Pro on the auth path.
- `public-tracking-backend` (Spring Boot 3.2.12) — public-facing tracking API; **HikariCP `maximumPoolSize=5` on a public surface** (outlier); Unleash on the request path; reCAPTCHA + attempt-limited bot blocking.
- `trip-planner` (Quarkus 3.27.0) — freight trip orchestration; CTMS bridge with **no `connect-timeout`/`read-timeout` on `CtmsClient`** (P0 in the rest-client-registry); 3 datasources (primary JDBC + reactive usermgmt + reactive ctms); trip capacity hardcoded at 12.

**Analytics depth (1 seed):**
- `user-activity-tracker` (Quarkus 3.20.2.2) — event-ingestion + HyperLogLog + Parquet→GCS; **Redis pool 10000** (extreme outlier); Hadoop 3.3.6 dep; ShedLock missing on exports; re-domained `identity` → `analytics`.

**Platform depth (2 seeds) — both very-high-fanout callees:**
- `attachment-backend` (Quarkus 3.20.4) — fleet-wide attachments; **only Quarkus outbound HTTP with explicit timeouts** (`PT60S` URL-fetch); Vert.x EventBus is in-process only (not cross-replica); `DELETE /?id=...` silently swallows per-ID errors.
- `metadata` (Quarkus 3.20.2.2) — central key-value registry; **publish-without-outbox is the core correctness gap** — DB commit can succeed while Pub/Sub cache-invalidation publish fails. Ships in-repo `spring-client` module that Spring consumers compile against — a major-version rename here breaks Spring downstreams silently.

**Pricing-billing depth (1 seed) — the actual pricing engine:**
- `rateengine` (**Python/Django 2.1.7 / DRF 3.8.2 — both EOL since 2020**) — ML-powered carrier-pay quotes (scikit-learn / LightGBM / CatBoost). `requests.Session()` with **no timeout** on outbound central-dispatch. Second-biggest fleet lifecycle flag after `lead-parser`.

**Re-domains:**
- `autoims-backend`: `pricing-billing` → `integrations` (AutoIMS shim, not a billing service).
- `user-activity-tracker`: `identity` → `analytics` (event tracking + Parquet/BigQuery export).

**Service-graph delta:** +22 new edges + 4 new inbound-fanout confirmations. `user-backend` inbound REST count now 10 (was 8). Two new platform-fanout callees confirmed: `attachment-backend` (6 inbound) and `metadata` (8 inbound). `location-provider` is the operations-side fanout king at 9 inbound.

**Data-stores rollup published** (`relations/data-stores.md`): 35-row PG table + Redis + ES + GCS + etcd + external. **6 services run pool-size ≤ 10** (`notification-backend` 5, `public-tracking-backend` 5, `load-bookmark-backend` 4 prod, `location-provider` 4, `autoims-backend` 10, `driveaway-backend` 10). The 4 smallest pools all sit on the request path of either fleet-wide fanout or public-facing traffic.

## Recommended next deepening passes (Phase 4.9, optional)

1. **Two new P0s now actionable on the actual repos** (separate work, not catalog edits):
   - `rateengine`: minimum-viable is adding `timeout=(5, 30)` to every `requests.Session()` call. Real answer is Django/DRF upgrade.
   - `trip-planner.CtmsClient`: add `quarkus.rest-client.ctms-api.connect-timeout` + `read-timeout`. Two lines in `application.properties`.
2. **Communication-domain depth**: the parallel-paths question between `notification-backend` and `notification-orchestrator` still needs an owner. No more useful catalog work is possible until that decision is made.
3. **Integrations-domain depth**: 11 stubs, 2 seeds (`integrations-backend`, `autoims-backend` after re-domain). Pick the 3 highest-traffic stubs.
4. **Identity-domain depth** is now thinner after the re-domain (10 stubs, 2 seeds). `user-backend` + `impersonator` cover the high-value surface; remaining stubs likely yield diminishing returns.
5. **Catalog hygiene**: regenerate `_index.md` (done in this pass); consider auto-deriving `domains/<domain>.md` member-lists from shadow frontmatter via a script so the rollups stay current.
6. **Pool-size right-sizing PR sweep**: outside the catalog, raise `notification-backend` (5 → 16), `public-tracking-backend` (5 → 16), `load-bookmark-backend` (4 prod → 16), `location-provider` (4 → 16). All are 1-line PRs and retire the most concentrated risk in `data-stores.md`.

## Phase 5 / Entity catalog — done 2026-05-15

Added the first cross-repo **business-entity catalog** to the map (`relations/entity-catalog.md`, 25 per-entity pages under `domains/entities/`, `## Entities` rollups injected into 58 Java-shadow docs).

**Why now.** The fleet has no shared contract layer (zero service-level proto / GraphQL, only 2 OpenAPI specs, `models-lib` shared but covers ≤30% of the entity flow). The same logical entity — `Vehicle`, `User`, `Company`, `Load`, `Posting`, `Transaction`, `Attachment`, `Negotiation` — is redefined across 5-20+ repos as locally-owned synced copies. That cross-repo divergence is the most expensive-to-derive part of the map and was the biggest gap after Phase 4.9.

**Pipeline (two scripts, stdlib-only):**

- `scripts/extract_entities.py` — walks every repo whose shadow `stack:` starts with `Java/` (~73 repos) + `models-lib` as a pseudo-repo. Detects `@Entity`, `@Embeddable`, Lombok DTOs, and records; filters Hibernate Envers infrastructure, pagination wrappers, framework configs, and Pub/Sub envelopes. Emits `relations/entity-catalog.raw.tsv` (one row per declared class — currently 2,627 rows: 2,402 DTOs / 198 JPA / 23 mapped-superclasses / 4 embeddables). Runs in ~2 s; zero parse errors over the whole fleet.
- `scripts/cluster_entities.py` — normalizes class names (strip suffix → strip service prefix → apply `entity_aliases.yaml` overrides), computes composite score `occurrence + 2 * distinct-domain-count`, picks owning service, renders 25 per-entity pages with REST + Spring/Panache-repository + Pub/Sub use-case rollups. Cross-references `relations/event-schemas/` `canonical-dto:` field (resolves 33 schema bindings). Full run ~18 s.

**Hand-curated input:** `relations/entity_aliases.yaml` — 35 canonicals, 99 aliases, 3 split rules. Force-splits `Message` (chat vs queue) and `Notification` (entity vs payload). Reviewer-driven side-channel `relations/entity-catalog.unaliased.tsv` (99 unaliased canonicals with occurrence ≥3 from this pass) drives the next tightening loop.

**Top-25 picture (after v1 tightening):**

| Rank | Canonical | Variants | Repos | Domains |
|---:|---|---:|---:|---|
| 1 | `Company` | 42 | 18 | listings-trade, integrations, operations, communication, identity, pricing-billing |
| 2 | `Vehicle` | 42 | 20 | listings-trade, integrations, operations, communication, platform, pricing-billing |
| 3 | `User` | 39 | 18 | listings-trade, integrations, operations, communication, identity, platform |
| 4 | `Attachment` | 25 | 10 | listings-trade, integrations, operations, platform |
| 5 | `Location` | 25 | 15 | listings-trade, integrations, operations, communication, platform |
| 6 | `Load` | 25 | 9 | listings-trade, operations |
| 7 | `Trip` | 21 | 6 | operations |
| 8 | `Posting` | 16 | 7 | listings-trade, integrations |
| 9 | `Offer` | 16 | 5 | listings-trade |
| 10 | `GpsPosition` | 14 | 7 | operations, communication, platform |
| 11 | `Negotiation` | 13 | 6 | listings-trade, integrations |
| 12 | `VehicleSpecification` | 14 | 4 | listings-trade |
| 13 | `Quote` | 13 | 3 | pricing-billing |
| 14 | `Driver` | 11 | 3 | operations |
| 15 | `CompanyConfig` | 10 | 5 | integrations, pricing-billing |
| 16 | `Transaction` | 9 | 4 | pricing-billing |
| 17 | `Contact` | 9 | 7 | listings-trade, operations |

Full table at `relations/entity-catalog.md`.

**Concrete cross-cutting findings surfaced by the pass:**
- **`Vehicle` is the most-replicated entity in the fleet** — 42 declarations across 20 repos and 6 domains. The 20 repos each maintain their own field-level view (JPA in inventory-backend has 52 fields; `InventoryUnitDto` in the same repo has 94; `VehicleDto` variants run from 0-fields to 64-fields). Strong candidate for a schema-coordination ADR.
- **`Company` and `User` each touch 18 repos** — every entity-aware service in the fleet maintains some local projection. The `DbCompany` / `DbUser` shape (used by `db-syncer` consumers: `load-recommender`, `notification-orchestrator`, `pusher`, `trip-planner`) is a separate de-facto "syncer view" that has no documented contract.
- **CTMS-side mirrors** (`CtmsPosting`, `CtmsNegotiation`, `CtmsAttachment`, `CtmsVehicle`) are merged into the corresponding canonical here, so divergence shows up in the variants table rather than as a separate entity. The 56-field `CtmsVehicleReadDto` in `models-lib` is the widest projection.
- **`VehicleSpecification` is a stable embedded shape across 4 repos** — already a candidate for promotion to a shared model.

**Limitations of v1 (documented in `entity-catalog.md` frontmatter):**
- Java-only. TS / Python / Node entity discovery is deferred.
- Field shapes are persisted / serialized shapes, not Java API surface (Lombok / hand-written accessors not surveyed).
- The owning-service heuristic is REST-count-then-field-count and can be wrong for entities owned by event-only services.
- `## Entities` shadow-doc sections are injected into all Java shadows with detected entities (auto-determined), not gated on seed/stub. 58 shadows touched.

**Recommended next deepening passes (Phase 5.1, optional):**
1. **Tighten `entity_aliases.yaml`** against the 99-row `unaliased.tsv` side-channel. Highest-impact remaining merges: `DateDetail` → `DateRange`?, `Filter` → maybe split per repo, `SavedSearch` is real, `FileContent` → maybe `Attachment`.
2. **Hand-edit per-entity narratives** (Section 1 "What it is" in the top-5 pages). Currently auto-stubbed with `TODO: human narrative`. Vehicle, User, Company, Load, Posting are worth one paragraph each.
3. **Promote `entity-catalog.md` to a real "schema-coordination" track**: pick `Vehicle` and write a 1-page ADR proposing a shared read-model in `models-lib` to retire the 20-way divergence.
4. **Drift integration**: extend `scripts/drift_check.py` to flag when `entity-catalog.raw.tsv` is older than its source repos' HEADs.
5. **TS entity discovery** (`backoffice-frontend`, `loadboard-frontend`, etc.) — frontends carry an additional projection layer. Out of v1 scope per user.

## Cross-repo data-flow convention (added 2026-07-27)

Multi-hop data-flows that span 5+ services and aren't visible from any single shadow doc (e.g. how a value is assembled/rewritten as it crosses service boundaries) are recorded in **`relations/<topic>-flows.md`** as an **ordered producer→consumer hop table**: one row per hop with `repo | role | what-it-does | path:line evidence`, plus the async topic name(s) and any data-store (ES index / bucket / table) the flow reads or writes. **Role** classifies each hop as `mints` / `owns` / `relays` / `stores-path` / `literal-lookup` so the single **fix site** (`owns`) is unambiguous vs. relays and literal-lookups. Cross-link every participating shadow doc back to the flow entry from its *Relevant ADRs / docs* section (one line, naming the hop role).

First instance: **`relations/media-url-flows.md`** — the LBv3 load/attachment media-URL pipeline (`loadboard-backend` → `platform-backend` → `syncer` → `cube` → `media-proxy`, seeded by `attachment-backend`); the root-cause map for SCP-14564. `syncer` owns the URL construction (`CtmsMediaUrlTransformer`); the 6 participating shadows are cross-linked.

