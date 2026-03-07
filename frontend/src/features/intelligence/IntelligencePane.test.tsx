import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { IntelligencePane } from "./IntelligencePane";
import type { IntelligenceData } from "./types";

const fullData: IntelligenceData = {
  conversation_id: "conv-1",
  positions: [
    {
      agent_id: "a1",
      agent_name: "Alice",
      position: "agree",
      summary: "Looks good",
    },
    {
      agent_id: "a2",
      agent_name: "Bob",
      position: "disagree",
      summary: "Not convinced",
    },
  ],
  memo: {
    generated_at: "2026-03-07T12:00:00Z",
    summary: "Mixed opinions.",
    key_points: ["Some agree", "Some disagree"],
    recommendation: "Discuss further.",
  },
};

const dataWithoutMemo: IntelligenceData = {
  conversation_id: "conv-2",
  positions: [
    {
      agent_id: "a1",
      agent_name: "Alice",
      position: "neutral",
      summary: "Undecided",
    },
  ],
  memo: null,
};

describe("IntelligencePane", () => {
  it("renders with full data", () => {
    render(<IntelligencePane data={fullData} />);
    expect(screen.getByTestId("intelligence-pane")).toBeInTheDocument();
    expect(screen.getByTestId("agreement-bar")).toBeInTheDocument();
    expect(screen.getByTestId("memo-card")).toBeInTheDocument();
  });

  it("shows empty state when data is null", () => {
    render(<IntelligencePane data={null} />);
    expect(screen.getByTestId("intelligence-empty")).toBeInTheDocument();
    expect(screen.getByText("No intelligence data")).toBeInTheDocument();
  });

  it("renders positions but shows memo empty state when memo is null", () => {
    render(<IntelligencePane data={dataWithoutMemo} />);
    expect(screen.getByTestId("intelligence-pane")).toBeInTheDocument();
    expect(screen.getByTestId("agreement-bar")).toBeInTheDocument();
    expect(screen.getByTestId("memo-empty")).toBeInTheDocument();
  });
});
