---
repo: asg-checkout-spa
path: ~/projects/ship-cars-usa/asg-checkout-spa
stack: React 15.6 / Redux 3.6 + react-redux 5.0 / react-router 3 + react-router-redux 4 / redux-form 7 / axios 0.16 / node-sass 4 / Webpack 2 / Express server (Node)
domain: operations
shape: single-module (custom Webpack build + Express server; not single-spa)
last-synced-commit: a0ffbccb9076a95aa15b2b8aa013e372ce3a5946
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# asg-checkout-spa

## What it is
The **ASG / Montway Checkout SPA** (`asg-checkout-spa` v3.0.0) — a standalone consumer-facing checkout flow for the Montway auto-transport order form. The surface (`react-credit-card-input`, `react-google-recaptcha`, `react-input-mask`, `redux-form`, `google-map-react`) is the multi-step form a customer fills out to book a car-shipping order online. It ships its own Express server (`server/` + `express-http-proxy`/`express-request-proxy`) and `nginx.conf`, so it deploys as a containerized standalone app — **not** mounted into Loadmate and **not** single-spa.

**The entire stack is 8+ years stale** and unchanged since the last sync:

- **React 15.6.1** (2017) — three majors behind current React 18.
- **Redux 3.6 / react-redux 5.0 / react-router 3 / react-router-redux 4 / redux-form 7** — the full 2017 Redux/router/form toolchain.
- **axios 0.16.2** — older than the 0.21.x CVE-flagged versions elsewhere in the fleet.
- **node-sass 4.14** (deprecated libsass), **Webpack 2** with a bespoke `build/scripts/compile.js` pipeline.
- 2017-era UI deps: `react-id-swiper`, `react-responsive-modal`, `react-tooltip`, `react-select` 1.0-rc, `react-datepicker` 0.49.

Still on the active deploy path — HEAD is a `Merge branch 'production' into master` (2026-07-10), and recent history shows minor pricing tweaks — but no modernization. This is **frozen-but-deployed legacy** for an external Montway-branded product, similar in posture to `socket-server-old`.

## How it fits

- **Consumes API of:** Montway's order/quote API surface (assumed the same `gateway.montway.com/`-style endpoint referenced in `home-delivery-backend`), proxied through the app's own Express server. May also hit a Ship.Cars quote service if the Montway flow was migrated. Exact upstream not verifiable at this depth.
- **Publishes events to:** none.
- **Owns data store:** none (browser-only; Redux + redux-form state).
- **Deployment:** standalone container — Express front controller (`server/`) serving the built bundle + `nginx.conf` reverse proxy. Not part of Loadmate.

## Build / test / run
```
npm install                        # or yarn (README references legacy yarn 0.23)
npm start                          # NODE_ENV=development nodemon build/scripts/start.js
npm run build                      # NODE_ENV=production node build/scripts/compile.js
npm run start-dist                 # NODE_ENV=production node build/scripts/start.js (serves built output)
npm run clean                      # rimraf dist
npm run lint                       # eslint .
```

## Key abstractions

- `src/` — React 15 app source (Redux store, redux-form checkout steps, route tree via react-router 3).
- `server/` — Express server (static bundle + submit/proxy routes via `express-http-proxy` / `express-request-proxy`).
- `build/scripts/compile.js`, `build/scripts/start.js` — custom Webpack 2 build + dev/prod launchers (nodemon in dev).
- `nginx.conf` — production reverse-proxy config.
- `order.json` — sample order shape used during dev.
- `public/`, `config/` — static assets and config.

## Don't-do-here / gotchas

- **EOL across the entire stack** (React 15, Redux 3, react-router 3, Webpack 2, node-sass 4, axios 0.16). Bumping any one major without a coordinated migration breaks the bespoke `compile.js` chain.
- **Branded as Montway, not Ship.Cars** — white-labeled checkout; treat the URL surface + wire format as a partner-facing contract.
- **PCI-adjacent inputs** — `react-credit-card-input` 1.1 + `react-input-mask` 1.0 handle card/phone formatting. Confirm the actual submit target (likely Montway's payment provider, not Ship.Cars) before treating any change as low-risk.
- **reCAPTCHA** — `react-google-recaptcha` needs the correct site key per env on deploy.
- **No test tooling of substance** (only `react-test-renderer`/`react-addons-test-utils` 15.x present; no test script) — treat UI changes as effectively untested.
- **Not single-spa** — owns its own root, server, and deploy. Don't apply Loadmate-MFE conventions.

## Status / recommendation
**Archive-candidate or deliberately frozen** depending on Montway's continued use of the standalone checkout. Still receiving production merges, so confirm helm/deploy status before proposing retirement; if live, it's a P1 lifecycle item alongside other EOL repos (`lead-parser`, `rateengine`).

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/home-delivery-backend.md` — the other Montway-facing service; same per-dealer-token contract pattern.
- `~/projects/codebase-map/relations/infrastructure-triage.md` — flagged for re-evaluation.
- `~/projects/codebase-map/domains/operations.md`.
