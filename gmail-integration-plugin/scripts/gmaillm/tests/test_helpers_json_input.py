"""Comprehensive tests for JSON input helpers."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any, List

import typer

from gmaillm.helpers.cli.validation import (
    load_and_validate_json,
    display_schema_and_exit,
)


class TestLoadAndValidateJson:
    """Test load_and_validate_json function."""

    def test_load_valid_json_with_no_validation_errors(self, tmp_path):
        """Test loading valid JSON that passes validation."""
        json_file = tmp_path / "valid.json"
        data = {"to": ["alice@example.com"], "subject": "Test", "body": "Message"}
        json_file.write_text(json.dumps(data))

        # Validator that returns no errors
        def validator(json_data):
            return []

        result = load_and_validate_json(
            str(json_file),
            validator,
            "gmail send --schema"
        )

        assert result == data

    def test_load_valid_json_with_complex_data(self, tmp_path):
        """Test loading complex nested JSON structure."""
        json_file = tmp_path / "complex.json"
        data = {
            "to": ["alice@example.com", "bob@example.com"],
            "cc": ["manager@example.com"],
            "subject": "Team Meeting",
            "body": "Let's discuss Q4 plans",
            "attachments": ["/path/to/report.pdf", "/path/to/slides.pptx"]
        }
        json_file.write_text(json.dumps(data))

        def validator(json_data):
            return []

        result = load_and_validate_json(
            str(json_file),
            validator,
            "gmail send --schema"
        )

        assert result == data

    def test_file_not_found(self, tmp_path):
        """Test error when file doesn't exist."""
        nonexistent = tmp_path / "nonexistent.json"

        def validator(json_data):
            return []

        with pytest.raises(typer.Exit) as exc_info:
            load_and_validate_json(
                str(nonexistent),
                validator,
                "gmail send --schema"
            )

        assert exc_info.value.exit_code == 1

    def test_not_a_file_is_directory(self, tmp_path):
        """Test error when path is a directory, not a file."""
        directory = tmp_path / "not_a_file"
        directory.mkdir()

        def validator(json_data):
            return []

        with pytest.raises(typer.Exit) as exc_info:
            load_and_validate_json(
                str(directory),
                validator,
                "gmail send --schema"
            )

        assert exc_info.value.exit_code == 1

    def test_invalid_json_syntax(self, tmp_path):
        """Test error when JSON has syntax errors."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text("{ invalid json syntax }")

        def validator(json_data):
            return []

        with pytest.raises(typer.Exit) as exc_info:
            load_and_validate_json(
                str(json_file),
                validator,
                "gmail send --schema"
            )

        assert exc_info.value.exit_code == 1

    def test_empty_json_file(self, tmp_path):
        """Test error when JSON file is empty."""
        json_file = tmp_path / "empty.json"
        json_file.write_text("")

        def validator(json_data):
            return []

        with pytest.raises(typer.Exit) as exc_info:
            load_and_validate_json(
                str(json_file),
                validator,
                "gmail send --schema"
            )

        assert exc_info.value.exit_code == 1

    def test_validation_fails_single_error(self, tmp_path):
        """Test validation failure with one error."""
        json_file = tmp_path / "invalid_data.json"
        data = {"subject": "Test", "body": "Message"}  # Missing 'to' field
        json_file.write_text(json.dumps(data))

        def validator(json_data):
            return ["Missing required field: 'to'"]

        with pytest.raises(typer.Exit) as exc_info:
            load_and_validate_json(
                str(json_file),
                validator,
                "gmail send --schema"
            )

        assert exc_info.value.exit_code == 1

    def test_validation_fails_multiple_errors(self, tmp_path):
        """Test validation failure with multiple errors."""
        json_file = tmp_path / "invalid_data.json"
        data = {"body": "Message"}  # Missing 'to' and 'subject'
        json_file.write_text(json.dumps(data))

        def validator(json_data):
            return [
                "Missing required field: 'to'",
                "Missing required field: 'subject'"
            ]

        with pytest.raises(typer.Exit) as exc_info:
            load_and_validate_json(
                str(json_file),
                validator,
                "gmail send --schema"
            )

        assert exc_info.value.exit_code == 1

    def test_validation_with_custom_validator(self, tmp_path):
        """Test with custom validator checking specific constraints."""
        json_file = tmp_path / "test.json"
        data = {"email": "invalid-email", "age": 15}
        json_file.write_text(json.dumps(data))

        def custom_validator(json_data):
            errors = []
            if "@" not in json_data.get("email", ""):
                errors.append("Invalid email format")
            if json_data.get("age", 0) < 18:
                errors.append("Age must be at least 18")
            return errors

        with pytest.raises(typer.Exit) as exc_info:
            load_and_validate_json(
                str(json_file),
                custom_validator,
                "mycommand --schema"
            )

        assert exc_info.value.exit_code == 1

    def test_read_permission_error(self, tmp_path):
        """Test error when file cannot be read due to permissions."""
        json_file = tmp_path / "unreadable.json"
        json_file.write_text('{"key": "value"}')

        def validator(json_data):
            return []

        # Mock open to raise PermissionError
        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            with pytest.raises(typer.Exit) as exc_info:
                load_and_validate_json(
                    str(json_file),
                    validator,
                    "gmail send --schema"
                )

            assert exc_info.value.exit_code == 1

    def test_unicode_content(self, tmp_path):
        """Test loading JSON with Unicode characters."""
        json_file = tmp_path / "unicode.json"
        data = {
            "to": ["recipient@example.com"],
            "subject": "Café ☕ Meeting",
            "body": "Let's discuss über-important topics 中文"
        }
        json_file.write_text(json.dumps(data, ensure_ascii=False))

        def validator(json_data):
            return []

        result = load_and_validate_json(
            str(json_file),
            validator,
            "gmail send --schema"
        )

        assert result == data
        assert result["subject"] == "Café ☕ Meeting"


class TestDisplaySchemaAndExit:
    """Test display_schema_and_exit function."""

    def test_display_schema_basic(self):
        """Test basic schema display."""
        def schema_getter(indent=2):
            return json.dumps({
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "required": ["field1"]
            }, indent=indent)

        # Should not raise - just prints and exits
        display_schema_and_exit(
            schema_getter,
            "Test Schema",
            "This is a test schema",
            "mycommand --json test.json"
        )

    def test_display_schema_with_custom_indent(self):
        """Test schema display with custom indentation."""
        indent_used = None

        def schema_getter(indent=2):
            nonlocal indent_used
            indent_used = indent
            return json.dumps({"type": "object"}, indent=indent)

        display_schema_and_exit(
            schema_getter,
            "Test Schema",
            "Description",
            "example command"
        )

        assert indent_used == 2

    def test_display_schema_with_complex_schema(self):
        """Test displaying complex nested schema."""
        def schema_getter(indent=2):
            complex_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "to": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1
                    },
                    "subject": {"type": "string"},
                    "body": {"type": "string"}
                },
                "required": ["to", "subject", "body"]
            }
            return json.dumps(complex_schema, indent=indent)

        display_schema_and_exit(
            schema_getter,
            "Email Schema",
            "Schema for sending emails",
            "gmail send --json email.json"
        )

    def test_display_schema_calls_getter_with_indent(self):
        """Test that schema getter is called with indent parameter."""
        called_with_indent = None

        def schema_getter(indent=2):
            nonlocal called_with_indent
            called_with_indent = indent
            return json.dumps({"test": "schema"}, indent=indent)

        display_schema_and_exit(
            schema_getter,
            "Title",
            "Description",
            "usage example"
        )

        assert called_with_indent == 2

    @patch("gmaillm.helpers.json_input.console")
    def test_display_schema_prints_all_sections(self, mock_console):
        """Test that all sections are printed."""
        def schema_getter(indent=2):
            return json.dumps({"type": "object"}, indent=indent)

        display_schema_and_exit(
            schema_getter,
            "Test Title",
            "Test Description",
            "test command example"
        )

        # Verify console.print was called (title, description, usage)
        assert mock_console.print.call_count >= 3
        # Verify print_json was called for schema
        assert mock_console.print_json.call_count == 1
