---
name: managing-snippets
description: Comprehensive CRUD operations for managing Claude Code snippets - creating new snippets with regex patterns, viewing existing snippet configurations, updating snippet patterns or content, and deleting snippets with backup. Use this skill when users want to create, read, update, delete, or manage snippet configurations in their Claude Code environment.
---

# Managing Snippets

## Purpose

This skill provides comprehensive snippet management through four core operations: Create, Read, Update, and Delete. Snippets are context injection files that automatically load when their regex patterns match user messages, providing relevant documentation or instructions to Claude.

## When to Use

Use this skill when the user wants to:
- **Create** a new snippet with custom patterns and content
- **View/List** existing snippets and their configurations
- **Update** snippet patterns, content, or settings
- **Delete** or remove snippets from the system
- **Manage** snippet configurations and understand snippet behavior

## Available Operations

### Creating Snippets (`/create-snippet`)

**Reference**: `skills/managing-snippets/creating.md` (symlinked from `commands/create-snippet.md`)

Use this operation to create new snippet files from scratch. The create operation:
- Guides users through an interactive setup process
- Validates and formats regex patterns according to protocol standards
- Supports both inline content and file-based content sources
- Prepends Agent Skills YAML frontmatter to all snippets
- Shows comprehensive preview before creation
- Creates verification test suite after snippet is created
- Requires explicit user approval before any changes

**Common use cases**:
- "Create a docker snippet for containerization context"
- "Add a kubernetes snippet using my existing k8s.md file"
- "Setup a snippet that triggers on AWS or amazon web services"

**Key features**:
- Natural language input parsing (handles imperative statements, questions, conversational input)
- Intelligent pattern formatting (converts user input to proper regex)
- Mandatory preview and approval gate
- Automatic YAML frontmatter generation
- Post-creation testing and verification
- No-space pattern enforcement (`[-_]?` instead of `\s`)

### Reading Snippets (`/read-snippets`)

**Reference**: `skills/managing-snippets/reading.md` (symlinked from `commands/read-snippets.md`)

Use this operation to inspect existing snippets and their configurations. The read operation:
- Lists all configured snippets with summary statistics
- Shows detailed view of specific snippets (name, pattern, content)
- Displays pattern alternatives and match conditions
- Provides file size and status information
- Suggests quick actions (update, delete, test)

**Common use cases**:
- "Show me all my snippets"
- "What snippets are enabled right now?"
- "Display the content of the docker snippet"
- "List snippet patterns and their triggers"

**Key features**:
- Summary view (all snippets) or detailed view (specific snippet)
- Shows enabled/disabled status with icons (✓/✗)
- Lists pattern alternatives with counts
- Displays full snippet content when viewing specific snippet
- Provides actionable suggestions for next steps

### Updating Snippets (`/update-snippet`)

**Reference**: `skills/managing-snippets/updating.md` (symlinked from `commands/update-snippet.md`)

Use this operation to modify existing snippet configurations. The update operation:
- Shows current state before making any changes
- Supports updating patterns, content, enabled status, or names
- Can infer changes from conversation context if not explicitly provided
- Validates patterns against comprehensive Regex Protocol Guide
- Displays detailed preview of all proposed changes
- Tests snippet after update to verify it still works
- Requires explicit approval before applying changes

**Common use cases**:
- "Update docker snippet to include 'compose' keyword"
- "Disable the mail snippet temporarily"
- "Rename gcal snippet to google-calendar"
- "Update kubernetes snippet with new content from ~/k8s-v2.md"
- "update-snippet POST" (infers changes from conversation)

**Key features**:
- **Context-aware**: Can analyze recent conversation to infer necessary changes
- **Protocol validation**: Checks patterns against comprehensive regex standards
- **Multi-aspect updates**: Change pattern, content, status, or name in one operation
- **Comprehensive preview**: Shows before/after for all changes
- **Safety checks**: Validation against protocol, duplicate detection, conflict warnings
- **Transparent sourcing**: Indicates if changes were inferred vs. explicitly provided

**Regex Protocol Standards** (enforced by CLI validation):

**STANDARD FORMAT**: `\b(PATTERN)[.,;:]?\b`

