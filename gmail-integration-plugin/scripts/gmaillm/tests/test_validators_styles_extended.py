"""Extended comprehensive tests for style validators.

This test module covers:
- JSON schema validation edge cases
- StyleLinter section validation
- Style name validation edge cases
- Frontmatter validation details
- Section content validation
- Section ordering validation
- Format validation
- create_style_from_json functionality
"""

import pytest
import json
from pathlib import Path
from gmaillm.validators.styles import (
    validate_style_name,
    validate_json_against_schema,
    create_style_from_json,
    StyleLinter,
    get_style_json_schema,
    get_style_json_schema_string,
)
from rich.console import Console


# Test Classes

class TestJsonSchemaEdgeCases:
    """Test JSON schema validation edge cases."""

    def test_validate_json_all_fields_valid(self):
        """Test validation passes with all valid fields."""
        data = {
            "name": "test-style",
            "description": "When to use: professional business communications with clients",
            "examples": ["Example 1 content here"],
            "greeting": ["Dear {name}"],
            "body": ["Be clear and concise"],
            "closing": ["Best regards"],
            "do": ["Use formal language", "Be respectful"],
            "dont": ["Use slang", "Be overly casual"],
        }

        errors = validate_json_against_schema(data)

        assert len(errors) == 0

    def test_validate_json_missing_optional_examples(self):
        """Test validation allows minimum 1 example."""
        data = {
            "name": "test-style",
            "description": "When to use: professional business communications with clients",
            "examples": ["Single example"],  # Min 1
            "greeting": ["Hi {name}"],
            "body": ["Be clear"],
            "closing": ["Regards"],
            "do": ["Item 1", "Item 2"],
            "dont": ["Item 1", "Item 2"],
        }

        errors = validate_json_against_schema(data)

        assert len(errors) == 0

    def test_validate_json_maximum_examples(self):
        """Test validation allows maximum 3 examples."""
        data = {
            "name": "test-style",
            "description": "When to use: professional business communications with clients",
            "examples": ["Example 1", "Example 2", "Example 3"],  # Max 3
            "greeting": ["Hi {name}"],
            "body": ["Be clear"],
            "closing": ["Regards"],
            "do": ["Item 1", "Item 2"],
            "dont": ["Item 1", "Item 2"],
        }

        errors = validate_json_against_schema(data)

        assert len(errors) == 0

    def test_validate_json_too_many_examples(self):
        """Test validation fails with > 3 examples."""
        data = {
            "name": "test-style",
            "description": "When to use: professional business communications with clients",
            "examples": ["Ex 1", "Ex 2", "Ex 3", "Ex 4"],  # Too many
            "greeting": ["Hi"],
            "body": ["Clear"],
            "closing": ["Regards"],
            "do": ["A", "B"],
            "dont": ["C", "D"],
        }

        errors = validate_json_against_schema(data)

        assert any("examples" in err and "at most 3" in err for err in errors)

    def test_validate_json_empty_string_in_array(self):
        """Test validation fails with empty strings in arrays."""
        data = {
            "name": "test-style",
            "description": "When to use: professional business communications with clients",
            "examples": ["Example 1"],
            "greeting": ["Hi", ""],  # Empty string
            "body": ["Be clear"],
            "closing": ["Regards"],
            "do": ["Item 1", "Item 2"],
            "dont": ["Item 1", "Item 2"],
        }

        errors = validate_json_against_schema(data)

        assert any("greeting" in err and "cannot be empty" in err for err in errors)

    def test_validate_json_whitespace_only_string(self):
        """Test validation fails with whitespace-only strings."""
        data = {
            "name": "test-style",
            "description": "When to use: professional business communications with clients",
            "examples": ["Example 1"],
            "greeting": ["Hi"],
            "body": ["   "],  # Whitespace only
            "closing": ["Regards"],
            "do": ["Item 1", "Item 2"],
            "dont": ["Item 1", "Item 2"],
        }

        errors = validate_json_against_schema(data)

        assert any("body" in err and "cannot be empty" in err for err in errors)

    def test_validate_json_non_string_in_array(self):
        """Test validation fails with non-string items in arrays."""
        data = {
            "name": "test-style",
            "description": "When to use: professional business communications with clients",
            "examples": ["Example 1"],
            "greeting": ["Hi"],
            "body": ["Clear", 123],  # Number instead of string
            "closing": ["Regards"],
            "do": ["A", "B"],
            "dont": ["C", "D"],
        }

        errors = validate_json_against_schema(data)

        assert any("body" in err and "must be a string" in err for err in errors)

    def test_validate_json_unexpected_fields(self):
        """Test validation detects unexpected fields."""
        data = {
            "name": "test-style",
            "description": "When to use: professional business communications with clients",
            "examples": ["Example 1"],
            "greeting": ["Hi"],
            "body": ["Clear"],
            "closing": ["Regards"],
            "do": ["A", "B"],
            "dont": ["C", "D"],
            "extra_field": "should not be here",
            "another_extra": 123,
        }

        errors = validate_json_against_schema(data)

        assert any("Unexpected fields" in err for err in errors)
        assert any("extra_field" in err for err in errors)
        assert any("another_extra" in err for err in errors)

    def test_validate_json_non_dict_input(self):
        """Test validation handles non-dict input gracefully."""
        # Passing a list instead of dict
        data = ["not", "a", "dict"]

        # Should raise AttributeError when trying to check required fields
        with pytest.raises(AttributeError):
            validate_json_against_schema(data)

    def test_validate_json_wrong_type_for_name(self):
        """Test validation fails when name is not a string."""
        data = {
            "name": 123,  # Should be string
            "description": "When to use: professional business communications",
            "examples": ["Example"],
            "greeting": ["Hi"],
            "body": ["Clear"],
            "closing": ["Regards"],
            "do": ["A", "B"],
            "dont": ["C", "D"],
        }

        errors = validate_json_against_schema(data)

        assert any("name" in err and "must be a string" in err for err in errors)

    def test_validate_json_wrong_type_for_description(self):
        """Test validation fails when description is not a string."""
        data = {
            "name": "test-style",
            "description": ["not", "a", "string"],  # Should be string
            "examples": ["Example"],
            "greeting": ["Hi"],
            "body": ["Clear"],
            "closing": ["Regards"],
            "do": ["A", "B"],
            "dont": ["C", "D"],
        }

        errors = validate_json_against_schema(data)

        assert any("description" in err and "must be a string" in err for err in errors)

    def test_validate_json_wrong_type_for_arrays(self):
        """Test validation fails when array fields are not arrays."""
        data = {
            "name": "test-style",
            "description": "When to use: professional business communications",
            "examples": "not an array",  # Should be array
            "greeting": ["Hi"],
            "body": ["Clear"],
            "closing": ["Regards"],
            "do": ["A", "B"],
            "dont": ["C", "D"],
        }

        errors = validate_json_against_schema(data)

        assert any("examples" in err and "must be an array" in err for err in errors)


