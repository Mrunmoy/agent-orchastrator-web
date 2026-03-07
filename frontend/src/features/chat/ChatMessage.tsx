import React from "react";
import type { ChatMessageData } from "./types";
import "./ChatMessage.css";

export interface ChatMessageProps {
  message: ChatMessageData;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const { agentName, text, timestamp, isUser, isThinking } = message;
  const variant = isUser ? "chat-message--user" : "chat-message--agent";

  return (
    <div className={`chat-message ${variant}`} data-testid="chat-message">
      <div className="chat-avatar" data-testid="chat-avatar">
        {agentName.charAt(0).toUpperCase()}
      </div>
      <div className="chat-bubble">
        <div className="chat-bubble__header">
          <span className="chat-bubble__name">{agentName}</span>
          <span className="chat-bubble__time">
            {new Date(timestamp).toLocaleTimeString()}
          </span>
        </div>
        {isThinking ? (
          <div className="thinking-indicator" data-testid="thinking-indicator">
            <span className="thinking-indicator__dot" />
            <span className="thinking-indicator__dot" />
            <span className="thinking-indicator__dot" />
          </div>
        ) : (
          <div className="chat-bubble__text">{text}</div>
        )}
      </div>
    </div>
  );
}
