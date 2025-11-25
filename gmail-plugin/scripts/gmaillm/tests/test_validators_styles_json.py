"""Tests for style JSON schema validation."""

import pytest
from gmaillm.validators.styles import (
    get_style_json_schema,
    get_style_json_schema_string,
    validate_json_against_schema,
)


class TestGetStyleJsonSchema:
    """Test get_style_json_schema function."""

    def test_returns_dict(self):
        """Test returns dictionary."""
        schema = get_style_json_schema()
        assert isinstance(schema, dict)

    def test_has_required_fields(self):
        """Test schema has required fields."""
        schema = get_style_json_schema()
        assert "$schema" in schema
        assert "type" in schema
        assert "required" in schema
        assert "properties" in schema

    def test_required_fields_list(self):
        """Test required fields list."""
        schema = get_style_json_schema()
        required = schema["required"]
        assert "name" in required
        assert "description" in required
        assert "greeting" in required
        assert "body" in required
        assert "closing" in required
        assert "do" in required
        assert "dont" in required


class TestGetStyleJsonSchemaString:
    """Test get_style_json_schema_string function."""

    def test_returns_string(self):
        """Test returns string."""
        result = get_style_json_schema_string()
        assert isinstance(result, str)

    def test_valid_json(self):
        """Test returns valid JSON."""
        import json
        result = get_style_json_schema_string()
        # Should not raise
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_custom_indent(self):
        """Test custom indentation."""
        result = get_style_json_schema_string(indent=4)
        # Check for 4-space indentation
        assert "    " in result


