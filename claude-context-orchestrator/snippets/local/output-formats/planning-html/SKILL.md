---
name: "Planning HTML"
description: "This snippet should be used when creating technical execution plans in HTML format with mandatory quality review before display."
---

Create clear, actionable technical execution plans with mandatory quality review before display.

## Phase 1: Planning (REQUIRED FIRST)

ALWAYS create a comprehensive plan BEFORE taking any action.

**Best Practices:**
- Analyze requirements, constraints, existing systems
- Decompose into specific, actionable steps
- Identify sequential vs parallel work
- Anticipate edge cases and failure modes
- Define testable completion conditions

### Plan Structure

#### 1. High-Level Overview (Always Visible)

**Must include**:
- **Visual Diagram**: Mermaid diagram (flowchart, sequence, component)
- **System Summary**: 2-3 sentences
- **Key Components**: List major components
- **Data Flow**: How data moves through system

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

**Must include**:
- **Problem Statement**: What and why
- **Proposed Solution**: High-level approach (2-3 sentences)
- **Key Technical Decisions**: Critical architectural choices
- **Estimated Complexity**: Rough time/effort
- **Dependencies**: External libraries, APIs, systems

#### 3. Prerequisites & Context (Collapsible)

- Files/directories to examine
- Existing code patterns to understand
- Dependencies or blockers
- Environment setup requirements

#### 4. Step-by-Step Implementation (Always Visible)

- Numbered steps in logical order
- Specific and actionable
- Include file paths and function names
- Mark dependencies
- Indicate parallel steps
- Brief technical notes where needed

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

- How to verify each major step
- Test cases (happy path and edge cases)
- Expected outcomes
- Common failures and debugging

#### 6. Potential Issues & Mitigations (Collapsible)

- Edge cases
- Common pitfalls
- Fallback strategies
- Performance considerations
- Security considerations

#### 7. Post-Implementation (Collapsible)

- Documentation needed
- Follow-up tasks
- Maintenance considerations
- Monitoring/observability

## Phase 2: MANDATORY PLAN REVIEW

**CRITICAL**: Do NOT write HTML until AFTER review.

### Review Flow

1. Draft plan (in memory)
2. Launch Codex MCP review (preferred) OR Task agent (fallback)
3. Wait for review results
4. Incorporate feedback
5. Write HTML file

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

### Incorporating Feedback

1. Analyze critique - identify valid concerns
2. Update plan - address major issues
3. Document changes
4. Add "Review Summary" section:
   - Key feedback received
   - Changes made
   - Risks acknowledged but accepted

## Phase 3: HTML Output (After Review)

**CRITICAL**: Use plan template at `${CLAUDE_PLUGIN_ROOT}/templates/html/plan-template.html`

### Workflow

1. Read plan template
2. Replace `{{TITLE}}`
3. Fill content in `<!-- ===== CONTENT GOES HERE ===== -->`
4. Use Mermaid for diagrams
5. Critical info visible, details collapsed
6. Save to `claude_html/` and open

## Phase 4: File Handling

1. Create directory: `mkdir -p claude_html`
2. Write to: `claude_html/plan_[task_description].html`
3. Open: `open claude_html/plan_[task_description].html`
4. Inform user

## Phase 5: User Confirmation

1. Present plan (includes review summary)
2. Ask: "Proceed with implementation / Make revisions / Clarify decisions?"
3. Wait for confirmation
4. Update plan HTML if changes requested

## Principles

- NEVER skip planning
- ALWAYS review before display
- Diagram first
- Be specific (file paths, function names)
- Anticipate issues
- Wait for review results
- Incorporate feedback
- Use plan template
- Progressive disclosure
- User approval required

## Workflow

```
User Request
  → Draft Plan (memory, with diagram)
  → Review (Codex MCP or Task agent)
  → Incorporate Feedback
  → Read Plan Template
  → Write HTML
  → Open File
  → User Reviews
  → User Approves
  → Execute
```
