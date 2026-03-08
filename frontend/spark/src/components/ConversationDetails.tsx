import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Progress } from '@/components/ui/progress'
import { 
  ChartBar, 
  Clock, 
  CheckCircle, 
  GitBranch, 
  User,
  ListChecks,
  GitPullRequest
} from '@phosphor-icons/react'
import type { Agent, Task, Conversation } from '@/lib/types'
import { StatusBadge } from './StatusBadge'
import { motion, AnimatePresence } from 'framer-motion'

interface ConversationDetailsProps {
  conversation: Conversation | null
  agents: Agent[]
  tasks: Task[]
}

export function ConversationDetails({ conversation, agents, tasks }: ConversationDetailsProps) {
  if (!conversation) {
    return (
      <div className="w-80 border-l bg-muted/30 flex items-center justify-center">
        <p className="text-sm text-muted-foreground px-6 text-center">
          Select a conversation to view details
        </p>
      </div>
    )
  }

  const conversationAgentIds = conversation.agents.map(a => a.id)
  const conversationAgents = agents.filter(a => conversationAgentIds.includes(a.id))
  const conversationTasks = tasks.filter(t => conversationAgentIds.includes(t.agentId))

  const activeTasks = conversationTasks.filter(
    t => t.status === 'executing' || t.status === 'planning'
  )
  const completedTasks = conversationTasks.filter(t => t.status === 'completed')
  const totalProgress = conversationTasks.length > 0
    ? Math.round(conversationTasks.reduce((sum, t) => sum + t.progress, 0) / conversationTasks.length)
    : 0

  const onlineAgents = conversationAgents.filter(a => a.status === 'online' || a.status === 'busy')

  return (
    <div className="w-80 border-l bg-card flex flex-col">
      <div className="border-b px-4 py-3">
        <h3 className="font-semibold text-sm">Conversation Details</h3>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
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
                  <div className="text-2xl font-bold text-accent">{onlineAgents.length}</div>
                  <div className="text-xs text-muted-foreground">Active Agents</div>
                </div>
                <div className="space-y-1">
                  <div className="text-2xl font-bold text-warning">{activeTasks.length}</div>
                  <div className="text-xs text-muted-foreground">Running Tasks</div>
                </div>
              </div>
              <Separator />
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Overall Progress</span>
                  <span className="font-medium">{totalProgress}%</span>
                </div>
                <Progress value={totalProgress} className="h-1.5" />
              </div>
            </CardContent>
          </Card>

          <div>
            <div className="flex items-center gap-2 mb-3">
              <User size={16} className="text-muted-foreground" />
              <h4 className="text-sm font-semibold">Active Agents</h4>
              <Badge variant="secondary" className="ml-auto text-xs">
                {conversationAgents.length}
              </Badge>
            </div>
            <div className="space-y-2">
              <AnimatePresence mode="popLayout">
                {conversationAgents.map((agent, idx) => {
                  const agentTask = conversationTasks.find(
                    t => t.agentId === agent.id && t.status !== 'completed' && t.status !== 'failed'
                  )
                  
                  return (
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
                          <AvatarImage src={agent.avatar} />
                          <AvatarFallback className="text-xs">
                            {agent.name.slice(0, 2).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        {agent.status === 'online' && (
                          <div className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-success border-2 border-card" />
                        )}
                        {agent.status === 'busy' && (
                          <div className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-warning border-2 border-card animate-pulse" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-xs truncate">{agent.name}</div>
                        {agentTask ? (
                          <div className="text-xs text-muted-foreground truncate">
                            {agentTask.title}
                          </div>
                        ) : (
                          <div className="text-xs text-muted-foreground">Idle</div>
                        )}
                      </div>
                    </motion.div>
                  )
                })}
              </AnimatePresence>
              {conversationAgents.length === 0 && (
                <div className="text-center py-4 text-xs text-muted-foreground">
                  No agents yet
                </div>
              )}
            </div>
          </div>

          <Separator />

          <div>
            <div className="flex items-center gap-2 mb-3">
              <ListChecks size={16} className="text-muted-foreground" />
              <h4 className="text-sm font-semibold">Recent Tasks</h4>
              <Badge variant="secondary" className="ml-auto text-xs">
                {conversationTasks.length}
              </Badge>
            </div>
            <div className="space-y-2">
              <AnimatePresence mode="popLayout">
                {conversationTasks.slice(0, 5).map((task, idx) => {
                  const taskAgent = conversationAgents.find(a => a.id === task.agentId)
                  
                  return (
                    <motion.div
                      key={task.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      transition={{ delay: idx * 0.05 }}
                      className="p-2 rounded-lg bg-muted/40 space-y-2"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <div className="text-xs font-medium truncate">{task.title}</div>
                          {taskAgent && (
                            <div className="text-xs text-muted-foreground">
                              by {taskAgent.name}
                            </div>
                          )}
                        </div>
                        <StatusBadge status={task.status} className="text-[10px] px-1.5 py-0.5 shrink-0" />
                      </div>
                      {task.status !== 'idle' && task.status !== 'completed' && (
                        <div className="space-y-1">
                          <Progress value={task.progress} className="h-1" />
                          <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <Clock size={10} />
                              {task.phase}
                            </span>
                            <span>{task.progress}%</span>
                          </div>
                        </div>
                      )}
                      {task.prId && (
                        <div className="flex items-center gap-1 text-[10px] text-muted-foreground">
                          <GitPullRequest size={10} />
                          <code className="font-mono">PR #{task.prId}</code>
                        </div>
                      )}
                    </motion.div>
                  )
                })}
              </AnimatePresence>
              {conversationTasks.length === 0 && (
                <div className="text-center py-4 text-xs text-muted-foreground">
                  No tasks yet
                </div>
              )}
              {conversationTasks.length > 5 && (
                <div className="text-center pt-2">
                  <p className="text-xs text-muted-foreground">
                    +{conversationTasks.length - 5} more tasks
                  </p>
                </div>
              )}
            </div>
          </div>

          <Separator />

          <div>
            <div className="flex items-center gap-2 mb-3">
              <CheckCircle size={16} weight="duotone" className="text-success" />
              <h4 className="text-sm font-semibold">Completed</h4>
              <Badge variant="secondary" className="ml-auto text-xs bg-success/10 text-success border-success/20">
                {completedTasks.length}
              </Badge>
            </div>
            <div className="text-xs text-muted-foreground">
              {completedTasks.length === 0 ? (
                <p className="text-center py-2">No completed tasks yet</p>
              ) : (
                <p>{completedTasks.length} task{completedTasks.length !== 1 ? 's' : ''} completed</p>
              )}
            </div>
          </div>

          <Separator />

          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-3">
              Batch Intelligence
            </h4>
            <div className="space-y-2">
              <Card className="border-l-4 border-l-success">
                <CardHeader className="pb-2 pt-3 px-3">
                  <CardTitle className="text-xs font-semibold">Agreement Map</CardTitle>
                </CardHeader>
                <CardContent className="px-3 pb-3">
                  <p className="text-xs text-muted-foreground">No agreements recorded yet.</p>
                </CardContent>
              </Card>

              <Card className="border-l-4 border-l-destructive">
                <CardHeader className="pb-2 pt-3 px-3">
                  <CardTitle className="text-xs font-semibold">Conflict Map</CardTitle>
                </CardHeader>
                <CardContent className="px-3 pb-3">
                  <p className="text-xs text-muted-foreground">No conflicts recorded yet.</p>
                </CardContent>
              </Card>

              <Card className="border-l-4 border-l-muted-foreground">
                <CardHeader className="pb-2 pt-3 px-3">
                  <CardTitle className="text-xs font-semibold">Neutral Memo</CardTitle>
                </CardHeader>
                <CardContent className="px-3 pb-3">
                  <p className="text-xs text-muted-foreground">No memo available.</p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </ScrollArea>
    </div>
  )
}
