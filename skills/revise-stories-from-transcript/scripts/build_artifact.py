#!/usr/bin/env python3
"""Staple a body fragment + metadata into the shared story-revisions template.

The template (`assets/artifact_template.html`) owns everything that must stay
constant across every run: the light "ledger" palette + full CSS, the header
scaffold, the legend, the "editable / copy" intro note, and the trailing
copy-to-clipboard + contenteditable <script>. It is a byte-for-byte lift of the
first shipped artifact, so every page this skill produces looks identical to it.

You author only the BODY — the "At a glance" table through the open-questions
register — plus a small META json for the header text. This script fills the
placeholders and inserts the body at the `<!-- BODY -->` marker.

    python3 build_artifact.py BODY.html META.json OUT.html

META.json (all strings; HTML allowed in `lede`, `meta`, `foot`):
    {
      "title":   "Faster Payments — Story Revisions",              # browser tab / gallery name
      "eyebrow": "Grooming review · Epic SCP-14954",
      "h1":      "Faster Payments — Story Revisions from the Call",
      "lede":    "How the <date> call changes the epic's N child stories: ...",
      "meta":    "Source: <span>...</span> · Epic: <a href=...>SCP-14954</a> · PRD: <a ...>CPDR-436</a>",
      "foot":    "Draft — no Jira issues were modified. ..."
    }

The body fragment is inserted verbatim; it may contain the .card / .pill / .jira
markup documented in references/artifact-format.md. Do NOT include <title>,
<style>, <script>, the header, the legend, or the foot — the template owns those.
The output is ready to hand to the Artifact tool (no <!doctype>/<head>/<body>).
"""

import json
import os
import sys

TEMPLATE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "assets", "artifact_template.html")

DEFAULTS = {
    "title": "Story Revisions",
    "eyebrow": "Grooming review",
    "h1": "Story Revisions from the Transcript",
    "lede": "",
    "meta": "",
    "foot": "Draft — no Jira issues were modified. Verify quotes against the live tickets before pasting.",
}


def main(argv):
    if len(argv) < 4:
        sys.exit(__doc__)
    body_path, meta_path, out_path = argv[1], argv[2], argv[3]

    with open(TEMPLATE, encoding="utf-8") as fh:
        tpl = fh.read()
    with open(body_path, encoding="utf-8") as fh:
        body = fh.read()
    with open(meta_path, encoding="utf-8") as fh:
        meta = json.load(fh)

    for key, default in DEFAULTS.items():
        tpl = tpl.replace("{{" + key.upper() + "}}", str(meta.get(key, default)))
    tpl = tpl.replace("<!-- BODY -->", body)

    leftover = [p for p in ("{{TITLE}}", "{{EYEBROW}}", "{{H1}}", "{{LEDE}}", "{{META}}", "{{FOOT}}")
                if p in tpl]
    if leftover:
        sys.stderr.write(f"warning: unfilled placeholders remain: {leftover}\n")

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(tpl)
    sys.stderr.write(f"wrote {out_path} ({len(tpl)} bytes)\n")


if __name__ == "__main__":
    main(sys.argv)
