import { fireEvent, render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { TopBar } from "./TopBar";

describe("TopBar", () => {
  it("renders the top bar container", () => {
    render(<TopBar />);
    expect(screen.getByTestId("top-bar")).toBeInTheDocument();
  });

  it("displays the app title", () => {
    render(<TopBar />);
    expect(screen.getByText("Agent Orchestrator Lab")).toBeInTheDocument();
  });

  it("renders the working directory input", () => {
    render(<TopBar />);
    expect(screen.getByLabelText("Working Directory")).toBeInTheDocument();
  });

  it("allows editing and saving the working directory", () => {
    render(<TopBar />);
    const input = screen.getByLabelText("Working Directory");
    fireEvent.change(input, { target: { value: "/tmp/my-project" } });
    fireEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(window.localStorage.getItem("ao_working_dir")).toBe("/tmp/my-project");
  });

  it("renders a status indicator", () => {
    render(<TopBar />);
    expect(screen.getByTestId("run-status")).toBeInTheDocument();
  });

  it("renders StatusBadge with 'idle' when runStatus is 'Idle'", () => {
    render(<TopBar runStatus="Idle" />);
    const badge = screen.getByTestId("status-badge");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveAttribute("data-status", "idle");
  });

  it("renders StatusBadge with 'running' when runStatus is 'Running'", () => {
    render(<TopBar runStatus="Running" />);
    const badge = screen.getByTestId("status-badge");
    expect(badge).toHaveAttribute("data-status", "running");
  });

  it("renders StatusBadge with 'paused' when runStatus is 'Paused'", () => {
    render(<TopBar runStatus="Paused" />);
    const badge = screen.getByTestId("status-badge");
    expect(badge).toHaveAttribute("data-status", "paused");
  });

  it("renders StatusBadge with 'idle' for unknown runStatus values", () => {
    render(<TopBar runStatus="SomethingElse" />);
    const badge = screen.getByTestId("status-badge");
    expect(badge).toHaveAttribute("data-status", "idle");
  });

  it("renders run batch button", () => {
    render(<TopBar />);
    expect(screen.getByRole("button", { name: /run.*batch/i })).toBeInTheDocument();
  });

  it("renders stop button", () => {
    render(<TopBar />);
    expect(screen.getByRole("button", { name: /stop/i })).toBeInTheDocument();
  });
});
