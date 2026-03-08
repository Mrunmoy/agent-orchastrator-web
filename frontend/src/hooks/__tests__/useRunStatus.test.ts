import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

import type { RunStatusData } from "../../api/client";
import { useRunStatus, mapBackendStatus } from "../useRunStatus";

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

const mockFetchRunStatus = vi.fn<(id: string) => Promise<RunStatusData | null>>();

vi.mock("../../api/client", () => ({
  fetchRunStatus: (...args: unknown[]) => mockFetchRunStatus(args[0] as string),
}));

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeRun(overrides: Partial<RunStatusData> = {}): RunStatusData {
  return {
    run_id: overrides.run_id ?? "run-1",
    status: overrides.status ?? "running",
    turns_completed: overrides.turns_completed ?? 5,
    turns_total: overrides.turns_total ?? 20,
    started_at: overrides.started_at ?? "2026-03-08T00:00:00Z",
    updated_at: overrides.updated_at ?? "2026-03-08T00:01:00Z",
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

describe("mapBackendStatus", () => {
  it("maps queued to Running", () => {
    expect(mapBackendStatus("queued")).toBe("Running");
  });

  it("maps running to Running", () => {
    expect(mapBackendStatus("running")).toBe("Running");
  });

  it("maps paused to Paused", () => {
    expect(mapBackendStatus("paused")).toBe("Paused");
  });

  it("maps done to Idle", () => {
    expect(mapBackendStatus("done")).toBe("Idle");
  });

  it("maps failed to Idle", () => {
    expect(mapBackendStatus("failed")).toBe("Idle");
  });
});

describe("useRunStatus", () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    mockFetchRunStatus.mockReset();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("returns Idle when conversationId is null", async () => {
    const { result } = renderHook(() => useRunStatus(null));
    await flushPromises();

    expect(result.current.status).toBe("Idle");
    expect(result.current.run).toBeNull();
    expect(mockFetchRunStatus).not.toHaveBeenCalled();
  });

  it("fetches run status immediately when conversationId is provided", async () => {
    const run = makeRun({ status: "running" });
    mockFetchRunStatus.mockResolvedValueOnce(run);

    const { result } = renderHook(() => useRunStatus("conv-1", 5000));
    await flushPromises();

    expect(mockFetchRunStatus).toHaveBeenCalledWith("conv-1");
    expect(result.current.status).toBe("Running");
    expect(result.current.run).toEqual(run);
  });

  it("polls at the specified interval", async () => {
    const run1 = makeRun({ status: "running" });
    const run2 = makeRun({ status: "paused" });
    mockFetchRunStatus.mockResolvedValueOnce(run1);

    const { result } = renderHook(() => useRunStatus("conv-1", 1000));
    await flushPromises();

    expect(result.current.status).toBe("Running");

    mockFetchRunStatus.mockResolvedValueOnce(run2);
    await act(async () => {
      vi.advanceTimersByTime(1000);
    });
    await flushPromises();

    expect(mockFetchRunStatus).toHaveBeenCalledTimes(2);
    expect(result.current.status).toBe("Paused");
    expect(result.current.run).toEqual(run2);
  });

  it("returns Idle when fetchRunStatus returns null", async () => {
    mockFetchRunStatus.mockResolvedValueOnce(null);

    const { result } = renderHook(() => useRunStatus("conv-1", 5000));
    await flushPromises();

    expect(result.current.status).toBe("Idle");
    expect(result.current.run).toBeNull();
  });

  it("resets status when conversationId changes", async () => {
    const run = makeRun({ status: "running" });
    mockFetchRunStatus.mockResolvedValueOnce(run);

    const { result, rerender } = renderHook(
      ({ convId }: { convId: string | null }) => useRunStatus(convId, 5000),
      { initialProps: { convId: "conv-1" as string | null } },
    );

    await flushPromises();
    expect(result.current.status).toBe("Running");

    // Switch conversation — should reset to Idle then fetch new status.
    const run2 = makeRun({ status: "paused" });
    mockFetchRunStatus.mockResolvedValueOnce(run2);

    rerender({ convId: "conv-2" });
    await flushPromises();

    expect(result.current.status).toBe("Paused");
    expect(result.current.run).toEqual(run2);
  });

  it("resets to Idle when conversationId becomes null", async () => {
    const run = makeRun({ status: "running" });
    mockFetchRunStatus.mockResolvedValueOnce(run);

    const { result, rerender } = renderHook(
      ({ convId }: { convId: string | null }) => useRunStatus(convId, 5000),
      { initialProps: { convId: "conv-1" as string | null } },
    );

    await flushPromises();
    expect(result.current.status).toBe("Running");

    rerender({ convId: null });
    await flushPromises();

    expect(result.current.status).toBe("Idle");
    expect(result.current.run).toBeNull();
  });

  it("cleans up interval on unmount", async () => {
    mockFetchRunStatus.mockResolvedValue(makeRun());

    const { unmount } = renderHook(() => useRunStatus("conv-1", 1000));
    await flushPromises();

    expect(mockFetchRunStatus).toHaveBeenCalledTimes(1);

    unmount();
    mockFetchRunStatus.mockClear();

    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    await flushPromises();

    expect(mockFetchRunStatus).not.toHaveBeenCalled();
  });

  it("maps done status to Idle", async () => {
    mockFetchRunStatus.mockResolvedValueOnce(makeRun({ status: "done" }));

    const { result } = renderHook(() => useRunStatus("conv-1"));
    await flushPromises();

    expect(result.current.status).toBe("Idle");
  });

  it("maps queued status to Running", async () => {
    mockFetchRunStatus.mockResolvedValueOnce(makeRun({ status: "queued" }));

    const { result } = renderHook(() => useRunStatus("conv-1"));
    await flushPromises();

    expect(result.current.status).toBe("Running");
  });
});
