import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { StatusBadge } from './StatusBadge'
import { Clock, GitBranch, User, Robot } from '@phosphor-icons/react'
import type { Agent, Task } from '@/lib/types'
import { motion } from 'framer-motion'

interface AgentCardProps {
  agent: Agent
  task?: Task
  onClick?: () => void
}

export function AgentCard({ agent, task, onClick }: AgentCardProps) {
  const statusColor = {
    online: 'bg-success',
    offline: 'bg-muted-foreground',
    busy: 'bg-warning'
  }[agent.status]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card
        className="transition-all hover:shadow-md hover:border-primary/20"
      >
        <CardHeader className="pb-3">
          <div className="flex items-center gap-3 mb-3">
            <div className="relative">
              <Avatar>
                <AvatarImage src={agent.avatar} />
                <AvatarFallback>{agent.name.slice(0, 2).toUpperCase()}</AvatarFallback>
              </Avatar>
              <div
                className={`absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-card ${statusColor}`}
              />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold">{agent.name}</h3>
              <p className="text-xs text-muted-foreground capitalize">{agent.status}</p>
            </div>
          </div>
          <div className="flex flex-col gap-2">
            {agent.personality && (
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <User size={14} weight="duotone" />
                <span>{agent.personality}</span>
              </div>
            )}
            {agent.model && (
              <div className="flex items-center gap-1.5 text-xs">
                <Robot size={14} weight="duotone" className="text-muted-foreground" />
                <Badge variant="secondary" className="text-xs font-mono">
                  {agent.model}
                </Badge>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {task ? (
            <>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">{task.title}</span>
                  <StatusBadge status={task.status} />
                </div>
                <p className="text-xs text-muted-foreground line-clamp-2">
                  {task.description}
                </p>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Progress</span>
                  <span className="font-medium">{task.progress}%</span>
                </div>
                <Progress value={task.progress} className="h-1.5" />
              </div>

              <div className="flex items-center gap-4 text-xs text-muted-foreground pt-2">
                {task.prId && (
                  <div className="flex items-center gap-1">
                    <GitBranch size={14} />
                    <code className="font-mono">#{task.prId}</code>
                  </div>
                )}
                <div className="flex items-center gap-1">
                  <Clock size={14} />
                  <span>{task.phase}</span>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-4 text-sm text-muted-foreground">
              No active task
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
