"""JSON schema validators for email operations (send, reply, groups)."""

import json
from pathlib import Path
from typing import Any, Dict, List

# JSON Schema for sending emails
SEND_EMAIL_JSON_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["to", "subject", "body"],
    "properties": {
        "to": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "format": "email"},
            "description": "List of recipient email addresses"
        },
        "cc": {
            "type": "array",
            "items": {"type": "string", "format": "email"},
            "description": "List of CC email addresses (optional)"
        },
        "bcc": {
            "type": "array",
            "items": {"type": "string", "format": "email"},
            "description": "List of BCC email addresses (optional)"
        },
        "subject": {
            "type": "string",
            "minLength": 1,
            "description": "Email subject line"
        },
        "body": {
            "type": "string",
            "minLength": 1,
            "description": "Email body text"
        },
        "attachments": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of file paths for attachments (optional)"
        }
    },
    "additionalProperties": False
}

# JSON Schema for replying to emails
REPLY_EMAIL_JSON_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["body"],
    "properties": {
        "body": {
            "type": "string",
            "minLength": 1,
            "description": "Reply body text"
        },
        "reply_all": {
            "type": "boolean",
            "description": "Reply to all recipients (optional, default: false)"
        }
    },
    "additionalProperties": False
}

# JSON Schema for creating email groups
GROUP_JSON_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["name", "members"],
    "properties": {
        "name": {
            "type": "string",
            "minLength": 1,
            "pattern": "^[a-z0-9-_]+$",
            "description": "Group name (lowercase, numbers, hyphens, underscores only)"
        },
        "members": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "format": "email"},
            "description": "List of member email addresses"
        }
    },
    "additionalProperties": False
}


def get_send_email_json_schema() -> Dict[str, Any]:
    """Return the JSON schema for sending emails."""
    return SEND_EMAIL_JSON_SCHEMA


def get_reply_email_json_schema() -> Dict[str, Any]:
    """Return the JSON schema for replying to emails."""
    return REPLY_EMAIL_JSON_SCHEMA


def get_group_json_schema() -> Dict[str, Any]:
    """Return the JSON schema for creating groups."""
    return GROUP_JSON_SCHEMA


def get_send_email_json_schema_string(indent: int = 2) -> str:
    """Return formatted JSON schema for send email command."""
    return json.dumps(SEND_EMAIL_JSON_SCHEMA, indent=indent)


def get_reply_email_json_schema_string(indent: int = 2) -> str:
    """Return formatted JSON schema for reply command."""
    return json.dumps(REPLY_EMAIL_JSON_SCHEMA, indent=indent)


def get_group_json_schema_string(indent: int = 2) -> str:
    """Return formatted JSON schema for groups command."""
    return json.dumps(GROUP_JSON_SCHEMA, indent=indent)


