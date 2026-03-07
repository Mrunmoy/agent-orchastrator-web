import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { RunControls } from "./RunControls";

const defaultProps = {
  status: "idle" as const,
  onRun: vi.fn(),
  onContinue: vi.fn(),
  onStop: vi.fn(),
  onSteer: vi.fn(),
};

describe("RunControls", () => {
  it("renders the run-controls container", () => {
    render(<RunControls {...defaultProps} />);
    expect(screen.getByTestId("run-controls")).toBeInTheDocument();
  });

  it("shows status indicator with current status text", () => {
    render(<RunControls {...defaultProps} status="idle" />);
    const statusEl = screen.getByTestId("run-status");
    expect(statusEl.textContent).toContain("idle");
  });

  it("shows Run button when status is idle", () => {
    render(<RunControls {...defaultProps} status="idle" />);
    expect(screen.getByTestId("run-button")).toBeInTheDocument();
    expect(screen.queryByTestId("continue-button")).not.toBeInTheDocument();
    expect(screen.queryByTestId("stop-button")).not.toBeInTheDocument();
  });

  it("calls onRun when Run button is clicked", () => {
    const onRun = vi.fn();
    render(<RunControls {...defaultProps} status="idle" onRun={onRun} />);
    fireEvent.click(screen.getByTestId("run-button"));
    expect(onRun).toHaveBeenCalledOnce();
  });

  it("shows Continue button when status is paused", () => {
    render(<RunControls {...defaultProps} status="paused" />);
    expect(screen.getByTestId("continue-button")).toBeInTheDocument();
    expect(screen.queryByTestId("run-button")).not.toBeInTheDocument();
  });

  it("calls onContinue when Continue button is clicked", () => {
    const onContinue = vi.fn();
    render(
      <RunControls {...defaultProps} status="paused" onContinue={onContinue} />,
    );
    fireEvent.click(screen.getByTestId("continue-button"));
    expect(onContinue).toHaveBeenCalledOnce();
  });

  it("shows Stop button when status is running", () => {
    render(<RunControls {...defaultProps} status="running" />);
    expect(screen.getByTestId("stop-button")).toBeInTheDocument();
    expect(screen.queryByTestId("run-button")).not.toBeInTheDocument();
    expect(screen.queryByTestId("continue-button")).not.toBeInTheDocument();
  });

  it("shows Stop button when status is queued", () => {
    render(<RunControls {...defaultProps} status="queued" />);
    expect(screen.getByTestId("stop-button")).toBeInTheDocument();
  });

  it("calls onStop when Stop button is clicked", () => {
    const onStop = vi.fn();
    render(<RunControls {...defaultProps} status="running" onStop={onStop} />);
    fireEvent.click(screen.getByTestId("stop-button"));
    expect(onStop).toHaveBeenCalledOnce();
  });

  it("shows steering input when status is running", () => {
    render(<RunControls {...defaultProps} status="running" />);
    expect(screen.getByTestId("steer-input")).toBeInTheDocument();
    expect(screen.getByTestId("steer-button")).toBeInTheDocument();
  });

  it("shows steering input when status is paused", () => {
    render(<RunControls {...defaultProps} status="paused" />);
    expect(screen.getByTestId("steer-input")).toBeInTheDocument();
    expect(screen.getByTestId("steer-button")).toBeInTheDocument();
  });

  it("does not show steering input when status is idle", () => {
    render(<RunControls {...defaultProps} status="idle" />);
    expect(screen.queryByTestId("steer-input")).not.toBeInTheDocument();
    expect(screen.queryByTestId("steer-button")).not.toBeInTheDocument();
  });

  it("calls onSteer with note text and clears input", () => {
    const onSteer = vi.fn();
    render(
      <RunControls {...defaultProps} status="running" onSteer={onSteer} />,
    );
    const input = screen.getByTestId("steer-input") as HTMLInputElement;
    fireEvent.change(input, { target: { value: "Focus on tests" } });
    fireEvent.click(screen.getByTestId("steer-button"));
    expect(onSteer).toHaveBeenCalledWith("Focus on tests");
    expect(input.value).toBe("");
  });

  it("does not call onSteer with empty note", () => {
    const onSteer = vi.fn();
    render(
      <RunControls {...defaultProps} status="running" onSteer={onSteer} />,
    );
    fireEvent.click(screen.getByTestId("steer-button"));
    expect(onSteer).not.toHaveBeenCalled();
  });
});
