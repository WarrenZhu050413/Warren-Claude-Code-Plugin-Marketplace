# HTML Output Examples & Reference

This document provides complete examples and patterns for using the HTML template system.

## Table of Contents
- [Component Examples](#component-examples)
- [Mermaid Diagrams](#mermaid-diagrams)
- [Layout Patterns](#layout-patterns)
- [Complete Page Examples](#complete-page-examples)

---

## Component Examples

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

### Collapsible Section (Closed by Default)

```html
<div class="collapsible" data-collapsible="closed">
    <div class="collapsible-header">
        <span>📊 Additional Details</span>
        <span class="arrow">▶</span>
    </div>
    <div class="collapsible-content">
        <p>Secondary information that can be expanded when needed.</p>
    </div>
</div>
```

### Collapsible Section (Open by Default)

```html
<div class="collapsible" data-collapsible="open">
    <div class="collapsible-header">
        <span>📈 Key Metrics</span>
        <span class="arrow">▶</span>
    </div>
    <div class="collapsible-content">
        <p>Important information that starts visible.</p>
    </div>
</div>
```

### Critical Priority Collapsible

```html
<div class="collapsible critical" data-collapsible="open">
    <div class="collapsible-header">
        <span>⚠️ Urgent Action Required</span>
        <span class="arrow">▶</span>
    </div>
    <div class="collapsible-content">
        <p>Critical information with red border styling.</p>
    </div>
</div>
```

### Code Block (Inline)

```html
<p>Use the <code>print()</code> function to output text.</p>
```

### Code Block (Multi-line)

```html
<pre><code>def hello_world():
    print("Hello, World!")
    return True</code></pre>
```

### Two-Column Layout

```html
<div class="two-column-layout">
    <div class="column">
        <h3>Option A</h3>
        <pre><code>// Before
const x = 1;</code></pre>
    </div>
    <div class="column">
        <h3>Option B</h3>
        <pre><code>// After
let x = 1;</code></pre>
    </div>
</div>
```

### Two-Column Layout (Uneven - Left Larger)

```html
<div class="two-column-layout uneven">
    <div>
        <h3>Main Content (2/3 width)</h3>
        <p>Primary content goes here.</p>
    </div>
    <div>
        <h3>Sidebar (1/3 width)</h3>
        <p>Supporting info.</p>
    </div>
</div>
```

### Dense List with Visual Indicators

```html
<ul class="dense-list">
    <li><strong>Feature:</strong> Description of feature</li>
    <li><strong>Status:</strong> <span class="success">Completed</span></li>
    <li><strong>Priority:</strong> <span class="warning">Medium</span></li>
</ul>
```

### Status Indicators

```html
<span class="critical">Critical Issue</span>
<span class="warning">Warning</span>
<span class="success">Success</span>
<span class="muted">Less important</span>
<span class="highlight">Highlighted text</span>
```

### Metrics Display

```html
<div class="metric">Users: 1,234</div>
<div class="metric important">Revenue: $5,678</div>
<div class="metric">Uptime: 99.9%</div>
```

### Table with Hierarchy

```html
<table>
    <thead>
        <tr>
            <th>Property</th>
            <th>Value</th>
            <th>Status</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Database</td>
            <td>PostgreSQL</td>
            <td><span class="success">Active</span></td>
        </tr>
        <tr>
            <td>Cache</td>
            <td>Redis</td>
            <td><span class="warning">Degraded</span></td>
        </tr>
    </tbody>
</table>
```

### Buttons

```html
<button id="expand-all">Expand All</button>
<button id="collapse-all">Collapse All</button>
```

---

## Mermaid Diagrams

### Flowchart (Process Flow)

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

### Sequence Diagram (API Interactions)

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

### Class Diagram (Structure)

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

### State Diagram (State Machine)

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

### Entity Relationship Diagram

```html
<div class="diagram-container">
    <div class="mermaid">
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ LINE_ITEM : contains
    PRODUCT ||--o{ LINE_ITEM : includes

    USER {
        string id PK
        string name
        string email
    }
    ORDER {
        string id PK
        string user_id FK
        date created_at
    }
    </div>
</div>
```

### Custom Styled Flowchart (Chinese Palette)

```html
<div class="diagram-container">
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
</div>
```

---

## Layout Patterns

### Two-Column with Collapsibles

```html
<div class="two-column-layout">
    <!-- Left column -->
    <div class="collapsible" data-collapsible="closed">
        <div class="collapsible-header">
            <span>📊 Left Section</span>
            <span class="arrow">▶</span>
        </div>
        <div class="collapsible-content">
            <p>Content for left column.</p>
        </div>
    </div>

    <!-- Right column -->
    <div class="collapsible" data-collapsible="closed">
        <div class="collapsible-header">
            <span>📈 Right Section</span>
            <span class="arrow">▶</span>
        </div>
        <div class="collapsible-content">
            <p>Content for right column.</p>
        </div>
    </div>

    <!-- Full-width section spans both columns -->
    <div class="collapsible full-width" data-collapsible="closed">
        <div class="collapsible-header">
            <span>🎯 Full Width Section</span>
            <span class="arrow">▶</span>
        </div>
        <div class="collapsible-content">
            <p>Content spanning both columns.</p>
        </div>
    </div>
</div>
```

### Hierarchical Sections

```html
<div class="primary-section">
    <h2>Primary Section</h2>
    <p>Most important information at top level.</p>

    <div class="secondary-section">
        <h3>Secondary Section</h3>
        <p>Supporting details nested within.</p>

        <div class="tertiary-section">
            <h4>Tertiary Section</h4>
            <p>Fine-grained details at deepest level.</p>
        </div>
    </div>
</div>
```

### Compact Grid Layout

```html
<div class="compact-grid">
    <div class="card">
        <h3>Card 1</h3>
        <p>Content</p>
    </div>
    <div class="card">
        <h3>Card 2</h3>
        <p>Content</p>
    </div>
    <div class="card priority">
        <h3>Priority Card</h3>
        <p>Important content</p>
    </div>
</div>
```

### Dense Columns (Newspaper Style)

```html
<div class="dense-columns">
    <p>This content will flow across multiple columns automatically, creating a newspaper-style layout. Great for long lists or related items that benefit from compact presentation.</p>

    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
        <li>Item 3</li>
        <!-- More items... -->
    </ul>
</div>
```

---

## Complete Page Examples

### Example 1: Code Review Report

```html
<div class="container">
    <h1>Code Review Report</h1>

    <!-- Critical findings always visible -->
    <div class="important-always-visible">
        <h2>🎯 Critical Findings</h2>
        <div class="two-column-layout">
            <ul class="dense-list">
                <li><strong>Security:</strong> <span class="critical">3 issues</span></li>
                <li><strong>Performance:</strong> <span class="warning">5 issues</span></li>
            </ul>
            <ul class="dense-list">
                <li><strong>Code Quality:</strong> <span class="success">Good</span></li>
                <li><strong>Test Coverage:</strong> 87%</li>
            </ul>
        </div>
    </div>

    <!-- Detailed findings in collapsibles -->
    <div class="collapsible critical" data-collapsible="open">
        <div class="collapsible-header">
            <span>🔒 Security Issues</span>
            <span class="arrow">▶</span>
        </div>
        <div class="collapsible-content">
            <table>
                <thead>
                    <tr>
                        <th>File</th>
                        <th>Issue</th>
                        <th>Severity</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>auth.js</td>
                        <td>SQL injection vulnerability</td>
                        <td><span class="critical">Critical</span></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <div class="collapsible" data-collapsible="closed">
        <div class="collapsible-header">
            <span>⚡ Performance Issues</span>
            <span class="arrow">▶</span>
        </div>
        <div class="collapsible-content">
            <p>Details about performance issues...</p>
        </div>
    </div>
</div>
```

### Example 2: System Architecture with Diagram

```html
<div class="container">
    <h1>System Architecture Overview</h1>

    <!-- Summary -->
    <div class="important-always-visible">
        <h2>📊 Architecture Summary</h2>
        <ul class="dense-list">
            <li><strong>Type:</strong> Microservices</li>
            <li><strong>Services:</strong> 7</li>
            <li><strong>Database:</strong> PostgreSQL + Redis</li>
        </ul>
    </div>

    <!-- Architecture diagram -->
    <div class="diagram-container">
        <h2>System Components</h2>
        <div class="mermaid">
flowchart TB
    subgraph Frontend
        UI[Web UI]
    end

    subgraph Backend
        API[API Gateway]
        Auth[Auth Service]
        Data[Data Service]
    end

    subgraph Storage
        DB[(PostgreSQL)]
        Cache[(Redis)]
    end

    UI --> API
    API --> Auth
    API --> Data
    Auth --> DB
    Data --> DB
    Data --> Cache

    style UI fill:#1B3A57,color:#fff
    style API fill:#7A1712,color:#fff
    style DB fill:#2D5016,color:#fff
        </div>
    </div>

    <!-- Service details in collapsibles -->
    <div class="two-column-layout">
        <div class="collapsible" data-collapsible="closed">
            <div class="collapsible-header">
                <span>🌐 Frontend Details</span>
                <span class="arrow">▶</span>
            </div>
            <div class="collapsible-content">
                <p>React-based web application...</p>
            </div>
        </div>

        <div class="collapsible" data-collapsible="closed">
            <div class="collapsible-header">
                <span>⚙️ Backend Services</span>
                <span class="arrow">▶</span>
            </div>
            <div class="collapsible-content">
                <p>Node.js microservices...</p>
            </div>
        </div>
    </div>
</div>
```

### Example 3: Before/After Comparison

```html
<div class="container">
    <h1>Code Refactoring Analysis</h1>

    <div class="important-always-visible">
        <h2>🎯 Improvements Summary</h2>
        <div class="two-column-layout">
            <div class="metric important">Lines reduced: 30%</div>
            <div class="metric important">Performance: +40%</div>
        </div>
    </div>

    <div class="two-column-layout">
        <div class="primary-section">
            <h2>❌ Before</h2>
            <pre><code>function processData(data) {
    let result = [];
    for (let i = 0; i < data.length; i++) {
        if (data[i].active) {
            result.push(data[i]);
        }
    }
    return result;
}</code></pre>
        </div>

        <div class="primary-section">
            <h2>✅ After</h2>
            <pre><code>function processData(data) {
    return data.filter(item => item.active);
}</code></pre>
        </div>
    </div>

    <div class="collapsible" data-collapsible="closed">
        <div class="collapsible-header">
            <span>📊 Detailed Analysis</span>
            <span class="arrow">▶</span>
        </div>
        <div class="collapsible-content">
            <p>The refactored code uses functional programming...</p>
        </div>
    </div>
</div>
```

---

## Mermaid Templates Reference

Ready-to-use templates available at `~/.claude/templates/mermaid/`:

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

---

## Best Practices

### When to Use Each Component

| Use Case | Component | Example |
|----------|-----------|---------|
| Critical always-visible info | `.important-always-visible` | System alerts, key metrics |
| Primary content section | `.primary-section` | Main findings, core results |
| Two-option comparison | `.two-column-layout` | Before/after, alternatives |
| Supporting details | `.collapsible` (closed) | Technical details, logs |
| Priority information | `.card.priority` | Key recommendations |
| System architecture | Mermaid flowchart | Component interactions |
| Data flow | Mermaid flowchart LR | ETL pipelines |
| API interactions | Mermaid sequence | Request/response flows |

### Multi-line Code Rules

**✅ ALWAYS wrap multiline code in `<pre><code>`:**
```html
<pre><code>def hello():
    print("Hello")</code></pre>
```

**❌ NEVER use div for code blocks:**
```html
<!-- WRONG - newlines will collapse -->
<div class="code-block">
def hello():
    print("Hello")
</div>
```

### Progressive Disclosure Guidelines

1. **Critical info first** - Always visible at top
2. **Secondary details collapsed** - Use `data-collapsible="closed"`
3. **Visual hierarchy** - Primary → Secondary → Tertiary sections
4. **Color coding** - Red=critical, Gold=important, Green=success
5. **Two-column default** - Maximize information density

---

**Last Updated:** 2025-10-12
