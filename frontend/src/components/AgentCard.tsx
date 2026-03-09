import {
  Card,
  CardContent,
  CardHeader,
} from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { User, Robot } from "@phosphor-icons/react";
import { motion } from "framer-motion";

interface AgentUI {
  id: string;
  display_name: string;
  provider: string;
  model: string;
  role: string;
  status: string;
  personality_key?: string;
}

interface AgentCardProps {
  agent: AgentUI;
}

export function AgentCard({ agent }: AgentCardProps) {
  const statusColor = {
    idle: "bg-success",
    running: "bg-warning",
    blocked: "bg-error",
    offline: "bg-muted-foreground",
  }[agent.status] ?? "bg-muted-foreground";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="transition-all hover:shadow-md hover:border-primary/20">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-3 mb-3">
            <div className="relative">
              <Avatar>
                <AvatarImage
                  src={`https://api.dicebear.com/7.x/bottts/svg?seed=${agent.display_name}`}
                />
                <AvatarFallback>
                  {agent.display_name.slice(0, 2).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div
                className={`absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-card ${statusColor}`}
              />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold">{agent.display_name}</h3>
              <p className="text-xs text-muted-foreground capitalize">
                {agent.status}
              </p>
            </div>
          </div>
          <div className="flex flex-col gap-2">
            {agent.personality_key && (
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <User size={14} weight="duotone" />
                <span>{agent.personality_key}</span>
              </div>
            )}
            {agent.model && (
              <div className="flex items-center gap-1.5 text-xs">
                <Robot
                  size={14}
                  weight="duotone"
                  className="text-muted-foreground"
                />
                <Badge variant="secondary" className="text-xs font-mono">
                  {agent.model}
                </Badge>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs capitalize">
              {agent.role}
            </Badge>
            <Badge variant="outline" className="text-xs capitalize">
              {agent.provider}
            </Badge>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
