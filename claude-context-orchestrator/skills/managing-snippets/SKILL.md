---
name: managing-snippets
description: Comprehensive guide for managing Claude Code snippets v2.0 - discovering locations, creating snippets from files, searching by name/pattern/description, and validating configurations. Use this skill when users want to create, search, or manage snippet configurations in their Claude Code environment. Updated for LLM-friendly interface with TTY auto-detection.
---

# Managing Snippets (v2.0)

Snippets auto-inject context when regex patterns match user messages. This skill provides a streamlined workflow for discovering snippet locations, creating snippets, searching configurations, and direct file editing.

## About Snippets

Snippets are pattern-triggered context injection files that enhance Claude's capabilities by automatically loading relevant information when specific keywords appear in user prompts. Think of them as "smart bookmarks" that activate based on what you're working on.

### What Snippets Provide

1. **Automatic context loading** - Inject relevant documentation when keywords match
2. **Workflow enhancement** - Load domain-specific guidance without manual selection
3. **Consistency** - Ensure same context is available across sessions
4. **Efficiency** - Skip manual skill invocation for frequently-used contexts

### When to Use Snippets

- Frequently-used skills that should activate on keywords (e.g., "DOCKER", "TERRAFORM")
- Domain-specific documentation that's needed for specific topics
- Quick-reference material that should load automatically
- Workflow guides tied to specific technologies or tasks

## Anatomy of a Snippet

Every snippet consists of two components:

### 1. config.local.json Entry (Required)

Located at:
```
/Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/scripts/config.local.json
```

**Structure:**
```json
{
  "name": "snippet-identifier",
  "pattern": "\\b(PATTERN)\\b[.,;:!?]?",
  "snippet": ["../snippets/local/category/name/SNIPPET.md"],
  "separator": "\n",
  "enabled": true
}
```

**Key fields:**
- `name`: Unique identifier for the snippet
- `pattern`: Regex pattern that triggers the snippet (MUST follow standard format)
- `snippet`: Array of file paths to inject (relative to config file)
- `separator`: How to join multiple files (usually `"\n"`)
- `enabled`: Whether snippet is active (`true`/`false`)

### 2. SNIPPET.md File (Required)

Located in subdirectory under:
```
/Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/snippets/local/
```

**Structure:**
```markdown
---
name: "Descriptive Name"
description: "When to use this snippet and what it provides"
---

[Content to be injected into context]
```

**Organization:**
Snippets are organized by category:
- `snippets/local/communication/` - Email, reports, writing templates
- `snippets/local/documentation/` - Guides, references, how-tos
- `snippets/local/development/` - Code patterns, debugging workflows
- `snippets/local/productivity/` - Workflow automation, task management
- `snippets/local/output-formats/` - Formatting styles, templates

## CLI v2.0 Overview

The snippets CLI provides four focused commands:

1. **`paths`** - Discover available snippet categories and locations
2. **`create`** - Create snippets from source files with validation
3. **`list` / search** - Search snippets by name, pattern, or description
4. **`validate`** - Verify configuration integrity

**Installation:**
```bash
cd /Users/wz/.claude/plugins/.../scripts
make install  # Global: uv tool install
# OR
make dev      # Local dev: uv run snippets
```

**Auto-detect modes:**
- **TTY (terminal)**: Interactive selection interface
- **Non-TTY (piped)**: JSON output for scripting

## Snippet Management Process

Follow these steps in order to effectively manage snippets.

### Step 1: Discover Available Locations

Before creating a snippet, explore where snippets can be placed using the `paths` command.

**List all categories:**
```bash
snippets paths
# OR with JSON output
snippets paths --output json
```

**Filter by keyword:**
```bash
snippets paths dev        # Shows categories matching "dev"
snippets paths email      # Shows categories matching "email"
```

**Output:**
- Base directory path
- Category names (communication, documentation, development, productivity, output-formats)
- Category descriptions
- Full paths to each category

### Step 2: Planning the Pattern

Determine the regex pattern that will trigger your snippet. Patterns must follow the standard format (see Regex Protocol below).

**Pattern planning:**
1. List all keywords that should trigger the snippet
2. Convert to ALL CAPS (e.g., "docker" → "DOCKER")
3. Handle multi-word patterns (use `_`, `-`, or no separator)
4. Combine alternatives with `|`
5. Apply standard format: `\b(PATTERN)\b[.,;:!?]?`

**Examples:**
- Single keyword: `\b(DOCKER)\b[.,;:!?]?`
- Multiple alternatives: `\b(DOCKER|CONTAINER|DOCKERFILE)\b[.,;:!?]?`
- Multi-word: `\b(BUILD_ARTIFACT)\b[.,;:!?]?`

