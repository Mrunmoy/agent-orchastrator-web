# Planning Guide

A Slack-themed Agent Workspace with conversation-scoped Agent Orchestrator Dashboard that provides real-time visibility into AI agent tasks, execution status, and PR lifecycle management per conversation.

**Experience Qualities**: 
1. **Command Center Feel** - Users should feel like they're operating a mission control center, with clear visibility into all ongoing agent activities and their real-time status updates within a specific conversation context.
2. **Effortless Monitoring** - Information should be scannable at a glance with visual hierarchies that instantly communicate urgency, progress, and completion states for the active conversation.
3. **Developer-Friendly** - The interface should speak the language of developers with familiar concepts like PRs, commits, branches, and build statuses presented in an intuitive way.

**Complexity Level**: Complex Application (advanced functionality, likely with multiple views)
This is a sophisticated monitoring and orchestration platform that manages multiple conversations, each with their own agents and tasks. It integrates with GitHub PR workflows and provides conversation-scoped analytics. It requires state management across views, real-time status updates, and detailed drill-down capabilities.

## Essential Features

### Slack-Themed Main Workspace
- **Functionality**: Primary landing page mimicking Slack's interface with conversations (projects), direct messages to agents, and a conversational feed
- **Purpose**: Provides a familiar, communication-focused environment for monitoring agent activities through messages and notifications
- **Trigger**: Application loads to this view by default
- **Progression**: Load app → View conversations and DMs → See agent messages → Select a conversation → Click "Agent Dashboard" button → Navigate to conversation-scoped dashboard
- **Success criteria**: Slack-like interface with conversations, direct messages, and message feed; quick stats card shows overview for active conversation; smooth navigation to dashboard

### Conversation Management
- **Functionality**: Users can create and manage multiple conversations (projects), each with its own set of agents and tasks
- **Purpose**: Organize work into isolated contexts where each conversation represents a distinct project or workstream
- **Trigger**: User views conversation list in sidebar
- **Progression**: View conversation list → Select conversation → See conversation-specific messages → Navigate to dashboard for that conversation's agents and tasks
- **Success criteria**: Conversations are clearly distinguished; switching between conversations updates the view; each conversation maintains its own state

### Conversation-Scoped Dashboard
- **Functionality**: Dashboard displays only agents, tasks, and PRs belonging to the currently selected conversation
- **Purpose**: Provides focused visibility into work happening within a specific conversation/project context
- **Trigger**: Click "Agent Dashboard" button from main workspace
- **Progression**: Main workspace → Select conversation → Click dashboard button → View agents and tasks for this conversation only → Click back arrow → Return to main workspace
- **Success criteria**: Dashboard shows only relevant data for selected conversation; navigation preserves conversation context; clean transition between views

### Agent Task Board
- **Functionality**: Display all agents assigned to the current conversation with their tasks, progress indicators, and status badges
- **Purpose**: Provides immediate visibility into what each agent in this conversation is working on and their current state
- **Trigger**: Automatically loads on dashboard mount; filters by conversation; updates in real-time as agent states change
- **Progression**: Dashboard loads for conversation → Agent cards render with current tasks → Status indicators show progress → Task details visible
- **Success criteria**: All conversation agents visible with accurate task assignments; status updates reflect within 2 seconds of state changes; agents from other conversations are not shown

### Direct Messages Panel
- **Functionality**: Sidebar panel showing all agents available for direct messaging, allowing 1-on-1 communication for steering or guidance
- **Purpose**: Enables direct interaction with individual agents for debugging, guidance, or status updates
- **Trigger**: Always visible in sidebar on both main workspace and dashboard
- **Progression**: View agent list → Click agent → Open chat interface → Send messages → Receive responses
- **Success criteria**: Agent list shows online status; chat opens instantly; message history persists; typing indicators work

### Task Status Tracking
- **Functionality**: Hierarchical view of tasks showing current phase (planning, execution, review), progress percentage, and time tracking
- **Purpose**: Allows users to understand task progression and identify bottlenecks or stalled work
- **Trigger**: Selecting a specific agent or viewing the main task list
- **Progression**: Select task → View detailed breakdown → See substeps and dependencies → Monitor progress metrics → Identify blockers
- **Success criteria**: Task progress accurately reflects agent activity; phase transitions are clearly indicated; time estimates are displayed

