<snippet_verification>

When the user mentions "snippetV" or "snippet-verify", perform a comprehensive snippet verification check.

## Verification Process

### Step 1: Identify Injected Snippets

Search your current context for snippet tags and verification hashes. Look for:
- XML-style tags like `<snippet_name>...</snippet_name>`
**VERIFICATION_HASH:** `56f127e9a844040d`

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

- ✅ **Match**: Hash in context matches CLI hash → Snippet correctly injected
- ❌ **Mismatch**: Hash differs → Snippet outdated or corrupted
- ⚠️ **Missing in Context**: Snippet in CLI but not in your context → Not triggered
- ⚠️ **Missing Hash**: Snippet tag present but no hash found → Verification impossible

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

## Important Notes

- The verification hash is a unique identifier generated when the snippet is created/updated
- It uses Python's hashlib and includes timestamp for uniqueness
- Hashes are embedded directly in snippet content as `**VERIFICATION_HASH:** \`hash\``
- The CLI command `list --show-content` is the authoritative source
- Always use Bash tool to run the CLI command, don't assume values

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

</snippet_verification>
