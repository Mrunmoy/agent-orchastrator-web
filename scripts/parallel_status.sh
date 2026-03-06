#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== Worktrees =="
git -C "$REPO_ROOT" worktree list

echo
echo "== Agent Branches =="
git -C "$REPO_ROOT" for-each-ref \
  --format='%(refname:short) | %(committerdate:iso8601) | %(subject)' \
  refs/heads/agent || true