### PR Status Integration
- **Functionality**: Real-time GitHub PR status display showing open/merged/closed state, review status, CI/CD pipeline results, and merge conflicts for the current conversation
- **Purpose**: Connects agent work to actual code delivery within the conversation context, showing the full lifecycle from task to deployed code
- **Trigger**: Agent in conversation completes code generation task; PR is created or updated
- **Progression**: Agent creates PR → Dashboard shows PR card → Display review requests → Show CI status → Indicate merge readiness → Track merge completion
- **Success criteria**: PR status syncs with GitHub within 5 seconds; all PR metadata (reviewers, checks, conflicts) is visible; clickable links to GitHub; only PRs from conversation agents are shown

## Edge Case Handling

- **No Active Agents**: Display empty state with "Add New Agent" CTA and helpful onboarding message
- **Failed API Calls**: Show error toasts with retry buttons; maintain cached data until refresh succeeds
- **Long-Running Tasks**: Display "estimated time remaining" and allow users to cancel/pause tasks
- **Merge Conflicts**: Highlight conflicted PRs with red indicators and provide conflict resolution guidance
- **Network Loss**: Queue status updates locally; sync when connection restored; show offline indicator
- **Concurrent Edits**: Implement optimistic UI updates with rollback on conflict detection
- **Missing PR Data**: Gracefully handle deleted or inaccessible PRs with appropriate fallback UI

## Design Direction

The design should evoke the feeling of a **sophisticated developer command center** - merging Slack's conversational warmth with the precision of a technical dashboard. It should feel like a tool built by developers, for developers, with attention to detail that suggests both power and ease of use. The interface should breathe confidence through its use of space, clear typography, and purposeful color coding that instantly communicates status without requiring mental translation.

## Color Selection

The color scheme builds on Slack's deep purple foundation while introducing vibrant status indicators that create instant visual recognition.

- **Primary Color**: `oklch(0.35 0.12 285)` - Deep Purple - Establishes the authoritative, focused feel of a command center; used for primary navigation and key headings
- **Secondary Colors**: 
  - `oklch(0.25 0.08 285)` - Darker Purple - Sidebar and panel backgrounds creating depth
  - `oklch(0.92 0.02 285)` - Light Purple Tint - Subtle hover states and secondary panels
- **Accent Color**: `oklch(0.75 0.18 145)` - Vibrant Green - Success states, completed tasks, merged PRs, and primary CTAs; signals positive outcomes
- **Status Colors**:
  - Success: `oklch(0.75 0.18 145)` - Green for completed/merged
  - Warning: `oklch(0.85 0.15 85)` - Amber for in-progress/pending review
  - Error: `oklch(0.65 0.22 25)` - Coral Red for failed/blocked
  - Info: `oklch(0.65 0.18 235)` - Blue for informational states
- **Foreground/Background Pairings**: 
  - Primary Background (Deep Purple `oklch(0.35 0.12 285)`): White text `oklch(0.98 0 0)` - Ratio 7.2:1 ✓
  - Card Background (Light Gray `oklch(0.97 0 0)`): Dark text `oklch(0.25 0.02 285)` - Ratio 11.5:1 ✓
  - Accent Green (`oklch(0.75 0.18 145)`): Dark text `oklch(0.2 0.05 285)` - Ratio 7.8:1 ✓
  - Warning Amber (`oklch(0.85 0.15 85)`): Dark text `oklch(0.25 0.02 285)` - Ratio 9.1:1 ✓

## Font Selection

Typography should balance technical precision with approachable readability, using fonts that feel modern and developer-friendly while maintaining excellent legibility at all sizes.

- **Primary Font**: **Space Grotesk** - A geometric sans-serif with a technical yet friendly character; perfect for headings and labels
- **Secondary Font**: **Inter** - Clean, highly legible sans-serif for body text and data displays

