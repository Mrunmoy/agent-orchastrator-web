# Playbook 07: Checkpoint Recovery

Conversation context is lost, corrupted, or has grown too large to fit within token limits.

## Symptoms

- `CheckpointPack.token_estimate` exceeds `max_token_estimate` (default 4000 tokens).
- A checkpoint has too many `recent_events` and the context pack is bloated.
- The summary is empty or truncated after compaction, indicating the checkpoint was severely over-budget.
- Conversation resume fails because the JSONL event log is missing or unreadable.
- `EventLogReader.read_all()` returns an empty list when events should exist.

## Diagnosis

### 1. Check the token estimate

The `CheckpointBuilder.estimate_tokens()` method uses a rough heuristic: `word_count * 1.3`, rounded to the nearest integer.

```python
builder = CheckpointBuilder(
    conversation_id="conv-123",
    max_recent_events=20,
    max_token_estimate=4000,
)
pack = builder.build(summary="...", key_decisions=[...])
print(f"Token estimate: {pack.token_estimate}")
print(f"Max allowed: {builder.max_token_estimate}")
print(f"Recent events: {len(pack.recent_events)}")
```

### 2. Inspect the checkpoint pack contents

A `CheckpointPack` contains:

| Field | Description |
|-------|-------------|
| `conversation_id` | Which conversation this checkpoint belongs to |
| `summary` | Free-text summary of the conversation so far |
| `key_decisions` | List of important decisions made |
| `recent_events` | Last N events from the JSONL event log (default N=20) |
| `token_estimate` | Estimated token count of all packed content |
| `created_at` | ISO-8601 UTC timestamp |

### 3. Check the event log

The `CheckpointBuilder.build()` method reads events from the JSONL event log if no explicit events list is provided. Verify the log exists and is readable:

```python
from agent_orchestrator.storage.event_log import EventLogReader, conversation_log_path

path = conversation_log_path("conv-123")
print(f"Log path: {path}")
print(f"Exists: {path.exists()}")

reader = EventLogReader(path)
events = reader.read_all()
print(f"Event count: {len(events)}")
```

### 4. Identify compaction impact

After calling `compact()`, check what was trimmed:

- If `recent_events` is shorter than the original, oldest events were dropped.
- If `summary` is shorter than the original, it was truncated word-by-word to fit.
- If `summary` is empty, the checkpoint was severely over-budget and all content was trimmed.

## Recovery

### Fix 1: Compact the checkpoint

The `CheckpointBuilder.compact()` method reduces a checkpoint to fit within `max_token_estimate` using a two-phase approach:

**Phase 1:** Drop oldest recent events one at a time until the estimate fits.
**Phase 2:** If still over budget after removing all events, truncate the summary word-by-word.

```python
oversized_pack = builder.build(summary=long_summary, key_decisions=decisions)
compacted_pack = builder.compact(oversized_pack)
print(f"Before: {oversized_pack.token_estimate} tokens, {len(oversized_pack.recent_events)} events")
print(f"After: {compacted_pack.token_estimate} tokens, {len(compacted_pack.recent_events)} events")
```

### Fix 2: Rebuild from event log

If the checkpoint is corrupted or lost, rebuild it from the JSONL event log:

```python
reader = EventLogReader(conversation_log_path("conv-123"))
events = reader.read_all()

# Generate a fresh summary from the events
summary = "... (manually written or LLM-generated summary) ..."
key_decisions = ["Decision 1", "Decision 2"]

pack = builder.build(
    summary=summary,
    key_decisions=key_decisions,
    events=events,  # pass events directly instead of reading from log
)
```

### Fix 3: Adjust token budget

If checkpoints are consistently too large, increase the budget or reduce the event window:

```python
builder = CheckpointBuilder(
    conversation_id="conv-123",
    max_recent_events=10,     # was 20 -- fewer events in context
    max_token_estimate=8000,  # was 4000 -- allow larger checkpoints
)
```

**Trade-off:** Larger checkpoints provide more context but consume more of the LLM's context window. Fewer recent events mean less immediate conversation history.

### Fix 4: Fix or recreate the event log

If `conversation_log_path()` points to a missing or corrupted file:

1. Check the expected path (derived from `conversation_id`).
2. If the file exists but is corrupted (malformed JSON lines), manually fix or remove bad lines.
3. If the file is missing entirely, the conversation history is lost. Start a new conversation or manually reconstruct the log.

## Prevention

- Monitor `token_estimate` after each batch run and compact proactively.
- Keep summaries concise -- they are the most expensive part of the checkpoint after compaction removes events.
- Use meaningful `key_decisions` entries rather than verbose descriptions.
- Periodically compact long-running conversations to prevent token budget overflow.

## Code References

- `backend/src/agent_orchestrator/storage/checkpoint.py` -- `CheckpointBuilder`, `CheckpointPack`, `build()`, `compact()`, `estimate_tokens()`.
- `backend/src/agent_orchestrator/storage/event_log.py` -- `EventLogReader`, `conversation_log_path()`.
