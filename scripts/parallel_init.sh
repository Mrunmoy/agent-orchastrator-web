#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <agent-name> [agent-name...]"
    echo "Example: $0 codex-ui claude-backend ollama-coordinator"
    exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKTREE_ROOT="${WORKTREE_ROOT:-$REPO_ROOT/../agent-orchestrator-worktrees}"
BASE_BRANCH="${BASE_BRANCH:-master}"
BRANCH_PREFIX="${BRANCH_PREFIX:-agent}"

mkdir -p "$WORKTREE_ROOT"

git -C "$REPO_ROOT" fetch --all --prune >/dev/null 2>&1 || true

for agent in "$@"; do
    safe_name="$(printf "%s" "$agent" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9._-' '-')"
    safe_name="${safe_name#-}"
    safe_name="${safe_name%-}"
    if [[ -z "$safe_name" ]]; then
        echo "[skip] invalid agent name: $agent"
        continue
    fi
    branch="${BRANCH_PREFIX}/${safe_name}"
    path="$WORKTREE_ROOT/$safe_name"

    if [[ -d "$path/.git" || -f "$path/.git" ]]; then
        echo "[skip] worktree exists: $path"
        continue
    fi

    if git -C "$REPO_ROOT" show-ref --verify --quiet "refs/heads/$branch"; then
        git -C "$REPO_ROOT" worktree add "$path" "$branch"
    else
        git -C "$REPO_ROOT" worktree add -b "$branch" "$path" "$BASE_BRANCH"
    fi

    cat > "$path/.agent-context.md" <<CTX
# Agent Context

Agent: $agent
Branch: $branch
Worktree: $path

Rules:
- Only modify files assigned to this agent's task.
- Commit in small slices with passing checks.
- Do not merge to $BASE_BRANCH directly.
CTX

    echo "[ok] $agent -> $path ($branch)"
done

echo
echo "Worktrees ready. Next:"
echo "  1) Assign each agent one scoped task from docs/coordination/task-board.md"
echo "  2) Run agents inside their own worktree directories"
echo "  3) Merge branches sequentially via merge coordinator"
