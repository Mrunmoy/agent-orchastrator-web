import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { IntelligencePane } from "./IntelligencePane";

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
});
