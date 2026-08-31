---
name: write-test-cases
description: >
  Write QA test cases for a Jira story by reading the ticket, its Figma designs, and the
  implementing repo(s). Use when asked to "write test cases", "generate test cases", "create a
  test plan", "design tests", "QA this story", or "what should we test for <JIRA-KEY>" (e.g.
  "write test cases for SCP-14292"). Fetches the ticket (read-only) via the Atlassian MCP, reviews
  every Figma link via the Figma MCP, fans out read-only Explore sub-agents over the implementing
  repos to ground cases in real behavior, then selects and applies formal techniques by feature type
  (equivalence partitioning, boundary-value analysis, decision tables, state transitions, pairwise,
  CRUD coverage, auth matrix, accessibility, security vectors, SFDPOT, zero-one-many, negative
  testing — grounded in ISTQB/ISO-25010/OWASP/WCAG), expanding the epic + subtasks + linked issues
  and tracking AC- and subtask-level coverage. It explicitly hunts edge-case scenarios and flags any
  behavior that CANNOT be extrapolated from the requirements as an open question. Output is a Test Design Document written
  as both a markdown file and a self-contained HTML page in a dedicated <TDD_DIR>/ folder — plus, whenever
  the story involves UI interaction, a self-contained per-step UI mockup page that visualizes each
  scenario's Given/When/Then. It only writes test cases — it does not design the implementation,
  evaluate Definition-of-Ready, or create Jira issues.
argument-hint: "<JIRA-KEY> [output-dir]   e.g. SCP-14292   (default output: <TDD_DIR>/)"
---

# Write test cases for a Jira story (Jira + Figma + repos → Test Design Document)

Given a Jira key, this skill produces a **Test Design Document (TDD)**: a traceable set of QA test
cases grounded in the story's acceptance criteria, its Figma designs, and the actual behavior of
the implementing repo(s) — plus an explicit **edge-case** pass and an **open-questions** list for
behavior the requirements don't define. It writes the result to `<TDD_DIR>/<KEY>.md` **and**
`<TDD_DIR>/<KEY>.html` — and, **whenever the story involves UI interaction, also `<TDD_DIR>/<KEY>-mockups.html`**,
a per-step visualization of each scenario (Step 8). The mockups are a standard deliverable for any
UI-facing story, not an opt-in extra.

It is an **orchestration** skill: fetch (MCP) → review designs (MCP) → discover behavior
(sub-agents) → derive cases (this thread) → emit md + html → **emit per-step UI mockups when UI is
involved** (Step 8, via an intent-aware sub-agent).

**Scope — this skill only writes test cases.** It deliberately does *not*:
- design the implementation or propose code changes,
- evaluate Definition-of-Ready or estimate work,
- create or edit Jira issues (all Jira access is read-only),
- write automated test *code* (it produces the case specs an engineer or a test-writer agent then
  automates).

If a full engineering breakdown is wanted, that's a different skill; here, stay on test cases,
edge cases, and open questions.

**Path placeholders below resolve from the `install-sdlc.sh` workspace layout** (`<REPO>` =
the `agentic-sdlc-artifacts` checkout; test-design output goes to `<TDD_DIR>` = `$TDD_DIR` or
`<REPO>/tdd`). The skill's own files are at `<REPO>/skills/write-test-cases/` — the HTML helpers
are `scripts/wrap_html.py` and `assets/html_skeleton.html`, and the technique catalog is
`reference/test-design-techniques.md`. **Read the reference file before deriving cases** — it is
the source of the techniques and the edge-case checklist this skill applies.

## Prerequisites

- **Atlassian MCP** (Jira) connected — this is how the ticket is read. Confirm it's available
  (e.g. `mcp__atlassian__getJiraIssue` is callable, or run `/mcp`). You need the **Cloud ID** and
  the issue key. See the sibling `atlassian-tools` plugin's `atlassian-jira` skill for the exact
  tool shapes and field-discovery. If Jira MCP isn't connected, ask the user to paste the ticket
  text and proceed from that — say you're doing so.
- **Figma MCP** connected (`claude.ai Figma` connector or equivalent) for Step 2. A View seat is
  enough for `get_screenshot`/`get_metadata`. If it isn't connected, don't silently skip designs —
  leave the Figma links listed and raise an open question for each un-reviewed frame.
- **The implementing repo(s)** available locally for Step 3. If you don't know which repo(s),
  ask the user or infer from the ticket's components/keywords; the fan-out can run against any repo
  path the user names.
- **Python 3** (stdlib only) for the HTML step (`scripts/wrap_html.py`) and, for UI stories, the
  per-state screenshot planner (`scripts/figma_state_shots.py`, Steps 2/8). Verify both resolve:
  ```bash
  python3 <REPO>/skills/write-test-cases/scripts/wrap_html.py 2>&1 | head -1
  python3 <REPO>/skills/write-test-cases/scripts/figma_state_shots.py 2>&1 | head -1
  ```
  (each prints its usage docstring — the "no args" behavior, confirming it runs.)
