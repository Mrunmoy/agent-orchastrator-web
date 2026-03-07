import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { MemoCard } from "./MemoCard";
import type { NeutralMemo } from "./types";

const mockMemo: NeutralMemo = {
  generated_at: "2026-03-07T10:30:00Z",
  summary: "The team mostly agrees on the approach.",
  key_points: [
    "Architecture is sound",
    "Performance needs benchmarking",
    "Security review pending",
  ],
  recommendation: "Proceed with implementation after security review.",
};

describe("MemoCard", () => {
  it("renders memo summary", () => {
    render(<MemoCard memo={mockMemo} />);
    expect(
      screen.getByText("The team mostly agrees on the approach.")
    ).toBeInTheDocument();
  });

  it("renders all key points as list items", () => {
    render(<MemoCard memo={mockMemo} />);
    expect(screen.getByText("Architecture is sound")).toBeInTheDocument();
    expect(
      screen.getByText("Performance needs benchmarking")
    ).toBeInTheDocument();
    expect(screen.getByText("Security review pending")).toBeInTheDocument();
  });

  it("renders recommendation", () => {
    render(<MemoCard memo={mockMemo} />);
    expect(
      screen.getByText("Proceed with implementation after security review.")
    ).toBeInTheDocument();
  });

  it("renders generated_at timestamp", () => {
    render(<MemoCard memo={mockMemo} />);
    expect(screen.getByText(/2026-03-07T10:30:00Z/)).toBeInTheDocument();
  });

  it("renders the memo-card container", () => {
    render(<MemoCard memo={mockMemo} />);
    expect(screen.getByTestId("memo-card")).toBeInTheDocument();
  });

  it("shows empty state when memo is null", () => {
    render(<MemoCard memo={null} />);
    expect(screen.getByTestId("memo-empty")).toBeInTheDocument();
    expect(screen.getByText("No memo available")).toBeInTheDocument();
  });
});
