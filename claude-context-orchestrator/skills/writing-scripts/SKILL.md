---
name: Writing Scripts
description: Best practices for Python and Bash scripting, subprocess patterns, error handling, when to use each language. Use when writing automation scripts, debugging subprocess errors, or choosing between Python and Bash.
---

# Writing Scripts

Best practices for Python and Bash automation scripts with templates and common patterns.

## When to Use Python vs Bash

### Use Bash For

**Simple CLI orchestration** (< 100 lines):
- Piping commands: `grep pattern file | sort | uniq`
- System administration tasks
- Quick file operations
- Environment where Python unavailable

**Performance-critical shell operations**:
- 3-5x faster than Python for CLI utilities
- Minimal overhead for system calls

**Example**: Backup script
```bash
#!/usr/bin/env bash
tar -czf "backup-$(date +%Y%m%d).tar.gz" /important/data
```

### Use Python For

**Complex logic** (> 100 lines):
- Data processing and transformation
- Multiple functions and classes
- Need testing and debugging

**Cross-platform**:
- Works on Windows, Linux, macOS
- Consistent behavior across systems

**Rich ecosystem**:
- Libraries for HTTP, JSON, databases, APIs
- Better error handling and exceptions

**Example**: API automation
```python
import requests
data = requests.get('https://api.example.com/data').json()
for item in data:
    process(item)
```

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
| File processing | ✅ | ✅ |

## Python Best Practices

### Subprocess Patterns

**Two-stage subprocess** (avoid shell parsing issues):

```python
# ❌ Don't: shell=True with complex patterns
cmd = 'curl -s "url" | grep -oE "pattern(with|parens)"'
subprocess.run(cmd, shell=True, ...)

# ✅ Do: Separate calls with input= piping
curl_result = subprocess.run(['curl', '-s', url],
                            capture_output=True, text=True)
grep_result = subprocess.run(['grep', '-oE', pattern],
                            input=curl_result.stdout,
                            capture_output=True, text=True)
```

**Why list arguments work**:
- Python executes command directly (no shell interpretation)
- Arguments passed as literal strings
- Special chars like `|(){}` treated as text, not operators

**When shell=True is needed**:
- Hard-coded commands only
- Need shell features: `*` wildcards, `~` expansion, `&&` operators

### Debugging Subprocess Failures

**Workflow**:
1. Test command in bash first
2. Add debug output:
   ```python
   result = subprocess.run(cmd, ...)
   print(f"stdout: {result.stdout[:100]}")
   print(f"stderr: {result.stderr}")
   print(f"returncode: {result.returncode}")
   ```
3. Check stderr for shell errors
4. Rewrite without shell=True

**Common errors**:
- `syntax error near unexpected token '('` → Shell parsing issue
- `command not found` → PATH issue
- Empty stdout → Command construction error

### Error Handling

```python
import sys
import subprocess

try:
    result = subprocess.run(['command'],
                          capture_output=True,
                          text=True,
                          check=True)  # Raises on non-zero exit
except subprocess.CalledProcessError as e:
    print(f"Error: Command failed with exit code {e.returncode}", file=sys.stderr)
    print(f"stderr: {e.stderr}", file=sys.stderr)
    sys.exit(1)
except FileNotFoundError:
    print("Error: Command not found in PATH", file=sys.stderr)
    sys.exit(1)
```

### Argparse Patterns

**Multi-mode scripts**:
```python
parser = argparse.ArgumentParser(description='Script description')
parser.add_argument('input', nargs='?', help='Input file or topic')
parser.add_argument('--url', help='Direct URL mode')
parser.add_argument('--verify', action='store_true', help='Verify output')
args = parser.parse_args()

# Validate combinations
if not args.input and not args.url:
    parser.error("Provide either input or --url")
```

**Flag patterns**:
```python
parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument('-f', '--force', action='store_true')
parser.add_argument('-o', '--output', default='output.txt')
parser.add_argument('--count', type=int, default=5)
```

### Environment Variables

```python
import os

# ✅ Never hardcode credentials
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    print("Error: API_KEY environment variable not set", file=sys.stderr)
    sys.exit(1)

# ✅ Provide defaults
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
```

## Bash Best Practices

### Error Handling

