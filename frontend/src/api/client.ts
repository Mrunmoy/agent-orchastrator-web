export type ApiEnvelope<T> = {
  ok: boolean;
  data: T;
  error?: string;
};

export type Conversation = {
  id: string;
  title: string;
  project_path: string;
  active: number;
  updated_at: string;
};

export type Agent = {
  id: string;
  display_name: string;
  provider: "claude" | "codex" | "ollama" | "gemini";
  model: string;
  role: "worker" | "coordinator" | "moderator";
  status: "idle" | "running" | "blocked" | "offline";
  personality_key?: string | null;
  sort_order: number;
  turn_order?: number;
};

const API_BASE = import.meta.env.VITE_API_BASE_URL?.toString().replace(/\/$/, "") ?? "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    let errorMessage = `Request failed: ${response.status}`;
    try {
      const errorBody = (await response.json()) as Partial<ApiEnvelope<T>>;
      if (typeof errorBody.error === "string" && errorBody.error.trim().length > 0) {
        errorMessage = errorBody.error;
      }
    } catch {
      // Non-JSON error body; keep status-based message.
    }
    throw new Error(errorMessage);
  }

  const body = (await response.json()) as ApiEnvelope<T>;
  if (!body.ok) {
    throw new Error(body.error ?? "Request failed");
  }
  return body.data;
}

export async function listConversations(): Promise<Conversation[]> {
  const data = await request<{ conversations: Conversation[] }>("/conversations");
  return data.conversations;
}

export async function createConversation(
  title: string,
  projectPath: string,
): Promise<Conversation> {
  const data = await request<{ conversation: Conversation }>("/conversations/new", {
    method: "POST",
    body: JSON.stringify({ title, project_path: projectPath }),
  });
  return data.conversation;
}

export async function selectConversation(conversationId: string): Promise<Conversation> {
  const data = await request<{ conversation: Conversation }>("/conversations/select", {
    method: "POST",
    body: JSON.stringify({ conversation_id: conversationId }),
  });
  return data.conversation;
}

export async function deleteConversation(conversationId: string): Promise<void> {
  await request<{ conversation: Conversation }>("/conversations/delete", {
    method: "POST",
    body: JSON.stringify({ conversation_id: conversationId }),
  });
}

export async function clearConversations(): Promise<void> {
  await request<{ deleted_count: number }>("/conversations/clear-all", { method: "POST" });
}

export async function listAgents(): Promise<Agent[]> {
  const data = await request<{ agents: Agent[] }>("/agents");
  return data.agents;
}

export async function listConversationAgents(conversationId: string): Promise<Agent[]> {
  const data = await request<{ agents: Agent[] }>(`/conversations/${conversationId}/agents`);
  return data.agents;
}

export async function createAgent(body: {
  display_name: string;
  provider: Agent["provider"];
  model: string;
  role: Agent["role"];
  personality_key?: string;
  conversation_id?: string;
}): Promise<Agent> {
  const data = await request<{ agent: Agent }>("/agents", {
    method: "POST",
    body: JSON.stringify(body),
  });
  return data.agent;
}

export async function updateAgent(body: {
  agent_id: string;
  display_name?: string;
  provider?: Agent["provider"];
  model?: string;
  role?: Agent["role"];
  personality_key?: string;
}): Promise<Agent> {
  const data = await request<{ agent: Agent }>("/agents/update", {
    method: "POST",
    body: JSON.stringify(body),
  });
  return data.agent;
}

export async function deleteAgent(agentId: string): Promise<void> {
  await request<{ deleted_id: string }>("/agents/delete", {
    method: "POST",
    body: JSON.stringify({ agent_id: agentId }),
  });
}

export async function reorderAgent(agentId: string, sortOrder: number): Promise<Agent> {
  const data = await request<{ agent: Agent }>(`/agents/${agentId}/order`, {
    method: "PATCH",
    body: JSON.stringify({ sort_order: sortOrder }),
  });
  return data.agent;
}

export async function removeAgentFromConversation(
  conversationId: string,
  agentId: string,
): Promise<void> {
  await request<Record<string, unknown>>(
    `/conversations/${conversationId}/agents/${agentId}`,
    { method: "DELETE" },
  );
}

export async function reorderConversationAgents(
  conversationId: string,
  agentIds: string[],
): Promise<void> {
  await request<Record<string, unknown>>(`/conversations/${conversationId}/agents/reorder`, {
    method: "PATCH",
    body: JSON.stringify({ agent_ids: agentIds }),
  });
}

/** Raw event shape returned by the backend JSONL event log. */
export type BackendEvent = {
  event_id: string;
  conversation_id: string;
  source_type: string;
  source_id?: string;
  text: string;
  event_type: string;
  metadata_json?: string;
  timestamp?: string;
  created_at?: string;
};

/**
 * Fetch events for a conversation.
 * When `since` is provided, only returns events after that event_id.
 */
export async function fetchEvents(
  conversationId: string,
  since?: string,
): Promise<BackendEvent[]> {
  const params = new URLSearchParams({ conversation_id: conversationId });
  if (since) {
    params.set("since", since);
  }
  const data = await request<{ events: BackendEvent[] }>(`/events?${params.toString()}`);
  return data.events;
}

/**
 * Fetch the latest N events for a conversation.
 */
export async function fetchLatestEvents(
  conversationId: string,
  n = 10,
): Promise<BackendEvent[]> {
  const params = new URLSearchParams({
    conversation_id: conversationId,
    n: String(n),
  });
  const data = await request<{ events: BackendEvent[] }>(`/events/latest?${params.toString()}`);
  return data.events;
}

export async function runBatch(conversationId: string, batchSize = 20): Promise<void> {
  await request<{ run: unknown }>(`/orchestration/${conversationId}/run`, {
    method: "POST",
    body: JSON.stringify({ batch_size: batchSize }),
  });
}

export async function continueBatch(conversationId: string): Promise<void> {
  await request<{ run: unknown }>(`/orchestration/${conversationId}/continue`, { method: "POST" });
}

export async function stopBatch(conversationId: string): Promise<void> {
  await request<{ run: unknown }>(`/orchestration/${conversationId}/stop`, { method: "POST" });
}

export async function steerConversation(conversationId: string, note: string): Promise<void> {
  await request<{ event: unknown }>(`/orchestration/${conversationId}/steer`, {
    method: "POST",
    body: JSON.stringify({ note }),
  });
}
