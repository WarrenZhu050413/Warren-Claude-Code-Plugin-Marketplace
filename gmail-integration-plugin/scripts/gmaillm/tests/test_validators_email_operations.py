"""Comprehensive tests for email operations validators."""

import json
import pytest
from pathlib import Path

from gmaillm.validators.email_operations import (
    get_send_email_json_schema,
    get_reply_email_json_schema,
    get_group_json_schema,
    get_send_email_json_schema_string,
    get_reply_email_json_schema_string,
    get_group_json_schema_string,
    validate_send_email_json,
    validate_reply_email_json,
    validate_group_json,
    load_json_from_file,
)


class TestSchemaGetters:
    """Test schema getter functions."""

    def test_get_send_email_json_schema(self):
        """Test getting send email JSON schema."""
        schema = get_send_email_json_schema()

        assert isinstance(schema, dict)
        assert "$schema" in schema
        assert "required" in schema
        assert set(schema["required"]) == {"to", "subject", "body"}
        assert "properties" in schema

    def test_get_reply_email_json_schema(self):
        """Test getting reply email JSON schema."""
        schema = get_reply_email_json_schema()

        assert isinstance(schema, dict)
        assert "$schema" in schema
        assert "required" in schema
        assert schema["required"] == ["body"]
        assert "properties" in schema

    def test_get_group_json_schema(self):
        """Test getting group JSON schema."""
        schema = get_group_json_schema()

        assert isinstance(schema, dict)
        assert "$schema" in schema
        assert "required" in schema
        assert set(schema["required"]) == {"name", "members"}
        assert "properties" in schema

    def test_get_send_email_json_schema_string(self):
        """Test getting send email schema as string."""
        schema_str = get_send_email_json_schema_string()

        assert isinstance(schema_str, str)
        schema = json.loads(schema_str)  # Should be valid JSON
        assert "$schema" in schema

    def test_get_send_email_json_schema_string_custom_indent(self):
        """Test schema string with custom indentation."""
        schema_str = get_send_email_json_schema_string(indent=4)

        assert "    " in schema_str  # 4-space indentation
        schema = json.loads(schema_str)
        assert "$schema" in schema

    def test_get_reply_email_json_schema_string(self):
        """Test getting reply schema as string."""
        schema_str = get_reply_email_json_schema_string()

        assert isinstance(schema_str, str)
        schema = json.loads(schema_str)
        assert "body" in schema["required"]

    def test_get_group_json_schema_string(self):
        """Test getting group schema as string."""
        schema_str = get_group_json_schema_string()

        assert isinstance(schema_str, str)
        schema = json.loads(schema_str)
        assert "name" in schema["required"]


