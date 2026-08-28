#!/bin/bash
# run-drift-check.sh — wrapper invoked by the cars.codebase-map.drift launchd job.
# Runs drift_check.py --all --mark-stale and appends a timestamped report to
# ~/projects/codebase-map/relations/drift-log.md.
#
# Manual invocation:
#   bash ~/projects/codebase-map/scripts/run-drift-check.sh
#
# Exit code is the underlying drift_check.py exit code (0 clean, 1 drift, 2 error).

set -u

PROJECTS="$HOME/projects"
MAP="$PROJECTS/codebase-map"
LOG="$MAP/relations/drift-log.md"
SCRIPT="$MAP/scripts/drift_check.py"

ts() { date -Iseconds; }

# Seed the log with a header on first run.
if [ ! -f "$LOG" ]; then
    cat > "$LOG" <<EOF
# Drift Check Log

Auto-appended by \`scripts/run-drift-check.sh\` (launchd job \`cars.codebase-map.drift\`, weekly Mondays 09:00). Each section is one run.

If a run reports drift, the affected shadow's frontmatter is rewritten to \`status: stale\` automatically — re-read the source and re-bootstrap (or re-author) the shadow to clear the stale state.

EOF
fi

# Capture output and exit code.
output=$(/usr/bin/python3 "$SCRIPT" --all --mark-stale 2>&1)
rc=$?

{
    echo ""
    echo "## $(ts)"
    echo ""
    echo '```'
    echo "$output"
    echo '```'
} >> "$LOG"

exit "$rc"
