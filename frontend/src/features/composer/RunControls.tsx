import React, { useState } from "react";
import type { RunControlsProps } from "./types";
import "./RunControls.css";

export function RunControls({ status, onRun, onContinue, onStop, onSteer }: RunControlsProps) {
  const [steerNote, setSteerNote] = useState("");

  const showSteering = status === "running" || status === "paused";

  function handleSteer() {
    const trimmed = steerNote.trim();
    if (!trimmed) return;
    onSteer(trimmed);
    setSteerNote("");
  }

  return (
    <div className="run-controls" data-testid="run-controls">
      <div className="run-controls__status" data-testid="run-status">
        {status}
      </div>

      <div className="run-controls__buttons">
        {status === "idle" && (
          <button
            className="run-controls__button run-controls__button--run"
            data-testid="run-button"
            onClick={onRun}
            type="button"
          >
            Run
          </button>
        )}

        {status === "paused" && (
          <button
            className="run-controls__button run-controls__button--continue"
            data-testid="continue-button"
            onClick={onContinue}
            type="button"
          >
            Continue
          </button>
        )}

        {(status === "running" || status === "queued") && (
          <button
            className="run-controls__button run-controls__button--stop"
            data-testid="stop-button"
            onClick={onStop}
            type="button"
          >
            Stop
          </button>
        )}
      </div>

      {showSteering && (
        <div className="run-controls__steering">
          <input
            className="run-controls__steer-input"
            data-testid="steer-input"
            type="text"
            placeholder="Steering note..."
            value={steerNote}
            onChange={(e) => setSteerNote(e.target.value)}
          />
          <button
            className="run-controls__steer-button"
            data-testid="steer-button"
            onClick={handleSteer}
            type="button"
          >
            Inject
          </button>
        </div>
      )}
    </div>
  );
}
