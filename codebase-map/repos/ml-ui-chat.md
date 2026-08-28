---
repo: ml-ui-chat
path: ~/projects/ship-cars-usa/ml-ui-chat
stack: Python 3.9 / Streamlit 1.27.0 / streamlit-chat 0.1.1
domain: communication
shape: single-module
last-synced-commit: 774806162400f3aa2a26de632e655ec821e8866a
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# ml-ui-chat

## What it is
"Sofia" — the customer-facing chat UI for the `ml-service-chat` `/customer/...` endpoints. Single-file Streamlit app (`code/app.py`, ~253 lines) served at base path `/chat/`. Originally launched 2023-10-17 (per README) as the pilot carrier-chat frontend; presently the customer-side companion to the carrier chat exposed by Loadmate.

User flow:
1. Customer arrives via URL with `?token=…` query parameter.
2. App validates token shape (`startswith("1337")` and parses as UUID — purely structural, not cryptographic).
3. Customer enters a `load_id`; `get_session_id` POSTs to `ml-service-chat /customer/chat/conversation/init` to create a session.
4. Q&A loop posts each message to `/customer/chat/conversation/question`, displays the bot reply via `streamlit-chat`.
5. Thumbs-up / thumbs-down ratings hit `/customer/chat/conversation/question/rate`.

## How it fits
- **Consumes API of:** `ml-service-chat` (`ML_SERVICE_CHAT_URL` env var, suffixed with `/customer`). Three endpoints: `conversation/init`, `conversation/question`, `conversation/question/rate`. **No timeouts on any `requests.post()` call** — a hung `ml-service-chat` stalls the UI thread indefinitely.
- **Publishes events to:** none.
- **Owns data store:** none — pure UI; all state is `st.session_state` (in-memory per Streamlit session).
- **Auth model:** opaque token in URL query string. Token contents and validity are validated server-side by `ml-service-chat` via the `x-auth-token` header forwarded by this UI.

## Build / test / run
```
pip install -r builder/files/requirements.txt
cd code
ML_SERVICE_CHAT_URL=http://localhost:8087 streamlit run app.py
# In prod: served via the Dockerfile ENTRYPOINT:
# streamlit run app.py --server.port=80 --server.baseUrlPath=/chat/ \
#   --theme.base=dark --client.toolbarMode=minimal --client.showErrorDetails=false
```

## Key abstractions
- `app.py:get_session_id(load_id, token)` — opens a chat conversation. Returns session_id on 201; surfaces a `st.error` on 429 (rate-limited) or other (treated as invalid token/load).
- `app.py:ask_question(prompt, load_id, session_id, token)` — sends a question, appends both user and assistant turns to `st.session_state["messages"]`.
- `app.py:rate(value, session_id, token)` — fire-and-forget thumbs vote.
- `app.py:sanity_check(token)` — UUID-shape + `1337` prefix check. **Not security** — purely a malformed-input filter.
- `clear()` — resets session state except `load_id`, `initial_load_id`, `session_id`.

## Don't-do-here / gotchas
- **`requests.post(...)` calls have no `timeout=...` argument.** A slow or hung `ml-service-chat` will stall the Streamlit worker thread; in heavy traffic this can exhaust the worker pool. Minimum-viable fix: `timeout=(5, 30)` on every call.
- **Token in URL query parameter** (`?token=…`) — lands in proxy / load-balancer / Streamlit access logs. Treat as PII; either rotate often, scrub from logs, or move to a POST-based session handoff.
- **`st.experimental_get_query_params()` is deprecated** (removed in Streamlit ≥ 1.30). This service is pinned to `streamlit==1.27.0`, so it works today but **blocks any Streamlit version bump** without a code change to use `st.query_params`.
- **Streamlit 1.27.0 (Sep 2023) is 1+ year stale** — current is 1.40+. CVE exposure to be audited. Bumping requires the `experimental_get_query_params` migration plus a `streamlit-chat` review (0.1.1 is pre-1.0).
- **Hardcoded English copy + a single `Sofia` brand** — internationalization isn't supported. If the product needs Spanish carriers / customers, this is a rewrite scope, not a config.
- **`@NOTE: This format is not compatible with the carrier_chat`** comment in `ask_question` — the question payload shape for the customer side differs from the carrier side. Don't try to share a Pydantic model between the two; respect the divergence.
- **`st.markdown(..., unsafe_allow_html=True)`** is used for layout — XSS risk if any user input flows through it. Today the only `unsafe` markdown is hardcoded copy, but adding any user-content path here would be unsafe.
- **No retry on network errors** — a transient `ml-service-chat` failure shows a generic `GENERAL_ERROR_MESSAGE` and gives up.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/ml-service-chat.md` — the API this UI fronts.
- `~/projects/codebase-map/domains/communication.md`.
- `~/projects/quarkus-rest-client-timeout-anti-pattern.md` — Quarkus-focused but the same anti-pattern (call without timeout) applies here at the Python layer.
