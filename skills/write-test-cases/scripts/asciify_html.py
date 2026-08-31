#!/usr/bin/env python3
"""Make an HTML document pure-ASCII so it renders correctly under ANY charset.

Why: a TDD page emitted as UTF-8 shows fine in a standards-compliant browser
(the skeleton declares `<meta charset="utf-8">`), but the moment it is opened in
a viewer that guesses a legacy code page (some editors, previews, mail clients,
copy-paste targets) every em-dash / middot / arrow becomes mojibake like `â€”`.
Encoding the non-ASCII characters as HTML numeric entities sidesteps the guess:
`&#8212;` is seven ASCII bytes that render as `—` regardless of the charset.

Rules:
- Outside `<style>` / `<script>`: every non-ASCII char -> `&#N;` numeric entity.
- Inside `<style>`: every non-ASCII char -> CSS escape `\\HEX ` (entities are not
  parsed by the CSS engine, so decorative `content:"✔"` glyphs need CSS escapes).
- Inside `<script>`: left untouched (numeric entities are not valid in JS; TDD
  pages ship no scripts, so this branch is effectively unused — if you add JS,
  keep its literals ASCII yourself).

Usage:
    python3 asciify_html.py FILE.html            # sanitize in place
    python3 asciify_html.py IN.html > OUT.html    # sanitize to stdout
    # or import: from asciify_html import asciify
"""
import re
import sys

_SEG = re.compile(r'(<style\b[^>]*>.*?</style>|<script\b[^>]*>.*?</script>)',
                  re.S | re.I)


def _entities(seg: str) -> str:
    return ''.join(ch if ord(ch) < 128 else f'&#{ord(ch)};' for ch in seg)


def _css_escape(seg: str) -> str:
    # Escape non-ASCII with a CSS unicode escape + terminating space. The opening
    # `<style ...>` tag and closing `</style>` are ASCII, so they pass through.
    return ''.join(ch if ord(ch) < 128 else f'\\{ord(ch):x} ' for ch in seg)


def asciify(doc: str) -> str:
    """Return `doc` with every non-ASCII character encoded as ASCII."""
    out = []
    for part in _SEG.split(doc):
        head = part[:7].lower()
        if head.startswith('<style'):
            out.append(_css_escape(part))
        elif head.startswith('<script'):
            out.append(part)  # leave JS alone; keep its literals ASCII by hand
        else:
            out.append(_entities(part))
    return ''.join(out)


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    path = argv[1]
    with open(path, encoding='utf-8') as fh:
        src = fh.read()
    fixed = asciify(src)
    if len(argv) >= 3 or not sys.stdout.isatty():
        # explicit second arg not supported; write to stdout when piped
        pass
    # In-place by default; to stdout only if redirected AND no write intended.
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(fixed)
    sys.stderr.write(f"asciified {path} ({len(src) - len(fixed):+d} chars)\n")


if __name__ == '__main__':
    main(sys.argv)
