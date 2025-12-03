"""Tests for gmaillm.validators.styles module."""

import pytest

from gmaillm.validators.styles import (
    validate_style_name,
    StyleLinter,
    StyleLintError
)


class TestValidateStyleName:
    """Tests for validate_style_name function."""

    def test_valid_style_names(self):
        """Test that valid style names pass validation."""
        valid_names = [
            "formal",
            "casual",
            "professional",
            "my-style",
            "my_style",
            "style123",
        ]
        for name in valid_names:
            # Should not raise
            validate_style_name(name)

    def test_empty_style_name(self):
        """Test that empty name raises typer.Exit."""
        import typer
        with pytest.raises(typer.Exit):
            validate_style_name("")

    def test_style_name_too_short(self):
        """Test that name shorter than min length raises typer.Exit."""
        import typer
        # Min length is 3
        with pytest.raises(typer.Exit):
            validate_style_name("ab")

    def test_style_name_too_long(self):
        """Test that name longer than max length raises typer.Exit."""
        import typer
        # Max length is 50
        long_name = "a" * 51
        with pytest.raises(typer.Exit):
            validate_style_name(long_name)

    def test_invalid_characters(self):
        """Test that invalid characters raise typer.Exit."""
        import typer
        invalid_names = [
            "style with spaces",
            "style/slash",
            "style\\backslash",
            "style<tag>",
            "style&amp",
            'style"quote',
            "style'quote",
            "style`backtick",
        ]
        for name in invalid_names:
            with pytest.raises(typer.Exit):
                validate_style_name(name)

    def test_reserved_names(self):
        """Test that reserved names raise typer.Exit."""
        import typer
        reserved_names = ["default", "template", "base", "system"]
        for name in reserved_names:
            with pytest.raises(typer.Exit):
                validate_style_name(name)


class TestStyleLintError:
    """Tests for StyleLintError dataclass."""

    def test_error_without_line(self):
        """Test formatting error without line number."""
        error = StyleLintError('test', 'Test message')
        assert str(error) == '[test] Test message'

    def test_error_with_line(self):
        """Test formatting error with line number."""
        error = StyleLintError('test', 'Test message', line=42)
        assert str(error) == '[test] Line 42: Test message'


