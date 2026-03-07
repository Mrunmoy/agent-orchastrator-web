import React, { useState } from "react";
import type { ComposerProps } from "./types";
import "./Composer.css";

export function Composer({
  onSend,
  disabled = false,
}: Omit<ComposerProps, "agents"> & { agents?: ComposerProps["agents"] }) {
  const [message, setMessage] = useState("");

  function handleSend() {
    const trimmed = message.trim();
    if (!trimmed) return;
    onSend(trimmed);
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
