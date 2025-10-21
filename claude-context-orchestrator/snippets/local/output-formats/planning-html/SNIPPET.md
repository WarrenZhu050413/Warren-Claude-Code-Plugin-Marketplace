---
description: Creating technical execution plans in HTML format with mandatory review
SNIPPET_NAME: planning-html
ANNOUNCE_USAGE: true
---

## Purpose

Create clear, actionable technical execution plans with mandatory quality review before display.

## Philosophy: Plans as Execution Roadmaps

Plans should provide clear, efficient paths from problem to solution. Focus on technical accuracy, architectural clarity, and actionable steps.

**Core Principle**: Users should have a complete understanding of WHAT needs to be built, HOW it fits together, and a clear execution path.

## Phase 1: Planning (REQUIRED FIRST)

ALWAYS create a comprehensive plan BEFORE taking any action. DO NOT skip this step.

### Why Planning Matters

Breaking complex tasks into structured plans reduces errors and enables efficient execution. Planning helps you:

- **Avoid thrashing**: Clear path prevents wasted effort
- **Catch dependencies early**: Proper sequencing prevents rework
- **Set realistic expectations**: Clear scope and timeline
- **Enable parallelization**: Identify independent tasks

### Planning Best Practices

1. **Think Before Acting**: Analyze requirements, constraints, and existing systems
2. **Break Down Complexity**: Decompose into specific, actionable steps
3. **Consider Dependencies**: Identify sequential vs parallel work
4. **Anticipate Edge Cases**: Plan for error conditions and failure modes
5. **Define Success Criteria**: Specify testable completion conditions
6. **Progressive Refinement**: Start high-level, then add detail

### Plan Structure Requirements

Your plan MUST include these sections:

#### 1. High-Level Overview (ALWAYS FIRST - Always Visible)

**Purpose**: Provide immediate visual and conceptual understanding of the system

**Content Requirements**:
- **Visual Diagram**: Mermaid diagram (flowchart, sequence, or component) OR ASCII art
- **System Summary**: 2-3 sentences describing what's being built
- **Key Components**: List of major system components
- **Data Flow**: Brief description of how data moves through the system

**Why Diagram First**: A picture is worth 1000 words. Stakeholders understand architecture visually faster than reading text.

**Diagram Guidelines**:
- Use Mermaid for interactive diagrams (flowchart, sequence, graph)
- Use ASCII art for simple structures or when Mermaid is overkill
- Show relationships between components
- Highlight critical paths or data flows

**Example**:

```
🏗️ System Architecture Overview

[Mermaid Flowchart Here]

**System Summary**: Chrome extension that captures webpage elements and saves them to a persistent canvas using Shadow DOM isolation and chrome.storage for cross-context state management.

**Key Components**:
- Background Worker (service worker, manages storage)
- Content Script (injected into pages, captures elements)
- Canvas UI (React app, displays saved elements)
- Storage Layer (chrome.storage.local, source of truth)

**Data Flow**: User triggers capture → Content script extracts element → Background worker persists to storage → Canvas UI reacts to storage change → UI updates
```

#### 2. Executive Summary (Always Visible)

**Purpose**: Give stakeholders a 30-second understanding without reading details

**Content Requirements**:
- **Problem Statement**: What is being requested and why
- **Proposed Solution**: High-level technical approach (2-3 sentences)
- **Key Technical Decisions**: Critical architectural choices
- **Estimated Complexity**: Rough time/effort estimate
- **Dependencies**: External libraries, APIs, or systems required

#### 3. Prerequisites & Context (Collapsible)

**Purpose**: Ensure all dependencies are met before starting work

**Content Requirements**:
- Files/directories that need to be examined
- Existing code patterns to understand
- Dependencies or blockers
- Environment setup requirements

**Example**:
- Review existing Chrome extension manifest structure
- Understand current storage patterns in codebase
- Verify React and Vite are configured
- Check if DOMPurify is already installed

#### 4. Step-by-Step Implementation (Primary Focus - Always Visible)

**Purpose**: Provide a clear, numbered execution roadmap

**Content Requirements**:
- Numbered steps in logical order
- Each step should be specific and actionable
- Include file paths and function names
- Mark dependencies between steps
- Indicate which steps can be done in parallel
- Include brief technical notes where needed

**Example Step Format**:

