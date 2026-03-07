import React, { useState } from "react";
import type { ComposerProps } from "./types";
import "./Composer.css";

export function Composer({ agents, onSend, disabled = false }: ComposerProps) {
  const [message, setMessage] = useState("");
  const [targetAgentId, setTargetAgentId] = useState<string>("");

  function handleSend() {
    const trimmed = message.trim();
    if (!trimmed) return;
    onSend(trimmed, targetAgentId || null);
    setMessage("");
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="composer" data-testid="composer">
      <div className="composer__controls">
        <select
          className="composer__agent-selector"
          data-testid="agent-selector"
          value={targetAgentId}
          onChange={(e) => setTargetAgentId(e.target.value)}
          disabled={disabled}
        >
          <option value="">All agents</option>
          {agents.map((agent) => (
            <option key={agent.id} value={agent.id}>
              {agent.display_name}
            </option>
          ))}
        </select>
      </div>
      <div className="composer__input-row">
        <textarea
          className="composer__input"
          data-testid="composer-input"
          placeholder="Type a message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          rows={2}
        />
        <button
          className="composer__send-button"
          data-testid="send-button"
          onClick={handleSend}
          disabled={disabled}
          type="button"
        >
          Send
        </button>
      </div>
    </div>
  );
}
