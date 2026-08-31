#!/usr/bin/env python3
"""Driver for the `breakdown-story` skill.

Turns a Jira key (e.g. SCP-14292) into one clean markdown block: the story,
its parent, its subtasks (each with a flattened description), its linked
issues — including the **full description + attachments of each linked issue**
(the product story an SCP ticket "implements" usually lives in a sibling project
like CPDR and carries the real problem statement, designs, and mind-maps) — and
the story's own attachments. This is the programmatic handle the skill uses —
without it every run re-derives ADF parsing by hand and silently drops the
product context + design images.

Read-only against Jira. Reuses the vendored grooming/jira_client.py for auth +
pagination + binary fetch; does NOT re-implement the token / HTTP layer. It DOES
write downloaded image/PDF attachments to a local cache dir so the agent can
Read (and, for images, actually *see*) them — those files are the only thing it
creates, and they land under <BREAKDOWNS_DIR>/attachments/, never inside a repo.

    python3 fetch_ticket.py SCP-14292
    python3 fetch_ticket.py SCP-14292 --json            # raw fields, for scripting
    python3 fetch_ticket.py SCP-14292 --no-links-deep   # don't fetch linked-issue bodies
    python3 fetch_ticket.py SCP-14292 --no-attachments  # list attachments but don't download
    python3 fetch_ticket.py SCP-14292 --no-video         # download video but skip ffmpeg frame extraction

Jira returns description/AC as ADF (Atlassian Document Format) JSON, not text.
`adf_to_md` flattens it to markdown. Attachments arrive as a separate `attachment`
field (NOT inline in the ADF); ADF only carries opaque `media` nodes, so the
attachment list is the authoritative source for "what images are on this issue."
"""

import json
import os
import re
import shutil
import subprocess
import sys

# --- Workspace-relative path resolution (no hardcoded user paths) ----------
# This script lives at <REPO>/skills/breakdown-story/fetch_ticket.py.
#   REPO_ROOT      = two dirs up from this script's own dir (…/skills/<name>/ -> REPO)
#   WORKSPACE_ROOT = $AGENTIC_SDLC_WORKSPACE or the parent of REPO_ROOT
#   GROOMING_DIR   = $GROOMING_DIR   or <REPO_ROOT>/grooming  (holds the vendored client)
#   BREAKDOWNS_DIR = $BREAKDOWNS_DIR or <REPO_ROOT>/jira-breakdowns
_SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(_SKILL_DIR))
WORKSPACE_ROOT = os.environ.get("AGENTIC_SDLC_WORKSPACE") or os.path.dirname(REPO_ROOT)
GROOMING = os.environ.get("GROOMING_DIR") or os.path.join(REPO_ROOT, "grooming")
BREAKDOWNS_DIR = os.environ.get("BREAKDOWNS_DIR") or os.path.join(REPO_ROOT, "jira-breakdowns")

# --- Wire in the shared grooming client (reuse, don't reimplement) ---------
if GROOMING not in sys.path:
    sys.path.insert(0, GROOMING)

try:
    from jira_client import api_get, api_get_binary  # noqa: E402
except Exception as exc:  # pragma: no cover - environment guard
    sys.exit(
        f"Could not import jira_client from {GROOMING}: {exc}\n"
        "Expected <GROOMING_DIR>/jira_client.py to exist and a Jira token to be set "
        "($JIRA_READ_TOKEN or <GROOMING_DIR>/jira-read.txt)."
    )

# Fields fetched for the main issue. Subtasks/parent are fetched shallowly.
FIELDS = (
    "summary,description,issuetype,status,labels,components,priority,"
    "parent,subtasks,issuelinks,assignee,comment,attachment"
)

# Linked issues are fetched one level deep so the product story's problem
# statement + designs come along; `attachment` is included so its images
# download too. We do NOT recurse into the linked issue's own links.
LINK_FIELDS = "summary,description,status,issuetype,attachment"
MAX_DEEP_LINKS = 12  # safety cap; issues with more links note the truncation

# Attachment handling. Image mimetypes are downloaded so the agent can SEE them
# (vision); PDFs are downloaded because the Read tool ingests them as pages. Both
# are reachable with the existing read token (no further auth) — that is the line
# the user's request draws: fetch what the token already unlocks. Other mimetypes
# (.docx, .xlsx, …) are listed but not downloaded; an external link (Figma) is not
# an attachment at all and never appears here.
IMAGE_MIMES = {
    "image/png", "image/jpeg", "image/jpg", "image/gif",
    "image/webp", "image/bmp", "image/tiff", "image/svg+xml",
}
FETCHABLE_MIMES = IMAGE_MIMES | {"application/pdf"}

