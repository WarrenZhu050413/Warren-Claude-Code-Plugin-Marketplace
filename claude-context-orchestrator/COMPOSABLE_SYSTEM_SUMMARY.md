# ✅ Composable Component System - READY TO USE

## What You Now Have

A **complete composable artifact system** where components are stored as pure information, completely separate from styling.

---

## 🎯 The Core Innovation

### Information-Only Storage

**Before** (coupled):
```html
<div class="bg-red-500 p-4 rounded-lg shadow-xl">Content</div>
```
- Style classes embedded
- Can't reuse without CSS baggage
- Hard to extract

**After** (composable):
```html
<section data-component="card">
    <div data-role="content">Content</div>
</section>
```
- Zero style information
- Pure structure
- Works with ANY style system

---

## 📦 Component Library

### Structural Components (4)
1. **collapsible.html** - Expandable sections
2. **card.html** - Content cards
3. **tabs.html** - Tabbed interfaces
4. **mermaid.html** - Diagrams

### Style Systems (1)
1. **minimal.css** - Clean and simple

### Behaviors (1)
1. **collapsible.js** - Interactive collapsibles

---

## 🚀 Three Ways to Use

### Method 1: JSON Definition (Recommended)

```json
{
  "title": "My Artifact",
  "style": "minimal",
  "behaviors": ["collapsible"],
  "components": [
    {
      "type": "collapsible",
      "data": {
        "STATE": "open",
        "TITLE": "My Section",
        "CONTENT": "<p>My content</p>"
      }
    }
  ]
}
```

Build:
```bash
python3 scripts/component_assembler.py build my-artifact.json \
    -o ~/Desktop/Artifacts/my-artifact.html
```

### Method 2: Programmatic (Python API)

```python
from scripts.component_assembler import ComponentAssembler

assembler = ComponentAssembler(style_system="minimal")

html = assembler.assemble_artifact(
    components=[
        {
            'type': 'card',
            'data': {
                'TITLE': 'Welcome',
                'CONTENT': '<p>Hello world</p>',
                'FOOTER': 'Created today'
            }
        }
    ],
    title="My Artifact",
    behaviors=['collapsible']
)

# Save
from pathlib import Path
Path("~/Desktop/Artifacts/output.html").expanduser().write_text(html)
```

### Method 3: CLI Creation

```bash
python3 scripts/component_assembler.py create \
    --title "My Artifact" \
    --components '[{"type":"card","data":{"TITLE":"Hi","CONTENT":"Content"}}]' \
    -o ~/Desktop/Artifacts/my-artifact.html \
    -s minimal
```

---

## 💡 Live Demo

I just created `~/Desktop/Artifacts/composable-demo.html` (now open in your browser).

It demonstrates:
- ✅ Components assembled from pure data (JSON)
- ✅ Minimal style system applied
- ✅ Interactive behavior (collapsibles)
- ✅ Zero style classes in components
- ✅ Fully composable and reusable

---

## 🔧 How It Works

```
JSON Definition
    ↓
Component Assembler
    ├─ Loads structural templates (collapsible.html, card.html, etc.)
    ├─ Replaces {{PLACEHOLDERS}} with your data
    ├─ Injects chosen style system (minimal.css)
    ├─ Adds behaviors (collapsible.js)
    └─ Outputs complete HTML artifact

Result: Single HTML file, ready to use
```

---

## 🎨 Style Systems Are Swappable

**Same JSON, different styles**:

```bash
# Minimal style
python3 scripts/component_assembler.py build my-artifact.json \
    -o output-minimal.html -s minimal

# Chinese palette style (when you create it)
python3 scripts/component_assembler.py build my-artifact.json \
    -o output-chinese.html -s chinese-palette

# Dark modern style (when you create it)
python3 scripts/component_assembler.py build my-artifact.json \
    -o output-dark.html -s dark-modern
```

**Same components, completely different looks, zero code changes!**

---

## 📖 Complete Documentation

1. **COMPOSABLE_COMPONENTS.md** - Full system architecture and patterns
2. **example-artifact-definition.json** - Working example
3. **scripts/component_assembler.py** - The assembler tool

---

## 🏗️ Component Structure

### Anatomy of a Component

```html
<!-- components/structural/collapsible.html -->
<section data-component="collapsible" data-state="{{STATE}}">
    <header data-role="trigger">
        <h3 data-role="title">{{TITLE}}</h3>
        <span data-role="icon">▼</span>
    </header>
    <div data-role="content">
        {{CONTENT}}
    </div>
</section>
```

**Key features**:
- `data-component`: What it is
- `data-role`: Structural parts
- `data-state`: Component state
- `{{PLACEHOLDERS}}`: Data injection points
- **Zero style classes**