class TestValidateSendEmailJson:
    """Test validate_send_email_json function."""

    def test_valid_send_email_minimal(self):
        """Test validation with minimal valid send email data."""
        data = {
            "to": ["alice@example.com"],
            "subject": "Test",
            "body": "Test message"
        }

        errors = validate_send_email_json(data)

        assert len(errors) == 0

    def test_valid_send_email_full(self):
        """Test validation with all optional fields."""
        data = {
            "to": ["alice@example.com", "bob@example.com"],
            "cc": ["manager@example.com"],
            "bcc": ["audit@example.com"],
            "subject": "Meeting Tomorrow",
            "body": "Let's meet at 3pm",
            "attachments": ["/path/to/file.pdf"]
        }

        errors = validate_send_email_json(data)

        assert len(errors) == 0

    def test_missing_to_field(self):
        """Test validation fails when 'to' field is missing."""
        data = {
            "subject": "Test",
            "body": "Test message"
        }

        errors = validate_send_email_json(data)

        assert len(errors) > 0
        assert any("Missing required field: 'to'" in err for err in errors)

    def test_missing_subject_field(self):
        """Test validation fails when 'subject' field is missing."""
        data = {
            "to": ["alice@example.com"],
            "body": "Test message"
        }

        errors = validate_send_email_json(data)

        assert len(errors) > 0
        assert any("Missing required field: 'subject'" in err for err in errors)

    def test_missing_body_field(self):
        """Test validation fails when 'body' field is missing."""
        data = {
            "to": ["alice@example.com"],
            "subject": "Test"
        }

        errors = validate_send_email_json(data)

        assert len(errors) > 0
        assert any("Missing required field: 'body'" in err for err in errors)

    def test_to_not_array(self):
        """Test validation fails when 'to' is not an array."""
        data = {
            "to": "alice@example.com",  # Should be array
            "subject": "Test",
            "body": "Test message"
        }

        errors = validate_send_email_json(data)

        assert len(errors) > 0
        assert any("'to' must be an array" in err for err in errors)

    def test_to_empty_array(self):
        """Test validation fails when 'to' is empty array."""
        data = {
            "to": [],
            "subject": "Test",
            "body": "Test message"
        }

        errors = validate_send_email_json(data)

        assert len(errors) > 0
        assert any("must have at least 1 recipient" in err for err in errors)

    def test_to_contains_non_string(self):
        """Test validation fails when 'to' contains non-string."""
        data = {
            "to": ["alice@example.com", 123],  # Number instead of string
            "subject": "Test",
            "body": "Test message"
        }

        errors = validate_send_email_json(data)

        assert len(errors) > 0
        assert any("'to[1]' must be a string" in err for err in errors)

    def test_to_contains_empty_string(self):
        """Test validation fails when 'to' contains empty string."""
        data = {
            "to": ["alice@example.com", ""],
            "subject": "Test",
            "body": "Test message"
        }

        errors = validate_send_email_json(data)

        assert len(errors) > 0
        assert any("'to[1]' cannot be empty" in err for err in errors)

    def test_cc_not_array(self):
        """Test validation fails when 'cc' is not an array."""
        data = {
            "to": ["alice@example.com"],
            "cc": "manager@example.com",  # Should be array
            "subject": "Test",
            "body": "Test message"
        }

        errors = validate_send_email_json(data)

        assert len(errors) > 0
        assert any("'cc' must be an array" in err for err in errors)

    def test_bcc_not_array(self):
        """Test validation fails when 'bcc' is not an array."""
        data = {
            "to": ["alice@example.com"],
            "bcc": "audit@example.com",  # Should be array
            "subject": "Test",
            "body": "Test message"
        }

        errors = validate_send_email_json(data)

        assert len(errors) > 0
        assert any("'bcc' must be an array" in err for err in errors)

    def test_subject_not_string(self):
        """Test validation fails when 'subject' is not a string."""
        data = {
            "to": ["alice@example.com"],
            "subject": 123,  # Should be string
            "body": "Test message"
        }

        errors = validate_send_email_json(data)

        assert len(errors) > 0
        assert any("'subject' must be a string" in err for err in errors)

    def test_subject_empty_string(self):
        """Test validation fails when 'subject' is empty."""
        data = {
            "to": ["alice@example.com"],
            "subject": "",
            "body": "Test message"
        }

        errors = validate_send_email_json(data)

        assert len(errors) > 0
        assert any("'subject' cannot be empty" in err for err in errors)

    def test_body_not_string(self):
        """Test validation fails when 'body' is not a string."""
        data = {
            "to": ["alice@example.com"],
            "subject": "Test",
            "body": ["should", "be", "string"]  # Should be string
        }

        errors = validate_send_email_json(data)

        assert len(errors) > 0
        assert any("'body' must be a string" in err for err in errors)

    def test_body_empty_string(self):
        """Test validation fails when 'body' is empty."""
        data = {
            "to": ["alice@example.com"],
            "subject": "Test",
            "body": "   "  # Whitespace only
        }

        errors = validate_send_email_json(data)

        assert len(errors) > 0
        assert any("'body' cannot be empty" in err for err in errors)

    def test_attachments_not_array(self):
        """Test validation fails when 'attachments' is not an array."""
        data = {
            "to": ["alice@example.com"],
            "subject": "Test",
            "body": "Test",
            "attachments": "/path/to/file.pdf"  # Should be array
        }

        errors = validate_send_email_json(data)

        assert len(errors) > 0
        assert any("'attachments' must be an array" in err for err in errors)

    def test_unexpected_fields(self):
        """Test validation detects unexpected fields."""
        data = {
            "to": ["alice@example.com"],
            "subject": "Test",
            "body": "Test",
            "priority": "high",  # Unexpected field
            "tags": ["important"]  # Unexpected field
        }

        errors = validate_send_email_json(data)

        assert len(errors) > 0
        assert any("Unexpected fields" in err for err in errors)
        assert any("priority" in err for err in errors)


