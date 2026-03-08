import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

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
}));

vi.mock("../api/client", () => api);

import { AppShell } from "./AppShell";

describe("T-306: PhaseBanner integration in AppShell", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.listConversations.mockResolvedValue([]);
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
