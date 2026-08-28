# `codebase-map/workspaces/`

VS Code multi-root workspace files. Each one is a domain-scoped lens onto a subset of the 232 repos plus the codebase-map itself. Open one when you want Claude Code (or your editor) to have *just* that domain in context.

## Why per-domain instead of one giant workspace

Loading 232 repos into one workspace breaks file watchers, search latency, and your sanity. Per-domain workspaces keep the loaded surface to the 5–30 repos that are actually relevant to whatever you're doing right now.

## Existing workspaces (v1)

- **`all-backend.code-workspace`** — the 7 fleet-reviewed services. Seeded for early testing of the map. Will grow as more backend shadows reach `seed` status, or split into `payments.code-workspace`, `integrations.code-workspace`, etc. at phase 4.

## Adding a new workspace

1. Copy `all-backend.code-workspace` to `<domain>.code-workspace`.
2. Replace the `folders` array with the repos in that domain (look up via `domain:` in shadow frontmatter, or read `domains/<domain>.md` once phase 4 lands).
3. Always include the `_codebase-map` and `_projects-root` folders at the top so Claude can navigate to shadow docs and PROJECTS_INDEX.md without leaving the workspace.

## Tips

- Add `.vscode/settings.json` overrides at the workspace level rather than per-repo — keeps repos pristine (the no-files-in-repos constraint).
- Path is relative to *this folder* (`workspaces/`), so the prefix `../../ship-cars-usa/<repo>` is correct.