class TestStyleNameValidationEdgeCases:
    """Test style name validation edge cases."""

    def test_validate_style_name_exactly_min_length(self):
        """Test name with exactly minimum length (3) is valid."""
        # Should not raise
        try:
            validate_style_name("abc")
        except SystemExit:
            pytest.fail("Should accept name with min length 3")

    def test_validate_style_name_exactly_max_length(self):
        """Test name with exactly maximum length (50) is valid."""
        name = "a" * 50
        # Should not raise
        try:
            validate_style_name(name)
        except SystemExit:
            pytest.fail("Should accept name with max length 50")

    def test_validate_style_name_just_below_min(self):
        """Test name with length 2 (below min 3) fails."""
        with pytest.raises(SystemExit):
            validate_style_name("ab")

    def test_validate_style_name_just_above_max(self):
        """Test name with length 51 (above max 50) fails."""
        name = "a" * 51
        with pytest.raises(SystemExit):
            validate_style_name(name)

    def test_validate_style_name_with_space(self):
        """Test name with space fails."""
        with pytest.raises(SystemExit):
            validate_style_name("test style")

    def test_validate_style_name_with_special_chars(self):
        """Test name with special characters fails."""
        special_chars = ['/', '\\', '<', '>', '&', '"', "'", '`']

        for char in special_chars:
            with pytest.raises(SystemExit):
                validate_style_name(f"test{char}style")

    def test_validate_style_name_reserved_names(self):
        """Test reserved names fail validation."""
        reserved = ['default', 'template', 'base', 'system']

        for name in reserved:
            with pytest.raises(SystemExit):
                validate_style_name(name)

    def test_validate_style_name_reserved_case_insensitive(self):
        """Test reserved names are case-insensitive."""
        with pytest.raises(SystemExit):
            validate_style_name("DEFAULT")

        with pytest.raises(SystemExit):
            validate_style_name("Template")

    def test_validate_style_name_empty_string(self):
        """Test empty string fails validation."""
        with pytest.raises(SystemExit):
            validate_style_name("")

    def test_validate_style_name_with_hyphens(self):
        """Test name with hyphens is valid."""
        # Should not raise
        try:
            validate_style_name("test-style-name")
        except SystemExit:
            pytest.fail("Should accept hyphens in name")

    def test_validate_style_name_with_numbers(self):
        """Test name with numbers is valid."""
        try:
            validate_style_name("test123")
        except SystemExit:
            pytest.fail("Should accept numbers in name")


