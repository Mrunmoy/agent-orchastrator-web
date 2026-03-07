import React, { useEffect, useRef } from "react";
import type { ChatMessageData } from "./types";
import { ChatMessage } from "./ChatMessage";
import "./ChatTimeline.css";

export interface ChatTimelineProps {
  messages: ChatMessageData[];
}

export function ChatTimeline({ messages }: ChatTimelineProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (bottomRef.current && typeof bottomRef.current.scrollIntoView === "function") {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="chat-timeline" data-testid="chat-timeline">
        <div className="chat-timeline__empty">No messages yet. Start a conversation!</div>
      </div>
    );
  }

  return (
    <div className="chat-timeline" data-testid="chat-timeline">
      <div className="chat-timeline__messages">
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
