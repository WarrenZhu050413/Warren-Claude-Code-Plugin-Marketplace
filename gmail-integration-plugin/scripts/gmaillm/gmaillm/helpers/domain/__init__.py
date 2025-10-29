"""Domain business logic for gmaillm."""

from gmaillm.helpers.domain.groups import (
    expand_email_groups,
    load_email_groups,
    save_email_groups,
)
from gmaillm.helpers.domain.styles import (
    create_style_from_template,
    extract_style_metadata,
    load_all_styles,
)

__all__ = [
    # Email groups
    "load_email_groups",
    "save_email_groups",
    "expand_email_groups",
    # Email styles
    "load_all_styles",
    "extract_style_metadata",
    "create_style_from_template",
]
