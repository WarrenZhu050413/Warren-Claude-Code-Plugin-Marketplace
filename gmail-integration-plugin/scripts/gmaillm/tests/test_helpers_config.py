"""Tests for gmaillm.helpers.config module."""

import json
import pytest
from pathlib import Path

from gmaillm.helpers.config import (
    get_plugin_config_dir,
    load_json_config,
    save_json_config,
    load_email_groups,
    save_email_groups,
    expand_email_groups,
    get_groups_file_path,
    get_styles_dir,
    get_style_file_path,
    load_all_styles,
    extract_style_metadata,
    create_backup,
    create_style_from_template
)


class TestConfigDirFunctions:
    """Tests for configuration directory functions."""

    def test_get_plugin_config_dir_returns_path(self):
        """Test that get_plugin_config_dir returns a Path object."""
        result = get_plugin_config_dir()
        assert isinstance(result, Path)

    def test_get_styles_dir_creates_directory(self, temp_dir, monkeypatch):
        """Test that get_styles_dir creates the directory if it doesn't exist."""
        # Mock get_plugin_config_dir to return temp_dir
        def mock_config_dir():
            return temp_dir
        monkeypatch.setattr('gmaillm.helpers.config.get_plugin_config_dir', mock_config_dir)

        styles_dir = get_styles_dir()
        assert styles_dir.exists()
        assert styles_dir.is_dir()

    def test_get_style_file_path(self, temp_dir, monkeypatch):
        """Test that get_style_file_path returns correct path."""
        def mock_styles_dir():
            return temp_dir
        monkeypatch.setattr('gmaillm.helpers.config.get_styles_dir', mock_styles_dir)

        path = get_style_file_path("test-style")
        assert path == temp_dir / "test-style.md"

    def test_get_groups_file_path(self, temp_dir, monkeypatch):
        """Test that get_groups_file_path returns correct path."""
        def mock_config_dir():
            return temp_dir
        monkeypatch.setattr('gmaillm.helpers.config.get_plugin_config_dir', mock_config_dir)

        path = get_groups_file_path()
        assert path == temp_dir / "email-groups.json"


class TestJsonConfig:
    """Tests for JSON configuration functions."""

    def test_load_json_config_existing_file(self, temp_dir):
        """Test loading an existing JSON config file."""
        config_file = temp_dir / "test.json"
        test_data = {"key": "value", "number": 42}
        config_file.write_text(json.dumps(test_data))

        result = load_json_config(config_file)
        assert result == test_data

    def test_load_json_config_nonexistent_file(self, temp_dir):
        """Test loading a nonexistent file returns empty dict."""
        config_file = temp_dir / "nonexistent.json"
        result = load_json_config(config_file)
        assert result == {}

    def test_load_json_config_invalid_json(self, temp_dir):
        """Test loading invalid JSON returns empty dict with warning."""
        config_file = temp_dir / "invalid.json"
        config_file.write_text("{invalid json")

        result = load_json_config(config_file)
        assert result == {}

    def test_save_json_config(self, temp_dir):
        """Test saving JSON config file."""
        config_file = temp_dir / "test.json"
        test_data = {"key": "value", "list": [1, 2, 3]}

        save_json_config(config_file, test_data)

        assert config_file.exists()
        loaded = json.loads(config_file.read_text())
        assert loaded == test_data

    def test_save_json_config_creates_parent_dirs(self, temp_dir):
        """Test that save_json_config creates parent directories."""
        config_file = temp_dir / "subdir" / "test.json"
        test_data = {"key": "value"}

        save_json_config(config_file, test_data)

        assert config_file.exists()
        loaded = json.loads(config_file.read_text())
        assert loaded == test_data


