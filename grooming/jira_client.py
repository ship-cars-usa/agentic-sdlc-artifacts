#!/usr/bin/env python3
"""Shared read-only Jira client for the SCP reports.

Scoped Atlassian API tokens 401 against the *.atlassian.net host directly, so all
calls go through the api.atlassian.com gateway with HTTP Basic auth (email:token).

Deliberately SECRET-FREE. The token is *discovered* at runtime, first match wins:

    1. $JIRA_READ_TOKEN  (or $JIRA_API_TOKEN)   — env var
    2. jira-read.txt sitting next to this file  — <GROOMING_DIR>/jira-read.txt, gitignored

This file is vendored at <REPO>/grooming/jira_client.py, so "next to this file" IS
<GROOMING_DIR>. Email defaults to the team address; override with $JIRA_EMAIL.
"""

import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

# --- Config ---------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))

EMAIL = os.environ.get("JIRA_EMAIL", "hristo.savov@ship.cars")
CLOUD_ID = os.environ.get("JIRA_CLOUD_ID", "94804e79-99c3-4531-9ef1-8f0fb8d02581")
BASE = f"https://api.atlassian.com/ex/jira/{CLOUD_ID}/rest/api/3"
SITE = "https://shipcars.atlassian.net"
BOARD_URL = f"{SITE}/jira/software/c/projects/SCP/boards/87"


def _load_token():
    tok = os.environ.get("JIRA_READ_TOKEN") or os.environ.get("JIRA_API_TOKEN")
    if tok:
        return tok.strip()
    path = os.path.join(HERE, "jira-read.txt")  # == <GROOMING_DIR>/jira-read.txt
    if os.path.isfile(path):
        with open(path) as fh:
            return fh.read().strip()
    sys.exit(
        "No Jira token found. Set $JIRA_READ_TOKEN, or place jira-read.txt next "
        "to this script (<GROOMING_DIR>/jira-read.txt)."
    )


TOKEN = _load_token()
_AUTH = "Basic " + base64.b64encode(f"{EMAIL}:{TOKEN}".encode()).decode()


# --- HTTP helpers ---------------------------------------------------------
def api_get(path, params):
    url = f"{BASE}/{path}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url, headers={"Authorization": _AUTH, "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        sys.exit(f"\nHTTP {exc.code} calling {path}\n{body}\n")


def api_get_binary(url, timeout=120):
    """GET raw bytes from a full Atlassian URL using the same read-only auth.

    Used for attachment downloads: the `attachment.content` link is already a
    full api.atlassian.com gateway URL (e.g. .../rest/api/3/attachment/content/<id>)
    and 302-redirects to a signed media URL — urllib follows that automatically and
    the bearer header is fine on the gateway hop. No extra authentication is needed
    beyond the read token, which is exactly why image/PDF attachments are fetchable
    here while external links (Figma, Google Drive) are not.
    """
    req = urllib.request.Request(url, headers={"Authorization": _AUTH})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")[:300]
        raise RuntimeError(f"HTTP {exc.code} fetching attachment: {body}") from exc


def search_all(jql, fields):
    """Page through search/jql, returning every issue (handles nextPageToken)."""
    issues = []
    token = None
    while True:
        params = {"jql": jql, "fields": ",".join(fields), "maxResults": 100}
        if token:
            params["nextPageToken"] = token
        data = api_get("search/jql", params)
        issues.extend(data.get("issues", []))
        token = data.get("nextPageToken")
        if not token or data.get("isLast"):
            break
    return issues


def chunked(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i : i + size]
