import { useState, useEffect, useMemo } from "react";
import { Button } from "@/components/ui/button";
import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from "@/components/ui/avatar";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Hash,
  Bell,
  MagnifyingGlass,
  Gear,
  ChartBar,
  Plus,
  At,
  DotsThree,
  Trash,
  PaperPlaneTilt,
  Play,
  Stop,
} from "@phosphor-icons/react";
import { motion } from "framer-motion";
import { ConversationDetails } from "@/components/ConversationDetails";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";
import { providerModels, personalities } from "@/lib/models";
import {
  listConversations,
  createConversation as createConversationApi,
  selectConversation as selectConversationApi,
  deleteConversation as deleteConversationApi,
  listConversationAgents,
  createAgent as createAgentApi,
  deleteAgent as deleteAgentApi,
  steerConversation,
  runBatch,
  stopBatch,
  type Conversation,
  type Agent,
} from "@/api/client";
import { useEventStream } from "@/hooks/useEventStream";
import { eventsToChatMessages, mergeWithLocal } from "@/features/chat/eventTransform";
import { useArtifacts } from "@/hooks/useArtifacts";
import { useRunStatus, type DisplayStatus } from "@/hooks/useRunStatus";
import type { ChatMessageData } from "@/features/chat/types";

interface MainAppProps {
  onNavigateToDashboard: (conversationId: string) => void;
}

type ConvSummary = {
  id: string;
  title: string;
  updatedAt: string;
};

type AgentUI = {
  id: string;
  display_name: string;
  provider: string;
  model: string;
  role: string;
  status: string;
  personality_key?: string;
  sort_order: number;
};

function toConvSummary(row: Conversation): ConvSummary {
  return { id: row.id, title: row.title, updatedAt: row.updated_at };
}

function toAgentUI(row: Agent): AgentUI {
  return {
    id: row.id,
    display_name: row.display_name,
    provider: row.provider,
    model: row.model,
    role: row.role,
    status: row.status,
    personality_key: row.personality_key ?? undefined,
    sort_order: row.sort_order,
  };
}

const WORKING_DIR_KEY = "ao_working_dir";
const DEFAULT_WORKING_DIR = "/home/user/workspace";

function getWorkingDirectory(): string {
  try {
    return window.localStorage.getItem(WORKING_DIR_KEY) ?? DEFAULT_WORKING_DIR;
  } catch {
    return DEFAULT_WORKING_DIR;
  }
}

