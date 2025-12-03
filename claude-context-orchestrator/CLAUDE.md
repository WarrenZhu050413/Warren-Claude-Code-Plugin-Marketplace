# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ CRITICAL: Apache 2.0 License Compliance - READ BEFORE ANY COMMIT

**MANDATORY PRE-COMMIT WORKFLOW** for ANY modifications to Anthropic-derived skills:

### Step 1: Identify if Your Changes Affect Apache 2.0 Licensed Skills

**Anthropic-derived skills** (Apache 2.0 licensed):
- `skills/building-artifacts/`
- `skills/building-mcp/`
- `skills/testing-webapps/`
- `skills/theming-artifacts/`
- `skills/managing-skills/` (derived from Anthropic documentation)

**If you modified ANY of these**, proceed to Step 2. Otherwise, standard MIT license applies.

### Step 2: Update the NOTICE File

**BEFORE committing**, edit `skills/ANTHROPIC_SKILLS_NOTICE`:

1. **Locate the "MODIFICATIONS:" section** (around line 43)
2. **Add your modification** following this format:

```
MODIFICATIONS:

[Previous modifications...]

Modified by: Fucheng Warren Zhu
Date: [YYYY-MM-DD]

Changes made to [skill-name]:
- [Specific change 1]
- [Specific change 2]
- [Brief description of why the change was needed]

---
```

**Example entry**:
```
Modified by: Fucheng Warren Zhu
Date: 2025-10-21

Changes made to building-artifacts:
- Updated React version in examples from 18.2 to 18.3
- Added TypeScript strict mode examples
- Enhanced template to include Vite configuration

Reason: Updated to current React best practices and added type safety guidance

---
```

### Step 3: Verify License Files Are Present

Ensure these files exist and are unmodified:
- `skills/ANTHROPIC_SKILLS_LICENSE` - Full Apache 2.0 license text
- `skills/ANTHROPIC_SKILLS_NOTICE` - Attribution and modifications tracking
- `LICENSE` - Main MIT license with Apache 2.0 notice

### Step 4: Commit with Proper Attribution

Use commit messages that reference the license:

```bash
git commit -m "Update building-artifacts skill with React 18.3 examples

Modified Apache 2.0 licensed skill from Anthropic example-skills.
See skills/ANTHROPIC_SKILLS_NOTICE for modification details.
"
```

### Quick Reference: What Requires NOTICE Updates?

✅ **YES - Update NOTICE**:
- Modifying skill instructions or content
- Adding/removing examples in Anthropic skills
- Changing skill structure or organization
- Updating references or documentation
- Any functional changes to skill behavior

❌ **NO - No NOTICE update needed**:
- Changes to MIT-licensed skills (using-codex, using-claude, etc.)
- Changes to snippets system (scripts/, snippets/, hooks/)
- Changes to templates (unless in Anthropic skills)
- Documentation updates outside skills directory
- Test file modifications

---

## Project Overview

**Plugin Name**: `claude-context-orchestrator` (formerly `claude-code-skills-manager`, originally `claude-code-snippets-plugin`)
**Version**: 3.0.0
**Type**: Claude Code plugin with hybrid context management (Agent Skills + deterministic snippets)
**License**: Dual-licensed (MIT + Apache 2.0 for Anthropic skills)

This plugin orchestrates two complementary context injection systems:

1. **Agent Skills** - Model-invoked capabilities including:
   - **Anthropic example-skills** (Apache 2.0): building-artifacts, building-mcp, testing-webapps, theming-artifacts, managing-skills
   - **Warren's custom skills** (MIT): using-codex, using-claude, searching-deeply, making-clearer, managing-snippets

2. **Deterministic Snippets** (MIT) - Hook-based pattern matching for reliable, always-on context injection via UserPromptSubmit hook

This hybrid architecture provides both intelligent, on-demand context (skills) and predictable, rule-based context (snippets) working seamlessly together.

## Architecture

### Core Components

1. **Agent Skills** (`skills/`) - Model-invoked capabilities
   - `managing-skills/` - Overall skill management guidance
   - `creating-skills/` - Instructions for creating new skills
   - `updating-skills/` - Guide for modifying existing skills
   - `deleting-skills/` - Safe deletion procedures
   - `reading-skills/` - Listing and viewing skills
   - Additional skills: `mcp-builder/`, `theme-factory/`, `webapp-testing/`, `artifacts-builder/`

