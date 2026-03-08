import { useKV } from '@/shims/spark-hooks'
import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { ArrowLeft, Hash, GithubLogo, ArrowSquareOut, CloudArrowDown } from '@phosphor-icons/react'
import { AgentCard } from '@/components/AgentCard'
import { PRCard } from '@/components/PRCard'
import { useAgentActivitySimulation } from '@/hooks/use-agent-activity-simulation'
import type { Agent, Task, PullRequest, Conversation } from '@/lib/types'
import { Toaster } from '@/components/ui/sonner'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { toast } from 'sonner'
import { fetchGitHubPRs, parseGitHubURL } from '@/lib/github'

interface DashboardProps {
  conversationId: string
  onNavigateBack: () => void
}

export function Dashboard({ conversationId, onNavigateBack }: DashboardProps) {
  const [conversations] = useKV<Conversation[]>('conversations', [])
  const [agents] = useKV<Agent[]>('agents', [])
  const [tasks] = useKV<Task[]>('tasks', [])
  const [pullRequests] = useKV<PullRequest[]>('pullRequests', [])

  const conversation = conversations?.find(c => c.id === conversationId)
  const conversationName = conversation?.name || conversationId

  const conversationAgentIds = conversation?.agents.map(a => a.id) || []
  const conversationAgents = agents?.filter(a => conversationAgentIds.includes(a.id)) || []
  
  const conversationTasks = tasks?.filter(t => conversationAgentIds.includes(t.agentId)) || []
  const conversationPRs = pullRequests?.filter(pr => {
    const prTask = tasks?.find(t => t.prId === pr.id.toString())
    return prTask && conversationAgentIds.includes(prTask.agentId)
  }) || []

  const getTaskForAgent = (agentId: string): Task | undefined => {
    return conversationTasks.find(t => t.agentId === agentId && t.status !== 'completed' && t.status !== 'failed')
  }

  const activeTasks = conversationTasks.filter(t => t.status === 'executing' || t.status === 'planning') || []
  const completedTasks = conversationTasks.filter(t => t.status === 'completed') || []
  const openPRs = conversationPRs.filter(pr => pr.status === 'open') || []

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <Toaster />
      
      <aside className="w-64 bg-primary text-primary-foreground flex flex-col border-r">
        <div className="p-4 border-b border-primary-foreground/10">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-lg font-bold">Dashboard</h1>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="p-3 border-t border-primary-foreground/10">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-xs font-semibold uppercase tracking-wide opacity-70">Direct Messages</h2>
            </div>
            <div className="space-y-0.5">
              {conversationAgents && conversationAgents.length > 0 ? (
                conversationAgents.map((agent) => (
                  <button
                    key={agent.id}
                    className="w-full flex items-center justify-between px-2 py-1.5 rounded text-sm text-primary-foreground/80 hover:bg-primary-foreground/10 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <div className="relative">
                        <Avatar className="h-5 w-5">
                          <AvatarImage src={agent.avatar} />
                          <AvatarFallback className="text-xs">{agent.name.slice(0, 2).toUpperCase()}</AvatarFallback>
                        </Avatar>
                        {agent.status === 'online' && (
                          <div className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-success border-2 border-primary" />
                        )}
                      </div>
                      <span className="truncate">{agent.name}</span>
                    </div>
                  </button>
                ))
              ) : (
                <p className="text-xs text-primary-foreground/60 px-2 py-2">No agents yet</p>
              )}
            </div>
          </div>
        </div>

        <div className="p-3 border-t border-primary-foreground/10">
          <div className="flex items-center gap-2">
            <Avatar className="h-8 w-8">
              <AvatarImage src="https://github.com/github.png" />
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

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="border-b bg-card sticky top-0 z-50">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
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
                  <h1 className="text-2xl font-bold tracking-tight">{conversationName}</h1>
                </div>
              </div>
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-7xl px-6 py-6 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-card border rounded-lg p-4">
                <div className="text-sm text-muted-foreground mb-1">Active Agents</div>
                <div className="text-3xl font-bold">{conversationAgents.filter(a => a.status !== 'offline').length}</div>
              </div>
              <div className="bg-card border rounded-lg p-4">
                <div className="text-sm text-muted-foreground mb-1">Running Tasks</div>
                <div className="text-3xl font-bold text-warning">{activeTasks.length}</div>
              </div>
              <div className="bg-card border rounded-lg p-4">
                <div className="text-sm text-muted-foreground mb-1">Completed</div>
                <div className="text-3xl font-bold text-success">{completedTasks.length}</div>
              </div>
              <div className="bg-card border rounded-lg p-4">
                <div className="text-sm text-muted-foreground mb-1">Open PRs</div>
                <div className="text-3xl font-bold text-info">{openPRs.length}</div>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">Agents</h2>
                <Badge variant="outline" className="text-xs">
                  {conversationAgents.length} total
                </Badge>
              </div>
              {conversationAgents && conversationAgents.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {conversationAgents.map(agent => (
                    <AgentCard
                      key={agent.id}
                      agent={agent}
                      task={getTaskForAgent(agent.id)}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 bg-muted/30 rounded-lg border-2 border-dashed">
                  <p className="text-muted-foreground mb-4">No agents in this conversation yet</p>
                </div>
              )}
            </div>

            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">Pull Requests</h2>
                <Badge variant="outline" className="text-xs">
                  {conversationPRs.length} total
                </Badge>
              </div>
              {conversationPRs && conversationPRs.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {conversationPRs.map(pr => (
                    <PRCard key={pr.id} pr={pr} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 bg-muted/30 rounded-lg border-2 border-dashed">
                  <p className="text-muted-foreground">No pull requests yet</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
