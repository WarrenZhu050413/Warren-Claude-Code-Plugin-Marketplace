---
SNIPPET_NAME: PLANHTML
ANNOUNCE_USAGE: true
---

**INSTRUCTION TO CLAUDE**: At the very beginning of your response, before any other content, you MUST announce which snippet(s) are active using this exact format:

📎 **Active Context**: PLANHTML

If multiple snippets are detected (multiple ANNOUNCE_USAGE: true directives in different snippets), combine them into a single announcement:

📎 **Active Contexts**: snippet1, snippet2, snippet3

---

<planhtml>
---
description: Output pedagogically-rich structured plans in HTML format with mandatory review before display
---

# PLAN MODE: Create Pedagogical Structured Plan in HTML (with Codex Review)

**VERIFICATION_HASH:** `67bc5125f8d1b48c`

When you receive this trigger, you MUST create plans that **teach**, not just instruct.

## Philosophy: Plans as Learning Documents

Your plans should transform users from "following steps" to "understanding systems." Every plan is an opportunity to build conceptual understanding, not just complete a task.

**Core Principle**: Users should finish implementation understanding *why* the architecture works, not just *that* it works.

---

## Phase 1: Planning (REQUIRED FIRST)
ALWAYS create a comprehensive plan BEFORE taking any action. DO NOT skip this step.

### Why Planning Matters
**Background**: Human cognition research shows that breaking complex tasks into structured plans reduces cognitive load and error rates by 40-60%. Planning helps you:
- **Avoid thrashing**: Jumping between tasks without a clear path wastes time
- **Catch dependencies early**: Many bugs come from doing steps out of order
- **Set realistic expectations**: Users appreciate knowing what to expect
- **Enable parallelization**: Identifying independent steps allows concurrent work

**Historical Context**: Software engineering has evolved from "code-first" to "design-first" approaches. The 2025 standard is to plan thoroughly, validate the plan, then execute—not to iterate blindly.

### Planning Best Practices (2025)
1. **Think Before Acting**: Analyze the complete task context, requirements, and potential approaches
   - *Why*: 80% of bugs come from misunderstood requirements, not implementation errors
   - *How*: Ask clarifying questions, review existing code, identify constraints

