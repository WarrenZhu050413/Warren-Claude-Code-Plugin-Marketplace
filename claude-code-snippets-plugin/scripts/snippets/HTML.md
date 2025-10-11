<html_output>
---
description: Write compact, information-dense HTML content using full width with minimal spacing
---




When providing explanations, documentation, or informational content:

## Primary Purpose

**VERIFICATION_HASH:** `8c73bf20e73d10f9`

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

## Snippet Storage Location
**NOTE:** This HTML output snippet is stored in the Claude Code snippets plugin at:
- **Path:** `~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts/snippets/HTML.md`
- **Purpose:** Provides consistent HTML formatting instructions across all Claude Code sessions
- **Management:** Use `/claude-code-snippets:read-snippets`, `/claude-code-snippets:update-snippet`, etc. to manage snippets

## Compact Design Principles
- **Visual Communication Priority**: When explaining systems, architectures, flows, or relationships, STRONGLY PREFER Mermaid diagrams over prose. A diagram is worth 1000 words. See Mermaid templates at `~/.claude/templates/mermaid/`.
- **Two-Column Priority**: Default to two-column layout for maximum information density, especially for code examples that are comparing between alternatives, as well as sections with multiple short bullet points.
- **Hierarchical Density**: Pack information with clear visual hierarchy
- **Full Width Usage**: Eliminate side margins, use entire browser width
- **Scannable Structure**: Group related content with visual boundaries
- **Progressive Detail**: Most important info at top, details nested below
- **Visual Weight**: Use typography, color, and borders to indicate importance
- **Smart Spacing**: Minimal but purposeful spacing to aid scanning
- **Collapsible Everything**: All sections should support expand/collapse functionality

## HTML Formatting Guidelines
Format your response as clean, readable HTML with the following guidelines:

## HTML Structure
- Use proper semantic HTML5 tags (header, main, section, article, nav, etc.)
- Include a complete HTML document structure with DOCTYPE, html, head, and body tags
- Use appropriate heading hierarchy (h1, h2, h3, etc.)
- Wrap content in semantic containers

## Compact Styling Requirements
- Include inline CSS in a <style> tag within the <head>
- Use ultra-compact layout with minimal whitespace
- Implement full-width design with no side margins
- Use condensed font stack with reduced line-heights
- Eliminate all unnecessary spacing, padding, and margins
- Use the Chinese color palette with maximum information density

## Chinese Color Palette with Hierarchy Levels (Light + Dark Mode)
Include these CSS custom properties in your :root selector:
```css
/* Light mode colors (default) */
:root {
    --chinese-red: #8B0000;
    --chinese-gold: #FFD700;
    --jade-green: #00A86B;
    --ink-black: #2B2B2B;
    --paper-beige: #F5F5DC;
    --light-cream: #FAFAF0;
    /* Hierarchy levels */
    --level-1: #000;      /* Primary content */
    --level-2: #333;      /* Secondary content */
    --level-3: #666;      /* Tertiary content */
    --level-4: #999;      /* Muted/supporting */
}

/* Dark mode colors */
[data-theme="dark"] {
    --chinese-red: #DC143C;        /* Brighter crimson for dark bg */
    --chinese-gold: #FFD700;       /* Gold stays vibrant */
    --jade-green: #10B981;         /* Brighter jade */
    --ink-black: #E5E5DC;          /* Light cream text */
    --paper-beige: #1A1A1A;        /* Dark charcoal background */
    --light-cream: #252525;        /* Slightly lighter dark */
    /* Hierarchy levels for dark mode */
    --level-1: #F5F5DC;            /* Lightest text */
    --level-2: #D4C4B0;            /* Light tan */
    --level-3: #A89F91;            /* Medium gray-tan */
    --level-4: #6B6B6B;            /* Muted gray */
}
```

