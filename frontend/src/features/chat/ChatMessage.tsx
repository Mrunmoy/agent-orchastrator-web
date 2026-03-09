import React from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { motion, useReducedMotion } from "framer-motion";
import type { ChatMessageData } from "./types";
import { agentColor } from "./agentColor";
import { fadeInUp } from "../../utils/animations";
import "./ChatMessage.css";

export interface ChatMessageProps {
  message: ChatMessageData;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const prefersReducedMotion = useReducedMotion();

  const {
    agentName,
    agentId,
    agentRole,
    text,
    timestamp,
    isUser,
    isThinking,
    type = "chat_message",
    round,
    totalRounds,
    phaseLabel,
  } = message;

  // Phase divider — full-width, no avatar/bubble
  if (type === "phase_change") {
    return (
      <div className="phase-divider" data-testid="phase-divider">
        <span className="phase-divider__label">{phaseLabel}</span>
      </div>
    );
  }

  // Determine variant CSS class
  const variantClass = (() => {
    if (type === "steer") return "chat-message--steer chat-message--user";
    if (type === "system_notice") return "chat-message--system";
    if (type === "debate_turn") return "chat-message--debate";
    if (isUser) return "chat-message--user";
    return "chat-message--agent";
  })();

  // Display name: steer messages always show "You"
  const displayName = type === "steer" ? "You" : agentName;

  // Avatar background: hash-based for agents, default for user
  const avatarStyle = !isUser && agentId ? { backgroundColor: agentColor(agentId) } : undefined;

  return (
    <motion.div
      className={`chat-message ${variantClass}`}
      data-testid="chat-message"
      {...(prefersReducedMotion ? {} : fadeInUp)}
    >
      <div className="chat-avatar" data-testid="chat-avatar" style={avatarStyle}>
        {displayName.charAt(0).toUpperCase()}
      </div>
      <div className="chat-bubble" data-testid="chat-bubble">
        <div className="chat-bubble__header">
          <span className="chat-bubble__name">{displayName}</span>
          {agentRole && (
            <span className="chat-bubble__role" data-testid="role-badge">
              {agentRole}
            </span>
          )}
          {type === "debate_turn" && round != null && totalRounds != null && (
            <span className="chat-bubble__round" data-testid="round-badge">
              Round {round}/{totalRounds}
            </span>
          )}
          <span className="chat-bubble__time">{new Date(timestamp).toLocaleTimeString()}</span>
        </div>
        {isThinking ? (
          <div className="thinking-indicator" data-testid="thinking-indicator">
            <span className="thinking-indicator__dot" />
            <span className="thinking-indicator__dot" />
            <span className="thinking-indicator__dot" />
          </div>
        ) : (
          <div className="chat-bubble__text">
            <Markdown remarkPlugins={[remarkGfm]}>{text}</Markdown>
          </div>
        )}
      </div>
    </motion.div>
  );
}
