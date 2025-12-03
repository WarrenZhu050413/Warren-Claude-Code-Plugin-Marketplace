---
name: "Generating HTML"
description: "This snippet should be used when creating user-journey-optimized HTML documents that guide readers through a clear narrative arc with curated content and dark mode support."
---

Create journey-focused HTML documents that guide users from context → insight → action.

## Workflow (MANDATORY)

1. **Setup**: `mkdir -p claude_files/html`
2. **Read template**: `${CLAUDE_PLUGIN_ROOT}/templates/html/base-template.html`
3. **Write** entire template to `claude_files/html/{description}.html` (no modifications)
4. **Edit** `{{TITLE}}` → actual title
5. **Edit** `<!-- ===== CONTENT GOES HERE ===== -->` → actual content
6. **Open**: `open claude_files/html/{description}.html`

**Violations → STOP:**
- Writing `<!DOCTYPE html>` manually
- Writing `<style>` tags
- Generating HTML from scratch
- Using hardcoded colors
- Skipping Read step

## File Handling

1. Create: `mkdir -p claude_files/html`
2. Write to: `claude_files/html/{description}.html` (lowercase, kebab-case)
3. Open: `open claude_files/html/{description}.html`
4. Inform user

**Naming convention:**
- Lowercase, kebab-case (e.g., `api-comparison.html`, `youtube-tutorial.html`)
- NO underscores (use hyphens instead)

## Templates

- **Base**: `${CLAUDE_PLUGIN_ROOT}/templates/html/base-template.html` (CSS, JS, structure)
- **Plan**: `${CLAUDE_PLUGIN_ROOT}/templates/html/plan-template.html` (for PLANHTML)
- **Examples**: `${CLAUDE_PLUGIN_ROOT}/templates/html/examples.md`

**Workflow**: Read → Write → Edit (preserves CSS exactly)

## CSS Rules

**NEVER use hardcoded colors** - use CSS variables or existing classes

**Checklist:**
- [ ] Read → Write → Edit workflow
- [ ] Edit content section only
- [ ] Use existing CSS classes
- [ ] NO inline styles with hardcoded colors
- [ ] Code blocks in `<pre><code>`
- [ ] Mermaid in `.diagram-container`

## Principles

**CORE PHILOSOPHY: Less is more. Curate ruthlessly.**

- **Journey-first** - Every element moves the user forward: Context → Understanding → Action
- **Curate, don't dump** - Include only what serves the journey; omit everything else
- **Visual anchors** - One diagram per section max; use Mermaid for concepts that need visualization
- **Scannable hierarchy** - User should grasp the arc in 10 seconds from headers alone
- **Progressive depth** - Surface the answer first, collapse supporting evidence
- **Clear next steps** - End with actionable takeaways, not more information

**Anti-patterns to AVOID:**
- ❌ Including everything "just in case"
- ❌ Multiple diagrams competing for attention
- ❌ Dense bullet lists without synthesis
- ❌ Information without interpretation
- ❌ Collapsibles hiding essential content

**Color coding:** Red=critical, Gold=important, Green=good, Gray=muted

## User Journey Structure

Every HTML document should follow this arc:

### 1. HOOK (What & Why) — `.important-always-visible`
- One-sentence summary of the core insight
- Why this matters to the user RIGHT NOW
- **Limit:** 2-3 bullet points max

### 2. CONTEXT (Background) — `.primary-section` or brief prose
- Only context needed to understand the insight
- Skip if the user already knows this
- **Limit:** One short paragraph or 3-5 bullets

### 3. INSIGHT (The meat) — Mermaid + `.two-column-layout`
- The key finding, comparison, or recommendation
- ONE visual diagram if it aids understanding
- Synthesize—don't list raw data
- **Limit:** One diagram, one comparison block

### 4. EVIDENCE (Supporting) — `.collapsible` (collapsed)
- Technical details, logs, raw data
- For users who want to verify, not required reading
- **Limit:** Collapse aggressively

### 5. ACTION (Next steps) — `.card.priority` or bold list
- What the user should DO with this information
- Concrete, specific, actionable
- **Limit:** 3 actions max