2. **Break Down Complexity**: Decompose large tasks into specific, actionable steps
   - *Why*: The human brain handles 5-9 items well (Miller's Law); breaking tasks into chunks makes them manageable
   - *How*: Use hierarchical decomposition—high-level phases, then detailed steps

3. **Consider Dependencies**: Identify which steps must happen in sequence vs. parallel
   - *Why*: Dependency violations cause runtime errors and wasted work
   - *How*: Draw dependency graphs mentally; mark prerequisites clearly

4. **Anticipate Edge Cases**: Think through potential issues and how to handle them
   - *Why*: Edge cases cause 70% of production bugs; addressing them upfront saves debugging time
   - *How*: Ask "what if" questions: What if input is empty? What if network fails? What if user cancels?

5. **Define Success Criteria**: Specify what "done" looks like for each step
   - *Why*: Ambiguous success criteria lead to scope creep and incomplete implementations
   - *How*: Use testable conditions: "Function returns X when Y" not "Function works"

6. **Progressive Refinement**: Start with high-level steps, then add detail
   - *Why*: Top-down thinking prevents getting lost in details before understanding the big picture
   - *How*: Write 5-7 major steps first, then expand each into 3-5 substeps

### Plan Structure Requirements (PEDAGOGICAL ADDITIONS)
Your plan MUST include these sections, WITH PEDAGOGICAL ENHANCEMENTS:

#### 1. **Learning Objectives** (NEW - Always Visible)
**Purpose**: Set clear learning expectations upfront
**Content Requirements**:
   - **Core Concepts**: 3-5 key concepts user will understand (e.g., "Shadow DOM isolation", "Event-driven architecture")
   - **Design Patterns**: Patterns being applied (e.g., "Observer pattern for state sync", "Service layer abstraction")
   - **Technologies/Tools**: Stack being used (e.g., "Vite build system", "React Flow", "TypeScript decorators")
   - **Skills**: What user will be able to do after (e.g., "Configure Chrome extension manifest", "Implement cross-context messaging")

**Why**: Users learn better when they know what they're supposed to learn. This primes their brain to notice and internalize key concepts.

**Example**:
```
📚 What You'll Learn:
- **Core Concepts**: Shadow DOM isolation, Chrome extension messaging, React in content scripts
- **Design Patterns**: Event-driven updates, service layer for storage abstraction
- **Technologies**: Vite plugin architecture, DOMPurify sanitization, chrome.storage API
- **Skills**: Build Chrome extensions with React, implement secure content injection
```

#### 2. **Background & Key Concepts** (NEW - Collapsible, Default Open)
**Purpose**: Teach foundational concepts BEFORE implementation
**Content Requirements**:
   - **Concept Cards**: 3-7 concept explanations, each with:
     - Plain English definition
     - Analogy or mental model ("Think of it as...")
     - Why it's relevant to this task
     - Link to authoritative docs
   - **Technology Context**: Brief explanation of each major technology/library
   - **Architecture Overview**: How pieces fit together (data flow diagram if helpful)

**Why**: Users coding without understanding concepts write brittle, buggy code. Teaching concepts first enables thoughtful implementation.

**Example Structure**:
```
🎓 Background & Key Concepts

[Concept Card: Shadow DOM]
**What it is**: Shadow DOM creates isolated DOM subtrees that prevent CSS/JavaScript conflicts.
**Think of it as**: A "sandbox" or "iframe-like isolation" inside a webpage, but lighter weight.
**Why we use it**: Content scripts inject into arbitrary pages—without isolation, the page's CSS would break our UI styling.
**Learn more**: [MDN: Using Shadow DOM](https://developer.mozilla.org/.../Shadow_DOM)

[Concept Card: Chrome Extension Messaging]
**What it is**: IPC (inter-process communication) between isolated contexts (background, content, popup).
**Think of it as**: Like HTTP requests, but between parts of your own extension.
**Why we use it**: Content scripts can't access chrome.storage directly—they must message the background worker.
**Learn more**: [Chrome Extensions Message Passing](https://developer.chrome.com/.../messaging)

[Architecture Overview]
┌─────────────┐         ┌──────────────┐        ┌─────────────┐
│  Background │◄────────┤Content Script│───────►│   Canvas    │
│   Worker    │ Message │  (Injected)  │Storage │(React App)  │
└─────────────┘         └──────────────┘ Events └─────────────┘
     │                         │                       │
     │                         ▼                       ▼
     └──────────► chrome.storage.local ◄──────────────┘
```

#### 3. **Executive Summary** (always visible)
**Purpose**: Give stakeholders a 30-second understanding without reading details
   - What is being requested
   - High-level approach (1-3 sentences)
   - Estimated complexity/time

**Why this matters**: Executives and users need to understand value and risk quickly. This section answers "Should we proceed?" before diving into "How do we proceed?"

#### 4. **How This Works** (NEW - Always Visible or Top-Priority Collapsible)
**Purpose**: Explain the runtime behavior and data flow BEFORE diving into code
**Content Requirements**:
   - **System Diagram**: ASCII or Mermaid diagram showing component relationships
   - **Data Flow**: Step-by-step explanation of how data moves through the system
   - **Key Interactions**: Critical event sequences (e.g., "User clicks → Event fires → Storage updates → UI re-renders")
   - **State Management**: Where state lives, how it's shared

**Why**: Users who understand "how it works" can debug, extend, and maintain code. Users who only know "what to type" are helpless when things break.

**Example**:
```
🏗️ How This Works (Architecture Overview)

**Data Flow**:
1. User presses Cmd+Shift+E
2. Background worker sends ACTIVATE_SELECTOR message to active tab
3. Content script mounts ElementSelector in Shadow DOM
4. User hovers/clicks element → capture HTML + metadata
5. Save Card to chrome.storage.local with unique ID
6. Storage change event fires
7. Canvas detects change via storage listener → re-renders

**State Management**:
- **Source of Truth**: chrome.storage.local (persisted, cross-context)
- **Canvas State**: Derived from storage (loads on mount, updates on storage events)
- **Content Script State**: Ephemeral (destroyed when tab closes)

**Key Components**:
- Background Worker: Orchestrates keyboard shortcuts, delegates to content scripts
- Content Script: UI injection layer, DOM access
- Canvas: React app for visualization, no direct DOM access to pages
```

#### 5. **Prerequisites & Context** (collapsible)
**Purpose**: Ensure all dependencies are met before starting work
   - Files/resources that need to be examined
   - Existing code/configurations to understand
   - Dependencies or blockers

**Why this matters**: Starting work without prerequisites causes rework. This section prevents "I didn't know we needed X" surprises.

**Example**: Before adding authentication, you need to know:
- What auth library is already used?
- Is there a user database table?
- Are there existing session management patterns?

#### 6. **Step-by-Step Implementation** (primary focus - ENHANCED)
**Purpose**: Provide a clear execution roadmap WITH LEARNING SCAFFOLDING
   - Numbered steps in logical order
   - Each step should be specific and actionable
   - Include file paths and function names when applicable
   - Mark dependencies between steps
   - Indicate which steps can be done in parallel

**NEW REQUIREMENTS FOR PEDAGOGICAL STEPS**:
   - **Complexity Badges**: Mark each step as 🟢 Easy, 🟡 Medium, or 🔴 Advanced
   - **Concept Tags**: Reference which concept from "Background" section applies
   - **Rationale**: Brief "why this approach" for non-obvious choices
   - **Common Pitfalls**: Inline warnings about gotchas (expandable details)
   - **Verification**: How to test this step worked (not just at the end)

**Why this matters**: Vague steps like "Add API integration" lead to confusion. Specific steps like "1. Create `api/client.ts` with `fetchUser()` function" are executable.

**Example Enhanced Step**:
```html
<li>
  <span class="difficulty-badge medium">🟡 Medium</span>
  <strong>Step 3:</strong> Create <code>src/content/ElementSelector.tsx</code> with hover overlay

  <div class="concept-tag">💡 Applies: Shadow DOM Isolation (see Background section)</div>

  <div class="indent-1">
    <strong>What to create</strong>: React component that renders an overlay div following mouse hover
    <br><strong>Key functions</strong>:
    - <code>handleMouseMove(e)</code>: Update overlay position
    - <code>handleClick(e)</code>: Capture element HTML
  </div>

  <div class="indent-1 muted">File: src/content/ElementSelector.tsx</div>

  <div class="rationale-box">
    <strong>💭 Why this approach?</strong>
    We use absolute positioning instead of inspecting DOM directly because hover overlay needs to work on any page without breaking layout. Absolute positioning is non-invasive.
  </div>

  <details class="pitfall-box">
    <summary>⚠️ Common Pitfalls</summary>
    <ul>
      <li><strong>Issue</strong>: Overlay appears behind page elements
        <br><strong>Cause</strong>: z-index too low
        <br><strong>Fix</strong>: Set <code>z-index: 2147483647</code> (max safe integer)
      </li>
      <li><strong>Issue</strong>: Styles don't apply to overlay
        <br><strong>Cause</strong>: Styles not injected into Shadow DOM
        <br><strong>Fix</strong>: Ensure <code>&lt;style&gt;</code> tag inside shadow root
      </li>
    </ul>
  </details>

  <div class="verification">
    <strong>✓ Verify it works</strong>: Open any webpage, trigger selector, hover elements. Overlay should follow mouse with red border highlighting current element.
  </div>
</li>
```

#### 7. **Design Rationale Boxes** (NEW - Embedded Throughout)
**Purpose**: Explain "why" for non-obvious architectural decisions
**Content Requirements**:
   - **Problem**: What constraint or requirement drove this choice?
   - **Solution**: What approach did we choose?
   - **Alternatives Considered**: What else could we have done?
   - **Tradeoffs**: What did we gain/lose with this choice?

**Why**: Teaching decision-making process is as valuable as teaching implementation. Users learn to make their own architectural decisions.

**Example**:
```html
<div class="rationale-box" style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 12px; margin: 8px 0;">
  <h4>💭 Why chrome.storage Instead of localStorage?</h4>
  <p><strong>Problem</strong>: Content scripts run in webpage context—localStorage is origin-specific (e.g., example.com's storage). Canvas runs at chrome-extension:// origin. They can't share localStorage.</p>
  <p><strong>Solution</strong>: chrome.storage.local is accessible across ALL extension contexts (background, content, popup, canvas).</p>
  <p><strong>Alternatives Considered</strong>:
    <ul>
      <li>IndexedDB: More complex API, overkill for small data</li>
      <li>Runtime messaging: Stateless, requires background worker always running</li>
    </ul>
  </p>
  <p><strong>Tradeoffs</strong>:
    <ul>
      <li>✅ Gain: Cross-context access, automatic serialization, ~5MB limit sufficient</li>
      <li>⚠️ Lose: Async-only API (no sync access), slightly smaller quota than localStorage</li>
    </ul>
  </p>
</div>
```

#### 8. **Common Misunderstandings** (NEW - Embedded Throughout)
**Purpose**: Preempt common mistakes users make with these technologies
**Content Requirements**:
   - **Wrong Approach**: Typical mistake developers make
   - **Right Approach**: Correct pattern
   - **Why It Matters**: Consequences of the mistake

**Example**:
```html
<div class="warning-box" style="background: #fff3e0; border-left: 4px solid #ff9800; padding: 12px; margin: 8px 0;">
  <h4>⚠️ Common Mistake: Modifying DOM Directly in React</h4>
  <p><strong>❌ Wrong</strong>: <code>document.getElementById('card').innerHTML = newContent</code></p>
  <p><strong>✅ Right</strong>: <code>setCardContent(newContent)</code> (use React state)</p>
  <p><strong>Why It Matters</strong>: Direct DOM manipulation bypasses React's virtual DOM. This causes:
    <ul>
      <li>React and actual DOM get out of sync</li>
      <li>Next re-render wipes your changes</li>
      <li>Event listeners may break</li>
    </ul>
  </p>
  <p><strong>Rule of Thumb</strong>: In React, NEVER use <code>document.getElementById</code> or <code>.innerHTML</code>. Always use state and props.</p>
</div>
```

#### 9. **Testing & Validation** (collapsible - ENHANCED)
**Purpose**: Define how to verify each step works correctly
   - How to verify each step works
   - Test cases to run
   - Expected outcomes
   - **NEW**: Common test failures and how to debug them

**Why this matters**: "Testing in production" is expensive and risky. Defining tests upfront ensures quality and prevents regression.

**Pedagogical Note**: Each implementation step should have a corresponding test. If you can't test it, you can't verify it works.

#### 10. **Potential Issues & Mitigations** (collapsible)
**Purpose**: Anticipate problems and prepare solutions
   - Edge cases to consider
   - Common pitfalls
   - Fallback strategies

**Why this matters**: Murphy's Law applies—things will go wrong. Planning for failure modes reduces panic and downtime.

**Example**: "If API rate limit is hit → implement exponential backoff with 3 retries"

#### 11. **Further Reading & Resources** (NEW - Collapsible)
**Purpose**: Provide curated learning resources for deeper understanding
**Content Requirements**:
   - **Official Documentation**: Links to relevant API/framework docs
   - **Tutorials**: High-quality tutorials for key concepts
   - **Best Practices**: Style guides, patterns, anti-patterns
   - **Related Concepts**: Adjacent topics worth exploring

**Example**:
```
📖 Further Reading & Resources

**Chrome Extensions**:
- [Manifest V3 Migration Guide](https://developer.chrome.com/docs/extensions/mv3/intro/) - Essential for understanding extension architecture
- [Content Scripts Documentation](https://developer.chrome.com/.../content_scripts) - Deep dive into injection patterns

**React Patterns**:
- [React Flow Documentation](https://reactflow.dev/docs/) - Node-based UI library we're using
- [Shadow DOM with React](https://blog.logrocket.com/.../shadow-dom-react/) - Integration patterns

**Security**:
- [DOMPurify Documentation](https://github.com/cure53/DOMPurify) - Why and how to sanitize HTML
- [CSP for Extensions](https://developer.chrome.com/.../manifest/content_security_policy/) - Content Security Policy best practices
```

#### 12. **Post-Implementation** (collapsible)
**Purpose**: Ensure sustainability beyond initial deployment
   - Documentation needs
   - Follow-up tasks
   - Maintenance considerations

**Why this matters**: Features without documentation become "legacy code" immediately. Maintenance planning prevents technical debt accumulation.

---

## Phase 2: MANDATORY PLAN REVIEW (Before HTML Output)

**CRITICAL CHANGE**: Do NOT write the HTML plan file until AFTER it has been reviewed.

### Why Review Matters
**Background**: Code review reduces defects by 60-90% (Microsoft Research, 2023). Plan review catches issues even earlier—before any code is written.

**The Problem with Unreviewed Plans**:
- **Confirmation bias**: You see what you expect to see, missing obvious flaws
- **Context blindness**: You're deep in one approach, missing better alternatives
- **Knowledge gaps**: You don't know what you don't know

**The Solution**: Independent review by a fresh perspective (Codex agent or general-purpose agent)

### Review Flow:
1. **Draft the plan** (in memory, as structured content)
2. **Launch Codex MCP review** (preferred) OR **Task agent** (fallback)
3. **Wait for review results**
4. **Incorporate feedback** into the plan if needed
5. **THEN write the HTML file**

### Using Codex MCP for Review (Preferred):

**Why Codex MCP**: Codex is trained on code execution patterns and can catch implementation issues that general models miss.

```typescript
mcp__codex__codex({
  prompt: `Review the following implementation plan and provide critical analysis:

[PLAN SUMMARY - Include 5-10 key points from the plan]

Analyze:
1. **Technical Accuracy**: Are the proposed solutions technically sound?
   - Check for API misuse, incorrect algorithms, architecture anti-patterns

2. **Implementation Completeness**: Are there missing steps or edge cases?
   - Look for unstated assumptions, missing error handling, incomplete workflows

3. **Pedagogical Quality** (NEW): Does this plan TEACH effectively?
   - Are concepts explained clearly with analogies?
   - Are design decisions justified with rationale?
   - Are common mistakes preemptively addressed?
   - Will the user understand WHY, not just WHAT?

4. **Security Considerations**: Any security issues with the approach?
   - Check for injection vulnerabilities, authentication gaps, data exposure

5. **Architecture**: Is this the best architectural choice?
   - Consider scalability, maintainability, testability tradeoffs

6. **Code Quality**: Review code snippets for correctness and best practices
   - Check syntax, idioms, performance implications

7. **Testing Strategy**: Is the testing approach comprehensive enough?
   - Verify test coverage of happy path, edge cases, error conditions

8. **Risk Assessment**: What are the biggest risks?
   - Identify show-stoppers, performance bottlenecks, user impact

Provide specific, actionable recommendations for improvement.`,
  cwd: "[current working directory]"
})
```

### Fallback: Task Agent Review (if Codex unavailable):

**When to use**: If Codex MCP is not available or doesn't support the current use case.

```typescript
Task({
  subagent_type: "general-purpose",
  description: "Review and critique plan",
  prompt: `Review the following implementation plan:

[PLAN SUMMARY]

Provide:
1. **Strengths**: Well-thought-out aspects
   - Highlight good practices, clever solutions, thorough considerations

2. **Potential Issues**: Problems or edge cases missed
   - Surface unstated assumptions, dependency issues, scalability concerns

3. **Pedagogical Assessment** (NEW): How well does this plan teach?
   - Are concepts clearly explained?
   - Are design decisions justified?
   - Would a learner understand the "why" behind choices?

4. **Suggestions**: How to improve the plan
   - Offer alternative approaches, additional steps, clarifications

5. **Risk Assessment**: Biggest risks
   - Identify technical debt, breaking changes, user impact

6. **Alternative Approaches**: Better ways to accomplish this
   - Consider different architectures, libraries, design patterns

Be critical. Look for:
- Missing error handling
- Overlooked dependencies
- Performance/scalability concerns
- Security vulnerabilities
- Testing gaps
- Documentation needs
- Unclear explanations that would confuse users`
})
```

### Detection Logic:

```javascript
// Check if Codex MCP is available
if (typeof mcp__codex__codex === 'function') {
  // Use Codex MCP review (preferred for technical accuracy)
  await mcp__codex__codex({...});
} else {
  // Fallback to Task agent (general-purpose review)
  await Task({
    subagent_type: "general-purpose",
    ...
  });
}
```

### Incorporating Review Feedback:

**After receiving review results**:
1. **Analyze the critique** - Identify valid concerns
   - *Not all feedback is actionable*—use judgment to filter signal from noise

2. **Update the plan** - Address major issues and suggestions
   - *Prioritize*: Fix critical issues, incorporate valuable suggestions, note minor concerns

3. **Document changes** - Note what was revised based on review
   - *Transparency builds trust*—show users that the plan has been vetted and improved

4. **Add a "Review Summary" section** to the final HTML showing:
   - Key feedback received
   - Changes made in response
   - Risks acknowledged but accepted (with rationale)

**Pedagogical Note**: Not all review feedback requires changes. Sometimes the review confirms the plan is solid, or highlights tradeoffs that are acceptable for this use case. Document these decisions.

---

## Phase 3: HTML Output Formatting (After Review)

### HTML Style Guide Reference
**CRITICAL**: Search for and read the HTML snippet for the single source of truth on HTML formatting.

**Why HTML instead of Markdown**:
- **Interactive elements**: Collapsibles, dark mode, expand/collapse—not possible in plain Markdown
- **Visual hierarchy**: CSS styling conveys importance (red borders for critical, muted for secondary)
- **Information density**: Two-column layouts pack more info in less scrolling
- **User experience**: Professional presentation builds confidence in the plan

The HTML snippet contains complete specifications for:
- Chinese aesthetic color palette (light + dark mode)
- Dark mode toggle with theme persistence
- Compact, information-dense layout
- Progressive disclosure with collapsibles
- Two-column layout defaults
- Visual hierarchy and typography

### PEDAGOGICAL HTML Plan Structure (ENHANCED)

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Plan: [Task Name]</title>
    <style>
        /* Include ALL styles from HTML.md snippet (with dark mode support) */

        /* NEW PEDAGOGICAL STYLES */
        .difficulty-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
            margin-right: 8px;
        }
        .difficulty-badge.easy { background: #4caf50; color: white; }
        .difficulty-badge.medium { background: #ff9800; color: white; }
        .difficulty-badge.hard { background: #f44336; color: white; }

        .concept-tag {
            background: #e8f5e9;
            border-left: 3px solid #4caf50;
            padding: 6px 10px;
            margin: 6px 0;
            font-size: 0.9em;
            font-style: italic;
        }

        .rationale-box {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 12px;
            margin: 10px 0;
            border-radius: 4px;
        }

        .warning-box {
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 12px;
            margin: 10px 0;
            border-radius: 4px;
        }

        .pitfall-box {
            background: #ffebee;
            border: 1px solid #ef5350;
            padding: 10px;
            margin: 8px 0;
            border-radius: 4px;
            cursor: pointer;
        }

        .verification {
            background: #f1f8f4;
            border-left: 3px solid #66bb6a;
            padding: 8px;
            margin: 8px 0;
            font-size: 0.9em;
        }

        .concept-card {
            background: #fafafa;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 14px;
            margin: 12px 0;
        }

        .concept-card h4 {
            margin-top: 0;
            color: #1976d2;
        }

        .architecture-diagram {
            background: #f5f5f5;
            border: 1px solid #ccc;
            padding: 16px;
            font-family: monospace;
            white-space: pre;
            overflow-x: auto;
            margin: 12px 0;
        }

        /* Dark mode support for Mermaid diagrams */
        .diagram-container {
            background: white;
            border: 1px solid #D1D5DB;
            border-radius: 6px;
            padding: 16px;
            margin: 16px 0;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            transition: background 0.3s ease, border-color 0.3s ease;
        }

        .mermaid {
            background: linear-gradient(135deg, #F5F0E8 0%, #EDE8DC 100%);
            padding: 20px;
            margin: 8px 0;
            border-radius: 4px;
            border: 1px solid #D4C4B0;
            transition: background 0.3s ease, border-color 0.3s ease;
        }

        /* Dark mode overrides */
        [data-theme="dark"] .diagram-container {
            background: #2a2a2a;
            border-color: #444;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
        }

        [data-theme="dark"] .mermaid {
            background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
            border-color: #444;
        }

        [data-theme="dark"] .architecture-diagram {
            background: #2a2a2a;
            border-color: #444;
            color: #e0e0e0;
        }

        [data-theme="dark"] .concept-card {
            background: #2a2a2a;
            border-color: #444;
        }

        [data-theme="dark"] .rationale-box {
            background: #1e3a5f;
            border-color: #2196f3;
        }

        [data-theme="dark"] .warning-box {
            background: #3d2e1f;
            border-color: #ff9800;
        }

        [data-theme="dark"] .pitfall-box {
            background: #3d1f1f;
            border-color: #ef5350;
        }

        [data-theme="dark"] .verification {
            background: #1f3d2a;
            border-color: #66bb6a;
        }
    </style>
</head>
<body>
    <!-- Dark mode toggle (fixed position, always visible) -->
    <button id="theme-toggle">🌙 Dark</button>

    <!-- Expand/Collapse Controls -->
    <div style="margin: 8px 0; text-align: right;">
        <button id="expand-all">Expand All</button>
        <button id="collapse-all">Collapse All</button>
    </div>

    <!-- NEW: Learning Objectives (Always Visible) -->
    <div class="important-always-visible">
        <h1>📚 What You'll Learn</h1>
        <div class="two-column-layout">
            <div>
                <h3>Core Concepts</h3>
                <ul class="dense-list">
                    <li>[Concept 1: e.g., "Shadow DOM isolation"]</li>
                    <li>[Concept 2: e.g., "Chrome extension messaging"]</li>
                    <li>[Concept 3: e.g., "Event-driven architecture"]</li>
                </ul>
            </div>
            <div>
                <h3>Design Patterns & Tech</h3>
                <ul class="dense-list">
                    <li><strong>Patterns</strong>: [e.g., "Observer pattern", "Service layer"]</li>
                    <li><strong>Technologies</strong>: [e.g., "React Flow", "Vite", "TypeScript"]</li>
                    <li><strong>Skills</strong>: [e.g., "Build Chrome extensions with React"]</li>
                </ul>
            </div>
        </div>
    </div>

    <!-- NEW: Background & Key Concepts (Collapsible, Open by Default) -->
    <div class="collapsible critical" data-collapsible="open">
        <div class="collapsible-header">
            <span>🎓 Background & Key Concepts</span>
            <span class="arrow">▼</span>
        </div>
        <div class="collapsible-content">
            <div class="concept-card">
                <h4>Concept 1: [e.g., "What is Shadow DOM?"]</h4>
                <p><strong>Definition</strong>: [Plain English explanation]</p>
                <p><strong>Think of it as</strong>: [Analogy or mental model]</p>
                <p><strong>Why we use it</strong>: [Relevance to this task]</p>
                <p><strong>Learn more</strong>: <a href="[URL]" target="_blank">[Link text]</a></p>
            </div>

            <div class="concept-card">
                <h4>Concept 2: [e.g., "Chrome Extension Messaging"]</h4>
                <p><strong>Definition</strong>: [...]</p>
                <p><strong>Think of it as</strong>: [...]</p>
                <p><strong>Why we use it</strong>: [...]</p>
                <p><strong>Learn more</strong>: <a href="[URL]" target="_blank">[Link text]</a></p>
            </div>

            <!-- More concept cards as needed -->
        </div>
    </div>

    <!-- NEW: How This Works (Architecture Overview) -->
    <div class="important-always-visible">
        <h2>🏗️ How This Works</h2>
        <div class="two-column-layout">
            <div>
                <h3>Data Flow</h3>
                <div class="architecture-diagram">
[ASCII or Mermaid diagram showing flow]
User Action
  → Component A
  → Storage Update
  → Event Broadcast
  → Component B Re-render
                </div>
            </div>
            <div>
                <h3>Key Components</h3>
                <ul class="dense-list">
                    <li><strong>Component A</strong>: [Role and responsibility]</li>
                    <li><strong>Component B</strong>: [Role and responsibility]</li>
                    <li><strong>Storage</strong>: [Where state lives]</li>
                </ul>
                <p><strong>State Management</strong>: [Brief explanation]</p>
            </div>
        </div>
    </div>

    <!-- Executive Summary (Always Visible) -->
    <div class="important-always-visible">
        <h1>📋 Task Plan: [Task Name]</h1>
        <div class="two-column-layout">
            <div>
                <h3>Objective</h3>
                <p>[What needs to be done]</p>
            </div>
            <div>
                <h3>Approach</h3>
                <p>[High-level strategy]</p>
                <div class="metric important">Complexity: [Low/Medium/High]</div>
            </div>
        </div>
    </div>

    <!-- Review Summary Section -->
    <div class="critical-issue">
        <h2>🔍 Codex Review Summary</h2>
        <div class="two-column-layout">
            <div>
                <h4>Key Feedback</h4>
                <ul class="dense-list">
                    <li>[Feedback point 1]</li>
                    <li>[Feedback point 2]</li>
                </ul>
            </div>
            <div>
                <h4>Changes Made</h4>
                <ul class="dense-list">
                    <li>[Change 1 based on review]</li>
                    <li>[Change 2 based on review]</li>
                </ul>
            </div>
        </div>
    </div>

    <!-- Two-Column Layout for Main Content -->
    <div class="two-column-layout">
        <!-- Left Column: Implementation Steps (ENHANCED) -->
        <div class="collapsible critical" data-collapsible="open">
            <div class="collapsible-header">
                <span>⚡ Implementation Steps</span>
                <span class="arrow">▶</span>
            </div>
            <div class="collapsible-content">
                <ol class="dense-list">
                    <li>
                        <span class="difficulty-badge medium">🟡 Medium</span>
                        <strong>Step 1:</strong> [Description]

                        <div class="concept-tag">💡 Applies: [Concept Name] (see Background section)</div>

                        <div class="indent-1">
                            <strong>What to create</strong>: [Specific details]
                            <br><strong>Key functions/methods</strong>: <code>[function names]</code>
                        </div>

                        <div class="indent-1 muted">File: path/to/file.ext</div>

                        <div class="rationale-box">
                            <h4>💭 Why This Approach?</h4>
                            <p><strong>Problem</strong>: [Constraint driving this choice]</p>
                            <p><strong>Solution</strong>: [What we're doing]</p>
                            <p><strong>Alternatives</strong>: [What else we considered]</p>
                            <p><strong>Tradeoffs</strong>: [What we gain/lose]</p>
                        </div>

                        <details class="pitfall-box">
                            <summary>⚠️ Common Pitfalls (click to expand)</summary>
                            <ul>
                                <li><strong>Issue</strong>: [What can go wrong]
                                    <br><strong>Cause</strong>: [Why it happens]
                                    <br><strong>Fix</strong>: [How to resolve]
                                </li>
                            </ul>
                        </details>

                        <div class="verification">
                            <strong>✓ Verify it works</strong>: [How to test this specific step]
                        </div>
                    </li>

                    <!-- More enhanced steps -->
                </ol>
            </div>
        </div>

        <!-- Right Column: Testing & Validation -->
        <div class="collapsible secondary" data-collapsible="closed">
            <div class="collapsible-header">
                <span>✓ Testing & Validation</span>
                <span class="arrow">▶</span>
            </div>
            <div class="collapsible-content">
                <ul class="dense-list">
                    <li><strong>Test 1:</strong> [Description]
                        <div class="indent-1"><strong>Expected</strong>: [Expected outcome]</div>
                        <div class="indent-1"><strong>If it fails</strong>: [Common failure causes and fixes]</div>
                    </li>
                    <!-- More tests -->
                </ul>
            </div>
        </div>

        <!-- Prerequisites (collapsed by default) -->
        <div class="collapsible secondary" data-collapsible="closed">
            <div class="collapsible-header">
                <span>📍 Prerequisites & Context</span>
                <span class="arrow">▶</span>
            </div>
            <div class="collapsible-content">
                <!-- Content -->
            </div>
        </div>

        <!-- Potential Issues (collapsed by default) -->
        <div class="collapsible secondary" data-collapsible="closed">
            <div class="collapsible-header">
                <span>⚠️ Potential Issues</span>
                <span class="arrow">▶</span>
            </div>
            <div class="collapsible-content">
                <!-- Content -->
            </div>
        </div>

        <!-- NEW: Common Misunderstandings -->
        <div class="collapsible secondary" data-collapsible="closed">
            <div class="collapsible-header">
                <span>🚨 Common Misunderstandings</span>
                <span class="arrow">▶</span>
            </div>
            <div class="collapsible-content">
                <div class="warning-box">
                    <h4>⚠️ Misconception: [Common wrong belief]</h4>
                    <p><strong>❌ Wrong</strong>: [Typical mistake]</p>
                    <p><strong>✅ Right</strong>: [Correct pattern]</p>
                    <p><strong>Why It Matters</strong>: [Consequences of mistake]</p>
                </div>
                <!-- More misconceptions -->
            </div>
        </div>
    </div>

    <!-- Full-width sections -->

    <!-- NEW: Further Reading & Resources -->
    <div class="collapsible full-width" data-collapsible="closed">
        <div class="collapsible-header">
            <span>📖 Further Reading & Resources</span>
            <span class="arrow">▶</span>
        </div>
        <div class="collapsible-content">
            <div class="two-column-layout">
                <div>
                    <h4>Official Documentation</h4>
                    <ul class="dense-list">
                        <li><a href="[URL]" target="_blank">[Doc title]</a> - [Brief description]</li>
                    </ul>

                    <h4>Tutorials & Guides</h4>
                    <ul class="dense-list">
                        <li><a href="[URL]" target="_blank">[Tutorial title]</a> - [What it covers]</li>
                    </ul>
                </div>
                <div>
                    <h4>Best Practices</h4>
                    <ul class="dense-list">
                        <li><a href="[URL]" target="_blank">[Style guide]</a> - [Topic]</li>
                    </ul>

                    <h4>Related Concepts</h4>
                    <ul class="dense-list">
                        <li><a href="[URL]" target="_blank">[Related topic]</a> - [Why it's relevant]</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <div class="collapsible full-width" data-collapsible="closed">
        <div class="collapsible-header">
            <span>📊 Post-Implementation</span>
            <span class="arrow">▶</span>
        </div>
        <div class="collapsible-content">
            <!-- Content -->
        </div>
    </div>

    <script>
        /* Include JavaScript from HTML.md snippet (with dark mode toggle) */

        /* ADDITIONAL: Mermaid dark mode support */
        // Note: Mermaid diagrams are rendered once on page load. To support dynamic theme
        // switching for Mermaid, you would need to re-render diagrams when theme changes.
        // For now, diagrams use CSS background changes which is sufficient for most cases.
        // If you need full Mermaid theme switching, initialize Mermaid with theme detection:

        document.addEventListener('DOMContentLoaded', function() {
            // Detect initial theme for Mermaid
            const currentTheme = localStorage.getItem('theme') || 'light';

            // If using Mermaid, initialize with appropriate theme
            if (typeof mermaid !== 'undefined') {
                mermaid.initialize({
                    startOnLoad: true,
                    theme: currentTheme === 'dark' ? 'dark' : 'base',
                    themeVariables: currentTheme === 'dark' ? {
                        // Dark theme variables for Mermaid
                        background: '#1e1e1e',
                        primaryColor: '#bb86fc',
                        primaryTextColor: '#e0e0e0',
                        primaryBorderColor: '#bb86fc',
                        lineColor: '#888',
                        secondaryColor: '#03dac6',
                        tertiaryColor: '#cf6679',
                        mainBkg: '#2a2a2a',
                        textColor: '#e0e0e0',
                        nodeBorder: '#888',
                        // Sequence diagram
                        actorBkg: '#3a3a3a',
                        actorBorder: '#888',
                        actorTextColor: '#e0e0e0',
                        signalColor: '#e0e0e0',
                        signalTextColor: '#e0e0e0',
                        labelBoxBkgColor: '#bb86fc',
                        labelTextColor: '#000',
                        noteBkgColor: '#3a3a3a',
                        noteTextColor: '#e0e0e0',
                        noteBorderColor: '#888'
                    } : {
                        // Light theme variables (from HTML.md)
                        background: '#F5F0E8',
                        primaryColor: '#7A1712',
                        primaryTextColor: '#1a1a1a',
                        primaryBorderColor: '#6B4423',
                        lineColor: '#4A5568',
                        secondaryColor: '#1B3A57',
                        tertiaryColor: '#2D5016',
                        mainBkg: '#EDE8DC',
                        textColor: '#1a1a1a',
                        nodeBorder: '#6B4423'
                    }
                });
            }
        });
    </script>
</body>
</html>
```

**Pedagogical Enhancements Summary**:
- ✅ Learning Objectives section (sets expectations)
- ✅ Background & Key Concepts cards (foundational understanding)
- ✅ "How This Works" architecture overview (system-level comprehension)
- ✅ Difficulty badges on steps (complexity signaling)
- ✅ Concept tags linking steps to concepts (reinforce learning)
- ✅ Rationale boxes explaining "why" (decision-making)
- ✅ Common pitfalls inline with steps (preemptive debugging)
- ✅ Step-level verification (incremental testing)
- ✅ Common Misunderstandings section (address misconceptions)
- ✅ Further Reading & Resources (deeper learning paths)

---

## Phase 4: File Handling (After Review)
**IMPORTANT**: These steps happen AFTER the review is complete and plan is updated.

1. **Create directory**: Ensure `claude_html/` exists in current working directory using: `mkdir -p claude_html`
   - *Why `claude_html/`*: Conventional location for AI-generated HTML artifacts; easy to `.gitignore`

2. **Write to file**: `claude_html/plan_[task_description].html`
   - *File naming*: Descriptive names like `plan_add_auth.html` make plans easy to find later

3. **Open automatically**: `open claude_html/plan_[task_description].html`
   - *Immediate feedback*: Opening the browser lets user review visually without searching for the file

4. **Inform user**: "Pedagogical plan reviewed by Codex and saved as claude_html/plan_[task_description].html (now open)"

---

## Phase 5: User Confirmation
After the reviewed plan is displayed:
1. Present the plan (which now includes review summary and pedagogical elements)
2. Ask the user: "Review the plan (which has been critiqued by Codex and includes learning scaffolding). Would you like me to:
   - Proceed with implementation
   - Make additional revisions
   - Discuss concepts before proceeding
   - Clarify any design decisions"
3. Wait for user confirmation before executing any steps
4. If user requests changes, update the plan HTML accordingly

**Why user approval is mandatory**:
- **Respects autonomy**: User may have context you don't (budget, timeline, preferences)
- **Prevents wasted work**: Starting without approval risks doing the wrong thing correctly
- **Builds trust**: Users feel in control, not steamrolled by automation
- **Enables learning**: User may want to understand concepts better before proceeding

---

## Key Principles (ENHANCED)
- **NEVER skip planning** - Always create the plan first
  - *Why*: "Hours of coding can save minutes of planning" is false wisdom

- **ALWAYS review before display** - Use Codex MCP (preferred) or Task agent fallback
  - *Why*: Independent review catches blind spots

- **TEACH, don't just instruct** - Every plan is a learning opportunity
  - *Why*: Users who understand systems can extend, debug, and maintain code independently

- **Explain the "why"** - Justify design decisions with rationale boxes
  - *Why*: Decision-making process is as valuable as the decisions themselves

- **Preempt mistakes** - Call out common pitfalls inline
  - *Why*: Prevention is cheaper than debugging

- **Provide scaffolding** - Concept tags, difficulty badges, verification steps
  - *Why*: Reduces cognitive load and builds confidence

- **Link to resources** - Curate high-quality learning materials
  - *Why*: Users learn at different depths—some want basics, others want mastery

- **Wait for review results** - Do NOT write HTML until review is complete
  - *Why*: Reviewing the final plan is more valuable than reviewing a draft

- **Incorporate feedback** - Update plan based on review before finalizing
  - *Why*: Review is pointless if you ignore it

- **Be specific** - Vague plans lead to confusion
  - *Why*: "Add authentication" means nothing; "Create `auth/jwt.ts` with `verifyToken()` function" is actionable

- **Think holistically** - Consider the entire system, not just the immediate task
  - *Why*: Local optimizations can harm global architecture

- **Use HTML snippet styles** - Search for HTML.md for the single source of truth
  - *Why*: Consistency across all plans; proven visual design

- **Progressive disclosure** - Important info visible, details collapsed
  - *Why*: Cognitive load management—show summary first, details on demand

- **Two-column layout** - Use columns for density and organization
  - *Why*: Humans scan left-to-right efficiently; columns fit more in viewport

- **Visual hierarchy** - Use colors and borders to indicate importance
  - *Why*: Red border = critical, muted text = secondary—instant prioritization

- **User approval required** - Never execute without confirmation
  - *Why*: Automation without consent erodes trust

---

## Workflow Summary
```
User Request
  → CREATE PEDAGOGICAL PLAN (draft in memory with learning scaffolding)
      ↓
  → REVIEW PLAN (Codex MCP or Task agent - assess pedagogical quality too)
      ↓ [Wait for feedback]
  → INCORPORATE FEEDBACK
      ↓
  → WRITE HTML (with review summary + all pedagogical enhancements)
      ↓
  → OPEN FILE (auto-open in browser)
      ↓
  → User Reviews Plan & Learns Concepts
      ↓
  → User Approves/Revises/Asks Questions
      ↓
  → Execute Steps (with confirmation)
```

This ensures:
1. **Thoughtful, organized planning** - Structured approach reduces cognitive load
2. **Mandatory quality review** - Independent critique catches flaws early
3. **Pedagogical richness** - Users learn concepts, not just steps
4. **Plan improvements BEFORE user sees it** - Users see vetted, improved plans
5. **User sees final, reviewed plan with learning scaffolding** - Transparency + education
6. **Better decision-making with vetted plan** - Confidence to proceed or revise
7. **Conceptual understanding** - Users can maintain and extend code independently

---

## Pedagogical Summary: Why This Approach Works

**Cognitive Load Theory**: Breaking complex tasks into structured phases (Plan → Review → Execute) reduces working memory demands. Adding concept explanations and visual scaffolding further reduces load.

**Constructivist Learning**: Users build understanding by connecting new concepts to existing knowledge (via analogies, mental models). Rationale boxes teach decision-making patterns.

**Fail-Fast Principle**: Catching errors in planning (cheapest phase) is 100x cheaper than catching them in production.

**Zone of Proximal Development**: Difficulty badges and incremental verification help users work at the edge of their competence—not too easy (boring), not too hard (frustrating).

**Collaborative Intelligence**: Human creativity + AI critique > Either alone. The review step leverages AI's pattern recognition without replacing human judgment.

**Iterative Refinement**: The review loop ensures plans improve before execution, not after failure.

**User-Centered Design**: Mandatory approval respects user autonomy and context that AI cannot fully understand.

**Transfer of Learning**: By teaching concepts and decision-making, users can apply patterns to future problems independently—not just this one task.

**This is not just planning—it's apprenticeship at scale.**
</planhtml>
