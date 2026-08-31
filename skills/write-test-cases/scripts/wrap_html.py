#!/usr/bin/env python3
"""Wrap an authored HTML body fragment in the shared Test-Design-Document skeleton.

The skeleton (`../assets/html_skeleton.html`) owns all the boilerplate — the
light-first, card-based, theme-aware palette (matching the Step-8 mockups look),
the CSS, the header/chips scaffold, the footer frame, and every pill /
open-question style. You author only the *body*: the summary, the test-case
tables, the edge-case section, the open-questions callouts, and any inline SVG.
This script staples them together so the CSS is never re-typed and every TDD page
looks identical.

    python3 wrap_html.py BODY_FRAGMENT.html META.json > <TDD_DIR>/<KEY>.html

META.json shape (all keys optional except title/h1):
    {
      "title":    "SCP-14292 — Test Design Document",   # browser tab
      "h1":       "SCP-14292 — Test Design Document",
      "subtitle": "MFA phone change · Story · 23 cases · 4 open questions",
      "chips":    [ {"text":"Story"},
                    {"text":"42 test cases",  "cls":"qa"},
                    {"text":"7 edge cases",   "cls":"edge"},
                    {"text":"4 open questions","cls":"oq"} ],
      "footer":   "Sources: Jira <code>SCP-14292</code> · Figma · repos<br><em>Authored by ...</em>"
    }

chip `cls` is one of: "" (default blue), "qa" (teal), "edge" (amber),
"oq" (red), "surf" (green) — matches the skeleton's CSS. The body fragment is
inserted verbatim at the `<!-- BODY -->` marker, so it may contain <h2>, tables,
.pill, .oq, .fig/.svg, etc. No external assets: everything is inline, CSP-safe,
self-contained.
"""

import html
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from asciify_html import asciify  # noqa: E402

SKEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "html_skeleton.html")


def render_chips(chips):
    out = []
    for c in chips or []:
        cls = c.get("cls", "").strip()
        klass = f"chip {cls}".strip()
        out.append(f'    <span class="{klass}">{html.escape(c.get("text", ""))}</span>')
    return "\n".join(out)


def build(body, meta):
    with open(SKEL, encoding="utf-8") as fh:
        skel = fh.read()
    title = meta.get("title") or meta.get("h1") or "Test Design Document"
    repl = {
        "{{TITLE}}": html.escape(title),
        "{{H1}}": html.escape(meta.get("h1") or title),
        "{{SUBTITLE}}": meta.get("subtitle", ""),   # may contain inline markup
        "{{CHIPS}}": render_chips(meta.get("chips")),
        "{{FOOTER}}": meta.get("footer", ""),
    }
    for k, v in repl.items():
        skel = skel.replace(k, v)
    # Emit pure-ASCII HTML (numeric entities outside <style>, CSS escapes inside)
    # so the page renders identically even in viewers that mis-guess the charset.
    return asciify(skel.replace("<!-- BODY -->", body))


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    with open(argv[1], encoding="utf-8") as fh:
        body = fh.read()
    with open(argv[2], encoding="utf-8") as fh:
        meta = json.load(fh)
    # Force UTF-8 on stdout so the redirected file is well-formed regardless of
    # the ambient locale (the output is ASCII anyway after asciify(), but this
    # guards any stray char and non-UTF-8 LC_* environments).
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    sys.stdout.write(build(body, meta))


if __name__ == "__main__":
    main(sys.argv)
