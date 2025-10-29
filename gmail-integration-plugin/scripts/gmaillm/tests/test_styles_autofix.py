"""Comprehensive tests for StyleLinter autofix functionality.

This test module covers:
- Auto-fix trailing whitespace
- Auto-fix list item spacing
- Auto-fix combined issues
- Preservation of valid content during autofix
- Edge cases (empty lines, mixed whitespace, partial fixes)
- Verification that unfixable errors remain
"""

import pytest
from gmaillm.validators.styles import StyleLinter, StyleLintError


# Test Classes

class TestAutoFixTrailingWhitespace:
    """Test autofix for trailing whitespace."""

    def test_autofix_single_line_trailing_whitespace(self):
        """Test autofix removes trailing whitespace from single line."""
        linter = StyleLinter()
        content = "---\nname: \"test\"\n---  \n"

        fixed, errors = linter.lint_and_fix(content)

        # Trailing whitespace should be removed
        assert fixed == "---\nname: \"test\"\n---\n"

        # No formatting errors should remain for whitespace
        assert not any('trailing whitespace' in err.message.lower() for err in errors)

    def test_autofix_multiple_lines_trailing_whitespace(self):
        """Test autofix removes trailing whitespace from multiple lines."""
        linter = StyleLinter()
        content = "---\nname: \"test\"  \ndescription: \"When to use: test\"  \n---  \n"

        fixed, errors = linter.lint_and_fix(content)

        # All trailing whitespace should be removed
        assert fixed == "---\nname: \"test\"\ndescription: \"When to use: test\"\n---\n"

        # No formatting errors should remain
        assert not any('trailing whitespace' in err.message.lower() for err in errors)

    def test_autofix_preserves_content_with_trailing_whitespace(self):
        """Test autofix preserves actual content when removing trailing whitespace."""
        linter = StyleLinter()
        content = "---\nname: \"formal-business\"    \ndescription: \"When to use: professional communication\"   \n---\n"

        fixed, errors = linter.lint_and_fix(content)

        # Content should be preserved, only trailing spaces removed
        assert 'name: "formal-business"' in fixed
        assert 'description: "When to use: professional communication"' in fixed
        assert fixed.count('    ') == 0  # No trailing spaces
        assert fixed.count('   ') == 0

    def test_autofix_tabs_as_trailing_whitespace(self):
        """Test autofix removes trailing tabs."""
        linter = StyleLinter()
        content = "---\nname: \"test\"\t\t\ndescription: \"When to use: test\"\t\n---\n"

        fixed, errors = linter.lint_and_fix(content)

        # Tabs should be removed
        assert fixed == "---\nname: \"test\"\ndescription: \"When to use: test\"\n---\n"

    def test_autofix_mixed_trailing_whitespace(self):
        """Test autofix removes mixed spaces and tabs."""
        linter = StyleLinter()
        content = "---\nname: \"test\" \t \ndescription: \"When to use: test\"\t  \n---\n"

        fixed, errors = linter.lint_and_fix(content)

        # All trailing whitespace should be removed
        assert fixed == "---\nname: \"test\"\ndescription: \"When to use: test\"\n---\n"


class TestAutoFixListItemSpacing:
    """Test autofix for list item spacing."""

    def test_autofix_list_item_missing_space(self):
        """Test autofix adds space after hyphen in list items."""
        linter = StyleLinter()
        content = """---
name: "test"
description: "When to use: test style for various professional communications"
---

<do>

-Use proper spacing
-Format correctly

</do>

<dont>

-Skip formatting
-Ignore rules

</dont>
"""

        fixed, errors = linter.lint_and_fix(content)

        # Space should be added after hyphens
        assert '- Use proper spacing' in fixed
        assert '- Format correctly' in fixed
        assert '- Skip formatting' in fixed
        assert '- Ignore rules' in fixed

        # List syntax errors should not appear
        assert not any('list syntax' in err.message.lower() for err in errors)

    def test_autofix_list_item_already_correct(self):
        """Test autofix preserves correct list formatting."""
        linter = StyleLinter()
        content = """<do>

- Use proper spacing
- Format correctly

</do>
"""

        fixed, errors = linter.lint_and_fix(content)

        # Should remain unchanged
        assert '- Use proper spacing' in fixed
        assert '- Format correctly' in fixed

    def test_autofix_list_item_multiple_hyphens(self):
        """Test autofix handles multiple list items."""
        linter = StyleLinter()
        content = """<do>

-Item 1
-Item 2
-Item 3
-Item 4

</do>
"""

        fixed, errors = linter.lint_and_fix(content)

        # All should be fixed
        assert '- Item 1' in fixed
        assert '- Item 2' in fixed
        assert '- Item 3' in fixed
        assert '- Item 4' in fixed

    def test_autofix_list_item_preserves_indentation(self):
        """Test autofix preserves indentation in list items."""
        linter = StyleLinter()
        # Note: In actual style files, items should start at beginning of line
        content = """<do>

-First item with long text
-Second item

</do>
"""

        fixed, errors = linter.lint_and_fix(content)

        # Spacing should be added
        assert '- First item with long text' in fixed
        assert '- Second item' in fixed


