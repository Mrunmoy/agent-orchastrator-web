import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ChatTimeline } from "./ChatTimeline";
import type { ChatMessageData } from "./types";

function makeMessage(
  overrides: Partial<ChatMessageData> = {},
): ChatMessageData {
  return {
    id: "msg-1",
    agentName: "Claude",
    text: "Hello, world!",
    timestamp: "2026-03-07T12:00:00Z",
    isUser: false,
    ...overrides,
  };
}

describe("ChatTimeline", () => {
  it("renders empty state when no messages", () => {
    render(<ChatTimeline messages={[]} />);
    expect(
      screen.getByText("No messages yet. Start a conversation!"),
    ).toBeInTheDocument();
  });

  it("renders list of messages", () => {
    const messages = [
      makeMessage({ id: "m1", text: "First message" }),
      makeMessage({ id: "m2", text: "Second message" }),
    ];
    render(<ChatTimeline messages={messages} />);
    expect(screen.getByText("First message")).toBeInTheDocument();
    expect(screen.getByText("Second message")).toBeInTheDocument();
  });

  it("renders messages in order", () => {
    const messages = [
      makeMessage({ id: "m1", text: "Alpha" }),
      makeMessage({ id: "m2", text: "Beta" }),
      makeMessage({ id: "m3", text: "Gamma" }),
    ];
    render(<ChatTimeline messages={messages} />);
    const items = screen.getAllByTestId("chat-message");
    expect(items).toHaveLength(3);
    expect(items[0]).toHaveTextContent("Alpha");
    expect(items[1]).toHaveTextContent("Beta");
    expect(items[2]).toHaveTextContent("Gamma");
  });
});
