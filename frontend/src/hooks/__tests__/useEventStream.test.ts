import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

import type { BackendEvent } from "../../api/client";
import { useEventStream } from "../useEventStream";

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

const mockFetchEvents = vi.fn<(id: string, since?: string) => Promise<BackendEvent[]>>();
const mockFetchLatestEvents = vi.fn<(id: string, n?: number) => Promise<BackendEvent[]>>();

vi.mock("../../api/client", () => ({
  fetchEvents: (...args: unknown[]) =>
    mockFetchEvents(args[0] as string, args[1] as string | undefined),
  fetchLatestEvents: (...args: unknown[]) =>
    mockFetchLatestEvents(args[0] as string, args[1] as number | undefined),
}));

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeEvent(overrides: Partial<BackendEvent> = {}): BackendEvent {
  return {
    event_id: overrides.event_id ?? "evt-1",
    conversation_id: overrides.conversation_id ?? "conv-1",
    source_type: overrides.source_type ?? "agent",
    source_id: overrides.source_id ?? "agent-1",
    text: overrides.text ?? "Hello",
    event_type: overrides.event_type ?? "chat_message",
    timestamp: overrides.timestamp ?? "2026-03-08T00:00:00Z",
    metadata_json: overrides.metadata_json ?? "{}",
  };
}

