---
domain: identity
status: draft
owner-team: unknown
member-services: 9
last-reviewed: 2026-05-12
---

# Domain — identity

## Purpose
User and authentication. Keycloak as the IdP, custom Keycloak SPIs for events / 2FA / phone login / password reset. User account lifecycle, impersonation for support, hashing utilities.

## Member services
| Repo | Role | Stack |
|---|---|---|
| user-backend | User and company management for LoadMate | Java/Spring Boot 3.2.12 |
| user-frontend | user / company / billing UI (`@shipcars/user` single-spa MFE) | TypeScript / React 18 / Webpack 5.105 / MUI v6 / axios 1.15 |
| keycloak | Keycloak 26.0.5 custom Docker image (theme + 4 bundled SPIs) | Keycloak distribution / Quarkus |
| keycloak-events-plugin | Keycloak SPI — event listener | Java/Quarkus |
| keycloak-mfa-plugin | Keycloak SPI — 2FA login step | Java/Quarkus |
| keycloak-phone-login-plugin | Keycloak SPI — phone-number login | Java/Quarkus |
| keycloak-password-reset-link | Keycloak SPI — password reset link generator | Java/Maven |
| impersonator | user impersonation service | Go |
| hasher | hasher service | Go |

## Key flows
- **Login:** browser → Keycloak (with our custom SPIs for MFA + phone login) → JWT issued → all backends validate JWT (Quarkus services use `quarkus-oidc`; Spring services use `spring-boot-starter-oauth2-resource-server`).
- **Support impersonation:** support engineer → `impersonator` (Go) → issues a scoped JWT to act as a customer. Used by `contract-pricing-backend` per its seed shadow.
- **User lifecycle:** `user-backend` is the system-of-record for user / company; `user-frontend` is the admin UI; `user-activity-tracker` records analytics events.

## Data stores
- Keycloak: Postgres (its own DB; standard Keycloak deployment).
- `user-backend`: Postgres.
- `user-activity-tracker`: TBD — likely time-series-friendly given "event tracking + analytics" purpose.

## Cross-cutting concerns
- `user-backend` is Spring Boot 3.2.12, not Quarkus — `PROJECTS_INDEX.md` miscategorizes it.
- Custom Keycloak SPIs are tied to a specific Keycloak version — when upgrading Keycloak, all 4 plugins need recompilation/testing.
- `impersonator` is the only auth-adjacent service in Go; rest of the domain is JVM.

## Open questions / known gaps
- ~~The `keycloak/` repo says "Keycloak theme + Dockerfile"~~ — resolved (Phase 4.10): custom Docker image bundling Keycloak 26.0.5 + 4 SPIs + Ship.Cars theme. Version-drift between `docker-compose.yml` (KC 12.0.2) and the Dockerfile (KC 26.0.5) flagged in the seed.
- ~~What's the JWT validation pattern across the 65 backend services?~~ — resolved (Phase 4.10 + earlier seeds): Quarkus services use `quarkus-oidc` validating against Keycloak's RS256 public key; Spring services use `spring-boot-starter-oauth2-resource-server` (wired via `spring-commons`). The legacy `socket-server-old` HS256 JWT path is the exception — uses a shared hardcoded secret (P0 per the `socket-server-old` seed).
- ~~Where does `hasher` get used?~~ — resolved (Phase 4.10): tiny Go ID-obfuscation service (`Hashids` lib); **not a security control** — reversible by anyone with salt + alphabet.
- `user-activity-tracker` was re-domained `identity` → `analytics` in Phase 4.8 (event tracking + HyperLogLog + Parquet export is analytics work, not identity). Rollup updated.

## Related ADRs
- None recorded yet.

## Coverage
**9 of 9 shadows are `seed`** — identity domain is **catalog-complete** as of 2026-05-12 (Phase 4.19). Last seed: `user-frontend`. Every active service in the identity domain has a `seed`-status shadow doc.
