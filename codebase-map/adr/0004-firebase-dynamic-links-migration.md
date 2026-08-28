# ADR 0004 — Migrate off Firebase Dynamic Links

**Status:** Proposed
**Date:** 2026-05-12
**Forcing function:** Google announced shutdown of Firebase Dynamic Links (FDL).
**Context author:** codebase-map maintenance

## Context

`keycloak-phone-login-plugin` (a bundled Keycloak SPI plugin in the `keycloak` Docker image) wraps every SMS-delivered password-reset URL with a Firebase Dynamic Link template:

```
https://ydqx9.app.goo.gl/?link=<reset_url>&app_apn=<android_pkg>&apple_bundle=<ios_bundle>&app_store_id=<ios_id>
```

This is hardcoded in `DeepLinkProvider.makeDeepLink()`. The intent is mobile **deep-linking**: when a user opens the SMS on a phone that has the Ship.Cars mobile app installed, FDL routes the click into the app; otherwise it falls back to the web reset URL with App Store / Play Store install hints.

**Google has officially deprecated FDL with a published shutdown date.** Once FDL stops resolving:

- Every SMS reset link **already in user inboxes / SMS history** will break.
- New reset links emitted via this plugin will break the moment the service is up after the FDL endpoint goes dark.
- This is an authentication-critical surface: a broken password-reset link blocks login recovery for any user who lost their password and tried to reset via SMS.

The deprecation timer is the forcing function. The decision is not *whether* to migrate; it is *to what*.

## Options

### Option A: Google's recommended path — App Links + Universal Links

- **Android**: App Links (autoVerify intent filter pointing at a domain you control, with a hosted `assetlinks.json`).
- **iOS**: Universal Links (Apple App Site Association file on the same domain).
- **Web fallback**: the same URL serves a fallback web page that handles the reset if the app isn't installed.

**Pros:** the platform-native, FDL-recommended successor. No third-party gateway. Once configured per-domain, individual plugin changes are minimal — emit a plain URL on a Ship.Cars domain and let App Links / Universal Links resolve it.

**Cons:** requires hosting `assetlinks.json` and `apple-app-site-association` on a stable Ship.Cars domain with TLS + correct headers. Requires mobile-app changes (intent filter + entitlement). One-time setup cost: medium; ongoing maintenance: low.

### Option B: In-house deep-link gateway

- A small Ship.Cars-owned service (Go or Quarkus, ~200 LoC) at e.g. `link.ship.cars/r/<short>` that records the click, decodes the original target, and 302s — with App Links / Universal Links wired on its domain.

**Pros:** centralizes deep-link logic and click telemetry; gives a single place to add A/B routing, app-vs-web detection, expiry, abuse detection.

**Cons:** another service to operate; the `hasher` repo already does something similar at a smaller scale.

### Option C: Third-party paid deep-link service (Branch, AppsFlyer, etc.)

- Replace `ydqx9.app.goo.gl` with a Branch / AppsFlyer URL.

**Pros:** managed product; rich analytics; less in-house code.

**Cons:** introduces a paid third-party on a critical-auth path; same long-term-supplier risk that hit FDL.

## Decision (proposed)

**Adopt Option A (App Links + Universal Links) on a Ship.Cars-owned domain.** Plain HTTPS URLs; no third-party gateway.

Sequence:

1. **Pick the domain.** Likely `reset.ship.cars/r/<token>` or a path under an existing domain.
2. **Host `assetlinks.json` and `apple-app-site-association`** on that domain (well-known paths, no redirects, correct Content-Type).
3. **Build a small reset-resolver** (could live in `keycloak-password-reset-link` or a new tiny service) that maps `/r/<token>` to the underlying Keycloak reset URL + handles the fallback page when the app isn't installed.
4. **Update `keycloak-phone-login-plugin.DeepLinkProvider`** to emit the new URL instead of `ydqx9.app.goo.gl`. Externalize the URL template via Keycloak config; do not hardcode again.
5. **Mobile app**: add the App Links intent filter (Android) + Universal Links entitlement (iOS).
6. **Cut over** with a feature flag on the plugin side; verify with a small percentage of new resets before flipping fleet-wide.
7. **Bridge existing FDL links**: while FDL is still alive, run a temporary redirector at `ydqx9.app.goo.gl/?link=...` → `reset.ship.cars/r/<token>` if any links remain in user inboxes. After FDL shuts down, links already in the wild that weren't clicked are lost — communicate this clearly to support.

## Consequences

- **Pro:** removes a SaaS dependency on the authentication path; mobile deep-linking owned in-house.
- **Pro:** unblocks all future deep-link work (other plugins, marketing links, etc.) by establishing the App Links / Universal Links setup once.
- **Con:** one-time mobile-app release coordinated with the Keycloak plugin release.
- **Con:** support burden during the FDL-shutdown window — links not clicked before shutdown are lost; support must communicate "request a new reset link" rather than "this link didn't work".

## Out of scope

- Whether to switch `keycloak-phone-login-plugin`'s URL shortener to an in-house shortener as well (the plugin currently calls a configurable external shortener with no timeout). Treat as a separate decision; the shortener problem is orthogonal to the FDL problem.

## References

- `~/projects/codebase-map/repos/keycloak-phone-login-plugin.md` — primary affected service.
- `~/projects/codebase-map/repos/keycloak.md` — bundled image.
- `~/projects/codebase-map/domains/identity.md`.
- Google Firebase Dynamic Links deprecation notice (public web; consult Google's documentation for the official shutdown date).
