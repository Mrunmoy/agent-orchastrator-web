# Design Document: Multi-Agent CLI Orchestrator Web App

## 1. Objective
Build a LAN-accessible web app for orchestrating local CLI agents (Codex, Claude, optional Ollama manager) to run a disciplined engineering workflow:
- debate design,
- converge on decision,
- implement with TDD,
- integrate and validate,
- capture learnings,
- merge safely.

## 2. Product Intent
This is not only a chat UI. It is a human-in-the-loop engineering cockpit where the user remains the decision maker and agents are structured collaborators.

## 3. Scope
### In Scope
- Multi-agent orchestration (N agents)
- Unique agent identity (name, type, order, session, personality)
- Directed first message to selected agent
- Strict round-robin relay
- Batch execution (default 20 turns), auto-pause, continue
- User steering notes and preference notes between batches
- Stop-now control
- Working-directory selection for CLI context
- Personality profile loading from file
- Transcript and memory persistence
- Group-chat UI with avatars/bubbles/typing status

### Out of Scope (v1)
- Internet hosting
- Multi-user auth/roles
- Voice/audio

## 4. Engineering Operating Model (Core Design Philosophy)
The orchestration engine must support these explicit phases and gates.

### Phase A: Design Debate
Goal: evaluate architecture options and constraints.
Output: candidate options, tradeoffs, recommendation.
Gate: user accepts a chosen direction.

### Phase B: TDD Planning
Goal: define tests before implementation.
Output: test matrix (unit/integration/target), acceptance criteria.
Gate: tests and success criteria are approved.

### Phase C: Implementation
Goal: split work into small tasks and execute.
Output: scoped changes by agent/task.
Gate: all planned tests for each task pass.

### Phase D: Integration and Validation
Goal: combine outputs and verify behavior.
Output: integrated branch, host test evidence, target/hardware evidence when applicable.
Gate: integration checks are green.

### Phase E: Documentation and Learnings
Goal: preserve rationale and debugging findings.
Output: updated design notes, decision log, failure/debug notes.
Gate: docs synced with final behavior.

### Phase F: Merge Readiness
Goal: quality and traceability check before merge.
Output: merge checklist complete.
Gate: user approval to merge.

## 5. Functional Requirements
1. User can add, edit, remove, enable/disable, and reorder agents.
2. User can assign unique names to agents.
3. User can set agent type (`codex`, `claude`, optional `ollama_manager`) and optional session id.
4. User can set per-agent personality.
5. User can choose a target agent for first turn.
6. Orchestrator runs in strict round-robin order.
7. Orchestrator runs in batches (`batch_turns`, default 20), then pauses.
8. On pause, user can continue, stop, or inject steering/preference instructions.
9. UI can switch current workflow phase (A-F) and show current gate status.
10. Prompting logic includes active phase and expected output format.
11. System tracks agreement and phase completion status.
12. System persists sessions, configuration, and transcript memory.

## 6. Non-Functional Requirements
- Local-first runtime
- LAN-safe access with token
- Deterministic scheduling/order
- Graceful failure and resumability
- Mobile-friendly UI

## 7. Coding Standards and Design-Pattern Policy
These are mandatory for agent-generated implementation tasks.

### C++ Standard
- Use Google C++ style as baseline.
- Exceptions required by owner:
- Class member variables use `m_` prefix.
- Use `camelCase` for methods and variables.
- Put opening braces on the next line (Allman style).

### Python Standard
- Follow PEP 8.
- Prefer type hints and clear module boundaries.
- Use `ruff`/`black` compatible formatting.

### Web/Frontend Standard
- Prefer TypeScript where practical.
- Enforce ESLint + Prettier style consistency.
- Keep components small and testable.

### Cross-Language Engineering Rules
- Always evaluate at least one relevant design pattern before implementation (for example Strategy, Adapter, State, Factory, Observer).
- Document chosen pattern and why alternatives were rejected.
- Keep functions/classes small and testable.
- Apply TDD-first discipline: tests planned before implementation tasks are approved.

## 8. High-Level Architecture
1. Web/API Server
- state endpoints, events, control endpoints.

2. Orchestrator Engine
- turn execution, batch lifecycle, phase/gate state machine.

3. CLI Adapter Layer
- Codex adapter, Claude adapter, optional Ollama manager adapter.

4. Memory Layer
- append-only JSONL transcript,
- SQLite index,
- periodic markdown summaries.

5. Frontend SPA
- chat timeline,
- agent management,
- phase/gate controls,
- batch controls,
- steering panel.

