"""Tests for validators."""

from pathlib import Path

import pytest

from snippets.validators import (
    # Pattern validators
    check_pattern_match,
    extract_pattern_groups,
    validate_config_mapping,
    validate_full_config,
    validate_regex_pattern,
    validate_snippet_content,
    # Snippet validators
    validate_snippet_file,
    validate_snippet_name,
)

# =============================================================================
# PATTERN VALIDATION TESTS
# =============================================================================

def test_validate_regex_pattern_valid():
    """Test: Valid regex pattern returns True."""
    is_valid, error = validate_regex_pattern("test.*pattern")

    assert is_valid
    assert error is None


def test_validate_regex_pattern_invalid():
    """Test: Invalid regex pattern returns False with error."""
    is_valid, error = validate_regex_pattern("[invalid(regex")

    assert not is_valid
    assert error is not None
    assert "Invalid regex" in error


def test_validate_regex_pattern_empty():
    """Test: Empty pattern returns False."""
    is_valid, error = validate_regex_pattern("")

    assert not is_valid
    assert "cannot be empty" in error


def test_validate_regex_pattern_whitespace_only():
    """Test: Whitespace-only pattern returns False."""
    is_valid, error = validate_regex_pattern("   ")

    assert not is_valid
    assert "whitespace" in error


def test_check_pattern_match_success():
    """Test: Check pattern matches text."""
    assert check_pattern_match("test.*snippet", "test my snippet")
    assert check_pattern_match("test.*snippet", "TEST MY SNIPPET")  # Case insensitive


def test_check_pattern_match_failure():
    """Test: Check pattern does not match text."""
    assert not check_pattern_match("test.*snippet", "no match here")


def test_check_pattern_match_invalid_pattern():
    """Test: Invalid pattern returns False."""
    assert not check_pattern_match("[invalid(", "any text")


def test_extract_pattern_groups():
    """Test: Extract named groups from pattern."""
    pattern = r"use (?P<keyword>\w+)"
    text = "use testing"

    groups = extract_pattern_groups(pattern, text)

    assert groups is not None
    assert groups["keyword"] == "testing"


def test_extract_pattern_groups_no_match():
    """Test: Extract returns None if no match."""
    pattern = r"use (?P<keyword>\w+)"
    text = "no match"

    groups = extract_pattern_groups(pattern, text)

    assert groups is None


def test_extract_pattern_groups_invalid_pattern():
    """Test: Extract returns None for invalid pattern."""
    groups = extract_pattern_groups("[invalid(", "any text")

    assert groups is None


# =============================================================================
# SNIPPET FILE VALIDATION TESTS
# =============================================================================

def test_validate_snippet_file_valid(tmp_path):
    """Test: Valid snippet file returns True."""
    snippet_file = tmp_path / "test.md"
    snippet_file.write_text("Test content")

    is_valid, error = validate_snippet_file(snippet_file)

    assert is_valid
    assert error is None


def test_validate_snippet_file_not_found(tmp_path):
    """Test: Nonexistent file returns False."""
    snippet_file = tmp_path / "nonexistent.md"

    is_valid, error = validate_snippet_file(snippet_file)

    assert not is_valid
    assert "does not exist" in error


def test_validate_snippet_file_is_directory(tmp_path):
    """Test: Directory path returns False."""
    snippet_dir = tmp_path / "dir"
    snippet_dir.mkdir()

    is_valid, error = validate_snippet_file(snippet_dir)

    assert not is_valid
    assert "Not a file" in error


def test_validate_snippet_file_empty(tmp_path):
    """Test: Empty file returns False."""
    snippet_file = tmp_path / "empty.md"
    snippet_file.write_text("")

    is_valid, error = validate_snippet_file(snippet_file)

    assert not is_valid
    assert "empty" in error


# =============================================================================
# SNIPPET NAME VALIDATION TESTS
# =============================================================================

def test_validate_snippet_name_valid():
    """Test: Valid snippet name returns True."""
    is_valid, error = validate_snippet_name("test-snippet")

    assert is_valid
    assert error is None


def test_validate_snippet_name_empty():
    """Test: Empty name returns False."""
    is_valid, error = validate_snippet_name("")

    assert not is_valid
    assert "cannot be empty" in error


def test_validate_snippet_name_with_slash():
    """Test: Name with slash returns False."""
    is_valid, error = validate_snippet_name("test/snippet")

    assert not is_valid
    assert "slashes" in error


def test_validate_snippet_name_with_backslash():
    """Test: Name with backslash returns False."""
    is_valid, error = validate_snippet_name("test\\snippet")

    assert not is_valid
    assert "slashes" in error


def test_validate_snippet_name_starts_with_dot():
    """Test: Name starting with dot returns False."""
    is_valid, error = validate_snippet_name(".hidden")

    assert not is_valid
    assert "dot" in error


def test_validate_snippet_name_too_long():
    """Test: Name exceeding max length returns False."""
    long_name = "a" * 101

    is_valid, error = validate_snippet_name(long_name)

    assert not is_valid
    assert "too long" in error


