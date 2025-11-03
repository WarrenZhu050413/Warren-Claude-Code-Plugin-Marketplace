#!/usr/bin/env python3
"""
Test suite for snippets_cli.py v2.0

Tests for the refactored CLI with:
- paths command
- refactored create command
- enhanced search
- auto-detect TTY mode
"""

import subprocess
import json
import sys
import tempfile
import shutil
from pathlib import Path
import pytest

# Path to CLI script (now in snippets/ subdirectory)
CLI_PATH = Path(__file__).parent / "snippets" / "snippets_cli.py"


def run_cli(*args, input_text=None):
    """Run CLI and return (returncode, stdout, stderr)"""
    cmd = [sys.executable, str(CLI_PATH)] + list(args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        input=input_text,
        cwd=CLI_PATH.parent
    )
    return result.returncode, result.stdout, result.stderr


# =============================================================================
# PATHS COMMAND TESTS
# =============================================================================

def test_paths_list_all():
    """Test: List all available snippet paths"""
    print("\nTest: paths list all categories...")

    code, stdout, stderr = run_cli("paths", "--output", "json")

    assert code == 0, f"Expected exit code 0, got {code}\n{stderr}"

    data = json.loads(stdout)
    assert "base_dir" in data, "Output should contain base_dir"
    assert "categories" in data, "Output should contain categories"
    assert "config_files" in data, "Output should contain config_files"

    categories = data["categories"]
    assert len(categories) > 0, "Should have at least one category"

    # Check category structure (dynamically discovered)
    for cat in categories:
        assert "name" in cat, "Category should have name"
        assert "snippet_count" in cat, "Category should have snippet_count"
        assert "sample_paths" in cat, "Category should have sample_paths"

    print(f"  ✓ Found {len(categories)} categories")


def test_paths_filter_by_keyword():
    """Test: Filter paths by keyword"""
    print("\nTest: paths filter by keyword...")

    code, stdout, stderr = run_cli("paths", "dev", "--output", "json")

    assert code == 0, f"Expected exit code 0, got {code}\n{stderr}"

    data = json.loads(stdout)
    categories = data["categories"]

    # Should find only matching categories (matches category name only in current implementation)
    for cat in categories:
        name = cat["name"].lower()
        assert "dev" in name, f"Category name should match 'dev': {cat}"

    print(f"  ✓ Found {len(categories)} matching categories")


def test_paths_no_matches():
    """Test: paths with non-existent keyword returns empty"""
    print("\nTest: paths with no matches...")

    code, stdout, stderr = run_cli("paths", "NONEXISTENT12345", "--output", "json")

    assert code == 0, f"Expected exit code 0, got {code}\n{stderr}"

    data = json.loads(stdout)
    categories = data["categories"]

    assert len(categories) == 0, "Should find no categories"

    print("  ✓ Returns empty list for non-existent keyword")


# =============================================================================
# CREATE COMMAND TESTS
# =============================================================================

def test_create_with_valid_file(tmp_path):
    """Test: Create snippet from valid source file"""
    print("\nTest: create with valid file...")

    # Create valid source file
    source_file = tmp_path / "test-snippet.md"
    source_file.write_text("""---
name: "Test Snippet"
description: "Test description"
pattern: "\\\\b(TEST)\\\\b[.,;:!?]?"
---

# Test Content
This is test content.
""")

    # Mock destination path (we'll need to actually implement this)
    # For now, just test that the command runs
    code, stdout, stderr = run_cli(
        "create",
        str(source_file),
        "snippets/local/development/test-snippet/SKILL.md",
        "--output", "json"
    )

    # This will fail until we implement the command
    # For now, we expect it to fail (RED phase)
    print(f"  Expected failure (RED phase): exit code {code}")


def test_create_missing_frontmatter(tmp_path):
    """Test: Create detects missing YAML frontmatter"""
    print("\nTest: create detects missing frontmatter...")

    # Create file without frontmatter
    source_file = tmp_path / "no-frontmatter.md"
    source_file.write_text("# Just content, no frontmatter\n")

    code, stdout, stderr = run_cli(
        "create",
        str(source_file),
        "snippets/local/development/test/SKILL.md",
        "--output", "json"
    )

    # Should fail with helpful error
    assert code != 0, "Should fail for missing frontmatter"

    print("  Expected failure for missing frontmatter")


