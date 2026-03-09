import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const api = vi.hoisted(() => ({
  listConversations: vi.fn(),
  createConversation: vi.fn(),
  selectConversation: vi.fn(),
  deleteConversation: vi.fn(),
  clearConversations: vi.fn(),
  listAgents: vi.fn(),
  listConversationAgents: vi.fn(),
  createAgent: vi.fn(),
  updateAgent: vi.fn(),
  deleteAgent: vi.fn(),
  reorderAgent: vi.fn(),
  removeAgentFromConversation: vi.fn(),
  reorderConversationAgents: vi.fn(),
  runBatch: vi.fn(),
  continueBatch: vi.fn(),
  stopBatch: vi.fn(),
  steerConversation: vi.fn(),
  fetchEvents: vi.fn(),
  fetchLatestEvents: vi.fn(),
  fetchTasks: vi.fn(),
  fetchRunStatus: vi.fn(),
}));

vi.mock("../api/client", () => api);

import { AppShell } from "./AppShell";

describe("AppShell", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.listConversations.mockResolvedValue([]);
    api.listAgents.mockResolvedValue([]);
    api.listConversationAgents.mockResolvedValue([]);
    api.removeAgentFromConversation.mockResolvedValue(undefined);
    api.reorderConversationAgents.mockResolvedValue(undefined);
    api.createConversation.mockResolvedValue({
      id: "conv-1",
      title: "Conversation 1",
      updated_at: "2026-01-01T00:00:00Z",
    });
    api.selectConversation.mockResolvedValue({
      id: "conv-1",
      title: "Conversation 1",
      updated_at: "2026-01-01T00:00:00Z",
    });
    api.deleteConversation.mockResolvedValue(undefined);
    api.clearConversations.mockResolvedValue(undefined);
    api.runBatch.mockResolvedValue(undefined);
    api.continueBatch.mockResolvedValue(undefined);
    api.stopBatch.mockResolvedValue(undefined);
    api.steerConversation.mockResolvedValue(undefined);
    api.fetchTasks.mockResolvedValue([]);
    api.fetchRunStatus.mockResolvedValue(null);
    api.createAgent.mockResolvedValue({
      id: "agent-1",
      display_name: "Codex Worker",
      provider: "codex",
      model: "codex-1",
      role: "worker",
      status: "idle",
      sort_order: 0,
    });
    api.updateAgent.mockResolvedValue({
      id: "agent-1",
      display_name: "Codex Worker",
      provider: "codex",
      model: "codex-1",
      role: "worker",
      status: "idle",
      sort_order: 0,
    });
    api.deleteAgent.mockResolvedValue(undefined);
    api.reorderAgent.mockResolvedValue(undefined);
  });

  it("renders the root layout container", async () => {
    render(<AppShell />);
    expect(screen.getByTestId("app-shell")).toBeInTheDocument();
    await waitFor(() => expect(api.listConversations).toHaveBeenCalledOnce());
  });

  it("shows new conversation form when + New is clicked", async () => {
    render(<AppShell />);
    await waitFor(() => expect(api.listConversations).toHaveBeenCalledOnce());

    fireEvent.click(screen.getByRole("button", { name: /\+ new/i }));

    expect(screen.getByTestId("conversation-creator")).toBeInTheDocument();
    expect(api.createConversation).not.toHaveBeenCalled();
  });

  it("cancels new conversation form without creating", async () => {
    render(<AppShell />);
    await waitFor(() => expect(api.listConversations).toHaveBeenCalledOnce());

    fireEvent.click(screen.getByRole("button", { name: /\+ new/i }));
    const creator = screen.getByTestId("conversation-creator");
    fireEvent.click(within(creator).getByRole("button", { name: /cancel/i }));

    expect(screen.queryByTestId("conversation-creator")).not.toBeInTheDocument();
    expect(api.createConversation).not.toHaveBeenCalled();
  });

  it("creates a new conversation when form is submitted", async () => {
    render(<AppShell />);
    await waitFor(() => expect(api.listConversations).toHaveBeenCalledOnce());

    fireEvent.click(screen.getByRole("button", { name: /\+ new/i }));
    const creator = screen.getByTestId("conversation-creator");

    fireEvent.change(within(creator).getByLabelText(/title/i), {
      target: { value: "My Project" },
    });
    fireEvent.change(within(creator).getByLabelText(/working directory/i), {
      target: { value: "/tmp/myproject" },
    });
    fireEvent.click(within(creator).getByRole("button", { name: /create/i }));

    await waitFor(() =>
      expect(api.createConversation).toHaveBeenCalledWith("My Project", "/tmp/myproject"),
    );
    const list = screen.getByTestId("conversation-list");
    expect(within(list).getByText("Conversation 1")).toBeInTheDocument();
    expect(screen.queryByTestId("conversation-creator")).not.toBeInTheDocument();
  });

  it("sends a message to orchestrator steer endpoint", async () => {
    render(<AppShell />);
    await waitFor(() => expect(api.listConversations).toHaveBeenCalledOnce());

    fireEvent.click(screen.getByRole("button", { name: /\+ new/i }));
    const creator = screen.getByTestId("conversation-creator");
    fireEvent.click(within(creator).getByRole("button", { name: /create/i }));
    await waitFor(() => expect(api.createConversation).toHaveBeenCalledOnce());

    fireEvent.change(screen.getByPlaceholderText("Type a message..."), {
      target: { value: "hello agents" },
    });
    fireEvent.click(screen.getByRole("button", { name: /send to group/i }));

    await waitFor(() =>
      expect(api.steerConversation).toHaveBeenCalledWith("conv-1", "hello agents"),
    );
    expect(screen.getByText("hello agents")).toBeInTheDocument();
  });

  it("clear all removes conversations", async () => {
    render(<AppShell />);
    await waitFor(() => expect(api.listConversations).toHaveBeenCalledOnce());

    fireEvent.click(screen.getByRole("button", { name: /\+ new/i }));
    const creator = screen.getByTestId("conversation-creator");
    fireEvent.click(within(creator).getByRole("button", { name: /create/i }));
    await waitFor(() => expect(api.createConversation).toHaveBeenCalledOnce());

    fireEvent.click(screen.getByRole("button", { name: /clear all/i }));

    await waitFor(() => expect(api.clearConversations).toHaveBeenCalledOnce());
    expect(screen.getByText("No conversations yet")).toBeInTheDocument();
  });

  it("opens agent editor and creates an agent", async () => {
    render(<AppShell />);
    await waitFor(() => expect(api.listConversations).toHaveBeenCalledOnce());

    fireEvent.click(screen.getByRole("button", { name: /add agent/i }));
    expect(screen.getByTestId("agent-editor")).toBeInTheDocument();

    const editor = screen.getByTestId("agent-editor");
    fireEvent.change(within(editor).getByLabelText("Name"), {
      target: { value: "Codex Worker" },
    });
    // Model is a dropdown; select a valid claude model
    fireEvent.change(within(editor).getByLabelText("Model"), {
      target: { value: "claude-3-5-sonnet-latest" },
    });
    fireEvent.click(within(editor).getByRole("button", { name: /save agent/i }));

    await waitFor(() => expect(api.createAgent).toHaveBeenCalledOnce());
    expect(screen.getAllByText("Codex Worker").length).toBeGreaterThanOrEqual(1);
  });

  it("model dropdown resets to first model when provider changes", async () => {
    render(<AppShell />);
    await waitFor(() => expect(api.listConversations).toHaveBeenCalledOnce());

    fireEvent.click(screen.getByRole("button", { name: /add agent/i }));
    const editor = screen.getByTestId("agent-editor");

    // Default is claude — first claude model should be selected
    const modelSelect = within(editor).getByLabelText("Model") as HTMLSelectElement;
    expect(modelSelect.value).toBe("claude-opus-4-5");

    // Switch provider to ollama
    fireEvent.change(within(editor).getByLabelText("Provider"), {
      target: { value: "ollama" },
    });

    // Model should have reset to first ollama model
    expect(modelSelect.value).toBe("llama3.2");
    const ollamaOptions = Array.from(modelSelect.options).map((o) => o.value);
    expect(ollamaOptions).toContain("llama3.2");
    expect(ollamaOptions).not.toContain("claude-opus-4-5");
  });

  it("personality dropdown shows all options and can be selected", async () => {
    render(<AppShell />);
    await waitFor(() => expect(api.listConversations).toHaveBeenCalledOnce());

    fireEvent.click(screen.getByRole("button", { name: /add agent/i }));
    const editor = screen.getByTestId("agent-editor");

    const personalitySelect = within(editor).getByLabelText("Personality") as HTMLSelectElement;
    expect(personalitySelect).toBeInTheDocument();

    const optionTexts = Array.from(personalitySelect.options).map((o) => o.text);
    expect(optionTexts).toContain("— none —");
    expect(optionTexts).toContain("Software Developer");
    expect(optionTexts).toContain("Code Reviewer");
    expect(optionTexts).toContain("Friendly Brainstormer");

    // Select a personality
    fireEvent.change(personalitySelect, { target: { value: "code_reviewer" } });
    expect(personalitySelect.value).toBe("code_reviewer");
  });

  it("removes agent from conversation (not global delete) when conversation is selected", async () => {
    api.listConversations.mockResolvedValue([
      {
        id: "conv-1",
        title: "Test",
        project_path: "/tmp",
        updated_at: "2026-01-01T00:00:00Z",
        active: 1,
      },
    ]);
    api.listConversationAgents.mockResolvedValue([
      {
        id: "agent-1",
        display_name: "Claude Bot",
        provider: "claude",
        model: "opus",
        role: "worker",
        status: "idle",
        sort_order: 0,
        turn_order: 1,
      },
    ]);
    render(<AppShell />);
    await waitFor(() => expect(api.listConversations).toHaveBeenCalledOnce());
    await waitFor(() => expect(api.listConversationAgents).toHaveBeenCalled());

    // Click Edit on the agent card
    const editBtn = await screen.findByRole("button", { name: /edit/i });
    fireEvent.click(editBtn);

    // Click Delete Agent
    const deleteBtn = await screen.findByRole("button", { name: /delete agent/i });
    fireEvent.click(deleteBtn);

    await waitFor(() =>
      expect(api.removeAgentFromConversation).toHaveBeenCalledWith("conv-1", "agent-1"),
    );
    expect(api.deleteAgent).not.toHaveBeenCalled();
  });

  it("app-shell has dark theme root element", () => {
    render(<AppShell />);
    const shell = screen.getByTestId("app-shell");
    expect(shell).toBeInTheDocument();
    expect(shell).toHaveClass("app-shell");
  });

  it("top bar has data-testid=top-bar with correct structure", async () => {
    render(<AppShell />);
    const topBar = screen.getByTestId("top-bar");
    expect(topBar).toBeInTheDocument();
    expect(topBar).toHaveClass("top-bar");
  });
});

