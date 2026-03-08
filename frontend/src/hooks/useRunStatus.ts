/**
 * useRunStatus — polls the backend for the latest scheduler run status
 * and maps backend statuses to UI display strings.
 */

import { useCallback, useEffect, useRef, useState } from "react";

import { type RunStatusData, fetchRunStatus } from "../api/client";

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export type DisplayStatus = "Idle" | "Running" | "Paused";

export interface UseRunStatusResult {
  status: DisplayStatus;
  run: RunStatusData | null;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const STATUS_MAP: Record<RunStatusData["status"], DisplayStatus> = {
  queued: "Running",
  running: "Running",
  paused: "Paused",
  done: "Idle",
  failed: "Idle",
};

export function mapBackendStatus(backendStatus: RunStatusData["status"]): DisplayStatus {
  return STATUS_MAP[backendStatus];
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

const DEFAULT_POLL_INTERVAL_MS = 3000;

export function useRunStatus(
  conversationId: string | null,
  pollIntervalMs: number = DEFAULT_POLL_INTERVAL_MS,
): UseRunStatusResult {
  const [status, setStatus] = useState<DisplayStatus>("Idle");
  const [run, setRun] = useState<RunStatusData | null>(null);

  // Track conversationId for stale-response protection.
  const activeIdRef = useRef<string | null>(conversationId);
  activeIdRef.current = conversationId;

  const poll = useCallback(async () => {
    if (!conversationId) return;

    const data = await fetchRunStatus(conversationId);

    // Guard against stale responses after conversation switch.
    if (activeIdRef.current !== conversationId) return;

    if (data) {
      setRun(data);
      setStatus(mapBackendStatus(data.status));
    } else {
      setRun(null);
      setStatus("Idle");
    }
  }, [conversationId]);

  // Reset when conversation changes.
  useEffect(() => {
    setStatus("Idle");
    setRun(null);
  }, [conversationId]);

  useEffect(() => {
    if (!conversationId) return;

    void poll();

    const intervalId = setInterval(() => {
      void poll();
    }, pollIntervalMs);

    return () => {
      clearInterval(intervalId);
    };
  }, [conversationId, pollIntervalMs, poll]);

  return { status, run };
}
