# Ownership

Which team owns which service. Placeholder in v1 — `maintainer: unknown` is the default in shadow frontmatter until a real source-of-truth (PagerDuty schedules, GitHub CODEOWNERS, internal team-services spreadsheet) is identified.

## Conventions

- `team` is the canonical team name (no aliases, no Slack channel names).
- `since` is `YYYY-MM-DD` if known.
- `secondary` is the team that handles overflow / escalation.

## Edges

| Service | Team | Since | Secondary | Evidence |
|---|---|---|---|---|
| _none recorded yet_ | | | | |

## Source-of-truth candidates (to confirm)

- GitHub `CODEOWNERS` file at `~/projects/ship-cars-usa/<repo>/CODEOWNERS` — opportunistic; not all repos have it.
- PagerDuty service definitions — authoritative for on-call but may not match dev ownership.
- Internal team-services spreadsheet — ask user when this phase starts.
- `git shortlog -sn` per repo — top committer is *a* signal, not an authoritative answer.

## Notes

- A repo can have **maintainer** (the team responsible for changes) and **on-call** (the team that gets paged). They're often the same; when they differ, capture both.
- A service with no clear owner is a flag, not a feature. Mark explicitly: `team: unowned`.
