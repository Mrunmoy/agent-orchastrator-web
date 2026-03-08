import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu'
import { Hash, Bell, MagnifyingGlass, Gear, ChartBar, Plus, At, DotsThree, Trash, PaperPlaneTilt } from '@phosphor-icons/react'
import { motion } from 'framer-motion'
import { DemoDataButton } from '@/components/DemoDataButton'
import { ConversationDetails } from '@/components/ConversationDetails'
import { useKV } from '@/shims/spark-hooks'
import { useAgentActivitySimulation } from '@/hooks/use-agent-activity-simulation'
import type { Conversation, Agent, Task } from '@/lib/types'
import { toast } from 'sonner'
import { Toaster } from '@/components/ui/sonner'
import { providerModels, personalities } from '@/lib/models'

interface MainAppProps {
  onNavigateToDashboard: (conversationId: string) => void
}

interface Message {
  id: string
  senderId: string
  senderName: string
  senderAvatar: string
  senderType: 'user' | 'agent'
  timestamp: string
  content: string
  isDM?: boolean
  recipientId?: string
}

export function MainApp({ onNavigateToDashboard }: MainAppProps) {
  const [conversations, setConversations] = useKV<Conversation[]>('conversations', [])
  const [agents, setAgents] = useKV<Agent[]>('agents', [])
  const [tasks, setTasks] = useKV<Task[]>('tasks', [])
  const [messages, setMessages] = useKV<Record<string, Message[]>>('messages', {})
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null)
  const [newConversationName, setNewConversationName] = useState('')
  const [newAgentName, setNewAgentName] = useState('')
  const [newAgentShortName, setNewAgentShortName] = useState('')
  const [newAgentProvider, setNewAgentProvider] = useState('claude')
  const [newAgentModel, setNewAgentModel] = useState('claude-opus-4-5')
  const [newAgentPersonality, setNewAgentPersonality] = useState('Software Developer')
  const [isAddConversationOpen, setIsAddConversationOpen] = useState(false)
  const [isAddAgentOpen, setIsAddAgentOpen] = useState(false)
  const [messageInput, setMessageInput] = useState('')
  const [availableModels, setAvailableModels] = useState<string[]>(providerModels.claude)
  const [showMentionSuggestions, setShowMentionSuggestions] = useState(false)
  const [mentionSearch, setMentionSearch] = useState('')

  useAgentActivitySimulation(true)

  useEffect(() => {
    if (!activeConversationId && conversations && conversations.length > 0) {
      setActiveConversationId(conversations[0].id)
    }
  }, [conversations, activeConversationId])

  useEffect(() => {
    const models = providerModels[newAgentProvider as keyof typeof providerModels] || []
    setAvailableModels(models)
    if (models.length > 0) {
      setNewAgentModel(models[0])
    }
  }, [newAgentProvider])

  const activeConversation = conversations?.find(c => c.id === activeConversationId)
  
  const conversationAgentIds = activeConversation?.agents.map(a => a.id) || []
  const conversationAgents = agents?.filter(a => conversationAgentIds.includes(a.id)) || []
  const conversationTasks = tasks?.filter(t => conversationAgentIds.includes(t.agentId)) || []

  const conversationMessages = activeConversationId ? (messages?.[activeConversationId] || []) : []

  const handleAddConversation = () => {
    if (!newConversationName.trim()) {
      toast.error('Please enter a conversation name')
      return
    }

    const newConversation: Conversation = {
      id: `conversation-${Date.now()}`,
      name: newConversationName,
      agents: [],
      tasks: [],
      pullRequests: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    }

    setConversations((current) => [...(current || []), newConversation])
    setActiveConversationId(newConversation.id)
    setNewConversationName('')
    setIsAddConversationOpen(false)
    toast.success(`Created conversation: ${newConversationName}`)
  }

  const handleAddAgent = () => {
    if (!newAgentName.trim()) {
      toast.error('Please enter an agent name')
      return
    }

    if (!newAgentShortName.trim()) {
      toast.error('Please enter an agent short name')
      return
    }

    if (!activeConversationId) {
      toast.error('Please select a conversation first')
      return
    }

    const shortNameExists = agents?.some(a => a.shortName?.toLowerCase() === newAgentShortName.toLowerCase())
    if (shortNameExists) {
      toast.error('Short name already in use')
      return
    }

    const newAgent: Agent = {
      id: `agent-${Date.now()}`,
      name: newAgentName,
      shortName: newAgentShortName,
      avatar: `https://api.dicebear.com/7.x/bottts/svg?seed=${newAgentName}`,
      status: 'online',
      provider: newAgentProvider,
      model: newAgentModel,
      personality: newAgentPersonality,
    }

    setAgents((current) => [...(current || []), newAgent])
    
    setConversations((current) =>
      (current || []).map(conv =>
        conv.id === activeConversationId
          ? { ...conv, agents: [...conv.agents, newAgent], updatedAt: new Date() }
          : conv
      )
    )

    setNewAgentName('')
    setNewAgentShortName('')
    setNewAgentProvider('claude')
    setNewAgentModel('claude-opus-4-5')
    setNewAgentPersonality('Software Developer')
    setIsAddAgentOpen(false)
    toast.success(`Added agent: ${newAgentName}`)
  }

  const handleDeleteConversation = (conversationId: string) => {
    const conversation = conversations?.find(c => c.id === conversationId)
    if (!conversation) return

    setConversations((current) => (current || []).filter(c => c.id !== conversationId))
    
    if (activeConversationId === conversationId) {
      const remaining = (conversations || []).filter(c => c.id !== conversationId)
      setActiveConversationId(remaining.length > 0 ? remaining[0].id : null)
    }

    toast.success(`Deleted conversation: ${conversation.name}`)
  }

  const handleDeleteAgent = (agentId: string) => {
    const agent = agents?.find(a => a.id === agentId)
    if (!agent) return

    setAgents((current) => (current || []).filter(a => a.id !== agentId))
    
    setConversations((current) =>
      (current || []).map(conv => ({
        ...conv,
        agents: conv.agents.filter(a => a.id !== agentId),
        updatedAt: new Date(),
      }))
    )

    toast.success(`Deleted agent: ${agent.name}`)
  }

  const handleSendMessage = async () => {
    if (!messageInput.trim() || !activeConversationId) return

    // SHIMMED: was window.spark.user() — replace with actual user context
    const user = { id: 1, login: 'You', avatarUrl: '' }
    
    const newMessage: Message = {
      id: `message-${Date.now()}`,
      senderId: user?.id.toString() || 'unknown',
      senderName: user?.login || 'You',
      senderAvatar: user?.avatarUrl || 'https://github.com/github.png',
      senderType: 'user',
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      content: messageInput,
    }

    setMessages((current) => ({
      ...(current || {}),
      [activeConversationId]: [...(current?.[activeConversationId] || []), newMessage],
    }))

    setMessageInput('')
    toast.success('Message sent!')
  }

  const activeConversationName = activeConversation?.name || 'Select a conversation'

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <Toaster />
      
      <aside className="w-64 bg-primary text-primary-foreground flex flex-col border-r">
        <div className="p-4 border-b border-primary-foreground/10">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-lg font-bold">Agent Workspace</h1>
            <Button variant="ghost" size="icon" className="h-8 w-8 text-primary-foreground hover:bg-primary-foreground/10">
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
            <DemoDataButton />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="p-3">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-xs font-semibold uppercase tracking-wide opacity-70">Conversations</h2>
              <Dialog open={isAddConversationOpen} onOpenChange={setIsAddConversationOpen}>
                <DialogTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-5 w-5 text-primary-foreground/70 hover:bg-primary-foreground/10">
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
                          if (e.key === 'Enter') {
                            handleAddConversation()
                          }
                        }}
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setIsAddConversationOpen(false)}>
                      Cancel
                    </Button>
                    <Button onClick={handleAddConversation}>Create</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
            <div className="space-y-0.5">
              {conversations && conversations.length > 0 ? (
                conversations.map((conversation) => (
                  <div
                    key={conversation.id}
                    className={`w-full flex items-center justify-between px-2 py-1.5 rounded text-sm transition-colors group ${
                      activeConversationId === conversation.id
                        ? 'bg-accent/20 text-primary-foreground font-medium'
                        : 'text-primary-foreground/80 hover:bg-primary-foreground/10'
                    }`}
                  >
                    <button
                      onClick={() => setActiveConversationId(conversation.id)}
                      className="flex items-center gap-2 flex-1 text-left"
                    >
                      <Hash size={16} />
                      <span className="truncate">{conversation.name}</span>
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
                          onClick={() => handleDeleteConversation(conversation.id)}
                        >
                          <Trash size={14} className="mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                ))
              ) : (
                <p className="text-xs text-primary-foreground/60 px-2 py-2">No conversations yet</p>
              )}
            </div>
          </div>

          <div className="p-3 border-t border-primary-foreground/10">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-xs font-semibold uppercase tracking-wide opacity-70">Direct Messages</h2>
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
                          onChange={(e) => setNewAgentShortName(e.target.value.replace('@', '').toLowerCase())}
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="agent-personality">Personality</Label>
                        <Select value={newAgentPersonality} onValueChange={setNewAgentPersonality}>
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
                        <Select value={newAgentProvider} onValueChange={setNewAgentProvider}>
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
                    <Button variant="outline" onClick={() => setIsAddAgentOpen(false)}>
                      Cancel
                    </Button>
                    <Button onClick={handleAddAgent}>Save Agent</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
            <div className="space-y-0.5">
              {conversationAgents && conversationAgents.length > 0 ? (
                conversationAgents.map((agent) => (
                  <div
                    key={agent.id}
                    className="w-full flex items-center justify-between px-2 py-1.5 rounded text-sm text-primary-foreground/80 hover:bg-primary-foreground/10 transition-colors group"
                  >
                    <div className="flex items-center gap-2 flex-1">
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
                          onClick={() => handleDeleteAgent(agent.id)}
                        >
                          <Trash size={14} className="mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
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

      <div className="flex-1 flex flex-col">
        <header className="h-14 border-b bg-card flex items-center justify-between px-4">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Hash size={20} className="text-muted-foreground" />
              <h2 className="font-semibold text-lg">{activeConversationName}</h2>
            </div>
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
              <div className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-accent" />
            </Button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {activeConversation ? (
            <>
              {conversationMessages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex gap-3 hover:bg-muted/30 -mx-2 px-2 py-2 rounded"
                >
                  <Avatar className="h-10 w-10">
                    <AvatarImage src={message.senderAvatar || 'https://github.com/github.png'} />
                    <AvatarFallback>{(message.senderName || 'UN').slice(0, 2).toUpperCase()}</AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-baseline gap-2 mb-1">
                      <span className="font-semibold text-sm">{message.senderName || 'Unknown'}</span>
                      <span className="text-xs text-muted-foreground">{message.timestamp}</span>
                    </div>
                    <p className="text-sm">{message.content}</p>
                  </div>
                </motion.div>
              ))}

              {conversationMessages.length === 0 && (
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
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSendMessage()
                }
              }}
              disabled={!activeConversation}
            />
            <Button 
              size="icon" 
              className="bg-accent hover:bg-accent/90 text-accent-foreground"
              onClick={handleSendMessage}
              disabled={!activeConversation || !messageInput.trim()}
            >
              <PaperPlaneTilt size={18} weight="fill" />
            </Button>
          </div>
        </div>
      </div>

      <ConversationDetails 
        conversation={activeConversation || null}
        agents={agents || []}
        tasks={tasks || []}
      />
    </div>
  )
}
