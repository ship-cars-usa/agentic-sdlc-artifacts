# Analysis method — transcript vs. epic stories

The job: read a meeting/call transcript, compare what was said against every child
story of a Jira epic (and the epic's PRD), and produce **revision suggestions** —
per story: a link, a verbatim quote, and a suggested change — plus **design gaps**
from the linked Figma. Read-only: never write to Jira.

## 1. Classify every finding

- **Requirement change / conflict** (`change`) — the transcript contradicts,
  narrows, or invalidates a current AC, title, or design. Example: a term the
  stories promise ("2 business days") that the operational reality can't deliver.
- **Open question** (`open`) — a decision the transcript surfaces but leaves
  undecided (owner named or not). Example: "business days vs calendar days —
  Operations decides." Give it a suggested owner in the register.
- **Net-new** (`new`) — a real need raised in the call that **no current story**
  (and sometimes the PRD's stated scope) covers. Propose a story draft.

## 2. What to compare

Iterate over **every child story of the epic, and every subtask under each story** (the driver
expands both — don't skip the subtasks; a broken-down story often carries its real AC there).
For each, read its AC and hold it against:
- the transcript (what stakeholders actually said — quote it with `mm:ss`), and
- the PRD/product issue (what the pilot officially scopes in/out).

The artifact's unit is the **story** (one card per child story). Subtasks inform that story's
card — fold a subtask-level gap into the parent story's card, and only give a subtask its own
card if the subtask itself needs a revision.

Hunt specifically for:
- **Numbers and terms** the stories hard-code (fees, day counts, defaults) that the
  transcript says are *not final*, *not decided*, or *not achievable*.
- **Titles / user stories** that name a value now in doubt.
- **Operational realities** (funding cycles, cut-offs, manual steps, approvals) that
  change what the software must do or make a promised behaviour infeasible.
- **New surfaces / workflows** the call implies (an ops queue, a reject path, a new
  document rule) with no story — and whether they clash with the PRD's assumptions.
- **Story ↔ PRD conflicts** (e.g. a story allows changing a choice; the PRD lists that
  as out of scope) — flag them explicitly.

## 3. Shape of each suggestion (non-negotiable)

Every per-story revision must carry all four:
1. **Link** to the story (`https://shipcars.atlassian.net/browse/<KEY>`).
2. **Verbatim quote** of the current story text it changes (a `<blockquote>`).
3. **Suggested change** in plain terms.
4. **Paste-ready Jira draft** — the exact text to drop into the story or a comment,
   in a `.jira` `<pre>` block.

State cross-cutting findings **once** (F1, F2, …) and link them from the per-story
cards, rather than repeating the evidence in every card.

## 4. Figma evaluation (always, if any link exists)

`fetch_epic.py` prints a `## Figma design links` section — every figma.com URL found
anywhere (epic, PRD, each story's description and its comments, and subtasks), tagged
with the issue it came from. **Iterate over all of them** (multiple links can hang off one
story). Review each surface against the *transcript-revised*
requirements. Fan out one sub-agent per design surface **in a single message**
(parallel), `subagent_type: "general-purpose"`. Give each agent: the node URL(s), the
story AC it should cover, and the specific requirement uncertainties from the call to
check against. Ask each to report, as text (no files):

- what the screen shows (where term / fee / carrier-pay / selection / confirmation appear);
- **missing design** — required elements with no design;
- **design changes needed** — elements that conflict with the call's revised requirements;
- variants/states present vs. missing.

Prompt skeleton:
```
Evaluate this Figma frame for <feature> against the requirements.
Use the claude.ai Figma MCP tools (get_screenshot, get_metadata, get_design_context);
load their schemas first with ToolSearch "select:mcp__claude_ai_Figma__get_screenshot,
mcp__claude_ai_Figma__get_metadata,mcp__claude_ai_Figma__get_design_context".
FILE: <fileKey>  NODE(S): <url(s)>
STORY REQUIREMENTS: <the AC this surface must cover>
CHECK AGAINST THESE UNCERTAINTIES FROM THE CALL: <the specific findings — e.g. term may
change, fees not final, single vs multi option, a value that must come from settings>.
Report: what the screen shows; MISSING DESIGN; DESIGN CHANGES NEEDED; variants present/missing.
Do NOT write files. If Figma access fails, say so with the error.
```
Fold the results into the Figma section (decision/defect cards + the missing-design
table). Extract the concrete design work items so the "Designs" tracking ticket can own them.

If the Figma MCP is not authenticated (`/mcp` → "claude.ai Figma"), don't guess — leave
the links for a human and say the design review is pending.

## 5. Consolidated register

End with a table of every open question, each with a **suggested owner** and the stories
it blocks. This is the "what has to be decided" checklist.

## Do NOT simplify the language

This skill deliberately **omits** any reading-level / text-simplification pass. Write
clear, correct, professional prose in one register and stop. Do not run a second pass to
"make it easier for non-native speakers" unless the user explicitly asks for it after the
artifact is produced — it is out of scope for this skill.

## Read-only, drafts only

No Jira issues are ever created or edited. Every `<pre>` is a *draft* for a human to paste.
Quotes can contain transcription errors — say so in the foot and tell the reader to verify
against the live tickets before pasting.
