---
name: breakdown-story
description: >
  Break down and design a Jira story across the Ship.Cars stack. Use when asked to
  "break down", "groom", "decompose", "design", or "plan the work for" a Jira ticket
  (e.g. "break down SCP-14292", "groom this story", "design SCP-14292"). Fetches the
  ticket (read-only) via the grooming client, identifies which surfaces it touches
  (platform-backend Django, the Java services, the React micro-frontends, mobile),
  fans out Sonnet sub-agents to find the relevant files in each repo, always checks
  whether the change reaches the iOS/Android ePOD apps, always reviews any Figma design
  links found in the story or its linked product issue via the Figma MCP, evaluates the
  Definition-of-Ready checklist with evidence, and — for bug/defect tickets — fans out sub-agents to
  query the corresponding environment's GCP Cloud Logging (read-only) to confirm the failure and
  surface the root-cause signal, then designs the cross-component implementation and emits
  paste-ready Jira sub-tasks as both a markdown doc and a self-contained HTML page
  (with inline SVG sequence/design diagrams), plus a matching Change Design Record folder
  (a directly-editable README.md as the single source of truth + a self-contained diagram.svg)
  under <CDR_DIR>/<KEY>/.
argument-hint: "<JIRA-KEY>   e.g. SCP-14292"
---

# Break down a Jira story (cross-component design)

Given a Jira key, this skill produces an engineering breakdown + design spanning the four
Ship.Cars surface families and writes it to `<BREAKDOWNS_DIR>/<KEY>.md` **and**
`<BREAKDOWNS_DIR>/<KEY>.html` — **and** a per-story **Change Design Record** folder at
`<CDR_DIR>/<KEY>/` (a directly-editable `README.md` — the single source
of truth — plus a self-contained `diagram.svg`) so the model / event / API deltas the design implies
are captured in the change-record format and stay joinable to `codebase-map/`. The skill writes the
CDR **locally** only; publishing it to the `agentic-sdlc-artifacts` repo is a separate, explicit step.

It is an **orchestration** skill, driven by one small driver plus sub-agents:

1. **Fetch** the ticket with `fetch_ticket.py` (read-only; wraps `<GROOMING_DIR>/jira_client.py`).
   It also expands each linked issue (the product story it `implements`) and downloads the
   story's + linked issues' image/PDF attachments locally — **`Read` the design images.** The
   driver also surfaces a **`## Figma design links`** section (every `figma.com` URL it found
   anywhere in the story, subtasks, comments, or linked issues).
1b. **Review Figma designs (always, via MCP)** — for every link the driver surfaced, open it with
   the Figma MCP and actually look at it. Figma links are external URLs the read token can't
   download, so they are *not* in the attachment images — this is the only way to see them.
1c. **Review video attachments (always, if any)** — the driver downloads any screen recording and,
   via ffmpeg, extracts still frames under `<name>.frames/`. **`Read` those frames in order** — a
   repro/design often lives *only* in a video (empty prose AC).
2. **Identify surfaces** — tags are a low-trust hint; reconcile the keyword map with a
   tag-independent fleet-wide token grep so wrong/missing tags can't silently drop a repo.
3. **Fan out (Sonnet)** — one `Explore` sub-agent per candidate repo to find relevant files.
3b. **Mobile impact check (always)** — decide whether the change reaches the iOS/Android ePOD apps.
3c. **Definition-of-Ready evaluation** — verdict + justification + evidence for all 12 checklist items.
3d. **Bug/defect log check (GCP, conditional)** — for bug tickets with a server-side signal, fan out
   Sonnet sub-agents to read the corresponding environment's Cloud Logging (read-only) and confirm the
   failure / find the root-cause signal. Skipped (with a recorded reason) for non-bugs.
4. **Design (Opus, this thread)** — synthesize findings into the breakdown. **Every breakdown item
   (each per-component design entry and each proposed sub-task) carries a proposed solution +
   justification + tradeoffs** — the *chosen* approach, *why* it wins here, and *what alternatives
   were rejected and what you give up*.
5. **Emit markdown** — the doc + paste-ready sub-tasks. Never auto-creates Jira issues (token is read-only).
6. **Emit HTML** — a self-contained companion page with inline SVG diagrams (solution/justification/tradeoffs rendered too).
7. **Emit CDR** — a Change Design Record folder `<CDR_DIR>/<KEY>/` (a directly-editable `README.md` — the single source of truth — + a self-contained `diagram.svg`) capturing the design's data-model / event / REST deltas as GitHub-native Markdown.

**Path placeholders below resolve from the workspace layout `install-sdlc.sh` creates**
(`<WORKSPACE>/agentic-sdlc-artifacts/` = `<REPO>`, `<WORKSPACE>/ship-cars-usa/` = `<SHIP_CARS_DIR>`).
The scripts resolve these themselves from their own location (no `cd` needed), and each
placeholder is overridable by the matching env var: `<REPO>` (this checkout),
`<SHIP_CARS_DIR>` (`$SHIP_CARS_DIR`), `<CODEBASE_MAP_DIR>` (`$CODEBASE_MAP_DIR`, default
`<REPO>/codebase-map`), `<GROOMING_DIR>` (`$GROOMING_DIR`, default `<REPO>/grooming`),
`<BREAKDOWNS_DIR>` (`$BREAKDOWNS_DIR`, default `<REPO>/jira-breakdowns`), `<CDR_DIR>`
(`$CDR_DIR`, default `<REPO>/CDR`). The driver is `<REPO>/skills/breakdown-story/fetch_ticket.py`;
the HTML helpers are `<REPO>/skills/breakdown-story/wrap_html.py` and `assets/html_skeleton.html`.

## Prerequisites

This skill assumes the post-install workspace: **`install-sdlc.sh` has run** (so
`<SHIP_CARS_DIR>` and this `<REPO>` are checked out and `<REPO>/codebase-map`,
`<REPO>/grooming`, `<REPO>/jira-breakdowns`, `<REPO>/CDR` exist), and credentials are
set — a **Jira read token** (`$JIRA_READ_TOKEN` or `<GROOMING_DIR>/jira-read.txt`), the
**claude.ai Figma** MCP connected (Step 1b), **gcloud** authed (Step 3d), and **git**
configured. No hardcoded user paths: every location resolves from `<REPO>` (this
checkout) or its matching env override.

Python 3 (stdlib only) and the Jira token. Verify in one shot (token via env or file):

```bash
{ [ -n "$JIRA_READ_TOKEN" ] || [ -f <GROOMING_DIR>/jira-read.txt ]; } \
  && test -d <CODEBASE_MAP_DIR> && echo ok
```

For **video attachments** (Step 1c), `ffmpeg` (with `ffprobe`) enables automatic frame extraction —
the driver downloads the video either way, but only samples it into Readable frames when ffmpeg is on
PATH. It's an **optional** dependency: absent it, the driver still saves the video and prints how to
extract frames, so the skill degrades gracefully. Verify / install:

```bash
which ffmpeg ffprobe || brew install ffmpeg
```

For Step 1b (Figma review), the **claude.ai Figma** MCP connector must be authenticated — run
`/mcp`, select "claude.ai Figma", and authorize. Confirm with the `whoami` Figma tool — note the
seat type: a "View" seat can `get_screenshot`/`get_metadata` but not necessarily
`get_design_context`. If it's not connected, the skill still runs — it just leaves Figma links
for a human and flags DoR item 2.

For **Step 3d** (bug/defect log investigation), the `gcloud` CLI must be installed and authenticated
with access to the four environment projects. Verify in one shot:

```bash
gcloud auth list --filter=status:ACTIVE --format='value(account)' \
  && gcloud projects list --format='value(projectId)' | grep '^shipcars-platform-' && echo ok
```

