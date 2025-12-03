# Updating Skills

Guidance for modifying and maintaining existing Agent Skills in Claude Code.

## Quick Update Process

### 1. Locate the Skill

```bash
# Personal skills
ls ~/.claude/skills/*/SKILL.md

# Project skills
ls .claude/skills/*/SKILL.md

# Find specific skill
find ~/.claude/skills -name "SKILL.md" -path "*/my-skill/*"
```

### 2. Edit SKILL.md

```bash
# Personal
code ~/.claude/skills/my-skill/SKILL.md

# Project
code .claude/skills/my-skill/SKILL.md
```

### 3. Apply Changes

Changes take effect the next time Claude Code starts.

**If Claude Code is already running**: Restart it to load updates.

## Common Update Scenarios

### Update Description

The description is critical for skill discovery. Update it when:
- Skill's purpose has expanded
- Trigger terms need refinement
- Usage context has changed

**Requirements**:
- Write in third person
- Include what the skill does AND when to use it
- Add specific trigger terms
- Maximum 1024 characters

**Before**:
```yaml
description: Helps with PDFs
```

**After**:
```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

### Update Instructions

When adding new features or improving clarity:

**Before** (vague):
```markdown
## Instructions

Process the data and generate output.
```

**After** (specific):
```markdown
## Instructions

1. Load data from CSV file using pandas:
   ```python
   import pandas as pd
   df = pd.read_csv('data.csv')
   ```

2. Clean data:
   - Remove null values
   - Normalize formats
   - Validate ranges

3. Generate summary statistics:
   ```python
   summary = df.describe()
   ```

4. Export results to Excel:
   ```python
   summary.to_excel('output.xlsx')
   ```
```

### Add Examples

Examples improve skill effectiveness. Add input/output pairs:

````markdown
## Examples

**Example 1: Simple Extraction**
Input: PDF with plain text
Output:
```python
import pdfplumber
with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

**Example 2: Table Extraction**
Input: PDF with tables
Output:
```python
import pdfplumber
with pdfplumber.open("tables.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            # Process table data
            pass
```
````

### Add or Update allowed-tools

Restrict which tools Claude can use when the skill is active:

**Before** (no restrictions):
```yaml
---
name: Data Analyzer
description: Analyze data files and generate reports
---
```

**After** (read-only):
```yaml
---
name: Data Analyzer
description: Analyze data files and generate reports
allowed-tools: Read, Grep, Glob
---
```

This ensures Claude can't modify files when using this skill.

### Split Large Skills

If SKILL.md exceeds 500 lines, use progressive disclosure:

**Before** (single large file):
```markdown
# PDF Processing

## Basic Text Extraction
[100 lines of content...]

## Advanced Table Extraction
[150 lines of content...]

## Form Filling
[200 lines of content...]

## API Reference
[300 lines of content...]
```

**After** (split into multiple files):

```
pdf-processing/
├── SKILL.md              # Overview and quick start
├── tables.md             # Table extraction guide
├── forms.md              # Form filling guide
└── reference.md          # Complete API docs
```

**SKILL.md**:
```markdown
# PDF Processing

## Quick Start
[Brief overview]

## Text Extraction
[Common usage]

## Advanced Features
- **Table Extraction**: See [tables.md](tables.md)
- **Form Filling**: See [forms.md](forms.md)
- **Complete API**: See [reference.md](reference.md)
```

### Update Reference Files

When updating longer reference files (>100 lines), include a table of contents:

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

## Refactoring Patterns

### Make Skills More Concise

Remove unnecessary explanations:

**Before** (too verbose):
```markdown
JSON (JavaScript Object Notation) is a data format that is commonly used
for APIs and configuration files. It uses key-value pairs and is human-readable.
To parse JSON in Python, you'll need to import the json module, which is
part of the standard library so you don't need to install anything extra.
```

**After** (concise):
```markdown
Parse JSON:
```python
import json
with open('data.json') as f:
    data = json.load(f)
```
```

### Improve Terminology Consistency

**Before** (inconsistent):
```markdown
Use the API endpoint to send a request to the URL. The route will return...
The path can be accessed via the API...
```

**After** (consistent):
```markdown
Use the API endpoint to send a request. The endpoint will return...
The endpoint can be accessed via...
```

(Always use "API endpoint", never mix with "URL", "route", "path")

### Add Workflows for Complex Tasks

When users struggle with multi-step processes:

````markdown
## Data Analysis Workflow

Copy this checklist and track your progress:

```
Task Progress:
- [ ] Step 1: Load and validate data
- [ ] Step 2: Clean and normalize data
- [ ] Step 3: Perform analysis
- [ ] Step 4: Generate visualizations
- [ ] Step 5: Export results
```

**Step 1: Load and validate data**
```python
import pandas as pd
df = pd.read_csv('data.csv')
assert len(df) > 0, "Data file is empty"
assert not df.isnull().all().any(), "Column has all null values"
```

**Step 2: Clean and normalize data**
[Detailed instructions...]

**Step 3: Perform analysis**
[Detailed instructions...]

