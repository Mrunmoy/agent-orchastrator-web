export type Provider = "claude" | "codex" | "ollama" | "gemini";
export type AgentRole = "worker" | "coordinator" | "moderator";
export type AgentStatusType = "idle" | "running" | "blocked" | "offline";

export interface AgentData {
  id: string;
  display_name: string;
  provider: Provider;
  model: string;
  role: AgentRole;
  status: AgentStatusType;
  personality_key?: string;
  sort_order: number;
}
