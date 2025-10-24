---
name: Managing Skills
description: Comprehensive guidance for creating, reading, updating, and deleting Agent Skills in Claude Code. Use when the user asks to create, list, view, modify, update, delete, or manage skills, or needs help with skill authoring, structure, descriptions, naming conventions, or best practices.
---

# Managing Skills

Comprehensive guidance for managing Agent Skills in Claude Code, following official best practices.

## Core Principles

### 1. Conciseness is Critical

The context window is shared across all skills, conversation history, and the current task. Every token counts.

**Default assumption**: Claude already has extensive knowledge. Only add information Claude doesn't already know.

**Challenge each piece of information**:

- Does Claude really need this explanation?
- Can I assume Claude knows this?
- Does this content justify its token cost?

**Example - Concise** (preferred):

```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

**Example - Too verbose** (avoid):

```
PDF (Portable Document Format) files are a common file format...
To extract text, you'll need to use a library. There are many
libraries available, but we recommend pdfplumber because...
```

### 2. Progressive Disclosure

Keep SKILL.md under 500 lines. Use separate reference files for detailed content.

**Pattern**:

```markdown
# My Skill

## Quick Start

[Brief overview and common usage]

## Advanced Features

See [reference.md](reference.md) for complete API documentation.
See [examples.md](examples.md) for usage patterns.
```

Claude loads additional files only when needed.

### 3. Clear Descriptions

Descriptions enable skill discovery. Include both WHAT the skill does and WHEN to use it.

**Requirements**:

- Write in third person (this goes in system prompt)
- Be specific with trigger terms
- Include key terms users would mention
- Maximum 1024 characters

**Good**:

```yaml
description: Analyzes Excel spreadsheets, creates pivot tables, generates charts. Use when working with Excel files, spreadsheets, tabular data, or .xlsx files.
```

**Bad**:

```yaml
description: Helps with documents
```

## Skill Structure

### Required: SKILL.md with YAML Frontmatter

```yaml
---
name: Your Skill Name
description: What it does and when to use it (include trigger terms)
---

# Your Skill Name

## Instructions
[Step-by-step guidance]

## Examples
[Concrete examples]
```

### Optional: Supporting Files

```
my-skill/
├── SKILL.md (required)
├── reference.md (detailed documentation)
├── examples.md (usage examples)
├── scripts/
│   └── helper.py
└── templates/
    └── template.txt
```

Reference files from SKILL.md:

```markdown
For advanced usage, see [reference.md](reference.md).
```

### Tool Restrictions (allowed-tools)

Limit which tools Claude can use when a skill is active:

```yaml
---
name: Safe File Reader
description: Read files without making changes. Use when you need read-only file access.
allowed-tools: Read, Grep, Glob
---
```

When active, Claude can only use the specified tools without asking permission.

## Naming Conventions

**Prefer gerund form** (verb + -ing):

- "Processing PDFs"
- "Analyzing Spreadsheets"
- "Managing Databases"
- "Testing Code"
- "Writing Documentation"

**Avoid**:

- Vague names: "Helper", "Utils", "Tools"
- Overly generic: "Documents", "Data", "Files"

## Best Practices

### Keep Skills Focused

One skill = one capability

**Good** (focused):

- "PDF form filling"
- "Excel data analysis"
- "Git commit messages"

**Too broad** (split into separate skills):

- "Document processing"
- "Data tools"

### Use Workflows for Complex Tasks

For multi-step processes, provide a clear checklist:

````markdown
## PDF Form Filling Workflow

Copy this checklist and track your progress:

```
Task Progress:
- [ ] Step 1: Analyze form structure
- [ ] Step 2: Create field mapping
- [ ] Step 3: Validate mapping
- [ ] Step 4: Fill the form
- [ ] Step 5: Verify output
```

**Step 1: Analyze form structure**
Run: `python scripts/analyze_form.py input.pdf`
...
````

### Implement Feedback Loops

For error-prone operations, validate after each step:

```markdown
## Document Editing Process

1. Make edits to `word/document.xml`
2. **Validate immediately**: `python scripts/validate.py`
3. If validation fails:
   - Review error message
   - Fix issues
   - Run validation again
