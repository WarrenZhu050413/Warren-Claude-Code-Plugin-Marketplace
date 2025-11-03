"""Tests for helpers.core utilities."""

import json
import pytest
from pathlib import Path

from snippets.helpers.core import (
    # Config
    add_mapping,
    find_mapping_by_pattern,
    load_config_file,
    load_merged_config,
    merge_configs,
    remove_mapping,
    save_config_file,
    update_mapping,
    # Hashing
    compute_verification_hash,
    extract_verification_hash,
    update_verification_hash,
    verify_hash,
    # Paths
    discover_categories,
    resolve_snippet_path,
)


# =============================================================================
# CONFIG TESTS
# =============================================================================

@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file."""
    config_path = tmp_path / "config.json"
    config_data = {
        "mappings": [
            {
                "name": "test1",
                "pattern": "test.*1",
                "snippet": ["test1.md"],
                "priority": 0
            },
            {
                "name": "test2",
                "pattern": "test.*2",
                "snippet": ["test2.md"],
                "priority": 10
            }
        ]
    }
    with open(config_path, 'w') as f:
        json.dump(config_data, f)
    return config_path


def test_load_config_file(temp_config_file):
    """Test: Load config file successfully."""
    config = load_config_file(temp_config_file)

    assert "mappings" in config
    assert len(config["mappings"]) == 2


def test_load_config_file_not_found(tmp_path):
    """Test: Loading nonexistent config raises error."""
    with pytest.raises(FileNotFoundError):
        load_config_file(tmp_path / "nonexistent.json")


def test_save_config_file(tmp_path):
    """Test: Save config file."""
    config_path = tmp_path / "new_config.json"
    config_data = {
        "mappings": [{"name": "test", "pattern": ".*", "snippet": ["test.md"]}]
    }

    save_config_file(config_path, config_data)

    assert config_path.exists()

    with open(config_path) as f:
        loaded = json.load(f)
        assert loaded == config_data


def test_merge_configs():
    """Test: Merge base and local configs."""
    base = {
        "mappings": [
            {"name": "base1", "pattern": ".*", "snippet": ["base1.md"]}
        ],
        "setting1": "value1"
    }
    local = {
        "mappings": [
            {"name": "local1", "pattern": ".*", "snippet": ["local1.md"]}
        ],
        "setting1": "override",
        "setting2": "value2"
    }

    merged = merge_configs(base, local)

    # Should have both mappings (base first, then local)
    assert len(merged["mappings"]) == 2
    assert merged["mappings"][0]["name"] == "base1"
    assert merged["mappings"][1]["name"] == "local1"

    # Local settings should override
    assert merged["setting1"] == "override"
    assert merged["setting2"] == "value2"


def test_merge_configs_with_none_local():
    """Test: Merge with None local config returns base."""
    base = {"mappings": [{"name": "test", "pattern": ".*", "snippet": ["test.md"]}]}

    merged = merge_configs(base, None)

    assert merged == base


def test_load_merged_config(temp_config_file, tmp_path):
    """Test: Load and merge base and local configs."""
    # Create local config
    local_path = tmp_path / "config.local.json"
    local_data = {
        "mappings": [
            {"name": "local", "pattern": "local.*", "snippet": ["local.md"]}
        ]
    }
    with open(local_path, 'w') as f:
        json.dump(local_data, f)

    merged = load_merged_config(temp_config_file, local_path)

    assert len(merged["mappings"]) == 3  # 2 from base + 1 from local


def test_find_mapping_by_pattern():
    """Test: Find mapping by pattern."""
    config = {
        "mappings": [
            {"name": "test1", "pattern": "pattern1", "snippet": ["test1.md"]},
            {"name": "test2", "pattern": "pattern2", "snippet": ["test2.md"]}
        ]
    }

    result = find_mapping_by_pattern(config, "pattern1")

    assert result is not None
    assert result["name"] == "test1"


def test_find_mapping_by_pattern_not_found():
    """Test: Find mapping returns None if not found."""
    config = {"mappings": []}

    result = find_mapping_by_pattern(config, "nonexistent")

    assert result is None


def test_add_mapping():
    """Test: Add new mapping to config."""
    config = {"mappings": []}

    updated = add_mapping(config, "test.*pattern", ["test.md"], priority=5)

    assert len(updated["mappings"]) == 1
    assert updated["mappings"][0]["pattern"] == "test.*pattern"
    assert updated["mappings"][0]["priority"] == 5


def test_remove_mapping():
    """Test: Remove mapping from config."""
    config = {
        "mappings": [
            {"name": "keep", "pattern": "keep", "snippet": ["keep.md"]},
            {"name": "remove", "pattern": "remove", "snippet": ["remove.md"]}
        ]
    }

    updated = remove_mapping(config, "remove")

    assert len(updated["mappings"]) == 1
    assert updated["mappings"][0]["pattern"] == "keep"


def test_update_mapping():
    """Test: Update existing mapping."""
    config = {
        "mappings": [
            {"name": "test", "pattern": "old", "snippet": ["test.md"], "priority": 0}
        ]
    }

    updated = update_mapping(config, "old", {"pattern": "new", "priority": 10})

    assert updated["mappings"][0]["pattern"] == "new"
    assert updated["mappings"][0]["priority"] == 10


# =============================================================================
# HASHING TESTS
# =============================================================================

def test_compute_verification_hash():
    """Test: Compute verification hash for content."""
    content = "Test content here"

    hash_value = compute_verification_hash(content)

    assert isinstance(hash_value, str)
    assert len(hash_value) == 8
    assert hash_value.isalnum()


def test_compute_verification_hash_removes_existing_hash():
    """Test: Computing hash removes existing hash from content."""
    content = """**VERIFICATION_HASH:** `oldvalue`

