#!/usr/bin/env python3
"""Wrap an Opus-authored HTML body fragment in the shared breakdown skeleton.

The skeleton (`assets/html_skeleton.html`) owns all the boilerplate — the dark
palette, the CSS, the `header.doc`/chips scaffold, the footer frame. You author
only the *body*: the prose sections and the bespoke inline SVG diagrams. This
script staples them together so the ~90 lines of CSS are never re-typed and every
breakdown page looks identical.

    python3 wrap_html.py BODY_FRAGMENT.html META.json > <BREAKDOWNS_DIR>/<KEY>.html

META.json shape (all keys optional except title/h1):
    {
      "title":    "SCP-14523 — Breakdown & Design",   # browser tab
      "h1":       "SCP-14523 — Breakdown & Design",
      "subtitle": "[Carrier Risk] Stat Cards · Story · Priority: Pending",
      "chips":    [ {"text":"Story"},
                    {"text":"surface: loadboard-frontend", "cls":"surf"},
                    {"text":"mobile: not affected",        "cls":"mob"} ],
      "footer":   "Driver: <code>...</code><br><em>Breakdown by ...</em>"
    }

chip `cls` is one of: "" (default blue), "surf" (green), "bug" (red), "mob"
(purple) — matches the skeleton's CSS. The body fragment is inserted verbatim at
the `<!-- BODY -->` marker, so it may contain <h2>, tables, .fig/.svg, .pill, etc.
No external assets: everything is inline, CSP-safe, self-contained.
"""

import html
import json
import os
import sys

SKEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "html_skeleton.html")


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
    title = meta.get("title") or meta.get("h1") or "Breakdown & Design"
    repl = {
        "{{TITLE}}": html.escape(title),
        "{{H1}}": html.escape(meta.get("h1") or title),
        "{{SUBTITLE}}": meta.get("subtitle", ""),   # may contain inline markup
        "{{CHIPS}}": render_chips(meta.get("chips")),
        "{{FOOTER}}": meta.get("footer", ""),
    }
    for k, v in repl.items():
        skel = skel.replace(k, v)
    return skel.replace("<!-- BODY -->", body)


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    with open(argv[1], encoding="utf-8") as fh:
        body = fh.read()
    with open(argv[2], encoding="utf-8") as fh:
        meta = json.load(fh)
    sys.stdout.write(build(body, meta))


if __name__ == "__main__":
    main(sys.argv)
