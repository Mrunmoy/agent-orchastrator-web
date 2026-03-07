import React, { useRef, useState } from "react";
import type { AgentData } from "./types";
import { AgentCard } from "./AgentCard";
import { reorderAgent as defaultReorderAgent } from "../../api/client";
import "./AgentRoster.css";

interface AgentRosterProps {
  agents: AgentData[];
  onEdit: (agentId: string) => void;
  onAdd: () => void;
  reorderAgent?: (agentId: string, sortOrder: number) => Promise<unknown>;
  reorderConversationAgents?: (agentIds: string[]) => Promise<unknown>;
}

function orderKey(a: AgentData): number {
  return a.turn_order != null ? a.turn_order : a.sort_order;
}

function sortByOrder(agents: AgentData[]): AgentData[] {
  return [...agents].sort((a, b) => orderKey(a) - orderKey(b));
}

export const AgentRoster: React.FC<AgentRosterProps> = ({
  agents,
  onEdit,
  onAdd,
  reorderAgent = defaultReorderAgent,
  reorderConversationAgents,
}) => {
  const [localAgents, setLocalAgents] = useState<AgentData[]>(() => sortByOrder(agents));
  const prevAgentsRef = useRef(agents);
  const dragId = useRef<string | null>(null);

  if (prevAgentsRef.current !== agents) {
    prevAgentsRef.current = agents;
    setLocalAgents(sortByOrder(agents));
  }

  const handleDragStart = (_e: React.DragEvent, agentId: string) => {
    dragId.current = agentId;
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (_e: React.DragEvent, targetId: string) => {
    if (!dragId.current || dragId.current === targetId) return;
    const reordered = [...localAgents];
    const fromIdx = reordered.findIndex((a) => a.id === dragId.current);
    const toIdx = reordered.findIndex((a) => a.id === targetId);
    if (fromIdx < 0 || toIdx < 0) {
      dragId.current = null;
      return;
    }
    const [moved] = reordered.splice(fromIdx, 1);
    reordered.splice(toIdx, 0, moved);
    const withOrder = reordered.map((a, i) => ({
      ...a,
      sort_order: i,
      ...(a.turn_order != null ? { turn_order: i + 1 } : {}),
    }));
    setLocalAgents(withOrder);
    if (reorderConversationAgents) {
      reorderConversationAgents(withOrder.map((a) => a.id)).catch(console.error);
    } else {
      for (const a of withOrder) {
        reorderAgent(a.id, a.sort_order).catch(console.error);
      }
    }
    dragId.current = null;
  };

  return (
    <div className="agent-roster" data-testid="agent-roster">
      <div className="agent-roster-header">
        <span className="agent-roster-title">Agents</span>
        <button type="button" className="agent-roster-add-btn" onClick={onAdd}>
          Add Agent
        </button>
      </div>
      {localAgents.length === 0 ? (
        <p className="agent-roster-empty">No agents configured</p>
      ) : (
        <div className="agent-roster-grid">
          {localAgents.map((agent) => (
            <div
              key={agent.id}
              data-testid="agent-roster-item"
              className="agent-roster-item"
              draggable
              onDragStart={(e) => handleDragStart(e, agent.id)}
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, agent.id)}
            >
              <span className="drag-handle" aria-hidden="true">
                ⠿
              </span>
              <AgentCard agent={agent} onEdit={onEdit} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