All patterns MUST follow this format:
1. **Word boundaries**: `\b` at start and end
2. **Parentheses**: Pattern wrapped in `()`
3. **ALL CAPS**: Pattern content must be uppercase (A-Z, 0-9)
4. **Multi-word separators**: Use `_`, `-`, or no separator (never spaces)
5. **Optional punctuation**: `[.,;:]?` at the end
6. **Alternation**: Use `|` for multiple patterns

**CLI Validation Rules**:
- ✅ Pattern must match: `\b(PATTERN)[.,;:]?\b`
- ✅ Pattern content must be ALL CAPS
- ✅ No spaces allowed (use `_`, `-`, or nothing)
- ✅ Cannot mix `_` and `-` in same pattern
- ❌ Lowercase letters will be rejected
- ❌ Missing parentheses will be rejected
- ❌ Missing `[.,;:]?` will be rejected

**Valid Examples**:
- `\b(BUILD_ARTIFACT)[.,;:]?\b` - with underscore
- `\b(BUILD-ARTIFACT)[.,;:]?\b` - with hyphen
- `\b(BUILDARTIFACT)[.,;:]?\b` - no separator
- `\b(DOCKER|CONTAINER)[.,;:]?\b` - alternation

**Invalid Examples**:
- `\bBUILD_ARTIFACT\b` - missing parentheses and punctuation
- `\b(build_artifact)[.,;:]?\b` - not ALL CAPS
- `\b(BUILD ARTIFACT)[.,;:]?\b` - contains space
- `\b(BUILD_ART-IFACT)[.,;:]?\b` - mixed separators

### Deleting Snippets (`/delete-snippet`)

**Reference**: `skills/managing-snippets/deleting.md` (symlinked from `commands/delete-snippet.md`)

Use this operation to safely remove snippets from the system. The delete operation:
- Shows complete details of snippet to be deleted
- Creates timestamped backup before deletion
- Requires explicit confirmation (unless forced)
- Provides restore instructions after deletion
- Verifies removal and shows remaining snippets

**Common use cases**:
- "Delete the old terraform snippet"
- "Remove mail snippet with backup"
- "Clean up unused snippets"

**Key features**:
- **Automatic backups**: Creates timestamped backup directory by default
- **Preview before deletion**: Shows what will be deleted
- **Detailed backup info**: Location, timestamp format, restore instructions
- **Verification**: Lists remaining snippets after deletion
- **Safety gates**: Requires approval unless `--force` flag used

**Backup format**:
- Directory: `backups/YYYYMMDD_HHMMSS_{snippet_name}/`
- Contains: `{snippet_name}.md` + `config_backup.json`
- Restore instructions provided after deletion

## Workflow Examples

### Example 1: Creating a New Context Snippet

**Scenario**: User wants Docker context loaded when discussing containerization.

```
User: "Create a docker snippet for containerization topics"

Claude (using /create-snippet):
1. Parses intent: name=docker, context=containerization
2. Infers pattern: \b(docker|container|dockerfile)\b
3. Prompts for content source (template, file, or inline)
4. Shows comprehensive preview with pattern alternatives
5. Requests approval
6. Creates snippet with YAML frontmatter
7. Runs verification tests
8. Displays final snippet content
```

### Example 2: Discovering and Updating a Snippet

**Scenario**: User notices a snippet didn't trigger when it should have.

```
User: "Why didn't my kubernetes snippet load?"

Claude (using /read-snippets):
1. Lists all snippets to identify the issue
2. Shows kubernetes snippet pattern: \b(kubernetes|k8s)\b

User: "Add kubectl to the pattern"

Claude (using /update-snippet):
1. Shows current pattern
2. Proposes new pattern: \b(kubernetes|k8s|kubectl)\b
3. Validates against Regex Protocol
4. Shows preview with before/after
5. Requests approval
6. Updates snippet
7. Tests new pattern matches "kubectl"
8. Displays updated snippet content
```

### Example 3: Context-Aware Update (No Explicit Instructions)

**Scenario**: Snippet was just used but didn't match all expected keywords.

```
User: "I mentioned 'POST' but the snippet didn't load"
[conversation about POST command functionality]

User: "update-snippet POST"

Claude (using /update-snippet with conversation analysis):
1. Analyzes recent conversation context
2. Identifies pattern mismatch: "POST" mentioned but didn't match
3. Infers necessary changes: Expand pattern alternatives
4. Proposes: "Based on our session where POST didn't match, I propose updating POST snippet to include additional keyword variations"
5. Shows current vs. proposed pattern
6. Requests approval
7. Applies updates and tests
```

