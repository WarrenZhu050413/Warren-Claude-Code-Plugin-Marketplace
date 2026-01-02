# Reading Skills

Guidance for listing, viewing, and inspecting Agent Skills in Claude Code.

## Quick Reference

### List All Available Skills

Ask Claude:
```
What skills are available?
```

or

```
List all available skills
```

Claude will show all skills from:
- Personal skills (`~/.claude/skills/`)
- Project skills (`.claude/skills/`)
- Plugin skills (from installed plugins)

### View Specific Skill

```bash
# Personal skill
cat ~/.claude/skills/my-skill/SKILL.md

# Project skill
cat .claude/skills/my-skill/SKILL.md

# Open in editor
code ~/.claude/skills/my-skill/SKILL.md
```

## Filesystem Commands

### List Personal Skills

```bash
# List all personal skills
ls ~/.claude/skills/

# List with details
ls -la ~/.claude/skills/

# Show skill names only
ls -1 ~/.claude/skills/
```

### List Project Skills

```bash
# From project root
ls .claude/skills/

# Find all project skills recursively
find . -path "*/.claude/skills/*/SKILL.md"
```

### View Skill Metadata

Extract name and description from YAML frontmatter:

```bash
# View frontmatter
head -n 10 ~/.claude/skills/my-skill/SKILL.md

# Extract just description
grep "description:" ~/.claude/skills/my-skill/SKILL.md
```

### Check Skill Structure

```bash
# List all files in skill directory
ls -la ~/.claude/skills/my-skill/

# Show directory tree
tree ~/.claude/skills/my-skill/

# Or without tree command
find ~/.claude/skills/my-skill/ -type f
```

## Inspection Patterns

### View Complete Skill Content

```bash
# View entire SKILL.md
cat ~/.claude/skills/my-skill/SKILL.md

# View with pagination
less ~/.claude/skills/my-skill/SKILL.md

# View with line numbers
cat -n ~/.claude/skills/my-skill/SKILL.md
```

### View Skill Supporting Files

```bash
# List all markdown files
ls ~/.claude/skills/my-skill/*.md

# View reference file
cat ~/.claude/skills/my-skill/reference.md

# View examples
cat ~/.claude/skills/my-skill/examples.md
```

### Search Within Skills

```bash
# Search for keyword in specific skill
grep -r "PDF" ~/.claude/skills/pdf-processing/

# Search across all personal skills
grep -r "authentication" ~/.claude/skills/

# Case-insensitive search
grep -ri "docker" ~/.claude/skills/
```

### Check Skill Size

```bash
# Size of SKILL.md
wc -l ~/.claude/skills/my-skill/SKILL.md

# Total size of skill directory
du -sh ~/.claude/skills/my-skill/

# Detailed size breakdown
du -h ~/.claude/skills/my-skill/*
```

## Finding Skills

### By Name Pattern

```bash
# Find skills with "pdf" in name
ls ~/.claude/skills/ | grep -i pdf

# Find all skills with "processing" in name
find ~/.claude/skills/ -type d -name "*processing*"
```

### By Description Content

```bash
# Find skills mentioning "Excel"
grep -l "Excel" ~/.claude/skills/*/SKILL.md

# Find skills with "API" in description
grep "description:.*API" ~/.claude/skills/*/SKILL.md
```

### By Trigger Terms

```bash
# Find which skill handles "docker"
for skill in ~/.claude/skills/*/SKILL.md; do
    if grep -qi "docker" "$skill"; then
        echo "Found in: $(dirname $skill)"
        grep "description:" "$skill"
    fi
done
```

## Understanding Skill Structure

### Check if Skill Has allowed-tools

```bash
# Check frontmatter for allowed-tools
head -n 15 ~/.claude/skills/my-skill/SKILL.md | grep "allowed-tools"
```

If present, the skill restricts which tools Claude can use.

### Identify Progressive Disclosure

```bash
# Check if skill references other files
grep -E "\[.*\]\(.*\.md\)" ~/.claude/skills/my-skill/SKILL.md

# List referenced files
ls ~/.claude/skills/my-skill/*.md
```

Skills with multiple .md files use progressive disclosure.

### Check for Scripts

```bash
# Check if skill has scripts
ls ~/.claude/skills/my-skill/scripts/

# Check for templates
ls ~/.claude/skills/my-skill/templates/
```

## Comparing Skills

### Compare Two Skill Descriptions

```bash
# View both descriptions
echo "=== Skill A ==="
head -n 10 ~/.claude/skills/skill-a/SKILL.md

echo "=== Skill B ==="
head -n 10 ~/.claude/skills/skill-b/SKILL.md
```

### Find Overlapping Skills

```bash
# Check if two skills have similar descriptions
skill_a_desc=$(grep "description:" ~/.claude/skills/skill-a/SKILL.md)
skill_b_desc=$(grep "description:" ~/.claude/skills/skill-b/SKILL.md)

echo "Skill A: $skill_a_desc"
echo "Skill B: $skill_b_desc"
```

