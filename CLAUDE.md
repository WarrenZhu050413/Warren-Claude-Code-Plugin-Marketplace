# Claude Code Plugin Development Guide

**VERIFICATION_HASH:** `9f2e4a8c6d1b5730`

A concise guide to plugin development for Claude Code, focused on structure and best practices.

---

## Quick Reference

### Essential Documentation
- **[Plugin Reference](https://docs.claude.com/en/docs/claude-code/plugins-reference.md)** - Complete plugin structure
- **[Plugin Marketplaces](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces.md)** - Marketplace setup
- **[Plugins Overview](https://docs.claude.com/en/docs/claude-code/plugins.md)** - How plugins work
- **[Hooks Reference](https://docs.claude.com/en/docs/claude-code/hooks.md)** - Hook configuration and events

---

## Plugin Structure

### Minimal Plugin

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # REQUIRED: Plugin manifest
├── commands/                # Optional: Slash commands
│   └── my-command.md
├── snippets/                # Optional: Context snippets
│   └── my-snippet.md
└── README.md                # Recommended
```

### Plugin Manifest (`.claude-plugin/plugin.json`)

```json
{
  "name": "my-plugin",           // REQUIRED: kebab-case
  "version": "1.0.0",            // REQUIRED: semver
  "description": "Brief desc",   // REQUIRED
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "commands": "./commands",      // Optional: relative path
  "snippets": "./snippets"       // Optional: relative path
}
```

**Key Rules:**
- All paths MUST be relative: `./commands`, `./snippets`
- Never use absolute paths
- Plugin name MUST be kebab-case
- Version MUST follow semver (X.Y.Z)

---

## Marketplace Structure

### Marketplace Manifest (`.claude-plugin/marketplace.json`)

```json
{
  "name": "marketplace-name",
  "owner": {
    "name": "Owner Name",
    "email": "owner@example.com"
  },
  "plugins": [
    {
      "name": "plugin-name",
      "version": "1.0.0",
      "description": "Brief description",
      "source": "./plugin-directory"
    }
  ]
}
```

**Installation:**
```bash
# Add marketplace
/plugin marketplace add username/repo

# Install plugin
/plugin install plugin-name@marketplace-name
```

---

## Command Files

### Structure

```markdown
---
description: Brief description (shows in /help)
---

# Command Title

## Arguments

Input: `$ARGUMENTS`

## Instructions

1. **Parse arguments**:
   - Check for flags: `-f`, `--force`
   - Extract main input from `$ARGUMENTS`
   - Validate input

2. **Ask for confirmation** (unless `-f` or `--force`):
   - Show what will change
   - Wait for yes/no
   - Proceed only if yes

3. **Execute action**:
   - Perform operation
   - Handle errors gracefully
   - Confirm completion

## Example Usage

```
/my-command example input
/my-command --force another example
```

## Notes

- Important notes here
```

**Key Points:**
- **MUST have YAML frontmatter** with `description`
- **ALWAYS use `$ARGUMENTS`** for user input
- **Ask for confirmation** for create/update/delete (unless forced)
- **No confirmation** for read-only operations

---

## Snippet Files

### Structure

Snippets provide contextual instructions to Claude through the `UserPromptSubmit` hook. They follow a similar structure to commands but serve as continuous context rather than one-time actions.

```markdown
---
description: Brief description of what this snippet provides
SNIPPET_NAME: unique-identifier
ANNOUNCE_USAGE: true
---

# Snippet Title

**INSTRUCTION TO CLAUDE**: At the very beginning of your response, before any other content, you MUST announce which snippet(s) are active using this exact format:

📎 **Active Context**: snippet-name

If multiple snippets are detected, combine them:

📎 **Active Contexts**: snippet1, snippet2, snippet3

---

**VERIFICATION_HASH:** `unique-hash-here`

[Main instructions for Claude...]

## Section 1: Core Instructions

[Detailed instructions...]

## Section 2: Additional Guidance

[More instructions...]
```

**Key Points:**
- **YAML frontmatter** with `description`, `SNIPPET_NAME`, and `ANNOUNCE_USAGE`
- **Announcement block** at the top (tells Claude to announce active contexts)
- **Verification hash** for content integrity tracking
- **Clear section structure** for organization
- **Instructions are directives** to Claude, not conversational

---

## Template Pattern for Complex Snippets

For snippets that require external files (templates, examples), use this pattern:

### Directory Structure

```
my-plugin/
├── snippets/
│   └── my-snippet.md          # Main snippet with instructions
└── templates/
    └── my-template/
        ├── base-template.html  # Base template file
        └── examples.md         # Usage examples
```

### Template-Based Snippet Structure

```markdown
---
description: Snippet description
SNIPPET_NAME: my-snippet
ANNOUNCE_USAGE: true
---

# My Snippet Title

**INSTRUCTION TO CLAUDE**: Announcement block...

---

**VERIFICATION_HASH:** `hash-here`

## Primary Purpose

Main instructions for Claude...

## File Handling Instructions

1. **ALWAYS** create output directory: `mkdir -p output/`
2. Write to: `output/{description}.ext`
3. Open file after writing

## Template System

**Base Template:** `${CLAUDE_PLUGIN_ROOT}/templates/my-template/base-template.html`
- Contains all structure and styling
- Ready to use - just add content
- Includes feature X, Y, Z

**Examples & Reference:** `${CLAUDE_PLUGIN_ROOT}/templates/my-template/examples.md`
- Complete component examples
- Usage patterns
- Best practices

**Workflow:**
1. Read the base template: `${CLAUDE_PLUGIN_ROOT}/templates/my-template/base-template.html`
2. Replace `{{PLACEHOLDER}}` with actual content
3. Add custom content in designated section
4. Reference examples.md for patterns if needed

## Component Selection Guide

Quick reference table for choosing the right patterns:

| Use Case | Pattern | When to Use |
|----------|---------|-------------|
| Feature A | Pattern 1 | Scenario 1 |
| Feature B | Pattern 2 | Scenario 2 |

## Design Principles

### Principle 1: Title
- **Rule 1**: Description
- **Rule 2**: Description

### Principle 2: Title
- **Rule 1**: Description
- **Rule 2**: Description

## Common Patterns

### Pattern 1

\```language
# Example code
\```

### Pattern 2

\```language
# Example code
\```

## Best Practices

1. **Practice 1**: Explanation
2. **Practice 2**: Explanation
```

### Real-World Example: HTML Output Snippet

The `claude-code-snippets-plugin/snippets/HTML.md` demonstrates this pattern:

**Structure:**
```
claude-code-snippets-plugin/
├── snippets/
│   └── HTML.md                    # Main snippet with instructions
└── templates/
    └── html/
        ├── base-template.html     # Complete HTML template
        └── examples.md            # Component examples
```

**Key Features:**
- **Base template** contains all CSS, JavaScript, and HTML structure
- **Placeholders** like `{{TITLE}}` and `<!-- CONTENT GOES HERE -->`
- **Examples file** shows complete usage patterns
- **Workflow instructions** tell Claude to read template → replace placeholders → add content

**Benefits:**
1. **Separation of concerns** - Instructions separate from templates
2. **Reusability** - Templates can be used independently
3. **Maintainability** - Update template without changing snippet instructions
4. **Discoverability** - Examples file serves as reference documentation

### Template Pattern Best Practices

**1. Use `${CLAUDE_PLUGIN_ROOT}` for paths:**

✅ **Good:**
```markdown
**Base Template:** `${CLAUDE_PLUGIN_ROOT}/templates/html/base-template.html`
```

❌ **Bad:**
```markdown
**Base Template:** `./templates/html/base-template.html`
```

**2. Provide clear workflow steps:**

```markdown
**Workflow:**
1. Read the base template: `${CLAUDE_PLUGIN_ROOT}/templates/...`
2. Replace `{{PLACEHOLDER}}` with actual content
3. Add content in designated section
4. Reference examples.md for patterns
```

**3. Include quick reference tables:**

Component selection guides help Claude choose the right patterns quickly.

**4. Keep snippet focused on instructions:**

The snippet file should contain instructions and references, not embed large templates inline.

**5. Document placeholder format:**

Clearly specify what placeholders exist and how to replace them.

---

## Hooks

**IMPORTANT:** When writing or configuring hooks, ALWAYS consult the **[Hooks Reference](https://docs.claude.com/en/docs/claude-code/hooks.md)** documentation for the correct structure and format.

### Hook Configuration (`hooks/hooks.json`)

Hooks can be defined in either `hooks/hooks.json` or inline in `plugin.json`.

**Correct Structure:**

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "pattern",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/my-script.py"
          }
        ]
      }
    ]
  }
}
```

**Common Events:**
- `UserPromptSubmit` - Before user prompt is processed
- `PreToolUse` - Before tool execution
- `PostToolUse` - After tool execution
- `Notification` - System notifications
- `SessionStart` / `SessionEnd` - Session lifecycle

**Key Rules:**
- ALWAYS use `${CLAUDE_PLUGIN_ROOT}` for script paths (not relative paths like `./`)
- Events are organized by event name as keys
- Each event contains an array of matchers
- `matcher` field is required (use `".*"` to match all)
- Hook type can be `command`, `validation`, or `notification`

**Example - User Prompt Hook:**

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/snippet_injector.py"
          }
        ]
      }
    ]
  }
}
```

