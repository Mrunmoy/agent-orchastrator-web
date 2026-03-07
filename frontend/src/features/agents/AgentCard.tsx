import React from "react";
import type { AgentData } from "./types";
import "./AgentCard.css";

interface AgentCardProps {
  agent: AgentData;
  onEdit: (agentId: string) => void;
}

export const AgentCard: React.FC<AgentCardProps> = ({ agent, onEdit }) => {
  return (
    <div className="agent-card" data-testid="agent-card">
      <div className="agent-card-header">
        <span
          className={`status-indicator status-${agent.status}`}
          data-testid="status-indicator"
        />
        <span className="agent-card-name">{agent.display_name}</span>
      </div>
      <div className="agent-card-meta">
        <span className={`provider-badge provider-${agent.provider}`}>
          {agent.provider}
        </span>
        <span className="role-badge">{agent.role}</span>
      </div>
      <span className="agent-card-model">{agent.model}</span>
      <div className="agent-card-footer">
        <button
          className="agent-card-edit-btn"
          onClick={() => onEdit(agent.id)}
        >
          Edit
        </button>
      </div>
    </div>
  );
};