2. **Legacy Snippet System** (`scripts/`, `hooks/`)
   - `snippet_injector.py` - UserPromptSubmit hook for pattern-based injection
   - `snippets_cli.py` - CLI for CRUD operations on snippet configs
   - `config.json` - Base snippet configuration (committed)
   - `config.local.json` - User-specific overrides (gitignored)

3. **Commands** (`commands/`)
   - Slash commands for snippet management (legacy v1.0 compatibility)
   - Local commands in `commands/local/` (user-specific, not in marketplace)

4. **Templates** (`templates/`)
   - Reusable templates for skills (e.g., `html/base-template.html`)
   - Examples and reference documentation

### Configuration System

**Layered Configuration**:
- `config.json`: Base configuration (committed to git)
- `config.local.json`: User-specific overrides (gitignored, takes precedence)
- Config merging priority: base → local → project-specific

**Snippet Injection Hook** (`hooks/hooks.json`):
- Listens to `UserPromptSubmit` events
- Matches patterns against user prompts using regex
- Injects snippet content via `additionalContext`
- Supports multi-file snippets with custom separators

## Common Development Commands

### Testing the Plugin Locally

```bash
# Install plugin locally for testing
/plugin marketplace add file:///Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace
/plugin install claude-context-orchestrator@warren-claude-code-plugin-marketplace

# Verify installation
/help | grep -A5 "claude-context-orchestrator"
```

### Managing Snippets via CLI

```bash
# Navigate to plugin directory
cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator

# List all snippets with statistics
python3 scripts/snippets_cli.py --config scripts/config.json list --show-stats

# Create a new snippet
python3 scripts/snippets_cli.py --config scripts/config.json create my-snippet \
  --pattern "pattern-regex" --content "snippet content"

# Update a snippet
python3 scripts/snippets_cli.py --config scripts/config.json update my-snippet \
  --pattern "new-pattern-regex"

# Delete a snippet (with backup)
python3 scripts/snippets_cli.py --config scripts/config.json delete my-snippet --backup

# Validate snippet configurations
python3 scripts/snippets_cli.py --config scripts/config.json validate
```

### Working with Skills

**List all skills**:
```bash
find skills -name "SKILL.md" | sort
```

**View a skill**:
```bash
cat skills/managing-skills/SKILL.md
```

**Create a new skill**:
```bash
mkdir -p skills/my-skill
cat > skills/my-skill/SKILL.md << 'EOF'
---
name: My Skill Name
description: What it does and when to use it (include trigger keywords)
---

# My Skill Name

[Instructions for Claude]
EOF
```

**Test skill activation**: Ask Claude a question that matches the skill's description keywords

### Running Tests

```bash
# Run all tests
python3 -m pytest tests/

# Run unit tests only
python3 -m pytest tests/unit/

# Run integration tests
python3 -m pytest tests/integration/

# Run validation tests
python3 -m pytest tests/validation/

# Run specific test file
python3 -m pytest tests/unit/test_snippet_injector.py -v
```

### Git Workflow with Apache 2.0 Compliance

**Standard workflow** (for MIT-licensed code):
```bash
git add .
git commit -m "Your commit message"
git push
```

**Apache 2.0 workflow** (for Anthropic-derived skills):
```bash
# 1. Make your changes to an Anthropic skill
vim skills/building-artifacts/SKILL.md

# 2. Update the NOTICE file (CRITICAL!)
vim skills/ANTHROPIC_SKILLS_NOTICE
# Add your modification entry in the MODIFICATIONS section

# 3. Verify license files are present
ls -la skills/ANTHROPIC_SKILLS_LICENSE skills/ANTHROPIC_SKILLS_NOTICE

# 4. Commit with proper attribution
git add skills/building-artifacts/SKILL.md skills/ANTHROPIC_SKILLS_NOTICE
git commit -m "Update building-artifacts skill with [description]

Modified Apache 2.0 licensed skill from Anthropic example-skills.
See skills/ANTHROPIC_SKILLS_NOTICE for modification details.
"
git push
```

### Version Management

```bash
# Update plugin version in manifest
vim .claude-plugin/plugin.json
# Change "version" field

# Update marketplace version
cd ..
vim .claude-plugin/marketplace.json
# Change "version" field for claude-context-orchestrator entry

# Update CHANGELOG
vim CHANGELOG.md
# Add new version entry

# Commit version bump
git add .claude-plugin/plugin.json ../.claude-plugin/marketplace.json CHANGELOG.md
git commit -m "Bump version to X.Y.Z"
git tag vX.Y.Z
git push && git push --tags
```

## Development Workflows

### Working with Skills

