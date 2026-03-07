import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { SteeringPanel } from "./SteeringPanel";
import type { SteeringPanelProps } from "./types";

const defaultProps: SteeringPanelProps = {
  status: "running",
  steeringHistory: [],
  onSteer: vi.fn(),
};

describe("SteeringPanel", () => {
  it("renders the steering panel container", () => {
    render(<SteeringPanel {...defaultProps} />);
    expect(screen.getByTestId("steering-panel")).toBeInTheDocument();
  });

  it("renders a textarea for steering input", () => {
    render(<SteeringPanel {...defaultProps} />);
    const textarea = screen.getByTestId("steering-textarea");
    expect(textarea.tagName).toBe("TEXTAREA");
    expect(textarea).toHaveAttribute("placeholder", expect.stringContaining("steering"));
  });

  it("renders a submit button", () => {
    render(<SteeringPanel {...defaultProps} />);
    const button = screen.getByTestId("steering-submit");
    expect(button).toBeInTheDocument();
    expect(button).toHaveAttribute("type", "button");
  });

  it("calls onSteer with trimmed text and clears textarea on submit", () => {
    const onSteer = vi.fn();
    render(<SteeringPanel {...defaultProps} onSteer={onSteer} />);
    const textarea = screen.getByTestId("steering-textarea") as HTMLTextAreaElement;
    fireEvent.change(textarea, { target: { value: "  Focus on tests  " } });
    fireEvent.click(screen.getByTestId("steering-submit"));
    expect(onSteer).toHaveBeenCalledWith("Focus on tests");
    expect(textarea.value).toBe("");
  });

  it("does not call onSteer with empty or whitespace-only text", () => {
    const onSteer = vi.fn();
    render(<SteeringPanel {...defaultProps} onSteer={onSteer} />);
    const textarea = screen.getByTestId("steering-textarea") as HTMLTextAreaElement;
    fireEvent.change(textarea, { target: { value: "   " } });
    fireEvent.click(screen.getByTestId("steering-submit"));
    expect(onSteer).not.toHaveBeenCalled();
  });

  it("submits on Enter key (without Shift)", () => {
    const onSteer = vi.fn();
    render(<SteeringPanel {...defaultProps} onSteer={onSteer} />);
    const textarea = screen.getByTestId("steering-textarea") as HTMLTextAreaElement;
    fireEvent.change(textarea, { target: { value: "Run more tests" } });
    fireEvent.keyDown(textarea, { key: "Enter", shiftKey: false });
    expect(onSteer).toHaveBeenCalledWith("Run more tests");
  });

  it("does not submit on Shift+Enter (allows newline)", () => {
    const onSteer = vi.fn();
    render(<SteeringPanel {...defaultProps} onSteer={onSteer} />);
    const textarea = screen.getByTestId("steering-textarea") as HTMLTextAreaElement;
    fireEvent.change(textarea, { target: { value: "Run more tests" } });
    fireEvent.keyDown(textarea, { key: "Enter", shiftKey: true });
    expect(onSteer).not.toHaveBeenCalled();
  });

  it("renders steering history entries", () => {
    const history = [
      { id: "1", text: "Focus on tests", timestamp: 1000 },
      { id: "2", text: "Skip docs", timestamp: 2000 },
    ];
    render(<SteeringPanel {...defaultProps} steeringHistory={history} />);
    const list = screen.getByTestId("steering-history");
    expect(list).toBeInTheDocument();
    expect(screen.getByText("Focus on tests")).toBeInTheDocument();
    expect(screen.getByText("Skip docs")).toBeInTheDocument();
  });

  it("does not render history list when history is empty", () => {
    render(<SteeringPanel {...defaultProps} steeringHistory={[]} />);
    expect(screen.queryByTestId("steering-history")).not.toBeInTheDocument();
  });

  it("is hidden when status is idle", () => {
    render(<SteeringPanel {...defaultProps} status="idle" />);
    expect(screen.queryByTestId("steering-panel")).not.toBeInTheDocument();
  });

  it("is visible when status is paused", () => {
    render(<SteeringPanel {...defaultProps} status="paused" />);
    expect(screen.getByTestId("steering-panel")).toBeInTheDocument();
  });
});