class TestStyleLinter:
    """Tests for StyleLinter class."""

    @pytest.fixture
    def linter(self):
        """Create a StyleLinter instance."""
        return StyleLinter()

    @pytest.fixture
    def valid_style_content(self):
        """Minimal valid style content."""
        return """---
name: "test-style"
description: "When to use: This is a test style for testing purposes and validation checks."
---

<examples>
Hi John,

Test example.

Best,
Warren
</examples>

<greeting>
- Hi [Name],
</greeting>

<body>
- Keep it simple
</body>

<closing>
- Best,
</closing>

<do>
- Be clear
- Be concise
</do>

<dont>
- Be vague
- Be wordy
</dont>
"""

    def test_valid_content_passes(self, linter, valid_style_content):
        """Test that valid content has no errors."""
        errors = linter.lint(valid_style_content)
        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_missing_frontmatter(self, linter):
        """Test that missing frontmatter is detected."""
        content = "<examples>Test</examples>"
        errors = linter.lint(content)
        assert any('Missing YAML frontmatter' in str(e) for e in errors)

    def test_invalid_yaml(self, linter):
        """Test that invalid YAML is detected."""
        content = """---
name: test
invalid yaml: [unclosed
---"""
        errors = linter.lint(content)
        assert any('Invalid YAML' in str(e) for e in errors)

    def test_missing_name_field(self, linter):
        """Test that missing name field is detected."""
        content = """---
description: "When to use: Test"
---

<examples>Test</examples>
<greeting>Hi</greeting>
<body>Test</body>
<closing>Best</closing>
<do>Do this</do>
<dont>Dont this</dont>
"""
        errors = linter.lint(content)
        assert any('Missing "name" field' in str(e) for e in errors)

    def test_missing_description_field(self, linter):
        """Test that missing description field is detected."""
        content = """---
name: "test"
---

<examples>Test</examples>
<greeting>Hi</greeting>
<body>Test</body>
<closing>Best</closing>
<do>Do this</do>
<dont>Dont this</dont>
"""
        errors = linter.lint(content)
        assert any('Missing "description" field' in str(e) for e in errors)

    def test_description_wrong_format(self, linter):
        """Test that description not starting with 'When to use:' is detected."""
        content = """---
name: "test"
description: "This is wrong format"
---

<examples>Test</examples>
<greeting>Hi</greeting>
<body>Test</body>
<closing>Best</closing>
<do>Do this</do>
<dont>Dont this</dont>
"""
        errors = linter.lint(content)
        assert any('must start with "When to use:"' in str(e) for e in errors)

    def test_missing_required_section(self, linter):
        """Test that missing required sections are detected."""
        content = """---
name: "test-style"
description: "When to use: Test style for testing purposes and validation."
---

<examples>Test</examples>
"""
        errors = linter.lint(content)
        # Should have errors for missing greeting, body, closing, do, dont
        assert len(errors) >= 5

    def test_unclosed_section(self, linter):
        """Test that unclosed sections are detected."""
        content = """---
name: "test"
description: "When to use: Test"
---

<examples>
Test
"""
        errors = linter.lint(content)
        assert any('not properly closed' in str(e) for e in errors)

    def test_empty_section(self, linter):
        """Test that empty sections are detected."""
        content = """---
name: "test-style"
description: "When to use: Test style for testing purposes and validation."
---

<examples></examples>
<greeting></greeting>
<body></body>
<closing></closing>
<do></do>
<dont></dont>
"""
        errors = linter.lint(content)
        assert any('is empty' in str(e) for e in errors)

    def test_section_order(self, linter):
        """Test that wrong section order is detected."""
        content = """---
name: "test-style"
description: "When to use: Test style for testing purposes and validation."
---

<body>
- Test
</body>

<examples>
Test
</examples>

<greeting>
- Hi,
</greeting>

<closing>
- Best,
</closing>

<do>
- Do this
- Do that
</do>

<dont>
- Dont this
- Dont that
</dont>
"""
        errors = linter.lint(content)
        assert any('out of order' in str(e) for e in errors)

    def test_lint_and_fix_trailing_whitespace(self, linter):
        """Test that trailing whitespace is auto-fixed."""
        content = """---
name: "test"
description: "When to use: Test"
---

<examples>
Test
</examples>

<greeting>
- Hi,
</greeting>

<body>
- Test
</body>

<closing>
- Best,
</closing>

<do>
- Do
- This
</do>

<dont>
- Dont
- This
</dont>
"""
        fixed_content, errors = linter.lint_and_fix(content)
        # Trailing whitespace should be fixed
        assert '   \n' not in fixed_content
        assert '  \n' not in fixed_content