class TestStyleLinterSectionValidation:
    """Test StyleLinter section-specific validation."""

    def test_lint_sections_all_present(self):
        """Test linting passes when all sections present."""
        linter = StyleLinter()
        content = """---
name: "test"
description: "When to use: test style for professional communications"
---

<examples>
Example 1
</examples>

<greeting>
- Hi
</greeting>

<body>
- Clear
</body>

<closing>
- Regards
</closing>

<do>
- Item 1
- Item 2
</do>

<dont>
- Item 1
- Item 2
</dont>
"""

        errors = linter._lint_sections_exist(content)

        assert len(errors) == 0

    def test_lint_sections_missing_opening_tag(self):
        """Test linting detects missing opening tag."""
        linter = StyleLinter()
        content = "Content without opening tag\n</examples>"

        errors = linter._lint_sections_exist(content)

        assert any("Missing required section: <examples>" in err.message for err in errors)

    def test_lint_sections_missing_closing_tag(self):
        """Test linting detects missing closing tag."""
        linter = StyleLinter()
        content = "<examples>\nContent without closing tag"

        errors = linter._lint_sections_exist(content)

        assert any("not properly closed" in err.message for err in errors)

    def test_lint_sections_correct_order(self):
        """Test linting validates correct section order."""
        linter = StyleLinter()
        content = """<examples>
Example
</examples>

<greeting>
- Hi
</greeting>

<body>
- Clear
</body>

<closing>
- Regards
</closing>

<do>
- A
</do>

<dont>
- B
</dont>
"""

        errors = linter._lint_sections_order(content)

        assert len(errors) == 0

    def test_lint_sections_wrong_order(self):
        """Test linting detects wrong section order."""
        linter = StyleLinter()
        content = """<do>
- A
</do>

<examples>
Example
</examples>
"""

        errors = linter._lint_sections_order(content)

        assert any("out of order" in err.message for err in errors)

    def test_lint_section_content_empty(self):
        """Test linting detects empty sections."""
        linter = StyleLinter()
        content = """<do>

</do>
"""

        errors = linter._lint_section_content(content)

        assert any("empty" in err.message.lower() for err in errors)

    def test_lint_section_content_no_list_items(self):
        """Test linting detects sections without list items."""
        linter = StyleLinter()
        content = """<do>
Just text without list items
</do>
"""

        errors = linter._lint_section_content(content)

        assert any("must contain list items" in err.message for err in errors)

    def test_lint_section_content_too_few_do_items(self):
        """Test linting detects < 2 items in do section."""
        linter = StyleLinter()
        content = """<do>
- Only one item
</do>
"""

        errors = linter._lint_section_content(content)

        assert any("at least 2 items" in err.message for err in errors)

    def test_lint_section_content_too_few_dont_items(self):
        """Test linting detects < 2 items in dont section."""
        linter = StyleLinter()
        content = """<dont>
- Only one item
</dont>
"""

        errors = linter._lint_section_content(content)

        assert any("at least 2 items" in err.message for err in errors)