# Video attachments (screen recordings) are the third fetchable kind. A bug repro
# or a design walkthrough is often ONLY in a video — the prose AC is empty (see
# SCS-1997, whose entire repro lived in a 17s .mp4). The Read tool can't ingest an
# mp4, but it CAN read still frames, so the driver downloads the video AND, when
# ffmpeg is on PATH, samples it into frames the agent Reads like any screenshot.
# ffmpeg is an optional dependency: absent it, the video is still downloaded and the
# driver says how to extract frames, so the skill degrades gracefully, never crashes.
VIDEO_MIMES = {
    "video/mp4", "video/quicktime", "video/webm", "video/x-msvideo",
    "video/x-matroska", "video/mpeg", "video/ogg", "video/3gpp",
}
# Frame sampling: one frame every VIDEO_FRAME_INTERVAL_S seconds, scaled to
# VIDEO_FRAME_WIDTH px wide, capped at VIDEO_MAX_FRAMES (for a long video the
# interval is stretched so the whole thing is still covered by ~MAX frames).
VIDEO_FRAME_INTERVAL_S = float(os.environ.get("BREAKDOWN_VIDEO_INTERVAL", "2"))
VIDEO_FRAME_WIDTH = int(os.environ.get("BREAKDOWN_VIDEO_WIDTH", "1280"))
VIDEO_MAX_FRAMES = int(os.environ.get("BREAKDOWN_VIDEO_MAX_FRAMES", "48"))

ATTACHMENTS_ROOT = os.environ.get("BREAKDOWN_ATTACHMENTS_DIR") or os.path.join(
    BREAKDOWNS_DIR, "attachments"
)

# Collects "<ISSUE-KEY>: <video name>" for every video that was downloaded but could
# NOT be frame-extracted because ffmpeg is missing. render() turns a non-empty list
# into a loud banner at the very top of the output, so the agent (and the user) can't
# miss that a video exists whose frames were never produced — the whole point of the
# feature fails silently otherwise. Populated during rendering; read at the end.
_VIDEO_NO_FFMPEG = []

# Figma (and other external design) links are NOT attachments — they live as URLs
# inside the description/AC, comments, subtask bodies, or a linked product issue, so
# the read token never downloads them. But they are first-class design evidence
# (DoR items 2/3/4), and now that the Figma MCP connector exists the agent CAN open
# them. The driver's job is to make them impossible to miss: scan the whole rendered
# block (story + subtasks + linked issues + comments) and surface every figma.com URL
# in one section. `adf_to_md` already turns ADF link marks / inlineCards into bare
# URLs, so a single regex over the assembled markdown catches links wherever they hide.
FIGMA_URL_RE = re.compile(
    r"https?://(?:www\.)?figma\.com/(?:file|design|proto|board|slides|make)/[^\s)\]>\"'}]+",
    re.IGNORECASE,
)


def extract_figma_links(text):
    """Return the de-duplicated, order-preserving list of figma.com URLs in `text`."""
    seen, out = set(), []
    for m in FIGMA_URL_RE.finditer(text or ""):
        url = m.group(0).rstrip(".,;")  # trim trailing sentence punctuation
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out


def render_figma_links(urls):
    """Markdown section listing the Figma design links found anywhere in the issue.

    These are external URLs (not Jira attachments), so the driver can't download a
    picture — but the agent can open each with the Figma MCP (get_screenshot /
    get_metadata) and review it as design evidence. See the skill's Step 1b.
    """
    out = [f"## Figma design links ({len(urls)})", ""]
    if not urls:
        out.append(
            "_(none found in the story, its subtasks, comments, or linked issues)_"
        )
        out.append("")
        return out
    out.append(
        "**Open each with the Figma MCP — these are design evidence, not decoration.** "
        "Use `get_screenshot` (View-seat-safe) to SEE the frame and `get_metadata` for "
        "structure; extract `fileKey` + `nodeId` from the `node-id=` query param. "
        "See the skill's Step 1b."
    )
    out.append("")
    for u in urls:
        out.append(f"- {u}")
    out.append("")
    return out


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
        # ADF media nodes are opaque pointers — the real file (and whether it's an
        # image worth downloading) is in the issue's `attachment` field, rendered in
        # the "## Attachments" section. Point the reader there instead of dropping it.
        alt = (node.get("attrs") or {}).get("alt") or ""
        label = f"embedded image: {alt}" if alt else "embedded image / file"
        return f"_[{label} — see ## Attachments]_\n\n"
    # Unknown node: recurse into its content so nothing is silently dropped.
    return adf_to_md(content, depth)