**Step 4: Generate visualizations**
[Detailed instructions...]

**Step 5: Export results**
[Detailed instructions...]
````

### Add Feedback Loops

For error-prone operations:

**Before** (no validation):
```markdown
1. Make changes to config.json
2. Deploy application
3. Test in production
```

**After** (with validation loop):
```markdown
1. Make changes to config.json
2. **Validate immediately**: `python scripts/validate_config.py`
3. If validation fails:
   - Review error messages
   - Fix issues in config.json
   - Run validation again
4. **Only proceed when validation passes**
5. Deploy to staging
6. Test in staging environment
7. Deploy to production
```

## Version Management

### Document Changes

Add a version history section to track updates:

```markdown
# My Skill

## Version History
- v2.1.0 (2025-10-16): Added batch processing support
- v2.0.0 (2025-10-01): Breaking changes to API
- v1.1.0 (2025-09-15): Added table extraction
- v1.0.0 (2025-09-01): Initial release

## Instructions
...
```

### Deprecate Features

When removing old approaches:

```markdown
## Current Method

Use the v2 API for all new integrations:
```python
from api.v2 import Client
client = Client(api_key="...")
```

## Old Patterns

<details>
<summary>Legacy v1 API (deprecated 2025-08)</summary>

The v1 API used a different client:
```python
from api.v1 import OldClient  # Don't use
```

This API is no longer supported. Migrate to v2.
</details>
```

## Testing Updates

### 1. Verify YAML Syntax

After updating frontmatter:

```bash
cat SKILL.md | head -n 10
```

Check:
- Opening `---` on line 1
- Closing `---` before markdown content
- Valid YAML (no tabs, correct indentation)
- No special characters in unquoted strings

### 2. Test Description Changes

If you updated the description, test that Claude uses the skill appropriately:

Ask questions that match your new description and verify Claude activates the skill.

### 3. Check File References

If you added or renamed reference files, verify links work:

```bash
cd ~/.claude/skills/my-skill

# Check that referenced files exist
ls -l *.md
```

### 4. Verify Examples Run

If you added code examples, test them:

```bash
# Extract and run Python examples
python test_examples.py
```

## Common Update Mistakes

### ❌ Forgetting to Restart

**Problem**: Updates don't appear after editing SKILL.md

**Solution**: Restart Claude Code to load changes

### ❌ Breaking YAML Frontmatter

**Problem**: Skill stops working after update

**Check**:
```bash
cat SKILL.md | head -n 10
```

**Common issues**:
- Missing closing `---`
- Tabs instead of spaces
- Unquoted strings with colons
- Incorrect indentation

### ❌ Making Description Too Generic

**Problem**: Skill activates too often or not at all

**Before**:
```yaml
description: Helps with files
```

**After**:
```yaml
description: Analyzes log files and system metrics for performance monitoring, debugging, and diagnostics. Use when analyzing logs, system performance, or troubleshooting issues.
```

### ❌ Adding Too Much Content

**Problem**: SKILL.md becomes >500 lines

**Solution**: Use progressive disclosure:
- Keep core instructions in SKILL.md
- Move detailed content to separate reference files
- Link to reference files from SKILL.md

### ❌ Nested References

**Problem**: Claude doesn't find information in deeply nested files

**Bad** (too deep):
```markdown
# SKILL.md → references advanced.md
# advanced.md → references details.md
# details.md → has the actual info
```

**Good** (one level):
```markdown
# SKILL.md → directly references all docs
- advanced.md
- details.md
- examples.md
```

## Rollback Strategy

### Create Backup Before Major Changes

```bash
# Backup entire skill
cp -r ~/.claude/skills/my-skill ~/.claude/skills/my-skill.backup

# Or just backup SKILL.md
cp ~/.claude/skills/my-skill/SKILL.md ~/.claude/skills/my-skill/SKILL.md.backup
```

### Restore from Backup

```bash
# Restore entire skill
rm -rf ~/.claude/skills/my-skill
mv ~/.claude/skills/my-skill.backup ~/.claude/skills/my-skill

# Or just restore SKILL.md
mv ~/.claude/skills/my-skill/SKILL.md.backup ~/.claude/skills/my-skill/SKILL.md
```

### Use Version Control

For project skills (in git repositories):

```bash
# See what changed
git diff .claude/skills/my-skill/SKILL.md

# Revert changes
git checkout .claude/skills/my-skill/SKILL.md

# Commit updates
git add .claude/skills/my-skill/
git commit -m "Update my-skill: add batch processing support"
```

## Team Collaboration

### Communicate Changes

For project skills, notify team members:

```bash
git commit -m "Update PDF skill: add form filling capability

- Added form filling workflow
- Updated description to include 'forms' trigger
- Added forms.md reference guide

Team members should restart Claude Code to get updates."

git push
```

### Review Process

For shared skills, consider a review process:

1. Create feature branch
2. Update skill
3. Test thoroughly
4. Create pull request
5. Have teammate review
6. Merge when approved
7. Team members pull and restart
