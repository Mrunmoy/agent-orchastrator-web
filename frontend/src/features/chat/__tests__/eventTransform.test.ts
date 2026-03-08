import { describe, expect, it } from "vitest";
import type { AgentData } from "../../agents/types";
import type { EventData } from "../../../hooks/useEventStream";
import type { ChatMessageData } from "../types";
import { eventToChatMessage, eventsToChatMessages, mergeWithLocal } from "../eventTransform";

const agents: AgentData[] = [
  {
    id: "agent-1",
    display_name: "Claude Worker",
    provider: "claude",
    model: "claude-opus-4-5",
    role: "worker",
    status: "idle",
    sort_order: 0,
  },
  {
    id: "agent-2",
    display_name: "Codex Reviewer",
    provider: "codex",
    model: "codex-mini-latest",
    role: "coordinator",
    status: "idle",
    sort_order: 1,
  },
];

function makeEvent(overrides: Partial<EventData> = {}): EventData {
  return {
    id: "evt-1",
    conversationId: "conv-1",
    sourceType: "agent",
    sourceId: "agent-1",
    text: "Hello world",
    eventType: "debate_turn",
    timestamp: "2026-03-08T10:00:00Z",
    metadata: {},
    ...overrides,
  };
}

describe("eventToChatMessage", () => {
  it("maps a debate_turn event to a ChatMessageData with agent lookup", () => {
    const result = eventToChatMessage(makeEvent(), agents);

    expect(result).toEqual({
      id: "evt-1",
      agentName: "Claude Worker",
      agentId: "agent-1",
      agentRole: "worker",
      text: "Hello world",
      timestamp: "2026-03-08T10:00:00Z",
      isUser: false,
      isThinking: false,
      type: "debate_turn",
      round: undefined,
      totalRounds: undefined,
      phaseLabel: undefined,
    });
  });

  it("marks user source types as isUser=true", () => {
    const event = makeEvent({ sourceType: "user", eventType: "steer" });
    const result = eventToChatMessage(event, agents);

    expect(result.isUser).toBe(true);
    expect(result.agentName).toBe("You");
    expect(result.type).toBe("steer");
  });

  it("marks steering source type as isUser=true", () => {
    const event = makeEvent({ sourceType: "steering", eventType: "steer" });
    const result = eventToChatMessage(event, agents);

    expect(result.isUser).toBe(true);
  });

  it("falls back to sourceId when agent is not found", () => {
    const event = makeEvent({ sourceId: "unknown-agent" });
    const result = eventToChatMessage(event, agents);

    expect(result.agentName).toBe("unknown-agent");
    expect(result.agentId).toBe("unknown-agent");
    expect(result.agentRole).toBeUndefined();
  });

  it("falls back to sourceType when sourceId is missing", () => {
    const event = makeEvent({ sourceId: undefined, sourceType: "system" });
    const result = eventToChatMessage(event, agents);

    expect(result.agentName).toBe("system");
  });

  it("defaults event type to chat_message for unknown types", () => {
    const event = makeEvent({ eventType: "unknown_thing" });
    const result = eventToChatMessage(event, agents);

    expect(result.type).toBe("chat_message");
  });

  it("maps phase_change event type correctly", () => {
    const event = makeEvent({
      eventType: "phase_change",
      metadata: { phaseLabel: "TDD Planning" },
    });
    const result = eventToChatMessage(event, agents);

    expect(result.type).toBe("phase_change");
    expect(result.phaseLabel).toBe("TDD Planning");
  });

  it("extracts round/totalRounds from metadata", () => {
    const event = makeEvent({
      metadata: { round: 3, totalRounds: 10 },
    });
    const result = eventToChatMessage(event, agents);

    expect(result.round).toBe(3);
    expect(result.totalRounds).toBe(10);
  });

  it("extracts isThinking from metadata", () => {
    const event = makeEvent({ metadata: { isThinking: true } });
    const result = eventToChatMessage(event, agents);

    expect(result.isThinking).toBe(true);
  });

  it("maps system_notice event type", () => {
    const event = makeEvent({ eventType: "system_notice", sourceType: "system", sourceId: undefined });
    const result = eventToChatMessage(event, agents);

    expect(result.type).toBe("system_notice");
    expect(result.isUser).toBe(false);
    expect(result.agentName).toBe("system");
  });
});

describe("eventsToChatMessages", () => {
  it("converts multiple events preserving order", () => {
    const events = [
      makeEvent({ id: "e1", text: "first" }),
      makeEvent({ id: "e2", text: "second", sourceId: "agent-2" }),
    ];
    const result = eventsToChatMessages(events, agents);

    expect(result).toHaveLength(2);
    expect(result[0].id).toBe("e1");
    expect(result[0].text).toBe("first");
    expect(result[1].id).toBe("e2");
    expect(result[1].agentName).toBe("Codex Reviewer");
  });

  it("returns empty array for empty events", () => {
    expect(eventsToChatMessages([], agents)).toEqual([]);
  });
});

describe("mergeWithLocal", () => {
  const eventMessages: ChatMessageData[] = [
    {
      id: "evt-1",
      agentName: "Claude Worker",
      text: "server message",
      timestamp: "2026-03-08T10:00:00Z",
      isUser: false,
    },
    {
      id: "evt-2",
      agentName: "Codex Reviewer",
      text: "server message 2",
      timestamp: "2026-03-08T10:01:00Z",
      isUser: false,
    },
  ];

  it("returns event messages when no local messages", () => {
    expect(mergeWithLocal(eventMessages, [])).toEqual(eventMessages);
  });

  it("returns local messages when no event messages", () => {
    const local: ChatMessageData[] = [
      { id: "local-1", agentName: "You", text: "hi", timestamp: "2026-03-08T10:02:00Z", isUser: true },
    ];
    expect(mergeWithLocal([], local)).toEqual(local);
  });

  it("drops local messages that exist in event messages (server wins)", () => {
    const local: ChatMessageData[] = [
      { id: "evt-1", agentName: "You", text: "duplicate", timestamp: "2026-03-08T10:00:00Z", isUser: true },
    ];
    const result = mergeWithLocal(eventMessages, local);

    expect(result).toHaveLength(2);
    expect(result.find((m) => m.text === "duplicate")).toBeUndefined();
  });

  it("appends surviving local messages sorted by timestamp", () => {
    const local: ChatMessageData[] = [
      {
        id: "local-1",
        agentName: "You",
        text: "optimistic steer",
        timestamp: "2026-03-08T10:00:30Z",
        isUser: true,
        type: "steer",
      },
    ];
    const result = mergeWithLocal(eventMessages, local);

    expect(result).toHaveLength(3);
    // Should be sorted: evt-1 (10:00), local-1 (10:00:30), evt-2 (10:01)
    expect(result[0].id).toBe("evt-1");
    expect(result[1].id).toBe("local-1");
    expect(result[2].id).toBe("evt-2");
  });
});
