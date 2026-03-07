import { useEffect, useMemo, useState } from "react";
import type { AgentData, AgentRole, Provider } from "../features/agents";
import {
  clearConversations as clearConversationsApi,
  createAgent as createAgentApi,
  createConversation as createConversationApi,
  deleteAgent as deleteAgentApi,
  deleteConversation as deleteConversationApi,
  listAgents,
  listConversations,
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

type AgentEditorState = {
  mode: "create" | "edit";
  agentId?: string;
  displayName: string;
  provider: Provider;
  model: string;
  role: AgentRole;
};

function getWorkingDirectory(): string {
  try {
    return window.localStorage.getItem(WORKING_DIR_KEY) ?? DEFAULT_WORKING_DIR;
  } catch {
    return DEFAULT_WORKING_DIR;
  }
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
}): AgentData {
  return {
    id: row.id,
    display_name: row.display_name,
    provider: row.provider,
    model: row.model,
    role: row.role,
    status: row.status,
    personality_key: row.personality_key ?? undefined,
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
        const [conversationRows, agentRows] = await Promise.all([
          listConversations(),
          listAgents(),
        ]);
        const nextConversations = conversationRows.map(toConversationSummary);
        setConversations(nextConversations);
        setSelectedConversationId(
          conversationRows.find((conversation) => conversation.active === 1)?.id ??
            nextConversations[0]?.id ??
            null,
        );
        setAgents(agentRows.map(toAgentData));
      } catch (error) {
        setErrorText(error instanceof Error ? error.message : "Failed to load initial data");
      }
    };
    void load();
  }, []);

  const createConversation = async () => {
    try {
      const created = await createConversationApi(
        `Conversation ${conversations.length + 1}`,
        getWorkingDirectory(),
      );
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
      setErrorText(null);
      return selectedId;
    } catch (error) {
      setErrorText(error instanceof Error ? error.message : "Failed to create conversation");
      return null;
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
      const nextConversations = conversations.filter(
        (conversation) => conversation.id !== selectedConversationId,
      );
      setConversations(nextConversations);
      setMessagesByConversation((prev) => {
        const next = { ...prev };
        delete next[selectedConversationId];
        return next;
      });
      const fallbackId = nextConversations[0]?.id ?? null;
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
    return createConversation();
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
      model: "",
      role: "worker",
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
    });
  };

  const saveAgent = async () => {
    if (!agentEditor) return;
    const payload = {
      display_name: agentEditor.displayName.trim(),
      provider: agentEditor.provider,
      model: agentEditor.model.trim(),
      role: agentEditor.role,
    };
    if (!payload.display_name || !payload.model) {
      setErrorText("Agent display name and model are required.");
      return;
    }
    try {
      if (agentEditor.mode === "create") {
        const created = await createAgentApi(payload);
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
    }
  };

  const removeAgent = async () => {
    if (!agentEditor?.agentId) return;
    try {
      await deleteAgentApi(agentEditor.agentId);
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
          onNewConversation={() => void createConversation()}
          onDeleteConversation={() => void deleteConversation()}
          onClearConversations={() => void clearAllConversations()}
          onSelectConversation={(conversationId) => void selectConversation(conversationId)}
          onAddAgent={openCreateAgent}
          onEditAgent={openEditAgent}
        />
        <ChatPane
          activeConversationTitle={selectedConversation?.title ?? null}
          messages={selectedMessages}
          onSend={(text, target) => void sendMessage(text, target)}
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
                  setAgentEditor((prev) =>
                    prev
                      ? {
                          ...prev,
                          provider: event.target.value as Provider,
                        }
                      : prev,
                  )
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
              <input
                value={agentEditor.model}
                onChange={(event) =>
                  setAgentEditor((prev) => (prev ? { ...prev, model: event.target.value } : prev))
                }
              />
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
          </div>
          <div className="agent-editor__actions">
            <button className="btn btn--primary" onClick={() => void saveAgent()}>
              Save Agent
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
