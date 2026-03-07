import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
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

  it("calls onSelect with correct id when clicking an item", async () => {
    const handleSelect = vi.fn();
    const user = userEvent.setup();
    render(
      <ConversationList
        conversations={sampleConversations}
        onSelect={handleSelect}
        onCreate={() => {}}
        onClearAll={() => {}}
      />,
    );
    await user.click(screen.getByText("Second conversation"));
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

  it("calls onCreate when New Conversation button is clicked", async () => {
    const handleCreate = vi.fn();
    const user = userEvent.setup();
    render(
      <ConversationList
        conversations={[]}
        onSelect={() => {}}
        onCreate={handleCreate}
        onClearAll={() => {}}
      />,
    );
    await user.click(screen.getByRole("button", { name: /new conversation/i }));
    expect(handleCreate).toHaveBeenCalledOnce();
  });

  it("calls onClearAll when Clear All is confirmed", async () => {
    const handleClearAll = vi.fn();
    const user = userEvent.setup();
    // Mock window.confirm to return true
    vi.spyOn(window, "confirm").mockReturnValue(true);
    render(
      <ConversationList
        conversations={sampleConversations}
        onSelect={() => {}}
        onCreate={() => {}}
        onClearAll={handleClearAll}
      />,
    );
    await user.click(screen.getByRole("button", { name: /clear all/i }));
    expect(handleClearAll).toHaveBeenCalledOnce();
    vi.restoreAllMocks();
  });

  it("does not call onClearAll when Clear All is cancelled", async () => {
    const handleClearAll = vi.fn();
    const user = userEvent.setup();
    vi.spyOn(window, "confirm").mockReturnValue(false);
    render(
      <ConversationList
        conversations={sampleConversations}
        onSelect={() => {}}
        onCreate={() => {}}
        onClearAll={handleClearAll}
      />,
    );
    await user.click(screen.getByRole("button", { name: /clear all/i }));
    expect(handleClearAll).not.toHaveBeenCalled();
    vi.restoreAllMocks();
  });
});