export function MainApp({ onNavigateToDashboard }: MainAppProps) {
  // --- State ---
  const [conversations, setConversations] = useState<ConvSummary[]>([]);
  const [agents, setAgents] = useState<AgentUI[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messagesByConversation, setMessagesByConversation] = useState<
    Record<string, ChatMessageData[]>
  >({});

  // Conversation creator
  const [isAddConversationOpen, setIsAddConversationOpen] = useState(false);
  const [newConversationName, setNewConversationName] = useState("");
  const [newConversationWorkDir, setNewConversationWorkDir] = useState(getWorkingDirectory());

  // Agent creator
  const [isAddAgentOpen, setIsAddAgentOpen] = useState(false);
  const [newAgentName, setNewAgentName] = useState("");
  const [newAgentShortName, setNewAgentShortName] = useState("");
  const [newAgentProvider, setNewAgentProvider] = useState("claude");
  const [newAgentModel, setNewAgentModel] = useState("claude-opus-4-5");
  const [newAgentPersonality, setNewAgentPersonality] = useState("Software Developer");
  const [availableModels, setAvailableModels] = useState<string[]>(providerModels.claude);

  // Chat
  const [messageInput, setMessageInput] = useState("");

  // Run status
  const [runStatusOverride, setRunStatusOverride] = useState<DisplayStatus | null>(null);
  const { status: polledRunStatus } = useRunStatus(activeConversationId);
  useEffect(() => {
    if (runStatusOverride !== null && polledRunStatus === runStatusOverride) {
      setRunStatusOverride(null);
    }
  }, [polledRunStatus, runStatusOverride]);
  const runStatus = runStatusOverride ?? polledRunStatus;

  // Artifacts
  const { agreementMap, conflictMap, neutralMemo } = useArtifacts(activeConversationId);

  // Event stream
  const { events: streamEvents } = useEventStream(activeConversationId);
  const eventMessages = useMemo(
    () =>
      eventsToChatMessages(
        streamEvents,
        agents.map((a) => ({
          id: a.id,
          display_name: a.display_name,
          provider: a.provider as "claude" | "codex" | "ollama" | "gemini",
          model: a.model,
          role: a.role as "worker" | "coordinator" | "moderator",
          status: a.status as "idle" | "running" | "blocked" | "offline",
          sort_order: a.sort_order,
        })),
      ),
    [streamEvents, agents],
  );
  const localMessages = useMemo(
    () => (activeConversationId ? (messagesByConversation[activeConversationId] ?? []) : []),
    [activeConversationId, messagesByConversation],
  );
  const selectedMessages = useMemo(
    () => mergeWithLocal(eventMessages, localMessages),
    [eventMessages, localMessages],
  );

  // --- Effects ---
  useEffect(() => {
    const load = async () => {
      try {
        const rows = await listConversations();
        const convs = rows.map(toConvSummary);
        setConversations(convs);
        const activeId = rows.find((c) => c.active === 1)?.id ?? convs[0]?.id ?? null;
        setActiveConversationId(activeId);
      } catch (err) {
        toast.error(err instanceof Error ? err.message : "Failed to load conversations");
      }
    };
    void load();
  }, []);

  useEffect(() => {
    const loadAgents = async () => {
      if (activeConversationId) {
        try {
          const rows = await listConversationAgents(activeConversationId);
          setAgents(rows.map(toAgentUI));
        } catch {
          setAgents([]);
        }
      } else {
        setAgents([]);
      }
    };
    void loadAgents();
  }, [activeConversationId]);

  useEffect(() => {
    const models =
      providerModels[newAgentProvider as keyof typeof providerModels] ?? [];
    setAvailableModels(models);
    if (models.length > 0) {
      setNewAgentModel(models[0] ?? "");
    }
  }, [newAgentProvider]);

  const activeConversation = conversations.find((c) => c.id === activeConversationId);

  // --- Handlers ---
  const handleAddConversation = async () => {
    if (!newConversationName.trim()) {
      toast.error("Please enter a conversation name");
      return;
    }
    try {
      const created = await createConversationApi(
        newConversationName,
        newConversationWorkDir || DEFAULT_WORKING_DIR,
      );
      await selectConversationApi(created.id);
      setConversations((prev) => [toConvSummary(created), ...prev]);
      setActiveConversationId(created.id);
      setNewConversationName("");
      setIsAddConversationOpen(false);
      toast.success(`Created conversation: ${newConversationName}`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to create conversation");
    }
  };

  const handleAddAgent = async () => {
    if (!newAgentName.trim()) {
      toast.error("Please enter an agent name");
      return;
    }
    if (!activeConversationId) {
      toast.error("Please select a conversation first");
      return;
    }
    try {
      const created = await createAgentApi({
        display_name: newAgentName,
        provider: newAgentProvider as Agent["provider"],
        model: newAgentModel,
        role: "worker",
        personality_key: newAgentPersonality,
        conversation_id: activeConversationId,
      });
      setAgents((prev) => [...prev, toAgentUI(created)]);
      setNewAgentName("");
      setNewAgentShortName("");
      setNewAgentProvider("claude");
      setNewAgentModel("claude-opus-4-5");
      setNewAgentPersonality("Software Developer");
      setIsAddAgentOpen(false);
      toast.success(`Added agent: ${newAgentName}`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to add agent");
    }
  };

  const handleDeleteConversation = async (conversationId: string) => {
    const conv = conversations.find((c) => c.id === conversationId);
    if (!conv) return;
    try {
      await deleteConversationApi(conversationId);
      setConversations((prev) => prev.filter((c) => c.id !== conversationId));
      if (activeConversationId === conversationId) {
        const remaining = conversations.filter((c) => c.id !== conversationId);
        setActiveConversationId(remaining.length > 0 ? remaining[0]!.id : null);
      }
      toast.success(`Deleted conversation: ${conv.title}`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to delete conversation");
    }
  };

  const handleDeleteAgent = async (agentId: string) => {
    const agent = agents.find((a) => a.id === agentId);
    if (!agent) return;
    try {
      await deleteAgentApi(agentId);
      setAgents((prev) => prev.filter((a) => a.id !== agentId));
      toast.success(`Deleted agent: ${agent.display_name}`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to delete agent");
    }
  };

  const appendLocalMessage = (sender: string, text: string) => {
    if (!activeConversationId) return;
    const now = new Date().toISOString();
    const newMessage: ChatMessageData = {
      id: `${activeConversationId}-${Date.now()}`,
      agentName: sender,
      text,
      timestamp: now,
      isUser: true,
      type: "steer",
    };
    setMessagesByConversation((prev) => ({
      ...prev,
      [activeConversationId]: [...(prev[activeConversationId] ?? []), newMessage],
    }));
  };

  const handleSendMessage = async () => {
    if (!messageInput.trim() || !activeConversationId) return;
    try {
      await steerConversation(activeConversationId, messageInput);
      appendLocalMessage("You", messageInput);
      setMessageInput("");
      toast.success("Message sent!");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to send message");
    }
  };

  const handleRunBatch = async () => {
    if (!activeConversationId) return;
    try {
      await runBatch(activeConversationId, 20);
      setRunStatusOverride("Running");
      toast.success("Batch started (20 turns)");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to start batch");
    }
  };

  const handleStopBatch = async () => {
    if (!activeConversationId) return;
    try {
      await stopBatch(activeConversationId);
      setRunStatusOverride("Idle");
      toast.success("Batch stopped");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to stop batch");
    }
  };

  const activeConversationName = activeConversation?.title || "Select a conversation";

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <Toaster />

      {/* Sidebar */}
      <aside className="w-64 bg-primary text-primary-foreground flex flex-col border-r">
        <div className="p-4 border-b border-primary-foreground/10">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-lg font-bold">Agent Workspace</h1>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-primary-foreground hover:bg-primary-foreground/10"
            >
              <Gear size={18} />
            </Button>
          </div>
          <div className="space-y-2">
            {activeConversationId && (
              <Button
                onClick={() => onNavigateToDashboard(activeConversationId)}
                className="w-full bg-accent hover:bg-accent/90 text-accent-foreground flex items-center gap-2 justify-start"
              >
                <ChartBar size={18} weight="duotone" />
                Agent Dashboard
              </Button>
            )}
            <div className="flex gap-1">
              {runStatus === "Idle" || runStatus === "Paused" ? (
                <Button
                  onClick={() => void handleRunBatch()}
                  variant="ghost"
                  size="sm"
                  className="flex-1 text-primary-foreground hover:bg-primary-foreground/10"
                  disabled={!activeConversationId}
                >
                  <Play size={14} className="mr-1" />
                  Run Batch
                </Button>
              ) : (
                <Button
                  onClick={() => void handleStopBatch()}
                  variant="ghost"
                  size="sm"
                  className="flex-1 text-primary-foreground hover:bg-primary-foreground/10"
                >
                  <Stop size={14} className="mr-1" />
                  Stop
                </Button>
              )}
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {/* Conversations */}
          <div className="p-3">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-xs font-semibold uppercase tracking-wide opacity-70">
                Conversations
              </h2>
              <Dialog open={isAddConversationOpen} onOpenChange={setIsAddConversationOpen}>
                <DialogTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-5 w-5 text-primary-foreground/70 hover:bg-primary-foreground/10"
                  >
                    <Plus size={14} />
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Create New Conversation</DialogTitle>
                    <DialogDescription>
                      Add a new conversation to organize your agents and tasks.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label htmlFor="conversation-name">Conversation Name</Label>
                      <Input
                        id="conversation-name"
                        placeholder="e.g., Project Alpha"
                        value={newConversationName}
                        onChange={(e) => setNewConversationName(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter") {
                            void handleAddConversation();
                          }
                        }}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="conversation-workdir">Working Directory</Label>
                      <Input
                        id="conversation-workdir"
                        placeholder="/path/to/project"
                        value={newConversationWorkDir}
                        onChange={(e) => setNewConversationWorkDir(e.target.value)}
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button
                      variant="outline"
                      onClick={() => setIsAddConversationOpen(false)}
                    >
                      Cancel
                    </Button>
                    <Button onClick={() => void handleAddConversation()}>Create</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
            <div className="space-y-0.5">
              {conversations.length > 0 ? (
                conversations.map((conversation) => (
                  <div
                    key={conversation.id}
                    className={`w-full flex items-center justify-between px-2 py-1.5 rounded text-sm transition-colors group ${
                      activeConversationId === conversation.id
                        ? "bg-accent/20 text-primary-foreground font-medium"
                        : "text-primary-foreground/80 hover:bg-primary-foreground/10"
                    }`}
                  >
                    <button
                      onClick={() => {
                        setActiveConversationId(conversation.id);
                        void selectConversationApi(conversation.id);
                      }}
                      className="flex items-center gap-2 flex-1 text-left"
                    >
                      <Hash size={16} />
                      <span className="truncate">{conversation.title}</span>
                    </button>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-5 w-5 opacity-0 group-hover:opacity-100 transition-opacity text-primary-foreground/70 hover:bg-primary-foreground/20"
                        >
                          <DotsThree size={16} weight="bold" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          className="text-destructive focus:text-destructive"
                          onClick={() => void handleDeleteConversation(conversation.id)}
                        >
                          <Trash size={14} className="mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                ))
              ) : (
                <p className="text-xs text-primary-foreground/60 px-2 py-2">
                  No conversations yet
                </p>
              )}
            </div>
          </div>

          {/* Direct Messages (Agent list) */}
          <div className="p-3 border-t border-primary-foreground/10">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-xs font-semibold uppercase tracking-wide opacity-70">
                Direct Messages
              </h2>
              <Dialog open={isAddAgentOpen} onOpenChange={setIsAddAgentOpen}>
                <DialogTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-5 w-5 text-primary-foreground/70 hover:bg-primary-foreground/10"
                    disabled={!activeConversationId}
                  >
                    <Plus size={14} />
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl">
                  <DialogHeader>
                    <DialogTitle>Add Agent</DialogTitle>
                    <DialogDescription>
                      Add a new agent to the current conversation.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="agent-name">Name</Label>
                        <Input
                          id="agent-name"
                          placeholder="Enter agent name..."
                          value={newAgentName}
                          onChange={(e) => setNewAgentName(e.target.value)}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="agent-short-name">Short Name (@ mention)</Label>
                        <Input
                          id="agent-short-name"
                          placeholder="e.g., dev, tester, doc"
                          value={newAgentShortName}
                          onChange={(e) =>
                            setNewAgentShortName(
                              e.target.value.replace("@", "").toLowerCase(),
                            )
                          }
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="agent-personality">Personality</Label>
                        <Select
                          value={newAgentPersonality}
                          onValueChange={setNewAgentPersonality}
                        >
                          <SelectTrigger id="agent-personality" className="w-full">
                            <SelectValue placeholder="Select personality" />
                          </SelectTrigger>
                          <SelectContent>
                            {personalities.map((personality) => (
                              <SelectItem key={personality} value={personality}>
                                {personality}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="agent-provider">Provider</Label>
                        <Select
                          value={newAgentProvider}
                          onValueChange={setNewAgentProvider}
                        >
                          <SelectTrigger id="agent-provider" className="w-full">
                            <SelectValue placeholder="Select provider" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="claude">Claude (Anthropic)</SelectItem>
                            <SelectItem value="openai">OpenAI</SelectItem>
                            <SelectItem value="gemini">Gemini (Google)</SelectItem>
                            <SelectItem value="ollama">Ollama (Local)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="agent-model">Model</Label>
                        <Select value={newAgentModel} onValueChange={setNewAgentModel}>
                          <SelectTrigger id="agent-model" className="w-full">
                            <SelectValue placeholder="Select model" />
                          </SelectTrigger>
                          <SelectContent>
                            {availableModels.map((model) => (
                              <SelectItem key={model} value={model}>
                                {model}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </div>
                  <DialogFooter>
                    <Button
                      variant="outline"
                      onClick={() => setIsAddAgentOpen(false)}
                    >
                      Cancel
                    </Button>
                    <Button onClick={() => void handleAddAgent()}>Save Agent</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
            <div className="space-y-0.5">
              {agents.length > 0 ? (
                agents.map((agent) => (
                  <div
                    key={agent.id}
                    className="w-full flex items-center justify-between px-2 py-1.5 rounded text-sm text-primary-foreground/80 hover:bg-primary-foreground/10 transition-colors group"
                  >
                    <div className="flex items-center gap-2 flex-1">
                      <div className="relative">
                        <Avatar className="h-5 w-5">
                          <AvatarImage
                            src={`https://api.dicebear.com/7.x/bottts/svg?seed=${agent.display_name}`}
                          />
                          <AvatarFallback className="text-xs">
                            {agent.display_name.slice(0, 2).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        {(agent.status === "idle" || agent.status === "running") && (
                          <div className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-success border-2 border-primary" />
                        )}
                      </div>
                      <span className="truncate">{agent.display_name}</span>
                    </div>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-5 w-5 opacity-0 group-hover:opacity-100 transition-opacity text-primary-foreground/70 hover:bg-primary-foreground/20"
                        >
                          <DotsThree size={16} weight="bold" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          className="text-destructive focus:text-destructive"
                          onClick={() => void handleDeleteAgent(agent.id)}
                        >
                          <Trash size={14} className="mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                ))
              ) : (
                <p className="text-xs text-primary-foreground/60 px-2 py-2">
                  No agents yet
                </p>
              )}
            </div>
          </div>
        </div>

        {/* User footer */}
        <div className="p-3 border-t border-primary-foreground/10">
          <div className="flex items-center gap-2">
            <Avatar className="h-8 w-8">
              <AvatarFallback>ME</AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">You</div>
              <div className="text-xs opacity-70 flex items-center gap-1">
                <div className="h-2 w-2 rounded-full bg-success" />
                Active
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        <header className="h-14 border-b bg-card flex items-center justify-between px-4">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Hash size={20} className="text-muted-foreground" />
              <h2 className="font-semibold text-lg">{activeConversationName}</h2>
            </div>
            {runStatus !== "Idle" && (
              <span
                className={`text-xs px-2 py-0.5 rounded-full ${
                  runStatus === "Running"
                    ? "bg-success/10 text-success animate-pulse"
                    : "bg-warning/10 text-warning"
                }`}
              >
                {runStatus}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" className="h-9 w-9">
              <MagnifyingGlass size={18} />
            </Button>
            <Button variant="ghost" size="icon" className="h-9 w-9">
              <At size={18} />
            </Button>
            <Button variant="ghost" size="icon" className="h-9 w-9 relative">
              <Bell size={18} />
            </Button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {activeConversation ? (
            <>
              {selectedMessages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex gap-3 hover:bg-muted/30 -mx-2 px-2 py-2 rounded"
                >
                  <Avatar className="h-10 w-10">
                    <AvatarImage
                      src={
                        message.isUser
                          ? undefined
                          : `https://api.dicebear.com/7.x/bottts/svg?seed=${message.agentName}`
                      }
                    />
                    <AvatarFallback>
                      {(message.agentName || "UN").slice(0, 2).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-baseline gap-2 mb-1">
                      <span className="font-semibold text-sm">
                        {message.agentName || "Unknown"}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {new Date(message.timestamp).toLocaleTimeString("en-US", {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </span>
                    </div>
                    <p className="text-sm whitespace-pre-wrap">{message.text}</p>
                  </div>
                </motion.div>
              ))}

              {selectedMessages.length === 0 && (
                <div className="text-center py-12 text-muted-foreground">
                  <p>No messages yet. Start the conversation!</p>
                </div>
              )}
            </>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center space-y-4">
                <p className="text-muted-foreground">No conversation selected</p>
                <Button onClick={() => setIsAddConversationOpen(true)}>
                  Create Your First Conversation
                </Button>
              </div>
            </div>
          )}
        </div>

        <div className="border-t p-4">
          <div className="flex items-center gap-2">
            <Input
              type="text"
              placeholder={`Message #${activeConversationName}`}
              className="flex-1"
              value={messageInput}
              onChange={(e) => setMessageInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  void handleSendMessage();
                }
              }}
              disabled={!activeConversation}
            />
            <Button
              size="icon"
              className="bg-accent hover:bg-accent/90 text-accent-foreground"
              onClick={() => void handleSendMessage()}
              disabled={!activeConversation || !messageInput.trim()}
            >
              <PaperPlaneTilt size={18} weight="fill" />
            </Button>
          </div>
        </div>
      </div>

      {/* Right panel - Conversation Details */}
      <ConversationDetails
        conversationId={activeConversationId}
        agents={agents}
        agreementArtifact={agreementMap}
        conflictArtifact={conflictMap}
        memoArtifact={neutralMemo}
      />
    </div>
  );
}
