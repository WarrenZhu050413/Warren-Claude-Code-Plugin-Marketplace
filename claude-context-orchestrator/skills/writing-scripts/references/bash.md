# Bash Scripting Reference

Detailed patterns and examples for Bash automation scripts.

## Error Handling

### Essential Settings

Put these at the top of **every** Bash script:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
trap cleanup SIGINT SIGTERM ERR EXIT

cleanup() {
    trap - SIGINT SIGTERM ERR EXIT
    # Cleanup code here (remove temp files, etc.)
}
```

### Flag Breakdown

**`-E` (errtrap):** Error traps work in functions
```bash
trap 'echo "Error"' ERR
func() { false; }  # Trap fires (wouldn't without -E)
```

**`-e` (errexit):** Stop on first error
```bash
command_fails  # Script exits here
never_runs     # Never executes
```

**`-u` (nounset):** Catch undefined variables
```bash
echo "$TYPO"  # Error: TYPO: unbound variable (not silent)
```

**`-o pipefail`:** Detect failures in pipes
```bash
false | true  # Fails (not just last command status)
```

**`trap`:** Run cleanup on exit/error/signal

## String Escaping for LaTeX and Special Characters

**Problem:** Bash interprets escape sequences in double-quoted strings, which corrupts LaTeX commands and special text.

**Dangerous sequences:** `\b` (backspace), `\n` (newline), `\t` (tab), `\r` (return)

### Example Failure

```bash
# ❌ Wrong: Creates backspace character
echo "\\begin{document}" >> file.tex  # Becomes: <backspace>egin{document}
echo "\\bibliographystyle{ACM}" >> file.tex  # Becomes: <backspace>ibliographystyle{ACM}
```

### Safe Approaches

**1. Single quotes** (Best for simple cases):
```bash
echo '\begin{document}' >> file.tex  # ✅ No interpretation
echo '\bibliographystyle{ACM-Reference-Format}' >> file.tex  # ✅ Safe
```

**2. Double backslashes** (When variables needed):
```bash
echo "\\\\begin{document}" >> file.tex  # ✅ 4 backslashes → \b
cmd="begin"
echo "\\\\${cmd}{document}" >> file.tex  # ✅ Works with variables
```

**3. Printf** (More predictable):
```bash
printf '%s\n' '\begin{document}' >> file.tex  # ✅ Literal strings
printf '%s\n' '\bibliographystyle{ACM-Reference-Format}' >> file.tex
```

**4. Heredoc** (Best for multi-line LaTeX):
```bash
cat >> file.tex << 'EOF'  # ✅ Note quoted delimiter
\begin{document}
\section{Title}
\bibliographystyle{ACM-Reference-Format}
\end{document}
EOF
```

### Quick Reference

| Character | Echo double-quotes | Echo single-quotes | Heredoc |
|-----------|-------------------|-------------------|---------|
| `\b` | ❌ Backspace | ✅ Literal | ✅ Literal |
| `\n` | ❌ Newline | ✅ Literal | ✅ Literal |
| `\t` | ❌ Tab | ✅ Literal | ✅ Literal |
| Variables | ✅ Work | ❌ Don't expand | ✅ With `"EOF"` |

**Rule of thumb:** For LaTeX, use single quotes or heredocs to avoid escape sequence interpretation.

## Variable Quoting

### Always Quote Variables

```bash
# ✅ Always quote variables
file="my file.txt"
cat "$file"          # Correct

# ❌ Unquoted breaks on spaces
cat $file            # WRONG: tries to cat "my" and "file.txt"
```

### Array Expansion

```bash
files=("file 1.txt" "file 2.txt")

# ✅ Quote array expansion
for file in "${files[@]}"; do
    echo "$file"
done

# ❌ Unquoted splits on spaces
for file in ${files[@]}; do
    echo "$file"  # WRONG: treats spaces as separators
done
```

## Script Directory Detection

```bash
# Get directory where script is located
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

# Use for relative paths
source "${script_dir}/config.sh"
data_file="${script_dir}/../data/input.txt"
```

## Functions

### Function Template

```bash
# Document functions with comments
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

### Local Variables

Always use `local` for function variables:

```bash
process_data() {
    local data="$1"  # ✅ Local to function
    local result

    result=$(transform "$data")
    echo "$result"
}
```

## Error Messages

### Write Errors to Stderr

```bash
# ✅ Write errors to stderr
echo "Error: File not found" >&2

# ✅ Exit with non-zero code
exit 1

# ❌ Don't write errors to stdout
echo "Error: File not found"
```

### Structured Error Handling

```bash
error() {
    echo "Error: $*" >&2
    exit 1
}

warn() {
    echo "Warning: $*" >&2
}

# Usage
[[ -f "$config" ]] || error "Config file not found: $config"
[[ -w "$output" ]] || warn "Output file not writable: $output"
```

## Checking Commands Exist