describe("T-306: PhaseBanner integration in AppShell", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.listConversations.mockResolvedValue([]);
    api.listAgents.mockResolvedValue([]);
    api.listConversationAgents.mockResolvedValue([]);
  });

  it("renders PhaseBanner in the layout", () => {
    render(<AppShell />);
    expect(screen.getByTestId("phase-banner")).toBeInTheDocument();
  });

  it("displays the default phase name 'Design Debate'", () => {
    render(<AppShell />);
    expect(screen.getByTestId("phase-name")).toHaveTextContent("Design Debate");
  });

  it("displays the default round counter 'Round 1/5'", () => {
    render(<AppShell />);
    expect(screen.getByTestId("round-counter")).toHaveTextContent("Round 1/5");
  });

  it("does not show speaking indicator when no agent is speaking", () => {
    render(<AppShell />);
    expect(screen.queryByTestId("speaking-indicator")).not.toBeInTheDocument();
  });

  it("PhaseBanner appears between TopBar and main content", () => {
    render(<AppShell />);
    const shell = screen.getByTestId("app-shell");
    const topBar = screen.getByTestId("top-bar");
    const phaseBanner = screen.getByTestId("phase-banner");
    const mainContent = screen.getByTestId("main-content");

    const children = Array.from(shell.children);
    const topBarIndex = children.indexOf(topBar);
    const bannerIndex = children.indexOf(phaseBanner);
    const mainIndex = children.indexOf(mainContent);

    expect(topBarIndex).toBeLessThan(bannerIndex);
    expect(bannerIndex).toBeLessThan(mainIndex);
  });
});

