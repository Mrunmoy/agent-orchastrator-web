# UI Wireframes: Multi-Agent Orchestrator

## 1. Goals
- Make multi-agent debate easy to follow at a glance.
- Keep user in control with clear pause/continue/steer actions.
- Surface agreement vs disagreement without reading every message.
- Support desktop first, but remain usable on tablet/phone.

## 2. Primary Layout (Desktop)
Three-column layout with persistent control surfaces:

1. Top Bar (full width)
- Workspace selector
- Run state badge (`Idle`, `Running`, `Paused`)
- Current workflow phase + gate state
- Quick controls: `Run New Batch (N)`, `Stop Current Run`
- Batch size input (`N`, default 20)

2. Left Panel: Agents
- Agent cards list in round-robin order (1,2,3...)
- Each card shows:
- avatar, name
- type (`codex`, `claude`, `ollama_manager`)
- session id (editable)
- personality dropdown
- enabled toggle
- Drag handle for reordering
- Add/remove agent actions
- "Target next message" selector

3. Center Panel: Group Chat
- Bubble-style timeline
- Distinct visual identity per speaker
- Sticky section labels for batch boundaries
- Typing indicator for current agent
- Composer at bottom:
- text box
- target-agent dropdown
- send button

4. Right Panel: Batch Intelligence
- Agreement Map card (green)
- Conflict Map card (amber table)
- Ollama Neutral Memo card (slate)
- "Apply memo as steering" button
- Phase gate recommendation chip

5. Bottom Control Drawer (collapsible)
- Steering note input
- Preference note input
- Phase transition intent
- `Continue Batch (N) With Notes`
- `Mark Gate Ready For My Review`

## 3. Responsive Behavior
### Tablet
- Left panel collapses into slide-over drawer.
- Right panel becomes tabbed section above composer.

### Mobile
- Single-column stack:
- Top bar (compact)
- Chat timeline
- Composer
- Bottom tabs: `Agents`, `Intelligence`, `Controls`, `Settings`

## 4. Component Specs
## 4.1 Status Badge
States:
- Idle (gray)
- Running (blue pulse)
- Paused (amber)
- Error (red)

## 4.2 Message Bubble
Fields:
- speaker name + avatar
- timestamp
- message text
- meta chips: phase, turn number, batch number

Types:
- user
- agent
- orchestrator/system
- error

## 4.3 Typing Indicator
Text:
- `<AgentName> is thinking...`
Shows only while current turn is active.

## 4.4 Agreement/Conflict Cards
Agreement card:
- bullet list of aligned points

Conflict card:
- table columns:
- topic
- agent A position
- agent B position

Neutral memo card:
- decision framing
- recommended path (ordered list)
- gate status

## 4.5 Agent Card
Inputs:
- name
- type
- session id
- personality
- model
- enabled
- order index

Actions:
- save
- duplicate
- remove

## 5. Key Interaction Flows
## 5.1 Start Debate
1. User types message.
2. User chooses target agent.
3. User clicks `Run New Batch (N)`.
4. System runs exactly N turns then auto-pauses.

## 5.2 Pause and Steer
1. UI shows `Paused` and batch artifact cards.
2. User reviews conflicts.
3. User writes steering/preference note.
4. User clicks `Continue Batch (N) With Notes` or `Continue Batch (N)` (without notes).

## 5.3 Phase Gate Approval
1. Agents report gate-ready.
2. UI highlights gate card.
3. User clicks `Approve Gate` or continues discussion.

## 5.4 Stop
1. User clicks `Stop`.
2. System stops at turn boundary.
3. UI emits system event and keeps transcript consistent.

## 6. Visual Language
- Human chat aesthetic: rounded bubbles, avatars, contextual spacing.
- Clear hierarchy: chat center, controls around it.
- Color roles:
- Codex family: deep blue
- Claude family: amber/rust
- Ollama memo: slate/neutral
- User: teal
- System: graphite
- Motion:
- subtle pulse on running state
- fade-in for new messages
- no excessive animation

## 7. Accessibility and Usability
- Keyboard shortcuts:
- `Enter` send
- `Ctrl+Enter` run batch
- `Esc` stop request confirmation
- Contrast-safe palettes for cards and badges.
- Labels on all dropdowns/toggles.
- Avoid color-only cues; include icons/text labels.

## 8. MVP Screen Checklist
- [ ] Main desktop shell
- [ ] Agent list with order and session edit
- [ ] Chat bubbles + typing indicator
- [ ] Batch controls (`Run N`, `Continue N`, `Stop`)
- [ ] Agreement/Conflict/Neutral cards
- [ ] Steering + preference inputs
- [ ] Settings panel (workdir, token, timeout)

## 9. Prototype File
A static visual prototype is provided at:
- `src/mockup.html`

Use it as a visual target while implementing the real UI.


## 5.5 Control Semantics
- `Run New Batch (N)`: starts a new batch run from current paused/idle point.
- `Stop Current Run`: requests stop at next turn boundary.
- `Continue Batch (N) With Notes`: resumes paused run and injects steering/preference notes.
- `Mark Gate Ready For My Review`: agents signal phase-ready; user sees checklist and decides approve/reject.