class TestValidateReplyEmailJson:
    """Test validate_reply_email_json function."""

    def test_valid_reply_minimal(self):
        """Test validation with minimal valid reply data."""
        data = {
            "body": "Thanks for your email!"
        }

        errors = validate_reply_email_json(data)

        assert len(errors) == 0

    def test_valid_reply_with_reply_all(self):
        """Test validation with reply_all flag."""
        data = {
            "body": "Thanks everyone!",
            "reply_all": True
        }

        errors = validate_reply_email_json(data)

        assert len(errors) == 0

    def test_missing_body_field(self):
        """Test validation fails when 'body' field is missing."""
        data = {
            "reply_all": True
        }

        errors = validate_reply_email_json(data)

        assert len(errors) > 0
        assert any("Missing required field: 'body'" in err for err in errors)

    def test_body_not_string(self):
        """Test validation fails when 'body' is not a string."""
        data = {
            "body": 123  # Should be string
        }

        errors = validate_reply_email_json(data)

        assert len(errors) > 0
        assert any("'body' must be a string" in err for err in errors)

    def test_body_empty_string(self):
        """Test validation fails when 'body' is empty."""
        data = {
            "body": ""
        }

        errors = validate_reply_email_json(data)

        assert len(errors) > 0
        assert any("'body' cannot be empty" in err for err in errors)

    def test_reply_all_not_boolean(self):
        """Test validation fails when 'reply_all' is not a boolean."""
        data = {
            "body": "Thanks!",
            "reply_all": "yes"  # Should be boolean
        }

        errors = validate_reply_email_json(data)

        assert len(errors) > 0
        assert any("'reply_all' must be a boolean" in err for err in errors)

    def test_unexpected_fields(self):
        """Test validation detects unexpected fields."""
        data = {
            "body": "Thanks!",
            "attachments": ["/path/to/file.pdf"]  # Not allowed in reply
        }

        errors = validate_reply_email_json(data)

        assert len(errors) > 0
        assert any("Unexpected fields" in err for err in errors)


