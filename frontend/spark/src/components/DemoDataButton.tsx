import { Button } from '@/components/ui/button'
import { useKV } from '@/shims/spark-hooks'
import type { Agent, Task, PullRequest, Conversation } from '@/lib/types'
import { toast } from 'sonner'

export function DemoDataButton() {
  const [, setConversations] = useKV<Conversation[]>('conversations', [])
  const [, setAgents] = useKV<Agent[]>('agents', [])
  const [, setTasks] = useKV<Task[]>('tasks', [])
  const [, setPullRequests] = useKV<PullRequest[]>('pullRequests', [])

  const loadDemoData = () => {
    const demoAgents: Agent[] = [
      {
        id: 'agent-1',
        name: 'Agent Alpha',
        shortName: 'alpha',
        avatar: 'https://api.dicebear.com/7.x/bottts/svg?seed=alpha',
        status: 'busy',
        provider: 'claude',
        model: 'claude-opus-4-5',
        personality: 'Tech Lead',
      },
      {
        id: 'agent-2',
        name: 'Agent Beta',
        shortName: 'beta',
        avatar: 'https://api.dicebear.com/7.x/bottts/svg?seed=beta',
        status: 'online',
        provider: 'openai',
        model: 'gpt-4o',
        personality: 'Software Developer',
      },
      {
        id: 'agent-3',
        name: 'Agent Gamma',
        shortName: 'gamma',
        avatar: 'https://api.dicebear.com/7.x/bottts/svg?seed=gamma',
        status: 'busy',
        provider: 'gemini',
        model: 'gemini-2.0-flash-exp',
        personality: 'DevOps Engineer',
      },
    ]

    const demoConversations: Conversation[] = [
      {
        id: 'conversation-1',
        name: 'Project Alpha',
        agents: demoAgents,
        tasks: [],
        pullRequests: [],
        createdAt: new Date(Date.now() - 86400000),
        updatedAt: new Date(),
      },
    ]

    const demoTasks: Task[] = [
      {
        id: 'task-1',
        agentId: 'agent-1',
        title: 'Refactor authentication module',
        description: 'Update OAuth implementation to use latest security standards',
        status: 'executing',
        progress: 65,
        startedAt: new Date(Date.now() - 3600000),
        phase: 'Implementation',
        prId: '234',
        subtasks: [
          { id: 'st-1', title: 'Update dependencies', completed: true },
          { id: 'st-2', title: 'Implement new flow', completed: true },
          { id: 'st-3', title: 'Write tests', completed: false },
        ],
      },
      {
        id: 'task-2',
        agentId: 'agent-2',
        title: 'Design new dashboard components',
        description: 'Create reusable components for the analytics dashboard',
        status: 'planning',
        progress: 25,
        startedAt: new Date(Date.now() - 1800000),
        phase: 'Design',
        subtasks: [
          { id: 'st-4', title: 'Sketch wireframes', completed: true },
          { id: 'st-5', title: 'Create component library', completed: false },
        ],
      },
      {
        id: 'task-3',
        agentId: 'agent-3',
        title: 'Optimize database queries',
        description: 'Improve performance of slow-running queries in production',
        status: 'reviewing',
        progress: 90,
        startedAt: new Date(Date.now() - 7200000),
        phase: 'Code Review',
        prId: '235',
        subtasks: [
          { id: 'st-6', title: 'Identify bottlenecks', completed: true },
          { id: 'st-7', title: 'Optimize queries', completed: true },
          { id: 'st-8', title: 'Address review comments', completed: false },
        ],
      },
      {
        id: 'task-4',
        agentId: 'agent-1',
        title: 'API documentation update',
        description: 'Update API docs with new endpoints',
        status: 'idle',
        progress: 0,
        startedAt: new Date(),
        phase: 'Pending',
        subtasks: [],
      },
      {
        id: 'task-5',
        agentId: 'agent-2',
        title: 'Mobile responsive fixes',
        description: 'Fix layout issues on mobile devices',
        status: 'completed',
        progress: 100,
        startedAt: new Date(Date.now() - 14400000),
        phase: 'Done',
        prId: '232',
        subtasks: [
          { id: 'st-9', title: 'Test on iOS', completed: true },
          { id: 'st-10', title: 'Test on Android', completed: true },
          { id: 'st-11', title: 'Merge PR', completed: true },
        ],
      },
    ]

    const demoPRs: PullRequest[] = [
      {
        id: 'pr-1',
        number: 234,
        title: 'feat: Update OAuth implementation with latest security standards',
        status: 'open',
        url: 'https://github.com/example/repo/pull/234',
        branch: 'feature/auth-refactor',
        author: 'Agent Alpha',
        createdAt: new Date(Date.now() - 3600000),
        updatedAt: new Date(Date.now() - 1800000),
        checks: [
          { name: 'Build', status: 'success' },
          { name: 'Unit Tests', status: 'success' },
          { name: 'E2E Tests', status: 'pending' },
          { name: 'Code Coverage', status: 'success' },
        ],
        reviewers: [
          { name: 'Tech Lead', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=tech', approved: false },
        ],
        hasConflicts: false,
        additions: 342,
        deletions: 128,
      },
      {
        id: 'pr-2',
        number: 235,
        title: 'perf: Optimize slow database queries in production',
        status: 'open',
        url: 'https://github.com/example/repo/pull/235',
        branch: 'perf/db-optimization',
        author: 'Agent Gamma',
        createdAt: new Date(Date.now() - 7200000),
        updatedAt: new Date(Date.now() - 900000),
        checks: [
          { name: 'Build', status: 'success' },
          { name: 'Unit Tests', status: 'success' },
          { name: 'Performance Tests', status: 'success' },
        ],
        reviewers: [
          { name: 'DB Admin', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=db', approved: true },
        ],
        hasConflicts: false,
        additions: 89,
        deletions: 203,
      },
      {
        id: 'pr-3',
        number: 232,
        title: 'fix: Mobile responsive layout issues',
        status: 'merged',
        url: 'https://github.com/example/repo/pull/232',
        branch: 'fix/mobile-responsive',
        author: 'Agent Beta',
        createdAt: new Date(Date.now() - 14400000),
        updatedAt: new Date(Date.now() - 3600000),
        checks: [
          { name: 'Build', status: 'success' },
          { name: 'Unit Tests', status: 'success' },
          { name: 'Visual Regression', status: 'success' },
        ],
        reviewers: [
          { name: 'Design Lead', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=design', approved: true },
        ],
        hasConflicts: false,
        additions: 156,
        deletions: 87,
      },
    ]

    setConversations(demoConversations)
    setAgents(demoAgents)
    setTasks(demoTasks)
    setPullRequests(demoPRs)
    toast.success('Demo data loaded successfully!')
  }

  return (
    <Button onClick={loadDemoData} variant="outline" size="sm" className="w-full">
      Load Demo Data
    </Button>
  )
}
