---
repo: keycloak
path: ~/projects/ship-cars-usa/keycloak
stack: Keycloak 26.0.5 (Quarkus distribution) — Docker image build
domain: identity
shape: single-module
last-synced-commit: dd6613103263b9fbeca1d18a99e3be26eeb9c205
last-synced-date: 2026-05-11
maintainer: unknown
status: stale
---

# keycloak

## What it is
**Custom Keycloak deployment-config repo**, not a service in the usual sense. Builds a Docker image on top of `quay.io/keycloak/keycloak:26.0.5` (the Quarkus-based Keycloak), bundling four Ship.Cars SPI plugins into `/opt/keycloak/providers/` (`keycloak-events-plugin`, `keycloak-password-reset-link`, MFA, phone-login) and a custom `shipcars` theme. Keycloak itself is the fleet-wide **OIDC / OAuth2 provider** consumed by `user-backend`, `loadboard-backend`, `socket-server`, every `keycloak-resource-server`-configured Quarkus service, and the frontends. This repo is the build-and-deploy boundary for that.

## How it fits
- Consumes API of: GitHub Packages (Maven) at image-build time to fetch each plugin JAR (requires `GITHUB_READ_TOKEN`).
- Publishes events to: via the bundled `keycloak-events-plugin` — Pub/Sub topic `${KC_SPI_EVENTS_TOPIC}` carrying enriched `ExtendedEvent`s; consumed by `fraud-detector` and `pusher`.
- Subscribes to: none.
- Owns data store: Keycloak's own PostgreSQL (configured externally; not in this repo).

## Build / test / run
```
docker build --build-arg GITHUB_READ_TOKEN=... -t shipcars/keycloak:26.0.5 .
docker compose up   # local dev — note this pins Keycloak 12.0.2, NOT 26.0.5
```

## Key abstractions
- `Dockerfile` — multi-stage UBI9 builder; downloads 4 plugin JARs at fixed versions; copies the `shipcars` theme.
- `themes/shipcars/` — custom FreeMarker templates + CSS for login / registration / account pages.
- `standalone.xml` / `standalone-ha.xml` — legacy server-config XML retained in repo for reference (Quarkus Keycloak no longer needs these for primary config, but the files still document the desired realm settings).
- `docker-compose.yml` — local dev environment.

## Don't-do-here / gotchas
- **Version drift between local and prod**: `docker-compose.yml` pins Keycloak **12.0.2**; the Dockerfile pins **26.0.5**. Local testing does not reflect prod behavior. Update or remove the compose file's pin.
- **Plugin versions hardcoded in the Dockerfile** (`1.0.5`, `1.0.6`, etc.). A plugin bump requires editing the Dockerfile; no env-var override. Consider parameterizing via build args.
- **`GITHUB_READ_TOKEN` build-arg is mandatory** — the build fails without it. No fallback to public artifacts. Document the operational requirement.
- **Plugin compile-target version skew**: `keycloak-events-plugin` is built against Keycloak **24.0.4** SPI; the deployed image is **26.0.5**. SPI is mostly stable across minors, but verify on every plugin or KC upgrade.
- **Theme path changed in Keycloak 26**: Quarkus-based Keycloak uses `/opt/keycloak/themes/`. Dockerfile is correct, but anyone backporting to KC < 26 will need `/opt/jboss/keycloak/themes/`.
- **No automated upgrade tests** — `standalone.xml` and realm-config drift between this repo and the actual Keycloak admin state isn't checked. A drift-detection script (export realm JSON, diff against checked-in baseline) would help.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/keycloak-events-plugin.md` — bundled event-emitter plugin.
- `~/projects/codebase-map/repos/keycloak-password-reset-link.md` — bundled reset-link plugin.
- `~/projects/codebase-map/repos/keycloak-mfa-plugin.md` (stub).
- `~/projects/codebase-map/repos/keycloak-phone-login-plugin.md` (stub).
- `~/projects/codebase-map/domains/identity.md`.
