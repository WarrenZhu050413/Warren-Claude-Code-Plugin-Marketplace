"""Email group business logic for gmaillm."""

from pathlib import Path
from typing import Dict, List, Optional

from rich.console import Console

from gmaillm.helpers.core.io import load_json_config, save_json_config
from gmaillm.helpers.core.paths import get_groups_dir

console = Console()


def normalize_group_name(name: str) -> str:
    """Normalize group name by removing # prefix if present.

    Args:
        name: Group name with or without # prefix

    Returns:
        Group name without # prefix

    Examples:
        >>> normalize_group_name("#team")
        'team'
        >>> normalize_group_name("team")
        'team'
    """
    return name.lstrip('#')


def load_email_groups(groups_file: Optional[Path] = None) -> Dict[str, List[str]]:
    """Load email distribution groups from config.

    Args:
        groups_file: Optional path to groups file (for testing)

    Returns:
        Dictionary mapping group names to email lists
    """
    if groups_file is None:
        groups_dir = get_groups_dir()
        groups_file = groups_dir / "groups.json"

    groups = load_json_config(groups_file)
    # Filter out metadata/comment keys
    return {k: v for k, v in groups.items() if not k.startswith("_")}


def save_email_groups(groups: Dict[str, List[str]], groups_file: Optional[Path] = None) -> None:
    """Save email distribution groups to config.

    Args:
        groups: Dictionary mapping group names to email lists
        groups_file: Optional path to groups file (for testing)
    """
    if groups_file is None:
        groups_dir = get_groups_dir()
        groups_file = groups_dir / "groups.json"

    save_json_config(groups_file, groups)


def expand_email_groups(recipients: List[str], groups: Optional[Dict[str, List[str]]] = None) -> List[str]:
    """Expand #groupname references to actual email addresses.

    Args:
        recipients: List of email addresses or #group references
        groups: Optional groups dict (for testing), loads from config if None

    Returns:
        Expanded list with all #group references resolved (duplicates removed)
    """
    if groups is None:
        groups = load_email_groups()

    expanded = []
    seen = set()

    for recipient in recipients:
        if recipient.startswith("#"):
            # This is a group reference
            group_name = recipient[1:]  # Remove # prefix
            if group_name in groups:
                for email in groups[group_name]:
                    if email not in seen:
                        expanded.append(email)
                        seen.add(email)
            else:
                available = ", ".join("#" + k for k in groups.keys())
                console.print(
                    f"[yellow]Warning: Unknown group '#{group_name}', available: {available}[/yellow]"
                )
                if recipient not in seen:
                    expanded.append(recipient)  # Keep as-is if group not found
                    seen.add(recipient)
        else:
            if recipient not in seen:
                expanded.append(recipient)
                seen.add(recipient)

    return expanded