**Essential settings** (put at top of every script):
```bash
#!/usr/bin/env bash
set -Eeuo pipefail  # Exit on error, undefined vars, pipe failures
trap cleanup SIGINT SIGTERM ERR EXIT

cleanup() {
    trap - SIGINT SIGTERM ERR EXIT
    # Cleanup code here (remove temp files, etc.)
}
```

**Flag breakdown**:

`-E` (errtrap): Error traps work in functions
```bash
trap 'echo "Error"' ERR
func() { false; }  # Trap fires (wouldn't without -E)
```

`-e` (errexit): Stop on first error
```bash
command_fails  # Script exits here
never_runs     # Never executes
```

`-u` (nounset): Catch undefined variables
```bash
echo "$TYPO"  # Error: TYPO: unbound variable (not silent)
```

`-o pipefail`: Detect failures in pipes
```bash
false | true  # Fails (not just last command status)
```

`trap`: Run cleanup on exit/error/signal

### Script Directory Detection

```bash
# Get directory where script is located
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

# Use for relative paths
source "${script_dir}/config.sh"
```

### Functions

```bash
# Document functions
# Args:
#   $1 - input file
#   $2 - output file
# Returns:
#   0 on success, 1 on error
process_file() {
    local input="$1"
    local output="$2"

    if [[ ! -f "$input" ]]; then
        echo "Error: Input file not found: $input" >&2
        return 1
    fi

    # Process file
    grep pattern "$input" > "$output"
}

# Call function
if process_file "input.txt" "output.txt"; then
    echo "Success"
else
    echo "Failed" >&2
    exit 1
fi
```

### Error Messages

```bash
# ✅ Write errors to stderr
echo "Error: File not found" >&2

# ✅ Exit with non-zero code
exit 1

# ❌ Don't write errors to stdout
echo "Error: File not found"
```

### Variable Quoting

```bash
# ✅ Always quote variables
file="my file.txt"
cat "$file"          # Correct
cat "$file"          # Correct

# ❌ Unquoted breaks on spaces
cat $file            # WRONG: tries to cat "my" and "file.txt"
```

### Checking Commands Exist

```bash
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed" >&2
    exit 1
fi
```

## Templates

### Python Script Template

See: `scripts/python/template.py`

Features:
- Argparse setup
- Logging configuration
- Error handling
- Main function pattern

### Bash Script Template

See: `scripts/bash/template.sh`

Features:
- Error handling (set -Eeuo pipefail)
- Trap for cleanup
- Script directory detection
- Function examples
- Argument parsing

## Common Patterns

### Python: URL Verification

```python
import subprocess

def verify_url(url: str) -> bool:
    """Verify URL is accessible with HTTP HEAD request."""
    result = subprocess.run(['curl', '-I', '-s', url],
                          capture_output=True, text=True)

    if 'HTTP/2 200' in result.stdout or 'HTTP/1.1 200' in result.stdout:
        if 'content-type:' in result.stdout.lower():
            return True
    return False
```

### Python: File Processing

```python
def process_files(pattern: str) -> list[str]:
    """Find and process files matching pattern."""
    import glob

    files = glob.glob(pattern)
    results = []

    for file in files:
        try:
            with open(file, 'r') as f:
                content = f.read()
                # Process content
                results.append(process(content))
        except IOError as e:
            print(f"Error reading {file}: {e}", file=sys.stderr)

    return results
```

### Bash: Parallel Processing

```bash
# Run commands in parallel, wait for all
for file in *.txt; do
    process_file "$file" &
done
wait

echo "All files processed"
```

### Bash: Configuration File

```bash
# Load config file if exists
config_file="${script_dir}/config.sh"
if [[ -f "$config_file" ]]; then
    source "$config_file"
else
    # Default values
    LOG_DIR="/var/log"
    BACKUP_DIR="/backup"
fi
```

## Automation Script Patterns

### Safety-First Operations

**Dry-Run Mode** - Preview changes before applying:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--force', action='store_true',
                   help='Apply changes (dry-run by default)')
args = parser.parse_args()

dry_run = not args.force

# Use dry_run flag throughout script
for item in items:
    change_description = f"Would rename {item['old']} → {item['new']}"

    if dry_run:
        print(f"→ {change_description}")
    else:
        print(f"✓ {change_description}")
        apply_change(item)
```

**Why this matters**: Bulk operations on configs/files need risk-free preview. Running with dry-run first builds confidence before `--force` mode.

### Backup-First Pattern

Automatic backups prevent data loss:

```python
from datetime import datetime
import shutil

