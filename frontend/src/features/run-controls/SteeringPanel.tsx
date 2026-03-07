import React, { useState } from "react";
import type { SteeringPanelProps } from "./types";
import "./SteeringPanel.css";

export function SteeringPanel({ status, steeringHistory, onSteer }: SteeringPanelProps) {
  const [note, setNote] = useState("");

  if (status === "idle") {
    return null;
  }

  function handleSubmit() {
    const trimmed = note.trim();
    if (!trimmed) return;
    onSteer(trimmed);
    setNote("");
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  return (
    <div className="steering-panel" data-testid="steering-panel">
      <div className="steering-panel__input-row">
        <textarea
          className="steering-panel__textarea"
          data-testid="steering-textarea"
          placeholder="Enter steering note..."
          value={note}
          onChange={(e) => setNote(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={2}
        />
        <button
          className="steering-panel__submit"
          data-testid="steering-submit"
          type="button"
          onClick={handleSubmit}
        >
          Inject
        </button>
      </div>

      {steeringHistory.length > 0 && (
        <ul className="steering-panel__history" data-testid="steering-history">
          {steeringHistory.map((entry) => (
            <li
              key={entry.id}
              className="steering-panel__history-item"
              data-testid="steering-history-item"
            >
              {entry.text}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
