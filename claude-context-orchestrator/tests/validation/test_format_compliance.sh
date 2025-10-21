#!/usr/bin/env bash
# Test format compliance for snippets and skills

set -e

# Get plugin root dynamically
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PLUGIN_ROOT"

echo "Testing Format Compliance"
echo "======================================================================"

# Test 1: All SNIPPET.md files have required YAML frontmatter
echo "✓ Checking YAML frontmatter in snippets:"
FAILED=0
SNIPPET_COUNT=0

while IFS= read -r file; do
    ((SNIPPET_COUNT++))

    # Check for description
    if ! grep -q "^description:" "$file"; then
        echo "  FAIL: Missing 'description' in $file"
        FAILED=1
    fi

    # Check for SNIPPET_NAME
    if ! grep -q "^SNIPPET_NAME:" "$file"; then
        echo "  FAIL: Missing 'SNIPPET_NAME' in $file"
        FAILED=1
    fi

    # Check for ANNOUNCE_USAGE (optional but recommended)
    if ! grep -q "^ANNOUNCE_USAGE:" "$file"; then
        # This is just a warning, not a failure
        : # no-op
    fi
done < <(find snippets -name "SNIPPET.md" -o -name "*.md" | grep -v "/README.md")

if [[ $FAILED -eq 0 ]]; then
    echo "  PASS: All $SNIPPET_COUNT snippets have required frontmatter"
else
    exit 1
fi

# Test 2: All SKILL.md files have required YAML frontmatter
echo "✓ Checking YAML frontmatter in skills:"
FAILED=0
SKILL_COUNT=0

while IFS= read -r file; do
    ((SKILL_COUNT++))

    # Check for name
    if ! grep -q "^name:" "$file"; then
        echo "  FAIL: Missing 'name' in $file"
        FAILED=1
    fi

    # Check for description
    if ! grep -q "^description:" "$file"; then
        echo "  FAIL: Missing 'description' in $file"
        FAILED=1
    fi
done < <(find skills -name "SKILL.md")

if [[ $FAILED -eq 0 ]]; then
    echo "  PASS: All $SKILL_COUNT skills have required frontmatter"
else
    exit 1
fi

# Test 3: plugin.json is valid JSON
echo "✓ Checking plugin.json validity:"
if python3 -m json.tool .claude-plugin/plugin.json > /dev/null 2>&1; then
    echo "  PASS: plugin.json is valid JSON"
else
    echo "  FAIL: plugin.json is invalid JSON"
    exit 1
fi

# Test 4: config.json is valid JSON
echo "✓ Checking config.json validity:"
if python3 -m json.tool scripts/config.json > /dev/null 2>&1; then
    echo "  PASS: config.json is valid JSON"
else
    echo "  FAIL: config.json is invalid JSON"
    exit 1
fi

# Test 5: hooks.json is valid JSON
echo "✓ Checking hooks.json validity:"
if python3 -m json.tool hooks/hooks.json > /dev/null 2>&1; then
    echo "  PASS: hooks.json is valid JSON"
else
    echo "  FAIL: hooks.json is invalid JSON"
    exit 1
fi

# Test 6: No trailing whitespace in key files (optional check)
echo "✓ Checking for common formatting issues:"
if find . -name "*.md" -not -path "*/test_env/*" -not -path "*/.git/*" -exec grep -l "[[:space:]]$" {} \; 2>/dev/null | head -1 | grep -q .; then
    echo "  WARNING: Found trailing whitespace in some markdown files (non-critical)"
else
    echo "  PASS: No trailing whitespace found"
fi

echo "======================================================================"
echo "All format compliance tests passed!"
