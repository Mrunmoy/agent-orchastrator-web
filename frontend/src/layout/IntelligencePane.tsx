import type { Artifact } from "../api/client";
import type { AgentData } from "../features/agents";
import "./IntelligencePane.css";

const PROVIDER_COLORS: Record<string, string> = {
  claude: "#c97a2e",
  codex: "#10a37f",
  ollama: "#0077b6",
  gemini: "#8e44ad",
};

const MAX_VISIBLE_AGENTS = 5;

type IntelligencePaneProps = {
  agreementSummary?: string;
  conflictSummary?: string;
  memoSummary?: string;
  agreementArtifact?: Artifact | null;
  conflictArtifact?: Artifact | null;
  memoArtifact?: Artifact | null;
  agents?: AgentData[];
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

/** Render payload content — bullet list for arrays, paragraph otherwise. */
function PayloadContent({
  payload,
  fallback,
  hasArtifact,
}: {
  payload: Record<string, unknown> | null;
  fallback: string;
  hasArtifact: boolean;
}) {
  if (!payload) {
    return <p className={hasArtifact ? "intel-card__content" : "intel-card__empty"}>{fallback}</p>;
  }

  // Check for items/points arrays
  const items = Array.isArray(payload.items)
    ? (payload.items as string[])
    : Array.isArray(payload.points)
      ? (payload.points as string[])
      : null;

  if (items && items.length > 0) {
    return (
      <ul className="intel-card__list">
        {items.map((item, i) => (
          <li key={i}>{String(item)}</li>
        ))}
      </ul>
    );
  }

  const text = renderPayloadSummary(payload) ?? fallback;
  return <p className={payload ? "intel-card__content" : "intel-card__empty"}>{text}</p>;
}

function AgentAvatar({ agent }: { agent: AgentData }) {
  const bgColor = PROVIDER_COLORS[agent.provider] ?? "#666";
  const letter = agent.display_name.charAt(0).toUpperCase();
  return (
    <span
      className="agent-avatar"
      style={{ backgroundColor: bgColor }}
      aria-label={`${agent.display_name} avatar`}
    >
      {letter}
    </span>
  );
}

export function IntelligencePane({
  agreementSummary = "No agreements recorded yet.",
  conflictSummary = "No conflicts recorded yet.",
  memoSummary = "No memo available.",
  agreementArtifact,
  conflictArtifact,
  memoArtifact,
  agents = [],
}: IntelligencePaneProps) {
  const agreementPayload = parsePayload(agreementArtifact);
  const conflictPayload = parsePayload(conflictArtifact);
  const memoPayload = parsePayload(memoArtifact);

  const agreementText = renderPayloadSummary(agreementPayload) ?? agreementSummary;
  const conflictText = renderPayloadSummary(conflictPayload) ?? conflictSummary;
  const memoText = renderPayloadSummary(memoPayload) ?? memoSummary;

  const artifactCount =
    (agreementArtifact ? 1 : 0) + (conflictArtifact ? 1 : 0) + (memoArtifact ? 1 : 0);

  const visibleAgents = agents.slice(0, MAX_VISIBLE_AGENTS);
  const overflowCount = agents.length - MAX_VISIBLE_AGENTS;

  return (
    <aside className="panel intel-pane" data-testid="intelligence-pane">
      <h3>Batch Intelligence</h3>
      <div className="intel-pane__scroll">
        {/* Quick Overview */}
        <div className="overview-card" data-testid="overview-card">
          <h4 className="section-header">Overview</h4>
          <div className="overview-card__stats">
            <span className="overview-stat">
              <strong>{agents.length}</strong> agent{agents.length !== 1 ? "s" : ""}
            </span>
            <span className="overview-stat">
              <strong>{artifactCount}</strong> artifact{artifactCount !== 1 ? "s" : ""}
            </span>
          </div>
        </div>

        {/* Active Agents */}
        <div className="active-agents-section" data-testid="active-agents-section">
          <h4 className="section-header">Active Agents</h4>
          {agents.length === 0 ? (
            <p className="intel-card__empty">No agents assigned.</p>
          ) : (
            <>
              <ul className="agent-list">
                {visibleAgents.map((agent) => (
                  <li key={agent.id} className="agent-list__item">
                    <AgentAvatar agent={agent} />
                    <div className="agent-list__info">
                      <span className="agent-list__name">{agent.display_name}</span>
                      <span className="agent-list__status">{agent.status}</span>
                    </div>
                  </li>
                ))}
              </ul>
              {overflowCount > 0 && (
                <p className="agent-list__overflow" data-testid="agents-overflow">
                  and {overflowCount} more
                </p>
              )}
            </>
          )}
        </div>

        {/* Batch Intelligence Cards */}
        <div data-testid="intelligence-section">
          <h4 className="section-header">Intelligence</h4>
          <div className="intel-card intel-card--ok" data-testid="agreement-section">
            <h4>Agreement Map</h4>
            <PayloadContent
              payload={agreementPayload}
              fallback={agreementText}
              hasArtifact={!!agreementPayload}
            />
          </div>
          <div className="intel-card intel-card--warn" data-testid="conflict-section">
            <h4>Conflict Map</h4>
            <PayloadContent
              payload={conflictPayload}
              fallback={conflictText}
              hasArtifact={!!conflictPayload}
            />
          </div>
          <div className="intel-card intel-card--memo" data-testid="memo-section">
            <h4>Neutral Memo</h4>
            <PayloadContent payload={memoPayload} fallback={memoText} hasArtifact={!!memoPayload} />
          </div>
        </div>
      </div>
    </aside>
  );
}
