---
repo: keycloak-mfa-plugin
path: ~/projects/ship-cars-usa/keycloak-mfa-plugin
stack: Java 21 / Keycloak SPI plugin (Keycloak 26.0.5 SPI)
domain: identity
shape: single-module
last-synced-commit: eec8d534f39551cba1c645d60204d6c47edbe148
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# keycloak-mfa-plugin

## What it is
**Keycloak SPI plugin (not a service)** — Java 21 JAR bundled into the `keycloak` Docker image. Implements `Authenticator` (provider ID `mfa-authenticator`) to inject a 2FA / OTP verification step into the browser login flow. After username/password, generates a time-limited code (default 6 digits, 5 min TTL) and sends it via SMS (default) or email through `quarkus-notification-client` → Pub/Sub topic. Resend throttled (default 15 s). Also ships a `ConditionalAuthenticator` (`mfa-configured-condition`) that gates MFA to users with a configured MFA role, and a `CredentialProvider<TrustedDeviceCredentialModel>` (`trusted-device`) that lets users skip MFA on repeat login from the same device (UA + IP hash, encrypted).

## How it fits
- Consumes API of: Keycloak session API for user attribute lookup (`verifiedPhoneForMfa`, `verifiedEmailForMfa`); Keycloak's native brute-force lockout (`UserLoginFailureModel`).
- Publishes events to: Pub/Sub topic `${mfa.notification-topic}` (e.g., `keycloak-mfa-events`) via `quarkus-notification-client` → consumed by `notification-backend` / `notification-orchestrator` for SMS/email delivery. Also emits Keycloak `EventBuilder` events (`MFA_REQUESTED`, `MFA_SEND`, `MFA_CODE_OK`, `MFA_CODE_ERROR`, `MFA_RESEND`) that flow through `keycloak-events-plugin` onto the main events topic.
- Subscribes to: not applicable.
- Owns data store: none — OTP state held in the Keycloak auth session.

## Build / test / run
```
./mvnw clean package
# Produces target/mfa-extension-*-jar-with-dependencies.jar
# Drop into Keycloak's /opt/keycloak/providers/ (the `keycloak` repo's Dockerfile bundles this)
```

## Key abstractions
- `MfaAuthenticatorFactory` — provider ID `mfa-authenticator`; config keys: `code-length`, `code-ttl`, `code-alphabet`, `resend-wait-period`, primary/secondary channels.
- `MfaAuthenticator` — generates + sends code, validates submission, enforces resend throttle, decides primary channel (SMS if `verifiedPhoneForMfa=true`, else email).
- `MfaConfiguredConditionFactory` / `MfaConfiguredCondition` — runs the MFA step only when the user has the configured `mfa-role`.
- `TrustedDeviceCredentialProviderFactory` / `TrustedDeviceCredentialProvider` — provider ID `trusted-device`; skip-MFA-from-known-device token, encrypted.
- `NotificationClientProvider` — lazy-init singleton wiring `quarkus-notification-client` to scope `mfa`.

## Don't-do-here / gotchas
- **No timeout on Pub/Sub publish** — `NotificationClientImpl.future.get()` (the fleet-wide issue called out in `quarkus-notification-client`'s shadow) blocks the Keycloak auth-thread. A hung Pub/Sub stalls *user logins*.
- **No DLQ on publish failure** — `IOException` is logged + swallowed (inherited from `quarkus-notification-client`); user sees "code sent" but no SMS arrives.
- **Auth-session-only storage** — if the Keycloak pod with the user's auth session restarts, the in-flight code is lost; user must resend.
- **`commons` excluded** from runtime to dodge GH-issue-26396 (Keycloak/commons-lang3 conflict). Document this on any dependency bump.
- **Hardcoded default alphabet** (`0123456789`); admin can override but no validation that the override is sane.
- **Asymmetric channel fallback** — only offers email-as-fallback if BOTH channels are verified. If admin enables phone but user only verified email, no fallback is offered. Document the assumption.
- **SPI version skew** — built against KC 26.0.5 SPI; deployed against KC 26.0.5; no current drift, but verify on KC upgrade.
- **MFA role config is global per flow** — multi-tenant scoping requires multiple flows.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/keycloak.md` — bundled image.
- `~/projects/codebase-map/repos/keycloak-events-plugin.md` — sibling event emitter.
- `~/projects/codebase-map/repos/keycloak-password-reset-link.md` — sibling SPI plugin.
- `~/projects/codebase-map/repos/keycloak-phone-login-plugin.md` — sibling SPI plugin (phone-based login + reset).
- `~/projects/codebase-map/repos/quarkus-notification-client.md` — publish path.
- `~/projects/codebase-map/domains/identity.md`.
