#!/usr/bin/env python3
"""Driver for the `revise-stories-from-transcript` skill.

Turns an epic key (e.g. SCP-14954) into one clean markdown block the skill reads
to compare against a meeting/call transcript:

  * the EPIC (summary, status, description, and the product issue it `implements`)
  * that linked PRD / product issue, expanded one level (its full description)
  * every CHILD story (parent = <EPIC>): status, labels, description (ADF
    flattened, with link + inline-card URLs preserved), issue links (clone /
    cloned-by), and comments
  * each story's SUBTASKS (one level deeper), expanded with their own description
    + labels — so a story that has already been broken down is not analysed as a
    black box
  * a consolidated `## Figma design links` section — every figma.com URL found
    ANYWHERE (epic, PRD, each story's description AND comments, and subtasks),
    tagged with the issue it came from (the skill opens each via the Figma MCP)

Read-only against Jira. Reuses the skill-local jira_client.py (secret-free token
discovery); creates no files.

    python3 fetch_epic.py SCP-14954
    python3 fetch_epic.py SCP-14954 --json        # raw fields, for scripting
    python3 fetch_epic.py SCP-14954 --no-comments # skip comment bodies
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from jira_client import api_get, search_all, SITE  # noqa: E402

CHILD_FIELDS = "summary,status,issuetype,description,labels,issuelinks,comment,subtasks"
SUB_FIELDS = "summary,status,issuetype,description,labels,issuelinks"
MAX_SUBTASKS = 30  # per story; guards a pathological breakdown
FIGMA_RE = re.compile(r"https?://[^\s\"'<>\]\)]*figma\.com[^\s\"'<>\]\)]*")


def adf_to_text(node, out):
    """Flatten an ADF (Atlassian Document Format) node to text, preserving the
    URLs that carry the design/product references we must not lose."""
    if node is None:
        return
    if isinstance(node, list):
        for n in node:
            adf_to_text(n, out)
        return
    t = node.get("type")
    if t == "text":
        out.append(node.get("text", ""))
        for m in node.get("marks", []) or []:
            if m.get("type") == "link":
                href = (m.get("attrs") or {}).get("href")
                if href:
                    out.append(f" [link: {href}] ")
    if t in ("inlineCard", "blockCard", "embedCard"):
        url = (node.get("attrs") or {}).get("url")
        if url:
            out.append(f" [card: {url}] ")
    if t in ("media", "mediaSingle", "mediaGroup"):
        out.append(" [image/attachment] ")
    for child in node.get("content", []) or []:
        adf_to_text(child, out)
    if t in ("paragraph", "heading", "listItem", "tableRow", "blockquote"):
        out.append("\n")


def flat(adf):
    out = []
    adf_to_text(adf, out)
    # collapse runs of blank lines
    return re.sub(r"\n{3,}", "\n\n", "".join(out)).strip()


def figma_urls(text):
    # de-dupe while preserving order
    seen, urls = set(), []
    for u in FIGMA_RE.findall(text or ""):
        u = u.rstrip(".,);]")
        if u not in seen:
            seen.add(u)
            urls.append(u)
    return urls


def issue_links(fields):
    rows = []
    for lk in fields.get("issuelinks") or []:
        other = lk.get("outwardIssue") or lk.get("inwardIssue")
        if not other:
            continue
        rel = (lk["type"]["outward"] if lk.get("outwardIssue") else lk["type"]["inward"])
        rows.append((rel, other["key"], other["fields"]["summary"]))
    return rows


def comments(fields, include):
    if not include:
        return []
    out = []
    for c in (fields.get("comment") or {}).get("comments", []) or []:
        out.append((c["author"]["displayName"], c["created"][:10], flat(c.get("body"))))
    return out


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    if not args:
        sys.exit(__doc__)
    epic_key = args[0].upper()
    want_json = "--json" in flags
    want_comments = "--no-comments" not in flags

    epic = api_get(f"issue/{epic_key}", {"fields": "summary,status,issuetype,description,issuelinks,labels"})
    ef = epic["fields"]
    epic_desc = flat(ef.get("description"))

    # The product issue the epic "implements" (the PRD) — expand it one level.
    prd = None
    for rel, key, summ in issue_links(ef):
        if rel.lower() in ("implements", "is implemented by") or key.split("-")[0] != epic_key.split("-")[0]:
            try:
                p = api_get(f"issue/{key}", {"fields": "summary,status,description"})
                prd = (key, p["fields"]["summary"], p["fields"]["status"]["name"], flat(p["fields"].get("description")))
                break
            except SystemExit:
                pass

    kids = search_all(f"parent = {epic_key} ORDER BY key", CHILD_FIELDS.split(","))

    if want_json:
        print(json.dumps({"epic": epic, "children": kids, "prd_key": prd[0] if prd else None}, indent=2))
        return

    all_figma = []  # (story_key, url)
    L = []
    L.append(f"# EPIC {epic_key} — {ef['summary']}")
    L.append(f"type: {ef['issuetype']['name']} · status: {ef['status']['name']} · {SITE}/browse/{epic_key}")
    if epic_desc:
        L.append("\n## Epic description\n" + epic_desc)
    for u in figma_urls(epic_desc):
        all_figma.append((epic_key, u))

    if prd:
        L.append(f"\n## Linked product issue (PRD) — {prd[0]}: {prd[1]}  (status: {prd[2]})")
        L.append(f"{SITE}/browse/{prd[0]}")
        L.append(prd[3] or "(no description)")
        for u in figma_urls(prd[3]):
            all_figma.append((prd[0], u))

    L.append(f"\n## Child stories ({len(kids)})")
    for k in kids:
        f = k["fields"]
        key = k["key"]
        L.append("\n" + "=" * 78)
        L.append(f"### {key}  [{f['issuetype']['name']}]  status: {f['status']['name']}")
        L.append(f"{SITE}/browse/{key}")
        L.append(f"SUMMARY: {f['summary']}")
        labs = f.get("labels") or []
        if labs:
            L.append("LABELS: " + ", ".join(labs))
        desc = flat(f.get("description"))
        L.append("--- DESCRIPTION ---")
        L.append(desc if desc else "(empty)")
        links = issue_links(f)
        if links:
            L.append("--- LINKS ---")
            for rel, lkey, summ in links:
                L.append(f"  {rel}: {lkey} — {summ}")
        for u in figma_urls(desc):
            all_figma.append((key, u))
        cs = comments(f, want_comments)
        if cs:
            L.append("--- COMMENTS ---")
            for who, when, body in cs:
                L.append(f"  [{who} · {when}] {body[:800]}")
                for u in figma_urls(body):          # figma links can live only in a comment
                    all_figma.append((f"{key} (comment)", u))

        # Subtasks — one level deeper, expanded (a broken-down story is not a black box).
        subs = f.get("subtasks") or []
        if subs:
            L.append(f"--- SUBTASKS ({len(subs)}) ---")
            for st in subs[:MAX_SUBTASKS]:
                sk = st["key"]
                sf = api_get(f"issue/{sk}", {"fields": SUB_FIELDS})["fields"]
                sdesc = flat(sf.get("description"))
                slabs = sf.get("labels") or []
                L.append(f"  • {sk} [{sf['issuetype']['name']}] ({sf['status']['name']}) — {sf['summary']}"
                         + (f"  labels: {', '.join(slabs)}" if slabs else ""))
                if sdesc:
                    L.append("    " + sdesc.replace("\n", "\n    "))
                for u in figma_urls(sdesc):
                    all_figma.append((sk, u))
            if len(subs) > MAX_SUBTASKS:
                L.append(f"  … {len(subs) - MAX_SUBTASKS} more subtasks not expanded (cap {MAX_SUBTASKS})")

    L.append("\n## Figma design links")
    if all_figma:
        L.append("(open each via the claude.ai Figma MCP — external URLs the read token cannot download)")
        for story_key, u in all_figma:
            L.append(f"  {story_key}: {u}")
    else:
        L.append("  (none found in the epic, PRD, or child stories)")

    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv)
