---
repo: synclink-chrome-extension
path: ~/projects/ship-cars-usa/synclink-chrome-extension
stack: Browser extension (Chrome Manifest V3, ES module service worker)
domain: operations
shape: single-module (flat JS files)
last-synced-commit: d27fcf08ce4dded901e0a996cce8d6d1da22eb24
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# synclink-chrome-extension

## What it is
The browser-side companion to `synclink-backend`. A Chrome MV3 extension that **runs on `shipper.superdispatch.com` pages**, intercepts that site's order API responses via injected fetch hook, hashes each order's relevant fields, and batch-syncs changed orders to Ship.Cars's `/api/synclink/load-state` endpoint.

Together with `synclink-backend`, this extension is the bridge that imports SuperDispatch carrier-portal order state into the Ship.Cars `posting-backend` flow without requiring SuperDispatch API credentials — the carrier user is already logged into SuperDispatch, the extension piggy-backs on their session via fetch interception, and re-emits the data to Ship.Cars.

Architecture (per README):
```
SuperDispatch API call (single order or list)
  → Injected Script (intercepts window.fetch, adds timestamp)
    → Content Script (forwards via postMessage)
      → Background Service Worker
          ├─ Hashes order (SHA-256 of ~50 field paths)
          ├─ Caches hash + timestamp in chrome.storage.local
          └─ Batches up to 20 changed orders → POSTs to Ship.Cars
              → synclink-backend /api/synclink/load-state
```

## How it fits

- **Runs on:** `shipper.superdispatch.com/*` (declared in `manifest.json` `content_scripts.matches` and `host_permissions`). The extension does **not** run on Ship.Cars pages — it only consumes Ship.Cars APIs as the sync target.
- **Consumes API of:**
  - `synclink-backend` (via Ship.Cars main domain). Per `background.js`'s `ENV_CONFIG`: `https://ship.cars/api/synclink/load-state` (prod), `https://staging.ship.cars/api/synclink//load-state` (staging — **note double-slash typo**), `https://qa.ship.cars/api/synclink//load-state` (qa — **same typo**), `https://dev.ship.cars/api/synclink/load-state` (dev — correct, no typo), `http://localhost:3000/api/synclink/load-state` (local).
  - Keycloak (`auth.ship.cars/auth`) for OAuth via `chrome.identity` API. Client ID: `chrome-extension`.
- **Owns data store:** `chrome.storage.local` — caches per-order SHA-256 hash + timestamp + pending-sync queue.
- **Publishes events to:** none directly; the sync POST is REST.

## Build / test / run
```
# Dev: load unpacked
1. chrome://extensions/ → enable Developer Mode → "Load unpacked" → select repo folder
2. Click the extension icon; popup.html lets the user log in via Keycloak and pick environment (local/dev/qa/staging/prod)
3. Navigate to https://shipper.superdispatch.com — the extension auto-injects and starts intercepting

# Production: pack into .zip and upload to Chrome Web Store
```

No build step — the extension is shipped as raw JS (manifest V3 module-style service worker).

## Key abstractions

