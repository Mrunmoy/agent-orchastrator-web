import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { Composer } from "./Composer";

const agents = [
  { id: "agent-1", display_name: "Claude" },
  { id: "agent-2", display_name: "Codex" },
  { id: "agent-3", display_name: "Bob" },
];

describe("Composer", () => {
  it("renders input and send button without agent selector", () => {
    render(<Composer agents={agents} onSend={vi.fn()} />);
    expect(screen.getByTestId("composer")).toBeInTheDocument();
    expect(screen.getByTestId("composer-input")).toBeInTheDocument();
    expect(screen.queryByTestId("agent-selector")).not.toBeInTheDocument();
    expect(screen.getByTestId("send-button")).toBeInTheDocument();
  });

  it("sends message without targetAgentId", () => {
    const onSend = vi.fn();
    render(<Composer agents={agents} onSend={onSend} />);
    const input = screen.getByTestId("composer-input");
    fireEvent.change(input, { target: { value: "Hello world" } });
    fireEvent.click(screen.getByTestId("send-button"));
    expect(onSend).toHaveBeenCalledWith("Hello world", undefined);
  });

  it("clears input after send", () => {
    const onSend = vi.fn();
    render(<Composer agents={agents} onSend={onSend} />);
    const input = screen.getByTestId("composer-input") as HTMLTextAreaElement;
    fireEvent.change(input, { target: { value: "Will be cleared" } });
    fireEvent.click(screen.getByTestId("send-button"));
    expect(input.value).toBe("");
  });

  it("does not send empty message", () => {
    const onSend = vi.fn();
    render(<Composer agents={agents} onSend={onSend} />);
    fireEvent.click(screen.getByTestId("send-button"));
    expect(onSend).not.toHaveBeenCalled();
  });

  it("disables interaction when disabled prop is true", () => {
    const onSend = vi.fn();
    render(<Composer agents={agents} onSend={onSend} disabled={true} />);
    const input = screen.getByTestId("composer-input") as HTMLTextAreaElement;
    const button = screen.getByTestId("send-button") as HTMLButtonElement;
    expect(input.disabled).toBe(true);
    expect(button.disabled).toBe(true);
  });

  it("sends on Enter key press", () => {
    const onSend = vi.fn();
    render(<Composer agents={agents} onSend={onSend} />);
    const input = screen.getByTestId("composer-input");
    fireEvent.change(input, { target: { value: "Enter send" } });
    fireEvent.keyDown(input, { key: "Enter", shiftKey: false });
    expect(onSend).toHaveBeenCalledWith("Enter send", undefined);
  });

  it("does not send on Shift+Enter (allows newline)", () => {
    const onSend = vi.fn();
    render(<Composer agents={agents} onSend={onSend} />);
    const input = screen.getByTestId("composer-input");
    fireEvent.change(input, { target: { value: "Newline" } });
    fireEvent.keyDown(input, { key: "Enter", shiftKey: true });
    expect(onSend).not.toHaveBeenCalled();
  });

  // TT-303-01: Typing '@' in textarea shows agent suggestion dropdown
  describe("@mention autocomplete", () => {
    it("TT-303-01: typing '@' shows agent suggestion dropdown", () => {
      render(<Composer agents={agents} onSend={vi.fn()} />);
      const input = screen.getByTestId("composer-input") as HTMLTextAreaElement;

      // Type '@' to trigger autocomplete
      fireEvent.change(input, { target: { value: "@" } });
      // Simulate cursor position at end
      Object.defineProperty(input, "selectionStart", { value: 1, writable: true });
      fireEvent.change(input, { target: { value: "@" } });

      const dropdown = screen.getByTestId("mention-dropdown");
      expect(dropdown).toBeInTheDocument();
      // All agents should be shown
      expect(screen.getByText("Claude")).toBeInTheDocument();
      expect(screen.getByText("Codex")).toBeInTheDocument();
      expect(screen.getByText("Bob")).toBeInTheDocument();
    });

    // TT-303-02: Filtering works — typing '@Bo' filters to matching agents
    it("TT-303-02: typing '@Bo' filters to matching agents", () => {
      render(<Composer agents={agents} onSend={vi.fn()} />);
      const input = screen.getByTestId("composer-input") as HTMLTextAreaElement;

      fireEvent.change(input, { target: { value: "@Bo" } });
      Object.defineProperty(input, "selectionStart", { value: 3, writable: true });
      fireEvent.change(input, { target: { value: "@Bo" } });

      const dropdown = screen.getByTestId("mention-dropdown");
      expect(dropdown).toBeInTheDocument();
      expect(screen.getByText("Bob")).toBeInTheDocument();
      expect(screen.queryByText("Claude")).not.toBeInTheDocument();
      expect(screen.queryByText("Codex")).not.toBeInTheDocument();
    });

    // TT-303-03: Selecting an agent from dropdown inserts @AgentName into text
    it("TT-303-03: selecting agent from dropdown inserts @AgentName", () => {
      render(<Composer agents={agents} onSend={vi.fn()} />);
      const input = screen.getByTestId("composer-input") as HTMLTextAreaElement;

      fireEvent.change(input, { target: { value: "@" } });
      Object.defineProperty(input, "selectionStart", { value: 1, writable: true });
      fireEvent.change(input, { target: { value: "@" } });

      // Click on an agent in the dropdown (mouseDown because we use onMouseDown to prevent blur)
      const option = screen.getByText("Claude");
      fireEvent.mouseDown(option);

      expect(input.value).toBe("@Claude ");
      // Dropdown should be closed
      expect(screen.queryByTestId("mention-dropdown")).not.toBeInTheDocument();
    });

    // TT-303-04: Enter sends message, Shift+Enter inserts newline (already tested above, but verify with mention)
    it("TT-303-04: Enter sends message with @mention, Shift+Enter newline", () => {
      const onSend = vi.fn();
      render(<Composer agents={agents} onSend={onSend} />);
      const input = screen.getByTestId("composer-input") as HTMLTextAreaElement;

      // Set message with a mention already inserted
      fireEvent.change(input, { target: { value: "@Claude hello" } });
      // No active mention query (cursor not after @)
      Object.defineProperty(input, "selectionStart", {
        value: 13,
        writable: true,
      });

      // Shift+Enter should NOT send
      fireEvent.keyDown(input, { key: "Enter", shiftKey: true });
      expect(onSend).not.toHaveBeenCalled();

      // Enter should send
      fireEvent.keyDown(input, { key: "Enter", shiftKey: false });
      expect(onSend).toHaveBeenCalledWith("@Claude hello", "agent-1");
    });

    // TT-303-05: Send payload includes target_agent_id when @mention is present
    it("TT-303-05: send payload includes target_agent_id for @mentioned agent", () => {
      const onSend = vi.fn();
      render(<Composer agents={agents} onSend={onSend} />);
      const input = screen.getByTestId("composer-input") as HTMLTextAreaElement;

      // Simulate a message that has a mention
      fireEvent.change(input, { target: { value: "@Bob can you review?" } });
      fireEvent.keyDown(input, { key: "Enter", shiftKey: false });

      expect(onSend).toHaveBeenCalledWith("@Bob can you review?", "agent-3");
    });

    it("navigates dropdown with arrow keys and selects with Enter", () => {
      render(<Composer agents={agents} onSend={vi.fn()} />);
      const input = screen.getByTestId("composer-input") as HTMLTextAreaElement;

      fireEvent.change(input, { target: { value: "@" } });
      Object.defineProperty(input, "selectionStart", { value: 1, writable: true });
      fireEvent.change(input, { target: { value: "@" } });

      // Dropdown should be open
      expect(screen.getByTestId("mention-dropdown")).toBeInTheDocument();

      // ArrowDown to highlight second item
      fireEvent.keyDown(input, { key: "ArrowDown" });
      // ArrowDown again to highlight third item
      fireEvent.keyDown(input, { key: "ArrowDown" });
      // ArrowUp to go back to second item
      fireEvent.keyDown(input, { key: "ArrowUp" });

      // Enter to select
      fireEvent.keyDown(input, { key: "Enter" });

      // Second agent (Codex) should be selected
      expect(input.value).toBe("@Codex ");
      expect(screen.queryByTestId("mention-dropdown")).not.toBeInTheDocument();
    });

    it("closes dropdown on Escape", () => {
      render(<Composer agents={agents} onSend={vi.fn()} />);
      const input = screen.getByTestId("composer-input") as HTMLTextAreaElement;

      fireEvent.change(input, { target: { value: "@" } });
      Object.defineProperty(input, "selectionStart", { value: 1, writable: true });
      fireEvent.change(input, { target: { value: "@" } });

      expect(screen.getByTestId("mention-dropdown")).toBeInTheDocument();

      fireEvent.keyDown(input, { key: "Escape" });
      expect(screen.queryByTestId("mention-dropdown")).not.toBeInTheDocument();
    });

    it("does not show dropdown when no agents match", () => {
      render(<Composer agents={agents} onSend={vi.fn()} />);
      const input = screen.getByTestId("composer-input") as HTMLTextAreaElement;

      fireEvent.change(input, { target: { value: "@xyz" } });
      Object.defineProperty(input, "selectionStart", { value: 4, writable: true });
      fireEvent.change(input, { target: { value: "@xyz" } });

      expect(screen.queryByTestId("mention-dropdown")).not.toBeInTheDocument();
    });
  });
});
