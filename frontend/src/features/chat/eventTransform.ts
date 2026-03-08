/**
 * eventTransform — converts backend EventData into ChatMessageData for the UI.
 */

import type { AgentData } from "../agents/types";
import type { ChatMessageData, MessageType } from "./types";
import type { EventData } from "../../hooks/useEventStream";

/** Map backend event_type strings to ChatMessageData type values. */
const EVENT_TYPE_MAP: Record<string, MessageType> = {
  steer: "steer",
  debate_turn: "debate_turn",
  phase_change: "phase_change",
  system_notice: "system_notice",
  chat_message: "chat_message",
};

/** Source types that represent user-originated messages. */
const USER_SOURCE_TYPES = new Set(["user", "steering"]);

/**
 * Convert a single backend EventData into a ChatMessageData suitable for
 * the ChatPane timeline.
 */
export function eventToChatMessage(event: EventData, agents: AgentData[]): ChatMessageData {
  const agent = event.sourceId ? agents.find((a) => a.id === event.sourceId) : undefined;

  const isUser = USER_SOURCE_TYPES.has(event.sourceType);
  const type: MessageType = EVENT_TYPE_MAP[event.eventType] ?? "chat_message";

  const agentName = isUser
    ? "You"
    : (agent?.display_name ?? event.sourceId ?? event.sourceType ?? "System");

  const meta = event.metadata;

  return {
    id: event.id,
    agentName,
    agentId: event.sourceId,
    agentRole: agent?.role,
    text: event.text,
    timestamp: event.timestamp,
    isUser,
    isThinking: meta.isThinking === true,
    type,
    round: typeof meta.round === "number" ? meta.round : undefined,
    totalRounds: typeof meta.totalRounds === "number" ? meta.totalRounds : undefined,
    phaseLabel: typeof meta.phaseLabel === "string" ? meta.phaseLabel : undefined,
  };
}

/**
 * Convert an array of EventData into ChatMessageData[], preserving order.
 */
export function eventsToChatMessages(events: EventData[], agents: AgentData[]): ChatMessageData[] {
  return events.map((event) => eventToChatMessage(event, agents));
}

/**
 * Merge event-sourced messages with local optimistic messages.
 *
 * Local messages whose id appears in the event-sourced list are dropped
 * (the server version wins). Remaining local messages are appended at
 * the end, sorted by timestamp.
 */
export function mergeWithLocal(
  eventMessages: ChatMessageData[],
  localMessages: ChatMessageData[],
): ChatMessageData[] {
  if (localMessages.length === 0) return eventMessages;
  if (eventMessages.length === 0) return localMessages;

  const eventIds = new Set(eventMessages.map((m) => m.id));
  const surviving = localMessages.filter((m) => !eventIds.has(m.id));

  if (surviving.length === 0) return eventMessages;

  // Merge and sort by timestamp.
  const merged = [...eventMessages, ...surviving];
  merged.sort((a, b) => a.timestamp.localeCompare(b.timestamp));
  return merged;
}
