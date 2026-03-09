import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  ChartBar,
  CheckCircle,
  User,
} from "@phosphor-icons/react";
import { motion, AnimatePresence } from "framer-motion";
import type { Artifact } from "@/api/client";

interface AgentUI {
  id: string;
  display_name: string;
  provider: string;
  model: string;
  role: string;
  status: string;
}

interface ConversationDetailsProps {
  conversationId: string | null;
  agents: AgentUI[];
  agreementArtifact?: Artifact | null;
  conflictArtifact?: Artifact | null;
  memoArtifact?: Artifact | null;
}

function extractSummary(artifact: Artifact | null | undefined): string | null {
  if (!artifact) return null;
  try {
    const parsed = JSON.parse(artifact.payload_json) as Record<string, unknown>;
    return (
      (typeof parsed.summary === "string" ? parsed.summary : null) ??
      (typeof parsed.text === "string" ? parsed.text : null)
    );
  } catch {
    return null;
  }
}

export function ConversationDetails({
  conversationId,
  agents,
  agreementArtifact,
  conflictArtifact,
  memoArtifact,
}: ConversationDetailsProps) {
  if (!conversationId) {
    return (
      <div className="w-80 border-l bg-muted/30 flex items-center justify-center">
        <p className="text-sm text-muted-foreground px-6 text-center">
          Select a conversation to view details
        </p>
      </div>
    );
  }

  const onlineAgents = agents.filter(
    (a) => a.status === "idle" || a.status === "running",
  );

  const agreementText = extractSummary(agreementArtifact);
  const conflictText = extractSummary(conflictArtifact);
  const memoText = extractSummary(memoArtifact);

  return (
    <div className="w-80 border-l bg-card flex flex-col">
      <div className="border-b px-4 py-3">
        <h3 className="font-semibold text-sm">Conversation Details</h3>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          {/* Quick Overview */}
          <Card className="bg-accent/5 border-accent/20">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <ChartBar size={16} weight="duotone" className="text-accent" />
                Quick Overview
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <div className="text-2xl font-bold text-accent">
                    {onlineAgents.length}
                  </div>
                  <div className="text-xs text-muted-foreground">Active Agents</div>
                </div>
                <div className="space-y-1">
                  <div className="text-2xl font-bold text-warning">
                    {agents.filter((a) => a.status === "running").length}
                  </div>
                  <div className="text-xs text-muted-foreground">Running</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Active Agents */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <User size={16} className="text-muted-foreground" />
              <h4 className="text-sm font-semibold">Active Agents</h4>
              <Badge variant="secondary" className="ml-auto text-xs">
                {agents.length}
              </Badge>
            </div>
            <div className="space-y-2">
              <AnimatePresence mode="popLayout">
                {agents.map((agent, idx) => (
                  <motion.div
                    key={agent.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ delay: idx * 0.05 }}
                    className="flex items-start gap-2 p-2 rounded-lg bg-muted/40 hover:bg-muted/60 transition-colors"
                  >
                    <div className="relative shrink-0">
                      <Avatar className="h-8 w-8">
                        <AvatarImage
                          src={`https://api.dicebear.com/7.x/bottts/svg?seed=${agent.display_name}`}
                        />
                        <AvatarFallback className="text-xs">
                          {agent.display_name.slice(0, 2).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      {(agent.status === "idle" || agent.status === "running") && (
                        <div className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-success border-2 border-card" />
                      )}
                      {agent.status === "running" && (
                        <div className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-warning border-2 border-card animate-pulse" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-xs truncate">
                        {agent.display_name}
                      </div>
                      <div className="text-xs text-muted-foreground capitalize">
                        {agent.status} &middot; {agent.provider}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              {agents.length === 0 && (
                <div className="text-center py-4 text-xs text-muted-foreground">
                  No agents yet
                </div>
              )}
            </div>
          </div>

          <Separator />

          {/* Batch Intelligence */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-3">
              Batch Intelligence
            </h4>
            <div className="space-y-2">
              <Card className="border-l-4 border-l-success">
                <CardHeader className="pb-2 pt-3 px-3">
                  <CardTitle className="text-xs font-semibold">
                    Agreement Map
                  </CardTitle>
                </CardHeader>
                <CardContent className="px-3 pb-3">
                  <p className="text-xs text-muted-foreground">
                    {agreementText ?? "No agreements recorded yet."}
                  </p>
                </CardContent>
              </Card>

              <Card className="border-l-4 border-l-destructive">
                <CardHeader className="pb-2 pt-3 px-3">
                  <CardTitle className="text-xs font-semibold">
                    Conflict Map
                  </CardTitle>
                </CardHeader>
                <CardContent className="px-3 pb-3">
                  <p className="text-xs text-muted-foreground">
                    {conflictText ?? "No conflicts recorded yet."}
                  </p>
                </CardContent>
              </Card>

              <Card className="border-l-4 border-l-muted-foreground">
                <CardHeader className="pb-2 pt-3 px-3">
                  <CardTitle className="text-xs font-semibold">
                    Neutral Memo
                  </CardTitle>
                </CardHeader>
                <CardContent className="px-3 pb-3">
                  <p className="text-xs text-muted-foreground">
                    {memoText ?? "No memo available."}
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>

          <Separator />

          <div>
            <div className="flex items-center gap-2 mb-3">
              <CheckCircle size={16} weight="duotone" className="text-success" />
              <h4 className="text-sm font-semibold">Status</h4>
            </div>
            <div className="text-xs text-muted-foreground">
              <p>
                {agents.length} agent{agents.length !== 1 ? "s" : ""} configured
              </p>
            </div>
          </div>
        </div>
      </ScrollArea>
    </div>
  );
}