class TestAutoFixCombinedIssues:
    """Test autofix with multiple issues simultaneously."""

    def test_autofix_trailing_whitespace_and_list_spacing(self):
        """Test autofix handles both trailing whitespace and list spacing."""
        linter = StyleLinter()
        content = """---
name: "test"
description: "When to use: test style for various professional communications"
---

<do>

-Use proper spacing
-Format correctly

</do>

<dont>

-Skip formatting

</dont>
"""

        fixed, errors = linter.lint_and_fix(content)

        # Both issues should be fixed
        assert fixed.count('  ') == 0  # No trailing double spaces
        assert '- Use proper spacing' in fixed
        assert '- Format correctly' in fixed
        assert '- Skip formatting' in fixed

    def test_autofix_complex_document(self):
        """Test autofix on complex document with multiple sections."""
        linter = StyleLinter()
        content = """---
name: "formal-business"
description: "When to use: professional business communication with clients"
---

<examples>

Example 1 here

---

Example 2 here

</examples>

<greeting>

-Dear {name}
-Good morning {name}

</greeting>

<body>

-Be clear
-Be professional

</body>

<closing>

-Best regards
-Sincerely

</closing>

<do>

-Use formal language
-Be respectful

</do>

<dont>

-Use slang
-Be casual

</dont>
"""

        fixed, errors = linter.lint_and_fix(content)

        # All trailing whitespace removed
        assert '  \n' not in fixed

        # All list items fixed
        assert '- Dear {name}' in fixed
        assert '- Be clear' in fixed
        assert '- Best regards' in fixed
        assert '- Use formal language' in fixed
        assert '- Use slang' in fixed


class TestAutoFixPreservation:
    """Test that autofix preserves valid content."""

    def test_autofix_preserves_frontmatter(self):
        """Test autofix preserves YAML frontmatter structure."""
        linter = StyleLinter()
        content = """---
name: "test-style"
description: "When to use: professional correspondence"
---
"""

        fixed, errors = linter.lint_and_fix(content)

        # Frontmatter structure preserved
        assert fixed.startswith('---\n')
        assert 'name: "test-style"' in fixed
        assert 'description: "When to use: professional correspondence"' in fixed

    def test_autofix_preserves_examples_separator(self):
        """Test autofix preserves example separator (---)."""
        linter = StyleLinter()
        content = """<examples>

Example 1

---

Example 2

</examples>
"""

        fixed, errors = linter.lint_and_fix(content)

        # Separator should be preserved
        assert '\n---\n' in fixed
        assert 'Example 1' in fixed
        assert 'Example 2' in fixed

    def test_autofix_preserves_empty_lines_between_sections(self):
        """Test autofix preserves structural empty lines."""
        linter = StyleLinter()
        content = """<do>

-Item 1
-Item 2

</do>

<dont>

-Item 3

</dont>
"""

        fixed, errors = linter.lint_and_fix(content)

        # Empty lines between sections preserved
        assert '\n\n</do>\n\n<dont>' in fixed or '</do>\n\n<dont>' in fixed

    def test_autofix_preserves_section_tags(self):
        """Test autofix preserves XML-style section tags."""
        linter = StyleLinter()
        content = """<do>
-Item
</do>
"""

        fixed, errors = linter.lint_and_fix(content)

        # Tags should be preserved
        assert '<do>' in fixed
        assert '</do>' in fixed


