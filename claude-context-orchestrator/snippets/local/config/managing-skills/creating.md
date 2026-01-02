# Creating Skills

Step-by-step guidance for creating new Agent Skills in Claude Code.

## Quick Start

### 1. Choose Skill Location

**Personal Skills** (`~/.claude/skills/`):
- Individual workflows
- Experimental skills
- Personal productivity tools

**Project Skills** (`.claude/skills/`):
- Team workflows
- Project-specific expertise
- Shared utilities (commit to git)

**Plugin Skills** (plugin's `skills/` directory):
- Distributable skills
- Part of a plugin package
- Automatically available when plugin installed

### 2. Create Skill Directory

```bash
# Personal
mkdir -p ~/.claude/skills/my-skill-name

# Project
mkdir -p .claude/skills/my-skill-name

# Plugin
mkdir -p path/to/plugin/skills/my-skill-name
```

### 3. Create SKILL.md

Minimum required structure:

```yaml
---
name: Your Skill Name
description: What it does and when to use it (include trigger terms)
---

# Your Skill Name

## Instructions

Provide clear, step-by-step guidance.

## Examples

Show concrete examples of using this skill.
```

## Writing Effective Descriptions

The `description` field is critical for skill discovery.

### Requirements

- **Write in third person** (goes into system prompt)
- **Include WHAT the skill does**
- **Include WHEN to use it**
- **Add specific trigger terms** users would mention
- **Maximum 1024 characters**

### Good Examples

**PDF Processing**:
```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

**Excel Analysis**:
```yaml
description: Analyze Excel spreadsheets, create pivot tables, generate charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files.
```

**Git Commit Helper**:
```yaml
description: Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages or reviewing staged changes.
```

### Bad Examples

```yaml
description: Helps with documents  # Too vague

description: Processes data  # Not specific enough

description: Does stuff with files  # No trigger terms
```

## Skill Structure Guidelines

### Keep Skills Focused

One skill = one capability

**Good** (focused):
- "PDF form filling"
- "Excel data analysis"
- "Git commit messages"

**Too broad** (split into multiple skills):
- "Document processing"
- "Data tools"
- "File operations"

### Use Progressive Disclosure

Keep SKILL.md under 500 lines. Split content into separate files.

**Pattern**:

```
my-skill/
├── SKILL.md              # Main instructions (< 500 lines)
├── reference.md          # Detailed API docs
├── examples.md           # Usage examples
└── scripts/
    └── helper.py         # Utility scripts
```

**In SKILL.md**:

```markdown
# My Skill

## Quick Start
[Brief overview and common usage]

## Advanced Features
For complete API documentation, see [reference.md](reference.md).
For usage patterns, see [examples.md](examples.md).
```

Claude loads additional files only when needed.

### Avoid Deeply Nested References

**Keep references one level deep from SKILL.md**.

**Bad** (too deep):
```markdown
# SKILL.md
See [advanced.md](advanced.md)...

# advanced.md
See [details.md](details.md)...

# details.md
Here's the actual information...
```

**Good** (one level):
```markdown
# SKILL.md

**Basic usage**: [instructions in SKILL.md]
**Advanced features**: See [advanced.md](advanced.md)
**API reference**: See [reference.md](reference.md)
**Examples**: See [examples.md](examples.md)
```

### Structure Longer Reference Files

For reference files >100 lines, include a table of contents:

```markdown
# API Reference

## Contents
- Authentication and setup
- Core methods (create, read, update, delete)
- Advanced features (batch operations, webhooks)
- Error handling patterns
- Code examples

## Authentication and Setup
...

## Core Methods
...
```

## Content Guidelines

### Be Concise

**Challenge each piece of information**:
- Does Claude really need this explanation?
- Can I assume Claude knows this?
- Does this justify its token cost?

**Good** (concise):
````markdown
## Extract PDF Text

Use pdfplumber:

```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
````

**Bad** (too verbose):
```markdown
## Extract PDF Text

PDF (Portable Document Format) files are a common file format that contains
text, images, and other content. To extract text from a PDF, you'll need to
use a library. There are many libraries available for PDF processing, but we
recommend pdfplumber because it's easy to use and handles most cases well.
First, you'll need to install it using pip. Then you can use the code below...
```

### Use Consistent Terminology

Choose one term and use it throughout:

**Good**:
- Always "API endpoint"
- Always "field"
- Always "extract"

**Bad**:
- Mix "API endpoint", "URL", "API route", "path"
- Mix "field", "box", "element", "control"

### Avoid Time-Sensitive Information

**Bad**:
```markdown
If you're doing this before August 2025, use the old API.
```

**Good**:
```markdown
## Current Method
Use the v2 API: `api.example.com/v2/messages`

## Old Patterns
<details>
<summary>Legacy v1 API (deprecated 2025-08)</summary>
The v1 API used: `api.example.com/v1/messages`
This endpoint is no longer supported.
</details>
```

## Tool Restrictions (Optional)

Use `allowed-tools` to limit which tools Claude can use when the skill is active:

```yaml
---
name: Safe File Reader
description: Read files without making changes. Use when you need read-only file access.
allowed-tools: Read, Grep, Glob
---

# Safe File Reader

This skill provides read-only file access.

## Instructions
1. Use Read to view file contents
2. Use Grep to search within files
3. Use Glob to find files by pattern
```

When this skill is active, Claude can only use the specified tools without asking permission.

**Use cases**:
- Read-only skills that shouldn't modify files
- Limited scope skills (e.g., only data analysis, no file writing)
- Security-sensitive workflows

## Testing Your Skill

### 1. Test by Asking Relevant Questions

Ask questions that match your description:

**Example**: If your description mentions "PDF files":
```
Can you help me extract text from this PDF?
```

Claude should autonomously use your skill.

### 2. Check Skill Discovery

**List all skills**:
Ask Claude: "What skills are available?"

**Verify file structure**:
```bash
# Personal
ls ~/.claude/skills/my-skill/SKILL.md

# Project
ls .claude/skills/my-skill/SKILL.md
```

### 3. Debug Common Issues

**Skill doesn't activate**:
- Make description more specific
- Include trigger terms users would mention
- Add "when to use" guidance

**YAML syntax errors**:
```bash
cat SKILL.md | head -n 10
```

Ensure:
- Opening `---` on line 1
- Closing `---` before markdown
- Valid YAML (no tabs, correct indentation)

**Wrong location**:
Check skill is in correct directory with SKILL.md file.

## Complete Examples

### Simple Skill (Single File)

```
commit-helper/
└── SKILL.md
```

**SKILL.md**:
```yaml
---
name: Generating Commit Messages
description: Generates clear commit messages from git diffs. Use when writing commit messages or reviewing staged changes.
---

# Generating Commit Messages

## Instructions

1. Run `git diff --staged` to see changes
2. Suggest a commit message with:
   - Summary under 50 characters
   - Detailed description
   - Affected components

## Best Practices

- Use present tense
- Explain what and why, not how
```

### Multi-File Skill

```
pdf-processing/
├── SKILL.md
├── FORMS.md
├── REFERENCE.md
└── scripts/
    ├── fill_form.py
    └── validate.py
```

**SKILL.md**:
````yaml
---
name: PDF Processing
description: Extract text, fill forms, merge PDFs. Use when working with PDF files, forms, or document extraction. Requires pypdf and pdfplumber packages.
---

# PDF Processing

## Quick Start

Extract text:
```python
import pdfplumber
with pdfplumber.open("doc.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

For form filling, see [FORMS.md](FORMS.md).
For detailed API reference, see [REFERENCE.md](REFERENCE.md).

## Requirements

Install packages:
```bash
pip install pypdf pdfplumber
```
````

## Best Practices Summary

✅ **Do**:
- Write descriptions in third person
- Include trigger terms in description
- Keep SKILL.md under 500 lines
- Use progressive disclosure for large content
- Be concise - assume Claude is smart
- Use consistent terminology
- Test with relevant questions
- Keep skills focused (one capability per skill)

❌ **Don't**:
- Write vague descriptions
- Include time-sensitive information
- Nest references more than one level deep
- Over-explain things Claude already knows
- Create overly broad skills
- Use inconsistent terminology
