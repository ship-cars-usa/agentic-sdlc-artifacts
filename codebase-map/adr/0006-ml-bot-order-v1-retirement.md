# ADR 0006 — Retire `ml-bot-order` (v1)

**Status:** Proposed
**Date:** 2026-05-12
**Forcing function:** v2 (`ml-bot-order-v2`) is the active-development line and the canonical producer of the `ml-bot-order` Pub/Sub topic that `posting-backend` consumes. v1 currently runs in parallel but does not publish a topic — it writes directly to `posting-backend` via REST.
**Context author:** codebase-map maintenance

## Context

Two services coexist:

| | `ml-bot-order` (v1) | `ml-bot-order-v2` |
|---|---|---|
| Stack | Python 3.11 / FastAPI / Tortoise-ORM / **legacy `google-genai` SDK** | Python 3.12 / FastAPI / Tortoise-ORM 0.25+ / **LiteLLM (Gemini 2.5-flash primary, 2.0-flash fallback)** |
| Source-of-LLM | Gemini directly via legacy SDK | LiteLLM Router (multi-provider, fallback chain) |
| Input | SMS via Pub/Sub | SMS + email + attachments via Pub/Sub |
| Output | Direct REST POST to `posting-backend` via `impersonator` | Publishes `oib-outbound-lm` + `oib-outbound-sf` Pub/Sub topics |
| Idempotency | None — Pub/Sub auto-ack after handler | `UNIQUE(request_id, codename, status) ON CONFLICT DO NOTHING` |
| Audit | `IncomingEventLog` 20-state lifecycle | `ingest_requests_log` + `pubsub_events_log` |
| In-repo design docs | Minimal | **Fleet's best** (`ARCHITECTURE.md`, `AGENTS.md`, `LESSONS.md`, `STATE.md`) |
| Convention conformance | None | Conforms to the user's `*-conventions` skill set |

**The two services are NOT in a load-balanced pair.** They serve different feeds:
- v1's `sms-events` subscription handles legacy SMS-only flow.
- v2's `oib-inbound-lm` / `oib-inbound-sf` handle the modernized flow (SMS + email + docs, multi-destination).

What the v2 shadow already says: "Plan a v1 retirement once v2 reaches parity."

## What "parity" means

For v1 to be safely retired, **v2 must cover all the input paths v1 currently serves**:

1. v2 already accepts the same SMS message shapes that v1 consumes (verify by diffing `SMSEventParser` against v2's inbound subscribers).
2. v2's `oib-outbound-lm` topic must be wired to `posting-backend` in the same way v1's direct-REST path is — i.e., `posting-backend` consumes the topic and creates the same drafts. **This is already true** per `posting-backend`'s shadow (it subscribes to `ml-bot-order`, supplied by v2 per ADR-0003 contract).
3. v2 must handle whatever business-logic differences exist between v1's direct-REST `posting-backend` calls and what v2 emits via topic.

The third item is the gating risk. Without a behavioral-parity test, retiring v1 risks dropping drafts.

## Decision (proposed)

**Retire v1 in three stages over one quarter:**

### Stage 1 — Behavioral-parity audit (2-3 weeks)

1. Sample one week's worth of v1's `IncomingEventLog` records — every SMS that landed at v1 and resulted in a `CREATED_DRAFT_POSTING` or `FAILED_*`.
2. Re-feed the same SMS payloads to v2 in a non-production environment. Compare drafts emitted on `oib-outbound-lm` against drafts created by v1.
3. Triage any divergence:
   - Schema differences → port the missing fields to v2 before retirement.
   - Business-logic differences → decide intent and port the missing logic.
   - Tolerable noise → document.

### Stage 2 — Traffic mirror (3-4 weeks)

1. Add a `traffic-mirror` consumer to the v1 `sms-events` subscription that forwards each message to v2's `oib-inbound-lm` topic.
2. Run both services live. Compare drafts at `posting-backend` (which sees both: v1 via REST, v2 via topic). Alert on divergence.
3. Tune until divergence is within tolerance for ~2 weeks.

### Stage 3 — Cutover (1-2 weeks)

1. Disable v1's `SMSEventParser` (stop consuming the `sms-events` subscription).
2. Re-point the `sms-events` upstream to publish to v2's inbound topic instead (or, simpler: keep v1's Pub/Sub plumbing but have the parser only forward, not parse).
3. Keep v1's PG snapshot for one quarter as evidence; retire the service after the quarter passes without rollback.

## Consequences

- **Pro:** removes a parallel service consuming Gemini quota separately. Removes the legacy `google-genai` SDK exposure (Google's deprecation timer applies; v2 is on the current Google AI SDK via LiteLLM).
- **Pro:** removes a no-idempotency Pub/Sub consumer from production.
- **Pro:** simplifies the integrations-domain catalog: one service per concern.
- **Con:** Stage-1 audit work + the traffic-mirror infra is real engineering. A team needs to do it.
- **Risk:** any v1-only path that doesn't surface in the one-week sample becomes a silent regression after cutover. The 2-week mirror period is the mitigation.

## Migration path if reversed

If retirement reveals a gap that takes more than one quarter to fix in v2, the safe path is to revive v1's `SMSEventParser` (the service should remain deployed, just not consuming) and ship v2's missing logic before re-attempting.

## Out of scope

- Retiring v2's `oib-outbound-sf` (Salesforce-flavored) is a separate decision based on whether the SF integrator path is still in use.
- Whether `posting-backend` should be the one to consume `ml-bot-order` directly, or whether an intermediate `oib-router` service should sit between v2's outbound topic and `posting-backend`. Treat as a future optimization, not part of this ADR.

## References

- `~/projects/codebase-map/repos/ml-bot-order.md` — v1 shadow.
- `~/projects/codebase-map/repos/ml-bot-order-v2.md` — v2 shadow; already documents the retirement intent.
- `~/projects/codebase-map/repos/posting-backend.md` — common downstream.
- `~/projects/codebase-map/repos/impersonator.md` — auth flow used by v1's direct REST.
- `~/projects/codebase-map/domains/integrations.md`.