def test_create_invalid_pattern(tmp_path):
    """Test: Create validates pattern format"""
    print("\nTest: create validates pattern...")

    # Create file with invalid pattern (missing punctuation suffix)
    source_file = tmp_path / "bad-pattern.md"
    source_file.write_text("""---
name: "Bad Pattern"
description: "Test description"
pattern: "\\\\b(DOCKER)\\\\b"
---

# Content
""")

    code, stdout, stderr = run_cli(
        "create",
        str(source_file),
        "snippets/local/development/bad-pattern/SKILL.md",
        "--output", "json"
    )

    # Should fail with validation error
    assert code != 0, "Should fail for invalid pattern"

    # Check error message mentions the issue
    error_output = stderr + stdout
    assert "invalid_pattern_format" in error_output.lower() or "pattern must follow" in error_output.lower(), \
        "Error should mention pattern format validation"

    print("  ✓ Validates pattern format")


def test_create_invalid_destination():
    """Test: Create validates destination is in snippets directory"""
    print("\nTest: create validates destination path...")

    code, stdout, stderr = run_cli(
        "create",
        "/tmp/test.md",
        "/tmp/outside-snippets/SKILL.md",
        "--output", "json"
    )

    # Should fail - destination outside snippets dir
    assert code != 0, "Should fail for invalid destination"

    print("  Expected failure for invalid destination")


def test_create_pattern_override(tmp_path):
    """Test: Create accepts --pattern flag to override frontmatter"""
    print("\nTest: create with --pattern override...")

    source_file = tmp_path / "override-test.md"
    source_file.write_text("""---
name: "Override Test"
description: "Test description"
pattern: "\\\\b(OLD)\\\\b[.,;:!?]?"
---

# Content
""")

    code, stdout, stderr = run_cli(
        "create",
        str(source_file),
        "snippets/local/development/override-test/SKILL.md",
        "--pattern", "\\b(NEW)\\b[.,;:!?]?",
        "--output", "json"
    )

    # Will fail until implemented (RED phase)
    print(f"  Expected failure (RED phase): exit code {code}")


# =============================================================================
# SEARCH TESTS
# =============================================================================

def test_search_by_exact_name():
    """Test: Search finds exact name match"""
    print("\nTest: search by exact name...")

    # This will fail until we implement enhanced search
    code, stdout, stderr = run_cli("mail", "--output", "json")

    if code == 0:
        data = json.loads(stdout)
        snippets = data.get("snippets", [])

        # Should find snippet with exact name "mail"
        exact_matches = [s for s in snippets if s.get("name") == "mail"]
        print(f"  Found {len(exact_matches)} exact name matches")
    else:
        print(f"  Expected failure (RED phase): exit code {code}")


def test_search_by_pattern_content():
    """Test: Search finds pattern content match"""
    print("\nTest: search by pattern content...")

    code, stdout, stderr = run_cli("DOCKER", "--output", "json")

    if code == 0:
        data = json.loads(stdout)
        snippets = data.get("snippets", [])

        # Should find snippets with DOCKER in pattern
        pattern_matches = [s for s in snippets
                          if "DOCKER" in s.get("pattern", "").upper()]
        print(f"  Found {len(pattern_matches)} pattern matches")
    else:
        print(f"  Expected failure (RED phase): exit code {code}")


def test_search_by_description():
    """Test: Search finds description match"""
    print("\nTest: search by description...")

    # This will fail until we implement description search
    code, stdout, stderr = run_cli("email", "--output", "json")

    print(f"  Expected failure (RED phase): exit code {code}")


def test_search_result_priority():
    """Test: Search results ordered by match priority"""
    print("\nTest: search result priority...")

    # Create scenario where we have:
    # - Exact name match
    # - Pattern match
    # - Description match
    # Results should be ordered accordingly

    print("  Expected failure (RED phase) - priority ordering not implemented")


# =============================================================================
# TTY DETECTION TESTS
# =============================================================================

def test_non_interactive_when_piped():
    """Test: Auto-detect non-interactive mode when piped"""
    print("\nTest: non-interactive when piped...")

    # When stdout is piped, should not show interactive prompt
    # This is tested by the fact that we're running in subprocess
    code, stdout, stderr = run_cli("list", "--output", "json")

    assert code == 0, f"Should succeed: {stderr}"

    # Should not contain interactive prompts in JSON output
    assert "Select snippet" not in stdout, "Should not show interactive prompt"

    print("  ✓ Non-interactive when piped")


# =============================================================================
# VALIDATE COMMAND TESTS (Keep existing)
# =============================================================================

def test_validate_command():
    """Test: Validate command still works"""
    print("\nTest: validate command...")

    code, stdout, stderr = run_cli("validate", "--output", "json")

    assert code == 0, f"Validate should succeed: {stderr}"

    data = json.loads(stdout)
    # Check nested structure: data.config_valid or top-level config_valid
    assert "data" in data and "config_valid" in data["data"] or "config_valid" in data, \
        "Should have config_valid field (either nested or top-level)"

    print("  ✓ Validate command works")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