def backup_before_modify(config_path):
    """Create timestamped backup before modifications."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{config_path}.backup.{timestamp}"

    shutil.copy2(config_path, backup_path)
    print(f"✓ Backup created: {backup_path}")

    return backup_path

# Use in operations
if not dry_run:
    backup_before_modify(config_path)
    # Now safe to modify original
    update_config(config_path)
```

### Config-as-Code Management

Use CLI tools for config modifications instead of manual editing:

```python
# ❌ Bad: Users manually edit JSON
# Causes: syntax errors, conflicts, no validation

# ✅ Good: CLI for all config changes
# Example: python3 config_cli.py update name --pattern "new-pattern"

def cli_update_config(name, pattern, file=None):
    """Update config via validated CLI."""
    config = load_config()

    # Validate pattern format
    if not validate_pattern(pattern):
        raise ValueError(f"Invalid pattern: {pattern}")

    # Check for conflicts
    if pattern_exists_elsewhere(pattern, config):
        raise ValueError(f"Pattern conflict: {pattern}")

    # Update with safety checks
    entry = config['mappings'].find(lambda x: x['name'] == name)
    entry['pattern'] = pattern
    if file:
        entry['snippet'] = [file]

    save_config(config)
    return entry
```

**Benefits**:
- ✅ Validation prevents JSON syntax errors
- ✅ Conflict detection prevents duplicates
- ✅ Automatic backups before changes
- ✅ Audit trail of all modifications

### Self-Documenting Scripts

Output tells the story of what the script does:

```python
# ✅ Good: Script output is the specification
print("=" * 70)
print("CONFIGURATION MIGRATION")
print("=" * 70)
print()

print("Step 1: Analyzing input files")
print("-" * 70)
files = find_files()
print(f"Found: {len(files)} files")
for f in files[:5]:
    print(f"  • {f}")
print()

print("Step 2: Validating configuration")
print("-" * 70)
errors = validate_config()
if errors:
    print(f"✗ Found {len(errors)} errors")
    for error in errors:
        print(f"  • {error}")
else:
    print("✓ Configuration valid")
```

This approach makes the script **self-reporting**: users see exactly what happens without separate docs.

## Validation Tools

### Python

```bash
# Check syntax
python3 -m py_compile script.py

# Lint with pylint
pip install pylint
pylint script.py

# Format with black
pip install black
black script.py

# Type check with mypy
pip install mypy
mypy script.py
```

### Bash

```bash
# Check syntax
bash -n script.sh

# Static analysis with shellcheck
brew install shellcheck  # macOS
shellcheck script.sh

# Run with debug mode
bash -x script.sh
```

## Real Examples

**Python automation**: `skills/fetching-images/scripts/fetch_wikimedia_image.py`
- Two-stage subprocess pattern
- Argparse with optional arguments
- URL verification
- Multi-mode operation

**Bash template**: `scripts/bash/template.sh`
- Error handling
- Cleanup trap
- Function structure

## Common Pitfalls

### Python

❌ **Using shell=True unnecessarily**
```python
# Vulnerable and error-prone
subprocess.run(f'rm -rf {user_input}', shell=True)  # DANGER
```

✅ **Use list arguments**
```python
subprocess.run(['rm', '-rf', user_input])  # Safe
```

❌ **Not handling encoding**
```python
result = subprocess.run(['cmd'], capture_output=True)
print(result.stdout)  # bytes, not string
```

✅ **Specify text=True**
```python
result = subprocess.run(['cmd'], capture_output=True, text=True)
print(result.stdout)  # string
```

### Bash

❌ **Unquoted variables**
```bash
file=$1
cat $file  # Breaks with spaces
```

✅ **Always quote**
```bash
file="$1"
cat "$file"
```

❌ **No error handling**
```bash
#!/bin/bash
command_that_might_fail
continue_anyway
```

✅ **Fail fast**
```bash
#!/usr/bin/env bash
set -Eeuo pipefail
command_that_might_fail  # Script exits on failure
```

## References

- Python subprocess: https://docs.python.org/3/library/subprocess.html
- Bash error handling: https://bertvv.github.io/cheat-sheets/Bash.html
- ShellCheck: https://www.shellcheck.net/
- Real Python subprocess guide: https://realpython.com/python-subprocess/
