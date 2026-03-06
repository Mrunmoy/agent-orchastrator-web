#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HANDOFF_DIR="$REPO_ROOT/docs/handoff"
SHA="$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)"
NOW="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

MANAGERS=("codex-code" "claude-code")
if [[ $# -gt 0 ]]; then
    MANAGERS=("$@")
fi

mkdir -p "$HANDOFF_DIR"

for manager in "${MANAGERS[@]}"; do
    manager_dir="$HANDOFF_DIR/$manager"
    mkdir -p "$manager_dir"

    cat > "$manager_dir/KICKOFF.md" <<DOC
# ${manager} Kickoff

## Snapshot
- Generated: $NOW
- Base commit: $SHA
- Repo: agent-orchestrator-web

## Mission
Implement assigned slices in parallel through your own sub-agents while preserving integration safety and test quality.

## Read First
1. AGENTS.md
2. docs/DESIGN.md
3. docs/IMPLEMENTATION_PLAN_V1.md
4. docs/coordination/PARALLEL_AGENT_WORKFLOW.md
5. docs/coordination/CROSS_TOOL_HANDOFF.md
6. docs/coordination/task-board.md

## Execution Contract
- Create sub-agent branches using namespace: 
  - ${manager%%-*}/<subagent-name>
- Keep one scope per sub-agent.
- Require test evidence before marking task as Review.
- Do not merge to master directly.

## Suggested Steps
1. Claim unowned tasks from task-board.
2. Spawn sub-agents for independent slices.
3. Submit integration-ready branches with verification notes.
4. Hand back a consolidated status memo with:
   - completed tasks
   - blocked tasks
   - open decisions

## Report Template
- Task IDs completed:
- Branches ready for merge:
- Tests run:
- Risks/conflicts:
- Next 24h plan:
DOC

done

echo "Prepared handoff packs under: $HANDOFF_DIR"
