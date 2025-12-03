# Snippet Verification

Comprehensive guide for verifying that snippets are correctly injected into Claude's context.

---

## Overview

When the user mentions "snippetV" or "snippet-verify", perform a comprehensive snippet verification check to ensure snippets are correctly injected into context.

This verification system uses **verification hashes** - unique identifiers embedded in snippet content to confirm:
- Snippet was injected
- Snippet content matches the source
- Snippet hasn't been corrupted or modified

---

## Verification Process

### Step 1: Identify Injected Snippets

Search your current context for snippet tags and verification hashes.

**Look for:**
- XML-style tags like `<snippet_name>...</snippet_name>`
- Lines containing `**VERIFICATION_HASH:** \`hash\``

List all snippets found in your context with their extracted hashes.

### Step 2: Get Ground Truth from CLI

Run this command to retrieve the authoritative snippet list with hashes:

```bash
cd ~/.claude/snippets && ./snippets-cli.py list --show-content
```

Parse the JSON output to extract:
- Snippet names
- Patterns
- Verification hashes (found in content as `**VERIFICATION_HASH:** \`...\``)
- File paths
- Enabled status

### Step 3: Cross-Verify

Compare the hashes found in your context against the CLI ground truth:

- ✅ **Match** - Hash in context matches CLI hash → Snippet correctly injected
- ❌ **Mismatch** - Hash differs → Snippet outdated or corrupted
- ⚠️ **Missing in Context** - Snippet in CLI but not in your context → Not triggered
- ⚠️ **Missing Hash** - Snippet tag present but no hash found → Verification impossible

### Step 4: Report Results

Present a clear verification report with proper line breaks for readability:

```
📋 Snippet Verification Report

INJECTED SNIPPETS IN CONTEXT:

✅ snippet-name (hash) - Verified

❌ snippet-name (hash) - MISMATCH (expected: correct_hash)

⚠️ snippet-name - Missing hash

ALL SNIPPETS IN CLI:

• snippet-name: hash (pattern: regex)

• snippet-name: hash (pattern: regex)

SUMMARY:

• Total in CLI: X

• Injected in context: Y

• Verified: Z

• Mismatches: M

• Missing hashes: N
```

---

## Important Notes

- The verification hash is a unique identifier generated when the snippet is created/updated
- It uses Python's hashlib and includes timestamp for uniqueness
- Hashes are embedded directly in snippet content as `**VERIFICATION_HASH:** \`hash\``
- The CLI command `list --show-content` is the authoritative source
- Always use Bash tool to run the CLI command, don't assume values

---

## Example CLI Output Format

```json
{
  "success": true,
  "operation": "list",
  "data": {
    "snippets": [
      {
        "name": "codex",
        "pattern": "\\b(codex|cdx)\\b",
        "file": "snippets/codex.md",
        "enabled": true,
        "content": "<codex>\n**VERIFICATION_HASH:** `95f6ccff3c85627c`\n..."
      }
    ]
  }
}
```

Extract the hash from the content field using regex or string parsing.

---

## Verification Hash System

### How Hashes Are Generated

```python
import hashlib
import time

def generate_hash():
    """Generate unique verification hash"""
    timestamp = str(time.time())
    return hashlib.md5(timestamp.encode()).hexdigest()[:16]
```

### Hash Format in Snippets

```markdown
**VERIFICATION_HASH:** `8d3a7f1b9c4e2056`
```

**Requirements:**
- Must be in markdown bold format: `**VERIFICATION_HASH:**`
- Hash must be in backticks: \`hash\`
- Typically placed near the top of snippet content (after YAML frontmatter)

### When Hashes Are Updated

Hashes are regenerated when:
- Snippet content is modified via CLI
- Snippet file is manually edited and hash is removed
- Snippet is created for the first time

---

## Verification Workflow

### Complete Verification Example

```bash
# 1. User asks for verification
# "Can you verify my snippets?"

# 2. Search context for verification hashes
# Look for: **VERIFICATION_HASH:** `...`

# 3. Run CLI to get authoritative list
cd ~/.claude/snippets
./snippets-cli.py list --show-content

# 4. Parse JSON output
{
  "success": true,
  "operation": "list",
  "data": {
    "snippets": [
      {
        "name": "docker",
        "pattern": "\\b(docker|DOCKER)\\b",
        "file": "snippets/docker.md",
        "enabled": true,
        "content": "**VERIFICATION_HASH:** `a1b2c3d4e5f67890`\n..."
      }
    ]
  }
}

# 5. Compare hashes
# Context hash: a1b2c3d4e5f67890
# CLI hash: a1b2c3d4e5f67890
# Result: ✅ Match - Verified

# 6. Generate report
```

---

## Common Verification Scenarios

### Scenario 1: All Snippets Verified

```
📋 Snippet Verification Report

INJECTED SNIPPETS IN CONTEXT:

✅ docker (a1b2c3d4e5f67890) - Verified
✅ python (f9e8d7c6b5a43210) - Verified

ALL SNIPPETS IN CLI:

• docker: a1b2c3d4e5f67890 (pattern: \b(docker|DOCKER)\b)
• python: f9e8d7c6b5a43210 (pattern: \b(python|PYTHON)\b)