### Styling via Data Attributes

```css
/* styles/minimal.css */
[data-component="collapsible"] {
    border-left: 3px solid var(--accent);
}

[data-role="trigger"] {
    cursor: pointer;
}

[data-component="collapsible"][data-state="open"] [data-role="content"] {
    display: block;
}
```

**Targets data attributes, not classes!**

---

## 🎯 Use Cases

### 1. Create New Artifacts from Scratch

```json
{
  "title": "API Documentation",
  "style": "minimal",
  "components": [
    {"type": "card", "data": {"TITLE": "Overview", "CONTENT": "..."}},
    {"type": "collapsible", "data": {"TITLE": "Endpoints", "CONTENT": "..."}}
  ]
}
```

### 2. Extract Components from Existing Work

```bash
# Future feature: Extract component from HTML
python3 scripts/component_assembler.py extract \
    ~/Desktop/Artifacts/my-doc.html \
    --selector ".my-custom-section" \
    --output components/structural/custom-section.html
```

### 3. Reuse Components Across Projects

```json
{
  "title": "Project A",
  "components": [{"type": "collapsible", "data": {...}}]
}
```

```json
{
  "title": "Project B",
  "components": [{"type": "collapsible", "data": {...}}]
}
```

**Same component, different content!**

---

## 🚦 Next Steps

### 1. Create More Style Systems

```css
/* components/styles/chinese-palette.css */
[data-component="collapsible"] {
    background: var(--paper-beige);
    border: 2px solid var(--chinese-red);
}

[data-role="title"] {
    background: linear-gradient(var(--chinese-red), #CD5C5C);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
```

Then use:
```bash
python3 scripts/component_assembler.py build artifact.json \
    -o output.html -s chinese-palette
```

### 2. Create More Components

```html
<!-- components/structural/timeline.html -->
<div data-component="timeline">
    <div data-role="item" data-year="{{YEAR}}">
        <h4 data-role="title">{{TITLE}}</h4>
        <p data-role="description">{{DESCRIPTION}}</p>
    </div>
</div>
```

### 3. Extract from Existing Artifacts

When you create a great pattern, extract it as a reusable component.

---

## 🧠 Key Principles

1. **Information ≠ Presentation**
   - Store structure and content only
   - Apply style separately

2. **Data Attributes > Classes**
   - `data-component`, `data-role` for selection
   - No style classes in components

3. **Placeholders for Data**
   - `{{NAME}}` convention
   - Replaced during assembly

4. **Progressive Enhancement**
   - HTML works without CSS
   - CSS works without JS
   - JS enhances experience

---

## 📊 Comparison

| Aspect | Old Way | New Way |
|--------|---------|---------|
| **Storage** | HTML with style classes | JSON data |
| **Reusability** | Copy-paste entire sections | Reference component type |
| **Styling** | Embedded in HTML | Separate CSS file |
| **Changes** | Edit every instance | Change once, applies everywhere |
| **Composition** | Manual assembly | Programmatic assembly |
| **Extraction** | Difficult | Simple (pure data) |

---

## 🎉 What This Enables

1. **Component Library**: Build once, use everywhere
2. **Style Variants**: Same content, multiple designs
3. **Easy Extraction**: Save good patterns for reuse
4. **Programmatic Creation**: Claude can assemble artifacts from data
5. **Version Control**: Store components as data (JSON/YAML)

---

## 💬 Example Workflow

**You**: "Create a documentation page with these sections: Introduction, API Reference, Examples"

**Claude**:
```python
assembler = ComponentAssembler(style_system="minimal")

html = assembler.assemble_artifact(
    components=[
        {
            'type': 'card',
            'data': {
                'TITLE': 'Introduction',
                'CONTENT': '<p>Welcome to the API docs</p>'
            }
        },
        {
            'type': 'collapsible',
            'data': {
                'STATE': 'open',
                'TITLE': 'API Reference',
                'CONTENT': '<ul><li>GET /api/users</li></ul>'
            }
        },
        {
            'type': 'collapsible',
            'data': {
                'STATE': 'closed',
                'TITLE': 'Examples',
                'CONTENT': '<pre><code>curl /api/users</code></pre>'
            }
        }
    ],
    title="API Documentation",
    behaviors=['collapsible']
)

Path("~/Desktop/Artifacts/api-docs.html").expanduser().write_text(html)
```

**Result**: Artifact created, opened, ready to use!

---

**Status**: ✅ FULLY OPERATIONAL
**Created**: 2025-10-21
**Demo**: ~/Desktop/Artifacts/composable-demo.html (OPEN NOW)
