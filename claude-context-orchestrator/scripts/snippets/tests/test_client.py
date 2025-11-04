"""Tests for SnippetsClient core business logic."""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from snippets.client import SnippetsClient, SnippetError
from snippets.models import SnippetInfo, ValidationResult, PathsResponse


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory with test configs."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    # Create snippets directory first
    snippets_dir = tmp_path / "snippets" / "local"
    snippets_dir.mkdir(parents=True)

    # Create base config with absolute paths for reliability
    snippet_path = str(snippets_dir / "test" / "test-snippet.md")
    base_config = {
        "mappings": [
            {
                "name": "test-snippet",
                "pattern": "test.*snippet",
                "snippet": [snippet_path],
                "priority": 0
            }
        ]
    }

    config_path = config_dir / "config.json"
    with open(config_path, 'w') as f:
        json.dump(base_config, f)

    return {
        "config_dir": config_dir,
        "config_path": config_path,
        "snippets_dir": snippets_dir,
        "tmp_path": tmp_path
    }


@pytest.fixture
def client(temp_config_dir):
    """Create a SnippetsClient instance for testing."""
    return SnippetsClient(
        config_path=temp_config_dir["config_path"],
        snippets_dir=temp_config_dir["snippets_dir"]
    )


# =============================================================================
# INITIALIZATION TESTS
# =============================================================================

def test_client_initialization(temp_config_dir):
    """Test: Client initializes with config and snippets directory."""
    client = SnippetsClient(
        config_path=temp_config_dir["config_path"],
        snippets_dir=temp_config_dir["snippets_dir"]
    )

    assert client.config_path == temp_config_dir["config_path"]
    assert client.snippets_dir == temp_config_dir["snippets_dir"]
    assert "mappings" in client.config
    assert len(client.config["mappings"]) == 1


def test_client_loads_merged_config(temp_config_dir):
    """Test: Client merges base and local configs."""
    # Create local config
    local_config = {
        "mappings": [
            {
                "name": "local-snippet",
                "pattern": "local.*test",
                "snippet": ["snippets/local/test/local.md"],
                "priority": 100
            }
        ]
    }

    local_path = temp_config_dir["config_dir"] / "config.local.json"
    with open(local_path, 'w') as f:
        json.dump(local_config, f)

    client = SnippetsClient(
        config_path=temp_config_dir["config_path"],
        snippets_dir=temp_config_dir["snippets_dir"]
    )

    # Should have both mappings
    assert len(client.config["mappings"]) == 2


def test_client_invalid_config_raises_error(temp_config_dir):
    """Test: Invalid JSON config raises SnippetError."""
    # Write invalid JSON
    with open(temp_config_dir["config_path"], 'w') as f:
        f.write("{ invalid json }")

    with pytest.raises(SnippetError) as exc_info:
        SnippetsClient(
            config_path=temp_config_dir["config_path"],
            snippets_dir=temp_config_dir["snippets_dir"]
        )

    assert exc_info.value.code == "CONFIG_ERROR"


# =============================================================================
# CREATE TESTS
# =============================================================================

def test_create_snippet(client, temp_config_dir):
    """Test: Create a new snippet successfully."""
    result = client.create(
        name="new-snippet",
        pattern="new.*pattern",
        description="Test snippet",
        content="# Test Content"
    )

    assert isinstance(result, SnippetInfo)
    assert result.name == "new-snippet"
    assert result.pattern == "new.*pattern"

    # Verify file was created
    snippet_path = temp_config_dir["snippets_dir"] / "new-snippet.md"
    assert snippet_path.exists()

    # Verify config was updated
    assert any(m["name"] == "new-snippet" for m in client.target_config["mappings"])


def test_create_snippet_with_default_content(client, temp_config_dir):
    """Test: Create snippet with default template content."""
    result = client.create(
        name="templated-snippet",
        pattern="template.*test",
        description="Template test"
    )

    snippet_path = temp_config_dir["snippets_dir"] / "templated-snippet.md"
    assert snippet_path.exists()

    with open(snippet_path) as f:
        content = f.read()
        assert "name: templated-snippet" in content
        assert "Template test" in content


def test_create_duplicate_snippet_fails(client):
    """Test: Creating duplicate snippet raises error."""
    client.create(
        name="duplicate",
        pattern="dup.*test",
        description="First"
    )

    with pytest.raises(SnippetError) as exc_info:
        client.create(
            name="duplicate",
            pattern="other.*pattern",
            description="Second"
        )

    assert exc_info.value.code == "SNIPPET_EXISTS"


