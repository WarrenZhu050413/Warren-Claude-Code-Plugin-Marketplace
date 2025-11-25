# Snippet Injection System Testing

## Overview

The snippet injection system automatically injects contextual snippets into Claude's prompts based on keyword matching. This test suite validates the entire system.

## Running Tests

```bash
cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/scripts/snippets
python3 test_snippets.py
```

## Test Coverage

The test suite runs 5 comprehensive tests:

### Test 1: File Existence
- ✓ Validates all snippet files referenced in config exist
- ✓ Checks both enabled and disabled snippets
- ✓ Reports missing files with full paths

### Test 2: Regex Pattern Validation
- ✓ Verifies all regex patterns compile correctly
- ✓ Tests pattern matching against sample keywords
- ✓ Validates expected matches for common keywords:
  - SCREENSHOT → screenshot-workflow
  - HTML → generating-html
  - SEARCH → search-cli
  - NVIM → nvim
  - SNIPPET → managing-snippets
  - TODO → add-todo

### Test 3: Full Injection Flow
- ✓ Runs `snippet_injector.py` with test prompts
- ✓ Validates JSON output structure
- ✓ Confirms content injection when keywords present
- ✓ Confirms no injection when no keywords match

### Test 4: Config Merging
- ✓ Tests multi-config priority system
- ✓ Validates config.json (priority 0) and config.local.json (priority 100)
- ✓ Confirms higher priority configs override lower ones

### Test 5: Content Loading
- ✓ Loads actual snippet file content
- ✓ Validates files are readable and not empty
- ✓ Reports file sizes for verification
- ✓ Detects encoding issues

## Expected Results

All tests should pass:
```
Overall: 5/5 tests passed
All tests passed! ✓
```

Current status:
- **51 enabled snippets** (all working)
- **3 disabled snippets** (test-snippet, override-test, pbcopy)
- **0 encoding errors**

## Common Issues

### Encoding Errors
If you see UTF-8 codec errors, fix with:
```bash
iconv -f ISO-8859-1 -t UTF-8 file.md > file_fixed.md
mv file_fixed.md file.md
```

### Path Resolution Errors
Ensure paths in config are relative to `claude-context-orchestrator/`:
- ✓ Correct: `snippets/local/...` or `skills/...`
- ✗ Wrong: `../../snippets/local/...`

### Pattern Not Matching
Check regex escaping in config.local.json:
- Use `\\b` for word boundaries (not `\b`)
- Test patterns: `python3 -c "import re; print(re.search(r'\\bKEYWORD\\b', 'test KEYWORD here'))"`

## Configuration Files

- `config.json`: Base configuration (priority 0, currently empty)
- `config.local.json`: Local overrides (priority 100, active config)
- `snippet_injector.py`: Main injection script
- `test_snippets.py`: This test suite

## Adding New Snippets

1. Create snippet file in appropriate location:
   ```bash
   mkdir -p snippets/local/category/my-snippet
   vim snippets/local/category/my-snippet/SKILL.md
   ```

2. Add mapping to `config.local.json`:
   ```json
   {
     "name": "my-snippet",
     "pattern": "\\b(KEYWORD)\\b[.,;:!?]?",
     "snippet": ["snippets/local/category/my-snippet/SKILL.md"],
     "separator": "\n",
     "enabled": true
   }
   ```

3. Run tests to validate:
   ```bash
   python3 test_snippets.py
   ```

4. Test keyword in actual prompt:
   ```bash
   echo '{"prompt": "KEYWORD test"}' | python3 snippet_injector.py
   ```

## Debugging

Enable verbose output:
```bash
# Test specific snippet
echo '{"prompt": "SCREENSHOT test"}' | python3 snippet_injector.py 2>&1 | jq

# Check which snippets match
python3 <<'EOF'
import json, re
from pathlib import Path

config_path = Path("config.local.json")
with open(config_path) as f:
    config = json.load(f)

prompt = "YOUR TEST PROMPT HERE"
for mapping in config["mappings"]:
    if re.search(mapping["pattern"], prompt):
        print(f"Matched: {mapping['name']}")
EOF
```

## Maintenance

Run tests after:
- Modifying `snippet_injector.py`
- Adding/removing snippets
- Changing regex patterns
- Moving snippet files
- Updating config files

## CI/CD Integration

To integrate into CI/CD:
```bash
# Run tests and exit with proper code
python3 test_snippets.py
if [ $? -eq 0 ]; then
    echo "✓ All snippet tests passed"
else
    echo "✗ Snippet tests failed"
    exit 1
fi
```