/** Flush microtasks so async effects / resolved promises settle. */
async function flushPromises() {
  await act(async () => {
    await new Promise((r) => setTimeout(r, 0));
  });
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("useEventStream", () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    mockFetchEvents.mockReset();
    mockFetchLatestEvents.mockReset();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("returns empty events when conversationId is null", async () => {
    const { result } = renderHook(() => useEventStream(null));
    await flushPromises();

    expect(result.current.events).toEqual([]);
    expect(result.current.isConnected).toBe(false);
    expect(result.current.error).toBeNull();
    expect(mockFetchLatestEvents).not.toHaveBeenCalled();
    expect(mockFetchEvents).not.toHaveBeenCalled();
  });

  it("fetches initial events using fetchLatestEvents on first poll", async () => {
    const events = [makeEvent({ event_id: "e1" }), makeEvent({ event_id: "e2" })];
    mockFetchLatestEvents.mockResolvedValueOnce(events);

    const { result } = renderHook(() =>
      useEventStream("conv-1", { pollIntervalMs: 5000 }),
    );

    await flushPromises();

    expect(mockFetchLatestEvents).toHaveBeenCalledWith("conv-1", 50);
    expect(result.current.isConnected).toBe(true);
    expect(result.current.events).toHaveLength(2);
    expect(result.current.events[0]?.id).toBe("e1");
    expect(result.current.events[1]?.id).toBe("e2");
  });

  it("uses fetchEvents with since param on subsequent polls", async () => {
    const initialEvents = [makeEvent({ event_id: "e1" })];
    mockFetchLatestEvents.mockResolvedValueOnce(initialEvents);

    const { result } = renderHook(() =>
      useEventStream("conv-1", { pollIntervalMs: 1000 }),
    );

    await flushPromises();
    expect(result.current.events).toHaveLength(1);

    // Set up next poll.
    const newEvents = [makeEvent({ event_id: "e2", text: "World" })];
    mockFetchEvents.mockResolvedValueOnce(newEvents);

    // Advance timer to trigger interval.
    await act(async () => {
      vi.advanceTimersByTime(1000);
    });
    await flushPromises();

    expect(mockFetchEvents).toHaveBeenCalledWith("conv-1", "e1");
    expect(result.current.events).toHaveLength(2);
    expect(result.current.events[1]?.id).toBe("e2");
  });

  it("does not duplicate events", async () => {
    const events = [makeEvent({ event_id: "e1" })];
    mockFetchLatestEvents.mockResolvedValueOnce(events);

    const { result } = renderHook(() =>
      useEventStream("conv-1", { pollIntervalMs: 1000 }),
    );

    await flushPromises();
    expect(result.current.events).toHaveLength(1);

    // Return the same event again.
    mockFetchEvents.mockResolvedValueOnce([makeEvent({ event_id: "e1" })]);

    await act(async () => {
      vi.advanceTimersByTime(1000);
    });
    await flushPromises();

    expect(mockFetchEvents).toHaveBeenCalled();
    expect(result.current.events).toHaveLength(1);
  });

  it("sets error state on fetch failure", async () => {
    mockFetchLatestEvents.mockRejectedValueOnce(new Error("Network error"));

    const { result } = renderHook(() =>
      useEventStream("conv-1", { pollIntervalMs: 5000 }),
    );

    await flushPromises();

    expect(result.current.error).not.toBeNull();
    expect(result.current.error?.message).toBe("Network error");
    expect(result.current.isConnected).toBe(false);
  });

  it("recovers from error on successful poll", async () => {
    mockFetchLatestEvents.mockRejectedValueOnce(new Error("Network error"));

    const { result } = renderHook(() =>
      useEventStream("conv-1", { pollIntervalMs: 1000 }),
    );

    await flushPromises();
    expect(result.current.error).not.toBeNull();

    // Next poll succeeds (initial load not done due to error, so fetchLatestEvents again).
    mockFetchLatestEvents.mockResolvedValueOnce([makeEvent({ event_id: "e1" })]);

    await act(async () => {
      vi.advanceTimersByTime(1000);
    });
    await flushPromises();

    expect(result.current.isConnected).toBe(true);
    expect(result.current.error).toBeNull();
  });

  it("does not poll when enabled is false", async () => {
    const { result } = renderHook(() =>
      useEventStream("conv-1", { enabled: false }),
    );

    await act(async () => {
      vi.advanceTimersByTime(10000);
    });
    await flushPromises();

    expect(mockFetchLatestEvents).not.toHaveBeenCalled();
    expect(mockFetchEvents).not.toHaveBeenCalled();
    expect(result.current.isConnected).toBe(false);
  });

  it("resets events when conversationId changes", async () => {
    const events = [makeEvent({ event_id: "e1" })];
    mockFetchLatestEvents.mockResolvedValueOnce(events);

    const { result, rerender } = renderHook(
      ({ convId }: { convId: string | null }) =>
        useEventStream(convId, { pollIntervalMs: 5000 }),
      { initialProps: { convId: "conv-1" as string | null } },
    );

    await flushPromises();
    expect(result.current.events).toHaveLength(1);

    // Change conversation.
    const newEvents = [makeEvent({ event_id: "e5", conversation_id: "conv-2" })];
    mockFetchLatestEvents.mockResolvedValueOnce(newEvents);

    rerender({ convId: "conv-2" });
    await flushPromises();

    expect(result.current.events).toHaveLength(1);
    expect(result.current.events[0]?.id).toBe("e5");
  });

  it("cleans up interval on unmount", async () => {
    mockFetchLatestEvents.mockResolvedValue([]);

    const { unmount } = renderHook(() =>
      useEventStream("conv-1", { pollIntervalMs: 1000 }),
    );

    await flushPromises();
    expect(mockFetchLatestEvents).toHaveBeenCalledTimes(1);

    unmount();
    mockFetchLatestEvents.mockClear();

    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    await flushPromises();

    expect(mockFetchLatestEvents).not.toHaveBeenCalled();
    expect(mockFetchEvents).not.toHaveBeenCalled();
  });

  it("transforms metadata_json into parsed metadata object", async () => {
    const events = [
      makeEvent({
        event_id: "e1",
        metadata_json: '{"round": 2, "phase": "debate"}',
      }),
    ];
    mockFetchLatestEvents.mockResolvedValueOnce(events);

    const { result } = renderHook(() => useEventStream("conv-1"));
    await flushPromises();

    expect(result.current.events).toHaveLength(1);
    expect(result.current.events[0]?.metadata).toEqual({
      round: 2,
      phase: "debate",
    });
  });

  it("uses created_at as fallback when timestamp is missing", async () => {
    const event = makeEvent({ event_id: "e1" });
    // Remove timestamp, set created_at.
    delete (event as Record<string, unknown>)["timestamp"];
    (event as Record<string, unknown>)["created_at"] = "2026-03-08T12:00:00Z";
    mockFetchLatestEvents.mockResolvedValueOnce([event]);

    const { result } = renderHook(() => useEventStream("conv-1"));
    await flushPromises();

    expect(result.current.events).toHaveLength(1);
    expect(result.current.events[0]?.timestamp).toBe("2026-03-08T12:00:00Z");
  });
});
