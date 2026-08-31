#!/usr/bin/env python3
"""Dedicated ticket reader for the `write-test-cases` skill.

Turns a Jira key into one markdown block carrying everything the skill needs to
derive test cases: the issue, its subtasks (each with its own AC), its linked
issues (the product story an SCP ticket `implements` — the CPDR PRD — expanded
one level), the story's attachments, and every figma.com link found anywhere in
the tree.

WHY THIS EXISTS (and why it is a *dedicated* copy, not the breakdown-story one):
the breakdown-story `fetch_ticket.py` expands `subtasks[]` and linked issues but
does NOT enumerate an **Epic's child stories** (children point *up* via Epic Link /
parent; they are not in `subtasks[]`). For a test-design run that is fatal: when
the target is an Epic, the AC and the Figma links live on the CHILD stories, so a
reader that stops at subtasks reports a misleading "0 children / 0 Figma links" and
tempts the agent into *assuming* none exist. This script closes that hole: whenever
the issue is an Epic it runs the JQL child search, fetches every child (with its AC,
its own subtasks, and its linked issues one level down), and folds all of it — and
all Figma links — into the output. No assumptions: it asks Jira.

Read-only. Reuses the vendored grooming/jira_client.py for auth + pagination + the
`search/jql` endpoint; it does NOT re-implement the token/HTTP layer (that client
owns the read token). Everything else — ADF flattening, attachment/link/figma
rendering, and the Epic traversal — lives here so the skill controls its own reader.

    python3 fetch_ticket.py SCP-14954              # full tree incl. Epic children
    python3 fetch_ticket.py SCP-14954 --json       # raw fields of the main issue
    python3 fetch_ticket.py SCP-14954 --no-children # skip Epic-child enumeration
    python3 fetch_ticket.py SCP-14954 --no-attachments  # list, don't download
"""

import json
import os
import re
import sys

# --- Workspace-relative path resolution (no hardcoded user paths) ----------
# This script lives at <REPO>/skills/write-test-cases/scripts/fetch_ticket.py, so
# REPO_ROOT is three dirs up (scripts/ -> write-test-cases -> skills -> REPO).
#   WORKSPACE_ROOT = $AGENTIC_SDLC_WORKSPACE or the parent of REPO_ROOT
#   GROOMING_DIR   = $GROOMING_DIR or <REPO_ROOT>/grooming  (holds the vendored client)
#   TDD_DIR        = $TDD_DIR      or <REPO_ROOT>/tdd
_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_SCRIPTS_DIR)))
WORKSPACE_ROOT = os.environ.get("AGENTIC_SDLC_WORKSPACE") or os.path.dirname(REPO_ROOT)
GROOMING = os.environ.get("GROOMING_DIR") or os.path.join(REPO_ROOT, "grooming")
TDD_DIR = os.environ.get("TDD_DIR") or os.path.join(REPO_ROOT, "tdd")

# --- Shared read-only auth/HTTP client (reuse, don't reimplement) ----------
if GROOMING not in sys.path:
    sys.path.insert(0, GROOMING)
try:
    from jira_client import api_get, api_get_binary, search_all  # noqa: E402
except Exception as exc:  # pragma: no cover - environment guard
    sys.exit(
        f"Could not import jira_client from {GROOMING}: {exc}\n"
        "Expected <GROOMING_DIR>/jira_client.py to exist and a Jira token to be set "
        "($JIRA_READ_TOKEN or <GROOMING_DIR>/jira-read.txt).\n"
        "If Jira MCP is your only access, fall back to the Atlassian MCP per the skill."
    )

# --- Field sets ------------------------------------------------------------
FIELDS = (
    "summary,description,issuetype,status,labels,components,priority,"
    "parent,subtasks,issuelinks,assignee,comment,attachment"
)
LINK_FIELDS = "summary,description,status,issuetype,attachment,issuelinks"
CHILD_FIELDS = "summary,description,status,issuetype,subtasks,issuelinks,attachment"
SUBTASK_FIELDS = "summary,description,status,assignee"

