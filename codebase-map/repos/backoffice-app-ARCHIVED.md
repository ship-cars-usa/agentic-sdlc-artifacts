---
repo: backoffice-app-ARCHIVED
path: ~/projects/ship-cars-usa/backoffice-app-ARCHIVED
stack: Python / Flask 2.3 / Flask-Dance (OAuth) / Flask-Login / Flask-WTF
domain: platform
shape: archived Flask app (predecessor of `backoffice-backend` + `backoffice-frontend`)
last-synced-commit: ea96baa8e7ddfbb81ef894e3b19e5c261910da66
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# backoffice-app-ARCHIVED

## What it is
**Archived predecessor** of the modern BackOffice (NestJS backend + Vite frontend split). Python **Flask 2.3** monolithic web app with:

- `Flask-Dance` for OAuth flows (likely Google / Keycloak SSO).
- `Flask-Login` for session management.
- `Flask-WTF` for form rendering + CSRF.

Repo name carries the `-ARCHIVED` suffix indicating its retirement status. **Last commit 2023-07-17** (`ARCH-000 Docker files`) — 2.5+ years stale. The modern BackOffice migrated to the NestJS + Vite stack, retiring this Flask app.

## How it fits

- **Retired.** Replaced by `backoffice-backend` (NestJS) + `backoffice-frontend` (Vite).
- **No longer deployed** (presumably — confirm helm chart status before formal archive).
- **Historical artifact.** Code may still inform what features the modern BackOffice needs to cover.

## Build / test / run

Not relevant — archived.

## Don't-do-here / gotchas

- **Don't pattern-match new admin tooling after this repo.** The modern path is `backoffice-backend` + `backoffice-frontend`.
- **Archive-formally if helm confirms no active deploy.** The name suffix already declares retirement; ensure CI / Argo are aligned.
- **Flask + Python 3.x deps may still be useful for understanding what features the modern BackOffice should cover** — read the source for feature parity, not for code reuse.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/backoffice-backend.md` — modern successor.
- `~/projects/codebase-map/repos/backoffice-frontend.md` — modern UI successor.
- `~/projects/codebase-map/relations/infrastructure-triage.md` — flag for formal archive.
- `~/projects/codebase-map/domains/platform.md`.
