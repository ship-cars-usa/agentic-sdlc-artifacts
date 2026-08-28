---
repo: keycloak-phone-login-plugin
path: ~/projects/ship-cars-usa/keycloak-phone-login-plugin
stack: Java 17 / Keycloak SPI plugin (Keycloak 26.7.1 SPI)
domain: identity
shape: single-module
last-synced-commit: 6f82c815cefbaa00c5d9ce86f9b432e2d166cfd8
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# keycloak-phone-login-plugin

## What it is
**Keycloak SPI plugin (not a service)** — `cars.ship.keycloak:phone-login` 1.0.6, built against Keycloak 26.7.1 (`pom.xml`), Java 17. Bundled into the `keycloak` Docker image. Enables **phone-number-based login and password-reset** and several related auth-flow steps by shipping custom `Authenticator`/`FormAuthenticator` SPI providers. Packaged as a `jar-with-dependencies` (maven-assembly-plugin) so its bundled `notification-client` + `quarkus-pubsub` deps ride along.

Per `README.md`: users log in with a phone number **only if `verifiedPhoneForMfa=true`**; the plugin does not rename the Keycloak username, it just falls back to phone lookup when email lookup fails. Operators must swap the default `browser` and `reset credentials` flow steps for this plugin's replacements (custom flows, since built-ins can't be edited).

## How it fits
- **What it provides — the registered SPI providers (all via `@AutoService`):**
  1. **`auth-phone-username-password-form`** (`PhoneUsernamePasswordForm`) — replaces the standard `UsernamePasswordForm`; login by username/email **or** phone (attribute `userPhoneNumber`, gated on `verifiedPhoneForMfa`).
  2. **`auth-phone-username-form`** (`PhoneUsernameForm`) — **new** passwordless "Username/Phone Form"; selects a user by username, email, or phone with no password prompt.
  3. **`choose-user-email-or-phone`** (`ChooseUserEmailOrPhone`) — reset-flow user-selection step; records the email-vs-phone channel choice in the auth session.
  4. **`reset-credential-email-or-phone`** (`ResetCredentialEmailOrSms`, "Send Reset Email or SMS") — routes the reset link via email (`EmailTemplateProvider`) **or** SMS (via bundled `notification-client` → Pub/Sub), with a Firebase Dynamic Link deep-link and an external URL shortener for SMS.
  5. **`direct-grant-django-authenticator`** (`DjangoDirectGrantAuthenticator`) + `DjangoAuthenticator` — optional legacy-user password validation against a Django backend.
  6. **`fingerprint-auth`** (`fingerprint/FingerprintAuthenticator`, "Add fingerprint") + `fingerprint/UpdatePasswordPatched` ("Update Password (handles fingerprint)") — **new** fingerprint-related required-action / authenticator.
- **Consumes API of:** Keycloak session API; an external **URL shortener** (`UrlShortener`, endpoint from `Config.scope("phone-login").get("shortener_url")`, via Apache HttpClient 4.5.14); a configurable **Django backend** for legacy auth.
- **Publishes events to:** Pub/Sub via the bundled `ship.cars.notification:notification-client` 0.14.0 (+ `quarkus-pubsub` runtime 1.0.0) for SMS-link delivery.
- **Hard dependency:** `cars.ship.keycloak:reset-password-extension` 1.0.5 (the `keycloak-password-reset-link` repo) is a compile+runtime dependency — both JARs must be in `/providers/`.
- **Owns data store:** none — stateless; phone attributes live on the Keycloak `UserModel`.

## Build / test / run
```
./mvnw clean package        # produces target/phone-login-1.0.6-jar-with-dependencies.jar
./mvnw test                 # JUnit 5.10.3 + testcontainers-keycloak 4.3.1 (Testcontainers-driven)
# Drop the jar into Keycloak's /opt/keycloak/providers/
# HARD DEPENDENCY: keycloak-password-reset-link (reset-password-extension) must also be present
# Published to GitHub Packages: maven.pkg.github.com/ship-cars-usa/keycloak-phone-login-plugin
```
After install, edit the `browser` and `reset credentials` flows in the KC admin console to substitute this plugin's steps (see `README.md`).

