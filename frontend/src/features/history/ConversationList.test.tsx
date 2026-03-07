import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ConversationList } from "./ConversationList";
import type { ConversationSummary } from "./types";

const sampleConversations: ConversationSummary[] = [
  {
    id: "c1",
    title: "First conversation",
    state: "debate",
    active: true,
    updated_at: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
  },
  {
    id: "c2",
    title: "Second conversation",
    state: "completed",
    active: false,
    updated_at: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
  },
];

describe("ConversationList", () => {
  it("renders empty state message when no conversations", () => {
    render(
      <ConversationList
        conversations={[]}
        onSelect={() => {}}
        onCreate={() => {}}
        onClearAll={() => {}}
      />,
    );
    expect(screen.getByText("No conversations yet")).toBeInTheDocument();
  });

  it("renders list of conversations", () => {
    render(
      <ConversationList
        conversations={sampleConversations}
        onSelect={() => {}}
        onCreate={() => {}}
        onClearAll={() => {}}
      />,
    );
    expect(screen.getByText("First conversation")).toBeInTheDocument();
    expect(screen.getByText("Second conversation")).toBeInTheDocument();
  });

  it("calls onSelect with correct id when clicking an item", () => {
    const handleSelect = vi.fn();
    render(
      <ConversationList
        conversations={sampleConversations}
        onSelect={handleSelect}
        onCreate={() => {}}
        onClearAll={() => {}}
      />,
    );
    fireEvent.click(screen.getByText("Second conversation"));
    expect(handleSelect).toHaveBeenCalledWith("c2");
  });

  it("highlights the active conversation", () => {
    render(
      <ConversationList
        conversations={sampleConversations}
        onSelect={() => {}}
        onCreate={() => {}}
        onClearAll={() => {}}
      />,
    );
    const items = screen.getAllByTestId("conv-item");
    expect(items[0]!.className).toContain("conv-item--active");
    expect(items[1]!.className).not.toContain("conv-item--active");
  });

  it("calls onCreate when New Conversation button is clicked", () => {
    const handleCreate = vi.fn();
    render(
      <ConversationList
        conversations={[]}
        onSelect={() => {}}
        onCreate={handleCreate}
        onClearAll={() => {}}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: /new conversation/i }));
    expect(handleCreate).toHaveBeenCalledOnce();
  });

  it("calls onClearAll when Clear All is confirmed", () => {
    const handleClearAll = vi.fn();
    vi.spyOn(window, "confirm").mockReturnValue(true);
    render(
      <ConversationList
        conversations={sampleConversations}
        onSelect={() => {}}
        onCreate={() => {}}
        onClearAll={handleClearAll}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: /clear all/i }));
    expect(handleClearAll).toHaveBeenCalledOnce();
    vi.restoreAllMocks();
  });

  it("does not call onClearAll when Clear All is cancelled", () => {
    const handleClearAll = vi.fn();
    vi.spyOn(window, "confirm").mockReturnValue(false);
    render(
      <ConversationList
        conversations={sampleConversations}
        onSelect={() => {}}
        onCreate={() => {}}
        onClearAll={handleClearAll}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: /clear all/i }));
    expect(handleClearAll).not.toHaveBeenCalled();
    vi.restoreAllMocks();
  });
});