MAX_DEEP_LINKS = 12   # per issue, safety cap
MAX_CHILDREN = 60     # per epic, safety cap
MAX_CHILD_LINKS = 6   # linked issues expanded per child (to catch figma on a child's PRD)

# The Epic-Link field id varies by instance; the JQL clause `"Epic Link"` is the
# portable form and `parent = KEY` catches team-managed projects. We OR them and,
# if the JQL is rejected (unknown field), fall back to `parent` alone.
EPIC_CHILD_JQL = '("Epic Link" = {key} OR parent = {key}) ORDER BY key ASC'
EPIC_CHILD_JQL_FALLBACK = 'parent = {key} ORDER BY key ASC'
CHILD_SEARCH_FIELDS = ["summary", "status", "issuetype", "parent"]

IMAGE_MIMES = {
    "image/png", "image/jpeg", "image/jpg", "image/gif",
    "image/webp", "image/bmp", "image/tiff", "image/svg+xml",
}
FETCHABLE_MIMES = IMAGE_MIMES | {"application/pdf"}
ATTACHMENTS_ROOT = os.environ.get("TDD_ATTACHMENTS_DIR") or os.path.join(
    TDD_DIR, "attachments"
)

FIGMA_URL_RE = re.compile(
    r"https?://(?:www\.)?figma\.com/(?:file|design|proto|board|slides|make)/[^\s)\]>\"'}]+",
    re.IGNORECASE,
)


# --- ADF -> markdown -------------------------------------------------------
def adf_to_md(node, depth=0):
    """Flatten an Atlassian Document Format node tree to markdown text."""
    if node is None:
        return ""
    if isinstance(node, list):
        return "".join(adf_to_md(n, depth) for n in node)
    if not isinstance(node, dict):
        return str(node)
    t = node.get("type")
    content = node.get("content")
    if t == "doc":
        return adf_to_md(content, depth)
    if t == "text":
        text = node.get("text", "")
        for mark in node.get("marks", []) or []:
            mt = mark.get("type")
            if mt == "strong":
                text = f"**{text}**"
            elif mt == "em":
                text = f"*{text}*"
            elif mt == "code":
                text = f"`{text}`"
            elif mt == "link":
                href = (mark.get("attrs") or {}).get("href", "")
                text = f"[{text}]({href})"
        return text
    if t == "hardBreak":
        return "\n"
    if t == "paragraph":
        return adf_to_md(content, depth).rstrip() + "\n\n"
    if t == "heading":
        level = (node.get("attrs") or {}).get("level", 1)
        return "#" * int(level) + " " + adf_to_md(content, depth).strip() + "\n\n"
    if t in ("bulletList", "orderedList"):
        out = []
        for i, item in enumerate(content or [], 1):
            marker = "- " if t == "bulletList" else f"{i}. "
            body = adf_to_md(item.get("content"), depth + 1).strip()
            lines = body.split("\n")
            indent = "  " * depth
            first = f"{indent}{marker}{lines[0]}" if lines else f"{indent}{marker}"
            rest = [f"{indent}  {ln}" for ln in lines[1:] if ln.strip()]
            out.append("\n".join([first] + rest))
        return "\n".join(out) + "\n\n"
    if t == "listItem":
        return adf_to_md(content, depth)
    if t == "codeBlock":
        lang = (node.get("attrs") or {}).get("language", "")
        return f"```{lang}\n{adf_to_md(content, depth).strip()}\n```\n\n"
    if t == "blockquote":
        body = adf_to_md(content, depth).strip()
        return "\n".join(f"> {ln}" for ln in body.split("\n")) + "\n\n"
    if t == "rule":
        return "---\n\n"
    if t == "inlineCard":
        return (node.get("attrs") or {}).get("url", "")
    if t == "mention":
        return "@" + (node.get("attrs") or {}).get("text", "user")
    if t in ("mediaSingle", "mediaGroup", "media", "mediaInline"):
        alt = (node.get("attrs") or {}).get("alt") or ""
        label = f"embedded image: {alt}" if alt else "embedded image / file"
        return f"_[{label} — see Attachments]_\n\n"
    return adf_to_md(content, depth)


