import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { RunWindow } from "./RunWindow";
import type { RunWindowProps } from "./types";

const defaultProps: RunWindowProps = {
  status: "running",
  currentTurn: 5,
  batchSize: 20,
  elapsedSeconds: 120,
  steeringHistory: [],
  onNext20: vi.fn(),
  onContinue20: vi.fn(),
  onStopNow: vi.fn(),
  onSteer: vi.fn(),
};

describe("RunWindow", () => {
  it("renders the run window container", () => {
    render(<RunWindow {...defaultProps} />);
    expect(screen.getByTestId("run-window")).toBeInTheDocument();
  });

  // --- Batch window display ---

  it("displays current turn and batch size", () => {
    render(<RunWindow {...defaultProps} currentTurn={5} batchSize={20} />);
    const turnDisplay = screen.getByTestId("run-window-turn");
    expect(turnDisplay.textContent).toContain("5");
    expect(turnDisplay.textContent).toContain("20");
  });

  it("displays a progress bar", () => {
    render(<RunWindow {...defaultProps} currentTurn={10} batchSize={20} />);
    const progressBar = screen.getByTestId("run-window-progress");
    expect(progressBar).toBeInTheDocument();
    // progress bar inner element should reflect 50%
    const fill = screen.getByTestId("run-window-progress-fill");
    expect(fill.style.width).toBe("50%");
  });

  it("clamps progress bar to 100% when turn exceeds batch size", () => {
    render(<RunWindow {...defaultProps} currentTurn={25} batchSize={20} />);
    const fill = screen.getByTestId("run-window-progress-fill");
    expect(fill.style.width).toBe("100%");
  });

  it("displays elapsed time in mm:ss format", () => {
    render(<RunWindow {...defaultProps} elapsedSeconds={125} />);
    const elapsed = screen.getByTestId("run-window-elapsed");
    expect(elapsed.textContent).toContain("2:05");
  });

  it("displays elapsed time for less than a minute", () => {
    render(<RunWindow {...defaultProps} elapsedSeconds={9} />);
    const elapsed = screen.getByTestId("run-window-elapsed");
    expect(elapsed.textContent).toContain("0:09");
  });

  // --- Buttons based on status ---

  it("shows StopNow button when status is running", () => {
    render(<RunWindow {...defaultProps} status="running" />);
    expect(screen.getByTestId("stop-now-button")).toBeInTheDocument();
    expect(screen.queryByTestId("next-20-button")).not.toBeInTheDocument();
    expect(screen.queryByTestId("continue-20-button")).not.toBeInTheDocument();
  });

  it("shows Next20 and Continue20 buttons when status is paused", () => {
    render(<RunWindow {...defaultProps} status="paused" />);
    expect(screen.getByTestId("next-20-button")).toBeInTheDocument();
    expect(screen.getByTestId("continue-20-button")).toBeInTheDocument();
    expect(screen.queryByTestId("stop-now-button")).not.toBeInTheDocument();
  });

  it("shows StopNow button when status is queued", () => {
    render(<RunWindow {...defaultProps} status="queued" />);
    expect(screen.getByTestId("stop-now-button")).toBeInTheDocument();
  });

  it("shows no action buttons when status is idle", () => {
    render(<RunWindow {...defaultProps} status="idle" />);
    expect(screen.queryByTestId("stop-now-button")).not.toBeInTheDocument();
    expect(screen.queryByTestId("next-20-button")).not.toBeInTheDocument();
    expect(screen.queryByTestId("continue-20-button")).not.toBeInTheDocument();
  });

  // --- Button callbacks ---

  it("calls onNext20 when Next20 button is clicked", () => {
    const onNext20 = vi.fn();
    render(<RunWindow {...defaultProps} status="paused" onNext20={onNext20} />);
    fireEvent.click(screen.getByTestId("next-20-button"));
    expect(onNext20).toHaveBeenCalledOnce();
  });

  it("calls onContinue20 when Continue20 button is clicked", () => {
    const onContinue20 = vi.fn();
    render(<RunWindow {...defaultProps} status="paused" onContinue20={onContinue20} />);
    fireEvent.click(screen.getByTestId("continue-20-button"));
    expect(onContinue20).toHaveBeenCalledOnce();
  });

  it("shows confirmation before calling onStopNow", () => {
    const onStopNow = vi.fn();
    const confirmSpy = vi.spyOn(window, "confirm").mockReturnValue(false);
    render(<RunWindow {...defaultProps} status="running" onStopNow={onStopNow} />);
    fireEvent.click(screen.getByTestId("stop-now-button"));
    expect(confirmSpy).toHaveBeenCalled();
    expect(onStopNow).not.toHaveBeenCalled();
    confirmSpy.mockRestore();
  });

  it("calls onStopNow when user confirms stop", () => {
    const onStopNow = vi.fn();
    const confirmSpy = vi.spyOn(window, "confirm").mockReturnValue(true);
    render(<RunWindow {...defaultProps} status="running" onStopNow={onStopNow} />);
    fireEvent.click(screen.getByTestId("stop-now-button"));
    expect(onStopNow).toHaveBeenCalledOnce();
    confirmSpy.mockRestore();
  });

  // --- Button types ---

  it("all buttons have type=button", () => {
    render(<RunWindow {...defaultProps} status="paused" />);
    const buttons = screen.getAllByRole("button");
    for (const button of buttons) {
      expect(button).toHaveAttribute("type", "button");
    }
  });

  // --- SteeringPanel integration ---

  it("renders SteeringPanel when status is running or paused", () => {
    render(<RunWindow {...defaultProps} status="running" />);
    expect(screen.getByTestId("steering-panel")).toBeInTheDocument();
  });

  it("does not render SteeringPanel when status is idle", () => {
    render(<RunWindow {...defaultProps} status="idle" />);
    expect(screen.queryByTestId("steering-panel")).not.toBeInTheDocument();
  });

  it("passes onSteer to SteeringPanel", () => {
    const onSteer = vi.fn();
    render(<RunWindow {...defaultProps} status="running" onSteer={onSteer} />);
    const textarea = screen.getByTestId("steering-textarea") as HTMLTextAreaElement;
    fireEvent.change(textarea, { target: { value: "Do more" } });
    fireEvent.click(screen.getByTestId("steering-submit"));
    expect(onSteer).toHaveBeenCalledWith("Do more");
  });

  // --- Status display ---

  it("displays current status text", () => {
    render(<RunWindow {...defaultProps} status="running" />);
    const statusEl = screen.getByTestId("run-window-status");
    expect(statusEl.textContent).toContain("running");
  });
});
