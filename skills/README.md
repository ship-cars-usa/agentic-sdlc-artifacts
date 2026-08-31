# Vendored Ship.Cars SDLC skills

This is the **repo-wired** copy of the Ship.Cars Claude Code skills, vendored into
`agentic-sdlc-artifacts` so they are self-contained and workspace-relative — **no
hardcoded user paths**. These are distinct from a user's personal `~/.claude/skills`
or `~/projects/.claude/skills`: those keep working locally; this bundle is the one
`install-sdlc.sh` copies into `<WORKSPACE>/.claude/skills/` (re-run install-sdlc.sh to
update) so any checkout of the workspace has them.

## Skills in the bundle

| Skill | What it does | Path / credential deps |
|---|---|---|
| `breakdown-story` | Break down + design a Jira story across the stack; emits markdown + HTML + a CDR folder. | Jira token, Figma MCP, gcloud (bug tickets), `<SHIP_CARS_DIR>`, `<CODEBASE_MAP_DIR>` |
| `write-test-cases` | Derive a Test Design Document (+ UI mockups) for a Jira story. | Jira token (or Atlassian MCP), Figma MCP, `<SHIP_CARS_DIR>` |
| `revise-stories-from-transcript` | Turn a meeting transcript into per-story revision suggestions for an epic. | Jira token (own client), Figma MCP |
| `diagnose-db-load` | Trace a Cloud SQL load/latency spike to the offending code. | gcloud (read-only), `<SHIP_CARS_DIR>` |
| `be-principal-engineer` | Principal-engineer review for Java/Python. | none |
| `be-ios-principal-engineer` | Principal-engineer review for iOS/Swift. | none |

## Path-resolution convention

Every vendored Python script resolves its locations from **its own file position**
(`__file__`), with env overrides — never `/Users/...` and never a hardcoded
`~/projects`. `install-sdlc.sh` lays the workspace out as:

```
<WORKSPACE>/
├── ship-cars-usa/            # the org code repos  → <SHIP_CARS_DIR>
├── agentic-sdlc-artifacts/   # this repo           → <REPO>
│   ├── skills/<name>/…       # the vendored skills
│   ├── grooming/             # vendored jira_client.py (+ your gitignored jira-read.txt)
│   ├── codebase-map/         # cross-repo shadow docs
│   ├── jira-breakdowns/      # breakdown-story output
│   ├── CDR/                  # Change Design Records
│   └── tdd/                  # write-test-cases output
└── .claude/skills/<name>     # copies of <REPO>/skills/<name> (re-run install-sdlc.sh to update)
```

| Placeholder | Env override | Default |
|---|---|---|
| `<REPO_ROOT>` | — (computed from `__file__`) | two dirs up from a skill dir (`…/skills/<name>/` → repo) |
| `<WORKSPACE_ROOT>` | `AGENTIC_SDLC_WORKSPACE` | `dirname(<REPO_ROOT>)` |
| `<SHIP_CARS_DIR>` | `SHIP_CARS_DIR` | `<WORKSPACE_ROOT>/ship-cars-usa` |
| `<CODEBASE_MAP_DIR>` | `CODEBASE_MAP_DIR` | `<REPO_ROOT>/codebase-map` |
| `<GROOMING_DIR>` | `GROOMING_DIR` | `<REPO_ROOT>/grooming` |
| `<BREAKDOWNS_DIR>` | `BREAKDOWNS_DIR` | `<REPO_ROOT>/jira-breakdowns` |
| `<CDR_DIR>` | `CDR_DIR` | `<REPO_ROOT>/CDR` |
| `<TDD_DIR>` | `TDD_DIR` | `<REPO_ROOT>/tdd` |

The **Jira read token** is discovered first-match-wins: `$JIRA_READ_TOKEN` (or
`$JIRA_API_TOKEN`) → `<GROOMING_DIR>/jira-read.txt`. The token file is **never**
committed (see the repo `.gitignore`).

## Prerequisites (post-install)

1. Run `install-sdlc.sh` — it lays out `ship-cars-usa/` + this repo and copies the
   skills into `<WORKSPACE>/.claude/skills/` (re-run it, e.g. after `git pull`, to update them).
2. Provide a **Jira read token** (`$JIRA_READ_TOKEN` or `<GROOMING_DIR>/jira-read.txt`).
3. Connect the **claude.ai Figma** MCP (Figma-review steps).
4. Authenticate **gcloud** with access to the environment projects (log/DB steps).
5. Configure **git** (for committing generated artifacts).

With those in place and no other setup, the skills are fully functional.