**Creating a new skill**:
```bash
mkdir -p skills/my-skill
cat > skills/my-skill/SKILL.md << 'EOF'
---
name: My Skill Name
description: What it does and when to use it (include trigger keywords)
---

# My Skill Name

[Instructions for Claude]
EOF
```

**Testing a skill**:
Ask Claude a relevant question that matches the skill's description trigger terms.

**Updating a skill**:
Edit the `SKILL.md` file directly. No restart needed—skills reload automatically.

### Working with Legacy Snippets

**Using the CLI directly**:
```bash
# List all snippets
python3 scripts/snippets_cli.py --config scripts/config.json list --show-stats

# Create a snippet
python3 scripts/snippets_cli.py --config scripts/config.json create my-snippet \
  --pattern "pattern" --content "content"

# Update a snippet
python3 scripts/snippets_cli.py --config scripts/config.json update my-snippet \
  --pattern "new-pattern"

# Delete a snippet
python3 scripts/snippets_cli.py --config scripts/config.json delete my-snippet --backup
```

**Config file locations**:
- Base: `scripts/config.json`
- Local: `scripts/config.local.json`
- Use `--use-base-config` flag to modify base config instead of local

### Testing the Plugin

**Install locally for testing**:
```bash
# From marketplace root directory
/plugin marketplace add file:///Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace

# Install plugin
/plugin install claude-code-skills-manager@warren-claude-code-plugin-marketplace

# Verify installation
/help | grep -A5 "claude-code-skills-manager"
```

## Important Patterns

### Template Pattern for Complex Skills

Skills that need external files (templates, examples) use this pattern:

```
skills/
└── my-skill/
    ├── SKILL.md                    # Main skill with instructions
    └── reference/
        ├── template.html           # Reusable template
        └── examples.md             # Usage patterns
```

**In SKILL.md**, reference files with `${CLAUDE_PLUGIN_ROOT}`:
```markdown
**Template**: `${CLAUDE_PLUGIN_ROOT}/skills/my-skill/reference/template.html`
```

### Verification Hash System

Snippets use verification hashes to track content integrity:
```markdown
**VERIFICATION_HASH:** `9f2e4a8c6d1b5730`
```

Hashes are auto-generated and updated by `snippets_cli.py` when content changes.

### Announcement System

Snippets can announce themselves when active:
```yaml
---
SNIPPET_NAME: my-snippet
ANNOUNCE_USAGE: true
---
```

The injector adds a meta-instruction that tells Claude to announce active contexts at the start of responses.

## Key Files

- **Plugin manifest**: `.claude-plugin/plugin.json` - Defines skills directory
- **Marketplace manifest**: `../.claude-plugin/marketplace.json` - Lists all plugins
- **Migration guide**: `MIGRATION_GUIDE.md` - v1→v2 upgrade instructions
- **Documentation**: `docs/` - Comprehensive guides and references

## Version Migration (v1.0 → v2.0)

**v1.0 (Snippets)**:
- Hook-based injection with regex patterns
- Always-on context loading
- CLI management tools

**v2.0 (Skills)**:
- Model-invoked via descriptions
- Progressive disclosure
- Native Claude Code integration

**Both systems coexist** for backward compatibility. The hook system still works for users who need it.

## Best Practices

1. **Skills over snippets** - Prefer Agent Skills for new functionality
2. **Use `${CLAUDE_PLUGIN_ROOT}`** - Never hardcode absolute paths
3. **Local config for personal overrides** - Don't commit `config.local.json`
4. **Test before committing** - Install locally and verify functionality
5. **Follow template pattern** - Separate instructions from reusable templates
6. **Write clear descriptions** - Include what, when, and trigger keywords

## Common Tasks

**Add a new meta-skill to the plugin**:
1. Create `skills/new-skill/SKILL.md` with YAML frontmatter
2. Write description with clear trigger terms
3. Test with relevant queries
4. Update version in `.claude-plugin/plugin.json`

**Update existing documentation**:
1. Edit `CLAUDE.md` in the parent directory
2. Update the modification log at the bottom
3. Commit with descriptive message

**Add a new plugin to the marketplace**:
1. Create plugin directory with `.claude-plugin/plugin.json`
2. Add entry to `../.claude-plugin/marketplace.json`
3. Update marketplace version
4. Test local installation

## Resources

- [Official Skills Documentation](https://docs.claude.com/en/docs/claude-code/skills.md)
- [Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices.md)
- [Plugin Reference](https://docs.claude.com/en/docs/claude-code/plugins-reference.md)
- [Hooks Reference](https://docs.claude.com/en/docs/claude-code/hooks.md)