## 9. Data Model
```text
Agent
- id
- name
- kind: codex|claude|ollama_manager
- session_id
- personality_key
- order
- enabled
- model
- avatar

Settings
- workdir
- batch_turns_default
- batch_turns_max
- per_turn_timeout_sec
- access_token

WorkflowState
- phase: DESIGN_DEBATE|TDD_PLANNING|IMPLEMENTATION|INTEGRATION|DOCS|MERGE
- gate_status: OPEN|SATISFIED|APPROVED
- gate_notes

ConversationState
- busy
- paused
- stop_requested
- current_speaker_agent_id
- turn_count_total
- turn_count_in_batch
- latest_agreement[agent_id]
- pending_steering_note
- pending_preference_note
```

## 10. Orchestration Algorithm (Batch + Pause + Workflow Phases)
Given ordered agents `A[0..n-1]` and target `A[k]`:
1. `incoming = user_message`
2. `current = k`
3. `limit = batch_turns`
4. For each step in `1..limit`:
- if stop requested: terminate run
- speaker = `A[current]`
- build prompt with: phase context + personality + coding-standard policy + incoming + recent transcript + pending steering/preference
- call speaker CLI adapter
- append response
- parse `AGREEMENT_STATUS: AGREE|CONTINUE`
- parse `PHASE_STATUS: READY_FOR_GATE|NEEDS_MORE_WORK`
- clear pending steering/preference after first successful consumption
- if all enabled agents are `AGREE` and phase status indicates gate-ready: set gate satisfied, pause for user approval
- incoming = speaker reply
- current = `(current + 1) % n`
5. If steps exhausted: pause and await user action.

## 11. User Steering Controls
Between batches, user can inject:
- Steering note: directional correction.
- Preference note: selected option/idea.
- Phase transition intent: request move to next phase.

These notes are high-priority prompt headers for subsequent turns.

## 11.5 Conversation History and Smart Resume

### History UX Requirements
- Left pane conversation list is scrollable for large histories.
- Each conversation row supports select, rename, delete.
- Global action supports `Clear All Conversations` with confirmation.
- No thread model; conversations stay linear.

### Persistence Model
- `data/conversations.json`: metadata index (id, title, created_at, updated_at, phase, status, deleted flag).
- `data/transcripts/<conversation_id>.jsonl`: full append-only event/message log.
- `data/summaries/<conversation_id>.json`: rolling summaries per batch/phase.
- `data/artifacts/<conversation_id>/<batch_id>.json`: agreement/conflict/memo outputs.

### Checkpoint-First Resume Model (Session ID Optional)
- Conversation continuity is owned by local persisted state, not provider session IDs.
- Agent session IDs are optional accelerators only.
- Resume must work even when no prior provider session exists.

Resume bootstrap modes:
1. `continue-session` mode: if valid session id exists, continue and apply context delta.
2. `reconstruct` mode: if no session id, start fresh agent turn with checkpoint context pack.

Checkpoint data saved every batch:
- phase/gate state,
- accepted decisions,
- unresolved conflicts,
- next actions,
- latest steering/preference directives.

### Smart Resume Context Pack (Token-Efficient)
When user selects a conversation, do not replay full transcript. Build a compact resume pack:
1. conversation objective + constraints,
2. active phase + gate state,
3. latest steering/preference notes,
4. last 2 batch summaries,
5. latest agreement/conflict/memo artifact,
6. last 8-12 raw messages only.

Target context budget per agent turn after resume:
- soft target: 1200-2800 tokens,
- hard cap: configurable (default 3500 tokens).

If pack exceeds cap:
- reduce raw message window,
- compress summaries,
- keep latest decisions and unresolved conflicts mandatory.

## 11.6 Multi-Conversation Background Execution Model

### Conversation Lifecycle Modes
Each conversation is a long-lived workspace with states:
- `Debate`
- `Execution Planning`
- `Autonomous Work`
- `Needs User Input`
- `Completed`
- `Failed`
- `Queued`

Switching away from a conversation does not end it; background execution can continue.

### Concurrency and Capacity Policy
- Scheduler is `auto-throttle` based on:
- current system capacity (CPU/RAM/load),
- available agent capacity.
- If resources are insufficient for a new run:
- do not start it,
- inform user: `not possible now, waiting for resources`,
- notify user when resources become available.

### Permission Model
Use role-based permissions per conversation run:
- Worker agents: full development permissions for coding/testing/docs on isolated branches/worktrees.
- Merge Coordinator (single role): only one coordinator can perform integration and prepare merge candidate.
- Main branch merge is serialized and user-gated.

Rationale: prevents multiple agents merging simultaneously and creating conflict loops.

### Clarification Handling
- If one subtask needs user clarification, unrelated subtasks continue.
- Only dependent task graph branches pause.

### Completion Criteria (All Required)
A conversation can be marked `Completed` only when all are true:
- all planned tasks done,
- tests pass (host + target where relevant),
- design/docs updated,
- final integration complete,
- user approval/sign-off.

### Notification Priority (Left Pane)
When multiple statuses exist, priority order:
1. `Needs User Input`
2. `Failed/Error`
3. `Completed`
4. `In Progress`
5. `Queued/Saved`