class TestEmailGroups:
    """Tests for email groups functions."""

    def test_load_email_groups(self, temp_dir, sample_email_groups):
        """Test loading email groups from file."""
        groups_file = temp_dir / "email-groups.json"
        groups_file.write_text(json.dumps(sample_email_groups))

        result = load_email_groups(groups_file)
        assert result == sample_email_groups

    def test_load_email_groups_filters_metadata(self, temp_dir):
        """Test that metadata keys (starting with _) are filtered out."""
        groups_data = {
            "team": ["user@example.com"],
            "_comment": "This is metadata",
            "_version": "1.0"
        }
        groups_file = temp_dir / "email-groups.json"
        groups_file.write_text(json.dumps(groups_data))

        result = load_email_groups(groups_file)
        assert "team" in result
        assert "_comment" not in result
        assert "_version" not in result

    def test_save_email_groups(self, temp_dir):
        """Test saving email groups to file."""
        groups_file = temp_dir / "email-groups.json"
        groups_data = {"team": ["alice@example.com", "bob@example.com"]}

        save_email_groups(groups_data, groups_file)

        assert groups_file.exists()
        loaded = json.loads(groups_file.read_text())
        assert loaded == groups_data

    def test_expand_email_groups_no_groups(self):
        """Test expanding emails when no groups are referenced."""
        recipients = ["alice@example.com", "bob@example.com"]
        groups = {}

        result = expand_email_groups(recipients, groups)
        assert result == recipients

    def test_expand_email_groups_with_group_ref(self):
        """Test expanding group references."""
        recipients = ["#team", "charlie@example.com"]
        groups = {"team": ["alice@example.com", "bob@example.com"]}

        result = expand_email_groups(recipients, groups)
        assert "alice@example.com" in result
        assert "bob@example.com" in result
        assert "charlie@example.com" in result
        assert "#team" not in result

    def test_expand_email_groups_removes_duplicates(self):
        """Test that duplicate emails are removed."""
        recipients = ["#team", "alice@example.com"]
        groups = {"team": ["alice@example.com", "bob@example.com"]}

        result = expand_email_groups(recipients, groups)
        # alice should only appear once
        assert result.count("alice@example.com") == 1
        assert len(result) == 2  # alice and bob

    def test_expand_email_groups_nonexistent_group(self):
        """Test that nonexistent group reference is kept as-is."""
        recipients = ["#nonexistent"]
        groups = {"team": ["alice@example.com"]}

        result = expand_email_groups(recipients, groups)
        # Nonexistent group kept as-is
        assert "#nonexistent" in result

    def test_expand_email_groups_nested_not_expanded(self):
        """Test that nested group references are not automatically expanded."""
        recipients = ["#outer"]
        groups = {
            "outer": ["#inner", "user@example.com"],
            "inner": ["nested@example.com"]
        }

        result = expand_email_groups(recipients, groups)
        # Nested groups are not automatically expanded
        assert "#inner" in result
        assert "user@example.com" in result


class TestStyleFunctions:
    """Tests for style-related functions."""

    def test_load_all_styles_empty_dir(self, temp_dir, monkeypatch):
        """Test loading styles from empty directory."""
        def mock_styles_dir():
            return temp_dir
        monkeypatch.setattr('gmaillm.helpers.config.get_styles_dir', mock_styles_dir)

        result = load_all_styles(temp_dir)
        assert result == []

    def test_load_all_styles_with_files(self, temp_dir):
        """Test loading styles from directory with style files."""
        # Create test style files
        style1 = temp_dir / "formal.md"
        style1.write_text("""---
name: formal
description: Test formal style
---

Content
""")

        style2 = temp_dir / "casual.md"
        style2.write_text("""---
name: casual
description: Test casual style
---

Content
""")

        result = load_all_styles(temp_dir)
        assert len(result) == 2
        assert any(s['name'] == 'formal' for s in result)
        assert any(s['name'] == 'casual' for s in result)

    def test_extract_style_metadata_with_frontmatter(self, temp_dir):
        """Test extracting metadata from style file with YAML frontmatter."""
        style_file = temp_dir / "test.md"
        style_file.write_text("""---
name: test-style
description: Test description
---

Content
""")

        result = extract_style_metadata(style_file)
        assert result['name'] == 'test-style'
        assert result['description'] == 'Test description'

    def test_extract_style_metadata_without_frontmatter(self, temp_dir):
        """Test extracting metadata from file without frontmatter."""
        style_file = temp_dir / "test.md"
        style_file.write_text("Just content, no frontmatter")

        result = extract_style_metadata(style_file)
        assert result['name'] == 'test'
        assert result['description'] == 'No description'

    def test_create_style_from_template(self, temp_dir):
        """Test creating style file from template."""
        output_path = temp_dir / "new-style.md"

        create_style_from_template("new-style", output_path)

        assert output_path.exists()
        content = output_path.read_text()
        assert 'name: "new-style"' in content
        assert '<examples>' in content
        assert '<greeting>' in content
        assert '<body>' in content
        assert '<closing>' in content
        assert '<do>' in content
        assert '<dont>' in content


class TestUtilityFunctions:
    """Tests for utility functions."""

    def test_create_backup(self, temp_dir):
        """Test creating a backup of a file."""
        original_file = temp_dir / "test.txt"
        original_file.write_text("Original content")

        backup_path = create_backup(original_file)

        assert backup_path.exists()
        assert backup_path.read_text() == "Original content"
        assert "backup" in backup_path.name
        assert original_file.stem in backup_path.name

    def test_create_backup_preserves_extension(self, temp_dir):
        """Test that backup preserves file extension."""
        original_file = temp_dir / "test.json"
        original_file.write_text('{"key": "value"}')

        backup_path = create_backup(original_file)

        assert backup_path.suffix == ".json"
        assert "backup" in backup_path.name
