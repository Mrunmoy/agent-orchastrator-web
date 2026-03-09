import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Toaster } from "@/components/ui/sonner";
import { ArrowLeft, Hash } from "@phosphor-icons/react";
import { AgentCard } from "@/components/AgentCard";

interface AgentUI {
  id: string;
  display_name: string;
  provider: string;
  model: string;
  role: string;
  status: string;
  personality_key?: string;
  sort_order: number;
}

interface DashboardProps {
  conversationTitle: string;
  agents: AgentUI[];
  onNavigateBack: () => void;
}

export function Dashboard({
  conversationTitle,
  agents,
  onNavigateBack,
}: DashboardProps) {
  const activeAgents = agents.filter(
    (a) => a.status !== "offline",
  );
  const runningAgents = agents.filter((a) => a.status === "running");

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <Toaster />

      {/* Sidebar */}
      <aside className="w-64 bg-primary text-primary-foreground flex flex-col border-r">
        <div className="p-4 border-b border-primary-foreground/10">
          <h1 className="text-lg font-bold">Dashboard</h1>
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="p-3 border-t border-primary-foreground/10">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-xs font-semibold uppercase tracking-wide opacity-70">
                Agents
              </h2>
            </div>
            <div className="space-y-0.5">
              {agents.length > 0 ? (
                agents.map((agent) => (
                  <div
                    key={agent.id}
                    className="w-full flex items-center px-2 py-1.5 rounded text-sm text-primary-foreground/80 hover:bg-primary-foreground/10 transition-colors"
                  >
                    <div className="flex items-center gap-2">
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

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="border-b bg-card sticky top-0 z-50">
          <div className="px-6 py-4">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="icon"
                onClick={onNavigateBack}
                className="text-foreground hover:bg-muted"
              >
                <ArrowLeft size={20} />
              </Button>
              <div className="flex items-center gap-2">
                <Hash size={20} className="text-muted-foreground" />
                <h1 className="text-2xl font-bold tracking-tight">
                  {conversationTitle}
                </h1>
              </div>
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-7xl px-6 py-6 space-y-6">
            {/* Stats cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-card border rounded-lg p-4">
                <div className="text-sm text-muted-foreground mb-1">
                  Active Agents
                </div>
                <div className="text-3xl font-bold">{activeAgents.length}</div>
              </div>
              <div className="bg-card border rounded-lg p-4">
                <div className="text-sm text-muted-foreground mb-1">
                  Running
                </div>
                <div className="text-3xl font-bold text-warning">
                  {runningAgents.length}
                </div>
              </div>
              <div className="bg-card border rounded-lg p-4">
                <div className="text-sm text-muted-foreground mb-1">Idle</div>
                <div className="text-3xl font-bold text-success">
                  {agents.filter((a) => a.status === "idle").length}
                </div>
              </div>
              <div className="bg-card border rounded-lg p-4">
                <div className="text-sm text-muted-foreground mb-1">
                  Total Agents
                </div>
                <div className="text-3xl font-bold text-info">
                  {agents.length}
                </div>
              </div>
            </div>

            {/* Agent grid */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">Agents</h2>
                <Badge variant="outline" className="text-xs">
                  {agents.length} total
                </Badge>
              </div>
              {agents.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {agents.map((agent) => (
                    <AgentCard key={agent.id} agent={agent} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 bg-muted/30 rounded-lg border-2 border-dashed">
                  <p className="text-muted-foreground mb-4">
                    No agents in this conversation yet
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
