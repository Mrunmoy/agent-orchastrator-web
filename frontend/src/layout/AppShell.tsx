import { useMemo, useState } from "react";
import "./AppShell.css";
import { TopBar } from "./TopBar";
import { ConversationSummary, HistoryPane } from "./HistoryPane";
import { ChatMessage, ChatPane } from "./ChatPane";
import { IntelligencePane } from "./IntelligencePane";
import { BottomControls } from "./BottomControls";

export function AppShell() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);
  const [messagesByConversation, setMessagesByConversation] = useState<
    Record<string, ChatMessage[]>
  >({});
  const [runStatus, setRunStatus] = useState("Idle");
  const [gateStatus, setGateStatus] = useState("Open");
  const [memoSummary, setMemoSummary] = useState("No memo available.");

  const selectedConversation = useMemo(
    () => conversations.find((c) => c.id === selectedConversationId) ?? null,
    [conversations, selectedConversationId],
  );
  const selectedMessages = selectedConversationId
    ? (messagesByConversation[selectedConversationId] ?? [])
    : [];

  const createConversation = () => {
    const now = new Date().toISOString();
    const id =
      typeof crypto !== "undefined" && typeof crypto.randomUUID === "function"
        ? crypto.randomUUID()
        : `${Date.now()}`;
    const conversation: ConversationSummary = {
      id,
      title: `Conversation ${conversations.length + 1}`,
      updatedAt: now,
    };
    setConversations((prev) => [conversation, ...prev]);
    setSelectedConversationId(id);
  };

  const deleteConversation = () => {
    if (!selectedConversationId) return;
    const nextConversations = conversations.filter(
      (conversation) => conversation.id !== selectedConversationId,
    );
    setConversations(nextConversations);
    setMessagesByConversation((prev) => {
      const next = { ...prev };
      delete next[selectedConversationId];
      return next;
    });
    setSelectedConversationId(
      nextConversations.length > 0 ? (nextConversations[0]?.id ?? null) : null,
    );
  };

  const clearConversations = () => {
    setConversations([]);
    setMessagesByConversation({});
    setSelectedConversationId(null);
    setRunStatus("Idle");
    setGateStatus("Open");
    setMemoSummary("No memo available.");
  };

  const sendMessage = (text: string, target: string) => {
    let activeConversationId = selectedConversationId;
    if (!activeConversationId) {
      const now = new Date().toISOString();
      const id =
        typeof crypto !== "undefined" && typeof crypto.randomUUID === "function"
          ? crypto.randomUUID()
          : `${Date.now()}`;
      setConversations((prev) => [
        { id, title: `Conversation ${prev.length + 1}`, updatedAt: now },
        ...prev,
      ]);
      setSelectedConversationId(id);
      activeConversationId = id;
    }
    if (!activeConversationId) return;

    const now = new Date().toISOString();
    const sender = target === "all" ? "You -> Group" : `You -> ${target}`;
    const newMessage: ChatMessage = {
      id: `${activeConversationId}-${Date.now()}`,
      sender,
      text,
      timestamp: now,
    };
    setMessagesByConversation((prev) => ({
      ...prev,
      [activeConversationId!]: [...(prev[activeConversationId!] ?? []), newMessage],
    }));
    setConversations((prev) =>
      prev.map((conversation) =>
        conversation.id === activeConversationId
          ? { ...conversation, updatedAt: now }
          : conversation,
      ),
    );
    setMemoSummary("Latest user direction captured and queued for next agent turn.");
  };

  const runNewBatch = () => {
    setRunStatus("Running");
    setGateStatus("Open");
    if (!selectedConversationId) {
      createConversation();
    }
  };

  const stopRun = () => {
    setRunStatus("Idle");
  };

  const continueBatch = (steeringNote: string, preferenceNote: string) => {
    setRunStatus("Running");
    setGateStatus("Open");
    const notes = [steeringNote.trim(), preferenceNote.trim()].filter(Boolean).join(" | ");
    if (notes) {
      sendMessage(`Steering notes: ${notes}`, "all");
    }
  };

  const markGateReady = () => {
    setGateStatus("Ready");
    setRunStatus("Paused");
  };

  return (
    <div className="app-shell" data-testid="app-shell">
      <TopBar
        runStatus={runStatus}
        gateStatus={gateStatus}
        onRunNewBatch={runNewBatch}
        onStopRun={stopRun}
      />
      <section className="app-shell__main" data-testid="main-content">
        <HistoryPane
          conversations={conversations}
          selectedConversationId={selectedConversationId}
          onNewConversation={createConversation}
          onDeleteConversation={deleteConversation}
          onClearConversations={clearConversations}
          onSelectConversation={setSelectedConversationId}
        />
        <ChatPane
          activeConversationTitle={selectedConversation?.title ?? null}
          messages={selectedMessages}
          onSend={sendMessage}
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
      <BottomControls onContinueBatch={continueBatch} onMarkGateReady={markGateReady} />
    </div>
  );
}
