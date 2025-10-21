# Interactive Primary Source Artifacts

Create explorable visualizations of documentation, papers, books, and primary sources. Don't summarize—surface original content in digestible, interactive formats.

## Core Philosophy

**Don't summarize, surface.** The goal is to make primary sources:
- **Explorable** - Users navigate to what interests them
- **Contextualized** - Relationships and connections are visible
- **Preserved** - Original content remains intact
- **Searchable** - Easy to find specific information
- **Annotated** - Key insights are highlighted without replacing source material

## Implementation Workflow

### Step 1: Analyze Source Material

Before building:
- Identify the source's natural structure (chapters, sections, timeline)
- Locate key concepts and their definitions
- Find important passages and their context
- Note relationships between ideas
- Extract citation information

### Step 2: Choose Display Patterns

Select patterns that match the source:
- **Documentation** → Collapsible index + concept map
- **Research paper** → Searchable excerpt table + concept relationships
- **Book** → Chapter index + key quotes with context
- **Timeline/Historical** → Timeline view with original sources
- **Technical spec** → Nested collapsibles with code examples

### Step 3: Build the Artifact

Use the base template: `${CLAUDE_PLUGIN_ROOT}/templates/html/base-template.html`

1. Read the template to understand structure
2. Create collapsible sections for each major division
3. Preserve original text—don't paraphrase
4. Include citations and location references
5. Add concept diagrams showing relationships
6. Implement search or quick-access tables

### Step 4: Maintain Readability

Keep the experience focused:
- Most sections **collapsed by default** (users expand what interests them)
- Use expand/collapse all buttons for full navigation
- Clear hierarchy: h2 for major sections, h3 for subsections
- Consistent citation format throughout
- Color-code source material vs. annotations

## Common Patterns

### Pattern 1: Collapsible Documentation Index

Use the collapsible system from the base template to create an explorable table of contents:

```html
<div class="primary-section">
  <h2>Documentation Index</h2>
  <div class="collapsible critical" data-collapsible="closed">
    <div class="collapsible-header">
      <span>Section 1: Core Concepts</span>
      <span class="arrow">▸</span>
    </div>
    <div class="collapsible-content">
      <ul class="dense-list">
        <li><strong>Concept 1:</strong> Original definition from source</li>
        <li><strong>Concept 2:</strong> Direct quote with citation</li>
      </ul>
    </div>
  </div>
</div>
```

### Pattern 2: Key Quotes with Context

Surface important passages with their surrounding context:

```html
<div class="card">
  <blockquote>
    "Original quote from source"
  </blockquote>
  <div class="muted" style="margin-top: 4px;">
    <strong>Source:</strong> Document/Chapter/Page
    <br><strong>Context:</strong> Brief explanation of why this passage matters
  </div>
</div>
```

### Pattern 3: Concept Map

Display relationships between key ideas:

```html
<div class="diagram-container">
  <div class="mermaid">
    graph TD
      A["Concept from Source"] --> B["Related Concept"]
      B --> C["Manifestation"]
  </div>
</div>
```

### Pattern 4: Timeline View

For historical documents or chronological content:

```html
<div class="collapsible full-width" data-collapsible="closed">
  <div class="collapsible-header">
    <span>Timeline: 1990-2000</span>
    <span class="arrow">▸</span>
  </div>
  <div class="collapsible-content">
    <div class="tertiary-section">
      <strong>1995:</strong> Event from source
    </div>
    <div class="tertiary-section">
      <strong>1998:</strong> Another event with original text
    </div>
  </div>
</div>
```

### Pattern 5: Searchable Excerpt Index

Create a table for quick scanning:

```html
<table>
  <thead>
    <tr>
      <th>Section</th>
      <th>Key Excerpt</th>
      <th>Location</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Chapter 2</td>
      <td>"Direct quote from source"</td>
      <td>Page 45</td>
    </tr>
  </tbody>
</table>
```

## Complete Examples

### Example 1: Technical Documentation

**Source Type**: API documentation or technical specification
**Goal**: Make API endpoints and parameters easily discoverable

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>REST API Reference</title>
    <!-- Link to base template CSS -->
