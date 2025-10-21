# Configuration

Complete guide to the configuration system and snippet structure.

## Table of Contents

- [Configuration System](#configuration-system)
- [Config File Structure](#config-file-structure)
- [Snippet File Structure](#snippet-file-structure)
- [Pattern Syntax](#pattern-syntax)
- [Advanced Configuration](#advanced-configuration)
- [Examples](#examples)

---

## Configuration System

The plugin uses a **layered configuration system** with two config files:

### 1. Base Config (`scripts/config.json`)

- Minimal shared examples
- Contains 2 basic snippets (HTML, nvim)
- Simple starting point
- Committed to repository

### 2. Local Config (`scripts/config.local.json`)

- **Contains 20+ example snippets** from real usage
- Shows patterns for email, calendar, search, HTML, testing, etc.
- **Committed to repo** as learning examples
- References files in various locations
- **Overrides base config** by snippet name

### Merge Behavior

Both config files are loaded and merged:

- If a snippet name exists in both configs, **local wins**
- Otherwise, snippets from both configs are combined
- Result: You get base examples + local examples

**Example:**

```json
// config.json (base)
{
  "mappings": [
    {
      "name": "HTML",
      "pattern": "\\bHTML\\b\\.?",
      "snippet": ["snippets/HTML.md"],
      "enabled": true
    }
  ]
}

// config.local.json (local - overrides HTML if same name)
{
  "mappings": [
    {
      "name": "HTML",
      "pattern": "\\bHTML\\b",  // Different pattern
      "snippet": ["snippets/custom-html.md"],
      "enabled": true
    },
    {
      "name": "docker",
      "pattern": "\\b(docker|container)\\b",
      "snippet": ["snippets/docker.md"],
      "enabled": true
    }
  ]
}

// Result: HTML from local config wins, docker is added
```

### Which Config to Edit?

**Use `config.json` for:**
- Shared snippets across all users
- Simple, universal snippets
- Base functionality

**Use `config.local.json` for:**
- Personal snippets
- Project-specific context
- Custom workflows
- Examples and templates

---

## Config File Structure

### Basic Structure

```json
{
  "mappings": [
    {
      "name": "snippet-name",
      "pattern": "\\bpattern\\b",
      "snippet": ["path/to/snippet.md"],
      "enabled": true,
      "separator": "\n"
    }
  ]
}
```

### Field Descriptions

#### `name` (required, string)
- Unique identifier for the snippet
- Used in commands and logging
- Convention: lowercase, hyphen-separated

**Example:**
```json
"name": "docker"
"name": "google-calendar"
"name": "html-format"
```

#### `pattern` (required, string)
- Regex pattern for matching prompts
- Case-insensitive by default
- Use `\b` for word boundaries

**Example:**
```json
"pattern": "\\bHTML\\b"
"pattern": "\\b(docker|container|dockerfile)\\b"
"pattern": "\\b(google\\s*calendar|gcal)\\b"
```

See [Pattern Syntax](#pattern-syntax) for details.

#### `snippet` (required, array of strings)
- List of snippet file paths
- Relative to `scripts/` directory
- Can combine multiple files

**Example:**
```json
"snippet": ["snippets/docker.md"]
"snippet": ["snippets/part1.md", "snippets/part2.md"]
"snippet": ["../commands/local/mail.md"]
```

#### `enabled` (required, boolean)
- Whether the snippet is active
- Set to `false` to temporarily disable

**Example:**
```json
"enabled": true   // Active
"enabled": false  // Disabled (won't match)
```

#### `separator` (optional, string)
- Separator between multiple snippet files
- Default: `"\n"` (single newline)

**Example:**
```json
"separator": "\n\n---\n\n"  // Add horizontal rule between files
"separator": "\n\n"         // Double newline
```

### Complete Example

```json
{
  "mappings": [
    {
      "name": "docker",
      "pattern": "\\b(docker|container|dockerfile|compose)\\b",
      "snippet": ["snippets/docker.md"],
      "enabled": true,
      "separator": "\n"
    },
    {
      "name": "multipart-snippet",
      "pattern": "\\bmultipart\\b",
      "snippet": [
        "snippets/part1.md",
        "snippets/part2.md",
        "snippets/part3.md"
      ],
      "enabled": true,
      "separator": "\n\n---\n\n"
    },
    {
      "name": "disabled-example",
      "pattern": "\\bdisabled\\b",
      "snippet": ["snippets/disabled.md"],
      "enabled": false
    }
  ]
}
```

---

## Snippet File Structure

### Basic Snippet File

```markdown
---
description: Brief description of this snippet
SNIPPET_NAME: snippet-name
ANNOUNCE_USAGE: true
---

# Snippet Title

**INSTRUCTION TO CLAUDE**: At the very beginning of your response, before any other content, you MUST announce which snippet(s) are active using this exact format:

📎 **Active Context**: snippet-name

---

**VERIFICATION_HASH:** `unique-hash-here`

## Content

Your instructions and content here...
```

### YAML Frontmatter

The frontmatter at the top of the file (between `---` lines) contains metadata:

#### `description` (required)
- Brief description of the snippet
- Used in help text and listings

#### `SNIPPET_NAME` (required)
- Must match the `name` field in config
- Used for announcement coordination

#### `ANNOUNCE_USAGE` (recommended)
- Set to `true` to enable usage announcements
- Shows "📎 **Active Context**: snippet-name" at start of Claude's response

### Announcement Block

```markdown
**INSTRUCTION TO CLAUDE**: At the very beginning of your response, before any other content, you MUST announce which snippet(s) are active using this exact format:

📎 **Active Context**: snippet-name

If multiple snippets are detected, combine them:

📎 **Active Contexts**: snippet1, snippet2, snippet3
```

This tells Claude to announce which snippets are active, providing transparency.

### Verification Hash

```markdown
**VERIFICATION_HASH:** `abc123def456`
```

Optional hash for testing snippet injection:
- Ask Claude: "What is the verification hash?"
- If Claude returns the hash, snippet was injected successfully

### Content

The rest of the file contains your instructions and content:

```markdown
## Instructions for Claude

Tell Claude what to do when this snippet is injected.

## Context

Provide relevant context, cheat sheets, guidelines, etc.

## Examples

Show examples of how to use this information.
```

### Complete Example

```markdown
---
description: Docker commands and best practices
SNIPPET_NAME: docker
ANNOUNCE_USAGE: true
---

# Docker Snippet

**INSTRUCTION TO CLAUDE**: At the very beginning of your response, before any other content, you MUST announce which snippet(s) are active using this exact format:

📎 **Active Context**: docker

---

**VERIFICATION_HASH:** `d0ck3r_h4sh_2024`

## Docker Commands

When helping with Docker, use these commands:

### Container Management

- `docker ps` - List running containers
- `docker ps -a` - List all containers
- `docker stop <container>` - Stop a container
- `docker rm <container>` - Remove a container

### Image Management

- `docker images` - List images
- `docker pull <image>` - Pull an image
- `docker rmi <image>` - Remove an image

## Best Practices

1. Use `.dockerignore` to exclude files
2. Multi-stage builds for smaller images
3. Use specific image tags, not `latest`
4. Run as non-root user when possible

## Example Dockerfile

\```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
USER node
CMD ["node", "server.js"]
\```
```

---

## Pattern Syntax

Patterns use **regular expressions (regex)** for matching.

### Basic Patterns

#### Exact Word Match

```json
"pattern": "\\bHTML\\b"
```

Matches: `HTML`, `html`, `HtMl`
Doesn't match: `htmlparse`, `myHTML`

**Explanation:**
- `\b` = Word boundary
- `HTML` = The word (case-insensitive)
- `\b` = Word boundary

#### Multiple Alternatives

```json
"pattern": "\\b(docker|container|dockerfile)\\b"
```

Matches any of: `docker`, `container`, `dockerfile`

**Explanation:**
- `(option1|option2|option3)` = Alternatives (OR)
- `\b` = Word boundaries around the whole group

#### Phrase with Optional Spaces

```json
"pattern": "\\b(google\\s*calendar|gcal)\\b"
```

Matches: `google calendar`, `googlecalendar`, `gcal`

**Explanation:**
- `\s*` = Zero or more whitespace characters
- `|` = OR
- Alternative shorter form also included

### Advanced Patterns

#### Optional Words

```json
"pattern": "\\b(docker\\s+)?(container|compose)\\b"
```

Matches: `container`, `docker container`, `compose`, `docker compose`

**Explanation:**
- `(docker\s+)?` = Optional "docker" followed by whitespace
- `?` = Makes the group optional

#### Pattern with Optional Punctuation

```json
"pattern": "\\bHTML\\b\\.?"
```

Matches: `HTML`, `HTML.`, `html`

**Explanation:**
- `\.?` = Optional period
- `?` = Makes the period optional

#### Case-Sensitive Pattern (Advanced)

All patterns are case-insensitive by default. For case-sensitive matching, you would need to modify the hook script.

### Pattern Testing

Test your patterns before committing:

```bash
cd scripts/
python3 snippets_cli.py test snippet-name "test text with keywords"
```

**Example:**

```bash
python3 snippets_cli.py test docker "I need help with Docker containers"
# Output: ✅ Pattern matches
```

### Common Pattern Mistakes

❌ **Wrong:** Missing word boundaries
```json
"pattern": "HTML"
```
This matches `inHTML`, `HTMLparser`, etc.

✅ **Right:** With word boundaries
```json
"pattern": "\\bHTML\\b"
```
Only matches whole word `HTML`.

---

❌ **Wrong:** Single backslash
```json
"pattern": "\bHTML\b"
```
JSON requires escaping backslashes.

✅ **Right:** Double backslash
```json
"pattern": "\\bHTML\\b"
```

---

❌ **Wrong:** Forgetting parentheses for alternatives
```json
"pattern": "\\bdocker|container\\b"
```
This matches `docker` OR `anything ending with 'container'`.

✅ **Right:** Parentheses around alternatives
```json
"pattern": "\\b(docker|container)\\b"
```

---

## Advanced Configuration

### Multi-File Snippets

Combine multiple files into one snippet:

```json
{
  "name": "complete-guide",
  "pattern": "\\bcomplete-guide\\b",
  "snippet": [
    "snippets/guide-part1-intro.md",
    "snippets/guide-part2-examples.md",
    "snippets/guide-part3-advanced.md"
  ],
  "separator": "\n\n---\n\n",
  "enabled": true
}
```

Each file is concatenated with the separator between them.

### Temporarily Disable Snippets

Set `"enabled": false` to temporarily disable:

```json
{
  "name": "docker",
  "pattern": "\\b(docker|container)\\b",
  "snippet": ["snippets/docker.md"],
  "enabled": false  // Temporarily disabled
}
```

The snippet is still configured but won't match any prompts.

### Path Resolution

Paths in `snippet` array are relative to `scripts/` directory:

```json
"snippet": ["snippets/docker.md"]           // scripts/snippets/docker.md
"snippet": ["../commands/local/mail.md"]    // commands/local/mail.md
"snippet": ["../../somewhere/file.md"]      // ../../somewhere/file.md
```

### Configuration Validation

Validate your configuration:

```bash
cd scripts/
python3 snippets_cli.py validate
```

This checks:
- JSON syntax
- Required fields present
- File paths exist
- Pattern syntax is valid
- No duplicate names

---

## Examples

### Example 1: Simple Snippet

```json
{
  "name": "python-tips",
  "pattern": "\\bpython\\b",
  "snippet": ["snippets/python.md"],
  "enabled": true
}
```

### Example 2: Multiple Keywords

```json
{
  "name": "js-frameworks",
  "pattern": "\\b(react|vue|angular|svelte)\\b",
  "snippet": ["snippets/js-frameworks.md"],
  "enabled": true
}
```

### Example 3: Multi-File Snippet

```json
{
  "name": "project-context",
  "pattern": "\\b(project|codebase|architecture)\\b",
  "snippet": [
    "snippets/project-overview.md",
    "snippets/project-conventions.md",
    "snippets/project-architecture.md"
  ],
  "separator": "\n\n━━━━━━━━━━━━━━━━━━━━━\n\n",
  "enabled": true
}
```

### Example 4: Local File Reference

```json
{
  "name": "mail",
  "pattern": "\\b(email|mail|gmail)\\b",
  "snippet": ["../commands/local/mail.md"],
  "enabled": true
}
```

### Example 5: Disabled Snippet

```json
{
  "name": "deprecated-feature",
  "pattern": "\\bdeprecated\\b",
  "snippet": ["snippets/deprecated.md"],
  "enabled": false,
  "separator": "\n"
}
```

---

**Next:**
- [Commands Reference](commands-reference.md) - Snippet management commands
- [Template Pattern](template-pattern.md) - Advanced template-based snippets
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
