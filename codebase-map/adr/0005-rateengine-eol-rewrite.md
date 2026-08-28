# ADR 0005 — `rateengine` EOL Posture

**Status:** Proposed
**Date:** 2026-05-12
**Forcing function:** Django 2.1.7 + DRF 3.8.2 + Python 3.6 — **all EOL since 2020-2021**. Sat on `lead-parser` (Spring Boot 2.1.4 RELEASE, EOL since 2019) as the fleet's two oldest backends.
**Context author:** codebase-map maintenance

## Context

`rateengine` is **the actual pricing engine** for non-contracted lanes in the Ship.Cars fleet. Per the pricing-stack boundary clarification in `domains/pricing-billing.md`:

- `quote-manager-backend` owns quote lifecycle (state facade).
- `contract-pricing-backend` owns per-customer overrides.
- **`rateengine` computes the base rate**, calling `ml-service-dispatcher` underneath for ML model predictions and applying business-rule adjustments (multi-vehicle surcharge, special routing, enclosed premium).
- `ml-service-dispatcher` is the synchronous gateway to the actual ML model services.

`rateengine` runs **Django 2.1.7 + DRF 3.8.2 + Python 3.6 + Gunicorn**. All three of Django 2.1, DRF 3.8, and Python 3.6 are long past EOL — they have not received security backports for ≥5 years. Adjacent stack also has known issues:

- `requests.Session()` with no timeout on outbound central-dispatch calls (worst-case hangs the worker forever).
- ML models loaded in-memory at startup (slow boot, blue/green required for updates).
- Elasticsearch on the request path (potentially load-bearing for quote audit).
- Token-only auth (no OAuth, no mTLS).
- ~54 Aerich-equivalent Django migrations in the repo (schema drift exposure).

This is the **second-biggest fleet lifecycle/security flag**, behind `lead-parser` (which is similarly EOL and has explicit replace-not-patch recommendation already documented). The difference: `lead-parser` parses inbound emails (replaceable), `rateengine` is the **canonical pricing engine** (request-path-critical; rewriting requires more care).

## Options

### Option A: Full rewrite to Python 3.12 + FastAPI

- New repo `rateengine-v2` (or in-place re-stack).
- Port `Facade`, `MLFacade`, `Calculator`, `QuoteViewSet` (and siblings: `StarRatingViewSet`, `UpsellViewSet`, `VehicleViewSet`, `MarketViewSet`) to FastAPI + Pydantic.
- Replace Django ORM with SQLAlchemy 2.x async (or Tortoise; the rest of the Python fleet uses Tortoise — pick to match).
- Keep ML model loading semantics; introduce model-version stamps.
- Replace `requests` with `httpx` async + explicit timeouts.
- Use the `ml-bot-order-v2` repo's `ARCHITECTURE.md` / conventions as the template (best-documented service in the fleet).

**Pros:** ergonomically aligned with the rest of the Python fleet; removes the EOL framework risk; opens the door to async I/O for the multiple downstream model calls; future feature-velocity is higher.

**Cons:** highest effort. Quote-engine is request-path-critical; a rewrite needs parallel-run + comparison-testing before cutover. **6-9 person-months for a small team.**

### Option B: Thin Python-FastAPI shell wrapping the Django logic

- Stand up a FastAPI service that proxies into a frozen Django-2.1.7 process (in-process via WSGI bridge or subprocess) for the actual compute.
- Patch surface security issues (`requests.Session` timeout, token rotation, etc.) at the FastAPI layer.

**Pros:** removes the public-internet exposure of Django; less effort than full rewrite.

**Cons:** doubles the operational footprint (two stacks in one pod); doesn't actually remove the EOL Django, just hides it. Sec-fix for any future Django 2.1 vulnerability is still impossible.

### Option C: Status quo with hardened ops

- Keep Django 2.1.7. Patch the surface issues (timeouts, token rotation, audit).
- Run behind a hardened WAF; accept the EOL exposure as a documented risk.

**Pros:** zero engineering investment.

**Cons:** doesn't address the underlying CVE exposure; auditor-flagged; can't compile against modern dependency versions for new features.

## Decision (proposed)

**Adopt Option A** — full rewrite to Python 3.12 + FastAPI on the fleet's modern Python conventions (matching `ml-bot-order-v2`).

Sequence:

1. **Scope phase** (~2 weeks): build a behavioral test harness that captures every public REST call into the current `rateengine` over a representative production traffic window. This becomes the parity acceptance gate.
2. **Build phase** (~3-4 months): new repo or in-place re-stack. Port the `Facade` → `MLFacade` → `Calculator` chain. Use the `ml-bot-order-v2` conventions (see the user-defined skills: `utility-conventions`, `database-conventions`, `schema-conventions`, `service-conventions`, `testing-conventions`, `environment-conventions`).
3. **Shadow phase** (~1 month): traffic mirror — every production request hits both old and new; compare outputs; alert on divergence > tolerance.
4. **Cutover** (~2 weeks): canary % → 100%. Old service kept warm for rollback for one quarter.
5. **Decommission**: after the warm-rollback window closes, retire the Django service.

**Hard constraints:**

- No model-output regressions tolerated beyond a tightly-bounded numeric tolerance (definition needed from data-science team before cutover).
- Pricing-correctness audit log must be preserved (Elasticsearch index migration plan needed).
- Existing tokens-and-endpoints remain valid through cutover; the new service is API-compatible.

## Consequences

- **Pro:** retires the highest pricing-stack lifecycle risk in the fleet. Aligns the engine with the rest of the Python fleet's conventions.
- **Pro:** opens async I/O across `ml-service-dispatcher` (today's `requests` calls are sequential; FastAPI + `httpx.AsyncClient` can parallelize the 4-5 model calls).
- **Con:** 6-9 person-months. Pricing is correctness-critical; the bar for parallel-run + comparison is high.
- **Con:** Data-science team needs to validate the ported model behavior; coordination cost.

## Out of scope

- Whether `ml-service-dispatcher` and `rateengine` should be merged. Worth its own ADR after this rewrite lands; the boundary clarification in `domains/pricing-billing.md` (added 2026-05-12) is the input for that future decision.

## References

- `~/projects/codebase-map/repos/rateengine.md` — current shadow.
- `~/projects/codebase-map/repos/ml-service-dispatcher.md` — downstream model gateway.
- `~/projects/codebase-map/repos/quote-manager-backend.md` — upstream state facade.
- `~/projects/codebase-map/repos/contract-pricing-backend.md` — per-customer overlay.
- `~/projects/codebase-map/repos/ml-bot-order-v2.md` — the in-fleet template for the new stack.
- `~/projects/codebase-map/domains/pricing-billing.md` — pricing-stack boundary clarification.