Test content"""

    hash1 = compute_verification_hash(content)
    hash2 = compute_verification_hash(content.replace("oldvalue", "different"))

    # Should produce same hash (ignores existing hash)
    assert hash1 == hash2


def test_compute_verification_hash_stable():
    """Test: Same content produces same hash."""
    content = "Test content"

    hash1 = compute_verification_hash(content)
    hash2 = compute_verification_hash(content)

    assert hash1 == hash2


def test_extract_verification_hash():
    """Test: Extract hash from content."""
    content = """---
name: test
---

**VERIFICATION_HASH:** `abc12345`

Content here
"""

    hash_value = extract_verification_hash(content)

    assert hash_value == "abc12345"


def test_extract_verification_hash_not_found():
    """Test: Extract returns None if no hash found."""
    content = "No hash here"

    hash_value = extract_verification_hash(content)

    assert hash_value is None


def test_update_verification_hash_adds_hash():
    """Test: Update adds hash if not present."""
    content = "Test content"

    updated = update_verification_hash(content, "newhash1")

    assert "VERIFICATION_HASH:" in updated
    assert "newhash1" in updated


def test_update_verification_hash_replaces_existing():
    """Test: Update replaces existing hash."""
    content = """**VERIFICATION_HASH:** `oldhash`

Test content"""

    updated = update_verification_hash(content, "newhash2")

    assert "newhash2" in updated
    assert "oldhash" not in updated


def test_update_verification_hash_preserves_frontmatter():
    """Test: Update preserves YAML frontmatter."""
    content = """---
name: test
description: Test snippet
---

Content here
"""

    updated = update_verification_hash(content, "hashvalue")

    assert content.startswith("---")
    assert "VERIFICATION_HASH:" in updated
    assert "hashvalue" in updated


def test_verify_hash_valid():
    """Test: Verify hash returns True for valid hash."""
    content = "Test content"
    hash_value = compute_verification_hash(content)
    content_with_hash = update_verification_hash(content, hash_value)

    assert verify_hash(content_with_hash)


def test_verify_hash_invalid():
    """Test: Verify hash returns False for invalid hash."""
    content = """**VERIFICATION_HASH:** `wronghash`

Test content"""

    assert not verify_hash(content)


def test_verify_hash_missing():
    """Test: Verify hash returns False if no hash present."""
    content = "No hash here"

    assert not verify_hash(content)


# =============================================================================
# PATHS TESTS
# =============================================================================

def test_discover_categories():
    """Test: Discover categories from config."""
    config = {
        "mappings": [
            {
                "name": "dev1",
                "pattern": ".*",
                "snippet": ["snippets/local/development/test/SKILL.md"]
            },
            {
                "name": "dev2",
                "pattern": ".*",
                "snippet": ["snippets/local/development/other/SKILL.md"]
            },
            {
                "name": "output1",
                "pattern": ".*",
                "snippet": ["snippets/local/output-formats/latex/SKILL.md"]
            }
        ]
    }

    categories = discover_categories(config)

    assert "development" in categories
    assert "output-formats" in categories
    assert categories["development"]["count"] == 2
    assert categories["output-formats"]["count"] == 1


def test_discover_categories_handles_skills():
    """Test: Discover categories handles skills directory."""
    config = {
        "mappings": [
            {
                "name": "skill1",
                "pattern": ".*",
                "snippet": ["../skills/my-skill/SKILL.md"]
            }
        ]
    }

    categories = discover_categories(config)

    assert "skills" in categories
    assert categories["skills"]["count"] == 1


def test_discover_categories_empty_config():
    """Test: Discover categories with empty config."""
    config = {"mappings": []}

    categories = discover_categories(config)

    assert len(categories) == 0


def test_resolve_snippet_path_absolute(tmp_path):
    """Test: Resolve absolute path returns as-is."""
    absolute_path = tmp_path / "test.md"
    absolute_path.touch()

    resolved = resolve_snippet_path(str(absolute_path), tmp_path)

    assert resolved == absolute_path


def test_resolve_snippet_path_relative(tmp_path):
    """Test: Resolve relative path against base dir."""
    base_dir = tmp_path / "snippets"
    base_dir.mkdir()

    snippet_file = base_dir / "test.md"
    snippet_file.touch()

    resolved = resolve_snippet_path("test.md", base_dir)

    assert resolved == snippet_file.resolve()


def test_resolve_snippet_path_nonexistent(tmp_path):
    """Test: Resolve nonexistent path returns path as-is."""
    base_dir = tmp_path / "snippets"
    base_dir.mkdir()

    resolved = resolve_snippet_path("nonexistent.md", base_dir)

    # Should return some path (won't exist, but that's okay)
    assert isinstance(resolved, Path)
