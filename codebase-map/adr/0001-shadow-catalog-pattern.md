# ADR 0001 — Shadow Catalog Pattern

**Status:** Accepted
**Date:** 2026-05-08
**Context:** Initial design of `~/projects/codebase-map/`.

## Decision

Maintain a **central, repo-external catalog** at `~/projects/codebase-map/` that mirrors per-repo metadata (CLAUDE.md content, Backstage `catalog-info.yaml`, domain assignment, ownership) without writing those files into the repos themselves. Every shadow doc names its target repo via `repo:` and `path:` frontmatter fields and pins its sync point with `last-synced-commit`.

## Why not the standard pattern (per-repo CLAUDE.md / per-repo catalog-info.yaml)?

The standard recommendation — and the original recommendation in the survey at the top of this work — was to put a `CLAUDE.md` and a `catalog-info.yaml` at the root of each of the 232 repos. The user explicitly ruled this out:

> "add it in a separate folder on top level and don't change any existing files nor add files in repo folders"

Reasons the user holds this constraint matter for future readers:
- Each of the 232 directories is a separately-owned git repo. Adding a file means a commit per repo, a PR per repo, and a maintainer-relationship per repo. That's 232 social transactions before the map is useful.
- Many repos are infrequently touched; a local file would rot quickly, and the staleness would be invisible to the central tooling.
- The user wants the map to be regenerable, movable, and version-controlled independently of any individual repo's lifecycle.

## Tradeoffs accepted

| Standard pattern wins at | Shadow pattern wins at |
|---|---|
| Drift detection is automatic (file lives next to the code) | Single source of truth; can be regenerated/moved/re-indexed centrally |
| Backstage / IDE plugins find catalog files natively | No 232 PRs needed to bootstrap |
| Discovery is "open the repo, see CLAUDE.md" | Discovery is "open `~/projects/codebase-map/repos/<repo>.md`" |
| Owner of repo controls their own metadata | Map owner controls metadata centrally; clearer accountability |

## How drift is mitigated despite physical separation

- Every shadow records `last-synced-commit`. `scripts/drift_check.py --all` walks every shadow and compares against `git rev-parse HEAD` of the target repo. With `--mark-stale`, frontmatter `status` is rewritten in place.
- Status values (`seed | stub | verified | stale`) make staleness explicit in human-readable form. A consumer (Claude or human) can choose to ignore `stale` shadows and re-read source.
- A weekly sweep is the recommended cadence (Phase 6 turns this into a scheduled job).

## Migration path if the constraint is ever lifted

If the user later decides per-repo files are acceptable:
1. Write a script that reads each shadow and writes the body (without the `path:` and `last-synced-commit:` fields, which become unnecessary in-repo) to `~/projects/ship-cars-usa/<repo>/CLAUDE.md`.
2. For Backstage YAMLs, write `catalog/components/<repo>.yaml` content into `~/projects/ship-cars-usa/<repo>/catalog-info.yaml`.
3. Delete the shadow folder once each repo's PR is merged. Keep `relations/`, `domains/`, and `adr/` here — those genuinely belong central.

This migration is one-way easy. The reverse (going from per-repo files back to shadows) is a `git rm` per repo and a script that pulls the content back. So this decision is reversible at low cost.

## Status of related concerns

- **Per-repo `CLAUDE.md` for AI agents:** the shadow doc serves the same purpose for now. The orchestrator at `~/projects/CLAUDE.md` instructs Claude to read the shadow first.
- **Backstage adoption:** if Backstage is later stood up, point its GitHub Discovery at `codebase-map/catalog/` (treat the map directory as a `Location` source). No need to push catalog-info.yaml into each repo.
- **SCIP / xref index:** orthogonal to this decision; lives outside the codebase-map folder when added.
