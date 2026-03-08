# UI Implementation Brief for Copilot Spark

## Project Overview

Multi-agent orchestration web app — an engineering cockpit for running AI coding agents (Claude, Codex, Ollama) in structured workflows. Think: Slack meets Linear meets a terminal. The UI manages conversations where multiple AI agents debate, plan, code, review, and merge — all orchestrated with customer steering.

**Tech stack:** React 19, TypeScript, Vite, CSS (no Tailwind — custom CSS with CSS variables).

---

## Layout Architecture

Four-zone layout, persistent across views:

```
┌──────────────────────────────────────────────────────────┐
│                        TopBar                             │
├─────────────┬─────────────────────────┬──────────────────┤
│             │                         │                  │
│  History    │      Center Pane        │  Intelligence    │
│  Pane       │   (Chat or Dashboard)   │  Pane            │
│  (sidebar)  │                         │  (Roster or      │
│             │                         │   Activity)      │
│             │                         │                  │
├─────────────┴─────────────────────────┴──────────────────┤
│               Bottom Controls (Composer)                  │
└──────────────────────────────────────────────────────────┘
```

- **HistoryPane** (left, ~240px): Conversation list, create button, search
- **Center Pane**: Toggles between Chat View and Dashboard View
- **IntelligencePane** (right, ~300px): Agent roster OR activity viewer (per-agent)
- **BottomControls**: Composer bar that spans the center pane

---

## Views & Components

### 1. Chat View (Center Pane — default)

The primary conversation interface. Messages from customer, agents, and system.

**Message types with distinct rendering:**
- **Agent message**: Avatar (hash-based HSL color from agent ID), agent name + role badge (e.g. "Analyst", "Team Lead"), markdown-rendered body, timestamp
- **Customer message**: Right-aligned or distinct style, "You" label
- **System notice**: Muted inline banner (phase changes, gate approvals, merge events)
- **Debate turn**: Like agent message but with round indicator badge ("Round 3/20")
- **Steer message**: Customer message with highlight border (amber/gold), indicates steering
- **Phase divider**: Full-width horizontal divider with phase name ("Design Debate", "Execution")

**Phase banner** (sticky at top of chat):
- Shows current phase name + round counter: "Design Debate — Round 5/20"
- Hidden when no active phase

**Speaking indicator** (above composer):
- Shows which agent is currently generating: avatar + name + animated dots
- Hidden when no agent is active

**Clarification banner** (amber):
- Appears when an agent asks the customer a question (@Customer mention)
- "Agent X needs your input" with "Scroll to question" button

**Gate controls** (appear during phase transitions):
- Three buttons: "Approve & Advance", "Steer", "Decide"
- Appear when gate_status is pending_approval

**Auto-scroll behavior:**
- When at bottom: new messages auto-scroll into view
- When scrolled up: floating "New messages (N)" badge at bottom, click to jump down

### 2. Dashboard View (Center Pane — toggled)

Kanban board for project status.

**Columns** (horizontal scroll):
```
Todo | Design | TDD | Implementing | Testing | PR Raised | In Review | Fixing Comments | Merging | Done
```

Each column:
- Header with status name + task count badge
- Empty columns shown but dimmed
- Cards stack vertically within column

**Task Card:**
- Title (truncated with tooltip on hover)
- Agent badge: small avatar circle + agent name (color-coded by agent)
- Status accent: left border color per status (green for done, blue for implementing, etc.)
- PR link: clickable "#42" badge if PR exists
- Reviewer badge if assigned
- Click opens Task Detail Modal

**Task Detail Modal** (overlay):
- Full title, status badge, priority badge (P0/P1/P2 with colors)
- Markdown description
- Scope: file list
- Dependencies: list with status indicators (green check if done, grey if pending)
- PR section: number, URL, CI status (pass/fail/pending), review status
- Assigned agent link
- Activity log (filtered to this task)

**Agent Status Bar** (compact strip, above or below kanban):
- Each agent as a pill: status dot (green=idle, blue=running, red=error, grey=offline) + name + current task title
- Click opens activity viewer in right pane