class TestConvertJsonToMarkdownStyle:
    """Tests for create_style_from_json function."""

    def test_convert_valid_json_to_markdown(self, tmp_path):
        """Test converting valid JSON to markdown style file."""
        from gmaillm.validators.styles import create_style_from_json
        
        json_data = {
            "name": "test-style",
            "description": "When to use: For testing purposes with adequate description length.",
            "examples": ["Example 1", "Example 2"],
            "greeting": ["Hi,", "Hello,"],
            "body": ["Keep it brief.", "Be clear."],
            "closing": ["Best,", "Thanks,"],
            "do": ["Be professional", "Be concise"],
            "dont": ["Don't ramble", "Don't be vague"]
        }
        
        output_file = tmp_path / "test-style.md"
        create_style_from_json(json_data, output_file)
        
        assert output_file.exists()
        content = output_file.read_text()
        
        # Check YAML frontmatter
        assert "---" in content
        assert 'name: "test-style"' in content
        assert 'description: "When to use:' in content
        
        # Check all sections exist
        assert "<examples>" in content
        assert "</examples>" in content
        assert "<greeting>" in content
        assert "</greeting>" in content
        assert "<body>" in content
        assert "</body>" in content
        assert "<closing>" in content
        assert "</closing>" in content
        assert "<do>" in content
        assert "</do>" in content
        assert "<dont>" in content
        assert "</dont>" in content
        
        # Check content
        assert "Example 1" in content
        assert "- Hi," in content
        assert "- Keep it brief." in content
        assert "- Best," in content
        assert "- Be professional" in content
        assert "- Don't ramble" in content

    def test_convert_with_single_example(self, tmp_path):
        """Test converting with single example (no separator needed)."""
        from gmaillm.validators.styles import create_style_from_json
        
        json_data = {
            "name": "simple",
            "description": "When to use: Simple style with one example only for testing.",
            "examples": ["Only one example"],
            "greeting": ["Hi,"],
            "body": ["Be brief."],
            "closing": ["Thanks,"],
            "do": ["Do this", "Do that"],
            "dont": ["Don't this", "Don't that"]
        }
        
        output_file = tmp_path / "simple.md"
        create_style_from_json(json_data, output_file)
        
        content = output_file.read_text()
        assert "Only one example" in content
        # Should not have --- separator between examples
        assert content.count("---") == 2  # Only YAML frontmatter delimiters

    def test_convert_with_multiple_examples(self, tmp_path):
        """Test converting with multiple examples (separator needed)."""
        from gmaillm.validators.styles import create_style_from_json
        
        json_data = {
            "name": "multi",
            "description": "When to use: Style with multiple examples for testing purposes.",
            "examples": ["Example 1", "Example 2", "Example 3"],
            "greeting": ["Hi,"],
            "body": ["Be brief."],
            "closing": ["Thanks,"],
            "do": ["Do this", "Do that"],
            "dont": ["Don't this", "Don't that"]
        }
        
        output_file = tmp_path / "multi.md"
        create_style_from_json(json_data, output_file)
        
        content = output_file.read_text()
        # Should have separators between examples
        assert "Example 1" in content
        assert "Example 2" in content
        assert "Example 3" in content

    def test_convert_invalid_json_raises_error(self, tmp_path):
        """Test that invalid JSON raises ValueError."""
        from gmaillm.validators.styles import create_style_from_json
        
        invalid_json = {
            "name": "A",  # Too short
            "description": "Short",  # Wrong format
            "examples": []  # Too few
        }
        
        output_file = tmp_path / "invalid.md"
        
        with pytest.raises(ValueError, match="Invalid JSON data"):
            create_style_from_json(invalid_json, output_file)

    def test_convert_missing_required_field(self, tmp_path):
        """Test that missing required field raises ValueError."""
        from gmaillm.validators.styles import create_style_from_json
        
        incomplete_json = {
            "name": "test-style",
            # Missing description and other fields
        }
        
        output_file = tmp_path / "incomplete.md"
        
        with pytest.raises(ValueError, match="Invalid JSON data"):
            create_style_from_json(incomplete_json, output_file)

    def test_convert_creates_proper_list_format(self, tmp_path):
        """Test that list items are formatted with bullet points."""
        from gmaillm.validators.styles import create_style_from_json
        
        json_data = {
            "name": "list-test",
            "description": "When to use: Testing list formatting in markdown output style.",
            "examples": ["Example"],
            "greeting": ["First greeting", "Second greeting"],
            "body": ["First body item", "Second body item"],
            "closing": ["First closing", "Second closing"],
            "do": ["First do", "Second do", "Third do"],
            "dont": ["First dont", "Second dont", "Third dont"]
        }
        
        output_file = tmp_path / "list-test.md"
        create_style_from_json(json_data, output_file)
        
        content = output_file.read_text()
        
        # All list items should have "- " prefix
        assert "- First greeting" in content
        assert "- Second greeting" in content
        assert "- First body item" in content
        assert "- Second body item" in content
        assert "- First do" in content
        assert "- Third do" in content
        assert "- First dont" in content
        assert "- Third dont" in content
