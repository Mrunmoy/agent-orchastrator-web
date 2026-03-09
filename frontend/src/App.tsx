import { useState } from "react";
import { MainApp } from "@/components/MainApp";
import { Dashboard } from "@/components/Dashboard";
import { listConversations, listConversationAgents } from "@/api/client";

type View = "main" | "dashboard";

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

function App() {
  const [currentView, setCurrentView] = useState<View>("main");
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);
  const [dashboardTitle, setDashboardTitle] = useState("");
  const [dashboardAgents, setDashboardAgents] = useState<AgentUI[]>([]);

  const handleNavigateToDashboard = async (conversationId: string) => {
    setSelectedConversationId(conversationId);
    try {
      const conversations = await listConversations();
      const conv = conversations.find((c) => c.id === conversationId);
      setDashboardTitle(conv?.title ?? conversationId);
      const agents = await listConversationAgents(conversationId);
      setDashboardAgents(
        agents.map((a) => ({
          id: a.id,
          display_name: a.display_name,
          provider: a.provider,
          model: a.model,
          role: a.role,
          status: a.status,
          personality_key: a.personality_key ?? undefined,
          sort_order: a.sort_order,
        })),
      );
    } catch {
      setDashboardTitle(conversationId);
      setDashboardAgents([]);
    }
    setCurrentView("dashboard");
  };

  const handleNavigateBack = () => {
    setCurrentView("main");
    setSelectedConversationId(null);
  };

  if (currentView === "dashboard" && selectedConversationId) {
    return (
      <Dashboard
        conversationTitle={dashboardTitle}
        agents={dashboardAgents}
        onNavigateBack={handleNavigateBack}
      />
    );
  }

  return (
    <MainApp
      onNavigateToDashboard={(id) => void handleNavigateToDashboard(id)}
    />
  );
}

export default App;
