# ADR-003: Checkpoint-First Resume Strategy

## Status: Accepted

## Context

Conversations in the orchestrator can span many turns across multiple batch windows. When resuming a conversation, we need to provide agents with enough context to continue meaningfully. Two approaches were considered:

1. **Full replay** -- feed the entire conversation transcript back to the agent. This is simple but scales poorly: token costs grow linearly, context windows overflow, and resume latency increases with conversation length.
2. **Checkpoint-first** -- build a compact context pack (summary + key decisions + recent events) bounded by a token budget. This is more complex to build but keeps resume cost constant regardless of conversation length.

## Decision

We chose checkpoint-first resume, implemented in `CheckpointBuilder` (`backend/src/agent_orchestrator/storage/checkpoint.py`).

Key design points:

- **CheckpointPack structure**: A dataclass containing `conversation_id`, `summary` (free-text), `key_decisions` (list of strings), `recent_events` (last N event dicts from the JSONL log), `token_estimate`, and `created_at`.
- **Token-bounded context packs**: The builder is configured with `max_token_estimate` (default 4000 tokens) and `max_recent_events` (default 20). The `build()` method takes the last `max_recent_events` from the event log and estimates the total token count.
- **Token estimation**: `estimate_tokens()` uses a simple heuristic: `word_count * 1.3`, rounded to an integer. This avoids importing a tokenizer library while providing a reasonable approximation for English text mixed with JSON.
- **Two-phase compaction**: The `compact()` method reduces an over-budget pack in two phases:
  1. **Phase 1 -- Event trimming**: Drop the oldest recent events one at a time, re-estimating tokens after each removal, until the pack fits within `max_token_estimate`.
  2. **Phase 2 -- Summary truncation**: If removing all events is still not enough, progressively truncate the summary by removing words from the end until the budget is met.
  - Key decisions are never trimmed -- they are considered the most critical context for maintaining conversation coherence.
- **Event source**: Events can be provided directly as a list of dicts, or the builder reads them from the JSONL event log on disk using `EventLogReader`. The `log_path` parameter allows overriding the default path.
- **`_pack_text()` helper**: Combines summary, key decisions, and JSON-serialized events into a single string for token estimation. This ensures the estimate accounts for all content that would be sent to an agent.

## Consequences

- **Constant resume cost**: Regardless of how long a conversation has been running, resume context stays within the token budget. This keeps costs predictable and avoids context window overflow.
- **Lossy by design**: Compaction discards information. Old events are lost first (acceptable since they are least relevant), and in extreme cases the summary is truncated. Key decisions are preserved as the irreducible minimum.
- **Approximation risk**: The `words * 1.3` heuristic may under- or over-estimate actual token counts, especially for JSON-heavy content or non-English text. This is acceptable for a local-first tool where precision matters less than simplicity.
- **No incremental updates**: Currently, checkpoints are built from scratch each time rather than incrementally updated. This is fine for conversations with up to hundreds of events but could become a bottleneck at larger scales.
- **Integration point**: The checkpoint pack is designed to be serialized and injected as a prompt prefix when resuming a session via `BaseAdapter.resume_session()`.