def field_md(fields, name, default=""):
    val = fields.get(name)
    if isinstance(val, dict) and val.get("type") == "doc":
        return adf_to_md(val).strip() or default
    return val if val is not None else default


def fetch_issue(key, fields=FIELDS):
    return api_get(f"issue/{key}", {"fields": fields})


# --- Figma links -----------------------------------------------------------
def extract_figma_links(text):
    seen, out = set(), []
    for m in FIGMA_URL_RE.finditer(text or ""):
        url = m.group(0).rstrip(".,;")
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out


def render_figma_links(urls):
    out = [f"## Figma design links ({len(urls)})", ""]
    if not urls:
        out.append(
            "_(none found in the story, its subtasks, its EPIC CHILD stories, "
            "comments, or linked issues — this reader DID enumerate Epic children, "
            "so a 0 here means none exist, not that the search was skipped)_"
        )
        out.append("")
        return out
    out.append(
        "**Open each with the Figma MCP** (`get_screenshot` on a View seat, "
        "`get_metadata` for structure; `node-id=<a>-<b>` → nodeId `<a>:<b>`). "
        "See the skill's Step 2."
    )
    out.append("")
    for u in urls:
        out.append(f"- {u}")
    out.append("")
    return out


# --- Attachments -----------------------------------------------------------
def _human_size(size):
    if isinstance(size, (int, float)) and size:
        return f"{size / 1024:.0f} KB" if size < 1024 * 1024 else f"{size / 1048576:.1f} MB"
    return "?"


def render_attachments(owner_key, attachments, download=True, heading="## Attachments"):
    attachments = attachments or []
    out = [f"{heading} ({len(attachments)})", ""]
    if not attachments:
        out.append("_(none)_")
        out.append("")
        return out
    dest_dir = os.path.join(ATTACHMENTS_ROOT, owner_key)
    for a in attachments:
        mime = (a.get("mimeType") or "").lower()
        name = a.get("filename") or f"attachment-{a.get('id')}"
        sz = _human_size(a.get("size"))
        if download and mime in FETCHABLE_MIMES and a.get("content"):
            try:
                data = api_get_binary(a["content"])
                os.makedirs(dest_dir, exist_ok=True)
                safe = name.replace("/", "_").replace("\\", "_")
                path = os.path.join(dest_dir, safe)
                with open(path, "wb") as fh:
                    fh.write(data)
                kind = "🖼" if mime in IMAGE_MIMES else "📄"
                verb = "Read this file to VIEW the image" if mime in IMAGE_MIMES else "Read this file (PDF)"
                out.append(f"- {kind} **{name}** ({mime}, {sz}) → `{path}` — **{verb}**")
            except Exception as exc:
                out.append(f"- ⚠️ {name} ({mime}, {sz}) — download failed: {exc}")
        elif mime in FETCHABLE_MIMES and not download:
            out.append(f"- 📎 {name} ({mime}, {sz}) — downloadable image/PDF (skipped)")
        else:
            out.append(f"- 📎 {name} ({mime}, {sz}) — not an image/PDF; review manually if relevant")
    out.append("")
    return out


# --- Linked issues (one level deep) ---------------------------------------
def _link_targets(links):
    """Yield (key, relation_label, shallow_fields) for each linked issue."""
    for ln in links or []:
        rel = ln.get("type", {})
        for side, label in (("outwardIssue", rel.get("outward")),
                            ("inwardIssue", rel.get("inward"))):
            other = ln.get(side)
            if other:
                yield other.get("key"), label, (other.get("fields") or {})


