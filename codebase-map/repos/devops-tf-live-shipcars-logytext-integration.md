---
repo: devops-tf-live-shipcars-logytext-integration
path: ~/projects/ship-cars-usa/devops-tf-live-shipcars-logytext-integration
stack: Terraform (live env) — GCP Pub/Sub + IAM
domain: integrations
shape: live-env (multi-env layout: `live/iam/`, `live/messaging/{prod,staging}/`, `live/tf-state/`)
last-synced-commit: 37ade28ea16e45de22108784ee0a67abe9095bb8
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# devops-tf-live-shipcars-logytext-integration

## What it is
The Terraform **live environment** repo that provisions the GCP-side resources backing the Logytext integration in `integrations-backend` (the seeded `integrations-backend` shadow's `logytext` module). Two GCP-resource categories:

- **`live/iam/`** — service-account definitions, external service-account references, and user/role bindings for the Logytext integration's GCP identity.
- **`live/messaging/{prod,staging}/`** — Pub/Sub topics + subscriptions for the integration:
  - `logytext.events` — outbound events to Logytext.
  - `logytext.hooks` — inbound webhook events from Logytext.
- **`live/tf-state/`** — the per-env Terraform backend (state bucket / config).

Per the `live/messaging/prod/topic-logytext_events.tf` module call, both topics are configured with **exactly-once delivery + message ordering + 5 max delivery attempts + 10–600s backoff + 7-day retention** — fleet-good defaults.

## How it fits

- **Provisions resources consumed by:** `integrations-backend`'s `logytext` module (the Logytext webhook consumer + outbound publisher). The Pub/Sub subscription names defined here are what `integrations-backend` references in its `application.properties`.
- **Consumes API of:** GCP (via `google` Terraform provider). Backend state stored per env in a GCS state bucket configured by `live/tf-state/`.
- **Publishes events to:** none directly (provisions topics, doesn't publish).
- **Owns data store:** GCS-backed Terraform state.

## Build / test / run
```
cd live/messaging/prod
terraform init
terraform plan
terraform apply       # only after review + change-control approval
```

Each subdirectory under `live/` is a standalone Terraform module rooted at its own `backend.tf`. **Always operate per-subdirectory** — there is no top-level Terraform module that wraps the entire repo.

## Key abstractions

- `live/messaging/{prod,staging}/topic-logytext_events.tf` — declares the events topic + subscription via a `module "logytext_events_pubsub" { source = "./module" ... }` invocation. The `./module` lives in a sibling internal Terraform module (probably copy-paste or git-submodule reference).
- `live/messaging/{prod,staging}/topic-logytext_hooks.tf` — the webhook-inbound counterpart.
- `live/iam/service-accounts-external.tf` + `users.tf` — IAM bindings (external = Logytext-side; users = Ship.Cars side).
- `live/tf-state/main.tf` + `backend.tf` — the bootstrap that creates the state bucket itself.

## Don't-do-here / gotchas

- **Probably belongs in the `infrastructure` domain, not `integrations`.** The repo is pure IaC supporting the Logytext integration; the *integration logic* lives in `integrations-backend`. The pattern across the fleet: per-product `devops-tf-live-*` repos are infrastructure. The shadow currently sits in `integrations` because the name matched; consider re-domain on the next infrastructure-triage refresh.
- **Two parallel envs (`prod`, `staging`) — no `dev` / `qa` envs visible.** Either Logytext doesn't need them, or they're deployed via a different IaC repo. Worth confirming before assuming a missing dev env is a gap.
- **Both topics use `enable_exactly_once_delivery = true`.** Fleet-positive — but enables the GCP-side guarantee only; the consumer (`integrations-backend`'s `LogytextPubSubConsumer`) must implement idempotency on the consumer side to actually achieve at-most-once effects.
- **`max_delivery_attempts = 5` + DLQ is not declared in the visible files** — confirm whether a dead-letter topic is set up via another Terraform module or via the GCP console.
- **Last touched 2025-08-19** — relatively stale for a live IaC repo. Verify any new GCP API changes haven't outdated the resource shapes (e.g. provider version bumps).
- **Don't run `terraform apply` from a personal machine.** State is shared per env via the GCS backend — concurrent applies risk state corruption. CI / pipelines should be the only execution path.
- **`.terraform.lock.hcl` files are checked in** (visible in the tree). Honor them — `terraform init -upgrade` should be deliberate, not accidental.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/integrations-backend.md` — the Java consumer of the topics this repo provisions; specifically the `logytext` module (`LogytextPubSubConsumer.java`).
- `~/projects/codebase-map/relations/infrastructure-triage.md` — flag for re-domain to `infrastructure` on next refresh.
- `~/projects/codebase-map/domains/integrations.md`.
