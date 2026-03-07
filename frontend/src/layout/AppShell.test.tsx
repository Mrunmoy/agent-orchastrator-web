import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const api = vi.hoisted(() => ({
  listConversations: vi.fn(),
  createConversation: vi.fn(),
  selectConversation: vi.fn(),
  deleteConversation: vi.fn(),
  clearConversations: vi.fn(),
  listAgents: vi.fn(),
  createAgent: vi.fn(),
  updateAgent: vi.fn(),
  deleteAgent: vi.fn(),
  runBatch: vi.fn(),
  continueBatch: vi.fn(),
  stopBatch: vi.fn(),
  steerConversation: vi.fn(),
}));

vi.mock("../api/client", () => api);

import { AppShell } from "./AppShell";

describe("AppShell", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.listConversations.mockResolvedValue([]);
    api.listAgents.mockResolvedValue([]);
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
    api.createAgent.mockResolvedValue({
      id: "agent-1",
      display_name: "Codex Worker",
      provider: "codex",
      model: "codex-1",
      role: "worker",
      status: "idle",
    });
    api.updateAgent.mockResolvedValue({
      id: "agent-1",
      display_name: "Codex Worker",
      provider: "codex",
      model: "codex-1",
      role: "worker",
      status: "idle",
    });
    api.deleteAgent.mockResolvedValue(undefined);
  });

  it("renders the root layout container", async () => {
    render(<AppShell />);
    expect(screen.getByTestId("app-shell")).toBeInTheDocument();
    await waitFor(() => expect(api.listConversations).toHaveBeenCalledOnce());
  });

  it("creates a new conversation when New is clicked", async () => {
    render(<AppShell />);
    await waitFor(() => expect(api.listConversations).toHaveBeenCalledOnce());

    fireEvent.click(screen.getByRole("button", { name: /\+ new/i }));

    await waitFor(() => expect(api.createConversation).toHaveBeenCalledOnce());
    const list = screen.getByTestId("conversation-list");
    expect(within(list).getByText("Conversation 1")).toBeInTheDocument();
  });

  it("sends a message to orchestrator steer endpoint", async () => {
    render(<AppShell />);
    await waitFor(() => expect(api.listConversations).toHaveBeenCalledOnce());

    fireEvent.click(screen.getByRole("button", { name: /\+ new/i }));
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
    await waitFor(() => expect(api.createConversation).toHaveBeenCalledOnce());

    fireEvent.click(screen.getByRole("button", { name: /clear all/i }));

    await waitFor(() => expect(api.clearConversations).toHaveBeenCalledOnce());
    expect(screen.getByText("No conversations yet")).toBeInTheDocument();
  });

  it("opens agent editor and creates an agent", async () => {
    render(<AppShell />);
    await waitFor(() => expect(api.listAgents).toHaveBeenCalledOnce());

    fireEvent.click(screen.getByRole("button", { name: /add agent/i }));
    expect(screen.getByTestId("agent-editor")).toBeInTheDocument();

    const editor = screen.getByTestId("agent-editor");
    const inputs = within(editor).getAllByRole("textbox");
    fireEvent.change(inputs[0], { target: { value: "Codex Worker" } });
    fireEvent.change(inputs[1], { target: { value: "codex-1" } });
    fireEvent.click(within(editor).getByRole("button", { name: /save agent/i }));

    await waitFor(() => expect(api.createAgent).toHaveBeenCalledOnce());
    expect(screen.getByText("Codex Worker")).toBeInTheDocument();
  });
});
