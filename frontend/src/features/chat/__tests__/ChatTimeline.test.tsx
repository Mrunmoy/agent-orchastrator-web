import React from "react";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { ChatTimeline } from "../ChatTimeline";
import type { ChatMessageData } from "../types";

function makeMessage(overrides: Partial<ChatMessageData> = {}): ChatMessageData {
  return {
    id: "msg-1",
    agentName: "Claude",
    text: "Hello, world!",
    timestamp: "2026-03-07T12:00:00Z",
    isUser: false,
    ...overrides,
  };
}

/**
 * Helper to mock scroll geometry on a container element.
 * Sets scrollTop, scrollHeight, clientHeight to simulate scroll position.
 */
function mockScrollGeometry(
  element: HTMLElement,
  opts: { scrollTop: number; scrollHeight: number; clientHeight: number },
) {
  Object.defineProperty(element, "scrollTop", {
    get: () => opts.scrollTop,
    set: vi.fn(),
    configurable: true,
  });
  Object.defineProperty(element, "scrollHeight", {
    value: opts.scrollHeight,
    configurable: true,
  });
  Object.defineProperty(element, "clientHeight", {
    value: opts.clientHeight,
    configurable: true,
  });
}

describe("ChatTimeline – auto-scroll & new-message badge (T-302)", () => {
  beforeEach(() => {
    // scrollIntoView is not implemented in jsdom
    Element.prototype.scrollIntoView = vi.fn();
  });

  it("TT-302-01: auto-scrolls to bottom when new message arrives and user is at bottom", () => {
    const messages = [
      makeMessage({ id: "m1", text: "First" }),
      makeMessage({ id: "m2", text: "Second" }),
    ];

    const { rerender } = render(<ChatTimeline messages={messages} />);

    const container = screen.getByTestId("chat-timeline");

    // Simulate user being at the bottom (scrollTop + clientHeight >= scrollHeight - threshold)
    mockScrollGeometry(container, {
      scrollTop: 900,
      scrollHeight: 1000,
      clientHeight: 100,
    });

    // Add a new message
    const updatedMessages = [
      ...messages,
      makeMessage({ id: "m3", text: "Third" }),
    ];

    rerender(<ChatTimeline messages={updatedMessages} />);

    // The bottom sentinel should have been scrolled into view
    expect(Element.prototype.scrollIntoView).toHaveBeenCalled();
  });

  it("TT-302-02: shows 'New messages' badge when user scrolls up and new message arrives", () => {
    const messages = [
      makeMessage({ id: "m1", text: "First" }),
      makeMessage({ id: "m2", text: "Second" }),
    ];

    const { rerender } = render(<ChatTimeline messages={messages} />);

    const container = screen.getByTestId("chat-timeline");

    // Simulate user scrolled up (far from bottom)
    mockScrollGeometry(container, {
      scrollTop: 100,
      scrollHeight: 1000,
      clientHeight: 100,
    });

    // Fire a scroll event so the component detects the position
    fireEvent.scroll(container);

    // Add a new message
    const updatedMessages = [
      ...messages,
      makeMessage({ id: "m3", text: "Third" }),
    ];

    rerender(<ChatTimeline messages={updatedMessages} />);

    // The "New messages" badge should appear
    expect(screen.getByTestId("new-messages-badge")).toBeInTheDocument();
    expect(screen.getByText(/new messages/i)).toBeInTheDocument();
  });

  it("TT-302-03: clicking badge scrolls to latest message and hides badge", () => {
    const messages = [
      makeMessage({ id: "m1", text: "First" }),
      makeMessage({ id: "m2", text: "Second" }),
    ];

    const { rerender } = render(<ChatTimeline messages={messages} />);

    const container = screen.getByTestId("chat-timeline");

    // Simulate user scrolled up
    mockScrollGeometry(container, {
      scrollTop: 100,
      scrollHeight: 1000,
      clientHeight: 100,
    });

    fireEvent.scroll(container);

    // Add a new message to trigger the badge
    const updatedMessages = [
      ...messages,
      makeMessage({ id: "m3", text: "Third" }),
    ];

    rerender(<ChatTimeline messages={updatedMessages} />);

    const badge = screen.getByTestId("new-messages-badge");
    expect(badge).toBeInTheDocument();

    // Click the badge
    fireEvent.click(badge);

    // Badge should disappear
    expect(screen.queryByTestId("new-messages-badge")).not.toBeInTheDocument();

    // scrollIntoView should have been called (to scroll to bottom)
    expect(Element.prototype.scrollIntoView).toHaveBeenCalled();
  });
});
