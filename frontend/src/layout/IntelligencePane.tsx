import type { Artifact } from "../api/client";
import "./IntelligencePane.css";

type IntelligencePaneProps = {
  agreementSummary?: string;
  conflictSummary?: string;
  memoSummary?: string;
  agreementArtifact?: Artifact | null;
  conflictArtifact?: Artifact | null;
  memoArtifact?: Artifact | null;
};

/** Safely parse an artifact's payload_json. */
function parsePayload(artifact: Artifact | null | undefined): Record<string, unknown> | null {
  if (!artifact) return null;
  try {
    return JSON.parse(artifact.payload_json) as Record<string, unknown>;
  } catch {
    return null;
  }
}

/** Render a parsed payload as a readable summary. */
function renderPayloadSummary(payload: Record<string, unknown> | null): string | null {
  if (!payload) return null;

  // Common field: "summary"
  if (typeof payload.summary === "string" && payload.summary.trim()) {
    return payload.summary;
  }

  // Common field: "text"
  if (typeof payload.text === "string" && payload.text.trim()) {
    return payload.text;
  }

  // Fallback: stringify the top-level keys
  const keys = Object.keys(payload);
  if (keys.length === 0) return null;
  return JSON.stringify(payload, null, 2);
}

export function IntelligencePane({
  agreementSummary = "No agreements recorded yet.",
  conflictSummary = "No conflicts recorded yet.",
  memoSummary = "No memo available.",
  agreementArtifact,
  conflictArtifact,
  memoArtifact,
}: IntelligencePaneProps) {
  const agreementPayload = parsePayload(agreementArtifact);
  const conflictPayload = parsePayload(conflictArtifact);
  const memoPayload = parsePayload(memoArtifact);

  const agreementText = renderPayloadSummary(agreementPayload) ?? agreementSummary;
  const conflictText = renderPayloadSummary(conflictPayload) ?? conflictSummary;
  const memoText = renderPayloadSummary(memoPayload) ?? memoSummary;

  return (
    <aside className="panel intel-pane" data-testid="intelligence-pane">
      <h3>Batch Intelligence</h3>
      <div className="intel-pane__scroll">
        <div className="intel-card intel-card--ok" data-testid="agreement-section">
          <h4>Agreement Map</h4>
          <p className={agreementPayload ? "intel-card__content" : "intel-card__empty"}>
            {agreementText}
          </p>
        </div>
        <div className="intel-card intel-card--warn" data-testid="conflict-section">
          <h4>Conflict Map</h4>
          <p className={conflictPayload ? "intel-card__content" : "intel-card__empty"}>
            {conflictText}
          </p>
        </div>
        <div className="intel-card intel-card--memo" data-testid="memo-section">
          <h4>Neutral Memo</h4>
          <p className={memoPayload ? "intel-card__content" : "intel-card__empty"}>
            {memoText}
          </p>
        </div>
      </div>
    </aside>
  );
}
