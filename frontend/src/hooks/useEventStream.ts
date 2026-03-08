/**
 * useEventStream — polls the backend for live message/event updates.
 *
 * Uses the `GET /api/events?conversation_id=X&since=Y` endpoint for
 * incremental event fetching, tracking the last seen event_id so each
 * poll only returns new events.
 */

import { useCallback, useEffect, useRef, useState } from "react";

import { type BackendEvent, fetchEvents, fetchLatestEvents } from "../api/client";

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export interface EventData {
  id: string;
  conversationId: string;
  sourceType: string;
  sourceId?: string;
  text: string;
  eventType: string;
  timestamp: string;
  metadata: Record<string, unknown>;
}

export interface UseEventStreamOptions {
  /** Polling interval in milliseconds. Default 3000. */
  pollIntervalMs?: number;
  /** Whether polling is active. Default true. */
  enabled?: boolean;
  /** Number of initial events to fetch on first load. Default 50. */
  initialCount?: number;
}

export interface UseEventStreamResult {
  events: EventData[];
  isConnected: boolean;
  error: Error | null;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function parseMetadata(raw?: string): Record<string, unknown> {
  if (!raw) return {};
  try {
    return JSON.parse(raw) as Record<string, unknown>;
  } catch {
    return {};
  }
}

function toEventData(be: BackendEvent): EventData {
  return {
    id: be.event_id,
    conversationId: be.conversation_id,
    sourceType: be.source_type,
    sourceId: be.source_id,
    text: be.text,
    eventType: be.event_type,
    timestamp: be.timestamp ?? be.created_at ?? new Date().toISOString(),
    metadata: parseMetadata(be.metadata_json),
  };
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useEventStream(
  conversationId: string | null,
  options?: UseEventStreamOptions,
): UseEventStreamResult {
  const { pollIntervalMs = 3000, enabled = true, initialCount = 50 } = options ?? {};

  const [events, setEvents] = useState<EventData[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Track last event id across renders without triggering re-renders.
  const lastEventIdRef = useRef<string | null>(null);
  // Track whether the initial fetch has completed.
  const initialLoadDoneRef = useRef(false);

  // Reset state when conversationId changes.
  useEffect(() => {
    setEvents([]);
    setError(null);
    setIsConnected(false);
    lastEventIdRef.current = null;
    initialLoadDoneRef.current = false;
  }, [conversationId]);

  const poll = useCallback(async () => {
    if (!conversationId) return;

    try {
      let backendEvents: BackendEvent[];

      if (!initialLoadDoneRef.current) {
        // First poll: fetch latest N events to bootstrap the view.
        backendEvents = await fetchLatestEvents(conversationId, initialCount);
        initialLoadDoneRef.current = true;
      } else if (lastEventIdRef.current) {
        // Subsequent polls: fetch only events after the last seen id.
        backendEvents = await fetchEvents(conversationId, lastEventIdRef.current);
      } else {
        // No last event id but initial load done (empty conversation) — fetch all.
        backendEvents = await fetchEvents(conversationId);
      }

      if (backendEvents.length > 0) {
        const newEvents = backendEvents.map(toEventData);
        const lastEvent = newEvents[newEvents.length - 1];
        if (lastEvent) {
          lastEventIdRef.current = lastEvent.id;
        }

        setEvents((prev) => {
          if (!initialLoadDoneRef.current || prev.length === 0) {
            // Replace on initial load (already set above but guard).
            return newEvents;
          }
          // Deduplicate: only append events we haven't seen.
          const existingIds = new Set(prev.map((e) => e.id));
          const truly = newEvents.filter((e) => !existingIds.has(e.id));
          return truly.length > 0 ? [...prev, ...truly] : prev;
        });
      }

      setIsConnected(true);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
      setIsConnected(false);
    }
  }, [conversationId, initialCount]);

  useEffect(() => {
    if (!conversationId || !enabled) {
      setIsConnected(false);
      return;
    }

    // Kick off immediately, then set interval.
    void poll();

    const intervalId = setInterval(() => {
      void poll();
    }, pollIntervalMs);

    return () => {
      clearInterval(intervalId);
    };
  }, [conversationId, enabled, pollIntervalMs, poll]);

  return { events, isConnected, error };
}