If descriptions overlap significantly, consider consolidating.

### Diff Two Skills

```bash
# Compare skill structures
diff ~/.claude/skills/skill-a/SKILL.md ~/.claude/skills/skill-b/SKILL.md

# Or use a better diff tool
code --diff ~/.claude/skills/skill-a/SKILL.md ~/.claude/skills/skill-b/SKILL.md
```

## Validation Checks

### Verify YAML Frontmatter

```bash
# Check frontmatter syntax
head -n 15 ~/.claude/skills/my-skill/SKILL.md

# Verify required fields present
head -n 10 ~/.claude/skills/my-skill/SKILL.md | grep -E "(name:|description:)"
```

Required fields:
- `name:` - Skill name
- `description:` - What it does and when to use it

### Check File Existence

```bash
# Verify SKILL.md exists
test -f ~/.claude/skills/my-skill/SKILL.md && echo "✓ SKILL.md exists" || echo "✗ SKILL.md missing"

# Check for broken references
for ref in $(grep -oE "\[.*\]\((.*\.md)\)" ~/.claude/skills/my-skill/SKILL.md | grep -oE "\(.*\.md\)" | tr -d '()'); do
    if [ -f "~/.claude/skills/my-skill/$ref" ]; then
        echo "✓ $ref exists"
    else
        echo "✗ $ref missing"
    fi
done
```

### Validate Description Length

```bash
# Check description character count
desc=$(grep "description:" ~/.claude/skills/my-skill/SKILL.md | cut -d':' -f2-)
echo "Description length: ${#desc} characters (max 1024)"

if [ ${#desc} -gt 1024 ]; then
    echo "⚠️  Description too long!"
fi
```

## Organizing Skill Information

### Create Skill Inventory

```bash
# Generate list of all skills with descriptions
for skill in ~/.claude/skills/*/SKILL.md; do
    skill_name=$(dirname $skill | xargs basename)
    description=$(grep "description:" "$skill" | cut -d':' -f2-)
    echo "- **$skill_name**: $description"
done
```

### Export Skill Documentation

```bash
# Create markdown file with all skill info
{
    echo "# Personal Skills Inventory"
    echo ""
    for skill in ~/.claude/skills/*/SKILL.md; do
        echo "## $(grep "name:" $skill | cut -d':' -f2-)"
        echo ""
        echo "**Description**: $(grep "description:" $skill | cut -d':' -f2-)"
        echo ""
        echo "**Location**: $skill"
        echo ""
        echo "---"
        echo ""
    done
} > ~/skills-inventory.md
```

### Generate Skills Summary

```bash
# Count skills by location
personal_count=$(ls ~/.claude/skills/ 2>/dev/null | wc -l)
project_count=$(ls .claude/skills/ 2>/dev/null | wc -l)

echo "Skills Summary:"
echo "  Personal: $personal_count"
echo "  Project:  $project_count"
echo "  Total:    $((personal_count + project_count))"
```

## Troubleshooting

### Skill Not Appearing

**Check if file exists**:
```bash
ls ~/.claude/skills/my-skill/SKILL.md
```

**Check YAML syntax**:
```bash
head -n 10 ~/.claude/skills/my-skill/SKILL.md
```

**Verify location**:
- Personal: `~/.claude/skills/skill-name/SKILL.md`
- Project: `.claude/skills/skill-name/SKILL.md`

### Cannot Read Skill File

**Check permissions**:
```bash
ls -la ~/.claude/skills/my-skill/SKILL.md

# Fix if needed
chmod 644 ~/.claude/skills/my-skill/SKILL.md
```

### Skill Directory Empty

```bash
# Check if skills directory exists
ls -la ~/.claude/skills/

# Create if missing
mkdir -p ~/.claude/skills/
```

## Best Practices

### Regular Skill Audits

Periodically review your skills:

```bash
# List all skills with last modified date
ls -lt ~/.claude/skills/*/SKILL.md

# Find skills not modified in 90 days
find ~/.claude/skills/ -name "SKILL.md" -mtime +90
```

Consider updating or removing stale skills.

### Document Your Skills

Maintain a skills inventory:

```markdown
# My Claude Code Skills

## Active Skills
- **pdf-processing**: Extract and manipulate PDFs
- **data-analysis**: Analyze CSV and Excel files
- **commit-helper**: Generate git commit messages

## Experimental
- **new-skill**: Testing new approach

## Deprecated
- **old-skill**: Replaced by new-skill
```

### Track Skill Usage

Note which skills you use frequently:

```markdown
# Skill Usage Notes

## Frequently Used
- commit-helper (daily)
- pdf-processing (weekly)

## Rarely Used
- legacy-api (consider removing)

## Never Used
- experiment-1 (delete)
```