**Merge Queue Display** (panel, below kanban or in sidebar):
- Ordered list of PRs waiting to merge
- Each entry: position number, status icon, PR number, task title, author agent name
- Currently-merging PR highlighted

### 3. Composer (Bottom Controls)

Message input that spans the center pane.

**Features:**
- Textarea with auto-resize (min 1 line, max ~6 lines)
- **@mention autocomplete**: typing "@" opens a dropdown of agents in the conversation, filtered as user types. Arrow keys to navigate, Enter/click to select. Inserts "@AgentName" styled as a chip/tag.
- Send button (or Enter to send, Shift+Enter for newline)
- When debate is running: show Run/Stop/Continue controls next to send

### 4. History Pane (Left Sidebar)

Conversation list.

- "New Conversation" button at top
- List of conversations: title, last activity time, phase badge, unread indicator
- Active conversation highlighted
- Click to switch conversations
- Search/filter input

### 5. Intelligence Pane (Right Sidebar)

Two states, toggled:

**State A — Agent Roster (default):**
- List of agents in the conversation
- Each agent row: avatar (color-coded), name, provider badge ("Claude"/"Codex"/"Ollama"), role badge ("Analyst"/"Developer"/"Team Lead"), status dot, current task
- "Add Agent" button with form (name, provider dropdown, model, personality)
- Drag to reorder (turn order)
- Click agent row → switches to Activity Viewer

