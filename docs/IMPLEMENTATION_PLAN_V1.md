# Implementation Plan v1

## 1. Stack Decision
## Backend
- Language: Python 3.12+
- Framework: FastAPI
- Storage: SQLite (WAL) + JSONL logs
- Testing: pytest, pytest-asyncio, httpx
- Quality: ruff, black, mypy

## Frontend
- Language: TypeScript
- Framework: React + Vite
- State: React Query + local reducer/store (or Zustand)
- Testing: Vitest + Playwright (critical flows)
- Styling: CSS variables + modular components

## 2. Architecture Modules
## Backend Modules
- `src/backend/api/` HTTP routes
- `src/backend/core/` orchestration engine, phase/gate logic
- `src/backend/scheduler/` capacity checks, queue, background run control
- `src/backend/adapters/` codex/claude/ollama adapters
- `src/backend/storage/` repositories, schema, migrations
- `src/backend/resume/` checkpoint + context pack builder
- `src/backend/notifications/` status priority and badge state

## Frontend Modules
- `src/frontend/app/` app shell and routing
- `src/frontend/features/topbar/`
- `src/frontend/features/history/`
- `src/frontend/features/chat/`
- `src/frontend/features/intelligence/`
- `src/frontend/features/controls/`
- `src/frontend/shared/api/` typed API client
- `src/frontend/shared/types/` generated/static contracts

## 3. Delivery Strategy
Use vertical slices with TDD gates. Each slice includes:
1. backend logic tests first,
2. API tests,
3. frontend integration,
4. UI smoke test,
5. doc update.

## 4. Sprint Plan
## Sprint 0: Project Bootstrap
### Goals
- repo structure, toolchain, CI scripts, lint/test commands.

### Deliverables
- `pyproject.toml`, backend package scaffold.
- `package.json`, Vite React TS scaffold.
- unified dev command and readme setup.

### TDD Tasks
- add baseline test harness for backend and frontend.

### Exit Criteria
- `pytest`, `ruff`, `mypy`, `vitest` all runnable.

## Sprint 1: Conversation History Core
### Goals
- create/select/delete/clear conversation workflows.

### Backend
- schema for conversation metadata.
- endpoints: `GET /conversations`, `POST /conversations/new`, `select`, `delete`, `clear-all`.

### Frontend
- left pane history list with active selection and status tags.

### TDD First
- repository tests for conversation CRUD.
- API tests for each endpoint.
- UI test for selection and active highlight.

### Exit Criteria
- scrollable history works with 100+ rows.

## Sprint 2: Chat Stream and Events
### Goals
- linear message stream with polling updates.

### Backend
- `message_event` persistence + `GET /events?since=`.

### Frontend
- Slack-like stream: avatar, bold name, timestamp, text.
- composer + target-agent selector.

### TDD First
- event ordering tests.
- incremental polling test.
- UI smoke test for new message append.

### Exit Criteria
- stream remains stable under rapid updates.

## Sprint 3: Batch Orchestration Loop
### Goals
- run/pause/continue/stop for one conversation.

### Backend
- orchestration loop with batch limit and pause state.
- endpoints: `/chat`, `/continue`, `/stop`.

### Frontend
- top and bottom controls wired to real state.

### TDD First
- state machine tests for `idle/running/paused/stopped`.
- API tests for invalid transitions.

### Exit Criteria
- exactly N turns run then pause.

## Sprint 4: Checkpoint Resume (Session-ID Optional)
### Goals
- deterministic resume without relying on provider session IDs.

### Backend
- checkpoint writer per batch.
- context-pack builder with token caps.
- dual mode: `continue-session` or `reconstruct`.

### Frontend
- resume source indicator in chat header/history.

### TDD First
- resume builder tests with cap/truncation.
- fallback tests with missing/expired session IDs.

### Exit Criteria
- resume works accurately with and without provider session.

## Sprint 5: Background Scheduler + Capacity Control
### Goals
- multiple conversations can run in background.

### Backend
- auto-throttle scheduler using resource snapshots.
- queue/waiting states and resource-ready notifications.

### Frontend
- left pane statuses update without selecting conversation.

### TDD First
- scheduler admission/denial tests.
- notification emission tests.

### Exit Criteria
- cannot start when capacity unavailable; user gets clear notification later.

## Sprint 6: Task Division + Coordinator Pipeline
### Goals
- divide labor among agents and serialize integration/merge.

### Backend
- task model + assignment logic.
- worker vs merge coordinator enforcement.

### Frontend
- task overview panel (basic) in active conversation.

### TDD First
- coordinator-only merge path tests.
- unrelated-task continuation when one branch blocked.

### Exit Criteria
- no concurrent direct-main merges possible.

## Sprint 7: Intelligence Pane + Ollama Moderator
### Goals
- batch artifact generation and display.

### Backend
- artifact builders: agreement/conflict/memo.
- endpoints: `/moderate`, `/summarize`, `/gate-check`.

### Frontend
- right pane cards fully dynamic.

### TDD First
- artifact schema validation tests.
- UI test for applying memo as steering.

### Exit Criteria
- user can steer next batch from intelligence panel alone.

## Sprint 8: Hardening and Release Candidate
### Goals
- performance, resilience, deployment docs.

### Backend
- retry policies, timeout handling, dedupe safeguards.

### Frontend
- responsive polish and accessibility cleanup.

### TDD First
- end-to-end scenario:
- debate -> agreement -> go-ahead -> task split -> autonomous work -> integration -> notify -> sign-off.

### Exit Criteria
- release candidate quality.

## 5. TDD Rules (Project-Wide)
- No feature code before failing test exists.
- Every bug fix includes regression test.
- Merge blocked if tests/lint/typecheck fail.

## 6. Suggested Initial File Skeleton (Superseded by 6.1)
```text
src/
  backend/
    api/
    core/
    scheduler/
    adapters/
    storage/
    resume/
    notifications/
  frontend/
    app/
    features/
      topbar/
      history/
      chat/
      intelligence/
      controls/
    shared/
      api/
      types/
```


## 6.1 Directory Structure (Aligned to Component-First + Modular OOP Strategy)
```text
agent-orchestrator-web/
  src/
    backend/
      api/
        routes/
        schemas/
      core/
        orchestrator/
        workflow/
        tasks/
      scheduler/
      adapters/
      storage/
        repositories/
        migrations/
      models/
      services/
      resume/
      notifications/

    frontend/
      app/
      components/
        primitives/
          Button/
          Select/
          Input/
          Textarea/
          Badge/
          Avatar/
          Icon/
        composites/
          ConversationRow/
          MessageRow/
          StatusTag/
      features/
        topbar/
        history/
        chat/
        intelligence/
        controls/
      models/
      services/
      pages/
      hooks/
      shared/
        api/
        types/
        utils/

  docs/
    design/
    playbook/
    saga/
    decisions/
    changelog/
    specs/
    templates/
    checklists/

  data/
    conversations.json
    transcripts/
    summaries/
    artifacts/
    checkpoints/
```

### Build Order Rule
1. Build UI primitives first (`components/primitives`).
2. Build domain models/services second.
3. Build feature pages from those building blocks.
4. Integrate into app shell last.

### Commit Strategy
- Commit in small, vertical slices with tests and docs updates together.
- Avoid broad multi-feature commits.

## 7. Milestone Review Cadence
- End of each sprint:
- demo UI behavior,
- review test coverage delta,
- review performance metrics,
- review docs changes.

## 8. Definition of Done (Global)
A slice is done only if:
- implementation complete,
- tests pass,
- docs updated,
- observable in UI,
- no critical regressions.
