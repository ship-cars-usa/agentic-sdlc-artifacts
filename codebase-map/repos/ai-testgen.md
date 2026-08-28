---
repo: ai-testgen
path: ~/projects/ship-cars-usa/ai-testgen
stack: Python 3.9+ / Claude (Anthropic) + Jira REST + Figma REST / AWS Secrets Manager
domain: analytics
shape: single-module (flat scripts)
last-synced-commit: 65b00600de144321cb0a34ea9da1ba6f17f667a6
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# ai-testgen

## What it is
**AI Test-Case Generator** — a Python automation tool that fetches a Jira issue, follows links to its Figma designs, runs the combined ticket-text + design context through **Claude** to generate test scenarios, and posts the generated test cases back as a Jira comment on the originating issue. Originally written 2026-01-27 (single commit `LITE-7061`).

Not a long-running service — it's a script that runs on-demand (CLI-style `main.py`) per issue.

## How it fits

- **Consumes:**
  - **Jira REST API** (issue fetch + comment post) — credentials via `secrets_manager.py` reading from AWS Secrets Manager.
  - **Figma REST API** (design fetch via links found in the Jira ticket). Optional — also accessible via Claude Code MCP per the README.
  - **Anthropic Claude API** (the AI model that generates test cases).
- **Publishes:** Jira comments only.
- **Owns data store:** none (stateless; intermediate state via `figma_data.json` for caching during a run).

## Build / test / run
```
pip install -r requirements.txt
# AWS creds with access to the company's Secrets Manager required.
python main.py --issue-key <JIRA-KEY>
```

## Key abstractions

- `main.py` — CLI entry; orchestrates fetch → Claude call → post comment.
- `ai_generator_claude.py` — Claude API wrapper; prompts + structured-output handling.
- `jira_fetch.py` — Jira REST client (issue details, attachments, linked design URLs, comment posting).
- `figma_fetch.py` — Figma REST client.
- `secrets_manager.py` — AWS Secrets Manager wrapper for API tokens.
- `logger.py` — structlog or stdlib logging setup.
- `figma_data.json` — sample / cached Figma payload (probably a fixture).
- `docs/` — internal documentation (worth reading for prompt templates).

## Don't-do-here / gotchas

- **Posts directly to the originating Jira issue.** If run against a production-priority ticket by accident, the generated test cases land as a real comment visible to engineering. Treat as a "test ticket" sandbox before running against live work.
- **AWS Secrets Manager dependency.** Requires AWS IAM credentials with `secretsmanager:GetSecretValue` for the relevant secret names. Local dev needs AWS CLI configured.
- **Anthropic API key cost.** Each run consumes Claude tokens proportional to the issue + design size. No rate limiting visible in the script.
- **No tests in repo.** Single-commit MVP; treat any modification as functionally untested.
- **Single-commit `LITE-7061`** suggests this is a recent / experimental tool; status unclear whether it's actively used or shelved. Worth confirming with the QA team.
- **Figma + Jira tokens are environment-specific.** Don't commit personal access tokens; use the Secrets Manager path.

## Relevant ADRs / docs
- `~/projects/codebase-map/domains/analytics.md`.
