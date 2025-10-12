# Template Pattern for Advanced Snippets

The template pattern is a powerful way to create sophisticated snippets that need external resources like templates, examples, or complex assets.

## Table of Contents

- [Why Use the Template Pattern?](#why-use-the-template-pattern)
- [Architecture](#architecture)
- [Real-World Example: HTML Snippet](#real-world-example-html-snippet)
- [Creating Your Own Template-Based Snippet](#creating-your-own-template-based-snippet)
- [Best Practices](#best-practices)
- [Benefits](#benefits)
- [When to Use Template Pattern](#when-to-use-template-pattern)
- [Advanced: Multiple Templates](#advanced-multiple-templates)

---

## Why Use the Template Pattern?

**Problem**: Some snippets need more than just instructions - they need templates, examples, style guides, or other assets.

**Solution**: Separate concerns by putting:
- **Instructions** in the snippet file (what Claude should do)
- **Templates** in separate files (reusable assets)
- **Examples** in documentation files (reference patterns)

## Architecture

```
my-plugin/
├── snippets/
│   └── my-snippet.md          # Instructions for Claude
└── templates/
    └── my-template/
        ├── base-template.ext  # Template file(s)
        └── examples.md        # Usage documentation
```

## Real-World Example: HTML Snippet

The HTML snippet demonstrates this pattern perfectly:

```
claude-code-snippets-plugin/
├── snippets/
│   └── HTML.md                    # Instructions to Claude
└── templates/
    └── html/
        ├── base-template.html     # Complete HTML template (665 lines)
        └── examples.md            # Component examples (651 lines)
```

### Component Breakdown

#### 1. `snippets/HTML.md` (Instructions)

This file tells Claude:
- When to use HTML output
- How to read the template from `${CLAUDE_PLUGIN_ROOT}/templates/html/base-template.html`
- How to replace placeholders like `{{TITLE}}` and `<!-- CONTENT GOES HERE -->`
- Where to find examples: `${CLAUDE_PLUGIN_ROOT}/templates/html/examples.md`
- Component selection guide (which HTML components to use when)
- Design principles and best practices

#### 2. `templates/html/base-template.html` (Template)

This file contains:
- Complete HTML structure with CSS and JavaScript
- Dark mode support with localStorage persistence
- Chinese color palette (light + dark modes)
- Collapsible sections with animations
- Mermaid diagram integration
- Responsive design
- Placeholders: `{{TITLE}}` and `<!-- CONTENT GOES HERE -->`

#### 3. `templates/html/examples.md` (Reference)

This file provides:
- Complete component examples (collapsibles, tables, code blocks)
- Mermaid diagram patterns (flowcharts, sequence, ERD)
- Layout patterns (two-column, hierarchical sections)
- Before/after comparison examples
- Best practices and decision trees

### How It Works

When you type "HTML Explain something":

1. **Pattern matches** → `HTML.md` snippet is injected
2. **Claude reads** `HTML.md` instructions
3. **Claude reads** `base-template.html` for structure
4. **Claude replaces** `{{TITLE}}` with "Something Explanation"
5. **Claude adds content** in `<!-- CONTENT GOES HERE -->` section
6. **Claude references** `examples.md` for component patterns
7. **File created**: `claude_html/something_explanation.html`
8. **File opened** in browser

## Creating Your Own Template-Based Snippet

### Step 1: Create the Snippet File

```markdown
---
description: Brief description of your snippet
SNIPPET_NAME: my-snippet
ANNOUNCE_USAGE: true
---

# My Snippet Title

**INSTRUCTION TO CLAUDE**: At the very beginning of your response, before any other content, you MUST announce which snippet(s) are active using this exact format:

📎 **Active Context**: my-snippet

---

**VERIFICATION_HASH:** `unique-hash-here`

## Primary Purpose

Explain what this snippet is for and when it should be used.

## File Handling Instructions

1. **ALWAYS** create output directory: `mkdir -p output/`
2. Write to: `output/{description}.ext`
3. Open file after writing

## Template System

**Base Template:** `${CLAUDE_PLUGIN_ROOT}/templates/my-template/base-template.ext`
- Contains all structure and configuration
- Ready to use - just replace placeholders
- Includes feature X, Y, Z

**Examples & Reference:** `${CLAUDE_PLUGIN_ROOT}/templates/my-template/examples.md`
- Complete usage examples
- Common patterns
- Best practices

**Workflow:**
1. Read the base template: `${CLAUDE_PLUGIN_ROOT}/templates/my-template/base-template.ext`
2. Replace `{{PLACEHOLDER}}` with actual values
3. Add content in designated section
4. Reference examples.md for patterns if needed

## Component Selection Guide

Quick reference for choosing the right patterns:

| Use Case | Pattern | When to Use |
|----------|---------|-------------|
| Feature A | Pattern 1 | Scenario 1 |
| Feature B | Pattern 2 | Scenario 2 |

## Design Principles

### Principle 1: Title
- **Rule 1**: Description
- **Rule 2**: Description

## Best Practices

1. **Practice 1**: Explanation
2. **Practice 2**: Explanation
```

### Step 2: Create Template Directory

```bash
cd ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin
mkdir -p templates/my-template/
```

### Step 3: Create Base Template

Create `templates/my-template/base-template.ext` with:
- All boilerplate code/structure
- Clearly marked placeholders (e.g., `{{TITLE}}`, `<!-- CONTENT -->`)
- Complete styling/configuration
- Ready to use with minimal changes

**Example placeholders:**
```
{{TITLE}}                  # Simple replacement
{{AUTHOR}}                 # Metadata
<!-- CONTENT GOES HERE --> # Content insertion point
{{DATE}}                   # Dynamic content
```

### Step 4: Create Examples File

Create `templates/my-template/examples.md` with:

```markdown
# Template Name - Examples & Reference

## Table of Contents
- [Component Examples](#component-examples)
- [Common Patterns](#common-patterns)
- [Complete Examples](#complete-examples)

---

## Component Examples

### Example 1: Basic Component

\```language
# Code example here
\```

### Example 2: Advanced Component

\```language
# Code example here
\```

## Common Patterns

### Pattern 1: Use Case A

\```language
# Pattern example
\```

### Pattern 2: Use Case B

\```language
# Pattern example
\```

## Complete Examples

### Example: Full Implementation

\```language
# Complete working example
\```
```

### Step 5: Configure the Snippet

Add to `scripts/config.json` or `scripts/config.local.json`:

```json
{
  "name": "my-snippet",
  "pattern": "\\bmy-snippet\\b",
  "snippet": ["snippets/my-snippet.md"],
  "enabled": true
}
```

### Step 6: Test the Snippet

```bash
cd scripts/
python3 snippets_cli.py test my-snippet "I need my-snippet help"
```

## Best Practices

### 1. Use `${CLAUDE_PLUGIN_ROOT}` for Paths

✅ **Good:**
```markdown
**Base Template:** `${CLAUDE_PLUGIN_ROOT}/templates/html/base-template.html`
```

❌ **Bad:**
```markdown
**Base Template:** `./templates/html/base-template.html`
```

### 2. Provide Clear Workflow Steps

```markdown
**Workflow:**
1. Read the base template: `${CLAUDE_PLUGIN_ROOT}/templates/...`
2. Replace `{{PLACEHOLDER}}` with actual content
3. Add content in designated section
4. Reference examples.md for patterns
```

### 3. Include Quick Reference Tables

Component selection guides help Claude choose the right patterns quickly:

```markdown
| Use Case | Component | When to Use |
|----------|-----------|-------------|
| Critical info | `.important-always-visible` | System alerts |
| Comparison | `.two-column-layout` | Before/after |
```

### 4. Keep Snippet Focused on Instructions

- Don't embed large templates inline in the snippet file
- Reference external files instead
- Separate concerns clearly

### 5. Document Placeholder Format

List all placeholders and explain what each one does:

```markdown
## Placeholders

- `{{TITLE}}`: Document title
- `{{AUTHOR}}`: Author name
- `<!-- CONTENT GOES HERE -->`: Main content insertion point
```

### 6. Create Comprehensive Examples

- Show complete working examples
- Include common patterns
- Provide before/after comparisons
- Document edge cases

## Benefits

### 1. Separation of Concerns
- Instructions separate from templates
- Easy to update templates without changing snippets
- Clear responsibility boundaries

### 2. Reusability
- Templates can be used independently
- Examples serve as standalone documentation
- Patterns can be shared across snippets

### 3. Maintainability
- Update templates without touching snippet logic
- Version control works better (diff templates separately)
- Easier to test individual components

### 4. Discoverability
- Examples file serves as reference documentation
- New users can learn from examples
- Patterns are documented and searchable

### 5. Scalability
- Add new templates without bloating snippet files
- Multiple templates can share examples
- Easy to extend with new patterns

## When to Use Template Pattern

### Use the Template Pattern When:

- ✅ Your snippet needs external assets (HTML, CSS, config files)
- ✅ You have complex formatting requirements
- ✅ Multiple related patterns need to be documented
- ✅ Templates are large (>100 lines)
- ✅ You want examples separate from instructions
- ✅ Multiple variants of output are needed
- ✅ Asset files need to be updated independently

### Use Simple Snippets When:

- ❌ Instructions are short and self-contained
- ❌ No external assets needed
- ❌ Format is simple and doesn't need templates
- ❌ No reusable patterns to document
- ❌ Total content is <50 lines

## Advanced: Multiple Templates

For snippets that need multiple template variants:

```
templates/
└── my-template/
    ├── base-template-simple.ext    # Simple variant
    ├── base-template-advanced.ext  # Advanced variant
    ├── base-template-minimal.ext   # Minimal variant
    └── examples.md                 # Examples for all variants
```

**In snippet instructions:**

```markdown
## Template System

Choose the appropriate template:

**Simple:** `${CLAUDE_PLUGIN_ROOT}/templates/my-template/base-template-simple.ext`
- Use for basic cases
- Minimal features
- Quick setup

**Advanced:** `${CLAUDE_PLUGIN_ROOT}/templates/my-template/base-template-advanced.ext`
- Use for complex cases
- Full feature set
- Maximum customization

**Minimal:** `${CLAUDE_PLUGIN_ROOT}/templates/my-template/base-template-minimal.ext`
- Use for quick prototypes
- Bare bones only
- Fastest performance
```

## Template Pattern in Action

See the HTML snippet for a complete, production-ready implementation:
- **Snippet**: `snippets/HTML.md`
- **Template**: `templates/html/base-template.html`
- **Examples**: `templates/html/examples.md`

### Try It Yourself

```
HTML Explain the template pattern
```

Claude will:
1. Announce: `📎 **Active Context**: HTML`
2. Read the base template
3. Replace `{{TITLE}}` with "Template Pattern Explanation"
4. Add content about the template pattern
5. Reference examples.md for formatting patterns
6. Create `claude_html/template_pattern_explanation.html`
7. Open in browser

---

**Next Steps:**
- Study the HTML snippet implementation
- Create your first template-based snippet
- See [Configuration](configuration.md) for setup details
- See [Commands Reference](commands-reference.md) for snippet management