# =============================================================================
# SNIPPET CONTENT VALIDATION TESTS
# =============================================================================

def test_validate_snippet_content_valid():
    """Test: Valid content returns True."""
    content = """---
name: test
---

Test content
"""

    is_valid, warnings = validate_snippet_content(content)

    assert is_valid


def test_validate_snippet_content_empty():
    """Test: Empty content returns False."""
    is_valid, warnings = validate_snippet_content("")

    assert not is_valid
    assert "empty" in warnings[0]


def test_validate_snippet_content_incomplete_frontmatter():
    """Test: Incomplete frontmatter produces warning."""
    content = """---
name: test
"""  # Missing closing ---

    is_valid, warnings = validate_snippet_content(content)

    assert is_valid
    assert any("frontmatter" in w.lower() for w in warnings)


# =============================================================================
# CONFIG MAPPING VALIDATION TESTS
# =============================================================================

def test_validate_config_mapping_valid(tmp_path):
    """Test: Valid mapping returns no errors."""
    snippet_file = tmp_path / "test.md"
    snippet_file.write_text("Test content")

    mapping = {
        "pattern": "test.*pattern",
        "snippet": [str(snippet_file)]
    }

    errors = validate_config_mapping(mapping, tmp_path)

    assert len(errors) == 0


def test_validate_config_mapping_missing_pattern():
    """Test: Missing pattern field returns error."""
    mapping = {
        "snippet": ["test.md"]
    }

    errors = validate_config_mapping(mapping, Path("/tmp"))

    assert len(errors) > 0
    assert any(e.error_type == "missing_field" for e in errors)


def test_validate_config_mapping_missing_snippet():
    """Test: Missing snippet field returns error."""
    mapping = {
        "pattern": "test"
    }

    errors = validate_config_mapping(mapping, Path("/tmp"))

    assert len(errors) > 0
    assert any(e.error_type == "missing_field" for e in errors)


def test_validate_config_mapping_invalid_pattern():
    """Test: Invalid regex pattern returns error."""
    mapping = {
        "pattern": "[invalid(regex",
        "snippet": ["test.md"]
    }

    errors = validate_config_mapping(mapping, Path("/tmp"))

    assert len(errors) > 0
    assert any(e.error_type == "invalid_pattern" for e in errors)


def test_validate_config_mapping_missing_file(tmp_path):
    """Test: Missing snippet file returns error."""
    mapping = {
        "pattern": "test",
        "snippet": ["nonexistent.md"]
    }

    errors = validate_config_mapping(mapping, tmp_path)

    assert len(errors) > 0
    assert any(e.error_type == "invalid_snippet_file" for e in errors)


def test_validate_config_mapping_multiple_files(tmp_path):
    """Test: Validate mapping with multiple snippet files."""
    file1 = tmp_path / "test1.md"
    file2 = tmp_path / "test2.md"
    file1.write_text("Content 1")
    file2.write_text("Content 2")

    mapping = {
        "pattern": "test",
        "snippet": [str(file1), str(file2)]
    }

    errors = validate_config_mapping(mapping, tmp_path)

    assert len(errors) == 0


# =============================================================================
# FULL CONFIG VALIDATION TESTS
# =============================================================================

def test_validate_full_config_valid(tmp_path):
    """Test: Valid full config returns no errors."""
    snippet_file = tmp_path / "test.md"
    snippet_file.write_text("Test content")

    config = {
        "mappings": [
            {
                "pattern": "test1",
                "snippet": [str(snippet_file)]
            }
        ]
    }

    errors = validate_full_config(config, tmp_path)

    assert len(errors) == 0


def test_validate_full_config_missing_mappings():
    """Test: Config without mappings returns error."""
    config = {}

    errors = validate_full_config(config, Path("/tmp"))

    assert len(errors) > 0
    assert any(e.error_type == "missing_field" for e in errors)


def test_validate_full_config_multiple_mappings(tmp_path):
    """Test: Validate config with multiple mappings."""
    file1 = tmp_path / "test1.md"
    file2 = tmp_path / "test2.md"
    file1.write_text("Content 1")
    file2.write_text("Content 2")

    config = {
        "mappings": [
            {"pattern": "test1", "snippet": [str(file1)]},
            {"pattern": "test2", "snippet": [str(file2)]},
        ]
    }

    errors = validate_full_config(config, tmp_path)

    assert len(errors) == 0


def test_validate_full_config_mixed_valid_invalid(tmp_path):
    """Test: Config with mix of valid and invalid mappings."""
    valid_file = tmp_path / "valid.md"
    valid_file.write_text("Content")

    config = {
        "mappings": [
            {"pattern": "valid", "snippet": [str(valid_file)]},
            {"pattern": "[invalid(", "snippet": ["nonexistent.md"]},
        ]
    }

    errors = validate_full_config(config, tmp_path)

    assert len(errors) > 0
    # Should have errors for the second mapping
    assert any("Mapping #1" in e.message for e in errors)
