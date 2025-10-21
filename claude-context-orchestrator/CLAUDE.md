# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Plugin Name**: `claude-context-orchestrator` (formerly `claude-code-skills-manager`, originally `claude-code-snippets-plugin`)
**Version**: 3.0.0
**Type**: Claude Code plugin with hybrid context management (Agent Skills + deterministic snippets)

This plugin orchestrates two complementary context injection systems:

1. **Agent Skills** - Model-invoked capabilities including:
   - Custom meta-skills for skill/snippet management
   - Anthropic example-skills (building-artifacts, building-mcp, testing-webapps, theming-artifacts)
   - Warren's custom skills (using-codex, using-claude, searching-deeply, making-clearer)

2. **Deterministic Snippets** - Hook-based pattern matching for reliable, always-on context injection via UserPromptSubmit hook

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

**Snippet Injection Hook** (`hooks/hooks.json`):
- Listens to `UserPromptSubmit` events
- Matches patterns against user prompts using regex
- Injects snippet content via `additionalContext`
- Supports multi-file snippets with custom separators

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
