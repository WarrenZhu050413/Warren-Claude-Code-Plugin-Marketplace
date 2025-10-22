---
name: managing-snippets
description: Comprehensive CRUD operations for managing Claude Code snippets - creating new snippets with regex patterns, viewing existing snippet configurations, updating snippet patterns or content, and deleting snippets with backup. Use this skill when users want to create, read, update, delete, or manage snippet configurations in their Claude Code environment.
---

# Managing Snippets

CRUD operations for snippet management. Snippets auto-inject context when regex patterns match user messages.

## Core Operations

### Create (`/create-snippet`)

Creates new snippets with interactive setup, pattern validation, YAML frontmatter, preview, and verification tests.

**Examples**: "Create docker snippet", "Add kubernetes snippet from k8s.md"

**Features**: Natural language parsing, pattern formatting, mandatory approval, post-creation testing

### Read (`/read-snippets`)

Lists/inspects snippets with statistics, patterns, and content.

**Examples**: "Show all snippets", "Display docker snippet"

**Features**: Summary/detailed views, enabled status (✓/✗), pattern alternatives, actionable suggestions

### Update (`/update-snippet`)

Modifies patterns, content, status, or names. Can infer changes from conversation context.

**Examples**: "Update docker snippet to include compose", "Disable mail snippet", "update-snippet POST" (context-aware)

**Features**: Context analysis, protocol validation, multi-aspect updates, before/after preview, safety checks

### Delete (`/delete-snippet`)

Safely removes snippets with timestamped backups and restore instructions.

**Examples**: "Delete terraform snippet"

**Features**: Auto-backup, preview, verification, restore instructions

## Regex Protocol (CLI-Enforced)

**STANDARD FORMAT**: `\b(PATTERN)[.,;:]?\b`

**Rules**:
1. Word boundaries: `\b` at start/end
2. Parentheses: Pattern wrapped in `()`
3. ALL CAPS: Uppercase only (A-Z, 0-9)
4. Multi-word: `_`, `-`, or no separator (never spaces, never mixed)
5. Optional punctuation: `[.,;:]?` at end
6. Alternation: Use `|`

**Valid**:
- `\b(DOCKER)[.,;:]?\b`
- `\b(BUILD_ARTIFACT)[.,;:]?\b`
- `\b(BUILD-ARTIFACT)[.,;:]?\b`
- `\b(DOCKER|CONTAINER|KUBE)[.,;:]?\b`

**Invalid**:
- `\b(docker)[.,;:]?\b` - lowercase
- `\b(BUILD ARTIFACT)[.,;:]?\b` - space
- `\b(BUILD_ART-IFACT)[.,;:]?\b` - mixed separators
- `\bDOCKER\b` - missing parens/punctuation

## Workflow Examples

### Create Docker Snippet
```
User: "Create docker snippet"
1. Parse intent: name=docker
2. Infer pattern: \b(docker|container|dockerfile)\b
3. Prompt for content source
4. Show preview
5. Request approval
6. Create with YAML frontmatter
7. Run verification tests
```

### Update Missing Pattern
```
User: "Why didn't kubernetes snippet load?"
- Read snippets, show pattern: \b(kubernetes|k8s)\b

User: "Add kubectl"
- Show current pattern
- Propose: \b(kubernetes|k8s|kubectl)\b
- Validate, preview, request approval
- Update and test
```

### Context-Aware Update
```
User: "POST didn't trigger the snippet"
[conversation about POST]
User: "update-snippet POST"
- Analyze conversation
- Infer pattern expansion needed
- Propose changes
- Show before/after, request approval
```

### Safe Deletion
```
User: "Delete terraform snippet"
- Show details
- Display backup location: backups/20251021_143022_terraform/
- Request confirmation
- Create backup, delete
- Show restore instructions
```

## Best Practices

**Creating**:
- Use descriptive names (docker, not snip1)
- Test patterns before approval
- Review previews
- Include YAML descriptions

**Reading**:
- Regular audits with `/read-snippets`
- Check enabled status
- Verify patterns match intentions

**Updating**:
- Backup before major changes
- Validate protocol compliance
- Update one aspect at a time
- Use context-aware inference
- Avoid `\s` (use `[-_]?`)
- Keep alternatives < 8

**Deleting**:
- Always backup (default)
- Review before confirming
- Clean old backups periodically
- Verify after deletion

**General**:
- One operation at a time
- Use `config.local.json` (personal) or `config.json` (shared with `--use-base-config`)
- Test after changes
- Document patterns

## Configuration

**Targets**:
- `config.local.json` (default): Personal snippets
- `config.json` (with `--use-base-config`): Shared snippets

**Usage**:
- Personal context → local config
- Team conventions → base config
- Test locally, promote to base later

## Common Patterns

**Iterative Development**:
1. Create with basic pattern
2. Test in conversation
3. Update based on usage
4. Verify changes
5. Refine

**Bulk Management**:
1. Audit: `/read-snippets`
2. Identify outdated
3. Update patterns
4. Delete unused with backup
5. Verify final state

**Troubleshooting**:
- Not loading → check enabled status, pattern match
- Too many loading → check overlapping patterns, disable conflicts
- Pattern not matching → verify protocol compliance, add alternatives

## Technical Details

**File Structure**:
```markdown
---
name: snippet-identifier
description: When/why to use
---
[Content]
```

**Pattern Transformation**:
1. Extract: "build artifact" → BUILD_ARTIFACT
2. Apply ALL CAPS
3. Handle multi-word: `_`, `-`, or nothing
4. Wrap: `\b(BUILD_ARTIFACT)[.,;:]?\b`

**File Locations**:
- Snippets: `commands/local/{name}.md`
- Config: `scripts/config.local.json` or `scripts/config.json`
- Backups: `backups/YYYYMMDD_HHMMSS_{name}/`
- Tests: `/Users/wz/.claude/tests/shared/{name}_test.sh`

**CLI**:
```bash
cd /Users/wz/.claude/plugins/.../scripts
python3 snippets_cli.py [--use-base-config] <command> <args>
```

Commands: `create`, `list`, `update`, `delete`

## Quick Reference

| Task | Command | Example |
|------|---------|---------|
| Create | `/create-snippet` | `/create-snippet docker` |
| List all | `/read-snippets` | `/read-snippets` |
| View one | `/read-snippets <name>` | `/read-snippets docker` |
| Update pattern | `/update-snippet <name>` | `/update-snippet docker add compose` |
| Context update | `/update-snippet <name>` | `/update-snippet POST` |
| Rename | `/update-snippet <name> rename to <new>` | `/update-snippet gcal rename to google-calendar` |
| Disable | `/update-snippet <name> --disable` | `/update-snippet mail --disable` |
| Delete | `/delete-snippet <name>` | `/delete-snippet terraform` |

## Reminders

- Preview before approval
- Test after changes
- Backup before deletion
- Follow Regex Protocol
- Document intent in YAML
- Use local config by default

**See** `skills/managing-snippets/updating.md` for comprehensive Regex Protocol standards and edge cases.
