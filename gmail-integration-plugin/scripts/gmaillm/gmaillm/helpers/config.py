"""Configuration and file management utilities for gmaillm."""

import json
import os
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console

console = Console()


def get_plugin_config_dir() -> Path:
    """Get the plugin config directory path.

    Always uses ~/.gmaillm/ for consistency with credentials storage.

    Returns:
        Path to config directory (~/.gmaillm/)
    """
    config_dir = Path.home() / ".gmaillm"
    config_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
    return config_dir


def load_json_config(file_path: Path) -> Dict[str, Any]:
    """Load JSON config file with error handling.

    Args:
        file_path: Path to JSON config file

    Returns:
        Dictionary containing config data, or empty dict on error
    """
    try:
        with open(file_path) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except (OSError, json.JSONDecodeError) as e:
        console.print(f"[yellow]Warning: Could not load {file_path}: {e}[/yellow]")
        return {}


def save_json_config(file_path: Path, data: Dict[str, Any]) -> None:
    """Save data to JSON config file.

    Args:
        file_path: Path to JSON config file
        data: Dictionary to save

    Raises:
        OSError: If file cannot be written
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')  # Ensure trailing newline


def load_email_groups(groups_file: Optional[Path] = None) -> Dict[str, List[str]]:
    """Load email distribution groups from config.

    Args:
        groups_file: Optional path to groups file (for testing)

    Returns:
        Dictionary mapping group names to email lists
    """
    if groups_file is None:
        config_dir = get_plugin_config_dir()
        groups_file = config_dir / "email-groups.json"

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
        config_dir = get_plugin_config_dir()
        groups_file = config_dir / "email-groups.json"

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


def get_groups_file_path() -> Path:
    """Get path to email groups file.

    Returns:
        Path to email-groups.json
    """
    config_dir = get_plugin_config_dir()
    return config_dir / "email-groups.json"


def get_styles_dir() -> Path:
    """Get the email styles directory path.

    Returns:
        Path to email styles directory
    """
    config_dir = get_plugin_config_dir()
    styles_dir = config_dir / "email-styles"
    styles_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
    return styles_dir


def get_style_file_path(name: str) -> Path:
    """Get path to a specific style file.

    Args:
        name: Style name

    Returns:
        Path to style file
    """
    styles_dir = get_styles_dir()
    return styles_dir / f"{name}.md"


def load_all_styles(styles_dir: Path) -> List[Dict[str, Any]]:
    """Load all style files and extract metadata.

    Args:
        styles_dir: Directory containing style files

    Returns:
        List of style metadata dictionaries
    """
    styles = []
    for style_file in styles_dir.glob("*.md"):
        try:
            metadata = extract_style_metadata(style_file)
            styles.append({
                'name': style_file.stem,
                'description': metadata.get('description', 'No description'),
                'path': style_file,
            })
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load {style_file}: {e}[/yellow]")
    return sorted(styles, key=lambda x: x['name'])


def extract_style_metadata(style_file: Path) -> Dict[str, str]:
    """Extract YAML frontmatter metadata from style file.

    Args:
        style_file: Path to style file

    Returns:
        Dictionary of metadata fields
    """
    content = style_file.read_text()

    # Check for YAML frontmatter
    if content.startswith('---'):
        try:
            end_idx = content.index('\n---\n', 3)
            frontmatter = content[3:end_idx]
            return yaml.safe_load(frontmatter)
        except Exception:
            pass

    # Fallback: minimal metadata
    return {'name': style_file.stem, 'description': 'No description'}


def create_backup(file_path: Path) -> Path:
    """Create timestamped backup of file.

    Args:
        file_path: Path to file to backup

    Returns:
        Path to backup file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.parent / f"{file_path.stem}.backup.{timestamp}{file_path.suffix}"
    backup_path.write_text(file_path.read_text())
    return backup_path


def create_style_from_template(name: str, output_path: Path) -> None:
    """Create new style file from default template.

    Args:
        name: Name of the style
        output_path: Path where style file should be created
    """
    template = """---
name: "{name}"
description: "When to use: [Describe the context and recipients for this style]. [Characteristics of this style]."
---

<examples>
Hi [Name],

[Example email body goes here]

Best,
Warren
---
[Optional second example]
</examples>

<greeting>
- "Hi [Name],"
- "Hello [Name],"
</greeting>

<body>
- Keep sentences clear and concise
- Use active voice
- Organize with paragraphs or bullet points
</body>

<closing>
- "Best,"
- "Thank you,"
</closing>

<do>
- Be direct about requests
- Use appropriate formality for recipient
- Proofread before sending
</do>

<dont>
- Use overly casual language inappropriately
- Write excessively long paragraphs
- Forget to include next steps or action items
</dont>
"""
    output_path.write_text(template.format(name=name))