## 12. API Design
- `GET /state` -> full app state including phase/gate.
- `GET /events?since=` -> incremental events.
- `POST /chat` -> start batch (`text`, `target_agent_id`, `batch_turns`).
- `POST /continue` -> continue paused run (`batch_turns`).
- `POST /steer` -> set steering/preference notes (+ optional auto continue).
- `POST /stop` -> stop active run.
- `POST /phase` -> set active workflow phase.
- `POST /gate/approve` -> user approves phase gate.
- `POST /agents` -> upsert ordered agents.
- `POST /settings` -> update workdir/batch/timeouts/token.
- `GET /conversations` -> list conversation metadata for history pane.
- `POST /conversations/new` -> create conversation.
- `POST /conversations/select` -> activate conversation + build checkpoint-based smart resume pack.
- `POST /conversations/delete` -> delete one conversation.
- `POST /conversations/clear-all` -> clear all conversations with confirmation token.
- `GET /personalities` -> list profiles.
- `GET /scheduler/status` -> resource and queue status.
- `POST /scheduler/recheck` -> force immediate capacity re-evaluation.
- `POST /conversations/notify-ack` -> mark conversation notification as read.

## 13. Prompt Contract
Every agent turn should include mandatory output markers:
- `AGREEMENT_STATUS: AGREE|CONTINUE`
- `PHASE_STATUS: READY_FOR_GATE|NEEDS_MORE_WORK`
- `NEXT_ACTION: <one-line concrete next step>`
- `PATTERN_DECISION: <pattern name or "none-needed" with short reason>`

## 13.5 Batch Artifact Contract (Required)
After every batch, orchestrator must publish a structured artifact with:

- `Agreement Map`: points where worker agents agree.
- `Conflict Map`: explicit disagreement rows (`Agent A`, `Agent B`, `topic`, `difference`).
- `Ollama Neutral Memo`: neutral framing, recommendation, and gate hint.

Example schema:
```json
{
  "batch_id": "...",
  "topic": "...",
  "agreement_map": ["..."],
  "conflict_map": [
    {
      "topic": "buffer ownership",
      "agent_a": "codex",
      "agent_b": "claude",
      "agent_a_position": "...",
      "agent_b_position": "..."
    }
  ],
  "ollama_neutral_memo": {
    "decision_framing": "...",
    "recommended_path": ["..."],
    "gate_status": "READY_FOR_GATE|NEEDS_MORE_WORK"
  }
}
```

UI must display this artifact in three cards: `Agreements`, `Disagreements`, `Neutral Memo`.

## 14. Optional Ollama Manager Agent
Purpose: coordination quality, not code authority.

Manager modes:
- `post_batch_moderator` (recommended): run after each batch.
- `in_round_robin` (optional): included as a normal ordered agent.

Manager responsibilities:
- Summarize drift/risk after each batch.
- Produce neutral decision memo when worker agents disagree.
- Provide gate-check recommendation (`READY_FOR_GATE` / `NEEDS_MORE_WORK`).
- Generate compact memory summary for next-batch prompts.

Suggested endpoints:
- `POST /moderate`
- `POST /summarize`
- `POST /gate-check`

Suggested local call:
- `ollama run <model> <prompt>`

## 15. Memory Plan
- JSONL transcript: source of truth.
- SQLite local index: fast query/filter.
- Markdown batch summaries: human-readable and reusable in prompts.

## 16. Safety and Reliability
- Per-turn timeout and retry policy.
- Structured error events in chat timeline.
- Validated workdir.
- Access token required for LAN deployment.

## 17. Milestones
1. M1: Core orchestrator with batch/pause/continue + strict order
2. M2: Agent roster management + session continuity + workdir controls
3. M3: Workflow phases/gates + prompt contracts
4. M4: Steering/preference controls + agreement handling
5. M5: UI redesign (avatars, bubbles, typing, control strips)
6. M6: Memory layer (JSONL + SQLite + markdown summaries)
7. M7: Hardening, tests, deployment docs

## 18. Acceptance Criteria
- User can run 3+ agents in deterministic round-robin order.
- System pauses every N turns and waits for explicit user decision.
- User steering and preference notes alter subsequent debate direction.
- Phase/gate workflow is visible and enforceable.
- TDD planning occurs before implementation phase progression.
- Coding standards policy is consistently applied in generated plans.
- Pattern selection rationale is visible in implementation-oriented responses.
- Batch artifacts show Agreement Map, Conflict Map, and Ollama Neutral Memo.
- User can see exactly where Codex and Claude disagree per topic.
- Session IDs, transcripts, and summaries are persisted.
- UI is clear on desktop and mobile.
- Conversation history is scrollable and supports delete/clear-all actions.
- Conversation selection resumes with a bounded token context pack (works with or without provider session IDs).
- Resume does not replay full transcript by default.
