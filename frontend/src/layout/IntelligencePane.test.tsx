import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { IntelligencePane } from "./IntelligencePane";
import type { Artifact } from "../api/client";
import type { AgentData } from "../features/agents";

function makeArtifact(overrides: Partial<Artifact> = {}): Artifact {
  return {
    id: overrides.id ?? "art-1",
    conversation_id: overrides.conversation_id ?? "conv-1",
    type: overrides.type ?? "agreement_map",
    payload_json: overrides.payload_json ?? '{"summary":"All agree"}',
    created_at: overrides.created_at ?? "2026-03-08T00:00:00Z",
    batch_id: overrides.batch_id ?? null,
  };
}

function makeAgent(overrides: Partial<AgentData> = {}): AgentData {
  return {
    id: overrides.id ?? "agent-1",
    display_name: overrides.display_name ?? "Alice",
    provider: overrides.provider ?? "claude",
    model: overrides.model ?? "claude-opus-4-5",
    role: overrides.role ?? "worker",
    status: overrides.status ?? "idle",
    sort_order: overrides.sort_order ?? 0,
  };
}

describe("IntelligencePane", () => {
  it("renders the intelligence pane container", () => {
    render(<IntelligencePane />);
    expect(screen.getByTestId("intelligence-pane")).toBeInTheDocument();
  });

  it("displays the Batch Intelligence heading", () => {
    render(<IntelligencePane />);
    expect(screen.getByText("Batch Intelligence")).toBeInTheDocument();
  });

  it("renders the agreement section", () => {
    render(<IntelligencePane />);
    expect(screen.getByTestId("agreement-section")).toBeInTheDocument();
  });

  it("renders the conflict section", () => {
    render(<IntelligencePane />);
    expect(screen.getByTestId("conflict-section")).toBeInTheDocument();
  });

  it("renders the memo section", () => {
    render(<IntelligencePane />);
    expect(screen.getByTestId("memo-section")).toBeInTheDocument();
  });

  it("shows default text when no artifacts provided", () => {
    render(<IntelligencePane />);
    expect(screen.getByText("No agreements recorded yet.")).toBeInTheDocument();
    expect(screen.getByText("No conflicts recorded yet.")).toBeInTheDocument();
    expect(screen.getByText("No memo available.")).toBeInTheDocument();
  });

  it("shows artifact summary when agreementArtifact is provided", () => {
    const artifact = makeArtifact({
      type: "agreement_map",
      payload_json: '{"summary":"Agents agree on architecture"}',
    });
    render(<IntelligencePane agreementArtifact={artifact} />);
    expect(screen.getByText("Agents agree on architecture")).toBeInTheDocument();
  });

  it("shows artifact summary when conflictArtifact is provided", () => {
    const artifact = makeArtifact({
      type: "conflict_map",
      payload_json: '{"summary":"Disagree on testing strategy"}',
    });
    render(<IntelligencePane conflictArtifact={artifact} />);
    expect(screen.getByText("Disagree on testing strategy")).toBeInTheDocument();
  });

  it("shows artifact summary when memoArtifact is provided", () => {
    const artifact = makeArtifact({
      type: "neutral_memo",
      payload_json: '{"summary":"Balanced view of options"}',
    });
    render(<IntelligencePane memoArtifact={artifact} />);
    expect(screen.getByText("Balanced view of options")).toBeInTheDocument();
  });

  it("falls back to text field when summary is not present in payload", () => {
    const artifact = makeArtifact({
      payload_json: '{"text":"Using text field instead"}',
    });
    render(<IntelligencePane agreementArtifact={artifact} />);
    expect(screen.getByText("Using text field instead")).toBeInTheDocument();
  });

  it("falls back to string props when artifact payload is invalid JSON", () => {
    const artifact = makeArtifact({ payload_json: "not-json" });
    render(<IntelligencePane agreementArtifact={artifact} agreementSummary="Fallback text" />);
    expect(screen.getByText("Fallback text")).toBeInTheDocument();
  });

  it("prefers artifact data over string props", () => {
    const artifact = makeArtifact({
      payload_json: '{"summary":"From artifact"}',
    });
    render(<IntelligencePane agreementArtifact={artifact} agreementSummary="From prop" />);
    expect(screen.getByText("From artifact")).toBeInTheDocument();
    expect(screen.queryByText("From prop")).not.toBeInTheDocument();
  });

  it("uses intel-card__content class when artifact data is present", () => {
    const artifact = makeArtifact({
      payload_json: '{"summary":"Has data"}',
    });
    render(<IntelligencePane agreementArtifact={artifact} />);
    const section = screen.getByTestId("agreement-section");
    const paragraph = section.querySelector("p");
    expect(paragraph?.className).toBe("intel-card__content");
  });

  it("uses intel-card__empty class when no artifact data", () => {
    render(<IntelligencePane />);
    const section = screen.getByTestId("agreement-section");
    const paragraph = section.querySelector("p");
    expect(paragraph?.className).toBe("intel-card__empty");
  });

  // --- New tests for T-505 ---

  it("renders overview card with agent count", () => {
    const agents = [makeAgent({ id: "a1" }), makeAgent({ id: "a2", display_name: "Bob" })];
    render(<IntelligencePane agents={agents} />);
    const card = screen.getByTestId("overview-card");
    expect(card).toBeInTheDocument();
    expect(card.textContent).toContain("2");
    expect(card.textContent).toContain("agents");
  });

  it("renders overview card with zero agents when none provided", () => {
    render(<IntelligencePane />);
    const card = screen.getByTestId("overview-card");
    expect(card).toBeInTheDocument();
    expect(card.textContent).toContain("0");
  });

  it("renders overview card with artifact count", () => {
    const artifact = makeArtifact({ payload_json: '{"summary":"ok"}' });
    render(<IntelligencePane agreementArtifact={artifact} conflictArtifact={artifact} />);
    const card = screen.getByTestId("overview-card");
    expect(card.textContent).toContain("2");
    expect(card.textContent).toContain("artifacts");
  });

  it("renders active agents section with agent avatars", () => {
    const agents = [
      makeAgent({ id: "a1", display_name: "Alice", provider: "claude" }),
      makeAgent({ id: "a2", display_name: "Bob", provider: "codex" }),
    ];
    render(<IntelligencePane agents={agents} />);
    const section = screen.getByTestId("active-agents-section");
    expect(section).toBeInTheDocument();
    expect(section.textContent).toContain("Alice");
    expect(section.textContent).toContain("Bob");
    // Check avatars render first letter
    const avatars = section.querySelectorAll(".agent-avatar");
    expect(avatars).toHaveLength(2);
    expect(avatars[0].textContent).toBe("A");
    expect(avatars[1].textContent).toBe("B");
  });

  it("renders intelligence cards with colored borders", () => {
    render(<IntelligencePane />);
    const section = screen.getByTestId("intelligence-section");
    expect(section).toBeInTheDocument();
    const agreementCard = screen.getByTestId("agreement-section");
    expect(agreementCard.classList.contains("intel-card--ok")).toBe(true);
    const conflictCard = screen.getByTestId("conflict-section");
    expect(conflictCard.classList.contains("intel-card--warn")).toBe(true);
    const memoCard = screen.getByTestId("memo-section");
    expect(memoCard.classList.contains("intel-card--memo")).toBe(true);
  });

  it("shows 'and N more' for overflow agents", () => {
    const agents = Array.from({ length: 8 }, (_, i) =>
      makeAgent({ id: `a${i}`, display_name: `Agent${i}` }),
    );
    render(<IntelligencePane agents={agents} />);
    const overflow = screen.getByTestId("agents-overflow");
    expect(overflow).toBeInTheDocument();
    expect(overflow.textContent).toBe("and 3 more");
  });

  it("does not show overflow when agents fit within limit", () => {
    const agents = [makeAgent({ id: "a1" }), makeAgent({ id: "a2", display_name: "Bob" })];
    render(<IntelligencePane agents={agents} />);
    expect(screen.queryByTestId("agents-overflow")).not.toBeInTheDocument();
  });

  it("falls back to text summaries when no artifacts provided", () => {
    render(
      <IntelligencePane
        agreementSummary="Custom agreement text"
        conflictSummary="Custom conflict text"
        memoSummary="Custom memo text"
      />,
    );
    expect(screen.getByText("Custom agreement text")).toBeInTheDocument();
    expect(screen.getByText("Custom conflict text")).toBeInTheDocument();
    expect(screen.getByText("Custom memo text")).toBeInTheDocument();
  });

  it("shows 'No agents assigned' when agents array is empty", () => {
    render(<IntelligencePane agents={[]} />);
    expect(screen.getByText("No agents assigned.")).toBeInTheDocument();
  });

  it("shows singular 'agent' for exactly 1 agent", () => {
    render(<IntelligencePane agents={[makeAgent()]} />);
    const card = screen.getByTestId("overview-card");
    expect(card.textContent).toContain("1");
    expect(card.textContent).toMatch(/1\s*agent(?!s)/);
  });
});
