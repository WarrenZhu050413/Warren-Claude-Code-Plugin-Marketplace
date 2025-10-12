<html_output>
---
description: Write compact, information-dense HTML content using full width with minimal spacing
SNIPPET_NAME: HTML
ANNOUNCE_USAGE: true
---

**INSTRUCTION TO CLAUDE**: At the very beginning of your response, before any other content, you MUST announce which snippet(s) are active using this exact format:

📎 **Active Context**: HTML

If multiple snippets are detected (multiple ANNOUNCE_USAGE: true directives in different snippets), combine them into a single announcement:

📎 **Active Contexts**: snippet1, snippet2, snippet3

---

When providing explanations, documentation, or informational content:

## Primary Purpose

**VERIFICATION_HASH:** `b6491b8c313273ea`

The HTML output should prioritize **important information first** with **progressive disclosure** through:
- Critical information prominently displayed and always visible
- Secondary details in collapsible sections (closed by default)
- Visual hierarchy using progressive indentation and typography weights
- Color-coded importance levels (critical, important, normal, muted)
- Grouped content by priority with expandable details
- Smart use of space with folded content for better focus

## File Handling Instructions
1. **ALWAYS** create a `claude_html/` directory in the current working directory if it doesn't exist using: `mkdir -p claude_html`
2. Write the HTML content to a file named `claude_html/{description_of_the_subject}.html`, where {description_of_the_subject} is a lowercase, underscore-separated description of the content (e.g., `claude_html/git_analysis.html`, `claude_html/code_review.html`, `claude_html/project_overview.html`)
3. After writing the file, use the Bash tool to open it with: `open claude_html/{description_of_the_subject}.html` (macOS) or appropriate command for the OS
4. Inform the user that the HTML has been saved as `claude_html/{description_of_the_subject}.html` and opened

## Template System

**Base Template:** `${CLAUDE_PLUGIN_ROOT}/templates/html/base-template.html`
- Contains all CSS styles, JavaScript, and HTML structure
- Ready to use - just add content in the container div
- Includes dark mode toggle, collapsibles, Mermaid support

**Examples & Reference:** `${CLAUDE_PLUGIN_ROOT}/templates/html/examples.md`
- Complete component examples
- Mermaid diagram patterns
- Layout patterns
- Best practices

**Workflow:**
1. Read the base template: `${CLAUDE_PLUGIN_ROOT}/templates/html/base-template.html`
2. Replace `{{TITLE}}` with appropriate title
3. Add content inside `<!-- ===== CONTENT GOES HERE ===== -->` section
4. Reference examples.md for component patterns if needed

## Design Principles

### Compact Design
- **⚠️ NO ASCII ART DIAGRAMS**: NEVER use ASCII art for architecture/flow diagrams (like `┌─────┐`, `│`, `└─────┘`). ALWAYS use Mermaid diagrams instead.
- **Visual Communication Priority**: When explaining systems, architectures, flows, or relationships, STRONGLY PREFER Mermaid diagrams over prose. See examples at `${CLAUDE_PLUGIN_ROOT}/templates/html/examples.md`
- **Two-Column Priority**: Default to two-column layout for maximum information density
- **Full Width Usage**: Eliminate side margins, use entire browser width
- **Progressive Detail**: Most important info at top, details nested below
- **Collapsible Everything**: All sections should support expand/collapse functionality

### Progressive Disclosure Requirements
1. **Two-Column Default**: Use two-column layout as the default for maximum density
2. **Important First**: Critical information always visible at the top
3. **Collapsible Everything**: All sections should be collapsible, with secondary info collapsed by default
4. **Visual Hierarchy**: Use primary/secondary/tertiary sections with distinct borders
5. **Progressive Indentation**: Each level indents further (0px, 8px, 16px, 24px)
6. **Typography Weight**: Heavier fonts for important, lighter for details
7. **Color Coding**: Red=critical, Gold=important, Green=good, Gray=muted

## Component Selection Guide

**Quick reference for choosing the right HTML components:**

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

## Chinese Color Palette (Light + Dark Mode)

The template includes a warm, earthy Chinese-inspired color palette:

**Light Mode:**
- Chinese Red (#8B0000): Primary accent, buttons, highlights
- Chinese Gold (#FFD700): Secondary accent, borders, emphasis
- Jade Green (#00A86B): Success states, call-to-action
- Ink Black (#2B2B2B): Main text
- Paper Beige (#F5F5DC): Background base
- Light Cream (#FAFAF0): Content backgrounds

**Dark Mode:**
- Automatically switches with localStorage persistence
- Fixed toggle button (top-right corner)
- All colors optimized for dark backgrounds

## Code Block Rules (CRITICAL)

**⚠️ ALWAYS wrap multiline code in `<pre><code>` tags to preserve formatting!**

**✅ CORRECT - Multiline code block:**
```html
<pre><code>def hello_world():
    print("Hello, World!")
    return True</code></pre>
```

**✅ CORRECT - Inline code:**
```html
<p>Use the <code>print()</code> function to output text.</p>
```

**❌ WRONG - Missing pre/code tags (newlines will collapse):**
```html
<div class="code-block">
def hello_world():
    print("Hello, World!")
</div>
```

**Key Rules:**
1. **Inline code** (within sentences): Use `<code>text</code>`
2. **Multiline code blocks**: Use `<pre><code>text</code></pre>`
3. **Never** put raw code directly in `<div>` without `<pre><code>` wrappers

## Mermaid Diagram Integration

### When to Use Mermaid (STRONGLY ENCOURAGED)

**Visual-First Principle**: When explaining systems, architectures, flows, or relationships, PREFER diagrams over prose.

**ALWAYS USE diagrams for:**
- ✅ System architecture and component interactions
- ✅ Data flow and ETL pipelines
- ✅ API interactions and authentication flows
- ✅ State machines and workflow transitions
- ✅ Database schemas and entity relationships
- ✅ Process flows and decision trees

**When text is better:**
- ❌ Simple 2-3 step linear sequences (use numbered lists)
- ❌ Complex business logic with nuanced rules (use prose)
- ❌ Dense data tables (use HTML tables)

### Diagram Usage

The base template includes:
- Mermaid.js from CDN
- Theme detection (light/dark mode support)
- Chinese color palette for custom styling

**Basic structure:**
```html
<div class="diagram-container">
    <div class="mermaid">
flowchart TD
    Start --> Process
    Process --> End
    </div>
</div>
```

**For complete examples**, see `${CLAUDE_PLUGIN_ROOT}/templates/html/examples.md`:
- Flowcharts (process flows)
- Sequence diagrams (API interactions)
- State diagrams (state machines)
- ERD diagrams (database schemas)
- Custom styled diagrams (Chinese palette)

### Mermaid Templates

Ready-to-use templates available at `~/.claude/templates/mermaid/`:
- `architecture-3tier.mmd` - Classic web app architecture
- `architecture-microservices.mmd` - Microservices with gateway
- `dataflow-etl.mmd` - ETL pipeline with validation
- `sequence-api-auth.mmd` - Authentication flows
- `state-workflow.mmd` - Document/entity workflows
- `erd-database.mmd` - Database schema design

**Usage**: Read template file, customize labels for your scenario, embed in HTML.

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

### Full-Width Collapsible in Two-Column Layout
```html
<div class="two-column-layout">
    <div class="collapsible" data-collapsible="closed">
        <div class="collapsible-header">
            <span>Left Section</span>
            <span class="arrow">▶</span>
        </div>
        <div class="collapsible-content">Left content</div>
    </div>

    <div class="collapsible" data-collapsible="closed">
        <div class="collapsible-header">
            <span>Right Section</span>
            <span class="arrow">▶</span>
        </div>
        <div class="collapsible-content">Right content</div>
    </div>

    <!-- This spans both columns -->
    <div class="collapsible full-width" data-collapsible="closed">
        <div class="collapsible-header">
            <span>Full Width Section</span>
            <span class="arrow">▶</span>
        </div>
        <div class="collapsible-content">Full-width content</div>
    </div>
</div>
```

### Status Indicators
```html
<span class="critical">Critical</span>
<span class="warning">Warning</span>
<span class="success">Success</span>
<span class="muted">Less important</span>
```

### Table
```html
<table>
    <thead>
        <tr>
            <th>Column 1</th>
            <th>Column 2</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Data 1</td>
            <td>Data 2</td>
        </tr>
    </tbody>
</table>
```

## Implementation Workflow

1. **Read the base template**: `${CLAUDE_PLUGIN_ROOT}/templates/html/base-template.html`
2. **Customize title**: Replace `{{TITLE}}`
3. **Add content**: Insert HTML inside the container div
4. **Use components**: Reference the Component Selection Guide above
5. **Add diagrams**: Use Mermaid for architecture/flows (see examples.md)
6. **Follow hierarchy**: Important info first, details in collapsibles
7. **Test dark mode**: Toggle works automatically
8. **Save & open**: Write to `claude_html/` and open in browser

## Reference Files

- **Base Template**: `${CLAUDE_PLUGIN_ROOT}/templates/html/base-template.html` - Complete HTML structure with all styles
- **Examples**: `${CLAUDE_PLUGIN_ROOT}/templates/html/examples.md` - Component patterns and complete page examples
- **Mermaid Templates**: `~/.claude/templates/mermaid/*.mmd` - Ready-to-use diagram templates

## Self-Contained Requirements
- No external dependencies (no CDN links, external stylesheets, or scripts) - EXCEPT for Mermaid diagrams which may use CDN
- All styling is included in the base template
- Ensure the HTML renders properly in any modern browser
- Dark mode and collapsibles work automatically via included JavaScript
</html_output>