All log reads are `gcloud logging read` (read-only), and a global PreToolUse guard
(`~/.claude/hooks/gcloud-readonly-guard.py`, wired in `~/.claude/settings.json`) blocks **any**
mutating `gcloud`/`gsutil`/`bq` verb — so this step can never change cloud state, in this thread or in
a sub-agent. If gcloud isn't set up, the skill still runs: Step 3d records "GCP not available" and
leaves log verification to a human.

## Step 1 — Fetch the ticket

```bash
python3 <REPO>/skills/breakdown-story/fetch_ticket.py SCP-14292
```

Prints one markdown block: summary, components, **parent**, description/AC (ADF flattened),
the story's **attachments**, **existing subtasks** (each with description **+ status · estimate ·
assignee**), **linked issues — each expanded with its full description + attachments**, and
**comments** (ADF flattened). Read all of it — the parent and links carry the real scope; the
subtask fields and comments are the evidence for the Step 3c DoR evaluation. (Add `--json` for
raw fields if you need a custom field id.)

**Product stories and design images are fetched automatically — use them.** An SCP story usually
`implements` a product issue in a sibling project (e.g. `CPDR-…`) that holds the real problem
statement, the success metrics, and the design **mind-maps/screenshots**. The driver now:

- **Expands every linked issue one level deep** — prints its full description/AC inline under a
  `### 🔗 Linked issue <KEY>` heading. The product story's framing (and often a flow design the
  SCP ticket only gestures at) lives there. Disable with `--no-links-deep` only if a story has a
  huge, irrelevant link web.
- **Downloads image + PDF attachments** (of the story *and* of each linked issue) to
  `<BREAKDOWNS_DIR>/attachments/<ISSUE-KEY>/` and prints the local path. **These need no auth
  beyond the read token.** A Figma/Drive link is *not* an attachment — it's an external URL the
  token can't download. Figma links are instead collected into the **`## Figma design links`**
  section (see Step 1b); other external links (Drive, Loom) are left as URLs for a human.
  Disable attachment download with `--no-attachments` to list-without-fetch.
- **Downloads video attachments and extracts frames** (of the story *and* of each linked issue) —
  a screen recording is pulled to `<BREAKDOWNS_DIR>/attachments/<ISSUE-KEY>/<name>` and, when ffmpeg
  is available, sampled into stills under `<name>.frames/` (one frame every ~2s, capped at ~48). The
  Read tool can't ingest an mp4 but it *can* Read those frames — so a repro/design that lives only in
  a video becomes visible design evidence (see Step 1c). The output prints a `🎞 … → <path>` line and
  a `🖼 extracted N frames → <dir>/ — Read these frames …` line. Disable with `--no-video` (still
  downloads the video, skips extraction).

When the output lists a downloaded image (`🖼 … → <path> — Read this file to VIEW the image`),
**actually `Read` that path** before designing. The flow diagram / mind-map frequently disagrees
with or refines the prose AC (e.g. the *real* completion trigger, an SMS-copy requirement, an
empty-state) — that is exactly the design evidence DoR items 2, 3 and 4 ask for, and it is the
content the old `_[attachment]_` flattening silently dropped. ADF `media` nodes in the body now
read `_[embedded image — see ## Attachments]_` and point you at the downloaded file.

## Step 1b — Review Figma designs via MCP (always, if any link exists)

The driver's **`## Figma design links`** section lists every `figma.com` URL it found anywhere
in the story, its subtasks, comments, or the linked product issue. **For each one, open it with
the Figma MCP and look at it before you design.** A Figma link is an external URL — the read
token cannot download it, so unlike a Jira image attachment it is *not* among the files Step 1
saved. The MCP is the only way to see it, and the design it points at is exactly the evidence
DoR items 2 (designs validated), 3 (functionality ↔ implementation), and 4 (variants/empty
states) ask for. **If the section lists links and you skipped them, the breakdown is incomplete.**

**Prereq:** the **claude.ai Figma** connector must be authenticated (`/mcp` → "claude.ai Figma").
If it isn't connected, say so, fall back to leaving the links as URLs for a human, and mark DoR
item 2 `⚠️ needs human` — don't silently drop them.

**How to read a link.** Extract `fileKey` and `nodeId` from the URL
(`figma.com/design/<fileKey>/<name>?node-id=<n1>-<n2>` → `nodeId` is `<n1>:<n2>`; a
`branch/<branchKey>` segment means use the `branchKey` as the `fileKey`):

1. **`get_screenshot(fileKey, nodeId)`** — the primary tool. It renders the frame as a PNG you
   can actually see, works on a **View seat**, and works for design files, FigJam `/board/`, and
   Slides. Bump `maxDimension` (e.g. 2048) when you need to read fine copy. This is what validates
   the design against the AC.
2. **`get_metadata(fileKey[, nodeId])`** — design files only (`/design/`). Cheap structural
   overview (node ids, names, sizes). Omit `nodeId` to list the file's top-level pages when the
   URL has no `node-id`; then drill in. Use it to enumerate states/variants for DoR item 4.
3. Reach for `get_design_context` **only** if you genuinely need design-to-code detail (tokens,
   exact spacing) — it's the heavy codegen tool and may be gated above a View seat. For a
   *breakdown* you almost never need it; the screenshot + metadata are enough to review intent.

If the URL has **no `node-id`**, call `get_metadata(fileKey)` (no node) to list pages, or
`get_screenshot` on a page node — don't guess a node id. FigJam/Slides links: use
`get_screenshot` only (`get_metadata`/`get_design_context` are design-file-only).

