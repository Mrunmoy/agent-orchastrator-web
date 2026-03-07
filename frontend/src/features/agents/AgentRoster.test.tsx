import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { AgentRoster } from "./AgentRoster";
import type { AgentData } from "./types";

const agents: AgentData[] = [
  {
    id: "agent-1",
    display_name: "Claude Worker",
    provider: "claude",
    model: "opus-4",
    role: "worker",
    status: "idle",
  },
  {
    id: "agent-2",
    display_name: "Codex Helper",
    provider: "codex",
    model: "codex-1",
    role: "coordinator",
    status: "running",
  },
];

describe("AgentRoster", () => {
  it("renders empty state when no agents", () => {
    render(<AgentRoster agents={[]} onEdit={() => {}} onAdd={() => {}} />);
    expect(screen.getByText("No agents configured")).toBeInTheDocument();
  });

  it("renders list of agents", () => {
    render(<AgentRoster agents={agents} onEdit={() => {}} onAdd={() => {}} />);
    expect(screen.getByText("Claude Worker")).toBeInTheDocument();
    expect(screen.getByText("Codex Helper")).toBeInTheDocument();
  });

  it("add button calls onAdd", () => {
    const onAdd = vi.fn();
    render(<AgentRoster agents={[]} onEdit={() => {}} onAdd={onAdd} />);
    fireEvent.click(screen.getByRole("button", { name: /add agent/i }));
    expect(onAdd).toHaveBeenCalledTimes(1);
  });
});
