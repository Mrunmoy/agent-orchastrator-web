import React from "react";
import type { RunWindowProps } from "./types";
import { SteeringPanel } from "./SteeringPanel";
import "./RunWindow.css";

function formatElapsed(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${String(secs).padStart(2, "0")}`;
}

export function RunWindow({
  status,
  currentTurn,
  batchSize,
  elapsedSeconds,
  steeringHistory,
  onNext20,
  onContinue20,
  onStopNow,
  onSteer,
}: RunWindowProps) {
  const progressPercent = Math.min((currentTurn / batchSize) * 100, 100);

  function handleStopNow() {
    if (window.confirm("Are you sure you want to stop the current batch?")) {
      onStopNow();
    }
  }

  return (
    <div className="run-window" data-testid="run-window">
      <div className="run-window__info">
        <span className="run-window__status" data-testid="run-window-status">
          {status}
        </span>
        <span className="run-window__turn" data-testid="run-window-turn">
          Turn {currentTurn} of {batchSize}
        </span>
        <span className="run-window__elapsed" data-testid="run-window-elapsed">
          {formatElapsed(elapsedSeconds)}
        </span>
      </div>

      <div className="run-window__progress" data-testid="run-window-progress">
        <div
          className="run-window__progress-fill"
          data-testid="run-window-progress-fill"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      <div className="run-window__actions">
        {status === "paused" && (
          <>
            <button
              className="run-window__button run-window__button--next"
              data-testid="next-20-button"
              type="button"
              onClick={onNext20}
            >
              Next 20
            </button>
            <button
              className="run-window__button run-window__button--continue"
              data-testid="continue-20-button"
              type="button"
              onClick={onContinue20}
            >
              Continue 20
            </button>
          </>
        )}

        {(status === "running" || status === "queued") && (
          <button
            className="run-window__button run-window__button--stop"
            data-testid="stop-now-button"
            type="button"
            onClick={handleStopNow}
          >
            Stop Now
          </button>
        )}
      </div>

      <SteeringPanel status={status} steeringHistory={steeringHistory} onSteer={onSteer} />
    </div>
  );
}
