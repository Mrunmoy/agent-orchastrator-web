import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MainApp } from "../MainApp";

// Mock the API client
vi.mock("@/api/client", () => ({
  listConversations: vi.fn().mockResolvedValue([
    { id: "conv-1", title: "Test Conv", project_path: "/tmp", active: 1, updated_at: "2026-01-01T00:00:00Z" },
    { id: "conv-2", title: "Second Conv", project_path: "/tmp", active: 0, updated_at: "2026-01-01T00:00:00Z" },
  ]),
  listConversationAgents: vi.fn().mockResolvedValue([
    { id: "agent-1", display_name: "Alpha", provider: "claude", model: "claude-opus-4-5", role: "worker", status: "idle", sort_order: 0 },
  ]),
  createConversation: vi.fn().mockResolvedValue({ id: "conv-new", title: "New Conv", project_path: "/tmp", active: 1, updated_at: "2026-01-01T00:00:00Z" }),
  selectConversation: vi.fn().mockResolvedValue({ id: "conv-1", title: "Test Conv", project_path: "/tmp", active: 1, updated_at: "2026-01-01T00:00:00Z" }),
  deleteConversation: vi.fn().mockResolvedValue(undefined),
  createAgent: vi.fn().mockResolvedValue({ id: "agent-new", display_name: "New Agent", provider: "claude", model: "claude-opus-4-5", role: "worker", status: "idle", sort_order: 1 }),
  deleteAgent: vi.fn().mockResolvedValue(undefined),
  steerConversation: vi.fn().mockResolvedValue(undefined),
  runBatch: vi.fn().mockResolvedValue(undefined),
  stopBatch: vi.fn().mockResolvedValue(undefined),
  fetchRunStatus: vi.fn().mockResolvedValue(null),
  fetchArtifacts: vi.fn().mockResolvedValue([]),
  fetchLatestArtifact: vi.fn().mockResolvedValue(null),
  fetchEvents: vi.fn().mockResolvedValue([]),
  fetchLatestEvents: vi.fn().mockResolvedValue([]),
}));

// Mock sonner
vi.mock("sonner", async (importOriginal) => {
  const actual = await importOriginal<typeof import("sonner")>();
  return {
    ...actual,
    toast: { success: vi.fn(), error: vi.fn() },
  };
});

const mockNavigate = vi.fn();

describe("MainApp", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the sidebar with Agent Workspace heading", async () => {
    render(<MainApp onNavigateToDashboard={mockNavigate} />);
    expect(screen.getByText("Agent Workspace")).toBeInTheDocument();
  });

  it("renders Conversations and Direct Messages sections", async () => {
    render(<MainApp onNavigateToDashboard={mockNavigate} />);
    expect(screen.getByText("Conversations")).toBeInTheDocument();
    expect(screen.getByText("Direct Messages")).toBeInTheDocument();
  });

  it("loads conversations from API on mount", async () => {
    render(<MainApp onNavigateToDashboard={mockNavigate} />);
    await waitFor(() => {
      expect(screen.getAllByText("Test Conv").length).toBeGreaterThanOrEqual(1);
    });
  });

  it("loads agents when a conversation is active", async () => {
    render(<MainApp onNavigateToDashboard={mockNavigate} />);
    await waitFor(() => {
      // Alpha appears in sidebar agent list and possibly details panel
      expect(screen.getAllByText("Alpha").length).toBeGreaterThanOrEqual(1);
    });
  });

  it("renders the active conversation name in the header", async () => {
    render(<MainApp onNavigateToDashboard={mockNavigate} />);
    await waitFor(() => {
      // Appears in both sidebar and header
      expect(screen.getAllByText("Test Conv").length).toBeGreaterThanOrEqual(2);
    });
  });

  it("renders icon buttons with aria-labels", async () => {
    render(<MainApp onNavigateToDashboard={mockNavigate} />);
    expect(screen.getByLabelText("Search")).toBeInTheDocument();
    expect(screen.getByLabelText("Mentions")).toBeInTheDocument();
    expect(screen.getByLabelText("Notifications")).toBeInTheDocument();
    expect(screen.getByLabelText("Settings")).toBeInTheDocument();
  });

  it("renders Agent Dashboard button when conversation is active", async () => {
    render(<MainApp onNavigateToDashboard={mockNavigate} />);
    await waitFor(() => {
      expect(screen.getByText("Agent Dashboard")).toBeInTheDocument();
    });
  });

  it("renders Run Batch button when idle", async () => {
    render(<MainApp onNavigateToDashboard={mockNavigate} />);
    await waitFor(() => {
      expect(screen.getByText("Run Batch")).toBeInTheDocument();
    });
  });

  it("renders user footer with You and Active status", () => {
    render(<MainApp onNavigateToDashboard={mockNavigate} />);
    expect(screen.getByText("You")).toBeInTheDocument();
    expect(screen.getByText("Active")).toBeInTheDocument();
  });

  it("renders the message input", async () => {
    render(<MainApp onNavigateToDashboard={mockNavigate} />);
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Message #/)).toBeInTheDocument();
    });
  });

  it("renders conversation details panel", async () => {
    render(<MainApp onNavigateToDashboard={mockNavigate} />);
    await waitFor(() => {
      expect(screen.getByText("Conversation Details")).toBeInTheDocument();
    });
  });

  it("opens create conversation dialog", async () => {
    const user = userEvent.setup();
    render(<MainApp onNavigateToDashboard={mockNavigate} />);
    // Click the + button next to Conversations
    const addButtons = screen.getAllByRole("button");
    const conversationPlusBtn = addButtons.find(
      (btn) => btn.getAttribute("aria-haspopup") === "dialog" && btn.closest(".p-3"),
    );
    if (conversationPlusBtn) {
      await user.click(conversationPlusBtn);
      await waitFor(() => {
        expect(screen.getByText("Create New Conversation")).toBeInTheDocument();
      });
    }
  });
});
