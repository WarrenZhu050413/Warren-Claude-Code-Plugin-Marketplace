"""Snippet validation utilities."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..models import ValidationError


def validate_snippet_file(snippet_path: Path) -> Tuple[bool, Optional[str]]:
    """Validate a snippet file exists and is readable.

    Args:
        snippet_path: Path to snippet file

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not snippet_path.exists():
        return False, f"File does not exist: {snippet_path}"

    if not snippet_path.is_file():
        return False, f"Not a file: {snippet_path}"

    try:
        with open(snippet_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.strip():
                return False, f"File is empty: {snippet_path}"
        return True, None
    except Exception as e:
        return False, f"Cannot read file: {e}"


def validate_snippet_name(name: str) -> Tuple[bool, Optional[str]]:
    """Validate a snippet name.

    Args:
        name: Snippet name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Snippet name cannot be empty"

    if "/" in name or "\\" in name:
        return False, "Snippet name cannot contain slashes"

    if name.startswith("."):
        return False, "Snippet name cannot start with a dot"

    if len(name) > 100:
        return False, "Snippet name too long (max 100 characters)"

    return True, None


def validate_snippet_content(content: str) -> Tuple[bool, List[str]]:
    """Validate snippet content.

    Checks for:
    - Non-empty content
    - Valid UTF-8 encoding
    - Optional: YAML frontmatter format

    Args:
        content: Snippet content to validate

    Returns:
        Tuple of (is_valid, list_of_warnings)
    """
    warnings = []

    if not content.strip():
        return False, ["Content is empty"]

    # Check for frontmatter
    if content.strip().startswith("---"):
        parts = content.split("---", 2)
        if len(parts) < 3:
            warnings.append("YAML frontmatter appears incomplete")

    # Check for verification hash
    if "VERIFICATION_HASH:" not in content:
        warnings.append("No verification hash found (will be added automatically)")

    return True, warnings


def validate_config_mapping(
    mapping: Dict,
    base_dir: Path
) -> List[ValidationError]:
    """Validate a single configuration mapping.

    Args:
        mapping: Mapping dictionary from config
        base_dir: Base directory for resolving paths

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check required fields
    if "pattern" not in mapping:
        errors.append(ValidationError(
            error_type="missing_field",
            message="Mapping missing 'pattern' field"
        ))

    if "snippet" not in mapping:
        errors.append(ValidationError(
            error_type="missing_field",
            message="Mapping missing 'snippet' field"
        ))
        return errors

    # Validate pattern
    pattern = mapping.get("pattern", "")
    from .patterns import validate_regex_pattern

    is_valid, error_msg = validate_regex_pattern(pattern)
    if not is_valid:
        errors.append(ValidationError(
            pattern=pattern,
            error_type="invalid_pattern",
            message=error_msg
        ))

    # Validate snippet files
    snippet_files = mapping["snippet"]
    if isinstance(snippet_files, str):
        snippet_files = [snippet_files]

    for snippet_file in snippet_files:
        # Use resolve_snippet_path to properly handle relative paths
        from snippets.helpers.core.paths import resolve_snippet_path
        snippet_path = resolve_snippet_path(snippet_file, base_dir)

        is_valid, error_msg = validate_snippet_file(snippet_path)
        if not is_valid:
            errors.append(ValidationError(
                snippet_path=str(snippet_path),
                pattern=pattern,
                error_type="invalid_snippet_file",
                message=error_msg
            ))

    return errors


def validate_full_config(config: Dict, base_dir: Path) -> List[ValidationError]:
    """Validate entire configuration.

    Args:
        config: Full configuration dictionary
        base_dir: Base directory for resolving paths

    Returns:
        List of all validation errors
    """
    all_errors = []

    if "mappings" not in config:
        all_errors.append(ValidationError(
            error_type="missing_field",
            message="Config missing 'mappings' field"
        ))
        return all_errors

    for i, mapping in enumerate(config["mappings"]):
        mapping_errors = validate_config_mapping(mapping, base_dir)
        for error in mapping_errors:
            # Add mapping index for context
            error_dict = error.model_dump()
            error_dict["message"] = f"Mapping #{i}: {error_dict['message']}"
            all_errors.append(ValidationError(**error_dict))

    return all_errors