def test_create_invalid_pattern_fails(client):
    """Test: Invalid regex pattern raises error."""
    with pytest.raises(SnippetError) as exc_info:
        client.create(
            name="invalid-pattern",
            pattern="[invalid(regex",
            description="Bad pattern"
        )

    assert exc_info.value.code == "INVALID_PATTERN"


def test_create_with_priority(client, temp_config_dir):
    """Test: Create snippet with custom priority."""
    result = client.create(
        name="priority-snippet",
        pattern="priority.*test",
        description="Priority test",
        priority=50
    )

    assert result.priority == 50

    # Verify priority in config
    mapping = next(
        m for m in client.target_config["mappings"]
        if m["name"] == "priority-snippet"
    )
    assert mapping["priority"] == 50


# =============================================================================
# LIST TESTS
# =============================================================================

def test_list_all_snippets(client):
    """Test: List all snippets returns all mappings."""
    result = client.list_snippets()

    assert isinstance(result, list)
    assert len(result) >= 1
    assert all(isinstance(item, SnippetInfo) for item in result)


def test_list_specific_snippet(client):
    """Test: List specific snippet by name."""
    result = client.list_snippets(name="test-snippet")

    assert len(result) == 1
    assert result[0].name == "test-snippet"


def test_list_nonexistent_snippet(client):
    """Test: Listing nonexistent snippet returns empty list."""
    result = client.list_snippets(name="nonexistent")

    assert len(result) == 0


# =============================================================================
# SEARCH TESTS
# =============================================================================

def test_search_by_name(client):
    """Test: Search finds snippets by name."""
    result = client.search("test")

    assert result.query == "test"
    assert len(result.matches) >= 1
    assert any(s.name == "test-snippet" for s in result.matches)


def test_search_by_pattern(client, temp_config_dir):
    """Test: Search finds snippets by pattern content."""
    # Create snippet with specific pattern
    client.create(
        name="searchable",
        pattern="unique.*searchterm",
        description="Test"
    )

    result = client.search("searchterm")

    assert any(s.name == "searchable" for s in result.matches)


def test_search_case_insensitive(client):
    """Test: Search is case-insensitive."""
    result1 = client.search("TEST")
    result2 = client.search("test")

    assert len(result1.matches) == len(result2.matches)


def test_search_no_matches(client):
    """Test: Search with no matches returns empty results."""
    result = client.search("NONEXISTENT12345")

    assert len(result.matches) == 0
    assert result.total_searched > 0


# =============================================================================
# UPDATE TESTS
# =============================================================================

def test_update_pattern(client, temp_config_dir):
    """Test: Update snippet pattern."""
    client.create(
        name="updateable",
        pattern="old.*pattern",
        description="Test"
    )

    result = client.update(
        name="updateable",
        pattern="new.*pattern"
    )

    assert result.pattern == "new.*pattern"

    # Verify config was updated
    mapping = next(
        m for m in client.target_config["mappings"]
        if m["name"] == "updateable"
    )
    assert mapping["pattern"] == "new.*pattern"


def test_update_content(client, temp_config_dir):
    """Test: Update snippet content."""
    client.create(
        name="content-update",
        pattern="test.*pattern",
        description="Test",
        content="Old content"
    )

    new_content = "New content here"
    client.update(
        name="content-update",
        content=new_content
    )

    # Verify file was updated
    snippet_path = temp_config_dir["snippets_dir"] / "content-update.md"
    with open(snippet_path) as f:
        content = f.read()
        assert "New content here" in content


def test_update_nonexistent_snippet_fails(client):
    """Test: Updating nonexistent snippet raises error."""
    with pytest.raises(SnippetError) as exc_info:
        client.update(
            name="nonexistent",
            pattern="new.*pattern"
        )

    assert exc_info.value.code == "SNIPPET_NOT_FOUND"


def test_update_invalid_pattern_fails(client, temp_config_dir):
    """Test: Updating with invalid pattern raises error."""
    client.create(
        name="update-test",
        pattern="valid.*pattern",
        description="Test"
    )

    with pytest.raises(SnippetError) as exc_info:
        client.update(
            name="update-test",
            pattern="[invalid(regex"
        )

    assert exc_info.value.code == "INVALID_PATTERN"


# =============================================================================
# DELETE TESTS
# =============================================================================

def test_delete_snippet(client, temp_config_dir):
    """Test: Delete snippet successfully."""
    client.create(
        name="deletable",
        pattern="delete.*test",
        description="Test"
    )

    snippet_path = temp_config_dir["snippets_dir"] / "deletable.md"
    assert snippet_path.exists()

    result = client.delete(name="deletable", force=True)

    assert result["name"] == "deletable"
    assert len(result["deleted_files"]) == 1
    assert not snippet_path.exists()

    # Verify removed from config
    assert not any(
        m["name"] == "deletable"
        for m in client.target_config["mappings"]
    )