class TestValidateJsonAgainstSchema:
    """Test validate_json_against_schema function."""

    def test_valid_minimal_style(self):
        """Test validation passes for minimal valid style."""
        data = {
            "name": "test-style",
            "description": "When to use: For testing purposes.",
            "examples": ["Example 1", "Example 2"],
            "greeting": ["Hi,"],
            "body": ["Keep it brief."],
            "closing": ["Best,"],
            "do": ["Be clear", "Be concise"],
            "dont": ["Don't ramble", "Don't be vague"]
        }

        errors = validate_json_against_schema(data)
        assert len(errors) == 0

    def test_missing_required_name(self):
        """Test error when 'name' field is missing."""
        data = {
            "description": "When to use: Test.",
            "examples": ["Example"],
        }

        errors = validate_json_against_schema(data)
        assert any("Missing required field: 'name'" in err for err in errors)

    def test_missing_required_description(self):
        """Test error when 'description' field is missing."""
        data = {
            "name": "test-style",
            "examples": ["Example"],
        }

        errors = validate_json_against_schema(data)
        assert any("Missing required field: 'description'" in err for err in errors)

    def test_name_not_string(self):
        """Test error when 'name' is not a string."""
        data = {
            "name": 123,
            "description": "When to use: Test.",
            "examples": ["Example"],
        }

        errors = validate_json_against_schema(data)
        assert any("'name' must be a string" in err for err in errors)

    def test_name_too_short(self):
        """Test error when 'name' is too short."""
        data = {
            "name": "ab",  # Less than 3 chars
            "description": "When to use: Test.",
            "examples": ["Example"],
        }

        errors = validate_json_against_schema(data)
        assert any("'name' too short" in err for err in errors)

    def test_name_too_long(self):
        """Test error when 'name' is too long."""
        data = {
            "name": "a" * 51,  # More than 50 chars
            "description": "When to use: Test.",
            "examples": ["Example"],
        }

        errors = validate_json_against_schema(data)
        assert any("'name' too long" in err for err in errors)

    def test_name_invalid_characters(self):
        """Test error when 'name' contains invalid characters."""
        data = {
            "name": "Test Style",  # Space not allowed
            "description": "When to use: Test.",
            "examples": ["Example"],
        }

        errors = validate_json_against_schema(data)
        assert any("invalid characters" in err for err in errors)

    def test_name_uppercase_not_allowed(self):
        """Test error when 'name' contains uppercase letters."""
        data = {
            "name": "TestStyle",  # Uppercase not allowed
            "description": "When to use: Test.",
            "examples": ["Example"],
        }

        errors = validate_json_against_schema(data)
        assert any("invalid characters" in err for err in errors)

    def test_description_not_string(self):
        """Test error when 'description' is not a string."""
        data = {
            "name": "test-style",
            "description": ["Not", "a", "string"],
            "examples": ["Example"],
        }

        errors = validate_json_against_schema(data)
        assert any("'description' must be a string" in err for err in errors)

    def test_description_wrong_prefix(self):
        """Test error when 'description' doesn't start with 'When to use:'."""
        data = {
            "name": "test-style",
            "description": "This is a test description.",
            "examples": ["Example"],
        }

        errors = validate_json_against_schema(data)
        assert any("must start with 'When to use:'" in err for err in errors)

    def test_description_too_short(self):
        """Test error when 'description' is too short."""
        data = {
            "name": "test-style",
            "description": "When to use: X.",  # Less than 30 chars
            "examples": ["Example"],
        }

        errors = validate_json_against_schema(data)
        assert any("'description' too short" in err for err in errors)

    def test_description_too_long(self):
        """Test error when 'description' is too long."""
        data = {
            "name": "test-style",
            "description": "When to use: " + "x" * 200,  # More than 200 chars
            "examples": ["Example"],
        }

        errors = validate_json_against_schema(data)
        assert any("'description' too long" in err for err in errors)

    def test_examples_not_array(self):
        """Test error when 'examples' is not an array."""
        data = {
            "name": "test-style",
            "description": "When to use: For testing.",
            "examples": "Not an array",
        }

        errors = validate_json_against_schema(data)
        assert any("'examples' must be an array" in err for err in errors)

    def test_examples_too_few(self):
        """Test error when 'examples' has too few items."""
        data = {
            "name": "test-style",
            "description": "When to use: For testing.",
            "examples": [],  # Need at least 1
        }

        errors = validate_json_against_schema(data)
        assert any("'examples' must have at least 1" in err for err in errors)

    def test_examples_too_many(self):
        """Test error when 'examples' has too many items."""
        data = {
            "name": "test-style",
            "description": "When to use: For testing.",
            "examples": ["Ex1", "Ex2", "Ex3", "Ex4"],  # Max 3
        }

        errors = validate_json_against_schema(data)
        assert any("'examples' must have at most 3" in err for err in errors)

    def test_examples_contains_non_string(self):
        """Test error when 'examples' contains non-string."""
        data = {
            "name": "test-style",
            "description": "When to use: For testing.",
            "examples": ["Example 1", 123],  # Second item is not a string
        }

        errors = validate_json_against_schema(data)
        assert any("'examples[1]' must be a string" in err for err in errors)

    def test_examples_contains_empty_string(self):
        """Test error when 'examples' contains empty string."""
        data = {
            "name": "test-style",
            "description": "When to use: For testing.",
            "examples": ["Example 1", "   "],  # Empty after strip
        }

        errors = validate_json_against_schema(data)
        assert any("'examples[1]' cannot be empty" in err for err in errors)

    def test_greeting_not_array(self):
        """Test error when 'greeting' is not an array."""
        data = {
            "name": "test-style",
            "description": "When to use: For testing.",
            "examples": ["Ex1", "Ex2"],
            "greeting": "Hi there",
        }

        errors = validate_json_against_schema(data)
        assert any("'greeting' must be an array" in err for err in errors)

    def test_greeting_empty_array(self):
        """Test error when 'greeting' is empty."""
        data = {
            "name": "test-style",
            "description": "When to use: For testing.",
            "examples": ["Ex1", "Ex2"],
            "greeting": [],
        }

        errors = validate_json_against_schema(data)
        assert any("'greeting' must have at least 1" in err for err in errors)

    def test_body_not_array(self):
        """Test error when 'body' is not an array."""
        data = {
            "name": "test-style",
            "description": "When to use: For testing.",
            "examples": ["Ex1", "Ex2"],
            "body": "Body text",
        }

        errors = validate_json_against_schema(data)
        assert any("'body' must be an array" in err for err in errors)

    def test_do_too_few_items(self):
        """Test error when 'do' has too few items."""
        data = {
            "name": "test-style",
            "description": "When to use: For testing.",
            "examples": ["Ex1", "Ex2"],
            "do": ["Only one"],  # Need at least 2
        }

        errors = validate_json_against_schema(data)
        assert any("'do' must have at least 2" in err for err in errors)

    def test_dont_too_few_items(self):
        """Test error when 'dont' has too few items."""
        data = {
            "name": "test-style",
            "description": "When to use: For testing.",
            "examples": ["Ex1", "Ex2"],
            "dont": ["Only one"],  # Need at least 2
        }

        errors = validate_json_against_schema(data)
        assert any("'dont' must have at least 2" in err for err in errors)

    def test_unexpected_fields(self):
        """Test error for unexpected fields."""
        data = {
            "name": "test-style",
            "description": "When to use: For testing.",
            "examples": ["Ex1", "Ex2"],
            "extra_field": "Not allowed",
            "another_field": 123,
        }

        errors = validate_json_against_schema(data)
        assert any("Unexpected fields" in err for err in errors)
        assert any("extra_field" in err for err in errors)

    def test_multiple_errors_accumulated(self):
        """Test multiple validation errors are accumulated."""
        data = {
            "name": "A",  # Too short
            "description": "Wrong prefix",  # Doesn't start with "When to use:"
            "examples": ["Only one"],  # Too few
        }

        errors = validate_json_against_schema(data)
        # Should have multiple errors
        assert len(errors) >= 3