**Plugin Manifest Reference:**

In `plugin.json`, add:
```json
{
  "hooks": "./hooks/hooks.json"
}
```

---

## Best Practices

### 1. Always Parse `$ARGUMENTS`

✅ **Good:**
```markdown
1. **Parse arguments**:
   - Extract snippet type from `$ARGUMENTS`
   - Check for `-f` or `--force` flag
```

❌ **Bad:**
```markdown
1. **Do the thing**
   - Just do it
```

### 2. Confirmation Pattern

**For destructive operations (create/update/delete):**

```markdown
**Ask for confirmation** (UNLESS `-f` or `--force`):
- Show user what will change
- Ask: "Proceed? (yes/no)"
- If no, abort
- If yes, proceed
```

**For read operations:**
- No confirmation needed

### 3. Backup Before Destructive Ops

```markdown
**Create backup**:
- Copy to `[filename].backup.[timestamp]`
- Inform user of backup location
```

### 4. Clear Error Messages

✅ **Good:**
```
❌ Error: File not found: ~/.claude/snippets/mail.md

Suggestion: Run `/create-snippet mail` to create it.
```

❌ **Bad:**
```
Error: File not found
```

### 5. Helpful Feedback

```markdown
✅ Created: ~/.claude/snippets/mail.md
✅ Backup: ~/.claude/snippets/mail.md.backup.20251010_123456

Next steps:
1. Restart Claude Code
2. Test with `/read-snippets`
```

