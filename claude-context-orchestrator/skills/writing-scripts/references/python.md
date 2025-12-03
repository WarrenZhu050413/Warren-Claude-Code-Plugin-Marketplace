# Python Scripting Reference

Detailed patterns and examples for Python automation scripts.

## Subprocess Patterns

### Two-Stage Subprocess (Avoid Shell Parsing)

**Problem:** Using `shell=True` with complex patterns causes shell parsing issues.

**❌ Don't: shell=True with complex patterns**
```python
cmd = 'curl -s "url" | grep -oE "pattern(with|parens)"'
subprocess.run(cmd, shell=True, ...)
```

**✅ Do: Separate calls with input= piping**
```python
curl_result = subprocess.run(['curl', '-s', url],
                            capture_output=True, text=True)
grep_result = subprocess.run(['grep', '-oE', pattern],
                            input=curl_result.stdout,
                            capture_output=True, text=True)
```

### Why List Arguments Work

- Python executes command directly (no shell interpretation)
- Arguments passed as literal strings
- Special chars like `|(){}` treated as text, not operators

### When shell=True Is Needed

Only use for hard-coded commands that require shell features:
- `*` wildcards
- `~` home directory expansion
- `&&` operators
- Environment variable expansion

```python
# Hard-coded command only
subprocess.run('ls *.txt | wc -l', shell=True, ...)
```

## Debugging Subprocess Failures

### Workflow

1. **Test command in bash first** - Verify it works outside Python
2. **Add debug output:**
   ```python
   result = subprocess.run(cmd, ...)
   print(f"stdout: {result.stdout[:100]}")
   print(f"stderr: {result.stderr}")
   print(f"returncode: {result.returncode}")
   ```
3. **Check stderr for shell errors** - Syntax errors indicate shell parsing issues
4. **Rewrite without shell=True** - Use list arguments and two-stage pattern

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `syntax error near unexpected token '('` | Shell parsing regex/parens | Two-stage subprocess |
| `command not found` | PATH issue or typo | Check command exists with `which` |
| Empty stdout | Command construction error | Debug with stderr output |

### Debugging Invisible Characters

**Problem:** Files with invisible characters (backspace, null bytes) cause mysterious errors.

**Symptoms:**
- LaTeX: `Unicode character ^^H (U+0008) not set up for use with LaTeX`
- Commands fail with "invalid character" but file looks normal

**Detection:**
```bash
# Show all characters including invisible ones
od -c file.txt

# Check specific line range
sed -n '10,20p' file.txt | od -c

# Find backspaces
grep -P '\x08' file.txt
```

**Example output:**
```
0000000    %   %       f   i   l   e   .  \n  \b   \   b   e   g   i
                                            ^^^ backspace character
```

**Fix:**
```bash
# Remove all backspace characters
tr -d '\b' < corrupted.tex > clean.tex

# Remove all control characters (preserve newlines)
tr -cd '[:print:]\n' < file.txt > clean.txt
```

**Prevention:** Use proper quoting when generating files (see Bash reference for LaTeX string escaping).

## Error Handling

### Basic Pattern

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

### File Operations

```python
try:
    with open(file_path, 'r') as f:
        content = f.read()
except FileNotFoundError:
    print(f"Error: File not found: {file_path}", file=sys.stderr)
    sys.exit(1)
except PermissionError:
    print(f"Error: Permission denied: {file_path}", file=sys.stderr)
    sys.exit(1)
except IOError as e:
    print(f"Error reading file: {e}", file=sys.stderr)
    sys.exit(1)
```

## Argparse Patterns

### Multi-Mode Scripts

```python
import argparse

parser = argparse.ArgumentParser(description='Script description')
parser.add_argument('input', nargs='?', help='Input file or topic')
parser.add_argument('--url', help='Direct URL mode')
parser.add_argument('--verify', action='store_true', help='Verify output')
args = parser.parse_args()

# Validate combinations
if not args.input and not args.url:
    parser.error("Provide either input or --url")
```

### Common Flag Patterns

```python
parser.add_argument('-v', '--verbose', action='store_true',
                   help='Verbose output')
parser.add_argument('-f', '--force', action='store_true',
                   help='Force operation')
parser.add_argument('-o', '--output', default='output.txt',
                   help='Output file')
parser.add_argument('--count', type=int, default=5,
                   help='Number of items')
parser.add_argument('--config', type=str,
                   help='Config file path')
```

### Mutually Exclusive Groups

```python
group = parser.add_mutually_exclusive_group()
group.add_argument('--json', action='store_true')
group.add_argument('--yaml', action='store_true')
```

## Environment Variables

```python
import os

# ✅ Never hardcode credentials
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    print("Error: API_KEY environment variable not set", file=sys.stderr)
    sys.exit(1)

# ✅ Provide defaults
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', './output')

# ✅ Type conversion with defaults
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
TIMEOUT = float(os.getenv('TIMEOUT', '30.0'))
```

## File Processing Patterns

### Process Files Matching Pattern

```python
import glob
import sys

def process_files(pattern: str) -> list[str]:
    """Find and process files matching pattern."""
    files = glob.glob(pattern, recursive=True)
    results = []

    for file in files:
        try:
            with open(file, 'r') as f:
                content = f.read()
                results.append(process(content))
        except IOError as e:
            print(f"Error reading {file}: {e}", file=sys.stderr)

    return results
```

### Safe File Writing

```python
import tempfile
import shutil

def safe_write(file_path: str, content: str):
    """Write to temp file first, then atomic move."""
    # Write to temp file in same directory
    dir_name = os.path.dirname(file_path)
    with tempfile.NamedTemporaryFile(mode='w', dir=dir_name,
                                     delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    # Atomic move
    shutil.move(tmp_path, file_path)
```

## URL Verification

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

## Automation Script Patterns

### Dry-Run Mode

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

### Backup-First Pattern

```python
from datetime import datetime
import shutil

def backup_before_modify(config_path: str) -> str:
    """Create timestamped backup before modifications."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{config_path}.backup.{timestamp}"

    shutil.copy2(config_path, backup_path)
    print(f"✓ Backup created: {backup_path}")

    return backup_path

# Use in operations
if not dry_run:
    backup_before_modify(config_path)
    update_config(config_path)
```

### Self-Documenting Output

```python
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

## Common Pitfalls

### ❌ Using shell=True Unnecessarily

```python
# Vulnerable and error-prone
subprocess.run(f'rm -rf {user_input}', shell=True)  # DANGER
```

### ✅ Use List Arguments

```python
subprocess.run(['rm', '-rf', user_input])  # Safe
```

### ❌ Not Handling Encoding

```python
result = subprocess.run(['cmd'], capture_output=True)
print(result.stdout)  # bytes, not string
```

### ✅ Specify text=True

```python
result = subprocess.run(['cmd'], capture_output=True, text=True)
print(result.stdout)  # string
```

### ❌ Ignoring Errors

```python
result = subprocess.run(['cmd'])
# No error handling
```

### ✅ Check Exit Code

```python
result = subprocess.run(['cmd'], capture_output=True, text=True)
if result.returncode != 0:
    print(f"Error: {result.stderr}", file=sys.stderr)
    sys.exit(1)
```

## Validation Tools

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

## References

- Python subprocess docs: https://docs.python.org/3/library/subprocess.html
- Real Python subprocess guide: https://realpython.com/python-subprocess/
- Argparse tutorial: https://docs.python.org/3/howto/argparse.html
