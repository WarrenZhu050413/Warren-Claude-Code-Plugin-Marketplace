---
name: "Visualizing Subagents"
description: "Visualize subagent task dependencies using ASCII diagrams before launching agents and create comprehensive HTML summaries after completion."
---

# Visualizing Subagents

## ASCII Diagram FIRST

**CRITICAL:** Draw ASCII diagram as FIRST thing before launching Task tool.

### When to Draw
1. **BEFORE launching:** Show planned structure
2. **AFTER completion:** Show completed workflow (on request)

### Diagram Formats

**Parallel:**
```
USER REQUEST: [task]
    │
    ├─→ AGENT 1: [Task A]
    ├─→ AGENT 2: [Task B]
    └─→ AGENT 3: [Task C]
    │
    └─→ SYNTHESIS
```

**Sequential:**
```
USER REQUEST: [task]
    ↓
AGENT 1: [First]
    ↓
AGENT 2: [Second, needs Agent 1]
    ↓
AGENT 3: [Final]
```

**Mixed:**
```
USER REQUEST: [Verify quotations]
    │
    ├─→ AGENT 1: Quote A, p.400
    ├─→ AGENT 2: Quote B, p.401
    └─→ AGENT 3: Quote C, p.402
    │
    └─→ AGENT 4: Verify all exact
```

### Labels
- Agent number (AGENT 1, AGENT 2)
- Task (max 3-4 words)
- Critical parameter (page, file)

### Response Structure
```
[ASCII DIAGRAM FIRST]
[Brief strategy - 1-2 sentences]
[Tool calls]
```

### Benefits
- Shows structure at glance
- Clarifies dependencies
- Sets expectations
- Documents approach

## HTML Visualization (Post-Completion)

When user wants to visualize/summarize subagents, create interactive HTML: `claude_agent_workflow_[task_name].html`

### Components

**1. Mermaid Dependency Graph**
- User request → agents → synthesis → output
- Color coding: launched (sky blue), running (gold), completed (green), synthesized (plum)

**2. Statistics Dashboard**
- Agents launched/completed/success rate
- Execution mode (parallel/sequential/mixed)
- Tokens, word count, time

**3. Task Detail Cards**
- Status indicator, agent number, type badge
- Task description, tags
- Collapsible key findings (discoveries, patterns, limitations)
- Grid layout (2-3 columns)

**4. Synthesis Process**
- Execution strategy (why parallel vs sequential)
- Data integration (how merged)
- Cross-validation, conflict resolution
- Output generation

**5. Dependency Analysis**
- Independent tasks (parallel)
- Dependencies (sequential)
- Critical path, bottlenecks
- Efficiency gains

**6. Key Insights**
- ✓ Strengths | ⚠ Challenges | 💡 Lessons | 🎯 Recommendations

### Generation Steps
1. Analyze context (Task tool usage)
2. Extract metadata (agents, tasks, dependencies, findings)
3. Structure data
4. Generate HTML
5. Save as `claude_agent_workflow_[name].html`
6. Open in browser
7. Confirm to user

### Trigger Phrases
- "visualize the subagents"
- "dependency graph"
- "summarize what subagents found"
- "workflow diagram"

### Quality Checklist
- All agents represented
- Dependencies accurate
- Status colors correct
- Findings summarized
- Statistics calculated
- Interactive features work
- Mermaid syntax valid
- File saved and opened