Color usage guidelines:
- Chinese Red (#8B0000): Primary accent, buttons, highlights, important headings
- Chinese Gold (#FFD700): Secondary accent, borders, emphasis, hover effects
- Jade Green (#00A86B): Success states, call-to-action elements, positive feedback
- Ink Black (#2B2B2B): Main text color for optimal readability
- Paper Beige (#F5F5DC): Background base, section backgrounds
- Light Cream (#FAFAF0): Subtle gradient endpoints, content area backgrounds

## Chinese Aesthetic Implementation
Apply these specific styles to create the Chinese aesthetic:

### Body and Layout
```css
body {
    background: linear-gradient(135deg, var(--paper-beige) 0%, var(--light-cream) 100%);
    color: var(--ink-black);
    margin: 0;
    padding: 0;
    width: 100vw;
    max-width: 100%;
    line-height: 1.2;
    font-size: 14px;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

.container {
    width: 100%;
    padding: 0;
    margin: 0;
}
```

### Hierarchical Headers
```css
/* Primary heading - most important */
h1 { 
    font-size: 24px;
    font-weight: 900;
    margin: 4px 0;
    padding: 6px 4px;
    background: linear-gradient(135deg, var(--chinese-red), #CD5C5C);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}

/* Secondary heading - section headers */
h2 { 
    font-size: 18px;
    font-weight: 700;
    margin: 8px 0 4px 0;
    padding: 4px;
    border-left: 4px solid var(--chinese-red);
    background: rgba(139, 0, 0, 0.03);
    color: var(--level-1);
}

/* Tertiary heading - subsections */
h3 { 
    font-size: 14px;
    font-weight: 600;
    margin: 4px 0 2px 8px;
    color: var(--level-2);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Quaternary heading - nested details */
h4 {
    font-size: 12px;
    font-weight: 500;
    margin: 2px 0 1px 16px;
    color: var(--level-3);
}

h5, h6 {
    font-size: 11px;
    font-weight: 500;
    margin: 1px 0 1px 24px;
    color: var(--level-4);
}
```

### Interactive Elements & Collapsibles
```css
button, .button {
    background: linear-gradient(135deg, var(--chinese-red), #CD5C5C);
    color: white;
    border: 1px solid rgba(255, 215, 0, 0.3);
    transition: all 0.2s ease;
    padding: 2px 6px;
    margin: 1px;
    font-size: 12px;
    line-height: 1.1;
}

button:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(139, 0, 0, 0.3);
    border-color: var(--chinese-gold);
}

/* Dark mode toggle button */
#theme-toggle {
    position: fixed;
    top: 8px;
    right: 8px;
    z-index: 10000;
    background: var(--chinese-gold);
    color: var(--ink-black);
    border: 2px solid var(--chinese-red);
    padding: 4px 10px;
    cursor: pointer;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 700;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
    transition: all 0.2s ease;
}

#theme-toggle:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
}

/* Collapsible Sections for Progressive Disclosure */
.collapsible {
    margin: 4px 0;
    width: 100%;
}

.collapsible-header {
    cursor: pointer;
    padding: 6px 8px;
    background: linear-gradient(135deg, rgba(139, 0, 0, 0.05), rgba(255, 215, 0, 0.02));
    border-left: 3px solid var(--chinese-gold);
    display: flex;
    align-items: center;
    justify-content: space-between;
    user-select: none;
    transition: all 0.2s ease;
}

.collapsible-header:hover {
    background: linear-gradient(135deg, rgba(139, 0, 0, 0.1), rgba(255, 215, 0, 0.05));
}

.collapsible-header .arrow {
    display: inline-block;
    transition: transform 0.3s ease;
    color: var(--chinese-red);
    font-size: 10px;
}

.collapsible.open .arrow {
    transform: rotate(90deg);
}

.collapsible-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
    padding: 0 8px;
    margin-left: 12px;
}

.collapsible.open .collapsible-content {
    max-height: 5000px;
    padding: 8px;
}

/* Column-aware collapsibles */
.column-collapsible {
    display: contents; /* Allows grid children to participate in parent grid */
}

.two-column-layout .collapsible {
    grid-column: span 1; /* Each collapsible takes one column */
}

.two-column-layout .collapsible.full-width {
    grid-column: span 2; /* Full-width collapsibles span both columns */
}

/* Priority-based collapsibles */
.collapsible.critical .collapsible-header {
    border-left: 4px solid var(--chinese-red);
    background: rgba(139, 0, 0, 0.08);
    font-weight: 700;
}

.collapsible.secondary .collapsible-header {
    border-left: 2px solid #999;
    background: rgba(0, 0, 0, 0.02);
    font-size: 13px;
}

/* Always-visible important content */
.important-always-visible {
    background: linear-gradient(135deg, rgba(255, 215, 0, 0.1), white);
    border: 2px solid var(--chinese-gold);
    padding: 8px;
    margin: 8px 0;
    border-radius: 3px;
}

.important-always-visible h2 {
    color: var(--chinese-red);
    margin-top: 0;
}
```

### Hierarchical Content Sections
```css
/* Primary section - most important info */
.primary-section {
    border: 2px solid var(--chinese-red);
    background: white;
    margin: 6px 0;
    padding: 6px;
}

/* Secondary section - main content */
.secondary-section {
    border-left: 3px solid var(--chinese-gold);
    background: rgba(255, 215, 0, 0.05);
    margin: 4px 0 4px 8px;
    padding: 4px;
}

/* Tertiary section - supporting details */
.tertiary-section {
    margin-left: 16px;
    padding-left: 8px;
    border-left: 1px dashed #ccc;
}

/* Priority cards */
.card {
    background: white;
    border: 1px solid rgba(139, 0, 0, 0.2);
    border-radius: 2px;
    padding: 6px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card.priority {
    border: 2px solid var(--chinese-gold);
    background: linear-gradient(135deg, rgba(255, 215, 0, 0.05), white);
}

/* Scannable lists with visual indicators */
.dense-list {
    list-style: none;
    padding: 0;
    margin-left: 8px;
}

.dense-list li {
    padding: 2px 0 2px 12px;
    border-left: 2px solid transparent;
    position: relative;
}

.dense-list li:before {
    content: "▸";
    position: absolute;
    left: 0;
    color: var(--chinese-red);
    font-size: 10px;
}

.dense-list li strong {
    color: var(--level-2);
    font-weight: 600;
}

/* Indentation system for hierarchy */
.indent-1 { margin-left: 12px; }
.indent-2 { margin-left: 24px; }
.indent-3 { margin-left: 36px; }

/* Visual separators */
.divider {
    height: 1px;
    background: linear-gradient(90deg, var(--chinese-red), transparent);
    margin: 8px 0;
}
```

### Code Blocks
```css
/* Inline code */
code {
    background: linear-gradient(135deg, rgba(245, 245, 220, 0.3), rgba(255, 255, 255, 0.5));
    border: 1px solid rgba(139, 0, 0, 0.1);
    padding: 2px 4px;
    margin: 0 1px;
    font-family: 'Monaco', 'Menlo', 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.1;
    border-radius: 2px;
}

/* Block code - CRITICAL: white-space preserves newlines and indentation */
pre {
    background: linear-gradient(135deg, rgba(245, 245, 220, 0.3), rgba(255, 255, 255, 0.5));
    border: 1px solid rgba(139, 0, 0, 0.1);
    padding: 6px 8px;
    margin: 4px 0;
    font-family: 'Monaco', 'Menlo', 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.4;
    white-space: pre-wrap;       /* Preserve newlines and spaces, wrap long lines */
    word-wrap: break-word;       /* Break long words if needed */
    overflow-x: auto;            /* Horizontal scroll for very long lines */
    tab-size: 4;                 /* Set tab width to 4 spaces */
    -moz-tab-size: 4;
    border-radius: 3px;
}

pre code {
    background: none;
    border: none;
    padding: 0;
    margin: 0;
    font-size: inherit;
    line-height: inherit;
    white-space: inherit;        /* Inherit pre-wrap from parent */
}

/* Dark mode code blocks */
[data-theme="dark"] code {
    background: rgba(40, 40, 40, 0.8);
    border-color: #555;
    color: #e0e0e0;
}

[data-theme="dark"] pre {
    background: rgba(30, 30, 30, 0.9);
    border-color: #555;
    color: #e0e0e0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 2px 0;
    font-size: 12px;
}

th, td {
    border: 1px solid rgba(139, 0, 0, 0.2);
    padding: 2px 4px;
    text-align: left;
    line-height: 1.1;
}

th {
    background: rgba(139, 0, 0, 0.1);
}
```

## Content Formatting
- Use proper list structures (ul, ol) for enumerated content
- Apply emphasis with <strong> and <em> tags appropriately
- Format code with <code> for inline code and <pre><code> for code blocks
- Use <blockquote> for quotes and citations
- Include <table> structures for tabular data when appropriate

## Component Selection Guide

**Quick reference for choosing the right HTML components:**

| Use Case | Component | When to Use | Example |
|----------|-----------|-------------|---------|
| Critical always-visible info | `.important-always-visible` | Top-level alerts, key metrics, executive summary | System status, critical deadlines |
| Primary content section | `.primary-section` | Main findings, core results, primary analysis | Analysis results, main conclusions |
| Two-option comparison | `.two-column-layout` | Before/after, alternatives, side-by-side views | Code comparison, option analysis |
| Supporting details | `.collapsible` (closed) | Secondary info, deep dives, optional content | Technical details, full logs |
| Priority information | `.card.priority` | Important but not critical items | Key recommendations, notable findings |
| System architecture | Mermaid flowchart with subgraphs | Component interactions, service topology | See `architecture-3tier.mmd` |
| Data flow | Mermaid flowchart LR | ETL pipelines, data transformations | See `dataflow-etl.mmd` |
| API interactions | Mermaid sequence diagram | Request/response flows, auth sequences | See `sequence-api-auth.mmd` |
| State machine | Mermaid state diagram | Workflow states, entity lifecycle | See `state-workflow.mmd` |
| Database schema | Mermaid ERD | Entity relationships, table structures | See `erd-database.mmd` |

**Decision Tree:**
- Need to show structure/flow? → **Use Mermaid diagram** (templates in `~/.claude/templates/mermaid/`)
- Comparing 2 options? → **Use `.two-column-layout`**
- Critical information? → **Use `.important-always-visible`**
- Supporting detail? → **Use `.collapsible`** (collapsed by default)
- Tabular data? → **Use `<table>`**

## Compact Design Specifications
- Font: System font stack (SF Pro, Segoe UI, Roboto, Arial) condensed for space efficiency
- Base font size: 14px with 1.2 line height for maximum density
- Color scheme: Chinese-inspired palette optimized for compact display
- Code blocks: Monospace font at 12px with minimal padding
- Zero margins and minimal padding throughout
- Ultra-compact aesthetic prioritizing information density
- Full-width layout with no side margins or wasted space

## Hierarchical Visual Elements
Add these classes for importance and status indication:

```css
/* Importance indicators */
.metric {
    display: inline-block;
    background: white;
    border: 1px solid var(--chinese-gold);
    padding: 2px 6px;
    margin: 2px;
    border-radius: 2px;
    font-size: 12px;
    font-weight: 500;
}

.metric.important {
    background: var(--chinese-gold);
    color: white;
    font-weight: 700;
}

/* Status colors */
.critical { color: var(--chinese-red); font-weight: 700; }
.success { color: var(--jade-green); font-weight: 600; }
.warning { color: var(--chinese-gold); font-weight: 600; }
.muted { color: var(--level-4); font-size: 11px; }

/* Highlighting */
.highlight { background: rgba(255, 215, 0, 0.2); padding: 1px 2px; }

/* Enhanced tables with visual hierarchy */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 4px 0;
    font-size: 12px;
}

th {
    background: var(--chinese-red);
    color: white;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 3px 6px;
}

td {
    border: 1px solid #ddd;
    padding: 3px 6px;
    text-align: left;
}

tr:nth-child(even) { background: rgba(0,0,0,0.02); }
td:first-child { font-weight: 600; color: var(--level-2); }
```

## Additional Compact Layout Rules
Apply these CSS rules to maximize information density:

```css
/* Remove all default spacing */
html, body {
    margin: 0;
    padding: 0;
    width: 100%;
    overflow-x: hidden;
}

/* Compact containers */
.main-container {
    width: 100vw;
    max-width: 100%;
    padding: 2px;
    margin: 0;
}

/* Two-column layout as default */
.two-column-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    width: 100%;
}

.two-column-layout.uneven {
    grid-template-columns: 2fr 1fr;
}

.two-column-layout.reverse-uneven {
    grid-template-columns: 1fr 2fr;
}

/* Multi-column layouts for dense information */
.dense-columns {
    column-count: 2;
    column-gap: 8px;
    column-fill: balance;
}

@media (max-width: 1200px) {
    .dense-columns { column-count: 2; }
}

@media (max-width: 800px) {
    .dense-columns { column-count: 1; }
    .two-column-layout,
    .two-column-layout.uneven,
    .two-column-layout.reverse-uneven {
        grid-template-columns: 1fr;
    }
}

/* Compact grids */
.compact-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 4px;
    width: 100%;
}

/* Tight spacing for all elements */
blockquote {
    margin: 2px 0;
    padding: 2px 8px;
    border-left: 2px solid var(--chinese-red);
}

hr {
    margin: 2px 0;
    border: none;
    height: 1px;
    background: var(--chinese-red);
}
```

## Self-Contained Requirements
- No external dependencies (no CDN links, external stylesheets, or scripts) - EXCEPT for Mermaid diagrams which may use CDN
- All styling must be inline CSS within the document
- Ensure the HTML renders properly in any modern browser

## Mermaid Diagram Integration

### When to Use Mermaid Diagrams (STRONGLY ENCOURAGED)

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

### Diagram Templates

**Ready-to-use templates available at `~/.claude/templates/mermaid/`:**

| Template | Use Case |
|----------|----------|
| `architecture-3tier.mmd` | Classic web app architecture |
| `architecture-microservices.mmd` | Microservices with gateway |
| `dataflow-etl.mmd` | ETL pipeline with validation |
| `dataflow-pipeline.mmd` | Linear data processing |
| `sequence-api-auth.mmd` | Authentication flows |
| `sequence-api-crud.mmd` | Standard CRUD operations |
| `state-workflow.mmd` | Document/entity workflows |
| `erd-database.mmd` | Database schema design |
| `flowchart-decision.mmd` | Decision trees/algorithms |

**Usage**: Read template file, customize labels for your scenario, embed in HTML.

### Mermaid Setup (with Dark Mode Support)
Include Mermaid.js from CDN (exception to no-CDN rule):

```html
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Detect initial theme for Mermaid
    const currentTheme = localStorage.getItem('theme') || 'light';

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
            noteBorderColor: '#888',
            fontSize: '14px',
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif'
        } : {
            // Light theme variables (warm beige aesthetic)
            background: '#F5F0E8',
            primaryColor: '#7A1712',
            primaryTextColor: '#1a1a1a',
            primaryBorderColor: '#6B4423',
            lineColor: '#4A5568',
            secondaryColor: '#1B3A57',
            tertiaryColor: '#2D5016',
            mainBkg: '#EDE8DC',
            textColor: '#1a1a1a',
            nodeBorder: '#6B4423',
            // Sequence diagram
            actorBkg: '#D4C4B0',
            actorBorder: '#6B4423',
            actorTextColor: '#1a1a1a',
            actorLineColor: '#6B4423',
            signalColor: '#1a1a1a',
            signalTextColor: '#1a1a1a',
            labelBoxBkgColor: '#7A1712',
            labelBoxBorderColor: '#6B4423',
            labelTextColor: '#fff',
            loopTextColor: '#1a1a1a',
            noteBkgColor: '#FEF3C7',
            noteTextColor: '#6B4423',
            noteBorderColor: '#D97706',
            activationBorderColor: '#6B4423',
            activationBkgColor: '#D4C4B0',
            // State diagram
            labelColor: '#1a1a1a',
            // Class diagram
            classText: '#1a1a1a',
            fontSize: '14px',
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif'
        },
        flowchart: {
            curve: 'basis',
            padding: 20,
            useMaxWidth: true,
            htmlLabels: true
        },
        sequence: {
            actorMargin: 50,
            diagramMarginX: 8,
            diagramMarginY: 8,
            useMaxWidth: true
        }
    });
});
</script>
```

**Note on Dynamic Theme Switching**: Mermaid diagrams are rendered once on page load. The code above detects the initial theme from localStorage. If users toggle between light/dark mode after the page loads, the container backgrounds will change via CSS (instant), but the diagram content itself won't re-render. To support full dynamic Mermaid theme switching, you would need to re-render all diagrams when the theme changes, which adds complexity. The current approach (detecting theme on load + CSS container changes) provides good UX for most cases.

### Mermaid Container Styling
```css
.diagram-container {
    background: white;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    padding: 16px;
    margin: 16px 0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: background 0.3s ease, border-color 0.3s ease;
}

/* Warm beige gradient background - perfect balance for readability */
.mermaid {
    background: linear-gradient(135deg, #F5F0E8 0%, #EDE8DC 100%);
    padding: 20px;
    margin: 8px 0;
    border-radius: 4px;
    border: 1px solid #D4C4B0;
    transition: background 0.3s ease, border-color 0.3s ease;
}

/* Dark mode overrides for Mermaid diagrams */
[data-theme="dark"] .diagram-container {
    background: #2a2a2a;
    border-color: #444;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
}

[data-theme="dark"] .mermaid {
    background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
    border-color: #444;
}
```

### Mermaid Usage Examples

**Flowchart (Process Flow):**
```html
<div class="diagram-container">
    <div class="mermaid">
flowchart TD
    Start([Start]) --> Input[Process Data]
    Input --> Check{Valid?}
    Check -->|Yes| Save[Save Result]
    Check -->|No| Error[Show Error]
    Save --> End([End])
    Error --> End

    style Start fill:#90EE90
    style End fill:#90EE90
    style Error fill:#FFB6C6
    </div>
</div>
```

**Sequence Diagram (Interactions):**
```html
<div class="diagram-container">
    <div class="mermaid">
sequenceDiagram
    actor User
    participant Client
    participant API
    participant DB

    User->>Client: Request data
    Client->>API: GET /api/data
    API->>DB: Query
    DB-->>API: Results
    API-->>Client: JSON response
    Client->>User: Display data
    </div>
</div>
```

**Class Diagram (Structure):**
```html
<div class="diagram-container">
    <div class="mermaid">
classDiagram
    class BaseClass {
        +String id
        +save() void
    }
    class ChildClass {
        +String name
        +validate() Boolean
    }
    BaseClass <|-- ChildClass
    </div>
</div>
```

**State Diagram (State Machine):**
```html
<div class="diagram-container">
    <div class="mermaid">
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : start()
    Processing --> Success : complete()
    Processing --> Error : fail()
    Success --> [*]
    Error --> Idle : retry()
    </div>
</div>
```

### Mermaid Best Practices
1. **Keep it Simple**: Max 10-15 nodes per diagram
2. **Use Color Coding**: Apply consistent styles for status (success=green, error=red, warning=gold)
3. **Label Clearly**: Short, descriptive text (3-5 words max per node)
4. **Group Logically**: Use subgraphs for related components
5. **Add Context**: Use notes for important constraints or timing
6. **Match Theme**: Use Chinese color palette in custom styles
7. **Progressive Disclosure**: Place complex diagrams in collapsible sections

### Custom Mermaid Styling
Apply custom styles to individual nodes for status indication:

```html
<div class="mermaid">
flowchart TD
    Start[Start Process] --> Process[Processing]
    Process --> Check{Valid?}
    Check -->|Yes| Success[Success]
    Check -->|No| Error[Error]

    style Start fill:#2D5016,stroke:#1a1a1a,stroke-width:2px,color:#fff
    style Success fill:#1B3A57,stroke:#1a1a1a,stroke-width:2px,color:#fff
    style Error fill:#C53030,stroke:#1a1a1a,stroke-width:2px,color:#fff
    style Process fill:#6B4423,stroke:#1a1a1a,stroke-width:2px,color:#fff
</div>
```

**Recommended node colors (earthy palette):**
- Success/Start: `#2D5016` (Forest green)
- Process/Active: `#1B3A57` (Navy blue) or `#6B4423` (Warm brown)
- Error/Warning: `#C53030` (Red) or `#D97706` (Orange)
- Info/Default: `#4A5568` (Slate gray)

## Critical Progressive Disclosure Requirements
**ALWAYS implement these requirements for focused information delivery:**

1. **Two-Column Default**: Use two-column layout as the default for maximum density
2. **Important First**: Critical information always visible at the top
3. **Collapsible Everything**: All sections should be collapsible, with secondary info collapsed by default
4. **Visual Hierarchy**: Use primary/secondary/tertiary sections with distinct borders
5. **Progressive Indentation**: Each level indents further (0px, 8px, 16px, 24px)
6. **Typography Weight**: Heavier fonts for important, lighter for details
7. **Color Coding**: Red=critical, Gold=important, Green=good, Gray=muted
8. **Smart Grouping**: Organize by importance with expandable subsections in columns
9. **Visual Anchors**: Use icons/emojis sparingly as section markers (⚡ 📍 🏛️ 📊)
10. **Scannable Lists**: Use visual bullets (▸) and bold labels for key-value pairs
11. **Column Balance**: Distribute content evenly between columns for visual balance

## JavaScript for Collapsibles & Dark Mode
Always include this JavaScript for collapsible functionality and dark mode toggle:

```javascript
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Dark mode: Load saved theme and setup toggle
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.textContent = savedTheme === 'dark' ? '☀️ Light' : '🌙 Dark';
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            this.textContent = newTheme === 'dark' ? '☀️ Light' : '🌙 Dark';
        });
    }

    // Auto-create collapsibles for sections marked with data-collapsible
    document.querySelectorAll('[data-collapsible]').forEach(function(section) {
        const isOpen = section.getAttribute('data-collapsible') === 'open';
        section.classList.add('collapsible');
        if (isOpen) section.classList.add('open');
    });

    // Handle collapsible clicks
    document.querySelectorAll('.collapsible-header').forEach(function(header) {
        header.addEventListener('click', function() {
            const collapsible = this.closest('.collapsible');
            collapsible.classList.toggle('open');
        });
    });

    // Expand/Collapse all buttons
    const expandAllBtn = document.getElementById('expand-all');
    const collapseAllBtn = document.getElementById('collapse-all');

    if (expandAllBtn) {
        expandAllBtn.addEventListener('click', function() {
            document.querySelectorAll('.collapsible').forEach(function(c) {
                c.classList.add('open');
            });
        });
    }

    if (collapseAllBtn) {
        collapseAllBtn.addEventListener('click', function() {
            document.querySelectorAll('.collapsible').forEach(function(c) {
                c.classList.remove('open');
            });
        });
    }
});
</script>
```

## HTML Structure Guidelines for Progressive Disclosure

### Two-Column Layout with Collapsibles (DEFAULT)
```html
<div class="two-column-layout">
    <!-- Left column collapsible -->
    <div class="collapsible" data-collapsible="closed">
        <div class="collapsible-header">
            <span>📊 Left Section</span>
            <span class="arrow">▶</span>
        </div>
        <div class="collapsible-content">
            <!-- Content for left column -->
        </div>
    </div>

    <!-- Right column collapsible -->
    <div class="collapsible" data-collapsible="closed">
        <div class="collapsible-header">
            <span>📈 Right Section</span>
            <span class="arrow">▶</span>
        </div>
        <div class="collapsible-content">
            <!-- Content for right column -->
        </div>
    </div>

    <!-- Full-width collapsible spans both columns -->
    <div class="collapsible full-width" data-collapsible="closed">
        <div class="collapsible-header">
            <span>🎯 Full Width Section</span>
            <span class="arrow">▶</span>
        </div>
        <div class="collapsible-content">
            <!-- Content spanning both columns -->
        </div>
    </div>
</div>
```

### Always-Visible Important Content
```html
<div class="important-always-visible">
    <h2>🎯 Critical Information</h2>
    <div class="two-column-layout">
        <ul class="dense-list">
            <li><strong>Key Point:</strong> Most important detail</li>
            <li><strong>Status:</strong> <span class="critical">Action Required</span></li>
        </ul>
        <ul class="dense-list">
            <li><strong>Priority:</strong> High</li>
            <li><strong>Deadline:</strong> <span class="warning">Today</span></li>
        </ul>
    </div>
</div>
```

### Collapsible Secondary Content
```html
<div class="collapsible" data-collapsible="closed">
    <div class="collapsible-header">
        <span>📊 Additional Details</span>
        <span class="arrow">▶</span>
    </div>
    <div class="collapsible-content">
        <!-- Secondary information here -->
    </div>
</div>
```

### Control Buttons
```html
<!-- Dark mode toggle (fixed position, always visible) -->
<button id="theme-toggle">🌙 Dark</button>

<!-- Expand/Collapse controls -->
<div style="margin: 8px 0; text-align: right;">
    <button id="expand-all">Expand All</button>
    <button id="collapse-all">Collapse All</button>
</div>
```

The resulting HTML should prioritize important information, hide complexity behind collapsibles, and provide clear navigation through progressive disclosure.
</html_output>
