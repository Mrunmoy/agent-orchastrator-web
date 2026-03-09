import React from "react";
import type { AgentData } from "./types";
import "./AgentCard.css";

interface AgentCardProps {
  agent: AgentData;
  onEdit: (agentId: string) => void;
}

const PROVIDER_COLORS: Record<string, string> = {
  claude: "#611f69",
  codex: "#2bac76",
  ollama: "#1264a3",
  gemini: "#ecb22e",
};

export const AgentCard: React.FC<AgentCardProps> = ({ agent, onEdit }) => {
  const statusLabel = agent.status.charAt(0).toUpperCase() + agent.status.slice(1);
  const personalityLabel = agent.personality_key
    ? agent.personality_key
        .split("_")
        .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
        .join(" ")
    : null;
  const displayOrder =
    agent.turn_order != null ? agent.turn_order : agent.sort_order + 1;

  const avatarLetter = agent.display_name.charAt(0).toUpperCase();
  const avatarColor = PROVIDER_COLORS[agent.provider] ?? "#888";

  return (
    <div
      className="agent-card"
      data-testid="agent-card"
      data-agent-testid={`agent-card-${agent.id}`}
    >
      <span
        className="order-badge"
        data-testid="order-badge"
        aria-label={`Position ${displayOrder}`}
      >
        {displayOrder}
      </span>

      <div className="agent-card-body">
        <div className="agent-card-avatar-wrapper">
          <div
            className={`agent-card-avatar provider-avatar-${agent.provider}`}
            data-testid="agent-avatar"
            style={{ backgroundColor: avatarColor }}
          >
            {avatarLetter}
          </div>
          <span
            className={`agent-card-status-dot status-dot-${agent.status}`}
            data-testid="status-indicator"
            title={statusLabel}
            aria-label={`Status: ${statusLabel}`}
          />
        </div>

        <div className="agent-card-info">
          <div className="agent-card-name-row">
            <span className="agent-card-name">{agent.display_name}</span>
            <span
              className="role-badge"
              data-testid="role-badge"
            >
              {agent.role}
            </span>
          </div>

          <span className="agent-card-model" data-testid="agent-model">
            {agent.model}
          </span>

          <div className="agent-card-meta">
            <span className={`provider-badge provider-${agent.provider}`}>{agent.provider}</span>
            {personalityLabel && (
              <span className="personality-badge" data-testid="personality-tag">
                {personalityLabel}
              </span>
            )}
          </div>
        </div>

        <div className="agent-card-actions">
          <button type="button" className="agent-card-edit-btn" onClick={() => onEdit(agent.id)}>
            Edit
          </button>
        </div>
      </div>
    </div>
  );
};
