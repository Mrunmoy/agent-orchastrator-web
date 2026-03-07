# Playbook 02: Adapter Failures

CLI adapters (Claude, Codex, Ollama) fail consistently when invoked by the batch runner.

## Symptoms

- `TurnRecord.status` is `AdapterStatus.ERROR` or `AdapterStatus.TIMED_OUT` for one or more turns.
- `TurnRecord.response_text` is empty (`""`) on error turns.
- The batch completes all its turns but every response is an error, producing no useful output.
- `adapter.is_available()` returns `False`.

## Diagnosis

### 1. Check adapter availability

Every adapter implements `BaseAdapter.is_available() -> bool`. This checks whether the underlying CLI tool (e.g., `claude`, `codex`) is installed and reachable on the system.

```python
# base.py -- BaseAdapter ABC
@abc.abstractmethod
def is_available(self) -> bool:
    """Check if the CLI tool is available on the system."""
```

Call `adapter.is_available()` for each adapter in the `adapter_map` to identify which ones are failing.

### 2. Check the AdapterResult status

Successful calls return an `AdapterResult` with `status=AdapterStatus.IDLE`. The possible values are:

| Status | Meaning |
|--------|---------|
| `IDLE` | Call succeeded, response ready |
| `RUNNING` | Adapter is still processing (should not appear in turn records) |
| `TIMED_OUT` | CLI agent exceeded `timeout_seconds` (default 120s) |
| `ERROR` | Exception during `send_prompt()` or `resume_session()` |

### 3. Verify the CLI binary is installed

The adapters shell out to CLI tools. Verify the binary exists:

```bash
which claude    # for Claude adapter
which codex     # for Codex adapter
which ollama    # for Ollama adapter
```

### 4. Check the working directory

`send_prompt()` accepts a `working_dir` parameter. The batch runner passes `"."` by default. If the adapter's working directory does not exist or lacks permissions, the CLI invocation will fail.

```python
# batch_runner.py line 118-121
result = await adapter.send_prompt(
    prompt,
    working_dir=".",
)
```

### 5. Check timeout configuration

The default timeout is 120 seconds (defined in `BaseAdapter.send_prompt` signature). Complex prompts or slow models may exceed this. Ollama running large local models is particularly susceptible.

## Recovery

### Fix 1: Install or reinstall the CLI tool

Ensure the CLI binary is on `$PATH` and functional:

```bash
# Test Claude CLI
claude --version

# Test Codex CLI
codex --version

# Test Ollama
ollama list
```

### Fix 2: Adjust timeout

If `TIMED_OUT` errors are frequent, increase `timeout_seconds` when constructing adapter calls. The `BaseAdapter.send_prompt()` signature accepts this:

```python
await adapter.send_prompt(
    prompt,
    working_dir="/path/to/project",
    timeout_seconds=300.0,  # 5 minutes instead of default 2
)
```

### Fix 3: Verify working directory

Ensure the `working_dir` passed to `send_prompt()` is a valid, accessible directory. For the batch runner, this is currently hardcoded to `"."`.

### Fix 4: Check session state

For `resume_session()` calls, verify the `session_id` is valid. If a session has expired or was cleaned up by the CLI tool, the adapter will error. Fall back to `send_prompt()` with a fresh session.

### Fix 5: Restart after fix

After resolving the underlying issue, create a new `BatchRunner` with fresh adapters. The batch runner does not retry failed turns -- each turn is attempted once and the result (success or error) is recorded in `turn_log`.

## Code References

- `backend/src/agent_orchestrator/adapters/base.py` -- `BaseAdapter` ABC, `AdapterResult`, `AdapterStatus` enum.
- `backend/src/agent_orchestrator/orchestrator/batch_runner.py` -- exception handling in `run()` (lines 116-141), `TurnRecord` dataclass.
- `backend/src/agent_orchestrator/adapters/claude_adapter.py` -- Claude CLI adapter implementation.
- `backend/src/agent_orchestrator/adapters/codex_adapter.py` -- Codex CLI adapter implementation.
