# Troubleshooting

Common issues and solutions for the Claude Code Snippets Plugin.

## Table of Contents

- [Snippet Not Injecting](#snippet-not-injecting)
- [Pattern Not Matching](#pattern-not-matching)
- [Commands Not Found](#commands-not-found)
- [Configuration Errors](#configuration-errors)
- [Hook Not Loading](#hook-not-loading)
- [File Not Found Errors](#file-not-found-errors)
- [Template Pattern Issues](#template-pattern-issues)
- [Debugging Tips](#debugging-tips)

---

## Snippet Not Injecting

### Symptom
Your prompt contains the keywords but the snippet is not being injected.

### Diagnosis

1. **Check if pattern matches:**
   ```bash
   cd ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts
   python3 snippets_cli.py test snippet-name "your test prompt here"
   ```

2. **Check if snippet is enabled:**
   ```bash
   python3 snippets_cli.py list --name snippet-name
   ```
   Look for: `Status: ✅ Enabled` (not ❌ Disabled)

3. **Check if file exists:**
   ```bash
   ls -l snippets/snippet-name.md
   ```

### Solutions

#### Pattern doesn't match
```bash
# Update the pattern
/claude-code-snippets:update-snippet snippet-name

# When prompted, provide a new pattern
> docker, container, dockerfile
```

#### Snippet is disabled
Edit `scripts/config.local.json` or `scripts/config.json`:
```json
{
  "name": "snippet-name",
  "enabled": false  // Change to true
}
```

#### File doesn't exist
Create the snippet file:
```bash
/claude-code-snippets:create-snippet snippet-name
```

---

## Pattern Not Matching

### Symptom
Test command shows pattern doesn't match when it should.

### Common Pattern Mistakes

#### Missing word boundaries

❌ **Wrong:**
```json
"pattern": "HTML"
```
This matches `inHTML`, `HTMLparser`, etc.

✅ **Fix:**
```json
"pattern": "\\bHTML\\b"
```

#### Single backslash in JSON

❌ **Wrong:**
```json
"pattern": "\bHTML\b"
```
JSON requires escaped backslashes.

✅ **Fix:**
```json
"pattern": "\\bHTML\\b"
```

#### Wrong grouping for alternatives

❌ **Wrong:**
```json
"pattern": "\\bdocker|container\\b"
```
This matches `docker` OR `anything ending with 'container'`.

✅ **Fix:**
```json
"pattern": "\\b(docker|container)\\b"
```

### Testing Patterns

1. **Test with CLI:**
   ```bash
   cd scripts/
   python3 snippets_cli.py test snippet-name "test prompt with keywords"
   ```

2. **Test regex online:**
   - Use https://regex101.com/
   - Set flavor to "Python"
   - Set flags to "case insensitive" (i)
   - Test your pattern against various inputs

3. **Update pattern:**
   ```bash
   /claude-code-snippets:update-snippet snippet-name
   ```

---

## Commands Not Found

### Symptom
```
Command not found: /claude-code-snippets:create-snippet
```

### Diagnosis

1. **Check if plugin is installed:**
   ```bash
   /plugin list
   ```
   Look for: `claude-code-snippets@warren-claude-code-plugin-marketplace`

2. **Check if commands are loaded:**
   ```bash
   /help | grep claude-code-snippets
   ```

### Solutions

#### Plugin not installed
```bash
/plugin marketplace add WarrenZhu050413/Warren-Claude-Code-Plugin-Marketplace
/plugin install claude-code-snippets@warren-claude-code-plugin-marketplace
```

#### Plugin installed but commands not showing
1. Restart Claude Code
2. Check plugin manifest at `.claude-plugin/plugin.json`
3. Verify `commands` path is correct

#### Permission issues
```bash
cd ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin
chmod +x scripts/*.py
```

---

## Configuration Errors

### Symptom
```
Error: Invalid JSON in config file
Error: Missing required field
```

### Diagnosis

**Validate configuration:**
```bash
cd scripts/
python3 snippets_cli.py validate
```

### Common Errors

#### Invalid JSON syntax

❌ **Wrong:**
```json
{
  "name": "docker",
  "pattern": "\\bdocker\\b",  // Trailing comma
}
```

✅ **Fix:**
```json
{
  "name": "docker",
  "pattern": "\\bdocker\\b"
}
```

#### Missing required fields

❌ **Wrong:**
```json
{
  "name": "docker",
  "pattern": "\\bdocker\\b"
  // Missing: snippet, enabled
}
```

✅ **Fix:**
```json
{
  "name": "docker",
  "pattern": "\\bdocker\\b",
  "snippet": ["snippets/docker.md"],
  "enabled": true
}
```

#### Duplicate snippet names

❌ **Wrong:**
```json
{
  "mappings": [
    {
      "name": "docker",
      "pattern": "\\bdocker\\b",
      "snippet": ["snippets/docker.md"],
      "enabled": true
    },
    {
      "name": "docker",  // Duplicate!
      "pattern": "\\bcontainer\\b",
      "snippet": ["snippets/container.md"],
      "enabled": true
    }
  ]
}
```

✅ **Fix:**
Use unique names for each snippet.

### Solutions

1. **Validate JSON:**
   - Use https://jsonlint.com/
   - Copy/paste your config and check for errors

2. **Check required fields:**
   Every snippet must have:
   - `name` (string)
   - `pattern` (string)
   - `snippet` (array)
   - `enabled` (boolean)

3. **Fix and test:**
   ```bash
   python3 snippets_cli.py validate
   ```

---

## Hook Not Loading

### Symptom
Snippet injection not working at all, no matter what you type.

### Diagnosis

**Check hook configuration:**
```bash
cat ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/hooks/hooks.json
```

Should contain:
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

### Solutions

#### Hook file missing or corrupted
Restore from backup or reinstall plugin.

#### Python not in PATH
```bash
which python3
# Should output a path like: /usr/bin/python3
```

If not found, install Python 3.

#### Script not executable
```bash
chmod +x ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts/snippet_injector.py
```

#### Restart Claude Code
After fixing hooks, restart Claude Code to reload.

---

## File Not Found Errors

### Symptom
```
Error: Snippet file not found: snippets/docker.md
```

### Diagnosis

**Check file exists:**
```bash
cd ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts
ls -l snippets/docker.md
```

### Solutions

#### File path is wrong in config

Check config file:
```json
{
  "name": "docker",
  "snippet": ["snippets/docker.md"]  // Path relative to scripts/
}
```

File should be at:
```
scripts/snippets/docker.md
```

#### File was deleted

Recreate it:
```bash
/claude-code-snippets:create-snippet docker
```

Or restore from backup:
```bash
ls scripts/snippets/*.backup.*
cp scripts/snippets/docker.md.backup.20251012_143530 scripts/snippets/docker.md
```

#### Wrong directory structure

Ensure directory exists:
```bash
mkdir -p scripts/snippets/
```

---

## Template Pattern Issues

### Symptom
Template-based snippet not working, Claude not reading templates.

### Common Issues

#### Wrong path to template

❌ **Wrong:**
```markdown
**Base Template:** `./templates/html/base-template.html`
```

✅ **Right:**
```markdown
**Base Template:** `${CLAUDE_PLUGIN_ROOT}/templates/html/base-template.html`
```

#### Template file doesn't exist

Check if file exists:
```bash
ls -l templates/html/base-template.html
```

Create if missing.

#### Placeholder not documented

Make sure to document all placeholders in the snippet:
```markdown
## Placeholders

- `{{TITLE}}`: Document title
- `<!-- CONTENT GOES HERE -->`: Main content insertion point
```

### Solutions

1. **Verify template path:**
   ```bash
   cd ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin
   ls -l templates/your-template/
   ```

2. **Use correct path format:**
   Always use `${CLAUDE_PLUGIN_ROOT}/templates/...`

3. **Test template reading:**
   Ask Claude: "Please read the template at ${CLAUDE_PLUGIN_ROOT}/templates/html/base-template.html"

4. **Check examples file exists:**
   ```bash
   ls -l templates/your-template/examples.md
   ```

---

## Debugging Tips

### Enable Verbose Logging

Add debug output to your snippet:

```markdown
**VERIFICATION_HASH:** `debug_snippet_123`

At the start of your response, always say:
"DEBUG: Snippet 'snippet-name' is active. Hash: debug_snippet_123"
```

Then test:
```
Test the snippet-name snippet
```

If you see the debug message, the snippet is being injected.

### Test Snippet Injection Manually

1. **Get snippet content:**
   ```bash
   cat scripts/snippets/docker.md
   ```

2. **Copy content to clipboard**

3. **Manually paste into prompt:**
   ```
   [Pasted snippet content]

   Now help me with Docker
   ```

4. If this works but automatic injection doesn't, the issue is with the hook or pattern matching.

### Check Verification Hashes

Add a verification hash to your snippet:
```markdown
**VERIFICATION_HASH:** `docker_v1_2024`
```

Test:
```
What is the verification hash for the docker snippet?
```

If Claude returns the hash, injection is working.

### CLI Validation

Run full validation:
```bash
cd scripts/
python3 snippets_cli.py validate
```

This checks:
- JSON syntax
- File paths
- Pattern validity
- Required fields
- Duplicate names

### Check Multiple Configs

Remember both configs are loaded:
```bash
cd scripts/
cat config.json        # Base config
cat config.local.json  # Local config (overrides)
```

If a snippet appears in both, local wins.

### Network/Permission Issues

Check file permissions:
```bash
ls -la scripts/snippets/
ls -la scripts/*.json
```

All files should be readable:
```
-rw-r--r--  1 user  group  123 Oct 12 14:30 docker.md
```

---

## Still Having Issues?

### Gather Information

1. **Plugin version:**
   ```bash
   cat .claude-plugin/plugin.json | grep version
   ```

2. **Configuration:**
   ```bash
   cat scripts/config.local.json
   ```

3. **Validation output:**
   ```bash
   python3 scripts/snippets_cli.py validate
   ```

4. **Test results:**
   ```bash
   python3 scripts/snippets_cli.py test snippet-name "test prompt"
   ```

### Report Issue

Include this information when reporting issues:
- Plugin version
- Error message (exact text)
- Configuration snippet (relevant parts)
- Test command output
- Steps to reproduce

### Quick Fixes

**Try these in order:**

1. **Restart Claude Code**
2. **Validate configuration:** `python3 scripts/snippets_cli.py validate`
3. **Test pattern:** `python3 scripts/snippets_cli.py test snippet-name "test"`
4. **Check file exists:** `ls scripts/snippets/snippet-name.md`
5. **Recreate snippet:** `/claude-code-snippets:delete-snippet name` then `/claude-code-snippets:create-snippet name`
6. **Reinstall plugin:** Uninstall, then reinstall from marketplace

---

**Related Documentation:**
- [Getting Started](getting-started.md) - Basic setup and usage
- [Configuration](configuration.md) - Configuration system details
- [Commands Reference](commands-reference.md) - Command documentation
- [Template Pattern](template-pattern.md) - Advanced template-based snippets