---

## Common Gotchas

### 1. Absolute Paths

❌ **Wrong:**
```json
{
  "commands": "/Users/me/.claude/plugins/my-plugin/commands"
}
```

✅ **Right:**
```json
{
  "commands": "./commands"
}
```

### 2. Missing Frontmatter

❌ **Wrong:**
```markdown
# My Command
...
```

✅ **Right:**
```markdown
---
description: Brief description
---

# My Command
...
```

### 3. Not Parsing `$ARGUMENTS`

Commands MUST parse `$ARGUMENTS` - it contains everything after the command name.

### 4. No Confirmation for Destructive Ops

ALWAYS ask for confirmation before create/update/delete (unless `-f`/`--force`).

### 5. Plugin Name Mismatch

Directory name and manifest `name` should match:
```
my-plugin/                           # Directory
  .claude-plugin/
    plugin.json: { "name": "my-plugin" }  # Must match
```

### 6. Forgetting `.gitignore`

```gitignore
.env
*.backup.*
.DS_Store
node_modules/
```

### 7. Hardcoded Credentials

Never commit credentials. Use `.env` files (and gitignore them).

### 8. Not Restarting Claude Code

After editing plugins, MUST restart Claude Code or reload plugin to see changes.

---

## Testing Before Installation

### 1. Create Local Test Marketplace

