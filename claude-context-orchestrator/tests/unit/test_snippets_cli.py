#!/usr/bin/env python3
"""
Comprehensive tests for snippets_cli.py

Tests cover:
- SnippetManager class and all CRUD operations
- Configuration loading and merging (base + local)
- Create, list, update, delete operations
- Validation and pattern testing
- Error handling and edge cases
- CLI argument parsing
- Output formatting
"""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import sys
import argparse

# Import the snippets_cli module
from snippets_cli import (
    SnippetManager,
    SnippetError,
    format_output,
    ANNOUNCEMENT_TEMPLATE
)


class TestSnippetManagerInit:
    """Test SnippetManager initialization and config loading"""

    def test_init_with_empty_dirs(self, tmp_path):
        """Test initialization with empty directories"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        manager = SnippetManager(config_path, snippets_dir)

        assert manager.config_path == config_path
        assert manager.snippets_dir == snippets_dir
        assert manager.config == {"mappings": []}

    def test_init_loads_base_config(self, tmp_path):
        """Test that base config is loaded on init"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        base_config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"]}
            ]
        }
        with open(config_path, 'w') as f:
            json.dump(base_config, f)

        manager = SnippetManager(config_path, snippets_dir)

        assert len(manager.config["mappings"]) == 1
        assert manager.config["mappings"][0]["name"] == "test1"

    def test_init_merges_local_config(self, tmp_path):
        """Test that local config is merged with base config"""
        config_path = tmp_path / "config.json"
        local_config_path = tmp_path / "config.local.json"
        snippets_dir = tmp_path / "snippets"

        base_config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"]}
            ]
        }
        with open(config_path, 'w') as f:
            json.dump(base_config, f)

        local_config = {
            "mappings": [
                {"name": "test2", "pattern": "world", "snippet": ["snippets/test2.md"]}
            ]
        }
        with open(local_config_path, 'w') as f:
            json.dump(local_config, f)

        manager = SnippetManager(config_path, snippets_dir)

        # Should have both snippets
        assert len(manager.config["mappings"]) == 2
        names = {m["name"] for m in manager.config["mappings"]}
        assert names == {"test1", "test2"}

    def test_init_local_overrides_base(self, tmp_path):
        """Test that local config overrides base config for same name"""
        config_path = tmp_path / "config.json"
        local_config_path = tmp_path / "config.local.json"
        snippets_dir = tmp_path / "snippets"

        base_config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"]}
            ]
        }
        with open(config_path, 'w') as f:
            json.dump(base_config, f)

        local_config = {
            "mappings": [
                {"name": "test1", "pattern": "hi", "snippet": ["snippets/override.md"]}
            ]
        }
        with open(local_config_path, 'w') as f:
            json.dump(local_config, f)

        manager = SnippetManager(config_path, snippets_dir)

        # Should only have one (local overrides base)
        assert len(manager.config["mappings"]) == 1
        assert manager.config["mappings"][0]["pattern"] == "hi"
        assert manager.config["mappings"][0]["snippet"] == ["snippets/override.md"]

    def test_init_with_malformed_config(self, tmp_path):
        """Test that malformed config raises error"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        # Write invalid JSON
        with open(config_path, 'w') as f:
            f.write("not valid json")

        with pytest.raises(SnippetError) as exc_info:
            SnippetManager(config_path, snippets_dir)

        assert exc_info.value.code == "CONFIG_ERROR"


class TestSnippetCreate:
    """Test snippet creation"""

    def test_create_simple_snippet(self, tmp_path):
        """Test creating a simple snippet with inline content"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        # Initialize with empty config
        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        result = manager.create(
            name="test1",
            pattern="hello",
            description="Test snippet",
            content="Test content"
        )

        # Check result
        assert result["name"] == "test1"
        assert result["pattern"] == "hello"
        assert result["enabled"] is True
        assert result["file_count"] == 1

        # Check file was created
        snippet_file = snippets_dir / "test1.md"
        assert snippet_file.exists()

        # Check content includes announcement
        content = snippet_file.read_text()
        assert "Test snippet" in content
        assert "Test content" in content

        # Check config was updated
        local_config = tmp_path / "config.local.json"
        assert local_config.exists()
        with open(local_config) as f:
            config = json.load(f)
        assert len(config["mappings"]) == 1
        assert config["mappings"][0]["name"] == "test1"

    def test_create_from_file(self, tmp_path):
        """Test creating snippet from file"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        # Create source file
        source_file = tmp_path / "source.md"
        source_file.write_text("Source content")

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        result = manager.create(
            name="test1",
            pattern="hello",
            description="Test snippet",
            file_path=str(source_file)
        )

        # Check file was created with content
        snippet_file = snippets_dir / "test1.md"
        assert snippet_file.exists()
        content = snippet_file.read_text()
        assert "Source content" in content

    def test_create_multi_file_snippet(self, tmp_path):
        """Test creating snippet with multiple files"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        # Create source files
        (snippets_dir / "part1.md").write_text("Part 1")
        (snippets_dir / "part2.md").write_text("Part 2")

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        result = manager.create(
            name="multi",
            pattern="test",
            description="Multi-file snippet",
            file_paths=["snippets/part1.md", "snippets/part2.md"],
            separator="\n---\n"
        )

        # Check result
        assert result["file_count"] == 2
        assert result["separator"] == "\n---\n"
        assert len(result["files"]) == 2

    def test_create_duplicate_name_fails(self, tmp_path):
        """Test that creating duplicate snippet fails without force"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        # Create first snippet
        manager.create("test1", "hello", "Test", content="Content 1")

        # Try to create duplicate
        with pytest.raises(SnippetError) as exc_info:
            manager.create("test1", "world", "Test", content="Content 2")

        assert exc_info.value.code == "DUPLICATE_NAME"

    def test_create_with_force_overwrites(self, tmp_path):
        """Test that force flag allows overwriting"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        # Create first snippet
        manager.create("test1", "hello", "Test", content="Content 1")

        # Overwrite with force
        result = manager.create("test1", "world", "Test", content="Content 2", force=True)

        assert result["pattern"] == "world"

        # Check file was updated
        snippet_file = snippets_dir / "test1.md"
        content = snippet_file.read_text()
        assert "Content 2" in content

    def test_create_invalid_regex(self, tmp_path):
        """Test that invalid regex pattern raises error"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        # Invalid regex (unclosed group)
        with pytest.raises(SnippetError) as exc_info:
            manager.create("test1", "(unclosed", "Test", content="Content")

        assert exc_info.value.code == "INVALID_REGEX"

    def test_create_without_content_fails(self, tmp_path):
        """Test that creating without content fails"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        with pytest.raises(SnippetError) as exc_info:
            manager.create("test1", "hello", "Test")

        assert exc_info.value.code == "INVALID_INPUT"

    def test_create_with_announce_flag(self, tmp_path):
        """Test announcement template is added when announce=True"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        manager.create("test1", "hello", "Test description", content="Content", announce=True)

        snippet_file = snippets_dir / "test1.md"
        content = snippet_file.read_text()

        # Should have YAML frontmatter
        assert "---" in content
        assert "name: test1" in content
        assert "description: Test description" in content


class TestSnippetList:
    """Test snippet listing"""

    def test_list_empty(self, tmp_path):
        """Test listing with no snippets"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        result = manager.list()

        assert result["snippets"] == []

    def test_list_all_snippets(self, tmp_path):
        """Test listing all snippets"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        # Create config with snippets
        config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"], "enabled": True},
                {"name": "test2", "pattern": "world", "snippet": ["snippets/test2.md"], "enabled": False}
            ]
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)

        # Create snippet files
        (snippets_dir / "test1.md").write_text("Content 1")
        (snippets_dir / "test2.md").write_text("Content 2")

        manager = SnippetManager(config_path, snippets_dir)

        result = manager.list()

        assert len(result["snippets"]) == 2
        names = {s["name"] for s in result["snippets"]}
        assert names == {"test1", "test2"}

        # Check enabled status
        test1 = next(s for s in result["snippets"] if s["name"] == "test1")
        assert test1["enabled"] is True

        test2 = next(s for s in result["snippets"] if s["name"] == "test2")
        assert test2["enabled"] is False

    def test_list_with_stats(self, tmp_path):
        """Test listing with statistics"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"], "enabled": True},
                {"name": "test2", "pattern": "world", "snippet": ["snippets/test2.md"], "enabled": False},
                {"name": "test3", "pattern": "foo", "snippet": ["snippets/test3.md"], "enabled": True}
            ]
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)

        (snippets_dir / "test1.md").write_text("Content 1")
        (snippets_dir / "test2.md").write_text("Content 2")
        (snippets_dir / "test3.md").write_text("Content 3")

        manager = SnippetManager(config_path, snippets_dir)

        result = manager.list(show_stats=True)

        assert result["total"] == 3
        assert result["enabled"] == 2
        assert result["disabled"] == 1

    def test_list_specific_snippet(self, tmp_path):
        """Test listing a specific snippet by name"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"], "enabled": True},
                {"name": "test2", "pattern": "world", "snippet": ["snippets/test2.md"], "enabled": True}
            ]
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)

        (snippets_dir / "test1.md").write_text("Content 1")
        (snippets_dir / "test2.md").write_text("Content 2")

        manager = SnippetManager(config_path, snippets_dir)

        result = manager.list(name="test1")

        assert len(result["snippets"]) == 1
        assert result["snippets"][0]["name"] == "test1"

    def test_list_with_content(self, tmp_path):
        """Test listing with snippet content"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"], "enabled": True}
            ]
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)

        (snippets_dir / "test1.md").write_text("Test content here")

        manager = SnippetManager(config_path, snippets_dir)

        result = manager.list(show_content=True)

        assert "content" in result["snippets"][0]
        assert result["snippets"][0]["content"] == "Test content here"

    def test_list_missing_files(self, tmp_path):
        """Test listing detects missing files"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"], "enabled": True}
            ]
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)

        # Don't create the snippet file

        manager = SnippetManager(config_path, snippets_dir)

        result = manager.list(show_stats=True)

        assert result["snippets"][0]["missing"] is True
        assert result["missing_files"] == 1


class TestSnippetUpdate:
    """Test snippet updating"""

    def test_update_pattern(self, tmp_path):
        """Test updating snippet pattern"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        # Create snippet
        manager.create("test1", "hello", "Test", content="Content")

        # Update pattern
        result = manager.update("test1", pattern="goodbye")

        assert "pattern" in result["changes"]
        assert result["changes"]["pattern"]["old"] == "hello"
        assert result["changes"]["pattern"]["new"] == "goodbye"

    def test_update_content(self, tmp_path):
        """Test updating snippet content"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        # Create snippet
        manager.create("test1", "hello", "Test", content="Old content")

        # Update content
        result = manager.update("test1", content="New content")

        assert "content" in result["changes"]

        # Check file was updated
        snippet_file = snippets_dir / "test1.md"
        content = snippet_file.read_text()
        assert "New content" in content

    def test_update_enabled_status(self, tmp_path):
        """Test updating enabled status"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        # Create snippet (enabled by default)
        manager.create("test1", "hello", "Test", content="Content")

        # Disable it
        result = manager.update("test1", enabled=False)

        assert "enabled" in result["changes"]
        assert result["changes"]["enabled"]["old"] is True
        assert result["changes"]["enabled"]["new"] is False

    def test_update_rename(self, tmp_path):
        """Test renaming snippet"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        # Create snippet
        manager.create("test1", "hello", "Test", content="Content")

        # Rename it
        result = manager.update("test1", rename="test2")

        assert "name" in result["changes"]
        assert result["changes"]["name"]["old"] == "test1"
        assert result["changes"]["name"]["new"] == "test2"

        # Check file was renamed
        old_file = snippets_dir / "test1.md"
        new_file = snippets_dir / "test2.md"
        assert not old_file.exists()
        assert new_file.exists()

    def test_update_nonexistent_snippet(self, tmp_path):
        """Test updating nonexistent snippet fails"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        with pytest.raises(SnippetError) as exc_info:
            manager.update("nonexistent", pattern="test")

        assert exc_info.value.code == "NOT_FOUND"

    def test_update_rename_to_existing_fails(self, tmp_path):
        """Test renaming to existing name fails"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        # Create two snippets
        manager.create("test1", "hello", "Test", content="Content 1")
        manager.create("test2", "world", "Test", content="Content 2")

        # Try to rename test1 to test2
        with pytest.raises(SnippetError) as exc_info:
            manager.update("test1", rename="test2")

        assert exc_info.value.code == "DUPLICATE_NAME"


class TestSnippetDelete:
    """Test snippet deletion"""

    def test_delete_snippet(self, tmp_path):
        """Test deleting a snippet"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        # Create snippet
        manager.create("test1", "hello", "Test", content="Content")

        # Delete it
        result = manager.delete("test1", backup=False)

        assert result["config_updated"] is True
        assert len(result["deleted"]) > 0

        # Check file was deleted
        snippet_file = snippets_dir / "test1.md"
        assert not snippet_file.exists()

        # Check config was updated
        assert len(manager.config["mappings"]) == 0

    def test_delete_with_backup(self, tmp_path):
        """Test deleting with backup"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        # Create snippet
        manager.create("test1", "hello", "Test", content="Content")

        # Delete with backup
        result = manager.delete("test1", backup=True)

        assert result["backup_location"] is not None

        # Check backup exists
        backup_path = Path(result["backup_location"])
        assert backup_path.exists()
        assert (backup_path / "test1.md").exists()

    def test_delete_with_custom_backup_dir(self, tmp_path):
        """Test deleting with custom backup directory"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        backup_dir = tmp_path / "my_backups"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        # Create snippet
        manager.create("test1", "hello", "Test", content="Content")

        # Delete with custom backup dir
        result = manager.delete("test1", backup=True, backup_dir=str(backup_dir))

        assert str(backup_dir) in result["backup_location"]
        assert backup_dir.exists()

    def test_delete_nonexistent_snippet(self, tmp_path):
        """Test deleting nonexistent snippet fails"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        with pytest.raises(SnippetError) as exc_info:
            manager.delete("nonexistent")

        assert exc_info.value.code == "NOT_FOUND"


class TestSnippetValidate:
    """Test configuration validation"""

    def test_validate_valid_config(self, tmp_path):
        """Test validation with valid config"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"]}
            ]
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)

        (snippets_dir / "test1.md").write_text("Content")

        manager = SnippetManager(config_path, snippets_dir)

        result = manager.validate()

        assert result["config_valid"] is True
        assert len(result["issues"]) == 0

    def test_validate_missing_file(self, tmp_path):
        """Test validation detects missing files"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"]}
            ]
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)

        # Don't create the file

        manager = SnippetManager(config_path, snippets_dir)

        result = manager.validate()

        assert result["config_valid"] is False
        assert len(result["issues"]) > 0
        assert any(issue["type"] == "missing_file" for issue in result["issues"])

    def test_validate_invalid_regex(self, tmp_path):
        """Test validation detects invalid regex"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        config = {
            "mappings": [
                {"name": "test1", "pattern": "(unclosed", "snippet": ["snippets/test1.md"]}
            ]
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)

        (snippets_dir / "test1.md").write_text("Content")

        manager = SnippetManager(config_path, snippets_dir)

        result = manager.validate()

        assert result["config_valid"] is False
        assert any(issue["type"] == "invalid_pattern" for issue in result["issues"])


