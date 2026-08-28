---
repo: keycloak-password-reset-link
path: ~/projects/ship-cars-usa/keycloak-password-reset-link
stack: Java 11 / Keycloak SPI plugin (Keycloak 26.7.1 SPI)
domain: identity
shape: single-module
last-synced-commit: 7d5b6aa71ed50529b2ddf8c83f8938edf589cbc2
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# keycloak-password-reset-link

## What it is
**Keycloak SPI plugin (not a service)** — `cars.ship.keycloak:reset-password-extension` 1.0.6, built against Keycloak 26.7.1 (`pom.xml`; all KC deps `provided`). Java 11 (`maven.compiler.source/target=11`). Adds an **admin-callable REST endpoint** that **returns** a clickable reset-password link directly to the caller instead of Keycloak's default flow, which emails the user.

Per `README.md`: `POST <realm-url>/reset-password` (form-data), `user_email` (required), `redirect_uri` (optional success-page URI). Caller must present a **bearer token whose user has the `admin` role** (`ResetPasswordResource.java:41` `ADMIN_ROLE_NAME = "admin"`), and the realm's "Forgot Password" option must be enabled. When AppsFlyer formatting is on, the link is wrapped with deep-link params (`ResetPasswordResource.java:107-111`). A second resource provider (`RemoveFederationLinkResourceProvider`) handles LDAP federation-link cleanup.

## How it fits
- **What it provides:** two `RealmResourceProvider`s — the `reset-password` endpoint (`ResetPasswordResourceFactory` is `@AutoService(RealmResourceProviderFactory.class)`, `ResetPasswordResourceFactory.java:10`) and a federation-link removal resource (`RemoveFederationLinkResourceProvider`) — plus a custom `ActionTokenHandler` (`CustomResetCredentialsHandlerFactory`, registered via `META-INF/services/org.keycloak.authentication.actiontoken.ActionTokenHandlerFactory`) that fires when the generated link is clicked.
- **Consumed by:** the `keycloak` Docker image bundles this JAR into `/opt/keycloak/providers/`; internal Ship.Cars admin/API flows that need to drive a password reset without Keycloak's email path. It is also a **hard build+runtime dependency of `keycloak-phone-login-plugin`** (that repo depends on `reset-password-extension` 1.0.5).
- **Consumes API of:** Keycloak's own session API (`UserModel` lookup by email); AppsFlyer URL construction (no external HTTP — URL string composition only).
- **Owns data store:** none — stateless plugin; reads from the Keycloak session.

## Build / test / run
```
./mvnw clean package        # produces target/reset-password-extension-1.0.6.jar
./mvnw test                 # JUnit 5.9.3 + Mockito 5.3.1
# Drop the jar into Keycloak's /opt/keycloak/providers/ (bundled by the `keycloak` repo image)
# Published to GitHub Packages: maven.pkg.github.com/ship-cars-usa/keycloak-password-reset-link
```

## Key abstractions
- `ResetPasswordResource` — `src/main/java/cars/ship/keycloak/extension/rest/ResetPasswordResource.java` — handles `POST /reset-password`; admin-role check; user lookup by `user_email`; mints `CustomResetCredentialsToken`; returns the reset link (optionally AppsFlyer-wrapped).
- `ResetPasswordResourceFactory` — `.../rest/ResetPasswordResourceFactory.java` — `@AutoService`-registered `RealmResourceProviderFactory`; provider ID from `getId()`.
- `RemoveFederationLinkResource` / `RemoveFederationLinkResourceProvider` — `.../rest/` — LDAP federation-link cleanup resource.
- `CustomResetCredentialsHandler` / `CustomResetCredentialsHandlerFactory` — `.../handler/` — `AbstractActionTokenHandler<CustomResetCredentialsToken>` invoked when the reset link is clicked; triggers Keycloak's reset-credentials flow. Factory registered via `META-INF/services`.
- `CustomResetCredentialsToken` — `.../handler/CustomResetCredentialsToken.java` — serializable action token.
- `AppsflyerConfig` — `.../config/AppsflyerConfig.java` — reads AppsFlyer settings from **environment variables**: `KC_SPI_PASSWORD_RESET_APPSFLYER_ENABLED`, `KC_SPI_PASSWORD_RESET_INTERNAL_ENDPOINT_APPSFLYER_ENABLED`, `KC_SPI_PASSWORD_RESET_APPSFLYER_LINK_URL`, `KC_SPI_PASSWORD_RESET_APPSFLYER_INTERSTITIAL_PAGE_BASE_URL`.
- `AppsflyerUrlBuilderUtil` — `.../util/AppsflyerUrlBuilderUtil.java` — deep-link URL composition (`buildAppsFlyerUrl`).

## Don't-do-here / gotchas
- **AppsFlyer env-var names changed.** The current config keys are the `KC_SPI_PASSWORD_RESET_APPSFLYER_*` set above (`AppsflyerConfig.java`). Older docs referencing `KEYCLOAK_INTERNAL_RESET_PASSWORD_ENDPOINT_APPSFLYER_FORMAT_ENABLED` are stale.
- **Source/target Java 11 vs Keycloak runtime Java 17+** — still on 11 as of 1.0.6; works in practice but blocks newer language features. Contrast with `keycloak-phone-login-plugin` (Java 17). Consider bumping.
- **Email-based user lookup** — if more than one user shares the email (LDAP-federation edge), the first match wins; no selector or error.
- **`realm.isResetPasswordAllowed()` is a hard gate** — the endpoint 400s if the realm's "Forgot Password" setting is off, even for admins who disabled it deliberately.
- **Action-token lifetime is the realm-wide `actionTokenGeneratedByUserLifespan` for `RESET_CREDENTIALS`** — not customizable per-call.
- **No built-in audit of who-generated-a-link-for-whom** — Keycloak's standard admin event log doesn't capture this custom endpoint. SOC2/SOX evidence needs a custom emitter.
- **Endpoint auth is "bearer token with `admin` role" only** — a compromised admin token grants reset-link generation for any user. Consider IP allowlist + per-call audit.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/keycloak.md` — deployment image that bundles this plugin.
- `~/projects/codebase-map/repos/keycloak-phone-login-plugin.md` — depends on this JAR (1.0.5+) at build+runtime.
- `~/projects/codebase-map/domains/identity.md`.