```bash
mkdir -p test-marketplace/.claude-plugin

cat > test-marketplace/.claude-plugin/marketplace.json <<EOF
{
  "name": "test-marketplace",
  "owner": {
    "name": "Test",
    "email": "test@example.com"
  },
  "plugins": [
    {
      "name": "my-plugin",
      "version": "1.0.0",
      "description": "Test",
      "source": "../my-plugin"
    }
  ]
}
EOF
```

### 2. Install Locally

```bash
# Add test marketplace (use absolute path)
/plugin marketplace add file:///absolute/path/to/test-marketplace

# Install plugin
/plugin install my-plugin@test-marketplace

# Test command
/my-command test input

# Verify in help
/help | grep my-command
```

### 3. Pre-Release Checklist

- [ ] Plugin manifest is valid JSON
- [ ] All paths are relative
- [ ] Commands have frontmatter
- [ ] `$ARGUMENTS` parsing works
- [ ] Confirmation prompts work (unless forced)
- [ ] Error messages are helpful
- [ ] No hardcoded paths or credentials
- [ ] `.gitignore` configured
- [ ] README is accurate
- [ ] Version number updated

---

## Publishing to Marketplace

### 1. Add Plugin Entry

In marketplace's `.claude-plugin/marketplace.json`:

```json
{
  "plugins": [
    {
      "name": "my-plugin",
      "version": "1.0.0",
      "description": "Brief description",
      "source": "./my-plugin"
    }
  ]
}
```

### 2. Users Install Via

```bash
/plugin marketplace add username/marketplace-repo
/plugin install my-plugin@marketplace-name
```

### 3. Document in README

```markdown
## Installation

1. Add marketplace:
   ```bash
   /plugin marketplace add username/marketplace-repo
   ```

2. Install plugin:
   ```bash
   /plugin install my-plugin@marketplace-name
   ```

3. Verify:
   ```bash
   /help
   ```
```

---

## File Naming Conventions

**Commands:**
- Use kebab-case: `create-snippet.md`, `update-config.md`
- Be descriptive: `setup-oauth.md` not `setup.md`

**Snippets:**
- Use lowercase: `mail.md`, `calendar.md`
- Keep short and memorable

---

## Troubleshooting

**Plugin not loading:**
- Check manifest exists at `.claude-plugin/plugin.json`
- Validate JSON (use jsonlint.com)
- Ensure paths are relative
- Restart Claude Code

**Commands not appearing:**
- Check YAML frontmatter exists
- Verify `commands` path in manifest
- Files must end in `.md`
- Run `/help` to verify

**Changes not taking effect:**
- Restart Claude Code after editing plugins

---

## Resources

- [Plugin Reference](https://docs.claude.com/en/docs/claude-code/plugins-reference.md)
- [Plugin Marketplaces](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces.md)
- [Plugins Overview](https://docs.claude.com/en/docs/claude-code/plugins.md)
- [Hooks Reference](https://docs.claude.com/en/docs/claude-code/hooks.md)
- [MCP Specification](https://modelcontextprotocol.io)

**Examples in this marketplace:**
- `claude-code-snippets-plugin` - Snippet injection system
- `gmail-gcal-mcp-plugin` - Gmail & Calendar automation

---

## Modification Log

This section tracks modifications to this guide and the marketplace.

### 2025-10-16
- **Added**: `skills-warren` plugin to marketplace
  - Created new plugin for custom Apache-licensed skills
  - Includes Apache 2.0 compliance snippet
  - Prepared for adaptation of Anthropic example-skills:
    - mcp-builder
    - skill-creator
    - theme-factory
    - webapp-testing
    - artifacts-builder
  - Full LICENSE and NOTICE files included
  - Plugin structure: `.claude-plugin/plugin.json`, `snippets/`, `skills/`

### 2025-10-12
- Initial guide created
- Documented plugin development best practices
- Added template patterns for complex snippets
- Included hooks reference and examples

---

**Last Updated:** 2025-10-16
**Author:** Fucheng Warren Zhu
