---
description: Three-round iterative exploration strategy for complex topics with parallel subagents
SNIPPET_NAME: iterating-code
ANNOUNCE_USAGE: false
---

# Iterating Through Code and Complex Topics

Use this strategy when exploring complex, multi-faceted topics requiring deep understanding, abstract or theoretical concepts needing multiple angles, historical or academic subjects with interconnected themes, or when you want to build knowledge progressively across rounds where synthesis and connection-making are the goals.

## The 3-Round Exploration Pattern

Structure your research in **three focused rounds**, each building on previous findings:

### Round 1: Foundation & Overview
**Goal:** Establish baseline understanding
- **What to explore:** Core concepts, historical context, key figures
- **Focus:** Breadth over depth
- **Output:** Mental map of the territory

### Round 2: Deep Dive & Connections
**Goal:** Understand relationships and nuances
- **What to explore:** How concepts relate, critical perspectives, debates
- **Focus:** Connections between Round 1 findings
- **Output:** Integrated understanding of major themes

### Round 3: Synthesis & Analysis
**Goal:** Advanced understanding and critical evaluation
- **What to explore:** Implications, contradictions, scholarly debates
- **Focus:** Evaluate competing interpretations
- **Output:** Sophisticated, multi-layered comprehension

## Subagent Coordination Strategy

For efficient parallel exploration, use the **Task tool** to launch multiple research agents:

### Within Each Round:

**Parallel Agents** (if multiple sub-topics):
```
Round Goal
    │
    ├─→ Agent 1: Aspect A
    ├─→ Agent 2: Aspect B
    └─→ Agent 3: Aspect C
    │
    └─→ Synthesis: Integrate findings
```

**Sequential Rounds** (each round uses previous round's output):
```
Round 1: Foundation
    ↓ (synthesize)
Round 2: Connections
    ↓ (synthesize)
Round 3: Analysis
    ↓ (final synthesis)
Final Understanding
```

### Agent Assignment Examples

**Topic: Chinese Women's History (Ko & Mann)**

*Round 1 - Foundation:*
- Agent 1: Historical context (Ming-Qing dynasties)
- Agent 2: Confucian patriarchy framework
- Agent 3: Women's educational access

*Round 2 - Connections:*
- Agent 1: Revisionist historiography challenge to modernization narrative
- Agent 2: Ko's footbinding & agency reinterpretation
- Agent 3: Mann's "moral wives" and state ideology role

*Round 3 - Synthesis:*
- Agent 1: Modernization school vs. revisionist school debate
- Agent 2: Why "tradition" doesn't explain China's path
- Agent 3: Implications for understanding patriarchy and agency

## Quick Implementation

### Step 1: Defining your topic and exploration angles
```
Topic: [Your complex topic]
Round 1 angles: [3 foundational aspects]
Round 2 angles: [3 connection/debate aspects]
Round 3 angles: [3 analytical/critical aspects]
```

### Step 2: Launching Round 1 agents in parallel
Use Task tool to launch 2-3 agents exploring different foundational angles simultaneously.

### Step 3: Synthesizing Round 1 findings
Before Round 2, synthesize connections and patterns that emerged.

### Step 4: Launching Round 2 agents (refined by Round 1)
Now explore deeper relationships and nuanced perspectives.

### Step 5: Synthesizing Round 2 findings
Identify remaining gaps or tensions.

### Step 6: Launching Round 3 agents (critical analysis)
Explore competing interpretations and advanced implications.

### Step 7: Final synthesis
Integrate all three rounds into coherent, multi-layered understanding.

## Why Iterative Rounds Work

- **Progressive complexity:** Foundation → Connections → Analysis
- **Reduced cognitive load:** Each round is focused and specific
- **Better retention:** Building understanding step-by-step creates stronger mental models
- **Identifies gaps:** Each round reveals what to explore next
- **Parallel efficiency:** Multiple agents investigate angles simultaneously within each round
- **Synthesis moments:** Deliberate integration points strengthen learning

## Key Principles

1. **Clear round objectives** - Each round has ONE clear goal
2. **Parallel within, sequential between** - Parallel agents in each round, sequential rounds overall
3. **Synthesis after each round** - Always integrate before moving to next round
4. **Refine based on findings** - Later rounds adjust based on earlier discoveries
5. **Document connections** - Explicitly note how Round 1 → Round 2 → Round 3 build on each other
