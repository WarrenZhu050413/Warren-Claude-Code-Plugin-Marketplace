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

Create new Agent Skills with proper structure and descriptions.

**Quick Start**:
```bash
mkdir -p ~/.claude/skills/my-skill
```

**⚠️ IMPORTANT: Always Create HTML Summary**

After creating a skill, generate a high-density, minimalistic black HTML summary page and open it in the browser:

```bash
# Generate HTML summary (use template)
cat > skill-summary.html << 'EOF'
[HTML content with skill details]
EOF

# Open in browser
open skill-summary.html
```

**HTML Summary Must Include:**
- Skill name, description, triggers
- Files created
- What it does
- Key features
- Usage examples
- Configuration details
- Testing instructions
- Related skills
- Next steps
- Verification commands
- Completion summary

**Style Requirements:**
- Black background (#000)
- High information density
- Minimalistic design
- Green/cyan accents (#0f0, #0ff)
- Monospace fonts
- Compact layout

For complete guidance, see [creating.md](creating.md).

### Reading Skills

List, view, and inspect available Agent Skills.

**Quick Start**:
Ask Claude: "What skills are available?"

For complete guidance, see [reading.md](reading.md).

### Updating Skills

Modify and maintain existing Agent Skills.

**Quick Start**:
```bash
code ~/.claude/skills/my-skill/SKILL.md
```

Changes take effect after restarting Claude Code.

For complete guidance, see [updating.md](updating.md).

### Deleting Skills

Safely remove Agent Skills with backup.

**Quick Start**:
```bash
cp -r ~/.claude/skills/my-skill ~/.claude/skills/my-skill.backup
rm -rf ~/.claude/skills/my-skill
```

For complete guidance, see [deleting.md](deleting.md).

## Snippet Configuration

Skills can optionally have snippet entries in `config.local.json` for hook-based injection. This allows skills to be triggered by specific keywords in user prompts.

### When to Add Snippet Entries

Add snippet entries when:
- You want keyword-based triggering (e.g., typing `BUILD_MCP` loads the building-mcp skill)
- The skill is frequently used and benefits from explicit activation
- You want backward compatibility with the hook-based snippet system

**Note**: Most skills work fine without snippet entries - they're discovered automatically via descriptions.

### Regex Pattern Convention

**All snippet trigger patterns MUST follow the ALL CAPS convention**:

- **Format**: `\\b<KEYWORD>[.,;:]?\\b`
- **Style**: ALL CAPS, descriptive, not too long (≤15 chars)
- **Multi-word naming**: Use one of these separators:
  - **Underscore**: `BUILD_ARTIFACT`, `MANAGE_SKILL` (preferred)
  - **Hyphen**: `BUILD-ARTIFACT`, `MANAGE-SKILL`
  - **No separator**: `BUILDARTIFACT`, `MANAGESKILL`
- **Examples**:
  - ✅ `BUILD_ARTIFACT`, `BUILD-ARTIFACT`, `BUILDARTIFACT`
  - ❌ `build-artifact`, `BuildArtifact`, `Build_Artifact`

### Adding Snippet Entries

Snippet entries are stored in `scripts/config.local.json` (gitignored) or `scripts/config.json` (committed).

**By default, add entries to `config.local.json`** for personal configurations.

#### ⚠️ CRITICAL: ALWAYS Use CLI for Config Editing

**REQUIRED: Use `snippets_cli.py` CLI for ALL config modifications**

```bash
cd ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/scripts

# Create new snippet with file reference
python3 snippets_cli.py create my-skill \
  --pattern "\\bMY_SKILL[.,;:]?\\b" \
  --file ../skills/my-skill/SKILL.md

# Update existing pattern
python3 snippets_cli.py update my-skill \
  --pattern "\\bNEW_PATTERN[.,;:]?\\b"

# Update pattern AND content
python3 snippets_cli.py update my-skill \
  --pattern "\\bNEW_PATTERN[.,;:]?\\b" \
  --file ../skills/my-skill/SKILL.md

# Enable/disable snippet
python3 snippets_cli.py update my-skill --enabled true
python3 snippets_cli.py update my-skill --enabled false

# Delete snippet
python3 snippets_cli.py delete my-skill
```

**Why CLI-only?**

The CLI ensures:
- ✅ Proper validation
- ✅ Automatic backups
- ✅ Pattern format checking
- ✅ Conflict detection
- ✅ File integrity
- ✅ JSON syntax validation
- ✅ Transaction safety

❌ **NEVER manually edit config files** - This can cause:
- Invalid JSON syntax
- Pattern conflicts
- Missing backups
- Configuration corruption
- No validation

#### CLI Operations Reference

**List all snippets:**
```bash
python3 snippets_cli.py list
python3 snippets_cli.py list | grep "my-skill"
```

**Get snippet details:**
```bash
python3 snippets_cli.py get my-skill
python3 snippets_cli.py get my-skill --json
```

**Create snippet referencing a skill:**
```bash
# Reference existing SKILL.md
python3 snippets_cli.py create my-skill \
  --pattern "\\bMY_SKILL[.,;:]?\\b" \
  --file ../skills/my-skill/SKILL.md

# Or create new content
python3 snippets_cli.py create my-snippet \
  --pattern "\\bMY_SNIPPET[.,;:]?\\b" \
  --content "Snippet content here"
```

**Update snippet:**
```bash
# Update pattern only
python3 snippets_cli.py update my-skill \
  --pattern "\\bNEW_PATTERN[.,;:]?\\b"

# Update both pattern and file reference
python3 snippets_cli.py update my-skill \
  --pattern "\\bNEW_PATTERN[.,;:]?\\b" \
  --file ../skills/my-skill/SKILL.md

# Rename snippet
python3 snippets_cli.py update my-skill --rename new-name
```

**Delete snippet:**
```bash
# With backup (default)
python3 snippets_cli.py delete my-skill

# Force without confirmation
python3 snippets_cli.py delete my-skill --force

# Skip backup
python3 snippets_cli.py delete my-skill --force --backup false
```

For complete CLI documentation, see the [Using CLIs](../using-clis/SKILL.md) skill.

### Current Skill Snippet Entries

These skills have snippet entries in `config.local.json`:

| Skill | Trigger Pattern | Purpose |
|-------|----------------|---------|
| building-artifacts | `BUILD_ARTIFACT` | Build claude.ai HTML artifacts |
| building-mcp | `BUILD_MCP` | Create MCP servers |
| managing-skills | `MANAGE_SKILL` | Manage Agent Skills |
| managing-snippets | `MANAGE_SNIPPET` | Manage snippet configs |
| searching-deeply | `DEEP_SEARCH` | Deep web/code search |
| testing-webapps | `TEST_WEB` | Test web apps with Playwright |
| theming-artifacts | `THEME_ARTIFACT` | Apply themes to artifacts |
| using-claude | `USE_CLAUDE` | Claude Code features & debugging |
| using-codex | `USE_CODEX` | Codex MCP analysis tool |

### Best Practices

✅ **Do**:
- Use ALL CAPS for trigger keywords
- For multi-word patterns, use `_`, `-`, or no separator consistently
- Keep patterns short and memorable (≤15 chars)
- Point `snippet` to `SKILL.md` by default
- Add to `config.local.json` for personal use
- Add to `config.json` for shared/committed patterns

❌ **Don't**:
- Use lowercase or mixed case in patterns
- Mix separators within the same pattern (e.g., `BUILD_ARTIFACT-TEST`)
- Use spaces in patterns
- Make patterns too long (>15 chars)
- Include multiple files unless necessary
- Duplicate patterns across different skills

### Testing Snippet Entries

After adding snippet entries:

1. **Restart Claude Code** to reload configurations
2. **Test pattern matching**:
   ```bash
   cd scripts
   python3 -c "import re; print(re.search(r'\\bMY_SKILL[.,;:]?\\b', 'MY_SKILL'))"
   ```
3. **Verify in conversation**: Type the trigger keyword in a prompt

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
