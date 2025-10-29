---
name: "Generating HTML"
description: "This snippet should be used when creating information-dense HTML documents using full width with minimal spacing, progressive disclosure through collapsibles, and dark mode support."
---

Create information-dense HTML documents with progressive disclosure and dark mode support.

## Workflow (MANDATORY)

1. **Setup**: `mkdir -p claude_html` + add to .gitignore
2. **Read template**: `${CLAUDE_PLUGIN_ROOT}/templates/html/base-template.html`
3. **Write** entire template to `claude_html/{description}.html` (no modifications)
4. **Edit** `{{TITLE}}` → actual title
5. **Edit** `<!-- ===== CONTENT GOES HERE ===== -->` → actual content
6. **Open**: `open claude_html/{description}.html`

**Violations → STOP:**
- Writing `<!DOCTYPE html>` manually
- Writing `<style>` tags
- Generating HTML from scratch
- Using hardcoded colors
- Skipping Read step

## File Handling

1. Create: `mkdir -p claude_html`
2. Add to gitignore (if git repo)
3. Write to: `claude_html/{description}.html` (lowercase, underscores)
4. Open: `open claude_html/{description}.html`
5. Inform user

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

- **NO ASCII ART** - use Mermaid diagrams
- **Visual first** - Mermaid for systems/flows/architecture
- **Two-column** default for density
- **Full width** - no side margins
- **Progressive disclosure** - important first, details collapsed
- **Color coding** - Red=critical, Gold=important, Green=good, Gray=muted

## Component Selection Guide

Quick reference for choosing the right HTML components:

| Use Case | Component | When to Use |
|----------|-----------|-------------|
| Critical always-visible info | `.important-always-visible` | System status, critical deadlines |
| Primary content section | `.primary-section` | Main findings, core results |
| Two-option comparison | `.two-column-layout` | Before/after, alternatives |
| Supporting details | `.collapsible` (closed) | Technical details, full logs |
| Priority information | `.card.priority` | Key recommendations |
| System architecture | Mermaid flowchart with subgraphs | Component interactions |
| Data flow | Mermaid flowchart LR | ETL pipelines |
| API interactions | Mermaid sequence diagram | Request/response flows |
| State machine | Mermaid state diagram | Workflow states |
| Database schema | Mermaid ERD | Entity relationships |

**Decision Tree:**
- Need to show structure/flow? → **Use Mermaid diagram** (examples in `${CLAUDE_PLUGIN_ROOT}/templates/html/examples.md`)
- Comparing 2 options? → **Use `.two-column-layout`**
- Critical information? → **Use `.important-always-visible`**
- Supporting detail? → **Use `.collapsible`** (collapsed by default)
- Tabular data? → **Use `<table>`**

## Code Blocks

- Inline: `<code>text</code>`
- Multiline: `<pre><code>text</code></pre>`
- Never raw code in `<div>`

## Mermaid Diagrams

**Use for:** Architecture, data flow, API interactions, state machines, DB schemas, process flows

**Basic structure:**
```html
<div class="diagram-container">
  <div class="mermaid">
flowchart TD
    Start --> Process --> End
  </div>
</div>
```

**Examples**: See `${CLAUDE_PLUGIN_ROOT}/templates/html/examples.md`

### Mermaid Styling

**Rules:**
1. Prefer no inline styling (let theme handle colors)
2. If needed: Use `classDef` with light text (`color:#fff`)
3. NEVER `color:#000` in inline styles
4. Test both light/dark modes

## Common HTML Patterns

### Always-Visible Important Content
```html
<div class="important-always-visible">
    <h2>🎯 Critical Information</h2>
    <div class="two-column-layout">
        <ul class="dense-list">
            <li><strong>Key Point:</strong> Detail</li>
        </ul>
    </div>
</div>
```

### Collapsible Section
```html
<div class="collapsible" data-collapsible="closed">
    <div class="collapsible-header">
        <span>📊 Section Title</span>
        <span class="arrow">▶</span>
    </div>
    <div class="collapsible-content">
        <!-- Content here -->
    </div>
</div>
```

### Two-Column Layout
```html
<div class="two-column-layout">
    <div>Left content</div>
    <div>Right content</div>
</div>
```

## Implementation

1. Read template
2. Write entire template to destination
3. Edit `{{TITLE}}`
4. Edit content section
5. Open in browser and test dark mode

## Reference

- **Base Template**: `${CLAUDE_PLUGIN_ROOT}/templates/html/base-template.html`
- **Examples**: `${CLAUDE_PLUGIN_ROOT}/templates/html/examples.md`
