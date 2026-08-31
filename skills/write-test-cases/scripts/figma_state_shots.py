#!/usr/bin/env python3
"""Plan and verify per-state-node Figma screenshots for the write-test-cases mockups (Step 8).

Why this exists
---------------
Wide "Accept Order" / "Order Details" frames are 6000-10000 px boards holding many state
panels side by side. A single whole-frame `get_screenshot` renders each panel a few hundred
pixels wide, so copy read off it is a *guess* (`CONFIRM RECEIVABLES` where it says
`CONFIRM RECEIVING`; a `REQUEST NEW` button where the entry point is a `Faster Pay` toggle).
The fix is mechanical: screenshot EACH state panel by its own node id. This helper makes that
non-optional — it lists the exact node ids to shoot, and later checks you actually shot them.

It does NOT call Figma. The Figma MCP needs the live session's auth; a standalone script can't
reach it. So the flow is:

  1.  (in the agent) get_metadata(fileKey, <frame node>)  →  save the tool result to a file
  2.  plan:   python3 figma_state_shots.py plan <metadata_file> --filekey <FK> [--frame <node>]
              → prints the per-state get_screenshot worklist (+ optional --out worklist.json)
  3.  (in the agent) run each get_screenshot(nodeId=...) the plan lists; curl each PNG to a dir,
              naming the file after the node id (e.g. 4535-27857.png)
  4.  check:  python3 figma_state_shots.py check worklist.json <shots_dir>
              → non-zero exit + a MISSING list if any planned state panel has no downloaded shot

`get_metadata` returns a JSON array [{type, text}] whose `text` is an XML dump; this script
accepts that JSON, or a raw XML dump, or the ">>> exceeds max tokens, saved to file" artifact
the MCP writes for large frames. stdlib only.

Usage
-----
  figma_state_shots.py plan  METADATA_FILE [--frame NODE] [--filekey FK]
                             [--min-h PX] [--out worklist.json] [--all]
  figma_state_shots.py check WORKLIST_JSON SHOTS_DIR
"""
import json
import math
import os
import re
import sys

TAG_RE = re.compile(r"<(/?)([A-Za-z]+)((?:\s+[\w:-]+=\"[^\"]*\")*)\s*(/?)>")
ATTR_RE = re.compile(r"([\w:-]+)=\"([^\"]*)\"")
SIZED_TAGS = {"frame", "instance", "group", "section", "text", "component", "rectangle", "vector"}


class Node:
    __slots__ = ("id", "tag", "name", "x", "y", "w", "h", "children", "parent")

    def __init__(self, tag, attrs):
        self.tag = tag
        self.id = attrs.get("id", "")
        self.name = attrs.get("name", "")
        self.x = _f(attrs.get("x"))
        self.y = _f(attrs.get("y"))
        self.w = _f(attrs.get("width"))
        self.h = _f(attrs.get("height"))
        self.children = []
        self.parent = None


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def load_xml(path):
    """Return the XML text from a metadata file (JSON tool-result, raw XML, or saved artifact)."""
    raw = open(path, encoding="utf-8").read()
    stripped = raw.lstrip()
    if stripped.startswith("[") or stripped.startswith("{"):
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                data = [data]
            return "\n".join(
                d.get("text", "") for d in data if isinstance(d, dict)
            )
        except json.JSONDecodeError:
            pass
    return raw


def parse_tree(xml):
    """Build a Node tree from the metadata XML. Returns a synthetic root holding top-level nodes."""
    root = Node("root", {})
    stack = [root]
    for m in TAG_RE.finditer(xml):
        closing, tag, attr_str, self_close = m.group(1), m.group(2).lower(), m.group(3), m.group(4)
        if closing:
            if len(stack) > 1 and stack[-1].tag == tag:
                stack.pop()
            continue
        attrs = dict(ATTR_RE.findall(attr_str))
        node = Node(tag, attrs)
        node.parent = stack[-1]
        stack[-1].children.append(node)
        if not self_close:
            stack.append(node)
    return root


def find_by_id(node, node_id):
    want = node_id.replace("-", ":")
    if node.id.replace("-", ":") == want:
        return node
    for c in node.children:
        r = find_by_id(c, node_id)
        if r:
            return r
    return None


def rec_maxdim(node):
    longest = max(node.w or 0, node.h or 0)
    return int(min(4096, max(800, math.ceil(longest / 100.0) * 100)))


def classify(node, min_h):
    """Guess whether a direct child frame is a state panel or page chrome/label."""
    w, h = node.w or 0, node.h or 0
    if h and w and h >= min_h:
        if 300 <= w <= 480:
            return "MOBILE STATE"
        return "STATE PANEL"
    if h and h < 200 and w > 2.5 * h:
        return "banner/label"
    return "chrome?"