def validate_send_email_json(json_data: Dict[str, Any]) -> List[str]:
    """Validate JSON data for sending emails.

    Args:
        json_data: Dictionary containing email data

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Check required fields
    for field in ["to", "subject", "body"]:
        if field not in json_data:
            errors.append(f"Missing required field: '{field}'")

    # Validate 'to' field
    if "to" in json_data:
        if not isinstance(json_data["to"], list):
            errors.append(f"Field 'to' must be an array, got {type(json_data['to']).__name__}")
        elif len(json_data["to"]) == 0:
            errors.append("Field 'to' must have at least 1 recipient")
        else:
            for i, email in enumerate(json_data["to"]):
                if not isinstance(email, str):
                    errors.append(f"Field 'to[{i}]' must be a string, got {type(email).__name__}")
                elif not email.strip():
                    errors.append(f"Field 'to[{i}]' cannot be empty")

    # Validate optional 'cc' field
    if "cc" in json_data:
        if not isinstance(json_data["cc"], list):
            errors.append(f"Field 'cc' must be an array, got {type(json_data['cc']).__name__}")
        else:
            for i, email in enumerate(json_data["cc"]):
                if not isinstance(email, str):
                    errors.append(f"Field 'cc[{i}]' must be a string, got {type(email).__name__}")
                elif not email.strip():
                    errors.append(f"Field 'cc[{i}]' cannot be empty")

    # Validate optional 'bcc' field
    if "bcc" in json_data:
        if not isinstance(json_data["bcc"], list):
            errors.append(f"Field 'bcc' must be an array, got {type(json_data['bcc']).__name__}")
        else:
            for i, email in enumerate(json_data["bcc"]):
                if not isinstance(email, str):
                    errors.append(f"Field 'bcc[{i}]' must be a string, got {type(email).__name__}")
                elif not email.strip():
                    errors.append(f"Field 'bcc[{i}]' cannot be empty")

    # Validate 'subject' field
    if "subject" in json_data:
        if not isinstance(json_data["subject"], str):
            errors.append(f"Field 'subject' must be a string, got {type(json_data['subject']).__name__}")
        elif not json_data["subject"].strip():
            errors.append("Field 'subject' cannot be empty")

    # Validate 'body' field
    if "body" in json_data:
        if not isinstance(json_data["body"], str):
            errors.append(f"Field 'body' must be a string, got {type(json_data['body']).__name__}")
        elif not json_data["body"].strip():
            errors.append("Field 'body' cannot be empty")

    # Validate optional 'attachments' field
    if "attachments" in json_data:
        if not isinstance(json_data["attachments"], list):
            errors.append(f"Field 'attachments' must be an array, got {type(json_data['attachments']).__name__}")
        else:
            for i, path in enumerate(json_data["attachments"]):
                if not isinstance(path, str):
                    errors.append(f"Field 'attachments[{i}]' must be a string, got {type(path).__name__}")
                elif not path.strip():
                    errors.append(f"Field 'attachments[{i}]' cannot be empty")

    # Check for unexpected fields
    allowed_fields = set(SEND_EMAIL_JSON_SCHEMA["properties"].keys())
    extra_fields = set(json_data.keys()) - allowed_fields
    if extra_fields:
        errors.append(f"Unexpected fields: {', '.join(sorted(extra_fields))}")

    return errors


def validate_reply_email_json(json_data: Dict[str, Any]) -> List[str]:
    """Validate JSON data for replying to emails.

    Args:
        json_data: Dictionary containing reply data

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Check required fields
    if "body" not in json_data:
        errors.append("Missing required field: 'body'")

    # Validate 'body' field
    if "body" in json_data:
        if not isinstance(json_data["body"], str):
            errors.append(f"Field 'body' must be a string, got {type(json_data['body']).__name__}")
        elif not json_data["body"].strip():
            errors.append("Field 'body' cannot be empty")

    # Validate optional 'reply_all' field
    if "reply_all" in json_data:
        if not isinstance(json_data["reply_all"], bool):
            errors.append(f"Field 'reply_all' must be a boolean, got {type(json_data['reply_all']).__name__}")

    # Check for unexpected fields
    allowed_fields = set(REPLY_EMAIL_JSON_SCHEMA["properties"].keys())
    extra_fields = set(json_data.keys()) - allowed_fields
    if extra_fields:
        errors.append(f"Unexpected fields: {', '.join(sorted(extra_fields))}")

    return errors


def validate_group_json(json_data: Dict[str, Any]) -> List[str]:
    """Validate JSON data for creating email groups.

    Args:
        json_data: Dictionary containing group data

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Check required fields
    for field in ["name", "members"]:
        if field not in json_data:
            errors.append(f"Missing required field: '{field}'")

    # Validate 'name' field
    if "name" in json_data:
        name = json_data["name"]
        if not isinstance(name, str):
            errors.append(f"Field 'name' must be a string, got {type(name).__name__}")
        else:
            if not name.strip():
                errors.append("Field 'name' cannot be empty")
            # Check pattern (lowercase, numbers, hyphens, underscores)
            import re
            if not re.match(r'^[a-z0-9-_]+$', name):
                errors.append("Field 'name' must contain only lowercase letters, numbers, hyphens, and underscores")

    # Validate 'members' field
    if "members" in json_data:
        if not isinstance(json_data["members"], list):
            errors.append(f"Field 'members' must be an array, got {type(json_data['members']).__name__}")
        elif len(json_data["members"]) == 0:
            errors.append("Field 'members' must have at least 1 member")
        else:
            for i, email in enumerate(json_data["members"]):
                if not isinstance(email, str):
                    errors.append(f"Field 'members[{i}]' must be a string, got {type(email).__name__}")
                elif not email.strip():
                    errors.append(f"Field 'members[{i}]' cannot be empty")

    # Check for unexpected fields
    allowed_fields = set(GROUP_JSON_SCHEMA["properties"].keys())
    extra_fields = set(json_data.keys()) - allowed_fields
    if extra_fields:
        errors.append(f"Unexpected fields: {', '.join(sorted(extra_fields))}")

    return errors


def load_json_from_file(file_path: Path) -> Dict[str, Any]:
    """Load and parse JSON from a file.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data as dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not valid JSON or not a regular file
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    try:
        with open(file_path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}")
    except Exception as e:
        raise ValueError(f"Error reading file: {e}")