</head>
<body>
    <button id="theme-toggle">🌙 Dark</button>
    <div class="container">
        <h1>REST API Reference</h1>
        <p class="muted">Complete documentation preserved in interactive format</p>

        <div style="margin: 8px 0;">
            <button id="expand-all">▼ Expand All</button>
            <button id="collapse-all">▲ Collapse All</button>
        </div>

        <!-- Authentication Section -->
        <div class="collapsible critical" data-collapsible="closed">
            <div class="collapsible-header">
                <span>Authentication</span>
                <span class="arrow">▸</span>
            </div>
            <div class="collapsible-content">
                <blockquote>
                    All API requests must include an Authorization header with a valid Bearer token.
                </blockquote>
                <pre><code>Authorization: Bearer YOUR_API_KEY</code></pre>
            </div>
        </div>

        <!-- Endpoints by Category -->
        <div class="collapsible critical" data-collapsible="closed">
            <div class="collapsible-header">
                <span>Users Endpoints</span>
                <span class="arrow">▸</span>
            </div>
            <div class="collapsible-content">
                <div class="tertiary-section">
                    <strong>GET /users/{id}</strong>
                    <p class="muted">Retrieve user by ID</p>
                    <strong>Parameters:</strong>
                    <ul class="dense-list">
                        <li><code>id</code> (path) - User ID</li>
                        <li><code>include</code> (query) - Fields to include in response</li>
                    </ul>
                    <strong>Response:</strong>
                    <pre><code>{
  "id": "123",
  "name": "John Doe",
  "email": "john@example.com"
}</code></pre>
                </div>
            </div>
        </div>
    </div>

    <!-- Include base template's script for collapsibles -->
</body>
</html>
```

### Example 2: Academic Paper

**Source Type**: Research paper
**Goal**: Surface arguments, methodology, and findings without summarizing

```html
<div class="primary-section">
    <h1>Paper: "Mechanisms of Learning in Neural Networks"</h1>
    <p class="muted">
        Authors: Smith, J., Johnson, K. (2023) |
        Published: Nature Machine Intelligence
    </p>

    <!-- Abstract -->
    <div class="collapsible critical" data-collapsible="open">
        <div class="collapsible-header">
            <span><strong>Abstract</strong></span>
            <span class="arrow">▸</span>
        </div>
        <div class="collapsible-content">
            <blockquote>
                Neural networks learn through gradient descent optimization. This paper
                investigates the mechanisms by which information is propagated and retained
                during training, revealing critical phase transitions in learning dynamics.
            </blockquote>
            <p class="muted"><strong>Pages:</strong> 1 | <strong>Word count:</strong> 250</p>
        </div>
    </div>

    <!-- Main Arguments -->
    <div class="collapsible critical" data-collapsible="closed">
        <div class="collapsible-header">
            <span><strong>Key Arguments</strong></span>
            <span class="arrow">▸</span>
        </div>
        <div class="collapsible-content">
            <div class="secondary-section">
                <h3>Argument 1: Learning Occurs in Phases</h3>
                <blockquote>
                    "Learning exhibits three distinct phases: random initialization,
                    rapid feature acquisition, and convergence to fixed representations."
                </blockquote>
                <p class="muted"><strong>Found in:</strong> Introduction, para 3</p>
            </div>

            <div class="secondary-section">
                <h3>Argument 2: Information Bottleneck Principle</h3>
                <blockquote>
                    "Networks minimize mutual information about input while preserving
                    task-relevant information, creating an information bottleneck."
                </blockquote>
                <p class="muted"><strong>Found in:</strong> Theoretical Framework, para 2</p>
            </div>
        </div>
    </div>

    <!-- Methodology -->
    <div class="collapsible" data-collapsible="closed">
        <div class="collapsible-header">
            <span><strong>Methodology</strong></span>
            <span class="arrow">▸</span>
        </div>
        <div class="collapsible-content">
            <blockquote>
                We conducted experiments on image classification tasks (CIFAR-10, ImageNet)
                using fully-connected networks of varying depth (1-10 layers) and width
                (100-1000 units). Each configuration was trained 100 times with different
                random seeds.
            </blockquote>
            <p class="muted"><strong>Pages:</strong> 4-5</p>
        </div>
    </div>

    <!-- Results -->
    <div class="collapsible" data-collapsible="closed">
        <div class="collapsible-header">
            <span><strong>Key Results</strong></span>
            <span class="arrow">▸</span>
        </div>
        <div class="collapsible-content">
            <table>
                <thead>
                    <tr>
                        <th>Finding</th>
                        <th>Data</th>
                        <th>Page</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Phase transition at 10% training</td>
                        <td>Occurs in 95% of runs</td>
                        <td>6</td>
                    </tr>
                    <tr>
                        <td>Wider networks learn faster</td>
                        <td>Width correlates r=0.89 with speed</td>
                        <td>7</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <!-- Concept Map -->
    <div class="collapsible" data-collapsible="closed">
        <div class="collapsible-header">
            <span><strong>Concept Relationships</strong></span>
            <span class="arrow">▸</span>
        </div>
        <div class="collapsible-content">
            <div class="diagram-container">
                <div class="mermaid">
                    graph TD
                        A["Gradient Descent"] --> B["Phase Transitions"]
                        B --> C["Fast Learning Phase"]
                        B --> D["Convergence Phase"]
                        C --> E["Information Bottleneck"]
                        D --> E
                        E --> F["Generalization"]
                </div>
            </div>
        </div>
    </div>