Fold what you see into Step 4 (does the design match the AC? any state/variant the AC misses?)
and cite it in the Step 3c DoR table (item 2: "reviewed Figma frame <node> — matches AC" / "AC
omits the empty state shown in the design").

## Step 1c — Review video attachments (always, if any exist)

**A video is often the only real evidence.** Tech-support bugs and product walkthroughs frequently
ship a screen recording with an empty prose description — SCS-1997's *entire* repro was a 17-second
`.mp4` and nothing else (no AC, no steps, no components). The Read tool can't open an mp4, so the
driver downloads the video **and** (Step 1 above) samples it into still frames you *can* Read. When
the output shows a `🎞 … → <path>` line followed by `🖼 extracted N frames → <dir>/ — Read these
frames …`, **actually `Read` those frames** — in order — before designing. Do not skip them and
design from the summary alone; a recording that made it onto a ticket is there because it carries the
repro or the flow the words don't.

- **Read the frames as a sequence.** They're `f_001.jpg … f_NNN.jpg`, ~1 frame / 2s. Reconstruct the
  before → action → after: the starting state, what the user clicks, and the resulting (often wrong)
  state. For a bug, the contradiction between the first and last frame is usually the defect itself
  (SCS-1997: status advanced to PICKED UP while the revision panel was *still pending*).
- **Use the frames as the AC when the ticket has none.** What you reconstruct becomes the "reproduced
  behaviour" you write into `## Ticket` / `## Root cause`, and the expected-vs-actual you design the
  fix against. Cite specific frames ("frame 4 shows the success toast with the revision still
  un-acknowledged") so a reviewer can verify.
- **If ffmpeg is missing** the driver prints a loud banner at the very top of its output
  (`⚠️ ACTION NEEDED — ffmpeg not installed, video frames NOT extracted`) plus a `⚠️ ffmpeg not
  installed …` line under the attachment. When you see it, **you MUST tell the user, in your chat
  reply, that the ticket has a video that could not be turned into frames and that ffmpeg needs
  installing** — state the video's name and that `brew install ffmpeg` + re-running `fetch_ticket.py`
  will make it viewable. Do not bury it or proceed as if no video existed: offer to install ffmpeg
  and re-run, and flag DoR item 2 accordingly (the repro/design evidence is unreviewed). Never
  silently design from the text alone when a video is present but unextracted.
- **Fold it into everything downstream:** the Step 3 fan-out (what repos the observed screen implies),
  the Step 3b mobile check (was the recording taken on a driver app?), and the Step 3c DoR table
  (item 2 designs/evidence, items 3/4 functionality & variants). A video you didn't watch is a
  breakdown built on a guess.

## Step 2 — Identify touched surfaces

**Tags are a low-trust prior, never the answer.** The `Components`/labels/`[UM]`-style
prefixes are a *hint* about where the work lives — they are frequently wrong or incomplete:
`BE` is ambiguous (Django *or* a Java service), `PROJECTS_INDEX.md` miscategorizes ~12 of 30
sampled "Quarkus" backends that are actually Spring, and a story routinely touches a repo no
tag mentions. So the candidate list is built from **two independent derivations that you then
reconcile** — and the second one does not look at the tags at all.

### 2a — Tag-derived candidates (the hint)
Start from `Components` + subtask prefixes + labels + the keyword map below. This gives a
first-guess list. **`BE` is ambiguous** — disambiguate with subtask prefixes and keywords:

| Subtask prefix / keyword | Surface (repo) |
|---|---|
| `[UM]`, user, account, login, MFA, auth, Keycloak | **`user-backend`** (Java/Spring, identity) |
| email, SMS, notification, message, SendGrid, Twilio | **`notification-backend`** (Java/Spring) |
| `[Django]`, carrier network, driver, truck, asset, onboarding, premium, payments-django | **`platform-backend`** (Django) + maybe `rateengine`, `company-documents` |
| posting, load board, offer, negotiation | `posting-frontend`, Django BE, `syncer` |
| cube, aggregation, search, filter, count | `cube` (Quarkus) |
| sync, event, posting_review_actor | `syncer` (Quarkus) |
| AAAG, ASI, AutoIMS, CarsArrive, Super Dispatch, Rivian | `integration-executor`, `command-executor`, `quote-manager-backend` |
| contract pricing, mileage band, lane, line item | `contract-pricing-backend`, `contract-pricing-frontend` |
| `[FE]`, screen, modal, tooltip, page, button | the matching `*-frontend` micro-FE (+ root `platform-frontend`, shared `globals-frontend-package`) |
| ePOD, inspection, BOL, signature, damage, attachment | `epod-ios`, `epod-android` (**mobile — always run the Step 3b mobile-impact check; whether app sub-tasks are in scope is a separate decision**) |

If a candidate repo has no `codebase-map/repos/<repo>.md` shadow, fall back to
`PROJECTS_INDEX.md` + the repo's `pom.xml`/`package.json`. The full surface map and
domain rollups live in `codebase-map/` and the sibling `jira/ticket-classification-runbook.md`.

### 2b — Content-derived discovery (tag-independent — ALWAYS run this)
Pull the **distinctive tokens** out of the AC + subtask titles — entity/class names, endpoint
paths, enum values, DB column names, distinctive domain nouns (e.g. `mfa_phone_number`,
`updateMfaVerificationSettings`, `CarrierPerformanceStats`). Pick the 2–5 *most distinctive*
(skip generic words like "user", "email", "update" — they match everything). Then grep the
**whole fleet**, ignoring tags entirely, to see which repos actually contain them:

```bash
rg -l -i -e 'token1' -e 'token2' -e 'token3' ship-cars-usa 2>/dev/null \
  | sed 's#.*/ship-cars-usa/\([^/]*\)/.*#\1#' | sort -u
```

~3.5s across all 232 repos. This is the safety net for wrong/missing tags — it surfaces the
real code owners regardless of how the ticket was labelled. (For SCP-14292 it surfaced
`keycloak-mfa-plugin` and `platform-frontend`, which `Components: BE` alone would never have
pointed at.) Two caveats: (i) generic infra repos hold no domain tokens, so a repo reached only
through a shared client (e.g. `notification-backend` via `notification-client`) won't appear
here — keep it from 2a; (ii) a hit in a repo doesn't prove *this* story touches it, only that
the term lives there — the Step 3 fan-out confirms.

### 2c — Reconcile
Union 2a + 2b into the candidate list, and resolve the disagreements explicitly:
- **In 2b but not 2a** → the tags missed it. **Add it** and fan out (this is the whole point).
- **In 2a but no code evidence** (no shadow, no tokens, nothing the fan-out finds) → the tag is
  likely wrong. Keep it as a candidate for *one* fan-out, but if that agent finds nothing,
  record it as "tagged `<X>` but no implementing code found — likely mis-tagged" rather than
  inventing work for it.
- The mobile apps (`epod-ios`/`epod-android`) are handled by the always-on Step 3b check, not this list.

Produce the reconciled candidate list (typically 2–5 repos). For SCP-14292 this is
`user-backend` (primary) + `notification-backend` (reached via the shared client — from 2a, not
2b), with `keycloak-mfa-plugin`/`platform-frontend` checked and ruled out as not in scope.

## Step 3 — Fan out Sonnet search agents (one per candidate repo)

Spawn them **in a single message** (parallel). Use `subagent_type: "Explore"` and
`model: "sonnet"` — cheap, read-only, source-grepping. Prompt template:

```
Repo: <repo>  (<SHIP_CARS_DIR>/<repo>)
Jira story: <KEY> — <summary>
Relevant requirement for THIS repo:
<paste the slice of the AC / subtask that maps to this repo>

1. Read <CODEBASE_MAP_DIR>/repos/<repo>.md first (note its `status`: seed/verified are
   trustworthy; stub/stale → trust the source more than the body).
2. Grep the repo source for the files/symbols this change would touch — entry points,
   services, controllers/resources, DTOs/models, event publishers/consumers, templates,
   config (feature flags, application.properties).
3. Report, as a structured list:
   - Relevant files (path → one-line why)
   - Key symbols/classes/functions to extend (with file:line)
   - Existing patterns to REUSE (e.g. an existing email-sending service, an event already
     published) so we don't build new where one exists
   - Integration points: events published/consumed, REST endpoints, DB tables touched
   - Any "don't-do-here" gotchas from the shadow doc
4. RELEVANCE CHECK (answer even if it contradicts the tags):
   - Is this repo actually involved in this change? If you find NOTHING relevant, say
     "NOT RELEVANT" plainly — do not manufacture a connection to justify the tag.
   - Does the change clearly belong to or also require a DIFFERENT repo you can see referenced
     here (an imported client, a called endpoint, a shared package, an event consumed
     elsewhere)? Name that repo so we can fan out to it.
Do not propose a design — just find and report.
```

**Act on the relevance answers.** If an agent says "NOT RELEVANT," drop that repo and record it
as mis-tagged in the breakdown. If an agent names another repo, add it and fan out (a second
small round is normal — better than shipping a breakdown that misses a surface). The candidate
list is not frozen after Step 2; it converges as the agents report.

## Step 3b — Mobile impact check (always)

**Run this on every breakdown.** The rule that makes it cheap: the two ePOD apps (`epod-ios`,
`epod-android`) **share no code with the web/FE surfaces** — they are native Swift/Kotlin and
only talk to the fleet over **backend HTTP APIs** (posting/attachment/location/user-backend,
Keycloak). So a change can reach mobile *only* through a **backend API / DTO / event-contract**
delta. A pure-FE (React micro-frontend) or internal-tooling ticket has **zero** mobile impact by
construction — say so explicitly with that reasoning as the evidence.

1. From the Step 3 findings, build the **contract-delta list**: every changed/added REST
   endpoint, request/response DTO field, and published event.
2. **If that list is empty** (or no driver-facing backend is touched) → record "no
   mobile-consumable surface touched" with the specific reason, and **skip the agents**.
3. **Otherwise** spawn **two Sonnet `Explore` agents in one message** (parallel),
   `model: "sonnet"`, one per app. Prompt template:

```
Repo: <epod-ios | epod-android>  (<SHIP_CARS_DIR>/<repo>)
Jira story: <KEY> — <summary>
A backend change is being made. Determine if THIS app is affected.

Changed/added backend contract (endpoints, DTO fields, events):
<paste the contract-delta list from step 1>

1. Read <CODEBASE_MAP_DIR>/repos/<repo>.md first (both are `seed` — trustworthy).
2. Grep the app's remote/API layer for these endpoints/DTO field names:
   - Android: module_data/.../remote/ (Retrofit services, request/response models, mappers)
   - iOS:     ShipCars/Data (API clients, Codable DTOs, endpoint definitions)
3. Report, as a structured list:
   - AFFECTED? yes/no, with the evidence (file:line of the call site / DTO that matches)
   - Which endpoints/fields this app actually consumes (file:line)
   - Whether a removed/renamed/required-changed field would break decoding here
   - Any versioning/back-compat note (does the app pin an API version or tolerate extra fields?)
Do not propose a design — just find and report whether and where this app is affected.
```

Carry the result into the `## Mobile impact` section (Step 5) **and** into DoR item 7
("ePOD side effects — Are there API changes?") in Step 3c. An affected app that the ticket
does *not* yet have sub-tasks for is an open question / proposed sub-task, not a silent pass.

## Step 3c — Definition-of-Ready evaluation

Evaluate **all 12** "Definition of Ready for Development during Grooming" items. Each gets a
**verdict** + one-line **justification** + **cited evidence** — a Jira field from the driver
output, a `file:line`, a design decision in this breakdown, or an explicit "needs human".
Never assert "met" without evidence; when the evidence isn't in reach, say what to check.
Verdict vocabulary is **closed** — the Verdict cell contains **exactly one** of these four
tokens, nothing else: `✅ met` · `⚠️ partial / needs action` · `❌ not met` · `N/A`. All nuance
("needs human", "needs decision", "race only", "with why") goes in the **Justification** column,
never in the verdict — do not invent variant strings like `⚠️ needs human` or `⚠️ partial / needs human`.

Evidence sources per item (what to look at):

| # | Checklist item | Primary evidence |
|---|---|---|
| 1 | Story is a proper, testable vertical split | The surface table + AC slices — does each surface deliver a user-visible vertical, independently testable? |
| 2 | Designs have been validated | The **`## Figma design links`** the driver surfaced (open each via the Figma MCP — Step 1b) **and/or** an image/PDF attachment on the story or its linked product issue (the driver downloads these — `Read` the saved path) **and/or** the frames extracted from a video attachment (Step 1c — `Read` them in order). Validation note in comments? Don't mark `❌` if there are Figma links you haven't opened, design images you haven't read, or video frames you haven't reviewed; mark `⚠️ partial / needs action` (justify "needs human") only if the Figma connector is unauthenticated. |
| 3 | Functionalities implied in the design are in the tech implementation | Cross-check every AC bullet ↔ a per-component design line; flag any AC with no implementing component. |
| 4 | Designs complete (all functionalities **and variants**) | AC variant/empty-state/responsive list ↔ design coverage (e.g. `N=0` empty state, mobile reflow). |
| 5 | Feature flag considered + decision taken | Grep the touched repo for the flag mechanism — FE: `useFlag`/`src/constants/unleash.ts`; Java: Unleash / `application.properties`. State the decision (flag yes/no + name). |
| 6 | Mixpanel events evaluated | AC names events? Matched to `track()` call sites (`globals-frontend-package` / `analytics.ts`). |
| 7 | ePOD side effects considered (API changes?) | **From Step 3b** — the mobile-impact verdict + contract-delta. |
| 8 | Sub-tasks created for each component | Driver `## Existing subtasks` ↔ the surface table (one per touched surface?). |
| 9 | Sub-tasks estimated | Driver subtask `Estimate:` field (`—` = unestimated). |
| 10 | Automation-test sub-task created, estimated, **and assigned** | Driver subtasks: is there an automation/QA-tagged sub-task with a non-`—` estimate and a named assignee? |
| 11 | API contract agreed + written into the Story as a comment | Driver `## Comments` section — is there a comment stating the contract? (Commonly absent → `❌`.) |
| 12 | Sub-tasks **and** Story in status `To Do` | Driver Status fields (story + each subtask). "Requirements refinement" ≠ `To Do`. |

A `❌`/`⚠️` verdict is actionable: surface it in Step 4 as an open question and (where it implies
work) a proposed sub-task.

## Step 3d — Bug/defect log investigation (GCP Cloud Logging, conditional)

**Only for bug/defect tickets, and only when there is a server-side signal to look for.** This is
the log-evidence analogue of the Step 3b mobile check: a **gated** fan-out that runs when it can add
evidence and is skipped — with a one-line recorded reason — when it can't. It never mutates anything
(read-only guard, see Prerequisites), so running it against any environment is safe.

### When to run — both must hold
1. **The ticket is a bug/defect** — driver `Type: Bug` (or `Defect`/`Regression`), or strong defect
   signals: a `bug`/`regression`/`hotfix` label, an "actual vs expected / steps to reproduce" AC, or a
   pasted stack trace / error message / HTTP 5xx. A feature/story is **not** a bug — skip.
2. **A touched *backend* service exists to inspect** — from the Step 2/3 reconciled surfaces. A defect
   that is purely UI/copy/design with no server-side symptom has nothing in the logs; record "no
   server-side log signal to investigate" and skip.

If either is false, write one line in the breakdown ("not a bug" / "no server-side log signal" /
"GCP not available") and move on — do **not** fan out.

### Pick the environment (the "corresponding environment")
Each environment is its own GCP **project**: `shipcars-platform-{dev,qa,staging,prod}`. Choose from the
ticket, most-specific first:
- An explicit env in the description/comments/an "Environment" field, a prod customer/URL, or an
  affects-version → that env.
- A QA/staging reproduction described in the ticket → that lower env.
- **Default `prod`** for a reported/customer-facing bug — that's where reported failures live (and the
  CLI's default project). State the chosen project and *why* in one line. If genuinely ambiguous,
  default prod, mark it an assumption, and note the lower envs are one `--project` flag away (reading
  any env is safe).

### Map service → log filter (verified against the live fleet)
The GKE **`container_name` equals the repo/service name** for Ship.Cars services — `platform-backend`,
`user-backend`, `quote-manager-backend`, `cube`, `location-provider`, `keycloak`,
`integration-executor`, `api-gateway`, `location-history-backend`, … Filter on `container_name` alone
(not namespace). If unsure of a repo's container name, discover the names seen recently:

```bash
gcloud logging read 'resource.type="k8s_container"' \
  --project=shipcars-platform-prod --limit=400 --freshness=1d \
  --format='value(resource.labels.namespace_name, resource.labels.container_name)' \
  | sort | uniq -c | sort -rn
```

### Fan out (Sonnet) — one agent per candidate backend service
Spawn them **in a single message** (parallel), `subagent_type: "Explore"`, `model: "sonnet"` (they have
Bash, and the read-only guard covers their gcloud calls too). Give each the env project, the container
name, the symptom to hunt, and the time window (prefer the bug's reported time as an absolute
`timestamp>=/<=` range; else `--freshness=<N>d`). Prompt template:

```
Environment (GCP project): shipcars-platform-<env>
Service (GKE container_name): <service = repo name>
Jira bug: <KEY> — <summary>
Symptom to confirm: <the exception / stack-trace / endpoint / status-code / domain signature from the ticket>
Time window: <ISO start>..<ISO end>   (or "last <N>d" if the ticket gives no time)

Run READ-ONLY log queries only (a guard blocks any mutating gcloud verb; do not chain a mutating
command into the same shell line or the whole line is blocked). Start broad, then narrow:

1. Errors for this service in the window:
   gcloud logging read \
     'resource.type="k8s_container" AND resource.labels.container_name="<service>" AND severity>=WARNING AND timestamp>="<start>" AND timestamp<="<end>"' \
     --project=shipcars-platform-<env> --limit=50 \
     --format='json(severity,timestamp,jsonPayload,textPayload,labels)'
   (swap the two timestamp clauses for `--freshness=<N>d` if you only have a relative window)

2. Narrow to the symptom — add ONE clause that fits the signal:
   ... AND jsonPayload.message:"<substring>"      # structured logs (most Java/Python services here)
   ... AND textPayload:"<substring>"               # plain-text logs
   ... AND jsonPayload.status_code>=500            # HTTP failures
   ... AND "<free-text substring>"                 # global match across the payload
   If a trace id shows up, pivot to pull the whole request:
   ... AND jsonPayload."dd.trace_id"="<id>"

Report, structured:
- CONFIRMED? does the log show THIS failure in this env/window? yes/no + the single strongest matching
  entry (timestamp, severity, exception class + message, logger).
- Root-cause signal: the exception / stack frame / status_code / logger that points at the cause
  (quote the key line verbatim).
- Blast radius: rough frequency (hit count), first/last seen in the window, any trace_id/request_id to follow.
- Which field carried it (jsonPayload.<key> vs textPayload) so the design can cite it precisely.
Do NOT propose a fix — just find and report what the logs prove.
```

### Fold the result in
Carry every agent's finding into the **`## Root cause`** section (Step 5, bugs-only) — log evidence is
what turns a *guessed* root cause into a *confirmed* one — and into the Step 4 design (the fix targets
the confirmed failure, not just the reported symptom). If the logs **don't** confirm the bug in the
chosen env, say so and treat it as an open question (wrong env? not reproduced? already fixed? logs
aged out of retention?) — never a silent pass. Cite the confirming entry (env · container · timestamp ·
the quoted log line) so a reviewer can re-run the same `gcloud logging read`.

## Step 4 — Design synthesis (Opus, this thread)

This is the "fall back to Opus for the actual design" step. Read every sub-agent's findings
and produce the breakdown using the template in Step 5. For each component decide: what
changes, which files/symbols to touch, what is reused vs new, and the **cross-component
contract** (the event/REST/DTO each side must agree on). Then order the work by dependency
(producer before consumer; contract before either side codes against it) and list open
questions that block estimation. **Fold in** the Step 3b mobile verdict, every Step 3c
`❌`/`⚠️` DoR item, and (for bugs) the Step 3d log evidence — each becomes an open question and, where
it implies work, a proposed sub-task (e.g. a missing automation-test sub-task, an unwritten
API-contract comment). For a bug, the confirmed log signal from Step 3d is the spine of the
`## Root cause` section and anchors the fix to the real failure rather than the reported symptom.

**Every item gets a proposed solution + justification + tradeoffs.** This is the core of the
breakdown — not just *that* a component changes, but *how* you propose to change it, *why* that
approach, and *what you considered and rejected*. For each per-component design entry **and** each
proposed sub-task, author three things, grounded in the Step 3 findings (not generic):

- **Proposed solution** — the concrete approach you recommend: the specific method to add/extend,
  the pattern to follow, the contract shape. Cite the `file:line` / existing pattern it builds on.
- **Justification** — why *this* approach wins here: fits an existing pattern the agents found,
  smallest blast radius, keeps the contract backward-compatible, avoids a new dependency, etc.
  Tie it to evidence from the fan-out, not to first principles.
- **Tradeoffs / alternatives** — the real fork(s) in the road: the other viable approach(es), and
  what each costs. Name what you give up by choosing the recommended one (e.g. "reusing the shared
  template couples the two emails' copy; a second template id is more work but lets them diverge").
  If a fork can't be resolved without a human (Q-item), say so and point at the open question.

Keep each concise (1–2 sentences per field). A breakdown item with a `Change:` but no
solution/justification/tradeoffs is **incomplete** — the whole point of this step is the
*reasoned recommendation*, not a list of files. If there is genuinely only one sane approach,
say so explicitly in Tradeoffs ("no real alternative — this is the only extension point") rather
than omitting it.

## Step 5 — Emit markdown

Write `<BREAKDOWNS_DIR>/<KEY>.md` (create the dir if needed; it mirrors
`jira/classifications/`). Use this shape:

```markdown
---
ticket: <KEY>
summary: "<exact summary>"
parent: <KEY — Title>          # always "KEY — Title"; use "none" if parentless. Never a bare key.
components: [<from Jira — low-trust tag>]
surfaces: [<repos touched>]
tag-note: <OPTIONAL — only when components (Jira tag) diverges from surfaces, e.g. "tagged [iOS] but work is platform-backend — Jira mis-tag"; omit the line entirely otherwise>
broken-down-on: <YYYY-MM-DD>
breakdown-by: Claude Code (Opus), Sonnet search agents — human review pending
---

# <KEY> — Breakdown & Design

## Ticket
> <verbatim summary + AC, from the driver output>

## Root cause
<OPTIONAL — bug tickets only. Use exactly this heading (do not rename to "Root-cause analysis",
"What's actually broken", "TL;DR — root cause", etc.). Omit the section entirely for non-bug work.
When Step 3d ran, lead with the **confirmed log evidence** — env (`shipcars-platform-<env>`) · service
(container) · timestamp · the quoted exception/log line · trace_id — then the mechanism it reveals. If
Step 3d could not confirm it, say so here and carry the "why not" into Open questions.>

## Touched surfaces
| Surface | Repo | Why |
|---|---|---|

## Per-component design
### <repo> (<stack>)
- **Change:** ... (one line — what changes)
- **Proposed solution:** ... (the concrete recommended approach + the `file:line`/pattern it builds on)
- **Justification:** ... (why this approach wins here — tie to a fan-out finding, not first principles)
- **Tradeoffs / alternatives:** ... (the other viable approach(es) and what each costs; or "no real alternative — <why>")
- **Files / symbols:** `path:line` ...
- **Reuse:** ...   **New:** ...
- **Contract (in/out):** publishes/consumes <event>, calls <endpoint>, DTO <name>

## Mobile impact (iOS + Android)
<One line stating the rule outcome: "No mobile-consumable surface touched (FE/internal only)"
OR the contract-delta that reaches mobile.>
<!-- Use these four column headers VERBATIM. Do not shorten "Evidence (endpoint/DTO · file:line)"
     to "Evidence" or "Evidence (file:line)", and do not reword "Affected?". -->
| App | Affected? | Evidence (endpoint/DTO · file:line) | Follow-up |
|---|---|---|---|
| epod-ios | ✅/❌ | ... | ... |
| epod-android | ✅/❌ | ... | ... |

## Definition of Ready evaluation
<!-- Verdict cell = exactly one of: ✅ met / ⚠️ partial / needs action / ❌ not met / N/A.
     Nuance ("needs human", "needs decision", race-only, etc.) goes in the Justification column. -->
| # | Item | Verdict | Justification + evidence |
|---|---|---|---|
| 1 | Testable vertical split | ✅ met / ⚠️ partial / needs action / ❌ not met / N/A | ... |
| ... | ... | ... | ... |
| 12 | Sub-tasks + Story in `To Do` | ✅/⚠️/❌ | ... |

## Cross-component sequencing
1. ...  (producer/contract first)

## Open questions / risks
- ...  (include every ❌/⚠️ DoR item and any affected-but-unplanned mobile app)

## Proposed Jira sub-tasks (paste-ready — token is read-only, create manually)
- **[<COMP>] <title>**
  AC: ... (a TERSE, reviewer-facing "done" statement — the observable outcome, not a restatement
       of the Per-component design prose. Put the *how* in `Solution:` and reference the design
       section; do not re-derive the files/symbols here.)
  Solution: ... (the recommended approach for this sub-task, in one line)
  Justification & tradeoffs: ... (why this approach; the alternative considered + what it costs, or "no real alternative — <why>")

## Cross-references
- Shadows: codebase-map/repos/<repo>.md (one per touched surface)
- Reuse: <ticket-specific file:line anchors the design builds on>
- Companion analysis (if any): <KEY>-<slug>.md
```

(Do **not** re-emit the skill's own `fetch_ticket.py` / `wrap_html.py` paths in the breakdown's
Cross-references — they are byte-identical boilerplate in every file and carry no ticket-specific
information. They live here in the SKILL, not in the output. Keep only ticket-specific references.)

**Before writing the file, run this completeness check** — every breakdown emits the full
canonical section set, in this order, with **no omissions**:
`## Ticket` → (`## Root cause`, bugs only) → `## Touched surfaces` → `## Per-component design` →
`## Mobile impact (iOS + Android)` → `## Definition of Ready evaluation` (all 12 rows) →
`## Cross-component sequencing` → `## Open questions / risks` →
`## Proposed Jira sub-tasks …` → `## Cross-references`. **`## Mobile impact` and
`## Definition of Ready evaluation` are mandatory on every breakdown** — including single-surface,
no-mobile, and bug tickets. A no-mobile story still emits the one-line "No mobile-consumable surface
touched" + the two-row table; a no-UI story still emits the 12-row DoR table (mark items `N/A` with
why). Never silently drop a section — a missing section reads as "the check was skipped," not "N/A."

Then present the proposed-sub-task block in chat for the human to paste. **Stop there** —
do not create issues, and do not write anything inside `ship-cars-usa/<repo>/`.

## Step 6 — Emit HTML companion

Write `<BREAKDOWNS_DIR>/<KEY>.html` — a self-contained, CSP-safe page (no external
assets). **Do not re-type CSS or hand-roll `<head>`** — the boilerplate lives in
`assets/html_skeleton.html`. You author only the **body fragment** + a small **meta.json**, then
staple them with `wrap_html.py`:

```bash
# author body.html (sections + SVG) and meta.json in a scratch dir, then:
python3 <REPO>/skills/breakdown-story/wrap_html.py /tmp/body.html /tmp/meta.json \
  > <BREAKDOWNS_DIR>/<KEY>.html
```

What the body fragment must contain (mirror the markdown, but richer):

- The `<h2>Ticket</h2>` blockquote, `Touched surfaces` table, and `Per-component design`.
- **A proposed-solution block under each per-component design entry** — the solution / justification /
  tradeoffs must render in the HTML too, not only the markdown. Use the skeleton's `.soln` card (it's
  already styled — do **not** add CSS): a `<div class="soln">` with three labelled sections via
  `<span class="lbl">`, `<span class="lbl why">`, `<span class="lbl trade">`. Shape:
  ```html
  <div class="soln">
    <span class="lbl">Proposed solution</span>
    <p>Add <code>sendMfaChangeNotificationSms(...)</code> to <code>MfaNotificationService</code>, mirroring the publish pattern at <code>UserVerificationChannelServiceImpl.java:350</code>.</p>
    <span class="lbl why">Justification</span>
    <p>Reuses the existing <code>notificationClient.sendSms</code> path the agents found — no new infra, contract stays additive.</p>
    <span class="lbl trade">Tradeoffs / alternatives</span>
    <p>Could inline the send at the call site (less indirection) but that duplicates the DTO-build; the service method keeps it testable. No new SendGrid template needed unless copy must diverge (Q2).</p>
  </div>
  ```
  The proposed sub-tasks table likewise carries a `Solution` and `Justification & tradeoffs` line per row (or a `.soln` block beneath it).
- **(Bugs only) A log-evidence block under `<h2>Root cause</h2>`** — when Step 3d ran, render its
  finding immediately after the Ticket blockquote, reusing the skeleton's **`.callout block`** (the red
  bug-callout) + **`.mono`** + a status **`.pill`** — **do not add CSS**. Lead with a status pill
  (`<span class="pill bad">confirmed in logs</span>` when the log confirms the failure, or
  `<span class="pill na">not confirmed</span>` when it doesn't), then the location line (env · container ·
  timestamp · severity), the quoted log line in `.mono`, the mechanism it reveals, and the exact
  re-runnable `gcloud logging read`. **Escape `>` as `&gt;`** inside the query
  (`severity&gt;=WARNING`). Omit the block entirely for non-bug tickets. Verified shape:
  ```html
  <h2>Root cause</h2>
  <div class="callout block">
    <b>Log evidence (GCP) — <span class="pill bad">confirmed in logs</span></b>
    <p><code>shipcars-platform-prod</code> · container <code>platform-backend</code> · 2026-07-27T07:55:37.596Z · <code>ERROR</code></p>
    <p class="mono">status_code 410 · logger epod.middleware · GET /s/J1bQ5ldz/ · dd.trace_id 6a670ef9…</p>
    <p>Middleware returns <code>410 Gone</code> before the view runs — a null <code>token.expires_at</code> is treated as expired.</p>
    <p>Re-run: <span class="mono">gcloud logging read 'resource.type="k8s_container" AND resource.labels.container_name="platform-backend" AND jsonPayload.status_code=410' --project=shipcars-platform-prod --freshness=3d</span></p>
  </div>
  ```
  (Not confirmed → same box with `<span class="pill na">not confirmed</span>` and the "why not / open question" one-liner instead of the log line.) For a bug where Step 3d confirmed, also add a
  `{"text":"root cause: confirmed in prod logs","cls":"bug"}` chip to `meta.json`.
