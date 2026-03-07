import { useEffect, useMemo, useState } from "react";
import personalitiesJson from "../config/personalities.json";
import type { AgentData, AgentRole, Provider } from "../features/agents";
import {
  clearConversations as clearConversationsApi,
  createAgent as createAgentApi,
  createConversation as createConversationApi,
  deleteAgent as deleteAgentApi,
  deleteConversation as deleteConversationApi,
  listAgents,
  listConversationAgents,
  listConversations,
  removeAgentFromConversation as removeAgentFromConversationApi,
  reorderConversationAgents as reorderConversationAgentsApi,
  runBatch,
  selectConversation as selectConversationApi,
  steerConversation,
  stopBatch,
  continueBatch as continueBatchApi,
  updateAgent as updateAgentApi,
} from "../api/client";
import "./AppShell.css";
import { TopBar } from "./TopBar";
import { ConversationSummary, HistoryPane } from "./HistoryPane";
import { ChatMessage, ChatPane } from "./ChatPane";
import { IntelligencePane } from "./IntelligencePane";
import { BottomControls } from "./BottomControls";

const WORKING_DIR_KEY = "ao_working_dir";
const DEFAULT_WORKING_DIR = "/home/user/workspace";

const PROVIDER_MODELS: Record<Provider, string[]> = {
  claude: [
    "claude-opus-4-5",
    "claude-3-7-sonnet-20250219",
    "claude-3-5-sonnet-latest",
    "claude-3-5-haiku-latest",
  ],
  codex: ["codex-mini-latest", "gpt-4.1", "gpt-4.1-mini", "o4-mini"],
  ollama: ["llama3.2", "llama3.1", "mistral", "codellama", "phi3"],
  gemini: ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
};

const PERSONALITY_OPTIONS: { key: string; label: string }[] = [
  { key: "", label: "— none —" },
  ...Object.entries(personalitiesJson).map(([key, val]) => ({ key, label: val.label })),
];

type AgentEditorState = {
  mode: "create" | "edit";
  agentId?: string;
  displayName: string;
  provider: Provider;
  model: string;
  role: AgentRole;
  personality_key: string;
};

type ConversationCreatorState = {
  title: string;
  workingDirectory: string;
};

function getWorkingDirectory(): string {
  try {
    return window.localStorage.getItem(WORKING_DIR_KEY) ?? DEFAULT_WORKING_DIR;
  } catch {
    return DEFAULT_WORKING_DIR;
  }
}

function generateDefaultTitle(count: number): string {
  return `Conversation ${count + 1}`;
}

function toConversationSummary(row: {
  id: string;
  title: string;
  updated_at: string;
}): ConversationSummary {
  return { id: row.id, title: row.title, updatedAt: row.updated_at };
}

function toAgentData(row: {
  id: string;
  display_name: string;
  provider: Provider;
  model: string;
  role: AgentRole;
  status: "idle" | "running" | "blocked" | "offline";
  personality_key?: string | null;
  sort_order?: number;
  turn_order?: number;
}): AgentData {
  return {
    id: row.id,
    display_name: row.display_name,
    provider: row.provider,
    model: row.model,
    role: row.role,
    status: row.status,
    personality_key: row.personality_key ?? undefined,
    sort_order: row.sort_order ?? 0,
    turn_order: row.turn_order,
  };
}

