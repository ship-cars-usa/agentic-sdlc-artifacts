---
repo: public-tracking-frontend
path: ~/projects/ship-cars-usa/public-tracking-frontend
stack: TypeScript 5.9 / React 18.3 / single-spa 6.0.3 + single-spa-react 6.0.2 (app-parcel) / Webpack 5.105 / MUI 6.4 + @mui/x-date-pickers 7 / @tanstack/react-query 5 / react-router 7 / axios 1.17 / pnpm 11 / Node 22+
domain: operations
shape: single-module (single-spa **app-parcel** only)
last-synced-commit: 805ab55d73ed60e9b557306e23872d721c7ce36d
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# public-tracking-frontend

## What it is
`@ship-cars/ship-cars-public-tracking` — the public-facing **load-tracking UI** that a recipient of a tracking link opens (no Keycloak login) to see the live status, carrier/driver info, load details, paperwork and status timeline of a delivery. Rendered as `@ship-cars/public-tracking-app`, the **default route** parcel of the `public-root-app-frontend` shell (`public.ship.cars` / `public-dev.ship.cars`).

**Correction vs. the previous shadow:** this repo is now a **single-spa app-parcel only** — it no longer ships its own single-spa root config. The root moved out to `public-root-app-frontend`, which mounts this parcel at its default route (see `public-root-app-frontend/src/microfrontend-layout.html`). The old "two builds in one repo (root + app)" description is stale; the README still references `start:root` / `start:app` / port 7100 but `package.json` has a single `start` script on **port 7110**.

Modernized to the LoadMate ("lm-") MFE generation: single-spa 6, react-query, react-router 7, MUI 6.4, pnpm, Node 22, ESLint 9 flat config. Data access is via the shared `@ship-cars-usa/lm-data-layer` package rather than an in-repo axios client. The commit history is on the **LITE** Jira project (LoadMate/Lite), and the UI is Montway-branded (`MONTWAY_AUTO_TRANSPORT` shipper constant in `src/constants/shipper.ts`).

## How it fits

- **Consumes API of:** `public-tracking-backend` (Spring Boot) — via `getLoadInfo(publicLinkKey, token)` imported from `@ship-cars-usa/lm-data-layer/public-tracking` (`src/components/PublicTracking/PublicTracking.tsx`). The base URL is resolved by `@ship-cars-usa/lm-global-config`, not hardcoded in-repo. No other backend is called directly.
- **Auth model:** no Keycloak. Access is gated by (a) the opaque `publicLinkKey` route param (`/loads/:publicLinkKey`) and (b) an **invisible Google reCAPTCHA v3** token minted client-side (`useRecaptcha`, `recaptchaSiteKey()` from lm-global-config); the react-query fetch is `enabled: !!token`, so no load data is requested until the captcha token exists. `public-tracking-backend` validates both.
- **3rd-party integrations:** Mixpanel analytics (`src/common-utils/analyticsUtils`), Rollbar error tracking (person = `publicLinkKey`), and the Salesforce **Agentforce "Sophie" embedded chatbot** (`src/hooks/useChatbot.ts`, prod + staging Montway orgs).
- **Publishes events to:** none.
- **Owns data store:** none.
- **Deployment surface:** standalone public site, mounted by `public-root-app-frontend`. **Not mounted into the authenticated Loadmate shell.**

## Build / test / run
```
# Registry auth (one-time): pnpm needs FontAwesome + GitHub Packages tokens in ~/.npmrc
pnpm config set "//npm.fontawesome.com/:_authToken" "$FONTAWESOME_TOKEN"
pnpm config set "//npm.pkg.github.com/:_authToken" "$GITHUB_TOKEN"
pnpm install
pnpm start            # webpack serve --port 7110 --env isLocal  -> http://localhost:7110/
pnpm build            # webpack --mode=production
pnpm test             # jest (jest.config.ts, jsdom)
pnpm typecheck        # tsc
pnpm lint / format
```
Note: README's `start:root` / `start:app` / `:7100` instructions are stale (single-root era). Use `pnpm start` on 7110.

## Key abstractions

- `src/shipcars-public-tracking-app.tsx` — single-spa app-parcel lifecycle (`bootstrap/mount/unmount`) via `single-spa-react`; also initializes Mixpanel per `deploymentInstance`.
- `src/root.component.tsx` — top-level React tree.
- `src/routes.ts` — `PublicTrackingRoutes` enum: `/loads/:publicLinkKey` (main) + `/404`.
- `src/components/PublicTracking/PublicTracking.tsx` — the main page: recaptcha token flow → `useQuery(getLoadInfo(...))` → renders sub-sections (`PublicTrackingCarrierAndDriverInfo`, `PublicTrackingLoadDetails`, `PublicTrackingLoadUpdates`, `PublicTrackingMenu`, `PublicTrackingPaperwork`, `PublicTrackingStatus`).
- `src/pages/Error404Page/` — the 404 page.
- `src/hooks/useRecaptcha.ts` — loads reCAPTCHA v3 script (via `useScript` from lm-utilities) and runs it to mint the fetch token.
- `src/hooks/useChatbot.ts` — Salesforce Agentforce "Sophie" embedded-messaging bootstrap.
- `src/common-utils/analyticsUtils.ts` — Mixpanel client wrapper.
- `Dockerfiles/` + root `Dockerfile` / `Dockerfile-test` — runtime + test images.
- `scripts/registry-auth.sh`, `eslint.config.mjs` (ESLint 9 flat), `sonar-project.properties`, `webpack.common.mjs` + `webpack.config.mjs`.

## Don't-do-here / gotchas

- **App-parcel only now — don't reintroduce a root here.** The route→parcel wiring lives in `public-root-app-frontend/src/microfrontend-layout.html`. Adding routing/root logic here duplicates the shell.
- **README is stale.** `start:root` / `start:app` / `:7100` / "Deploy - TODO" / "Import map Overrides - TODO" all predate the app-parcel + pnpm migration. Trust `package.json` (port 7110) over the README.
- **No load data without a reCAPTCHA token.** If the tracking page renders blank, first suspect the recaptcha script/token path (`useRecaptcha`, `recaptchaSiteKey()`), not the backend — the query is `enabled: !!token`.
- **`public-tracking-backend` HikariCP `max-size=5`** is a fleet pool-size outlier on a public surface — many concurrent tracking-link readers at peak can exhaust the pool. The frontend can't fix this; relevant when investigating "tracking page slow at peak."
- **Backend base URL + recaptcha site key come from `lm-global-config`**, not this repo. Env drift ("wrong environment's data") is usually a lm-global-config / `deploymentInstance` issue.
- **`single-spa-layout` 3.0.0 is listed as a dependency but the entry is app-parcel-only** — likely a leftover from the root era; verify before relying on it.
- **Montway-specific branding + Salesforce Sophie chatbot** are hardcoded (`useChatbot.ts`, `shipper.ts`). This is not a white-label generic tracker.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/public-tracking-backend.md` — the Spring Boot backend (HikariCP=5 outlier; reCAPTCHA on the auth path).
- `~/projects/codebase-map/repos/public-root-app-frontend.md` — the single-spa root shell that mounts this parcel (default route).
- `~/projects/codebase-map/repos/driveaway-public-tracking-frontend.md` — sibling public-facing tracking UI (Driveaway), also mounted by the same root.
- `~/projects/codebase-map/domains/operations.md`.
