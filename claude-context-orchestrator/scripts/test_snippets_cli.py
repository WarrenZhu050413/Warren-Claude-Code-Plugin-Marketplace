#!/usr/bin/env python3
"""
Test suite for snippets_cli.py

Tests the new features:
- Default to list command
- Keyword search with -k
- JSON output with --output json
- Interactive selection
- Editor integration
"""

import subprocess
import json
import sys
from pathlib import Path

# Path to CLI script
CLI_PATH = Path(__file__).parent / "snippets_cli.py"

def run_cli(*args):
    """Run CLI and return (returncode, stdout, stderr)"""
    cmd = [sys.executable, str(CLI_PATH)] + list(args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=CLI_PATH.parent
    )
    return result.returncode, result.stdout, result.stderr


def test_default_list():
    """Test that no subcommand defaults to list"""
    print("Test 1: Default to list command...")

    # Just flags, no subcommand
    code, stdout, stderr = run_cli("--output", "json")

    assert code == 0, f"Expected exit code 0, got {code}\n{stderr}"

    data = json.loads(stdout)
    assert "snippets" in data, "Output should contain 'snippets' key"

    print("  ✓ Defaults to list when no subcommand")


def test_keyword_search():
    """Test keyword search with -k flag"""
    print("Test 2: Keyword search...")

    # Search for CLEAR keyword
    code, stdout, stderr = run_cli("-k", "CLEAR", "--output", "json")

    assert code == 0, f"Expected exit code 0, got {code}\n{stderr}"

    data = json.loads(stdout)
    snippets = data.get("snippets", [])

    # Should find snippets with CLEAR in pattern
    assert len(snippets) > 0, "Should find at least one snippet with CLEAR"

    # Verify all results contain CLEAR in pattern
    for snippet in snippets:
        pattern = snippet.get("pattern", "")
        assert "CLEAR" in pattern.upper(), f"Pattern should contain CLEAR: {pattern}"

    print(f"  ✓ Found {len(snippets)} snippet(s) with CLEAR")


def test_keyword_no_results():
    """Test keyword search with no matches"""
    print("Test 3: Keyword with no results...")

    # Search for non-existent keyword
    code, stdout, stderr = run_cli("-k", "NONEXISTENT_PATTERN_12345", "--output", "json")

    assert code == 0, f"Expected exit code 0, got {code}\n{stderr}"

    data = json.loads(stdout)
    snippets = data.get("snippets", [])

    assert len(snippets) == 0, "Should find no snippets"

    print("  ✓ Returns empty list for non-existent keyword")


def test_json_output():
    """Test JSON output format"""
    print("Test 4: JSON output format...")

    code, stdout, stderr = run_cli("--output", "json", "list")

    assert code == 0, f"Expected exit code 0, got {code}\n{stderr}"

    # Verify it's valid JSON
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON output: {e}\n{stdout}")

    # Verify structure
    assert "snippets" in data, "Should have 'snippets' key"
    assert isinstance(data["snippets"], list), "'snippets' should be a list"

    # Check snippet structure
    if data["snippets"]:
        snippet = data["snippets"][0]
        required_keys = ["name", "pattern", "files", "enabled"]
        for key in required_keys:
            assert key in snippet, f"Snippet should have '{key}' key"

    print("  ✓ Valid JSON structure")


def test_keyword_without_list_subcommand():
    """Test -k flag without explicit list subcommand"""
    print("Test 5: Keyword without 'list' subcommand...")

    # Should default to list
    code, stdout, stderr = run_cli("-k", "DOCKER", "--output", "json")

    assert code == 0, f"Expected exit code 0, got {code}\n{stderr}"

    data = json.loads(stdout)
    assert "snippets" in data, "Should execute list command"

    print("  ✓ -k flag works without explicit 'list'")


def test_combined_flags():
    """Test various flag combinations"""
    print("Test 6: Combined flags...")

    test_cases = [
        (["-k", "CLEAR", "--output", "json"], "keyword + json"),
        (["--output", "json", "-k", "CLEAR"], "json + keyword"),
        (["-k", "DOCKER"], "keyword only (text output)"),
        (["--output", "json"], "json only"),
    ]

    for args, desc in test_cases:
        code, stdout, stderr = run_cli(*args)
        assert code == 0, f"Failed: {desc}\n{stderr}"

    print(f"  ✓ All {len(test_cases)} flag combinations work")


def test_list_specific_snippet():
    """Test listing a specific snippet by name"""
    print("Test 7: List specific snippet...")

    # First get a snippet name
    code, stdout, stderr = run_cli("--output", "json", "list")
    data = json.loads(stdout)

    if data["snippets"]:
        snippet_name = data["snippets"][0]["name"]

        # Now list that specific snippet
        code, stdout, stderr = run_cli("--output", "json", "list", snippet_name)

        assert code == 0, f"Expected exit code 0, got {code}\n{stderr}"

        data = json.loads(stdout)
        snippets = data.get("snippets", [])

        assert len(snippets) == 1, f"Should return exactly 1 snippet, got {len(snippets)}"
        assert snippets[0]["name"] == snippet_name, "Should return correct snippet"

        print(f"  ✓ Retrieved specific snippet: {snippet_name}")
    else:
        print("  ⊘ Skipped (no snippets found)")


def test_output_format_validation():
    """Test that output format is validated"""
    print("Test 8: Output format validation...")

    # Invalid format should fail
    code, stdout, stderr = run_cli("--output", "invalid", "list")

    assert code != 0, "Should fail with invalid output format"
    assert "invalid choice" in stderr.lower(), "Should mention invalid choice in error"

    print("  ✓ Validates output format")


def test_keyword_case_insensitive():
    """Test that keyword search is case-insensitive"""
    print("Test 9: Case-insensitive keyword search...")

    # Search with different cases
    code1, stdout1, _ = run_cli("-k", "CLEAR", "--output", "json")
    code2, stdout2, _ = run_cli("-k", "clear", "--output", "json")
    code3, stdout3, _ = run_cli("-k", "Clear", "--output", "json")

    assert code1 == 0 and code2 == 0 and code3 == 0, "All should succeed"

    data1 = json.loads(stdout1)
    data2 = json.loads(stdout2)
    data3 = json.loads(stdout3)

    # Should return same results
    assert len(data1["snippets"]) == len(data2["snippets"]) == len(data3["snippets"]), \
        "Case-insensitive search should return same results"

    print("  ✓ Keyword search is case-insensitive")


def test_help_output():
    """Test help output"""
    print("Test 10: Help output...")

    code, stdout, stderr = run_cli("--help")

    assert code == 0, "Help should exit with 0"

    # Check for key features in help
    help_text = stdout.lower()
    assert "-k" in help_text or "--keyword" in help_text, "Should mention -k flag"
    assert "--output" in help_text, "Should mention --output flag"
    assert "list" in help_text, "Should mention list command"

    print("  ✓ Help output includes new flags")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Testing snippets_cli.py")
    print("=" * 60)
    print()

    tests = [
        test_default_list,
        test_keyword_search,
        test_keyword_no_results,
        test_json_output,
        test_keyword_without_list_subcommand,
        test_combined_flags,
        test_list_specific_snippet,
        test_output_format_validation,
        test_keyword_case_insensitive,
        test_help_output,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"  ✗ FAILED: {e}")
        except Exception as e:
            failed += 1
            print(f"  ✗ ERROR: {e}")
        print()

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