export function AppShell() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);
  const [messagesByConversation, setMessagesByConversation] = useState<
    Record<string, ChatMessage[]>
  >({});
  const [agents, setAgents] = useState<AgentData[]>([]);
  const [agentEditor, setAgentEditor] = useState<AgentEditorState | null>(null);
  const [isSavingAgent, setIsSavingAgent] = useState(false);
  const [conversationCreator, setConversationCreator] = useState<ConversationCreatorState | null>(
    null,
  );
  const [isCreatingConversation, setIsCreatingConversation] = useState(false);
  const [runStatus, setRunStatus] = useState("Idle");
  const [gateStatus, setGateStatus] = useState("Open");
  const [memoSummary, setMemoSummary] = useState("No memo available.");
  const [errorText, setErrorText] = useState<string | null>(null);

  const selectedConversation = useMemo(
    () => conversations.find((c) => c.id === selectedConversationId) ?? null,
    [conversations, selectedConversationId],
  );
  const selectedMessages = selectedConversationId
    ? (messagesByConversation[selectedConversationId] ?? [])
    : [];

  useEffect(() => {
    const load = async () => {
      try {
        const conversationRows = await listConversations();
        const nextConversations = conversationRows.map(toConversationSummary);
        setConversations(nextConversations);
        const activeId =
          conversationRows.find((conversation) => conversation.active === 1)?.id ??
          nextConversations[0]?.id ??
          null;
        setSelectedConversationId(activeId);
      } catch (error) {
        setErrorText(error instanceof Error ? error.message : "Failed to load initial data");
      }
    };
    void load();
  }, []);

  useEffect(() => {
    const loadAgents = async () => {
      try {
        if (selectedConversationId) {
          const agentRows = await listConversationAgents(selectedConversationId);
          setAgents(agentRows.map(toAgentData));
        } else {
          setAgents([]);
        }
      } catch {
        // Fallback to global agents if conversation-scoped endpoint fails
        try {
          const agentRows = await listAgents();
          setAgents(agentRows.map(toAgentData));
        } catch (error) {
          setErrorText(error instanceof Error ? error.message : "Failed to load agents");
        }
      }
    };
    void loadAgents();
  }, [selectedConversationId]);

  const createConversation = async (
    title: string,
    workingDirectory: string,
  ): Promise<string | null> => {
    try {
      const created = await createConversationApi(title, workingDirectory);
      const selected = await selectConversationApi(created.id);
      const selectedId = selected.id;
      setConversations((prev) => [
        toConversationSummary({
          id: created.id,
          title: created.title,
          updated_at: created.updated_at,
        }),
        ...prev,
      ]);
      setSelectedConversationId(selectedId);
      setConversationCreator(null);
      setErrorText(null);
      return selectedId;
    } catch (error) {
      setErrorText(error instanceof Error ? error.message : "Failed to create conversation");
      return null;
    }
  };

  const openConversationCreator = () => {
    setConversationCreator({
      title: generateDefaultTitle(conversations.length),
      workingDirectory: getWorkingDirectory(),
    });
  };

  const submitConversationCreator = async () => {
    if (!conversationCreator || isCreatingConversation) return;
    const title = conversationCreator.title.trim();
    const workingDirectory = conversationCreator.workingDirectory.trim();
    if (!title) {
      setErrorText("Conversation title is required.");
      return;
    }
    if (!workingDirectory) {
      setErrorText("Working directory is required.");
      return;
    }
    setIsCreatingConversation(true);
    try {
      await createConversation(title, workingDirectory);
    } finally {
      setIsCreatingConversation(false);
    }
  };

  const selectConversation = async (conversationId: string) => {
    try {
      await selectConversationApi(conversationId);
      setSelectedConversationId(conversationId);
      setConversations((prev) => {
        const now = new Date().toISOString();
        return prev
          .map((conversation) =>
            conversation.id === conversationId ? { ...conversation, updatedAt: now } : conversation,
          )
          .sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));
      });
      setErrorText(null);
    } catch (error) {
      setErrorText(error instanceof Error ? error.message : "Failed to select conversation");
    }
  };

  const deleteConversation = async () => {
    if (!selectedConversationId) return;
    try {
      await deleteConversationApi(selectedConversationId);
      let fallbackId: string | null = null;
      setConversations((prev) => {
        const next = prev.filter((conversation) => conversation.id !== selectedConversationId);
        fallbackId = next[0]?.id ?? null;
        return next;
      });
      setMessagesByConversation((prev) => {
        const next = { ...prev };
        delete next[selectedConversationId];
        return next;
      });
      setSelectedConversationId(fallbackId);
      if (fallbackId) {
        await selectConversationApi(fallbackId);
      }
      setErrorText(null);
    } catch (error) {
      setErrorText(error instanceof Error ? error.message : "Failed to delete conversation");
    }
  };

  const clearAllConversations = async () => {
    try {
      await clearConversationsApi();
      setConversations([]);
      setMessagesByConversation({});
      setSelectedConversationId(null);
      setRunStatus("Idle");
      setGateStatus("Open");
      setMemoSummary("No memo available.");
      setErrorText(null);
    } catch (error) {
      setErrorText(error instanceof Error ? error.message : "Failed to clear conversations");
    }
  };

  const ensureConversation = async (): Promise<string | null> => {
    if (selectedConversationId) {
      return selectedConversationId;
    }
    return createConversation(generateDefaultTitle(conversations.length), getWorkingDirectory());
  };

  const appendLocalMessage = (conversationId: string, sender: string, text: string) => {
    const now = new Date().toISOString();
    const newMessage: ChatMessage = {
      id: `${conversationId}-${Date.now()}`,
      sender,
      text,
      timestamp: now,
    };
    setMessagesByConversation((prev) => ({
      ...prev,
      [conversationId]: [...(prev[conversationId] ?? []), newMessage],
    }));
    setConversations((prev) =>
      prev
        .map((conversation) =>
          conversation.id === conversationId ? { ...conversation, updatedAt: now } : conversation,
        )
        .sort((a, b) => b.updatedAt.localeCompare(a.updatedAt)),
    );
  };

  const sendMessage = async (text: string, target: string) => {
    const conversationId = await ensureConversation();
    if (!conversationId) return;
    try {
      await steerConversation(conversationId, text);
      appendLocalMessage(
        conversationId,
        target === "all" ? "You -> Group" : `You -> ${target}`,
        text,
      );
      setMemoSummary("Latest direction sent to orchestrator.");
      setErrorText(null);
    } catch (error) {
      setErrorText(error instanceof Error ? error.message : "Failed to send message");
    }
  };

  const runNewBatch = async () => {
    const conversationId = await ensureConversation();
    if (!conversationId) return;
    try {
      await runBatch(conversationId, 20);
      setRunStatus("Running");
      setGateStatus("Open");
      setMemoSummary("Batch queued (20 turns).");
      setErrorText(null);
    } catch (error) {
      setErrorText(error instanceof Error ? error.message : "Failed to start batch");
    }
  };

  const stopRun = async () => {
    if (!selectedConversationId) return;
    try {
      await stopBatch(selectedConversationId);
      setRunStatus("Idle");
      setMemoSummary("Batch stopped.");
      setErrorText(null);
    } catch (error) {
      setErrorText(error instanceof Error ? error.message : "Failed to stop batch");
    }
  };

  const continueBatch = async (steeringNote: string, preferenceNote: string) => {
    const conversationId = await ensureConversation();
    if (!conversationId) return;
    const notes = [steeringNote.trim(), preferenceNote.trim()].filter(Boolean).join(" | ");
    try {
      if (notes) {
        await steerConversation(conversationId, notes);
        appendLocalMessage(conversationId, "You -> Group", `Steering notes: ${notes}`);
      }
      await continueBatchApi(conversationId);
      setRunStatus("Running");
      setGateStatus("Open");
      setMemoSummary("Batch resumed.");
      setErrorText(null);
    } catch (error) {
      setErrorText(error instanceof Error ? error.message : "Failed to continue batch");
    }
  };

  const markGateReady = () => {
    setGateStatus("Ready");
    setRunStatus("Paused");
  };

  const openCreateAgent = () => {
    setAgentEditor({
      mode: "create",
      displayName: "",
      provider: "claude",
      model: PROVIDER_MODELS.claude[0],
      role: "worker",
      personality_key: "",
    });
  };

  const openEditAgent = (agentId: string) => {
    const agent = agents.find((entry) => entry.id === agentId);
    if (!agent) return;
    setAgentEditor({
      mode: "edit",
      agentId: agent.id,
      displayName: agent.display_name,
      provider: agent.provider,
      model: agent.model,
      role: agent.role,
      personality_key: agent.personality_key ?? "",
    });
  };

  const saveAgent = async () => {
    if (!agentEditor || isSavingAgent) return;
    const payload = {
      display_name: agentEditor.displayName.trim(),
      provider: agentEditor.provider,
      model: agentEditor.model,
      role: agentEditor.role,
      ...(agentEditor.personality_key ? { personality_key: agentEditor.personality_key } : {}),
    };
    if (!payload.display_name || !payload.model) {
      setErrorText("Agent display name and model are required.");
      return;
    }
    setIsSavingAgent(true);
    try {
      if (agentEditor.mode === "create") {
        const created = await createAgentApi({
          ...payload,
          ...(selectedConversationId ? { conversation_id: selectedConversationId } : {}),
        });
        setAgents((prev) =>
          [...prev, toAgentData(created)].sort((a, b) =>
            a.display_name.localeCompare(b.display_name),
          ),
        );
      } else if (agentEditor.agentId) {
        const updated = await updateAgentApi({
          agent_id: agentEditor.agentId,
          ...payload,
        });
        setAgents((prev) =>
          prev
            .map((agent) => (agent.id === updated.id ? toAgentData(updated) : agent))
            .sort((a, b) => a.display_name.localeCompare(b.display_name)),
        );
      }
      setAgentEditor(null);
      setErrorText(null);
    } catch (error) {
      setErrorText(error instanceof Error ? error.message : "Failed to save agent");
    } finally {
      setIsSavingAgent(false);
    }
  };

  const removeAgent = async () => {
    if (!agentEditor?.agentId) return;
    try {
      if (selectedConversationId) {
        await removeAgentFromConversationApi(selectedConversationId, agentEditor.agentId);
      } else {
        await deleteAgentApi(agentEditor.agentId);
      }
      setAgents((prev) => prev.filter((agent) => agent.id !== agentEditor.agentId));
      setAgentEditor(null);
      setErrorText(null);
    } catch (error) {
      setErrorText(error instanceof Error ? error.message : "Failed to delete agent");
    }
  };

  return (
    <div className="app-shell" data-testid="app-shell">
      <TopBar
        runStatus={runStatus}
        gateStatus={gateStatus}
        onRunNewBatch={() => void runNewBatch()}
        onStopRun={() => void stopRun()}
      />
      {errorText ? (
        <div className="app-shell__error" role="status">
          {errorText}
        </div>
      ) : null}
      <section className="app-shell__main" data-testid="main-content">
        <HistoryPane
          conversations={conversations}
          selectedConversationId={selectedConversationId}
          agents={agents}
          onNewConversation={() => openConversationCreator()}
          onDeleteConversation={() => void deleteConversation()}
          onClearConversations={() => void clearAllConversations()}
          onSelectConversation={(conversationId) => void selectConversation(conversationId)}
          onAddAgent={openCreateAgent}
          onEditAgent={openEditAgent}
          reorderConversationAgents={
            selectedConversationId
              ? (agentIds: string[]) =>
                  reorderConversationAgentsApi(selectedConversationId, agentIds)
              : undefined
          }
        />
        <ChatPane
          activeConversationTitle={selectedConversation?.title ?? null}
          messages={selectedMessages}
          onSend={(text) => void sendMessage(text, null)}
        />
        <IntelligencePane
          agreementSummary={
            selectedMessages.length > 0
              ? "Conversation active. Agents are gathering agreement points."
              : undefined
          }
          memoSummary={memoSummary}
        />
      </section>
      <BottomControls
        onContinueBatch={(steering, preference) => void continueBatch(steering, preference)}
        onMarkGateReady={markGateReady}
      />
      {conversationCreator ? (
        <section className="conversation-creator" data-testid="conversation-creator">
          <h3>New Conversation</h3>
          <div className="conversation-creator__grid">
            <label>
              Title
              <input
                value={conversationCreator.title}
                onChange={(event) =>
                  setConversationCreator((prev) =>
                    prev ? { ...prev, title: event.target.value } : prev,
                  )
                }
                placeholder="My conversation"
              />
            </label>
            <label>
              Working Directory
              <input
                value={conversationCreator.workingDirectory}
                onChange={(event) =>
                  setConversationCreator((prev) =>
                    prev ? { ...prev, workingDirectory: event.target.value } : prev,
                  )
                }
                placeholder="/path/to/project"
              />
            </label>
          </div>
          <div className="conversation-creator__actions">
            <button
              className="btn btn--primary"
              onClick={() => void submitConversationCreator()}
              disabled={isCreatingConversation}
            >
              {isCreatingConversation ? "Creating…" : "Create"}
            </button>
            <button className="btn btn--subtle" onClick={() => setConversationCreator(null)}>
              Cancel
            </button>
          </div>
        </section>
      ) : null}
      {agentEditor ? (
        <section className="agent-editor" data-testid="agent-editor">
          <h3>{agentEditor.mode === "create" ? "Add Agent" : "Edit Agent"}</h3>
          <div className="agent-editor__grid">
            <label>
              Name
              <input
                value={agentEditor.displayName}
                onChange={(event) =>
                  setAgentEditor((prev) =>
                    prev ? { ...prev, displayName: event.target.value } : prev,
                  )
                }
              />
            </label>
            <label>
              Provider
              <select
                value={agentEditor.provider}
                onChange={(event) =>
                  setAgentEditor((prev) => {
                    if (!prev) return prev;
                    const newProvider = event.target.value as Provider;
                    return {
                      ...prev,
                      provider: newProvider,
                      model: PROVIDER_MODELS[newProvider][0],
                    };
                  })
                }
              >
                <option value="claude">claude</option>
                <option value="codex">codex</option>
                <option value="ollama">ollama</option>
                <option value="gemini">gemini</option>
              </select>
            </label>
            <label>
              Model
              <select
                value={agentEditor.model}
                onChange={(event) =>
                  setAgentEditor((prev) => (prev ? { ...prev, model: event.target.value } : prev))
                }
              >
                {PROVIDER_MODELS[agentEditor.provider].map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
                {!PROVIDER_MODELS[agentEditor.provider].includes(agentEditor.model) &&
                  agentEditor.model && (
                    <option key={agentEditor.model} value={agentEditor.model}>
                      {agentEditor.model}
                    </option>
                  )}
              </select>
            </label>
            <label>
              Role
              <select
                value={agentEditor.role}
                onChange={(event) =>
                  setAgentEditor((prev) =>
                    prev
                      ? {
                          ...prev,
                          role: event.target.value as AgentRole,
                        }
                      : prev,
                  )
                }
              >
                <option value="worker">worker</option>
                <option value="coordinator">coordinator</option>
                <option value="moderator">moderator</option>
              </select>
            </label>
            <label>
              Personality
              <select
                value={agentEditor.personality_key}
                onChange={(event) =>
                  setAgentEditor((prev) =>
                    prev ? { ...prev, personality_key: event.target.value } : prev,
                  )
                }
              >
                {PERSONALITY_OPTIONS.map((p) => (
                  <option key={p.key} value={p.key}>
                    {p.label}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="agent-editor__actions">
            <button
              className="btn btn--primary"
              onClick={() => void saveAgent()}
              disabled={isSavingAgent}
            >
              {isSavingAgent ? "Saving…" : "Save Agent"}
            </button>
            {agentEditor.mode === "edit" ? (
              <button className="btn btn--danger" onClick={() => void removeAgent()}>
                Delete Agent
              </button>
            ) : null}
            <button className="btn btn--subtle" onClick={() => setAgentEditor(null)}>
              Cancel
            </button>
          </div>
        </section>
      ) : null}
    </div>
  );
}