- **Encoding — emit pure-ASCII output so it can't mojibake.** A file written as UTF-8 renders fine
  in a compliant browser but turns typographic characters (`—` em-dash, `·` middot, `→`/`↔` arrows,
  `“ ”` curly quotes, `⚠`/`❌`) into garbage like `â€”` the moment it's opened in a viewer that
  guesses a legacy code page (many editors, markdown previews, mail/paste targets). Two guards, both
  automatic once you follow the steps: (1) **HTML** — `wrap_html.py` now runs every page through
  `scripts/asciify_html.py`, which encodes non-ASCII as numeric HTML entities (`&#8212;`) outside
  `<style>` and as CSS escapes (`\2014 `) inside it, so the emitted `.html` is pure ASCII and glyphs
  still render under any charset. A **hand/agent-authored** page (the Step 8 mockups) does NOT pass
  through `wrap_html.py`, so you must run `asciify_html.py` on it yourself (Step 8). (2) **Markdown** —
  `.md` has no entity mechanism, so write the markdown itself in ASCII: use `--` for em-dash, `|` or
  `-` for the `·` separator, `->`/`<->` for arrows, straight quotes, `...` for `…`, `(!)`/`[x]` for
  `⚠`/`❌`; put any genuinely non-ASCII *test data* (unicode strings you're testing) as codepoints
  (`U+03A9`) or a described value, not literal glyphs.

## Step 1 — Fetch the ticket (Atlassian MCP, read-only)

Read the story and everything that carries its real intent. **Expand the full issue tree**, not just
the one ticket — the AC that drives cases is spread across the epic, the subtasks, and the linked
issues:

```javascript
mcp__atlassian__getJiraIssue({ cloudId: "<cloud-id>", issueIdOrKey: "<KEY>" })
```

1. **Main issue** — summary, description, **acceptance criteria** (numbered/bulleted "done"
   statements — your primary source), issue type & priority, attachments, and the most recent
   comments (clarifications, agreed limits, copy).
2. **Epic** — find it via `parent.key` (when the parent is an Epic), the Epic Link custom field
   (commonly `customfield_10014`), or any field whose name contains "epic" holding a `KEY-123`
   value; fetch it for the problem framing and success metrics.
3. **Each subtask** — from the `subtasks[]` array, fetch every one individually (the parent's array
   omits their bodies) and pull its **summary, status, and its own AC** (sections beginning
   `Acceptance Criteria:` / `AC:` / `Definition of Done:` / `DoD:` / `Criteria:`). **Keep the list of
   subtask keys** — Step 6 reports coverage per subtask.
4. **Child stories (when the main issue is an Epic)** — an Epic's children are **not** in
   `subtasks[]`; they're separate issues that point *up* to the epic. Enumerate them and fetch each
   one, then recurse into **its** subtasks and linked issues too. Find children by any of: a JQL
   search `"Epic Link" = <KEY> OR parent = <KEY>` (via `mcp__atlassian__searchJiraIssuesUsingJql`),
   the epic's `issuelinks[]` rows typed `is parent of` / `is epic of`, or the child's own
   `parent.key` / Epic Link (`customfield_10014`) equalling the epic. Design and mock links usually
   live on a **child** story (e.g. a "Designs" story), not on the epic body — so this traversal is
   where most Figma links come from when you're handed an epic. Note each child's summary, status,
   and its own AC. **Keep the list of child-story keys** — Step 6 reports coverage per child too.
5. **Linked issues** — from `issuelinks[]`, capture key, **relationship type** (blocks / is blocked
   by / relates to / implements), summary, status; a story often `implements` a product issue that
   holds the real requirement and the design links — read it.

Jira descriptions are ADF — read the rendered text the MCP returns. If an individual fetch (epic,
a subtask, a child story, a linked issue) fails, note a warning and continue; only a failed **main**
issue aborts.

Collect every **`figma.com` URL** found anywhere in the tree — the main issue, its **subtasks**, its
**child stories** (and those children's subtasks/linked issues), comments, and linked issues — into a
single Figma-links list for Step 2, tagging each link with the issue key it came from. Do **not**
restrict the search to the parent/main issue: when the target is an epic, the design links are almost
always on a child. Collect image/PDF **attachments** the same way — if the MCP exposes them, view
them; a flow diagram or mock is design evidence the prose omits.

**If the description/AC is empty or vague, say so** — thin requirements mean more open questions,
not invented expected results.

> Ship.Cars note: this plugin is MCP-first for portability, but when a Jira token is available
> (`$JIRA_READ_TOKEN` or `<GROOMING_DIR>/jira-read.txt`) **prefer this skill's own dedicated
> reader** — it does the whole-tree traversal for you so you
> never have to guess whether children exist:
> ```bash
> python3 <REPO>/skills/write-test-cases/scripts/fetch_ticket.py <KEY>
> ```
> Unlike the breakdown-story reader, this one **enumerates an Epic's child stories via Epic Link /
> parent by default** (JQL `("Epic Link" = <KEY> OR parent = <KEY>)`), fetches each child with its
> own AC + subtasks + linked issues, auto-downloads image/PDF attachments, and folds **every**
> `figma.com` link from the entire tree — main issue, subtasks, **epic children**, and linked
> issues — into one `## Figma design links` section. A `0` from it is a *verified* zero (it ran the
> search), **never** an assumed one. **Do not conclude "no children / no designs" without running
> this (or the equivalent JQL via the Atlassian MCP) — the whole point of this reader is that the
> assumption is unnecessary.** The Atlassian MCP remains the portable default when the local Jira
> token is unavailable; if you must use the MCP on an Epic, run the
> child-story JQL yourself and re-scan those children for `figma.com` links.

## Step 2 — Review Figma designs (Figma MCP, always if any link exists)

For **every** Figma link from Step 1, open it and actually look — the design is where the states,
variants, and empty/error screens live, and those are exactly the conditions and edge cases the AC
under-specifies. A Figma link is an external URL the Jira token can't download; the MCP is the only
way to see it.

Extract `fileKey` and `nodeId` from the URL
(`figma.com/design/<fileKey>/<name>?node-id=<n1>-<n2>` → `nodeId` is `<n1>:<n2>`; a
`branch/<branchKey>` segment means use `branchKey` as the `fileKey`):

1. **`get_screenshot(fileKey, nodeId)`** — the primary tool; renders the frame as a PNG you can
   read. Works on a View seat and for design / FigJam / Slides. Bump `maxDimension` (e.g. 2048) to
   read fine copy. **The response reports `original_width`/`original_height` (the node's true canvas
   size) next to the rendered `width`/`height`. If the original is much larger than what you
   rendered, the copy you're reading is downscaled — trust it for layout, NOT for exact text/values;
   re-request higher, or (for a wide multi-panel frame) screenshot the sub-frames individually — see
   the next paragraph.**
2. **`get_metadata(fileKey[, nodeId])`** — design files only; cheap structural list of node ids /
   names / sizes. Omit `nodeId` (when the URL has none) to list top-level pages, then drill in.
   **Use it to enumerate every state/variant** — each is a test condition.

**Wide composite frames — screenshot each state sub-frame by its own node id; never read fine copy
off the zoomed-out whole.** A single "Accept Order" / "Order Details" frame is frequently a
6000–10000 px-wide board holding many desktop + mobile *state* panels side by side (default,
selected, error, the modal open, mobile mirror). At any `maxDimension` that fits the whole board,
each panel renders only a few hundred pixels — so section headers, radio-tier labels, checkbox copy,
button colour/enabled-state, and **dollar amounts** come out illegible or *plausibly-wrong* (you'll
"read" `CONFIRM RECEIVABLES` where it says `CONFIRM RECEIVING`, or miss that the entry point is a
toggle, not a button). Do **not** transcribe copy from that view. Instead:
`get_metadata(fileKey, <frame node>)` → read off the named child-frame node ids (each state panel and
the modal) → `get_screenshot` **each state's own node id** at `maxDimension` 1400+. Read every label,
control, and value from those per-state shots. This is the only reliable way to capture modal section
headers, exact tier labels, entry-point controls, and per-state `$` values — and it is mandatory
whenever `original_width` ≫ what a whole-frame shot can render legibly.

**Don't hand-parse the metadata — use the helper.** Save the `get_metadata` result to a file, then:
```bash
python3 <REPO>/skills/write-test-cases/scripts/figma_state_shots.py plan <metadata_file> \
        --filekey <fileKey> --frame <frame node> --out worklist.json
```
It flags the composite case, enumerates every state panel (desktop + mobile) in reading order, and
prints the exact `get_screenshot(nodeId=…, maxDimension=…)` worklist to run — so you can't eyeball the
node list and silently drop a panel. Run each shot, `curl` each PNG into a dir named after its node id
(`4535-27857.png`); then in Step 8, `figma_state_shots.py check worklist.json <shots_dir>` exits
non-zero and lists any planned state that has no screenshot yet.

For each frame, note: the happy-path UI, **every** empty/loading/error/disabled/validation state,
responsive variants, and any interactive rule (what enables a button, what a field rejects). Each
distinct state becomes one or more test cases; **any state the design shows but the AC never
describes the behavior for → an open question** (Step 5). If Figma is unreachable, list the link
and raise an open question rather than guessing.

## Step 3 — Discover real behavior in the repo(s) (fan out Explore sub-agents)

Requirements describe intent; the code describes what actually happens — including validation
limits, error paths, enum values, and boundary constants the AC never states. Fan out **read-only
`Explore` sub-agents (model `sonnet`), one per implementing repo, in a single message** (parallel).
Prompt template:

```
Repo: <repo>  (<path/to/repo>)
Jira story: <KEY> — <summary>
The acceptance criteria for THIS story:
<paste the AC / the slice relevant to this repo>

You are helping DESIGN TEST CASES — not fix or implement anything. Find the *testable behavior*.
1. Locate the code that implements (or will implement) this feature: entry points, controllers/
   resources/handlers, services, validators, models/DTOs, state machines, event producers/consumers,
   feature flags, config.
2. Report, as a structured list, the facts a tester needs:
   - Input fields and their VALIDATION rules (required/optional, type, min/max, length, regex,
     allowed enum values) with file:line.
   - Boundary constants and limits (page sizes, timeouts, retry counts, money/quantity caps).
   - Error paths and the exact error/status returned for each failure (file:line).
   - States and transitions (what status/lifecycle exists, which transitions are allowed/blocked).
   - Permission/role checks (who can do this, what's rejected).
   - Side effects: events published, endpoints called, DB writes — anything with observable outcome.
   - Behaviors present in code that the AC does NOT mention (surface these explicitly — they are
     candidate edge cases or open questions).
3. If the feature is NOT YET implemented, say so and report the nearest existing pattern (how
   similar features validate/error/transition) so cases can be written against the expected shape.
Do NOT propose a design or a fix. Just find and report observable, testable behavior with file:line.
```

Use the findings to (a) make expected results **precise** (real limits, real error messages),
(b) generate **negative and boundary** cases the AC omits, and (c) flag any code-implied behavior
the requirements don't confirm as an **open question**.

> Ship.Cars note: if `<CODEBASE_MAP_DIR>/repos/<repo>.md` shadow docs exist, tell each agent
> to read its shadow first (trust `seed`/`verified`; on `stub`/`stale` trust source). To find which
> repos a story touches, the fleet-wide token grep and keyword map documented in the
> `breakdown-story` skill's Step 2 work here too — but keep this skill's job to *test cases*, not a
> surface breakdown.

## Step 4 — Derive the test cases (this thread)

**Read `reference/test-design-techniques.md` first.** Then, before writing cases, **select the
techniques**: using the feature-type → technique matrix in that reference, detect **all** feature
types the story matches (a story usually matches several — a form + a workflow + a permission gate),
and **combine and deduplicate** the techniques from every matching row. Print the detected feature
types and the combined technique list so the coverage is auditable, then generate. The matrix pulls
in, beyond the core ISTQB set:

- **Equivalence partitioning / Boundary-value analysis** — one representative per input class; and
  min−1/min/min+1 … max−1/max/max+1, 0, empty, overflow for every range/limit found in the AC/code.
- **Decision tables** — condition combinations (flags/roles/states) → expected action; the `AND`/`OR`
  logic the prose only spells out for the happy path.
- **State-transition** — every valid transition once, plus the invalid ones (event in a state that
  shouldn't accept it).
- **Pairwise (combinatorial)** — when there are many independent options/toggles, cover every pair
  of values instead of the full cross-product.
- **CRUD coverage** — full create/read/update/delete lifecycle matrix × role, for any entity.
- **Auth & authorization matrix** — actor × resource → allow/deny, with an explicit expected error on
  every deny.
- **Accessibility (WCAG)** — keyboard, focus, screen-reader labels, contrast, announced errors, for UI.
- **Security vectors (OWASP)** — injection / XSS / IDOR / SSRF / unsafe-upload / data-exposure, only
  for the surfaces the feature actually exposes.
- **SFDPOT / Zero-One-Many** — for open-ended or thin requirements, and for every collection (zero /
  one / many + past-a-page).
- **Negative / error guessing** — wrong type, null/empty, oversized, malformed, duplicate submit,
  expired token, concurrent edit, dependency failure.

Every case cites the **one** technique that produced it. Organize cases by **feature / AC group**,
and make sure **every subtask's AC** (from Step 1) is represented.

**Write each case as a Given/When/Then scenario under a one-line metadata header — not a table row.**
The AC that drives these cases is already written in Given/When/Then, so the scenario body stays
faithful to the source; the metadata that makes this a test-*design* doc (technique, priority,
traceability, automation) lives in the header. Each case has:

| Field | Where it goes | Meaning |
|---|---|---|
| **ID** | header | `TC-<KEY>-NNN` (stable, sequential) |
| **Title** | header | one line — the behavior under test |
| **Type** | header | `positive` / `negative` / `boundary` / `edge` |
| **Priority** | header | `P1` (critical path / data-integrity / security), `P2` (important), `P3` (minor) |
| **Technique** | header | the one technique that produced it (EP / BVA / decision-table / state / negative / …) |
| **Source** | header | AC id / Figma node / `file:line` it traces to |
| **Automation** | header | `auto` (deterministic, API/UI-drivable) or `manual` (exploratory/visual) — a hint, not the code |
| **Given** | body | preconditions — state / data / role needed before the action (chain extra ones with **And**) |
| **When** | body | the action(s), with the concrete **test data** inline (the boundary value, the bad input, the role) |
| **Then** | body | the precise observable outcome, **citing the AC / design / `file:line`** it's from (chain extra assertions with **And**) |

The markdown shape for one case (see Step 6 for the full document):

```markdown
**TC-<KEY>-001** · <Title> — `positive` · `P1`
*Technique:* EP · *Source:* AC-1, Figma <node> · *Automation:* auto
- **Given** <precondition + role/state>
- **And** <extra precondition>
- **When** <action with concrete test data>
- **Then** <precise observable outcome — cite AC/design/`file:line`>
```

**Tabular techniques → `Scenario Outline` + `Examples`.** For BVA, decision-table, and pairwise
families, don't write one block per row — write a single case with placeholders and an Examples
table, so the whole matrix stays in one place:

```markdown
**TC-<KEY>-012** · Fee applied per tier — `boundary` · `P1`
*Technique:* BVA · *Source:* Figma <node> · *Automation:* auto
- **When** I select the `<term>` tier on a $1,180.00 carrier pay
- **Then** the resulting carrier pay is `<pay>`

| term | pay |
|---|---|
| 7 business days | $1,168.20 |
| 3 business days | $1,156.40 |
| 2 business days | $1,132.00 |
```

**The `Then` guardrail #1 — derivable, never fabricated (this is the whole point of the skill).**
A `Then` asserts a definite outcome — so it must be *derivable* from the AC, the design, or the
code. **Never write a `Then` that fabricates an undetermined outcome.** If the correct result can't
be extrapolated, the case does not get a confident `Then`: it becomes an **open question** (Step 5),
or — at most — its `Then` is written explicitly as the *proposed default (assumption)* and tagged
with the open-question it depends on (e.g. `Then … *(proposed default — see open question 4)*`).
This keeps Given/When/Then from quietly turning "we don't know yet" into a false assertion.

**The `Then` guardrail #2 — atomic and assertable, never a noun-phrase list.** Every `Then` (and
each chained `And`) must state **one** observable outcome that a person or a script can mark
pass/fail without judgement. It names **what** is expected (the exact value / text / status / state
/ emitted event) and **where** it's observed (the field, element, API response, event, DB row) —
tool-agnostic, not a selector syntax. Concretely:

- **One assertion per line.** If you're tempted to write "the term, the method, the cue and the
  tooltip are shown", that is *four* outcomes → split into four `Then`/`And` lines. A comma-separated
  list of UI nouns is the tell-tale of a useless `Then`.
- **Ban vague predicates.** "shown", "displayed correctly", "works", "handled", "as expected",
  "properly", "reflects the change" — each hides the actual check. Replace with the concrete value
  and target: *not* "Then payment terms shown" but "Then the payment-term field reads
  `15 business days`" (cite `OfferPaymentTerms.tsx:52`). Prefer a real expected string/number/status
  from Step 3 grounding over a paraphrase.
- **Negative outcomes are assertions too.** "informational only" → "Then no control to elect a tier
  is present"; "rejected" → "Then the request returns `403` and the order is unchanged".
- **If you can't make it concrete, that's a signal, not a license to be vague** — the missing value
  is an open question (guardrail #1); write the specific `Then` you *would* assert and tag it with
  the OQ, so the unknown is visible instead of buried under "…is shown".

**The `Then` guardrail #3 — clause hygiene (keep each clause in its lane, self-contained,
deliberately authored).** These are the rules that make a scenario runnable, not just readable:

- **Role separation — the commonest mistake.** `Given` = preconditions only (state, the actor's
  role, the data fixture, feature-flag); `When` = the single action under test in the actor's voice
  ("the carrier selects the 2-day tier"), carrying only the **actual input values**; `Then` = the
  observed outcome. Do **not** smuggle a precondition into `When` as "test data" — *a COD load*,
  *not eligible*, *eligible load card* are Givens, not inputs. Do **not** put an observation step
  (*inspect the revision*, *open the invoice*, *check the events*) in `When` — the observation is
  implied by the `Then`; the `When` is only the action that triggers the outcome.
- **One action per `When`, one assertion per `Then`** — chain the rest with `And` (this restates
  guardrail #2 for the `When` side too).
- **Self-contained — no back-references.** Never write "Given as above / as before". Either restate
  the precondition, or hoist the preconditions shared by a feature group into a single
  `Background:` block at the top of that group so **every scenario runs in isolation**.
- **Author each clause deliberately — never mechanically chop a prose sentence into clauses.**
  Splitting an expected-result string on commas / semicolons / `&` yields fragments like
  `Then …faster term &` → `And $1156.40`, or `Then No cue` → `And standard term still shown` — each
  reads as nonsense and asserts nothing. Write every `Given/When/Then/And` as one complete,
  standalone clause. If you **script** the markdown/HTML emission (Step 7), the clause *text* must
  already be atomic — the script only formats it; it must not split prose into clauses.

**The `Then` guardrail #4 — Gherkin structural integrity.** Each scenario is a *well-formed*
Given/When/Then, not a loose pile of clauses. When you script emission, the keyword-assignment logic
must guarantee all of this — then **re-parse the output to confirm** (a scenario starting with `And`
is the classic sign it's broken):

- **Start with `Given`** (the scenario's own preconditions), or with `When` when every precondition
  already lives in the group `Background`. A scenario must **never start with `And`.**
- **Order is strictly `Given` → `When` → `Then`.** No `Given` after a `When`/`Then`; no `When` after
  a `Then`.
- **`And` only continues the immediately preceding keyword** (Given-And, When-And, or Then-And). It
  never opens a scenario and never introduces a new section.
- **Every scenario has ≥1 `When` and ≥1 `Then`** (a `Scenario Outline` uses `When`/`Then` +
  `Examples`). A "given/when" with no `Then` asserts nothing; a lone `Given` is not a test.
- **`Background` is a separate block, not part of any scenario.** It holds only the preconditions
  shared by *every* scenario in the group; a scenario's own extra preconditions still begin with
  `Given` — they do **not** chain the Background with `And` across the block boundary.

## Step 5 — Edge cases and open questions (the required extras)

Two mandatory passes on top of the AC-derived cases:

**Edge-case pass.** Walk the edge-case checklist in `reference/test-design-techniques.md`
(empty/zero, boundaries, large/many, nulls, type/format, time/timezone, concurrency, auth/permissions,
lifecycle, failure/recovery, money, i18n/a11y, data integrity). Every item that applies **and whose
correct behavior IS derivable** becomes a test case of type `edge`. Aim to cover the failure and
boundary space the AC glosses over — this is a core deliverable, not an afterthought.

**Open-questions pass.** Any scenario you can construct but whose **correct expected result cannot
be extrapolated** from the AC, the Figma designs, *or* the repo code is an **open question** — never
a guessed expected result buried in a case. For each, record:
- the **scenario** (what a tester would do),
- **why it's undetermined** — which source is silent (AC doesn't say / design has no such state /
  code doesn't guard it),
- **where it would sit** in the suite (which feature group),
- a **proposed default**, clearly marked as an assumption, for a human to confirm or correct,
- **evidence** (`file:line`) when the code *implies* a behavior the requirements don't state —
  then ask whether that implied behavior is intended.

Typical open questions: an error/empty state the design never shows; an unquantified limit
("large files", "reasonable length"); an undefined decision-table combination; an unguarded
concurrency/ordering outcome; a role the story doesn't say whether to allow; a dependency-failure
path with no specified UX; referenced-but-missing copy/thresholds. **A thin or ambiguous ticket
should produce more open questions — that is the correct, honest output**, not fabricated coverage.

## Step 6 — Emit the markdown TDD

Write `<TDD_DIR>/<KEY>.md` (create the `<TDD_DIR>/` folder if needed; default is `<TDD_DIR>/` in the current
working directory, or the output dir passed as the second argument). Use this shape:

```markdown
---
ticket: <KEY>
summary: "<exact summary>"
type: <Story | Bug | Task>
sources:
  jira: <KEY>
  epic: <EPIC-KEY | none>
  subtasks: [<KEY>, ...]                      # or "none"
  linked: [<KEY (relationship)>, ...]         # or "none"
  figma: [<frame/node reviewed>, ...]         # or "none"
  repos: [<repo>, ...]                        # what the Explore agents read
authored-on: <YYYY-MM-DD>
authored-by: Claude Code — write-test-cases skill (human review pending)
counts: { cases: N, edge: N, open_questions: N, ac_covered: "n/total", subtasks_covered: "n/total" }
---

# <KEY> — Test Design Document

## Summary
> <verbatim story summary + AC, from the ticket>
One-paragraph statement of what is being tested and what the sources were (Jira / Figma frames /
repos read).

## Coverage at a glance
- Total test cases: N   (P1: n · P2: n · P3: n)
- By type: positive n · negative n · boundary n · edge n
- Automation candidates: n auto · n manual
- Techniques applied: <combined, deduplicated list from Step 4>
- AC coverage: n/total acceptance criteria covered   (uncovered → open question / gap)
- Subtask coverage: n/total subtasks have ≥1 case   (list any uncovered subtask key)
- Open questions: N   ← blocks a fully-specified suite until answered

## Test cases
### <Feature / AC group 1>
**Background** (preconditions shared by every scenario in this group — so each case stays
self-contained without "as above"):
- **Given** <shared precondition, e.g. a load on payment method X with the feature enabled>

**TC-<KEY>-001** · <Title> — `positive` · `P1`
*Technique:* EP · *Source:* AC-1, Figma <node> · *Automation:* auto
- **Given** <precondition + role/state>
- **And** <extra precondition>
- **When** <action with concrete test data>
- **Then** <precise observable outcome — cite AC/design/`file:line`>

**TC-<KEY>-002** · <Title> — `boundary` · `P1`
*Technique:* BVA · *Source:* Figma <node> · *Automation:* auto
- **When** I <action> with `<param>`
- **Then** the result is `<expected>`

| param | expected |
|---|---|
| <value 1> | <result 1> |
| <value 2> | <result 2> |

### <Feature / AC group 2>
<more Given/When/Then cases …>

## Edge cases
<Type-`edge` cases, same Given/When/Then block format (header + Given/When/Then). These cover
boundaries/failure/concurrency/etc. whose correct behavior IS derivable. Group them here or fold
them into the feature groups — but they must be clearly identifiable as `edge`. Any edge scenario
whose outcome is *not* derivable is an open question instead, or carries a `Then … *(proposed
default — see open question N)*`.>

## Open questions
<Numbered. Each: scenario · why undetermined (which source is silent) · where it sits · proposed
default (assumption) · evidence file:line if code-implied. These are the behaviors that cannot be
extrapolated from the requirements.>
1. **<scenario>** — Undetermined because <source> is silent. Would sit under <group>. Proposed
   default (assumption): <...>. Evidence: `<file:line>` implies <...> — intended?

## Traceability
| Source (AC id / subtask key / Figma node / behavior) | Covered by | Gap? |
|---|---|---|
| AC-1 | TC-…-001, TC-…-002 | — |
| AC-3 | — | ❌ no case — see open question 2 |
| SUBTASK LITE-1234 | TC-…-004, TC-…-005 | — |
| SUBTASK LITE-1236 | — | ❌ uncovered subtask |
<Every AC bullet, every subtask, and every design state maps to ≥1 case, or is listed as a
gap/open question. The subtask rows are what back the "Subtask coverage: n/total" metric above.>
```

**Completeness check before writing:** every TDD emits, in order — `## Summary` →
`## Coverage at a glance` → `## Test cases` → `## Edge cases` → `## Open questions` →
`## Traceability`. The **Edge cases** and **Open questions** sections are mandatory on every run,
even if one says "none — all boundary behavior is specified" / "none — no undetermined behavior"
with the reason. Never silently drop a section.

**Write the markdown in ASCII** (the `.md` has no HTML-entity fallback, so a UTF-8 typographic
character becomes `â€”`-style mojibake in a viewer that guesses a legacy code page). Use `--` for the
em-dash, `|` or `-` for the `·` separator between header fields, `->`/`<->`/`<-` for arrows, straight
`"`/`'` quotes, `...` for `…`, `(!)`/`[x]` for `⚠`/`❌`, and `>=`/`<=` for `≥`/`≤`. Put genuinely
non-ASCII **test data** (unicode strings under test) as codepoints (`U+03A9`) or a described value,
not literal glyphs. (The HTML companion in Step 7 is auto-ASCII'd by `wrap_html.py`; this rule is
about the markdown you author by hand.)

Then present the counts (cases / edge / open questions) in chat. **If the story involves UI
interaction, the run is not complete until Step 8 has also emitted `<TDD_DIR>/<KEY>-mockups.html`** — treat
it as a required output alongside the md/html, not a follow-up the user must request. **Stop at test
cases** — do not design the implementation, do not create Jira issues, do not write test code (the
mockups are illustrative scenario visualizations, not shippable UI code).

## Step 7 — Emit the HTML companion

Write `<TDD_DIR>/<KEY>.html` — self-contained and CSP-safe (no external assets). Don't re-type CSS or
hand-roll `<head>`; author only the **body fragment** + a small **meta.json**, then staple with
`wrap_html.py`:

```bash
# author body.html (the sections below, mirroring the markdown) and meta.json in a scratch dir, then:
python3 <REPO>/skills/write-test-cases/scripts/wrap_html.py /tmp/body.html /tmp/meta.json > <TDD_DIR>/<KEY>.html
```

`wrap_html.py` emits **pure-ASCII HTML** (it forces UTF-8 on stdout and runs the whole page through
`asciify_html.py` — non-ASCII becomes numeric entities outside `<style>`, CSS escapes inside), so
this file can't mojibake in a charset-guessing viewer. You don't do anything extra here; just don't
hand-edit the wrapped `.html` afterward with raw typographic characters.

The body fragment mirrors the markdown, rendered richer:

- A **`## Coverage at a glance`** stat row using `<div class="stats">` with `<div class="stat"><div
  class="n">N</div><div class="l">label</div></div>` tiles — total, P1, edge, **AC covered (n/total)**,
  **subtasks covered (n/total)**, and open questions. Below the tiles, a one-line
  `Techniques applied: …` note.
- The **test cases** as Given/When/Then **blocks** (not tables) — the skeleton ships these styled,
  **do not add CSS**. One case is:
  ```html
  <div class="tc">
    <div class="tc-h">
      <span class="id">TC-<KEY>-001</span>
      <span class="ttl">Title</span>
      <span class="pill pos">positive</span><span class="pill p1">P1</span><span class="pill auto">auto</span>
    </div>
    <div class="tc-meta">Technique: EP · Source: AC-1, Figma &lt;node&gt;</div>
    <ul class="gwt">
      <li><span class="kw g">Given</span><span>a precondition + role/state</span></li>
      <li><span class="kw and">And</span><span>an extra precondition</span></li>
      <li><span class="kw w">When</span><span>the action with concrete test data</span></li>
      <li><span class="kw t">Then</span><span>the observable outcome (cite AC/design/<code>file:line</code>)</span></li>
    </ul>
  </div>
  ```
  Pill classes: `pos|neg|bound|edge` (type), `p1|p2|p3` (priority), `auto|manual`. Keyword classes:
  `kw g` (Given), `kw w` (When), `kw t` (Then), `kw and` (And). For **Scenario Outline** cases put
  the `Examples` table inside the block wrapped in `<div class="tbl-scroll examples"> … </div>`.
  There are usually dozens of cases — **generate the blocks with a small script** (hold the case
  data in a list and emit the HTML) rather than hand-typing each block.
- The **Open questions** as `<div class="oq">` callouts: `<span class="q">the scenario</span>` then
  a `<span class="why">why it's undetermined + proposed default</span>`. These are the visual
  centerpiece — a reviewer should spot the unknowns immediately.
- The **Traceability** table (gaps flagged with `<span class="pill neg">❌ gap</span>`).
- Optionally one inline `<svg>` state-transition or flow diagram in a
  `<div class="fig"><div class="fig-scroll"><svg …>…</svg></div><div class="cap"><b>Figure 1.</b>
  …</div></div>` when a lifecycle is central to the tests.

`meta.json` keys: `title`, `h1`, `subtitle` (one-liner: summary · type · N cases · N open
questions), `chips` (list of `{text, cls}` — `cls` ∈ `""` blue / `qa` teal / `edge` amber /
`oq` red / `surf` green; include `{"text":"N test cases","cls":"qa"}`,
`{"text":"N edge cases","cls":"edge"}`, `{"text":"N open questions","cls":"oq"}`), and `footer`
(HTML — cite the sources: Jira key, Figma frames, repos read). See the header of `wrap_html.py`
for the exact shape.

## Step 8 — Per-step scenario mockups (required whenever the story involves UI interaction)

**This is a standard part of the TDD, not an opt-in extra.** Whenever the feature has a
**user-visible UI** — a screen, form, list, modal, cue, or state (i.e. Step 2 reviewed any Figma
frame, or Step 4 detected a UI feature type) — you **must** also emit `<TDD_DIR>/<KEY>-mockups.html` as
part of the run. **Skip it only** when the story is purely non-UI (backend / API / config / data
pipeline / analytics with no user-visible surface); **if in doubt, generate it.** The user should get
the mockups automatically for any UI-facing story without having to ask.

It renders, per UI-facing scenario, a small synthetic UI for **each Given/When/Then state** (default
→ input → validation → result), as one self-contained `<TDD_DIR>/<KEY>-mockups.html` (HTML/CSS, inline
only, CSP-safe). It **re-draws** the state — it does *not* paste the Figma image (that's Step 7's
preview job, a different thing).

**Scope within a UI-facing story.** Only mockup the scenarios with a **user-visible UI**; the
backend / config-API / analytics scenarios of the same story still get no mockup. Build a mockup for
a scenario **only where a reviewed Figma frame — or, absent a frame, explicit AC + a repo component —
grounds it.** If neither exists, do **not** invent a mockup: list the scenario under a "no design
reference" note (same honesty as an open question).

**Drive the mockup from three reconciled sources — the scenarios, the requirement, the design.** A
mockup re-drawn from the frame alone is a redundant screenshot; its value is that it makes the
*tests* visible. Build each state from all three, and the mockup becomes a **three-way consistency
check on tests ↔ requirement ↔ design**:

- **The scenarios (Step 4) are the spec for what to render.** Each `When` is a state to draw; each
  `Then`/`And` is a concrete assertion that state must make **literally visible** — the disabled
  `ACCEPT ORDER`, the `$1,132.00`, the ticked confirm box, the absent control, the exact error copy.
  If a `Then` isn't visible in the rendered state, the mockup is wrong (or the `Then` is vague — fix
  it per guardrail #2).
  - **Every mockup card carries its OWN full `Given / When / Then` caption — never a single keyword
    pill.** A card is one scenario (or one step of one): three text lines — the `Given` precondition,
    the `When` action, the `Then` outcome. **Do not label a whole card with one keyword** — that is
    the wall-of-`Then` bug (a card "at rest" is still a full G/W/T; a "tooltip opened" card's `When`
    is *open the tooltip*). The pass/fail assertions go in a separate `Checks` list.
  - **Draw an image for EACH clause that has an applicable, *distinct* visual — a scenario is a
    before → action → after, not one picture with a caption.** This is the core rule; getting it
    wrong (rendering only the outcome and demoting Given/When to text) is a recurring defect. Per
    clause:
    **RESTRICTED FORMAT — mandatory.** Render one frame for **every** `Given`/`When`/`Then` clause that
    has any applicable visual. The default is the full **three panels: base → act → result** —
    `Given` | `When` | `Then` side by side — and you do **not** collapse them to fewer. The *only* clause
    that stays a text line (no frame) is one with genuinely **no** visual: a role (`dispatcher`), a
    status (`new`/`delivered`), a feature flag, a server precondition, or a backend-only event.
    - **`Given` → ALWAYS render the *base* screen at rest** (no highlight) whenever the precondition is
      an actual screen (the payment card with the toggle OFF; a COD load card; the modal already open) —
      **including for a display scenario**, so the before-state is visible. Only a **non-visual**
      precondition (a role/status/flag) stays text-only; never invent a frame for a role.
    - **`When` → ALWAYS render it as its OWN frame: the same base screen with the acted-on control
      highlighted** (the toggle mid-press, the tier radio being chosen, the confirm box being ticked,
      the field focused, the button being pressed). This middle panel is what makes the interaction
      legible — **do NOT reduce a visible action to a bare arrow**; the reader must see *which* control
      drives the transition. Make the highlight unmistakable (press state, focus ring, or a callout at
      the exact control). Drop the `When` frame **only** when the action is genuinely non-visual (a
      backend event, a role check, a config change) — then it stays a text line.
    - **`Then` → ALWAYS render the *after* state** (the resulting screen).
    - **Do NOT collapse to a single frame.** A **display / same-screen** scenario (view a card → a cue
      is shown) still renders a `Given` base frame **and** a `Then` frame (before → after) — draw the
      before-state (e.g. the card/list without the asserted element, or an ineligible variant) and the
      after/asserted state as two frames. The **only** narrow exception: when a clause's frame would be
      *pixel-identical* to the frame immediately beside it (a pure same-screen read, or a flow's shared
      state already drawn on the neighbouring card), reference that frame instead of drawing a
      byte-for-byte duplicate — that is never a licence to drop a *distinct* before-state or a *visible*
      action.
  - **In a multi-step flow, never redraw a screen a neighbouring card already shows.** Each step's
    `Given` *is* the previous step's `Then`; drawing the base frame on every card would render the same
    modal four times. Rule: *a frame is drawn when it is **distinct from what the row already
    shows***. So a flow is a `.row` of step-cards with `→` `.flowarrow`s between them; a mid-flow card
    typically shows its **`When`** (the current screen with the action highlighted) and its **`Then`**
    (the result), with its `Given` being the prior card's `Then` (not redrawn). A **standalone**
    (non-flow) scenario renders its own full **base → act → result** because no neighbour supplies the
    base.

  Card shape — a standalone interactive scenario renders all three panels (define the CSS inline;
  class names are illustrative):
  ```html
  <div class="state">
    <div class="st-h"><span class="tcids">TC-…-NNN</span><span class="nodeid">&lt;figma node&gt;</span></div>
    <div class="gwt">
      <div class="ln"><span class="k g">Given</span><span>the precondition</span></div>
      <div class="ln"><span class="k w">When</span><span>the action the user takes</span></div>
      <div class="ln"><span class="k t">Then</span><span>the observed outcome</span></div>
    </div>
    <div class="frames">                              <!-- base → act → result -->
      <div class="frame"><span class="fl g">Given</span> … base screen at rest (toggle OFF) … </div>
      <div class="flowarrow">→</div>
      <div class="frame"><span class="fl w">When</span> … SAME screen, the toggle highlighted mid-press … </div>
      <div class="flowarrow">→</div>
      <div class="frame"><span class="fl t">Then</span> … after-state (modal open) … </div>
    </div>
    <div class="checks"><span class="hd">CHECKS</span><ul><li>concrete assertion (TC-…)</li></ul></div>
  </div>
  ```
  - **Display / same-screen scenario** → render a `Given` base frame (the neutral/before state — e.g.
    the card without the cue, or an ineligible variant) **and** a `Then` frame (the asserted state);
    do **not** reduce it to a single `Then`.
  - **Non-visual Given/When** (role/status/flag/backend event) → drop only that clause's frame; keep it
    as a text line in the caption. Every *visual* clause still gets its own frame.
  - **Flow** → the shared state is drawn once in the neighbouring card; a mid-flow card shows its
    `When`(highlighted)→`Then`, `→` between cards; don't re-draw the prior state.
  - **Platform variants** (desktop vs ePOD) sit **side by side without a `→`** — the arrow denotes a
    transition (before → after), not "here is another variant".
  The `.gwt .k.g/.k.w/.k.t` caption pills and the `.fl g/.fl w/.fl t` frame labels reuse the
  Given/When/Then colours. **There is no single-keyword header pill** — the G/W/T lives in the `.gwt`
  caption; do not reintroduce a lone-keyword header (that scheme is what the wall-of-`Then` came from).

  The quick test: **if you can name the user action that produced the state, it's a `When`; if the
  state is just something rendered to be read, it's a `Then`.** **A state's caption and its
  Asserts must claim only what the state actually renders.** If the design omits an element the AC
  requires (e.g. a payment-method label the frame drops), render it as a **flagged gap** in the
  mockup — never list it in the caption as "shown" while the assert underneath says it's missing;
  that contradiction (caption says shown / state omits / assert flags missing) is the exact
  three-way conflict the mockup exists to surface, so make it visible, don't paper over it.
- **The requirement / AC (Step 1 + linked PRD) supplies intent** — the *why* behind each state — so
  you render intended behavior and know which states matter (default vs. validation vs. error vs.
  empty), not just whatever the frame happens to show.
- **The design (Figma) supplies layout, copy, and the full set of states/variants** (the fidelity
  rules below).

Reconcile them: where the scenario's `Then`, the AC, and the frame **agree**, render that; where they
**disagree**, the disagreement is a finding — mirror the design, tag the open question, and confirm
that conflict is also captured as an OQ in Step 5. (A `Then` asserting reduced *Carrier Pay* while the
frame reduces *Receivables* is OQ-5 surfacing in three places at once — the mockup should catch it,
not hide it.) **Coverage:** every UI-facing scenario's `Then` is represented by ≥1 mockup state, and
every state is captioned with the scenario id(s) it visualizes; a state the design shows but no
scenario covers is a **missing test** — loop back to Step 4/5, don't just draw it.

> **Author the mockups with a dedicated, intent-aware sub-agent — do not procedurally slot-fill and
> do not patch them incrementally.** A template that fills caption/label/value slots (or a human
> hand-editing one state at a time) drifts into incoherence: a caption that claims an element the
> state omits, a display group with no `Then`, a scenario that starts with `And`. Give **one**
> sub-agent the whole picture at once — the exact Given/When/Then blocks, the AC/PRD intent, and the
> reviewed frames (open them **at their per-state node ids per Step 2, not a zoomed-out composite;
> transcribe every label and value freshly from the re-opened frame, never from memory or an
> earlier `design-notes`/extraction file**) — and have it *reason* about each state, then
> **self-verify** before finishing. Every state must pass all of:
> 1. **Caption ↔ state ↔ Asserts agree** — the caption claims *only* elements actually rendered; the
>    Asserts match what's on screen; nothing is claimed that the state omits.
> 2. **Every UI scenario's `Then` is rendered**, or listed with a reason if not statically renderable
>    (a11y interaction, failure injection, pairwise matrix, ePOD mirror, cross-repo check).
> 3. **Design/AC conflicts appear as flagged gaps** on the state (e.g. an AC-required label the frame
>    omits → a visible "missing (AC ...)" placeholder), never smoothed over or silently claimed.
> 4. **Full G/W/T caption + per-clause panels (RESTRICTED FORMAT — mandatory).** (a) Every card carries
>    all three `Given/When/Then` text lines — never a lone keyword header (two+ cards headed by the
>    *same* single keyword is the wall-of-`Then` bug). (b) **Every clause that has any visual is rendered
>    as its own frame** — an interactive scenario shows **three** panels (`Given` base → `When` the same
>    screen with the acted-on control highlighted → `Then` the result), and a **display / same-screen**
>    scenario still shows a `Given` base frame **and** a `Then` frame (before → after) — it is **not**
>    collapsed to one. A **visible action rendered as only an arrow (no `When` frame) is a defect**, and
>    a display scenario reduced to a single frame is a defect. The **only** clauses without a frame are
>    genuinely non-visual ones (role/status/flag/backend event → text line); the **only** frame not drawn
>    is one *pixel-identical* to the neighbour already showing it (flow's shared state / pure same-screen
>    read) — reference it, never drop a distinct before-state or a visible action. Platform variants
>    (desktop/ePOD) sit side by side **without** a `→`.
> 5. **Every state is diffed against a freshly re-opened frame — its OWN per-state node, not a
>    composite, not notes.** Re-`get_screenshot` the state's source node and compare *verbatim*:
>    section headers, exact option/tier labels, checkbox copy, the **entry-point control** (a
>    lookalike `REQUEST NEW` button vs a `Faster Pay` toggle are different controls), each button's
>    **colour and enabled/disabled state**, and **every `$` value character-for-character**. A number
>    the mockup computes must equal the number the frame literally prints; if it doesn't, that is a
>    design inconsistency to **mirror-and-flag** (Fidelity rules below), never to silently recompute.
>
> The sub-agent reports its verification results **as an explicit per-state diff table** (state → node
> id checked → substantive diffs → cosmetic diffs); if any state has an unfixed substantive diff it
> fixes and re-diffs. Re-checking against your own earlier notes instead of a re-opened frame is not
> verification — it re-confirms the same mistake. **If this sub-agent dies mid-run and the work is
> taken over (by the main thread or a fresh agent), the takeover STILL performs this full
> re-open-and-diff per state — it does not shortcut from the dead run's notes or the Step-2
> extraction. Drawing mockup copy from previously-extracted text instead of a re-opened per-state
> frame is the single most common way these mockups silently go wrong.**

**Fidelity rules — the mockup must not drift from the design.** The whole value is that it mirrors
what will ship, so any difference from the frame is a defect unless it's a deliberate simplification
of surrounding chrome. Before drawing a state, re-open **that state's own node** (its per-state
sub-frame per Step 2 — a `get_screenshot` at `maxDimension` 1400+, not the composite) and
`get_metadata` to enumerate its text nodes. Transcribe from that shot **now**; do not draw from
memory or an earlier extraction. Then:

- **Copy verbatim.** Labels, button text, tooltip lines, empty-state text, section headers come
  **exactly** from the re-opened frame (`CONFIRM RECEIVING`, `I confirm that I will receive $X`, the
  location-sharing line) — never paraphrase or substitute a synonym (`Enable Faster Payment` ≠
  `REQUEST NEW`; `CONFIRM RECEIVING` ≠ `CONFIRM RECEIVABLES`). Copy read off a downscaled composite is
  a guess, not a transcription.
- **Draw the control the scenario is about — not a lookalike.** A single frame often holds several
  similar-looking controls (a driver-location `REQUEST NEW` button *and* a payment `Faster Pay`
  toggle; an enabled green CTA on one surface and a white/disabled CTA on another). Confirm which
  control the *scenario's* `When`/`Then` references and draw that one, with its real shape (button vs
  toggle vs link), colour, and enabled/disabled state — at the node where it actually lives.
- **Show only what the frame shows; hide what it hides.** Do not add data the design omits (e.g.
  per-tier dollar amounts in a tooltip the design lists as `N days – X%` only), especially where the
  AC/PRD or an open question says to hide it. Cross-check every value against the "don't show"
  constraints and OQs from Steps 2/5.
- **Render the full set of options/states — never abbreviate.** Four radio tiers in the frame → draw
  four; disabled→enabled Save → draw both. Dropping options "for space" changes the meaning.
- **Mirror the design's data model, not the prose.** Change the exact fields the frame changes and
  leave the rest untouched — if the frame reduces *Receivables* and leaves *Carrier Pay* unchanged, do
  that; do **not** strike through Carrier Pay because a PRD sentence says `total = original − fee`.
  Where the design conflicts with the AC/code, **mirror the design and tag the conflict with its
  open-question** (`— see OQ-n`); never silently pick a side.
- **Don't invent visual treatments** the frame doesn't use (strikethroughs, toggles, badges, centered
  empty-state blocks). If the frame's "unavailable" state is just the normal card without the action,
  draw that.
- **Cover the variants the frame includes** — desktop *and* ePOD/mobile if the design has both (or
  state which you rendered and why).
- **Flag the design's own defects, don't smooth them over.** If the frame is internally inconsistent
  (one sub-frame confirms `$1,156.40`, another shows `$1,132.00`), render one and **note the
  inconsistency for design** — do not quietly harmonize it.

**Verify before finishing — re-fetch, don't recall.** For each state, re-`get_screenshot` its **own
source node** (the per-state sub-frame, `maxDimension` 1400+ — never a downscaled composite, never
your notes) and diff the drawn state against it side by side: section headers, the full option list,
checkbox copy, the **entry-point control's shape** (button vs toggle vs link), each button's
**colour and enabled/disabled state**, and **every number/`$` character-for-character**. Classify
each remaining difference as **substantive** (a value/label/control/enabled-state a tester would
check) or **cosmetic** (chrome/spacing/theme). Fix all substantive ones; keep the cosmetic list in
the mockup file's footer so the simplifications are explicit. Emit the diff as an explicit per-state
table (state → node id checked → substantive → cosmetic) in your working notes. Confirm you actually
shot every state first: `python3 <REPO>/skills/write-test-cases/scripts/figma_state_shots.py check
worklist.json <shots_dir>` must exit 0 (no planned state panel left un-screenshot) before you trust
the diff. **Verifying against
your own earlier notes/extraction instead of a re-opened frame is not verification — it re-confirms
the same mistake.** A mockup that silently diverges on a value, a label, or an entry-point control is
worse than none.

**ASCII-safe the mockups file before finishing.** Unlike the Step 7 companion, the mockups page is
authored by hand (or by a sub-agent), so it does **not** pass through `wrap_html.py` and will contain
raw UTF-8 glyphs (arrows, checks, warning signs, em-dashes) that mojibake in a charset-guessing
viewer. Run the sanitizer on it as the last step:
```bash
python3 <REPO>/skills/write-test-cases/scripts/asciify_html.py <TDD_DIR>/<KEY>-mockups.html
```
It rewrites in place — non-ASCII becomes numeric HTML entities outside `<style>` and CSS escapes
(`\2714 `) inside it, so decorative `content:"✔"` pseudo-element glyphs keep working. Confirm it's
clean: the file should contain no bytes > 127 afterward.

## Gotchas

- **Stay scoped to test cases.** The temptation is to slide into "and here's how to build it" —
  don't. No implementation design, no DoR, no Jira writes, no test *code*. Case specs only.
- **Encoding — don't ship mojibake.** Raw UTF-8 typographic characters (`—` `·` `→` `↔` `“ ”` `⚠`
  `❌`) show as `â€”`-style garbage in any viewer that mis-guesses the charset. The `.html` from
  `wrap_html.py` is auto-ASCII'd; the **hand-authored mockups page is not** — run
  `scripts/asciify_html.py <TDD_DIR>/<KEY>-mockups.html` before finishing. Write the **markdown** in ASCII
  (`--`, `|`, `->`, straight quotes, `...`, `(!)`), and encode non-ASCII test data as codepoints
  (`U+03A9`). A file with any byte > 127 is a latent mojibake bug.
- **Never guess an expected result to avoid an open question.** If the AC, the design, and the code
  are all silent, the honest output is an open question with a clearly-labelled proposed default —
  not a case that asserts an outcome nobody defined. Fabricated expected results are the main
  failure mode of auto-generated tests.
- **No vague `Then`s.** A `Then` like "term, SmartHaul, cue + tooltip shown" is not a test — it's a
  list of nouns with no pass/fail. Every `Then`/`And` asserts exactly one observable outcome with a
  concrete expected value and where it's observed (guardrail #2 in Step 4). Split compound "X, Y, Z
  are shown" into one line each; ban "shown / works / handled / as expected"; if the concrete value
  isn't derivable, tag the line with its open question rather than paraphrasing.
- **Keep clauses in their lane and self-contained (guardrail #3).** Preconditions → `Given` (never a
  precondition disguised as `When`'s "test data"); the single triggering action → `When` (never an
  "inspect / open / check" observation step); the outcome → `Then`. No "Given as above" — hoist
  shared preconditions into a `Background:` per feature group. And never mechanically split a prose
  expected-result on `,`/`;`/`&` — that yields garbage fragments like `Then …faster term &` /
  `And $1156.40`. Author each clause whole.
- **Scenarios that don't parse as Gherkin (guardrail #4).** Starting a scenario with `And`, a `Given`
  after a `When`/`Then`, or a scenario with no `Then` all break structural integrity — and are exactly
  what a scripted generator produces if it chains the `Background` into each scenario with `And`.
  Start every scenario with `Given` (or `When` when the `Background` covers setup), keep
  `Given`→`When`→`Then` order, give each a `When` and a `Then`, and **re-parse the emitted file** to
  confirm none start with `And`.
- **Mockups (Step 8) mirror the design, not your mental model.** The failure mode is re-drawing what
  you *think* the behavior is instead of what the frame shows: paraphrasing button copy, adding values
  the design hides (tooltip $ amounts), abbreviating option lists, or inventing visual treatments
  (striking through Carrier Pay when the frame reduces Receivables). Re-read the frame, copy labels
  verbatim, show only what it shows, render every option/state, and where design conflicts with
  AC/code mirror the design and tag the OQ. Only mockup where a frame (or AC + component) grounds it;
  verify each state against its frame before finishing.
- **The composite-frame trap — the most common silent failure.** Wide "Accept Order"/"Order Details"
  frames pack many state panels into one 6000–10000 px board; a whole-frame screenshot renders each
  panel too small to read, so you "transcribe" `CONFIRM RECEIVABLES` (it says `CONFIRM RECEIVING`),
  draw a `REQUEST NEW` button (the real entry point is a `Faster Pay` toggle), or colour a CTA green
  (it's white/disabled). The fix is mechanical: enumerate child nodes with `get_metadata`, screenshot
  **each state by its own node id** at `maxDimension` 1400+, and transcribe from those — at draw time,
  not from earlier notes. This also surfaces frame-internal `$` inconsistencies (a `2 business days -
  4% fee` tier confirming a `−2%` amount) that you must **mirror and flag as an OQ**, never recompute.
  If a mockup sub-agent dies and you take over, still do the per-state re-open — do not shortcut from
  the extraction.
- **The design carries states the AC omits** — open every Figma frame. Empty/error/loading/disabled
  states are where the negative and edge cases come from; skipping Figma silently drops coverage.
- **Ground expected results in code, not vibes** — the Step 3 agents give you the *real* limits and
  error messages. "Should show an error" is weak; "returns 422 with `field required`
  (`Validator.java:88`)" is a test. Cite the source.
- **Requirements describe the happy path; code and the checklist reveal the rest** — most bugs live
  in boundaries, invalid transitions, concurrency, and failure paths. The edge-case pass
  (Step 5) is a deliverable, not optional garnish.
- **Not-yet-implemented is fine** — if the feature isn't built, write cases against the AC + design
  and the nearest existing pattern the agent found, and mark expected results that depend on
  unbuilt behavior as open questions.
- **All Jira/Figma access is read-only** — this skill reads; it never creates or edits issues, and
  it never writes inside a product repo. Output goes to `<TDD_DIR>/` only.
- **HTML: don't re-type CSS** — wrap with `wrap_html.py`; only the body fragment + meta.json are
  yours. Wide tables go inside `.tbl-scroll` so the page never scrolls horizontally on mobile.
- **`<TDD_DIR>/` folder — the right set of files, every time.** Always emit `<KEY>.md` and `<KEY>.html`
  together (markdown-only is incomplete). **For any UI-facing story, also emit `<KEY>-mockups.html`
  (Step 8)** — a UI story that ships only the md/html is incomplete. Only a purely non-UI story is
  done at two files.

## Troubleshooting

- **Atlassian MCP not connected / `getJiraIssue` unavailable** → run `/mcp` and connect Atlassian,
  or ask the user to paste the ticket text and proceed from that (say you're doing so).
- **Figma frame won't render / seat gated** → `get_screenshot` works on a View seat; if
  `get_design_context` is gated, you don't need it — screenshot + metadata are enough. If the
  connector is missing entirely, list the links and raise an open question per un-reviewed frame.
- **Don't know which repo implements the story** → ask the user, or infer from the ticket's
  components/keywords; the Step 3 fan-out runs against whatever repo path(s) you're given.
- **`wrap_html.py` prints its docstring** → that's the no-args usage message; pass
  `body.html meta.json`. **`FileNotFoundError` for the skeleton** → run the script by its real path
  (`<REPO>/skills/write-test-cases/scripts/wrap_html.py`) so it resolves `../assets/html_skeleton.html`.
- **`json.decoder.JSONDecodeError`** → `meta.json` is malformed; validate it (`python3 -m json.tool
  meta.json`) before wrapping.
