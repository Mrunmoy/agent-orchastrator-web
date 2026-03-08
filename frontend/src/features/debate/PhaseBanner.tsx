import type { PhaseBannerProps } from "./types";
import "./PhaseBanner.css";

export function PhaseBanner({
  phase,
  round,
  totalRounds,
  speakingAgent = null,
}: PhaseBannerProps) {
  return (
    <div className="phase-banner" data-testid="phase-banner">
      <span className="phase-banner__phase" data-testid="phase-name">
        {phase}
      </span>
      <span className="phase-banner__separator" aria-hidden="true">
        —
      </span>
      <span className="phase-banner__round" data-testid="round-counter">
        Round {round}/{totalRounds}
      </span>

      {speakingAgent && (
        <span
          className="phase-banner__speaking"
          data-testid="speaking-indicator"
          aria-live="polite"
          aria-atomic="true"
        >
          {speakingAgent}
          <span
            className="phase-banner__speaking-dots"
            aria-label={`${speakingAgent} is generating`}
          >
            <span className="phase-banner__speaking-dot" />
            <span className="phase-banner__speaking-dot" />
            <span className="phase-banner__speaking-dot" />
          </span>
        </span>
      )}
    </div>
  );
}
