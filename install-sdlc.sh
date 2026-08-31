#!/usr/bin/env bash
#
# Set up (or update) a full Agentic SDLC workspace in one folder.
#
# Derived from clone_repos.sh — same parallel clone/ff-pull engine, but it lays
# out the workspace so the skills' paths resolve:
#
#   <WORKSPACE>/
#   ├── ship-cars-usa/            # all org code repos (the 232+)
#   └── agentic-sdlc-artifacts/   # this repo — CDR/ + jira-breakdowns/ outputs
#
# Repos named in ROOT_REPOS are cloned at the workspace root (not inside
# ship-cars-usa/); everything else goes under ship-cars-usa/.
#
# Usage:
#   # bootstrap a brand-new workspace folder:
#   curl -fsSL https://raw.githubusercontent.com/ship-cars-usa/agentic-sdlc-artifacts/main/install-sdlc.sh | bash -s -- ~/agentic-sdlc
#
#   # or, from inside a checkout of this repo (workspace defaults to the repo's parent):
#   ./install-sdlc.sh
#
#   # or explicit target:
#   ./install-sdlc.sh /path/to/workspace
#
# Env vars:
#   ORG=ship-cars-usa      # GitHub org
#   CODE_DIR=ship-cars-usa # subfolder for the code repos
#   ROOT_REPOS="agentic-sdlc-artifacts"   # space-separated; cloned at workspace root
#   JOBS=8                 # parallel workers
#   CLONE_PROTO=ssh        # "ssh" or "https"
#   GITHUB_TOKEN=...       # for private repos / higher rate limit
#
# Requirements: git, xargs, and either `gh` (preferred) or `curl` + `jq`.

set -euo pipefail

ORG="${ORG:-ship-cars-usa}"
CODE_DIR="${CODE_DIR:-ship-cars-usa}"
ROOT_REPOS="${ROOT_REPOS:-agentic-sdlc-artifacts}"
CLONE_PROTO="${CLONE_PROTO:-ssh}"
JOBS="${JOBS:-8}"

# ---- Resolve the workspace root ------------------------------------------------
# Priority: explicit arg > parent of this repo (when run from inside a checkout) > cwd.
resolve_default_ws() {
    local src="${BASH_SOURCE[0]:-}"
    if [[ -n "$src" && -f "$src" ]]; then
        local dir; dir="$(cd "$(dirname "$src")" && pwd)"
        # if the script lives in an agentic-sdlc-artifacts checkout, use its parent
        if [[ "$(basename "$dir")" == "agentic-sdlc-artifacts" ]]; then
            dirname "$dir"; return
        fi
    fi
    echo "$PWD"
}

WORKSPACE="${1:-$(resolve_default_ws)}"
mkdir -p "$WORKSPACE"
WORKSPACE="$(cd "$WORKSPACE" && pwd)"

echo "==> Agentic SDLC workspace: $WORKSPACE"
echo "==> Org: $ORG   code dir: $CODE_DIR/   root repos: $ROOT_REPOS"

# ---- Fetch the repo list -------------------------------------------------------
echo "==> Fetching repo list for org: $ORG"

if command -v gh >/dev/null 2>&1; then
    repos=$(gh repo list "$ORG" --limit 1000 --json name --jq '.[].name')
else
    command -v jq   >/dev/null 2>&1 || { echo "Error: install 'gh' or 'jq'." >&2; exit 1; }
    command -v curl >/dev/null 2>&1 || { echo "Error: 'curl' is required." >&2; exit 1; }

    auth_header=()
    [[ -n "${GITHUB_TOKEN:-}" ]] && auth_header=(-H "Authorization: Bearer $GITHUB_TOKEN")

    repos=""
    page=1
    while :; do
        resp=$(curl -fsSL "${auth_header[@]}" \
            -H "Accept: application/vnd.github+json" \
            "https://api.github.com/orgs/$ORG/repos?per_page=100&page=$page")
        chunk=$(echo "$resp" | jq -r '.[].name')
        [[ -z "$chunk" ]] && break
        repos+="$chunk"$'\n'
        page=$((page + 1))
    done
fi

if [[ -z "${repos// }" ]]; then
    echo "No repos found (or no access). Check org name and auth." >&2
    exit 1
fi

# ---- Partition: root repos vs. code repos --------------------------------------
is_root_repo() {
    local name="$1" r
    for r in $ROOT_REPOS; do [[ "$name" == "$r" ]] && return 0; done
    return 1
}

root_list=""
code_list=""
while IFS= read -r name; do
    [[ -z "$name" ]] && continue
    if is_root_repo "$name"; then root_list+="$name"$'\n'; else code_list+="$name"$'\n'; fi
done <<< "$repos"

code_count=$(echo "$code_list" | grep -c . || true)
root_count=$(echo "$root_list" | grep -c . || true)
echo "==> $code_count code repo(s) → $CODE_DIR/   |   $root_count root repo(s) → workspace root"

