# `codebase-map/`

A central, file-based representation of the 232 sibling repos under `~/projects/ship-cars-usa/`. Designed so Claude Code (and humans) can ask "what is this service?", "who owns it?", "what does it talk to?" without re-reading every repo from scratch each session.

## Why this exists

`~/projects/PROJECTS_INDEX.md` gives one line per repo. That's enough for "list all Python services" but not for "what does `chat-backend` actually do, and what would I need to know to safely edit it?" This folder is the next layer of depth.

The standard pattern (per-repo `CLAUDE.md`, per-repo `catalog-info.yaml`) was rejected for this codebase because the user wants the 232 repos to remain pristine. So we use a **shadow catalog** — every artifact that would normally live inside a repo is mirrored here, indexed by repo name. See `adr/0001-shadow-catalog-pattern.md` for the rationale and the migration path if the constraint is ever lifted.

## Layout

```
README.md                 you are here
PLAN.md                   persistent multi-session work plan
repos/                    one .md per repo (the "shadow CLAUDE.md")
  _index.md               alpha-sorted list of existing shadows
  <repo>.md
domains/                  logical-domain rollups (phase 4+)
catalog/                  Backstage catalog-info.yaml shadows (phase 3+)
relations/                cross-cutting facts (service-graph, data-stores, ownership)
adr/                      decisions about the *map itself*
workspaces/               VS Code multi-root workspace files per domain
scripts/                  bootstrap / drift_check / verify_links (Python 3 stdlib only)
templates/                shadow-doc / domain / catalog-component skeletons
```

## How a shadow doc is structured

YAML frontmatter (`repo`, `path`, `stack`, `domain`, `shape`, `last-synced-commit`, `last-synced-date`, `maintainer`, `status`) followed by Markdown sections: *What it is*, *How it fits*, *Build/test/run*, *Key abstractions*, *Don't-do-here / gotchas*, *Relevant ADRs / docs*. See `templates/repo.md.template` for the canonical shape.

`status` is one of:
- `seed` — hand-authored from real review material; richest content.
- `stub` — output of `bootstrap_repo_md.py`; thin but accurate (frontmatter + a placeholder body).
- `verified` — a human re-reviewed and confirmed accuracy after the last sync.
- `stale` — `drift_check.py` flagged divergence from the repo's current HEAD.

## Workflows

**New repo appears.** `python3 scripts/bootstrap_repo_md.py <repo>` to lay down a stub. Edit by hand to add real content. Promote `status: stub` → `status: seed` when you're confident.

**Weekly drift sweep.** `python3 scripts/drift_check.py --all --mark-stale`. Read the report. Resync shadows that have drifted in ways that matter.

**Pre-commit lint.** `python3 scripts/verify_links.py`. Fails on missing frontmatter, broken cross-refs, or `_index.md` mismatch.

## Coverage in v1

- 30 backend services have shadow docs (the 7 already reviewed in `~/projects/quarkus-fleet-review-2026-05-07.md` plus 23 core-domain Java/Quarkus + Spring services).
- The other ~200 repos are not yet covered. Phase 2 (a separate session) auto-stubs them.
- No domain rollups, no Backstage YAMLs, no embeddings yet. Those are phases 3–5.

## Pointers

- Persistent plan: `PLAN.md` (mirror of `~/.claude/plans/pick-at-random-and-effervescent-aurora.md`).
- Top-level orchestrator that tells Claude how to use this map: `~/projects/CLAUDE.md`.
- The 232-repo inventory: `~/projects/PROJECTS_INDEX.md`.
- The fleet review that seeded the first 7 shadows: `~/projects/quarkus-fleet-review-2026-05-07.md`.
- The companion anti-pattern doc: `~/projects/quarkus-rest-client-timeout-anti-pattern.md`.
