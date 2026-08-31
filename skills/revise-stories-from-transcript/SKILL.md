---
name: revise-stories-from-transcript
description: >
  Turn a meeting/call transcript into story-revision suggestions for a Jira epic. Use when
  asked to "review this transcript against <EPIC>", "compare the call to the stories",
  "what should we change in the epic after this call", "reconcile this transcript with Jira",
  or "create revision suggestions from these notes" (e.g. "review the test-prep transcript
  against SCP-14954"). Reads a transcript file, fetches the epic + all child stories + their
  comments + the linked PRD (read-only, via the skill's own Jira client), reviews every linked
  Figma design via the Figma MCP (fanned out to sub-agents), then compares what was said against
  each story and emits — as a self-contained, editable, copy-to-clipboard HTML artifact — a
  per-story revision (link + verbatim quote + suggested change + paste-ready Jira draft),
  proposed net-new stories, a Figma design-gap review, and a consolidated open-questions
  register. Read-only: never creates or edits Jira issues.
argument-hint: "<transcript-file> <EPIC-KEY>   e.g. notes.txt SCP-14954"
---

# Revise epic stories from a call transcript

Given a **transcript file** and an **epic key**, this skill produces the story-revision
deliverable as a published Artifact — same look and behaviour as the reference artifact
(light "ledger" theme, editable paste-blocks with Copy buttons). It compares the conversation
against every child story and the PRD, and surfaces requirement changes, open questions,
net-new stories, and Figma design gaps.

It is an **orchestration** skill: one small fetch driver + Figma sub-agents + this thread doing
the analysis and authoring. **It never writes to Jira** (read-only token) and **does not run any
text-simplification pass** (deliberately out of scope — see `references/analysis-method.md`).

Path placeholders below resolve from the `install-sdlc.sh` workspace layout (`<REPO>` =
the `agentic-sdlc-artifacts` checkout; `<GROOMING_DIR>` = `$GROOMING_DIR` or `<REPO>/grooming`).
The scripts are under `<REPO>/skills/revise-stories-from-transcript/scripts/`; the reference
docs under `references/`.

## Prerequisites

- **Python 3** (stdlib only).
- **A read-only Jira token.** The skill's client (`scripts/jira_client.py`) discovers it, first
  match wins: `$JIRA_READ_TOKEN` → a `jira-read.txt` next to the script → `<GROOMING_DIR>/jira-read.txt`.
  It is intentionally secret-free (no token is committed into the skill). Verify with:
  ```bash
  test -f <GROOMING_DIR>/jira-read.txt || test -n "$JIRA_READ_TOKEN" && echo token-ok
  ```
- **The claude.ai Figma MCP connector** for Step 3. If it isn't authenticated (`/mcp` → "claude.ai
  Figma"), the skill still runs — it leaves the Figma links for a human and says the design review is pending.

## Step 1 — Read the transcript

`Read` the transcript file the user gave. Understand who is speaking and pull out the
requirement-relevant claims: decisions, disagreements, numbers said aloud, operational
constraints (funding cycles, cut-offs, manual steps, approvals), and any need that implies new
software. Note `mm:ss` timestamps — quotes in the artifact are verbatim and cite them.

## Step 2 — Fetch the epic, its stories, and the PRD

Determine the epic key: from the user's argument, else infer it from the transcript and confirm
with the user before proceeding (don't guess silently).

```bash
python3 <REPO>/skills/revise-stories-from-transcript/scripts/fetch_epic.py SCP-14954
```

Prints one markdown block: the **epic**, the **linked PRD/product issue** expanded one level
(the real scope — in/out of scope, definitions, fee model), every **child story** (status,
labels, description with link/card URLs preserved, issue links, comments), **each story's
subtasks expanded one level deeper** (their own summary/status/description — so a story that has
already been broken down isn't treated as a black box), and a consolidated **`## Figma design
links`** section (every figma.com URL found **anywhere** — epic, PRD, each story's description
*and* its comments, and subtasks — tagged with the issue it came from). Read all of it — the PRD
and comments carry the scope the transcript pushes against, and a subtask can hold an AC the
parent story only gestures at. (`--json` for raw fields; `--no-comments` to skip comment bodies.)

## Step 3 — Review the Figma designs (always, via MCP sub-agents)

For the links the driver surfaced, fan out **one sub-agent per design surface in a single
message** (parallel), `subagent_type: "general-purpose"`. Give each agent the node URL(s), the
story AC that surface must cover, and the **specific requirement uncertainties from the call** to
check against. Each returns: what the screen shows, **missing design**, **design changes needed**,
and variants present/missing. The exact prompt skeleton and rules are in
`references/analysis-method.md` (§4). These are external URLs the read token can't download — the
MCP is the only way to see them. If the connector isn't authenticated, skip and mark the design
review pending.

## Step 4 — Compare and derive findings

Following `references/analysis-method.md`: hold each story's AC against the transcript and the
PRD. Classify every finding as **requirement change / conflict**, **open question**, or
**net-new**. Every per-story revision must carry all four of: the story **link**, a **verbatim
quote** of the current text, a **suggested change**, and a **paste-ready Jira draft**. State
cross-cutting findings once (F1, F2, …) and link them from the per-story cards. Fold the Step 3
Figma results into the design-gaps section. Finish with a consolidated open-questions register
(each with a suggested owner).

## Step 5 — Build and publish the artifact

Author only the **BODY fragment** (the "At a glance" table through the register) using the exact
markup in `references/artifact-format.md`, plus a small **META json** for the header text. Then
staple them into the template (which owns the CSS, header scaffold, legend, and the
copy/editable `<script>` — so the page looks and behaves identically to the reference artifact):

```bash
python3 <REPO>/skills/revise-stories-from-transcript/scripts/build_artifact.py \
  BODY.html META.json /path/to/<epic>-revisions.html
```

Write `BODY.html` and `META.json` to your scratchpad. `build_artifact.py` warns on any unfilled
placeholder. Then publish the result with the **Artifact** tool (a distinctive 2–4 word title
like "Faster Payments — Story Revisions", favicon `⚡`, a one-line description). The output has no
`<!doctype>`/`<head>`/`<body>` — it is ready for the Artifact tool as-is. Editable paste-blocks
and Copy buttons come from the template automatically; do not re-implement them.

Hand the user the artifact link and a short summary of the headline findings. Offer — but do not
perform — pushing any subset back to Jira as comments (that needs write access and explicit
per-ticket go-ahead).

## Guardrails

- **Read-only.** Never create or edit Jira issues. Every paste-block is a draft for a human.
- **Quotes are verbatim** (transcript lines keep speaker + timestamp; story text stays exact).
  Transcription can contain errors — the foot says so and tells the reader to verify before pasting.
- **No text-simplification pass** — out of scope for this skill unless the user explicitly asks
  after the fact.
- Don't restyle the artifact; the template is a byte-for-byte lift of the reference UI.