describe("T-404: Dashboard view toggle", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.listConversations.mockResolvedValue([]);
    api.listAgents.mockResolvedValue([]);
    api.listConversationAgents.mockResolvedValue([]);
    api.removeAgentFromConversation.mockResolvedValue(undefined);
    api.reorderConversationAgents.mockResolvedValue(undefined);
    api.fetchTasks.mockResolvedValue([]);
    api.fetchRunStatus.mockResolvedValue(null);
    api.createConversation.mockResolvedValue({
      id: "conv-1",
      title: "Conversation 1",
      updated_at: "2026-01-01T00:00:00Z",
    });
    api.selectConversation.mockResolvedValue({
      id: "conv-1",
      title: "Conversation 1",
      updated_at: "2026-01-01T00:00:00Z",
    });
    api.runBatch.mockResolvedValue(undefined);
    api.continueBatch.mockResolvedValue(undefined);
    api.stopBatch.mockResolvedValue(undefined);
    api.steerConversation.mockResolvedValue(undefined);
  });

  it("renders view toggle with Chat and Dashboard buttons", async () => {
    render(<AppShell />);
    await waitFor(() => expect(api.listConversations).toHaveBeenCalledOnce());

    expect(screen.getByTestId("view-toggle")).toBeInTheDocument();
    expect(screen.getByTestId("view-toggle-chat")).toBeInTheDocument();
    expect(screen.getByTestId("view-toggle-dashboard")).toBeInTheDocument();
  });

  it("shows ChatPane by default, not KanbanBoard", async () => {
    render(<AppShell />);
    await waitFor(() => expect(api.listConversations).toHaveBeenCalledOnce());

    expect(screen.getByTestId("chat-pane")).toBeInTheDocument();
    expect(screen.queryByTestId("dashboard-view")).not.toBeInTheDocument();
  });

  it("switches to dashboard view when Dashboard button is clicked", async () => {
    render(<AppShell />);
    await waitFor(() => expect(api.listConversations).toHaveBeenCalledOnce());

    fireEvent.click(screen.getByTestId("view-toggle-dashboard"));

    expect(screen.queryByTestId("chat-pane")).not.toBeInTheDocument();
    expect(screen.getByTestId("dashboard-view")).toBeInTheDocument();
    expect(screen.getByTestId("stats-row")).toBeInTheDocument();
  });

  it("switches back to chat view when Chat button is clicked", async () => {
    render(<AppShell />);
    await waitFor(() => expect(api.listConversations).toHaveBeenCalledOnce());

    fireEvent.click(screen.getByTestId("view-toggle-dashboard"));
    expect(screen.getByTestId("dashboard-view")).toBeInTheDocument();

    fireEvent.click(screen.getByTestId("view-toggle-chat"));
    expect(screen.getByTestId("chat-pane")).toBeInTheDocument();
    expect(screen.queryByTestId("dashboard-view")).not.toBeInTheDocument();
  });

  it("fetches tasks when switching to dashboard with a selected conversation", async () => {
    api.listConversations.mockResolvedValue([
      {
        id: "conv-1",
        title: "Test",
        project_path: "/tmp",
        updated_at: "2026-01-01T00:00:00Z",
        active: 1,
      },
    ]);
    api.fetchTasks.mockResolvedValue([
      { id: "UI-001", title: "Build top bar", status: "done", assignee: "claude" },
      { id: "UI-002", title: "History pane", status: "implementing", assignee: "codex" },
    ]);

    render(<AppShell />);
    await waitFor(() => expect(api.listConversations).toHaveBeenCalledOnce());

    fireEvent.click(screen.getByTestId("view-toggle-dashboard"));

    await waitFor(() => expect(api.fetchTasks).toHaveBeenCalledWith("conv-1"));
    // DashboardView renders stats cards with task counts
    const completedCard = screen.getByTestId("stats-card-completed-tasks");
    expect(completedCard).toHaveTextContent("1");
    const runningCard = screen.getByTestId("stats-card-running-tasks");
    expect(runningCard).toHaveTextContent("1");
  });

  it("displays task stats in dashboard view", async () => {
    api.listConversations.mockResolvedValue([
      {
        id: "conv-1",
        title: "Test",
        project_path: "/tmp",
        updated_at: "2026-01-01T00:00:00Z",
        active: 1,
      },
    ]);
    api.fetchTasks.mockResolvedValue([
      { id: "T-1", title: "Task A", status: "todo" },
      { id: "T-2", title: "Task B", status: "done" },
    ]);

    render(<AppShell />);
    await waitFor(() => expect(api.listConversations).toHaveBeenCalledOnce());

    fireEvent.click(screen.getByTestId("view-toggle-dashboard"));

    await waitFor(() => expect(api.fetchTasks).toHaveBeenCalledWith("conv-1"));

    const totalCard = screen.getByTestId("stats-card-total-tasks");
    expect(totalCard).toHaveTextContent("2");

    const completedCard = screen.getByTestId("stats-card-completed-tasks");
    expect(completedCard).toHaveTextContent("1");
  });
});
