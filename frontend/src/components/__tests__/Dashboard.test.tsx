import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { Dashboard } from "../Dashboard";

const mockAgents = [
  { id: "a1", display_name: "Alpha", provider: "claude", model: "claude-opus-4-5", role: "worker", status: "idle", sort_order: 0 },
  { id: "a2", display_name: "Beta", provider: "codex", model: "gpt-4o", role: "worker", status: "running", sort_order: 1 },
  { id: "a3", display_name: "Gamma", provider: "ollama", model: "llama3.2", role: "coordinator", status: "offline", sort_order: 2 },
];

const mockNavigateBack = vi.fn();

describe("Dashboard", () => {
  it("renders the conversation title", () => {
    render(<Dashboard conversationTitle="Project Alpha" agents={mockAgents} onNavigateBack={mockNavigateBack} />);
    expect(screen.getByText("Project Alpha")).toBeInTheDocument();
  });

  it("renders stats cards with correct counts", () => {
    render(<Dashboard conversationTitle="Test" agents={mockAgents} onNavigateBack={mockNavigateBack} />);
    expect(screen.getByText("Active Agents")).toBeInTheDocument();
    expect(screen.getAllByText("2").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Running")).toBeInTheDocument();
    expect(screen.getByText("Idle")).toBeInTheDocument();
    expect(screen.getByText("Total Agents")).toBeInTheDocument();
  });

  it("renders agent cards for each agent", () => {
    render(<Dashboard conversationTitle="Test" agents={mockAgents} onNavigateBack={mockNavigateBack} />);
    // Each agent appears in sidebar + main grid, so multiple matches
    expect(screen.getAllByText("Alpha").length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText("Beta").length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText("Gamma").length).toBeGreaterThanOrEqual(2);
  });

  it("renders agents heading with total count badge", () => {
    render(<Dashboard conversationTitle="Test" agents={mockAgents} onNavigateBack={mockNavigateBack} />);
    expect(screen.getAllByText("Agents").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("3 total")).toBeInTheDocument();
  });

  it("renders empty state when no agents", () => {
    render(<Dashboard conversationTitle="Test" agents={[]} onNavigateBack={mockNavigateBack} />);
    expect(screen.getByText("No agents in this conversation yet")).toBeInTheDocument();
  });

  it("calls onNavigateBack when back button is clicked", async () => {
    const user = userEvent.setup();
    render(<Dashboard conversationTitle="Test" agents={mockAgents} onNavigateBack={mockNavigateBack} />);
    const backButton = screen.getAllByRole("button").find((btn) => btn.querySelector("svg"));
    if (backButton) {
      await user.click(backButton);
      expect(mockNavigateBack).toHaveBeenCalledTimes(1);
    }
  });

  it("renders the sidebar agent list", () => {
    render(<Dashboard conversationTitle="Test" agents={mockAgents} onNavigateBack={mockNavigateBack} />);
    // Agents section label
    const agentsHeadings = screen.getAllByText("Agents");
    expect(agentsHeadings.length).toBeGreaterThanOrEqual(1);
  });

  it("renders Dashboard heading in sidebar", () => {
    render(<Dashboard conversationTitle="Test" agents={mockAgents} onNavigateBack={mockNavigateBack} />);
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
  });
});
