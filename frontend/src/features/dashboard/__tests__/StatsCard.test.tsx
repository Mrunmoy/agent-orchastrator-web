import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { StatsCard } from "../StatsCard";

describe("StatsCard", () => {
  it("renders label and value", () => {
    render(<StatsCard label="Active Agents" value={3} />);
    expect(screen.getByText("Active Agents")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("generates correct data-testid from label", () => {
    render(<StatsCard label="Active Agents" value={5} />);
    expect(screen.getByTestId("stats-card-active-agents")).toBeInTheDocument();
  });

  it("renders string value", () => {
    render(<StatsCard label="Status" value="OK" />);
    expect(screen.getByText("OK")).toBeInTheDocument();
  });

  it("renders icon when provided", () => {
    render(<StatsCard label="Tasks" value={10} icon={<span data-testid="test-icon">I</span>} />);
    expect(screen.getByTestId("test-icon")).toBeInTheDocument();
  });

  it("does not render icon container when no icon", () => {
    const { container } = render(<StatsCard label="Tasks" value={0} />);
    expect(container.querySelector(".stats-card__icon")).toBeNull();
  });

  it("applies border-top color when color prop is provided", () => {
    render(<StatsCard label="Test" value={1} color="#ff0000" />);
    const card = screen.getByTestId("stats-card-test");
    expect(card).toHaveStyle({ borderTopColor: "#ff0000" });
  });
});
