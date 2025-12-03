"""Tests for helpers/domain/styles.py module."""

import pytest
from pathlib import Path

from gmaillm.helpers.domain.styles import (
    load_all_styles,
    extract_style_metadata,
)


class TestLoadAllStyles:
    """Test load_all_styles function."""

    def test_empty_directory(self, tmp_path):
        """Test with empty styles directory."""
        styles = load_all_styles(tmp_path)
        assert styles == []

    def test_single_valid_style(self, tmp_path):
        """Test with one valid style file."""
        style_file = tmp_path / "test-style.md"
        style_file.write_text("""---
name: "Test Style"
description: "When to use: For testing purposes."
---

<examples>
Example 1
</examples>
""")

        styles = load_all_styles(tmp_path)

        assert len(styles) == 1
        assert styles[0]['name'] == 'test-style'
        assert 'description' in styles[0]
        assert styles[0]['path'] == style_file

    def test_multiple_styles_sorted(self, tmp_path):
        """Test multiple styles are sorted by name."""
        (tmp_path / "zebra.md").write_text("---\nname: Zebra\n---\n")
        (tmp_path / "alpha.md").write_text("---\nname: Alpha\n---\n")
        (tmp_path / "beta.md").write_text("---\nname: Beta\n---\n")

        styles = load_all_styles(tmp_path)

        assert len(styles) == 3
        assert styles[0]['name'] == 'alpha'
        assert styles[1]['name'] == 'beta'
        assert styles[2]['name'] == 'zebra'

    def test_non_markdown_files_ignored(self, tmp_path):
        """Test non-.md files are ignored."""
        (tmp_path / "style.md").write_text("---\nname: Style\n---\n")
        (tmp_path / "readme.txt").write_text("Not a style")
        (tmp_path / "config.yaml").write_text("key: value")

        styles = load_all_styles(tmp_path)

        # Should only find the .md file
        assert len(styles) == 1
        assert styles[0]['name'] == 'style'


class TestExtractStyleMetadata:
    """Test extract_style_metadata function."""

    def test_valid_yaml_frontmatter(self, tmp_path):
        """Test extracting valid YAML frontmatter."""
        style_file = tmp_path / "test.md"
        style_file.write_text("""---
name: "Professional"
description: "When to use: For business communications."
---

Content here
""")

        metadata = extract_style_metadata(style_file)

        assert metadata['name'] == 'Professional'
        assert metadata['description'] == 'When to use: For business communications.'

    def test_frontmatter_with_complex_yaml(self, tmp_path):
        """Test frontmatter with nested YAML structures."""
        style_file = tmp_path / "test.md"
        style_file.write_text("""---
name: "Complex"
description: "Test"
tags:
  - professional
  - formal
settings:
  auto_format: true
---

Content
""")

        metadata = extract_style_metadata(style_file)

        assert metadata['name'] == 'Complex'
        assert 'tags' in metadata
        assert 'settings' in metadata

    def test_no_frontmatter_returns_default(self, tmp_path):
        """Test file without frontmatter returns minimal metadata."""
        style_file = tmp_path / "test.md"
        style_file.write_text("Just plain content without frontmatter")

        metadata = extract_style_metadata(style_file)

        # Should return some default/minimal metadata
        assert isinstance(metadata, dict)

    def test_malformed_yaml_frontmatter(self, tmp_path):
        """Test malformed YAML in frontmatter returns fallback."""
        style_file = tmp_path / "test.md"
        style_file.write_text("""---
name: "Test"
invalid: [unclosed bracket
---

Content
""")

        metadata = extract_style_metadata(style_file)

        # Should handle error gracefully and return fallback
        assert isinstance(metadata, dict)

    def test_frontmatter_missing_closing_delimiter(self, tmp_path):
        """Test frontmatter without closing --- delimiter."""
        style_file = tmp_path / "test.md"
        style_file.write_text("""---
name: "Test"
description: "No closing delimiter"

Content here
""")

        metadata = extract_style_metadata(style_file)

        # Should fallback gracefully
        assert isinstance(metadata, dict)

    def test_empty_file(self, tmp_path):
        """Test empty file returns minimal metadata."""
        style_file = tmp_path / "empty.md"
        style_file.write_text("")

        metadata = extract_style_metadata(style_file)

        assert isinstance(metadata, dict)

    def test_frontmatter_with_special_characters(self, tmp_path):
        """Test frontmatter with special characters."""
        style_file = tmp_path / "test.md"
        style_file.write_text("""---
name: "Test & Style"
description: "When to use: For emails with special chars: <>, &, etc."
---

Content
""")

        metadata = extract_style_metadata(style_file)

        assert 'name' in metadata
        assert 'description' in metadata
