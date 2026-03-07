import React from "react";
import type { AgentData } from "./types";
import { AgentCard } from "./AgentCard";
import "./AgentRoster.css";

interface AgentRosterProps {
  agents: AgentData[];
  onEdit: (agentId: string) => void;
  onAdd: () => void;
}

export const AgentRoster: React.FC<AgentRosterProps> = ({
  agents,
  onEdit,
  onAdd,
}) => {
  return (
    <div className="agent-roster" data-testid="agent-roster">
      <div className="agent-roster-header">
        <span className="agent-roster-title">Agents</span>
        <button type="button" className="agent-roster-add-btn" onClick={onAdd}>
          Add Agent
        </button>
      </div>
      {agents.length === 0 ? (
        <p className="agent-roster-empty">No agents configured</p>
      ) : (
        <div className="agent-roster-grid">
          {agents.map((agent) => (
            <AgentCard key={agent.id} agent={agent} onEdit={onEdit} />
          ))}
        </div>
      )}
    </div>
  );
};
