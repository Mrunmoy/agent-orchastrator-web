import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ChatMessage } from "./ChatMessage";
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

describe("ChatMessage", () => {
  it("shows agent name", () => {
    render(<ChatMessage message={makeMessage()} />);
    expect(screen.getByText("Claude")).toBeInTheDocument();
  });

  it("shows message text", () => {
    render(<ChatMessage message={makeMessage({ text: "Test message" })} />);
    expect(screen.getByText("Test message")).toBeInTheDocument();
  });

  it("shows avatar with first letter", () => {
    render(<ChatMessage message={makeMessage({ agentName: "Omega" })} />);
    const avatar = screen.getByTestId("chat-avatar");
    expect(avatar).toHaveTextContent("O");
  });

  it("user message has user class", () => {
    render(<ChatMessage message={makeMessage({ isUser: true })} />);
    const el = screen.getByTestId("chat-message");
    expect(el.className).toContain("chat-message--user");
  });

  it("agent message has agent class", () => {
    render(<ChatMessage message={makeMessage({ isUser: false })} />);
    const el = screen.getByTestId("chat-message");
    expect(el.className).toContain("chat-message--agent");
  });

  it("shows thinking indicator when isThinking is true", () => {
    render(<ChatMessage message={makeMessage({ isThinking: true })} />);
    expect(screen.getByTestId("thinking-indicator")).toBeInTheDocument();
  });

  it("hides thinking indicator when isThinking is false", () => {
    render(<ChatMessage message={makeMessage({ isThinking: false })} />);
    expect(screen.queryByTestId("thinking-indicator")).not.toBeInTheDocument();
  });
});
