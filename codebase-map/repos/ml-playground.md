---
repo: ml-playground
path: ~/projects/ship-cars-usa/ml-playground
stack: Mixed (Python + devops folder); per README mostly ChatGPT-related learning experiments
domain: analytics
shape: top-level folders (`chatGPT/`, `devops/`)
last-synced-commit: c970cffd82ec17614c418bfa1d2346c923a4a058
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# ml-playground

## What it is
**"All kinds of learning experiments"** (per the one-line README — note the typo `ml-palyground`). Predates the fleet's standardized ML repos. The README documents an `chatGPT/.env` template with `OPENAI_API_KEY`, DB credentials, and app-port config — implying the `chatGPT/` folder contained early ChatGPT-API experimentation that fed into the later productionized `ml-service-chat` / `ml-bot-order-v2` lineage.

Last commit 2023-06-20 (`Merge branch 'update'`) — **three years stale**. Effectively archived.

## How it fits

- **Not a service.** Historical experiment dump.
- **Influenced** the early ChatGPT-based services (`ml-service-chat` launched 2023-10-09 per its README — only a few months after this repo's last activity).

## Build / test / run
```
# Manual — each folder is its own experiment.
# README documents the chatGPT/.env template required by the chatGPT/ subfolder.
```

## Don't-do-here / gotchas

- **Archive-candidate.** Three years stale; productionized work has moved to `ml-service-chat`, `ml-bot-order-v2`, etc. Confirm no helm chart references this before formal archive.
- **Typo in README title** (`ml-palyground` instead of `ml-playground`). Don't bother fixing — repo is on its way out.
- **`.env` placeholders include OpenAI and DB creds.** If anyone re-runs the chatGPT folder code, they need to populate those — but they shouldn't, because this work has been superseded.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/ml-service-chat.md` — productionized descendant.
- `~/projects/codebase-map/repos/ml-bot-order-v2.md` — newer-generation LLM service in the fleet.
- `~/projects/codebase-map/repos/ml-experiments-template.md` — the modern replacement for new experiments.
- `~/projects/codebase-map/relations/infrastructure-triage.md` — flag for archive on next refresh.
- `~/projects/codebase-map/domains/analytics.md`.