### Step 3: Creating a Snippet

Create snippets using the `create` command, which validates and registers the snippet automatically.

**Creation workflow:**

1. **Create source SKILL.md file with frontmatter:**
   ```markdown
   ---
   name: "Docker Best Practices"
   description: "Use when working with Docker containers, images, and containerization"
   pattern: "\\b(DOCKER|CONTAINER|DOCKERFILE)\\b[.,;:!?]?"
   ---

   # Docker Best Practices
   [Content here...]
   ```

2. **Run create command:**
   ```bash
   snippets create source.md snippets/local/development/docker/SKILL.md

   # With pattern override
   snippets create source.md snippets/local/development/docker/SKILL.md \
     --pattern "\\b(NEW_PATTERN)\\b[.,;:!?]?"

   # Force overwrite existing
   snippets create source.md snippets/local/development/docker/SKILL.md --force
   ```

**What create does:**
1. ✅ Validates source file exists
2. ✅ Parses YAML frontmatter (name, description, pattern)
3. ✅ Validates pattern format (ALL CAPS, proper structure)
4. ✅ Validates destination is within snippets/local/
5. ✅ Extracts snippet name from destination path
6. ✅ Checks destination doesn't already exist (unless --force)
7. ✅ Creates destination directory
8. ✅ Copies file to destination
9. ✅ Registers in config.local.json automatically

**Helpful error messages:**
- Missing frontmatter → Shows required YAML structure
- Invalid pattern → Explains pattern requirements with examples
- Invalid destination → Shows expected path format
- Missing pattern → Reminds to add --pattern flag or pattern field

**Common mistakes to avoid:**
- ❌ Using lowercase in pattern
- ❌ Missing `\\b` word boundaries (requires double backslash)
- ❌ Destination outside snippets/local/ directory
- ❌ Forgetting YAML frontmatter

### Step 4: Searching and Inspecting Snippets

Search snippets using enhanced multi-level matching (name → pattern → description).

**List all snippets:**
```bash
snippets                    # Default: list all (TTY: interactive, piped: JSON)
snippets list               # Explicit list command
snippets --output json      # Force JSON output
```

**Search by keyword:**
```bash
snippets docker             # Searches name, pattern, and description
snippets kubernetes         # Priority: exact name > name contains > pattern > description
```

**Interactive mode (TTY):**
- Shows formatted list with match indicators
- Navigate with arrow keys
- Select to open in $EDITOR
- ESC to cancel

**Non-interactive mode (piped/JSON):**
- JSON output with match_type and match_priority
- Can pipe to jq for filtering
- Suitable for scripting

**Match priority ranking:**
1. **Exact name match** (priority 1) - `snippets mail` finds snippet named "mail"
2. **Name contains** (priority 2) - `snippets dock` finds "docker"
3. **Pattern content** (priority 3) - `snippets KUBECTL` finds patterns with KUBECTL
4. **Description match** (priority 4) - `snippets "email templates"` finds description matches

**What to check:**
- Enabled status (✓ or ✗)
- Pattern alternatives (does it cover all intended keywords?)
- File paths (do they point to correct locations?)
- Content (read SKILL.md to verify)

**Regular audits:**
- Review snippets monthly
- Disable unused snippets (edit config.local.json)
- Update patterns based on usage
- Remove outdated content

### Step 5: Updating Snippets (Direct File Editing)

**Philosophy:** v2.0 CLI focuses on search and creation. Updates are done by editing files directly.

Modify existing snippets when:
- Pattern doesn't match expected keywords
- Content is outdated
- Need to enable/disable temporarily
- Want to rename for clarity

**Update workflow:**

1. **Find the snippet:**
   ```bash
   snippets docker          # Search to locate snippet
   # OR in interactive mode: select snippet → opens in $EDITOR
   ```

2. **Determine what needs updating:**
   - **Pattern expansion** → Edit config.local.json
   - **Content modification** → Edit SKILL.md directly
   - **Status change** → Edit config.local.json (`enabled` field)
   - **Rename** → Edit config.local.json (`name` field)

3. **For pattern updates:**
   ```bash
   # Edit config.local.json directly
   vim ~/.claude/plugins/.../scripts/config.local.json

   # Modify the pattern field
   {
     "name": "docker",
     "pattern": "\\b(DOCKER|CONTAINER|DOCKERFILE|KUBECTL)\\b[.,;:!?]?",  # Added KUBECTL
     ...
   }
   ```