class TestValidateGroupJson:
    """Test validate_group_json function."""

    def test_valid_group(self):
        """Test validation with valid group data."""
        data = {
            "name": "team-alpha",
            "members": ["alice@example.com", "bob@example.com"]
        }

        errors = validate_group_json(data)

        assert len(errors) == 0

    def test_missing_name_field(self):
        """Test validation fails when 'name' field is missing."""
        data = {
            "members": ["alice@example.com"]
        }

        errors = validate_group_json(data)

        assert len(errors) > 0
        assert any("Missing required field: 'name'" in err for err in errors)

    def test_missing_members_field(self):
        """Test validation fails when 'members' field is missing."""
        data = {
            "name": "team-alpha"
        }

        errors = validate_group_json(data)

        assert len(errors) > 0
        assert any("Missing required field: 'members'" in err for err in errors)

    def test_name_not_string(self):
        """Test validation fails when 'name' is not a string."""
        data = {
            "name": 123,  # Should be string
            "members": ["alice@example.com"]
        }

        errors = validate_group_json(data)

        assert len(errors) > 0
        assert any("'name' must be a string" in err for err in errors)

    def test_name_empty_string(self):
        """Test validation fails when 'name' is empty."""
        data = {
            "name": "",
            "members": ["alice@example.com"]
        }

        errors = validate_group_json(data)

        assert len(errors) > 0
        assert any("'name' cannot be empty" in err for err in errors)

    def test_name_invalid_pattern_uppercase(self):
        """Test validation fails when 'name' contains uppercase."""
        data = {
            "name": "Team-Alpha",  # Uppercase not allowed
            "members": ["alice@example.com"]
        }

        errors = validate_group_json(data)

        assert len(errors) > 0
        assert any("lowercase letters, numbers, hyphens, and underscores" in err for err in errors)

    def test_name_invalid_pattern_space(self):
        """Test validation fails when 'name' contains space."""
        data = {
            "name": "team alpha",  # Space not allowed
            "members": ["alice@example.com"]
        }

        errors = validate_group_json(data)

        assert len(errors) > 0
        assert any("lowercase letters, numbers, hyphens, and underscores" in err for err in errors)

    def test_members_not_array(self):
        """Test validation fails when 'members' is not an array."""
        data = {
            "name": "team-alpha",
            "members": "alice@example.com"  # Should be array
        }

        errors = validate_group_json(data)

        assert len(errors) > 0
        assert any("'members' must be an array" in err for err in errors)

    def test_members_empty_array(self):
        """Test validation fails when 'members' is empty."""
        data = {
            "name": "team-alpha",
            "members": []
        }

        errors = validate_group_json(data)

        assert len(errors) > 0
        assert any("must have at least 1 member" in err for err in errors)

    def test_members_contains_non_string(self):
        """Test validation fails when 'members' contains non-string."""
        data = {
            "name": "team-alpha",
            "members": ["alice@example.com", 123]
        }

        errors = validate_group_json(data)

        assert len(errors) > 0
        assert any("'members[1]' must be a string" in err for err in errors)

    def test_unexpected_fields(self):
        """Test validation detects unexpected fields."""
        data = {
            "name": "team-alpha",
            "members": ["alice@example.com"],
            "description": "Engineering team"  # Unexpected field
        }

        errors = validate_group_json(data)

        assert len(errors) > 0
        assert any("Unexpected fields" in err for err in errors)


class TestLoadJsonFromFile:
    """Test load_json_from_file function."""

    def test_load_valid_json(self, tmp_path):
        """Test loading valid JSON file."""
        json_file = tmp_path / "test.json"
        data = {"to": ["alice@example.com"], "subject": "Test", "body": "Message"}
        json_file.write_text(json.dumps(data))

        result = load_json_from_file(json_file)

        assert result == data

    def test_load_nonexistent_file(self, tmp_path):
        """Test loading nonexistent file raises FileNotFoundError."""
        json_file = tmp_path / "nonexistent.json"

        with pytest.raises(FileNotFoundError, match="File not found"):
            load_json_from_file(json_file)

    def test_load_invalid_json(self, tmp_path):
        """Test loading invalid JSON raises ValueError."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text("{ invalid json }")

        with pytest.raises(ValueError, match="Invalid JSON"):
            load_json_from_file(json_file)

    def test_load_directory_not_file(self, tmp_path):
        """Test loading directory raises ValueError."""
        directory = tmp_path / "not_a_file"
        directory.mkdir()

        with pytest.raises(ValueError, match="Not a file"):
            load_json_from_file(directory)

    def test_load_empty_json_file(self, tmp_path):
        """Test loading empty JSON file."""
        json_file = tmp_path / "empty.json"
        json_file.write_text("")

        with pytest.raises(ValueError, match="Invalid JSON"):
            load_json_from_file(json_file)
