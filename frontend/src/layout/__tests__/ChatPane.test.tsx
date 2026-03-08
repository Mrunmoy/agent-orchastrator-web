import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { ChatPane } from "../ChatPane";
import type { ChatMessageData } from "../../features/chat/types";

function makeMessage(overrides: Partial<ChatMessageData> = {}): ChatMessageData {
  return {
    id: "msg-1",
    agentName: "Claude",
    text: "Hello, world!",
    timestamp: "2026-03-07T12:00:00Z",
    isUser: false,
    ...overrides,
  };
}

describe("ChatPane", () => {
  it("renders the chat pane container", () => {
    render(<ChatPane />);
    expect(screen.getByTestId("chat-pane")).toBeInTheDocument();
  });

  it("shows conversation title when provided", () => {
    render(<ChatPane activeConversationTitle="My Debate" />);
    expect(screen.getByText("My Debate")).toBeInTheDocument();
  });

  it("shows fallback text when no conversation title", () => {
    render(<ChatPane />);
    expect(screen.getByText("No active conversation")).toBeInTheDocument();
  });

  it("renders ChatTimeline with empty state when no messages", () => {
    render(<ChatPane />);
    expect(screen.getByTestId("chat-timeline")).toBeInTheDocument();
    expect(
      screen.getByText("No messages yet. Start a conversation!"),
    ).toBeInTheDocument();
  });

  it("renders messages through ChatTimeline", () => {
    const messages = [
      makeMessage({ id: "m1", text: "First message", agentName: "Alice" }),
      makeMessage({ id: "m2", text: "Second message", agentName: "Bob" }),
    ];
    render(<ChatPane messages={messages} />);
    expect(screen.getByText("First message")).toBeInTheDocument();
    expect(screen.getByText("Second message")).toBeInTheDocument();
  });

  it("renders agent avatars via ChatMessage component", () => {
    const messages = [
      makeMessage({ id: "m1", agentName: "Claude", agentId: "agent-1" }),
    ];
    render(<ChatPane messages={messages} />);
    expect(screen.getByTestId("chat-avatar")).toBeInTheDocument();
    expect(screen.getByTestId("chat-bubble")).toBeInTheDocument();
  });

  it("renders the composer input and send button", () => {
    render(<ChatPane />);
    expect(screen.getByTestId("composer")).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText("Type a message..."),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Send To Group" }),
    ).toBeInTheDocument();
  });

  it("calls onSend with trimmed text when send button clicked", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<ChatPane onSend={onSend} />);

    const input = screen.getByPlaceholderText("Type a message...");
    await user.type(input, "  hello world  ");
    await user.click(screen.getByRole("button", { name: "Send To Group" }));

    expect(onSend).toHaveBeenCalledWith("hello world");
  });

  it("calls onSend on Enter key press", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<ChatPane onSend={onSend} />);

    const input = screen.getByPlaceholderText("Type a message...");
    await user.type(input, "test message{Enter}");

    expect(onSend).toHaveBeenCalledWith("test message");
  });

  it("clears input after sending", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<ChatPane onSend={onSend} />);

    const input = screen.getByPlaceholderText("Type a message...");
    await user.type(input, "hello{Enter}");

    expect(input).toHaveValue("");
  });

  it("does not call onSend for empty/whitespace-only input", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<ChatPane onSend={onSend} />);

    const input = screen.getByPlaceholderText("Type a message...");
    await user.type(input, "   {Enter}");

    expect(onSend).not.toHaveBeenCalled();
  });

  it("renders different message types correctly", () => {
    const messages = [
      makeMessage({
        id: "m1",
        type: "steer",
        agentName: "You",
        text: "Focus on tests",
        isUser: true,
      }),
      makeMessage({
        id: "m2",
        type: "debate_turn",
        agentName: "Claude",
        text: "I agree",
        round: 1,
        totalRounds: 3,
      }),
      makeMessage({
        id: "m3",
        type: "phase_change",
        agentName: "System",
        phaseLabel: "Implementation Phase",
        text: "",
      }),
      makeMessage({
        id: "m4",
        type: "system_notice",
        agentName: "System",
        text: "Batch started",
      }),
    ];
    render(<ChatPane messages={messages} />);
    expect(screen.getByText("Focus on tests")).toBeInTheDocument();
    expect(screen.getByText("I agree")).toBeInTheDocument();
    expect(screen.getByText("Implementation Phase")).toBeInTheDocument();
    expect(screen.getByText("Batch started")).toBeInTheDocument();
  });

  it("renders debate turn with round badge", () => {
    const messages = [
      makeMessage({
        id: "m1",
        type: "debate_turn",
        agentName: "Claude",
        text: "My argument",
        round: 2,
        totalRounds: 5,
      }),
    ];
    render(<ChatPane messages={messages} />);
    expect(screen.getByTestId("round-badge")).toHaveTextContent("Round 2/5");
  });
});