4. **Only proceed when validation passes**
5. Rebuild document
```

### Avoid Time-Sensitive Information

**Bad** (will become outdated):

```markdown
If you're doing this before August 2025, use the old API.
```

**Good** (use "old patterns" section):

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

### Use Consistent Terminology

Choose one term and use it throughout:

**Good** (consistent):

- Always "API endpoint"
- Always "field"
- Always "extract"

**Bad** (inconsistent):

- Mix "API endpoint", "URL", "API route", "path"

## Common Patterns

### Template Pattern

Provide templates for consistent output:

````markdown
## Report Structure

Use this template:

```markdown
# [Analysis Title]

## Executive Summary

[Overview]

## Key Findings

- Finding 1
- Finding 2

## Recommendations

1. Recommendation 1
2. Recommendation 2
```
````

### Examples Pattern

Show input/output pairs for clarity:

````markdown
## Commit Message Format

**Example 1:**
Input: Added user authentication
Output:

```
feat(auth): implement JWT authentication

Add login endpoint and token validation
```

**Example 2:**
Input: Fixed date bug in reports
Output:

```
fix(reports): correct timezone handling

Use UTC consistently across reports
```
````

### Conditional Workflow Pattern

Guide through decision points:

```markdown
## Document Modification Workflow

1. Determine modification type:
   **Creating new?** → Follow "Creation workflow"
   **Editing existing?** → Follow "Editing workflow"

2. Creation workflow:
   - Use docx-js library
   - Build from scratch

3. Editing workflow:
   - Unpack existing document
   - Modify XML directly
   - Validate changes
```

## Skill Locations

### Personal Skills

**Location**: `~/.claude/skills/`
**Use for**: Individual workflows, experimental skills, personal tools

### Project Skills

**Location**: `.claude/skills/` (in project root)
**Use for**: Team workflows, project-specific expertise, shared utilities
**Note**: Commit to git for team sharing

### Plugin Skills

**Location**: Plugin's `skills/` directory
**Use for**: Distributable skills as part of a plugin
**Note**: Automatically available when plugin is installed

## CRUD Operations

### Creating Skills

#### Step 1: Choose Skill Location

**Personal Skills** (`~/.claude/skills/`):

- Individual workflows, experimental skills, personal tools

**Project Skills** (`.claude/skills/`):

- Team workflows, project-specific expertise, commit to git

**Plugin Skills** (plugin's `skills/` directory):

- Distributable skills, part of plugin packages

#### Step 2: Create Directory & SKILL.md

```bash
# Personal
mkdir -p ~/.claude/skills/my-skill

# Create SKILL.md with required frontmatter
```

**YAML Frontmatter Requirements**:

❌ **WRONG** - Missing YAML or no trigger terms:

```yaml
description: Helps with documents
```

✅ **RIGHT** - Specific, includes when to use:

```yaml
---
name: Your Skill Name
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
---
```

**Why:** Description enables skill discovery and includes both what + when to use.

#### Step 3: Write Clear Instructions

❌ **WRONG** - Too vague:

```markdown
## Instructions

Process the data and generate output.
```

✅ **RIGHT** - Concrete, step-by-step:

````markdown
## Instructions

1. Load data from CSV using pandas:
   ```python
   import pandas as pd
   df = pd.read_csv('data.csv')
   ```
````

2. Clean data:
   - Remove null values
   - Normalize formats

3. Generate summary statistics:
   ```python
   summary = df.describe()
   ```

```

#### Step 4: Keep SKILL.md Under 500 Lines

Use **progressive disclosure** for large content:

```

my-skill/
├── SKILL.md # Main (< 500 lines)
├── reference.md # Detailed API docs
└── examples.md # Usage patterns

````

**In SKILL.md**:
```markdown
## Quick Start
[Brief overview]

## Advanced Features
For complete API documentation, see [reference.md](reference.md).
````

Claude loads additional files only when needed.

#### Step 5: Test Your Skill

Ask Claude a question matching your description:

```
Can you help me extract text from this PDF?
```

Claude should autonomously activate your skill if:

- ✅ Description is specific (includes trigger terms)
- ✅ YAML frontmatter is valid
- ✅ Skill is in correct location
- ✅ Claude Code has been restarted

