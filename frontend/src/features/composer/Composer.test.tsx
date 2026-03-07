import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { Composer } from "./Composer";

const agents = [
  { id: "agent-1", display_name: "Claude" },
  { id: "agent-2", display_name: "Codex" },
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
    expect(onSend).toHaveBeenCalledWith("Hello world");
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
    expect(onSend).toHaveBeenCalledWith("Enter send");
  });

  it("does not send on Shift+Enter (allows newline)", () => {
    const onSend = vi.fn();
    render(<Composer agents={agents} onSend={onSend} />);
    const input = screen.getByTestId("composer-input");
    fireEvent.change(input, { target: { value: "Newline" } });
    fireEvent.keyDown(input, { key: "Enter", shiftKey: true });
    expect(onSend).not.toHaveBeenCalled();
  });
});