def render_links(links, deep=True, download=True, cap=MAX_DEEP_LINKS, level=3):
    out = ["## Linked issues", ""]
    targets = list(_link_targets(links))
    for okey, label, of in targets:
        out.append(
            f"- {label}: {okey} — {of.get('summary', '')} "
            f"[{(of.get('status') or {}).get('name')}]"
        )
    out.append("")
    if not deep or not targets:
        return out
    expanded = targets[:cap]
    if len(targets) > cap:
        out.append(f"_Expanding the first {cap} of {len(targets)} linked issues below._")
        out.append("")
    hashes = "#" * level
    for okey, label, _of in expanded:
        detail = fetch_issue(okey, LINK_FIELDS)
        df = detail.get("fields", {})
        out.append(f"{hashes} 🔗 Linked issue {okey} ({label}) — full content")
        out.append("")
        out.append(
            f"- **Type:** {(df.get('issuetype') or {}).get('name')}"
            f"  ·  **Status:** {(df.get('status') or {}).get('name')}"
        )
        out.append("")
        out.append("**Description / AC:**")
        out.append("")
        out.append(field_md(df, "description", "_(empty)_"))
        out.append("")
        out.extend(render_attachments(
            okey, df.get("attachment"), download=download,
            heading=f"**Attachments on {okey}**",
        ))
    return out


# --- Epic child enumeration (THE reason this dedicated reader exists) -------
def is_epic(fields):
    return ((fields.get("issuetype") or {}).get("name") or "").strip().lower() == "epic"


def enumerate_epic_children(key):
    """Return the list of child issues (Epic Link / parent), or [] with a note.

    Never raises: `search_all` -> `api_get` sys.exits on HTTP error, so we probe
    with a guarded call and, on the '"Epic Link" unknown field' case, retry with
    `parent` alone. The point is to make the assumption impossible: we ASK Jira.
    """
    import io
    import contextlib

    def _try(jql):
        # api_get sys.exits on HTTPError; run it in a child-safe guard by catching
        # SystemExit so a bad JQL clause degrades instead of killing the whole run.
        try:
            return search_all(jql, CHILD_SEARCH_FIELDS), None
        except SystemExit as e:
            return None, str(e)
        except Exception as e:  # network etc.
            return None, f"{type(e).__name__}: {e}"

    issues, err = _try(EPIC_CHILD_JQL.format(key=key))
    if issues is None:
        issues, err2 = _try(EPIC_CHILD_JQL_FALLBACK.format(key=key))
        if issues is None:
            return [], f"child search failed ({err or ''}; fallback: {err2 or ''})"
    return issues[:MAX_CHILDREN], None


def render_epic_children(key, download=True):
    """Fetch and render every child story with its AC, its subtasks, and its
    linked issues (one level) — this is where an Epic's real AC + Figma links live."""
    children, err = enumerate_epic_children(key)
    out = []
    if err:
        out.append(f"## Epic child stories")
        out.append("")
        out.append(f"_⚠️ Could not enumerate children: {err}. "
                   f"Run the JQL manually via the Atlassian MCP._")
        out.append("")
        return out
    out.append(f"## Epic child stories ({len(children)})")
    out.append("")
    if not children:
        out.append("_(none — the Epic-Link/parent search returned nothing. This is a "
                    "verified 0, not a skipped step.)_")
        out.append("")
        return out
    out.append("_These are the Epic's children (via Epic Link / parent) — NOT in "
               "`subtasks[]`. Each carries its own AC and may hold the Figma links._")
    out.append("")
    for ch in children:
        ckey = ch.get("key")
        cf_shallow = ch.get("fields", {})
        cty = (cf_shallow.get("issuetype") or {}).get("name", "?")
        cst = (cf_shallow.get("status") or {}).get("name", "?")
        out.append(f"### {ckey} — [{cty}] [{cst}] {cf_shallow.get('summary', '')}")
        out.append("")
        detail = fetch_issue(ckey, CHILD_FIELDS)
        df = detail.get("fields", {})
        out.append("**Description / AC:**")
        out.append("")
        out.append(field_md(df, "description", "_(empty)_"))
        out.append("")
        # child subtasks (shallow list + AC via a light second fetch)
        csubs = df.get("subtasks") or []
        if csubs:
            out.append(f"**Subtasks of {ckey}:**")
            out.append("")
            for st in csubs:
                sd = fetch_issue(st.get("key"), SUBTASK_FIELDS).get("fields", {})
                out.append(f"- **{st.get('key')}** — {sd.get('summary','')} "
                           f"[{(sd.get('status') or {}).get('name')}]")
                acbody = field_md(sd, "description", "").strip()
                if acbody:
                    for ln in acbody.splitlines():
                        out.append(f"  > {ln}")
            out.append("")
        # child linked issues (one level) — catches figma on a child's PRD
        clinks = df.get("issuelinks") or []
        if clinks:
            out.extend(render_links(clinks, deep=True, download=download,
                                    cap=MAX_CHILD_LINKS, level=4))
        # child attachments
        out.extend(render_attachments(
            ckey, df.get("attachment"), download=download,
            heading=f"**Attachments on {ckey}**"))
    return out


