# Parallel Prototype Orchestration

Build and compare multiple web app prototypes simultaneously using sub-agents. Design first, spawn parallel builders, serve all variants, then iterate or finalize.

## When to Use

- User says "PROTOTYPE", "WEBAPP", or wants to explore multiple approaches
- Need to compare different design directions
- Want rapid parallel development with live preview
- Orchestra MCP is available for sub-agent spawning

## Overview

This skill orchestrates a multi-prototype workflow:

1. **Propose** n prototype variants (default: 3)
2. **Spawn** executor sub-agents to build each in parallel git worktrees
3. **Serve** all prototypes on different ports with live preview
4. **Select** the winning prototype, iterate, or kill all servers

---

## Phase 1: Design Variants (10-15 min)

Before spawning any agents, design multiple distinct approaches. Each variant should explore a different:

- **Visual style** (minimal vs rich, dark vs light)
- **Interaction pattern** (modals vs inline, tabs vs panels)
- **Architecture approach** (SPA vs multi-page, stateful vs stateless)
- **Feature focus** (speed vs features, simplicity vs power)

### Variant Proposal Template

Present variants to the user in this format:

```
## Prototype Variants

### Variant A: [Name] - [One-liner]
**Focus**: [Primary design goal]
**Visual**: [Style description]
**Interaction**: [How user interacts]
**Trade-off**: [What it optimizes for vs sacrifices]

### Variant B: [Name] - [One-liner]
**Focus**: [Primary design goal]
**Visual**: [Style description]
**Interaction**: [How user interacts]
**Trade-off**: [What it optimizes for vs sacrifices]

### Variant C: [Name] - [One-liner]
**Focus**: [Primary design goal]
**Visual**: [Style description]
**Interaction**: [How user interacts]
**Trade-off**: [What it optimizes for vs sacrifices]

Which variants would you like me to build? (A/B/C/all/suggest more)
```

### Example Variants for a Note-Taking App

```
### Variant A: "Zen" - Distraction-free writing
**Focus**: Minimal UI, maximum focus
**Visual**: White background, single centered column, no sidebar
**Interaction**: Everything via keyboard shortcuts, hidden toolbar
**Trade-off**: Speed over discoverability

### Variant B: "Dashboard" - Power user's command center
**Focus**: Information density, quick navigation
**Visual**: Dark theme, three-column layout, visible sidebar
**Interaction**: Click-driven with command palette (⌘K)
**Trade-off**: Features over simplicity

### Variant C: "Mobile-First" - Touch-optimized responsive
**Focus**: Works great on all devices
**Visual**: Large touch targets, bottom navigation, swipe gestures
**Interaction**: Thumb-friendly actions, pull-to-refresh
**Trade-off**: Mobile experience over desktop power features
```

---

## Phase 2: Spawn Parallel Builders (2-3 min)

Once user approves variants, spawn executor sub-agents in parallel using Orchestra MCP.

### Pre-Spawn Checklist

1. Confirm Orchestra MCP is available
2. Get source path from project config
3. Generate unique session names for each variant

### Spawning Pattern

For each approved variant, call `spawn_subagent` with:

```python
spawn_subagent(
    parent_session_name="main",
    child_session_name="prototype-{variant_letter}",
    source_path="/path/to/project",
    agent_type="executor",
    instructions="""
# Prototype {Variant Letter}: {Variant Name}

## Your Mission
Build a working prototype implementing this specific design direction.

## Design Spec
{Full design specification from Phase 1}

## Tech Stack
- Frontend: React + Vite
- Backend: FastAPI (if needed) or static
- Database: SQLite (if needed)
- Styling: Tailwind CSS or vanilla CSS

## Requirements
1. Must run on port {assigned_port}
2. Create in: src/prototypes/variant-{letter}/
3. Include a launcher script that starts the dev server
4. Implement core features only (no gold plating)
5. Add ⌘S (save) and ⌘/ (help) keyboard shortcuts

## Success Criteria
- App runs on http://localhost:{port}
- Core user flow works end-to-end
- No console errors
- Clean, readable code

## When Done
Message the main session with:
- Confirmation prototype is running
- The URL to access it
- Brief summary of implementation choices
"""
)
```

### Port Assignment

Use this port scheme to avoid conflicts:

| Variant | Frontend Port | Backend Port |
|---------|--------------|--------------|
| A       | 5173         | 8001         |
| B       | 5174         | 8002         |
| C       | 5175         | 8003         |
| D       | 5176         | 8004         |
| E       | 5177         | 8005         |

### Parallel Spawn Example

```python
# Spawn all variants in parallel (single message with multiple tool calls)
spawn_subagent(
    parent_session_name="main",
    child_session_name="prototype-a",
    source_path=source_path,
    instructions="... Variant A spec ..."
)
spawn_subagent(
    parent_session_name="main",
    child_session_name="prototype-b",
    source_path=source_path,
    instructions="... Variant B spec ..."
)
spawn_subagent(
    parent_session_name="main",
    child_session_name="prototype-c",
    source_path=source_path,
    instructions="... Variant C spec ..."
)
```