class TestAutoFixEdgeCases:
    """Test autofix edge cases."""

    def test_autofix_empty_content(self):
        """Test autofix handles empty content."""
        linter = StyleLinter()
        content = ""

        fixed, errors = linter.lint_and_fix(content)

        # Should not crash
        assert fixed == ""

    def test_autofix_only_whitespace(self):
        """Test autofix handles content with only whitespace."""
        linter = StyleLinter()
        content = "   \n  \n\t\n"

        fixed, errors = linter.lint_and_fix(content)

        # Should remove trailing whitespace
        assert fixed == "\n\n\n"

    def test_autofix_no_newline_at_end(self):
        """Test autofix handles content without final newline."""
        linter = StyleLinter()
        content = "---\nname: \"test\"\n---"

        fixed, errors = linter.lint_and_fix(content)

        # Should not add newline, just remove trailing spaces
        assert fixed == "---\nname: \"test\"\n---"

    def test_autofix_consecutive_empty_lines(self):
        """Test autofix preserves multiple consecutive empty lines."""
        linter = StyleLinter()
        content = "---\nname: \"test\"\n\n\n\n---\n"

        fixed, errors = linter.lint_and_fix(content)

        # Empty lines should be preserved
        assert '\n\n\n\n' in fixed

    def test_autofix_unicode_content(self):
        """Test autofix handles Unicode content correctly."""
        linter = StyleLinter()
        content = "---\nname: \"test\"  \ndescription: \"When to use: café résumé\"  \n---\n"

        fixed, errors = linter.lint_and_fix(content)

        # Unicode should be preserved
        assert 'café résumé' in fixed
        # Trailing whitespace should be removed
        assert '  \n' not in fixed


class TestAutoFixUnfixableErrors:
    """Test that unfixable errors remain after autofix."""

    def test_unfixable_missing_sections(self):
        """Test that missing section errors remain after autofix."""
        linter = StyleLinter()
        content = """---
name: "test"
description: "When to use: test style"
---

<do>
- Item 1
- Item 2
</do>
"""
        # Missing: examples, greeting, body, closing, dont

        fixed, errors = linter.lint_and_fix(content)

        # Should have errors for missing sections
        assert any('examples' in err.section.lower() for err in errors)
        assert any('greeting' in err.section.lower() for err in errors)
        assert any('body' in err.section.lower() for err in errors)

    def test_unfixable_wrong_section_order(self):
        """Test that section order errors remain after autofix."""
        linter = StyleLinter()
        content = """---
name: "test"
description: "When to use: test style for professional communications"
---

<do>
- Item 1
- Item 2
</do>

<examples>
Example 1
</examples>
"""
        # Wrong order: do before examples

        fixed, errors = linter.lint_and_fix(content)

        # Should have error about order
        assert any('order' in err.message.lower() for err in errors)

    def test_unfixable_invalid_frontmatter(self):
        """Test that frontmatter errors remain after autofix."""
        linter = StyleLinter()
        content = """---
name: "x"
description: "Short"
---
"""
        # Name too short, description doesn't start with "When to use:" and too short

        fixed, errors = linter.lint_and_fix(content)

        # Should have frontmatter errors
        assert any('frontmatter' in err.section.lower() for err in errors)

    def test_unfixable_empty_sections(self):
        """Test that empty section errors remain after autofix."""
        linter = StyleLinter()
        content = """---
name: "test-style"
description: "When to use: test style for professional communications"
---

<examples>

</examples>

<greeting>
</greeting>

<body>
</body>

<closing>
</closing>

<do>
</do>

<dont>
</dont>
"""

        fixed, errors = linter.lint_and_fix(content)

        # Should have errors for empty sections
        assert any('empty' in err.message.lower() for err in errors)


class TestAutoFixReturnValues:
    """Test autofix return values."""

    def test_autofix_returns_fixed_content_and_errors(self):
        """Test autofix returns tuple of (fixed_content, errors)."""
        linter = StyleLinter()
        content = "---\nname: \"test\"  \n---\n"

        result = linter.lint_and_fix(content)

        # Should return tuple
        assert isinstance(result, tuple)
        assert len(result) == 2

        fixed_content, errors = result
        assert isinstance(fixed_content, str)
        assert isinstance(errors, list)

    def test_autofix_fixed_content_different_from_original(self):
        """Test that fixed content differs from original when fixes applied."""
        linter = StyleLinter()
        content = "---\nname: \"test\"  \n---  \n"

        fixed, errors = linter.lint_and_fix(content)

        # Fixed should differ from original
        assert fixed != content
        assert '  \n' not in fixed

    def test_autofix_no_changes_when_content_valid(self):
        """Test that autofix doesn't change already valid formatting."""
        linter = StyleLinter()
        content = "---\nname: \"test\"\n---\n"

        fixed, errors = linter.lint_and_fix(content)

        # Should remain unchanged
        assert fixed == content
