import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { IntelligencePane } from "./IntelligencePane";
import type { Artifact } from "../api/client";

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
    render(
      <IntelligencePane
        agreementArtifact={artifact}
        agreementSummary="Fallback text"
      />,
    );
    expect(screen.getByText("Fallback text")).toBeInTheDocument();
  });

  it("prefers artifact data over string props", () => {
    const artifact = makeArtifact({
      payload_json: '{"summary":"From artifact"}',
    });
    render(
      <IntelligencePane
        agreementArtifact={artifact}
        agreementSummary="From prop"
      />,
    );
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
});
