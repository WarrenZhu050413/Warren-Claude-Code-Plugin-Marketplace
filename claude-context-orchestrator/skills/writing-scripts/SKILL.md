---
name: Writing Scripts
description: Best practices for writing automation scripts in Python and Bash. Use when writing automation scripts, choosing between languages, debugging subprocess errors, or implementing error handling patterns. Load language-specific references as needed.
---

# Writing Scripts

Best practices for Python and Bash automation scripts with language-specific references for deep-dive topics.

## When to Use This Skill

Use this skill when:
- Writing new automation scripts (Python or Bash)
- Debugging subprocess errors and shell parsing issues
- Implementing error handling and validation patterns
- Choosing between Python and Bash for a task
- Setting up script templates with proper structure

## Quick Decision: Python vs Bash

### Use Bash For
- **Simple CLI orchestration** (< 100 lines)
- Piping commands: `grep pattern file | sort | uniq`
- System administration tasks
- Quick file operations
- **Performance-critical shell operations** (3-5x faster than Python)

### Use Python For
- **Complex logic** (> 100 lines)
- Data processing and transformation
- Cross-platform compatibility
- API calls and HTTP requests
- Testing and debugging requirements

### Decision Matrix

| Task | Bash | Python |
|------|------|--------|
| Chain CLI tools | ✅ | ❌ |
| < 100 lines | ✅ | 🟡 |
| Data manipulation | ❌ | ✅ |
| Cross-platform | ❌ | ✅ |
| Testing needed | ❌ | ✅ |
| Complex logic | ❌ | ✅ |
| API calls | 🟡 | ✅ |

## Core Principles

### 1. Safety First
- Always implement error handling (Python: try/except, Bash: set -Eeuo pipefail)
- Provide dry-run mode for destructive operations
- Create automatic backups before modifications
- Validate inputs and check for required commands

### 2. Self-Documenting Output
- Print clear progress messages
- Show what the script is doing at each step
- Use structured output (headers, separators)
- Write errors to stderr, not stdout

### 3. Maintainability
- Keep scripts under 500 lines (split if larger)
- Use functions for repeated logic
- Document non-obvious patterns
- Include usage examples in help text

## Language-Specific References

For detailed patterns and examples, read the appropriate reference file:

### Python Reference (`references/python.md`)

Load when working with Python scripts. Contains:
- Subprocess patterns (two-stage, avoiding shell=True)
- Debugging subprocess failures
- Error handling with try/except
- Argparse patterns for CLI arguments
- Environment variable management
- File processing patterns
- URL verification examples
- Common pitfalls and solutions

**Read this when:** Writing Python scripts, debugging subprocess issues, setting up CLI arguments

### Bash Reference (`references/bash.md`)

Load when working with Bash scripts. Contains:
- Error handling (set -Eeuo pipefail, trap)
- String escaping for LaTeX and special characters
- Variable quoting rules
- Function patterns and documentation
- Script directory detection
- Configuration file loading
- Parallel processing patterns
- Common pitfalls (unquoted variables, escape sequences)

**Read this when:** Writing Bash scripts, handling LaTeX generation, debugging string escaping issues

## Common Patterns Across Languages

### Dry-Run Mode

Provide a way to preview changes before applying:

**Python:**
```python
parser.add_argument('--force', action='store_true',
                   help='Apply changes (dry-run by default)')
args = parser.parse_args()
dry_run = not args.force

if dry_run:
    print(f"→ Would rename {old} → {new}")
else:
    print(f"✓ Renamed {old} → {new}")
    apply_change()
```

**Bash:**
```bash
DRY_RUN=true
[[ "${1}" == "--force" ]] && DRY_RUN=false

if $DRY_RUN; then
    echo "→ Would delete $file"
else
    echo "✓ Deleted $file"
    rm "$file"
fi
```

### Automatic Backups

Create timestamped backups before modifications:

**Python:**
```python
from datetime import datetime
import shutil

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_path = f"{config_path}.backup.{timestamp}"
shutil.copy2(config_path, backup_path)
print(f"✓ Backup created: {backup_path}")
```

**Bash:**
```bash
backup_file="${config}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$config" "$backup_file"
echo "✓ Backup created: $backup_file"
```

### Check Required Commands

**Python:**
```python
import shutil
if not shutil.which('jq'):
    print("Error: jq is required but not installed", file=sys.stderr)
    sys.exit(1)
```

**Bash:**
```bash
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed" >&2
    exit 1
fi
```

## Validation Tools

### Python
```bash
python3 -m py_compile script.py  # Check syntax
pylint script.py                 # Lint
black script.py                  # Format
mypy script.py                   # Type check
```

### Bash
```bash
bash -n script.sh      # Check syntax
shellcheck script.sh   # Static analysis
bash -x script.sh      # Debug mode
```

## How to Use This Skill

1. **Start here** - Use the decision matrix to choose Python or Bash
2. **Read language reference** - Load `references/python.md` or `references/bash.md` for detailed patterns
3. **Apply core principles** - Implement safety, documentation, and maintainability patterns
4. **Validate** - Run syntax checkers and linters before using the script

The references contain detailed code examples, debugging workflows, and common pitfalls specific to each language. Load them as needed to avoid cluttering context when working on single-language scripts.