4. **For content updates:**
   ```bash
   # Edit SKILL.md directly
   vim ~/.claude/plugins/.../snippets/local/development/docker/SKILL.md

   # Update content while maintaining YAML frontmatter
   ```

5. **Validate changes:**
   ```bash
   snippets validate        # Check for errors
   snippets validate --output json  # JSON output for scripting
   ```

6. **Test:**
   - Type trigger keyword in new prompt
   - Confirm content loads correctly

**Context-aware updating:**
If a snippet failed to load during a session, analyze why:
- Did the pattern not match? → Edit config.local.json to expand pattern
- Was it disabled? → Change `"enabled": false` to `true`
- Missing keywords? → Add alternatives to pattern

### Step 6: Deleting Snippets (Direct File Editing)

Remove snippets that are:
- No longer needed
- Superseded by other snippets or skills
- Creating conflicts with other patterns

**Deletion workflow:**

1. **Backup first:**
   ```bash
   # Create backup of config
   cp ~/.claude/plugins/.../scripts/config.local.json \
      ~/.claude/plugins/.../scripts/config.local.json.backup.$(date +%Y%m%d_%H%M%S)

   # Backup snippet file
   cp -r ~/.claude/plugins/.../snippets/local/category/snippet-name \
         ~/.claude/plugins/.../backups/snippet-name_$(date +%Y%m%d_%H%M%S)
   ```

2. **Remove from config.local.json:**
   ```bash
   vim ~/.claude/plugins/.../scripts/config.local.json

   # Delete the entire mapping object
   # Ensure JSON remains valid (check commas)
   ```

3. **Optionally delete SKILL.md:**
   ```bash
   rm -rf ~/.claude/plugins/.../snippets/local/category/snippet-name
   ```

4. **Validate and verify:**
   ```bash
   snippets validate              # Check JSON is valid
   snippets                       # Confirm snippet is gone
   # Type trigger keyword → should not load
   ```

**Restoration:**
If you need to restore:
1. `cp backup/config.local.json.backup.TIMESTAMP config.local.json`
2. `cp -r backup/snippet-name_TIMESTAMP snippets/local/category/snippet-name`
3. `snippets validate` and test trigger keyword

## Regex Protocol (Standard Format)

**CRITICAL:** All snippet patterns MUST follow this format.

### Standard Format

```
\b(PATTERN)\b[.,;:!?]?
```

**Rules:**
1. **Word boundaries:** `\b` at start and end
2. **Parentheses:** Pattern wrapped in `()`
3. **ALL CAPS:** Uppercase only (A-Z, 0-9)
4. **Multi-word:** Use `_`, `-`, or no separator (never spaces)
5. **No mixed separators:** Can't mix `_` and `-` in same pattern
6. **Optional punctuation:** `[.,;:!?]?` at end
7. **Alternation:** Use `|` for multiple keywords

### Why Full Punctuation Matters

Users naturally add punctuation when typing. Excluding punctuation causes mismatches:
- ❌ Pattern `[.,;:]?` does NOT match "ARTIFACT!"
- ✅ Pattern `[.,;:!?]?` matches "ARTIFACT!", "ARTIFACT?", "ARTIFACT."

**Always use the full set:** `[.,;:!?]?`

### Valid Examples

```
\b(DOCKER)\b[.,;:!?]?                      # Single word
\b(DOCKER|CONTAINER|DOCKERFILE)\b[.,;:!?]? # Alternation
\b(BUILD_ARTIFACT)\b[.,;:!?]?              # Underscore separator
\b(BUILD-ARTIFACT)\b[.,;:!?]?              # Hyphen separator
\b(BUILDARTIFACT)\b[.,;:!?]?               # No separator
```

### Invalid Examples

```
\b(docker)\b[.,;:!?]?              # ❌ Lowercase
\b(BUILD ARTIFACT)\b[.,;:!?]?      # ❌ Space separator
\b(BUILD_ART-IFACT)\b[.,;:!?]?     # ❌ Mixed separators
\bDOCKER\b                         # ❌ Missing parens and punctuation
\b(DOCKER)\b[.,;:]?                # ❌ Incomplete punctuation
```

### Pattern Transformation

User input → Standard format:

1. **Convert to ALL CAPS:**
   - "docker" → "DOCKER"
   - "build artifact" → "BUILD_ARTIFACT"

2. **Handle multi-word:**
   - Choose one separator: `_` (preferred), `-`, or none
   - Apply consistently throughout pattern

3. **Handle alternation:**
   - "docker, container, dockerfile" → `(DOCKER|CONTAINER|DOCKERFILE)`