def field_md(fields, name, default=""):
    val = fields.get(name)
    if isinstance(val, dict) and val.get("type") == "doc":
        return adf_to_md(val).strip() or default
    return val if val is not None else default


# Subtask second-fetch: we need estimate + assignee to judge the Definition-of-Ready
# items ("sub-tasks estimated", "Automation test sub-task estimated and assigned",
# "status To Do"), not just the summary/description/status the parent listing gives.
# Common Jira-Cloud default for the Story Points field. May differ per instance;
# if it's blank everywhere, discover the real id with `--json` and adjust here.
STORY_POINTS_FIELD = "customfield_10016"

SUBTASK_FIELDS = (
    "summary,description,status,assignee,timetracking,timeoriginalestimate,"
    + STORY_POINTS_FIELD
)


def fmt_estimate(fields):
    """Best-effort human estimate string from a subtask's fields, or '—'."""
    tt = fields.get("timetracking") or {}
    if tt.get("originalEstimate"):
        return tt["originalEstimate"]
    secs = fields.get("timeoriginalestimate")
    if isinstance(secs, (int, float)) and secs:
        hours = secs / 3600.0
        return f"{hours:g}h"
    sp = fields.get(STORY_POINTS_FIELD)
    if isinstance(sp, (int, float)) and sp:
        return f"{sp:g} pts"
    return "—"


def fmt_assignee(fields):
    a = fields.get("assignee") or {}
    return a.get("displayName") or "unassigned"


def fetch_issue(key, fields=FIELDS):
    return api_get(f"issue/{key}", {"fields": fields})


def _human_size(size):
    if isinstance(size, (int, float)) and size:
        return f"{size / 1024:.0f} KB" if size < 1024 * 1024 else f"{size / 1048576:.1f} MB"
    return "?"


def _ffmpeg_bin():
    """Path to ffmpeg if it's on PATH, else None. Frame extraction is optional."""
    return shutil.which("ffmpeg")


def _video_duration(path):
    """Duration in seconds via ffprobe, or None if unknown/unavailable."""
    probe = shutil.which("ffprobe")
    if not probe:
        return None
    try:
        out = subprocess.run(
            [probe, "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", path],
            capture_output=True, text=True, timeout=30,
        )
        return float(out.stdout.strip())
    except Exception:
        return None


def extract_video_frames(video_path, dest_dir, base):
    """Sample a downloaded video into still frames the Read tool can view.

    Returns (frame_paths, note). `frame_paths` is a sorted list of the JPEGs
    written (empty on failure); `note` is a human string for the output line.
    ffmpeg is optional — if it's missing we return ([], reason) and the caller
    still points at the downloaded video so a human can extract frames manually.
    """
    ff = _ffmpeg_bin()
    if not ff:
        return [], "ffmpeg not found on PATH — install it (e.g. `brew install ffmpeg`) to auto-extract frames"
    # Stretch the sampling interval for long videos so we stay under the frame cap
    # while still covering the whole recording end to end.
    interval = VIDEO_FRAME_INTERVAL_S
    dur = _video_duration(video_path)
    if dur and dur / interval > VIDEO_MAX_FRAMES:
        interval = dur / VIDEO_MAX_FRAMES
    frames_dir = os.path.join(dest_dir, f"{base}.frames")
    os.makedirs(frames_dir, exist_ok=True)
    # Clear any stale frames from a previous run so counts/paths stay truthful.
    for old in os.listdir(frames_dir):
        if old.endswith(".jpg"):
            try:
                os.remove(os.path.join(frames_dir, old))
            except OSError:
                pass
    pattern = os.path.join(frames_dir, "f_%03d.jpg")
    try:
        subprocess.run(
            [ff, "-v", "error", "-y", "-i", video_path,
             "-vf", f"fps=1/{interval},scale={VIDEO_FRAME_WIDTH}:-1",
             "-q:v", "4", pattern],
            capture_output=True, text=True, timeout=300, check=True,
        )
    except Exception as exc:
        return [], f"frame extraction failed: {exc}"
    frames = sorted(
        os.path.join(frames_dir, fn) for fn in os.listdir(frames_dir) if fn.endswith(".jpg")
    )
    if not frames:
        return [], "ffmpeg produced no frames (unreadable/empty video?)"
    return frames, f"{len(frames)} frames, ~1 frame / {interval:.0f}s"


