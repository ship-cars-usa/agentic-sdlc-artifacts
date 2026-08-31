#!/usr/bin/env python3
"""Read-only Jira client for the `revise-stories-from-transcript` skill.

This is the skill's OWN copy of the shared SCP Jira client (same auth model as
the vendored grooming/jira_client.py): scoped Atlassian tokens 401 against the
*.atlassian.net host, so every call goes through the api.atlassian.com gateway
with HTTP Basic auth (email:token).

Deliberately SECRET-FREE. The live token is a fleet-wide credential and must not
be duplicated into a second file. Instead the token is *discovered* at runtime,
first match wins:

    1. $JIRA_READ_TOKEN  (or $JIRA_API_TOKEN)          — env var
    2. jira-read.txt sitting next to this script        — skill-local, gitignored
    3. <GROOMING_DIR>/jira-read.txt                     — the team convention
                                                          (<REPO_ROOT>/grooming)

Email defaults to the team address; override with $JIRA_EMAIL.
"""

import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
# This client lives at <REPO>/skills/revise-stories-from-transcript/scripts/, so
# REPO_ROOT is three dirs up (scripts/ -> revise-… -> skills -> REPO); the grooming
# dir default is <REPO_ROOT>/grooming, overridable with $GROOMING_DIR.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
GROOMING_DIR = os.environ.get("GROOMING_DIR") or os.path.join(REPO_ROOT, "grooming")

EMAIL = os.environ.get("JIRA_EMAIL", "hristo.savov@ship.cars")
CLOUD_ID = os.environ.get("JIRA_CLOUD_ID", "94804e79-99c3-4531-9ef1-8f0fb8d02581")
BASE = f"https://api.atlassian.com/ex/jira/{CLOUD_ID}/rest/api/3"
SITE = "https://shipcars.atlassian.net"


def _load_token():
    tok = os.environ.get("JIRA_READ_TOKEN") or os.environ.get("JIRA_API_TOKEN")
    if tok:
        return tok.strip()
    for path in (
        os.path.join(HERE, "jira-read.txt"),
        os.path.join(GROOMING_DIR, "jira-read.txt"),
    ):
        if os.path.isfile(path):
            with open(path) as fh:
                return fh.read().strip()
    sys.exit(
        "No Jira token found. Set $JIRA_READ_TOKEN, or place jira-read.txt next "
        "to this script, or keep <GROOMING_DIR>/jira-read.txt in place."
    )


TOKEN = _load_token()
_AUTH = "Basic " + base64.b64encode(f"{EMAIL}:{TOKEN}".encode()).decode()


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