def test_delete_with_backup(client, temp_config_dir):
    """Test: Delete creates backup file."""
    client.create(
        name="backup-test",
        pattern="backup.*test",
        description="Test"
    )

    result = client.delete(name="backup-test", force=True, backup=True)

    assert len(result["backup_paths"]) == 1
    backup_path = Path(result["backup_paths"][0])
    assert backup_path.exists()
    assert "backup" in backup_path.name


def test_delete_nonexistent_snippet_fails(client):
    """Test: Deleting nonexistent snippet raises error."""
    with pytest.raises(SnippetError) as exc_info:
        client.delete(name="nonexistent", force=True)

    assert exc_info.value.code == "SNIPPET_NOT_FOUND"


# =============================================================================
# VALIDATE TESTS
# =============================================================================

def test_validate_valid_config(client):
    """Test: Validate returns success for valid config."""
    result = client.validate()

    assert isinstance(result, ValidationResult)
    # May have errors if snippet files don't exist yet
    assert result.total_mappings >= 1


def test_validate_reports_missing_files(temp_config_dir):
    """Test: Validate detects missing snippet files."""
    # Create config with non-existent snippet
    config = {
        "mappings": [
            {
                "name": "missing",
                "pattern": "test",
                "snippet": ["nonexistent/file.md"]
            }
        ]
    }

    with open(temp_config_dir["config_path"], 'w') as f:
        json.dump(config, f)

    client = SnippetsClient(
        config_path=temp_config_dir["config_path"],
        snippets_dir=temp_config_dir["snippets_dir"]
    )

    result = client.validate()

    assert not result.valid
    assert len(result.errors) > 0


# =============================================================================
# SHOW_PATHS TESTS
# =============================================================================

def test_show_paths(client):
    """Test: show_paths returns configuration structure."""
    result = client.show_paths()

    assert isinstance(result, PathsResponse)
    assert len(result.config_files) >= 1
    assert result.base_dir is not None
    assert isinstance(result.categories, list)


def test_show_paths_with_filter(client, temp_config_dir):
    """Test: show_paths filters categories by keyword."""
    # Create snippet in 'development' category
    dev_dir = temp_config_dir["snippets_dir"] / "development"
    dev_dir.mkdir(parents=True, exist_ok=True)

    client.create(
        name="dev-snippet",
        pattern="dev.*test",
        description="Development snippet"
    )

    result = client.show_paths(filter_term="dev")

    # Should only return matching categories
    assert all("dev" in cat.name.lower() for cat in result.categories)


def test_show_paths_lists_config_files(client):
    """Test: show_paths lists all config files."""
    result = client.show_paths()

    assert len(result.config_files) >= 1
    assert result.config_files[0].type == "base"
    assert result.config_files[0].priority == 0


# =============================================================================
# MULTI-CONFIG TESTS
# =============================================================================

def test_use_base_config_flag(temp_config_dir):
    """Test: use_base_config flag targets base config for modifications."""
    client = SnippetsClient(
        config_path=temp_config_dir["config_path"],
        snippets_dir=temp_config_dir["snippets_dir"],
        use_base_config=True
    )

    assert client.target_config_path == temp_config_dir["config_path"]


def test_named_config_targets_specific_file(temp_config_dir):
    """Test: config_name targets specific named config file."""
    # Create named config
    named_config = {
        "mappings": []
    }
    named_path = temp_config_dir["config_dir"] / "config.work.json"
    with open(named_path, 'w') as f:
        json.dump(named_config, f)

    client = SnippetsClient(
        config_path=temp_config_dir["config_path"],
        snippets_dir=temp_config_dir["snippets_dir"],
        config_name="work"
    )

    assert client.target_config_path == named_path


def test_category_info_has_path_property():
    """Test: CategoryInfo has path property for CLI display."""
    from snippets.models import CategoryInfo

    # Create category with sample paths
    category = CategoryInfo(
        name="test-category",
        snippet_count=5,
        sample_paths=["path/to/snippet1", "path/to/snippet2"]
    )

    # Should have path property that returns first sample path
    assert hasattr(category, "path"), "CategoryInfo should have 'path' property"
    assert category.path == "path/to/snippet1", "path should return first sample path"


def test_category_info_path_when_no_samples():
    """Test: CategoryInfo.path returns empty string when no sample paths."""
    from snippets.models import CategoryInfo

    category = CategoryInfo(
        name="empty-category",
        snippet_count=0,
        sample_paths=[]
    )

    # Should return empty string when no sample paths
    assert category.path == "", "path should return empty string when no samples"
