---
repo: ml-lib-extraction
path: ~/projects/ship-cars-usa/ml-lib-extraction
stack: Python async / LiteLLM (router) / structured-output schema validation / token-usage + cost tracking
domain: analytics
shape: reusable Python library
last-synced-commit: 1f11abd52590045eba5000e192712ff02fa638dd
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# ml-lib-extraction

## What it is
**Reusable async Python extraction library** — `ExtractionResult`-returning LLM-extraction pipeline built on `LiteLLM`'s router pattern. The fleet's standardized "give me structured output from unstructured input" library, factored out so that downstream consumers (most prominently `ml-bot-order-v2`) don't reinvent the LLM-call + schema-validation + cost-tracking + repair loop.

`ExtractionResult` carries 4 fields per the README:
1. `output` — validated structured output (per a caller-supplied schema).
2. `raw` — raw model content when available.
3. `usage` — token usage (input/output/total).
4. `cost` — best-effort USD cost estimate (input/output/total).

The library is **provider-aware**: same caller API, different LLM provider underneath (OpenAI / Anthropic / Gemini / etc. via LiteLLM). Includes a **one-step repair** mechanism for when the model returns invalid structured output — re-prompt with the validation error, accept the corrected version. Configurable via `ai-instructions.toml`.

**Unusually well-documented repo** with `ARCHITECTURE.md` (system design), `SPEC.md` (contracts), `STATE.md` (current snapshot), `LESSONS.md` (operational learnings), `EXAMPLES.md`, plus a working `demo.py`. **Best-documented Python library in the fleet** at the time of this seed.

## How it fits

- **Consumed by:** `ml-bot-order-v2` (per repo cross-reference); likely the LiteLLM-extraction primitive for other ML services that need structured LLM output (`ml-document-parser`, `ml-bot-order` v1, potentially future ones).
- **Consumes:** LLM providers via LiteLLM (OpenAI, Anthropic, Gemini routed by config).
- **Publishes:** none.
- **Owns data store:** none.

## Build / test / run
```
pip install -e .
python demo.py       # walks through a typical extraction call
```

## Key abstractions

- `demo.py` — runnable example (start here when learning the API).
- `configs/` — extraction-pipeline configs (TOML-style; per-pipeline / per-domain).
- `ai-instructions.toml` — LLM-instruction templates (prompts, system messages, retry rules).
- `ARCHITECTURE.md` — system design (read before extending).
- `SPEC.md` — contracts (return shapes, error semantics).
- `STATE.md` — current implementation snapshot (read before grep-driven changes — it's authoritative).
- `LESSONS.md` — operational lessons (read before adding new providers or changing the repair loop).
- `EXAMPLES.md` — copy-pasteable examples.
- `CHANGELOG.md` — versioned changes.

## Don't-do-here / gotchas

- **Pipeline-level LLM call mode override** (per the latest commit `1f11abd`) — the call mode can be overridden per pipeline. Read the commit + STATE.md before introducing new modes.
- **`ExtractionResult.cost` is best-effort.** LiteLLM's pricing tables are not always current; treat the cost field as an estimate, not an invoice.
- **One-step repair only.** If the model can't produce valid output on attempt 2, the call fails. Caller must decide whether to retry at a higher layer (different prompt, different model).
- **TOML config drift.** Multiple consumers may have different `ai-instructions.toml`. A change here that affects defaults can shift behavior in `ml-bot-order-v2` without an obvious code-diff trail.
- **No public deployment.** Library only; runtime impact is via consumers.
- **Provider-aware packaging.** Adding a new provider means updating LiteLLM router config + verifying schema-validation behavior; not all providers return structured output the same way.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/ml-bot-order-v2.md` — canonical consumer.
- `~/projects/codebase-map/repos/ml-document-parser.md` — potential consumer.
- `~/projects/codebase-map/repos/ml-bot-order.md` — v1 may still use this or its own LLM client.
- `~/projects/codebase-map/domains/analytics.md`.