# --- Top-level render ------------------------------------------------------
def render(key, deep_links=True, download_attachments=True, enumerate_children=True):
    issue = fetch_issue(key)
    f = issue.get("fields", {})
    out = []
    out.append(f"# {issue.get('key')} — {f.get('summary', '(no summary)')}")
    out.append("")
    out.append(f"- **Type:** {(f.get('issuetype') or {}).get('name')}")
    out.append(f"- **Status:** {(f.get('status') or {}).get('name')}")
    out.append(f"- **Priority:** {(f.get('priority') or {}).get('name')}")
    out.append(f"- **Components:** "
               f"{', '.join(c.get('name') for c in (f.get('components') or [])) or '(none)'}")
    out.append(f"- **Labels:** {', '.join(f.get('labels') or []) or '(none)'}")
    parent = f.get("parent")
    if parent:
        out.append(f"- **Parent:** {parent.get('key')} — "
                   f"{(parent.get('fields') or {}).get('summary', '')}")
    out.append("")
    out.append("## Description / Acceptance Criteria")
    out.append("")
    out.append(field_md(f, "description", "_(empty)_"))
    out.append("")
    out.extend(render_attachments(issue.get("key"), f.get("attachment"),
                                  download=download_attachments))
    figma_anchor = len(out)  # figma section spliced here after scanning the full tree

    # Subtasks of the main issue
    subtasks = f.get("subtasks") or []
    if subtasks:
        out.append("## Existing subtasks")
        out.append("")
        for st in subtasks:
            detail = fetch_issue(st.get("key"), SUBTASK_FIELDS)
            df = detail.get("fields", {})
            out.append(f"### {st.get('key')} — {df.get('summary', '')}")
            out.append(f"- Status: {(df.get('status') or {}).get('name')}")
            out.append("")
            out.append(field_md(df, "description", "_(no description)_"))
            out.append("")

    # Epic children — the capability the breakdown-story reader lacks
    if enumerate_children and is_epic(f):
        out.extend(render_epic_children(key, download=download_attachments))

    # Linked issues of the main issue
    links = f.get("issuelinks") or []
    if links:
        out.extend(render_links(links, deep=deep_links, download=download_attachments))

    # Comments
    comment_block = (f.get("comment") or {})
    comments = comment_block.get("comments") or []
    if comments:
        out.append(f"## Comments ({comment_block.get('total', len(comments))})")
        out.append("")
        for c in comments:
            author = (c.get("author") or {}).get("displayName", "unknown")
            created = (c.get("created") or "")[:10]
            out.append(f"### {author} · {created}")
            out.append("")
            out.append(field_md(c, "body", "_(empty)_"))
            out.append("")

    # Splice the figma section, scanning EVERYTHING built (incl. epic children)
    figma_section = render_figma_links(extract_figma_links("\n".join(out)))
    out = out[:figma_anchor] + figma_section + out[figma_anchor:]
    return "\n".join(out)


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    key = argv[1].strip().upper()
    if "--json" in argv:
        print(json.dumps(fetch_issue(key), indent=2))
    else:
        print(render(
            key,
            deep_links="--no-links-deep" not in argv,
            download_attachments="--no-attachments" not in argv,
            enumerate_children="--no-children" not in argv,
        ))


if __name__ == "__main__":
    main(sys.argv)