---

## Phase 3: Monitor & Serve (During Build)

### Tracking Progress

While executors build, periodically check:

1. `.orchestra/messages.jsonl` for status updates
2. Git worktrees at `/Users/wz/.orchestra/subagents/{session-id}/`
3. Port availability for each prototype

### Status Dashboard (Show to User)

```
## Prototype Status

| Variant | Session         | Status      | URL                    |
|---------|-----------------|-------------|------------------------|
| A       | prototype-a     | ⏳ Building | http://localhost:5173  |
| B       | prototype-b     | ✅ Running  | http://localhost:5174  |
| C       | prototype-c     | ⏳ Building | http://localhost:5175  |

Last updated: [timestamp]
```

### Opening Prototypes

When an executor reports completion:

1. Verify the dev server is running on the assigned port
2. Open in browser: `open http://localhost:{port}`
3. Update status dashboard
4. Notify user: "Variant {X} is now live at http://localhost:{port}"

### Bulk Open Command

Once all prototypes are ready:

```bash
# Open all prototypes in browser tabs
open http://localhost:5173 http://localhost:5174 http://localhost:5175
```

---

## Phase 4: Selection & Iteration

### Presenting Options

Once all prototypes are running, ask the user:

```
## All Prototypes Ready!

🅰️ Variant A "Zen" - http://localhost:5173
🅱️ Variant B "Dashboard" - http://localhost:5174
🅲️ Variant C "Mobile-First" - http://localhost:5175

**What would you like to do?**

1. **Select winner** - Choose one to continue developing
2. **Iterate** - Request changes to specific variants
3. **Combine** - Merge features from multiple variants
4. **More variants** - Generate n more prototype ideas
5. **Kill all** - Stop all servers and clean up
```

### User Choice Handling

#### Choice 1: Select Winner

```
User: "I like Variant B"

Action:
1. Kill dev servers for A and C
2. Merge Variant B branch to main (with user approval)
3. Continue development on selected prototype
4. Clean up unused worktrees
```

#### Choice 2: Iterate

```
User: "Can you make Variant A have a sidebar like B?"

Action:
1. Send iteration instructions to prototype-a executor:
   send_message_to_session(
       session_name="prototype-a",
       message="Add a collapsible sidebar similar to Variant B's implementation...",
       source_path=source_path,
       sender_name="main"
   )
2. Wait for completion
3. Refresh browser / notify user
```

#### Choice 3: Combine

```
User: "I want A's minimal editor with B's sidebar and C's mobile responsiveness"

Action:
1. Create new variant specification combining features
2. Spawn new executor: prototype-combined
3. Use existing code as reference
```

#### Choice 4: More Variants

```
User: "Show me 2 more ideas"

Action:
1. Return to Phase 1
2. Generate 2 new distinct variants (D, E)
3. Spawn new executors
4. Keep existing prototypes running
```

#### Choice 5: Kill All

```
User: "Kill all servers"

Action:
1. Find all running dev server processes
2. Kill each by port:
   lsof -ti:5173 | xargs kill -9
   lsof -ti:5174 | xargs kill -9
   lsof -ti:5175 | xargs kill -9
   lsof -ti:8001 | xargs kill -9
   lsof -ti:8002 | xargs kill -9
   lsof -ti:8003 | xargs kill -9
3. Confirm all stopped
4. Optionally clean up worktrees
```

---

## Server Management Commands

### Start a Prototype Server

```bash
# Navigate to worktree and start
cd /Users/wz/.orchestra/subagents/prototype-a/
npm run dev -- --port 5173
```

### Kill Server by Port

```bash
# Kill process on specific port
lsof -ti:5173 | xargs kill -9 2>/dev/null || echo "No process on port 5173"
```

### Kill All Prototype Servers

```bash
# Kill all prototype servers (ports 5173-5177 and 8001-8005)
for port in 5173 5174 5175 5176 5177 8001 8002 8003 8004 8005; do
  lsof -ti:$port | xargs kill -9 2>/dev/null
done
echo "All prototype servers stopped"
```

### Check Running Servers

```bash
# List all running dev servers
lsof -i :5173-5177 -i :8001-8005 | grep LISTEN
```

---

## Project Structure

When building prototypes, use this structure:

```
project/
├── src/
│   └── prototypes/
│       ├── variant-a/
│       │   ├── frontend/
│       │   │   ├── src/
│       │   │   ├── package.json
│       │   │   └── vite.config.js
│       │   ├── backend/          # if needed
│       │   │   ├── server.py
│       │   │   └── requirements.txt
│       │   └── launcher.sh
│       ├── variant-b/
│       │   └── ...
│       └── variant-c/
│           └── ...
├── .orchestra/
│   ├── designer.md              # Design discussion
│   └── messages.jsonl           # Sub-agent messages
└── package.json
```

---

## Executor Instructions Template

Use this template when spawning executors:

