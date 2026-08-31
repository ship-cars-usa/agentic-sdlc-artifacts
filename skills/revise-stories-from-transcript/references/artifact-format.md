# Artifact body format

The template (`assets/artifact_template.html`) owns the `<title>`, the full CSS,
the header (eyebrow/H1/lede/meta), the legend, the "editable / copy" note, the
foot, and the copy-to-clipboard `<script>`. **You author only the BODY** — the
fragment inserted at `<!-- BODY -->` — using the classes below, then run
`build_artifact.py`. Do not restyle anything; the look must stay identical to the
first shipped artifact.

## Section order (top to bottom)

1. `## At a glance` — a summary table of every finding.
2. `## Requirement changes across many stories` — the cross-cutting findings (F1, F2, …), each stated once.
3. `## Per-story revisions` — one card per child story.
4. `## New stories the call raises` — proposed-story cards for needs with no story.
5. `## Figma design gaps & changes` — design decisions/defects + a missing-design table.
6. `## Full list of open questions` — the consolidated register with owners.

(Headings are plain `<h2 class="anchor" id="...">`. The foot is added by the template.)

## Colour semantics (already in CSS — just use the classes)

- `change` (rust) = **requirement change / conflict / defect** — the call contradicts, narrows, or breaks a current AC/design.
- `open` (amber) = **open question** — undecided; needs an owner before the story is Ready.
- `new` (blue) = **net-new** — a surfaced need with no story yet.
- `key` (grey) = a Jira key chip.

## Building blocks (copy these patterns)

### Summary table
```html
<div class="tablewrap"><table>
  <thead><tr><th>#</th><th>Theme</th><th>Type</th><th>Stories affected</th></tr></thead>
  <tbody>
    <tr><td class="k">1</td><td>Short theme sentence</td>
        <td><span class="pill change">Change</span></td>
        <td class="k">14968, 14971</td></tr>
  </tbody>
</table></div>
```

### Cross-cutting finding card (anchor id `f1`, `f2`, … so per-story cards can link to it)
```html
<div class="card anchor" id="f1">
  <div class="card-hd"><div class="t">
    <div class="tags"><span class="pill change"><span class="dot change"></span>Finding 1 · Requirement change</span></div>
    <h3>One-line finding headline</h3>
  </div></div>
  <div class="card-bd">
    <p class="affects">Affects: <a href="https://shipcars.atlassian.net/browse/SCP-14968">14968</a>, …</p>
    <div class="block">
      <div class="lbl">From the transcript</div>
      <div class="transcript">
        <p style="margin:0 0 8px"><span class="ts">24:13</span> <b>Janet:</b> "verbatim quote…"</p>
      </div>
    </div>
    <div class="block">
      <div class="lbl">Why it matters</div>
      <p style="margin:0;font-size:14px;color:var(--muted)">Explanation.</p>
    </div>
    <div class="block">
      <div class="lbl"><span class="dot change"></span>Suggested change</div>
      <div class="change-txt">The concrete change to make.</div>
    </div>
  </div>
</div>
```

### Per-story card — the core deliverable unit
Every per-story card MUST carry: (1) the story **link**, (2) a **verbatim quote**
of the current story text, (3) a **suggested revision**, (4) a **paste-ready**
`.jira` block.
```html
<div class="card anchor" id="s14968">
  <div class="card-hd">
    <div class="t">
      <div class="tags"><span class="pill key">SCP-14968</span>
        <span class="pill change"><span class="dot change"></span>F1, F3</span>
        <span class="pill open"><span class="dot open"></span>F2</span></div>
      <h3>Story summary</h3>
    </div>
    <a href="https://shipcars.atlassian.net/browse/SCP-14968">open ↗</a>
  </div>
  <div class="card-bd">
    <div class="block">
      <div class="lbl">Current AC (quote)</div>
      <blockquote>"Verbatim text from the story — do not paraphrase."</blockquote>
    </div>
    <div class="block">
      <div class="lbl"><span class="dot change"></span>Suggested revision</div>
      <ul class="tight"><li>Point, linking findings like <a href="#f1">F1</a>.</li></ul>
    </div>
    <div class="jira">
      <div class="cap">Paste into story — comment</div>
      <pre>NOTE (YYYY-MM-DD call): concrete, paste-ready revision text…</pre>
    </div>
  </div>
</div>
```

### Net-new story card
Same shell, `<span class="pill new"><span class="dot new"></span>Proposed story</span>`,
a `From the transcript` block, a `Why it's new` block, and a `.jira` block whose
`<pre>` is a full draft: `Title:`, user story, `Draft AC:`, `OPEN QUESTIONS:`.

### Figma section
Open with a `<p class="note">` (frames reviewed) and a `<div class="callout" style="border-left-color:var(--change)">` summarising the headline design tension. Then one `card` per decision/defect (same shell as a finding card, `<h3>` + a `<p>`/`<ul class="tight">`), then a **missing-design table**:
```html
<div class="tablewrap"><table>
  <thead><tr><th>Surface</th><th>Present</th><th>Missing / gap</th></tr></thead>
  <tbody><tr><td class="k">Order Details<br>14971</td><td>…</td><td>…</td></tr></tbody>
</table></div>
```

### Open-questions register
```html
<div class="tablewrap"><table>
  <thead><tr><th>Open question</th><th>Suggested owner</th><th>Blocks</th></tr></thead>
  <tbody><tr><td>Question</td><td>Owner</td><td class="k">14968, 14971</td></tr></tbody>
</table></div>
```

## Rules

- **Quotes are verbatim.** Transcript lines keep their speaker + `mm:ss` timestamp inside `.transcript`; story text goes in a `<blockquote>`. Never paraphrase inside a quote.
- **Every `<pre>` is what the user pastes into Jira.** Keep it self-contained and accurate; it becomes editable + copyable automatically (the template's script wires every `.jira` block).
- **Cross-cutting findings are stated once** in section 2 and linked (`<a href="#f1">`) from the per-story cards — don't repeat the evidence.
- Wide content (tables) always sits inside `<div class="tablewrap">`.
- Do not add `<style>`/`<script>`/`<title>` to the body — the template owns them.
