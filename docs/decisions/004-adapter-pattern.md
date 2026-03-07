# ADR-004: Adapter Pattern for CLI Agents

## Status: Accepted

## Context

The orchestrator manages multiple CLI agent types (Claude, Codex, Ollama) that have different command-line interfaces, output formats, and session management mechanisms. We need a uniform interface so the batch runner and scheduler can interact with any agent without knowing its implementation details.

## Decision

We chose an abstract base class (ABC) pattern, implemented in `BaseAdapter` (`backend/src/agent_orchestrator/adapters/base.py`).

Key design points:

- **Three abstract methods**:
  1. `send_prompt(prompt, *, working_dir, session_id=None, timeout_seconds=120.0) -> AdapterResult` -- Send a prompt to the CLI agent. The `working_dir` parameter sets the subprocess working directory. Optional `session_id` allows attaching to an existing session.
  2. `resume_session(session_id, prompt, *, working_dir, timeout_seconds=120.0) -> AdapterResult` -- Resume a specific session with a new prompt. This is a separate method (rather than just using `session_id` on `send_prompt`) to make the intent explicit and allow adapters to use different CLI flags for resumption.
  3. `is_available() -> bool` -- Synchronous check for whether the CLI tool is installed and reachable on the system. Called before attempting to use an adapter.

- **AdapterResult contract**: A dataclass returned by both `send_prompt` and `resume_session`:
  - `text: str` -- The agent's response text (normalized from CLI output).
  - `session_id: str | None` -- The session identifier for future resume calls, or `None` if sessions are not supported.
  - `status: AdapterStatus` -- One of `IDLE`, `RUNNING`, `TIMED_OUT`, or `ERROR`.
  - `metadata: dict` -- Arbitrary key-value pairs for adapter-specific data (token counts, exit codes, etc.).

- **AdapterStatus enum**: Defines four states:
  - `IDLE` -- The adapter completed successfully and is ready for the next call.
  - `RUNNING` -- Included for completeness but not typically returned (the adapter blocks until completion).
  - `TIMED_OUT` -- The CLI subprocess exceeded `timeout_seconds`.
  - `ERROR` -- The CLI subprocess failed (non-zero exit, parse error, etc.).

- **Output normalization**: Each concrete adapter is responsible for extracting clean response text from CLI output, which may include ANSI escape codes, progress indicators, or structured JSON. The `text` field on `AdapterResult` should contain only the meaningful response content.

## Consequences

- **Uniform batch runner integration**: The `BatchRunner` holds a `dict[str, BaseAdapter]` mapping agent IDs to adapters. It calls `send_prompt()` without knowing whether the underlying agent is Claude, Codex, or Ollama.
- **Easy to add new agents**: Adding support for a new CLI tool (e.g., Gemini) requires implementing a single class with three methods. No changes to the scheduler or batch runner are needed.
- **Async interface**: Both `send_prompt` and `resume_session` are `async` methods, allowing the batch runner to use `await` even though current implementations are subprocess-based. This leaves room for future HTTP-based adapters.
- **Timeout delegation**: Each adapter manages its own subprocess timeout using the `timeout_seconds` parameter. The batch runner does not enforce its own timeout, trusting the adapter to respect it.
- **No streaming**: The current interface returns complete responses, not streaming chunks. If real-time output display is needed in the UI, the adapter interface would need a streaming variant.