def cmd_plan(args):
    opts = {"--frame": None, "--filekey": "<FK>", "--min-h": "300", "--out": None}
    flags = {"--all": False}
    path = None
    i = 0
    while i < len(args):
        a = args[i]
        if a in opts:
            opts[a] = args[i + 1]; i += 2
        elif a in flags:
            flags[a] = True; i += 1
        elif path is None:
            path = a; i += 1
        else:
            i += 1
    if not path:
        sys.exit("plan: METADATA_FILE required")
    min_h = float(opts["--min-h"])
    tree = parse_tree(load_xml(path))
    frame = find_by_id(tree, opts["--frame"]) if opts["--frame"] else None
    if frame is None:
        # default: the largest top-level section/frame in the dump
        cands = [c for c in _walk(tree) if c.tag in ("section", "frame") and c.w and c.h]
        if not cands:
            sys.exit("plan: no frame/section nodes found in metadata")
        frame = max(cands, key=lambda n: (n.w or 0) * (n.h or 0))

    kids = [c for c in frame.children if c.tag in SIZED_TAGS and c.w and c.h]
    kids.sort(key=lambda n: (round((n.y or 0) / 200.0), n.x or 0))  # reading order: row then col

    panels = [k for k in kids if classify(k, min_h) in ("STATE PANEL", "MOBILE STATE")]
    show = kids if flags["--all"] else panels or kids

    # composite detection
    fw, fh = frame.w or 0, frame.h or 0
    big_kids = [k for k in kids if (k.w or 0) * (k.h or 0) > 0.02 * (fw * fh or 1)]
    is_composite = fw > 3000 or len(panels) > 2 or len(big_kids) > 2

    fk = opts["--filekey"]
    print(f"# Frame: {frame.id}  {frame.name!r}  ({int(fw)}x{int(fh)})")
    verdict = "COMPOSITE — you MUST screenshot each state node below individually" if is_composite \
        else "single-panel — a whole-frame screenshot at maxDimension>=native is enough"
    print(f"# Verdict: {verdict}")
    print(f"# Direct child state panels: {len(panels)}  (total sized children: {len(kids)})")
    print("#")
    print(f"# {'node id':<16} {'kind':<14} {'size':<12} name")
    for k in show:
        print(f"# {k.id:<16} {classify(k, min_h):<14} {f'{int(k.w)}x{int(k.h)}':<12} {k.name!r}")
    print("#\n# --- get_screenshot worklist (run each in the agent, then curl the PNG to <node>.png) ---")
    for k in show:
        md = rec_maxdim(k)
        print(f'get_screenshot(fileKey="{fk}", nodeId="{k.id}", maxDimension={md})   '
              f'# {k.name}  ({int(k.w)}x{int(k.h)})')

    if opts["--out"]:
        worklist = [
            {"node_id": k.id, "name": k.name, "w": int(k.w), "h": int(k.h),
             "maxDimension": rec_maxdim(k), "kind": classify(k, min_h)}
            for k in show
        ]
        json.dump({"fileKey": fk, "frame": frame.id, "panels": worklist},
                  open(opts["--out"], "w"), indent=2)
        print(f"\n# wrote worklist -> {opts['--out']}  ({len(worklist)} panels)")


def _walk(node):
    for c in node.children:
        yield c
        yield from _walk(c)


def cmd_check(args):
    if len(args) < 2:
        sys.exit("check: WORKLIST_JSON SHOTS_DIR required")
    worklist_path, shots_dir = args[0], args[1]
    wl = json.load(open(worklist_path))
    panels = wl.get("panels", wl if isinstance(wl, list) else [])
    files = os.listdir(shots_dir) if os.path.isdir(shots_dir) else []
    joined = " ".join(files)
    missing = []
    for p in panels:
        nid = p["node_id"] if isinstance(p, dict) else p
        # a shot counts if its filename contains the node id in ':' or '-' form
        if nid not in joined and nid.replace(":", "-") not in joined:
            missing.append((nid, p.get("name", "") if isinstance(p, dict) else ""))
    total = len(panels)
    print(f"planned state panels: {total}   shots present: {total - len(missing)}   "
          f"missing: {len(missing)}")
    for nid, name in missing:
        print(f"  MISSING  {nid}  {name!r}  <- screenshot this node before drawing its state")
    if missing:
        sys.exit(1)
    print("OK — every planned state node has a downloaded screenshot.")


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    cmd, rest = argv[1], argv[2:]
    if cmd == "plan":
        cmd_plan(rest)
    elif cmd == "check":
        cmd_check(rest)
    else:
        sys.exit(f"unknown command {cmd!r}; use 'plan' or 'check'")


if __name__ == "__main__":
    main(sys.argv)
