"""Pattern validation utilities."""

import re
from typing import Optional, Tuple


def validate_regex_pattern(pattern: str) -> Tuple[bool, Optional[str]]:
    """Validate a regex pattern.

    Args:
        pattern: Regex pattern string to validate

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if pattern is valid regex
        - error_message: None if valid, error string if invalid
    """
    if not pattern:
        return False, "Pattern cannot be empty"

    if not pattern.strip():
        return False, "Pattern cannot be only whitespace"

    try:
        re.compile(pattern)
        return True, None
    except re.error as e:
        return False, f"Invalid regex: {e}"


def check_pattern_match(pattern: str, text: str) -> bool:
    """Check if a pattern matches text.

    Args:
        pattern: Regex pattern
        text: Text to match against

    Returns:
        True if pattern matches, False otherwise
    """
    try:
        compiled = re.compile(pattern, re.IGNORECASE)
        return bool(compiled.search(text))
    except re.error:
        return False


def extract_pattern_groups(pattern: str, text: str) -> Optional[dict]:
    """Extract named groups from a pattern match.

    Args:
        pattern: Regex pattern with named groups
        text: Text to match against

    Returns:
        Dictionary of group names to values, or None if no match
    """
    try:
        compiled = re.compile(pattern, re.IGNORECASE)
        match = compiled.search(text)
        if match:
            return match.groupdict()
        return None
    except re.error:
        return None