- **`manifest.json`** — MV3 manifest. Declares `service_worker: "background.js"` with `type: "module"`, content scripts running on `shipper.superdispatch.com` at `document_start`, web-accessible resources (`injected-script.js`, `generateHash.js`), and host permissions for the 4 Ship.Cars envs + SuperDispatch + Keycloak realms.
- **`injected-script.js`** — runs in the SuperDispatch page context (highest privilege re. the page's fetch API). Overrides `window.fetch` to capture order API responses + adds a client timestamp.
- **`content-script.js`** — runs in the isolated content-script world. Injects `injected-script.js` into the page, listens for `postMessage`s from it, forwards them to the service worker via `chrome.runtime.sendMessage`. Also manages the **red "Please log in" banner** that appears if the user has open SuperDispatch but isn't authenticated to Ship.Cars.
- **`background.js`** (service worker) — the brain. Handles: Keycloak OAuth (token refresh via `alarms` API), `chrome.storage.local` cache of (order_guid → {hash, timestamp}), batch-of-20 sync POSTs, environment selection.
- **`generateHash.js`** — SHA-256 hash of a fixed list of **`HASHABLE_FIELD_PATHS`** (~50 entries: order core fields, vehicle array fields, customer fields, pickup/delivery venue fields). **MUST match** `HashableOrderFields.HASHABLE_FIELD_PATHS` in the `synclink-backend` Java code. Comment in the file makes the contract explicit.
- **`popup.html` + `popup.js`** — the extension popup. Shows logged-in / logged-out state, lets the user log in / log out / pick environment.

## Don't-do-here / gotchas

- **The hash-field-paths list is a hard contract with `synclink-backend`.** Every field added or removed here must be mirrored in `cars.ship.synclink.HashableOrderFields.HASHABLE_FIELD_PATHS` in the Java code (and vice versa). A divergence causes either: (a) silent missed syncs (extension sees no hash change, doesn't sync, but backend would have — when a backend-only field changes), or (b) re-sync storms (extension thinks hash changed every time, syncs every order on every load — when the lists go out of order). Treat both sides as a single versioned contract.
- **Double-slash typo in prod/staging/qa sync URLs.** `https://ship.cars/api/synclink//load-state` (and same for staging/qa) — note the `//`. The dev URL is correct (`/api/synclink/load-state`). Whether routing tolerates this depends on the gateway; worth confirming on the next deploy that this isn't producing 404s in prod. (If it works, it works because of permissive route matching — fragile.)
- **Manifest V3 service worker termination.** Background service workers can be killed by Chrome when idle and re-spawned on event. State held in JS module-level variables is lost; all persistent state must round-trip through `chrome.storage.local`. The current code mostly does this, but any new feature must respect it — don't add an in-memory queue without persistence.
- **Keycloak `clientId: 'chrome-extension'` is shared across all installations.** The redirect URI uses `chrome.identity.getRedirectURL()` which produces a per-extension-ID URL; OK. But the Keycloak client itself is one shared public client — token-issuance rate-limiting is per-client, not per-user. A misbehaving user can affect token issuance for everyone if they refresh aggressively.
- **`SCRIPT` injection model.** The extension creates a `<script>` element in the page DOM pointing at `injected-script.js`. This is the canonical MV3 pattern, but means the page can detect (and theoretically defeat) the extension by removing the script tag or overriding `window.fetch` after injection. If SuperDispatch ever decides this is unwelcome scraping, they have technical means to block it.
- **Banner is positioned `position: fixed; top: 10px; right: 10px; zIndex: 999999`** — could collide visually with SuperDispatch's own UI elements during incident-flagged sessions. Worth a UX check.
- **`web_accessible_resources` exposes `injected-script.js` + `generateHash.js`** to `https://shipper.superdispatch.com/*`. Anyone on that domain can fetch them and read the hash field-paths list. Not a real secret (the SuperDispatch field list is well-known) but the explicit contract is now public to anyone running JS on SuperDispatch.
- **No exponential backoff on sync failures.** The current code (per README) syncs in batches of 20 with no obvious retry strategy on 5xx. A `synclink-backend` outage means each batch retries on the next intercept rather than queueing.
- **`https://www.engine6.io` and `http://www.engine6.io`** appear in some host_permissions — looks like a former integration partner. Worth confirming whether still active.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/synclink-backend.md` — the Quarkus backend; canonical source of `HashableOrderFields.HASHABLE_FIELD_PATHS` that this extension must match.
- `~/projects/codebase-map/repos/posting-backend.md` — downstream consumer of synced order state via `synclink-backend`'s outbox.
- `~/projects/codebase-map/domains/operations.md` (the extension is currently in `operations`; consider re-domaining to `integrations` to mirror the 2026-05-11 re-domain of `synclink-backend`).
