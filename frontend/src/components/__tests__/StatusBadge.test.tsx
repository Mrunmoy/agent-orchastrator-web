import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { StatusBadge, type BadgeStatus } from "../StatusBadge";

describe("StatusBadge", () => {
  const allStatuses: BadgeStatus[] = [
    "idle",
    "running",
    "blocked",
    "done",
    "failed",
    "offline",
    "queued",
    "paused",
  ];

  it.each(allStatuses)("renders '%s' status text", (status) => {
    render(<StatusBadge status={status} />);
    expect(screen.getByTestId("status-badge")).toHaveTextContent(status);
  });

  it.each(allStatuses)(
    "applies data-status='%s' attribute",
    (status) => {
      render(<StatusBadge status={status} />);
      expect(screen.getByTestId("status-badge")).toHaveAttribute(
        "data-status",
        status,
      );
    },
  );

  it.each(allStatuses)("renders an SVG icon for '%s'", (status) => {
    const { container } = render(<StatusBadge status={status} />);
    expect(container.querySelector("svg")).toBeTruthy();
  });

  it("defaults to 'md' size (no --sm class)", () => {
    render(<StatusBadge status="idle" />);
    const badge = screen.getByTestId("status-badge");
    expect(badge.className).toContain("status-badge");
    expect(badge.className).not.toContain("status-badge--sm");
  });

  it("applies 'status-badge--sm' class when size='sm'", () => {
    render(<StatusBadge status="idle" size="sm" />);
    const badge = screen.getByTestId("status-badge");
    expect(badge.className).toContain("status-badge--sm");
  });

  it("applies 'md' size class without --sm modifier", () => {
    render(<StatusBadge status="running" size="md" />);
    const badge = screen.getByTestId("status-badge");
    expect(badge.className).toContain("status-badge");
    expect(badge.className).not.toContain("status-badge--sm");
  });
});
