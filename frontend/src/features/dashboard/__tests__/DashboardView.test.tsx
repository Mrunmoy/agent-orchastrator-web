import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { DashboardView } from "../DashboardView";
import type { AgentData } from "../../agents";

vi.mock("../../../api/client", () => ({
  fetchTasks: vi.fn(),
}));

import { fetchTasks } from "../../../api/client";
const mockFetchTasks = vi.mocked(fetchTasks);

const MOCK_AGENTS: AgentData[] = [
  {
    id: "a1",
    display_name: "Claude Worker",
    provider: "claude",
    model: "claude-opus-4-5",
    role: "worker",
    status: "idle",
    sort_order: 0,
  },
  {
    id: "a2",
    display_name: "Codex Helper",
    provider: "codex",
    model: "codex-mini-latest",
    role: "coordinator",
    status: "running",
    sort_order: 1,
  },
  {
    id: "a3",
    display_name: "Offline Bot",
    provider: "ollama",
    model: "llama3.2",
    role: "worker",
    status: "offline",
    sort_order: 2,
  },
];

describe("DashboardView", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFetchTasks.mockResolvedValue([]);
  });

  it("renders the dashboard-view root", () => {
    render(<DashboardView conversationId={null} agents={[]} />);
    expect(screen.getByTestId("dashboard-view")).toBeInTheDocument();
  });

  it("renders four stats cards", () => {
    render(<DashboardView conversationId={null} agents={MOCK_AGENTS} />);
    expect(screen.getByTestId("stats-card-active-agents")).toBeInTheDocument();
    expect(screen.getByTestId("stats-card-running-tasks")).toBeInTheDocument();
    expect(screen.getByTestId("stats-card-completed-tasks")).toBeInTheDocument();
    expect(screen.getByTestId("stats-card-total-tasks")).toBeInTheDocument();
  });

  it("computes active agents count (excludes offline)", () => {
    render(<DashboardView conversationId={null} agents={MOCK_AGENTS} />);
    const card = screen.getByTestId("stats-card-active-agents");
    // 2 agents are not offline (idle + running)
    expect(card).toHaveTextContent("2");
  });

  it("renders agent grid with agent cards", () => {
    render(<DashboardView conversationId={null} agents={MOCK_AGENTS} />);
    expect(screen.getByTestId("agent-grid")).toBeInTheDocument();
    expect(screen.getByTestId("agent-card-a1")).toBeInTheDocument();
    expect(screen.getByTestId("agent-card-a2")).toBeInTheDocument();
    expect(screen.getByTestId("agent-card-a3")).toBeInTheDocument();
  });

  it("shows agent name, model, role, and status", () => {
    render(<DashboardView conversationId={null} agents={MOCK_AGENTS} />);
    expect(screen.getByText("Claude Worker")).toBeInTheDocument();
    expect(screen.getByText("claude-opus-4-5")).toBeInTheDocument();
    expect(screen.getByText("Codex Helper")).toBeInTheDocument();
    expect(screen.getByText("running")).toBeInTheDocument();
  });

  it("shows empty state when no agents", () => {
    render(<DashboardView conversationId={null} agents={[]} />);
    expect(screen.getByTestId("dashboard-empty")).toBeInTheDocument();
  });

  it("fetches tasks when conversationId is provided", async () => {
    mockFetchTasks.mockResolvedValue([
      { id: "t1", title: "Task 1", status: "done" },
      { id: "t2", title: "Task 2", status: "implementing" },
      { id: "t3", title: "Task 3", status: "todo" },
    ]);

    render(<DashboardView conversationId="conv-1" agents={MOCK_AGENTS} />);

    await waitFor(() => {
      expect(mockFetchTasks).toHaveBeenCalledWith("conv-1");
    });

    // Check task stats updated
    const completedCard = screen.getByTestId("stats-card-completed-tasks");
    expect(completedCard).toHaveTextContent("1");

    const runningCard = screen.getByTestId("stats-card-running-tasks");
    expect(runningCard).toHaveTextContent("1");

    const totalCard = screen.getByTestId("stats-card-total-tasks");
    expect(totalCard).toHaveTextContent("3");
  });

  it("does not fetch tasks when conversationId is null", () => {
    render(<DashboardView conversationId={null} agents={[]} />);
    expect(mockFetchTasks).not.toHaveBeenCalled();
  });

  it("handles fetch error gracefully", async () => {
    mockFetchTasks.mockRejectedValue(new Error("Network error"));

    render(<DashboardView conversationId="conv-1" agents={MOCK_AGENTS} />);

    await waitFor(() => {
      expect(mockFetchTasks).toHaveBeenCalled();
    });

    // Should show 0 for all task stats
    const totalCard = screen.getByTestId("stats-card-total-tasks");
    expect(totalCard).toHaveTextContent("0");
  });
});