def render_attachments(owner_key, attachments, download=True, extract_video=True,
                       heading="## Attachments"):
    """List an issue's attachments; download images/PDFs/videos locally so the agent
    can Read (and, for images and video frames, see) them. Returns markdown lines.

    Images/PDFs need no auth beyond the read token, so they're pulled down to
    <BREAKDOWNS_DIR>/attachments/<owner_key>/. Videos are pulled down too and, when
    ffmpeg is available, sampled into still frames under <name>.frames/ so a repro
    or design recording is Readable as images (see extract_video_frames). Anything
    else is listed with a note to review it manually — we don't guess at formats the
    Read tool can't open.
    """
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
            except Exception as exc:  # network / auth hiccup: surface, don't crash
                out.append(f"- ⚠️ {name} ({mime}, {sz}) — download failed: {exc}")
        elif mime in FETCHABLE_MIMES and not download:
            out.append(f"- 📎 {name} ({mime}, {sz}) — downloadable image/PDF (skipped: --no-attachments)")
        elif download and mime in VIDEO_MIMES and a.get("content"):
            try:
                data = api_get_binary(a["content"])
                os.makedirs(dest_dir, exist_ok=True)
                safe = name.replace("/", "_").replace("\\", "_")
                path = os.path.join(dest_dir, safe)
                with open(path, "wb") as fh:
                    fh.write(data)
                out.append(f"- 🎞 **{name}** ({mime}, {sz}) → `{path}`")
                if extract_video:
                    frames, note = extract_video_frames(path, dest_dir, safe)
                    if frames:
                        fdir = os.path.dirname(frames[0])
                        out.append(
                            f"    - 🖼 extracted {note} → `{fdir}/` "
                            f"— **Read these frames to VIEW the recording** "
                            f"(`{os.path.basename(frames[0])}` … `{os.path.basename(frames[-1])}`)"
                        )
                    elif "ffmpeg not found" in note:
                        _VIDEO_NO_FFMPEG.append(f"{owner_key}: {name}")
                        out.append(
                            f"    - ⚠️ **ffmpeg not installed — NO frames were extracted from this "
                            f"video.** Install it (`brew install ffmpeg`) and re-run to see the "
                            f"recording, or Read the saved file manually. See the banner at the top."
                        )
                    else:
                        out.append(f"    - ⚠️ {note} — Read the video manually, or install ffmpeg and re-run")
                else:
                    out.append("    - (frame extraction skipped: --no-video) — Read the video manually")
            except Exception as exc:  # network / auth hiccup: surface, don't crash
                out.append(f"- ⚠️ {name} ({mime}, {sz}) — video download failed: {exc}")
        elif mime in VIDEO_MIMES and not download:
            out.append(f"- 📎 {name} ({mime}, {sz}) — video (skipped: --no-attachments)")
        else:
            out.append(f"- 📎 {name} ({mime}, {sz}) — not an image/PDF/video; review manually if relevant")
    out.append("")
    return out


def render_links(links, deep=True, download=True, extract_video=True):
    """Render the linked-issue list, and (deep=True) pull each linked issue's full
    description + attachments one level down. The product story an SCP ticket
    `implements` lives here — fetching it is the whole point of this enhancement."""
    out = ["## Linked issues", ""]
    deep_targets = []  # (key, relation_label) to expand below the list
    for ln in links:
        rel = ln.get("type", {})
        for side, label in (("outwardIssue", rel.get("outward")), ("inwardIssue", rel.get("inward"))):
            other = ln.get(side)
            if not other:
                continue
            okey = other.get("key")
            of = other.get("fields") or {}
            out.append(
                f"- {label}: {okey} — {of.get('summary', '')} "
                f"[{(of.get('status') or {}).get('name')}]"
            )
            deep_targets.append((okey, label))
    out.append("")

    if not deep or not deep_targets:
        return out

    expanded = deep_targets[:MAX_DEEP_LINKS]
    if len(deep_targets) > MAX_DEEP_LINKS:
        out.append(
            f"_Expanding the first {MAX_DEEP_LINKS} of {len(deep_targets)} linked issues "
            f"below; fetch the rest manually if relevant._"
        )
        out.append("")
    for okey, label in expanded:
        detail = fetch_issue(okey, LINK_FIELDS)
        df = detail.get("fields", {})
        out.append(f"### 🔗 Linked issue {okey} ({label}) — full content")
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
        out.extend(
            render_attachments(
                okey, df.get("attachment"), download=download, extract_video=extract_video,
                heading=f"**Attachments on {okey}**",
            )
        )
    return out


