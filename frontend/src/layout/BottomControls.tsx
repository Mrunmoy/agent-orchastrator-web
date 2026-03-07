import { useState } from "react";
import "./BottomControls.css";

type BottomControlsProps = {
  onContinueBatch?: (steeringNote: string, preferenceNote: string) => void;
  onMarkGateReady?: () => void;
};

export function BottomControls({ onContinueBatch, onMarkGateReady }: BottomControlsProps) {
  const [steeringNote, setSteeringNote] = useState("");
  const [preferenceNote, setPreferenceNote] = useState("");

  return (
    <section className="bottom-controls" data-testid="bottom-controls">
      <div className="bottom-controls__field">
        <label htmlFor="steering-note">Steering Note</label>
        <textarea
          id="steering-note"
          rows={2}
          value={steeringNote}
          onChange={(event) => setSteeringNote(event.target.value)}
        />
      </div>
      <div className="bottom-controls__field">
        <label htmlFor="preference-note">Preference Note</label>
        <textarea
          id="preference-note"
          rows={2}
          value={preferenceNote}
          onChange={(event) => setPreferenceNote(event.target.value)}
        />
      </div>
      <button
        className="btn btn--ok"
        onClick={() => onContinueBatch?.(steeringNote, preferenceNote)}
      >
        Continue Batch (20) With Notes
      </button>
      <button className="btn btn--subtle" onClick={onMarkGateReady}>
        Mark Gate Ready For My Review
      </button>
    </section>
  );
}