- **At least one SVG sequence/flow diagram** and **one design diagram** — bespoke, hand-authored
  inline `<svg>` that encodes *this* ticket's architecture (the producer→consumer call path, the
  contract handshake, or the screen/data flow). Wrap each in
  `<div class="fig"><div class="fig-scroll"><svg viewBox=...>…</svg></div><div class="cap"><b>Figure N.</b> …</div></div>`
  so wide diagrams scroll instead of breaking the page. Reuse the visual language already
  established in existing pages (e.g. `<BREAKDOWNS_DIR>/SCP-13483.html`): rounded boxes, lane
  labels, `<marker>` arrowheads, the palette CSS vars.
- A **Mobile impact** table and the **Definition of Ready** table, rendering verdicts with the
  pill classes: `<span class="pill good">✅ met</span>`, `pill warn` (⚠️), `pill bad` (❌),
  `pill na` (N/A).
- The proposed sub-tasks table and a `<footer>` (set via meta `footer`).

`meta.json` keys: `title`, `h1`, `subtitle` (one-liner: title · type · priority · status),
`chips` (list of `{text, cls}` — `cls` ∈ `""` blue / `surf` green / `bug` red / `mob` purple;
add a `{"text":"mobile: affected|not affected","cls":"mob"}` chip), and `footer` (HTML). See the
header of `wrap_html.py` for the exact shape.