### Example 4: Cleaning Up Old Snippets

**Scenario**: User wants to remove outdated context.

```
User: "Delete the old terraform snippet"

Claude (using /delete-snippet):
1. Shows snippet details (pattern, file, size, status)
2. Displays deletion preview with backup location
3. Requests confirmation
4. Creates backup: backups/20251021_143022_terraform/
5. Deletes snippet and config entry
6. Shows restore instructions
7. Lists remaining snippets for verification
```

## Best Practices

### Creating Snippets

1. **Use descriptive names**: Choose clear, memorable snippet names (e.g., `docker`, `kubernetes`, not `snip1`)
2. **Follow naming conventions**: Use lowercase for natural triggers, UPPERCASE for explicit commands
3. **Test patterns thoroughly**: Verify pattern matches expected keywords before creation
4. **Review previews carefully**: Always check the preview before approving creation
5. **Leverage templates**: Use existing snippet files as templates when appropriate
6. **Include descriptions**: YAML frontmatter descriptions help with discovery

### Reading Snippets

1. **Regular audits**: Periodically review all snippets with `/read-snippets` (no args)
2. **Check enabled status**: Verify which snippets are active vs. disabled
3. **Review patterns**: Ensure patterns still match your intended triggers
4. **Content verification**: View full snippet content to check for outdated information

### Updating Snippets

1. **Always backup**: While updates don't auto-backup, manually backup before major changes
2. **Validate patterns**: Check that new patterns follow Regex Protocol Guide standards
3. **Test incrementally**: Update one aspect at a time (pattern OR content, not both)
4. **Review conversation context**: Let Claude analyze recent sessions for smart updates
5. **Verify protocol compliance**:
   - Use `\b...[.,;:]?\b` structure
   - Avoid `\s` in patterns (use `[-_]?` instead)
   - Keep alternative count reasonable (< 8)

### Deleting Snippets

1. **Always backup**: Accept default backup creation unless you're absolutely sure
2. **Review before deletion**: Use "Details" option to see full content before confirming
3. **Keep backups organized**: Periodically clean old backups from `backups/` directory
4. **Document restore process**: Save restore instructions if you might need to undo
5. **Verify afterward**: Check remaining snippets list to confirm deletion

### General Management

1. **One operation at a time**: Don't chain create/update/delete without verification
2. **Use local config for personal snippets**: Default behavior uses `config.local.json`
3. **Use base config for shared snippets**: Add `--use-base-config` for team-wide snippets
4. **Test after changes**: Verify snippets load correctly after create/update
5. **Document your patterns**: Keep notes on why certain patterns are structured a certain way
6. **Follow gerund naming**: Use present continuous form when applicable (e.g., "searching", "creating")

## Configuration Targets

All operations support two configuration targets:

- **Local config** (default): `config.local.json` - Personal, user-specific snippets
- **Base config** (opt-in): `config.json` - Global, shared snippets (use `--use-base-config`)

**When to use which**:
- Personal context (email templates, private notes): Use local config (default)
- Team conventions, shared documentation: Use base config (`--use-base-config`)
- Testing new snippets: Use local config first, promote to base later

## Common Patterns

### Iterative Development

```
1. Create initial snippet with basic pattern
   /create-snippet docker --pattern "docker"

2. Test in conversation: "Help me with docker"

3. Update based on usage: "Add compose and container to docker snippet"
   /update-snippet docker  # Claude infers from conversation

4. Verify changes: /read-snippets docker

5. Refine further if needed
```

### Bulk Management

```
1. Audit all snippets: /read-snippets

2. Identify outdated/unused snippets

3. Update patterns to protocol standard:
   /update-snippet <name>  # Claude checks protocol compliance

4. Remove unused: /delete-snippet <name> --backup

5. Verify final state: /read-snippets
```

### Troubleshooting Snippet Issues

```
1. Snippet not loading:
   - Read snippet: /read-snippets <name>
   - Check enabled status
   - Verify pattern matches your keyword
   - Update pattern if needed: /update-snippet <name>

2. Too many snippets loading:
   - Audit patterns: /read-snippets
   - Look for overlapping alternatives
   - Narrow patterns or disable conflicting snippets

3. Pattern not matching:
   - Check Regex Protocol compliance
   - Test with different keyword variations
   - Update to include missing alternatives
```