```markdown
# Prototype Executor: Variant {LETTER} - "{NAME}"

## Context
You are building one of {N} parallel prototypes. Your variant focuses on:
{VARIANT_FOCUS}

## Design Specification

### Visual Design
{VISUAL_SPEC}

### User Interactions
{INTERACTION_SPEC}

### Data Models (if applicable)
{DATA_MODELS}

### API Endpoints (if applicable)
{API_ENDPOINTS}

## Technical Requirements

### Stack
- Frontend: React 18 + Vite 5
- Styling: {STYLE_CHOICE}
- Backend: {BACKEND_CHOICE}
- Database: {DB_CHOICE}

### Port Configuration
- Frontend dev server: {FRONTEND_PORT}
- Backend server: {BACKEND_PORT}

### File Location
Create all files in: `src/prototypes/variant-{letter}/`

### Launcher Script
Create `launcher.sh` that:
1. Installs dependencies (if not present)
2. Starts backend (if applicable)
3. Starts frontend dev server on assigned port
4. Opens browser to frontend URL

## Implementation Order
1. Set up project structure (5 min)
2. Build core UI shell (15 min)
3. Implement main user flow (30 min)
4. Add keyboard shortcuts ⌘S, ⌘/ (5 min)
5. Polish and test (10 min)

## Completion Criteria
- [ ] App runs on http://localhost:{FRONTEND_PORT}
- [ ] Core user flow works
- [ ] Keyboard shortcuts functional
- [ ] No console errors
- [ ] launcher.sh works

## When Done
Send message to main session:
```
Prototype {LETTER} complete!
URL: http://localhost:{FRONTEND_PORT}
Summary: {brief description of implementation}
```
```

---

## Workflow Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROTOTYPE ORCHESTRATION                       │
└─────────────────────────────────────────────────────────────────┘

User Request
    │
    ▼
┌─────────────────┐
│  Phase 1: Design │ ──► Present n variant proposals
│  (10-15 min)     │     User approves subset
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Phase 2: Spawn  │ ──► Parallel spawn_subagent calls
│  (2-3 min)       │     Each builds in own worktree
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Phase 3: Serve  │ ──► Monitor progress
│  (build time)    │     Open browsers when ready
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────┐
│  Phase 4: Select │ ──►│ Winner  │──► Merge & continue
│                  │     └─────────┘
│                  │     ┌─────────┐
│                  │ ──►│ Iterate │──► Message executors
│                  │     └─────────┘
│                  │     ┌─────────┐
│                  │ ──►│ More    │──► Back to Phase 1
│                  │     └─────────┘
│                  │     ┌─────────┐
│                  │ ──►│ Kill    │──► Stop all servers
└─────────────────┘     └─────────┘
```

---

## Quick Reference

### Key Commands

| Action | Command |
|--------|---------|
| Spawn executor | `spawn_subagent(...)` via Orchestra MCP |
| Message executor | `send_message_to_session(...)` via Orchestra MCP |
| Check messages | Read `.orchestra/messages.jsonl` |
| Open prototype | `open http://localhost:{port}` |
| Kill by port | `lsof -ti:{port} \| xargs kill -9` |
| Kill all | Loop through ports 5173-5177, 8001-8005 |

### Default Ports

| Variant | Frontend | Backend |
|---------|----------|---------|
| A | 5173 | 8001 |
| B | 5174 | 8002 |
| C | 5175 | 8003 |
| D | 5176 | 8004 |
| E | 5177 | 8005 |

### Status Indicators

| Symbol | Meaning |
|--------|---------|
| ⏳ | Building |
| ✅ | Running |
| ❌ | Failed |
| 🔄 | Iterating |
| 💀 | Killed |

---

## Fallback: No Orchestra MCP

If Orchestra MCP is not available:

1. **Inform user**: "Orchestra MCP not detected. I'll build prototypes sequentially instead of in parallel."
2. **Sequential build**: Build variants one at a time in the main session
3. **Same structure**: Use `src/prototypes/variant-{x}/` organization
4. **Manual servers**: Start each dev server in background with `&`

```bash
# Sequential fallback
cd src/prototypes/variant-a && npm run dev -- --port 5173 &
cd src/prototypes/variant-b && npm run dev -- --port 5174 &
cd src/prototypes/variant-c && npm run dev -- --port 5175 &
```

---

## Rules for Claude

**DO:**
- Design multiple distinct variants before building
- Spawn executors in parallel (single message, multiple tool calls)
- Assign unique ports to each prototype
- Track status and update user regularly
- Open all prototypes in browser when ready
- Clean up servers when done

**DON'T:**
- Build without user approval on variants
- Use overlapping ports
- Forget to kill servers after selection
- Spawn sequentially when parallel is possible
- Assume Orchestra MCP is available (check first)

---

## Success Criteria

A successful prototype session:
- ✅ User saw n distinct design proposals
- ✅ Selected variants built in parallel
- ✅ All prototypes accessible via browser
- ✅ User could compare live implementations
- ✅ Clear path to iterate, select, or discard
- ✅ All servers cleaned up when done
