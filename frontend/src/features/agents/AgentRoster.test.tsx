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
    sort_order: 0,
  },
  {
    id: "agent-2",
    display_name: "Codex Helper",
    provider: "codex",
    model: "codex-1",
    role: "coordinator",
    status: "running",
    sort_order: 1,
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

  it("renders agents sorted by sort_order", () => {
    const unsortedAgents: AgentData[] = [
      { ...agents[1], sort_order: 0 },
      { ...agents[0], sort_order: 1 },
    ];
    render(<AgentRoster agents={unsortedAgents} onEdit={() => {}} onAdd={() => {}} />);
    const items = screen.getAllByTestId("agent-roster-item");
    expect(items[0]).toHaveTextContent("Codex Helper");
    expect(items[1]).toHaveTextContent("Claude Worker");
  });

  it("drag-drop reorders agents in the list", () => {
    const mockReorder = vi.fn().mockResolvedValue(undefined);
    render(
      <AgentRoster agents={agents} onEdit={() => {}} onAdd={() => {}} reorderAgent={mockReorder} />,
    );
    const items = screen.getAllByTestId("agent-roster-item");
    fireEvent.dragStart(items[0]);
    fireEvent.dragOver(items[1]);
    fireEvent.drop(items[1]);
    const updatedItems = screen.getAllByTestId("agent-roster-item");
    expect(updatedItems[0]).toHaveTextContent("Codex Helper");
    expect(updatedItems[1]).toHaveTextContent("Claude Worker");
    expect(mockReorder).toHaveBeenCalled();
  });
});