</div>
```

### Example 3: Book Chapter

```html
<div class="primary-section">
    <h1>Chapter 5: Market Economics</h1>
    <p class="muted">From: "Principles of Modern Economics" (3rd ed.) | Pages: 112-156</p>

    <!-- Introduction -->
    <div class="collapsible critical" data-collapsible="open">
        <div class="collapsible-header">
            <span>Chapter Introduction</span>
            <span class="arrow">▸</span>
        </div>
        <div class="collapsible-content">
            <blockquote>
                Markets are mechanisms for coordinating production and consumption.
                This chapter explores how prices emerge and what determines equilibrium
                in competitive markets.
            </blockquote>
            <p class="muted"><strong>Pages:</strong> 112-115</p>
        </div>
    </div>

    <!-- Sections -->
    <div class="collapsible" data-collapsible="closed">
        <div class="collapsible-header">
            <span>5.1: Supply and Demand</span>
            <span class="arrow">▸</span>
        </div>
        <div class="collapsible-content">
            <p>
                Supply is the quantity of goods producers are willing to provide at each price.
                Demand is the quantity consumers are willing to buy at each price.
            </p>
            <p class="muted"><strong>Pages:</strong> 115-125</p>
        </div>
    </div>

    <!-- Key Definitions -->
    <div class="collapsible full-width" data-collapsible="closed">
        <div class="collapsible-header">
            <span>Key Definitions</span>
            <span class="arrow">▸</span>
        </div>
        <div class="collapsible-content">
            <table>
                <thead>
                    <tr>
                        <th>Term</th>
                        <th>Definition from Text</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Price Floor</td>
                        <td>"A legal minimum price set above equilibrium"</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</div>
```

## Design Principles

### 1. Preserve Over Simplify
Show the actual source content. Annotations should enhance, not replace.

### 2. Structure by Source Logic
Use the source's own organization (chapters, sections, argument flow) rather than imposing an artificial structure.

### 3. Make Connections Visible
Show how concepts relate without forcing interpretation. Use diagrams for structural relationships.

### 4. Enable Exploration
Collapsibles let users dive deep or skim quickly based on their interest.

### 5. Provide Context
Every excerpt should include:
- Source location (page, section, chapter)
- Why this content is highlighted
- Related passages (linked via the diagram or index)

## Anti-Patterns to Avoid

❌ **Don't summarize**: Paraphrasing defeats the purpose. Use direct quotes.

❌ **Don't over-structure**: Let the source's organization guide you, not arbitrary categories.

❌ **Don't hide citations**: Always show where information comes from.

❌ **Don't add excessive commentary**: Annotations should clarify, not interpret.

❌ **Don't expand all sections by default**: Let users explore at their own pace.

## Pattern Selection Guide

| Source Type | Best Patterns | Why |
|---|---|---|
| API Docs | Nested collapsibles, Tables | Easy endpoint browsing |
| Academic Paper | Concept map, Quote cards, Tables | Show argument structure |
| Book/Textbook | Chapter index, Definitions table | Preserve chapter logic |
| Historical | Timeline, Events with context | Chronological navigation |
| Technical Spec | Nested sections, Code blocks | Deep hierarchical structure |
| Blog/Article | Topic collapsibles, Pull quotes | Skimmable sections |
