/**
 * useArtifacts — polls the backend for structured artifacts (agreement maps,
 * conflict maps, neutral memos) associated with the selected conversation.
 *
 * Uses `GET /api/artifacts?conversation_id=X&type=Y` to fetch each artifact
 * type independently and exposes the latest of each.
 */

import { useCallback, useEffect, useRef, useState } from "react";

import { type Artifact, fetchArtifacts } from "../api/client";

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export interface UseArtifactsOptions {
  /** Polling interval in milliseconds. Default 5000. */
  pollIntervalMs?: number;
  /** Whether polling is active. Default true. */
  enabled?: boolean;
}

export interface UseArtifactsResult {
  /** Most recent agreement_map artifact, or null. */
  agreementMap: Artifact | null;
  /** Most recent conflict_map artifact, or null. */
  conflictMap: Artifact | null;
  /** Most recent neutral_memo artifact, or null. */
  neutralMemo: Artifact | null;
  /** Whether we have successfully fetched at least once. */
  isLoaded: boolean;
  /** Last fetch error, if any. */
  error: Error | null;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Pick the most recent artifact from an array (by created_at). */
function latest(artifacts: Artifact[]): Artifact | null {
  if (artifacts.length === 0) return null;
  return artifacts.reduce((a, b) => (a.created_at > b.created_at ? a : b));
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useArtifacts(
  conversationId: string | null,
  options?: UseArtifactsOptions,
): UseArtifactsResult {
  const { pollIntervalMs = 5000, enabled = true } = options ?? {};

  const [agreementMap, setAgreementMap] = useState<Artifact | null>(null);
  const [conflictMap, setConflictMap] = useState<Artifact | null>(null);
  const [neutralMemo, setNeutralMemo] = useState<Artifact | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const mountedRef = useRef(true);

  // Reset when conversationId changes.
  useEffect(() => {
    setAgreementMap(null);
    setConflictMap(null);
    setNeutralMemo(null);
    setIsLoaded(false);
    setError(null);
  }, [conversationId]);

  const poll = useCallback(async () => {
    if (!conversationId) return;

    try {
      const [agreements, conflicts, memos] = await Promise.all([
        fetchArtifacts(conversationId, "agreement_map"),
        fetchArtifacts(conversationId, "conflict_map"),
        fetchArtifacts(conversationId, "neutral_memo"),
      ]);

      if (!mountedRef.current) return;

      setAgreementMap(latest(agreements));
      setConflictMap(latest(conflicts));
      setNeutralMemo(latest(memos));
      setIsLoaded(true);
      setError(null);
    } catch (err) {
      if (!mountedRef.current) return;
      setError(err instanceof Error ? err : new Error(String(err)));
    }
  }, [conversationId]);

  useEffect(() => {
    mountedRef.current = true;

    if (!conversationId || !enabled) {
      return;
    }

    // Fetch immediately, then poll.
    void poll();

    const intervalId = setInterval(() => {
      void poll();
    }, pollIntervalMs);

    return () => {
      mountedRef.current = false;
      clearInterval(intervalId);
    };
  }, [conversationId, enabled, pollIntervalMs, poll]);

  return { agreementMap, conflictMap, neutralMemo, isLoaded, error };
}
