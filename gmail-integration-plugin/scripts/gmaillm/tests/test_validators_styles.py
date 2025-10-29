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
