import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

import type { Artifact, ArtifactType } from "../../api/client";
import { useArtifacts } from "../useArtifacts";

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

const mockFetchArtifacts = vi.fn<
  (id: string, type?: ArtifactType) => Promise<Artifact[]>
>();

vi.mock("../../api/client", () => ({
  fetchArtifacts: (...args: unknown[]) =>
    mockFetchArtifacts(args[0] as string, args[1] as ArtifactType | undefined),
}));

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeArtifact(overrides: Partial<Artifact> = {}): Artifact {
  return {
    id: overrides.id ?? "art-1",
    conversation_id: overrides.conversation_id ?? "conv-1",
    type: overrides.type ?? "agreement_map",
    payload_json: overrides.payload_json ?? '{"summary":"All agree"}',
    created_at: overrides.created_at ?? "2026-03-08T00:00:00Z",
    batch_id: overrides.batch_id ?? null,
  };
}

async function flushPromises() {
  await act(async () => {
    await new Promise((r) => setTimeout(r, 0));
  });
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("useArtifacts", () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    mockFetchArtifacts.mockReset();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("returns null artifacts when conversationId is null", async () => {
    const { result } = renderHook(() => useArtifacts(null));
    await flushPromises();

    expect(result.current.agreementMap).toBeNull();
    expect(result.current.conflictMap).toBeNull();
    expect(result.current.neutralMemo).toBeNull();
    expect(result.current.isLoaded).toBe(false);
    expect(mockFetchArtifacts).not.toHaveBeenCalled();
  });

  it("fetches all three artifact types on first poll", async () => {
    const agreement = makeArtifact({ id: "a1", type: "agreement_map" });
    const conflict = makeArtifact({
      id: "c1",
      type: "conflict_map",
      payload_json: '{"summary":"Disagree on X"}',
    });
    const memo = makeArtifact({
      id: "m1",
      type: "neutral_memo",
      payload_json: '{"summary":"Neutral take"}',
    });

    mockFetchArtifacts.mockImplementation(async (_id, type) => {
      if (type === "agreement_map") return [agreement];
      if (type === "conflict_map") return [conflict];
      if (type === "neutral_memo") return [memo];
      return [];
    });

    const { result } = renderHook(() =>
      useArtifacts("conv-1", { pollIntervalMs: 5000 }),
    );

    await flushPromises();

    expect(mockFetchArtifacts).toHaveBeenCalledWith("conv-1", "agreement_map");
    expect(mockFetchArtifacts).toHaveBeenCalledWith("conv-1", "conflict_map");
    expect(mockFetchArtifacts).toHaveBeenCalledWith("conv-1", "neutral_memo");
    expect(result.current.agreementMap).toEqual(agreement);
    expect(result.current.conflictMap).toEqual(conflict);
    expect(result.current.neutralMemo).toEqual(memo);
    expect(result.current.isLoaded).toBe(true);
    expect(result.current.error).toBeNull();
  });

  it("returns the most recent artifact when multiple exist", async () => {
    const older = makeArtifact({
      id: "a1",
      type: "agreement_map",
      created_at: "2026-03-07T00:00:00Z",
      payload_json: '{"summary":"Old"}',
    });
    const newer = makeArtifact({
      id: "a2",
      type: "agreement_map",
      created_at: "2026-03-08T00:00:00Z",
      payload_json: '{"summary":"New"}',
    });

    mockFetchArtifacts.mockImplementation(async (_id, type) => {
      if (type === "agreement_map") return [older, newer];
      return [];
    });

    const { result } = renderHook(() => useArtifacts("conv-1"));
    await flushPromises();

    expect(result.current.agreementMap?.id).toBe("a2");
  });

  it("returns null for artifact types with no data", async () => {
    mockFetchArtifacts.mockResolvedValue([]);

    const { result } = renderHook(() => useArtifacts("conv-1"));
    await flushPromises();

    expect(result.current.agreementMap).toBeNull();
    expect(result.current.conflictMap).toBeNull();
    expect(result.current.neutralMemo).toBeNull();
    expect(result.current.isLoaded).toBe(true);
  });

  it("sets error on fetch failure", async () => {
    mockFetchArtifacts.mockRejectedValue(new Error("Network error"));

    const { result } = renderHook(() => useArtifacts("conv-1"));
    await flushPromises();

    expect(result.current.error?.message).toBe("Network error");
  });

  it("polls at the configured interval", async () => {
    mockFetchArtifacts.mockResolvedValue([]);

    renderHook(() => useArtifacts("conv-1", { pollIntervalMs: 2000 }));
    await flushPromises();

    // Initial fetch = 3 calls (one per type)
    expect(mockFetchArtifacts).toHaveBeenCalledTimes(3);

    mockFetchArtifacts.mockClear();

    await act(async () => {
      vi.advanceTimersByTime(2000);
    });
    await flushPromises();

    // Second poll = 3 more calls
    expect(mockFetchArtifacts).toHaveBeenCalledTimes(3);
  });

  it("does not poll when enabled is false", async () => {
    renderHook(() => useArtifacts("conv-1", { enabled: false }));

    await act(async () => {
      vi.advanceTimersByTime(10000);
    });
    await flushPromises();

    expect(mockFetchArtifacts).not.toHaveBeenCalled();
  });

  it("resets state when conversationId changes", async () => {
    const agreement = makeArtifact({ id: "a1", type: "agreement_map" });
    mockFetchArtifacts.mockImplementation(async (_id, type) => {
      if (type === "agreement_map") return [agreement];
      return [];
    });

    const { result, rerender } = renderHook(
      ({ convId }: { convId: string | null }) =>
        useArtifacts(convId, { pollIntervalMs: 5000 }),
      { initialProps: { convId: "conv-1" as string | null } },
    );

    await flushPromises();
    expect(result.current.agreementMap).toEqual(agreement);

    // Change conversation — state should reset
    mockFetchArtifacts.mockResolvedValue([]);
    rerender({ convId: "conv-2" });
    await flushPromises();

    expect(result.current.agreementMap).toBeNull();
  });

  it("cleans up interval on unmount", async () => {
    mockFetchArtifacts.mockResolvedValue([]);

    const { unmount } = renderHook(() =>
      useArtifacts("conv-1", { pollIntervalMs: 1000 }),
    );

    await flushPromises();
    expect(mockFetchArtifacts).toHaveBeenCalledTimes(3);

    unmount();
    mockFetchArtifacts.mockClear();

    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    await flushPromises();

    expect(mockFetchArtifacts).not.toHaveBeenCalled();
  });
});
