#!/bin/bash
# Test Suite for Snippet: nvim
# Pattern: \b(nvim|neovim|vim\s+(config|configuration|setup)|\.vimrc|init\.vim|init\.lua)\b
# Verification Hash: nvim_wzhu_config

SNIPPET_NAME="nvim"
TEST_KEYWORD="nvim"
VERIFICATION_TEXT="~/.config/nvim"
TESTS_PASSED=0
TESTS_FAILED=0
# Get plugin root from CLAUDE_PLUGIN_ROOT env var, or use relative path from script location
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"

echo "🧪 Testing Snippet: $SNIPPET_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test 1: Snippet file exists
echo "Test 1: Checking snippet file exists..."
if [ -f "$PLUGIN_ROOT/scripts/snippets/nvim.md" ]; then
    echo "  ✅ PASS"
    ((TESTS_PASSED++))
else
    echo "  ❌ FAIL"
    ((TESTS_FAILED++))
fi

# Test 2: Snippet listed
echo "Test 2: Checking snippet is listed..."
if cd "$PLUGIN_ROOT/scripts" && python3 snippets_cli.py list | grep -q "$SNIPPET_NAME"; then
    echo "  ✅ PASS"
    ((TESTS_PASSED++))
else
    echo "  ❌ FAIL"
    ((TESTS_FAILED++))
fi

# Test 3: Pattern matching test
echo "Test 3: Testing pattern matching..."
if cd "$PLUGIN_ROOT/scripts" && python3 snippets_cli.py test "$SNIPPET_NAME" "Tell me about $TEST_KEYWORD configuration" 2>&1 | grep -q "matched"; then
    echo "  ✅ PASS"
    ((TESTS_PASSED++))
else
    echo "  ❌ FAIL"
    ((TESTS_FAILED++))
fi

# Test 4: Content verification
echo "Test 4: Verifying snippet content..."
if grep -q "$VERIFICATION_TEXT" "$PLUGIN_ROOT/scripts/snippets/nvim.md"; then
    echo "  ✅ PASS"
    ((TESTS_PASSED++))
else
    echo "  ❌ FAIL"
    ((TESTS_FAILED++))
fi

echo ""
echo "Results: ✅ $TESTS_PASSED passed, ❌ $TESTS_FAILED failed"

[ $TESTS_FAILED -eq 0 ] && echo "🎉 All tests passed!" || echo "⚠️  Some tests failed"