```bash
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed" >&2
    exit 1
fi

# Check multiple commands
for cmd in curl jq sed; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "Error: $cmd is required but not installed" >&2
        exit 1
    fi
done
```

## Parallel Processing

```bash
# Run commands in parallel, wait for all
for file in *.txt; do
    process_file "$file" &
done
wait

echo "All files processed"
```

### Parallel with Error Handling

```bash
pids=()
for file in *.txt; do
    process_file "$file" &
    pids+=($!)
done

# Wait and check exit codes
failed=0
for pid in "${pids[@]}"; do
    if ! wait "$pid"; then
        ((failed++))
    fi
done

if [[ $failed -gt 0 ]]; then
    echo "Error: $failed jobs failed" >&2
    exit 1
fi
```

## Configuration Files

### Loading Config

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

### Safe Config Sourcing

```bash
# Validate config before sourcing
validate_config() {
    local config="$1"

    # Check syntax
    if ! bash -n "$config" 2>/dev/null; then
        echo "Error: Invalid syntax in $config" >&2
        return 1
    fi

    return 0
}

if validate_config "$config_file"; then
    source "$config_file"
else
    exit 1
fi
```

## Argument Parsing

### Simple Pattern

```bash
# Parse flags
VERBOSE=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done
```

### Usage Function

```bash
usage() {
    cat << EOF
Usage: $0 [OPTIONS] INPUT OUTPUT

Process files with various options.

OPTIONS:
    -v, --verbose    Verbose output
    -f, --force      Force operation
    -o, --output     Output file
    -h, --help       Show this help

EXAMPLES:
    $0 input.txt output.txt
    $0 -v --force input.txt output.txt
EOF
}

# Show usage on error or -h
[[ "$1" == "-h" || "$1" == "--help" ]] && usage && exit 0
[[ $# -lt 2 ]] && usage && exit 1
```

## Temporary Files

### Safe Temp File Creation

```bash
# Create temp file
tmpfile=$(mktemp)
trap "rm -f '$tmpfile'" EXIT

# Use temp file
curl -s "$url" > "$tmpfile"
process "$tmpfile"

# Cleanup happens automatically via trap
```

### Temp Directory

```bash
# Create temp directory
tmpdir=$(mktemp -d)
trap "rm -rf '$tmpdir'" EXIT

# Use temp directory
download_files "$tmpdir"
process_directory "$tmpdir"
```

## Common Patterns

### File Existence Checks

```bash
# Check file exists
[[ -f "$file" ]] || error "File not found: $file"

# Check directory exists
[[ -d "$dir" ]] || error "Directory not found: $dir"

# Check file readable
[[ -r "$file" ]] || error "File not readable: $file"

# Check file writable
[[ -w "$file" ]] || error "File not writable: $file"
```

### String Comparisons

```bash
# Check empty string
[[ -z "$var" ]] && error "Variable is empty"

# Check non-empty string
[[ -n "$var" ]] || error "Variable not set"

# String equality
[[ "$a" == "$b" ]] && echo "Equal"

# Pattern matching
[[ "$file" == *.txt ]] && echo "Text file"
```

### Numeric Comparisons

```bash
# Greater than
[[ $count -gt 10 ]] && echo "More than 10"

# Less than or equal
[[ $count -le 5 ]] && echo "5 or fewer"

# Equal
[[ $count -eq 0 ]] && echo "Zero"
```

## Common Pitfalls

### ❌ Unquoted Variables

```bash
file=$1
cat $file  # Breaks with spaces
```

### ✅ Always Quote

```bash
file="$1"
cat "$file"
```

### ❌ Escape Sequences in LaTeX

```bash
# Corrupts \begin, \bibitem, etc.
echo "\\begin{document}" >> file.tex  # Creates <backspace>egin
```

### ✅ Use Single Quotes or Heredocs

```bash
echo '\begin{document}' >> file.tex
# Or:
cat >> file.tex << 'EOF'
\begin{document}
EOF
```

### ❌ No Error Handling

```bash
#!/bin/bash
command_that_might_fail
continue_anyway
```

### ✅ Fail Fast

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
command_that_might_fail  # Script exits on failure
```

### ❌ Unvalidated User Input

```bash
rm -rf /$user_input  # DANGER
```

### ✅ Validate Input

```bash
# Validate directory name
if [[ ! "$user_input" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    error "Invalid directory name"
fi
```

## Validation Tools

```bash
# Check syntax
bash -n script.sh

# Static analysis with shellcheck
brew install shellcheck  # macOS
apt install shellcheck   # Ubuntu
shellcheck script.sh

# Run with debug mode
bash -x script.sh
```

## References

- Bash error handling: https://bertvv.github.io/cheat-sheets/Bash.html
- ShellCheck: https://www.shellcheck.net/
- Bash best practices: https://mywiki.wooledge.org/BashGuide
