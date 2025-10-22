# Composable Component System

**Philosophy**: Separate structure, style, and behavior into independent layers that can be mixed and matched.

---

## The Three-Layer Model

```
LAYER 1: STRUCTURE (HTML with data attributes)
├── What it is
├── How it works
└── No styling classes

LAYER 2: STYLE (CSS that targets data attributes)
├── chinese-palette.css
├── minimal.css
├── dark-mode.css
└── Can swap freely

LAYER 3: BEHAVIOR (Optional JavaScript)
├── Enhances structure
├── No style dependencies
└── Progressive enhancement
```

---

## Layer 1: Structural Components

### Principle: Semantic HTML + Data Attributes Only

**No class names for styling, only data attributes for structure.**

### Example: Collapsible Component

```html
<!-- components/structural/collapsible.html -->
<section data-component="collapsible" data-state="closed">
    <header data-role="trigger">
        <h3 data-role="title">{{TITLE}}</h3>
        <span data-role="icon" aria-hidden="true">▼</span>
    </header>
    <div data-role="content">
        {{CONTENT}}
    </div>
</section>
```

**Key points**:
- `data-component`: Identifies what it is
- `data-role`: Identifies structural parts
- `data-state`: Tracks component state
- No `.classes` for styling
- Semantic HTML (`<section>`, `<header>`, `<h3>`)

### Example: Tab Component

```html
<!-- components/structural/tabs.html -->
<div data-component="tabs">
    <nav data-role="tab-list">
        <button data-role="tab" data-tab-id="tab1" data-active="true">
            {{TAB_1_TITLE}}
        </button>
        <button data-role="tab" data-tab-id="tab2">
            {{TAB_2_TITLE}}
        </button>
    </nav>

    <div data-role="panels">
        <div data-role="panel" data-panel-id="tab1" data-active="true">
            {{TAB_1_CONTENT}}
        </div>
        <div data-role="panel" data-panel-id="tab2">
            {{TAB_2_CONTENT}}
        </div>
    </div>
</div>
```

### Example: Mermaid Diagram

```html
<!-- components/structural/mermaid.html -->
<figure data-component="diagram" data-diagram-type="mermaid">
    <div data-role="diagram-content" class="mermaid">
        {{MERMAID_CODE}}
    </div>
    <figcaption data-role="caption">
        {{CAPTION}}
    </figcaption>
</figure>
```

---

## Layer 2: Style Systems

### Principle: Target Data Attributes, Not Classes

**CSS selects by data attributes, making it reusable across any structurally compatible component.**

### Example: Chinese Palette Style

```css
/* styles/chinese-palette.css */

/* Collapsible styling */
[data-component="collapsible"] {
    background: var(--paper-beige);
    border: 1px solid var(--border-light);
    border-radius: 8px;
    margin: 1rem 0;
}

[data-component="collapsible"][data-state="open"] {
    border-color: var(--chinese-red);
}

[data-role="trigger"] {
    padding: 1rem;
    cursor: pointer;
    background: linear-gradient(135deg, var(--chinese-red), #CD5C5C);
}

[data-role="title"] {
    font-weight: 700;
    color: var(--ink-black);
}

[data-role="content"] {
    padding: 0 1rem;
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
}

[data-component="collapsible"][data-state="open"] [data-role="content"] {
    max-height: 1000px;
    padding: 1rem;
}
```

### Example: Minimal Style

```css
/* styles/minimal.css */

/* Same structure, different look */
[data-component="collapsible"] {
    border-left: 3px solid #000;
    margin: 0.5rem 0;
}

[data-role="trigger"] {
    padding: 0.5rem;
    background: none;
}

[data-role="title"] {
    font-size: 1rem;
    font-weight: 600;
}

[data-role="content"] {
    padding-left: 1rem;
}

/* No animation in minimal style */
[data-component="collapsible"][data-state="open"] [data-role="content"] {
    display: block;
}
```

**Key insight**: Same HTML structure works with ANY style system!

---

## Layer 3: Behaviors (Optional)

### Principle: Enhance Structure with JavaScript

```javascript
// behaviors/collapsible.js

document.querySelectorAll('[data-component="collapsible"]').forEach(el => {
    const trigger = el.querySelector('[data-role="trigger"]');

    trigger.addEventListener('click', () => {
        const isOpen = el.dataset.state === 'open';
        el.dataset.state = isOpen ? 'closed' : 'open';
    });
});
```

**Key points**:
- Selects by data attributes
- Works with any styling
- Progressive enhancement (works without JS for basic content)

---

## Component Extraction Pattern

### How to Extract a Component from Existing Artifact

**Before (styled artifact)**:
```html
<div class="card shadow-lg bg-gradient p-4 rounded-xl border-red">
    <h2 class="text-2xl font-bold text-gold">My Title</h2>
    <p class="mt-2 text-gray-700">Content here</p>
</div>
```

**After (structural component)**:
```html
<section data-component="card">
    <h2 data-role="title">My Title</h2>
    <div data-role="content">
        <p>Content here</p>
    </div>
</section>
```

**Extraction process**:
1. Remove all style classes
2. Add `data-component` attribute
3. Add `data-role` to structural parts
4. Keep semantic HTML elements
5. Save as component template

---

## Component Library Structure

```
components/
├── structural/                # Style-agnostic structure
│   ├── collapsible.html
│   ├── tabs.html
│   ├── card.html
│   ├── timeline.html
│   ├── mermaid.html
│   ├── code-block.html
│   ├── navigation.html
│   └── table-of-contents.html
│
├── styles/                    # Swappable style systems
│   ├── chinese-palette.css
│   ├── minimal.css
│   ├── dark-modern.css
│   ├── academic.css
│   └── playful.css
│
├── behaviors/                 # Optional enhancements
│   ├── collapsible.js
│   ├── tabs.js
│   ├── mermaid-init.js
│   └── theme-toggle.js
│
└── templates/                 # Full page templates
    ├── documentation.html
    ├── presentation.html
    └── reference.html
```

