---
repo: catch-me
path: ~/projects/ship-cars-usa/catch-me
stack: Go / Fiber v2 / logrus JSON logging
domain: infrastructure
shape: small Go web service (55 files, `core/` + `handler/` + `frontend/`)
last-synced-commit: bfc949fcf8e987e07781dc6410dfa50a650c85f2
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# catch-me

## What it is
"**Catch Me**" — Go Fiber v2 web service. Per `main.go`: listens on `:3000`, registers routes from a `router` package, uses a `LogMiddleware` from `handler`, has body-limit 20MB + 128kB read buffer. Has a `frontend/` directory implying it serves an embedded UI.

Without deeper reading of `core/` / `handler/` / `frontend/`, the precise purpose isn't obvious from the README (`Catch Me`). Could be a generic webhook-capture / request-inspection / health-check / "catch-all 404 with helpful redirects" tool — common Go-Fiber service patterns. Last commit 2025-10-10 (Claude config sweep only); content older.

## How it fits

- **Standalone Go service** — Fiber v2 + logrus pattern.
- **Listens on :3000.**
- **Serves an embedded `frontend/`** — implies an admin UI / dashboard for whatever the service catches.

## Build / test / run
```
go build ./...
./catch-me
```

## Don't-do-here / gotchas

- **Purpose not clear from README.** Read `core/` and `handler/router.go` to understand actual function before changing behavior.
- **20MB body limit** is generous — confirm whether large-payload handling is the design intent.
- **Listen port :3000** is a common dev-server default — verify production deployment routes it correctly.

## Relevant ADRs / docs
- `~/projects/codebase-map/domains/infrastructure.md`.