**State B — Activity Viewer:**
- Terminal-like aesthetic: dark background (#0a0e1a), monospace font, colored text
- "Back to Roster" button at top
- Agent name + status in header
- Scrolling event stream with distinct styling per event type:
  - **thinking**: dimmed italic text, grey
  - **text**: normal white text
  - **tool_call**: highlighted with tool name badge (cyan/blue), command shown
  - **tool_result**: indented under tool_call, slightly muted
  - **file_edit**: filename in green, diff snippet (red/green lines)
  - **shell_command**: `$ command` in yellow, output below
  - **error**: red text, error icon
- Auto-scrolls to bottom; when user scrolls up, "Resume" button appears

### 6. Toast Notifications (Top-right corner)

Stack of notification toasts:
- **clarification** (amber): "Agent X needs your input"
- **max_rounds** (yellow): "Debate reached round limit"
- **pr_ready** (blue): "PR #42 ready for review"
- **agent_blocked** (red): "Agent Y is blocked — merge conflict"

Each toast: icon + message + close button. Auto-dismiss after 8 seconds. Clickable (navigates to relevant context).

### 7. TopBar

- App title/logo (left)
- View switcher: "Chat" | "Dashboard" tabs (center)
- Connection status indicator (green dot when SSE connected)
- Settings/config gear icon (right)

---

## Design Theme

Engineering cockpit aesthetic — dark, professional, information-dense.

**Color palette:**
```css
--bg: #0a0e1a;          /* App background */
--surface: #111827;      /* Card/panel background */
--surface2: #1e293b;     /* Elevated surface */
--border: #1e293b;       /* Borders */
--text: #e2e8f0;         /* Primary text */
--text-muted: #94a3b8;   /* Secondary text */
--accent: #818cf8;       /* Primary accent (indigo) */
--accent2: #a78bfa;      /* Secondary accent (violet) */
--green: #34d399;        /* Success, idle, done */
--yellow: #fbbf24;       /* Warning, pending */
--red: #f87171;          /* Error, blocked */
--blue: #60a5fa;         /* Info, running */
--cyan: #22d3ee;         /* Code, identifiers */
--orange: #fb923c;       /* Attention */
```

**Typography:**
- UI text: Inter or system sans-serif
- Code/terminal: JetBrains Mono or system monospace
- Agent names: semi-bold
- Timestamps: small, muted

**Agent colors:** Each agent gets a deterministic accent color derived from hashing their ID to an HSL hue (fixed saturation 65%, lightness 60%). Used for avatar background, message left-border accent, task card badges.

**Borders:** 1px solid, subtle. Cards have 8px border-radius. Hover states lighten borders.

---

## Mock Data

Use this mock data structure for all components:

```typescript
// Conversation
interface Conversation {
  id: string;
  title: string;
  phase: 'debate' | 'task_planning' | 'execution' | 'review' | 'merge' | 'done';
  gate_status: 'open' | 'pending_approval' | 'approved' | 'rejected';
  created_at: string;
  updated_at: string;
}

// Agent
interface Agent {
  id: string;
  name: string;
  provider: 'claude' | 'codex' | 'ollama';
  model: string;
  role: 'analyst' | 'developer' | 'team_lead';
  personality: string;
  status: 'idle' | 'running' | 'error' | 'offline';
  current_task_id?: string;
  turn_order: number;
}

// Message
interface Message {
  id: string;
  conversation_id: string;
  source_type: 'customer' | 'agent' | 'system';
  source_id?: string;           // agent ID if source_type is 'agent'
  event_type: 'chat_message' | 'debate_turn' | 'phase_change' | 'system_notice' | 'steer';
  body: string;                 // markdown text
  metadata?: {
    round?: number;
    max_rounds?: number;
    target_agent_id?: string;
    phase?: string;
  };
  created_at: string;
}

// Task
interface Task {
  id: string;
  title: string;
  description: string;          // markdown
  status: 'todo' | 'design' | 'tdd' | 'implementing' | 'testing' | 'pr_raised' | 'in_review' | 'fixing_comments' | 'merging' | 'done' | 'blocked';
  priority: 'P0' | 'P1' | 'P2';
  owner_agent_id?: string;
  reviewer_agent_id?: string;
  pr_number?: number;
  pr_url?: string;
  depends_on: string[];         // task IDs
  scope_files: string[];
}

// Merge Queue Entry
interface MergeQueueEntry {
  id: string;
  task_id: string;
  pr_number: number;
  pr_branch: string;
  author_agent_id: string;
  reviewer_agent_id?: string;
  position: number;
  status: 'queued' | 'rebasing' | 'testing' | 'merging' | 'merged' | 'failed' | 'blocked';
}

// Activity Event (for Activity Viewer)
interface ActivityEvent {
  type: 'thinking' | 'text' | 'tool_call' | 'tool_result' | 'file_edit' | 'shell_command' | 'error';
  content: string;
  metadata?: Record<string, unknown>;
  timestamp: string;
}

// Toast
interface Toast {
  id: string;
  type: 'clarification' | 'max_rounds' | 'pr_ready' | 'agent_blocked';
  message: string;
  agent_id?: string;
  dismissAt: number;  // ms from now
}
```

**Sample mock data to populate the UI:**

```typescript
const MOCK_AGENTS: Agent[] = [
  { id: 'a1', name: 'Aria', provider: 'claude', model: 'opus-4', role: 'analyst', personality: 'Methodical architect', status: 'running', current_task_id: 't3', turn_order: 1 },
  { id: 'a2', name: 'Bolt', provider: 'codex', model: 'codex-1', role: 'developer', personality: 'Fast implementer', status: 'idle', turn_order: 2 },
  { id: 'a3', name: 'Nova', provider: 'claude', model: 'sonnet-4', role: 'developer', personality: 'Test-driven craftsman', status: 'running', current_task_id: 't5', turn_order: 3 },
  { id: 'a4', name: 'Sentinel', provider: 'ollama', model: 'llama3', role: 'team_lead', personality: 'Coordinator', status: 'idle', turn_order: 0 },
];

const MOCK_TASKS: Task[] = [
  { id: 't1', title: 'Database schema v4 migration', status: 'done', priority: 'P0', owner_agent_id: 'a2', depends_on: [], scope_files: ['backend/storage/schema.sql'], description: 'Add merge_queue table...' },
  { id: 't2', title: 'Message event CRUD API', status: 'done', priority: 'P0', owner_agent_id: 'a3', depends_on: ['t1'], scope_files: ['backend/api/routes/messages.py'], description: 'POST/GET endpoints...' },
  { id: 't3', title: 'SSE streaming infrastructure', status: 'implementing', priority: 'P0', owner_agent_id: 'a1', depends_on: ['t2'], scope_files: ['backend/api/routes/streaming.py'], description: 'EventSource endpoints...', pr_number: undefined },
  { id: 't4', title: 'Chat message components', status: 'pr_raised', priority: 'P0', owner_agent_id: 'a2', reviewer_agent_id: 'a3', pr_number: 42, pr_url: '#', depends_on: [], scope_files: ['frontend/src/features/chat/'], description: 'Message variants...' },
  { id: 't5', title: 'Kanban board', status: 'implementing', priority: 'P1', owner_agent_id: 'a3', depends_on: [], scope_files: ['frontend/src/features/dashboard/'], description: 'Dashboard columns...' },
  { id: 't6', title: '@mention autocomplete', status: 'todo', priority: 'P1', depends_on: [], scope_files: ['frontend/src/features/composer/'], description: 'Composer enhancement...' },
  { id: 't7', title: 'Debate turn manager', status: 'design', priority: 'P0', owner_agent_id: 'a1', depends_on: ['t1'], scope_files: ['backend/orchestrator/debate.py'], description: 'Round-robin engine...' },
  { id: 't8', title: 'Phase gate state machine', status: 'tdd', priority: 'P0', owner_agent_id: 'a2', depends_on: [], scope_files: ['backend/orchestrator/phase_gate.py'], description: 'Phase transitions...' },
  { id: 't9', title: 'Merge queue manager', status: 'in_review', priority: 'P0', owner_agent_id: 'a3', reviewer_agent_id: 'a1', pr_number: 45, pr_url: '#', depends_on: ['t1'], scope_files: ['backend/orchestrator/merge_queue.py'], description: 'FIFO queue...' },
  { id: 't10', title: 'Toast notification system', status: 'testing', priority: 'P1', owner_agent_id: 'a2', depends_on: [], scope_files: ['frontend/src/features/notifications/'], description: 'In-app toasts...' },
];

const MOCK_MERGE_QUEUE: MergeQueueEntry[] = [
  { id: 'mq1', task_id: 't4', pr_number: 42, pr_branch: 'claude/chat-messages', author_agent_id: 'a2', reviewer_agent_id: 'a3', position: 1, status: 'testing' },
  { id: 'mq2', task_id: 't9', pr_number: 45, pr_branch: 'claude/merge-queue', author_agent_id: 'a3', reviewer_agent_id: 'a1', position: 2, status: 'queued' },
];
```

---

## Key Interactions

1. **View toggle**: Click "Chat"/"Dashboard" in TopBar → center pane switches, sidebar + right pane persist
2. **Send message**: Type in composer → Enter sends → message appears in timeline → agent responds (SSE)
3. **@mention**: Type "@" → dropdown appears → select agent → "@AgentName" inserted → message directed to that agent
4. **Agent activity**: Click agent in roster → right pane shows ActivityViewer → "Back to Roster" returns
5. **Task detail**: Click task card in kanban → modal opens with full details
6. **Phase gate**: When debate concludes → gate controls appear → customer clicks "Approve" → next phase
7. **Toast**: Event occurs (PR ready, agent blocked) → toast slides in from top-right → auto-dismisses or click to navigate
8. **New conversation**: Click "+" in sidebar → form for title + project path → new conversation created

---

## File References

For full details, refer to these files in the repo:

- **UI Requirements (30 reqs):** `docs/requirements/data/02-ui-ux.json`
- **Chat & Debate UI Design:** `docs/design/data/03-chat-debate-ui.json`
- **Dashboard & Activity Design:** `docs/design/data/04-dashboard-activity.json`
- **Product Requirements:** `docs/requirements/data/01-product.json`
- **Existing frontend code:** `frontend/src/` (React 19 + Vite, existing layout in `frontend/src/layout/`)