---

## Assembly Pattern

### Option 1: Manual Assembly

```html
<!DOCTYPE html>
<html>
<head>
    <title>My Artifact</title>
    <!-- Choose your style -->
    <link rel="stylesheet" href="styles/chinese-palette.css">
    <link rel="stylesheet" href="styles/dark-mode.css">
</head>
<body>
    <!-- Insert components -->
    <section data-component="collapsible">
        <header data-role="trigger">
            <h3 data-role="title">Introduction</h3>
        </header>
        <div data-role="content">
            <p>Content goes here</p>
        </div>
    </section>

    <!-- Behaviors if needed -->
    <script src="behaviors/collapsible.js"></script>
</body>
</html>
```

### Option 2: Programmatic Assembly (Python)

```python
class ComponentAssembler:
    def __init__(self, style_system="chinese-palette"):
        self.components_dir = Path("components/structural")
        self.styles_dir = Path("components/styles")
        self.behaviors_dir = Path("components/behaviors")
        self.style_system = style_system

    def load_component(self, name):
        """Load structural component"""
        path = self.components_dir / f"{name}.html"
        return path.read_text()

    def render_component(self, name, data):
        """Render component with data"""
        template = self.load_component(name)

        # Replace placeholders
        for key, value in data.items():
            template = template.replace(f"{{{{{key}}}}}", value)

        return template

    def assemble_artifact(self, components, title):
        """Assemble full artifact from components"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <link rel="stylesheet" href="styles/{self.style_system}.css">
</head>
<body>
"""

        for component in components:
            html += self.render_component(
                component['type'],
                component['data']
            )

        html += """
</body>
</html>"""

        return html

# Usage
assembler = ComponentAssembler(style_system="chinese-palette")

artifact = assembler.assemble_artifact([
    {
        'type': 'collapsible',
        'data': {
            'TITLE': 'Introduction',
            'CONTENT': '<p>Welcome to the guide</p>'
        }
    },
    {
        'type': 'mermaid',
        'data': {
            'MERMAID_CODE': 'graph TD\n  A --> B',
            'CAPTION': 'System flow'
        }
    }
], title="My Documentation")
```

### Option 3: YAML Definition

```yaml
# artifact-definition.yml
title: My Documentation
style: chinese-palette
behaviors:
  - collapsible
  - mermaid-init

components:
  - type: collapsible
    title: Introduction
    content: |
      Welcome to this documentation.
      This is a comprehensive guide.

  - type: mermaid
    diagram: |
      graph TD
        A[Start] --> B[Process]
        B --> C[End]
    caption: Workflow diagram

  - type: tabs
    tabs:
      - title: Overview
        content: This is the overview
      - title: Details
        content: Here are the details
```

Then:
```python
# Convert YAML to artifact
def yaml_to_artifact(yaml_file, output_file):
    with open(yaml_file) as f:
        config = yaml.safe_load(f)

    assembler = ComponentAssembler(style_system=config['style'])
    html = assembler.assemble_artifact(config['components'], config['title'])

    with open(output_file, 'w') as f:
        f.write(html)
```

---

## Component Storage Format

### Recommended: JSON for Pure Data

```json
{
    "component": "collapsible",
    "data": {
        "title": "Introduction",
        "state": "open",
        "content": "<p>This is the introduction</p>"
    }
}
```

**Benefits**:
- Language-agnostic
- Easy to parse
- Can be version controlled
- No styling information

### Alternative: Markdown with Frontmatter

```markdown
---
component: collapsible
state: open
---

# Introduction

This is the introduction with **markdown** support.
```

**Benefits**:
- Human-readable
- Easy to edit
- Natural for content
- Supports rich text

---

## Key Principles

1. **Structure ≠ Style**: Never mix structural HTML with style classes
2. **Data Attributes for Selection**: Use `data-*` for CSS/JS targeting
3. **Semantic HTML**: Use proper elements (`<section>`, `<article>`, `<nav>`)
4. **Placeholders**: Use `{{NAME}}` for data injection points
5. **State in Attributes**: `data-state`, `data-active` for component states

---

## Migration Strategy

### Phase 1: Extract Components
Extract common patterns from existing artifacts into structural components.

### Phase 2: Create Style Systems
Define 2-3 style systems that target structural components.

### Phase 3: Build Assembler
Create Python tool to combine components with styles.

### Phase 4: Library
Build library of reusable components.

---

## Example: Complete Workflow

```bash
# 1. Extract component from existing artifact
python3 scripts/extract_component.py \
    ~/Desktop/Artifacts/my-doc.html \
    --selector ".collapsible-section" \
    --output components/structural/custom-collapsible.html

# 2. Define artifact in YAML
cat > my-artifact.yml << EOF
title: My New Doc
style: chinese-palette
components:
  - type: custom-collapsible
    title: Section 1
    content: Content here
EOF

# 3. Assemble artifact
python3 scripts/assemble_artifact.py \
    my-artifact.yml \
    --output ~/Desktop/Artifacts/my-new-doc.html

# 4. Switch styles
python3 scripts/assemble_artifact.py \
    my-artifact.yml \
    --style minimal \
    --output ~/Desktop/Artifacts/my-new-doc-minimal.html
```

**Same content, different look, no code changes!**

---

**Created**: 2025-10-21
**Philosophy**: Information is style-agnostic. Structure enables composition. Behavior enhances progressively.
