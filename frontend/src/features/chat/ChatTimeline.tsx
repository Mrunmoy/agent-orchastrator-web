import React, { useCallback, useEffect, useRef, useState } from "react";
import type { ChatMessageData } from "./types";
import { ChatMessage } from "./ChatMessage";
import "./ChatTimeline.css";

export interface ChatTimelineProps {
  messages: ChatMessageData[];
}

/** How close to the bottom (in px) the user must be for auto-scroll to engage. */
const SCROLL_THRESHOLD = 80;

export function ChatTimeline({ messages }: ChatTimelineProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const isAtBottomRef = useRef(true);
  const [showBadge, setShowBadge] = useState(false);
  const prevMessageCountRef = useRef(messages.length);

  /** Determine whether the user is scrolled near the bottom. */
  const checkIsAtBottom = useCallback(() => {
    const el = containerRef.current;
    if (!el) return true;
    return el.scrollTop + el.clientHeight >= el.scrollHeight - SCROLL_THRESHOLD;
  }, []);

  /** Track scroll position on every scroll event. */
  const handleScroll = useCallback(() => {
    isAtBottomRef.current = checkIsAtBottom();
    // If user scrolled back to bottom while badge is showing, dismiss it
    if (isAtBottomRef.current && showBadge) {
      setShowBadge(false);
    }
  }, [checkIsAtBottom, showBadge]);

  /** When messages change: auto-scroll if at bottom, otherwise show badge. */
  useEffect(() => {
    const hasNewMessages = messages.length > prevMessageCountRef.current;
    prevMessageCountRef.current = messages.length;

    if (!hasNewMessages) return;

    if (isAtBottomRef.current) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    } else {
      setShowBadge(true);
    }
  }, [messages]);

  /** Clicking the badge scrolls to bottom and hides it. */
  const handleBadgeClick = useCallback(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    setShowBadge(false);
    isAtBottomRef.current = true;
  }, []);

  if (messages.length === 0) {
    return (
      <div className="chat-timeline" data-testid="chat-timeline">
        <div className="chat-timeline__empty">No messages yet. Start a conversation!</div>
      </div>
    );
  }

  return (
    <div
      className="chat-timeline"
      data-testid="chat-timeline"
      ref={containerRef}
      onScroll={handleScroll}
    >
      <div className="chat-timeline__messages">
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
        <div ref={bottomRef} />
      </div>

      {showBadge && (
        <button
          className="chat-timeline__new-messages-badge"
          data-testid="new-messages-badge"
          onClick={handleBadgeClick}
          type="button"
        >
          New messages
        </button>
      )}
    </div>
  );
}