**Typographic Hierarchy**:
- H1 (App Title): Space Grotesk Bold / 24px / tight letter-spacing (-0.02em)
- H2 (Section Headers): Space Grotesk SemiBold / 18px / normal letter-spacing
- H3 (Card Titles): Space Grotesk Medium / 16px / normal letter-spacing
- Body (General Text): Inter Regular / 14px / normal letter-spacing
- Small (Metadata): Inter Regular / 12px / slightly wide letter-spacing (0.01em)
- Code/Monospace: JetBrains Mono / 13px / used for PR numbers, commit hashes

## Animations

Animations should reinforce the feeling of a responsive, intelligent system that reacts instantly to user actions while providing subtle feedback that tasks are progressing.

- **Status Transitions**: Smooth 300ms ease-in-out transitions when task status changes (pending → running → complete)
- **Card Reveals**: Staggered fade-in with slight upward slide (150ms delay between cards) when loading dashboard
- **Progress Indicators**: Animated progress bars with spring physics (framer-motion) to emphasize momentum
- **Toast Notifications**: Slide-in from top-right with gentle bounce for PR updates and task completions
- **Hover States**: Subtle 150ms scale (1.02) and shadow deepening on interactive cards
- **Loading States**: Skeleton screens with shimmer effect rather than spinners for content areas

## Component Selection

- **Components**:
  - **Sidebar**: Navigation with collapsible sections for Conversations, Agents, and Dashboard views
  - **Card**: Container for agent task cards, PR status cards, and batch intelligence panels
  - **Badge**: Status indicators (idle, active, blocked, complete) with color-coded variants
  - **Progress**: Linear progress bars for task completion percentage
  - **Tabs**: Switching between Dashboard, Batch Intelligence, and Conversation History
  - **Dialog**: Detailed task view modal when clicking on agent cards
  - **Popover**: Quick-view for PR details and agent actions
  - **Scroll Area**: Smooth scrolling for conversation transcripts and task lists
  - **Separator**: Visual dividers between dashboard sections
  - **Avatar**: Agent profile images with online/offline indicators
  - **Button**: Primary actions (Run New Batch, Add Agent) and secondary actions (view details, refresh)
  - **Input**: Search/filter fields for conversations and tasks
  - **Tooltip**: Contextual help for status icons and abbreviated labels

- **Customizations**:
  - Custom **StatusTimeline** component showing task progression through phases
  - Custom **PRStatusCard** with GitHub-style merge indicators and check status
  - Custom **AgentActivityChart** using D3 for visualizing agent workload distribution
  - Custom **ConflictMapViz** showing agreement/disagreement patterns in batch intelligence

- **States**:
  - Buttons: Default with subtle gradient, hover with scale + shadow, active with inset shadow, disabled with reduced opacity
  - Cards: Default with border, hover with elevated shadow and border accent, selected with colored left border
  - Inputs: Default with light border, focus with ring and accent border, error with red border and icon
  - Status badges: Pulsing animation for "in-progress", static for completed/failed

- **Icon Selection**:
  - GitBranch, GitPullRequest, GitMerge - PR-related actions
  - CheckCircle, XCircle, Clock, AlertCircle - Status indicators
  - Play, Pause, Square (stop) - Task control actions
  - Users, User - Agent representation
  - ChartBar, Activity - Analytics and metrics
  - ChatCircle, Chat - Conversations
  - Plus, Pencil, Trash - CRUD operations

- **Spacing**:
  - Container padding: `p-6` (24px)
  - Card padding: `p-4` (16px)
  - Section gaps: `gap-6` (24px)
  - Component spacing: `gap-4` (16px)
  - Tight spacing: `gap-2` (8px)
  - Page margins: `mx-auto max-w-7xl`

- **Mobile**:
  - Sidebar collapses to hamburger menu with slide-out drawer
  - Three-column dashboard becomes single column stack
  - Agent cards maintain full width, stack vertically
  - Tabs become dropdown selector on mobile
  - Touch targets minimum 44px height
  - Reduced padding: `p-4` → `p-3` on mobile
  - Hidden metadata on small screens, revealed via tap/expand