# ---- Worker: clone if missing, else fast-forward pull --------------------------
# args: name org proto basedir
clone_or_pull() {
    local name="$1" org="$2" proto="$3" base="$4"
    [[ -z "$name" ]] && return 0
    mkdir -p "$base"

    local url
    if [[ "$proto" == "ssh" ]]; then url="git@github.com:$org/$name.git"
    else url="https://github.com/$org/$name.git"; fi

    if [[ -d "$base/$name/.git" ]]; then
        if git -C "$base/$name" pull --ff-only --quiet 2>/dev/null; then
            echo "[ok]   pull  $name"
        else
            echo "[fail] pull  $name"
        fi
    else
        if git -C "$base" clone --quiet "$url" 2>/dev/null; then
            echo "[ok]   clone $name"
        else
            echo "[fail] clone $name"
        fi
    fi
}
export -f clone_or_pull

# ---- Clone root repos (workspace root) -----------------------------------------
if [[ -n "${root_list// }" ]]; then
    echo "==> Root repos → $WORKSPACE"
    echo "$root_list" | grep . | \
        xargs -P "$JOBS" -I{} bash -c 'clone_or_pull "$@"' _ {} "$ORG" "$CLONE_PROTO" "$WORKSPACE"
fi

# ---- Clone code repos (ship-cars-usa/) -----------------------------------------
echo "==> Code repos → $WORKSPACE/$CODE_DIR   ($JOBS parallel workers)"
echo "$code_list" | grep . | \
    xargs -P "$JOBS" -I{} bash -c 'clone_or_pull "$@"' _ {} "$ORG" "$CLONE_PROTO" "$WORKSPACE/$CODE_DIR"

# ---- Ensure artifact output + support folders exist ----------------------------
REPO_DIR="$WORKSPACE/agentic-sdlc-artifacts"
if [[ -d "$REPO_DIR/.git" ]]; then
    mkdir -p "$REPO_DIR/CDR" \
             "$REPO_DIR/jira-breakdowns" \
             "$REPO_DIR/tdd" \
             "$REPO_DIR/grooming"
fi

# ---- Jira token reminder -------------------------------------------------------
# The vendored grooming client + the skills' readers discover the read-only Jira
# token first-match-wins: $JIRA_READ_TOKEN, else <REPO>/grooming/jira-read.txt.
# The token is NEVER committed (see .gitignore), so it must be provided per machine.
if [[ -d "$REPO_DIR/.git" ]]; then
    if [[ -z "${JIRA_READ_TOKEN:-}" && ! -f "$REPO_DIR/grooming/jira-read.txt" ]]; then
        echo "==> NOTE: no Jira token found. The grooming/test-case skills need a read-only"
        echo "          Jira token — either export JIRA_READ_TOKEN=... or write it to:"
        echo "            $REPO_DIR/grooming/jira-read.txt"
    fi
fi

# ---- Discovery: COPY vendored skills into <WORKSPACE>/.claude/skills/ -----------
# Claude Code discovers skills under .claude/skills/. We copy (not symlink) each
# vendored skill so it works OS-agnostically (Windows/Git Bash restrict symlinks).
# This step doubles as the UPDATE mechanism: on every run we refresh (overwrite)
# the copies of the skills WE vendor, matched by their known names — so
# `git pull && ./install-sdlc.sh` updates them. A .claude/skills/<name> that is not
# one of ours is never touched. Idempotent.
if [[ -d "$REPO_DIR/skills" ]]; then
    SKILLS_DEST="$WORKSPACE/.claude/skills"
    mkdir -p "$SKILLS_DEST"
    echo "==> Copying skills into $SKILLS_DEST (re-run to update)"
    for skill_path in "$REPO_DIR/skills"/*/; do
        [[ -d "$skill_path" ]] || continue
        name="$(basename "$skill_path")"
        src="${skill_path%/}"
        dest="$SKILLS_DEST/$name"
        # Refresh a clean copy: remove our previous copy (or a stale symlink from an
        # older install), then copy fresh. Only ever removes the destination that
        # bears one of OUR vendored skill names, so a foreign skill of a different
        # name is never affected.
        rm -rf "$dest"
        cp -R "$src" "$dest"
        echo "[ok]   copy  $name"
    done
fi

# ---- Done ----------------------------------------------------------------------
cat <<EOF

==> Done. Workspace laid out at: $WORKSPACE
      $CODE_DIR/                 code repos
      agentic-sdlc-artifacts/   skills/ + grooming/ + codebase-map/ + CDR/ + jira-breakdowns/ + tdd/
      .claude/skills/           copies of the vendored skills (re-run install-sdlc.sh to update them)

Next: provide a Jira read token ($JIRA_READ_TOKEN or agentic-sdlc-artifacts/grooming/jira-read.txt),
connect the Figma MCP, and ensure gcloud + git are authenticated. Then the skills are ready.
EOF