def render(key, deep_links=True, download_attachments=True, extract_video=True):
    issue = fetch_issue(key)
    f = issue.get("fields", {})
    out = []
    out.append(f"# {issue.get('key')} — {f.get('summary', '(no summary)')}")
    out.append("")
    out.append(f"- **Type:** {(f.get('issuetype') or {}).get('name')}")
    out.append(f"- **Status:** {(f.get('status') or {}).get('name')}")
    out.append(f"- **Priority:** {(f.get('priority') or {}).get('name')}")
    out.append(
        f"- **Components:** {', '.join(c.get('name') for c in (f.get('components') or [])) or '(none)'}"
    )
    out.append(f"- **Labels:** {', '.join(f.get('labels') or []) or '(none)'}")
    parent = f.get("parent")
    if parent:
        out.append(
            f"- **Parent:** {parent.get('key')} — {(parent.get('fields') or {}).get('summary', '')}"
        )
    out.append("")
    out.append("## Description / Acceptance Criteria")
    out.append("")
    out.append(field_md(f, "description", "_(empty)_"))
    out.append("")

    # The story's own image/PDF attachments (designs, mind-maps) — downloaded so
    # the agent can actually look at them, not flatten them to "_[attachment]_".
    out.extend(render_attachments(issue.get("key"), f.get("attachment"),
                                  download=download_attachments, extract_video=extract_video))

    # Anchor: the Figma-links section is inserted here (after the story attachments,
    # before subtasks) once the rest of the body is built — see the splice below. It
    # scans the FULL block, so links inside linked issues/comments surface here too.
    figma_anchor = len(out)

    subtasks = f.get("subtasks") or []
    if subtasks:
        out.append("## Existing subtasks")
        out.append("")
        for st in subtasks:
            # Subtask descriptions/estimate/assignee need a second fetch (the parent
            # listing omits them). These feed the Definition-of-Ready evaluation:
            # "sub-tasks estimated", "Automation test sub-task estimated and assigned",
            # and "status To Do".
            detail = fetch_issue(st.get("key"), SUBTASK_FIELDS)
            df = detail.get("fields", {})
            out.append(f"### {st.get('key')} — {df.get('summary', '')}")
            out.append(
                f"- Status: {(df.get('status') or {}).get('name')}"
                f"  ·  Estimate: {fmt_estimate(df)}"
                f"  ·  Assignee: {fmt_assignee(df)}"
            )
            out.append("")
            out.append(field_md(df, "description", "_(no description)_"))
            out.append("")

    links = f.get("issuelinks") or []
    if links:
        out.extend(render_links(links, deep=deep_links, download=download_attachments,
                                extract_video=extract_video))

    # Comments carry the agreed API contract for the Definition-of-Ready item
    # "API contract has been agreed and written into the Story as a comment".
    # `comment` is already requested in FIELDS; the parent fetch returns it inline.
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

    # Splice the Figma-links section in at the anchor, scanning everything built so
    # far (story + subtasks + linked issues + comments) for figma.com URLs.
    figma_section = render_figma_links(extract_figma_links("\n".join(out)))
    out = out[:figma_anchor] + figma_section + out[figma_anchor:]

    # Loud, unmissable banner when a video was downloaded but ffmpeg couldn't extract
    # its frames. Goes at the VERY TOP so neither the agent nor the user scrolls past
    # it — a video whose frames never rendered is a silent gap in the design evidence.
    if _VIDEO_NO_FFMPEG:
        vids = "; ".join(_VIDEO_NO_FFMPEG)
        banner = [
            "> ⚠️ **ACTION NEEDED — ffmpeg not installed, video frames NOT extracted.**",
            f"> This ticket has a video attachment ({vids}) that was downloaded but could **not**",
            "> be sampled into frames, so its repro/design is not yet visible. Install ffmpeg",
            "> (`brew install ffmpeg`) and re-run `fetch_ticket.py`, or Read the saved video manually.",
            "> **Tell the user this** — do not design from the text alone as if no video existed.",
            "",
        ]
        out = banner + out

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
            extract_video="--no-video" not in argv,
        ))


if __name__ == "__main__":
    main(sys.argv)
