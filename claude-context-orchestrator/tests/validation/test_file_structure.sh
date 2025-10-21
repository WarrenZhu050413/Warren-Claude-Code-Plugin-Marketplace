#!/usr/bin/env bash
# Test file structure and organization

set -e

echo "Testing File Structure"
echo "======================================================================"

# Get plugin root dynamically
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PLUGIN_ROOT"

echo "Plugin root: $PLUGIN_ROOT"
echo ""

# Test 1: Core directories exist
echo "✓ Checking core directory structure:"
CORE_DIRS=(
    ".claude-plugin"
    "skills"
    "snippets"
    "commands"
    "scripts"
    "hooks"
    "templates"
    "tests"
)

for dir in "${CORE_DIRS[@]}"; do
    echo -n "  - $dir... "
    if [[ -d "$dir" ]]; then
        echo "PASS"
    else
        echo "FAIL"
        exit 1
    fi
done

# Test 2: Critical files exist
echo ""
echo "✓ Checking critical files:"
CRITICAL_FILES=(
    ".claude-plugin/plugin.json"
    "skills/README.md"
    "skills/ANTHROPIC_SKILLS_LICENSE"
    "skills/ANTHROPIC_SKILLS_NOTICE"
    "scripts/snippet_injector.py"
    "scripts/snippets_cli.py"
    "scripts/config.json"
    "hooks/hooks.json"
    "README.md"
    "LICENSE"
    "CLAUDE.md"
)

for file in "${CRITICAL_FILES[@]}"; do
    echo -n "  - $file... "
    if [[ -f "$file" ]]; then
        echo "PASS"
    else
        echo "FAIL"
        exit 1
    fi
done

# Test 3: Skills directory structure
echo ""
echo "✓ Checking skills directory:"
SKILL_COUNT=$(find skills -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
echo "  - Found $SKILL_COUNT skills"
if [[ $SKILL_COUNT -ge 5 ]]; then
    echo "  - Skill count check: PASS (minimum 5 skills)"
else
    echo "  - Skill count check: FAIL (expected at least 5 skills)"
    exit 1
fi

# List skills
echo "  - Skills found:"
find skills -name "SKILL.md" -exec dirname {} \; | xargs -n1 basename | sort | sed 's/^/    • /'

# Test 4: Snippets directory structure
echo ""
echo "✓ Checking snippets directory:"
if [[ -d "snippets/local" ]]; then
    echo "  - snippets/local exists: PASS"
    SNIPPET_COUNT=$(find snippets/local -name "SNIPPET.md" 2>/dev/null | wc -l | tr -d ' ')
    echo "  - Found $SNIPPET_COUNT local snippets"
else
    echo "  - snippets/local exists: PASS (optional)"
fi

# Test 5: Test directory structure
echo ""
echo "✓ Checking test directory structure:"
TEST_DIRS=(
    "tests/unit"
    "tests/integration"
    "tests/validation"
)

for dir in "${TEST_DIRS[@]}"; do
    echo -n "  - $dir... "
    if [[ -d "$dir" ]]; then
        echo "PASS"
    else
        echo "FAIL"
        exit 1
    fi
done

# Test 6: No test files in scripts directory
echo ""
echo "✓ Checking no test files in scripts directory:"
TEST_FILES_IN_SCRIPTS=$(find scripts -maxdepth 1 -name "test*.py" 2>/dev/null | wc -l | tr -d ' ')
if [[ $TEST_FILES_IN_SCRIPTS -eq 0 ]]; then
    echo "  - No test files in scripts: PASS"
else
    echo "  - Found $TEST_FILES_IN_SCRIPTS test files in scripts: FAIL"
    exit 1
fi

echo ""
echo "======================================================================"
echo "All file structure tests passed!"