## Component Selection

| Journey Stage | Component | Content Type |
|---------------|-----------|--------------|
| Hook | `.important-always-visible` | TL;DR, key takeaway |
| Context | Brief prose or bullets | Background needed |
| Insight | Mermaid + `.two-column-layout` | Core analysis |
| Evidence | `.collapsible` (closed) | Supporting details |
| Action | `.card.priority` | Next steps |

**Decision Tree:**
- Is it the main takeaway? → **`.important-always-visible`** (always visible, never collapsed)
- Is it a process/relationship? → **ONE Mermaid diagram** (pick the most important view)
- Is it a comparison? → **`.two-column-layout`** (max one per document)
- Is it supporting evidence? → **`.collapsible`** (collapsed by default)
- Is it actionable? → **`.card.priority`** at the END

## Code Blocks

- Inline: `<code>text</code>`
- Multiline: `<pre><code>text</code></pre>`
- Never raw code in `<div>`

## Mermaid Diagrams

**Rule: ONE diagram per document.** Pick the single most illuminating view.

**Ask before adding a diagram:**
- Does this concept NEED visualization, or can prose explain it?
- Is there already a diagram? If yes, choose the better one, delete the other.
- Will users actually study this, or just skim past it?

**Basic structure:**
```html
<div class="diagram-container">
  <div class="mermaid">
flowchart TD
    Start --> Process --> End
  </div>
</div>
```

**Styling:**
- Prefer no inline styling (let theme handle colors)
- If needed: Use `classDef` with light text (`color:#fff`)
- NEVER `color:#000` in inline styles

**Examples**: See `${CLAUDE_PLUGIN_ROOT}/templates/html/examples.md`

## Common HTML Patterns

### Hook: The Takeaway (Journey Stage 1)
```html
<div class="important-always-visible">
    <h2>🎯 Bottom Line</h2>
    <p><strong>One sentence capturing the key insight.</strong></p>
    <ul>
        <li><strong>Impact:</strong> Why this matters</li>
        <li><strong>Recommendation:</strong> What to do</li>
    </ul>
</div>
```

### Insight: Comparison (Journey Stage 3)
```html
<div class="two-column-layout">
    <div>
        <h3>Option A</h3>
        <p>Synthesized pros/cons</p>
    </div>
    <div>
        <h3>Option B</h3>
        <p>Synthesized pros/cons</p>
    </div>
</div>
```

### Evidence: Supporting Details (Journey Stage 4)
```html
<div class="collapsible" data-collapsible="closed">
    <div class="collapsible-header">
        <span>📊 Technical Details</span>
        <span class="arrow">▶</span>
    </div>
    <div class="collapsible-content">
        <!-- Raw data, logs, extended analysis -->
    </div>
</div>
```

### Action: Next Steps (Journey Stage 5)
```html
<div class="card priority">
    <h3>📋 Next Steps</h3>
    <ol>
        <li><strong>First:</strong> Immediate action</li>
        <li><strong>Then:</strong> Follow-up action</li>
        <li><strong>Finally:</strong> Verification step</li>
    </ol>
</div>
```

## Content Curation Checklist

Before adding ANY content, ask:

- [ ] Does this move the user forward in their journey?
- [ ] Can I cut this in half and still convey the message?
- [ ] Is this interpretation or raw data? (prefer interpretation)
- [ ] Would a user skip this? If yes, collapse or remove it.
- [ ] Am I including this "just in case"? (if yes, delete it)

**Target:** A user should be able to understand the key insight in 30 seconds by reading only uncollapsed content.

## Implementation

1. Read template
2. Write entire template to destination
3. Edit `{{TITLE}}`
4. **Plan the journey** before writing content (Hook → Context → Insight → Evidence → Action)
5. Edit content section, applying curation checklist
6. **Review and cut** 20% of what you wrote
7. Open in browser and test dark mode

## Reference

- **Base Template**: `${CLAUDE_PLUGIN_ROOT}/templates/html/base-template.html`
- **Examples**: `${CLAUDE_PLUGIN_ROOT}/templates/html/examples.md`