4. **Apply standard format:**
   - Wrap in `\b` boundaries
   - Add parentheses
   - Add `[.,;:!?]?` for punctuation

### JSON Escaping

**IMPORTANT:** In config.local.json, backslashes must be doubled:

```json
{
  "pattern": "\\b(DOCKER)\\b[.,;:!?]?"
}
```

Single `\b` becomes `\\b` in JSON.

## Complete Examples

### Example 1: Create Docker Snippet

**Step 1:** Understand needs
- Trigger: "docker", "container", "dockerfile"
- Provides: Docker best practices and commands
- Frequent use: Yes

**Step 2:** Plan pattern
- Keywords: DOCKER, CONTAINER, DOCKERFILE
- Pattern: `\b(DOCKER|CONTAINER|DOCKERFILE)\b[.,;:!?]?`

**Step 3:** Create snippet
1. Create directory:
   ```bash
   mkdir -p ~/.claude/plugins/.../snippets/local/development/docker
   ```

2. Create SNIPPET.md:
   ```markdown
   ---
   name: "Docker Best Practices"
   description: "Use when working with Docker containers, images, and containerization"
   ---

   # Docker Best Practices
   [Content here...]
   ```

3. Add to config.local.json:
   ```json
   {
     "name": "docker",
     "pattern": "\\b(DOCKER|CONTAINER|DOCKERFILE)\\b[.,;:!?]?",
     "snippet": ["../snippets/local/development/docker/SNIPPET.md"],
     "separator": "\n",
     "enabled": true
   }
   ```

**Step 4:** Test
- Type "DOCKER" → snippet loads
- Type "working with containers" → snippet loads

### Example 2: Update Pattern After Mismatch

**Scenario:** User typed "kubectl" but kubernetes snippet didn't load

**Step 5:** Update pattern
1. Current pattern: `\b(KUBERNETES|K8S)\b[.,;:!?]?`
2. Analysis: Missing "kubectl" keyword
3. New pattern: `\b(KUBERNETES|K8S|KUBECTL)\b[.,;:!?]?`

4. Edit config.local.json:
   ```json
   {
     "name": "kubernetes",
     "pattern": "\\b(KUBERNETES|K8S|KUBECTL)\\b[.,;:!?]?",
     ...
   }
   ```

5. Test: Type "kubectl" → snippet now loads

### Example 3: Delete Unused Snippet

Backup → Remove from config.local.json → Delete SNIPPET.md → Verify

## File Locations

- Config: `~/.claude/plugins/.../scripts/config.local.json`
- Snippets: `~/.claude/plugins/.../snippets/local/{category}/{name}/SNIPPET.md`
- Categories: `communication/`, `documentation/`, `development/`, `productivity/`, `output-formats/`

## Best Practices

- Check architecture first (read config.local.json before creating)
- Pattern in config.local.json, NOT YAML frontmatter
- Use ALL CAPS in patterns with full punctuation: `[.,;:!?]?`
- Double-escape in JSON: `\\b` not `\b`
- Test after changes
- Backup before deletion

## Quick Reference (v2.0)

| Task | Command / Action |
|------|------------------|
| **Discover categories** | `snippets paths` or `snippets paths <filter>` |
| **Create snippet** | `snippets create source.md snippets/local/category/name/SKILL.md` |
| **List all snippets** | `snippets` or `snippets list` |
| **Search snippets** | `snippets <keyword>` (searches name/pattern/description) |
| **Update pattern** | Edit `pattern` field in config.local.json directly |
| **Update content** | Edit SKILL.md file directly (or use `snippets <name>` in TTY → opens $EDITOR) |
| **Enable/disable** | Change `enabled` field in config.local.json |
| **Delete snippet** | 1. Backup files<br>2. Remove from config.local.json<br>3. Delete SKILL.md directory |
| **Validate config** | `snippets validate` or `snippets validate --output json` |
| **Test pattern** | Type trigger keyword in new prompt |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Not loading | Check `enabled: true`, pattern matches (ALL CAPS), file path correct |
| Pattern not matching | Verify standard format, use `[.,;:!?]?`, test with ALL CAPS |
| Too many loading | Check overlapping patterns, disable conflicts |
| JSON errors | Validate syntax, use `\\b` not `\b` |

## Critical Reminders

**Architecture:**
- Pattern goes in config.local.json (NOT YAML frontmatter)
- Always read config.local.json before creating snippets
- Double-escape in JSON: `\\b`

**When User Corrects You:**
Stop → Read actual files → Understand architecture → Fix all related mistakes → Verify