class TestSnippetTest:
    """Test pattern matching test functionality"""

    def test_test_pattern_match(self, tmp_path):
        """Test that pattern matching test works"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        # Create snippet
        manager.create("test1", "hello", "Test", content="Content")

        # Test matching text
        result = manager.test("test1", "hello world")

        assert result["matched"] is True
        assert result["match_count"] > 0

    def test_test_pattern_no_match(self, tmp_path):
        """Test pattern not matching"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        # Create snippet
        manager.create("test1", "hello", "Test", content="Content")

        # Test non-matching text
        result = manager.test("test1", "goodbye world")

        assert result["matched"] is False
        assert result["match_count"] == 0

    def test_test_nonexistent_snippet(self, tmp_path):
        """Test testing nonexistent snippet fails"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        with pytest.raises(SnippetError) as exc_info:
            manager.test("nonexistent", "test text")

        assert exc_info.value.code == "NOT_FOUND"


class TestOutputFormatting:
    """Test output formatting functions"""

    def test_format_success_json(self):
        """Test formatting success output as JSON"""
        output = format_output(
            success=True,
            operation="create",
            data={"name": "test1"},
            message="Success",
            format_type="json"
        )

        result = json.loads(output)
        assert result["success"] is True
        assert result["operation"] == "create"
        assert result["data"]["name"] == "test1"
        assert result["message"] == "Success"

    def test_format_error_json(self):
        """Test formatting error output as JSON"""
        error = SnippetError("TEST_ERROR", "Test error message", {"detail": "value"})

        output = format_output(
            success=False,
            operation="create",
            error=error,
            format_type="json"
        )

        result = json.loads(output)
        assert result["success"] is False
        assert result["error"]["code"] == "TEST_ERROR"
        assert result["error"]["message"] == "Test error message"
        assert result["error"]["details"]["detail"] == "value"

    def test_format_success_text(self):
        """Test formatting success output as text"""
        output = format_output(
            success=True,
            operation="create",
            message="Success",
            format_type="text"
        )

        assert "✓" in output
        assert "Success" in output

    def test_format_error_text(self):
        """Test formatting error output as text"""
        error = SnippetError("TEST_ERROR", "Test error message")

        output = format_output(
            success=False,
            operation="create",
            error=error,
            format_type="text"
        )

        assert "✗" in output
        assert "Test error message" in output


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_empty_snippet_name(self, tmp_path):
        """Test empty snippet name fails"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        with pytest.raises(SnippetError) as exc_info:
            manager.create("", "pattern", "Test", content="Content")

        assert exc_info.value.code == "INVALID_INPUT"

    def test_unicode_in_pattern(self, tmp_path):
        """Test Unicode characters in pattern"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        # Create snippet with Unicode pattern
        result = manager.create("test1", "你好", "Test", content="Content")

        assert result["pattern"] == "你好"

        # Test it matches
        test_result = manager.test("test1", "你好世界")
        assert test_result["matched"] is True

    def test_special_regex_chars_in_pattern(self, tmp_path):
        """Test special regex characters in pattern"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        # Word boundary pattern
        result = manager.create("test1", r"\bhello\b", "Test", content="Content")

        assert result["pattern"] == r"\bhello\b"

    def test_very_long_content(self, tmp_path):
        """Test handling of very long content"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        # Create very long content (10MB)
        long_content = "x" * (10 * 1024 * 1024)

        result = manager.create("test1", "hello", "Test", content=long_content)

        assert result["size_bytes"] > 10 * 1024 * 1024

    def test_count_alternatives(self, tmp_path):
        """Test counting pattern alternatives"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir)

        # Pattern with alternatives
        result = manager.create("test1", r"\b(hello|hi|hey)\b", "Test", content="Content")

        assert result["alternatives"] == 3


class TestBaseConfigFlag:
    """Test --use-base-config flag behavior"""

    def test_create_saves_to_base_config(self, tmp_path):
        """Test that use_base_config=True saves to config.json"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir, use_base_config=True)

        manager.create("test1", "hello", "Test", content="Content")

        # Check base config was updated
        with open(config_path) as f:
            config = json.load(f)
        assert len(config["mappings"]) == 1
        assert config["mappings"][0]["name"] == "test1"

        # Local config should not exist
        local_config_path = tmp_path / "config.local.json"
        assert not local_config_path.exists()

    def test_create_saves_to_local_config_by_default(self, tmp_path):
        """Test that use_base_config=False saves to config.local.json"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        manager = SnippetManager(config_path, snippets_dir, use_base_config=False)

        manager.create("test1", "hello", "Test", content="Content")

        # Check local config was created
        local_config_path = tmp_path / "config.local.json"
        assert local_config_path.exists()

        with open(local_config_path) as f:
            config = json.load(f)
        assert len(config["mappings"]) == 1

        # Base config should remain empty
        with open(config_path) as f:
            base_config = json.load(f)
        assert len(base_config["mappings"]) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