## Step 7 — Emit the Change Design Record (CDR)

The breakdown already *is* the design; this step re-expresses its **data-model / event / REST
deltas** as a Change Design Record — a directly-editable Markdown file that renders on GitHub. The
CDR is the *diff* the design implies; `codebase-map/` stays the *snapshot*.

**A CDR's single source of truth is `README.md`.** There is no `cdr.json` and no HTML viewer — author
the record as Markdown directly. Each record is a folder holding just:

```
<CDR_DIR>/<KEY>/
  README.md     the record (edit this directly)
  diagram.svg   the blast-radius graphic (self-contained; optional)
```

**Write the files locally only.** Publishing a CDR to the `agentic-sdlc-artifacts` repo is a
separate, explicit step — never commit or push as part of grooming. On a re-groom, overwrite
`README.md` + `diagram.svg` from the latest design
and say so in chat; but if a human has hand-edited `README.md` since (it's the SoT), surface that
before clobbering.

### `README.md` — structure

Author it in exactly this shape (this is what renders cleanly on GitHub):

```markdown
# <exact story summary>

`<KEY>` · **proposed** · <YYYY-MM-DD> · <you@ship.cars> · groomed <YYYY-MM-DD>

**Services:** `<repo-slug>`, `<repo-slug>`, …

**Legend:** 🟢 added · 🟡 updated · 🔴 removed · 🔵 reused

![Design diagram](./diagram.svg)

## Context
<root cause (bugs) + the decision, in 2–5 short paragraphs separated by blank lines. Plain Markdown —
**bold**, `code`, and lists render. If you enumerate points, use a real Markdown list (one `- ` or
`1.` per line), NEVER inline `(1) … (2) …`. Never emit one dense run-on block.>

## §2a · PostgreSQL
*Column delta · <table>*
| Column | Type | Change | Null | Default / backfill |
| --- | --- | --- | --- | --- |
| `<col>` | `<type>` | 🟢 added | <y/n> | <default \| proposed> |

## §3 · Pub/Sub event
*<caption>*
| Field | Type | Change | JSON name | Subscriber action |
| --- | --- | --- | --- | --- |
| `<field>` | `<type>` | 🟡 updated | `<json>` | <what consumers must do> |

## Where it lives & how it's wired
| Aspect | Detail |
| --- | --- |
| service | `<repo · module>` |
| file | `<migration / controller path>` |
| instance | `<main\|core\|users\|edge\|platform> · DB <name>` |
| topic | `<cars.ship.{env}.…>` |

## Rollout
> ⚠️ **§5 · rollout & sequencing**
>
> <one-sentence lead-in — e.g. the ordering principle ("Producer-before-consumer.").>
>
> 1. <step one>
> 2. <step two — **bold** / `code` as needed>
> 3. <step three>
>
> **Risk:** <the coordination / data risk in one line — or a `- ` bullet per risk.>
```

(Use ℹ️ instead of ⚠️ when there's no breaking / coordination risk.)

Rules (derive, don't invent):

- **Sections** ← only the delta kinds the design actually touches — `§2a PostgreSQL`, `§2b
  Elasticsearch`, `§3 Pub/Sub event`, `§4 REST API & DTO`; omit kinds with no delta. Where the
  breakdown names concrete columns/fields/endpoints/DTOs, fill rows; where it's directional, emit one
  row describing the intended change. Exactly one column per table is the **Change** column.
- **The Change column is emoji-coded** by what happens to that row: **🟢 added** (new column / field /
  endpoint / enum value, including a new *optional* field), **🔴 removed** (dropped), **🔵 reused**
  (unchanged / consumed as-is), **🟡 updated** (everything else — changed / renamed / validated /
  extended / version-bumped / conditional). Keep a short label after the emoji (`🟢 added`,
  `🟡 renamed`).
- **Where it lives** ← the Step 3 "where it lives" facts (instance + logical DB + Helm host var,
  owning file/entity/DTO, topic, ES index). Same ownership conventions as `codebase-map`.
- **Rollout** ← Step 5's sequencing, formatted as the multi-line blockquote above: a lead-in line,
  then each step on its own `> N.` line, then a `> **Risk:**` line (or `- ` bullets), with blank `>`
  lines between those blocks. **Never** collapse the steps into one inline `(1) … (2) …` paragraph —
  GitHub won't render it as a list, it becomes a wall of text. Use ⚠️ when there's an ES
  drop-and-rebuild resync, a forward-only migration/backfill, a breaking event change, or a cross-DB
  read to coordinate — otherwise ℹ️.
- Keep `services` slugs identical to `codebase-map/repos/<slug>.md` so the record stays joinable.
- Escape any literal `|` inside a table cell as `\|`.

### `diagram.svg` — MUST be self-contained (GitHub-native)

Adapt the Step 6 flow SVG into a standalone `diagram.svg` (add `xmlns`, drop the skeleton wrapper).
It is embedded in `README.md` and viewed on GitHub, which **strips `<style>` and CSS variables** — so
the SVG must carry all styling as **inline presentation attributes**, not classes/CSS:

- First child after `<defs>`: an opaque white background — `<rect x="0" y="0" width="<vbW>"
  height="<vbH>" fill="#ffffff"/>` — so it reads on both GitHub themes.
- Node rects: `fill="#f5f6f8" stroke="#cbd2d9" stroke-width="1.5"`; a changed ("touched") node:
  `fill="#fbe7d6" stroke="#c2703d"`.
- Flow paths: `fill="none" stroke="#8a929b" stroke-width="1.6"`; primary ("hot"): `stroke="#b45309"
  stroke-width="1.8"`; the red "this breaks" edge: `stroke="#b91c1c" stroke-dasharray="5 3"`.
- `<marker>` polygons: filled with a concrete colour (`#b45309`, or `#b91c1c` for the break edge) —
  never `var(--…)`.
- Text: titles `fill="#16191d" font-size="14" font-weight="600"`, subs `fill="#5c646d"
  font-size="12"`, store notes `fill="#7a828b" font-size="11" font-style="italic"`, edge labels
  `fill="#374151"` (hot → `#b45309`, remove → `#b91c1c`); give every `<text>` a
  `font-family="system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif"` and center edge labels
  over the arrow gap (`text-anchor="middle"`).
- If the ticket has no meaningful flow, omit `diagram.svg` and drop the `![Design diagram]` line.

Then, in chat, print the CDR path (`<CDR_DIR>/<KEY>/README.md`) alongside
the breakdown paths and note it's directly-editable Markdown that renders on GitHub. **Stop there** —
same rule as Steps 5–6: never create Jira issues, never write inside `ship-cars-usa/<repo>/`.

## Gotchas

- **Descriptions are ADF JSON**, not text. `fetch_ticket.py` flattens it (`adf_to_md`). If
  you ever call `jira_client` directly, you must flatten yourself.
- **Attachments live in the `attachment` field, not in the ADF body** — the body only has opaque
  `media` nodes. The driver downloads image/PDF attachments to
  `<BREAKDOWNS_DIR>/attachments/<KEY>/` and prints the path; an `🖼 … Read this file to VIEW`
  line means **open it with `Read`** — a flow diagram or metrics screenshot is real design
  evidence, and not opening it is how the prose-only read of SCP-14363 missed the actual
  completion trigger and an SMS-copy requirement.
- **Video attachments are auto-extracted into frames — Read them (Step 1c).** The driver downloads
  a screen recording and, when ffmpeg is on PATH, samples it into `<name>.frames/f_NNN.jpg`; a
  `🎞 … → <path>` line plus `🖼 extracted N frames → <dir>/ — Read these frames …` means **Read those
  frames in order** before designing. A video is frequently the *only* evidence on a tech-support bug
  (SCS-1997 had an empty description and a lone 17s `.mp4`) — designing from the summary while ignoring
  the frames is exactly the prose-only failure the image gotcha warns about, one step worse. If you
  see `⚠️ … ffmpeg not found …` instead, install ffmpeg and re-run rather than skipping the video.
- **Linked product stories are expanded automatically** (one level). The `implements: CPDR-…`
  link is not just a reference — its description carries the problem framing/metrics and its
  attachments carry the designs. Read the `### 🔗 Linked issue` block; it frequently contradicts
  or refines the SCP story's own AC. (`--no-links-deep` disables it; rarely wanted.)
- **Only the read token's reach is auto-fetched** — Jira *attachments* (images, PDFs, and videos)
  come down because the read token already unlocks them. An external link is *not* an attachment and
  the token can't download it. **Figma links are the exception now handled in-skill:** the driver lists them in
  `## Figma design links` and you open each with the Figma MCP (Step 1b) — no file is downloaded,
  you view the frame live. Other external links (Google Drive, Loom) still need separate auth and
  are left as URLs for a human; don't assume the driver pulled them.
- **Figma MCP is read-via-connector, not a download** — `get_screenshot`/`get_metadata` need the
  **claude.ai Figma** connector authenticated (`/mcp`); on a **View seat** the screenshot path
  works but `get_design_context` may be gated (and you rarely need it for a breakdown). If the
  connector is missing, mark DoR item 2 `⚠️ needs human` and leave the links as URLs — never
  silently skip a surfaced Figma link.
- **`components: ['BE']` is ambiguous** — Django vs a Java service. Always disambiguate via
  subtask prefixes (`[UM]`, `[Django]`) and keywords before fanning out.
- **Never trust tags to scope the repo list** — they're a hint, not ground truth (`BE`
  ambiguity, `PROJECTS_INDEX.md` Spring/Quarkus miscategorization, missing surfaces). The
  Step 2b fleet-wide token grep + the Step 3 agent relevance-check are the guardrails: a repo
  the tags never mentioned can still be the real owner, and a tagged component can have zero
  implementing code. Reconcile both directions every time — don't let the candidate list be
  tag-only.
- **The token is read-only** (`grooming/jira-read.txt`). You can read any issue but cannot
  create/update — sub-tasks are emitted as paste-ready text only.
- **Shadow `status` matters** — `seed`/`verified` bodies are trustworthy; on `stub`/`stale`
  trust the repo source and treat the shadow as a pointer.
- **Subtask descriptions need a second fetch** — the parent's `subtasks` array omits them;
  the driver re-fetches each one (now also pulling `status`/estimate/assignee for DoR items 9, 10, 12).
- **Mobile breaks only through backend contract drift** — `epod-ios`/`epod-android` share no
  code with the web FE; a FE-only ticket has zero mobile impact *by construction*. Don't fan out
  the two mobile agents for a pure-CSS/React change — record "no mobile-consumable surface
  touched" and move on. Conversely, never skip the check just because the ticket isn't tagged
  ePOD: a `user-backend`/`posting`/`attachment` API change can break a driver app silently.
- **The API-contract comment is usually missing** — DoR item 11 is the most common `❌`. The
  driver's `## Comments` section is the only evidence; an empty section means "not met", not "unknown".
- **Story-points field id varies** — the driver tries `customfield_10016` (Jira-Cloud default).
  If estimates show `—` everywhere but the board shows points, find the real id via
  `fetch_ticket.py <KEY> --json` and update `STORY_POINTS_FIELD` in the driver.
- **Solution/justification/tradeoffs must be grounded, not generic** — every breakdown item needs
  them (Step 4), but they're only useful if tied to the Step 3 fan-out evidence: cite the
  `file:line`/pattern the solution builds on, justify by an actual finding (an existing service to
  reuse, a contract that stays additive), and name a *real* alternative the agents surfaced. "Use
  best practices / it's the clean way" is a non-answer — if there's genuinely one extension point,
  write "no real alternative — <the reason>" rather than padding. A `Change:` with no
  solution/justification/tradeoffs is an incomplete item.
- **The `.soln` block is already styled** — render solution/justification/tradeoffs in the HTML with
  the skeleton's `<div class="soln">` + `<span class="lbl">`/`lbl why`/`lbl trade`; never add CSS for
  it. It must appear under each per-component entry so the HTML and markdown carry the same reasoning.
- **HTML: don't re-type CSS** — wrap with `wrap_html.py`; only the body fragment + SVGs are
  yours. Wide SVGs go inside `.fig-scroll` so the page never scrolls horizontally on mobile.
- **GCP log filter: `container_name` = the repo/service name, not the namespace.** Verified against
  the live fleet — `platform-backend`, `user-backend`, `cube`, `keycloak`, … all appear as
  `resource.labels.container_name`. Filter on that; the namespace (`production`) is noise. `argocd`,
  `kube-system`, `datadog-agent`, `traefik-gateway-*`, `ingress-nginx-*` are infra containers — a bare
  `severity>=ERROR` scan drowns in them, so always pin `container_name` to your service.
- **Environment = GCP project, always passed explicitly.** `shipcars-platform-{dev,qa,staging,prod}`.
  The CLI's default project is **prod**, so omitting `--project` silently queries prod — pass
  `--project=shipcars-platform-<env>` on every query so you're provably reading the intended env.
- **Payload shape: mostly `jsonPayload`, sometimes `textPayload`.** Ship.Cars services log structured
  JSON — `jsonPayload.message`, `jsonPayload.logger`, `jsonPayload.status_code`, and Datadog
  correlation keys (`jsonPayload."dd.trace_id"`, `dd.service`). Search `jsonPayload.message:"…"` for
  structured logs and `textPayload:"…"` for plain-text ones; when unsure, a bare `"…"` clause matches
  across the whole payload. Quote dotted keys: `jsonPayload."dd.trace_id"`.
- **`--freshness` (relative) vs `timestamp>=/<=` (absolute).** Use the absolute window when the bug
  cites a time; `--freshness=<N>d` otherwise. Logging retention is finite — an empty result for an old
  bug may mean the logs **aged out**, which is an open question, not "bug not reproduced."
- **The read-only guard also blocks per-line, not per-invocation.** Any mutating `gcloud`/`gsutil`/`bq`
  verb is denied, AND a whole Bash line is denied if *any* invocation in it mutates — so don't chain a
  `logging read` with a mutating command via `&&`/`;`/`|`; run reads on their own lines. If a genuine
  mutation is ever needed, the human runs it with `! gcloud …` (see `~/.claude/settings.json`).
- **Empty ≠ "not a real bug."** Before concluding a failure didn't happen, widen the window, drop the
  severity floor to `WARNING`/`DEFAULT`, re-check the `container_name` via the discovery query, and
  confirm the env — an empty set usually means wrong env/window/service, not a non-bug.
- **Never write inside `ship-cars-usa/<repo>/`** (CLAUDE.md hard rule #1). Output goes to
  `<BREAKDOWNS_DIR>/` only.

## Troubleshooting

- `HTTP 401/403 calling issue/...` → token in `grooming/jira-read.txt` is missing/expired;
  rotate it in Atlassian and re-run.
- `Could not import jira_client` → run from a shell that can read `<GROOMING_DIR>/`, or
  confirm `jira_client.py` + `jira-read.txt` exist there.
- Driver prints an issue but description is `_(empty)_` → the ticket genuinely has no body;
  flag it as "needs refinement" rather than designing from the summary alone.
- `Blocked: … is a mutating operation (read-only guard …)` on a Step 3d command → you used a mutating
  gcloud verb (or chained one into the same line). Re-issue as a pure `gcloud logging read`. This is
  the guard working as designed; never try to route around it.
- `PERMISSION_DENIED` / `caller does not have permission` on `logging.read` for a project → the account
  lacks log access in that env. Note it in the breakdown and either try a different env or leave log
  verification to a human — don't treat it as "no logs found."
- `gcloud: command not found` or no active account (`gcloud auth list` empty) → skip Step 3d entirely,
  record "GCP not available" in the breakdown, and leave log verification to a human.
- Step 3d returns nothing → widen `--freshness`, lower the severity floor, re-run the container-name
  discovery query, and re-confirm `--project`; an empty set is almost always wrong env/window/service
  or aged-out retention, not proof the bug isn't real.
