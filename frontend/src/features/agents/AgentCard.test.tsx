import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { AgentCard } from "./AgentCard";
import type { AgentData } from "./types";

const mockAgent: AgentData = {
  id: "agent-1",
  display_name: "Claude Worker",
  provider: "claude",
  model: "opus-4",
  role: "worker",
  status: "idle",
};

describe("AgentCard", () => {
  it("shows display_name", () => {
    render(<AgentCard agent={mockAgent} onEdit={() => {}} />);
    expect(screen.getByText("Claude Worker")).toBeInTheDocument();
  });

  it("shows provider badge with correct class", () => {
    render(<AgentCard agent={mockAgent} onEdit={() => {}} />);
    const badge = screen.getByText("claude");
    expect(badge).toBeInTheDocument();
    expect(badge.className).toContain("provider-claude");
  });

  it("shows model name", () => {
    render(<AgentCard agent={mockAgent} onEdit={() => {}} />);
    expect(screen.getByText("opus-4")).toBeInTheDocument();
  });

  it("shows role badge", () => {
    render(<AgentCard agent={mockAgent} onEdit={() => {}} />);
    expect(screen.getByText("worker")).toBeInTheDocument();
  });

  it("shows status indicator with correct class", () => {
    render(<AgentCard agent={mockAgent} onEdit={() => {}} />);
    const status = screen.getByTestId("status-indicator");
    expect(status.className).toContain("status-idle");
  });

  it("edit button calls onEdit with agent id", () => {
    const onEdit = vi.fn();
    render(<AgentCard agent={mockAgent} onEdit={onEdit} />);
    fireEvent.click(screen.getByRole("button", { name: /edit/i }));
    expect(onEdit).toHaveBeenCalledWith("agent-1");
  });
});
