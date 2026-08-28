# ADR 0002 — Keep the No-Files-In-Repos Constraint

**Status:** Accepted (re-confirmed 2026-05-08)
**Supersedes:** none. Re-confirms the original v1 constraint after the shadow catalog has been built and proven across all 232 repos.
**Date:** 2026-05-08

## Context

ADR 0001 captured the *original* decision to use a shadow catalog because the user explicitly forbade adding files inside any of the 232 repos. After Phase 2 (full-fleet stub coverage) and Phase 4 (9 domain rollups + service-graph from seeds) the catalog was a working, useful artifact, and the user was offered the option to relax the constraint and graduate the catalog into per-repo `CLAUDE.md` files (PLAN.md Phase 7).

The user re-confirmed: **keep the constraint.**

## Decision

The shadow catalog at `~/projects/codebase-map/` remains the **only** location for per-repo metadata. No `CLAUDE.md`, `catalog-info.yaml`, or other map artifact may be added to any repo under `~/projects/ship-cars-usa/`.

## Why this re-confirmation matters

Future sessions might naively assume the original ADR was provisional — a "we can do better later" gesture — and start migrating shadows into repos. This ADR makes the choice durable: the central catalog is the *intended* end state, not a stepping stone.

Concrete consequences for future work:

1. New repo created? `python3 codebase-map/scripts/bootstrap_repo_md.py <repo>` and edit the shadow. **Do not** add a CLAUDE.md to the new repo.
2. Tempted to push richer per-repo onboarding docs into the repo? Add them to the shadow doc's *Build / test / run* and *Don't-do-here* sections instead.
3. Backstage adoption (Phase 3, currently deferred)? The Backstage `Location` entity points at `codebase-map/catalog/`; do not add `catalog-info.yaml` files into repos.
4. Tooling that *expects* per-repo files (e.g., GitHub's CODEOWNERS, IDE auto-discovery): live with the constraint. Where a tool genuinely cannot work without a file in the repo, propose an exception in a follow-up ADR; do not act unilaterally.

## Tradeoffs (still accepted)

Same as ADR 0001:
- Drift detection requires the central `drift_check.py` (now wired to launchd as of Phase 6) instead of being implicit-in-the-commit.
- Per-repo discovery ("open the repo, see CLAUDE.md") requires the orchestrator at `~/projects/CLAUDE.md` to point Claude at the shadow.
- Backstage / IDE plugins that look natively for in-repo files won't find them; we ingest centrally instead.

## Migration path remains documented

If this decision is ever reversed in a future ADR, the migration recipe in ADR 0001 still applies: a script reads each shadow and writes its body to `~/projects/ship-cars-usa/<repo>/CLAUDE.md`, then deletes the shadow. The reverse migration is also cheap. So while this ADR makes the *current* answer durable, it does not lock the design forever.
