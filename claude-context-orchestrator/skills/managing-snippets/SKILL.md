---
name: managing-snippets
description: Comprehensive guide for managing Claude Code snippets - creating, reading, updating, and deleting snippet configurations with regex pattern matching. Use this skill when users want to create, inspect, modify, or manage snippet configurations in their Claude Code environment.
---

# Managing Snippets

Snippets auto-inject context when regex patterns match user messages. This skill provides a comprehensive workflow for creating, managing, and maintaining snippet configurations.

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

## Snippet Management Process

Follow these steps in order to effectively manage snippets.

### Step 1: Understanding Snippet Needs

Before creating a snippet, clearly understand:
- **What triggers it?** - Keywords that should activate the snippet
- **What does it provide?** - Context, guidance, or reference material
- **How often is it used?** - Frequent use justifies snippet automation
- **What's the scope?** - Narrow (specific tool) vs. broad (general concept)

**Example questions:**
- "What keywords should trigger this snippet?"
- "Is this content used frequently enough to justify automatic injection?"
- "Does this belong in a snippet or should it be a skill?"

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

Once you've planned the pattern and identified the content, create the snippet.

**Architecture check (CRITICAL):**
1. **Read config.local.json first** to understand existing structure
2. **Examine 1-2 existing snippets** to see the pattern
3. **Understand the separation:**
   - YAML frontmatter (name, description) goes in SNIPPET.md
   - Pattern and file path go in config.local.json
   - Never put pattern in YAML frontmatter

**Creation workflow:**

1. **Create SNIPPET.md file:**
   ```bash
   mkdir -p ~/.claude/plugins/.../snippets/local/category/snippet-name
   # Create SNIPPET.md with proper frontmatter
   ```

2. **Add entry to config.local.json:**
   ```json
   {
     "name": "snippet-name",
     "pattern": "\\b(PATTERN)\\b[.,;:!?]?",
     "snippet": ["../snippets/local/category/snippet-name/SNIPPET.md"],
     "separator": "\n",
     "enabled": true
   }
   ```

3. **Verify the snippet works:**
   - Type the trigger keyword in a new prompt
   - Confirm content loads automatically

**Common mistakes to avoid:**
- ❌ Putting pattern in YAML frontmatter
- ❌ Using lowercase in pattern
- ❌ Missing `\\b` word boundaries (requires double backslash in JSON)
- ❌ Forgetting to add entry to config.local.json

### Step 4: Reading/Inspecting Snippets

To view configured snippets:

**List all snippets:**
```bash
cd /Users/wz/.claude/plugins/.../scripts
python3 snippets_cli.py list --snippets-dir ../snippets/local
```

**View specific snippet:**
```bash
python3 snippets_cli.py list <snippet-name> --snippets-dir ../snippets/local
```

**What to check:**
- Enabled status (✓ or ✗)
- Pattern alternatives (does it cover all intended keywords?)
- File paths (do they point to correct locations?)
- Content (read SNIPPET.md to verify)

**Regular audits:**
- Review snippets monthly
- Disable unused snippets
- Update patterns based on usage
- Remove outdated content

### Step 5: Updating Snippets

Modify existing snippets when:
- Pattern doesn't match expected keywords
- Content is outdated
- Need to enable/disable temporarily
- Want to rename for clarity

**Update workflow:**

1. **Show current state:**
   ```bash
   python3 snippets_cli.py list <snippet-name> --snippets-dir ../snippets/local
   ```

2. **Determine what needs updating:**
   - Pattern expansion (add more keywords)
   - Content modification (edit SNIPPET.md)
   - Status change (enable/disable)
   - Rename (update name field)

3. **For pattern updates:**
   - Edit config.local.json
   - Modify the `pattern` field
   - Ensure new pattern follows standard format

4. **For content updates:**
   - Edit the SNIPPET.md file directly
   - Maintain YAML frontmatter structure

5. **Verify changes:**
   - Test trigger keywords
   - Confirm content loads correctly

**Context-aware updating:**
If a snippet failed to load during a session, analyze why:
- Did the pattern not match? → Expand pattern
- Was it disabled? → Enable it
- Missing keywords? → Add alternatives

### Step 6: Deleting Snippets

Remove snippets that are:
- No longer needed
- Superseded by other snippets or skills
- Creating conflicts with other patterns

**Deletion workflow:**

1. **Backup first:**
   ```bash
   # Create backup directory
   mkdir -p ~/.claude/plugins/.../backups/$(date +%Y%m%d_%H%M%S)_snippet-name

   # Copy files
   cp SNIPPET.md config.local.json backups/...
   ```

2. **Remove from config.local.json:**
   - Delete the entire mapping object
   - Ensure JSON remains valid (check commas)

3. **Optionally delete SNIPPET.md:**
   ```bash
   rm -rf ~/.claude/plugins/.../snippets/local/category/snippet-name
   ```

4. **Verify deletion:**
   - List remaining snippets
   - Confirm trigger keyword no longer loads content

**Restoration:**
If you need to restore:
1. Copy files from backup directory
2. Add mapping back to config.local.json
3. Verify pattern works

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

## Quick Reference

| Task | Action |
|------|--------|
| Create snippet | 1. Create SNIPPET.md with frontmatter<br>2. Add entry to config.local.json |
| List all snippets | `python3 snippets_cli.py list` |
| View one snippet | `python3 snippets_cli.py list <name>` |
| Update pattern | Edit `pattern` field in config.local.json |
| Update content | Edit SNIPPET.md file directly |
| Enable/disable | Change `enabled` field in config.local.json |
| Delete snippet | 1. Backup files<br>2. Remove from config.local.json<br>3. Delete SNIPPET.md |
| Test pattern | Type trigger keyword in new prompt |

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
