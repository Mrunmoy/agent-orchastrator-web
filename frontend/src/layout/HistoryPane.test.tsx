import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { HistoryPane } from "./HistoryPane";

describe("HistoryPane", () => {
  it("renders the history pane container", () => {
    render(<HistoryPane />);
    expect(screen.getByTestId("history-pane")).toBeInTheDocument();
  });

  it("displays the Conversations heading", () => {
    render(<HistoryPane />);
    expect(screen.getByText("Conversations")).toBeInTheDocument();
  });

  it("renders action buttons (New, Delete, Clear All)", () => {
    render(<HistoryPane />);
    expect(screen.getByRole("button", { name: /new/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /delete/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /clear all/i })).toBeInTheDocument();
  });

  it("renders the conversation list area", () => {
    render(<HistoryPane />);
    expect(screen.getByTestId("conversation-list")).toBeInTheDocument();
  });

  it("renders the agent roster area", () => {
    render(<HistoryPane />);
    expect(screen.getByTestId("agent-roster")).toBeInTheDocument();
  });
});