#### Step 6: Add Contributing Section (Optional)

For skills that benefit from growing with real-world usage, add a "Contributing" section at the **end of SKILL.md**:

```markdown
## Contributing Patterns

When you discover useful workflows or patterns using this skill:

1. Create in `~/.claude/skills/my-skill/workflows/` with clear documentation
2. Update this section with link and brief description
3. Next session will have access to your discovery!

### Available Patterns

- **pattern-name.sh** - What it does, when to use it
- **another-pattern.md** - What it does, when to use it

See: `~/.claude/skills/my-skill/workflows/`
```

**Why:** Creates feedback loop where practical discoveries get captured. Skills become living documents that improve over time from real usage.

**Example:** See `using-github-cli` skill for this pattern in action.

#### HTML Summary (Optional)

For visual verification:

```bash
cd ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/scripts
python3 generate-skill-html.py ../skills/my-skill > /tmp/my-skill-summary.html
open /tmp/my-skill-summary.html
```

For complete guidance, see [creating.md](creating.md).

---

### Reading Skills

#### List All Available Skills

**Ask Claude**:

```
What skills are available?
```

Or use filesystem:

```bash
# Personal skills
ls ~/.claude/skills/

# Project skills
ls .claude/skills/

# With descriptions
head -n 10 ~/.claude/skills/*/SKILL.md
```

#### Inspect a Specific Skill

```bash
# View SKILL.md
cat ~/.claude/skills/my-skill/SKILL.md

# Check directory structure
ls -la ~/.claude/skills/my-skill/

# View referenced files
ls ~/.claude/skills/my-skill/*.md
```

#### Find Skills by Keyword

```bash
# Find skills mentioning "PDF"
grep -l "PDF" ~/.claude/skills/*/SKILL.md

# Find by description
grep "description:.*Excel" ~/.claude/skills/*/SKILL.md
```

#### Validate Skill Structure

Check that a skill has required components:

```bash
# Verify SKILL.md exists
test -f ~/.claude/skills/my-skill/SKILL.md && echo "✓ Found" || echo "✗ Missing"

# Check YAML frontmatter
head -n 10 ~/.claude/skills/my-skill/SKILL.md

# Verify description length (max 1024 chars)
grep "description:" ~/.claude/skills/my-skill/SKILL.md
```

For complete guidance, see [reading.md](reading.md).

---

### Updating Skills

#### Locate & Edit

```bash
# Personal
code ~/.claude/skills/my-skill/SKILL.md

# Project
code .claude/skills/my-skill/SKILL.md
```

❌ **WRONG** - Changes don't appear:

```
Edit SKILL.md → Keep Claude Code running
→ Changes don't load
```

✅ **RIGHT** - Always restart after editing:

```
Edit SKILL.md → Restart Claude Code → Changes load
```

#### Common Updates

**Update Description**:

❌ Generic:

```yaml
description: Helps with PDFs
```

✅ Specific:

```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

**Add Examples**:

````markdown
## Examples

**Example 1: Simple Extraction**
Input: PDF with plain text
Output:

```python
import pdfplumber
with pdfplumber.open("document.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
````

```

**Split Large Skills** (> 500 lines):

```

Before: SKILL.md with 800 lines
After:
├── SKILL.md (overview + quick start)
├── reference.md (API documentation)
└── examples.md (usage patterns)

````

#### Version Management

Track updates:
```markdown
## Version History
- v2.1.0 (2025-10-16): Added batch processing
- v2.0.0 (2025-10-01): Breaking changes to API
- v1.0.0 (2025-09-01): Initial release
````

#### Testing After Update

1. **Verify YAML syntax**:

   ```bash
   head -n 10 SKILL.md
   ```

   Check for: opening `---`, closing `---`, valid YAML

2. **Test with relevant question**:
   Ask Claude a question matching your updated description

3. **Check file references**:
   ```bash
   ls ~/.claude/skills/my-skill/*.md
   ```
   Verify all linked files exist

For complete guidance, see [updating.md](updating.md).

---

### Deleting Skills

#### Simple Deletion

```bash
# Create backup first
cp -r ~/.claude/skills/my-skill ~/.claude/skills/my-skill.backup

# Delete
rm -rf ~/.claude/skills/my-skill

# Verify
ls ~/.claude/skills/
```

#### For Project Skills (in git)

```bash
# Backup
cp -r .claude/skills/my-skill ~/skill-backups/my-skill-backup

# Remove from git
git rm -rf .claude/skills/my-skill

# Commit
git commit -m "Remove my-skill: no longer needed"

# Notify team to restart Claude Code
```

#### Safety Checklist

Before deleting a skill, ask:

- [ ] Is anyone else using this skill?
- [ ] Do I have a backup?
- [ ] Is there a migration path for users?
- [ ] Will this break any workflows?

❌ **WRONG** - Delete without backup:

```bash
rm -rf ~/.claude/skills/my-skill  # Lost forever!
```

✅ **RIGHT** - Always backup first:

```bash
cp -r ~/.claude/skills/my-skill ~/skill-backups/
rm -rf ~/.claude/skills/my-skill
```

#### Restore from Backup

```bash
# Restore entire skill
cp -r ~/skill-backups/my-skill ~/.claude/skills/my-skill

# Restart Claude Code
```

For complete guidance, see [deleting.md](deleting.md).

## Snippet Configuration

Skills can optionally have snippet entries in `config.local.json` for hook-based injection. This allows skills to be triggered by specific keywords in user prompts.

If the managing-snippets skill is available, then read it to understand how to add snippets. You should always add snippet unless the user says otherwise.

### Troubleshooting

**Snippet not loading**:

- Check pattern regex syntax
- Verify file paths are relative to `scripts/` directory
- Ensure `enabled: true`
- Restart Claude Code

**Pattern not matching**:

- Test regex with Python: `python3 -c "import re; print(re.match(r'YOUR_PATTERN', 'test'))"`
- Check for typos in ALL CAPS keyword
- Verify `\\b` word boundaries are present

## Testing Skills

### Make Description Specific

**Too vague**:

```yaml
description: Helps with documents
```

**Specific**:

```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

### Verify File Structure

**Personal Skills**: `~/.claude/skills/skill-name/SKILL.md`
**Project Skills**: `.claude/skills/skill-name/SKILL.md`

Check file exists:

```bash
ls ~/.claude/skills/my-skill/SKILL.md
```

### Check YAML Syntax

Invalid YAML prevents skill loading:

```bash
cat SKILL.md | head -n 10
```

Ensure:

- Opening `---` on line 1
- Closing `---` before markdown content
- Valid YAML (no tabs, correct indentation)

## Troubleshooting

### Claude Doesn't Use My Skill

**Check**: Is the description specific enough?

Include both what the skill does AND when to use it, with key terms users would mention.

**Check**: Is YAML valid?

Run validation:

```bash
cat ~/.claude/skills/my-skill/SKILL.md | head -n 15
```

**Check**: Is the skill in the correct location?

```bash
# Personal
ls ~/.claude/skills/*/SKILL.md

# Project
ls .claude/skills/*/SKILL.md
```

**Check**: Did you restart Claude Code?

Changes to skills require restarting Claude Code to take effect.

### Multiple Skills Conflict

Be specific in descriptions with distinct trigger terms:

**Instead of**:

```yaml
# Skill 1
description: For data analysis

# Skill 2
description: For analyzing data
```

**Use**:

```yaml
# Skill 1
description: Analyze sales data in Excel files and CRM exports. Use for sales reports, pipeline analysis, revenue tracking.

# Skill 2
description: Analyze log files and system metrics. Use for performance monitoring, debugging, system diagnostics.
```

### YAML Frontmatter Errors

**Common issues**:

- Missing closing `---`
- Tabs instead of spaces
- Unquoted strings with colons
- Incorrect indentation

**Validation**:

```bash
cat SKILL.md | head -n 10
```

### Permission Issues

**Check permissions**:

```bash
ls -la ~/.claude/skills/my-skill/SKILL.md
```

**Fix if needed**:

```bash
chmod 644 ~/.claude/skills/my-skill/SKILL.md
```

## External Resources

- Official Docs: https://docs.claude.com/en/docs/claude-code/skills.md
- Best Practices: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices.md
- Quick Start: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/quickstart.md
- Agent Skills Overview: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview.md
