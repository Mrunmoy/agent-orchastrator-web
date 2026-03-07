import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ConversationItem } from "./ConversationItem";
import type { ConversationSummary } from "./types";

function makeConversation(
  overrides: Partial<ConversationSummary> = {},
): ConversationSummary {
  return {
    id: "conv-1",
    title: "Test conversation",
    state: "debate",
    active: false,
    updated_at: new Date().toISOString(),
    ...overrides,
  };
}

describe("ConversationItem", () => {
  it("shows the conversation title", () => {
    render(
      <ConversationItem conversation={makeConversation()} onSelect={() => {}} />,
    );
    expect(screen.getByText("Test conversation")).toBeInTheDocument();
  });

  it("truncates long titles", () => {
    const longTitle = "A".repeat(80);
    render(
      <ConversationItem
        conversation={makeConversation({ title: longTitle })}
        onSelect={() => {}}
      />,
    );
    const titleEl = screen.getByTestId("conv-item-title");
    expect(titleEl.textContent!.length).toBeLessThan(longTitle.length);
    expect(titleEl.textContent).toContain("...");
  });

  it("shows state badge with correct color class for debate", () => {
    render(
      <ConversationItem
        conversation={makeConversation({ state: "debate" })}
        onSelect={() => {}}
      />,
    );
    const badge = screen.getByTestId("state-badge");
    expect(badge).toHaveTextContent("debate");
    expect(badge.className).toContain("badge--debate");
  });

  it("shows state badge with correct color class for autonomous_work", () => {
    render(
      <ConversationItem
        conversation={makeConversation({ state: "autonomous_work" })}
        onSelect={() => {}}
      />,
    );
    const badge = screen.getByTestId("state-badge");
    expect(badge).toHaveTextContent("autonomous_work");
    expect(badge.className).toContain("badge--autonomous_work");
  });

  it("shows state badge with correct color class for needs_user_input", () => {
    render(
      <ConversationItem
        conversation={makeConversation({ state: "needs_user_input" })}
        onSelect={() => {}}
      />,
    );
    const badge = screen.getByTestId("state-badge");
    expect(badge.className).toContain("badge--needs_user_input");
  });

  it("shows state badge with correct color class for completed", () => {
    render(
      <ConversationItem
        conversation={makeConversation({ state: "completed" })}
        onSelect={() => {}}
      />,
    );
    const badge = screen.getByTestId("state-badge");
    expect(badge.className).toContain("badge--completed");
  });

  it("shows state badge with correct color class for failed", () => {
    render(
      <ConversationItem
        conversation={makeConversation({ state: "failed" })}
        onSelect={() => {}}
      />,
    );
    const badge = screen.getByTestId("state-badge");
    expect(badge.className).toContain("badge--failed");
  });

  it("shows relative time", () => {
    const twoMinAgo = new Date(Date.now() - 2 * 60 * 1000).toISOString();
    render(
      <ConversationItem
        conversation={makeConversation({ updated_at: twoMinAgo })}
        onSelect={() => {}}
      />,
    );
    expect(screen.getByTestId("conv-item-time")).toHaveTextContent("2m ago");
  });

  it("highlights active conversation", () => {
    render(
      <ConversationItem
        conversation={makeConversation({ active: true })}
        onSelect={() => {}}
      />,
    );
    const row = screen.getByTestId("conv-item");
    expect(row.className).toContain("conv-item--active");
  });

  it("does not highlight inactive conversation", () => {
    render(
      <ConversationItem
        conversation={makeConversation({ active: false })}
        onSelect={() => {}}
      />,
    );
    const row = screen.getByTestId("conv-item");
    expect(row.className).not.toContain("conv-item--active");
  });
});