class TestCreateStyleFromJson:
    """Test create_style_from_json functionality."""

    def test_create_style_from_valid_json(self, tmp_path):
        """Test creating style file from valid JSON."""
        data = {
            "name": "test-style",
            "description": "When to use: professional business communications with clients",
            "examples": ["Example 1 content here"],
            "greeting": ["Dear {name}"],
            "body": ["Be clear and concise"],
            "closing": ["Best regards"],
            "do": ["Use formal language", "Be respectful"],
            "dont": ["Use slang", "Be overly casual"],
        }

        output_path = tmp_path / "test-style.md"
        create_style_from_json(data, output_path)

        # Verify file was created
        assert output_path.exists()

        # Verify content
        content = output_path.read_text()
        assert 'name: "test-style"' in content
        assert "When to use: professional business communications" in content
        assert "<examples>" in content
        assert "<greeting>" in content
        assert "<body>" in content
        assert "<closing>" in content
        assert "<do>" in content
        assert "<dont>" in content

    def test_create_style_from_json_invalid_raises(self, tmp_path):
        """Test creating style with invalid JSON raises ValueError."""
        data = {
            "name": "x",  # Too short
            "description": "Short",  # Missing "When to use:" prefix and too short
            # Missing required fields
        }

        output_path = tmp_path / "test.md"

        with pytest.raises(ValueError, match="Invalid JSON data"):
            create_style_from_json(data, output_path)

    def test_create_style_preserves_multiple_examples(self, tmp_path):
        """Test creating style with multiple examples preserves separator."""
        data = {
            "name": "test-style",
            "description": "When to use: professional business communications with clients",
            "examples": ["Example 1", "Example 2", "Example 3"],
            "greeting": ["Hi"],
            "body": ["Clear"],
            "closing": ["Regards"],
            "do": ["A", "B"],
            "dont": ["C", "D"],
        }

        output_path = tmp_path / "test.md"
        create_style_from_json(data, output_path)

        content = output_path.read_text()

        # Check examples are separated by ---
        assert "Example 1" in content
        assert "\n---\n" in content
        assert "Example 2" in content
        assert "Example 3" in content

    def test_create_style_formats_lists_correctly(self, tmp_path):
        """Test creating style formats list items with hyphens."""
        data = {
            "name": "test-style",
            "description": "When to use: professional business communications with clients",
            "examples": ["Example"],
            "greeting": ["Dear {name}", "Hello {name}"],
            "body": ["Point 1", "Point 2", "Point 3"],
            "closing": ["Best", "Regards"],
            "do": ["Do 1", "Do 2"],
            "dont": ["Dont 1", "Dont 2"],
        }

        output_path = tmp_path / "test.md"
        create_style_from_json(data, output_path)

        content = output_path.read_text()

        # All items should be formatted as "- Item"
        assert "- Dear {name}" in content
        assert "- Hello {name}" in content
        assert "- Point 1" in content
        assert "- Do 1" in content
        assert "- Dont 1" in content


class TestGetSchemaFunctions:
    """Test schema getter functions."""

    def test_get_style_json_schema_returns_dict(self):
        """Test get_style_json_schema returns dictionary."""
        schema = get_style_json_schema()

        assert isinstance(schema, dict)
        assert "$schema" in schema
        assert "required" in schema
        assert "properties" in schema

    def test_get_style_json_schema_string_returns_string(self):
        """Test get_style_json_schema_string returns string."""
        schema_str = get_style_json_schema_string()

        assert isinstance(schema_str, str)
        # Should be valid JSON
        schema = json.loads(schema_str)
        assert "$schema" in schema

    def test_get_style_json_schema_string_custom_indent(self):
        """Test get_style_json_schema_string with custom indent."""
        schema_str = get_style_json_schema_string(indent=4)

        # Should have 4-space indentation
        assert "    " in schema_str


class TestFrontmatterValidation:
    """Test frontmatter validation details."""

    def test_lint_frontmatter_missing(self):
        """Test linting detects missing frontmatter."""
        linter = StyleLinter()
        content = "Content without frontmatter"

        errors = linter._lint_frontmatter(content)

        assert any("Missing YAML frontmatter" in err.message for err in errors)

    def test_lint_frontmatter_not_closed(self):
        """Test linting detects unclosed frontmatter."""
        linter = StyleLinter()
        content = "---\nname: test\n"  # Missing closing ---

        errors = linter._lint_frontmatter(content)

        assert any("missing closing ---" in err.message for err in errors)

    def test_lint_frontmatter_invalid_yaml(self):
        """Test linting detects invalid YAML syntax."""
        linter = StyleLinter()
        content = "---\n{invalid yaml\n---\n"

        errors = linter._lint_frontmatter(content)

        assert any("Invalid YAML syntax" in err.message for err in errors)

    def test_lint_frontmatter_extra_fields(self):
        """Test linting detects unexpected fields in frontmatter."""
        linter = StyleLinter()
        content = """---
name: "test"
description: "When to use: test style for professional communications"
extra_field: "should not be here"
---
"""

        errors = linter._lint_frontmatter(content)

        assert any("Unexpected fields" in err.message for err in errors)

    def test_lint_frontmatter_description_wrong_prefix(self):
        """Test linting detects description without 'When to use:' prefix."""
        linter = StyleLinter()
        content = """---
name: "test-style"
description: "This is a test style for various communications"
---
"""

        errors = linter._lint_frontmatter(content)

        assert any('must start with "When to use:"' in err.message for err in errors)