SUMMARY:

• Total in CLI: 2
• Injected in context: 2
• Verified: 2
• Mismatches: 0
• Missing hashes: 0
```

### Scenario 2: Hash Mismatch Detected

```
📋 Snippet Verification Report

INJECTED SNIPPETS IN CONTEXT:

✅ docker (a1b2c3d4e5f67890) - Verified
❌ python (OLD_HASH_HERE) - MISMATCH (expected: f9e8d7c6b5a43210)

ALL SNIPPETS IN CLI:

• docker: a1b2c3d4e5f67890 (pattern: \b(docker|DOCKER)\b)
• python: f9e8d7c6b5a43210 (pattern: \b(python|PYTHON)\b)

SUMMARY:

• Total in CLI: 2
• Injected in context: 2
• Verified: 1
• Mismatches: 1
• Missing hashes: 0

⚠️ RECOMMENDATION: Restart Claude Code to reload updated snippets
```

### Scenario 3: Snippet Not Triggered

```
📋 Snippet Verification Report

INJECTED SNIPPETS IN CONTEXT:

✅ docker (a1b2c3d4e5f67890) - Verified

ALL SNIPPETS IN CLI:

• docker: a1b2c3d4e5f67890 (pattern: \b(docker|DOCKER)\b)
• python: f9e8d7c6b5a43210 (pattern: \b(python|PYTHON)\b)
• git: 1234567890abcdef (pattern: \b(git|GIT)\b)

SUMMARY:

• Total in CLI: 3
• Injected in context: 1
• Verified: 1
• Mismatches: 0
• Missing hashes: 0

ℹ️ NOTE: 'python' and 'git' snippets not triggered (user prompt didn't match patterns)
```

### Scenario 4: Missing Verification Hash

```
📋 Snippet Verification Report

INJECTED SNIPPETS IN CONTEXT:

✅ docker (a1b2c3d4e5f67890) - Verified
⚠️ python - Missing hash (cannot verify)

ALL SNIPPETS IN CLI:

• docker: a1b2c3d4e5f67890 (pattern: \b(docker|DOCKER)\b)
• python: f9e8d7c6b5a43210 (pattern: \b(python|PYTHON)\b)

SUMMARY:

• Total in CLI: 2
• Injected in context: 2
• Verified: 1
• Mismatches: 0
• Missing hashes: 1

⚠️ RECOMMENDATION: Update 'python' snippet to include verification hash
```

---

## Troubleshooting

### Hash Not Found in Context

**Possible causes:**
- Snippet wasn't injected (pattern didn't match)
- Snippet file doesn't contain verification hash
- Hash was stripped during injection

**Solutions:**
- Check if user prompt matches snippet pattern
- Add verification hash to snippet file manually
- Re-generate snippet via CLI to auto-add hash

### Hash Mismatch

**Possible causes:**
- Snippet file was updated but Claude Code wasn't restarted
- Snippet content was corrupted during injection
- Multiple versions of snippet exist

**Solutions:**
- Restart Claude Code
- Verify snippet file content manually
- Re-create snippet via CLI

### CLI Command Fails

**Possible causes:**
- Snippets directory doesn't exist
- CLI script not executable
- Python environment issues

**Solutions:**
```bash
# Check directory exists
ls ~/.claude/snippets

# Make CLI executable
chmod +x ~/.claude/snippets/snippets-cli.py

# Run with python3 explicitly
python3 ~/.claude/snippets/snippets-cli.py list --show-content
```

---

## Advanced Verification

### Automated Verification Script

```bash
#!/bin/bash
# verify-snippets.sh

echo "🔍 Starting Snippet Verification..."

# Get CLI snippets
cd ~/.claude/snippets
CLI_OUTPUT=$(./snippets-cli.py list --show-content)

# Extract hashes
CLI_HASHES=$(echo "$CLI_OUTPUT" | jq -r '.data.snippets[] | "\(.name):\(.content | match("VERIFICATION_HASH.*`([a-f0-9]+)`").captures[0].string)"')

echo "CLI Snippets:"
echo "$CLI_HASHES"

# Ask Claude to verify
claude -p "snippetV - verify all injected snippets"
```

### Continuous Integration

```yaml
# .github/workflows/verify-snippets.yml
name: Verify Snippets
on: [push]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Verify Snippet Hashes
        run: |
          cd ~/.claude/snippets
          ./snippets-cli.py validate
```

---

## Quick Reference

```bash
# Get all snippets with hashes
cd ~/.claude/snippets && ./snippets-cli.py list --show-content

# Verify specific snippet
claude -p "what is the verification hash for docker?"

# Full verification
claude -p "snippetV"

# Manual hash extraction
cat ~/.claude/snippets/snippets/docker.md | grep "VERIFICATION_HASH"

# Validate snippet files
cd ~/.claude/snippets && ./snippets-cli.py validate
```

---

## Integration with Managing Snippets

For creating and managing snippets with verification hashes, see the **managing-snippets** skill.

**Key integration points:**
- Snippets CLI automatically generates hashes on create/update
- Hashes are embedded in markdown frontmatter section
- Verification system uses CLI as single source of truth
