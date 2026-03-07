import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

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
  reorderAgent: vi.fn(),
  runBatch: vi.fn(),
  continueBatch: vi.fn(),
  stopBatch: vi.fn(),
  steerConversation: vi.fn(),
}));

vi.mock("../api/client", () => api);

import { AppShell } from "./AppShell";
import { TopBar } from "./TopBar";
import { HistoryPane } from "./HistoryPane";

describe("UI-012 Theme Smoke Tests", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    api.listConversations.mockResolvedValue([]);
    api.listAgents.mockResolvedValue([]);
  });

  it("AppShell root element has app-shell class", () => {
    render(<AppShell />);
    expect(screen.getByTestId("app-shell")).toHaveClass("app-shell");
  });

  it("TopBar renders with top-bar class", () => {
    render(<TopBar />);
    expect(screen.getByTestId("top-bar")).toHaveClass("top-bar");
  });

  it("HistoryPane renders with panel and history-pane classes", () => {
    render(<HistoryPane />);
    const pane = screen.getByTestId("history-pane");
    expect(pane).toHaveClass("panel");
    expect(pane).toHaveClass("history-pane");
  });

  it("TopBar status indicator has run-status testid", () => {
    render(<TopBar />);
    expect(screen.getByTestId("run-status")).toBeInTheDocument();
  });
});
