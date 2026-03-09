export type TaskStatus = 'idle' | 'planning' | 'executing' | 'reviewing' | 'completed' | 'failed' | 'blocked'

export type PRStatus = 'open' | 'merged' | 'closed' | 'draft'

export type CheckStatus = 'pending' | 'success' | 'failure' | 'queued'

export interface Agent {
  id: string
  name: string
  shortName: string
  avatar: string
  status: 'online' | 'offline' | 'busy'
  currentTask?: Task
  provider?: string
  model?: string
  personality?: string
}

export interface Task {
  id: string
  agentId: string
  title: string
  description: string
  status: TaskStatus
  progress: number
  startedAt: Date
  estimatedCompletion?: Date
  prId?: string
  phase: string
  subtasks: Subtask[]
}

export interface Subtask {
  id: string
  title: string
  completed: boolean
}

export interface PullRequest {
  id: string
  number: number
  title: string
  status: PRStatus
  url: string
  branch: string
  author: string
  createdAt: Date
  updatedAt: Date
  checks: Check[]
  reviewers: Reviewer[]
  hasConflicts: boolean
  additions: number
  deletions: number
}

export interface Check {
  name: string
  status: CheckStatus
  conclusion?: 'success' | 'failure' | 'cancelled'
  url?: string
}

export interface Reviewer {
  name: string
  avatar: string
  approved: boolean
}

export interface Conversation {
  id: string
  name: string
  agents: Agent[]
  tasks: Task[]
  pullRequests: PullRequest[]
  createdAt: Date
  updatedAt: Date
}

export interface BatchIntelligence {
  id: string
  batchName: string
  executedAt: Date
  agreementMap: AgreementData[]
  conflictMap: ConflictData[]
  neutralMemos: string[]
  summary: string
}

export interface AgreementData {
  topic: string
  agreementLevel: number
  participants: string[]
}

export interface ConflictData {
  topic: string
  conflictLevel: number
  positions: { agent: string; position: string }[]
}
