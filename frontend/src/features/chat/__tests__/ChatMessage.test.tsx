import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ChatMessage } from "../ChatMessage";
import type { ChatMessageData } from "../types";
import { agentHue } from "../agentColor";

function makeMessage(overrides: Partial<ChatMessageData> = {}): ChatMessageData {
  return {
    id: "msg-1",
    agentName: "Claude",
    agentId: "agent-claude-1",
    text: "Hello, world!",
    timestamp: "2026-03-07T12:00:00Z",
    isUser: false,
    ...overrides,
  };
}

describe("ChatMessage — T-301", () => {
  // TT-301-01: Agent message with avatar showing first letter and hash-based color
  describe("TT-301-01: agent avatar with hash-based color", () => {
    it("renders avatar with first letter of agent name", () => {
      render(<ChatMessage message={makeMessage({ agentName: "Omega" })} />);
      const avatar = screen.getByTestId("chat-avatar");
      expect(avatar).toHaveTextContent("O");
    });

    it("applies hash-based HSL background color from agent ID", () => {
      render(
        <ChatMessage
          message={makeMessage({ agentId: "agent-abc", agentName: "Alpha" })}
        />,
      );
      const avatar = screen.getByTestId("chat-avatar");
      // jsdom normalizes HSL to RGB, so just verify inline style is set
      expect(avatar.style.backgroundColor).toBeTruthy();
      // Verify it's not the default (i.e., it was set by our component)
      expect(avatar.getAttribute("style")).toContain("background-color");
    });

    it("produces deterministic hue for same agent ID", () => {
      const h1 = agentHue("agent-xyz");
      const h2 = agentHue("agent-xyz");
      expect(h1).toBe(h2);
    });

    it("produces different hues for different agent IDs", () => {
      const h1 = agentHue("agent-aaa");
      const h2 = agentHue("agent-bbb");
      expect(h1).not.toBe(h2);
    });
  });

  // TT-301-02: Markdown rendering (code block, bold, link)
  describe("TT-301-02: markdown rendering", () => {
    it("renders bold text as <strong>", () => {
      render(
        <ChatMessage message={makeMessage({ text: "This is **bold** text" })} />,
      );
      const strong = screen.getByText("bold");
      expect(strong.tagName).toBe("STRONG");
    });

    it("renders inline code as <code>", () => {
      render(
        <ChatMessage
          message={makeMessage({ text: "Run `npm install` first" })}
        />,
      );
      const code = screen.getByText("npm install");
      expect(code.tagName).toBe("CODE");
    });

    it("renders links as <a>", () => {
      render(
        <ChatMessage
          message={makeMessage({
            text: "Visit [example](https://example.com)",
          })}
        />,
      );
      const link = screen.getByText("example");
      expect(link.tagName).toBe("A");
      expect(link).toHaveAttribute("href", "https://example.com");
    });
  });

  // TT-301-03: phase_change as styled divider
  describe("TT-301-03: phase_change divider", () => {
    it("renders phase_change as a divider with phase label", () => {
      render(
        <ChatMessage
          message={makeMessage({
            type: "phase_change",
            phaseLabel: "Design Debate",
            text: "",
          })}
        />,
      );
      expect(screen.getByTestId("phase-divider")).toBeInTheDocument();
      expect(screen.getByText("Design Debate")).toBeInTheDocument();
    });

    it("does not render avatar or bubble for phase_change", () => {
      render(
        <ChatMessage
          message={makeMessage({
            type: "phase_change",
            phaseLabel: "TDD Planning",
            text: "",
          })}
        />,
      );
      expect(screen.queryByTestId("chat-avatar")).not.toBeInTheDocument();
      expect(screen.queryByTestId("chat-bubble")).not.toBeInTheDocument();
    });
  });

  // TT-301-04: steer message with highlight border and 'You' label
  describe("TT-301-04: steer message", () => {
    it("renders steer message with highlight border class", () => {
      render(
        <ChatMessage
          message={makeMessage({
            type: "steer",
            isUser: true,
            agentName: "User",
            text: "Focus on performance",
          })}
        />,
      );
      const el = screen.getByTestId("chat-message");
      expect(el.className).toContain("chat-message--steer");
    });

    it("shows 'You' as sender label for steer messages", () => {
      render(
        <ChatMessage
          message={makeMessage({
            type: "steer",
            isUser: true,
            agentName: "User",
            text: "Focus on tests",
          })}
        />,
      );
      expect(screen.getByText("You")).toBeInTheDocument();
    });
  });

  // Additional variant tests
  describe("debate_turn variant", () => {
    it("renders round badge with round info", () => {
      render(
        <ChatMessage
          message={makeMessage({
            type: "debate_turn",
            round: 3,
            totalRounds: 20,
            text: "I disagree because...",
          })}
        />,
      );
      expect(screen.getByTestId("round-badge")).toHaveTextContent("Round 3/20");
    });
  });

  describe("system_notice variant", () => {
    it("renders system notice with muted banner style", () => {
      render(
        <ChatMessage
          message={makeMessage({
            type: "system_notice",
            agentName: "System",
            text: "Gate approved",
          })}
        />,
      );
      const el = screen.getByTestId("chat-message");
      expect(el.className).toContain("chat-message--system");
    });
  });

  describe("role badge", () => {
    it("shows role badge next to agent name when agentRole is set", () => {
      render(
        <ChatMessage
          message={makeMessage({ agentRole: "coordinator" })}
        />,
      );
      expect(screen.getByTestId("role-badge")).toHaveTextContent("coordinator");
    });

    it("does not show role badge when agentRole is not set", () => {
      render(<ChatMessage message={makeMessage({ agentRole: undefined })} />);
      expect(screen.queryByTestId("role-badge")).not.toBeInTheDocument();
    });
  });
});
