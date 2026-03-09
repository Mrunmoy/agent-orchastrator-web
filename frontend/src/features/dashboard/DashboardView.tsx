import { useCallback, useEffect, useState } from "react";
import type { AgentData } from "../agents";
import type { Task } from "../../api/client";
import { fetchTasks } from "../../api/client";
import { StatsCard } from "./StatsCard";
import "./DashboardView.css";

type DashboardViewProps = {
  conversationId: string | null;
  agents: AgentData[];
};

export function DashboardView({ conversationId, agents }: DashboardViewProps) {
  const [tasks, setTasks] = useState<Task[]>([]);

  const loadTasks = useCallback(async (convId: string) => {
    try {
      const fetched = await fetchTasks(convId);
      setTasks(fetched);
    } catch {
      setTasks([]);
    }
  }, []);

  useEffect(() => {
    if (conversationId) {
      void loadTasks(conversationId);
    } else {
      setTasks([]);
    }
  }, [conversationId, loadTasks]);

  const activeAgents = agents.filter((a) => a.status !== "offline").length;
  const runningTasks = tasks.filter(
    (t) => t.status === "implementing" || t.status === "in_progress",
  ).length;
  const completedTasks = tasks.filter((t) => t.status === "done").length;
  const totalTasks = tasks.length;

  return (
    <div className="dashboard-view" data-testid="dashboard-view">
      <div className="dashboard-view__stats-row" data-testid="stats-row">
        <StatsCard label="Active Agents" value={activeAgents} color="#4a9eff" />
        <StatsCard label="Running Tasks" value={runningTasks} color="#22c55e" />
        <StatsCard label="Completed Tasks" value={completedTasks} color="#a78bfa" />
        <StatsCard label="Total Tasks" value={totalTasks} color="#f59e0b" />
      </div>

      <h3 className="dashboard-view__section-title">Agents</h3>

      {agents.length === 0 ? (
        <div className="dashboard-view__empty" data-testid="dashboard-empty">
          No agents configured. Add agents from the sidebar.
        </div>
      ) : (
        <div className="dashboard-view__agent-grid" data-testid="agent-grid">
          {agents.map((agent) => (
            <div
              key={agent.id}
              className="dashboard-view__agent-card"
              data-testid={`agent-card-${agent.id}`}
            >
              <div
                className={`dashboard-view__agent-avatar dashboard-view__agent-avatar--${agent.provider}`}
              >
                {agent.display_name.charAt(0).toUpperCase()}
              </div>
              <div className="dashboard-view__agent-info">
                <div className="dashboard-view__agent-name">{agent.display_name}</div>
                <div className="dashboard-view__agent-meta">
                  <span>{agent.model}</span>
                  <span>{agent.role}</span>
                </div>
              </div>
              <span
                className={`dashboard-view__agent-status dashboard-view__agent-status--${agent.status}`}
              >
                {agent.status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
