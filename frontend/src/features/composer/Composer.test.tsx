import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { Composer } from "./Composer";

const agents = [
  { id: "agent-1", display_name: "Claude" },
  { id: "agent-2", display_name: "Codex" },
];

describe("Composer", () => {
  it("renders input, agent selector, and send button", () => {
    render(<Composer agents={agents} onSend={vi.fn()} />);
    expect(screen.getByTestId("composer")).toBeInTheDocument();
    expect(screen.getByTestId("composer-input")).toBeInTheDocument();
    expect(screen.getByTestId("agent-selector")).toBeInTheDocument();
    expect(screen.getByTestId("send-button")).toBeInTheDocument();
  });

  it("renders agent options including All agents default", () => {
    render(<Composer agents={agents} onSend={vi.fn()} />);
    const selector = screen.getByTestId("agent-selector") as HTMLSelectElement;
    const options = selector.querySelectorAll("option");
    expect(options).toHaveLength(3);
    expect(options[0]?.textContent).toBe("All agents");
    expect(options[1]?.textContent).toBe("Claude");
    expect(options[2]?.textContent).toBe("Codex");
  });

  it("sends message with null agent when All agents selected", () => {
    const onSend = vi.fn();
    render(<Composer agents={agents} onSend={onSend} />);
    const input = screen.getByTestId("composer-input");
    fireEvent.change(input, { target: { value: "Hello world" } });
    fireEvent.click(screen.getByTestId("send-button"));
    expect(onSend).toHaveBeenCalledWith("Hello world", null);
  });

  it("sends message with selected agent id", () => {
    const onSend = vi.fn();
    render(<Composer agents={agents} onSend={onSend} />);
    const input = screen.getByTestId("composer-input");
    const selector = screen.getByTestId("agent-selector");
    fireEvent.change(selector, { target: { value: "agent-1" } });
    fireEvent.change(input, { target: { value: "Target message" } });
    fireEvent.click(screen.getByTestId("send-button"));
    expect(onSend).toHaveBeenCalledWith("Target message", "agent-1");
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
    const selector = screen.getByTestId("agent-selector") as HTMLSelectElement;
    const button = screen.getByTestId("send-button") as HTMLButtonElement;
    expect(input.disabled).toBe(true);
    expect(selector.disabled).toBe(true);
    expect(button.disabled).toBe(true);
  });

  it("sends on Enter key press", () => {
    const onSend = vi.fn();
    render(<Composer agents={agents} onSend={onSend} />);
    const input = screen.getByTestId("composer-input");
    fireEvent.change(input, { target: { value: "Enter send" } });
    fireEvent.keyDown(input, { key: "Enter", shiftKey: false });
    expect(onSend).toHaveBeenCalledWith("Enter send", null);
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
