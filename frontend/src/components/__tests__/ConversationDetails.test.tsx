import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ConversationDetails } from "../ConversationDetails";

const mockAgents = [
  { id: "a1", display_name: "Alpha", provider: "claude", model: "opus", role: "worker", status: "idle" },
  { id: "a2", display_name: "Beta", provider: "codex", model: "gpt-4o", role: "worker", status: "running" },
];

describe("ConversationDetails", () => {
  it("shows placeholder when no conversation selected", () => {
    render(<ConversationDetails conversationId={null} agents={[]} />);
    expect(screen.getByText("Select a conversation to view details")).toBeInTheDocument();
  });

  it("renders Conversation Details heading when conversation active", () => {
    render(<ConversationDetails conversationId="conv-1" agents={mockAgents} />);
    expect(screen.getByText("Conversation Details")).toBeInTheDocument();
  });

  it("renders Quick Overview card with agent counts", () => {
    render(<ConversationDetails conversationId="conv-1" agents={mockAgents} />);
    expect(screen.getByText("Quick Overview")).toBeInTheDocument();
    expect(screen.getAllByText("Active Agents").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Running").length).toBeGreaterThanOrEqual(1);
  });

  it("renders active agents with display names", () => {
    render(<ConversationDetails conversationId="conv-1" agents={mockAgents} />);
    expect(screen.getByText("Alpha")).toBeInTheDocument();
    expect(screen.getByText("Beta")).toBeInTheDocument();
  });

  it("shows agent status and provider", () => {
    render(<ConversationDetails conversationId="conv-1" agents={mockAgents} />);
    // Alpha is idle, Claude provider
    expect(screen.getByText(/idle.*claude/i)).toBeInTheDocument();
  });

  it("renders Batch Intelligence section", () => {
    render(<ConversationDetails conversationId="conv-1" agents={mockAgents} />);
    expect(screen.getByText("Batch Intelligence")).toBeInTheDocument();
    expect(screen.getByText("Agreement Map")).toBeInTheDocument();
    expect(screen.getByText("Conflict Map")).toBeInTheDocument();
    expect(screen.getByText("Neutral Memo")).toBeInTheDocument();
  });

  it("shows default text when no artifacts", () => {
    render(<ConversationDetails conversationId="conv-1" agents={mockAgents} />);
    expect(screen.getByText("No agreements recorded yet.")).toBeInTheDocument();
    expect(screen.getByText("No conflicts recorded yet.")).toBeInTheDocument();
    expect(screen.getByText("No memo available.")).toBeInTheDocument();
  });

  it("displays agreement artifact summary when provided", () => {
    const artifact = {
      id: "art-1",
      conversation_id: "conv-1",
      type: "agreement_map" as const,
      payload_json: '{"summary":"All agents agree"}',
      created_at: "2026-01-01T00:00:00Z",
      batch_id: null,
    };
    render(<ConversationDetails conversationId="conv-1" agents={mockAgents} agreementArtifact={artifact} />);
    expect(screen.getByText("All agents agree")).toBeInTheDocument();
  });

  it("displays conflict artifact summary when provided", () => {
    const artifact = {
      id: "art-2",
      conversation_id: "conv-1",
      type: "conflict_map" as const,
      payload_json: '{"summary":"Disagree on approach"}',
      created_at: "2026-01-01T00:00:00Z",
      batch_id: null,
    };
    render(<ConversationDetails conversationId="conv-1" agents={mockAgents} conflictArtifact={artifact} />);
    expect(screen.getByText("Disagree on approach")).toBeInTheDocument();
  });

  it("shows empty agents message when no agents", () => {
    render(<ConversationDetails conversationId="conv-1" agents={[]} />);
    expect(screen.getByText("No agents yet")).toBeInTheDocument();
  });

  it("shows correct configured agent count", () => {
    render(<ConversationDetails conversationId="conv-1" agents={mockAgents} />);
    expect(screen.getByText("2 agents configured")).toBeInTheDocument();
  });

  it("shows singular agent text for 1 agent", () => {
    render(<ConversationDetails conversationId="conv-1" agents={[mockAgents[0]!]} />);
    expect(screen.getByText("1 agent configured")).toBeInTheDocument();
  });
});
