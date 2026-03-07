#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <TASK_ID> [PREFIX] [WORKER] [--shell]"
    echo "Example: $0 SETUP-001 claude claude-setup --shell"
    exit 1
fi

TASK_ID="$1"
PREFIX="${2:-claude}"
WORKER="${3:-worker}"
OPEN_SHELL="0"

if [[ "${*: -1}" == "--shell" ]]; then
    OPEN_SHELL="1"
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Ensure/sync task worktree and capture its path.
WT_OUTPUT="$($REPO_ROOT/scripts/task_worktree.py "$TASK_ID" --branch-prefix "$PREFIX")"
WT_PATH="$(printf '%s\n' "$WT_OUTPUT" | awk -F= '/^path=/{print $2}' | tail -n1)"

if [[ -z "$WT_PATH" ]]; then
    echo "Failed to resolve worktree path for $TASK_ID"
    echo "$WT_OUTPUT"
    exit 1
fi

# Write task prompt into the task worktree.
PROMPT_FILE="$WT_PATH/TASK_PROMPT.md"
$REPO_ROOT/scripts/task_prompt.py "$TASK_ID" --prefix "$PREFIX" --worker-name "$WORKER" > "$PROMPT_FILE"

cat <<MSG
[ok] task prepared
- task: $TASK_ID
- prefix: $PREFIX
- worker: $WORKER
- worktree: $WT_PATH
- prompt: $PROMPT_FILE
MSG

if [[ "$OPEN_SHELL" == "1" ]]; then
    cd "$WT_PATH"
    exec "${SHELL:-/bin/bash}" -i
fi