## Technical Notes

### Snippet File Structure

All snippets created/updated use Agent Skills format:

```markdown
---
name: snippet-identifier
description: When/why to use this snippet
---

[Snippet content follows...]
```

### Pattern Format Standards (CLI-Enforced)

**STANDARD FORMAT**: `\b(PATTERN)[.,;:]?\b`

**Requirements** (enforced by `snippets_cli.py` validation):

1. **Structure**:
   - Start: `\b(`
   - Pattern: ALL CAPS (A-Z, 0-9, `_`, `-`, `|`)
   - End: `)[.,;:]?\b`

2. **Pattern Content Rules**:
   - ALL CAPS only (no lowercase)
   - Multi-word: Use `_` or `-` (not both in same pattern)
   - Alternation: Separate with `|`
   - No spaces allowed (forbidden: `\s`, `\s*`, `\s+`)

3. **Examples**:
   ```regex
   # Valid patterns
   \b(DOCKER)[.,;:]?\b                    # Single word
   \b(BUILD_ARTIFACT)[.,;:]?\b            # Underscore separator
   \b(BUILD-ARTIFACT)[.,;:]?\b            # Hyphen separator
   \b(DOCKER|CONTAINER|KUBE)[.,;:]?\b    # Alternation

   # Invalid patterns (CLI will reject)
   \b(docker)[.,;:]?\b                    # Lowercase
   \b(BUILD ARTIFACT)[.,;:]?\b            # Space
   \b(BUILD_ART-IFACT)[.,;:]?\b          # Mixed separators
   \bDOCKER\b                             # Missing parens and punctuation
   ```

**Pattern Transformation Process**:

When you provide pattern input, Claude transforms to standard format:
1. Extract pattern content: `"build artifact"` → `BUILD_ARTIFACT`
2. Apply ALL CAPS: `build_artifact` → `BUILD_ARTIFACT`
3. Handle multi-word: Use `_` (preferred), `-`, or no separator
4. Add structure: Wrap in `\b(...)` and add `[.,;:]?\b`
5. Result: `\b(BUILD_ARTIFACT)[.,;:]?\b`

**See Regex Protocol Guide in `skills/managing-snippets/updating.md` for comprehensive standards and edge cases.**

### File Locations

- **Snippet files**: `commands/local/{name}.md`
- **Configuration**: `scripts/config.local.json` (personal) or `scripts/config.json` (global)
- **Backups**: `backups/YYYYMMDD_HHMMSS_{name}/`
- **Tests**: `/Users/wz/.claude/tests/shared/{name}_test.sh`

### CLI Invocation

All operations use the underlying `snippets_cli.py`:

```bash
cd /Users/wz/.claude/plugins/.../scripts
python3 snippets_cli.py [--use-base-config] <command> <args>
```

Commands: `create`, `list`, `update`, `delete`

## Integration with Other Skills

This skill works well with:
- **reading-skills**: Use to discover and view Agent Skills
- **creating-skills**: Use to create new Agent Skills (similar to snippets)
- **updating-skills**: Use to modify existing Agent Skills
- **deleting-skills**: Use to remove Agent Skills

## Quick Reference

| Task | Command | Example |
|------|---------|---------|
| Create new snippet | `/create-snippet` | `/create-snippet docker` |
| List all snippets | `/read-snippets` | `/read-snippets` |
| View specific snippet | `/read-snippets <name>` | `/read-snippets docker` |
| Update pattern | `/update-snippet <name>` | `/update-snippet docker add compose` |
| Update from context | `/update-snippet <name>` | `/update-snippet POST` (no args) |
| Rename snippet | `/update-snippet <name> rename to <new>` | `/update-snippet gcal rename to google-calendar` |
| Disable snippet | `/update-snippet <name> --disable` | `/update-snippet mail --disable` |
| Delete snippet | `/delete-snippet <name>` | `/delete-snippet terraform` |

## Important Reminders

- **Always preview before approval**: All operations show what will happen before executing
- **Always test after changes**: Verify snippets work as expected
- **Always backup before deletion**: Accept default backup creation
- **Follow Regex Protocol**: Ensure patterns comply with standards
- **Document your intent**: Use clear descriptions in YAML frontmatter
- **Use local config by default**: Only use `--use-base-config` for shared snippets