## Key abstractions
- `PhoneUsernamePasswordForm` — `.../phone/PhoneUsernamePasswordForm.java` — `PROVIDER_ID = auth-phone-username-password-form`; `PHONE_NUMBER_ATTRIBUTE_NAME = "userPhoneNumber"`, `PHONE_NUMBER_VERIFIED_ATTRIBUTE = "verifiedPhoneForMfa"`; phone fallback in user lookup.
- `PhoneUsernameForm` — `.../phone/PhoneUsernameForm.java` — `auth-phone-username-form`; passwordless user selection ("Username/Phone Form", added in this sync).
- `ChooseUserEmailOrPhone` — `.../phone/ChooseUserEmailOrPhone.java` — `choose-user-email-or-phone`; persists the reset channel into the auth session.
- `ResetCredentialEmailOrSms` — `.../phone/ResetCredentialEmailOrSms.java` — `reset-credential-email-or-phone`; branches on channel; for SMS calls `UrlShortener` → `DeepLinkProvider` → `NotificationClientProvider`.
- `UrlShortener` — `.../phone/UrlShortener.java` — Apache HttpClient POST to `Config.scope("phone-login").get("shortener_url")`.
- `DeepLinkProvider` — `.../phone/DeepLinkProvider.java` — Firebase Dynamic Link template, hardcoded domain `https://ydqx9.app.goo.gl/?link=%s&apn=%s&ibi=%s&isi=%s`.
- `NotificationClientProvider` — `.../phone/NotificationClientProvider.java` — wires the bundled `notification-client` for SMS publish.
- `PhoneParser` — `.../phone/PhoneParser.java` — region-aware phone parse/validate.
- `LocalUserStorageManager` — `.../phone/LocalUserStorageManager.java` — user lookup by phone.
- `MessageResolver`, `EpodConfig` — `.../phone/` — reset-message text resolution and EPOD-client detection config.
- `DjangoAuthenticator` / `DjangoDirectGrantAuthenticator` / `django/Config` — `.../phone/django/` — optional legacy-auth path (`direct-grant-django-authenticator`).
- `fingerprint/FingerprintAuthenticator` (`fingerprint-auth`) + `fingerprint/UpdatePasswordPatched` — `.../phone/fingerprint/` — fingerprint required-action / patched update-password.

## Don't-do-here / gotchas
- **Firebase Dynamic Links domain `ydqx9.app.goo.gl` is hardcoded** in `DeepLinkProvider`. Firebase Dynamic Links is deprecated by Google (shutdown announced) — links through this template will eventually stop resolving. Migration to App Links / Universal Links or an in-house deep-link gateway is needed.
- **URL shortener HTTP call** — Apache HttpClient with no timeout override (`UrlShortener`); a hung shortener stalls the reset flow.
- **Django fallback** inherits Keycloak's `HttpClientProvider` default (~30 s) unless overridden — a slow Django stalls auth before falling back.
- **SMS delivery has no DLQ / outbox** — a Pub/Sub publish failure means the user sees "reset sent" but no SMS arrives.
- **Phone-attribute naming**: this plugin keys login on `userPhoneNumber` + the `verifiedPhoneForMfa` flag; keep in mind `keycloak-mfa-plugin` also uses `verifiedPhoneForMfa`. Don't let the attribute schemas drift.
- **Hard runtime dependency on `reset-password-extension`** (1.0.5) — plugin fails to load if that JAR isn't in `/providers/`. The `keycloak` image Dockerfile must bundle both.
- **`commons-lang3` is `provided`** (not shaded) by design — bundling it in the jar-with-dependencies triggers KC issue #26396. Keep it `provided`; the `quarkus-pubsub`/`notification-client` deps deliberately exclude `ship.cars.commons:commons` and Quarkus OTel/core/arc to avoid class conflicts inside Keycloak.
- **Java source-target 17** here vs Java 11 in `keycloak-password-reset-link`; consider unifying the plugin toolchains.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/keycloak.md` — bundled image.
- `~/projects/codebase-map/repos/keycloak-password-reset-link.md` — hard build+runtime dependency.
- `~/projects/codebase-map/repos/keycloak-mfa-plugin.md` — sibling MFA plugin (shares `verifiedPhoneForMfa`).
- `~/projects/codebase-map/domains/identity.md`.
