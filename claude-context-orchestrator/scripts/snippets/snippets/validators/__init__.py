"""Validation utilities for snippets management."""

from .patterns import (
    check_pattern_match,
    extract_pattern_groups,
    validate_regex_pattern,
)
from .snippets import (
    validate_config_mapping,
    validate_full_config,
    validate_snippet_content,
    validate_snippet_file,
    validate_snippet_name,
)

__all__ = [
    # Pattern validators
    "check_pattern_match",
    "extract_pattern_groups",
    "validate_regex_pattern",
    # Snippet validators
    "validate_config_mapping",
    "validate_full_config",
    "validate_snippet_content",
    "validate_snippet_file",
    "validate_snippet_name",
]