```html
<li>
  <strong>Step 3:</strong> Create <code>src/content/ElementSelector.tsx</code> - React component for hover overlay

  <div class="indent-1">
    <strong>Key functions</strong>:
    - <code>handleMouseMove(e)</code>: Update overlay position based on cursor
    - <code>handleClick(e)</code>: Capture element HTML and metadata
    - <code>injectStyles()</code>: Add styles to Shadow DOM
  </div>

  <div class="indent-1 muted">
    File: src/content/ElementSelector.tsx
  </div>

  <div class="tech-note">
    <strong>Technical Note:</strong> Use absolute positioning with z-index: 2147483647 to ensure overlay appears above all page content. Inject styles into Shadow DOM to prevent page CSS conflicts.
  </div>
</li>
```

#### 5. Testing & Validation (Collapsible)

**Purpose**: Define how to verify implementation correctness

**Content Requirements**:
- How to verify each major step works
- Test cases to run (happy path and edge cases)
- Expected outcomes
- Common test failures and debugging steps

#### 6. Potential Issues & Mitigations (Collapsible)

**Purpose**: Anticipate problems and prepare solutions

**Content Requirements**:
- Edge cases to consider
- Common pitfalls (technical issues, not learning mistakes)
- Fallback strategies
- Performance considerations
- Security considerations

#### 7. Post-Implementation (Collapsible)

**Purpose**: Ensure sustainability beyond initial deployment

**Content Requirements**:
- Documentation that needs to be written
- Follow-up tasks or future enhancements
- Maintenance considerations
- Monitoring or observability needs

## Phase 2: MANDATORY PLAN REVIEW (Before HTML Output)

**CRITICAL**: Do NOT write the HTML plan file until AFTER it has been reviewed.

### Why Review Matters

Plan review catches issues before any code is written. Independent review identifies:
- Technical inaccuracies
- Missing steps or edge cases
- Better architectural approaches
- Security vulnerabilities
- Implementation risks

### Review Flow:

1. **Draft the plan** (in memory, as structured content)
2. **Launch Codex MCP review** (preferred) OR **Task agent** (fallback)
3. **Wait for review results**
4. **Incorporate feedback** into the plan
5. **THEN write the HTML file**

### Using Codex MCP for Review (Preferred):

```typescript
mcp__codex__codex({
  prompt: `Review the following technical implementation plan and provide critical analysis:

[PLAN SUMMARY - Include key sections: Overview, Executive Summary, Implementation Steps]

Analyze:
1. **Technical Accuracy**: Are the proposed solutions technically sound?
   - Check for API misuse, incorrect algorithms, architecture anti-patterns

2. **Implementation Completeness**: Are there missing steps or edge cases?
   - Look for unstated assumptions, missing error handling, incomplete workflows

3. **Architecture**: Is this the best architectural choice?
   - Consider scalability, maintainability, testability tradeoffs

4. **Security Considerations**: Any security issues with the approach?
   - Check for injection vulnerabilities, authentication gaps, data exposure

5. **Code Quality**: Review code snippets for correctness and best practices
   - Check syntax, idioms, performance implications

6. **Testing Strategy**: Is the testing approach comprehensive enough?
   - Verify test coverage of happy path, edge cases, error conditions

7. **Risk Assessment**: What are the biggest risks?
   - Identify show-stoppers, performance bottlenecks, user impact

Provide specific, actionable recommendations for improvement.`,
  cwd: "[current working directory]",
});
```

### Fallback: Task Agent Review (if Codex unavailable):

```typescript
Task({
  subagent_type: "general-purpose",
  description: "Review and critique plan",
  prompt: `Review the following technical implementation plan:

[PLAN SUMMARY]

Provide:
1. **Strengths**: Well-thought-out aspects
2. **Potential Issues**: Problems or edge cases missed
3. **Suggestions**: How to improve the plan
4. **Risk Assessment**: Biggest technical risks
5. **Alternative Approaches**: Better ways to accomplish this

Be critical. Look for:
- Missing error handling
- Overlooked dependencies
- Performance/scalability concerns
- Security vulnerabilities
- Testing gaps
- Unclear technical specifications`,
});
```

### Detection Logic:

```javascript
// Check if Codex MCP is available
if (typeof mcp__codex__codex === 'function') {
  // Use Codex MCP review (preferred for technical accuracy)
  await mcp__codex__codex({...});
} else {
  // Fallback to Task agent
  await Task({subagent_type: "general-purpose", ...});
}
```

### Incorporating Review Feedback:

1. **Analyze the critique** - Identify valid concerns
2. **Update the plan** - Address major issues and suggestions
3. **Document changes** - Note what was revised based on review
4. **Add a "Review Summary" section** showing:
   - Key feedback received
   - Changes made in response
   - Risks acknowledged but accepted (with rationale)

## Phase 3: HTML Output Formatting (After Review)

### HTML Style Guide Reference

**CRITICAL**: For PLANHTML documents, ALWAYS use the plan template at `${CLAUDE_PLUGIN_ROOT}/templates/html/plan-template.html`.

Do NOT use base-template.html for plans - the plan template includes all necessary styles PLUS plan-specific pedagogical elements (difficulty badges, concept cards, rationale boxes, etc.).

**Why HTML instead of Markdown**:
- Interactive collapsibles for information density
- Visual hierarchy with colors and borders
- Dark mode support
- Mermaid diagram rendering
- Professional presentation

**The plan template contains**:
- All styles from the base template
- Plan-specific structure
- Collapsible sections
- Mermaid support
- Dark mode toggle

### Implementation Workflow

1. **ALWAYS read the plan template FIRST**: `${CLAUDE_PLUGIN_ROOT}/templates/html/plan-template.html`
2. **Replace placeholders**: `{{TITLE}}` with plan title
3. **Fill in content sections** inside `<!-- ===== CONTENT GOES HERE ===== -->`
4. **Use Mermaid for diagrams**: Architecture, data flow, state machines
5. **Follow hierarchy**: Critical info first (always visible), details in collapsibles (closed by default)
6. **Test collapsibles**: Ensure expand/collapse all buttons work
7. **Save & open**: Write to `claude_html/` and open in browser

## Phase 4: File Handling (After Review)

**IMPORTANT**: These steps happen AFTER the review is complete and plan is updated.

1. **Create directory**: Ensure `claude_html/` exists using: `mkdir -p claude_html`
2. **Write to file**: `claude_html/plan_[task_description].html`
3. **Open automatically**: `open claude_html/plan_[task_description].html`
4. **Inform user**: "Technical plan reviewed by Codex and saved as claude_html/plan_[task_description].html (now open)"

## Phase 5: User Confirmation

After the reviewed plan is displayed:

1. Present the plan (which now includes review summary)
2. Ask: "Review the plan. Would you like me to:
   - Proceed with implementation
   - Make revisions to the plan
   - Clarify any technical decisions"
3. Wait for user confirmation before executing
4. If user requests changes, update the plan HTML

**Why user approval is mandatory**:
- User may have context you don't (budget, timeline, preferences)
- Prevents wasted work on wrong approach
- Builds trust and collaboration

## Key Principles

- **NEVER skip planning** - Always create the plan first
- **ALWAYS review before display** - Use Codex MCP (preferred) or Task agent fallback
- **Diagram first** - Visual architecture overview before text
- **Be specific** - File paths, function names, concrete steps
- **Anticipate issues** - Edge cases, failure modes, mitigations
- **Wait for review results** - Do NOT write HTML until review is complete
- **Incorporate feedback** - Update plan based on review
- **Use the plan template** - Reference `${CLAUDE_PLUGIN_ROOT}/templates/html/plan-template.html`
- **Progressive disclosure** - Critical info visible, details collapsed
- **User approval required** - Never execute without confirmation

## Workflow Summary

```
User Request
  → CREATE TECHNICAL PLAN (draft in memory with visual diagram)
      ↓
  → REVIEW PLAN (Codex MCP or Task agent - technical assessment)
      ↓ [Wait for feedback]
  → INCORPORATE FEEDBACK
      ↓
  → READ PLAN TEMPLATE (${CLAUDE_PLUGIN_ROOT}/templates/html/plan-template.html)
      ↓
  → WRITE HTML (with review summary)
      ↓
  → OPEN FILE (auto-open in browser)
      ↓
  → User Reviews Plan
      ↓
  → User Approves/Revises
      ↓
  → Execute Steps (with confirmation)
```

This ensures:
1. **Clear visual architecture** - Diagram provides immediate understanding
2. **Thoughtful, organized planning** - Structured approach reduces errors
3. **Mandatory quality review** - Independent critique catches flaws early
4. **Plan improvements BEFORE user sees it** - Users see vetted plans
5. **Better decision-making** - Confidence to proceed or revise
6. **Efficient execution** - Clear roadmap minimizes confusion
