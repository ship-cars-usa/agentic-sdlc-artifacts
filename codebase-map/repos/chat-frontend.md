---
repo: chat-frontend
path: ~/projects/ship-cars-usa/chat-frontend
stack: TypeScript 4.9.5 / React 18.2.0 / single-spa 6.0.3 + single-spa-react 6.0.2 / Webpack 5.104.1 / MUI 6.1.10 / axios 1.15.0 / dompurify 3.4 / jwt-decode 3.1 / pnpm 11 (Node >=22)
domain: communication
shape: single-module
last-synced-commit: 5b4b876063e9c28a9b19f1c0b2cbec0563880e3f
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# chat-frontend

## What it is
`@shipcars/chat` — a **single-spa micro-frontend** that owns the in-app chat / discussion UI inside the Loadmate posting shell. Built with `webpack-config-single-spa-react-ts` (not Vite), bundled as an app-parcel and mounted by the parent shell into the posting route. pnpm-managed, Node >=22.

Small UI (~20 TS/TSX files): a `Chat` container with `Message` cells and a Draft.js-style `RichTextEditor`. Pairs with `chat-backend` (the Spring Boot chat service). Latest commit LITE-7808 (2026-06-29) is MUI-v6 cleanup (removing deprecated MUI props).

## How it fits
- **Consumes API of:** `chat-backend` via REST. `src/services/message.service.ts` builds `${CHAT_API}/v1/discussions...` (get/patch/post — discussions, send message, is-typing). `CHAT_API` comes from `@ship-cars-usa/lm-global-config` `environments.posting()` — every `src/environments/*.ts` re-exports it, so no URLs live in the repo (`src/environments/utils.ts` only declares the `CHAT_API` shape).
- **Publishes events to:** none directly.
- **Subscribes to:** DOM `CustomEvent`s, not a WebSocket. `src/services/socket.service.ts` does `document.addEventListener("new_socket_events.<EventName>", …)`; the only event today is `ChatUpdated` (`= "chatUpdateReceived"`). **Another bundle in the shell owns the actual WebSocket and re-dispatches events on `document`** — this repo neither opens the socket nor documents the publisher.
- **Owns data store:** none (browser-only, ephemeral React state).

## Build / test / run
```
pnpm install                  # Node >=22, pnpm >=11
pnpm start                    # webpack serve --port 7080
pnpm start:https              # HTTPS dev server (webpack.https.js)
pnpm start:standalone         # standalone (no parent shell)
pnpm build:webpack            # webpack --mode=production
pnpm lint / pnpm typecheck    # eslint / tsc
pnpm coverage                 # jest (unit only; no e2e)
```
Local-in-deployed-env workflow (`README.md`): serve this bundle and override the import-map entry in the QA shell to point at `https://localhost:7080`.

## Key abstractions
- `Entry` — `src/shipcars-chat.tsx` — single-spa lifecycle (`singleSpaReact`).
- `Root` — `src/root.component.tsx` — top-level React tree mounted by single-spa.
- `Chat` — `src/Chat/Chat.tsx` + `src/Chat/useSocket.tsx` — chat container + the DOM-CustomEvent socket hook.
- `HttpService` — `src/services/http.service.ts` — `axios.create()` with a request interceptor injecting `Bearer ${localStorage.getItem("token")}`; `setInterceptAxiosResponse(callback)` lets the shell wire a 401 "force re-login" handler.
- `MessageService` — `src/services/message.service.ts` — REST for discussions/messages against `CHAT_API`.
- `SocketService` — `src/services/socket.service.ts` — `document` CustomEvent bus under the `new_socket_events.*` namespace.
- `src/common/RichTextEditor/` — inline-style + color controls; output sanitized with `dompurify`.
- `jwt-decode` is a dependency (token inspection).

## Don't-do-here / gotchas
- **Token in `localStorage`** — `http.service.ts` reads it synchronously on every request; XSS in the shell exfiltrates it.
- **No request `timeout`** — `axios.create()` has no defaults; a hung `chat-backend` holds the request until the browser aborts. Add `timeout` if needed.
- **Shared deps from the shell.** `package.json` has no runtime `dependencies` block override for React beyond declaring it; React/MUI/single-spa are provided by the shell's import-map. Version drift (esp. React 18.2 here vs the shell) can produce mismatched-hooks errors at mount that CI won't catch. `start:standalone` needs the shared deps available.
- **MUI v6** (6.1.10) — if the shell still serves MUI v5, components render against the wrong MUI runtime at mount. Verify the import-map.
- **DOM-event socket bus.** If `ChatUpdated` events stop arriving, the bug is almost certainly the shell's WebSocket bridge, not this repo — this bundle only listens.
- **`lm-global-config` is pinned to `^0.3.2`** here — older than the `user-frontend` / `contract-pricing-frontend` cohort's `0.6.7`. Confirm `environments.posting()` still exposes `CHAT_API` after any shared-config bump.
- **No e2e tests** — only `pnpm coverage` (Jest unit). Lifecycle coverage is implicit via shell smoke tests.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/chat-backend.md` — the Spring Boot REST backend.
- `~/projects/codebase-map/repos/socket-server.md` — the WebSocket layer whose events are bridged to `document` CustomEvents.
- `~/projects/codebase-map/domains/communication.md`.
